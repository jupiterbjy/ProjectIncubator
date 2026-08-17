for test_no in range(1, int(input()) + 1):
    a, b = map(int, input().split())
    diff = b - a

    if diff == 1 or a > b:
        print(f"#{test_no} -1")
    else:
        print(f"#{test_no} {diff // 2}")
