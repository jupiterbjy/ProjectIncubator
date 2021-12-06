"""
Used for recording start, end time of work session.

This is sort of wheel re-inventing of simple timer, but I couldn't find way to record time on this thing.
"""

import time
import json
import pathlib
from datetime import datetime, timedelta
from textwrap import dedent
from typing import List, Union, Iterable, Dict

import pytz
import pystray
from PIL import Image
from pynput import keyboard
from loguru import logger


# key def
TOGGLE_COMBO = "<scroll_lock>+<pause>"
CHECK_COMBO = "<scroll_lock>+<num_lock>"

FORMAT = "%Y-%m-%d %a %H:%M"

# TZ def
TIMEZONE_SOURCE = "Asia/Seoul"
TIMEZONE_TARGET = "America/Los_Angeles"

TZ_SRC_INIT = pytz.timezone(TIMEZONE_SOURCE)
TZ_TGT_INIT = pytz.timezone(TIMEZONE_TARGET)


# Generate paths
ROOT = pathlib.Path(__file__).parent
STORAGE = ROOT.joinpath("Sessions")
STORAGE.mkdir(exist_ok=True)
IMG_PATH = ROOT.joinpath("icon")

LOG_PATH = ROOT.joinpath("logs")
LOG_PATH.mkdir(exist_ok=True)


# Config resource paths

# logger.add(
#     LOG_PATH.joinpath("/work_{time}.log").as_posix(),
#     rotation="5 MB",
#     retention="7 days",
#     compression="zip",
# )


def fmt(dt: datetime):
    return dt.strftime(FORMAT)


def str_to_timedelta(string: str):
    # Ref: https://stackoverflow.com/a/12352624/10909029
    if "day" in string:
        day, string = string.split("day")
        delta = timedelta(days=int(day))
    else:
        delta = timedelta()

    temp = datetime.strptime(string, "%H:%M:%S.%f")
    return delta + timedelta(
        hours=temp.hour,
        minutes=temp.minute,
        seconds=temp.second,
        microseconds=temp.microsecond,
    )


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
            try:
                self._calculated = self.end - self.start
            except TypeError:
                # self.end is None, so still running!
                return datetime.now(TZ_SRC_INIT) - self.start

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


def session_sum(iterable: Iterable) -> timedelta:
    return sum((session.length for session in iterable), start=timedelta())


# def ring_multiple(count=1, freq=1000, duration=100):
#     for _ in range(count):
#         winsound.Beep(freq, duration)


class CustomTray(pystray.Icon):
    def __init__(self):
        super(CustomTray, self).__init__("WorkTimeRecord")

        self.active_img = Image.open(IMG_PATH.joinpath("active.png"))
        self.inactive_img = Image.open(IMG_PATH.joinpath("inactive.png"))

        #  toggle_menu = pystray.Menu(
        #      pystray.MenuItem("Toggle", self.timer.toggle),
        #      pystray.MenuItem("Exit", self.timer.exit)
        # )

        self.icon = self.inactive_img

    def activate(self):
        self.icon = self.active_img
        self.notify("Session started", "Session start")

    def deactivate(self, length: timedelta):
        self.icon = self.inactive_img
        self.notify(f"Session Duration: {length}", "Session end")

    # def check_running(self, length: timedelta):
    #     self.notify(f"Session Duration: {length}", "Session check")

    def check_stat(self, today_len: timedelta, prev_month_len: timedelta):
        self.notify(f"Today Length: {today_len}\nThis Month: {prev_month_len}", "Session check")


def gen_prev_month():
    record: Dict[str, List[pathlib.Path]] = {}
    for file_path in STORAGE.iterdir():
        if file_path.suffix != ".json" or "Error" in file_path.stem:
            continue
        try:
            record[file_path.stem[:-3]].append(file_path)
        except KeyError:
            record[file_path.stem[:-3]] = [file_path]

    for key, val in record.items():
        new_path = STORAGE.joinpath(f"{key}.txt")
        if new_path.exists() and new_path.stem not in str(datetime.now(TZ_TGT_INIT)):
            # then this is previous already calculated month, skip
            continue

        sum_ = timedelta()
        for path in val:
            try:
                file = path.read_text(encoding="utf8")
                json_ = json.loads(file)
                time_ = str_to_timedelta(json_["length"])
            except Exception as err:
                path_temp = STORAGE.joinpath(f"{path.stem}_{type(err).__name__}{path.suffix}")
                path.rename(path_temp)
            else:
                sum_ += time_
        new_path.write_text(f"{sum_}\nSession count:{len(val)}")


class Timer:
    def __init__(self, tray_instance: CustomTray):
        self.working = False
        self.sessions: List[Session] = []
        self.current_session: Union[Session, None] = None
        self.tray = tray_instance

        file_this_month = datetime.now(TZ_SRC_INIT).strftime("%Y-%m") + ".txt"
        time_string, _ = STORAGE.joinpath(file_this_month).read_text("utf8").split("\n")
        self.this_month = str_to_timedelta(time_string)

        logger.info("Initialized")
        self.load_session()

    def prompt_message(self):
        aggregated_time = session_sum(self.sessions)

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

        self.tray.deactivate(self.sessions[-1].length)

    def start(self):
        logger.debug("Called")
        if self.current_session:
            logger.warning("Session already running!")
            return

        self.current_session = Session()
        self.tray.activate()

    def toggle(self):
        logger.debug("Called")

        if self.current_session:
            self.stop()
        else:
            self.start()
        time.sleep(0.2)

    def check(self):
        logger.debug("Called")
        # if self.current_session:
        #     ring_multiple(2, freq=600)
        #     seconds = (self.total_length + self.current_session.length).total_seconds()
        # else:
        #     ring_multiple(1, freq=600)
        #     seconds = self.total_length.total_seconds()
        try:
            last_session = (
                self.current_session if self.current_session else self.sessions[-1]
            )
        except IndexError:
            self.tray.notify("No session in record", "Error")
        else:
            self.tray.check_stat(self.total_length, self.this_month)
            time.sleep(0.2)

    def exit(self):
        logger.debug("Called")
        if self.current_session:
            self.stop()

        self.save_session()
        exit(0)

    @property
    def total_length(self):
        cur = self.current_session.length if self.current_session else timedelta()
        return session_sum(self.sessions) + cur

    def load_session(self):
        file_name = datetime.now(TZ_SRC_INIT).strftime("%Y-%m-%d") + ".json"

        path_ = STORAGE.joinpath(file_name)

        if path_.exists():
            logger.info("Previous Session found. Loading session")
            existing = json.loads(path_.read_text("utf8"))

            self.sessions = [
                Session.from_json(entry) for entry in existing["entries"]
            ] + self.sessions

    def save_session(self):
        logger.debug("Called")
        file_name = self.sessions[0].start.strftime("%Y-%m-%d") + ".json"
        path_ = STORAGE.joinpath(file_name)

        current = [session.to_json() for session in self.sessions]

        output_dict = {
            "Sessions": len(current),
            "length": str(self.total_length),
            "entries": current,
        }

        path_.write_text(json.dumps(output_dict, indent=2), "utf8")
        logger.info("Saved sessions at {}", path_)


def main():
    gen_prev_month()

    tray = CustomTray()
    timer = Timer(tray)
    tray.run_detached()

    # toggle_hotkey = keyboard.HotKey(keyboard.HotKey.parse(TOGGLE_COMBINATION), timer.toggle)
    # exit_hotkey = keyboard.HotKey(keyboard.HotKey.parse(EXIT_COMBINATION), timer.exit)

    with keyboard.GlobalHotKeys(
        {TOGGLE_COMBO: timer.toggle, CHECK_COMBO: timer.check}
    ) as hotkey:
        hotkey.join()


if __name__ == "__main__":
    main()
