"""
Simply makes images perfect square by extending from shorter dimension.

`pip install pillow`

:Author: jupiterbjy@gmail.com
"""

import pathlib
import argparse

from PIL import Image


def main(image_files_: list[pathlib.Path]):

    root = pathlib.Path(__file__).parent.joinpath("Squared")
    root.mkdir(exist_ok=True)

    for image_path in image_files_:
        image: Image.Image = Image.open(image_path).convert("RGBA")

        img_x, img_y = image.size
        dim = max(img_x, img_y)

        x_offset = (dim - img_x) // 2
        y_offset = (dim - img_y) // 2

        # create new image
        new_empty = Image.new("RGBA", (dim, dim))

        # paste image
        new_empty.paste(image, (x_offset, y_offset))

        # save
        new_empty.save(root.joinpath(image_path.name))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Makes all image dimension square.")
    parser.add_argument(
        "images", metavar="I", type=pathlib.Path, nargs="+", help="Images to square-fy"
    )

    args = parser.parse_args()

    image_files: list = args.images
    image_files.sort(key=lambda x: x.stem)

    try:
        main(image_files)
    except Exception:
        import traceback

        traceback.print_exc()
        input()
