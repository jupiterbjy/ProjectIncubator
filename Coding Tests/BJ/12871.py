from math import gcd

s1 = input()
s2 = input()
lcm = len(s1) * len(s2) // gcd(len(s1), len(s2))

print(int(s1 * (lcm // len(s1)) == s2 * (lcm // len(s2))))
