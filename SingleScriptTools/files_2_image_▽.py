"""
Embeds file inside jpg metadata. Any decent unzipper can open as zip.

Check usage by executing without parameters.

![Example](readme_res/files_2_image.png)

:TODO: add one more image with zip file opened in BandiZip

:Author: jupiterbjy@gmail.com
"""

from collections.abc import MutableSequence, Sequence
from io import BytesIO
import argparse
import shutil
import tempfile
import pathlib
import time

from PIL import Image, ImageDraw, ImageFont


# --- Config ---

# Image file's stem(name without extension) to be used as disguise/display image.
# If such file is provided, it will disable placeholder image generation and use this instead.
DISGUISE_IMG_STEM = "_disguise"

# Add font here - lower the index, higher the priority
FONT_NAMES = ["not_existing_font_test.ttf", "malgunsl.ttf", "arial.ttf"]

OUTPUT_IMAGE = pathlib.Path(__file__).parent.joinpath(f"output_{time.time_ns()}.png")


# --- Font Load ---

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


# --- Logics ---


def generate_placeholder_img_from_paths(paths: Sequence[pathlib.Path]) -> BytesIO:
    """
    Generate placeholder image from given file paths.

    Args:
        paths: File paths to include in image

    Returns:
        Image's binary data writen by PIL
    """

    # sort path by DIR on top
    paths = sorted(paths, key=lambda p: p.is_dir())

    # prepare starting ment
    names = ["This image includes following files/directories:"]

    # add each file's name and type
    names.extend(f"{'DIR - ' if path.is_dir() else ''}{path.name}" for path in paths)

    # translate to pixel length - requires font to support all letters
    true_lengths = [FONT.getlength(name) for name in names]

    # find the longest string
    long = sorted(zip(true_lengths, names), key=lambda x: x[0])[-1][1]

    # find pixel dim
    _, y_pad, img_x, img_y = FONT.getbbox(long)
    img_y += y_pad

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

        # copy all files to temp dir
        for path in paths:
            print(path)
            if path.is_dir():
                shutil.copytree(path, tmp_copy_dir.joinpath(path.name))
            else:
                shutil.copyfile(path, tmp_copy_dir.joinpath(path.name))

        # create another to completely eliminate any possible name overlap
        with tempfile.TemporaryDirectory("ZIP_EMBED_OUTPUT") as tmp_out_str:
            tmp_out_dir = pathlib.Path(tmp_out_str)

            # create zip file
            shutil.make_archive(
                tmp_out_dir.joinpath("output").as_posix(), "zip", tmp_copy_dir
            )

            # now copy to memory
            with open(tmp_out_dir.joinpath("output.zip"), "rb") as fp:
                while data := fp.read(4096):
                    cache.write(data)

    # now all temp are clear. Return the data
    return cache


def embed_to_image(image_file: BytesIO, zipped_file: BytesIO):
    """Embed zipped file to image file.

    Args:
        image_file: In-memory image file
        zipped_file: In-memory zip file
    """
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


def extract_disguise_image(paths: MutableSequence[pathlib.Path]) -> BytesIO | None:
    """
    Find disguise image from given paths, Pop from given MutableSequence and return data of it.

    Args:
        paths: Paths to search for disguise image

    Returns:
        Image file's data if found, None otherwise
    """

    for path in paths:
        if path.stem == DISGUISE_IMG_STEM:
            data = Image.open(paths.pop(paths.index(path)))
            buffer = BytesIO()
            data.save(buffer, format="png")
            return buffer

    return None


def write_embedded_image(paths: Sequence[pathlib.Path]):
    """Write payload embedded image to disk.

    Args:
        paths: Files to embed inside image, optionally containing disguise image.
    """

    OUTPUT_IMAGE.touch()

    try:
        # check if we have thumbnail image
        disguise_img_bytes_io = extract_disguise_image(args.files)

        # if not create one
        if disguise_img_bytes_io is None:
            print(
                f"Disguise image with stem '{DISGUISE_IMG_STEM}' not found. Generating placeholder."
            )
            disguise_img_bytes_io = generate_placeholder_img_from_paths(args.files)

        # create in-memory zip archive
        zip_bytes_io = create_zip_archive(args.files)

        # create image from zip archive and thumbnail
        embed_to_image(disguise_img_bytes_io, zip_bytes_io)

    except Exception:
        # operation failed, remove touched img file
        OUTPUT_IMAGE.unlink()
        raise


# --- Driver ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Files2Image", description="Embed files into image."
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
        help=f"Files to embed inside image. Will be compressed as zip. Add '{DISGUISE_IMG_STEM}' to use as disguise."
        f"If not found, will generate placeholder image.",
    )

    args = parser.parse_args()
    write_embedded_image(args.files)
