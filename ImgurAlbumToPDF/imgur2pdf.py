"""
Demo code downloading and converting imgur album to PDF
Written on 3.10, but will probably work for python 3.8~3.10.

---

Licence: MIT License
Author: jupiterbjy@gmail.com
"""

from typing import TypedDict, Sequence, Union, List, Tuple
from io import BytesIO
import argparse
import pathlib

import trio
import httpx
from tqdm import tqdm
from PIL import Image


class SkipDownload(Exception):
    """
    Exception type for passing reason of failure and image in case it's needed.
    """

    def __init__(self, image: "ImgurImage", reason):
        self.image = image
        self.reason = reason

    def __str__(self):
        return f"Skipped {self.image['id']}, reason: {self.reason}"


class ImgurImage(TypedDict):
    """
    Type hint for https://api.imgur.com/models/album
    """

    id: str
    title: Union[None, str]
    description: Union[None, str]
    datetime: int
    type: str
    animated: bool
    width: int
    height: int
    size: int
    views: int
    bandwidth: int
    link: str


class ImgurAlbum(TypedDict):
    """
    Type hint for https://api.imgur.com/models/album
    """

    id: str
    title: str
    description: Union[None, str]
    datetime: int
    cover: str
    account_url: str
    account_id: int
    privacy: str
    layout: str
    views: int
    link: str
    images_count: int
    images: Sequence[ImgurImage]


class ImgurClient:
    """
    Imgur async client
    """

    def __init__(self, client_id, max_threads):
        self.http_client = httpx.AsyncClient()
        self.max_threads = trio.CapacityLimiter(max_threads)

        self.header = {"Authorization": f"Client-ID {client_id}"}

    async def download_image(self, image: ImgurImage) -> Image:
        """
        Downloads image and return it as pillow.Image.
        GIF will be converted into single frame PNG.

        Args:
            image: album hash/id

        Returns:
            pillow Image
        """

        if "image" not in image["type"]:
            raise SkipDownload(image, "Not an Image")

        resp = await self.http_client.get(image["link"])
        byte_io = BytesIO(resp.content)

        return Image.open(byte_io)

    async def get_album(self, album_id) -> ImgurAlbum:
        """
        Fetch album response of given album id.

        Args:
            album_id: album hash/id

        Returns:
            Album model

        Raises:
            HTTPStatusError: When provided Client ID is wrong, or album is unreachable.
        """

        resp = await self.http_client.get(
            f"https://api.imgur.com/3/album/{album_id}", headers=self.header
        )
        resp.raise_for_status()

        return resp.json()["data"]

    async def download_album(self, album: ImgurAlbum) -> List[Tuple[ImgurImage, Image.Image]]:
        """
        Downloads album. GIF will be converted into single frame PNG.

        Args:
            album: Album model

        Returns:
            List of image model & image pairs.
        """

        count = album['images_count']
        image_table = {}
        actual_successful_downloads = 0
        skipped_images = []
        progress_bar = tqdm(desc="Downloading Images", total=count)

        # define task ----
        async def download_task(idx_: int, image_model_: ImgurImage):
            """
            Stores image model & image pair with given index in dictionary.

            Args:
                idx_: Index of this image model
                image_model_: ImgurImage
            """

            nonlocal actual_successful_downloads

            try:
                image = await self.download_image(image_model_)

            except SkipDownload as err:
                skipped_images.append(str(err))
                return

            image_table[idx_] = image_model_, image

            # update counters
            actual_successful_downloads += 1
            progress_bar.update()

        # ----------------

        # start nursery, gotta cuddle that tasks
        async with trio.open_nursery() as nursery:

            for idx, image_model in enumerate(album["images"]):

                # limit maximum concurrent tasks
                async with self.max_threads:
                    nursery.start_soon(download_task, idx, image_model)

        progress_bar.close()
        print(f"Saved {actual_successful_downloads} out of {count}")

        if skipped_images:
            print(f"Skipped ID(s):", *skipped_images, sep="\n")

        return [img for idx, img in sorted(image_table.items(), key=lambda x: x[0])]

    async def aclose(self):
        """
        Closes HTTPX client gracefully.
        """
        await self.http_client.aclose()


def convert_rgba_to_rgb_gen(
    images: Sequence[Tuple[ImgurImage, Image.Image]], background_color=(255, 255, 255)
):
    """
    Converts RGBA image into RGB.

    Args:
        images: Sequence of Image model & pillow Image pair
        background_color: Background color to be used as background

    Yields:
        converted image
    """

    # type hinting manually because it's wrapped in tqdm and not working.
    image_model: ImgurImage
    image: Image.Image

    fail_list = []

    for image_model, image in tqdm(images, "Removing Transparency"):

        # imgur only have JPEG, PNG, APNG, GIF, TIFF, support.
        if image_model['type'] == "image/jpeg":
            yield image
            continue

        image = image.convert("RGBA")
        template = Image.new("RGBA", image.size, background_color)

        try:
            template.alpha_composite(image)
        except ValueError as err:
            fail_list.append(f"Image {image_model['id']} failed to merge, reason: {str(err)}")
            continue

        yield template.convert("RGB")

    print(*fail_list, sep="\n")


async def main_task():
    """
    Main task to wrap asynchronous contexts.
    """

    client = ImgurClient(args.client_id, args.threads)

    print("Album list:", *args.urls, end="\n---\n")

    try:
        for album_id in args.urls:
            album = await client.get_album(album_id)
            images = await client.download_album(album)

            if not images:
                print(f"No images to save for album {album['id']}\n", end="\n---\n")
                continue

            convert_iterator = convert_rgba_to_rgb_gen(images)

            first_image = next(convert_iterator)
            other_images = list(convert_iterator)

            print("Saving PDF")

            destination = args.output.joinpath(album["id"] + ".pdf")
            first_image.save(destination, save_all=True, append_images=other_images)

            print(f"Album {album['id']} saved.", end="\n---\n")

    finally:
        # make sure to close the connection
        await client.aclose()


if __name__ == "__main__":
    # parse args
    parser = argparse.ArgumentParser("Imgur album to PDF downloader")

    parser.add_argument(
        "-c",
        "--client_id",
        type=str,
        required=True,
        help="Imgur Client ID - get one from https://api.imgur.com/oauth2/addclient",
    )

    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=5,
        help="Limits the number of concurrent downloads. Defaults to 5.",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        default=pathlib.Path(__file__).parent,
        help="PDF Output directory",
    )

    parser.add_argument(
        "urls",
        metavar="URL",
        type=str,
        nargs="+",
        help="Public Imgur album URLs or ID.",
    )

    args = parser.parse_args()

    # convert provided URL to id if not already is.
    args.urls = [url.split("/")[-1] for url in args.urls]

    trio.run(main_task)
