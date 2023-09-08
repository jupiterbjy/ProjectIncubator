def main():
    max_date = [None, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    for test_no in range(1, int(input()) + 1):
        raw = input()

        m = int(raw[4:6])
        if not (1 <= m <= 12):
            print(f"#{test_no} -1")
            continue

        d = int(raw[6:])
        if not (1 <= d <= max_date[m]):
            print(f"#{test_no} -1")
            continue

        print(f"#{test_no} {raw[:4]}/{m:02}/{d:02}")


main()
