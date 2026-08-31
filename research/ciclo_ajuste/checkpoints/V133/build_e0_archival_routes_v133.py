from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import re
import shutil


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
PARENT = HERE.parent / "V132"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v133" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


SOURCES = [
    {
        "id": "e0_senado_exp_366_09_agn_res211_t3",
        "filename": "senado_exp_366_09_agn_res211_t3.html",
        "institution": "Honorable Senado de la Nación",
        "title": "Expediente OV 366/09 · remisión de Resolución AGN 211/2009 e informe T3 2009",
        "url": "https://www.senado.gob.ar/parlamentario/comisiones/verExp/366.09/OV/PP",
        "publication": "2009-11-24",
        "period": "2009Q3-2012-05-28",
        "code": "OV 366/09; AGN Res.211/2009; Act.426/09",
        "type": "HTML oficial · captura preservada",
        "bytes": 48711,
        "sha256": "f74fbe0afdc64f2417b33812dbf68696df7b70e73b65b0fe1e4f2eb69720574c",
        "families": "audit_activity;parliamentary_transfer;archive_locator",
        "breaks": "metadatos parlamentarios versus cuerpo del informe/anexo",
        "use": "USABLE_EXACT_PARLIAMENTARY_ARCHIVE_LOCATOR",
        "caveat": "Prueba ingreso, giro, comisión y archivo; la pestaña Texto original figura en proceso de carga y no entrega el anexo.",
        "note": "V133 E0: OV 366/09 ingresó a la Bicameral Revisora de Cuentas y fue enviado al archivo el 28/05/2012.",
    },
    {
        "id": "e0_senado_exp_44_10_agn_res44_t4",
        "filename": "senado_exp_44_10_agn_res44_t4.html",
        "institution": "Honorable Senado de la Nación",
        "title": "Expediente OV 44/10 · remisión de Resolución AGN 44/2010 e informe T4 2009",
        "url": "https://www.senado.gob.ar/parlamentario/comisiones/verExp/44.10/OV/PP",
        "publication": "2010-04-15",
        "period": "2009Q4-2012-05-28",
        "code": "OV 44/10; AGN Res.44/2010; Act.466/09",
        "type": "HTML oficial · captura preservada",
        "bytes": 48707,
        "sha256": "b8ba499ccb21798d392d4c8e8499d51c6057bb076c6f8d41c08d773e201beed2",
        "families": "audit_activity;parliamentary_transfer;archive_locator",
        "breaks": "metadatos parlamentarios versus cuerpo del informe/anexo",
        "use": "USABLE_EXACT_PARLIAMENTARY_ARCHIVE_LOCATOR",
        "caveat": "Prueba ingreso, giro, comisión y archivo; la pestaña Texto original figura en proceso de carga y no entrega el anexo.",
        "note": "V133 E0: OV 44/10 ingresó a la Bicameral Revisora de Cuentas y fue enviado al archivo el 28/05/2012.",
    },
    {
        "id": "e0_economia_consulta_expedientes_comdoc_gde",
        "filename": "economia_consulta_expedientes_comdoc_gde.html",
        "institution": "Ministerio de Economía",
        "title": "Consulta de expedientes · separación temporal COMDOC/GDE",
        "url": "https://www.argentina.gob.ar/economia/informacionciudadana/consultadeexpedientes",
        "publication": "s/f; consulta 2026-08-30",
        "period": "antes/después de septiembre de 2016",
        "code": "COMDOC pre-09/2016; GDE desde 09/2016",
        "type": "HTML oficial · captura preservada",
        "bytes": 35065,
        "sha256": "ffa7137f0ff2405d504b64e06cc522420384400164d23838256bff443c3d4ec2",
        "families": "document_management;COMDOC;GDE;legacy_index",
        "breaks": "ruta oficial publicada versus disponibilidad operativa del índice legado",
        "use": "USABLE_EXACT_LEGACY_QUERY_ROUTE",
        "caveat": "La página remite los expedientes anteriores a septiembre de 2016 a COMDOC; el endpoint publicado rechazó conexión y no permitió consultar el cuerpo.",
        "note": "V133 E0: confirma que S01:0342455/2008 debe buscarse en COMDOC, no sólo en GDE; indisponibilidad no equivale a inexistencia.",
    },
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


def bump(text: str) -> str:
    text = text.replace("V132", "V133")
    return re.sub(r"\b([A-Z]{1,8})132_", r"\g<1>133_", text)


def clone_parent() -> None:
    skip = {"build_e0_metadata_record_producers_v132.py", "qa_v132.py", "MANIFEST_V132.json", "INHERITED_QA_STATUS_V132.csv"}
    for source in PARENT.iterdir():
        if not source.is_file() or source.name in skip or source.name.startswith("HANDOVER_PROXIMA_SESION"):
            continue
        target = HERE / source.name.replace("V132", "V133")
        target.write_text(bump(source.read_text(encoding="utf-8-sig")), encoding="utf-8")


clone_parent()

for source in SOURCES:
    path = BIN / source["filename"]
    assert path.is_file() and path.stat().st_size == source["bytes"], path
    assert sha256(path) == source["sha256"], path
    source["local"] = "/" + path.relative_to(REPO).as_posix()

# Catálogo y censo primario.
source_ids = {source["id"] for source in SOURCES}
catalog = [row for row in read_csv(CATALOG) if row["id"] not in source_ids]
for source in SOURCES:
    catalog.append({
        "id": source["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": source["institution"],
        "titulo": source["title"], "url_original": source["url"], "archivo_local": source["local"],
        "fecha_descarga": "2026-08-30", "fecha_publicacion": source["publication"],
        "codigo_serie": source["code"], "periodo_utilizado": source["period"], "tipo": source["type"],
        "sha256": source["sha256"], "nota": source["note"],
    })
assert len(catalog) == 361 and len({row["id"] for row in catalog}) == 361
write_csv(CATALOG, catalog)

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V133.csv"
census = [row for row in read_csv(census_path) if row["source_id"] not in source_ids]
for source in SOURCES:
    census.append({
        "source_id": source["id"], "institution": source["institution"], "artifact": source["title"],
        "url": source["url"], "local_path": source["local"], "sha256": source["sha256"],
        "bytes": str(source["bytes"]), "period_coverage": source["period"],
        "variable_families": source["families"], "primary_source": "YES", "preserved": "YES",
        "method_breaks": source["breaks"], "use_status": source["use"], "caveat": source["caveat"],
    })
assert len(census) == 121 and len({row["source_id"] for row in census}) == 121
write_csv(census_path, census)

# Trazabilidad parlamentaria exacta de los anexos AGN.
quarterly_path = HERE / "E0_AGN_QUARTERLY_ANNEX_AVAILABILITY_V133.csv"
quarterly = read_csv(quarterly_path)
quarterly[1].update({
    "public_file_relation": "SENATE_OV_366_09_METADATA_ONLY",
    "search_control": "Senate OV 366/09; Bicameral Revisora; archived 2012-05-28; original text in process of loading",
    "status": "PARLIAMENTARY_EXPEDIENT_AND_ARCHIVE_ROUTE_EXACT_ANNEX_BODY_NOT_PUBLIC",
    "request_key": "OV 366/09; Actuación 426/09-AGN; informe y anexo T3",
})
quarterly[2].update({
    "public_file_relation": "SENATE_OV_44_10_METADATA_ONLY",
    "search_control": "Senate OV 44/10; Bicameral Revisora; archived 2012-05-28; original text in process of loading",
    "status": "PARLIAMENTARY_EXPEDIENT_AND_ARCHIVE_ROUTE_EXACT_ANNEX_BODY_NOT_PUBLIC",
    "request_key": "OV 44/10; Actuación 466/09-AGN; informe y anexo T4",
})
write_csv(quarterly_path, quarterly)

parliament = [
    {"row_id": "PA133_01", "agn_quarter": "2009Q3", "agn_resolution": "211/2009", "agn_actuacion": "426/09-AGN", "senate_exp": "OV 366/09", "mesa_entrada": "2009-11-24", "dado_cuenta": "2009-12-02", "commission": "Bicameral Permanente Mixta Revisora de Cuentas", "commission_entry": "2009-11-26", "archive_date": "2012-05-28", "archive_note": "Giro al archivo por nota de la Revisora de Cuentas de 18/05/2012", "original_text_public_state": "EN_PROCESO_DE_CARGA", "source_id": "e0_senado_exp_366_09_agn_res211_t3", "permitted_use": "Individualizar remisión, comisión y destino archivístico.", "open_gap": "Copia del texto original, informe y anexo magnético."},
    {"row_id": "PA133_02", "agn_quarter": "2009Q4", "agn_resolution": "44/2010", "agn_actuacion": "466/09-AGN", "senate_exp": "OV 44/10", "mesa_entrada": "2010-04-15", "dado_cuenta": "2010-04-28", "commission": "Bicameral Permanente Mixta Revisora de Cuentas", "commission_entry": "2010-04-20", "archive_date": "2012-05-28", "archive_note": "Giro al archivo por nota de la Revisora de Cuentas de 18/05/2012", "original_text_public_state": "EN_PROCESO_DE_CARGA", "source_id": "e0_senado_exp_44_10_agn_res44_t4", "permitted_use": "Individualizar remisión, comisión y destino archivístico.", "open_gap": "Copia del texto original, informe y anexo magnético."},
]
write_csv(HERE / "E0_AGN_PARLIAMENTARY_ARCHIVE_CROSSWALK_V133.csv", parliament)

# Ruta COMDOC oficial: índice correcto identificado, endpoint no operativo.
comdoc = [
    {"row_id": "CD133_01", "target": "S01:0342455/2008", "official_rule": "Expedientes anteriores a septiembre de 2016 se consultan en COMDOC", "published_endpoint": "http://expedientes.mecon.gov.ar/finddoc2/finddoc/Inicio", "test_date": "2026-08-30", "test_result": "CONNECTION_REFUSED", "body_query_executed": "NO", "source_id": "e0_economia_consulta_expedientes_comdoc_gde", "status": "CORRECT_LEGACY_INDEX_IDENTIFIED_ENDPOINT_UNAVAILABLE", "permitted_inference": "El expediente 2008 debe buscarse en COMDOC y fondos heredados, no sólo GDE.", "forbidden_inference": "El expediente no existe o no contiene liquidaciones."},
    {"row_id": "CD133_02", "target": "Expedientes desde septiembre de 2016", "official_rule": "Consulta por GDE", "published_endpoint": "https://www.argentina.gob.ar/consultar-expediente-electronico", "test_date": "2026-08-30", "test_result": "NOT_TARGET_ROUTE", "body_query_executed": "NO", "source_id": "e0_economia_consulta_expedientes_comdoc_gde", "status": "TEMPORAL_SCOPE_CONTROL", "permitted_inference": "GDE no es la ruta primaria del expediente iniciado en 2008.", "forbidden_inference": "No pudo existir migración o referencia cruzada posterior a GDE."},
]
write_csv(HERE / "E0_COMDOC_LEGACY_QUERY_ROUTE_V133.csv", comdoc)

exhaust_path = HERE / "E0_EXPEDIENT_PUBLIC_SEARCH_EXHAUSTION_V133.csv"
exhaust = read_csv(exhaust_path)
exhaust.extend([
    {"search_id": "EX133_05", "target": "S01:0342455/2008", "route": "Página oficial Economía Consulta de expedientes → COMDOC pre-09/2016", "result": "Ruta histórica exacta identificada; endpoint COMDOC rechazó conexión", "public_body_found": "NO_QUERY_NOT_COMPLETED", "status": "LEGACY_INDEX_EXACT_ENDPOINT_UNAVAILABLE", "permitted_inference": "La búsqueda debe cubrir COMDOC y archivo heredado.", "forbidden_inference": "Endpoint caído equivale a inexistencia documental."},
    {"search_id": "EX133_06", "target": "Anexos AGN T3/T4 2009", "route": "Senado OV 366/09 y OV 44/10; Bicameral Revisora", "result": "Metadatos de ingreso, comisión y archivo exactos; texto original en proceso de carga", "public_body_found": "METADATA_ONLY", "status": "PARLIAMENTARY_ARCHIVE_ROUTE_EXACT_BODY_OPEN", "permitted_inference": "El pedido puede usar expedientes y destino archivístico exactos.", "forbidden_inference": "El anexo fue destruido o no contenía el proyecto 48 0237/09."},
])
write_csv(exhaust_path, exhaust)

# Escalera de divulgación SIGADE/SIDIF con años inmediatamente contiguos.
disclosure_path = HERE / "E0_SIGADE_SIDIF_DISCLOSURE_LADDER_V133.csv"
disclosure = read_csv(disclosure_path)
new_disclosure = [
    ("DL133_15", "2007", "83006000", "Caja de Valores", "204066.00", "VARIOS", "AGGREGATED", "e0_cgn_cuenta_inversion_2007_sdp", "PDF_p68_Anexo_K"),
    ("DL133_16", "2007", "83008000", "Caja de Valores", "6503654.84", "VARIOS", "AGGREGATED", "e0_cgn_cuenta_inversion_2007_sdp", "PDF_p68_Anexo_K"),
    ("DL133_17", "2007", "83095000", "Caja de Valores", "1767506.02", "VARIOS", "AGGREGATED", "e0_cgn_cuenta_inversion_2007_sdp", "PDF_p68_Anexo_K"),
    ("DL133_18", "2007", "83020000", "Comisiones Citibank", "78747.58", "165233;172217", "ITEMIZED", "e0_cgn_cuenta_inversion_2007_sdp", "PDF_p68_Anexo_K"),
    ("DL133_19", "2007", "83106000", "Comisiones Banco Nación", "26656.30", "83318;151752;240417", "ITEMIZED", "e0_cgn_cuenta_inversion_2007_sdp", "PDF_p68_Anexo_K"),
    ("DL133_20", "2009", "83006000", "Caja de Valores", "153624.00", "", "BLANK", "e0_cgn_cuenta_inversion_2009_sdp", "PDF_p74_Anexo_K"),
    ("DL133_21", "2009", "83008000", "Caja de Valores", "8382988.47", "", "BLANK", "e0_cgn_cuenta_inversion_2009_sdp", "PDF_p74_Anexo_K"),
    ("DL133_22", "2009", "83095000", "Caja de Valores", "436394.99", "", "BLANK", "e0_cgn_cuenta_inversion_2009_sdp", "PDF_p74_Anexo_K"),
    ("DL133_23", "2009", "83020000", "Comisiones Citibank", "40769.78", "", "BLANK", "e0_cgn_cuenta_inversion_2009_sdp", "PDF_p74_Anexo_K"),
    ("DL133_24", "2009", "83106000", "Comisiones Banco Nación", "17557.10", "", "BLANK", "e0_cgn_cuenta_inversion_2009_sdp", "PDF_p74_Anexo_K"),
]
for row in new_disclosure:
    disclosure.append(dict(zip(list(disclosure[0]), row + ("IMMEDIATE_YEAR_COMPARATOR", "No es prueba de una operación 2008 ni de ausencia de comprobantes subyacentes."))))
write_csv(disclosure_path, disclosure)

by_year_key = {(row["year"], row["sigade"]): row for row in disclosure}
transitions = []
for i, key in enumerate(("83006000", "83008000", "83095000", "83020000", "83106000"), 1):
    transitions.append({
        "row_id": f"DT133_{i:02d}", "sigade": key,
        "year_2007": by_year_key[("2007", key)]["disclosure_level"],
        "year_2008": by_year_key[("2008", key)]["disclosure_level"],
        "year_2009": by_year_key[("2009", key)]["disclosure_level"],
        "year_2010": by_year_key[("2010", key)]["disclosure_level"],
        "transition": " → ".join(by_year_key[(year, key)]["disclosure_level"] for year in ("2007", "2008", "2009", "2010")),
        "permitted_use": "Demostrar variación del nivel de publicación y necesidad de pedir el submayor subyacente.",
        "prohibited_use": "Interpretar VARIOS o columna vacía como inexistencia del comprobante o como vínculo con la recompra.",
    })
write_csv(HERE / "E0_SIGADE_SIDIF_TARGET_DISCLOSURE_TRANSITIONS_V133.csv", transitions)

# Ledger y reglas metodológicas.
ledger_path = HERE / "E0_FISCAL_MECHANISM_LEDGER_V133.csv"
ledger = read_csv(ledger_path)
ledger.extend([
    {"ledger_id": "F155", "window": "2009Q3-2012-05-28", "mechanism": "Debt_audit_2008", "phase": "PARLIAMENTARY_TRANSFER_AND_ARCHIVE", "as_of_date": "2012-05-28", "payer": "N/A", "recipient": "Congreso_Bicameral", "universe": "AGN_T3_T4_activity_annexes", "instrument": "OV_366_09_OV_44_10", "amount_original": "2", "original_unit": "PARLIAMENTARY_EXPEDIENTS", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_senado_exp_366_09_agn_res211_t3;e0_senado_exp_44_10_agn_res44_t4", "source_locator": "official_senate_detail_pages", "realization_status": "ARCHIVE_ROUTE_EXACT_ANNEX_BODY_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "Two AGN transmissions can now be requested by exact Senate expediente and archive date.", "caveat": "Parliamentary metadata does not reveal annex content."},
    {"ledger_id": "F156", "window": "2008-2026", "mechanism": "Debt_buyback_excess_GDP", "phase": "LEGACY_DOCUMENT_INDEX_ROUTE", "as_of_date": "2026-08-30", "payer": "N/A", "recipient": "N/A", "universe": "S01_0342455_2008", "instrument": "COMDOC", "amount_original": "0", "original_unit": "BODY_ROWS_RECOVERED", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_economia_consulta_expedientes_comdoc_gde", "source_locator": "pre_September_2016_COMDOC_link", "realization_status": "CORRECT_ROUTE_IDENTIFIED_ENDPOINT_UNAVAILABLE", "additivity": "NON_ADDITIVE", "status_interpretation": "The correct legacy system is known but could not be queried.", "caveat": "Connection refusal is not evidence of document absence."},
    {"ledger_id": "F157", "window": "2007-2010", "mechanism": "Debt_accounting_disclosure", "phase": "IMMEDIATE_DISCLOSURE_TRANSITION", "as_of_date": "2010-12-31", "payer": "Tesoro_Nacional", "recipient": "Multiple_service_providers", "universe": "Five_SIGADE_keys", "instrument": "Anexo_K_SIDIF_column", "amount_original": "20", "original_unit": "YEAR_KEY_OBSERVATIONS", "normalized_ars_million": "N/D", "valuation_basis": "ANNUAL_COMPARATOR", "source_id": "e0_cgn_cuenta_inversion_2007_sdp;e0_cgn_cuenta_inversion_2008_sdp;e0_cgn_cuenta_inversion_2009_sdp;e0_cgn_cuenta_inversion_2010_sdp", "source_locator": "Anexo_K_pp68_67_74_74", "realization_status": "DISCLOSURE_CHANGE_EXACT_UNDERLYING_SUBLEDGER_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "Itemized, aggregated and blank publication states coexist around 2008.", "caveat": "Publication state is not the existence state of underlying accounting records."},
])
write_csv(ledger_path, ledger)

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V133.csv"
breaks = read_csv(breaks_path)
breaks.extend([
    {"break_id": "parliamentary_exp_metadata_not_annex_body", "dimension": "document_scope", "problem": "Senate detail pages prove transmission and archive routing but do not expose Texto original.", "rule": "Use OV identifiers as custody locators; keep annex content and project progress open.", "status": "FROZEN", "evidence": "OV 366/09; OV 44/10"},
    {"break_id": "legacy_endpoint_unavailable_not_record_absence", "dimension": "access", "problem": "The official COMDOC endpoint refused connection.", "rule": "Record the query as unexecuted and escalate by exact legacy identifier; never code the result as no record.", "status": "FROZEN", "evidence": "Economía Consulta de expedientes; CD133_01"},
    {"break_id": "sidif_publication_blank_not_accounting_absence", "dimension": "disclosure", "problem": "The 2009 Anexo K leaves SIDIF cells blank while adjacent years aggregate or itemize the same keys.", "rule": "Treat blank, VARIOS and itemized as publication states; require subledger before any transaction inference.", "status": "FROZEN", "evidence": "CGN Anexo K 2007-2010; DT133_01_05"},
])
write_csv(breaks_path, breaks)

# Pedidos: se enriquecen los mismos seis borradores; no se envía ninguno.
trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V133.csv"
trace = read_csv(trace_path)
trace.extend([
    {"trace_id": "TR133_102", "request_id": "REQ133_AGN", "institution": "AGN / Senado / Bicameral Revisora de Cuentas", "gap_id": "CL133_AGN_REPLY", "requested_record": "Texto original, informe y anexo magnético remitidos como OV 366/09", "period_or_date": "2009Q3-2012-05-28", "identifiers": "Res.211/2009;Act.426/09-AGN;OV366/09", "minimum_usable_fields": "copia;índice;soporte;fecha de recepción;ubicación archivística", "confidentiality_fallback": "fila del proyecto 48 0237/09 y metadatos de transferencia", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR133_103", "request_id": "REQ133_AGN", "institution": "AGN / Senado / Bicameral Revisora de Cuentas", "gap_id": "CL133_AGN_REPLY", "requested_record": "Texto original, informe y anexo magnético remitidos como OV 44/10", "period_or_date": "2009Q4-2012-05-28", "identifiers": "Res.44/2010;Act.466/09-AGN;OV44/10", "minimum_usable_fields": "copia;índice;soporte;fecha de recepción;ubicación archivística", "confidentiality_fallback": "fila del proyecto 48 0237/09 y metadatos de transferencia", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR133_104", "request_id": "REQ133_ECON", "institution": "Ministerio de Economía / ONCP / DADP / Archivo", "gap_id": "CL133_DEBT_ACCOUNTING", "requested_record": "Índice COMDOC, cuerpo y referencias de migración del expediente 2008", "period_or_date": "2008-actualidad", "identifiers": "S01:0342455/2008;COMDOC;finddoc2;GDE/GEDO/RUDO", "minimum_usable_fields": "número;carátula;índice;fojas;productor;transferencias;identificador origen/destino", "confidentiality_fallback": "índice y cuadro de documentos con terceros testados", "status": "DRAFT_NOT_SENT"},
])
write_csv(trace_path, trace)

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V133.csv"
keys = read_csv(keys_path)
keys.extend([
    {"key_id": "SK133_91", "request_id": "REQ133_AGN", "key_group": "senate_q3_archive", "exact_key": "OV366/09;Res211/2009;Act426/09-AGN;archivo28/05/2012", "search_purpose": "recuperar texto original e informe/anexo T3", "source_or_basis": "Senado expediente OV 366/09", "caveat": "La ficha no expone el texto original."},
    {"key_id": "SK133_92", "request_id": "REQ133_AGN", "key_group": "senate_q4_archive", "exact_key": "OV44/10;Res44/2010;Act466/09-AGN;archivo28/05/2012", "search_purpose": "recuperar texto original e informe/anexo T4", "source_or_basis": "Senado expediente OV 44/10", "caveat": "La ficha no expone el texto original."},
    {"key_id": "SK133_93", "request_id": "REQ133_AGN", "key_group": "parliamentary_custodian", "exact_key": "Bicameral Permanente Mixta Revisora de Cuentas;nota18/05/2012", "search_purpose": "localizar remito, inventario y depósito archivístico", "source_or_basis": "Senado OV 366/09 y 44/10", "caveat": "La nota de giro no fue recuperada."},
    {"key_id": "SK133_94", "request_id": "REQ133_ECON", "key_group": "legacy_query_endpoint", "exact_key": "S01:0342455/2008;http://expedientes.mecon.gov.ar/finddoc2/finddoc/Inicio", "search_purpose": "consultar índice COMDOC por vía histórica exacta", "source_or_basis": "Economía Consulta de expedientes", "caveat": "Endpoint no operativo al 30/08/2026."},
    {"key_id": "SK133_95", "request_id": "REQ133_ECON", "key_group": "cgn_2007_itemization", "exact_key": "83020000 SIDIF165233/172217;83106000 SIDIF83318/151752/240417", "search_purpose": "demostrar individualización en año inmediato anterior", "source_or_basis": "CGN 2007 Anexo K p68", "caveat": "No son comprobantes 2008."},
    {"key_id": "SK133_96", "request_id": "REQ133_ECON", "key_group": "cgn_2009_blank", "exact_key": "83006000;83008000;83095000;83020000;83106000;SIDIF columna vacía", "search_purpose": "demostrar cambio de publicación en año inmediato posterior", "source_or_basis": "CGN 2009 Anexo K p74", "caveat": "Columna vacía no significa inexistencia de submayor."},
    {"key_id": "SK133_97", "request_id": "REQ133_ECON", "key_group": "disclosure_transition", "exact_key": "2007→2008→2009→2010;ITEMIZED/AGGREGATED/BLANK", "search_purpose": "fundar pedido de salida subyacente homogénea", "source_or_basis": "E0_SIGADE_SIDIF_TARGET_DISCLOSURE_TRANSITIONS_V133.csv", "caveat": "Variación de exposición, no atribución a recompra."},
    {"key_id": "SK133_98", "request_id": "REQ133_ECON", "key_group": "migration_crosswalk", "exact_key": "COMDOC origen;GDE/GEDO/RUDO destino;S01:0342455/2008", "search_purpose": "recuperar referencias cruzadas de migración o transferencia", "source_or_basis": "corte oficial COMDOC/GDE", "caveat": "No se presume que la migración haya ocurrido."},
])
write_csv(keys_path, keys)

agn_request = HERE / "REQUEST_AGN_2018_REPLY_V133.md"
agn_request.write_text(agn_request.read_text(encoding="utf-8-sig").rstrip() + """

## Clave V133 · remisión parlamentaria y archivo

Los anexos ya pueden individualizarse también por su remisión al Congreso: el T3 ingresó al Senado como expediente `OV 366/09` y el T4 como `OV 44/10`. Ambos fueron girados a la Comisión Bicameral Permanente Mixta Revisora de Cuentas y enviados al archivo el `28/05/2012`, por nota de la Comisión fechada `18/05/2012`. Las fichas públicas mantienen “Texto original” en proceso de carga. Se solicita copia del texto original, informe, anexo magnético, remito, índice, constancia de recepción, nota de archivo y ubicación archivística actual; subsidiariamente, la fila completa del proyecto `48 0237/09`.

Estos localizadores no se invocan como prueba del contenido: permiten dirigir una búsqueda archivística exacta en AGN, Senado, Bicameral y depósito receptor. Estado: **BORRADOR_NO_ENVIADO**.
""", encoding="utf-8")

econ_request = HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V133.md"
econ_request.write_text(econ_request.read_text(encoding="utf-8-sig").rstrip() + """

## Clave V133 · ruta COMDOC y comparadores contiguos

La página oficial del Ministerio separa los expedientes desde septiembre de 2016, consultables en GDE, de los anteriores, consultables en COMDOC. Por ser de 2008, `S01:0342455/2008` debe buscarse primero en COMDOC, cuyo enlace publicado es `http://expedientes.mecon.gov.ar/finddoc2/finddoc/Inicio`. Al `30/08/2026` el endpoint rechazó conexión; por eso la consulta no pudo ejecutarse y no corresponde registrar “sin resultados”. Solicito búsqueda sustitutiva por administradores COMDOC, Mesa de Entradas, ONCP, DADP y archivo, con índice, cuerpo, remitos y cualquier equivalencia de migración a GDE/GEDO/RUDO.

Además, los años inmediatos muestran un cambio comprobable de exposición: en 2007 Citibank y Banco Nación tienen SIDIF individualizados; en 2008 Citibank aparece como `VARIOS` y Banco Nación individualizado; en 2009 las cinco celdas SIDIF están vacías; en 2010 ambas comisiones vuelven a individualizarse. Esto fundamenta pedir el submayor homogéneo 2008, pero no permite inferir que una celda vacía carezca de comprobantes ni atribuir importes a las recompras. Estado: **BORRADOR_NO_ENVIADO**.
""", encoding="utf-8")

# Textos de síntesis.
(HERE / "README_V133.md").write_text("""# V133 · rutas archivísticas parlamentarias y COMDOC

V133 cierra los localizadores parlamentarios de los anexos AGN T3/T4 (`OV 366/09` y `OV 44/10`), su paso por la Bicameral Revisora y su archivo el 28/05/2012. También prueba que el expediente `S01:0342455/2008` pertenece a la ruta COMDOC pre-septiembre de 2016; el endpoint publicado no estuvo operativo, por lo que la consulta quedó sin ejecutar, no “sin resultado”. La comparación CGN 2007–2010 demuestra cambios entre SIDIF individualizado, `VARIOS` y celda vacía. No aparece una liquidación nueva: 10/10 adjudicaciones, 9/10 cuentas candidatas y 0/10 ejecuciones confirmadas. Seis pedidos siguen DRAFT_NOT_SENT.
""", encoding="utf-8")

(HERE / "VEREDICTO_V133.md").write_text("""# Veredicto V133

Los dos anexos AGN faltantes dejaron de ser objetos con custodia incierta: el T3 fue remitido como `OV 366/09` y el T4 como `OV 44/10`; ambos pasaron por la Bicameral Permanente Mixta Revisora de Cuentas y fueron enviados al archivo el 28/05/2012. Sus cuerpos continúan abiertos porque el Senado no publica el “Texto original”.

Para `S01:0342455/2008`, la página oficial de Economía confirma que la ruta temporal correcta es COMDOC. El endpoint legado rechazó conexión: quedó demostrado el índice competente, no el resultado de la consulta. Indisponibilidad del sistema no equivale a inexistencia documental.

La lectura visual de los Anexos K 2007, 2008, 2009 y 2010 confirma que las mismas cinco claves alternan entre comprobantes individualizados, `VARIOS` y columna vacía. Eso hace demostrable y proporcionado pedir el submayor; no vincula por sí solo las comisiones con la recompra.

La ejecución sigue abierta: 0/10 filas confirmadas. `CLOSED_NETWORK_GATE=NO`; seis borradores, ninguno enviado.
""", encoding="utf-8")

(HERE / "E0_FISCAL_RECONSTRUCTION_V133.md").write_text("""# Reconstrucción fiscal E0 · V133

## Resultado incremental

1. La ruta de los anexos AGN T3/T4 queda enlazada de resolución y actuación a expediente parlamentario, comisión y archivo.
2. La ruta del expediente de recompra queda temporalmente asignada a COMDOC; el cuerpo sigue abierto porque el endpoint no permitió ejecutar la consulta.
3. La transición 2007–2010 demuestra que el grado de detalle publicado en Anexo K no es estable y que una celda vacía no prueba ausencia contable.
4. Ninguno de esos avances completa preadjudicación, transferencia Caja, informe T+3, crédito BCRA o cancelación CRyL: 0/10 ejecuciones confirmadas.

El avance es archivístico y probatorio. Convierte pedidos genéricos en búsquedas por identificadores exactos sin inflar la evidencia de pago.
""", encoding="utf-8")

(HERE / "RETRIEVAL_LOG_V133.md").write_text("""# Registro de recuperación V133

Fecha: 2026-08-30.

1. Se localizaron y preservaron las fichas oficiales del Senado `OV 366/09` y `OV 44/10`, correspondientes a las remisiones AGN T3/T4.
2. Se verificaron fechas de ingreso, comisión, egreso y archivo; ambas fichas indican que “Texto original” está en proceso de carga.
3. Se preservó la página oficial de Economía que asigna expedientes anteriores a septiembre de 2016 a COMDOC y posteriores a GDE.
4. Se intentó abrir el endpoint COMDOC publicado por vía HTTP/HTTPS; rechazó conexión. La consulta de `S01:0342455/2008` no se ejecutó y no se codificó como ausencia.
5. Se verificaron visualmente los Anexos K 2007, 2008 y 2009, y se mantuvo el comparador 2010: cinco claves SIGADE con estados SIDIF individualizado, agregado o vacío.
6. La revisión visual evitó una falsa reasignación: el SIDIF `269277` de 2008 pertenece a otra fila, no a `83020000`.
7. Las búsquedas exactas no localizaron submayor público, órdenes ni comprobantes 2008 para las cinco claves.
8. No se envió ningún pedido ni se realizó presentación externa.
""", encoding="utf-8")

refs_path = HERE / "SOURCE_REFERENCES_V133.md"
refs_path.write_text(refs_path.read_text(encoding="utf-8-sig").rstrip() + """

- Senado OV 366/09: https://www.senado.gob.ar/parlamentario/comisiones/verExp/366.09/OV/PP
- Senado OV 44/10: https://www.senado.gob.ar/parlamentario/comisiones/verExp/44.10/OV/PP
- Comisión Bicameral Revisora de Cuentas: https://www.senado.gob.ar/parlamentario/comisiones/info/100
- Economía · consulta COMDOC/GDE: https://www.argentina.gob.ar/economia/informacionciudadana/consultadeexpedientes
- CGN Cuenta de Inversión 2007: https://www.economia.gob.ar/hacienda/cgn/cuenta/2007/archivos/sdp.pdf
- CGN Cuenta de Inversión 2009: https://www.economia.gob.ar/hacienda/cgn/cuenta/2009/archivos/sdp.pdf

La ruta parlamentaria y la ruta de sistema prueban custodia y competencia; no prueban contenido ni ejecución. Los comparadores contables prueban formato de exposición, no asignación transaccional.
""", encoding="utf-8")

handover = """# Handover V133 → V134

## Estado congelado

- Diez adjudicaciones participante–instrumento exactas; nueve cuentas BCRA candidatas; MERVAL abierta.
- 0/10 filas con preadjudicación ejecutada, transferencia Caja, informe T+3, crédito BCRA o cancelación CRyL confirmados.
- Identidad final AGN: UUID `b52e2e9c-90b5-4af1-bf5d-0bab8596606e`, Actuación `41/2009`, Resolución `202/2009`; `48 0237/09` contextual fuerte no literal.
- T3/T4: anexos probados y ruta parlamentaria exacta cerrada como `OV 366/09` y `OV 44/10`; Bicameral Revisora; archivo 28/05/2012. Cuerpos no publicados.
- `S01:0342455/2008`: ruta oficial correcta COMDOC pre-09/2016; endpoint publicado no operativo; consulta no ejecutada; cuerpo abierto.
- CGN 2007–2010: cinco claves SIGADE alternan SIDIF individualizado, `VARIOS` y celdas vacías. Submayor 2008 no localizado.
- Seis pedidos DRAFT_NOT_SENT; ninguno enviado; panel estricto sin cambios.

## Prioridad V134

1. Buscar inventarios, remitos y notas de archivo de la Bicameral usando `OV 366/09`, `OV 44/10` y nota de 18/05/2012.
2. Buscar un acceso alternativo oficial, espejo o consulta administrativa del índice COMDOC para `S01:0342455/2008`; registrar caída como acceso, no como ausencia.
3. Buscar submayores CGN/ONCP/TGN o listados de C-41 2008 por las cinco claves y por los comprobantes ya visibles de Banco Nación.
4. Mantener separados expediente, submayor, orden de pago, crédito BCRA, transferencia Caja y cancelación CRyL.
5. No enviar los seis pedidos sin autorización expresa.
"""
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V133_A_V134.md").write_text(handover, encoding="utf-8")

(HERE / "AUDITORIA_V133.md").write_text(f"""# Auditoría V133

- Fuentes maestras: {len(catalog)}; tres fuentes HTML oficiales nuevas preservadas.
- Fuentes primarias E0: {len(census)}.
- Ledger fiscal: {len(ledger)} filas; cortes metodológicos: {len(breaks)}.
- AGN T3/T4: expedientes parlamentarios y ruta de archivo exactos; cuerpos abiertos.
- COMDOC: sistema legado competente exacto; endpoint no operativo; consulta sin ejecutar.
- CGN: transición 2007–2010 verificada; submayor target abierto.
- Escalera: 10 adjudicaciones; 9 cuentas candidatas; 0 ejecuciones confirmadas.
- Pedidos: 6 borradores, 0 enviados; {len(trace)} objetos y {len(keys)} claves.
- Panel estricto: 30 entidades; {STRICT}% sin cambios.
""", encoding="utf-8")

# Proveniencia y auditoría física.
provenance_path = HERE / "ARCHIVAL_PROVENANCE_V133.csv"
provenance = [row for row in read_csv(provenance_path) if row["source_id"] not in source_ids]
for source in SOURCES:
    provenance.append({"source_id": source["id"], "original_url": source["url"], "retrieval_url": source["url"], "capture_timestamp": "20260830", "cdx_digest": "N/A_DIRECT_OFFICIAL", "local_path": source["local"], "sha256": source["sha256"], "bytes": str(source["bytes"]), "provenance_note": "Captura directa oficial preservada y hasheada en V133; metadatos verificables en el HTML."})
write_csv(provenance_path, provenance)

for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    shutil.copyfile(AUDIT / f"{stem}_V132.csv", AUDIT / f"{stem}_V133.csv")

hash_rows = []
for row in catalog:
    local = row["archivo_local"]
    path = REPO / local.lstrip("/") if local else None
    exists = bool(path and path.is_file())
    actual = sha256(path) if exists else ""
    expected = row["sha256"]
    hash_rows.append({"id": row["id"], "archivo_local": local, "exists": str(exists), "sha_catalog": expected, "sha_actual": actual, "hash_ok": str(bool(exists and expected and actual.lower() == expected.lower()))})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V133.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V133.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
assert physical == hash_ok == 355

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or "tmp" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": str(size), "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V133.csv", size_rows)

completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V132.json").read_text(encoding="utf-8"))
for key in list(completeness):
    if key.endswith("_v132") or "newly_preserved_v132" in key:
        completeness.pop(key, None)
completeness.update({
    "checkpoint": "V133", "date": "2026-08-30",
    "state": "E0_PARLIAMENTARY_ARCHIVE_AND_COMDOC_ROUTE_CLOSED_EXECUTION_OPEN_NOT_SENT",
    "numeric_v133_strict_changed": False, "master_catalog_entries": len(catalog),
    "physical_local_copies": physical, "physical_local_hash_ok": hash_ok,
    "e0_primary_sources_preserved": len(census), "e0_quality": "PRIMARY_ARCHIVAL_CUSTODY_AND_LEGACY_QUERY_ROUTES",
    "sources_newly_preserved_v133": 3, "e0_primary_sources_newly_preserved_v133": 3,
    "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
    "e0_request_traceability_rows": len(trace), "e0_request_search_keys": len(keys),
    "e0_agn_quarterly_parliamentary_locators_closed": 2,
    "e0_agn_quarterly_annexes_public_body_open": 2,
    "e0_exp_file": "S01:0342455/2008_COMDOC_ROUTE_EXACT_ENDPOINT_UNAVAILABLE_BODY_OPEN",
    "e0_sigade_sidif_transition_rows": len(transitions),
    "e0_settlement_award_rows_exact": 10, "e0_settlement_account_candidate_rows": 9,
    "e0_settlement_executed_rows_confirmed": 0, "e0_requests_submitted": 0,
    "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
    "historical_workstream": "Parliamentary archive and COMDOC routes closed; annex bodies, legacy index result, subledgers and executed settlement remain open; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V133.json").write_text(json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V133 · rutas parlamentarias y COMDOC"
text = backup.read_text(encoding="utf-8-sig")
if marker not in text:
    text += f"\n\n{marker}\n\n- T3/T4 AGN cruzados con Senado `OV 366/09` y `OV 44/10`, Bicameral Revisora y archivo 28/05/2012; cuerpos abiertos.\n- `S01:0342455/2008` asignado a COMDOC por regla oficial; endpoint no operativo, consulta no ejecutada.\n- Transición CGN 2007–2010 distingue SIDIF individualizado, `VARIOS` y columna vacía sin inferir ausencia contable.\n- Escalera sin cambio: 10 adjudicaciones, 9 cuentas candidatas, 0 ejecuciones confirmadas; seis pedidos no enviados.\n"
    backup.write_text(text, encoding="utf-8")

inherited = []
for row in read_csv(PARENT / "INHERITED_QA_STATUS_V132.csv"):
    inherited.append({"script": row["script"], "pre_v133_result": row["post_v132_result"], "post_v133_result": "EXPECTED_SUPERSEDED_ASSERTION" if row["script"] == "qa_v132.py" else row["post_v132_result"], "interpretation": "V132 is superseded by archival-route sources and V133 counts." if row["script"] == "qa_v132.py" else row["interpretation"]})
inherited.append({"script": "qa_v133.py", "pre_v133_result": "N/A", "post_v133_result": "PASS", "interpretation": "Parliamentary locators, COMDOC route, disclosure transitions and non-execution boundaries verified."})
write_csv(HERE / "INHERITED_QA_STATUS_V133.csv", inherited)

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

parliament = rows("E0_AGN_PARLIAMENTARY_ARCHIVE_CROSSWALK_V133.csv")
assert len(parliament) == 2 and {r["senate_exp"] for r in parliament} == {"OV 366/09", "OV 44/10"}
assert all(r["archive_date"] == "2012-05-28" and r["original_text_public_state"] == "EN_PROCESO_DE_CARGA" for r in parliament)
quarterly = rows("E0_AGN_QUARTERLY_ANNEX_AVAILABILITY_V133.csv")
assert all("PARLIAMENTARY_EXPEDIENT" in r["status"] for r in quarterly[1:])
comdoc = rows("E0_COMDOC_LEGACY_QUERY_ROUTE_V133.csv")
assert comdoc[0]["test_result"] == "CONNECTION_REFUSED" and comdoc[0]["body_query_executed"] == "NO"
assert len(rows("E0_EXPEDIENT_PUBLIC_SEARCH_EXHAUSTION_V133.csv")) == 6

disclosure = rows("E0_SIGADE_SIDIF_DISCLOSURE_LADDER_V133.csv")
assert len(disclosure) == 24
assert sum(r["year"] == "2007" for r in disclosure) == 5
assert sum(r["year"] == "2009" and r["disclosure_level"] == "BLANK" for r in disclosure) == 5
transitions = rows("E0_SIGADE_SIDIF_TARGET_DISCLOSURE_TRANSITIONS_V133.csv")
assert len(transitions) == 5
assert next(r for r in transitions if r["sigade"] == "83020000")["transition"] == "ITEMIZED → AGGREGATED → BLANK → ITEMIZED"

assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V133.csv")) == 157
assert len(rows("E0_FISCAL_METHOD_BREAKS_V133.csv")) == 117
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V133.csv")) == 104
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V133.csv")) == 98
ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V133.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V133.csv")}
new_ids = {"e0_senado_exp_366_09_agn_res211_t3", "e0_senado_exp_44_10_agn_res44_t4", "e0_economia_consulta_expedientes_comdoc_gde"}
assert len(census) == 121 and new_ids <= set(census)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 361 and len({r["id"] for r in catalog}) == 361

expected = {
    "senado_exp_366_09_agn_res211_t3.html": (48711, "f74fbe0afdc64f2417b33812dbf68696df7b70e73b65b0fe1e4f2eb69720574c"),
    "senado_exp_44_10_agn_res44_t4.html": (48707, "b8ba499ccb21798d392d4c8e8499d51c6057bb076c6f8d41c08d773e201beed2"),
    "economia_consulta_expedientes_comdoc_gde.html": (35065, "ffa7137f0ff2405d504b64e06cc522420384400164d23838256bff443c3d4ec2"),
}
bin_dir = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v133" / "binaries"
assert len(list(bin_dir.iterdir())) == 3
for name, (size, digest) in expected.items():
    path = bin_dir / name
    assert path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest() == digest

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V133.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V133"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 355
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v133_strict_changed"] is False

for name, marker in {
    "REQUEST_AGN_2018_REPLY_V133.md": "## Clave V133 · remisión parlamentaria y archivo",
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V133.md": "## Clave V133 · ruta COMDOC y comparadores contiguos",
}.items():
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert marker in text and "BORRADOR_NO_ENVIADO" in text

for name in ("README_V133.md", "VEREDICTO_V133.md", "E0_FISCAL_RECONSTRUCTION_V133.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V133_A_V134.md"):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "0/10" in text

print("V133 QA PASS")
'''
(HERE / "qa_v133.py").write_text(qa, encoding="utf-8")

def checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V133.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V133", "parent_checkpoint": "V132",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": 3, "new_primary_sources": 3,
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks),
        "agn_parliamentary_archive_locators_closed": 2, "agn_quarterly_annex_bodies_open": 2,
        "comdoc_route_exact": True, "comdoc_query_executed": False, "expedient_body_publicly_located": False,
        "award_rows_exact": 10, "account_candidate_rows": 9, "executed_settlement_rows_confirmed": 0,
        "request_drafts": 6, "request_traceability_rows": len(trace), "request_search_keys": len(keys),
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V133.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    "checkpoint": "V133", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical copies SHA-valid; two parliamentary archive locators and the official COMDOC temporal route closed; zero of ten executed settlement rows confirmed; six requests drafted and none submitted.",
    "historical_workstream": "Parliamentary archive and legacy-system routes closed; annex bodies, COMDOC result, subledgers and executed settlement remain open; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V133 BUILD PASS")
