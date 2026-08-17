from sys import stdin
input = stdin.readline


counts = [0] * 10001
for n in range(int(input())):
    counts[int(input())] += 1

for i in range(1, 10001):
    print('%d\n' % i * counts[i], end='')
