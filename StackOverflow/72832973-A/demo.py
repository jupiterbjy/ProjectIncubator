"""
Demo code for https://stackoverflow.com/q/72832973/10909029

Demonstration of worker design with multiprocessing
"""
import logging
import functools
import random
from os import getpid
from multiprocessing import Pool


logging.basicConfig(format="%(levelname)-8s %(message)s", level=logging.DEBUG)
logger = logging.getLogger()


def wrapper(func, max_retries, data):
    """
    Wrapper adding retry capabilities to workload with some fancy output.

    Args:
        func: function to execute.
        max_retries: Maximum retries until moving on.
        data: data to process.

    Returns:
        (Input data, result) Tuple.
    """
    pid = f"{getpid():<6}"
    logger.info(f"[{pid}]  Processing {data}")

    # just a line to satisfy pylint
    result = None

    # wrap in while in case for retry.
    retry_count = 0

    while retry_count <= max_retries:
        # try to process data
        try:
            result = func(data)
        except Exception as err:
            # on exception print out error, set result as err, then retry
            logger.error(
                f"[{pid}]  {err.__class__.__name__} while processing {data}, "
                f"{max_retries - retry_count} retries left. "
            )
            result = err
        else:
            break

        retry_count += 1

    # print and return result
    logger.info(f"[{pid}]  Processing {data} done")
    return data, result


class RogueAIException(Exception):
    pass


def workload(n):
    """
    Quite rebellious Fibonacci function
    """

    if random.randint(0, 1):
        raise RogueAIException("I'm sorry Dave, I'm Afraid I can't do that.")

    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b

    return b


def main():
    data = [random.randint(0, 100) for _ in range(20)]

    # fix parameters. Decorator can't be pickled, we'll have to live with this.
    wrapped_workload = functools.partial(wrapper, workload, 3)

    with Pool(processes=3) as pool:
        # apply function for each data
        results = pool.map(wrapped_workload, data)

        print("\nInput Output")
        for fed_data, result in results:
            print(f"{fed_data:<6}{result}")


if __name__ == '__main__':
    main()
