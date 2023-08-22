PARSE_DICT = {
    "0001101": 0,
    "0011001": 1,
    "0010011": 2,
    "0111101": 3,
    "0100011": 4,
    "0110001": 5,
    "0101111": 6,
    "0111011": 7,
    "0110111": 8,
    "0001011": 9
}


def find_multiplier(binary_line: str):
    """Samples first 3 digits to determine the multiplier"""

    value_changes = 0
    counts = [0, 0, 0]
    current_letter = "1"

    for letter in reversed(binary_line):
        if letter != current_letter:
            current_letter = "0" if current_letter == "1" else "1"
            value_changes += 1

        if value_changes == 3:
            break

        counts[value_changes] += 1

    # all ratio has 1 between 2nd ~ 4th position, thus checking last 3 digit will do
    # i.e. 3:2:1:1, 1:1:3:2, ... - then smallest count would be '1' component's multiple
    return min(counts)


def zero_pad(line, multiplier):
    """Pads missing leading zeros"""

    return "0" * (56 * multiplier - (len(line) % (56 * multiplier))) + line


def decode(code, mult_factor):
    """decode binary code into digits"""

    if mult_factor != 1:
        # compress if factor is greater than 1
        code = code[::mult_factor]

    return tuple(PARSE_DICT[code[7 * idx:7 * idx + 7]] for idx in range(8))


def validate(code: tuple):
    """Validates decoded result"""

    total = 0
    digit_iter = iter(code)

    for odd, even in zip(digit_iter, digit_iter):
        total += 3 * odd + even

    return total % 10 == 0


def consume_line(line):
    found = []

    while line:
        multiplier = find_multiplier(line)

        # calculate binary starting position
        start_idx = len(line) - (56 * multiplier)

        # if start_idx < 0, leading 0s are lost & end of line - add padding & break
        if start_idx < 0:
            found.append(decode(zero_pad(line, multiplier), multiplier))
            break

        found.append(decode(line[start_idx:], multiplier))
        line = line[:start_idx].rstrip("0")

    return found


def main():
    for test_n in range(1, int(input()) + 1):
        rows, _ = map(int, input().strip().split(" "))

        codes_found = set()

        for _ in range(rows):
            # apparently input has some issues, requires stripping
            line = bin(int(input().strip(), base=16))[2:].rstrip("0")

            # if blank aka zero only line pass
            if not line:
                continue

            for code in consume_line(line):
                codes_found.add(code)

        # calculate total valid codes' sum
        total = 0
        for code in codes_found:
            if validate(code):
                total += sum(code)

        print(f"#{test_n} {total}")


# file = open("sample_input (1).txt")
# def input():
#     return file.readline()
main()
