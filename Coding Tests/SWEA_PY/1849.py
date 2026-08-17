# INCOMPLETE - Getting timeout, logic might be correct...?

class CompareHistory:
    # used to look like disjoint set, not anymore now

    def __init__(self, sample_count):
        sample_count += 1

        # disjoint set arr
        self.root_nodes = list(range(sample_count))

        # child list to accelerate search
        self.children = [[] for _ in range(sample_count)]

        # size diff list comparing to parent node
        self.diff = [0 for _ in range(sample_count)]

    def insert(self, a, b, diff):
        a_root = self.root_nodes[a]
        b_root = self.root_nodes[b]

        # fail fast. If root is same then they already can be calculated.
        if a_root == b_root:
            return

        # make sure smaller sized set merge to larger sized set
        if len(self.children[a_root]) < len(self.children[b_root]):
            a_root, b_root = b_root, a_root
            a, b = b, a
            diff *= -1

        # each element's diff in b_root(rb) need to be recalculated for a_root(ra)
        # b - a = diff, rb - ra = (rb - b) - (ra - b) = (rb - b) - (ra - a - diff)
        # we know (b - rb) and (a - ra) we can calculate diff between root nodes
        root_diff = (self.diff[a] + diff) - self.diff[b]

        # now add offset & update root node for each b_root's children
        self.children[b_root].append(b_root)

        for node in self.children[b_root]:
            self.diff[node] += root_diff
            self.root_nodes[node] = a_root

        # update a_root's child set & clear b_root's child set
        self.children[a_root].extend(self.children[b_root])
        # self.children[b_root].clear()

    def query_diff(self, a, b):

        # check if node has same root
        if self.root_nodes[a] != self.root_nodes[b]:
            return "UNKNOWN"

        # then node is connected. Since node is compressed, search immediate diff
        return self.diff[b] - self.diff[a]


def main():
    for test_n in range(1, int(input()) + 1):
        sample_count, work_count = map(int, input().split(" "))

        history = CompareHistory(sample_count)

        print(f"#{test_n}", end="")

        for _ in range(work_count):

            command, *param = input().split(" ")

            if command == "!":
                history.insert(*map(int, param))
            else:
                print(f" {history.query_diff(*map(int, param))}", end="")

        print()


main()
