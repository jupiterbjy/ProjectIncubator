"""
Embeds file inside jpg metadata. Any decent unzipper can open as zip.

Check usage by executing without parameters

![Example](readme_res/files_2_image.png)
"""

from typing import Sequence
from io import BytesIO
import argparse
import shutil
import tempfile
import pathlib
import time

from PIL import Image, ImageDraw, ImageFont

# Add font here - lower the index, higher the priority
FONT_NAMES = ["not_existing_font_test.ttf", "malgunsl.ttf", "arial.ttf"]

OUTPUT_IMAGE = pathlib.Path(__file__).parent.joinpath(f"output_{time.time_ns()}.png")


# try to load font
for font in FONT_NAMES:
    try:
        FONT = ImageFont.truetype(font, size=20)
    except OSError:
        print(f"Failed to load font <{font}> - Falling back")
        continue

    break
else:
    # no default font exists, use fallback
    print("No other fonts are available, using default - May encounter glyph error.")
    FONT = ImageFont.load_default()


def generate_image_from_file_paths(paths: Sequence[pathlib.Path]) -> BytesIO:
    """
    Generate image from given file paths.

    Args:
        paths: Bytes IO file list

    Returns:
        Image's binary
    """

    # sort path by DIR on top
    paths = sorted(paths, key=lambda p: p.is_dir())

    # prepare starting ment
    names = ["This image includes following files/directories:"]

    # add each file's name and type
    names.extend(f"{'DIR - ' if path.is_dir() else ''}{path.name}" for path in paths)

    # translate to pixel length - requires font to support all letters
    true_lengths = [FONT.getsize(name) for name in names]

    # find the longest string
    long = sorted(zip(true_lengths, names), key=lambda x: x[0])[-1][1]

    # find pixel length
    img_x, img_y = FONT.getsize(long)

    # create image from known length
    image = Image.new("RGB", (img_x, img_y * len(names)), color=(0, 0, 0))

    # draw text
    drawer = ImageDraw.Draw(image)

    for idx, line in enumerate(names):
        drawer.text((0, idx * img_y), line, font=FONT)

    # save into bytes io
    data = BytesIO()
    image.save(data, format="png")

    return data


def create_zip_archive(paths: Sequence[pathlib.Path]) -> BytesIO:
    """
    Zips files at given path using temp directories.

    Args:
        paths: File paths to compress

    Returns:
        BytesIO containing compressed zip file
    """

    cache = BytesIO()

    # create temp dir to copy all requested files into
    with tempfile.TemporaryDirectory("IMG_ZIP_EMBED") as tmp_copy_str:
        tmp_copy_dir = pathlib.Path(tmp_copy_str)
        for path in paths:
            print(path)
            if path.is_dir():
                shutil.copytree(path, tmp_copy_dir.joinpath(path.name))
            else:
                shutil.copyfile(path, tmp_copy_dir.joinpath(path.name))

        # create another to completely eliminate name any possible name overlap
        with tempfile.TemporaryDirectory("ZIP_EMBED_OUTPUT") as tmp_out_str:
            tmp_out_dir = pathlib.Path(tmp_out_str)

            # create zip file
            shutil.make_archive(tmp_out_dir.joinpath("output").as_posix(), "zip", tmp_copy_dir)

            # now copy to memory
            with open(tmp_out_dir.joinpath("output.zip"), "rb") as fp:
                while data := fp.read(4096):
                    cache.write(data)

    # now all temp are clear. Return the data
    return cache


def embed_to_image(image_file: BytesIO, zipped_file: BytesIO):

    # reset zip cursor to start
    zipped_file.seek(0)

    # write zip to image file
    while data := zipped_file.read(4096):
        image_file.write(data)

    image_file.seek(0)

    # save as image with timestamp as name
    with OUTPUT_IMAGE.open("wb") as fp:
        while data := image_file.read(4096):
            fp.write(data)


def main():
    OUTPUT_IMAGE.touch()

    try:
        image_io = generate_image_from_file_paths(args.files)
        zip_io = create_zip_archive(args.files)

        embed_to_image(image_io, zip_io)
    except Exception:
        # operation failed, remove touched img file
        OUTPUT_IMAGE.unlink()
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        "Files2Image",
        description="Embed files into image."
    )

    # parser.add_argument(
    #     "-i",
    #     "--image",
    #     type=pathlib.Path,
    #     help="Optional image file for extra surprise. If omitted, will generate placeholder image."
    # )

    parser.add_argument(
        "files",
        metavar="F",
        type=pathlib.Path,
        nargs="+",
        help="Files to embed inside image. Will be compressed as zip."
    )

    args = parser.parse_args()

    main()
