from itertools import combinations_with_replacement

lookup = {a * b for a, b in combinations_with_replacement(range(1, 10), 2)}
print(
    *((f"#{n} Yes" if int(input()) in lookup else f"#{n} No") for n in range(1, int(input()) + 1)),
    sep="\n"
)
