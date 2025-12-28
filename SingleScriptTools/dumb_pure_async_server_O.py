"""
Dumb probably unsafe async HTTP server, purely made of included batteries for fun.

Provides minimal-escape-protected file listing interface by default, can also serve static files such as HTML.

Rewrite of [stackoverflow answer](https://stackoverflow.com/a/70649803) I wrote.

For slightly better structure, refer `dumb_pure_async_api_server_m.py`.

![](readme_res/dumb_async_server.png)

:Author: jupiterbjy@gmail.com
"""

import asyncio
import pathlib
from pprint import pprint
from urllib.parse import unquote, quote
from functools import partial

# ROOT = pathlib.Path(__file__).parent


# --- Utilities ---

def sanitize_path(root: pathlib.Path, rel_path: str) -> pathlib.Path | None:
    """Sanitizes `subdir` relative to root.

    Args:
        root: Root directory currently being served
        rel_path: Subdirectory relative to root

    Returns:
        Sanitized path or None if invalid
    """

    p = root / pathlib.PurePosixPath(rel_path)

    # try normalizing dir, aka resolving `/../../bla` things
    try:
        p = p.resolve(strict=True)
    except (FileNotFoundError, RuntimeError, OSError):
        return None

    # prevent escape by checking if root exists in parent list
    if root != p and root not in p.parents:
        return None

    return p


class HTTPUtils:
    """HTTP Header creation helper class"""

    _RESP_HEADER = {
        200: " 200 OK\r\n",
        403: " 403 Forbidden\r\n",
        404: " 404 Not Found\r\n",
        405: " 405 Method Not Allowed\r\n",
    }

    @classmethod
    def create_resp_header(
        cls, http_ver: str, status: int, content_type="", content_len=0
    ) -> str:
        """Create HTTP response header

        Args:
            http_ver: HTTP version string - e.g. "HTTP/1.1" or "HTTP/2"
            status: HTTP status code - e.g. 200
            content_type: HTTP Content type - e.g. "text/html" or "application/octet-stream
            content_len: Length of the body

        Returns:
            HTTP response header string
        """

        return "".join(
            (
                http_ver,
                cls._RESP_HEADER[status],
                "Content-Type: {}\r\nContent-Length: {}\r\n".format(
                    content_type, content_len
                ) if content_len else "",
                "Connection: close\r\n\r\n" if http_ver.startswith("HTTP/1") else "\r\n\r\n",
            )
        )

    @classmethod
    def create_html_resp(cls, http_ver, content: bytes) -> tuple[str, bytes]:
        """Syntax sugar for creating HTML response header and pairing with body"""
        return cls.create_resp_header(http_ver, 200, "text/html", len(content)), content

    @classmethod
    def create_bytes_resp(cls, http_ver, content: bytes) -> tuple[str, bytes]:
        """Syntax sugar for creating octet stream response header and pairing with body"""
        return cls.create_resp_header(http_ver, 200, "application/octet-stream", len(content)), content

    @staticmethod
    def parse_req(raw_req: str) -> dict[str, str]:
        """Chops request into more manageable dictionary

        Args:
            raw_req: Raw request string

        Returns:
            Dictionarified request string
        """

        line_iter = iter(raw_req.rstrip().splitlines())

        # assume 1st line is head cause wtf, makes putting all others much easier
        method, dir_, http_ver = next(line_iter).split()
        req_dict = {
            "Method": method,
            "Directory": dir_,
            "HTTP": http_ver,
        }

        for line in line_iter:
            req_dict.__setitem__(*line.split(": "))

        return req_dict


async def read_all(reader: asyncio.StreamReader, chunk_size: int = 1024) -> str:
    """Reads all data from an asyncio StreamReader

    Args:
        reader: Stream reader
        chunk_size: Reading unit size

    Returns:
        UTF8 decoded string
    """

    output = ""

    while recv := await reader.read(chunk_size):
        output += recv.decode("utf8")

        if len(recv) < chunk_size:
            break

    return output


# --- Logics ---

def _generate_dir_listing_html(root: pathlib.Path, sanitized_abs_sub_path: pathlib.Path) -> str:
    """Generates directory listing HTML for given directory.

    Args:
        root: Root directory currently being served
        sanitized_abs_sub_path: Absolute Subdirectory path that was sanitized

    Returns:
        HTML string
    """

    # prep link for stepping back. Will trigger for root but better for safeguarding
    try:
        parent_str = sanitized_abs_sub_path.parent.relative_to(root).as_posix()
        if parent_str == ".":
            parent_str = ""

    except ValueError:
        parent_str = ""

    relative = quote(
        "/"
        if sanitized_abs_sub_path == root
        else f"/{sanitized_abs_sub_path.relative_to(root).as_posix()}/"
    )

    lines: list[str] = [
        f'<meta charset="UTF-8">\n'
        f'<h1>Directory Listing for {relative}</h1>\n'
        f'<a href="/{quote(parent_str)}">Go Up</a><br>'
    ]

    # sort stuff by name for each, so we can put dir first then file
    listing = [*sanitized_abs_sub_path.iterdir()]
    dirs = sorted([p for p in listing if p.is_dir()], key=lambda p: p.name)
    files = sorted([p for p in listing if p.is_file()], key=lambda p: p.name)

    for sub_p in dirs + files:

        # make sure it's escaped
        path_name = quote(sub_p.name)

        # if dir or html, then set href to it
        if sub_p.is_dir():
            lines.append(f'D <a href="{relative}{path_name}">{sub_p.name}</a>')

        elif sub_p.suffix.lower() == ".html":
            lines.append(f'H <a href="{relative}{path_name}">{sub_p.name}</a>')

        else:
            lines.append(f'F <a href="{relative}{path_name}" download="{path_name}">{sub_p.name}</a>')

    return "<br>\n".join(lines)


def _create_resp(req_dict: dict[str, str], root: pathlib.Path) -> tuple[str, bytes]:
    """Create response for given request.
    To make logging more readable, returns response as `(header, body)` pair.

    Args:
        req_dict: Parsed request dict
        root: Currently served root directory

    Returns:
        (Header str, Body bytes) tuple
    """

    http_ver = req_dict["HTTP"]

    # reject user when non-GET are used, we don't support it
    if req_dict["Method"] != "GET":
        return HTTPUtils.create_resp_header(http_ver, 405), b""

    dir_ = sanitize_path(root, req_dict["Directory"].removeprefix("/"))
    if not dir_:
        return HTTPUtils.create_resp_header(http_ver, 404), b""

    if dir_.is_dir():

        # if index.html exists direct to it
        idx_p = dir_ / "index.html"

        if idx_p.exists():
            return HTTPUtils.create_html_resp(http_ver, idx_p.read_text("utf8").encode("utf8"))

        # otherwise serve directory
        return HTTPUtils.create_html_resp(http_ver, _generate_dir_listing_html(root, dir_).encode("utf8"))

    # is this html file?
    if dir_.suffix.lower() == ".html":
        return HTTPUtils.create_html_resp(http_ver, dir_.read_text().encode("utf8"))

    # otherwise just send as octet stream
    return HTTPUtils.create_bytes_resp(http_ver, dir_.read_bytes())


async def tcp_handler(r: asyncio.StreamReader, w: asyncio.StreamWriter, root: pathlib.Path = pathlib.Path(".")):
    """Handles incoming TCP connection. Yeah that's it

    Args:
        r: StreamReader from asyncio.start_server()
        w: StreamWriter from asyncio.start_server()
        root: Root directory to serve
    """

    # Receive
    print("\n\nReceiving")

    parsed = HTTPUtils.parse_req(await read_all(r))
    pprint(parsed)

    print("Received")

    # Prep response
    header, body = _create_resp(parsed, root)

    # Respond
    print("\nResponding ---")

    print(header)
    w.write(header.encode("utf8") + body)

    await w.drain()
    w.close()

    print("--- Response sent")


async def serve_files(root: pathlib.Path, address: str = "127.0.0.1", port: int = 8000):

    server = await asyncio.start_server(partial(tcp_handler, root=root), address, port)

    print(f"Started at http://{address}:{port}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(serve_files(pathlib.Path(__file__).parent))
