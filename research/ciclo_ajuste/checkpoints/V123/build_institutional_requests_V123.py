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
V122 = HERE.parent / "V122"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v123" / "binaries"
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
        "id": "e0_banco_columbia_codigo_caja_boden_strip_2009",
        "institution": "Banco Columbia S.A.",
        "title": "Estados contables al 30/06/2009 · Anexo A con Identificación Caja de Valores",
        "url": "https://secure.bancocolumbia.com.ar/web/Multimedios/Otros/6937.pdf?v=58",
        "file": "banco_columbia_estados_2009_codigo_caja.pdf",
        "publication": "2009-08-12",
        "period": "tenencias al 2009-06-30; contemporáneo al llamado del cupón separado",
        "type": "PDF bancario auditado · binario preservado",
        "families": "state_bcra;fiscal;debt;security_identifiers;Caja;historical_codes;strip_coupon",
        "breaks": "identificación de especie versus liquidación objetivo; denominación/fecha versus ISIN",
        "use": "USABLE_CONTEMPORANEOUS_CAJA_CODE_TABLE",
        "caveat": "La tabla identifica especies mantenidas por el banco; no prueba una entrega, recepción o pago de las recompras objetivo.",
        "verified": "64 páginas; página PDF 26 renderizada e inspeccionada visualmente; la columna Identificación Caja de Valores vincula BODEN 2012 cupón vto. 03/08/2009 con 5326.",
    },
    {
        "id": "e0_banco_patagonia_boden_strip_code_2009",
        "institution": "Banco Patagonia S.A.",
        "title": "Financial statements as of 30/06/2009 · Exhibit A securities identification",
        "url": "https://www.bancopatagonia.com.ar/relacionconinversores/english/docs/info_financiera_gestion/estados_contables/financial_statements_june_2009.pdf",
        "file": "banco_patagonia_estados_junio_2009.pdf",
        "publication": "2009-08-10",
        "period": "tenencias al 2009-06-30; corroboración bancaria contemporánea independiente",
        "type": "PDF bancario auditado · binario preservado",
        "families": "state_bcra;fiscal;debt;security_identifiers;historical_codes;strip_coupon",
        "breaks": "identificación contable versus Código Caja rotulado; tenencia bancaria versus liquidación objetivo",
        "use": "USABLE_CONTEMPORANEOUS_INDEPENDENT_STRIP_CODE_CORROBORATION",
        "caveat": "Corrobora la denominación y el código 5326, pero el encabezado dice Identification y no acredita por sí solo el tipo institucional del código ni la operación objetivo.",
        "verified": "81 páginas; página PDF 48 renderizada e inspeccionada visualmente; BODEN 2012 coupon 15 income and depreciation figura con identificación 5326.",
    },
    {
        "id": "e0_caja_sistema_transferencias_electronicas_manual",
        "institution": "Caja de Valores S.A.",
        "title": "Sistema de Transferencias Electrónicas · Manual Agentes y Sociedades de Bolsa",
        "url": "https://home.byma.com.ar/sba/descargas/manuales/sliq.pdf",
        "file": "caja_valores_sistema_transferencias_custodia_sliq.pdf",
        "publication": "2018-02-08",
        "period": "manual operativo sin fecha interna; PDF reexportado en 2018 y preservado vía archivo web",
        "type": "PDF operativo de Caja · binario archivado preservado",
        "families": "state_bcra;fiscal;debt;Caja;custody;deferred_transfer;immediate_transfer;matching;batch",
        "breaks": "definición operativa posterior/sin fecha interna versus vigencia 2008; modalidad versus ejecución objetivo",
        "use": "USABLE_RETROSPECTIVE_OPERATIONAL_DEFINITION_DATE_BOUNDARY_OPEN",
        "caveat": "Define inmediata/diferida, confirmación, matching y procesamiento nocturno, pero no demuestra que esta edición estuviera vigente en 2008.",
        "verified": "94 páginas; portada y páginas PDF 9-12 renderizadas e inspeccionadas visualmente; modalidades, fases, contrapartes, formularios y matching legibles.",
    },
    {
        "id": "e0_cnv_res_16189_recepcion_diferida_2009",
        "institution": "Comisión Nacional de Valores",
        "title": "Resolución 16.189 · formularios de Recepción Diferida y movimientos de Caja",
        "url": "https://www.cnv.gov.ar/descargas/RD/blob/8726491E-A033-4F6C-ABEF-17B3C8D8E0FE",
        "file": "cnv_resolucion_16189_2009_recepcion_diferida.pdf",
        "publication": "2009-08-20",
        "period": "operación y documentación de agosto de 2009; expediente originado por verificación de agosto de 2008",
        "type": "PDF regulatorio oficial · binario preservado",
        "families": "state_bcra;fiscal;debt;CNV;Caja;custody;deferred_receipt;form;movements",
        "breaks": "práctica 2009 versus vigencia exacta 2008; formulario presentado versus movimiento objetivo",
        "use": "USABLE_NEAR_CONTEMPORANEOUS_DEFERRED_FORM_PRACTICE",
        "caveat": "Prueba formularios numerados de Recepción Diferida y listados de movimientos en 2009; no prueba la edición vigente ni los registros de las recompras de 2008.",
        "verified": "2 páginas; página PDF 1 renderizada e inspeccionada visualmente; formularios 0102704/0102705, BODEN 2012 y listado de movimientos de Caja legibles.",
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
            "nota": f"V123 E0 fiscal: {spec['bytes']:,} bytes. {spec['verified']}",
        }
    )
write_csv(CATALOG, catalog)


census = [row for row in read_csv(V122 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V122.csv") if row["source_id"] not in new_ids]
for spec in source_specs:
    census.append(
        {
            "source_id": spec["id"], "institution": spec["institution"], "artifact": spec["title"],
            "url": spec["url"], "local_path": spec["local"], "sha256": spec["sha256"], "bytes": str(spec["bytes"]),
            "period_coverage": spec["period"], "variable_families": spec["families"], "primary_source": "YES",
            "preserved": "YES", "method_breaks": spec["breaks"], "use_status": spec["use"], "caveat": spec["caveat"],
        }
    )
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V123.csv", census)


ledger = read_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V123.csv")
breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V123.csv")
channels = read_csv(HERE / "CURRENT_OFFICIAL_SUBMISSION_CHANNELS_V123.csv")
trace = read_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V123.csv")
responses = read_csv(HERE / "E0_REQUEST_RESPONSE_REGISTER_V123.csv")
closures = read_csv(HERE / "E0_REQUEST_CLOSURE_CRITERIA_V123.csv")
system_map = read_csv(HERE / "E0_DOCUMENT_SYSTEM_TEMPORAL_MAP_V123.csv")
authorities = read_csv(HERE / "E0_ARCHIVAL_RETENTION_AUTHORITY_MATRIX_V123.csv")
negative_adequacy = read_csv(HERE / "E0_NEGATIVE_RESPONSE_ADEQUACY_V123.csv")
producer_map = read_csv(HERE / "E0_RECORD_PRODUCER_SYSTEM_MAP_V123.csv")
search_keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V123.csv")
attachments = read_csv(HERE / "E0_REQUEST_ATTACHMENT_MINIMUM_V123.csv")
version_chain = read_csv(HERE / "E0_CRYL_EFFECTIVE_VERSION_CHAIN_V123.csv")
term_audit = read_csv(HERE / "E0_BUYBACK_MODALITY_TERM_AUDIT_V123.csv")
cga_map = read_csv(HERE / "E0_CRYL_CGA_RECORD_MAP_V123.csv")


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
        "rule": "Usar 5326 para ARARGE03G415 y conservar 5426 sólo para el BODEN 2012 principal; no colapsar ambas especies.",
        "status": "RESOLVED_IDENTIFIER_LAYER_ONLY", "evidence": "Llamado strip 2009; Banco Columbia Anexo A; Banco Patagonia Exhibit A",
    },
    {
        "break_id": "bank_disclosure_identifier_not_target_settlement", "dimension": "phase",
        "problem": "Una tabla bancaria contemporánea puede identificar inequívocamente la especie sin documentar la entrega, recepción o liquidación de la recompra objetivo.",
        "rule": "Aceptar la tabla para el puente de identificadores y mantener abiertos los asientos de Caja, el matching y el pago BCRA.",
        "status": "FROZEN", "evidence": "Banco Columbia 30/06/2009; Banco Patagonia 30/06/2009",
    },
    {
        "break_id": "near_contemporaneous_deferred_form_not_exact_2008_edition", "dimension": "legal_time",
        "problem": "La CNV prueba formularios numerados de Recepción Diferida en agosto de 2009, pero no identifica la edición vigente durante las rondas de 2008.",
        "rule": "Usar 2009 como práctica cercana y solicitar la versión, vigencia o tabla de equivalencias exacta de 2008.",
        "status": "FROZEN", "evidence": "CNV Resolución 16.189 del 20/08/2009",
    },
]
break_ids = {row["break_id"] for row in new_breaks}
breaks = [row for row in breaks if row["break_id"] not in break_ids] + new_breaks
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V123.csv", breaks)


new_search_keys = [
    {"key_id": "SK123_44", "request_id": "REQ123_ECON", "key_group": "historical_code", "exact_key": "5426;5427;45698;45701;5326", "search_purpose": "cruzar resultados, especie recibida y registración de deuda", "source_or_basis": "llamados oficiales + tablas AFIP + Banco Columbia/Patagonia", "caveat": "Los cinco códigos identifican especies; no son por sí solos asientos liquidados."},
    {"key_id": "SK123_45", "request_id": "REQ123_BCRA", "key_group": "security_bridge", "exact_key": "ARARGE034678=5426;ARARGE035709=5427;ARARGE03E147=45698;ARARGE03E154=45701;ARARGE03G415=5326", "search_purpose": "pedir corroboración histórica ISIN-código de custodia/CRyL", "source_or_basis": "llamados oficiales + Banco Columbia/Patagonia", "caveat": "Puente público cerrado por denominación y fecha; sigue abierta la etiqueta CRyL y la liquidación."},
    {"key_id": "SK123_46", "request_id": "REQ123_CAJA", "key_group": "security_bridge", "exact_key": "ARARGE034678=5426;ARARGE035709=5427;ARARGE03E147=45698;ARARGE03E154=45701;ARARGE03G415=5326", "search_purpose": "confirmar vigencia y localizar asientos por Código Caja", "source_or_basis": "llamados oficiales + Anexo A Banco Columbia", "caveat": "La tabla rotula Identificación Caja de Valores, pero no contiene los asientos objetivo."},
    {"key_id": "SK123_47", "request_id": "REQ123_CAJA", "key_group": "form", "exact_key": "Recepción Diferida 0102704;Recepción Diferida 0102705;F-33914.01;F-33915.01", "search_purpose": "obtener versión vigente en 2008 o equivalencia", "source_or_basis": "CNV Res. 16.189/2009 + formularios CVSA 2017", "caveat": "La práctica está probada en 2009; la edición exacta de 2008 sigue abierta."},
    {"key_id": "SK123_48", "request_id": "REQ123_CAJA", "key_group": "matching", "exact_key": "proceso batch nocturno;almacenamiento provisorio;matching;fecha de ejecución;fecha límite de validez", "search_purpose": "buscar instrucción emparejada, procesada y conciliada", "source_or_basis": "Manual Sistema de Transferencias + formularios CVSA", "caveat": "La definición operativa y los campos no prueban el registro objetivo."},
    {"key_id": "SK123_49", "request_id": "REQ123_ECON", "key_group": "strip_code", "exact_key": "ARARGE03G415=5326;BODEN 2012 cupón 15;vto.03/08/2009", "search_purpose": "cruzar la subespecie con recepción, pago y baja de deuda", "source_or_basis": "llamado oficial 2009 + Banco Columbia/Patagonia", "caveat": "5326 no debe confundirse con 5426 del título principal."},
    {"key_id": "SK123_50", "request_id": "REQ123_BCRA", "key_group": "channel_modality", "exact_key": "TSA;modalidad diferida;batch nocturno;CGA;FT;FTC;Código CVSA;Código CRyL", "search_purpose": "pedir equivalencias históricas sin confundir canal, modalidad y estado", "source_or_basis": "B9173; Manual Caja; CVSA 10290; BYMA NSC 2023", "caveat": "El manual carece de fecha interna y no acredita uso en las rondas objetivo."},
]
new_key_ids = {row["key_id"] for row in new_search_keys}
search_keys = [row for row in search_keys if row["key_id"] not in new_key_ids] + new_search_keys
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V123.csv", search_keys)


new_trace = [
    {"trace_id": "TR123_068", "request_id": "REQ123_ECON", "institution": "Ministerio de Economía / Tesoro", "gap_id": "CL123_SECURITY_CODE", "requested_record": "Tabla o registro interno que corrobore los cinco códigos públicos", "period_or_date": "2008-2009", "identifiers": "cinco ISIN; 5426; 5427; 45698; 45701; 5326", "minimum_usable_fields": "ISIN; código; denominación; vigencia; sistema", "confidentiality_fallback": "certificación por especie", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR123_069", "request_id": "REQ123_CAJA", "institution": "Caja de Valores S.A.", "gap_id": "CL123_SECURITY_CODE", "requested_record": "Tabla histórica ISIN-Código Caja y vigencia de las cinco especies", "period_or_date": "2008-2009", "identifiers": "cinco ISIN; 5426; 5427; 45698; 45701; 5326", "minimum_usable_fields": "ISIN; Código Caja; subespecie; alta/baja; vigencia", "confidentiality_fallback": "confirmación institucional sin tenedores", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR123_070", "request_id": "REQ123_CAJA", "institution": "Caja de Valores S.A.", "gap_id": "CL123_DEFERRED_MODALITY", "requested_record": "Versión 2008 del formulario o procedimiento de entrega/recepción diferida", "period_or_date": "2008-2009", "identifiers": "F-33914.01; F-33915.01; modalidad diferida", "minimum_usable_fields": "edición; vigencia; campos; matching; reemplazo", "confidentiality_fallback": "manual o tabla de equivalencias", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR123_071", "request_id": "REQ123_CAJA", "institution": "Caja de Valores S.A.", "gap_id": "CL123_CAJA_ROUTE", "requested_record": "Instrucciones diferidas emparejadas y estado de ejecución", "period_or_date": "fechas T+2 2008-2009", "identifiers": "0306/40000; cinco ISIN; códigos 5426/5427/45698/45701/5326", "minimum_usable_fields": "fecha ejecución; límite matching; emisor/receptor; código; cantidad; estado", "confidentiality_fallback": "agregado por fecha/especie/estado", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR123_072", "request_id": "REQ123_BCRA", "institution": "BCRA / CRyL", "gap_id": "CL123_SECURITY_CODE", "requested_record": "Diccionario histórico entre ISIN, código de custodia/Caja y código CRyL", "period_or_date": "2008-2009", "identifiers": "cinco ISIN; 5426; 5427; 45698; 45701; 5326", "minimum_usable_fields": "identificador; tipo; especie; vigencia; sistema", "confidentiality_fallback": "tabla testada sin cuentas", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR123_073", "request_id": "REQ123_BCRA", "institution": "BCRA / CRyL", "gap_id": "CL123_DEFERRED_MODALITY", "requested_record": "Equivalencia histórica entre modalidad diferida, TSA/CGA y fórmula CRyL", "period_or_date": "2008-2009", "identifiers": "diferida; TSA; CGA; FT; FTC; DVP", "minimum_usable_fields": "canal; modalidad; formulario/archivo; estado; vigencia", "confidentiality_fallback": "manual o diccionario de códigos", "status": "DRAFT_NOT_SENT"},
]
new_trace_ids = {row["trace_id"] for row in new_trace}
trace = [row for row in trace if row["trace_id"] not in new_trace_ids] + new_trace
write_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V123.csv", trace)


new_closures = [
    {"gap_id": "CL123_SECURITY_CODE", "target_question": "¿Cuál era el Código Caja/CRyL de cada una de las cinco especies objetivo?", "minimum_positive_evidence": "Cadena pública contemporánea que vincule ISIN, denominación y Código Caja propio de cada especie; corroboración institucional deseable para vigencia y capa CRyL.", "minimum_negative_route_evidence": "N/A: el puente público se cerró; conservar búsqueda institucional sólo como corroboración y para los asientos.", "does_not_close": "La identificación de especie no demuestra matching, recepción, pago ni baja de deuda.", "initial_status": "PUBLIC_CROSSWALK_CLOSED_FIVE_CAJA_CODES_SETTLEMENT_STILL_OPEN_NOT_SENT"},
    {"gap_id": "CL123_DEFERRED_MODALITY", "target_question": "¿Qué formulario, archivo y estados operativos implementaron la modalidad diferida en 2008?", "minimum_positive_evidence": "Versión vigente en 2008 más instrucción/lote objetivo que separe canal, modalidad, matching, recepción y liquidación.", "minimum_negative_route_evidence": "Búsqueda reproducible por modalidad diferida, formularios 0102704/0102705, F-33914/F-33915, batch nocturno, TSA, CGA, FT/FTC/DVP, cuenta, fechas y repositorios históricos/sucesores.", "does_not_close": "Práctica regulatoria 2009; manual sin fecha interna reexportado en 2018; formulario 2017 en blanco; retiro de modalidades en 2023.", "initial_status": "OPEN_2009_PRACTICE_AND_OPERATIONAL_DEFINITION_PRESERVED_EXACT_2008_EDITION_NOT_SENT"},
]
new_closure_ids = {row["gap_id"] for row in new_closures}
closures = [row for row in closures if row["gap_id"] not in new_closure_ids] + new_closures
write_csv(HERE / "E0_REQUEST_CLOSURE_CRITERIA_V123.csv", closures)


deferred_audit = [
    {"audit_id": "DM123_01", "artifact_date": "2008", "artifact_or_rule": "Procedimiento específico de recompra", "term_or_mechanism": "modalidad diferida", "observed_definition_or_field": "Instrucción a Caja hasta cierre T+2; Caja informa T+3; Tesoro paga luego en BCRA", "relation_to_2008_target": "DIRECT_TARGET_RULE", "evidence_status": "EXACT_TERM_PROCEDURE_ONLY", "prohibited_inference": "No asignar TSA, CGA, FT, FTC, DVP ni formulario sin el registro técnico.", "source_id": "e0_argentina_rc_212_24_2008_recompra", "locator": "Anexo; puntos 2.1-2.3"},
    {"audit_id": "DM123_02", "artifact_date": "2008-01", "artifact_or_rule": "BCRA Comunicación B 9173", "term_or_mechanism": "CGA para FT/FTC", "observed_definition_or_field": "Archivo X-400/MCT; primera validación condicional y segunda etapa", "relation_to_2008_target": "CONTEMPORANEOUS_AVAILABLE_ROUTE", "evidence_status": "ROUTE_AVAILABLE_USAGE_UNPROVEN", "prohibited_inference": "No equiparar CGA con diferida ni validación con liquidación.", "source_id": "e0_bcra_b9173_cryl_cga_x400_2008", "locator": "Anexos I-III"},
    {"audit_id": "DM123_03", "artifact_date": "2017", "artifact_or_rule": "CVSA F-33914.01", "term_or_mechanism": "entrega diferida", "observed_definition_or_field": "Fecha de ejecución; límite de matching; Código Caja; emisor y receptor", "relation_to_2008_target": "RETROSPECTIVE_FIELD_SCHEMA", "evidence_status": "SCHEMA_ONLY_POST_TARGET", "prohibited_inference": "No afirmar edición o uso en 2008.", "source_id": "e0_cvsa_f33914_deferred_delivery_2017", "locator": "páginas PDF 1-2"},
    {"audit_id": "DM123_04", "artifact_date": "2017", "artifact_or_rule": "CVSA F-33915.01", "term_or_mechanism": "recepción diferida", "observed_definition_or_field": "Autorización receptora con campos espejo y matching", "relation_to_2008_target": "RETROSPECTIVE_COUNTERPART_SCHEMA", "evidence_status": "SCHEMA_ONLY_POST_TARGET", "prohibited_inference": "No tratar autorización en blanco como recepción ejecutada.", "source_id": "e0_cvsa_f33915_deferred_receipt_2017", "locator": "páginas PDF 1-2"},
    {"audit_id": "DM123_05", "artifact_date": "2020", "artifact_or_rule": "CVSA Comunicado 10290", "term_or_mechanism": "TSA + diferida", "observed_definition_or_field": "Archivos TSA hasta 19 h; subcuentas sólo admiten transferencias diferidas", "relation_to_2008_target": "POST_TARGET_CATEGORY_DISTINCTION", "evidence_status": "CHANNEL_AND_MODALITY_COEXIST", "prohibited_inference": "No convertir TSA en sinónimo de diferida ni proyectar el canje 2020 a 2008.", "source_id": "e0_cvsa_communication_10290_tsa_deferred_2020", "locator": "página PDF 2"},
    {"audit_id": "DM123_06", "artifact_date": "2023", "artifact_or_rule": "BYMA Instructivo NSC", "term_or_mechanism": "TSA + retiro de diferida/inmediata", "observed_definition_or_field": "TSA conserva formato; exige código de custodia; el NSC elimina tipos diferida/inmediata", "relation_to_2008_target": "POST_TARGET_METHOD_BREAK", "evidence_status": "DISTINCT_LAYERS_AND_REGIME_CHANGE", "prohibited_inference": "No retrotraer la regla NSC ni confundir ISIN con código de custodia.", "source_id": "e0_byma_nsc_tsa_modality_retirement_2023", "locator": "página PDF 3"},
    {"audit_id": "DM123_07", "artifact_date": "2009-08-20", "artifact_or_rule": "CNV Resolución 16.189", "term_or_mechanism": "formularios de Recepción Diferida", "observed_definition_or_field": "Formularios numerados 0102704 y 0102705; boleto BODEN 2012; listado de saldos y movimientos remitido por Caja", "relation_to_2008_target": "NEAR_CONTEMPORANEOUS_DOCUMENTED_PRACTICE", "evidence_status": "DEFERRED_FORM_PRACTICE_CONFIRMED_2009", "prohibited_inference": "No atribuir esos formularios ni su edición a las rondas de 2008.", "source_id": "e0_cnv_res_16189_recepcion_diferida_2009", "locator": "página PDF 1"},
    {"audit_id": "DM123_08", "artifact_date": "sin fecha interna; PDF 2018", "artifact_or_rule": "Caja · Sistema de Transferencias Electrónicas", "term_or_mechanism": "inmediata versus diferida", "observed_definition_or_field": "Inmediata en tiempo real; diferida por batch nocturno; alta, confirmación, almacenamiento provisorio, procesamiento, matching y formulario", "relation_to_2008_target": "RETROSPECTIVE_OPERATIONAL_DEFINITION", "evidence_status": "MECHANISM_DEFINED_DATE_BOUNDARY_OPEN", "prohibited_inference": "No afirmar vigencia 2008 ni ejecución objetivo sin versión fechada y registros.", "source_id": "e0_caja_sistema_transferencias_electronicas_manual", "locator": "páginas PDF 9-12"},
]
write_csv(HERE / "E0_DEFERRED_MODALITY_EQUIVALENCE_AUDIT_V123.csv", deferred_audit)


crosswalk = [
    {"crosswalk_id": "ID123_01", "target_instrument": "BODEN 2012; U$S LIBOR 2012 1ra serie", "isin": "ARARGE034678", "historical_code": "5426", "code_label_in_source": "IDENTIFICACIÓN CAJA DE VALORES", "primary_chain": "llamados 2008 por nombre/ISIN + AFIP 2007/2008 + Banco Columbia 30/06/2009 + Banco Patagonia 30/06/2009", "evidence_status": "CONTEMPORANEOUS_CAJA_CODE_CONFIRMED", "unresolved_element": "Asiento objetivo y eventual equivalencia CRyL", "prohibited_inference": "No inferir recepción o liquidación."},
    {"crosswalk_id": "ID123_02", "target_instrument": "BODEN 2013; U$S LIBOR 2013 1ra serie", "isin": "ARARGE035709", "historical_code": "5427", "code_label_in_source": "IDENTIFICACIÓN CAJA DE VALORES", "primary_chain": "llamados 2008 por nombre/ISIN + AFIP 2007/2008 + Banco Columbia 30/06/2009", "evidence_status": "CONTEMPORANEOUS_CAJA_CODE_CONFIRMED", "unresolved_element": "Asiento objetivo y eventual equivalencia CRyL", "prohibited_inference": "No inferir recepción o liquidación."},
    {"crosswalk_id": "ID123_03", "target_instrument": "Unidad vinculada al PIB denominada en pesos", "isin": "ARARGE03E147", "historical_code": "45698", "code_label_in_source": "IDENTIFICACIÓN CAJA DE VALORES", "primary_chain": "llamados 2008 por nombre/ISIN + AFIP 2007/2008 + Banco Columbia 30/06/2009", "evidence_status": "CONTEMPORANEOUS_CAJA_CODE_CONFIRMED", "unresolved_element": "Asiento objetivo y eventual equivalencia CRyL", "prohibited_inference": "La identificación no prueba uso ni liquidación en 2008."},
    {"crosswalk_id": "ID123_04", "target_instrument": "Unidad vinculada al PIB en dólares; ley argentina", "isin": "ARARGE03E154", "historical_code": "45701", "code_label_in_source": "IDENTIFICACIÓN CAJA DE VALORES", "primary_chain": "llamados 2008 por nombre/ISIN + AFIP 2007/2008 + Banco Columbia 30/06/2009", "evidence_status": "CONTEMPORANEOUS_CAJA_CODE_CONFIRMED", "unresolved_element": "Asiento objetivo y eventual equivalencia CRyL", "prohibited_inference": "No confundir variantes de cable/exterior ni inferir liquidación."},
    {"crosswalk_id": "ID123_05", "target_instrument": "BODEN 2012 cupón 15 separado", "isin": "ARARGE03G415", "historical_code": "5326", "code_label_in_source": "IDENTIFICACIÓN CAJA DE VALORES; IDENTIFICATION", "primary_chain": "llamado oficial 2009 por nombre/ISIN/vencimiento + Banco Columbia por denominación/vencimiento/código + Banco Patagonia por cupón 15/código", "evidence_status": "EXACT_CONTEMPORANEOUS_CAJA_CODE_TWO_BANK_DISCLOSURES", "unresolved_element": "Asiento objetivo y eventual equivalencia CRyL", "prohibited_inference": "No confundir 5326 del cupón separado con 5426 del BODEN 2012 principal ni inferir liquidación."},
]
write_csv(HERE / "E0_SECURITY_IDENTIFIER_CROSSWALK_V123.csv", crosswalk)


settlement_stages = [
    {"stage_id": "ST123_01", "sequence": "1", "stage": "adjudicación", "producer": "Secretaría de Finanzas", "expected_record": "resultado publicado y comunicación de adjudicación", "asset_leg": "monto/especie adjudicados", "cash_leg": "precio adjudicado; aún no pagado", "evidence_status": "PUBLIC_RESULT_PRESERVED", "open_gap": "comunicación individual y expediente", "do_not_collapse_with": "entrega; recepción; pago"},
    {"stage_id": "ST123_02", "sequence": "2", "stage": "instrucción diferida", "producer": "depositante adjudicado / Caja", "expected_record": "instrucción por fecha, especie, código, cantidad y cuenta 0306/40000", "asset_leg": "orden de transferir", "cash_leg": "ninguna", "evidence_status": "DIRECT_TARGET_TERM_PLUS_2009_FORM_PRACTICE", "open_gap": "formulario/archivo, edición exacta 2008 y registro objetivo", "do_not_collapse_with": "matching o ejecución"},
    {"stage_id": "ST123_03", "sequence": "3", "stage": "matching/autorización", "producer": "depositantes emisor/receptor / Caja", "expected_record": "entrega y recepción coincidentes; fecha límite y estado", "asset_leg": "instrucciones emparejadas", "cash_leg": "ninguna", "evidence_status": "OPERATIONAL_MECHANISM_DEFINED_TARGET_RECORD_OPEN", "open_gap": "registro objetivo y versión vigente 2008", "do_not_collapse_with": "recepción efectivamente asentada"},
    {"stage_id": "ST123_04", "sequence": "4", "stage": "cierre de recepción T+2", "producer": "Caja de Valores", "expected_record": "asiento de títulos recibidos/rechazados en 0306/40000", "asset_leg": "débito emisor y crédito fiduciario", "cash_leg": "ninguna", "evidence_status": "SCHEDULED_NOT_CONFIRMED", "open_gap": "asiento, lote y estado por especie", "do_not_collapse_with": "confirmación T+3"},
    {"stage_id": "ST123_05", "sequence": "5", "stage": "informe Caja T+3 10 h", "producer": "Caja de Valores", "expected_record": "detalle de transferencias recibidas remitido a Secretaría", "asset_leg": "confirmación de recepción", "cash_leg": "base para instruir pago", "evidence_status": "SCHEDULED_NOT_CONFIRMED", "open_gap": "mensaje, identificador y contenido", "do_not_collapse_with": "pago BCRA"},
    {"stage_id": "ST123_06", "sequence": "6", "stage": "pago T+3", "producer": "Tesoro / BCRA", "expected_record": "orden y débito/crédito en cuentas corrientes BCRA", "asset_leg": "conciliación con títulos recibidos", "cash_leg": "efectivo pagado", "evidence_status": "SCHEDULED_NOT_CONFIRMED", "open_gap": "orden, importe, moneda, estado y conciliación", "do_not_collapse_with": "acuse técnico"},
    {"stage_id": "ST123_07", "sequence": "paralela/condicional", "stage": "mensajería CRyL/CGA si aplicó", "producer": "Caja / entidad / BCRA-CRyL", "expected_record": "CGA, segunda validación, CG3 o fórmula papel", "asset_leg": "registro técnico de transferencia", "cash_leg": "ninguna por sí sola", "evidence_status": "AVAILABLE_ROUTE_USAGE_UNPROVEN", "open_gap": "equivalencia con modalidad diferida y lote objetivo", "do_not_collapse_with": "liquidación económica"},
    {"stage_id": "ST123_08", "sequence": "7", "stage": "conciliación y baja de deuda", "producer": "ONCP/DADP/TGN", "expected_record": "conciliación resultado-entrega-pago y registración de deuda", "asset_leg": "títulos recomprados/cancelados", "cash_leg": "pago conciliado", "evidence_status": "OPEN", "open_gap": "documento contable por ronda/especie", "do_not_collapse_with": "estimaciones fiscales agregadas"},
]
write_csv(HERE / "E0_CAJA_CRYL_SETTLEMENT_STAGE_MATRIX_V123.csv", settlement_stages)


assert len(catalog) == 291
assert len(census) == 92
assert len(ledger) == 125
assert len(breaks) == 81
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
assert len(deferred_audit) == 8
assert len(crosswalk) == 5
assert len(settlement_stages) == 8


evidence_path = HERE / "HISTORICAL_EVIDENCE_COVERAGE_V123.csv"
evidence = read_csv(evidence_path)
for row in evidence:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            {
                "quality": "PRIMARY_BUYBACK_STRIP_EXACT_ACCOUNT_ROUTE_FIVE_CONTEMPORANEOUS_CAJA_CODES_AND_DEFERRED_PRACTICE_PRESERVED",
                "gap": "Los cinco ISIN tienen puente público a Código Caja, incluido 5326 para el cupón separado; la práctica de Recepción Diferida está probada en 2009 y el mecanismo está definido, pero faltan la edición exacta de 2008 y los registros ejecutados/pagados.",
                "next_action": "Presentar sólo con autorización expresa usando las claves V123; pedir la versión vigente en 2008 y asientos separados de instrucción, matching, recepción y pago.",
            }
        )
write_csv(evidence_path, evidence)


queue_path = HERE / "HISTORICAL_SOURCE_QUEUE_V123.csv"
queue = read_csv(queue_path)
for row in queue:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            {
                "status": "INSTITUTIONAL_REQUEST_SETTLEMENT_AND_EXACT_2008_MODALITY_KEYS_READY_NOT_SENT",
                "why": "Cuatro fuentes nuevas cierran públicamente los cinco Códigos Caja y preservan práctica 2009 más definición operativa de la modalidad diferida; 73 objetos siguen trazados sin presentación ni respuesta.",
                "next_action": "Obtener autorización expresa, completar datos personales, presentar sólo los pedidos autorizados y conservar constancias.",
            }
        )
write_csv(queue_path, queue)


inherited = [
    {"script": "qa_v97.py", "pre_v123_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v123_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V97 exige que una fuente recuperada después permanezca sin ruta/hash."},
    *({"script": f"qa_v{i}.py", "pre_v123_result": "PASS", "post_v123_result": "PASS", "interpretation": "Compatible"} for i in (98, 100, 101, 102, 103, 104, 105, 106)),
    *({"script": f"qa_v{i}.py", "pre_v123_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v123_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "Congela un checkpoint o conteo anterior."} for i in range(107, 123)),
    {"script": "qa_v123.py", "pre_v123_result": "N/A", "post_v123_result": "PASS", "interpretation": "Cinco Códigos Caja, práctica diferida, etapas separadas, claves y estados no enviados."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V123.csv", inherited)


for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    shutil.copyfile(AUDIT / f"{stem}_V122.csv", AUDIT / f"{stem}_V123.csv")

hash_rows = [row for row in read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V122.csv") if row["id"] not in new_ids]
for spec in source_specs:
    hash_rows.append(
        {"id": spec["id"], "archivo_local": spec["local"], "exists": "True", "sha_catalog": spec["sha256"], "sha_actual": spec["sha256"], "hash_ok": "True"}
    )
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V123.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V123.csv", hash_rows)


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
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V123.csv", size_rows)


physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V122.json").read_text(encoding="utf-8"))
completeness.update(
    {
        "checkpoint": "V123",
        "date": "2026-08-29",
        "state": "E0_FIVE_CONTEMPORANEOUS_CAJA_CODES_DEFERRED_2009_PRACTICE_PRESERVED_EXACT_2008_EDITION_OPEN_NOT_SENT",
        "numeric_v123_strict_changed": False,
        "master_catalog_entries": len(catalog),
        "physical_local_copies": physical,
        "physical_local_hash_ok": hash_ok,
        "binary_required_entries": len(catalog) - 5,
        "binary_required_preserved": physical,
        "e0_primary_sources_preserved": len(census),
        "e0_quality": "PRIMARY_BUYBACK_STRIP_EXACT_ACCOUNT_ROUTE_FIVE_CONTEMPORANEOUS_CAJA_CODES_AND_DEFERRED_PRACTICE_PRESERVED",
        "sources_newly_preserved_v123": len(source_specs),
        "e0_primary_sources_newly_preserved_v123": len(source_specs),
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
        "historical_workstream": "E0_FIVE_CONTEMPORANEOUS_CAJA_CODES_DEFERRED_2009_PRACTICE_PRESERVED_EXACT_2008_EDITION_OPEN_NOT_SENT",
    }
)
completeness.pop("numeric_v121_strict_changed", None)
completeness.pop("sources_newly_preserved_v121", None)
completeness.pop("e0_primary_sources_newly_preserved_v121", None)
completeness.pop("numeric_v122_strict_changed", None)
completeness.pop("sources_newly_preserved_v122", None)
completeness.pop("e0_primary_sources_newly_preserved_v122", None)
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V123.json").write_text(
    json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)


backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V123 · cinco Códigos Caja y práctica diferida contemporánea"
old_backup = backup.read_text(encoding="utf-8-sig")
if marker not in old_backup:
    old_backup += (
        f"\n\n{marker}\n\n"
        "- Se preservaron cuatro fuentes primarias nuevas: estados contables de Banco Columbia y Banco Patagonia, el manual de transferencias de Caja y la Resolución CNV 16.189.\n"
        "- Los cinco ISIN objetivo tienen ahora puente público a Código Caja: 5426, 5427, 45698, 45701 y 5326; este último corresponde al cupón 15 separado ARARGE03G415.\n"
        "- La CNV prueba formularios numerados de Recepción Diferida en 2009 y el manual define matching y procesamiento nocturno; la edición exacta vigente en 2008 sigue abierta.\n"
        "- Los seis borradores incorporan 22 rutas productor-sistema, 50 claves técnicas, 7 adjuntos mínimos y 73 objetos trazados.\n"
        "- Todos los pedidos permanecen DRAFT_NOT_SENT; no hay plazos ni respuestas en curso.\n"
        "- Las fuentes E0 suben a 92; cifras fiscales y panel bancario permanecen sin cambios.\n"
    )
    backup.write_text(old_backup, encoding="utf-8")


def write_checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V123.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V123",
        "parent_checkpoint": "V122",
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
    (HERE / "MANIFEST_V123.json").write_text(
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
    "checkpoint": "V123",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT,
    "exact_entities": 30,
    "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical local copies with {hash_ok}/{physical} SHA-valid; four new primary Caja-code/deferred-practice sources preserved; six system-keyed requests drafted and none submitted.",
    "historical_workstream": "E0 five contemporaneous Caja codes and 2009 deferred-receipt practice preserved; exact 2008 edition, settled asset leg and cash payment remain open; no request submitted",
    "file_count_excluding_manifest": len(global_files),
    "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V123 BUILD PASS")


