def func(x, y):
    x, y = int(x), int(y)
    if x > 0:
        print(1 if y > 0 else 4)
    else:
        print(2 if y > 0 else 3)


if __name__ == '__main__':
    func(input(), input())
