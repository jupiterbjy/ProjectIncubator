"""
![](readme_res/img_auto_rename.webp)

Based on watchdog_file_events, renames newly added images using current time as name.

On duplicated name, will start adding suffixes. Despite it being costly, it rarely happens anyway!

This is purely for me who tend to drag-drop images I see online to desktop, then organize later.

Since especially YouTube Community images are all named 'unnamed' which always duplicates,
requiring me to rename existing images first, I made this just for that rare use-case.

This may not work on non-Windows, due to this script depending on `pathlib.Path.rename` to
[raise](https://docs.python.org/3.12/library/pathlib.html#pathlib.Path.rename) FileExistsError
on failure.

:Author: jupiterbjy@gmail.com
"""

import time
import pathlib
import contextlib
from typing import Callable, List, Type
from collections import defaultdict

import trio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent, FileCreatedEvent


# --- CONFIG ---

# should this check files recursively?
RECURSIVE = False

# extensions to look for
EXTENSIONS = {".png", ".PNG", ".jpg", ".jpeg", ".JPG", ".webp"}

# format for names
# this will look like this if there's 3 duplicated unix time: "img_12332342342_2.png"
FORMAT = "img_{}_{}"

# Desktop path
ROOT = pathlib.Path.home() / "Desktop"


# --- Handler ---

class CustomHandler(FileSystemEventHandler):
    """Custom FileSystemEvent handler to Add custom callback on event."""

    def __init__(self):

        # callback entries for each event
        self._table: defaultdict[Type[FileSystemEvent], List[Callable]] = defaultdict(list)
        self._default_callbacks: List[Callable] = [self._default_event_cb]
        self._trio_token = trio.lowlevel.current_trio_token()

    @staticmethod
    def _default_event_cb(event: Type[FileSystemEvent]):
        """Default fallback callback when given event has no registered callback."""
        pass

    def register(self, event: Type[FileSystemEvent], callback: Callable):
        """Registers new callback to event, with trio-token wrapping"""

        def wrapped(_event: Type[FileSystemEvent]):
            self._trio_token.run_sync_soon(callback, _event)

        self._table[event].append(wrapped)

    def on_created(self, event: Type[FileSystemEvent]) -> None:
        """Executes all the associated callbacks.
        This will react to ANY file system event,
        so rename this to one you use if you know what you are doing.

        for i.e. on_created / on_deleted / on_modified / on_moved."""

        for cb in self._table.get(event.__class__, self._default_callbacks):
            cb(event)


async def rename_task_processor(recv_ch: trio.MemoryReceiveChannel):
    """Keep alive & process renaming queue"""

    task_id = 0

    async with trio.open_nursery() as nursery:

        # start task for each event

        path: pathlib.Path
        try:
            async for path in recv_ch:

                nursery.start_soon(
                    rename_safely,
                    task_id,
                    path,
                    time.time(),
                )
                task_id += 1

        except KeyboardInterrupt:
            return


async def wait_until_lock_release(path_obj: pathlib.Path):
    """Wait until lock is released, because 2008's issue NEVER solved yet.

    Args:
        path_obj: Path object waiting for release
    """

    # https://github.com/python/cpython/issues/46780
    # 2008's ISSUE is not resolved, what the heck...

    pass


async def rename_safely(task_id: int, path_obj: pathlib.Path, creation_time: int):
    """Attempt renaming with given creation time.

    If name's already taken, starts increasing suffix counter until resolved.

    This is VERY costly, but duplicate rarely happens anyway, going simple crude way.

    (Who will drop 10 images per second anyway!)
    (Even for automated job, it's THEIR role to rename files when saving!)

    Args:
        task_id: ID to identify task name.
        path_obj: pathlib.Path object that couldn't change name
        creation_time: int value of file's creation time, floored
    """

    suffix_idx = 0
    name = path_obj.with_stem(FORMAT.format(creation_time, suffix_idx))

    # start with wait, OS will not allow it anyway
    await trio.sleep(1)
    print(f"[{task_id}] Attempting to rename {path_obj}")

    while True:

        try:
            path_obj.rename(name)

        # OS's still modifying data, wait for it, should not take too long...
        except PermissionError:
            print(f"[{task_id}] Permission Error")
            await trio.sleep(0.5)

        # name duplicated, one more time!
        except FileExistsError:
            print(f"[{task_id}] Duplicated Name")
            suffix_idx += 1
            name = path_obj.with_stem(FORMAT.format(creation_time, suffix_idx))

        else:
            print(f"[{task_id}] Done!")
            return


def enqueue_callback_closure(send_ch: trio.MemorySendChannel):
    """Create callback with given send channel."""
    def enqueue_callback(event: FileCreatedEvent):
        """Enqueue event to be renamed.
        This is due to Windows Python limitation of NOT implementing
        proper os.access."""

        path = pathlib.Path(event.src_path)

        # is suffix in whitelist?
        if path.suffix not in EXTENSIONS:
            return

        try:
            send_ch.send_nowait(path)

        except trio.WouldBlock:
            # we can't do stuff here, accept our failure and move on
            # should be better than dying without realising
            print("Channel full, rejecting event for:\n" + event.src_path)

    return enqueue_callback


@contextlib.contextmanager
def observer_mgr(handler: FileSystemEventHandler, path_str: str, recursive=False):
    """Cleans up observer on exit"""

    observer = Observer()
    observer.schedule(handler, path_str, recursive=recursive)
    observer.start()
    try:
        yield observer
    finally:
        observer.stop()
        observer.join()


async def main():
    handler = CustomHandler()
    send_ch, recv_ch = trio.open_memory_channel(1024)
    async with send_ch, recv_ch:
        handler.register(FileCreatedEvent, enqueue_callback_closure(send_ch))

        with observer_mgr(handler, str(ROOT), RECURSIVE):
            await rename_task_processor(recv_ch)


if __name__ == '__main__':
    trio.run(main)
