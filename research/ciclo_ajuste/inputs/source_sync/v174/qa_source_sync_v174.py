from pathlib import Path
import csv,hashlib
root=Path(__file__).resolve().parents[5]
rows=list(csv.DictReader(Path(__file__).with_name('SOURCE_SYNC_FILE_MANIFEST_V174.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==6
for r in rows:
 p=root/r['relative_path'].lstrip('/'); assert p.is_file() and p.stat().st_size==int(r['size_bytes']) and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
print('SOURCE SYNC V174 PASS · 6/6')
