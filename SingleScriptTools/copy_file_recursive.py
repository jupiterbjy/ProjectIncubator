"""
Fetch all files with matching extension to script's location/Copied. Recursive.

:Author: jupiterbjy@gmail.com
"""

import shutil
import pathlib
from typing import Generator


ROOT = pathlib.Path(__file__).parent
TARGET = ROOT / "Copied"
TARGET.mkdir(exist_ok=True)

SUFFIX = input("Target Extension(If none exits): ")

if not SUFFIX:
    # if empty exit
    exit()

elif not SUFFIX[0] == ".":
    # check if dot is omitted
    SUFFIX = "." + SUFFIX


def check_file_gen(path: pathlib.Path, suffix) -> Generator[pathlib.Path, None, None]:
    """yield file path with given suffix(Including leading period, like .txt)"""

    print(f"In {path.relative_to(ROOT)}")

    for path_ in path.iterdir():

        # if dir then recurse
        if path_.is_dir():
            yield from check_file_gen(path_, suffix)
            continue

        # otherwise file
        if path_.suffix == SUFFIX:
            print(f"Found file '{path_.relative_to(ROOT)}'")
            yield path_


def main():
    for file in check_file_gen(ROOT, SUFFIX):
        print(f"Copying {file.relative_to(ROOT)}")
        shutil.copyfile(file, TARGET / file.name)


if __name__ == '__main__':
    main()
    input("Press enter to exit")
