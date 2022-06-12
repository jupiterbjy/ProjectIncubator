from __future__ import annotations
from typing import Generator, Tuple, Union
import pathlib
import json

from PIL import Image
import trio


class ClippedImage:
    def __init__(self, image_path, thumbnail_path, json_path):
        image_path: Union[pathlib.Path, str]
        thumbnail_path: Union[pathlib.Path, str]
        json_path: Union[pathlib.Path, str]

        self.image_path = pathlib.Path(image_path)
        self.thumbnail_path = pathlib.Path(thumbnail_path)
        self.json_path = pathlib.Path(json_path)

        with open(json_path) as fp:
            data = json.loads(fp.read())
            self.dimension = data["clipPoints"][2]

        # seems like it's thumbnail file has it's own designated dimensions.

    def __repr__(self):
        return f"ClippedImage({str(self.image_path)}, {str(self.thumbnail_path)}, {self.json_path.as_posix()})"

    async def get_image_data(self):
        return await trio.Path(self.image_path).read_bytes()

    async def get_thumbnail_data(self):
        return await trio.Path(self.thumbnail_path).read_bytes()

    async def delete_clip(self):
        pass
        # Not sure if it's possible, can't see API for removing things.


def image_grouper_gen(path_: pathlib.Path) -> Generator[ClippedImage, None, None]:
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
        yield ClippedImage(**output_dict)
