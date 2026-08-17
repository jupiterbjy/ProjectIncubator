import sys

i = sys.stdin.readline
p = sys.stdout.write
src = []

for _ in range(int(i())):
    inp = i()

    if 'h_f' in inp:
        src.insert(0, inp.split(' ')[-1])

    elif 'h_b' in inp:
        src.append(inp.split(' ')[-1])

    elif 'p_f' in inp:
        p(src.pop(0) if src else '-1\n')

    elif 'p_b' in inp:
        p(src.pop() if src else '-1\n')

    elif 's' in inp:
        p(str(src.__len__()) + '\n')

    elif 'e' in inp:
        p('0\n' if src else '1\n')

    elif 'f' in inp:
        p(src[0] if src else '-1\n')

    else:
        p(src[-1] if src else '-1\n')

