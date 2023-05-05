"""
https://stackoverflow.com/q/76180068/10909029
https://stackoverflow.com/a/76180482/10909029
"""

# some arbitrary matrix size
mat_x, mat_y = (9, 7)
mat = [list(range(start * mat_x, (start + 1) * mat_x)) for start in range(mat_y)]


def part_mat(matrix, row, col):
    """Partition matrix into 4 chunks from (row, col) position.

    Args:
        matrix: Matrix to cut
        row: row cut index
        col: column cut index

    Returns:
        4 Partitioned matrices, ordered from top left & right, bottom left & right
    """

    # split column into top & bottom section & transpose
    upper, lower = list(zip(*matrix[:col])), list(zip(*matrix[col:]))

    # cut row and transpose again
    return [list(zip(*rows)) for rows in (upper[:row], upper[row:], lower[:row], lower[row:])]

# ---

import numpy as np
# pprint.pprint ain't doing its job fine, using numpy for prett printing

print(f"Original Matrix:\n{np.array(mat)}\n")

for sub_mat in part_mat(mat, 3, 4):
    print(np.array(sub_mat))
