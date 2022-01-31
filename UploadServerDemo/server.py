"""
Author: jupiterbjy@gmail.com
Copyright: MIT

---
## Introduction

Demo Code for file upload - tested on CPython3.10

Runs drastically faster on CPython due to C Library translation in pypy3.

---
## How to use


To send api call:
POST http://127.0.0.1:8000/file with Multipart file attachment.

"""
import argparse
import time
import hashlib
from configparser import ConfigParser
from typing import Union

import trio
import trio_mysql
from hypercorn import Config
from hypercorn.trio import serve
from fastapi import FastAPI, UploadFile


app = FastAPI()


# ENV VARS ================================================
ROOT: trio.Path = trio.Path(__file__).parent
UPLOAD: trio.Path = ROOT.joinpath("uploaded")

CONFIG = ConfigParser()

DB_CONNECTION: Union[trio_mysql.Connection, None] = None
NURSERY: Union[trio.Nursery, None] = None
# =========================================================


@app.post("/file")
async def file_upload(file: UploadFile) -> str:
    """
    POST route.

    Args:
        file: File object passed by FastAPI

    Returns:
        Short string "Success"
    """

    print("RECV - " + file.filename)

    # When this is called, file is already cached.
    # Pass it to global nursery immediately.
    # Meanwhile, I am not sure how this is possible, is it downloading somewhere?
    # No info on documents afaik
    NURSERY.start_soon(write_to_file, file)
    return "Success"


async def write_to_file(file: UploadFile):
    """
    Write the file into Filesystem, and add new record to DB.

    Args:
        file: File object passed by FastAPI
    """

    # prep hash
    md5 = hashlib.md5()

    # use epoch time as temp file name while copying/downloading.
    save_file = UPLOAD.joinpath(str(time.time_ns()))

    # keep ref because there's too many access
    file_name = file.filename

    # Open file and read 2**20 chunks unit.
    # feeds to hasher and to temp file same time. Efficiency! (I hope)
    async with await save_file.open("wb") as fp:
        while data := await file.read(1048576):
            await fp.write(data)
            md5.update(data)

        print("RECV DONE - " + file_name)

    # START TRANSACTION
    async with DB_CONNECTION.transaction():
        async with DB_CONNECTION.cursor() as cursor:

            # insert new record with received file's name & it's hash
            await cursor.execute(
                "INSERT INTO main (file_name, hash) VALUES (%s, %s)",
                (file_name, md5.hexdigest()),
            )

            # Send command for selecting lastly inserted record autoincrement ID.
            # Transaction hides the record until commit, totally safe.
            await cursor.execute("SELECT LAST_INSERT_ID();")

            # if there's file extension, keep it
            # then rename file with record ID.
            suffix = "." + file_name.split('.')[-1] if "." in file_name else ""
            new_name = f"{(await cursor.fetchone())[0]}{suffix}"

    await save_file.rename(save_file.with_name(new_name))
    print(f"DB COMMIT DONE; RENAMING {file_name} to {new_name}")


def get_db_connection() -> trio_mysql.Connection:
    """
    Convenience function for DB connection.

    Returns:
        MySQL Connection
    """

    return trio_mysql.connect(
        host="localhost",
        user=CONFIG["db"]["user"],
        password=CONFIG["db"]["password"],
        db=CONFIG["db"]["db"],
        charset="utf8mb4",
        # cursorclass=trio_mysql.cursors.DictCursor,
    )


async def main_task():
    """
    Main task to fire up all necessary setup and guarantee DB shutdown.
    """

    global DB_CONNECTION, NURSERY

    await UPLOAD.mkdir(exist_ok=True)
    # mkdir if file doesn't exist

    async with trio.open_nursery() as nursery:
        # Store Nursery to global namespace
        NURSERY = nursery

        async with get_db_connection() as connection:
            # Store connection to global namespace
            DB_CONNECTION = connection

            try:
                # start server
                await serve(app, cornfig)
            finally:
                # guarantee DB connection to be closed on exception.
                await connection.aclose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        type=trio.Path,
        default=ROOT.joinpath("db_conf.ini"),
        help="Path to the configuration ini file.",
    )

    # parse args
    args = parser.parse_args()

    # read configuration file
    CONFIG.read(args.config)

    # HyperCorn's config, so Cornfig. I'm sorry.
    cornfig = Config()
    cornfig.bind = "localhost:8000"

    trio.run(main_task)
