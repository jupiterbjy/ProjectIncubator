from __future__ import annotations
import logging

import trio
from kivy.app import App
from kivy.lang.builder import Builder

from UI import MainUI


logger = logging.getLogger("ClippedImageViewer")
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("[%(levelname)s][%(funcName)s] %(asctime)s - %(msg)s"))
logger.addHandler(_handler)
logger.setLevel("DEBUG")


class MainApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        logger.debug("Loading UI")
        Builder.load_file("UI.kv")
        return MainUI()

    async def _wrapper(self, nursery: trio.Nursery):
        logger.debug("App start")

        await self.async_run(async_lib="trio")
        nursery.cancel_scope.cancel()

        logger.debug("App stop")

    async def trio_driver(self):
        """
        Main driver in trio event loop.
        """

        async with trio.open_nursery() as nursery:
            nursery.start_soon(self._wrapper, nursery)


if __name__ == '__main__':
    trio.run(MainApp().trio_driver)
