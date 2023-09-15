# seems like generator is WAY more expensive in pypy
# thanks for this BS-tery Q, what the F.
from math import ceil, sqrt

out = []
for t_no in range(1, int(input()) + 1):
    score = 0
    for _ in range(int(input())):
        x, y = map(int, input().split())
        d = ceil(sqrt(x * x + y * y) / 20)
        if d < 11:
            score += 10 if d == 0 else 11 - d

    out.append(f'#{t_no} {score}')

for s in out:
    print(s)
