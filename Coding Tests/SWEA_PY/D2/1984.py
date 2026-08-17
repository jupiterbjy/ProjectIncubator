for test_no in range(1, int(input()) + 1):
    _, *val, _ = sorted(map(int, input().split()))
    print(f"#{test_no} {round(sum(val) / len(val))}")
