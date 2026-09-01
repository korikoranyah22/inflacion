from pathlib import Path
import csv
import hashlib
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"


def rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


manifest = rows(HERE / "SOURCE_SYNC_FILE_MANIFEST_V163.csv")
assert len(manifest) == 1
for row in manifest:
    path = REPO / row["relative_path"].lstrip("/")
    assert path.is_file()
    assert path.stat().st_size == int(row["size_bytes"])
    assert digest(path) == row["sha256"]
    assert path.read_bytes().startswith(b"%PDF-")

endpoints = rows(HERE / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V163.csv")
assert len(endpoints) == 6
assert any(row["result"] == "OFFICIAL_PDF_ARCHIVED" for row in endpoints)

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V163.json").read_text(encoding="utf-8-sig"))
assert complete["master_catalog_entries"] == 579
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 579
assert complete["remaining_catalog_physical_or_hash_gaps"] == 0

print("V163 SOURCE SYNC QA PASS · files=1 · catalog=579/579 · missing=0")
