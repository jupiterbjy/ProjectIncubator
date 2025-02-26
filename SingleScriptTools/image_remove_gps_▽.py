"""
Removes GPS tags from image EXIF data

`pip install exif`

:Author: jupiterbjy@gmail.com
"""

import pathlib
import argparse

from exif import Image


# --- Logics ---


def remove_gps_tags(image_path: pathlib.Path, new_img_suffix: str = ""):
    """Remove gps tags from image and save it with new suffix.
    If suffix is not provided, the original file will be overwritten.

    Args:
        image_path: Path to image
        new_img_suffix: Suffix for output image. If empty, will overwrite original instead.
    """

    try:
        print("Processing", image_path)

        img = Image(image_path.read_bytes())

        # filter all GPS tags and delete it
        gps_tag_names = [name for name in img.list_all() if name.startswith("gps")]

        if not gps_tag_names:
            print("No GPS tags found, skipping\n")
            return

        print("Found GPS tags:", gps_tag_names)

        for name in gps_tag_names:
            img.delete(name)

        # save
        if new_img_suffix:
            image_path = image_path.with_stem(image_path.stem + new_img_suffix)

        image_path.write_bytes(img.get_file())

        print(f"Image saved at {image_path}\n")

    except Exception as e:
        print(f"Error processing {image_path}: {e}\n")


# --- Drivers ---

if __name__ == "__main__":

    _parser = argparse.ArgumentParser(description="Remove EXIF GPS tags from images")
    _parser.add_argument(
        "images", nargs="+", type=pathlib.Path, help="List of image files to process"
    )
    _parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="Overwrite original image instead of saving to a new file",
    )
    _parser.add_argument(
        "-n",
        "--nowait",
        action="store_true",
        help="Don't wait for user input after processing",
    )
    _args = _parser.parse_args()

    _suffix = "" if _args.overwrite else "_gps_stripped"

    for _image in _args.images:
        remove_gps_tags(_image, _suffix)

    if not _args.nowait:
        input("Press enter to exit")
