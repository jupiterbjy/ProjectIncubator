#!/usr/bin/python3

"""
This will run 24/7/365, polling periodically for upcoming streams.

Logging to file is turned off by default, as Piping it to file seemed better.
"program [arguments] 2>&1 | tee output.file" would redirect stdout/stderr to
both console and file. This way you can also collect child tasks' logs.
"""

import datetime
import argparse
import logging
import pathlib
import json
import subprocess
from typing import Dict

import trio

from log_initalizer import init_logger
from youtube_api_client import Client, HttpError


ROOT = pathlib.Path(__file__).parent.absolute()
CONFIG_PATH = ROOT.joinpath("autorec_config.json")
LOG_STAT_PATH = ROOT.joinpath("log_stat.py")
LOG_PATH = ROOT.joinpath("Logs")
logger = logging.getLogger("AutoRecord")

LOG_PATH.mkdir(parents=True, exist_ok=True)


def load_json(path) -> Dict:
    """
    Just convenience method for loading json.

    :param path: path to json file
    :return: loaded dict
    """
    with open(path, encoding="utf8") as fp_:
        return json.load(fp_)


class Manager:
    """
    Main logic, should be driven by external loop inside event loop.
    Generate task to run stream logging.
    """
    def __init__(self, config_path, client_: Client):
        self.client = client_

        self.config_path = config_path
        self.loaded = dict()

        # key: alphabetical channel name / val: channel id
        self.channel_list = dict()
        # self.channel_live = dict()

        # will contain Tuple[abc. channel name / channel id / video id]
        self.video_in_task = set()

        self.last_check = datetime.datetime.now(datetime.timezone.utc)
        self.load_config()

    @property
    def check_interval(self):
        return self.loaded["check_interval_hour"]

    @property
    def get_next_checkup(self) -> datetime.datetime:
        return self.last_check + datetime.timedelta(hours=self.check_interval)

    def load_config(self):
        self.loaded = load_json(self.config_path)

        self.channel_list = self.loaded["channels"]

    def fetch_live(self) -> Dict[str, str]:
        video_live = {}
        video_upcoming = {}

        for channel, channel_id in self.channel_list.items():
            try:
                upcoming = self.client.get_upcoming_streams(channel_id)
                live = self.client.get_live_streams(channel_id)
            except HttpError as err:
                if err.error_details == "quotaExceeded":
                    logger.critical("Data API quota exceeded, cannot use the API.")
                else:
                    logger.critical(
                        "Unknown HttpError received, error detail: %s",
                        err.error_details,
                    )
                raise

            logger.debug("Checking channel %s %s", channel, channel_id)

            if live:
                # Will there be two stream concurrently for a channel -
                # unless it's association like NASA?

                for vid_id in live:
                    # seems like it's better this way rather than gen-exp. Even shorter.
                    # No need to include videos which is already assigned.

                    if vid_id not in self.video_in_task:
                        video_live[vid_id] = channel

            if upcoming:
                # you know, this ain't as rare as concurrent live streams.

                for vid_id in upcoming:
                    if vid_id not in self.video_in_task:
                        video_upcoming[vid_id] = channel

        # check how much time we have for upcoming videos
        for video_id, channel in video_upcoming.items():
            stream_start = self.client.get_start_time(video_id)

            # if it's due before next checkup, just consider it as live.
            if stream_start < self.get_next_checkup:
                video_live[video_id] = channel

        logger.info(
            "Found %s upcoming stream(s), %s live/imminent stream(s)",
            len(video_upcoming),
            len(video_live),
        )

        return video_live

    def task_gen(self):
        def closure(ch_name, vid_id):
            path = LOG_STAT_PATH.parent.joinpath(ch_name)
            path.mkdir(parents=True, exist_ok=True)

            async def task():
                # add video id to running tasks list
                self.video_in_task.add(vid_id)

                arg = f'"{LOG_STAT_PATH.as_posix()}"' \
                      f' -o "{path}" ' \
                      f'{self.loaded["log_stat_param"]} ' \
                      f'{vid_id}'

                if args.api:
                    arg += f" -a {args.api}"

                try:
                    await trio.run_process(arg, shell=True)
                except subprocess.CalledProcessError as err:
                    logger.critical(
                        "Subprocess %s failed. return code: %s", vid_id, err.returncode
                    )
                finally:
                    self.video_in_task.remove(vid_id)
                    logger.info("Task %s returned.", vid_id)

            return task

        for video_id, channel in self.fetch_live().items():
            yield channel, video_id, closure(channel, video_id)


async def main():
    manager = Manager(CONFIG_PATH, client)

    async def main_loop_gen():
        while True:
            if tasks_ := tuple(manager.task_gen()):
                yield tasks_

            # sleep. goodnight my kid.. kids? kid? who cares.
            sleep_time = manager.get_next_checkup
            manager.last_check = sleep_time
            logger.info("Sleeping until next check at %s", sleep_time)
            await trio.sleep(
                (sleep_time - datetime.datetime.now(datetime.timezone.utc)).seconds
            )

            # reload config
            logger.debug("Reloading config")
            manager.load_config()

    async with trio.open_nursery() as nursery:
        async for tasks in main_loop_gen():
            # map(nursery.start_soon, tasks)

            for channel, video_id, task in tasks:
                logger.info("Starting task %s for channel %s", video_id, channel)
                nursery.start_soon(task)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--api", metavar="KEY", type=str, default=None)
    parser.add_argument("-o", "--output-log", action="store_true")

    args = parser.parse_args()
    client = Client(args.api)

    start_time = datetime.datetime.now()

    log_path = (
        LOG_PATH.joinpath(f"{start_time.date().isoformat()}.log")
        if args.output_log
        else None
    )

    init_logger(logger, True, log_path)

    logger.info(
        "Started at %s utc", datetime.datetime.utcfromtimestamp(start_time.timestamp())
    )

    trio.run(main)
