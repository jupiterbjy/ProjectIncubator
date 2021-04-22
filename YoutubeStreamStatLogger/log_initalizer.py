import logging


def init_logger(logger, debug, file_output=""):
    """
    Initialize logger.
    """
    level = logging.DEBUG if debug else logging.DEBUG

    formatter = logging.Formatter("[%(name)s][%(levelname)s] %(asctime)s <%(funcName)s> %(message)s")

    handlers = [logging.StreamHandler()]
    if file_output:
        handlers.append(logging.FileHandler(file_output))

    for handler in handlers:
        handler.setFormatter(formatter)
        handler.setLevel(level)
        logger.addHandler(handler)

    logger.setLevel(level)
