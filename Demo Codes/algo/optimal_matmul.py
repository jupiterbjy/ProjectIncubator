"""
Optimal matrix multiplication algorithm

Based on lecture https://youtu.be/5MXOUix_Ud4
"""

import math
import array
from copy import deepcopy
from typing import Sequence, Tuple

# just for better printing, pprint won't align numbers with fixed width
import numpy as np


def calculate_optimal(dims: Sequence[int]) -> Tuple[Sequence, Sequence]:
    length = len(dims)

    # 0 col 0 row will not be used - originally used array.array but output wasn't pretty
    m = np.array([[-1 for _ in range(length)] for _ in range(length)])
    p = deepcopy(m)

    # set diagonal to 0, as there's no calculation like self matmul
    for n in range(1, length):
        m[n][n] = 0

    for diagonal in range(1, length - 1):
        for row in range(1, length - diagonal):
            col = row + diagonal
            m[row][col], p[row][col] = minimum(m, dims, col, row)

    return m, p


def minimum(m: Sequence[Sequence[int]], dims: Sequence[int], col, row):
    best = math.inf
    best_k = None

    for k in range(row, col):
        # corresponds to m[i][k] + m[k+1][j] + (d_i-1 * d_k * d_j)
        mul_count = m[row][k] + m[k + 1][col] + dims[row - 1] * dims[k] * dims[col]

        if mul_count < best:
            best = mul_count
            best_k = k

    return best, best_k


def order(p: Sequence[Sequence[int]], i, j):
    if i == j:
        return f"A{i}"

    k = p[i][j]
    return f"({order(p, i, k)}{order(p, k + 1, j)})"


if __name__ == '__main__':
    # (5 x 2) (2 x 3) (3 x 4) (4 x 6) (6 x 7) (7 x 8)
    sample_ = array.array("i", (5, 2, 3, 4, 6, 7, 8))
    m_, p_ = calculate_optimal(sample_)
    print(np.array(m_))
    print(np.array(p_))
    print(order(p_, 1, len(p_) - 1))
