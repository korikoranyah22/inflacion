from pathlib import Path
import csv
R=Path(__file__).resolve().parents[5]
rows=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==697 and len({x['id'] for x in rows})==697
print('SOURCE SYNC V182 PASS · 13 new · 697/697')
