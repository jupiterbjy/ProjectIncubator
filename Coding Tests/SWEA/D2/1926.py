def main():
    print(1, end="")
    checks = "369"

    for val in range(2, int(input()) + 1):
        s = str(val)
        count = sum(s.count(char) for char in checks)

        print(" " + ("-" * count if count else s), end="")


main()
