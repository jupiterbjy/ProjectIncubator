"""
Serverside code
"""

import asyncio


HOST = "127.0.0.1"
PORTS = [9001, 9002, 9003]


# really, really, bad way to check matching protocol
HANDSHAKE_RECV_PHRASE = "Do you love me?".encode()
HANDSHAKE_SEND_PHRASE = "I can really move!".encode()


async def callback(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    print("Connected")

    # if not valid close and return
    if HANDSHAKE_RECV_PHRASE != await reader.read(1024):
        writer.close()
        await writer.wait_closed()

    try:
        # valid, send our phrase
        writer.write(HANDSHAKE_SEND_PHRASE)
        await writer.drain()

        # wait for any write as ack
        await reader.read(1024)

        # now send some data
        writer.write("Sorasaki hina".encode())
        await writer.drain()

    # close
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    servers = [
        await asyncio.start_server(callback, HOST, port) for port in PORTS
    ]

    for server in servers:
        await server.start_serving()
        print(server)

    try:
        while True:
            await asyncio.sleep(10000)
    finally:
        await asyncio.gather(*servers)


if __name__ == '__main__':
    asyncio.run(main())
