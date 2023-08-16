from functools import lru_cache


@lru_cache()
def man_dist(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def main():
    for n in range(1, int(input()) + 1):
        _ = input()

        entries = iter(map(int, input().split(" ")))

        company, home, *customers = zip(entries, entries)
        shortest = 1e10

        def visit(p1, remaining: set, travel):
            nonlocal shortest

            if travel >= shortest:
                return

            if not remaining:
                dist = travel + man_dist(p1, home)
                if dist < shortest:
                    shortest = dist

            for p2 in remaining:
                visit(p2, remaining - {p2}, travel + man_dist(p1, p2))

        visit(company, set(customers), 0)
        print(f"#{n} {shortest}")


main()
