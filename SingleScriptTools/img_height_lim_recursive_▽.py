"""
Simply resizes images to identical height. Intended for static, non-indexed color images (png & jpg mostly).

This will create new directory with configured suffix, for all passed directories recursively.

Also, if files already exist in destination, `st_mtime` will be used to decide whether to overwrite or not,
so that you don't have to re-process every file.

Script will by default try to maintain `st_mtime` so you can order by modification time.
(more like I need it, since I mix parsec & apollo for streaming)

This is designed to be used in networked drive with high IO latency (which is what I have)
so this uses multiple threads.

Would've preferred using `trio.Path` for async file operation, but it still delegates to thread internally.
So result would be similar regardless.

`pip install pillow`

```text
Target height in pixels: 800

# Delete pass for F:\_Backups\NyaruTab
NyaruTab\DCIM\Game media\Artemis - deletes 433

# Write pass for F:\_Backups\NyaruTab
NyaruTab\DCIM\9나인 소라 배드엔딩 - writes 0 / skipped 3055
NyaruTab\DCIM\9나인 노아 배드엔딩 - writes 0 / skipped 2658
NyaruTab\DCIM\벚꽃, 싹트다 쿠로 - writes 0 / skipped 6945
NyaruTab\DCIM\벚꽃, 싹트다 하루 - writes 0 / skipped 4720
NyaruTab\DCIM\와가하이 아샤 - writes 0 / skipped 2577
NyaruTab\DCIM\와가하이 토아 - writes 0 / skipped 1763
NyaruTab\DCIM\코노소라 공통 - writes 0 / skipped 3477
NyaruTab\DCIM\코노소라 코토리 - writes 0 / skipped 1944
NyaruTab\DCIM\형형색색의 세계 공통 - writes 0 / skipped 3015
NyaruTab\DCIM\형형색색의 세계 신쿠 - writes 0 / skipped 3156
NyaruTab\DCIM\호시메모 공통 - writes 0 / skipped 4224
NyaruTab\DCIM\호시메모 코모모 - writes 0 / skipped 2044
...
NyaruTab\DCIM\Game media\Artemis - writes 709 / skipped 0

Total - deletes 433 / writes 997 / skipped 213583
Press enter to exit:
```

<sub>~~I might have too many screenshots~~</sub>

:Author: jupiterbjy@gmail.com
"""

import pathlib
import argparse
import os
from collections.abc import Sequence, Generator
from concurrent.futures import ThreadPoolExecutor

from PIL import Image


# --- Config ---

SUFFIX = "_v{}"

EXT_WHITELIST = {".png", ".jpg", ".jpeg"}

# since it's mostly IO task...
THREAD_COUNT = 8

# Default delete mode. This changes argument's default behavior.
# Useful when using this script via drag & drop.
DELETE_MODE_DEFAULT = True

# Extensions that doesnt have alpha channel.
# For minor optimization
# NON_ALPHA_EXT = {".jpeg", ".jpg"}


# --- Logics ---


def lim_img(src_path: pathlib.Path, dest_path: pathlib.Path, v_pixels: int):
    """Limits src_path's image height to designated pixels & save to dest_path."""

    src = Image.open(src_path)

    # if src_path.suffix.lower() not in NON_ALPHA_EXT and src.mode == "RGBA":
    #     is_trans = not src.getextrema()[-1] == (255, 255)
    #     if not is_trans:
    #         src = src.convert("RGB")

    ratio = v_pixels / src.height

    resized = src.resize((round(src.width * ratio), v_pixels))

    # save & update mtime
    resized.save(dest_path)
    os.utime(dest_path, (src_path.stat().st_atime, src_path.stat().st_mtime))


def task(params: tuple[pathlib.Path, pathlib.Path, int]) -> bool:
    """ThreadPool task func, returns True if file was written."""

    src_path: pathlib.Path
    dest_path: pathlib.Path
    tgt_height: int

    src_path, dest_path, tgt_height = params

    # skip if matching mtime
    if dest_path.exists() and dest_path.stat().st_mtime == src_path.stat().st_mtime:
        return False
    else:
        lim_img(src_path, dest_path, tgt_height)
        return True


def delete_pass(src_root: pathlib.Path, dest_root: pathlib.Path) -> int:
    """Deletion pass of process

    Args:
        src_root: Source root dir
        dest_root: Destination root dir

    Returns:
        File deletion count
    """

    print("\n# Delete pass for", src_root)

    total_deletes = 0

    for (
        dest_dir,
        dir_names,
        file_names,
    ) in dest_root.walk(top_down=False):
        src_dir = src_root / dest_dir.relative_to(dest_root)

        deletes = 0

        prefix = f"{src_dir.relative_to(src_root.parent)}"

        for fn in file_names:
            src_path = src_dir / fn

            if not src_path.exists():
                (dest_dir / fn).unlink()
                deletes += 1
                print(f"{prefix} - deletes {deletes}", end="\r")

        for dn in dir_names:
            src_path = src_dir / dn

            if not src_path.exists():
                (dest_dir / dn).rmdir()
                deletes += 1
                print(f"{prefix} - deletes {deletes}", end="\r")

        # only insert newline when there were any meaningful files
        if deletes:
            print()

        total_deletes += deletes

    return total_deletes


def write_pass(
    src_root: pathlib.Path, dest_root: pathlib.Path, tgt_height: int
) -> tuple[int, int]:
    """Writing pass of process

    Args:
        src_root: Source root dir
        dest_root: Destination root dir
        tgt_height: Target height in pixel

    Returns:
        (writes_count, skipped_count)
    """

    print("\n# Write pass for", src_root)

    total_writes = 0
    total_skipped = 0

    for src_dir in src_root.rglob(""):
        dest_dir = dest_root / src_dir.relative_to(src_root)
        dest_dir.mkdir(exist_ok=True)

        prefix = f"{src_dir.relative_to(src_root.parent)}"

        writes = 0
        skipped = 0

        def workload_gen() -> (
            Generator[tuple[pathlib.Path, pathlib.Path, int], None, None]
        ):
            for src_path in src_dir.iterdir():
                if src_path.suffix.lower() not in EXT_WHITELIST:
                    continue

                yield src_path, dest_dir / src_path.name, tgt_height

        with ThreadPoolExecutor(THREAD_COUNT) as executor:
            for is_written in executor.map(task, workload_gen()):
                if is_written:
                    writes += 1
                else:
                    skipped += 1

                # since wide character messes things up, better rewrite entire line
                print(f"{prefix} - writes {writes} / skipped {skipped}", end="\r")

        # only insert newline when there were any meaningful files
        if any((writes, skipped)):
            print()

        total_writes += writes
        total_skipped += skipped

    return total_writes, total_skipped


def main(tgt_height: int, paths: Sequence[pathlib.Path], delete: bool):

    total_writes = 0
    total_skipped = 0
    total_deletes = 0

    for src_root in paths:

        if src_root.is_file():
            print("Ignoring file", src_root)
            return

        dest_root = src_root.with_name(src_root.name + SUFFIX.format(tgt_height))
        dest_root.mkdir(exist_ok=True)

        deletes = delete_pass(src_root, dest_root)
        writes, skipped = write_pass(src_root, dest_root, tgt_height)

        total_writes += writes
        total_skipped += skipped
        total_deletes += deletes

    print(
        f"\nTotal - deletes {total_deletes} / writes {total_writes} / skipped {total_skipped}"
    )


if __name__ == "__main__":
    _parser = argparse.ArgumentParser("Limits image height")

    _parser.add_argument(
        "-p",
        "--pixels",
        type=int,
        default=0,
        help="Target height in pixels. If not specified, will prompt for input",
    )

    _parser.add_argument(
        "-t" "--threads",
        type=int,
        default=THREAD_COUNT,
        help="Number of threads to use",
    )

    _parser.add_argument(
        "paths",
        type=pathlib.Path,
        nargs="+",
        help="Directories to process",
    )

    _parser.add_argument(
        "-d",
        "--delete",
        action="store_true" if DELETE_MODE_DEFAULT else "store_false",
        help="Deletes files & directories nonexistent in source",
    )

    _args = _parser.parse_args()
    if _args.pixels < 1:
        _args.pixels = int(input("Target height in pixels: "))

    try:
        main(_args.pixels, _args.paths, _args.delete)

    except Exception:
        import traceback

        traceback.print_exc()
        input("Press enter to exit:")

        raise

    input("Press enter to exit:")
