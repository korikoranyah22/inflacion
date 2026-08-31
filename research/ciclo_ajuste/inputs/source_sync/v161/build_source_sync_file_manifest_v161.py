"""Build the per-file archival manifest for the V161 source synchronization."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
SYNC = REPO / "research/ciclo_ajuste/inputs/source_sync/v161"
BINARIES = SYNC / "binaries"
OUTPUT = SYNC / "SOURCE_SYNC_FILE_MANIFEST_V161.csv"
CNV_MANIFEST = SYNC / "SOURCE_SYNC_CNV_ATTACHMENTS_V161.csv"
CATALOG = REPO / "data/fuentes/FUENTES.csv"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signature(path: Path) -> str:
    head = path.read_bytes()[:16]
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "PDF_MAGIC_OK" if head.startswith(b"%PDF-") else "PDF_MAGIC_FAIL"
    if suffix == ".docx":
        return "ZIP_MAGIC_OK" if head.startswith(b"PK") else "ZIP_MAGIC_FAIL"
    if suffix == ".html":
        return "HTML_SIGNATURE_OK" if b"<!DOCTYPE html" in head.upper() else "HTML_SNAPSHOT"
    if suffix == ".js":
        return "TEXT_JAVASCRIPT"
    return "FILE_PRESENT"


def main() -> None:
    rows: list[dict[str, str | int]] = []
    attachment_meta: dict[str, dict[str, str]] = {}
    with CNV_MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            attachment_meta[row["local_path"]] = row

    publicview_urls = {
        row["archived_publicview"]: row["publicview_url"]
        for row in attachment_meta.values()
    }
    roots = {
        "banco_rioja_eeff_fy2023.pdf": "https://bancorioja.com.ar/pdf/EEFF-BR-2023.pdf",
        "banco_corrientes_eeff_fy2023.pdf": "https://www.bancodecorrientes.com.ar/DesktopModules/EasyDNNNews/DocumentDownload.ashx?articleid=221&documentid=1193&moduleid=1510&portalid=0",
        "todosobrelamora_snapshot.html": "https://todosobrelamora.vercel.app/",
        "cnv_santander_filings_2023_index.html": "https://www.cnv.gov.ar/SitioWeb/Empresas/Empresa/30500008454",
    }

    for path in sorted(BINARIES.rglob("*")):
        if not path.is_file():
            continue
        rel_sync = path.relative_to(SYNC).as_posix()
        if rel_sync in attachment_meta:
            meta = attachment_meta[rel_sync]
            source_url = meta["publicview_url"]
            role = "CNV_PUBLIC_ATTACHMENT"
            note = (
                f"blob_guid={meta['blob_guid']}; property={meta['property_id']}; "
                f"declared_hash_matches_served_bytes={meta['declared_hash_matches_served_bytes']}"
            )
        elif rel_sync in publicview_urls:
            source_url = publicview_urls[rel_sync]
            role = "CNV_PUBLICVIEW_HTML"
            note = "Full public-view response with embedded filing data and attachment metadata."
        else:
            source_url = roots.get(path.name, "")
            role = {
                "banco_rioja_eeff_fy2023.pdf": "OFFICIAL_FINANCIAL_STATEMENTS",
                "banco_corrientes_eeff_fy2023.pdf": "OFFICIAL_FINANCIAL_STATEMENTS",
                "todosobrelamora_snapshot.html": "SECONDARY_SITE_SNAPSHOT",
                "cnv_santander_filings_2023_index.html": "CNV_INDEX_SNAPSHOT",
            }.get(path.name, "ARCHIVED_SOURCE")
            note = ""
        rows.append(
            {
                "relative_path": "/" + path.relative_to(REPO).as_posix(),
                "archive_role": role,
                "source_url": source_url,
                "size_bytes": path.stat().st_size,
                "sha256": digest(path),
                "format_verification": signature(path),
                "note": note,
            }
        )

    for filename, source_url, role in (
        (
            "fb.publicuploader.js",
            "https://aif2.cnv.gov.ar/Engine/js/fbhtmlcontrols/fb.publicuploader.js",
            "CNV_PUBLIC_DOWNLOAD_CONTRACT_SCRIPT",
        ),
        (
            "site.bo.min.js",
            "https://aif2.cnv.gov.ar/js/site.bo.min.js?v=IGhBiXe1fb2NFEGNYLVaOYb957igFRpHbYLChEyNPOc",
            "CNV_PUBLIC_DOWNLOAD_CONTRACT_SCRIPT",
        ),
    ):
        path = SYNC / filename
        rows.append(
            {
                "relative_path": "/" + path.relative_to(REPO).as_posix(),
                "archive_role": role,
                "source_url": source_url,
                "size_bytes": path.stat().st_size,
                "sha256": digest(path),
                "format_verification": signature(path),
                "note": "Archived to document GetPublicValetKey and DownloadBlob public retrieval flow.",
            }
        )

    with CATALOG.open(encoding="utf-8-sig", newline="") as handle:
        pampa = next(
            row
            for row in csv.DictReader(handle)
            if row["id"] == "issuer_v93_g08_banco_de_la_pampa_s_e_m"
        )
    pampa_path = REPO / pampa["archivo_local"].lstrip("/")
    rows.append(
        {
            "relative_path": pampa["archivo_local"],
            "archive_role": "CANONICAL_UNICODE_PATH_COPY",
            "source_url": pampa["url_original"],
            "size_bytes": pampa_path.stat().st_size,
            "sha256": digest(pampa_path),
            "format_verification": signature(pampa_path),
            "note": "Byte-identical canonical-path copy; the earlier mojibake-named file was preserved and not deleted.",
        }
    )

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"files={len(rows)} bytes={sum(int(row['size_bytes']) for row in rows)}")


if __name__ == "__main__":
    main()
