"""Runs the whole pipeline in order: download → clean → calculate → charts → web page.

Usage:  python scripts/run_all.py            (downloads fresh data)
        python scripts/run_all.py --offline  (reuses the files already in data/raw)
"""
import sys

import analize
import apstrade
import grafiki
import lapa
import lejupielade

if "--offline" not in sys.argv:
    print("1/5 Downloading data"); lejupielade.main()
print("2/5 Cleaning"); apstrade.main()
print("3/5 Calculations and Excel"); analize.main()
print("4/5 Charts"); grafiki.main()
print("5/5 Web page"); lapa.main()
print("Done.")
