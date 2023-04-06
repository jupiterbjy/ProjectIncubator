from sys import stdin, stdout
from math import sqrt


def f():
    i = stdin.readline
    p = stdout.write

    diag, h_r, w_r = map(int, i().split(" "))
    factor = diag / sqrt(h_r ** 2 + w_r ** 2)

    p(f"{int(h_r * factor)} {int(w_r * factor)}")


f()
