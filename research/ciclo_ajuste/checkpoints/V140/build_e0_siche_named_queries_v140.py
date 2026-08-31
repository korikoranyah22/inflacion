from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import re


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
PARENT = HERE.parent / "V139"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v140" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


EXPECTED = {
    "argentina_dgsiaf_esidif_line33_landing_2020.html": (31448, "8467e602b9e94773099cbe6c2a271c9c9aa720b9c2381d31be249f78c888fc67"),
    "argentina_dgsiaf_esidif_line33_sigade_payments_2020.pdf": (305243, "fe4b2382623d04bd313422b9fb72593a4d1e9ce1b8906770d81b4639581ae319"),
    "argentina_dgsiaf_execution_webservice.html": (30159, "d33b4a32fff38b7479b4ce1528d8cff8ba7cf386196e74c80a983a6eed7c557d"),
    "argentina_dgsiaf_siche_special_queries_2022_q3.html": (34162, "a368fb11936b716c4a03b5c708edc9bac50ed70d883551f4ac00d56dd0b344f0"),
}


def source(source_id: str, filename: str, title: str, url: str, publication: str,
           code: str, families: str, breaks: str, use: str, caveat: str,
           note: str) -> dict[str, object]:
    size, digest = EXPECTED[filename]
    source_type = "PDF oficial · captura preservada" if filename.endswith(".pdf") else "HTML oficial · captura preservada"
    return {
        "id": source_id, "filename": filename,
        "institution": "Dirección General de Sistemas Informáticos de Administración Financiera",
        "title": title, "url": url, "publication": publication, "period": publication,
        "code": code, "families": families, "breaks": breaks, "use": use,
        "caveat": caveat, "note": note, "bytes": size, "sha256": digest,
        "type": source_type,
    }


SOURCES = [
    source(
        "e0_dgsiaf_siche_special_queries_2022_q3",
        "argentina_dgsiaf_siche_special_queries_2022_q3.html",
        "SICHE · consultas especiales y mejoras · julio 2022",
        "https://www.argentina.gob.ar/economia/sechacienda/dgsiaf/boletin-trimestral-iii-2022/siche",
        "2022-07", "SICHE; consultas especiales",
        "SICHE;SIGADE;budget_item;beneficiary;order_observations;due_debt;journal_entries",
        "consulta disponible versus ejecución y cobertura target",
        "USABLE_EXACT_NAMED_QUERY_AND_FIELD_PROOF",
        "Prueba nombres y filtros de consultas internas para órganos rectores; no contiene resultados ni acceso público directo.",
        "V140 E0: publica Formulario por Pda. Presupuestaria y Sigade, Gastos por Beneficiarios, Deuda Exigible hasta 2008 y asientos detallados 2001-2012.",
    ),
    source(
        "e0_dgsiaf_esidif_line33_landing_2020",
        "argentina_dgsiaf_esidif_line33_landing_2020.html",
        "e-SIDIF · versión línea 33 · página de publicación",
        "https://www.argentina.gob.ar/noticias/e-sidif-version-linea-33",
        "2020-10-01", "e-SIDIF línea 33",
        "eSIDIF;release_date;payments;SIGADE",
        "fecha de versión versus operación histórica 2008",
        "USABLE_OFFICIAL_RELEASE_DATE_CONTROL",
        "Sólo fecha y vínculo del boletín; no prueba migración de registros 2008.",
        "V140 E0: fija la publicación oficial de línea 33 el 1 de octubre de 2020.",
    ),
    source(
        "e0_dgsiaf_esidif_line33_sigade_payments_2020",
        "argentina_dgsiaf_esidif_line33_sigade_payments_2020.pdf",
        "Newsletter e-SIDIF línea 33 · atributo SIGADE en Pagos",
        "https://www.argentina.gob.ar/sites/default/files/dgsiaf-newsletter-esidif-version-linea-33.pdf",
        "2020-10", "e-SIDIF línea 33; Pagos",
        "SIGADE;EPP;PG;NPG;CMR_DP;TCE;RTCE;payment_reports;payment_medium",
        "modelo e-SIDIF 2020 versus SC/SLU 2008 y migración no probada",
        "USABLE_PAYMENT_SIGADE_ATTRIBUTE_CROSSWALK",
        "Prueba campos y vínculos modernos en entorno Nación, no que el target haya migrado.",
        "V140 E0: SIGADE impacta EPP, PG, NPG, CMR-DP, TCE/RTCE y consultas/reportes; distingue medios originados al confirmar o después.",
    ),
    source(
        "e0_dgsiaf_execution_webservice_current",
        "argentina_dgsiaf_execution_webservice.html",
        "Servicio web · consulta de devengado y pagado por expediente",
        "https://www.argentina.gob.ar/economia/sechacienda/dgsiaf/compras-y-gastos/ejecucion",
        "consulta 2026-08-30", "Compras y Gastos; Ejecución",
        "expedient;payment_order;associated_payment;webservice",
        "servicio actual versus expediente/registro heredado 2008",
        "USABLE_CURRENT_EXPEDIENT_PAYMENT_LINK_CROSSWALK",
        "Describe el vínculo lógico por expediente; no prueba que S01:0342455/2008 sea consultable ni que contenga los target.",
        "V140 E0: la consulta actual retorna órdenes de pago y pagos asociados por ejercicio, tipo y número de expediente.",
    ),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        if not rows:
            raise ValueError(f"fields required for {path}")
        fields = list(rows[0])
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clone_parent() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    skip = {"build_e0_siche_capability_v139.py", "qa_v139.py", "MANIFEST_V139.json", "INHERITED_QA_STATUS_V139.csv"}
    for item in PARENT.iterdir():
        if not item.is_file() or item.name in skip or item.name.startswith("HANDOVER_PROXIMA_SESION"):
            continue
        target = HERE / item.name.replace("V139", "V140")
        text = item.read_text(encoding="utf-8-sig")
        placeholder = "historical_retrieval/__PARENT_V139__/"
        text = text.replace("historical_retrieval/v139/", placeholder)
        text = text.replace("_V139", "_V140").replace("_v139", "_v140")
        text = text.replace(placeholder, "historical_retrieval/v139/")
        if item.name.startswith("REQUEST_") or item.name in {
            "CURRENT_STATE_V139.csv", "E0_INSTITUTIONAL_REQUEST_PACKAGE_V139.md",
            "RETRIEVAL_LOG_V139.md",
        }:
            text = text.replace("V139", "V140").replace("v139", "v140")
        target.write_text(text, encoding="utf-8")


clone_parent()

for filename, (size, digest) in EXPECTED.items():
    path = BIN / filename
    assert path.is_file() and path.stat().st_size == size, path
    assert sha256(path) == digest, path

for item in SOURCES:
    item["local"] = "/" + (BIN / str(item["filename"])).relative_to(REPO).as_posix()

source_ids = {str(item["id"]) for item in SOURCES}

catalog = [row for row in read_csv(CATALOG) if row["id"] not in source_ids]
assert len(catalog) == 430
for item in SOURCES:
    catalog.append({
        "id": item["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": item["institution"],
        "titulo": item["title"], "url_original": item["url"], "archivo_local": item["local"],
        "fecha_descarga": "2026-08-30", "fecha_publicacion": item["publication"],
        "codigo_serie": item["code"], "periodo_utilizado": item["period"], "tipo": item["type"],
        "sha256": item["sha256"], "nota": item["note"],
    })
assert len(catalog) == 434 and len({row["id"] for row in catalog}) == 434
write_csv(CATALOG, catalog)
catalog_by_id = {row["id"]: row for row in catalog}

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V140.csv"
census = [row for row in read_csv(census_path) if row["source_id"] not in source_ids]
assert len(census) == 190
for row in census:
    master = catalog_by_id[row["source_id"]]
    row["local_path"] = master["archivo_local"]
    row["sha256"] = master["sha256"]
    path = REPO / master["archivo_local"].lstrip("/") if master["archivo_local"] else None
    if path and path.is_file():
        row["bytes"] = str(path.stat().st_size)
for item in SOURCES:
    census.append({
        "source_id": item["id"], "institution": item["institution"], "artifact": item["title"],
        "url": item["url"], "local_path": item["local"], "sha256": item["sha256"],
        "bytes": str(item["bytes"]), "period_coverage": item["period"],
        "variable_families": item["families"], "primary_source": "YES", "preserved": "YES",
        "method_breaks": item["breaks"], "use_status": item["use"], "caveat": item["caveat"],
    })
assert len(census) == 194 and len({row["source_id"] for row in census}) == 194
write_csv(census_path, census)

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V140.csv"
provenance = [row for row in read_csv(provenance_path) if row["source_id"] not in source_ids]
assert len(provenance) == 93
for row in provenance:
    master = catalog_by_id[row["source_id"]]
    row["local_path"] = master["archivo_local"]
    row["sha256"] = master["sha256"]
    path = REPO / master["archivo_local"].lstrip("/") if master["archivo_local"] else None
    if path and path.is_file():
        row["bytes"] = str(path.stat().st_size)
for item in SOURCES:
    provenance.append({
        "source_id": item["id"], "original_url": item["url"], "retrieval_url": item["url"],
        "capture_timestamp": "20260830", "cdx_digest": "N/A_DIRECT_OFFICIAL",
        "local_path": item["local"], "sha256": item["sha256"], "bytes": str(item["bytes"]),
        "provenance_note": "Descarga directa segura desde dominio oficial; binario preservado y validado con SHA-256.",
    })
assert len(provenance) == 97
write_csv(provenance_path, provenance)


named_queries = [
    {"row_id": "NQ140_01", "query_name": "Formulario por Pda. Presupuestaria y Sigade", "proved_filter_or_field": "partida presupuestaria + SIGADE", "target_input": "7.2.8;83106000;ejercicio2008;SAF355", "requested_output": "exportación completa y diccionario", "positive_result_use": "identifica formulario y contexto SIGADE", "zero_result_limit": "no prueba inexistencia ni falta de pago", "status": "EXACT_NAMED_QUERY_PROVED_NOT_RUN", "source_id": "e0_dgsiaf_siche_special_queries_2022_q3"},
    {"row_id": "NQ140_02", "query_name": "Formulario por Pda. Presupuestaria y Sigade", "proved_filter_or_field": "Beneficiario", "target_input": "sin filtro primero; luego BNA/Banco Nación y valor que devuelva la fila", "requested_output": "código;denominación;CUIT si obra", "positive_result_use": "resuelve beneficiario registral", "zero_result_limit": "la leyenda de cuenta no garantiza que BNA sea beneficiario", "status": "EXACT_FILTER_PROVED_NOT_RUN", "source_id": "e0_dgsiaf_siche_special_queries_2022_q3"},
    {"row_id": "NQ140_03", "query_name": "Formulario por Pda. Presupuestaria y Sigade", "proved_filter_or_field": "Clasificador Económico", "target_input": "valor sin restringir; recuperar valor de salida", "requested_output": "clasificador y descripción", "positive_result_use": "clasifica naturaleza económica", "zero_result_limit": "no usar un valor supuesto para excluir filas", "status": "EXACT_FILTER_PROVED_NOT_RUN", "source_id": "e0_dgsiaf_siche_special_queries_2022_q3"},
    {"row_id": "NQ140_04", "query_name": "Formulario por Pda. Presupuestaria y Sigade", "proved_filter_or_field": "Observaciones de la orden de pago", "target_input": "comisión;Banco Nación;83106000;71597;152677;2876", "requested_output": "texto íntegro de observaciones", "positive_result_use": "puede vincular propósito, medio o antecedente", "zero_result_limit": "campo vacío no equivale a operación inexistente", "status": "EXACT_OUTPUT_FIELD_PROVED_NOT_RUN", "source_id": "e0_dgsiaf_siche_special_queries_2022_q3"},
    {"row_id": "NQ140_05", "query_name": "Gastos por Beneficiarios", "proved_filter_or_field": "consulta especial", "target_input": "SAF355;ejercicio2008;BNA/Banco Nación;partida7.2.8", "requested_output": "formulario;beneficiario;importe;estado;vínculos", "positive_result_use": "control independiente por beneficiario", "zero_result_limit": "BNA puede no ser el beneficiario registral", "status": "NAMED_QUERY_PROVED_NOT_RUN", "source_id": "e0_dgsiaf_siche_special_queries_2022_q3"},
    {"row_id": "NQ140_06", "query_name": "Deuda Exigible hasta 2008", "proved_filter_or_field": "consulta especial", "target_input": "SAF355;71597;152677;2876;83106000", "requested_output": "definición temporal;estado;saldo;fecha de corte", "positive_result_use": "puede identificar deuda exigible al corte de la consulta", "zero_result_limit": "ausencia no prueba pago, anulación o inexistencia", "status": "NAMED_QUERY_PROVED_SEMANTICS_OPEN_NOT_RUN", "source_id": "e0_dgsiaf_siche_special_queries_2022_q3"},
    {"row_id": "NQ140_07", "query_name": "Consulta detallada de asientos 2001 a 2012", "proved_filter_or_field": "Debe y Haber", "target_input": "ejercicio2008;importe32270.30;cuenta/descripcion", "requested_output": "Debe;Haber;signo;fecha", "positive_result_use": "identifica sentido contable", "zero_result_limit": "asiento contable no prueba débito bancario", "status": "NAMED_QUERY_FIELDS_PROVED_NOT_RUN", "source_id": "e0_dgsiaf_siche_special_queries_2022_q3"},
    {"row_id": "NQ140_08", "query_name": "Consulta detallada de asientos 2001 a 2012", "proved_filter_or_field": "descripción de cuenta contable", "target_input": "comisiones;Banco Nación;cuentas vinculadas", "requested_output": "cuenta;código;descripción", "positive_result_use": "permite construir contrapartida", "zero_result_limit": "descripción SIGADE y cuenta contable son dominios distintos", "status": "NAMED_QUERY_FIELDS_PROVED_NOT_RUN", "source_id": "e0_dgsiaf_siche_special_queries_2022_q3"},
    {"row_id": "NQ140_09", "query_name": "Consulta detallada de asientos 2001 a 2012", "proved_filter_or_field": "número de asiento anual + tipo", "target_input": "ejercicio2008;Normal;importe/fecha", "requested_output": "número anual;tipo Inicio/Normal/Cierre", "positive_result_use": "distingue movimiento operativo de apertura/cierre", "zero_result_limit": "sin diccionario no asignar un asiento al target", "status": "NAMED_QUERY_FIELDS_PROVED_NOT_RUN", "source_id": "e0_dgsiaf_siche_special_queries_2022_q3"},
    {"row_id": "NQ140_10", "query_name": "Paquete discriminante V140", "proved_filter_or_field": "cuatro consultas preexistentes", "target_input": "runbook V140", "requested_output": "exportaciones separadas + parámetros + conteos", "positive_result_use": "resuelve tipo, beneficiario, contabilidad y posible deuda exigible", "zero_result_limit": "cero sólo es evaluable con metadatos, diccionario y cobertura", "status": "EXACT_QUERY_PACKAGE_PROVED_TARGET_ROWS_OPEN", "source_id": "e0_dgsiaf_siche_special_queries_2022_q3"},
]
write_csv(HERE / "E0_SICHE_NAMED_QUERY_TARGET_MAP_V140.csv", named_queries)

payment_crosswalk = [
    {"row_id": "PX140_01", "record": "EPP", "proved_sigade_scope": "atributo SIGADE en detalle de ítems", "target_use": "escenario/programación", "required_link": "SIGADE83106000→OP/Pago", "status": "CURRENT_SCHEMA_PROVED_LEGACY_MIGRATION_OPEN", "source_id": "e0_dgsiaf_esidif_line33_sigade_payments_2020", "locator": "PDF p.4"},
    {"row_id": "PX140_02", "record": "PG", "proved_sigade_scope": "atributo SIGADE en detalle de ítems", "target_use": "pago", "required_link": "PG→medio→beneficiario→importe", "status": "CURRENT_SCHEMA_PROVED_LEGACY_MIGRATION_OPEN", "source_id": "e0_dgsiaf_esidif_line33_sigade_payments_2020", "locator": "PDF p.4"},
    {"row_id": "PX140_03", "record": "NPG", "proved_sigade_scope": "atributo SIGADE en detalle de ítems", "target_use": "nota de pago", "required_link": "NPG→OP/PG→cuentas", "status": "CURRENT_SCHEMA_PROVED_LEGACY_MIGRATION_OPEN", "source_id": "e0_dgsiaf_esidif_line33_sigade_payments_2020", "locator": "PDF p.4"},
    {"row_id": "PX140_04", "record": "CMR-DP", "proved_sigade_scope": "atributo SIGADE en anulación/rechazo bancario", "target_use": "estado reversado/rechazado", "required_link": "comprobante origen→motivo→fecha", "status": "CURRENT_SCHEMA_PROVED_LEGACY_MIGRATION_OPEN", "source_id": "e0_dgsiaf_esidif_line33_sigade_payments_2020", "locator": "PDF p.4"},
    {"row_id": "PX140_05", "record": "TCE/RTCE", "proved_sigade_scope": "atributo SIGADE", "target_use": "transferencia entre cuentas escriturales", "required_link": "cuenta origen/destino→importe", "status": "CURRENT_SCHEMA_PROVED_LEGACY_MIGRATION_OPEN", "source_id": "e0_dgsiaf_esidif_line33_sigade_payments_2020", "locator": "PDF p.4"},
    {"row_id": "PX140_06", "record": "Consultas y reportes de Pagos", "proved_sigade_scope": "ajuste de visibilidad SIGADE", "target_use": "salida filtrable", "required_link": "exportación por SIGADE", "status": "CURRENT_SCHEMA_PROVED_LEGACY_MIGRATION_OPEN", "source_id": "e0_dgsiaf_esidif_line33_sigade_payments_2020", "locator": "PDF p.4"},
    {"row_id": "PX140_07", "record": "Solicitud de Pagos por web service", "proved_sigade_scope": "recepción con atributo SIGADE", "target_use": "control de interoperabilidad", "required_link": "solicitud→pago", "status": "CURRENT_SCHEMA_PROVED_NOT_TARGET_ROUTE", "source_id": "e0_dgsiaf_esidif_line33_sigade_payments_2020", "locator": "PDF p.4"},
    {"row_id": "PX140_08", "record": "Reporte Variable Resumen de Pagos", "proved_sigade_scope": "beneficiario, carácter, fuente de cuenta y emisor distinto", "target_use": "control de beneficiario real", "required_link": "emisor/beneficiario/cuenta", "status": "CURRENT_FILTER_SCHEMA_PROVED_LEGACY_MIGRATION_OPEN", "source_id": "e0_dgsiaf_esidif_line33_sigade_payments_2020", "locator": "PDF p.4"},
    {"row_id": "PX140_09", "record": "Modelo de Medios de Pago", "proved_sigade_scope": "marca de medio originado en confirmación o generado después", "target_use": "separar confirmación de regularización posterior", "required_link": "marca temporal→medio→PG", "status": "CURRENT_PHASE_DISCRIMINATOR_PROVED_LEGACY_MIGRATION_OPEN", "source_id": "e0_dgsiaf_esidif_line33_sigade_payments_2020", "locator": "PDF p.4"},
    {"row_id": "PX140_10", "record": "Consulta devengado/pagado por expediente", "proved_sigade_scope": "retorna OP y pagos asociados por ejercicio/tipo/número", "target_use": "cerrar expediente→OP→pago si existe cruce", "required_link": "S01:0342455/2008 o identificador migrado", "status": "CURRENT_LOGICAL_LINK_PROVED_LEGACY_TARGET_OPEN", "source_id": "e0_dgsiaf_execution_webservice_current", "locator": "página oficial"},
]
write_csv(HERE / "E0_SIGADE_PAYMENT_ATTRIBUTE_CROSSWALK_V140.csv", payment_crosswalk)

runbook = [
    {"step_id": "QR140_01", "sequence": "1", "query": "Formulario por Pda. Presupuestaria y Sigade", "filters": "SAF355;2008;Pda7.2.8;SIGADE83106000;sin beneficiario", "output": "todas las filas y columnas", "decision": "establecer universo base", "status": "DRAFT_NOT_SENT"},
    {"step_id": "QR140_02", "sequence": "2", "query": "misma consulta", "filters": "N°SIDIF71597;152677;2876 si el campo existe", "output": "coincidencia individual", "decision": "resolver tipo/número/estado", "status": "DRAFT_NOT_SENT"},
    {"step_id": "QR140_03", "sequence": "3", "query": "misma consulta", "filters": "Beneficiario sin restricción; luego BNA/Banco Nación", "output": "beneficiario/código/CUIT", "decision": "probar o refutar BNA registral", "status": "DRAFT_NOT_SENT"},
    {"step_id": "QR140_04", "sequence": "4", "query": "misma consulta", "filters": "observaciones contiene comisión/Banco Nación/83106000", "output": "observaciones íntegras", "decision": "buscar propósito y medio", "status": "DRAFT_NOT_SENT"},
    {"step_id": "QR140_05", "sequence": "5", "query": "Gastos por Beneficiarios", "filters": "SAF355;2008;partida7.2.8;BNA y variantes", "output": "gastos/formularios/estados", "decision": "control independiente", "status": "DRAFT_NOT_SENT"},
    {"step_id": "QR140_06", "sequence": "6", "query": "Deuda Exigible hasta 2008", "filters": "SAF355;SIDIF target;SIGADE83106000", "output": "definición;corte;saldo;estado", "decision": "clasificar deuda al corte sin inferir después", "status": "DRAFT_NOT_SENT"},
    {"step_id": "QR140_07", "sequence": "7", "query": "Consulta detallada de asientos 2001 a 2012", "filters": "2008;32270.30 y partes;cuenta/descripcion", "output": "Debe;Haber;cuenta;asiento anual;tipo;fecha", "decision": "construir contrapartida", "status": "DRAFT_NOT_SENT"},
    {"step_id": "QR140_08", "sequence": "8", "query": "Pagos por SIGADE", "filters": "83106000;2008;target IDs", "output": "EPP;PG;NPG;CMR-DP;TCE/RTCE o equivalentes legacy", "decision": "cruzar pago, rechazo y regularización", "status": "DRAFT_NOT_SENT"},
    {"step_id": "QR140_09", "sequence": "9", "query": "Resumen de Pagos", "filters": "beneficiario;emisor distinto;fuente/cuenta", "output": "exportación con medios", "decision": "resolver pagador/beneficiario/cuenta", "status": "DRAFT_NOT_SENT"},
    {"step_id": "QR140_10", "sequence": "10", "query": "Conciliación Bancaria", "filters": "cuenta BNA;importe/partes;formulario recuperado", "output": "extracto externo;interno/Libro Banco;aplicación;estado", "decision": "cerrar débito", "status": "DRAFT_NOT_SENT"},
    {"step_id": "QR140_11", "sequence": "11", "query": "AMIDDF", "filters": "tipo/número/SAF recuperados", "output": "índice;caja;cuerpo;folios;imagen", "decision": "cerrar respaldo", "status": "DRAFT_NOT_SENT"},
    {"step_id": "QR140_12", "sequence": "12", "query": "Auditoría de resultado cero", "filters": "cada consulta por separado", "output": "sistema;modelo;consulta;parámetros;fecha;filas;cobertura;exclusiones;diccionario", "decision": "evaluar suficiencia negativa", "status": "DRAFT_NOT_SENT"},
]
write_csv(HERE / "E0_EXACT_SICHE_QUERY_RUNBOOK_V140.csv", runbook)

zero_rules = [
    {"rule_id": "ZR140_01", "query": "Formulario por Pda. y Sigade", "zero_permits": "sólo que esos filtros no devolvieron filas en ese dataset", "zero_forbids": "inexistencia del formulario o falta de pago", "required_metadata": "modelo;cobertura;filtros;diccionario;filas", "status": "FROZEN"},
    {"rule_id": "ZR140_02", "query": "Gastos por Beneficiarios=BNA", "zero_permits": "BNA no aparece bajo esa variante", "zero_forbids": "BNA no intervino", "required_metadata": "campo/código/denominaciones/rango", "status": "FROZEN"},
    {"rule_id": "ZR140_03", "query": "Deuda Exigible hasta 2008", "zero_permits": "no hay fila bajo definición y corte informados", "zero_forbids": "fue pagado o anulado", "required_metadata": "definición;fecha de corte;estados incluidos", "status": "FROZEN"},
    {"rule_id": "ZR140_04", "query": "Asientos 2001-2012", "zero_permits": "no coincide importe/cuenta consultados", "zero_forbids": "no existió asiento agregado o por partes", "required_metadata": "cuentas;importe exacto/partes;tipo;periodo", "status": "FROZEN"},
    {"rule_id": "ZR140_05", "query": "Pagos por SIGADE", "zero_permits": "no hay fila en el esquema consultado", "zero_forbids": "el legacy no pagó", "required_metadata": "migración/cobertura SC-SLU-eSIDIF;tipos", "status": "FROZEN"},
    {"rule_id": "ZR140_06", "query": "Conciliación Bancaria", "zero_permits": "sin coincidencia bajo cuenta/fecha/importe", "zero_forbids": "no hubo débito ni regularización", "required_metadata": "cuentas;extractos cargados;ventana;partes", "status": "FROZEN"},
    {"rule_id": "ZR140_07", "query": "AMIDDF", "zero_permits": "índice consultado no localizó caja/cuerpo", "zero_forbids": "documentación expurgada o nunca remitida", "required_metadata": "fondo;serie;subserie;ejercicio;planillas;cajas consultadas", "status": "FROZEN"},
    {"rule_id": "ZR140_08", "query": "Paquete completo", "zero_permits": "cierre de rutas consultadas con alcance declarado", "zero_forbids": "0/10 confirmado sin respuesta institucional y cadena de custodia", "required_metadata": "respuesta firmada/expediente;adjuntos;derivaciones", "status": "FROZEN"},
]
write_csv(HERE / "E0_QUERY_ZERO_RESULT_INTERPRETATION_V140.csv", zero_rules)

pdf_visual = [
    {"control_id": "PV140_01", "source_id": "e0_dgsiaf_esidif_line33_sigade_payments_2020", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v140/binaries/argentina_dgsiaf_esidif_line33_sigade_payments_2020.pdf", "pdf_page": "1", "rendered_check": "portada: línea 33, octubre 2020, DGSIAF", "result": "PASS"},
    {"control_id": "PV140_02", "source_id": "e0_dgsiaf_esidif_line33_sigade_payments_2020", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v140/binaries/argentina_dgsiaf_esidif_line33_sigade_payments_2020.pdf", "pdf_page": "4", "rendered_check": "SIGADE en EPP/PG/NPG/CMR-DP/TCE-RTCE y marca temporal de medio", "result": "PASS"},
]
write_csv(HERE / "E0_V140_PDF_VISUAL_CONTROL.csv", pdf_visual)


query_plan = [
    {"query_id": "SQ140_01", "sequence": "1", "system": "SICHE · Formulario por Pda. Presupuestaria y Sigade", "filter_set": "SAF355;2008;7.2.8;83106000;sin beneficiario", "requested_output": "universo completo, columnas y diccionario", "success_test": "fila(s) base identificada(s)", "fallback": "consulta especial por parámetros equivalentes", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ140_02", "sequence": "2", "system": "SICHE · misma consulta", "filter_set": "SIDIF71597;152677;2876;observaciones", "requested_output": "tipo;número;estado;beneficiario;observaciones", "success_test": "tres registros clasificados", "fallback": "sin filtro SIDIF y cruce por importe", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ140_03", "sequence": "3", "system": "SICHE · Gastos por Beneficiarios", "filter_set": "SAF355;2008;BNA/Banco Nación;7.2.8", "requested_output": "formularios e importes", "success_test": "control independiente", "fallback": "variantes/código de beneficiario", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ140_04", "sequence": "4", "system": "SICHE · Deuda Exigible hasta 2008", "filter_set": "SAF355;SIDIF target;SIGADE83106000", "requested_output": "definición;corte;estado;saldo", "success_test": "estado al corte definido", "fallback": "consulta sin restricción de estado", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ140_05", "sequence": "5", "system": "SICHE · Asientos detallados 2001-2012", "filter_set": "2008;32270.30/partes;cuenta/descripcion", "requested_output": "Debe;Haber;cuenta;asiento anual;tipo;fecha", "success_test": "contrapartida identificada", "fallback": "rango anual por descripción", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ140_06", "sequence": "6", "system": "Pagos · SIGADE", "filter_set": "83106000;2008;SIDIF/OP target", "requested_output": "EPP;PG;NPG;CMR-DP;TCE/RTCE o equivalentes", "success_test": "pago/rechazo/regularización vinculados", "fallback": "SC/SLU legacy y reporte variable", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ140_07", "sequence": "7", "system": "Consulta por expediente", "filter_set": "S01:0342455/2008 o identificador migrado", "requested_output": "OP y pagos asociados", "success_test": "expediente→OP→pago", "fallback": "COMDOC/FindDoc y cruce manual", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ140_08", "sequence": "8", "system": "Conciliación Bancaria", "filter_set": "cuenta;importe/partes;formulario recuperado", "requested_output": "extracto externo;interno/Libro Banco;aplicación;estado", "success_test": "débito conciliado", "fallback": "ventana ampliada", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ140_09", "sequence": "9", "system": "AMIDDF", "filter_set": "SAF355;2008;tipo/número recuperados", "requested_output": "índice;caja;cuerpo;folios;imágenes", "success_test": "respaldo localizado", "fallback": "planillas/tejuelos por subserie", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ140_10", "sequence": "10", "system": "RAIP Economía · auditoría de consulta", "filter_set": "cada consulta y fallback por separado", "requested_output": "parámetros;diccionario;cobertura;filas;exclusiones", "success_test": "positivo o cero reproducible", "fallback": "derivación al órgano rector", "status": "DRAFT_NOT_SENT"},
]
write_csv(HERE / "E0_SICHE_TARGET_QUERY_PLAN_V140.csv", query_plan)

ledger_path = HERE / "E0_FISCAL_MECHANISM_LEDGER_V140.csv"
new_ids = {f"F{n}" for n in range(209, 219)}
ledger = [row for row in read_csv(ledger_path) if row["ledger_id"] not in new_ids]
ledger_specs = [
    (209, "2022", "SICHE_NAMED_QUERY", "PDA_SIGADE_FORM", "Secretaría de Hacienda", "órganos rectores", "formularios", "Pda+SIGADE", "e0_dgsiaf_siche_special_queries_2022_q3", "página oficial", "EXACT_QUERY_PROVED_NOT_RUN", "Consulta exacta para 7.2.8/83106000."),
    (210, "2022", "SICHE_NAMED_QUERY", "BENEFICIARY_EXPANSION", "Secretaría de Hacienda", "órganos rectores", "gastos", "Gastos por Beneficiarios", "e0_dgsiaf_siche_special_queries_2022_q3", "página oficial", "QUERY_PROVED_NOT_RUN", "Control independiente por beneficiario."),
    (211, "2022", "SICHE_NAMED_QUERY", "DUE_DEBT", "Secretaría de Hacienda", "órganos rectores", "deuda hasta 2008", "Deuda Exigible", "e0_dgsiaf_siche_special_queries_2022_q3", "página oficial", "QUERY_PROVED_SEMANTICS_OPEN_NOT_RUN", "Requiere fecha de corte y diccionario."),
    (212, "2001-2012", "SICHE_NAMED_QUERY", "DETAILED_JOURNAL", "Secretaría de Hacienda", "órganos rectores", "asientos", "Debe/Haber/cuenta/asiento/tipo", "e0_dgsiaf_siche_special_queries_2022_q3", "página oficial", "QUERY_FIELDS_PROVED_NOT_RUN", "Asiento no equivale a pago bancario."),
    (213, "2020", "ESIDIF_PAYMENT", "SIGADE_ATTRIBUTE", "SAF/TGN", "beneficiario", "EPP/PG/NPG/CMR-DP/TCE/RTCE", "SIGADE", "e0_dgsiaf_esidif_line33_sigade_payments_2020", "PDF p.4", "CURRENT_SCHEMA_PROVED_LEGACY_OPEN", "Crosswalk; migración no probada."),
    (214, "2020", "ESIDIF_PAYMENT", "PAYMENT_SUMMARY", "SAF/TGN", "usuarios", "pagos", "beneficiario/emisor/fuente/cuenta", "e0_dgsiaf_esidif_line33_sigade_payments_2020", "PDF p.4", "CURRENT_FILTERS_PROVED_LEGACY_OPEN", "Útil para separar emisor y beneficiario."),
    (215, "2020", "ESIDIF_PAYMENT", "PAYMENT_MEDIUM_TIMING", "SAF/TGN", "contabilidad", "medios", "originado en confirmación/posterior", "e0_dgsiaf_esidif_line33_sigade_payments_2020", "PDF p.4", "CURRENT_DISCRIMINATOR_PROVED_LEGACY_OPEN", "Distingue pago de regularización posterior."),
    (216, "actual", "EXECUTION_WEBSERVICE", "EXPEDIENT_LINK", "SAF", "usuario", "expediente", "OP+pagos asociados", "e0_dgsiaf_execution_webservice_current", "página oficial", "CURRENT_LOGICAL_LINK_PROVED_TARGET_OPEN", "Servicio actual; expediente legado abierto."),
    (217, "2008-2026", "TARGET_QUERY", "RUNBOOK", "Ministerio de Economía", "solicitante", "tres SIDIF", "consultas nombradas", "e0_dgsiaf_siche_special_queries_2022_q3", "runbook V140", "QUERY_PACKAGE_PROVED_NOT_EXECUTED", "Seis pedidos siguen no enviados."),
    (218, "2008-2026", "TARGET_QUERY", "ZERO_RESULT_AUDIT", "Ministerio de Economía", "solicitante", "cada dataset", "metadatos de búsqueda", "e0_dgsiaf_siche_special_queries_2022_q3", "matriz V140", "NEGATIVE_STANDARD_PROVED_NO_RESPONSE", "Cero sin metadatos no cierra la brecha."),
]
for number, window, mechanism, phase, payer, recipient, universe, instrument, sid, locator, status, interpretation in ledger_specs:
    ledger.append({
        "ledger_id": f"F{number}", "window": window, "mechanism": mechanism, "phase": phase,
        "as_of_date": "N/D", "payer": payer, "recipient": recipient, "universe": universe,
        "instrument": instrument, "amount_original": "N/D", "original_unit": "N/D",
        "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE",
        "source_id": sid, "source_locator": locator, "realization_status": status,
        "additivity": "NON_ADDITIVE", "status_interpretation": interpretation,
        "caveat": "No convertir capacidad, campo o consulta en resultado target.",
    })
assert len(ledger) == 218
write_csv(ledger_path, ledger)

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V140.csv"
breaks = read_csv(breaks_path)
new_break_ids = {
    "named_query_not_executed", "pda_sigade_query_not_target_row", "beneficiary_filter_not_bna_identity",
    "due_debt_zero_not_payment", "journal_entry_not_bank_debit", "current_sigade_payment_schema_not_legacy_migration",
    "payment_medium_timing_not_target_state", "current_expedient_service_not_legacy_availability",
}
breaks = [row for row in breaks if row["break_id"] not in new_break_ids]
new_breaks = [
    ("named_query_not_executed", "access", "Conocer el nombre de consulta no ejecuta la búsqueda.", "Mantener runbook y pedido como borrador hasta autorización.", "e0_dgsiaf_siche_special_queries_2022_q3"),
    ("pda_sigade_query_not_target_row", "inference", "Pda+SIGADE es un ajuste exacto de filtros, no una fila.", "Exigir exportación, parámetros y conteo.", "e0_dgsiaf_siche_special_queries_2022_q3"),
    ("beneficiary_filter_not_bna_identity", "identity", "La leyenda Banco Nación no fija el beneficiario registral.", "Correr primero sin beneficiario y después variantes.", "E0_SICHE_NAMED_QUERY_TARGET_MAP_V140.csv"),
    ("due_debt_zero_not_payment", "state", "Cero en Deuda Exigible depende de definición y corte.", "No inferir pago o anulación sin diccionario/estado.", "e0_dgsiaf_siche_special_queries_2022_q3"),
    ("journal_entry_not_bank_debit", "phase", "Debe/Haber prueba asiento, no banco.", "Cruzar extracto, Libro Banco y aplicación.", "e0_dgsiaf_siche_special_queries_2022_q3"),
    ("current_sigade_payment_schema_not_legacy_migration", "system", "SIGADE aparece en Pagos e-SIDIF 2020.", "Usar como crosswalk y preguntar por equivalente SC/SLU.", "e0_dgsiaf_esidif_line33_sigade_payments_2020"),
    ("payment_medium_timing_not_target_state", "phase", "La marca temporal moderna distingue origen del medio.", "No atribuirla retroactivamente al target.", "e0_dgsiaf_esidif_line33_sigade_payments_2020"),
    ("current_expedient_service_not_legacy_availability", "system", "El servicio actual enlaza expediente, OP y pagos.", "No presumir que un expediente COMDOC 2008 esté migrado.", "e0_dgsiaf_execution_webservice_current"),
]
for break_id, dimension, problem, rule, evidence in new_breaks:
    breaks.append({"break_id": break_id, "dimension": dimension, "problem": problem, "rule": rule, "status": "FROZEN_V140", "evidence": evidence})
assert len(breaks) == 171
write_csv(breaks_path, breaks)

trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V140.csv"
trace = [row for row in read_csv(trace_path) if not row["trace_id"].startswith("TR140_")]
trace_specs = [
    (157, "SICHE_PDA_SIGADE", "Exportación Formulario por Pda. Presupuestaria y Sigade", "7.2.8;83106000;SAF355;2008", "tipo;número;SIDIF;estado;beneficiario;importe;observaciones"),
    (158, "SICHE_BENEFICIARY", "Exportación Gastos por Beneficiarios", "SAF355;2008;BNA/Banco Nación", "beneficiario;código;CUIT;formulario;importe;estado"),
    (159, "SICHE_DUE_DEBT", "Exportación Deuda Exigible hasta 2008 y definición", "71597;152677;2876;83106000", "fecha de corte;estados;saldo;tipo;vínculos"),
    (160, "SICHE_JOURNAL", "Asientos detallados 2001-2012 para 2008", "32270.30;partes;cuenta/descripcion", "Debe;Haber;cuenta;asiento anual;tipo;fecha"),
    (161, "PAYMENT_SIGADE", "Pagos y modificaciones con atributo SIGADE", "83106000;target SIDIF/OP", "EPP;PG;NPG;CMR-DP;TCE/RTCE;medio;estado"),
    (162, "PAYMENT_SUMMARY", "Resumen de Pagos y filtros de beneficiario/emisor/cuenta", "SAF355;2008;83106000", "emisor;beneficiario;fuente;cuenta;medio;importe"),
    (163, "EXPEDIENT_PAYMENT", "OP y pagos asociados al expediente", "S01:0342455/2008;equivalencia migrada", "expediente;OP;PG;estado;fecha;importe"),
    (164, "QUERY_AUDIT", "Metadatos y diccionario de cada consulta", "cuatro consultas SICHE;Pagos;Conciliación", "sistema;modelo;consulta;filtros;fecha;filas;cobertura;exclusiones"),
]
for number, gap, record, identifiers, fields in trace_specs:
    trace.append({
        "trace_id": f"TR140_{number}", "request_id": "REQ133_ECON",
        "institution": "Ministerio de Economía / Secretaría de Hacienda",
        "gap_id": gap, "requested_record": record, "period_or_date": "2008; consulta 2026",
        "identifiers": identifiers, "minimum_usable_fields": fields,
        "confidentiality_fallback": "exportación disociada; tachas parciales; metadatos y diccionario",
        "status": "DRAFT_NOT_SENT",
    })
assert len(trace) == 164
write_csv(trace_path, trace)

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V140.csv"
keys = [row for row in read_csv(keys_path) if not row["key_id"].startswith("SK140_")]
key_specs = [
    (171, "named_query", "Formulario por Pda. Presupuestaria y Sigade", "consulta target principal"),
    (172, "named_query", "Gastos por Beneficiarios", "control por beneficiario"),
    (173, "named_query", "Deuda Exigible hasta 2008", "control de estado al corte"),
    (174, "named_query", "Consulta detallada de asientos 2001 a 2012", "control contable"),
    (175, "base_filters", "SAF355;ejercicio2008;Pda7.2.8;SIGADE83106000", "universo base"),
    (176, "sidif", "71597;152677;2876", "localizadores individuales"),
    (177, "beneficiary", "sin_restriccion;BNA;Banco Nación", "evitar falso negativo"),
    (178, "observations", "comisión;Banco Nación;83106000", "texto OP"),
    (179, "journal", "32270.30;partes;Debe;Haber;Normal", "asiento y signo"),
    (180, "payment_records", "EPP;PG;NPG;CMR-DP;TCE;RTCE", "crosswalk SIGADE"),
    (181, "expedient", "S01:0342455/2008;identificador migrado", "expediente→OP→pago"),
    (182, "negative_metadata", "consulta;modelo;diccionario;filtros;fecha;filas;cobertura;exclusiones", "resultado cero reproducible"),
]
for number, group, key, purpose in key_specs:
    keys.append({
        "key_id": f"SK140_{number}", "request_id": "REQ133_ECON", "key_group": group,
        "exact_key": key, "search_purpose": purpose,
        "source_or_basis": "E0_SICHE_NAMED_QUERY_TARGET_MAP_V140.csv;E0_EXACT_SICHE_QUERY_RUNBOOK_V140.csv",
        "caveat": "Clave o nombre probado; no confirma resultado.",
    })
assert len(keys) == 182
write_csv(keys_path, keys)


register_path = HERE / "E0_REQUEST_RESPONSE_REGISTER_V140.csv"
register = read_csv(register_path)
for row in register:
    row["status"] = "DRAFT_NOT_SENT"
    row["submitted_on"] = "N/A"
    row["submission_channel"] = "N/A"
    row["receipt_or_case_id"] = "N/A"
write_csv(register_path, register)

request_path = HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V140.md"
request_text = request_path.read_text(encoding="utf-8-sig")
marker = "## Clave V140 · consultas SICHE nombradas y runbook exacto"
if marker not in request_text:
    request_text += f"""

{marker}

La documentación técnica oficial de DGSIAF permite reemplazar el pedido genérico de “buscar en SICHE” por consultas preexistentes con nombre y alcance publicados. Se solicita que el organismo competente ejecute o derive internamente las siguientes consultas y entregue sus exportaciones en el estado en que obren, junto con el diccionario de datos y los parámetros utilizados:

1. **`Formulario por Pda. Presupuestaria y Sigade`**: ejecutar primero para `SAF 355`, ejercicio `2008`, partida `7.2.8` y SIGADE `83106000`, sin restringir beneficiario. Luego cruzar con SIDIF `71597`, `152677` y `2876` si ese campo está disponible. Entregar tipo y número de formulario, estado, fechas, beneficiario, importes, clasificador económico y texto íntegro de las observaciones de la orden de pago. DGSIAF documentó expresamente que esta consulta permite filtrar por beneficiario y clasificador económico e incorpora observaciones de la orden de pago.
2. **`Gastos por Beneficiarios`**: consultar el mismo SAF, ejercicio y partida, primero sin identificar beneficiario y después con variantes `BNA` y `Banco Nación`, preservando código, denominación y CUIT si obran. La leyenda contable no se toma como prueba de que BNA sea el beneficiario registral.
3. **`Deuda Exigible hasta 2008`**: buscar por los tres SIDIF y SIGADE `83106000`, informando previamente la definición de “deuda exigible”, fecha de corte, estados incluidos y tratamiento de pagos parciales, rechazos, anulaciones y regularizaciones. Una respuesta sin filas no se interpretará como pago o inexistencia sin esos metadatos.
4. **`Consulta detallada de asientos 2001 a 2012`**: filtrar ejercicio 2008 por `$32.270,30`, por sus eventuales componentes y por descripciones/cuentas vinculadas a comisiones y Banco Nación. Entregar Debe, Haber, signo, código y descripción de cuenta, número de asiento anual, tipo `Inicio/Normal/Cierre` y fecha. El asiento se solicita como puente contable y no sustituye el extracto bancario.

Como cruce de Pagos se pide la salida por atributo SIGADE —o equivalente funcional de SIDIF Central/SLU— para `EPP`, `PG`, `NPG`, `CMR-DP`, `TCE/RTCE` y reportes asociados. La línea 33 de e-SIDIF documenta que SIGADE alcanza esos comprobantes en el entorno Nación y que el modelo de medios de pago distingue los generados al confirmar el pago de los creados con posterioridad. Este esquema de 2020 se usa únicamente como diccionario de búsqueda: no se presume migración de los registros 2008.

Si obra una equivalencia consultable del expediente `S01:0342455/2008`, se solicita asimismo la consulta de devengado y pagado por expediente, que según el catálogo oficial devuelve órdenes de pago y pagos asociados por ejercicio, tipo y número. Finalmente, toda fila positiva deberá cruzarse con Conciliación Bancaria y AMIDDF. Para cada resultado cero se requieren sistema, modelo, nombre exacto de consulta, filtros, fecha, cobertura temporal, cantidad de filas, exclusiones y diccionario. **Estado: BORRADOR_NO_ENVIADO.**
"""
request_path.write_text(request_text, encoding="utf-8")

checklist_path = HERE / "REQUEST_SUBMISSION_CHECKLIST_V140.md"
checklist = checklist_path.read_text(encoding="utf-8-sig")
check_marker = "## Control V140 · consultas nombradas"
if check_marker not in checklist:
    checklist += f"""

{check_marker}

- [ ] Pedir `Formulario por Pda. Presupuestaria y Sigade` con 7.2.8/83106000 y sin beneficiario primero.
- [ ] Correr por separado `Gastos por Beneficiarios`, `Deuda Exigible hasta 2008` y asientos 2001-2012.
- [ ] Pedir definición y fecha de corte de Deuda Exigible antes de interpretar resultados.
- [ ] Usar SIGADE en Pagos como crosswalk posterior, sin presumir migración 2008.
- [ ] Separar asiento, orden, pago, medio posterior, débito y conciliación.
- [ ] Exigir diccionario, filtros y cobertura para todo resultado cero.
- [ ] Confirmar autorización expresa antes de presentar cualquiera de los seis borradores.
"""
checklist_path.write_text(checklist, encoding="utf-8")

source_refs_path = HERE / "SOURCE_REFERENCES_V140.md"
source_refs = source_refs_path.read_text(encoding="utf-8-sig")
ref_lines = []
for line in source_refs.splitlines():
    match = re.match(r"^- `([^`]+)`", line)
    if match and match.group(1) in catalog_by_id:
        canonical = catalog_by_id[match.group(1)]["archivo_local"]
        line = re.sub(r"`/[^`]+`", f"`{canonical}`", line)
    ref_lines.append(line)
source_refs = "\n".join(ref_lines) + "\n"
refs_marker = "## Fuentes nuevas V140 · consultas SICHE nombradas y SIGADE en Pagos"
if refs_marker not in source_refs:
    source_refs += "\n" + refs_marker + "\n\n"
    for item in SOURCES:
        source_refs += f"- `{item['id']}` · {item['title']} · {item['url']} · `{item['local']}` · `{item['sha256']}`\n"
source_refs_path.write_text(source_refs, encoding="utf-8")

(HERE / "README_V140.md").write_text("""# V140 · consultas SICHE nombradas y puente SIGADE-Pagos

V140 identifica por primera vez una consulta SICHE cuyo nombre coincide exactamente con las claves target: `Formulario por Pda. Presupuestaria y Sigade`. Para `7.2.8 + 83106000`, la consulta admite beneficiario y clasificador económico e incluye observaciones de la orden de pago. Se agregan tres controles preexistentes: `Gastos por Beneficiarios`, `Deuda Exigible hasta 2008` y `Consulta detallada de asientos 2001 a 2012` con Debe/Haber, cuenta, asiento anual y tipo.

El Newsletter e-SIDIF línea 33 prueba además que el atributo SIGADE aparece en EPP, PG, NPG, CMR-DP, TCE/RTCE y consultas/reportes del entorno Nación. Se usa como crosswalk posterior, no como prueba de migración 2008. El runbook queda listo, pero ninguna consulta fue ejecutada ni enviada. Resultado estricto: 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas; seis pedidos `DRAFT_NOT_SENT`.
""", encoding="utf-8")

(HERE / "VEREDICTO_V140.md").write_text("""# Veredicto V140

La brecha ya no es “qué buscar”, sino ejecutar cuatro consultas oficiales nombradas. `Formulario por Pda. Presupuestaria y Sigade` es el objeto principal porque combina los dos identificadores públicos exactos del renglón: partida `7.2.8` y SIGADE `83106000`. Beneficiario, clasificador económico y observaciones permiten clasificar la fila sin presuponer C-41 o C-55. Las consultas de beneficiarios, deuda exigible y asientos aportan controles independientes.

El atributo SIGADE en Pagos ofrece un puente hacia EPP/PG/NPG/CMR-DP/TCE-RTCE y permite pedir rechazo, anulación, transferencia o medio posterior. Pero es un esquema e-SIDIF de 2020: no acredita migración de SIDIF Central/SLU 2008. Tampoco un asiento prueba débito bancario, ni un cero en Deuda Exigible prueba pago.

No apareció una exportación target, cuerpo AMIDDF, pago, extracto o conciliación. El balance permanece en 10 adjudicaciones exactas, 9 cuentas candidatas y 0/10 ejecuciones confirmadas. Los seis pedidos continúan sin enviar.
""", encoding="utf-8")

(HERE / "E0_FISCAL_RECONSTRUCTION_V140.md").write_text("""# Reconstrucción fiscal E0 V140

V140 fija una secuencia verificable: formulario por partida/SIGADE; beneficiario y observaciones; estado de deuda exigible; asiento Debe/Haber; comprobantes de Pagos por SIGADE; conciliación; respaldo AMIDDF. Cada capa responde una pregunta distinta y ninguna sustituye a la siguiente. Hasta ejecutar el runbook y obtener filas target, el numerador permanece en 0/10 ejecuciones confirmadas.
""", encoding="utf-8")

(HERE / "AUDITORIA_V140.md").write_text(f"""# Auditoría V140

- Fuentes maestras: 434; cuatro fuentes oficiales nuevas.
- Fuentes primarias E0: 194; copias catalogadas SHA-válidas esperadas: 428.
- Consultas SICHE nombradas: {len(named_queries)} controles; runbook: {len(runbook)} pasos.
- Crosswalk SIGADE-Pagos: {len(payment_crosswalk)} filas; resultados cero: {len(zero_rules)} reglas.
- Control visual PDF: {len(pdf_visual)} páginas.
- Ledger fiscal: {len(ledger)} filas; cortes metodológicos: {len(breaks)}.
- Trazabilidad: {len(trace)} objetos; claves: {len(keys)}.
- Escalera: 10 adjudicaciones; 9 cuentas candidatas; 0 ejecuciones confirmadas.
- Pedidos: 6 borradores, 0 enviados; panel estricto {STRICT}% sin cambios.
""", encoding="utf-8")

(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V140_A_V141.md").write_text("""# Handover V140 → V141

## Estado

- QA V140: ejecutar y exigir PASS.
- Consulta principal exacta: `Formulario por Pda. Presupuestaria y Sigade` con SAF355/2008/7.2.8/83106000.
- Consultas de control: `Gastos por Beneficiarios`, `Deuda Exigible hasta 2008` y asientos 2001-2012.
- Campos probados: beneficiario, clasificador económico, observaciones OP, Debe/Haber, cuenta, asiento anual y tipo.
- Pagos: SIGADE está en EPP, PG, NPG, CMR-DP, TCE/RTCE y reportes e-SIDIF 2020; migración 2008 abierta.
- Doble prioridad documental/mecánica V139 permanece; ninguna fila target recuperada.
- Seis pedidos `DRAFT_NOT_SENT`; 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas.

## Prioridad V141

1. Mantener los seis pedidos como borradores salvo autorización expresa.
2. Si se autoriza, presentar Economía/RAIP con los nombres exactos de consulta y el runbook V140.
3. Exigir exportación sin beneficiario primero; luego filtros y observaciones.
4. Exigir definición/corte de Deuda Exigible y diccionario de todos los datasets.
5. Cruzar toda fila con Pagos por SIGADE, Conciliación Bancaria y AMIDDF.
6. Mantener cero de consulta separado de ausencia, pago, anulación o expurgo.
""", encoding="utf-8")


# Auditoría de preservación y estado acumulado.
for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    source_path = AUDIT / f"{stem}_V139.csv"
    target_path = AUDIT / f"{stem}_V140.csv"
    target_path.write_text(
        source_path.read_text(encoding="utf-8-sig").replace("V139", "V140").replace("v139", "v140"),
        encoding="utf-8",
    )

hash_rows = []
for row in catalog:
    local = row["archivo_local"]
    path = REPO / local.lstrip("/") if local else None
    exists = bool(path and path.is_file())
    actual = sha256(path) if exists else ""
    expected = row["sha256"]
    hash_rows.append({
        "id": row["id"], "archivo_local": local, "exists": str(exists),
        "sha_catalog": expected, "sha_actual": actual,
        "hash_ok": str(bool(exists and expected and actual.lower() == expected.lower())),
    })
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V140.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V140.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
assert physical == hash_ok == 428

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or "tmp" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({
        "path": path.relative_to(REPO).as_posix(), "bytes": str(size),
        "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576),
        "over_100_mib": str(size > 100 * 1048576),
    })
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V140.csv", size_rows)

completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V139.json").read_text(encoding="utf-8"))
for key in list(completeness):
    if key.endswith("_v139") or "newly_preserved_v139" in key or "duplicate_recaptures_v139" in key:
        completeness.pop(key, None)
completeness.update({
    "checkpoint": "V140", "date": "2026-08-30",
    "state": "E0_EXACT_SICHE_NAMED_QUERY_PROVED_PAYMENT_SIGADE_CROSSWALK_TARGET_RUN_NOT_EXECUTED_NOT_SENT",
    "numeric_v140_strict_changed": False,
    "master_catalog_entries": len(catalog), "physical_local_copies": physical,
    "physical_local_hash_ok": hash_ok, "binary_required_entries": 365,
    "binary_required_preserved": 364, "binary_required_source_complete": False,
    "remaining_physical_gaps": 1,
    "e0_primary_sources_preserved": len(census),
    "e0_quality": "PRIMARY_EXACT_SICHE_NAMED_QUERIES_AND_PAYMENT_SIGADE_CROSSWALK",
    "sources_newly_preserved_v140": 4, "e0_primary_sources_newly_preserved_v140": 4,
    "e0_duplicate_recaptures_v140": 0,
    "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
    "e0_request_traceability_rows": len(trace), "e0_request_search_keys": len(keys),
    "e0_siche_named_query_target_rows": len(named_queries),
    "e0_payment_sigade_crosswalk_rows": len(payment_crosswalk),
    "e0_exact_siche_query_runbook_rows": len(runbook),
    "e0_query_zero_result_rules": len(zero_rules),
    "e0_pdf_visual_controls": len(pdf_visual),
    "e0_siche_query_plan_rows": len(query_plan),
    "e0_sidif_candidate_types": 4, "e0_sidif_target_document_types_located": 0,
    "e0_c41_document_comparator_priority": True,
    "e0_c55_mechanism_comparator_priority": True,
    "e0_document_type_hypothesis_status": "DUAL_PRIORITY_NO_TARGET_PROOF",
    "e0_c55_target_rows_located": 0, "e0_siche_target_exports_located": 0,
    "e0_siche_named_queries_executed": 0,
    "e0_settlement_award_rows_exact": 10, "e0_settlement_account_candidate_rows": 9,
    "e0_settlement_executed_rows_confirmed": 0, "e0_requests_submitted": 0,
    "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
    "historical_workstream": "Exact SICHE named query for Pda+SIGADE and three named controls proved; payment SIGADE crosswalk and current expediente→OP→payment link documented; target export, 2008 migration, AMIDDF body, reconciliation, CRYL and executed settlement remain open; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V140.json").write_text(
    json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
backup_text = backup.read_text(encoding="utf-8-sig")
backup_marker = "## V140 · consultas SICHE nombradas y puente SIGADE-Pagos"
if backup_marker not in backup_text:
    backup_text += f"""

{backup_marker}

- Consulta exacta identificada: `Formulario por Pda. Presupuestaria y Sigade`, aplicable a 7.2.8/83106000.
- Controles nombrados: Gastos por Beneficiarios, Deuda Exigible hasta 2008 y asientos detallados 2001-2012.
- e-SIDIF línea 33 prueba SIGADE en EPP, PG, NPG, CMR-DP, TCE/RTCE y reportes; migración 2008 no probada.
- Runbook y estándar de resultados cero listos, pero ninguna consulta fue ejecutada.
- 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas; seis borradores no enviados.
"""
backup.write_text(backup_text, encoding="utf-8")

inherited = [
    {"script": "qa_v139.py", "pre_v140_result": "PASS", "post_v140_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V139 queda supersedida por consultas SICHE nombradas, crosswalk de Pagos y runbook V140."},
    {"script": "qa_v140.py", "pre_v140_result": "N/A", "post_v140_result": "PASS", "interpretation": "Fuentes, hashes, consultas, límites de inferencia, trazabilidad y no envío verificados."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V140.csv", inherited)

qa = r'''from pathlib import Path
import csv
import hashlib
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
AUDIT = REPO / "research" / "ciclo_ajuste" / "source_audit"

def rows(name):
    with (HERE / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

named = rows("E0_SICHE_NAMED_QUERY_TARGET_MAP_V140.csv")
crosswalk = rows("E0_SIGADE_PAYMENT_ATTRIBUTE_CROSSWALK_V140.csv")
runbook = rows("E0_EXACT_SICHE_QUERY_RUNBOOK_V140.csv")
zero = rows("E0_QUERY_ZERO_RESULT_INTERPRETATION_V140.csv")
visual = rows("E0_V140_PDF_VISUAL_CONTROL.csv")
plan = rows("E0_SICHE_TARGET_QUERY_PLAN_V140.csv")
assert len(named) == 10
assert named[0]["query_name"] == "Formulario por Pda. Presupuestaria y Sigade"
assert named[0]["target_input"] == "7.2.8;83106000;ejercicio2008;SAF355"
assert all("NOT_RUN" in r["status"] or r["status"].endswith("TARGET_ROWS_OPEN") for r in named)
assert len(crosswalk) == 10
assert {"EPP", "PG", "NPG", "CMR-DP", "TCE/RTCE"} <= {r["record"] for r in crosswalk}
assert all("LEGACY" in r["status"] or "NOT_TARGET_ROUTE" in r["status"] for r in crosswalk)
assert len(runbook) == 12 and all(r["status"] == "DRAFT_NOT_SENT" for r in runbook)
assert len(zero) == 8 and all(r["status"] == "FROZEN" for r in zero)
assert all("pag" in r["zero_forbids"].casefold() or r["rule_id"] not in {"ZR140_01", "ZR140_03", "ZR140_05"} for r in zero)
assert len(visual) == 2 and all(r["result"] == "PASS" for r in visual)
assert len(plan) == 10 and all(r["status"] == "DRAFT_NOT_SENT" for r in plan)

assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V140.csv")) == 218
assert len(rows("E0_FISCAL_METHOD_BREAKS_V140.csv")) == 171
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V140.csv")) == 164
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V140.csv")) == 182

ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V140.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)
register = rows("E0_REQUEST_RESPONSE_REGISTER_V140.csv")
assert len(register) == 6 and all(r["status"] == "DRAFT_NOT_SENT" for r in register)
assert all(r["submitted_on"] == "N/A" and r["submission_channel"] == "N/A" and r["receipt_or_case_id"] == "N/A" for r in register)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V140.csv")}
new_ids = ''' + repr(source_ids) + r'''
assert len(census) == 194 and new_ids <= set(census)
for row in census.values():
    local = row["local_path"]
    assert local and (REPO / local.lstrip("/")).is_file(), (row["source_id"], local)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 434 and len({r["id"] for r in catalog}) == 434

expected = ''' + repr(EXPECTED) + r'''
bin_dir = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v140" / "binaries"
assert len(list(bin_dir.iterdir())) == 4
for name, (size, digest) in expected.items():
    path = bin_dir / name
    assert path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest() == digest

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V140.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V140"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 428
assert complete["binary_required_entries"] == 365 and complete["binary_required_preserved"] == 364
assert complete["e0_siche_named_query_target_rows"] == 10
assert complete["e0_payment_sigade_crosswalk_rows"] == 10
assert complete["e0_exact_siche_query_runbook_rows"] == 12
assert complete["e0_siche_named_queries_executed"] == 0
assert complete["e0_sidif_target_document_types_located"] == 0
assert complete["e0_siche_target_exports_located"] == 0
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v140_strict_changed"] is False

request = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V140.md").read_text(encoding="utf-8-sig")
assert "## Clave V140 · consultas SICHE nombradas y runbook exacto" in request
assert "Formulario por Pda. Presupuestaria y Sigade" in request
assert "BORRADOR_NO_ENVIADO" in request and "resultado cero" in request
refs = (HERE / "SOURCE_REFERENCES_V140.md").read_text(encoding="utf-8-sig")
assert refs.count("## Fuentes nuevas V140 · consultas SICHE nombradas y SIGADE en Pagos") == 1
combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv")) + "\n" + request
assert "QUERY_EXECUTED_TARGET_FOUND" not in combined
assert "REQUEST_SENT" not in combined
for name in ("README_V140.md", "VEREDICTO_V140.md", "E0_FISCAL_RECONSTRUCTION_V140.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V140_A_V141.md"):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "0/10" in text
assert "ninguna consulta fue ejecutada" in (HERE / "README_V140.md").read_text(encoding="utf-8-sig")

print("V140 QA PASS")
'''
(HERE / "qa_v140.py").write_text(qa, encoding="utf-8")


def checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V140.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V140", "parent_checkpoint": "V139",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": 4, "duplicate_recaptures": 0,
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks),
        "siche_named_query_rows": len(named_queries), "payment_sigade_crosswalk_rows": len(payment_crosswalk),
        "exact_query_runbook_rows": len(runbook), "zero_result_rules": len(zero_rules),
        "sidif_candidate_types": 4, "sidif_target_document_types_located": 0,
        "hypothesis_status": "DUAL_PRIORITY_NO_TARGET_PROOF", "siche_target_exports_located": 0,
        "siche_named_queries_executed": 0,
        "award_rows_exact": 10, "account_candidate_rows": 9, "executed_settlement_rows_confirmed": 0,
        "request_drafts": 6, "request_traceability_rows": len(trace), "request_search_keys": len(keys),
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V140.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


checkpoint_manifest()


def build_tree(root: Path) -> str:
    lines = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix().casefold()):
        if ".git" in path.parts or "__pycache__" in path.parts or "tmp" in path.parts:
            continue
        lines.append(path.relative_to(root).as_posix() + ("/" if path.is_dir() else ""))
    return "\n".join(lines) + "\n"


(REPO / "TREE.txt").write_text(build_tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(build_tree(CYCLE), encoding="utf-8")

global_manifest_path = CYCLE / "MANIFEST_SHA256.json"
global_files = []
for path in sorted(REPO.rglob("*"), key=lambda item: item.relative_to(REPO).as_posix().casefold()):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or "tmp" in path.parts or path == global_manifest_path:
        continue
    global_files.append({"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})
global_manifest = {
    "checkpoint": "V140",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical catalog copies SHA-valid; 4 new official sources; exact named Pda+SIGADE query proved but not run; payment SIGADE crosswalk proved with legacy migration open; zero of ten executed settlement rows confirmed; six requests drafted and none submitted.",
    "historical_workstream": "Run exact SICHE Pda+SIGADE query and named controls if authorized; obtain exports, query metadata, Pagos crosswalk, Conciliacion Bancaria and AMIDDF; keep zero distinct from payment, absence or destruction; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V140 BUILD PASS")
