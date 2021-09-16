"""
Used for recording start, end time of work session.

This is sort of wheel re-inventing of simple timer, but I couldn't find way to record time on this thing.
"""

import json
import pathlib
import winsound
from datetime import datetime, timedelta
from textwrap import dedent
from typing import List, Union

import pytz
from pynput import keyboard
from loguru import logger


TIMEZONE_SOURCE = "Asia/Seoul"
TIMEZONE_TARGET = "America/Los_Angeles"

TOGGLE_COMBINATION = "<f10>+<f12>"
EXIT_COMBINATION = "<f9>+<f12>"

FORMAT = "%Y-%m-%d %a %H:%M"


TZ_SRC_INIT = pytz.timezone(TIMEZONE_SOURCE)
TZ_TGT_INIT = pytz.timezone(TIMEZONE_TARGET)

# Generate paths
ROOT = pathlib.Path(__file__).parent
STORAGE = ROOT.joinpath("Sessions")
STORAGE.mkdir(exist_ok=True)

LOG_PATH = ROOT.joinpath("logs")
LOG_PATH.mkdir(exist_ok=True)

# Config resource paths

logger.add(
    LOG_PATH.joinpath("/work_{time}.log").as_posix(),
    rotation="5 MB",
    retention="7 days",
    compression="zip",
)


def fmt(dt: datetime):
    return dt.strftime(FORMAT)


class Session:
    def __init__(self):

        self.start = datetime.now(TZ_SRC_INIT)
        self.end: Union[datetime, None] = None

        self.index = int(self.start.timestamp())

        self.alt_tz_start = self.start.astimezone(TZ_TGT_INIT)
        self.alt_tz_end = None

        self.tz_local = TIMEZONE_SOURCE
        self.tz_remote = TIMEZONE_TARGET

        self._calculated: Union[None, timedelta] = None

    def stop(self):
        self.end = datetime.now(TZ_SRC_INIT)
        self.alt_tz_end = self.end.astimezone(TZ_TGT_INIT)

        self._calculated = self.end - self.start

    def __str__(self):
        if not self._calculated:
            raise RuntimeError("Session is still running.")

        string = f"""
        <Session {self.index} - {self._calculated} long>
        > {fmt(self.start)} ({TIMEZONE_SOURCE})
        > {fmt(self.alt_tz_start)} ({TIMEZONE_TARGET})
        |
        < {fmt(self.end)} ({TIMEZONE_SOURCE})
        < {fmt(self.alt_tz_end)} ({TIMEZONE_TARGET})
        """

        return dedent(string)

    @property
    def length(self) -> timedelta:
        if not self._calculated:
            self._calculated = self.end - self.start

        return self._calculated

    def to_json(self):
        # dict_ = self.__dict__
        dict_ = {
            "index": self.index,
            "duration": str(self.length),
            "start": self.start.timestamp(),
            "end": self.end.timestamp(),
            "alt_tz_start": self.alt_tz_start.timestamp(),
            "alt_tz_end": self.alt_tz_end.timestamp(),
            "tz_local": self.tz_local,
            "tz_remote": self.tz_remote,
        }

        return dict_

    @classmethod
    def from_json(cls, json_dict):
        # dict_ = self.__dict__
        tz_local = pytz.timezone(json_dict["tz_local"])
        tz_remote = pytz.timezone(json_dict["tz_remote"])

        dict_ = {
            "start": datetime.fromtimestamp(json_dict["start"], tz_local).astimezone(
                pytz.timezone(TIMEZONE_SOURCE)
            ),
            "end": datetime.fromtimestamp(json_dict["end"], tz_local).astimezone(
                pytz.timezone(TIMEZONE_SOURCE)
            ),
            "alt_tz_start": datetime.fromtimestamp(
                json_dict["alt_tz_start"], tz_remote
            ).astimezone(pytz.timezone(TIMEZONE_TARGET)),
            "alt_tz_end": datetime.fromtimestamp(
                json_dict["alt_tz_end"], tz_remote
            ).astimezone(pytz.timezone(TIMEZONE_TARGET)),
        }

        instance = cls()
        instance.__dict__.update(json_dict)
        instance.__dict__.update(dict_)

        return instance


def ring_multiple(count=1):
    for _ in range(count):
        winsound.Beep(1000, 100)


class Timer:
    def __init__(self):
        self.working = False
        self.sessions: List[Session] = []
        self.current_session: Union[Session, None] = None

        logger.info("Initialized")

    def prompt_message(self):
        aggregated_time = sum(
            (session.length for session in self.sessions), start=timedelta()
        )

        print(
            f"Aggregated: {aggregated_time}",
            f"Sessions count: {len(self.sessions)}",
            f"Session Running: Session {self.current_session.index}"
            f" started at {self.current_session.start.astimezone(TZ_SRC_INIT)}"
            if self.current_session
            else "",
            sep="\n",
        )

    def stop(self):
        logger.debug("Called")
        try:
            self.current_session.stop()
        except AttributeError:
            logger.warning("No sessions to stop!")
        else:
            self.sessions.append(self.current_session)
            self.current_session = None
            self.save_session()

        ring_multiple(1)

    def start(self):
        logger.debug("Called")
        if self.current_session:
            logger.warning("Session already running!")
            return

        self.current_session = Session()
        ring_multiple(2)

    def toggle(self):
        logger.debug("Called")
        if self.current_session:
            self.stop()
        else:
            self.start()

    def exit(self):
        logger.debug("Called")
        if self.current_session:
            self.stop()

        self.save_session()
        ring_multiple(3)
        exit(0)

    @property
    def total_length(self):
        return sum((session.length for session in self.sessions), start=timedelta())

    def save_session(self):
        logger.debug("Called")
        file_name = self.sessions[0].start.strftime("%Y-%m-%d") + ".json"

        path_ = STORAGE.joinpath(file_name)

        # if exists
        if path_.exists():

            # read first
            existing = json.loads(path_.read_text("utf8"))

            # check if first index is same, if same then just overwrite it.
            try:
                assert existing["entries"][0]["index"] == self.sessions[0].index

            # empty entry, skip
            except IndexError:
                pass

            # probably previous entry before this process started. load up
            except AssertionError:
                logger.info("Previous Session found. Loading session")
                self.sessions = [
                    Session.from_json(entry) for entry in existing["entries"]
                ] + self.sessions

        current = [session.to_json() for session in self.sessions]

        output_dict = {"Sessions": len(current), "length": str(self.total_length), "entries": current}

        path_.write_text(json.dumps(output_dict, indent=2), "utf8")
        logger.info("Saved sessions at {}", path_)


# class CustomTray:
#     def __init__(self):
#
#         self.active_img = Image.open(IMG_PATH.joinpath("active.png"))
#         self.inactive_img = Image.open(IMG_PATH.joinpath("inactive.png"))
#         self.error_img = Image.open(IMG_PATH.joinpath("error.png"))
#
#         self.timer = Timer()
#
#         toggle_menu = pystray.Menu(
#             pystray.MenuItem("Toggle", self.timer.toggle),
#             pystray.MenuItem("Exit", self.timer.exit)
#        )
#
#         self.tray = pystray.Icon("Timer", self.inactive_img, toggle_menu)
#
#     def toggle(self):
#         pass


def main():
    timer = Timer()

    # toggle_hotkey = keyboard.HotKey(keyboard.HotKey.parse(TOGGLE_COMBINATION), timer.toggle)
    # exit_hotkey = keyboard.HotKey(keyboard.HotKey.parse(EXIT_COMBINATION), timer.exit)

    with keyboard.GlobalHotKeys(
        {TOGGLE_COMBINATION: timer.toggle, EXIT_COMBINATION: timer.exit}
    ) as hotkey:
        hotkey.join()


if __name__ == "__main__":
    main()
