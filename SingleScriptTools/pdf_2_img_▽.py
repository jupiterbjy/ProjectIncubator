"""
Split image pdf back to multiple images

`pip install pypdf`

:Author: jupiterbjy@gmail.com
"""

import pathlib
import argparse
from pypdf import PdfReader

ROOT = pathlib.Path(__file__).parent
SUBDIR_SUFFIX = "_split"


def pdf_path_to_images(path: pathlib.Path) -> None:
    """Load given image paths and save as pdf file.

    Args:
        paths: Sequence of image paths
    """

    subdir = path.parent / f"{path.stem}{SUBDIR_SUFFIX}"
    subdir.mkdir(exist_ok=True)

    reader = PdfReader(path)
    digits = len(str(len(reader.pages)))


    for p_idx, page in enumerate(reader.pages):
        img_digits = len(str(len(page.images)))

        for img_idx, img_obj in enumerate(page.images):
            save_file = subdir / f"{p_idx:0{digits}}_{img_idx:0{img_digits}}.png"
            img_obj.image.save(save_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "PDF2Img",
        description="Combine images into single pdf file."
        "Will create subdir next to src pdf with name {src_name}_split",
    )

    parser.add_argument(
        "file",
        type=pathlib.Path,
        help="Files to embed inside image. Will be compressed as zip.",
    )

    args = parser.parse_args()
    pdf_path_to_images(args.file)
