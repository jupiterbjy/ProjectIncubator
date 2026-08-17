from functools import lru_cache


@lru_cache(maxsize=128)
def func(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1

    return func(n - 2) + func(n - 1)


if __name__ == '__main__':
    result = func(int(input()))
    print(result)   # Sparse is better than dense.

