def possibility_gen(src: list):  # Generator ftw
    for f in src:
        pool_1 = src[:]
        pool_1.remove(f)
        for s in pool_1[:]:
            pool_2 = pool_1[:]
            pool_2.remove(s)
            for t in pool_2:
                yield f + s + t


n, m = map(int, input().split())
inp = list(map(int, input().split()))
results = [i for i in possibility_gen(inp) if i <= m]
print(max(results))
