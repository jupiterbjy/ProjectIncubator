out = []
for _ in range(int(input())):
    raw = input()
    out.append("Yes" if len(set(raw)) == raw.count(raw[0]) == 2 else "No")

print(*(f"#{n} {res}" for n, res in enumerate(out, 1)), sep="\n")
