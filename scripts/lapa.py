"""Step 5 — the results web page (docs/index.html), published with GitHub Pages."""
import html
import json

from kopigais import DOCS, PROCESSED, lv

CAPTIONS = {
    "01_baltija_pret_es": "Baltijas valstu aizsardzības izdevumi salīdzinājumā ar ES-27",
    "02_valstu_salidzinajums": "Valstu salīdzinājums jaunākajā gadā",
    "03_izmaina_kops_2014": "Izmaiņa kopš 2014. gada",
    "04_regionu_videjie": "Eiropas reģionu vidējie",
    "05_realie_izdevumi_indekss": "Reālo izdevumu pieaugums kopš 2014. gada",
    "06_izdevumi_un_izaugsme": "Aizsardzības izdevumi un IKP izaugsme",
    "07_uz_iedzivotaju": "Izdevumi uz vienu iedzīvotāju",
    "08_latvija_divi_avoti": "Latvija pēc diviem datu avotiem",
}


def caption(name):
    for k, v in CAPTIONS.items():
        if name.startswith(k):
            return v
    return name


def main():
    f = json.loads((PROCESSED / "kopsavilkums.json").read_text())
    charts = [c for c in (DOCS / "grafiki" / "_saraksts.txt").read_text().split("\n") if c]
    last = f["latest"]
    b = f["baltics"]
    lvd = b["LVA"]
    facts = [
        f"{last}. gadā Latvija aizsardzībai tērēja <b>{lv(lvd['last'], 2)} %</b> no IKP (2014. gadā — {lv(lvd['y2014'], 2)} %, 2000. gadā — {lv(lvd['y2000'], 2)} %).",
        f"Lietuva: <b>{lv(b['LTU']['last'], 2)} %</b>, Igaunija: <b>{lv(b['EST']['last'], 2)} %</b>. "
        f"Starp {f['n_ranked']} Eiropas valstīm (bez Ukrainas, Krievijas, Baltkrievijas un Islandes) Latvija ir {lvd['rank']}. vietā, Lietuva {b['LTU']['rank']}., Igaunija {b['EST']['rank']}.",
        f"ES-27 kopumā (svērtais vidējais): <b>{lv(f['eu_last'], 2)} %</b> no IKP {last}. gadā pret {lv(f['eu_2014'], 2)} % 2014. gadā.",
        f"NATO Eiropas dalībvalstis, kas sasniedz 2 % mērķi: <b>{f['nato_eur_over2_last']} no {f['nato_eur_n_last']}</b> {last}. gadā (2014. gadā — {f['nato_eur_over2_2014']}).",
        "Augstākie izdevumi: " + ", ".join(f"{html.escape(n)} {lv(v, 2)} %" for n, v in f["top3"]) + ".",
    ]
    figs = "\n".join(
        f'<figure><a href="grafiki/{c}.png"><img src="grafiki/{c}.png" alt="{html.escape(caption(c))}" loading="lazy"></a>'
        f'<figcaption><b>{i}.</b> {html.escape(caption(c))} · <a href="grafiki/{c}.png" download>lejupielādēt PNG</a></figcaption></figure>'
        for i, c in enumerate(charts, 1))
    page = f"""<!doctype html>
<html lang="lv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Aizsardzības izdevumi Eiropā 2000–{last}</title>
<style>
:root {{ --ink:#16202B; --muted:#5B6672; --line:#DDE2E8; --bg:#F6F7F9; --card:#fff; --accent:#9E3039; color-scheme: light dark; }}
@media (prefers-color-scheme: dark) {{ :root {{ --ink:#E6EAF0; --muted:#A5AFBC; --line:#2B3440; --bg:#11161C; --card:#18202A; --accent:#E07A86; }} }}
* {{ box-sizing: border-box; }}
body {{ margin:0; font-family: system-ui, -apple-system, "Segoe UI", sans-serif; background:var(--bg); color:var(--ink); line-height:1.55; }}
main {{ max-width: 980px; margin: 0 auto; padding: 32px 18px 60px; }}
h1 {{ font-size: clamp(1.7rem, 4vw, 2.4rem); line-height:1.15; margin: 0 0 8px; letter-spacing:-0.01em; }}
h2 {{ margin: 36px 0 10px; font-size: 1.3rem; }}
.lede {{ color: var(--muted); max-width: 70ch; margin: 0 0 20px; }}
.facts {{ background: var(--card); border:1px solid var(--line); border-left: 4px solid var(--accent); border-radius: 10px; padding: 14px 20px; }}
.facts li {{ margin: 6px 0; }}
.dl {{ display:flex; gap:10px; flex-wrap:wrap; }}
.dl a {{ background: var(--card); border:1px solid var(--line); border-radius: 8px; padding: 10px 14px; text-decoration:none; color: var(--ink); font-weight:600; }}
.dl a:hover {{ border-color: var(--accent); }}
.dl span {{ display:block; font-weight:400; font-size:.85rem; color: var(--muted); }}
figure {{ margin: 0 0 22px; background: #fff; border:1px solid var(--line); border-radius: 10px; padding: 10px; }}
figure img {{ width:100%; height:auto; display:block; }}
figcaption {{ font-size:.9rem; color:#4B5563; padding: 8px 4px 0; }}
a {{ color: var(--accent); }}
.note {{ font-size:.92rem; color: var(--muted); max-width: 75ch; }}
footer {{ margin-top: 40px; font-size: .85rem; color: var(--muted); border-top:1px solid var(--line); padding-top: 14px; }}
</style>
</head>
<body>
<main>
<h1>Aizsardzības izdevumi Eiropā, 2000–{last}</h1>
<p class="lede">Dati, aprēķini un grafiki kursa darbam par aizsardzības izdevumu tendencēm Eiropā, īpaši Baltijas valstīs. Dati tiek lejupielādēti un pārrēķināti automātiski. Pēdējā atjaunināšana: {f['downloaded']}.</p>

<h2>Galvenie skaitļi</h2>
<ul class="facts">{''.join(f'<li>{x}</li>' for x in facts)}</ul>

<h2>Dati</h2>
<div class="dl">
  <a href="dati/aizsardzibas_izdevumi.xlsx">Excel darbgrāmata<span>tabulas pa gadiem, periodu un reģionu vidējie</span></a>
  <a href="dati/dati_visi.csv">Visi dati (CSV)<span>viena rinda katrai valstij un gadam</span></a>
</div>

<h2>Grafiki</h2>
{figs}

<h2>Metodoloģija</h2>
<p class="note">Galvenais avots ir Pasaules Bankas datubāze, kuras militāro izdevumu dati nāk no Stokholmas Starptautiskā miera pētniecības institūta (SIPRI). SIPRI definīcija ietver bruņoto spēku, aizsardzības ministrijas, miera uzturēšanas spēku un paramilitāro vienību izdevumus, kā arī militārās pensijas. Salīdzinājumam izmantoti Eurostat valdības izdevumi pēc funkcijām (COFOG GF02 „Aizsardzība”), kuru definīcija ir šaurāka, tāpēc skaitļi var atšķirties. Reālie izdevumi aprēķināti kā izdevumu daļa no IKP, reizināta ar IKP 2015. gada cenās. ES-27 svērtais vidējais ir visu dalībvalstu kopējie izdevumi, dalīti ar kopējo IKP. Ukraina, Krievija un Baltkrievija ir datos, bet nav iekļautas reitingos un vidējos rādītājos, jo kara ietekme izkropļotu salīdzinājumu. Arī Islande nav reitingos, jo tai nav bruņoto spēku.</p>
<p class="note">Korelācija starp izdevumiem un izaugsmi ir aprakstoša: tā neparāda, vai aizsardzības izdevumi ietekmē izaugsmi.</p>

<footer>Avoti: <a href="https://data.worldbank.org/indicator/MS.MIL.XPND.GD.ZS">Pasaules Banka / SIPRI</a>, <a href="https://ec.europa.eu/eurostat/databrowser/view/gov_10a_exp/default/table">Eurostat gov_10a_exp</a>. Kods: <a href="https://github.com/Argent0rum/aizsardzibas-izdevumi">github.com/Argent0rum/aizsardzibas-izdevumi</a>.</footer>
</main>
</body>
</html>
"""
    (DOCS / "index.html").write_text(page)
    print("Web page saved to docs/index.html")


if __name__ == "__main__":
    main()
