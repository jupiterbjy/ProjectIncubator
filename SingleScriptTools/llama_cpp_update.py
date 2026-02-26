"""
Dumb script to fetch newest llama-cpp prebuilt binaries

:Author: jupiterbjy@gmail.com
"""

import urllib.request
import json
import zipfile
import tarfile
import pathlib
import tempfile
import shutil
import argparse
import platform


# --- Config ---

ROOT = pathlib.Path(__file__).parent

# File used to store build version
VERSION_FILE_NAME = "llama-cpp-version.txt"

URL = "https://api.github.com/repos/ggml-org/llama.cpp/releases/latest"

# Download file's tail & destination dir name
FILE_DEST_MAP: dict[str, str] = {
    "Darwin": {
        "macos-arm64.tar.gz": "cpu",
        "macos-x64.tar.gz": "cpu",
    },
    "Windows": {
        # "win-cpu-arm64.zip": "cpu",
        "win-cpu-x64.zip": "cpu",
        # "win-cuda-12.4-x64.zip": "cuda12",
        # "win-cuda-13.1-x64.zip": "cuda13",
        # "win-hip-radeon-x64.zip": "hip",
        # "win-opencl-adreno-arm64.zip": "opencl-adreno",
        # "win-sycl-x64.zip": "sycl",
        "win-vulkan-x64.zip": "vulkan",
    },
    "Linux": {
        "ubuntu-vulkan-x64.tar.gz": "vulkan",
        "ubuntu-x64.tar.gz": "cpu",
    }
}[platform.system()]

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


# --- Utils ---

def unnest_dir(dir_path: pathlib.Path):
    """Unnest content of given path, basically moving them to parent's"""

    parent = dir_path.parent

    try:
        for sub_path in dir_path.iterdir():
            sub_path.move_into(parent)
    
    except AttributeError:
        # seems like pathlib.move_into was added in 3.14, yet I use debian

        parent_str_path = parent.as_posix()

        for sub_path in dir_path.iterdir():
            shutil.move(sub_path.as_posix(), parent_str_path)
    
    dir_path.rmdir()


def unpack_archive(archive_path: pathlib.Path, dest_path: pathlib.Path):
    """Some wrapper for zipfile & tarfile. yeah that's it"""

    match archive_path.suffix:
        # assumming it's .tar.gz
        case ".gz":
            with tarfile.open(archive_path, "r:gz") as archive:
                archive.extractall(dest_path)
            
            # linux archive has extra nested path in `llama-b8147` format,
            # so unnest it
            nested_dir: pathlib.Path = next(dest_path.iterdir())
            
            assert nested_dir.is_dir() and nested_dir.stem.startswith("llama-b"), (
                f"Expected nested directory of `llama-bxxxx` format, got `{nested_dir}`"
            )

            unnest_dir(nested_dir)
        
        case ".zip":
            with zipfile.ZipFile(archive_path) as archive:
                archive.extractall(dest_path)


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

    dl_path: pathlib.Path = temp_dir / tail
    extension = dl_path.suffix

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
    unpack_archive(dl_path, dest_path)

    print(f"Deleting    {tail}")
    dl_path.unlink()


def fetch_latest_releases(dest: pathlib.Path, force_redownload: bool):

    parsed = json.loads(urllib.request.urlopen(URL).read())
    version = int(parsed["tag_name"].removeprefix("b"))

    if not force_redownload and get_local_version(dest) >= version:
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
    _parser.add_argument(
        "-f",
        "--force-redownload",
        action="store_true",
        help="Redownload regardless of existing version check",
    )


    _args = _parser.parse_args()

    fetch_latest_releases(_args.destination, _args.force_redownload)
