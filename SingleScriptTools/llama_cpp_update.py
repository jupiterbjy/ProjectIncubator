"""
Dumb script to fetch newest llama-cpp prebuilt binaries

:Author: jupiterbjy@gmail.com
"""

import urllib.request
import json
import zipfile
import pathlib
import tempfile
import shutil
import argparse


# --- Config ---

ROOT = pathlib.Path(__file__).parent

# File used to store build version
VERSION_FILE_NAME = "llama-cpp-version.txt"

URL = "https://api.github.com/repos/ggml-org/llama.cpp/releases/latest"

# Download file's tail & destination dir name
FILE_DEST_MAP: dict[str, str] = {
    # "macos-arm64.tar.gz": "cpu",
    # "macos-x64.tar.gz": "cpu",
    # "ubuntu-vulkan-x64.tar.gz": "vulkan",
    # "ubuntu-x64.tar.gz": "cpu",
    # "win-cpu-arm64.zip": "cpu",
    "win-cpu-x64.zip": "cpu",
    # "win-cuda-12.4-x64.zip": "cuda12",
    # "win-cuda-13.1-x64.zip": "cuda13",
    "win-hip-radeon-x64.zip": "hip",
    # "win-opencl-adreno-arm64.zip": "opencl-adreno",
    # "win-sycl-x64.zip": "sycl",
    "win-vulkan-x64.zip": "vulkan",
}

# Memo
r"""
{
  ...
  "tag_name": "b7898",
  "name": "b7898",
  "draft": false,
  "immutable": false,
  "prerelease": false,
  "created_at": "2026-01-31T05:14:20Z",
  "updated_at": "2026-01-31T07:17:57Z",
  "published_at": "2026-01-31T07:16:51Z",
  "assets": [
    {
      ...
      "name": "llama-b7898-bin-win-vulkan-x64.zip",
      ...
      "browser_download_url": "..."
    },
    ...
  ]
}

cudart-llama-bin-win-cuda-12.4-x64.zip
cudart-llama-bin-win-cuda-13.1-x64.zip
llama-b7898-bin-310p-openEuler-aarch64.tar.gz
llama-b7898-bin-310p-openEuler-x86.tar.gz
llama-b7898-bin-910b-openEuler-aarch64-aclgraph.tar.gz
llama-b7898-bin-910b-openEuler-x86-aclgraph.tar.gz
llama-b7898-bin-macos-arm64.tar.gz
llama-b7898-bin-macos-x64.tar.gz
llama-b7898-bin-ubuntu-s390x.tar.gz
llama-b7898-bin-ubuntu-vulkan-x64.tar.gz
llama-b7898-bin-ubuntu-x64.tar.gz
llama-b7898-bin-win-cpu-arm64.zip
llama-b7898-bin-win-cpu-x64.zip
llama-b7898-bin-win-cuda-12.4-x64.zip
llama-b7898-bin-win-cuda-13.1-x64.zip
llama-b7898-bin-win-hip-radeon-x64.zip
llama-b7898-bin-win-opencl-adreno-arm64.zip
llama-b7898-bin-win-sycl-x64.zip
llama-b7898-bin-win-vulkan-x64.zip
llama-b7898-xcframework.zip
"""


# --- Logics ---


def get_local_version(root: pathlib.Path) -> int:
    try:
        version_file = root / VERSION_FILE_NAME
        return int(version_file.read_text("utf8")) if version_file.exists() else 0
    except ValueError:
        return 0


def workload(
    root: pathlib.Path, tgt_file_prefix: str, temp_dir: pathlib.Path, asset: dict
):
    name = asset["name"]

    if not name.startswith(tgt_file_prefix):
        return

    tail = name[len(tgt_file_prefix) :]

    if tail not in FILE_DEST_MAP:
        return

    dl_path = temp_dir / (FILE_DEST_MAP[tail] + ".zip")
    dest_path = root / FILE_DEST_MAP[tail]

    if dest_path.exists():
        print(f"Removing existing directory {dest_path}")
        shutil.rmtree(dest_path)

    size = 0
    with (
        dl_path.open("wb") as fp,
        urllib.request.urlopen(asset["browser_download_url"]) as resp,
    ):
        while data := resp.read(32768):
            size += len(data)
            print(f"Downloading {tail} - {size} B", end="\r")
            fp.write(data)

        print(f"Downloaded  {tail} - {size} B")

    print(f"Extracting  {tail}")
    zipfile.ZipFile(dl_path).extractall(dest_path)

    dl_path.unlink()


def fetch_latest_releases(dest: pathlib.Path):

    parsed = json.loads(urllib.request.urlopen(URL).read())
    version = int(parsed["tag_name"].removeprefix("b"))

    if get_local_version(dest) >= version:
        print(f"Already up to date. (b{version})")
        return

    tgt_file_prefix = f"llama-b{version}-bin-"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = pathlib.Path(temp_dir)

        for asset in parsed["assets"]:
            workload(dest, tgt_file_prefix, temp_dir, asset)

    # update version last
    (dest / VERSION_FILE_NAME).write_text(str(version), "utf8")


if __name__ == "__main__":
    _parser = argparse.ArgumentParser()

    _parser.add_argument(
        "-d",
        "--destination",
        type=pathlib.Path,
        default=ROOT,
        help="Destination directory to extract binaries to",
    )

    _args = _parser.parse_args()

    fetch_latest_releases(_args.destination)
