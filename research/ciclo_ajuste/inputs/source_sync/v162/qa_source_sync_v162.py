from pathlib import Path
import csv
import hashlib
import json
import subprocess


REPO = Path(__file__).resolve().parents[5]
CYCLE = REPO / "research/ciclo_ajuste"
SYNC = CYCLE / "inputs/source_sync/v162"
CATALOG = REPO / "data/fuentes/FUENTES.csv"
AUDIT = CYCLE / "source_audit/MASTER_LOCAL_HASH_VALIDATION_V162.csv"
MISSING = CYCLE / "source_audit/SOURCE_PRESERVATION_MISSING_V162.csv"
COMPLETE = CYCLE / "source_audit/CURRENT_SOURCE_COMPLETENESS_V162.json"
GLOBAL = CYCLE / "MANIFEST_SHA256.json"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"


def rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


failures = []
catalog = rows(CATALOG)
if len(catalog) != 578:
    failures.append(f"catalog rows {len(catalog)} != 578")
if len({row["id"] for row in catalog}) != len(catalog):
    failures.append("duplicate catalog ids")
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    if not path.is_file():
        failures.append(f"missing catalog file: {row['id']}")
    elif digest(path) != row["sha256"].lower():
        failures.append(f"catalog hash mismatch: {row['id']}")

audit = rows(AUDIT)
if len(audit) != 578 or any(row["exists"] != "True" or row["hash_ok"] != "True" for row in audit):
    failures.append("V162 master audit is not 578/578 physical and hash-valid")
if rows(MISSING):
    failures.append("V162 missing-source table is not empty")

sync = rows(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V162.csv")
if len(sync) != 1:
    failures.append(f"sync manifest rows {len(sync)} != 1")
for row in sync:
    path = REPO / row["relative_path"].lstrip("/")
    if not path.is_file() or digest(path) != row["sha256"]:
        failures.append(f"sync binary failure: {row['relative_path']}")
    else:
        result = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, errors="replace")
        if result.returncode != 0 or "Pages:           9" not in result.stdout:
            failures.append("Banco Rioja 9M PDF structural/page-count failure")

endpoints = rows(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V162.csv")
if len(endpoints) != 4:
    failures.append(f"public endpoint controls {len(endpoints)} != 4")
if sum("PENDING_SERVER_RESET" in row["local_status"] for row in endpoints) != 2:
    failures.append("expected exactly two transparent BCRA binary-recovery leads")

complete = json.loads(COMPLETE.read_text(encoding="utf-8-sig"))
expected = {
    "checkpoint": "V162",
    "master_catalog_entries": 578,
    "physical_local_copies": 578,
    "physical_local_hash_ok": 578,
    "remaining_catalog_physical_or_hash_gaps": 0,
    "exact_entities": 33,
    "discovered_official_binary_recovery_queue": 2,
    "request_drafts_status": "DRAFT_NOT_SENT",
}
for key, value in expected.items():
    if complete.get(key) != value:
        failures.append(f"completeness {key}={complete.get(key)!r}, expected {value!r}")

global_manifest = json.loads(GLOBAL.read_text(encoding="utf-8-sig"))
if global_manifest.get("checkpoint") != "V162" or global_manifest.get("exact_entities") != 33:
    failures.append("global manifest is not at V162/33 entities")
if global_manifest.get("file_count_excluding_manifest") != len(global_manifest.get("files", [])):
    failures.append("global manifest count is internally inconsistent")

origin_paths = {row["path"] for row in rows(ORIGINS)}
for path in SYNC.rglob("*"):
    if path.is_file():
        rel = path.relative_to(CYCLE).as_posix()
        if rel not in origin_paths:
            failures.append(f"FILE_ORIGINS missing V162 artifact: {rel}")

if failures:
    print("QA V162 SOURCE SYNC: FAIL")
    for failure in failures:
        print(f"- {failure}")
    raise SystemExit(1)

print("QA V162 SOURCE SYNC: PASS")
print("catalog=578 local=578 hash_ok=578 gaps=0 new_binary=1 pending_official_binaries=2")
print("analytical_promotion=NONE requests=DRAFT_NOT_SENT")
