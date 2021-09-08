"""
Setting this up everytime in interpreter ain't fun. So just import this in interpreter.
Will look for google api from file named `api_key` on cwd.
You can manually specify it when building resource file.

Readability is 'amazing', even I can't read well. Will add docstrings when I can.
"""
import inspect
import os
import pathlib
import datetime
from typing import Tuple, Union

import googleapiclient.discovery
import googleapiclient.errors
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from dateutil.parser import isoparse


scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


API_SERV_NAME = "youtube"
API_VERSION = "v3"


def build_client(
    api_key=None,
    client_secret_dir=None,
    token_dir=None,
    console=False,
    secure=True,
) -> "YoutubeClient":
    """
    Builds authenticated Youtube client wrapper.

    Args:
        api_key: Google Data API key
        client_secret_dir: client secret file to load from.
        token_dir: Oauth token file to create credential from.
        console: If true, accept code via command line. Otherwise opens a local web server.
        secure: Enables Https request.

    Returns:
        YoutubeClient object
    """

    # config dict to feed on builder
    config = {"serviceName": API_SERV_NAME, "version": API_VERSION}

    # check parameters start ----
    if not secure:
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    if api_key is not None:
        config["developerKey"] = api_key

    if token_dir:
        token_dir = pathlib.Path(token_dir)

    if client_secret_dir:
        client_secret_dir = pathlib.Path(client_secret_dir)

    credential = None

    if token_dir and token_dir.exists():
        # cached oauth remains, try to load it
        credential = Credentials.from_authorized_user_file(token_dir.as_posix())

    if not credential or not credential.valid:
        if credential and credential.expired and credential.refresh_token:
            credential.refresh(Request())
        else:
            file = pathlib.Path(client_secret_dir)
            flow = InstalledAppFlow.from_client_secrets_file(file.as_posix(), scopes)

            if console:
                credential = flow.run_console()
            else:
                credential = flow.run_local_server()

            if token_dir:
                print(f"Saving oauth token for later use at '{token_dir}'")
                token_dir.write_text(credential.to_json(), "utf8")

    # check parameters end ------

    youtube = googleapiclient.discovery.build(**config, credentials=credential)
    return YoutubeClient(youtube, credential)


class LazyProperty:
    # python cookbook 3E

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            value = self.func(instance)
            setattr(instance, self.func.__name__, value)
            return value


class LiveStream:
    def __init__(self, dict_: dict):
        self.json = dict_

        self.status = self.json["status"]["streamStatus"]
        self.title = self.json["snippet"]["title"]
        self.description = self.json["snippet"]["description"]
        self.published_at = self.json["snippet"]["description"]

    @property
    def pub_date(self):
        return isoparse(self.published_at)

    @property
    def is_live(self):
        return self.status == "active"


class LiveBroadcast:
    def __init__(self, dict_: dict):
        self.json = dict_
        self.status = self.json["status"]
        self.snippet = self.json["snippet"]

        # basic ----
        self.kind = self.json["kind"]
        self.etag = self.json["etag"]
        self.id = self.json["id"]

        # status ---
        self.life_cycle_status = self.status.get("lifeCycleStatus", None)
        self.privacy_status = self.status.get("privacyStatus", None)
        self.recording_status = self.status.get("recordingStatus", None)
        self.made_for_kids = self.status.get("madeForKids", None)
        self.self_declared_made_for_kids = self.status.get(
            "selfDeclaredMadeForKids", None
        )

        # snippet ---
        self._published_at = self.snippet.get("publishedAt", None)
        self.channel_id = self.snippet.get("channelId", None)
        self.title = self.snippet.get("title", None)
        self.description = self.snippet.get("description", None)

        self._thumbnail = self.snippet.get("thumbnails", None)
        self._scheduled_start_time: str = self.snippet.get("scheduledStartTime", None)
        self._scheduled_end_time: str = self.snippet.get("scheduled_end_time", None)
        self._actual_start_time: str = self.snippet.get("actualStartTime", None)
        self._actual_end_time: str = self.snippet.get("actualEndTime", None)

        self.is_default_broadcast: bool = self.snippet.get("isDefaultBroadcast", None)
        self.live_chat_id: str = self.snippet.get("liveChatId", None)

    def __str__(self):
        return f"<LiveBroadcast instance of stream {self.id}>"

    @LazyProperty
    def link(self):
        """
        This is Property - access like an attribute

        Returns:
            url of the stream
        """

        return f"https://www.youtube.com/watch?v={self.id}"

    @LazyProperty
    def published_at(self):
        """
        This is Property - access like an attribute

        Returns:
            Timezone-aware datetime object or None
        """

        if self._published_at:
            return isoparse(self._published_at)
        return None

    @LazyProperty
    def scheduled_start_time(self):
        """
        This is Property - access like an attribute

        Returns:
            Timezone-aware datetime object or None
        """

        if self._scheduled_start_time:
            return isoparse(self._scheduled_start_time)
        return None

    @LazyProperty
    def scheduled_end_time(self):
        """
        This is Property - access like an attribute

        Returns:
            Timezone-aware datetime object or None
        """

        if self._scheduled_end_time:
            return isoparse(self._scheduled_end_time)
        return None

    @LazyProperty
    def actual_start_time(self):
        """
        This is Property - access like an attribute

        Returns:
            Timezone-aware datetime object or None
        """

        if self._actual_start_time:
            return isoparse(self._actual_start_time)
        return None

    @LazyProperty
    def actual_end_time(self):
        """
        This is Property - access like an attribute

        Returns:
            Timezone-aware datetime object or None
        """

        if self._actual_end_time:
            return isoparse(self._actual_end_time)
        return None

    @LazyProperty
    def is_live(self):
        """
        This is Property - access like an attribute

        Returns:
            True if stream is currently live.
        """

        return self.life_cycle_status == "live"

    def thumbnails(self, quality=2):
        quality = quality if 0 <= quality <= 4 else 4

        table = ("default", "medium", "high", "standard", "maxres")

        return self._thumbnail[table[quality]]["url"]

    def as_dict(self):
        return {k: v for k, v in inspect.getmembers(self)}


class Video:
    def __init__(self, dict_: dict):
        self.json = dict_

        snippet = dict_["snippet"]

        self.title = snippet["title"]
        self.description = snippet["description"]
        self.channel_title = snippet["channelTitle"]
        self.channel_id = snippet["channelId"]
        self.published_at = snippet["publishedAt"]

        try:
            self.video_id = snippet["resourceId"]["videoId"]
        except KeyError:
            self.video_id = dict_["id"]

        try:
            self.live_content = snippet["liveBroadcastContent"]
        except KeyError:
            self.live_content = ""

        self._thumbnail = snippet["thumbnails"]

        self.view_count: Union[None, int] = None
        self.like_count: Union[None, int] = None

        if "statistics" in dict_.keys():
            self.view_count = dict_["statistics"]["viewCount"]
            self.like_count = dict_["statistics"]["likeCount"]

    @property
    def pub_date(self):
        return isoparse(self.published_at)

    @property
    def is_upcoming(self):
        return self.live_content == "upcoming"

    @property
    def is_live(self):
        return self.live_content == "live"

    def thumbnail_url(self, quality=2):
        quality = quality if 0 <= quality <= 4 else 4

        table = ("default", "medium", "high", "standard", "maxres")

        return self._thumbnail[table[quality]]["url"]


class YoutubeClient:
    def __init__(self, youtube_client, credential: Credentials):
        self.youtube_client = youtube_client
        self.credential = credential

        self.video_api = self.youtube_client.videos()
        self.channel_api = self.youtube_client.channels()
        self.search_api = self.youtube_client.search()
        self.playlist_item_api = self.youtube_client.playlistItems()
        self.live_streams = self.youtube_client.liveStreams()
        self.live_broadcasts = self.youtube_client.liveBroadcasts()

    def revoke_token(self):
        self.credential.refresh(Request())

    def get_latest_videos(self, channel_id, fetch=3) -> Tuple[Video, ...]:
        # https://stackoverflow.com/a/55373181/10909029

        req = self.playlist_item_api.list(
            part="snippet,contentDetails",
            maxResults=fetch,
            playlistId="UU" + channel_id[2:],
        )
        resp = req.execute()

        return tuple(map(Video, resp["items"]))

    def get_videos_info(self, *video_ids) -> Tuple[Video, ...]:

        req = self.video_api.list(
            part="snippet,contentDetails,statistics", id=",".join(video_ids)
        )
        resp = req.execute()

        return tuple(map(Video, resp["items"]))

    def get_stream_status(self, video_id) -> str:
        # This is most inefficient out of these methods.. but it's way simpler than first code.

        req = self.video_api.list(
            id=video_id, part="snippet", fields="items/snippet/liveBroadcastContent"
        )
        resp = req.execute()

        return resp["items"][0]["snippet"]["liveBroadcastContent"]

    def get_video_title(self, video_id) -> str:

        req = self.video_api.list(
            id=video_id, part="snippet", fields="items/snippet/title"
        )
        resp = req.execute()

        return resp["items"][0]["snippet"]["title"]

    def get_video_description(self, video_id) -> str:

        req = self.video_api.list(
            id=video_id, part="snippet", fields="items/snippet/description"
        )

        resp = req.execute()

        return resp["items"][0]["snippet"]["description"]

    def get_channel_id(self, video_id) -> str:

        req = self.video_api.list(
            id=video_id, part="snippet", fields="items/snippet/channelId"
        )

        resp = req.execute()

        return resp["items"][0]["snippet"]["channelId"]

    def get_subscribers_count(self, channel_id) -> int:

        req = self.channel_api.list(
            id=channel_id,
            part="statistics",
            fields="items/statistics/subscriberCount",
        )

        resp = req.execute()
        return int(resp["items"][0]["statistics"]["subscriberCount"])

    def get_upcoming_streams(self, channel_id: str) -> Tuple[Video, ...]:

        req = self.search_api.list(
            channelId=channel_id, part="snippet", type="video", eventType="upcoming"
        )

        resp = req.execute()
        return tuple(
            vid_info for vid_info in map(Video, resp["items"]) if vid_info.is_upcoming
        )

    def get_live_streams(self, channel_id: str) -> Tuple[Video, ...]:

        req = self.search_api.list(
            channelId=channel_id, part="snippet", type="video", eventType="live"
        )

        resp = req.execute()
        return tuple(
            vid_info for vid_info in map(Video, resp["items"]) if vid_info.is_live
        )

    def get_start_time(self, video_id) -> datetime.datetime:

        req = self.video_api.list(
            id=video_id,
            part="liveStreamingDetails",
            fields="items/liveStreamingDetails/scheduledStartTime",
        )

        resp = req.execute()
        time_string = resp["items"][0]["liveStreamingDetails"]["scheduledStartTime"]

        start_time = isoparse(time_string)

        return start_time

    def get_user_livestream(self, max_results=10):
        """
        Gets authorized user's livestreams.
        Neither I know what's different with broadcasts, but it's different.

        Args:
            max_results:

        Returns:
            Tuple of LiveStream objects if any. Else returns None.
        """

        req = self.live_streams.list(
            part="snippet,status", maxResults=max_results, mine=True
        )

        resp = req.execute()
        return tuple(map(LiveStream, resp["items"]))

    def _get_user_broadcasts(self, status, max_results):
        """
        Gets authorized user's broadcasts.

        Args:
            status: Status to filter with. Supported: "active/all/completed/upcoming/
            max_results: Maximum number of results to get.

        Returns:
            Tuple of LiveStream objects if any. Else returns None.
        """

        req = self.live_broadcasts.list(
            part="snippet,status",
            broadcastStatus=status,
            broadcastType="all",
            maxResults=max_results,
        )

        resp = req.execute()
        return tuple(map(LiveBroadcast, resp["items"]))

    def get_active_user_broadcasts(self, max_results=10):
        """
        Gets authorized user's active broadcasts.

        Args:
            max_results: Maximum number of results to get.

        Returns:
            Tuple of LiveStream objects if any. Else returns None.
        """

        return self._get_user_broadcasts(status="active", max_results=max_results)

    def get_all_user_broadcasts(self, max_results=10):
        """
        Gets authorized user's broadcasts of any status.

        Args:
            max_results: Maximum number of results to get.

        Returns:
            Tuple of LiveStream objects if any. Else returns None.
        """

        return self._get_user_broadcasts(status="all", max_results=max_results)

    def get_completed_user_broadcasts(self, max_results=10):
        """
        Gets authorized user's completed broadcasts.

        Args:
            max_results: Maximum number of results to get.

        Returns:
            Tuple of LiveStream objects if any. Else returns None.
        """

        return self._get_user_broadcasts(status="completed", max_results=max_results)

    def get_upcoming_user_broadcasts(self, max_results=10):
        """
        Gets authorized user's upcoming broadcasts.

        Args:
            max_results: Maximum number of results to get.

        Returns:
            Tuple of LiveStream objects if any. Else returns None.
        """

        return self._get_user_broadcasts(status="upcoming", max_results=max_results)
