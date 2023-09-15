out = []
for test_no in range(1, int(input()) + 1):
    l, r = 1, 1

    for cmd in input():
        if cmd == "L":
            l = l
            r = l + r
        else:
            l = l + r
            r = r

    out.append(f"#{test_no} {l} {r}")

print(*out, sep="\n")
