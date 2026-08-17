import sys
import collections

i = sys.stdin.readline
p = sys.stdout.write
src = collections.deque()

for _ in range(int(i())):
    inp = i().split(' ')

    if 'pu' in inp[0]:
        src.append(inp[-1])

    elif 'po' in inp[0]:
        p(src.popleft() if src else '-1\n')

    elif 'si' in inp[0]:
        p(str(src.__len__()) + '\n')

    elif 'em' in inp[0]:
        p('0\n' if src else '1\n')

    elif 'fr' in inp[0]:
        p(src[0] if src else '-1\n')

    else:
        p(src[-1] if src else '-1\n')

