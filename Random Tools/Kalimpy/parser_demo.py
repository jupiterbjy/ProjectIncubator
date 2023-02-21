"""
Prototyping playground
"""
from typing import Sequence

import winsound

import trio

from parser.parser import tune, TabLine, tab_parser


async def playback_task(freq, duration):
    await trio.to_thread.run_sync(winsound.Beep, int(freq), duration)


async def async_player(tab_lines: Sequence[TabLine]):
    duration = 200
    fade_duration = 400

    async with trio.open_nursery() as nursery:
        for line_idx, tab_line in enumerate(tab_lines):
            print(f"Line {line_idx}")

            for tab_idx, tab in enumerate(tab_line):
                print(f"{tab_idx:3}|{tab.alphabetic:3}| {tab}")
                if tab.frequency:
                    nursery.start_soon(playback_task, tab.frequency, fade_duration)

                await trio.sleep(duration / 1000)


if __name__ == '__main__':
    import winsound

    line_1 = r"1' 1'2' 2' 1' 1'3' 4'3' 1' 1'2' 2' 1' 1' 7 1' /"
    line_2 = r"5 1'  5' 2' 1'  5 1'1'2' 3'2' 1'3'   5 1'  5' 2' 1'4'3' 2' 1'2'3' 4'3'1'  2' /"
    tune("C4 D4 E4 F4 G4 A4 B4 C5 D5 E5 F5 G5 A5 B5 C6 D6 E6".split())

    parsed = [TabLine(tab_parser(line)) for line in (line_1, line_2)]

    trio.run(async_player, parsed)
