x_ = []
y_ = []
for _ in range(3):
    x, y = map(int, input().split())
    if x in x_:
        x_.remove(x)
    else:
        x_.append(x)
    if y in y_:
        y_.remove(y)
    else:
        y_.append(y)

print(*x_, *y_)
