import io
import requests
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw
from matplotlib.offsetbox import OffsetImage, AnnotationBbox


# From: Labour force participation rate
DF_EM = pd.read_csv("data/participation-rate.csv")

# From: Infra-annual labour statistics
DF_UE = pd.read_csv("data/unemployment-rate.csv")

# From: Incidence of full-time and part-time employment based on OECD-harmonized definition
DF_PT = pd.read_csv("data/part-time.csv")

REGION_CODE_TO_ISO = {
    "aus": "au",
    "fin": "fi",
    "swe": "se",
    "nor": "no",
    "est": "ee",
    "lva": "lv",
    "ltu": "lt",
    "hun": "hu",
    "cze": "cz",
    "pol": "pl",
    "aut": "at",
    "deu": "de",
    "fin": "fi",
    "fra": "fr",
    "grc": "gr",
    "hun": "hu",
    "irl": "ie",
    "ita": "it",
    "nld": "nl",
    "bel": "be",
    "che": "ch",
    "tur": "tr",
    "dnk": "dk",
    "svk": "sk",
    "svn": "si",
    "esp": "es",
    "isl": "is",
    "hun": "hu",
    "cze": "cz",
    "pol": "pl",
    "lux": "lu",
    "prt": "pt",
    "bgr": "bg",
    "can": "ca",
    "chl": "cl",
    "col": "co",
    "hrv": "hr",
    "cyp": "cy",
    "hrv": "hr",
    "hun": "hu",
    "tur": "tr",
    "ukr": "ua",
    "usa": "us",
    "gbr": "gb",
    "isr": "il",
    "jpn": "jp",
    "kor": "kr",
    "mex": "mx",
    "nzl": "nz",
    "rus": "ru",
    "zaf": "za",
}

IMAGE_HEIGHT = 240


def get_regions():
    r = (set(DF_EM.REF_AREA.unique()) & set(DF_UE.REF_AREA.unique()) & set(DF_PT.REF_AREA.unique()))
    r.remove("ZAF")
    r.remove("OECD")
    return r


def get_data(df0, regions, year):
    arr = []
    for region in regions:
        df = df0
        df = df[df.REF_AREA == region]
        df = df[df.TIME_PERIOD == year]
        arr.append(df.OBS_VALUE.iloc[0])
    return np.array(arr)


def get_unemployment_rate(regions, year):
    return get_data(DF_UE, regions, year)


def get_employment_rate(regions, year):
    return get_data(DF_EM, regions, year)


def get_part_time_rate(regions, year):
    df = DF_PT
    df = df[df.WORK_TIME_ARNGMNT == "PT"]
    return get_data(df, regions, year)


def get_flag_image_raw(iso_code):
    local = f"data/flags/{iso_code}.png"
    url = f"https://flagcdn.com/h{IMAGE_HEIGHT}/{iso_code}.png"
    try:
        im = Image.open(local)
    except FileNotFoundError:
        response = requests.get(url)
        response.raise_for_status()
        with open(local, "wb") as f:
            f.write(response.content)
        im = Image.open(io.BytesIO(response.content))
    im = im.convert("RGBA")
    return im


def get_flag_image_badge(iso_code):
    raw = get_flag_image_raw(iso_code)
    avg_color = raw.resize((1, 1)).getpixel((0, 0))

    im = raw.resize((IMAGE_HEIGHT, IMAGE_HEIGHT), Image.Resampling.LANCZOS)

    mask = Image.new("L", (IMAGE_HEIGHT, IMAGE_HEIGHT), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, IMAGE_HEIGHT, IMAGE_HEIGHT), fill=255)

    jm = Image.new("RGBA", (IMAGE_HEIGHT, IMAGE_HEIGHT), (255, 255, 255, 0))
    jm.paste(im, (0, 0), mask)

    border_width = IMAGE_HEIGHT // 10
    bigger_width = IMAGE_HEIGHT + 2 * border_width
    km = Image.new("RGBA", (bigger_width, bigger_width), (255, 255, 255, 0))
    ImageDraw.Draw(km).ellipse((0, 0, bigger_width, bigger_width), fill=(128, 128, 128))
    km.paste(jm, (border_width, border_width), jm)

    return km.resize((30, 30), Image.Resampling.LANCZOS)


def place_country_point(ax, region_code, xy, xytext, size=20):
    iso_code = REGION_CODE_TO_ISO[region_code.lower()]
    im = get_flag_image_badge(iso_code)
    zoom = size / im.size[0]
    imagebox = OffsetImage(im, zoom=zoom)
    ab = AnnotationBbox(imagebox, xy, frameon=False)
    ax.add_artist(ab)
    ax.annotate(
        iso_code.upper(),
        xy,
        xytext=xytext,
        textcoords="offset points",
        ha="center",
        va="center",
        fontsize=9,
        family="sans-serif",
    )
