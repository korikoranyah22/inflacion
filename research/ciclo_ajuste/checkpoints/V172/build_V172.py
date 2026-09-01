from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import os


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
PARENT = CYCLE / "checkpoints" / "V171"
AUDIT = CYCLE / "source_audit"
SYNC = CYCLE / "inputs" / "source_sync" / "v172"
HIST_ROOT = CYCLE / "inputs" / "historical_retrieval" / "v172"
HIST = HIST_ROOT / "binaries"
QUERY = HIST_ROOT / "query_logs"
METHODS = HIST_ROOT / "methods"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"

COVERAGE = "63.4406041403540997520463142785031521252747951992299547614348265414453439585848248058817492708499966268585997481191265825"
NUMERATOR = "61345602.215"
SYSTEM_ASSETS = "96697695.5"
EXCLUDED_DIRS = {".git", "__pycache__", "tmp", "node_modules"}

SIGEN07 = HIST / "sigen_memory_2007_digital_archive_and_mesa_system.pdf"
CIR17 = HIST / "cgn_circular_17_2005_note_reference_metadata.html"
DISP32 = HIST / "cgn_disposition_32_2009_midyear_hybrid_submission.html"
CC_CONTROL = QUERY / "commoncrawl_health_control_2014_49.csv"
CC_2016 = QUERY / "commoncrawl_exact_prefix_2016_remaining.csv"
CC_1720 = QUERY / "commoncrawl_exact_prefix_2017_2020.csv"
SCANNER = METHODS / "commoncrawl_exact_prefix_scanner_v172.ps1"
EXPECTED = {
    SIGEN07: (87754, "4d545f42010260fa25dbe66fd6cf7274f460531989dec41b473ae31fb6b4f1d1"),
    CIR17: (5036, "73008df0c1a699b66f077392ed1866ad7afec1418daf337d3626edcaba09b21f"),
    DISP32: (25476, "c25b2426d701bf5a69a7a80a0c284b8ddcb6241a782c8164f1306ecef44caf6b"),
    CC_CONTROL: (836, "67206ea81e0fb629996e31f05ed0518efc2e6cf2f94f7d4286d226f4cdd34e8d"),
    CC_2016: (5084, "9cfdbc080af89f81d40fba1c2131154dea1b667129e70fb114447cd166784ad0"),
    CC_1720: (31988, "b939d23ded4767087ae62d9ea26ab7c7170a2a6abba0a85d08981ef4798245cf"),
    SCANNER: (6014, "e4fede8e068fecb83702b5d11e5b515b92a1f8d8f4b4e7b03270ae151838457a"),
}


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
    skip = {
        "MANIFEST_V171.json", "README_V171.md", "VEREDICTO_V171.md", "AUDITORIA_V171.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V171_A_V172.md", "V171_SOURCE_BUNDLE.csv",
        "V171_PUBLIC_SEARCH_LOG.csv", "E0_PLAN_2009_ARCHIVE_RECOVERY_NOTE_V171.md",
        "E0_SIGEN_ARCHIVAL_INDEX_RECOVERY_NOTE_V171.md", "E0_FISCAL_RECONSTRUCTION_V171.md",
        "CNV_ATTACHMENT_ANALYTIC_REVIEW_V171.md",
    }
    for source in sorted(PARENT.iterdir(), key=lambda path: path.name.casefold()):
        if not source.is_file() or source.name in skip or source.name.startswith(("build_", "qa_")):
            continue
        target = HERE / source.name.replace("V171", "V172")
        target.write_text(source.read_text(encoding="utf-8-sig").replace("V171", "V172"), encoding="utf-8")


HERE.mkdir(parents=True, exist_ok=True)
clone_parent()
for path, (size, digest) in EXPECTED.items():
    assert path.is_file() and path.stat().st_size == size and sha256(path) == digest

sources = [
    {
        "id": "e0_sigen_memory_2007_computerized_mesa_and_digital_archive_v172",
        "tema": "ciclo_ajuste_e0_fiscal", "institucion": "Sindicatura General de la Nación",
        "titulo": "Memoria SIGEN 2007 · sistema informático de Mesa y bases del Archivo Digital",
        "url_original": "https://www.argentina.gob.ar/sites/default/files/memoria_sigen_2007.pdf",
        "archivo_local": "/" + SIGEN07.relative_to(REPO).as_posix(),
        "fecha_descarga": "2026-08-31", "fecha_publicacion": "2007",
        "codigo_serie": "Memoria SIGEN 2007", "periodo_utilizado": "2007-2009; capacidad preexistente",
        "tipo": "PDF oficial preservado · control visual PDF p.22 / impresa p.21",
        "sha256": EXPECTED[SIGEN07][1],
        "nota": "V172: documenta un sistema informático de Mesa de Entradas y la Resolución SGN 41/07 para digitalización/publicación, además de clasificación del Archivo General. No nombra el producto informático, no contiene la Nota 3672/09 ni acredita que esa nota fuera digitalizada.",
    },
    {
        "id": "e0_cgn_circular_17_2005_note_subject_and_prior_reference_v172",
        "tema": "ciclo_ajuste_e0_fiscal", "institucion": "Contaduría General de la Nación",
        "titulo": "Circular CGN 17/2005 · asunto, referencia y número de tramitación previa en notas",
        "url_original": "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/2005/cir17.htm",
        "archivo_local": "/" + CIR17.relative_to(REPO).as_posix(),
        "fecha_descarga": "2026-08-31", "fecha_publicacion": "2005-12-29",
        "codigo_serie": "Circular CGN 17/2005", "periodo_utilizado": "2005-2009",
        "tipo": "HTML oficial preservado · TLS histórico vencido documentado",
        "sha256": EXPECTED[CIR17][1],
        "nota": "V172: las notas presentadas a CGN debían llevar asunto/referencia y podían consignar el número de una tramitación anterior complementada. Amplía claves para localizar 3672/09; no contiene su cuerpo ni asiento.",
    },
    {
        "id": "e0_cgn_disposition_32_2009_hybrid_mesa_submission_v172",
        "tema": "ciclo_ajuste_e0_fiscal", "institucion": "Contaduría General de la Nación",
        "titulo": "Disposición CGN 32/2009 · presentación híbrida por Mesa, nota e índice",
        "url_original": "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/2009/disp32/disp32.htm",
        "archivo_local": "/" + DISP32.relative_to(REPO).as_posix(),
        "fecha_descarga": "2026-08-31", "fecha_publicacion": "2009-06-26",
        "codigo_serie": "Disposición CGN 32/2009", "periodo_utilizado": "2009; comparador contemporáneo de custodia",
        "tipo": "HTML oficial preservado · TLS histórico vencido documentado",
        "sha256": EXPECTED[DISP32][1],
        "nota": "V172: art. 15 exige original foliado, CD/disquete, nota de elevación e índice; controla integridad al recibir y prevé devolución en 72 horas. Art. 17 asigna responsabilidad por respaldo y archivo oficial. El circuito es de cierre intermedio y no prueba que se aplicara idénticamente a la Nota 3672/09.",
    },
]

catalog = read_csv(CATALOG)
catalog_fields = list(catalog[0])
by_id = {row["id"]: row for row in catalog}
for row in sources:
    by_id[row["id"]] = row
catalog = list(by_id.values())
write_csv(CATALOG, catalog, catalog_fields)
assert len(catalog) == len(by_id) == 602

audit_rows = []
for row in catalog:
    local = REPO / row["archivo_local"].lstrip("/")
    actual = sha256(local) if local.is_file() else ""
    audit_rows.append({
        "id": row["id"], "archivo_local": row["archivo_local"], "exists": str(local.is_file()),
        "sha_catalog": row["sha256"].lower(), "sha_actual": actual,
        "hash_ok": str(local.is_file() and bool(row["sha256"]) and actual == row["sha256"].lower()),
    })
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V172.csv", audit_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V172.csv", audit_rows)
missing = [row for row in audit_rows if row["exists"] != "True" or row["hash_ok"] != "True"]
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V172.csv", missing, list(audit_rows[0]))
assert not missing

raw_specs = [("HEALTH_CONTROL_2014_49", CC_CONTROL), ("2016_REMAINING", CC_2016), ("2017_2020_FULL", CC_1720)]
execution = []
for scope, path in raw_specs:
    for row in read_csv(path):
        item = dict(row)
        item["run_scope"] = scope
        item["evidentiary_effect"] = "SCOPED_NO_CAPTURE_FOR_COLLECTION_HOST" if row["classification"] == "NO_CAPTURE_VALID" else "NONE_NOT_NEGATIVE"
        execution.append(item)
write_csv(HERE / "E0_COMMONCRAWL_EXACT_PREFIX_EXECUTION_V172.csv", execution)
assert len(execution) == 106 and all(row["classification"] == "NO_CAPTURE_VALID" for row in execution)

query_summary = [
    {"batch": "HEALTH_CONTROL_2014_49", "collections_targeted": "1", "hosts_per_collection": "2", "queries": "2", "valid_no_capture": "2", "service_errors": "0", "captures": "0", "pending_queries": "0", "decision": "SERVICE_HEALTH_CONFIRMED"},
    {"batch": "2016_REMAINING", "collections_targeted": "7", "hosts_per_collection": "2", "queries": "14", "valid_no_capture": "14", "service_errors": "0", "captures": "0", "pending_queries": "0", "decision": "2016_REMAINDER_COMPLETE_SCOPED_NEGATIVES"},
    {"batch": "2017_2020_FULL", "collections_targeted": "45", "hosts_per_collection": "2", "queries": "90", "valid_no_capture": "90", "service_errors": "0", "captures": "0", "pending_queries": "0", "decision": "2017_2020_COMPLETE_SCOPED_NEGATIVES"},
    {"batch": "V172_TOTAL", "collections_targeted": "53_distinct", "hosts_per_collection": "2", "queries": "106", "valid_no_capture": "106", "service_errors": "0", "captures": "0", "pending_queries": "0", "decision": "PUBLIC_ARCHIVE_SURFACE_EXHAUSTED_FOR_2016_REMAINDER_AND_2017_2020"},
]
write_csv(HERE / "E0_COMMONCRAWL_QUERY_COMPLETENESS_V172.csv", query_summary)

coverage_rows = read_csv(HERE / "E0_COMMONCRAWL_COLLECTION_COVERAGE_V172.csv")
run_by_collection = {}
for row in execution:
    run_by_collection.setdefault(row["collection"], []).append(row)
for row in coverage_rows:
    values = run_by_collection.get(row["collection_id"], [])
    if values and all(item["classification"] == "NO_CAPTURE_VALID" for item in values):
        row["exact_prefix_status"] = "NO_CAPTURE_VALID_2_HOSTS"
        row["evidentiary_effect"] = "SCOPED_COLLECTION_HOST_NEGATIVE"
write_csv(HERE / "E0_COMMONCRAWL_COLLECTION_COVERAGE_V172.csv", coverage_rows)

pdf_control = [{
    "control_id": "PDF172_01", "source_id": sources[0]["id"], "pdf_page": "22", "printed_page": "21",
    "target": "sistema informático de Mesa de Entradas; Resolución SGN 41/07; Archivo General",
    "visual_result": "PASS_TEXT_LEGIBLE_LAYOUT_COHERENT", "text_result": "PASS_TARGET_PASSAGES_PRESENT",
    "evidentiary_limit": "Capacidad y procedimiento; no cuerpo ni asiento de Nota 3672/09.",
}]
write_csv(HERE / "V172_PDF_VISUAL_CONTROL.csv", pdf_control)

mesa = [
    {"row_id": "SM172_01", "period": "2007", "institution": "SIGEN", "record_or_system": "sistema informático de Mesa de Entradas", "documented_fact": "soportaba fundamentalmente la gestión documental", "target_query": "salida 3672/09 por número, fecha, GSEyP, destinatario, asunto y adjuntos", "probative_value": "CONTEMPORANEOUS_SYSTEM_CAPABILITY", "limit": "nombre técnico y esquema no publicados; no recupera la nota", "source_id": sources[0]["id"]},
    {"row_id": "SM172_02", "period": "2007", "institution": "SIGEN", "record_or_system": "Archivo Digital / Res. SGN 41/07", "documented_fact": "procedimiento de digitalización/publicación y clasificación documental", "target_query": "índice digital; clase; soporte; fecha; hash; regla de acceso; disposición", "probative_value": "DIGITAL_ARCHIVE_PROCEDURE", "limit": "cuerpo de la resolución y cobertura exacta abiertos", "source_id": sources[0]["id"]},
    {"row_id": "SM172_03", "period": "2009", "institution": "SIGEN", "record_or_system": "Archivo Digital + Archivo General", "documented_fact": "memoria 2009 informa consolidación digital y clasificación/registro/reordenamiento general", "target_query": "inventario 2009; serie notas GSEyP; libro salida; caja; transferencia; depuración", "probative_value": "CONTINUITY_REREADING", "limit": "fuente ya catalogada; no implica inclusión del target", "source_id": "e0_sigen_memory_2009_account_2008_global_control_report"},
]
write_csv(HERE / "E0_SIGEN_MESA_DIGITAL_ARCHIVE_CONTINUITY_V172.csv", mesa)

custody = [
    {"row_id": "NC172_01", "date": "1996-06-26", "institution": "CGN", "rule_or_event": "ingreso obligatorio y pases", "documented_trace": "Mesa controla ingreso y sistema registra pases", "target_use": "asiento receptor e historial 3672/09", "status": "PRIMARY_ROUTE", "limit": "norma no es asiento", "source_id": "e0_cgn_disposition_41_1996_mandatory_entry_and_internal_pass_registry_v171"},
    {"row_id": "NC172_02", "date": "2005-12-29", "institution": "CGN", "rule_or_event": "metadatos de nota", "documented_trace": "asunto/referencia y posible número de trámite anterior", "target_use": "buscar 3672/09, 0120/09 DAIF, respuesta, cierre 2008, UEPEX", "status": "SEARCH_KEY_UPGRADE", "limit": "no identifica valor concreto del campo", "source_id": sources[1]["id"]},
    {"row_id": "NC172_03", "date": "2008", "institution": "Economía", "rule_or_event": "COMDOC III ya operativo", "documented_trace": "procedimiento contemporáneo usa COMDOC III en un circuito de deuda", "target_use": "consulta subsidiaria 2009 y migración", "status": "TEMPORAL_CORRECTION", "limit": "no prueba uso para toda nota CGN", "source_id": "e0_argentina_rc_26_216_2008_tsa_sigade"},
    {"row_id": "NC172_04", "date": "2009-06-26", "institution": "CGN", "rule_or_event": "paquete híbrido por Mesa", "documented_trace": "original foliado + soporte óptico + nota + índice + control de integridad", "target_use": "pedir soporte, contenedor, índice, folios y constancia de recepción", "status": "CONTEMPORANEOUS_CUSTODY_COMPARATOR", "limit": "procedimiento de cierre, no identidad automática con nota SIGEN", "source_id": sources[2]["id"]},
    {"row_id": "NC172_05", "date": "2010-03-22", "institution": "CGN", "rule_or_event": "alcance CGN de COMDOC y continuidad Nota", "documented_trace": "ciertos expedientes ministeriales por COMDOC; otras actuaciones internas por Nota", "target_use": "buscar ambas rutas sin exclusividad", "status": "SCOPE_BOUNDARY", "limit": "posterior a nota target", "source_id": "e0_cgn_circular_04_2010_comdoc_transition_and_note_route_v171"},
    {"row_id": "NC172_06", "date": "2016-09", "institution": "Economía", "rule_or_event": "corte COMDOC/GDE", "documented_trace": "consulta pública separa actuaciones anteriores y posteriores", "target_use": "pedir crosswalk de migración sin inventar ID GDE originario", "status": "LATER_MIGRATION_BOUNDARY", "limit": "ruta actual no sustituye sistema 2009", "source_id": "e0_economia_consulta_expedientes_comdoc_gde"},
]
write_csv(HERE / "E0_CGN_NOTE_METADATA_AND_HYBRID_CUSTODY_V172.csv", custody)

correction = [
    {"claim_id": "CD172_01", "prior_shorthand": "COMDOC comienza en 2010", "corrected_claim": "COMDOC III ya estaba operativo en Economía al menos en 2008 para ciertos circuitos", "evidence": "RC SH/SF 216/26 de 2008", "effect": "corregir cronología; buscar COMDOC como ruta posible", "guardrail": "capacidad ministerial no prueba inclusión de toda nota CGN"},
    {"claim_id": "CD172_02", "prior_shorthand": "Circular 04/2010 crea COMDOC", "corrected_claim": "Circular 04/2010 fija un alcance obligatorio específico ante CGN y mantiene rutas por Nota", "evidence": "Circular CGN 04/2010", "effect": "distinguir existencia del sistema de obligación por circuito", "guardrail": "no retroproyectar la regla a 2009"},
    {"claim_id": "CD172_03", "prior_shorthand": "un negativo COMDOC cierra 2009", "corrected_claim": "el cierre exige Mesa CGN, registro legado, archivo, COMDOC si correspondió y migraciones", "evidence": "Disposición 41/1996 + Circular 17/2005 + Disp.32/2009 + Circ.04/2010", "effect": "negativo fundado multisistema", "guardrail": "ninguna ruta aislada prueba inexistencia"},
]
write_csv(HERE / "E0_COMDOC_SCOPE_CORRECTION_V172.csv", correction)

res41 = [
    {"test_id": "R41172_01", "surface": "Memoria SIGEN 2007", "query_or_reference": "Resolución Nº 41/07 SGN", "result": "referencia y objeto documental localizados", "classification": "ACT_REFERENCE_LOCATED_BODY_OPEN", "next_step": "pedir cuerpo, anexos, procedimiento y registro de vigencia"},
    {"test_id": "R41172_02", "surface": "buscador público web oficial/general", "query_or_reference": "resolución SIGEN 41/2007 digitalización publicación documentación", "result": "sin cuerpo oficial recuperado", "classification": "PUBLIC_BODY_SEARCH_NEGATIVE_SCOPED", "next_step": "consulta AIP/archivo SIGEN por acto exacto"},
    {"test_id": "R41172_03", "surface": "índice histórico dinámico SIGEN", "query_or_reference": "resoluciones.asp / POST Result_resoluciones.asp / año 2007 / número 41", "result": "formulario y campos conocidos; respuesta POST no preservada", "classification": "HISTORICAL_QUERY_SCHEMA_ONLY", "next_step": "pedir exportación del índice o asiento del acto"},
]
write_csv(HERE / "E0_SIGEN_RES41_2007_BODY_SEARCH_V172.csv", res41)

keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V172.csv")
keys.extend([
    {"key_id": "SK172_20", "request_id": "REQ155_SIGEN", "key_group": "computerized_mesa_outgoing", "exact_key": "sistema informático de Mesa de Entradas SIGEN · Nota 3672/09 · GSEyP · 2009", "search_purpose": "recuperar asiento de salida y producto/sistema", "source_or_basis": "Memoria SIGEN 2007 p.21 impresa", "caveat": "capacidad no prueba registro target"},
    {"key_id": "SK172_21", "request_id": "REQ155_SIGEN", "key_group": "digital_archive_resolution", "exact_key": "Resolución SGN 41/07 · digitalización · publicación · clasificación · Archivo General", "search_purpose": "recuperar procedimiento, índice y cobertura de la serie", "source_or_basis": "Memoria SIGEN 2007", "caveat": "acto/body no localizado públicamente"},
    {"key_id": "SK172_22", "request_id": "REQ133_ECON", "key_group": "note_subject_prior_reference", "exact_key": "3672/09; 0120/09 DAIF; respuesta; cierre Cuenta 2008; UEPEX; GSEyP", "search_purpose": "buscar en asunto/referencia y número de tramitación previa", "source_or_basis": "Circular CGN 17/2005", "caveat": "consultar variantes y campos separados"},
    {"key_id": "SK172_23", "request_id": "REQ133_ECON", "key_group": "hybrid_container_index", "exact_key": "original foliado; CD/disquete; nota de elevación; índice; constancia de recepción; devolución 72 horas", "search_purpose": "localizar contenedor y relaciones del paquete 2009", "source_or_basis": "Disposición CGN 32/2009 arts.15-17", "caveat": "comparador contemporáneo, no aplicación automática"},
    {"key_id": "SK172_24", "request_id": "REQ155_SIGEN/REQ133_ECON", "key_group": "cross_system_correlation", "exact_key": "salida SIGEN 3672/09 ↔ entrada CGN ↔ trámite previo 0120/09 ↔ SISIO ↔ COMDOC/migración", "search_purpose": "producir tabla de equivalencias con fechas y custodios", "source_or_basis": "cadena V170-V172", "caveat": "no aceptar equivalencia inferida sin identificadores"},
])
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V172.csv", keys)

objects = read_csv(HERE / "E0_V172_REQUEST_OBJECTS.csv")
objects.extend([
    {"row_id": "RO172_20", "object_id": "SIGEN_MESA_OUTGOING_3672", "custodian": "SIGEN · Mesa de Entradas, Salidas y Archivo/GSEyP", "exact_record": "exportación del asiento de salida de Nota 3672/09 y cuerpo asociado", "period": "2009", "minimum_fields": "sistema/producto; número; fecha/hora; emisor; firmante; destinatario; asunto/referencia; trámite previo; adjuntos; pases; acuse; soporte", "closure_rule": "Cuerpo+metadatos o negativo fundado por sistema, serie, campos, variantes y período.", "status": "DRAFT_NOT_SENT"},
    {"row_id": "RO172_21", "object_id": "SIGEN_RES41_2007_DIGITAL_ARCHIVE", "custodian": "SIGEN · Archivo/Mesa/Normativa", "exact_record": "Resolución SGN 41/07, procedimiento, anexos e índice de documentos clasificados/digitalizados", "period": "2007-2010", "minimum_fields": "acto; anexos; vigencia; clases; metadatos; soporte; índice; fecha digitalización; ubicación; acceso; transferencia/depuración", "closure_rule": "Acto e inventario o certificación de búsqueda y disposición documental.", "status": "DRAFT_NOT_SENT"},
    {"row_id": "RO172_22", "object_id": "CGN_NOTE_REFERENCE_AND_CONTAINER_3672", "custodian": "CGN · Mesa/DAIF/Archivo", "exact_record": "asiento 3672/09 con asunto/referencia, trámite anterior, soporte, contenedor e índice", "period": "2009", "minimum_fields": "entrada; fecha/hora; remitente; destinatario; asunto/referencia; 0120/09; folios; CD/disquete; índice; constancia; pases; destino", "closure_rule": "Consultar libro/sistema legado/archivo/COMDOC y explicar cada negativo.", "status": "DRAFT_NOT_SENT"},
    {"row_id": "RO172_23", "object_id": "SIGEN_CGN_SISIO_IDENTIFIER_CROSSWALK", "custodian": "SIGEN + CGN + Economía/UAI", "exact_record": "tabla de correlación salida/entrada/trámite previo/SISIO/COMDOC-migración", "period": "2009 en adelante", "minimum_fields": "id; sistema; productor; receptor; fecha; asunto; relación; estado; contenedor; migración; evidencia", "closure_rule": "Una fila por identificador; no aceptar resumen sin claves y trazabilidad.", "status": "DRAFT_NOT_SENT"},
])
write_csv(HERE / "E0_V172_REQUEST_OBJECTS.csv", objects)
write_csv(HERE / "E0_V172_REQUEST_OBJECTS_V172.csv", objects)

breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V172.csv")
breaks.extend([
    {"break_id": "comdoc_existence_not_cgn_scope_start_v172", "dimension": "temporal_system", "problem": "COMDOC existía antes de la regla CGN 2010.", "rule": "Separar capacidad ministerial 2008 de obligación por circuito 2010.", "status": "FROZEN_V172", "evidence": "RC 216/26-2008 + Circular CGN 04/2010"},
    {"break_id": "computerized_mesa_capability_not_target_record_v172", "dimension": "document_route", "problem": "La Mesa informatizada SIGEN 2007 no prueba que 3672/09 esté en su base o archivo digital.", "rule": "Pedir exportación, cuerpo e índice; mantener target abierto.", "status": "FROZEN_V172", "evidence": "Memoria SIGEN 2007 p.21 impresa"},
    {"break_id": "hybrid_closing_submission_not_note_identity_v172", "dimension": "scope", "problem": "El circuito híbrido de cierre 2009 no es automáticamente el circuito de toda nota.", "rule": "Usarlo como comparador de soportes/custodia, no como identidad documental.", "status": "FROZEN_V172", "evidence": "Disposición CGN 32/2009 arts.15-17"},
    {"break_id": "commoncrawl_106_valid_negatives_are_scoped_v172", "dimension": "archive_query", "problem": "106 respuestas válidas sin captura cubren colecciones/prefijos, no la existencia institucional.", "rule": "Cerrar sólo esa superficie pública; mantener archivos internos abiertos.", "status": "FROZEN_V172", "evidence": "V172 Common Crawl logs"},
    {"break_id": "referenced_resolution_not_body_v172", "dimension": "act_recovery", "problem": "La Memoria cita Resolución 41/07 pero no reproduce su cuerpo.", "rule": "Marcar referencia localizada y acto abierto.", "status": "FROZEN_V172", "evidence": "Memoria SIGEN 2007"},
])
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V172.csv", breaks)

producer = read_csv(HERE / "E0_RECORD_PRODUCER_SYSTEM_MAP_V172.csv")
producer.extend([
    {"map_id": "PS172_01", "institution": "SIGEN", "producer_or_custodian": "Mesa de Entradas, Salidas y Archivo", "system_or_record": "sistema informático de Mesa de Entradas", "record_class": "entrada/salida y gestión documental", "exact_fields_or_trace": "número; fecha; remitente/emisor; destinatario; asunto; adjuntos; pases; soporte", "target_use": "salida Nota 3672/09", "source_id": sources[0]["id"], "source_locator": "PDF p.22 / impresa p.21", "applicability": "CAPABILITY_PRE_TARGET", "caveat": "nombre del sistema y esquema abiertos"},
    {"map_id": "PS172_02", "institution": "CGN", "producer_or_custodian": "Mesa de Entradas/DAIF/Archivo", "system_or_record": "registro de notas y trámite previo", "record_class": "asunto/referencia", "exact_fields_or_trace": "leyenda; número anterior; respuesta; remitente; destino", "target_use": "entrada 3672/09 y vínculo 0120/09", "source_id": sources[1]["id"], "source_locator": "Circular 17/2005", "applicability": "RULE_IN_FORCE_BEFORE_TARGET", "caveat": "no contiene el asiento"},
    {"map_id": "PS172_03", "institution": "CGN", "producer_or_custodian": "Mesa/archivo oficial", "system_or_record": "paquete híbrido de cierre", "record_class": "original+medio+nota+índice", "exact_fields_or_trace": "folios; cuadros; índice; soporte; recepción; devolución; respaldo", "target_use": "contenedor y cadena de custodia 2009", "source_id": sources[2]["id"], "source_locator": "arts.15-17", "applicability": "CONTEMPORANEOUS_COMPARATOR", "caveat": "no se transpone automáticamente a Nota SIGEN"},
])
write_csv(HERE / "E0_RECORD_PRODUCER_SYSTEM_MAP_V172.csv", producer)

temporal = read_csv(HERE / "E0_DOCUMENT_SYSTEM_TEMPORAL_MAP_V172.csv")
temporal.extend([
    {"institution": "SIGEN", "target_period": "2007-2009", "contemporaneous_route": "sistema informático de Mesa; Archivo Digital; Archivo General; salida/GSEyP", "later_route_or_migration": "bases e índices posteriores; GDE si hubo migración", "required_search_scope": "número; asunto; destinatario; adjuntos; libro/base; índice digital; fondo físico; migración; disposición", "temporal_caveat": "la memoria prueba capacidad, no inclusión de la Nota 3672/09", "official_basis": sources[0]["id"]},
    {"institution": "CGN", "target_period": "2009", "contemporaneous_route": "Mesa; sistema de seguimiento; nota con asunto/referencia; papel foliado y soportes híbridos según circuito; COMDOC posible", "later_route_or_migration": "COMDOC/GDE, archivo y repositorios migrados", "required_search_scope": "entrada; trámite previo; pases; soporte; contenedor; índice; COMDOC si correspondió; crosswalk", "temporal_caveat": "COMDOC existía en 2008 pero Circular 04/2010 define sólo un alcance específico posterior", "official_basis": "CGN 41/1996 + 17/2005 + 32/2009 + 04/2010"},
])
write_csv(HERE / "E0_DOCUMENT_SYSTEM_TEMPORAL_MAP_V172.csv", temporal)

addendum = """

## Adenda V172 · Mesa SIGEN, metadatos CGN y custodia híbrida

La Memoria SIGEN 2007 declara que la gestión documental era soportada fundamentalmente por un sistema informático de Mesa de Entradas y que la Resolución SGN Nº 41/07 aprobó el procedimiento de digitalización y publicación, mientras se clasificaba el Archivo General. Se solicita la exportación de salida de la Nota Nº 3672/09 GSEyP, el nombre y esquema del sistema, el cuerpo y anexos, y el índice del Archivo Digital/físico. La referencia a la resolución no sustituye su cuerpo ni acredita que la nota haya sido digitalizada.

La Circular CGN Nº 17/2005 exige asunto o referencia y permite consignar un número de tramitación anterior. Búsquese por separado `3672/09`, `0120/09 DAIF`, `respuesta`, `Cuenta/Cierre 2008`, `UEPEX` y `GSEyP`, incluyendo variantes. La Disposición CGN Nº 32/2009 documenta un circuito contemporáneo de original foliado, CD/disquete, nota de elevación, índice, control de recepción y respaldo en archivo oficial. Se pide soporte, contenedor, folios, índice y constancia, pero no se presume que todo ese procedimiento rigiera idénticamente para la Nota SIGEN.

Se corrige la cronología: COMDOC III ya estaba operativo en el Ministerio en 2008 para ciertos circuitos; la Circular CGN 04/2010 no lo crea, sino que fija un alcance específico y conserva actuaciones por Nota. El negativo debe abarcar Mesa CGN, sistema legado, archivo, campos asunto/referencia, COMDOC si correspondió, migraciones y disposición. Correlacionar salida SIGEN, entrada CGN, antecedente 0120/09 e IDs SISIO. Estado DRAFT_NOT_SENT; solicitudes enviadas 0; SAF355 0/5; ejecución 0/10.
"""
for name in ("REQUEST_ECONOMIA_TESORO_SETTLEMENT_V172.md", "REQUEST_SUBMISSION_CHECKLIST_V172.md", "E0_INSTITUTIONAL_REQUEST_PACKAGE_V172.md"):
    path = HERE / name
    body = path.read_text(encoding="utf-8-sig")
    if "Adenda V172 · Mesa SIGEN" not in body:
        path.write_text(body + addendum, encoding="utf-8")

strict = read_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V172.csv")
strict[0]["coverage_set"] = "V172 strict 34-entity set; unchanged from V171"
strict[0]["v161_change"] = "V172: no banking promotion; numerator and coverage unchanged from V171."
write_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V172.csv", strict)

public_log = [{
    "log_id": f"CC172_{index:03d}", "surface": "Common Crawl exact prefix", "query_or_target": row["query_url"],
    "result": row["classification"], "classification": row["classification"],
    "limit_or_next_step": "Negativo limitado a colección y host; no prueba ausencia institucional.",
} for index, row in enumerate(execution, 1)]
public_log.extend({
    "log_id": row["test_id"], "surface": row["surface"], "query_or_target": row["query_or_reference"],
    "result": row["result"], "classification": row["classification"], "limit_or_next_step": row["next_step"],
} for row in res41)
write_csv(HERE / "V172_PUBLIC_SEARCH_LOG.csv", public_log)

recovery = f"""# Recuperación archivística · V172

Common Crawl volvió a responder: control 2/2, resto 2016 14/14 y 2017-2020 90/90, total V172 106 negativos válidos acotados, 0 errores y 0 capturas. Se cierra esa superficie pública, no la custodia institucional.

SIGEN documentó en 2007 un sistema informático de Mesa y bases regladas del Archivo Digital; su Memoria 2009 confirma continuidad de clasificación/registro/reordenamiento. CGN exigía desde 2005 asunto/referencia y permitía vincular trámite previo. Su Disposición 32/2009 prueba una cadena híbrida con original foliado, medio óptico, nota, índice, control de integridad y responsabilidad por respaldo. Se corrige que COMDOC no comenzó en 2010: ya existía en 2008 para ciertos circuitos; la regla 2010 sólo fija alcance CGN y continuidad de Nota. Cuerpo/asiento 3672, acto 41/07, IDs receptor/SISIO y Plan 2009 siguen abiertos. Archivo 602/602; panel 34 y {COVERAGE}%; seis borradores DRAFT_NOT_SENT, solicitudes 0, SAF355 0/5 y ejecución 0/10.
"""
for name in ("E0_PLAN_2009_ARCHIVE_RECOVERY_NOTE_V172.md", "E0_SIGEN_ARCHIVAL_INDEX_RECOVERY_NOTE_V172.md", "E0_FISCAL_RECONSTRUCTION_V172.md"):
    (HERE / name).write_text(recovery, encoding="utf-8")
(HERE / "CNV_ATTACHMENT_ANALYTIC_REVIEW_V172.md").write_text(f"""# Revisión analítica acumulada V172

Panel congelado: 34 entidades y {COVERAGE}% de activos. V172 no promueve bancos. Agrega tres fuentes oficiales que vuelven más testable la salida SIGEN y el ingreso/custodia CGN; corrige el alcance temporal de COMDOC. Common Crawl agrega 106 negativos acotados sin errores ni capturas. Cuerpos, actos, asientos, IDs SISIO y ejecución siguen abiertos. Seis pedidos DRAFT_NOT_SENT; SAF355 0/5 y ejecución 0/10.
""", encoding="utf-8")

bundle_specs = [
    ("SIGEN_MEMORY_2007", SIGEN07, sources[0]["url_original"], "computerized Mesa and Digital Archive procedure"),
    ("CGN_CIRCULAR_17_2005", CIR17, sources[1]["url_original"], "note subject/reference and prior proceeding number"),
    ("CGN_DISPOSITION_32_2009", DISP32, sources[2]["url_original"], "hybrid submission and custody comparator"),
    ("COMMONCRAWL_HEALTH_CONTROL", CC_CONTROL, "generated retrieval log", "2 valid control negatives"),
    ("COMMONCRAWL_2016_REMAINING", CC_2016, "generated retrieval log", "14 valid scoped negatives"),
    ("COMMONCRAWL_2017_2020", CC_1720, "generated retrieval log", "90 valid scoped negatives"),
    ("COMMONCRAWL_SCANNER_V172", SCANNER, "generated retrieval method", "exact-prefix method preserved"),
]
bundle = [{"role": role, "path": "/" + path.relative_to(REPO).as_posix(), "url": url, "bytes": str(path.stat().st_size), "sha256": sha256(path), "analytic_use": use} for role, path, url, use in bundle_specs]
write_csv(HERE / "V172_SOURCE_BUNDLE.csv", bundle)

SYNC.mkdir(parents=True, exist_ok=True)
sync_rows = []
for source in sources:
    local = REPO / source["archivo_local"].lstrip("/")
    sync_rows.append({
        "role": "V172_PUBLIC_SOURCE", "relative_path": source["archivo_local"], "source_url": source["url_original"],
        "size_bytes": str(local.stat().st_size), "sha256": source["sha256"],
        "format_verification": "PDF_VISUAL_TEXT_PASS_TLS_VALID" if local.suffix.lower() == ".pdf" else "HTML_EXPECTED_TITLE_AND_SUBSTANTIVE_TEXT_TLS_EXCEPTION_DISCLOSED",
    })
write_csv(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V172.csv", sync_rows)
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V172.csv", public_log)
(SYNC / "SOURCE_SYNC_REPORT_V172.md").write_text("""# Sincronización incremental de fuentes · V172

- Catálogo: 602/602 copias locales y SHA-256 válido; brecha 0.
- Nuevas fuentes: Memoria SIGEN 2007, Circular CGN 17/2005 y Disposición CGN 32/2009.
- Transporte: PDF oficial con TLS válido; dos HTML históricos con certificado TLS vencido, excepción y hashes declarados.
- Derivados: scanner y 106 consultas Common Crawl válidas preservados.
- Nota 3672/09, asiento, Resolución 41/07, Plan 2009, IDs SISIO y ejecución permanecen abiertos.
""", encoding="utf-8")
(SYNC / "qa_source_sync_v172.py").write_text("""from pathlib import Path
import csv, hashlib
root = Path(__file__).resolve().parents[5]
rows = list(csv.DictReader(Path(__file__).with_name('SOURCE_SYNC_FILE_MANIFEST_V172.csv').open(encoding='utf-8-sig', newline='')))
assert len(rows) == 3
for row in rows:
    path = root / row['relative_path'].lstrip('/')
    assert path.is_file() and path.stat().st_size == int(row['size_bytes'])
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
print('SOURCE SYNC V172 PASS · 3/3')
""", encoding="utf-8")

local_census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V172.csv")
for source in sources:
    local = REPO / source["archivo_local"].lstrip("/")
    local_census.append({
        "source_id": source["id"], "institution": source["institucion"], "artifact": source["titulo"],
        "url": source["url_original"], "local_path": source["archivo_local"], "sha256": source["sha256"],
        "bytes": str(local.stat().st_size), "period_coverage": source["periodo_utilizado"],
        "variable_families": "Nota3672;SIGEN;CGN;Mesa;ArchiveDigital;COMDOC;hybrid_custody",
        "primary_source": "YES", "preserved": "YES", "method_breaks": "route/capability source not target body",
        "use_status": "E0_USABLE_RECORD_ROUTE", "caveat": source["nota"],
    })
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V172.csv", local_census)

archival = read_csv(HERE / "ARCHIVAL_PROVENANCE_V172.csv")
for source in sources:
    local = REPO / source["archivo_local"].lstrip("/")
    tls = "N/A_OFFICIAL_DIRECT_TLS_VALID" if local.suffix.lower() == ".pdf" else "N/A_DIRECT_TLS_CERT_EXPIRED_INSECURE_TRANSPORT"
    note = source["nota"]
    if local.suffix.lower() == ".html":
        note += " Descarga inicial segura falló por certificado expirado; copia preservada con excepción explícita y contenido cotejado."
    archival.append({
        "source_id": source["id"], "original_url": source["url_original"], "retrieval_url": source["url_original"],
        "capture_timestamp": "2026-08-31", "cdx_digest": tls, "local_path": source["archivo_local"],
        "sha256": source["sha256"], "bytes": str(local.stat().st_size), "provenance_note": note,
    })
write_csv(HERE / "ARCHIVAL_PROVENANCE_V172.csv", archival)

refs = HERE / "SOURCE_REFERENCES_V172.md"
with refs.open("a", encoding="utf-8") as handle:
    handle.write("\n## V172 · Mesa SIGEN, metadatos CGN y custodia híbrida\n")
    for source in sources:
        handle.write(f"\n- `{source['id']}` · {source['titulo']} · {source['url_original']} · `{source['archivo_local']}` · `{source['sha256']}`\n")
    handle.write("\n- El PDF fue controlado visualmente en PDF p.22/impresa p.21. Las rutas prueban capacidad y deberes; no sustituyen cuerpos/asientos.\n")

retrieval = HERE / "RETRIEVAL_LOG_V172.md"
with retrieval.open("a", encoding="utf-8") as handle:
    handle.write("\n## V172 · resultados nuevos\n\n- Common Crawl: 106 consultas, 106 negativos válidos acotados, 0 errores, 0 capturas.\n- SIGEN: Mesa informatizada y Archivo Digital pre-target documentados.\n- CGN: metadatos asunto/referencia y custodia híbrida contemporánea documentados.\n- Resolución SIGEN 41/07: referencia localizada, cuerpo abierto.\n")

(HERE / "README_V172.md").write_text(f"""# Checkpoint V172

- Archivo: 602/602 copias locales con hash válido; +3 fuentes oficiales.
- Common Crawl V172: 106 consultas, 106 negativos válidos acotados, 0 errores y 0 capturas; resto 2016 y 2017-2020 completos.
- SIGEN 2007: sistema informático de Mesa y bases del Archivo Digital documentados; nombre técnico y registros target abiertos.
- CGN: asunto/referencia, trámite previo y custodia híbrida 2009 agregados al protocolo.
- COMDOC: corregido; ya existía en 2008 para ciertos circuitos, mientras la regla CGN 2010 fija alcance específico y conserva Notas.
- Nota 3672/09, Resolución SGN 41/07, Plan 2009, IDs SISIO y ejecución siguen abiertos.
- Panel: 34 entidades; activos {NUMERATOR}/{SYSTEM_ASSETS}; cobertura {COVERAGE}%.
- SAF355 0/5; ejecución 0/10; seis borradores no enviados; solicitudes enviadas 0.
""", encoding="utf-8")
(HERE / "VEREDICTO_V172.md").write_text("""# Veredicto V172

Avance archivístico sustantivo sin cierre indebido. La web pública archivada queda agotada para el resto de 2016 y 2017-2020 bajo dos prefijos, pero eso no demuestra inexistencia institucional. SIGEN tenía Mesa informatizada y archivo digital reglado antes de 2009; CGN exigía metadatos de referencia y aplicaba controles híbridos trazables en 2009. La búsqueda puede exigir ahora exportaciones, índices, contenedores y equivalencias concretas. No se recuperaron la Nota 3672/09, su asiento receptor, la Resolución 41/07 ni el Plan. Sin promoción bancaria ni solicitud enviada.
""", encoding="utf-8")
(HERE / "AUDITORIA_V172.md").write_text(f"""# Auditoría V172

- Catálogo/copia/hash: 602/602; huecos 0; fuentes nuevas 3.
- Common Crawl: 106 consultas nuevas; 106 `NO_CAPTURE_VALID`, 0 errores, 0 capturas.
- PDF SIGEN 2007: control visual PASS en PDF p.22 / impresa p.21.
- Dos HTML históricos: certificado TLS oficial vencido, excepción declarada; PDF oficial TLS válido.
- Nota/Plan/acto/IDs: abiertos; no se confunde ruta, capacidad o referencia con cuerpo.
- Panel 34, {COVERAGE}%; promociones 0; solicitudes 0; SAF355 0/5; ejecución 0/10.
""", encoding="utf-8")
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V172_A_V173.md").write_text("""# Handover V172 → V173

## Cerrado

- Archivo 602/602; tres fuentes nuevas con procedencia y control visual/TLS explícitos.
- Common Crawl: resto 2016 y 2017-2020 completos; 106 negativos válidos V172, 0 errores, 0 capturas.
- SIGEN: sistema informático de Mesa y Archivo Digital reglado documentados desde 2007.
- CGN: asunto/referencia, trámite previo y paquete híbrido/indexado documentados.
- Corrección: COMDOC existía en 2008; 2010 fija alcance CGN, no creación del sistema.

## Prioridad V173

1. Recuperar cuerpo, anexos e índice/registro de la Resolución SIGEN 41/07.
2. Identificar nombre/esquema de la base SIGEN Mesa 2007-2009 y pedir salida 3672/09.
3. Buscar libro/asiento CGN por asunto/referencia y número previo 0120/09, más soporte/contenedor.
4. Correlacionar salida SIGEN, entrada CGN, SISIO y eventual COMDOC/migración.
5. Reintentar las dos colecciones de frontera 2016 y las colecciones 2013-2015 que quedaron con error, bajo control de salud válido.
6. Mantener seis borradores DRAFT_NOT_SENT, solicitudes 0, SAF355 0/5 y ejecución 0/10.
""", encoding="utf-8")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V171.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint": "V172", "date": "2026-08-31", "master_catalog_entries": 602,
    "physical_local_copies": 602, "physical_local_hash_ok": 602, "remaining_catalog_physical_or_hash_gaps": 0,
    "state": "SOURCE_ARCHIVE_COMPLETE_PUBLIC_ARCHIVE_2016_REMAINDER_AND_2017_2020_SCOPED_COMPLETE_SIGEN_CGN_ROUTES_LOCATED_TARGET_RECORDS_OPEN",
    "analytical_promotion": "NONE_V172_ARCHIVAL_ROUTE_ONLY", "exact_entities": 34,
    "strict_asset_numerator_million_ars": NUMERATOR, "system_assets_million_ars": SYSTEM_ASSETS,
    "strict_coverage_pct": COVERAGE, "strict_coverage_increment_v171_pp": "0",
    "request_drafts_status": "DRAFT_NOT_SENT", "requests_submitted": 0, "responses_received": 0,
    "saf355_certifications_located": 0, "executed_historical_bank_rows_confirmed": 0,
    "plan_sigen_2009_body_located": False, "plan_sigen_2009_approval_act_located": False,
    "note_3672_09_body_located": False, "note_3672_formal_addressee_located": False,
    "note_3672_recipient_identifier_located": False, "note_3672_primary_recipient_registry_route_located": True,
    "sigen_computerized_mesa_capability_located": True, "sigen_resolution_41_2007_reference_located": True,
    "sigen_resolution_41_2007_body_located": False, "cgn_note_subject_prior_reference_rule_located": True,
    "cgn_2009_hybrid_custody_comparator_located": True, "comdoc_operational_by_2008_some_circuits": True,
    "comdoc_2010_creation_claim_corrected": True,
    "commoncrawl_catalog_collections_2013_2020": 74,
    "commoncrawl_exact_prefix_queries_completed": 150, "commoncrawl_exact_prefix_queries_v172": 106,
    "commoncrawl_exact_prefix_service_errors": 40, "commoncrawl_service_errors_v172": 0,
    "commoncrawl_evaluable_query_responses_v172": 106, "commoncrawl_valid_no_capture_v172": 106,
    "commoncrawl_capture_rows_v172": 0, "commoncrawl_2016_remaining_queries_deferred": 0,
    "commoncrawl_2017_2020_queries_completed_v172": 90, "new_v172_sources": 3,
    "historical_server_tls_certificate_expired_disclosed": True,
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V172.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

origin_rows = read_csv(ORIGINS)
origin_by_path = {row["path"]: row for row in origin_rows}
for path in iter_files(HIST_ROOT):
    rel = path.relative_to(CYCLE).as_posix()
    if path in (SIGEN07, CIR17, DISP32):
        origin = "downloaded/preserved V172"
        note = "official source; PDF TLS valid or historical HTML TLS exception disclosed"
    else:
        origin = "generated/preserved V172"
        note = "Common Crawl exact-prefix method or raw diagnostic log"
    origin_by_path[rel] = {"path": rel, "origin": origin, "note": note}
for path in iter_files(SYNC):
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path": rel, "origin": "generated/updated V172", "note": "incremental source synchronization"}
for path in sorted(HERE.iterdir(), key=lambda item: item.name.casefold()):
    if path.is_file():
        rel = path.relative_to(CYCLE).as_posix()
        origin_by_path[rel] = {"path": rel, "origin": "generated/updated V172", "note": "SIGEN-CGN documentary-route checkpoint"}
for path in (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V172.csv", AUDIT / "SOURCE_BACKUP_CENSUS_V172.csv", AUDIT / "SOURCE_PRESERVATION_MISSING_V172.csv", AUDIT / "CURRENT_SOURCE_COMPLETENESS_V172.json"):
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path": rel, "origin": "generated/updated V172", "note": "602-source completeness"}
write_csv(ORIGINS, list(origin_by_path.values()), ["path", "origin", "note"])

transparency = CYCLE / "TRANSPARENCY_README.md"
body = transparency.read_text(encoding="utf-8-sig")
if "## V172 · Mesa SIGEN y custodia híbrida CGN" not in body:
    body += """

## V172 · Mesa SIGEN y custodia híbrida CGN

La Memoria SIGEN 2007 documenta Mesa informatizada y bases del Archivo Digital; la Circular CGN 17/2005 agrega asunto/referencia y trámite previo; la Disposición CGN 32/2009 prueba un circuito híbrido, foliado e indexado con controles de recepción. Se corrige la cronología: COMDOC III ya existía en 2008 para ciertos circuitos y la Circular 04/2010 fija un alcance CGN posterior, no su creación. Common Crawl agregó 106 negativos válidos acotados sin capturas. Ruta y capacidad no se convierten en cuerpo/asiento. Archivo 602/602; panel 34 sin cambio; solicitudes 0.
"""
    transparency.write_text(body, encoding="utf-8")

(REPO / "BACKUP_ACTUALIZACION_2026-08-31.md").write_text(f"""# Backup de actualización · 2026-08-31

- Checkpoint: V172.
- Fuentes: 602/602; +3 oficiales y 106 consultas Common Crawl preservadas.
- SIGEN: Mesa informatizada y Archivo Digital pre-target documentados; acto 41/07/cuerpo 3672 abiertos.
- CGN: asunto/referencia, trámite previo y custodia híbrida 2009 documentados.
- Common Crawl: 106 negativos acotados, 0 errores, 0 capturas.
- Panel: 34; {COVERAGE}% de activos; promociones 0.
- Solicitudes: 0 enviadas; seis DRAFT_NOT_SENT; SAF355 0/5; ejecución 0/10.
""", encoding="utf-8")

(HERE / "qa_v172.py").write_text("""from pathlib import Path
import csv, hashlib, json
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / 'research/ciclo_ajuste'
AUDIT = CYCLE / 'source_audit'
COVERAGE = '63.4406041403540997520463142785031521252747951992299547614348265414453439585848248058817492708499966268585997481191265825'
NEW_IDS = {'e0_sigen_memory_2007_computerized_mesa_and_digital_archive_v172','e0_cgn_circular_17_2005_note_subject_and_prior_reference_v172','e0_cgn_disposition_32_2009_hybrid_mesa_submission_v172'}
def rows(name):
    return list(csv.DictReader((HERE/name).open(encoding='utf-8-sig', newline='')))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
catalog = list(csv.DictReader((REPO/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig', newline='')))
assert len(catalog) == len({r['id'] for r in catalog}) == 602
new = [r for r in catalog if r['id'] in NEW_IDS]
assert len(new) == 3
for r in catalog:
    p = REPO/r['archivo_local'].lstrip('/')
    assert p.is_file() and sha(p) == r['sha256'].lower()
audit = list(csv.DictReader((AUDIT/'MASTER_LOCAL_HASH_VALIDATION_V172.csv').open(encoding='utf-8-sig', newline='')))
assert len(audit) == 602 and all(r['exists']=='True' and r['hash_ok']=='True' for r in audit)
assert (AUDIT/'SOURCE_PRESERVATION_MISSING_V172.csv').read_text(encoding='utf-8-sig').count('\\n') == 1
complete = json.loads((AUDIT/'CURRENT_SOURCE_COMPLETENESS_V172.json').read_text(encoding='utf-8-sig'))
assert complete['checkpoint']=='V172' and complete['master_catalog_entries']==complete['physical_local_copies']==complete['physical_local_hash_ok']==602
assert complete['commoncrawl_exact_prefix_queries_v172']==complete['commoncrawl_valid_no_capture_v172']==106
assert complete['commoncrawl_service_errors_v172']==complete['commoncrawl_capture_rows_v172']==0
assert complete['sigen_computerized_mesa_capability_located'] is True and complete['sigen_resolution_41_2007_body_located'] is False
assert complete['comdoc_operational_by_2008_some_circuits'] is True and complete['comdoc_2010_creation_claim_corrected'] is True
assert complete['requests_submitted']==complete['responses_received']==complete['saf355_certifications_located']==complete['executed_historical_bank_rows_confirmed']==0
execution = rows('E0_COMMONCRAWL_EXACT_PREFIX_EXECUTION_V172.csv')
assert len(execution)==106 and all(r['classification']=='NO_CAPTURE_VALID' for r in execution)
assert {r['run_scope'] for r in execution}=={'HEALTH_CONTROL_2014_49','2016_REMAINING','2017_2020_FULL'}
summary = rows('E0_COMMONCRAWL_QUERY_COMPLETENESS_V172.csv')
total = next(r for r in summary if r['batch']=='V172_TOTAL')
assert total['queries']=='106' and total['valid_no_capture']=='106' and total['service_errors']=='0' and total['captures']=='0'
control = rows('V172_PDF_VISUAL_CONTROL.csv')
assert len(control)==1 and control[0]['pdf_page']=='22' and control[0]['printed_page']=='21' and control[0]['visual_result'].startswith('PASS')
assert len(rows('E0_SIGEN_MESA_DIGITAL_ARCHIVE_CONTINUITY_V172.csv'))==3
assert len(rows('E0_CGN_NOTE_METADATA_AND_HYBRID_CUSTODY_V172.csv'))==6
assert len(rows('E0_COMDOC_SCOPE_CORRECTION_V172.csv'))==3
assert len(rows('E0_SIGEN_RES41_2007_BODY_SEARCH_V172.csv'))==3
keys = rows('E0_REQUEST_SEARCH_KEY_MATRIX_V172.csv')
assert {'SK172_20','SK172_21','SK172_22','SK172_23','SK172_24'} <= {r['key_id'] for r in keys}
objects = rows('E0_V172_REQUEST_OBJECTS.csv')
assert {'RO172_20','RO172_21','RO172_22','RO172_23'} <= {r['row_id'] for r in objects}
assert all(r['status']=='DRAFT_NOT_SENT' for r in objects)
assert objects == rows('E0_V172_REQUEST_OBJECTS_V172.csv')
for name in ('REQUEST_AGN_2018_REPLY_V172.md','REQUEST_BCRA_CRYL_SETTLEMENT_V172.md','REQUEST_BNA_FIRST_STAGE_BLOTTER_V172.md','REQUEST_CAJA_SETTLEMENT_HOLDINGS_V172.md','REQUEST_CNV_CUSTODY_RECORDS_V172.md','REQUEST_ECONOMIA_TESORO_SETTLEMENT_V172.md'):
    text=(HERE/name).read_text(encoding='utf-8-sig')
    assert 'DRAFT_NOT_SENT' in text or 'BORRADOR_NO_ENVIADO' in text
assert 'Adenda V172 · Mesa SIGEN' in (HERE/'REQUEST_ECONOMIA_TESORO_SETTLEMENT_V172.md').read_text(encoding='utf-8-sig')
panel=rows('FOUR_LEG_PASS_PANEL_V172.csv')
assert len(panel)==45 and sum(r['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for r in panel)==34
coverage=rows('STRICT_Q4_FOUR_LEG_COVERAGE_V172.csv')
assert len(coverage)==1 and coverage[0]['asset_coverage_pct']==COVERAGE and coverage[0]['asset_numerator_million_ars']=='61345602.215'
bundle=rows('V172_SOURCE_BUNDLE.csv')
assert len(bundle)==7
for r in bundle:
    p=REPO/r['path'].lstrip('/')
    assert p.is_file() and p.stat().st_size==int(r['bytes']) and sha(p)==r['sha256']
manifest=json.loads((HERE/'MANIFEST_V172.json').read_text(encoding='utf-8-sig'))
assert manifest['checkpoint']=='V172' and manifest['parent_checkpoint']=='V171' and manifest['requests_submitted']==0
assert manifest['commoncrawl_queries_v172']==manifest['commoncrawl_valid_negatives_v172']==106
assert manifest['commoncrawl_service_errors_v172']==manifest['commoncrawl_captures_v172']==0
for r in manifest['files']:
    p=HERE/r['path']; assert p.is_file() and p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
print('V172 QA PASS · 602/602 · new=3 · cc=106/106-valid-negative/0-error/0-capture · SIGEN_CGN_ROUTES=LOCATED · panel=34 · requests=0 · SAF355=0/5 · execution=0/10')
""", encoding="utf-8")

(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")

files = [{"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)} for path in sorted(HERE.iterdir(), key=lambda item: item.name.casefold()) if path.is_file() and path.name != "MANIFEST_V172.json"]
manifest = {
    "checkpoint": "V172", "parent_checkpoint": "V171",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "exact_entities": 34, "strict_coverage_pct": COVERAGE,
    "strict_asset_numerator_million_ars": NUMERATOR, "system_assets_million_ars": SYSTEM_ASSETS,
    "new_promotions": [], "historical_finding": "SIGEN computerized Mesa and Digital Archive route plus CGN note metadata/hybrid custody located; COMDOC chronology corrected",
    "source_archive": "602/602 catalogued physical SHA-valid; three V172 sources added",
    "commoncrawl_queries_v172": 106, "commoncrawl_valid_negatives_v172": 106,
    "commoncrawl_service_errors_v172": 0, "commoncrawl_captures_v172": 0,
    "plan_sigen_2009_body": "NOT_LOCATED", "approval_act": "NOT_LOCATED", "note_3672_09_body": "NOT_LOCATED",
    "sigen_computerized_mesa": "LOCATED_CAPABILITY", "sigen_resolution_41_2007_body": "NOT_LOCATED",
    "cgn_note_metadata_rule": "LOCATED", "cgn_hybrid_custody_comparator": "LOCATED",
    "comdoc_operational_by_2008_some_circuits": True, "comdoc_2010_creation_claim": "CORRECTED",
    "crosswalk_gate": "OPEN", "closed_network_gate": "NO",
    "saf355_certifications": "0/5", "executed_historical_bank_rows": "0/10", "requests_submitted": 0,
    "files": files,
}
(HERE / "MANIFEST_V172.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in iter_files(REPO) if path != global_manifest]
payload = {
    "checkpoint": "V172", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": COVERAGE, "exact_entities": 34, "closed_network_gate": "NO",
    "source_audit": "602 master; 602 physical SHA-valid; three V172 sources added",
    "historical_workstream": "public archive 2016 remainder and 2017-2020 scoped complete; two 2016 boundary collections plus 2013-2015 errors remain; SIGEN/CGN routes narrowed; target bodies/ids and execution open; six drafts not sent",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
tmp = global_manifest.with_suffix(".json.V172tmp")
tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
tmp.replace(global_manifest)

print("V172 BUILD PASS · catalog=602/602 · new=3 · cc=106/106 valid negatives/0 errors/0 captures · SIGEN_CGN_ROUTES=LOCATED · panel=34 · requests=0")
