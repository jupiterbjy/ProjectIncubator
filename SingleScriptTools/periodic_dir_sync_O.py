"""
Syncs two independent directories periodically, with file extension whitelist.

Used to sync dependant resources real time while writing my own static webpage builder for github.io page.

![](readme_res/periodic_dir_sync.jpg)

:Auther: jupiterbjy@gmail.com
"""

from argparse import ArgumentParser
import pathlib
import time


# --- Utilities ---

CHANGES_FORMAT = "f+ {} / f- {} / d+ {} / d- {}"


def print_changes(change_tuple: tuple[int, int, int, int]):
    print(CHANGES_FORMAT.format(*change_tuple))


# --- Logics ---


def sync_dir(
    src_root: pathlib.Path, dest_root: pathlib.Path, src_excl: set[str] = None
) -> tuple[int, int, int, int]:
    """Syncs all files from src to dest excluding file extensions in excluded_exts.

    Args:
        src_root: Source's root dir
        dest_root: Destination's root dir
        src_excl: Excluded files from source's root dir

    Returns:
        (created file count, deleted file count, created dir count, deleted dir count)
    """

    # since we can't really use watchdog.utils.dirsnapshot due to diff dir we go manual
    src_excl = src_excl or set()

    all_dest_paths = set(p.relative_to(dest_root) for p in dest_root.rglob("*"))
    all_src_paths = set(
        p.relative_to(src_root) for p in src_root.rglob("*") if p.suffix not in src_excl
    )

    dangling_dest_paths = {p for p in (all_dest_paths - all_src_paths)}

    # delete extra paths
    f_deletes = 0
    d_deletes = 0

    for root, dir_names, file_names in dest_root.walk(top_down=False):

        for fn in file_names:
            path = root / fn
            if path.relative_to(dest_root) not in dangling_dest_paths:
                continue

            f_deletes += 1
            (root / fn).unlink()

        for dn in dir_names:
            path = root / dn
            if path.relative_to(dest_root) not in dangling_dest_paths:
                continue

            d_deletes += 1
            (root / dn).rmdir()

    # copy new paths if missing or different with mtime
    f_creates = 0
    d_creates = 0

    for root, dir_names, file_names in src_root.walk():

        for fn in file_names:

            src_path = root / fn

            if src_path.suffix in src_excl:
                continue

            dest_path = dest_root / src_path.relative_to(src_root)

            dest_mtime = dest_path.stat().st_mtime if dest_path.exists() else 0

            if src_path.stat().st_mtime > dest_mtime:
                src_path.copy(dest_path, preserve_metadata=True)
                # don't need this param in windows but still

                f_creates += 1

        for dn in dir_names:
            src_path = root / dn
            dest_path = dest_root / src_path.relative_to(src_root)

            if not dest_path.exists():
                dest_path.mkdir(exist_ok=True)
                d_creates += 1

    return f_creates, f_deletes, d_creates, d_deletes


# --- Drivers ---


def periodic_sync(src_root: pathlib.Path, dest_root: pathlib.Path, interval: float):
    while True:
        changes = sync_dir(src_root, dest_root)

        if sum(changes) > 0:
            print(f"{time.time():.1f}: ", end="")
            print_changes(changes)

        time.sleep(interval)


if __name__ == "__main__":
    _parser = ArgumentParser()
    _parser.add_argument(
        "src_root",
        type=pathlib.Path,
        help="Path to the source directory",
    )
    _parser.add_argument(
        "dest_root",
        type=pathlib.Path,
        help="Path to the destination directory",
    )
    _parser.add_argument(
        "-t",
        "--time-interval",
        type=float,
        default=1,
        help="Time interval in seconds between syncs",
    )

    _args = _parser.parse_args()

    try:
        periodic_sync(_args.src_root, _args.dest_root, _args.time_interval)
    except KeyboardInterrupt:
        pass
