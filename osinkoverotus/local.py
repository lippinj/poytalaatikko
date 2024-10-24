import numpy as np
from matplotlib import pyplot as plt


class Data:
    def __init__(
        self,
        corp_tax_rate=20,
        cap_tax_rate_lo=30,
        cap_tax_rate_hi=34,
        earn_tax_rate_lo=0,
        earn_tax_rate_hi=44 + 7.46 + 1.38,
    ):
        self.corp_tax_rate = corp_tax_rate
        self.cap_tax_rate_lo = cap_tax_rate_lo
        self.cap_tax_rate_hi = cap_tax_rate_hi
        self.earn_tax_rate_lo = earn_tax_rate_lo
        self.earn_tax_rate_hi = earn_tax_rate_hi
        self.labels = []
        self.corp_tax = []
        self.cap_tax_lo = []
        self.cap_tax_hi = []
        self.earn_tax_lo = []
        self.earn_tax_hi = []
        self.cap_net = []
        self.earn_net = []
        self.corp_tax_color = "cornflowerblue"
        self.cap_tax_color = "sandybrown"
        self.earn_tax_color = "peru"
        self.cap_net_color = "aquamarine"
        self.earn_net_color = "lightgreen"

    def __len__(self):
        return len(self.labels)

    @property
    def cap_tax_diff(self):
        return np.array(self.cap_tax_hi) - np.array(self.cap_tax_lo)

    @property
    def earn_tax_diff(self):
        return np.array(self.earn_tax_hi) - np.array(self.earn_tax_lo)

    @property
    def corp_tax_label(self):
        return f"yhteisövero, {self.corp_tax_rate}%"

    @property
    def cap_tax_label(self):
        return f"pääomatulovero, {self.cap_tax_rate_lo}%"

    @property
    def cap_tax_prog_label(self):
        return f"pääomatuloveron progressio, {self.cap_tax_rate_lo}% - {self.cap_tax_rate_hi}%"

    @property
    def earn_tax_label(self):
        return f"ansiotulovero, {self.earn_tax_rate_lo}%"

    @property
    def earn_tax_prog_label(self):
        return f"ansiotuloveron progressio, {self.earn_tax_rate_lo}% - {self.earn_tax_rate_hi}%"

    @property
    def cap_net_label(self):
        return f"nettotulo, pääomatuloa"

    @property
    def earn_net_label(self):
        return f"nettotulo, ansiotuloa"

    @property
    def has_corp_tax(self):
        return any(self.corp_tax)

    @property
    def has_cap_tax_lo(self):
        return any(self.cap_tax_lo)

    @property
    def has_cap_tax_hi(self):
        return any(self.cap_tax_hi)

    @property
    def has_cap_tax(self):
        return self.has_cap_tax_lo or self.has_cap_tax_hi

    @property
    def has_earn_tax_lo(self):
        return any(self.earn_tax_lo)

    @property
    def has_earn_tax_hi(self):
        return any(self.earn_tax_hi)

    @property
    def has_earn_tax(self):
        return self.has_earn_tax_lo or self.has_earn_tax_hi

    @property
    def has_cap_net(self):
        return any(self.cap_net)

    @property
    def has_earn_net(self):
        return any(self.earn_net)

    def append(self, *args):
        self.labels.append(args[0])
        self.corp_tax.append(args[1])
        self.cap_tax_lo.append(args[2])
        self.cap_tax_hi.append(args[3])
        self.earn_tax_lo.append(args[4])
        self.earn_tax_hi.append(args[5])
        if args[2] or args[3]:
            self.cap_net.append(100 - args[1] - args[3])
            self.earn_net.append(0)
        else:
            self.cap_net.append(0)
            self.earn_net.append(100 - args[1] - args[5])

    def sale(self, *args):
        self.push_sale(*args)
        return self

    def interest(self, *args):
        self.push_interest(*args)
        return self

    def div(self, *args):
        self.push_dividend(*args)
        return self

    def dive(self, *args):
        self.push_dividend_earned(*args)
        return self

    def wage(self, *args):
        self.push_wage(*args)
        return self

    def push_dividend(self, taxable=100, prefix=""):
        label = f"{prefix}{taxable}% veronalainen\npääomatulo-osinko"
        corp_tax = self.corp_tax_rate
        x = 100 - corp_tax
        xt = (taxable / 100) * x
        cap_tax_lo = (self.cap_tax_rate_lo / 100) * xt
        cap_tax_hi = (self.cap_tax_rate_hi / 100) * xt
        self.append(label, corp_tax, cap_tax_lo, cap_tax_hi, 0, 0)

    def push_dividend_earned(self, taxable=100, prefix=""):
        label = f"{prefix}{taxable}% veronalainen\nansiotulo-osinko"
        corp_tax = self.corp_tax_rate
        x = 100 - corp_tax
        x -= corp_tax
        xt = (taxable / 100) * x
        earn_tax_lo = (self.earn_tax_rate_lo / 100) * xt
        earn_tax_hi = (self.earn_tax_rate_hi / 100) * xt
        self.append(label, corp_tax, 0, 0, earn_tax_lo, earn_tax_hi)

    def push_sale(self, prefix=""):
        label = f"{prefix}luovutusvoitto"
        cap_tax_lo = self.cap_tax_rate_lo
        cap_tax_hi = self.cap_tax_rate_hi
        self.append(label, 0, cap_tax_lo, cap_tax_hi, 0, 0)

    def push_interest(self, prefix=""):
        label = f"{prefix}korkotulo"
        cap_tax_lo = self.cap_tax_rate_lo
        cap_tax_hi = self.cap_tax_rate_hi
        self.append(label, 0, cap_tax_lo, cap_tax_hi, 0, 0)

    def push_wage(self, prefix=""):
        label = f"{prefix}palkkatulo"
        earn_tax_lo = (self.earn_tax_rate_lo / 100) * (100 - 7.94)
        earn_tax_hi = (self.earn_tax_rate_hi / 100) * (100 - 7.94)
        self.append(label, 0, 0, 0, earn_tax_lo, earn_tax_hi)

    def plot_corp_tax(self, ax, top):
        if self.has_corp_tax:
            top -= self.corp_tax
            ax.bar(
                self.labels,
                self.corp_tax,
                bottom=top,
                color=self.corp_tax_color,
                label=self.corp_tax_label,
            )
        return top

    def plot_cap_tax(self, ax, top):
        if self.has_cap_tax_lo:
            top -= self.cap_tax_lo
            ax.bar(
                self.labels,
                self.cap_tax_lo,
                bottom=top,
                color=self.cap_tax_color,
                label=self.cap_tax_label,
            )
        if self.has_cap_tax_hi:
            top -= self.cap_tax_diff
            ax.bar(
                self.labels,
                self.cap_tax_diff,
                bottom=top,
                color=self.cap_net_color,
                hatch="/",
                edgecolor=self.cap_tax_color,
                linewidth=0,
                label=self.cap_tax_prog_label,
            )
        return top

    def plot_earn_tax(self, ax, top):
        if self.has_earn_tax_lo:
            top -= self.earn_tax_lo
            ax.bar(
                self.labels,
                self.earn_tax_lo,
                bottom=top,
                color=self.earn_tax_color,
                label=self.earn_tax_label,
            )
        if self.has_earn_tax_hi:
            top -= self.earn_tax_diff
            ax.bar(
                self.labels,
                self.earn_tax_diff,
                bottom=top,
                color=self.earn_net_color,
                hatch="/",
                edgecolor=self.earn_tax_color,
                linewidth=0,
                label=self.earn_tax_prog_label,
            )
        return top

    def plot_cap_net(self, ax, top):
        if self.has_cap_net:
            top -= self.cap_net
            ax.bar(
                self.labels,
                self.cap_net,
                bottom=top,
                color=self.cap_net_color,
                label=self.cap_net_label,
            )
        return top

    def plot_earn_net(self, ax, top):
        if self.has_earn_net:
            top -= self.earn_net
            ax.bar(
                self.labels,
                self.earn_net,
                bottom=top,
                color=self.earn_net_color,
                label=self.earn_net_label,
            )
        return top

    def plot_guides(self, ax):
        if self.has_cap_tax:
            y = 100 - self.cap_tax_rate_lo
            ax.axhline(y=y, linestyle=":", color="black", alpha=0.5)
            y = 100 - self.cap_tax_rate_hi
            ax.axhline(y=y, linestyle=":", color="black", alpha=0.5)
        if self.has_earn_tax:
            y = 100 - (self.earn_tax_rate_hi * (100 - 7.94) / 100)
            ax.axhline(y=y, linestyle=":", color="black", alpha=0.5)

    def plot(self, ax, title=None):
        plt.rcParams["hatch.linewidth"] = 8
        top = 100 * np.ones(len(self))
        top = self.plot_corp_tax(ax, top)
        top = self.plot_cap_tax(ax, top)
        top = self.plot_earn_tax(ax, top)
        top = self.plot_cap_net(ax, top)
        top = self.plot_earn_net(ax, top)
        self.plot_guides(ax)
        ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
        ax.set_ylabel("Osuus tuotosta (%)")
        ax.set_xlim(-0.6, len(self) - 0.4)
        if title:
            ax.set_title(title)
