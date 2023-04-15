from __future__ import annotations
from typing import Callable
import logging


logger = logging.getLogger("debug")


class StopTask(Exception):
    """
    Exception to escape from continuous execution
    """


class ScheduledTask:
    """
    Interface for task units. Inherit this to each py scripts for execution.

    # Below description is plan, not implemented

    self.parameters dict only receives string inputs,
    it's up to user to convert param as they desire.
    """

    def __init__(self, task_start_method: Callable):
        """
        Script will check output periodically.
        """
        self.run = False
        self.name = ""
        self._parameters = dict()
        self._task_starter = task_start_method

    def update_parameter(self, **kwargs):
        """
        No need to implement fail-safe, only keys in self.parameters will be shown on UI for editing.
        Will clear storage on value changes.
        """
        self._parameters.update(kwargs)

    async def task_wrap(self):
        """
        Wraps task to check run conditions.
        """

        if self.run:
            return await self.task()

        raise StopTask()

    async def task(self):
        """
        Fill out your own actions here. Return value will be displayed on widget.
        """

        return None

    def stop_task(self):
        """
        Interface to raise StopTask.
        """
        self.run = False

        raise StopTask()

    def start_task(self):
        """
        Interface to schedule execution of this task.
        Will be overridden by widget.
        """
        self.run = True

        self._task_starter()

    def on_click(self):
        """
        Action to do when widget is pressed. Default behavior is pause-resuming task.
        """
        self.run = not self.run

        # in reverse!
        if self.run:
            self.start_task()
