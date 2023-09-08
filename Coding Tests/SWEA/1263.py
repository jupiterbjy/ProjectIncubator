from collections import deque
from typing import List, Tuple


def calculate_dist_gen(nodes: List[List[int]], start) -> Tuple[int, int]:
    """yield distance to each node in bfs order"""

    # cache visited nodes for fast check, with distance
    visited = {start: 0}
    queue = deque()
    queue.append((start, nodes[start]))

    while queue:
        prev_node, next_nodes = queue.popleft()
        dist = visited[prev_node] + 1

        # for each connected nodes, if not visited, add to visited entry & yield distance
        for node in next_nodes:
            if node in visited:
                continue

            visited[node] = dist
            queue.append((node, nodes[node]))

            yield dist


def main():
    for test_n in range(1, int(input()) + 1):
        input_iter = map(int, input().split())

        counts = next(input_iter)
        zipped = zip(*(input_iter for _ in range(counts)))

        # build adjacent node list
        nodes = [[]]
        nodes.extend(
            [n for n, connected in enumerate(conns, start=1) if connected]
            for idx, conns in enumerate(zipped, start=1)
        )

        shortest_total = float("inf")

        # for each start point, calculate total
        for start_node in range(1, counts + 1):
            total = 0

            for distance in calculate_dist_gen(nodes, start_node):
                total += distance

                # if total value already is not looking good, break out
                if total >= shortest_total:
                    break
            else:
                # no break was called, this gotta be current best.
                shortest_total = total

        print(f"#{test_n} {shortest_total}")


# file = open("input.txt")
# input = file.readline
main()
