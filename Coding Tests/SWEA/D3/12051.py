out = []
for _ in range(int(input())):
    max_d, perc_d, perc_g = map(int, input().split())

    if perc_g == 100:
        out.append("Possible" if perc_d == 100 else "Broken")
        continue

    if perc_g == 0 and perc_d != 0:
        out.append("Broken")
        continue

    for d in range(max_d, 0, -1):
        if d * perc_d % 100 == 0:
            out.append("Possible")
            break
    else:
        out.append("Broken")

print(*(f"#{idx} {res}" for idx, res in enumerate(out, 1)), sep="\n")


"""
7
100 1 50
1000 81 83
10 10 100
1 1 1
1 0 100
1 100 0
2 50 1

#1 Possible
#2 Possible
#3 Broken
#4 Broken
#5 Broken
#6 Broken
#7 Possible
"""