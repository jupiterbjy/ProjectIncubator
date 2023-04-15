import trio
import math
import logging
from typing import List, Callable

# Kivy imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty, StringProperty
from kivy.core.window import Window

from KivyCustomModule import BackgroundManagerMixin
from InnerWidget import InnerWidget
import Loader


logger = logging.getLogger("debug")


class MainUI(BoxLayout, BackgroundManagerMixin):
    start_stop_wid = ObjectProperty()
    listing_layout: GridLayout = ObjectProperty()
    current_text = StringProperty()

    def __init__(self, send_channel, fn_accept_tasks, fn_stop_task, **kwargs):
        self.bg_color = (0.3, 0.3, 0.3, 1)

        self.orientation = "vertical"

        self.send_ch = send_channel
        self.loaded_widget_reference: List[InnerWidget] = []

        self.task_start: Callable = fn_accept_tasks
        self.task_stop: Callable = fn_stop_task

        super().__init__(**kwargs)

        self.update_bg(self.bg_color)

    def on_toggle_release(self):
        logger.debug("Press Event on Start")
        if self.start_stop_wid.state == "down":
            self.start_action()
        else:
            self.stop_action()

    def on_reload_release(self):
        """
        Clear and re-check python scripts in Schedules module and load them.
        :return:
        """
        self.stop_action()

        logger.debug("Press Event on Reload")

        # Drop widget first then drop reference.
        self.listing_layout.clear_widgets()
        self.loaded_widget_reference.clear()

        for task_class in Loader.fetch_scripts():
            self.loaded_widget_reference.append(InnerWidget(task_class, self.send_ch))

            self.listing_layout.add_widget(self.loaded_widget_reference[-1])

            logger.info(f"Added: {self.loaded_widget_reference[-1]}")

        self.resize_accordingly()

    def start_action(self):
        """
        Start scheduling execution of Task objects.
        """
        self.start_stop_wid.text = "stop"
        self.task_start()
        for widget in self.loaded_widget_reference:
            logger.debug(f"Starting task {widget}")
            widget.submit_task()

    def stop_action(self):
        """
        Cancel the trio.CancelScope, stopping re-scheduling and execution of Task objects.
        """
        self.start_stop_wid.text = "start"
        self.task_stop()

    def callback(self):
        logger.debug(f"in callback")
        self.resize_accordingly()

    def _get_subwidget_size_target(self) -> (int, int):
        """
        Calculate subwidget size.
        :return: (int, int)
        """
        widget_per_row = self.listing_layout.cols
        spacing_x, spacing_y = self.listing_layout.spacing

        win_x, win_y = Window.size

        size_x = (win_x - spacing_x * 2) // widget_per_row
        size_y = (win_x - spacing_y * 2) // widget_per_row
        logger.debug((size_x, size_y))
        return size_x, size_y

    def resize_accordingly(self):
        """
        Check how many widgets are loaded and resize Grid Size accordingly.
        """
        widget_per_row = self.listing_layout.cols
        spacing_x, spacing_y = self.listing_layout.spacing

        count = len(self.loaded_widget_reference)
        rows = math.ceil(count / widget_per_row)
        cols = count if count < widget_per_row else widget_per_row

        wid_x, wid_y = self._get_subwidget_size_target()

        new_win_x = (wid_x + spacing_x) * cols - spacing_x
        new_win_y = (wid_y + spacing_y) * rows - spacing_y

        logger.debug((new_win_x, new_win_y))
        if new_win_x < 1 or new_win_y < 1:
            logger.warning("Negative value for size!")

        # self.listing_layout.size_hint_max_x = new_win_x
        self.listing_layout.size_hint_min = new_win_x, new_win_y
        self.listing_layout.size_hint_max = new_win_x, new_win_y


class MainUIApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.send_ch, self.recv_ch = trio.open_memory_channel(500)

        self.cancel_scope: trio.CancelScope = trio.CancelScope()  # Pointless init for hinting.
        self.event: trio.Event = trio.Event()

    def build(self):
        return MainUI(self.send_ch, self.start_tasks, self.cancel_tasks)

    def start_tasks(self):
        self.event.set()

    def cancel_tasks(self):
        logger.debug("Canceling Scope!")
        self.cancel_scope.cancel()

    async def app_func(self):
        """Trio wrapper async function."""

        async with trio.open_nursery() as nursery:

            async def run_wrapper():
                # Set trio
                await self.async_run(async_lib="trio")
                logger.info("App Stop")
                nursery.cancel_scope.cancel()

            nursery.start_soon(self.wait_for_tasks)
            logger.info("Starting UI")
            nursery.start_soon(run_wrapper)

    async def wait_for_tasks(self):
        async def scheduler():
            logger.debug("Now accepting tasks.")

            async with trio.open_nursery() as nursery_sub:
                async for task_coroutine in self.recv_ch:

                    nursery_sub.start_soon(task_coroutine)
                    # logger.debug(f"Scheduled execution of task <{task_coroutine}>")

        while True:
            with trio.CancelScope() as cancel_scope:
                self.cancel_scope = cancel_scope
                await scheduler()

            try:
                while leftover := self.recv_ch.receive_nowait():
                    logger.debug(f"Dumping {leftover}")
            except trio.WouldBlock:
                pass

            logger.debug(f"Cancel scope closed, waiting for start event.")
            await self.event.wait()
            self.event = trio.Event()


if __name__ == "__main__":
    trio.run(MainUIApp().app_func)
