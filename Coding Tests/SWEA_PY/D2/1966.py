for test_no in range(1, int(input()) + 1):
    input()
    print(f"#{test_no}", *sorted(map(int, input().split())))
