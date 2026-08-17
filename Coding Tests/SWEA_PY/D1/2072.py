def main():
    for line in range(1, int(input()) + 1):
        ns = [n for n in map(int, input().split(" ")) if n & 1]
        print(f"#{line} {sum(ns)}")


main()
