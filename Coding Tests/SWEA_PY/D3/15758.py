from math import gcd


for test_no in range(1, int(input()) + 1):
    a, b = input().split()
    l_a, l_b = len(a), len(b)
    lcm = l_a * l_b // gcd(l_a, l_b)
    print(f"#{test_no}", "yes" if a * (lcm // l_a) == b * (lcm // l_b) else "no")
