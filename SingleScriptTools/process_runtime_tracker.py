"""
Simple (& terrible) script to track process runtime by pooling processes every 10 seconds.

Tracked time is written to a sqlite3 database created next to this script.

`pip install psutil`

:Author: jupiterbjy@gmail.com
"""

import datetime
import re
import time
import pathlib
import sqlite3
from argparse import ArgumentParser
from typing import TypedDict

import psutil


# --- Config ---

DB_PATH = pathlib.Path(__file__).parent / "process_runtime_tracker.sqlite"

# Check intervals in seconds
CHECK_INTERVAL_SEC = 5.0

# DB Configurations
TABLE_NAME = "process_times"
CREATE_QUERY = (
    f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} (process TEXT PRIMARY KEY, time REAL)"
)
UPDATE_QUERY = f"INSERT INTO {TABLE_NAME} (process, time) VALUES (?, ?) ON CONFLICT(process) DO UPDATE SET time=time+?"
FETCH_ALL_QUERY = f"SELECT * FROM {TABLE_NAME}"

RE_PATTERN = re.compile(r"[^\W.]+")

# List of process names to track time of.
# Will ignore all parts unmatched from above RE_PATTERN.
# i.e. "SomeProcess_abc.exe" -> "someprocess_abc"
# noinspection SpellCheckingInspection
PROCESS_WHITELIST = {"hikari_kr", "shinku_kr", "kate", "pycharm"}


# --- Utilities ---


def _normalize_process_name(raw_proc_name: str) -> str:
    """Normalizes process name. Returns an empty string if it's unable to be normalized."""

    matched = RE_PATTERN.match(raw_proc_name)
    normalized_name = matched.group(0).lower() if matched else ""

    return normalized_name


def _clear_screen(newlines=100):
    """Just pushes a bunch of newlines to mimic screen clear."""

    print("\n" * newlines)


def _sec_to_human_readable(sec: float) -> str:
    """Converts seconds to human-readable format"""

    return str(datetime.timedelta(seconds=sec))


class _ProcessEntryType(TypedDict):
    proc_name: str
    accumulated_sec: float


# --- Logics ---


def db_update_time(
    db_conn: sqlite3.Connection, process_name: str, duration_added: float
):
    """Adds the process's runtime to db"""

    db_conn.execute(UPDATE_QUERY, (process_name, duration_added, duration_added))


def db_list_records(db_conn: sqlite3.Connection):
    """Returns a list of (process_name, duration) tuples"""

    return db_conn.execute(FETCH_ALL_QUERY).fetchall()


def main_loop(conn: sqlite3.Connection):
    """Primary loop"""

    next_t = time.time()

    while True:
        next_t += CHECK_INTERVAL_SEC
        time.sleep(next_t - time.time())

        for process in psutil.process_iter(["name"]):
            normalized = _normalize_process_name(process.info["name"])

            if normalized in PROCESS_WHITELIST:
                db_update_time(conn, normalized, CHECK_INTERVAL_SEC)

        conn.commit()

        _clear_screen()
        print("Process Time Summary:")
        print(
            *(
                f"{pn:10}:{_sec_to_human_readable(t)}"
                for pn, t in db_list_records(conn)
            ),
            sep="\n",
        )


def main():
    print(f"Tracking following processes:\n{PROCESS_WHITELIST}\n")

    # im god darn lazy so gonna create inmem db to reduce write without changing code..
    in_mem_conn = sqlite3.connect(":memory:")
    in_mem_conn.execute(CREATE_QUERY)

    try:
        main_loop(in_mem_conn)
    finally:
        print("Saving results...")

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(CREATE_QUERY)

            # add in-mem db times to local data
            conn.executemany(
                UPDATE_QUERY,
                ((pn, t, t) for (pn, t) in db_list_records(in_mem_conn)),
            )
            conn.commit()

        print("All done!")


if __name__ == "__main__":
    _parser = ArgumentParser("Script to track time spent on each whitelisted processes")

    _parser.add_argument(
        "-a",
        "--add-processes",
        action="extend",
        nargs="+",
        type=str,
        help="Add process to whitelist, for use-cases where editing script isn't viable.",
    )

    _args = _parser.parse_args()
    if _args.add_processes:
        PROCESS_WHITELIST.update(_args.add_processes)

    main()
