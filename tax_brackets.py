import numpy as np


class TaxBrackets:
    """Computes tax revenue based on a distribution"""

    def __init__(self):
        self._brackets = []
        self._revenue = []
        self._sum = []

    @property
    def total_revenue(self):
        """Total tax revenue from all brackets"""
        return np.sum(self._revenue)

    @property
    def revenue(self):
        """Bracket-wise collected revenue"""
        assert len(self._revenue) == len(self._brackets)
        return self._revenue

    @property
    def sum(self):
        """Bracket-wise tax base (on which tax is levied)"""
        assert len(self._sum) == len(self._brackets)
        return self._sum

    def add(self, rate, threshold):
        if len(self._brackets) > 0:
            assert threshold > self._brackets[-1][1]
        self._brackets.append((rate, threshold))
        return self

    def iter_brackets(self):
        """Generator of tax brackets as (rate, low, high)"""
        for i in range(len(self._brackets)):
            rate, threshold_low = self._brackets[i]
            if i + 1 < len(self._brackets):
                threshold_high = self._brackets[i + 1][1]
                yield rate, threshold_low, threshold_high
            else:
                yield rate, threshold_low, None

    def compute(self, f):
        self._sum = []
        self._revenue = []
        for i, (r, a, b) in enumerate(self.iter_brackets()):
            r = r / 100
            s = f.band_sum(a, b)
            self._sum.append(s)
            self._revenue.append(r * s)
