def func(inp):
    inp = int(inp)
    for i in range(1, 10):
        print(f'{inp} * {i} = {inp * i}')


if __name__ == '__main__':
    func(input())
