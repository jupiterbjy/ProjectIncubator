tgt = "abcdefghijklmnopqrstuvwxyz"
for test_no in range(1, int(input()) + 1):
    combo = 0
    for a, b in zip(tgt, input()):
        if a != b:
            break
        combo += 1

    print(f"#{test_no} {combo}")
