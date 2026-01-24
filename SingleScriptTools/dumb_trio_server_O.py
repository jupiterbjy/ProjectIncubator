"""
Dumb probably unsafe async HTTP server, purely made of included batteries & trio async lib for fun.

This is separate from asyncio ver purely because I personally only prefer trio to asyncio,
but asyncio do allow writing something pure without 3rd party libraries - which is kinda fun in itself.

Provides minimal-escape-protected file listing interface by default, can also serve static files such as HTML.

Rewrite of [stackoverflow answer](https://stackoverflow.com/a/70649803) I wrote.

For slightly better structure, refer `dumb_trio_api_server_m.py`.

![](readme_res/dumb_async_server.png)

:Author: jupiterbjy@gmail.com
"""

import pathlib
from argparse import ArgumentParser
from pprint import pprint
from urllib.parse import quote
from functools import partial

import trio

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


def read_text_utf8(path: pathlib.Path) -> str:
    """Attempts to read file as UTF8 text, then retries as native encoding.

    Raises:
        UnicodeDecodeError: If file can't be open as either utf8 or system native encoding.
    """

    try:
        return path.read_text("utf8")
    except UnicodeDecodeError:
        pass

    return path.read_text()


class HTTPUtils:
    """HTTP Header creation helper class"""

    _RESP_HEADER = {
        200: " 200 OK",
        403: " 403 Forbidden",
        404: " 404 Not Found",
        405: " 405 Method Not Allowed",
    }

    _FILE_TYPE_MAP: dict[str, str] = {
        ".txt": "text/plain",
        ".md": "text/plain",
        ".html": "text/html",
        ".css": "text/css",
        ".js": "text/javascript",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".ico": "image/x-icon",
        ".webp": "image/webp",
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".ogg": "video/ogg",
        ".pdf": "application/pdf",
        ".json": "application/json",
    }

    _TEXT_EXT: set[str] = {
        ".txt",
        ".md",
        ".html",
        ".css",
        ".js",
        ".json",
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

        headers: dict[str, str] = {
            "Cross-Origin-Resource-Policy": "cross-origin",
            # ^^^ required for youtube embeds
            # "Access-Control-Allow-Origin": "*",
            # "Referrer-Policy": "strict-origin-when-cross-origin",
            # "Cache-Control": "no-cache",
        }

        if http_ver.startswith("HTTP/1"):
            headers["Connection"] = "close"

        if content_type:
            headers["Content-Type"] = content_type
            headers["Content-Length"] = str(content_len)

        return "\r\n".join(
            (
                http_ver,
                cls._RESP_HEADER[status],
                *(f"{k}: {v}" for k, v in headers.items()),
            )
        )

    @classmethod
    def create_data_resp(
        cls, http_ver, content_type: str, content: bytes
    ) -> tuple[str, bytes]:
        """Syntax sugar for creating header/body pair"""
        return (
            cls.create_resp_header(http_ver, 200, content_type, len(content)),
            content,
        )

    @classmethod
    def create_html_resp(cls, http_ver, content: str) -> tuple[str, bytes]:
        return cls.create_data_resp(http_ver, "text/html", content.encode("utf8"))

    @classmethod
    def create_file_resp(cls, http_ver, path: pathlib.Path) -> tuple[str, bytes]:
        """Attempts to automatically determine type based on file extension and return header/body pair."""

        ext = path.suffix.lower()
        content_type: str = cls._FILE_TYPE_MAP.get(ext, "application/octet-stream")
        data: bytes = (
            read_text_utf8(path).encode("utf8")
            if ext in cls._TEXT_EXT
            else path.read_bytes()
        )

        return cls.create_data_resp(http_ver, content_type, data)

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


async def read_all(reader: trio.SocketStream, chunk_size: int = 1024) -> str:
    """Reads all data from an asyncio StreamReader

    Args:
        reader: Stream reader
        chunk_size: Reading unit size

    Returns:
        UTF8 decoded string
    """

    output = ""

    while recv := await reader.receive_some(chunk_size):
        output += recv.decode("utf8")

        if len(recv) < chunk_size:
            break

    return output


# --- Logics ---


def _generate_dir_listing_html(
    root: pathlib.Path, sanitized_abs_sub_path: pathlib.Path
) -> str:
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

        # make sure it's absolute & ends with slash, otherwise relative resource access breaks
        if parent_str == ".":
            parent_str = "/"
        else:
            parent_str = f"/{parent_str}/"

    except ValueError:
        parent_str = "/"

    relative = quote(
        "/"
        if sanitized_abs_sub_path == root
        else f"/{sanitized_abs_sub_path.relative_to(root).as_posix()}/"
    )

    lines: list[str] = [
        f'<meta charset="UTF-8">\n'
        f"<h1>Directory Listing for {relative}</h1>\n"
        f'<a href="{parent_str}">Go Up</a><br>'
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
            lines.append(f'D <a href="{relative}{path_name}/">{sub_p.name}</a>')

        elif sub_p.suffix.lower() == ".html":
            lines.append(f'H <a href="{relative}{path_name}">{sub_p.name}</a>')

        else:
            lines.append(
                f'F <a href="{relative}{path_name}" download="{path_name}">{sub_p.name}</a>'
            )

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
            return HTTPUtils.create_html_resp(http_ver, idx_p.read_text("utf8"))

        # otherwise serve directory
        return HTTPUtils.create_html_resp(
            http_ver, _generate_dir_listing_html(root, dir_)
        )

    # otherwise serve file
    return HTTPUtils.create_file_resp(http_ver, dir_)


async def tcp_handler_verbose(
    stream: trio.SocketStream,
    root: pathlib.Path = pathlib.Path("."),
):
    """Handles incoming TCP connection. Yeah that's it

    Args:
        stream: `SocketStream` from `trio.serve_tcp()`
        root: Root directory to serve
    """

    try:
        # Receive
        print("\n\nReceiving")

        parsed = HTTPUtils.parse_req(await read_all(stream))
        pprint(parsed)

        print("Received")

        # Prep response
        header, body = _create_resp(parsed, root)

        # Respond
        print("\nResponding ---")

        print(header)
        await stream.send_all(f"{header}\r\n\r\n".encode("utf8") + body)

        print("--- Response sent")

        # uncomment prints above and use this for compact printing
        print(f"Request {header.split(" ")[1]}: {parsed['Directory']}")

    except Exception as _err:
        print(f"Server Error: {_err}")


async def tcp_handler(
    stream: trio.SocketStream,
    root: pathlib.Path = pathlib.Path("."),
):
    """Handles incoming TCP connection. Yeah that's it

    Args:
        stream: `SocketStream` from `trio.serve_tcp()`
        root: Root directory to serve
    """

    try:
        parsed = HTTPUtils.parse_req(await read_all(stream))
        header, body = _create_resp(parsed, root)
        await stream.send_all(f"{header}\r\n\r\n".encode("utf8") + body)

        print(f"Request {header.split(" ")[1]}: {parsed['Directory']}")

    except Exception as _err:
        print(f"Server Error: {_err}")


async def serve_files(
    root: pathlib.Path,
    address: str = "localhost",
    port: int = 8000,
    verbose: bool = False,
):
    # make sure root is absolute
    root = root.resolve()

    print(
        f"Server Starting at http://{address}:{port}",
        f"-Root: {root}",
        f"-Verbose: {verbose}",
        sep="\n",
    )

    handler = tcp_handler_verbose if verbose else tcp_handler

    try:
        await trio.serve_tcp(partial(handler, root=root), port, host=address)
    except* KeyboardInterrupt:
        print("Server Stopped")


if __name__ == "__main__":
    _parser = ArgumentParser()

    _parser.add_argument(
        "-r",
        "--root",
        type=pathlib.Path,
        default=pathlib.Path(__file__).parent,
        help="Root directory to serve",
    )

    _parser.add_argument(
        "-a",
        "--address",
        type=str,
        default="localhost",
        help="Address to bind to",
    )

    _parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Prints A LOT",
    )

    _parser.add_argument("-p", "--port", type=int, default=8000, help="Port to bind to")

    trio.run(partial(serve_files, **_parser.parse_args().__dict__))
