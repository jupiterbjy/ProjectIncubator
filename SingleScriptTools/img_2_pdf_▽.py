"""
Convert multiples images into single pdf

`pip install pillow`

:Author: jupiterbjy@gmail.com
"""

import pathlib
import argparse
import time
import traceback
from typing import Sequence, Generator

from PIL import Image


TIMEOUT = 10


def fetch_image_gen(
    paths: Sequence[pathlib.Path],
) -> Generator[Image.Image, None, None]:
    """Fetch images from given Sequence of Path objects.

    Args:
        paths: Sequence of image paths

    Returns:
        Generator yielding PIL Images
    """

    for path in paths:
        print(f"Loading {path.name}")
        img_temp = Image.open(path)

        # convert all into RGB, no RGBA or else allowed
        if img_temp.mode == "RGBA":

            # use white bg
            bg = Image.new("RGBA", img_temp.size, (255, 255, 255))
            bg.alpha_composite(img_temp)
            img_temp = bg

        elif img_temp.mode != "RGB":
            img_temp.convert("RGB")

        yield img_temp


def image_path_to_pdf(paths: Sequence[pathlib.Path]):
    """Load given image paths and save as pdf file.

    Args:
        paths: Sequence of image paths
    """
    save_file = paths[0].with_suffix(".pdf")

    try:
        # fetch first img & append others
        first_img, *rest_img = fetch_image_gen(paths)
        first_img.save(save_file, "pdf", save_all=True, append_images=rest_img)

    except Exception as err:
        # report error and wait

        traceback.print_exc()

        print(f"{type(err).__name__} while loading images. Check last traceback.")
        print(f"Will be closed in {TIMEOUT} seconds.")
        time.sleep(TIMEOUT)

        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Img2PDF",
        description="Combine images into single pdf file."
        "Will use first file name as resulting PDF.",
    )

    parser.add_argument(
        "files",
        metavar="F",
        type=pathlib.Path,
        nargs="+",
        help="Files to embed inside image. Will be compressed as zip.",
    )

    args = parser.parse_args()
    image_path_to_pdf(args.files)
