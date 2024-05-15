import trio


async def io_task(duration: float):
    await trio.sleep(duration)


async def main():
    async with trio.open_nursery() as nursery:
        # unlike asyncio, one can only spawn task inside nursery
        for n in range(5):
            nursery.start_soon(io_task, n)

        # nursery automatically waits for ALL spawned tasks to end


if __name__ == '__main__':
    trio.run(main)
