"""
Counts number of lines and characters in predetermined file types & encodings.

```text
Checking files under /home/...
Whitelisted encodings: utf-8 utf-8-sig cp949 big5
.bat     | lines:      67 | characters:     2658 | files: 3
.cpp     | lines:      89 | characters:     3578 | files: 1
.hpp     | lines:   72734 | characters:  2215146 | files: 486
.h       | lines: 1294296 | characters: 48226107 | files: 4314
.sh      | lines:    9215 | characters:   367937 | files: 48
.md      | lines:    1829 | characters:    96983 | files: 15
.c       | lines: 1450257 | characters: 65720511 | files: 1901
.txt     | lines:   22743 | characters:  1507211 | files: 260
.mk      | lines:   65149 | characters:  3020539 | files: 285
.py      | lines:   19463 | characters:   734760 | files: 113
Total 2935842 lines, 121895430 characters from 7426 files
Press enter to exit: 
```

:Author: jupiterbjy@gmail.com
"""

import pathlib
import sys
from collections.abc import Sequence
from argparse import ArgumentParser


# --- Config ---

ROOT = pathlib.Path(__file__).parent

# Whitelisted extensions to look for
# I just groupped for PEP8 without excessive line breaks
EXTENSIONS = {
    # shell scripts
    *(".sh", ".bat", ".ps1"),

    # text-ish stuffs
    *(".txt", ".md"),

    # c derivatives or remotely related
    *(".cpp", ".c", ".hpp", ".h", ".mk"),

    # etc
    *(".py", ".gd"),
}

ENCODING_CANDIDATES = [
    "utf-8",
    "utf-8-sig",
    "cp949",
    "big5",  # some chip vender's SDK uses it...
]
if sys.getdefaultencoding() not in ENCODING_CANDIDATES:
    ENCODING_CANDIDATES.append(sys.getdefaultencoding())
# ^^^ wish I could just use set but I want it sorted


# --- Util ---


class NoMatchingEncodingError(Exception):
    pass


def read_text_retry(path, encodings: Sequence[str]) -> str:
    """
    Retry opening file with given encodings.

    Raises:
        UnicodeDecodeError - if all encodings fail
    """

    for candidate in encodings:
        try:
            return path.read_text(candidate)

        except UnicodeDecodeError:
            continue

    raise NoMatchingEncodingError


# --- Logic ---


def recursive_search(new_root: pathlib.Path, suffix=""):
    lines = 0
    texts = 0
    files = 0

    for path in new_root.iterdir():
        if path.is_dir():
            sub_lines, sub_texts, sub_files = recursive_search(path, suffix)

            lines += sub_lines
            texts += sub_texts
            files += sub_files

            continue

        if not suffix or path.suffix != suffix:
            continue

        files += 1

        try:
            data = path.read_text("utf8")

        except UnicodeDecodeError:
            try:
                data = read_text_retry(path, ENCODING_CANDIDATES)

            except NoMatchingEncodingError:
                print(f"Can't read file {path.as_posix()} - No matching encoding")
                continue

            except Exception as err:
                print(f"Can't read file {path.as_posix()} - {type(err).__name__} {err}")
                continue

        lines += len(data.splitlines())
        texts += len(data)

    return lines, texts, files


def main(path: pathlib.Path, **_kwargs):

    root = path

    total_lines = 0
    total_texts = 0
    total_files = 0
    
    print("Checking files under", root.as_posix())
    print("Whitelisted encodings:", *ENCODING_CANDIDATES)

    for _extension in EXTENSIONS:
        lines, texts, files = recursive_search(root, _extension)

        # if 0 files pass
        if files == 0:
            continue

        total_lines += lines
        total_texts += texts
        total_files += files

        print(
            f"{_extension:8} | lines: {lines:7} | characters: {texts:8} | files: {files}"
        )

    print(f"Total {total_lines} lines, {total_texts} characters from {total_files} files")
    input("Press enter to exit: ")


if __name__ == "__main__":
    _parser = ArgumentParser()
    _parser.add_argument(
        "path",
        nargs="?",
        type=pathlib.Path,
        default=ROOT,
        help="Root path to recursively start counting from",
    )

    main(**vars(_parser.parse_args()))
