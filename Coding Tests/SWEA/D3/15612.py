def iter_board():
    board = [input() for _ in range(8)]
    yield from board
    yield from ("".join(line) for line in zip(*board))


for t_no in range(1, int(input()) + 1):
    print(f"#{t_no}", "yes" if all(line.count("O") == 1 for line in iter_board()) else "no")
