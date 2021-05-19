#!/usr/bin/python3

import argparse
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
from log_initalizer import init_logger
from youtube_api_client import Client, HttpError


# End of import --------------


JSON_PATH = pathlib.Path(__file__).parent.absolute().joinpath("configuration.json")


def webhook_closure(webhook_url: str):
    def template(message_, **kwargs):
        DiscordWebhook(url=webhook_url, content=message_, **kwargs).execute()

    return template


def format_closure():
    """
    Make sure to have separators in video descriptions if you're going to use it!
    """

    try:
        with open(JSON_PATH, encoding="utf8") as fp:
            loaded = json.load(fp)

    except (FileNotFoundError, json.decoder.JSONDecodeError) as err_:
        logger.debug("Couldn't load separators. Using entire descriptions without stripping.")
        logger.debug("Error detail: %s", err_)

        start = ""
        end = ""
        format_ = "Description:\n{}\nLink:\nhttps://youtu.be/{}"

    else:
        start = loaded["start"]
        end = loaded["end"]
        format_ = loaded["format"]

    # bake function, like how cakes bake a loaf. Meow.
    def inner(message_: str, vid_id: str):

        # if start separator is specified, check position.
        if start:
            message_ = message_.split(start)[-1]

        # Same goes for end separator
        if end:
            message_ = message_.split(end)[0]

        # Make sure to have one newline in both end. Can't use backslash in f-string inner block.
        striped = message_.strip('\n')
        message_ = f"\n{striped}\n"

        return format_.format(message_, vid_id)

    return inner


format_description = format_closure()


def task_gen(
    client: Client, channel_id: str, next_check: datetime.datetime
) -> Generator[List, None, None]:

    notified = deque(maxlen=10)

    def notify_live(vid_id: str):
        bot((format_description(client.get_video_description(vid_id), vid_id)))

        logger.debug("Notified for video %s", vid_id)

        notified.append(vid_id)

    async def task(vid_id: str):
        notified.append(vid_id)
        await wait_for_stream(client, vid_id)

        logger.debug("Task %s returned.", vid_id)

    if args.exclude_live:
        def check_live():
            pass

    else:
        def check_live():
            live_tuple = client.get_live_streams(channel_id)

            # If it's already live, we're screwed, notify it asap
            for live in set(live_tuple) - set(notified):
                notify_live(live)

    while True:
        check_live()

        # Else check if upcoming will start before next checkup tasks
        upcoming_tuple = client.get_upcoming_streams(channel_id)

        yield [
            functools.partial(task, vid_id=v_id)
            for v_id in upcoming_tuple
            if client.get_start_time(v_id) < next_check
        ]


async def main_coroutine():
    ch_id = args.channel_id
    client = Client(args.api)

    interval = args.interval
    time_delta = datetime.timedelta(minutes=interval)

    async with trio.open_nursery() as nursery:
        next_checkup = datetime.datetime.now(datetime.timezone.utc) + time_delta

        for tasks in task_gen(client, ch_id, next_checkup):

            for task in tasks:
                nursery.start_soon(task)

            next_checkup += time_delta
            await trio.sleep((next_checkup - datetime.datetime.now(datetime.timezone.utc)).seconds)

        logger.debug("Next checkup is %s", next_checkup)


def test_output():
    target = args.test
    client = Client(args.api)

    bot(format_description(client.get_video_description(target), target))


if __name__ == "__main__":

    # parsing start =================================

    logger = logging.getLogger("DiscordBot")
    init_logger(logger, True)

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-a",
        "--api",
        metavar="KEY",
        type=str,
        required=True,
        help="Google Data API key",
    )
    parser.add_argument(
        "-u",
        "--url",
        metavar="URL",
        type=str,
        required=True,
        help="Discord webhook url.",
    )
    parser.add_argument(
        "-i",
        "--interval",
        metavar="INTERVAL",
        type=int,
        default=5,
        help="Check interval in minutes. If omitted, will be set to 5.",
    )
    parser.add_argument(
        "-e",
        "--exclude-live",
        action="store_true",
        default=False,
        help="Excludes check for already live streams. This reduces Quota usages roughly by a bit short on half.",
    )
    exclusive = parser.add_mutually_exclusive_group(required=True)
    exclusive.add_argument(
        "-c",
        "--channel-id",
        metavar="ID",
        type=str,
        help="Youtube channel's ID.",
    )
    exclusive.add_argument(
        "-t",
        "--test",
        metavar="VID_ID",
        type=str,
        help="Test output with youtube video id",
    )

    args = parser.parse_args()
    args_got = {key: item for key, item in vars(args).items()}
    del args_got["api"]
    del args_got["url"]

    # parsing end ===================================

    print(args)
    bot = webhook_closure(args.url)

    # validate first using empty string
    try:
        bot("")
    except (ConnectionError, MissingSchema) as err:
        logger.critical("Connection/Schema Error! Is provided url a valid one?")
        logger.critical("Message: %s", err)
        exit(-1)

    # determine test mode
    if args.channel_id is None:
        test_output()

    else:
        try:
            trio.run(main_coroutine)

        except HttpError as err:
            logger.critical("Got HTTP Error, did connection lost or quota exceeded?")
            logger.critical("Message: %s", err)
            exit(-1)

        except KeyboardInterrupt:
            pass
