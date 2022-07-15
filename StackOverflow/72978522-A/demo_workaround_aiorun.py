"""
Task shielding demonstration with asyncio + aiorun, all OS
"""
import asyncio
import os

from aiorun import run, shutdown_waits_for


async def work(n):
    """Some random io intensive work to test shielding"""
    print(f"[{n}] Task start!")
    try:
        await asyncio.sleep(10)

    except asyncio.CancelledError:
        print(f"[{n}] Canceled!")
        return

    print(f"[{n}] Task done!")


async def main():
    print(f"PID: {os.getpid()}")
    child_tasks = []

    # spawn tasks that will be shielded
    child_tasks.extend(
        asyncio.create_task(shutdown_waits_for(work(n))) for n in range(3)
    )

    # spawn tasks without shielding for comparison
    child_tasks.extend(asyncio.create_task(work(n)) for n in range(3))

    # aiorun runs forever by default, even without any coroutines left to run.
    # We'll have to manually stop the loop, but can't use asyncio.all_tasks()
    # check as aiorun's internal tasks included in it run forever.
    # instead, keep child task spawned by main task and await those.
    await asyncio.gather(*child_tasks)
    asyncio.get_running_loop().stop()


run(main())
