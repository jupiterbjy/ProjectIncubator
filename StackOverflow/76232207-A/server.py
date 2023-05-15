"""
Demo codes for https://stackoverflow.com/questions/76232207
"""

import asyncio
from random import randint

from quart import request, jsonify, Quart


app = Quart("Very named Much app")


@app.get("/json")
async def send_json():
    """
    Sleeps 0~4 seconds before returning response.

    Returns:
        json response
    """
    key = request.args["user"]
    print("Received " + key)

    await asyncio.sleep(randint(0, 4))
    return jsonify({"user": key})


asyncio.run(app.run_task())
