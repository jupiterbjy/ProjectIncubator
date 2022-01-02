"""
Used for recording start, end time of work session.

This is sort of wheel re-inventing of simple timer, but I couldn't find way to record time on this thing.
"""

import time
import json
import pathlib
import sqlite3
from contextlib import contextmanager, AbstractContextManager
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

# DB
NAME = "data.db"

# Generate paths
ROOT = pathlib.Path(__file__).parent
STORAGE = ROOT.joinpath("Sessions")
STORAGE.mkdir(exist_ok=True)
IMG_PATH = ROOT.joinpath("icon")

LOG_PATH = ROOT.joinpath("logs")
LOG_PATH.mkdir(exist_ok=True)


# Config resource paths

logger.add(
    LOG_PATH.joinpath("work_{time}.log").as_posix(),
    rotation="5 MB",
    retention="7 days",
    compression="zip",
)


def tz_src_now():
    return datetime.now(TZ_SRC_INIT)


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


def get_month_relative(index: int, tz=None):
    """
    Relative month calculator. Work similar to dateutil relative delta.

    Args:
        index(int): offset
        tz: if supplied, uses given timezone when calling datetime.now().

    Returns:
        (Tuple[int, int]): year and month
    """

    dt_now = datetime.now(tz)

    if index > 0:
        adder = timedelta(days=3)
        while index > 0:
            index -= 1
            dt_now = dt_now.replace(day=28) + adder

    else:
        subtractor = timedelta(days=1)
        while index < 0:
            index += 1
            dt_now = dt_now.replace(day=1) - subtractor

    return dt_now.year, dt_now.month


class Session:
    def __init__(self):

        self.start = tz_src_now()
        self.end: Union[datetime, None] = None

        self.index = int(self.start.timestamp())

        self.alt_tz_start = self.start.astimezone(TZ_TGT_INIT)
        self.alt_tz_end = None

        self.tz_local = TIMEZONE_SOURCE
        self.tz_remote = TIMEZONE_TARGET

        self._calculated: Union[None, timedelta] = None

    def stop(self):
        self.end = tz_src_now()
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
                return tz_src_now() - self.start

        return self._calculated


def session_sum(iterable: Iterable) -> timedelta:
    return sum((session.length for session in iterable), start=timedelta())


class DBWrapper:
    # spamming contextmanager here because I couldn't catch system exit event
    # so every action should open and close the connection

    def __init__(self, db_path_):
        self.path = db_path_

        with self.con() as con:
            con.execute(
                "CREATE TABLE IF NOT EXISTS ACCUMULATION("
                "ts DOUBLE PRIMARY KEY, y INTEGER, m INTEGER, d INTEGER, total_sec DOUBLE"
                ")"
            )

            con.commit()

    @contextmanager
    def con(self) -> AbstractContextManager[sqlite3.Connection]:
        connection: Union[None, sqlite3.Connection] = None
        try:
            connection = sqlite3.connect(self.path)
            yield connection
        finally:
            if connection:
                connection.close()

    @contextmanager
    def cursor(self) -> AbstractContextManager[sqlite3.Cursor]:
        with self.con() as con:
            try:
                yield con.cursor()
            finally:
                pass

    def add_session(self, session: Session):
        start_dt = session.start
        length = session.length.total_seconds()

        with self.con() as con:
            con.execute(
                "INSERT INTO ACCUMULATION(ts, y, m, d, total_sec) VALUES(?, ?, ?, ?, ?)",
                (
                    start_dt.timestamp(),
                    start_dt.year,
                    start_dt.month,
                    start_dt.day,
                    length,
                ),
            )

            con.commit()

    def get_month_total(self, year, month) -> float:
        """
        Accumulate and return total seconds of month with given year and month.

        Args:
            year(int): year
            month(int): month

        Returns:
            (float): Accumulated total seconds of given month index

        Raises:
            AssertionError: When provided time is future or invalid
        """
        now = datetime.now()
        y_cur = now.year
        m_cur = now.month

        assert 1 <= month <= 12 and year >= 0, "Input is invalid"
        assert not (
            year > y_cur or (year == y_cur and month > m_cur)
        ), "Tried to perform time travel"

        with self.cursor() as cursor:
            cursor.execute(
                "SELECT total_sec FROM ACCUMULATION WHERE y = ? AND m = ?",
                (year, month),
            )

            return sum(wrapped[0] for wrapped in cursor.fetchall())

    def get_month_total_relative(self, relative_month: int = 0) -> float:
        """
        Accumulate and return total seconds of month with given relative index.

        Args:
            relative_month(int): Optional. Relative index of month to search.

        Returns:
            (float): Accumulated total seconds of given month index

        Raises:
            AssertionError: When relative month is <= 0
        """

        assert relative_month <= 0, "Tried to perform time travel"

        target_year, target_month = get_month_relative(relative_month, TZ_SRC_INIT)
        return self.get_month_total(target_year, target_month)

    @property
    def is_emtpy(self) -> bool:

        self.cursor.execute("SELECT EXISTS(SELECT 1 FROM ACCUMULATION)")

        return not self.cursor.fetchone()[0]


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

    def running_check_stat(
        self,
        current: timedelta,
        today: timedelta,
        this_month: timedelta,
        last_month: timedelta,
    ):
        self.notify(
            f"Current: {current}\nToday Length: {today}\nThis Month: {this_month}\nLast Month: {last_month}",
            "Session check",
        )

    def check_stat(
        self, today: timedelta, this_month: timedelta, last_month: timedelta
    ):
        self.notify(
            f"Today Length: {today}\nThis Month: {this_month}\nLast Month: {last_month}",
            "Session check",
        )


def gen_prev_month():
    record: Dict[str, List[pathlib.Path]] = {}
    now = str(datetime.now(TZ_TGT_INIT))

    for file_path in STORAGE.iterdir():
        if file_path.suffix != ".json" or "Error" in file_path.stem:
            continue
        try:
            record[file_path.stem[:-3]].append(file_path)
        except KeyError:
            record[file_path.stem[:-3]] = [file_path]

    for key, val in record.items():
        new_path = STORAGE.joinpath(f"{key}.txt")
        if new_path.exists() and new_path.stem not in now:
            # then this is previous already calculated month, skip
            continue

        sum_ = timedelta()
        for path in val:
            try:
                file = path.read_text(encoding="utf8")
                json_ = json.loads(file)
                time_ = str_to_timedelta(json_["length"])
            except Exception as err:
                path_temp = STORAGE.joinpath(
                    f"{path.stem}_{type(err).__name__}{path.suffix}"
                )
                path.rename(path_temp)
            else:
                sum_ += time_
        new_path.write_text(f"{sum_}\nSession count:{len(val)}")


class Timer:
    def __init__(self, tray_instance: CustomTray):
        self.working = False
        self.current_session: Union[Session, None] = None
        self.tray = tray_instance

        self.db = DBWrapper(STORAGE.joinpath(NAME))

        logger.info("Initialized")

    def stop(self):
        logger.debug("Called")
        try:
            self.current_session.stop()
        except AttributeError:
            logger.warning("No sessions to stop!")
        else:
            self.tray.deactivate(self.current_session.length)
            self.save_session()

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
        current_month = timedelta(seconds=self.db.get_month_total_relative(0))
        last_month = timedelta(seconds=self.db.get_month_total_relative(-1))

        if self.current_session:
            self.tray.running_check_stat(
                self.current_session.length,
                self.total_length,
                current_month,
                last_month,
            )
        else:
            self.tray.check_stat(self.total_length, current_month, last_month)

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
        return timedelta(seconds=self.db.get_month_total_relative(0)) + cur

    def save_session(self):
        logger.debug("Called")
        self.db.add_session(self.current_session)
        self.current_session = None


def main():
    gen_prev_month()

    tray = CustomTray()
    timer = Timer(tray)
    tray.run_detached()

    with keyboard.GlobalHotKeys(
        {TOGGLE_COMBO: timer.toggle, CHECK_COMBO: timer.check}
    ) as hotkey:
        hotkey.join()


if __name__ == "__main__":
    main()
