"""
Simple Image to pdf script
"""

import pathlib
import argparse
from typing import Sequence, Generator

from PIL import Image


def path_to_image_gen(paths: Sequence[pathlib.Path]) -> Generator[None, Image.Image, None]:
    for path in paths:
        img_temp = Image.open(path)

        # convert all into RGB
        if img_temp.mode != "RGB":
            img_temp = img_temp.convert("RGB")

        yield img_temp


def image_path_to_pdf(paths: Sequence[pathlib.Path]):
    save_file = paths[0].with_suffix(".pdf")
    try:
        first_img, *rest_img = path_to_image_gen(paths)
    except Exception:
        print(f"Encountered error while loading images. Check last traceback.")
        raise

    try:
        first_img: Image.Image
        first_img.save(save_file, "pdf", save_all=True, append_images=rest_img)
    except Exception:
        print(f"Encountered error while saving images. Check last traceback.")
        raise


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
