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
from youtube_api_client import Client


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

    except (FileNotFoundError, json.decoder.JSONDecodeError) as err:
        logger.debug("Couldn't load separators. Using entire descriptions without stripping.")
        logger.debug("Error detail: %s", err)

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

    while True:
        live_tuple, upcoming_tuple = (
            client.get_live_streams(channel_id),
            client.get_upcoming_streams(channel_id),
        )

        # If it's already live, we're screwed, notify it asap
        for live in set(live_tuple) - set(notified):
            notify_live(live)

        # Else check if upcoming will start before next checkup tasks
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

    message_format = "#live\n{}\n[Youtube]https://youtu.be/{}"
    description = format_description(client.get_video_description(target))
    bot(message_format.format(description, target))


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
    except (ConnectionError, MissingSchema):
        logger.critical("Connection/Schema Error! Is provided url a valid one?")
        exit(-1)

    # determine test mode
    if args.channel_id is None:
        test_output()

    else:
        trio.run(main_coroutine)
