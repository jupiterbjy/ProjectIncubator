"""
Simple script to track focused window and measure total time
whenever there's input with configurable margin, windows only.

`pip install win32gui, win32process, psutil, pynput`

![](readme_res/effective_work_timer.png)

:Author: jupiterbjy@gmail.com
"""

import datetime
import pathlib
import re
import time
import functools
import json
import traceback
from argparse import ArgumentParser
from typing import TypedDict, Sequence

import win32gui
import win32process
import psutil
import pynput


# --- Constants ---

TIMEOUT_SEC = 30

PRINT_INTERVAL_SEC = 1

KEY_TYPE = pynput.keyboard.Key | pynput.keyboard.KeyCode

# Combination of keys to pause/quit timer. Uses pynput's Key.
STOP_HOTKEY: list[KEY_TYPE] = [
    pynput.keyboard.KeyCode.from_char("8"),
    pynput.keyboard.KeyCode.from_char("9"),
    pynput.keyboard.KeyCode.from_char("0"),
    # pynput.keyboard.Key.f12,
]

LOG_ENCODING = "utf-8"

LOG_LOCATION = pathlib.Path(__file__).parent / "effective_work_timer_results.json"

RE_PATTERN = re.compile(r"[^\W\-_.]+")

# List of process names to consider as "work" - this is just an example.
# Will ignore all parts unmatched from above RE_PATTERN. Name is all lowercased prior to matching.
# i.e. "SomeProcess_abc.exe" -> "someprocess"
# noinspection SpellCheckingInspection
WORK_PROCESS_WHITELIST = {
    "fleet",
    "msedge",
    "godot",
    "blender",
    "paintdotnet",
    "inkscape",
    "windowsterminal",
    "audacity",
    # "notepad++",
    "notepad",
    "obs",
    "pycharm64",
    "rider64",
    "explorer",
}

# used for formatting
_MAX_PROC_NAME_LEN = max(len(proc_name) for proc_name in WORK_PROCESS_WHITELIST)


# --- Utilities ---


def _get_active_window_process_name() -> str:
    """Get currently focused window's process name.
    Returns empty string if unable to get process name.

    References:
        https://stackoverflow.com/a/65363087/10909029

    Returns:
        Process's Name. Raises

    Raises:
        ValueError: When negative PID is received
        psutil.NoSuchProcess: When process with given PID is not found(idk how yet)
    """

    pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[-1]
    return psutil.Process(pid).name()


def _normalize_process_name(raw_proc_name: str) -> str:
    """Normalizes process name. Returns empty string if it's unable to be normalized."""

    matched = RE_PATTERN.match(raw_proc_name)
    normalized_name = matched.group(0).lower() if matched else ""

    return normalized_name


def _clear_screen(newlines=100):
    """Just pushes a bunch of newlines to mimic screen clear."""

    print("\n" * newlines)


def _sec_to_human_readable(sec: float) -> str:
    """Converts seconds to human-readable format.
    (Personally raw seconds isn't that bad though)
    (nvm it is helpful to have both actually, mybad)
    """

    return str(datetime.timedelta(seconds=sec))


class _ProcessEntryType(TypedDict):
    proc_name: str
    accumulated_sec: float


class _ResultEntryType(TypedDict):
    duration: float
    effective_duration: float
    processes: list[_ProcessEntryType]


_ResultsType: dict[int, _ResultEntryType]


# --- Logics ---


class HotKeyManager:
    """Class managing hotkey state.
    This is due to pynput seemingly can't mix global hotkey to listeners."""

    def __init__(self, hotkeys: Sequence[KEY_TYPE]):

        # hotkey status
        self._hotkey_status: dict[KEY_TYPE, bool] = {key: False for key in hotkeys}

        self.triggered = False

    def update_hotkey_status(self, key: KEY_TYPE, pressed: bool):
        """Check which keys are currently pressed, and toggle pause flag when all keys are pressed.
        Ignores non-hotkey keys."""

        if key not in self._hotkey_status:
            return

        self._hotkey_status[key] = pressed

        if all(self._hotkey_status.values()):
            self.triggered = not self.triggered


class Tracker:
    """Tracks work time with non-busy method."""

    def __init__(self):

        # per process's accumulated time
        self._per_proc_accumulations: dict[str, float] = {}

        # started time, floored so it can act as key in dict without being too long.
        self._start_time = int(time.time())

        # last process name
        self._last_proc_name = ""

        # last input time
        self._last_input_time = 0.0

        # started time string
        self._start_time_str = datetime.datetime.fromtimestamp(
            self._start_time
        ).strftime("%Y-%m-%d %H:%M:%S")

    @property
    def _elapsed(self) -> float:
        return time.time() - self._start_time

    @property
    def _active_total(self) -> float:
        """Returns sum of active duration of all processes."""

        # would love to see caching of these sum... but welp doesn't matter much for now
        return sum(self._per_proc_accumulations.values())

    def print_stats(self):
        """Prints total accumulated time and per process's accumulated time."""

        _clear_screen()

        elapsed = int(self._elapsed)
        active_total = int(self._active_total)

        # print generic info
        print(
            f"Start Time       : {self._start_time_str}",
            f"Elapsed          : {_sec_to_human_readable(elapsed)} ({elapsed}s)",
            f"Total Accumulated: {_sec_to_human_readable(active_total)} ({active_total}s)",
            f"Efficiency       : {active_total / elapsed if elapsed else 0:.2%}",
            f"Current Focused  : {self._last_proc_name}",
            sep="\n",
        )

        # print per process time
        print("\n# Per Process Accumulated")
        for proc_name, accumulated_sec in self._per_proc_accumulations.items():
            print(
                f"{proc_name:{_MAX_PROC_NAME_LEN}}: {_sec_to_human_readable(int(accumulated_sec))}s"
            )

        # print(self._hotkey_status)
        print(f"\nPress {STOP_HOTKEY} to stop timer.")

    def tick(self):
        """Updates per process's accumulated time and total accumulated time.
        Call this on every new input events. Does nothing when paused."""

        cur_time = time.time()

        # fetch process name
        try:
            proc_name = _normalize_process_name(_get_active_window_process_name())

        except ValueError:
            # negative PID received
            proc_name = ""

        except psutil.NoSuchProcess:
            # process not found, probably due to delay or some system process?
            proc_name = ""

        except Exception as _err:
            # unknown error, but gotta catch anyway to prevent listeners dying.
            traceback.print_tb(_err.__traceback__)
            proc_name = ""

        # check if last process was valid, if so accumulate
        if self._last_proc_name in WORK_PROCESS_WHITELIST:
            duration = min(cur_time - self._last_input_time, TIMEOUT_SEC)

            # feels like setdefault better be fitting here, but whatever
            # 99.9% gonna be success anyway so checking all time might be more wasteful
            try:
                self._per_proc_accumulations[self._last_proc_name] += duration
            except KeyError:
                self._per_proc_accumulations[self._last_proc_name] = duration

        self._last_proc_name = proc_name
        self._last_input_time = cur_time

    def write_result(self):
        """Flush log to file as json. If file exists, attempts to open and add entry to it."""

        # wish to use SQLite here but feels like it's overkill...

        existing: _ResultsType = {}

        # attempt load existing, if failure just overwrite
        if LOG_LOCATION.exists():
            try:
                existing.update(json.loads(LOG_LOCATION.read_text(LOG_ENCODING)))
            except (ValueError, json.JSONDecodeError):
                pass

        # add new entry, this automatically overwrites existing entry with same key(start time)
        existing[self._start_time] = {
            "duration": self._elapsed,
            "effective_duration": self._active_total,
            "processes": [
                {"proc_name": proc_name, "accumulated_sec": accumulated_sec}
                for proc_name, accumulated_sec in self._per_proc_accumulations.items()
            ],
        }

        # write back
        LOG_LOCATION.write_text(json.dumps(existing, indent=2), LOG_ENCODING)
        print(f"Result saved!")


# def main_loop_coro():
#     """Primary coroutine to track work time.
#     Send True to continue, False to exit."""
#
#     total_accumulated = 0.0
#
#     last_proc_name = ""
#     last_input_time = 0.0
#
#     should_continue = True
#
#     while should_continue:
#         should_continue = yield
#
#         cur_time = time.time()
#
#         # fetch process name
#         proc_name = _get_active_window_process_name()
#
#         # check if last process was valid, if so accumulate
#         if _is_process_valid(last_proc_name):
#             duration = min(cur_time - last_input_time, TIMEOUT_SEC)
#             total_accumulated += duration
#
#         last_proc_name = proc_name
#         last_input_time = cur_time
#
#     print("Exit requested!")


# --- Drivers ---


def _on_mouse_move(tracker: Tracker, _x: int, _y: int):
    tracker.tick()


def _on_mouse_scroll(tracker: Tracker, _x: int, _y: int, _dx: int, _dy: int):
    tracker.tick()


def _on_mouse_click(
    tracker: Tracker, _x: int, _y: int, _button: pynput.mouse.Button, _pressed: bool
):
    tracker.tick()


def _on_key_press(tracker: Tracker, hotkey_manager: HotKeyManager, key: KEY_TYPE):
    # print("p", type(key), repr(key))
    tracker.tick()
    hotkey_manager.update_hotkey_status(key, True)


def _on_key_release(tracker: Tracker, hotkey_manager: HotKeyManager, key: KEY_TYPE):
    # print("r", repr(key))
    tracker.tick()
    hotkey_manager.update_hotkey_status(key, False)
    # due to design when paused it may record as TIMEOUT_SEC but that's small enough error
    # when this deals with hours


def _main(extra_processes: Sequence[str], save_result: bool):

    if save_result:
        print("Result will be saved to:", LOG_LOCATION, end="\n\n")

    # add extra processes to whitelist
    WORK_PROCESS_WHITELIST.update(extra_processes)

    print("Will start scanning for following processes:")

    for _proc_name in WORK_PROCESS_WHITELIST:
        print(f" - {_proc_name}")

    print(f"\nWith timeout of {TIMEOUT_SEC} sec.")
    print(f"Status is logged only on every {PRINT_INTERVAL_SEC} sec.")

    while True:
        # check whether to start new session or to quit.
        # only consider last input as some input might get mixed
        if not input("\nStart new session? [y/n]: ")[-1] in "yY":
            return

        tracker = Tracker()

        # prep listeners
        hotkey_mgr = HotKeyManager(STOP_HOTKEY)

        mouse_listener = pynput.mouse.Listener(
            on_move=functools.partial(_on_mouse_move, tracker),
            on_scroll=functools.partial(_on_mouse_scroll, tracker),
            on_click=functools.partial(_on_mouse_click, tracker),
        )

        keyboard_listener = pynput.keyboard.Listener(
            on_press=functools.partial(_on_key_press, tracker, hotkey_mgr),
            on_release=functools.partial(_on_key_release, tracker, hotkey_mgr),
        )

        with mouse_listener, keyboard_listener:
            # just a dumb ctrl+c catcher for windows. with occasional logging
            while not hotkey_mgr.triggered:
                tracker.print_stats()
                time.sleep(PRINT_INTERVAL_SEC)

            if save_result:
                tracker.write_result()


if __name__ == "__main__":
    _parser = ArgumentParser(
        description="Script to track time spent on work processes."
    )

    _parser.add_argument(
        "-s",
        "--save-result",
        action="store_true",
        help="Enable result saving to file (created next to script)",
    )

    _parser.add_argument(
        "-a",
        "--add-processes",
        action="extend",
        nargs="+",
        type=str,
        help="Add process to whitelist, for use-cases where editing script isn't viable.",
    )

    try:
        _args = _parser.parse_args()
        _main(_args.add_processes if _args.add_processes else [], _args.save_result)

    except Exception as err:
        print(err)
        input("\nPress enter to exit:")
        raise
