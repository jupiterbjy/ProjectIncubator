import sys
r = sys.stdin.readline


def compDistance(x1, y1, d1, x2, y2, d2):
    point_dist_sq = (x1 - x2) ** 2 + (y1 - y2) ** 2
    mx_dist_squared = (d1 + d2) ** 2

    if point_dist_sq > mx_dist_squared:
        return 0

    if point_dist_sq == mx_dist_squared:
        return 1

    if point_dist_sq < mx_dist_squared:
        delta_dist = abs(d1 - d2)

        if not point_dist_sq:  # 0이면 동심원
            if not delta_dist:
                return -1
            return 0

        if point_dist_sq == delta_dist ** 2:
            return 1

        if point_dist_sq < delta_dist ** 2:
            return 0

    return 2


for _ in range(int(r())):
    print(compDistance(*map(int, r().split())))
