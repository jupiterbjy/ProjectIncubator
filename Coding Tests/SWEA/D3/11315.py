def board_iter():
    o_board = [input() for _ in range(int(input()))]
    yield from o_board
    yield from ["".join(line) for line in zip(*o_board)]

    for board in (o_board, o_board[::-1]):
        for col_idx in range(len(board) - 5 + 1):
            yield "".join(board[idx][col_idx + idx] for idx in range(len(board) - col_idx))

        for row_idx in range(1, len(board) - 5 + 1):
            yield "".join(board[row_idx + idx][idx] for idx in range(len(board) - row_idx))


def gen():
    tgt = "ooooo"
    for t_no in range(1, int(input()) + 1):
        for line in board_iter():
            if tgt in line:
                yield f"#{t_no} YES"
                break
        else:
            yield f"#{t_no} NO"


print(*gen(), sep="\n")
