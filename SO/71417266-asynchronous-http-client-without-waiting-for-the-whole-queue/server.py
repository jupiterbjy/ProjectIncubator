"""
Demo codes for https://stackoverflow.com/questions/71417266
"""

import trio
from quart import request, jsonify
from quart_trio import QuartTrio


app = QuartTrio("Very named Much app")


@app.get("/json")
async def send_json():
    """
    Sleeps 5 + n seconds before returning response.

    Returns:
        json response
    """
    key = int(request.args["key"])

    await trio.sleep(5 + key)
    return jsonify({"key": key})


trio.run(app.run_task)
