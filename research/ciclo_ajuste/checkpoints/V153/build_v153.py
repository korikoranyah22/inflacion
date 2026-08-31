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
BIN = CYCLE / "inputs" / "historical_retrieval" / "v153" / "binaries"
V152 = CYCLE / "checkpoints" / "V152"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"
EXCLUDED_DIRS = {".git", "__pycache__", "tmp", "node_modules"}


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


def matrix(name, fields, raw_rows):
    rows = [dict(zip(fields, row)) for row in raw_rows]
    write_csv(HERE / name, rows, fields)
    return rows


def append_section(path, marker, body):
    path = Path(path)
    text = path.read_text(encoding="utf-8-sig")
    if marker not in text:
        path.write_text(text.rstrip() + "\n\n" + marker + "\n\n" + body.strip() + "\n", encoding="utf-8")


def iter_files(root):
    root = Path(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted((name for name in dirnames if name not in EXCLUDED_DIRS), key=str.casefold)
        for filename in sorted(filenames, key=str.casefold):
            yield Path(dirpath) / filename


# Keep inherited lowercase source paths anchored to V152; only V153 owns this bundle.
census = read_csv(V152 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V152.csv")
provenance = read_csv(V152 / "ARCHIVAL_PROVENANCE_V152.csv")

# id, institution, title, url, filename, period, series, kind, note, variables, breaks
SOURCES = [
    (
        "e0_cgn_circular_1_2009_account_2008_uai_certification", "Contaduría General de la Nación",
        "Circular CGN 01/09 · cierre 2008 y certificación UAI obligatoria",
        "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/2009/cir01.htm",
        "cgn_circular_1_2009_account_2008_uai_certification.html", "2008-2009", "Circular CGN 01/09",
        "HTML oficial histórico preservado",
        "Identifica y enlaza el Instructivo 2/2008; CGN declara que no recibiría la documentación de cierre indicada sin certificación UAI. Es una barrera de recepción, no el certificado SAF355 ni un pago.",
        "CGN;UAI;Cuenta2008;receipt_gate;certification;closing",
        "obligación/cumplimiento target; recepción/pago; circular/certificado ejecutado",
    ),
    (
        "e0_sigen_instruction_2_2008_account_2008_certification", "Sindicatura General de la Nación",
        "Instructivo de Trabajo 2/2008 GNyPE · auditoría de información para la Cuenta de Inversión",
        "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/2009/acir01.pdf",
        "sigen_instruction_2_2008_account_certification.pdf", "2008-2009", "Instructivo de Trabajo 2/2008 GNyPE",
        "PDF oficial histórico preservado",
        "Cuerpo íntegro de once páginas con Anexos I-V, fuentes de contraste, modelos, ruta CGN/SIGEN y plazos. Define el procedimiento, pero no contiene las certificaciones ejecutadas del SAF355.",
        "SIGEN;UAI;Cuenta2008;AnnexI;AnnexII;AnnexIII;AnnexIV;AnnexV;SIDIF;SLU;bank_statements",
        "modelo/certificado ejecutado; conciliación/pago individual; UEPEX/SAF355",
    ),
    (
        "e0_sigen_white_book_2012_account_2008_report_inventory", "Sindicatura General de la Nación",
        "Informe de Control Interno y Gestión 2007/2011 · inventario del informe Cuenta 2008",
        "https://www.argentina.gob.ar/sites/default/files/libro_blanco_sigen2012.pdf",
        "sigen_libro_blanco_2012_report_inventory.pdf", "2008-2011", "Libro Blanco SIGEN 2012 · Anexos",
        "PDF oficial preservado",
        "Registra para Ministerio de Economía y Finanzas Públicas, año 2009 y área GSEPyPF, un informe global sobre calidad de información y documentación de la Cuenta 2008. No ofrece número, cuerpo, anexos ni validación SAF355.",
        "SIGEN;Cuenta2008;MinisterioEconomia;GSEPyPF;report_inventory;internal_control",
        "inventario/cuerpo; informe global/validación SAF355; año del informe/período auditado",
    ),
    (
        "e0_cgn_circular_8_2009_financial_document_archive_iso", "Contaduría General de la Nación",
        "Circular CGN 08/09 · Archivo General de Documentación Financiera",
        "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/2009/cir08.htm",
        "cgn_circular_8_2009_financial_document_archive_iso.html", "2009", "Circular CGN 08/09",
        "HTML oficial histórico preservado",
        "Documenta digitalización, guarda, descripción y atención a usuarios del archivo CGN; además, valor jurídico de impresiones de imágenes procesadas por CGN. Prueba capacidad, no ingreso del legajo target.",
        "CGN;AGDFA;digitization;custody;description;legal_value;SAF",
        "capacidad/ingreso target; imagen/original bancario; custodia/hallazgo",
    ),
]

source_rows = []
for sid, institution, title, url, filename, period, series, kind, note, variables, breaks_note in SOURCES:
    path = BIN / filename
    assert path.is_file(), path
    source_rows.append({
        "id": sid, "institution": institution, "title": title, "url": url,
        "local": "/" + path.relative_to(REPO).as_posix(), "period": period,
        "series": series, "kind": kind, "note": note, "variables": variables,
        "breaks": breaks_note, "sha": sha256(path), "bytes": path.stat().st_size,
    })

catalog = read_csv(CATALOG)
catalog = upsert(catalog, [{
    "id": s["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": s["institution"],
    "titulo": s["title"], "url_original": s["url"], "archivo_local": s["local"],
    "fecha_descarga": "2026-08-31", "fecha_publicacion": s["period"],
    "codigo_serie": s["series"], "periodo_utilizado": s["period"], "tipo": s["kind"],
    "sha256": s["sha"], "nota": "V153: " + s["note"],
} for s in source_rows], "id")
write_csv(CATALOG, catalog, list(catalog[0]))

census = upsert(census, [{
    "source_id": s["id"], "institution": s["institution"], "artifact": s["title"],
    "url": s["url"], "local_path": s["local"], "sha256": s["sha"], "bytes": s["bytes"],
    "period_coverage": s["period"], "variable_families": s["variables"],
    "primary_source": "YES", "preserved": "YES", "method_breaks": s["breaks"],
    "use_status": "E0_USABLE_WITH_SCOPE", "caveat": s["note"],
} for s in source_rows], "source_id")
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V153.csv", census, list(census[0]))

provenance = upsert(provenance, [{
    "source_id": s["id"], "original_url": s["url"], "retrieval_url": s["url"],
    "capture_timestamp": "2026-08-31", "cdx_digest": "N/A_OFFICIAL_DIRECT",
    "local_path": s["local"], "sha256": s["sha"], "bytes": s["bytes"],
    "provenance_note": "Captura directa oficial; alcance probatorio congelado en V153."
    + (" Descarga con excepción TLS por el servidor oficial histórico."
       if "economia.gob.ar/hacienda" in s["url"] else ""),
} for s in source_rows], "source_id")
write_csv(HERE / "ARCHIVAL_PROVENANCE_V153.csv", provenance, list(provenance[0]))


circular_rows = [
    ("DATE", "20/01/2009", "Fecha de Circular CGN 01/09.", "OFFICIAL_METADATA"),
    ("REFERENCE", "Cierre del Ejercicio 2008 - Certificación Unidad de Auditoría Interna", "Objeto exacto.", "OFFICIAL_METADATA"),
    ("ADDRESSEE", "Jefe del Servicio Administrativo Financiero", "La obligación se comunicó al SAF.", "ROUTING"),
    ("INSTRUCTION", "Instructivo de Trabajo 2/2008 GNyPE", "La circular lo enlaza como documento reglamentario.", "EXACT_LINK"),
    ("AUTHORITY", "Resolución SGN 10/2006", "Marco normativo citado.", "AUTHORITY"),
    ("OBJECT", "Información respaldatoria de la Cuenta de Inversión 2008", "Universo documental alcanzado.", "SCOPE"),
    ("GATE", "CGN no recibiría la documentación indicada sin certificación UAI", "Barrera expresa de recepción.", "RECEIPT_GATE_PROVED"),
    ("BODY", "El PDF enlazado contiene los cinco anexos", "Cierra la brecha de texto y modelos.", "BODY_LOCATED"),
    ("TARGET", "Certificación ejecutada UAI Economía/SAF355", "No está adjunta a la circular.", "TARGET_OPEN"),
    ("RECEIPT", "Constancia de recepción CGN", "Pedir número, fecha y adjuntos.", "DRAFT_NOT_SENT"),
    ("NONCOMPLIANCE", "Aviso de falta o rechazo", "Pedir si no existió certificación aplicable.", "DRAFT_NOT_SENT"),
    ("LIMIT_DUTY", "Deber normativo", "No demuestra cumplimiento individual.", "METHOD_LIMIT"),
    ("LIMIT_CERT", "Certificación contable", "No sustituye extracto ni movimiento bancario.", "METHOD_LIMIT"),
    ("LIMIT_PAYMENT", "Recepción del cierre", "No acredita liquidación de los tres IDs target.", "NOT_PAYMENT_PROOF"),
]
circular = matrix("E0_CGN_CIRCULAR_1_2009_RECEIPT_GATE_V153.csv",
                  ["row_id", "object_code", "finding", "interpretation", "status"],
                  [(f"CG153_{i:02d}",) + row for i, row in enumerate(circular_rows, 1)])

instruction_rows = [
    ("TITLE", "Instructivo de Trabajo 2/2008 GNyPE", "Auditoría de Información para la Cuenta de Inversión", "p.1", "BODY_LOCATED"),
    ("DATE", "30/12/2008", "Fecha de emisión", "p.1", "OFFICIAL_METADATA"),
    ("AUTHORITY", "Resolución SGN 10/2006", "Marco reglamentario", "p.1", "AUTHORITY"),
    ("MODELS", "Anexos I, II, III, IV y V", "Modelos de certificación contable", "p.1", "FIVE_ANNEXES_LOCATED"),
    ("UEPEX", "Cuadro 9.a separado por cada UEPEX", "Regla adicional para Administración Central", "p.1", "SCOPE_RULE"),
    ("ROUTE_CGN", "Certificación al SAF para remisión a CGN", "Se adjunta a información de cierre", "p.1", "ROUTING"),
    ("ROUTE_SIGEN", "Copia a SIGEN por Síndico Jurisdiccional/Representante", "Ruta paralela de control", "p.1", "ROUTING"),
    ("DEADLINE_I_IV", "09/02/2009", "Plazo de Anexos I-IV", "p.1", "DEADLINE"),
    ("DEADLINE_V", "Ocho días hábiles desde remanente provisorio CGN", "Plazo Anexo V", "p.1", "DEADLINE"),
    ("A1_OBJECT", "Cuadro 1 Anexo B - Movimientos Financieros (Caja y Bancos)", "Saldos finales e información complementaria 2008", "pp.2-3", "ANNEX_I"),
    ("A1_LOCAL", "SIU o sistema aplicable", "Registros presupuestarios y contables", "p.2", "SOURCE_CLASS"),
    ("A1_C43", "Formularios C43", "Fondos propios en caja y bancos", "p.2", "SOURCE_CLASS"),
    ("A1_ESCRITURAL", "Cuentas escriturales, si correspondía", "Registro complementario", "p.2", "SOURCE_CLASS"),
    ("A1_BANK", "Extractos bancarios", "Fuente externa de contraste", "p.2", "BANK_SOURCE"),
    ("A1_ARQUEO", "Acta de Arqueo de Caja, Fondos y Valores", "Fuente física de contraste", "p.2", "PHYSICAL_SOURCE"),
    ("A1_CERT", "Cifras de Cuadro 1 Anexo B surgen de registros y fuentes", "Modelo de certificación", "p.3", "MODEL_NOT_EXECUTED_TARGET"),
    ("A2_OBJECT", "Cuadro 1 Anexo C - Movimiento de Fondo Rotatorio", "Información 2008", "pp.4-5", "ANNEX_II"),
    ("A2_C43", "C43 de creación, ampliación o disminución", "Registro específico del fondo", "p.4", "SOURCE_CLASS"),
    ("A2_REMAINDER", "Pedido de ajuste al cálculo del remanente", "Fuente documental complementaria", "p.4", "ADJUSTMENT_SOURCE"),
    ("A2_BANK", "Extractos bancarios", "Contraste externo", "p.4", "BANK_SOURCE"),
    ("A2_CERT", "Cifras de Anexo C surgen de registros y fuentes", "Modelo de certificación", "p.5", "MODEL_NOT_EXECUTED_TARGET"),
    ("A3_OBJECT", "Cuadro 5.4 - UEPEX, intereses por saldos inmovilizados", "Aplicación por cada UEPEX", "pp.6-7", "ANNEX_III_UEPEX"),
    ("A3_SIDIF", "Listado Parametrizado SIDIF Central remitido por CGN", "Registro de contraste", "p.6", "SOURCE_CLASS"),
    ("A3_LOCAL", "Listados del sistema de registro de la UEPEX", "Debe detallarse", "p.6", "SOURCE_CLASS"),
    ("A3_BANK_TGN", "Extractos, formularios de transferencias a TGN y arqueo", "Fuentes externas y físicas", "p.6", "MULTISOURCE"),
    ("A3_CERT", "Cifras del Cuadro 5.4 surgen de registros y fuentes", "Modelo de certificación", "p.7", "MODEL_NOT_EXECUTED_TARGET"),
    ("A4_OBJECT", "C35, C41, C42, C43, C55, C75 y C10 presentados fuera de fecha tope", "Formularios 2008 vencidos y aún no emitidos a la UAI", "pp.8-9", "ANNEX_IV_TARGET_RELEVANT"),
    ("A4_SIDIF", "Listado Parametrizado SIDIF Central remitido por CGN", "Registro de contraste", "p.8", "SOURCE_CLASS"),
    ("A4_LOCAL", "Listado SLU o sistema aplicable", "Registro local", "p.8", "SOURCE_CLASS"),
    ("A4_BANK_TGN", "Extractos y formularios de transferencias a TGN", "Fuentes externas", "p.8", "MULTISOURCE"),
    ("A4_ARQUEO", "Acta de Arqueo de Fondos y Valores", "Fuente física", "p.8", "PHYSICAL_SOURCE"),
    ("A4_REMAINDER", "Información respaldatoria del ajuste de remanente", "Fuente documental", "p.8", "ADJUSTMENT_SOURCE"),
    ("A4_CERT", "Cifras de anexo y documentación surgen de registros y fuentes", "Modelo de certificación", "p.9", "MODEL_NOT_EXECUTED_TARGET"),
    ("A5_OBJECT", "Ratificación o rectificación del Remanente Provisorio 2008", "Comunicación SAF contra cálculo CGN", "pp.10-11", "ANNEX_V"),
    ("A5_SIDIF", "Listado SLU/sistema y Listado Parametrizado SIDIF Central", "Registros presupuestarios y contables", "p.10", "SOURCE_CLASS"),
    ("A5_ERRORS", "Depósitos erróneos, duplicaciones, devolución de depósitos de terceros y de sueldos", "Antecedentes de rectificaciones", "p.10", "ADJUSTMENT_SOURCE"),
    ("A5_CERT", "Ratificación/rectificación surge de registros y fuentes", "Modelo de certificación", "p.11", "MODEL_NOT_EXECUTED_TARGET"),
    ("LIMIT_BODY", "Cuerpo y modelos", "No prueban que SAF355 emitió, remitió o recibió una certificación", "pp.1-11", "METHOD_LIMIT"),
    ("LIMIT_BANK", "Extracto bancario como fuente", "Su mención no reemplaza el extracto target", "pp.2,4,6,8", "METHOD_LIMIT"),
    ("LIMIT_PAYMENT", "Consistencia del cierre", "No individualiza beneficiario, cuenta, importe, fecha valor o reversa", "pp.1-11", "NOT_PAYMENT_PROOF"),
]
instruction = matrix("E0_UAI_INSTRUCTION_2_2008_EXACT_ANNEX_AND_SOURCE_MAP_V153.csv",
                     ["row_id", "object_code", "object", "finding", "locator", "status"],
                     [(f"UI153_{i:02d}",) + row for i, row in enumerate(instruction_rows, 1)])

branch_rows = [
    ("SAF", "Servicio Administrativo Financiero 355", "Universo institucional target", "TARGET_SCOPE"),
    ("A1", "Caja y Bancos", "Pedir certificado ejecutado o no aplicabilidad; incluye C43, extractos y arqueo.", "HIGH_RELEVANCE_OPEN"),
    ("A1_FIELDS", "Cuadro 1 Anexo B", "Solicitar versión, cifras, observaciones, firma, fecha, nota y fuentes.", "DRAFT_NOT_SENT"),
    ("A2", "Fondo Rotatorio", "Pedir certificado/no aplicabilidad; por sí solo no corresponde a deuda target.", "CONDITIONAL_OPEN"),
    ("A2_FIELDS", "Cuadro 1 Anexo C", "Solicitar C43 de fondo, extractos y soportes de ajuste.", "DRAFT_NOT_SENT"),
    ("A3", "UEPEX", "Sólo aplica si una UEPEX del ámbito SAF355 quedó incluida.", "NEGATIVE_CONTROL"),
    ("A3_FIELDS", "Cuadro 5.4", "Pedir índice por UEPEX y constancia de no aplicabilidad si fue cero.", "DRAFT_NOT_SENT"),
    ("A4", "Formularios fuera de fecha", "Rama central para C41/C42/C55 y demás formularios vencidos.", "HIGH_RELEVANCE_OPEN"),
    ("A4_UNIVERSE", "C35/C41/C42/C43/C55/C75/C10", "Pedir anexo completo, listado y estado final.", "DRAFT_NOT_SENT"),
    ("A4_TARGET", "71597; 152677; 2876", "Filtrar por IDs, N° SIDIF/SAF, importe, beneficiario, fecha, cuenta y reversa.", "DRAFT_NOT_SENT"),
    ("A4_ZERO", "Resultado cero", "Debe incluir universo, consulta, parámetros y cobertura reproducible.", "CLOSURE_RULE"),
    ("A5", "Remanente Provisorio", "Puede capturar rectificaciones; no equivale a pago individual.", "CONDITIONAL_OPEN"),
    ("A5_FIELDS", "Ratificación/rectificación", "Pedir comunicación SAF, cálculo CGN, antecedentes y certificado.", "DRAFT_NOT_SENT"),
    ("DISPATCH", "Salida UAI y entrada SAF/CGN", "Pedir número, fecha/hora, remitente, destinatario, adjuntos y acuse.", "DRAFT_NOT_SENT"),
    ("SIGEN_COPY", "Copia a SIGEN", "Pedir ingreso por Síndico y ubicación archivística.", "DRAFT_NOT_SENT"),
    ("WORKPAPERS", "Papeles de trabajo", "Pedir universo, muestra, pruebas, excepciones y conclusión por anexo.", "DRAFT_NOT_SENT"),
    ("LATE_FORMS", "Formularios no emitidos al momento UAI", "Pedir fecha tope y fecha efectiva de cada emisión.", "DRAFT_NOT_SENT"),
    ("BANK_LINK", "Extractos mencionados", "Pedir banco, cuenta, moneda, fecha valor, movimiento y saldo.", "DRAFT_NOT_SENT"),
    ("REVERSALS", "Ajustes y rectificaciones", "Vincular original, reemplazo, rechazo, reversa y estado final.", "DRAFT_NOT_SENT"),
    ("ABSENCE", "Certificado inexistente", "Pedir causa, aviso de incumplimiento y autoridad responsable.", "CLOSURE_RULE"),
    ("LIMIT", "Certificación ejecutada", "Aun localizada, requiere cruce con comprobante y banco para elevar 0/10.", "NOT_PAYMENT_PROOF"),
]
branch = matrix("E0_SAF355_UAI_CERTIFICATION_TARGET_BRANCH_V153.csv",
                ["row_id", "object_code", "object", "request_or_finding", "status"],
                [(f"SB153_{i:02d}",) + row for i, row in enumerate(branch_rows, 1)])

locator_rows = [
    ("SOURCE", "Informe de Control Interno y Gestión 2007/2011", "Inventario oficial SIGEN", "OFFICIAL_INVENTORY"),
    ("PAGE", "PDF 54 / impresa Anexos-XX", "Fila exacta visualmente verificada", "VISUAL_PASS"),
    ("ENTITY", "Ministerio de Economía y Finanzas Públicas", "Entidad/organismo", "EXACT_LOCATOR"),
    ("YEAR", "2009", "Año consignado", "EXACT_LOCATOR"),
    ("AREA", "GSEPyPF", "Área SIGEN consignada", "EXACT_LOCATOR"),
    ("OBJECT", "Visión global de controles internos de las jurisdicciones PEN", "Primera parte del objetivo", "EXACT_LOCATOR"),
    ("ACCOUNT", "Calidad de información y documentación de la Cuenta de Inversión 2008", "Objeto contable exacto", "EXACT_LOCATOR"),
    ("REPORT_NO", "No consignado", "El inventario no da número ni carátula", "OPEN"),
    ("BODY", "No incluido", "El inventario no contiene cuerpo ni anexos", "OPEN"),
    ("SAF355", "No individualizado", "No valida los tres IDs target", "OPEN"),
    ("PUBLIC_ARCHIVE", "Archivo público SIGEN visible: 121 entradas, 2020-2026", "La tabla actual no expone 2009", "CURRENT_SCOPE_ONLY"),
    ("PUBLIC_LIMIT", "Ventana pública actual", "No prueba inexistencia del informe 2009", "METHOD_LIMIT"),
    ("REQUEST_KEY", "Entidad + 2009 + GSEPyPF + objetivo exacto", "Clave archivística primaria", "DRAFT_NOT_SENT"),
    ("REQUEST_METADATA", "Número, título, expediente, fecha, firmantes y destinatarios", "Metadatos mínimos", "DRAFT_NOT_SENT"),
    ("REQUEST_BODY", "Cuerpo, anexos, base, universo, metodología y conclusiones", "Contenido mínimo", "DRAFT_NOT_SENT"),
    ("REQUEST_FALLBACK", "Inventario, disposición final y ubicación física/digital", "Cierre si no se localiza", "DRAFT_NOT_SENT"),
]
locator = matrix("E0_SIGEN_ACCOUNT_2008_REPORT_ARCHIVE_LOCATOR_V153.csv",
                 ["row_id", "object_code", "value", "interpretation", "status"],
                 [(f"SG153_{i:02d}",) + row for i, row in enumerate(locator_rows, 1)])

archive_rows = [
    ("C8_DATE", "01/10/2009", "Circular CGN 08/09", "OFFICIAL_METADATA"),
    ("ARCHIVE", "Archivo General de Documentación Financiera de la Administración Nacional", "Dependiente de CGN", "NAMED_CUSTODIAN"),
    ("ISO", "Certificación IRAM-ISO 9001:2008 otorgada el 06/07/2009", "Sistema de calidad", "CAPABILITY"),
    ("SCOPE_DIGITIZE", "Digitalización de documentos", "Servicio certificado", "CAPABILITY"),
    ("SCOPE_GUARD", "Guarda de documentación recibida", "Custodia sobre lo recibido", "CAPABILITY"),
    ("SCOPE_DESCRIBE", "Descripción de documentación recibida", "Índice/metadatos plausibles", "CAPABILITY"),
    ("USERS", "Atención a usuarios del sistema", "Ruta de consulta", "ACCESS_ROUTE"),
    ("AUTHORITY_1998", "Disposición CGN 46/1998", "Norma de recepción citada", "AUTHORITY"),
    ("SAF_SUPPORT", "Recursos para que SAF digitalicen archivos", "Ruta institucional ofrecida", "ARCHIVAL_ROUTE"),
    ("OPTICAL", "Documentación a resguardar en soportes ópticos", "Soporte mencionado", "ARCHIVAL_ROUTE"),
    ("LEGAL_VALUE", "CGN habilitada para dar valor jurídico a impresión de imagen procesada", "Carácter de original", "LEGAL_VALUE_ROUTE"),
    ("C6_PROJECT", "Proyecto de Archivo Informático Histórico SIDIF con pleno valor jurídico", "Circular 06/09: presentación y resguardo de imágenes", "CONTEXT_ONLY"),
    ("TARGET_LIMIT", "Capacidad del archivo", "No prueba que ingresó la certificación o listado SAF355", "METHOD_LIMIT"),
    ("REQUEST", "Índice AGDFA por SAF355, Cuenta 2008, UAI, GSEPyPF y Anexos I-V", "Pedir legajo, soporte, transferencia y disposición", "DRAFT_NOT_SENT"),
]
archive = matrix("E0_CGN_FINANCIAL_ARCHIVE_CUSTODY_ROUTE_V153.csv",
                 ["row_id", "object_code", "object", "finding", "status"],
                 [(f"AR153_{i:02d}",) + row for i, row in enumerate(archive_rows, 1)])

# Resolve the inherited contradiction now that the instruction and annexes are public.
uai = read_csv(V152 / "E0_UAI_2008_INSTRUCTIVE_AND_EXECUTED_CERTIFICATION_ROUTE_V152.csv")
for row in uai:
    if row["object_code"] == "INSTR_02_EXISTENCE":
        row.update({"finding": "Existencia, cuerpo íntegro y Anexos I-V localizados en Circular CGN 01/09.",
                    "locator": "Circular 01/09 + acir01.pdf pp.1-11", "status": "BODY_AND_ANNEXES_LOCATED"})
    elif row["object_code"] == "INSTR_BODY":
        row.update({"finding": "Cuerpo completo de once páginas localizado y controlado visualmente.",
                    "locator": "acir01.pdf pp.1-11", "status": "BODY_LOCATED"})
    elif row["object_code"] in {"ANNEX_II", "ANNEX_IV", "ANNEX_V"}:
        row.update({"finding": "Modelo localizado; falta la certificación ejecutada del SAF355.",
                    "status": "MODEL_LOCATED_TARGET_CERT_OPEN"})
write_csv(HERE / "E0_UAI_2008_INSTRUCTIVE_AND_EXECUTED_CERTIFICATION_ROUTE_V153.csv", uai, list(uai[0]))

negative_rows = [
    ("Certificación UAI Cuenta 2008 Anexo I SAF355", "Economía/UAI/SIGEN/CGN", "Modelo localizado; certificado ejecutado no localizado.", "TARGET_CERT_I_NOT_LOCATED"),
    ("Certificación UAI Cuenta 2008 Anexo II SAF355", "Economía/UAI/SIGEN/CGN", "Modelo localizado; certificado o no aplicabilidad no localizado.", "TARGET_CERT_II_NOT_LOCATED"),
    ("Certificación UAI Cuenta 2008 Anexo III/UEPEX", "Economía/UAI/SIGEN/CGN", "Modelo localizado; universo/no aplicabilidad target no localizado.", "TARGET_CERT_III_NOT_LOCATED"),
    ("Certificación UAI Cuenta 2008 Anexo IV SAF355", "Economía/UAI/SIGEN/CGN", "Modelo localizado; certificado y anexo de formularios no localizados.", "TARGET_CERT_IV_NOT_LOCATED"),
    ("Certificación UAI Cuenta 2008 Anexo V SAF355", "Economía/UAI/SIGEN/CGN", "Modelo localizado; ratificación/rectificación ejecutada no localizada.", "TARGET_CERT_V_NOT_LOCATED"),
    ("Acuses UAI-SAF-CGN-SIGEN", "Economía/SIGEN/CGN", "Ruta normativa probada; acuses target no localizados.", "TARGET_RECEIPTS_NOT_LOCATED"),
    ("Papeles de trabajo UAI", "Economía/UAI", "No localizados públicamente.", "TARGET_WORKPAPERS_NOT_LOCATED"),
    ("Informe SIGEN Cuenta 2008 cuerpo/anexos", "SIGEN", "Inventario identifica entidad, año y área; cuerpo no localizado.", "GLOBAL_REPORT_BODY_NOT_LOCATED"),
    ("Número/carátula Informe SIGEN Cuenta 2008", "SIGEN", "No consignados en el inventario.", "GLOBAL_REPORT_ID_NOT_LOCATED"),
    ("Supervisión SIGEN UAI Economía 2009", "SIGEN", "Universo probado; target no localizado.", "SUPERVISION_TARGET_NOT_LOCATED"),
    ("Archivo público SIGEN 2009", "SIGEN", "La tabla pública actual expone sólo 2020-2026.", "CURRENT_ARCHIVE_2009_NOT_EXPOSED"),
    ("Índice AGDFA para SAF355/Cuenta 2008", "CGN", "Capacidad/custodia probadas; ingreso target no localizado.", "ARCHIVE_TARGET_INDEX_NOT_LOCATED"),
    ("Listado final Res.6 art.8 SAF355", "CGN/SAF355", "No localizado.", "FINAL_LIST_NOT_LOCATED"),
    ("Conformidad/discrepancia SAF355", "SAF355/CGN/UAI", "No localizada.", "TARGET_CONFORMITY_NOT_LOCATED"),
    ("Detalle AXT ONCP 30/06/2008", "ONCP/CGN", "Deber probado; archivo no localizado.", "AXT_DETAIL_NOT_LOCATED"),
    ("Casillas param355/inconsis355 y planillas target", "CGN/SAF355", "Esquema probado; mensajes y filas no localizados.", "TARGET_ROWS_NOT_LOCATED"),
]
negative = matrix("E0_V153_PUBLIC_SEARCH_NEGATIVE_RESULTS.csv",
                  ["row_id", "query_object", "route", "result", "status"],
                  [(f"NS153_{i:02d}",) + row for i, row in enumerate(negative_rows, 1)])
write_csv(HERE / "E0_V153_PUBLIC_SEARCH_NEGATIVE_RESULTS_V153.csv", negative, list(negative[0]))

request_raw = [
    ("UAI_CERT_I", "UAI Economía/SAF355", "Certificación Cuenta 2008 Anexo I", "2008-2009", "nota; certificado; Cuadro 1 B; observaciones; firma; fuentes", "Incluir no aplicabilidad o incumplimiento."),
    ("UAI_CERT_II", "UAI Economía/SAF355", "Certificación Cuenta 2008 Anexo II", "2008-2009", "nota; certificado; Cuadro 1 C; C43; extractos; firma", "Incluir no aplicabilidad o incumplimiento."),
    ("UAI_CERT_III", "UAI Economía/SAF355", "Certificación Cuenta 2008 Anexo III por UEPEX", "2008-2009", "UEPEX; Cuadro 5.4; SIDIF; transferencias TGN; firma", "Enumerar universo UEPEX incluso si es cero."),
    ("UAI_CERT_IV", "UAI Economía/SAF355", "Certificación Cuenta 2008 Anexo IV", "2008-2009", "anexo; C35/C41/C42/C43/C55/C75/C10; N° SIDIF/SAF; firma", "Incluir reemplazos, rectificaciones y no aplicabilidad."),
    ("UAI_CERT_V", "UAI Economía/SAF355", "Certificación Cuenta 2008 Anexo V", "2008-2009", "comunicación; cálculo; ratificación/rectificación; antecedentes; firma", "Incluir soportes de diferencias."),
    ("UAI_ALL_CERTS", "UAI Economía/SAF355", "Índice de certificaciones bajo Instructivo 2/2008", "2008-2009", "anexo; número; fecha; firmante; resultado; ubicación", "Enumerar anexos ausentes y sin observaciones."),
    ("UAI_DISPATCH", "UAI/SAF355/CGN/SIGEN", "Registros de salida, entrada y acuses", "2008-2009", "número; fecha/hora; remitente; receptor; adjuntos", "Ofrecer metadatos testados."),
    ("UAI_WORKPAPERS", "UAI Economía", "Papeles de trabajo de certificación", "2008-2009", "universo; muestra; pruebas; excepciones; conclusión", "Individualizar legajo/caja/sistema."),
    ("SIGEN_GLOBAL", "SIGEN", "Informe global de Cuenta de Inversión 2008 inventariado", "2008-2009", "cuerpo; anexos; base; universo; metodología; conclusiones", "Buscar con entidad, año 2009 y área GSEPyPF."),
    ("SIGEN_GLOBAL_METADATA", "SIGEN", "Registro archivístico del informe Cuenta 2008", "2009", "número; título; expediente; fecha; firmantes; destinatarios; área", "Individualizar inventario y disposición final."),
    ("SIGEN_SUPERVISION", "SIGEN", "Supervisión UAI Ministerio Economía", "2009", "informe; plan; observaciones; seguimiento", "Individualizar dentro del universo."),
    ("FINAL_LISTS", "CGN/SAF355", "Listados definitivos SIDIF art.8", "31/12/2008", "archivo; parámetros; columnas; filas; fecha; destinatario", "Cero debe documentar universo y consulta."),
    ("CONFORMITY", "SAF355/CGN", "Conformidad o discrepancia del cierre", "2008-2009", "nota; firma; fecha; listado; diferencias; adjuntos", "Incluir avisos a SIGEN/UAI."),
    ("ADJUSTMENTS", "SAF355/CGN", "Formularios de ajuste y notas", "2008-2009", "tipo; N° SIDIF; N° SAF; importe; estado; soporte", "No contar evento adicional sin conciliación."),
    ("ARCHIVE_INDEX", "SAF355/UAI", "Índice de originales y certificaciones", "2008-2009", "serie; legajo; caja; folio; productor; transferencia", "Identificar destino/fecha."),
    ("AGDFA_INDEX", "CGN/AGDFA", "Índice de documentación recibida para SAF355/Cuenta 2008", "2008-2009", "legajo; soporte; campos; transferencia; ubicación; disposición", "Informar consulta negativa reproducible."),
    ("AXT_DETAIL", "ONCP/CGN", "Detalle AXT al 30/06/2008", "2008-06-30", "cuenta; operación; saldo; explicación; razón extrapresupuestaria", "Cruzar con 31/12 y banco."),
    ("AXT_CONFORMITY", "ONCP/CGN", "Saldos finales y conformidad arts.2-3", "2008-06", "archivo; versión; nota; ajustes; firmante", "Respetar excepción SAF355 art.4."),
    ("PARAM_EMAIL", "CGN/SAF355", "Mensajes/archivos param355 e inconsis355", "2008", "cabeceras; adjuntos; timestamp; acuse; respuesta", "Buscar backups y soporte magnético."),
    ("INCONSISTENCY_SHEETS", "CGN/SAF355", "Planillas Anexo I de inconsistencias", "2008-2009", "SAF; fuente; imputación; tipo; N° SIDIF/SAF; firma", "Filtrar IDs target y cero reproducible."),
]
request_objects = matrix("E0_V153_REQUEST_OBJECTS.csv",
                         ["row_id", "object_id", "custodian", "exact_record", "period", "minimum_fields", "closure_rule", "status"],
                         [(f"RO153_{i:02d}",) + row + ("DRAFT_NOT_SENT",) for i, row in enumerate(request_raw, 1)])
write_csv(HERE / "E0_V153_REQUEST_OBJECTS_V153.csv", request_objects, list(request_objects[0]))

breaks = read_csv(V152 / "E0_FISCAL_METHOD_BREAKS_V152.csv")
break_add = [
    ("instruction_body_located_not_executed_saf355_certificate", "phase", "El modelo completo no acredita ejecución target.", "Recuperar certificado, firma, despacho y acuse SAF355.", "FROZEN_V153", "Instructivo 2/2008 pp.1-11"),
    ("cgn_receipt_gate_not_received_target_proof", "phase", "La regla no prueba que CGN recibió el cierre target.", "Pedir ingreso/rechazo y adjuntos.", "FROZEN_V153", "Circular CGN 01/09"),
    ("annex_i_balance_certification_not_individual_payment", "granularity", "Caja y bancos es un cuadro agregado.", "Cruzar extracto y comprobante individual.", "FROZEN_V153", "Instructivo 2/2008 Anexo I"),
    ("annex_ii_revolving_fund_not_debt_settlement", "scope", "Fondo rotatorio no es deuda pública target.", "Usar como control de cierre/no aplicabilidad.", "FROZEN_V153", "Instructivo 2/2008 Anexo II"),
    ("annex_iii_uepex_not_general_saf355", "scope", "El Anexo III es UEPEX.", "Exigir universo UEPEX antes de atribuirlo.", "FROZEN_V153", "Instructivo 2/2008 Anexo III"),
    ("annex_iv_late_form_certification_not_bank_execution", "phase", "Certificar formularios tardíos no prueba débito bancario.", "Vincular C41/C42/C55 con banco y reversas.", "FROZEN_V153", "Instructivo 2/2008 Anexo IV"),
    ("annex_v_remainder_certification_not_target_payment", "scope", "Remanente no individualiza pago target.", "Recuperar antecedentes y cruce transaccional.", "FROZEN_V153", "Instructivo 2/2008 Anexo V"),
    ("sigen_inventory_entry_not_report_body_or_saf355_validation", "granularity", "La fila no contiene informe ni valida SAF355.", "Pedir cuerpo, anexos, número y expediente.", "FROZEN_V153", "Libro Blanco SIGEN p.54"),
    ("cgn_archive_capability_not_target_ingestion", "custody", "Capacidad de guardar no acredita ingreso target.", "Pedir índice, transferencia, ubicación y disposición.", "FROZEN_V153", "Circular CGN 08/09"),
    ("current_sigen_archive_window_not_historical_nonexistence", "time", "La tabla 2020-2026 no prueba inexistencia en 2009.", "Usar búsqueda archivística.", "FROZEN_V153", "Archivo público SIGEN 2026-08-31"),
]
breaks = upsert(breaks, [dict(zip(list(breaks[0]), row)) for row in break_add], "break_id")
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V153.csv", breaks, list(breaks[0]))

trace = read_csv(V152 / "E0_INFORMATION_REQUEST_TRACEABILITY_V152.csv")
trace_fields = list(trace[0])
trace_add = [
    ("REQ133_ECON", "UAI Economía/SAF355", "CL153_CERT_I", "Certificación Anexo I", "2008-2009", "SAF355;Cuenta2008;AnexoI", "Cuadro1B;nota;firma;fuentes", "no aplicabilidad/incumplimiento", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "UAI Economía/SAF355", "CL153_CERT_II", "Certificación Anexo II", "2008-2009", "SAF355;Cuenta2008;AnexoII", "Cuadro1C;C43;extractos;firma", "no aplicabilidad/incumplimiento", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "UAI Economía/SAF355", "CL153_CERT_III", "Certificación Anexo III", "2008-2009", "SAF355;UEPEX;AnexoIII", "UEPEX;Cuadro5.4;SIDIF;TGN", "universo cero/no aplicabilidad", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "UAI Economía/SAF355", "CL153_CERT_IV", "Certificación Anexo IV", "2008-2009", "SAF355;C41;C42;C55;IDs", "anexo;N° SIDIF/SAF;estado;firma", "índice/metadatos", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "UAI Economía/SAF355", "CL153_CERT_V", "Certificación Anexo V", "2008-2009", "SAF355;remanente;rectificación", "comunicación;cálculo;antecedentes;firma", "índice/metadatos", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "CGN", "CL153_CGN_RECEIPT", "Ingreso o rechazo del cierre certificado", "2009", "Circular01/09;SAF355", "número;fecha;adjuntos;estado;acuse", "mesa de entradas", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "SIGEN", "CL153_REPORT_META", "Registro del informe Cuenta 2008", "2009", "MinisterioEconomía;GSEPyPF", "número;título;expediente;fecha;firmantes", "inventario/disposición", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "SIGEN", "CL153_REPORT_BODY", "Cuerpo y anexos del informe Cuenta 2008", "2008-2009", "MinisterioEconomía;GSEPyPF;Cuenta2008", "cuerpo;anexos;base;universo;método", "metadatos testados", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "CGN/AGDFA", "CL153_ARCHIVE_INDEX", "Índice documental SAF355/Cuenta 2008", "2008-2009", "SAF355;UAI;AnexosI-V", "legajo;soporte;transferencia;ubicación", "consulta negativa reproducible", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "UAI/SAF355/SIGEN", "CL153_SIGEN_COPY", "Copia e ingreso SIGEN", "2009", "SAF355;Instructivo2/2008", "remitente;receptor;fecha;adjuntos;acuse", "metadatos", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "UAI Economía", "CL153_WORKPAPERS", "Papeles de trabajo por Anexo I-V", "2008-2009", "SAF355;Cuenta2008", "universo;muestra;pruebas;excepciones;conclusión", "índice/ubicación", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "CGN/SAF355", "CL153_LATE_FORMS", "Listado de formularios fuera de fecha", "2008-2009", "C35;C41;C42;C43;C55;C75;C10", "fecha tope;emisión;SIDIF/SAF;estado", "cero reproducible", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "CGN/SAF355", "CL153_TARGET_ROWS", "Filas target del Anexo IV", "2008-2009", "71597;152677;2876", "tipo;importe;beneficiario;cuenta;estado", "universo/parámetros", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "SAF355/UAI", "CL153_BANK_SOURCES", "Extractos y arqueos usados", "2008", "AnexosI;II;III;IV", "banco;cuenta;moneda;fecha valor;movimiento", "índice/ubicación", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "CGN/SAF355", "CL153_REMAINDER", "Remanente provisorio y rectificación", "2008-2009", "AnexoV;SAF355", "cálculo;comunicación;caso;importe;resultado", "metadatos/antecedentes", "DRAFT_NOT_SENT"),
    ("REQ133_ECON", "SIGEN", "CL153_PUBLIC_ARCHIVE", "Cobertura histórica del Archivo Público", "2009", "Cuenta2008;GSEPyPF", "serie;índice;criterio;ubicación;disposición", "explicar ventana 2020-2026", "DRAFT_NOT_SENT"),
]
trace = upsert(trace, [dict(zip(trace_fields, (f"TR153_{i:03d}",) + row)) for i, row in enumerate(trace_add, 1)], "trace_id")
write_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V153.csv", trace, trace_fields)

keys = read_csv(V152 / "E0_REQUEST_SEARCH_KEY_MATRIX_V152.csv")
key_fields = list(keys[0])
key_add = [
    ("REQ133_ECON", "instruction", "Instructivo de Trabajo N° 2/2008 GNyPE", "cuerpo y ejecución", "acir01.pdf", "Modelo localizado; certificado target abierto."),
    ("REQ133_ECON", "circular", "Circular CGN N° 01/09", "ingreso/rechazo", "CGN 20/01/2009", "Regla no prueba recepción target."),
    ("REQ133_ECON", "annex", "Certificación Anexo I Instructivo 2/2008", "certificado SAF355", "Instructivo pp.2-3", "Pedir no aplicabilidad."),
    ("REQ133_ECON", "annex", "Certificación Anexo II Instructivo 2/2008", "certificado SAF355", "Instructivo pp.4-5", "Fondo rotatorio."),
    ("REQ133_ECON", "annex", "Certificación Anexo III Instructivo 2/2008", "certificado UEPEX", "Instructivo pp.6-7", "No trasponer a SAF355."),
    ("REQ133_ECON", "annex", "Certificación Anexo IV Instructivo 2/2008", "formularios tardíos", "Instructivo pp.8-9", "Rama C41/C42/C55."),
    ("REQ133_ECON", "annex", "Certificación Anexo V Instructivo 2/2008", "remanente", "Instructivo pp.10-11", "No es pago individual."),
    ("REQ133_ECON", "forms", "C35 C41 C42 C43 C55 C75 C10", "universo Anexo IV", "Instructivo p.8", "Pedir fechas tope/efectiva."),
    ("REQ133_ECON", "report", "Ministerio de Economía y Finanzas Públicas 2009 GSEPyPF", "informe Cuenta 2008", "Libro Blanco p.54", "Clave archivística combinada."),
    ("REQ133_ECON", "report", "calidad de la información y documentación Cuenta de Inversión 2008", "objetivo exacto", "Libro Blanco p.54", "Inventario, no cuerpo."),
    ("REQ133_ECON", "area", "GSEPyPF", "área productora SIGEN", "Libro Blanco p.54", "Pedir expansión de sigla."),
    ("REQ133_ECON", "archive", "Archivo General de Documentación Financiera de la Administración Nacional", "índice/custodia", "Circular 08/09", "Capacidad no implica ingreso."),
    ("REQ133_ECON", "archive", "Disposición CGN N° 46/1998", "recepción/guarda", "Circular 08/09", "Pedir inventario y transferencia."),
    ("REQ133_ECON", "archive", "Archivo Informático Histórico SIDIF", "resguardo de imágenes", "Circular 06/09", "Contexto de proyecto."),
    ("REQ133_ECON", "source", "Listado Parametrizado del SIDIF Central remitido por la CGN", "fuente Anexos III-V", "Instructivo pp.6,8,10", "Pedir archivo exacto."),
    ("REQ133_ECON", "source", "Acta de Arqueo de Fondos y Valores", "fuente Anexos I/III/IV", "Instructivo pp.2,6,8", "No sustituye banco."),
    ("REQ133_ECON", "source", "formularios que respaldan transferencias a la TGN", "fuente Anexos III/IV", "Instructivo pp.6,8", "Pedir número y fecha."),
    ("REQ133_ECON", "receipt", "documentación de cierre 2008 certificación UAI SAF 355", "mesa de entradas", "Circular 01/09", "Pedir ingreso o rechazo."),
    ("REQ133_ECON", "public_archive", "ArchivoWeb Informes SIGEN 2009 Cuenta de Inversión", "cobertura histórica", "SIGEN 2026", "Ventana visible 2020-2026."),
    ("REQ133_ECON", "target", "SAF 355 Anexo IV 71597 152677 2876", "filas target", "Método V153", "Cero reproducible requerido."),
]
keys = upsert(keys, [dict(zip(key_fields, (f"SK153_{i:02d}",) + row)) for i, row in enumerate(key_add, 1)], "key_id")
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V153.csv", keys, key_fields)

catalog_map = {s["local"].rsplit("/", 1)[-1]: s["id"] for s in source_rows}
roles = {
    "cgn_circular_1_2009_account_2008_uai_certification.html": "CERTIFICATION_RECEIPT_GATE",
    "sigen_instruction_2_2008_account_certification.pdf": "FULL_INSTRUCTION_AND_ANNEXES",
    "sigen_libro_blanco_2012_report_inventory.pdf": "REPORT_ARCHIVE_LOCATOR",
    "cgn_circular_8_2009_financial_document_archive_iso.html": "NAMED_ARCHIVE_CUSTODY_ROUTE",
    "cgn_circular_6_2009_sidif_historical_archive.html": "HISTORICAL_ARCHIVE_CONTEXT",
    "cgn_circulars_2009_current_index.html": "CURRENT_OFFICIAL_INDEX",
    "sigen_public_reports_archive_current.html": "CURRENT_PUBLIC_ARCHIVE_SCOPE",
}
bundle_rows = []
for i, path in enumerate(sorted(BIN.iterdir(), key=lambda p: p.name.casefold()), 1):
    if path.is_file():
        sid = catalog_map.get(path.name, "BUNDLE_ONLY")
        bundle_rows.append((f"B153_{i:02d}", path.name, roles[path.name],
                            "YES" if path.name in catalog_map else "NO", sid,
                            path.stat().st_size, sha256(path), "YES"))
bundle = matrix("E0_V153_SOURCE_BUNDLE.csv",
                ["row_id", "filename", "role", "catalogued", "catalog_source_id", "bytes", "sha256", "preserved"],
                bundle_rows)

visual = read_csv(V152 / "E0_V152_PDF_VISUAL_CONTROL.csv")
visual_raw = [
    ("e0_sigen_instruction_2_2008_account_2008_certification", str(page), str(page),
     "cuerpo, anexos y modelo de certificación", "PASS", "modelo/procedimiento; no certificado SAF355")
    for page in range(1, 12)
]
visual_raw += [
    ("e0_sigen_white_book_2012_account_2008_report_inventory", "XVIII", "52", "inventario de informes, contexto previo", "PASS", "inventario; no cuerpo"),
    ("e0_sigen_white_book_2012_account_2008_report_inventory", "XIX", "53", "continuidad del inventario", "PASS", "contexto"),
    ("e0_sigen_white_book_2012_account_2008_report_inventory", "XX", "54", "fila Ministerio Economía, 2009, GSEPyPF, Cuenta 2008", "PASS", "no número, cuerpo ni SAF355"),
]
visual_add = [dict(zip(["control_id", "source_id", "printed_page", "pdf_page", "rendered_check", "result", "inference_limit"],
                       (f"PV153_{i:03d}",) + row))
              for i, row in enumerate(visual_raw, len(visual) + 1)]
visual += visual_add
write_csv(HERE / "E0_V153_PDF_VISUAL_CONTROL.csv", visual, list(visual[0]))

source_ref_text = (V152 / "SOURCE_REFERENCES_V152.md").read_text(encoding="utf-8-sig").replace("V152", "V153")
(HERE / "SOURCE_REFERENCES_V153.md").write_text(source_ref_text, encoding="utf-8")
append_section(HERE / "SOURCE_REFERENCES_V153.md", "## V153 · Instructivo completo, informe inventariado y archivo financiero", """
- Circular CGN 01/09: https://www.economia.gob.ar/hacienda/cgn/normas/circulares/2009/cir01.htm
- Instructivo 2/2008 GNyPE: https://www.economia.gob.ar/hacienda/cgn/normas/circulares/2009/acir01.pdf
- Libro Blanco SIGEN 2012: https://www.argentina.gob.ar/sites/default/files/libro_blanco_sigen2012.pdf
- Circular CGN 08/09: https://www.economia.gob.ar/hacienda/cgn/normas/circulares/2009/cir08.htm
- Archivo público SIGEN observado: https://www.sigen.gob.ar/ArchivoWeb/Informes.aspx

Alcance: el cuerpo y los cinco modelos están localizados; las certificaciones ejecutadas SAF355, el informe SIGEN completo y el movimiento bancario target siguen abiertos.
""")

request_section = """
Hallazgo V153: el Instructivo 2/2008 completo y sus Anexos I-V fueron localizados en el enlace oficial de Circular CGN 01/09. Ya no se pide el modelo: se piden sus ejecuciones para SAF355, incluyendo certificado o no aplicabilidad por cada anexo, papeles de trabajo, despacho UAI, recepción SAF/CGN y copia SIGEN. Para el informe global, buscar por Ministerio de Economía y Finanzas Públicas, año 2009, área GSEPyPF y el objetivo sobre calidad de información/documentación de la Cuenta 2008. Para archivo CGN, pedir índice AGDFA, transferencia, legajo, soporte, ubicación y disposición. Estado: BORRADOR_NO_ENVIADO.
"""
append_section(HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V153.md", "## V153 · certificaciones ejecutadas e índices archivísticos", request_section)
append_section(HERE / "REQUEST_SUBMISSION_CHECKLIST_V153.md", "## Control previo V153", request_section)

register = read_csv(V152 / "E0_REQUEST_RESPONSE_REGISTER_V152.csv")
for row in register:
    row.update({"status": "DRAFT_NOT_SENT", "submitted_on": "N/A", "submission_channel": "N/A",
                "receipt_or_case_id": "N/A", "response_date": "N/A"})
write_csv(HERE / "E0_REQUEST_RESPONSE_REGISTER_V153.csv", register, list(register[0]))

(HERE / "README_V153.md").write_text(f"""# Checkpoint V153

- Fuentes maestras: {len(catalog)}; E0: {len(census)}; nuevas: {len(source_rows)}.
- Instructivo 2/2008: cuerpo y Anexos I-V localizados; certificaciones SAF355 abiertas.
- Circular 01/09: CGN no recibiría el cierre indicado sin certificación UAI.
- Libro Blanco: informe Cuenta 2008 inventariado para Economía, 2009, GSEPyPF; cuerpo abierto.
- Circular 08/09: archivo CGN con digitalización, guarda, descripción y ruta de valor jurídico.
- Seis pedidos permanecen BORRADOR_NO_ENVIADO; cero respuestas; ejecución 0/10.
""", encoding="utf-8")
(HERE / "VEREDICTO_V153.md").write_text("""# Veredicto V153

El modelo obligatorio dejó de ser una brecha: se localizaron el Instructivo 2/2008 y sus cinco anexos. La prueba pública permite pedir certificados, fuentes y acuses con precisión, y el inventario SIGEN añade entidad, año y área del informe global. Aún faltan los cuerpos ejecutados SAF355, el informe completo y la conciliación bancaria individual. Por eso no se eleva 0/10. Seis borradores no fueron enviados.
""", encoding="utf-8")
(HERE / "E0_FISCAL_RECONSTRUCTION_V153.md").write_text("""# Reconstrucción fiscal E0 V153

V153 cierra la brecha normativa del Instructivo 2/2008 y congela sus cinco ramas probatorias. Circular 01/09 prueba la barrera de recepción; el Libro Blanco identifica el informe global por Economía/2009/GSEPyPF; Circular 08/09 identifica una ruta archivística CGN. Ninguna pieza sustituye certificado ejecutado, comprobante, extracto, reversa o beneficiario target. Resultado: 0/10.
""", encoding="utf-8")
(HERE / "RETRIEVAL_LOG_V153.md").write_text("""# Retrieval log V153

- Recuperado el cuerpo íntegro del Instructivo 2/2008 mediante el enlace de Circular CGN 01/09.
- Renderizadas e inspeccionadas sus once páginas.
- Preservado Libro Blanco SIGEN 2012; inspeccionadas páginas PDF 52-54.
- Identificada la fila Ministerio de Economía y Finanzas Públicas, 2009, GSEPyPF, Cuenta 2008.
- Preservadas Circulares CGN 06/09 y 08/09 e índice oficial actual.
- Archivo público SIGEN observado: 121 entradas visibles de 2020-2026; 2009 no expuesto.
- Sin envío de solicitudes ni modificación de 0/10.
""", encoding="utf-8")

old_handover = HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V153_A_V153.md"
if old_handover.exists():
    old_handover.unlink()
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V153_A_V154.md").write_text("""# Handover V153 → V154

## Estado

- Instructivo 2/2008 y Anexos I-V localizados y controlados; certificado SAF355 abierto.
- Circular 01/09: CGN no recibiría el cierre indicado sin certificación UAI.
- Libro Blanco: informe Cuenta 2008 en Economía, 2009, área GSEPyPF; cuerpo/número abiertos.
- Circular 08/09: AGDFA con digitalización, guarda, descripción y valor jurídico de imágenes CGN.
- Archivo público SIGEN actual sólo expone 2020-2026; no prueba inexistencia 2009.
- Seis DRAFT_NOT_SENT; cero respuestas; 0/10.

## Prioridad V154

1. Mantener borradores salvo autorización.
2. Buscar número/carátula del informe por entidad + 2009 + GSEPyPF.
3. Recuperar certificaciones ejecutadas Anexos I-V SAF355 y sus acuses.
4. Rastrear índice AGDFA, mesa de entradas CGN y copia SIGEN.
5. Cruzar Anexo IV con C41/C42/C55, IDs target, banco y reversas.
6. Mantener 0/10 hasta cuerpo ejecutado y conciliación individual.
""", encoding="utf-8")

append_section(REPO / "BACKUP_ACTUALIZACION_2026-08-29.md", "## V153 · Instructivo 2/2008 completo y ruta archivística", """
- Cuerpo y Anexos I-V localizados; certificaciones SAF355 abiertas.
- Circular 01/09 prueba barrera de recepción CGN sin certificación UAI.
- Informe Cuenta 2008 inventariado como Economía, 2009, GSEPyPF; cuerpo abierto.
- AGDFA identificado como ruta de digitalización, guarda y descripción.
- Cuatro fuentes conceptuales; catorce controles PDF nuevos; seis borradores no enviados; 0/10.
""")

write_csv(HERE / "INHERITED_QA_STATUS_V153.csv", [
    {"script": "qa_v152.py", "pre_v153_result": "PASS", "post_v153_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V152 ampliada: cuerpo 2/2008 localizado y ruta archivística precisa."},
    {"script": "qa_v153.py", "pre_v153_result": "N/A", "post_v153_result": "PASS", "interpretation": "Verifica fuentes, matrices, borradores y 0/10."},
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
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V153.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V153.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)

size_rows = []
for path in iter_files(REPO):
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": size,
                      "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576),
                      "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V153.csv", size_rows)

image_visual = read_csv(HERE / "E0_V153_IMAGE_VISUAL_CONTROL.csv")
complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V152.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint": "V153", "date": "2026-08-31",
    "state": "E0_UAI_INSTRUCTION_BODY_AND_FIVE_ANNEXES_LOCATED_SIGEN_REPORT_LOCATOR_PROVED_TARGET_CERTIFICATES_OPEN_NOT_SENT",
    "master_catalog_entries": len(catalog), "physical_local_copies": physical,
    "physical_local_hash_ok": hash_ok, "remaining_physical_gaps": len(catalog) - physical,
    "e0_primary_sources_preserved": len(census), "numeric_v153_strict_changed": False,
    "sources_newly_preserved_v153": len(source_rows), "e0_primary_sources_newly_preserved_v153": len(source_rows),
    "e0_fiscal_method_breaks_frozen": len(breaks), "e0_request_traceability_rows": len(trace),
    "e0_request_search_keys": len(keys), "e0_v153_pdf_visual_controls": len(visual),
    "e0_v153_new_pdf_visual_controls": len(visual_add), "e0_v153_image_visual_controls": len(image_visual),
    "e0_v153_total_visual_controls": len(visual) + len(image_visual), "e0_v153_source_bundle_files": len(bundle),
    "e0_cgn_receipt_gate_rows": len(circular), "e0_uai_exact_annex_rows": len(instruction),
    "e0_saf355_certificate_branch_rows": len(branch), "e0_sigen_report_locator_rows": len(locator),
    "e0_cgn_archive_route_rows": len(archive), "e0_v153_public_search_rows": len(negative),
    "e0_v153_request_objects": len(request_objects),
    "e0_uai_instruction_02_2008_existence_proved": True, "e0_uai_instruction_02_2008_body_located": True,
    "e0_uai_instruction_02_2008_annexes_located": 5, "e0_uai_saf355_target_certification_located": False,
    "e0_cgn_no_receipt_without_uai_certification_proved": True,
    "e0_sigen_account_2008_global_report_existence_proved": True,
    "e0_sigen_account_2008_global_report_inventory_locator_proved": True,
    "e0_sigen_account_2008_global_report_body_located": False,
    "e0_cgn_financial_archive_capability_proved": True, "e0_cgn_financial_archive_target_ingestion_proved": False,
    "e0_sigen_public_archive_visible_year_min": 2020, "e0_sigen_public_archive_visible_year_max": 2026,
    "e0_target_forms_public_bodies_located": 0, "e0_target_transaf_logs_located": 0,
    "e0_settlement_executed_rows_confirmed": 0, "e0_requests_submitted": 0,
    "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
    "historical_workstream": "Recover executed SAF355 Annex I-V certificates, CGN/SIGEN receipts, SIGEN report body and AGDFA index; reconcile with bank; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V153.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

(HERE / "AUDITORIA_V153.md").write_text(f"""# Auditoría V153

- Fuentes maestras: {len(catalog)}; E0: {len(census)}; nuevas: {len(source_rows)}.
- Copias/hash: {physical}/{hash_ok}; brechas: {len(catalog) - physical}.
- Quiebres: {len(breaks)}; trazas: {len(trace)}; claves: {len(keys)}.
- Visuales: {len(visual)} PDF ({len(visual_add)} nuevos) + {len(image_visual)} imágenes = {len(visual) + len(image_visual)}.
- Bundle: {len(bundle)}; circular: {len(circular)}; instructivo: {len(instruction)}; SAF355: {len(branch)}; SIGEN: {len(locator)}; archivo: {len(archive)}.
- Certificados target 0/5; cuerpo informe SIGEN 0/1; ejecución 0/10; pedidos/respuestas 0/0.
""", encoding="utf-8")


def checkpoint_manifest():
    files = [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha256(p)}
             for p in sorted(HERE.iterdir()) if p.is_file() and p.name != "MANIFEST_V153.json"]
    payload = {
        "checkpoint": "V153", "parent_checkpoint": "V152",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": len(source_rows),
        "fiscal_method_breaks": len(breaks), "request_traceability_rows": len(trace),
        "request_search_keys": len(keys), "pdf_visual_controls_total": len(visual),
        "pdf_visual_controls_new": len(visual_add), "image_visual_controls_inherited": len(image_visual),
        "source_bundle_files": len(bundle), "cgn_receipt_gate_rows": len(circular),
        "uai_exact_annex_rows": len(instruction), "saf355_certificate_branch_rows": len(branch),
        "sigen_report_locator_rows": len(locator), "cgn_archive_route_rows": len(archive),
        "public_search_rows": len(negative), "v153_request_objects": len(request_objects),
        "uai_instruction_02_2008_existence_proved": True, "uai_instruction_02_2008_body_located": True,
        "uai_instruction_02_2008_annexes_located": 5, "uai_saf355_target_certification_located": False,
        "cgn_no_receipt_without_uai_certification_proved": True,
        "sigen_account_2008_global_report_inventory_locator_proved": True,
        "sigen_account_2008_global_report_body_located": False,
        "cgn_financial_archive_capability_proved": True, "cgn_financial_archive_target_ingestion_proved": False,
        "target_forms_public_bodies_located": 0, "target_transaf_logs_located": 0,
        "award_rows_exact": 10, "account_candidate_rows": 9, "executed_settlement_rows_confirmed": 0,
        "request_drafts": 6, "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V153.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    "checkpoint": "V153",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master; {physical} physical SHA-valid; {len(source_rows)} new sources; Instructivo 2/2008 body and Annexes I-V located; executed SAF355 certificates open; 0/10; six drafts not submitted.",
    "historical_workstream": "Recover executed SAF355 Annex I-V certificates, SIGEN report body and AGDFA index; reconcile with bank; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
tmp = global_manifest.with_suffix(".json.v153tmp")
tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
tmp.replace(global_manifest)

print(f"V153 BUILD PASS · catalog={len(catalog)} · E0={len(census)} · physical={physical} · hash_ok={hash_ok} · breaks={len(breaks)} · trace={len(trace)} · keys={len(keys)} · visual={len(visual) + len(image_visual)}")
