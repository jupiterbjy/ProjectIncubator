for test_no in range(1, int(input()) + 1):
    val = int(input())
    print(f"#{test_no} {-(val // 2) + val * (val & 1)}")
