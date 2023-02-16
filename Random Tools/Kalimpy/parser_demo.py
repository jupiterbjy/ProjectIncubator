"""
Prototyping playground
"""
import winsound

import trio

from parser.parser import tune, TabLine, tab_parser


async def playback_task(freq, duration):
    await trio.to_thread.run_sync(winsound.Beep, int(freq), duration)


async def async_player(tab_line: TabLine):
    duration = 200
    fade_duration = 400

    async with trio.open_nursery() as nursery:
        for idx, tab in enumerate(tab_line):
            print(f"{idx:3}|{tab.alphabetic:3}| {tab}")
            if tab.frequency:
                nursery.start_soon(playback_task, tab.frequency, fade_duration)

            await trio.sleep(duration / 1000)


if __name__ == '__main__':
    import winsound

    line = r"1' 1'2' 2' 1' 1'3' 4'3' 1' 1'2' 2' 1' 1' 7 1' /"
    tune("C4 D4 E4 F4 G4 A4 B4 C5 D5 E5 F5 G5 A5 B5 C6 D6 E6".split())

    parsed = TabLine(tab_parser(line))
    trio.run(async_player, parsed)
