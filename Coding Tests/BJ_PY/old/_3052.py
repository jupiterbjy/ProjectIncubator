def func(*args):
    diff = dict()
    for n in args:
        if n < 42:
            diff[n] = n
        else:
            cal = n % 42
            diff[cal] = cal

    print(len(diff))


if __name__ == '__main__':
    inp = [int(input()) for _ in range(10)]
    func(*inp)
