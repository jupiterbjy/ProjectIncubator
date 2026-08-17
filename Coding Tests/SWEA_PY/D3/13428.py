# WHY THE HECK THIS IS D3???

def swap(top, string, tgt):
    l_, r = string.rsplit(tgt, 1)
    return tgt + l_ + top + r


def template(vals, method):
    """template for sorting either asc / desc"""
    top, rem = vals[0], vals[1:]
    if not rem:
        return top

    tgt = method(vals)
    return swap(top, rem, tgt) if top != tgt else top + template(rem, method)


def sort_once(vals):
    top, rem = vals[0], vals[1:]
    smallest = min((n for n in rem if n != "0"), default="9")

    out = swap(top, rem, smallest) if top > smallest else top + template(rem, min)
    return out, template(vals, max)


for test_no in range(1, int(input()) + 1):
    raw = input()
    print(f"#{test_no}", *((raw, raw) if len(raw) == 1 else sort_once(raw)))