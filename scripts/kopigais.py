"""Shared helpers used by the analysis, chart and web page scripts."""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
DOCS = ROOT / "docs"

GROUP_ORDER = ["Baltijas valstis", "Ziemeļvalstis", "Centrāleiropa", "Rietumeiropa",
               "Dienvideiropa", "Dienvidaustrumeiropa", "Austrumeiropa"]
BALTICS = ["EST", "LVA", "LTU"]
# Countries at war (or a party to it) are left out of rankings and averages so they don't distort the scale.
WAR = {"UKR", "RUS", "BLR"}
# Iceland has no armed forces (its military spending is reported as zero), so it is left out of rankings too.
EXCLUDE = WAR | {"ISL"}
SOURCE_WB = "Avots: Pasaules Banka (SIPRI dati), autora aprēķini"
SOURCE_ES = "Avots: Eurostat (gov_10a_exp, COFOG GF02), autora aprēķini"


def load():
    df = pd.read_csv(PROCESSED / "dati.csv")
    return df


def latest_year(df, col="mil_gdp"):
    """Most recent year for which at least 3/4 of EU countries have data."""
    eu = df[df["es"] == 1]
    counts = eu.dropna(subset=[col]).groupby("year")["iso3"].nunique()
    ok = counts[counts >= 0.75 * eu["iso3"].nunique()]
    return int(ok.index.max())


def periods(latest):
    return [(2000, 2013, "2000–2013"), (2014, 2021, "2014–2021"), (2022, latest, f"2022–{latest}")]


def eu_weighted(df, num="mil_usd", den="gdp_usd"):
    """EU-27 total military spending as % of EU-27 total GDP, per year (countries with both values)."""
    eu = df[(df["es"] == 1)].dropna(subset=[num, den])
    g = eu.groupby("year")[[num, den]].sum()
    return (g[num] / g[den] * 100).rename("ES-27")


def lv(x, d=1):
    """Latvian number format: decimal comma, space as thousands separator."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "–"
    s = f"{x:,.{d}f}"
    return s.replace(",", " ").replace(".", ",").replace("-", "−")
