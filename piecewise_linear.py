import scipy
import numpy as np
from numpy.testing import assert_almost_equal
from dataclasses import dataclass


def _lerp(t, a, b):
    return t * b + (1 - t) * a


class PiecewiseLinear:
    """Piecewise linear function."""

    def __init__(self, xp, yp, low=None, high=None):
        self.xp = np.array(xp)
        self.yp = np.array(yp)
        self.low = low
        self.high = high
        assert len(xp) == len(yp)
        assert all(xp[1:] >= xp[:-1])
        assert all(yp[1:] >= yp[:-1])

    @property
    def xmin(self):
        return self.xp[0]

    @property
    def xmax(self):
        return self.xp[-1]

    @property
    def ymin(self):
        return self.yp[0]

    @property
    def ymax(self):
        return self.yp[-1]

    def __call__(self, x):
        return np.interp(x, self.xp, self.yp, self.low, self.high)

    def clip(self, lo=None, hi=None):
        if lo is None and hi is None:
            return self
        yp = np.clip(self.yp, lo, hi)
        low = None if self.low is None else np.clip(self.low, lo, hi)
        high = None if self.high is None else np.clip(self.high, lo, hi)
        return PiecewiseLinear(self.xp, yp, low, high)

    def band_sum(self, lo=None, hi=None):
        return self.clip(None, hi).sum() - self.clip(None, lo).sum()

    def pieces(self):
        low = self.low or self.yp[0]
        high = self.high or self.yp[-1]
        yield None, self.xp[0], low, low
        for i in range(len(self.xp) - 1):
            yield self.xp[i], self.xp[i + 1], self.yp[i], self.yp[i + 1]
        yield self.xp[-1], None, high, high

    def overlaps(self, a, b):
        a = a or self.xmin
        b = b or self.xmax
        for xa, xb, ya, yb in self.pieces():
            if xa is None:
                assert ya == yb
                if a < xb:
                    yield a, xb, ya, ya
            elif xb is None:
                assert ya == yb
                if b > xa:
                    yield xa, b, yb, yb
            else:
                Xa = max(xa, a)
                Xb = min(xb, b)
                if Xb > Xa:
                    ta = (Xa - xa) / (xb - xa)
                    tb = (Xb - xa) / (xb - xa)
                    Ya = _lerp(ta, ya, yb)
                    Yb = _lerp(tb, ya, yb)
                    yield Xa, Xb, Ya, Yb

    def inv(self, y):
        return np.interp(y, self.yp, self.xp, self.xp[0], self.xp[-1])

    def sum(self, a=None, b=None):
        """∫f(x)dx from x=a to x=b"""
        a = a or self.xmin
        b = b or self.xmax
        s = 0.0
        for xa, xb, ya, yb in self.overlaps(a, b):
            s += (xb - xa) * (ya + yb) / 2
        return s

    def mean(self, a=None, b=None):
        a = a or self.xmin
        b = b or self.xmax
        return self.sum(a, b) / (b - a)


class PiecewiseLinearBuilder:
    """Optimizing builder for a PiecewiseLinear."""

    @dataclass
    class Segment:
        def __init__(self, xa, xb, mean, samples):
            W = xb - xa
            x = np.array([xa] + [xa + r * W for r, y in samples] + [xb])
            y = np.array([y for r, y in samples])
            w = (x[1:] - x[:-1]) / W
            C = ((2 * mean) - (w[:-1] + w[1:]).dot(y)) / w[-1]
            D = w[0] / w[-1]
            assert all(x >= xa)
            assert all(x <= xb)
            assert all(w >= 0)
            self.x = x
            self.y = y
            self.C = C
            self.D = D

        def b(self, a):
            return self.C - self.D * a

    def __init__(self):
        self._start = 0.0
        self._segments = []
        self.score_middle = self.center_exp_l2

    @property
    def top(self):
        if len(self._segments) > 0:
            return self._segments[-1].x[-1]
        else:
            return self._start

    @property
    def bot(self):
        if len(self._segments) > 0:
            return self._segments[-1].x[0]
        else:
            return self._start

    def start(self, x):
        assert len(self._segments) == 0
        self._start = x

    def segment(self, width, mean, samples):
        xa = self.top
        xb = self.top + width
        seg = PiecewiseLinearBuilder.Segment(xa, xb, mean, samples)
        self._segments.append(seg)

    def build(self, a):
        x = [[self._start]]
        y = [[a]]
        for seg in self._segments:
            b = seg.b(a)
            x.append(seg.x[1:])
            y.append(seg.y)
            y.append([b])
            a = b
        x = np.concatenate(x)
        y = np.concatenate(y)
        return PiecewiseLinear(x, y)

    def score(self, a):
        assert len(self._segments) >= 1
        if len(self._segments) == 1:
            raise NotImplementedError
        else:
            s = 0.0
            for i in range(len(self._segments) - 1):
                seg_a = self._segments[i]
                seg_b = self._segments[i + 1]
                b = seg_a.b(a)
                s += self.score_middle(seg_a, b, seg_b)
                a = b
            return s

    def optimize(self):
        assert len(self._segments) >= 1
        opt = scipy.optimize.minimize(lambda x: self.score(x[0]), self.bot)
        assert opt.success
        return opt.x[0]

    def build_optimized(self):
        return self.build(self.optimize())

    @staticmethod
    def center_exp_l2(seg_a, b, seg_b):
        a = seg_a.y[-1]
        c = seg_b.y[0]
        if a >= 1:
            return ((c / b) - (b / c)) ** 2
        else:
            return ((c - b) - (b - a)) ** 2


def test_build_from_household_stats():
    N0 = 279_305
    N1 = 278_626
    N = N0 + N1

    m0 = -17_467
    m1 = 1_260

    p25_0 = -16_951
    p50_0 = -8_141
    p75_0 = -3_630
    p25_1 = 283
    p50_1 = 1_000
    p75_1 = 2_043

    builder = PiecewiseLinearBuilder()
    builder.segment(N0, m0, [(0.25, p25_0), (0.50, p50_0), (0.75, p75_0)])
    builder.segment(N1, m1, [(0.25, p25_1), (0.50, p50_1), (0.75, p75_1)])
    L = builder.build_optimized()

    assert L(N0 * (1 / 4)) == p25_0
    assert L(N0 * (2 / 4)) == p50_0
    assert L(N0 * (3 / 4)) == p75_0
    assert L(N0 + N1 * (1 / 4)) == p25_1
    assert L(N0 + N1 * (2 / 4)) == p50_1
    assert L(N0 + N1 * (3 / 4)) == p75_1

    assert_almost_equal(L.mean(0, N0), m0)
    assert_almost_equal(L.mean(N0, N), m1)
    assert_almost_equal(L.inv(p75_0), N0 * (3 / 4))
    assert_almost_equal(L.inv(p75_1), N0 + N1 * (3 / 4))
    assert_almost_equal(L(L.inv(-101)), -101)

    assert_almost_equal(L.sum(1, 3), L.sum(1, 2) + L.sum(2, 3), decimal=2)
    assert_almost_equal(L.sum(), L.sum(None, 254_300) + L.sum(254_300, None), decimal=2)
    assert_almost_equal(
        L.sum(),
        L.sum(None, 9_999) + L.sum(9_999, 401_000) + L.sum(401_000, None),
        decimal=2,
    )

    assert_almost_equal(
        L.band_sum(p75_1, None),
        L.sum(N0 + (3 / 4) * N1, None) - ((N1 / 4) * p75_1),
        decimal=2,
    )
    assert_almost_equal(
        L.band_sum(p50_1, None),
        L.sum(N0 + (2 / 4) * N1, None) - ((N1 / 2) * p50_1),
        decimal=2,
    )
