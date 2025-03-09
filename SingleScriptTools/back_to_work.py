"""
Simple script to track focused window and measure total time
whenever there's input with configurable margin, windows only.

`pip install win32gui, win32process, psutil, pynput`

:Author: jupiterbjy@gmail.com
"""

import re
import time
import traceback
import functools

import win32gui
import win32process
import psutil
import pynput


# --- Constants ---

TIMEOUT_SEC = 30

PRINT_INTERVAL_SEC = 1

# List of process names to consider as "work" - this is just an example.
# Will ignore all parts since underscore or hyphen of process's name, all lowercased.
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
    "notepad++",
    "obs",
    "pycharm64",
}

# used for formatting
_MAX_PROC_NAME_LEN = max(len(proc_name) for proc_name in WORK_PROCESS_WHITELIST)


RE_PATTERN = re.compile(r"[^\W\-.]+")


# --- Utilities ---


def _get_active_window_process_name() -> str:
    """Get currently focused window's process name.
    Returns empty string if unable to get process name.

    References:
        https://stackoverflow.com/a/65363087/10909029

    Returns:
        Process's Name. Raises
    """

    # noinspection PyBroadException
    try:
        pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
        return psutil.Process(pid[-1]).name()

    except Exception as _:
        # not exactly sure what's raising what yet, so log trace and pass for now
        # will update with appropriate error info or handling once identified
        traceback.print_exc()

    return ""


def _normalize_process_name(raw_proc_name: str) -> str:
    """Normalizes process name. Returns empty string if it's unable to be normalized."""

    matched = RE_PATTERN.match(raw_proc_name)
    normalized_name = matched.group(0).lower() if matched else ""

    return normalized_name


# def flush_log(log_file: pathlib.Path, logs: list[tuple[str, float, float]]):
#     """Flush logs to file.
#
#     Args:
#         log_file (pathlib.Path): Path to log file.
#         logs (list[tuple[str, float, float]]): List of logs to be flushed. Each log is a tuple of
#             process name, duration and total time.
#     """
#
#     with log_file.open("a", encoding=LOG_ENCODING) as fp:
#         for proc_n, duration, total_t in logs:
#             fp.write(f"{proc_n},{duration:.2f},{total_t:.2f}\n")


def _clear_screen(newlines=100):
    """Just pushes a bunch of newlines to mimic screen clear."""

    print("\n" * newlines)


# --- Logics ---


class Tracker:
    """Tracks work time with non-busy method."""

    def __init__(self):

        # per process's accumulated time
        self._per_proc_accumulations: dict[str, float] = {}

        # total accumulated time
        self._total_accumulated_sec = 0.0

        # started time
        self._start_time = time.time()

        # last process name
        self._last_proc_name = ""

        # last input time
        self._last_input_time = 0.0

    def print_stats(self):
        """Prints total accumulated time and per process's accumulated time."""

        _clear_screen()

        print(f"Elapsed: {time.time() - self._start_time:.2f}s")
        print(f"Total Accumulated: {self._total_accumulated_sec:.2f}s")

        print("\nPer Process Accumulated:")
        for proc_name, accumulated_sec in self._per_proc_accumulations.items():
            print(f"{proc_name:{_MAX_PROC_NAME_LEN}}: {accumulated_sec:10.2f}s")

    def tick(self):
        """Updates per process's accumulated time and total accumulated time.
        Call this on every new input events."""

        cur_time = time.time()

        # fetch process name
        proc_name = _normalize_process_name(_get_active_window_process_name())

        # check if last process was valid, if so accumulate
        if self._last_proc_name in WORK_PROCESS_WHITELIST:
            duration = min(cur_time - self._last_input_time, TIMEOUT_SEC)
            self._total_accumulated_sec += duration

            try:
                self._per_proc_accumulations[self._last_proc_name] += duration
            except KeyError:
                self._per_proc_accumulations[self._last_proc_name] = duration

        self._last_proc_name = proc_name
        self._last_input_time = cur_time


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


def _on_key_press(tracker: Tracker, _key):
    tracker.tick()


def _on_key_release(tracker: Tracker, _key):
    tracker.tick()


def _main():

    tracker = Tracker()

    mouse_listener = pynput.mouse.Listener(
        on_move=functools.partial(_on_mouse_move, tracker),
        on_scroll=functools.partial(_on_mouse_scroll, tracker),
        on_click=functools.partial(_on_mouse_click, tracker),
    )

    keyboard_listener = pynput.keyboard.Listener(
        on_press=functools.partial(_on_key_press, tracker),
        on_release=functools.partial(_on_key_release, tracker),
    )

    with mouse_listener, keyboard_listener:

        # just a dumb ctrl+c catcher for windows. with occasional logging
        try:
            while True:
                tracker.print_stats()
                time.sleep(PRINT_INTERVAL_SEC)
        except KeyboardInterrupt:
            pass

    input("\nPress enter to exit:")


if __name__ == "__main__":
    print("Started scanning for following processes:")

    for _proc_name in WORK_PROCESS_WHITELIST:
        print(f" - {_proc_name}")

    print(f"\nWith timeout of {TIMEOUT_SEC} sec.")
    print(f"Status is logged only on every {PRINT_INTERVAL_SEC} sec.")

    input("\nPress enter to start:")

    _main()
