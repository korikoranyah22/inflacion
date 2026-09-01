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
PARENT = CYCLE / "checkpoints" / "V173"
AUDIT = CYCLE / "source_audit"
SYNC = CYCLE / "inputs" / "source_sync" / "v174"
HIST_ROOT = CYCLE / "inputs" / "historical_retrieval" / "v174"
HIST = HIST_ROOT / "binaries"
QUERY = HIST_ROOT / "query_logs"
METHODS = HIST_ROOT / "methods"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"
COVERAGE = "63.4406041403540997520463142785031521252747951992299547614348265414453439585848248058817492708499966268585997481191265825"
NUMERATOR = "61345602.215"
ASSETS = "96697695.5"
EXCLUDED = {".git", "__pycache__", "tmp", "node_modules"}


FILES = {
    "auditors": HIST / "sigen_auditoresweb_note_2518_2009.html",
    "da235": HIST / "infoleg_da_235_2010_note_3059_2009.html",
    "da722": HIST / "infoleg_da_722_2010_note_4169_2009.html",
    "acta12": HIST / "eras_acta_12_2009_note_3832.pdf",
    "acta01": HIST / "eras_acta_01_2010_note_5095.pdf",
    "orden01": HIST / "eras_orden_dia_01_2010_note_5095.pdf",
    "cc": QUERY / "commoncrawl_health_control_2014_49_v174.csv",
    "scanner": METHODS / "commoncrawl_exact_prefix_scanner_v174.ps1",
}
EXPECTED = {
    FILES["auditors"]: (71266, "8e94c52627edb5e0d69b0dbd82c408c8546cac67f10af7850b952cfbc728151c"),
    FILES["da235"]: (40230, "dff04c4ca7289651e5a21a1ff586f1b46feadd685317f5404c442a68039cc8ad"),
    FILES["da722"]: (39536, "f02d8b5301d66934ffd64b5ea34f9a37824ac43f8861aada01ec07c1411c7cd8"),
    FILES["acta12"]: (98667, "8c800ce669b3bbe19ec8117df6da034029700d5274c88d6e60f9b93173db8788"),
    FILES["acta01"]: (82377, "0b7fa031e9f53a8b15dba32595969c9608428bf99ff1573c9c722c5cb11bcc21"),
    FILES["orden01"]: (61220, "1ecbd11564e1b6e197080135495ffeb4ceefc9e991c4f74241331e2156c118ae"),
}


def read_csv(path: Path | str):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path | str, rows, fields=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or (list(rows[0]) if rows else [])
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def sha(path: Path | str):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def iter_files(root: Path):
    for dp, dns, fns in os.walk(root):
        dns[:] = sorted((x for x in dns if x not in EXCLUDED), key=str.casefold)
        for fn in sorted(fns, key=str.casefold):
            yield Path(dp) / fn


def tree(root: Path):
    out = []
    for dp, dns, fns in os.walk(root):
        dns[:] = sorted((x for x in dns if x not in EXCLUDED), key=str.casefold)
        base = Path(dp)
        out += [(base / x).relative_to(root).as_posix() + "/" for x in dns]
        out += [(base / x).relative_to(root).as_posix() for x in sorted(fns, key=str.casefold)]
    return "\n".join(out) + "\n"


def clone_parent():
    skip = {
        "MANIFEST_V173.json", "README_V173.md", "VEREDICTO_V173.md", "AUDITORIA_V173.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V173_A_V174.md", "V173_SOURCE_BUNDLE.csv",
        "V173_PUBLIC_SEARCH_LOG.csv", "V173_PDF_VISUAL_CONTROL.csv",
        "V173_PDF_VISUAL_AND_TEXT_CONTROL.csv",
    }
    for src in sorted(PARENT.iterdir(), key=lambda p: p.name.casefold()):
        if not src.is_file() or src.name in skip or src.name.startswith(("build_", "qa_")):
            continue
        dst = HERE / src.name.replace("V173", "V174")
        dst.write_text(src.read_text(encoding="utf-8-sig").replace("V173", "V174"), encoding="utf-8")


HERE.mkdir(parents=True, exist_ok=True)
clone_parent()
for path, (size, digest) in EXPECTED.items():
    assert path.is_file() and path.stat().st_size == size and sha(path) == digest

cc = read_csv(FILES["cc"])
assert len(cc) == 2 and all(r["classification"] == "SERVICE_ERROR" for r in cc)

sources = [
    {
        "id": "e0_sigen_auditoresweb_note_2518_2009_dated_comparator_v174",
        "tema": "ciclo_ajuste_e0_fiscal", "institucion": "Sindicatura General de la Nación",
        "titulo": "Listado de auditores internos · Nota SIGEN 2518/2009 fechada 6/7/2009",
        "url_original": "https://www.sigen.gob.ar/AuditoresWeb/",
        "archivo_local": "/" + FILES["auditors"].relative_to(REPO).as_posix(),
        "fecha_descarga": "2026-09-01", "fecha_publicacion": "2009-07-06",
        "codigo_serie": "Nota SIGEN 2518/2009", "periodo_utilizado": "2009",
        "tipo": "HTML oficial preservado · comparador serial fechado", "sha256": EXPECTED[FILES["auditors"]][1],
        "nota": "V174: prueba que la numeración 2009 de Notas SIGEN se conserva públicamente con fecha en otra superficie institucional. Comparador; no fija por sí solo la fecha de 3672/09.",
    },
    {
        "id": "e0_infoleg_da235_note3059_2009_recital_v174",
        "tema": "ciclo_ajuste_e0_fiscal", "institucion": "Jefatura de Gabinete / Infoleg",
        "titulo": "Decisión Administrativa 235/2010 · recepción de Nota SIGEN 3059/09",
        "url_original": "https://www.argentina.gob.ar/normativa/nacional/norma-166842/texto",
        "archivo_local": "/" + FILES["da235"].relative_to(REPO).as_posix(),
        "fecha_descarga": "2026-09-01", "fecha_publicacion": "2010-05-04",
        "codigo_serie": "DA 235/2010 · Nota SIGEN 3059/09", "periodo_utilizado": "2009",
        "tipo": "HTML oficial completo preservado", "sha256": EXPECTED[FILES["da235"]][1],
        "nota": "V174: ubica 3059/09 en una secuencia receptora entre hechos de 13/8 y 3/9/2009; la posición narrativa no equivale a fecha exacta de emisión.",
    },
    {
        "id": "e0_infoleg_da722_note4169_2009_recital_v174",
        "tema": "ciclo_ajuste_e0_fiscal", "institucion": "Jefatura de Gabinete / Infoleg",
        "titulo": "Decisión Administrativa 722/2010 · recepción de Nota SIGEN 4169/09",
        "url_original": "https://www.argentina.gob.ar/normativa/nacional/decisi%C3%B3n_administrativa-722-2010-173404/texto",
        "archivo_local": "/" + FILES["da722"].relative_to(REPO).as_posix(),
        "fecha_descarga": "2026-09-01", "fecha_publicacion": "2010-10-13",
        "codigo_serie": "DA 722/2010 · Nota SIGEN 4169/09", "periodo_utilizado": "2009",
        "tipo": "HTML oficial completo preservado", "sha256": EXPECTED[FILES["da722"]][1],
        "nota": "V174: ubica 4169/09 entre un acto de apertura del 27/10 y un dictamen del 15/12/2009; comparador contextual, no fecha exacta.",
    },
    {
        "id": "e0_eras_acta12_2009_note3832_recipient_expte828_v174",
        "tema": "ciclo_ajuste_e0_fiscal", "institucion": "Ente Regulador de Agua y Saneamiento",
        "titulo": "Acta de Directorio ERAS 12/09 · Nota SIGEN 3832/2009-GSPF y Expediente 828-09",
        "url_original": "https://www.argentina.gob.ar/sites/default/files/contrataciones/2009/acta%201209.pdf",
        "archivo_local": "/" + FILES["acta12"].relative_to(REPO).as_posix(),
        "fecha_descarga": "2026-09-01", "fecha_publicacion": "2009-12-21",
        "codigo_serie": "Acta ERAS 12/09 · punto 5", "periodo_utilizado": "2009",
        "tipo": "PDF oficial preservado · control visual páginas 1-2", "sha256": EXPECTED[FILES["acta12"]][1],
        "nota": "V174: correlaciona número/área/asunto de Nota SIGEN con expediente receptor 828-09 y respuesta institucional. Comparador contemporáneo de doble identificador.",
    },
    {
        "id": "e0_eras_acta01_2010_note5095_recipient_expte878_v174",
        "tema": "ciclo_ajuste_e0_fiscal", "institucion": "Ente Regulador de Agua y Saneamiento",
        "titulo": "Acta de Directorio ERAS 1/10 · Nota SIGEN 5095/2009-GSPF y Expediente 878-09",
        "url_original": "https://www.argentina.gob.ar/sites/default/files/contrataciones/2010/acta%200110.pdf",
        "archivo_local": "/" + FILES["acta01"].relative_to(REPO).as_posix(),
        "fecha_descarga": "2026-09-01", "fecha_publicacion": "2010-01-29",
        "codigo_serie": "Acta ERAS 1/10 · punto 4", "periodo_utilizado": "2009-2010",
        "tipo": "PDF oficial preservado · control visual página 1", "sha256": EXPECTED[FILES["acta01"]][1],
        "nota": "V174: correlaciona Nota 5095/2009-GSPF, asunto, distribución interna, respuesta y expediente receptor 878-09.",
    },
    {
        "id": "e0_eras_order01_2010_note5095_recipient_expte878_v174",
        "tema": "ciclo_ajuste_e0_fiscal", "institucion": "Ente Regulador de Agua y Saneamiento",
        "titulo": "Orden del Día ERAS 29/1/2010 · Nota SIGEN 5095/2009-GSPF y Expediente 878-09",
        "url_original": "https://www.argentina.gob.ar/sites/default/files/ordendia0110.pdf",
        "archivo_local": "/" + FILES["orden01"].relative_to(REPO).as_posix(),
        "fecha_descarga": "2026-09-01", "fecha_publicacion": "2010-01-29",
        "codigo_serie": "Orden del Día ERAS 1/10 · punto 4", "periodo_utilizado": "2009-2010",
        "tipo": "PDF oficial preservado · control visual página 1", "sha256": EXPECTED[FILES["orden01"]][1],
        "nota": "V174: control independiente pre-deliberación del vínculo Nota 5095/2009-GSPF → expediente receptor 878-09.",
    },
]

catalog = read_csv(CATALOG)
catalog_fields = list(catalog[0])
by_id = {r["id"]: r for r in catalog}
for row in sources:
    by_id[row["id"]] = row
catalog = list(by_id.values())
write_csv(CATALOG, catalog, catalog_fields)
assert len(catalog) == 613

audit = []
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    actual = sha(path) if path.is_file() else ""
    audit.append({"id": row["id"], "archivo_local": row["archivo_local"], "exists": str(path.is_file()), "sha_catalog": row["sha256"].lower(), "sha_actual": actual, "hash_ok": str(path.is_file() and bool(row["sha256"]) and actual == row["sha256"].lower())})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V174.csv", audit)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V174.csv", audit)
missing = [r for r in audit if r["hash_ok"] != "True"]
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V174.csv", missing, list(audit[0]))
assert not missing

serial_rows = [
    {"row_id":"NS174_01","note":"2518/2009","area":"no consignada en la cita","date_or_envelope":"06/07/2009","recipient_record":"designación UAI conservada en AuditoresWeb","evidence_level":"EXACT_NOTE_AND_DATE","target_use":"comparador inferior fechado","limit":"otra materia; no prueba serie global"},
    {"row_id":"NS174_02","note":"3059/09","area":"no consignada","date_or_envelope":"posición narrativa entre 13/08/2009 y 03/09/2009","recipient_record":"Expediente PFA S02:0002320/2007","evidence_level":"CONTEXTUAL_RECITAL_ENVELOPE","target_use":"comparador numérico inferior cercano","limit":"orden del considerando no es fecha certificada"},
    {"row_id":"NS174_03","note":"3672/09","area":"GSEyP","date_or_envelope":"fecha exacta abierta; buscar todo 2009","recipient_record":"CGN/DAIF: identificador receptor abierto","evidence_level":"TARGET_REFERENCE_ONLY","target_use":"objeto principal","limit":"no fechar sólo por interpolación"},
    {"row_id":"NS174_04","note":"3832/2009","area":"GSPF","date_or_envelope":"recibida y tratada a más tardar 21/12/2009","recipient_record":"Expediente ERAS 828-09","evidence_level":"EXACT_NOTE_SUBJECT_RECIPIENT_FILE","target_use":"comparador superior y patrón de correlación","limit":"fecha de emisión no impresa"},
    {"row_id":"NS174_05","note":"4169/09","area":"no consignada","date_or_envelope":"posición narrativa entre 27/10/2009 y 15/12/2009","recipient_record":"Expediente PFA 843-01-000409/07","evidence_level":"CONTEXTUAL_RECITAL_ENVELOPE","target_use":"control superior adicional","limit":"no fecha exacta"},
    {"row_id":"NS174_06","note":"5095/2009","area":"GSPF","date_or_envelope":"en agenda y tratada 29/01/2010","recipient_record":"Expediente ERAS 878-09","evidence_level":"EXACT_NOTE_SUBJECT_RECIPIENT_FILE","target_use":"prueba de continuidad receptora","limit":"nota emitida en 2009; fecha exacta abierta"},
]
write_csv(HERE / "E0_SIGEN_2009_NOTE_SERIAL_DATE_ENVELOPE_V174.csv", serial_rows)

recipient_rows = [
    {"row_id":"RC174_01","sender_note":"3832/2009-GSPF","recipient":"ERAS","subject":"Informe de Evaluación del Sistema de Control Interno 2008 - ERAS - Junio 2009","recipient_identifier":"Expte. 828-09","recorded_actions":"informes internos; dictamen jurídico; respuesta a SIGEN con copia JGM","status":"COMPARATOR_PROVED"},
    {"row_id":"RC174_02","sender_note":"5095/2009-GSPF","recipient":"ERAS","subject":"Supervisión UAI ERAS - Plan enero-junio 2009","recipient_identifier":"Expte. 878-09","recorded_actions":"pases a áreas; retorno UAI; instrucción jurídica urgente","status":"COMPARATOR_PROVED"},
    {"row_id":"RC174_03","sender_note":"3672/09-GSEyP","recipient":"CGN según contexto; confirmar destinatario formal","subject":"respuesta a 0120/09 DAIF; seguimiento de hallazgos UEPEX/cierre 2008","recipient_identifier":"ABIERTO","recorded_actions":"alta SISIO e instrucciones referidas; metadatos y cuerpo abiertos","status":"TARGET_RECIPIENT_FILE_OPEN"},
]
write_csv(HERE / "E0_RECIPIENT_NOTE_TO_LOCAL_FILE_COMPARATORS_V174.csv", recipient_rows)

write_csv(HERE / "E0_ARCHIVEWEB_EXACT_SEARCH_CONTROL_V174.csv", [
    {"control_id":"AW174_01","date":"2026-09-01","surface":"ArchivoWeb/Buscador.aspx","filters":"Año=2009; Palabras clave=3672; tipo=(Todos); organismo vacío","visible_result":"Total de informes: 0","classification":"ZERO_WITHIN_PUBLIC_REPORT_UNIVERSE","evidentiary_effect":"no prueba ausencia de Nota 3672/09","next_step":"backend Archivo Digital/Secretaría General/Archivo General"},
])

write_csv(HERE / "E0_SIGEN_NOTE_SEARCH_WINDOW_V174.csv", [
    {"priority":"1","scope":"todo 2009","keys":"NOT; 3672; 03672; 3672/09; 3672/2009; GSEyP; 0120/09 DAIF","reason":"evita falsa precisión temporal","closure":"registro/cuerpo o negativo fundado por campos y sistemas"},
    {"priority":"2","scope":"serie 2500-4200/2009","keys":"exportación de libro/asientos de Notas y tabla de numeración","reason":"comparadores públicos 2518, 3059, 3832 y 4169","closure":"regla de numeración y fila 3672 con campos CIDD"},
    {"priority":"3","scope":"aproximación julio-diciembre 2009","keys":"fecha, destinatario CGN, asunto UEPEX/cierre 2008","reason":"ventana operativa inferida, no hecho probado","closure":"usar sólo como ayuda secundaria"},
])

write_csv(HERE / "V174_PDF_VISUAL_CONTROL.csv", [
    {"control_id":"PDF174_01","source_id":sources[3]["id"],"pdf_pages":"1-2","target":"fecha reunión; Nota 3832; asunto; Expte 828-09","result":"PASS_LEGIBLE_COMPLETE","limit":"no fecha de emisión"},
    {"control_id":"PDF174_02","source_id":sources[4]["id"],"pdf_pages":"1","target":"Nota 5095; asunto; Expte 878-09; actuaciones","result":"PASS_LEGIBLE_COMPLETE","limit":"comparador posterior"},
    {"control_id":"PDF174_03","source_id":sources[5]["id"],"pdf_pages":"1","target":"control de agenda Nota 5095 → Expte 878-09","result":"PASS_LEGIBLE_COMPLETE","limit":"comparador posterior"},
])

note_search = read_csv(HERE / "E0_NOTE_3672_ARCHIVAL_SEARCH_V174.csv")
note_search += [
    {"route_id":"N174_30","surface":"ArchivoWeb Informes","target":"Año 2009 + palabra 3672","result":"Total de informes: 0","status":"PUBLIC_REPORT_SEARCH_NEGATIVE_ONLY","required_record":"backend NOT/CIDD/SPD/caja"},
    {"route_id":"N174_31","surface":"ERAS actas públicas","target":"Notas SIGEN 3832 y 5095 de 2009","result":"correlación exacta con expedientes receptores 828-09 y 878-09","status":"RECIPIENT_FILE_PATTERN_PROVED","required_record":"aplicar patrón a CGN sin trasladar numeración"},
]
write_csv(HERE / "E0_NOTE_3672_ARCHIVAL_SEARCH_V174.csv", list({r["route_id"]: r for r in note_search}.values()))

dual = read_csv(HERE / "E0_NOTE_3672_DUAL_IDENTIFIER_ROUTE_V174.csv")
dual += [
    {"row_id":"DI174_20","year":"2009","sigen_note":"3832/2009-GSPF","recipient_record_system":"Expediente ERAS","recipient_record":"828-09","subject":"Evaluación SCI 2008 ERAS","source_location":"Acta ERAS 12/09 punto 5","analytic_use":"doble identificador + asunto + respuesta","target_limit":"comparador; no es CGN","status":"COMPARATOR_ONLY"},
    {"row_id":"DI174_21","year":"2009","sigen_note":"5095/2009-GSPF","recipient_record_system":"Expediente ERAS","recipient_record":"878-09","subject":"Supervisión UAI enero-junio 2009","source_location":"Orden/Acta ERAS 1/10 punto 4","analytic_use":"doble identificador + pases/acciones","target_limit":"comparador; no es CGN","status":"COMPARATOR_ONLY"},
]
write_csv(HERE / "E0_NOTE_3672_DUAL_IDENTIFIER_ROUTE_V174.csv", list({r["row_id"]: r for r in dual}.values()))

keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V174.csv")
new_keys = [
    {"key_id":"SK174_20","request_id":"REQ155_SIGEN","key_group":"annual_note_register","exact_key":"exportación 2009 tipo NOT, rango 2500-4200, con fila 3672","search_purpose":"resolver fecha y clave CIDD de 3672/09","source_or_basis":"comparadores 2518/3059/3832/4169","caveat":"rango auxiliar; buscar también todo 2009"},
    {"key_id":"SK174_21","request_id":"REQ155_SIGEN","key_group":"note_numbering_rules","exact_key":"regla de numeración anual de Notas SIGEN 2009; secuencia común o por área","search_purpose":"validar o descartar interpolación serial","source_or_basis":"comparadores multiárea","caveat":"no presumir monotonicidad global"},
    {"key_id":"SK174_22","request_id":"REQ133_ECON","key_group":"recipient_local_file","exact_key":"Nota SIGEN 3672/09-GSEyP ↔ expediente/actuación CGN 2009","search_purpose":"obtener identificador receptor","source_or_basis":"patrón ERAS 3832→828-09 y 5095→878-09","caveat":"no trasladar serie ERAS a CGN"},
    {"key_id":"SK174_23","request_id":"REQ133_ECON","key_group":"subject_search","exact_key":"0120/09 DAIF; UEPEX; cierre 2008; hallazgos SISIO; GSEyP","search_purpose":"hallar asiento cuando el número emisor no esté indexado","source_or_basis":"Cuenta 2009 + campos CIDD","caveat":"devolver coincidencias y criterios"},
    {"key_id":"SK174_24","request_id":"REQ155_SIGEN/REQ133_ECON","key_group":"search_window","exact_key":"todo 2009; secundariamente julio-diciembre 2009","search_purpose":"evitar negativo por ventana estrecha","source_or_basis":"cronología serial V174","caveat":"ventana secundaria es inferencia"},
    {"key_id":"SK174_25","request_id":"REQ155_SIGEN/REQ133_ECON","key_group":"negative_certificate","exact_key":"sistemas, tablas, serie, campos, variantes, período, acceso, transferencia/baja","search_purpose":"hacer auditable una respuesta negativa","source_or_basis":"Res.41/07 + comparadores receptores","caveat":"cero de ArchivoWeb no satisface cierre"},
]
keys = list({r["key_id"]: r for r in keys + new_keys}.values())
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V174.csv", keys)

objects = read_csv(HERE / "E0_V174_REQUEST_OBJECTS.csv")
new_objects = [
    {"row_id":"RO174_20","object_id":"SIGEN_2009_NOT_REGISTER_EXPORT","custodian":"SIGEN · Secretaría General/Mesa/TI","exact_record":"libro/exportación de Notas SIGEN 2009, tipo NOT, incluida fila 3672","period":"2009","minimum_fields":"número; fecha/hora; área; emisor; firmante; destinatario; asunto; expediente/oficio; CIDD; acceso; archivo; caja","closure_rule":"exportación íntegra o certificación de esquema/rango y resultado","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO174_21","object_id":"SIGEN_2009_NOTE_NUMBERING_RULE","custodian":"SIGEN · Secretaría General/Mesa","exact_record":"regla y serie de numeración de Notas SIGEN 2009","period":"2009","minimum_fields":"serie; alcance; reinicio; áreas; anuladas; reservadas; saltos; prefijos; sistemas","closure_rule":"norma/diccionario o explicación técnica firmada","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO174_22","object_id":"CGN_3672_RECIPIENT_FILE_CROSSWALK","custodian":"CGN · Mesa/DAIF/Archivo","exact_record":"vínculo Nota SIGEN 3672/09 ↔ expediente/actuación/asiento receptor","period":"2009-2010","minimum_fields":"entrada; fecha; remitente; destinatario; asunto; expediente; pases; adjuntos; respuesta; archivo","closure_rule":"crosswalk documental o negativo fundado por cada sistema/serie","status":"DRAFT_NOT_SENT"},
]
objects = list({r["row_id"]: r for r in objects + new_objects}.values())
write_csv(HERE / "E0_V174_REQUEST_OBJECTS.csv", objects)
write_csv(HERE / "E0_V174_REQUEST_OBJECTS_V174.csv", objects)

addendum = """

## Adenda V174 · serie anual y expediente receptor

Fuentes oficiales contemporáneas muestran que otras Notas SIGEN de 2009 dejaron un doble rastro: número/área/asunto del emisor y expediente del receptor. ERAS vinculó la Nota 3832/2009-GSPF con el Expediente 828-09, y la Nota 5095/2009-GSPF con el Expediente 878-09, registrando además informes internos, dictamen, pases y respuesta. La superficie AuditoresWeb conserva la Nota 2518/2009 con fecha 6/7/2009; Infoleg conserva 3059/09 y 4169/09 en secuencias receptoras fechadas.

Por ello se pide: (a) exportación del libro/tabla de Notas SIGEN 2009 tipo `NOT`, sin limitar la búsqueda a publicaciones; (b) regla de numeración anual y alcance común o por área; (c) fila 3672/09 con todos los campos CIDD; y (d) crosswalk con el expediente/actuación/asiento de ingreso CGN. La aproximación julio-diciembre es sólo auxiliar: la búsqueda principal debe cubrir todo 2009. Un cero del buscador público de Informes no es una certificación negativa del Archivo Digital de Notas.

Common Crawl volvió a fallar 2/2 en el control V174; las 40 consultas siguen pendientes y no producen ausencia. Estado DRAFT_NOT_SENT; solicitudes 0; SAF355 0/5; ejecución bancaria 0/10.
"""
for name in ("REQUEST_ECONOMIA_TESORO_SETTLEMENT_V174.md", "REQUEST_SUBMISSION_CHECKLIST_V174.md", "E0_INSTITUTIONAL_REQUEST_PACKAGE_V174.md"):
    path = HERE / name
    body = path.read_text(encoding="utf-8-sig")
    if "Adenda V174 · serie anual" not in body:
        path.write_text(body + addendum, encoding="utf-8")

strict = read_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V174.csv")
strict[0]["coverage_set"] = "V174 strict 34-entity set; unchanged from V173"
strict[0]["v161_change"] = "V174: no banking promotion; unchanged from V173."
write_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V174.csv", strict)

public_log = [
    {"log_id":"PUB174_01","surface":"ArchivoWeb","query_or_target":"Año 2009 + 3672","result":"Total de informes: 0","classification":"PUBLIC_REPORT_SEARCH_NEGATIVE_ONLY","limit_or_next_step":"no cubre NOT/backend"},
    {"log_id":"PUB174_02","surface":"SIGEN AuditoresWeb","query_or_target":"Nota 2518/2009","result":"fecha 6/7/2009 localizada","classification":"DATED_SERIAL_COMPARATOR","limit_or_next_step":"no interpolar sin regla"},
    {"log_id":"PUB174_03","surface":"Infoleg","query_or_target":"Notas 3059/09 y 4169/09","result":"secuencias receptoras fechadas localizadas","classification":"CONTEXTUAL_SERIAL_COMPARATORS","limit_or_next_step":"fecha exacta no impresa"},
    {"log_id":"PUB174_04","surface":"ERAS acta 12/09","query_or_target":"Nota 3832/2009-GSPF","result":"asunto + Expte 828-09 + respuesta","classification":"RECIPIENT_DUAL_IDENTIFIER_PROVED","limit_or_next_step":"aplicar método a CGN"},
    {"log_id":"PUB174_05","surface":"ERAS orden/acta 1/10","query_or_target":"Nota 5095/2009-GSPF","result":"asunto + Expte 878-09 + pases","classification":"RECIPIENT_DUAL_IDENTIFIER_PROVED","limit_or_next_step":"comparador posterior"},
    {"log_id":"PUB174_06","surface":"Common Crawl","query_or_target":"control CC-MAIN-2014-49 dos hosts","result":"2 service errors","classification":"SERVICE_ERROR","limit_or_next_step":"40 pendientes no ejecutadas"},
]
write_csv(HERE / "V174_PUBLIC_SEARCH_LOG.csv", public_log)

recovery = f"""# Recuperación archivística · V174

Se probó el patrón contemporáneo Nota SIGEN → expediente receptor: 3832/2009-GSPF → ERAS 828-09 y 5095/2009-GSPF → ERAS 878-09, ambos con asunto y actuaciones. La serie pública añade 2518/2009 fechada 6/7/2009 y comparadores contextuales 3059/09 y 4169/09. Esto mejora la búsqueda de 3672/09, pero no autoriza fecharla por interpolación ni trasladar la numeración ERAS a CGN. Debe pedirse el libro NOT 2009, regla de numeración, fila CIDD y crosswalk receptor CGN. ArchivoWeb 2009+3672 dio 0 dentro de Informes, no dentro de Notas. Common Crawl volvió a fallar 2/2; 40 pendientes. Archivo 613/613; panel 34 y {COVERAGE}%; solicitudes 0, SAF355 0/5, ejecución 0/10.
"""
for name in ("E0_PLAN_2009_ARCHIVE_RECOVERY_NOTE_V174.md", "E0_SIGEN_ARCHIVAL_INDEX_RECOVERY_NOTE_V174.md", "E0_FISCAL_RECONSTRUCTION_V174.md"):
    (HERE / name).write_text(recovery, encoding="utf-8")
(HERE / "CNV_ATTACHMENT_ANALYTIC_REVIEW_V174.md").write_text(f"# Revisión acumulada V174\n\nPanel 34 y {COVERAGE}% congelado. El patrón Nota→expediente receptor quedó probado por comparadores ERAS; 3672/09 y su expediente CGN siguen abiertos. Solicitudes 0; SAF355 0/5; ejecución 0/10.\n", encoding="utf-8")

bundle_specs = [
    ("SIGEN_AUDITORES_2518", FILES["auditors"], sources[0]["url_original"], "comparador fechado"),
    ("INFOLEG_NOTE3059", FILES["da235"], sources[1]["url_original"], "comparador contextual inferior"),
    ("INFOLEG_NOTE4169", FILES["da722"], sources[2]["url_original"], "comparador contextual superior"),
    ("ERAS_NOTE3832", FILES["acta12"], sources[3]["url_original"], "nota→expediente receptor"),
    ("ERAS_NOTE5095_ACTA", FILES["acta01"], sources[4]["url_original"], "nota→expediente y actuaciones"),
    ("ERAS_NOTE5095_ORDER", FILES["orden01"], sources[5]["url_original"], "control de agenda"),
    ("CC_CONTROL", FILES["cc"], "generated log", "2 service errors"),
    ("CC_SCANNER", FILES["scanner"], "generated method", "reproducible control"),
]
bundle = [{"role": role, "path": "/" + path.relative_to(REPO).as_posix(), "url": url, "bytes": str(path.stat().st_size), "sha256": sha(path), "analytic_use": use} for role, path, url, use in bundle_specs]
write_csv(HERE / "V174_SOURCE_BUNDLE.csv", bundle)

SYNC.mkdir(parents=True, exist_ok=True)
sync = []
for source in sources:
    path = REPO / source["archivo_local"].lstrip("/")
    sync.append({"role":"V174_PUBLIC_SOURCE","relative_path":source["archivo_local"],"source_url":source["url_original"],"size_bytes":str(path.stat().st_size),"sha256":source["sha256"],"format_verification":"PDF_VISUAL_PASS_TLS_VALID" if path.suffix.lower() == ".pdf" else "HTML_CONTENT_PASS_TLS_VALID"})
write_csv(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V174.csv", sync)
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V174.csv", public_log)
(SYNC / "SOURCE_SYNC_REPORT_V174.md").write_text("# Sincronización V174\n\n- Catálogo 613/613, hash válido, brecha 0.\n- +6 fuentes oficiales: tres comparadores seriales y tres documentos ERAS.\n- Tres PDF controlados visualmente.\n- Common Crawl control 2/2 errores; lote 40 no ejecutado.\n", encoding="utf-8")
(SYNC / "qa_source_sync_v174.py").write_text("""from pathlib import Path
import csv,hashlib
root=Path(__file__).resolve().parents[5]
rows=list(csv.DictReader(Path(__file__).with_name('SOURCE_SYNC_FILE_MANIFEST_V174.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==6
for r in rows:
 p=root/r['relative_path'].lstrip('/'); assert p.is_file() and p.stat().st_size==int(r['size_bytes']) and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
print('SOURCE SYNC V174 PASS · 6/6')
""", encoding="utf-8")

census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V174.csv")
for source in sources:
    path = REPO / source["archivo_local"].lstrip("/")
    census.append({"source_id":source["id"],"institution":source["institucion"],"artifact":source["titulo"],"url":source["url_original"],"local_path":source["archivo_local"],"sha256":source["sha256"],"bytes":str(path.stat().st_size),"period_coverage":source["periodo_utilizado"],"variable_families":"Nota3672;SIGEN;serial;recipient_file;CGN","primary_source":"YES","preserved":"YES","method_breaks":"comparator not target body","use_status":"E0_USABLE_COMPARATOR","caveat":source["nota"]})
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V174.csv", list({r["source_id"]: r for r in census}.values()))
prov = read_csv(HERE / "ARCHIVAL_PROVENANCE_V174.csv")
for source in sources:
    path = REPO / source["archivo_local"].lstrip("/")
    prov.append({"source_id":source["id"],"original_url":source["url_original"],"retrieval_url":source["url_original"],"capture_timestamp":"2026-09-01","cdx_digest":"N/A_OFFICIAL_DIRECT_TLS_VALID","local_path":source["archivo_local"],"sha256":source["sha256"],"bytes":str(path.stat().st_size),"provenance_note":source["nota"]})
write_csv(HERE / "ARCHIVAL_PROVENANCE_V174.csv", list({r["source_id"]: r for r in prov}.values()))
with (HERE / "SOURCE_REFERENCES_V174.md").open("a", encoding="utf-8") as f:
    f.write("\n## V174 · serie de Notas y expedientes receptores\n")
    for source in sources:
        f.write(f"\n- `{source['id']}` · {source['titulo']} · {source['url_original']} · `{source['archivo_local']}` · `{source['sha256']}`\n")
with (HERE / "RETRIEVAL_LOG_V174.md").open("a", encoding="utf-8") as f:
    f.write("\n## V174\n\n- ArchivoWeb 2009+3672: 0 informes, negativo no trasladable a Notas.\n- Comparadores 2518, 3059, 3832, 4169 y 5095 localizados.\n- Patrón Nota SIGEN→expediente receptor probado en ERAS.\n- CC control 2/2 errores; lote 40 detenido.\n")

(HERE / "README_V174.md").write_text(f"""# Checkpoint V174

- Archivo 613/613; +6 fuentes oficiales; hashes válidos.
- ArchivoWeb 2009 + `3672`: 0 informes; no es un negativo del universo `NOT`.
- Nota 2518/2009 fechada 6/7/2009; 3059/09 y 4169/09 preservadas como comparadores contextuales.
- ERAS prueba el patrón Nota SIGEN → expediente receptor: 3832/2009-GSPF → 828-09; 5095/2009-GSPF → 878-09.
- La fecha exacta y el expediente receptor CGN de 3672/09 siguen abiertos; no se interpola como hecho.
- Pedido mejorado: libro NOT 2009, regla de numeración, fila CIDD y crosswalk CGN.
- Common Crawl: nuevo control 2/2 errores; cuarenta pendientes no ejecutadas.
- Panel 34; {NUMERATOR}/{ASSETS}; {COVERAGE}%; solicitudes 0; SAF355 0/5; ejecución 0/10.
""", encoding="utf-8")
(HERE / "VEREDICTO_V174.md").write_text("# Veredicto V174\n\nAvance probatorio metodológico. Quedó probado con fuentes oficiales contemporáneas que Notas SIGEN de 2009 se correlacionaban con expedientes del receptor, asunto y actuaciones. Esto fortalece la exigencia de buscar 3672/09 tanto en SIGEN como en CGN. No se recuperó aún su cuerpo, fila CIDD, SPD, caja ni expediente receptor; no hay promoción bancaria ni solicitud enviada.\n", encoding="utf-8")
(HERE / "AUDITORIA_V174.md").write_text(f"# Auditoría V174\n\n- 613/613 fuentes; huecos 0; nuevas 6.\n- PDF visual: ERAS acta 12/09 páginas 1-2 PASS; acta 1/10 página 1 PASS; orden 1/10 página 1 PASS.\n- Comparadores seriales 6; crosswalk receptor 3; control ArchivoWeb 1.\n- CC: 2 errores de control; lote 40 no ejecutado.\n- Panel 34, {COVERAGE}%; solicitudes 0; SAF355 0/5; ejecución 0/10.\n", encoding="utf-8")
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V174_A_V175.md").write_text("""# Handover V174 → V175

## Cerrado
- Archivo 613/613; seis fuentes oficiales nuevas.
- ArchivoWeb 2009+3672 produjo 0 sólo dentro de Informes.
- Comparadores seriales 2518, 3059, 3832, 4169 y 5095 preservados.
- ERAS prueba Nota SIGEN → expediente receptor + asunto + actuaciones.
- Common Crawl volvió a fallar 2/2; cuarenta pendientes.

## Prioridad V175
1. Buscar regla de numeración anual de Notas SIGEN 2009 y exportación tipo NOT.
2. Recuperar fila CIDD 3672/09, SPD, archivo, acceso y caja.
3. Obtener en CGN el expediente/actuación receptor por número, asunto y 0120/09 DAIF.
4. Correlacionar salida SIGEN, ingreso CGN, expediente, SISIO y COMDOC sin inferencias.
5. Reintentar Common Crawl sólo tras control válido.
6. Mantener seis DRAFT_NOT_SENT, solicitudes 0, SAF355 0/5 y ejecución 0/10.
""", encoding="utf-8")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V173.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint":"V174", "date":"2026-09-01", "master_catalog_entries":613, "physical_local_copies":613, "physical_local_hash_ok":613, "remaining_catalog_physical_or_hash_gaps":0,
    "state":"SOURCE_ARCHIVE_COMPLETE_RECIPIENT_FILE_PATTERN_PROVED_NOTE_TARGET_OPEN", "analytical_promotion":"NONE_V174_ARCHIVAL_COMPARATORS_ONLY", "exact_entities":34,
    "strict_coverage_pct":COVERAGE, "strict_asset_numerator_million_ars":NUMERATOR, "system_assets_million_ars":ASSETS, "strict_coverage_increment_v173_pp":"0",
    "requests_submitted":0, "responses_received":0, "saf355_certifications_located":0, "executed_historical_bank_rows_confirmed":0,
    "note_3672_09_body_located":False, "note_3672_archive_digital_record_located":False, "note_3672_spd_located":False, "note_3672_physical_box_located":False,
    "note_3672_recipient_file_located":False, "sigen_2009_note_numbering_rule_located":False, "recipient_note_to_local_file_pattern_proved":True,
    "archiveweb_2009_3672_total_reports":0, "archiveweb_zero_proves_note_absence":False,
    "commoncrawl_exact_prefix_queries_completed":154, "commoncrawl_exact_prefix_queries_v174":2, "commoncrawl_valid_no_capture_v174":0, "commoncrawl_service_errors_v174":2,
    "commoncrawl_exact_prefix_service_errors":44, "commoncrawl_capture_rows_v174":0, "commoncrawl_pending_retry_queries":40, "commoncrawl_pending_retry_collections":20,
    "new_v174_sources":6,
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V174.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

origins = read_csv(ORIGINS)
by_path = {r["path"]: r for r in origins}
for path in iter_files(HIST_ROOT):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"downloaded/preserved V174" if path.parent == HIST else "generated/preserved V174","note":"official comparator or controlled diagnostic"}
for path in iter_files(SYNC):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V174","note":"incremental source synchronization"}
for path in HERE.iterdir():
    if path.is_file():
        by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V174","note":"recipient-file comparator checkpoint"}
for path in (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V174.csv", AUDIT / "SOURCE_BACKUP_CENSUS_V174.csv", AUDIT / "SOURCE_PRESERVATION_MISSING_V174.csv", AUDIT / "CURRENT_SOURCE_COMPLETENESS_V174.json"):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V174","note":"613-source completeness"}
write_csv(ORIGINS, list(by_path.values()), ["path", "origin", "note"])

transparency = CYCLE / "TRANSPARENCY_README.md"
body = transparency.read_text(encoding="utf-8-sig")
if "## V174 · Notas y expedientes receptores" not in body:
    body += "\n\n## V174 · Notas y expedientes receptores\n\nFuentes oficiales contemporáneas prueban el patrón Nota SIGEN→expediente receptor con asunto y actuaciones. La 3672/09 sigue abierta y no se fecha por interpolación. ArchivoWeb sólo dio cero dentro de Informes; Common Crawl volvió a fallar. Archivo 613/613; panel 34; solicitudes 0.\n"
    transparency.write_text(body, encoding="utf-8")
(REPO / "BACKUP_ACTUALIZACION_2026-09-01.md").write_text(f"# Backup de actualización · 2026-09-01\n\n- V174; 613/613 fuentes.\n- Patrón Nota SIGEN→expediente receptor probado; target 3672 aún abierto.\n- ArchivoWeb cero sólo en Informes.\n- CC control falló; 40 pendientes no ejecutadas.\n- Panel 34, {COVERAGE}%; solicitudes 0; SAF355 0/5; ejecución 0/10.\n", encoding="utf-8")

(HERE / "qa_v174.py").write_text("""from pathlib import Path
import csv,hashlib,json
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==613
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V174.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==613 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V174.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V174' and co['master_catalog_entries']==613
assert co['recipient_note_to_local_file_pattern_proved'] and not co['note_3672_recipient_file_located'] and not co['archiveweb_zero_proves_note_absence']
assert co['commoncrawl_service_errors_v174']==2 and co['commoncrawl_pending_retry_queries']==40 and co['requests_submitted']==co['saf355_certifications_located']==co['executed_historical_bank_rows_confirmed']==0
assert len(rows('E0_SIGEN_2009_NOTE_SERIAL_DATE_ENVELOPE_V174.csv'))==6 and len(rows('E0_RECIPIENT_NOTE_TO_LOCAL_FILE_COMPARATORS_V174.csv'))==3
assert len(rows('E0_ARCHIVEWEB_EXACT_SEARCH_CONTROL_V174.csv'))==1 and len(rows('E0_SIGEN_NOTE_SEARCH_WINDOW_V174.csv'))==3
assert len(rows('V174_PDF_VISUAL_CONTROL.csv'))==3 and all(x['result'].startswith('PASS') for x in rows('V174_PDF_VISUAL_CONTROL.csv'))
keys=rows('E0_REQUEST_SEARCH_KEY_MATRIX_V174.csv'); assert {'SK174_20','SK174_21','SK174_22','SK174_23','SK174_24','SK174_25'}<={x['key_id'] for x in keys}
obj=rows('E0_V174_REQUEST_OBJECTS.csv'); assert {'RO174_20','RO174_21','RO174_22'}<={x['row_id'] for x in obj} and all(x['status']=='DRAFT_NOT_SENT' for x in obj) and obj==rows('E0_V174_REQUEST_OBJECTS_V174.csv')
for n in ('REQUEST_AGN_2018_REPLY_V174.md','REQUEST_BCRA_CRYL_SETTLEMENT_V174.md','REQUEST_BNA_FIRST_STAGE_BLOTTER_V174.md','REQUEST_CAJA_SETTLEMENT_HOLDINGS_V174.md','REQUEST_CNV_CUSTODY_RECORDS_V174.md','REQUEST_ECONOMIA_TESORO_SETTLEMENT_V174.md'):
 s=(H/n).read_text(encoding='utf-8-sig'); assert 'DRAFT_NOT_SENT' in s or 'BORRADOR_NO_ENVIADO' in s
panel=rows('FOUR_LEG_PASS_PANEL_V174.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
assert len(rows('V174_SOURCE_BUNDLE.csv'))==8
m=json.loads((H/'MANIFEST_V174.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V174' and m['parent_checkpoint']=='V173' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V174 QA PASS · 613/613 · new=6 · RECIPIENT-FILE-PATTERN=PROVED · CC=2-errors/40-pending · panel=34 · requests=0 · SAF355=0/5 · execution=0/10')
""", encoding="utf-8")

(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")
manifest_files = [{"path":p.name,"bytes":p.stat().st_size,"sha256":sha(p)} for p in sorted(HERE.iterdir(), key=lambda x: x.name.casefold()) if p.is_file() and p.name != "MANIFEST_V174.json"]
manifest = {
    "checkpoint":"V174", "parent_checkpoint":"V173", "created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "exact_entities":34, "strict_coverage_pct":COVERAGE, "strict_asset_numerator_million_ars":NUMERATOR, "system_assets_million_ars":ASSETS,
    "new_promotions":[], "source_archive":"613/613; six sources added",
    "historical_finding":"recipient Note→local file pattern proved; serial comparators preserved; target body/record still open",
    "note_3672_09_body":"NOT_LOCATED", "note_3672_recipient_file":"NOT_LOCATED", "commoncrawl_queries_v174":2,
    "commoncrawl_service_errors_v174":2, "commoncrawl_pending":40, "closed_network_gate":"NO", "saf355_certifications":"0/5",
    "executed_historical_bank_rows":"0/10", "requests_submitted":0, "files":manifest_files,
}
(HERE / "MANIFEST_V174.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path":p.relative_to(REPO).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)} for p in iter_files(REPO) if p != global_manifest]
payload = {"checkpoint":"V174","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),"strict_coverage_pct":COVERAGE,"exact_entities":34,"closed_network_gate":"NO","source_audit":"613 master; 613 physical SHA-valid","historical_workstream":"recipient file pattern proved; target record/body open; CC pending 40; six drafts not sent","file_count_excluding_manifest":len(global_files),"files":global_files}
tmp = global_manifest.with_suffix(".json.V174tmp")
tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
tmp.replace(global_manifest)
print("V174 BUILD PASS · catalog=613/613 · new=6 · recipient-file-pattern=PROVED · cc=2 errors/40 pending · panel=34 · requests=0")
