"""
Demonstration of color overlapping
"""

import pygame as pg


class Player(pg.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.image = pg.Surface((50, 50))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()

        # setting alpha on player
        self.image.set_alpha(125)

    def update(self, *args, **kwargs):
        x, y = pg.mouse.get_pos()
        c_x, c_y = self.rect.center
        self.rect.move_ip(x - c_x, y - c_y)


def mainloop():
    player = Player()
    screen = pg.display.set_mode((500, 500))

    circle_colors = (255, 0, 0), (0, 255, 0), (0, 0, 255)
    circle_coords = (150, 250), (250, 250), (350, 250)

    # make surface, set alpha then draw circle
    bg_surfaces = []
    for (color, center) in zip(circle_colors, circle_coords):
        surface = pg.Surface((500, 500), pg.SRCALPHA, 32)
        surface.convert_alpha()
        surface.set_alpha(125)
        pg.draw.circle(surface, color, center, 75)
        bg_surfaces.append(surface)

    running = True

    while running:
        screen.fill((0, 0, 0))

        # draw background
        for surface in bg_surfaces:
            screen.blit(surface, surface.get_rect())

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        player.update()
        screen.blit(player.image, player.rect)
        pg.display.flip()


if __name__ == '__main__':
    pg.init()
    mainloop()
    pg.quit()
