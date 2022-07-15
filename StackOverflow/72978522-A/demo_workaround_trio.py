"""
Task shielding demonstration with trio, all OS
"""
import os

import trio


async def work(n):
    """Some random io intensive work to test shielding"""
    print(f"[{n}] Task start!")
    try:
        await trio.sleep(10)

    except trio.Cancelled:
        print(f"[{n}] Canceled!")
        raise

    print(f"[{n}] Task done!")


async def shielded():
    # opening explicit concurrency context.
    # Every concurrency in trio is explicit, via Nursery that takes care of tasks.
    async with trio.open_nursery() as nursery:

        # shield nursery from cancellation. Now all tasks in this scope is shielded.
        nursery.cancel_scope.shield = True

        # spawn tasks
        for n in range(3):
            nursery.start_soon(work, n)


async def main():
    print(f"PID: {os.getpid()}")

    try:
        async with trio.open_nursery() as nursery:
            nursery.start_soon(shielded)

            for n in range(3, 6):
                nursery.start_soon(work, n)

    except (trio.Cancelled, KeyboardInterrupt):
        # Nursery always make sure all child tasks are done - either canceled or not.
        # This try-except is just here to suppress traceback. Not quite required.
        print("Nursery Cancelled!")


trio.run(main)
