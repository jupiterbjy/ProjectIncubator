def main():
    ratios = 0.35, 0.45, 0.2
    ratings = "A+", "A0", "A-", "B+", "B0", "B-", "C+", "C0", "C-", "D0"

    for test_no in range(1, int(input()) + 1):
        total, tgt = map(int, input().split())

        # calc final scores
        scores = [
            sum(int(val) * rate for val, rate in zip(input().split(), ratios))
            for _ in range(total)
        ]

        # div score index by 10
        rating = sorted(scores, reverse=True).index(scores[tgt - 1]) // (total // 10)
        print(f"#{test_no} {ratings[rating]}")


main()
