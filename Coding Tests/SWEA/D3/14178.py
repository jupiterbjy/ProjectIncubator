output = []
for test_no in range(1, int(input()) + 1):
    len_, range_ = map(int, input().split())
    range_ = range_ * 2 + 1
    output.append(f"#{test_no} {len_ // range_ + (len_ % range_ != 0)}")

# what the heck is wrong with pypy print call latency????
print(*output, sep="\n")
