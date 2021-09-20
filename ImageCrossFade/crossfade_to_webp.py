import json
import pathlib
import argparse
import traceback
from pprint import pprint
from multiprocessing import Pool
from typing import List, Tuple

import ffmpeg
from tqdm import tqdm
from PIL import Image


root = pathlib.Path(__file__).parent.absolute()
temp = root.joinpath("temp_img")
output_dir = root.joinpath("output")

output_dir.mkdir(exist_ok=True)


class Args:
    fade_step: int
    fps_cap: int
    files: List[pathlib.Path]


def save_workload(arguments: Tuple[Image.Image, int, int]):
    save(*arguments)


def save(img: Image.Image, index: int, digit: int):
    w, h = img.size
    x, y = w & 1, h & 1
    path = temp.joinpath(f"{str(index).zfill(digit)}.png")

    if any((x, y)):
        # crop image to make it even numbered
        x = w if not x else w - 1
        y = h if not y else h - 1

        img = img.crop((0, 0, x, y))

    img.save(path)


def generate_fade(
    img_first: Image.Image, img_second: Image.Image
):
    alpha_fade = [n / 100 for n in range(100, 0, int(-args.fade_step * 100))]

    if alpha_fade[-1] != 1:
        alpha_fade.append(0)

    size = len(alpha_fade)
    digit = len(str(size))

    last_idx = 0

    def cross_fade_gen():
        for idx, alpha in enumerate(alpha_fade):

            yield Image.blend(
                img_second, img_first, alpha=alpha
            ), idx, digit

    with Pool() as pool:
        tuple(tqdm(pool.imap(save_workload, cross_fade_gen()), "Generating CrossFade", size))


def generate_video():
    path_ = output_dir.joinpath(pathlib.Path(args.files[0]).name)

    fps = args.fps_cap

    txt = temp.joinpath("files.txt")

    # create txt file for input
    directory_listing = [
        f"file {p.as_posix()}" for p in temp.iterdir() if p.suffix == ".png"
    ]

    directory_listing = sorted(directory_listing)

    # repeat index 1 ~ -1 in reverse step
    directory_listing.extend(directory_listing[-1:1:-1])

    with open(txt, "w") as fp:
        for directory in directory_listing:
            fp.write(f"{directory}\nduration 1\n")

        fp.write(f"{directory_listing[-1]}")

    # Write webm
    output = path_.with_suffix(".webm").absolute()
    output.unlink(missing_ok=True)
    (
        ffmpeg.input(txt.as_posix(), r=str(fps), f="concat", safe="0")
        .output(
            output.as_posix(),
            vcodec="libvpx-vp9",
            **{"pix_fmt": "yuva420p", "c:v": "libfvpx-vp9", "crf": "20", "b:v": "0"},
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

    print("target", args.files)

    img_1 = Image.open(args.files[0]).convert("RGBA")
    img_2 = Image.open(args.files[1]).convert("RGBA")

    generate_fade(img_1, img_2)
    generate_video()


if __name__ == "__main__":

    args = Args()

    parser = argparse.ArgumentParser(
        "Script generating cross-fade webm animation for 2 given image."
    )
    parser.add_argument(
        "-s",
        "--fade-step",
        metavar="INT",
        type=int,
        help="alpha value step size for fading effects",
    )
    parser.add_argument(
        "-f",
        "--fps-cap",
        metavar="INT",
        type=int,
        help="Sets hard limit on frame rate.",
    )
    parser.add_argument("files", nargs=2, type=pathlib.Path, help="Path to image")

    # Load config and write into args singleton
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

    finally:
        # clear temp
        if temp.exists():
            for file in temp.iterdir():
                file.unlink()

        temp.unlink(missing_ok=True)
