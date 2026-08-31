"""Finalize provenance, trees and the global SHA-256 manifest after V161 sync."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
CYCLE = REPO / "research/ciclo_ajuste"
SYNC = CYCLE / "inputs/source_sync/v161"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"
GLOBAL_MANIFEST = CYCLE / "MANIFEST_SHA256.json"
EXCLUDED_DIRS = {".git", "__pycache__", "tmp", "node_modules"}
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            (name for name in dirnames if name not in EXCLUDED_DIRS), key=str.casefold
        )
        for filename in sorted(filenames, key=str.casefold):
            yield Path(dirpath) / filename


def tree(root: Path) -> str:
    lines: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            (name for name in dirnames if name not in EXCLUDED_DIRS), key=str.casefold
        )
        base = Path(dirpath)
        lines.extend((base / name).relative_to(root).as_posix() + "/" for name in dirnames)
        lines.extend(
            (base / name).relative_to(root).as_posix()
            for name in sorted(filenames, key=str.casefold)
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    with ORIGINS.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or ["path", "origin", "note"]
        rows = list(reader)
    order = [row["path"] for row in rows]
    by_path = {row["path"]: row for row in rows}

    def upsert(path: Path, origin: str, note: str) -> None:
        relative = path.relative_to(CYCLE).as_posix()
        by_path[relative] = {"path": relative, "origin": origin, "note": note}
        if relative not in order:
            order.append(relative)

    for path in sorted(SYNC.rglob("*")):
        if not path.is_file():
            continue
        if "/binaries/cnv_attachments/" in "/" + path.relative_to(CYCLE).as_posix():
            origin = "CNV AIF public attachment · recovered V161"
            note = "Public GetPublicValetKey/DownloadBlob retrieval; CNV-declared and served-byte hashes retained separately."
        elif path.name.endswith("_publicview.html"):
            origin = "CNV AIF PublicView · copied V161"
            note = "Full official public-view response with embedded filing and attachment metadata."
        elif path.name in {"fb.publicuploader.js", "site.bo.min.js"}:
            origin = "CNV AIF public frontend · copied V161"
            note = "Public frontend script preserved to document the attachment-retrieval contract."
        elif path.suffix.lower() in {".pdf", ".html"} and path.parent == SYNC / "binaries":
            origin = "Remote source snapshot · recovered V161"
            note = "Source response preserved locally with size and SHA-256 in the V161 file manifest."
        else:
            origin = "generated/updated V161 source sync"
            note = "Reproducible archival synchronization, manifest, report or QA artifact."
        upsert(path, origin, note)

    for name in (
        "CURRENT_SOURCE_COMPLETENESS_V161.json",
        "MASTER_LOCAL_HASH_VALIDATION_V161.csv",
        "SOURCE_BACKUP_CENSUS_V161.csv",
        "SOURCE_PRESERVATION_MISSING_V161.csv",
    ):
        upsert(
            CYCLE / "source_audit" / name,
            "generated/updated V161 source sync",
            "V161 master-catalog physical and hash completeness audit.",
        )
    upsert(
        CYCLE / "inputs/issuer_retrieval/v93/binaries/008_Diseño Memoria y Balance General 2023 web.pdf",
        "canonical Unicode copy V161",
        "Byte-identical canonical-path copy; prior mojibake-named source retained.",
    )
    upsert(
        CYCLE / "TRANSPARENCY_README.md",
        "generated/updated V161 source sync",
        "V161 archival completeness and CNV hash-anomaly disclosure appended.",
    )
    upsert(
        CYCLE / "TREE.txt",
        "generated/updated V161 source sync",
        "Cycle inventory regenerated after V161 archival synchronization.",
    )
    upsert(
        CYCLE / "MANIFEST_SHA256.json",
        "generated/updated V161 source sync",
        "Global repository manifest regenerated after V161 archival synchronization.",
    )
    data_catalog = "data/fuentes/FUENTES.csv"
    by_path[data_catalog] = {
        "path": data_catalog,
        "origin": "generated/updated V161 source sync",
        "note": "V161 promotes preserved snapshots and 30 CNV attachments; 577/577 local hash-valid sources.",
    }
    if data_catalog not in order:
        order.append(data_catalog)

    with ORIGINS.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(by_path[path] for path in order)

    (REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
    (CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")

    files = [
        {
            "path": path.relative_to(REPO).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in iter_files(REPO)
        if path != GLOBAL_MANIFEST
    ]
    payload = {
        "checkpoint": "V161_SOURCE_ARCHIVE_SYNC",
        "created_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "strict_coverage_pct": STRICT,
        "exact_entities": 30,
        "closed_network_gate": "NO",
        "source_audit": "577 master; 577 physical SHA-valid; 0 catalogue gaps; 6 CNV PublicView pages and 30 attachments archived; declared-vs-served hash anomaly retained; no analytical promotion.",
        "historical_workstream": "Resume V161 analysis after archival sync; SAF355 and bank-execution gates remain strict; six information-request drafts not submitted.",
        "file_count_excluding_manifest": len(files),
        "files": files,
    }
    temporary = GLOBAL_MANIFEST.with_suffix(".json.V161tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(GLOBAL_MANIFEST)
    print(f"origins={len(order)} manifest_files={len(files)}")


if __name__ == "__main__":
    main()
