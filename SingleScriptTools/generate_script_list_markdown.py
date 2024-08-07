"""
Script for generating markdown entry for this SingleScriptTools.
Assuming every script in directory starts with docstring.

:Author: jupiterbjy@gmail.com
"""

import re
import pathlib
from typing import Iterator

ROOT = pathlib.Path(__file__).parent
WRITE_TO = ROOT / "README.md"

SKIP_LINE_STARTING_WITH = ":"
DOCS_REGEX = re.compile(r'^"""([\s\S]*?)"""')
ENCODING = "utf8"
FORMAT = """
---

### [{}]({})
{}

<br>
<br>

"""


def docstring_extract_gen(file_iterator: Iterator[pathlib.Path]):
    for file in file_iterator:
        # discard files starting with underscore
        if file.stem[0] == "_":
            continue

        # file's small, reading entire file for first few lines are not a concern
        docs = DOCS_REGEX.match(file.read_text(ENCODING)).groups()[0].strip()

        # discard any line starting with specific strings
        docs = "\n".join(
            line for line in docs.splitlines() if not line.startswith(SKIP_LINE_STARTING_WITH)
        )
        yield file.name, file.as_posix(), docs


def main():

    # create .py script list iterator except one starting with underscore
    file_list = (p for p in ROOT.iterdir() if p.stem[0] != "_" and p.suffix == ".py")

    # cut in first --- & strip all newlines, then add single newline
    data = WRITE_TO.read_text("utf8").split("---")[0].strip() + "\n"

    # write to file
    with WRITE_TO.open("wt", encoding="utf8") as fp:
        fp.write(data)

        # append docs
        for name, _, docs in docstring_extract_gen(file_list):
            print(f"Writing {name}")
            fp.write(FORMAT.format(name, name, docs))


if __name__ == '__main__':
    main()
