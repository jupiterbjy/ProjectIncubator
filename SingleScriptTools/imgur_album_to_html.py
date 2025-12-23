"""
Downloads imgur album(with descriptions) and converts into html with concurrent downloading.

Downloads all image/videos and generates:

- `online_lookup.html`: Uses imgur's original link, a workaround for sharing private album since imgur blocked it
- `offline_lookup.html`: Uses downloaded image/video paths


Example output:
```text
Album list: ['abcdefg']
---
[abcdefg] Downloading 413 images
[4uwdbyL] Downloaded
...
[qvuPRUh] File already exists, skipping
[abcdefg] Generating HTML for standalone HTML share
[abcdefg] Generating HTML for lookup
[abcdefg] All done
```

![](readme_res/imgur_album_to_html.png)

:Author: jupiterbjy@gmail.com
"""

import asyncio
import json
import urllib.parse
from typing import TypedDict, Sequence, Union
import argparse
import pathlib

import httpx


# --- Config ---

ROOT = pathlib.Path(__file__).parent / "imgur_album_downloads"
ROOT.mkdir(exist_ok=True)


_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
</head>
<body>
<h1>{title}</h1>
{body}
</body>
</html>
""".strip()

_HTML_IMG_TEMPLATE = """
<hr>
<br>
<img src="{link}" alt="{id}" height=500px>
<br>
{description}
<br>
<br>
"""

_HTML_VIDEO_TEMPLATE = """
<hr>
<br>
<video height=500px controls>
    <source src="{link}" type="{type}">
    Your browser does not support the video tag.
</video>
<br>
{description}
<br>
<br>
"""


# --- Utilities ---


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


def _generate_html(album: ImgurAlbum) -> str:
    """Generate HTML for quick lookup.

    Args:
        album: Album model

    Returns:
        HTML text
    """

    parts = []
    for image in album["images"]:
        if image["type"].startswith("video"):
            parts.append(
                _HTML_VIDEO_TEMPLATE.format(
                    link=image["link"],
                    type=image["type"],
                    description=(
                        image["description"].replace("\n", "<br>")
                        if image["description"]
                        else ""
                    ),
                )
            )
        else:
            parts.append(
                _HTML_IMG_TEMPLATE.format(
                    link=image["link"],
                    id=image["id"],
                    description=(
                        image["description"].replace("\n", "<br>")
                        if image["description"]
                        else ""
                    ),
                )
            )

    return _HTML_TEMPLATE.format(
        title=f"{album['title']}({album['id']})", body="".join(parts)
    )


# --- Logics ---


class ImgurClient:
    """
    Imgur async client
    """

    def __init__(self, client_id, max_threads):
        self.max_threads = max_threads
        self.http_client = httpx.AsyncClient()

        self.auth_header = {"Authorization": f"Client-ID {client_id}"}

        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
        self.http_client.headers.update({"User-Agent": self.user_agent})

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
            f"https://api.imgur.com/3/album/{album_id}", headers=self.auth_header
        )
        resp.raise_for_status()

        return resp.json()["data"]

    async def download_image(self, image: ImgurImage, root_path: pathlib.Path):
        """
        Download image. Yeah.

        Args:
            image: album hash/id
            root_path: Subdirectory to save image to

        Raises:
            httpx.HTTPStatusError: When provided Client ID is wrong, or album is unreachable
        """

        # parse url to get file name, since file name field can be empty or non-unique
        path = root_path / urllib.parse.urlparse(image["link"]).path.lstrip("/")

        # if exists skip
        if path.exists():
            print(f"[{image['id']}] File already exists, skipping")
            return

        # save json response
        (root_path / f"{image['id']}.json").write_text(
            json.dumps(image, indent=2), "utf-8"
        )

        # download, I don't think it'll be larger than ram...
        resp = await self.http_client.get(image["link"])
        resp.raise_for_status()

        path.write_bytes(resp.content)

        print(f"[{image['id']}] Downloaded")

    async def download_album(self, album: ImgurAlbum, root_path: pathlib.Path):
        """
        Downloads album.

        Args:
            album: Album model
            root_path: Subdirectory to save album to

        Raises:
            httpx.HTTPStatusError: When provided Client ID is wrong, or album is unreachable
        """

        root = root_path / album["id"]
        root.mkdir(exist_ok=True)

        # save response
        (root_path / f"{album['id']}.json").write_text(
            json.dumps(album, indent=2), "utf-8"
        )

        # initiate download for each image
        stack = list(album["images"])

        # since async != parallel, no need for queue
        async def download_task():
            while stack:
                await self.download_image(stack.pop(), root)

        print(f"[{album['id']}] Downloading {len(stack)} images")

        # TODO: add failsafe
        # start download tasks
        async with asyncio.TaskGroup() as tg:
            for idx in range(self.max_threads):
                tg.create_task(download_task())

        print(f"[{album['id']}] Generating HTML for standalone HTML share")

        (root_path / "online_lookup.html").write_text(_generate_html(album), "utf-8")

        print(f"[{album['id']}] Generating HTML for lookup")

        # replace links to the dir path, since I'm too lazy to make new parameter on function
        for image in album["images"]:
            image["link"] = (
                f"{album['id']}/{urllib.parse.urlparse(image["link"]).path.lstrip("/")}"
            )

        (root_path / "offline_lookup.html").write_text(_generate_html(album), "utf-8")

        print(f"[{album['id']}] All done")

    async def aclose(self):
        """
        Closes HTTPX client gracefully.
        """
        await self.http_client.aclose()


async def main_task(
    client_id: str, urls: Sequence[str], output: pathlib.Path, max_threads: int
) -> None:
    """
    Main task to wrap asynchronous contexts.
    """

    client = ImgurClient(client_id, max_threads)

    # convert provided URL to id if not already is.
    album_ids = [url.split("/")[-1] for url in urls]

    print("Album list:", album_ids, end="\n---\n")

    try:
        for album_id in album_ids:
            album = await client.get_album(album_id)
            await client.download_album(album, output)

    finally:
        await client.aclose()


if __name__ == "__main__":
    # parse args
    parser = argparse.ArgumentParser("Imgur album to HTML downloader")

    parser.add_argument(
        "-c",
        "--client_id",
        type=str,
        required=True,
        default="",
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
        default=ROOT,
        help="PDF Output directory",
    )

    parser.add_argument(
        "urls",
        metavar="URL",
        type=str,
        nargs="+",
        help="Public Imgur album URLs or ID.",
    )

    _args = parser.parse_args()

    asyncio.run(
        main_task(_args.client_id, _args.urls, _args.output.resolve(), _args.threads)
    )
