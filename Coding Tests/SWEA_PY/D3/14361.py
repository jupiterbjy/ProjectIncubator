from itertools import permutations


for test_no in range(1, int(input()) + 1):
    raw = input()
    if int(raw[0]) >= 5:
        print(f"#{test_no} impossible")
        continue

    val = int(raw)
    for comb in permutations(raw, len(raw)):
        quo, rem = divmod(int("".join(comb)), val)

        if not rem and quo != 1:
            print(f"#{test_no} possible")
            break
    else:
        print(f"#{test_no} impossible")
