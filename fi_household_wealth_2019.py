from matplotlib import pyplot as plt
from piecewise_linear import PiecewiseLinear, PiecewiseLinearBuilder
from tax_brackets import TaxBrackets

# Nettovarallisuus tietokannasta:
# pxdata.stat.fi/PxWeb/pxweb/fi/StatFin/StatFin__vtutk/statfin_vtutk_pxt_136z.px
DATA_2019 = [
    #    lkm  keskiarvo   alakvart.  mediaani   yläkvart.
    (279_305,   -17_467,   -16_915,    -8_141,    -3_630),
    (278_626,     1_260,       283,     1_000,     2_043),
    (278_339,    10_123,     5_857,     9_373,    13_499),
    (279_243,    39_519,    28_749,    38_849,    50_161),
    (278_384,    83_157,    72_019,    84_085,    94_190),
    (278_451,   128_686,   116_000,   128_730,   141_716),
    (278_953,   185_326,   170_360,   186_062,   200_280),
    (278_510,   260_032,   238_101,   257_880,   279_583),
    (278_708,   392_592,   346_738,   386_344,   433_791),
    (278_681, 1_065_204,   606_702,   766_220, 1_088_466),
]


def WealthStats():
    builder = PiecewiseLinearBuilder()
    for count, mean, p25, p50, p75 in DATA_2019:
        segments = [(0.25, p25), (0.50, p50), (0.75, p75)]
        builder.segment(count, mean, segments)
    return builder.build_optimized()


def report_wealth_stats(stats):
    print(f"Kotitalouksia yhteensä:                 {int(stats.xmax):>9,}")
    print(f"Nettovarallisuuden keskiarvo:           {stats.mean():>9,.0f}")
    print(f"Nettovarallisuus yhteensä:              {stats.sum()*1e-9:5.0f} mrd.")
    print(f"Nettovarallisuus yhteensä, ≥ 0:         {stats.band_sum(0)*1e-9:5.0f} mrd.")
    print(f"Nettovarallisuus yhteensä, ≥ 100 000:   {stats.band_sum(100_000)*1e-9:5.0f} mrd.")
    print(f"Nettovarallisuus yhteensä, ≥ 500 000:   {stats.band_sum(500_000)*1e-9:5.0f} mrd.")
    print(f"Nettovarallisuus yhteensä, ≥ 1 000 000: {stats.band_sum(1_000_000)*1e-9:5.0f} mrd.")


def plot_wealth_stats(axs, stats):
    n = 25

    axs[0].plot(stats.xp[:n] / 1e3, stats.yp[:n] / 1e3, linewidth = 1, marker = ".")
    axs[0].set_xlabel("Kotitalous (1 000)")
    axs[0].set_ylabel("Nettovarallisuus (t. eur)")
    axs[0].autoscale(enable=True, axis="x", tight=True)
    axs[0].grid()

    axs[1].plot(stats.xp[n:] / 1e3, stats.yp[n:] / 1e6, linewidth = 1, marker = ".")
    axs[1].set_xlabel("Kotitalous (1 000)")
    axs[1].set_ylabel("Nettovarallisuus (milj. eur)")
    axs[1].autoscale(enable=True, axis="x", tight=True)
    axs[1].grid()


def report_wealth_tax(tax):
    print("--------------------------------------------------------")
    print("  alaraja ..   yläraja  vero      kertymä      veropohja")
    print("--------------------------------------------------------")
    for (r, a, b), t, s in zip(tax.iter_brackets(), tax.revenue, tax.sum):
        if b is None:
            print(f"{a:>9,} ..           {r:>5.2f}% {t*1e-9:>7.2f} mrd. {s*1e-9:>9.2f} mrd.")
        else:
            print(f"{a:>9,} .. {b:>9,} {r:>5.2f}% {t*1e-9:>7.2f} mrd. {s*1e-9:>9.2f} mrd.")
    print(f"Yhteensä: {tax.total_revenue*1e-9:.2f} mrd.")
