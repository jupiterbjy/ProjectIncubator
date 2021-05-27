import socket
from io import StringIO
from contextlib import redirect_stderr, redirect_stdout

import trio

end_signature = "\u200a\u200a\u200a"
end_signature_encoded = end_signature.encode("utf8")


def encode(string: str):
    string += end_signature

    return string.encode("utf8")


def decode(byte_string: bytes):
    decoded = byte_string.decode("utf8")

    return decoded.removeprefix(end_signature)


async def receive():
    server = trio.socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    await server.bind(("172.17.0.1", 5901))
    server.listen(10)

    while True:
        connection, address = await server.accept()

        data = b""

        while received := await connection.recv(1024):
            data += received

            if end_signature_encoded in data:
                break

        decoded = data.decode("utf8")

        output = StringIO()

        with redirect_stderr(output), redirect_stdout(output):
            try:
                exec(decoded)
            except Exception as err:
                print(err)

        await connection.send(encode(output.read()))


while True:
    try:
        trio.run(receive)
    except Exception as err_:
        print(err_)
