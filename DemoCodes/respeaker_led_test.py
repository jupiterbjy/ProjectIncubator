"""
Simple script to test Respeaker product's LED & button

pixel_ring module is from:
https://github.com/respeaker/pixel_ring

2023-02-16 jupiterbjy
"""

import time
from typing import Dict, Tuple

import trio
from pixel_ring.apa102 import APA102
from RPi import GPIO

# CONFIG SECTION ------------------------------------
# number of LED in your model - for 6ch model it's 12
LED_COUNT = 12

# long press n seconds to stop script
LONG_PRESS_SEC = 3

# button state checking interval
CHECK_INTERVAL = 0.25

# how long should led stay lit?
LED_LIT_DURATION = CHECK_INTERVAL

# LED color?
LED_COLOR = (0, 100, 0)
# ---------------------------------------------------


# gpio id of button
BUTTON = 26

# LED driver & state
LED_DRIVER = APA102(LED_COUNT)
LED_STATE: Dict[int, Tuple[int, int, int]] = {}

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN)


async def activate_led(led_id, rgb: Tuple[int, int, int], duration=1.):
    """Activates LED for designated duration"""

    # cache LED's current color & overwrite with new color
    last_state = LED_STATE.get(led_id, (0, 0, 0))
    LED_STATE[led_id] = rgb

    # save color in buffer then send buffer.
    LED_DRIVER.set_pixel(led_id, *rgb)
    LED_DRIVER.show()

    # wait for designated duration
    await trio.sleep(duration)

    del LED_STATE[led_id]
    LED_DRIVER.set_pixel(led_id, *last_state)
    LED_DRIVER.show()


async def main():
    # calculate how many button pressed state combos are needed to terminate script
    combo = 0
    combo_required = int(LONG_PRESS_SEC / CHECK_INTERVAL)

    # prepare nursery - explicit concurrency is quite nice
    async with trio.open_nursery() as nursery:
        print(f"Script started - press button for {LONG_PRESS_SEC}s to stop.")

        while combo < combo_required:
            # get button state - somehow it's inverted
            state = not GPIO.input(BUTTON)

            # if btn is pressed state then activate led using combo as led_id
            if state:
                nursery.start_soon(activate_led, combo, LED_COLOR)
                combo += 1
            else:
                combo = 0

            print(f"combo: {combo:2} | state: {LED_STATE}")
            await trio.sleep(LED_LIT_DURATION)

    # stop led & disconnect driver
    LED_DRIVER.clear_strip()
    LED_DRIVER.cleanup()


trio.run(main)
