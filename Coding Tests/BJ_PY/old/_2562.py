def func(*args):
    # print(n := max(args)) << do this in python 3.8+
    n = max(args)
    print(f'{n}\n{args.index(n) + 1}')


if __name__ == '__main__':
    inp = [int(input()) for _ in range(9)]
    func(*inp)
