"""
Merges m4s files of steam's recording clips into mp4.

This script exists because as of 2024-10-14 steam beta is broken and can't export video properly.
As of 11-17 STILL NOT WORKING so we'll need this script a bit longer...

Refer -h for usage.

Requires ffmpeg in PATH.

:Author: jupiterbjy@gmail.com
"""

import functools
import pathlib
import argparse
import subprocess
import tempfile
import json
import urllib.request
import urllib.error
from typing import Sequence, List, Tuple


# --- Configs ---

# URL to json with all steam app's AppID-Name mapping.
# Not using ISteamApps/GetAppList/v0002/ because it's not reliable.
STEAM_APP_DETAIL_URL = "http://store.steampowered.com/api/appdetails?appids="

# FFMPEG command to fix video full range flag (regardless of it being av1 h265 or h264)
# FFMPEG_FIX_RANGE_FLAG = "-bsf:v h264_metadata=video_full_range_flag=1"
FFMPEG_FIX_RANGE_FLAG = ""

# FFMPEG command to run when merging final video and audio streams
FFMPEG_CMD = " ".join(
    [
        'ffmpeg -i "{}" -i "{}" -c copy -map 0:v:0 -map 1:a:0 -y',
        FFMPEG_FIX_RANGE_FLAG,
        '"{}"',
    ]
)

SUFFIX = ".m4s"

CHUNK_PREFIX = "chunk"
VIDEO_STREAM = "stream0"
AUDIO_STREAM = "stream1"

INIT_VIDEO_STREAM = "init-stream0.m4s"
INIT_AUDIO_STREAM = "init-stream1.m4s"

REVISION = "3 (2024-11-17)"

SPLASH_MSG = f"""
=========================================
jupiterbjy's Steam clip extraction script
Revision {REVISION}
=========================================
""".strip()


# --- Utilities ---


@functools.cache
def app_id_2_name(app_id: int) -> str:
    """Converts app_id to app_name. Failsafe back to app_id if fails.

    Args:
        app_id: Steam AppID

    Returns:
        app_name
    """

    print(f"Inquiring AppID {app_id} to steam API")

    url = STEAM_APP_DETAIL_URL + str(app_id)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    resp = urllib.request.urlopen(req)

    print("Response code:", resp.getcode())

    if resp.getcode() != 200:
        # probably rate limit if this fails
        print("Content:", resp.read())

        print("Falling back to AppID")
        return str(app_id)

    data = json.loads(resp.read().decode())
    name = data[str(app_id)]["data"]["name"]
    print("Got name:", name)

    return name


def concat_file(parts: Sequence[pathlib.Path], output_path: pathlib.Path) -> None:
    """Concatenates given files into output_path.

    Args:
        parts: files to concatenate
        output_path: output file path
    """

    with output_path.open("wb") as fp:
        for part in parts:
            fp.write(part.read_bytes())


# --- Logic ---


def fetch_parts(
    m4s_root: pathlib.Path,
) -> Tuple[List[pathlib.Path], List[pathlib.Path]]:
    """Fetches m4s parts from m4s_root and returns video and audio parts.

    Args:
        m4s_root: directory where m4s files are stored

    Returns:
        (video_parts, audio_parts)
    """

    # prep list for video and audio parts
    video_parts: List[pathlib.Path] = []
    audio_parts: List[pathlib.Path] = []

    init_video_part: pathlib.Path = m4s_root / INIT_VIDEO_STREAM
    init_audio_part: pathlib.Path = m4s_root / INIT_AUDIO_STREAM

    # extract video and audio parts
    for m4s_path in m4s_root.iterdir():
        if m4s_path.suffix != SUFFIX:
            continue

        if not m4s_path.stem.startswith(CHUNK_PREFIX):
            continue

        if VIDEO_STREAM in m4s_path.stem:
            video_parts.append(m4s_path)

        elif AUDIO_STREAM in m4s_path.stem:
            audio_parts.append(m4s_path)

    # sort files
    video_parts.sort()
    audio_parts.sort()

    return [init_video_part] + video_parts, [init_audio_part] + audio_parts


def merge_streams(
    video_parts: List[pathlib.Path],
    audio_parts: List[pathlib.Path],
    temp_dir: pathlib.Path,
    output_file: pathlib.Path,
) -> bool:
    """Merges video and audio parts into output_path.

    Args:
        video_parts: video parts
        audio_parts: audio parts
        temp_dir: path to store merged video and audio temporarily
        output_file: final output path

    Returns:
        True if successful, False otherwise
    """

    # temp path for merged streams
    merged_video_path = temp_dir / "merged_video.mp4"
    merged_audio_path = temp_dir / "merged_audio.mp4"

    # merge parts
    print("Concatenating streams")
    concat_file(video_parts, merged_video_path)
    concat_file(audio_parts, merged_audio_path)

    # merge video and audio via ffmpeg
    print("Merging streams")
    proc = subprocess.run(
        FFMPEG_CMD.format(
            merged_video_path.as_posix(),
            merged_audio_path.as_posix(),
            output_file,
        ),
        capture_output=True,
    )

    # if ffmpeg failed then let it be
    if proc.returncode == 0:
        print("Saved as", output_file.name)
        return True

    print("Failed to merge!")
    print(proc.stderr.decode("utf8"))

    return False


# --- Drivers ---


def main(clip_paths: Sequence[pathlib.Path], output_dir: pathlib.Path):
    """Main logic"""

    # successful count
    success_count = 0

    # setup temp dir
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)

        for clip_path in clip_paths:

            print("\nProcessing", clip_path.name)

            # fetch app id
            _, app_id, date, time = clip_path.name.split("_")

            # fetch app name from id
            app_name = app_id_2_name(int(app_id))
            new_file_name = f"{app_name} {date}_{time}.mp4"

            # get dir starting with fg
            m4s_root: pathlib.Path = next((clip_path / "video").iterdir())

            # fetch & sort parts
            video_parts, audio_parts = fetch_parts(m4s_root)
            print(f"Found V:{len(video_parts)} + A:{len(audio_parts)} parts")

            # merge streams
            success_count += merge_streams(
                video_parts, audio_parts, tmpdir, output_dir / new_file_name
            )

    print(f"\nAll done - {success_count}/{len(clip_paths)} successful")


if __name__ == "__main__":

    print(SPLASH_MSG)

    _parser = argparse.ArgumentParser(
        description="Merges m4s files of steam's recording clips into mp4.",
        add_help=True,
    )

    _parser.add_argument(
        "clip_paths",
        type=pathlib.Path,
        nargs="+",
        help="Paths to each clip directory containing m4s files with 'clip_<game_id>_YYYYDDMM_HHMMSS' naming.",
    )

    _parser.add_argument(
        "-o",
        "--output-dir",
        type=pathlib.Path,
        default=pathlib.Path(__file__).parent,
        help="Output directory for merged files. Defaults to script's directory.",
    )

    _args = _parser.parse_args()

    # make sure it's not just single directory with name 'clips' which is parent dir
    if len(_args.clip_paths) == 1 and _args.clip_paths[0].name == "clips":
        _args.clip_paths = _args.clip_paths[0].iterdir()

    # make sure directory is filtered
    _args.clip_paths = [
        _p for _p in _args.clip_paths if _p.stem.startswith("clip") and _p.is_dir()
    ]

    try:
        main(_args.clip_paths, _args.output_dir)

    except Exception:
        import traceback

        traceback.print_exc()

        input("\n\nPress Enter to exit: ")
        raise

    input("\n\nPress Enter to exit: ")
