"""
Batch image embedding & querying script.

Written to make my miserable life of searching 500GB screenshots
w/ specific dialogue of a scene a bit more manageable.

Assumes /v1/embeddings endpoint that support batch embedding,
tested against llama.cpp EmbeddingGemma2 with ctx=ub=b=4096 / pooling mean

Indexing mode:
```text
$ py embed_img_▽.py ".../하나사키워크스프링 히카리"

[VectorDB] open w/ 464 rows
[EmbedServer] open

Batch: 8
Resize width: 1280
Resize threshold: 1536

Checking new/modified images in dir
Got 2539 new/modified imgs
Batch 0 start
...
Batch 317 start

Indexed 2539 new/modified files in 1872.62 (1.356/s)

[EmbedServer] closed
[VectorDB] closed
```

Query mode:
```text
$ py embed_img_▽.py ".../하나사키워크스프링 히카리" \
> -q "image containing monologue '삼각건이 머리에 얹어졌다' with blonde girl making >w< face"

[VectorDB] open w/ 3003 rows
[EmbedServer] open

Top-5:
  0.73515  +0.01231  Artemis_2026-09-08-00-57-38.jpg
  0.72284  +0.00446  Artemis_2026-09-08-00-57-26.jpg
  0.71838  +0.00357  Artemis_2026-09-07-02-36-38.jpg
  0.71481  +0.00017  Artemis_2026-09-07-02-40-09.jpg
  0.71464  --------  Artemis_2026-09-07-02-36-52.jpg

[EmbedServer] closed
[VectorDB] closed
```

A bit too long for 'single script' constraint but welp

:Author: jupiterbjy@gmail.com
"""

import itertools
import time
import base64
import io
import sqlite3
import pathlib
from math import ceil
from typing import Iterable, TypedDict
from argparse import ArgumentParser

import trio
import httpx
from tqdm.asyncio import tqdm
import sqlite_vec
import numpy as np
from PIL import Image

# --- Config ---

# Default llama.cpp or v1 compat endpoint url
DEFAULT_URL = "http://127.0.0.1:8081"

# Resulting embed vec dim
# TODO: support EmbeddingGemma2 256/512/768 selectable dim
EMBED_DIM: int = [256, 512, 768][-1]

# Batch size sent to endpoint, preferably match to your embedding speed
EMBED_BATCH_SIZE = 8

# Remote server timeout for each file in batch
EMBED_TIMEOUT = 60

EMBED_DB_NAME = "_embedding.sqlite"

# Image suffix mapping; also used to check supported suffixes
SUFFIX_TO_MIME: dict[str, str] = {
    ".png": "png",
    ".jpeg": "jpeg",
    ".jpg": "jpeg",
}

# Image resizing conf so one embedding doesn't take hours
IMG_WIDTH = 1280
IMG_RESIZE_THRESHOLD = round(1280 * 1.2)


# --- Util ---


def _resize_img_in_buffer(
    ext: str, img_buffer: io.BytesIO, resize_width: int, resize_threshold: int
) -> io.BytesIO:
    """Resize image in buffer if it's larger than threshold width.
    Modifies & Returns given buffer directly.
    """

    pil_img = Image.open(img_buffer)

    if pil_img.width > resize_threshold:
        pil_img = pil_img.resize(
            (resize_width, round(pil_img.height * resize_width / pil_img.width))
        )
        img_buffer.seek(0)
        img_buffer.truncate()
        # pil_img.save(img_buffer, pil_img.format)
        pil_img.save(img_buffer, ext)

    return img_buffer


class EmbedResponseObject(TypedDict):
    object: str
    index: int
    embedding: list[float]


class EmbedResponse(TypedDict):
    object: str
    data: list[EmbedResponseObject]
    # omitting etc, wont use


class EmbedPayload(TypedDict):
    input: list[str | dict]
    encoding_format: str


class EmbedServer:
    """Just a /v1 subset endpoint wrapper"""

    def __init__(self, server_url: str):
        self.url = server_url
        self.embed_endpoint = server_url + "/v1/embeddings"

        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "EmbedServer":
        self._client = httpx.AsyncClient()

        await self._raise_for_health(timeout=10)

        print(f"[EmbedServer] open for {self.url}")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
            self._client = None

        print("[EmbedServer] closed")

    @staticmethod
    def _create_img_payload(
        path_bytes_pairs: Iterable[tuple[trio.Path, bytes]],
    ) -> EmbedPayload:
        """Create payload for (mime_type, img_file_bytes) pairs"""

        # insert adogen nested code meme, lmao
        return {
            "input": [
                {
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": (
                                    f"data:image/{SUFFIX_TO_MIME[path.suffix]};base64,"
                                    f"{base64.b64encode(data).decode()}"
                                )
                            },
                        }
                    ]
                }
                for (path, data) in path_bytes_pairs
            ],
            "encoding_format": "float",
        }

    @staticmethod
    def _create_text_payload(texts: Iterable[str]) -> EmbedPayload:
        """Create payload for text strings"""

        return {"input": list(texts), "encoding_format": "float"}

    async def _raise_for_health(self, timeout: int) -> bool:
        """
        Raises:
            httpx.HTTPStatusError: yeah
            httpx.TimeoutException: when server reply did not return in time
        """

        assert self._client, "Client not initialized"

        resp = await self._client.get(self.url + "/v1/health", timeout=timeout)
        resp.raise_for_status()

        # won't do any strict checks, server better be working at this point
        return resp.json()["status"] == "ok"

    async def _post(self, payload: EmbedPayload, timeout: int) -> list[list[float]]:
        """Generate embeddings from given payload"""

        assert self._client, "Client not initialized"

        resp = await self._client.post(
            self.embed_endpoint,
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()

        resp_data: EmbedResponse = resp.json()

        return [obj["embedding"] for obj in resp_data["data"]]

    async def embed_texts(self, texts: list[str], timeout: int) -> list[list[float]]:

        return await self._post(self._create_text_payload(texts), timeout)

    async def embed_images(
        self, path_bytes_pairs: Iterable[tuple[trio.Path, bytes]], timeout: int
    ) -> list[list[float]]:

        payload = self._create_img_payload(
            path_bytes_pairs,
        )
        return await self._post(payload, timeout)


# noinspection SqlNoDataSourceInspection
class VectorDB:
    """Wraps sqlite DB w/ vector extension"""

    # will keep file mtime to see if file was updated or not
    _db_create_query = f"""
    CREATE VIRTUAL TABLE IF NOT EXISTS embeddings USING vec0(
        fn text primary key,
        +mtime float,
        v float[{EMBED_DIM}] distance_metric=cosine
    )
    """

    # since we can't truc in sqlite
    _db_del_query = f"""
    DELETE FROM embeddings;
    """

    _db_upsert_query = r"""
    INSERT OR REPLACE INTO embeddings (fn, mtime, v) VALUES (?, ?, ?)
    """

    _db_fetch_query = r"""
    SELECT mtime, v FROM embeddings WHERE fn = ?
    """

    # noinspection SqlNoDataSourceInspection
    _db_search_query = r"""
    SELECT fn, vec_distance_cosine(v, ?) AS d
    FROM embeddings WHERE v match ? and k = {}
    """

    _db_count_query = r"""
    SELECT COUNT(fn) FROM embeddings
    """

    def __init__(self, db_path: pathlib.Path, autocommit: bool = False):
        self.db_path = db_path
        self.autocommit = autocommit
        # ^^^ since my screenshots are on DB every transaction take 0.n seconds...

        self._conn: sqlite3.Connection | None = None

    def __enter__(self) -> "VectorDB":
        self._conn = sqlite3.connect(self.db_path, autocommit=self.autocommit)

        self._conn.enable_load_extension(True)
        sqlite_vec.load(self._conn)

        self._conn.execute(self._db_create_query)
        self._conn.commit()

        print(f"[VectorDB] open w/ {self.rows_count()} rows")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            self._conn.commit()
            self._conn.close()
            self._conn = None

        print("[VectorDB] closed")

    def commit(self) -> None:
        self._conn.commit()

    def truncate(self) -> None:
        self._conn.execute(self._db_del_query)
        self._conn.execute(self._db_create_query)
        self._conn.commit()

    @staticmethod
    def _serialize(vec: list[float]) -> list[float]:
        v = np.asarray(vec, dtype=np.float32)

        assert v.shape[0] == EMBED_DIM, f"expected {EMBED_DIM} dim, got {v.shape[0]}"

        # normalize to keep cosine dist stable
        # TODO: check if server already normalize this or not
        return sqlite_vec.serialize_float32(v / np.linalg.norm(v))  # type: ignore

        # --embd-normalize N
        # normalisation for embeddings (default: 2)
        # (-1=none, 0=max absolute int16, 1=taxicab, 2=euclidean, >2=p-norm)

    def upsert(self, key: str, mtime: float, embed_vec: list[float]):
        """Add/update given key & vector to DB"""

        assert self._conn, "DB not initialized"

        self._conn.execute(
            self._db_upsert_query,
            (key, mtime, self._serialize(embed_vec)),
        )
        self._conn.commit()

    def fetch(self, key: str) -> tuple[float, list[float]]:
        """Fetches recorded modification time & vector for given key"""

        assert self._conn, "DB not initialized"

        return self._conn.execute(
            self._db_fetch_query,
            (key,),
        ).fetchone()

    def query(self, query_vec: list[float], top_k: int = 5) -> list[tuple[str, float]]:
        """Perform KNN search for given query vector & return top k results

        Returns:
            [(key, cosine_similarity), ...]
        """

        assert self._conn, "DB not initialized"

        query_vec = self._serialize(query_vec)

        return [
            (path, 1.0 - d)
            for path, d in self._conn.execute(
                self._db_search_query.format(top_k),
                (query_vec, query_vec),
            ).fetchall()
        ]

    def rows_count(self) -> int:
        assert self._conn, "DB not initialized"
        return self._conn.execute(self._db_count_query).fetchone()[0]


# --- Logic ---

def _fetch_paths(root: pathlib.Path, vector_db: VectorDB) -> list[trio.Path]:
    """Returns new or updated files"""

    print("Checking new/modified images in dir")

    new_paths: list[trio.Path] = [
        trio.Path(p)
        for p in root.iterdir()
        if (
            p.suffix.lower() in SUFFIX_TO_MIME
            and (
                not (record := vector_db.fetch(p.name))
                or p.stat().st_mtime != record[0]
            )
        )
    ]
    print(f"Got {len(new_paths)} new/modified imgs")

    return new_paths


async def _producer_task(
    valid_path_list: list[trio.Path],
    send_ch: trio.MemorySendChannel[list[tuple[trio.Path, bytes]]],
) -> None:
    """Asynchronously read & resize img from dir & push to queue.
    Will check for file mtime to determine whether it needs to be updated or not
    """

    for paths in itertools.batched(valid_path_list, EMBED_BATCH_SIZE):
        batch = [
            (
                path,
                _resize_img_in_buffer(
                    SUFFIX_TO_MIME[path.suffix.lower()],
                    io.BytesIO(await path.read_bytes()),
                    IMG_WIDTH,
                    IMG_RESIZE_THRESHOLD,
                ).getvalue(),
            )
            for path in paths
        ]
        await send_ch.send(batch)


async def _consumer_task(
    vector_db: VectorDB,
    embed_server: EmbedServer,
    recv_ch: trio.MemoryReceiveChannel[list[tuple[trio.Path, bytes]]],
    total_count: int,
) -> None:
    """Get image embedding vector in batch & add to DB"""

    batch_timeout = EMBED_TIMEOUT * EMBED_BATCH_SIZE

    # flush stdout so tqdm dont mess up lines
    print(end="", flush=True)

    # noinspection PyTypeChecker
    # bar = tqdm(recv_ch, total=ceil(total_count / EMBED_BATCH_SIZE))
    bar = tqdm(total=ceil(total_count / EMBED_BATCH_SIZE), unit="batch")

    async def _task() -> None:
        async for batch in recv_ch:
            for (path, _), embedding in zip(
                batch, await embed_server.embed_images(batch, batch_timeout)
            ):
                vector_db.upsert(path.name, (await path.stat()).st_mtime, embedding)
            vector_db.commit()
            bar.update(1)

    # run 2 to ensure at least 1 batch is always queued in remote
    async with trio.open_nursery() as nursery:
        for _ in range(2):
            # noinspection PyTypeChecker
            nursery.start_soon(_task)

    bar.close()


async def query_image(
    url: str, root: pathlib.Path, query: str, top_k: int,
) -> list[tuple[pathlib.Path, float]]:
    """Query top k similar imgs via text query.

    For import use in far future, maybe

    Returns:
        [(path, similarity), ...]
    """

    with VectorDB(root / EMBED_DB_NAME) as vec_db:
        async with EmbedServer(url) as embed_server:
            vec_key: list[float] = (
                await embed_server.embed_texts([query], EMBED_TIMEOUT)
            )[0]

        return [
            (root / fn, sim) for fn, sim in vec_db.query(vec_key, top_k)
        ]


async def index_image(url: str, root: pathlib.Path, force_reindex: bool) -> int:
    """Index imgs in given dir and updates/creates db.
    Uses file mtime to determine if a file need reindexing or not.

    For import use in far future, maybe

    Returns:
        Newly added/updated entries count.
    """

    with VectorDB(root / EMBED_DB_NAME) as vec_db:
        if force_reindex:
            print("Truncating DB")
            vec_db.truncate()

        paths = _fetch_paths(root, vec_db)

        if not len(paths):
            return 0

        async with (
            EmbedServer(url) as embed_server,
            trio.open_nursery() as nursery,
        ):
            send_ch, recv_ch = trio.open_memory_channel(0)

            nursery.start_soon(
                _consumer_task, vec_db, embed_server, recv_ch, len(paths),
            )
            async with send_ch:
                await _producer_task(paths, send_ch)

    return len(paths)


async def _query_mode_flow(
    url: str, root: pathlib.Path, query: str, top_k: int,
) -> None:

    key_sim_pairs = await query_image(url, root, query, top_k)

    print(f"\nQuery:\n{query}")
    print(f"\nTop-{top_k}:")

    # display cos similarity & delta from prev one so it's a bit easier to read
    for idx, (path, sim) in enumerate(key_sim_pairs[:-1]):
        print(f"  {sim:.5f}  +{sim - key_sim_pairs[idx + 1][1]:.5f}  {path.name}")

    print(f"  {key_sim_pairs[-1][1]:.5f}  --------  {key_sim_pairs[-1][0].name}\n")

    # also display full path so I can ctrl click in term to quickly check
    for path, _ in key_sim_pairs:
        print(f"'{path.absolute()}'")

    print()


async def _index_mode_flow(
    url: str, root: pathlib.Path, force_reindex: bool,
) -> None:

    print(
        f"Batch: {EMBED_BATCH_SIZE}",
        f"Resize width: {IMG_WIDTH}",
        f"Resize threshold: {IMG_RESIZE_THRESHOLD}\n",
        sep="\n",
    )

    start_t = time.time()
    file_count = await index_image(url, root, force_reindex)
    delta_t = time.time() - start_t

    if not file_count:
        return

    print(
        f"\nIndexed {file_count} new/modified files in {delta_t:.2f} "
        f"({file_count / delta_t:.3f}/s)\n"
    )


# --- Driver ---

async def main(url: str, root: pathlib.Path, force_reindex: bool, query: str, top_k: int):

    if query:
        await _query_mode_flow(url, root, query, top_k)
        return

    await _index_mode_flow(url, root, force_reindex)


if __name__ == "__main__":
    _parser = ArgumentParser()

    _parser.add_argument(
        "dir",
        type=pathlib.Path,
        help="Directory containing images",
    )
    _parser.add_argument(
        "-r",
        "--remote",
        type=str,
        default=DEFAULT_URL,
        help="Embedding server url:port, preferably from llama.cpp",
    )
    _parser.add_argument(
        "-f",
        "--force-reindex",
        action="store_true",
        help="If true, nukes DB & recreate during index. For debugging convenience"
    )
    _parser.add_argument(
        "-q",
        "--query",
        type=str,
        help="Queries DB with given text instead of indexing",
    )
    _parser.add_argument(
        "-k",
        "--top-k",
        type=int,
        default=5,
        help="Number of results to return for query",
    )

    _args = _parser.parse_args()

    assert _args.dir.is_dir(), f"Given path is not a directory: {_args.dir}"

    trio.run(main, _args.remote, _args.dir, _args.force_reindex, _args.query, _args.top_k)
