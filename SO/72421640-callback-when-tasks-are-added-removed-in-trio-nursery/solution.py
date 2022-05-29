"""
Based on https://stackoverflow.com/a/72422377/10909029
"""

import time
import random
from collections import defaultdict

import trio
from trio.lowlevel import add_instrument
from trio.abc import Instrument

task_counts = defaultdict(lambda: 0)


class TaskCountInstrument(Instrument):
    def task_spawned(self, task):
        task_counts[task.parent_nursery] += 1
        print(f"[N:{id(task.parent_nursery)}][R:{task_counts[task.parent_nursery]}] task {id(task)} spawned!")

    def task_exited(self, task):
        if task.parent_nursery not in task_counts:
            # if it's not there probably not my fault, must be internal nurseries.
            return

        task_counts[task.parent_nursery] -= 1
        print(f"[N:{id(task.parent_nursery)}][R:{task_counts[task.parent_nursery]}] task {id(task)} finished!")


async def dummy_task(task_no, lifetime):
    """
    A very meaningful and serious workload

    Args:
        task_no: Task's ID
        lifetime: Lifetime of task
    """
    print(f"  Task {task_no} started")
    start = time.time()
    await trio.sleep(lifetime)
    print(f"  Task {task_no} finished")


async def main():
    add_instrument(TaskCountInstrument())
    async with trio.open_nursery() as nursery:
        for n in range(5):
            nursery.start_soon(dummy_task, n, random.randint(1, 4))


if __name__ == '__main__':
    trio.run(main)
