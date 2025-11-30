"""
Batch validates video files using ffmpeg - which just actually is decoding and looking for errors.

Requires FFMPEG

:Author: jupiterbjy@gmail.com
"""

import pathlib
import argparse
import subprocess
import sqlite3
from typing import Sequence, Iterable


# --- Config ---

FFMPEG_CMD = 'ffmpeg -v error -i "{}" -f null -'

# Expecting all lowercase
SUPPORTED_EXTS = {".mp4", ".mkv", ".avi"}


# --- Logic ---


def filter_supported_ext(paths: Iterable[pathlib.Path]) -> list[pathlib.Path]:
    """Filters out paths that don't have supported extension"""

    return [p for p in paths if p.suffix.lower() in SUPPORTED_EXTS]


def main(paths: Sequence[pathlib.Path]):

    files: list[pathlib.Path] = []
    for p in paths:
        files.extend(filter_supported_ext(p.iterdir()))

    for idx, file in enumerate(files, start=1):

        print(f"\n\n=== Validating {idx} / {len(files)} ===")

        print(f"File: '{file.as_posix()}'")
        subprocess.run(FFMPEG_CMD.format(file.as_posix()), shell=True)


if __name__ == "__main__":
    _parser = argparse.ArgumentParser(
        description="Convert batch files to av1 codec for storage saving."
    )

    _parser.add_argument(
        "video",
        metavar="VID",
        type=pathlib.Path,
        nargs="+",
        help="Video files to convert. Must be either all files or all folders.",
    )

    try:
        _args = _parser.parse_args()
        main(_args.video)
        input("Press any key to exit:")

    except Exception as _err:
        import traceback

        traceback.print_exc()
        input("Press any key to exit:")
        raise
