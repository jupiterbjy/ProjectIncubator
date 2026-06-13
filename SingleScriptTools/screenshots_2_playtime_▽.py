"""
Dumb script to estimate playtime from screenshots.

<sup>(also first fully nvim written one among these, excl. npp)</sup>

Expects `PREFIXyyyy-mm-dd-hh-mm-ssSUFFIX` format images,
and support mixed file names as long as dates are ordered.

e.g.:
```
❯ foreach ($dir in ls -Directory *세계*) { py ./screenshots_2_playtime_▽.py $dir.name }
Session info for '형형색색의 세계 공통' w/ 300 sec max gap
- Session 0 2025-05-26 02:59:18 - 0.00 hr / 1 screenshots
- Session 1 2025-05-26 03:14:24 - 0.16 hr / 12 screenshots
- Session 2 2025-05-26 03:37:45 - 3.66 hr / 513 screenshots
- Session 3 2025-05-26 19:36:07 - 0.07 hr / 7 screenshots
- Session 4 2025-05-26 20:01:07 - 3.23 hr / 671 screenshots
- Session 5 2025-05-27 00:17:21 - 4.31 hr / 808 screenshots
- Session 6 2025-05-29 04:53:05 - 3.53 hr / 972 screenshots
- Session 7 2025-06-01 11:59:23 - 0.15 hr / 16 screenshots
- Session 8 2025-08-21 20:05:47 - 0.00 hr / 2 screenshots
Total 15.10 hr / 3002 screenshots

Session info for '형형색색의 세계 미오' w/ 300 sec max gap
- Session 0 2025-05-29 08:25:15 - 0.00 hr / 1 screenshots
- Session 1 2025-05-30 02:06:03 - 3.79 hr / 915 screenshots
- Session 2 2025-05-30 06:18:29 - 0.23 hr / 43 screenshots
- Session 3 2025-06-01 08:33:02 - 0.55 hr / 103 screenshots
- Session 4 2025-06-01 09:25:29 - 2.26 hr / 533 screenshots
Total 6.83 hr / 1595 screenshots

Session info for '형형색색의 세계 신쿠' w/ 300 sec max gap
- Session 0 2025-06-03 00:20:33 - 9.51 hr / 2534 screenshots
- Session 1 2025-06-03 17:37:19 - 1.59 hr / 481 screenshots
- Session 2 2025-06-03 19:25:50 - 0.41 hr / 102 screenshots
- Session 3 2025-07-15 11:06:09 - 0.00 hr / 2 screenshots
- Session 4 2025-08-21 20:05:02 - 0.07 hr / 33 screenshots
Total 11.58 hr / 3152 screenshots

...
```

:Author: jupiterbjy@gmail.com
"""

import pathlib
import re
import datetime as dt
import bisect
from argparse import ArgumentParser


# --- Config ---

# Minimum interval between screenshot to determine idle state
IDLE_MIN_SEC: float = 60 * 5

# Image extension filter
IMG_EXTS: set[str] = {
    ".png", ".jpg",
}

# date extraction pattern
DATE_PATTERN = re.compile(
    r".*_(\d\d\d\d-\d\d-\d\d-\d\d-\d\d-\d\d).*"
)

"""
just memo

Parsec_2024-09-13-18-19-42.jpg
Artemis_2026-05-12-01-53-20.jpg
"""


# --- Utils ---

def extract_date(raw: str) -> dt.datetime:
    """extract date via regex

    Raises:
        AttributeError: if matching failed
        TypeError: if matching failed
    """

    return dt.datetime(
        *map(int, DATE_PATTERN.match(raw).group(1).split("-"))
    )

    
def fetch_time_ordered_path(root_path: pathlib.Path) -> list[pathlib.Path]:
    """Fetch screenshot files in dir and sort in ascending order.
    """

    date_file_pairs: list[tuple[dt.datetime, pathlib.Path]] = []

    for p in root_path.iterdir():
        if p.suffix not in IMG_EXTS:
            continue

        try:
            bisect.insort(
                date_file_pairs,
                (extract_date(p.stem), p),
                key=lambda x: x[0],
            )
        except (TypeError, AttributeError):
            pass

    return date_file_pairs


# --- Logics ---

def main(root_path: pathlib.Path, min_combo_sec: int):

    dt_path_pairs = fetch_time_ordered_path(root_path)
    if not dt_path_pairs:
        print("Empty directory, nothing to do")
        return
    
    session_times: list[float] = [0.0]
    session_sc_count: list[int] = [0]
    session_start: list[dt.datetime] = [dt_path_pairs[0][0]]

    last_dt: dt.datetime = session_start[-1]

    for idx, (date, p) in enumerate(fetch_time_ordered_path(root_path)):
        diff = (date - last_dt).total_seconds()
        
        # accumulate session if time gap isn't wide
        if diff < min_combo_sec:
            session_times[-1] += diff
            session_sc_count[-1] += 1
            last_dt = date
            continue
        
        # otherwise new session starts
        try:
            session_start.append(dt_path_pairs[idx + 1][0])
        except IndexError:
            break

        session_times.append(0.0)
        session_sc_count.append(0)
        last_dt = session_start[-1]

    # would be better printing while accumulating but I might reuse above later
    session_digits = len(str(len(session_times)))
    
    total_duration = 0.0
    total_sc_count = 0
    
    print(f"Session info for '{root_path.name}' w/ {min_combo_sec} sec max gap")

    for idx, (duration, sc_count, start_dt) in enumerate(zip(session_times, session_sc_count, session_start)):
        total_duration += duration
        total_sc_count += sc_count

        print(f"- Session {idx:0{session_digits}} {start_dt} - {duration / 3600:.2f} hr / {sc_count} screenshots")

    print(f"Total {total_duration / 3600:.2f} hr / {total_sc_count} screenshots\n")


# --- Drivers ---

if __name__ == "__main__":
    _parser = ArgumentParser()
    _parser.add_argument(
        "path",
        type=pathlib.Path,
        help="path to get session info of"
    )
    _parser.add_argument(
        "--max-gap",
        type=int,
        default=IDLE_MIN_SEC,
        help="interval between screenshot date to distinguish sessions"
    )

    _args = _parser.parse_args()

    main(_args.path, _args.max_gap)

