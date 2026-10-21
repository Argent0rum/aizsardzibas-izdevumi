"""Step 4 — charts for the paper (Latvian labels, decimal comma).

Saves PNG files (200 dpi, ready to paste into Word) to docs/grafiki/.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
import numpy as np
import pandas as pd

from kopigais import BALTICS, DOCS, GROUP_ORDER, SOURCE_ES, SOURCE_WB, WAR, eu_weighted, latest_year, load, lv

OUT = DOCS / "grafiki"
COL = {"LVA": "#9E3039", "LTU": "#D99A00", "EST": "#2a78d6", "EU": "#30343B", "OTHER": "#B9C1CC", "TARGET": "#C0392B"}
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10.5, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#E3E6EA", "grid.linewidth": 0.8, "axes.axisbelow": True,
    "axes.edgecolor": "#9AA3AE", "axes.titleweight": "bold", "axes.titlesize": 13, "axes.titlelocation": "left",
    "figure.dpi": 100, "savefig.dpi": 200, "savefig.bbox": "tight", "legend.frameon": False,
})
comma = lambda d: FuncFormatter(lambda v, _: lv(v, d))
SAVED = []


def finish(fig, ax, name, title, subtitle, source=SOURCE_WB):
    ax.set_title(title, pad=24)
    ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=9.5, color="#555B63", va="bottom")
    fig.text(0.01, -0.01, source, fontsize=8.5, color="#6B7280", ha="left", va="top")
    fig.savefig(OUT / f"{name}.png", facecolor="white")
    plt.close(fig)
    SAVED.append(name)
    print(f"  {name}.png")


def mark_events(ax, last):
    for yr, label in [(2014, "2014: Krimas aneksija"), (2022, "2022: Krievijas iebrukums Ukrainā")]:
        if yr <= last:
            ax.axvline(yr, color="#8A9099", lw=1, ls=":", zorder=1)
            ax.text(yr + 0.2, ax.get_ylim()[1] * 0.98, label, fontsize=8.5, color="#5B616A", va="top")


def target_line(ax, horizontal=True):
    (ax.axhline if horizontal else ax.axvline)(2, color=COL["TARGET"], lw=1.2, ls="--", zorder=2)


def chart_baltics_vs_eu(df, last):
    fig, ax = plt.subplots(figsize=(9, 5))
    names = df.drop_duplicates("iso3").set_index("iso3")["valsts"]
    for iso in BALTICS:
        s = df[df["iso3"] == iso].set_index("year")["mil_gdp"].loc[2000:last]
        ax.plot(s.index, s.values, color=COL[iso], lw=2.6, label=names[iso])
        ax.text(s.index[-1] + 0.3, s.values[-1], lv(s.values[-1], 2), color=COL[iso], va="center", fontsize=9, fontweight="bold")
    eu = eu_weighted(df).loc[2000:last]
    ax.plot(eu.index, eu.values, color=COL["EU"], lw=2, ls="-", label="ES-27 (svērtais vidējais)")
    ax.text(eu.index[-1] + 0.3, eu.values[-1], lv(eu.values[-1], 2), color=COL["EU"], va="center", fontsize=9)
    ax.set_ylim(0, max(4, np.nanmax(df[df["iso3"].isin(BALTICS) & (df["year"] <= last)]["mil_gdp"]) * 1.15))
    target_line(ax)
    ax.text(2000.2, 2.05, "NATO 2 % mērķis", color=COL["TARGET"], fontsize=8.5, va="bottom")
    mark_events(ax, last)
    ax.set_xlim(2000, last + 1.6)
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.yaxis.set_major_formatter(comma(1))
    ax.set_ylabel("% no IKP")
    ax.legend(loc="upper left", bbox_to_anchor=(0, 0.9), ncol=1)
    finish(fig, ax, "01_baltija_pret_es", "Baltijas valstu aizsardzības izdevumi salīdzinājumā ar ES",
           f"Militārie izdevumi, % no IKP, 2000–{last}")


def bar_chart(df, col, last, name, title, subtitle, digits=1, target=False, xlabel="", diverging=False):
    d = df.drop(index=[i for i in WAR if i in df.index]).dropna(subset=[col]).sort_values(col)
    fig, ax = plt.subplots(figsize=(9, max(6, len(d) * 0.24)))
    colors = [COL[i] if i in BALTICS else (COL["EU"] if i == "EU" else COL["OTHER"]) for i in d.index]
    ax.barh(d["valsts"], d[col], color=colors, height=0.72)
    for y, (v, iso) in enumerate(zip(d[col], d.index)):
        ax.text(v + (abs(d[col]).max() * 0.01) * (1 if v >= 0 else -1), y, lv(v, digits), va="center", ha="left" if v >= 0 else "right",
                fontsize=8, color="#30343B", fontweight="bold" if iso in BALTICS or iso == "EU" else "normal")
    for lab in ax.get_yticklabels():
        if lab.get_text() in [df.loc[i, "valsts"] for i in BALTICS if i in df.index] or lab.get_text().startswith("ES-27"):
            lab.set_fontweight("bold")
    if target:
        target_line(ax, horizontal=False)
        ax.text(2.03, len(d) - 0.35, "NATO 2 % mērķis", color=COL["TARGET"], fontsize=8.5, va="bottom")
    if diverging:
        ax.axvline(0, color="#30343B", lw=0.8)
    ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(comma(0 if digits == 0 else 1))
    ax.set_xlabel(xlabel)
    ax.margins(y=0.01)
    ax.set_xlim(min(0, d[col].min() * 1.15), d[col].max() * 1.12)
    finish(fig, ax, name, title, subtitle)


def chart_regions(df, last):
    d = df[~df["iso3"].isin(WAR) & (df["year"] <= last)]
    t = d.pivot_table(index="year", columns="grupa", values="mil_gdp", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(9, 5))
    palette = ["#9E3039", "#2a78d6", "#1baf7a", "#6250d6", "#eb6834", "#D99A00"]
    for g, c in zip([g for g in GROUP_ORDER if g != "Austrumeiropa" and g in t.columns], palette):
        s = t[g].loc[2000:last]
        ax.plot(s.index, s.values, lw=2.8 if g == "Baltijas valstis" else 1.8, color=c, label=g)
    eu = eu_weighted(df).loc[2000:last]
    ax.plot(eu.index, eu.values, color=COL["EU"], lw=1.6, ls="--", label="ES-27 (svērtais)")
    ax.set_ylim(0, None)
    target_line(ax)
    mark_events(ax, last)
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.yaxis.set_major_formatter(comma(1))
    ax.set_ylabel("% no IKP")
    ax.legend(ncol=3, loc="upper left", bbox_to_anchor=(0, 0.92), fontsize=9)
    finish(fig, ax, "04_regionu_videjie", "Aizsardzības izdevumi Eiropas reģionos",
           f"Reģiona valstu vienkāršais vidējais, % no IKP, 2000–{last} (bez Ukrainas, Krievijas, Baltkrievijas)")


def chart_real_index(df, last):
    fig, ax = plt.subplots(figsize=(9, 5))
    names = df.drop_duplicates("iso3").set_index("iso3")["valsts"]
    for iso in BALTICS:
        s = df[df["iso3"] == iso].set_index("year")["mil_real_usd_2015"].loc[2010:last]
        if 2014 in s and s[2014]:
            s = s / s[2014] * 100
            ax.plot(s.index, s.values, color=COL[iso], lw=2.6, label=names[iso])
            ax.text(s.index[-1] + 0.2, s.values[-1], lv(s.values[-1], 0), color=COL[iso], va="center", fontsize=9, fontweight="bold")
    eu = df[df["es"] == 1].dropna(subset=["mil_real_usd_2015"]).groupby("year")["mil_real_usd_2015"].sum().loc[2010:last]
    if 2014 in eu:
        eu = eu / eu[2014] * 100
        ax.plot(eu.index, eu.values, color=COL["EU"], lw=2, label="ES-27 kopā")
        ax.text(eu.index[-1] + 0.2, eu.values[-1], lv(eu.values[-1], 0), color=COL["EU"], va="center", fontsize=9)
    ax.axhline(100, color="#30343B", lw=0.8)
    mark_events(ax, last)
    ax.set_xlim(2010, last + 1.2)
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.yaxis.set_major_formatter(comma(0))
    ax.set_ylabel("Indekss, 2014 = 100")
    ax.legend(loc="upper left", bbox_to_anchor=(0, 0.9))
    finish(fig, ax, "05_realie_izdevumi_indekss", "Reālo aizsardzības izdevumu pieaugums kopš 2014. gada",
           f"Izdevumi salīdzināmajās (2015. gada) cenās, indekss 2014 = 100, 2010–{last}",
           SOURCE_WB + "; reālie izdevumi = % no IKP × IKP 2015. g. cenās")


def chart_growth_scatter(df, last):
    d = df[~df["iso3"].isin(WAR) & df["year"].between(2000, last)]
    g = d.groupby(["iso3", "valsts"]).agg(mil=("mil_gdp", "mean"), gr=("gdp_growth", "mean")).dropna().reset_index()
    r = g["mil"].corr(g["gr"])
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(g["mil"], g["gr"], s=34, color=[COL.get(i, COL["OTHER"]) if i in BALTICS else "#7E8794" for i in g["iso3"]], zorder=3)
    for _, row in g.iterrows():
        ax.annotate(row["valsts"], (row["mil"], row["gr"]), xytext=(4, 3), textcoords="offset points", fontsize=7.5,
                    color=COL[row["iso3"]] if row["iso3"] in BALTICS else "#4B5058", fontweight="bold" if row["iso3"] in BALTICS else "normal")
    k, b = np.polyfit(g["mil"], g["gr"], 1)
    xs = np.linspace(g["mil"].min(), g["mil"].max(), 50)
    ax.plot(xs, k * xs + b, color=COL["TARGET"], lw=1.2, ls="--")
    ax.text(0.98, 0.04, f"Pīrsona r = {lv(r, 2)}", transform=ax.transAxes, ha="right", fontsize=10)
    ax.xaxis.set_major_formatter(comma(1)); ax.yaxis.set_major_formatter(comma(1))
    ax.set_xlabel(f"Vidējie aizsardzības izdevumi, % no IKP (2000–{last})")
    ax.set_ylabel("Vidējā reālā IKP izaugsme, % gadā")
    finish(fig, ax, "06_izdevumi_un_izaugsme", "Aizsardzības izdevumi un ekonomiskā izaugsme",
           "Katrs punkts ir viena valsts. Aprakstoša sakarība, nevis cēloņsakarība.")


def chart_sources(df, last):
    s = df[df["iso3"] == "LVA"].set_index("year")
    if s["es_cofog_gdp"].notna().sum() < 5:
        return
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.plot(s.index, s["mil_gdp"], color=COL["LVA"], lw=2.4, label="SIPRI (Pasaules Banka)")
    ax.plot(s.index, s["es_cofog_gdp"], color=COL["EU"], lw=2, ls="--", label="Eurostat COFOG (GF02)")
    ax.set_xlim(2000, max(last, s["es_cofog_gdp"].last_valid_index() or last))
    ax.set_ylim(0, None)
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.yaxis.set_major_formatter(comma(1))
    ax.set_ylabel("% no IKP")
    ax.legend(loc="upper left")
    finish(fig, ax, "08_latvija_divi_avoti", "Latvijas aizsardzības izdevumi pēc diviem datu avotiem",
           "Definīcijas atšķiras: SIPRI ietver, piem., militārās pensijas; COFOG seko valdības finanšu statistikai",
           "Avoti: Pasaules Banka (SIPRI), Eurostat (gov_10a_exp); autora aprēķini")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = load()
    last = latest_year(df)
    print("Charts:")
    chart_baltics_vs_eu(df, last)
    latest = df[df["year"] == last].set_index("iso3")
    eu_row = pd.DataFrame({"valsts": ["ES-27 (svērtais vidējais)"], "mil_gdp": [eu_weighted(df).get(last)]}, index=["EU"])
    bar_chart(pd.concat([latest[["valsts", "mil_gdp"]], eu_row]), "mil_gdp", last, f"02_valstu_salidzinajums_{last}",
              f"Aizsardzības izdevumi Eiropas valstīs {last}. gadā", "% no IKP (bez Ukrainas, Krievijas, Baltkrievijas)", 2, target=True, xlabel="% no IKP")
    y14 = df[df["year"] == 2014].set_index("iso3")["mil_gdp"]
    ch = latest[["valsts"]].assign(change=latest["mil_gdp"] - y14)
    bar_chart(ch, "change", last, "03_izmaina_kops_2014", f"Aizsardzības izdevumu izmaiņa no 2014. līdz {last}. gadam",
              "Izmaiņa procentpunktos (% no IKP)", 2, xlabel="procentpunkti", diverging=True)
    chart_regions(df, last)
    chart_real_index(df, last)
    chart_growth_scatter(df, last)
    bar_chart(latest[["valsts", "mil_per_person_usd"]], "mil_per_person_usd", last, f"07_uz_iedzivotaju_{last}",
              f"Aizsardzības izdevumi uz vienu iedzīvotāju {last}. gadā", "ASV dolāri faktiskajās cenās", 0, xlabel="USD uz iedzīvotāju")
    chart_sources(df, last)
    (DOCS / "grafiki" / "_saraksts.txt").write_text("\n".join(SAVED))


if __name__ == "__main__":
    main()
