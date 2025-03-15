import local


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
