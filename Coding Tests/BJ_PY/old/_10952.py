def func(*args):
    for tup in args:
        a, b = map(int, tup.split())
        print(a + b)


if __name__ == '__main__':
    inp = []
    while True:
        c = input()
        if c != '0 0':
            inp.append(c)
        else:
            break

    func(*inp)
