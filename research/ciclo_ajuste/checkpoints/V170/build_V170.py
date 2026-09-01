from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import os
import re


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
PARENT = CYCLE / "checkpoints" / "V169"
AUDIT = CYCLE / "source_audit"
SYNC = CYCLE / "inputs" / "source_sync" / "v170"
HIST_ROOT = CYCLE / "inputs" / "historical_retrieval" / "v170"
HIST = HIST_ROOT / "binaries"
QUERY_LOGS = HIST_ROOT / "query_logs"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"

CC_CATALOG = HIST / "commoncrawl_collection_catalog_2026_08_31.json"
CC_BROAD_RAW = QUERY_LOGS / "commoncrawl_broad_query_raw_superseded.csv"
CC_EXACT_RAW = QUERY_LOGS / "commoncrawl_exact_prefix_query_raw_2013.csv"
CC_SCANNER = QUERY_LOGS / "commoncrawl_exact_prefix_scanner.ps1"
EXPECTED = {
    CC_CATALOG: (34947, "c82b50cd071b1491081c794b63f4399782a9dd909c0f24510951c98552dcb3a7"),
    CC_BROAD_RAW: (14632, "2cc4d2a39968b245f8d12f66cfff0878a3882164b7dc6d99bec79ce3512d8985"),
    CC_EXACT_RAW: (1283, "b8a2cb7dcb2a92853a0f120f1a406719c0129ee312419fb9516c1a95cbf8f8ac"),
    CC_SCANNER: (2179, "742c69f737fd8c895f17d1306ab3e0f443cbd3bd9182aa2bdb73cc1d5010ed0a"),
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
        "MANIFEST_V169.json", "README_V169.md", "VEREDICTO_V169.md", "AUDITORIA_V169.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V169_A_V170.md", "V169_SOURCE_BUNDLE.csv",
        "V169_PUBLIC_SEARCH_LOG.csv", "E0_PLAN_2009_ARCHIVE_RECOVERY_NOTE_V169.md",
        "E0_SIGEN_ARCHIVAL_INDEX_RECOVERY_NOTE_V169.md", "E0_FISCAL_RECONSTRUCTION_V169.md",
        "CNV_ATTACHMENT_ANALYTIC_REVIEW_V169.md",
    }
    for source in sorted(PARENT.iterdir(), key=lambda path: path.name.casefold()):
        if not source.is_file() or source.name in skip_names or source.name.startswith(skip_prefixes):
            continue
        target = HERE / source.name.replace("V169", "V170")
        target.write_text(source.read_text(encoding="utf-8-sig").replace("V169", "V170"), encoding="utf-8")


clone_parent()

for path, (size, digest) in EXPECTED.items():
    assert path.is_file() and path.stat().st_size == size and sha256(path) == digest

collections = json.loads(CC_CATALOG.read_text(encoding="utf-8"))
assert isinstance(collections, list) and len(collections) > 100
collection_ids = [row["id"] for row in collections]
assert len(collection_ids) == len(set(collection_ids))
target_collections = [row for row in collections if re.match(r"^CC-MAIN-(2013|2014|2015|2016|2017|2018|2019|2020)-", row["id"])]
assert len(target_collections) == 74

broad_rows = read_csv(CC_BROAD_RAW)
exact_rows = read_csv(CC_EXACT_RAW)
assert len(broad_rows) == 20 and len(exact_rows) == 4
assert sum(row["classification"] == "CAPTURE_ROWS" for row in broad_rows) == 8
assert sum(row["classification"] == "SERVICE_ERROR" for row in broad_rows) == 12
html_false = [row for row in broad_rows if row["classification"] == "CAPTURE_ROWS" and "503 Service Temporarily Unavailable" in row["response"]]
domain_false = [row for row in broad_rows if row["classification"] == "CAPTURE_ROWS" and row not in html_false]
assert len(html_false) == 6 and len(domain_false) == 2
assert all("/documentacion/plananualpdfs/" not in row["response"].lower() for row in domain_false)
assert all(row["classification"] == "SERVICE_ERROR" for row in exact_rows)
assert {row["target"] for row in exact_rows} == {
    "www.sigen.gov.ar/documentacion/plananualpdfs/",
    "sigen.gov.ar/documentacion/plananualpdfs/",
}
assert all("matchType=prefix" in row["query_url"] for row in exact_rows)

catalog = read_csv(CATALOG)
catalog_fields = list(catalog[0])
new_source = {
    "id": "commoncrawl_collection_catalog_2026_08_31_v170",
    "tema": "ciclo_ajuste_historico",
    "institucion": "Common Crawl",
    "titulo": "Catálogo oficial de índices Common Crawl preservado el 31-08-2026",
    "url_original": "https://index.commoncrawl.org/collinfo.json",
    "archivo_local": "/" + CC_CATALOG.relative_to(REPO).as_posix(),
    "fecha_descarga": "2026-08-31",
    "fecha_publicacion": "2013-2026",
    "codigo_serie": "COMMONCRAWL-COLLINFO",
    "periodo_utilizado": "2013-2020",
    "tipo": "JSON oficial · catálogo de colecciones",
    "sha256": EXPECTED[CC_CATALOG][1],
    "nota": "V170: autentica 74 colecciones 2013-2020 disponibles para consulta. No contiene capturas target ni convierte errores del índice en negativos.",
}
catalog_by_id = {row["id"]: row for row in catalog}
catalog_by_id[new_source["id"]] = new_source
catalog = list(catalog_by_id.values())
write_csv(CATALOG, catalog, catalog_fields)
assert len(catalog) == 597 and len(catalog_by_id) == 597

audit_rows = []
for row in catalog:
    local = REPO / row["archivo_local"].lstrip("/")
    actual = sha256(local) if local.is_file() else ""
    audit_rows.append({
        "id": row["id"], "archivo_local": row["archivo_local"], "exists": str(local.is_file()),
        "sha_catalog": row["sha256"].lower(), "sha_actual": actual,
        "hash_ok": str(local.is_file() and bool(row["sha256"]) and actual == row["sha256"].lower()),
    })
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V170.csv", audit_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V170.csv", audit_rows)
missing = [row for row in audit_rows if row["exists"] != "True" or row["hash_ok"] != "True"]
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V170.csv", missing, list(audit_rows[0]))
assert not missing

semantics = [
    {"audit_id": "CC170_01", "observed_query": "*.sigen.gov.ar/documentacion/plananualpdfs/*", "observed_response": "12 transport timeouts; 6 HTML 503 bodies; 2 general-domain capture lists", "original_label": "8 CAPTURE_ROWS / 12 SERVICE_ERROR", "corrected_classification": "BROAD_QUERY_INVALID_FOR_FOLDER_CENSUS", "reason": "La semántica aplicada no restringió la ruta y curl exit 0 no validó el tipo de respuesta.", "rule": "No usar el lote para afirmar captura o ausencia del directorio."},
    {"audit_id": "CC170_02", "observed_query": "broad query · six collections", "observed_response": "HTML 503 Service Temporarily Unavailable", "original_label": "CAPTURE_ROWS", "corrected_classification": "SERVICE_ERROR_FALSE_POSITIVE", "reason": "Una página de error HTML no es una fila CDX JSON.", "rule": "Validar HTTP/cuerpo y parsear cada línea JSON antes de contar."},
    {"audit_id": "CC170_03", "observed_query": "broad query · CC-MAIN-2015-32 and 2015-40", "observed_response": "páginas generales de sigen.gov.ar", "original_label": "CAPTURE_ROWS", "corrected_classification": "DOMAIN_CAPTURE_NOT_FOLDER_CAPTURE", "reason": "Las URLs devueltas no pertenecen a /documentacion/plananualpdfs/.", "rule": "Validar prefijo de cada URL devuelta."},
    {"audit_id": "CC170_04", "observed_query": "www host exact folder + matchType=prefix", "observed_response": "2 timeouts en colecciones 2013", "original_label": "SERVICE_ERROR", "corrected_classification": "SERVICE_ERROR_NOT_NEGATIVE", "reason": "No hubo respuesta de índice evaluable.", "rule": "Reintentar; no sumar ausencia."},
    {"audit_id": "CC170_05", "observed_query": "no-www host exact folder + matchType=prefix", "observed_response": "2 timeouts en colecciones 2013", "original_label": "SERVICE_ERROR", "corrected_classification": "SERVICE_ERROR_NOT_NEGATIVE", "reason": "La variante de host es necesaria pero tampoco respondió.", "rule": "Mantener ambas variantes en el protocolo."},
    {"audit_id": "CC170_06", "observed_query": "V169 LA169_03", "observed_response": "No Captures found en cuatro colecciones", "original_label": "FOUR_COLLECTION_NEGATIVE_SCOPED", "corrected_classification": "SUPERSEDED_INVALID_QUERY_NEGATIVE", "reason": "La prueba posterior mostró que el patrón ancho no era un censo fiable de la ruta.", "rule": "Retirar ese negativo del balance probatorio sin reescribir V169."},
    {"audit_id": "CC170_07", "observed_query": "catálogo oficial collinfo.json", "observed_response": "74 colecciones 2013-2020", "original_label": "N/A", "corrected_classification": "COLLECTION_UNIVERSE_VERIFIED_QUERY_RESULTS_PENDING", "reason": "El catálogo prueba disponibilidad nominal de índices, no resultado target.", "rule": "Separar universo de colecciones de consultas completadas."},
]
write_csv(HERE / "E0_COMMONCRAWL_QUERY_SEMANTICS_AND_FALSE_POSITIVE_AUDIT_V170.csv", semantics)

coverage_rows = []
errored = {row["collection"] for row in exact_rows}
for item in target_collections:
    coverage_rows.append({
        "collection_id": item["id"], "collection_name": item.get("name", ""),
        "year": item["id"][8:12], "catalog_endpoint": item.get("timegate", ""),
        "exact_prefix_status": "SERVICE_ERROR_2_HOSTS" if item["id"] in errored else "PENDING_SERVICE_RECOVERY",
        "target_prefixes": "www.sigen.gov.ar/documentacion/plananualpdfs/ | sigen.gov.ar/documentacion/plananualpdfs/",
        "evidentiary_effect": "NONE_NOT_NEGATIVE",
    })
write_csv(HERE / "E0_COMMONCRAWL_COLLECTION_COVERAGE_V170.csv", coverage_rows)

filename_search = [
    {"search_id": "FN170_01", "exact_query": '"Plan SIGEN 2009.pdf"', "target": "Plan SIGEN 2009.pdf", "surface": "public web exact-title search", "result": "no target body returned", "classification": "SEARCH_ENGINE_NEGATIVE_SCOPED", "limit": "No prueba inexistencia ni ausencia en custodia."},
    {"search_id": "FN170_02", "exact_query": '"Anexo G - Capacitacion 2009.pdf"', "target": "Anexo G - Capacitacion 2009.pdf", "surface": "public web exact-title search", "result": "no target body returned", "classification": "SEARCH_ENGINE_NEGATIVE_SCOPED", "limit": "No prueba inexistencia ni ausencia en custodia."},
    {"search_id": "FN170_03", "exact_query": '"planred2009.pdf" SIGEN', "target": "planred2009.pdf", "surface": "public web exact-title search", "result": "no target body returned", "classification": "SEARCH_ENGINE_NEGATIVE_SCOPED", "limit": "No prueba inexistencia ni ausencia en custodia."},
    {"search_id": "FN170_04", "exact_query": '"Anexo F - Cuadro 18" "SIGEN" 2009', "target": "Anexo F - Cuadro 18.pdf", "surface": "public web exact-title search", "result": "no target body returned", "classification": "SEARCH_ENGINE_NEGATIVE_SCOPED", "limit": "Los otros diez cuadros permanecen en el inventario de 14 enlaces, no como cuerpos recuperados."},
]
write_csv(HERE / "E0_PLAN_2009_EXACT_FILENAME_PUBLIC_SEARCH_V170.csv", filename_search)

pronoun_chain = [
    {"step_id": "PR170_01", "text_marker": "CGN elevó Nota 0120/09 DAIF a SIGEN", "actor_or_antecedent": "Contaduría General de la Nación", "inference": "CGN inicia el intercambio institucional narrado.", "confidence": "DIRECT_STATEMENT", "open_limit": "No identifica mesa ni expediente."},
    {"step_id": "PR170_02", "text_marker": "Al respecto", "actor_or_antecedent": "enlace con la respuesta al informe CGN", "inference": "La Nota SIGEN 3672/09 responde al antecedente inmediato.", "confidence": "STRONG_CONTEXTUAL_LINK", "open_limit": "No sustituye el cuerpo de la respuesta."},
    {"step_id": "PR170_03", "text_marker": "Nota SIGEN 3672/09 GSEyP", "actor_or_antecedent": "SIGEN / Síndico General", "inference": "Se identifica emisor, firmante y número de salida.", "confidence": "DIRECT_STATEMENT", "open_limit": "Fecha completa, adjuntos y distribución abiertos."},
    {"step_id": "PR170_04", "text_marker": "esta repartición fue notificada", "actor_or_antecedent": "CGN, narradora y antecedente institucional inmediato", "inference": "CGN es la receptora contextual de la notificación.", "confidence": "HIGH_CONTEXTUAL_INFERENCE", "open_limit": "No prueba destinatario nominal ni número de entrada."},
    {"step_id": "PR170_05", "text_marker": "áreas pertinentes + SISIO + UAI", "actor_or_antecedent": "SIGEN y UAI competentes", "inference": "La respuesta ordena circulación y seguimiento, no acredita ejecución ni cierre.", "confidence": "DIRECT_STATEMENT_WITH_LIMIT", "open_limit": "IDs SISIO, responsables, fechas y regularizaciones abiertos."},
]
write_csv(HERE / "E0_NOTE_3672_RECIPIENT_PRONOUN_CHAIN_V170.csv", pronoun_chain)

late_scan = read_csv(HERE / "E0_PLAN_2009_LATE_ARCHIVE_COLLECTION_SCAN_V170.csv")
for row in late_scan:
    if row["scan_id"] == "LA169_03":
        row.update({
            "result": "superseded in V170: wildcard/domain query did not reliably constrain the folder",
            "classification": "SUPERSEDED_INVALID_QUERY_NEGATIVE", "service_state": "INVALIDATED",
            "next_step": "exact host prefix + matchType=prefix + JSON/URL validation",
        })
late_scan.extend([
    {"scan_id": "LA170_07", "surface": "Common Crawl official catalog", "period_or_collection": "2013-2020 · 74 collections", "target": "queryable collection universe", "result": "74 collection identifiers authenticated", "classification": "COLLECTION_UNIVERSE_VERIFIED_RESULTS_PENDING", "service_state": "CATALOG_OK", "next_step": "resume exact-prefix batches"},
    {"scan_id": "LA170_08", "surface": "Common Crawl broad query audit", "period_or_collection": "2013-2015 · 20 collections", "target": "wildcard domain/path pattern", "result": "12 service errors; 6 HTML-503 false positives; 2 general-domain result sets", "classification": "BROAD_BATCH_INVALIDATED", "service_state": "MIXED_INVALID", "next_step": "do not use as capture or negative evidence"},
    {"scan_id": "LA170_09", "surface": "Common Crawl exact-prefix retry", "period_or_collection": "2013 · 2 collections × 2 hosts", "target": "exact folder prefix with matchType=prefix", "result": "4 service errors; zero evaluable responses", "classification": "SERVICE_ERRORS_NOT_NEGATIVES", "service_state": "ERROR", "next_step": "retry with backoff when service recovers"},
    {"scan_id": "LA170_10", "surface": "public exact-title search", "period_or_collection": "2026-08-31", "target": "four exact Plan 2009 filename/title probes", "result": "no target body returned", "classification": "SEARCH_ENGINE_NEGATIVE_SCOPED", "service_state": "OK", "next_step": "institutional custody by 14 exact routes"},
    {"scan_id": "LA170_11", "surface": "SIGEN/Normativa/Boletín Oficial search", "period_or_collection": "approval date 2008-12-15", "target": "Plan SIGEN 2009 approval act", "result": "no act number or body located; Memory 2008 remains exact approval reference", "classification": "PUBLIC_ACT_SEARCH_NEGATIVE_SCOPED", "service_state": "OK", "next_step": "approval register, file and UAI communication"},
    {"scan_id": "LA170_12", "surface": "CGN Cuenta 2009 UEPEX", "period_or_collection": "2009", "target": "recipient of Nota SIGEN 3672/09", "result": "CGN identified as contextual recipient by narrative antecedent", "classification": "RECIPIENT_IDENTIFIED_BY_CONTEXT_CGN", "service_state": "OK", "next_step": "formal addressee and CGN incoming identifier"},
])
write_csv(HERE / "E0_PLAN_2009_LATE_ARCHIVE_COLLECTION_SCAN_V170.csv", late_scan)
public_log = [{
    "log_id": row["scan_id"], "surface": row["surface"], "query_or_target": row["target"],
    "result": row["result"], "classification": row["classification"],
    "limit_or_next_step": row["next_step"],
} for row in late_scan]
public_log.extend({
    "log_id": row["search_id"], "surface": row["surface"], "query_or_target": row["exact_query"],
    "result": row["result"], "classification": row["classification"],
    "limit_or_next_step": row["limit"],
} for row in filename_search)
write_csv(HERE / "V170_PUBLIC_SEARCH_LOG.csv", public_log)

approval = read_csv(HERE / "E0_PLAN_2009_APPROVAL_ACT_SEARCH_V170.csv")
approval.extend([
    {"test_id": "AA170_06", "question": "¿Las búsquedas exactas en SIGEN, Normativa y Boletín Oficial revelan el acto?", "evidence": "consultas públicas exactas del 31/08/2026", "result": "No apareció número ni cuerpo del acto", "classification": "PUBLIC_SEARCH_NEGATIVE_SCOPED", "remaining_gap": "registro de aprobación; expediente; firma; comunicación"},
    {"test_id": "AA170_07", "question": "¿Qué puede afirmarse después del nuevo barrido?", "evidence": "Memoria SIGEN 2008 + búsquedas oficiales", "result": "Aprobación 15/12/2008 confirmada; clase y número aún abiertos", "classification": "EXISTENCE_DATE_CONFIRMED_ACT_OPEN", "remaining_gap": "acto original o certificación de custodia"},
])
write_csv(HERE / "E0_PLAN_2009_APPROVAL_ACT_SEARCH_V170.csv", approval)

note_route = read_csv(HERE / "E0_NOTE_3672_ARCHIVAL_SEARCH_V170.csv")
note_route.extend([
    {"route_id": "N170_08", "surface": "CGN Cuenta 2009 UEPEX · cadena narrativa", "target": "receptor institucional de Nota SIGEN 3672/09", "result": "CGN es el referente de 'esta repartición' en el intercambio Nota 0120/09 → Nota 3672/09", "status": "RECIPIENT_IDENTIFIED_BY_CONTEXT_CGN", "required_record": "cuerpo para confirmar destinatario formal"},
    {"route_id": "N170_09", "surface": "CGN Mesa/registro de entradas 2009", "target": "Nota SIGEN 3672/09 GSEyP", "result": "número de entrada, fecha y pases no localizados", "status": "FORMAL_ADDRESSEE_AND_INCOMING_ID_OPEN", "required_record": "asiento; fecha; destinatario; remitente; asunto; pases; contenedor; adjuntos"},
    {"route_id": "N170_10", "surface": "Ministerio de Economía COMDOC 2009", "target": "ruta subsidiaria de Nota SIGEN 3672/09", "result": "mantener sólo si CGN no conserva registro propio o hubo pase ministerial", "status": "SECONDARY_ROUTING_HYPOTHESIS", "required_record": "registro por número SIGEN, fecha, remitente y asunto"},
])
write_csv(HERE / "E0_NOTE_3672_ARCHIVAL_SEARCH_V170.csv", note_route)

search_keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V170.csv")
search_keys.extend([
    {"key_id": "SK170_01", "request_id": "REQ133_ECON", "key_group": "primary_recipient_registry", "exact_key": "CGN Mesa/registro de entradas 2009 · Nota SIGEN 3672/09 GSEyP", "search_purpose": "recuperar asiento receptor contextual", "source_or_basis": "Cuenta de Inversión 2009 UEPEX · 'esta repartición'", "caveat": "CGN contextual; confirmar destinatario formal."},
    {"key_id": "SK170_02", "request_id": "REQ155_SIGEN", "key_group": "sender_outgoing_registry", "exact_key": "salida SIGEN 3672/09 GSEyP · respuesta a Nota 0120/09 DAIF", "search_purpose": "vincular salida con ingreso CGN", "source_or_basis": "Cuenta 2009 + comparadores ENARGAS", "caveat": "No asumir número receptor."},
    {"key_id": "SK170_03", "request_id": "REQ133_ECON", "key_group": "secondary_registry", "exact_key": "COMDOC Economía 2009 · 3672/09 · SIGEN · 0120/09 DAIF", "search_purpose": "ruta subsidiaria por pase o registro central", "source_or_basis": "estructura documental contemporánea", "caveat": "No sustituye búsqueda primaria CGN."},
    {"key_id": "SK170_04", "request_id": "REQ155_SIGEN", "key_group": "followup_system", "exact_key": "SISIO hallazgos derivados de Nota 0120/09 DAIF y Nota SIGEN 3672/09", "search_purpose": "recuperar ids, altas, responsables y regularizaciones", "source_or_basis": "Cuenta de Inversión 2009 UEPEX", "caveat": "Seguimiento no equivale a ejecución bancaria."},
])
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V170.csv", search_keys)

request_objects = read_csv(HERE / "E0_V170_REQUEST_OBJECTS.csv")
request_objects.extend([
    {"row_id": "RO170_01", "object_id": "CGN_INCOMING_3672", "custodian": "CGN · Mesa/archivo/DAIF", "exact_record": "asiento de ingreso de Nota SIGEN 3672/09 GSEyP, respuesta a Nota 0120/09 DAIF", "period": "2009", "minimum_fields": "número de entrada; fecha; destinatario; remitente; asunto; pases; contenedor; adjuntos", "closure_rule": "Copia o negativa fundada por sistema, período y campos consultados.", "status": "DRAFT_NOT_SENT"},
    {"row_id": "RO170_02", "object_id": "SIGEN_OUTGOING_3672", "custodian": "SIGEN · salida/GSEyP/archivo", "exact_record": "Nota SIGEN 3672/09 GSEyP y asiento de salida", "period": "2009", "minimum_fields": "fecha; firmante; destinatario formal; asunto; distribución; anexos; acuses; vínculo con Nota 0120/09", "closure_rule": "Cuerpo y metadatos o negativa fundada por repositorio y serie.", "status": "DRAFT_NOT_SENT"},
    {"row_id": "RO170_03", "object_id": "SISIO_0120_3672_CHAIN", "custodian": "SIGEN / UAI Economía / CGN", "exact_record": "entradas SISIO vinculadas a hallazgos de Notas 0120/09 DAIF y 3672/09 GSEyP", "period": "2009 en adelante", "minimum_fields": "id; hallazgo; alta; responsable; unidad; estado; cambios; evidencia; regularización; cierre", "closure_rule": "Exportación íntegra e historial; no aceptar resumen sin identificadores.", "status": "DRAFT_NOT_SENT"},
])
write_csv(HERE / "E0_V170_REQUEST_OBJECTS.csv", request_objects)
write_csv(HERE / "E0_V170_REQUEST_OBJECTS_V170.csv", request_objects)

method_breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V170.csv")
method_breaks.extend([
    {"break_id": "commoncrawl_wildcard_domain_not_exact_prefix", "dimension": "archive_query", "problem": "El patrón ancho devolvió páginas generales del dominio y no un censo de la carpeta.", "rule": "Usar host exacto + matchType=prefix y validar cada URL devuelta.", "status": "FROZEN_V170", "evidence": "V170 broad raw audit"},
    {"break_id": "curl_exit_zero_html_error_not_capture", "dimension": "transport", "problem": "Seis respuestas HTML 503 llegaron con salida técnica 0 y fueron etiquetadas como capturas.", "rule": "Validar estado, content-type, cuerpo y JSON antes de contar resultados.", "status": "FROZEN_V170", "evidence": "V170 false-positive audit"},
    {"break_id": "commoncrawl_service_error_not_negative_v170", "dimension": "archive", "problem": "Las cuatro consultas exact-prefix de 2013 terminaron en timeout.", "rule": "Registrar error y pendiente; nunca ausencia.", "status": "FROZEN_V170", "evidence": "V170 exact-prefix raw log"},
    {"break_id": "contextual_recipient_not_formal_addressee", "dimension": "document_routing", "problem": "La cadena narrativa identifica a CGN como receptora contextual.", "rule": "Priorizar su registro de entrada sin afirmar persona destinataria ni número receptor.", "status": "FROZEN_V170", "evidence": "CGN Cuenta 2009 UEPEX"},
    {"break_id": "search_engine_absence_not_custody_absence_v170", "dimension": "public_search", "problem": "Las búsquedas exactas no devolvieron cuerpos ni acto.", "rule": "Mantener pedido de custodia; no convertir silencio del buscador en inexistencia.", "status": "FROZEN_V170", "evidence": "V170 public search log"},
])
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V170.csv", method_breaks)

addendum = """

## Adenda V170 · receptor contextual CGN y protocolo de búsqueda

La Cuenta de Inversión 2009 está redactada por la Contaduría General de la Nación: informa que la CGN remitió la Nota Nº 0120/09 DAIF a SIGEN y, al describir la respuesta mediante Nota SIGEN Nº 3672/09 GSEyP, dice que «esta repartición» fue notificada. Por antecedente institucional inmediato, la CGN queda identificada como receptora contextual. Esto no prueba el destinatario nominal ni su número de entrada. La búsqueda primaria debe realizarse en Mesa/registro de entradas, archivo y DAIF de la CGN; la búsqueda COMDOC del Ministerio de Economía es subsidiaria para pases o registro central. En paralelo debe pedirse a SIGEN el asiento de salida y el cuerpo, y a SIGEN/UAI el historial SISIO correlacionado. Campos mínimos: números emisor y receptor, fecha, remitente, destinatario, asunto, pases, contenedor, adjuntos, acuses e identificadores SISIO. Estado DRAFT_NOT_SENT; solicitudes enviadas 0.
"""
for name in ("REQUEST_ECONOMIA_TESORO_SETTLEMENT_V170.md", "REQUEST_SUBMISSION_CHECKLIST_V170.md"):
    path = HERE / name
    text = path.read_text(encoding="utf-8-sig")
    if "Adenda V170 · receptor contextual CGN" not in text:
        path.write_text(text + addendum, encoding="utf-8")

write_csv(HERE / "CURRENT_STATE_V170.csv", read_csv(PARENT / "CURRENT_STATE_V169.csv"))
write_csv(HERE / "FOUR_LEG_PASS_PANEL_V170.csv", read_csv(PARENT / "FOUR_LEG_PASS_PANEL_V169.csv"))
strict_rows = read_csv(PARENT / "STRICT_Q4_FOUR_LEG_COVERAGE_V169.csv")
strict_rows[0]["coverage_set"] = "V170 strict 34-entity set; unchanged from V169"
strict_rows[0]["v161_change"] = "V170: no banking promotion; numerator and coverage unchanged from V169."
write_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V170.csv", strict_rows)

recovery_note = f"""# Recuperación archivística y receptor documental · V170

V170 corrige una sobrelectura del barrido Common Crawl. El patrón ancho usado previamente no garantizaba restricción a la carpeta: doce consultas fallaron por transporte, seis devolvieron HTML 503 que una clasificación inicial contó como filas y dos devolvieron capturas generales de SIGEN ajenas a `plananualpdfs`. El supuesto negativo de cuatro colecciones V169 queda expresamente superado. El protocolo válido exige host exacto, `matchType=prefix`, parseo JSON y validación del prefijo de cada URL.

El catálogo oficial preservado autentica 74 colecciones 2013-2020. El reintento exacto en las dos colecciones 2013 y dos variantes de host produjo cuatro errores de servicio: cero respuestas evaluables, por lo tanto cero negativos nuevos. Las búsquedas públicas por cuatro títulos exactos tampoco devolvieron cuerpos; eso es un negativo de buscador, no de existencia o custodia. La aprobación del 15/12/2008 continúa confirmada por la Memoria SIGEN, sin acto, número ni expediente recuperados.

La Cuenta de Inversión 2009 permite acotar el receptor de la Nota SIGEN 3672/09: la CGN es la narradora, remitió la Nota 0120/09 y luego afirma que «esta repartición» fue notificada. Se clasifica como receptor contextual CGN, con alta confianza contextual. Permanecen abiertos el destinatario formal, el número de entrada, cuerpo, adjuntos, acuses e IDs SISIO. La ruta primaria es CGN; COMDOC/Economía queda subsidiaria. Archivo 597/597; panel 34 y {COVERAGE}%; seis borradores DRAFT_NOT_SENT, solicitudes 0, SAF355 0/5 y ejecución 0/10.
"""
for name in ("E0_PLAN_2009_ARCHIVE_RECOVERY_NOTE_V170.md", "E0_SIGEN_ARCHIVAL_INDEX_RECOVERY_NOTE_V170.md", "E0_FISCAL_RECONSTRUCTION_V170.md"):
    (HERE / name).write_text(recovery_note, encoding="utf-8")
(HERE / "CNV_ATTACHMENT_ANALYTIC_REVIEW_V170.md").write_text(f"""# Revisión analítica acumulada V170

Panel congelado: 34 entidades y {COVERAGE}% de activos. V170 agrega una fuente oficial de metadatos, invalida un falso negativo Common Crawl y fija el protocolo exact-prefix. También acota a CGN como receptora contextual de Nota 3672/09, sin afirmar destinatario formal ni identificador de ingreso. No recupera cuerpos, acto, IDs SISIO ni ejecución. Seis pedidos DRAFT_NOT_SENT; SAF355 0/5 y ejecución 0/10.
""", encoding="utf-8")

bundle_specs = [
    ("COMMONCRAWL_OFFICIAL_COLLECTION_CATALOG", CC_CATALOG, new_source["url_original"], "collection universe and endpoints"),
    ("COMMONCRAWL_BROAD_QUERY_RAW_SUPERSEDED", CC_BROAD_RAW, "generated retrieval log", "false-positive audit"),
    ("COMMONCRAWL_EXACT_PREFIX_RAW_2013", CC_EXACT_RAW, "generated retrieval log", "service-error evidence"),
    ("COMMONCRAWL_EXACT_PREFIX_SCANNER", CC_SCANNER, "generated retrieval method", "reproducible query protocol"),
]
bundle = []
for role, path, url, use in bundle_specs:
    bundle.append({"role": role, "path": "/" + path.relative_to(REPO).as_posix(), "url": url, "bytes": str(path.stat().st_size), "sha256": sha256(path), "analytic_use": use})
write_csv(HERE / "V170_SOURCE_BUNDLE.csv", bundle)

SYNC.mkdir(parents=True, exist_ok=True)
sync_rows = [{
    "role": "V170_PUBLIC_SOURCE", "relative_path": new_source["archivo_local"],
    "source_url": new_source["url_original"], "size_bytes": str(CC_CATALOG.stat().st_size),
    "sha256": sha256(CC_CATALOG), "format_verification": "PARSED_JSON_UNIQUE_COLLECTION_IDS",
}]
write_csv(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V170.csv", sync_rows)
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V170.csv", late_scan)
(SYNC / "SOURCE_SYNC_REPORT_V170.md").write_text("""# Sincronización incremental de fuentes · V170

- Catálogo: 597/597 copias locales y SHA-256 válido; brecha 0.
- Nueva fuente: catálogo oficial Common Crawl; 74 colecciones 2013-2020 autenticadas.
- Logs/método: lote ancho invalidado, consulta exact-prefix y scanner preservados como derivados, no como fuentes target.
- Cuerpos Plan 2009, acto, Nota 3672/09, identificador de entrada e IDs SISIO siguen abiertos.
""", encoding="utf-8")
(SYNC / "qa_source_sync_v170.py").write_text("""from pathlib import Path
import csv, hashlib, json
root = Path(__file__).resolve().parents[5]
rows = list(csv.DictReader(Path(__file__).with_name('SOURCE_SYNC_FILE_MANIFEST_V170.csv').open(encoding='utf-8-sig', newline='')))
assert len(rows) == 1
for row in rows:
    path = root / row['relative_path'].lstrip('/')
    assert path.is_file() and path.stat().st_size == int(row['size_bytes'])
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
    payload = json.loads(path.read_text(encoding='utf-8'))
    assert isinstance(payload, list) and len(payload) > 100
print('SOURCE SYNC V170 PASS · 1/1')
""", encoding="utf-8")

local_census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V170.csv")
local_census.append({
    "source_id": new_source["id"], "institution": new_source["institucion"], "artifact": new_source["titulo"],
    "url": new_source["url_original"], "local_path": new_source["archivo_local"], "sha256": new_source["sha256"],
    "bytes": str(CC_CATALOG.stat().st_size), "period_coverage": new_source["periodo_utilizado"],
    "variable_families": "Plan2009;archive;CommonCrawl;collection_catalog;query_method",
    "primary_source": "YES_SERVICE_METADATA", "preserved": "YES",
    "method_breaks": "catálogo de colecciones no equivale a resultados ni capturas target",
    "use_status": "E0_USABLE_AS_QUERY_UNIVERSE", "caveat": new_source["nota"],
})
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V170.csv", local_census)

archival = read_csv(HERE / "ARCHIVAL_PROVENANCE_V170.csv")
archival.append({
    "source_id": new_source["id"], "original_url": new_source["url_original"],
    "retrieval_url": new_source["url_original"], "capture_timestamp": "2026-08-31",
    "cdx_digest": "N/A_DIRECT_SERVICE_METADATA", "local_path": new_source["archivo_local"],
    "sha256": new_source["sha256"], "bytes": str(CC_CATALOG.stat().st_size),
    "provenance_note": new_source["nota"],
})
write_csv(HERE / "ARCHIVAL_PROVENANCE_V170.csv", archival)

refs = HERE / "SOURCE_REFERENCES_V170.md"
with refs.open("a", encoding="utf-8") as handle:
    handle.write("\n## V170 · universo Common Crawl y corrección metodológica\n")
    handle.write(f"\n- `{new_source['id']}` · {new_source['titulo']} · {new_source['url_original']} · `{new_source['archivo_local']}` · `{new_source['sha256']}`\n")
    handle.write("\n- La Cuenta de Inversión 2009 UEPEX ya preservada en V155 sustenta la inferencia contextual CGN; no se duplica en el catálogo.\n")

(HERE / "README_V170.md").write_text(f"""# Checkpoint V170

- Archivo: 597/597 copias locales con hash válido; +1 fuente oficial y 3 derivados de consulta preservados.
- Common Crawl: 74 colecciones 2013-2020 autenticadas; el lote ancho previo queda invalidado por semántica y falsos positivos.
- Reintento válido: 4 consultas exact-prefix en 2013, 4 errores de servicio, 0 respuestas evaluables y 0 negativos nuevos.
- Plan 2009: 14 enlaces conocidos; 14 cuerpos y acto aprobatorio aún no localizados.
- Nota 3672/09: CGN identificada como receptora contextual; destinatario formal y número de entrada siguen abiertos.
- Panel: 34 entidades; activos {NUMERATOR}/{SYSTEM_ASSETS}; cobertura {COVERAGE}%.
- SAF355 0/5; ejecución 0/10; seis borradores no enviados; solicitudes enviadas 0.
""", encoding="utf-8")
(HERE / "VEREDICTO_V170.md").write_text("""# Veredicto V170

Avance metodológico y archivístico sin cierre indebido. Se retira del balance probatorio un supuesto negativo Common Crawl: el patrón ancho no restringía de manera confiable la carpeta y seis respuestas HTML 503 habían sido mal clasificadas. El catálogo permite definir 74 colecciones 2013-2020, pero el reintento exacto de 2013 sólo produjo errores de servicio. En la Nota 3672/09, la redacción contemporánea permite priorizar a la CGN como receptora contextual; no habilita inventar el destinatario nominal ni el identificador receptor. Sin promoción bancaria ni solicitud enviada.
""", encoding="utf-8")
(HERE / "AUDITORIA_V170.md").write_text(f"""# Auditoría V170

- Catálogo/copia/hash: 597/597; huecos 0; nueva fuente 1.
- Common Crawl: 74 colecciones 2013-2020; lote ancho 20 filas invalidado (12 errores, 6 HTML 503, 2 resultados de dominio ajenos a la carpeta).
- Consulta exact-prefix 2013: 2 colecciones × 2 hosts = 4 errores; 0 respuestas evaluables.
- Búsqueda pública: 4 títulos exactos sin cuerpo; acto aprobatorio no recuperado; negativos estrictamente acotados.
- Nota 3672/09: receptor contextual CGN; destinatario formal, ingreso, cuerpo e IDs SISIO abiertos.
- Panel 34, {COVERAGE}%; promociones 0; solicitudes 0; SAF355 0/5; ejecución 0/10.
""", encoding="utf-8")
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V170_A_V171.md").write_text("""# Handover V170 → V171

## Cerrado

- Catálogo oficial Common Crawl preservado: 74 colecciones 2013-2020.
- Falso negativo V169 invalidado y protocolo exact-prefix fijado.
- Cuatro consultas exactas 2013 clasificadas como error, no negativo.
- CGN priorizada como receptora contextual de Nota 3672/09.
- Archivo 597/597; panel 34 sin cambio.

## Prioridad V171

1. Reintentar Common Crawl exact-prefix con backoff, empezando por 2014-2016 y ambas variantes de host.
2. Buscar los 14 nombres exactos en catálogos bibliotecarios, repositorios y respaldos institucionales.
3. Reconstruir el registro de aprobación del Plan 2009: acto, expediente, firma y comunicación a UAI Economía.
4. Ubicar salida SIGEN 3672/09 e ingreso primario CGN; usar COMDOC sólo como ruta subsidiaria; correlacionar SISIO.
5. Mantener seis borradores DRAFT_NOT_SENT, SAF355 0/5 y ejecución 0/10.
""", encoding="utf-8")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V169.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint": "V170", "date": "2026-08-31", "master_catalog_entries": 597,
    "physical_local_copies": 597, "physical_local_hash_ok": 597,
    "remaining_catalog_physical_or_hash_gaps": 0,
    "state": "SOURCE_ARCHIVE_COMPLETE_COMMONCRAWL_FALSE_NEGATIVE_CORRECTED_CGN_CONTEXTUAL_RECIPIENT_IDENTIFIED_FORMAL_RECORDS_OPEN",
    "analytical_promotion": "NONE_V170_METHOD_AND_DOCUMENT_ROUTE_ONLY", "exact_entities": 34,
    "strict_asset_numerator_million_ars": NUMERATOR, "system_assets_million_ars": SYSTEM_ASSETS,
    "strict_coverage_pct": COVERAGE, "strict_coverage_increment_v169_pp": "0",
    "request_drafts_status": "DRAFT_NOT_SENT", "requests_submitted": 0, "responses_received": 0,
    "saf355_certifications_located": 0, "executed_historical_bank_rows_confirmed": 0,
    "plan_sigen_2009_body_located": False, "plan_sigen_2009_approval_act_located": False,
    "note_3672_09_body_located": False, "note_3672_contextual_recipient": "CGN",
    "note_3672_formal_addressee_located": False, "note_3672_recipient_identifier_located": False,
    "commoncrawl_catalog_collections_2013_2020": 74,
    "commoncrawl_exact_prefix_queries_completed": 4,
    "commoncrawl_exact_prefix_service_errors": 4,
    "commoncrawl_evaluable_query_responses_v170": 0,
    "commoncrawl_false_capture_rows_reclassified": 8,
    "commoncrawl_prior_negative_invalidated": True, "new_v170_sources": 1,
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V170.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

origin_rows = read_csv(ORIGINS)
origin_by_path = {row["path"]: row for row in origin_rows}
for path in iter_files(HIST_ROOT):
    rel = path.relative_to(CYCLE).as_posix()
    kind = "downloaded/preserved V170" if path == CC_CATALOG else "generated/preserved V170"
    note = "Common Crawl official catalog" if path == CC_CATALOG else "Common Crawl query method or raw diagnostic log"
    origin_by_path[rel] = {"path": rel, "origin": kind, "note": note}
for path in iter_files(SYNC):
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path": rel, "origin": "generated/updated V170", "note": "incremental source synchronization"}
for path in sorted(HERE.iterdir(), key=lambda item: item.name.casefold()):
    if path.is_file():
        rel = path.relative_to(CYCLE).as_posix()
        origin_by_path[rel] = {"path": rel, "origin": "generated/updated V170", "note": "archive-query correction and CGN recipient checkpoint"}
for path in (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V170.csv", AUDIT / "SOURCE_BACKUP_CENSUS_V170.csv", AUDIT / "SOURCE_PRESERVATION_MISSING_V170.csv", AUDIT / "CURRENT_SOURCE_COMPLETENESS_V170.json"):
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path": rel, "origin": "generated/updated V170", "note": "597-source completeness"}
write_csv(ORIGINS, list(origin_by_path.values()), ["path", "origin", "note"])

transparency = CYCLE / "TRANSPARENCY_README.md"
text = transparency.read_text(encoding="utf-8-sig")
if "## V170 · Corrección Common Crawl y receptor contextual CGN" not in text:
    text += """

## V170 · Corrección Common Crawl y receptor contextual CGN

El lote Common Crawl con patrón ancho no se usa como evidencia: seis páginas HTML 503 y dos grupos de capturas generales del dominio fueron falsos positivos, y el negativo V169 asociado queda superado. El catálogo oficial conserva 74 colecciones 2013-2020; cuatro consultas válidas exact-prefix de 2013 fallaron por servicio y no cuentan como ausencia. La Cuenta 2009 identifica contextualmente a CGN como receptora de Nota 3672/09, pero el destinatario formal, número de entrada, cuerpo e IDs SISIO permanecen abiertos. Archivo 597/597; panel 34 sin cambio.
"""
    transparency.write_text(text, encoding="utf-8")

(REPO / "BACKUP_ACTUALIZACION_2026-08-31.md").write_text(f"""# Backup de actualización · 2026-08-31

- Checkpoint: V170.
- Fuentes: 597/597; +1 fuente oficial y 3 derivados de consulta preservados.
- Plan 2009: falso negativo Common Crawl corregido; 14 cuerpos y acto abiertos.
- Nota 3672/09: CGN receptora contextual; cuerpo, ingreso formal e IDs SISIO abiertos.
- Panel: 34; {COVERAGE}% de activos; promociones 0.
- Solicitudes: 0 enviadas; seis DRAFT_NOT_SENT.
""", encoding="utf-8")

(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")

files = [{"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)} for path in sorted(HERE.iterdir(), key=lambda item: item.name.casefold()) if path.is_file() and path.name != "MANIFEST_V170.json"]
manifest = {
    "checkpoint": "V170", "parent_checkpoint": "V169",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "exact_entities": 34, "strict_coverage_pct": COVERAGE,
    "strict_asset_numerator_million_ars": NUMERATOR, "system_assets_million_ars": SYSTEM_ASSETS,
    "new_promotions": [], "historical_finding": "Common Crawl false negative corrected; CGN contextual recipient of Note 3672 identified",
    "source_archive": "597/597 catalogued physical SHA-valid; one V170 source added",
    "commoncrawl_collections_2013_2020": 74, "commoncrawl_evaluable_results_v170": 0,
    "plan_sigen_2009_page": "LOCATED", "plan_sigen_2009_body": "NOT_LOCATED",
    "approval_act": "NOT_LOCATED", "note_3672_09_body": "NOT_LOCATED",
    "note_3672_contextual_recipient": "CGN", "note_3672_formal_addressee": "NOT_LOCATED",
    "note_3672_recipient_identifier": "NOT_LOCATED", "crosswalk_gate": "OPEN",
    "closed_network_gate": "NO", "saf355_certifications": "0/5",
    "executed_historical_bank_rows": "0/10", "requests_submitted": 0, "files": files,
}
(HERE / "MANIFEST_V170.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in iter_files(REPO) if path != global_manifest]
payload = {
    "checkpoint": "V170", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": COVERAGE, "exact_entities": 34, "closed_network_gate": "NO",
    "source_audit": "597 master; 597 physical SHA-valid; one V170 source added",
    "historical_workstream": "Common Crawl query corrected; CGN contextual recipient identified; bodies, act, formal entry, SISIO and execution open; six drafts not sent",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
tmp = global_manifest.with_suffix(".json.V170tmp")
tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
tmp.replace(global_manifest)

print("V170 BUILD PASS · catalog=597/597 · new=1 · cc_collections=74 · exact_queries=4 errors=4 · recipient=CGN_CONTEXTUAL · exact=34 · requests=0")
