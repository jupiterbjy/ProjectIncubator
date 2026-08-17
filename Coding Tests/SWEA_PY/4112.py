from itertools import accumulate, count, takewhile


# create indexes for last number in each floor - last num would be 10011
FLOOR_IDENTS = list(takewhile(lambda x: x <= 10011, accumulate(count(1))))


def find_floor_idx(n):
    """Returns floor idx from the highest floor"""
    for idx, floor_identifier in enumerate(FLOOR_IDENTS):
        if n <= floor_identifier:
            break

    # noinspection PyUnboundLocalVariable
    return idx


def find_x_idx(floor_idx, n):
    """Returns left-handed & right-handed coordinate"""
    right_handed_idx = FLOOR_IDENTS[floor_idx] - n

    try:
        upper_floor_ident = FLOOR_IDENTS[floor_idx - 1]
        left_handed_idx = n - (upper_floor_ident + 1)

    except IndexError:
        # probably n == 1
        left_handed_idx = 0

    return left_handed_idx, right_handed_idx


def main():
    for test_n in range(1, int(input()) + 1):

        # make sure 'a' is higher up in triangle
        a, b = sorted(map(int, input().split(" ")))

        a_floor = find_floor_idx(a)
        b_floor = find_floor_idx(b)
        floor_diff = b_floor - a_floor

        a_lx, a_rx = find_x_idx(a_floor, a)
        b_lx, b_rx = find_x_idx(b_floor, b)

        # triangle with 'a' on top has the same & shortest dist
        # if 'b' is outside that triangle, need to travel horizontally too.
        if b_lx < a_lx:
            dist = (a_lx - b_lx) + floor_diff
        elif b_rx < a_rx:
            dist = (a_rx - b_rx) + floor_diff
        else:
            dist = floor_diff

        print(f"#{test_n} {dist}")


main()
