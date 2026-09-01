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
PARENT = CYCLE / "checkpoints" / "V170"
AUDIT = CYCLE / "source_audit"
SYNC = CYCLE / "inputs" / "source_sync" / "v171"
HIST_ROOT = CYCLE / "inputs" / "historical_retrieval" / "v171"
HIST = HIST_ROOT / "binaries"
QUERY = HIST_ROOT / "query_logs"
METHODS = HIST_ROOT / "methods"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"

COVERAGE = "63.4406041403540997520463142785031521252747951992299547614348265414453439585848248058817492708499966268585997481191265825"
NUMERATOR = "61345602.215"
SYSTEM_ASSETS = "96697695.5"
EXCLUDED_DIRS = {".git", "__pycache__", "tmp", "node_modules"}

DISP = HIST / "cgn_disposition_41_1996_mesa_entradas_registry.html"
CIRC = HIST / "cgn_circular_04_2010_comdoc_note_routes.html"
CC2014 = QUERY / "commoncrawl_exact_prefix_2014.csv"
CC2015 = QUERY / "commoncrawl_exact_prefix_2015.csv"
CC2016 = QUERY / "commoncrawl_exact_prefix_2016_boundary.csv"
SCANNER = METHODS / "commoncrawl_exact_prefix_scanner_v171.ps1"
EXPECTED = {
    DISP: (5287, "e5a912148b9fb0298812c1370967b8835dce00dd46b8c2ce21b3c8dab46d0475"),
    CIRC: (6381, "6ff30b36e9743955a4e505c90d238799edb5e20eb4dba304b35a00b2f7d5b396"),
    CC2014: (5420, "a55c8a1eddcbd0639736f8f6f22ec33a537b59cb0b52972e6f81465deec34dcf"),
    CC2015: (6588, "884ad3bf689b532df8332addc1d9a8d5a14325203bca9eed6011122eaeef5dcb"),
    CC2016: (1420, "0b9cb8dab8c0f42622c518ae0dee12d83d4643f53a2bd6b08f05f84e83f134d8"),
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
    skip_names = {
        "MANIFEST_V170.json", "README_V170.md", "VEREDICTO_V170.md", "AUDITORIA_V170.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V170_A_V171.md", "V170_SOURCE_BUNDLE.csv",
        "V170_PUBLIC_SEARCH_LOG.csv", "E0_PLAN_2009_ARCHIVE_RECOVERY_NOTE_V170.md",
        "E0_SIGEN_ARCHIVAL_INDEX_RECOVERY_NOTE_V170.md", "E0_FISCAL_RECONSTRUCTION_V170.md",
        "CNV_ATTACHMENT_ANALYTIC_REVIEW_V170.md",
    }
    for source in sorted(PARENT.iterdir(), key=lambda path: path.name.casefold()):
        if not source.is_file() or source.name in skip_names or source.name.startswith(("build_", "qa_")):
            continue
        target = HERE / source.name.replace("V170", "V171")
        target.write_text(source.read_text(encoding="utf-8-sig").replace("V170", "V171"), encoding="utf-8")


clone_parent()
for path, (size, digest) in EXPECTED.items():
    assert path.is_file() and path.stat().st_size == size and sha256(path) == digest

sources = [
    {
        "id": "e0_cgn_disposition_41_1996_mandatory_entry_and_internal_pass_registry_v171",
        "tema": "ciclo_ajuste_e0_fiscal",
        "institucion": "Contaduría General de la Nación",
        "titulo": "Disposición CGN 41/1996 · ingreso obligatorio por Mesa y registro de pases internos",
        "url_original": "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/1996/dis41.htm",
        "archivo_local": "/" + DISP.relative_to(REPO).as_posix(),
        "fecha_descarga": "2026-08-31", "fecha_publicacion": "1996-06-26",
        "codigo_serie": "Disposición CGN 41/1996", "periodo_utilizado": "1996-2010; aplicable a 2009",
        "tipo": "HTML oficial preservado · TLS histórico vencido documentado",
        "sha256": EXPECTED[DISP][1],
        "nota": "V171: arts. 1-4 obligan ingreso por Mesa CGN, control de documentación y registro de pases en el sistema de seguimiento. Fija productor registral para una respuesta recibida en 2009; no contiene la Nota 3672/09.",
    },
    {
        "id": "e0_cgn_circular_04_2010_comdoc_transition_and_note_route_v171",
        "tema": "ciclo_ajuste_e0_fiscal",
        "institucion": "Contaduría General de la Nación",
        "titulo": "Circular CGN 4/2010 · transición COMDOC III y continuidad de actuaciones por Nota",
        "url_original": "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/2010/cir04.htm",
        "archivo_local": "/" + CIRC.relative_to(REPO).as_posix(),
        "fecha_descarga": "2026-08-31", "fecha_publicacion": "2010-03-22",
        "codigo_serie": "Circular CGN 04/2010", "periodo_utilizado": "2010; límite temporal para 2009",
        "tipo": "HTML oficial preservado · TLS histórico vencido documentado",
        "sha256": EXPECTED[CIRC][1],
        "nota": "V171: fecha la ruta COMDOC III para expedientes ministeriales desde 2010 y mantiene diversos trámites internos por Nota ante Mesa CGN. Impide exigir GDE y desaconseja usar sólo COMDOC para una nota de 2009.",
    },
]

catalog = read_csv(CATALOG)
catalog_fields = list(catalog[0])
by_id = {row["id"]: row for row in catalog}
for row in sources:
    by_id[row["id"]] = row
catalog = list(by_id.values())
write_csv(CATALOG, catalog, catalog_fields)
assert len(catalog) == len(by_id) == 599

audit_rows = []
for row in catalog:
    local = REPO / row["archivo_local"].lstrip("/")
    actual = sha256(local) if local.is_file() else ""
    audit_rows.append({
        "id": row["id"], "archivo_local": row["archivo_local"], "exists": str(local.is_file()),
        "sha_catalog": row["sha256"].lower(), "sha_actual": actual,
        "hash_ok": str(local.is_file() and bool(row["sha256"]) and actual == row["sha256"].lower()),
    })
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V171.csv", audit_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V171.csv", audit_rows)
missing = [row for row in audit_rows if row["exists"] != "True" or row["hash_ok"] != "True"]
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V171.csv", missing, list(audit_rows[0]))
assert not missing

raw_specs = [("2014_FULL", CC2014), ("2015_FULL", CC2015), ("2016_BOUNDARY", CC2016)]
execution = []
for scope, path in raw_specs:
    for row in read_csv(path):
        item = dict(row)
        item["run_scope"] = scope
        item["evidentiary_effect"] = "SCOPED_NO_CAPTURE_FOR_COLLECTION_HOST" if row["classification"] == "NO_CAPTURE_VALID" else "NONE_SERVICE_ERROR"
        execution.append(item)
write_csv(HERE / "E0_COMMONCRAWL_EXACT_PREFIX_EXECUTION_V171.csv", execution)
assert len(execution) == 40
assert sum(row["classification"] == "NO_CAPTURE_VALID" for row in execution) == 4
assert sum(row["classification"] == "SERVICE_ERROR" for row in execution) == 36

query_summary = [
    {"batch": "2014_FULL", "collections_targeted": "8", "hosts_per_collection": "2", "queries": "16", "valid_no_capture": "4", "service_errors": "12", "captures": "0", "pending_queries": "0", "decision": "VALID_NEGATIVES_ONLY_FOR_2014_49_AND_2014_52_BOTH_HOSTS"},
    {"batch": "2015_FULL", "collections_targeted": "10", "hosts_per_collection": "2", "queries": "20", "valid_no_capture": "0", "service_errors": "20", "captures": "0", "pending_queries": "0", "decision": "NO_EVIDENTIARY_RESULT_SERVICE_FAILURE"},
    {"batch": "2016_BOUNDARY", "collections_targeted": "2_of_9", "hosts_per_collection": "2", "queries": "4", "valid_no_capture": "0", "service_errors": "4", "captures": "0", "pending_queries": "14", "decision": "FULL_BATCH_DEFERRED_AFTER_4_OF_4_BOUNDARY_ERRORS"},
    {"batch": "V171_TOTAL", "collections_targeted": "20_distinct", "hosts_per_collection": "2", "queries": "40", "valid_no_capture": "4", "service_errors": "36", "captures": "0", "pending_queries": "14", "decision": "ZERO_CAPTURES_FOUR_SCOPED_NEGATIVES_ERRORS_NOT_ABSENCE"},
]
write_csv(HERE / "E0_COMMONCRAWL_QUERY_COMPLETENESS_V171.csv", query_summary)

coverage_rows = read_csv(HERE / "E0_COMMONCRAWL_COLLECTION_COVERAGE_V171.csv")
run_by_collection = {}
for row in execution:
    run_by_collection.setdefault(row["collection"], []).append(row)
for row in coverage_rows:
    cid = row["collection_id"]
    if cid in run_by_collection:
        values = run_by_collection[cid]
        if len(values) == 2 and all(item["classification"] == "NO_CAPTURE_VALID" for item in values):
            row["exact_prefix_status"] = "NO_CAPTURE_VALID_2_HOSTS"
            row["evidentiary_effect"] = "SCOPED_COLLECTION_HOST_NEGATIVE"
        elif len(values) == 2 and all(item["classification"] == "SERVICE_ERROR" for item in values):
            row["exact_prefix_status"] = "SERVICE_ERROR_2_HOSTS"
            row["evidentiary_effect"] = "NONE_NOT_NEGATIVE"
    elif row["year"] == "2016":
        row["exact_prefix_status"] = "DEFERRED_AFTER_4_OF_4_BOUNDARY_ERRORS"
        row["evidentiary_effect"] = "NONE_NOT_QUERIED"
write_csv(HERE / "E0_COMMONCRAWL_COLLECTION_COVERAGE_V171.csv", coverage_rows)

filenames = [
    "Anexo F - Cuadro 10 - Superv y Coord UAI.pdf",
    "Anexo F - Cuadro 11 - Fiscalización.pdf",
    "Anexo F - Cuadro 12 - Auditorías.pdf",
    "Anexo F - Cuadro 13 - Otras competencias.pdf",
    "Anexo F - Cuadro 14 - UAI Conducción.pdf",
    "Anexo F - Cuadro 15 - UAI Superv Gral SCI.pdf",
    "Anexo F - Cuadro 16 - UAI Auditorías.pdf",
    "Anexo F - Cuadro 17 - UAI Otras actividades.pdf",
    "Anexo F - Cuadro 18.pdf",
    "Anexo F - Cuadro 8 - Normativa.pdf",
    "Anexo F - Cuadro 9 - Supervisión General del SCI.pdf",
    "Anexo G - Capacitacion 2009.pdf",
    "Plan SIGEN 2009.pdf",
    "planred2009.pdf",
]
filename_rows = [{
    "search_id": f"FN171_{index:02d}", "exact_query": f'"{name}"', "target": name,
    "surface": "public web + official/library/repository/archive exact-title search",
    "result": "no target body returned", "classification": "SEARCH_ENGINE_NEGATIVE_SCOPED",
    "limit": "No prueba inexistencia ni ausencia en custodia; el nombre sí consta en la página archivada oficial.",
} for index, name in enumerate(filenames, 1)]
write_csv(HERE / "E0_PLAN_2009_EXACT_FILENAME_PUBLIC_SEARCH_V171.csv", filename_rows)

registry = [
    {"route_id": "RG171_01", "source": "Disposición CGN 41/1996 art. 1", "date_scope": "vigente como regla histórica; aplicable a 2009", "rule": "toda documentación que ingrese a CGN debe hacerlo por Mesa de Entradas", "target_effect": "debe existir asiento o búsqueda negativa fundada para Nota 3672/09", "limit": "no recupera la nota", "status": "PRIMARY_RECIPIENT_REGISTRY_IDENTIFIED"},
    {"route_id": "RG171_02", "source": "Disposición CGN 41/1996 art. 2", "date_scope": "1996-2009", "rule": "Mesa controla la documentación de ingreso", "target_effect": "pedir campos de control, recepción y remitente", "limit": "no nombra sistema", "status": "CONTROL_PRODUCER_IDENTIFIED"},
    {"route_id": "RG171_03", "source": "Disposición CGN 41/1996 art. 4", "date_scope": "1996-2009", "rule": "los pases entre Direcciones deben indicar motivo y registrarse en el sistema de seguimiento de expedientes", "target_effect": "pedir historial de pases y unidad receptora", "limit": "nombre técnico del sistema abierto", "status": "INTERNAL_PASS_LOG_DUTY_IDENTIFIED"},
    {"route_id": "RG171_04", "source": "Circular CGN 04/2010", "date_scope": "desde 2010-02/03", "rule": "expedientes originados por órganos del Ministerio ingresan por Mesa central mediante COMDOC III", "target_effect": "COMDOC es ruta subsidiaria para pases o expediente posterior", "limit": "no debe retrotraerse automáticamente a 2009", "status": "COMDOC_TEMPORAL_BOUNDARY"},
    {"route_id": "RG171_05", "source": "Circular CGN 04/2010", "date_scope": "2010", "rule": "trámites internos como respuestas a parametrizados y cuadros de Cuenta continúan por Nota ante Mesa CGN", "target_effect": "buscar serie Nota y registro CGN además de COMDOC", "limit": "comparador cercano, no cuerpo target", "status": "NOTE_ROUTE_CONTINUITY"},
    {"route_id": "RG171_06", "source": "Cuenta de Inversión 2009 UEPEX + normas CGN", "date_scope": "Nota 3672/09", "rule": "CGN es receptora contextual y Mesa es productor registral obligatorio", "target_effect": "consulta primaria: número SIGEN, remitente, asunto, fecha, Nota 0120/09, pases y contenedor", "limit": "destinatario nominal y número de entrada abiertos", "status": "TESTABLE_REGISTRY_QUERY"},
]
write_csv(HERE / "E0_CGN_LEGACY_NOTE_REGISTRY_ROUTE_V171.csv", registry)

scan = read_csv(HERE / "E0_PLAN_2009_LATE_ARCHIVE_COLLECTION_SCAN_V171.csv")
scan.extend([
    {"scan_id": "LA171_13", "surface": "Common Crawl exact-prefix", "period_or_collection": "2014 · 8 collections × 2 hosts", "target": "SIGEN plananualpdfs exact prefix", "result": "4 valid no-capture responses; 12 service errors; 0 captures", "classification": "FOUR_SCOPED_NEGATIVES_TWELVE_ERRORS", "service_state": "MIXED", "next_step": "retry only errors; do not generalize four negatives"},
    {"scan_id": "LA171_14", "surface": "Common Crawl exact-prefix", "period_or_collection": "2015 · 10 collections × 2 hosts", "target": "SIGEN plananualpdfs exact prefix", "result": "20 service errors; 0 evaluable responses", "classification": "SERVICE_ERRORS_NOT_NEGATIVES", "service_state": "ERROR", "next_step": "retry after service recovery"},
    {"scan_id": "LA171_15", "surface": "Common Crawl boundary control", "period_or_collection": "2016 · first/last collections × 2 hosts", "target": "SIGEN plananualpdfs exact prefix", "result": "4 of 4 service errors; full batch deferred", "classification": "BOUNDARY_FAILURE_BATCH_DEFERRED", "service_state": "ERROR", "next_step": "run remaining 14 queries only after valid control"},
    {"scan_id": "LA171_16", "surface": "public/library/repository/archive exact-title search", "period_or_collection": "14 archived official filenames", "target": "Plan 2009, Annex F 8-18, Annex G, Plan Red", "result": "0 target bodies returned", "classification": "FOURTEEN_FILENAME_NEGATIVE_SCOPED", "service_state": "OK", "next_step": "institutional custody request"},
    {"scan_id": "LA171_17", "surface": "CGN Disposition 41/1996", "period_or_collection": "record rule applicable to 2009", "target": "recipient registry for Note 3672/09", "result": "mandatory Mesa entry and internal-pass log identified", "classification": "PRIMARY_REGISTRY_ROUTE_LOCATED", "service_state": "OK", "next_step": "request exact entry and pass history"},
    {"scan_id": "LA171_18", "surface": "CGN Circular 04/2010", "period_or_collection": "2010 transition comparator", "target": "COMDOC versus Note route", "result": "COMDOC boundary dated; internal Note route persists", "classification": "TEMPORAL_DOCUMENT_ROUTE_BOUNDARY_LOCATED", "service_state": "OK", "next_step": "do not make COMDOC exclusive for 2009"},
    {"scan_id": "LA171_19", "surface": "SIGEN/Normativa/Boletín Oficial exact-date search", "period_or_collection": "approval 2008-12-15", "target": "Plan SIGEN 2009 approval act", "result": "no act number or body located", "classification": "PUBLIC_ACT_SEARCH_NEGATIVE_SCOPED", "service_state": "OK", "next_step": "approval registry and file remain requested"},
])
write_csv(HERE / "E0_PLAN_2009_LATE_ARCHIVE_COLLECTION_SCAN_V171.csv", scan)

approval = read_csv(HERE / "E0_PLAN_2009_APPROVAL_ACT_SEARCH_V171.csv")
approval.extend([
    {"test_id": "AA171_20", "question": "¿El barrido exacto de fecha, SIGEN, InfoLEG y Boletín Oficial reveló el acto?", "evidence": "consultas públicas exactas 31/08/2026", "result": "No apareció número ni cuerpo", "classification": "PUBLIC_SEARCH_NEGATIVE_SCOPED", "remaining_gap": "registro de aprobación; expediente; firma; comunicación"},
    {"test_id": "AA171_21", "question": "¿Qué sigue probado?", "evidence": "Memoria SIGEN 2008 preservada", "result": "El Plan fue aprobado el 15/12/2008; tipo y número del acto siguen abiertos", "classification": "EXISTENCE_DATE_CONFIRMED_ACT_OPEN", "remaining_gap": "acto original o certificación de custodia"},
])
write_csv(HERE / "E0_PLAN_2009_APPROVAL_ACT_SEARCH_V171.csv", approval)

note_route = read_csv(HERE / "E0_NOTE_3672_ARCHIVAL_SEARCH_V171.csv")
note_route.extend([
    {"route_id": "N171_20", "surface": "CGN Mesa de Entradas bajo Disposición 41/1996", "target": "ingreso Nota SIGEN 3672/09 GSEyP", "result": "productor registral y deber de asiento identificados", "status": "PRIMARY_REGISTRY_DUTY_LOCATED_RECORD_OPEN", "required_record": "asiento; fecha; remitente; destinatario; asunto; soporte; contenedor"},
    {"route_id": "N171_21", "surface": "CGN sistema de seguimiento de expedientes", "target": "pases internos de Nota 3672/09", "result": "deber de registrar pases identificado; nombre del sistema y entrada abiertos", "status": "PASS_HISTORY_ROUTE_LOCATED", "required_record": "dirección origen/destino; fecha; motivo; usuario; estado; expediente/carpeta"},
    {"route_id": "N171_22", "surface": "COMDOC III según Circular 04/2010", "target": "ruta subsidiaria posterior", "result": "COMDOC III no debe tratarse como repositorio exclusivo para documento de 2009", "status": "COMDOC_EXCLUSIVITY_REJECTED", "required_record": "consulta subsidiaria y explicación de migración/ausencia"},
])
write_csv(HERE / "E0_NOTE_3672_ARCHIVAL_SEARCH_V171.csv", note_route)

keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V171.csv")
keys.extend([
    {"key_id": "SK171_20", "request_id": "REQ133_ECON", "key_group": "mandatory_cgn_entry_registry", "exact_key": "Mesa CGN 2009 · ingreso Nota SIGEN 3672/09 GSEyP · antecedente Nota 0120/09 DAIF", "search_purpose": "recuperar identificador receptor y cuerpo", "source_or_basis": "Disposición CGN 41/1996 arts. 1-2", "caveat": "pedir negativo fundado si no aparece"},
    {"key_id": "SK171_21", "request_id": "REQ133_ECON", "key_group": "legacy_internal_pass_log", "exact_key": "sistema de seguimiento CGN · pases de Nota 3672/09 · 2009-2010", "search_purpose": "reconstruir destinatario y lifecycle", "source_or_basis": "Disposición CGN 41/1996 art. 4", "caveat": "nombre del sistema abierto"},
    {"key_id": "SK171_22", "request_id": "REQ133_ECON", "key_group": "nonexclusive_comdoc_secondary", "exact_key": "COMDOC III · 3672/09 · SIGEN · 0120/09 DAIF", "search_purpose": "detectar pase o migración posterior", "source_or_basis": "Circular CGN 04/2010", "caveat": "no usar como única base para negativo 2009"},
    {"key_id": "SK171_23", "request_id": "REQ155_SIGEN", "key_group": "sender_recipient_correlation", "exact_key": "salida SIGEN 3672/09 + ingreso Mesa CGN + alta SISIO", "search_purpose": "correlacionar tres identificadores", "source_or_basis": "Cuenta 2009 + reglas CGN + Resolución SIGEN 15/2006", "caveat": "ninguna capa sustituye a las otras"},
])
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V171.csv", keys)

objects = read_csv(HERE / "E0_V171_REQUEST_OBJECTS.csv")
objects.extend([
    {"row_id": "RO171_20", "object_id": "CGN_2009_MANDATORY_ENTRY_3672", "custodian": "CGN · Mesa de Entradas/Archivo/DAIF", "exact_record": "asiento obligatorio de ingreso Nota SIGEN 3672/09 GSEyP", "period": "2009", "minimum_fields": "número entrada; fecha/hora; remitente; destinatario; asunto; soporte; contenedor; adjuntos", "closure_rule": "Copia o negativa que identifique registro, período, claves y resultado.", "status": "DRAFT_NOT_SENT"},
    {"row_id": "RO171_21", "object_id": "CGN_2009_INTERNAL_PASS_HISTORY_3672", "custodian": "CGN · sistema de seguimiento/Archivo", "exact_record": "historial de pases internos vinculados a Nota 3672/09", "period": "2009-2010", "minimum_fields": "áreas; fechas; motivos; usuarios; estados; expediente/carpeta; disposición final", "closure_rule": "Exportación íntegra o certificado de búsqueda por sistemas y series.", "status": "DRAFT_NOT_SENT"},
    {"row_id": "RO171_22", "object_id": "CGN_LEGACY_TO_COMDOC_MIGRATION", "custodian": "CGN / Economía · Archivo y COMDOC", "exact_record": "tabla o regla de migración de notas 2009 a COMDOC/GDE", "period": "2009-2017", "minimum_fields": "sistema origen; sistema destino; serie; rango; fecha; integridad; descarte/transferencia", "closure_rule": "No aceptar negativo basado sólo en COMDOC sin explicar legado.", "status": "DRAFT_NOT_SENT"},
])
write_csv(HERE / "E0_V171_REQUEST_OBJECTS.csv", objects)
write_csv(HERE / "E0_V171_REQUEST_OBJECTS_V171.csv", objects)

breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V171.csv")
breaks.extend([
    {"break_id": "valid_404_json_no_capture_not_transport_error_v171", "dimension": "archive_query", "problem": "Un 404 JSON 'No Captures found' es respuesta evaluable; un timeout/000/5xx no lo es.", "rule": "Contar sólo el primero como negativo acotado a colección y host.", "status": "FROZEN_V171", "evidence": "V171 Common Crawl execution"},
    {"break_id": "boundary_failure_stops_batch_v171", "dimension": "service_control", "problem": "2016 devolvió 4/4 errores en primera y última colección.", "rule": "Diferir el resto hasta que un control responda; no multiplicar errores.", "status": "FROZEN_V171", "evidence": "V171 2016 boundary log"},
    {"break_id": "mandatory_registry_route_not_target_record_v171", "dimension": "document_routing", "problem": "La norma prueba dónde debía registrarse la nota, no que el asiento haya sido recuperado.", "rule": "Usar la ruta para un pedido testable y mantener cuerpo/id abiertos.", "status": "FROZEN_V171", "evidence": "CGN Disposition 41/1996"},
    {"break_id": "comdoc_2010_not_exclusive_for_2009_v171", "dimension": "temporal_system", "problem": "COMDOC III aparece en la regla de 2010 y varias actuaciones seguían por Nota.", "rule": "No aceptar búsqueda exclusiva en COMDOC como negativo de una nota 2009.", "status": "FROZEN_V171", "evidence": "CGN Circular 04/2010"},
    {"break_id": "tls_expired_transport_must_be_disclosed_v171", "dimension": "provenance", "problem": "El servidor oficial histórico presentó certificado TLS vencido.", "rule": "Registrar excepción, hash y cotejo del contenido; no describir como TLS validado.", "status": "FROZEN_V171", "evidence": "V171 source provenance"},
])
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V171.csv", breaks)

addendum = """

## Adenda V171 · registro obligatorio CGN y corte temporal COMDOC

La Disposición CGN Nº 41/1996 obliga a que toda documentación que ingrese a la Contaduría lo haga por Mesa de Entradas, atribuye a esa Mesa el control del ingreso y ordena registrar en el sistema de seguimiento los pases entre Direcciones con su motivo. Para la Nota SIGEN Nº 3672/09 GSEyP se solicita, por ello, el asiento receptor completo y el historial de pases: número de entrada, fecha y hora, remitente, destinatario, asunto, soporte, contenedor, adjuntos, áreas, fechas, motivos, usuarios y estado final. La Circular CGN Nº 04/2010 fecha la ruta COMDOC III para ciertos expedientes desde 2010 y confirma que diversos trámites internos continuaban por Nota ante la Mesa de la CGN. En consecuencia, una búsqueda limitada a COMDOC o GDE no cierra una nota de 2009: debe abarcar libro/registro de Mesa, sistema legado de seguimiento, archivo, DAIF, eventuales migraciones y disposiciones documentales. Si no se localiza, se pide certificado de búsqueda que identifique sistemas, fondos/series, período, claves exactas y resultado. Estado DRAFT_NOT_SENT; solicitudes enviadas 0.
"""
for name in ("REQUEST_ECONOMIA_TESORO_SETTLEMENT_V171.md", "REQUEST_SUBMISSION_CHECKLIST_V171.md"):
    path = HERE / name
    body = path.read_text(encoding="utf-8-sig")
    if "Adenda V171 · registro obligatorio CGN" not in body:
        path.write_text(body + addendum, encoding="utf-8")

strict = read_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V171.csv")
strict[0]["coverage_set"] = "V171 strict 34-entity set; unchanged from V170"
strict[0]["v161_change"] = "V171: no banking promotion; numerator and coverage unchanged from V170."
write_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V171.csv", strict)

public_log = [{
    "log_id": row["scan_id"], "surface": row["surface"], "query_or_target": row["target"],
    "result": row["result"], "classification": row["classification"], "limit_or_next_step": row["next_step"],
} for row in scan]
public_log.extend({
    "log_id": row["search_id"], "surface": row["surface"], "query_or_target": row["exact_query"],
    "result": row["result"], "classification": row["classification"], "limit_or_next_step": row["limit"],
} for row in filename_rows)
write_csv(HERE / "V171_PUBLIC_SEARCH_LOG.csv", public_log)

recovery = f"""# Recuperación archivística · V171

Common Crawl: se ejecutaron 40 consultas nuevas. En 2014, cuatro respuestas válidas —colecciones 2014-49 y 2014-52, ambos hosts— informaron ausencia de capturas; doce consultas fallaron. En 2015, las veinte fallaron. En 2016, el control de primera y última colección falló 4/4 y el resto se difirió. Resultado: 4 negativos estrictamente acotados, 36 errores, 0 capturas; ningún error se convierte en ausencia. Los catorce nombres oficiales del Plan 2009 fueron buscados exactamente sin recuperar cuerpos. El acto aprobatorio continúa abierto; la Memoria prueba sólo la aprobación del 15/12/2008.

La Disposición CGN 41/1996 identifica el productor registral primario de la Nota 3672/09: Mesa de Entradas y el sistema de seguimiento de pases. La Circular CGN 04/2010 fija el límite COMDOC y prueba continuidad de trámites por Nota. Por ello, COMDOC/GDE no puede ser la única superficie de un negativo 2009. Se piden asiento, historial, cuerpo, migración y, en su defecto, negativo fundado por sistema y serie. Las dos fuentes se preservaron desde el dominio oficial con SHA-256; el certificado TLS histórico estaba vencido y esa excepción queda declarada. Archivo 599/599; panel 34 y {COVERAGE}%; seis borradores DRAFT_NOT_SENT, solicitudes 0, SAF355 0/5 y ejecución 0/10.
"""
for name in ("E0_PLAN_2009_ARCHIVE_RECOVERY_NOTE_V171.md", "E0_SIGEN_ARCHIVAL_INDEX_RECOVERY_NOTE_V171.md", "E0_FISCAL_RECONSTRUCTION_V171.md"):
    (HERE / name).write_text(recovery, encoding="utf-8")
(HERE / "CNV_ATTACHMENT_ANALYTIC_REVIEW_V171.md").write_text(f"""# Revisión analítica acumulada V171

Panel congelado: 34 entidades y {COVERAGE}% de activos. V171 no promueve bancos. Agrega dos normas CGN que convierten la Nota 3672/09 en una búsqueda registral testable y documentan el corte temporal de COMDOC. Common Crawl aporta cuatro negativos acotados, 36 errores y cero capturas. Cuerpos, acto, asiento, IDs SISIO y ejecución siguen abiertos. Seis pedidos DRAFT_NOT_SENT; SAF355 0/5 y ejecución 0/10.
""", encoding="utf-8")

bundle_specs = [
    ("CGN_DISPOSITION_41_1996", DISP, sources[0]["url_original"], "mandatory entry and pass registry"),
    ("CGN_CIRCULAR_04_2010", CIRC, sources[1]["url_original"], "COMDOC temporal boundary and Note continuity"),
    ("COMMONCRAWL_EXACT_PREFIX_2014", CC2014, "generated retrieval log", "4 scoped negatives / 12 errors"),
    ("COMMONCRAWL_EXACT_PREFIX_2015", CC2015, "generated retrieval log", "20 errors"),
    ("COMMONCRAWL_2016_BOUNDARY", CC2016, "generated retrieval log", "4/4 boundary errors"),
    ("COMMONCRAWL_SCANNER_V171", SCANNER, "generated retrieval method", "resume/retry and boundary controls"),
]
bundle = [{"role": role, "path": "/" + path.relative_to(REPO).as_posix(), "url": url, "bytes": str(path.stat().st_size), "sha256": sha256(path), "analytic_use": use} for role, path, url, use in bundle_specs]
write_csv(HERE / "V171_SOURCE_BUNDLE.csv", bundle)

SYNC.mkdir(parents=True, exist_ok=True)
sync_rows = [{
    "role": "V171_PUBLIC_SOURCE", "relative_path": row["archivo_local"], "source_url": row["url_original"],
    "size_bytes": str((REPO / row["archivo_local"].lstrip("/")).stat().st_size), "sha256": row["sha256"],
    "format_verification": "HTML_EXPECTED_TITLE_AND_SUBSTANTIVE_TEXT_TLS_EXCEPTION_DISCLOSED",
} for row in sources]
write_csv(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V171.csv", sync_rows)
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V171.csv", scan)
(SYNC / "SOURCE_SYNC_REPORT_V171.md").write_text("""# Sincronización incremental de fuentes · V171

- Catálogo: 599/599 copias locales y SHA-256 válido; brecha 0.
- Nuevas fuentes: Disposición CGN 41/1996 y Circular CGN 04/2010.
- Transporte: servidor oficial con certificado TLS vencido; excepción, hash y cotejo de contenido documentados.
- Derivados: 40 consultas Common Crawl, scanner y matrices de búsqueda exacta preservados.
- Plan 2009, acto, Nota 3672/09, ingreso e IDs SISIO siguen abiertos.
""", encoding="utf-8")
(SYNC / "qa_source_sync_v171.py").write_text("""from pathlib import Path
import csv, hashlib
root = Path(__file__).resolve().parents[5]
rows = list(csv.DictReader(Path(__file__).with_name('SOURCE_SYNC_FILE_MANIFEST_V171.csv').open(encoding='utf-8-sig', newline='')))
assert len(rows) == 2
for row in rows:
    path = root / row['relative_path'].lstrip('/')
    assert path.is_file() and path.stat().st_size == int(row['size_bytes'])
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
    text = path.read_text(encoding='cp1252', errors='replace')
    assert 'Contadur' in text and 'Mesa de Entradas' in text
print('SOURCE SYNC V171 PASS · 2/2')
""", encoding="utf-8")

local_census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V171.csv")
for source in sources:
    local = REPO / source["archivo_local"].lstrip("/")
    local_census.append({
        "source_id": source["id"], "institution": source["institucion"], "artifact": source["titulo"],
        "url": source["url_original"], "local_path": source["archivo_local"], "sha256": source["sha256"],
        "bytes": str(local.stat().st_size), "period_coverage": source["periodo_utilizado"],
        "variable_families": "Nota3672;CGN;Mesa_de_Entradas;legacy_registry;COMDOC;document_route",
        "primary_source": "YES", "preserved": "YES", "method_breaks": "route source not target body",
        "use_status": "E0_USABLE_RECORD_ROUTE", "caveat": source["nota"],
    })
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V171.csv", local_census)

archival = read_csv(HERE / "ARCHIVAL_PROVENANCE_V171.csv")
for source in sources:
    local = REPO / source["archivo_local"].lstrip("/")
    archival.append({
        "source_id": source["id"], "original_url": source["url_original"], "retrieval_url": source["url_original"],
        "capture_timestamp": "2026-08-31", "cdx_digest": "N/A_DIRECT_TLS_CERT_EXPIRED_INSECURE_TRANSPORT",
        "local_path": source["archivo_local"], "sha256": source["sha256"], "bytes": str(local.stat().st_size),
        "provenance_note": source["nota"] + " Descarga inicial segura falló por certificado expirado; copia preservada con excepción explícita y contenido cotejado con índice público.",
    })
write_csv(HERE / "ARCHIVAL_PROVENANCE_V171.csv", archival)

refs = HERE / "SOURCE_REFERENCES_V171.md"
with refs.open("a", encoding="utf-8") as handle:
    handle.write("\n## V171 · registro CGN y corte COMDOC\n")
    for source in sources:
        handle.write(f"\n- `{source['id']}` · {source['titulo']} · {source['url_original']} · `{source['archivo_local']}` · `{source['sha256']}`\n")
    handle.write("\n- Ambas fuentes identifican la ruta de registro; no sustituyen la Nota 3672/09 ni su asiento. La excepción TLS queda en la procedencia.\n")

retrieval = HERE / "RETRIEVAL_LOG_V171.md"
with retrieval.open("a", encoding="utf-8") as handle:
    handle.write("\n## V171 · resultados nuevos\n\n- Common Crawl: 40 consultas; 4 negativos válidos acotados, 36 errores, 0 capturas.\n- Catorce títulos exactos: 0 cuerpos.\n- CGN: deber de asiento y registro de pases localizado; COMDOC no exclusivo para 2009.\n")

(HERE / "README_V171.md").write_text(f"""# Checkpoint V171

- Archivo: 599/599 copias locales con hash válido; +2 fuentes CGN y 4 derivados de consulta/método.
- Common Crawl V171: 40 consultas, 4 negativos válidos acotados, 36 errores técnicos, 0 capturas; 2016 completo diferido tras 4/4 fallas de frontera.
- Plan 2009: 14 nombres exactos buscados; 14 cuerpos y acto aprobatorio aún no localizados.
- Nota 3672/09: Mesa CGN y registro de pases identificados como ruta primaria; cuerpo, destinatario formal y número de entrada abiertos.
- COMDOC: ruta subsidiaria, no repositorio exclusivo para una nota de 2009.
- Panel: 34 entidades; activos {NUMERATOR}/{SYSTEM_ASSETS}; cobertura {COVERAGE}%.
- SAF355 0/5; ejecución 0/10; seis borradores no enviados; solicitudes enviadas 0.
""", encoding="utf-8")
(HERE / "VEREDICTO_V171.md").write_text("""# Veredicto V171

Avance registral sustantivo sin cierre indebido. La propia normativa CGN identifica dónde debía registrarse una respuesta recibida en 2009 y obliga a registrar sus pases internos. La circular de 2010 impide usar una búsqueda exclusiva en COMDOC/GDE como prueba de inexistencia. Common Crawl sólo aporta cuatro negativos acotados; treinta y seis errores no cuentan. No se recuperaron el Plan, el acto ni la Nota 3672/09. Sin promoción bancaria ni solicitud enviada.
""", encoding="utf-8")
(HERE / "AUDITORIA_V171.md").write_text(f"""# Auditoría V171

- Catálogo/copia/hash: 599/599; huecos 0; fuentes nuevas 2.
- Common Crawl: 40 consultas nuevas; 4 `NO_CAPTURE_VALID`, 36 `SERVICE_ERROR`, 0 capturas.
- Títulos Plan 2009: 14/14 consultados; 0 cuerpos; negativo de superficie pública únicamente.
- Nota 3672/09: productor registral primario y deber de pases identificados; asiento/cuerpo/IDs abiertos.
- Transporte de dos HTML históricos: certificado TLS oficial vencido, excepción declarada y SHA-256 preservado.
- Panel 34, {COVERAGE}%; promociones 0; solicitudes 0; SAF355 0/5; ejecución 0/10.
""", encoding="utf-8")
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V171_A_V172.md").write_text("""# Handover V171 → V172

## Cerrado

- Archivo 599/599; dos normas CGN nuevas preservadas con procedencia TLS explícita.
- Ruta primaria de Nota 3672/09: Mesa CGN + sistema legado de seguimiento de pases.
- COMDOC fechado como ruta 2010 y no exclusivo para una nota 2009.
- Common Crawl V171: 4 negativos válidos acotados, 36 errores, 0 capturas.
- Catorce nombres exactos buscados sin recuperar cuerpos.

## Prioridad V172

1. Buscar índice/libro de Mesa CGN y nombre del sistema legado 2008-2010; reconstruir migración a COMDOC/GDE.
2. Localizar salida SIGEN 3672/09 y correlacionar número receptor CGN e IDs SISIO.
3. Recuperar registro de aprobación Plan 2009 y comunicación a UAI.
4. Reanudar Common Crawl sólo tras un control válido; luego 2016 restante y 2017-2020.
5. Mantener seis borradores DRAFT_NOT_SENT, solicitudes 0, SAF355 0/5 y ejecución 0/10.
""", encoding="utf-8")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V170.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint": "V171", "date": "2026-08-31", "master_catalog_entries": 599,
    "physical_local_copies": 599, "physical_local_hash_ok": 599, "remaining_catalog_physical_or_hash_gaps": 0,
    "state": "SOURCE_ARCHIVE_COMPLETE_CGN_PRIMARY_REGISTRY_ROUTE_LOCATED_TARGET_RECORDS_OPEN",
    "analytical_promotion": "NONE_V171_ARCHIVAL_ROUTE_ONLY", "exact_entities": 34,
    "strict_asset_numerator_million_ars": NUMERATOR, "system_assets_million_ars": SYSTEM_ASSETS,
    "strict_coverage_pct": COVERAGE, "strict_coverage_increment_v170_pp": "0",
    "request_drafts_status": "DRAFT_NOT_SENT", "requests_submitted": 0, "responses_received": 0,
    "saf355_certifications_located": 0, "executed_historical_bank_rows_confirmed": 0,
    "plan_sigen_2009_body_located": False, "plan_sigen_2009_approval_act_located": False,
    "plan_sigen_2009_exact_filenames_searched_v171": 14, "plan_sigen_2009_bodies_located_v171": 0,
    "note_3672_09_body_located": False, "note_3672_contextual_recipient": "CGN",
    "note_3672_formal_addressee_located": False, "note_3672_recipient_identifier_located": False,
    "note_3672_primary_recipient_registry_route_located": True,
    "note_3672_internal_pass_registry_duty_located": True, "comdoc_exclusive_for_2009_rejected": True,
    "commoncrawl_catalog_collections_2013_2020": 74,
    "commoncrawl_exact_prefix_queries_completed": 44, "commoncrawl_exact_prefix_queries_v171": 40,
    "commoncrawl_exact_prefix_service_errors": 40, "commoncrawl_service_errors_v171": 36,
    "commoncrawl_evaluable_query_responses_v171": 4, "commoncrawl_valid_no_capture_v171": 4,
    "commoncrawl_capture_rows_v171": 0, "commoncrawl_2016_remaining_queries_deferred": 14,
    "new_v171_sources": 2, "historical_server_tls_certificate_expired_disclosed": True,
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V171.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

origin_rows = read_csv(ORIGINS)
origin_by_path = {row["path"]: row for row in origin_rows}
for path in iter_files(HIST_ROOT):
    rel = path.relative_to(CYCLE).as_posix()
    if path in (DISP, CIRC):
        origin = "downloaded/preserved V171"
        note = "official CGN HTML; expired TLS certificate disclosed"
    else:
        origin = "generated/preserved V171"
        note = "Common Crawl query method or raw diagnostic log"
    origin_by_path[rel] = {"path": rel, "origin": origin, "note": note}
for path in iter_files(SYNC):
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path": rel, "origin": "generated/updated V171", "note": "incremental source synchronization"}
for path in sorted(HERE.iterdir(), key=lambda item: item.name.casefold()):
    if path.is_file():
        rel = path.relative_to(CYCLE).as_posix()
        origin_by_path[rel] = {"path": rel, "origin": "generated/updated V171", "note": "CGN registry-route checkpoint"}
for path in (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V171.csv", AUDIT / "SOURCE_BACKUP_CENSUS_V171.csv", AUDIT / "SOURCE_PRESERVATION_MISSING_V171.csv", AUDIT / "CURRENT_SOURCE_COMPLETENESS_V171.json"):
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path": rel, "origin": "generated/updated V171", "note": "599-source completeness"}
write_csv(ORIGINS, list(origin_by_path.values()), ["path", "origin", "note"])

transparency = CYCLE / "TRANSPARENCY_README.md"
body = transparency.read_text(encoding="utf-8-sig")
if "## V171 · Ruta registral CGN y corte COMDOC" not in body:
    body += """

## V171 · Ruta registral CGN y corte COMDOC

La Disposición CGN 41/1996 obliga a ingresar documentación por Mesa y registrar los pases internos; la Circular CGN 04/2010 fecha COMDOC III y confirma continuidad de actuaciones por Nota. Para la Nota 3672/09, CGN pasa de receptor contextual a productor registral primario testable, sin que aparezcan aún asiento, cuerpo o IDs SISIO. Common Crawl: 40 consultas nuevas, 4 negativos acotados, 36 errores y 0 capturas; los catorce títulos exactos no devolvieron cuerpos. Las copias históricas oficiales se preservaron declarando certificado TLS vencido. Archivo 599/599; panel 34 sin cambio.
"""
    transparency.write_text(body, encoding="utf-8")

(REPO / "BACKUP_ACTUALIZACION_2026-08-31.md").write_text(f"""# Backup de actualización · 2026-08-31

- Checkpoint: V171.
- Fuentes: 599/599; +2 normas CGN y 4 derivados preservados.
- Plan 2009: 14 nombres exactos buscados; cuerpos y acto abiertos.
- Nota 3672/09: Mesa CGN y registro de pases localizados como ruta; asiento/cuerpo/IDs abiertos.
- Common Crawl V171: 4 negativos acotados, 36 errores, 0 capturas.
- Panel: 34; {COVERAGE}% de activos; promociones 0.
- Solicitudes: 0 enviadas; seis DRAFT_NOT_SENT.
""", encoding="utf-8")

(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")

files = [{"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)} for path in sorted(HERE.iterdir(), key=lambda item: item.name.casefold()) if path.is_file() and path.name != "MANIFEST_V171.json"]
manifest = {
    "checkpoint": "V171", "parent_checkpoint": "V170",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "exact_entities": 34, "strict_coverage_pct": COVERAGE,
    "strict_asset_numerator_million_ars": NUMERATOR, "system_assets_million_ars": SYSTEM_ASSETS,
    "new_promotions": [], "historical_finding": "CGN mandatory incoming registry and pass-log route located; COMDOC nonexclusive for 2009",
    "source_archive": "599/599 catalogued physical SHA-valid; two V171 sources added",
    "commoncrawl_queries_v171": 40, "commoncrawl_valid_negatives_v171": 4,
    "commoncrawl_service_errors_v171": 36, "commoncrawl_captures_v171": 0,
    "plan_sigen_2009_page": "LOCATED", "plan_sigen_2009_body": "NOT_LOCATED",
    "approval_act": "NOT_LOCATED", "note_3672_09_body": "NOT_LOCATED",
    "note_3672_contextual_recipient": "CGN", "note_3672_primary_registry_route": "LOCATED",
    "note_3672_formal_addressee": "NOT_LOCATED", "note_3672_recipient_identifier": "NOT_LOCATED",
    "comdoc_2009_exclusivity": "REJECTED", "crosswalk_gate": "OPEN", "closed_network_gate": "NO",
    "saf355_certifications": "0/5", "executed_historical_bank_rows": "0/10", "requests_submitted": 0,
    "files": files,
}
(HERE / "MANIFEST_V171.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in iter_files(REPO) if path != global_manifest]
payload = {
    "checkpoint": "V171", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": COVERAGE, "exact_entities": 34, "closed_network_gate": "NO",
    "source_audit": "599 master; 599 physical SHA-valid; two V171 sources added",
    "historical_workstream": "CGN registry route located; Plan bodies, approval act, Note body/entry, SISIO and execution open; six drafts not sent",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
tmp = global_manifest.with_suffix(".json.V171tmp")
tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
tmp.replace(global_manifest)

print("V171 BUILD PASS · catalog=599/599 · new=2 · cc=40 queries/4 valid negatives/36 errors/0 captures · filenames=14/14 · CGN_REGISTRY_ROUTE=LOCATED · panel=34 · requests=0")
