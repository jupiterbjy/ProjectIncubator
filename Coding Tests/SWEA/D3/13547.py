for test_no in range(1, int(input()) + 1):
    raw = input()
    wins = raw.count("o")
    loses = len(raw) - wins

    print(f"#{test_no}", "YES" if wins + 15 - len(raw) >= 8 else "NO")
