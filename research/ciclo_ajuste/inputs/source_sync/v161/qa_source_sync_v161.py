"""Strict QA for the V161 archival synchronization."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
SYNC = REPO / "research/ciclo_ajuste/inputs/source_sync/v161"
CATALOG = REPO / "data/fuentes/FUENTES.csv"
AUDIT = REPO / "research/ciclo_ajuste/source_audit/MASTER_LOCAL_HASH_VALIDATION_V161.csv"
MISSING = REPO / "research/ciclo_ajuste/source_audit/SOURCE_PRESERVATION_MISSING_V161.csv"
CNV_MANIFEST = SYNC / "SOURCE_SYNC_CNV_ATTACHMENTS_V161.csv"
FILE_MANIFEST = SYNC / "SOURCE_SYNC_FILE_MANIFEST_V161.csv"
GLOBAL_MANIFEST = REPO / "research/ciclo_ajuste/MANIFEST_SHA256.json"
ORIGINS = REPO / "research/ciclo_ajuste/FILE_ORIGINS.csv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    failures: list[str] = []
    with CATALOG.open(encoding="utf-8-sig", newline="") as handle:
        catalog = list(csv.DictReader(handle))
    if len(catalog) != 577:
        failures.append(f"catalog rows {len(catalog)} != 577")
    if len({row["id"] for row in catalog}) != len(catalog):
        failures.append("duplicate catalogue ids")
    for row in catalog:
        path = REPO / row["archivo_local"].lstrip("/") if row["archivo_local"] else None
        if not path or not path.is_file():
            failures.append(f"missing catalogue file: {row['id']}")
            continue
        if not row["sha256"] or sha256(path) != row["sha256"].lower():
            failures.append(f"catalogue hash mismatch: {row['id']}")

    with AUDIT.open(encoding="utf-8-sig", newline="") as handle:
        audit = list(csv.DictReader(handle))
    if len(audit) != 577:
        failures.append(f"audit rows {len(audit)} != 577")
    if any(row["exists"] != "True" or row["hash_ok"] != "True" for row in audit):
        failures.append("master audit contains a physical/hash failure")
    with MISSING.open(encoding="utf-8-sig", newline="") as handle:
        if list(csv.DictReader(handle)):
            failures.append("V161 missing-source table is not empty")

    with CNV_MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
        cnv = list(csv.DictReader(handle))
    if len(cnv) != 30:
        failures.append(f"CNV attachment rows {len(cnv)} != 30")
    if len({row["blob_guid"] for row in cnv}) != 30:
        failures.append("CNV attachment blob GUIDs are not unique")
    filing_counts: dict[str, int] = {}
    pdfs: list[Path] = []
    for row in cnv:
        filing_counts[row["filing_key"]] = filing_counts.get(row["filing_key"], 0) + 1
        path = SYNC / row["local_path"]
        if not path.is_file():
            failures.append(f"missing CNV attachment: {row['local_path']}")
            continue
        if sha256(path) != row["served_sha256_hex"]:
            failures.append(f"served-byte hash mismatch: {row['local_path']}")
        if row["magic_valid"] != "true":
            failures.append(f"invalid attachment magic: {row['local_path']}")
        if row["declared_hash_matches_served_bytes"] != "false":
            failures.append(f"unexpected declared-hash relation: {row['local_path']}")
        if path.suffix.lower() == ".pdf":
            pdfs.append(path)
        elif path.suffix.lower() == ".docx":
            try:
                with zipfile.ZipFile(path) as archive:
                    if "word/document.xml" not in archive.namelist():
                        failures.append(f"DOCX structure missing document.xml: {row['local_path']}")
            except zipfile.BadZipFile:
                failures.append(f"invalid DOCX archive: {row['local_path']}")
    if set(filing_counts.values()) != {5} or len(filing_counts) != 6:
        failures.append(f"expected six filings with five attachments each: {filing_counts}")

    for name, expected_pages in (
        ("banco_rioja_eeff_fy2023.pdf", 86),
        ("banco_corrientes_eeff_fy2023.pdf", 142),
    ):
        path = SYNC / "binaries" / name
        if not path.is_file() or not path.read_bytes().startswith(b"%PDF-"):
            failures.append(f"invalid official PDF: {name}")
        else:
            pdfs.append(path)

    pdfinfo = shutil.which("pdfinfo")
    if not pdfinfo:
        failures.append("pdfinfo not available for structural PDF validation")
    else:
        for path in pdfs:
            result = subprocess.run(
                [pdfinfo, str(path)], capture_output=True, text=True, errors="replace"
            )
            if result.returncode != 0 or "Pages:" not in result.stdout:
                failures.append(f"pdfinfo failed: {path.relative_to(REPO)}")

    with FILE_MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
        files = list(csv.DictReader(handle))
    if len(files) != 43:
        failures.append(f"sync file-manifest rows {len(files)} != 43")
    for row in files:
        path = REPO / row["relative_path"].lstrip("/")
        if not path.is_file() or sha256(path) != row["sha256"]:
            failures.append(f"file-manifest failure: {row['relative_path']}")

    completeness = json.loads(
        (REPO / "research/ciclo_ajuste/source_audit/CURRENT_SOURCE_COMPLETENESS_V161.json").read_text(
            encoding="utf-8"
        )
    )
    expected = {
        "master_catalog_entries": 577,
        "physical_local_copies": 577,
        "physical_local_hash_ok": 577,
        "remaining_catalog_physical_or_hash_gaps": 0,
        "cnv_attachments_archived": 30,
        "cnv_attachment_magic_valid": 30,
        "cnv_declared_hash_matches_served_bytes": 0,
        "cnv_declared_hash_mismatches_served_bytes": 30,
    }
    for key, value in expected.items():
        if completeness.get(key) != value:
            failures.append(f"completeness {key}={completeness.get(key)!r}, expected {value!r}")
    phase = completeness.get("checkpoint")
    if phase == "V161_SOURCE_ARCHIVE_SYNC":
        expected_global_checkpoint = "V161_SOURCE_ARCHIVE_SYNC"
        expected_promotion = "NONE_ARCHIVAL_SYNC_ONLY"
    elif phase == "V161":
        expected_global_checkpoint = "V161"
        expected_promotion = "BMA_MARIVA_CORRIENTES_EXACT_HSBC_ND_STRICT"
        if completeness.get("exact_entities") != 33:
            failures.append("final analytical phase does not report 33 exact entities")
    else:
        expected_global_checkpoint = None
        expected_promotion = None
        failures.append(f"unknown V161 lifecycle phase: {phase!r}")
    if completeness.get("analytical_promotion") != expected_promotion:
        failures.append(
            f"analytical promotion mismatch for {phase}: "
            f"{completeness.get('analytical_promotion')!r} != {expected_promotion!r}"
        )
    if completeness.get("request_drafts_status") != "DRAFT_NOT_SENT":
        failures.append("request-draft status changed")

    global_manifest = json.loads(GLOBAL_MANIFEST.read_text(encoding="utf-8"))
    if global_manifest.get("checkpoint") != expected_global_checkpoint:
        failures.append(
            f"global manifest phase mismatch: {global_manifest.get('checkpoint')!r} "
            f"!= {expected_global_checkpoint!r}"
        )
    manifest_files = global_manifest.get("files", [])
    if global_manifest.get("file_count_excluding_manifest") != len(manifest_files):
        failures.append("global manifest file count is internally inconsistent")
    manifest_by_path = {row["path"]: row for row in manifest_files}
    required_global_paths = [
        "data/fuentes/FUENTES.csv",
        "research/ciclo_ajuste/TRANSPARENCY_README.md",
        "research/ciclo_ajuste/TREE.txt",
        "research/ciclo_ajuste/inputs/source_sync/v161/SOURCE_SYNC_REPORT_V161.md",
        "research/ciclo_ajuste/inputs/source_sync/v161/SOURCE_SYNC_CNV_ATTACHMENTS_V161.csv",
        "research/ciclo_ajuste/source_audit/CURRENT_SOURCE_COMPLETENESS_V161.json",
    ]
    for relative in required_global_paths:
        path = REPO / relative
        item = manifest_by_path.get(relative)
        if not item:
            failures.append(f"global manifest missing: {relative}")
        elif item["sha256"] != sha256(path) or item["bytes"] != path.stat().st_size:
            failures.append(f"global manifest stale: {relative}")

    cycle_tree = (REPO / "research/ciclo_ajuste/TREE.txt").read_text(encoding="utf-8")
    if "inputs/source_sync/v161/SOURCE_SYNC_REPORT_V161.md" not in cycle_tree:
        failures.append("cycle tree does not expose the V161 sync report")
    with ORIGINS.open(encoding="utf-8-sig", newline="") as handle:
        origin_paths = {row["path"] for row in csv.DictReader(handle)}
    for path in SYNC.rglob("*"):
        if path.is_file() and path.relative_to(REPO / "research/ciclo_ajuste").as_posix() not in origin_paths:
            failures.append(f"FILE_ORIGINS missing V161 artifact: {path.relative_to(REPO)}")

    if failures:
        print("QA V161 SOURCE SYNC: FAIL")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("QA V161 SOURCE SYNC: PASS")
    print("catalog=577 local=577 hash_ok=577 gaps=0")
    print("cnv_publicviews=6 cnv_attachments=30 valid=30 declared_vs_served_mismatch=30")
    print(
        f"sync_manifest_files=43 global_manifest_files={len(manifest_files)}; "
        f"phase={phase}; analytical_promotion={expected_promotion}; requests=DRAFT_NOT_SENT"
    )


if __name__ == "__main__":
    main()
