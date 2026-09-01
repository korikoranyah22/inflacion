from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
from pathlib import Path
import csv
import hashlib
import json
import os
import re


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
PARENT = CYCLE / "checkpoints" / "V168"
AUDIT = CYCLE / "source_audit"
SYNC = CYCLE / "inputs" / "source_sync" / "v169"
HIST = CYCLE / "inputs" / "historical_retrieval" / "v169" / "binaries"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"

INFOLEG_INDEX = HIST / "infoleg_actos_gobierno_index_2008_2010.html"
WAYBACK_LATE = HIST / "wayback_sigen_planannualpdfs_2013_2020.json"
ENARGAS_INDEX = HIST / "enargas_informe_anual_2009_index.html"
ENARGAS_CHAPTER = HIST / "enargas_informe_anual_2009_capitulo1_official.pdf"
ENARGAS_FULL = HIST / "enargas_informe_anual_2009.pdf"
EXPECTED = {
    INFOLEG_INDEX: (76326, "a9be89b0b86c183826ae0f08e50da250c82a6ac92b0acf6aaea26e62705796b5"),
    WAYBACK_LATE: (4592, "fe458c7aee86ceb2230d02095055117ad61a565b844520e7529ab180110d9200"),
    ENARGAS_INDEX: (10221, "cfebd52eba88ad607edfb47b1f84ec8bae474d83d9ce6ac2290395ee52e94540"),
    ENARGAS_CHAPTER: (3094747, "41eefe2f80fa26b355ab8c54b58fa61fbf1650ee74326d89f67488fde6f8d9f5"),
    ENARGAS_FULL: (8934599, "e29c6ae545d829daa172bc0ae882cabffdc4308a533b79be3447c4ad459f0686"),
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
    skip_prefixes = ("build_", "qa_")
    skip_names = {
        "MANIFEST_V168.json", "README_V168.md", "VEREDICTO_V168.md", "AUDITORIA_V168.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V168_A_V169.md", "V168_SOURCE_BUNDLE.csv",
        "V168_PUBLIC_SEARCH_LOG.csv", "V168_PDF_VISUAL_AND_TEXT_CONTROL.csv",
        "E0_PLAN_2009_ARCHIVE_RECOVERY_NOTE_V168.md", "E0_SIGEN_ARCHIVAL_INDEX_RECOVERY_NOTE_V168.md",
        "E0_FISCAL_RECONSTRUCTION_V168.md", "CNV_ATTACHMENT_ANALYTIC_REVIEW_V168.md",
    }
    for source in sorted(PARENT.iterdir(), key=lambda path: path.name.casefold()):
        if not source.is_file() or source.name in skip_names or source.name.startswith(skip_prefixes):
            continue
        target = HERE / source.name.replace("V168", "V169")
        target.write_text(source.read_text(encoding="utf-8-sig").replace("V168", "V169"), encoding="utf-8")


clone_parent()

for path, (size, digest) in EXPECTED.items():
    assert path.is_file() and path.stat().st_size == size and sha256(path) == digest
assert ENARGAS_CHAPTER.read_bytes().startswith(b"%PDF-")
assert ENARGAS_FULL.read_bytes().startswith(b"%PDF-")

infoleg_text = INFOLEG_INDEX.read_text(encoding="utf-8", errors="replace")
headings = [unescape(re.sub(r"<[^>]+>", "", item)).strip() for item in re.findall(r"(?is)<h2[^>]*>(.*?)</h2>", infoleg_text)]
links = [unescape(re.sub(r"<[^>]+>", "", item)).strip() for item in re.findall(r"(?is)<a[^>]*>(.*?)</a>", infoleg_text)]
sigen_plan_titles = [item for item in links if "SINDICATURA GENERAL DE LA NACION" in item.upper()]
assert len(headings) == 78
assert headings[0].endswith("08/03/2010") and headings[-1].endswith("15/09/2008")
assert sigen_plan_titles == [
    "PLAN 2010 DE LA SINDICATURA GENERAL DE LA NACION (SEGUNDA Y ULTIMA PARTE)",
    "PLAN 2010 DE LA SINDICATURA GENERAL DE LA NACION (PRIMERA PARTE)",
    "PLAN 2008 SINDICATURA GENERAL DE LA NACION",
]
assert "PLAN SIGEN 2009" not in infoleg_text.upper()

wayback = json.loads(WAYBACK_LATE.read_text(encoding="utf-8"))
assert wayback[0] == ["timestamp", "original", "statuscode", "mimetype", "digest", "length"]
late_rows = wayback[1:]
late_urls = [row[1] for row in late_rows]
assert len(late_rows) == 25 and all(row[2] == "200" and row[3] == "application/pdf" for row in late_rows)
assert {row[0][:4] for row in late_rows} == {"2014", "2016"}
assert any("/2013/" in url for url in late_urls) and any("/2015/" in url for url in late_urls)
assert not any("2009" in url.lower() or "plan sigen 2009" in url.lower() for url in late_urls)

enargas_index_text = ENARGAS_INDEX.read_text(encoding="utf-8", errors="replace")
assert "Informe de balance y gestión 2009" in enargas_index_text
assert "2009-Capitulo1" in enargas_index_text and "informe-completo-2009.zip" in enargas_index_text

catalog = read_csv(CATALOG)
catalog_fields = list(catalog[0])
new_sources = [
    {
        "id": "infoleg_actos_gobierno_index_2008_2010_v169", "tema": "ciclo_ajuste_historico",
        "institucion": "InfoLEG · Suplemento Actos de Gobierno",
        "titulo": "Índice oficial de Actos de Gobierno · 15-09-2008 a 08-03-2010",
        "url_original": "https://www.infoleg.gob.ar/?page_id=842",
        "archivo_local": "/" + INFOLEG_INDEX.relative_to(REPO).as_posix(), "fecha_descarga": "2026-08-31",
        "fecha_publicacion": "2008-09-15/2010-03-08", "codigo_serie": "ACTOS-DE-GOBIERNO-INDEX",
        "periodo_utilizado": "2008-2010", "tipo": "HTML oficial · índice de 78 suplementos",
        "sha256": EXPECTED[INFOLEG_INDEX][1],
        "nota": "V169: enumera Plan SIGEN 2008 y las dos partes del Plan 2010; no enumera Plan 2009. Negativo limitado a esta superficie editorial.",
    },
    {
        "id": "wayback_sigen_planannualpdfs_late_inventory_2013_2020_v169", "tema": "ciclo_ajuste_historico",
        "institucion": "SIGEN · metadatos Internet Archive",
        "titulo": "Inventario tardío Wayback de la carpeta plananualpdfs · consulta 2013-2020",
        "url_original": "https://web.archive.org/cdx/search/cdx?url=www.sigen.gov.ar/documentacion/plananualpdfs/*&output=json&from=2013&to=2020&filter=statuscode:200",
        "archivo_local": "/" + WAYBACK_LATE.relative_to(REPO).as_posix(), "fecha_descarga": "2026-08-31",
        "fecha_publicacion": "2014-08-09/2016-06-06", "codigo_serie": "WAYBACK-CDX-LATE-DIRECTORY",
        "periodo_utilizado": "2013-2020", "tipo": "JSON · inventario CDX preservado",
        "sha256": EXPECTED[WAYBACK_LATE][1],
        "nota": "V169: 25 capturas PDF HTTP 200 correspondientes a planes 2013-2015; no contiene los 14 cuerpos 2009. No es inventario exhaustivo del servidor.",
    },
    {
        "id": "enargas_informe_anual_2009_index_v169", "tema": "ciclo_ajuste_historico",
        "institucion": "ENARGAS",
        "titulo": "Página oficial del Informe de balance y gestión 2009",
        "url_original": "https://www.enargas.gob.ar/secciones/publicaciones/informes-anuales-de-balance-y-gestion/informe-anual.php?ano=informe-anual-2009",
        "archivo_local": "/" + ENARGAS_INDEX.relative_to(REPO).as_posix(), "fecha_descarga": "2026-08-31",
        "fecha_publicacion": "2009-2011", "codigo_serie": "ENARGAS-INFORME-ANUAL-2009",
        "periodo_utilizado": "2009", "tipo": "HTML oficial · índice y rutas de descarga",
        "sha256": EXPECTED[ENARGAS_INDEX][1],
        "nota": "V169: autentica Capítulo I y la descarga del informe completo; fuente de proveniencia para la tabla I-11.",
    },
    {
        "id": "enargas_informe_anual_2009_capitulo1_v169", "tema": "ciclo_ajuste_historico",
        "institucion": "ENARGAS",
        "titulo": "Informe anual ENARGAS 2009 · Capítulo I · Cuadro I-11",
        "url_original": "https://www.enargas.gob.ar/secciones/publicaciones/informes-anuales-de-balance-y-gestion/pdf/anuales/2009/Capitulo1.pdf",
        "archivo_local": "/" + ENARGAS_CHAPTER.relative_to(REPO).as_posix(), "fecha_descarga": "2026-08-31",
        "fecha_publicacion": "2009-2011", "codigo_serie": "ENARGAS-INFORME-2009-CAP1",
        "periodo_utilizado": "2009", "tipo": "PDF oficial · 48 páginas",
        "sha256": EXPECTED[ENARGAS_CHAPTER][1],
        "nota": "V169: página PDF 42 / impresa 52 empareja seis Notas SIGEN con seis Actuaciones ENARGAS. La copia seccionada presenta recorte visual; texto cotejado con informe completo.",
    },
    {
        "id": "enargas_informe_anual_2009_full_mirror_v169", "tema": "ciclo_ajuste_historico",
        "institucion": "ENARGAS · espejo ARIAE",
        "titulo": "Informe anual ENARGAS 2009 completo · espejo de preservación",
        "url_original": "https://www.ariae.org/sites/default/files/2017-04/ENARGAS.IA_2009%20%20.pdf",
        "archivo_local": "/" + ENARGAS_FULL.relative_to(REPO).as_posix(), "fecha_descarga": "2026-08-31",
        "fecha_publicacion": "2009-2011", "codigo_serie": "ENARGAS-INFORME-2009-FULL-MIRROR",
        "periodo_utilizado": "2009", "tipo": "PDF institucional · espejo ARIAE · 337 páginas",
        "sha256": EXPECTED[ENARGAS_FULL][1],
        "nota": "V169: página PDF/impresa 52 permite control visual íntegro del Cuadro I-11. Autenticada por índice oficial y cotejo con capítulo oficial; ARIAE es espejo, no emisor.",
    },
]
catalog_by_id = {row["id"]: row for row in catalog}
for row in new_sources:
    catalog_by_id[row["id"]] = row
catalog = list(catalog_by_id.values())
write_csv(CATALOG, catalog, catalog_fields)
assert len(catalog) == 596 and len(catalog_by_id) == 596

audit_rows = []
for row in catalog:
    local = REPO / row["archivo_local"].lstrip("/")
    actual = sha256(local) if local.is_file() else ""
    audit_rows.append({
        "id": row["id"], "archivo_local": row["archivo_local"], "exists": str(local.is_file()),
        "sha_catalog": row["sha256"].lower(), "sha_actual": actual,
        "hash_ok": str(local.is_file() and bool(row["sha256"]) and actual == row["sha256"].lower()),
    })
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V169.csv", audit_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V169.csv", audit_rows)
missing = [row for row in audit_rows if row["exists"] != "True" or row["hash_ok"] != "True"]
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V169.csv", missing, list(audit_rows[0]))
assert not missing

late_scan = [
    {"scan_id": "LA169_01", "surface": "Wayback CDX", "period_or_collection": "2013-2020", "target": "www.sigen.gov.ar/documentacion/plananualpdfs/*", "result": "25 HTTP-200 PDF rows; plans 2013-2015 only", "classification": "LATE_DIRECTORY_CAPTURE_TARGET_2009_ABSENT_SCOPED", "service_state": "OK", "next_step": "institutional archive and mirrors"},
    {"scan_id": "LA169_02", "surface": "Wayback CDX", "period_or_collection": "2013-2020", "target": "Plan SIGEN 2009 + Anexo G + planred2009", "result": "not present among returned directory rows", "classification": "LATE_ARCHIVE_NEGATIVE_SCOPED", "service_state": "OK", "next_step": "do not infer deletion date"},
    {"scan_id": "LA169_03", "surface": "Common Crawl", "period_or_collection": "CC-MAIN-2013-20/2013-48/2014-10/2014-15", "target": "*.sigen.gov.ar/documentacion/plananualpdfs/*", "result": "No Captures found", "classification": "FOUR_COLLECTION_NEGATIVE_SCOPED", "service_state": "OK", "next_step": "other collections when service stable"},
    {"scan_id": "LA169_04", "surface": "Common Crawl", "period_or_collection": "catalog/full 2013-2020 retry", "target": "directory + exact main/annex G/plan red", "result": "catalog/index connection timed out; batch interrupted without completed export", "classification": "SERVICE_UNAVAILABLE_NOT_NEGATIVE", "service_state": "ERROR", "next_step": "rerun bounded yearly batches"},
    {"scan_id": "LA169_05", "surface": "InfoLEG Actos de Gobierno", "period_or_collection": "78 issues 2008-09-15 to 2010-03-08", "target": "Plan SIGEN annual publications", "result": "Plan 2008 and two Plan 2010 parts; no Plan 2009 title", "classification": "EDITORIAL_SURFACE_NEGATIVE_SCOPED", "service_state": "OK", "next_step": "request publication/custody certificate"},
    {"scan_id": "LA169_06", "surface": "public web exact-title search", "period_or_collection": "2026-08-31", "target": "four exact Plan 2009 filenames/titles", "result": "no target bodies; official Memory 2008 remained only exact approval reference", "classification": "SEARCH_ENGINE_NEGATIVE_SCOPED", "service_state": "OK", "next_step": "custody request by exact filenames"},
]
write_csv(HERE / "E0_PLAN_2009_LATE_ARCHIVE_COLLECTION_SCAN_V169.csv", late_scan)
write_csv(HERE / "V169_PUBLIC_SEARCH_LOG.csv", late_scan)

publication = [
    {"control_id": "PC169_01", "date_or_span": "2008-09-15", "surface": "InfoLEG Actos de Gobierno", "observed": "PLAN 2008 SINDICATURA GENERAL DE LA NACION", "meaning": "La superficie publicó el plan precedente", "limit": "No prueba regla anual obligatoria", "status": "PRECEDING_PUBLICATION_CONTROL"},
    {"control_id": "PC169_02", "date_or_span": "2008-12-15", "surface": "SIGEN Memoria 2008", "observed": "Plan SIGEN 2009 aprobado", "meaning": "Existencia y fecha confirmadas", "limit": "No identifica instrumento", "status": "TARGET_EXISTENCE_CONFIRMED"},
    {"control_id": "PC169_03", "date_or_span": "2008-12-15", "surface": "Boletín Oficial Primera Sección", "observed": "sin resolución SIGEN aprobatoria en lista diaria", "meaning": "No publicación ese día en esa sección", "limit": "No excluye acto interno u otra fecha", "status": "DATE_SCOPED_PUBLICATION_NEGATIVE"},
    {"control_id": "PC169_04", "date_or_span": "2008-09-15/2010-03-08", "surface": "InfoLEG Actos de Gobierno · 78 ediciones", "observed": "sin título Plan SIGEN 2009", "meaning": "Discontinuidad en esa superficie editorial", "limit": "No equivale a inexistencia ni no publicación universal", "status": "EDITORIAL_SURFACE_GAP"},
    {"control_id": "PC169_05", "date_or_span": "2010-02-22/2010-03-01", "surface": "InfoLEG Actos de Gobierno", "observed": "Plan 2010 primera y segunda parte", "meaning": "La superficie retomó difusión del plan siguiente", "limit": "No determina causa del hueco 2009", "status": "FOLLOWING_PUBLICATION_CONTROL"},
    {"control_id": "PC169_06", "date_or_span": "2014-2016 captures", "surface": "Wayback carpeta plananualpdfs", "observed": "planes 2013-2015; ningún cuerpo 2009", "meaning": "La carpeta y convención persistieron", "limit": "No fija cuándo ni por qué faltan cuerpos 2009", "status": "LATE_DIRECTORY_CONTINUITY_TARGET_ABSENT"},
]
write_csv(HERE / "E0_PLAN_2009_PUBLICATION_SURFACE_COMPARATOR_V169.csv", publication)

note_pairs = [
    ("1368/09", "8833/09", "Informe de Auditoría del Sistema de Transporte Norte"),
    ("1927/09", "11884/09", "Informe de Supervisión UAI"),
    ("2668/09", "16395/09", "Informe Compre Trabajo Argentino"),
    ("3159/09", "19970/09", "Informe de Actas Acuerdo UNIREN"),
    ("4986/09", "30571/09", "Evaluación del Sistema de Control Interno 2008"),
    ("5086/09", "30680/09", "Cumplimiento Plan Anual UAI enero-junio 2009"),
]
dual_rows = []
for index, (note, act, subject) in enumerate(note_pairs, 1):
    dual_rows.append({
        "row_id": f"DI169_{index:02}", "year": "2009", "sigen_note": note,
        "recipient_record_system": "Actuación ENARGAS", "recipient_record": act, "subject": subject,
        "source_location": "Informe ENARGAS 2009 · Cuadro I-11 · página impresa 52",
        "analytic_use": "Prueba contemporánea de doble identificador emisor/receptor",
        "target_limit": "No identifica actuación receptora de Nota 3672/09 ni prueba que el receptor usara idéntica serie",
        "status": "COMPARATOR_ONLY",
    })
write_csv(HERE / "E0_NOTE_3672_DUAL_IDENTIFIER_ROUTE_V169.csv", dual_rows)

note_route = read_csv(HERE / "E0_NOTE_3672_ARCHIVAL_SEARCH_V169.csv")
note_route.extend([
    {"route_id": "N169_06", "surface": "ENARGAS Informe 2009 Cuadro I-11", "target": "seis Notas SIGEN 2009", "result": "cada nota está emparejada con Actuación ENARGAS", "status": "RECIPIENT_DUAL_IDENTIFIER_PATTERN_PROVED", "required_record": "buscar asiento receptor target sin asumir numeración"},
    {"route_id": "N169_07", "surface": "CGN/Economía Mesa o COMDOC", "target": "Nota SIGEN 3672/09 GSEyP", "result": "número de entrada receptor no localizado", "status": "RECIPIENT_IDENTIFIER_OPEN", "required_record": "asiento de ingreso; fecha; remitente; asunto; pase; contenedor"},
])
write_csv(HERE / "E0_NOTE_3672_ARCHIVAL_SEARCH_V169.csv", note_route)

search_keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V169.csv")
search_keys.extend([
    {"key_id": "SK169_01", "request_id": "REQ160_SIGEN", "key_group": "dual_identifier", "exact_key": "Nota SIGEN 3672/09 GSEyP + actuación/asiento receptor", "search_purpose": "vincular salida SIGEN con ingreso del destinatario", "source_or_basis": "ENARGAS Informe 2009 Cuadro I-11", "caveat": "comparador ENARGAS; no trasladar su numeración"},
    {"key_id": "SK169_02", "request_id": "REQ157_SIGEN", "key_group": "exact_filename", "exact_key": "Plan SIGEN 2009.pdf; Anexo F Cuadros 8-18; Anexo G - Capacitacion 2009.pdf; planred2009.pdf", "search_purpose": "localizar 14 cuerpos por título/ruta exactos", "source_or_basis": "plananual2009.asp", "caveat": "enlace no equivale a cuerpo"},
    {"key_id": "SK169_03", "request_id": "REQ160_SIGEN", "key_group": "recipient_registry", "exact_key": "Nota 0120/09 DAIF; Nota 3672/09; SISIO; hallazgos Cuenta 2008", "search_purpose": "recuperar cadena remisión-respuesta-carga", "source_or_basis": "CGN Cuenta 2009 + comparador ENARGAS", "caveat": "pedir vínculos, no inferirlos"},
])
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V169.csv", search_keys)

request_objects = read_csv(HERE / "E0_V169_REQUEST_OBJECTS.csv")
request_objects.extend([
    {"row_id": "RO169_01", "object_id": "NOTE_3672_DUAL_IDENTIFIER", "custodian": "SIGEN + CGN/Economía Mesa/COMDOC", "exact_record": "salida Nota 3672/09 y actuación/asiento receptor correlacionado", "period": "2009", "minimum_fields": "fecha; remitente; destinatario; asunto; número de salida; número de ingreso; pases; contenedor; adjuntos; hash", "closure_rule": "Vínculo documental o certificación negativa fundada en ambos registros.", "status": "DRAFT_NOT_SENT"},
    {"row_id": "RO169_02", "object_id": "PLAN2009_PUBLICATION_CERT", "custodian": "SIGEN/Archivo General/Centro de Documentación", "exact_record": "certificación de publicación y custodia del Plan SIGEN 2009 y 14 cuerpos", "period": "2008-2010", "minimum_fields": "acto; fecha; versión; URL/ruta; baja/migración; soporte; ubicación; inventario; transferencia", "closure_rule": "Copia íntegra o certificado de búsqueda, transferencia y disposición.", "status": "DRAFT_NOT_SENT"},
    {"row_id": "RO169_03", "object_id": "PLAN2009_APPROVAL_REGISTER", "custodian": "SIGEN Mesa/Despacho/Archivo", "exact_record": "registro aprobatorio 15/12/2008 y comunicación a UAI Economía", "period": "2008-2009", "minimum_fields": "tipo; número; expediente; firmante; versión; anexos; distribución; acuses; asiento", "closure_rule": "Acto y cadena o certificación negativa por cada sistema consultado.", "status": "DRAFT_NOT_SENT"},
])
write_csv(HERE / "E0_V169_REQUEST_OBJECTS.csv", request_objects)
write_csv(HERE / "E0_V169_REQUEST_OBJECTS_V169.csv", request_objects)

method_breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V169.csv")
method_breaks.extend([
    {"break_id": "actos_gobierno_gap_not_universal_nonpublication", "dimension": "publication", "problem": "El índice publica Plan 2008 y Plan 2010 pero no Plan 2009.", "rule": "Tratar como hueco de esa superficie editorial; no como inexistencia o no publicación universal.", "status": "FROZEN_V169", "evidence": "InfoLEG Actos de Gobierno 78 ediciones"},
    {"break_id": "late_directory_absence_not_deletion_date", "dimension": "archive", "problem": "Capturas tardías de la carpeta contienen 2013-2015, no 2009.", "rule": "No inferir fecha o causa de retiro; pedir historial de migración/custodia.", "status": "FROZEN_V169", "evidence": "Wayback CDX 2013-2020"},
    {"break_id": "recipient_dual_id_comparator_not_target_id", "dimension": "identifier", "problem": "ENARGAS empareja notas SIGEN con actuaciones receptoras.", "rule": "Buscar doble clave para 3672/09 sin inventar serie o número CGN/Economía.", "status": "FROZEN_V169", "evidence": "ENARGAS Cuadro I-11"},
    {"break_id": "common_crawl_timeout_not_negative", "dimension": "archive", "problem": "El barrido ampliado no completó por indisponibilidad del índice.", "rule": "Registrar error de servicio y reintentar por lotes; no sumar negativo.", "status": "FROZEN_V169", "evidence": "V169 scan log"},
    {"break_id": "official_split_pdf_render_defect_mirror_not_emitter", "dimension": "format", "problem": "Capítulo oficial seccionado presenta recorte visual; espejo completo renderiza íntegro.", "rule": "Autenticar con índice oficial y cotejar ambos; identificar ARIAE como espejo.", "status": "FROZEN_V169", "evidence": "ENARGAS official chapter + full mirror"},
])
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V169.csv", method_breaks)

pdf_controls = [
    {"control_id": "PV169_01", "artifact": "enargas_informe_anual_2009_capitulo1_official.pdf", "page": "PDF 42 / impresa 52", "method": "Poppler 160 dpi + pypdf text", "target": "Cuadro I-11", "result": "TEXT_CONFIRMED_VISUAL_CLIPPING", "observation": "Seis pares extraíbles; copia oficial seccionada recorta visualmente parte de la columna izquierda."},
    {"control_id": "PV169_02", "artifact": "enargas_informe_anual_2009.pdf", "page": "PDF/impresa 52", "method": "Poppler 160 dpi original-detail + pypdf text", "target": "Cuadro I-11", "result": "PASS", "observation": "Tabla íntegra y legible; seis Notas SIGEN y seis Actuaciones ENARGAS."},
    {"control_id": "PV169_03", "artifact": "official chapter vs full mirror", "page": "42 vs 52", "method": "cotejo visual y textual", "target": "seis pares y objetos", "result": "CONTENT_MATCH", "observation": "Mismos números y objetos; el espejo resuelve legibilidad pero no reemplaza autenticación oficial."},
]
write_csv(HERE / "V169_PDF_VISUAL_AND_TEXT_CONTROL.csv", pdf_controls)

addendum = """

## Adenda V169 · doble identificador documental

El Cuadro I-11 del Informe ENARGAS 2009 empareja seis Notas SIGEN con seis números propios de Actuación ENARGAS. Este control contemporáneo no identifica el asiento receptor de la Nota SIGEN Nº 3672/09 GSEyP, pero justifica pedir dos registros correlacionados: (a) salida SIGEN con fecha, destinatario, asunto, adjuntos y pases; y (b) ingreso del destinatario —CGN/Economía o el organismo que resulte— con su número de actuación/COMDOC, fecha, remitente, asunto, pases y contenedor. Debe informarse el vínculo entre ambos o una certificación negativa fundada por sistema, período y campo buscado. Se conserva como DRAFT_NOT_SENT; solicitudes enviadas 0.
"""
for name in ("REQUEST_ECONOMIA_TESORO_SETTLEMENT_V169.md", "REQUEST_SUBMISSION_CHECKLIST_V169.md"):
    path = HERE / name
    text = path.read_text(encoding="utf-8-sig")
    if "Adenda V169 · doble identificador documental" not in text:
        path.write_text(text + addendum, encoding="utf-8")

write_csv(HERE / "CURRENT_STATE_V169.csv", read_csv(PARENT / "CURRENT_STATE_V168.csv"))
write_csv(HERE / "FOUR_LEG_PASS_PANEL_V169.csv", read_csv(PARENT / "FOUR_LEG_PASS_PANEL_V168.csv"))
coverage_rows = read_csv(PARENT / "STRICT_Q4_FOUR_LEG_COVERAGE_V168.csv")
coverage_rows[0]["coverage_set"] = "V169 strict 34-entity set; unchanged from V168"
coverage_rows[0]["v161_change"] = "V169: no banking promotion; numerator and coverage unchanged from V168."
write_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V169.csv", coverage_rows)

recovery_note = """# Recuperación archivística y doble clave documental · V169

V169 amplía la búsqueda más allá de las colecciones tempranas. El inventario Wayback 2013-2020 devuelve 25 capturas PDF HTTP 200 de la misma carpeta oficial, correspondientes a planes 2013-2015; ninguno de los catorce cuerpos 2009 aparece. Esto confirma continuidad de carpeta y convención, no una fecha ni causa de retiro.

El índice oficial de 78 ediciones de Actos de Gobierno entre 15-09-2008 y 08-03-2010 enumera el Plan SIGEN 2008 y las dos partes del Plan 2010, pero no el Plan 2009. Junto con la Memoria que confirma su aprobación el 15-12-2008, queda demostrado un hueco de esa superficie editorial, no inexistencia ni ausencia universal de publicación. El acto aprobatorio, expediente y comunicación UAI Economía siguen abiertos.

El Cuadro I-11 del Informe ENARGAS 2009 aporta seis pares Nota SIGEN/Actuación receptora. La Nota 3672/09 debe buscarse con doble clave —salida SIGEN e ingreso del destinatario—, sin inventar el número receptor. Su cuerpo, adjuntos, distribución e ids SISIO permanecen abiertos. Common Crawl no completó el barrido extendido por indisponibilidad; el error queda separado de los negativos válidos. Seis borradores DRAFT_NOT_SENT, solicitudes enviadas 0, SAF355 0/5 y ejecución bancaria 0/10.
"""
for name in ("E0_PLAN_2009_ARCHIVE_RECOVERY_NOTE_V169.md", "E0_SIGEN_ARCHIVAL_INDEX_RECOVERY_NOTE_V169.md", "E0_FISCAL_RECONSTRUCTION_V169.md"):
    (HERE / name).write_text(recovery_note, encoding="utf-8")
(HERE / "CNV_ATTACHMENT_ANALYTIC_REVIEW_V169.md").write_text(f"""# Revisión analítica acumulada V169

Panel congelado: 34 entidades y {COVERAGE}% de activos. V169 suma un negativo editorial acotado para Plan 2009, un inventario tardío de carpeta y la doble clave Nota SIGEN/actuación receptora. No recupera los 14 cuerpos, acto, Nota 3672/09, ids SISIO ni ejecución. Seis pedidos DRAFT_NOT_SENT; SAF355 0/5 y ejecución 0/10.
""", encoding="utf-8")

bundle = []
for role, path, url, use in [
    ("INFOLEG_ACTOS_INDEX", INFOLEG_INDEX, new_sources[0]["url_original"], "publication-surface comparator"),
    ("WAYBACK_LATE_PLAN_DIRECTORY", WAYBACK_LATE, new_sources[1]["url_original"], "late archive inventory"),
    ("ENARGAS_OFFICIAL_INDEX", ENARGAS_INDEX, new_sources[2]["url_original"], "official provenance"),
    ("ENARGAS_OFFICIAL_CHAPTER", ENARGAS_CHAPTER, new_sources[3]["url_original"], "dual-identifier text comparator"),
    ("ENARGAS_FULL_MIRROR", ENARGAS_FULL, new_sources[4]["url_original"], "complete visual comparator"),
]:
    bundle.append({"role": role, "path": "/" + path.relative_to(REPO).as_posix(), "url": url, "bytes": str(path.stat().st_size), "sha256": sha256(path), "analytic_use": use})
write_csv(HERE / "V169_SOURCE_BUNDLE.csv", bundle)

SYNC.mkdir(parents=True, exist_ok=True)
sync_rows = []
for row in new_sources:
    path = REPO / row["archivo_local"].lstrip("/")
    verification = "PDF_MAGIC_HASH_AND_RELEVANT_PAGE_VISUAL" if path.suffix.lower() == ".pdf" else "PARSED_CONTENT_AND_HASH"
    sync_rows.append({"role": "V169_PUBLIC_SOURCE", "relative_path": row["archivo_local"], "source_url": row["url_original"], "size_bytes": str(path.stat().st_size), "sha256": sha256(path), "format_verification": verification})
write_csv(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V169.csv", sync_rows)
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V169.csv", late_scan)
(SYNC / "SOURCE_SYNC_REPORT_V169.md").write_text("""# Sincronización incremental de fuentes · V169

- Catálogo: 596/596 copias locales y SHA-256 válido; brecha 0.
- Nuevas: índice InfoLEG, inventario Wayback, página ENARGAS, capítulo oficial y memoria completa espejo.
- PDF: página relevante inspeccionada en copia oficial y completa; defecto visual documentado.
- Cuerpos Plan 2009, acto, Nota 3672/09 e ids SISIO siguen abiertos.
""", encoding="utf-8")
(SYNC / "qa_source_sync_v169.py").write_text("""from pathlib import Path
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
""", encoding="utf-8")

local_census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V169.csv")
for row in new_sources:
    path = REPO / row["archivo_local"].lstrip("/")
    local_census.append({
        "source_id": row["id"], "institution": row["institucion"], "artifact": row["titulo"],
        "url": row["url_original"], "local_path": row["archivo_local"], "sha256": row["sha256"],
        "bytes": str(path.stat().st_size), "period_coverage": row["periodo_utilizado"],
        "variable_families": "Plan2009;publication;archive;Nota3672;dual_identifier",
        "primary_source": "YES" if "espejo" not in row["institucion"].lower() and "Wayback" not in row["institucion"] else "PRESERVED_COPY_OR_METADATA",
        "preserved": "YES", "method_breaks": "superficie/index/mirror/comparator no sustituye cuerpo target",
        "use_status": "E0_USABLE_WITH_SCOPE", "caveat": row["nota"],
    })
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V169.csv", local_census)

archival = read_csv(HERE / "ARCHIVAL_PROVENANCE_V169.csv")
for row in new_sources:
    path = REPO / row["archivo_local"].lstrip("/")
    archival.append({
        "source_id": row["id"], "original_url": row["url_original"], "retrieval_url": row["url_original"],
        "capture_timestamp": "2026-08-31", "cdx_digest": "N/A_DIRECT_OR_QUERY_METADATA",
        "local_path": row["archivo_local"], "sha256": row["sha256"], "bytes": str(path.stat().st_size),
        "provenance_note": row["nota"],
    })
write_csv(HERE / "ARCHIVAL_PROVENANCE_V169.csv", archival)

refs = HERE / "SOURCE_REFERENCES_V169.md"
with refs.open("a", encoding="utf-8") as handle:
    handle.write("\n## V169 · superficie editorial, archivo tardío y doble identificador\n")
    for row in new_sources:
        handle.write(f"\n- `{row['id']}` · {row['titulo']} · {row['url_original']} · `{row['archivo_local']}` · `{row['sha256']}`\n")

(HERE / "README_V169.md").write_text(f"""# Checkpoint V169

- Archivo: 596/596 copias locales con hash válido; +5 fuentes/objetos.
- Plan 2009: 14 enlaces conocidos; 14 cuerpos aún no localizados.
- Publicación: índice oficial de 78 ediciones muestra Plan 2008 y Plan 2010, no Plan 2009; negativo limitado a esa superficie.
- Archivo tardío: 25 PDFs 2013-2015 en la carpeta oficial, ninguno de 2009; continuidad confirmada, fecha de retiro desconocida.
- Nota 3672/09: seis comparadores de 2009 prueban doble clave Nota SIGEN/Actuación receptora; el identificador target sigue abierto.
- Aprobación: 15/12/2008 confirmada; acto/número/expediente y comunicación UAI Economía no localizados.
- Panel: 34 entidades; activos {NUMERATOR}/{SYSTEM_ASSETS}; cobertura {COVERAGE}%.
- SAF355 0/5; ejecución 0/10; seis borradores no enviados; solicitudes enviadas 0.
""", encoding="utf-8")
(HERE / "VEREDICTO_V169.md").write_text("""# Veredicto V169

Avance sustantivo sin cierre indebido. Se demuestra una discontinuidad editorial específica: Plan 2008 y Plan 2010 fueron publicados en Actos de Gobierno, mientras Plan 2009 no figura en las 78 ediciones indexadas. La carpeta oficial reaparece archivada con planes posteriores, no con los cuerpos target. Para Nota 3672/09 queda probada una práctica contemporánea de doble identificador emisor/receptor, que mejora la solicitud pero no identifica el asiento target. Common Crawl ampliado quedó inconcluso por servicio, no como negativo. Sin promoción bancaria ni solicitud enviada.
""", encoding="utf-8")
(HERE / "AUDITORIA_V169.md").write_text(f"""# Auditoría V169

- Catálogo/copia/hash: 596/596; huecos 0; nuevas 5.
- InfoLEG: 78 ediciones; 3 títulos SIGEN —Plan 2008, Plan 2010 partes 1 y 2—; Plan 2009 0.
- Wayback tardío: 25 PDFs HTTP 200; planes 2013-2015; cuerpos 2009 0.
- ENARGAS: 6/6 pares Nota SIGEN/Actuación receptora; página relevante cotejada en dos PDFs.
- Guardas: hueco editorial ≠ no publicación universal; comparador ≠ id target; timeout ≠ negativo.
- Panel 34, {COVERAGE}%; promociones 0; solicitudes 0; SAF355 0/5; ejecución 0/10.
""", encoding="utf-8")
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V169_A_V170.md").write_text("""# Handover V169 → V170

## Cerrado

- Superficie Actos de Gobierno 2008-2010: Plan 2008 y Plan 2010, hueco Plan 2009 acotado.
- Wayback tardío: 25 capturas de planes 2013-2015; ningún cuerpo 2009.
- Seis pares contemporáneos Nota SIGEN/Actuación receptora.
- Archivo 596/596; panel 34 sin cambio.

## Prioridad V170

1. Reintentar Common Crawl 2013-2020 por lotes y separar timeout de negativo.
2. Buscar Plan 2009 en bibliotecas, repositorios documentales y respaldos institucionales por los 14 nombres exactos.
3. Pedir/ubicar la doble clave de Nota 3672/09: salida SIGEN e ingreso CGN/Economía, más ids SISIO.
4. Reconstruir acto aprobatorio 15/12/2008 y comunicación UAI Economía.
5. Mantener seis borradores DRAFT_NOT_SENT, SAF355 0/5 y ejecución 0/10.
""", encoding="utf-8")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V168.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint": "V169", "date": "2026-08-31", "master_catalog_entries": 596,
    "physical_local_copies": 596, "physical_local_hash_ok": 596,
    "remaining_catalog_physical_or_hash_gaps": 0,
    "state": "SOURCE_ARCHIVE_COMPLETE_PLAN2009_EDITORIAL_GAP_AND_NOTE_DUAL_IDENTIFIER_COMPARATOR_LOCATED_TARGET_BODIES_OPEN",
    "analytical_promotion": "NONE_V169_ARCHIVAL_AND_DOCUMENT_ROUTE_ONLY", "exact_entities": 34,
    "strict_asset_numerator_million_ars": NUMERATOR, "system_assets_million_ars": SYSTEM_ASSETS,
    "strict_coverage_pct": COVERAGE, "strict_coverage_increment_v168_pp": "0",
    "request_drafts_status": "DRAFT_NOT_SENT", "requests_submitted": 0, "responses_received": 0,
    "saf355_certifications_located": 0, "executed_historical_bank_rows_confirmed": 0,
    "plan_sigen_2009_body_located": False, "plan_sigen_2009_approval_act_located": False,
    "note_3672_09_body_located": False, "note_3672_recipient_identifier_located": False,
    "infoleg_actos_issues_checked": 78, "wayback_late_directory_pdf_rows": 25,
    "contemporary_sigen_note_recipient_id_pairs": 6, "new_v169_sources": 5,
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V169.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

origin_rows = read_csv(ORIGINS)
origin_by_path = {row["path"]: row for row in origin_rows}
for path in iter_files(HIST.parent):
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path": rel, "origin": "downloaded/preserved V169", "note": "InfoLEG/Wayback/ENARGAS archival and comparator sources"}
for path in iter_files(SYNC):
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path": rel, "origin": "generated/updated V169", "note": "incremental source synchronization"}
for path in sorted(HERE.iterdir(), key=lambda item: item.name.casefold()):
    if path.is_file():
        rel = path.relative_to(CYCLE).as_posix()
        origin_by_path[rel] = {"path": rel, "origin": "generated/updated V169", "note": "publication and dual-identifier checkpoint"}
for path in (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V169.csv", AUDIT / "SOURCE_BACKUP_CENSUS_V169.csv", AUDIT / "SOURCE_PRESERVATION_MISSING_V169.csv", AUDIT / "CURRENT_SOURCE_COMPLETENESS_V169.json"):
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path": rel, "origin": "generated/updated V169", "note": "596-source completeness"}
write_csv(ORIGINS, list(origin_by_path.values()), ["path", "origin", "note"])

transparency = CYCLE / "TRANSPARENCY_README.md"
text = transparency.read_text(encoding="utf-8-sig")
if "## V169 · Hueco editorial y doble identificador" not in text:
    text += """

## V169 · Hueco editorial y doble identificador

El índice oficial de 78 suplementos Actos de Gobierno entre septiembre de 2008 y marzo de 2010 enumera Plan SIGEN 2008 y Plan SIGEN 2010, pero no el Plan 2009: negativo de esa superficie, no de existencia o publicación universal. Wayback conserva 25 PDFs tardíos de la misma carpeta para planes 2013-2015, ninguno target. El Informe ENARGAS 2009 prueba con seis ejemplos que una Nota SIGEN podía adquirir otro número de actuación al ingresar al receptor; por eso Nota 3672/09 se buscará por salida e ingreso correlacionados. Cuerpos, acto, nota e ids SISIO siguen abiertos. Archivo 596/596; panel 34 sin cambio.
"""
    transparency.write_text(text, encoding="utf-8")

(REPO / "BACKUP_ACTUALIZACION_2026-08-31.md").write_text(f"""# Backup de actualización · 2026-08-31

- Checkpoint: V169.
- Fuentes: 596/596; +5 objetos.
- Plan 2009: hueco editorial acotado y archivo tardío controlado; 14 cuerpos y acto abiertos.
- Nota 3672/09: ruta doble salida/ingreso incorporada; cuerpo e ids SISIO abiertos.
- Panel: 34; {COVERAGE}% de activos; promociones 0.
- Solicitudes: 0 enviadas; seis DRAFT_NOT_SENT.
""", encoding="utf-8")

(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")

files = [{"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)} for path in sorted(HERE.iterdir(), key=lambda item: item.name.casefold()) if path.is_file() and path.name != "MANIFEST_V169.json"]
manifest = {
    "checkpoint": "V169", "parent_checkpoint": "V168",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "exact_entities": 34, "strict_coverage_pct": COVERAGE,
    "strict_asset_numerator_million_ars": NUMERATOR, "system_assets_million_ars": SYSTEM_ASSETS,
    "new_promotions": [], "historical_finding": "Scoped Plan 2009 editorial gap and six recipient dual-identifier comparators located",
    "source_archive": "596/596 catalogued physical SHA-valid; five V169 sources added",
    "plan_sigen_2009_page": "LOCATED", "plan_sigen_2009_body": "NOT_LOCATED",
    "approval_act": "NOT_LOCATED", "note_3672_09_body": "NOT_LOCATED",
    "note_3672_recipient_identifier": "NOT_LOCATED", "crosswalk_gate": "OPEN",
    "closed_network_gate": "NO", "saf355_certifications": "0/5",
    "executed_historical_bank_rows": "0/10", "requests_submitted": 0, "files": files,
}
(HERE / "MANIFEST_V169.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in iter_files(REPO) if path != global_manifest]
payload = {
    "checkpoint": "V169", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": COVERAGE, "exact_entities": 34, "closed_network_gate": "NO",
    "source_audit": "596 master; 596 physical SHA-valid; five V169 sources added",
    "historical_workstream": "Plan 2009 editorial gap and late archive checked; Note 3672 dual-key route added; bodies, act, SISIO and execution open; six drafts not sent",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
tmp = global_manifest.with_suffix(".json.V169tmp")
tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
tmp.replace(global_manifest)

print("V169 BUILD PASS · catalog=596/596 · new=5 · infoleg_issues=78 · wayback_late=25 · dual_pairs=6 · exact=34 · requests=0")
