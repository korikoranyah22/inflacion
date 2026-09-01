from pathlib import Path
import csv, hashlib
root = Path(__file__).resolve().parents[5]
rows = list(csv.DictReader(Path(__file__).with_name('SOURCE_SYNC_FILE_MANIFEST_V169.csv').open(encoding='utf-8-sig', newline='')))
assert len(rows) == 5
for row in rows:
    path = root / row['relative_path'].lstrip('/')
    assert path.is_file() and path.stat().st_size == int(row['size_bytes'])
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
    if path.suffix.lower() == '.pdf':
        assert path.read_bytes().startswith(b'%PDF-')
print('SOURCE SYNC V169 PASS · 5/5')
