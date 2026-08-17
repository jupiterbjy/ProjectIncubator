from itertools import tee


def get_combinations(string):
    results = set(string)

    if len(string) == 1:
        return results

    for letter_count in range(2, len(string) + 1):
        iterators = tee(string, letter_count)

        for idx, iterator in enumerate(iterators):
            for _ in range(idx):
                next(iterator)

        results.update("".join(part) for part in zip(*iterators))

    return results


def main():
    for test_n in range(1, int(input()) + 1):
        idx = int(input()) - 1

        combinations = sorted(get_combinations(input()))

        try:
            print(f"#{test_n} {combinations[idx]}")
        except IndexError:
            print(f"#{test_n} none")


main()
