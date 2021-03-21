from __future__ import annotations

import pathlib
import json
import trio


class ClippedImage:
    def __init__(self, image_path, thumbnail_path, json_path):
        self.image_path = image_path
        self.thumb_path = thumbnail_path
        self.dimension = self.get_capture_point(json_path)

        # seems like it's thumbnail file has it's own designated dimensions.

    @staticmethod
    def get_capture_point(json_str_path: str):
        with open(json_str_path) as fp:
            data = json.loads(fp.read())

        return data['clipPoints'][2]

    @property
    def get_image_data(self):
        with open(self.image_path, 'rb') as fp:
            return fp.read()

    @property
    def get_thumbnail_data(self):
        with open(self.image_path, 'rb') as fp:
            return fp.read()


