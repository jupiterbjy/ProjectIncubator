output = []
for test_no in range(1, int(input()) + 1):
    s_1, e_1, s_2, e_2 = map(int, input().split())
    output.append(max(0, min(e_1, e_2) - max(s_1, s_2)))

print(*(f"#{idx} {val}" for idx, val in enumerate(output, 1)), sep="\n")
