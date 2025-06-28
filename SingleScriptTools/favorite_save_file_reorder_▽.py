"""
Script to reorder save files from 'Irotoridori no Sekai'.
Should work for all visual novels from FAVORITE.

ALWAYS backup first.

Example output:
```
Save start idx: 1
Input files: s004.bin s005.bin s010.bin s012.bin ... s121.bin s122.bin s123.bin

Proceed? (y/N): y
Renamed s004.bin to s001.bin
Renamed s005.bin to s002.bin
Renamed s010.bin to s003.bin
Renamed s012.bin to s004.bin
Renamed s015.bin to s005.bin
...
Renamed s123.bin to s088.bin

Press enter to exit:
```

:Author: jupiterbjy@gmail.com
"""

import itertools
import pathlib
import argparse


PADDING = 3


def rename_save(files: list[pathlib.Path], start_idx: int):
    """Renames save files. Passed files are automatically sorted.
    Assumes index of save files are 0 padded (Which is the case for FAVORITE)

    Args:
        files: list of save file paths
        start_idx: new start index for save files.
    """

    # files better be 0 padded properly..
    files.sort()

    print("Input files:", " ".join(file.name for file in files))
    raw_in = input("\nProceed? (y/N): ")

    if raw_in not in "yY":
        print("Aborting")
        return

    counter = itertools.count(start_idx)
    for file in files:
        new_path = file.with_stem(f"s{next(counter):0{PADDING}}")
        # new_path = file.with_stem(f"s{next(iterator)}")
        file.rename(new_path)
        print(f"Renamed {file.name} to {new_path.name}")


if __name__ == "__main__":
    _parser = argparse.ArgumentParser()
    _parser.add_argument("files", nargs="+", type=pathlib.Path)
    _raw_in = input("Save start idx: ")

    try:
        rename_save(_parser.parse_args().files, int(_raw_in))

    except Exception as err:
        import traceback

        traceback.print_exc()
        input("\nPress enter to exit:")
        raise

    input("\nPress enter to exit:")
