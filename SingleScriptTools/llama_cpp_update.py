"""
Dumb script to fetch newest or specific llama-cpp release's prebuilt binaries

:Author: jupiterbjy@gmail.com
"""

import re
import urllib.request
import urllib.error
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

LATEST_URL = "https://api.github.com/repos/ggml-org/llama.cpp/releases/latest"

RELEASES_URL = "https://api.github.com/repos/ggml-org/llama.cpp/releases"

TAG_RELEASE_URL = "https://api.github.com/repos/ggml-org/llama.cpp/releases/tags"

# Download file config. Comment out to disable
FILE_DL_CONFIG: set[str] = {
    # macOS & android probably will not work at all
    "Darwin": {
        "macOS Apple Silicon (arm64)",
        # "macOS Intel (x64)",
    },
    "iOS": {
        "iOS XCFramework",
    },
    "Linux": {
        "Ubuntu x64 (CPU)",
        "Ubuntu x64 (Vulkan)",
        # "Ubuntu arm64 (Vulkan)",
        # "Ubuntu x64 (ROCm 7.2)",
        # "Ubuntu x64 (OpenVINO)",
        # "Ubuntu x64 (SYCL FP32)",
        # "Ubuntu x64 (SYCL FP16)",
    },
    "Android": {
        "Android arm64 (CPU)",
    },
    "Windows": {
        "Windows x64 (CPU)",
        # "Windows arm64 (OpenCL Adreno)",
        # "Windows x64 (CUDA 12)",
        # "Windows x64 (CUDA 13)",
        "Windows x64 (Vulkan)",
        # "Windows x64 (OpenVINO)",
        # "Windows x64 (SYCL)",
        # "Windows x64 (HIP)",
    },
}[platform.system()]

# Used to generate directory name from release name.
# uses whole name in snake case if not matched.
RUNTIME_DIR_NAME_PATTERN = re.compile(r"\(([\s\S]+?)\)")


# Memo
r"""
{
  ...
  "tag_name": "b9871",
  "target_commitish": "ef2d770117db45b05aa7ecd1b0acca36370c5470",
  "name": "b9871",
  "body": "VERY_LONG_MARKDOWN"
  ...
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

VERY_LONG_MARKDOWN:
**macOS/iOS:**
- [macOS Apple Silicon (arm64)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-macos-arm64.tar.gz)
- macOS Apple Silicon (arm64, KleidiAI enabled) [DISABLED](https://github.com/ggml-org/llama.cpp/pull/23780)
- [macOS Intel (x64)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-macos-x64.tar.gz)
- [iOS XCFramework](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-xcframework.zip)
**Linux:**
- [Ubuntu x64 (CPU)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-ubuntu-x64.tar.gz)
- [Ubuntu arm64 (CPU)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-ubuntu-arm64.tar.gz)
- [Ubuntu s390x (CPU)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-ubuntu-s390x.tar.gz)
- [Ubuntu x64 (Vulkan)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-ubuntu-vulkan-x64.tar.gz)
- [Ubuntu arm64 (Vulkan)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-ubuntu-vulkan-arm64.tar.gz)
- [Ubuntu x64 (ROCm 7.2)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-ubuntu-rocm-7.2-x64.tar.gz)
- [Ubuntu x64 (OpenVINO)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-ubuntu-openvino-2026.2.1-x64.tar.gz)
- [Ubuntu x64 (SYCL FP32)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-ubuntu-sycl-fp32-x64.tar.gz)
- [Ubuntu x64 (SYCL FP16)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-ubuntu-sycl-fp16-x64.tar.gz)
**Android:**
- [Android arm64 (CPU)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-android-arm64.tar.gz)
**Windows:**
- [Windows x64 (CPU)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-win-cpu-x64.zip)
- [Windows arm64 (CPU)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-win-cpu-arm64.zip)
- [Windows arm64 (OpenCL Adreno)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-win-opencl-adreno-arm64.zip)
- [Windows x64 (CUDA 12)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-win-cuda-12.4-x64.zip) - [CUDA 12.4 DLLs](https://github.com/ggml-org/llama.cpp/releases/download/b9871/cudart-llama-bin-win-cuda-12.4-x64.zip)
- [Windows x64 (CUDA 13)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-win-cuda-13.3-x64.zip) - [CUDA 13.3 DLLs](https://github.com/ggml-org/llama.cpp/releases/download/b9871/cudart-llama-bin-win-cuda-13.3-x64.zip)
- [Windows x64 (Vulkan)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-win-vulkan-x64.zip)
- [Windows x64 (OpenVINO)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-win-openvino-2026.2.1-x64.zip)
- [Windows x64 (SYCL)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-win-sycl-x64.zip)
- [Windows x64 (HIP)](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-bin-win-hip-radeon-x64.zip)
**openEuler:**
- [DISABLED](https://github.com/ggml-org/llama.cpp/pull/23705)
- openEuler x86 (310p)
- openEuler x86 (910b, ACL Graph)
- openEuler aarch64 (310p)
- openEuler aarch64 (910b, ACL Graph)
**UI:**
- [UI](https://github.com/ggml-org/llama.cpp/releases/download/b9871/llama-b9871-ui.tar.gz)
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
    """Some wrapper for zipfile & tarfile. Yeah, that's it"""

    match archive_path.suffix:
        # assuming it's .tar.gz
        case ".gz":
            with tarfile.open(archive_path, "r:gz") as archive:
                archive.extractall(dest_path)

            # linux archive has extra nested path in `llama-b8147` format,
            # so unnest it
            nested_dir: pathlib.Path = next(dest_path.iterdir())

            assert nested_dir.is_dir() and nested_dir.stem.startswith(
                "llama-b"
            ), f"Expected nested directory of `llama-bxxxx` format, got `{nested_dir}`"

            unnest_dir(nested_dir)

        case ".zip":
            with zipfile.ZipFile(archive_path) as archive:
                archive.extractall(dest_path)


# --- Logics ---


def fetch_release_list() -> list[int]:
    """Fetches valid lists that has assets without b prefix"""

    all_releases = json.loads(urllib.request.urlopen(RELEASES_URL).read())

    return [
        int(release["tag_name"][1:]) for release in all_releases if release["assets"]
    ]


def fetch_url_map(release_json: dict) -> dict[str, list[str]]:
    """Generate {link_name: link} from llama.cpp release's body.
    Absolutely no fail safeguard for now

    Returns:
        {link_name: [link, ...]}
    """

    # Used to extract name & link from markdown
    pattern = re.compile(r"\[([\S\s]+?)]\((\S+?)\)")

    # expected [("... HIP", "some_url"), [("... CUDA 12", "some_url"), ("... DLLs", "cuda_dll_url")], ...]
    url_pairs: list[list[tuple[str, str]]] = [
        pattern.findall(line)
        for line in release_json["body"].splitlines()
        if line.startswith("- [") and not line.startswith("- [DIS")
    ]

    # normalize name & filter
    return {pairs[0][0]: [pair[1] for pair in pairs] for pairs in url_pairs}


def get_local_version(root: pathlib.Path) -> int:
    """Get local version of llama-cpp binaries in dumb way"""
    try:
        version_file = root / VERSION_FILE_NAME
        return int(version_file.read_text("utf8")) if version_file.exists() else 0
    except ValueError:
        return 0


def dl_runtime(
    root: pathlib.Path, temp_dir: pathlib.Path, runtime_name: str, urls: list[str]
) -> bool:
    """Download/unpack workload for each download candidate.

    Returns:
        bool: True if downloaded, False otherwise

    Raises:
        urllib.error.HTTPError: Happens for b9871 where assets are missing, 404
    """

    # try to use in-parenthesis name
    try:
        runtime_name = next(RUNTIME_DIR_NAME_PATTERN.finditer(runtime_name)).group(1)
    except StopIteration:
        pass

    normalized_name = runtime_name.replace(" ", "_").lower()

    dest_path = root / normalized_name

    if dest_path.exists():
        print(f"Removing existing directory {dest_path}")
        shutil.rmtree(dest_path)

    # download & unpack each url to same dir for CUDA + CUDA DLL condition
    for url in urls:
        size = 0

        dl_path: pathlib.Path = temp_dir / pathlib.Path(url).name

        with (
            dl_path.open("wb") as fp,
            urllib.request.urlopen(url) as resp,
        ):
            while data := resp.read(32768):
                size += len(data)
                print(f"Downloading {runtime_name} - {size:,} B", end="\r")
                fp.write(data)

            print(f"Downloaded  {runtime_name} - {size:,} B")

        print(f"Extracting  {runtime_name}")
        unpack_archive(dl_path, dest_path)

        dl_path.unlink()

    return True


def dl_release(dest: pathlib.Path, force_redownload: bool, release: str):
    """Attempt to fetch latest releases from GitHub API.

    Args:
        dest: Download destination dir
        force_redownload: Ignore existing version check and always redownload binaries
        release: Release tag to fetch. If empty, fetches latest release. e.g. "b9871"

    Raises:
        urllib.error.HTTPError: Happens for b9871 where assets are missing, 404
    """

    release_list = fetch_release_list()

    if release:
        initial_version = int(release.removeprefix("b"))
        version: int = max(n for n in release_list if n <= int(initial_version))
        # dumb af but oneliner, I don't care for now

        if initial_version != version:
            print(
                f"Release {release} has no assets, selecting previous valid release {version}"
            )
    else:
        version: int = release_list[-1]

    parsed = json.loads(urllib.request.urlopen(f"{TAG_RELEASE_URL}/b{version}").read())

    if not force_redownload and get_local_version(dest) >= version:
        print(f"Already using release b{version}")
        return

    print(f"Downloading release b{version}")

    url_map = fetch_url_map(parsed)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = pathlib.Path(temp_dir)

        for runtime_str in FILE_DL_CONFIG:
            if runtime_str not in url_map:
                continue

            dl_runtime(dest, temp_dir, runtime_str, url_map[runtime_str])

    # update version last
    (dest / VERSION_FILE_NAME).write_text(str(version), "utf8")


# --- Drivers ---


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
    _parser.add_argument(
        "-r",
        "--release",
        type=str,
        default="",
        help="Specific release to download from. e.g. b9871",
    )

    _args = _parser.parse_args()

    print(f"Using '{_args.destination}' as root")

    dl_release(_args.destination, _args.force_redownload, _args.release)
