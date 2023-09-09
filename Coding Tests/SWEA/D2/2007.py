# Problem seems to be quite ill-defined... check it out yourself.
for test_no in range(1, int(input()) + 1):
    raw = input()

    for substr_len in range(1, 11):
        if raw[:substr_len] == raw[substr_len: substr_len * 2]:
            print(f"#{test_no} {substr_len}")
            break
