import pathlib
from io import BytesIO

from PIL import Image

# TODO: reject non png

ROOT = pathlib.Path(__file__).parent
TEMPLATE_IMG_PATH = ROOT.joinpath("template.png")
assert TEMPLATE_IMG_PATH.exists()

TEMPLATE_TOP_LEFT_START = (115, 237)
SQUARE_SIZE = 155
ANGLE = 3.23


def rotate_image(image: Image, angle: float) -> Image:
    return image.rotate(angle, expand=True)


def overlay_image(image: Image, background_image: Image, offset_x, offset_y) -> Image:

    background_image.paste(image, (offset_x, offset_y), image)

    return background_image


def make_square(image: Image):
    width, height = image.size

    # check if already square
    if width == height:
        return image

    side = max(height, width)

    temp = Image.new(image.mode, (side, side))

    if width < height:
        temp.paste(image, ((side - width) // 2, 0), image)
    else:
        temp.paste(image, (0, (side - height) // 2), image)

    return temp


def resize_image(image: Image, pixel_length) -> Image:
    """
    Only accepts squares.
    """
    
    return image.resize((pixel_length, pixel_length))


def main(bg_img_bytes: BytesIO, fore_img_bytes: BytesIO):
    
    img = Image.open(bg_img_bytes)
    img.convert("RGBA")
    
    template = Image.open(fore_img_bytes)
    img.convert("RGBA")

    foreground = resize_image(rotate_image(make_square(img), ANGLE), SQUARE_SIZE)

    final_img = overlay_image(foreground, template, *TEMPLATE_TOP_LEFT_START)
    final_img.save(ROOT.joinpath("output.png").as_posix())


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    #
    # parser.add_argument("image", type=pathlib.Path, help="Path to image")
    # parser.add_argument("angle", type=float, help="Angle of image rotation in clockwise")
    #
    # args = parser.parse_args()

    file = BytesIO(ROOT.joinpath("test.png").read_bytes())
    background_file = BytesIO(ROOT.joinpath("template.png").read_bytes())

    main(file, background_file)
