from math import gcd

for test_no in range(1, int(input()) + 1):
    common, b = map(int, input().split())

    for n in range(common + 1, b + 1):
        common = gcd(common, n)
        if common == 1:
            break

    print(f"#{test_no} {common}")
