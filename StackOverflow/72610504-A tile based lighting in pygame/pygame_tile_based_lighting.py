import math
import random
from typing import Dict, Tuple, Sequence

import pygame
import pygame as pg


pg.init()
pg.font.init()


class Position:
    """Namespace for size and positions"""
    tile_x = 20
    tile_size = tile_x, tile_x


class SpriteGroup:
    """Namespace for sprite groups"""
    ground = pg.sprite.Group()
    light_overlay = pg.sprite.Group()


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
        """Calculate distance between mouse"""
        distance = math.dist(self.rect.center, pg.mouse.get_pos())

        if distance > self.light_radius:
            return self.lighting_lo

        return (distance / self.light_radius) * self.lighting_lo


class TileGround(pg.sprite.Sprite):
    def __init__(self, x, y, tile_color: Sequence[float]):
        super(TileGround, self).__init__()

        self.image = pg.Surface(Position.tile_size)
        self.image.fill(tile_color)

        self.rect = self.image.get_rect()
        self.rect.move_ip(x * Position.tile_x, y * Position.tile_x)

        SpriteGroup.ground.add(self)

        self.light_tile = TileLightOverlay(x, y)


class World:
    # tile type storing color etc. for this example only have color.
    tile_type: Dict[int, Tuple[float, float, float]] = {
        0: (100, 100, 100),
        1: (255, 255, 255),
    }

    def __init__(self):
        # coord system : +x → / +y ↓
        # generating random tile data
        self.tile_data = [
            [random.randint(0, 1) for _ in range(25)]
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
            pg.event.post(pygame.event.Event(pg.QUIT))
        case pg.K_UP:
            pass
        # etc..


def display_fps_closure(screen: pg.Surface):
    font_name = pg.font.get_default_font()
    font = pg.font.Font(font_name, 10)
    color = (0, 255, 0)

    def inner(fps: float):
        text = font.render(f"{int(fps)} fps", True, color)
        screen.blit(text, text.get_rect())

    return inner


def mainloop():
    display = pg.display
    screen = display.set_mode((500, 500))
    screen.fill((0, 0, 0))

    running = True
    events = pg.event.get

    world = World()
    world.generate()

    clock = pg.time.Clock()
    display_fps = display_fps_closure(screen)

    # main loop
    while running:
        # process event
        for event in events():
            match event.type:
                case pg.QUIT:
                    running = False
                case pg.KEYDOWN:
                    process_input(event)

        # draw ground tiles
        for sprite in SpriteGroup.ground:
            screen.blit(sprite.image, sprite.rect)

        # draw light overlay tiles
        for sprite in SpriteGroup.light_overlay:
            sprite.update()
            screen.blit(sprite.image, sprite.rect)

        # draw fps
        clock.tick(240)
        display_fps(clock.get_fps())

        display.flip()

    pg.quit()


if __name__ == '__main__':
    mainloop()
