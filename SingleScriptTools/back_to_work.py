"""
Simple script to track focused window and measure total time
whenever there's input with configurable margin, windows only.

`pip install win32gui, win32process, psutil, pynput`

:Author: jupiterbjy@gmail.com
"""

import re
import time
import traceback

import win32gui
import win32process
import psutil
import pynput


# --- Constants ---

TIMEOUT_SEC = 30

PRINT_INTERVAL_SEC = 1.0

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


def _is_process_valid(proc_name: str) -> bool:
    """Checks whether given process name is whitelisted as work or not."""

    matched = RE_PATTERN.match(proc_name)
    normalized_name = matched.group(0).lower() if matched else proc_name

    return normalized_name in WORK_PROCESS_WHITELIST


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


# --- Logics ---


def _main_loop_coro():

    accumulated_sec = 0.0

    last_proc_name = ""
    last_input_time = 0.0

    last_print_time = 0.0

    should_continue = True

    while should_continue:
        should_continue = yield

        cur_time = time.time()

        # fetch process name
        proc_name = _get_active_window_process_name()

        # check if last process was valid, if so accumulate
        if _is_process_valid(last_proc_name):
            duration = min(cur_time - last_input_time, TIMEOUT_SEC)
            accumulated_sec += duration

            # print if interval is met
            if cur_time - last_print_time > PRINT_INTERVAL_SEC:
                print(
                    f"{proc_name}: Accumulated {duration:.2f} sec. total {accumulated_sec:.2f}"
                )
                last_print_time = cur_time

        last_proc_name = proc_name
        last_input_time = cur_time

    print("Exit requested!")


_LOOP = _main_loop_coro()


# --- Drivers ---


def _on_mouse_move(_x: int, _y: int):
    _LOOP.send(True)


def _on_mouse_scroll(_x: int, _y: int, _dx: int, _dy: int):
    _LOOP.send(True)


def _on_mouse_click(_x: int, _y: int, _button: pynput.mouse.Button, _pressed: bool):
    _LOOP.send(True)


def _on_key_press(_key):
    # set your own specific key here for sending false so it can stop
    _LOOP.send(True)


def _on_key_release(_key):
    _LOOP.send(True)


def main():
    mouse_listener = pynput.mouse.Listener(
        on_move=_on_mouse_move,
        on_scroll=_on_mouse_scroll,
        on_click=_on_mouse_click,
    )

    keyboard_listener = pynput.keyboard.Listener(
        on_press=_on_key_press,
        on_release=_on_key_release,
    )

    # with mouse_listener, keyboard_listener:
    #     mouse_listener.join()
    #     keyboard_listener.join()

    mouse_listener.start()
    keyboard_listener.start()

    try:
        while True:
            time.sleep(1000000)
    except KeyboardInterrupt:
        pass

    mouse_listener.stop()
    keyboard_listener.stop()

    mouse_listener.join()
    keyboard_listener.join()

    input("\nPress enter to exit.")


if __name__ == "__main__":
    print("Press Ctrl+C here to exit.\n")
    next(_LOOP)
    main()
