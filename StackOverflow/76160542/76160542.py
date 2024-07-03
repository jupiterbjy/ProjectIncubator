"""Sample script to test asyncio functionality."""

import asyncio
import time


async def wait(i: int) -> None:
    print(f"Task {i} started!")

    try:
        await asyncio.sleep(5)
    except (asyncio.CancelledError, KeyboardInterrupt):
        print(f"Task {i} canceled!")
        raise

    print(f"Task {i} done!")


async def main() -> None:
    """The main."""
    tasks = [asyncio.create_task(wait(i)) for i in range(10)]

    print("Blocking main thread for 5 sec!")
    time.sleep(5)

    print("End of main!")


if __name__ == "__main__":
    asyncio.run(main=main())
    print("asyncio loop stopped!")
