"""
Dumb probably unsafe async API server, purely made of included batteries for fun.

Example Usage:
```python
import asyncio
import pathlib

from dumb_async_api_server import *


APP = DumbAPIServer()
ROOT = pathlib.Path(__file__).parent

@APP.get("/hello")
async def hello(subdir: str, fail="", **kwargs) -> HTTPResponse:
    await asyncio.sleep(1)

    # if this wasn't the exact dir match, ignore it
    if subdir:
        return HTTPResponse(404)

    # for status test
    if fail == "true":
        return HTTPResponse(400)

    return HTTPResponse.text(f"Hello, world!\nparams:{kwargs}")

@APP.get("/")
async def index(subdir: str) -> HTTPResponse:
    return serve_path(ROOT / subdir)


if __name__ == "__main__":
    asyncio.run(APP.serve())
```

:Author: jupiterbjy@gmail.com
"""


import asyncio
import pathlib
from urllib.parse import unquote
from pprint import pprint
from collections.abc import Callable, Awaitable

__all__ = ["DumbAPIServer", "HTTPError", "HTTPResponse", "serve_path"]

# --- Utilities ---

class HTTPError(Exception):
    """Used internally to trigger HTTP error from handlers"""

    def __init__(self, status: int):
        self.status = status


class HTTPResponse:
    """Helper class to create response. Create either directly or via named constructors."""

    def __init__(self, status: int, content_type: str = "", content: bytes = b""):
        self.status = status
        self.content_type = content_type
        self.content = content

    @classmethod
    def text(cls, body: str) -> "HTTPResponse":
        """Creates HTTP response instance with text body"""

        return cls(200, "text/plain", body.encode("utf8"))

    @classmethod
    def html(cls, body: str) -> "HTTPResponse":
        """Creates HTTP response instance with HTML body"""

        return cls(200, "text/html", body.encode("utf8"))

    @classmethod
    def octet_stream(cls, body: bytes) -> "HTTPResponse":
        """Creates HTTP response instance with octet stream body"""

        return cls(200, "application/octet-stream", body)


def serve_path(root: pathlib.Path, subdir: str = "") -> HTTPResponse:
    """Creates a response for Serving files for GET request."""

    p = root / pathlib.PurePosixPath(subdir)

    # try normalizing dir
    try:
        p = p.resolve(strict=True)
    except (FileNotFoundError, RuntimeError):
        return HTTPResponse(404)

    # prevent escape
    if root != p and root not in p.parents:
        return HTTPResponse(404)

    # serve files
    if p.is_dir():
        index_html = p / "index.html"
        if index_html.exists():
            return HTTPResponse.html(index_html.read_text("utf8"))

        return HTTPResponse(404)

    if p.suffix.lower() == ".html":
        return HTTPResponse.html(p.read_text("utf8"))

    return HTTPResponse.octet_stream(p.read_bytes())


class _HTTPUtils:
    """HTTP Header creation helper class"""

    _SUFFIX = "Connection: close\r\n"

    _RESP_HEADER = {
        200: " 200 OK\r\n",
        400: " 400 Bad Request\r\n",
        403: " 403 Forbidden\r\n",
        404: " 404 Not Found\r\n",
        405: " 405 Method Not Allowed\r\n",
    }

    _RESP_CONTENT_TEMPLATE = (
        "Content-Type: {content_type}\r\nContent-Length: {content_len}\r\n"
    )

    @classmethod
    def create_resp_header(
            cls, http_ver: str, response: HTTPResponse
    ) -> str:
        """Create HTTP response header

        Args:
            http_ver: HTTP version string - e.g. "HTTP/1.1" or "HTTP/2"
            response: HTTPResponse instance

        Returns:
            HTTP response header string
        """

        if not response.content_type:
            return "".join((http_ver, cls._RESP_HEADER[response.status], cls._SUFFIX))

        return "".join(
            (
                http_ver,
                cls._RESP_HEADER[response.status],
                cls._RESP_CONTENT_TEMPLATE.format(
                    content_type=response.content_type, content_len=len(response.content)
                ),
                cls._SUFFIX,
            )
        )

    @staticmethod
    def parse_raw_dir(raw_dir: str) -> tuple[str, dict[str, str]]:
        """Parses directory string with params.

        Args:
            raw_dir: Directory string with params

        Returns:
            (unquoted_directory, unquoted_param_dict) tuple

        Raises:
            ValueError: When the parameter section is malformed
        """

        # param could be empty, gotta get via star
        path, *param = unquote(raw_dir).split("?", maxsplit=1)

        kwargs: dict[str, str] = {}
        if param:
            for arg in param[0].split("&"):
                kwargs.__setitem__(*arg.split("="))

        return path, kwargs

    @staticmethod
    def parse_req(raw_req: str) -> dict[str, str]:
        """Chops request into more manageable dictionary

        Args:
            raw_req: Raw request string

        Returns:
            Dictionary-fied request string
        """

        header, *_ = raw_req.split("\r\n\r\n", maxsplit=1)

        line_iter = iter(header.rstrip().splitlines())

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


async def _read_all(reader: asyncio.StreamReader, chunk_size: int = 1024) -> str:
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

class DumbAPIServer:
    """Dumb probably unsafe async HTTP server"""

    _AsyncHandler = Callable[..., Awaitable[HTTPResponse]]

    def __init__(self):
        self.mapped_dirs: dict[str, dict[str, DumbAPIServer._AsyncHandler]] = {
            "GET": {},
            "POST": {},
        }

    def get(self, map_dir: str) -> Callable[[_AsyncHandler], _AsyncHandler]:
        """Decorator to map a directory to async function"""

        # @functools.wraps
        def decorator(async_func: DumbAPIServer._AsyncHandler) -> DumbAPIServer._AsyncHandler:
            if not asyncio.iscoroutinefunction(async_func):
                raise TypeError("Decorated function must be an async function")

            self.mapped_dirs["GET"][map_dir] = async_func
            return async_func

        return decorator

    def post(self, map_dir: str) -> Callable[[_AsyncHandler], _AsyncHandler]:
        """Decorator to map a directory to async function.
        Function must return (header: str, body: bytes) tuple.
        """

        # @functools.wraps
        def decorator(async_func: DumbAPIServer._AsyncHandler) -> DumbAPIServer._AsyncHandler:
            if not asyncio.iscoroutinefunction(async_func):
                raise TypeError("Decorated function must be an async function")

            self.mapped_dirs["POST"][map_dir] = async_func
            return async_func

        return decorator

    async def create_resp(self, req_dict: dict[str, str]) -> tuple[str, bytes]:
        """Create response for given request.
        To make logging more readable, returns response as `(header, body)` pair.

        Args:
            req_dict: Parsed request dict

        Returns:
            (Header str, Body bytes) tuple
        """

        http_ver = req_dict["HTTP"]

        # reject user when non-GET are used, we don't support it
        if req_dict["Method"] not in self.mapped_dirs:
            return _HTTPUtils.create_resp_header(http_ver, HTTPResponse(405)), b""

        # parse path + param
        try:
            path, kwargs = _HTTPUtils.parse_raw_dir(req_dict["Directory"])

        except ValueError:
            return _HTTPUtils.create_resp_header(http_ver, HTTPResponse(400)), b""

        # attempt to get handler by iterating parent
        try:

            for parent_path in pathlib.PurePosixPath(path).parents:
                p = parent_path.as_posix()

                if p in self.mapped_dirs[req_dict["Method"]]:
                    async_func = self.mapped_dirs[req_dict["Method"]][p]
                    subdir = pathlib.Path(path).relative_to(parent_path).as_posix()
                    break

            else:
                if path == "/":
                    async_func = self.mapped_dirs[req_dict["Method"]]["/"]
                    subdir = ""
                else:
                    raise KeyError()

        except KeyError:
            return _HTTPUtils.create_resp_header(http_ver, HTTPResponse(404)), b""

        # got valid hit, run it
        try:
            resp = await async_func(**kwargs, subdir=subdir)
            return _HTTPUtils.create_resp_header(http_ver, resp), resp.content

        except Exception as err:
            print(f"Exception in {async_func.__name__}: {err}")
            return _HTTPUtils.create_resp_header(http_ver, HTTPResponse(500)), b""

    async def _tcp_handler(self, r: asyncio.StreamReader, w: asyncio.StreamWriter):
        """Handles incoming TCP connection. Yeah, that's it

        Args:
            r: StreamReader from asyncio.start_server()
            w: StreamWriter from asyncio.start_server()
        """

        # TODO: Add keepalive

        # Receive
        print("\nReceiving")

        parsed = _HTTPUtils.parse_req(await _read_all(r))
        pprint(parsed)

        print("Received")

        # Prep response
        header, body = await self.create_resp(parsed)

        # Respond
        print("\nResponding ---")

        print(header)
        w.write(header.encode("utf8"))
        w.write(b"\r\n")

        print("--- Body length:", len(body))
        w.write(body)

        await w.drain()
        w.close()

        print("Response sent")

    async def serve(self, address: str = "127.0.0.1", port: int = 8080):
        """Name

        Args:
            address: Serving address
            port: Serving port
        """

        server = await asyncio.start_server(self._tcp_handler, address, port)

        print(f"Started at http://{address}:{port}")

        async with server:
            await server.serve_forever()
