"""Promote the V161 archival sync into the master source catalogue and audits."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
SYNC = REPO / "research/ciclo_ajuste/inputs/source_sync/v161"
BINARIES = SYNC / "binaries"
CATALOG = REPO / "data/fuentes/FUENTES.csv"
CNV_MANIFEST = SYNC / "SOURCE_SYNC_CNV_ATTACHMENTS_V161.csv"
AUDIT_DIR = REPO / "research/ciclo_ajuste/source_audit"
DATE = "2026-08-31"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_path(path: Path) -> str:
    return "/" + path.relative_to(REPO).as_posix()


def row_template(**updates: str) -> dict[str, str]:
    row = {
        "id": "",
        "tema": "ciclo_ajuste_bancos",
        "institucion": "",
        "titulo": "",
        "url_original": "",
        "archivo_local": "",
        "fecha_descarga": DATE,
        "fecha_publicacion": "",
        "codigo_serie": "",
        "periodo_utilizado": "",
        "tipo": "",
        "sha256": "",
        "nota": "",
    }
    row.update(updates)
    return row


def update_existing(
    by_id: dict[str, dict[str, str]],
    source_id: str,
    local: Path,
    source_type: str,
    note: str,
) -> None:
    row = by_id[source_id]
    row["archivo_local"] = repo_path(local)
    row["fecha_descarga"] = DATE
    row["tipo"] = source_type
    row["sha256"] = digest(local)
    if note not in row["nota"]:
        row["nota"] = row["nota"].rstrip() + " " + note


def main() -> None:
    with CATALOG.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        if not fieldnames:
            raise RuntimeError("master source catalogue has no header")
        rows = list(reader)
    by_id = {row["id"]: row for row in rows}

    update_existing(
        by_id,
        "todosobrelamora_cruce",
        BINARIES / "todosobrelamora_snapshot.html",
        "Snapshot HTML secundario · copia local preservada",
        "V161 archiva una captura HTML íntegra para resiliencia de enlaces; su carácter secundario y no oficial no cambia.",
    )
    update_existing(
        by_id,
        "santander_cnv_filings_2023",
        BINARIES / "cnv_santander_filings_2023_index.html",
        "Índice regulatorio oficial · snapshot HTML preservado",
        "V161 archiva la landing regulatoria completa; los estados contables subyacentes siguen catalogados por separado.",
    )
    update_existing(
        by_id,
        "mariva_cnv_9m2023_individual_discovery",
        BINARIES / "cnv_mariva_9m2023_publicview.html",
        "Presentación regulatoria oficial · snapshot HTML preservado",
        "V161 recupera además los cinco adjuntos oficiales mediante el mecanismo público GetPublicValetKey de la CNV; cada binario se cataloga por separado.",
    )
    update_existing(
        by_id,
        "mariva_cnv_fy2023_individual_discovery",
        BINARIES / "cnv_mariva_fy2023_publicview.html",
        "Presentación regulatoria oficial · snapshot HTML preservado",
        "V161 recupera además los cinco adjuntos oficiales mediante el mecanismo público GetPublicValetKey de la CNV; cada binario se cataloga por separado.",
    )
    update_existing(
        by_id,
        "banco_rioja_eeff_fy2023_annexq_pending_v102",
        BINARIES / "banco_rioja_eeff_fy2023.pdf",
        "PDF oficial · binario preservado",
        "V161 recupera el original de 86 páginas y confirma visualmente el Anexo Q; se mantiene el tratamiento de falsificador sin promoción automática.",
    )

    additions: list[dict[str, str]] = []
    corrientes = BINARIES / "banco_corrientes_eeff_fy2023.pdf"
    additions.append(
        row_template(
            id="banco_corrientes_eeff_fy2023_annexq_v161",
            institucion="Banco de Corrientes S.A.",
            titulo="Banco de Corrientes · EEFF anuales · 31/12/2023 · Anexo Q",
            url_original="https://www.bancodecorrientes.com.ar/DesktopModules/EasyDNNNews/DocumentDownload.ashx?articleid=221&documentid=1193&moduleid=1510&portalid=0",
            archivo_local=repo_path(corrientes),
            periodo_utilizado="2023-12",
            tipo="PDF oficial · binario preservado",
            sha256=digest(corrientes),
            nota="V161 recupera el original de 142 páginas desde el endpoint documental oficial y confirma visualmente el Anexo Q.",
        )
    )

    publicview_meta = {
        "bma_9m2023": ("CNV / Banco BMA S.A.U.", "Presentación #3119515 · individual · 30/09/2023", "2023-09"),
        "bma_fy2023": ("CNV / Banco BMA S.A.U.", "Presentación #3171909 · individual · 31/12/2023", "2023-12"),
        "hsbc_9m2023": ("CNV / HSBC Bank Argentina S.A. (hoy Banco GGAL S.A.)", "Presentación #3121099 · individual · 30/09/2023", "2023-09"),
        "hsbc_fy2023": ("CNV / HSBC Bank Argentina S.A. (hoy Banco GGAL S.A.)", "Presentación #3163537 · individual · 31/12/2023", "2023-12"),
    }
    publicview_urls = {
        "bma_9m2023": "https://aif2.cnv.gov.ar/presentations/publicview/9d3ded55-6d87-4ca2-9feb-920d961f3acd",
        "bma_fy2023": "https://aif2.cnv.gov.ar/presentations/publicview/36d0f59a-8e3f-42cd-bf18-db44e023f18d",
        "hsbc_9m2023": "https://aif2.cnv.gov.ar/presentations/publicview/d483d33a-5c86-4fbb-ab9c-6528bf43f572",
        "hsbc_fy2023": "https://aif2.cnv.gov.ar/presentations/publicview/39f37eb9-5637-4cb3-ab6b-715da7830bd1",
    }
    for key, (institution, title, period) in publicview_meta.items():
        local = BINARIES / f"cnv_{key}_publicview.html"
        additions.append(
            row_template(
                id=f"cnv_{key}_publicview_snapshot_v161",
                institucion=institution,
                titulo=title,
                url_original=publicview_urls[key],
                archivo_local=repo_path(local),
                periodo_utilizado=period,
                tipo="Presentación regulatoria oficial · snapshot HTML preservado",
                sha256=digest(local),
                nota="V161 conserva la presentación pública completa y sus metadatos de adjuntos; cada adjunto se cataloga por separado.",
            )
        )

    institution_by_key = {
        "bma_9m2023": "CNV / Banco BMA S.A.U.",
        "bma_fy2023": "CNV / Banco BMA S.A.U.",
        "hsbc_9m2023": "CNV / HSBC Bank Argentina S.A. (hoy Banco GGAL S.A.)",
        "hsbc_fy2023": "CNV / HSBC Bank Argentina S.A. (hoy Banco GGAL S.A.)",
        "mariva_9m2023": "CNV / Banco Mariva S.A.",
        "mariva_fy2023": "CNV / Banco Mariva S.A.",
    }
    period_by_key = {key: ("2023-09" if "9m" in key else "2023-12") for key in institution_by_key}
    short_property = {
        "ABEstadoContable": "estado_contable",
        "ABMemoria": "memoria",
        "ABInformeAuditorIndependiente": "informe_auditor",
        "ABInformeComisionFiscalizadoraSindico": "informe_comision_fiscalizadora_sindico",
        "ABResenaInformativa": "resena_informativa",
    }
    property_title = {
        "ABEstadoContable": "Estado contable",
        "ABMemoria": "Memoria",
        "ABInformeAuditorIndependiente": "Informe del auditor independiente",
        "ABInformeComisionFiscalizadoraSindico": "Informe de comisión fiscalizadora o síndico",
        "ABResenaInformativa": "Reseña informativa",
    }
    with CNV_MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
        attachment_rows = list(csv.DictReader(handle))
    for item in attachment_rows:
        key = item["filing_key"]
        property_id = item["property_id"]
        local = SYNC / item["local_path"]
        mismatch = item["declared_hash_matches_served_bytes"] != "true"
        additions.append(
            row_template(
                id=f"cnv_{key}_{short_property[property_id]}_v161",
                institucion=institution_by_key[key],
                titulo=f"{property_title[property_id]} · {key.replace('_', ' ')}",
                url_original=item["publicview_url"],
                archivo_local=repo_path(local),
                codigo_serie=item["blob_guid"],
                periodo_utilizado=period_by_key[key],
                tipo=("Adjunto oficial CNV · DOCX preservado" if local.suffix.lower() == ".docx" else "Adjunto oficial CNV · PDF preservado"),
                sha256=item["served_sha256_hex"],
                nota=(
                    f"Nombre publicado: {item['original_filename']}. GUID blob: {item['blob_guid']}. "
                    f"Huella CNV declarada (base64): {item['cnv_declared_sha256_base64']}. "
                    f"SHA-256 de bytes servidos: {item['served_sha256_hex']}. "
                    + ("Las huellas difieren; se conservan ambas sin afirmar equivalencia." if mismatch else "La huella declarada coincide con los bytes servidos.")
                ),
            )
        )

    for row in additions:
        if row["id"] not in by_id:
            rows.append(row)
            by_id[row["id"]] = row

    with CATALOG.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    audit_rows = []
    for row in rows:
        local_text = row["archivo_local"]
        local = REPO / local_text.lstrip("/") if local_text else None
        exists = bool(local and local.is_file())
        actual = digest(local) if exists and local else ""
        expected = row["sha256"]
        audit_rows.append(
            {
                "id": row["id"],
                "archivo_local": local_text,
                "exists": str(exists),
                "sha_catalog": expected,
                "sha_actual": actual,
                "hash_ok": str(bool(expected) and expected.lower() == actual.lower()),
            }
        )
    for name in ("MASTER_LOCAL_HASH_VALIDATION_V161.csv", "SOURCE_BACKUP_CENSUS_V161.csv"):
        with (AUDIT_DIR / name).open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(audit_rows[0]))
            writer.writeheader()
            writer.writerows(audit_rows)

    missing = [row for row in audit_rows if row["exists"] != "True" or row["hash_ok"] != "True"]
    with (AUDIT_DIR / "SOURCE_PRESERVATION_MISSING_V161.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(audit_rows[0]))
        writer.writeheader()
        writer.writerows(missing)

    completeness = {
        "checkpoint": "V161_SOURCE_ARCHIVE_SYNC",
        "date": DATE,
        "master_catalog_entries": len(rows),
        "physical_local_copies": sum(row["exists"] == "True" for row in audit_rows),
        "physical_local_hash_ok": sum(row["hash_ok"] == "True" for row in audit_rows),
        "remaining_catalog_physical_or_hash_gaps": len(missing),
        "cnv_publicview_pages_archived": 6,
        "cnv_attachments_archived": len(attachment_rows),
        "cnv_attachment_magic_valid": sum(item["magic_valid"] == "true" for item in attachment_rows),
        "cnv_declared_hash_matches_served_bytes": sum(
            item["declared_hash_matches_served_bytes"] == "true" for item in attachment_rows
        ),
        "cnv_declared_hash_mismatches_served_bytes": sum(
            item["declared_hash_matches_served_bytes"] != "true" for item in attachment_rows
        ),
        "analytical_promotion": "NONE_ARCHIVAL_SYNC_ONLY",
        "request_drafts_status": "DRAFT_NOT_SENT",
    }
    (AUDIT_DIR / "CURRENT_SOURCE_COMPLETENESS_V161.json").write_text(
        json.dumps(completeness, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(completeness, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
