from pathlib import Path
import csv
R=Path(__file__).resolve().parents[5]
rows=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==708 and len({x['id'] for x in rows})==708
print('SOURCE SYNC V184 PASS · 5 new · 708/708')
