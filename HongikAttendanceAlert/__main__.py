"""
Primitive script to check upcoming attendance check.
"""


from datetime import datetime
import random
import time

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import UnexpectedAlertPresentException, WebDriverException


child_xpath = ".//*"
url = "https://at.hongik.ac.kr/stud01.jsp"
time_range = 10, 15


def determine_status(driver: webdriver.Firefox):

    # Loop to check if site is loaded - less likely to be in loop more than once.
    while True:
        time.sleep(0.5)

        children = driver.find_elements_by_xpath("//tbody")[0]
        if children:
            break

    # Check if there's new attendance check
    if "[" not in children.text:
        print(datetime.now(), "No hit")
        return

    print(datetime.now(), children.text)
    for _ in range(3):
        print("\a")
        time.sleep(0.1)


def check_silence_alert(driver: webdriver.Firefox):
    try:
        assert driver.current_url == url
    except (UnexpectedAlertPresentException, AssertionError):
        return True

    return False


def main():

    # Prime driver
    capability = DesiredCapabilities().FIREFOX
    capability["pageLoadStrategy"] = "eager"
    driver = webdriver.Firefox(capabilities=capability)

    # wait for site login
    driver.get(url)
    time.sleep(1)

    while check_silence_alert(driver):
        time.sleep(1)
    else:
        time.sleep(5)

    # main loop
    while True:
        driver.refresh()
        determine_status(driver)
        time.sleep(random.randint(*time_range))


if __name__ == '__main__':
    try:
        main()
    except WebDriverException:
        print("Browser is closed.")
