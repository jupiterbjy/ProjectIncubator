offset = [(idx // 3, idx % 3) for idx in range(9)]


def group_gen(board):
    yield from (set(line) for line in board)
    yield from (set(line) for line in zip(*board))

    for grid_r in range(0, 9, 3):
        for grid_c in range(0, 9, 3):
            yield {board[grid_r + r][grid_c + c] for r, c in offset}


def main():
    digits = set("123456789")

    for test_no in range(1, int(input()) + 1):
        board = [list(input().split()) for _ in range(9)]

        for group in group_gen(board):
            if digits - group:
                print(f"#{test_no} 0")
                break
        else:
            print(f"#{test_no} 1")


main()