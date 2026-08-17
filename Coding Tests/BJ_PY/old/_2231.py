import sys


# https://stackoverflow.com/questions/14939953/ ref
def sum_digit(n):
    r = 0
    while n:
        r, n = r + n % 10, n//10
    return r


def main(n):
    for i in range(n):
        if sum_digit(i) + i == n:
            return i
    return 0


print(main(int(sys.stdin.readline())))
