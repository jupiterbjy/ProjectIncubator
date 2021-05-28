import re
import itertools
from typing import Tuple

import requests


def video_list_gen(channel_id: str, max_results: int) -> Tuple[str]:

    # Compile regex pattern
    pattern = re.compile(r'videoIds"[^"]*"([^"]*)')

    url = f"https://www.youtube.com/channel/{channel_id}"

    # Prepare session
    with requests.session() as session:
        while True:
            get = session.get(url)
            vid_ids = pattern.findall(get.text)

            print(get.status_code)

            # Fetch unique keys in appearing order, streams are likely to appear at top.
            yield tuple(k for (k, v), _ in zip(itertools.groupby(vid_ids), range(max_results)))
