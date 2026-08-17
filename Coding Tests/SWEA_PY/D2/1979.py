for test_no in range(1, int(input()) + 1):
    size, word_len = map(int, input().split())

    grid = ["".join(input().split()) for _ in range(size)]
    grid.extend("".join(col) for col in zip(*grid))

    count = (sum(1 for stub in line.split("0") if len(stub) == word_len) for line in grid)
    print(f"#{test_no} {sum(count)}")
