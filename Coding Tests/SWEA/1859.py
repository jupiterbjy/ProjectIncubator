def main():
    for case in range(1, int(input()) + 1):
        input()
        vals = reversed(list(map(int, input().split())))
        cur_sell = next(vals)
        gain = 0

        for val in vals:
            if cur_sell < val:
                cur_sell = val
            else:
                gain += cur_sell - val

        print(f"#{case} {gain}")


main()
