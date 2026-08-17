def func(tup):
    a, b = map(int, tup.split())
    print(a + b)


if __name__ == '__main__':
    while True:
        try:
            func(input())

        except Exception:
            exit()
