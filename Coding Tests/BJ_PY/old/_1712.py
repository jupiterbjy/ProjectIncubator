def func(fixed, manufacture, price):
    if manufacture >= price:
        print(-1)
    else:
        print(fixed // (price - manufacture) + 1)


if __name__ == '__main__':
    func(*map(int, input().split()))
