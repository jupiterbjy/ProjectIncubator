def test():
    grid = [input() for _ in range(int(input()))]

    # check if ALL # is connected by checking starting idx, length, count.
    check = [
        (line.index("#"), len(line.strip(".")), line.count("#"))
        for line in grid if "#" in line
    ]

    try:
        ref = check[0]
    except IndexError:
        return False

    # check if length == count == height, and if all lines are same
    return (ref[1] == ref[2] == len(check)) and len(set(check)) == 1


for test_no in range(1, int(input()) + 1):
    print(f"#{test_no} yes" if test() else f"#{test_no} no")
