# WHAT THE -- THIS Q IS??
out = []
for _ in range(int(input())):
    out.append("N" if input().strip() + "a" == input().strip() else "Y")

print(*(f"#{n} {res}" for n, res in enumerate(out, 1)), sep="\n")
