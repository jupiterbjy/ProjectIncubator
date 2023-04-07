"""
Simple code generating Contour animation-ish video out of image drag-n-drop.
Download GPL FFMPEG from https://github.com/BtbN/FFmpeg-Builds/releases/tag/latest

This adds GUI addon so that you can configure threshold without guessing

Author: jupiterbjy@gmail.com / nyarukoishi@gmial.com
"""

import pathlib
import argparse

import cv2

from contour_gen import main


class Args:
    file: pathlib.Path


class CannyPreviewer:
    """Shows preview GUI where you can adjust thresholds"""

    def __init__(self, img_path, init_threshold=(0, 0)):
        self.threshold = init_threshold
        self.original_img = cv2.imread(img_path)
        self._win_name = "Threshold adjust - Close once confirmed"

        cv2.namedWindow(self._win_name, cv2.WINDOW_AUTOSIZE)
        cv2.createTrackbar("Threshold 2", self._win_name, 0, 400, self.update_threshold_2)
        cv2.createTrackbar("Threshold 1", self._win_name, 0, 400, self.update_threshold_1)
        # cv2.createButton("Generate", self.on_button_press)
        self.trigger_preview_update()

    def wait_for_value(self):
        """Waits until window is closed then returns thresholds"""
        cv2.waitKey()

        print("Using threshold", self.threshold)
        return self.threshold

    def update_threshold_1(self, val):
        self.threshold = val, self.threshold[1]
        self.trigger_preview_update()

    def update_threshold_2(self, val):
        self.threshold = self.threshold[0], val
        self.trigger_preview_update()

    def trigger_preview_update(self):
        edges = cv2.Canny(self.original_img, *self.threshold)
        mask = (edges != 0)[:, :, None].astype(self.original_img.dtype)

        cv2.imshow(self._win_name, self.original_img * mask)


if __name__ == '__main__':
    args = Args()

    parser = argparse.ArgumentParser(
        "Script generating contour timelapse video for given image."
    )
    parser.add_argument("file", type=pathlib.Path, help="Path to image")

    args = parser.parse_args(namespace=args)

    viewer = CannyPreviewer(args.file.as_posix())
    main(args.file, viewer.wait_for_value(), 1)
