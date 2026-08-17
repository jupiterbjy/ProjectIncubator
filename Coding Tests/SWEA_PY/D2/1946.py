for test_no in range(1, int(input()) + 1):
    enc = (input().split() for _ in range(int(input())))
    dec = "".join(char * int(count) for char, count in enc)

    print(f"#{test_no}", *(dec[idx:idx + 10] for idx in range(0, len(dec), 10)), sep="\n")
