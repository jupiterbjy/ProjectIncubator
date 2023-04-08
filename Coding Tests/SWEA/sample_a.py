"""

Memo:
- N by N cells
- each cell could be core, cable or nothing
- edges cells are already connected to power
- connect power to core by cable
- cable should not overlap
- cable can only run straight, absolutely no tilting even at terminals

=> Minimum sum of cables lengths when connecting as many core as possible?

Rule:
- Cell state:
    - 0: empty
    - 1: core

Condition:
- cell size N -> 7 <= N <= 12
- Core count C -> 1 <= C <= 12
- there could be core that can't be connected

Plan:
0. row-first. (row, col), ↓ → ordering
1. find already connected edge cores
2. put cable-required cores in queue
3. for each cores in queue find sides that can be connected
4. save terminal coordinates of cables connecting each of connectable sides
5. run brute force and find minimum cables with maximum connections
    5.a. check whether cables are crossing by using saved terminal coordinates?
    5.b. record entire cells cable takes and check if there's intersection?
"""


from typing import List


class Cable:
    def __init__(self, start, end):
        row_min, row_max = sorted((start[0], end[0]))
        col_min, col_max = sorted((start[1], end[1]))

        self.coord = start, end
        self.cells = set()

        for row in range(row_min, row_max + 1):
            for col in range(col_min, col_max + 1):
                self.cells.add((row, col))

    def __len__(self):
        return len(self.cells)

    def __repr__(self):
        return f"Cable{self.coord}"


class InnerCore:
    def __init__(self, row, col, n, all_cores):
        self.pos = row, col

        # check 4 cables in order 'up right down left'
        cables = [
            Cable((row - 1, col), (0, col)),
            Cable((row, col + 1), (row, n)),
            Cable((row + 1, col), (n, col)),
            Cable((row, col - 1), (row, 0)),
        ]

        # filter out overlapping cables
        self.cables = [cable for cable in cables if not cable.cells & all_cores]

    def __repr__(self):
        return f"InnerCore{self.pos}"


def recursive_brute_force(cores_: List[InnerCore], global_occupied: set):
    """Returns successfully connected core count & total cable length"""
    if not cores_:
        return 0, 0

    core = cores_[0]

    # calculate best case without using this core
    best_count, best_length = recursive_brute_force(cores_[1:], global_occupied)

    for cable in core.cables:
        # if overlaps then skip cable
        if cable.cells & global_occupied:
            continue

        # otherwise recursive & update bests if equal or better ones are found
        # then add up current core & cable length
        count, length = recursive_brute_force(cores_[1:], global_occupied | cable.cells)
        count += 1
        length += len(cable)

        # if results are good we have new champions
        if (count > best_count) or (count == best_count and length < best_length):
            best_count = count
            best_length = length

    return best_count, best_length


def main():
    for case in range(1, int(input()) + 1):
        n = int(input()) - 1
        arr = [[*map(int, input().split())] for _ in range(n + 1)]

        # get cores coordinates
        all_cores = set()
        for idx_row, row_ in enumerate(arr):
            for idx_col, item in enumerate(row_):
                if item == 1:
                    all_cores.add((idx_row, idx_col))

        # find edge-touching cores
        edges = (0, n)
        edge_cores = set(core for core in all_cores if core[0] in edges or core[1] in edges)
        inner_cores = [InnerCore(*core, n, all_cores) for core in (all_cores - edge_cores)]

        # for each non-edge cores brute force maximum core count with minimum cables
        _, cable_length = recursive_brute_force(inner_cores, all_cores)

        print(f"#{case} {cable_length}")


main()
