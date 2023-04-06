"""
python 3.8+

파이썬에서의 float 는 기본적으로 IEEE754 배정밀도를 따르기 때문에 64bit 입니다.

문제에서 주는 수식 (x-2sinx)^2 은 bisection method로 근을 구할수 없어 (x-2sinx)로 바꿨습니다.

------

# 실행결과 (64bit - double precision, Ubuntu 20.04 WSL2)

❯ python3.9 hw5-10.py
[Iteration   1] Range: [1.57, 5.785]                     intermediate: 5.785
[Iteration   2] Range: [1.57, 3.6775]                    intermediate: 3.6775
[Iteration   3] Range: [1.57, 2.6237500000000002]        intermediate: 2.6237500000000002
[Iteration   4] Range: [1.57, 2.0968750000000003]        intermediate: 2.0968750000000003
[Iteration   5] Range: [1.8334375, 2.0968750000000003]   intermediate: 1.8334375
[Iteration   6] Range: [1.8334375, 1.9651562500000002]   intermediate: 1.9651562500000002
[Iteration   7] Range: [1.8334375, 1.899296875]          intermediate: 1.899296875
[Iteration   8] Range: [1.8663671875, 1.899296875]       intermediate: 1.8663671875
[Iteration   9] Range: [1.88283203125, 1.899296875]      intermediate: 1.88283203125
[Iteration  10] Range: [1.891064453125, 1.899296875]     intermediate: 1.891064453125
[Iteration  11] Range: [1.8951806640625, 1.899296875]    intermediate: 1.8951806640625
[Iteration  11] Met threshold: got 0.004116210937500142, threshold 0.005
Answer: 1.89723876953125

"""

import math
import itertools


def bisection_method(function_, initial_range, x_threshold, y_threshold):
    """
    With given initial range, continue iteration until value is under given threshold.
    초기 범위를 받아 범위 크기가 허용 오차 값보다 작아질 때까지 연산을 계속합니다.

    As raising exception for undesired outcome is best practice in python,
    will use intentional raise where return; is used in other languages.
    파이썬에서 맘에 안드는 상황은 명시적 if문 체크보다는 명시적 오류 발생 후 오류를
    잡는것이 기본이므로, 타 언어에서 return;이 들어갈 자리에 명시적으로 오류를 발생시켰습니다.

    :param function_: mathematics function for calculation / 계산할 수식
    :param initial_range: initial range of guaranteed root / 근이 보장된 최초 범위
    :param x_threshold: x's maximum error / x값 허용 오차 크기(+/- 더한 값)
    :param y_threshold: f(x)'s maximum error / 함수값 허용 오차
    :return: computed approximated val / 근삿값
    """

    func = function_
    left, right = initial_range

    assert func(left) * func(right) <= 0.0, f"Range [{left}, {right}] " \
                                            f"is not suitable for bisection method."

    for iteration_ in itertools.count(1):
        left_y, right_y = func(left), func(right)
        mid_val = (left + right) / 2.0
        mid_y = func(mid_val)

        if left_y * mid_y > 0:
            left = mid_val
        else:
            right = mid_val

        print(f"[Iteration {iteration_:3}] " + f"Range: [{left}, {right}]".ljust(40)
              + f" intermediate: {mid_val}")

        if (diff := abs(left - right)) < x_threshold and mid_y < y_threshold:
            print(f"[Iteration {iteration_:3}] Met threshold: got {diff},"
                  f"x threshold {x_threshold}")
            return (left + right) / 2


def main():
    def func(x):
        return x - 2 * math.sin(x)

    try:
        print(f"Answer: {bisection_method(func, (1.57, 10.0), 0.005, 0.001)}")
    except AssertionError as err:
        print(f"Encountered error: {err}")


if __name__ == '__main__':
    main()
