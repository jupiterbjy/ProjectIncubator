def func(*args):
    for idx, tup in enumerate(args):
        a, b = map(int, tup.split())
        print(f'Case #{idx + 1}: {a + b}')


if __name__ == '__main__':
    inp = []
    for i in range(int(input())):
        inp.append(input())

    func(*inp)
