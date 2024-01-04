"""
Script to automate key inputs for extracting voices from CrystalDiskInfo's voice `.DLL` files.
(C:/Program Files/CrystalDiskInfo/CdiResource/voice)

Requires Jetbrains DotPeek.

![](readme_res/cdi_voice_extract.webp)
"""

import pyautogui
import time


# number of tracks. 22 for Aoi Edition.
VOICE_COUNT = 8 + 7 + 6 + 1


def action():
    # context menu
    pyautogui.keyDown("shift")
    pyautogui.press("f10")
    pyautogui.keyUp("shift")

    # move to 4th(2nd backward)
    pyautogui.press("up")
    pyautogui.press("up")

    pyautogui.press("enter")

    # wait for modal and move caret to end while disabling selection.
    time.sleep(1)
    pyautogui.press("end")

    # change extension to .ogg
    for _ in range(3):
        pyautogui.press("backspace")

    pyautogui.write("ogg")
    pyautogui.press("enter")


def main():
    # wait for positioning
    print("Waiting for 10 sec, please select CDI_VOICE_001.")
    time.sleep(10)

    # loop
    for n in range(1, VOICE_COUNT + 1):
        print(f"Loop {n}/{VOICE_COUNT}")
        action()

        # move to next file
        pyautogui.press("down")


main()
