"""
Remove alpha channel from gif image, replacing it with desired color.

:Author: jupiterbjy@gmail.com
"""

import argparse
import pathlib
from collections.abc import Generator
from typing import Sequence, Tuple, Any, List
from ast import literal_eval

from PIL import Image, ImageSequence

# --- Config ---

ROOT = pathlib.Path(__file__).parent

OUTPUT_DIR = ROOT / "output"

SUFFIX_WHITELIST = {
    ".gif",
    ".webp",
}

OUTPUT_SUFFIX = ".gif"


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


def rgb_to_hex(color: Tuple[int, int, int], prefix: str = "#") -> str:
    """Convert RGB to hex"""

    return f"{prefix}{color[0]:02x}{color[1]:02x}{color[2]:02x}"


# --- Logics ---

def remove_bg(img_path: pathlib.Path, bg_color=(0, 0, 0), speed_multiplier=1.0):
    """
    Open & convert image to RGB with given background color

    Args:
        img_path: Image path
        bg_color: Background color to overlay image onto
        speed_multiplier: Speed multiplier

    Returns:
        Background overlaid image
    """

    print("Processing", img_path)

    gif_img = Image.open(img_path)
    img_iterator = ImageSequence.Iterator(gif_img)

    durations: List[int] = []
    converted_frames: List[Image.Image] = []

    for frame in img_iterator:

        bg_img = Image.new("RGBA", frame.size, bg_color)

        # Overlay the original image onto the black background
        converted_frames.append(Image.alpha_composite(bg_img, frame.convert("RGBA")).convert("RGB"))

        # in web. Only after accessing frame data it's loaded 'duration' is exposed.
        durations.append(max(frame.info["duration"] // speed_multiplier, 1))

    new_name = img_path.with_stem(img_path.stem + f"_{rgb_to_hex(bg_color, 'bg')}_x{speed_multiplier}")

    # combine to gif
    converted_frames[0].save(
        str(OUTPUT_DIR / new_name.with_suffix(OUTPUT_SUFFIX).name),
        save_all=True,
        loop=0,
        append_images=converted_frames[1:],
        duration=durations,
    )


def _main(img_paths: Sequence[pathlib.Path], bg_color: Tuple[int, int, int], speed_multiplier: float):
    OUTPUT_DIR.mkdir(exist_ok=True)

    for path in img_paths:
        try:
            remove_bg(path, bg_color, speed_multiplier)

        except Exception as err:
            print(err)


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
    _parser.add_argument(
        "-s",
        "--speed-multiplier",
        type=float,
        default=1.0,
        help="gif play speed multiplier",
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

    _main(_paths, _args.color, _args.speed_multiplier)
