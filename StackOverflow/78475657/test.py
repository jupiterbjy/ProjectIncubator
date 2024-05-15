# won't run on notebook

import multiprocessing as mp
import time
from os import getpid
from typing import Tuple

MAX_CPU = 6


def processing_func(task: Tuple[int, int]) -> int:
    """Calculate digits of input**10000000"""
    task_id, task_input = task

    print(f"[PID {getpid():6}] Processing task {task_id}")

    start = time.time()

    digits = 0
    num = (task_input ** 1000000)

    while num:
        digits += 1
        num //= 10

    duration = time.time() - start

    print(f"[PID {getpid():6}] Task {task_id} done in {duration:.2f}")
    return digits


def main():
    tasks = enumerate(range(10))

    with mp.Pool(MAX_CPU) as pool:
        print("Pool started")
        results = pool.map(processing_func, tasks)

    print("Pool done, Results:")
    for result in results:
        print(result)


if __name__ == '__main__':
    main()
