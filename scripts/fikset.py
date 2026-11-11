"""Saglabā pašreizējo datu fiksētu kopiju mapē docs/arhivs/<lejupielādes datums>/.

Lapa atjaunojas reizi mēnesī, un SIPRI precizē jaunākos gadus, tāpēc darbā (piem., kursa darbā)
citētie skaitļi vēlāk var vairs nesakrist ar lapu. Fiksētā kopija nemainās.

Lietošana:  python scripts/fikset.py        (pēc tam: python scripts/lapa.py, lai kopija parādītos lapā)
"""
import shutil
from kopigais import DOCS, ROOT

RAW = ROOT / "data" / "raw"


def main():
    datums = (RAW / "lejupielades_datums.txt").read_text().strip()[:10]
    mape = DOCS / "arhivs" / datums
    mape.mkdir(parents=True, exist_ok=True)
    for f in sorted((DOCS / "dati").iterdir()):
        if f.is_file():
            shutil.copy2(f, mape / f.name)
    (mape / "LASIMANI.txt").write_text(
        f"Fiksēta datu kopija. Dati lejupielādēti {datums} no Pasaules Bankas (SIPRI) un Eurostat.\n"
        "Šī mape netiek atjaunināta. Atsaucē norādi šo datumu.\n", encoding="utf-8")
    print("Saglabāts:", mape)


if __name__ == "__main__":
    main()
