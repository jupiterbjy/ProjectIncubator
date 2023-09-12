for test_no in range(1, int(input()) + 1):
    n = int(input())
    total = n
    digits = set(str(n))

    while len(digits) != 10:
        total += n
        digits.update(str(total))

    print(f"#{test_no} {total}")
