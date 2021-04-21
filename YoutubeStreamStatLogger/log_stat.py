#!/usr/bin/env python

"""
Just a script using google Data API to fetch and accumulate live stream details.
Use `./log_stat -h` to see usages.

require google api key for this.
"""

import logging
import itertools
import pathlib
import datetime
import json
import argparse
from typing import Generator, Mapping, List, Union

import trio
import jsbeautifier
from dateutil import parser as date_parser
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


YOUTUBE_API_SERVICE = "youtube"
YOUTUBE_API_VERSION = "v3"
API_FILE = pathlib.Path(__file__).parent.joinpath("api_key").absolute()

logger = logging.getLogger("MAIN")


# parsing start =================================

parser = argparse.ArgumentParser(
    description="Records livestream details using Google Data API."
)
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="Enables debug logging.",
)
parser.add_argument(
    "-g",
    "--graph",
    action="store_true",
    help="Show plot at the end of the program.",
)
parser.add_argument(
    "-o",
    "--output",
    metavar="PATH",
    type=pathlib.Path,
    default=API_FILE.parent,
    help="Output folder, default is script's directory.",
)
parser.add_argument(
    "-p",
    "--poll",
    metavar="INTERVAL",
    type=int,
    default=5,
    help="Changes interval between polls. Default is 5.",
)
parser.add_argument(
    "-f",
    "--flush",
    metavar="INTERVAL",
    type=int,
    default=40,
    help="Interval between write flush. Flushes very Nth poll. Default is 40.",
)
parser.add_argument(
    "-a",
    "--api",
    metavar="KEY",
    type=str,
    default=None,
    help="Google Data API key, can be omitted if you store in file 'api_key' at script directory.",
)
parser.add_argument(
    "video_id", metavar="VIDEO_ID", type=str, help="ID of live youtube stream."
)


args = parser.parse_args()

# Validate
if args.api is None:
    try:
        with open(API_FILE) as _fp:
            args.api = _fp.read()

    except FileNotFoundError as err:
        parser.print_help()

        raise RuntimeError(
            "[-a KEY, --api-key KEY] was omitted without providing api file."
        ) from err


# parsing end ===================================


def init_logger():
    """
    Initialize logger.
    """

    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(asctime)s <%(funcName)s> %(msg)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    level = logging.DEBUG if args.verbose else logging.DEBUG
    handler.setLevel(level)
    logger.setLevel(level)


def build_video_resource():
    """
    Convenience function for building youtube api client.
    """

    youtube = build(YOUTUBE_API_SERVICE, YOUTUBE_API_VERSION, developerKey=args.api)
    video_instance = youtube.videos()

    return video_instance


async def data_gen(request_obj) -> Generator[dict, None, None]:
    """
    Polls Google Data API periodically and yields it.

    :param request_obj: Data API client
    :return: yields dict with key concurrentViewers, viewCount, likeCount, dislikeCount
    """

    try:
        for iteration in itertools.count(0):

            response_dict = request_obj.execute()["items"][0]

            statistics = response_dict["statistics"]
            viewers = response_dict["liveStreamingDetails"]["concurrentViewers"]

            new_dict = {"concurrentViewers": viewers}
            new_dict.update(statistics)

            yield new_dict

            log_string = "Viewers(Cur/Tot):{concurrentViewers}/{viewCount}" \
                         " Likes:{likeCount}/{dislikeCount}".format(**new_dict)
            logger.debug("[%s] %s", iteration, log_string)

            await trio.sleep(args.poll)

    except (KeyError, HttpError):
        logger.warning("Stream ID %s closed.", args.video_id)
        return

    except KeyboardInterrupt:
        logger.warning("Got ctrl+c")
        return


class Router:
    """
    Just a storage only to provide __dict__
    as this use key of given dict as self.__dict__'s key, pep8 violation is inevitable.
    """
    def __init__(self):
        self.concurrentViewers = []
        self.viewCount = []
        self.likeCount = []
        self.dislikeCount = []

    def __len__(self):
        return len(self.concurrentViewers)

    def append(self, value_dict: Mapping):
        """
        Dumb dispatching to associated list

        :param value_dict: mapping containing keys with exact same name of object's attributes
        """

        for key, val in value_dict.items():
            self.__dict__[key].append(int(val))

    def dump(self) -> dict:
        """
        Just a convenience method, better than using dunder method directly!

        :return: object's __dict__
        """

        return self.__dict__


def write_json_closure(file_path: Union[str, pathlib.Path], data: Mapping):
    """
    Closure for initializing writing configs.
    Expects direct changes to data

    :param file_path: location to save file
    :param data: data to store - Anything that json serializable
    :return: function write(), no additional param needed
    """

    option = jsbeautifier.default_options()
    option.indent_size = 2

    # validate path
    try:
        file_path.touch()
    except OSError:
        logger.critical(
            "Could not touch the file at %s! Is filename supported by os?",
            file_path.as_posix()
        )
        raise

    logger.debug("Successfully created %s.", file_path.as_posix())

    def write():
        with open(file_path, "w", encoding="utf8") as fp:
            fp.write(
                jsbeautifier.beautify(json.dumps(data, ensure_ascii=False), option)
            )

        logger.info("Written %s sample(s).", len(data['data']['dislikeCount']))

    return write


def fetch_api(request) -> dict:
    """
    Just to shorten line width.

    :param request: google api request object ready to be executed
    :return: 1 step flatten and merged dict
    """

    response: Mapping[str, List[dict]] = request.execute()

    new_dict = {}

    for dict_ in response["items"]:
        new_dict.update(dict_)

    return new_dict


async def wait_for_stream(api_client):
    """
    Literally does what it's named for.

    :param api_client: google api request object
    """

    # check if actually there is active/upcoming stream
    stream_started_check = api_client.list(
        id=args.video_id, part="snippet", fields="items/snippet/liveBroadcastContent"
    )

    def status_fetch():
        return fetch_api(stream_started_check)["snippet"]["liveBroadcastContent"]

    # Dispatch cases
    status = status_fetch()

    if status == "live":
        logger.debug(
            "liveBroadcastContent returned `%s`, stream already active.",
            status
        )
        return

    if status == "none":
        logger.critical(
            "liveBroadcastContent returned `%s`, is this a livestream?",
            status
        )
        raise RuntimeError("No upcoming/active stream.")

    # upcoming state, fetch scheduled start time
    start_time_request = api_client.list(
        id=args.video_id,
        part="liveStreamingDetails",
        fields="items/liveStreamingDetails/scheduledStartTime",
    )
    start_time_string = fetch_api(start_time_request)["liveStreamingDetails"][
        "scheduledStartTime"
    ]
    start_time = date_parser.isoparse(start_time_string)

    # get timedelta
    current = datetime.datetime.now(datetime.timezone.utc)

    # workaround for negative timedelta case. Checks if start time is future
    if start_time > current:

        delta = (start_time - current).seconds
        logger.info(
            "Will wait for %s seconds until stream starts. Press Ctrl+C to terminate.",
            delta
        )

        # Sleep until due time
        await trio.sleep((current - start_time).seconds)

    # Check if stream is actually started
    while status := status_fetch():
        logger.debug("Status check: %s", status)

        if status == "none":
            logger.critical(
                "liveBroadcastContent returned `%s`, is stream canceled?",
                status
            )
            raise RuntimeError("No upcoming/active stream.")

        if status == "live":
            return

        await trio.sleep(5)


async def main():
    """
    Main coroutine
    """

    video = build_video_resource()

    # validate api key and video ID
    try:
        video_title = fetch_api(
            video.list(id=args.video_id, part="snippet", fields="items/snippet/title")
        )["snippet"]["title"]
    except HttpError:
        logger.critical("Request failed, check if API or video ID is correct.")
        raise

    # pre-bake file writer function. Will validate output path in process
    data = {"stream_title": video_title, "interval": args.poll}
    start_t = datetime.datetime.now()
    file_name = f"{start_t.date().isoformat()}_{args.video_id}_{int(start_t.timestamp())}.json"
    full_file_path: pathlib.Path = args.output.joinpath(pathlib.Path(file_name))

    write_func = write_json_closure(full_file_path, data)

    # Wait for stream to start
    try:
        await wait_for_stream(video)
    except (Exception, KeyboardInterrupt):
        # Make sure to delete file
        full_file_path.unlink()
        logger.warning("Removing empty json file %s", full_file_path.as_posix())
        raise

    # Request object for data polling
    combined_request = video.list(
        id=args.video_id,
        part=["statistics", "liveStreamingDetails"],
        fields="items(statistics(likeCount,dislikeCount,viewCount),"
               "liveStreamingDetails/concurrentViewers)",
    )

    # initialize data dispatcher, and add __dict__ instance to data
    router_instance = Router()
    data["data"] = router_instance.__dict__

    # to make async for loop do something every n time, will use infinite cycler.
    flush_interval_control = itertools.cycle(
        not bool(n) for n in reversed(range(args.flush))
    )

    # We got a lot of time for appending, hope async sleep in async for works better!
    try:
        async for fetched_dict in data_gen(combined_request):
            router_instance.append(fetched_dict)

            if next(flush_interval_control):
                logger.info("Saving, do not interrupt.")
                write_func()
    except KeyboardInterrupt:
        logger.warning("Got ctrl+c")

    write_func()

    if args.graph:
        logger.info("Preparing graph.")
        try:
            from logged_data_viewer import plot_main
        except ImportError as err_:
            logger.critical("Cannot import module - %s", err_)
            return

        plot_main(data)


if __name__ == "__main__":
    init_logger()
    trio.run(main)
