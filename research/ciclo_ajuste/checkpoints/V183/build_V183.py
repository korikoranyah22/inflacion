from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import csv
import hashlib
import json
import os


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
PARENT = CYCLE / "checkpoints" / "V182"
AUDIT = CYCLE / "source_audit"
SYNC = CYCLE / "inputs" / "source_sync" / "v183"
HIST_ROOT = CYCLE / "inputs" / "historical_retrieval" / "v183"
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
        "MANIFEST_V182.json", "README_V182.md", "VEREDICTO_V182.md", "AUDITORIA_V182.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V182_A_V183.md", "V182_SOURCE_BUNDLE.csv",
        "V182_PUBLIC_SEARCH_LOG.csv", "V182_PDF_VISUAL_CONTROL.csv", "V182_PDF_TEXT_CONTROL.csv",
        "V182_XLSX_CONTENT_CONTROL.csv", "V182_HTML_CONTENT_CONTROL.csv", "V182_JSON_CONTENT_CONTROL.csv",
        "CORRECTION_LOG_V182.md",
    }
    HERE.mkdir(parents=True, exist_ok=True)
    for source in sorted(PARENT.iterdir(), key=lambda path: path.name.casefold()):
        if not source.is_file() or source.name in skip or source.name.startswith(("build_", "qa_")):
            continue
        target = HERE / source.name.replace("V182", "V183")
        target.write_bytes(source.read_bytes())


SOURCE_SPECS = [
    {
        "id":"e0_cgn_account2005_separata_my4002_negative_boundary_v183",
        "title":"Cuenta de Inversión 2005 · Separata · límite negativo MY4002",
        "url":"https://www.economia.gob.ar/hacienda/cgn/cuenta/2005/archivos/sep.pdf",
        "file":"cgn_cuenta_inversion_2005_separata.pdf", "published":"2006", "period":"2005",
        "note":"La búsqueda textual integral no localiza MY4002. La ausencia no prueba inexistencia; las Cuentas 2006/2007 dicen retrospectivamente que el saldo informado al cierre 2005 era cero.",
    },
    {
        "id":"e0_cgn_account2006_my4002_retrospective_zero_v183",
        "title":"Cuenta de Inversión 2006 · MY4002 retrospectivo en cero",
        "url":"https://www.economia.gob.ar/hacienda/cgn/cuenta/2006/archivos/sep.pdf",
        "file":"cgn_cuenta_inversion_2006_separata.pdf", "published":"2007", "period":"2005-2006",
        "note":"Página PDF 116: MY4002 aparece en cero; el programa no presentó información 2006 y se expusieron saldos al 31/12/2005.",
    },
    {
        "id":"e0_cgn_account2007_my4002_retrospective_zero_v183",
        "title":"Cuenta de Inversión 2007 · MY4002 retrospectivo en cero",
        "url":"https://www.economia.gob.ar/hacienda/cgn/cuenta/2007/archivos/Sep2017.pdf".replace("2017/archivos/Sep2017", "2007/archivos/sep"),
        "file":"cgn_cuenta_inversion_2007_separata.pdf", "published":"2008", "period":"2005-2007",
        "note":"Página PDF 125: MY4002 aparece en cero; no hubo información financiera 2007 y se arrastró la última presentación, correspondiente a 2005.",
    },
    {
        "id":"e0_cgn_account2010_my4002_account_row_v183",
        "title":"Cuenta de Inversión 2010 · fila MY4002 conciliada con extracto",
        "url":"https://www.economia.gob.ar/hacienda/cgn/cuenta/2010/archivos/sep.pdf",
        "file":"cgn_cuenta_inversion_2010_separata.pdf", "published":"2011", "period":"2010",
        "note":"Página PDF 194: MY4002 termina en ARS 52.580,35 y moneda extranjera 13.358,83, igual al saldo según extracto; no identifica contraparte del movimiento.",
    },
    {
        "id":"e0_cgn_account2017_my4002_stable_foreign_balance_v183",
        "title":"Cuenta de Inversión 2017 · MY4002 estable en moneda extranjera",
        "url":"https://www.mecon.gob.ar/hacienda/cgn/cuenta/2017/archivos/Sep2017.pdf",
        "file":"cgn_cuenta_inversion_2017_separata.pdf", "published":"2018", "period":"2017",
        "note":"Página PDF 245: MY4002 pasa de ARS 214.504,78 a 251.985,38, mientras el saldo en moneda extranjera y según extracto permanece en 13.584,85.",
    },
    {
        "id":"e0_cgn_account2018_my4002_uepex_zero_unsupported_reconstruction_v183",
        "title":"Cuenta de Inversión 2018 · MY4002: UEPEX cero y reconstrucción no respaldada",
        "url":"https://www.mecon.gob.ar/hacienda/cgn/cuenta/2018/archivos/Separata%20Ejecucion%20Presupuestaria%202018.pdf",
        "file":"cgn_cuenta_inversion_2018_separata.pdf", "published":"2019", "period":"2018",
        "note":"Página PDF 249: registros exponen ARS 569.350,57 / ME 15.182,68, pero UEPEX declaró cero y el resumen aportado carecía de membrete, sello bancario y fecha verificable; no es extracto BCRA ni prueba de pago bancario.",
    },
]


clone_parent()
SYNC.mkdir(parents=True, exist_ok=True)
for spec in SOURCE_SPECS:
    assert (HIST / spec["file"]).is_file(), spec["file"]

catalog = read_csv(CATALOG)
catalog_fields = list(catalog[0])
by_id = {row["id"]: row for row in catalog}
note_2008 = " V183 usa la fila MY4002: saldo final contable ME 9.332,28 frente a extracto 10.186,68; CGN advierte incoherencias, falta de extracto y tipos de cambio de referencia."
if note_2008.strip() not in by_id["e0_cgn_account_2008_uepex_closing_exception"]["nota"]:
    by_id["e0_cgn_account_2008_uepex_closing_exception"]["nota"] += note_2008
note_2009 = " V183 usa la fila MY4002: saldo final contable ME 12.195,51 frente a extracto 12.305,78; CGN documenta inconsistencias de fórmula y tipo de cambio."
if note_2009.strip() not in by_id["e0_cgn_account_2009_uepex_2008_note_sisio_chain"]["nota"]:
    by_id["e0_cgn_account_2009_uepex_2008_note_sisio_chain"]["nota"] += note_2009

new_sources = []
for spec in SOURCE_SPECS:
    path = HIST / spec["file"]
    row = {
        "id":spec["id"], "tema":"ciclo_ajuste_e0_fiscal", "institucion":"Contaduría General de la Nación",
        "titulo":spec["title"], "url_original":spec["url"],
        "archivo_local":"/" + path.relative_to(REPO).as_posix(), "fecha_descarga":"2026-09-01",
        "fecha_publicacion":spec["published"], "codigo_serie":spec["title"], "periodo_utilizado":spec["period"],
        "tipo":"PDF oficial preservado · extracción estructurada y control visual", "sha256":sha(path), "nota":spec["note"],
    }
    by_id[row["id"]] = row
    new_sources.append(row)
catalog = list(by_id.values())
write_csv(CATALOG, catalog, catalog_fields)
assert len(catalog) == len({row["id"] for row in catalog}) == 703

audit = []
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    actual = sha(path) if path.is_file() else ""
    audit.append({"id":row["id"],"archivo_local":row["archivo_local"],"exists":str(path.is_file()),"sha_catalog":row["sha256"].lower(),"sha_actual":actual,"hash_ok":str(path.is_file() and bool(row["sha256"]) and actual == row["sha256"].lower())})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V183.csv", audit)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V183.csv", audit)
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V183.csv", [row for row in audit if row["hash_ok"] != "True"], list(audit[0]))
assert all(row["hash_ok"] == "True" for row in audit)

series_raw = [
    (2006,"0.00","0.00","0.00","0.00","0.00","0.00","0.00","RETROSPECTIVE_2005_ZERO_NO_2006_INFORMATION","Cuenta 2006 PDF 116"),
    (2007,"0.00","0.00","0.00","0.00","0.00","0.00","0.00","RETROSPECTIVE_2005_ZERO_NO_2007_INFORMATION","Cuenta 2007 PDF 125"),
    (2008,"21619.80","6953.94","10231.26","0.00","31851.06","9332.28","10186.68","INCONSISTENT_NO_EXTRACT_REFERENCE_FX","Cuenta 2008 PDF 118"),
    (2009,"34767.14","10186.68","11314.45","226.46","45855.13","12195.51","12305.78","INCONSISTENT_FORMULA_AND_FX","Cuenta 2009 PDF 143"),
    (2010,"46269.73","12305.78","6310.62","0.00","52580.35","13358.83","13358.83","TABLE_TIES_EXTRACT_COUNTERPARTY_OPEN","Cuenta 2010 PDF 194"),
    (2011,"52580.35","13358.83","5301.53","0.00","57881.88","13574.55","13574.55","TABLE_TIES_EXTRACT_COUNTERPARTY_OPEN","Cuenta 2011 PDF 201"),
    (2012,"57881.88","13574.55","8385.02","0.00","66266.90","13584.85","13584.85","TABLE_TIES_EXTRACT_COUNTERPARTY_OPEN","Cuenta 2012 PDF 223"),
    (2013,"66266.90","13584.85","21776.51","0.00","88043.41","13584.85","13584.85","ME_STABLE_PESO_REMEASUREMENT","Cuenta 2013 PDF 220"),
    (2014,"88043.41","13584.85","26762.16","0.00","114805.57","13584.85","13584.85","ME_STABLE_PESO_REMEASUREMENT","Cuenta 2014 PDF 223"),
    (2015,"114805.57","13584.85","0.00","0.00","175787.96","13584.85","13584.85","ARITHMETIC_GAP_OR_UNSHOWN_VALUATION","Cuenta 2015 PDF 220"),
    (2016,"175787.96","13584.85","38716.82","0.00","214504.78","13584.85","13584.85","ME_STABLE_PESO_REMEASUREMENT","Cuenta 2016 PDF 160"),
    (2017,"214504.78","13584.85","37480.60","0.00","251985.38","13584.85","13584.85","ME_STABLE_PESO_REMEASUREMENT","Cuenta 2017 PDF 245"),
    (2018,"251985.38","13584.85","330950.04","13584.85","569350.57","15182.68","0.00","UEPEX_ZERO_CGN_RECONSTRUCTION_WITHOUT_BANK_IDENTIFIABLE_SUPPORT","Cuenta 2018 PDF 249"),
]
series = []
for year, opening_ars, opening_me, debit, credit, closing_ars, closing_me, extract_me, status, source in series_raw:
    oa, om, de, cr, ca, cm, ex = map(Decimal, (opening_ars, opening_me, debit, credit, closing_ars, closing_me, extract_me))
    series.append({
        "year":str(year),"opening_ars":str(oa),"opening_foreign":str(om),"debit_ars":str(de),"credit_ars":str(cr),
        "closing_ars":str(ca),"closing_foreign":str(cm),"extract_foreign":str(ex),
        "ars_identity_gap":str(ca - (oa + de - cr)),"closing_vs_extract_foreign_gap":str(cm - ex),
        "implied_closing_ars_per_foreign":str((ca / cm).quantize(Decimal("0.000001"))) if cm else "",
        "evidence_status":status,"source":source,"legal_limit":"cuenta/valuación no identifica pagador, acto, deuda firme, pago, daño o responsabilidad",
    })
write_csv(HERE / "E0_BID1192_MY4002_ACCOUNT_SERIES_2006_2018_V183.csv", series)

start_2012 = Decimal("66266.90")
end_2017 = Decimal("251985.38")
write_csv(HERE / "E0_BID1192_MY4002_DECOMPOSITION_V183.csv", [
    {"phase":"2005-2007","proved":"Cuentas 2006/2007 arrastran saldo MY4002 cero de 2005 por falta de información corriente","calculation":"0","interpretation":"límite retrospectivo","not_proved":"estado bancario efectivo 2006/2007"},
    {"phase":"2008-2009","proved":"la cuenta reaparece con valores, pero CGN documenta falta de extracto, tipo de cambio e inconsistencias","calculation":"extracto-contable ME: 854.40 en 2008; 110.27 en 2009","interpretation":"actividad no conciliada","not_proved":"contraparte y naturaleza de cada ingreso"},
    {"phase":"2010-2012","proved":"saldo contable en ME coincide con columna extracto y sube 13,358.83→13,584.85","calculation":"+226.02 ME","interpretation":"acumulación pequeña con contraparte abierta","not_proved":"Macro/Credicoop como pagadores"},
    {"phase":"2012-2017","proved":"ME queda exactamente en 13,584.85 mientras ARS sube","calculation":f"ARS +{end_2017-start_2012}; factor {(end_2017/start_2012).quantize(Decimal('0.000001'))}","interpretation":"crecimiento nominal compatible con reexpresión cambiaria, no con nuevo principal en ME","not_proved":"mayor contable y norma de valuación"},
    {"phase":"2015","proved":"debe/haber publicados son cero pero ARS final sube 60,982.39","calculation":"175787.96-114805.57=60982.39","interpretation":"movimiento de valuación omitido o inconsistencia del cuadro","not_proved":"asiento subyacente"},
    {"phase":"2018","proved":"CGN reconstruye ARS 569,350.57 / ME 15,182.68; UEPEX declaró cero; respaldo no identificable como BCRA","calculation":"251985.38+330950.04-13584.85=569350.57","interpretation":"aritmética reproducible, existencia bancaria no certificada","not_proved":"extracto, pago, contraparte o vínculo Res1406"},
    {"phase":"2019-2021","proved":"Cuenta 2019 repite referencia 2018; 2020 todo cero sin cierre certificado; 2021 ausencia publicada","calculation":"transición documental","interpretation":"cierre operativo compatible, cierre jurídico abierto","not_proved":"acto, destino y extinción"},
])

write_csv(HERE / "E0_BID1192_MY4002_CLAIM_SEPARATION_V183.csv", [
    {"level":"1","proposition":"existió un identificador contable MY4002 denominado Fondo Comisión de Compromiso","status":"SUPPORTED","proof":"serie CGN 2006-2018","missing":"ninguno para identidad contable"},
    {"level":"2","proposition":"hubo valores/movimientos contables en esa cuenta","status":"SUPPORTED_WITH_CONTROL_BREAKS","proof":"filas 2008-2018","missing":"mayor y respaldos de 2008/2009/2015/2018"},
    {"level":"3","proposition":"el saldo 2018 estaba efectivamente depositado en BCRA","status":"NOT_PROVED","proof":"CGN reconstruye valor, pero columna extracto es cero","missing":"extracto BCRA con membrete, sello, fecha y cuenta"},
    {"level":"4","proposition":"los movimientos provinieron de Macro o Credicoop","status":"NOT_PROVED","proof":"ninguna fila identifica contraparte","missing":"transferencia, recibo y asiento espejo"},
    {"level":"5","proposition":"MY4002 era la liquidación de la Resolución 1406","status":"NOT_PROVED","proof":"coincidencia nominal solamente","missing":"asiento con expediente, acto, cálculo y concepto"},
    {"level":"6","proposition":"existió deuda firme o pago extinguidor","status":"NOT_PROVED","proof":"SIGEN reporta recursos pendientes y liquidación irresuelta","missing":"decisión final, notificación, pago y cierre"},
    {"level":"7","proposition":"existió daño resarcible o responsabilidad de bancos/funcionarios","status":"NOT_PROVED","proof":"sin contrafáctico ni nexo causal cerrado","missing":"pericia, expediente completo y cuantificación jurídica"},
])

write_csv(HERE / "E0_BID1192_SIGEN_RECURRENCE_STATUS_CONTROL_V183.csv", [
    {"compilation":"SIGEN octubre 2017","underlying_statement":"Res1406 noviembre 2014; intimación a Macro/Credicoop; recursos de bancos y fiduciario; liquidación no resuelta","recurrence_flag":"SI","corrective_action":"sin solución acreditada","meaning":"observación recurrente en esa compilación"},
    {"compilation":"SIGEN febrero 2019","underlying_statement":"mismo texto sobre Res1406, recursos y liquidación no resuelta","recurrence_flag":"NO","corrective_action":"Sin acción correctiva","meaning":"cambio de bandera compilatoria; no decisión de fondo"},
])
write_csv(HERE / "E0_BID1192_RES1406_CUSTODY_ROUTE_V183.csv", [
    {"route_step":"hecho reportado","custodian_or_area":"área auditada MyPES II","record":"Resolución 1406 de noviembre 2014 e intimaciones","evidence":"cita reproducida por SIGEN","limit":"acto y notificaciones no recuperados"},
    {"route_step":"unidad organizativa posterior","custodian_or_area":"Secretaría de Emprendedores y de la Pequeña y Mediana Empresa · Ministerio de Producción","record":"cierre/liquidación MyPES II","evidence":"encabezado de observación SIGEN","limit":"sucesión documental por verificar"},
    {"route_step":"recursos","custodian_or_area":"Asuntos Jurídicos del Ministerio","record":"reconsideración con jerárquico en subsidio de bancos y fiduciario","evidence":"texto informado por área auditada","limit":"dictámenes y decisión no públicos"},
    {"route_step":"control externo","custodian_or_area":"SIGEN","record":"observación Cuenta 2016/2017","evidence":"dos compilaciones oficiales","limit":"SIGEN no certifica deuda ni pago"},
])

requests = read_csv(HERE / "E0_V183_REQUEST_OBJECTS.csv")
requests += [
    {"row_id":"RO183_80","object_id":"MY4002_COMPLETE_LEDGER_2008_2018","custodian":"SAF362 · CGN · TGN · BCRA","exact_record":"mayor, asientos, extractos y conciliaciones MY4002","period":"2008-2018","minimum_fields":"fecha; moneda; debe; haber; saldo; contraparte; comprobante; expediente; valuación","closure_rule":"conciliar cada fila anual y explicar gaps 2008, 2009, 2015 y 2018","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO183_81","object_id":"MY4002_2018_BCRA_SUPPORT","custodian":"SAF362 · BCRA · CGN","exact_record":"resumen remitido por UEPEX y extracto/certificación BCRA al 31/12/2018","period":"2018","minimum_fields":"membrete; sello; fecha; cuenta; moneda; saldo; firmante; hash; expediente","closure_rule":"confirmar o descartar ARS 569350.57 / ME 15182.68 con documento bancario identificable","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO183_82","object_id":"RES1406_FULL_APPEAL_DECISION_PACKAGE","custodian":"Ministerio de Producción/Economía · Asuntos Jurídicos · Secretaría PyME","exact_record":"Res1406 noviembre 2014, expediente, intimaciones, recursos, dictámenes y decisión","period":"2014-cierre","minimum_fields":"autoridad; fecha; monto; fórmula; bancos; fiduciario; notificación; recurso; dictamen; decisión; pago","closure_rule":"separar pretensión, deuda firme, pago y extinción por documento","status":"DRAFT_NOT_SENT"},
]
write_csv(HERE / "E0_V183_REQUEST_OBJECTS.csv", requests)
write_csv(HERE / "E0_V183_REQUEST_OBJECTS_V183.csv", requests)

keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V183.csv")
keys += [
    {"key_id":"SK183_79","request_id":"RO183_80","key_group":"account","exact_key":"MY 4002; Fondo Comisión de Compromiso; 13584.85; 15182.68","search_purpose":"recuperar mayor y asientos","source_or_basis":"Cuentas 2008-2018","caveat":"saldo no identifica contraparte"},
    {"key_id":"SK183_80","request_id":"RO183_81","key_group":"bank_support","exact_key":"569350.57; 15182.68; 31/12/18; BCRA; UEPEX","search_purpose":"certificar saldo 2018","source_or_basis":"Cuenta 2018 PDF 249","caveat":"resumen sin referencia bancaria"},
    {"key_id":"SK183_81","request_id":"RO183_82","key_group":"administrative_file","exact_key":"Resolución 1406; noviembre 2014; comisión de compromiso; Macro; Credicoop; reconsideración; jerárquico","search_purpose":"recuperar expediente integral","source_or_basis":"SIGEN 2017/2019","caveat":"no confundir con Res ST 1406/2014 laboral"},
]
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V183.csv", keys)

write_csv(HERE / "V183_PUBLIC_SEARCH_LOG.csv", [
    {"query_id":"PS183_01","query":"Notas 04854651SSFP#MP/2017 y 7813292/SSFP#MP/2017 + variantes GDE","result":"sólo informe SIGEN indexado","limit":"cuerpos y anexos no localizados"},
    {"query_id":"PS183_02","query":"Resolución 1406 noviembre 2014 Macro Credicoop comisión compromiso","result":"sólo dos compilaciones SIGEN oficiales","limit":"acto interno/no publicado abierto"},
    {"query_id":"PS183_03","query":"Cuenta de Inversión 2005-2018 MY4002","result":"rutas históricas oficiales localizadas; seis fuentes nuevas y un duplicado exacto preservados","limit":"filas contables no sustituyen mayores/extractos"},
    {"query_id":"PS183_04","query":"Cuenta 2017/2018 menú histórico CGN","result":"Sep2017.pdf y Separata Ejecucion Presupuestaria 2018.pdf localizados por menu.js oficial","limit":"servidor con certificado histórico vencido"},
])

duplicate_2008 = HIST / "cgn_cuenta_inversion_2008_separata.pdf"
existing_2008 = REPO / by_id["e0_cgn_account_2008_uepex_closing_exception"]["archivo_local"].lstrip("/")
assert sha(duplicate_2008) == sha(existing_2008)
bundle = []
for row in new_sources:
    path = REPO / row["archivo_local"].lstrip("/")
    bundle.append({"source_id":row["id"],"file":path.name,"bytes":path.stat().st_size,"sha256":sha(path),"status":"CATALOGUED_SHA_VALID"})
bundle.append({"source_id":"duplicate_of_e0_cgn_account_2008_uepex_closing_exception","file":duplicate_2008.name,"bytes":duplicate_2008.stat().st_size,"sha256":sha(duplicate_2008),"status":"BYTE_IDENTICAL_DUPLICATE_NOT_NEW_CATALOG_ROW"})
write_csv(HERE / "V183_SOURCE_BUNDLE.csv", bundle)
write_csv(HERE / "V183_PDF_VISUAL_CONTROL.csv", [
    {"file":"cgn_cuenta_inversion_2006_separata.pdf","pages":"116","result":"PASS_MY4002_RETROSPECTIVE_ZERO"},
    {"file":"cgn_cuenta_inversion_2007_separata.pdf","pages":"125","result":"PASS_MY4002_RETROSPECTIVE_ZERO"},
    {"file":"cgn_cuenta_inversion_2008_separata.pdf","pages":"118","result":"PASS_MY4002_INCONSISTENT_NO_EXTRACT"},
    {"file":"cgn_cuenta_2009_uepex_note_sisio_chain.pdf","pages":"143","result":"PASS_MY4002_FORMULA_AND_FX_WARNING"},
    {"file":"cgn_cuenta_inversion_2010_separata.pdf","pages":"194","result":"PASS_MY4002_TIES_EXTRACT"},
    {"file":"cgn_cuenta_inversion_2017_separata.pdf","pages":"245","result":"PASS_MY4002_ME_STABLE"},
    {"file":"cgn_cuenta_inversion_2018_separata.pdf","pages":"249","result":"PASS_UEPEX_ZERO_UNSUPPORTED_RECONSTRUCTION"},
])
write_csv(HERE / "V183_PDF_TEXT_CONTROL.csv", [
    {"file":"cgn_cuenta_inversion_2005_separata.pdf","pages_scanned":"115","needle":"MY4002 / Fondo Comisión de Compromiso","result":"NO_MATCH_SCOPE_LIMIT_ONLY"},
    {"file":"cgn_cuenta_inversion_2006_separata.pdf","pages_scanned":"118","needle":"MY 4002","result":"MATCH_PDF_116"},
    {"file":"cgn_cuenta_inversion_2007_separata.pdf","pages_scanned":"128","needle":"MY 4002","result":"MATCH_PDF_125"},
    {"file":"cgn_cuenta_inversion_2008_separata.pdf","pages_scanned":"122","needle":"MY 4002","result":"MATCH_PDF_118"},
    {"file":"cgn_cuenta_inversion_2010_separata.pdf","pages_scanned":"197","needle":"MY 4002","result":"MATCH_PDF_194"},
    {"file":"cgn_cuenta_inversion_2017_separata.pdf","pages_scanned":"254","needle":"MY 4002","result":"MATCH_PDF_245"},
    {"file":"cgn_cuenta_inversion_2018_separata.pdf","pages_scanned":"284","needle":"MY 4002","result":"MATCH_PDF_249"},
])

archival = read_csv(HERE / "ARCHIVAL_PROVENANCE_V183.csv")
for row in new_sources:
    path = REPO / row["archivo_local"].lstrip("/")
    archival.append({"source_id":row["id"],"original_url":row["url_original"],"retrieval_url":row["url_original"],"capture_timestamp":"2026-09-01","cdx_digest":"N/A_OFFICIAL_DIRECT_DOWNLOAD","local_path":row["archivo_local"],"sha256":row["sha256"],"bytes":path.stat().st_size,"provenance_note":row["nota"]})
write_csv(HERE / "ARCHIVAL_PROVENANCE_V183.csv", archival)

census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V183.csv")
for row in new_sources:
    path = REPO / row["archivo_local"].lstrip("/")
    census.append({"source_id":row["id"],"institution":row["institucion"],"artifact":row["titulo"],"url":row["url_original"],"local_path":row["archivo_local"],"sha256":row["sha256"],"bytes":path.stat().st_size,"period_coverage":row["periodo_utilizado"],"variable_families":"BID1192;MY4002;accounts;valuation;control","primary_source":"YES","preserved":"YES","method_breaks":"account table vs extract vs unsupported UEPEX summary","use_status":"USABLE_WITH_EXPLICIT_LIMIT","caveat":row["nota"]})
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V183.csv", census)

append_once(HERE / "SOURCE_REFERENCES_V183.md", "## V183 · serie MY4002 2005-2018", """
## V183 · serie MY4002 2005-2018

- Seis separatas CGN nuevas preservadas: 2005, 2006, 2007, 2010, 2017 y 2018; la copia 2008 es byte idéntica a una fuente V148 ya catalogada.
- MY4002: cero retrospectivo 2005; reaparición no conciliada 2008/2009; extracto coincidente 2010-2017; saldo ME estable 2012-2017; reconstrucción 2018 sin respaldo BCRA identificable.
- La serie prueba identidad y problemas de control. No prueba pagador, deuda firme, pago, daño ni vínculo con Res1406.
""")
append_once(HERE / "RETRIEVAL_LOG_V183.md", "## V183 · búsqueda 2026-09-01", """
## V183 · búsqueda 2026-09-01

- Recuperadas rutas históricas oficiales de las separatas 2005-2018 mediante los menús CGN.
- Las notas 04854651 y 7813292/2017 y el acto MyPES Res1406 siguen sin cuerpo público localizado.
- Solicitudes enviadas: 0; tres objetos de evidencia quedaron DRAFT_NOT_SENT.
""")

(HERE / "README_V183.md").write_text("""# Checkpoint V183

## Hallazgo principal

V183 reconstruye la serie anual de `MY 4002 – Fondo Comisión de Compromiso` entre el cero retrospectivo de 2005 y la publicación 2018. El resultado corrige una lectura tentadora pero incorrecta: los ARS 569.350,57 de 2018 no son, por sí solos, un pago de Macro o Credicoop ni una deuda firme.

Entre 2012 y 2017 el saldo en moneda extranjera permanece exactamente en 13.584,85, mientras su equivalente en pesos pasa de ARS 66.266,90 a 251.985,38. Ese crecimiento nominal es compatible con reexpresión cambiaria, no con un nuevo ingreso de capital en moneda extranjera. En 2015, además, el cuadro muestra debe/haber cero pero un aumento de ARS 60.982,39: falta el asiento de valuación o existe una inconsistencia.

La Cuenta 2018 exhibe ARS 569.350,57 / ME 15.182,68, pero la propia CGN dice que la UEPEX declaró saldo cero y aportó un resumen sin membrete, sello bancario ni fecha que permitiera atribuirlo al BCRA. La aritmética se reproduce; la existencia bancaria y la contraparte no están certificadas.

## Consecuencia probatoria

- Identidad y existencia histórica de MY4002: probadas.
- Movimientos/valuaciones contables: probados con quiebres de control explícitos.
- Saldo bancario BCRA al 31/12/2018: no probado.
- Pago de Macro/Credicoop, vínculo con Res1406, deuda firme, daño o responsabilidad: no probados.
- Archivo: 703/703 fuentes catalogadas con SHA-256 válido; seis nuevas y un duplicado exacto conservado como control.
- Solicitudes enviadas: 0.
""", encoding="utf-8")

(HERE / "VEREDICTO_V183.md").write_text("""# Veredicto V183

MY4002 es una pista contable real y persistente, pero no es todavía el puente jurídico hacia la intimación de 2014. La mejor afirmación defendible es que existió una cuenta estatal destinada a “Comisión de Compromiso”, con saldos y reexpresiones publicados, y que su control documental fue defectuoso en 2008/2009, aritméticamente incompleto en 2015 y no bancariamente identificable en 2018. Para promoverlo a pago de las IFI o a liquidación Res1406 hacen falta mayor, extractos, contrapartes, comprobantes y asiento con expediente. Hasta entonces, saldo contable, reclamo, deuda firme, pago, daño y responsabilidad permanecen separados.
""", encoding="utf-8")

(HERE / "AUDITORIA_V183.md").write_text("""# Auditoría V183

- 703/703 fuentes catalogadas, físicas y SHA-256 válidas; seis nuevas.
- Un PDF 2008 descargado en V183 es byte idéntico a la copia catalogada V148; no duplica el catálogo.
- Siete páginas relevantes controladas visualmente; siete PDF sometidos a búsqueda textual integral.
- Serie MY4002: 13 cortes 2006-2018 con identidad aritmética, brecha contra extracto e índice de valuación reproducibles.
- Quiebres: 2008/2009 inconsistencias CGN; 2015 gap ARS 60.982,39; 2018 UEPEX cero y respaldo no identificable como BCRA.
- Res1406: bandera “recurrente” cambia SI→NO entre compilaciones sin que el texto deje de decir liquidación irresuelta.
- Daño no probado; panel 34; cobertura 63,440604%; solicitudes enviadas 0.
""", encoding="utf-8")

(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V183_A_V184.md").write_text("""# Handover V183 → V184

## Cerrado

- Serie MY4002 2005-2018 reconstruida y controlada visualmente.
- Separación entre saldo en moneda extranjera, equivalente en pesos, extracto y reconstrucción CGN formalizada.
- Quiebres 2008, 2009, 2015 y 2018 cuantificados.
- Bandera SIGEN de recurrencia separada del estado jurídico de la liquidación.
- Seis nuevas separatas oficiales preservadas; archivo 703/703.

## Prioridad V184

1. Recuperar mayor/asientos/extractos MY4002 y respaldo BCRA de 2018.
2. Recuperar Res1406, expediente, intimaciones, recursos, dictámenes y decisión final.
3. Recuperar Notas SSFP 04854651 y 7813292/2017 con anexos.
4. Obtener certificado de cierre BID1192 y conciliar el cero 2020 con las cuentas históricas.
5. Recuperar adjuntos SIGEN 2018-2020 por IdDocumento/IdA.
6. Mantener separados cuenta, valuación, reclamo, deuda firme, pago, daño y responsabilidad.
""", encoding="utf-8")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V182.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint":"V183","date":"2026-09-01","master_catalog_entries":703,"physical_local_copies":703,"physical_local_hash_ok":703,"remaining_catalog_physical_or_hash_gaps":0,
    "state":"MY4002_2005_2018_SERIES_RECONSTRUCTED_2018_BANK_SUPPORT_UNVERIFIED_RES1406_LEDGER_PAYMENT_DAMAGE_OPEN",
    "analytical_promotion":"ACCOUNT_SERIES_AND_CONTROL_BREAKS_ONLY_NO_FIRM_DEBT_PAYMENT_DAMAGE_OR_LIABILITY_V183",
    "my4002_series_2006_2018_rows":13,"my4002_foreign_balance_stable_2012_2017":True,"my4002_2015_arithmetic_gap_ars":"60982.39",
    "my4002_2018_cgn_reconstructed_ars":"569350.57","my4002_2018_cgn_reconstructed_foreign":"15182.68","my4002_2018_uepex_declared_zero":True,"my4002_2018_bcra_identifiable_support":False,
    "my4002_counterparty_proved":False,"bid1192_my4002_link_to_res1406_proved":False,"mypesii_res1406_full_act_located":False,"mypesii_res1406_payment_proved":False,"bid1192_damage_or_appropriation_proved":False,
    "requests_submitted":0,"responses_received":0,"new_v183_sources":6,"v183_pdf_visual_pages":7,
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V183.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

origins = read_csv(ORIGINS)
by_path = {row["path"]:row for row in origins}
for path in iter_files(HIST_ROOT):
    note = "official CGN separata preserved V183"
    if path.name == "cgn_cuenta_inversion_2008_separata.pdf":
        note = "byte-identical duplicate of catalogued V148 source; local control copy"
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"downloaded/preserved V183","note":note}
for path in HERE.iterdir():
    if path.is_file():
        by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V183","note":"MY4002 longitudinal account/control checkpoint"}
for path in (AUDIT/"MASTER_LOCAL_HASH_VALIDATION_V183.csv",AUDIT/"SOURCE_BACKUP_CENSUS_V183.csv",AUDIT/"SOURCE_PRESERVATION_MISSING_V183.csv",AUDIT/"CURRENT_SOURCE_COMPLETENESS_V183.json"):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V183","note":"703-source completeness"}
write_csv(ORIGINS, list(by_path.values()), ["path","origin","note"])

append_once(CYCLE / "TRANSPARENCY_README.md", "## V183 · serie MY4002 2005-2018", """
## V183 · serie MY4002 2005-2018

La serie CGN separa moneda extranjera, equivalente en pesos y extracto. MY4002 mantiene ME 13.584,85 entre 2012 y 2017; el crecimiento en pesos es reexpresión, no prueba de pago. En 2018 CGN reconstruye ARS 569.350,57 / ME 15.182,68, pero UEPEX declaró cero y el respaldo carecía de identificación bancaria verificable. No se promueven saldo, reclamo, deuda, pago, daño o responsabilidad. Archivo 703/703; solicitudes 0.
""")
(REPO / "BACKUP_ACTUALIZACION_2026-09-01.md").write_text("""# Backup de actualización · 2026-09-01

- V183; 703/703 fuentes catalogadas; seis nuevas.
- MY4002 reconstruida 2005-2018: ME estable 2012-2017; pesos reexpresados.
- Quiebres: 2008/2009 inconsistencias; 2015 gap ARS 60.982,39; 2018 UEPEX cero y respaldo no identificable como BCRA.
- ARS 569.350,57 / ME 15.182,68 es reconstrucción contable 2018, no pago bancario probado.
- Res1406, ledger, decisión, pago y daño abiertos; solicitudes enviadas 0.
""", encoding="utf-8")

(SYNC / "SOURCE_SYNC_REPORT_V183.md").write_text("""# Source sync V183

- Seis separatas CGN nuevas catalogadas; una copia 2008 byte idéntica preservada sin duplicar catálogo.
- 703/703 fuentes físicas y SHA-256 válidas; brecha 0.
- Serie MY4002 2005-2018 y límites de control documentados.
""", encoding="utf-8")
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V183.csv", [
    {"id":"PS183_01","endpoint":"CGN 2005-2010","result":"MY4002 zero/reappearance/inconsistencies/2010 tie","preserved":"YES","limit":"counterparty open"},
    {"id":"PS183_02","endpoint":"CGN 2011-2017","result":"foreign balance stabilizes; peso remeasurement","preserved":"YES","limit":"ledger open"},
    {"id":"PS183_03","endpoint":"CGN 2018","result":"UEPEX zero; unsupported reconstruction","preserved":"YES","limit":"bank support open"},
    {"id":"PS183_04","endpoint":"SIGEN Res1406/SSFP notes","result":"only compilations indexed","preserved":"PRIOR_SOURCES","limit":"act and note bodies open"},
])

(SYNC / "qa_source_sync_v183.py").write_text("""from pathlib import Path
import csv
R=Path(__file__).resolve().parents[5]
rows=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==703 and len({x['id'] for x in rows})==703
print('SOURCE SYNC V183 PASS · 6 new · 703/703')
""", encoding="utf-8")

(HERE / "qa_v183.py").write_text("""from pathlib import Path
import csv,hashlib,json
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==703
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V183.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==703 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V183.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V183' and co['master_catalog_entries']==703
assert co['my4002_foreign_balance_stable_2012_2017'] and co['my4002_2018_uepex_declared_zero'] and not co['my4002_2018_bcra_identifiable_support']
assert not co['my4002_counterparty_proved'] and not co['bid1192_my4002_link_to_res1406_proved'] and not co['bid1192_damage_or_appropriation_proved']
s=rows('E0_BID1192_MY4002_ACCOUNT_SERIES_2006_2018_V183.csv'); assert len(s)==13
assert next(x for x in s if x['year']=='2015')['ars_identity_gap']=='60982.39'
assert next(x for x in s if x['year']=='2018')['closing_vs_extract_foreign_gap']=='15182.68'
assert len(rows('E0_BID1192_MY4002_DECOMPOSITION_V183.csv'))==7 and len(rows('E0_BID1192_MY4002_CLAIM_SEPARATION_V183.csv'))==7
assert len(rows('V183_SOURCE_BUNDLE.csv'))==7 and len(rows('V183_PDF_VISUAL_CONTROL.csv'))==7 and len(rows('V183_PDF_TEXT_CONTROL.csv'))==7
obj=rows('E0_V183_REQUEST_OBJECTS.csv'); assert {'RO183_80','RO183_81','RO183_82'}<={x['row_id'] for x in obj}; assert all(x['status']=='DRAFT_NOT_SENT' for x in obj); assert obj==rows('E0_V183_REQUEST_OBJECTS_V183.csv')
panel=rows('FOUR_LEG_PASS_PANEL_V183.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
m=json.loads((H/'MANIFEST_V183.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V183' and m['parent_checkpoint']=='V182' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V183 QA PASS · 703/703 · MY4002_SERIES · 2018_BANK_SUPPORT=NO · counterparty=NO · damage=NO · requests=0')
""", encoding="utf-8")

# Refresco de procedencia tras crear sincronización y QA.
origins = read_csv(ORIGINS)
by_path = {row["path"]:row for row in origins}
for path in iter_files(SYNC):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V183","note":"six-source synchronization"}
for path in HERE.iterdir():
    if path.is_file():
        by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V183","note":"MY4002 longitudinal account/control checkpoint"}
write_csv(ORIGINS, list(by_path.values()), ["path","origin","note"])

(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")

manifest_files = [{"path":path.name,"bytes":path.stat().st_size,"sha256":sha(path)} for path in sorted(HERE.iterdir(), key=lambda item:item.name.casefold()) if path.is_file() and path.name != "MANIFEST_V183.json"]
manifest = {
    "checkpoint":"V183","parent_checkpoint":"V182","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
    "exact_entities":34,"strict_coverage_pct":COVERAGE,"strict_asset_numerator_million_ars":NUMERATOR,"system_assets_million_ars":ASSETS,
    "new_promotions":[],"source_archive":"703/703; 6 new catalogued sources; one byte-identical duplicate control",
    "historical_finding":"MY4002 series 2005-2018 reconstructed; 2012-2017 foreign balance stable; 2018 bank support unverified; Res1406/ledger/payment/damage open",
    "my4002":"ACCOUNT_SERIES_CONTROL_BREAKS_NOT_DEBT_OR_PAYMENT","my4002_2018":"UEPEX_ZERO_CGN_RECONSTRUCTION_NO_BANK_IDENTIFIABLE_SUPPORT",
    "mypesii_res1406":"REPORTED_CONTESTED_FINAL_ACT_OPEN","closed_network_gate":"NO","saf355_certifications":"0/5","executed_historical_bank_rows":"0/10","requests_submitted":0,"files":manifest_files,
}
(HERE / "MANIFEST_V183.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path":path.relative_to(REPO).as_posix(),"bytes":path.stat().st_size,"sha256":sha(path)} for path in iter_files(REPO) if path != global_manifest]
payload = {"checkpoint":"V183","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),"strict_coverage_pct":COVERAGE,"exact_entities":34,"closed_network_gate":"NO","source_audit":"703 master; 703 physical SHA-valid","historical_workstream":"MY4002 longitudinal series and control breaks reconstructed; counterparty/Res1406/payment/damage open; drafts not sent","file_count_excluding_manifest":len(global_files),"files":global_files}
temporary = global_manifest.with_suffix(".json.V183tmp")
temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
temporary.replace(global_manifest)
print("V183 BUILD PASS · catalog=703/703 · new=6 · MY4002_SERIES · 2018_BANK_SUPPORT=NO · requests=0")
