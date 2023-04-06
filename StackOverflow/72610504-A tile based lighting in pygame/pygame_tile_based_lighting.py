"""
Code demonstration for https://stackoverflow.com/q/72610504/10909029
Written on Python 3.10 (Using Match on input / event dispatching)
"""

import math
import random
import itertools
from typing import Dict, Tuple, Sequence

import pygame as pg


class Position:
    """Namespace for size and positions"""
    tile_x = 20
    tile_size = tile_x, tile_x


class SpriteGroup:
    """Namespace for sprite groups, with chain iterator keeping the order"""
    ground = pg.sprite.Group()
    entities = pg.sprite.Group()
    light_overlay = pg.sprite.Group()

    @classmethod
    def all_sprites(cls):
        return itertools.chain(cls.ground, cls.entities, cls.light_overlay)


class Player(pg.sprite.Sprite):
    """Player class, which is merely a white rect in this example."""

    def __init__(self):
        super(Player, self).__init__()
        self.image = pg.Surface((50, 50))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()

        SpriteGroup.entities.add(self)

        self.rect.move_ip(225, 225)

    def update(self, *args, **kwargs):
        pass
        # Intentionally disabling mouse following code
        # x, y = pg.mouse.get_pos()
        # c_x, c_y = self.rect.center
        # self.rect.move_ip(x - c_x, y - c_y)


class TileLightOverlay(pg.sprite.Sprite):
    """
    Light overlay tile. Using separate sprites, so we don't have to blit on
    every object above ground that requires lighting.
    """

    # light lowest boundary
    lighting_lo = 255

    # light effect radius
    light_radius = Position.tile_x * 8

    def __init__(self, x, y):
        super(TileLightOverlay, self).__init__()

        self.image = pg.Surface(Position.tile_size)
        self.image.fill((0, 0, 0))

        self.rect = self.image.get_rect()
        self.rect.move_ip(x * Position.tile_x, y * Position.tile_x)

        SpriteGroup.light_overlay.add(self)

    def update(self, *args, **kwargs):
        self.image.set_alpha(self.brightness)

    @property
    def brightness(self):
        """Calculate distance between mouse & apply light falloff accordingly"""
        distance = math.dist(self.rect.center, pg.mouse.get_pos())

        if distance > self.light_radius:
            return self.lighting_lo

        return (distance / self.light_radius) * self.lighting_lo


class TileGround(pg.sprite.Sprite):
    """Ground tile representation. Not much is going on here."""

    def __init__(self, x, y, tile_color: Sequence[int]):
        super(TileGround, self).__init__()

        self.image = pg.Surface(Position.tile_size)
        self.image.fill(tile_color)

        self.rect = self.image.get_rect()
        self.rect.move_ip(x * Position.tile_x, y * Position.tile_x)

        SpriteGroup.ground.add(self)

        # create and keep its pair light overlay tile.
        self.light_tile = TileLightOverlay(x, y)


class World:
    """World storing ground tile data."""
    # tile type storing color etc. for this example only have color.
    tile_type: Dict[int, Tuple[float, float, float]] = {
        0: (56, 135, 93),
        1: (36, 135, 38),
        2: (135, 128, 56)
    }

    def __init__(self):
        # coord system : +x → / +y ↓
        # generating random tile data
        self.tile_data = [
            [random.randint(0, 2) for _ in range(25)]
            for _ in range(25)
        ]
        # generated tiles
        self.tiles = []

    def generate(self):
        """Generate world tiles"""
        for x, row in enumerate(self.tile_data):
            tiles_row = [TileGround(x, y, self.tile_type[col]) for y, col in enumerate(row)]
            self.tiles.append(tiles_row)


def process_input(event: pg.event.Event):
    """Process input, in case you need it"""
    match event.key:
        case pg.K_ESCAPE:
            pg.event.post(pg.event.Event(pg.QUIT))
        case pg.K_UP:
            pass
        # etc..


def display_fps_closure(screen: pg.Surface, clock: pg.time.Clock):
    """FPS display"""
    font_name = pg.font.get_default_font()
    font = pg.font.Font(font_name, 10)
    color = (0, 255, 0)

    def inner():
        text = font.render(f"{int(clock.get_fps())} fps", True, color)
        screen.blit(text, text.get_rect())

    return inner


def mainloop():
    # keeping reference of method/functions to reduce access overhead
    fetch_events = pg.event.get
    display = pg.display

    # local variable setup
    screen = display.set_mode((500, 500))
    player = Player()
    world = World()
    world.generate()

    clock = pg.time.Clock()
    display_fps = display_fps_closure(screen, clock)

    running = True

    # main loop
    while running:
        screen.fill((0, 0, 0))

        # process event
        for event in fetch_events():
            # event dispatch
            match event.type:
                case pg.QUIT:
                    running = False
                case pg.KEYDOWN:
                    process_input(event)

        # draw in ground > entities > light overlay order
        for sprite in SpriteGroup.all_sprites():
            sprite.update()
            screen.blit(sprite.image, sprite.rect)

        # draw fps - not related to question, was lazy to remove & looks fancy
        clock.tick()
        display_fps()

        display.flip()


if __name__ == '__main__':
    pg.init()
    pg.font.init()
    mainloop()
    pg.quit()
