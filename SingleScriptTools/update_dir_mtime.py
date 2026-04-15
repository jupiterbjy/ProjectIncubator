"""
Script for updating directory's modified time (`mtime`) to match it's content.

Three types of strategy is supported. (oldest, median, newest).

By default, median mode will be used, which choose median mtime of all subdir/files.

Useful when you want to sort by modified date of it's content,
e.g. when you make builds for each commits but still make some modifications to it's config fire.

```text=
some_fw-commit_hash0 - [file_or_dir_count f/d]
└─ 2026-04-15 01:06:40.590192 -> 2026-04-12 01:06:37.782191

some_fw-commit_hash1 - [28 f/d]
└─ 2026-04-07 08:01:50.267985 -> 2026-04-01 08:01:47.463026

some_fw-commit_hash2 - [28 f/d]
└─ 2026-03-31 01:41:14.000000 == 2026-03-31 01:41:14.000000
...
```

:Author: jupiterbjy@gmail.com
"""

import pathlib
import os
import datetime as dt
from argparse import ArgumentParser
from collections.abc import Iterator


ROOT = pathlib.Path(__file__).parent
DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


def _unix_to_date(unix_time: float) -> str:
    """Because this get got darn long"""
    return dt.datetime.fromtimestamp(unix_time, dt.timezone.utc).strftime(DATE_FORMAT)


def dir_list_gen(root: pathlib.Path) -> Iterator[tuple[pathlib.Path, float]]:
    """yields dirs to modify mtime of.
    
    Yields:
        (directory path, directory's current modified time)
    """
    
    for p in root.iterdir():
        if not p.is_dir():
            continue

        yield p, p.stat().st_mtime


def main(target_root: pathlib.Path, mode: str, **_kwargs):
    mode_factor: float = {
        "new": 1,
        "median": 0.5,
        "old": 0,
    }[mode]
    
    for p, p_mtime in dir_list_gen(ROOT):
        
        mtimes: list[float] = [
            sub_p.stat().st_mtime for sub_p in p.glob("**/*")
        ]
        
        print(f"{p.relative_to(ROOT).as_posix()} - [{len(mtimes)} f/d]")
        
        if not mtimes:
            print(f"└─ Nothing to update, skipping\n")
            continue
        
        mtimes.sort()
        new_mtime = mtimes[round(len(mtimes) * mode_factor)]
        symbol = "=="
        
        if p_mtime != new_mtime:
            os.utime(p, (p.stat().st_atime, new_mtime))
            symbol = "->"
        
        print(f"└─ {_unix_to_date(p_mtime)} {symbol} {_unix_to_date(new_mtime)}\n")
        


if __name__ == "__main__":
    _parser = ArgumentParser()
    _parser.add_argument(
        "-t",
        "--target-root",
        type=pathlib.Path,
        default=ROOT,
        help="Root directory of directories to update modified time of"
    )
    _parser.add_argument(
        "-m",
        "--mode",
        type=str,
        default="median",
        choices=["new", "median", "old"],
        help=(
            "Modified time determination method."
            "Should be either one of `n`(newest) `m`(median) `o`(oldest)"
        ),
    )
    _args = _parser.parse_args()
    
    main(**_args.__dict__)
