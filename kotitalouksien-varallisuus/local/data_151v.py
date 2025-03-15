import numpy as np
from local.table_151v import Table151v


class Data151v:
    def __init__(self):
        self.table = Table151v()

    @property
    def df(self):
        return self.table.df

    @property
    def vuosi(self):
        return self.table.years

    @property
    def vlim(self):
        return self.vuosi[0], self.vuosi[-1]

    @property
    def luokat10(self):
        return [f"D{i}" for i in range(1, 11)]

    @property
    def luokat6(self):
        return ["D1-5", "D6", "D7", "D8", "D9", "D10"]

    def __call__(self, v=None, d="SS", l="n", t="nm"):
        if t == "nt":
            return self(v, d, l, "nm") * self(v, d, l, "hn")
        if t == "rt":
            return self(v, d, l, "rm") * self(v, d, l, "hn")
        if t == "szt":
            return self(v, d, l, "hsz") * self(v, d, l, "hn")

        v, d, l, t = self.table.expand(v, d, l, t)

        if d == "SS" or isinstance(d, int):
            return self.at(v, d, l, t)

        hn = Table151v.tiedot("hn")
        x = np.array([self.at(v, i, l, t) for i in range(*d)])
        w = np.array([self.at(v, i, l, hn) for i in range(*d)])
        return Table151v.aggregator(t)(x, w)

    def at(self, v, d, l, t):
        df = self.df
        df = df[df.Vuosi == str(v)]
        df = df[df.Nettovarallisuuskymmenys == str(d)]
        df = df[df.Varallisuuslaji == l]
        assert len(df) == 1, (v, d, l, t)
        return df.iloc[0][t]

    def h(self, d, l, t):
        return np.array([self(v, d, l, t) for v in self.vuosi])

    def v(self, v, l, t):
        return np.array([self(v, d, l, t) for d in range(1, 11)])

    def hf(self, d=10, l="n", t="nt", c=100):
        all = self.h("SS", l, t)
        top = self.h(d, l, t)
        return c * top / all
