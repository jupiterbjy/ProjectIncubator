from sys import stdin
from operator import itemgetter
input = stdin.readline

n = int(input())
lists = [tuple(map(int, input().split())) for i in range(n)]
for i in sorted(lists, key=itemgetter(0, 1)):
    print("%d %d" % i)
