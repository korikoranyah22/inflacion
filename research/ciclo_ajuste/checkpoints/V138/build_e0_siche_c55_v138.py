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
PARENT = HERE.parent / "V137"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v138" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


EXPECTED = {
    "argentina_dgsiaf_siche_landing.html": (28514, "b3b406e2fc8c877697c5079c9b5c93602cbeee4bb942687f50441cfb918d8643"),
    "argentina_dgsiaf_slu_landing.html": (60179, "47cdbd46df0303a4ff3ba93a2ef5df7d596584843447d2c67cdd46f1520524a9"),
    "argentina_esidif_consultas_reportes_pagos_2013.pdf": (933107, "85de6b2645a11b2001575be1e4afa71783598227707d7a80bc073eb1786696a3"),
    "argentina_esidif_pagos_landing.html": (35485, "8854496b7955c45487a16750c66ecfa6541429a1239137467618a3e21de2be0a"),
    "argentina_resolucion_53_2024_siche.pdf": (166521, "1ad76881f500202c2557df9164e1b77a1c7222f9e40a20d430174038041c4a47"),
    "cgn_circular_05_2000_c55_regularization.html": (11277, "33ff6f2e0846d6ecddb3df183a4a48ee33aad0154a13538969c89cd63c78260a"),
    "cgn_circular_13_2002_foreign_payments.html": (9206, "88b09113bdbdb39ea9d90175d3c889e052c9d24649fdb4c38ecb7be35597357a"),
    "cgn_circular_22_2004_note_regularization.html": (8534, "626d6c57662055cc96756f9f203e843631f9ac9e5c144952e7ec7a8fe62cd3c7"),
    "cgn_cuenta_2010_esidif_saf355_deployment.html": (58482, "d0959a23bf1fd016f5ed38d07403201826b634613e55e4910680ab7c06848fc1"),
    "cgn_disposition_31_2006_parameterized_reports.html": (16804, "3b54ab0cee1c6b0f3e1644f7f5eaf671fadc08758235f64444aea180189fa9df"),
    "cgn_tgn_disposition_47_10_2008_foreign_payments_annex.html": (10869, "785381b2ae7ce14970b6f609264ba6a06a05e07aebd3645bcf163a2a49370874"),
    "cgn_tgn_disposition_47_10_2008_foreign_payments.html": (8398, "3d318e6b41f02116cb9cd68560e65a048cb5fe167d6d87a0d594a23c8e9e25e8"),
    "dgsiaf_slu_emite_consulta_pagos.doc": (161280, "05771a154e294999a86b4dc5c5f28429876e17e4c68adf15f1bfb060422d72cb"),
    "dgsiaf_slu_gastos_ingreso_numero_sidif.doc": (313856, "7a04b63200dbe5503d98f8975f6a4eef0f4960ab5e80bf2004c8f1747c4f6a51"),
    "dgsiaf_slu_nota_de_pago.doc": (996864, "cbc3861a11178583cede1161ab1f43fbb9eb05d59c5a7c1069fbaec452834eb4"),
    "dgsiaf_slu_regularizacion_global.doc": (617984, "389e2081612dfdad0efc4dba3355b993698fb0ea302ac3e42a32c8794c2b4f42"),
    "dgsiaf_slu_reportes_conciliacion_bancaria.doc": (730624, "141cf858a16714cf282a4d823b77b823d57f7038b63cdf627b5ae33a98e2472e"),
    "dgsiaf_slu_reportes_gastos.doc": (1448960, "9764c7ddff9ceeb2055f85e95b465ed8664ba16571df53fea0b1d78d1b5633a4"),
    "dgsiaf_slu_reportes_pagos.doc": (1211392, "90ddd573ef7bd967ea4e89cf0852a3300dbd54abde913bee3050ee845af0b9d1"),
}


def source(source_id, filename, institution, title, url, publication, period, code,
           families, breaks, use, caveat, note, transport="SECURE_DIRECT"):
    size, digest = EXPECTED[filename]
    suffix = Path(filename).suffix.lower()
    source_type = {".pdf": "PDF oficial · captura preservada", ".doc": "DOC oficial · binario preservado"}.get(
        suffix, "HTML oficial · captura preservada"
    )
    return {
        "id": source_id, "filename": filename, "institution": institution,
        "title": title, "url": url, "publication": publication, "period": period,
        "code": code, "families": families, "breaks": breaks, "use": use,
        "caveat": caveat, "note": note, "bytes": size, "sha256": digest,
        "type": source_type, "transport": transport,
    }


SOURCES = [
    source("e0_dgsiaf_siche_landing", "argentina_dgsiaf_siche_landing.html", "Dirección General de Sistemas Informáticos de Administración Financiera", "SICHE · Sistema de Consulta de Información para Sistemas Heredados", "https://www.argentina.gob.ar/economia/sechacienda/dgsiaf/siche", "consulta 2026-08-30", "vigente 2026", "SICHE", "legacy_systems;historical_queries;access", "página pública descriptiva versus acceso interno", "USABLE_CURRENT_LEGACY_QUERY_ROUTE", "Describe la función; no contiene datos target ni credenciales de acceso.", "V138 E0: confirma que SICHE estandariza el acceso a información de sistemas desafectados."),
    source("e0_dgsiaf_slu_landing", "argentina_dgsiaf_slu_landing.html", "Dirección General de Sistemas Informáticos de Administración Financiera", "SLU · manuales y transición a SICHE", "https://www.argentina.gob.ar/economia/sechacienda/dgsiaf/slu", "consulta 2026-08-30", "sistemas heredados", "SLU", "SLU;SICHE;manuales", "SLU parcialmente operativo versus información disponibilizada en SICHE", "USABLE_OFFICIAL_MANUAL_INDEX_AND_TRANSITION", "La página no prueba que cada base SAF 355 esté completa.", "V138 E0: publica los manuales históricos y declara que la información SLU se disponibiliza en SICHE."),
    source("e0_argentina_resolution_53_2024_siche", "argentina_resolucion_53_2024_siche.pdf", "Secretaría de Hacienda", "Resolución SH 53/2024 · SICHE como consulta única de sistemas discontinuados", "https://www.argentina.gob.ar/sites/default/files/rs-2024-65612078-apn-shmec.pdf", "2024-06-24", "desde 2024-07-01", "RESOL-2024-53-APN-SH#MEC", "SICHE;SIDIF_Central;SLU;export;integrity", "herramienta existente versus disponibilidad de cada fila", "USABLE_CURRENT_BINDING_LEGACY_QUERY_AUTHORITY", "La resolución garantiza la ruta y preservación sin transformación, no la existencia de los registros target.", "V138 E0: SICHE es la única herramienta para SC, BUDI y SLU discontinuados; permite filtros y exportación a planilla."),
    source("e0_dgsiaf_esidif_payments_landing", "argentina_esidif_pagos_landing.html", "Dirección General de Sistemas Informáticos de Administración Financiera", "e-SIDIF · módulo Pagos y guías", "https://www.argentina.gob.ar/economia/sechacienda/dgsiaf/e-sidif/pagos", "consulta 2026-08-30", "vigente 2026", "e-SIDIF Pagos", "payment_queries;PG;NPG;TGN", "funcionalidad actual versus target heredado 2008", "USABLE_CURRENT_QUERY_CAPABILITY_INDEX", "No prueba migración completa de 2008.", "V138 E0: publica consultas de OP/pagos, Nota de Pago, transmisión TGN y reportes."),
    source("e0_dgsiaf_esidif_payment_queries_2013", "argentina_esidif_consultas_reportes_pagos_2013.pdf", "Dirección General de Sistemas Informáticos de Administración Financiera", "e-SIDIF · Consultas y Reportes de Pagos", "https://www.argentina.gob.ar/sites/default/files/dgsiaf-2013_esidif_pagos_consultas_reportes_pagos_abril_2013.pdf", "2013-04", "2013; función actual", "PG; OP; Nro SIDIF", "payment_query;original_voucher;payer;payment_medium;budget_item", "modelo e-SIDIF posterior versus registro SLU/SC 2008", "USABLE_QUERY_FIELD_CROSSWALK", "Sirve como control de campos y vínculos, no como prueba de que el target migró.", "V138 E0: permite buscar por tipo, ejercicio, número interno o SIDIF y relacionar OP, PG, medio e imputación."),
    source("e0_cgn_account_2010_saf355_esidif_deployment", "cgn_cuenta_2010_esidif_saf355_deployment.html", "Contaduría General de la Nación", "Cuenta de Inversión 2010 · despliegue e-SIDIF en SAF 355", "https://www.economia.gob.ar/hacienda/cgn/cuenta/2010/tomoi/03aspectos.htm", "2011", "2010", "SAF 355; e-SIDIF", "SAF355;deployment;queries;all_businesses", "despliegue 2010 versus origen 2008", "USABLE_TEMPORAL_SYSTEM_CROSSWALK", "No identifica qué sistema local originó cada fila de 2008 ni su migración.", "V138 E0: en septiembre de 2010 se desplegaron consultas y listados de todos los negocios e-SIDIF en SAF 355.", "TLS_EXPIRED_OFFICIAL_SERVER"),
    source("e0_cgn_circular_05_2000_c55_regularization", "cgn_circular_05_2000_c55_regularization.html", "Contaduría General de la Nación", "Circular CGN 05/2000 · C-55 de regularización y desafectación", "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/2000/circ05.htm", "2000-02-25", "2000-2008", "Circular 05/00; C-55", "C55;regularization;note_payment;bank_account;SIDIF", "regularización genérica versus target", "USABLE_CONTEMPORANEOUS_C55_RULE", "No identifica las tres referencias SIDIF.", "V138 E0: el C-55 regulariza pagos por Nota y referencia documento original, cuenta debitada y número SIDIF.", "TLS_EXPIRED_OFFICIAL_SERVER"),
    source("e0_cgn_circular_13_2002_foreign_payments", "cgn_circular_13_2002_foreign_payments.html", "Contaduría General de la Nación", "Circular CGN 13/2002 · pagos al exterior SAF 355", "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/2002/circ13.htm", "2002-04-26", "2002-11/2008", "Circular 13/02", "SAF355;foreign_payment;C41;BNA;BCRA;commission_account", "orden exterior versus comisión target", "USABLE_CONTEMPORANEOUS_FOREIGN_PAYMENT_ROUTE", "La coincidencia conceptual no prueba que los tres target provengan de transferencias exteriores.", "V138 E0: SAF 355 podía usar BCRA/BNA; la nota debía identificar SIDIF y la cuenta del fondo rotatorio para gastos y comisiones.", "TLS_EXPIRED_OFFICIAL_SERVER"),
    source("e0_cgn_circular_22_2004_note_regularization", "cgn_circular_22_2004_note_regularization.html", "Contaduría General de la Nación", "Circular CGN 22/2004 · regularización de pagos por Nota", "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/2004/cir22.htm", "2004", "2004-2008", "Circular 22/04", "C55;note_payment;BNA_debit;regularization", "diferencia de débito versus comisión pura", "USABLE_CONTEMPORANEOUS_NOTE_REGULARIZATION", "Regula diferencias en pagos por Nota; no asigna tipo a los tres SIDIF.", "V138 E0: conecta débito BNA, C-41/C-42 y C-55 de regularización/desafectación.", "TLS_EXPIRED_OFFICIAL_SERVER"),
    source("e0_cgn_disposition_31_2006_parameterized_reports", "cgn_disposition_31_2006_parameterized_reports.html", "Contaduría General de la Nación", "Disposición CGN 31/2006 · listados parametrizados", "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/2006/disp31.htm", "2006", "2006-2008", "Disposición 31/06", "SLU;parameterized_report;commitment;accrual;paid", "agregado presupuestario versus fila target", "USABLE_CONTEMPORANEOUS_REPORT_AUTHORITY", "El listado normado es agregado y no sustituye el detalle por comprobante.", "V138 E0: CGN podía requerir al SAF listados parametrizados SLU con compromiso, devengado y pagado.", "TLS_EXPIRED_OFFICIAL_SERVER"),
    source("e0_cgn_tgn_disposition_47_10_2008_foreign_payments", "cgn_tgn_disposition_47_10_2008_foreign_payments.html", "Contaduría General de la Nación / Tesorería General de la Nación", "Disposición Conjunta CGN 47/08 y TGN 10/08 · pagos al exterior", "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/2008/disp47.htm", "2008-11-20", "desde 2008-11-20", "Disposición 47/08 CGN; 10/08 TGN", "foreign_payment;C41;paper;note;exchange_ticket", "vigencia desde noviembre versus target anual", "USABLE_LATE_2008_FOREIGN_PAYMENT_AUTHORITY", "Sólo rige desde su fecha; para meses previos se usa Circular 13/02.", "V138 E0: exige C-41, Nota y Boleto de Venta de Cambio para pagos al exterior.", "TLS_EXPIRED_OFFICIAL_SERVER"),
    source("e0_cgn_tgn_disposition_47_10_2008_foreign_payments_annex", "cgn_tgn_disposition_47_10_2008_foreign_payments_annex.html", "Contaduría General de la Nación / Tesorería General de la Nación", "Anexo Disposición Conjunta 47/08-10/08 · circuito exterior", "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/2008/adisp47.htm", "2008-11-20", "desde 2008-11-20", "Anexo Disposición 47/08-10/08", "SAF355;BNA;BCRA;C41;commission_debit;payment_instruction", "ruta exterior versus comisión target", "USABLE_EXACT_LATE_2008_COMMISSION_ACCOUNT_ROUTE", "No identifica los tres documentos ni el total de $32.270,30.", "V138 E0: para SAF 355 el beneficiario podía ser BNA/BCRA y la nota debía señalar la cuenta debitada por gastos y comisiones.", "TLS_EXPIRED_OFFICIAL_SERVER"),
    source("e0_dgsiaf_slu_payment_query_2004", "dgsiaf_slu_emite_consulta_pagos.doc", "Dirección General de Sistemas Informáticos de Administración Financiera", "SLU · Consulta de Pagos", "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_emite_cons_pagos.doc", "2004-03", "2004-2008", "PG_CPAR_EMITE_CONS_PAGO", "SLU;payment_date;order_type;bank;account;beneficiary", "manual de funcionalidad versus filas target", "USABLE_CONTEMPORANEOUS_PAYMENT_QUERY_SCHEMA", "No contiene datos de SAF 355.", "V138 E0: consulta pagos por fecha, ejercicio/tipo/rango de OP, banco, cuenta, estado y beneficiario."),
    source("e0_dgsiaf_slu_sidif_number_input_2003", "dgsiaf_slu_gastos_ingreso_numero_sidif.doc", "Dirección General de Sistemas Informáticos de Administración Financiera", "SLU · Gastos · Ingreso y modificación del número SIDIF", "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_gs_gtos_ingreso_nro_sidif.doc", "2003-12", "2003-2008", "Ingreso Nro. SIDIF", "SLU;SIDIF_number;C41;C42;C55", "función de ingreso manual versus universo completo del SIDIF", "USABLE_CONTEMPORANEOUS_TYPE_NARROWING", "Prueba los tipos permitidos en esta función SLU, no que todo número SIDIF del universo pertenezca necesariamente a esos tipos.", "V138 E0: el ingreso manual de número SIDIF admite C-41, C-42 y C-55 confirmados."),
    source("e0_dgsiaf_slu_note_payment_2001", "dgsiaf_slu_nota_de_pago.doc", "Dirección General de Sistemas Informáticos de Administración Financiera", "SLU · Nota de Pago", "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_nota_de_pago.doc", "2001-06", "2001-2008", "Nota de Pago SLU", "note_payment;C41;bank_accounts;commission_account;history", "manual de gestión versus nota target", "USABLE_CONTEMPORANEOUS_NOTE_PAYMENT_SCHEMA", "No contiene la Nota ni la instrucción de los target.", "V138 E0: la Nota vincula OP, beneficiario, documento, cuentas pagadora/receptora/de gastos, estados e historia."),
    source("e0_dgsiaf_slu_global_regularization_2004", "dgsiaf_slu_regularizacion_global.doc", "Dirección General de Sistemas Informáticos de Administración Financiera", "SLU · Regularización Global", "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_gs_regularizacion_global.doc", "2004-04; rev. 2005-06", "2004-2008", "C55-REG; Débito Directo", "C55;direct_debit;bank_commission;budget;book_bank;SIDIF_Central", "coincidencia de mecanismo versus identificación target", "USABLE_CONTEMPORANEOUS_DIRECT_DEBIT_MECHANISM", "Hace a C-55 la hipótesis prioritaria, pero no reemplaza la exportación target.", "V138 E0: un débito bancario por comisión se registra como C-55 Débito Directo, afecta pagado y Libro Banco tras aceptación central."),
    source("e0_dgsiaf_slu_bank_reconciliation_reports_2002", "dgsiaf_slu_reportes_conciliacion_bancaria.doc", "Dirección General de Sistemas Informáticos de Administración Financiera", "SLU · Reportes de Conciliación Bancaria", "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_reportes_conciliacion_bancaria.doc", "2002-09", "2002-2008", "conc_01.rep; conc_02.rep", "bank_extract;book_bank;reconciliation;form_type;beneficiary", "capacidad de reporte versus retención de cada movimiento", "USABLE_CONTEMPORANEOUS_RECONCILIATION_SCHEMA", "No contiene extractos o Libro Banco target.", "V138 E0: reporta estado de conciliación, fechas, movimiento, debe/haber/saldo y tipo/número de formulario."),
    source("e0_dgsiaf_slu_expense_reports_2003", "dgsiaf_slu_reportes_gastos.doc", "Dirección General de Sistemas Informáticos de Administración Financiera", "SLU · Reportes de Gastos", "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_reportes_gastos.doc", "2003-03", "2003-2008", "gastos_01.rep", "C41;C42;C55;supporting_document;beneficiary;paid;regularized", "reporte disponible versus exportación target no obtenida", "USABLE_CONTEMPORANEOUS_EXPENSE_EXPORT_SCHEMA", "La columna pagado es informativa y debe cruzarse con pagos/Libro Banco.", "V138 E0: gastos_01 identifica tipo/número, documento, beneficiario, clase, objeto, pagado y regularizado."),
    source("e0_dgsiaf_slu_payment_reports_2003", "dgsiaf_slu_reportes_pagos.doc", "Dirección General de Sistemas Informáticos de Administración Financiera", "SLU · Reportes de Pagos", "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_reportes_pagos.doc", "2003-03", "2003-2008", "pagos_02.rep; pagos_04.rep; F80", "F80;order;payment;beneficiary;payer;source;regularized", "reporte disponible versus exportación target no obtenida", "USABLE_CONTEMPORANEOUS_PAYMENT_EXPORT_SCHEMA", "Un F80/importe pagado debe cruzarse con rendición y conciliación.", "V138 E0: permite vincular orden, F80, pagador, fuente, beneficiario, pagado y regularizado."),
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
    skip = {"build_e0_amiddf_access_v137.py", "qa_v137.py", "MANIFEST_V137.json", "INHERITED_QA_STATUS_V137.csv"}
    for item in PARENT.iterdir():
        if not item.is_file() or item.name in skip or item.name.startswith("HANDOVER_PROXIMA_SESION"):
            continue
        target = HERE / item.name.replace("V137", "V138")
        text = item.read_text(encoding="utf-8-sig").replace("V137", "V138").replace("v137", "v138")
        target.write_text(text, encoding="utf-8")


clone_parent()

for item in SOURCES:
    path = BIN / item["filename"]
    assert path.is_file() and path.stat().st_size == item["bytes"], path
    assert sha256(path) == item["sha256"], path
    item["local"] = "/" + path.relative_to(REPO).as_posix()

source_ids = {item["id"] for item in SOURCES}

# Catálogo maestro, censo E0 y procedencia física.
catalog = [row for row in read_csv(CATALOG) if row["id"] not in source_ids]
for item in SOURCES:
    catalog.append({
        "id": item["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": item["institution"],
        "titulo": item["title"], "url_original": item["url"], "archivo_local": item["local"],
        "fecha_descarga": "2026-08-30", "fecha_publicacion": item["publication"],
        "codigo_serie": item["code"], "periodo_utilizado": item["period"], "tipo": item["type"],
        "sha256": item["sha256"], "nota": item["note"],
    })
assert len(catalog) == 422 and len({row["id"] for row in catalog}) == 422
write_csv(CATALOG, catalog)

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V138.csv"
census = [row for row in read_csv(census_path) if row["source_id"] not in source_ids]
for item in SOURCES:
    census.append({
        "source_id": item["id"], "institution": item["institution"], "artifact": item["title"],
        "url": item["url"], "local_path": item["local"], "sha256": item["sha256"],
        "bytes": str(item["bytes"]), "period_coverage": item["period"],
        "variable_families": item["families"], "primary_source": "YES", "preserved": "YES",
        "method_breaks": item["breaks"], "use_status": item["use"], "caveat": item["caveat"],
    })
assert len(census) == 182 and len({row["source_id"] for row in census}) == 182
write_csv(census_path, census)

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V138.csv"
provenance = [row for row in read_csv(provenance_path) if row["source_id"] not in source_ids]
for item in SOURCES:
    transport_note = (
        "Descarga directa desde dominio oficial con curl --insecure porque el certificado TLS del servidor histórico estaba vencido; contenido cotejado con el índice oficial y preservado con SHA-256."
        if item["transport"] == "TLS_EXPIRED_OFFICIAL_SERVER"
        else "Descarga directa segura desde dominio oficial; binario preservado con SHA-256."
    )
    provenance.append({
        "source_id": item["id"], "original_url": item["url"], "retrieval_url": item["url"],
        "capture_timestamp": "20260830", "cdx_digest": "N/A_DIRECT_OFFICIAL", "local_path": item["local"],
        "sha256": item["sha256"], "bytes": str(item["bytes"]), "provenance_note": transport_note,
    })
assert len(provenance) == 85
write_csv(provenance_path, provenance)

# Autoridad vigente de SICHE y alcance exacto de la consulta.
siche_authority = [
    {"rule_id": "SA138_01", "proposition": "SICHE es la única herramienta para sistemas discontinuados", "operative_detail": "aprobación por Resolución SH 53/2024", "target_effect": "la búsqueda oficial debe ejecutarse en SICHE", "source_id": "e0_argentina_resolution_53_2024_siche", "status": "PROVED"},
    {"rule_id": "SA138_02", "proposition": "SIDIF Central quedó bajo SICHE", "operative_detail": "acceso anterior desafectado desde 2024-07-01", "target_effect": "consultar SC por los tres N° SIDIF", "source_id": "e0_argentina_resolution_53_2024_siche", "status": "PROVED"},
    {"rule_id": "SA138_03", "proposition": "SLU quedó bajo SICHE", "operative_detail": "acceso anterior desafectado desde 2024-07-01", "target_effect": "consultar SLU SAF 355 y cruzar SC", "source_id": "e0_argentina_resolution_53_2024_siche;e0_dgsiaf_slu_landing", "status": "PROVED"},
    {"rule_id": "SA138_04", "proposition": "SICHE usa consultas estandarizadas", "operative_detail": "filtrar, seleccionar y ordenar", "target_effect": "pedir una consulta preexistente, no una investigación ad hoc", "source_id": "e0_argentina_resolution_53_2024_siche", "status": "PROVED"},
    {"rule_id": "SA138_05", "proposition": "SICHE exporta a planilla", "operative_detail": "grilla exportable", "target_effect": "pedir CSV/XLSX en el estado en que obre", "source_id": "e0_argentina_resolution_53_2024_siche", "status": "PROVED"},
    {"rule_id": "SA138_06", "proposition": "SICHE no transforma la fuente", "operative_detail": "toma repositorio tal como está", "target_effect": "preservar campos y valores originales", "source_id": "e0_argentina_resolution_53_2024_siche", "status": "PROVED"},
    {"rule_id": "SA138_07", "proposition": "La integridad del sistema de origen es una premisa", "operative_detail": "sin migración ni transformación", "target_effect": "una exportación negativa debe identificar sistema y filtros", "source_id": "e0_argentina_resolution_53_2024_siche", "status": "PROVED_RULE_TARGET_RESULT_OPEN"},
    {"rule_id": "SA138_08", "proposition": "La ruta pública es Ley 27.275", "operative_detail": "solicitud al Ministerio sobre registro existente", "target_effect": "pedir ejecución/exportación SICHE o derivación interna", "source_id": "e0_argentina_law_27275_updated_access;e0_argentina_economia_access_channel_2026", "status": "DRAFT_NOT_SENT"},
]
write_csv(HERE / "E0_SICHE_LEGACY_QUERY_AUTHORITY_V138.csv", siche_authority)

type_narrowing = [
    {"candidate": "UNCLASSIFIED", "rank": "0", "support": "Anexo K sólo imprime SIDIF", "contrary": "no da tipo", "decision_key": "consulta SICHE por N° SIDIF", "status": "EXACT_LOCATORS_TYPE_OPEN", "source_id": "e0_cgn_cuenta_inversion_2008_sdp"},
    {"candidate": "C55_DIRECT_DEBIT", "rank": "1", "support": "manual: débito bancario por comisión → C55 Débito Directo", "contrary": "falta exportación target", "decision_key": "tipo=C55; subtipo Débito Directo; cuenta; Libro Banco", "status": "PRIORITY_HYPOTHESIS_NOT_PROVED", "source_id": "e0_dgsiaf_slu_global_regularization_2004"},
    {"candidate": "C41_FOREIGN_PAYMENT", "rank": "2", "support": "SAF355 usaba C41 y cuenta del SAF para gastos/comisiones exteriores", "contrary": "concepto agregado puede ser regularización posterior", "decision_key": "tipo=C41; observación transferencia exterior; Nota/Boleto", "status": "ALTERNATIVE_HYPOTHESIS_NOT_PROVED", "source_id": "e0_cgn_circular_13_2002_foreign_payments;e0_cgn_tgn_disposition_47_10_2008_foreign_payments_annex"},
    {"candidate": "C42_NON_BUDGETARY", "rank": "3", "support": "tipo admitido por ingreso manual SIDIF", "contrary": "partida 7.2.8 es presupuestaria", "decision_key": "tipo=C42; AXT; razón extrapresupuestaria", "status": "LOWER_PRIORITY_NOT_EXCLUDED", "source_id": "e0_dgsiaf_slu_sidif_number_input_2003;e0_dgsiaf_slu_expense_reports_2003"},
    {"candidate": "C41_C42_C55_SET", "rank": "N/A", "support": "son los tipos permitidos por la función SLU de ingreso N° SIDIF", "contrary": "la función no prueba universo exhaustivo", "decision_key": "buscar los tres tipos primero y ampliar si no hay fila", "status": "PROVED_WORKFLOW_NARROWING", "source_id": "e0_dgsiaf_slu_sidif_number_input_2003"},
    {"candidate": "C55_NOTE_DIFFERENCE", "rank": "2B", "support": "C55 regulariza diferencias de débito de pagos por Nota", "contrary": "no conocemos una OP original ni diferencia cambiaria", "decision_key": "formulario original; medio Nota; diferencia; cuenta", "status": "SECONDARY_C55_VARIANT_OPEN", "source_id": "e0_cgn_circular_22_2004_note_regularization;e0_dgsiaf_slu_global_regularization_2004"},
    {"candidate": "DECISION", "rank": "N/A", "support": "el tipo, subtipo e historia del registro deciden", "contrary": "se prohíbe convertir ranking en hecho", "decision_key": "exportación SICHE + imagen/respaldos", "status": "OPEN", "source_id": "e0_argentina_resolution_53_2024_siche"},
]
write_csv(HERE / "E0_SLU_SIDIF_DOCUMENT_TYPE_NARROWING_V138.csv", type_narrowing)

c55_test = [
    {"test_id": "C55T138_01", "observable": "concepto", "target_or_expected": "COMISIONES - BANCO NACION", "c55_prediction": "coincide con ejemplo de comisión debitada", "discriminator": "tipo/subtipo", "target_status": "MATCH_NON_CONCLUSIVE", "source_id": "e0_cgn_cuenta_inversion_2008_sdp;e0_dgsiaf_slu_global_regularization_2004"},
    {"test_id": "C55T138_02", "observable": "tipo formulario", "target_or_expected": "C55", "c55_prediction": "C55-REG", "discriminator": "campo tipo", "target_status": "OPEN_CRITICAL", "source_id": "e0_dgsiaf_slu_sidif_number_input_2003"},
    {"test_id": "C55T138_03", "observable": "subtipo", "target_or_expected": "Débito Directo", "c55_prediction": "sin formulario original obligatorio", "discriminator": "campo subtipo", "target_status": "OPEN_CRITICAL", "source_id": "e0_dgsiaf_slu_global_regularization_2004"},
    {"test_id": "C55T138_04", "observable": "cuenta débito", "target_or_expected": "BNA; cuenta SAF 355/fondo rotatorio", "c55_prediction": "obligatoria", "discriminator": "banco/sucursal/cuenta", "target_status": "OPEN", "source_id": "e0_dgsiaf_slu_global_regularization_2004;e0_cgn_circular_13_2002_foreign_payments"},
    {"test_id": "C55T138_05", "observable": "beneficiario", "target_or_expected": "BNA o ente definido en registro", "c55_prediction": "obligatorio", "discriminator": "código/denominación/CUIT", "target_status": "OPEN", "source_id": "e0_dgsiaf_slu_global_regularization_2004"},
    {"test_id": "C55T138_06", "observable": "fuente y clase", "target_or_expected": "valores existentes", "c55_prediction": "obligatorios", "discriminator": "FF; clase de gasto", "target_status": "OPEN", "source_id": "e0_dgsiaf_slu_global_regularization_2004"},
    {"test_id": "C55T138_07", "observable": "imputación", "target_or_expected": "partida 7.2.8", "c55_prediction": "detalle presupuestario", "discriminator": "inciso/principal/parcial/subparcial", "target_status": "AGGREGATE_ONLY", "source_id": "e0_cgn_cuenta_inversion_2008_sdp;e0_dgsiaf_slu_global_regularization_2004"},
    {"test_id": "C55T138_08", "observable": "impactos", "target_or_expected": "compromiso/devengado/pagado o devengado/pagado", "c55_prediction": "al autorizar", "discriminator": "importes por etapa", "target_status": "OPEN", "source_id": "e0_dgsiaf_slu_global_regularization_2004"},
    {"test_id": "C55T138_09", "observable": "aceptación central", "target_or_expected": "aceptado/no rechazado", "c55_prediction": "impacto Libro Banco sólo tras aceptación", "discriminator": "historia envío/respuesta SC", "target_status": "OPEN_CRITICAL", "source_id": "e0_dgsiaf_slu_global_regularization_2004"},
    {"test_id": "C55T138_10", "observable": "Libro Banco", "target_or_expected": "débito y N° C55", "c55_prediction": "impacto +débito", "discriminator": "conc_02.rep", "target_status": "OPEN_CRITICAL", "source_id": "e0_dgsiaf_slu_global_regularization_2004;e0_dgsiaf_slu_bank_reconciliation_reports_2002"},
    {"test_id": "C55T138_11", "observable": "extracto", "target_or_expected": "movimiento BNA conciliado", "c55_prediction": "fecha/importe/estado", "discriminator": "conc_01.rep", "target_status": "OPEN_CRITICAL", "source_id": "e0_dgsiaf_slu_bank_reconciliation_reports_2002"},
    {"test_id": "C55T138_12", "observable": "suma", "target_or_expected": "tres filas = 32.270,30", "c55_prediction": "agregado exacto", "discriminator": "suma sin duplicar regularizaciones/desafectaciones", "target_status": "OPEN_CRITICAL", "source_id": "e0_cgn_cuenta_inversion_2008_sdp"},
]
write_csv(HERE / "E0_C55_DIRECT_DEBIT_HYPOTHESIS_TEST_V138.csv", c55_test)

foreign_chain = [
    {"step_id": "FP138_01", "period": "2002-11/2008", "actor": "SAF 355", "record_or_action": "C-41 pago exterior", "target_field": "N° SIDIF", "target_status": "OPEN", "source_id": "e0_cgn_circular_13_2002_foreign_payments"},
    {"step_id": "FP138_02", "period": "2002-11/2008", "actor": "SAF 355", "record_or_action": "beneficiario BNA o BCRA", "target_field": "beneficiario", "target_status": "OPEN", "source_id": "e0_cgn_circular_13_2002_foreign_payments"},
    {"step_id": "FP138_03", "period": "2002-11/2008", "actor": "SAF 355", "record_or_action": "Nota a TGN", "target_field": "beneficiario exterior; banco; cuenta; moneda; importe", "target_status": "OPEN", "source_id": "e0_cgn_circular_13_2002_foreign_payments"},
    {"step_id": "FP138_04", "period": "2002-11/2008", "actor": "BNA", "record_or_action": "débito de gastos/comisiones", "target_field": "cuenta fondo rotatorio SAF", "target_status": "MECHANISM_PROVED_TARGET_OPEN", "source_id": "e0_cgn_circular_13_2002_foreign_payments"},
    {"step_id": "FP138_05", "period": "desde 2008-11-20", "actor": "SAF 355", "record_or_action": "C-41 + Nota + Boleto", "target_field": "paquete respaldatorio", "target_status": "OPEN_DATE_DEPENDENT", "source_id": "e0_cgn_tgn_disposition_47_10_2008_foreign_payments"},
    {"step_id": "FP138_06", "period": "desde 2008-11-20", "actor": "BNA", "record_or_action": "visa Boleto de Venta", "target_field": "boleto visado", "target_status": "OPEN_DATE_DEPENDENT", "source_id": "e0_cgn_tgn_disposition_47_10_2008_foreign_payments_annex"},
    {"step_id": "FP138_07", "period": "desde 2008-11-20", "actor": "CGN", "record_or_action": "remite OP/Nota/Boleto", "target_field": "recepción y remisión", "target_status": "OPEN_DATE_DEPENDENT", "source_id": "e0_cgn_tgn_disposition_47_10_2008_foreign_payments_annex"},
    {"step_id": "FP138_08", "period": "desde 2008-11-20", "actor": "TGN", "record_or_action": "instrucción de pago a banco", "target_field": "fecha; lote; importe; anexos", "target_status": "OPEN_DATE_DEPENDENT", "source_id": "e0_cgn_tgn_disposition_47_10_2008_foreign_payments_annex"},
    {"step_id": "FP138_09", "period": "2008", "actor": "SAF 355", "record_or_action": "C-55 Débito Directo posterior", "target_field": "comisión; cuenta; Libro Banco", "target_status": "PRIORITY_HYPOTHESIS", "source_id": "e0_dgsiaf_slu_global_regularization_2004"},
    {"step_id": "FP138_10", "period": "2008", "actor": "SICHE", "record_or_action": "exportación cruzada SC/SLU", "target_field": "tipo; vínculos; historia; pago/regularización", "target_status": "DRAFT_NOT_SENT", "source_id": "e0_argentina_resolution_53_2024_siche"},
]
write_csv(HERE / "E0_FOREIGN_PAYMENT_COMMISSION_CHAIN_V138.csv", foreign_chain)

report_schema = [
    {"report_id": "RS138_01", "system": "SLU", "report_or_function": "Ingreso Nro. SIDIF", "filters": "tipo; ejercicio; estado; número local/SIDIF", "minimum_columns": "tipo C41/C42/C55; número; N° SIDIF; estado", "target_use": "resolver especie", "source_id": "e0_dgsiaf_slu_sidif_number_input_2003"},
    {"report_id": "RS138_02", "system": "SLU/SICHE", "report_or_function": "gastos_01.rep", "filters": "ejercicio 2008; SAF355; C41/C42/C55; 71597/152677/2876", "minimum_columns": "tipo/número; estado; documento; beneficiario; clase; objeto; pagado; regularizado", "target_use": "resolver tipo y etapas", "source_id": "e0_dgsiaf_slu_expense_reports_2003"},
    {"report_id": "RS138_03", "system": "SLU/SICHE", "report_or_function": "pagos_04.rep / F80", "filters": "OP asociada; ejercicio; pagador", "minimum_columns": "F80; OP; pagador; FF; beneficiario; pagado; regularizado", "target_use": "vincular pago", "source_id": "e0_dgsiaf_slu_payment_reports_2003"},
    {"report_id": "RS138_04", "system": "SLU/SICHE", "report_or_function": "PG_CPAR_EMITE_CONS_PAGO", "filters": "fecha; ejercicio/tipo/rango OP; banco/cuenta; estado; beneficiario", "minimum_columns": "fecha de pago; OP; banco; cuenta; beneficiario", "target_use": "certificar fecha/banco", "source_id": "e0_dgsiaf_slu_payment_query_2004"},
    {"report_id": "RS138_05", "system": "SLU/SICHE", "report_or_function": "Nota de Pago e historia", "filters": "OP; referencia; beneficiario", "minimum_columns": "estado; referencia; OP; documento; cuentas pagadora/receptora/de gastos; impresión/entrega/cumplimiento", "target_use": "probar medio Nota", "source_id": "e0_dgsiaf_slu_note_payment_2001"},
    {"report_id": "RS138_06", "system": "SLU/SICHE", "report_or_function": "C55 Regularización Global", "filters": "tipo; subtipo; cuenta; beneficiario; documento", "minimum_columns": "Débito Directo; FF; clase; imputación; importes; aceptación SC; historia", "target_use": "probar regularización", "source_id": "e0_dgsiaf_slu_global_regularization_2004"},
    {"report_id": "RS138_07", "system": "SLU/SICHE", "report_or_function": "conc_01.rep", "filters": "cuenta; fecha; tipo/estado", "minimum_columns": "fecha extracto/proceso; movimiento; debe/haber; saldo; conciliación", "target_use": "probar débito bancario", "source_id": "e0_dgsiaf_slu_bank_reconciliation_reports_2002"},
    {"report_id": "RS138_08", "system": "SLU/SICHE", "report_or_function": "conc_02.rep", "filters": "ejercicio; fecha autorización; número formulario", "minimum_columns": "estado; comprobante; tipo/número; beneficiario; debe/haber; saldo", "target_use": "probar Libro Banco", "source_id": "e0_dgsiaf_slu_bank_reconciliation_reports_2002"},
]
write_csv(HERE / "E0_SLU_LEGACY_REPORT_EXPORT_SCHEMA_V138.csv", report_schema)

query_plan = [
    {"query_id": "SQ138_01", "sequence": "1", "system": "SICHE · SIDIF Central", "filter_set": "ejercicio=2008; SAF=355; N°SIDIF=71597,152677,2876", "requested_output": "grilla/exportación sin transformación", "success_test": "tres filas o trazabilidad individual", "fallback": "constancia de sistemas/filtros/filas consultadas", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ138_02", "sequence": "2", "system": "SICHE · SLU", "filter_set": "SAF355; ejercicio 2008; tipos C41,C42,C55; N° SIDIF target", "requested_output": "tipo; número local; estado; historia", "success_test": "especie resuelta", "fallback": "buscar por importe/concepto/partida", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ138_03", "sequence": "3", "system": "SICHE · SLU gastos", "filter_set": "gastos_01.rep; 7.2.8; 32.270,30; BNA", "requested_output": "cabecera e ítems", "success_test": "suma y beneficiario", "fallback": "exportación anual filtrada", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ138_04", "sequence": "4", "system": "SICHE · SLU C55", "filter_set": "subtipo Débito Directo; BNA; 2008", "requested_output": "cuenta; FF; clase; imputación; historia SC", "success_test": "mecanismo exacto", "fallback": "todos C55 por comisión", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ138_05", "sequence": "5", "system": "SICHE · SLU pagos", "filter_set": "pagos_04.rep; OP target", "requested_output": "F80; pagador; beneficiario; pagado/regularizado", "success_test": "evento pago vinculado", "fallback": "todos F80 del día/importe", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ138_06", "sequence": "6", "system": "SICHE · SLU Nota", "filter_set": "OP target; BNA/BCRA", "requested_output": "nota; estados; cuentas; impresión/entrega/cumplimiento", "success_test": "medio Nota probado", "fallback": "historia/metadatos", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ138_07", "sequence": "7", "system": "SICHE · extracto", "filter_set": "conc_01.rep; cuenta BNA; fechas target", "requested_output": "movimiento; debe/haber; saldo; estado", "success_test": "débito conciliado", "fallback": "ventana ±5 días", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ138_08", "sequence": "8", "system": "SICHE · Libro Banco", "filter_set": "conc_02.rep; formulario target", "requested_output": "tipo/número; beneficiario; debe/haber; saldo", "success_test": "C55/OP impactó Libro Banco", "fallback": "buscar por importe/fecha", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ138_09", "sequence": "9", "system": "AMIDDF", "filter_set": "SAF355; 2008; Otros Gastos; tres SIDIF", "requested_output": "caja; tipo; imágenes; firmas", "success_test": "respaldo físico/digital", "fallback": "índice/tejuelo", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ138_10", "sequence": "10", "system": "RAIP Economía", "filter_set": "Resolución 53/2024 + Ley 27.275", "requested_output": "copias/exportaciones existentes", "success_test": "respuesta completa o derivación", "fallback": "denegación fundada y entrega parcial", "status": "DRAFT_NOT_SENT"},
]
write_csv(HERE / "E0_SICHE_TARGET_QUERY_PLAN_V138.csv", query_plan)

# Expansión del ledger metodológico.
ledger_path = HERE / "E0_FISCAL_MECHANISM_LEDGER_V138.csv"
ledger = [row for row in read_csv(ledger_path) if row["ledger_id"] not in {f"F{n}" for n in range(183, 196)}]
ledger_specs = [
    (183, "2003-2008", "SIDIF_IDENTIFIER_WORKFLOW", "DOCUMENT_CLASSIFICATION", "SAF", "SIDIF Central", "C41/C42/C55", "N° SIDIF", "e0_dgsiaf_slu_sidif_number_input_2003", "Tipos permitidos en función SLU", "TYPE_SET_NARROWED_TARGET_TYPE_OPEN", "Acota primero a C41/C42/C55; no confirma uno."),
    (184, "2004-2008", "BANK_COMMISSION_DIRECT_DEBIT", "ACCOUNTING_REGULARIZATION", "BNA", "SAF", "débito comisión", "C55 Débito Directo", "e0_dgsiaf_slu_global_regularization_2004", "Características y formas de ingreso", "MECHANISM_PROVED_TARGET_OPEN", "Coincidencia específica; aún sin fila target."),
    (185, "2001-2008", "NOTE_PAYMENT", "PAYMENT_MEDIUM", "SAF/TGN", "banco/beneficiario", "OP con medio Nota", "Nota de Pago", "e0_dgsiaf_slu_note_payment_2001", "Datos generales/cuentas/historia", "RECORD_SCHEMA_PROVED_TARGET_OPEN", "La nota no equivale a cumplimiento hasta confirmar."),
    (186, "2002-2008", "BANK_RECONCILIATION", "BANK_EXTRACT", "Banco", "SAF", "cuenta bancaria", "conc_01.rep", "e0_dgsiaf_slu_bank_reconciliation_reports_2002", "Movimientos del Extracto", "REPORT_SCHEMA_PROVED_TARGET_OPEN", "Extracto sin Libro Banco no cierra conciliación."),
    (187, "2002-2008", "BANK_RECONCILIATION", "BOOK_BANK", "SAF", "contabilidad", "formulario", "conc_02.rep", "e0_dgsiaf_slu_bank_reconciliation_reports_2002", "Movimientos del Libro Banco", "REPORT_SCHEMA_PROVED_TARGET_OPEN", "Libro Banco sin extracto no prueba débito bancario."),
    (188, "2003-2008", "EXPENSE_REPORT", "BUDGET_EXECUTION", "SAF", "CGN", "C35/C41/C42/C43/C55", "gastos_01.rep", "e0_dgsiaf_slu_expense_reports_2003", "Cabeceras e ítems", "REPORT_SCHEMA_PROVED_TARGET_OPEN", "Pagado es informativo; cruzar con F80/PG."),
    (189, "2003-2008", "PAYMENT_REPORT", "PAYMENT_EVENT", "SAF/TGN", "beneficiario", "F80/OP", "pagos_04.rep", "e0_dgsiaf_slu_payment_reports_2003", "Formularios por OP", "REPORT_SCHEMA_PROVED_TARGET_OPEN", "F80 requiere conciliación final."),
    (190, "2004-2008", "PAYMENT_QUERY", "PAYMENT_CERTIFICATE", "Tesorería", "beneficiario", "OP", "consulta pagos", "e0_dgsiaf_slu_payment_query_2004", "Filtros de consulta", "QUERY_SCHEMA_PROVED_TARGET_OPEN", "Capacidad no es resultado target."),
    (191, "2002-2008", "FOREIGN_PAYMENT", "C41_AND_COMMISSION_ACCOUNT", "SAF355", "BNA/BCRA", "beneficiario exterior", "C41+Nota", "e0_cgn_circular_13_2002_foreign_payments", "Puntos 1-9", "ROUTE_PROVED_TARGET_OPEN", "Regla aplicable antes de 20/11/2008."),
    (192, "2008-11/12", "FOREIGN_PAYMENT", "INSTRUCTION", "TGN", "BNA", "beneficiario exterior", "C41+Nota+Boleto", "e0_cgn_tgn_disposition_47_10_2008_foreign_payments_annex", "Puntos 1-5", "ROUTE_PROVED_TARGET_DATE_OPEN", "Sólo si la fecha target cae bajo la nueva norma."),
    (193, "2010", "SAF355_SYSTEM_DEPLOYMENT", "QUERY_CAPABILITY", "Secretaría de Hacienda", "SAF355", "todos los negocios", "e-SIDIF", "e0_cgn_account_2010_saf355_esidif_deployment", "Septiembre 2010", "DEPLOYMENT_PROVED_MIGRATION_SCOPE_OPEN", "No prueba integridad de cada registro 2008."),
    (194, "2024-2026", "LEGACY_SYSTEM_ACCESS", "QUERY_AUTHORITY", "Secretaría de Hacienda", "usuarios", "SC/SLU/BUDI", "SICHE", "e0_argentina_resolution_53_2024_siche", "Arts. 1-3", "CURRENT_UNIQUE_QUERY_ROUTE_PROVED", "Acceso público se gestiona vía RAIP; no enviado."),
    (195, "2013-2026", "ESIDIF_PAYMENT_QUERY", "QUERY_CROSSWALK", "Secretaría de Hacienda", "usuarios", "OP/PG", "consulta por N° SIDIF", "e0_dgsiaf_esidif_payment_queries_2013", "pp. 5-9", "CURRENT_SCHEMA_PROVED_TARGET_MIGRATION_OPEN", "Manual posterior usado sólo como crosswalk."),
]
for number, window, mechanism, phase, payer, recipient, universe, instrument, sid, locator, status, interpretation in ledger_specs:
    ledger.append({
        "ledger_id": f"F{number}", "window": window, "mechanism": mechanism, "phase": phase,
        "as_of_date": "N/D", "payer": payer, "recipient": recipient, "universe": universe,
        "instrument": instrument, "amount_original": "N/D", "original_unit": "N/D",
        "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": sid,
        "source_locator": locator, "realization_status": status, "additivity": "NON_ADDITIVE",
        "status_interpretation": interpretation, "caveat": "No convertir capacidad, ruta o hipótesis en ejecución target.",
    })
assert len(ledger) == 195
write_csv(ledger_path, ledger)

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V138.csv"
new_break_ids = {
    "sidif_identifier_not_document_type", "slu_allowed_types_not_exhaustive_universe", "mechanism_match_not_target_identity",
    "c55_authorized_not_sc_accepted", "book_bank_not_bank_extract", "bank_extract_not_book_bank",
    "paid_in_expense_report_informative", "f80_not_final_reconciliation", "foreign_payment_rule_date_split",
    "siche_route_not_row_existence", "siche_no_transform_not_completeness", "current_esidif_schema_not_2008_migration",
}
breaks = [row for row in read_csv(breaks_path) if row["break_id"] not in new_break_ids]
new_breaks = [
    ("sidif_identifier_not_document_type", "document", "El N° SIDIF no imprime por sí solo la especie.", "Resolver tipo en SICHE/SLU.", "e0_cgn_cuenta_inversion_2008_sdp"),
    ("slu_allowed_types_not_exhaustive_universe", "scope", "La función SLU admite C41/C42/C55 pero no define todo el universo SIDIF.", "Usar el conjunto como primera búsqueda, no como exclusión absoluta.", "e0_dgsiaf_slu_sidif_number_input_2003"),
    ("mechanism_match_not_target_identity", "inference", "Comisión debitada coincide con C55, sin identificar fila.", "Rotular C55 como hipótesis prioritaria.", "e0_dgsiaf_slu_global_regularization_2004"),
    ("c55_authorized_not_sc_accepted", "phase", "Autorización C55 precede respuesta SIDIF Central.", "Exigir historia y aceptación central.", "e0_dgsiaf_slu_global_regularization_2004"),
    ("book_bank_not_bank_extract", "reconciliation", "Libro Banco es registro interno.", "Cruzar con extracto.", "e0_dgsiaf_slu_bank_reconciliation_reports_2002"),
    ("bank_extract_not_book_bank", "reconciliation", "Extracto prueba banco, no imputación interna.", "Cruzar con Libro Banco/formulario.", "e0_dgsiaf_slu_bank_reconciliation_reports_2002"),
    ("paid_in_expense_report_informative", "phase", "gastos_01 muestra pagado a título informativo.", "Cruzar con F80/PG y conciliación.", "e0_dgsiaf_slu_expense_reports_2003"),
    ("f80_not_final_reconciliation", "phase", "F80 registra pago pero no necesariamente conciliación final.", "Exigir extracto y Libro Banco.", "e0_dgsiaf_slu_payment_reports_2003"),
    ("foreign_payment_rule_date_split", "time", "Disposición 47/08 rige desde 20/11; antes Circular 13/02.", "Clasificar cada target por fecha.", "e0_cgn_circular_13_2002_foreign_payments;e0_cgn_tgn_disposition_47_10_2008_foreign_payments"),
    ("siche_route_not_row_existence", "access", "La herramienta vigente no garantiza una fila concreta.", "Pedir exportación y metadatos de búsqueda negativa.", "e0_argentina_resolution_53_2024_siche"),
    ("siche_no_transform_not_completeness", "integrity", "Sin transformación preserva lo cargado, no prueba completitud.", "Separar integridad de cobertura.", "e0_argentina_resolution_53_2024_siche"),
    ("current_esidif_schema_not_2008_migration", "system", "Campos actuales no prueban migración histórica.", "Usar sólo crosswalk y consultar SICHE.", "e0_dgsiaf_esidif_payment_queries_2013"),
]
for break_id, dimension, problem, rule, evidence in new_breaks:
    breaks.append({"break_id": break_id, "dimension": dimension, "problem": problem, "rule": rule, "status": "FROZEN_V138", "evidence": evidence})
assert len(breaks) == 153
write_csv(breaks_path, breaks)

# Trazabilidad y claves para el pedido Economía/SICHE.
trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V138.csv"
trace = [row for row in read_csv(trace_path) if not row["trace_id"].startswith("TR138_")]
trace_specs = [
    (137, "SICHE_SC", "Exportación SIDIF Central por tres números", "2008", "SAF355;71597;152677;2876", "tipo;número;estado;fechas;importe;vínculos"),
    (138, "SICHE_SLU", "Exportación SLU por tres números SIDIF", "2008", "C41;C42;C55;71597;152677;2876", "tipo;número local;estado;historia SC"),
    (139, "SICHE_GASTOS", "gastos_01.rep cabecera e ítems", "2008", "7.2.8;83106000;32270.30", "documento;beneficiario;clase;objeto;pagado;regularizado"),
    (140, "SICHE_C55", "C55-REG Débito Directo", "2008", "BNA;comisiones;SAF355", "subtipo;cuenta;FF;clase;imputación;historia"),
    (141, "SICHE_F80", "pagos_04.rep / F80 vinculados", "2008", "OP target;pagador TGN/SAF", "F80;beneficiario;pagado;regularizado"),
    (142, "SICHE_NOTA", "Nota de Pago e historia", "2008", "BNA;BCRA;OP target", "referencia;cuentas;estado;impresión;cumplimiento"),
    (143, "SICHE_EXTRACT", "conc_01.rep movimientos extracto", "2008", "cuenta BNA;importe target", "fecha;movimiento;debe;haber;saldo;conciliación"),
    (144, "SICHE_BOOK", "conc_02.rep movimientos Libro Banco", "2008", "tipo/número target", "estado;formulario;beneficiario;debe;haber;saldo"),
    (145, "FOREIGN_PAYMENT", "Nota SAF a TGN y Boleto de Venta", "2008", "SAF355;BNA/BCRA", "OP SIDIF;beneficiario exterior;cuenta gastos;moneda;importe"),
    (146, "TGN_INSTRUCTION", "Instrucción TGN a entidad bancaria", "2008", "OP/Nota target", "fecha;importe;banco;anexo;acuse"),
    (147, "SICHE_NEGATIVE", "Metadatos de consulta negativa", "2026", "SC;SLU;filtros exactos", "sistema;dataset;filtros;fecha;filas;exclusiones"),
    (148, "AMIDDF", "Planilla/caja/imagen target", "2008", "SAF355;Otros Gastos;tres SIDIF", "caja;tipo;folio;firmas;imagen"),
]
for number, gap, record, period, identifiers, fields in trace_specs:
    trace.append({
        "trace_id": f"TR138_{number}", "request_id": "REQ133_ECON", "institution": "Ministerio de Economía / Secretaría de Hacienda",
        "gap_id": gap, "requested_record": record, "period_or_date": period, "identifiers": identifiers,
        "minimum_usable_fields": fields, "confidentiality_fallback": "exportación disociada; tachas parciales; metadatos de búsqueda", "status": "DRAFT_NOT_SENT",
    })
assert len(trace) == 148
write_csv(trace_path, trace)

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V138.csv"
keys = [row for row in read_csv(keys_path) if not row["key_id"].startswith("SK138_")]
key_specs = [
    (147, "system", "SICHE;SIDIF Central;SLU", "seleccionar repositorios heredados"),
    (148, "producer", "SAF 355;Dirección de Administración de la Deuda Pública", "entidad emisora/productora"),
    (149, "exercise", "2008", "ejercicio target"),
    (150, "sidif", "71597;152677;2876", "identificadores exactos"),
    (151, "sigade", "83106000", "cuenta/identificador asociado"),
    (152, "concept", "COMISIONES - BANCO NACION", "leyenda exacta"),
    (153, "amount", "32270.30;32.270,30", "importe agregado en ambas notaciones"),
    (154, "budget", "7.2.8", "partida exacta"),
    (155, "types", "C41;C42;C55", "primera búsqueda de tipo"),
    (156, "subtype", "Débito Directo;C55-REG", "hipótesis prioritaria"),
    (157, "report", "gastos_01.rep;pagos_04.rep", "tipo/etapas/F80"),
    (158, "report", "conc_01.rep;conc_02.rep", "extracto/Libro Banco"),
    (159, "medium", "Nota de Pago;transferencia al exterior", "rama C41/Nota"),
    (160, "archive", "Rendiciones de Cuentas;Otros Gastos", "rama AMIDDF"),
]
for number, group, key, purpose in key_specs:
    keys.append({
        "key_id": f"SK138_{number}", "request_id": "REQ133_ECON", "key_group": group,
        "exact_key": key, "search_purpose": purpose, "source_or_basis": "E0_SICHE_TARGET_QUERY_PLAN_V138.csv",
        "caveat": "Clave de búsqueda; no confirma resultado.",
    })
assert len(keys) == 160
write_csv(keys_path, keys)

c41_path = HERE / "E0_C41_PAYMENT_EXECUTION_CHAIN_V138.csv"
c41 = [row for row in read_csv(c41_path) if not row["stage_id"].startswith("CP138_")]
c41_specs = [
    (26, "SICHE_AUTHORITY", "Resolución SH 53/2024", "SC;SLU;filtros;exportación", "Ruta actual única", "e0_argentina_resolution_53_2024_siche", "ROUTE_PROVED", "SICHE debe consultarse.", "SICHE contiene necesariamente cada target."),
    (27, "TYPE_NARROWING", "Ingreso N° SIDIF SLU", "C41;C42;C55", "Conjunto inicial de tipos", "e0_dgsiaf_slu_sidif_number_input_2003", "THREE_CANDIDATES", "Buscar primero esos tipos.", "Uno está confirmado."),
    (28, "C55_DIRECT_DEBIT_CANDIDATE", "C55-REG", "Débito Directo;comisión;cuenta", "Hipótesis prioritaria", "e0_dgsiaf_slu_global_regularization_2004", "OPEN_PRIORITY", "Coincidencia específica de mecanismo.", "Los tres SIDIF son C55."),
    (29, "C41_FOREIGN_PAYMENT_CANDIDATE", "C41+Nota", "BNA/BCRA;cuenta de gastos", "Hipótesis alternativa", "e0_cgn_circular_13_2002_foreign_payments", "OPEN_ALTERNATIVE", "La comisión puede nacer de pago exterior.", "La línea target es la OP principal."),
    (30, "C42_CANDIDATE", "C42", "AXT;no presupuestario", "Hipótesis de menor prioridad", "e0_dgsiaf_slu_sidif_number_input_2003", "OPEN_LOW_PRIORITY", "No excluido hasta ver tipo.", "La partida presupuestaria prueba C42."),
    (31, "EXPENSE_EXPORT", "gastos_01.rep", "tipo;documento;beneficiario;pagado;regularizado", "Resuelve cabecera e ítems", "e0_dgsiaf_slu_expense_reports_2003", "TARGET_EXPORT_OPEN", "Salida preexistente solicitada.", "Pagado informativo cierra ejecución."),
    (32, "PAYMENT_EXPORT", "pagos_04.rep/F80", "OP;pagador;beneficiario;pagado", "Vincula pago", "e0_dgsiaf_slu_payment_reports_2003", "TARGET_EXPORT_OPEN", "Salida preexistente solicitada.", "F80 cierra conciliación bancaria."),
    (33, "BANK_RECONCILIATION_EXPORT", "conc_01.rep+conc_02.rep", "extracto;Libro Banco;estado;saldo", "Cruce bancario-contable", "e0_dgsiaf_slu_bank_reconciliation_reports_2002", "TARGET_EXPORT_OPEN", "Ambas caras son necesarias.", "Una cara sustituye la otra."),
    (34, "TARGET_TYPE_AND_PAYMENT_CLOSE", "exportación SICHE + respaldo", "tipo;subtipo;importe;historia;conciliación", "Cierre discriminante", "e0_argentina_resolution_53_2024_siche", "OPEN", "Sólo el registro decide rama y ejecución.", "El ranking cualitativo es prueba."),
]
for number, stage, record, fields, meaning, sid, status, permitted, forbidden in c41_specs:
    c41.append({
        "stage_id": f"CP138_{number}", "stage": stage, "record": record, "required_or_visible_fields": fields,
        "execution_meaning": meaning, "source_id": sid, "target_status": status,
        "permitted_inference": permitted, "forbidden_inference": forbidden,
    })
assert len(c41) == 34
write_csv(c41_path, c41)

# El canal SICHE se agrega como destino interno del pedido legal, nunca como envío autónomo.
channels_path = HERE / "CURRENT_OFFICIAL_SUBMISSION_CHANNELS_V138.csv"
channels = [row for row in read_csv(channels_path) if row["channel_id"] != "CH138_SICHE"]
channels.append({
    "channel_id": "CH138_SICHE", "institution": "Ministerio de Economía / Secretaría de Hacienda / DGSIAF",
    "request_type": "Exportación de sistemas heredados vía RAIP", "official_url": "https://www.argentina.gob.ar/economia/sechacienda/dgsiaf/siche",
    "online_route": "solicitar al RAIP la ejecución o derivación interna de consulta SICHE", "email_or_contact": "ciudadano@mecon.gov.ar",
    "physical_route": "Balcarce 186 piso 1 oficina 148 CABA", "published_deadline": "15 días hábiles; eventual prórroga de 15",
    "page_freshness": "SICHE y Resolución 53/2024 verificadas", "verified_on": "2026-08-30",
    "status": "OFFICIAL_INTERNAL_QUERY_ROUTE_DRAFT_NOT_SENT", "caveat": "No se accedió a credenciales ni se presentó solicitud.",
})
write_csv(channels_path, channels)

# Refinamiento idempotente del pedido a Economía y del checklist.
request_path = HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V138.md"
request_text = request_path.read_text(encoding="utf-8-sig")
# V137 heredaba dos secciones con el mismo título. La primera presuponía
# indebidamente C-41; se conserva la segunda, que ya formula la bifurcación
# como hipótesis condicionada a la clasificación del registro.
legacy_duplicate_marker = "## Clave V138 · salida FindDoc y cadena C-41"
legacy_first = request_text.find(legacy_duplicate_marker)
legacy_second = request_text.find(legacy_duplicate_marker, legacy_first + len(legacy_duplicate_marker))
if legacy_first >= 0 and legacy_second >= 0:
    request_text = request_text[:legacy_first] + request_text[legacy_second:]
request_marker = "## Clave V138 · exportación SICHE y prueba C-55 por débito directo"
if request_marker not in request_text:
    request_text += f"""

{request_marker}

Sin alterar el pedido AMIDDF, se solicita como primer producto electrónico que el organismo ejecute o derive internamente una consulta en **SICHE**, aplicación declarada por la Resolución SH 53/2024 como única herramienta para consultar SIDIF Central y SLU discontinuados. No se pide crear un análisis: se requieren las grillas o exportaciones existentes, tal como obren y sin transformación.

Filtros iniciales comunes: `SAF 355`, ejercicio `2008`, números SIDIF `71597`, `152677` y `2876`, identificador SIGADE `83106000`, concepto `COMISIONES - BANCO NACION`, partida `7.2.8` e importe agregado `$32.270,30`. En SLU, buscar primero tipos `C-41`, `C-42` y `C-55`, sin asumir de antemano cuál corresponde.

1. Exportar de SIDIF Central y SLU la identificación, tipo, número interno, N° SIDIF, estado, fechas de ingreso/autorización/aceptación, formulario original y generador, documento respaldatorio, beneficiario/CUIT, fuente, clase, objeto, pagador, cuentas, medio e importes comprometido, devengado, pagado y regularizado.
2. Ejecutar, si obran en SICHE con esos nombres o equivalentes, `gastos_01.rep`, `pagos_04.rep`, `conc_01.rep` y `conc_02.rep`, incluyendo cabeceras e ítems.
3. Si algún registro fuera `C-55`, informar subtipo —en especial Débito Directo—, cuenta de débito, detalle de imputación, historia de envío/respuesta del SIDIF Central e impacto en Libro Banco.
4. Si algún registro se vinculara a `C-41` con medio Nota o pago exterior, entregar Nota de Pago, historia, cuenta destinada a gastos/comisiones, Boleto de Venta de Cambio, instrucción TGN y acuse/rendición bancaria existentes.
5. Si no hubiese filas, identificar para cada búsqueda el sistema, conjunto consultado, filtros aplicados, fecha, cantidad de resultados, cobertura temporal y cualquier exclusión; si la información obra en otra dependencia, remitir el pedido conforme al artículo 10 de la Ley 27.275.

Se admite entrega parcial con tachas de datos personales o bancarios no necesarios, preservando identificadores, fechas, importes, estados, vínculos y trazabilidad. **Estado: BORRADOR_NO_ENVIADO.**
"""
    request_path.write_text(request_text, encoding="utf-8")

checklist_path = HERE / "REQUEST_SUBMISSION_CHECKLIST_V138.md"
checklist_text = checklist_path.read_text(encoding="utf-8-sig")
checklist_marker = "## Control V138 · SICHE"
if checklist_marker not in checklist_text:
    checklist_text += f"""

{checklist_marker}

- [ ] Mantener los tres números rotulados como SIDIF hasta recibir el tipo.
- [ ] Solicitar búsquedas separadas en SIDIF Central y SLU dentro de SICHE.
- [ ] Pedir exportaciones existentes de `gastos_01.rep`, `pagos_04.rep`, `conc_01.rep` y `conc_02.rep` o equivalentes.
- [ ] Tratar C-55 Débito Directo como hipótesis prioritaria, nunca como hecho previo a la respuesta.
- [ ] Exigir metadatos de una búsqueda sin resultados.
- [ ] Confirmar autorización expresa antes de cualquier envío.
"""
    checklist_path.write_text(checklist_text, encoding="utf-8")

register_path = HERE / "E0_REQUEST_RESPONSE_REGISTER_V138.csv"
register = read_csv(register_path)
for row in register:
    row["status"] = "DRAFT_NOT_SENT"
write_csv(register_path, register)

source_refs_path = HERE / "SOURCE_REFERENCES_V138.md"
source_refs = source_refs_path.read_text(encoding="utf-8-sig")
refs_marker = "## Fuentes nuevas V138 · SICHE, SLU y C-55"
if refs_marker not in source_refs:
    source_refs += "\n\n" + refs_marker + "\n\n"
    for item in SOURCES:
        source_refs += f"- `{item['id']}` · {item['title']} · {item['url']} · `{item['local']}` · `{item['sha256']}`\n"
    source_refs_path.write_text(source_refs, encoding="utf-8")

# Documentos de síntesis.
(HERE / "README_V138.md").write_text("""# V138 · SICHE y prueba discriminante C-55

V138 convierte la incertidumbre documental de los SIDIF 71597, 152677 y 2876 en una consulta oficial reproducible. La Resolución SH 53/2024 establece que SICHE es la única herramienta para consultar SIDIF Central y SLU discontinuados, con filtros y exportación sin transformación. Los manuales contemporáneos reducen la primera búsqueda a C-41/C-42/C-55 y hacen de C-55 Débito Directo la hipótesis prioritaria porque el sistema usa ese mecanismo cuando aparece un débito bancario por comisión. La hipótesis no se presenta como hecho: deben decidirla las exportaciones de gastos, pagos, extracto y Libro Banco. Resultado estricto sin cambio: 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas; seis pedidos DRAFT_NOT_SENT.
""", encoding="utf-8")

(HERE / "VEREDICTO_V138.md").write_text("""# Veredicto V138

Existe una ruta documental vigente y específica: SICHE debe concentrar las consultas del SIDIF Central y SLU discontinuados. El pedido ya puede identificar sistemas, filtros, reportes y columnas preexistentes; una respuesta negativa verificable también debe declarar qué se consultó.

C-55 por Débito Directo es la explicación mejor respaldada para `COMISIONES - BANCO NACION`: el manual SLU usa expresamente el débito de una comisión como supuesto de regularización, exige cuenta/beneficiario/imputación y produce impacto en Libro Banco luego de la aceptación central. La normativa de pagos al exterior de SAF 355 refuerza la plausibilidad al exigir una cuenta del SAF para gastos y comisiones. Pero ninguna fuente pública asigna aún los tres SIDIF a C-55; C-41 y C-42 siguen abiertos hasta la exportación.

No apareció ningún registro target de SICHE, C-55, F80/PG, Nota, extracto, Libro Banco ni conciliación. El balance sigue en 10 adjudicaciones exactas, 9 cuentas candidatas y 0/10 ejecuciones confirmadas. Los seis pedidos continúan sin enviar.
""", encoding="utf-8")

(HERE / "E0_FISCAL_RECONSTRUCTION_V138.md").write_text("""# Reconstrucción fiscal E0 V138

V138 prueba la infraestructura de consulta histórica y formaliza el test que separa tres especies posibles. La rama C-55 requiere tipo/subtipo, cuenta, imputación, aceptación central, Libro Banco y extracto; la rama C-41 requiere OP, Nota, cuenta de gastos/comisiones, instrucción y rendición; C-42 exige una justificación extrapresupuestaria. Ninguna rama se suma al panel cuantitativo sin una fila target y su conciliación. Por eso el numerador permanece en 0/10 ejecuciones confirmadas.
""", encoding="utf-8")

(HERE / "AUDITORIA_V138.md").write_text(f"""# Auditoría V138

- Fuentes maestras: 422; diecinueve fuentes oficiales nuevas preservadas.
- Fuentes primarias E0: 182; copias físicas SHA-válidas esperadas: 416.
- Autoridad SICHE: 8 controles; tipos SIDIF: 7 filas.
- Test C-55: 12 observables; cadena exterior: 10 etapas.
- Esquema de reportes: 8 salidas; plan de consulta: 10 pasos.
- Ledger fiscal: 195 filas; cortes metodológicos: 153.
- Trazabilidad: 148 objetos; claves: 160; cadena de ejecución: 34.
- Escalera: 10 adjudicaciones; 9 cuentas candidatas; 0 ejecuciones confirmadas.
- Pedidos: 6 borradores, 0 enviados; panel estricto {STRICT}% sin cambios.
""", encoding="utf-8")

(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V138_A_V139.md").write_text("""# Handover V138 → V139

## Estado

- QA V138: ejecutar y exigir PASS.
- SICHE: única herramienta vigente para SC y SLU discontinuados desde 2024-07-01; exporta sin transformación.
- Tres SIDIF exactos: 71597, 152677 y 2876; tipo todavía abierto.
- Primera búsqueda de tipo: C-41/C-42/C-55.
- Ranking cualitativo: C-55 Débito Directo primero; C-41/Nota exterior segundo; C-42 tercero. Ninguno confirmado.
- Reportes target: gastos_01, pagos_04/F80, conc_01 y conc_02; además Nota e historia C55/SC.
- Seis pedidos DRAFT_NOT_SENT; ninguno enviado.
- Escalera: 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas.

## Prioridad V139

1. Mantener los seis pedidos como borradores salvo autorización expresa.
2. Si se autoriza, presentar primero Economía/RAIP pidiendo exportación SICHE SC+SLU y Planilla AMIDDF.
3. Obtener tipo/subtipo antes de afirmar C-55 o C-41.
4. Si C-55: cerrar cuenta, aceptación SC, Libro Banco y extracto.
5. Si C-41: cerrar Nota, cuenta de comisiones, instrucción TGN y rendición.
6. Exigir metadatos de cualquier consulta negativa.
7. Mantener separados registro presupuestario, pago, débito, conciliación y cancelación CRYL.
""", encoding="utf-8")

# Auditoría global y estado acumulado.
for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    shutil.copyfile(AUDIT / f"{stem}_V137.csv", AUDIT / f"{stem}_V138.csv")

hash_rows = []
for row in catalog:
    local = row["archivo_local"]
    path = REPO / local.lstrip("/") if local else None
    exists = bool(path and path.is_file())
    actual = sha256(path) if exists else ""
    expected = row["sha256"]
    hash_rows.append({"id": row["id"], "archivo_local": local, "exists": str(exists), "sha_catalog": expected, "sha_actual": actual, "hash_ok": str(bool(exists and expected and actual.lower() == expected.lower()))})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V138.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V138.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
assert physical == hash_ok == 416

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or "tmp" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": str(size), "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V138.csv", size_rows)

completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V137.json").read_text(encoding="utf-8"))
for key in list(completeness):
    if key.endswith("_v137") or "newly_preserved_v137" in key:
        completeness.pop(key, None)
completeness.update({
    "checkpoint": "V138", "date": "2026-08-30",
    "state": "E0_SICHE_UNIQUE_ROUTE_PROVED_C55_PRIORITY_HYPOTHESIS_DESIGNATED_TARGET_EXPORT_OPEN_NOT_SENT",
    "numeric_v138_strict_changed": False, "master_catalog_entries": len(catalog),
    "physical_local_copies": physical, "physical_local_hash_ok": hash_ok,
    "e0_primary_sources_preserved": len(census), "e0_quality": "PRIMARY_SICHE_SLU_C55_PAYMENT_AND_RECONCILIATION_CONTROLS",
    "sources_newly_preserved_v138": 19, "e0_primary_sources_newly_preserved_v138": 19,
    "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
    "e0_request_traceability_rows": len(trace), "e0_request_search_keys": len(keys),
    "e0_c41_chain_rows": len(c41), "e0_sidif_target_ids": 3, "e0_sidif_target_document_types_located": 0,
    "e0_sidif_candidate_types": 3, "e0_c55_direct_debit_priority_hypothesis": True,
    "e0_c55_target_rows_located": 0, "e0_siche_unique_legacy_query_route_proved": True,
    "e0_siche_target_exports_located": 0, "e0_siche_query_plan_rows": len(query_plan),
    "e0_slu_report_schema_rows": len(report_schema), "e0_automatic_debit_target_rows_located": 0,
    "e0_bcra_note_target_rows_located": 0, "e0_settlement_award_rows_exact": 10,
    "e0_settlement_account_candidate_rows": 9, "e0_settlement_executed_rows_confirmed": 0,
    "e0_requests_submitted": 0, "e0_request_responses_received": 0,
    "e0_request_package_status": "DRAFT_NOT_SENT",
    "historical_workstream": "SICHE unique SC/SLU route proved; C55 direct debit is priority hypothesis; C41 foreign-payment and C42 alternatives remain open; target exports, AMIDDF box/body, reconciliation, CRYL and executed settlement remain open; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V138.json").write_text(json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
backup_text = backup.read_text(encoding="utf-8-sig")
backup_marker = "## V138 · SICHE y test C-55"
if backup_marker not in backup_text:
    backup_text += f"""

{backup_marker}

- SICHE es la ruta única vigente para SIDIF Central/SLU discontinuados y permite exportación sin transformación.
- Primera búsqueda de tipo: C-41/C-42/C-55; C-55 Débito Directo es hipótesis prioritaria, no hecho.
- Pedido Economía refinado a gastos_01, pagos_04, conc_01 y conc_02, con metadatos de búsqueda negativa.
- 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas; seis borradores no enviados.
"""
    backup.write_text(backup_text, encoding="utf-8")

inherited = [
    {"script": "qa_v137.py", "pre_v138_result": "PASS", "post_v138_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V137 queda supersedida por fuentes, conteos y ruta SICHE V138."},
    {"script": "qa_v138.py", "pre_v138_result": "N/A", "post_v138_result": "PASS", "interpretation": "SICHE, tipos candidatos, test C55, hashes y no envío verificados."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V138.csv", inherited)

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

authority = rows("E0_SICHE_LEGACY_QUERY_AUTHORITY_V138.csv")
types = rows("E0_SLU_SIDIF_DOCUMENT_TYPE_NARROWING_V138.csv")
c55 = rows("E0_C55_DIRECT_DEBIT_HYPOTHESIS_TEST_V138.csv")
foreign = rows("E0_FOREIGN_PAYMENT_COMMISSION_CHAIN_V138.csv")
schema = rows("E0_SLU_LEGACY_REPORT_EXPORT_SCHEMA_V138.csv")
plan = rows("E0_SICHE_TARGET_QUERY_PLAN_V138.csv")
assert len(authority) == 8 and authority[0]["status"] == "PROVED"
assert len(types) == 7 and types[1]["candidate"] == "C55_DIRECT_DEBIT"
assert types[1]["status"] == "PRIORITY_HYPOTHESIS_NOT_PROVED"
assert len(c55) == 12 and len(foreign) == 10 and len(schema) == 8 and len(plan) == 10
assert all(r["status"] == "DRAFT_NOT_SENT" for r in plan)
assert {r["report_or_function"] for r in schema} >= {"gastos_01.rep", "pagos_04.rep / F80", "conc_01.rep", "conc_02.rep"}

assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V138.csv")) == 195
assert len(rows("E0_FISCAL_METHOD_BREAKS_V138.csv")) == 153
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V138.csv")) == 148
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V138.csv")) == 160
c41 = rows("E0_C41_PAYMENT_EXECUTION_CHAIN_V138.csv")
assert len(c41) == 34 and c41[-1]["stage"] == "TARGET_TYPE_AND_PAYMENT_CLOSE"

ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V138.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V138.csv")}
new_ids = ''' + repr(source_ids) + r'''
assert len(census) == 182 and new_ids <= set(census)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 422 and len({r["id"] for r in catalog}) == 422

expected = ''' + repr(EXPECTED) + r'''
bin_dir = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v138" / "binaries"
assert len(list(bin_dir.iterdir())) == 19
for name, (size, digest) in expected.items():
    path = bin_dir / name
    assert path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest() == digest

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V138.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V138"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 416
assert complete["e0_siche_unique_legacy_query_route_proved"] is True
assert complete["e0_c55_direct_debit_priority_hypothesis"] is True
assert complete["e0_sidif_target_document_types_located"] == 0
assert complete["e0_c55_target_rows_located"] == 0
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v138_strict_changed"] is False

request = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V138.md").read_text(encoding="utf-8-sig")
assert "## Clave V138 · exportación SICHE y prueba C-55 por débito directo" in request
assert "BORRADOR_NO_ENVIADO" in request and "gastos_01.rep" in request and "conc_02.rep" in request
assert request.count("## Clave V138 · salida FindDoc y cadena C-41") == 1
assert "se solicitan los C-41 completos" not in request
register = rows("E0_REQUEST_RESPONSE_REGISTER_V138.csv")
assert len(register) == 6 and all(r.get("status") == "DRAFT_NOT_SENT" for r in register)
for name in ("README_V138.md", "VEREDICTO_V138.md", "E0_FISCAL_RECONSTRUCTION_V138.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V138_A_V139.md"):
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")

print("V138 QA PASS")
'''
(HERE / "qa_v138.py").write_text(qa, encoding="utf-8")


def checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V138.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V138", "parent_checkpoint": "V137",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": 19, "new_primary_sources": 19,
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks),
        "siche_authority_rows": len(siche_authority), "siche_target_exports_located": 0,
        "sidif_candidate_types": 3, "sidif_target_document_types_located": 0,
        "c55_priority_hypothesis_designated": True, "c55_target_rows_located": 0,
        "c41_chain_rows": len(c41), "automatic_debit_target_rows_located": 0, "bcra_note_target_rows_located": 0,
        "award_rows_exact": 10, "account_candidate_rows": 9, "executed_settlement_rows_confirmed": 0,
        "request_drafts": 6, "request_traceability_rows": len(trace), "request_search_keys": len(keys),
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V138.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    "checkpoint": "V138", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical copies SHA-valid; SICHE unique route proved; C55 direct debit designated priority hypothesis only; target type/export/reconciliation open; zero of ten executed settlement rows confirmed; six requests drafted and none submitted.",
    "historical_workstream": "Obtain SICHE SC+SLU export and AMIDDF index; decide C55/C41/C42; close Libro Banco/extracto or Nota/TGN instruction; CRYL and executed settlement remain open; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V138 BUILD PASS")
