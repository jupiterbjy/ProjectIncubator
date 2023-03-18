"""
Script for generating markdown entry for this SingleScriptTools.
Assuming every script in directory starts with docstring.
"""

import re
import pathlib
from typing import Iterator

ROOT = pathlib.Path(__file__).parent
WRITE_TO = ROOT / "README.md"

DOCS_RE = re.compile(r'(?:^""")([\s\S]*?)(?:""")')
ENCODING = "utf8"
FORMAT = """
### [{}]({})
{}

---
"""


def docstring_extract_gen(file_iterator: Iterator[pathlib.Path]):
    for file in file_iterator:
        # discard files starting with underscore
        if file.stem[0] == "_":
            continue

        # file's small, reading entire file for first few lines are not a concern
        docs = DOCS_RE.match(file.read_text(ENCODING)).groups()[0].strip()
        yield file.name, file.as_posix(), docs


def main():

    # create .py script list iterator except one starting with underscore
    file_list = (p for p in ROOT.iterdir() if p.stem[0] != "_" and p.suffix == ".py")

    # write to file
    with WRITE_TO.open("at", encoding="utf8") as fp:
        for name, path_, docs in docstring_extract_gen(file_list):
            print(f"Writing {name}")
            fp.write(FORMAT.format(name, path_, docs))


if __name__ == '__main__':
    main()
