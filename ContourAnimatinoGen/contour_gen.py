import pathlib
from sys import argv
from typing import List

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


# PARAM -------------
fade_div_factor = 5
transparent = False
time_limit = 5
res_multiply = 4
threshold = (0, 100)
line_width = 3
# -------------------


root = pathlib.Path(__file__).parent.absolute()
temp = root.joinpath("temp_img")
fade_factor = 254 // fade_div_factor
# use_canny = True


assert isinstance(res_multiply, int), "Should be integer"

try:
    file = argv[1]
except IndexError:
    print("No files provided.")

if temp.exists():
    for path in temp.iterdir():
        path.unlink(missing_ok=True)


print(f"Fade Frames: {fade_factor} / Transparent: {transparent} / Duration: {time_limit} / Resolution: {res_multiply}x")


def generate_fade(source_img: Image.Image, number_last, pad_size):

    if transparent:
        def load(image):
            return image
    else:
        def load(image: Image.Image):
            return image.convert("RGBA")

    if transparent:
        def output(image):
            return image
    else:
        output = remove_alpha

    for idx, alpha in enumerate(tqdm(range(254, 0, -fade_div_factor), "Generating Fade")):

        copied: Image.Image = load(source_img.copy())
        copied2: Image.Image = source_img.copy()
        copied.putalpha(alpha)

        copied2.paste(copied, copied2)

        target_file = temp.joinpath(f"{str(idx + number_last).zfill(pad_size)}.png")

        output(copied2).save(target_file)


def generate_images(contours: List[np.array]):

    # get size
    concat = np.concatenate(contours, axis=0)
    max_dim = np.amax(concat, axis=0)

    # prepare image
    img = Image.new("RGBA", tuple(max_dim))
    idx = 0

    # check digit
    digit = len(str(len(contours) + fade_factor))

    draw = ImageDraw.Draw(img)

    if transparent:
        def method(image):
            return image
    else:
        method = remove_alpha

    for idx, contour in enumerate(tqdm(contours, "Drawing Contours")):
        range_1 = tuple(range(len(contour)))
        range_2 = [*range_1[1:], 0]

        for dot_1, dot_2 in zip(range_1, range_2):

            draw.line(
                (tuple(contour[dot_1]), tuple(contour[dot_2])),
                fill="#00e5e5ff",
                width=line_width,
            )

        target_file = temp.joinpath(f"{str(idx).zfill(digit)}.png")

        method(img).save(target_file)

    # Generate fade images
    generate_fade(img, idx + 1, digit)


def remove_alpha(image):
    bg = Image.new("RGB", image.size)
    bg.paste(image, mask=image.split()[3])
    return bg


def generate_video():
    path_ = pathlib.Path(file)
    fps = len(tuple(temp.iterdir())) // time_limit

    print("Framerate:", fps)

    txt = temp.joinpath("files.txt")

    # create txt file for input
    with open(txt, "w") as fp:
        fp.write("\n".join(f"file {path_.as_posix()}" for path_ in temp.iterdir() if path_.suffix == ".png"))

    if transparent:
        output = path_.with_suffix(".webm").absolute()
        output.unlink(missing_ok=True)
        (
            ffmpeg
            .input(txt.as_posix(), r=str(fps), f="concat", safe="0")
            .output(output.as_posix(), vcodec="libvpx", **{"pix_fmt": "yuva420p", "auto-alt-ref": "0"}, )
            .run()
        )
    else:
        output = path_.with_suffix(".mp4").absolute()
        output.unlink(missing_ok=True)
        (
            ffmpeg
            .input(txt.as_posix(), r=str(fps), f="concat", safe="0")
            .output(output.as_posix())
            .run()
        )


def main():
    frame = cv2.imread(file)
    print("target", file)
    
    # if use_canny:
    base = cv2.Canny(frame, *threshold)
    # else:
    #     img_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #     _, base = cv2.threshold(img_grey, 200, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(
        base, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )

    # squeeze and multiply contours
    squeezed = [np.squeeze(cnt, axis=1) * [res_multiply, res_multiply] for cnt in contours]

    generate_images(squeezed)

    generate_video()


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(err)
        input()
        raise

