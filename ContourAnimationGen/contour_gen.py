import json
import pathlib
import argparse
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

    input("Please restart the script. Press Enter to exit.")
    exit()


root = pathlib.Path(__file__).parent.absolute()
temp = root.joinpath("temp_img")
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
    file: pathlib.Path


def save_workload(arguments: Tuple[Image.Image, pathlib.Path, bool]):
    if arguments[-1]:
        arguments[0].save(arguments[1])
    else:
        remove_alpha(arguments[0]).save(arguments[1])


def fade_workload(arguments: Tuple[Image.Image, pathlib.Path, bool, int]):

    image = arguments[0] if arguments[2] else arguments[0].convert("RGBA")
    copied2: Image.Image = arguments[0].copy()
    image.putalpha(arguments[3])

    copied2.paste(image, copied2)

    remove_alpha(copied2).save(arguments[1])


def generate_fade(source_img: Image.Image, number_last, pad_size):
    alpha_list = [n for n in range(254, 0, -args.fade_step)]

    def procedure_image_name_gen():
        for idx, alpha in enumerate(alpha_list):

            yield source_img.copy(), temp.joinpath(
                f"{str(idx + number_last).zfill(pad_size)}.png"
            ), args.transparent, alpha

    with Pool() as pool:
        list(
            tqdm(
                pool.imap(fade_workload, procedure_image_name_gen()),
                "Generating Fade",
                len(alpha_list),
            )
        )


def generate_images(contours: List[np.array]):

    # get size
    concat = np.concatenate(contours, axis=0)
    x, y = tuple(np.amax(concat, axis=0))

    # try to make dimension even numbered, using & instead of % here for fun
    if x & 1:
        x += 1

    if y & 1:
        y += 1

    # prepare image
    img = Image.new("RGBA", (x, y))

    # check digit
    digit = len(str(len(contours) + args.fade_step))

    draw = ImageDraw.Draw(img)

    def procedure_image_gen():
        for idx_, contour in enumerate(contours):
            range_1 = tuple(range(len(contour)))
            range_2 = [*range_1[1:], 0]

            for dot_1, dot_2 in zip(range_1, range_2):

                draw.line(
                    (tuple(contour[dot_1]), tuple(contour[dot_2])),
                    fill="#00e5e5ff",
                    width=args.line_width,
                )

            yield img.copy(), temp.joinpath(
                f"{str(idx_).zfill(digit)}.png"
            ), args.transparent

    with Pool() as pool:
        list(
            tqdm(
                pool.imap(save_workload, procedure_image_gen()),
                "Drawing Contours",
                total=len(contours),
            )
        )

    # Generate fade images
    generate_fade(img, len(contours) + 1, digit)


def remove_alpha(image):
    bg = Image.new("RGB", image.size)
    bg.paste(image, mask=image.split()[3])
    return bg


def generate_video():
    path_ = output_dir.joinpath(pathlib.Path(args.file).name)

    fps = len(tuple(temp.iterdir())) // args.duration
    if fps > args.fps_cap:
        fps = args.fps_cap

    txt = temp.joinpath("files.txt")

    # create txt file for input
    directory_listing = [
        f"file {p.as_posix()}" for p in temp.iterdir() if p.suffix == ".png"
    ]

    with open(txt, "w") as fp:
        for directory in directory_listing:
            fp.write(f"{directory}\nduration 1\n")

        fp.write(f"{directory_listing[-1]}")

    if args.transparent:
        output = path_.with_suffix(".webm").absolute()
        output.unlink(missing_ok=True)
        (
            ffmpeg.input(txt.as_posix(), r=str(fps), f="concat", safe="0")
            .output(
                output.as_posix(),
                vcodec="libvpx",
                **{"pix_fmt": "yuva420p", "auto-alt-ref": "0"},
            )
            .run()
        )
    else:
        output = path_.with_suffix(".mp4").absolute()
        output.unlink(missing_ok=True)
        (
            ffmpeg.input(txt.as_posix(), r=str(fps), f="concat", safe="0")
            .output(
                output.as_posix(),
                vcodec="libx264",
                **{"pix_fmt": "yuv420p", "c:v": "libx264"},
            )
            .run()
        )


def main():

    # clear temp
    if temp.exists():
        for file_ in temp.iterdir():
            file_.unlink()
    else:
        temp.mkdir()

    frame = cv2.imread(args.file.as_posix())
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

    generate_images(squeezed)

    generate_video()


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

    config_file = json.loads(root.joinpath("config.json").read_text("utf8"))
    vars(args).update(config_file)
    parser.parse_args(namespace=args)

    pprint(vars(args))

    try:
        main()
    except Exception as err:
        traceback.print_exc()
        input(f"Encountered Error [{type(err).__name__}] Press enter to exit.")
        raise
