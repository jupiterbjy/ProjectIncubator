import argparse
import pathlib
import json
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

CONCURRENCY_LIMIT = 3


class QueueEmtpy(Exception):
    pass


class LimitingQueue:
    def __init__(self, initial_val: Iterable, max_concurrency=10):
        self.max_concurrency = max_concurrency
        self._interval_list = [n for n in initial_val]
        self._issued_works_count = 0

    async def _wait_async(self, nowait=False):
        if self._issued_works_count < self.max_concurrency:
            self._issued_works_count += 1
            return
        else:
            while not nowait:
                await asyncio.sleep(0.5)
                if self._issued_works_count < self.max_concurrency:
                    self._issued_works_count += 1
                    return

            raise RuntimeError("Max number of tasks are issued.")

    async def get_async(self):
        await self._wait_async()

        try:
            return self._interval_list.pop()
        except IndexError as err:
            raise QueueEmtpy() from err

    def task_done(self):
        if self._issued_works_count:
            self._issued_works_count -= 1
        else:
            raise RuntimeError("No tasks has been issued!")

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return await self.get_async()
        except QueueEmtpy:
            raise StopAsyncIteration


async def workload(vid_id):
    data = []
    vid_path = ROOT.joinpath(vid_id + ".json")

    if vid_path.exists():
        logger.critical("File already exists for stream {}", vid_id)
        return

    logger.debug("task {} started", vid_id)

    async def callback(chat_data: Chatdata):

        logger.debug("Processing Data")

        async for chat in chat_data.async_items():
            chat: Chat
            json_data: dict = json.loads(chat.json())
            logger.debug(f"S:[{json_data['author']['name']}][{json_data['timestamp']}][{json_data['message']}]")
            data.append(json_data)

    try:
        # live_chat = LiveChatAsync(vid_id, callback=callback)
        live_chat = LiveChatAsync(vid_id, callback=callback, force_replay=True, direct_mode=True)
    except Exception:
        raise
    else:
        while live_chat.is_alive():
            await asyncio.sleep(5)

        try:
            live_chat.raise_for_status()
        except ChatDataFinished:
            logger.info("Chat data finished.")
        except Exception:
            raise

    new_dict = {idx: chat_json for idx, chat_json in enumerate(data)}
    vid_path.write_text(json.dumps(new_dict, indent=2), encoding="utf8")

    logger.info("Written {} chats for {}", len(data), vid_id)


async def workload_wrapper(queue: LimitingQueue, worker_id, invalid_list: list):
    async for vid_id in queue:
        logger.info("Worker {} Starting task {}", worker_id, vid_id)

        try:
            await workload(vid_id)
        except InvalidVideoIdException:
            traceback.print_exc()
            invalid_list.append(vid_id)

        finally:
            queue.task_done()


async def main_routine():
    limit = CONCURRENCY_LIMIT
    # ch_id = args.channel

    # TODO: add finished stream fetching feature

    invalid_list = []
    queue = LimitingQueue(HARD_CODED_LIST)

    if len(HARD_CODED_LIST) < limit:
        limit = len(HARD_CODED_LIST)

    tasks = tuple(workload_wrapper(queue, n, invalid_list) for n in range(limit))

    await asyncio.gather(*tasks)

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

    asyncio.run(main_routine())
