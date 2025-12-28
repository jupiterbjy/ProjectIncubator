"""
Watchdog callback register-able custom handler to see what's going on in current directory.

`pip install watchdog`

```python
import pathlib

from watchdog_file_events_m import start_watchdog, FileSystemEvent, FileCreatedEvent

def _cb(event: FileSystemEvent):
    print(f"Callback triggered for {event.__class__.__name__} at {event.src_path}")

with start_watchdog(str(pathlib.Path(__file__).parent.absolute()), True) as handler:

    handler.register(FileCreatedEvent, _cb)

    # handler.register_on_file_creation(_cb)
    handler.register_on_file_deletion(_cb)
    handler.register_on_file_modification(_cb)
    handler.register_on_file_move(_cb)

    # handler.register_global(_cb)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        return
```

![](readme_res/watchdog_file_events.png)

:Author: jupiterbjy@gmail.com
"""

import time
import pathlib
from contextlib import contextmanager
from typing import Callable, List, Iterator
from collections import defaultdict

from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEventHandler,
    FileSystemEvent,

    FileCreatedEvent,
    FileDeletedEvent,
    FileMovedEvent,
    FileModifiedEvent,

    DirCreatedEvent,
    DirDeletedEvent,
    DirMovedEvent,
    DirModifiedEvent,
)


class CustomHandler(FileSystemEventHandler):
    """Custom FileSystemEvent handler to Add custom callback on event."""

    def __init__(self):

        # callback entries for each event
        self._table: defaultdict[str, List[Callable]] = defaultdict(list)
        self._global_cb: List[Callable] = []

    @staticmethod
    def _default_event_cb(event: FileSystemEvent):
        """Default fallback callback when given event has no registered callback."""

        print(
            f"# Discarding unregistered {event.__class__.__name__} at {event.src_path}"
        )

    def register_global(self, callback: Callable):
        """Registers a callback to be called on ANY event."""
        self._global_cb.append(callback)

    def register(self, event: type[FileSystemEvent], callback: Callable):
        """Registers new callback to event.

        Args:
            event: `watchdog.FileSystemEvent` derived class
            callback: callable to register for the class
        """

        self._table[event.__name__].append(callback)

    def on_any_event(self, event: FileSystemEvent) -> None:
        """Executes all the associated callbacks.
        This will react to ANY file system event,
        so rename this to one you use if you know what you are doing.

        For e.g. on_created / on_deleted / on_modified / on_moved."""

        for cb in self._table.get(
            event.__class__.__name__,
            self._global_cb if self._global_cb else [self._default_event_cb]
        ):
            cb(event)

    def register_on_file_creation(self, callback: Callable[[FileCreatedEvent], None]):
        """Syntax sugar for register"""
        self.register(FileCreatedEvent, callback)

    def register_on_file_deletion(self, callback: Callable[[FileDeletedEvent], None]):
        """Syntax sugar for register"""
        self.register(FileDeletedEvent, callback)

    def register_on_file_modification(self, callback: Callable[[FileModifiedEvent], None]):
        """Syntax sugar for register"""
        self.register(FileModifiedEvent, callback)

    def register_on_file_move(self, callback: Callable[[FileMovedEvent], None]):
        """Syntax sugar for register"""
        self.register(FileMovedEvent, callback)

    def register_on_directory_creation(self, callback: Callable[[DirCreatedEvent], None]):
        """Syntax sugar for register"""
        self.register(DirCreatedEvent, callback)

    def register_on_directory_deletion(self, callback: Callable[[DirDeletedEvent], None]):
        """Syntax sugar for register"""
        self.register(DirDeletedEvent, callback)

    def register_on_directory_modification(self, callback: Callable[[DirModifiedEvent], None]):
        """Syntax sugar for register"""
        self.register(DirModifiedEvent, callback)

    def register_on_directory_move(self, callback: Callable[[DirMovedEvent], None]):
        """Syntax sugar for register"""
        self.register(DirMovedEvent, callback)


@contextmanager
def start_watchdog(path: str, recursive: bool) -> Iterator[CustomHandler]:
    """Wraps the start & stop of watchdog observer and yields the handler."""

    observer = Observer()
    handler = CustomHandler()
    observer.schedule(handler, path, recursive=recursive)
    observer.start()

    print(f"Watchdog started for: {path}")

    yield handler

    print(f"Watchdog stopping for: {path}")

    observer.stop()
    observer.join()


def _test():

    def _cb(event: FileSystemEvent):
        print(f"Callback triggered for {event.__class__.__name__} at {event.src_path}")

    with start_watchdog(str(pathlib.Path(__file__).parent.absolute()), True) as handler:

        handler.register(FileCreatedEvent, _cb)

        # handler.register_on_file_creation(_cb)
        handler.register_on_file_deletion(_cb)
        handler.register_on_file_modification(_cb)
        handler.register_on_file_move(_cb)

        # handler.register_global(_cb)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            return


if __name__ == "__main__":
    _test()
