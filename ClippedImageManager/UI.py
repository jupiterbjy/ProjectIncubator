from __future__ import annotations
from functools import cached_property
import logging
import pathlib
import math
from os import getenv
from typing import Tuple

# Kivy imports
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty

from ImageWrapper import ClippedImage, image_grouper_gen
from KivyCustomModule import BackgroundManagerMixin

logger = logging.getLogger("ClippedImageViewer")


class ImageWidget(ButtonBehavior, BoxLayout, BackgroundManagerMixin):
    source = StringProperty(None)

    def __init__(self, id_num: int, image_class: ClippedImage, **kwargs):
        super().__init__(**kwargs)

        self.ident = id_num
        self.image_class = image_class
        self.source = image_class.thumbnail_path.as_posix()

    def on_release(self):
        logger.debug(f"Release on Image No.{self.ident}")

    async def fetch_image_data(self):
        await self.image_class.get_image_data()


# If you want to load in-memory image, refer https://kivy.org/doc/stable/api-kivy.core.image.html


class MainUI(BoxLayout, BackgroundManagerMixin):
    image_grid_layout: GridLayout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.widget_references = []
        self.generate_clip_groups()
        self.update_bg()

    def generate_clip_groups(self):
        idx = -1
        for idx, clip_obj in enumerate(image_grouper_gen(self.clip_directory)):
            widget = ImageWidget(idx, clip_obj)
            self.image_grid_layout.add_widget(widget)
            self.widget_references.append(widget)

        logger.debug(f"Found {idx + 1} clips.")
        self.resize_accordingly()

    @cached_property
    def clip_directory(self) -> pathlib.Path:
        search_target = "MicrosoftWindows.Client.CBS"
        target_subdir = "TempState/ScreenClip"

        appdata_location = pathlib.Path(getenv("APPDATA")).parent.absolute()
        sub_dir = appdata_location.joinpath("Local/Packages")

        # All stuffs in sub_dir are folders. No need to filter file out.
        cbs_path = [file for file in sub_dir.glob("*/") if search_target in file.name][0]
        target_dir = cbs_path.joinpath(target_subdir)

        logger.debug(f"Found directory: {target_dir.as_posix()}")

        return target_dir

    def _get_subwidget_size_target(self) -> Tuple[int, int]:
        """
        Calculate subwidget size.
        :return: (width: int, height: int)
        """
        widget_per_row = self.image_grid_layout.cols
        spacing_x, spacing_y = self.image_grid_layout.spacing

        win_x, win_y = Window.size

        size_x = (win_x - spacing_x * 2) // widget_per_row
        size_y = (win_x - spacing_y * 2) // widget_per_row
        logger.debug((size_x, size_y))
        return size_x, size_y

    def resize_accordingly(self):
        """
        Check how many widgets are loaded and resize grid accordingly.
        """

        widget_per_row = self.image_grid_layout.cols
        spacing_x, spacing_y = self.image_grid_layout.spacing

        count = len(self.widget_references)
        rows = math.ceil(count / widget_per_row)
        cols = count if count < widget_per_row else widget_per_row

        wid_x, wid_y = self._get_subwidget_size_target()

        new_win_x = (wid_x + spacing_x) * cols - spacing_x
        new_win_y = (wid_y + spacing_y) * rows - spacing_y

        logger.debug((new_win_x, new_win_y))
        if new_win_x < 1 or new_win_y < 1:
            logger.warning("Negative value for size!")

        # self.listing_layout.size_hint_max_x = new_win_x
        self.image_grid_layout.size_hint_min = new_win_x, new_win_y
        self.image_grid_layout.size_hint_max = new_win_x, new_win_y

    def callback(self):
        logger.debug(f"in callback")
        self.resize_accordingly()
