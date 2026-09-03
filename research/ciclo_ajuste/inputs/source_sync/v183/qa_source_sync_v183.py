from pathlib import Path
import csv
R=Path(__file__).resolve().parents[5]
rows=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==703 and len({x['id'] for x in rows})==703
print('SOURCE SYNC V183 PASS · 6 new · 703/703')
