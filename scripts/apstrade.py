"""Step 2 — clean and combine the raw data into one table.

Reads the files saved by lejupielade.py and builds data/processed/dati.csv:
one row per country and year, one column per measure. Also works out a few
derived measures (spending per person, spending in constant prices).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"

# World Bank code -> short column name used in the rest of the project
WB_COLUMNS = {
    "MS.MIL.XPND.GD.ZS": "mil_gdp",        # military spending, % of GDP
    "MS.MIL.XPND.ZS": "mil_gov",           # military spending, % of government spending
    "MS.MIL.XPND.CD": "mil_usd",           # military spending, current US$
    "NY.GDP.MKTP.CD": "gdp_usd",           # GDP, current US$
    "NY.GDP.MKTP.KD": "gdp_usd_2015",      # GDP, constant 2015 US$
    "NY.GDP.MKTP.KD.ZG": "gdp_growth",     # real GDP growth, %
    "SP.POP.TOTL": "population",
}
EUROSTAT_UNITS = {"PC_GDP": "es_cofog_gdp", "PC_TOT": "es_cofog_tot", "MIO_EUR": "es_cofog_meur"}


def read_world_bank():
    frames = []
    for code, col in WB_COLUMNS.items():
        rows = json.loads((RAW / f"worldbank_{code}.json").read_text())[1] or []
        df = pd.DataFrame({"iso3": [r["countryiso3code"] for r in rows],
                           "year": [int(r["date"]) for r in rows],
                           col: [r["value"] for r in rows]})
        frames.append(df.set_index(["iso3", "year"]))
    return pd.concat(frames, axis=1).reset_index()


def parse_jsonstat(d):
    """Turn a Eurostat JSON-stat answer into a flat table (one row per value)."""
    ids, sizes = d["id"], d["size"]
    labels = []
    for dim in ids:
        idx = d["dimension"][dim]["category"]["index"]
        if isinstance(idx, list):
            labels.append(idx)
        else:
            pos = [None] * len(idx)
            for code, i in idx.items():
                pos[i] = code
            labels.append(pos)
    strides = [int(np.prod(sizes[k + 1:])) for k in range(len(sizes))]
    rows = []
    for flat, val in d["value"].items():
        flat = int(flat)
        rows.append({dim: labels[k][(flat // strides[k]) % sizes[k]] for k, dim in enumerate(ids)} | {"value": val})
    return pd.DataFrame(rows)


def read_eurostat(countries):
    path = RAW / "eurostat_gov_10a_exp_GF02.json"
    if not path.exists():
        return None
    df = parse_jsonstat(json.loads(path.read_text()))
    if df.empty:
        return None
    to_iso3 = dict(zip(countries["eurostat"], countries["iso3"]))
    df = df[df["geo"].isin(to_iso3)].copy()
    df["iso3"] = df["geo"].map(to_iso3)
    df["year"] = df["time"].astype(int)
    df["col"] = df["unit"].map(EUROSTAT_UNITS)
    return df.pivot_table(index=["iso3", "year"], columns="col", values="value").reset_index()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    countries = pd.read_csv(ROOT / "config" / "valstis.csv")
    df = read_world_bank()
    es = read_eurostat(countries)
    if es is not None:
        df = df.merge(es, on=["iso3", "year"], how="left")
    for c in EUROSTAT_UNITS.values():
        if c not in df:
            df[c] = np.nan

    # derived measures
    df["mil_per_person_usd"] = df["mil_usd"] / df["population"]                 # current US$ per person
    df["mil_real_usd_2015"] = df["mil_gdp"] / 100 * df["gdp_usd_2015"]          # constant 2015 US$

    df = df.merge(countries, on="iso3", how="left")
    df["nato"] = (df["nato_gads"].notna() & (df["year"] >= df["nato_gads"].fillna(9999))).astype(int)
    df = df.sort_values(["grupa", "valsts", "year"])
    df.to_csv(OUT / "dati.csv", index=False)
    print(f"Saved {len(df)} rows, years {df['year'].min()}–{df['year'].max()}, to data/processed/dati.csv")


if __name__ == "__main__":
    main()
