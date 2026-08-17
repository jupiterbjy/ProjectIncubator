import sys


def fib(n):
    # fast doubling
    # reference: www.nayuki.io/page/fast-fibonacci-algorithms
    if n == 0:
        return 0, 1

    a, b = fib(n >> 1)  # a, b = f(k), f(k+1)
    c = a * ((b << 1) - a)
    d = a * a + b * b

    if n & 1:
        return d, c + d
    else:
        return c, d


for i in range(int(sys.stdin.readline())):
    got = int(sys.stdin.readline())
    if got == 0:
        sys.stdout.write('1 0\n')
    else:
        print(*fib(got - 1))
