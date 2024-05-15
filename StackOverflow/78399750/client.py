"""
Demonstration of AsyncContextManager usage for network
"""

import asyncio
import logging
import itertools
from typing import Union


logger = logging.getLogger()
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


SERVERS = (
    ("127.0.0.1", 9001),
    ("127.0.0.1", 9002),
    ("127.0.0.1", 9003),
)

# really, really, bad way to check matching protocol
HANDSHAKE_SEND_PHRASE = "Do you love me?".encode()
HANDSHAKE_RECV_PHRASE = "I can really move!".encode()


class AsyncSocketClient:
    uid_gen = itertools.count()

    def __init__(self, url: str, port):
        self.url = url
        self.port = port
        self.uid = next(self.uid_gen)

        self._reader: Union[asyncio.StreamReader, None] = None
        self._writer: Union[asyncio.StreamWriter, None] = None

    async def _connect_n_validate(self):
        """Connect and validate opponent. Raises AssertionError on protocol mismatch."""

        logger.info(f"[{self.uid}] Connecting to {self.url}:{self.port}")
        self._reader, self._writer = await asyncio.open_connection(self.url, self.port)

        logger.info(f"[{self.uid}] Connected! Sending credential")
        self._writer.write(HANDSHAKE_SEND_PHRASE)
        await self._writer.drain()

        logger.info(f"[{self.uid}] Awaiting server response")
        assert HANDSHAKE_RECV_PHRASE == await self._reader.read(1024), "Protocol mismatch"

        logger.info(f"[{self.uid}] Connection validated!")

        # send anything as ack
        self._writer.write(" ".encode())
        await self._writer.drain()

        logger.info(f"[{self.uid}] Handshake done!")

    async def _ensure_connection_close(self):
        """Closes & wait for send buffer to be drained,
        and finally connection's terminated"""

        logger.info(f"[{self.uid}] Closing connection to {self.url}:{self.port}")
        self._writer.close()
        await self._writer.wait_closed()

    async def __aenter__(self) -> asyncio.StreamReader:
        try:
            await self._connect_n_validate()
        except AssertionError:
            # Oops, dialed wrong home. close active connection then rethrow
            if self._writer:
                await self._ensure_connection_close()

            raise
        return self._reader

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb):
        await self._ensure_connection_close()


async def some_io_task(url: str, port: int):
    """Establish 'secure' connection and receive some data"""

    async with AsyncSocketClient(url, port) as reader:
        _ = await reader.read(1024)
        logger.info(f"Receive done from {url}")


async def main():
    tasks = [
        asyncio.create_task(some_io_task(url, port)) for url, port in SERVERS
    ]

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
