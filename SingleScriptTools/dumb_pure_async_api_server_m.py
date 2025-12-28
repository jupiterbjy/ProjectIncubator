"""
Dumb probably unsafe async API server, purely made of included batteries BUT for trio for fun.

Run this module directly to start a test server. (run module directly to run this test yourself)

Example Usage:
```python
import asyncio
import pathlib

from dumb_pure_async_api_server_m import *

APP = DumbAPIServer()
ROOT = pathlib.Path(__file__).parent

DIR_LISTING = True
PLACEHOLDER_HTML = ...

@APP.get_deco("/delay_test")
async def delay_test(subdir: str, delay: str = "0", **_kwargs) -> HTTPResponse:

    if subdir:
        return HTTPResponse.redirect(f"/delay_test?delay=2")

    try:
        val = float(delay)
        assert val > 0
        await asyncio.sleep(val)
    except ValueError, AssertionError:
        return HTTPResponse.redirect(f"/delay_test?delay=2")

    return HTTPResponse.text(f"{delay}s wait done")

@APP.get_deco("/hello/nested")
async def nested(subdir: str, **kwargs) -> HTTPResponse:
    return HTTPResponse.text(f"(Hello, world!)^2\nsubdir: {subdir}\nparams:{kwargs}")

@APP.get_deco("/")
async def index(subdir: str, **_kwargs) -> HTTPResponse:
    if subdir:
        return serve_path(root, subdir, serve_listing=DIR_LISTING)

    if (root / "index.html").exists():
        return serve_path(root, serve_listing=DIR_LISTING)

    if DIR_LISTING:
        return serve_path(root, serve_listing=True)

    return HTTPResponse.html(placeholder_html)


if __name__ == "__main__":
    asyncio.run(APP.serve())
```

```text
Registered GET '/delay_test' -> 'delay_test'
Registered GET '/hello/nested' -> 'nested'
Registered GET '/' -> 'index'
Starting at http://127.0.0.1:8080 - Available GET:
http://127.0.0.1:8080/delay_test
http://127.0.0.1:8080/hello/nested
http://127.0.0.1:8080/

-> Receiving ---
{...
 'Directory': '/',
 'HTTP': 'HTTP/1.1',
 'Host': '127.0.0.1:8080',
 'Method': 'GET',
 ...
 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) '
               'Gecko/20100101 Firefox/146.0'}
--- Received

<- Responding ---
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 159
Connection: close

--- Response sent
```

:Author: jupiterbjy@gmail.com
"""

import asyncio
import pathlib
import inspect
import traceback
from urllib.parse import unquote, quote
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

    def __init__(self, status: int, content_type="", content=b"", headers: dict[str, str] = None):
        self.status = status
        self.content_type = content_type
        self.content = content
        self.headers: dict[str, str] = {}
        if headers:
            self.headers.update(headers)

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

    @classmethod
    def redirect(cls, url: str) -> "HTTPResponse":
        return cls(301, headers={"Location": url})


_AsyncHandler = Callable[..., Awaitable[HTTPResponse]]


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
    """Request helper class"""

    _RESP_HEADER = {
        200: " 200 OK",
        301: " 301 Moved Permanently",
        400: " 400 Bad Request",
        403: " 403 Forbidden",
        404: " 404 Not Found",
        405: " 405 Method Not Allowed",
        418: " 418 I'm a teapot",
        500: " 500 Internal Server Error",
    }

    _HEADER_TEMPLATE = "{http_ver} {status}\r\n{headers}"

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

        headers: dict[str, str] = response.headers.copy()

        if response.content_type:
            headers["Content-Type"] = response.content_type
            headers["Content-Length"] = str(len(response.content))

        # found that it's not standard on HTTP2,
        # not sure will anyone ever use this for HTTP2 though
        if http_ver.startswith("HTTP/1"):
            headers["Connection"] = "close"

        return cls._HEADER_TEMPLATE.format(
            http_ver=http_ver,
            status=cls._RESP_HEADER[response.status],
            headers="\r\n".join(f"{k}: {v}" for k, v in headers.items()) + "\r\n",
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

    output = b""

    while recv := await reader.read(chunk_size):
        output += recv

        if len(recv) < chunk_size:
            break

    return output.decode("utf8")


def generate_dir_listing_html(root: pathlib.Path, sanitized_abs_sub_path: pathlib.Path) -> str:
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


def serve_path(root: pathlib.Path, subdir="", serve_listing=False) -> HTTPResponse:
    """Creates a response for Serving files for GET request."""

    sub_p = sanitize_path(root, subdir)

    if not sub_p:
        return HTTPResponse(404)

    # serve files
    if sub_p.is_dir():
        index_html = sub_p / "index.html"

        if index_html.exists():
            return HTTPResponse.html(index_html.read_text("utf8"))

        if not serve_listing:
            return HTTPResponse(404)

        # serve dir
        return HTTPResponse.html(generate_dir_listing_html(root, sub_p))

    if sub_p.suffix.lower() == ".html":
        return HTTPResponse.html(sub_p.read_text("utf8"))

    return HTTPResponse.octet_stream(sub_p.read_bytes())


# --- Logics ---

class DumbAPIServer:
    """Dumb probably unsafe async HTTP server"""

    def __init__(self):
        self.mapped_dirs: dict[str, dict[str, _AsyncHandler]] = {
            "GET": {},
            "POST": {},
        }

    def get_deco(self, map_dir: str) -> Callable[[_AsyncHandler], _AsyncHandler]:
        """Decorator to map a directory to async function"""

        # @functools.wraps
        def decorator(async_func: _AsyncHandler) -> _AsyncHandler:
            if not inspect.iscoroutinefunction(async_func):
                raise TypeError("Decorated function must be an async function")

            self.mapped_dirs["GET"][map_dir] = async_func
            print(f"Registered GET '{map_dir}' -> '{async_func.__qualname__}'")

            return async_func

        return decorator

    def post_deco(self, map_dir: str) -> Callable[[_AsyncHandler], _AsyncHandler]:
        """Decorator to map a directory to async function.
        Function must return (header: str, body: bytes) tuple.
        """

        # @functools.wraps
        def decorator(async_func: _AsyncHandler) -> _AsyncHandler:
            if not inspect.iscoroutinefunction(async_func):
                raise TypeError("Decorated function must be an async function")

            self.mapped_dirs["POST"][map_dir] = async_func
            print(f"Registered POST {map_dir} -> {async_func.__name__}")

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

        # reject user when non-GET/POST are used, we don't support it
        if req_dict["Method"] not in self.mapped_dirs:
            return HTTPUtils.create_resp_header(http_ver, HTTPResponse(405)), b""

        # parse path + param
        try:
            str_path, kwargs = HTTPUtils.parse_raw_dir(req_dict["Directory"])
            path = pathlib.PurePosixPath(str_path)

        except ValueError:
            return HTTPUtils.create_resp_header(http_ver, HTTPResponse(400)), b""

        # attempt to get handler by finding match for self & parent dir
        async_func: _AsyncHandler
        subdir: str

        for candidate in [path, *path.parents]:
            p = candidate.as_posix()

            if p not in self.mapped_dirs[req_dict["Method"]]:
                continue

            async_func = self.mapped_dirs[req_dict["Method"]][p]
            subdir = path.relative_to(candidate).as_posix()

            if subdir == ".":
                subdir = ""
            break
        else:
            return HTTPUtils.create_resp_header(http_ver, HTTPResponse(404)), b""

        # got valid hit, run it
        try:
            # noinspection PyUnboundLocalVariable
            resp = await async_func(**kwargs, subdir=subdir)
            return HTTPUtils.create_resp_header(http_ver, resp), resp.content

        except Exception as err:
            print(f"Exception in {async_func.__name__}: {err}")
            return HTTPUtils.create_resp_header(http_ver, HTTPResponse(500)), b""

    async def _tcp_handler(self, r: asyncio.StreamReader, w: asyncio.StreamWriter):
        """Handles incoming TCP connection. Yeah, that's it

        Args:
            r: StreamReader from asyncio.start_server()
            w: StreamWriter from asyncio.start_server()
        """

        # TODO: Add keepalive

        # Receive
        print("\nReceiving ---")

        parsed = HTTPUtils.parse_req(await _read_all(r))
        pprint(parsed)

        print("--- Received")

        # Prep response
        # noinspection PyBroadException
        try:
            header, body = await self.create_resp(parsed)
        except Exception as _err:
            traceback.print_exc()
            header = HTTPUtils.create_resp_header(parsed["HTTP"], HTTPResponse(500))
            body = b""

        # Respond
        print("\nResponding ---")

        print(header)
        w.write(header.encode("utf8"))
        w.write(b"\r\n")
        w.write(body)

        await w.drain()
        w.close()

        print("--- Response sent")

    async def serve(self, address: str = "127.0.0.1", port: int = 8080):
        """Name

        Args:
            address: Serving address
            port: Serving port
        """

        # print links so it's easier to test
        url = f"http://{address}:{port}"

        print(f"Starting at {url} - Available GET:")
        for path in self.mapped_dirs["GET"]:
            print(url + path)

        server = await asyncio.start_server(self._tcp_handler, address, port)

        async with server:
            await server.serve_forever()


# --- Drivers ---

def __test_serve():
    print("!! Running test server !!")

    app = DumbAPIServer()
    root = pathlib.Path(__file__).parent
    dir_listing = True

    placeholder_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Placeholder Page</title>
    </head>
    <body>
        <h1>No index.html found!</h1>
    </body>
    </html>
    """

    @app.get_deco("/resp_test")
    async def resp_test(subdir: str, code: str, **_kwargs) -> HTTPResponse:
        if subdir:
            return HTTPResponse(404)

        try:
            return HTTPResponse(int(code))
        except ValueError:
            return HTTPResponse(400)

    @app.get_deco("/delay_test")
    async def delay_test(subdir: str, delay: str = "0", **_kwargs) -> HTTPResponse:

        if subdir:
            return HTTPResponse.redirect(f"/delay_test?delay=2")

        try:
            val = float(delay)
            assert val > 0
            await asyncio.sleep(val)
        except ValueError, AssertionError:
            return HTTPResponse.redirect(f"/delay_test?delay=2")

        return HTTPResponse.text(f"{delay}s wait done")

    @app.get_deco("/hello")
    async def hello(subdir: str, **kwargs) -> HTTPResponse:
        return HTTPResponse.text(f"Hello, world!\nsubdir: {subdir}\nparams:{kwargs}")

    @app.get_deco("/hello/nested")
    async def nested(subdir: str, **kwargs) -> HTTPResponse:
        return HTTPResponse.text(f"(Hello, world!)^2\nsubdir: {subdir}\nparams:{kwargs}")

    @app.get_deco("/")
    async def index(subdir: str, **_kwargs) -> HTTPResponse:

        if subdir:
            return serve_path(root, subdir, serve_listing=dir_listing)

        if (root / "index.html").exists():
            return serve_path(root, serve_listing=dir_listing)

        if dir_listing:
            return serve_path(root, serve_listing=True)

        return HTTPResponse.html(placeholder_html)

    asyncio.run(app.serve())


if __name__ == "__main__":
    __test_serve()
