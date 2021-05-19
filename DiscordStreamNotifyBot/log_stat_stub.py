import logging
import datetime

import trio

from log_initalizer import init_logger


logger = logging.getLogger("wait")
init_logger(logger, True)


async def wait_for_stream(client_, video_id):
    """
    Literally does what it's named for. await until designated stream time.

    Raises RuntimeError when stream is either seems to be canceled.
    """

    # check if actually it is active/upcoming stream

    # Dispatch cases
    status = client_.get_stream_status(video_id)

    if status == "live":
        logger.info(
            "API returned `%s`, stream already active.", status
        )
        return

    if status == "none":
        logger.critical(
            "API returned `%s`, is this a livestream?", status
        )
        raise RuntimeError("No upcoming/active stream.")

    # upcoming state, fetch scheduled start time
    start_time = client_.get_start_time(video_id)

    # get timedelta
    current = datetime.datetime.now(datetime.timezone.utc)

    # workaround for negative timedelta case. Checks if start time is future
    if start_time > current:

        delta = (start_time - current).seconds
        logger.info(
            "Will wait for %s seconds until stream starts. Press Ctrl+C to terminate.",
            delta,
        )

        # Sleep until due time
        await trio.sleep(delta)
        logger.info("Awake, waiting for live state.")

    # Check if stream is actually started
    while status := client_.get_stream_status(video_id):
        logger.debug("Status check: %s", status)

        if status == "none":
            logger.critical(
                "API returned `%s`, is stream canceled?", status
            )
            raise RuntimeError("No upcoming/active stream.")

        if status == "live":
            return

        await trio.sleep(5)
