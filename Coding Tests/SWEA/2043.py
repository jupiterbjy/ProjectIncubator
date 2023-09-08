pwd, start = map(int, input().split())
print((pwd - start + 1) if pwd >= start else (1000 + pwd - start + 1))
