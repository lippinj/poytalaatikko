import statfin
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import torch


COLORS = ["k", "k", "b", "k", "k", "r", "k", "k", "b", "k", "k"]


class Row:
    def __init__(self, row):
        self.p = np.array(
            [0.10, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.70, 0.75, 0.80, 0.90]
        )
        self.v = np.array(
            [
                row.P10,
                row.P20,
                row.Q1,
                row.P30,
                row.P40,
                row.P50,
                row.P60,
                row.P70,
                row.Q3,
                row.P80,
                row.P90,
            ]
        )
        self.m = row.Mean
        self.N = row.N
        self.raw = row
        self.sum = row.Sum
        self.fractiles = [(float(p), float(v)) for p, v in zip(self.p, self.v)]

    @property
    def P(self):
        return 100 * self.p

    @property
    def a(self):
        return self.v[:-1]

    @property
    def b(self):
        return self.v[1:]

    @property
    def w(self):
        return self.b - self.a

    @property
    def n(self):
        return self.N * (self.p[1:] - self.p[:-1])

    @property
    def d(self):
        return self.n / (self.w + 0.01)

    def dl(self, vmin):
        return (self.N * 0.10) / (self.v[0] - vmin + 0.01)

    def dr(self, vmax):
        return (self.N * 0.10) / (vmax - self.v[-1] + 0.01)

    def r2l(self, r):
        dp = self.p[1:] - self.p[:-1]
        mr = (self.b[-1] + r) / 2
        m = (self.a + self.b) / 2
        ml = (self.m - (0.10 * mr) - np.dot(dp, m)) / 0.10
        l = 2 * ml - self.b[0]
        return l

    def l2r(self, l):
        dp = self.p[1:] - self.p[:-1]
        ml = (self.b[0] + l) / 2
        m = (self.a + self.b) / 2
        mr = (self.m - (0.10 * ml) - np.dot(dp, m)) / 0.10
        r = 2 * mr - self.b[0]
        return r


class Data:
    def __init__(self, e="HVT_TULOT_50"):
        self.db = statfin.PxWebAPI.Verohallinto()
        self.table = self.db.table("Vero", "tulot_101.px")
        self.df = self.table.query(
            {
                "Verovuosi": "2023",
                "Erä": e,
                "Tulonsaajaryhmä": "Y",
                "Tuloluokka": "*",
            },
            cache="tulot_101.px",
        )

    def income_class_name(self, code):
        df = self.table.values["Tuloluokka"]
        return df[df.code == str(code)].iloc[0].text

    def row(self, income_class_code):
        row = self.df[self.df.Tuloluokka == str(income_class_code)]
        return Row(row.iloc[0])


class Chunk:
    def __init__(self, row):
        self.row = row
        self.vmin = max(0, row.v[0] - (row.v[1] - row.v[0]))
        self.vmax = row.l2r(self.vmin)

    def x_interior(self):
        return np.linspace(self.row.v[0], self.row.v[-1], 10_000)

    def x_left(self):
        return np.linspace(self.vmin, self.row.v[0], 1_000)

    def x_right(self):
        return np.linspace(self.row.v[-1], self.vmax, 1_000)

    def cumulative(self, x):
        try:
            return np.array([self.cumulative(e) for e in x])
        except TypeError:
            if x < self.vmin:
                return 0.0
            elif x > self.vmax:
                return 100.0
            elif x <= self.row.v[0]:
                t = (x - self.vmin) / (self.row.v[0] - self.vmin)
                return t * self.row.P[0] + (1 - t) * 0.0
            elif x > self.row.v[-1]:
                t = (x - self.row.v[-1]) / (self.vmax - self.row.v[-1])
                return t * 100.0 + (1 - t) * self.row.P[-1]
            else:
                i = np.searchsorted(self.row.v, x) - 1
                t = (x - self.row.v[i]) / (self.row.v[i + 1] - self.row.v[i])
                return t * self.row.P[i + 1] + (1 - t) * self.row.P[i]

    def density(self, x):
        try:
            return np.array([self.density(e) for e in x])
        except TypeError:
            if x < self.vmin:
                return 0.0
            elif x > self.vmax:
                return 0.0
            elif x <= self.row.v[0]:
                return self.row.dl(self.vmin)
            elif x > self.row.v[-1]:
                return self.row.dr(self.vmax)
            else:
                return self.row.d[np.searchsorted(self.row.v, x) - 1]


class Chunk:
    def __init__(self, row):
        self.row = row
        self.vmin = max(0, row.v[0] - (row.v[1] - row.v[0]))
        self.vmax = row.l2r(self.vmin)

    def x_interior(self):
        return np.linspace(self.row.v[0], self.row.v[-1], 10_000)

    def x_left(self):
        return np.linspace(self.vmin, self.row.v[0], 1_000)

    def x_right(self):
        return np.linspace(self.row.v[-1], self.vmax, 1_000)

    def cumulative(self, x):
        try:
            return np.array([self.cumulative(e) for e in x])
        except TypeError:
            if x < self.vmin:
                return 0.0
            elif x > self.vmax:
                return 100.0
            elif x <= self.row.v[0]:
                t = (x - self.vmin) / (self.row.v[0] - self.vmin)
                return t * self.row.P[0] + (1 - t) * 0.0
            elif x > self.row.v[-1]:
                t = (x - self.row.v[-1]) / (self.vmax - self.row.v[-1])
                return t * 100.0 + (1 - t) * self.row.P[-1]
            else:
                i = np.searchsorted(self.row.v, x) - 1
                t = (x - self.row.v[i]) / (self.row.v[i + 1] - self.row.v[i])
                return t * self.row.P[i + 1] + (1 - t) * self.row.P[i]

    def density(self, x):
        try:
            return np.array([self.density(e) for e in x])
        except TypeError:
            if x < self.vmin:
                return 0.0
            elif x > self.vmax:
                return 0.0
            elif x <= self.row.v[0]:
                return self.row.dl(self.vmin)
            elif x > self.row.v[-1]:
                return self.row.dr(self.vmax)
            else:
                return self.row.d[np.searchsorted(self.row.v, x) - 1]


def autolims(row):
    dv = row.v[-1] - row.v[0]
    vmin = max(0, row.v[0] - 0.10 * dv)
    vmax = row.v[-1] + 0.10 * dv
    return vmin, vmax


def plot_cumulative_2(ax, chunk, plot_ext=True):
    row = chunk.row
    x = chunk.x_interior()
    ax.plot(x, chunk.cumulative(x), linestyle=":", color="k")
    ax.plot(row.v, row.P, linewidth=0, marker=".", color="k")
    ax.plot(
        [row.v[2], row.v[8]],
        [row.P[2], row.P[8]],
        linewidth=0,
        marker=".",
        color="b",
        markersize=8,
    )
    ax.plot([row.v[5]], [row.P[5]], linewidth=0, marker=".", color="r", markersize=10)
    ax.hlines(
        y=row.P,
        xmin=0,
        xmax=row.v,
        colors=COLORS,
        linewidth=1,
        alpha=0.3,
        linestyle=":",
    )
    ax.vlines(
        x=row.v,
        ymin=0,
        ymax=row.P,
        colors=COLORS,
        linewidth=1,
        alpha=0.3,
        linestyle=":",
    )
    ax.axvline(x=row.m, color="g", alpha=0.5)

    if plot_ext:
        xl = chunk.x_left()
        xr = chunk.x_right()
        ax.plot(xl, chunk.cumulative(xl), linestyle=":", color="k", alpha=0.25)
        ax.plot(xr, chunk.cumulative(xr), linestyle=":", color="k", alpha=0.25)
        ax.scatter([chunk.vmin, chunk.vmax], [0, 100], color="k", alpha=0.25, s=10)
        ax.set_xlim(chunk.vmin, chunk.vmax)
    else:
        ax.set_xlim(*autolims(row))
    ax.set_ylim(0, 100)

    ax.set_xlabel("Total income, euros per year")
    ax.set_ylabel("Cumulative individuals, %")


def plot_cumulative(ax, row, vmin=None, vmax=None):
    ax.plot(row.v, row.P, linestyle=":", marker=".", color="k")
    ax.plot(
        [row.v[2], row.v[8]],
        [row.P[2], row.P[8]],
        linewidth=0,
        marker=".",
        color="b",
        markersize=8,
    )
    ax.plot([row.v[5]], [row.P[5]], linewidth=0, marker=".", color="r", markersize=10)
    ax.hlines(
        y=row.P,
        xmin=0,
        xmax=row.v,
        colors=COLORS,
        linewidth=1,
        alpha=0.3,
        linestyle=":",
    )
    ax.vlines(
        x=row.v,
        ymin=0,
        ymax=row.P,
        colors=COLORS,
        linewidth=1,
        alpha=0.3,
        linestyle=":",
    )
    ax.axvline(x=row.m, color="g", alpha=0.5)

    if vmin is not None:
        ax.plot([vmin, row.v[0]], [0, row.P[0]], linestyle=":", color="k", alpha=0.25)
        ax.plot(
            [row.v[-1], vmax], [row.P[-1], 100], linestyle=":", color="k", alpha=0.25
        )
        ax.scatter([vmin, vmax], [0, 100], color="k", alpha=0.25, s=10)
    else:
        vmin, vmax = autolims(row)

    ax.set_xlim(vmin, vmax)
    ax.set_ylim(0, 100)

    ax.set_xlabel("Total income, euros per year")
    ax.set_ylabel("Cumulative individuals, %")


def plot_density(ax, row, vmin=None, vmax=None):
    ax.bar(row.a, row.d, width=row.w, align="edge", color="k", alpha=0.25)
    ax.vlines(
        x=row.v,
        ymin=0,
        ymax=[*row.d, row.d[-1]],
        colors=COLORS,
        linewidth=1,
        linestyle=":",
    )
    ax.axvline(x=row.m, color="g", alpha=0.5)

    if vmin is not None:
        ax.bar(
            [vmin],
            [row.dl(vmin)],
            width=row.v[0] - vmin,
            align="edge",
            color="k",
            alpha=0.10,
        )
        ax.bar(
            [row.v[-1]],
            [row.dr(vmax)],
            width=vmax - row.v[-1],
            align="edge",
            color="k",
            alpha=0.10,
        )
    else:
        vmin, vmax = autolims(row)

    ax.set_xlim(vmin, vmax)
    ax.set_ylim(0, sorted(row.d)[-2] * 1.4)

    ax.set_xlabel("Total income, euros per year")
    ax.set_ylabel("Density of individuals, €⁻¹")


class Segment:
    def __init__(self, offset: int, begin: int, end: int, lo: float, hi: float | None):
        self.offset = offset
        self.begin = begin
        self.end = end
        self.lo = lo
        self.hi = hi

    @property
    def count(self):
        return self.end - self.begin

    @property
    def i(self):
        return self.offset

    @property
    def j(self):
        return self.offset + self.count

    @property
    def span(self):
        return self.hi - self.lo if self.hi else None

    @property
    def base(self):
        return self.lo * self.count

    @property
    def implied_step(self):
        return self.span / (self.count + 1) if self.span else None

    def __repr__(self):
        return f"<Segment [{self.begin}, {self.end}) {self.lo}..{self.hi}>"


class Problem:
    def __init__(self, count: int, total: float, fractiles: list[tuple[int, float]]):
        self.count = count
        self.total = total
        self.fixpoints = Problem._compute_fixpoints(count, fractiles)
        self.segments = Problem._compute_segments(count, self.fixpoints)
        self.fixed_count = len(self.fixpoints)
        self.fixed_total = np.sum([v for n, v in self.fixpoints])
        self.base_total = np.sum([seg.base for seg in self.segments])
        self.free_count = count - self.fixed_count
        self.free_total = total - self.fixed_total - self.base_total

    @staticmethod
    def _compute_fixpoints_sparse(
        count: int, fractiles: list[tuple[int, float]]
    ) -> list[tuple[int, float]]:
        result = []
        for p, v in fractiles:
            n = p * count
            if n == round(n):
                result.append((n, v))
            else:
                result.append((int(n), v))
                result.append((int(n) + 1, v))
        return result

    @staticmethod
    def _compute_fixpoints(
        count: int, fractiles: list[tuple[int, float]]
    ) -> list[tuple[int, float]]:
        result = []
        prevn, prevv = 0, 0
        for n, v in Problem._compute_fixpoints_sparse(count, fractiles):
            if v == prevv:
                for i in range(prevn + 1, n):
                    result.append((i, v))
            result.append((n, v))
            prevn, prevv = n, v
        return result

    @staticmethod
    def _compute_segments(
        count: int, fixpoints: list[tuple[int, float]]
    ) -> list[Segment]:
        result = []
        i, lo = 0, 0
        for j, hi in fixpoints:
            if j > i:
                offset = 0 if len(result) == 0 else result[-1].j
                result.append(Segment(offset, i, j, lo, hi))
            i = j + 1
            lo = hi
        result.append(Segment(result[-1].j, i, count, lo, None))
        return result
