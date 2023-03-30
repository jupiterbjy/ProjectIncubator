"""
asynchronous isort demo
"""

import pathlib
import asyncio
import itertools
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from timeit import timeit

import isort
from isort import format


# target dir with modules
FILE = pathlib.Path("./import_messes")


# Monkey-patching isort.format.create_terminal_printer to suppress Terminal bombarding.
# Totally not required nor recommended for normal use
class SuppressionPrinter:
    def __init__(self, *_, **__):
        pass

    def success(self, *_):
        pass

    def error(self, *_):
        pass

    def diff_line(self, *_):
        pass


isort.format.BasicPrinter = SuppressionPrinter


# -----------------------------
# Test functions

def filelist_gen():
    """Chain directory list multiple times to get meaningful difference"""
    yield from itertools.chain.from_iterable([FILE.iterdir() for _ in range(1000)])


def isort_synchronous(path_iter):
    """Synchronous usual isort use-case"""

    # return list of results
    return [isort.check_file(file) for file in path_iter]


def isort_thread(path_iter):
    """Threading isort"""

    # prepare thread pool
    with ThreadPoolExecutor(max_workers=2) as executor:
        # start loading
        futures = [executor.submit(isort.check_file, file) for file in path_iter]

        # return list of results
        return [fut.result() for fut in futures]


def isort_multiprocess(path_iter):
    """Multiprocessing isort"""

    # prepare process pool
    with ProcessPoolExecutor(max_workers=2) as executor:
        # start loading
        futures = [executor.submit(isort.check_file, file) for file in path_iter]

        # return list of results
        return [fut.result() for fut in futures]


async def isort_asynchronous(path_iter):
    """Asyncio isort using to_thread"""

    # create coroutines that delegate sync funcs to threads
    coroutines = [asyncio.to_thread(isort.check_file, file) for file in path_iter]

    # run coroutines and wait for results
    return await asyncio.gather(*coroutines)


if __name__ == '__main__':
    # run once, no repetition
    n = 1

    # synchronous runtime
    print(f"Sync func.: {timeit(lambda: isort_synchronous(filelist_gen()), number=n):.4f}")

    # threading demo
    print(f"Threading : {timeit(lambda: isort_thread(filelist_gen()), number=n):.4f}")

    # multiprocessing demo
    print(f"Multiproc.: {timeit(lambda: isort_multiprocess(filelist_gen()), number=n):.4f}")

    # asyncio to_thread demo
    print(f"to_thread : {timeit(lambda: asyncio.run(isort_asynchronous(filelist_gen())), number=n):.4f}")

