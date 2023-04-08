"""
Bipartite Graph problem
Refer 11375 for comments
"""

from itertools import chain


def is_edible(eater_idx, victim_idx):
    # compensate case for same ability to compare using idx size
    eater = sharks[eater_idx]
    victim = sharks[victim_idx]

    if eater == victim:
        return eater_idx < victim_idx

    return all(eater[idx] >= victim[idx] for idx in range(3))


def edible_candidates(eater_idx):
    e = sharks[eater_idx]
    # one can't eat itself, shark ain't Erysichthon
    return [
        v_idx for v_idx in range(total)
        if v_idx != eater_idx and is_edible(eater_idx, v_idx)
    ]


def dfs(eater_idx):
    # check if already visited or eater is dead
    if visited[eater_idx]:
        return False

    visited[eater_idx] = True

    for victim_idx in extended_edible[eater_idx]:
        # noinspection PyTypeChecker
        if matched[victim_idx] is None or dfs(matched[victim_idx]):

            matched[victim_idx] = eater_idx
            return True

        # print(matched, eater_idx, victim_idx, count)

    return False


total = int(input())
sharks = [tuple(map(int, input().split())) for _ in range(total)]
edible = [edible_candidates(n) for n in range(total)]

# we want max 2 sharks per one shark, so duplicate eaters
extended_edible = list(chain(*zip(edible, edible)))

matched = [None for _ in range(total)]


count = 0
for shark_idx in range(len(extended_edible)):
    visited = [False for _ in range(len(extended_edible))]

    if dfs(shark_idx):
        count += 1


print(total - count)
