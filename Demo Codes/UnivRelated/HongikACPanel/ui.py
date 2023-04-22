"""
UI part
"""

import trio
from loguru import logger

from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window


from api import ACManager, ACState


# UI ----
kivy_ui = """
#:kivy 2.1.0

<ACWidget>:
    orientation: "vertical"
    canvas.before:
        Color:
            rgba: 0, 0, 0, 0
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        id: box_temp_display
        orientation: "horizontal"

        Label:
            id: label_temp_cur
            text: root.text_temp

        Label:
            id: label_temp_tgt
            text: root.text_current

    GridLayout:
        id: grid_main
        spacing: 15, 15
        cols: 3

        Button:
            id: btn_t_down
            text: "Temp down"

        Button:
            id: btn_t_up
            text: "Temp up"

        Button:
            id: btn_power
            text: "Power"
"""


class ACWidget(BoxLayout):
    # TODO: use 7-seg display
    text_temp = StringProperty("--")
    text_current = StringProperty("--")


class ACApp(App):

    def __init__(self):
        super().__init__()

        self.nursery: None | trio.Nursery = None
        # self.ac_mgr = ACManager()

    def build(self):
        """
        Builds UI
        """
        Builder.load_string(kivy_ui)
        return ACWidget()

    async def app_func(self):
        """
        App bootstrapper. Schedules kivy to run inside trio's event loop.
        """

        # await self.ac_mgr.login()

        async with trio.open_nursery() as nursery:
            self.nursery = nursery

            async def wrapper():
                logger.info("Started")
                try:
                    await self.async_run("trio")
                finally:
                    nursery.cancel_scope.cancel()

            nursery.start_soon(wrapper)

    async def temp_up(self):
        pass

    async def temp_down(self):
        pass

    async def toggle_power(self):
        pass


if __name__ == '__main__':
    Window.size = (250, 350)
    app = ACApp()
    trio.run(app.app_func)
