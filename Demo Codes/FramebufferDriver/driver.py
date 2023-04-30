"""
RPi Frame Buffer Driver using pygame.

Primarily intended for weak devices like 1B+ where even mere x server is too heavy.

Uses trio to await for extra stability & safety.

Following is referenced from:
https://stackoverflow.com/a/54986161/10909029
"""

import time
import pathlib

import pygame
import trio


# Splash file to show up on framebuffer for testing
ROOT = pathlib.Path(__file__).parent
TEST_SPLASH_FILE = ROOT / "splash.png"

# Test screen via
# while true; do sudo cat /dev/urandom > /dev/fb1; sleep .01; done
# sudo fbi -T 2 -d /dev/fb1 -noverbose -a splash.png


class FramebufferDriver:

    def __init__(self, screen_x, screen_y, fb_id=0):
        """Initializes a new pygame screen using the Frame Buffer.

        Args:
            screen_x: Screen X pixels
            screen_y: Screen Y pixels
            fb_id: Framebuffer ID. Default 0

        Raises:
            NoUsableDriverError: If there's no usable framebuffer drivers
        """

        self.dim = (screen_x, screen_y)
        self.fb = trio.Path(f"/dev/fb{fb_id}")
        # leaving file open is not safe usually, but for framebuffer why not.

        print(f"Using {self.fb}")

        # Safe to call init multiple time anyway!
        pygame.init()
        self.screen = pygame.Surface(self.dim)

    def update_sync(self):
        """Synchronous framebuffer."""

        with open(self.fb, "wb") as fp:
            # noinspection PyTypeChecker
            fp.write(self.screen.convert(16, 0).get_buffer())

    async def update(self):
        """Update framebuffer."""

        # there's option to set pygame in 16bit, might need to check that out
        await self.fb.write_bytes(self.screen.convert(16, 0).get_buffer())

    def __del__(self):
        """Destructor to make sure pygame shuts down, etc."""

    def test(self):
        """Shows splash image"""

        # basically

        self.screen.blit(pygame.image.load(TEST_SPLASH_FILE.as_posix()), (0, 0))
        self.update_sync()

    def blank(self):
        self.screen.fill((0, 0, 0))


if __name__ == "__main__":
    # Create an instance of the PyScope class, assuming rpi, 480 320
    driver = FramebufferDriver(480, 320, 1)
    driver.test()
    time.sleep(10)
    driver.blank()
