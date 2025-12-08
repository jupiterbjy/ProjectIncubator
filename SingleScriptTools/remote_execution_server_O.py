"""
> WARNING: This is VERY UNSAFE and should not be used in general.

Copied from [gist](https://gist.github.com/jupiterbjy/dcf4dd27784c80369b76c65d2077b643)

Prototype written back in (probably) 2021, this was created to test feasibility of running python scripts
from discord without exposing the bot host, and this is server part of bot's
[module](https://github.com/jupiterbjy/Meow_py/tree/main/Meowpy/BotComponents/PythonExecution).

This listens for incoming connections and execute received python codes.
Obviously this is very dangerous. This is to be run on overlayFS with Raspbian.

![](readme_res/remote_execution_server_0.png)

![](readme_res/remote_execution_server_1.png)

:Author: jupiterbjy@gmail.com
"""

import subprocess
import itertools

import trio

from loguru import logger
from sys import executable


end_signature = "\u200a\u200a\u200a"
EOF_ = end_signature.encode("utf8")
TIMEOUT = 10
COUNTER = itertools.count()


logger.add(
    "/home/pyexec/py_{time}.log",
    rotation="5 MB",
    retention="7 days",
    compression="zip",
)


def encode(string: str):
    string += end_signature

    return string.encode("utf8")


def decode(byte_string: bytes):
    decoded = byte_string.decode("utf8")

    return decoded.removeprefix(end_signature)


async def try_to_send(stream: trio.SocketStream, bytes_, ident):
    logger.debug("[{}] Sending back {} bytes", ident, len(bytes_))
    try:
        await stream.send_all(bytes_)

    except Exception as err_:
        logger.critical("[{}] Could not send, reason: {}", ident, err_)
    else:
        logger.info("[{}] Sent {}", ident, len(bytes_))


async def receive(stream: trio.SocketStream, ident):
    data_ = b""

    logger.debug("[{}] Receiving", ident)

    while not data_.endswith(EOF_):
        data_ += await stream.receive_some()

    logger.info("[{}] Received {}", ident, len(data_))

    return data_


async def handler(stream: trio.SocketStream):
    ident = next(COUNTER)
    logger.debug("[{}] Receiving connection.", ident)

    # trio will fail when handler raises exception.
    # need to prevent it to keep server working, in case for unexpected
    try:
        try:
            data = await receive(stream, ident)
        except Exception as err_:
            logger.critical(err_)
            await try_to_send(stream, encode(str(err_)), ident)

        else:

            decoded = decode(data).strip()

            logger.debug("[{}] Executing code: \n{}", ident, decoded)

            try:
                with trio.fail_after(TIMEOUT):
                    proc = await trio.run_process(
                        [executable, "-c", decoded],
                        capture_stdout=True,
                        stderr=subprocess.STDOUT,
                        check=False,
                    )

            except trio.TooSlowError:
                logger.critical("[{}] Got timeout executing script.", ident)
                await try_to_send(
                    stream,
                    encode(f"Reached {TIMEOUT} seconds timeout limit while executing."),
                    ident
                )

            except Exception as err_:
                logger.critical("[{}] Got an error.\nDetails: {}", ident, err_)
                await try_to_send(stream, encode(str(err_)), ident)

            else:
                stdout = proc.stdout

                return_code = f"Return code was {proc.returncode}"
                output = (
                    f"```\n{stdout.decode('utf8')}```\n{return_code}"
                    if stdout
                    else return_code
                )

                await try_to_send(stream, encode(output), ident)

        finally:
            await stream.send_eof()
            logger.debug("[{}] Connection closed.", ident)
    except Exception as err_:
        logger.critical("[{}] Handler failed!\nDetail: {}", ident, err_)


async def main_routine():
    logger.info(f"Server starting.")
    await trio.serve_tcp(handler, 8123, task_status=trio.TASK_STATUS_IGNORED)


trio.run(main_routine)
