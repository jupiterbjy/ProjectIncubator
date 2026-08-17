import sys
input = sys.stdin.readline


def fastOddCheck(n):
    return n & 1


def check_area(area: list) -> int:
    def routine():
        cvt_needed = 0
        for r, row in enumerate(area):
            for idx, x in enumerate(row):
                if indicator[fastOddCheck(idx + 1 + r)] != x:
                    cvt_needed += 1
        return cvt_needed

    indicator = ['W', 'B']
    cvt_case = [routine()]
    indicator.reverse()
    cvt_case.append(routine())
    # inverting to avoid 'if' block, and directly use result of EvenCheck.

    return min(cvt_case)


# Assign to boards.
h, w = map(int, input().split())
board = []
for _ in range(h):
    board.append(input().strip())

max_cut_w = w - 8
max_cut_h = h - 8
results = []

# brutal force with full force TM Nyaruko.
for off_x in range(max_cut_w + 1):
    for off_y in range(max_cut_h + 1):
        cut_area = [row[off_x:off_x + 8] for row in board[off_y:off_y + 8]]
        results.append(check_area(cut_area))

print(min(results))
