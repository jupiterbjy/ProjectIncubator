"""
Multiplies video playback speed by discarding frames.
Requires FFMPEG

:Author: jupiterbjy@gmail.com
"""

import pathlib
import argparse
import subprocess


FPS: int = 60
FFMPEG_CMD = (
    'ffmpeg -i "{}" -r {} -filter:v "setpts={}*PTS" -an -c:v libx264 -crf 18 -y "{}"'
)


def main(paths: list[pathlib.Path], multiplier: float):
    if not multiplier:
        multiplier = float(input("Video speed multiplier: "))

    pts_factor = round(multiplier / FPS, 4)

    for path in paths:
        subprocess.run(
            FFMPEG_CMD.format(
                path.as_posix(),
                FPS,
                pts_factor,
                path.with_stem(f"{path.stem}_x{multiplier}fd").as_posix(),
            ),
            shell=True,
        )


if __name__ == "__main__":
    _parser = argparse.ArgumentParser()

    _parser.add_argument("video", metavar="VID", type=pathlib.Path, nargs="+")

    _parser.add_argument(
        "-m",
        "--multiplier",
        type=float,
        default=0.0,
        help="Video playback speed multiplier. If not set(or 0), will prompt for input.",
    )

    _args = _parser.parse_args()
    main(_args.video, _args.multiplier)
