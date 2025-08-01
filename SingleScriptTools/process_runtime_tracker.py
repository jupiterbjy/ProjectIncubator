"""
Simple (& terrible) script to track process runtime by pooling processes every 10 seconds.

Tracked time is written to a sqlite3 database created next to this script.

`pip install psutil`

:Author: jupiterbjy@gmail.com
"""

import datetime
import itertools
import re
import time
import pathlib
import sqlite3
import subprocess
from textwrap import dedent
from argparse import ArgumentParser
from typing import TypedDict


# --- Config ---

# Compiled regex pattern for normalizing process name
# PN_NORMALIZE_PATTERN = re.compile(r"[^\W.]+")
PN_NORMALIZE_PATTERN = re.compile(r"\w+")

# List of process names to track time of.
# noinspection SpellCheckingInspection
PROCESS_WHITELIST = {
    _pn
    # PN_NORMALIZE_PATTERN.match(_pn).group(0)
    for _pn in {"Hikari_KR", "Shinku_KR", "kate", "pycharm64", "notepad++"}
}

# Command to use to get process name list
PROC_LIST_CMD = (
    'powershell -Command "Get-Process | Select-Object -ExpandProperty ProcessName"'
)
# PROC_LIST_CMD = "ps -e -o comm="

DB_PATH = pathlib.Path(__file__).parent / "process_runtime_tracker.sqlite"

# Check intervals in seconds
CHECK_INTERVAL_SEC = 5.0

# Commit intervals in iteration(CHECK_INTERVAL_SEC)
COMMIT_INTERVAL_ITER = 12


class Query:
    """Namespace for queries, so it's easier to edit"""

    create_table = """
    CREATE TABLE IF NOT EXISTS "{}"
    (start_utc INTEGER, end_utc INTEGER, time REAL, PRIMARY KEY(start_utc))
    """
    create_table = dedent(create_table).strip().replace("\n", " ")

    update = """
    INSERT INTO "{}" VALUES (?, ?, ?)
    ON CONFLICT(start_utc) DO UPDATE SET end_utc=?, time=time+?
    """
    update = dedent(update).strip().replace("\n", " ")

    total_time = 'SELECT SUM(time) FROM "{}"'

    fetch_all = 'SELECT * FROM "{}"'

    single_time = 'SELECT time FROM "{}" WHERE start_utc=?'


# --- Utilities ---


def _normalize_process_name(raw_proc_name: str) -> str:
    """Normalizes process name. Returns an empty string if it's unable to be normalized."""

    matched = PN_NORMALIZE_PATTERN.match(raw_proc_name)
    normalized_name = matched.group(0) if matched else ""
    # normalized_name = matched.group(0).lower() if matched else ""

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


def get_processes() -> set[str]:
    """Returns a set of process names. Errors are ignored."""

    result = subprocess.run(PROC_LIST_CMD, shell=True, capture_output=True)
    return set(result.stdout.decode("utf-8").splitlines())


def print_time(conn: sqlite3.Connection, process_name: str, start_t: int):
    """Print give process's accumulated time"""

    p_time = _sec_to_human_readable(db_single_time(conn, process_name, start_t))
    total_time = _sec_to_human_readable(db_total_time(conn, process_name))
    print(f"{process_name:20} - {p_time:>10} ({total_time})")


# --- Logics ---


def db_update_time(
    db_conn: sqlite3.Connection, process_name: str, start_t: int, duration_added: float
):
    """Adds the process's runtime to db"""

    end_t = int(time.time())
    db_conn.execute(
        Query.update.format(process_name),
        (start_t, end_t, duration_added, end_t, duration_added),
    )


def db_list_records(db_conn: sqlite3.Connection, process_name: str) -> list[tuple]:
    """Returns a list of (process_name, duration) tuples"""

    return db_conn.execute(Query.fetch_all.format(process_name)).fetchall()


def db_total_time(db_conn: sqlite3.Connection, process_name: str) -> float:
    """Returns total accumulated playtime"""

    return db_conn.execute(Query.total_time.format(process_name)).fetchone()[0] or 0.0


def db_single_time(
    db_conn: sqlite3.Connection, process_name: str, start_t: int
) -> float:
    """Returns single process's runtime"""

    return (
        db_conn.execute(Query.single_time.format(process_name), (start_t,)).fetchone()[
            0
        ]
        or 0.0
    )


def ensure_table_exists(db_conn: sqlite3.Connection):
    """Ensures that the given table exists in the db"""

    for process_name in PROCESS_WHITELIST:
        db_conn.execute(Query.create_table.format(process_name))


def main_loop(conn: sqlite3.Connection):
    """Primary loop"""

    start_ts = {}
    next_t = time.time()
    next_commit = itertools.cycle(range(COMMIT_INTERVAL_ITER))

    while True:
        next_t += CHECK_INTERVAL_SEC
        try:
            time.sleep(next_t - time.time())

        except ValueError:
            # python process must've been paused and gives negative sleep time, reset time
            next_t = time.time() + CHECK_INTERVAL_SEC
            continue

        processes = get_processes()

        _clear_screen()
        print("Process Time Summary:")

        for process in processes:
            pn = process
            # pn = _normalize_process_name(process.info["name"])

            if pn not in PROCESS_WHITELIST:
                continue

            # if it wasn't started before register start time to use as pkey
            if pn not in start_ts:
                start_ts[pn] = int(time.time())

            db_update_time(conn, pn, start_ts[pn], CHECK_INTERVAL_SEC)
            print_time(conn, pn, start_ts[pn])

        # check for inactive processes and clear start times
        for process in PROCESS_WHITELIST:
            if process not in processes:
                start_ts.pop(process, None)

        if next(next_commit) == 0:
            conn.commit()


def main():
    print(f"Tracking following processes:\n{PROCESS_WHITELIST}\n")

    # in_mem_conn = sqlite3.connect(":memory:")
    # in_mem_conn.execute(CREATE_QUERY)

    with sqlite3.connect(DB_PATH) as conn:
        ensure_table_exists(conn)
        conn.commit()

        try:
            main_loop(conn)
        finally:
            conn.commit()


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
        PROCESS_WHITELIST.update(
            # _normalize_process_name(_pn) for _pn in _args.add_processes
            _pn
            for _pn in _args.add_processes
        )

    main()
