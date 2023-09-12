patterns = "()", "(|", "|)"
for test_no in range(1, int(input()) + 1):
    raw = input()
    print(f"#{test_no} {sum(raw.count(pattern) for pattern in patterns)}")
