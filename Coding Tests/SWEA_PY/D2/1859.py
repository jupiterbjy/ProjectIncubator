def main():
    for test_no in range(1, int(input()) + 1):
        input()

        # reverse to iterate future -> present order
        buy_prices = reversed(list(map(int, input().split())))
        sell_price = next(buy_prices)
        gain = 0

        for buy_price in buy_prices:
            # if buying > sell then we found new highest point to sell
            if sell_price < buy_price:
                sell_price = buy_price
            else:
                # else we're gaining profit if we buy this
                gain += sell_price - buy_price

        print(f"#{test_no} {gain}")


main()
