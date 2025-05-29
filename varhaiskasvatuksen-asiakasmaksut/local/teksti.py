def aikuisia(n):
    if n == 1:
        return "yksi aikuinen"
    else:
        assert n == 2
        return "kaksi aikuista"


def lapsia(n):
    WORDS = ["kaksi", "kolme", "neljä", "viisi", "kuusi", "seitsemän", "kahdeksan"]
    if n == 1:
        return "yksi varhaiskasvatuksessa oleva lapsi"
    elif n - 2 < len(WORDS):
        return f"{WORDS[n - 2]} varhaiskasvatuksessa olevaa lasta"
    else:
        return f"{n} lasta"
