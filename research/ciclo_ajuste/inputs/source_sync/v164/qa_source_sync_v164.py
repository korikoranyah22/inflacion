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


manifest = rows(HERE / "SOURCE_SYNC_FILE_MANIFEST_V164.csv")
assert len(manifest) == 5
for row in manifest:
    path = REPO / row["relative_path"].lstrip("/")
    assert path.is_file() and path.read_bytes().startswith(b"%PDF-")
    assert path.stat().st_size == int(row["size_bytes"])
    assert digest(path) == row["sha256"]

endpoints = rows(HERE / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V164.csv")
assert len(endpoints) == 5
assert any(row["result"] == "OFFICIAL_PLAN_AND_PUBLICATION_CROSSWALK_PRESERVED" for row in endpoints)
assert any(row["result"] == "OFFICIAL_SUPERVISION_AND_PUBLICATION_CROSSWALK_PRESERVED" for row in endpoints)

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V164.json").read_text(encoding="utf-8-sig"))
assert complete["master_catalog_entries"] == 584
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 584
assert complete["remaining_catalog_physical_or_hash_gaps"] == 0
assert complete["discovered_official_binary_recovery_queue"] == 0

print("V164 SOURCE SYNC QA PASS · files=5 · catalog=584/584 · queue=0 · missing=0")
