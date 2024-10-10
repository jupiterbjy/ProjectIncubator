"""
Remove alpha channel from image with desired color.

:Author: jupiterbjy@gmail.com
"""

import argparse
import pathlib
from collections.abc import Generator
from typing import Sequence, Tuple, Any
from ast import literal_eval

from PIL import Image


# --- Config ---

ROOT = pathlib.Path(__file__).parent

OUTPUT_DIR = ROOT / "output"

SUFFIX_WHITELIST = {
    ".png",
    ".webp",
    ".tiff",
    ".bmp",
}


# --- Utilities ---

def _extract_path(path: pathlib.Path) -> Generator[pathlib.Path]:
    """Extract path recursively."""

    if path.is_file():
        yield path
        return

    for inner_path in path.iterdir():
        yield from _extract_path(inner_path)


def _validate_color(supposed_to_be_color: Any):
    """Raise AssertionError if color is invalid."""

    assert isinstance(supposed_to_be_color, tuple)
    assert len(supposed_to_be_color) == 3
    assert all(isinstance(x, int) for x in supposed_to_be_color)
    assert all(0 <= x <= 255 for x in supposed_to_be_color)


# --- Logics ---

def remove_bg(img_path: pathlib.Path, bg_color=(0, 0, 0)) -> Image.Image:
    """
    Open & convert image to RGB with given background color

    Args:
        img_path: Image path
        bg_color: Background color to overlay image onto

    Returns:
        Background overlaid image
    """

    print("Processing", img_path)

    img = Image.open(img_path).convert("RGBA")
    bg_img = Image.new("RGBA", img.size, bg_color)

    # Overlay the original image onto the black background
    blended_img = Image.alpha_composite(bg_img, img).convert("RGB")

    return blended_img


def _main(img_paths: Sequence[pathlib.Path], bg_color: Tuple[int, int, int]):
    OUTPUT_DIR.mkdir(exist_ok=True)

    for path in img_paths:
        try:
            img = remove_bg(path, bg_color)
        except Exception as err:
            print(err)

        else:
            new_path = OUTPUT_DIR / path.name
            img.save(new_path)


if __name__ == "__main__":
    _parser = argparse.ArgumentParser(
        description="Remove alpha from img files by overlaying them on a black background."
    )

    _parser.add_argument(
        "paths", nargs="+", type=pathlib.Path, help="Image files/directories to convert"
    )
    _parser.add_argument(
        "-c",
        "--color",
        type=str,
        default="0,0,0",
        help="Background RGB color to overlay image onto",
    )

    _args = _parser.parse_args()
    try:
        _args.color = literal_eval(_args.color)
        _validate_color(_args.color)

    except (SyntaxError, AssertionError):
        print("Wrong color format provided")
        exit(1)

    _paths = []
    for _path in _args.paths:
        _paths.extend(_p for _p in  _extract_path(_path) if _p.suffix.lower() in SUFFIX_WHITELIST)

    _main(_paths, _args.color)
