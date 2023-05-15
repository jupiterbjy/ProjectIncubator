"""
Demo codes for https://stackoverflow.com/questions/76232207
"""


import asyncio

import httpx


async def request_task(id_, in_queue: asyncio.Queue, out_queue: asyncio.Queue):
    """Get json response data from url in queue. It's Consumer and also Producer.

    Args:
        id_: task ID
        in_queue: Queue for receiving url
        out_queue: Queue for returning data
    """
    print(f"[Req. Task {id_}] Started!")

    # create context for each task
    async with httpx.AsyncClient() as client:
        while True:
            user = await in_queue.get()
            print(f"[Req. Task {id_}] Processing user '{user}'")

            data = await client.get("http://127.0.0.1:5000/json?user=" + str(user))

            # do what you want here
            print(f"[Req. Task {id_}] Received {data}")
            await out_queue.put(data)

            # inform queue that we are done with data we took
            in_queue.task_done()


async def main():
    """
    Starter code
    """

    # create queues
    in_queue = asyncio.Queue()
    out_queue = asyncio.Queue()

    # create consumer tasks
    pool = [asyncio.create_task(request_task(n, in_queue, out_queue)) for n in range(3)]

    # populate queue with numbers as user's name
    for n in range(30):
        in_queue.put_nowait(n)

    # wait for enqueued works are complete
    await in_queue.join()

    # cancel tasks
    for task in pool:
        task.cancel()

    # check data
    print(f"[Main task] Processed {out_queue.qsize()} data!")


if __name__ == '__main__':
    asyncio.run(main())
