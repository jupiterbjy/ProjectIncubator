#!/usr/bin/python3

import argparse
import itertools
import functools
import logging
import pathlib
import json
import datetime
from collections import deque
from typing import Generator, List

import trio
from discord_webhook import DiscordWebhook
from requests.exceptions import ConnectionError, MissingSchema

from log_stat_stub import wait_for_stream
from youtube_api_client import GoogleClient, HttpError
from RequestExtension import video_list_gen
from log_initalizer import init_logger

# End of import --------------


JSON_PATH = pathlib.Path(__file__).parent.absolute().joinpath("configuration.json")


def webhook_closure(webhook_url: str):
    def template(message_, **kwargs):
        DiscordWebhook(url=webhook_url, content=message_, **kwargs).execute()

    return template


def format_closure(config_dict):
    """
    Make sure to have separators in video descriptions if you're going to use it!
    """

    start = config_dict["start"]
    end = config_dict["end"]
    format_ = config_dict["format"]

    # bake function, like how cakes bake a loaf. Meow.
    def inner(message_: str, vid_id: str):

        # if start separator is specified, check position.
        if start:
            message_ = message_.split(start)[-1]

        # Same goes for end separator
        if end:
            message_ = message_.split(end)[0]

        # Make sure to have one newline in both end. Can't use backslash in f-string inner block.
        message_ = message_.strip('\n')

        return format_.format(message_, vid_id)

    return inner


def task_gen(
        client: GoogleClient, config_dict: dict, next_check: datetime.datetime, args
) -> Generator[List, None, None]:
    notified = deque(maxlen=10)

    channel_id = config_dict["channels"]
    format_description = format_closure(config_dict)

    gen_instances = [video_list_gen(ch_id, args.count) for ch_id in channel_id]
    vid_list_gen = zip(*gen_instances)

    def notify_live(vid_id: str):
        notified.append(vid_id)

        bot((format_description(client.get_video_description(vid_id), vid_id)))

        logger.info("Notified for video %s", vid_id)

        notified.append(vid_id)

    async def task(vid_id: str):
        logger.debug("Task %s spawned.", vid_id)

        notified.append(vid_id)

        await wait_for_stream(client, vid_id)

        logger.debug("Task %s returned.", vid_id)

    while True:

        next_ = next(vid_list_gen)
        logger.debug("fetched following video IDs: %s", next_)

        videos = set(itertools.chain(*next_))

        upcoming = []

        for vid in videos:
            try:
                state = client.get_stream_status(vid)
            except HttpError as err_:
                logger.critical("Got HTTP Error, did connection lost or quota exceeded?")
                logger.critical("Message: %s", err_)

                if args.ignore_error:
                    continue

                else:
                    raise

            logger.debug("video IDs <%s> status: %s", vid, state)

            # if already live, notify asap
            if state == "live" and vid not in notified:
                notify_live(vid)
                continue

            # else put in upcoming.
            if state == "upcoming" and vid not in notified:
                upcoming.append(vid)

        # yield upcoming streams due to start before next check period.
        yield [
            functools.partial(task, vid_id=v_id)
            for v_id in upcoming
            if client.get_start_time(v_id) < next_check
        ]


async def main_coroutine(args, config_dict: dict):
    client = GoogleClient(args.api)

    interval = args.interval
    time_delta = datetime.timedelta(seconds=interval)

    logger.debug("Got configuration: %s", config_dict)

    async with trio.open_nursery() as nursery:
        next_checkup = datetime.datetime.now(datetime.timezone.utc) + time_delta

        for tasks in task_gen(client, config_dict, next_checkup, args):

            for task in tasks:
                nursery.start_soon(task)

            next_checkup += time_delta
            await trio.sleep((next_checkup - datetime.datetime.now(datetime.timezone.utc)).seconds)

            logger.info("Next checkup is %s", next_checkup)


if __name__ == "__main__":

    # parsing start =================================

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "api",
        type=str,
        help="Google Data API key.",
    )
    parser.add_argument(
        "url",
        type=str,
        help="Discord webhook url.",
    )
    parser.add_argument(
        "-p",
        "--path",
        metavar="CONFIG_PATH",
        type=pathlib.Path,
        default=pathlib.Path(__file__).absolute().parent.joinpath("configuration.json"),
        help="Path to configuration json file.",
    )
    parser.add_argument(
        "-i",
        "--interval",
        metavar="INTERVAL",
        type=int,
        default=5,
        help="interval between checks in seconds. Default is 60.",
    )
    parser.add_argument(
        "-c",
        "--count",
        metavar="NUM",
        type=int,
        default=5,
        help="Number of videos to fetch from each channel. Default is 3.",
    )
    parser.add_argument(
        "-I",
        "--ignore-error",
        action="store_true",
        default=False,
        help="Ignore HTTP Errors including quota check."
             "This will still fail to get data from Youtube, but script won't stop.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Enables debugging message.",
    )

    args_ = parser.parse_args()

    # parsing end ===================================

    logger = logging.getLogger("DiscordBot")
    init_logger(logger, args_.verbose)

    json_data = json.loads(args_.path.read_text())

    logger.info("Target Channel: %s", json_data["channels"])

    bot = webhook_closure(args_.url)

    # validate first using empty string
    try:
        bot("")
    except (ConnectionError, MissingSchema) as err:
        logger.critical("Connection/Schema Error! Is provided url a valid one?")
        logger.critical("Message: %s", err)
        exit(-1)

    else:
        try:
            trio.run(main_coroutine, args_, json_data)

        except HttpError as err:
            logger.critical("Got HTTP Error, did connection lost or quota exceeded?")
            logger.critical("Message: %s", err)
            exit(-1)

        except KeyboardInterrupt:
            pass
