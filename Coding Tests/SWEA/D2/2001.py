def conv_sum_gen(grid, kernel_size):
    size = len(grid) - kernel_size + 1
    for col in range(size):
        for row in range(size):
            yield sum(
                grid[row + r][col + c] for r in range(kernel_size)
                for c in range(kernel_size)
            )


def main():
    for test_no in range(1, int(input()) + 1):
        grid_size, flapper_size = map(int, input().split())
        grid = [
            list(map(int, input().split())) for _ in range(grid_size)
        ]
        print(f"#{test_no} {max(conv_sum_gen(grid, flapper_size))}")


main()
