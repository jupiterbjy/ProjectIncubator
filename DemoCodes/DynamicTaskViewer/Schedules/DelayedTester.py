import trio
import itertools
from collections import deque
from . import ScheduledTask


"""
Simple text cycler
"""


class TaskObject(ScheduledTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Delay Tester"
        self.delay = 0.5
        self._msgs = deque("バカにする奴は嫌いだ  "
                           "見下されるのも嫌いだ  "
                           "”アイドルなんか” という言葉を  "
                           "見てもいないくせに言うな  "
                           "頑張りを当然と言うな  "
                           "イメージとか強制するな  "
                           "”アイドルなんか” という言葉は  "
                           "この世で一番大嫌いだ")

    async def task(self):
        await trio.sleep(self.delay)
        self._msgs.rotate(-1)
        return "".join(itertools.islice(self._msgs, 10))
