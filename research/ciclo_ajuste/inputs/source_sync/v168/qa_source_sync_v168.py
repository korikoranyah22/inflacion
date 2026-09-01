from pathlib import Path
import csv, gzip, hashlib
root = Path(__file__).resolve().parents[5]
rows = list(csv.DictReader(Path(__file__).with_name('SOURCE_SYNC_FILE_MANIFEST_V168.csv').open(encoding='utf-8-sig', newline='')))
assert len(rows) == 4
for row in rows:
    path = root / row['relative_path'].lstrip('/')
    assert path.is_file() and path.stat().st_size == int(row['size_bytes'])
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
    text = gzip.open(path, 'rb').read().decode('cp1252', errors='replace') if path.name.endswith('.arc.gz') else path.read_bytes().decode('cp1252', errors='replace')
    assert 'sigen.gov.ar' in text or 'Plan Sigen 2009' in text
print('SOURCE SYNC V168 PASS · 4/4')
