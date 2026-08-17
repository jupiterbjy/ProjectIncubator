def slide_gen():
    arr_a = [*map(int, input().split())]
    arr_b = [*map(int, input().split())]

    if len(arr_a) > len(arr_b):
        arr_a, arr_b = arr_b, arr_a

    for offset in range(len(arr_b) - len(arr_a) + 1):
        yield sum(arr_a[idx] * arr_b[offset + idx] for idx in range(len(arr_a)))


for test_no in range(1, int(input()) + 1):
    input()
    print(f"#{test_no}", max(slide_gen()))
