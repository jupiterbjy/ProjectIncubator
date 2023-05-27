"""
Merges multiple images into one big tiled image with desired height & width ratio.

![Example](readme_res/parallel_merge.png)
"""

import pathlib
import argparse
import itertools
import time
import math
from typing import List, Tuple

from PIL import Image

# Config --------------------------------------

# Resulting image's X size relative to Y size
MAX_XY_RATIO = 1.5

ROOT = pathlib.Path(__file__).parent

# ---------------------------------------------


def calculate_row_col_size(x_size, y_size, image_counts) -> Tuple[int, int]:
    """Finds suitable size of row & column so that final big image's
    XY ratio roughly matches desired setting

    Args:
        x_size: Largest X pixel size in image
        y_size: Largest Y pixel size in image
        image_counts: Number of images to merge

    Returns:
        (column size, row size)
    """

    # iterate column size from largest to smallest
    for col_size in range(image_counts, 0, -1):

        # check if column pixel size ratio is below the target
        if col_size * x_size <= MAX_XY_RATIO * y_size * math.ceil(image_counts / col_size):

            # with decided img-per-line try dividing for even distribution
            final_row_size = math.ceil(image_counts / col_size)
            final_col_size = math.ceil(image_counts / final_row_size)
            break
    else:
        # otherwise just set to 1, can't find better ratio
        final_col_size = 1
        final_row_size = image_counts

    return final_col_size, final_row_size


def main():
    # load images - consider input is all fine.
    images: List[Image.Image] = [Image.open(path_).convert("RGBA") for path_ in args.images]

    # find the largest image dimension for each axis
    x_max = max(image.size[0] for image in images)
    y_max = max(image.size[1] for image in images)

    # get row col size
    col, row = calculate_row_col_size(x_max, y_max, len(images))

    # with that image per line counter, create new image.
    new_empty = Image.new("RGBA", (col * x_max, row * y_max))

    # prepare iterator for tile ordering
    x_iter = itertools.cycle((n for n in range(col)))
    y_iter = (n // col for n in range(col * row))

    # paste image
    for image, x, y in zip(images, x_iter, y_iter):
        new_empty.paste(image, (x_max * x, y_max * y))

    # save
    new_empty.save(ROOT / f"{int(time.time())}_merged_{len(images)}.png")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("images", metavar="I", type=pathlib.Path, nargs="+", help="Images to merge with.")

    args = parser.parse_args()

    main()
