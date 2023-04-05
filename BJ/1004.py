from sys import stdin, stdout
from math import dist


def f():
    i = stdin.readline
    p = stdout.write

    for _ in range(int(i())):
        s_x, s_y, e_x, e_y = map(int, i().split(" "))
        start = (s_x, s_y)
        end = (e_x, e_y)

        circles = [tuple(map(int, i().split())) for _ in range(int(i()))]

        count = 0

        for *coord, r in circles:
            start_in = dist(coord, start) < r
            end_in = dist(coord, end) < r

            if start_in & end_in:
                continue

            if start_in | end_in:
                count += 1

        p(f"{count}\n")


f()
