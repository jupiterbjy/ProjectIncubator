# I didn't know, but in pypy appending is significantly faster at cost of more memory.
output = []
for _ in range(int(input())):
    output.append(sum(map(int, input().split())) % 24)


print(*(f"#{idx} {val}" for idx, val in enumerate(output, 1)), sep="\n")
