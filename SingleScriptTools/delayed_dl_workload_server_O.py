"""
Async trio server for slow download simulation.

```text
http://<URL>/<SIZE_IN_BYTES>?interval=<INTERVAL_MS>&chunk=<CHUNK_SIZE_IN_BYTES>
```

e.g.:
```text
http://localhost:8000/2000000?interval=1&chunk=32768
```

Parameters are optional.

Based on 2022 [gist](https://gist.github.com/jupiterbjy/b0ad9a4dca162195aa0673b69e0af5cd)

:Author: jupiterbjy@gmail.com
"""

import random
import time
from argparse import ArgumentParser

import trio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.datastructures import Address
from hypercorn.config import Config
from hypercorn.trio import serve

from loguru import logger


app = FastAPI()


async def fake_stream_gen(
    total_bytes: int, interval_ms: int, chunk_bytes: int, client_addr: Address
):
    """
    Stream random bytes at given path with delay, to simulate DL speed.
    """
    
    total_m_bytes = total_bytes / 1000000
    session_info = f"{client_addr.host}:{client_addr.port} - {total_m_bytes:.2f} MB"

    logger.info("[{}] transfer started", session_info, total_bytes)

    remaining_bytes = total_bytes
    start_t = time.time()

    try:
        if interval_ms > 0:
            interval_sec = interval_ms / 1000.0

            while remaining_bytes > 0:
                await trio.sleep(interval_sec)

                if remaining_bytes < chunk_bytes:
                    chunk_bytes = remaining_bytes

                yield random.randbytes(chunk_bytes)

                remaining_bytes -= chunk_bytes
        
        else:
            while remaining_bytes > 0:
                if remaining_bytes < chunk_bytes:
                    chunk_bytes = remaining_bytes

                yield random.randbytes(chunk_bytes)

                remaining_bytes -= chunk_bytes
    
    except trio.Cancelled:
        logger.info("[{}] transfer canceled", session_info)
        raise

    end_t = time.time()
    logger.info("[{}] transfer complete in {:.2f} sec", session_info, end_t - start_t)


@app.get("/{size_bytes}")
async def send_file(
    size_bytes: int, request: Request, interval: int = 0, block_size: int = 4096
):
    """
    Args:
        size_bytes: Total download size in bytes
        interval: Interval between transmission
        block_size: Block size in bytes
    """

    return StreamingResponse(
        fake_stream_gen(size_bytes, interval, block_size, request.client),
        media_type="application/octet-stream",
        headers={
            "Content-Length": str(size_bytes),
        },
    )


if __name__ == '__main__':
    _parser = ArgumentParser()
    _parser.add_argument(
        "-a", "--address", type=str, default="0.0.0.0"
    )
    _parser.add_argument(
        "-p", "--port", type=int, default=8000
    )

    _args = _parser.parse_args()

    _config = Config()
    _config.bind = f"{_args.address}:{_args.port}"

    trio.run(serve, app, _config)
