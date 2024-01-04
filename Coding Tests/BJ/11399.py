input()
arr = sorted(map(int, input().split()))
total = 0
cumulative = 0
for n in arr:
    total += n
    cumulative += total

print(cumulative)
