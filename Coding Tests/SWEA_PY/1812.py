def cut(src_w, src_h, tgt, remaining: list):
    w_diff = src_w - tgt
    h_diff = src_h - tgt

    # if there's remaining part, append to remaining list.
    if w_diff:
        remaining.append((w_diff, tgt))

    if h_diff:
        remaining.append((tgt, h_diff))

    if w_diff and h_diff:
        remaining.append((w_diff, h_diff))


def main():
    for test_no in range(1, int(input()) + 1):
        _, src_side = map(int, input().split())
        tgt_sides = sorted((2 ** int(val) for val in input().split()), reverse=True)

        remaining_parts = [(src_side, src_side)]
        bought = 1

        for tgt_side in tgt_sides:

            # look for any remaining parts that fits - cut part if fits.
            for idx, part in enumerate(remaining_parts):
                if part[0] >= tgt_side and part[1] >= tgt_side:
                    cut(*remaining_parts.pop(idx), tgt_side, remaining_parts)
                    break
            else:
                # no part fits the tgt tile size, buy new.
                bought += 1
                cut(src_side, src_side, tgt_side, remaining_parts)

        print(f"#{test_no} {bought}")


# file = open("input.txt")
# input = file.readline
#
# file_2 = open("output.txt")
# p = print
# def print(s):
#     expected = file_2.readline().strip()
#     if s != expected:
#         p(s, expected)

main()
