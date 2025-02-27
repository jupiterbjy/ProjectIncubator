"""
Watchdog callback register-able custom handler to see what's going on in current directory.

`pip install watchdog`

![](readme_res/watchdog_file_events.png)

:Author: jupiterbjy@gmail.com
"""

import time
import pathlib
from typing import Callable, List
from collections import defaultdict

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


RECURSIVE = True
ROOT = pathlib.Path(__file__).parent.absolute()


class CustomHandler(FileSystemEventHandler):
    """Custom FileSystemEvent handler to Add custom callback on event."""

    def __init__(self):

        # callback entries for each event
        self._table: defaultdict[FileSystemEvent, List[Callable]] = defaultdict(list)
        self._default_callbacks: List[Callable] = [self._default_event_cb]

    @staticmethod
    def _default_event_cb(event: FileSystemEvent):
        """Default fallback callback when given event has no registered callback."""

        print(
            f"Discarding unregistered {type(event).event_type} event at:\n{event.src_path}"
        )

    def register(self, event: FileSystemEvent, callback: Callable):
        """Registers new callback to event"""

        self._table[event].append(callback)

    def on_any_event(self, event: FileSystemEvent) -> None:
        """Executes all the associated callbacks.
        This will react to ANY file system event,
        so rename this to one you use if you know what you are doing.

        for i.e. on_created / on_deleted / on_modified / on_moved."""

        for cb in self._table.get(event, self._default_callbacks):
            cb(event)


def keep_alive():
    """Keep alive until ctrl+c"""

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        return


def main():
    observer = Observer()
    handler = CustomHandler()
    observer.schedule(handler, str(ROOT), recursive=RECURSIVE)

    observer.start()
    keep_alive()
    observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
