from collections.abc import MutableSet
from typing import Iterator
import random
import time

import trio


class SetWithCallback(MutableSet):
    """
    Class to wrap around existing set for adding callback support
    """
    def __init__(self, original_set: set, add_callback=None, remove_callback=None):
        self.inner_set = original_set

        self.add_callback = add_callback if add_callback else lambda _: None
        self.remove_callback = remove_callback if remove_callback else lambda _: None

    def add(self, value) -> None:
        self.inner_set.add(value)
        self.add_callback(value)

    def remove(self, value) -> None:
        self.inner_set.remove(value)
        self.remove_callback(value)

    def discard(self, value) -> None:
        self.inner_set.discard(value)

    def __contains__(self, x: object) -> bool:
        return x in self.inner_set

    def __len__(self) -> int:
        return len(self.inner_set)

    def __iter__(self) -> Iterator:
        return iter(self.inner_set)


async def dummy_task(task_no, lifetime):
    """
    A very meaningful and serious workload

    Args:
        task_no: Task's ID
        lifetime: Lifetime of task
    """
    print(f"  Task {task_no} started, expecting lifetime of {lifetime}s!")
    start = time.time()
    await trio.sleep(lifetime)
    print(f"  Task {task_no} finished, actual lifetime was {time.time() - start:.6}s!")


async def main():
    # Wrap original tasks set with our new class
    # noinspection PyProtectedMember
    runner = trio._core._run.GLOBAL_RUN_CONTEXT.runner
    # noinspection PyTypeChecker
    runner.tasks = SetWithCallback(runner.tasks)

    async with trio.open_nursery() as nursery:

        # callback to be called on every task add/remove.
        # checks if task belongs to nursery.
        def add_callback(task):
            # do something
            # child tasks count + 1 because given task is yet to be added.
            print(f"Task {id(task)} added, {len(nursery.child_tasks) + 1} in nursery {id(nursery)}")

        def remove_callback(task):
            # do something
            if task in nursery.child_tasks:
                # child tasks count - 1 because given task is yet to be removed from it.
                print(f"Task {id(task)} done, {len(nursery.child_tasks) - 1} in nursery {id(nursery)}")

        # replace default callback to count the task count in nursery.
        runner.tasks.add_callback = add_callback
        runner.tasks.remove_callback = remove_callback

        # spawn tasks
        for n in range(5):
            nursery.start_soon(dummy_task, n, random.randint(2, 5))
            await trio.sleep(1)


if __name__ == '__main__':
    trio.run(main)
