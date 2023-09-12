def factorization_gen(val):
    for divider in (2, 3, 5, 7, 11):
        count = 0
        while True:
            divided, remain = divmod(val, divider)
            if remain:
                break

            val = divided
            count += 1

        yield count


for test_no in range(1, int(input()) + 1):
    print(f"#{test_no}", *factorization_gen(int(input())))
