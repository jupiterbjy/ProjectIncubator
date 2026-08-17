def func(*args):
    for tup in args:
        a, b = map(int, tup.split())
        print(a + b)


if __name__ == '__main__':
    inp = []
    for i in range(int(input())):
        inp.append(input())

    func(*inp)
