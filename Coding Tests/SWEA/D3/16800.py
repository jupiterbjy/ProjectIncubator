for test_no in range(1, int(input()) + 1):
    val = int(input())
    for divider in range(int(val ** 0.5), 0, -1):
        if val % divider == 0:
            print(f"#{test_no} {divider + val // divider - 2}")
            break
