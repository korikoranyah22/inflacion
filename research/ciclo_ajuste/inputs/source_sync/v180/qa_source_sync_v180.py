from pathlib import Path
import csv,hashlib
H=Path(__file__).resolve().parent; R=H.parents[4]
rows=list(csv.DictReader((H/'SOURCE_SYNC_FILE_MANIFEST_V180.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==24
for x in rows:
 p=R/x['local_path'].lstrip('/'); assert p.is_file() and p.stat().st_size==int(x['bytes']) and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
print('SOURCE SYNC V180 PASS · 24/24')
