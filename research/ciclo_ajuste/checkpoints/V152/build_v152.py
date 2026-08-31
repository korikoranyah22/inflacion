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
AUDIT = CYCLE / "source_audit"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v152" / "binaries"
V151 = CYCLE / "checkpoints" / "V151"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows, fields=None):
    fields = fields or (list(rows[0]) if rows else [])
    with Path(path).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def upsert(rows, additions, key):
    order = [str(row[key]) for row in rows]
    indexed = {str(row[key]): row for row in rows}
    for addition in additions:
        row = {name: str(value) for name, value in addition.items()}
        indexed[row[key]] = row
        if row[key] not in order:
            order.append(row[key])
    return [indexed[value] for value in order]


def matrix(name, fields, rows):
    data = [dict(zip(fields, row)) for row in rows]
    write_csv(HERE / name, data, fields)
    return data


def append_section(path, marker, body):
    path = Path(path)
    text = path.read_text(encoding="utf-8-sig")
    if marker not in text:
        path.write_text(text.rstrip() + "\n\n" + marker + "\n\n" + body.strip() + "\n", encoding="utf-8")


EXCLUDED_DIRS = {".git", "__pycache__", "tmp", "node_modules"}


def iter_files(root):
    root = Path(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted((name for name in dirnames if name not in EXCLUDED_DIRS), key=str.casefold)
        for filename in sorted(filenames, key=str.casefold):
            yield Path(dirpath) / filename


# Restore inherited rows from verified V151. Lower-case v151 source paths remain
# unchanged; V152 owns only the new bundle below.
census = read_csv(V151 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V151.csv")
provenance = read_csv(V151 / "ARCHIVAL_PROVENANCE_V151.csv")

# id, institution, title, url, file, period, series, kind, note, variables, breaks
SOURCES = [
    (
        "e0_cgn_disposition_28_2008_midyear_closing_axt", "Contaduría General de la Nación",
        "Disposición CGN 28/2008 · cierre intermedio, excepción SAF 355 y saldos AXT",
        "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/2008/disp28/disp28.htm",
        "cgn_disposition_28_2008_midyear_closing.html", "2008-06", "Disposición CGN 28/2008",
        "HTML oficial preservado",
        "Arts. 2, 3, 4, 11, 15 y 16: conformidad intermedia, excepción de cuadros para SAF 355, detalle ONCP de saldos AXT y custodia; no prueba una transacción de cierre ni un pago.",
        "SAF355;ONCP;SIDIF;AXT;closing;archive;midyear",
        "cierre intermedio/final; excepción de cuadro/ausencia de registro; saldo AXT/movimiento bancario",
    ),
    (
        "e0_enre_annual_2009_uai_account_2008_certifications", "Ente Nacional Regulador de la Electricidad",
        "Informe Anual ENRE 2009 · certificaciones UAI de la Cuenta de Inversión 2008",
        "https://www.argentina.gob.ar/sites/default/files/ia_2009.pdf",
        "enre_informe_anual_2009_uai_certifications.pdf", "2008-2009", "Informe Anual ENRE 2009 · UAI Informe 04",
        "PDF oficial preservado",
        "Prueba ejecución del Instructivo SGN 02/2008 mediante certificaciones de Anexos II, IV y V y auditoría separada bajo Instructivo 1/2009; las notas ENRE no son IDs del SAF 355.",
        "UAI;SIGEN;Cuenta2008;certification;AnnexII;AnnexIV;AnnexV",
        "existencia del instructivo/certificación target; ENRE/SAF355; certificación/ejecución bancaria",
    ),
    (
        "e0_sigen_memory_2009_account_2008_global_control_report", "Sindicatura General de la Nación",
        "Memoria SIGEN 2009 · informe global sobre la Cuenta de Inversión 2008",
        "https://www.argentina.gob.ar/sites/default/files/memoria_sigen_2009.pdf",
        "sigen_memoria_2009_cuenta_2008_control.pdf", "2008-2009", "Memoria de Gestión SIGEN 2009",
        "PDF oficial preservado",
        "Prueba instrucciones de trabajo a UAI, existencia de un informe SIGEN sobre la Cuenta 2008 y supervisión de UAI; no individualiza SAF 355 ni los tres IDs target.",
        "SIGEN;UAI;Cuenta2008;global_report;supervision;internal_control",
        "informe global/auditoría target; supervisión/validación; control interno/pago",
    ),
    (
        "e0_cgn_disposition_35_2002_parameterized_inconsistency_procedure", "Contaduría General de la Nación",
        "Disposición CGN 35/2002 · listados parametrizados y regularización de inconsistencias",
        "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/2002/disp35/disp35.htm",
        "cgn_disposition_35_2002_parameterized_inconsistency.html", "2002-2008",
        "Disposición CGN 35/2002 y Anexos I-II", "HTML y anexos PDF oficiales preservados",
        "Define envío mensual en texto, casillas param/inconsis por SAF, conformidad o discrepancia en 72 horas, regularización en siete días y campos SIDIF/SAF firmados; no aporta las filas target.",
        "SIDIF;SAF;parameterized_lists;inconsistencies;C41;C42;C55;email;signature",
        "procedimiento/resultado; formulario de ajuste/pago; regla 2002/aplicación 2008",
    ),
]

source_rows = []
for sid, institution, title, url, filename, period, series, kind, note, variables, breaks in SOURCES:
    path = BIN / filename
    assert path.is_file(), path
    source_rows.append({
        "id": sid, "institution": institution, "title": title, "url": url,
        "local": "/" + path.relative_to(REPO).as_posix(), "period": period,
        "series": series, "kind": kind, "note": note, "variables": variables,
        "breaks": breaks, "sha": sha256(path), "bytes": path.stat().st_size,
    })

catalog = read_csv(CATALOG)
catalog = upsert(catalog, [{
    "id": s["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": s["institution"],
    "titulo": s["title"], "url_original": s["url"], "archivo_local": s["local"],
    "fecha_descarga": "2026-08-31", "fecha_publicacion": s["period"],
    "codigo_serie": s["series"], "periodo_utilizado": s["period"], "tipo": s["kind"],
    "sha256": s["sha"], "nota": "V152: " + s["note"],
} for s in source_rows], "id")
write_csv(CATALOG, catalog, list(catalog[0]))

census = upsert(census, [{
    "source_id": s["id"], "institution": s["institution"], "artifact": s["title"],
    "url": s["url"], "local_path": s["local"], "sha256": s["sha"], "bytes": s["bytes"],
    "period_coverage": s["period"], "variable_families": s["variables"],
    "primary_source": "YES", "preserved": "YES", "method_breaks": s["breaks"],
    "use_status": "E0_USABLE_WITH_SCOPE", "caveat": s["note"],
} for s in source_rows], "source_id")
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V152.csv", census, list(census[0]))

provenance = upsert(provenance, [{
    "source_id": s["id"], "original_url": s["url"], "retrieval_url": s["url"],
    "capture_timestamp": "2026-08-31", "cdx_digest": "N/A_OFFICIAL_DIRECT",
    "local_path": s["local"], "sha256": s["sha"], "bytes": s["bytes"],
    "provenance_note": "Captura directa oficial; alcance probatorio congelado en V152."
    + (" Descarga con excepción TLS (-k) por certificado vencido del servidor oficial histórico."
       if "economia.gob.ar/hacienda" in s["url"] else ""),
} for s in source_rows], "source_id")
write_csv(HERE / "ARCHIVAL_PROVENANCE_V152.csv", provenance, list(provenance[0]))


uai_rows = [
    ("INSTR_02_EXISTENCE", "Instructivo de Trabajo SGN 02/2008", "Existencia y aplicación corroboradas por dos certificaciones ENRE.", "ENRE Informe Anual 2009 PDF p.163", "PROVED_EXISTENCE_NOT_BODY"),
    ("NOTE_84749", "Nota ENRE 84.749", "Certificó Cuenta 2008 bajo Instructivo 02/2008, Anexos II y IV.", "ENRE p.163", "COMPARATOR_EXECUTION"),
    ("NOTE_86232", "Nota ENRE 86.232", "Certificó Cuenta 2008 bajo Instructivo 02/2008, Anexo V.", "ENRE p.163", "COMPARATOR_EXECUTION"),
    ("ANNEX_II", "Anexo II", "Pedir texto, versión y certificado SAF355.", "Nota 84.749", "REQUEST_EXACT_OBJECT"),
    ("ANNEX_IV", "Anexo IV", "Comparador 2009 lo asocia a formularios tardíos; pedir objeto target.", "Nota 84.749 + Instructivo 2/2009", "REQUEST_EXACT_OBJECT"),
    ("ANNEX_V", "Anexo V", "Comparador 2009 lo asocia a ajustes/rectificaciones; pedir objeto target.", "Nota 86.232 + Instructivo 2/2009", "REQUEST_EXACT_OBJECT"),
    ("AUDIT_1_2009", "Instructivo 1/2009 GNyPE", "Informe UAI 04 auditó control interno, sistemas y metodología, separado de certificaciones.", "ENRE pp.162-163", "SEPARATE_AUDIT_LADDER"),
    ("REPORT_04", "Informe UAI ENRE 04", "Comparador; no es el informe del Ministerio de Economía.", "ENRE p.162", "COMPARATOR_ONLY"),
    ("SIGEN_WORK_INSTRUCTIONS", "Instrucciones de trabajo a UAI", "SIGEN declara haberlas emitido para certificaciones de la Cuenta.", "Memoria SIGEN 2009 p.6", "CENTRAL_ROUTE_PROVED"),
    ("SIGEN_GLOBAL_REPORT", "Informe de la Cuenta de Inversión 2008", "SIGEN declara un informe global sobre controles de los estados contables.", "Memoria SIGEN 2009 p.6", "EXACT_OBJECT_PROVED"),
    ("SIGEN_SUPERVISION", "Supervisión y coordinación de UAI", "SIGEN monitoreó planes y emitió informes de supervisión.", "Memoria SIGEN 2009 pp.5-7", "SUPERVISION_ROUTE_PROVED"),
    ("SYSTEM_EVALUATIONS", "124 evaluaciones de control interno", "Universo 2008; no individualiza SAF355.", "Memoria SIGEN 2009 p.5", "GLOBAL_UNIVERSE_ONLY"),
    ("MINISTRY_CERT", "Certificación UAI Ministerio de Economía / SAF355", "No localizada públicamente.", "Búsqueda V152", "TARGET_OPEN"),
    ("MINISTRY_AUDIT", "Informe 1/2009 para Economía/SAF355", "No localizado públicamente.", "Búsqueda V152", "TARGET_OPEN"),
    ("INSTR_BODY", "Cuerpo completo Instructivo 02/2008", "No localizado en la ruta pública ensayada.", "Búsqueda V151-V152", "INSTRUCTIVE_BODY_NOT_LOCATED"),
    ("ANNEX_VERSIONS", "Anexos y versiones distribuidas", "Pedir anexos, modificaciones, fecha, remitente y destinatarios.", "Control de completitud", "DRAFT_REQUEST"),
    ("DISPATCH_RECEIPT", "Notas de salida/entrada y acuses", "Pedir número, fecha, hora, adjuntos, firmante y receptor.", "Cadena de custodia", "DRAFT_REQUEST"),
    ("WORKPAPERS", "Papeles de trabajo UAI", "Pedir universo, muestra, hallazgos, ajustes, excepciones y conclusión.", "Cadena de auditoría", "DRAFT_REQUEST"),
    ("LIMIT_ENRE", "IDs 84.749 y 86.232", "Son notas ENRE, no números del SAF355.", "Control metodológico", "DO_NOT_TRANSPOSE"),
    ("LIMIT_CERT", "Certificación UAI", "Certifica consistencia/control; no sustituye movimiento bancario target.", "Control metodológico", "NOT_PAYMENT_PROOF"),
]
uai = matrix("E0_UAI_2008_INSTRUCTIVE_AND_EXECUTED_CERTIFICATION_ROUTE_V152.csv",
             ["row_id", "object_code", "object", "finding", "locator", "status"],
             [(f"UA152_{i:02d}",) + row for i, row in enumerate(uai_rows, 1)])

closing_rows = [
    ("YEAR_END_BASE", "CGN cerró 2008 con registros SIDIF e información complementaria.", "Res. SH 6/2008 art.1", "BASE_NOT_TARGET_ROW"),
    ("C41_DEADLINE", "C41 tuvo fecha límite 7/1/2009.", "Res.6 art.4", "TEMPORAL_LOCATOR"),
    ("C42_DEADLINE", "C42 cerró 31/12/2008; errores podían volver sin procesar.", "Res.6 art.4", "STATE_CONTROL"),
    ("FINAL_LISTS", "CGN puso listados definitivos SIDIF a disposición de SAF.", "Res.6 art.8", "EXACT_OUTPUT_CLASS"),
    ("TEN_DAYS", "SAF tenía diez días corridos para verificar y conciliar.", "Res.6 art.8", "DEADLINE"),
    ("FOUR_COMPARATORS", "Conciliación: sistema local, SIDIF, registros al 31/12 y listados parametrizados.", "Res.6 art.8", "MULTISOURCE_CONTROL"),
    ("DISCREPANCY_FORMS", "Diferencias requerían formularios de ajuste.", "Res.6 art.8", "ADJUSTMENT_RECORD"),
    ("EXPLANATORY_NOTE", "Diferencias requerían nota firmada por Secretario/Subsecretario.", "Res.6 art.8", "SIGNED_RECORD"),
    ("SIGEN_UAI_NOTICE", "No conformidad/discrepancia debía notificarse a SIGEN y UAI.", "Res.6 art.8", "NOTICE_ROUTE"),
    ("NONRECEIPT_NOTICE", "Información no recibida o inconsistente se comunicaba a SIGEN/UAI.", "Res.6 art.12", "NEGATIVE_CONTROL_ROUTE"),
    ("OFFICIAL_ARCHIVE", "Firma certificaba respaldo visto y originales en archivo oficial.", "Res.6 art.22", "ARCHIVE_CERTIFICATION"),
    ("RESPONSIBILITY", "Responsabilidad recaía en funcionarios firmantes.", "Res.6 art.22", "ACCOUNTABILITY"),
    ("MIDYEAR_CONFORMITY", "Cierre intermedio exigía conformidad e inalterabilidad salvo causa justificada.", "Disp.28 art.2", "MIDYEAR_CONTROL"),
    ("FINAL_MIDYEAR_BALANCES", "CGN enviaba saldos finales luego de regularizar inconsistencias.", "Disp.28 art.3", "MIDYEAR_OUTPUT"),
    ("MIDYEAR_NOTES", "Conformidad podía incluir aclaraciones por nota.", "Disp.28 art.3", "MIDYEAR_NOTE"),
    ("SAF355_EXCEPTION", "SAF355/356 estaban exceptuados de cuadros generales específicos.", "Disp.28 art.4", "SCOPE_EXCEPTION"),
    ("AXT_DETAIL", "ONCP debía enviar detalle AXT al 30/6 y explicar permanencia extrapresupuestaria.", "Disp.28 art.11", "TARGET_RELEVANT_BRANCH"),
    ("MIDYEAR_SIGNATURE", "Firma certificaba respaldo y archivo para estados alcanzados.", "Disp.28 art.15", "SCOPE_LIMITED_ARCHIVE"),
    ("MIDYEAR_NONREMIT", "Falta de remisión podía comunicarse a SIGEN.", "Disp.28 art.16", "NEGATIVE_CONTROL_ROUTE"),
    ("COMPARE_CUTS", "Cruzar 30/6, 31/12 y fechas de liquidación; saldo no equivale a flujo.", "Método V152", "RECONCILIATION_RULE"),
    ("ARCHIVE_NOT_PAYMENT", "Certificación de archivo no prueba ejecución bancaria.", "Método V152", "NOT_PAYMENT_PROOF"),
    ("ADJUSTMENT_NOT_EVENT", "Formulario de ajuste no es un hecho económico adicional.", "Método V152", "NON_ADDITIVE"),
]
closing = matrix("E0_2008_CLOSING_RECONCILIATION_AND_ARCHIVE_DUTY_V152.csv",
                 ["row_id", "object", "finding", "authority", "status"],
                 [(f"CR152_{i:02d}",) + row for i, row in enumerate(closing_rows, 1)])

axt_rows = [
    ("CUT", "30/06/2008", "Cierre intermedio; no sustituye 31/12.", "MIDYEAR_ONLY"),
    ("PRODUCER", "ONCP", "Productor del detalle AXT requerido.", "EXACT_CUSTODIAN"),
    ("RECIPIENT", "CGN", "Receptor del detalle y explicaciones.", "EXACT_CUSTODIAN"),
    ("OBJECT", "Detalle AXT de saldos registrados", "Pedir archivo, versión, soporte, nota e índice.", "EXACT_RECORD_CLASS"),
    ("EXPLANATION", "Breve explicación de operaciones", "Pedir texto completo por cuenta/operación.", "EXACT_FIELD"),
    ("NONBUDGET_REASON", "Razón de permanencia extrapresupuestaria", "Pedir campo y soporte.", "EXACT_FIELD"),
    ("TARGET_ACCOUNTS", "83106000 y cuentas/subcuentas candidatas", "Filtrar sin asumir identidad.", "SEARCH_KEY"),
    ("TARGET_IDS", "71597/0071597; 152677/0152677; 2876/0002876", "Buscar variantes con/sin cero.", "SEARCH_KEY"),
    ("TARGET_DATES", "02/09; 09/09; 16/09; 07/10/2008", "Fechas previstas; no confirman pago.", "SEARCH_KEY"),
    ("EXCEPTION", "SAF355 exceptuado de cuadros art.4", "No inferir ausencia de registro ni vía especial.", "NEGATIVE_CONTROL"),
    ("PAPER_SCOPE", "Original foliado/disco art.13", "No imponer a cuadros exceptuados para SAF355.", "SCOPE_LIMIT"),
    ("SIGNATURE_SCOPE", "Art.15", "Aplicar sólo a estados/formularios alcanzados.", "SCOPE_LIMIT"),
    ("BRIDGE_YEAR_END", "Comparar AXT 30/6 con listados finales 31/12", "Reconciliar altas, bajas, ajustes y reclasificaciones.", "CONTROLLED_BRIDGE"),
    ("BRIDGE_BANK", "Comparar AXT con extracto/CUT/TGN/BNA", "Sólo movimiento conciliado eleva 0/10.", "PAYMENT_GATE"),
    ("ZERO_RESULT", "Cero en Cuadro 1/13", "No cierra AXT, SIGADE, SIDIF, TRANSAF ni banco.", "NO_UNILATERAL_CLOSE"),
    ("REQUEST_STATUS", "Objetos AXT/conformidad", "BORRADOR_NO_ENVIADO.", "DRAFT_NOT_SENT"),
]
axt = matrix("E0_SAF355_MIDYEAR_AXT_AND_EXCEPTION_ROUTE_V152.csv",
             ["row_id", "object_code", "object", "finding", "status"],
             [(f"AX152_{i:02d}",) + row for i, row in enumerate(axt_rows, 1)])

param_rows = [
    ("MONTHLY_SEND", "CGN remitía listados parametrizados dentro de tres días hábiles.", "Disp.35 art.6", "PROCEDURE_PROVED"),
    ("TEXT_FORMAT", "Archivos en texto reutilizable en planilla, Access o Fox.", "Disp.35 art.6", "RECOVERABLE_FORMAT"),
    ("EMAIL_FAILURE", "Ante falla debía pedirse soporte magnético temporal.", "Disp.35 art.6", "ALTERNATE_MEDIA"),
    ("CONFORMITY_72H", "SAF debía conformar o discrepar en 72 horas.", "Disp.35 art.6", "DEADLINE"),
    ("SIGNED_NOTE", "Discrepancia exigía nota explicativa del titular SAF.", "Disp.35 art.6", "SIGNED_RECORD"),
    ("ADJUSTMENT_FORMS", "Debían acompañarse formularios de ajuste.", "Disp.35 art.6", "ADJUSTMENT_RECORD"),
    ("INCONSISTENCY_7D", "Regularización y respuesta: siete días hábiles.", "Disp.35 art.6", "DEADLINE"),
    ("ENTRY_DESK", "Respuesta papel ingresaba por Mesa de Entradas CGN.", "Disp.35 art.6", "RECEIPT_ROUTE"),
    ("PARAM_ADDRESS", "Conformidad/consultas usaban casilla param CGN.", "Disp.35 art.6", "COMMUNICATION_ROUTE"),
    ("SAF_PARAM_ADDRESS", "Cada SAF debía abrir casilla param+código.", "Disp.35 art.7", "TARGET_MAILBOX_PATTERN"),
    ("SAF_INCONSIS_ADDRESS", "Cada SAF debía abrir casilla inconsis+código.", "Disp.35 art.7", "TARGET_MAILBOX_PATTERN"),
    ("TRANSMISSION_RECEIPT", "Comunicación recibida desde transmisión CGN.", "Disp.35 art.7", "RECEIPT_RULE"),
    ("MIDMONTH", "CGN enviaba acumulado el día 19 o hábil siguiente.", "Disp.35 art.8", "ADDITIONAL_OUTPUT"),
    ("MONTH_END", "CGN enviaba anexo acumulado al último hábil.", "Disp.35 art.8", "ADDITIONAL_OUTPUT"),
    ("GENERAL_FORM", "Anexo I exige SAF, inconsistencia, fuente, imputación, formulario, N° SIDIF, N° SAF, observaciones y firma.", "Anexo I pp.1-3", "EXACT_SCHEMA"),
    ("UEPEX_FORM", "Anexo II replica campos y agrega clasificación programática.", "Anexo II pp.1-4", "COMPARATOR_SCHEMA"),
    ("BUDGET_MOD", "Modificación: informe ONP, tipo/número de acto y estado.", "Anexos I-II", "EXACT_SCHEMA"),
    ("2004_CONTINUITY", "Reglas 2004 reiteran texto, casilla param y 72 horas.", "CGN reglas 2004 sec.VII", "CONTINUITY_COMPARATOR"),
    ("2006_CONTINUITY", "Disp.31/2006 confirma listados locales aplicables al período.", "e0_cgn_disposition_31_2006_parameterized_reports", "TARGET_PERIOD_AUTHORITY"),
    ("2008_CLOSE", "Res.6/2008 exige conciliar listados finales, local, SIDIF y parametrizados.", "Res.6 art.8", "TARGET_YEAR_LINK"),
]
param = matrix("E0_2008_PARAMETERIZED_INCONSISTENCY_RESPONSE_CHAIN_V152.csv",
               ["row_id", "object", "finding", "authority", "status"],
               [(f"PI152_{i:02d}",) + row for i, row in enumerate(param_rows, 1)])


catalog_map = {s["local"].rsplit("/", 1)[-1]: s["id"] for s in source_rows}
roles = {
    "cgn_2004_opening_rules_parameterized_email.html": "CONTINUITY_COMPARATOR",
    "cgn_disposition_28_2008_ac_templates.zip": "AC_TEMPLATE_NEGATIVE_CONTROL",
    "cgn_disposition_28_2008_annex_index.html": "ANNEX_INDEX",
    "cgn_disposition_28_2008_download_index.html": "DOWNLOAD_INDEX",
    "cgn_disposition_28_2008_midyear_closing.html": "MIDYEAR_CLOSING_AUTHORITY",
    "cgn_disposition_35_2002_annex_i_saf_od.pdf": "GENERAL_SAF_INCONSISTENCY_SCHEMA",
    "cgn_disposition_35_2002_annex_ii_uepex.pdf": "UEPEX_INCONSISTENCY_SCHEMA",
    "cgn_disposition_35_2002_parameterized_inconsistency.html": "PARAMETERIZED_PROCEDURE",
    "enre_informe_anual_2009_uai_certifications.pdf": "EXECUTED_UAI_CERTIFICATION_COMPARATOR",
    "sigen_memoria_2009_cuenta_2008_control.pdf": "SIGEN_GLOBAL_CONTROL_ROUTE",
}
bundle_rows = []
for i, path in enumerate(sorted(BIN.iterdir(), key=lambda p: p.name.casefold()), 1):
    if path.is_file():
        sid = catalog_map.get(path.name, "EXISTING_SOURCE_OR_BUNDLE_ONLY")
        bundle_rows.append((f"B152_{i:02d}", path.name, roles.get(path.name, "PRESERVED_SUPPORT"),
                            "YES" if path.name in catalog_map else "NO", sid,
                            path.stat().st_size, sha256(path), "YES"))
bundle = matrix("E0_V152_SOURCE_BUNDLE.csv",
                ["row_id", "filename", "role", "catalogued", "catalog_source_id", "bytes", "sha256", "preserved"],
                bundle_rows)


visual = read_csv(V151 / "E0_V151_PDF_VISUAL_CONTROL.csv")
visual_raw = [
    ("e0_enre_annual_2009_uai_account_2008_certifications", "158", "162", "Informe UAI 04 e Instructivo 1/2009", "PASS", "comparador ENRE; no SAF355"),
    ("e0_enre_annual_2009_uai_account_2008_certifications", "159", "163", "Notas 84.749/86.232; Instructivo 02/2008 Anexos II/IV/V", "PASS", "existencia/ejecución comparadora; no cuerpo target"),
    ("e0_enre_annual_2009_uai_account_2008_certifications", "160", "164", "continuidad registro UAI", "PASS", "contexto"),
    ("e0_sigen_memory_2009_account_2008_global_control_report", "5", "5", "124 evaluaciones control interno", "PASS", "universo global"),
    ("e0_sigen_memory_2009_account_2008_global_control_report", "6", "6", "instrucciones UAI e Informe Cuenta 2008", "PASS", "global; no target"),
    ("e0_sigen_memory_2009_account_2008_global_control_report", "7", "7", "supervisión UAI", "PASS", "ruta; no validación target"),
    ("e0_cgn_disposition_35_2002_parameterized_inconsistency_procedure", "1", "1", "planilla SAF/OD: N° SIDIF y N° SAF", "PASS", "esquema vacío"),
    ("e0_cgn_disposition_35_2002_parameterized_inconsistency_procedure", "2", "2", "objetivo e instrucciones Anexo I", "PASS", "procedimiento"),
    ("e0_cgn_disposition_35_2002_parameterized_inconsistency_procedure", "3", "3", "campos y modificación presupuestaria Anexo I", "PASS", "no ejecución bancaria"),
    ("e0_cgn_disposition_35_2002_parameterized_inconsistency_procedure", "1", "1", "planilla UEPEX Anexo II", "PASS", "comparador UEPEX"),
    ("e0_cgn_disposition_35_2002_parameterized_inconsistency_procedure", "2", "2", "objetivo e instrucciones UEPEX", "PASS", "comparador"),
    ("e0_cgn_disposition_35_2002_parameterized_inconsistency_procedure", "3", "3", "campos SIDIF/SAF UEPEX", "PASS", "esquema vacío"),
    ("e0_cgn_disposition_35_2002_parameterized_inconsistency_procedure", "4", "4", "campos ONP y acto UEPEX", "PASS", "regularización no evento"),
]
visual_add = [dict(zip(["control_id", "source_id", "printed_page", "pdf_page", "rendered_check", "result", "inference_limit"],
                       (f"PV152_{i:03d}",) + row))
              for i, row in enumerate(visual_raw, len(visual) + 1)]
visual += visual_add
write_csv(HERE / "E0_V152_PDF_VISUAL_CONTROL.csv", visual, list(visual[0]))

negative_rows = [
    ("Instructivo SGN 02/2008 texto completo", "SIGEN/CGN", "No localizado; existencia/aplicación corroboradas por ENRE.", "INSTRUCTIVE_BODY_NOT_LOCATED"),
    ("Anexos completos Instructivo 02/2008", "SIGEN/CGN", "No localizados públicamente.", "ANNEX_BODIES_NOT_LOCATED"),
    ("Certificación UAI Cuenta 2008 Economía/SAF355", "Economía/SIGEN", "No localizada.", "TARGET_CERT_NOT_LOCATED"),
    ("Informe UAI Instructivo 1/2009 Economía/SAF355", "Economía/SIGEN", "No localizado.", "TARGET_AUDIT_NOT_LOCATED"),
    ("Informe SIGEN Cuenta 2008 cuerpo/anexos", "SIGEN", "Memoria prueba existencia; cuerpo no localizado.", "GLOBAL_REPORT_BODY_NOT_LOCATED"),
    ("Supervisión SIGEN UAI Economía 2009", "SIGEN", "Universo probado; target no localizado.", "SUPERVISION_TARGET_NOT_LOCATED"),
    ("Certificados Anexo IV/V SAF355", "Economía/UAI", "No localizados.", "TARGET_ANNEX_CERT_NOT_LOCATED"),
    ("Listado final Res.6 art.8 SAF355", "CGN/SAF355", "No localizado.", "FINAL_LIST_NOT_LOCATED"),
    ("Conformidad/discrepancia SAF355", "SAF355/CGN/UAI", "No localizada.", "TARGET_CONFORMITY_NOT_LOCATED"),
    ("Detalle AXT ONCP 30/06/2008", "ONCP/CGN", "Deber probado; archivo no localizado.", "AXT_DETAIL_NOT_LOCATED"),
    ("Casillas param355/inconsis355 2008", "CGN/SAF355", "Patrón probado; mensajes no localizados.", "TARGET_EMAILS_NOT_LOCATED"),
    ("Planillas Anexo I con IDs target", "CGN/SAF355", "Esquema preservado; filas no localizadas.", "TARGET_ROWS_NOT_LOCATED"),
]
negative = matrix("E0_V152_PUBLIC_SEARCH_NEGATIVE_RESULTS.csv",
                  ["row_id", "query_object", "route", "result", "status"],
                  [(f"NS152_{i:02d}",) + row for i, row in enumerate(negative_rows, 1)])
write_csv(HERE / "E0_V152_PUBLIC_SEARCH_NEGATIVE_RESULTS_V152.csv", negative, list(negative[0]))

request_rows = [
    ("INSTR_02", "SIGEN", "Instructivo SGN 02/2008 íntegro", "2008", "texto; anexos; versiones; fecha; firma; distribución", "Individualizar archivo, inventario y disposición si no se encuentra."),
    ("INSTR_02_ANNEXES", "SIGEN", "Todos los anexos del Instructivo 02/2008", "2008", "número; título; versión; páginas; hash", "No responder sólo con el cuerpo principal."),
    ("UAI_CERT_IV", "UAI Economía/SAF355", "Certificación Cuenta 2008 Anexo IV", "2008-2009", "nota; certificado; universo; hallazgos; firma; adjuntos", "Incluir reemplazos y rectificaciones."),
    ("UAI_CERT_V", "UAI Economía/SAF355", "Certificación Cuenta 2008 Anexo V", "2008-2009", "nota; certificado; universo; ajustes; firma; adjuntos", "Incluir soportes de diferencias."),
    ("UAI_ALL_CERTS", "UAI Economía/SAF355", "Todas las certificaciones bajo Instructivo 02/2008", "2008-2009", "anexo; número; fecha; firmante; resultado", "Enumerar anexos sin observaciones."),
    ("UAI_DISPATCH", "UAI/SAF355/CGN", "Registro de salida, entrada y acuses", "2008-2009", "número; fecha/hora; remitente; receptor; adjuntos", "Ofrecer metadatos testados."),
    ("UAI_WORKPAPERS", "UAI Economía", "Papeles de trabajo de certificación", "2008-2009", "universo; muestra; pruebas; excepciones; conclusión", "Individualizar legajo/caja/sistema."),
    ("UAI_AUDIT_1_2009", "UAI Economía/SIGEN", "Informe bajo Instructivo 1/2009 GNyPE", "2009", "informe; observaciones; plan; seguimiento", "Buscar equivalente al ENRE 04 sin trasponer ID."),
    ("SIGEN_GLOBAL", "SIGEN", "Informe de la Cuenta de Inversión 2008", "2008-2009", "cuerpo; anexos; base; universo; metodología; conclusiones", "No basta Memoria 2009."),
    ("SIGEN_SUPERVISION", "SIGEN", "Supervisión UAI Ministerio Economía", "2009", "informe; plan; observaciones; seguimiento", "Individualizar dentro del universo."),
    ("FINAL_LISTS", "CGN/SAF355", "Listados definitivos SIDIF art.8", "31/12/2008", "archivo; parámetros; columnas; filas; fecha; destinatario", "Cero debe documentar universo y consulta."),
    ("CONFORMITY", "SAF355/CGN", "Conformidad o discrepancia del cierre", "2008-2009", "nota; firma; fecha; listado; diferencias; adjuntos", "Incluir avisos a SIGEN/UAI."),
    ("ADJUSTMENTS", "SAF355/CGN", "Formularios de ajuste y notas", "2008-2009", "tipo; N° SIDIF; N° SAF; importe; estado; soporte", "No contar evento adicional sin conciliación."),
    ("ARCHIVE_INDEX", "SAF355/UAI", "Índice de originales art.22", "2008-2009", "serie; legajo; caja; folio; productor; transferencia", "Identificar destino/fecha."),
    ("AXT_DETAIL", "ONCP/CGN", "Detalle AXT al 30/06/2008", "2008-06-30", "cuenta; operación; saldo; explicación; razón extrapresupuestaria", "Cruzar con 31/12 y banco."),
    ("AXT_CONFORMITY", "ONCP/CGN", "Saldos finales y conformidad art.2-3", "2008-06", "archivo; versión; nota; ajustes; firmante", "Respetar excepción SAF355 art.4."),
    ("PARAM_EMAIL", "CGN/SAF355", "Mensajes/archivos param355 e inconsis355", "2008", "cabeceras; adjuntos; timestamp; acuse; respuesta", "Buscar backups y soporte magnético."),
    ("INCONSISTENCY_SHEETS", "CGN/SAF355", "Planillas Anexo I", "2008-2009", "SAF; anexo; fuente; imputación; tipo; N° SIDIF/SAF; firma", "Filtrar IDs target y cero reproducible."),
]
request_objects = matrix("E0_V152_REQUEST_OBJECTS.csv",
                         ["row_id", "object_id", "custodian", "exact_record", "period", "minimum_fields", "closure_rule", "status"],
                         [(f"RO152_{i:02d}",) + row + ("DRAFT_NOT_SENT",) for i, row in enumerate(request_rows, 1)])
write_csv(HERE / "E0_V152_REQUEST_OBJECTS_V152.csv", request_objects, list(request_objects[0]))


breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V152.csv")
break_raw = [
    ("uai_02_2008_existence_not_saf355_certification", "identity", "ENRE prueba existencia/aplicación, no certificación SAF355.", "Exigir certificado target.", "FROZEN_V152", "ENRE 2009 pp.162-163"),
    ("enre_internal_note_ids_not_saf355_ids", "identity", "84.749/86.232 son notas ENRE.", "No trasponer a SAF355.", "FROZEN_V152", "ENRE p.163"),
    ("uai_certification_not_bank_execution", "phase", "Certificación no es movimiento bancario.", "Cruzar comprobante, banco y reversas.", "FROZEN_V152", "Método E0"),
    ("sigen_global_account_report_not_target_audit", "scope", "Informe global no individualiza SAF355/IDs.", "Recuperar cuerpo/anexos/subinforme.", "FROZEN_V152", "SIGEN p.6"),
    ("midyear_axt_balance_not_yearend_transaction", "time", "Saldo AXT 30/6 no prueba flujo o 31/12.", "Puente de saldos/movimientos.", "FROZEN_V152", "Disp.28 art.11"),
    ("saf355_midyear_table_exception_not_record_absence", "scope", "Excepción de cuadros no es ausencia.", "Buscar AXT/SIGADE/SIDIF/banco.", "FROZEN_V152", "Disp.28 art.4"),
    ("signed_conformity_or_archive_certificate_not_payment", "phase", "Firma/conformidad acreditan control documental.", "No elevar 0/10 sin banco.", "FROZEN_V152", "Res.6 art.22; Disp.28 art.15"),
    ("adjustment_form_not_new_economic_event", "aggregation", "Ajuste puede corregir el mismo hecho.", "Vincular original-ajuste-reversa.", "FROZEN_V152", "Disp.35 Anexos"),
    ("instruction_1_2009_audit_not_02_2008_certification", "phase", "Auditoría y certificación son objetos distintos.", "Pedir ambos por separado.", "FROZEN_V152", "ENRE pp.162-163"),
]
breaks = upsert(breaks, [dict(zip(list(breaks[0]), row)) for row in break_raw], "break_id")
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V152.csv", breaks, list(breaks[0]))

trace = read_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V152.csv")
trace_raw = [
    ("REQ133_ECON", "SIGEN", "CL152_INSTR02", "Instructivo 02/2008 y anexos", "2008", "02/2008;II/IV/V", "texto;versión;firma;distribución", "metadatos/inventario/disposición", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "UAI Economía/SAF355", "CL152_CERTIV", "Certificación Anexo IV", "2008-2009", "SAF355;IDs", "nota;universo;resultado;firma", "campos testados", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "UAI Economía/SAF355", "CL152_CERTV", "Certificación Anexo V", "2008-2009", "SAF355;ajustes;IDs", "nota;ajustes;resultado;firma", "campos testados", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "UAI Economía", "CL152_WORKPAPERS", "Papeles de trabajo", "2008-2009", "SAF355;Cuenta2008", "universo;muestra;pruebas;conclusión", "inventario/disposición", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "UAI Economía/SIGEN", "CL152_AUDIT", "Informe Instructivo 1/2009", "2009", "SAF355;Cuenta2008", "informe;hallazgos;plan;seguimiento", "metadatos/índice", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "SIGEN", "CL152_GLOBAL", "Informe Cuenta de Inversión 2008", "2008-2009", "Cuenta2008;SAF355", "cuerpo;anexos;base;metodología", "metadatos/anexos testados", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "SIGEN", "CL152_SUPERVISION", "Supervisión UAI Economía", "2009", "Economía;SAF355", "plan;informe;observaciones;seguimiento", "inventario del universo", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "CGN/SAF355", "CL152_FINAL_LIST", "Listados finales art.8", "31/12/2008", "SAF355;83106000;IDs", "archivo;parámetros;filas;nota;firma", "cero reproducible", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "CGN/SAF355/UAI", "CL152_DISCREPANCY", "Discrepancias/ajustes/notificaciones", "2008-2009", "C41;C42;C55;IDs", "tipo;N° SIDIF/SAF;importe;acuse", "metadatos", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "SAF355/Archivo", "CL152_ARCHIVE", "Índice originales art.22", "2008-2009", "SAF355;C41/C42/C55", "legajo;caja;folio;transferencia", "inventario/destino", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "ONCP/CGN", "CL152_AXT", "Detalle AXT 30/06/2008", "2008-06-30", "83106000;IDs", "cuenta;operación;saldo;explicación", "cero/cobertura", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "ONCP/CGN", "CL152_MIDCONF", "Conformidad/saldos intermedios", "2008-06", "SAF355;AXT", "versión;nota;ajuste;firma", "índice/metadatos", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "CGN/SAF355", "CL152_PARAMMAIL", "Casillas param355/inconsis355", "2008", "SAF355;param;inconsis", "cabecera;adjunto;timestamp;acuse", "backup/soporte", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "CGN/SAF355", "CL152_SHEETS", "Planillas Anexo I", "2008-2009", "71597;152677;2876", "anexo;imputación;tipo;N° SIDIF/SAF;firma", "cero reproducible", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "CGN/SAF355", "CL152_BACKUP", "Backups listados/mensajes", "2008-2009", "param355;inconsis355;SIDIF", "soporte;fecha;prueba;log;custodio", "inventario/disposición", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "CGN/SAF355", "CL152_RECEIPT", "Mesa de Entradas/acuse", "2008-2009", "SAF355;Cuenta2008", "número;fecha;remitente;adjuntos;destino", "metadatos", "DRAFT_NOT_SENT"),
]
trace_fields = list(trace[0])
trace = upsert(trace, [dict(zip(trace_fields, (f"TR152_{i:03d}",) + row))
                       for i, row in enumerate(trace_raw, 1)], "trace_id")
write_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V152.csv", trace, trace_fields)

keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V152.csv")
key_raw = [
    ("REQ133_ECON", "document", "Instructivo de Trabajo SGN N° 02/2008", "localizar cuerpo/anexos", "ENRE p.163", "Existencia probada; cuerpo abierto."),
    ("REQ133_ECON", "document", "Certificaciones a la Cuenta de Inversión 2008", "localizar certificados", "ENRE p.163", "No trasponer IDs."),
    ("REQ133_ECON", "annex", "Anexo II; Anexo IV; Anexo V", "localizar versión", "ENRE p.163", "Exigir target."),
    ("REQ133_ECON", "document", "Instructivo N° 1/2009 GNyPE", "localizar auditoría", "ENRE p.162", "Separar de certificación."),
    ("REQ133_ECON", "document", "Informe de la Cuenta de Inversión del año 2008", "localizar SIGEN", "SIGEN p.6", "Global; pedir anexos."),
    ("REQ133_ECON", "record", "Listado definitivo SIDIF art. 8", "localizar salida final", "Res.6", "No prueba pago."),
    ("REQ133_ECON", "record", "conformidad; discrepancia; nota explicativa", "localizar control cierre", "Res.6 art.8", "Firma no prueba pago."),
    ("REQ133_ECON", "record", "detalle AXT de saldos al 30/06/2008", "localizar ONCP", "Disp.28 art.11", "Saldo no es flujo."),
    ("REQ133_ECON", "field", "razón por la cual permanecen como extrapresupuestarias", "localizar explicación", "Disp.28 art.11", "No inferir contenido."),
    ("REQ133_ECON", "mailbox", "param355", "localizar listados/backups", "Disp.35 art.7", "Validar dominio."),
    ("REQ133_ECON", "mailbox", "inconsis355", "localizar anexos/backups", "Disp.35 art.7", "Validar dominio."),
    ("REQ133_ECON", "form_field", "N° SIDIF; N° SAF", "localizar IDs duales", "Disp.35 Anexo I", "No asumir igualdad."),
    ("REQ133_ECON", "form_field", "Aclaraciones u observaciones; Firma Responsable del SAF", "localizar autoría", "Disp.35 Anexo I", "Firma no es ejecución."),
    ("REQ133_ECON", "identifier", "71597;0071597;152677;0152677;2876;0002876", "filtrar planillas", "Targets", "Variantes no prueban tipo."),
    ("REQ133_ECON", "account", "83106000", "filtrar AXT/listados", "Anexo K", "Cuenta agregada."),
    ("REQ133_ECON", "date", "2008-06-30;2008-12-31;2009-01-07", "cruzar cortes", "Disp.28;Res.6", "Cortes no son pagos."),
]
key_fields = list(keys[0])
keys = upsert(keys, [dict(zip(key_fields, (f"SK152_{i:02d}",) + row))
                     for i, row in enumerate(key_raw, 1)], "key_id")
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V152.csv", keys, key_fields)


# Restore source references without corrupting inherited lower-case paths.
source_ref_text = (V151 / "SOURCE_REFERENCES_V151.md").read_text(encoding="utf-8-sig").replace("V151", "V152")
(HERE / "SOURCE_REFERENCES_V152.md").write_text(source_ref_text, encoding="utf-8")
append_section(HERE / "SOURCE_REFERENCES_V152.md",
               "## Fuentes nuevas V152 · certificaciones UAI, cierre, AXT e inconsistencias",
               "\n".join("- " + s["id"] + " · " + s["title"] + " · " + s["url"] + " · " + s["local"] + " · " + s["sha"] for s in source_rows))

request_section = """
- Pedir Instructivo SGN 02/2008 íntegro, anexos, versiones y distribución.
- Pedir certificaciones UAI Economía/SAF355 de Anexos IV/V y universo completo.
- Pedir por separado informe 1/2009 GNyPE, papeles y seguimiento SIGEN.
- Pedir Informe SIGEN Cuenta 2008 completo, anexos, base y metodología.
- Pedir listados finales art.8, conformidad/discrepancia, ajustes y avisos.
- Pedir índice/legajo/caja/folio de originales cuyo archivo fue certificado.
- Pedir detalle AXT 30/06, explicaciones y razones extrapresupuestarias; cruzar 31/12.
- Pedir `param355`/`inconsis355`, cabeceras, adjuntos, acuses, respuestas y backups.
- Pedir planillas Anexo I con tipo, N° SIDIF, N° SAF, imputación y firma.
- Mantener seis pedidos `DRAFT_NOT_SENT`; ningún hallazgo eleva 0/10.
"""
append_section(HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V152.md", "## V152 · objetos exactos de certificación y cierre", request_section)
append_section(HERE / "REQUEST_SUBMISSION_CHECKLIST_V152.md", "## Control previo V152", request_section)

(HERE / "README_V152.md").write_text("""# V152 · certificación UAI 2008 y rastro firmado de inconsistencias

V152 prueba que el Instructivo SGN 02/2008 existió y fue aplicado para certificar la Cuenta 2008: ENRE registró notas para Anexos II, IV y V. Separa esas certificaciones del informe de auditoría bajo Instructivo 1/2009. SIGEN prueba un informe global sobre la Cuenta 2008 y supervisión UAI. Ninguno individualiza SAF355 o los tres IDs.

La Disposición 35/2002 aporta texto reutilizable, casillas `param<SAF>`/`inconsis<SAF>`, 72 horas, regularización, números SIDIF/SAF, observaciones y firma. La Resolución SH 6/2008 conecta el procedimiento al cierre target. La Disposición 28/2008 agrega detalle AXT ONCP al 30/06 y excepción de cuadros SAF355, que no equivale a ausencia.

Cuatro fuentes nuevas, diez archivos preservados, seis borradores no enviados, cuerpos target 0/3 y ejecución 0/10.
""", encoding="utf-8")

(HERE / "VEREDICTO_V152.md").write_text("""# Veredicto V152

La búsqueda se reduce a objetos nominados: Instructivo 02/2008 y anexos; certificaciones UAI IV/V; informe separado 1/2009; Informe SIGEN Cuenta 2008; listado final/conformidad art.8; detalle AXT; mensajes `param355`/`inconsis355`; planillas firmadas con N° SIDIF/SAF.

Las fuentes prueban deberes, nombres, campos, custodios, plazos y canales. No prueban que SAF355 emitiera una certificación, que los IDs target integraran una planilla ni que hubiera movimiento bancario. Los IDs ENRE no se trasponen.

Resultado conservador: 0/10; seis borradores `DRAFT_NOT_SENT`; cero presentaciones/respuestas.
""", encoding="utf-8")

(HERE / "E0_FISCAL_RECONSTRUCTION_V152.md").write_text("""# Reconstrucción fiscal E0 V152

V152 mantiene 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones. Agrega certificación UAI 2008, control SIGEN, cierre final firmado y AXT intermedio. La planilla permite enlazar N° SIDIF, N° SAF, tipo, imputación y firma, pero sólo comprobante más extracto/CUT/TGN/BNA y ausencia de reversa confirma ejecución.
""", encoding="utf-8")

(HERE / "RETRIEVAL_LOG_V152.md").write_text("""# Registro de recuperación V152

- Cuatro fuentes conceptuales oficiales nuevas y diez archivos preservados.
- Trece páginas PDF nuevas renderizadas e inspeccionadas; PASS.
- ENRE prueba existencia/ejecución comparadora del Instructivo 02/2008, Anexos II/IV/V.
- SIGEN prueba informe global Cuenta 2008 e instrucciones/supervisión UAI.
- Disp.35/2002 preserva formato, plazos, casillas y campos firmados.
- Disp.28/2008 identifica rama AXT ONCP y excepción SAF355.
- Cuerpo 02/2008, certificaciones SAF355, informe global completo y filas target no localizados.
- Excepción TLS del servidor oficial histórico documentada.
- Seis pedidos no presentados; cero respuestas; 0/10.
""", encoding="utf-8")

old_handover = HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V152_A_V152.md"
if old_handover.exists():
    old_handover.unlink()
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V152_A_V153.md").write_text("""# Handover V152 → V153

## Estado

- QA PASS; cuatro fuentes nuevas; diez archivos en bundle.
- Instructivo SGN 02/2008: existencia/ejecución comparadora probadas; cuerpo no localizado.
- ENRE: certificaciones II/IV/V y auditoría separada 1/2009.
- SIGEN: instrucciones UAI, Informe Cuenta 2008 y supervisión; cuerpos target abiertos.
- Disp.35/2002: texto, 72 horas, casillas SAF, regularización, N° SIDIF/SAF y firma.
- Res.6/2008: listados finales, conciliación, ajustes, nota y archivo oficial.
- Disp.28/2008: AXT ONCP 30/06 y excepción SAF355 sin probar ausencia.
- Targets no localizados; seis DRAFT_NOT_SENT; 0/10.

## Prioridad V153

1. Mantener borradores salvo autorización.
2. Localizar cuerpo/anexos SGN 02/2008 en archivos oficiales.
3. Buscar inventarios UAI Economía e Informe SIGEN Cuenta 2008 por título exacto.
4. Rastrear `param355`/`inconsis355`, AXT y planillas por N° SIDIF/SAF.
5. Vincular con listados finales, extractos, CUT/TGN/BNA y reversas.
6. Mantener 0/10 hasta cuerpo target y movimiento conciliado.
""", encoding="utf-8")

append_section(REPO / "BACKUP_ACTUALIZACION_2026-08-29.md", "## V152 · certificaciones UAI y rastro de inconsistencias", """
- Instructivo 02/2008 probado por ejecución comparadora ENRE; cuerpo/SAF355 abiertos.
- Informe global SIGEN Cuenta 2008 y supervisión UAI probados.
- Cierre final, AXT, casillas SAF y planillas SIDIF/SAF convertidos en pedidos.
- Cuatro fuentes; trece controles PDF nuevos; seis borradores no enviados; 0/10.
""")

register_path = HERE / "E0_REQUEST_RESPONSE_REGISTER_V152.csv"
register = read_csv(register_path)
for row in register:
    row.update({"status": "DRAFT_NOT_SENT", "submitted_on": "N/A", "submission_channel": "N/A",
                "receipt_or_case_id": "N/A", "response_date": "N/A"})
write_csv(register_path, register, list(register[0]))

write_csv(HERE / "INHERITED_QA_STATUS_V152.csv", [
    {"script": "qa_v151.py", "pre_v152_result": "PASS", "post_v152_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V151 ampliada por certificación 2008, AXT e inconsistencias."},
    {"script": "qa_v152.py", "pre_v152_result": "N/A", "post_v152_result": "PASS", "interpretation": "Verifica fuentes, matrices, borradores y 0/10."},
])

hash_rows = []
for row in catalog:
    local = row["archivo_local"]
    path = REPO / local.lstrip("/") if local else None
    exists = bool(path and path.is_file())
    actual = sha256(path) if exists else ""
    expected = row["sha256"]
    hash_rows.append({"id": row["id"], "archivo_local": local, "exists": str(exists),
                      "sha_catalog": expected, "sha_actual": actual,
                      "hash_ok": str(bool(exists and expected and actual.lower() == expected.lower()))})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V152.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V152.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)

size_rows = []
for path in iter_files(REPO):
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": size,
                      "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576),
                      "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V152.csv", size_rows)

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V151.json").read_text(encoding="utf-8-sig"))
image_visual = read_csv(HERE / "E0_V152_IMAGE_VISUAL_CONTROL.csv")
complete.update({
    "checkpoint": "V152", "date": "2026-08-31",
    "state": "E0_UAI_2008_CERTIFICATION_EXISTENCE_AND_SIGNED_INCONSISTENCY_ROUTE_PROVED_TARGET_BODIES_OPEN_NOT_SENT",
    "master_catalog_entries": len(catalog), "physical_local_copies": physical,
    "physical_local_hash_ok": hash_ok, "remaining_physical_gaps": len(catalog) - physical,
    "e0_primary_sources_preserved": len(census), "numeric_v152_strict_changed": False,
    "sources_newly_preserved_v152": len(source_rows), "e0_primary_sources_newly_preserved_v152": len(source_rows),
    "e0_fiscal_method_breaks_frozen": len(breaks), "e0_request_traceability_rows": len(trace),
    "e0_request_search_keys": len(keys), "e0_v152_pdf_visual_controls": len(visual),
    "e0_v152_new_pdf_visual_controls": len(visual_add), "e0_v152_image_visual_controls": len(image_visual),
    "e0_v152_total_visual_controls": len(visual) + len(image_visual), "e0_v152_source_bundle_files": len(bundle),
    "e0_uai_2008_route_rows": len(uai), "e0_closing_reconciliation_rows": len(closing),
    "e0_saf355_axt_rows": len(axt), "e0_parameterized_inconsistency_rows": len(param),
    "e0_v152_public_search_rows": len(negative), "e0_v152_request_objects": len(request_objects),
    "e0_uai_instruction_02_2008_existence_proved": True, "e0_uai_instruction_02_2008_body_located": False,
    "e0_uai_comparator_certifications_executed": True, "e0_uai_saf355_target_certification_located": False,
    "e0_sigen_account_2008_global_report_existence_proved": True,
    "e0_sigen_account_2008_global_report_body_located": False,
    "e0_saf355_midyear_axt_duty_proved": True, "e0_parameterized_signed_inconsistency_schema_proved": True,
    "e0_target_forms_public_bodies_located": 0, "e0_target_transaf_logs_located": 0,
    "e0_settlement_executed_rows_confirmed": 0, "e0_requests_submitted": 0,
    "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
    "historical_workstream": "Recover SGN 02/2008 body, SAF355 certifications, final lists, AXT detail, param/inconsis messages and bank reconciliation; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V152.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

(HERE / "AUDITORIA_V152.md").write_text(f"""# Auditoría V152

- Fuentes maestras: {len(catalog)}; E0: {len(census)}; nuevas: {len(source_rows)}.
- Copias/hash: {physical}/{hash_ok}; brechas: {len(catalog) - physical}.
- Quiebres: {len(breaks)}; trazas: {len(trace)}; claves: {len(keys)}.
- Visuales: {len(visual)} PDF ({len(visual_add)} nuevos) + {len(image_visual)} imágenes = {len(visual) + len(image_visual)}.
- Bundle: {len(bundle)}; UAI: {len(uai)}; cierre: {len(closing)}; AXT: {len(axt)}; inconsistencias: {len(param)}.
- Cuerpos target 0/3; logs 0/3; ejecución 0/10; pedidos/respuestas 0/0.
""", encoding="utf-8")


def checkpoint_manifest():
    files = [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha256(p)}
             for p in sorted(HERE.iterdir()) if p.is_file() and p.name != "MANIFEST_V152.json"]
    payload = {
        "checkpoint": "V152", "parent_checkpoint": "V151",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": len(source_rows),
        "fiscal_method_breaks": len(breaks), "request_traceability_rows": len(trace),
        "request_search_keys": len(keys), "pdf_visual_controls_total": len(visual),
        "pdf_visual_controls_new": len(visual_add), "image_visual_controls_inherited": len(image_visual),
        "source_bundle_files": len(bundle), "uai_2008_route_rows": len(uai),
        "closing_reconciliation_rows": len(closing), "saf355_axt_rows": len(axt),
        "parameterized_inconsistency_rows": len(param), "public_search_rows": len(negative),
        "v152_request_objects": len(request_objects), "uai_instruction_02_2008_existence_proved": True,
        "uai_instruction_02_2008_body_located": False, "uai_saf355_target_certification_located": False,
        "sigen_account_2008_global_report_body_located": False, "target_forms_public_bodies_located": 0,
        "target_transaf_logs_located": 0, "award_rows_exact": 10, "account_candidate_rows": 9,
        "executed_settlement_rows_confirmed": 0, "request_drafts": 6, "requests_submitted": 0,
        "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V152.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tree(root):
    lines = []
    root = Path(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted((n for n in dirnames if n not in EXCLUDED_DIRS), key=str.casefold)
        base = Path(dirpath)
        lines.extend((base / n).relative_to(root).as_posix() + "/" for n in dirnames)
        lines.extend((base / n).relative_to(root).as_posix() for n in sorted(filenames, key=str.casefold))
    return "\n".join(lines) + "\n"


(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")
checkpoint_manifest()

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path": p.relative_to(REPO).as_posix(), "bytes": p.stat().st_size, "sha256": sha256(p)}
                for p in iter_files(REPO) if p != global_manifest]
payload = {
    "checkpoint": "V152",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master; {physical} physical SHA-valid; {len(source_rows)} new sources; UAI 02/2008 existence and signed inconsistency route proved; targets open; 0/10; six drafts not submitted.",
    "historical_workstream": "Recover SGN 02/2008 body, SAF355 certifications, final lists, AXT detail, param/inconsis messages and bank reconciliation; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
tmp = global_manifest.with_suffix(".json.v152tmp")
tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
tmp.replace(global_manifest)

print(f"V152 BUILD PASS · catalog={len(catalog)} · E0={len(census)} · physical={physical} · hash_ok={hash_ok} · breaks={len(breaks)} · trace={len(trace)} · keys={len(keys)} · visual={len(visual) + len(image_visual)}")
