"""
Just generates random csv file
"""

import pathlib
import random
import csv


# --- Config ---

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


ITEM_COUNT = 10000


# --- Logic ---


def generate_one() -> None:
    """Generates one csv file with random data."""

    with pathlib.Path("sample.csv").open("w", newline="") as fp:

        # prep writer
        writer = csv.writer(fp)

        # write header-ish
        writer.writerow(map(lambda x: x.__name__, CSV_CONV_FUNCS))

        # write random data
        for _ in range(ITEM_COUNT):
            writer.writerow(map(lambda x: x(random.random()), CSV_CONV_FUNCS))


if __name__ == "__main__":
    generate_one()
