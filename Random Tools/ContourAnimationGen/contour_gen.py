"""
Simple code generating Contour animation-ish video out of image drag-n-drop.
Download GPL FFMPEG from https://github.com/BtbN/FFmpeg-Builds/releases/tag/latest

Author: jupiterbjy@gmail.com / nyarukoishi@gmail.com
"""

import shutil
import pathlib
import argparse
import tempfile
import traceback
from multiprocessing import Pool
from typing import List, Tuple

try:
    import cv2
    import numpy as np
    import ffmpeg
    from tqdm import tqdm
    from PIL import Image, ImageDraw
except ModuleNotFoundError:
    import install_module

    install_module.install()
    input("Please restart the script. Press Enter to exit.")
    exit()


ROOT = pathlib.Path(__file__).parent.absolute()
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(exist_ok=True)


class Config:
    """Hardcoded config area"""

    fade_step = 0.02
    transparent = False
    fps_cap = 60
    duration = 5
    res_multiply = 2
    threshold = 50, 200
    line_width = 2
    bg_color = 20, 20, 20
    line_color = 255, 255, 255, 255


def save_workload(
    arguments: Tuple[pathlib.Path, Image.Image, int, int, bool, Tuple[int, int, int]]
):
    """
    Wrapper for function 'save', just to unpack single parameter it
    received via process pool's map func.

    Args:
        arguments: tuple of parameters of save function.

    Returns:

    """
    save(*arguments)


def save(
    temp: pathlib.Path, img: Image.Image, index: int, digit: int, alpha: bool, bg_color
):
    """
    Actual save function intended to be used for multiprocessing.

    Args:
        temp: temp directory
        img: PIL loaded image to save
        index: frame number of the image
        digit: image file name padding digit
        alpha: if False, removes alpha channel from image.
        bg_color: background color to use for when removing alpha channel

    Returns:

    """

    w, h = img.size
    x, y = w & 1, h & 1
    path = temp / f"{str(index).zfill(digit)}.png"

    if any((x, y)):
        # crop image to make it even numbered
        x = w if not x else w - 1
        y = h if not y else h - 1

        img = img.crop((0, 0, x, y))

    if alpha:
        img.save(path)
    else:
        remove_alpha(img, bg_color).save(path)


def generate_fade(
    temp: pathlib.Path,
    source_img: Image.Image,
    contour_img: Image.Image,
    fade_step,
    transparent,
    bg_color,
    last_idx: int,
    digit: int,
):
    """
    Generate cross-fading frames.

    Notes:
        When creating stationary frames, script actually goes for dumb way to
        create tons of exact same frame to create sufficient length, to exclude
        logic and variables determining which frame has to be longer when encoding
        in ffmpeg.

    Args:
        temp: Temp directory
        source_img: PIL loaded source image
        contour_img: PIL loaded contoured image
        fade_step: fading step
        transparent: If true, will generate transparent images
        bg_color: background color
        last_idx: frame count in previous step
        digit: image file name padding digit

    Returns:

    """

    # cross-fade frame count
    alpha_fade = [n / 100 for n in range(100, 0, int(-fade_step * 100))]

    # frame count for each fade/stationary step
    size = len(alpha_fade)

    # using unnecessarily complex generator-fed process pool to make it work with tqdm
    def cross_fade_gen(alpha_list, start_idx):
        """
        Generate parameter tuples to field for process pool.

        Returns:
        """
        for idx, alpha in enumerate(alpha_list):
            blended_img = Image.blend(source_img, contour_img, alpha=alpha)
            yield temp, blended_img, start_idx + idx, digit, transparent, bg_color

    def stationary_gen():
        """
        Generate parameter tuples to field for process pool.

        Returns:
        """
        for idx_ in range(size):
            yield temp, source_img, idx_ + last_idx, digit, transparent, bg_color

    def fade_gen(alpha_list):
        """
        Generate parameter tuples to field for process pool.

        Returns:
        """
        for idx, alpha in enumerate(alpha_list):
            new_img = Image.new("RGBA", source_img.size)
            blended_img = Image.blend(new_img, source_img, alpha=alpha)

            yield temp, blended_img, last_idx + idx, digit, transparent, bg_color

    # feed process pool with generators
    with Pool() as pool:

        generators = (
            cross_fade_gen(alpha_fade, last_idx),
            stationary_gen(),
            fade_gen(alpha_fade),
        )
        messages = ("Generating CrossFade", "Generating Stationary", "Generating Fade")

        for gen, msg in zip(generators, messages):
            pool.map(save_workload, tqdm(gen, msg, size))
            last_idx += size


def generate_images(
    temp: pathlib.Path,
    contours: List[np.array],
    source_image: Image.Image,
    multiplier,
    fade_step,
    transparent: bool,
    bg_color,
    line_color,
    line_width,
):
    """
    Generate images to be used for ffmpeg encoding.

    Args:
        temp: temp directory
        contours: list of contour coordinates
        source_image: PIL loaded source image
        multiplier: resolution multiplier
        fade_step: total fading step
        transparent: if true, will generate transparent images
        bg_color: background color
        line_color: line color
        line_width: line width

    Returns:

    """

    # get size
    # concat = np.concatenate(contours, axis=0)
    # x, y = tuple(np.amax(concat, axis=0))

    src_x, src_y = source_image.size
    resized = source_image.resize((src_x * multiplier, src_y * multiplier))

    # prepare image
    img = Image.new("RGBA", resized.size)

    # check digit
    digit = len(str(len(contours) + len(range(100, 0, int(-fade_step * 100))) * 3))

    draw = ImageDraw.Draw(img)

    # maybe queue was better, but for memory.. idk
    def img_gen():
        """
        Generate parameter tuples to field for process pool.

        Returns:
        """

        for idx_, contour in enumerate(contours):
            range_1 = tuple(range(len(contour)))
            range_2 = [*range_1[1:], 0]

            for dot_1, dot_2 in zip(range_1, range_2):

                draw.line(
                    (tuple(contour[dot_1]), tuple(contour[dot_2])),
                    fill=line_color,
                    width=line_width,
                )

            yield temp, img.copy(), idx_, digit, transparent, bg_color

    # Save simultaneously, because saving operation in serial can be slower than HW capability
    with Pool() as pool:
        pool.map(save_workload, tqdm(img_gen(), "Drawing Contours", len(contours)))

    # now add fade to the frame fleets
    generate_fade(
        temp, resized, img, fade_step, transparent, bg_color, len(contours), digit
    )


def remove_alpha(image, bg_color: Tuple[int, int, int]):
    """
    Remove alpha channel from images by overlapping images.

    Args:
        image: image to remove background from
        bg_color: RGB background color

    Returns:
        non_transparent image
    """
    bg = Image.new("RGB", image.size, bg_color)
    bg.paste(image, mask=image.split()[3])
    return bg


def generate_video(
    temp: pathlib.Path, src_path: pathlib.Path, duration, fps_cap, transparent: bool
):
    """
    Generate video from previously created images using FFMPEG

    Args:
        temp: temp directory
        src_path: source image path
        duration: video duration
        fps_cap: maximum fps
        transparent: if true, will generate transparent video
    """

    # prepare output file path
    path_ = OUT_DIR / pathlib.Path(src_path).name

    # calculate fps, and enforce fps within range
    fps = len(tuple(temp.iterdir())) // duration
    if fps > fps_cap:
        fps = fps_cap

    txt = temp / "files.txt"

    # create txt file input for ffmpeg concat
    directory_listing = [
        f"file {p.as_posix()}" for p in temp.iterdir() if p.suffix == ".png"
    ]

    # now sort image order
    directory_listing = sorted(directory_listing)

    # start writing to input.txt
    with open(txt, "w") as fp:
        for directory in directory_listing:
            fp.write(f"{directory}\nduration 1\n")

        fp.write(f"{directory_listing[-1]}")

    # prepare save file and remove if same exists.
    output = path_.with_suffix(".webm" if transparent else ".mp4").absolute()
    output.unlink(missing_ok=True)

    # divide operation in 2 step. Not sure if I like this flow style.
    ffmpeg_setup = ffmpeg.input(txt.as_posix(), r=str(fps), f="concat", safe="0")

    # set param depending on transparency option
    if transparent:
        param = {"vcodec": "libvpx-vp9", "pix_fmt": "yuva420p", "crf": "20", "b:v": "0"}
    else:
        param = {"vcodec": "libx264", "pix_fmt": "yuv420p", "crf": "20"}

    # run ffmpeg
    ffmpeg_setup.output(output.as_posix(), **param).run()


def generate_contours(img_path, th_low: int, th_high: int, res_multiplier: int):
    """Generates contours using cv2.Canny

    Args:
        img_path: Absolute source image path
        th_low: Low threshold
        th_high: High threshold
        res_multiplier: Resolution Multiplier

    Returns:
        (contours, hierarchy)
    """

    source_img = cv2.imread(img_path)
    base = cv2.Canny(source_img, th_low, th_high)
    contours, hierarchy = cv2.findContours(
        base, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )

    # squeeze unnecessary dim and multiply contours to multiply resolutions
    multiplier = (res_multiplier, res_multiplier)
    squeezed = [np.squeeze(cnt, axis=1) * multiplier for cnt in contours]

    return squeezed, hierarchy


def main(file_path: pathlib.Path, thresholds: Tuple[int, int], multiplier):
    # print config
    config = {key: val for key, val in Config.__dict__.items() if key[0] != "_"}
    config["thresholds"] = thresholds
    config["multiplier"] = multiplier

    print("Config:", config)

    with tempfile.TemporaryDirectory("CONTOUR_GEN") as tmp:
        # prep temp - doing this because cv2 can't read unicode file path.
        tmp_dir = pathlib.Path(tmp).absolute()

        source_dir = tmp_dir / "source"
        source_dir.mkdir()

        # again copy file with some different name because cv2 can't read unicode file name.
        source_file = (source_dir / "source_file").with_suffix(file_path.suffix)
        shutil.copyfile(file_path, source_file)

        # generate contours
        contours, _ = generate_contours(source_file.as_posix(), *thresholds, multiplier)

        # generate contour drawing frames
        image = Image.open(file_path).convert("RGBA")
        generate_images(
            tmp_dir,
            contours,
            image,
            multiplier,
            Config.fade_step,
            Config.transparent,
            Config.bg_color,
            Config.line_color,
            Config.line_width,
        )

        # generate video from generated images inside tmp
        generate_video(
            tmp_dir, file_path, Config.duration, Config.fps_cap, Config.transparent
        )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        "Script generating contour timelapse video for given image."
    )
    parser.add_argument("file", type=pathlib.Path, help="Path to image")
    args = parser.parse_args()

    try:
        main(args.file, Config.threshold, Config.res_multiply)
    except Exception as err:
        traceback.print_exc()
        input(f"Encountered Error [{type(err).__name__}] Press enter to exit.")
