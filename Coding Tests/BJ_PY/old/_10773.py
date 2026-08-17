import sys

lst = []
for _ in range(int(sys.stdin.readline())):
    inp = sys.stdin.readline()
    if inp == '0':
        lst.pop()
    else:
        lst.append(int(inp))

print(sum(lst))
