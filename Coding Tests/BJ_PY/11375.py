"""
Bipartite Graph problem
"""


workers, works = map(int, input().split())

# -1 since works index start with 1 & cutting off possible works count
possible_works = [
    list(map(lambda x: int(x) - 1, input().split()))[1:]
    for _ in range(workers)
]
work_assignment = [None for _ in range(works)]


def dfs(worker_idx):
    # if visited pull back
    if workers_visited[worker_idx]:
        return False

    # mark visited
    workers_visited[worker_idx] = True

    # iter over available works
    for work_idx in possible_works[worker_idx]:

        # if target work not matched or matched worker can take other work
        if work_assignment[work_idx] is None or dfs(work_assignment[work_idx]):

            # assign current worker to this work
            work_assignment[work_idx] = worker_idx
            return True

    # otherwise no match
    return False


matches = 0
for worker in range(workers):
    # reset visited record -this record is to prevent possible circular dependency
    # i.e. matching b triggering re-match of a that requires re-match of b (a->b->a...)
    workers_visited = [False for _ in range(workers)]

    # if dfs succeeds then one match was made
    if dfs(worker):
        matches += 1


print(matches)
