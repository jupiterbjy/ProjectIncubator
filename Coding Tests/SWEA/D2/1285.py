for test_no in range(1, int(input()) + 1):
    count = 0
    best = 100001

    input()
    for x in map(int, input().split()):
        x = abs(x)
        if x < best:
            count = 0
            best = x
        elif x == best:
            count += 1

    print(f"#{test_no} {best} {count}")
