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
PARENT = HERE.parent / "V134"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v135" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


SOURCES = [
    {
        "id": "e0_cgn_cuenta_inversion_2008_tomo_ii_tgn_system_files",
        "filename": "cgn_cuenta_inversion_2008_tomo_ii.pdf",
        "institution": "Contaduría General de la Nación / Tesorería General de la Nación",
        "title": "Cuenta de Inversión 2008 · Tomo II · archivos de instrucciones y movimientos BCRA",
        "url": "https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/archivos/tomoii.pdf",
        "publication": "2009",
        "period": "2008",
        "code": "Tomo II; pp.177-178 impresas; TGN; BCRA",
        "type": "PDF oficial · binario preservado",
        "bytes": 3450121,
        "sha256": "a4047cec54c88efeff97d5f6602c45277cd4e813c71f3df1d8bab45dd40594ae",
        "families": "TGN;BCRA;payment_instruction_file;bank_movement_file;balance_file",
        "breaks": "capacidad general del sistema versus archivo asociado a cada C-41 objetivo",
        "use": "USABLE_2008_PAYMENT_SYSTEM_RECORD_CLASSES",
        "caveat": "Prueba clases de archivos operativas en 2008; no individualiza 71597, 152677 ni 2876.",
        "note": "V135 E0: páginas 178-180 físicas verificadas visualmente; TGN enviaba instrucciones y recibía movimientos/saldos por enlace con BCRA.",
    },
    {
        "id": "e0_cgn_tgn_disposicion_conjunta_47_10_2008_external_payments",
        "filename": "cgn_tgn_disposicion_conjunta_47_10_2008_pagos_exterior.html",
        "institution": "Contaduría General de la Nación / Tesorería General de la Nación",
        "title": "Disposición Conjunta CGN 47/2008 y TGN 10/2008 · pagos al exterior",
        "url": "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/2008/adisp47.htm",
        "publication": "2008-10-14",
        "period": "2008",
        "code": "Disposición Conjunta 47/2008 y 10/2008; SAF 355/356; C-41",
        "type": "HTML oficial · captura preservada",
        "bytes": 10869,
        "sha256": "785381b2ae7ce14970b6f609264ba6a06a05e07aebd3645bcf163a2a49370874",
        "families": "C41;external_payment;BCRA;BNA;SIDIF;exchange_rate;beneficiary",
        "breaks": "regla contemporánea condicional versus atribución de pago exterior al target",
        "use": "USABLE_EXACT_2008_EXTERNAL_PAYMENT_SCHEMA_CONDITIONAL",
        "caveat": "No está probado que las tres C-41 objetivo fueran pagos al exterior.",
        "note": "V135 E0: regla contemporánea exacta para SAF 355/356; identifica nota TGN, beneficiario exterior, banco, cuenta, moneda, cambio y número SIDIF.",
    },
    {
        "id": "e0_cgn_circular_34_1997_sdpgb_paid_beneficiary_schema",
        "filename": "cgn_circular_34_1997_archivo_pagado_beneficiario.html",
        "institution": "Contaduría General de la Nación",
        "title": "Anexo Circular CGN 34/97 · archivo Pagado a Beneficiarios/Deducciones",
        "url": "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/1997/cir34a.htm",
        "publication": "1997",
        "period": "1997",
        "code": "SDPGBXXX.CON; P/R/A; RN/CH/TR/TI/NS",
        "type": "HTML oficial · captura preservada",
        "bytes": 23844,
        "sha256": "d4019e3d1fb5ed2a426ab729e5c2512ff23a7eabc52d41fd910a0ae0a56fdd64",
        "families": "SIDIF;SDPGB;beneficiary;payment_state;bank;account;payment_medium",
        "breaks": "esquema histórico de salida versus conservación o sucesor exacto en 2008",
        "use": "USABLE_EXACT_PAYMENT_STATE_OUTPUT_SCHEMA_REFERENCE",
        "caveat": "La continuidad literal del nombre de archivo hasta 2008 no está demostrada; pedir SDPGB o sucesor equivalente.",
        "note": "V135 E0: define campos y códigos capaces de distinguir pagado, rechazado y anulado por OB SIDIF y beneficiario.",
    },
    {
        "id": "e0_tgn_circular_7_1997_daily_paid_files",
        "filename": "tgn_circular_7_1997_pagado_diario.html",
        "institution": "Tesorería General de la Nación",
        "title": "Circular TGN 7/97 · información del pagado diario",
        "url": "https://www.economia.gob.ar/digesto/circulares/tgn/1997/cirtgn07.htm",
        "publication": "1997",
        "period": "1997",
        "code": "Circular TGN 7/97; TRANSAF/SIDIF; SDPAG; SDPGB; 19:30",
        "type": "HTML oficial · captura preservada",
        "bytes": 3362,
        "sha256": "b24b54c462369508e47ead79c87b11618ac7796c581b3b5775658fdc6a40105e",
        "families": "TGN;TRANSAF;SIDIF;SDPAG;SDPGB;payment;annulment;rejection",
        "breaks": "transmisión diaria histórica versus retención/consulta target en 2008",
        "use": "USABLE_DAILY_PAYMENT_OUTPUT_AUTHORITY_REFERENCE",
        "caveat": "Prueba la salida diaria en 1997, no el resultado de las tres órdenes de 2008.",
        "note": "V135 E0: los archivos diarios SDPAG y SDPGB contenían pagos, anulaciones y rechazos procesados.",
    },
    {
        "id": "e0_economia_digesto_chapter_3_tgn_index",
        "filename": "economia_digesto_capitulo_3_indice.html",
        "institution": "Ministerio de Economía",
        "title": "Digesto de Administración Financiera · Capítulo III · índice TGN",
        "url": "https://www.economia.gob.ar/digesto/capi3.htm",
        "publication": "s/f; consulta 2026-08-30",
        "period": "1995-2000; consulta 2026",
        "code": "Capítulo III; Circular TGN 7/97",
        "type": "HTML oficial · captura preservada",
        "bytes": 40882,
        "sha256": "52d810ec5efffaaf3fbef071e2683648dcfce2398553a10ec5f64ad6d4142ea2",
        "families": "normative_index;TGN;circular_7_1997;provenance",
        "breaks": "índice normativo versus contenido y aplicación temporal",
        "use": "USABLE_OFFICIAL_PROVENANCE_INDEX",
        "caveat": "El índice autentica y describe la circular; el contenido operativo se toma de la circular preservada.",
        "note": "V135 E0: índice oficial que enlaza y describe la Circular TGN 7/97 como información del pagado diario.",
    },
    {
        "id": "e0_minplan_resolution_1522_2006_comdoc_custody",
        "filename": "minplan_resolucion_1522_2006_comdoc_custodia.html",
        "institution": "Ministerio de Planificación Federal, Inversión Pública y Servicios",
        "title": "Resolución MINPLAN 1522/2006 actualizada · custodia, remitos y reconstrucción COMDOC",
        "url": "https://www.argentina.gob.ar/normativa/nacional/norma-119314/actualizacion",
        "publication": "2006-04-27; actualización 2007",
        "period": "2006-2007",
        "code": "Resolución 1522/2006; art.34 mod. Res.971/2007; COMDOC",
        "type": "HTML oficial · captura preservada",
        "bytes": 93449,
        "sha256": "fda42ee250f8989a97122e38ef7c7e4a3527e1de46afeeb9696dceb2ed04f0e9",
        "families": "COMDOC;custody;remittance;folios;annexes;loss_search;reconstruction",
        "breaks": "regla MINPLAN contemporánea versus norma aplicable al custodio Economía target",
        "use": "USABLE_CONTEMPORANEOUS_COMDOC_CUSTODY_COMPARATOR",
        "caveat": "No se traslada automáticamente a Economía/ONCP; sirve para formular campos de custodia y reconstrucción verificables.",
        "note": "V135 E0: documenta remitos, cuerpos, anexos, último folio, área depositaria, búsqueda intensiva y reconstrucción certificada.",
    },
    {
        "id": "e0_debt_joint_resolution_216_26_2008_instruction_chain",
        "filename": "deuda_resolucion_conjunta_216_26_2008_comdoc_instruccion.html",
        "institution": "Secretaría de Hacienda / Secretaría de Finanzas",
        "title": "Resolución Conjunta 216/2008 y 26/2008 · instrucción y registro de títulos de deuda",
        "url": "https://www.argentina.gob.ar/normativa/nacional/norma-144186/texto",
        "publication": "2008-06-27",
        "period": "2008",
        "code": "Resolución Conjunta 216/2008 y 26/2008; art.5; COMDOC; SIGADE",
        "type": "HTML oficial · captura preservada",
        "bytes": 59049,
        "sha256": "f040e86ae5a1aa18ce11467d70b1559bb2a820303ad0912aab6c159fd280ab47",
        "families": "public_debt;ONCP;TGN;instruction_note;COMDOC;SIGADE;Caja",
        "breaks": "procedimiento de bonos de consolidación versus recompra target",
        "use": "USABLE_2008_DEBT_RECORD_CHAIN_COMPARATOR",
        "caveat": "No demuestra equivalencia con la recompra BODEN; sólo prueba clases documentales contemporáneas de otra operatoria de deuda.",
        "note": "V135 E0: ONCP/TGN podían emitir nota conjunta, reporte COMDOC, archivo de datos y constancia de aceptación/registro SIGADE.",
    },
    {
        "id": "e0_hcdn_historic_plenary_index_negative_control",
        "filename": "hcdn_indice_reuniones_historicas.html",
        "institution": "Honorable Cámara de Diputados de la Nación",
        "title": "Índice histórico de versiones taquigráficas y reuniones plenarias",
        "url": "https://www4.hcdn.gov.ar/sesionesxml/reuniones.php",
        "publication": "consulta 2026-08-30",
        "period": "histórico hasta período 133; consulta 2026",
        "code": "Versiones Taquigráficas; reuniones; sumarios",
        "type": "HTML oficial · captura preservada",
        "bytes": 3653023,
        "sha256": "ead063451f983ba1eff810c28dd1330c968684470a73aca8181226c2d106df3b",
        "families": "parliamentary_archive;plenary_index;negative_control;OV",
        "breaks": "índice público de sesiones versus inventario interno de expediente OV",
        "use": "USABLE_PARLIAMENTARY_PUBLIC_INDEX_NEGATIVE_CONTROL",
        "caveat": "No hallar variantes de OV 366/09 u OV 44/10 en este índice no prueba ausencia del fondo histórico.",
        "note": "V135 E0: búsqueda exacta de variantes de ambos OV sin coincidencia; control negativo limitado al índice público preservado.",
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
    return text.replace("V134", "V135").replace("v134", "v135")


def clone_parent() -> None:
    skip = {"build_e0_finddoc_c41_v134.py", "qa_v134.py", "MANIFEST_V134.json", "INHERITED_QA_STATUS_V134.csv"}
    for source in PARENT.iterdir():
        if not source.is_file() or source.name in skip or source.name.startswith("HANDOVER_PROXIMA_SESION"):
            continue
        target = HERE / source.name.replace("V134", "V135")
        target.write_text(bump(source.read_text(encoding="utf-8-sig")), encoding="utf-8")


clone_parent()

for source in SOURCES:
    path = BIN / source["filename"]
    assert path.is_file() and path.stat().st_size == source["bytes"], path
    assert sha256(path) == source["sha256"], path
    source["local"] = "/" + path.relative_to(REPO).as_posix()

source_ids = {source["id"] for source in SOURCES}

# Catálogo maestro, censo E0 y proveniencia.
catalog = [row for row in read_csv(CATALOG) if row["id"] not in source_ids]
for source in SOURCES:
    catalog.append({
        "id": source["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": source["institution"],
        "titulo": source["title"], "url_original": source["url"], "archivo_local": source["local"],
        "fecha_descarga": "2026-08-30", "fecha_publicacion": source["publication"],
        "codigo_serie": source["code"], "periodo_utilizado": source["period"], "tipo": source["type"],
        "sha256": source["sha256"], "nota": source["note"],
    })
assert len(catalog) == 377 and len({row["id"] for row in catalog}) == 377
write_csv(CATALOG, catalog)

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V135.csv"
census = [row for row in read_csv(census_path) if row["source_id"] not in source_ids]
for source in SOURCES:
    census.append({
        "source_id": source["id"], "institution": source["institution"], "artifact": source["title"],
        "url": source["url"], "local_path": source["local"], "sha256": source["sha256"],
        "bytes": str(source["bytes"]), "period_coverage": source["period"],
        "variable_families": source["families"], "primary_source": "YES", "preserved": "YES",
        "method_breaks": source["breaks"], "use_status": source["use"], "caveat": source["caveat"],
    })
assert len(census) == 137 and len({row["source_id"] for row in census}) == 137
write_csv(census_path, census)

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V135.csv"
provenance = [row for row in read_csv(provenance_path) if row["source_id"] not in source_ids]
for source in SOURCES:
    provenance.append({
        "source_id": source["id"], "original_url": source["url"], "retrieval_url": source["url"],
        "capture_timestamp": "20260830", "cdx_digest": "N/A_DIRECT_OFFICIAL", "local_path": source["local"],
        "sha256": source["sha256"], "bytes": str(source["bytes"]),
        "provenance_note": "Descarga directa oficial preservada y hasheada en V135; páginas PDF relevantes renderizadas cuando correspondió.",
    })
assert len(provenance) == 40
write_csv(provenance_path, provenance)

# FindDoc/COMDOC: capacidad, salida y control histórico separados del target.
finddoc = [
    {"row_id": "FD134_01", "evidence_type": "DESIGN_SPEC", "target": "Consulta pública FindDoc", "date": "2011", "output_schema": "número o patrón; hoja de ruta; ubicación", "result": "El ciudadano podía conocer ruta y ubicación.", "source_id": "e0_agenda_digital_finddoc_comdoc_architecture", "status": "CAPABILITY_PROVED", "permitted_inference": "FindDoc era el índice público competente para metadatos de ruta.", "forbidden_inference": "FindDoc publicaba el cuerpo completo."},
    {"row_id": "FD134_02", "evidence_type": "DESIGN_SPEC", "target": "Hoja de ruta", "date": "2011", "output_schema": "origen; destino; fecha de envío; fecha de recepción", "result": "Campos explícitos y movimientos desde ingreso en COMDOC.", "source_id": "e0_agenda_digital_finddoc_comdoc_architecture", "status": "OUTPUT_FIELDS_PROVED", "permitted_inference": "Una salida target permitiría reconstruir custodia temporal.", "forbidden_inference": "Los movimientos prueban contenido o pago."},
    {"row_id": "FD134_03", "evidence_type": "ARCHITECTURE", "target": "COMDOC3→FindDoc→Internet", "date": "2011", "output_schema": "COMDOC3/PostgreSQL; importador; FindDoc/MySQL en DMZ; usuario Internet", "result": "Separación técnica entre sistema interno e índice público.", "source_id": "e0_agenda_digital_finddoc_comdoc_architecture", "status": "ARCHITECTURE_PROVED", "permitted_inference": "La caída de FindDoc no implica pérdida de la base COMDOC interna.", "forbidden_inference": "La base interna continúa disponible sin verificación administrativa."},
    {"row_id": "FD134_04", "evidence_type": "HISTORIC_QUERY_CONTROL", "target": "S01:0130656/2008", "date": "2013-03-05", "output_schema": "estado; fecha del último pase; ubicación", "result": "En trámite; desde 11/06/2012 en Gabinete de la Subsecretaría de Obras Públicas.", "source_id": "e0_agn_informe_254_2013_finddoc_control", "status": "HISTORIC_QUERY_OPERATIONAL_CONTROL", "permitted_inference": "El endpoint entregaba datos útiles para un S01 de 2008 en 2013.", "forbidden_inference": "El expediente objetivo tuvo igual ruta o estado."},
    {"row_id": "FD134_05", "evidence_type": "TARGET_STATUS", "target": "S01:0342455/2008", "date": "2026-08-30", "output_schema": "origen; destino; fechas; ubicación esperables", "result": "Endpoint legado no operativo; consulta target no ejecutada.", "source_id": "e0_economia_consulta_expedientes_comdoc_gde;e0_agenda_digital_finddoc_comdoc_architecture;e0_agn_informe_254_2013_finddoc_control", "status": "TARGET_QUERY_UNEXECUTED_ADMINISTRATIVE_EXPORT_REQUIRED", "permitted_inference": "Pedir exportación o consulta administrativa exacta de la hoja de ruta.", "forbidden_inference": "Sin resultado o expediente inexistente."},
]
write_csv(HERE / "E0_COMDOC_FINDDOC_CAPABILITY_V135.csv", finddoc)

comdoc_path = HERE / "E0_COMDOC_LEGACY_QUERY_ROUTE_V135.csv"
comdoc = read_csv(comdoc_path)[:2]
comdoc.extend([
    {"row_id": "CD134_03", "target": "FindDoc public output", "official_rule": "La consulta pública mostraba hoja de ruta y ubicación con origen, destino y fechas", "published_endpoint": "http://expedientes.mecon.gov.ar/finddoc2/finddoc/VerExpediente", "test_date": "2011 design specification", "test_result": "OUTPUT_SCHEMA_PROVED", "body_query_executed": "NOT_APPLICABLE", "source_id": "e0_agenda_digital_finddoc_comdoc_architecture", "status": "ROUTE_METADATA_NOT_BODY", "permitted_inference": "La salida esperable es trazabilidad de pases.", "forbidden_inference": "La consulta reemplaza una copia del cuerpo."},
    {"row_id": "CD134_04", "target": "S01:0130656/2008", "official_rule": "AGN usó VerExpediente para consultar un S01/2008", "published_endpoint": "http://expedientes.mecon.gov.ar/finddoc2/finddoc/VerExpediente", "test_date": "2013-03-05", "test_result": "HISTORIC_QUERY_RETURNED_STATUS_AND_LOCATION", "body_query_executed": "CONTROL_ONLY", "source_id": "e0_agn_informe_254_2013_finddoc_control", "status": "HISTORIC_OPERATIONAL_CONTROL", "permitted_inference": "El servicio era operativo y útil en 2013.", "forbidden_inference": "El control responde por S01:0342455/2008."},
    {"row_id": "CD134_05", "target": "S01:0342455/2008", "official_rule": "Consulta sustitutiva por Dirección de Información Ciudadana/administradores COMDOC", "published_endpoint": "ciudadano@mecon.gov.ar; 0810-333-6326; Balcarce 186 piso 1 oficina 140", "test_date": "2026-08-30", "test_result": "CHANNEL_IDENTIFIED_NOT_CONTACTED", "body_query_executed": "NO", "source_id": "e0_economia_consulta_expedientes_comdoc_gde", "status": "ADMINISTRATIVE_ROUTE_READY_DRAFT_NOT_SENT", "permitted_inference": "Existe vía oficial alternativa para pedir la consulta.", "forbidden_inference": "El pedido fue presentado o contestado."},
])
write_csv(comdoc_path, comdoc)

# La C-41 es una orden; el pago requiere procesamiento y trazas posteriores.
c41_chain = [
    {"stage_id": "CP134_01", "stage": "C41_ISSUED", "record": "Formulario C-41 Orden de Pago", "required_or_visible_fields": "vencimiento contractual original; devengado; beneficiario/observaciones según operatoria", "execution_meaning": "Orden emitida", "source_id": "e0_cgn_circular_2_1997_c41_due_date", "target_status": "THREE_2008_IDS_VISIBLE_ONLY_AS_ANEXO_K_REFERENCES", "permitted_inference": "Los SIDIF 71597, 152677 y 2876 son localizadores de órdenes.", "forbidden_inference": "La orden fue pagada."},
    {"stage_id": "CP134_02", "stage": "C41_PROCESSING", "record": "C-41 presentada/procesada por CGN", "required_or_visible_fields": "crédito; cuota; conformidad", "execution_meaning": "Puede ser rechazada por insuficiencia", "source_id": "e0_cgn_circular_6_1995_c41_tgn", "target_status": "TARGET_BODIES_NOT_PUBLICLY_LOCATED", "permitted_inference": "Hace falta estado de procesamiento por número SIDIF.", "forbidden_inference": "La mera numeración prueba conformidad."},
    {"stage_id": "CP134_03", "stage": "TGN_PREPAYMENT", "record": "C-41 conformada remitida a TGN", "required_or_visible_fields": "formulario conformado; remisión", "execution_meaning": "Se envía 'a efectos de su pago'", "source_id": "e0_cgn_circular_6_1995_c41_tgn", "target_status": "OPEN", "permitted_inference": "Conformidad y pago son etapas separables.", "forbidden_inference": "Remisión a TGN equivale a débito o crédito."},
    {"stage_id": "CP134_04", "stage": "EXTERNAL_PAYMENT_INSTRUCTION", "record": "C-41 más nota a TGN", "required_or_visible_fields": "beneficiario; banco destino; cuenta; SIDIF; moneda; tipo de cambio; divisas; un beneficiario por orden", "execution_meaning": "Instrucción suficientemente individualizada", "source_id": "e0_cgn_circular_13_2002_external_payments_c41", "target_status": "APPLICABILITY_TO_TARGET_NOT_PROVED", "permitted_inference": "Pedir nota e instrucción asociadas si la operatoria fue exterior.", "forbidden_inference": "Las órdenes target fueron pagos al exterior."},
    {"stage_id": "CP134_05", "stage": "BANK_DEBIT", "record": "Débito bancario", "required_or_visible_fields": "banco; cuenta; importe; fecha; documento original", "execution_meaning": "Movimiento monetario posterior a la orden", "source_id": "e0_cgn_circular_22_2004_c55_bank_debit", "target_status": "NO_TARGET_DEBIT_LOCATED", "permitted_inference": "El débito es una evidencia distinta que debe pedirse.", "forbidden_inference": "Devengado C-41 y débito son siempre iguales."},
    {"stage_id": "CP134_06", "stage": "C55_REGULARIZATION", "record": "Formulario C-55 Regularización", "required_or_visible_fields": "débito BNA superior al devengado; banco/cuenta; documento original", "execution_meaning": "Reconcilia diferencia positiva", "source_id": "e0_cgn_circular_22_2004_c55_bank_debit", "target_status": "TARGET_SEARCH_NOT_EXECUTED", "permitted_inference": "Buscar C-55 vinculado a cada C-41.", "forbidden_inference": "Todo pago genera C-55."},
    {"stage_id": "CP134_07", "stage": "C55_DEACTIVATION", "record": "Formulario C-55 Desafectación", "required_or_visible_fields": "débito BNA inferior al devengado; banco/cuenta; documento original", "execution_meaning": "Reconcilia diferencia negativa", "source_id": "e0_cgn_circular_22_2004_c55_bank_debit", "target_status": "TARGET_SEARCH_NOT_EXECUTED", "permitted_inference": "Pedir desafectación/reversa si existe diferencia.", "forbidden_inference": "Ausencia web de C-55 prueba identidad de montos."},
    {"stage_id": "CP134_08", "stage": "TARGET_CLOSE", "record": "C-41 + estado + pago/débito + C-55 si aplica", "required_or_visible_fields": "71597;152677;2876; beneficiario; concepto; importe; moneda; fechas; estado; vínculo bancario", "execution_meaning": "Cadena mínima para atribución", "source_id": "e0_cgn_cuenta_inversion_2008_sdp;e0_cgn_circular_2_1997_c41_due_date;e0_cgn_circular_6_1995_c41_tgn;e0_cgn_circular_22_2004_c55_bank_debit", "target_status": "OPEN", "permitted_inference": "Los tres números reducen el universo de búsqueda.", "forbidden_inference": "Los tres números pertenecen a la recompra o prueban pago."},
    {"stage_id": "CP135_09", "stage": "SIDIF_DAILY_STATE_OUTPUT", "record": "SDPGB por beneficiario y SDPAG por ítem, o sucesor equivalente", "required_or_visible_fields": "OB SIDIF; SAF; beneficiario; importe; estado P/R/A; fecha; banco; cuenta; medio RN/CH/TR/TI/NS", "execution_meaning": "Distingue pagado, rechazado y anulado", "source_id": "e0_tgn_circular_7_1997_daily_paid_files;e0_cgn_circular_34_1997_sdpgb_paid_beneficiary_schema", "target_status": "SCHEMA_PROVED_TARGET_ROWS_NOT_LOCATED", "permitted_inference": "Pedir extracto exacto por 71597, 152677 y 2876 en SDPGB/SDPAG o sucesor.", "forbidden_inference": "La existencia del esquema prueba que las tres órdenes fueron pagadas."},
    {"stage_id": "CP135_10", "stage": "TGN_TO_BCRA_INSTRUCTION_FILE", "record": "Archivo de instrucciones de pago enviado por enlace", "required_or_visible_fields": "identificador de archivo; fecha/hora; orden; importe; moneda; destino; acuse", "execution_meaning": "Instrucción electrónica posterior a la orden", "source_id": "e0_cgn_cuenta_inversion_2008_tomo_ii_tgn_system_files", "target_status": "2008_RECORD_CLASS_PROVED_TARGET_FILE_OPEN", "permitted_inference": "Pedir el archivo o registro equivalente asociado a cada orden.", "forbidden_inference": "La capacidad del enlace prueba envío target."},
    {"stage_id": "CP135_11", "stage": "BCRA_MOVEMENT_AND_BALANCE_RETURN", "record": "Archivos de movimientos y saldos bancarios recibidos", "required_or_visible_fields": "cuenta; fecha valor; débito/crédito; importe; moneda; referencia; saldo", "execution_meaning": "Huella bancaria separada de la instrucción", "source_id": "e0_cgn_cuenta_inversion_2008_tomo_ii_tgn_system_files", "target_status": "2008_RECORD_CLASS_PROVED_TARGET_MOVEMENT_OPEN", "permitted_inference": "Exigir movimiento y saldo que permitan conciliar el eventual pago.", "forbidden_inference": "Todo archivo de movimiento corresponde a la recompra."},
    {"stage_id": "CP135_12", "stage": "TARGET_PAYMENT_STATE_CLOSE", "record": "C-41 + SDPGB/SDPAG + instrucción + movimiento + ajuste", "required_or_visible_fields": "71597;152677;2876; P/R/A; fecha; beneficiario; banco/cuenta; medio; instrucción; movimiento; C-55 si aplica", "execution_meaning": "Cadena mínima reforzada para pago efectivo", "source_id": "e0_cgn_cuenta_inversion_2008_sdp;e0_tgn_circular_7_1997_daily_paid_files;e0_cgn_circular_34_1997_sdpgb_paid_beneficiary_schema;e0_cgn_cuenta_inversion_2008_tomo_ii_tgn_system_files", "target_status": "OPEN", "permitted_inference": "Ahora se conocen los campos y clases documentales exactos a solicitar.", "forbidden_inference": "Esquema y capacidad equivalen a resultado target."},
]
write_csv(HERE / "E0_C41_PAYMENT_EXECUTION_CHAIN_V135.csv", c41_chain)

# Archivo parlamentario: el contexto masivo no sustituye el localizador exacto.
bicameral = [
    {"row_id": "BI134_01", "object": "OV 366/09", "route_checked": "Senado expediente exacto", "result": "Bicameral Revisora; archivo 28/05/2012 por nota 18/05/2012; texto original en carga", "status": "EXACT_METADATA_BODY_OPEN", "source_id": "e0_senado_exp_366_09_agn_res211_t3", "next_locator": "nota 18/05/2012; remito; inventario; depósito"},
    {"row_id": "BI134_02", "object": "OV 44/10", "route_checked": "Senado expediente exacto", "result": "Bicameral Revisora; archivo 28/05/2012 por nota 18/05/2012; texto original en carga", "status": "EXACT_METADATA_BODY_OPEN", "source_id": "e0_senado_exp_44_10_agn_res44_t4", "next_locator": "nota 18/05/2012; remito; inventario; depósito"},
    {"row_id": "BI134_03", "object": "Documentación pública Bicameral", "route_checked": "Sección Documentación y paginación visible", "result": "Documentos recientes visibles; nota 2012 no expuesta en el inventario revisado", "status": "PUBLIC_UI_NEGATIVE_CONTROL_ONLY", "source_id": "e0_senado_bicameral_revisora_current_documents", "next_locator": "REVISORA@SENADO.GOB.AR; internos 2310-2315"},
    {"row_id": "BI134_04", "object": "Lote de archivo parlamentario", "route_checked": "HCDN reunión 8 del 23/05/2012 punto 13", "result": "Amplio lote de archivos de la Revisora; strings exactas OV 366/09 y OV 44/10 no localizadas", "status": "MASS_ARCHIVE_CONTEXT_NOT_TARGET_PROOF", "source_id": "e0_hcdn_session_summary_2012_05_23_mass_archive", "next_locator": "No usar como disposición de los dos expedientes target"},
    {"row_id": "BI134_05", "object": "Nota Bicameral 18/05/2012", "route_checked": "Senado + documentación actual + sumario HCDN", "result": "Cuerpo e inventario de transferencia no localizados públicamente", "status": "EXACT_NOTE_BODY_OPEN", "source_id": "e0_senado_exp_366_09_agn_res211_t3;e0_senado_exp_44_10_agn_res44_t4;e0_senado_bicameral_revisora_current_documents;e0_hcdn_session_summary_2012_05_23_mass_archive", "next_locator": "Solicitud archivística exacta; borrador no enviado"},
    {"row_id": "BI135_06", "object": "OV 366/09 y OV 44/10", "route_checked": "Índice histórico HCDN de reuniones y versiones taquigráficas; variantes 0366-ov-2009, 366-ov-2009, 0044-ov-2010, 44-ov-2010, 366/09 y 44/10", "result": "Sin coincidencias exactas en el índice público preservado", "status": "PUBLIC_INDEX_NEGATIVE_CONTROL_NOT_ABSENCE", "source_id": "e0_hcdn_historic_plenary_index_negative_control", "next_locator": "Fondo interno de la Bicameral; nota, remito, inventario, caja y signatura"},
    {"row_id": "BI135_07", "object": "Custodia material de los dos OV", "route_checked": "Regla COMDOC contemporánea como comparador", "result": "Campos verificables: dos remitos, cuerpos, anexos, último folio, área depositaria; ante pérdida, búsqueda intensiva y reconstrucción certificada", "status": "CONTEMPORANEOUS_CUSTODY_COMPARATOR_NOT_TARGET_RULE", "source_id": "e0_minplan_resolution_1522_2006_comdoc_custody", "next_locator": "Pedir equivalentes aplicables al fondo Bicameral/Economía sin presumir identidad normativa"},
]
write_csv(HERE / "E0_BICAMERAL_PUBLIC_INVENTORY_AUDIT_V135.csv", bicameral)

# Control visual de una tabla horizontal: el renglón renderizado gobierna sobre el texto linealizado.
anexo_k_alignment = [
    {"row_id": "AK135_01", "rendered_row": "83100000 HONORARIOS - BANK OF NEW YORK", "amount_ars": "227910.00", "sidif_ids": "182705;24306", "visual_status": "VISUAL_TABLE_ROW_ALIGNMENT_EXACT", "linear_search_risk": "Puede desplazar identificadores a la fila siguiente", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "permitted_inference": "Los dos SIDIF pertenecen a Bank of New York.", "forbidden_inference": "Asignarlos a Banco Nación por orden de texto extraído."},
    {"row_id": "AK135_02", "rendered_row": "83106000 COMISIONES - BANCO NACION", "amount_ars": "32270.30", "sidif_ids": "71597;152677;2876", "visual_status": "VISUAL_TABLE_ROW_ALIGNMENT_EXACT", "linear_search_risk": "La linealización puede parecer asociarlos a Letras del Tesoro", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "permitted_inference": "Los tres SIDIF son referencias exactas de comisiones BNA.", "forbidden_inference": "La fila prueba pago o vínculo con recompra."},
    {"row_id": "AK135_03", "rendered_row": "81155000 LETRAS DEL TESORO", "amount_ars": "18530136.99", "sidif_ids": "171761", "visual_status": "VISUAL_TABLE_ROW_ALIGNMENT_EXACT", "linear_search_risk": "La extracción puede heredar los tres IDs de la fila anterior", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "permitted_inference": "El único SIDIF visible de esta fila es 171761.", "forbidden_inference": "71597, 152677 o 2876 pertenecen a Letras."},
    {"row_id": "AK135_04", "rendered_row": "Regla de lectura", "amount_ars": "N/A", "sidif_ids": "N/A", "visual_status": "SEARCH_SNIPPET_LINEARIZATION_FALSE_SHIFT_CONTROLLED", "linear_search_risk": "Alta en tablas horizontales con columnas", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "permitted_inference": "La alineación visual renderizada controla la atribución de fila.", "forbidden_inference": "Usar un snippet lineal como sustituto de la tabla."},
]
write_csv(HERE / "E0_2008_ANEXO_K_VISUAL_ALIGNMENT_CONTROL_V135.csv", anexo_k_alignment)

payment_state_schema = [
    {"row_id": "PS135_01", "record": "SDPGBXXX.CON", "field_or_code": "OB SIDIF; SAF; ejercicio; tipo y número de formulario", "meaning": "Identidad de la orden", "target_query": "71597;152677;2876", "source_id": "e0_cgn_circular_34_1997_sdpgb_paid_beneficiary_schema", "status": "EXACT_HISTORIC_SCHEMA_SUCCESSOR_2008_OPEN"},
    {"row_id": "PS135_02", "record": "SDPGBXXX.CON", "field_or_code": "beneficiario; descripción; deducción; importe", "meaning": "Sujeto y cuantía", "target_query": "beneficiario y monto por cada OB", "source_id": "e0_cgn_circular_34_1997_sdpgb_paid_beneficiary_schema", "status": "EXACT_HISTORIC_SCHEMA_SUCCESSOR_2008_OPEN"},
    {"row_id": "PS135_03", "record": "SDPGBXXX.CON", "field_or_code": "P;R;A", "meaning": "Pagado; rechazado; anulado", "target_query": "estado final por cada OB", "source_id": "e0_cgn_circular_34_1997_sdpgb_paid_beneficiary_schema", "status": "EXACT_STATE_CODES_PROVED_TARGET_VALUE_OPEN"},
    {"row_id": "PS135_04", "record": "SDPGBXXX.CON", "field_or_code": "fecha; banco; sucursal; tipo de cuenta; cuenta bancaria", "meaning": "Fecha y rastro bancario", "target_query": "fecha valor y cuenta por cada OB", "source_id": "e0_cgn_circular_34_1997_sdpgb_paid_beneficiary_schema", "status": "EXACT_HISTORIC_FIELDS_PROVED_TARGET_VALUE_OPEN"},
    {"row_id": "PS135_05", "record": "SDPGBXXX.CON", "field_or_code": "RN;CH;TR;TI;NS", "meaning": "Red bancaria; cheque; transferencia CUT; títulos; nota", "target_query": "medio de pago por cada OB", "source_id": "e0_cgn_circular_34_1997_sdpgb_paid_beneficiary_schema", "status": "EXACT_PAYMENT_MEDIA_CODES_PROVED_TARGET_VALUE_OPEN"},
    {"row_id": "PS135_06", "record": "SDPAG", "field_or_code": "pagado por ítem", "meaning": "Desagregación presupuestaria diaria", "target_query": "cruce por ítem de cada OB", "source_id": "e0_tgn_circular_7_1997_daily_paid_files", "status": "DAILY_OUTPUT_AUTHORITY_PROVED_TARGET_VALUE_OPEN"},
    {"row_id": "PS135_07", "record": "SDPGB", "field_or_code": "pagado por beneficiario", "meaning": "Desagregación diaria por sujeto", "target_query": "cruce por beneficiario de cada OB", "source_id": "e0_tgn_circular_7_1997_daily_paid_files", "status": "DAILY_OUTPUT_AUTHORITY_PROVED_TARGET_VALUE_OPEN"},
    {"row_id": "PS135_08", "record": "TRANSAF/SIDIF", "field_or_code": "procesamiento diario 19:30; pagos, anulaciones y rechazos", "meaning": "Corte operativo diario", "target_query": "archivo de la fecha de cada C-41 o sucesor equivalente", "source_id": "e0_tgn_circular_7_1997_daily_paid_files", "status": "HISTORIC_DAILY_PROCESS_PROVED_2008_CONTINUITY_OPEN"},
]
write_csv(HERE / "E0_SIDIF_PAID_BENEFICIARY_FILE_SCHEMA_V135.csv", payment_state_schema)

tgn_system_records = [
    {"row_id": "TS135_01", "2008_record_class": "Archivo de instrucciones de pago", "direction": "TGN→BCRA", "minimum_target_fields": "fecha/hora; orden; importe; moneda; cuenta/destino; acuse", "source_id": "e0_cgn_cuenta_inversion_2008_tomo_ii_tgn_system_files", "target_status": "CLASS_PROVED_TARGET_RECORD_OPEN"},
    {"row_id": "TS135_02", "2008_record_class": "Archivo de movimientos bancarios", "direction": "BCRA→TGN", "minimum_target_fields": "cuenta; fecha valor; débito/crédito; importe; referencia", "source_id": "e0_cgn_cuenta_inversion_2008_tomo_ii_tgn_system_files", "target_status": "CLASS_PROVED_TARGET_RECORD_OPEN"},
    {"row_id": "TS135_03", "2008_record_class": "Archivo de saldos bancarios", "direction": "BCRA→TGN", "minimum_target_fields": "cuenta; fecha; saldo inicial/final; moneda", "source_id": "e0_cgn_cuenta_inversion_2008_tomo_ii_tgn_system_files", "target_status": "CLASS_PROVED_TARGET_RECORD_OPEN"},
    {"row_id": "TS135_04", "2008_record_class": "Nota a TGN para pago exterior", "direction": "SAF355/356→TGN", "minimum_target_fields": "beneficiario; banco; cuenta; tipo de operación; SIDIF; moneda; cambio; divisas", "source_id": "e0_cgn_tgn_disposicion_conjunta_47_10_2008_external_payments", "target_status": "CONDITIONAL_ON_EXTERNAL_PAYMENT"},
    {"row_id": "TS135_05", "2008_record_class": "Boleto de Venta de Cambio y respaldos", "direction": "BNA↔SAF/TGN", "minimum_target_fields": "fecha; moneda; cotización; importe; firmas/poderes", "source_id": "e0_cgn_tgn_disposicion_conjunta_47_10_2008_external_payments", "target_status": "CONDITIONAL_ON_BNA_EXTERNAL_PAYMENT"},
    {"row_id": "TS135_06", "2008_record_class": "Nota conjunta ONCP/TGN + archivo/aceptación SIGADE/Caja", "direction": "ONCP/TGN→agente de registro/pago", "minimum_target_fields": "instrucción; archivo; validación; aceptación; registro", "source_id": "e0_debt_joint_resolution_216_26_2008_instruction_chain", "target_status": "COMPARATOR_OTHER_DEBT_PROCEDURE_NOT_TARGET_EQUIVALENCE"},
]
write_csv(HERE / "E0_TGN_BCRA_2008_PAYMENT_RECORD_CLASSES_V135.csv", tgn_system_records)

comdoc_custody = [
    {"row_id": "CC135_01", "control": "Registro COMDOC o seguimiento alternativo", "requested_field": "número; estado; área depositaria", "source_id": "e0_minplan_resolution_1522_2006_comdoc_custody", "scope_status": "CONTEMPORANEOUS_COMPARATOR", "target_use": "S01:0342455/2008 y anexos"},
    {"row_id": "CC135_02", "control": "Dos remitos", "requested_field": "emisor; receptor; firma; fecha", "source_id": "e0_minplan_resolution_1522_2006_comdoc_custody", "scope_status": "CONTEMPORANEOUS_COMPARATOR", "target_use": "probar entrega y recepción"},
    {"row_id": "CC135_03", "control": "Integridad material", "requested_field": "cantidad de cuerpos; anexos; último folio", "source_id": "e0_minplan_resolution_1522_2006_comdoc_custody", "scope_status": "CONTEMPORANEOUS_COMPARATOR", "target_use": "controlar contenido recibido"},
    {"row_id": "CC135_04", "control": "Pérdida alegada", "requested_field": "circular COMDOC; búsqueda intensiva; áreas consultadas; resultado", "source_id": "e0_minplan_resolution_1522_2006_comdoc_custody", "scope_status": "CONTEMPORANEOUS_COMPARATOR", "target_use": "exigir trazabilidad de búsqueda"},
    {"row_id": "CC135_05", "control": "Reconstrucción", "requested_field": "copias certificadas; informe explicativo; acto de reconstrucción", "source_id": "e0_minplan_resolution_1522_2006_comdoc_custody", "scope_status": "CONTEMPORANEOUS_COMPARATOR", "target_use": "evitar cerrar por mera ausencia"},
    {"row_id": "CC135_06", "control": "Instrucción de deuda contemporánea", "requested_field": "nota conjunta ONCP/TGN; firmantes; fecha; operación", "source_id": "e0_debt_joint_resolution_216_26_2008_instruction_chain", "scope_status": "OTHER_DEBT_PROCEDURE_COMPARATOR", "target_use": "buscar documento funcionalmente análogo sin presumirlo"},
    {"row_id": "CC135_07", "control": "Registro diario COMDOC", "requested_field": "reporte diario; archivo; fecha; identificador", "source_id": "e0_debt_joint_resolution_216_26_2008_instruction_chain", "scope_status": "OTHER_DEBT_PROCEDURE_COMPARATOR", "target_use": "formular búsqueda por sistema"},
    {"row_id": "CC135_08", "control": "Aceptación y registro", "requested_field": "validación; aceptación Caja; registro SIGADE; recibo/acreditación", "source_id": "e0_debt_joint_resolution_216_26_2008_instruction_chain", "scope_status": "OTHER_DEBT_PROCEDURE_COMPARATOR", "target_use": "mapear clases documentales, no adjudicar resultado"},
]
write_csv(HERE / "E0_COMDOC_CUSTODY_AND_DEBT_INSTRUCTION_COMPARATOR_V135.csv", comdoc_custody)

# Rutas agotadas, ledger y cortes metodológicos.
exhaust_path = HERE / "E0_EXPEDIENT_PUBLIC_SEARCH_EXHAUSTION_V135.csv"
exhaust = read_csv(exhaust_path)[:6]
exhaust.extend([
    {"search_id": "EX134_07", "target": "FindDoc capability", "route": "Agenda Digital Argentina pp.206-207", "result": "Esquema de salida y arquitectura exactos", "public_body_found": "DESIGN_SPEC", "status": "ROUTE_METADATA_CAPABILITY_PROVED", "permitted_inference": "El índice histórico mostraba pases y ubicación.", "forbidden_inference": "Mostraba el cuerpo."},
    {"search_id": "EX134_08", "target": "S01:0130656/2008", "route": "AGN Informe 254/2013", "result": "Consulta real al endpoint con estado y ubicación al 05/03/2013", "public_body_found": "CONTROL_QUERY_METADATA", "status": "HISTORIC_OPERATIONAL_CONTROL", "permitted_inference": "FindDoc funcionaba para un S01/2008.", "forbidden_inference": "Responde por el target."},
    {"search_id": "EX134_09", "target": "S01:0342455/2008", "route": "canales oficiales alternativos Economía", "result": "Email, teléfono y atención presencial identificados; no contactados", "public_body_found": "NO", "status": "ADMINISTRATIVE_ROUTE_READY_NOT_SENT", "permitted_inference": "Puede pedirse exportación de hoja de ruta.", "forbidden_inference": "La consulta fue presentada."},
    {"search_id": "EX134_10", "target": "Nota Bicameral 18/05/2012", "route": "inventario actual Senado + sumario HCDN 23/05/2012", "result": "Contexto de archivo masivo; cuerpo exacto no localizado", "public_body_found": "CONTEXT_ONLY", "status": "PUBLIC_INVENTORY_EXHAUSTED_EXACT_NOTE_OPEN", "permitted_inference": "El pedido puede dirigirse al contacto actual con dos OV exactos.", "forbidden_inference": "Los expedientes fueron parte del lote de Cámara o fueron destruidos."},
    {"search_id": "EX135_11", "target": "C-41 71597, 152677 y 2876", "route": "búsquedas oficiales exactas por número, Banco Nación, cuenta 83106000 e importe", "result": "Sólo se recuperó el Anexo K; no cuerpos C-41 ni filas SDPGB/SDPAG", "public_body_found": "REFERENCE_ROW_ONLY", "status": "THREE_C41_IDENTIFIERS_EXACT_PUBLIC_BODIES_AND_STATES_NOT_LOCATED", "permitted_inference": "Los tres números son claves de búsqueda exactas de comisiones BNA.", "forbidden_inference": "Fueron pagados o pertenecen a la recompra."},
    {"search_id": "EX135_12", "target": "OV 366/09 y OV 44/10", "route": "índice histórico HCDN; seis variantes exactas", "result": "Sin coincidencias en el índice público preservado", "public_body_found": "NO_IN_PUBLIC_INDEX", "status": "PUBLIC_INDEX_NEGATIVE_CONTROL_ONLY", "permitted_inference": "La búsqueda archivística debe usar todas las variantes.", "forbidden_inference": "Los expedientes no existen o fueron destruidos."},
    {"search_id": "EX135_13", "target": "Estado efectivo de las tres órdenes", "route": "normativa CGN/TGN y Cuenta de Inversión 2008", "result": "Esquema P/R/A y clases de instrucción/movimiento/saldo localizados; filas target no públicas", "public_body_found": "SYSTEM_SCHEMA_AND_RECORD_CLASSES", "status": "QUERY_SPECIFICATION_CLOSED_TARGET_VALUES_OPEN", "permitted_inference": "El pedido puede exigir campos y archivos concretos.", "forbidden_inference": "La arquitectura del sistema resuelve el estado target."},
])
write_csv(exhaust_path, exhaust)

ledger_path = HERE / "E0_FISCAL_MECHANISM_LEDGER_V135.csv"
ledger = read_csv(ledger_path)[:157]
ledger.extend([
    {"ledger_id": "F158", "window": "2011-2013", "mechanism": "Legacy_document_index", "phase": "FINDDOC_CAPABILITY_AND_CONTROL", "as_of_date": "2013-03-05", "payer": "N/A", "recipient": "N/A", "universe": "COMDOC_S01_files", "instrument": "FindDoc_route_metadata", "amount_original": "4", "original_unit": "OUTPUT_FIELD_FAMILIES", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_agenda_digital_finddoc_comdoc_architecture;e0_agn_informe_254_2013_finddoc_control", "source_locator": "Agenda_pp206_207;AGN_254_pp91_93_133", "realization_status": "HISTORIC_CAPABILITY_AND_OPERATIONAL_CONTROL_PROVED", "additivity": "NON_ADDITIVE", "status_interpretation": "FindDoc exposed route/location metadata and was actually used for another 2008 S01 file.", "caveat": "The target query remains unexecuted and body content is outside the proven output schema."},
    {"ledger_id": "F159", "window": "2008-2026", "mechanism": "Debt_buyback_excess_GDP", "phase": "TARGET_FINDDOC_ADMINISTRATIVE_QUERY", "as_of_date": "2026-08-30", "payer": "N/A", "recipient": "N/A", "universe": "S01_0342455_2008", "instrument": "COMDOC_FindDoc", "amount_original": "0", "original_unit": "TARGET_QUERY_RESULTS", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_economia_consulta_expedientes_comdoc_gde;e0_agenda_digital_finddoc_comdoc_architecture", "source_locator": "official_alternative_channels", "realization_status": "ADMINISTRATIVE_EXPORT_REQUIRED_DRAFT_NOT_SENT", "additivity": "NON_ADDITIVE", "status_interpretation": "The expected route fields and official contact channel are known.", "caveat": "No request was submitted and no target route was recovered."},
    {"ledger_id": "F160", "window": "1995-2008", "mechanism": "Debt_accounting_payment_chain", "phase": "C41_TO_BANK_DEBIT_RECONCILIATION", "as_of_date": "2008-12-31", "payer": "Tesoro_Nacional", "recipient": "Unknown_target_beneficiaries", "universe": "SIDIF_71597_152677_2876", "instrument": "C41_C55_bank_debit", "amount_original": "3", "original_unit": "C41_LOCATORS", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_cgn_cuenta_inversion_2008_sdp;e0_cgn_circular_2_1997_c41_due_date;e0_cgn_circular_6_1995_c41_tgn;e0_cgn_circular_13_2002_external_payments_c41;e0_cgn_circular_22_2004_c55_bank_debit", "source_locator": "Anexo_K_and_CGN_procedure_rules", "realization_status": "DOCUMENT_CLASS_AND_CHAIN_PROVED_TARGET_BODIES_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "Three exact identifiers can anchor searches for order, processing, debit and adjustment records.", "caveat": "An order number is not executed payment and is not yet linked to the buyback."},
    {"ledger_id": "F161", "window": "2012-05-18/2012-05-28", "mechanism": "AGN_parliamentary_archive", "phase": "MASS_ARCHIVE_CONTEXT_CONTROL", "as_of_date": "2012-05-28", "payer": "N/A", "recipient": "Parliamentary_archive", "universe": "OV_366_09_OV_44_10", "instrument": "Bicameral_note_and_HCDN_archive_batch", "amount_original": "2", "original_unit": "TARGET_EXPEDIENTS", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_senado_bicameral_revisora_current_documents;e0_hcdn_session_summary_2012_05_23_mass_archive", "source_locator": "current_public_inventory;HCDN_session_summary", "realization_status": "MASS_ARCHIVE_CONTEXT_ONLY_EXACT_NOTE_BODY_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "The period contains mass archival activity but the two target strings were not located in the inspected HCDN summary.", "caveat": "Context does not establish the disposition of either target expediente."},
    {"ledger_id": "F162", "window": "1997-2008", "mechanism": "Debt_accounting_payment_chain", "phase": "SIDIF_DAILY_PAYMENT_STATE_OUTPUT", "as_of_date": "2008-12-31", "payer": "Tesoro_Nacional", "recipient": "Unknown_target_beneficiaries", "universe": "SIDIF_71597_152677_2876", "instrument": "SDPGB_SDPAG_or_successor", "amount_original": "3", "original_unit": "TARGET_ORDER_IDS", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_tgn_circular_7_1997_daily_paid_files;e0_cgn_circular_34_1997_sdpgb_paid_beneficiary_schema", "source_locator": "Circular_TGN_7_97;Anexo_Circular_CGN_34_97", "realization_status": "PAYMENT_STATE_SCHEMA_PROVED_TARGET_ROWS_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "The official historical output distinguishes paid, rejected and annulled orders and exposes bank/payment fields.", "caveat": "Literal continuity of the filenames to 2008 and the three target rows remain unproved."},
    {"ledger_id": "F163", "window": "2008", "mechanism": "Treasury_central_account_payment_system", "phase": "TGN_BCRA_ELECTRONIC_RECORD_CLASSES", "as_of_date": "2008-12-31", "payer": "TGN", "recipient": "BCRA", "universe": "Payment_instructions_movements_balances", "instrument": "Electronic_files_over_communication_link", "amount_original": "3", "original_unit": "RECORD_CLASSES", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_cgn_cuenta_inversion_2008_tomo_ii_tgn_system_files", "source_locator": "Cuenta_Inversion_2008_Tomo_II_printed_p177", "realization_status": "2008_SYSTEM_RECORD_CLASSES_PROVED_TARGET_LINK_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "Payment instruction, movement and balance files existed as system classes in 2008.", "caveat": "No target instruction or movement has been located."},
    {"ledger_id": "F164", "window": "2008", "mechanism": "External_public_debt_payment", "phase": "C41_EXTERNAL_PAYMENT_DOCUMENT_PACKAGE", "as_of_date": "2008-10-14", "payer": "SAF_355_356", "recipient": "Conditional_foreign_beneficiary", "universe": "External_payments_if_applicable", "instrument": "C41_TGN_note_BNA_exchange_documents", "amount_original": "0", "original_unit": "TARGET_APPLICABILITY_PROVED", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_cgn_tgn_disposicion_conjunta_47_10_2008_external_payments", "source_locator": "Joint_Disposition_47_10_2008", "realization_status": "CONTEMPORANEOUS_SCHEMA_PROVED_TARGET_APPLICABILITY_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "If an order was external, the package should identify beneficiary, destination bank/account, currency and SIDIF order.", "caveat": "No target order is classified as external."},
    {"ledger_id": "F165", "window": "2006-2008", "mechanism": "COMDOC_document_custody", "phase": "REMIT_INTEGRITY_LOSS_RECONSTRUCTION_CONTROL", "as_of_date": "2008-12-31", "payer": "N/A", "recipient": "Depositary_area", "universe": "S01_0342455_2008_and_annexes", "instrument": "COMDOC_remits_folios_search_reconstruction", "amount_original": "0", "original_unit": "TARGET_CUSTODY_RECORDS_LOCATED", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_minplan_resolution_1522_2006_comdoc_custody", "source_locator": "Resolution_1522_2006_updated_art34", "realization_status": "CONTEMPORANEOUS_CUSTODY_COMPARATOR_TARGET_RECORDS_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "The comparator yields precise fields for remittance, integrity, intensive search and reconstruction requests.", "caveat": "The MINPLAN rule is not automatically governing for the Economy/ONCP target."},
    {"ledger_id": "F166", "window": "2008", "mechanism": "Public_debt_security_instruction", "phase": "ONCP_TGN_INSTRUCTION_AND_ACCEPTANCE_COMPARATOR", "as_of_date": "2008-06-27", "payer": "ONCP_TGN", "recipient": "Registration_or_payment_agent", "universe": "Consolidation_bond_procedure", "instrument": "Joint_note_COMDOC_file_SIGADE_Caja_acceptance", "amount_original": "0", "original_unit": "TARGET_EQUIVALENCE_PROVED", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_debt_joint_resolution_216_26_2008_instruction_chain", "source_locator": "Joint_Resolution_216_26_2008_art5_annex", "realization_status": "OTHER_DEBT_PROCEDURE_DOCUMENT_CLASS_COMPARATOR", "additivity": "NON_ADDITIVE", "status_interpretation": "A contemporaneous debt procedure generated instruction, data, validation, acceptance and SIGADE records.", "caveat": "It is not the buyback procedure and cannot be substituted for target proof."},
])
assert len(ledger) == 166
write_csv(ledger_path, ledger)

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V135.csv"
breaks = read_csv(breaks_path)[:117]
breaks.extend([
    {"break_id": "finddoc_route_metadata_not_expedient_body", "dimension": "document_scope", "problem": "FindDoc's public output is proven for route and location fields.", "rule": "Use it to trace custody; request the body separately.", "status": "FROZEN", "evidence": "Agenda Digital pp.206-207"},
    {"break_id": "historic_control_query_not_target_query", "dimension": "external_validity", "problem": "AGN queried another S01/2008 successfully in 2013.", "rule": "Use as operational control only; keep S01:0342455/2008 unqueried.", "status": "FROZEN", "evidence": "AGN 254/2013 pp.93,133"},
    {"break_id": "c41_order_not_executed_payment", "dimension": "phase", "problem": "C-41 is an order that can require processing, TGN action, debit and adjustment.", "rule": "Require payment/debit status and C-55 or equivalent where applicable.", "status": "FROZEN", "evidence": "CGN Circulares 2/97, 6/95, 13/02, 22/04"},
    {"break_id": "mass_archive_context_not_target_disposition", "dimension": "archival_scope", "problem": "A large HCDN archive batch is temporally adjacent but does not list the two exact target strings.", "rule": "Retain exact Senate metadata as locator and request the 18/05/2012 note.", "status": "FROZEN", "evidence": "HCDN reunión 8; Senate OV 366/09 and OV 44/10"},
    {"break_id": "horizontal_pdf_linearization_not_row_alignment", "dimension": "source_parsing", "problem": "Search snippets can shift identifiers between horizontally aligned table rows.", "rule": "The rendered visual row controls account, amount and SIDIF attribution.", "status": "FROZEN", "evidence": "CGN Cuenta de Inversión 2008 Anexo K, physical PDF page 67"},
    {"break_id": "payment_output_schema_not_target_state", "dimension": "phase", "problem": "SDPGB/SDPAG define paid, rejected and annulled outputs.", "rule": "Require the target row or certified successor extract before assigning a state.", "status": "FROZEN", "evidence": "TGN Circular 7/97; CGN Circular 34/97 annex"},
    {"break_id": "historic_filename_not_automatic_2008_continuity", "dimension": "temporal_scope", "problem": "The exact SDPGB/SDPAG filenames are proved in 1997.", "rule": "Request the named files or their 2008 successor equivalent; do not assert unchanged format.", "status": "FROZEN", "evidence": "TGN Circular 7/97; CGN Circular 34/97 annex"},
    {"break_id": "system_record_class_not_target_record", "dimension": "external_validity", "problem": "TGN/BCRA instruction, movement and balance file classes are documented for 2008.", "rule": "Require identifiers and target linkage for each of the three C-41 orders.", "status": "FROZEN", "evidence": "Cuenta de Inversión 2008 Tomo II, printed p.177"},
    {"break_id": "external_payment_schema_conditional", "dimension": "scope", "problem": "The 2008 external-payment rule provides detailed fields for SAF 355/356.", "rule": "Apply only after an order is classified as an external payment.", "status": "FROZEN", "evidence": "CGN/TGN Joint Disposition 47/10 of 2008"},
    {"break_id": "contemporaneous_comparator_not_target_governing_rule", "dimension": "legal_scope", "problem": "COMDOC custody and another debt-title procedure expose useful document classes.", "rule": "Use as search comparators, never as proof that the target was governed by or generated the same records.", "status": "FROZEN", "evidence": "MINPLAN Resolution 1522/2006; Joint Resolution 216/26 of 2008"},
])
assert len(breaks) == 127
write_csv(breaks_path, breaks)

# Se enriquecen los seis borradores; nada se envía.
trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V135.csv"
trace = read_csv(trace_path)[:104]
trace.extend([
    {"trace_id": "TR134_105", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / administradores COMDOC", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Exportación de hoja de ruta FindDoc/COMDOC del expediente target", "period_or_date": "2008-actualidad", "identifiers": "S01:0342455/2008;VerExpediente", "minimum_usable_fields": "origen;destino;fecha envío;fecha recepción;ubicación;estado", "confidentiality_fallback": "metadatos de pases sin cuerpo", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR134_106", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / CGN / TGN", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Cuerpo y estado de tres formularios C-41 2008", "period_or_date": "2008", "identifiers": "SIDIF 71597;152677;2876;SIGADE 83106000", "minimum_usable_fields": "SAF;beneficiario;concepto;importe;moneda;emisión;vencimiento;estado", "confidentiality_fallback": "cuadro certificado por número SIDIF", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR134_107", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / TGN / BNA", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Pago, débito, rechazo, reversa o C-55 asociados a cada C-41", "period_or_date": "2008-2009", "identifiers": "71597;152677;2876;C-41;C-55", "minimum_usable_fields": "fecha;importe;moneda;cuenta;estado;documento original;vínculo C-41", "confidentiality_fallback": "estado final y total por orden", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR134_108", "request_id": "REQ134_ECON", "institution": "Dirección de Información Ciudadana / Mesa de Entradas", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Consulta administrativa sustitutiva por caída del endpoint", "period_or_date": "2026-08-30", "identifiers": "ciudadano@mecon.gov.ar;0810-333-6326;Balcarce186 oficina140", "minimum_usable_fields": "acuse;número de gestión;resultado;derivación", "confidentiality_fallback": "derivación al custodio competente", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR134_109", "request_id": "REQ134_AGN", "institution": "Senado / Bicameral Revisora", "gap_id": "CL134_AGN_REPLY", "requested_record": "Nota de archivo del 18/05/2012 e inventario/remito asociado", "period_or_date": "2012-05-18/2012-05-28", "identifiers": "OV366/09;OV44/10;nota18/05/2012", "minimum_usable_fields": "emisor;destinatario;listado;fecha;depósito;signatura", "confidentiality_fallback": "renglones exactos de ambos OV", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR134_110", "request_id": "REQ134_AGN", "institution": "Senado / Bicameral Revisora", "gap_id": "CL134_AGN_REPLY", "requested_record": "Resultado de búsqueda en fondo histórico no expuesto por la UI pública", "period_or_date": "2009-2012", "identifiers": "Res211/2009;Res44/2010;Act426/09;Act466/09", "minimum_usable_fields": "serie;caja;legajo;soporte;estado de conservación", "confidentiality_fallback": "certificación de búsqueda y ruta de transferencia", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR135_111", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / TGN / CGN", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Extracto SDPGB por beneficiario o sucesor 2008", "period_or_date": "2008", "identifiers": "OB SIDIF 71597;152677;2876;SDPGBXXX.CON", "minimum_usable_fields": "SAF;beneficiario;importe;estado P/R/A;fecha;banco;sucursal;tipo y número de cuenta;motivo;medio", "confidentiality_fallback": "cuadro certificado de esos campos por cada OB", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR135_112", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / TGN / CGN", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Extracto SDPAG por ítem o sucesor 2008", "period_or_date": "2008", "identifiers": "OB SIDIF 71597;152677;2876;SDPAG", "minimum_usable_fields": "SAF;ítem;importe;estado;fecha;anulación/rechazo", "confidentiality_fallback": "estado final y total por OB", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR135_113", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / TGN / BCRA", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Archivo o registro de instrucciones de pago TGN→BCRA", "period_or_date": "2008", "identifiers": "71597;152677;2876;archivo instrucciones de pago", "minimum_usable_fields": "identificador;fecha/hora;orden;importe;moneda;destino;acuse;resultado", "confidentiality_fallback": "certificación de existencia/ausencia y estado por orden", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR135_114", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / TGN / BCRA", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Archivos o registros de movimientos y saldos bancarios asociados", "period_or_date": "2008-2009", "identifiers": "71597;152677;2876;cuenta BNA/BCRA;movimiento;saldo", "minimum_usable_fields": "cuenta;fecha valor;débito/crédito;importe;moneda;referencia;saldo", "confidentiality_fallback": "movimiento certificado anonimizado salvo referencia de orden", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR135_115", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / SAF 355/356 / TGN / BNA", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Paquete de pago exterior, únicamente si alguna C-41 fue clasificada así", "period_or_date": "2008", "identifiers": "71597;152677;2876;Disposición Conjunta 47/2008-10/2008", "minimum_usable_fields": "beneficiario exterior;banco;cuenta;tipo operación;SIDIF;moneda;cotización;divisas;boleto de cambio", "confidentiality_fallback": "confirmación de no aplicabilidad por cada OB", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR135_116", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / archivo COMDOC", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Remitos e integridad material del expediente target", "period_or_date": "2008-actualidad", "identifiers": "S01:0342455/2008", "minimum_usable_fields": "remitos;firmas;fechas;cuerpos;anexos;último folio;área depositaria", "confidentiality_fallback": "certificación de custodia y último pase", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR135_117", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / archivo COMDOC", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Actuaciones de búsqueda y reconstrucción si se alega pérdida", "period_or_date": "2008-actualidad", "identifiers": "S01:0342455/2008;circular COMDOC;reconstrucción", "minimum_usable_fields": "áreas consultadas;fechas;resultados;copias certificadas;informe;acto de reconstrucción", "confidentiality_fallback": "certificación motivada del procedimiento realizado", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR135_118", "request_id": "REQ134_AGN", "institution": "Senado / Bicameral Revisora / archivo parlamentario", "gap_id": "CL134_AGN_REPLY", "requested_record": "Remitos, integridad y depósito de OV 366/09 y OV 44/10", "period_or_date": "2009-2012", "identifiers": "0366-OV-2009;0044-OV-2010;nota 18/05/2012", "minimum_usable_fields": "remito;emisor;receptor;fecha;cuerpos;anexos;último folio;caja;signatura", "confidentiality_fallback": "renglones certificados de inventario y ruta de transferencia", "status": "DRAFT_NOT_SENT"},
])
assert len(trace) == 118
write_csv(trace_path, trace)

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V135.csv"
keys = read_csv(keys_path)[:98]
keys.extend([
    {"key_id": "SK134_99", "request_id": "REQ134_ECON", "key_group": "finddoc_output_schema", "exact_key": "origen;destino;fecha envío;fecha recepción;ubicación", "search_purpose": "pedir exportación COMDOC homogénea", "source_or_basis": "Agenda Digital pp.206-207", "caveat": "No es cuerpo documental."},
    {"key_id": "SK134_100", "request_id": "REQ134_ECON", "key_group": "finddoc_endpoint", "exact_key": "http://expedientes.mecon.gov.ar/finddoc2/finddoc/VerExpediente", "search_purpose": "identificar servicio histórico exacto", "source_or_basis": "AGN 254/2013", "caveat": "Endpoint no operativo en 2026."},
    {"key_id": "SK134_101", "request_id": "REQ134_ECON", "key_group": "historic_control", "exact_key": "S01:0130656/2008;consulta05/03/2013;último pase11/06/2012", "search_purpose": "probar salida histórica y precedente de S01/2008", "source_or_basis": "AGN 254/2013 pp.93,133", "caveat": "No es el expediente target."},
    {"key_id": "SK134_102", "request_id": "REQ134_ECON", "key_group": "target_comdoc", "exact_key": "S01:0342455/2008", "search_purpose": "obtener hoja de ruta target", "source_or_basis": "Resolución conjunta 212/2008-24/2008", "caveat": "Consulta aún no ejecutada."},
    {"key_id": "SK134_103", "request_id": "REQ134_ECON", "key_group": "official_channel", "exact_key": "ciudadano@mecon.gov.ar;0810-333-6326;Balcarce186 piso1 oficina140", "search_purpose": "consulta administrativa sustitutiva", "source_or_basis": "Economía Consulta de expedientes", "caveat": "No contactado."},
    {"key_id": "SK134_104", "request_id": "REQ134_ECON", "key_group": "c41_target_ids", "exact_key": "SIDIF71597;SIDIF152677;SIDIF2876;SIGADE83106000", "search_purpose": "recuperar tres C-41 2008", "source_or_basis": "CGN 2008 Anexo K", "caveat": "No prueban vínculo con recompra."},
    {"key_id": "SK134_105", "request_id": "REQ134_ECON", "key_group": "c41_external_fields", "exact_key": "beneficiario;banco destino;cuenta;SIDIF;moneda;cotización;divisas", "search_purpose": "pedir nota/instrucción asociada si aplica", "source_or_basis": "CGN Circular 13/02", "caveat": "Aplicabilidad target abierta."},
    {"key_id": "SK134_106", "request_id": "REQ134_ECON", "key_group": "c55_reconciliation", "exact_key": "C-55;regularización;desafectación;débito BNA;documento original", "search_purpose": "cerrar diferencia orden-débito", "source_or_basis": "CGN Circular 22/04", "caveat": "No todo pago genera C-55."},
    {"key_id": "SK134_107", "request_id": "REQ134_AGN", "key_group": "bicameral_contact", "exact_key": "REVISORA@SENADO.GOB.AR;2822-3000;internos2310-2315", "search_purpose": "solicitar nota e inventario 2012", "source_or_basis": "Senado Comisión 100", "caveat": "No contactado."},
    {"key_id": "SK134_108", "request_id": "REQ134_AGN", "key_group": "mass_archive_control", "exact_key": "HCDN período130 reunión8 punto13;23/05/2012", "search_purpose": "controlar contexto de archivo masivo", "source_or_basis": "Sumario HCDN", "caveat": "No individualiza los dos OV target."},
    {"key_id": "SK135_109", "request_id": "REQ134_ECON", "key_group": "sidif_paid_file", "exact_key": "SDPGBXXX.CON;Pago a Beneficiarios/Deducciones", "search_purpose": "localizar salida por beneficiario", "source_or_basis": "Anexo Circular CGN 34/97", "caveat": "Pedir sucesor equivalente si el nombre cambió en 2008."},
    {"key_id": "SK135_110", "request_id": "REQ134_ECON", "key_group": "sidif_item_file", "exact_key": "SDPAG;pagado por ítem", "search_purpose": "localizar salida diaria por ítem", "source_or_basis": "Circular TGN 7/97", "caveat": "Continuidad literal a 2008 abierta."},
    {"key_id": "SK135_111", "request_id": "REQ134_ECON", "key_group": "sidif_state_codes", "exact_key": "P=Pagado;R=Rechazado;A=Anulado", "search_purpose": "distinguir estado efectivo", "source_or_basis": "Anexo Circular CGN 34/97", "caveat": "Código target no recuperado."},
    {"key_id": "SK135_112", "request_id": "REQ134_ECON", "key_group": "sidif_payment_media", "exact_key": "RN=Red bancaria;CH=Cheque;TR=Transferencia CUT;TI=Títulos;NS=Nota", "search_purpose": "identificar medio de pago", "source_or_basis": "Anexo Circular CGN 34/97", "caveat": "Medio target abierto."},
    {"key_id": "SK135_113", "request_id": "REQ134_ECON", "key_group": "sidif_order_numbers", "exact_key": "OB71597;OB152677;OB2876", "search_purpose": "consultar tres filas exactas", "source_or_basis": "CGN 2008 Anexo K, alineación visual", "caveat": "Son comisiones BNA, no pago confirmado."},
    {"key_id": "SK135_114", "request_id": "REQ134_ECON", "key_group": "anexo_k_account", "exact_key": "SIGADE83106000;COMISIONES-BANCO NACION;ARS32270.30", "search_purpose": "evitar corrimiento de renglón", "source_or_basis": "CGN 2008 Anexo K renderizado", "caveat": "No atribuye recompra."},
    {"key_id": "SK135_115", "request_id": "REQ134_ECON", "key_group": "tgn_bcra_system_file", "exact_key": "archivo de instrucciones de pago TGN-BCRA", "search_purpose": "localizar instrucción electrónica 2008", "source_or_basis": "Cuenta de Inversión 2008 Tomo II", "caveat": "Clase general, vínculo target abierto."},
    {"key_id": "SK135_116", "request_id": "REQ134_ECON", "key_group": "tgn_bcra_return_files", "exact_key": "archivo de movimientos;archivo de saldos;cuentas bancarias", "search_purpose": "cerrar huella bancaria", "source_or_basis": "Cuenta de Inversión 2008 Tomo II", "caveat": "Clases generales, registros target abiertos."},
    {"key_id": "SK135_117", "request_id": "REQ134_ECON", "key_group": "external_payment_2008", "exact_key": "Transferencia al exterior;Apertura de Carta de Crédito;SAF355;SAF356", "search_purpose": "probar o descartar aplicabilidad", "source_or_basis": "Disposición Conjunta CGN47/TGN10 de 2008", "caveat": "No asumir que las tres órdenes fueron exteriores."},
    {"key_id": "SK135_118", "request_id": "REQ134_ECON", "key_group": "external_payment_note", "exact_key": "beneficiario;banco destino;cuenta;SIDIF;moneda;cotización;divisas;Boleto de Venta de Cambio", "search_purpose": "recuperar paquete exterior si aplica", "source_or_basis": "Disposición Conjunta CGN47/TGN10 de 2008", "caveat": "Condicional."},
    {"key_id": "SK135_119", "request_id": "REQ134_ECON", "key_group": "comdoc_custody", "exact_key": "dos remitos;cuerpos;anexos;último folio;área depositaria", "search_purpose": "probar custodia e integridad", "source_or_basis": "Resolución MINPLAN 1522/2006 actualizada", "caveat": "Comparador contemporáneo, no regla target automática."},
    {"key_id": "SK135_120", "request_id": "REQ134_ECON", "key_group": "comdoc_loss_reconstruction", "exact_key": "búsqueda intensiva;circular COMDOC;copias certificadas;informe explicativo;reconstrucción", "search_purpose": "controlar alegación de pérdida", "source_or_basis": "Resolución MINPLAN 1522/2006 actualizada", "caveat": "Comparador de clases documentales."},
    {"key_id": "SK135_121", "request_id": "REQ134_ECON", "key_group": "debt_instruction_comparator", "exact_key": "nota conjunta ONCP-TGN;archivo de datos;validación;aceptación Caja;registro SIGADE", "search_purpose": "buscar clases análogas de instrucción/aceptación", "source_or_basis": "Resolución Conjunta 216/2008 y 26/2008", "caveat": "Operatoria de consolidación, no recompra target."},
    {"key_id": "SK135_122", "request_id": "REQ134_AGN", "key_group": "hcdn_index_negative_control", "exact_key": "0366-OV-2009;366-OV-2009;0044-OV-2010;44-OV-2010;366/09;44/10", "search_purpose": "repetir búsqueda archivística con variantes exactas", "source_or_basis": "Índice histórico HCDN", "caveat": "Sin coincidencias sólo en el índice público."},
])
assert len(keys) == 122
write_csv(keys_path, keys)

agn_request = HERE / "REQUEST_AGN_2018_REPLY_V135.md"
agn_request.write_text(agn_request.read_text(encoding="utf-8-sig").rstrip() + """

## Clave V135 · inventario público y nota de archivo

La interfaz pública actual de la Comisión no expone, entre la documentación visible revisada, la nota de archivo del `18/05/2012` ni su inventario. El sumario de Diputados del `23/05/2012` prueba un contexto de archivo masivo de expedientes de la Revisora, pero no individualiza `OV 366/09` ni `OV 44/10`; no se lo presenta como disposición de estos casos. Tampoco se hallaron las variantes `0366-OV-2009`, `366-OV-2009`, `0044-OV-2010`, `44-OV-2010`, `366/09` o `44/10` en el índice histórico público de reuniones: es un control negativo limitado, no una afirmación de inexistencia.

Se solicita búsqueda en el fondo histórico por ambos OV, resoluciones y actuaciones AGN, y copia de la nota, remito, inventario, depósito y signatura. Para controlar custodia e integridad, se piden emisor, receptor, firma, fecha, número de cuerpos, anexos, último folio, caja y signatura; si se alegara pérdida, también las actuaciones de búsqueda y reconstrucción que resulten aplicables. Contacto público identificado: `REVISORA@SENADO.GOB.AR`, internos `2310-2315`. Estado: **BORRADOR_NO_ENVIADO**.
""", encoding="utf-8")

econ_request = HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V135.md"
econ_request.write_text(econ_request.read_text(encoding="utf-8-sig").rstrip() + """

## Clave V135 · salida FindDoc y cadena C-41

La especificación oficial de FindDoc prueba que la salida pública era una hoja de ruta: origen, destino, fechas de envío y recepción y ubicación. La AGN documentó una consulta efectiva al mismo endpoint el `05/03/2013` para otro expediente `S01:0130656/2008`, obteniendo estado y ubicación. Estos antecedentes permiten pedir una exportación administrativa equivalente para `S01:0342455/2008`, pero no sustituyen su consulta ni el cuerpo del expediente. Canales oficiales: `ciudadano@mecon.gov.ar`, `0810-333-6326`, Balcarce 186, piso 1, oficina 140.

La alineación visual del Anexo K 2008 confirma que `71597`, `152677` y `2876` pertenecen al renglón `83106000 COMISIONES - BANCO NACION`, por `ARS 32.270,30`; los snippets linealizados que parecen desplazarlos a otra cuenta son descartados como error de extracción. Esto fija la atribución de renglón, no prueba pago ni relación con la recompra.

Para cada número se solicita el C-41 completo y el extracto `SDPGB`/`SDPAG` de 2008 o sucesor equivalente. El esquema oficial histórico permite pedir: OB SIDIF, SAF, beneficiario, importe, estado `P` pagado / `R` rechazado / `A` anulado, fecha, banco, sucursal, tipo y número de cuenta, motivo y medio `RN/CH/TR/TI/NS`. La Cuenta de Inversión 2008 agrega tres clases de huella electrónica: archivo de instrucciones TGN→BCRA y archivos de movimientos y saldos BCRA→TGN. Se requieren los registros target, no sólo la descripción del sistema.

Si alguna orden fue un pago exterior bajo SAF 355/356, se pide además la nota TGN con beneficiario, banco, cuenta, tipo de operación, número SIDIF, moneda, cotización e importe en divisas, y el Boleto de Venta de Cambio BNA. Si no lo fue, basta certificar no aplicabilidad. También se piden remitos COMDOC, cuerpos, anexos, último folio y área depositaria; ante pérdida alegada, búsqueda y reconstrucción aplicables. Ningún número se atribuye por anticipado a la recompra. Estado: **BORRADOR_NO_ENVIADO**.
""", encoding="utf-8")

# Síntesis del checkpoint.
(HERE / "README_V135.md").write_text("""# V135 · estado SIDIF y huella bancaria 2008

V135 confirma visualmente que los SIDIF `71597`, `152677` y `2876` pertenecen al renglón `83106000 COMISIONES - BANCO NACION` por `ARS 32.270,30`; el corrimiento observado en snippets era un error de linealización. Además identifica el esquema oficial `SDPGB/SDPAG` para distinguir `P` pagado, `R` rechazado y `A` anulado, con fecha, beneficiario, banco, cuenta y medio, y prueba que en 2008 TGN/BCRA intercambiaban archivos de instrucciones, movimientos y saldos. Son clases y campos exactos para solicitar; las filas target aún no aparecieron. La custodia COMDOC y el índice parlamentario añaden controles acotados, sin probar pérdida ni disposición. Resultado estricto: 10/10 adjudicaciones, 9/10 cuentas candidatas y 0/10 ejecuciones confirmadas; seis pedidos DRAFT_NOT_SENT.
""", encoding="utf-8")

(HERE / "VEREDICTO_V135.md").write_text("""# Veredicto V135

La alineación visual del Anexo K controla la atribución de fila: `71597`, `152677` y `2876` corresponden a comisiones de Banco Nación; `182705` y `24306` a Bank of New York; `171761` a Letras del Tesoro. La aparente reasignación producida por el snippet queda descartada.

El avance documental es más preciso: `SDPGB` y `SDPAG` contenían pagos, anulaciones y rechazos diarios; el anexo técnico expone OB SIDIF, beneficiario, importe, estado `P/R/A`, fecha, banco, cuenta y medio. La Cuenta de Inversión 2008 demuestra archivos TGN→BCRA de instrucciones y BCRA→TGN de movimientos y saldos. Sin el extracto target o sucesor 2008, la descripción del sistema no convierte una orden en pago.

La regla 2008 de pagos al exterior permite pedir un paquete más rico sólo si alguna orden fue de esa clase. La regla COMDOC de otro ministerio y el procedimiento de consolidación sirven como comparadores contemporáneos de remito, integridad, búsqueda, reconstrucción, instrucción y aceptación; no se trasladan automáticamente a la recompra.

El índice histórico HCDN tampoco contiene las variantes exactas de ambos OV. Es un control negativo de un índice público, no prueba de inexistencia ni destrucción.

La ejecución sigue abierta: 0/10 filas confirmadas. `CLOSED_NETWORK_GATE=NO`; seis borradores, ninguno enviado.
""", encoding="utf-8")

(HERE / "E0_FISCAL_RECONSTRUCTION_V135.md").write_text("""# Reconstrucción fiscal E0 · V135

## Resultado incremental

1. La página original confirma `83106000 COMISIONES - BANCO NACION`, `ARS 32.270,30`, SIDIF `71597`, `152677` y `2876`.
2. `SDPGB/SDPAG` o su sucesor es la salida competente para pedir estado pagado/rechazado/anulado y datos bancarios por OB.
3. En 2008 existían archivos electrónicos diferenciados de instrucción, movimiento y saldo TGN/BCRA.
4. La regla de pagos exteriores agrega nota TGN y boleto de cambio sólo si la clasificación target lo hace aplicable.
5. Los comparadores COMDOC/deuda afinan remitos, folios, búsqueda, reconstrucción, instrucción y aceptación sin adjudicar equivalencia jurídica.
6. La búsqueda pública parlamentaria sigue negativa y limitada; la nota de 18/05/2012 permanece abierta.
7. No cambian transferencia Caja, informe T+3, crédito BCRA ni cancelación CRyL: 0/10 ejecuciones confirmadas.
""", encoding="utf-8")

(HERE / "RETRIEVAL_LOG_V135.md").write_text("""# Registro de recuperación V135

Fecha: 2026-08-30.

1. Se reabrió la página 67 física del Anexo K 2008 y se congeló la alineación visual de Bank of New York, Banco Nación y Letras del Tesoro frente al corrimiento de snippets.
2. Se preservaron Circular TGN 7/97 y Anexo Circular CGN 34/97: `SDPAG`, `SDPGB`, estados `P/R/A`, campos bancarios y medios de pago.
3. Se preservó y verificó visualmente el Tomo II de la Cuenta de Inversión 2008: instrucciones TGN→BCRA y retornos de movimientos/saldos BCRA→TGN.
4. Se preservó la Disposición Conjunta CGN 47/2008-TGN 10/2008, esquema contemporáneo condicional para pagos al exterior SAF 355/356.
5. Se preservaron dos comparadores: custodia/reconstrucción COMDOC y cadena de instrucción/aceptación de otra operatoria de deuda 2008.
6. Se preservó el índice histórico HCDN y se buscaron seis variantes de los dos OV, sin coincidencias; no se codificó ausencia del fondo.
7. Las búsquedas exactas de los tres SIDIF no localizaron cuerpos, extractos de estado, débitos ni C-55 target.
8. No se envió ningún pedido ni se realizó presentación externa.
""", encoding="utf-8")

refs_path = HERE / "SOURCE_REFERENCES_V135.md"
refs_path.write_text(refs_path.read_text(encoding="utf-8-sig").rstrip() + """

- CGN · Cuenta de Inversión 2008, Tomo II: https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/archivos/tomoii.pdf
- CGN/TGN · Disposición Conjunta 47/2008 y 10/2008: https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/2008/adisp47.htm
- CGN · Anexo Circular 34/97, SDPGB: https://www.economia.gob.ar/hacienda/cgn/normas/circulares/1997/cir34a.htm
- TGN · Circular 7/97, pagado diario: https://www.economia.gob.ar/digesto/circulares/tgn/1997/cirtgn07.htm
- Economía · índice del Digesto, capítulo III: https://www.economia.gob.ar/digesto/capi3.htm
- MINPLAN · Resolución 1522/2006 actualizada: https://www.argentina.gob.ar/normativa/nacional/norma-119314/actualizacion
- Secretaría de Hacienda/Finanzas · Resolución Conjunta 216/2008 y 26/2008: https://www.argentina.gob.ar/normativa/nacional/norma-144186/texto
- HCDN · índice histórico de reuniones: https://www4.hcdn.gov.ar/sesionesxml/reuniones.php

El esquema de estado y las clases de archivo determinan qué pedir; no responden todavía cuál fue el estado de las tres órdenes.
""", encoding="utf-8")

handover = """# Handover V135 → V136

## Estado congelado

- Diez adjudicaciones participante-instrumento exactas; nueve cuentas BCRA candidatas; MERVAL abierta; 0/10 ejecuciones confirmadas.
- Alineación visual exacta: cuenta `83106000`, Banco Nación, ARS 32.270,30, SIDIF `71597`, `152677`, `2876`; el corrimiento de snippet es falso.
- Esquema `SDPGB/SDPAG`: identidad OB, beneficiario, importe, `P/R/A`, fecha, banco, cuenta y medio; filas target no localizadas.
- Sistema 2008: clases de archivo de instrucción TGN→BCRA, movimientos y saldos BCRA→TGN probadas; vínculos target abiertos.
- Pago exterior: paquete documental exacto probado en 2008, sólo condicional a clasificación SAF 355/356.
- COMDOC/deuda: comparadores de remito, folios, búsqueda/reconstrucción, nota, aceptación y SIGADE; no equivalencia target.
- Bicameral: seis variantes exactas de los dos OV sin coincidencia en el índice HCDN; nota 18/05/2012 abierta.
- Seis pedidos DRAFT_NOT_SENT; ninguno enviado; panel estricto sin cambios.

## Prioridad V136

1. Si hay autorización expresa, presentar los seis pedidos; si no, mantenerlos como borradores.
2. Buscar extractos `SDPGB/SDPAG` 2008 o sucesor por OB `71597`, `152677`, `2876`.
3. Buscar archivos de instrucción TGN→BCRA y movimientos/saldos BCRA→TGN por esos identificadores, fechas y cuentas.
4. Probar o descartar clasificación exterior de cada orden antes de aplicar la Disposición 47/10.
5. Buscar remitos/cuerpos/anexos/último folio de `S01:0342455/2008` y nota/remito/inventario de ambos OV.
6. Mantener separados orden, estado SIDIF, instrucción, movimiento, Caja, crédito BCRA y cancelación CRyL.
"""
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V135_A_V136.md").write_text(handover, encoding="utf-8")

(HERE / "AUDITORIA_V135.md").write_text(f"""# Auditoría V135

- Fuentes maestras: {len(catalog)}; ocho fuentes oficiales nuevas preservadas.
- Fuentes primarias E0: {len(census)}.
- Ledger fiscal: {len(ledger)} filas; cortes metodológicos: {len(breaks)}.
- FindDoc: 5 controles de capacidad/salida/target; target sin consulta ejecutada.
- C-41/estado: {len(c41_chain)} etapas; esquema `P/R/A` y archivos 2008 probados; filas target abiertas.
- Controles nuevos: {len(anexo_k_alignment)} alineaciones, {len(payment_state_schema)} campos/códigos, {len(tgn_system_records)} clases de registro, {len(comdoc_custody)} controles comparadores.
- Bicameral: {len(bicameral)} controles; nota exacta e inventario abiertos.
- Escalera: 10 adjudicaciones; 9 cuentas candidatas; 0 ejecuciones confirmadas.
- Pedidos: 6 borradores, 0 enviados; {len(trace)} objetos y {len(keys)} claves.
- Panel estricto: 30 entidades; {STRICT}% sin cambios.
""", encoding="utf-8")

# Auditoría física y estado global.
for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    shutil.copyfile(AUDIT / f"{stem}_V134.csv", AUDIT / f"{stem}_V135.csv")

hash_rows = []
for row in catalog:
    local = row["archivo_local"]
    path = REPO / local.lstrip("/") if local else None
    exists = bool(path and path.is_file())
    actual = sha256(path) if exists else ""
    expected = row["sha256"]
    hash_rows.append({"id": row["id"], "archivo_local": local, "exists": str(exists), "sha_catalog": expected, "sha_actual": actual, "hash_ok": str(bool(exists and expected and actual.lower() == expected.lower()))})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V135.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V135.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
assert physical == hash_ok == 371

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or "tmp" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": str(size), "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V135.csv", size_rows)

completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V134.json").read_text(encoding="utf-8"))
for key in list(completeness):
    if key.endswith("_v134") or "newly_preserved_v134" in key:
        completeness.pop(key, None)
completeness.update({
    "checkpoint": "V135", "date": "2026-08-30",
    "state": "E0_PAYMENT_STATE_OUTPUT_SCHEMA_AND_2008_SYSTEM_RECORD_CLASSES_PROVED_TARGET_ROWS_OPEN_NOT_SENT",
    "numeric_v135_strict_changed": False, "master_catalog_entries": len(catalog),
    "physical_local_copies": physical, "physical_local_hash_ok": hash_ok,
    "e0_primary_sources_preserved": len(census), "e0_quality": "PRIMARY_PAYMENT_STATE_SCHEMA_AND_2008_SYSTEM_RECORD_CONTROLS",
    "sources_newly_preserved_v135": 8, "e0_primary_sources_newly_preserved_v135": 8,
    "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
    "e0_request_traceability_rows": len(trace), "e0_request_search_keys": len(keys),
    "e0_finddoc_capability_rows": len(finddoc), "e0_finddoc_target_query_executed": False,
    "e0_c41_chain_rows": len(c41_chain), "e0_c41_target_ids": 3, "e0_c41_target_bodies_located": 0,
    "e0_c41_target_payment_state_rows_located": 0,
    "e0_anexo_k_visual_alignment_rows": len(anexo_k_alignment),
    "e0_sidif_payment_state_schema_rows": len(payment_state_schema),
    "e0_tgn_bcra_2008_record_class_rows": len(tgn_system_records),
    "e0_comdoc_custody_comparator_rows": len(comdoc_custody),
    "e0_bicameral_inventory_control_rows": len(bicameral), "e0_bicameral_exact_note_body_located": False,
    "e0_settlement_award_rows_exact": 10, "e0_settlement_account_candidate_rows": 9,
    "e0_settlement_executed_rows_confirmed": 0, "e0_requests_submitted": 0,
    "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
    "historical_workstream": "Exact Anexo K row alignment, SIDIF P/R/A output schema and 2008 TGN-BCRA record classes proved; target payment-state rows, instructions, movements, COMDOC route/body, Bicameral note and executed settlement remain open; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V135.json").write_text(json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V135 · estado SIDIF y huella bancaria 2008"
text = backup.read_text(encoding="utf-8-sig")
if marker not in text:
    text += f"\n\n{marker}\n\n- Alineación visual Anexo K congelada: cuenta 83106000/BNA/ARS 32.270,30/SIDIF 71597, 152677 y 2876.\n- Esquema SDPGB/SDPAG con estados P/R/A, campos bancarios y medios de pago probado; filas target abiertas.\n- Archivos 2008 de instrucciones TGN→BCRA y movimientos/saldos BCRA→TGN probados como clases; vínculos target abiertos.\n- Controles COMDOC/deuda y búsqueda HCDN usados sólo como comparadores y controles negativos.\n- Escalera sin cambio: 10 adjudicaciones, 9 cuentas candidatas, 0 ejecuciones confirmadas; seis borradores no enviados.\n"
    backup.write_text(text, encoding="utf-8")

inherited = [
    {"script": "qa_v134.py", "pre_v135_result": "PASS", "post_v135_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V134 queda supersedido por nuevas fuentes y conteos V135."},
    {"script": "qa_v135.py", "pre_v135_result": "N/A", "post_v135_result": "PASS", "interpretation": "Alineación Anexo K, esquema P/R/A, archivos TGN/BCRA, comparadores, hashes y no ejecución verificados."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V135.csv", inherited)

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

finddoc = rows("E0_COMDOC_FINDDOC_CAPABILITY_V135.csv")
assert len(finddoc) == 5 and finddoc[-1]["status"] == "TARGET_QUERY_UNEXECUTED_ADMINISTRATIVE_EXPORT_REQUIRED"
assert "origen" in finddoc[1]["output_schema"] and "fecha de recepción" in finddoc[1]["output_schema"]
comdoc = rows("E0_COMDOC_LEGACY_QUERY_ROUTE_V135.csv")
assert len(comdoc) == 5 and comdoc[-1]["body_query_executed"] == "NO"

c41 = rows("E0_C41_PAYMENT_EXECUTION_CHAIN_V135.csv")
assert len(c41) == 12 and c41[0]["stage"] == "C41_ISSUED" and c41[-1]["target_status"] == "OPEN"
assert "71597" in c41[-1]["required_or_visible_fields"]
bicameral = rows("E0_BICAMERAL_PUBLIC_INVENTORY_AUDIT_V135.csv")
assert len(bicameral) == 7 and bicameral[-1]["status"] == "CONTEMPORANEOUS_CUSTODY_COMPARATOR_NOT_TARGET_RULE"

alignment = rows("E0_2008_ANEXO_K_VISUAL_ALIGNMENT_CONTROL_V135.csv")
assert len(alignment) == 4 and alignment[1]["sidif_ids"] == "71597;152677;2876"
assert alignment[2]["sidif_ids"] == "171761"
payment = rows("E0_SIDIF_PAID_BENEFICIARY_FILE_SCHEMA_V135.csv")
assert len(payment) == 8 and payment[2]["field_or_code"] == "P;R;A"
records = rows("E0_TGN_BCRA_2008_PAYMENT_RECORD_CLASSES_V135.csv")
assert len(records) == 6 and records[0]["direction"] == "TGN→BCRA"
custody = rows("E0_COMDOC_CUSTODY_AND_DEBT_INSTRUCTION_COMPARATOR_V135.csv")
assert len(custody) == 8 and custody[-1]["scope_status"] == "OTHER_DEBT_PROCEDURE_COMPARATOR"

assert len(rows("E0_EXPEDIENT_PUBLIC_SEARCH_EXHAUSTION_V135.csv")) == 13
assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V135.csv")) == 166
assert len(rows("E0_FISCAL_METHOD_BREAKS_V135.csv")) == 127
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V135.csv")) == 118
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V135.csv")) == 122
ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V135.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V135.csv")}
new_ids = {"e0_cgn_cuenta_inversion_2008_tomo_ii_tgn_system_files", "e0_cgn_tgn_disposicion_conjunta_47_10_2008_external_payments", "e0_cgn_circular_34_1997_sdpgb_paid_beneficiary_schema", "e0_tgn_circular_7_1997_daily_paid_files", "e0_economia_digesto_chapter_3_tgn_index", "e0_minplan_resolution_1522_2006_comdoc_custody", "e0_debt_joint_resolution_216_26_2008_instruction_chain", "e0_hcdn_historic_plenary_index_negative_control"}
assert len(census) == 137 and new_ids <= set(census)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 377 and len({r["id"] for r in catalog}) == 377

expected = {
    "cgn_circular_34_1997_archivo_pagado_beneficiario.html": (23844, "d4019e3d1fb5ed2a426ab729e5c2512ff23a7eabc52d41fd910a0ae0a56fdd64"),
    "cgn_cuenta_inversion_2008_tomo_ii.pdf": (3450121, "a4047cec54c88efeff97d5f6602c45277cd4e813c71f3df1d8bab45dd40594ae"),
    "cgn_tgn_disposicion_conjunta_47_10_2008_pagos_exterior.html": (10869, "785381b2ae7ce14970b6f609264ba6a06a05e07aebd3645bcf163a2a49370874"),
    "deuda_resolucion_conjunta_216_26_2008_comdoc_instruccion.html": (59049, "f040e86ae5a1aa18ce11467d70b1559bb2a820303ad0912aab6c159fd280ab47"),
    "economia_digesto_capitulo_3_indice.html": (40882, "52d810ec5efffaaf3fbef071e2683648dcfce2398553a10ec5f64ad6d4142ea2"),
    "hcdn_indice_reuniones_historicas.html": (3653023, "ead063451f983ba1eff810c28dd1330c968684470a73aca8181226c2d106df3b"),
    "minplan_resolucion_1522_2006_comdoc_custodia.html": (93449, "fda42ee250f8989a97122e38ef7c7e4a3527e1de46afeeb9696dceb2ed04f0e9"),
    "tgn_circular_7_1997_pagado_diario.html": (3362, "b24b54c462369508e47ead79c87b11618ac7796c581b3b5775658fdc6a40105e"),
}
bin_dir = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v135" / "binaries"
assert len(list(bin_dir.iterdir())) == 8
for name, (size, digest) in expected.items():
    path = bin_dir / name
    assert path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest() == digest

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V135.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V135"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 371
assert complete["e0_c41_target_payment_state_rows_located"] == 0
assert complete["e0_sidif_payment_state_schema_rows"] == 8
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v135_strict_changed"] is False

for name, marker in {
    "REQUEST_AGN_2018_REPLY_V135.md": "## Clave V135 · inventario público y nota de archivo",
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V135.md": "## Clave V135 · salida FindDoc y cadena C-41",
}.items():
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert marker in text and "BORRADOR_NO_ENVIADO" in text

for name in ("README_V135.md", "VEREDICTO_V135.md", "E0_FISCAL_RECONSTRUCTION_V135.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V135_A_V136.md"):
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")

print("V135 QA PASS")
'''
(HERE / "qa_v135.py").write_text(qa, encoding="utf-8")

def checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V135.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V135", "parent_checkpoint": "V134",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": 8, "new_primary_sources": 8,
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks),
        "finddoc_capability_rows": len(finddoc), "finddoc_target_query_executed": False,
        "c41_chain_rows": len(c41_chain), "c41_target_ids": 3, "c41_target_bodies_located": 0,
        "c41_target_payment_state_rows_located": 0,
        "anexo_k_visual_alignment_rows": len(anexo_k_alignment),
        "sidif_payment_state_schema_rows": len(payment_state_schema),
        "tgn_bcra_2008_record_class_rows": len(tgn_system_records),
        "comdoc_custody_comparator_rows": len(comdoc_custody),
        "bicameral_control_rows": len(bicameral), "bicameral_exact_note_body_located": False,
        "award_rows_exact": 10, "account_candidate_rows": 9, "executed_settlement_rows_confirmed": 0,
        "request_drafts": 6, "request_traceability_rows": len(trace), "request_search_keys": len(keys),
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V135.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    "checkpoint": "V135", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical copies SHA-valid; Anexo K alignment, SIDIF P/R/A schema and 2008 TGN-BCRA record classes proved; zero of ten executed settlement rows confirmed; six requests drafted and none submitted.",
    "historical_workstream": "Target SDPGB/SDPAG rows, payment instructions, bank movements, COMDOC route/body, Bicameral note and executed settlement remain open; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V135 BUILD PASS")
