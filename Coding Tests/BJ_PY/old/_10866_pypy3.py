import sys
i = sys.stdin.readline
p = sys.stdout.write
d = []

for _ in range(int(i())):
    inp = i()

    if 'push_front' in inp:
        d.insert(0, inp.split(' ')[1])

    elif 'push_back' in inp:
        d.append(inp.split(' ')[1])

    elif inp == 'pop_front\n':
        p(d.pop(0) if d else '-1\n')

    elif inp == 'pop_back\n':
        p(d.pop() if d else '-1\n')

    elif inp == 'size\n':
        p(str(len(d)) + '\n')

    elif inp == 'empty\n':
        p('0\n') if d else p('1\n')

    elif inp == 'front\n':
        p(d[0] if d else '-1\n')

    else:
        p(d[-1] if d else '-1\n')
