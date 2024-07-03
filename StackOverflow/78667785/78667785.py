import asyncio
import pathlib
import logging
from typing import Sequence, List

# --- Logging setup ---

LOG = logging.getLogger(__name__)

# logging format with "time [log level] <function> message"
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] <%(funcName)s> %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


# --- Logics ---

async def fetch(some_data) -> dict:
    """Some fake request that takes time to complete."""

    LOG.info("Fetching data...")
    await asyncio.sleep(0.5)
    return {"some_key": some_data}


async def task(items: Sequence[Sequence[str]], request_q: asyncio.Queue) -> None:

    # Read tasks from source of data

    for item in items:
        await request_q.put(
            asyncio.create_task(fetch({"data": item}))
        )

    # Sentinel value to signal we are done receiving from source
    await request_q.put(None)


async def request_task(request_q: asyncio.Queue, response_q: asyncio.Queue) -> None:

    while req := await request_q.get():
        print(f"INFO: request from request_q: {req}")

        # If we received sentinel for tasks, pass message to next queue
        if req is None:
            print(f"INFO: request in request_task: {req}")
            print("INFO: received sentinel from request_q")
            request_q.task_done()
            await response_q.put(None)
            break

        # Make the request which will put data into the response queue
        resp = await req
        print(f"INFO: response in request_task: {resp}")
        await response_q.put(resp)
        request_q.task_done()


async def response_task(response_q: asyncio.Queue, write_q: asyncio.Queue) -> None:
    while True:

        # Retrieve response
        resp = await response_q.get()

        # If we received sentinel for tasks, pass message to next queue
        if not resp:
            print("INFO: received sentinel from response_q")
            response_q.task_done()
            await write_q.put(None)
            break

        await write_q.put(resp)
        response_q.task_done()


async def async_write(file_path: pathlib.Path, content: str) -> None:
    """Delegate file writing to a thread."""

    await asyncio.to_thread(file_path.write_text, content, "utf-8")


async def write_task(write_q: asyncio.Queue) -> None:
    while data := await write_q.get():
        print(f"INFO: data in write_task: {data}")

        if data is None:
            print("INFO: received sentinel from write_q")
            write_q.task_done()
            break

        print("INFO: finished write task")
        write_q.task_done()


async def main() -> None:
    # Create fake data to POST
    items: List[List[str]] = [["hello", "world"], ["asyncio", "test"]]

    # Queues for orchestrating
    request_q = asyncio.Queue()
    response_q = asyncio.Queue()
    write_q = asyncio.Queue()

    # one producer
    producer = asyncio.create_task(
        task(items, request_q)
    )

    # 5 request consumers
    request_consumers = [
        asyncio.create_task(
            request_task(request_q, response_q)
        )
        for _ in range(5)
    ]

    # 5 response consumers
    response_consumers = [
        asyncio.create_task(
            response_task(response_q, write_q)
        )
        for _ in range(5)
    ]

    # 5 write consumers
    write_consumer = asyncio.create_task(
        write_task(write_q)
    )

    errors = await asyncio.gather(producer, return_exceptions=True)
    print(f"INFO: Producer has completed! exceptions: {errors}")

    await request_q.join()
    for c in request_consumers:
        c.cancel()
    print("INFO: request consumer has completed! ")

    await response_q.join()
    for c in response_consumers:
        c.cancel()
    print("INFO: response consumer has completed! ")
    print(f"INFO: write_q address in main: {id(write_q)}")
    print(f"INFO: write_q in main qsize: {write_q.qsize()}")

    await write_q.join()
    await write_consumer
    print("INFO: write consumer has completed! ")
    print("INFO: Complete!")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
