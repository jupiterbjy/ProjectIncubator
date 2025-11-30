"""
Convert batch files to av1 codec for storage saving. Assumes all passed paths
share common parent directory.

- Usecase 1: Drag-drop videos only, creates `./av1` directory and stores in it.
- Usecase 2: Drag-drop folders only, creates `../DIR_NAME_av1` directory and stores in it. Non-recursive.


Will create new directory named "av1" under the CWD,
since this script is designed to be for batch processing.

Also outputs `results.sqlite` that contains file size & compression ratio.

Requires FFMPEG

:Author: jupiterbjy@gmail.com
"""

import pathlib
import argparse
import subprocess
import sqlite3
from typing import Sequence, Iterable

# --- Config ---

FFMPEG_CMD = 'ffmpeg -i "{}" -c:v libsvtav1 -crf 17 -preset 5 -svtav1-params tune=0 -c:a copy -y "{}"'

# Expecting all lowercase
SUPPORTED_EXTS = {".mp4", ".mkv", ".avi"}

OUT_EXT = ".mp4"

OUT_DIR_NAME = "av1"

OUT_SIZE_DB = "results.sqlite"

TABLE_NAME = "enc_result"

DB_SCHEMA = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    idx INTEGER PRIMARY KEY,
    file_name TEXT,
    src_bytes INTEGER,
    enc_bytes INTEGER,
    ratio REAL
)
"""

INSERT_ROW = f"""
INSERT INTO {TABLE_NAME} VALUES (?, ?, ?, ?, ?)
"""

TOTAL_SRC_BYTES = f"""
SELECT SUM(src_bytes) FROM {TABLE_NAME} WHERE enc_bytes > 0
"""

TOTAL_ENC_BYTES = f"""
SELECT SUM(enc_bytes) FROM {TABLE_NAME} WHERE enc_bytes > 0
"""


# --- Logic ---


def validate_path_type(paths: Sequence[pathlib.Path]) -> bool:
    """Validates if all paths are either file or folder"""

    if not paths:
        return True

    if paths[0].is_dir():
        return all(p.is_dir() for p in paths)

    if paths[0].is_file():
        return all(p.is_file() for p in paths)

    return False


def filter_supported_ext(paths: Iterable[pathlib.Path]) -> list[pathlib.Path]:
    """Filters out paths that don't have supported extension"""

    return [p for p in paths if p.suffix.lower() in SUPPORTED_EXTS]


def bytes_to_human_readable(size: int | float) -> str:
    """Converts bytes to human-readable string"""

    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

    raise ValueError("Received size beyond human understanding")


def show_summary(conn: sqlite3.Connection) -> None:
    """Prints summary of all files in db"""

    print("=== Summary ===")

    src_bytes: int = conn.execute(TOTAL_SRC_BYTES).fetchone()[0]
    enc_bytes: int = conn.execute(TOTAL_ENC_BYTES).fetchone()[0]

    print(f"src bytes: {bytes_to_human_readable(src_bytes)}")
    print(f"enc bytes: {bytes_to_human_readable(enc_bytes)}")
    print(f"ratio    : {enc_bytes * 100 / src_bytes:.2f}%")


def process_batch(cmd, paths: Sequence[pathlib.Path], out_dir: pathlib.Path) -> None:
    """Processes all files in batch"""

    # remove existing db if any, since sqlite doesn't have truncate & no need for vacuum
    db_path = out_dir / OUT_SIZE_DB
    db_path.unlink(missing_ok=True)

    # open db connection & init
    conn = sqlite3.connect(db_path)
    conn.execute(DB_SCHEMA)

    for idx, src_path in enumerate(paths, start=1):
        print(f"=== Encoding {idx} / {len(paths)} ===")

        enc_path = (out_dir / src_path.name).with_suffix(OUT_EXT)

        proc = subprocess.run(
            cmd.format(
                src_path.as_posix(),
                enc_path.as_posix(),
            ),
            shell=True,
        )

        src_size: int = src_path.stat().st_size
        enc_size: int = 0
        ratio: float = 0.0

        if proc.returncode == 0:
            enc_size = enc_path.stat().st_size
            ratio = enc_size / src_size
            print(f"=== Done ({ratio * 100.0:.2f}%) ===")

        else:
            print(f"=== Failed (code: {proc.returncode}) ===")

        conn.execute(
            INSERT_ROW,
            (
                idx,
                src_path.name,
                src_size,
                enc_size,
                ratio,
            ),
        )

    conn.commit()

    show_summary(conn)
    conn.close()


def main(paths: Sequence[pathlib.Path], overwrite: bool):

    if not validate_path_type(paths):
        raise ValueError("All paths must be either file or folder")

    cmd = FFMPEG_CMD if overwrite else FFMPEG_CMD.replace("-y", "-n")

    if paths[0].is_file():
        print("=== Using batch file mode ===")

        process_batch(
            cmd, filter_supported_ext(paths), (paths[0].parent / OUT_DIR_NAME)
        )

    else:
        print("=== Using batch directory mode ===")

        for p in paths:
            process_batch(
                cmd,
                filter_supported_ext(p.iterdir()),
                p.with_name(f"{p.name}_{OUT_DIR_NAME}"),
            )


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

    _parser.add_argument(
        "-o", "--overwrite", action="store_true", help="Overwrite existing files"
    )

    try:
        _args = _parser.parse_args()
        main(_args.video, _args.overwrite)
        input("Press any key to exit:")

    except Exception as _err:
        import traceback

        traceback.print_exc()
        input("Press any key to exit:")
        raise
