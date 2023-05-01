"""
UI part
"""

import trio
import pygame
from loguru import logger


from api import ACManager, ACState


class ACApp:

    def __init__(self, ip, id_, pw):
        super().__init__()

        self.nursery: None | trio.Nursery = None
        self.ac_manager = ACManager(ip, id_, pw)

    async def app_func(self):
        """
        App bootstrapper. Schedules kivy to run inside trio's event loop.
        """

        # await self.ac_mgr.login()

        async with trio.open_nursery() as nursery:
            self.nursery = nursery
            pass

    async def temp_up(self):
        pass

    async def temp_down(self):
        pass

    async def toggle_power(self):
        pass


if __name__ == '__main__':
    app = ACApp()
    trio.run(app.app_func)
