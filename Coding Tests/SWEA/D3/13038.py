for test_no in range(1, int(input()) + 1):
    tgt = int(input())
    days = [idx for idx, val in enumerate(input().split()) if val == "1"]

    if tgt == 1:
        print(f"#{test_no} 1")
        continue

    # skip day 1 calculation, so end of dist is always lecture day
    total = 1
    tgt -= 1

    # calc distance to next lecture
    dists = [b - a for a, b in zip(days, days[1:])]
    dists.append(7 - days[-1] + days[0])

    # get full-week duration
    quo, rem = divmod(tgt, len(days))
    total += quo * 7

    # if remainder exists, choose the shortest sum of distances
    if rem:
        dists.extend(dists)
        total += min(sum(dists[i] for i in range(idx, idx + rem)) for idx in range(len(days)))

    print(f"#{test_no}", total)
