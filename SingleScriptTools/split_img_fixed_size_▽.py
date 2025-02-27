"""
Cuts the image fixed-size from top left corner.

`pip install pillow`

Designed to cut some sprites in Armada Tanks for recreating.

![](readme_res/split_img_fixed_size.png)

:Author: jupiterbjy@gmail.com
"""

from argparse import ArgumentParser
import pathlib

from PIL import Image


EXTENSION = ".png"


ROOT = pathlib.Path(__file__).parent
OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def img_cut_gen(cut_w, cut_h, img_path):
    pass


def get_target_w_h():
    """Gets target Width and Height from user."""

    while True:
        try:
            w, h = map(
                int, input("Enter target Width x Height (i.e. 96x96): ").split("x")
            )
        except ValueError:
            continue

        return w, h


def main(args):

    cut_w, cut_h = args.cut_size

    for image_path in args.images:
        img: Image.Image = Image.open(image_path).convert()
        img_w, img_h = img.size

        # make subdir with image's name
        subdir = OUTPUT_DIR / image_path.stem
        subdir.mkdir(exist_ok=True)

        cropped_images = []

        for top_y, bottom_y in zip(
            range(0, img_h, cut_h), range(cut_h - 1, img_h, cut_h)
        ):
            for left_x, right_x in zip(
                range(0, img_w, cut_w), range(cut_w - 1, img_w, cut_w)
            ):
                cropped_images.append(
                    # need to compensate 1 pixel loss, pillow uses 0.5 0.5 as 0, 0 for what I read
                    img.crop((left_x, top_y, right_x + 1, bottom_y + 1))
                )

        # detect file digit length, so next to 1 isn't 10.
        digits = len(str(len(cropped_images) - 1))

        for idx, cropped_img in enumerate(cropped_images):
            save_path = subdir / f"{idx:0{digits}}{EXTENSION}"
            cropped_img.save(save_path)


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        "Fixed W/H Image splitter",
        description="Splits each provided images with specified size from top-left corner",
    )

    arg_parser.add_argument(
        "images", metavar="I", type=pathlib.Path, nargs="+", help="Images to split"
    )

    arg_parser.add_argument(
        "-c",
        "--cut-size",
        default=None,
        help="Cut size. Specify in WxH format. i.e. 96x96",
    )

    _parsed = arg_parser.parse_args()

    # validate value
    if _parsed.cut_size is None:
        _parsed.cut_size = get_target_w_h()
    else:
        try:
            _w, _h = map(int, _parsed.cut_size.split("x"))
        except ValueError as _err:
            raise ValueError("Wrong cut_size provided!") from _err

        _parsed.cut_size = _w, _h

    main(_parsed)
