"""
Concept of Clipped Image class utilizing trio event loop for async load of thumbnails on kivy.
"""


from __future__ import annotations

from typing import Generator, Tuple
import pathlib
import json

from PIL import Image
import trio


class ClippedImage:
    def __init__(self, image_path: pathlib.Path, thumbnail_path: pathlib.Path, json_path: pathlib.Path):
        self.image_path = trio.Path(image_path)
        self.thumbnail_path = trio.Path(thumbnail_path)
        self.json_path = json_path
        self.dimension = self._get_capture_point(json_path)

        # seems like it's thumbnail file has it's own designated dimensions.

    def __repr__(self):
        return f"ClippedImage({str(self.image_path)}, {str(self.thumbnail_path)}, {self.json_path.as_posix()})"

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
        return await self.thumbnail_path.read_bytes()

    async def delete_clip(self):
        pass
        # Not sure if it's possible, can't see API for removing things.


def image_grouper(path_: pathlib.Path):
    # assuming there's no modification made on clipped caches!
    # That is, 3 files per clip, created within second
    # That means, I don't expect user to ever clip with less than one second interval.

    def n_group(iterable, group_unit: int) -> Generator[Tuple[pathlib.Path], None, None]:
        gen_instance = (item for item in iterable)

        while True:
            output = []

            try:
                for _ in range(group_unit):
                    output.append(next(gen_instance))
            except StopIteration:
                if not output:
                    return

            yield output

    ordered_dir_iterator = sorted(path_.iterdir(), key=lambda p: p.stat().st_ctime)

    for file_group in n_group(ordered_dir_iterator, 3):
        json_ = [f for f in file_group if f.suffix == ".json"][0]
        output_dict = {"json_path": json_}

        images = set(file_group) - {json_}

        for image_path in images:
            # Likelihood of getting exact thumbnail sized clip is low

            with open(image_path, 'rb') as fp:
                image: Image.Image = Image.open(fp)

                if (image.width, image.height) == (364, 180):
                    output_dict["thumbnail_path"] = image_path

                    image.close()
                    break

        output_dict["image_path"] = (images - {output_dict["thumbnail_path"]}).pop()
        yield output_dict


async def driver():
    common_path = "sample"
    img_1 = ["{EB054D81-209C-47D6-AB27-6B2786021506}.png",
             "{D1904FA5-2229-4AA6-98C7-089627EA930C}.png",
             "{176C28C1-0BD8-4B30-A804-0AE1F469A675}.json"]

    img_2 = ["{75434B73-9EF3-492C-8686-C180CBB5B5E3}.png",
             "{8EBA960C-09D4-4F5C-A926-AD6A13D37838}.png",
             "{7D423F0E-DFD5-421E-AFF0-78374F4E82CD}.json"]

    image_ref_1 = ClippedImage(*(pathlib.Path(common_path).joinpath(path_) for path_ in img_1))
    image_ref_2 = ClippedImage(*(pathlib.Path(common_path).joinpath(path_) for path_ in img_2))

    grouper_output = tuple(image_grouper(pathlib.Path("sample")))
    image_ref_1_auto, image_ref_2_auto = map(lambda x: ClippedImage(**x), grouper_output)

    assert repr(image_ref_1_auto) == repr(image_ref_1)
    assert repr(image_ref_2_auto) == repr(image_ref_2)

    #
    def wrapper(image_ref: ClippedImage):
        async def load_image():
            img_bytes = await image_ref.get_image_data
            tb_bytes = await image_ref.get_thumbnail_data
            dimensions = image_ref.dimension
            print(f"Image bytes: {len(img_bytes)}, Thumbnail bytes: {len(tb_bytes)}, Dimensions: {dimensions}")

        return load_image

    # Drive trio loop
    async with trio.open_nursery() as nursery:
        nursery.start_soon(wrapper(image_ref_1))
        nursery.start_soon(wrapper(image_ref_2))


if __name__ == '__main__':
    trio.run(driver)
