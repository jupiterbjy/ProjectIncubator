"""
Fetches transcript from YouTube video
Currently broken as API is gone, will rewrite again when I need this

`pip install youtube-transcript-api, httpx`

:Author: jupiterbjy@gmail.com
"""

# from argparse import ArgumentParser
from typing import Iterable, Tuple, Dict, List, Any
from urllib import parse
import urllib.request
import json

from youtube_transcript_api import YouTubeTranscriptApi

# import trio
import httpx


async def fetch_json(
    vid_id, async_context: httpx.AsyncClient = None, **kwargs
) -> Dict[str, Any]:
    params = {
        "format": "json",
        "url": f"https://www.youtube.com/watch?v={vid_id}",
    } | kwargs
    query_string = f"https://www.youtube.com/oembed?{parse.urlencode(params)}"

    if not async_context:
        async_context = httpx.AsyncClient()

    async with async_context:
        resp = await async_context.get(query_string)

    return json.loads(resp.read())


def fetch_transcript(vid_id, **kwargs) -> Tuple[str, List[Dict[str, Any]]]:
    params = {
        "format": "json",
        "url": f"https://www.youtube.com/watch?v={vid_id}",
    } | kwargs
    url = "https://www.youtube.com/oembed"

    query_string = parse.urlencode(params)
    url = url + "?" + query_string

    print(f"Fetching from {url}")

    with urllib.request.urlopen(url) as response:
        response_text = response.read()
        title = json.loads(response_text.decode())["title"]

    # retrieve the available transcripts
    transcript_list = YouTubeTranscriptApi.list_transcripts(vid_id)

    return title, transcript_list.find_transcript(["en"]).fetch()


def fetch_transcript_gen(vid_ids: Iterable):
    for video_id in vid_ids:
        yield fetch_transcript(video_id)


if __name__ == "__main__":
    from pprint import pprint

    for title_, data_ in fetch_transcript_gen(
        ["LfC6pv8VISk", "befUVytFC80", "4c_rKOaTquM"]
    ):
        print(f"\nTitle: {title_}\nData length: {len(data_)}\n")
        pprint(data_)
