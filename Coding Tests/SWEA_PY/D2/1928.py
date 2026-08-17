mapping = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
mapping = {_ch: _idx for _idx, _ch in enumerate(mapping)}


for test_no in range(1, int(input()) + 1):
    raw = "".join(bin(mapping[val])[2:].zfill(6) for val in input())
    print(f"#{test_no}", "".join(chr(int(raw[idx:idx + 8], base=2)) for idx in range(0, len(raw), 8)))
