import matplotlib.colors


def _hsv(h, s, v, a=1.0):
    return (matplotlib.colors.hsv_to_rgb((h, s, v)), a)


def _colors6(vals):
    keys = ["D1-5", "D6", "D7", "D8", "D9", "D10"]
    return {k: v for k, v in zip(keys, vals)}


def colors6(s=1, v=0.75, r=0.12):
    return _colors6([_hsv(r * t, s, v) for t in range(6)])


def colors6b():
    return _colors6(
        [
            "firebrick",  # D 1-5
            "darkorange",  # D6
            "gold",  # D7
            "seagreen",  # D8
            "dodgerblue",  # D9
            "mediumblue",  # D10
        ]
    )


def colors10():
    keys = [f"D{i}" for i in range(1, 11)]
    vals = [(0, 0, 0, 0.2 + 0.08 * i) for i in range(9)]
    vals += [(1, 0, 0)]
    return {k: v for k, v in zip(keys, vals)}
