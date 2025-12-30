"""
Simply resizes images to certain height, so it looks better when ordered in markdown or anything.
Only intended for non-animated, non-indexed color images (png & jpg mostly)

!! This WILL overwrite original files. !!

`pip install pillow`

:Author: jupiterbjy@gmail.com
"""

import pathlib
import argparse
from typing import Sequence

from PIL import Image


def main(tgt_height: int, img_paths: Sequence[pathlib.Path]):

    for img_p in img_paths:
        src = Image.open(img_p).convert("RGBA")

        ratio = tgt_height / src.height
        resized = src.resize((round(src.width * ratio), tgt_height))

        is_trans = not src.getextrema()[-1] == (255, 255)
        if not is_trans:
            resized = resized.convert("RGB")

        print(f"{img_p.name}->{src.size}->{resized.size}, alpha:{is_trans}")

        resized.save(img_p)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Limits image height")

    parser.add_argument(
        "-p",
        "--pixels",
        type=int,
        nargs=1,
        default=0,
        help="Target height in pixels. If not specified, will prompt for input.",
    )

    parser.add_argument(
        "images",
        type=pathlib.Path,
        nargs="+",
    )

    _args = parser.parse_args()
    if _args.pixels < 1:
        _args.pixels = int(input("Target height in pixels: "))

    try:
        main(_args.pixels, _args.images)

    except Exception:
        import traceback

        traceback.print_exc()
        input("Press enter to exit:")

        raise

    input("Press enter to exit:")
