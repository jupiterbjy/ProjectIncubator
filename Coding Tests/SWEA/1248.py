def path_from_root(parent_arr, search_tgt):
    history = [search_tgt]

    while parent_arr[search_tgt] != search_tgt:
        search_tgt = parent_arr[search_tgt]
        history.append(search_tgt)

    return reversed(history)


def find_common_parent(parents_arr, tgt_a, tgt_b):
    path_a = path_from_root(parents_arr, tgt_a)
    path_b = path_from_root(parents_arr, tgt_b)

    return [p_a for p_a, p_b in zip(path_a, path_b) if p_a == p_b][-1]


def fetch_size(child_arr, root):
    root <<= 1
    child_l, child_r = child_arr[root], child_arr[root + 1]

    size = 1

    if child_l is not None:
        size += fetch_size(child_arr, child_l)
    if child_r is not None:
        size += fetch_size(child_arr, child_r)

    return size


def main():
    for test_n in range(1, int(input()) + 1):

        vertex_n, _, tgt_a, tgt_b = map(int, input().split(" "))
        vertex_n += 1

        vertex_input = iter(map(int, input().split(" ")))

        parents = [1 for _ in range(vertex_n)]
        children = [None for _ in range(2 * vertex_n)]

        # build tree
        for parent, child in zip(vertex_input, vertex_input):
            parents[child] = parent
            parent <<= 1

            if children[parent] is None:
                children[parent] = child
            else:
                children[parent + 1] = child

        # find the lowest common parent & it's subtree size
        common_root = find_common_parent(parents, tgt_a, tgt_b)
        size = fetch_size(children, common_root)

        print(f"#{test_n} {common_root} {size}")


main()
