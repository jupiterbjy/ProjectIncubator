"""
Based on https://stackoverflow.com/a/72422377/10909029

For further information head out to:
https://trio.readthedocs.io/en/stable/reference-lowlevel.html#instrument-api
"""

import random
from collections import defaultdict

import trio
from trio.lowlevel import add_instrument
from trio.abc import Instrument


class TaskCountInstrument(Instrument):
    """
    Task counting instrument
    """
    def __init__(self):
        self.task_counts = defaultdict(lambda: 0)

    def task_spawned(self, task):
        parent = task.parent_nursery

        self.task_counts[parent] += 1
        print(f"[N:{id(parent)}][R:{self.task_counts[parent]}] task {id(task)} spawned!")

    def task_exited(self, task):
        parent = task.parent_nursery

        if parent not in self.task_counts:
            # if it's not there probably not my fault, must be internal nurseries.
            return

        self.task_counts[parent] -= 1
        print(f"[N:{id(parent)}][R:{self.task_counts[parent]}] task {id(task)} finished!")


async def dummy_task(task_no, lifetime):
    """
    A very meaningful and serious workload

    Args:
        task_no: Task's ID
        lifetime: Lifetime of task
    """
    print(f"  Task {task_no} started")
    await trio.sleep(lifetime)
    print(f"  Task {task_no} finished")


async def main():
    # Adding instrument
    add_instrument(TaskCountInstrument())

    async with trio.open_nursery() as nursery:
        for n in range(5):
            nursery.start_soon(dummy_task, n, random.randint(1, 4))


if __name__ == '__main__':
    trio.run(main)
