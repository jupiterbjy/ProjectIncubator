"""
Simple (& terrible) script to track process runtime by pooling processes every 10 seconds.

Either edit `PROCESS_WHITELIST` or use argument to specify which processes to track.
Tracked time is written to a sqlite3 database created next to this script.

No external dependencies are required, as long as provided default `PROC_LIST_CMD` works for you.

![](readme_res/process_runtime_tracker.jpg)

:Author: jupiterbjy@gmail.com
"""

import itertools
import platform
import time
import pathlib
import sqlite3
import subprocess
from datetime import timedelta
from argparse import ArgumentParser


# --- Config ---

# List of process names to track time of
# noinspection SpellCheckingInspection
PROCESS_WHITELIST = {
    "Hikari_KR",
    "Shinku_KR",
    "kate",
    "pycharm64",
    "notepad++",
    "HoshimemoEH_HD",
    "HoshiMemo_HD",
    "iroseka_HD_EN_steam",
    "Sakura_KR",
}

# Command to use to fetch process names, so we don't need psutil dependency
PROC_LIST_CMD = {
    "Windows": 'powershell -Command "Get-Process | Select-Object -ExpandProperty ProcessName"',
    "Linux": "ps -u $(whoami) -o comm=",
}[platform.system()]

DB_PATH = pathlib.Path(__file__).parent / "process_runtime_tracker.sqlite"

# Check intervals in seconds
CHECK_INTERVAL_SEC = 5.0

# Commit intervals in iteration (CHECK_INTERVAL_SEC * COMMIT_INTERVAL_ITER)
COMMIT_INTERVAL_ITER = 12


# --- Utilities ---


def _clear_screen(newlines=100):
    """Just pushes a bunch of newlines to mimic screen clear."""

    print("\n" * newlines)


def get_processes() -> set[str]:
    """Returns a set of process names. Errors are ignored."""

    result = subprocess.run(PROC_LIST_CMD, shell=True, capture_output=True)
    return set(result.stdout.decode("utf-8").splitlines())


# noinspection SqlNoDataSourceInspection,SqlResolve
class _Query:
    """Namespace for queries, so it's easier to edit"""

    create_table = """
    CREATE TABLE IF NOT EXISTS "{}" (start_utc INTEGER, end_utc INTEGER, time REAL, PRIMARY KEY(start_utc))
    """

    update = """
    INSERT INTO "{}" VALUES (?, ?, ?) ON CONFLICT(start_utc) DO UPDATE SET end_utc=?, time=time+?
    """

    total_time = 'SELECT SUM(time) FROM "{}"'

    fetch_all = 'SELECT * FROM "{}"'

    single_time = 'SELECT time FROM "{}" WHERE start_utc=?'


class DBWrapper:
    """Wraps sqlite3 database to simplify interfaces. Use this as context manager."""

    def __init__(self, db_path: pathlib.Path):
        self._path = db_path
        self._conn = None

    def __enter__(self):
        self._conn = sqlite3.connect(self._path)
        self._ensure_tables_exist()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.commit()
        self._conn.close()

    def _ensure_tables_exist(self):
        """Makes sure all tables exist in the db"""

        for process_name in PROCESS_WHITELIST:
            self._conn.execute(_Query.create_table.format(process_name))

        self._conn.commit()

    def commit(self):
        """Commit changes to DB"""

        self._conn.commit()

    def update_session_record(
        self,
        process_name: str,
        start_t: int,
        duration_added: float,
    ):
        """Increases/Set duration for given session."""

        end_t = int(time.time())
        self._conn.execute(
            _Query.update.format(process_name),
            (start_t, end_t, duration_added, end_t, duration_added),
        )

    def get_session_records(self, process_name: str) -> list[tuple[int, int, float]]:
        """Returns a list of (start_unix_time, end_unix_time, duration) tuples"""

        return self._conn.execute(_Query.fetch_all.format(process_name)).fetchall()

    def get_total_time(self, process_name: str) -> float:
        """Returns total accumulated playtime for the given process"""

        return (
            self._conn.execute(_Query.total_time.format(process_name)).fetchone()[0]
            or 0.0
        )

    def get_session_time(self, process_name: str, start_t: int) -> float:
        """Returns single process's runtime"""

        return (
            self._conn.execute(
                _Query.single_time.format(process_name), (start_t,)
            ).fetchone()[0]
            or 0.0
        )

    def print_time(self, process_name: str, start_t: int):
        """Print give process's accumulated time in human-readable format"""

        p_time = str(timedelta(seconds=self.get_session_time(process_name, start_t)))
        total_time = str(timedelta(seconds=self.get_total_time(process_name)))

        print(f"{process_name:20} - {p_time:>10} ({total_time})")


# --- Logics ---


def update_time(db: DBWrapper, start_ts: dict[str, int], commit=False):
    """Fetch processes and update process runtime in db.

    Args:
        db: DBWrapper instance
        start_ts: {process_name: start_time_of_session} dict
        commit: Whether to commit changes to db or not.
    """

    processes = PROCESS_WHITELIST & get_processes()

    _clear_screen()
    print("Process Time Summary:")

    for process in processes:
        pn = process

        # if it wasn't started before, register start time
        if pn not in start_ts:
            start_ts[pn] = int(time.time())

        db.update_session_record(pn, start_ts[pn], CHECK_INTERVAL_SEC)
        db.print_time(pn, start_ts[pn])

    # check for inactive processes and clear start times
    for process in PROCESS_WHITELIST - processes:
        start_ts.pop(process, None)

    if commit:
        db.commit()


def main():
    print(f"Tracking following processes:\n{PROCESS_WHITELIST}\n")

    start_ts = {}
    next_t = time.time()
    next_commit = itertools.cycle(range(COMMIT_INTERVAL_ITER))

    with DBWrapper(DB_PATH) as db:
        while True:

            # set next wakeup time
            next_t += CHECK_INTERVAL_SEC
            try:
                time.sleep(next_t - time.time())

            except ValueError:
                # python process must've been paused and gives negative sleep time, reset time
                next_t = time.time()
                continue

            update_time(db, start_ts, next(next_commit) == 0)


if __name__ == "__main__":
    _parser = ArgumentParser("Script to track time spent on each whitelisted processes")

    _parser.add_argument(
        "-a",
        "--whitelist",
        action="extend",
        nargs="+",
        type=str,
        help="Process name whitelist, for use-cases where editing script isn't viable.",
    )

    _args = _parser.parse_args()
    if _args.whitelist:
        PROCESS_WHITELIST = set(_args.whitelist)

    main()
