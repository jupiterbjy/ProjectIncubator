"""
Handles logging initialization.
"""

import logging

try:
    import coloredlogs
except ModuleNotFoundError:
    COLOR = False
else:
    COLOR = True


def init_logger(logger, debug, file_output="", disable_color=False):
    """
    Initialize logger.

    :param logger: logger created by logging module
    :param debug: if value is considered True, will set logging level to debug.
    :param file_output: path where log file is saved. leave it blank to disable file logging.
    :param disable_color: Force disable colored output.
    """

    level = logging.DEBUG if debug else logging.INFO

    fmt_str = "[%(name)s][%(asctime)s][%(levelname)s] <%(funcName)s> %(message)s"
    fmt = logging.Formatter(fmt_str)

    handlers = [logging.StreamHandler()]
    if file_output:
        handlers.append(logging.FileHandler(file_output))

    logger.setLevel(level)

    for handler in handlers:
        handler.setFormatter(fmt)
        handler.setLevel(level)
        logger.addHandler(handler)

    if COLOR and not disable_color:
        coloredlogs.install(level=level, fmt=fmt_str, logger=logger, isatty=True)
        logger.info("Colored logging enabled.")
    else:
        logger.info("Colored logging is disabled. Install 'coloredlogs' to enable it.")
