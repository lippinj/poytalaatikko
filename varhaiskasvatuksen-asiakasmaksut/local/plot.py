import numpy as np
from matplotlib.ticker import FuncFormatter

from local import säännöt, tulot


def _kformat(x, _):
    s = f"{int(x):,}"
    s = s.replace(",", " ")
    return s


kformatter = FuncFormatter(_kformat)


def aspect(ax):
    """Aspect ratio of the axis"""
    tinv = ax.figure.dpi_scale_trans.inverted()
    bbox = ax.get_window_extent().transformed(tinv)
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    kx = (x1 - x0) / bbox.width
    ky = (y1 - y0) / bbox.height
    return ky / kx


def slopetext(slope, ax):
    return dict(
        rotation=np.degrees(np.arctan2(slope, aspect(ax))),
        rotation_mode="anchor",
        va="bottom",
        ha="center",
    )


def slope_label(ax, m, t=0.47):
    x, y = m.slopepoint(t)
    ax.text(
        x,
        y * 1.01,
        f"maksuprosentti yht. {100*m.rate:.1f}%",
        **slopetext(m.rate, ax),
        size=12,
        style="italic",
    )


def fan_fill(ax, m, labels=False, offset=0.0, alpha_step=0.025):
    for i in range(1, m.n + 1):
        lo, hi, lapsi = m.at(i)
        ax.fill_between(
            m.x,
            lo + offset,
            hi + offset,
            color="k",
            alpha=i * alpha_step
        )
        if labels:
            if i == 1:
                x = m.x1 + 525
                text = "1. lapsi, 311 e/kk"
            else:
                x = m.x1 + 525
                text = f"{i}. lapsi, +{säännöt.enimmäismaksu(i)} e/kk"
            y = 0.5 * (lo[-1] + hi[-1])
            ax.text(
                x,
                y,
                text,
                size=10,
                weight=600,
                color="#444",
                va="center",
                ha="center",
            )


def backlines(ax, n, m, h, do_p90=False):
    assert m in (1, 2)

    yh = m == 1
    ne = np.arange(n[0] - 1, n[-1] + 2)
    nn = np.hstack([[x - h/2, x + h/2] for x in ne])
    ll = np.repeat(säännöt.lapsilisä(ne, yh), 2)

    q1 = m * tulot.q1() + ll
    md = m * tulot.med() + ll
    q3 = m * tulot.q3() + ll
    d9 = m * tulot.d9() + ll

    #ax.axvline(2 * xq1, zorder=-1, color="#999", linestyle=":")
    #ax.axvline(2 * xmd, zorder=-1, color="#999", linestyle="--")
    #ax.axvline(2 * xq3, zorder=-1, color="#999", linestyle=":")
    ax.plot(q1, nn, zorder=-1, color="#999", linestyle=":")
    ax.plot(md, nn, zorder=-1, color="#999", linestyle="--")
    ax.plot(q3, nn, zorder=-1, color="#999", linestyle=":")
    if do_p90:
        ax.plot(d9, nn, zorder=-1, color="#ccc", linestyle=":")

    xoffset = 100
    style = dict(size=12, rotation=0, color="#333", va="top", ha="right")
    ax.text(q1[0] - xoffset, n[0] - 0.62, "$Q_1$", **style, label="")
    ax.text(md[0] - xoffset, n[0] - 0.62, "$M$", **style)
    ax.text(q3[0] - xoffset, n[0] - 0.62, "$Q_3$", **style)
    if do_p90:
        ax.text(d9[0] - xoffset, n[0] - 0.62, "$P_{90}$", **style)
