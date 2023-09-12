for test_no in range(1, int(input()) + 1):
    hour_a, min_a, hour_b, min_b = map(int, input().split())
    m = min_a + min_b
    h = hour_a + hour_b

    if m >= 60:
        m -= 60
        h += 1

    if h > 12:
        h -= 12

    print(f"#{test_no} {h} {m}")
