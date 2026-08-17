from itertools import count


def create_shell(mat, start_r, start_c, shell_size, counter_instance):
    # if shell_size == 0 then 1x1 still remains, otherwise all filled.
    if shell_size == 0:
        mat[start_r][start_c] = next(counter_instance)
        return
    elif shell_size < 0:
        return

    # draw each shells' side
    for idx in range(shell_size):
        mat[start_r][start_c + idx] = next(counter_instance)

    for idx in range(shell_size):
        mat[start_r + idx][start_c + shell_size] = next(counter_instance)

    for idx in range(shell_size):
        mat[start_r + shell_size][start_c + shell_size - idx] = next(counter_instance)

    for idx in range(shell_size):
        mat[start_r + shell_size - idx][start_c] = next(counter_instance)

    create_shell(mat, start_r + 1, start_c + 1, shell_size - 2, counter_instance)


def main():
    for test_no in range(1, int(input()) + 1):
        size = int(input())

        mat = [[0] * size for _ in range(size)]
        create_shell(mat, 0, 0, size - 1, count(1))

        print(f"#{test_no}", *(" ".join(map(str, line)) for line in mat), sep="\n")


main()
