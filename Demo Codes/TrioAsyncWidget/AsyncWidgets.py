"""
Experiment of running kivy on trio event loop.

Author: jupiterbjy@gmail.com
"""

from typing import Sequence, Union

import trio

import kivy
from kivy.app import App, Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

kivy.require('2.0.0')

kv_layout = """
#:kivy 2.0.0

<AsyncWidget>:
    orientation: "vertical"
    background_color: root.color_disabled
    canvas.before:
        Color:
            rgba: root.color_disabled
        Rectangle:
            size: self.size
            pos: self.pos

    label_top: inner_label_top
    label_mid: inner_label_mid
    label_bottom: inner_label_bottom

    Label:
        id: inner_label_top
        text: root.text_top

    Label:
        id: inner_label_mid
        text: root.text_middle

    Label:
        id: inner_label_bottom
        text: root.text_bottom
"""


class AsyncWidget(ButtonBehavior, BoxLayout):
    """
    Async Widget definition
    """

    # binding for label in layout
    label_top: Label = ObjectProperty()
    label_mid: Label = ObjectProperty()
    label_bottom: Label = ObjectProperty()

    # binding for label's text
    text_top = StringProperty("")
    text_middle = StringProperty("Timer Stop")
    text_bottom = StringProperty("0")

    def __init__(self, color, nursery: trio.Nursery, **kwargs):
        self.nursery = nursery

        self.color_disabled = tuple(channel * 0.5 for channel in color)
        self.color_active = color

        # update top label's text as now we have color value
        self.text_top = str(self.color_disabled)

        self.countdown = 3
        self._rect = None

        # self.labels = (self.label_top, self.label_mid, self.label_bottom)

        super().__init__(**kwargs)

    def update_bg_color(self, color: Sequence[float]):
        """
        Updates background to given color.

        Args:
            color: Sequence / Tuple of colors in 4 channel, (r, g, b, a)

        Returns:

        """
        print(f"[{id(self)}] Updating background to {color}")

        self.canvas.before.clear()

        with self.canvas.before:
            Color(*color)
            self._rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *_):
        """
        Updates rectangle size upon resizing.
        """
        self._rect.pos = self.pos
        self._rect.size = self.size

    async def update(self):
        """
        Action taken when clicked. Will update background color and starts timer.
        """

        with self.canvas.before:
            self.update_bg_color(self.color_active)

        self.text_middle = "Timer Running"

        # copy text & text outline color
        for label in (self.label_top, self.label_mid, self.label_bottom):
            label.color = self.color_disabled
            label.outline_width = 2
            label.outline_color = (1, 1, 1, 1)

        # timer
        for i in range(self.countdown):
            self.text_bottom = str(self.countdown - i)
            await trio.sleep(1)

        # undo bg color change
        with self.canvas.before:
            self.update_bg_color(self.color_disabled)

        # restore text color & text outline color
        for label in (self.label_top, self.label_mid, self.label_bottom):
            label.color = (1, 1, 1, 1)
            label.outline_width = 0
            label.outline_color = (0, 0, 0, 0)

        # update text
        self.text_middle = 'Timer Stop'
        self.text_bottom = '0'

        # now allow click
        self.disabled = False

    def on_press(self):
        """
        Press action. Blocks further clicks by disabling itself first.
        """
        print(f"[{id(self)}] Click on {self.color_disabled}")
        self.disabled = True
        self.nursery.start_soon(self.update)


class AsyncWidgetApp(App):
    """
    Main App definition
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nursery: Union[None, trio.Nursery] = None

    def build(self):
        """
        Builds UI layout.
        """
        root = BoxLayout()

        Builder.load_string(kv_layout)

        for color in ((1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)):
            root.add_widget(AsyncWidget(color, self.nursery))
        return root

    async def app_func(self):
        """
        App bootstrapper. Schedule Kivy to run inside trio's event loop.
        """

        async with trio.open_nursery() as nursery:
            self.nursery = nursery

            async def wrapper():
                """
                Wrapper to make sure nursery is signalled about cancellation.
                """
                try:
                    await self.async_run('trio')
                finally:
                    nursery.cancel_scope.cancel()

            nursery.start_soon(wrapper)


if __name__ == '__main__':
    app = AsyncWidgetApp()
    trio.run(app.app_func)
