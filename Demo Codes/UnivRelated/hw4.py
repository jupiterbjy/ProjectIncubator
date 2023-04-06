"""
2021-03-23
------

# 실행결과 (64bit - double precision)

❯ py hw4.py
0.1 in memory  (BIN): 0011111110111001100110011001100110011001100110011001100110011010
Emach value (BIN/DEC): 0011110010110000000000000000000000000000000000000000000000000000 / 2.22044604925031308085e-16
Minimum num (BIN/DEC): 0000000000000000000000000000000000000000000000000000000000000001 / 4.94065645841246544177e-324

[DEBUG] <determine_epsilon_machine> Loop count: 53
[DEBUG] <determine_min_num> Loop count: 1075
[DEBUG] <float_to_binary> DEC: 0.1 | HEX: 3fb999999999999a | BIN: 0011111110111001100110011001100110011001100110011001100110011010
[DEBUG] <float_to_binary> DEC: 2.220446049250313e-16 | HEX: 3cb0000000000000 | BIN: 0011110010110000000000000000000000000000000000000000000000000000
[DEBUG] <float_to_binary> DEC: 5e-324 | HEX: 0000000000000001 | BIN: 0000000000000000000000000000000000000000000000000000000000000001

"""

import logging
import struct


logger = logging.getLogger("DEBUG")
SHOW_DEBUG_MSG = True


def initialize_logger():
    """
    Initializer setting up logger to distinguish from print lines.
    코드를 테스트하기 위해 만든 일반 출력과 디버깅 출력을 구분하기 위한 로거 설정과정 입니다.
    """

    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] <%(funcName)s> %(msg)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if SHOW_DEBUG_MSG:
        handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)


def float_to_binary(f: float, single_precision=False):
    """
    Convert float to binary format by IEEE754 standard
    부동소숫점을 IEEE754 표준을 따르는 2진 표현으로 나타냅니다.

    :param f: float number.
    :param single_precision: set to false if using 64bit standard.
    :return: binary representation of `f` as conventional str.
    """

    # Create hex representation of given floating number.
    hex_string = struct.pack("!f" if single_precision else "!d", f).hex()

    # Create binary representation of hex, and chop off preceding `0b` which is binary annotation.
    bin_string = bin(int(hex_string, base=16))[2:]

    # Pad zero at head to get consistent length determined by precision parameter.
    bin_string_fitted = bin_string.zfill(32 if single_precision else 64)

    # Debugging messages
    logger.debug(f"DEC: {f} | HEX: {hex_string} | BIN: {bin_string_fitted}")

    return bin_string_fitted


def determine_epsilon_machine():
    """
    Determines emach(epsilon machine).
    덧셈을 톰해 계산기 앱실론(emach)을 계산합니다.

    :return: emach
    """

    placeholder = 1.0
    emach = 1.0
    last_emach = 1.0

    loop_count = 0

    while placeholder != placeholder + emach:
        last_emach = emach
        emach /= 2.0

        loop_count += 1

    logger.debug(f"Loop count: {loop_count}")
    return last_emach


def determine_min_num():
    """
    Determines minimum-representable number in give system.
    계산을 통해 표현 가능한 최소의 숫자를 나타냅니다.

    :return: minimum number representable via IEEE754
    """

    placeholder = 1.0
    last_value = 1.0
    loop_count = 0

    while placeholder != 0.0:
        last_value = placeholder
        placeholder /= 2.0

        loop_count += 1

    logger.debug(f"Loop count: {loop_count}")
    return last_value


def main():
    initialize_logger()

    emach = determine_epsilon_machine()
    min_num = determine_min_num()
    print(f"0.1 in memory  (BIN): {float_to_binary(0.1)}")
    print(f"Emach value (BIN/DEC): {float_to_binary(emach)} / {emach:.20e}")
    print(f"Minimum num (BIN/DEC): {float_to_binary(min_num)} / {min_num:.20e}")


if __name__ == '__main__':
    main()
