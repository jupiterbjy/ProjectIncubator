"""
![](readme_res/strip_image_frame.png)

Simple script to strip n pixel from its border.

Resulting images will be saved at individual image locations with `_stripped` suffix.

Created this due to Bandicam keeps capturing images 2 pixel radius wider than actual window is.
Imagine dozens of such images to edit, hence this is.

:Author: jupiterbjy@gmail.com
"""


from argparse import ArgumentParser
import pathlib
import traceback

from PIL import Image


def strip(width: int, img_path: pathlib.Path):
    """Strip n pixel width from each sides"""

    img = Image.open(img_path)

    # skipping checks for whether stripping amount is larger than img size or not
    # just don't!

    img = img.crop((width, width, img.size[0] - width, img.size[0] - width))
    img_path = img_path.with_stem(img_path.stem + "_stripped")

    img.save(img_path)
    print(f"File saved at {img_path.name}")


def prompt() -> int:
    """Gets user input for how many pixel to strip from each side."""
    try:
        amount = int(input("Strip amount(in pixel): "))
        assert amount > 0

    except (ValueError, AssertionError):
        return prompt()

    return amount


def main(args):
    amount = prompt()
    path: pathlib.Path

    for path in args.images:
        try:
            strip(amount, path)
        except Exception:
            traceback.print_last()
            print(f"Skipping file {path.name}")


if __name__ == '__main__':
    _parser = ArgumentParser()
    _parser.add_argument(
        "images",
        metavar="I",
        type=pathlib.Path,
        nargs="+",
        help="Images to cut borders."
    )

    try:
        main(_parser.parse_args())
    except Exception:
        traceback.print_last()
        input("Press enter to exit:")
