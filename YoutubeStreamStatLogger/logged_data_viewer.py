#!/usr/bin/python

"""
Simple plot viewer for my own accumulated data.
"""

import itertools
import pathlib
import json
from array import array
from sys import argv, exit
from typing import Tuple, Generator

from matplotlib import pyplot
from matplotlib.font_manager import FontProperties


font = FontProperties(fname=pathlib.Path("Font/NotoSansMonoCJKkr-Regular.otf"))


def viewer_fluctuation_data(total_view, concurrent_view) -> Tuple[array, array]:
    def view_diff_gen(source):
        yield 0

        iterator = zip(source, itertools.islice(source, 1, None))

        for previous, current in iterator:
            yield current - previous

    total_view_diff_gen = view_diff_gen(total_view)
    live_view_diff_gen = view_diff_gen(concurrent_view)

    # Total view counts goes up until unknown certain point,
    # if video was re-watched more than 30 sec during session.

    # total_dif == added number of stream viewers, total_dif - live_dif == viewers left stream
    total_view_diff = array("i", total_view_diff_gen)
    live_view_diff = array("i", (total - live for total, live in zip(total_view_diff, live_view_diff_gen)))

    live_view_gain = array("i", (n if n > 0 else 0 for n in live_view_diff))
    live_view_left = array("i", (n if n < 0 else 0 for n in live_view_diff))


    return live_view_gain, live_view_left


def plot_main(mapping):
    title = mapping["stream_title"]
    interval = mapping["interval"]

    data = mapping["data"]
    live_gain, live_left = viewer_fluctuation_data(data["viewCount"], data["concurrentViewers"])

    live_loss_total = sum(live_left)
    live_gain_total = sum(live_gain)
    gain_total = max(data["viewCount"]) - min(data["viewCount"])

    fig, ax = pyplot.subplots(2, 1, figsize=(16, 8))
    fig.canvas.set_window_title(f"Gain total: {gain_total} / "
                                f"Live gain total: {live_gain_total} / "
                                f"Live loss total: {live_loss_total}")

    # Plot 1
    ax[0].set_title(title, fontproperties=font)
    ax[0].plot(data["viewCount"], color='cornflowerblue', label="Total views")
    ax[0].plot(data["concurrentViewers"], color='orange', label="Live viewers")
    ax[0].plot(data["likeCount"], color='green', label="Upvote")
    ax[0].plot(data["dislikeCount"], color='red', label="Downvote")
    ax[0].set_xlabel(f"time({interval}sec unit)")
    ax[0].legend()

    # determine min-max viewers
    max_val = max(data["viewCount"])
    ax[0].set_yticks([n for n in range(0, max_val + 1, max_val//10)])

    # Plot 2
    ax[1].plot(live_gain, color="green", label="Viewer gain approx.")
    ax[1].plot(live_left, color="red", label="Viewer loss approx.")
    ax[1].legend()

    pyplot.show()


if __name__ == '__main__':
    try:
        with open(argv[-1], encoding="utf8") as fp:
            loaded_data = json.load(fp)
    except FileNotFoundError:
        print(f"File {argv[-1]} does not exist.")
        exit()

    plot_main(loaded_data)
