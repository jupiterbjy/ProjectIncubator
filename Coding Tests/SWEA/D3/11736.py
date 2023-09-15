out = []
for _ in range(int(input())):
    input()
    arr = list(map(int, input().split()))
    out.append(
        sum(
            1 for n in range(1, len(arr) - 1) if arr[n] == sorted(arr[n - 1:n + 2])[1]
        )
    )

print(*(f"#{n} {val}" for n, val in enumerate(out, 1)), sep="\n")
