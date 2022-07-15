"""
Task shielding demonstration with pure asyncio, nix only
"""
import asyncio
import signal
import os


# Sets of tasks we shouldn't cancel
REQUIRE_SHIELDING = set()


async def work(n):
    """Some random io intensive work to test shielding"""
    print(f"[{n}] Task start!")
    try:
        await asyncio.sleep(10)

    except asyncio.CancelledError:
        # we shouldn't see following output
        print(f"[{n}] Canceled!")
        return

    print(f"[{n}] Task done!")


def install_handler():

    def handler(sig_name):
        print(f"Received {sig_name}")

        # distinguish what to await and what to cancel. We'll have to await all,
        # but we only have to manually cancel subset of it.
        to_await = asyncio.all_tasks()
        to_cancel = to_await - REQUIRE_SHIELDING

        # cancel tasks that don't require shielding
        for task in to_cancel:
            task.cancel()

        print(f"Cancelling {len(to_cancel)} out of {len(to_await)}")

    loop = asyncio.get_running_loop()

    # install for SIGINT and SIGTERM
    for signal_name in ("SIGINT", "SIGTERM"):
        loop.add_signal_handler(getattr(signal, signal_name), handler, signal_name)


async def main():
    print(f"PID: {os.getpid()}")

    # If main task is done - errored or not - all other tasks are canceled.
    # So we need to shield main task.
    REQUIRE_SHIELDING.add(asyncio.current_task())

    # install handler
    install_handler()

    # spawn tasks that will be shielded
    for n in range(3):
        REQUIRE_SHIELDING.add(asyncio.create_task(work(n)))

    # spawn tasks that won't be shielded, for comparison
    for n in range(3, 6):
        asyncio.create_task(work(n))

    # we'll need to keep main task alive until all other task excluding self is done.
    await asyncio.gather(*(REQUIRE_SHIELDING - {asyncio.current_task()}))

asyncio.run(main())
