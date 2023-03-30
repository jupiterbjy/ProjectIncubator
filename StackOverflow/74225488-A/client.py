"""
Async download iterator demo - client code
"""

import asyncio
import random
from typing import Tuple, AsyncIterator

import aiohttp


URL = r"http://127.0.0.1:8000"


async def dl_worker(
    session: aiohttp.ClientSession,
    worker_id: int,
    work_q: asyncio.Queue,
    done_q: asyncio.Queue,
    timeout: int,
):
    """Asynchronously download and return result.

    Args:
        session: aiohttp client session
        worker_id: worker's ID
        work_q: URL queue
        done_q: work submit queue
        timeout: maximum waiting seconds before terminating
    """
    print(f"[Worker {worker_id}] Started")

    while True:
        try:
            # await next url with timeout.
            url = await asyncio.wait_for(work_q.get(), timeout=timeout)

        except asyncio.TimeoutError:
            # Timeout waiting for url, then consider it end of operation.
            print(f"[Worker {worker_id}] Timeout, Terminating!")
            return

        # otherwise get from url and put to done queue.
        async with session.get(url) as req:
            print(f"[Worker {worker_id}] Got data for {url}")
            await done_q.put((url, await req.read()))


def dl_multiple(
    session: aiohttp.ClientSession,
    work_q: asyncio.Queue,
    done_q: asyncio.Queue,
    max_worker_n=5,
    timeout=10,
) -> AsyncIterator[Tuple[str, bytes]]:
    """Asynchronously download urls in queue.

    Args:
        session: aiohttp client session
        work_q: URL queue
        done_q: work submit queue
        max_worker_n: maximum # of workers
        timeout: maximum waiting seconds before terminating

    Returns:
        iterator yielding results
    """

    print("[Downloader] Starting!")

    # spawn tasks
    tasks = [
        asyncio.create_task(dl_worker(session, n, work_q, done_q, timeout))
        for n in range(max_worker_n)
    ]

    # keepalive them as task. Using 'None' as sentinel for work queue
    async def keepalive():
        await asyncio.gather(*tasks)
        print("[Downloader] Done, terminating iterator")
        await done_q.put(None)

    asyncio.create_task(keepalive())

    # define and return async generator
    async def inner_gen():
        # while result is not None keep yielding
        while result := await done_q.get():
            print(f"[Iterator] Yielding result of {result[0]}")
            yield result

    return inner_gen()


async def populate_url_queue(queue: asyncio.Queue):
    """Generates random URL targets with intentional delay"""

    # just replace range() with your generator.
    for _ in range(50):

        await queue.put(f"{URL}/{random.randint(3, 20)}")
        await asyncio.sleep(1)


async def main():
    work_queue = asyncio.Queue()
    done_queue = asyncio.Queue()

    # start url queue populating task
    asyncio.create_task(populate_url_queue(work_queue))

    async with aiohttp.ClientSession() as session:

        # demonstrating iterating the downloads
        async for url, data in dl_multiple(session, work_queue, done_queue):
            print(f">> Received {len(data)} from {url}")


if __name__ == "__main__":
    asyncio.run(main())
