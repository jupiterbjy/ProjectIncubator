"""
from collections import Counter
for _ in range(int(input())):
    print(f"#{input()}", Counter(map(int, input().split())).most_common(1)[0][0])
"""

for t_no in range(1, int(input()) + 1):
    input()
    arr = [0] * 101
    for val in map(int, input().split()):
        arr[100 - val] += 1

    print(f"#{t_no} {100 - arr.index(max(arr))}")
