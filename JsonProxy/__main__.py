from sys import path
from os.path import abspath

from quart_trio import QuartTrio
import trio

path.append(abspath(".."))
from TinyTools.LoggingConfigurator import logger


app = QuartTrio(__name__)


async def wrap_background_task(coro_function, *args):
    try:
        await coro_function(*args)
    except (trio.MultiError, Exception) as err:
        logger.critical(str(err))


@app.route('/modify_json/<value>')
async def modify(value):

    return f"{value}"


# @app.websocket('/ws')
# async def ws():
#     print('ran!')
#     while True:
#         await websocket.send("hello-")

app.run()
