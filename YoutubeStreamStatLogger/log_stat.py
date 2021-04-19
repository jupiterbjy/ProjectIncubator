#!/usr/bin/env python

"""
require google api key for this
"""

import logging
import itertools
import pathlib
import datetime
import json
import argparse
from typing import Generator, Mapping

import trio
import jsbeautifier
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


YOUTUBE_API_SERVICE = "youtube"
YOUTUBE_API_VERSION = "v3"
API_FILE = "api_key"

logger = logging.getLogger("MAIN")


parser = argparse.ArgumentParser(
    description="Records concurrent viewers of live video."
)
parser.add_argument(
    "video_id", metavar="V_ID", type=str, help="ID of live youtube video"
)
parser.add_argument(
    "api_key",
    metavar="API_KEY",
    type=str,
    nargs="?",
    default=None,
    help="Google API key, can be omitted if you save it in file `api_key`. next to this script.",
)
parser.add_argument(
    "--poll_interval",
    type=int,
    default=5,
    help="Interval between polls",
)
parser.add_argument(
    "--flush_interval",
    type=int,
    default=40,
    help="Interval between file flush, will be flushed in every Nth polling.",
)
parser.add_argument(
    "--v",
    action="store_true",
    help="Enables debugging output",
)
parser.add_argument(
    "--s",
    action="store_true",
    help="Show plot at the end of the program.",
)


args = parser.parse_args()
if args.api_key is None:
    try:
        with open(API_FILE) as _fp:
            api_key = _fp.read()
    except FileNotFoundError:
        api_key = input("api key: ")

    args.api_key = api_key


def init_logger():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] <%(funcName)s> %(msg)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if args.v:
        handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)


def build_video_resource():
    youtube = build(YOUTUBE_API_SERVICE, YOUTUBE_API_VERSION, developerKey=args.api_key)
    video_instance = youtube.videos()

    return video_instance


async def data_gen(request_obj) -> Generator[dict, None, None]:

    try:
        for iteration in itertools.count(0):

            response_dict = request_obj.execute()["items"][0]

            statistics = response_dict["statistics"]
            viewers = response_dict["liveStreamingDetails"]["concurrentViewers"]

            new_dict = {"concurrentViewers": viewers}
            new_dict.update(statistics)

            yield new_dict

            logger.debug(
                f"[{iteration}]"
                + "Viewers(Cur/Tot):{concurrentViewers}/{viewCount} "
                  "Likes:{likeCount}/{dislikeCount}".format(**new_dict)
            )

            await trio.sleep(args.poll_interval)

    except (KeyError, HttpError):
        logger.warning(f"Stream ID {args.video_id} closed.")
        return

    except KeyboardInterrupt:
        logger.warning("Got ctrl+c")
        return


class Router:
    def __init__(self):
        self.concurrentViewers = []
        self.viewCount = []
        self.likeCount = []
        self.dislikeCount = []

    def __len__(self):
        return len(self.concurrentViewers)

    def append(self, value_dict: Mapping):
        for key, val in value_dict.items():
            self.__dict__[key].append(int(val))

    def dump(self) -> dict:
        return self.__dict__


def write_json_closure(file_path, data: dict):

    option = jsbeautifier.default_options()
    option.indent_size = 2

    def write():
        with open(file_path, "w", encoding="utf8") as fp:
            fp.write(
                jsbeautifier.beautify(json.dumps(data, ensure_ascii=False), option)
            )

        logger.info(f"Written {len(data['data']['dislikeCount'])} data.")

    return write


async def main():
    video = build_video_resource()

    name_response = video.list(
        id=args.video_id, part="snippet", fields="items/snippet/title"
    ).execute()
    combined_request = video.list(
        id=args.video_id,
        part=["statistics", "liveStreamingDetails"],
        fields="items(statistics(likeCount,dislikeCount,viewCount),liveStreamingDetails/concurrentViewers)",
    )

    video_title = name_response["items"][0]["snippet"]["title"]
    start_time = datetime.datetime.now()
    file_path = pathlib.Path(
        f"{start_time.date().isoformat()}_{args.video_id}_{int(start_time.timestamp())}.json"
    )

    router_instance = Router()

    # We got a lot of time for appending, why not?
    flush_interval_control = itertools.cycle(([False] * (args.flush_interval - 1)) + [True])
    data = {"stream_title": video_title, "interval": args.poll_interval}
    write_func = write_json_closure(file_path, data)

    async for fetched_dict in data_gen(combined_request):
        router_instance.append(fetched_dict)

        if next(flush_interval_control):
            logger.info(f"Saving, do not interrupt.")
            data["data"] = router_instance.dump()
            write_func()

    if args.s:
        try:
            from logged_data_viewer import plot_main
        except ImportError as err:
            logger.critical(f"Cannot import module - {err}")
            return

        plot_main(data)


if __name__ == "__main__":
    init_logger()
    trio.run(main)
