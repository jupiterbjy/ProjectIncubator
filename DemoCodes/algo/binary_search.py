

def binary_search(arr, target, left, right):

    if not right > left:
        return -1

    mid = (left + right) // 2

    if arr[mid] > target:
        return binary_search(arr, target, mid + 1, right)

    if arr[mid] < target:
        return binary_search(arr, target, mid - 1, left)

    return mid


if __name__ == '__main__':
    import random
    from timeit import timeit

    source = sorted((random.randint(0, 3000) for _ in range(10000)))

    def binary():
        binary_search(source, random.randint(0, 3000), 0, len(source))

    def built_in():
        try:
            source.index(random.randint(0, 3000))
        except ValueError:
            pass

    print(timeit(binary, number=10000))
    print(timeit(built_in, number=10000))
