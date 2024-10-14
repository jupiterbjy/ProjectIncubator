"""
Merges m4s files of steam's recording clips into mp4.
This script exists because as of 2024-10-14 steam beta is broken and can't export video properly.

Refer -h for usage.

Requires ffmpeg in PATH.

:Author: jupiterbjy@gmail.com
"""

import pathlib
import argparse
import subprocess
import tempfile
from typing import Sequence, List, Tuple


# --- CONFIG ---

SUFFIX = ".m4s"

CHUNK_PREFIX = "chunk"
VIDEO_STREAM = "stream0"
AUDIO_STREAM = "stream1"

INIT_VIDEO_STREAM = "init-stream0.m4s"
INIT_AUDIO_STREAM = "init-stream1.m4s"

FFMPEG_CMD = "ffmpeg -i {} -i {} -c copy -map 0:v:0 -map 1:a:0 {}"


# --- Utilities ---


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


def main(clip_paths: Sequence[pathlib.Path]) -> None:

    # setup temp dir
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)

        # setup temp merged files
        merged_video_path = tmpdir / "merged_video.mp4"
        merged_audio_path = tmpdir / "merged_audio.mp4"

        for clip_path in clip_paths:
            print("Processing", clip_path.name)

            # get dir starting with fg
            m4s_root: pathlib.Path = next((clip_path / "video").iterdir())

            # fetch & sort parts
            video_parts, audio_parts = fetch_parts(m4s_root)

            # merge parts
            concat_file(video_parts, merged_video_path)
            concat_file(audio_parts, merged_audio_path)

            # merge video and audio
            proc = subprocess.run(
                FFMPEG_CMD.format(
                    merged_video_path.as_posix(),
                    merged_audio_path.as_posix(),
                    clip_path.parent / (clip_path.stem + ".mp4"),
                )
            )

            if proc.returncode == 0:
                print("Successfully merged", clip_path.name)
            else:
                print("Failed to merge", clip_path.name)


if __name__ == "__main__":
    _parser = argparse.ArgumentParser(
        description="Merges m4s files of steam's recording clips into mp4."
    )

    _parser.add_argument(
        "clip_paths",
        type=pathlib.Path,
        nargs="+",
        help="Paths to each clip directory containing m4s files with 'clip_<game_id>_YYYYDDMM_HHMMSS' naming.",
    )

    _args = _parser.parse_args()
    _p: pathlib.Path
    main([_p for _p in _args.clip_paths if _p.stem.startswith("clip") and _p.is_dir()])
