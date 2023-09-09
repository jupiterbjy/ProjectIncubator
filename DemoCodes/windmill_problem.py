"""
Windmill problem visualization & algorithm

Guessed from single image in https://youtu.be/M64HUIJFTZM?t=228
"""
import math
from random import randrange
from functools import cache
from math import sin, cos, asin, pi, sqrt, atan2
from typing import Tuple

import pygame


# GLOBAL CONFIGURATION -------------------
SCREEN_X = 400
SCREEN_Y = 400

ROTATION = pi * 0.1
FPS = 60

DOT_COUNT = 10
DOT_COLOR = (100, 100, 255)

FONT = "arial"
FONT_SIZE = 30
FONT_COLOR = (255, 255, 255)

LINE_COLOR = (255, 0, 0)
BG_COLOR = (0, 0, 0)
# ----------------------------------------

# INIT
pygame.init()
pygame.font.init()


class Vector2d:
    __slots__ = ("x", "y", "p1", "p2")

    def __init__(self, p1: tuple, p2: tuple = None):
        if p2 is None:
            p2 = p1
            p1 = (0, 0)

        self.p1 = p1
        self.p2 = p2
        self.x = p2[0] - p1[0]
        self.y = p2[1] - p1[1]

    def __neg__(self):
        return Vector2d((-self.x, -self.y))

    def __hash__(self):
        return hash((*self.p1, *self.p2))

    def __sub__(self, other: "Vector2d"):
        return Vector2d(self.x - other.x, self.y - other.y)

    def __abs__(self):
        return sqrt(self.x ** 2 + self.y ** 2)

    def __mul__(self, other: "Vector2d"):
        """perp dot product"""
        return self.x * other.y - self.y * other.x


# cached next dot & angle generator for faster execution time
def find_next_closest_gen(initial_pivot, initial_last_pivot, dots: set):
    # @cache
    def cal_angle(vector_1: Vector2d, vector_2: Vector2d):
        """Calculate perp-dot product aka 2D pseudo cross product"""
        # http://www.sunshine2k.de/articles/Notes_PerpDotProduct_R2.pdf

        # seems like there's 2 methods so far
        # return atan2(vector_1 * vector_2, vector_1.x * vector_2.x + vector_1.y * vector_1.y)
        # -: clockwise, +: counter clockwise
        return asin(vector_1 * vector_2 / (abs(vector_1) * abs(vector_2)))

    # @cache
    def find_closest_dot(pivot_, last_pivot_) -> Tuple[Tuple[int, int], float]:
        """Finds next dot with the closest positive angle relative to current."""

        vector_1 = Vector2d(pivot_, last_pivot_)

        fixed_dots = list(dots)
        angles = [cal_angle(vector_1, Vector2d(pivot_, dot)) for dot in fixed_dots]
        neg_pairs = [((dot, angle - pi) if angle > 0 else (dot, angle)) for dot, angle in zip(fixed_dots, angles)]

        closest_pair = max(neg_pairs, key=lambda x: x[1])
        return closest_pair

    # set init pivot & last pivot
    pivot = initial_pivot
    last_pivot = initial_last_pivot

    try:
        while True:
            next_dot, next_angle = find_closest_dot(pivot, last_pivot)
            yield next_dot, -next_angle

            dots.remove(next_dot)
            dots.add(last_pivot)

            pivot, last_pivot = next_dot, pivot
    finally:
        # just some debug output on generator exit
        print(f"{cal_angle.__name__} {cal_angle.cache_info()}")
        print(f"{find_closest_dot.__name__} {find_closest_dot.cache_info()}")


def draw_line(pivot, angle, surface: pygame.Surface):
    c_x, c_y = pivot

    d_x = sin(angle) * 1000
    d_y = cos(angle) * 1000

    # pygame.draw.line(surface, LINE_COLOR, (c_x - d_x, c_y - d_y), (c_x + d_x, c_y + d_y))
    pygame.draw.line(surface, (100, 0, 0), (c_x - d_x, c_y - d_y), (c_x, c_y))
    pygame.draw.line(surface, LINE_COLOR, (c_x, c_y), (c_x + d_x, c_y + d_y))


def draw_dots(dots, last_pivot, pivot, target, surface: pygame.Surface):
    for dot in dots:
        pygame.draw.circle(surface, DOT_COLOR, dot, radius=2)

    pygame.draw.circle(surface, (255, 255, 0), target, radius=2)
    pygame.draw.circle(surface, (255, 200, 0), last_pivot, radius=2)
    pygame.draw.circle(surface, (255, 150, 0), pivot, radius=2)


# closure for faster access time
def render():
    screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y))

    font_ = pygame.font.SysFont(FONT, FONT_SIZE)
    clock = pygame.time.Clock()

    # cache name for faster access time
    angle_per_frame = ROTATION / FPS

    dots = [
        (randrange(0, SCREEN_X), randrange(0, SCREEN_Y))
        for _ in range(DOT_COUNT)
    ]
    pivot = dots[0]
    last_pivot = dots[1]
    angle = atan2(pivot[1] - last_pivot[1], pivot[0] - last_pivot[0])

    dots_iterator = find_next_closest_gen(pivot, last_pivot, set(dots[2:]))

    for dot, angle_diff in dots_iterator:
        target_angle = angle + angle_diff

        print(f"p:{pivot}-{last_pivot}, {dot}, {math.degrees(angle_diff)}")

        for _ in range(int(angle_diff / angle_per_frame)):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            angle += angle_per_frame

            screen.fill((0, 0, 0))
            draw_line(pivot, angle, screen)
            draw_dots(dots, last_pivot, pivot, dot, screen)
            pygame.display.update()
            clock.tick(FPS)

        angle = atan2(dot[1] - pivot[1], dot[0] - pivot[0])
        pivot, last_pivot = dot, pivot

        screen.fill((0, 0, 0))
        draw_line(pivot, target_angle, screen)
        draw_dots(dots, last_pivot, pivot, dot, screen)
        pygame.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    render()
