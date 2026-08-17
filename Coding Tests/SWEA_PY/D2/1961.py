for test_no in range(1, int(input()) + 1):
    mat = [list(input().split()) for _ in range(int(input()))]
    mat_trans = list(zip(*mat))

    rot_90 = ("".join(reversed(line)) for line in mat_trans)
    rot_180 = ("".join(reversed(line)) for line in reversed(mat))
    rot_270 = ("".join(line) for line in reversed(mat_trans))

    print(f"#{test_no}")
    print(*(" ".join(lines) for lines in zip(rot_90, rot_180, rot_270)), sep="\n")
