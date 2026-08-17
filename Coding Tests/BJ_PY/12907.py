def possibility(seq) -> int:
    counts = [0] * (max(seq) + 1)

    for val in seq:
        counts[val] += 1

    # check if num of tallest are 0 or more than 2 or if it's not in descending order
    if not (0 < counts[0] < 3) or sorted(counts, reverse=True) != counts:
        return 0

    possibilities = 1

    for val in counts:
        if val == 2:
            possibilities *= 2
            continue

        # only single sequence left, multiply and quit
        possibilities *= 2
        break

    return possibilities


input()
print(possibility(list(map(int, input().split()))))
