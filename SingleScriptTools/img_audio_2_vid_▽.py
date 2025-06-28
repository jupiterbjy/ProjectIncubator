"""
Script to convert image + audio to video via FFMPEG. (Basically bloated bash script)
Assumes FFMPEG exists in PATH.

If not, install via `scoop install ffmpeg` or `sudo apt install ffmpeg` or whatever pkg manager you use.

Drag & drop image and audio to create video.

:Author: jupiterbjy@gmail.com
"""

import pathlib
import subprocess
from argparse import ArgumentParser


# ref: https://superuser.com/a/1521517/1252755
# ref: https://superuser.com/a/1649001/1252755
# framerate should be min 10 or vid get extra seconds
COMMAND = 'ffmpeg -y -loop 1 -framerate 10 -i "{img}" -i "{audio}" -c:v libx264 -tune stillimage -shortest -fflags +shortest -max_interleave_delta 100M -preset veryfast "{out}"'

IMG_EXT = {".jpg", ".jpeg", ".png", ".gif"}


def create_vid(image_path: str, audio_path: str, output_path: str):
    """Creates a video from an image and an audio file using ffmpeg.

    Args:
        image_path (str): Path to the input image file.
        audio_path (str): Path to the input audio file.
        output_path (str, optional): Path to save the output video file.

    Raises:
        subprocess.CalledProcessError: on ffmpeg call error
    """

    command = COMMAND.format(img=image_path, audio=audio_path, out=output_path)

    print("Running with command:", command)

    try:
        subprocess.run(command, check=True, capture_output=True)

    except subprocess.CalledProcessError as e:
        print("Error creating video:", e.stderr.decode(), sep="\n")
        raise

    print("Done\n")


if __name__ == "__main__":
    _parser = ArgumentParser(
        description="Script to convert image + audio to video via FFMPEG"
    )

    _parser.add_argument(
        "audio_path",
        type=pathlib.Path,
        help="Path to the input audio file",
    )

    _parser.add_argument(
        "image_path",
        type=pathlib.Path,
        help="Path to the input image file",
    )

    _parser.add_argument(
        "--output_path",
        "-o",
        type=pathlib.Path,
        default="output.mp4",
        help="Path to save the output video file",
    )

    _args = _parser.parse_args()

    # if image is not an image, swap
    if _args.image_path.suffix not in IMG_EXT:
        _args.image_path, _args.audio_path = _args.audio_path, _args.image_path

    try:
        create_vid(
            _args.image_path.as_posix(),
            _args.audio_path.as_posix(),
            _args.output_path.as_posix(),
        )

    except subprocess.CalledProcessError as _:
        input("\nPress enter to exit:")
        raise

    except Exception as _:
        import traceback

        traceback.print_exc()
        input("\nPress enter to exit:")
        raise
