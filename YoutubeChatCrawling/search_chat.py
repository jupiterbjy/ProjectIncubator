# TODO: use pycui

import json
import pathlib
import argparse
import re
from typing import Iterator, Tuple, Generator

from wcwidth import wcwidth, wcswidth


def pad_actual_length(source: Iterator[str], pad: str = "\u200b") -> Tuple[str, Generator[str, None, None]]:
    """
    Determine real-displaying character length, and provide padding accordingly to match length.
    This way slicing will cut asian letters properly, not breaking tidy layouts.
    Don't expect to have 0-width characters in given string!
    :param source: Original string to be manipulated. Accepts Iterator[str], allowing lazy generator.
    :param pad: Default character to pad, default ZWSP
    :return: padding character and lazy generator for padded string
    """

    def inner_gen(source_: Iterator[str]) -> Generator[str, None, None]:
        for char in source_:
            yield char
            # if wcwidth(char) == 2:
            #     yield pad

    return pad, inner_gen(source)
    # https://github.com/microsoft/terminal/issues/1472
    # Windows Terminal + (Powershell/CMD) combo can't run this due to ZWSP width issue.
    # Expected to run in purely CMD / Linux Terminal. or WSL + Windows Terminal.
    # Tested on Xfce4 & CMD.


def fit_to_actual_width(text: str, length_lim: int) -> str:
    """
    Cuts given text with varying character width to fit inside given width.
    Expects that lines is short enough, will read entire lines on memory multiple times.
    :param text: Source text
    :param length_lim: length limit in 1-width characters
    :return: cut string
    """

    ellipsis_ = "..."

    # returns immediately if no action is needed
    if wcswidth(text) != len(text):

        _, padded = pad_actual_length(text)
        source = "".join(padded)
        limited = source[:length_lim]

        # if last character was 2-width, padding unicode wore off, so last 2-width character can't fit.
        # instead pad with space for consistent ellipsis position.
        if wcwidth(limited[-1]) == 2:
            limited = limited[:-1] + " "
    else:
        source = text
        limited = text[:length_lim].ljust(length_lim)

    # Add ellipsis if original text was longer than given width
    if len(source) > length_lim:
        limited = limited[:length_lim - len(ellipsis_)]

        # check if last character was 2-width, if so, strip last char and add space
        if wcwidth(limited[-1]):
            limited = limited[:-1] + ' '

        limited += ellipsis_

    return limited


def main():

    chat_path: pathlib.Path = args.chat

    loaded: dict = json.loads(chat_path.read_text("utf8"))

    msg_only = True

    while (command := input("\nSearch (exit to exit): ")) != "exit":

        if command == "msg_only":
            msg_only = not msg_only
            continue

        for idx, entry in loaded.items():
            author = entry["author"]["name"]
            msg = entry["message"]
            time = entry["elapsedTime"]

            compiled = re.compile(command)

            if not msg_only and compiled.match(author) is not None:
                print(f"A [{idx}][{author}][{time}] - [{msg}]")

            elif compiled.match(msg) is not None:
                if msg_only:
                    print(f"[{idx:>5}][{author:<50}]", msg)
                else:
                    print(f"M [{idx}][{author}][{time}] - [{msg}]")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("chat", metavar="C", type=pathlib.Path, help="chat json to search for")

    args = parser.parse_args()

    main()

