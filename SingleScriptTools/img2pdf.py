"""
Simple Image to pdf script
"""

import pathlib
import argparse
from typing import Sequence

from PIL import Image


def image_path_to_pdf(image_paths: Sequence[pathlib.Path]):
    save_file = image_paths[0].with_suffix(".pdf")
    try:
        first_img, *rest_img = (Image.open(img_path) for img_path in image_paths)
    except Exception:
        print(f"Encountered error while loading images. Check last traceback.")
        raise

    first_img: Image.Image
    first_img.save(save_file, "pdf", save_all=True, append_images=rest_img)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        "Img2PDF",
        description="Combine images into single pdf file."
    )

    parser.add_argument(
        "files",
        metavar="F",
        type=pathlib.Path,
        nargs="+",
        help="Files to embed inside image. Will be compressed as zip."
    )

    args = parser.parse_args()
    image_path_to_pdf(args.files)
