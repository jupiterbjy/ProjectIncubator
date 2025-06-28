"""
Script to convert audio to video with placeholder image using FFMPEG.
Assumes FFMPEG exists in PATH.

Images should be numbered in ascending order - this will be used as order of video.

If not, install via `scoop install ffmpeg` or `sudo apt install ffmpeg` or whatever pkg manager you use.

Primarily written to generate YT Video for visual novel (Especially Hoshizora no Memoria).

Requires a mapping text file that defines which audio maps to image with format of:
```
audio_name title
```

where line no. becomes order of video.

For i.e. with text file 'Test.txt':

```
11 Chinamiism!
12 Tempo Up
...
16 Manatsu wa Festival! [A Midsummer Festival!]
45 Hoshikage [Starlight]
46 Oka no Ue de Futari [The Two of Us on a Hill]
47 Mikomai [Shrine Maiden Dance]
17 Whisper...
```

Would output files under 'script_root/output_Test' folder as:

```
01 Chinamiism!.mp4
02 Tempo Up.mp4
...
```

...Which is due to the fact audio files in bgm.bin aren't fully ordered.

Example output:
```
[L01] Creating 01 (Original) Eternal recurrence.mp4
Running with command: ffmpeg -y -loop 1 -framerate 1 -i "images/01.png" -i "sounds/01(original).ogg" ...
Done

[L02] Creating 02 Prelude ~Memoria~.mp4
Running with command: ffmpeg -y -loop 1 -framerate 1 -i "images/02.png" -i "sounds/02.ogg" ...
Done

[L03] Creating 03 Mezame [Awaken].mp4
Running with command: ffmpeg -y -loop 1 -framerate 1 -i "images/03.png" -i "sounds/03.ogg" ...
Done

...
```

:Author: jupiterbjy@gmail.com
"""

import pathlib
import subprocess
from argparse import ArgumentParser

# ref: https://superuser.com/a/1521517/1252755
# ref: https://superuser.com/a/1649001/1252755
# framerate should be min 10 or vid get extra seconds
COMMAND = 'ffmpeg -y -loop 1 -framerate 10 -i "{img}" -i "{audio}" -c:v libx264 -tune stillimage -shortest -fflags +shortest -max_interleave_delta 100M -preset veryfast "{out}"'


ROOT = pathlib.Path(__file__).parent
OUTPUT_DIR_PREFIX = "output_"
OUTPUT_EXT = ".mp4"


def create_vid(image_path: str, audio_path: str, output_path: str):
    """Creates a video from an image and an audio file using ffmpeg.

    Args:
        image_path (str): Path to the input image file.
        audio_path (str): Path to the input audio file.
        output_path (str, optional): Path to save the output video file.
    """

    command = COMMAND.format(img=image_path, audio=audio_path, out=output_path)

    print("Running with command:", command)

    try:
        subprocess.run(command, check=True, capture_output=True)

    except subprocess.CalledProcessError as e:
        print("Error creating video:", e.stderr.decode(), sep="\n")
        return

    print("Done\n")


def main(
    mapping_txt_path: pathlib.Path, image_dir: pathlib.Path, audio_dir: pathlib.Path
):
    """Main logic, yeah

    Args:
        mapping_txt_path: path to mapping txt file
        image_dir: Image directory containing numbered images
        audio_dir: Audio directory
    """

    lines = [
        line for line in mapping_txt_path.read_text("utf8").splitlines() if line.strip()
    ]

    digits = len(str(len(lines)))

    image_pool = {int(p.stem): p for p in image_dir.iterdir()}
    audio_pool = {p.stem: p for p in audio_dir.iterdir()}

    output_dir = ROOT / (OUTPUT_DIR_PREFIX + mapping_txt_path.stem)
    output_dir.mkdir(exist_ok=True)

    print(f"Got {len(lines)} files to process")

    for line_no, line in enumerate(lines, start=1):

        file_name, title = line.split(" ", 1)
        line_no_str = str(line_no).zfill(digits)

        if line_no not in image_pool or file_name not in audio_pool:
            print(f"\n[L{line_no_str}] Missing audio or image, skipping")
            continue

        image_path = image_pool[line_no]
        audio_path = audio_pool[file_name]
        output_path = output_dir / f"{line_no_str} {title}{OUTPUT_EXT}"

        print(f"\n[L{line_no_str}] Creating {output_path.name}")
        create_vid(image_path.as_posix(), audio_path.as_posix(), output_path.as_posix())


if __name__ == "__main__":
    _parser = ArgumentParser(
        description="Script to convert audio to video with placeholder image using FFMPEG"
    )

    _parser.add_argument(
        "mapping_txt_path",
        type=pathlib.Path,
        help="Path to the mapping txt file",
    )

    _parser.add_argument(
        "image_dir",
        type=pathlib.Path,
        help="Directory of image files",
    )
    _parser.add_argument(
        "audio_dir",
        type=pathlib.Path,
        help="Directory of audio files",
    )

    _args = _parser.parse_args()
    main(_args.mapping_txt_path, _args.image_dir, _args.audio_dir)
