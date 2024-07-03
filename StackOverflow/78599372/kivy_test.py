import asyncio

from kivy.app import App, Builder
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.widget import Widget

import selenium.webdriver


# --- CONFIG ---

HEADLESS = True

DRIVER = "Edge"

KV_LAYOUT_STR = """
<MainWidget>:
    # bidirectional bind
    # https://stackoverflow.com/a/44635831/10909029
            
    url_text: id_url_input.text
            
    BoxLayout:
        orientation: "vertical"
        size: root.size

        BoxLayout:
            orientation: "horizontal"
            size_hint_y: 0.1
                    
            TextInput:
                id: id_url_input
                text: root.url_text
                hint_text: "url..."
            
            Button:
                size_hint_x: 0.2
                disabled: root.btn_disabled
                text: "Fetch"
                on_release: root.press_action()
        
        TextInput:
            readonly: True
            id: id_output_label
            text: root.output_text
            hint_text: "Press Fetch to display data here..."
"""


# --- CODE ---


class SeleniumWrapper:

    def __init__(self, headless=False):
        # option for headless mode
        self.option = getattr(selenium.webdriver, DRIVER + "Options")()
        if headless:
            self.option.add_argument("--headless")

        self.driver = getattr(selenium.webdriver, DRIVER)(options=self.option)

    async def visit(self, url):
        """Visit a URL and return the page source asynchronously"""

        await asyncio.to_thread(self.driver.get, url)
        return self.driver.page_source


class MainWidget(Widget):

    # Properties that are updated bidirectionally
    url_text = StringProperty()
    output_text = StringProperty()
    btn_disabled = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.url_text = "https://noctua.at/"
        self.selenium = SeleniumWrapper(HEADLESS)

    async def _visit_wrapper(self):
        """Disables the button and visit the URL, and enables once done"""

        # disable the button
        self.btn_disabled = True
        self.output_text = "Fetching data..."

        # visit the URL & get the page source
        page_source = await self.selenium.visit(self.url_text)
        self.output_text = page_source

        # enable the button
        self.btn_disabled = False

    def press_action(self):
        """Action on button release"""

        asyncio.create_task(self._visit_wrapper())


# --- DRIVER ---


class AsyncApp(App):
    def build(self):
        Builder.load_string(KV_LAYOUT_STR)
        return MainWidget()

    async def app_func(self):
        # Run the app asynchronously
        await self.async_run("asyncio")


if __name__ == "__main__":
    asyncio.run(AsyncApp().app_func())
