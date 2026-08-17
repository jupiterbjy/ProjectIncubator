import sys
input = sys.stdout.readline

# just some demo for python's stuffs.
# not for efficiency at any aspect.


def counting_sort(arr):
    n = len(arr)
    m = max(arr)

    counts = [0 for _ in range(m+1)]
    results = [0 for _ in range(n)]

    for i in arr:
        counts[i] += 1

    yield counts[:]

    for i in range(m):
        counts[i+1] += counts[i]

    for i in arr:
        results[counts[i] - 1] = i
        counts[i] -= 1

    yield results


def convert_count(arr: list):
    src = arr[:]

    return arr.index(max(arr))


if __name__ == '__main__':
    length = int(input())
    source = [int(input()) for _ in range(length)]

    m = min(source)
    padded_arr = [i - m for i in source]

    gen = counting_sort(padded_arr)
    count, result = gen

    print(f"{round(sum(source)/length)}")
    print(result[length//2] + m)
    print(result[findMax(count)])
    print(result[-1] - result[0])
