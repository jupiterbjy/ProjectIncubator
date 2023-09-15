def gen():
    for t_no in range(1, int(input()) + 1):
        base, lvl, hits = map(int, input().split())
        yield t_no, base * hits + int((hits / 2) * (hits - 1)) * lvl * base // 100


print(*(f"#{n} {res}" for n, res in gen()), sep="\n")
