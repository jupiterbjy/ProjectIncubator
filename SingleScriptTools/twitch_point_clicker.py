"""
Dumb script that looks for twitch points button element on chat and clicks it

:Author: jupiterbjy@gmail.com
"""

import time

from selenium import webdriver


xpath_form = "//{type}[@{attribute}='{attribute_value}']"


def routine(driver, input_xform: str):
    while True:
        time.sleep(1)
        element = driver.find_elements_by_xpath(input_xform)
        if element:
            print("Found element")
            element[0].click()


def main():
    driver = webdriver.Chrome()
    routine(driver, xpath_form.format_map({"type": "button", "attribute": "aria-label", "attribute_value": "보너스 받기"}))


if __name__ == '__main__':
    main()
