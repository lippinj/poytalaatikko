import statfin
import numpy as np


class DataVtutk151u:
    ABBR_VLAJI = {
        "net": "nettoae_DN3001",    # Nettovarallisuus
        "net2": "nettoae_DN3001_2", # Nettovarallisuus (pl. säästö- ja sijoitusvakuutukset ja kryptovaluutat)
        "net3": "nettoae_suppea",   # Nettovarallisuus (pl. metsät, pellot, yritysvarallisuus, säästö- ja sijoitusvakuutukset ja kryptovaluutat)
        "rvar": "realvar2",         # Reaalivarat (1-3)
        "rvar2": "realvar",         # Reaalivarat (1-2, pl. metsät, pellot ja yritysvarallisuus)
        "fvar": "finan",            # Rahoitusvarat (4-9)
    }

    ABBR_COL = {
        "me_n": "vtutk_keskiarvo_n",
        "md_n": "vtutk_mediaani_n",
        "me_r": "vtutk_keskiarvo_r",
        "md_r": "vtutk_mediaani_r",
        "sz": "vtutk_kotitalouksia_keskikoko",  # Kotitalouden keskikoko
        "N": "vtutk_kotitalouksia_perusjoukko", # Kotitalouksia perusjoukossa
    }

    TABLE_NAME = "statfin_vtutk_pxt_151u"
    
    def __init__(self):
        self.db = statfin.PxWebAPI.StatFin()
        self.table = self.db.table("StatFin", f"{self.TABLE_NAME}.px")
        self.df = self.table.query({"Tulokymmenys": "*"}, self.TABLE_NAME)

    def __call__(self, vuosi, tkym, vlaji, col):
        vlaji = self.ABBR_VLAJI.get(vlaji, vlaji)
        col = self.ABBR_COL.get(col, col)

        if tkym == "D1-5":
            return self.aggregate(1, 5, vuosi, vlaji, col)

        if str(tkym).startswith("D"):
            tkym = int(tkym[1:])

        df = self.df
        df = df[df.Vuosi == str(vuosi)]
        df = df[df.Tulokymmenys == str(tkym)]
        df = df[df.Varallisuuslaji == vlaji]
        return df.iloc[0][col]

    def aggregate(self, i, j, vuosi, vlaji, col):
        if col.endswith("joukko"):
            return self.sum(i, j, vuosi, vlaji, col)
        else:
            return self.mean(i, j, vuosi, vlaji, col)

    def mean(self, i, j, vuosi, vlaji, col):
        x = np.array([self(vuosi, k, vlaji, col) for k in range(i, j+1)])
        w = np.array([self(vuosi, k, vlaji, "N") for k in range(i, j+1)])
        return np.dot(x, w) / w.sum()

    def sum(self, i, j, vuosi, vlaji, col):
        return np.sum([self(vuosi, k, vlaji, col) for k in range(i, j+1)])

    @property
    def years(self):
        return np.array(sorted([int(x) for x in list(self.df.Vuosi.unique())]))

    @property
    def classes(self):
        return [f"D{i}" for i in range(1, 11)]

    @property
    def classes2(self):
        return ["D1-5", "D6", "D7", "D8", "D9", "D10"]

    def by_year(self, *args, **kwargs):
        return np.array([self(y, *args, **kwargs) for y in self.years])

    def by_decile(self, year, *args, **kwargs):
        return np.array([self(year, d, *args, **kwargs) for d in range(1, 11)])