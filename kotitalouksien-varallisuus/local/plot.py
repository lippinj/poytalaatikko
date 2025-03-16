import itertools
import matplotlib.axes
import local


SOURCELINE = "Data: 151v - Kotitalouksien varat, velat ja tulot kotitalouden nettovarallisuuskymmenyksen mukaan, 1987-2023 (Tilastokeskus)"


def italics(s):
    return " ".join([f"$\\it{{{e}}}$" for e in s.split()])


def flatax(ax):
    if isinstance(ax[0], matplotlib.axes.Axes):
        return ax
    return list(itertools.chain(*ax))


def osuudet(ax, data, t, l, colors=None):
    colors = colors or local.colors.colors6()
    bot = data.vuosi * 0
    for d in data.luokat6:
        top = bot + data.hf(t=t, l=l, d=d)
        ax.fill_between(data.vuosi, bot, top, color=colors[d], label=d)
        bot = top
    ax.legend(loc="upper right")
    ax.set_xlim(data.vuosi[0], data.vuosi[-1])
    ax.set_ylim(0, 100)
    ax.set_ylabel("Osuus summasta yhteensä (%)")


def lajeittain(fig, ax, data, lajit, yfun, ylabel, ylim=None, colors=None, boty=0.07):
    ax = flatax(ax)
    colors = colors or local.colors.colors6()
    ylim = ylim or [None] * len(lajit)

    for i, l in enumerate(lajit):
        laji(ax[i], data, l, yfun, ylabel, colors, (0, ylim[i]))

    fig.subplots_adjust(hspace=0.35, wspace=0.25)
    fig.text(0.1, boty, SOURCELINE)


def laji(ax, data, l, yfun, ylabel, colors=None, ylim=None, title=None):
    colors = colors or local.colors.colors6()
    ylim = ylim or (0, None)

    for d in data.luokat6:
        y = yfun(d, l)
        ax.plot(data.vuosi, y, color=colors[d], marker=".", label=d)
    ax.plot(data.vuosi, yfun("SS", l), color=colors["SS"], linestyle="--", label="yht.")

    ax.set_title(data.table.label_varallisuuslaji(l))
    ax.set_ylabel(ylabel)
    ax.set_xlim(*data.vlim)
    ax.set_ylim(*ylim)
    ax.legend(loc="upper left")

    if title:
        ax.set_title(title)
