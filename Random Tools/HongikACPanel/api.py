"""
Experimental AC control code
Some a bit of improved code to discard need of Seleinum and chrome/firefox driver

Python 3.10+
2022-09-08 / 2023-03-09
jupiterbjy@gmail.com

References:
https://www.python-httpx.org/quickstart/
https://developer.mozilla.org/docs/Learn/Forms/Sending_and_retrieving_form_data
"""

import re
import functools
import argparse
from random import randint
from typing import Dict

import trio
import httpx

from bs4 import BeautifulSoup as bs

from loguru import logger


URL = "http://ENTER_IP_HERE/"
REMOTE_URL = URL + "webremo"

# AC mode translation list
OPERATION_MODE = ["Heating", "Cooling", "Fan only"]
WIND_SPEED_MODE = ["Auto", "Max", "medium", "low"]
WIND_DIRECTION_MODE = ["Swing", "Horizontal", "Vertical"]


class ACState:
    """
    Simplified web remote status representation from Parsed HTML.
    """

    """
    <MEMO>
    Guessed from html source & images

    <ip>/images/nn_0.gif = Heating
    <ip>/images/nn_1.gif = Cooling
    <ip>/images/nn_2.gif = Fan only
    Used with ID:
        Image_1 -> Showing current AC mode


    <ip>/images/Tem_xx.gif = Temp. XX being celcius displayed on image
    Used with ID:
        Image_2 -> current indoor temp
        Image_3 -> current target temp


    <ip>/images/mm_0.gif = Wind speed auto
    <ip>/images/mm_1.gif = Wind speed max
    <ip>/images/mm_2.gif = Wind speed medium
    <ip>/images/mm_3.gif = Wind speed low
    Used with ID:
        Image_4 -> current wind speed setting


    <ip>/images/kk_0.gif = Wind direction Swinging
    <ip>/images/kk_1.gif = Wind direction Horizontal
    <ip>/images/kk_2.gif = Wind direction Vertical
    Used with ID:
        Image_5 -> current wind direction setting
    """

    # Not sure if we need regex...but whatever
    # regex to find ID in temp image's name

    pattern = re.compile(r"\d+")

    def __init__(self, resp: httpx.Response):
        self.soup = bs(resp.content.decode(), "html.parser")

    def _pattern_match(self, src: str) -> int:
        return int(self.pattern.search(src)[0])

    @functools.cached_property
    def states(self) -> Dict[str, str]:
        """
        Gets __VIEWSTATE, __VIEWSTATEGENERATOR, __EVENTVALIDATION
        values from soup.
        """

        return {
            id_: self.soup.find("input", {"id": id_}).attrs["value"]
            for id_ in ("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION")
        }

    @functools.cached_property
    def operation_mode(self) -> str:
        """Determines operation mode"""

        img_src = self.soup.find("img", {"id": "Image_1"})["src"]
        return OPERATION_MODE[self._pattern_match(img_src)]

    @functools.cached_property
    def current_temp(self) -> int:
        """
        Gets current temperature.
        """

        img_src = self.soup.find("img", {"id": "Image_2"})["src"]
        return self._pattern_match(img_src)

    @functools.cached_property
    def target_temp(self) -> int:
        """
        Gets target temperature.
        """

        img_src = self.soup.find("img", {"id": "Image_3"})["src"]
        return self._pattern_match(img_src)

    @functools.cached_property
    def wind_speed(self) -> str:
        """Determines operation mode"""

        img_src = self.soup.find("img", {"id": "Image_4"})["src"]
        return WIND_SPEED_MODE[self._pattern_match(img_src)]

    @functools.cached_property
    def wind_angle(self) -> str:
        """Determines operation mode"""

        img_src = self.soup.find("img", {"id": "Image_5"})["src"]
        return WIND_DIRECTION_MODE[self._pattern_match(img_src)]

    # TODO: add permission checks


class ACManager:
    """
    AC controller class.
    """

    """
    <MEMO>
    Guessed from html source & images

    hdnNo list:
    1 = 0: off, 1: on
    2 = 25 | Minimum?
    3 = 1 0: Unknown, 1: Cooling mode, 2: Unknown
    4 = Target temp
    5 = 0
    6 = 0: On/Off perm, 2: Off perm, else: No perm -> to hdnNo_1
    7 = 0
    8 = 1 | 0: Mode change perm, else: No perm (No UI control avail.) -> to hdnNo_8

    10 = 1
    11 = 1
    12 = 29 AC upper temp lim, must be < 29
    13 = 25 AC lower temp lim, must be 
    14 = 1
    15 = 1
    16 = 1
    17 = 1
    18 = 1

    whichbtn = 0 Unused?

                  AC On | AC Off | T down | T up | None |
    btnSubmit.x = 94    | 108    | 95     | 41   | 55
    btnSubmit.y = 40    | 40     | 35     | 37   | 16
    """

    btn_action = {
        "on": (94, 40),
        "off": (108, 40),
        "temp_down": (95, 35),
        "temp_up": (41, 37),
        "": (55, 16),
    }

    # TODO: move base_state and associated to ACState
    base_state = {
        "hdnNo_1": 0,
        "hdnNo_2": 25,
        "hdnNo_3": 1,
        "hdnNo_4": 26,
        "hdnNo_5": 0,
        "hdnNo_6": 0,
        "hdnNo_7": 0,
        "hdnNo_8": 1,
        "hdnNo_10": 1,
        "hdnNo_11": 1,
        "hdnNo_12": 29,
        "hdnNo_13": 25,
        "hdnNo_14": 1,
        "hdnNo_15": 1,
        "hdnNo_16": 1,
        "hdnNo_17": 1,
        "hdnNo_18": 1,

        "whichbtn": 0,
        "btnSubmit.x": 55,
        "btnSubmit.y": 16,
    }

    def __init__(self, id_, password):
        self.client = httpx.AsyncClient()

        self.id_ = id_
        self.pw = password

        self.state: None | ACState = None
        self.target_temp = 0
        self.action = ""
        self.power_on = False

    async def login(self):
        """
        Performs login and follow into web remote controller site.

        Note:
            There's no login failure tolerance. I'm lazy.
        """

        # initial update
        if self.state is None:
            resp = await self.client.get(URL, follow_redirects=True)
            self.state = ACState(resp)

        payloads = self.state.states

        # adding login data
        payloads["txtId"] = self.id_
        payloads["txtPwd"] = self.pw

        # proceed login & update state
        resp = await self.client.post(URL, data=payloads, follow_redirects=True)

        resp.raise_for_status()
        logger.info(f"Login successful")

        await self.update(resp)

    async def update(self, resp: httpx.Response = None):
        """
        Manually trigger update.
        """

        if resp is None:
            resp = await self.client.get(URL, follow_redirects=True)

        self.state = ACState(resp)
        self.target_temp = self.state.target_temp
        logger.info(f"Cur. Temp      : {self.state.current_temp}")
        logger.info(f"Cur. Operation : {self.state.operation_mode}")
        logger.info(f"Cur. Wind speed: {self.state.wind_speed}")
        logger.info(f"Cur. Wind angle: {self.state.wind_angle}")

    async def keep_alive(self, interval_sec=600, deviation_max_sec=60):
        """
        Re-login and send commands again with given interval.
        Randomly adds up to deviation_max_sec to total waiting time.
        """
        logger.debug("Keepalive started")

        while True:
            sleep_duration = interval_sec + randint(0, deviation_max_sec)
            logger.info(f"Sleeping for {sleep_duration}")

            await trio.sleep(sleep_duration)
            await self.login()
            await self.send(True, self.target_temp)

    @property
    def payload(self):
        """
        Creates payload.
        """
        payload = {k: v for k, v in self.base_state.items()}
        payload["hdnNo_4"] = self.target_temp
        payload["hdnNo_1"] = 1 if self.power_on else 0

        payload["btnSubmit.x"], payload["btnSubmit.y"] = self.btn_action[self.action]

        return self.state.states | payload

    async def send(self, power: bool, temp: int):
        """
        Sends request.
        """

        # TODO: add & raise custom errors (i.e. permission, out of temp range, etc)

        self.power_on = power
        self.target_temp = temp

        logger.info("Sending request!")
        logger.debug(f"Power {self.power_on} / TGT Temp {self.target_temp}")

        resp = await self.client.post(REMOTE_URL, data=self.payload, follow_redirects=True)

        try:
            resp.raise_for_status()
        except Exception as err:
            logger.warning(f"{type(err).__name__} - {err}")
            logger.debug(f"Received response:\n{resp.content.decode()}\n")

        # await self.update()


async def main(arguments):
    logger.info("Note: This script will automatically stop AC when shutting down.")

    ac = ACManager(arguments.id, arguments.pwd)

    await ac.login()
    await ac.send(True, arguments.temp)

    try:
        await ac.keep_alive()

    except KeyboardInterrupt:
        await ac.send(False, arguments.temp)
        logger.info("Shutting down!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Controls AC")

    parser.add_argument(
        "-t",
        "--temp",
        type=int,
        default=26,
        help="Target temperature."
    )
    parser.add_argument(
        "-i",
        "--id",
        type=str,
        required=True,
        help="ID for login."
    )
    parser.add_argument(
        "-p",
        "--pwd",
        type=str,
        required=True,
        help="Password for login."
    )

    args = parser.parse_args()

    trio.run(main, args)
