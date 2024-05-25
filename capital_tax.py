import numpy as np


class CapitalTax:
    """Simulator for different ways of taxing capital"""

    def __init__(self, initial=100.0):
        # Time point
        self._time = [0]
        # All held capital, including gains not yet taxed
        self._capital = [initial]
        # Portion of held capital for which all gains taxes have been paid
        self._redeemed = [initial]
        # Taxes paid on the current time step
        self._taxes = [0.0]
        # Cumulative taxes paid (over all time steps)
        self._total_taxes = [0.0]

    def __len__(self):
        return len(self._time)

    @property
    def time(self):
        return np.array(self._time)

    @property
    def capital(self):
        return np.array(self._capital)

    @property
    def redeemed_capital(self):
        return np.array(self._redeemed_capital)

    @property
    def taxes(self):
        return np.array(self._taxes)

    @property
    def total_taxes(self):
        return np.array(self._total_taxes)

    def appreciate(self, rate):
        """Advance a time step, appreciating held capital."""
        self._time.append(self._time[-1] + 1)
        self._capital.append(self._capital[-1] * (1.0 + rate))
        self._redeemed.append(self._redeemed[-1])
        self._taxes.append(0.0)
        self._total_taxes.append(self._total_taxes[-1])

    def tax_gains(self, rate):
        """Apply a tax to all gains untaxed so far."""
        taxable = self._capital[-1] - self._redeemed[-1]
        revenue = rate * taxable
        self._capital[-1] -= revenue
        self._redeemed[-1] = self._capital[-1]
        self._taxes[-1] += revenue
        self._total_taxes[-1] += revenue

    def tax_wealth(self, rate):
        """Apply a tax to wealth, irrespective of gains.

        The wealth is taken to be the average wealth over the current step.
        """
        taxable = np.mean(self._capital[-2:])
        revenue = rate * taxable
        self._capital[-1] -= revenue
        self._taxes[-1] += revenue
        self._total_taxes[-1] += revenue

    @staticmethod
    def run_one_shot_gains_tax(N, profit_rate, tax_rate):
        """Run a scenario where all gains are taxed at the end."""
        ct = CapitalTax()
        for n in range(N):
            ct.appreciate(profit_rate)
        ct.tax_gains(tax_rate)
        return ct

    @staticmethod
    def run_regular_gains_tax(N, profit_rate, tax_rate):
        """Run a scenario where gains are taxed every period."""
        ct = CapitalTax()
        for n in range(N):
            ct.appreciate(profit_rate)
            ct.tax_gains(tax_rate)
        return ct

    @staticmethod
    def run_wealth_tax(N, profit_rate, tax_rate):
        """Run a scenario where wealth is taxed every period."""
        ct = CapitalTax()
        for n in range(N):
            ct.appreciate(profit_rate)
            ct.tax_wealth(tax_rate)
        return ct

    def npv(self, interest):
        """Net present value of tax revenues"""
        d = 1.0
        sum = 0.0
        for t in self._taxes:
            sum += d * t
            d /= 1.0 + interest
        return sum

    def print_report(self):
        print("-------------------------------------------")
        print("  time  capital      tax  cum.tax     total")
        print("-------------------------------------------")
        if len(self) <= 12:
            for n in range(len(self)):
                self.print_report_line(n)
        else:
            for n in range(3):
                self.print_report_line(n)
            print("   ...")
            for n in range(3):
                self.print_report_line(len(self) - 3 + n)

    def print_report_line(self, n):
        B = self._capital[n]
        t = self._taxes[n]
        T = self._total_taxes[n]
        print(f"{n:>6} {B:>8.2f} {t:>8.2f} {T:>8.2f} {T+B:>8.2f}")
