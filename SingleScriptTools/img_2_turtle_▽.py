"""
Generates hardcoded turtle drawing script drawing contour out of image.

![Example](readme_res/img_2_turtle.webp)

:Author: jupiterbjy@gmail.com
"""

import pathlib
import textwrap
from argparse import ArgumentParser
from typing import List, Sequence, Tuple

try:
    import cv2
    import numpy as np
    from PIL import Image
except ImportError:
    # install modules
    import pip
    for module in ("opencv-python", "numpy", "pillow"):
        pip.main(["install", module])

    import cv2
    import numpy as np
    from PIL import Image


MIN_VERTEX_TO_DRAW = 2


class CannyPreviewer:
    """Shows preview GUI where you can adjust thresholds"""

    def __init__(self, img_path, init_threshold=(10, 255)):
        self.threshold = init_threshold
        self.original_img = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2GRAY)
        self._win_name = "Threshold adjust - Close once confirmed"

        # cv2.WINDOW_AUTOSIZE
        cv2.namedWindow(self._win_name, cv2.WINDOW_AUTOSIZE)
        cv2.createTrackbar("Threshold 2", self._win_name, 255, 255, self.update_threshold_2)
        cv2.createTrackbar("Threshold 1", self._win_name, 255, 255, self.update_threshold_1)
        # cv2.createButton("Generate", self.on_button_press)

        cv2.resizeWindow(self._win_name, 600, 600)
        self.trigger_preview_update()

    def wait_for_value(self):
        """Waits until window is closed then returns thresholds"""
        cv2.waitKey()

        print("Using threshold", self.threshold)
        return self.threshold

    def update_threshold_1(self, val):
        self.threshold = int(val * 255 / 100), self.threshold[1]
        self.trigger_preview_update()

    def update_threshold_2(self, val):
        self.threshold = self.threshold[0], int(val * 255 / 100)
        self.trigger_preview_update()

    def trigger_preview_update(self):
        ret, threshold = cv2.threshold(self.original_img, *self.threshold, cv2.THRESH_OTSU)
        cv2.imshow(self._win_name, threshold)


def extract_contour(image_path: pathlib.Path, th_low, th_high) -> List[Sequence[Tuple[int, int]]]:
    """Extract outline points from image

    Args:
        image_path: path of image
        th_low: low threshold for contour
        th_high: high threshold for contour

    Returns:
        List of Contours - each contours contains coordinates required for contour.
    """

    source_img = cv2.imread(image_path.as_posix())
    # base = cv2.Canny(source_img, th_low, th_high)
    gray = cv2.cvtColor(source_img, cv2.COLOR_BGR2GRAY)
    ret, base = cv2.threshold(gray, th_low, th_high, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    contours, hierarchy = cv2.findContours(base, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_KCOS)

    # squeeze unnecessary dim and multiply contours to multiply resolutions
    squeezed = [np.squeeze(cnt, axis=1) for cnt in contours]

    # convert to tuple & apply multiplier
    converted = [
        [(x, y) for x, y in contour]
        for contour in squeezed if len(contour) >= MIN_VERTEX_TO_DRAW
    ]
    return converted


def save_script(image_path: pathlib.Path, image_dim, contours: Sequence[Sequence[Tuple[int, int]]]):
    """Save hard coded turtle code as image_name.py"""

    width, height = image_dim
    offset_x = width // 2
    offset_y = height // 2

    header = """
    import turtle
    
    width = {}
    height = {}
    offset_x = {}
    offset_y = {}
    
    screen = turtle.Screen()
    screen.setup(width, height, -offset_x, -offset_y)
    screen.delay(0)

    # create turtle
    pen = turtle.RawTurtle(screen.getcanvas())
    pen.width(2)
    
    # pen speedup
    pen.speed(0)
    screen.tracer(0)
    
    """
    header = header.format(width, height, offset_x, offset_y)
    header = textwrap.dedent(header)

    footer = "\n\nscreen.exitonclick()\n"

    contour_header = """
    pen.up()
    pen.goto({}, {})
    pen.down()
    """
    contour_header = textwrap.dedent(contour_header)

    contour_mid = "pen.goto({}, {})\n"

    # prep output file
    file = pathlib.Path(image_path.stem + ".py")

    # write to file
    with file.open("wt") as fp:

        fp.write(header)

        for idx_, start_points in enumerate(contours):

            # Could use collections.deque and rotate - but this is simpler.
            end_points = [*start_points[1:], start_points[0]]

            # write start pos
            fp.write(contour_header.format(start_points[0][0] - offset_x, offset_y - start_points[0][1]))

            # write vertex
            for end_x, end_y in end_points:
                fp.write(contour_mid.format(end_x - offset_x, offset_y - end_y))

        # write footer to keep screen alive
        fp.write(footer)


def main(img_path: pathlib.Path):

    # get threshold value
    viewer = CannyPreviewer(args.file.as_posix())

    # get img dim
    image = Image.open(img_path)

    # get contour
    contours = extract_contour(img_path, *viewer.wait_for_value())

    # save as script
    save_script(img_path, image.size, contours)

    # contour_to_turtle(image.size, contours)


if __name__ == '__main__':

    parser = ArgumentParser(
        "Script generating turtle image."
    )
    parser.add_argument("file", type=pathlib.Path, help="Path to image")

    args = parser.parse_args()

    main(args.file)
