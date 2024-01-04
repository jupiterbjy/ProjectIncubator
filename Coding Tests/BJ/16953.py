a, b = map(int, input().split())
operations = 0

while a < b:
    if b % 10 == 1:
        b //= 10
    elif not b & 1:
        b //= 2
    else:
        break

    operations += 1

print((operations + 1) if a == b else -1)
