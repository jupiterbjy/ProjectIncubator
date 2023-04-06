

def rgb_to_hex(r=0, g=0, b=0):
    arr = [r, g, b]
    out = [str(hex(i))[2:].zfill(2) for i in arr]
    return "#" + "".join(out)


def hex_to_rgb(hex_string: str):
    hex_string = hex_string.lstrip("#")
    iterator = iter(hex_string)
    return tuple((int(d1 + d2, base=16) for d1, d2 in zip(iterator, iterator)))

