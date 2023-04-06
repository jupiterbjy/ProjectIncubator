import time
import pathlib
from typing import Union, Callable

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, DirCreatedEvent, FileCreatedEvent

from loguru import logger


class NewFileHandler(FileSystemEventHandler):
    """Custom handler for Watchdog"""

    def __init__(self, watch_dir_create=False, callback: Callable = None):

        # save callback reference, if not provided, print() will be used instead.
        self.callback = callback if callback else print
        self.watch_dir_create = watch_dir_create

    # callback for File/Directory created event, called by Observer.
    def on_created(self, event: Union[DirCreatedEvent, FileCreatedEvent]):

        # check if it's File creation, not Directory creation
        if isinstance(event, FileCreatedEvent):
            if event.src_path[-3:] == ".h5":

                logger.debug("New h5 file at \"{}\"", event.src_path)

                # run callback with path string
                self.callback(event.src_path)

        elif self.watch_dir_create:
            logger.debug("New Directory at \"{}\"", event.src_path)

            self.callback(event.src_path)


class ObserverWrapper:
    """Encapsulated Observer boilerplate"""

    def __init__(self, path: str, recursive=True, watch_dir_create=False):
        self.path = path
        self.recursive = recursive

        self.observer = Observer()
        self.handler = NewFileHandler(watch_dir_create, self.callback)

        self.observer.schedule(self.handler, path=path, recursive=recursive)

    def start(self, blocking=True):
        """
        Starts observing for filesystem events.

        :param blocking: If true, blocks main thread until keyboard interrupt.
        """

        self.observer.start()
        logger.debug("Observer {} started", id(self))
        logger.debug("Path: \"{}\", Recursive: {}", self.path, self.recursive)

        if blocking:
            logger.debug("Blocking main thread. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.warning("Received KeyboardInterrupt")
                self.stop()

    def stop(self):
        """
        Stops the observer. When running self.start(blocking=True) then you don't need to call this.
        """

        self.observer.stop()
        self.observer.join()

    def callback(self, new_file_path: str):
        """
        Called every new file creation events.

        :param new_file_path: Newly created file's absolute path
        """

        # Do something here!
        print(f"Callback running for {new_file_path}!")


def main():
    # get current path as absolute, linux-style path.
    working_path = pathlib.Path(".").absolute().as_posix()

    wrapper = ObserverWrapper(working_path)
    wrapper.start()


if __name__ == '__main__':
    main()
