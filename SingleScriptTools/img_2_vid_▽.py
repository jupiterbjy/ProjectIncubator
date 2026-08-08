"""
Dumb script to create vid from images via ffmpeg,
primarily written to save storage after long rimworld plays.

e.g. output:
```
...

Summary:
 << Encoded 41 images to '...\rockandstone\tile-9819,0\_output.mp4' / 339.7MB -> 44.0MB (13.0%)
 << Encoded 418 images to '...\desert\tile-52038,0\_output.mp4' / 5.1GB -> 797.9MB (15.2%)
 << Encoded 162 images to '...\kiiro_valor_and_biotech\tile-114985,0\_output.mp4' / 2.3GB -> 329.0MB (13.7%)
 << Encoded 346 images to '...\neko!\tile-117003,0\_output.mp4' / 4.0GB -> 677.2MB (16.5%)
 << Encoded 184 images to '...\ratkin!\tile-17957,0\_output.mp4' / 1.5GB -> 207.7MB (13.8%)
 << Encoded 206 images to '...\RatkinMiners\tile-31164,0\_output.mp4' / 1.6GB -> 222.5MB (13.7%)

Press Enter to exit:
```

:Author: jupiterbjy@gmail.com
"""

import subprocess
import pathlib
from argparse import ArgumentParser
from typing import Iterator, Iterable

# --- Config ---

CRF: int = 30

FRAME_RATE: int = 1

GOP_SEC: float = 5

FFMPEG_CMD = """
ffmpeg -safe 0 -hide_banner -y -f concat -r {rate} -i {list_path} \
-c:v libsvtav1 -crf {crf} -preset 5 -g {gop} -pix_fmt yuv420p \
-movflags +faststart {out_path}
""".strip()
# ^^^ safe 0 needed since rimworld progress render generate filename with commas

SUFFIX_WHITELIST: set[str] = {
    ".jpg",
    ".jpeg",
    ".png",
}

# Minimum img per subdir to consider it as valid encoding target
MIN_IMAGE_PER_SET: int = 10

# Prefix blacklist for directories that shouldn't be encoded
PREFIX_BLACKLIST = {
    "_",
}


# --- Util ---


def encode_path_gen(
    search_paths: Iterable[pathlib.Path],
) -> Iterator[list[pathlib.Path]]:
    """Yields suitable image sets from given search paths"""

    # just in case...
    yielded_roots: set[pathlib.Path] = set()

    # this mess is necessary for better drag-drop experience
    for search_path in search_paths:
        for path in search_path.rglob("**/"):
            imgs = [p for p in path.iterdir() if p.suffix in SUFFIX_WHITELIST]

            if len(imgs) < MIN_IMAGE_PER_SET:
                continue

            if path in yielded_roots:
                continue

            yielded_roots.add(path)
            yield sorted(imgs)


def byte_2_human(bytes_: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_ < 1024.0:
            return f"{bytes_:3.1f}{unit}"

        bytes_ /= 1024.0

    return f"{bytes_:3.1f}Y"


# --- Logic ---


def encode(img_sets: list[pathlib.Path]) -> pathlib.Path:
    """Performs encoding and returns resulting vid path.

    Args:
        img_sets: sorted, pure-image paths

    Returns:
        pathlib.Path: output vid path
    """

    # just use first image's parent, since we're encoding in folders
    root = img_sets[0].parent
    concat_path = root / "_concat.txt"
    output_path = root / "_output.mp4"

    with concat_path.open("wt", encoding="utf8") as fp:
        for p in img_sets:
            # idk if we need this tbh
            # escaped = p.name.replace("'", "\\'")
            fp.write(f"file '{p.name}'\n")

    subprocess.run(
        FFMPEG_CMD.format(
            rate=FRAME_RATE,
            list_path=concat_path.name,
            crf=CRF,
            gop=GOP_SEC,
            out_path=output_path.name,
        ),
        cwd=root,
        shell=True,
        check=True,
    )
    return output_path


# --- Driver ---


def _main(search_roots: Iterable[pathlib.Path], delete: bool):
    # if delete:
    #     print("WARNING: Deleting original image sets after encoding, proceed?")
    #     if input("(y/n): ").lower() != "y":
    #         print("Aborting.")
    #         return

    # for last summary print
    histories: list[str] = []

    for img_sets in encode_path_gen(search_roots):

        print(f"\n >> Encoding {img_sets[0].parent}")
        output_path = encode(img_sets)

        # prep stat
        prev_size = sum(p.stat().st_size for p in img_sets)
        post_size = output_path.stat().st_size
        perc = post_size / prev_size * 100.0

        result_str = (
            f" << Encoded {len(img_sets)} images to '{output_path}' / "
            f"{byte_2_human(prev_size)} -> {byte_2_human(post_size)} ({perc:.1f}%)"
        )
        histories.append(result_str)
        print(result_str)

        # clear files if requested
        if delete:
            print(f" << Deleting {len(img_sets)} images")
            for p in img_sets:
                p.unlink()

    print("\nSummary:")
    for history in histories:
        print(history)


if __name__ == "__main__":
    _parser = ArgumentParser()
    _parser.add_argument(
        "search_roots",
        type=pathlib.Path,
        nargs="+",
        help="Paths to search for image sets to encode. Recursive.",
    )
    _parser.add_argument(
        "-d",
        "--delete",
        action="store_true",
        help="Deletes original image sets after encoding",
    )

    _args = _parser.parse_args()
    try:
        _main(_args.search_roots, _args.delete)

    except Exception:
        import traceback

        traceback.print_exc()
        raise

    finally:
        input("\nPress Enter to exit: ")
