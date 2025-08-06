"""
Dumb probably unsafe async HTTP server, purely made of included batteries for fun.

Provides minimal-escape-protected file listing interface by default, can also serve static files such as HTML.

Rewrite of [stackoverflow answer](https://stackoverflow.com/a/70649803) I wrote.

![](readme_res/dumb_async_server.png)

:Author: jupiterbjy@gmail.com
"""

import asyncio
import pathlib
from pprint import pprint
from typing import Iterator
from urllib.parse import unquote, quote

ROOT = pathlib.Path(__file__).parent


# --- Utilities ---


class HTTPUtils:
    """HTTP Header creation helper class"""

    _SUFFIX = "Connection: close\r\n\r\n"

    _RESP_HEADER = {
        200: " 200 OK\r\n",
        403: " 403 Forbidden\r\n",
        404: " 404 Not Found\r\n",
        405: " 405 Method Not Allowed\r\n",
    }

    _RESP_CONTENT_TEMPLATE = (
        "Content-Type: {content_type}\r\nContent-Length: {content_len}\r\n"
    )

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

        if not content_type:
            return "".join((http_ver, cls._RESP_HEADER[status], cls._SUFFIX))

        return "".join(
            (
                http_ver,
                cls._RESP_HEADER[status],
                cls._RESP_CONTENT_TEMPLATE.format(
                    content_type=content_type, content_len=content_len
                ),
                cls._SUFFIX,
            )
        )

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


def _dir_html_link_gen(abs_dir: pathlib.Path) -> Iterator[str]:
    """Yields anchor(`<a>`) elements for use as directory listing.
    HTML files will not use `download` attribute and will be served as static files.

    Args:
        abs_dir: absolute path to dir to be listed

    Yields:
        html anchor element string
    """

    for sub_path in abs_dir.iterdir():
        # calc url path
        relative = quote(
            "/"
            if abs_dir == ROOT
            else f"/{str(abs_dir.relative_to(ROOT)).removeprefix("./")}/"
        )
        path_name = quote(sub_path.name)

        # if dir or html file then set href to it
        if sub_path.is_dir() or sub_path.suffix.lower() == ".html":
            yield f'<a href="{relative}{path_name}">{path_name}</a>'
        else:
            # else set as download
            yield f'<a href="{relative}{path_name}" download="{path_name}">{path_name}</a>'


def _create_resp(req_dict: dict[str, str]) -> tuple[str, bytes]:
    """Create response for given request.
    To make logging more readable, returns response as `(header, body)` pair.

    Args:
        req_dict: Parsed request dict

    Returns:
        (Header str, Body bytes) tuple
    """

    http_ver = req_dict["HTTP"]

    # reject user when non-GET are used, we don't support it
    if req_dict["Method"] != "GET":
        return HTTPUtils.create_resp_header(http_ver, 405), b""

    # try normalizing the path
    dir_ = ROOT.joinpath(unquote(req_dict["Directory"]).removeprefix("/"))

    try:
        dir_ = dir_.resolve(strict=True)

    except FileNotFoundError:
        # unreachable path (or you have circular symlink for some reason)
        return HTTPUtils.create_resp_header(http_ver, 404), b""

    # check if it's subdir, if not kick the crap out of it
    if ROOT != dir_ and ROOT not in dir_.parents:
        return HTTPUtils.create_resp_header(http_ver, 403), b""

    # TODO: check for permission error

    if dir_.is_dir():

        # if index.html exists direct to it
        index_path = dir_ / "index.html"

        if index_path.exists():
            attach = index_path.read_text().encode("utf8")
            return (
                HTTPUtils.create_resp_header(http_ver, 200, "text/html", len(attach)),
                attach,
            )

        # otherwise serve directory
        try:
            parent_str = str(dir_.parent.relative_to(ROOT))
            if parent_str == ".":
                parent_str = ""

        except ValueError:
            parent_str = ""

        parent_dir = f'<a href="/{quote(parent_str)}">Go Up</a><br>'
        attach = (parent_dir + "<br>".join(_dir_html_link_gen(dir_))).encode("utf8")
        return (
            HTTPUtils.create_resp_header(http_ver, 200, "text/html", len(attach)),
            attach,
        )

    # is this html file?
    if dir_.suffix.lower() == ".html":
        attach = dir_.read_text().encode("utf8")
        return (
            HTTPUtils.create_resp_header(http_ver, 200, "text/html", len(attach)),
            attach,
        )

    # otherwise just send as octet stream
    attach = dir_.read_bytes()
    return (
        HTTPUtils.create_resp_header(
            http_ver, 200, "application/octet-stream", len(attach)
        ),
        attach,
    )


async def tcp_handler(r: asyncio.StreamReader, w: asyncio.StreamWriter):
    """Handles incoming TCP connection. Yeah that's it

    Args:
        r: StreamReader from asyncio.start_server()
        w: StreamWriter from asyncio.start_server()
    """

    # Receive
    print("\n\nReceiving")

    parsed = HTTPUtils.parse_req(await read_all(r))
    pprint(parsed)

    print("Received")

    # Prep response
    header, body = _create_resp(parsed)

    # Respond
    print("\nResponding ---")

    print(header)
    w.write(header.encode("utf8"))

    print("--- Body length:", len(body))
    w.write(body)

    await w.drain()
    w.close()

    print("Response sent")


async def serve_files(address: str = "127.0.0.1", port: int = 8080):
    server = await asyncio.start_server(tcp_handler, address, port)

    print(f"Started at http://{address}:{port}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(serve_files())
