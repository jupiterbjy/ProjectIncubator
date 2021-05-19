"""
Setting this up everytime in interpreter ain't fun. So just import this in interpreter.
Will look for google api from file named `api_key` on cwd.
You can manually specify it when building resource file.

Readability is 'amazing', even I can't read well
"""

import pathlib
import datetime
from typing import Tuple, Callable

from dateutil import parser as date_parser
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


assert HttpError
YOUTUBE_API_SERVICE = "youtube"
YOUTUBE_API_VERSION = "v3"
API_FILE = pathlib.Path(__file__).parent.joinpath("api_key").absolute()


def build_youtube_resource(api_key=None):
    if api_key is None:
        # if file path is wrong, will raise file not found. handle it outside.
        with open(API_FILE) as _fp:
            api_key = _fp.read()

    youtube = build(YOUTUBE_API_SERVICE, YOUTUBE_API_VERSION, developerKey=api_key)
    return youtube


class Client:
    def __init__(self, api_key=None):
        self.youtube_client = build_youtube_resource(api_key)
        self.video_api = self.youtube_client.videos()
        self.channel_api = self.youtube_client.channels()
        self.search_api = self.youtube_client.search()

    def get_stream_status(self, video_id) -> str:
        # This is most inefficient out of these methods.. but it's way simpler than first code.

        req = self.video_api.list(
            id=video_id, part="snippet", fields="items/snippet/liveBroadcastContent"
        )

        return req.execute()["items"][0]["snippet"]["liveBroadcastContent"]

    def get_video_title(self, video_id) -> str:

        req = self.video_api.list(
            id=video_id, part="snippet", fields="items/snippet/title"
        )

        return req.execute()["items"][0]["snippet"]["title"]

    def get_video_description(self, video_id) -> str:

        req = self.video_api.list(
            id=video_id, part="snippet", fields="items/snippet/description"
        )

        return req.execute()["items"][0]["snippet"]["description"]

    def get_channel_id(self, video_id) -> str:

        req = self.video_api.list(
            id=video_id, part="snippet", fields="items/snippet/channelId"
        )

        return req.execute()["items"][0]["snippet"]["channelId"]

    def get_subscribers_count(self, channel_id) -> Callable:

        req = self.channel_api.list(
            id=channel_id,
            part="statistics",
            fields="items/statistics/subscriberCount",
        )

        return req.execute()["items"][0]["statistics"]["subscriberCount"]

    def get_upcoming_streams(self, channel_id: str) -> Tuple[str, ...]:
        req = self.search_api.list(
            channelId=channel_id, part="snippet", type="video", eventType="upcoming"
        )
        items = req.execute()["items"]
        vid_ids = (item["id"]["videoId"] for item in items)
        return tuple(vid_id for vid_id in vid_ids if self.get_stream_status(vid_id) != "none")

    def get_live_streams(self, channel_id: str) -> Tuple[str, ...]:
        req = self.search_api.list(
            channelId=channel_id, part="snippet", type="video", eventType="live"
        )
        items = req.execute()["items"]
        vid_ids = (item["id"]["videoId"] for item in items)
        return tuple(vid_id for vid_id in vid_ids if self.get_stream_status(vid_id) != "none")

    def get_start_time(self, video_id) -> datetime.datetime:
        req = self.video_api.list(
            id=video_id,
            part="liveStreamingDetails",
            fields="items/liveStreamingDetails/scheduledStartTime",
        )
        time_string = req.execute()["items"][0]["liveStreamingDetails"][
            "scheduledStartTime"
        ]

        start_time = date_parser.isoparse(time_string)
        return start_time
