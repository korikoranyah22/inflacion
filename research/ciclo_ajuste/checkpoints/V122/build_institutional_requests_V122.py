from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import shutil


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
V121 = HERE.parent / "V121"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v122" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        if not rows:
            raise ValueError(f"fields required for empty CSV: {path}")
        fields = list(rows[0])
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


source_specs = [
    {
        "id": "e0_afip_rg2418_security_codes_2007",
        "institution": "Administración Federal de Ingresos Públicos",
        "title": "Resolución General 2418 · Anexo III; códigos y valuaciones de títulos al 31/12/2007",
        "url": "https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-2418-2008-138491/texto",
        "file": "afip_rg2418_anexo3_titulos_2007.pdf",
        "publication": "2008-03-10",
        "period": "códigos y valuaciones al 2007-12-31; publicado antes de las recompras 2008",
        "type": "PDF oficial · binario preservado",
        "families": "state_bcra;fiscal;debt;security_identifiers;historical_codes;valuation",
        "breaks": "código oficial de tabla versus identificación institucional del código; denominación versus ISIN",
        "use": "USABLE_CONTEMPORANEOUS_HISTORICAL_SECURITY_CODE_TABLE",
        "caveat": "Vincula denominaciones exactas con códigos, pero el encabezado dice sólo CÓDIGO y no prueba por sí solo que sean códigos CRyL ni una liquidación.",
        "verified": "16 páginas; páginas PDF 5 y 13 renderizadas e inspeccionadas visualmente; 5426, 5427, 45698 y 45701 legibles.",
    },
    {
        "id": "e0_afip_rg2575_security_codes_2008",
        "institution": "Administración Federal de Ingresos Públicos",
        "title": "Resolución General 2575 · Anexo III; códigos y valuaciones de títulos al 31/12/2008",
        "url": "https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-2575-2009-151297/texto",
        "file": "afip_rg2575_anexo3_valores_2008.pdf",
        "publication": "2009-03-09",
        "period": "códigos y valuaciones al 2008-12-31; corroboración inmediatamente posterior",
        "type": "PDF oficial · binario preservado",
        "families": "state_bcra;fiscal;debt;security_identifiers;historical_codes;valuation",
        "breaks": "código oficial de tabla versus identificación institucional del código; corroboración posterior versus uso en la operación",
        "use": "USABLE_NEAR_CONTEMPORANEOUS_SECURITY_CODE_CORROBORATION",
        "caveat": "Repite los cuatro códigos por denominación; no contiene los ISIN ni el código de la subespecie strip 2009.",
        "verified": "51 páginas; páginas PDF 44 y 51 renderizadas e inspeccionadas visualmente; los cuatro códigos se repiten.",
    },
    {
        "id": "e0_cvsa_f33914_deferred_delivery_2017",
        "institution": "Caja de Valores S.A.",
        "title": "Formulario F-33914.01 · Entrega diferida",
        "url": "https://cajadevalores.com.ar/img/Formularios/F-33914.01.pdf",
        "file": "cvsa_f33914_01_entrega_diferida.pdf",
        "publication": "2017-11-23",
        "period": "formulario legado publicado en 2017; evidencia retrospectiva posterior al objetivo",
        "type": "PDF oficial · binario preservado",
        "families": "state_bcra;fiscal;debt;Caja;custody;deferred_transfer;matching;form_schema",
        "breaks": "formulario posterior versus formulario usado en 2008; esquema en blanco versus instrucción ejecutada",
        "use": "USABLE_RETROSPECTIVE_DEFERRED_DELIVERY_SCHEMA",
        "caveat": "Aporta campos de entrega diferida; no acredita que esta edición o formulario se usara en las recompras de 2008-2009.",
        "verified": "2 páginas, original y duplicado, renderizadas e inspeccionadas visualmente; fecha de ejecución, límite de matching, Código Caja y contrapartes legibles.",
    },
    {
        "id": "e0_cvsa_f33915_deferred_receipt_2017",
        "institution": "Caja de Valores S.A.",
        "title": "Formulario F-33915.01 · Recepción diferida",
        "url": "https://cajadevalores.com.ar/img/Formularios/F-33915.01.pdf",
        "file": "cvsa_f33915_01_recepcion_diferida.pdf",
        "publication": "2017-11-23",
        "period": "formulario legado publicado en 2017; evidencia retrospectiva posterior al objetivo",
        "type": "PDF oficial · binario preservado",
        "families": "state_bcra;fiscal;debt;Caja;custody;deferred_transfer;matching;form_schema",
        "breaks": "formulario posterior versus formulario usado en 2008; autorización receptora versus liquidación",
        "use": "USABLE_RETROSPECTIVE_DEFERRED_RECEIPT_SCHEMA",
        "caveat": "Aporta la contraparte de recepción y matching; no prueba una instrucción ni una liquidación objetivo.",
        "verified": "2 páginas, original y duplicado, renderizadas e inspeccionadas visualmente; campos espejo de recepción legibles.",
    },
    {
        "id": "e0_cvsa_communication_10290_tsa_deferred_2020",
        "institution": "Caja de Valores S.A.",
        "title": "Comunicado 10290 · archivos TSA y transferencias diferidas",
        "url": "https://www.argentina.gob.ar/sites/default/files/ssn_200818_reestructuracioncomunicadocajavalores.pdf",
        "file": "cvsa_comunicado_10290_tsa_diferida_2020.pdf",
        "publication": "2020-08-18",
        "period": "operación de canje 2020; evidencia posterior de separación canal-modalidad",
        "type": "PDF oficial · binario preservado",
        "families": "state_bcra;fiscal;debt;Caja;TSA;deferred_transfer;CVSA_code;ISIN",
        "breaks": "TSA como canal versus modalidad diferida; mapeo contemporáneo 2020 versus operación 2008",
        "use": "USABLE_POST_TARGET_CHANNEL_MODALITY_DISTINCTION",
        "caveat": "Muestra que TSA y diferida coexisten y que Código CVSA e ISIN son columnas distintas; no prueba el canal de 2008.",
        "verified": "6 páginas renderizadas; páginas PDF 2 y 6 inspeccionadas visualmente; TSA/diferida y columnas Código CVSA/ISIN legibles.",
    },
    {
        "id": "e0_byma_nsc_tsa_modality_retirement_2023",
        "institution": "Bolsas y Mercados Argentinos S.A.",
        "title": "Instructivo de Liquidaciones · Nuevo Sistema de Custodia",
        "url": "https://data-widgets.byma.com.ar/wp-content/uploads/dlm_uploads/2023/09/Instructivo-Liquidaciones-Nuevo-Sistema-Custod.pdf",
        "file": "byma_instructivo_liquidaciones_nsc_2023.pdf",
        "publication": "2023-09-12",
        "period": "migración al Nuevo Sistema de Custodia 2023; evidencia posterior",
        "type": "PDF oficial · binario preservado",
        "families": "state_bcra;fiscal;debt;Caja;TSA;custody_code;ISIN;system_migration",
        "breaks": "regla nueva versus regla histórica; código custodia versus ISIN/código negociación; archivo TSA versus modalidad",
        "use": "USABLE_POST_TARGET_SYSTEM_DISTINCTION_AND_BREAK",
        "caveat": "Confirma que TSA conserva su formato mientras se eliminan los tipos diferida/inmediata; la regla 2023 no puede retrotraerse a 2008.",
        "verified": "5 páginas renderizadas; página PDF 3 inspeccionada visualmente; formato TSA, código de custodia y retiro de modalidades legibles.",
    },
]
for spec in source_specs:
    path = BIN / spec["file"]
    if not path.is_file():
        raise FileNotFoundError(path)
    spec["bytes"] = path.stat().st_size
    spec["sha256"] = sha256(path)
    spec["local"] = "/" + path.relative_to(REPO).as_posix()


new_ids = {spec["id"] for spec in source_specs}
catalog = [row for row in read_csv(CATALOG) if row["id"] not in new_ids]
for spec in source_specs:
    catalog.append(
        {
            "id": spec["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": spec["institution"],
            "titulo": spec["title"], "url_original": spec["url"], "archivo_local": spec["local"],
            "fecha_descarga": "2026-08-29", "fecha_publicacion": spec["publication"], "codigo_serie": "",
            "periodo_utilizado": spec["period"], "tipo": spec["type"], "sha256": spec["sha256"],
            "nota": f"V122 E0 fiscal: {spec['bytes']:,} bytes. {spec['verified']}",
        }
    )
write_csv(CATALOG, catalog)


census = [row for row in read_csv(V121 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V121.csv") if row["source_id"] not in new_ids]
for spec in source_specs:
    census.append(
        {
            "source_id": spec["id"], "institution": spec["institution"], "artifact": spec["title"],
            "url": spec["url"], "local_path": spec["local"], "sha256": spec["sha256"], "bytes": str(spec["bytes"]),
            "period_coverage": spec["period"], "variable_families": spec["families"], "primary_source": "YES",
            "preserved": "YES", "method_breaks": spec["breaks"], "use_status": spec["use"], "caveat": spec["caveat"],
        }
    )
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V122.csv", census)


ledger = read_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V122.csv")
breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V122.csv")
channels = read_csv(HERE / "CURRENT_OFFICIAL_SUBMISSION_CHANNELS_V122.csv")
trace = read_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V122.csv")
responses = read_csv(HERE / "E0_REQUEST_RESPONSE_REGISTER_V122.csv")
closures = read_csv(HERE / "E0_REQUEST_CLOSURE_CRITERIA_V122.csv")
system_map = read_csv(HERE / "E0_DOCUMENT_SYSTEM_TEMPORAL_MAP_V122.csv")
authorities = read_csv(HERE / "E0_ARCHIVAL_RETENTION_AUTHORITY_MATRIX_V122.csv")
negative_adequacy = read_csv(HERE / "E0_NEGATIVE_RESPONSE_ADEQUACY_V122.csv")
producer_map = read_csv(HERE / "E0_RECORD_PRODUCER_SYSTEM_MAP_V122.csv")
search_keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V122.csv")
attachments = read_csv(HERE / "E0_REQUEST_ATTACHMENT_MINIMUM_V122.csv")
version_chain = read_csv(HERE / "E0_CRYL_EFFECTIVE_VERSION_CHAIN_V122.csv")
term_audit = read_csv(HERE / "E0_BUYBACK_MODALITY_TERM_AUDIT_V122.csv")
cga_map = read_csv(HERE / "E0_CRYL_CGA_RECORD_MAP_V122.csv")


new_breaks = [
    {
        "break_id": "deferred_modality_not_tsa_channel", "dimension": "system",
        "problem": "La modalidad diferida describe el tipo o programación de transferencia; TSA describe un canal de archivos que puede transportarla.",
        "rule": "Mantener canal y modalidad en campos separados y exigir el registro objetivo antes de asignarlos a 2008.",
        "status": "FROZEN", "evidence": "CVSA Comunicado 10290; BYMA Instructivo NSC 2023",
    },
    {
        "break_id": "legacy_form_not_contemporaneous_2008_use", "dimension": "legal_time",
        "problem": "Los formularios F-33914.01 y F-33915.01 documentan un esquema de transferencia diferida en 2017, no su edición o uso en 2008.",
        "rule": "Usarlos sólo como diccionario retrospectivo de campos y pedir la versión vigente o la tabla de equivalencias histórica.",
        "status": "FROZEN", "evidence": "CVSA F-33914.01 y F-33915.01; metadatos 2017-11-23",
    },
    {
        "break_id": "matching_fields_not_completed_target_transfer", "dimension": "phase",
        "problem": "La existencia de fecha de ejecución, límite de matching y contrapartes en un formulario vacío no prueba una instrucción emparejada ni ejecutada.",
        "rule": "Exigir formulario completado, lote, estado de matching y asiento de recepción para cada fecha y especie.",
        "status": "FROZEN", "evidence": "CVSA F-33914.01 y F-33915.01",
    },
    {
        "break_id": "current_nsc_rule_not_historical_rule", "dimension": "legal_time",
        "problem": "El Nuevo Sistema de Custodia eliminó en 2023 los tipos diferida e inmediata; esa regla nueva no describe automáticamente 2008.",
        "rule": "Usar el cambio como corte metodológico y no retrotraerlo al período objetivo.",
        "status": "FROZEN", "evidence": "BYMA Instructivo de Liquidaciones NSC 2023",
    },
    {
        "break_id": "isin_not_cvsa_custody_code", "dimension": "identifier",
        "problem": "ISIN, código de negociación y código de custodia/CVSA son identificadores diferentes aunque señalen la misma especie.",
        "rule": "Conservar cada columna y documentar el puente fuente por fuente; no reemplazar un identificador por otro.",
        "status": "FROZEN", "evidence": "CVSA Comunicado 10290; BYMA Instructivo NSC 2023",
    },
    {
        "break_id": "parent_security_code_not_strip_subspecies_code", "dimension": "identifier",
        "problem": "El código del BODEN 2012 principal no identifica necesariamente la subespecie separada cupón 15 de 2009.",
        "rule": "Mantener ARARGE03G415 sin código público hasta localizar una tabla o registro de la subespecie; no heredar 5426.",
        "status": "FROZEN", "evidence": "Llamado strip 2009; RG AFIP 2418 y 2575",
    },
]
break_ids = {row["break_id"] for row in new_breaks}
breaks = [row for row in breaks if row["break_id"] not in break_ids] + new_breaks
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V122.csv", breaks)


new_search_keys = [
    {"key_id": "SK122_44", "request_id": "REQ122_ECON", "key_group": "historical_code", "exact_key": "5426;5427;45698;45701", "search_purpose": "cruzar resultados, especie recibida y registración de deuda", "source_or_basis": "RG AFIP 2418/2008 y 2575/2009", "caveat": "Códigos oficiales por denominación; no son por sí solos asiento liquidado ni código CRyL."},
    {"key_id": "SK122_45", "request_id": "REQ122_BCRA", "key_group": "security_bridge", "exact_key": "ARARGE034678=5426;ARARGE035709=5427;ARARGE03E147=45698;ARARGE03E154=45701", "search_purpose": "pedir tabla histórica ISIN-código de custodia/CRyL", "source_or_basis": "llamados oficiales + RG AFIP 2418/2575", "caveat": "Puente por denominación exacta; requerir confirmación institucional."},
    {"key_id": "SK122_46", "request_id": "REQ122_CAJA", "key_group": "security_bridge", "exact_key": "ARARGE034678=5426;ARARGE035709=5427;ARARGE03E147=45698;ARARGE03E154=45701", "search_purpose": "localizar especie y confirmar Código Caja histórico", "source_or_basis": "llamados oficiales + RG AFIP 2418/2575", "caveat": "El encabezado AFIP histórico dice CÓDIGO; confirmar equivalencia y vigencia en Caja."},
    {"key_id": "SK122_47", "request_id": "REQ122_CAJA", "key_group": "form", "exact_key": "F-33914.01;F-33915.01;Entrega diferida;Recepción diferida", "search_purpose": "obtener versión vigente en 2008 o equivalencia", "source_or_basis": "formularios CVSA publicados en 2017", "caveat": "La edición preservada es posterior al período objetivo."},
    {"key_id": "SK122_48", "request_id": "REQ122_CAJA", "key_group": "matching", "exact_key": "fecha de ejecución;fecha límite de Matching;Código Caja;depositante emisor;comitente emisor;depositante receptor;comitente receptor", "search_purpose": "buscar instrucción emparejada y estado de ejecución", "source_or_basis": "F-33914.01 y F-33915.01", "caveat": "Campos de esquema; no prueban que exista un formulario objetivo."},
    {"key_id": "SK122_49", "request_id": "REQ122_ECON", "key_group": "strip_code", "exact_key": "ARARGE03G415;BODEN 2012 cupón 15;subespecie;Código Caja", "search_purpose": "localizar el código propio del strip 2009", "source_or_basis": "llamado oficial 2009", "caveat": "No heredar 5426 del título principal."},
    {"key_id": "SK122_50", "request_id": "REQ122_BCRA", "key_group": "channel_modality", "exact_key": "TSA;modalidad diferida;CGA;FT;FTC;Código CVSA;Código CRyL", "search_purpose": "pedir equivalencias históricas sin confundir canal y modalidad", "source_or_basis": "B9173; CVSA 10290; BYMA NSC 2023", "caveat": "Evidencia posterior sólo delimita categorías; no acredita uso en 2008."},
]
new_key_ids = {row["key_id"] for row in new_search_keys}
search_keys = [row for row in search_keys if row["key_id"] not in new_key_ids] + new_search_keys
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V122.csv", search_keys)


new_trace = [
    {"trace_id": "TR122_068", "request_id": "REQ122_ECON", "institution": "Ministerio de Economía / Tesoro", "gap_id": "CL122_SECURITY_CODE", "requested_record": "Tabla o registro de códigos internos de las cuatro especies 2008", "period_or_date": "2008", "identifiers": "cuatro ISIN; 5426; 5427; 45698; 45701", "minimum_usable_fields": "ISIN; código; denominación; vigencia; sistema", "confidentiality_fallback": "certificación por especie", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR122_069", "request_id": "REQ122_CAJA", "institution": "Caja de Valores S.A.", "gap_id": "CL122_SECURITY_CODE", "requested_record": "Tabla histórica ISIN-Código Caja y código del strip", "period_or_date": "2008-2009", "identifiers": "cinco ISIN; cuatro códigos localizados", "minimum_usable_fields": "ISIN; Código Caja; subespecie; alta/baja; vigencia", "confidentiality_fallback": "confirmación institucional sin tenedores", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR122_070", "request_id": "REQ122_CAJA", "institution": "Caja de Valores S.A.", "gap_id": "CL122_DEFERRED_MODALITY", "requested_record": "Versión 2008 del formulario o procedimiento de entrega/recepción diferida", "period_or_date": "2008-2009", "identifiers": "F-33914.01; F-33915.01; modalidad diferida", "minimum_usable_fields": "edición; vigencia; campos; matching; reemplazo", "confidentiality_fallback": "manual o tabla de equivalencias", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR122_071", "request_id": "REQ122_CAJA", "institution": "Caja de Valores S.A.", "gap_id": "CL122_CAJA_ROUTE", "requested_record": "Instrucciones diferidas emparejadas y estado de ejecución", "period_or_date": "fechas T+2 2008-2009", "identifiers": "0306/40000; cinco ISIN; códigos 5426/5427/45698/45701", "minimum_usable_fields": "fecha ejecución; límite matching; emisor/receptor; código; cantidad; estado", "confidentiality_fallback": "agregado por fecha/especie/estado", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR122_072", "request_id": "REQ122_BCRA", "institution": "BCRA / CRyL", "gap_id": "CL122_SECURITY_CODE", "requested_record": "Diccionario histórico entre ISIN, código de custodia/Caja y código CRyL", "period_or_date": "2008-2009", "identifiers": "cinco ISIN; cuatro códigos localizados", "minimum_usable_fields": "identificador; tipo; especie; vigencia; sistema", "confidentiality_fallback": "tabla testada sin cuentas", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR122_073", "request_id": "REQ122_BCRA", "institution": "BCRA / CRyL", "gap_id": "CL122_DEFERRED_MODALITY", "requested_record": "Equivalencia histórica entre modalidad diferida, TSA/CGA y fórmula CRyL", "period_or_date": "2008-2009", "identifiers": "diferida; TSA; CGA; FT; FTC; DVP", "minimum_usable_fields": "canal; modalidad; formulario/archivo; estado; vigencia", "confidentiality_fallback": "manual o diccionario de códigos", "status": "DRAFT_NOT_SENT"},
]
new_trace_ids = {row["trace_id"] for row in new_trace}
trace = [row for row in trace if row["trace_id"] not in new_trace_ids] + new_trace
write_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V122.csv", trace)


new_closures = [
    {"gap_id": "CL122_SECURITY_CODE", "target_question": "¿Cuál era el Código Caja/CRyL de cada una de las cinco especies objetivo?", "minimum_positive_evidence": "Tabla o certificación institucional contemporánea que vincule ISIN, denominación, tipo de código, valor y vigencia; para el strip, código propio de subespecie.", "minimum_negative_route_evidence": "Búsqueda reproducible por los cinco ISIN, denominaciones, cuatro códigos conocidos, tablas históricas y sistemas sucesores en Economía, Caja y BCRA/CRyL.", "does_not_close": "Código AFIP por denominación sin etiqueta institucional; código del título principal heredado al strip; tabla posterior sin vigencia histórica.", "initial_status": "OPEN_FOUR_HISTORICAL_CODES_LOCATED_STRIP_CODE_NOT_SENT"},
    {"gap_id": "CL122_DEFERRED_MODALITY", "target_question": "¿Qué formulario, archivo y estados operativos implementaron la modalidad diferida en 2008?", "minimum_positive_evidence": "Manual o versión vigente en 2008 más instrucción/lote objetivo que separe canal, modalidad, matching, recepción y liquidación.", "minimum_negative_route_evidence": "Búsqueda reproducible por modalidad diferida, F-33914/F-33915, TSA, CGA, FT/FTC/DVP, cuenta, fechas y repositorios históricos/sucesores.", "does_not_close": "Formulario 2017 en blanco; coexistencia TSA-diferida en 2020; retiro de modalidades en 2023; silencio del procedimiento sobre siglas.", "initial_status": "OPEN_RETROSPECTIVE_FIELDS_PRESERVED_EXACT_2008_ROUTE_NOT_SENT"},
]
new_closure_ids = {row["gap_id"] for row in new_closures}
closures = [row for row in closures if row["gap_id"] not in new_closure_ids] + new_closures
write_csv(HERE / "E0_REQUEST_CLOSURE_CRITERIA_V122.csv", closures)


deferred_audit = [
    {"audit_id": "DM122_01", "artifact_date": "2008", "artifact_or_rule": "Procedimiento específico de recompra", "term_or_mechanism": "modalidad diferida", "observed_definition_or_field": "Instrucción a Caja hasta cierre T+2; Caja informa T+3; Tesoro paga luego en BCRA", "relation_to_2008_target": "DIRECT_TARGET_RULE", "evidence_status": "EXACT_TERM_PROCEDURE_ONLY", "prohibited_inference": "No asignar TSA, CGA, FT, FTC, DVP ni formulario sin el registro técnico.", "source_id": "e0_argentina_rc_212_24_2008_recompra", "locator": "Anexo; puntos 2.1-2.3"},
    {"audit_id": "DM122_02", "artifact_date": "2008-01", "artifact_or_rule": "BCRA Comunicación B 9173", "term_or_mechanism": "CGA para FT/FTC", "observed_definition_or_field": "Archivo X-400/MCT; primera validación condicional y segunda etapa", "relation_to_2008_target": "CONTEMPORANEOUS_AVAILABLE_ROUTE", "evidence_status": "ROUTE_AVAILABLE_USAGE_UNPROVEN", "prohibited_inference": "No equiparar CGA con diferida ni validación con liquidación.", "source_id": "e0_bcra_b9173_cryl_cga_x400_2008", "locator": "Anexos I-III"},
    {"audit_id": "DM122_03", "artifact_date": "2017", "artifact_or_rule": "CVSA F-33914.01", "term_or_mechanism": "entrega diferida", "observed_definition_or_field": "Fecha de ejecución; límite de matching; Código Caja; emisor y receptor", "relation_to_2008_target": "RETROSPECTIVE_FIELD_SCHEMA", "evidence_status": "SCHEMA_ONLY_POST_TARGET", "prohibited_inference": "No afirmar edición o uso en 2008.", "source_id": "e0_cvsa_f33914_deferred_delivery_2017", "locator": "páginas PDF 1-2"},
    {"audit_id": "DM122_04", "artifact_date": "2017", "artifact_or_rule": "CVSA F-33915.01", "term_or_mechanism": "recepción diferida", "observed_definition_or_field": "Autorización receptora con campos espejo y matching", "relation_to_2008_target": "RETROSPECTIVE_COUNTERPART_SCHEMA", "evidence_status": "SCHEMA_ONLY_POST_TARGET", "prohibited_inference": "No tratar autorización en blanco como recepción ejecutada.", "source_id": "e0_cvsa_f33915_deferred_receipt_2017", "locator": "páginas PDF 1-2"},
    {"audit_id": "DM122_05", "artifact_date": "2020", "artifact_or_rule": "CVSA Comunicado 10290", "term_or_mechanism": "TSA + diferida", "observed_definition_or_field": "Archivos TSA hasta 19 h; subcuentas sólo admiten transferencias diferidas", "relation_to_2008_target": "POST_TARGET_CATEGORY_DISTINCTION", "evidence_status": "CHANNEL_AND_MODALITY_COEXIST", "prohibited_inference": "No convertir TSA en sinónimo de diferida ni proyectar el canje 2020 a 2008.", "source_id": "e0_cvsa_communication_10290_tsa_deferred_2020", "locator": "página PDF 2"},
    {"audit_id": "DM122_06", "artifact_date": "2023", "artifact_or_rule": "BYMA Instructivo NSC", "term_or_mechanism": "TSA + retiro de diferida/inmediata", "observed_definition_or_field": "TSA conserva formato; exige código de custodia; el NSC elimina tipos diferida/inmediata", "relation_to_2008_target": "POST_TARGET_METHOD_BREAK", "evidence_status": "DISTINCT_LAYERS_AND_REGIME_CHANGE", "prohibited_inference": "No retrotraer la regla NSC ni confundir ISIN con código de custodia.", "source_id": "e0_byma_nsc_tsa_modality_retirement_2023", "locator": "página PDF 3"},
]
write_csv(HERE / "E0_DEFERRED_MODALITY_EQUIVALENCE_AUDIT_V122.csv", deferred_audit)


crosswalk = [
    {"crosswalk_id": "ID122_01", "target_instrument": "BODEN 2012; U$S LIBOR 2012 1ra serie", "isin": "ARARGE034678", "historical_code": "5426", "code_label_in_source": "CÓDIGO", "primary_chain": "llamados 2008 por nombre/ISIN + RG 2418 y RG 2575 por denominación/código", "evidence_status": "EXACT_NAME_CHAIN_TWO_OFFICIAL_TABLES", "unresolved_element": "Confirmación institucional de que 5426 era Código Caja/CRyL operativo para esas fechas", "prohibited_inference": "No inferir recepción o liquidación."},
    {"crosswalk_id": "ID122_02", "target_instrument": "BODEN 2013; U$S LIBOR 2013 1ra serie", "isin": "ARARGE035709", "historical_code": "5427", "code_label_in_source": "CÓDIGO", "primary_chain": "llamados 2008 por nombre/ISIN + RG 2418 y RG 2575 por denominación/código", "evidence_status": "EXACT_NAME_CHAIN_TWO_OFFICIAL_TABLES", "unresolved_element": "Confirmación institucional de que 5427 era Código Caja/CRyL operativo para esas fechas", "prohibited_inference": "No inferir recepción o liquidación."},
    {"crosswalk_id": "ID122_03", "target_instrument": "Unidad vinculada al PIB denominada en pesos", "isin": "ARARGE03E147", "historical_code": "45698", "code_label_in_source": "CÓDIGO; corroboración oficial posterior: CAJA DE VALORES", "primary_chain": "llamados 2008 + RG 2418/RG 2575 + informe oficial 2017", "evidence_status": "EXACT_NAME_CHAIN_AND_POST_TARGET_CAJA_LABEL", "unresolved_element": "Tabla contemporánea ISIN-Código Caja y asiento objetivo", "prohibited_inference": "La corroboración posterior no prueba uso ni liquidación en 2008."},
    {"crosswalk_id": "ID122_04", "target_instrument": "Unidad vinculada al PIB en dólares; ley argentina", "isin": "ARARGE03E154", "historical_code": "45701", "code_label_in_source": "CÓDIGO", "primary_chain": "llamados 2008 por nombre/ISIN + RG 2418 y RG 2575 por denominación/código", "evidence_status": "EXACT_NAME_CHAIN_TWO_OFFICIAL_TABLES", "unresolved_element": "Confirmación institucional de que 45701 era Código Caja/CRyL operativo para esas fechas", "prohibited_inference": "No confundir variantes de cable/exterior ni inferir liquidación."},
    {"crosswalk_id": "ID122_05", "target_instrument": "BODEN 2012 cupón 15 separado", "isin": "ARARGE03G415", "historical_code": "N/D", "code_label_in_source": "NO LOCALIZADO", "primary_chain": "llamado/resultados strip 2009; búsquedas públicas por ISIN y denominación", "evidence_status": "PUBLIC_CODE_NOT_LOCATED", "unresolved_element": "Código Caja/CRyL propio de la subespecie", "prohibited_inference": "No heredar 5426 del BODEN 2012 principal."},
]
write_csv(HERE / "E0_SECURITY_IDENTIFIER_CROSSWALK_V122.csv", crosswalk)


settlement_stages = [
    {"stage_id": "ST122_01", "sequence": "1", "stage": "adjudicación", "producer": "Secretaría de Finanzas", "expected_record": "resultado publicado y comunicación de adjudicación", "asset_leg": "monto/especie adjudicados", "cash_leg": "precio adjudicado; aún no pagado", "evidence_status": "PUBLIC_RESULT_PRESERVED", "open_gap": "comunicación individual y expediente", "do_not_collapse_with": "entrega; recepción; pago"},
    {"stage_id": "ST122_02", "sequence": "2", "stage": "instrucción diferida", "producer": "depositante adjudicado / Caja", "expected_record": "instrucción por fecha, especie, código, cantidad y cuenta 0306/40000", "asset_leg": "orden de transferir", "cash_leg": "ninguna", "evidence_status": "PROCEDURE_TERM_ONLY", "open_gap": "formulario/archivo y edición 2008", "do_not_collapse_with": "matching o ejecución"},
    {"stage_id": "ST122_03", "sequence": "3", "stage": "matching/autorización", "producer": "depositantes emisor/receptor / Caja", "expected_record": "entrega y recepción coincidentes; fecha límite y estado", "asset_leg": "instrucciones emparejadas", "cash_leg": "ninguna", "evidence_status": "RETROSPECTIVE_SCHEMA_ONLY", "open_gap": "registro objetivo y regla 2008", "do_not_collapse_with": "recepción efectivamente asentada"},
    {"stage_id": "ST122_04", "sequence": "4", "stage": "cierre de recepción T+2", "producer": "Caja de Valores", "expected_record": "asiento de títulos recibidos/rechazados en 0306/40000", "asset_leg": "débito emisor y crédito fiduciario", "cash_leg": "ninguna", "evidence_status": "SCHEDULED_NOT_CONFIRMED", "open_gap": "asiento, lote y estado por especie", "do_not_collapse_with": "confirmación T+3"},
    {"stage_id": "ST122_05", "sequence": "5", "stage": "informe Caja T+3 10 h", "producer": "Caja de Valores", "expected_record": "detalle de transferencias recibidas remitido a Secretaría", "asset_leg": "confirmación de recepción", "cash_leg": "base para instruir pago", "evidence_status": "SCHEDULED_NOT_CONFIRMED", "open_gap": "mensaje, identificador y contenido", "do_not_collapse_with": "pago BCRA"},
    {"stage_id": "ST122_06", "sequence": "6", "stage": "pago T+3", "producer": "Tesoro / BCRA", "expected_record": "orden y débito/crédito en cuentas corrientes BCRA", "asset_leg": "conciliación con títulos recibidos", "cash_leg": "efectivo pagado", "evidence_status": "SCHEDULED_NOT_CONFIRMED", "open_gap": "orden, importe, moneda, estado y conciliación", "do_not_collapse_with": "acuse técnico"},
    {"stage_id": "ST122_07", "sequence": "paralela/condicional", "stage": "mensajería CRyL/CGA si aplicó", "producer": "Caja / entidad / BCRA-CRyL", "expected_record": "CGA, segunda validación, CG3 o fórmula papel", "asset_leg": "registro técnico de transferencia", "cash_leg": "ninguna por sí sola", "evidence_status": "AVAILABLE_ROUTE_USAGE_UNPROVEN", "open_gap": "equivalencia con modalidad diferida y lote objetivo", "do_not_collapse_with": "liquidación económica"},
    {"stage_id": "ST122_08", "sequence": "7", "stage": "conciliación y baja de deuda", "producer": "ONCP/DADP/TGN", "expected_record": "conciliación resultado-entrega-pago y registración de deuda", "asset_leg": "títulos recomprados/cancelados", "cash_leg": "pago conciliado", "evidence_status": "OPEN", "open_gap": "documento contable por ronda/especie", "do_not_collapse_with": "estimaciones fiscales agregadas"},
]
write_csv(HERE / "E0_CAJA_CRYL_SETTLEMENT_STAGE_MATRIX_V122.csv", settlement_stages)


assert len(catalog) == 287
assert len(census) == 88
assert len(ledger) == 125
assert len(breaks) == 79
assert len(channels) == 7
assert len(trace) == 73
assert len(responses) == 6
assert len(closures) == 8
assert len(system_map) == 6
assert len(authorities) == 10
assert len(negative_adequacy) == 14
assert len(producer_map) == 22
assert len(search_keys) == 50
assert len(attachments) == 7
assert len(version_chain) == 9
assert len(term_audit) == 8
assert len(cga_map) == 8
assert len(deferred_audit) == 6
assert len(crosswalk) == 5
assert len(settlement_stages) == 8


evidence_path = HERE / "HISTORICAL_EVIDENCE_COVERAGE_V122.csv"
evidence = read_csv(evidence_path)
for row in evidence:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            {
                "quality": "PRIMARY_BUYBACK_STRIP_EXACT_ACCOUNT_ROUTE_FOUR_HISTORICAL_CODES_AND_DEFERRED_FIELDS_PRESERVED",
                "gap": "Cuatro especies 2008 tienen código histórico oficial por denominación y la modalidad diferida tiene campos retrospectivos; falta confirmar la etiqueta Caja/CRyL, el código del strip y los registros ejecutados/pagados.",
                "next_action": "Presentar sólo con autorización expresa usando las claves V122; exigir tabla histórica ISIN-código, edición 2008 del procedimiento y asientos separados de matching, recepción y pago.",
            }
        )
write_csv(evidence_path, evidence)


queue_path = HERE / "HISTORICAL_SOURCE_QUEUE_V122.csv"
queue = read_csv(queue_path)
for row in queue:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            {
                "status": "INSTITUTIONAL_REQUEST_SECURITY_AND_DEFERRED_KEYS_READY_NOT_SENT",
                "why": "Seis fuentes primarias nuevas preservan cuatro códigos históricos, los campos de entrega/recepción diferida y la separación canal-modalidad; 73 objetos quedan trazados sin presentación ni respuesta.",
                "next_action": "Obtener autorización expresa, completar datos personales, presentar sólo los pedidos autorizados y conservar constancias.",
            }
        )
write_csv(queue_path, queue)


inherited = [
    {"script": "qa_v97.py", "pre_v122_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v122_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V97 exige que una fuente recuperada después permanezca sin ruta/hash."},
    *({"script": f"qa_v{i}.py", "pre_v122_result": "PASS", "post_v122_result": "PASS", "interpretation": "Compatible"} for i in (98, 100, 101, 102, 103, 104, 105, 106)),
    *({"script": f"qa_v{i}.py", "pre_v122_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v122_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "Congela un checkpoint o conteo anterior."} for i in range(107, 122)),
    {"script": "qa_v122.py", "pre_v122_result": "N/A", "post_v122_result": "PASS", "interpretation": "Códigos históricos, modalidad diferida, etapas separadas, claves y estados no enviados."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V122.csv", inherited)


for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    shutil.copyfile(AUDIT / f"{stem}_V121.csv", AUDIT / f"{stem}_V122.csv")

hash_rows = [row for row in read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V121.csv") if row["id"] not in new_ids]
for spec in source_specs:
    hash_rows.append(
        {"id": spec["id"], "archivo_local": spec["local"], "exists": "True", "sha_catalog": spec["sha256"], "sha_actual": spec["sha256"], "hash_ok": "True"}
    )
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V122.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V122.csv", hash_rows)


size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append(
        {
            "path": path.relative_to(REPO).as_posix(),
            "bytes": str(size),
            "mib": f"{size / 1048576:.6f}",
            "over_50_mib": str(size > 50 * 1048576),
            "over_100_mib": str(size > 100 * 1048576),
        }
    )
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V122.csv", size_rows)


physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V121.json").read_text(encoding="utf-8"))
completeness.update(
    {
        "checkpoint": "V122",
        "date": "2026-08-29",
        "state": "E0_FOUR_HISTORICAL_SECURITY_CODES_DEFERRED_MODALITY_FIELDS_PRESERVED_STRIP_CODE_OPEN_NOT_SENT",
        "numeric_v122_strict_changed": False,
        "master_catalog_entries": len(catalog),
        "physical_local_copies": physical,
        "physical_local_hash_ok": hash_ok,
        "binary_required_entries": len(catalog) - 4,
        "binary_required_preserved": physical,
        "e0_primary_sources_preserved": len(census),
        "e0_quality": "PRIMARY_BUYBACK_STRIP_EXACT_ACCOUNT_ROUTE_FOUR_HISTORICAL_CODES_AND_DEFERRED_FIELDS_PRESERVED",
        "sources_newly_preserved_v122": len(source_specs),
        "e0_primary_sources_newly_preserved_v122": len(source_specs),
        "pending_external_request_actions": 6,
        "e0_request_drafts": len(responses),
        "e0_request_traceability_rows": len(trace),
        "e0_request_closure_rules": len(closures),
        "e0_document_system_temporal_routes": len(system_map),
        "e0_archival_retention_authorities": len(authorities),
        "e0_negative_response_adequacy_controls": len(negative_adequacy),
        "e0_record_producer_system_rows": len(producer_map),
        "e0_request_search_keys": len(search_keys),
        "e0_request_attachment_rows": len(attachments),
        "e0_cryl_effective_version_chain_rows": len(version_chain),
        "e0_buyback_modality_term_audit_rows": len(term_audit),
        "e0_cryl_cga_record_map_rows": len(cga_map),
        "e0_deferred_modality_equivalence_audit_rows": len(deferred_audit),
        "e0_security_identifier_crosswalk_rows": len(crosswalk),
        "e0_caja_cryl_settlement_stage_rows": len(settlement_stages),
        "e0_fiscal_method_breaks_frozen": len(breaks),
        "e0_official_submission_channels_verified": len(channels),
        "e0_requests_submitted": 0,
        "e0_request_responses_received": 0,
        "e0_request_package_status": "DRAFT_NOT_SENT",
        "historical_workstream": "E0_FOUR_HISTORICAL_SECURITY_CODES_DEFERRED_MODALITY_FIELDS_PRESERVED_STRIP_CODE_OPEN_NOT_SENT",
    }
)
completeness.pop("numeric_v121_strict_changed", None)
completeness.pop("sources_newly_preserved_v121", None)
completeness.pop("e0_primary_sources_newly_preserved_v121", None)
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V122.json").write_text(
    json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)


backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V122 · códigos históricos y modalidad diferida delimitados"
old_backup = backup.read_text(encoding="utf-8-sig")
if marker not in old_backup:
    old_backup += (
        f"\n\n{marker}\n\n"
        "- Se preservaron seis fuentes oficiales: dos tablas AFIP, dos formularios Caja, el Comunicado CVSA 10290 y el instructivo NSC de BYMA.\n"
        "- Se localizaron códigos oficiales por denominación para cuatro especies 2008: 5426, 5427, 45698 y 45701; el código del strip ARARGE03G415 sigue abierto.\n"
        "- La evidencia posterior separa TSA como canal de la modalidad diferida y aporta campos de matching sin probar el formulario usado en 2008.\n"
        "- Los seis borradores incorporan 22 rutas productor-sistema, 50 claves técnicas, 7 adjuntos mínimos y 73 objetos trazados.\n"
        "- Todos los pedidos permanecen DRAFT_NOT_SENT; no hay plazos ni respuestas en curso.\n"
        "- Las fuentes E0 suben a 88; cifras fiscales y panel bancario permanecen sin cambios.\n"
    )
    backup.write_text(old_backup, encoding="utf-8")


def write_checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V122.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V122",
        "parent_checkpoint": "V121",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30,
        "strict_coverage_pct": STRICT,
        "closed_network_gate": "NO",
        "e0_primary_sources": len(census),
        "new_preserved_sources": len(source_specs),
        "new_primary_sources": len(source_specs),
        "fiscal_ledger_rows": len(ledger),
        "fiscal_method_breaks": len(breaks),
        "request_drafts": len(responses),
        "official_submission_channels": len(channels),
        "request_traceability_rows": len(trace),
        "request_closure_rules": len(closures),
        "document_system_temporal_routes": len(system_map),
        "archival_retention_authorities": len(authorities),
        "negative_response_adequacy_controls": len(negative_adequacy),
        "record_producer_system_rows": len(producer_map),
        "request_search_keys": len(search_keys),
        "request_attachment_rows": len(attachments),
        "cryl_effective_version_chain_rows": len(version_chain),
        "buyback_modality_term_audit_rows": len(term_audit),
        "cryl_cga_record_map_rows": len(cga_map),
        "deferred_modality_equivalence_audit_rows": len(deferred_audit),
        "security_identifier_crosswalk_rows": len(crosswalk),
        "caja_cryl_settlement_stage_rows": len(settlement_stages),
        "requests_submitted": 0,
        "responses_received": 0,
        "files": files,
    }
    (HERE / "MANIFEST_V122.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


write_checkpoint_manifest()


def build_tree(root: Path) -> str:
    lines = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix().casefold()):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        lines.append(path.relative_to(root).as_posix() + ("/" if path.is_dir() else ""))
    return "\n".join(lines) + "\n"


(REPO / "TREE.txt").write_text(build_tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(build_tree(CYCLE), encoding="utf-8")


global_manifest_path = CYCLE / "MANIFEST_SHA256.json"
global_files = []
for path in sorted(REPO.rglob("*"), key=lambda item: item.relative_to(REPO).as_posix().casefold()):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or path == global_manifest_path:
        continue
    global_files.append(
        {"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)}
    )
global_manifest = {
    "checkpoint": "V122",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT,
    "exact_entities": 30,
    "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical local copies with {hash_ok}/{physical} SHA-valid; six new primary security-code/deferred-modality sources preserved; six system-keyed requests drafted and none submitted.",
    "historical_workstream": "E0 four historical security codes and deferred-transfer fields preserved; strip code, exact 2008 form, settled asset leg and cash payment remain open; no request submitted",
    "file_count_excluding_manifest": len(global_files),
    "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V122 BUILD PASS")


