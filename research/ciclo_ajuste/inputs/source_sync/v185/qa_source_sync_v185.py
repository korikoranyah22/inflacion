from pathlib import Path
import csv
R=Path(__file__).resolve().parents[5]
rows=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==718 and len({x['id'] for x in rows})==718
print('SOURCE SYNC V185 PASS · 10 new · 718/718')
