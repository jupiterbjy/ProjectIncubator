import time
import trio
from . import ScheduledTask

"""
Minimal task for minimal testing purpose.
"""


class TaskObject(ScheduledTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "time.time()"

    async def task(self):
        await trio.sleep(0.1)
        return f"{time.time():.6f}"
