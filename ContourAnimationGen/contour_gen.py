import json
import shutil
import pathlib
import argparse
import tempfile
import traceback
from pprint import pprint
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


root = pathlib.Path(__file__).parent.absolute()
output_dir = root.joinpath("output")
output_dir.mkdir(exist_ok=True)


class Args:
    fade_step: int
    transparent: bool
    fps_cap: int
    duration: float
    res_multiply: int
    threshold_low: int
    threshold_high: int
    line_width: int
    bg_color: Tuple[int, int, int]
    line_color: Tuple[int, int, int, int]
    file: pathlib.Path


def save_workload(arguments: Tuple[pathlib.Path, Image.Image, int, int, bool, Tuple[int, int, int]]):
    """
    Wrapper for function 'save', just to unpack single parameter it
    received via process pool's map func.

    Args:
        arguments: tuple of parameters of save function.

    Returns:

    """
    save(*arguments)


def save(temp: pathlib.Path, img: Image.Image, index: int, digit: int, alpha: bool, bg_color):
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
    path = temp.joinpath(f"{str(index).zfill(digit)}.png")

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
    temp: pathlib.Path, source_img: Image.Image, contour_img: Image.Image, last_idx, digit: int
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
        last_idx: frame count in previous step
        digit: image file name padding digit

    Returns:

    """

    # cross-fade frame count
    alpha_fade = [n / 100 for n in range(100, 0, int(-args.fade_step * 100))]

    # frame count for each fade/stationary step
    size = len(alpha_fade)

    # using unnecessarily complex generator-fed process pool to make it work with tqdm
    def cross_fade_gen(alpha_list, start_idx):
        """
        Generate parameter tuples to field for process pool.

        Returns:
        """
        for idx, alpha in enumerate(alpha_list):

            yield temp, Image.blend(
                source_img, contour_img, alpha=alpha
            ), start_idx + idx, digit, args.transparent, args.bg_color

    # This is the dumbest thing in this code, aww!
    def stationary_gen():
        """
        Generate parameter tuples to field for process pool.

        Returns:
        """
        for idx_ in range(size):
            yield temp, source_img, idx_ + last_idx, digit, args.transparent, args.bg_color

    def fade_gen(alpha_list):
        """
        Generate parameter tuples to field for process pool.

        Returns:
        """
        for idx, alpha in enumerate(alpha_list):
            new_img = Image.new("RGBA", source_img.size)

            yield temp, Image.blend(
                new_img, source_img, alpha=alpha
            ), last_idx + idx, digit, args.transparent, args.bg_color

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


def generate_images(temp: pathlib.Path, contours: List[np.array], source_image: Image.Image):
    """
    Generate images to be used for ffmpeg encoding.

    Args:
        temp: temp directory
        contours: list of contour coordinates
        source_image: PIL loaded source image

    Returns:

    """

    # get size
    # concat = np.concatenate(contours, axis=0)
    # x, y = tuple(np.amax(concat, axis=0))

    src_x, src_y = source_image.size
    factor = args.res_multiply

    resized = source_image.resize((src_x * factor, src_y * factor))

    # prepare image
    img = Image.new("RGBA", resized.size)

    # check digit
    digit = len(str(len(contours) + len(range(100, 0, int(-args.fade_step * 100))) * 3))

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
                    fill=args.line_color,
                    width=args.line_width,
                )

            yield temp, img.copy(), idx_, digit, args.transparent, args.bg_color

    # Save simultaneously, because saving operation in serial can be slower than HW capability
    with Pool() as pool:
        pool.map(save_workload, tqdm(img_gen(), "Drawing Contours", len(contours)))

    # now add fade to the frame fleets
    generate_fade(temp, resized, img, len(contours), digit)


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


def generate_video(temp: pathlib.Path):
    """
    Generate video from previously created images.

    Args:
        temp: temp directory

    Returns:

    """

    # prepare output file path
    path_ = output_dir.joinpath(pathlib.Path(args.file).name)

    # calculate fps, and check if it's within limit
    fps = len(tuple(temp.iterdir())) // args.duration
    if fps > args.fps_cap:
        fps = args.fps_cap

    txt = temp.joinpath("files.txt")

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
    output = path_.with_suffix(".webm" if args.transparent else ".mp4").absolute()
    output.unlink(missing_ok=True)

    # divide operation in 2 step. Not sure if I like this flow style.
    ffmpeg_setup = ffmpeg.input(txt.as_posix(), r=str(fps), f="concat", safe="0")

    if args.transparent:
        ffmpeg_setup.output(
            output.as_posix(),
            vcodec="libvpx-vp9",
            **{"pix_fmt": "yuva420p", "c:v": "libfvpx-vp9", "crf": "20", "b:v": "0"},
        ).run()

    else:
        ffmpeg_setup.output(
            output.as_posix(),
            vcodec="libx264",
            **{"pix_fmt": "yuv420p", "c:v": "libx264", "crf": "20"},
        ).run()


def main():
    with tempfile.TemporaryDirectory("CONTOUR_GEN") as tmp:
        # prep temp - doing this because cv2 can't read unicode file path.
        tmp_dir = pathlib.Path(tmp)

        source_dir = tmp_dir.joinpath("source")
        source_dir.mkdir()

        # again copy file with some different name because cv2 can't read unicode file name.
        source_file = source_dir.joinpath("source_file").with_suffix(args.file.suffix)
        shutil.copyfile(args.file, source_file)

        # now let cv2 read it
        frame = cv2.imread(source_file.as_posix())
        print("target", args.file.as_posix())

        base = cv2.Canny(frame, args.threshold_low, args.threshold_high)

        contours, hierarchy = cv2.findContours(
            base, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
        )

        # squeeze and multiply contours
        squeezed = [
            np.squeeze(cnt, axis=1) * [args.res_multiply, args.res_multiply]
            for cnt in contours
        ]

        generate_images(tmp_dir, squeezed, Image.open(args.file).convert("RGBA"))

        generate_video(tmp_dir)


if __name__ == "__main__":

    args = Args()

    parser = argparse.ArgumentParser(
        "Script generating contour timelapse video for given image."
    )
    parser.add_argument(
        "-s",
        "--fade-step",
        metavar="INT",
        type=int,
        help="alpha value step size for fading effects",
    )
    parser.add_argument(
        "-t",
        "--transparent",
        metavar="BOOL",
        type=bool,
        help="If true, generates transparent webm - this yield worse quality.",
    )
    parser.add_argument(
        "-f",
        "--fps-cap",
        metavar="INT",
        type=int,
        help="Sets hard limit on frame rate.",
    )
    parser.add_argument(
        "-d",
        "--duration",
        metavar="FLOAT",
        type=float,
        help="how long video should be in seconds. This will be ignored when fps exceed fps-cap.",
    )
    parser.add_argument(
        "-m",
        "--res-multiply",
        metavar="INT",
        type=int,
        help="Resolution multiplier for contours.",
    )
    parser.add_argument(
        "-tl",
        "--threshold-low",
        metavar="INT",
        type=int,
        help="Low threshold of canny edge detection. More lines are drawn when lower.",
    )
    parser.add_argument(
        "-th",
        "--threshold-high",
        metavar="INT",
        type=int,
        help="High threshold of canny edge detection. More lines are drawn when lower.",
    )
    parser.add_argument(
        "-w",
        "--line-width",
        metavar="INT",
        type=int,
        help="Thickness of contour lines.",
    )
    parser.add_argument("file", type=pathlib.Path, help="Path to image")

    # Load config and write into args namespace
    config_file = json.loads(root.joinpath("config.json").read_text("utf8"))
    vars(args).update(config_file)
    parser.parse_args(namespace=args)

    # convert parameters
    args.line_color = tuple(args.line_color)
    args.bg_color = tuple(args.bg_color)

    pprint(vars(args))

    # fail fast
    if not args.file.is_file():
        input("Supplied parameter is not a file. Press enter to exit.")
        exit(1)

    # else continue
    try:
        main()
    except Exception as err:
        traceback.print_exc()
        input(f"Encountered Error [{type(err).__name__}] Press enter to exit.")
        raise
