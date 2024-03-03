"""
Generates m3u8 file using audio files in current directory. Recursive.

:Author: jupiterbjy@gmail.com
"""

import pathlib
from typing import Generator, Tuple

import mutagen


ROOT = pathlib.Path(__file__).parent
SUFFIX = input("Target Extension(Default: .flac): ")

if not SUFFIX:
    # if empty set default
    SUFFIX = ".flac"

elif not SUFFIX[0] == ".":
    # check if dot is omitted
    SUFFIX = "." + SUFFIX


def check_file_gen(path: pathlib.Path, suffix) -> Generator[pathlib.Path, None, None]:
    """yield file path with given suffix(Including leading period, like .txt)"""

    print(f"In {path.relative_to(ROOT)}")

    for path_ in path.iterdir():

        # if dir then recurse
        if path_.is_dir():
            yield from check_file_gen(path_, suffix)
            continue

        # otherwise file
        if path_.suffix == SUFFIX:
            print(f"Found file '{path_.relative_to(ROOT)}'")
            yield path_


def get_len_n_title(path: pathlib.Path) -> Tuple[int, str]:
    """Get audio title and duration. Raises MutagenError if error opening."""

    try:
        tag: mutagen.FileType = mutagen.File(path)
    except mutagen.MutagenError as err:
        print(f"Error loading file '{path.relative_to(ROOT)}'")
        print("Details:", err)
        raise

    return round(tag.info.length), tag["title"]


def main():
    header = f"#EXTM3U"
    lines = [
        "#EXTINF:{},{}\n{}".format(*get_len_n_title(file), file.relative_to(ROOT))
        for file in check_file_gen(ROOT, SUFFIX)
    ]

    with open(ROOT / f"{ROOT.name}.m3u8", "wt", encoding="utf8") as fp:
        fp.write("\n".join((header, *lines)))

    print(f"Wrote {1 + 2 * len(lines)} lines.")


if __name__ == '__main__':
    main()
    input("Press enter to exit")
