import logging

# import pretty_errors
import trio
from MainUI import MainUIApp


# assert pretty_errors

SHOW_DEBUG_MSG = True
logger = logging.getLogger("debug")


def init_logger():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] <%(funcName)s> %(msg)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if SHOW_DEBUG_MSG:
        handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)


init_logger()


if __name__ == "__main__":

    trio.run(MainUIApp().app_func)
