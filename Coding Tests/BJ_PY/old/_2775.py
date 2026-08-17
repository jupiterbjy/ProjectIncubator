from functools import lru_cache


@lru_cache(maxsize=256)
def func(k, n):
    if k:
        s = 0
        for room in range(1, n + 1):
            s += func(k - 1, room)
        return s
    else:
        return n


for _ in range(int(input())):
    print(func(int(input()), int(input())))
