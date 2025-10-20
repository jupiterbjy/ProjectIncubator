"""
Generates HTML file to act as index for media files (audio, image, video).
Intended for creating fast lookup index for your local projects.

Assumes media exists in top level of each directory.

Usage:

1. Execute next to project directories to generate for all suitable subdir
2. Pass project directories as param(or drag drop) instead as whitelist

Either way, it will generate index.html in the same directory as script.

![](readme_res/project_media_html_index.png)

:Author: jupiterbjy@gmail.com
"""

import pathlib
import argparse
from datetime import datetime
from collections.abc import Iterable, Sequence
from typing import Callable


# --- Configs ---

ROOT = pathlib.Path(__file__).parent

# for test
# ROOT = pathlib.Path(r"E:\Media\Works\CSP\VNs")

OUTPUT_PATH = ROOT / "index.html"
# if one's gonna drag drop or just double click script to update index,
# would be better just creating it next to script either way.

# OUTPUT_COPIED_DATA_DIR = OUTPUT_DIR / "index_data"
# OUTPUT_COPIED_DATA_DIR.mkdir(exist_ok=True)

# File extension whitelist that determines a directory as project.
# Edit this to fit your project dir or pass param, i.e. `-e .pptx`.
# This does not necessarily have to be media format.
PROJ_FILE = {".clip", ".flp", ".ogg"}

# Project directory's time format
DT_FORMAT = "%Y-%m-%d %H:%M:%S"

# HTML Media Element width.
HTML_MEDIA_WIDTH = "500px"

HTML_MAIN_TEMPLATE = """
<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8">
    <title>{title}</title>
</head>

<style>
{css}
</style>

<body>
    <h1>{title}</h1>
    {body}
</body>

</html>
"""
# maybe tiling could be added in the future, or idk.
# not that I'm gonna maintain indent when formatting but for my sake

CSS = """
* {
    color: #fff;
}

body {
    background-color: #1e1f22;
}

.media {
    margin: 10px;
}

.project {
    margin-bottom: 10px;
}

.project_content {
    margin-left: 10px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(WIDTH, 1fr));
    grid-gap: 10px;
}
"""

HTML_DIR_TEMPLATE = """
<div class="project">
    <h2>{name}</h2>
    <div class="project_content">
        {body}
    </div>
</div>
"""


IMG_EXT_SET = {".jpg", ".jpeg", ".png", ".svg", ".webp", ".apng"}

HTML_IMG_TEMPLATE = """
<div class="media">
    <div>{name}</div>
    <img src="{src}" alt="" width={width}>
</div>
"""


VID_EXT_TYPE_MAP = {
    ".mp4": "video/mp4",
    ".webm": "video/webm",
}

HTML_VID_TEMPLATE = """
<div class="media">
    <div>{name}</div>
    <video width={width} controls>
        <source src="{src}" type="{type}">
        Your browser does not support the video tag.
    </video>
</div>
"""


AUDIO_EXT_TYPE_MAP = {
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
}

HTML_AUDIO_TEMPLATE = """
<div class="media">
    <div>{name}</div>
    <audio style="width:{width};display:block" controls>
        <source src="{src}" type="{type}">
        Your browser does not support the audio tag.
    </audio>
</div>
"""
# why the heck audio tags don't take width


# --- Registerer Boiler Plate ---


def template_main(title: str, body: str) -> str:

    return HTML_MAIN_TEMPLATE.format(css=CSS, title=title, body=body)


def template_directory(name: str, body: str) -> str:

    return HTML_DIR_TEMPLATE.format(name=name, body=body)


EXT_FUNC_MAP: dict[str, Callable[[str, str, str, str], str]] = {}


def template_media(name: str, src: str, ext: str, width: str) -> str:
    """Syntax sugar for EXT_FUNC_MAP. Combines all media templates into one."""

    return EXT_FUNC_MAP[ext](name, src, ext, width)


def _template_register_deco(extensions: Iterable[str]) -> Callable:
    """Used to register function to EXT_FUNC_MAP. Feels like overkill but welp"""

    def inner(func: Callable) -> Callable:
        EXT_FUNC_MAP.update({ext: func for ext in extensions})
        return func

    return inner


@_template_register_deco(IMG_EXT_SET)
def image(name: str, src: str, _ext: str, width: str) -> str:

    return HTML_IMG_TEMPLATE.format(name=name, src=src, width=width)


@_template_register_deco(VID_EXT_TYPE_MAP.keys())
def video(name: str, src: str, ext: str, width: str) -> str:

    return HTML_VID_TEMPLATE.format(
        name=name, src=src, type=VID_EXT_TYPE_MAP[ext], width=width
    )


@_template_register_deco(AUDIO_EXT_TYPE_MAP.keys())
def audio(name: str, src: str, ext: str, width: str) -> str:

    return HTML_AUDIO_TEMPLATE.format(
        name=name, src=src, type=AUDIO_EXT_TYPE_MAP[ext], width=width
    )


# --- Logics ---


def fetch_project_dirs(
    ext_whitelist: set[str], dir_whitelist: Sequence[pathlib.Path]
) -> list[pathlib.Path]:
    """Fetch project dirs that contains file(s) with given extension in top level.

    Args:
        ext_whitelist: file's extension to look for in top level
        dir_whitelist: project directory candidates

    Returns:
        list of project dirs, sorted by creation date
    """

    dir_birth_time_pairs: list[tuple[pathlib.Path, float]] = []

    for proj_dir in dir_whitelist:

        # sanity check
        if not proj_dir.is_dir():
            continue

        # if there's whitelisted file under it, append it
        for nested_dir in proj_dir.iterdir():
            if nested_dir.suffix in ext_whitelist:
                dir_birth_time_pairs.append((proj_dir, nested_dir.stat().st_birthtime))
                break

    # sort & return
    dir_birth_time_pairs.sort(key=lambda pair: pair[1])
    return [pair[0] for pair in dir_birth_time_pairs]


def generate_html(project_dirs: list[pathlib.Path], html_media_width: str) -> str:
    """Generate html file from given project dirs.

    Args:
        project_dirs: list of valid(hopefully) project directories
        html_media_width: width of media elements in generated html
    """

    html_parts: list[str] = []

    for proj_dir in project_dirs:

        parts = []

        for nested_dir in proj_dir.iterdir():
            if nested_dir.suffix in EXT_FUNC_MAP:
                parts.append(
                    template_media(
                        nested_dir.name,
                        str(nested_dir.relative_to(ROOT)),
                        nested_dir.suffix,
                        html_media_width,
                    )
                )

        dir_ctime = datetime.fromtimestamp(proj_dir.stat().st_birthtime).strftime(
            DT_FORMAT
        )
        dir_mtime = datetime.fromtimestamp(proj_dir.stat().st_mtime).strftime(DT_FORMAT)

        dir_name = f"{proj_dir.name} ({dir_ctime} ~ {dir_mtime})"

        html_parts.append(template_directory(dir_name, "\n".join(parts)))

    return template_main(f"Index for {ROOT.stem}", "<hr>\n".join(html_parts))


# --- Drivers ---


def main(
    ext_whitelist: set[str], dir_whitelist: list[pathlib.Path], html_media_width: str
):

    fetched = fetch_project_dirs(ext_whitelist, dir_whitelist)

    if fetched:
        print("Detected following dirs:", *fetched, sep="\n")
    else:
        print("No project dirs detected.")
        return

    OUTPUT_PATH.write_text(generate_html(fetched, html_media_width), "utf-8")


if __name__ == "__main__":
    _parser = argparse.ArgumentParser("Media HTML Index Generator")

    _parser.add_argument(
        "dirs",
        nargs="*",
        type=pathlib.Path,
        help="Project directories to generate index for."
        "If not provided, will use all neighboring directories containing media files.",
        default=list(ROOT.iterdir()),
    )

    _parser.add_argument(
        "-e",
        "--ext",
        nargs="*",
        type=str,
        help=f"File extension whitelist override. Default: {PROJ_FILE}",
        default=PROJ_FILE,
    )
    # kinda wondering if I should call this `exts` since `dirs` are multiple, but welp

    _parser.add_argument(
        "-w",
        "--width",
        type=str,
        help=f"Width of media elements. Default: {HTML_MEDIA_WIDTH}",
        default=HTML_MEDIA_WIDTH,
    )

    _args = _parser.parse_args()
    CSS = CSS.replace("WIDTH", _args.width)

    main(_args.ext, sorted(_args.dirs), _args.width)
