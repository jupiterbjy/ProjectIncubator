for test_no in range(1, int(input()) + 1):
    div = int(input()) // 2
    s = input()
    print(f"#{test_no}", "Yes" if s[:div] == s[div:] else "No")
