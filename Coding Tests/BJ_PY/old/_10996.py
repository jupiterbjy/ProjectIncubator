def func(n):
    if n == 1:
        print('*')
    else:
        line, odd_line = '', ''
        for i in range(1, n + 1):
            line += '*' if i & 1 else ' '
            odd_line += ' ' if i & 1 else '*'

        for i in range(1, 2 * n + 1):
            print(line if i & 1 else odd_line)


if __name__ == '__main__':
    func(int(input()))
