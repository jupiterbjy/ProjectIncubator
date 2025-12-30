"""
Just a Imagemagick wrapper to batch split webp into frames.

Made because I messed up few frames in ScreenToGif but it couldn't read webp it generated.

Requires Imagemagick in PATH.

:Author: jupiterbjy@gmail.com
"""

import subprocess
import pathlib
from typing import Sequence
from argparse import ArgumentParser


CMD = "magick {} -coalesce {}"
OUTPUT_NAME = "%05d.png"


def split(img_paths: Sequence[pathlib.Path]):
    for img_path in img_paths:
        if img_path.suffix != ".webp":
            print(f"ignoring non-webp {img_path.name}")
            continue

        print(f"Processing {img_path.name}")

        output_p = img_path.parent / img_path.stem / OUTPUT_NAME
        output_p.parent.mkdir(exist_ok=True)

        proc = subprocess.run(CMD.format(img_path.as_posix(), output_p.as_posix()))
        proc.check_returncode()


if __name__ == "__main__":
    _parser = ArgumentParser()
    _parser.add_argument("images", nargs="+", type=pathlib.Path)

    split(_parser.parse_args().images)
