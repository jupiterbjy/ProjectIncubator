"""
WARING - Experimental script. Make sure to archive your project.

Simple script to automatically follow & replace `res://` path to
`uid://` introduced in godot 4.4 dev5.

Assuming utf8 encoding as every sane people should do.

Also ignores addon directory.

:Author: jupiterbjy@gmail.com
"""

import pathlib
import re
from argparse import ArgumentParser


# --- Config ---

PATTERN = re.compile(r'(res://[^"]*)')


# --- Utilities ---


class ANSI:
    """Some colorful ANSI printer"""

    _table = {
        "RED": "\x1b[31m",
        "GREEN": "\x1b[32m",
        "YELLOW": "\x1b[33m",
        "": "",
    }
    _end = "\x1b[0m"

    @classmethod
    def print(cls, *args, color="", sep=" ", **kwargs):
        """Colored print"""

        print(f"{cls._table[color]}{sep.join(args)}{cls._end}", **kwargs)


def dir_recursive_iter_gen(path: pathlib.Path, ext_whitelist=(".gd",)):
    """
    recursively iterate all subdir within given path for which matchs ext in ext_whitelist.
    """

    if path.is_file():
        if path.suffix == ".svg":
            pass

        if path.suffix in ext_whitelist:
            yield path

        return

    # otherwise dir
    for subdir in path.iterdir():
        yield from dir_recursive_iter_gen(subdir, ext_whitelist)


def fetch_uid(project_root: pathlib.Path, res_path: str) -> str:
    """Read corresponding *.uid file for resource path and return it's uid.

    Raises:
        FileNotFoundError: if corresponding uid file is not found.
    """

    path = project_root / (res_path.removeprefix("res://") + ".uid")
    return path.read_text("utf-8")


def replace_to_uid(project_root: pathlib.Path, script_path: pathlib.Path):
    """
    Replaces all occurrences of line with "res://some/path" to their respective UID.
    Make sure all have their .uid file generated, as this will use res:// path to find uid.

    Uses line split and do regex per line to reduce calc in case of long code.
    """

    lines = script_path.read_text("utf-8").splitlines()
    hit = False

    for idx, line in enumerate(lines):
        # ignore comments
        if line.lstrip().startswith("#"):
            continue

        # if it doesn't have res skip
        matched = PATTERN.search(line)
        if not matched:
            continue

        # replace line
        try:
            lines[idx] = line.replace(matched[0], fetch_uid(project_root, matched[0]))
        except FileNotFoundError:
            print(
                f"{script_path.relative_to(project_root)}:{idx + 1}:"
                f" No corresponding uid file found for {matched[0]}"
            )
            continue

        print(f"{script_path.relative_to(project_root)}:{idx + 1}")
        ANSI.print("-", line, color="RED")
        ANSI.print("+", lines[idx], color="GREEN")
        print()

    # write back
    if hit:
        script_path.write_text("\n".join(lines), encoding="utf-8")


# --- Driver ---


def main(project_root: pathlib.Path):

    dir_blacklist = {
        path.absolute().as_posix()
        for path in (
            project_root / "addons",
            project_root / "Addons",
        )
    }

    for path in dir_recursive_iter_gen(project_root):

        # check if it's addon
        for blacklisted in dir_blacklist:
            if path.absolute().as_posix().startswith(blacklisted):
                continue

        replace_to_uid(project_root, path)


if __name__ == "__main__":
    _parser = ArgumentParser(
        description="Script to replace given project's res:// path to uid://."
    )
    _parser.add_argument("project_path", type=pathlib.Path)

    try:
        main(_parser.parse_args().project_path)

    except Exception:
        import traceback

        traceback.print_exc()
        input("\nPress enter to exit:")
        raise

    input("\nPress enter to exit:")
