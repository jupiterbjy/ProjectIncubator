import sys


def fib(n):
    # fast doubling
    if n == 0:
        return 0, 1

    a, b = fib(n >> 1)  # a, b = f(k), f(k+1)
    c = a * ((b << 1) - a)
    d = a * a + b * b

    if n & 1:
        return d, c + d
    else:
        return c, d


print(fib(int(sys.stdin.readline()))[0])
