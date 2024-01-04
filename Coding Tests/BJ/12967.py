from math import gcd
from itertools import combinations

n, k = map(int, input().split())

arr_gen = (gcd(k, int(ch)) for ch in input().split())

# compress to drop any 1s to reduce combination count
arr = [num for num in arr_gen if num != 1]

# add maximum 2 more 1s at back in case we need those, i.e. k=30 arr=[1 1 30]
arr.extend([1] * min(n - len(arr), 2))

# calc comb
counts = 0
for p, q, r in combinations(arr, 3):
    if gcd(p * q * r, k) == k:
        counts += 1

print(counts)
