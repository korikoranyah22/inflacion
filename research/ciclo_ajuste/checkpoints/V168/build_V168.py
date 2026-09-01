from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
from pathlib import Path
import csv
import gzip
import hashlib
import json
import os
import re


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
PARENT = CYCLE / "checkpoints" / "V167"
AUDIT = CYCLE / "source_audit"
SYNC = CYCLE / "inputs" / "source_sync" / "v168"
HIST = CYCLE / "inputs" / "historical_retrieval" / "v168" / "binaries"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"

PLAN_PAGE = HIST / "sigen_planannual_2009_20090221.html"
RES_2010 = HIST / "sigen_resolutions_index_20100729.arc.gz"
NORM_2010 = HIST / "sigen_normative_index_20100729.arc.gz"
RES_2012 = HIST / "sigen_resolutions_index_20120205.arc.gz"
EXPECTED = {
    PLAN_PAGE: (23667, "665f4b67f1295096cfa8f0921b360963cc56fcdf26caed106e9aa062f3907866"),
    RES_2010: (5762, "c9eb44dc4b260e3aba8173c8a96ccf0b02777703aff9474704d6c17390759586"),
    NORM_2010: (4451, "f9df6c7ec242b81734446bf9b8b46e2a50ce619ddc170871c1c379403a1c6687"),
    RES_2012: (6005, "89d267552b9e3e6f155f812bb680b7827dfacc730b46e61263ae02ce39781bdc"),
}
COVERAGE = "63.4406041403540997520463142785031521252747951992299547614348265414453439585848248058817492708499966268585997481191265825"
NUMERATOR = "61345602.215"
SYSTEM_ASSETS = "96697695.5"
EXCLUDED_DIRS = {".git", "__pycache__", "tmp", "node_modules"}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows, fields=None):
    fields = fields or (list(rows[0]) if rows else [])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted((name for name in dirnames if name not in EXCLUDED_DIRS), key=str.casefold)
        for filename in sorted(filenames, key=str.casefold):
            yield Path(dirpath) / filename


def tree(root: Path):
    lines = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted((name for name in dirnames if name not in EXCLUDED_DIRS), key=str.casefold)
        base = Path(dirpath)
        lines.extend((base / name).relative_to(root).as_posix() + "/" for name in dirnames)
        lines.extend((base / name).relative_to(root).as_posix() for name in sorted(filenames, key=str.casefold))
    return "\n".join(lines) + "\n"


def clone_parent():
    excluded = {
        "build_V167.py", "qa_v167.py", "MANIFEST_V167.json", "README_V167.md", "VEREDICTO_V167.md",
        "AUDITORIA_V167.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V167_A_V168.md",
        "CURRENT_STATE_V167.csv", "FOUR_LEG_PASS_PANEL_V167.csv", "STRICT_Q4_FOUR_LEG_COVERAGE_V167.csv",
        "V167_SOURCE_BUNDLE.csv", "V167_PUBLIC_SEARCH_LOG.csv", "CNV_ATTACHMENT_ANALYTIC_REVIEW_V167.md",
        "E0_FISCAL_RECONSTRUCTION_V167.md", "E0_PLAN_2009_ANNEX_G_PUBLIC_NEGATIVE_AND_EXACT_DATE_GATE_V167.csv",
        "E0_SIGEN_HISTORICAL_ROUTE_GRAMMAR_V167.csv", "E0_SIGEN_ARCHIVED_PAGE_LINKS_V167.csv",
        "E0_PLAN_2009_ARCHIVE_CANDIDATE_MATRIX_V167.csv", "E0_PLAN_2009_ARCHIVE_RECOVERY_NOTE_V167.md",
    }
    for source in sorted(PARENT.iterdir(), key=lambda path: path.name.casefold()):
        if not source.is_file() or source.name in excluded or source.name.startswith("E0_V167_"):
            continue
        target = HERE / source.name.replace("V167", "V168")
        target.write_text(source.read_text(encoding="utf-8-sig").replace("V167", "V168"), encoding="utf-8")


clone_parent()
for request_name in ("E0_V167_REQUEST_OBJECTS.csv", "E0_V167_REQUEST_OBJECTS_V167.csv"):
    source = PARENT / request_name
    target = HERE / request_name.replace("V167", "V168")
    target.write_text(source.read_text(encoding="utf-8-sig").replace("V167", "V168"), encoding="utf-8")

# Validate and catalogue four archival objects.
for path, (size, digest) in EXPECTED.items():
    assert path.is_file() and path.stat().st_size == size and sha256(path) == digest

catalog = read_csv(CATALOG)
catalog_fields = list(catalog[0])
new_sources = [
    {
        "id": "sigen_planannual_2009_wayback_20090221_v168", "tema": "ciclo_ajuste_historico",
        "institucion": "SIGEN · captura archivística Internet Archive",
        "titulo": "Página oficial histórica Plan SIGEN 2009 · captura 2009-02-21",
        "url_original": "http://www.sigen.gov.ar:80/plananual2009.asp",
        "archivo_local": "/" + PLAN_PAGE.relative_to(REPO).as_posix(), "fecha_descarga": "2026-08-31",
        "fecha_publicacion": "2009-02-21", "codigo_serie": "WAYBACK-CDX-20090221151746",
        "periodo_utilizado": "2008-2010", "tipo": "HTML · payload oficial preservado por archivo web",
        "sha256": EXPECTED[PLAN_PAGE][1],
        "nota": "V168: snapshot id_ sin reescritura. Enumera el Plan 2009, Anexo F 8-18, Anexo G capacitación y Plan Red 2009; no contiene los cuerpos PDF.",
    },
    {
        "id": "sigen_resolutions_index_cc_20100729_v168", "tema": "ciclo_ajuste_historico",
        "institucion": "SIGEN · captura archivística Common Crawl",
        "titulo": "Buscador oficial histórico de resoluciones SIGEN · captura 2010-07-29",
        "url_original": "http://www.sigen.gov.ar/resoluciones.asp",
        "archivo_local": "/" + RES_2010.relative_to(REPO).as_posix(), "fecha_descarga": "2026-08-31",
        "fecha_publicacion": "2010-07-29", "codigo_serie": "CC-MAIN-2009-2010",
        "periodo_utilizado": "1993-2010", "tipo": "ARC.GZ · payload oficial preservado por archivo web",
        "sha256": EXPECTED[RES_2010][1],
        "nota": "V168: ARC offset 46589177 length 5762. Formulario POST Result_resoluciones.asp con número, año, fechas y palabras clave.",
    },
    {
        "id": "sigen_normative_index_cc_20100729_v168", "tema": "ciclo_ajuste_historico",
        "institucion": "SIGEN · captura archivística Common Crawl",
        "titulo": "Índice oficial histórico de normativa SIGEN · captura 2010-07-29",
        "url_original": "http://www.sigen.gov.ar/normativa.asp",
        "archivo_local": "/" + NORM_2010.relative_to(REPO).as_posix(), "fecha_descarga": "2026-08-31",
        "fecha_publicacion": "2010-07-29", "codigo_serie": "CC-MAIN-2009-2010",
        "periodo_utilizado": "2008-2010", "tipo": "ARC.GZ · payload oficial preservado por archivo web",
        "sha256": EXPECTED[NORM_2010][1],
        "nota": "V168: ARC offset 46532340 length 4451. Recupera normas01.asp a normas05.asp y el vínculo al buscador de resoluciones.",
    },
    {
        "id": "sigen_resolutions_index_cc_20120205_v168", "tema": "ciclo_ajuste_historico",
        "institucion": "SIGEN · captura archivística Common Crawl",
        "titulo": "Buscador oficial histórico de resoluciones SIGEN · control 2012-02-05",
        "url_original": "http://www.sigen.gov.ar/resoluciones.asp",
        "archivo_local": "/" + RES_2012.relative_to(REPO).as_posix(), "fecha_descarga": "2026-08-31",
        "fecha_publicacion": "2012-02-05", "codigo_serie": "CC-MAIN-2012",
        "periodo_utilizado": "1993-2012", "tipo": "ARC.GZ · payload oficial preservado por archivo web",
        "sha256": EXPECTED[RES_2012][1],
        "nota": "V168: ARC offset 82161832 length 6005. Confirma estabilidad de formulario, endpoint y cobertura anual.",
    },
]
catalog_by_id = {row["id"]: row for row in catalog}
for row in new_sources:
    catalog_by_id[row["id"]] = row
catalog = list(catalog_by_id.values())
write_csv(CATALOG, catalog, catalog_fields)
assert len(catalog) == 591 and len(catalog_by_id) == 591

audit_rows = []
for row in catalog:
    local = REPO / row["archivo_local"].lstrip("/")
    actual = sha256(local) if local.is_file() else ""
    audit_rows.append({
        "id": row["id"], "archivo_local": row["archivo_local"], "exists": str(local.is_file()),
        "sha_catalog": row["sha256"].lower(), "sha_actual": actual,
        "hash_ok": str(local.is_file() and bool(row["sha256"]) and actual == row["sha256"].lower()),
    })
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V168.csv", audit_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V168.csv", audit_rows)
missing = [row for row in audit_rows if row["exists"] != "True" or row["hash_ok"] != "True"]
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V168.csv", missing, list(audit_rows[0]))
assert not missing

# Parse target page and historical indices.
page_text = PLAN_PAGE.read_bytes().decode("cp1252", errors="replace")
page_links = sorted({unescape(value) for value in re.findall(r"(?is)href\s*=\s*['\"]([^'\"]+)", page_text) if "plananualpdfs" in value.lower()})
assert "Plan Sigen 2009" in page_text and len(page_links) == 14
assert "documentacion/plananualpdfs/Plan SIGEN 2009.pdf" in page_links
annex_f = [link for link in page_links if "/Anexo F - Cuadro " in link]
assert len(annex_f) == 11
assert {int(re.search(r"Cuadro (\d+)", link).group(1)) for link in annex_f} == set(range(8, 19))
assert "documentacion/plananualpdfs/Anexo G - Capacitacion 2009.pdf" in page_links
assert "documentacion/plananualpdfs/planred2009.pdf" in page_links

res_2010_text = gzip.open(RES_2010, "rb").read().decode("cp1252", errors="replace")
norm_2010_text = gzip.open(NORM_2010, "rb").read().decode("cp1252", errors="replace")
res_2012_text = gzip.open(RES_2012, "rb").read().decode("cp1252", errors="replace")
for text in (res_2010_text, res_2012_text):
    assert 'action="Result_resoluciones.asp"' in text
    for field in ("txtNumero", "cboAnio", "calDesde", "calHasta", "txtKeywords", "hdnAccion"):
        assert field in text
    assert "value='2008'" in text and "value='2009'" in text
assert all(f"normas{i:02}.asp" in norm_2010_text for i in range(1, 6))

link_rows = []
for link in page_links:
    kind = "PLAN_MAIN" if link.endswith("Plan SIGEN 2009.pdf") else "RED_FEDERAL_PLAN" if link.endswith("planred2009.pdf") else "ANNEX_G" if "Anexo G" in link else "ANNEX_F_TABLE"
    table = re.search(r"Cuadro (\d+)", link)
    link_rows.append({
        "capture_timestamp": "20090221151746", "page": "plananual2009.asp", "href": link,
        "document_class": kind, "table_number": table.group(1) if table else "", "body_preserved": "NO",
        "status": "EXACT_OFFICIAL_LINK_BODY_NOT_CAPTURED",
    })
write_csv(HERE / "E0_SIGEN_PLAN_2009_ARCHIVED_PAGE_LINKS_V168.csv", link_rows)

grammar = [
    {"control_id": "RG168_01", "capture_or_period": "2008-10-06", "page": "plananual.asp", "document_route": "documentos_pdf/Plan_SIGEN_2007.pdf", "annex_route": "documentos_pdf/plannual2007/cuadro5..15.pdf", "result": "GENERIC_PAGE_STALE_STILL_PLAN_2007", "probative_use": "Control heredado V167", "limit": "No corresponde al Plan 2009"},
    {"control_id": "RG168_02", "capture_or_period": "2008-07-05", "page": "plananual2008.asp", "document_route": "documentacion/plananualpdfs/Plan SIGEN 2008.pdf", "annex_route": "Anexo D - Cuadro 5..15.pdf", "result": "SPECIFIC_2008_ROUTE_CONFIRMED", "probative_use": "Control heredado V167", "limit": "No determina contenido 2009"},
    {"control_id": "RG168_03", "capture_or_period": "2009-02-21", "page": "plananual2009.asp", "document_route": "documentacion/plananualpdfs/Plan SIGEN 2009.pdf", "annex_route": "Anexo F - Cuadro 8..18.pdf; Anexo G - Capacitacion 2009.pdf", "result": "TARGET_YEAR_PAGE_AND_EXACT_LINK_INVENTORY_RECOVERED", "probative_use": "Cierra URL y nombres exactos del inventario 2009", "limit": "La página no contiene los cuerpos PDF"},
    {"control_id": "RG168_04", "capture_or_period": "2010", "page": "plananual2010.asp", "document_route": "documentacion/plananualpdfs/Plan SIGEN 2010.pdf", "annex_route": "Anexo D Cuadro 4..14.pdf; Anexo E", "result": "NEAR_TARGET_CONTROL", "probative_use": "Confirma continuidad de carpeta", "limit": "No sustituye 2009"},
]
write_csv(HERE / "E0_SIGEN_HISTORICAL_ROUTE_GRAMMAR_V168.csv", grammar)

schema = [
    {"schema_id": "RI168_01", "capture": "2010-07-29", "surface": "resoluciones.asp", "element": "form", "name_or_value": "frmQuery", "semantics": "buscador histórico", "proof": "POST a Result_resoluciones.asp", "limit": "No se preservó respuesta POST"},
    {"schema_id": "RI168_02", "capture": "2010-07-29", "surface": "resoluciones.asp", "element": "field", "name_or_value": "txtNumero", "semantics": "número", "proof": "input text", "limit": "Sin resultado target"},
    {"schema_id": "RI168_03", "capture": "2010-07-29", "surface": "resoluciones.asp", "element": "field", "name_or_value": "cboAnio", "semantics": "año 1993-2010 o todos", "proof": "incluye 2008 y 2009", "limit": "Catálogo dinámico no exportado"},
    {"schema_id": "RI168_04", "capture": "2010-07-29", "surface": "resoluciones.asp", "element": "field", "name_or_value": "calDesde/calHasta", "semantics": "rango de fechas", "proof": "campos fecha", "limit": "Valores por defecto"},
    {"schema_id": "RI168_05", "capture": "2010-07-29", "surface": "resoluciones.asp", "element": "field", "name_or_value": "txtKeywords", "semantics": "palabras clave", "proof": "input text", "limit": "Sin índice invertido"},
    {"schema_id": "RI168_06", "capture": "2010-07-29", "surface": "resoluciones.asp", "element": "field", "name_or_value": "hdnAccion=Filtrar", "semantics": "acción", "proof": "hidden input", "limit": "No reconstruye respuesta"},
    {"schema_id": "RI168_07", "capture": "2012-02-05", "surface": "resoluciones.asp", "element": "control", "name_or_value": "mismo esquema; años 1993-2012", "semantics": "continuidad", "proof": "campos y endpoint estables", "limit": "No prueba exhaustividad"},
    {"schema_id": "RI168_08", "capture": "2010-07-29", "surface": "normativa.asp", "element": "routes", "name_or_value": "normas01.asp..normas05.asp", "semantics": "familias normativas", "proof": "cinco enlaces", "limit": "No es libro de resoluciones"},
]
write_csv(HERE / "E0_SIGEN_RESOLUTION_INDEX_SCHEMA_V168.csv", schema)

body_status = [
    {"object": "plananual2009.asp", "exact_route": "http://www.sigen.gov.ar:80/plananual2009.asp", "public_archive": "5 Wayback captures 2009-02-21 to 2010-01-18", "local_copy": "YES", "status": "PAGE_LOCATED", "proof_or_limit": "Página e inventario; no cuerpo PDF"},
    {"object": "Plan SIGEN 2009", "exact_route": "documentacion/plananualpdfs/Plan SIGEN 2009.pdf", "public_archive": "No capture in Wayback/Common Crawl/Arquivo.pt queries", "local_copy": "NO", "status": "BODY_NOT_LOCATED", "proof_or_limit": "Negativo limitado a índices/replay"},
    {"object": "Anexo F cuadros 8-18", "exact_route": "documentacion/plananualpdfs/Anexo F - Cuadro N - título.pdf", "public_archive": "Links exactos; cuerpos no capturados", "local_copy": "NO", "status": "LINK_INVENTORY_LOCATED_BODIES_OPEN", "proof_or_limit": "11 cuadros; no contenido"},
    {"object": "Anexo G capacitación", "exact_route": "documentacion/plananualpdfs/Anexo G - Capacitacion 2009.pdf", "public_archive": "Link exacto; cuerpo no capturado", "local_copy": "NO", "status": "LINK_LOCATED_BODY_OPEN", "proof_or_limit": "Evitar trasposición con Plan 2010"},
    {"object": "Plan Red Federal 2009", "exact_route": "documentacion/plananualpdfs/planred2009.pdf", "public_archive": "Link exacto; cuerpo no capturado", "local_copy": "NO", "status": "LINK_LOCATED_BODY_OPEN", "proof_or_limit": "Documento distinto del Plan SIGEN"},
]
write_csv(HERE / "E0_PLAN_2009_BODY_RECOVERY_STATUS_V168.csv", body_status)

# Freeze public-search outcomes with scope-correct negatives.
search = [
    {"search_id": "PS168_01", "surface": "Internet Archive CDX", "query_or_url": "plananual2009.asp 2008-2012", "result": "5 HTTP-200 captures: 20090221, 20090324, 20091116, 20091218, 20100118", "classification": "TARGET_PAGE_CAPTURES_LOCATED", "next_step": "preserve earliest payload"},
    {"search_id": "PS168_02", "surface": "Internet Archive replay", "query_or_url": "20090221151746id_/plananual2009.asp", "result": "official page and 14 links recovered", "classification": "OFFICIAL_PAGE_RECOVERED", "next_step": "request bodies by exact filenames"},
    {"search_id": "PS168_03", "surface": "Internet Archive CDX/replay", "query_or_url": "Plan SIGEN 2009.pdf and plananualpdfs prefix", "result": "no catalog capture; exact replays return archive 404", "classification": "BODY_ARCHIVE_NEGATIVE_SCOPED", "next_step": "institutional custody"},
    {"search_id": "PS168_04", "surface": "Arquivo.pt", "query_or_url": "exact Plan SIGEN 2009.pdf", "result": "estimated results 0", "classification": "SECOND_ARCHIVE_NEGATIVE_SCOPED", "next_step": "do not infer nonexistence"},
    {"search_id": "PS168_05", "surface": "Common Crawl 2009-2010/2012", "query_or_url": "Result_resoluciones.asp*", "result": "no captures; historical form used POST", "classification": "DYNAMIC_RESULT_NOT_ARCHIVED", "next_step": "request export or registry"},
    {"search_id": "PS168_06", "surface": "Common Crawl 2009-2010/2012", "query_or_url": "resoluciones_sigen/*", "result": "6 and 4 PDFs; none target 2008", "classification": "PARTIAL_DIRECTORY_CAPTURE_NOT_INVENTORY", "next_step": "do not treat crawl as register"},
    {"search_id": "PS168_07", "surface": "Internet Archive CDX", "query_or_url": "resoluciones_sigen/* 2008-2012", "result": "10 URLs; none Plan 2009 approval", "classification": "PARTIAL_DIRECTORY_CAPTURE_NOT_INVENTORY", "next_step": "query register by date/subject"},
    {"search_id": "PS168_08", "surface": "Boletín Oficial", "query_or_url": "Primera Sección 2008-12-15", "result": "no SIGEN plan-approval resolution in daily list", "classification": "PUBLICATION_NEGATIVE_DATE_SCOPED", "next_step": "seek internal act or other publication date"},
    {"search_id": "PS168_09", "surface": "SIGEN Memoria 2008", "query_or_url": "Plan SIGEN 2009 approval", "result": "approval 2008-12-15 and SIGEN/UAI scope", "classification": "CONTEMPORARY_APPROVAL_REFERENCE", "next_step": "recover instrument"},
    {"search_id": "PS168_10", "surface": "Internet Archive + Common Crawl", "query_or_url": "SIGEN URL variants 3672/Nota/GSEyP 2008-2015", "result": "no public URL capture", "classification": "NOTE_URL_ARCHIVE_NEGATIVE_SCOPED", "next_step": "Mesa, COMDOC, archivo, SISIO"},
    {"search_id": "PS168_11", "surface": "old live SIGEN host", "query_or_url": "resoluciones.asp / Result_resoluciones.asp", "result": "connection unavailable", "classification": "SERVICE_UNAVAILABLE_NOT_NEGATIVE", "next_step": "archive and institutional channels"},
]
write_csv(HERE / "V168_PUBLIC_SEARCH_LOG.csv", search)
write_csv(HERE / "E0_PLAN_2009_ARCHIVE_CANDIDATE_MATRIX_V168.csv", search)

approval = [
    {"test_id": "AA168_01", "question": "¿Se aprobó el Plan SIGEN 2009?", "evidence": "Memoria SIGEN 2008", "result": "Sí, 15/12/2008", "classification": "FACT_CONFIRMED", "remaining_gap": "instrumento, número, expediente, firma"},
    {"test_id": "AA168_02", "question": "¿La página 2009 identifica el acto?", "evidence": "plananual2009.asp", "result": "No; enlaza plan y anexos", "classification": "PAGE_SILENT_ON_ACT", "remaining_gap": "registro de aprobación"},
    {"test_id": "AA168_03", "question": "¿El BO del 15/12/2008 publicó resolución SIGEN aprobatoria?", "evidence": "sumario oficial", "result": "No aparece", "classification": "DATE_SCOPED_PUBLICATION_NEGATIVE", "remaining_gap": "otras fechas o acto interno"},
    {"test_id": "AA168_04", "question": "¿Existía buscador SIGEN por fecha, número y tema?", "evidence": "resoluciones.asp 2010", "result": "Sí", "classification": "HISTORICAL_REGISTRY_SCHEMA_LOCATED", "remaining_gap": "respuesta POST/exportación"},
    {"test_id": "AA168_05", "question": "¿Puede afirmarse acto interno?", "evidence": "cruce memoria, página, BO e índice", "result": "Sólo hipótesis prioritaria", "classification": "INFERENCE_NOT_FACT", "remaining_gap": "acto o certificación"},
]
write_csv(HERE / "E0_PLAN_2009_APPROVAL_ACT_SEARCH_V168.csv", approval)

note_search = [
    {"route_id": "N168_01", "surface": "CGN Cuenta 2009 UEPEX", "target": "Nota SIGEN 3672/09 GSEyP", "result": "referencia, firmante e instrucción SISIO", "status": "REFERENCE_LOCATED_BODY_OPEN", "required_record": "nota, anexos, distribución, acuses"},
    {"route_id": "N168_02", "surface": "Internet Archive CDX", "target": "URLs SIGEN *3672*", "result": "0 captures", "status": "URL_INDEX_NEGATIVE_SCOPED", "required_record": "salida/Mesa/COMDOC"},
    {"route_id": "N168_03", "surface": "Common Crawl 2009-2010", "target": "URLs SIGEN *3672*", "result": "No Captures found", "status": "URL_INDEX_NEGATIVE_SCOPED", "required_record": "salida/Mesa/COMDOC"},
    {"route_id": "N168_04", "surface": "Common Crawl 2012", "target": "URLs SIGEN *3672*", "result": "No Captures found", "status": "LATE_URL_INDEX_NEGATIVE_SCOPED", "required_record": "salida/Mesa/COMDOC"},
    {"route_id": "N168_05", "surface": "SISIO", "target": "hallazgos 0120/09 y 3672/09", "result": "sin id público", "status": "SYSTEM_ENTRY_NOT_LOCATED", "required_record": "exportación, historial, vínculos"},
]
write_csv(HERE / "E0_NOTE_3672_ARCHIVAL_SEARCH_V168.csv", note_search)

gate = read_csv(PARENT / "E0_PLAN_2009_ANNEX_G_PUBLIC_NEGATIVE_AND_EXACT_DATE_GATE_V167.csv")
gate.extend([
    {"row_id": "DG168_14", "question": "¿Se recuperó la página oficial del año objetivo?", "public_result": "Sí", "proved_fact": "Ruta y 14 enlaces", "remaining_gap": "cuerpos PDF", "required_record": "plan y anexos", "status": "TARGET_PAGE_CLOSED_BODY_OPEN"},
    {"row_id": "DG168_15", "question": "¿Qué era el Anexo G 2009?", "public_result": "Plan de capacitación", "proved_fact": "nombre exacto", "remaining_gap": "contenido", "required_record": "Anexo G - Capacitacion 2009.pdf", "status": "ANNEX_IDENTITY_CLOSED_BODY_OPEN"},
    {"row_id": "DG168_16", "question": "¿Se recuperó el acto aprobatorio?", "public_result": "No", "proved_fact": "aprobación 15/12/2008; sin resolución SIGEN en BO diario", "remaining_gap": "instrumento", "required_record": "acto, expediente o certificación", "status": "APPROVAL_REFERENCE_ONLY"},
])
write_csv(HERE / "E0_PLAN_2009_ANNEX_G_PUBLIC_NEGATIVE_AND_EXACT_DATE_GATE_V168.csv", gate)

method_breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V168.csv")
method_breaks.extend([
    {"break_id": "target_page_not_target_body", "dimension": "document", "problem": "La página 2009 prueba rutas y títulos, no PDFs.", "rule": "Separar PAGE_LOCATED de BODY_NOT_LOCATED.", "status": "FROZEN_V168", "evidence": "Wayback plananual2009.asp"},
    {"break_id": "post_search_form_not_result_inventory", "dimension": "archive", "problem": "Formulario capturado; resultados POST no.", "rule": "Pedir/exportar registro; no reconstruir resultados.", "status": "FROZEN_V168", "evidence": "Common Crawl resoluciones.asp"},
    {"break_id": "bo_date_negative_not_internal_act_negative", "dimension": "legal", "problem": "Ausencia en BO del día no excluye acto interno u otra fecha.", "rule": "Negativo de publicación fechado, no emisión.", "status": "FROZEN_V168", "evidence": "BO 15/12/2008 + Memoria"},
    {"break_id": "archive_url_negative_not_note_nonexistence", "dimension": "archive", "problem": "Nota 3672/09 puede no haber tenido URL.", "rule": "Buscar Mesa, COMDOC, archivo y SISIO.", "status": "FROZEN_V168", "evidence": "IA/CC URL queries"},
])
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V168.csv", method_breaks)

# Preserve unchanged banking state.
write_csv(HERE / "CURRENT_STATE_V168.csv", read_csv(PARENT / "CURRENT_STATE_V167.csv"))
write_csv(HERE / "FOUR_LEG_PASS_PANEL_V168.csv", read_csv(PARENT / "FOUR_LEG_PASS_PANEL_V167.csv"))
coverage_rows = read_csv(PARENT / "STRICT_Q4_FOUR_LEG_COVERAGE_V167.csv")
coverage_rows[0]["coverage_set"] = "V168 strict 34-entity set; unchanged from V167"
coverage_rows[0]["v161_change"] = "V168: no banking promotion; numerator and coverage unchanged from V167."
write_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V168.csv", coverage_rows)

recovery_note = """# Recuperación archivística Plan SIGEN 2009 · V168

V168 recupera por primera vez la página oficial exacta `plananual2009.asp`, preservada por Internet Archive el 21-02-2009. La captura enlaza catorce documentos: `Plan SIGEN 2009.pdf`, once cuadros del Anexo F —8 a 18—, `Anexo G - Capacitacion 2009.pdf` y `planred2009.pdf`. Quedan cerradas la URL, la convención de nombres y la identidad del Anexo G; no se declaran recuperados los cuerpos porque esos PDFs no aparecen en los catálogos o replays consultados.

También se recuperaron dos generaciones del buscador oficial de resoluciones y el índice normativo. El formulario admitía número, año, rango de fechas y palabras clave, mediante POST a `Result_resoluciones.asp`, pero las respuestas dinámicas no fueron archivadas. El Boletín Oficial del 15-12-2008 no muestra una resolución SIGEN aprobatoria; unido a la Memoria, esto prioriza —sin probar— la hipótesis de un acto interno o de otra fecha de publicación.

Las búsquedas archivísticas por `3672`, `Nota` y `GSEyP` no localizaron URL pública. La ruta principal sigue siendo Mesa de Entradas, registro de salida/COMDOC, archivo y SISIO. Plan, anexos, acto, Nota 3672/09 e ids SISIO permanecen abiertos. SAF355 0/5, ejecución bancaria 0/10 y seis solicitudes DRAFT_NOT_SENT.
"""
for name in ("E0_PLAN_2009_ARCHIVE_RECOVERY_NOTE_V168.md", "E0_SIGEN_ARCHIVAL_INDEX_RECOVERY_NOTE_V168.md", "E0_FISCAL_RECONSTRUCTION_V168.md"):
    (HERE / name).write_text(recovery_note, encoding="utf-8")
(HERE / "CNV_ATTACHMENT_ANALYTIC_REVIEW_V168.md").write_text(f"""# Revisión analítica acumulada V168

Panel congelado: 34 entidades y {COVERAGE}% de activos. V168 recupera página Plan 2009, 14 enlaces y esquema del buscador de resoluciones. No recupera PDFs, acto, Nota 3672/09 ni ids SISIO. Seis pedidos DRAFT_NOT_SENT; SAF355 0/5 y ejecución 0/10.
""", encoding="utf-8")

# Source synchronization.
bundle_specs = [
    ("SIGEN_PLAN_2009_TARGET_PAGE", PLAN_PAGE, "http://www.sigen.gov.ar:80/plananual2009.asp"),
    ("SIGEN_RESOLUTION_SEARCH_2010", RES_2010, "http://www.sigen.gov.ar/resoluciones.asp"),
    ("SIGEN_NORMATIVE_INDEX_2010", NORM_2010, "http://www.sigen.gov.ar/normativa.asp"),
    ("SIGEN_RESOLUTION_SEARCH_2012", RES_2012, "http://www.sigen.gov.ar/resoluciones.asp"),
    ("SIGEN_MEMORY_2008_APPROVAL", CYCLE / "inputs/historical_retrieval/v157/binaries/sigen_memoria_2008_plan_2009_approval.pdf", "https://www.argentina.gob.ar/sites/default/files/memoria_sigen_2008.pdf"),
    ("CGN_ACCOUNT_2009_NOTE_3672", CYCLE / "inputs/historical_retrieval/v155/binaries/cgn_cuenta_2009_uepex_note_sisio_chain.pdf", "https://www.economia.gob.ar/hacienda/cgn/cuenta/2009/archivos/sep.pdf"),
]
bundle = []
for role, path, url in bundle_specs:
    assert path.is_file()
    bundle.append({"role": role, "path": "/" + path.relative_to(REPO).as_posix(), "url": url, "bytes": str(path.stat().st_size), "sha256": sha256(path), "analytic_use": "Plan 2009 / acto / registro / Nota 3672 V168"})
write_csv(HERE / "V168_SOURCE_BUNDLE.csv", bundle)

SYNC.mkdir(parents=True, exist_ok=True)
sync_rows = []
for row in new_sources:
    path = REPO / row["archivo_local"].lstrip("/")
    verification = "HTML_OFFICIAL_PAGE_CONTENT_ASSERTED" if path.suffix == ".html" else "GZIP_MAGIC_ARC_RECORD_DECOMPRESSED_AND_CONTENT_ASSERTED"
    sync_rows.append({"role": "ARCHIVED_OFFICIAL_SIGEN_PAGE_OR_INDEX", "relative_path": row["archivo_local"], "source_url": row["url_original"], "size_bytes": str(path.stat().st_size), "sha256": sha256(path), "format_verification": verification})
write_csv(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V168.csv", sync_rows)
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V168.csv", search)
(SYNC / "SOURCE_SYNC_REPORT_V168.md").write_text("""# Sincronización incremental de fuentes · V168

- Catálogo: 591/591 copias locales y SHA-256 válido; brecha 0.
- Nuevas: página Plan 2009, dos buscadores de resoluciones y un índice normativo.
- Verificados formato, URL, timestamp, formulario y 14 enlaces.
- PDFs, acto, Nota 3672/09 e ids SISIO siguen abiertos.
""", encoding="utf-8")
(SYNC / "qa_source_sync_v168.py").write_text("""from pathlib import Path
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
""", encoding="utf-8")

# Summaries and completeness.
(HERE / "README_V168.md").write_text(f"""# Checkpoint V168

- Archivo: 591/591 copias locales con hash válido; +4 capturas SIGEN.
- Plan 2009: página exacta recuperada; 14 enlaces identificados.
- Cuerpos: plan, Anexo F 8-18, Anexo G capacitación y Plan Red no capturados.
- Aprobación: 15/12/2008 confirmada; acto/número/expediente no localizados. El BO del día no publica resolución SIGEN: negativo fechado solamente.
- Nota 3672/09: referencia contemporánea; cuerpo, salida e ids SISIO no localizados.
- Panel: 34 entidades; activos {NUMERATOR}/{SYSTEM_ASSETS}; cobertura {COVERAGE}%.
- SAF355 0/5; ejecución 0/10; seis borradores no enviados.
""", encoding="utf-8")
(HERE / "VEREDICTO_V168.md").write_text("""# Veredicto V168

Avance sustantivo: se cierra la página del año objetivo, la ruta del plan y el inventario de catorce documentos. No se cierra el cuerpo. El buscador histórico prueba capacidad de filtrar por año, fecha, número y tema, pero su respuesta POST no fue archivada. Acto, Nota 3672/09, SISIO, SAF355 y ejecución bancaria siguen abiertos. Sin promoción ni solicitud enviada.
""", encoding="utf-8")
(HERE / "AUDITORIA_V168.md").write_text(f"""# Auditoría V168

- Catálogo/copia/hash: 591/591; huecos 0; nuevas 4.
- Página 2009: HTML 23.667 bytes, 14 enlaces, 11 cuadros F 8-18.
- Índices: 3/3 ARC.GZ válidos; formularios 2010/2012 y normativa verificados.
- Guardas: página ≠ cuerpo; formulario ≠ resultados; BO fechado ≠ inexistencia.
- Panel 34, {COVERAGE}%; promociones 0; solicitudes 0; SAF355 0/5; ejecución 0/10.
""", encoding="utf-8")
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V168_A_V169.md").write_text("""# Handover V168 → V169

## Cerrado

- Página Plan SIGEN 2009 y 14 enlaces exactos.
- Esquema del buscador de resoluciones y familias normativas.
- Archivo 591/591; panel 34 sin cambio.

## Prioridad V169

1. Buscar los 14 PDFs por espejos, respaldos y referencias; link no es cuerpo.
2. Reconstruir registro del 15/12/2008 y recuperar acto, expediente y comunicación UAI Economía.
3. Buscar Nota 3672/09 en Mesa/COMDOC/archivo y enlazar ids SISIO.
4. Mantener seis borradores DRAFT_NOT_SENT, SAF355 0/5 y ejecución 0/10.
""", encoding="utf-8")

refs = HERE / "SOURCE_REFERENCES_V168.md"
with refs.open("a", encoding="utf-8") as handle:
    handle.write("\n## V168 · página Plan 2009 e índices SIGEN\n")
    for row in new_sources:
        handle.write(f"\n- `{row['id']}` · {row['titulo']} · {row['url_original']} · `{row['archivo_local']}` · `{row['sha256']}`\n")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V167.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint": "V168", "date": "2026-08-31", "master_catalog_entries": 591, "physical_local_copies": 591,
    "physical_local_hash_ok": 591, "remaining_catalog_physical_or_hash_gaps": 0,
    "state": "SOURCE_ARCHIVE_COMPLETE_PLAN2009_PAGE_AND_LINK_INVENTORY_RECOVERED_BODIES_OPEN",
    "analytical_promotion": "NONE_V168_ARCHIVAL_PAGE_ONLY", "exact_entities": 34,
    "strict_asset_numerator_million_ars": NUMERATOR, "system_assets_million_ars": SYSTEM_ASSETS,
    "strict_coverage_pct": COVERAGE, "strict_coverage_increment_v167_pp": "0",
    "request_drafts_status": "DRAFT_NOT_SENT", "requests_submitted": 0, "responses_received": 0,
    "saf355_certifications_located": 0, "executed_historical_bank_rows_confirmed": 0,
    "discovered_official_binary_recovery_queue": 0, "plan_sigen_2009_page_located": True,
    "plan_sigen_2009_link_inventory_count": 14, "plan_sigen_2009_body_located": False,
    "plan_sigen_2009_approval_act_located": False, "note_3672_09_body_located": False, "new_archival_captures": 4,
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V168.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Provenance and global inventories.
archival = read_csv(HERE / "ARCHIVAL_PROVENANCE_V168.csv")
meta = [
    (new_sources[0], "https://web.archive.org/web/20090221151746id_/http://www.sigen.gov.ar:80/plananual2009.asp", "20090221151746", "LCFKEDKVDYP2SQZNCKHBYMGCKAVPWJKL", "Wayback target page; bodies not embedded."),
    (new_sources[1], "https://data.commoncrawl.org/crawl-002/2010/08/09/45/1281356492042_45.arc.gz", "20100729123051", "DS4A244X5S6LBI3BYFLBCT7TVHOSXTYL", "ARC offset 46589177 length 5762; resolution form."),
    (new_sources[2], "https://data.commoncrawl.org/crawl-002/2010/08/09/45/1281356492042_45.arc.gz", "20100729122954", "TT7H7GRUEOJJCKHAYE3N2DCF6XCUNBWY", "ARC offset 46532340 length 4451; normative index."),
    (new_sources[3], "https://data.commoncrawl.org/parse-output/segment/1346981172239/1346997034768_1883.arc.gz", "20120205011945", "FTP2I3VTRACH33WOWPB7GTFZNT3ZPLYD", "ARC offset 82161832 length 6005; continuity control."),
]
for source, retrieval, timestamp, digest, note in meta:
    path = REPO / source["archivo_local"].lstrip("/")
    archival.append({"source_id": source["id"], "original_url": source["url_original"], "retrieval_url": retrieval, "capture_timestamp": timestamp, "cdx_digest": digest, "local_path": source["archivo_local"], "sha256": source["sha256"], "bytes": str(path.stat().st_size), "provenance_note": note})
write_csv(HERE / "ARCHIVAL_PROVENANCE_V168.csv", archival)

origin_rows = read_csv(ORIGINS)
origin_by_path = {row["path"]: row for row in origin_rows}
for path in iter_files(HIST.parent):
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path": rel, "origin": "downloaded/preserved V168", "note": "Wayback/Common Crawl official SIGEN content"}
for path in iter_files(SYNC):
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path": rel, "origin": "generated/updated V168", "note": "incremental archival synchronization"}
for path in sorted(HERE.iterdir(), key=lambda item: item.name.casefold()):
    if path.is_file():
        rel = path.relative_to(CYCLE).as_posix()
        origin_by_path[rel] = {"path": rel, "origin": "generated/updated V168", "note": "Plan 2009 page checkpoint"}
for path in (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V168.csv", AUDIT / "SOURCE_BACKUP_CENSUS_V168.csv", AUDIT / "SOURCE_PRESERVATION_MISSING_V168.csv", AUDIT / "CURRENT_SOURCE_COMPLETENESS_V168.json"):
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path": rel, "origin": "generated/updated V168", "note": "591-source completeness"}
write_csv(ORIGINS, list(origin_by_path.values()), ["path", "origin", "note"])

transparency = CYCLE / "TRANSPARENCY_README.md"
text = transparency.read_text(encoding="utf-8-sig")
if "## V168 · Página oficial Plan SIGEN 2009" not in text:
    text += """

## V168 · Página oficial Plan SIGEN 2009

Internet Archive conserva cinco capturas de `plananual2009.asp`; la primera fue preservada y enumera catorce documentos: plan, Anexo F 8-18, Anexo G capacitación y Plan Red. Los PDFs no aparecen en los archivos consultados. Common Crawl conserva el formulario histórico de resoluciones, pero no sus respuestas POST. La Memoria confirma aprobación el 15-12-2008; el BO del día no publica resolución SIGEN, negativo fechado que no descarta acto interno. Nota 3672/09 e ids SISIO siguen abiertos. Archivo 591/591; panel 34 sin cambio.
"""
    transparency.write_text(text, encoding="utf-8")

(REPO / "BACKUP_ACTUALIZACION_2026-08-31.md").write_text(f"""# Backup de actualización · 2026-08-31

- Checkpoint: V168.
- Fuentes: 591/591; +4 capturas SIGEN.
- Plan 2009: página y 14 enlaces; cuerpos, acto y Nota abiertos.
- Panel: 34; {COVERAGE}% de activos; promociones 0.
- Solicitudes: 0 enviadas; seis DRAFT_NOT_SENT.
""", encoding="utf-8")

(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")

files = [{"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)} for path in sorted(HERE.iterdir(), key=lambda item: item.name.casefold()) if path.is_file() and path.name != "MANIFEST_V168.json"]
manifest = {
    "checkpoint": "V168", "parent_checkpoint": "V167", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "exact_entities": 34, "strict_coverage_pct": COVERAGE, "strict_asset_numerator_million_ars": NUMERATOR,
    "system_assets_million_ars": SYSTEM_ASSETS, "new_promotions": [],
    "historical_finding": "Official Plan SIGEN 2009 page and 14-link inventory recovered; bodies absent",
    "source_archive": "591/591 catalogued physical SHA-valid; four SIGEN archival objects added",
    "plan_sigen_2009_page": "LOCATED", "plan_sigen_2009_body": "NOT_LOCATED", "approval_act": "NOT_LOCATED",
    "note_3672_09_body": "NOT_LOCATED", "crosswalk_gate": "OPEN", "closed_network_gate": "NO",
    "saf355_certifications": "0/5", "executed_historical_bank_rows": "0/10", "requests_submitted": 0, "files": files,
}
(HERE / "MANIFEST_V168.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in iter_files(REPO) if path != global_manifest]
payload = {
    "checkpoint": "V168", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": COVERAGE, "exact_entities": 34, "closed_network_gate": "NO",
    "source_audit": "591 master; 591 physical SHA-valid; four historical SIGEN captures added",
    "historical_workstream": "Plan 2009 page/link inventory recovered; bodies, act, Note 3672, SISIO and execution open; six drafts not sent",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
tmp = global_manifest.with_suffix(".json.V168tmp")
tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
tmp.replace(global_manifest)

print("V168 BUILD PASS · catalog=591/591 · archival_objects=4 · plan_page=located · plan_body=open · exact=34 · requests=0")
