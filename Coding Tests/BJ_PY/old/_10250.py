def func(floors, _, order):
    quotient, remainder = order // floors, order % floors
    if remainder:
        print(str(remainder) + str(quotient + 1).zfill(2))
    else:
        print(str(floors) + str(quotient).zfill(2))


if __name__ == '__main__':
    test = []
    for i in range(int(input())):
        test.append(tuple(map(int, input().split())))

    for t in test:
        func(*t)
