import statfin


_df = None

def df():
    global _df
    if _df is None:
        _df = statfin.StatFin().Kok.trek._131w.query(
            Sukupuoli="SSS",
            Tulonsaajaryhmä="SSS",
            Ikäluokka="SSS",
            Tuloluokka="SSS",
            Tuloerä="A00" # Palkat ja palkkiotulot
        )()
    return _df


def q1():
    return df().q1.mean()


def med():
    return df().med.mean()


def q3():
    return df().q3.mean()


def d9():
    return df().p90.mean()
