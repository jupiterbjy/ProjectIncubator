"""
Concept of Clipped Image class utilizing trio event loop for async load of thumbnails on kivy.

Apparently I hardcoded images and json, but will have to figure out that random file name.

One way would be grouping files by creation date within certain margin, and decide thumbnail by size.
"""


from __future__ import annotations

import pathlib
import json
import trio


class ClippedImage:
    def __init__(self, image_path: pathlib.Path, thumbnail_path: pathlib.Path, json_path: pathlib.Path):
        self.image_path = trio.Path(image_path)
        self.thumb_path = trio.Path(thumbnail_path)
        self.dimension = self._get_capture_point(json_path)

        # seems like it's thumbnail file has it's own designated dimensions.

    @staticmethod
    def _get_capture_point(json_str_path: pathlib.Path):
        with open(json_str_path) as fp:
            data = json.loads(fp.read())

        return data['clipPoints'][2]

    @property
    async def get_image_data(self):
        return await self.image_path.read_bytes()

    @property
    async def get_thumbnail_data(self):
        return await self.thumb_path.read_bytes()

    async def delete_clip(self):
        pass
        # Not sure if it's possible, can't see API for removing things.


async def driver():
    common_path = "sample"
    paths_1 = ["{D1904FA5-2229-4AA6-98C7-089627EA930C}.png",
               "{EB054D81-209C-47D6-AB27-6B2786021506}.png",
               "{176C28C1-0BD8-4B30-A804-0AE1F469A675}.json"]

    paths_2 = ["{75434B73-9EF3-492C-8686-C180CBB5B5E3}.png",
               "{8EBA960C-09D4-4F5C-A926-AD6A13D37838}.png",
               "{7D423F0E-DFD5-421E-AFF0-78374F4E82CD}.json"]

    image_ref_1 = ClippedImage(*(pathlib.Path(common_path).joinpath(path_) for path_ in paths_1))
    image_ref_2 = ClippedImage(*(pathlib.Path(common_path).joinpath(path_) for path_ in paths_2))

    def wrapper(image_ref: ClippedImage):
        async def load_image():
            img_bytes = await image_ref.get_image_data
            tb_bytes = await image_ref.get_image_data
            dimensions = image_ref.dimension
            print(len(img_bytes), len(tb_bytes), dimensions)

        return load_image

    async with trio.open_nursery() as nursery:
        nursery.start_soon(wrapper(image_ref_1))
        nursery.start_soon(wrapper(image_ref_2))


if __name__ == '__main__':
    trio.run(driver)
