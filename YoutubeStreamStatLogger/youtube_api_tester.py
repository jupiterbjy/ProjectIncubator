"""
Setting this up everytime in interpreter ain't fun. So just import this in interpreter.
Will look for google api from file named `api_key` on cwd, will ask for api if there's
no file.
"""

from googleapiclient.discovery import build


YOUTUBE_API_SERVICE = "youtube"
YOUTUBE_API_VERSION = "v3"
API_FILE = "api_key"


try:
    with open(API_FILE) as _fp:
        api_key = _fp.read()
except FileNotFoundError:
    api_key = input("api key: ")


def build_video_resource():
    youtube = build(YOUTUBE_API_SERVICE, YOUTUBE_API_VERSION, developerKey=api_key)
    video_instance = youtube.videos()

    return video_instance

