for test_no in range(1, int(input()) + 1):
    a, b = map(int, input().split())
    if a > b:
        print(f"#{test_no} >")
    elif a < b:
        print(f"#{test_no} <")
    else:
        print(f"#{test_no} =")
