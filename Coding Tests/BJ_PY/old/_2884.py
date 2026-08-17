def func(t):
    h, m = map(int, t.split())
    if m < 45:
        h = 23 if h < 1 else h - 1
        m += 15
    else:
        m -= 45

    print(h, m)


if __name__ == '__main__':
    func(input())
