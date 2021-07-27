import pathlib
from sys import argv
from typing import List

import cv2
import numpy as np
import ffmpeg
from PIL import Image, ImageDraw


root = pathlib.Path(__file__).parent.absolute()
temp = root.joinpath("temp_img")
fade_div_factor = 20

try:
    file = argv[1]
except IndexError:
    print("No files provided.")

if temp.exists():
    for path_ in temp.iterdir():
        path_.unlink(missing_ok=True)


def generate_fade(source_img: Image.Image, number_last, pad_size):
    fade_factor = 254 // fade_div_factor

    for idx, alpha in enumerate(range(254, 0, -fade_factor)):

        print(f"Generating fade {idx}")

        copied: Image.Image = source_img.copy()
        copied2: Image.Image = source_img.copy()
        copied.putalpha(alpha)

        copied2.paste(copied, copied2)

        target_file = temp.joinpath(f"{str(idx + number_last).zfill(pad_size)}.png")

        copied2.save(target_file)


def generate_images(contours: List[np.array]):

    # get size
    concat = np.concatenate(contours, axis=0)
    max_dim = np.amax(concat, axis=0)

    # prepare image
    img = Image.new("RGBA", tuple(max_dim))
    idx = 0

    # check digit
    digit = len(str(len(concat) + fade_div_factor))

    draw = ImageDraw.Draw(img)

    for idx, contour in enumerate(contours):
        range_1 = tuple(range(len(contour)))
        range_2 = [*range_1[1:], 0]

        for dot_1, dot_2 in zip(range_1, range_2):

            draw.line(
                (tuple(contour[dot_1]), tuple(contour[dot_2])),
                fill="#00e5e5ff",
                width=2,
            )

        print(f"Saving {idx + 1} / {len(contours)}")
        target_file = temp.joinpath(f"{str(idx).zfill(digit)}.png")
        img.save(target_file)

    # Generate fade images
    generate_fade(img, idx + 1, digit)


def generate_video():
    path_ = pathlib.Path(file)
    path_ = path_.with_suffix(".mp4").absolute()

    txt = temp.joinpath("files.txt")

    # create txt file for input
    with open(txt, "w") as fp:
        fp.write("\n".join(f"file {path.as_posix()}" for path in temp.iterdir() if path.suffix == ".png"))

    (
        ffmpeg
        .input(txt.as_posix(), r="20", f="concat", safe="0")
        .output(path_.as_posix(), vcodec="libx264")
        .run()
    )


def main():
    frame = cv2.imread(file)
    print("target", file)

    canny = cv2.Canny(frame, 255, 0)

    contours, hierarchy = cv2.findContours(
        canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )

    squeezed = [np.squeeze(cnt, axis=1) for cnt in contours]

    generate_images(squeezed)

    generate_video()


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(err)
        input()
        raise
