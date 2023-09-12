for test_no in range(1, int(input()) + 1):
    a_rate, base, limit, b_rate, usage = map(int, input().split())

    a = usage * a_rate
    b = base if usage < limit else base + (usage - limit) * b_rate
    print(f"#{test_no}", a if a < b else b)
