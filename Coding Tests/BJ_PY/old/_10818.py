def func(*args):
    print(min(args), max(args))


if __name__ == '__main__':
    _ = input()  # take that!
    func(*map(int, input().split()))
