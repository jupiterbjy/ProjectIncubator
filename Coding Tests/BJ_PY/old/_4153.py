while True:
    inp = input()
    if '0 0 0' in inp:
        break

    lst = sorted(map(lambda x: int(x)**2, inp.split()))

    if lst[2] - lst[1] - lst[0]:
        print('wrong')
    else:
        print('right')
