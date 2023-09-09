def draw():
    print(1)
    last_line = [1]

    for n in range(2, int(input()) + 1):
        # zip prev & next vals
        iter_1 = iter(last_line)
        iter_2 = iter(last_line)
        next(iter_2)

        cur_line = [1, *(a + b for a, b in zip(iter_1, iter_2)), 1]

        print(*cur_line)
        last_line = cur_line


for test_no in range(1, int(input()) + 1):
    print(f"#{test_no}")
    draw()
