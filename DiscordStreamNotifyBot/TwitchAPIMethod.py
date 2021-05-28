#!/usr/bin/python3

import argparse
import itertools
import pathlib
import time
import json
from collections import deque
from datetime import timedelta, datetime
from typing import Tuple, Callable

import requests
from traceback_with_variables import activate_by_import
from loguru import logger

from youtube_api_client import GoogleClient, HttpError
from DiscordMessaging import webhook_closure, embed_closure


YOUTUBE_FETCH_MAX_RETRY = 3


def get_new_token(client_id, client_secret) -> Tuple[str, int]:
    url = "https://id.twitch.tv/oauth2/token?client_id={}&client_secret={}&grant_type=client_credentials&scope="

    formatted = url.format(client_id, client_secret)
    logger.debug(formatted)

    req = requests.post(formatted)

    dict_ = req.json()

    token = dict_["access_token"]
    expires_in = dict_["expires_in"]

    return token, expires_in


class RequestInstance:
    def __init__(self, channel_name, client_id, client_secret, callback: Callable, interval, expire_margin=0.3):
        self.client_id = client_id
        self.client_secret = client_secret
        self.expire_margin = expire_margin

        self.channel_name = channel_name
        self.header = {}
        self.next_check = datetime.now()

        self.cached = deque(maxlen=5)

        self.generate_new_header()

        self.callback = callback
        self.interval = interval

    def generate_new_header(self):
        token, eta = get_new_token(self.client_id, self.client_secret)

        self.next_check = datetime.now() + timedelta(seconds=round(eta * self.expire_margin))

        header = {
            "Authorization": f"Bearer {token}",
            "Client-ID": f"{self.client_id}"
        }

        logger.info("Got token [{}]. Will expire in {}", token, (self.next_check - datetime.now()).seconds)

        self.header = header

    def start_checking(self):
        request_url = f"https://api.twitch.tv/helix/search/channels?query={self.channel_name}"

        with requests.session() as session:
            while True:
                while datetime.now() < self.next_check:
                    req = session.get(request_url, headers=self.header)
                    dict_ = req.json()["data"][0]

                    start_time = dict_["started_at"]

                    if start_time and start_time not in self.cached:
                        self.cached.append(start_time)
                        logger.info("Found a stream started at {}", start_time)

                        self.callback()

                    logger.debug("Rate left: {} Date: {}", req.headers["Ratelimit-Remaining"], req.headers["Date"])

                    time.sleep(2)

                # Get new token
                self.generate_new_header()


def callback_discord_notify_closure(discord_webhook, google_api_client: GoogleClient, json_data):
    # Check youtube side live streams

    channel_list = json_data["channels"]
    embed_builder = embed_closure(json_data)

    content = json_data["content"]

    def inner():
        for _ in range(YOUTUBE_FETCH_MAX_RETRY):
            try:
                live = list(itertools.chain(*map(google_api_client.get_live_streams, channel_list)))
            except HttpError as err:
                logger.critical("HttpError, did quota exceeded?\nDetails: {}", err)
                return

            if live:
                vid_id = live[0]
                description = google_api_client.get_video_description(vid_id)

                embed = embed_builder(vid_id, description)
                discord_webhook(content=content, embeds=[embed])
                logger.info("Sent live notification to discord.")
                return

            time.sleep(1)

        logger.critical("Failed to fetch youtube video after {} trials.", YOUTUBE_FETCH_MAX_RETRY)

    return inner


def main():

    json_data = json.loads(args.path.read_text(encoding="utf8"))

    logger.info("Target Channel: {}", json_data['channels'])

    bot = webhook_closure(args.url)
    client = GoogleClient(args.api)

    callback = callback_discord_notify_closure(bot, client, json_data)

    req_instance = RequestInstance(args.twitch_channel_name, args.client_id, args.client_secret, callback, args.interval)

    req_instance.start_checking()


if __name__ == "__main__":

    # parsing start =================================

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "twitch_channel_name",
        type=str,
        help="Twitch channel name",
    )
    parser.add_argument(
        "client_id",
        type=str,
        help="Twitch Application ID",
    )
    parser.add_argument(
        "client_secret",
        type=str,
        help="Twitch Application Secret",
    )
    parser.add_argument(
        "api",
        type=str,
        help="Google Data API key",
    )
    parser.add_argument(
        "url",
        type=str,
        help="Discord webhook url",
    )
    parser.add_argument(
        "-p",
        "--path",
        metavar="CONFIG_PATH",
        type=pathlib.Path,
        default=pathlib.Path(__file__).absolute().parent.joinpath("configuration.json"),
        help="Path to configuration json file. Default path is 'configuration.json' adjacent to this script",
    )
    parser.add_argument(
        "-i",
        "--interval",
        metavar="INTERVAL",
        type=int,
        default=1,
        help="interval between checks in seconds. Default is 1.",
    )

    args = parser.parse_args()

    # parsing end ===================================

    main()
