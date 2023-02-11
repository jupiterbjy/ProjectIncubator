"""
Kalimba tabs parser

Thought of using lexer but thought making readable as-is with it might be nightmare.
"""

import re
from os import PathLike
from typing import TextIO, Generator, Iterable, Dict, Sequence, Tuple, TypedDict
from collections import defaultdict

from loguru import logger

from .notations import *


# configs
ENCODING = "utf8"
# TAB_PARSER = re.compile(r"""([A-G]['"]?#?| )""")
TAB_PARSER = re.compile(r"""([1-7]['"]?#?| )""")
SECTION_SEP = "```"
OCTAVE_SYMBOLS = " ", "'", '"'
KEYS = 17


__all__ = ["Header", "Note", "TabLine", "TabSheet", "tune", "tab_parser", "parser"]


class Header(TypedDict):
    kalimpy: str
    title: str
    author: str
    tuning: Sequence[str]
    interval: float
    note: str


class Note:
    numeric_translation: Dict[str, str] | None = None

    def __init__(self, num_note: str):
        """Kalimba Note representation

        Args:
            num_note: Note in numerical notation
        """

        self.numeric = num_note
        self.alphabetic = self.numeric_translation[num_note]
        self.frequency = FREQUENCY[self.alphabetic]

    def __str__(self):
        return self.numeric

    @classmethod
    def setup_translation(cls, tuning: Sequence[str]):
        """Sets up Numeric to Alphabetical notation translation dictionary.

        Args:
            tuning: Tuning values from tab file
        """

        cls.numeric_translation = {
            num: alpha for num, alpha in zip(NUM_NOTATION[:KEYS], tuning)
        }
        # add whitespace, this will remove any possible special cases later on
        cls.numeric_translation[" "] = " "


class TabLine:
    def __init__(self, tabs: Iterable[str], lyrics=""):
        self.tabs = [Note(tab) for tab in tabs]
        self.lyrics = lyrics

    def __iter__(self):
        return iter(self.tabs)

    def __len__(self):
        return len(self.tabs)

    def __repr__(self):
        return f"TabLine({self.tabs}" + f", {self.lyrics})" if self.lyrics else ")"

    def __str__(self):
        return (f"{self.lyrics}\n" if self.lyrics else "") + str(self.tabs)


class TabSheet:
    def __init__(self, header: Header, lines: Sequence[TabLine]):
        self.header = header
        self.lines = lines
        self.title = self.header["title"]
        # TODO: parse grouped notes


# just for the interface shake
def tune(tuning: Sequence[str]):
    """Sets up Numeric to Alphabetical notation translation dictionary.

    Args:
        tuning: Tuning values from tab file
    """
    Note.setup_translation(tuning)


def _notes_gen(cycler: Iterable):
    for symbol in OCTAVE_SYMBOLS:
        yield from (f"{n}{symbol}" for n in cycler)


def num_notes_gen():
    yield from _notes_gen(range(1, 8))


def section_gen(fp: TextIO) -> Generator[Tuple[int, str], None, None]:
    """Iterate until reaching section separation marker.
    Also discards any comments. This is closure returning generator function.

    Args:
        fp: TextIO via open() or equivalent with rt mode & utf8.

    Yields:
        lines in sections
    """
    # read until section separator
    for line_no, line in enumerate(iter(fp.readline, SECTION_SEP)):

        # if line isn't comment nor empty, strip trailing newline and yield
        if line[0] != "#" and line != "\n":
            yield line_no, line.rstrip("\n")


def header_parser(fp: TextIO) -> Header:
    info_def_dict = defaultdict(str)

    for line_no, line in section_gen(fp):
        logger.debug(f"Parsing Line {line_no}")

        # separate into key & value, strip remaining string bits then concatenate
        # this is to simplify parsing multi line notes.
        key, val = line.split(": ")
        info_def_dict[key.strip(" -").lower()] += val

    # convert back to normal dict
    info_dict = dict(info_def_dict)

    # break tuning data into pieces, so we can use it for tab parsing & append white spacing
    info_dict["tuning"] = info_dict["tuning"].split(" ") + [" "]

    # convert spacing unit length(in milliseconds) back to number
    info_dict["interval"] = float(info_dict["interval"])

    # use tuning to set up note translation dict
    Note.setup_translation(info_dict["tuning"])
    logger.debug(f"Header parsing done:\n{info_dict}")

    return info_dict


def tab_parser(line: str):
    return [matched[0] for matched in TAB_PARSER.finditer(line)]


def tab_lines_parser(fp: TextIO) -> Sequence[TabLine]:
    parsed_lines = []
    current_lyrics = []

    for line_no, line in section_gen(fp):
        logger.debug(f"Parsing Line {line_no}")

        if line[0] == SECTION_SEP:
            # If there's leading whitespace, if so it's lyrics.
            current_lyrics.append(line.strip())

        elif line[0]:
            # if there's something not empty, it's tabs. Parse line & clear lyrics
            parsed_lines.append(TabLine(tab_parser(line), " ".join(current_lyrics)))
            current_lyrics.clear()
        else:
            # if none of that then just clear up list, probably mis-formatted file.
            current_lyrics.clear()

    return parsed_lines


def parser(file: PathLike):
    with open(file, "rt", encoding=ENCODING) as fp:
        # get a section line iterator function
        info_dict = header_parser(fp)
        tab_lines = tab_lines_parser(fp)
        # ignore 3rd section, won't use for a while

    return info_dict, tab_lines
