from sys import stdin

lists = set(stdin.readline().rstrip() for i in range(int(input())))
print('\n'.join(sorted(lists, key=lambda item: (len(item), item))))
