"""
Demo codes for https://stackoverflow.com/q/71416383/10909029

Showing canceling(not really) task running in thread

Python nor OS provide general mechanism to stop an arbitrary thread running synchronous code
"""

import time
import asyncio


def blocking_func(event: asyncio.Event):
    while not event.is_set():
        time.sleep(1)
        print("I'm still standing")


async def main():
    event = asyncio.Event()
    asyncio.create_task(asyncio.to_thread(blocking_func, event))

    await asyncio.sleep(5)
    # now lets stop
    event.set()

asyncio.run(main())
