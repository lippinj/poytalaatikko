import numpy as np
from matplotlib.ticker import FuncFormatter

from local.säännöt import enimmäismaksu


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
                text = f"{i}. lapsi, +{enimmäismaksu(i)} e/kk"
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
