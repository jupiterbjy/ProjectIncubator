"""
A very primitive script to unicode-fy passed text files, such as mass csv files, etc

:Author: jupiterbjy@gmail.com
"""


import pathlib
from argparse import ArgumentParser
from typing import Sequence, Union


class Argument:
    files: Sequence[pathlib.Path]
    encoding: str


def convert_files(files: Sequence[pathlib.Path], initial_encoding: Union[str, None]):
    """Converts given files into utf8"""

    for file in files:
        print(f"Converting {file.as_posix()}")

        # in case some file might already be in utf8
        try:
            file.write_text(file.read_text(initial_encoding), "utf8")
        except UnicodeDecodeError:
            print(f"Can't open via {initial_encoding}, assuming it's already in utf8.")


if __name__ == "__main__":
    parser = ArgumentParser("Makes all image dimension square.")
    parser.add_argument(
        "files", metavar="F", type=pathlib.Path, nargs="+", help="Text files"
    )
    parser.add_argument(
        "-e",
        "--encoding",
        type=str,
        help="Input file's encoding - if omitted, will use OS's default",
    )
    # parser.add_argument(
    #     "-n",
    #     "--new-line",
    #     type=str,
    #     help="Target newline ",
    # )

    args = Argument()
    parser.parse_args(namespace=args)

    try:
        convert_files(args.files, args.encoding)
    except Exception as err:
        import traceback

        traceback.print_exc()
        input()
        raise
