"""
Multiplies video playback speed by discarding frames without encoding
Requires FFMPEG

:Author: jupiterbjy@gmail.com
"""

import pathlib
import asyncio
import argparse
from typing import List


FPS = 60
SPEED_MULTIPLIER = float(input("Video speed multiplier: "))

FRAME_TIME = round(1 / SPEED_MULTIPLIER, 4)
FFMPEG_CMD = 'ffmpeg -y -i {} -r 60 -filter:v "setpts={}*PTS" {}'


async def main():
    file_list: List[pathlib.Path] = args.VIDEO
    print("Target(s):", file_list)

    new_file_list = [
        file.with_name(file.stem + f"_x{SPEED_MULTIPLIER}" + file.suffix)
        for file in file_list
    ]

    for file, new_file in zip(file_list, new_file_list):
        formatted = FFMPEG_CMD.format(
            f'"{file.as_posix()}"', FRAME_TIME, f'"{new_file.as_posix()}"'
        )

        proc = await asyncio.create_subprocess_shell(
            formatted, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
        )

        while line := await proc.stdout.readline():
            print(line.decode(), end="")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("VIDEO", metavar="VID", type=pathlib.Path, nargs="+")

    args = parser.parse_args()

    asyncio.run(main())
