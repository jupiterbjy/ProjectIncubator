import logging


def init_logger(logger, debug, file_output=""):
    """
    Initialize logger.
    """
    level = logging.DEBUG if debug else logging.INFO

    formatter = logging.Formatter("[%(name)s][%(levelname)s] %(asctime)s <%(funcName)s> %(message)s")

    handlers = [logging.StreamHandler()]
    if file_output:
        handlers.append(logging.FileHandler(file_output))

    logger.setLevel(level)

    for handler in handlers:
        handler.setFormatter(formatter)
        handler.setLevel(level)
        logger.addHandler(handler)

