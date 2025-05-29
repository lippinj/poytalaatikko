import numpy as np


# Korkein maksuprosentti tulorajan ylittävältä osalta
maksuprosentti = 10.70 / 100

# Korkein ensimmäisen lapsen enimmäismaksu
enimmäismaksu0 = 311

# Matalin perittävä maksu
maksukynnys = 30


def tuloraja(n):
    """Asiakasmaksun tuloraja, kun perheessä on n jäsentä"""
    DATA = [None, None, 4066, 5245, 5956, 6667, 7376]
    return DATA[min(n, 6)] + max(n - 6, 0) * 275


def yläraja(n):
    """Tuloraja, jolla maksu maksimoituu"""
    return tuloraja(n) + enimmäismaksu0 / maksuprosentti


def maksukerroin(i):
    """Asiakasmaksun kerroin i:nnelle lapselle"""
    assert i >= 1
    return [0.0, 1.0, 0.4, 0.2][min(i, 3)]


def maksukerroin_summa(n):
    """Maksukertoimien 1,...,n summa"""
    return sum([maksukerroin(i + 1) for i in range(n)])


def enimmäismaksu(i):
    """Enimmäismaksu i:nnestä lapsesta"""
    return round(maksukerroin(i) * enimmäismaksu0)


class Lapsi:
    def __init__(self, i, t):
        self.i = i
        self.k = maksukerroin(i)
        self.cap = enimmäismaksu(i)
        self.y = np.clip(maksuprosentti * self.k * t, 0, self.cap)
        self.z = (self.y >= 29.5) * self.y


class Maksut:
    def __init__(self, n, m):
        self.n = n
        self.m = m

        self.x0 = tuloraja(n + m)
        self.x1 = yläraja(n + m)

        self.x = np.hstack([[0], np.arange(self.x0, self.x1, 0.1), [20_000]])
        self.t = np.clip(self.x - self.x0, 0, None)

        self.lapset = [Lapsi(i, self.t) for i in range(1, n + 1)]

        self.y = np.sum([l.y for l in self.lapset], axis=0)
        self.z = np.sum([l.z for l in self.lapset], axis=0)
        self.i = np.where(self.y > self.z)[0]
        self.iz = self.i[-1] + 1
        self.xz = self.x[self.iz]
        self.yz = self.y[self.iz]

    @property
    def rate(self):
        return maksukerroin_summa(self.n) * maksuprosentti

    def slopepoint(self, t):
        x = ((1 - t) * self.xz) + (t * self.x1)
        y = ((1 - t) * self.yz) + (t * self.y[-1])
        return x, y

    def at(self, n):
        lo = 0.0 * self.y
        for i in range(0, n - 1):
            lo += self.lapset[i].z
        hi = lo + self.lapset[n - 1].z
        return lo, hi, self.lapset[n - 1]
