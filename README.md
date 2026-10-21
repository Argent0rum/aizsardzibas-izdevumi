# Aizsardzības izdevumi Eiropā, 2000–šodien

Dati, aprēķini un grafiki kursa darbam par aizsardzības izdevumu tendencēm Eiropā, īpaši Baltijas valstīs.

**Rezultāti:** https://argent0rum.github.io/aizsardzibas-izdevumi/
— galvenie skaitļi, visi grafiki un Excel darbgrāmata vienuviet.

*English summary: a data pipeline that downloads defence spending data for 41 European countries (World Bank / SIPRI and Eurostat), cleans it, calculates trends and comparisons, and produces charts, an Excel workbook and a results page in Latvian for a term paper at the University of Latvia. It re-runs automatically every month on GitHub Actions.*

## Kas te ir

| Mape / fails | Saturs |
|---|---|
| `docs/dati/aizsardzibas_izdevumi.xlsx` | Excel darbgrāmata: tabulas pa gadiem, periodu un reģionu vidējie, korelācija |
| `docs/dati/dati_visi.csv` | Visi dati vienā tabulā (viena rinda = viena valsts vienā gadā) |
| `docs/grafiki/` | Grafiki PNG formātā (200 dpi), gatavi ievietošanai Word dokumentā |
| `docs/index.html` | Rezultātu lapa |
| `config/valstis.csv` | Valstu saraksts: nosaukumi latviski, reģioni, ES un NATO dalība |
| `scripts/` | Python kods (skat. zemāk) |
| `data/raw/` | Neapstrādātie dati tieši tā, kā tie lejupielādēti |

## Kā tas strādā

Kods ir sadalīts piecos soļos, katrs savā failā:

1. `lejupielade.py` — lejupielādē datus no Pasaules Bankas API un Eurostat
2. `apstrade.py` — apvieno tos vienā tabulā un aprēķina atvasinātos rādītājus (izdevumi uz iedzīvotāju, reālie izdevumi)
3. `analize.py` — aprēķini un Excel darbgrāmata
4. `grafiki.py` — grafiki ar latviskiem nosaukumiem un decimālkomatu
5. `lapa.py` — rezultātu tīmekļa lapa

`run_all.py` palaiž visus soļus pēc kārtas.

**Automātiska atjaunināšana:** GitHub Actions (`.github/workflows/atjaunot-datus.yml`) palaiž visu procesu katra mēneša 1. datumā un katru reizi, kad mainās kods. Lai palaistu uzreiz: cilne **Actions → Atjaunot datus → Run workflow**.

**Lai palaistu savā datorā:**
```
pip install -r requirements.txt
python scripts/run_all.py
```

## Rādītāji

- **% no IKP** — militārie izdevumi kā daļa no iekšzemes kopprodukta (galvenais rādītājs; NATO mērķis — 2 %)
- **Uz vienu iedzīvotāju** — ASV dolāri faktiskajās cenās
- **Reālie izdevumi** — % no IKP × IKP 2015. gada cenās (salīdzināms laika gaitā bez inflācijas)
- **% no valdības izdevumiem** — cik liela budžeta daļa aiziet aizsardzībai
- **Eurostat COFOG GF02** — valdības izdevumi aizsardzībai pēc ES finanšu statistikas (šaurāka definīcija nekā SIPRI)

## Avoti

- Pasaules Banka, World Development Indicators — militāro izdevumu dati no SIPRI Military Expenditure Database: https://data.worldbank.org/indicator/MS.MIL.XPND.GD.ZS
- Eurostat, General government expenditure by function (COFOG), `gov_10a_exp`: https://ec.europa.eu/eurostat/databrowser/view/gov_10a_exp/default/table

Ukraina, Krievija un Baltkrievija ir datos, bet nav iekļautas reitingos un vidējos rādītājos, jo kara ietekme izkropļotu salīdzinājumu.
