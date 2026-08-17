import sys

pep = []

for _ in range(int(sys.stdin.readline())):
    pep.append((*map(int, sys.stdin.readline().split()),))

for fatty in pep:
    rank = 1
    for fatter in pep:
        if fatter[0] > fatty[0] and fatter[1] > fatty[1]:
            rank += 1

    sys.stdout.write('%d ' % rank)
