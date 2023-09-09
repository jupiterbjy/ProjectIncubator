n = int(input())

print(1, end="")
for d in range(2, n + 1):
    if n % d == 0:
        print(f" {d}", end="")
