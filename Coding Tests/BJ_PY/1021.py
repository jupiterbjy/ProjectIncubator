from collections import deque

n, _ = map(int, input().split())
q = deque(range(1, n + 1), maxlen=n)

actions = 0

for val in map(int, input().split()):
    idx = q.index(val)
    rev_idx = n - idx

    if idx < rev_idx:
        actions += idx
        q.rotate(-idx)
    else:
        actions += rev_idx
        q.rotate(rev_idx)

    n -= 1
    q.popleft()

print(actions)
