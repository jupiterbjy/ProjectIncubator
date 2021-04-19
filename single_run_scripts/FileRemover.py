"""
I am having all handbrake encoded mp4 causing dllhost(COM Surrogate) go wild,
preventing use of explorer. This simple hardcoded script would do for me.
"""

import pathlib
import time


TARGET_SUBDIR = "Encoding"


def main():
    current_dir = pathlib.Path(".").absolute()
    target_dir = current_dir.joinpath(TARGET_SUBDIR)

    for mp4_file in (file for file in target_dir.iterdir() if file.suffix in (".mp4", ".m4v")):
        print(f"Removing {mp4_file.as_posix()}")
        mp4_file.unlink()


main()
time.sleep(3)
