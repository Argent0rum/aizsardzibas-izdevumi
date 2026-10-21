"""Step 1 — download the raw data.

Downloads defence spending and GDP figures for every country in config/valstis.csv
from two free public sources and saves them unchanged in data/raw/:

  * World Bank Open Data API — military expenditure (its source is SIPRI), GDP, population
  * Eurostat — government spending on defence by function (COFOG code GF02)

Nothing is calculated here; that happens in apstrade.py. Keeping the raw files means
you can always check exactly what the sources said on the day of download.
"""
import json
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
START_YEAR = 2000

# World Bank indicator codes (see https://data.worldbank.org)
WB_INDICATORS = {
    "MS.MIL.XPND.GD.ZS": "Military expenditure (% of GDP)",
    "MS.MIL.XPND.ZS": "Military expenditure (% of general government expenditure)",
    "MS.MIL.XPND.CD": "Military expenditure (current US$)",
    "NY.GDP.MKTP.CD": "GDP (current US$)",
    "NY.GDP.MKTP.KD": "GDP (constant 2015 US$)",
    "NY.GDP.MKTP.KD.ZG": "GDP growth (annual %)",
    "SP.POP.TOTL": "Population, total",
}

EUROSTAT_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/gov_10a_exp"
    "?format=JSON&lang=EN&sector=S13&cofog99=GF02&na_item=TE"
    "&unit=PC_GDP&unit=PC_TOT&unit=MIO_EUR&sinceTimePeriod={start}"
)


def get(url, tries=4):
    """Download a URL, retrying a few times if the server is busy."""
    for attempt in range(1, tries + 1):
        try:
            r = requests.get(url, timeout=60, headers={"User-Agent": "aizsardzibas-izdevumi (student project)"})
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            if attempt == tries:
                raise
            print(f"  retry {attempt} after error: {e}")
            time.sleep(3 * attempt)


def download_world_bank(countries):
    codes = ";".join(countries["iso3"])
    for code, name in WB_INDICATORS.items():
        url = (f"https://api.worldbank.org/v2/country/{codes}/indicator/{code}"
               f"?date={START_YEAR}:2030&format=json&per_page=20000")
        print(f"World Bank: {name}")
        data = get(url).json()
        if not isinstance(data, list) or len(data) < 2 or data[1] is None:
            raise RuntimeError(f"Unexpected World Bank answer for {code}: {str(data)[:300]}")
        (RAW / f"worldbank_{code}.json").write_text(json.dumps(data, ensure_ascii=False))
        print(f"  {len(data[1])} rows")


def download_eurostat():
    print("Eurostat: general government expenditure on defence (COFOG GF02)")
    data = get(EUROSTAT_URL.format(start=START_YEAR)).json()
    if "value" not in data:
        raise RuntimeError(f"Unexpected Eurostat answer: {str(data)[:300]}")
    (RAW / "eurostat_gov_10a_exp_GF02.json").write_text(json.dumps(data, ensure_ascii=False))
    print(f"  {len(data['value'])} values")


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    countries = pd.read_csv(ROOT / "config" / "valstis.csv")
    download_world_bank(countries)
    try:
        download_eurostat()
    except Exception as e:  # Eurostat is a second opinion; carry on without it if it fails
        print(f"Eurostat download failed, continuing without it: {e}")
    (RAW / "lejupielades_datums.txt").write_text(time.strftime("%Y-%m-%d"))


if __name__ == "__main__":
    main()
