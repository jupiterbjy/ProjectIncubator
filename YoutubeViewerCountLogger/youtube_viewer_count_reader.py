#!/usr/bin/python

import pathlib
import json
from sys import argv, exit

from matplotlib import pyplot
from matplotlib.font_manager import FontProperties


font = FontProperties(fname=pathlib.Path("Font/NotoSansMonoCJKkr-Regular.otf"))


def plot_main(mapping):
    title = mapping["stream_title"]
    interval = mapping["interval"]

    data = mapping["data"]

    pyplot.title(title, fontproperties=font)

    pyplot.plot(data["viewCount"], color='cornflowerblue')
    pyplot.plot(data["concurrentViewers"], color='orange')
    pyplot.plot(data["likeCount"], color='green')
    pyplot.plot(data["dislikeCount"], color='red')

    pyplot.xlabel(f"time({interval}sec unit)")

    # determine min-max viewers
    max_val = max(data["viewCount"])
    pyplot.yticks([n for n in range(0, max_val + 1, max_val//10)])
    pyplot.show()


if __name__ == '__main__':
    try:
        with open(argv[-1], encoding="utf8") as fp:
            loaded_data = json.load(fp)
    except FileNotFoundError:
        print(f"File {argv[-1]} does not exist.")
        exit()

    plot_main(loaded_data)
