def func(n):
    for i in range(n, 1, -1):
        print(' ' * (n - i) + '*' * (i * 2 - 1))

    for i in range(1, n + 1):
        print(' ' * (n - i) + '*' * (i * 2 - 1))


if __name__ == '__main__':
    func(int(input()))
