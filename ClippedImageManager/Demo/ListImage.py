import logging
import trio

# kivy imports
from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty


logger = logging.getLogger("Demo")
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("[%(levelname)s][%(funcName)s] %(asctime)s - %(msg)s %(args)s"))
logger.addHandler(_handler)
logger.setLevel("DEBUG")


class ImageWidget(ButtonBehavior, BoxLayout):
    source = StringProperty(None)

    def __init__(self, id_num, image_path, **kwargs):
        super().__init__(**kwargs)
        self.id = id_num
        self.source = image_path

    def on_click(self):
        logger.debug(f"Click on {self.id}")


class MainUI(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reference = []

        image_tuple = ("{8EBA960C-09D4-4F5C-A926-AD6A13D37838}.png",
                       "{D1904FA5-2229-4AA6-98C7-089627EA930C}.png")

        for idx, image_path in enumerate("sample/" + image_name for image_name in image_tuple):
            widget_instance = ImageWidget(idx, image_path)

            self.add_widget(widget_instance)
            self.reference.append(widget_instance)

            logger.debug(f"Adding widget {widget_instance}")


class MainUIApp(App):

    def __init__(self, **kwargs):
        super(MainUIApp, self).__init__(**kwargs)

    def build(self):
        Builder.load_file("UI.kv")
        return MainUI()

    async def app_functions(self):
        """
        Main execution part in trio event loop.
        """

        async with trio.open_nursery() as nursery:
            nursery.start_soon(self._run_self, nursery)

    async def _run_self(self, nursery: trio.Nursery):
        logger.debug("Running app")

        await self.async_run("trio")
        nursery.cancel_scope.cancel()

        logger.debug("App stopped")


if __name__ == '__main__':
    trio.run(MainUIApp().app_functions)
