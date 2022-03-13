"""
Demo codes for https://stackoverflow.com/q/71458088/10909029

Waiting for child process to complete
"""

import os
import math
import queue
import multiprocessing as mp
from concurrent import futures


def child_process(task_queue: mp.Queue):
    pid = os.getpid()

    print(f"[{pid}] Started!")
    processed_count = 0

    while True:
        try:
            item = task_queue.get_nowait()
        except queue.Empty:
            # task done
            break

        # else continue on
        # some workload
        try:
            print(f"[{pid}] {item}! = {math.factorial(item)}")

        finally:
            # tell queue we processed the item.
            task_queue.task_done()
            processed_count += 1

    print(f"[{pid}] Task done!")


def main():
    # just merely rapping codes in function namespace makes codes tiny bit faster

    mp_manager = mp.Manager()
    task_queue = mp_manager.Queue()

    # populate queue
    for n in range(100):
        task_queue.put_nowait(n)

    # start pool
    with futures.ProcessPoolExecutor() as executor:
        future_list = [executor.submit(child_process, task_queue) for _ in range(5)]

        # can use executor.shutdown(wait=True) instead
        # not required since all executor wait for all process to stop when exiting `with` block.
        # hence, also no need to manually call executor.shutdown().
        futures.wait(future_list)


if __name__ == '__main__':
    main()
