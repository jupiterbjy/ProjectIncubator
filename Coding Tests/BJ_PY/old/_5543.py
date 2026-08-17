def func(*args):
    burgs, drinks = args[:3], args[3:5]
    product = [b + d - 50 for b in burgs for d in drinks]
    product.sort(reverse=True)
    print(product[-1])


if __name__ == '__main__':
    inp = [int(input()) for _ in range(5)]
    func(*inp)
