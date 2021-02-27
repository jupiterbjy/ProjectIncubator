import argparse
import pathlib
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from selenium import webdriver

try:
    from TinyTools.LoggingConfigurator import logger
except ModuleNotFoundError:
    from sys import path
    from os.path import abspath
    path.append(abspath(""))

    from TinyTools.LoggingConfigurator import logger


parser = argparse.ArgumentParser(description="Auto-reload designated HTML file using selenium and watchdog.")
parser.add_argument("file_location", metavar="FILE_PATH", type=str,
                    help='path of the HTML file')

args = parser.parse_args()


def validate_path(file: str):
    path = pathlib.Path(file)
    try:
        assert path.exists()
    except AssertionError:
        print("No such file. Refer `AutoHTMLReload -h` for additional information.")
        exit(1)
    else:
        return path


class Handler(FileSystemEventHandler):
    driver = webdriver.Firefox()

    def on_modified(self, event):
        logger.debug(f"Event {event} on {event.src_path}")

        if isinstance(event, FileModifiedEvent) and str(event.src_path) == self.driver.current_url:
            self.driver.refresh()


def html_closure():
    path = validate_path(args.file_location)
    event_handler = Handler()
    event_handler.driver.get(str(path.absolute()))

    observer = Observer()
    observer.schedule(event_handler=event_handler, path=str(path.parent.absolute()))
    return observer, event_handler.driver


if __name__ == '__main__':
    observer_instance, driver_ = html_closure()
    try:
        observer_instance.start()
        while True:
            time.sleep(1)
    finally:
        driver_.close()
