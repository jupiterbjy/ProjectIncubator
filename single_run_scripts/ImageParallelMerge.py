#!/usr/bin/env python3

import pathlib
import argparse
import itertools
import time
import math
from typing import List

from PIL import Image


MAX_X_RELATIVE_TO_Y = 1.5


def main():
    # load images - consider input is all fine.
    images: List[Image.Image] = [Image.open(path_).convert("RGBA") for path_ in args.images]
    length = len(images)

    # get x sizes
    sizes_x = [image.size[0] for image in images]

    # this expects all images to be at least in similar dimension, so Y will lock to highest.
    # and max width will be used to assume maximum dimension.
    x_max = max(sizes_x)
    y_max = max(image.size[1] for image in images)

    # try to make it square without breaking order with maximum dimension
    for image_per_line in range(length, 0, -1):
        if image_per_line * x_max <= MAX_X_RELATIVE_TO_Y * y_max * math.ceil(length / image_per_line):


            # with decided img-per-line try dividing for even distribution
            y_image_count = math.ceil(length / image_per_line)
            img_per_line = length // y_image_count
            break
    else:
        img_per_line = 1
        y_image_count = length

    # with that image per line counter, make dimensions.
    x_size = img_per_line * x_max
    y_size = y_image_count * y_max

    # create new image
    new_empty = Image.new("RGBA", (x_size, y_size))

    # prepare iterator for tile ordering
    x_iter = itertools.cycle((n for n in range(img_per_line)))
    y_iter = itertools.cycle((n // img_per_line for n in range(img_per_line * y_size)))

    # paste image
    for image, x, y in zip(images, x_iter, y_iter):
        new_empty.paste(image, (x_max * x, y_max * y))

    # save
    new_empty.save(pathlib.Path(f"{int(time.time())}_merged_{len(images)}.png"))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("images", metavar="I", type=pathlib.Path, nargs="+", help="Images to horizontally merge with.")

    args = parser.parse_args()

    main()
