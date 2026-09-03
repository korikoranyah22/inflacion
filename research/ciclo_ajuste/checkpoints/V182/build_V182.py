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
PARENT = CYCLE / "checkpoints" / "V181"
AUDIT = CYCLE / "source_audit"
SYNC = CYCLE / "inputs" / "source_sync" / "v182"
HIST_ROOT = CYCLE / "inputs" / "historical_retrieval" / "v182"
HIST = HIST_ROOT / "binaries"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"
EXCLUDED = {".git", "__pycache__", "tmp", "node_modules"}
COVERAGE = "63.440604"
NUMERATOR = "61345602.215"
ASSETS = "96697695.5"


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows, fields=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or (list(rows[0]) if rows else [])
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def iter_files(root):
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted((name for name in dirs if name not in EXCLUDED), key=str.casefold)
        for name in sorted(files, key=str.casefold):
            yield Path(directory) / name


def tree(root):
    out = []
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted((name for name in dirs if name not in EXCLUDED), key=str.casefold)
        base = Path(directory)
        out += [(base / name).relative_to(root).as_posix() + "/" for name in dirs]
        out += [(base / name).relative_to(root).as_posix() for name in sorted(files, key=str.casefold)]
    return "\n".join(out) + "\n"


def append_once(path, marker, text):
    body = path.read_text(encoding="utf-8-sig") if path.exists() else ""
    if marker not in body:
        path.write_text(body.rstrip() + "\n\n" + text.strip() + "\n", encoding="utf-8")


def clone_parent():
    skip = {
        "MANIFEST_V181.json", "README_V181.md", "VEREDICTO_V181.md", "AUDITORIA_V181.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V181_A_V182.md", "V181_SOURCE_BUNDLE.csv",
        "V181_PUBLIC_SEARCH_LOG.csv", "V181_PDF_VISUAL_CONTROL.csv", "V181_HTML_CONTENT_CONTROL.csv",
        "CORRECTION_LOG_V181.md",
    }
    HERE.mkdir(parents=True, exist_ok=True)
    for source in sorted(PARENT.iterdir(), key=lambda path: path.name.casefold()):
        if not source.is_file() or source.name in skip or source.name.startswith(("build_", "qa_")):
            continue
        target = HERE / source.name.replace("V181", "V182")
        target.write_bytes(source.read_bytes())


SOURCE_SPECS = [
    {
        "id": "e0_cgn_account2020_bid1192_zero_uncertified_closure_v182",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2020 · Anexo 4.21 SAF 362",
        "url": "https://www.argentina.gob.ar/sites/default/files/cuenta2020-separatai-anexo-4.21-mdp.xlsx",
        "file": "cgn_account_2020_annex_4_21_mdp.xlsx", "published": "2021", "period": "2020",
        "type": "XLSX oficial preservado · inspección estructural y visual",
        "note": "BID 1192 (FONDIF) presenta saldo inicial, entradas, salidas y saldo final en cero. La nota (3) exige separar cero financiero de cierre definitivo.",
    },
    {
        "id": "e0_cgn_account2020_bid1192_notes_uncertified_closure_v182",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2020 · Notas Anexo 4.21 SAF 362",
        "url": "https://www.argentina.gob.ar/sites/default/files/cuenta2020-separatai-anexo-4.21-notas.pdf",
        "file": "cgn_account_2020_annex_4_21_notes.pdf", "published": "2021", "period": "2020",
        "type": "PDF oficial preservado · control visual de página 1",
        "note": "Nota 3: el proyecto no informó transacciones en 2020, pero seguía incluido porque no se había certificado su cierre definitivo.",
    },
    {
        "id": "e0_cgn_account2020_bank_accounts_mypes_absence_v182",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2020 · Anexo 4.37 Cuentas Bancarias",
        "url": "https://www.argentina.gob.ar/sites/default/files/cuenta2020-separatai-anexo-4.37-cuentas_bancarias.xlsx",
        "file": "cgn_account_2020_annex_4_37_bank_accounts.xlsx", "published": "2021", "period": "2020",
        "type": "XLSX oficial preservado · búsqueda integral de identificadores",
        "note": "No contiene coincidencias textuales para BID 1192, MyPES, MY 4002, MYUEC, COBCAP o COBINT. Ausencia de publicación, no certificado de cierre.",
    },
    {
        "id": "e0_cgn_account2021_mdp_bid1192_absence_v182",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2021 · Anexo 4.20 SAF 362",
        "url": "https://www.argentina.gob.ar/sites/default/files/cuenta2021-separatai-anexo-4.20.xlsx",
        "file": "cgn_account_2021_annex_4_20_mdp.xlsx", "published": "2022", "period": "2021",
        "type": "XLSX oficial preservado · inspección estructural y visual",
        "note": "El BID 1192 ya no integra las columnas del SAF 362. La desaparición posterior al cero 2020 no prueba por sí sola extinción jurídica ni destino de saldos históricos.",
    },
    {
        "id": "e0_cgn_account2021_mdp_notes_v182",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2021 · Notas Anexo 4.20 SAF 362",
        "url": "https://www.argentina.gob.ar/sites/default/files/cuenta2021-separatai-anexo-4.20-notas.pdf",
        "file": "cgn_account_2021_annex_4_20_notes.pdf", "published": "2022", "period": "2021",
        "type": "PDF oficial preservado · control visual de páginas 1 y 3",
        "note": "Las notas ilustran que CGN exige documentación específica para certificar finalización y ausencia de deudas en otros componentes; no contienen esa certificación para BID 1192.",
    },
    {
        "id": "e0_cgn_account2021_bank_accounts_mypes_absence_v182",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2021 · Anexo 4.35 Cuentas Bancarias",
        "url": "https://www.argentina.gob.ar/sites/default/files/cuenta2021-separatai-anexo-4.35-cuentas-bancarias.xlsx",
        "file": "cgn_account_2021_annex_4_35_bank_accounts.xlsx", "published": "2022", "period": "2021",
        "type": "XLSX oficial preservado · búsqueda integral de identificadores",
        "note": "En la hoja ctas A1:P1041 no hay coincidencias textuales para BID 1192, MyPES, MY 4002, MYUEC, COBCAP o COBINT.",
    },
    {
        "id": "e0_infoleg_res1406_2014_labor_negative_identity_v182",
        "institution": "Boletín Oficial / Infoleg",
        "title": "Resolución 1406/2014 publicada · control negativo de identidad",
        "url": "https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-1406-2014-235340/texto",
        "file": "infoleg_resolution_1406_2014_labor_negative_comparator.html", "published": "2014-09-19", "period": "2014",
        "type": "HTML oficial preservado · control de identidad",
        "note": "La Resolución 1406/2014 publicada es laboral (Secretaría de Trabajo; APUAYE/Transcomahue) y no es el acto MyPES referido por SIGEN. Apunta a una serie interna o no publicada distinta.",
    },
    {
        "id": "e0_sigen_archive_cuenta2018_record_v182", "institution": "Sindicatura General de la Nación",
        "title": "ArchivoWeb SIGEN · ficha Cuenta de Inversión 2018", "url": "https://www.sigen.gob.ar/archivoweb/ArchivosAdjuntos_Ver.aspx?IdDocumento=201921",
        "file": "sigen_archive_record_cuenta_2018_201921.html", "published": "2019", "period": "2018-2019",
        "type": "HTML oficial preservado · metadatos sin binario público visible", "note": "Prueba la ficha 201921; la página pública expone metadatos, pero no enlace de adjunto recuperable.",
    },
    {
        "id": "e0_sigen_archive_cuenta2019_record_v182", "institution": "Sindicatura General de la Nación",
        "title": "ArchivoWeb SIGEN · ficha Cuenta de Inversión 2019", "url": "https://www.sigen.gob.ar/archivoweb/ArchivosAdjuntos_Ver.aspx?IdDocumento=204917",
        "file": "sigen_archive_record_cuenta_2019_204917.html", "published": "2020", "period": "2019-2020",
        "type": "HTML oficial preservado · metadatos sin binario público visible", "note": "Prueba la ficha 204917; la página pública expone metadatos, pero no enlace de adjunto recuperable.",
    },
    {
        "id": "e0_sigen_archive_cuenta2020_record_v182", "institution": "Sindicatura General de la Nación",
        "title": "ArchivoWeb SIGEN · ficha Cuenta de Inversión 2020", "url": "https://www.sigen.gob.ar/archivoweb/ArchivosAdjuntos_Ver.aspx?IdDocumento=207827",
        "file": "sigen_archive_record_cuenta_2020_207827.html", "published": "2021", "period": "2020-2021",
        "type": "HTML oficial preservado · metadatos sin binario público visible", "note": "Prueba la ficha 207827; la página pública expone metadatos, pero no enlace de adjunto recuperable.",
    },
    {
        "id": "e0_wayback_sigen_attachment_78595142_negative_control_v182", "institution": "SIGEN / Internet Archive",
        "title": "Adjunto SIGEN 78595142 · control negativo CNRT IESCI 2011", "url": "http://www.sigen.gob.ar/archivoweb/ArchivoAdjunto_Ver.aspx?IdA=78595142",
        "file": "wayback_sigen_attachment_78595142_cnrt_iesci_2011_negative_control.pdf", "published": "2012-06", "period": "2011-2012",
        "type": "PDF histórico preservado por Wayback · control visual páginas 1-3", "note": "Único adjunto capturado hallado por la consulta CDX exploratoria; corresponde a CNRT/IESCI 2011 y no a MyPES. Se conserva para impedir una atribución errónea.",
    },
    {
        "id": "e0_wayback_sigen_attachment_cdx_provenance_v182", "institution": "Internet Archive",
        "title": "CDX · consulta de adjuntos SIGEN 2019-2022", "url": "https://web.archive.org/cdx/search/cdx?url=www.sigen.gob.ar/archivoweb/ArchivoAdjunto_Ver.aspx%3FIdA%3D*&from=2019&to=2022&output=json&filter=statuscode:200&filter=mimetype:application/pdf&collapse=digest",
        "file": "wayback_cdx_sigen_attachment_query_2026-09-01.json", "published": "2026-09-01", "period": "2019-2022",
        "type": "JSON CDX preservado · procedencia de búsqueda", "note": "Devuelve un único digest/captura para el adjunto 78595142; no prueba inexistencia de otros binarios fuera de la cobertura de Wayback.",
    },
    {
        "id": "e0_wayback_sigen_detail_cdx_negative_v182", "institution": "Internet Archive",
        "title": "CDX · consulta de fichas SIGEN con IdDocumento", "url": "https://web.archive.org/cdx/search/cdx?url=www.sigen.gob.ar/archivoweb/ArchivosAdjuntos_Ver.aspx%3FIdDocumento%3D*&output=json&filter=statuscode:200&collapse=digest",
        "file": "wayback_cdx_sigen_detail_query_2026-09-01.json", "published": "2026-09-01", "period": "archivo histórico",
        "type": "JSON CDX preservado · resultado vacío", "note": "La consulta guardada devuelve []; es un negativo de cobertura, no prueba de que las fichas o adjuntos nunca existieron.",
    },
]


clone_parent()
SYNC.mkdir(parents=True, exist_ok=True)

for spec in SOURCE_SPECS:
    assert (HIST / spec["file"]).is_file(), spec["file"]

catalog = read_csv(CATALOG)
catalog_fields = list(catalog[0])
by_id = {row["id"]: row for row in catalog}
existing_2019 = by_id["e0_cgn_account2019_bid1192_missing_information_accounts_v177"]
sentence = "V182 identifica MY 4002 como Fondo Comisión de Compromiso y separa ese saldo de referencia 2018 de cualquier deuda, pago o provisión por Resolución 1406."
if sentence not in existing_2019["nota"]:
    existing_2019["nota"] = (existing_2019["nota"].rstrip() + " " + sentence).strip()

new_sources = []
for spec in SOURCE_SPECS:
    path = HIST / spec["file"]
    row = {
        "id": spec["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": spec["institution"],
        "titulo": spec["title"], "url_original": spec["url"],
        "archivo_local": "/" + path.relative_to(REPO).as_posix(), "fecha_descarga": "2026-09-01",
        "fecha_publicacion": spec["published"], "codigo_serie": spec["title"],
        "periodo_utilizado": spec["period"], "tipo": spec["type"], "sha256": sha(path), "nota": spec["note"],
    }
    by_id[row["id"]] = row
    new_sources.append(row)
catalog = list(by_id.values())
write_csv(CATALOG, catalog, catalog_fields)
assert len(catalog) == len({row["id"] for row in catalog}) == 697

audit = []
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    actual = sha(path) if path.is_file() else ""
    audit.append({"id": row["id"], "archivo_local": row["archivo_local"], "exists": str(path.is_file()), "sha_catalog": row["sha256"].lower(), "sha_actual": actual, "hash_ok": str(path.is_file() and bool(row["sha256"]) and actual == row["sha256"].lower())})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V182.csv", audit)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V182.csv", audit)
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V182.csv", [row for row in audit if row["hash_ok"] != "True"], list(audit[0]))
assert all(row["hash_ok"] == "True" for row in audit)

write_csv(HERE / "E0_BID1192_CGN_TRANSITION_2018_2021_V182.csv", [
    {"row_id":"CT182_01","cutoff":"2018-12-31","publication":"Cuenta 2019","status":"REFERENCE_BALANCES_ONLY","proved":"16 cuentas y ARS 824.861.366,21 equivalentes informados por referentes","not_proved":"extractos, conciliación, titularidad actual o disponibilidad 2019","source":"Cuenta 2019 Anexo 4.35 PDF 167-169"},
    {"row_id":"CT182_02","cutoff":"2019-12-31","publication":"Cuenta 2019","status":"NO_INFORMATION_SUBMITTED","proved":"CGN declara que no se presentó información del programa","not_proved":"cero, cierre, extinción, pago o destino","source":"Cuenta 2019 Anexo 4.35 PDF 167-169"},
    {"row_id":"CT182_03","cutoff":"2020-12-31","publication":"Cuenta 2020","status":"ZERO_FINANCIAL_MOVEMENTS_CLOSURE_UNCERTIFIED","proved":"BID 1192 con todos los rubros en cero; nota 3 sin cierre definitivo certificado","not_proved":"acto de cierre y conciliación con cuentas históricas","source":"Cuenta 2020 Anexo 4.21 C9/C13:C51 y nota 3"},
    {"row_id":"CT182_04","cutoff":"2021-12-31","publication":"Cuenta 2021","status":"ABSENT_FROM_SAF362_AND_BANK_TABLE","proved":"sin columna BID1192 y sin coincidencias de identificadores MyPES en cuadro bancario","not_proved":"fecha, causa y efectos jurídicos de baja","source":"Cuenta 2021 Anexos 4.20 y 4.35"},
])

accounts = [
    ("2119/45","ARS","22384741.80","22384741.80","cuenta nativa ARS"),("54451/95","ARS","45925902.21","45925902.21","cuenta nativa ARS"),
    ("210010000","USD","81779.15","3066718.24","sin rótulo específico"),("MI 4285","USD","524243.73","19659140.06","Cobro Intereses"),
    ("MS 4285","USD","6410591.97","240397198.95","Cobro Capital"),("MY 4002","USD","15182.68","569350.57","Fondo Comisión de Compromiso"),
    ("MY 4003","USD","12838.50","481443.72","Cobertura Incobrables IFIs"),("MY 4004","USD","31547.90","1183046.44","Gastos UCP"),
    ("MY 4005","USD","213.22","7995.84","Asistencia Técnica"),("MY 4006","USD","25592.23","959708.51","Cobertura Descalce Tasas"),
    ("MYUEC1","USD","4277314.31","160399286.55","Fondos Rotatorios Fideicomiso"),("MYUEC","USD","0.00","0.00","Fondos BID"),
    ("COBCAP","USD","4716737.55","176877658.03","Cobro IFIs Capital"),("COBINT","USD","3695724.11","138589654.14","Cobro IFIs Intereses"),
    ("FP1192","USD","382920.56","14359521.15","Fondo Rotatorio Facilidad"),("FDOGTOS","USD","0.00","0.00","Fondo de Gastos"),
]
write_csv(HERE / "E0_BID1192_ACCOUNT_BALANCES_REFERENCE_2018_V182.csv", [
    {"account_id":account,"currency":currency,"reference_balance_original":original,"reference_ars_equivalent":ars,"description":description,"evidence_status":"REFERENCE_REPORTED_NOT_BANK_STATEMENT","legal_limit":"no prueba deuda Res1406, pago, provisión ni disponibilidad posterior"}
    for account, currency, original, ars, description in accounts
])

write_csv(HERE / "E0_BID1192_MY4002_EVIDENCE_LADDER_V182.csv", [
    {"row_id":"MY182_01","proposition":"existía una cuenta denominada Fondo Comisión de Compromiso","status":"SUPPORTED_REFERENCE_2018","proof":"MY 4002 · USD 15.182,68 · ARS 569.350,57 a tipo 37,5","missing":"extracto, titular, ledger y conciliación"},
    {"row_id":"MY182_02","proposition":"el saldo MY 4002 era la liquidación Res. 1406","status":"NOT_PROVED","proof":"coincidencia temática de denominación","missing":"asiento con expediente/acto/contraparte y cálculo"},
    {"row_id":"MY182_03","proposition":"Macro o Credicoop pagaron esa suma","status":"NOT_PROVED","proof":"ninguna fuente pública localizada","missing":"orden de pago, transferencia, recibo, extracto y asiento espejo"},
    {"row_id":"MY182_04","proposition":"el saldo quedó extinguido en 2020","status":"NOT_PROVED","proof":"BID1192 figura en cero y cierre no certificado","missing":"acta de cierre, destino de remanentes y conciliación cuenta por cuenta"},
    {"row_id":"MY182_05","proposition":"la pretensión administrativa quedó firme","status":"NOT_PROVED","proof":"SIGEN reporta recursos pendientes","missing":"dictámenes, decisión final y notificación"},
])

write_csv(HERE / "E0_RES1406_IDENTITY_AND_ARCHIVE_CONTROL_V182.csv", [
    {"row_id":"RA182_01","object":"Resolución 1406/2014 publicada en Infoleg","result":"NEGATIVE_IDENTITY_CONTROL","proved":"acto laboral ST del 25/08/2014; APUAYE/Transcomahue","limit":"no es el acto MyPES de noviembre reportado por SIGEN"},
    {"row_id":"RA182_02","object":"SIGEN ficha Cuenta 2018 · 201921","result":"METADATA_ONLY","proved":"título, extracto y año","limit":"página pública sin adjunto visible"},
    {"row_id":"RA182_03","object":"SIGEN ficha Cuenta 2019 · 204917","result":"METADATA_ONLY","proved":"título y año","limit":"página pública sin adjunto visible"},
    {"row_id":"RA182_04","object":"SIGEN ficha Cuenta 2020 · 207827","result":"METADATA_ONLY","proved":"título, extracto y año","limit":"página pública sin adjunto visible"},
    {"row_id":"RA182_05","object":"Wayback wildcard ArchivoAdjunto 2019-2022","result":"ONE_IRRELEVANT_CAPTURE","proved":"IdA 78595142 es CNRT IESCI 2011","limit":"cobertura de Wayback incompleta; no prueba inexistencia"},
])

request_path = HERE / "E0_V182_REQUEST_OBJECTS.csv"
requests = read_csv(request_path)
requests += [
    {"row_id":"RO182_77","object_id":"BID1192_MY4002_LEDGER_AND_STATEMENTS","custodian":"SAF 362 · TGN · CGN · BCRA · fiduciario","exact_record":"mayor, extractos, conciliaciones y asientos espejo de MY 4002 Fondo Comisión de Compromiso","period":"2004-cierre definitivo","minimum_fields":"fecha; moneda; debe; haber; saldo; contraparte; concepto; expediente; comprobante; firmante","closure_rule":"Conciliar cada movimiento con banco y acto; negativo técnico si la cuenta se cerró o migró.","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO182_78","object_id":"BID1192_FINAL_CLOSURE_CERTIFICATE","custodian":"SAF 362 · CGN/DAIF · UAI · SIGEN","exact_record":"documentación que certificó o descartó el cierre definitivo del BID 1192 después de la nota 3/2020","period":"2020-2022","minimum_fields":"acto; fecha; autoridad; cuentas; saldos; destino; deudas; juicios; observaciones; anexos","closure_rule":"Debe explicar cero 2020, desaparición 2021 y destino de 16 cuentas históricas.","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO182_79","object_id":"SIGEN_CUENTA_2018_2020_ARCHIVE_BINARIES","custodian":"SIGEN ArchivoWeb / Archivo General","exact_record":"binarios y anexos asociados a IdDocumento 201921, 204917 y 207827","period":"2018-2021","minimum_fields":"IdDocumento; IdA; nombre; MIME; bytes; hash; fecha; versión; vínculo documental","closure_rule":"Entregar archivos o negativo técnico por cada IdDocumento/IdA, no búsqueda temática genérica.","status":"DRAFT_NOT_SENT"},
]
write_csv(request_path, requests)
write_csv(HERE / "E0_V182_REQUEST_OBJECTS_V182.csv", requests)

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V182.csv"
keys = read_csv(keys_path)
keys += [
    {"key_id":"SK182_76","request_id":"RO182_77","key_group":"bank_account","exact_key":"MY 4002; Fondo Comisión de Compromiso; BID 1192/OC-AR","search_purpose":"conciliar saldo 2018 con acto, contraparte y destino","source_or_basis":"Cuenta 2019 Anexo 4.35 PDF 168","caveat":"rótulo contable no equivale a deuda ni pago"},
    {"key_id":"SK182_77","request_id":"RO182_78","key_group":"closure","exact_key":"nota (3) Cuenta 2020; no se había certificado su cierre definitivo; BID 1192 FONDIF","search_purpose":"recuperar certificado y anexos de cierre","source_or_basis":"Cuenta 2020 Anexo 4.21 y notas","caveat":"cero financiero no certifica extinción"},
    {"key_id":"SK182_78","request_id":"RO182_79","key_group":"archive_id","exact_key":"IdDocumento 201921; 204917; 207827","search_purpose":"recuperar binarios SIGEN faltantes","source_or_basis":"ArchivoWeb SIGEN","caveat":"metadatos públicos sin adjunto visible"},
]
write_csv(keys_path, keys)

trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V182.csv"
trace = read_csv(trace_path)
trace += [
    {"trace_id":"TR182_77","request_id":"RO182_77","institution":"SAF 362/TGN/CGN/BCRA/fiduciario","gap_id":"CL182_MY4002","requested_record":"ledger, extractos y conciliaciones MY 4002","period_or_date":"2004-cierre","identifiers":"BID1192; MY4002; comisión compromiso","minimum_usable_fields":"fecha; concepto; contraparte; monto; saldo; comprobante","confidentiality_fallback":"testar datos personales; preservar monto, fecha y contraparte institucional","status":"DRAFT_NOT_SENT"},
    {"trace_id":"TR182_78","request_id":"RO182_78","institution":"SAF362/CGN/UAI/SIGEN","gap_id":"CL182_FINAL_CLOSURE","requested_record":"certificado o expediente de cierre BID1192","period_or_date":"2020-2022","identifiers":"nota 3; Anexo 4.21; BID1192","minimum_usable_fields":"acto; autoridad; cuentas; deudas; destino","confidentiality_fallback":"índice, metadatos y parte dispositiva","status":"DRAFT_NOT_SENT"},
    {"trace_id":"TR182_79","request_id":"RO182_79","institution":"SIGEN","gap_id":"CL182_ARCHIVE_BINARIES","requested_record":"adjuntos de fichas 201921/204917/207827","period_or_date":"2019-2021","identifiers":"IdDocumento; IdA","minimum_usable_fields":"archivo; hash; fecha; vínculo","confidentiality_fallback":"inventario y negativo técnico por archivo","status":"DRAFT_NOT_SENT"},
]
write_csv(trace_path, trace)

source_bundle = []
for row in new_sources:
    path = REPO / row["archivo_local"].lstrip("/")
    source_bundle.append({"source_id":row["id"],"file":path.name,"bytes":path.stat().st_size,"sha256":sha(path),"status":"CATALOGUED_SHA_VALID"})
duplicate = HIST / "cgn_account_2019_separata_i.pdf"
source_bundle.append({"source_id":"duplicate_of_e0_cgn_account2019_bid1192_missing_information_accounts_v177","file":duplicate.name,"bytes":duplicate.stat().st_size,"sha256":sha(duplicate),"status":"BYTE_IDENTICAL_DUPLICATE_LOCAL_CONTROL_NOT_NEW_CATALOG_ROW"})
write_csv(HERE / "V182_SOURCE_BUNDLE.csv", source_bundle)

write_csv(HERE / "V182_PDF_VISUAL_CONTROL.csv", [
    {"file":"cgn_account_2019_separata_i.pdf","pages":"167-169","result":"PASS_RELEVANT_ACCOUNT_ROWS_AND_NO_INFORMATION_NOTE"},
    {"file":"cgn_account_2020_annex_4_21_notes.pdf","pages":"1","result":"PASS_RELEVANT_NOTE_3"},
    {"file":"cgn_account_2021_annex_4_20_notes.pdf","pages":"1,3","result":"PASS_CLOSURE_DOCUMENTATION_COMPARATOR"},
    {"file":"wayback_sigen_attachment_78595142_cnrt_iesci_2011_negative_control.pdf","pages":"1-3","result":"PASS_NEGATIVE_IDENTITY_CONTROL_CNRT"},
])
write_csv(HERE / "V182_XLSX_CONTENT_CONTROL.csv", [
    {"file":"cgn_account_2020_annex_4_21_mdp.xlsx","sheet":"362","range":"A1:P52","result":"PASS_BID1192_COLUMN_ALL_ZERO"},
    {"file":"cgn_account_2020_annex_4_37_bank_accounts.xlsx","sheet":"F21","range":"A1:BJ51","result":"PASS_NO_MYPES_IDENTIFIER_MATCH"},
    {"file":"cgn_account_2021_annex_4_20_mdp.xlsx","sheet":"362","range":"A1:O52","result":"PASS_BID1192_COLUMN_ABSENT"},
    {"file":"cgn_account_2021_annex_4_35_bank_accounts.xlsx","sheet":"ctas","range":"A1:P1041","result":"PASS_NO_MYPES_IDENTIFIER_MATCH"},
])
write_csv(HERE / "V182_HTML_CONTENT_CONTROL.csv", [
    {"file":"infoleg_resolution_1406_2014_labor_negative_comparator.html","needle":"APUAYE / TRANSCOMAHUE / Secretaría de Trabajo","result":"PASS_NEGATIVE_IDENTITY_CONTROL"},
    {"file":"sigen_archive_record_cuenta_2018_201921.html","needle":"IdDocumento=201921 / Cuenta de Inversión 2018","result":"PASS_METADATA_ONLY"},
    {"file":"sigen_archive_record_cuenta_2019_204917.html","needle":"IdDocumento=204917 / Cuenta de Inversión 2019","result":"PASS_METADATA_ONLY"},
    {"file":"sigen_archive_record_cuenta_2020_207827.html","needle":"IdDocumento=207827 / Cuenta de Inversión 2020","result":"PASS_METADATA_ONLY"},
])
write_csv(HERE / "V182_JSON_CONTENT_CONTROL.csv", [
    {"file":"wayback_cdx_sigen_attachment_query_2026-09-01.json","result":"PASS_ONE_CAPTURE_78595142","limit":"coverage negative only"},
    {"file":"wayback_cdx_sigen_detail_query_2026-09-01.json","result":"PASS_EMPTY_ARRAY","limit":"coverage negative only"},
])

archival = read_csv(HERE / "ARCHIVAL_PROVENANCE_V182.csv")
for row in new_sources:
    path = REPO / row["archivo_local"].lstrip("/")
    archival.append({"source_id":row["id"],"original_url":row["url_original"],"retrieval_url":row["url_original"],"capture_timestamp":"2026-09-01","cdx_digest":"N/A_OFFICIAL_OR_RECORDED_QUERY","local_path":row["archivo_local"],"sha256":row["sha256"],"bytes":path.stat().st_size,"provenance_note":row["nota"]})
write_csv(HERE / "ARCHIVAL_PROVENANCE_V182.csv", archival)

census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V182.csv")
for row in new_sources:
    path = REPO / row["archivo_local"].lstrip("/")
    census.append({"source_id":row["id"],"institution":row["institucion"],"artifact":row["titulo"],"url":row["url_original"],"local_path":row["archivo_local"],"sha256":row["sha256"],"bytes":path.stat().st_size,"period_coverage":row["periodo_utilizado"],"variable_families":"BID1192;MyPESII;closure;accounts;archive","primary_source":"YES","preserved":"YES","method_breaks":"reference balance vs movement statement vs closure certificate","use_status":"USABLE_WITH_EXPLICIT_LIMIT","caveat":row["nota"]})
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V182.csv", census)

append_once(HERE / "SOURCE_REFERENCES_V182.md", "## V182 · transición contable BID 1192 y archivo SIGEN", """
## V182 · transición contable BID 1192 y archivo SIGEN

- Cuenta 2020: BID 1192 en cero, pero cierre definitivo todavía no certificado.
- Cuenta 2021: BID 1192 e identificadores MyPES ausentes de los anexos SAF 362 y cuentas bancarias publicados.
- Cuenta 2019: MY 4002 aparece como Fondo Comisión de Compromiso, saldo de referencia 2018; no prueba deuda, pago ni provisión.
- Infoleg: la Resolución 1406/2014 publicada es laboral y no corresponde al acto MyPES referido por SIGEN.
- ArchivoWeb SIGEN: fichas 2018-2020 preservadas; los adjuntos no son visibles en la página pública.
""")
append_once(HERE / "RETRIEVAL_LOG_V182.md", "## V182 · búsqueda 2026-09-01", """
## V182 · búsqueda 2026-09-01

- Preservados anexos CGN 2020/2021 de SAF 362 y cuadros bancarios; inspección estructural y visual completada.
- Control de identidad Infoleg completado: la Res. 1406/2014 publicada no es MyPES.
- Tres fichas ArchivoWeb SIGEN preservadas; sin adjuntos públicos visibles.
- Wayback produjo una única captura PDF irrelevante (CNRT 2011), preservada como control negativo.
- Solicitudes enviadas: 0. Tres objetos nuevos quedaron DRAFT_NOT_SENT.
""")

(HERE / "README_V182.md").write_text("""# Checkpoint V182

## Hallazgo principal

V182 reconstruye la transición publicada del BID 1192 después de los saldos de referencia 2018. La Cuenta de Inversión 2020 exhibe `BID 1192 (FONDIF)` con saldo inicial, entradas, salidas y saldo final en cero; su nota 3 aclara que no hubo transacciones, pero que el cierre definitivo aún no había sido certificado. En 2021 el proyecto desaparece del anexo SAF 362 y los identificadores MyPES tampoco aparecen en el cuadro bancario publicado.

La secuencia es compatible con cierre operativo, pero no prueba el acto de cierre, la extinción de obligaciones, el destino de remanentes ni la resolución de la controversia de comisión.

## La cuenta MY 4002

En la Cuenta 2019, dentro de 16 saldos de referencia 2018, `MY 4002` figura como `Fondo Comisión de Compromiso`: USD 15.182,68, equivalentes a ARS 569.350,57 al tipo implícito 37,5. El total de saldos USD referenciados es USD 20.174.685,91 y el total equivalente, sumadas dos cuentas nativas en pesos, ARS 824.861.366,21.

El rótulo es una pista de alta prioridad, no la liquidación de la Resolución 1406. Faltan mayor, extractos, titularidad, contrapartida, comprobantes y vínculo con el expediente.

## Resolución 1406 y archivo

- La Resolución 1406/2014 publicada en Infoleg es un acto laboral de la Secretaría de Trabajo sobre APUAYE/Transcomahue. No es el acto MyPES de noviembre mencionado por SIGEN.
- ArchivoWeb conserva fichas oficiales para las Cuentas 2018, 2019 y 2020, pero la interfaz pública no muestra adjuntos descargables.
- La exploración Wayback sólo recuperó un adjunto CNRT/IESCI 2011, preservado como control negativo; no demuestra inexistencia de los binarios buscados.

## Estado seguro

- Transición contable 2018→2021: probada en publicaciones CGN.
- Cierre jurídico definitivo BID 1192: no probado.
- Deuda firme, pago, provisión, daño o responsabilidad: no probados.
- Archivo: 697/697 fuentes catalogadas con SHA-256 válido; 13 nuevas.
- Solicitudes enviadas: 0; tres objetos nuevos DRAFT_NOT_SENT.
""", encoding="utf-8")

(HERE / "VEREDICTO_V182.md").write_text("""# Veredicto V182

La evidencia sube otro escalón, pero no autoriza el salto final. `MY 4002 – Fondo Comisión de Compromiso` demuestra que existía una cuenta específica asociada a ese concepto y que al cierre 2018 se informó un saldo de referencia. El BID 1192 aparece completamente en cero en 2020 mientras CGN declara que su cierre definitivo todavía no estaba certificado, y desaparece de los anexos publicados en 2021. Esta combinación obliga a pedir el mayor y extractos de MY 4002, el certificado de cierre y la conciliación de las 16 cuentas. Hasta obtenerlos, no corresponde identificar el saldo con la liquidación Res. 1406 ni afirmar pago, condonación, apropiación o daño.
""", encoding="utf-8")

(HERE / "AUDITORIA_V182.md").write_text("""# Auditoría V182

- 697/697 fuentes catalogadas, físicas y SHA-256 válidas; 13 fuentes nuevas.
- 4 PDF controlados visualmente en páginas relevantes; 4 XLSX inspeccionados con rangos definidos.
- 4 HTML oficiales controlados por identidad/metadatos; 2 JSON CDX preservados con límites explícitos.
- Cuenta 2019 duplicada en V182: byte idéntica a la copia catalogada V177; no crea una fuente nueva.
- BID1192 2020: C13/C22/C32/C46 en cero; nota 3: cierre no certificado.
- BID1192 2021: ausente del SAF 362; identificadores MyPES ausentes de cuadro bancario publicado.
- MY4002: USD 15.182,68 / ARS 569.350,57 de referencia 2018; no promovido a deuda ni pago.
- Daño no probado; panel 34; cobertura 63,440604%; solicitudes enviadas 0.
""", encoding="utf-8")

(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V182_A_V183.md").write_text("""# Handover V182 → V183

## Cerrado

- Transición CGN BID1192 2018→2021 reconstruida.
- MY4002 individualizada como Fondo Comisión de Compromiso y matemáticamente separada del total.
- Cero financiero 2020 separado de cierre definitivo no certificado.
- Ausencia 2021 separada de acto jurídico de baja.
- Resolución 1406 laboral de Infoleg descartada por identidad.
- Fichas SIGEN 2018-2020 preservadas; capa de metadatos separada de binarios.

## Prioridad V183

1. Obtener mayor, extractos y conciliaciones de MY4002 desde apertura hasta cierre.
2. Obtener certificado/expediente de cierre BID1192 que explique el cero 2020 y la ausencia 2021.
3. Recuperar adjuntos SIGEN de IdDocumento 201921, 204917 y 207827 mediante IdA/inventario.
4. Recuperar acto íntegro MyPES Res. 1406, expediente, notificaciones, recursos, dictámenes y decisión final.
5. Conciliar asiento espejo en TGN/CGN/fiduciario/bancos y cualquier provisión o pago.
6. Mantener separados saldo de cuenta, reclamo, deuda firme, pago, daño y responsabilidad.
""", encoding="utf-8")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V181.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint":"V182","date":"2026-09-01","master_catalog_entries":697,"physical_local_copies":697,"physical_local_hash_ok":697,"remaining_catalog_physical_or_hash_gaps":0,
    "state":"BID1192_2018_REFERENCE_ACCOUNTS_2020_ZERO_UNCERTIFIED_CLOSURE_2021_PUBLICATION_EXIT_MY4002_IDENTIFIED_FINAL_ACT_LEDGER_PAYMENT_OPEN",
    "analytical_promotion":"ACCOUNT_AND_CLOSURE_TRANSITION_ONLY_NO_FIRM_DEBT_PAYMENT_DAMAGE_OR_LIABILITY_V182",
    "bid1192_my4002_identified":True,"bid1192_my4002_reference_usd":"15182.68","bid1192_my4002_reference_ars":"569350.57","bid1192_my4002_link_to_res1406_proved":False,
    "bid1192_2020_all_financial_fields_zero":True,"bid1192_2020_final_closure_certified":False,"bid1192_2021_absent_from_published_saf362":True,"bid1192_final_closure_act_located":False,
    "mypesii_res1406_infoleg_published_identity_match":False,"mypesii_res1406_full_act_located":False,"mypesii_res1406_payment_proved":False,"bid1192_damage_or_appropriation_proved":False,
    "sigen_archive_metadata_records_preserved":3,"sigen_archive_target_binaries_located":0,"requests_submitted":0,"responses_received":0,"new_v182_sources":13,"v182_pdf_documents":4,"v182_xlsx_documents":4,
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V182.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

origins = read_csv(ORIGINS)
by_path = {row["path"]: row for row in origins}
for path in iter_files(HIST_ROOT):
    note = "official/archival artifact preserved V182"
    if path.name == "cgn_account_2019_separata_i.pdf":
        note = "byte-identical duplicate of catalogued V177 source; local control copy"
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"downloaded/preserved V182","note":note}
for path in iter_files(SYNC):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V182","note":"13-source synchronization"}
for path in HERE.iterdir():
    if path.is_file():
        by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V182","note":"BID1192 account/closure/archive checkpoint"}
for path in (AUDIT/"MASTER_LOCAL_HASH_VALIDATION_V182.csv", AUDIT/"SOURCE_BACKUP_CENSUS_V182.csv", AUDIT/"SOURCE_PRESERVATION_MISSING_V182.csv", AUDIT/"CURRENT_SOURCE_COMPLETENESS_V182.json"):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V182","note":"697-source completeness"}
write_csv(ORIGINS, list(by_path.values()), ["path","origin","note"])

append_once(CYCLE / "TRANSPARENCY_README.md", "## V182 · MY4002 y transición de cierre BID 1192", """
## V182 · MY4002 y transición de cierre BID 1192

CGN individualiza MY4002 como Fondo Comisión de Compromiso dentro de saldos de referencia 2018; BID1192 figura todo en cero en 2020 pero con cierre definitivo aún no certificado y desaparece de los anexos publicados en 2021. Infoleg descarta por identidad la Resolución 1406/2014 publicada, que es laboral. No se promueven saldo, reclamo, deuda, pago, daño o responsabilidad. Archivo 697/697; solicitudes 0.
""")
(REPO / "BACKUP_ACTUALIZACION_2026-09-01.md").write_text("""# Backup de actualización · 2026-09-01

- V182; 697/697 fuentes catalogadas; 13 nuevas.
- MY4002: Fondo Comisión de Compromiso; referencia 2018 USD 15.182,68 / ARS 569.350,57; no es deuda ni pago probado.
- BID1192 2020: todo en cero, cierre definitivo no certificado.
- BID1192 2021: ausente de anexos SAF362/cuentas bancarias publicados; acto de cierre abierto.
- Res. 1406 publicada en Infoleg descartada: acto laboral ajeno a MyPES.
- Daño no probado; panel 34; cobertura 63,440604%; solicitudes enviadas 0.
""", encoding="utf-8")

(SYNC / "SOURCE_SYNC_REPORT_V182.md").write_text("""# Source sync V182

- 13 fuentes nuevas catalogadas y verificadas por SHA-256.
- 1 copia CGN 2019 byte idéntica a V177 conservada como control, sin duplicar el catálogo.
- CGN 2020/2021, Infoleg, SIGEN ArchivoWeb y controles Wayback preservados.
- 697/697 fuentes físicas válidas; faltantes físicos/hash: 0.
""", encoding="utf-8")
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V182.csv", [
    {"id":"PS182_01","endpoint":"CGN Cuenta 2020 SAF362","result":"BID1192 all zero; closure uncertified","preserved":"YES","limit":"zero is not final legal closure"},
    {"id":"PS182_02","endpoint":"CGN Cuenta 2021 SAF362/banks","result":"BID1192/MyPES identifiers absent","preserved":"YES","limit":"absence is not closure act"},
    {"id":"PS182_03","endpoint":"Infoleg Res1406/2014","result":"labor resolution; identity mismatch","preserved":"YES","limit":"does not locate internal MyPES act"},
    {"id":"PS182_04","endpoint":"SIGEN ArchiveWeb 201921/204917/207827","result":"metadata visible; binaries absent","preserved":"YES","limit":"interface layer only"},
    {"id":"PS182_05","endpoint":"Wayback CDX SIGEN","result":"one irrelevant CNRT capture","preserved":"YES","limit":"incomplete archive coverage"},
])
(SYNC / "qa_source_sync_v182.py").write_text("""from pathlib import Path
import csv
R=Path(__file__).resolve().parents[5]
rows=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==697 and len({x['id'] for x in rows})==697
print('SOURCE SYNC V182 PASS · 13 new · 697/697')
""", encoding="utf-8")

(HERE / "qa_v182.py").write_text("""from pathlib import Path
import csv,hashlib,json
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==697
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V182.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==697 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V182.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V182' and co['master_catalog_entries']==697
assert co['bid1192_my4002_identified'] and not co['bid1192_my4002_link_to_res1406_proved']
assert co['bid1192_2020_all_financial_fields_zero'] and not co['bid1192_2020_final_closure_certified']
assert co['bid1192_2021_absent_from_published_saf362'] and not co['bid1192_final_closure_act_located']
assert not co['mypesii_res1406_infoleg_published_identity_match'] and not co['mypesii_res1406_payment_proved'] and not co['bid1192_damage_or_appropriation_proved']
assert len(rows('V182_SOURCE_BUNDLE.csv'))==14 and len(rows('V182_PDF_VISUAL_CONTROL.csv'))==4 and len(rows('V182_XLSX_CONTENT_CONTROL.csv'))==4
assert len(rows('V182_HTML_CONTENT_CONTROL.csv'))==4 and len(rows('V182_JSON_CONTENT_CONTROL.csv'))==2
assert len(rows('E0_BID1192_CGN_TRANSITION_2018_2021_V182.csv'))==4 and len(rows('E0_BID1192_ACCOUNT_BALANCES_REFERENCE_2018_V182.csv'))==16
assert len(rows('E0_BID1192_MY4002_EVIDENCE_LADDER_V182.csv'))==5 and len(rows('E0_RES1406_IDENTITY_AND_ARCHIVE_CONTROL_V182.csv'))==5
obj=rows('E0_V182_REQUEST_OBJECTS.csv'); assert {'RO182_77','RO182_78','RO182_79'}<={x['row_id'] for x in obj}; assert all(x['status']=='DRAFT_NOT_SENT' for x in obj); assert obj==rows('E0_V182_REQUEST_OBJECTS_V182.csv')
panel=rows('FOUR_LEG_PASS_PANEL_V182.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
m=json.loads((H/'MANIFEST_V182.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V182' and m['parent_checkpoint']=='V181' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V182 QA PASS · 697/697 · MY4002=REFERENCE_ONLY · 2020_ZERO_CLOSURE_UNCERTIFIED · 2021_EXIT_PUBLICATION_ONLY · damage=NO · requests=0')
""", encoding="utf-8")

# Refresco final de procedencia después de crear sincronización y QA.
origins = read_csv(ORIGINS)
by_path = {row["path"]: row for row in origins}
for path in iter_files(SYNC):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V182","note":"13-source synchronization"}
for path in HERE.iterdir():
    if path.is_file():
        by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V182","note":"BID1192 account/closure/archive checkpoint"}
write_csv(ORIGINS, list(by_path.values()), ["path","origin","note"])

(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")

manifest_files = [{"path":path.name,"bytes":path.stat().st_size,"sha256":sha(path)} for path in sorted(HERE.iterdir(), key=lambda item:item.name.casefold()) if path.is_file() and path.name != "MANIFEST_V182.json"]
manifest = {
    "checkpoint":"V182","parent_checkpoint":"V181","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
    "exact_entities":34,"strict_coverage_pct":COVERAGE,"strict_asset_numerator_million_ars":NUMERATOR,"system_assets_million_ars":ASSETS,
    "new_promotions":[],"source_archive":"697/697; 13 new catalogued sources; one byte-identical duplicate control",
    "historical_finding":"MY4002 identified; BID1192 zero but uncertified in 2020 and absent in 2021 publication; act/ledger/payment/damage open",
    "mypesii_my4002":"REFERENCE_ACCOUNT_NOT_DEBT_OR_PAYMENT","bid1192_2020":"ZERO_CLOSURE_UNCERTIFIED","bid1192_2021":"PUBLICATION_EXIT_ONLY",
    "mypesii_res1406":"INFOLEG_IDENTITY_MISMATCH_INTERNAL_ACT_OPEN","closed_network_gate":"NO","saf355_certifications":"0/5","executed_historical_bank_rows":"0/10","requests_submitted":0,"files":manifest_files,
}
(HERE / "MANIFEST_V182.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path":path.relative_to(REPO).as_posix(),"bytes":path.stat().st_size,"sha256":sha(path)} for path in iter_files(REPO) if path != global_manifest]
payload = {"checkpoint":"V182","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),"strict_coverage_pct":COVERAGE,"exact_entities":34,"closed_network_gate":"NO","source_audit":"697 master; 697 physical SHA-valid","historical_workstream":"MY4002/account/closure/archive transition reconstructed; debt/payment/damage open; drafts not sent","file_count_excluding_manifest":len(global_files),"files":global_files}
temporary = global_manifest.with_suffix(".json.V182tmp")
temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
temporary.replace(global_manifest)
print("V182 BUILD PASS · catalog=697/697 · new=13 · MY4002=REFERENCE_ONLY · 2020=ZERO_UNCERTIFIED · 2021=ABSENT_PUBLICATION · requests=0")
