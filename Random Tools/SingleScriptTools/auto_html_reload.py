"""
Watches for html file changes and reload pages with selenium
"""

import argparse
import pathlib
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from selenium import webdriver
from loguru import logger

# try:
#     from SingleScriptTools.LoggingConfigurator import logger
# except ModuleNotFoundError:
#     from sys import path
#     from os.path import abspath
#     path.append(abspath(""))
#
#     from SingleScriptTools.LoggingConfigurator import logger


parser = argparse.ArgumentParser(description="Auto-reload designated HTML file using selenium and watchdog.")
parser.add_argument("file_location", metavar="FILE_PATH", type=str,
                    help='path of the HTML file')

args = parser.parse_args()


def validate_path(file: str):
    path_ = pathlib.Path(file)
    try:
        assert path_.exists()
    except AssertionError:
        print("No such file. Refer `AutoHTMLReload -h` for additional information.")
        exit(1)
    else:
        return path_


class Handler(FileSystemEventHandler):
    driver = webdriver.Firefox()

    def on_modified(self, event):
        logger.debug(f"Event {event} on {event.src_path}")
        self.driver.refresh()


def html_closure():
    path_ = validate_path(args.file_location)
    event_handler = Handler()

    if path_.name.endswith((".html", ".php")):
        event_handler.driver.get(str(path_.absolute()))

    observer = Observer()
    observer.schedule(event_handler=event_handler, path=str(path_.parent.absolute()))
    return observer, event_handler.driver


if __name__ == '__main__':
    observer_instance, driver_ = html_closure()
    try:
        observer_instance.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        driver_.close()
