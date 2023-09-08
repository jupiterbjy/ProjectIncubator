def calc_pull_forces(xs, masses):

    for left_start_idx in range(len(masses) - 1):

        # invert sign to transposition left side force
        masses[left_start_idx] *= -1

        left = xs[left_start_idx]
        right = xs[left_start_idx + 1]

        while True:
            x_candid = (left + right) / 2

            # if possible error is within +- 1e-12 break
            if right - left < 2e-12:
                break

            # if force was positive, need to go closer to left side
            if 0 < sum(mass / (x - x_candid) ** 2 for mass, x in zip(masses, xs)):
                right = x_candid
            else:
                left = x_candid

        print(f" {x_candid:.10f}", end="")


def main():
    for test_no in range(1, int(input()) + 1):
        print(f"#{test_no}", end="")

        total = int(input())
        raw_ints = list(map(int, input().split()))

        # skip slicing on first param, zip will end on shortest.
        calc_pull_forces(raw_ints, raw_ints[total:])
        print()


# file = open("input.txt")
# input = file.readline
main()
