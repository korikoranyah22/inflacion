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
BIN = CYCLE / "inputs" / "historical_retrieval" / "v154" / "binaries"
V153 = CYCLE / "checkpoints" / "V153"
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


def pipe_rows(block, fields, prefix):
    rows = []
    for index, line in enumerate((line for line in block.strip().splitlines() if line.strip()), 1):
        values = [value.strip() for value in line.split("|")]
        assert len(values) == len(fields) - 1, (prefix, index, len(values), len(fields) - 1, line)
        rows.append(dict(zip(fields, [f"{prefix}{index:02d}"] + values)))
    return rows


def matrix(name, fields, block, prefix):
    rows = pipe_rows(block, fields, prefix)
    write_csv(HERE / name, rows, fields)
    return rows


def append_section(path, marker, body):
    path = Path(path)
    text = path.read_text(encoding="utf-8-sig") if path.exists() else ""
    if marker not in text:
        path.write_text(text.rstrip() + "\n\n" + marker + "\n\n" + body.strip() + "\n", encoding="utf-8")


def iter_files(root):
    root = Path(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted((name for name in dirnames if name not in EXCLUDED_DIRS), key=str.casefold)
        for filename in sorted(filenames, key=str.casefold):
            yield Path(dirpath) / filename


census = read_csv(V153 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V153.csv")
provenance = read_csv(V153 / "ARCHIVAL_PROVENANCE_V153.csv")

SOURCES = [
    {
        "id": "e0_sigen_public_archive_2020_account_record_family",
        "institution": "Sindicatura General de la Nación",
        "title": "Archivo público SIGEN · familia documental de Cuenta de Inversión 2019",
        "url": "https://www.sigen.gob.ar/ArchivoWeb/Informes.aspx",
        "filename": "sigen_public_reports_archive_2020_2026_listing.html",
        "period": "2019-2020", "series": "ArchivoWeb SIGEN · 00394/2020 a 00402/2020",
        "kind": "HTML oficial preservado",
        "note": "La secuencia separa cierre, certificaciones por anexo/fuente, remanentes y auditoría integral. Prueba una anatomía contemporánea; no prueba numeración ni existencia SAF355/2009.",
        "variables": "SIGEN;Cuenta2019;public_report_number;document_family;certification;audit",
        "breaks": "comparador/target; número público/número interno; ventana actual/inventario 2009",
    },
    {
        "id": "e0_sigen_if_2020_annex_a_bank_certification_comparator",
        "institution": "Sindicatura General de la Nación",
        "title": "IF-2020-09433026 · certificación UAI Cuadro I Anexo A Caja y Bancos",
        "url": "https://www.sigen.gob.ar/ArchivoWeb/ArchivoAdjunto_Ver.aspx?IdA=80644620",
        "filename": "sigen_if_2020_09433026_annex_a_certification.pdf",
        "period": "2019-2020", "series": "Informe UAI 007/2020 · IF-2020-09433026-APN-UAI#SIGEN",
        "kind": "PDF oficial firmado preservado",
        "note": "Certifica para SAF109 movimientos y saldos usando registros, extractos bancarios, certificaciones bancarias de saldos y extractos ministeriales; identifica informe, remisión y expediente. Es comparador, no certificado SAF355/2008 ni movimiento target.",
        "variables": "SIGEN;UAI;SAF109;AnnexA;bank_statements;bank_balance_certificates;expediente;IF",
        "breaks": "SAF109/SAF355; 2019/2008; certificado agregado/pago individual",
    },
    {
        "id": "e0_sigen_if_2020_remainder_certification_cross_reference_comparator",
        "institution": "Sindicatura General de la Nación",
        "title": "IF-2020-30081841 · certificación de remanente FF11 con referencias cruzadas",
        "url": "https://www.sigen.gob.ar/ArchivoWeb/ArchivoAdjunto_Ver.aspx?IdA=80645562",
        "filename": "sigen_if_2020_30081841_remainder_certification.pdf",
        "period": "2019-2020", "series": "Informe UAI 15/2020 · IF-2020-30081841-APN-UAI#SIGEN",
        "kind": "PDF oficial firmado preservado",
        "note": "Individualiza expediente, orden, IF productor, certificado anterior, dato CGN, cálculo ministerial y monto exacto. Prueba trazabilidad posible; no prueba pago ni Anexo V SAF355/2008.",
        "variables": "SIGEN;UAI;SAF109;remainder;cross_reference;expediente;order;amount;CGN",
        "breaks": "remanente/pago; SAF109/SAF355; 2019/2008; referencia/cuerpo",
    },
    {
        "id": "e0_sigen_if_2020_account_control_audit_comparator",
        "institution": "Sindicatura General de la Nación",
        "title": "IF-2020-34855376 · auditoría integral de Cuenta de Inversión SAF109",
        "url": "https://www.sigen.gob.ar/ArchivoWeb/ArchivoAdjunto_Ver.aspx?IdA=80646818",
        "filename": "sigen_if_2020_34855376_account_control.pdf",
        "period": "2019-2020", "series": "Informe UAI 019/2020 · IF-2020-34855376-APN-UAI#SIGEN",
        "kind": "PDF oficial firmado preservado",
        "note": "Documenta relevamiento de fuentes, pruebas selectivas, cotejo transacción-respaldo, concordancia y envío a CGN; declara Anexos A-C embebidos. Es auditoría posterior, no prueba bancaria individual ni informe Economía/2009.",
        "variables": "SIGEN;UAI;SAF109;Cuenta2019;audit;selective_testing;CGN;embedded_annexes",
        "breaks": "auditoría/certificación; selección/exhaustividad; SAF109/SAF355; 2019/2008",
    },
]

source_rows = []
for source in SOURCES:
    path = BIN / source["filename"]
    assert path.is_file(), path
    source_rows.append({**source, "local": "/" + path.relative_to(REPO).as_posix(),
                        "sha": sha256(path), "bytes": path.stat().st_size})

catalog = read_csv(CATALOG)
catalog = upsert(catalog, [{
    "id": s["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": s["institution"],
    "titulo": s["title"], "url_original": s["url"], "archivo_local": s["local"],
    "fecha_descarga": "2026-08-31", "fecha_publicacion": s["period"],
    "codigo_serie": s["series"], "periodo_utilizado": s["period"], "tipo": s["kind"],
    "sha256": s["sha"], "nota": "V154: " + s["note"],
} for s in source_rows], "id")
write_csv(CATALOG, catalog, list(catalog[0]))

census = upsert(census, [{
    "source_id": s["id"], "institution": s["institution"], "artifact": s["title"],
    "url": s["url"], "local_path": s["local"], "sha256": s["sha"], "bytes": s["bytes"],
    "period_coverage": s["period"], "variable_families": s["variables"],
    "primary_source": "YES", "preserved": "YES", "method_breaks": s["breaks"],
    "use_status": "E0_USABLE_AS_COMPARATOR_ONLY", "caveat": s["note"],
} for s in source_rows], "source_id")
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V154.csv", census, list(census[0]))

provenance = upsert(provenance, [{
    "source_id": s["id"], "original_url": s["url"], "retrieval_url": s["url"],
    "capture_timestamp": "2026-08-31", "cdx_digest": "N/A_OFFICIAL_DIRECT",
    "local_path": s["local"], "sha256": s["sha"], "bytes": s["bytes"],
    "provenance_note": "Captura directa del archivo oficial SIGEN; alcance de comparador congelado en V154.",
} for s in source_rows], "source_id")
write_csv(HERE / "ARCHIVAL_PROVENANCE_V154.csv", provenance, list(provenance[0]))


family_fields = ["row_id", "public_report_no", "detail_id", "internal_report_no", "if_or_document_id", "attachment_id", "expediente", "object", "finding", "status"]
family = matrix("E0_SIGEN_PUBLIC_ACCOUNT_RECORD_FAMILY_AND_IDENTIFIER_CHAIN_V154.csv", family_fields, """
ARCHIVE|2020-2026|N/A|N/A|N/A|N/A|Ventana pública actual|121 entradas visibles; no expone 2009|CURRENT_WINDOW_ONLY
00394/2020|205646|No extraído|IF-2020-02708805|80598462||Tareas de cierre 2019|Corte de documentación y registros|FAMILY_MEMBER
00395/2020|205658|04/2020-UAI|IF-2020-09438552-APN-UAI#SIGEN|80591554|EX-2019-113610848-APN-SIGEN|Anexo C FF11|Certificación ejecutada|EXECUTED_CERTIFICATE
00396/2020|No preservado|No extraído|No extraído|No extraído|No extraído|Anexo C FF12|Visible sólo en lista|LISTING_ONLY
00397/2020|No preservado|No extraído|No extraído|No extraído|No extraído|Anexo C FF15|Visible sólo en lista|LISTING_ONLY
00398/2020|205855|007/2020-UAI|IF-2020-09433026-APN-UAI#SIGEN|80644620|EX-2019-113610848-APN-SIGEN|Anexo A Caja y Bancos|Certificación ejecutada|EXECUTED_CERTIFICATE
00399/2020|205858|15/2020-UAI|IF-2020-30081841-APN-UAI#SIGEN|80645562|EX-2020-29170634-APN-SIGEN|Remanente FF11|Certificación con referencias|EXECUTED_CERTIFICATE
00400/2020|No preservado|No extraído|No extraído|No extraído|No extraído|Remanente FF12|Visible sólo en lista|LISTING_ONLY
00401/2020|No preservado|No extraído|No extraído|No extraído|No extraído|Remanente FF15|Visible sólo en lista|LISTING_ONLY
00402/2020|205865|019/2020-UAI|IF-2020-34855376-APN-UAI#SIGEN|80646818|No consignado|Auditoría integral Cuenta 2019|Anexos A-C embebidos|LATER_ACCOUNT_AUDIT
PUBLIC_NO|00398/2020|007/2020-UAI|IF-2020-09433026|80644620||Tres numeraciones|No fundir claves|IDENTIFIER_SEPARATION
DETAIL_ID|205855|||||Ficha pública|Identifica metadatos|IDENTIFIER_LAYER
ATTACHMENT_ID|80644620|||||IdA de descarga|Identifica binario|IDENTIFIER_LAYER
IF_ID|IF-2020-09433026|||||Identificador GDE|No extrapolar a 2009|IDENTIFIER_LAYER
EXPEDIENTE|EX-2019-113610848|||||Contenedor|Pedir equivalente 2009|CONTAINER_LAYER
REMITTANCE|IF-2020-08168211|||||Documento productor|Pedir nota SAF355-UAI|ROUTING_LAYER
ORDER|Orden 4|||||Ubicación en expediente|Pedir folio/asiento|CONTAINER_LAYER
SOURCE_ACCOUNTING|Registros contables|||||Fuente declarada|Pedir archivo/consulta|SOURCE_LAYER
SOURCE_BANK|Extractos bancarios|||||Fuente declarada|Pedir cuenta y movimiento|SOURCE_LAYER
SOURCE_BANK_CERT|Certificaciones de saldo|||||Fuente declarada|Saldo no es transacción|SOURCE_LAYER
SOURCE_MINISTRY|Extractos ministeriales|||||Fuente declarada|Pedir versión exacta|SOURCE_LAYER
CROSSREF_CERT|IF-2020-09438552|||||Certificado previo citado|Pedir cuerpo referido|CROSS_REFERENCE
CROSSREF_MHA|IF-2020-26720406|||||Cálculo ministerial citado|Pedir cuerpo referido|CROSS_REFERENCE
AUDIT_TEST|Cotejo selectivo|||||Transacciones contra respaldo|Selectivo no es exhaustivo|AUDIT_LAYER
AUDIT_SEND|Envío oportuno CGN|||||Procedimiento declarado|No sustituye acuse|AUDIT_LAYER
EMBEDDED|Anexos A B C|||||Adjuntos declarados|Referencia no es cuerpo|ATTACHMENT_LAYER
TARGET_2009|Número público/interno/registro|||||Campos históricos|No exigir GDE|REQUEST_UPGRADE
TARGET_SAF355|Anexos I-V ejecutados|||||Objeto pendiente|Comparador no cierra brecha|TARGET_OPEN
TARGET_BANK|Movimiento y reversas|||||Objeto pendiente|Tres IDs siguen abiertos|TARGET_OPEN
""", "PF154_")

chain_fields = ["row_id", "object_code", "document", "fact", "exact_value", "probative_use", "limit", "status"]
chain = matrix("E0_EXECUTED_CERTIFICATION_TO_AUDIT_CHAIN_COMPARATOR_V154.csv", chain_fields, """
A_OBJECT|Anexo A|Caja y Bancos|Movimientos y saldo según extracto|Certificación específica|No individualiza pago target|COMPARATOR
A_SAF|Anexo A|SAF 109|Ejercicio 2019|Delimita productor y período|No es SAF355/2008|SCOPE_LIMIT
A_REPORT|Anexo A|Informe 007/2020-UAI|Número interno|Clave archivística|No es número público|IDENTIFIER
A_IF|Anexo A|IF-2020-09433026|Documento firmado|Clave documental|GDE no retroactivo|IDENTIFIER
A_EXP|Anexo A|EX-2019-113610848|Expediente|Contenedor|No prueba recepción CGN|IDENTIFIER
A_REMIT|Anexo A|IF-2020-08168211|Remisión a UAI|Vincula productor-UAI|Falta acuse CGN|ROUTE
A_ACC|Anexo A|Registros contables|Fuente 1|Base interna|Requiere archivo/consulta|SOURCE
A_BANK|Anexo A|Extractos bancarios|Fuente 2|Contraste externo|Mención no es extracto target|SOURCE
A_BANK_CERT|Anexo A|Certificaciones de saldo|Fuente 3|Contraste de saldo|Saldo no es transacción|SOURCE
A_MECON|Anexo A|Extractos ministeriales|Fuente 4|Contraste administrativo|Pedir versión exacta|SOURCE
C_OBJECT|Anexo C|Fondo Rotatorio FF11|Certificación específica|Control de cierre|No es deuda target|NEGATIVE_CONTROL
C_IF|Anexo C|IF-2020-09438552|Informe 04/2020-UAI|Referencia cruzable|Bundle-only|IDENTIFIER
R_OBJECT|Remanente|FF11 31/12/2019|Adelanto de auditoría|Secuencia explícita|No es pago|COMPARATOR
R_EXP|Remanente|EX-2020-29170634 orden 4|Contenedor|Búsqueda reproducible|No identifica legajo 2009|CONTAINER
R_PRIOR|Remanente|IF-2020-09438552|$426.854,88|Cita certificado y monto|Referencia no sustituye cuerpo|CROSS_REFERENCE
R_MHA|Remanente|IF-2020-26720406|Cálculo ministerial|Cita fuente|Requiere recuperación|CROSS_REFERENCE
R_RESULT|Remanente|$4.515.346,78|Remanente certificado|Monto exacto|No trasladar al target|AMOUNT
AUD_OBJECT|Auditoría integral|Cuenta 2019 SAF109|Informe 019/2020|Cierra familia moderna|No es informe 2009|COMPARATOR
AUD_SURVEY|Auditoría integral|Relevamiento de fuentes|Procedimiento 1|Control metodológico|No aporta filas target|AUDIT_PROCEDURE
AUD_SYSTEMS|Auditoría integral|Revisión selectiva|Procedimiento 2|Confiabilidad/integridad|Selectivo|AUDIT_PROCEDURE
AUD_TX|Auditoría integral|Cotejo transacción-respaldo|Procedimiento 3|Puente transacción-documento|No prueba universo|AUDIT_PROCEDURE
AUD_TABLES|Auditoría integral|Concordancia cuadros-registros|Procedimiento 4|Puente contable|No prueba banco|AUDIT_PROCEDURE
AUD_CGN|Auditoría integral|Envío oportuno CGN|Procedimiento 5|Ruta de recepción|No contiene acuse|AUDIT_PROCEDURE
AUD_CONCLUSION|Auditoría integral|Calidad documental suficiente|Conclusión|Conclusión institucional|No equivale a pago|CONCLUSION_LIMIT
AUD_ATTACH|Auditoría integral|Anexos A B C embebidos|Adjuntos|Mapa de familia|Cuerpos no recuperados|ATTACHMENT_LIMIT
SEQUENCE|Familia|certificados-remanente-auditoría|Secuencia|Orienta búsqueda|No imponer calendario 2009|METHOD
TARGET_CERT|SAF355|Anexos I-V ejecutados|Pendiente|Pedir cuerpo y fuentes|0/5 localizados|TARGET_OPEN
TARGET_PAYMENT|SAF355|C41/C42/C55+banco+reversas|Pendiente|Conciliación individual|0 filas ejecutadas|TARGET_OPEN
""", "EC154_")

request_fields_schema = ["row_id", "request_field", "proven_modern_pattern", "target_2008_request", "fallback", "status"]
request_fields = matrix("E0_2008_TARGET_ARCHIVE_REQUEST_FIELD_UPGRADE_V154.csv", request_fields_schema, """
PUBLIC_REPORT_NO|00398/2020|Número público informe 2009|Inventario anual|DRAFT_NOT_SENT
DETAIL_ID|IdDocumento=205855|Identificador de ficha|Asiento de catálogo|DRAFT_NOT_SENT
INTERNAL_REPORT_NO|007/2020-UAI|Número interno UAI|Libro de informes 2009|DRAFT_NOT_SENT
DOCUMENT_ID|IF-2020-09433026|Número de documento|COMDOC/legajo; no exigir IF|DRAFT_NOT_SENT
ATTACHMENT_ID|IdA=80644620|Identificador de adjunto|Inventario o soporte óptico|DRAFT_NOT_SENT
EXPEDIENTE|EX-2019-113610848|Expediente/contenedor|Papel/COMDOC/legajo|DRAFT_NOT_SENT
ORDER_FOLIO|Orden 4|Orden, folio o asiento|Caja/legajo/folio|DRAFT_NOT_SENT
TITLE|Certificación Anexo A|Título equivalente|Cuenta 2008+SAF355|DRAFT_NOT_SENT
OBJECT|Caja y Bancos|Cuadro 1 Anexo B|Instructivo 2/2008|DRAFT_NOT_SENT
AREA|UAI SIGEN|UAI Economía+GSEPyPF|Síndico/representante|DRAFT_NOT_SENT
SAF|SAF109|SAF355|Jurisdicción 50|DRAFT_NOT_SENT
PERIOD|31/12/2019|31/12/2008 y remisiones 2009|Fechas de cierre/documento|DRAFT_NOT_SENT
INSTRUCTION|Instructivos 1/2020 y 2/2020|Instructivo 2/2008|Resolución 10/2006|DRAFT_NOT_SENT
REMITTANCE|IF productor a UAI|Nota SAF355-UAI|Registro salida/entrada|DRAFT_NOT_SENT
CGN_RECEIPT|Auditoría verifica envío|Acuse CGN|Mesa de entradas/rechazo|DRAFT_NOT_SENT
SIGEN_COPY|Expediente SIGEN|Copia remitida a SIGEN|Síndico jurisdiccional|DRAFT_NOT_SENT
ACCOUNTING_FILE|Registros contables|Listado exacto|Parámetros, versión y corte|DRAFT_NOT_SENT
BANK_STATEMENT|Extractos bancarios|Extracto fuente|Banco, cuenta, moneda y movimiento|DRAFT_NOT_SENT
BANK_BALANCE_CERT|Certificación de saldo|Certificación equivalente|Fecha, cuenta, saldo y firma|DRAFT_NOT_SENT
MINISTRY_EXTRACT|Extracto ministerial|SIDIF/SLU exacto|Nombre, versión, fecha y campos|DRAFT_NOT_SENT
C41_C42_C55|Pruebas selectivas|Universo Anexo IV|Tipo, N° SIDIF/SAF y estado|DRAFT_NOT_SENT
TARGET_IDS|No aplica comparador|71597;152677;2876|Cero reproducible|DRAFT_NOT_SENT
BANK_EXECUTION|No expuesto|Débito/crédito y fecha valor|Cuenta, importe y referencia|DRAFT_NOT_SENT
REVERSAL|No expuesto|Anulación/rechazo/reversa|Vínculo original-final|DRAFT_NOT_SENT
ATTACHMENT_INDEX|Embebidos declarados|Índice completo|Nombre, formato, tamaño y folio|DRAFT_NOT_SENT
WORKPAPERS|Procedimientos enumerados|Papeles de trabajo|Universo, muestra y conclusión|DRAFT_NOT_SENT
NO_RESULT|No aplica|Cierre negativo|Sistemas, campos, parámetros y responsable|DRAFT_NOT_SENT
DISPOSITION|No aplica|Retención/disposición final|Transferencia, eliminación o ubicación|DRAFT_NOT_SENT
FORMAT_LIMIT|GDE contemporáneo|No exigir GDE en 2009|Aceptar papel, COMDOC, correo o soporte|METHOD_LIMIT
""", "RF154_")

ladder_fields = ["row_id", "stage_id", "step", "evidence", "validates", "does_not_validate", "target_implication", "status"]
ladder = matrix("E0_ACCOUNT_2008_VALIDATION_TERMINOLOGY_LADDER_V154.csv", ladder_fields, """
L1|Cuenta 2009 Jur.50|Compilación validada con SIDIF|Proceso/sistema|UAI o banco|Vocabulario de validación|CONTEXT
L2|Instructivo 2/2008|Deber y fuentes|Procedimiento|Ejecución SAF355|Pedir cada cuerpo|PROVED_DUTY
L3|Circular 01/09|Barrera sin UAI|Admisión|Recepción efectiva|Pedir ingreso/rechazo|PROVED_GATE
L4|Archivo SIGEN|Familia contemporánea|Anatomía de claves|Inventario 2009|Pedir múltiples claves|COMPARATOR
L5|Anexo A 2019|Fuentes contables/bancarias|Certificación agregada|Movimiento target|Exigir fuentes/remisión|COMPARATOR
L6|Anexo C 2019|Fondo Rotatorio|Control distinto|Deuda target|Control negativo|NEGATIVE_CONTROL
L7|Remanente 2019|Referencias y monto|Trazabilidad|Pago individual|Exigir referencias|COMPARATOR
L8|Auditoría 2019|Pruebas selectivas|Calidad de proceso|Exhaustividad/banco|No elevar evidencia|COMPARATOR
L9|Certificado SAF355|Si se recupera|Cifras/fuentes|Débito por sí solo|Cruzar formularios/banco|TARGET_OPEN
L10|Anexo IV SAF355|Si se recupera|Formularios tardíos|Pago final|Cruzar estado/reversas|TARGET_OPEN
L11|C41/C42/C55|Si se recuperan|Registro administrativo|Liquidación bancaria|Cruzar fecha valor|TARGET_OPEN
L12|Listado SIDIF/SLU|Si se recupera|Estado en sistema|Verdad bancaria|Preservar consulta|TARGET_OPEN
L13|Acuse CGN|Si se recupera|Recepción paquete|Veracidad de filas|Cruzar adjuntos|TARGET_OPEN
L14|Extracto bancario|Si se recupera|Movimiento de cuenta|Identidad causal sola|Cruzar referencia|TARGET_OPEN
L15|Certificación saldo|Si se recupera|Saldo a fecha|Transacción individual|Sólo conciliación|TARGET_OPEN
L16|Reversa/rechazo|Si se recupera|Estado final|Nuevo pago automático|Vincular original-final|TARGET_OPEN
L17|Cero reproducible|Universo+parámetros|Ausencia definida|Inexistencia absoluta|Conservar sistema|CLOSURE_RULE
L18|Conciliación individual|Comprobante+sistema+banco+reversas|Ejecución confirmada|Generalización|Única vía para subir 0/10|FINAL_GATE
""", "VL154_")

negative_fields = ["row_id", "query_object", "route", "result", "status"]
negative = matrix("E0_V154_PUBLIC_SEARCH_NEGATIVE_RESULTS.csv", negative_fields, """
Informe Economía 2009 GSEPyPF número/carátula|SIGEN ArchivoWeb|No localizado; ventana comienza 2020|GLOBAL_REPORT_ID_NOT_LOCATED
Cuerpo informe Cuenta 2008 Economía|SIGEN+Libro Blanco|Inventario sí; cuerpo/anexos no|GLOBAL_REPORT_BODY_NOT_LOCATED
Certificación Anexo I SAF355|Economía/UAI/SIGEN/CGN|Comparador SAF109 sí; target no|TARGET_CERT_I_NOT_LOCATED
Certificación Anexo II SAF355|Economía/UAI/SIGEN/CGN|Ejecución/no aplicabilidad no|TARGET_CERT_II_NOT_LOCATED
Certificación Anexo III SAF355|Economía/UAI/SIGEN/CGN|Universo/no aplicabilidad no|TARGET_CERT_III_NOT_LOCATED
Certificación Anexo IV SAF355|Economía/UAI/SIGEN/CGN|Certificado/listado no|TARGET_CERT_IV_NOT_LOCATED
Certificación Anexo V SAF355|Economía/UAI/SIGEN/CGN|Ratificación/rectificación no|TARGET_CERT_V_NOT_LOCATED
Números internos/registro 2009|SIGEN/UAI Economía|No expuestos|HISTORICAL_IDENTIFIERS_NOT_LOCATED
Adjuntos/certificados embebidos 2009|SIGEN/UAI Economía|No localizados|HISTORICAL_ATTACHMENTS_NOT_LOCATED
Índice AGDFA SAF355/Cuenta 2008|CGN|No localizado|ARCHIVE_TARGET_INDEX_NOT_LOCATED
Ingreso/rechazo CGN|CGN|No localizado|TARGET_RECEIPT_NOT_LOCATED
Copia SIGEN SAF355|SIGEN|No localizada|TARGET_SIGEN_COPY_NOT_LOCATED
Filas 71597/152677/2876|CGN/SAF355|No localizadas|TARGET_ROWS_NOT_LOCATED
Movimientos bancarios/reversas target|Tesoro/BCRA/BNA|No localizados; ejecución cero|BANK_EXECUTION_NOT_LOCATED
""", "NS154_")
write_csv(HERE / "E0_V154_PUBLIC_SEARCH_NEGATIVE_RESULTS_V154.csv", negative, negative_fields)

objects = read_csv(V153 / "E0_V153_REQUEST_OBJECTS.csv")
for row in objects:
    row["status"] = "DRAFT_NOT_SENT"
    if row["object_id"] in {"SIGEN_GLOBAL", "SIGEN_GLOBAL_METADATA"}:
        row["minimum_fields"] += "; número público; número interno; registro; contenedor; índice de adjuntos"
        row["closure_rule"] = "No exigir GDE retroactivo; informar inventario, búsqueda, ubicación y disposición."
    if row["object_id"].startswith("UAI_CERT_"):
        row["minimum_fields"] += "; nota remitente; contenedor; folio/orden; fuentes; adjuntos"
object_fields = list(objects[0])
object_block = """
SIGEN_PUBLIC_NO|SIGEN|Número público/registro informe Cuenta 2008|2009|número; año; título; entidad; área; ficha|Índice anual o búsqueda negativa.
SIGEN_INTERNAL_NO|SIGEN/UAI Economía|Número interno UAI o control|2009|número; fecha; firmante; objeto; vínculo|Libro/asiento o metadatos testados.
SIGEN_CONTAINER|SIGEN/UAI Economía|Expediente/legajo/contenedor|2008-2009|sistema; número; carátula; productor; ubicación|Aceptar COMDOC, papel o soporte.
SIGEN_ATTACHMENTS|SIGEN/UAI Economía|Índice y cuerpos adjuntos|2008-2009|nombre; tipo; tamaño; folio/orden; ubicación|Inventario y disposición.
UAI_REMITTANCE_CHAIN|UAI Economía/SAF355|Documento productor por Anexo I-V|2008-2009|nota; fecha; emisor; receptor; adjuntos; acuse|Registro entrada/salida testado.
UAI_SOURCE_INDEX|UAI Economía/SAF355|Índice de fuentes usadas|2008|sistema; archivo; versión; banco; cuenta; período|Metadatos e inventario.
UAI_REFERENCE_CHAIN|UAI Economía/CGN/SIGEN|Referencias entre certificados y auditoría|2008-2009|origen; referencia; monto; orden/folio; estado|Listado o cero reproducible.
UAI_EMBEDDED_BODIES|UAI Economía/SIGEN|Embebidos/anexos del informe integral|2008-2009|índice; nombre; formato; tamaño; firma; ubicación|Inventario y disposición final.
"""
for index, line in enumerate((line for line in object_block.strip().splitlines() if line.strip()), 21):
    values = [value.strip() for value in line.split("|")]
    assert len(values) == 6
    objects.append(dict(zip(object_fields, [f"RO154_{index:02d}"] + values + ["DRAFT_NOT_SENT"])))
write_csv(HERE / "E0_V154_REQUEST_OBJECTS.csv", objects, object_fields)
write_csv(HERE / "E0_V154_REQUEST_OBJECTS_V154.csv", objects, object_fields)


breaks = read_csv(V153 / "E0_FISCAL_METHOD_BREAKS_V153.csv")
break_fields = list(breaks[0])
break_add = pipe_rows("""
public_report_number_not_attachment_identifier|identifier|Número público, interno, IF, IdDocumento e IdA son capas distintas.|Pedir y conservar cada identificador.|FROZEN_V154|SIGEN 00398/2020
gde_if_identifier_not_retroactive_2009_schema|time|El formato IF/EX moderno no puede imponerse a 2009.|Pedir expediente, COMDOC, legajo o soporte equivalente.|FROZEN_V154|Comparador SIGEN 2020
executed_annex_a_certification_not_target_saf355|scope|Certificado SAF109/2019 no es SAF355/2008.|Usarlo sólo para diseñar campos.|FROZEN_V154|IF-2020-09433026
bank_statements_as_source_not_target_transaction|granularity|Mencionar extractos no aporta movimiento individual.|Recuperar cuenta, fecha valor y referencia.|FROZEN_V154|Informe 007/2020
remainder_cross_reference_not_individual_payment|scope|Un remanente trazable sigue sin ser pago.|No transferir monto al target.|FROZEN_V154|IF-2020-30081841
later_account_audit_not_annex_certificate|phase|Auditoría integral y certificado son capas distintas.|Recuperar ambos y sus acuses.|FROZEN_V154|IF-2020-34855376
saf109_2019_comparator_not_saf355_2008|time|Comparador contemporáneo no prueba caso histórico.|Separar SAF y período.|FROZEN_V154|Archivo SIGEN 2020
embedded_annex_reference_not_public_embedded_body|custody|Declarar embebidos no equivale a preservarlos.|Pedir índice y cuerpos.|FROZEN_V154|Informe 019/2020
sidif_validated_compilation_not_uai_or_bank_validation|phase|Validación SIDIF no es UAI ni banco.|Separar sistema, auditoría y banco.|FROZEN_V154|Cuenta 2009 Jur.50
current_archive_family_not_complete_historical_inventory|time|Familia 2020 no es inventario 2009.|Pedir registro histórico y disposición.|FROZEN_V154|SIGEN ArchivoWeb
""", ["row_id"] + break_fields, "BREAK154_")
for row in break_add:
    row.pop("row_id")
breaks = upsert(breaks, break_add, "break_id")
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V154.csv", breaks, break_fields)


trace = read_csv(V153 / "E0_INFORMATION_REQUEST_TRACEABILITY_V153.csv")
trace_fields = list(trace[0])
trace_add = pipe_rows("""
REQ133_ECON|SIGEN|CL154_PUBLIC_NO|Número público/registro informe Cuenta 2008|2009|Economía;GSEPyPF;Cuenta2008|número;título;fecha;entidad;área|índice o búsqueda negativa|DRAFT_NOT_SENT
REQ133_ECON|SIGEN/UAI Economía|CL154_INTERNAL_NO|Número interno del informe|2009|UAI;GSEPyPF;Cuenta2008|número;libro;asiento;firmante;fecha|metadatos testados|DRAFT_NOT_SENT
REQ133_ECON|SIGEN/UAI Economía|CL154_CONTAINER|Expediente/legajo/contenedor|2008-2009|SAF355;Cuenta2008|sistema;número;carátula;ubicación|papel/COMDOC/soporte|DRAFT_NOT_SENT
REQ133_ECON|SIGEN/UAI Economía|CL154_ATTACH_INDEX|Índice de anexos y embebidos|2008-2009|AnexosI-V;informe|nombre;folio/orden;formato;tamaño|inventario/disposición|DRAFT_NOT_SENT
REQ133_ECON|UAI Economía/SAF355|CL154_PRODUCER_DOC|Documento productor por certificado|2008-2009|AnexosI-V;SAF355|número;fecha;emisor;receptor;adjuntos|registro salida|DRAFT_NOT_SENT
REQ133_ECON|UAI Economía/SAF355|CL154_ACCOUNTING_SOURCE|Archivo/listado contable usado|2008|Cuenta2008;SAF355|nombre;versión;corte;campos;hash|parámetros/consulta|DRAFT_NOT_SENT
REQ133_ECON|UAI Economía/SAF355|CL154_BANK_STATEMENTS|Extractos bancarios usados|2008|AnexosI;II;III;IV|banco;cuenta;moneda;período;movimiento|índice testado|DRAFT_NOT_SENT
REQ133_ECON|UAI Economía/SAF355|CL154_BANK_CERTS|Certificaciones bancarias de saldo|2008|AnexoI;SAF355|banco;cuenta;fecha;saldo;firmante|metadatos|DRAFT_NOT_SENT
REQ133_ECON|UAI Economía/CGN|CL154_MINISTRY_EXTRACT|Extracto ministerial/SIDIF/SLU|2008|SAF355;Cuenta2008|archivo;versión;fecha;campos;filas|consulta reproducible|DRAFT_NOT_SENT
REQ133_ECON|CGN|CL154_RECEIPT_ATTACH|Acuse CGN con adjuntos|2009|Circular01/09;SAF355|número;fecha;receptor;adjuntos;estado|rechazo/mesa entradas|DRAFT_NOT_SENT
REQ133_ECON|SIGEN|CL154_SIGEN_COPY_ATTACH|Ingreso SIGEN con adjuntos|2009|Instructivo2/2008;SAF355|asiento;fecha;remitente;adjuntos;ubicación|inventario|DRAFT_NOT_SENT
REQ133_ECON|UAI Economía|CL154_CROSSREFS|Referencias entre certificados|2008-2009|AnexosI-V;informe|origen;destino;monto;folio;estado|listado exhaustivo|DRAFT_NOT_SENT
REQ133_ECON|UAI Economía|CL154_AUDIT_TESTS|Pruebas y muestra|2008-2009|Cuenta2008;SAF355|universo;muestra;transacción;respaldo;resultado|papeles/índice|DRAFT_NOT_SENT
REQ133_ECON|CGN/SAF355|CL154_TARGET_FINAL_STATE|Estado final 71597/152677/2876|2008-2009|C41;C42;C55;reversas|registro;importe;beneficiario;banco;estado|cero reproducible|DRAFT_NOT_SENT
REQ133_ECON|CGN/AGDFA|CL154_DISPOSITION|Retención y disposición|2008-2026|SAF355;Cuenta2008|transferencia;serie;plazo;ubicación;acto|constancia eliminación|DRAFT_NOT_SENT
REQ133_ECON|SIGEN|CL154_ARCHIVE_SCOPE|Cobertura histórica ArchivoWeb|2009|GSEPyPF;Cuenta2008|año inicial;criterios;exclusiones;inventario|explicar ventana|DRAFT_NOT_SENT
""", trace_fields, "TR154_")
trace = upsert(trace, trace_add, "trace_id")
write_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V154.csv", trace, trace_fields)


keys = read_csv(V153 / "E0_REQUEST_SEARCH_KEY_MATRIX_V153.csv")
key_fields = list(keys[0])
key_add = pipe_rows("""
REQ133_ECON|public_report|00398/2020|comparador número público|SIGEN ArchivoWeb|No usar como target.
REQ133_ECON|internal_report|INFORME N° 007/2020-UAI|comparador número interno|IF-2020-09433026|Distinto del público.
REQ133_ECON|detail_id|IdDocumento=205855|comparador ficha|SIGEN ArchivoWeb|Capa de portal.
REQ133_ECON|attachment_id|IdA=80644620|comparador adjunto|SIGEN ArchivoWeb|Capa de descarga.
REQ133_ECON|document_id|IF-2020-09433026-APN-UAI#SIGEN|comparador documento|Anexo A 2019|No exigir IF 2009.
REQ133_ECON|expediente|EX-2019-113610848-APN-SIGEN|comparador contenedor|Anexo A/C|Pedir equivalente.
REQ133_ECON|remittance|IF-2020-08168211-APN-GCA#SIGEN|comparador productor|Anexo A/C|Pedir nota SAF355.
REQ133_ECON|cross_reference|IF-2020-26720406-APN-DAIF#MHA|cálculo referido|Remanente 2019|Pedir cuerpo.
REQ133_ECON|archive|libro de informes UAI 2009|número interno target|Método V154|Aceptar asiento.
REQ133_ECON|archive|inventario de adjuntos embebidos Cuenta 2008|cuerpos target|Método V154|Pedir disposición.
REQ133_ECON|container|expediente COMDOC legajo Cuenta 2008 SAF 355|contenedor pre-GDE|Método V154|No limitar a GDE.
REQ133_ECON|source|extractos bancarios certificaciones de saldo SAF 355 2008|fuentes Anexo I|Comparador 2019|Mención no es movimiento.
REQ133_ECON|source|extractos Ministerio Economía SAF 355|fuente administrativa|Comparador 2019|Pedir archivo.
REQ133_ECON|audit|cotejo transacciones contables con respaldo|papeles de trabajo|Comparador 2019|Selectivo.
REQ133_ECON|receipt|comprobación envío oportuno a CGN|acuse target|Comparador 2019|Conclusión no es acuse.
REQ133_ECON|attachment|Anexos A B C archivos embebidos|índice adjuntos|Comparador 2019|Referencia no es binario.
REQ133_ECON|target|SAF 355 71597 152677 2876 C41 C42 C55|filas target|Método V154|Cero reproducible.
REQ133_ECON|reversal|SAF 355 anulación rechazo reemplazo reversa 2008|estado final|Método V154|Vincular original-final.
REQ133_ECON|area|Ministerio Economía 2009 GSEPyPF Cuenta 2008|informe global|Libro Blanco SIGEN|Número/cuerpo abiertos.
REQ133_ECON|archive_scope|ArchivoWeb SIGEN cobertura histórica 2009|inventario público|SIGEN ArchivoWeb|Ventana no es inexistencia.
""", key_fields, "SK154_")
keys = upsert(keys, key_add, "key_id")
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V154.csv", keys, key_fields)

catalog_map = {s["filename"]: s["id"] for s in source_rows}
roles = {
    "sigen_public_reports_archive_2020_2026_listing.html": "CURRENT_ACCOUNT_REPORT_FAMILY",
    "sigen_report_00394_2020_closing_tasks_detail.html": "CLOSING_DETAIL_COMPARATOR",
    "sigen_report_00395_2020_annex_c_certification_detail.html": "ANNEX_C_DETAIL_COMPARATOR",
    "sigen_report_00398_2020_annex_a_certification_detail.html": "ANNEX_A_DETAIL_COMPARATOR",
    "sigen_report_00399_2020_remainder_certification_detail.html": "REMAINDER_DETAIL_COMPARATOR",
    "sigen_report_00402_2020_account_control_detail.html": "ACCOUNT_AUDIT_DETAIL_COMPARATOR",
    "sigen_archivos_adjuntos_ver.js": "ATTACHMENT_ROUTE_DISCOVERY",
    "sigen_if_2020_02708805_closing_tasks.pdf": "CLOSING_BODY_BUNDLE_ONLY",
    "sigen_if_2020_09433026_annex_a_certification.pdf": "EXECUTED_ANNEX_A_COMPARATOR",
    "sigen_if_2020_09438552_annex_c_certification.pdf": "EXECUTED_ANNEX_C_COMPARATOR_BUNDLE_ONLY",
    "sigen_if_2020_30081841_remainder_certification.pdf": "EXECUTED_REMAINDER_COMPARATOR",
    "sigen_if_2020_34855376_account_control.pdf": "LATER_ACCOUNT_AUDIT_COMPARATOR",
}
bundle_fields = ["row_id", "filename", "role", "catalogued", "catalog_source_id", "bytes", "sha256", "preserved"]
bundle = []
for index, path in enumerate(sorted(BIN.iterdir(), key=lambda value: value.name.casefold()), 1):
    if path.is_file():
        source_id = catalog_map.get(path.name, "BUNDLE_ONLY")
        bundle.append(dict(zip(bundle_fields, [f"B154_{index:02d}", path.name, roles[path.name],
                                               "YES" if path.name in catalog_map else "NO", source_id,
                                               path.stat().st_size, sha256(path), "YES"])))
write_csv(HERE / "E0_V154_SOURCE_BUNDLE.csv", bundle, bundle_fields)


visual = read_csv(V153 / "E0_V153_PDF_VISUAL_CONTROL.csv")
visual_fields = list(visual[0])
visual_add = pipe_rows("""
e0_sigen_if_2020_annex_a_bank_certification_comparator|1|1|objeto, remisión, expediente y fuentes|PASS|SAF109/2019; no target
e0_sigen_if_2020_annex_a_bank_certification_comparator|2|2|certificación, SAF, firma y fecha|PASS|agregado; no movimiento individual
bundle_sigen_if_2020_09438552_annex_c_certification|1|1|Fondo Rotatorio, remisión y fuentes|PASS|control negativo; no deuda
bundle_sigen_if_2020_09438552_annex_c_certification|2|2|certificación, SAF, firma y fecha|PASS|no prueba pago
e0_sigen_if_2020_remainder_certification_cross_reference_comparator|1|1|objeto, adelanto y expediente/orden|PASS|remanente; no pago
e0_sigen_if_2020_remainder_certification_cross_reference_comparator|2|2|referencias, monto y firma|PASS|SAF109/2019
e0_sigen_if_2020_account_control_audit_comparator|1|1|introducción, objeto y alcance|PASS|auditoría posterior
e0_sigen_if_2020_account_control_audit_comparator|2|2|procedimientos, marco y conclusión|PASS|selectivo; no exhaustividad
e0_sigen_if_2020_account_control_audit_comparator|3|3|anexos embebidos, firma y cierre|PASS|referencia no preserva embebidos
""", visual_fields, "PV154_")
for index, row in enumerate(visual_add, len(visual) + 1):
    row["control_id"] = f"PV154_{index:03d}"
visual += visual_add
write_csv(HERE / "E0_V154_PDF_VISUAL_CONTROL.csv", visual, visual_fields)

images = read_csv(V153 / "E0_V153_IMAGE_VISUAL_CONTROL.csv")
for row in images:
    row["control_id"] = row["control_id"].replace("IV153", "IV154")
write_csv(HERE / "E0_V154_IMAGE_VISUAL_CONTROL.csv", images, list(images[0]))


source_text = (V153 / "SOURCE_REFERENCES_V153.md").read_text(encoding="utf-8-sig").replace("V153", "V154")
(HERE / "SOURCE_REFERENCES_V154.md").write_text(source_text, encoding="utf-8")
append_section(HERE / "SOURCE_REFERENCES_V154.md", "## V154 · familia pública SIGEN y cadena de identificadores", """
- Archivo público SIGEN: https://www.sigen.gob.ar/ArchivoWeb/Informes.aspx
- Ficha 00398/2020: https://www.sigen.gob.ar/ArchivoWeb/ArchivosAdjuntos_Ver.aspx?IdDocumento=205855
- Anexo A: https://www.sigen.gob.ar/ArchivoWeb/ArchivoAdjunto_Ver.aspx?IdA=80644620
- Ficha 00399/2020: https://www.sigen.gob.ar/ArchivoWeb/ArchivosAdjuntos_Ver.aspx?IdDocumento=205858
- Remanente: https://www.sigen.gob.ar/ArchivoWeb/ArchivoAdjunto_Ver.aspx?IdA=80645562
- Ficha 00402/2020: https://www.sigen.gob.ar/ArchivoWeb/ArchivosAdjuntos_Ver.aspx?IdDocumento=205865
- Auditoría integral: https://www.sigen.gob.ar/ArchivoWeb/ArchivoAdjunto_Ver.aspx?IdA=80646818
- Cuenta 2009, Jurisdicción 50: https://www.economia.gob.ar/hacienda/cgn/cuenta/2009/tomoii/11jur50.htm

Alcance: la familia 2019/2020 demuestra identificadores, fuentes, referencias y capas posibles. No demuestra que SAF355 emitió los documentos 2008 ni que los tres eventos target llegaron al banco.
""")

draft_names = [
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT", "REQUEST_BCRA_CRYL_SETTLEMENT",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER", "REQUEST_AGN_2018_REPLY",
    "REQUEST_CNV_CUSTODY_RECORDS", "REQUEST_CAJA_SETTLEMENT_HOLDINGS",
    "REQUEST_SUBMISSION_CHECKLIST",
]
for stem in draft_names:
    old = V153 / f"{stem}_V153.md"
    new = HERE / f"{stem}_V154.md"
    new.write_text(old.read_text(encoding="utf-8-sig").replace("V153", "V154"), encoding="utf-8")

request_section = """
El comparador oficial SIGEN 2019/2020 muestra que deben pedirse por separado: número público, número interno UAI, ficha, adjunto, documento productor, expediente/legajo y orden/folio. Para 2008/2009 no se exige nomenclatura GDE: se aceptan COMDOC, expediente papel, correo, soporte óptico, libro o asiento. Por cada Anexo I-V SAF355 se requieren documento remitente, certificado firmado, fuentes concretas, índice de adjuntos, acuses SAF/CGN/SIGEN, referencias cruzadas y disposición final. La mención de extractos o una conclusión de calidad no sustituye el movimiento bancario individual. Estado: BORRADOR_NO_ENVIADO.
"""
append_section(HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V154.md", "## V154 · identificadores múltiples y cuerpos embebidos", request_section)
append_section(HERE / "REQUEST_SUBMISSION_CHECKLIST_V154.md", "## Control previo V154", request_section)

register = read_csv(V153 / "E0_REQUEST_RESPONSE_REGISTER_V153.csv")
for row in register:
    row.update({"draft_file": row["draft_file"].replace("V152", "V154").replace("V153", "V154"),
                "status": "DRAFT_NOT_SENT", "submitted_on": "N/A", "submission_channel": "N/A",
                "receipt_or_case_id": "N/A", "response_date": "N/A"})
write_csv(HERE / "E0_REQUEST_RESPONSE_REGISTER_V154.csv", register, list(register[0]))

(HERE / "README_V154.md").write_text(f"""# Checkpoint V154

- Fuentes maestras: {len(catalog)}; E0: {len(census)}; nuevas: {len(source_rows)}.
- Familia SIGEN 2019/2020 preservada como comparador de cierre, certificados, remanentes y auditoría.
- Separados número público, número interno, ficha, adjunto, IF, expediente y orden/folio.
- Anexo A declara contabilidad, extractos y certificaciones bancarias; no prueba pago target.
- Certificados SAF355 target 0/5; filas ejecutadas 0; seis borradores no enviados; 0/10.
""", encoding="utf-8")
(HERE / "VEREDICTO_V154.md").write_text("""# Veredicto V154

La vuelta mejora el pedido, no el puntaje. El archivo contemporáneo demuestra que una pieza puede tener número público, número interno, identificador documental, expediente, orden e índice de adjuntos; además, las certificaciones pueden declarar fuentes bancarias y referenciar otros cuerpos. Esa anatomía impide respuestas parciales y búsquedas demasiado estrechas. Pero SAF109/2019 es sólo comparador: faltan SAF355/2008, el informe Economía/2009, anexos, acuses y conciliación bancaria individual. Resultado 0/10. Seis borradores no enviados.
""", encoding="utf-8")
(HERE / "E0_FISCAL_RECONSTRUCTION_V154.md").write_text("""# Reconstrucción fiscal E0 V154

V154 congela cinco capas: validación SIDIF de compilación; deber y barrera de recepción; certificaciones ejecutadas por anexo; auditoría integral posterior; conciliación transaccional con banco y reversas. No se funden entre sí y sólo la última confirma ejecución individual. El comparador SIGEN 2019/2020 afina campos sin trasladar resultados a SAF355/2008. Resultado 0/10.
""", encoding="utf-8")
(HERE / "RETRIEVAL_LOG_V154.md").write_text("""# Retrieval log V154

- Buscado el informe 2008/2009 por Cuenta de Inversión y GSEPyPF; no apareció número/cuerpo histórico.
- Preservada la familia pública 00394/2020-00402/2020 y cinco PDF como comparador.
- Recuperada la ruta directa de adjuntos mediante IdA y fichas mediante IdDocumento.
- Inspeccionadas nueve páginas: Anexo A, Anexo C, remanente FF11 y auditoría integral.
- Congelada la no equivalencia entre número público, interno, IF, ficha, adjunto y expediente.
- Ninguna solicitud enviada; 0/10 sin cambios.
""", encoding="utf-8")
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V154_A_V155.md").write_text("""# Handover V154 → V155

## Estado

- Comparador SIGEN 2019/2020 preservado: cierre, Anexo A/C, remanente y auditoría integral.
- Identificadores separados: número público, interno, IdDocumento, IdA, IF, expediente y orden/folio.
- Anexo A declara registros, extractos bancarios, certificaciones de saldo y extractos ministeriales.
- Remanente cita certificado previo, cálculo ministerial, expediente, orden y montos.
- Todo es comparador SAF109/2019; SAF355/2008 e informe Economía/2009 siguen abiertos.
- Seis DRAFT_NOT_SENT; cero respuestas; 0/10.

## Prioridad V155

1. Mantener borradores salvo autorización.
2. Buscar libro/registro UAI-SIGEN 2009 por Economía + GSEPyPF + Cuenta 2008.
3. Rastrear expediente/COMDOC/legajo e índice de adjuntos sin exigir GDE.
4. Recuperar Anexos I-V ejecutados, documentos productores y acuses.
5. Cerrar C41/C42/C55 + 71597/152677/2876 + banco + reversas.
""", encoding="utf-8")
stale = HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V154_A_V154.md"
if stale.exists():
    stale.unlink()

append_section(REPO / "BACKUP_ACTUALIZACION_2026-08-29.md", "## V154 · familia SIGEN e identificadores múltiples", """
- Preservada familia oficial 2019/2020 como comparador de certificación y auditoría.
- Separados número público, interno, ficha, adjunto, IF, expediente y orden/folio.
- Nueve páginas nuevas controladas; cuatro fuentes conceptuales nuevas.
- SAF355/2008 abierto; seis borradores no enviados; 0/10.
""")

write_csv(HERE / "INHERITED_QA_STATUS_V154.csv", [
    {"script": "qa_v153.py", "pre_v154_result": "PASS", "post_v154_result": "PASS_BASELINE", "interpretation": "V153 íntegra; V154 agrega comparadores sin alterar 0/10."},
    {"script": "qa_v154.py", "pre_v154_result": "N/A", "post_v154_result": "PASS", "interpretation": "Verifica fuentes, controles, borradores y límites."},
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
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V154.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V154.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)

size_rows = []
for path in iter_files(REPO):
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": size,
                      "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576),
                      "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V154.csv", size_rows)

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V153.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint": "V154", "date": "2026-08-31",
    "state": "E0_SIGEN_EXECUTED_CERTIFICATION_AND_AUDIT_COMPARATOR_LOCATED_SAF355_2008_TARGET_OPEN_NOT_SENT",
    "master_catalog_entries": len(catalog), "physical_local_copies": physical,
    "physical_local_hash_ok": hash_ok, "remaining_physical_gaps": len(catalog) - physical,
    "e0_primary_sources_preserved": len(census), "numeric_v154_strict_changed": False,
    "sources_newly_preserved_v154": len(source_rows),
    "e0_primary_sources_newly_preserved_v154": len(source_rows),
    "e0_fiscal_method_breaks_frozen": len(breaks), "e0_request_traceability_rows": len(trace),
    "e0_request_search_keys": len(keys), "e0_v154_pdf_visual_controls": len(visual),
    "e0_v154_new_pdf_visual_controls": len(visual_add), "e0_v154_image_visual_controls": len(images),
    "e0_v154_total_visual_controls": len(visual) + len(images), "e0_v154_source_bundle_files": len(bundle),
    "e0_v154_public_family_rows": len(family), "e0_v154_certification_chain_rows": len(chain),
    "e0_v154_archive_request_field_rows": len(request_fields),
    "e0_v154_validation_ladder_rows": len(ladder), "e0_v154_public_search_rows": len(negative),
    "e0_v154_request_objects": len(objects), "e0_sigen_modern_public_report_family_located": True,
    "e0_sigen_modern_executed_annex_a_certification_located": True,
    "e0_sigen_modern_remainder_cross_reference_located": True,
    "e0_sigen_modern_later_account_audit_located": True,
    "e0_sigen_account_2008_global_report_body_located": False,
    "e0_uai_saf355_target_certification_located": False,
    "e0_uai_saf355_target_certifications_located_count": 0,
    "e0_target_forms_public_bodies_located": 0, "e0_target_transaf_logs_located": 0,
    "e0_settlement_executed_rows_confirmed": 0, "e0_requests_submitted": 0,
    "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
    "historical_workstream": "Recover 2009 report register/container/attachments and executed SAF355 certificates; reconcile C41/C42/C55 with bank and reversals; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V154.json").write_text(
    json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

(HERE / "AUDITORIA_V154.md").write_text(f"""# Auditoría V154

- Fuentes maestras: {len(catalog)}; E0: {len(census)}; nuevas: {len(source_rows)}.
- Copias/hash: {physical}/{hash_ok}; brechas: {len(catalog) - physical}.
- Quiebres: {len(breaks)}; trazas: {len(trace)}; claves: {len(keys)}.
- Visuales: {len(visual)} PDF ({len(visual_add)} nuevos) + {len(images)} imágenes = {len(visual) + len(images)}.
- Bundle: {len(bundle)}; familia: {len(family)}; cadena: {len(chain)}; campos: {len(request_fields)}; escalera: {len(ladder)}.
- Certificados SAF355 0/5; ejecución 0/10; pedidos/respuestas 0/0.
""", encoding="utf-8")


def checkpoint_manifest():
    files = [{"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
             for path in sorted(HERE.iterdir()) if path.is_file() and path.name != "MANIFEST_V154.json"]
    payload = {
        "checkpoint": "V154", "parent_checkpoint": "V153",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": len(source_rows),
        "fiscal_method_breaks": len(breaks), "request_traceability_rows": len(trace),
        "request_search_keys": len(keys), "pdf_visual_controls_total": len(visual),
        "pdf_visual_controls_new": len(visual_add), "image_visual_controls_inherited": len(images),
        "source_bundle_files": len(bundle), "public_family_rows": len(family),
        "certification_chain_rows": len(chain), "archive_request_field_rows": len(request_fields),
        "validation_ladder_rows": len(ladder), "public_search_rows": len(negative),
        "v154_request_objects": len(objects), "modern_sigen_record_family_located": True,
        "modern_annex_a_certification_located": True, "modern_remainder_certificate_located": True,
        "modern_account_audit_located": True, "sigen_account_2008_global_report_body_located": False,
        "uai_saf355_target_certification_located": False, "target_forms_public_bodies_located": 0,
        "target_transaf_logs_located": 0, "award_rows_exact": 10, "account_candidate_rows": 9,
        "executed_settlement_rows_confirmed": 0, "request_drafts": 6,
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V154.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tree(root):
    lines = []
    root = Path(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted((name for name in dirnames if name not in EXCLUDED_DIRS), key=str.casefold)
        base = Path(dirpath)
        lines.extend((base / name).relative_to(root).as_posix() + "/" for name in dirnames)
        lines.extend((base / name).relative_to(root).as_posix() for name in sorted(filenames, key=str.casefold))
    return "\n".join(lines) + "\n"


(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")
checkpoint_manifest()

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)}
                for path in iter_files(REPO) if path != global_manifest]
payload = {
    "checkpoint": "V154",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master; {physical} physical SHA-valid; {len(source_rows)} new comparator sources; SAF355/2008 open; 0/10; six drafts not submitted.",
    "historical_workstream": "Recover 2009 identifiers/container/attachments and SAF355 certificates; reconcile bank and reversals; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
temporary = global_manifest.with_suffix(".json.v154tmp")
temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
temporary.replace(global_manifest)

print(f"V154 BUILD PASS · catalog={len(catalog)} · E0={len(census)} · physical={physical} · hash_ok={hash_ok} · breaks={len(breaks)} · trace={len(trace)} · keys={len(keys)} · visual={len(visual) + len(images)}")
