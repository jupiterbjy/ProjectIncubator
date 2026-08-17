currencies = (50000, 10000, 5000, 1000, 500, 100, 50, 10)

for test_no in range(1, int(input()) + 1):
    print(f"#{test_no}")

    price = int(input())
    counts = []

    for curr in currencies:
        count, price = divmod(price, curr)
        counts.append(count)

    print(*counts)

