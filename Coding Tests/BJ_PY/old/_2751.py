import sys
input = sys.stdin.readline


def Quick(array):

    def Sub_Quick(left, right):

        if left < right:

            pivot_new = Partition(left, right)

            Sub_Quick(left, pivot_new)
            Sub_Quick(pivot_new + 1, right)

    def Partition(left, right):

        mid = (right + left) >> 1

        if array[mid] < array[left]:
            array[mid], array[left] = array[left], array[mid]

        if array[right] < array[left]:
            array[right], array[left] = array[left], array[right]

        pivot = array[mid]

        while True:
            while array[left] < pivot:
                left += 1

            while array[right] > pivot:
                right -= 1

            if left >= right:
                return right

            array[right], array[left] = array[left], array[right]

    Sub_Quick(0, num - 1)
    return array


num = int(input())
src = [int(input()) for _ in range(num)]
for i in Quick(src):
    print(i)
