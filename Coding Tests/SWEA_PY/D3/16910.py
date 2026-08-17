from math import sqrt
for test_no in range(1, int(input()) + 1):
    r = int(input())
    r_sq = r ** 2
    print(f"#{test_no} {sum(int(sqrt(r_sq - x ** 2)) for x in range(r)) * 4 + 1}")
