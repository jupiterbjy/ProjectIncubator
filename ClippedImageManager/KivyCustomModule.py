from typing import Tuple, Union

from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.uix.boxlayout import BoxLayout


class BackgroundManagerMixin:
    """
    Will run self.callback upon resizing or repositioning events.
    """
    def update_bg(self, color: Tuple[Union[int, float], ...] = (0.1, 0.1, 0.1, 1)):
        self: BoxLayout

        self.canvas.before.clear()
        # Is .before also canvas? I don't see method clear there.

        with self.canvas.before:
            # I hope no one would ever throw wrong sized tuple.. or do they?
            Color(*color)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_rect, size=self.update_rect)

    # They do pass more parameters.
    def update_rect(self, *_):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.callback()

    def callback(self):
        pass
