import statfin
import numpy as np


_TABLE = "statfin_vtutk_pxt_151v"

_VARALLISUUSLAJI = {
    "n": "nettoae_DN3001",  # Nettovarallisuus
    "n2": "nettoae_DN3001_2",  # Nettovarallisuus (pl. säästö- ja sijoitusvakuutukset ja kryptovaluutat)
    "n3": "nettoae_suppea",  # Nettovarallisuus (pl. metsät, pellot, yritysvarallisuus, säästö- ja sijoitusvakuutukset ja kryptovaluutat)
    "g": "bruttoae_DA1000",  # Varat yhteensä
    "g2": "bruttoae_DA1000_2",  # Varat yhteensä (pl. säästö- ja sijoitusvakuutukset ja kryptovaluutat)
    "g3": "bruttoae_suppea",  # Varat yhteensä (pl. metsät, pellot, yritysvarallisuus, säästö- ja sijoitusvakuutukset ja kryptovaluutat)
    "vr": "realvar2",  # Reaalivarat (1-3)
    "vr2": "realvar",  # Reaalivarat (1-2, pl. metsät, pellot ja yritysvarallisuus)
    "vf": "finan",  # Rahoitusvarat (4-9)
    "vf2": "finan2",  # Rahoitusvarat (pl. säästö- ja sijoitusvakuutukset ja kryptovaluutat)
    "d": "kturaha",  # Käytettävissä oleva rahatulot
    "a1": "asvara",  # 1. Asuntovarallisuus yhteensä
    "a11": "asarav",  # 1.1 Oma pääasiallinen asunto
    "a12": "vaarvy",  # 1.2 Vapaa-ajan asunnot
    "a13": "asaram",  # 1.3 Muut asunnot
    "a2": "kulku",  # 2. Kulkuvälineet
    "a3": "muurealvar",  # 3. Metsät, pellot ja yritysvarallisuus
    "a4": "talle",  # 4. Talletukset
    "a5": "pymar",  # 5. Pörssiosakkeet ja sijoitusrahastot
    "a51": "sirave",  # 5.1 Sijoitusrahastot
    "a52": "porsosa",  # 5.2 Pörssiosakkeet
    "a6": "muosa",  # 6. Muut osakkeet
    "a7": "elavak",  # 7. Yksilölliset eläkevakuutukset
    "a8": "vaksak",  # 8. Säästö- ja sijoitusvakuutukset
    "a9": "muufinan",  # 9. Muut rahoitusvarat
    "la": "luototy",  # 10. Velat yhteensä
    "la1": "asuntm",  # 10.1 Asuntovelat
    "la1": "muutvelat",  # 10.2 Kulutus- ja muut velat
    "nd": "asarav_netto",  # Oman asunnon nettoarvo (asunnon arvo - asuntovelat)
}

_TIEDOT = {
    "nq1": "vtutk_alakvartiili_n",  # Varallisuuslajin alakvartiili, nimellisissä euroissa
    "nm": "vtutk_keskiarvo_n",  # Varallisuuslajin keskiarvo, nimellisissä euroissa
    "nmed": "vtutk_mediaani_n",  # Varallisuuslajin mediaani, nimellisissä euroissa
    "nq3": "vtutk_ylakvartiili_n",  # Varallisuuslajin yläkvartiili, nimellisissä euroissa
    "rq1": "vtutk_alakvartiili_r",  # Varallisuuslajin alakvartiili, reaalisena (viimeisimmän tilastovuoden hinnoin)
    "rm": "vtutk_keskiarvo_r",  # Varallisuuslajin keskiarvo, reaalisena (viimeisimmän tilastovuoden hinnoin)
    "rmed": "vtutk_mediaani_r",  # Varallisuuslajin mediaani, reaalisena (viimeisimmän tilastovuoden hinnoin)
    "rq3": "vtutk_ylakvartiili_r",  # Varallisuuslajin yläkvartiili, reaalisena (viimeisimmän tilastovuoden hinnoin)
    "hnp": "vtutk_kotitalousomistajia",  # Kotitalouksia, joilla varallisuuslajia
    "hp": "vtutk_kotitalousosuus",  # Varallisuuslajia omistavien kotitalouksien osuus (%)
    "hn": "vtutk_kotitalouksia_perusjoukko",  # Kotitalouksia perusjoukossa
    "hsz": "vtutk_kotitalouksia_keskikoko",  # Kotitalouden keskikoko
    "hns": "vtutk_kotitalouksia_otoskoko",  # Otoskoko
}


def _aggregate_mean(x, w):
    return np.dot(x, w) / np.sum(w)


def _aggregate_sum(x, _):
    return np.sum(x)


def _aggregate_invalid(x, w):
    raise RuntimeError("Not aggregable")


_AGGREGATOR = {
    "vtutk_keskiarvo_n": _aggregate_mean,
    "vtutk_keskiarvo_r": _aggregate_mean,
    "vtutk_kotitalousomistajia": _aggregate_sum,
    "vtutk_kotitalousosuus": _aggregate_mean,
    "vtutk_kotitalouksia_perusjoukko": _aggregate_sum,
    "vtutk_kotitalouksia_keskikoko": _aggregate_mean,
}


class Table151v:
    def __init__(self):
        self.db = statfin.PxWebAPI.StatFin()
        self.table = self.db.table("StatFin", f"{_TABLE}.px")
        self.df = self.table.query({"Nettovarallisuuskymmenys": "*"}, _TABLE)
        self.years = np.array(sorted([int(x) for x in list(self.df.Vuosi.unique())]))

    def expand(self, vuosi, desiili, varallisuuslaji, tieto):
        vuosi = vuosi if vuosi is not None else self.years[-1]
        varallisuuslaji = self.varallisuuslaji(varallisuuslaji)
        tieto = self.tiedot(tieto)
        desiili = self.desiili(desiili)
        return vuosi, desiili, varallisuuslaji, tieto

    def label_varallisuuslaji(self, v):
        v = Table151v.varallisuuslaji(v)
        df = self.table.values["Varallisuuslaji"]
        df = df[df.code == v]
        assert len(df) == 1, v
        return df.iloc[0].text

    @staticmethod
    def varallisuuslaji(v):
        return _VARALLISUUSLAJI.get(v, v)

    @staticmethod
    def tiedot(v):
        return _TIEDOT.get(v, v)

    @staticmethod
    def desiili(v):
        if isinstance(v, int):
            return v
        if v == "SS":
            return v
        if v.startswith("D"):
            v = v[1:]
        v = v.split("-")
        if len(v) == 1:
            return int(v[0])
        else:
            a, b = v
            return int(a), int(b) + 1

    @staticmethod
    def aggregator(t):
        return _AGGREGATOR.get(_TIEDOT.get(t, t), _aggregate_invalid)
