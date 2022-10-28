"""
Async trio server for download testing
"""

import random

import trio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from hypercorn.config import Config
from hypercorn.trio import serve

from loguru import logger


app = FastAPI()


async def fake_stream_gen(length: int, client_ip, interval=1, block_size=4096):
    """Stream random bytes at given path with delay, to simulate DL speed.

    Args:
        length: Number of blocks to stream.
        client_ip: Client ip, literally.
        interval: Interval between iteration, essentially sleep time per block.
        block_size: Block size in bytes

    Raises:
        FileNotFoundError - when there's no such file
    """

    logger.info("{} - File transfer started", client_ip)

    for _ in range(length):

        await trio.sleep(interval)
        yield random.randbytes(block_size)

    logger.info("{} - File transfer complete", client_ip)


@app.get("/{file_size}")
async def send_file(file_size: int, request: Request):
    logger.info("{} - Requesting {}", request.client, file_size)

    return StreamingResponse(fake_stream_gen(file_size, request.client))


if __name__ == '__main__':
    trio.run(serve, app, Config())
