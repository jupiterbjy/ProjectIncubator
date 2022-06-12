import argparse
import pathlib
import json
import time
import traceback
from typing import Iterable

import asyncio
from pytchat import LiveChatAsync, ChatDataFinished, LiveChat
from pytchat.exceptions import InvalidVideoIdException
from pytchat.processors.default.processor import Chatdata, Chat
from loguru import logger


HARD_CODED_LIST = {"_va6BiOYaZo"}

ROOT = pathlib.Path(__file__).parent.joinpath("fetched")
ROOT.mkdir(exist_ok=True)


def workload(vid_id):
    data = []
    vid_path = ROOT.joinpath(vid_id + ".json")

    if vid_path.exists():
        logger.critical("File already exists for stream {}", vid_id)
        return

    logger.debug("task {} started", vid_id)

    def callback(chat_data: Chatdata):

        logger.debug("Processing Data")

        for chat in chat_data.items:
            chat: Chat
            json_data: dict = json.loads(chat.json())
            logger.debug(f"S:[{json_data['author']['name']}][{json_data['timestamp']}][{json_data['message']}]")
            data.append(json_data)

    try:
        # live_chat = LiveChatAsync(vid_id, callback=callback)
        live_chat = LiveChat(vid_id, callback=callback, force_replay=True)
    except Exception:
        raise
    else:
        while live_chat.is_alive():
            time.sleep(3)

        try:
            live_chat.raise_for_status()
        except ChatDataFinished:
            logger.info("Chat data finished.")
        except Exception:
            raise

    if data:
        new_dict = {idx: chat_json for idx, chat_json in enumerate(data)}
        vid_path.write_text(json.dumps(new_dict, indent=2), encoding="utf8")

        logger.info("Written {} chats for {}", len(data), vid_id)
    else:
        logger.warning("No data to write")


def workload_wrapper(vid_id, invalid_list: list):
    logger.info("Starting task {}", vid_id)

    try:
        workload(vid_id)
    except Exception:
        invalid_list.append(vid_id)
        traceback.print_exc()


def main():
    invalid_list = []

    for vid_id in HARD_CODED_LIST:
        workload_wrapper(vid_id, invalid_list)

    if invalid_list:
        logger.critical("Following videos failed to load: {}", invalid_list)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--channel",
        metavar="ID",
        default="UC9wbdkwvYVSgKtOZ3Oov98g",
        help="ID of yt channel",
    )

    args = parser.parse_args()
    main()
