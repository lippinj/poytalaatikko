import datetime

import numpy as np
import pandas as pd

import statfin


StatFin = statfin.StatFin()

PALKKIOT = pd.read_csv("palkkiot.csv", parse_dates=["alkaen"], date_format="%Y-%m-%d")
ANSIOTASOINDEKSI = StatFin.StatFin.ati._11zt.query()()
BKT_PER_CAPITA = StatFin.StatFin.vtp._123x.query(Taloustoimi="B1GMH")()
AK_TULOT = StatFin.StatFin.tjt._128c.query()()
KHI = StatFin.StatFin.khi.xq.query(Hyödyke=0, Indeksisarja="0_2000")()


def _extend_time(df):
    t = []
    for _, row in df.iterrows():
        if len(t) > 0:
            t.append(row.alkaen - datetime.timedelta(days=1))
        t.append(row.alkaen)
    t.append(datetime.datetime.now())
    return np.array(t)


def _deflate(tt, src):
    dst = []
    for t, x in zip(tt, src):
        y = t.year
        k = KHI[KHI.Kuukausi.dt.year == y].pisteluku.to_numpy().mean()
        dst.append(x * k)
    return np.array(dst)


def ind(x):
    return 100 * x / x[0]


def palkkiot():
    df = PALKKIOT
    t = _extend_time(df)
    x1 = np.repeat(df.ked.to_numpy(), 2)
    x2 = np.repeat(df.ked4.to_numpy(), 2)
    x3 = np.repeat(df.ked12.to_numpy(), 2)
    return t, x1, x2, x3


def ati():
    df = ANSIOTASOINDEKSI
    df = df[df.Vuosineljännes >= datetime.datetime(2001, 1, 1)]
    t = df.Vuosineljännes.to_numpy()
    x = df.ati_1964_100.to_numpy()
    return t, x


def bkt_per_capita():
    df = BKT_PER_CAPITA
    df = df[df.Vuosi >= datetime.datetime(2001, 1, 1)]
    t = df.Vuosi.to_numpy()
    x = df.cp_eur.to_numpy()
    return t, x


def tulot():
    df = AK_TULOT
    df = df[df.Vuosi >= datetime.datetime(2001, 1, 1)]
    t = df[df.Tulokymmenys == "SS"].Vuosi
    x1 = df[df.Tulokymmenys == "SS"].ekvikturaha_med.to_numpy()
    x2 = df[df.Tulokymmenys == "1"].ekvikturaha_mean.to_numpy()
    return t, _deflate(t, x1), _deflate(t, x2)


def plot_ati(ax):
    t, x = ati()
    ax.plot(t, ind(x), color="firebrick", label="Ansiotasoindeksi")


def plot_tulot(ax):
    t, x1, x2 = tulot()
    ax.plot(t, ind(x1), color="navy", label="Käytettävissä olevat tulot, mediaani")
    ax.plot(t, ind(x2), color="royalblue", label="Käytettävissä olevat tulot, pienituloisin 10%, keskiarvo")


def plot_bkt_per_capita(ax):
    t, x = bkt_per_capita()
    ax.plot(t, ind(x), color="forestgreen", label="BKT henkeä kohti")


def plot_palkkiot(ax):
    t, x1, x2, x3 = palkkiot()
    ax.plot(t, ind(x1), color="black", linestyle="-", label="Kansanedustajan palkkio, alle 4 vuotta")
    ax.plot(t, ind(x2), color="black", linestyle="--", label="Kansanedustajan. palkkio, 4-12 vuotta")
    ax.plot(t, ind(x3), color="black", linestyle=":", label="Kansanedustajan. palkkio, yli 12 vuotta")
