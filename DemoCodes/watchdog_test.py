import time
import pathlib
import argparse
from typing import Union, Callable

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, DirCreatedEvent, FileCreatedEvent


class CustomHandler(FileSystemEventHandler):

    def __init__(self, callback: Callable):
        self.callback = callback

        # Store callback to be called on every on_created event

    def on_created(self, event: Union[DirCreatedEvent, FileCreatedEvent]):
        print(f"Event type: {event.event_type}\nAt: {event.src_path}\n")

        # check if it's File creation, not Directory creation
        if isinstance(event, FileCreatedEvent):
            file = pathlib.Path(event.src_path)

            print(f"Processing file {file.name}\n")

            # call callback
            self.callback(file)


def main():
    path: pathlib.Path = args.dir

    # list for new files
    created_files = []

    # create callback
    def callback(path_: pathlib.Path):
        print(f"Adding {path_.name} to list!")
        created_files.append(path_)

    # create instance of observer and CustomHandler
    observer = Observer()
    handler = CustomHandler(callback)

    observer.schedule(handler, path=path.absolute().as_posix(), recursive=True)
    observer.start()

    print("Observer started")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

    print(f"{len(created_files)} new files was created!", "\n".join(p.name for p in created_files), sep="\n")
    input("Press enter to exit!")


if __name__ == '__main__':

    # get script's root
    ROOT = pathlib.Path(__file__).parent

    # parse argument - if provided given directory is used, otherwise
    parser = argparse.ArgumentParser(description="Listen for file change in directory.")

    parser.add_argument("dir", metavar="DIR", type=pathlib.Path, default=ROOT, nargs="?", help="Directory to listen for. If omitted, script path is used.")

    args = parser.parse_args()

    main()
