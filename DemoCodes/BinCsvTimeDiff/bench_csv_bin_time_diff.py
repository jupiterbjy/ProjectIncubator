"""
Demonstrates read time difference of CSV & Binary.

Since CPython's CSV module is written in C, so separation speed is comparable
to Compiled C++ speed.

Check -h for more info.

:Author: jupiterbjy@gmail.com
"""

import csv
import itertools
import random
import struct
import pathlib
import functools
import time
from argparse import ArgumentParser
from typing import Sequence, Callable, Generator


# --- Config ---

# Script root
ROOT = pathlib.Path(__file__).parent

# CSV File
CSV_DATA = ROOT / "sample.csv"

# BIN File
BIN_DATA = ROOT / "sample.bin"

# CSV column type converters
CSV_CONV_FUNCS = (
    int,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
)

# BIN byte order. <: little, >: big, =: native
BYTE_ORDER = "="

# BIN column type codes
BIN_TYPE_CODE = "Ifffffffff"

# Full type code
FULL_TYPE_CODE = BYTE_ORDER + BIN_TYPE_CODE

# BIN row size in bytes (from CSV_TYPE_CODES)
FULL_ROW_SIZE = struct.calcsize(FULL_TYPE_CODE)


# --- Utilities ---


def iter_path_recursive(path: pathlib.Path) -> Sequence[pathlib.Path]:
    """Iterates path recursively."""

    for p in path.iterdir():
        if p.is_file():
            yield p
        else:
            yield from iter_path_recursive(p)


def count_csv_rows(csv_file: pathlib.Path) -> int:
    """Count rows in given csv file path."""

    count = 0
    with csv_file.open("r") as fp:

        # count newlines
        while char := fp.read(1):
            if char == "\n":
                count += 1

        # check if last one was trailing newline, if so subtract one. it's not data.
        fp.seek(fp.tell() - 1)
        if fp.read(1) == "\n":
            count -= 1

    return count


def convert_csv_to_binary() -> None:
    """Converts csv to binary"""

    print(f"Converting {CSV_DATA.name} to binary")

    with BIN_DATA.open("wb") as dst_fp:

        # write length as uint32
        dst_fp.write(struct.pack(BYTE_ORDER + "I", count_csv_rows(CSV_DATA)))

        # write rows
        for row in read_csv_gen(CSV_DATA):
            dst_fp.write(struct.pack(FULL_TYPE_CODE, *row))


def measure_time_deco(repeats: int = 5) -> Callable[[Callable], Callable]:
    """Executes func multiple times and prints avg/min/max time.

    Args:
        repeats: number of function calls to measure

    Returns:
        time measuring decorator function
    """

    def _closure(func: Callable) -> Callable:

        @functools.wraps(func)
        def _wrapper(*args, **kwargs):

            print("Measuring time for", func.__name__)

            # spinner for eye candy
            spinner = itertools.cycle("⠋⠙⠸⠴⠦⠇")

            # digit required to display the highest repeat number
            repeat_digit = len(str(repeats))

            times = []

            for idx in range(1, repeats + 1):

                start = time.time()
                func(*args, **kwargs)
                end = time.time()

                times.append(end - start)
                print(
                    f"{next(spinner)} iter {idx:{repeat_digit}}/{repeats}: {times[-1]:3.5f}s",
                    end="\r",
                )
            print(f"\ntotal: {sum(times):.5f}s / avg: {sum(times) / repeats:.5f}s\n")

        return _wrapper

    return _closure


def generate_one() -> None:
    """Generates one csv file with random data."""

    with pathlib.Path("sample.csv").open("w", newline="") as fp:

        # prep writer
        writer = csv.writer(fp)

        # write header-ish
        writer.writerow(map(lambda x: x.__name__, CSV_CONV_FUNCS))

        # write random data
        for _ in range(50000):
            writer.writerow(map(lambda x: x(random.random()), CSV_CONV_FUNCS))


# --- Logics ---


def read_csv_gen(path: pathlib.Path) -> Generator[Sequence, None, None]:
    """Read csv from path."""

    with path.open("rt") as fp:

        # prep reader & skip header
        reader = csv.reader(fp)
        next(reader)

        # read, parse & yield data
        for row in reader:
            yield tuple(col_type(col) for col, col_type in zip(row, CSV_CONV_FUNCS))


def read_binary_gen(path: pathlib.Path) -> Generator[Sequence, None, None]:
    """Read binary from path."""

    with path.open("rb") as fp:

        # read length
        length = struct.unpack("I", fp.read(4))[0]

        # read data
        for _ in range(length):
            yield struct.unpack(FULL_TYPE_CODE, fp.read(FULL_ROW_SIZE))


# --- Drivers ---


def _main(repeats: int) -> None:
    """Main function to drive the test.

    It first converts the csv file to binary, then runs the test twice,
    once for csv and once for binary.

    Args:
        repeats: int, number of times to repeat the test.
    """

    # first generate & convert csv to binary
    generate_one()
    convert_csv_to_binary()

    # measure file size
    print(f"CSV size: {CSV_DATA.stat().st_size} bytes")
    print(f"BIN size: {BIN_DATA.stat().st_size} bytes\n")

    # bake test
    @measure_time_deco(repeats)
    def _test_csv():
        for _ in read_csv_gen(CSV_DATA):
            pass

    @measure_time_deco(repeats)
    def _test_binary():
        for _ in read_binary_gen(BIN_DATA):
            pass

    # run test
    _test_csv()
    _test_binary()


if __name__ == "__main__":
    # get number of repeats as param
    _parser = ArgumentParser(
        description="Measures time difference between binary and csv file reads."
    )

    _parser.add_argument(
        "-r",
        "--repeats",
        type=int,
        default=100,
        help="Number of times to repeat the test",
    )

    _args = _parser.parse_args()
    _main(_args.repeats)
