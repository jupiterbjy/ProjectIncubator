
import json
import pathlib
from contextlib import contextmanager
from datetime import datetime, timedelta
from textwrap import dedent
from typing import List, Union

import pytz


TIMEZONE_SOURCE = "Asia/Seoul"
TIMEZONE_TARGET = "America/Los_Angeles"

FORMAT = "%Y-%m-%d %a %H:%M"

TZ_SRC_INIT = pytz.timezone(TIMEZONE_SOURCE)
TZ_TGT_INIT = pytz.timezone(TIMEZONE_TARGET)

STORAGE = pathlib.Path(__file__).parent.joinpath("Sessions")
STORAGE.mkdir(exist_ok=True)


def fmt(dt: datetime):
    return dt.strftime(FORMAT)


@contextmanager
def pad_lines():
    print("\n" * 50)
    yield
    print("\n")


class Session:
    def __init__(self, index=0):
        self.index = index

        self.start = datetime.now(TZ_SRC_INIT)
        self.end = None

        self.alt_tz_start = self.start.astimezone(TZ_TGT_INIT)
        self.alt_tz_end = None

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
        if self._calculated:
            return self._calculated

        raise RuntimeError("Session is still running.")

    def to_json(self):
        dict_ = {
            "duration": str(self._calculated),
            TIMEZONE_SOURCE: {
                "start": self.start.isoformat(),
                "end": self.end.isoformat(),
            },
            TIMEZONE_TARGET: {
                "start": self.alt_tz_start.isoformat(),
                "end": self.alt_tz_end.isoformat(),
            }
        }

        return dict_


class Timer:
    def __init__(self):
        self.working = False
        self.sessions: List[Session] = []
        self.current_session: Union[Session, None] = None

        self.run = True

    def prompt_message(self):
        aggregated_time = sum((session.length for session in self.sessions), start=timedelta())

        print(
            f"Aggregated: {aggregated_time}",
            f"Sessions count: {len(self.sessions)}",
            f"Session Running: Session {self.current_session.index}"
            f" started at {self.current_session.start.astimezone(TZ_SRC_INIT)}" if self.current_session else "",
            sep="\n"
        )

    def stop(self):
        with pad_lines():
            try:
                self.current_session.stop()
            except AttributeError:
                print("No sessions to stop!")
            else:
                self.sessions.append(self.current_session)
                self.current_session = None

    def start(self):
        with pad_lines():
            if self.current_session:
                print("Session already running!")
                return

            self.current_session = Session(len(self.sessions))

    def exit(self):
        with pad_lines():
            if self.current_session:
                self.stop()

            self.print_sessions()

            self.save_session()
            input("\nPress enter to exit.")

        exit(0)

    def save_session(self):
        data = [session.to_json() for session in self.sessions]
        file_name = self.sessions[0].start.strftime("%Y-%m-%d") + ".json"

        path_ = STORAGE.joinpath(file_name)

        if path_.exists():
            existing = json.loads(path_.read_text("utf8"))
            existing.extend(data)

            data = existing

        path_.write_text(json.dumps(data, indent=2), "utf8")
        print("Saved sessions at", path_)

    def print_sessions(self):
        with pad_lines():
            print("\n".join((str(session) for session in self.sessions)))

    def start_parse_input(self):
        mapping = {"set": self.start, "stop": self.stop, "exit": self.exit, "show": self.print_sessions}

        while self.run:
            try:
                self.prompt_message()

                mapping[input("Enter command: ")]()
            except KeyError:
                continue


if __name__ == '__main__':
    timer = Timer()
    timer.start_parse_input()
