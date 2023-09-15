output = []
for _ in range(int(input())):
    a, b = map(int, input().split())
    output.append(a * b if a < 10 and b < 10 else -1)

print(*(f"#{idx} {val}" for idx, val in enumerate(output, 1)), sep="\n")
