def validate_grid(known_tiles):
    iterator = iter(known_tiles)
    ref_odd, ref_ch = next(iterator)

    for odd, ch in iterator:
        # if sum(r + c) is odd then color should be opposite
        if (ref_odd == odd and ref_ch != ch) or (ref_odd != odd and ref_ch == ch):
            return False

    return True


for test_no in range(1, int(input()) + 1):
    h, w = map(int, input().split())
    grid = [input() for _ in range(h)]
    known = [((r + c) & 1, grid[r][c]) for c in range(w) for r in range(h) if grid[r][c] != "?"]

    if len(known) <= 1 or validate_grid(known):
        print(f"#{test_no} possible")
    else:
        print(f"#{test_no} impossible")
