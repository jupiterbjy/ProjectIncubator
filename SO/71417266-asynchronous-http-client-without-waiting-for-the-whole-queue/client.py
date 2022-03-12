"""
Demo codes for https://stackoverflow.com/questions/71417266
"""


import asyncio
from typing import Dict

import aiohttp


async def process_response_queue(queue: asyncio.Queue):
    """
    Get json response data from queue.
    Effectively consumer.

    Args:
        queue: Queue for receiving url & json response pair
    """
    print("Processor started")

    while True:
        url_from, data = await queue.get()

        # do what you want here
        print(f"Received {data} from {url_from}")


class TaskManager:
    """
    Manage data fetching tasks
    """

    def __init__(self):
        self.queue = asyncio.Queue()
        self.tasks: Dict[str, asyncio.Task] = {}

    async def get_repeat(self, url, timeout=20):
        """
        Repeatedly fetch json response from given url and put into queue.
        Effectively producer.

        Args:
            url: URL to fetch from
            timeout: Time until timeout
        """
        print(f"Task for {url} started")

        try:
            async with aiohttp.ClientSession() as session:
                while True:
                    async with session.get(url, timeout=timeout) as resp:
                        await self.queue.put((url, await resp.json()))
        finally:
            del self.tasks[url]
            print(f"Task for {url} canceled")

    def start_processor(self):
        """
        Starts the processor.
        """
        self.tasks["_processor"] = asyncio.create_task(process_response_queue(self.queue))

    def start_new_task(self, url):
        """
        Create new task from url.

        Args:
            url: URL to fetch from.
        """
        self.tasks[url] = asyncio.create_task(self.get_repeat(url))

    def stop_task(self, url):
        """
        Stop existing task associated with url.

        Args:
            url: URL associated with task.

        Raises:
            KeyError: If no task associated with given url exists.
        """
        self.tasks[url].cancel()

    def close(self):
        """
        Cancels all tasks
        """

        for task in self.tasks.values():
            task.cancel()


async def main():
    """
    Starter code
    """

    task_manager = TaskManager()

    task_manager.start_processor()

    for n in range(5):
        task_manager.start_new_task(f"http://127.0.0.1:5000/json?key={n}")

    # wait 10 sec
    await asyncio.sleep(10)

    # cancel 1 task
    task_manager.stop_task("http://127.0.0.1:5000/json?key=3")

    # wait 20 sec
    await asyncio.sleep(20)

    # stop all
    task_manager.close()


if __name__ == '__main__':
    asyncio.run(main())
