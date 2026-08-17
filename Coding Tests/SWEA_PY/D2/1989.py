for test_no in range(1, int(input()) + 1):
    s = input()
    print(f"#{test_no} {int(s == s[::-1])}")
