"""
Simple script to spin up ReSpeaker's LED once pi is fully booted &
connected to wireless network.

This script will show CPU usage via LED until network is connected.

Once connected, this will keep spinning designated LED pattern until
a button press - which is to prevent myself slacking off indefinitely
not realizing pi has already booted.

2023-02-23 jupiterbjy
"""

from functools import partial

import psutil
import trio
from pixel_ring.apa102 import APA102
from RPi import GPIO


# CONFIG SECTION ------------------------------------
# Brightness %
BRIGHTNESS = 30

# LED pattern - 12 LED for 6ch model
LED_READY_PATTERN = [
    (255, 25, 251), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
    (255, 25, 251), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
]

# Network waiting LED color
LED_WAIT_COLOR = (255, 25, 25)

# CPU utilization check interval in seconds
CPU_CHECK_INTERVAL = 0.5

# LED spinning rpm - This also affect button state polling rate
RPM = 120
# ---------------------------------------------------


# gpio id of button
BUTTON = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN)


async def check_network_task(driver: APA102):

    # bring check function & names to local for speedup
    def connected():
        # noinspection PyUnresolvedReferences
        return "run" in psutil.net_if_stats()["wlan0"].flags

    check_cpu_util = partial(psutil.cpu_percent, None)

    # keep names to local for more speedup
    led_count = len(LED_READY_PATTERN)
    on_color = (*LED_WAIT_COLOR, BRIGHTNESS)
    off_color = (0, 0, 0, BRIGHTNESS)
    interval = CPU_CHECK_INTERVAL

    # call once to mark last call time
    check_cpu_util()

    while not connected():
        await trio.sleep(interval)

        # convert CPU utilization to LED
        active_led_count = int(check_cpu_util() * 100 / led_count)

        # update strip
        for led_idx in range(active_led_count):
            driver.set_pixel(led_idx, *on_color)

        for led_idx in range(active_led_count, led_count):
            driver.set_pixel(led_idx, *off_color)

        # send buffer
        driver.show()


async def check_button_task(driver: APA102):

    # by default non-pressed state is 1 and pressed state is 0, hence it sounds reversed.
    button_not_pressed = partial(GPIO.input, BUTTON)

    # calculate wait time
    interval = 60 / RPM / len(LED_READY_PATTERN)

    # print pattern
    for led_idx, color in enumerate(LED_READY_PATTERN):
        driver.set_pixel(led_idx, *color, BRIGHTNESS)

    while button_not_pressed():
        await trio.sleep(interval)

        # rotate
        driver.rotate()
        driver.show()


async def main():
    driver = APA102(len(LED_READY_PATTERN))

    await check_network_task(driver)
    await check_button_task(driver)

    # stop led & disconnect driver
    driver.clear_strip()
    driver.cleanup()


trio.run(main)
