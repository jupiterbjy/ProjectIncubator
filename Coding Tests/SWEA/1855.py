from collections import deque


def closure(parents, depths):
    """travel dist calculation closure"""

    def _match_depth(node_idx, target_depth):
        travel = 0

        while depths[node_idx] != target_depth:
            node_idx = parents[node_idx]
            travel += 1

        return node_idx, travel

    known_dist = {}

    def travel_distance(start, dest):
        """Calculate travel distance between a to b"""

        # setup sorted temps for cache key since frozenset is expensive
        tgt_a, tgt_b = (start, dest) if start < dest else (dest, start)

        # check if path to parent is cached - if so, reuse it & update cache
        key = (start, parents[dest]) if start < parents[dest] else (parents[dest], start)
        if key in known_dist:
            dist = known_dist[key] + 1
            known_dist[(tgt_a, tgt_b)] = dist
            return dist

        dist = 0

        # match depth
        if depths[start] < depths[dest]:
            dest, dist = _match_depth(dest, depths[start])
        elif depths[start] > depths[dest]:
            start, dist = _match_depth(start, depths[dest])

        # move both node up until both are same
        while start != dest:
            start = parents[start]
            dest = parents[dest]
            dist += 2

        # cache result
        known_dist[(tgt_a, tgt_b)] = dist
        return dist

    return travel_distance


def build_children_list(parents):
    children = [[] for _ in range(len(parents))]

    for idx in range(1, len(parents)):
        if parents[idx] != idx:
            children[parents[idx]].append(idx)

    return children


def main():
    for test_n in range(1, int(input()) + 1):
        n = int(input())
        n += 1

        # build parent / children / depths arr - using class is too slow in 3.7
        parents = [0, 1]
        try:
            parents.extend(map(int, input().split(" ")))
        except ValueError:
            # input was blank
            print(f"#{test_n} 0")
            continue

        children = build_children_list(parents)
        depths = [0 for _ in range(len(parents))]

        current = 1
        search_queue = deque(children[1])
        total_dist = 0

        calc_distance = closure(parents, depths)

        # bfs - depth is also initialized here for optimization's sake
        while search_queue:
            tgt = search_queue.popleft()
            search_queue.extend(children[tgt])

            depths[tgt] = depths[parents[tgt]] + 1

            total_dist += calc_distance(current, tgt)
            current = tgt

        print(f"#{test_n} {total_dist}")


main()
