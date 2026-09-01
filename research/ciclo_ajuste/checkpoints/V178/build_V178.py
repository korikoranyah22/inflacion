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
PARENT = CYCLE / "checkpoints" / "V177"
AUDIT = CYCLE / "source_audit"
SYNC = CYCLE / "inputs" / "source_sync" / "v178"
HIST_ROOT = CYCLE / "inputs" / "historical_retrieval" / "v178"
HIST = HIST_ROOT / "binaries"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"
COVERAGE = "63.440604"
NUMERATOR = "61345602.215"
ASSETS = "96697695.5"
EXCLUDED = {".git", "__pycache__", "tmp", "node_modules"}


def read_csv(path: Path | str):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path | str, rows, fields=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or (list(rows[0]) if rows else [])
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path | str):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def iter_files(root: Path):
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted((x for x in dirs if x not in EXCLUDED), key=str.casefold)
        for name in sorted(files, key=str.casefold):
            yield Path(directory) / name


def tree(root: Path):
    out = []
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted((x for x in dirs if x not in EXCLUDED), key=str.casefold)
        base = Path(directory)
        out += [(base / x).relative_to(root).as_posix() + "/" for x in dirs]
        out += [(base / x).relative_to(root).as_posix() for x in sorted(files, key=str.casefold)]
    return "\n".join(out) + "\n"


def clone_parent():
    skip = {
        "MANIFEST_V177.json", "README_V177.md", "VEREDICTO_V177.md", "AUDITORIA_V177.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V177_A_V178.md", "V177_SOURCE_BUNDLE.csv",
        "V177_PUBLIC_SEARCH_LOG.csv", "V177_PDF_VISUAL_CONTROL.csv", "V177_HTML_CONTENT_CONTROL.csv",
    }
    for src in sorted(PARENT.iterdir(), key=lambda p: p.name.casefold()):
        if not src.is_file() or src.name in skip or src.name.startswith(("build_", "qa_")):
            continue
        dst = HERE / src.name.replace("V177", "V178")
        dst.write_text(src.read_text(encoding="utf-8-sig").replace("V177", "V178"), encoding="utf-8")


FILES = {
    "cgn2011": HIST / "cgn_cuenta_inversion_2011_separata.pdf",
    "cgn2012": HIST / "cgn_cuenta_inversion_2012_separata.pdf",
    "cgn2013": HIST / "cgn_cuenta_inversion_2013_separata.pdf",
    "cgn2014": HIST / "cgn_cuenta_inversion_2014_separata.pdf",
    "cgn2015": HIST / "cgn_cuenta_inversion_2015_separata.pdf",
    "cgn2016": HIST / "cgn_cuenta_inversion_2016_separata.pdf",
    "d1273": HIST / "decreto_1273_2012_fondyf_actualizado.html",
    "d400": HIST / "decreto_400_2019_reforma_fondyf.html",
    "r148": HIST / "resolucion_148_2005_addenda_fideicomiso_mypes_ii.html",
    "r206": HIST / "resolucion_206_2012_convenio_colaboracion_fondyf.html",
    "r4": HIST / "resolucion_4_2016_asignacion_fondyf.html",
    "r48": HIST / "resolucion_48_2013_convenio_administracion_bna_fondyf.html",
    "r967": HIST / "resolucion_967_2006_fideicomiso_mypes_ii.html",
}

EXPECTED = {
    FILES["cgn2011"]: (3745829, "076932f6356fbcd1c0bea495791d43bd45d61b9340df1e17d3704fd70c2c6807"),
    FILES["cgn2012"]: (5253124, "fb3f779356f8a8ec87e952a68fededfb818d5290cad39cf94a598a3135ad4c0c"),
    FILES["cgn2013"]: (1287636, "229fa20f1f513f87f2b234b74537afa92cf5b3df7f05382231bf68cd34034c6a"),
    FILES["cgn2014"]: (1348562, "803daf3a8910f84e98e56614c3d6a3b0c4061fdd5033fa9fe2d8864a7267d15e"),
    FILES["cgn2015"]: (1377986, "9d62211892ce99dc479a9b3f0d0d9f2f1533e5f5337408e8480564f7d12ce3d5"),
    FILES["cgn2016"]: (3239008, "b4f621497ef71c289cacfbb784a08034000048ddf863226fa7a021a29e7eff28"),
    FILES["d1273"]: (49948, "26c29c6165fb266b5c3d8f9944462da7c75222310c65ce3509ba5c8903c2820f"),
    FILES["d400"]: (41932, "fbb18087ae54c45db3fd66f19ef89b81e3b1ade0fdedabeab30557f1c634a36e"),
    FILES["r148"]: (43306, "edf9b9a63da099bbaff49a5ca0a50a0c64814e4792cb696f010298ce5da21903"),
    FILES["r206"]: (50364, "3615c28788addb5bb134afd9cf38a1768f059e1a1d8a72d2c3814f4f4c0ad6fd"),
    FILES["r4"]: (45038, "e2d769085ba4f218f350c71ed6114cc5128d9b8c7a391b4e31361e471ca33c3f"),
    FILES["r48"]: (67281, "90f427c41f2381ed9a50486780f6efcff52c939dcb8885291c51fa5bd0d6805a"),
    FILES["r967"]: (43302, "e1556e309e52b8c5de5a38a57248be37f5c750dbd2d679774ef559057d37ee49"),
}


HERE.mkdir(parents=True, exist_ok=True)
clone_parent()
for path, (size, digest) in EXPECTED.items():
    assert path.is_file() and path.stat().st_size == size and sha(path) == digest


pdf_specs = []
for year, key, pages, note in [
    (2011, "cgn2011", "PDF 200-202", "Distingue cuentas cerradas con respaldo de MP0191, que seguía sin constancia fehaciente; preserva saldos y correcciones del BID 1192."),
    (2012, "cgn2012", "PDF 222-223", "Reitera MP0191 sin cierre certificado y que la Nota BCRA 466/1796/08 no informó si seguía activa; conserva el error arrastrado de COBINT."),
    (2013, "cgn2013", "PDF 219-220", "La Nota 88/14 atribuye MP0191 a otro programa, pero CGN observa que no justificó por qué se informó durante años como propia; preserva saldos por cuenta."),
    (2014, "cgn2014", "PDF 222-223", "MP0191 desaparece del anexo sin que esa ausencia pruebe cierre; mantiene la serie de cuentas y saldos del BID 1192."),
    (2015, "cgn2015", "PDF 220-221", "Último cierre con rótulo Programa Global de Crédito; cuantifica 15 filas por ARS 482.435.943,60 y observaciones aritméticas en COBCAP/COBINT."),
    (2016, "cgn2016", "PDF 159-161", "Primer anexo localizado con rótulo FONDYF; agrega 54451/95 y cuantifica 16 filas por ARS 676.322.549,15, con diferencias de fórmula en varias cuentas."),
]:
    pdf_specs.append({
        "id": f"e0_cgn_account{year}_bid1192_fondyf_trace_v178",
        "institucion": "Contaduría General de la Nación",
        "titulo": f"Cuenta de Inversión {year} · trazabilidad BID 1192/FONDYF",
        "url": f"https://www.economia.gob.ar/hacienda/cgn/cuenta/{year}/archivos/sep.pdf",
        "path": FILES[key], "publication": str(year + 1), "code": f"Cuenta de Inversión {year} · Separata · {pages}",
        "period": str(year), "type": "PDF oficial preservado · control visual de páginas relevantes", "note": note,
    })

html_specs = [
    {"id":"e0_norm_res148_2005_mypesii_addendum_v178","institucion":"Ministerio de Economía y Producción","titulo":"Resolución 148/2005 · Addenda del fideicomiso MyPEs II(a)","url":"https://www.argentina.gob.ar/normativa/nacional/norma-104640/texto","path":FILES["r148"],"publication":"2005-03-16","code":"Resolución 148/2005","period":"2004-2005","note":"Identifica el contrato suscripto el 26/05/2004, a SUD Inversiones y Análisis S.A. como fiduciaria y a Credicoop y Macro Bansud como IFI; incorpora mediana empresa."},
    {"id":"e0_norm_res967_2006_mypesii_trust_v178","institucion":"Ministerio de Economía y Producción","titulo":"Resolución 967/2006 · modelo de fideicomiso BID 1192/OC-AR","url":"https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-967-2006-122923/texto","path":FILES["r967"],"publication":"2006-12-06","code":"Resolución 967/2006","period":"1999-2006","note":"Prueba modificación del préstamo para usar fideicomiso, suscripción estatal de 2004 y participación de Credicoop, Macro y luego Nuevo Banco Suquía; el anexo contractual de 74 hojas no fue publicado."},
    {"id":"e0_norm_decree1273_2012_fondyf_v178","institucion":"Poder Ejecutivo Nacional","titulo":"Decreto 1273/2012 actualizado · creación e integración del FONDYF","url":"https://www.argentina.gob.ar/normativa/nacional/decreto-1273-2012-200358/actualizacion","path":FILES["d1273"],"publication":"2012-07-25","code":"Decreto 1273/2012 actualizado","period":"2011-2019","note":"Crea FONDYF, integra recuperos de los préstamos 643/867/1192, exime giros equivalentes a servicios desde 2011 y preserva objeto, presupuesto y transparencia."},
    {"id":"e0_norm_res206_2012_fondyf_collaboration_v178","institucion":"Secretaría de la Pequeña y Mediana Empresa y Desarrollo Regional","titulo":"Resolución 206/2012 · convenio de colaboración FONAPYME/FONDYF","url":"https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-206-2012-203435/texto","path":FILES["r206"],"publication":"2012-10-12","code":"Resolución 206/2012","period":"2012","note":"Extiende al FONDYF funciones del Comité FONAPYME; el modelo involucra Secretaría, Hacienda, BNA y BICE y una norma posterior afirma que se suscribió el 28/12/2012."},
    {"id":"e0_norm_res48_2013_fondyf_bna_admin_v178","institucion":"Secretaría de la Pequeña y Mediana Empresa y Desarrollo Regional","titulo":"Resolución 48/2013 · modelo de administración BNA-FONDYF","url":"https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-48-2013-211614/texto","path":FILES["r48"],"publication":"2013-04-18","code":"Resolución 48/2013 · anexo 13 cláusulas","period":"2013","note":"Define fondos como propiedad del FONDYF; BNA administra sin riesgo crediticio, cobra 2%, lleva legajos, informa mensualmente y recupera por instrucción; el Programa controla destino."},
    {"id":"e0_norm_res4_2016_fondyf_assignment_v178","institucion":"Secretaría de Emprendedores y de la Pequeña y Mediana Empresa","titulo":"Resolución 4/2016 · asignación de coordinación y ejecución FONDYF","url":"https://www.argentina.gob.ar/normativa/nacional/norma-258979/texto","path":FILES["r4"],"publication":"2016-02-19","code":"Resolución 4/2016","period":"2010-2016","note":"Reconstruye la cadena UCP→Dirección de Asistencia Financiera→Subsecretaría y asigna desde 01/01/2016 la coordinación y ejecución del FONDYF a la Subsecretaría de Financiamiento de la Producción."},
    {"id":"e0_norm_decree400_2019_fondyf_reform_v178","institucion":"Poder Ejecutivo Nacional","titulo":"Decreto 400/2019 · reforma operativa del FONDYF","url":"https://www.argentina.gob.ar/normativa/nacional/decreto-400-2019-323888/texto","path":FILES["d400"],"publication":"2019-06-04","code":"Decreto 400/2019","period":"2019","note":"Autoriza nuevos instrumentos y ejecución mediante fideicomisos de administración o financieros, exige transparencia e incorpora recursos al presupuesto anual de la Secretaría."},
]

source_specs = pdf_specs + [dict(x, type="HTML oficial preservado · texto normativo completo") for x in html_specs]
sources = []
for spec in source_specs:
    sources.append({
        "id":spec["id"], "tema":"ciclo_ajuste_e0_fiscal", "institucion":spec["institucion"],
        "titulo":spec["titulo"], "url_original":spec["url"],
        "archivo_local":"/" + spec["path"].relative_to(REPO).as_posix(),
        "fecha_descarga":"2026-09-01", "fecha_publicacion":spec["publication"],
        "codigo_serie":spec["code"], "periodo_utilizado":spec["period"], "tipo":spec["type"],
        "sha256":EXPECTED[spec["path"]][1], "nota":spec["note"],
    })

catalog = read_csv(CATALOG)
catalog_fields = list(catalog[0])
by_id = {row["id"]:row for row in catalog}
for source in sources:
    by_id[source["id"]] = source
catalog = list(by_id.values())
write_csv(CATALOG, catalog, catalog_fields)
assert len(catalog) == len({row["id"] for row in catalog}) == 643

audit = []
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    actual = sha(path) if path.is_file() else ""
    audit.append({"id":row["id"],"archivo_local":row["archivo_local"],"exists":str(path.is_file()),"sha_catalog":row["sha256"].lower(),"sha_actual":actual,"hash_ok":str(path.is_file() and bool(row["sha256"]) and actual == row["sha256"].lower())})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V178.csv", audit)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V178.csv", audit)
missing = [row for row in audit if row["hash_ok"] != "True"]
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V178.csv", missing, list(audit[0]))
assert not missing

totals = [
    (2011,"Programa Global de Crédito BID 1192/OC-AR",16,"393650090.25","200-202","MP0191 sin constancia de cierre; Nota BCRA no informa si sigue activa"),
    (2012,"Programa Global de Crédito BID 1192/OC-AR",16,"411376347.31","222-223","MP0191 y error COBINT reiterados"),
    (2013,"Programa Global de Crédito BID 1192/OC-AR",16,"529945367.19","219-220","Nota 88/14 atribuye MP0191 a otro programa sin explicar su inclusión previa"),
    (2014,"Programa Global de Crédito BID 1192/OC-AR",15,"457759073.67","222-223","MP0191 ya no aparece; ausencia no prueba cierre"),
    (2015,"Programa Global de Crédito BID 1192/OC-AR",15,"482435943.60","220-221","COBCAP y COBINT con diferencias aritméticas de centavos"),
    (2016,"Fondo Nacional para el Desarrollo y Fortalecimiento de las MiPyME (FONDYF)",16,"676322549.15","159-161","se incorpora 54451/95; varias diferencias de fórmula; cambio de rótulo oficial"),
]
write_csv(HERE / "E0_BID1192_ACCOUNT_TABLE_TOTALS_2011_2016_V178.csv", [
    {"row_id":f"AT178_{i:02d}","year":str(y),"published_program_label":label,"numeric_rows_summed":str(n),"sum_published_final_ars":amount,"calculation_rule":"suma de columna Saldo final $ de todas las filas numéricas del bloque; filas sin importe excluidas; filas cero incluidas","source_pages":f"Cuenta {y} PDF {pages}","qualification":note}
    for i,(y,label,n,amount,pages,note) in enumerate(totals,1)
])

write_csv(HERE / "E0_BID1192_MP0191_CLOSURE_ATTRIBUTION_CHAIN_V178.csv", [
    {"row_id":"MP178_01","period":"2009","record":"Cuenta 2009","statement":"MP0191 no expuesta; se desconoce si fue cerrada","evidentiary_state":"CLOSURE_UNKNOWN","limit":"sin documento de cierre"},
    {"row_id":"MP178_02","period":"2011","record":"Cuenta 2011 + Nota BCRA 466/1796/08","statement":"BCRA la atribuye al Programa de Crédito para Desarrollo y Empleo de San Juan, pero no informa si sigue activa","evidentiary_state":"OTHER_PROGRAM_ASSERTION_ACTIVE_STATUS_UNKNOWN","limit":"nota citada, cuerpo todavía no recuperado"},
    {"row_id":"MP178_03","period":"2012","record":"Cuenta 2012","statement":"CGN reitera falta de documentación fehaciente y la insuficiencia de la Nota 466/1796/08","evidentiary_state":"CLOSURE_STILL_UNPROVED","limit":"reiteración no agrega cuerpo de nota"},
    {"row_id":"MP178_04","period":"2013","record":"Cuenta 2013 + Nota 88/14","statement":"programa afirma que pertenece a otro programa; CGN objeta falta de criterio que explique años de exposición como propia","evidentiary_state":"ATTRIBUTION_CONTESTED","limit":"Nota 88/14 no recuperada"},
    {"row_id":"MP178_05","period":"2014-2015","record":"Cuentas 2014-2015","statement":"MP0191 deja de aparecer en los anexos numéricos","evidentiary_state":"ABSENCE_NOT_CLOSURE","limit":"omisión de fila no equivale a certificación"},
    {"row_id":"MP178_06","period":"2016-2017","record":"compilaciones SIGEN preservadas en V177","statement":"la falta de respaldo de cierre vuelve a figurar como observación y sin acción correctiva","evidentiary_state":"CONTROL_GAP_PERSISTS","limit":"no identifica saldo ni daño"},
])

write_csv(HERE / "E0_BID1192_FIDEICOMISO_FONDYF_LEGAL_CHAIN_V178.csv", [
    {"row_id":"LC178_01","date":"15/09/1999","instrument":"Contrato BID 1192/OC-AR","proved":"existencia, monto máximo USD 100m y objetivo","open":"cuerpo contractual completo","source":"Resoluciones 148/2005 y 967/2006"},
    {"row_id":"LC178_02","date":"05/09/2002","instrument":"modificación del contrato BID","proved":"adopción de fideicomiso como seguridad jurídica adicional","open":"texto de modificación","source":"Resoluciones 148/2005 y 967/2006"},
    {"row_id":"LC178_03","date":"26/05/2004","instrument":"Contrato de Fideicomiso MyPEs II(a)","proved":"suscripción por Estado; SUD fiduciaria; Credicoop y Macro Bansud IFI","open":"contrato ejecutado y anexos","source":"Resolución 148/2005"},
    {"row_id":"LC178_04","date":"06/12/2006","instrument":"Resolución 967/2006","proved":"modelo modificado de 74 hojas; incorpora Nuevo Banco Suquía como IFI","open":"anexo expresamente no publicado","source":"Resolución 967/2006"},
    {"row_id":"LC178_05","date":"25/07/2012","instrument":"Decreto 1273/2012","proved":"crea FONDYF e integra recuperos del programa 643/867/1192","open":"conciliación de cada cuenta a la nueva afectación","source":"Decreto 1273/2012"},
    {"row_id":"LC178_06","date":"12/10 y 28/12/2012","instrument":"Resolución 206/2012 + convenio","proved":"modelo público y suscripción posterior citada para extender Comité FONAPYME","open":"ejemplar firmado y anexos operativos","source":"Resoluciones 206/2012 y 4/2016"},
    {"row_id":"LC178_07","date":"18/04/2013","instrument":"Resolución 48/2013","proved":"modelo de administración BNA-FONDYF con 13 cláusulas","open":"ejemplar efectivamente suscripto y fecha","source":"Resolución 48/2013"},
    {"row_id":"LC178_08","date":"08/08/2014-01/01/2016","instrument":"Acta 398, Res. 1417/2014 y Res. 4/2016","proved":"reasignaciones de coordinación y ejecución","open":"Acta 398 y expediente de transferencia","source":"Resolución 4/2016"},
    {"row_id":"LC178_09","date":"31/12/2016","instrument":"Cuenta de Inversión 2016","proved":"bloque bancario publicado bajo rótulo FONDYF","open":"crosswalk formal Cuenta 2015→2016 y Cuadro 13.3","source":"Cuenta 2016 PDF 159-161"},
    {"row_id":"LC178_10","date":"04/06/2019","instrument":"Decreto 400/2019","proved":"amplía instrumentos, fideicomisos posibles y reglas de transparencia","open":"decisión concreta aplicada al stock BID 1192 en reunión 29/08/2019","source":"Decreto 400/2019"},
])

write_csv(HERE / "E0_BID1192_BNA_ADMINISTRATION_RESPONSIBILITY_MATRIX_V178.csv", [
    {"row_id":"BA178_01","subject":"titularidad","rule":"fondos propiedad del FONDYF transferidos al BNA para administración","proved":"BNA no es beneficiario económico del capital","source_clause":"Res. 48/2013, cláusulas 1 y 3.a"},
    {"row_id":"BA178_02","subject":"riesgo","rule":"BNA no asume riesgo de crédito cualquiera sea la contingencia","proved":"riesgo crediticio no bancario bajo el modelo","source_clause":"Res. 48/2013, cláusula 2.4"},
    {"row_id":"BA178_03","subject":"retribución","rule":"2% de créditos efectivamente otorgados más gastos taxativos","proved":"precio contractual del administrador","source_clause":"Res. 48/2013, cláusula 6"},
    {"row_id":"BA178_04","subject":"custodia y control","rule":"legajo por préstamo, control adecuado, informes periódicos y auditorías","proved":"deber documental del BNA","source_clause":"Res. 48/2013, cláusula 3.d-f"},
    {"row_id":"BA178_05","subject":"información","rule":"informes mensuales de cobranzas, mora, desembolsos, cancelaciones y saldos","proved":"universo de registros primarios exigibles","source_clause":"Res. 48/2013, cláusula 8"},
    {"row_id":"BA178_06","subject":"mora","rule":"BNA recupera y ejecuta previa instrucción del Comité/Secretaría","proved":"decisión de ejecución no autónoma","source_clause":"Res. 48/2013, cláusulas 4.e y 7"},
    {"row_id":"BA178_07","subject":"destino","rule":"seguimiento del destino y cumplimiento del proyecto queda a cargo del Programa","proved":"separación administrador/programa","source_clause":"Res. 48/2013, cláusula 5.h"},
    {"row_id":"BA178_08","subject":"límite","rule":"modelo público no acredita por sí solo firma ni cumplimiento de cada obligación","proved":"estructura normativa","source_clause":"ejemplar ejecutado, reportes y legajos pendientes"},
])

opening_table = Decimal("482435943.60")
closing_table = Decimal("676322549.15")
opening_sigen = Decimal("489607291.57")
closing_sigen = Decimal("685073367.12")
write_csv(HERE / "E0_BID1192_2015_2016_TOTAL_CROSSWALK_V178.csv", [
    {"row_id":"TC178_01","measure":"Cuenta 2015 sum / Cuenta 2016 opening rows","amount_ars":str(opening_table),"calculation":"sum 15/16 published rows","status":"REPRODUCED","limit":"table scope only"},
    {"row_id":"TC178_02","measure":"SIGEN-reported 2016 opening total","amount_ars":str(opening_sigen),"calculation":"source value","status":"REPORTED_NOT_VERIFIED","limit":"scope not reconciled"},
    {"row_id":"TC178_03","measure":"opening scope gap","amount_ars":str(opening_sigen-opening_table),"calculation":"489607291.57-482435943.60","status":"UNEXPLAINED","limit":"not damage"},
    {"row_id":"TC178_04","measure":"Cuenta 2016 closing row sum","amount_ars":str(closing_table),"calculation":"sum 16 published rows","status":"REPRODUCED","limit":"table scope only"},
    {"row_id":"TC178_05","measure":"SIGEN-reported 2016 closing total","amount_ars":str(closing_sigen),"calculation":"source value","status":"REPORTED_NOT_VERIFIED","limit":"Cuadro 13.3 not verified"},
    {"row_id":"TC178_06","measure":"closing scope gap","amount_ars":str(closing_sigen-closing_table),"calculation":"685073367.12-676322549.15","status":"UNEXPLAINED","limit":"not damage"},
    {"row_id":"TC178_07","measure":"published-row net movement","amount_ars":str(closing_table-opening_table),"calculation":"676322549.15-482435943.60","status":"REPRODUCED","limit":"nominal"},
    {"row_id":"TC178_08","measure":"SIGEN aggregate net movement","amount_ars":str(closing_sigen-opening_sigen),"calculation":"685073367.12-489607291.57","status":"REPRODUCED_FROM_REPORTED_TOTALS","limit":"substance unverified"},
    {"row_id":"TC178_09","measure":"difference between net movements","amount_ars":str((closing_sigen-opening_sigen)-(closing_table-opening_table)),"calculation":"195466075.55-193886605.55","status":"UNEXPLAINED","limit":"requires Cuadro 13.3/ledger crosswalk"},
])

write_csv(HERE / "E0_BID1192_PUBLIC_DOCUMENT_BOUNDARY_V178.csv", [
    {"row_id":"PB178_01","document":"Notas 04854651 y 7813292/2017","public_result":"not localized under printed or normalized GDE variants","proved":"scoped public retrieval negative","next":"request GDE metadata, body and annexes"},
    {"row_id":"PB178_02","document":"Nota BCRA 466/1796/08","public_result":"citation only in Cuentas 2011-2012","proved":"existence and limited described content","next":"request body and route"},
    {"row_id":"PB178_03","document":"Nota 88/14","public_result":"citation only in Cuenta 2013","proved":"other-program assertion and CGN objection","next":"request body and criteria"},
    {"row_id":"PB178_04","document":"Contrato de fideicomiso Res. 967/2006","public_result":"resolution says 74-page annex not published","proved":"parties/history/model approval","next":"DNR/Boletín Oficial consultation and certified copy"},
    {"row_id":"PB178_05","document":"Convenio Res. 206/2012","public_result":"model public; later norm says signed 28/12/2012","proved":"model plus execution recital","next":"executed counterpart and annexes"},
    {"row_id":"PB178_06","document":"Convenio Res. 48/2013","public_result":"model public with blank signature date","proved":"13-clause allocation of duties","next":"executed counterpart, reports and accounts"},
    {"row_id":"PB178_07","document":"Acta 398/2014","public_result":"cited in Res. 4/2016; unrelated search collisions only","proved":"meeting date and described decision","next":"act body and attachments"},
    {"row_id":"PB178_08","document":"reunión DAIF 29/08/2019","public_result":"narrative only in Cuenta 2019","proved":"participants/purpose at narrative level","next":"convocation, minutes, outcome"},
])

search_keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V178.csv")
search_keys += [
    {"key_id":"SK178_50","route":"REQ133_ECON/BCRA","key_type":"legacy_notes","search_keys":"466/1796/08; Nota 88/14; MP0191; Banco Credicoop cuenta indisponible","purpose":"cerrar atribución y estado de MP0191","source_hint":"Cuentas 2011-2013","warning":"cita no sustituye cuerpo"},
    {"key_id":"SK178_51","route":"DNR/Boletín Oficial/REQ133_ECON","key_type":"unpublished_contract_annex","search_keys":"Resolución 967/2006; anexo 74 hojas; contrato 26/05/2004; Res. 347/2004; Res. 389/2005","purpose":"recuperar contrato MyPEs II(a) ejecutado","source_hint":"Res. 967/2006","warning":"modelo/aprobación no prueba cada cláusula ejecutada"},
    {"key_id":"SK178_52","route":"BNA/Secretaría PyME/Hacienda/BICE","key_type":"executed_collaboration","search_keys":"Resolución 206/2012; convenio 28/12/2012; FONAPYME; FONDYF","purpose":"recuperar ejemplar firmado y anexos","source_hint":"Res. 4/2016","warning":"recital posterior no reemplaza ejemplar"},
    {"key_id":"SK178_53","route":"BNA/Secretaría PyME","key_type":"administration_agreement_and_reports","search_keys":"Resolución 48/2013; convenio administración; informes mensuales; 2%; cuenta Programa Global","purpose":"recuperar ejecución, reportes, legajos y remuneración","source_hint":"Res. 48/2013 cláusulas 3, 6 y 8","warning":"secreto bancario requiere tratamiento legal, no omisión total"},
    {"key_id":"SK178_54","route":"Secretaría PyME/Comité FONAPYME","key_type":"handoff_act","search_keys":"Acta 398 08/08/2014; Resolución 1417/2014; Resolución 4/2016","purpose":"cerrar cadena de responsabilidad y transferencia","source_hint":"Res. 4/2016","warning":"estructura no prueba cumplimiento"},
    {"key_id":"SK178_55","route":"CGN/UAI/SAF362","key_type":"total_crosswalk","search_keys":"482435943.60;489607291.57;676322549.15;685073367.12;1579470.00","purpose":"reconciliar filas publicadas con Cuadro 13.3","source_hint":"Cuentas 2015/2016 + SIGEN 2017","warning":"gap de alcance no equivale a daño"},
]
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V178.csv", search_keys)

objects = read_csv(HERE / "E0_V178_REQUEST_OBJECTS.csv")
objects += [
    {"row_id":"RO178_48","object":"BID1192_MP0191_LEGACY_NOTE_BODIES","custodian":"BCRA · CGN/DAIF · programa","document":"Notas 466/1796/08 y 88/14, anexos y rutas","period":"2008-2014","fields":"cuerpo; firmante; destinatario; cuenta; programa; estado; cierre; anexos; expediente","closure":"copia certificada y constancia bancaria de estado/cierre","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO178_49","object":"MYPESII_EXECUTED_TRUST_CONTRACT","custodian":"Dirección Nacional del Registro Oficial · Economía · fiduciario","document":"contrato 26/05/2004 y anexo 74 hojas Res. 967/2006, adendas","period":"2004-2006","fields":"partes; cuentas; patrimonio; propiedad; IFI; riesgo; reportes; cierre; firmas; anexos","closure":"ejemplar ejecutado íntegro o certificación de custodia/consulta","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO178_50","object":"FONDYF_EXECUTED_COLLABORATION_AGREEMENT","custodian":"Secretaría PyME · Hacienda · BNA · BICE","document":"convenio Res. 206/2012 suscripto 28/12/2012","period":"2012","fields":"firmas; fecha; obligaciones; Comité; anexos; expediente; vigencia","closure":"contraparte firmada y anexos","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO178_51","object":"FONDYF_BNA_EXECUTED_ADMIN_PACKAGE","custodian":"BNA · Secretaría PyME","document":"convenio Res. 48/2013, cuenta, informes mensuales, legajos y facturación 2%","period":"2013-2019","fields":"firma; fecha; cuenta; préstamo; CUIT; desembolso; cobro; mora; saldo; reporte; comisión; factura","closure":"ledger y reportes conciliables con Cuentas","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO178_52","object":"FONDYF_ACT398_HANDOFF_FILE","custodian":"Comité FONAPYME · Secretaría PyME","document":"Acta 398 del 08/08/2014, Res. 1417/2014 y transferencia a Res. 4/2016","period":"2014-2016","fields":"asistentes; decisión; inventario; cuentas; responsables; pendientes; entrega; recepción","closure":"acta y expediente de traspaso con inventario","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO178_53","object":"BID1192_CUADRO13_TOTAL_RECONCILIATION","custodian":"CGN · UAI · SAF362 · programa","document":"Cuadros 13.2/13.3, mayores, conciliaciones y estados 2015-2016","period":"2015-2016","fields":"cuenta; apertura; debe; haber; cierre; alcance; ajuste; total; certificante; respaldo","closure":"reconciliar gaps 7171347.97, 8750817.97 y 1579470.00","status":"DRAFT_NOT_SENT"},
]
write_csv(HERE / "E0_V178_REQUEST_OBJECTS.csv", objects)
write_csv(HERE / "E0_V178_REQUEST_OBJECTS_V178.csv", objects)
assert all(row["status"] == "DRAFT_NOT_SENT" for row in objects)

(HERE / "E0_REQUEST_PACKAGE_V178.md").write_text("""# Paquete de pedidos V178 · BORRADOR_NO_ENVIADO

No fue remitido. Incorpora seis objetos cerrables: Notas 466/1796/08 y 88/14; contrato MyPEs II(a) y anexo no publicado; convenio de colaboración ejecutado; paquete de administración BNA; Acta 398/2014; y reconciliación Cuadros 13.2/13.3 2015-2016. Toda respuesta debe incluir cuerpos, anexos, metadatos y, si no existe, negativo fundado por repositorio y período.
""", encoding="utf-8")

write_csv(HERE / "V178_PUBLIC_SEARCH_LOG.csv", [
    {"query_id":"PS178_01","query":"Notas 04854651SSFP#MP/2017 y 7813292/SSFP#MP/2017 + variantes GDE","result":"sin cuerpos públicos localizados","artifact":"compilación SIGEN 2017 ya preservada","limit":"negativo acotado"},
    {"query_id":"PS178_02","query":"BID 1192 + Cuenta 2020/2021 + no se presentó información","result":"sin seguimiento posterior indexado","artifact":"Cuenta 2019 ya preservada","limit":"índice web incompleto"},
    {"query_id":"PS178_03","query":"Cuenta de Inversión 2011-2016 /archivos/sep.pdf","result":"seis PDF oficiales accesibles por ruta histórica y redirección mecon","artifact":"seis PDF preservados","limit":"2017+ usa otra estructura"},
    {"query_id":"PS178_04","query":"MP0191 + 466/1796/08 + 88/14","result":"detalles sólo en Cuentas 2011-2013","artifact":"cadena MP0191","limit":"notas no recuperadas"},
    {"query_id":"PS178_05","query":"Resolución 967/2006 + fideicomiso MyPEs II","result":"norma oficial; anexo de 74 hojas expresamente no publicado","artifact":"HTML preservado","limit":"contrato ejecutado pendiente"},
    {"query_id":"PS178_06","query":"Resolución 148/2005 + SUD + Credicoop + Macro","result":"addenda oficial con partes del fideicomiso","artifact":"HTML preservado","limit":"addenda no reemplaza contrato"},
    {"query_id":"PS178_07","query":"Decreto 1273/2012 + FONDYF","result":"creación, recursos y afectación probados","artifact":"HTML preservado","limit":"no concilia cuentas"},
    {"query_id":"PS178_08","query":"Resolución 206/2012 + convenio colaboración","result":"modelo público; firma 28/12/2012 citada por Res. 4/2016","artifact":"HTML preservado","limit":"ejemplar firmado pendiente"},
    {"query_id":"PS178_09","query":"Resolución 48/2013 + convenio administración BNA","result":"13 cláusulas públicas y responsabilidades precisas","artifact":"HTML preservado","limit":"ejecución/reportes pendientes"},
    {"query_id":"PS178_10","query":"Acta 398/2014 + FONDYF","result":"sólo cita y resumen en Res. 4/2016; colisiones irrelevantes","artifact":"límite público documentado","limit":"acta pendiente"},
    {"query_id":"PS178_11","query":"Decreto 400/2019 + FONDYF","result":"reforma operativa y transparencia probadas","artifact":"HTML preservado","limit":"no prueba decisión de reunión 29/08/2019"},
])

write_csv(HERE / "V178_PDF_VISUAL_CONTROL.csv", [
    {"control_id":"PDF178_01","source_id":pdf_specs[0]["id"],"pdf_pages":"200-202","target":"MP0191, cierres respaldados y cuentas 2011","result":"PASS_LEGIBLE_COMPLETE","limit":"no cuerpo Nota 466/1796/08"},
    {"control_id":"PDF178_02","source_id":pdf_specs[1]["id"],"pdf_pages":"222-223","target":"MP0191 y COBINT 2012","result":"PASS_LEGIBLE_COMPLETE","limit":"cierre MP0191 abierto"},
    {"control_id":"PDF178_03","source_id":pdf_specs[2]["id"],"pdf_pages":"219-220","target":"Nota 88/14 y cuentas 2013","result":"PASS_LEGIBLE_COMPLETE","limit":"atribución disputada"},
    {"control_id":"PDF178_04","source_id":pdf_specs[3]["id"],"pdf_pages":"222-223","target":"serie numérica 2014","result":"PASS_LEGIBLE_COMPLETE","limit":"ausencia MP0191 no cierra"},
    {"control_id":"PDF178_05","source_id":pdf_specs[4]["id"],"pdf_pages":"220-221","target":"serie numérica y fórmulas 2015","result":"PASS_LEGIBLE_COMPLETE","limit":"agregado SIGEN difiere"},
    {"control_id":"PDF178_06","source_id":pdf_specs[5]["id"],"pdf_pages":"159-161","target":"rótulo FONDYF, 16 filas y fórmulas 2016","result":"PASS_LEGIBLE_COMPLETE","limit":"Cuadro 13.3 no disponible"},
])

html_checks = [
    ("HTML178_01",html_specs[0],"SUD INVERSIONES Y ANALISIS SOCIEDAD ANONIMA","PASS_EXACT_STRING"),
    ("HTML178_02",html_specs[1],"SETENTA Y CUATRO (74) hojas","PASS_EXACT_STRING"),
    ("HTML178_03",html_specs[2],"los recuperos de préstamos originados","PASS_EXACT_STRING"),
    ("HTML178_04",html_specs[3],"Modelo de Convenio de Colaboración","PASS_EXACT_STRING"),
    ("HTML178_05",html_specs[4],"El BANCO no asumirá riesgo de crédito alguno","PASS_EXACT_STRING"),
    ("HTML178_06",html_specs[5],"a partir del 1 de enero de 2016","PASS_EXACT_STRING"),
    ("HTML178_07",html_specs[6],"mecanismos que aseguren la debida transparencia","PASS_EXACT_STRING"),
]
for _, spec, needle, _ in html_checks:
    assert needle.casefold() in spec["path"].read_text(encoding="utf-8").casefold()
write_csv(HERE / "V178_HTML_CONTENT_CONTROL.csv", [
    {"control_id":cid,"source_id":spec["id"],"target_string":needle,"result":result,"limit":"control de contenido local; no prueba ejecución material"}
    for cid,spec,needle,result in html_checks
])

write_csv(HERE / "V178_SOURCE_BUNDLE.csv", [
    {"source_id":s["id"],"local_path":s["archivo_local"],"sha256":s["sha256"],"bytes":str((REPO / s["archivo_local"].lstrip("/")).stat().st_size),"url":s["url_original"],"role":"new V178 official source"}
    for s in sources
])

SYNC.mkdir(parents=True, exist_ok=True)
sync_rows = [{"source_id":s["id"],"local_path":s["archivo_local"],"sha256":s["sha256"],"bytes":str((REPO / s["archivo_local"].lstrip("/")).stat().st_size)} for s in sources]
write_csv(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V178.csv", sync_rows)
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V178.csv", [{"source_id":s["id"],"url":s["url_original"],"retrieval":"DIRECT_OFFICIAL_TLS_OR_HISTORICAL_REDIRECT","status":"PRESERVED"} for s in sources])
(SYNC / "SOURCE_SYNC_REPORT_V178.md").write_text("# Sincronización V178\n\n- Catálogo 643/643; hashes válidos; brecha 0.\n- Seis separatas CGN 2011-2016 y siete normas oficiales preservadas.\n- Trece páginas relevantes de seis PDF controladas visualmente; siete HTML controlados por contenido.\n- Contrato ejecutado/anexo de 74 hojas, notas, Acta 398 y reportes siguen pendientes.\n", encoding="utf-8")
(SYNC / "qa_source_sync_v178.py").write_text("""from pathlib import Path
import csv,hashlib
H=Path(__file__).resolve().parent; R=H.parents[4]
rows=list(csv.DictReader((H/'SOURCE_SYNC_FILE_MANIFEST_V178.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==13
for x in rows:
 p=R/x['local_path'].lstrip('/'); assert p.is_file() and p.stat().st_size==int(x['bytes']) and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
print('SOURCE SYNC V178 PASS · 13/13')
""", encoding="utf-8")

prov = read_csv(HERE / "ARCHIVAL_PROVENANCE_V178.csv")
for s in sources:
    p = REPO / s["archivo_local"].lstrip("/")
    prov.append({"source_id":s["id"],"original_url":s["url_original"],"retrieved_utc":"2026-09-01","cdx_digest":"N/A_OFFICIAL_DIRECT_DOWNLOAD","local_path":s["archivo_local"],"sha256":s["sha256"],"bytes":str(p.stat().st_size),"provenance_note":s["nota"]})
write_csv(HERE / "ARCHIVAL_PROVENANCE_V178.csv", list({row["source_id"]:row for row in prov}.values()))

with (HERE / "SOURCE_REFERENCES_V178.md").open("a", encoding="utf-8") as f:
    f.write("\n## V178 · cuentas 2011-2016 y arquitectura MyPEs II/FONDYF\n")
    for s in sources:
        f.write(f"\n- `{s['id']}` · {s['titulo']} · {s['url_original']} · `{s['archivo_local']}` · `{s['sha256']}`\n")
with (HERE / "RETRIEVAL_LOG_V178.md").open("a", encoding="utf-8") as f:
    f.write("\n## V178\n\n- Trece fuentes oficiales nuevas preservadas: seis Cuentas 2011-2016 y siete normas.\n- MP0191 trazada hasta Nota 88/14; ausencia posterior no equivale a cierre.\n- Fideicomiso 2004 y partes probados; anexo contractual de 74 hojas expresamente no publicado.\n- FONDYF creado en 2012; responsabilidades BNA/Programa delimitadas por el modelo 2013; rótulo contable cambia en 2016.\n- Sumas de filas 2015/2016 reproducidas; gaps con agregados SIGEN abiertos y no tratados como daño.\n")

recovery = f"""# Recuperación archivística · V178

La serie oficial 2011-2016 completa el tramo intermedio del BID 1192. MP0191 permaneció sin cierre fehaciente en 2011-2012; en 2013 la Nota 88/14 la atribuyó a otro programa, pero CGN objetó que no explicaba años de exposición propia. La arquitectura jurídica muestra un fideicomiso MyPEs II(a) suscripto en 2004, con SUD como fiduciaria y Credicoop/Macro como IFI; el anexo de 74 hojas aprobado en 2006 no fue publicado. El Decreto 1273/2012 creó FONDYF con los recuperos; el modelo BNA de 2013 separa propiedad, administración, riesgo, información y seguimiento. Las filas publicadas suman ARS 482.435.943,60 en 2015 y ARS 676.322.549,15 en 2016, mientras los agregados SIGEN son mayores en ARS 7.171.347,97 y ARS 8.750.817,97; la variación de la brecha es ARS 1.579.470,00 y no se atribuye sin Cuadro 13.3. Archivo 643/643; panel 34 y {COVERAGE}%; solicitudes 0.
"""
for name in ("E0_PLAN_2009_ARCHIVE_RECOVERY_NOTE_V178.md", "E0_SIGEN_ARCHIVAL_INDEX_RECOVERY_NOTE_V178.md", "E0_FISCAL_RECONSTRUCTION_V178.md"):
    (HERE / name).write_text(recovery, encoding="utf-8")
(HERE / "CNV_ATTACHMENT_ANALYTIC_REVIEW_V178.md").write_text(f"# Revisión acumulada V178\n\nPanel 34 y {COVERAGE}% congelado. El tramo 2011-2016, el fideicomiso y la asignación FONDYF están documentados; el anexo contractual, MP0191, Cuadro 13.3, SISIO/3672 y daño siguen abiertos. Solicitudes 0.\n", encoding="utf-8")

(HERE / "README_V178.md").write_text(f"""# Checkpoint V178

- Archivo 643/643; trece fuentes oficiales nuevas; hashes válidos.
- Se preservó la serie completa de Cuentas 2011-2016 para BID 1192/FONDYF.
- MP0191 siguió sin cierre fehaciente en 2011-2012; Nota 88/14 la atribuyó a otro programa en 2013 sin justificar la exposición previa.
- El fideicomiso MyPEs II(a) fue suscripto el 26/05/2004; SUD era fiduciaria y Credicoop/Macro IFI. El anexo contractual de 74 hojas de 2006 no fue publicado.
- Decreto 1273/2012 creó FONDYF con recuperos; Res. 206/2012 extendió el Comité; Res. 48/2013 delimitó administración BNA, riesgo, precio, reportes y control; Res. 4/2016 reasignó coordinación.
- La Cuenta cambia el rótulo Programa Global→FONDYF en 2016 y agrega 54451/95.
- Sumas publicadas: 2015 ARS 482435943.60; 2016 ARS 676322549.15.
- Frente a agregados SIGEN quedan gaps de ARS 7171347.97 y 8750817.97; la diferencia de movimientos es ARS 1579470.00. Son gaps de alcance no reconciliados, no daño.
- Contrato ejecutado completo, notas, Acta 398, reportes BNA, Cuadro 13.3 y SISIO/3672 siguen pendientes.
- Panel 34; {NUMERATOR}/{ASSETS}; {COVERAGE}%; solicitudes 0; SAF355 0/5; ejecución 0/10.
""", encoding="utf-8")
(HERE / "VEREDICTO_V178.md").write_text("# Veredicto V178\n\nAvance probatorio fuerte: ya no se trata de una clasificación abstracta. Hay una cadena normativa y contable 2004→2019 que distingue fideicomiso MyPEs II(a), recuperos, FONDYF, administrador BNA y Programa, y una serie de cuentas 2011-2016. También queda cuantificado un gap exacto entre la suma de filas publicadas y los agregados SIGEN. No promoverlo como daño: faltan contrato ejecutado completo, Cuadro 13.3, legajos/reportes y crosswalk SISIO/3672.\n", encoding="utf-8")
(HERE / "AUDITORIA_V178.md").write_text(f"# Auditoría V178\n\n- 643/643 fuentes; huecos 0; nuevas 13 oficiales.\n- PDF visual: 13 páginas de 6 documentos, PASS. HTML: 7/7 controles de contenido, PASS.\n- Totales reproducidos 2011-2016; gaps 2015/2016 y movimiento exactos.\n- Matrices nuevas: totales 6; MP0191 6; cadena legal 10; responsabilidad BNA 8; crosswalk total 9; límite público 8.\n- Pedidos nuevos 6, todos DRAFT_NOT_SENT; solicitudes efectivas 0.\n- Panel 34, {COVERAGE}%; SAF355 0/5; ejecución 0/10.\n", encoding="utf-8")
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V178_A_V179.md").write_text("""# Handover V178 → V179

## Cerrado
- Archivo 643/643; seis Cuentas 2011-2016 y siete normas oficiales nuevas.
- MP0191 trazada 2009→2017; atribución a otro programa no equivale a cierre.
- Fideicomiso MyPEs II(a), partes y transición FONDYF documentados.
- Responsabilidades BNA/Programa y deber mensual de información delimitados.
- Gaps de totales 2015/2016 cuantificados sin imputarlos como daño.

## Prioridad V179
1. Recuperar anexo de 74 hojas de Resolución 967/2006 y contrato ejecutado del 26/05/2004.
2. Recuperar Notas BCRA 466/1796/08 y 88/14 con rutas y anexos.
3. Recuperar convenio Res. 206 firmado 28/12/2012 y convenio Res. 48 efectivamente suscripto.
4. Recuperar Acta 398/2014 y expediente de transferencia 2014-2016.
5. Obtener informes mensuales BNA, cuenta Programa, legajos, recuperos y comisión 2%.
6. Obtener Cuadros 13.2/13.3 y reconciliar gaps 7.171.347,97; 8.750.817,97; 1.579.470,00.
7. Continuar Notas 2017, reunión DAIF 29/08/2019 y filas SISIO/3672.
8. Mantener gaps, omisiones y falta de cierre separados de daño o apropiación.
""", encoding="utf-8")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V177.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint":"V178","date":"2026-09-01","master_catalog_entries":643,"physical_local_copies":643,"physical_local_hash_ok":643,"remaining_catalog_physical_or_hash_gaps":0,
    "state":"SOURCE_ARCHIVE_COMPLETE_BID1192_2011_2016_AND_FONDYF_LEGAL_CHAIN_PROVED_CONTRACT_BODY_AND_TOTAL_CROSSWALK_OPEN","analytical_promotion":"NONE_V178_SCOPE_GAPS_NOT_DAMAGE","exact_entities":34,
    "strict_coverage_pct":COVERAGE,"strict_asset_numerator_million_ars":NUMERATOR,"system_assets_million_ars":ASSETS,"strict_coverage_increment_v177_pp":"0",
    "requests_submitted":0,"responses_received":0,"saf355_certifications_located":0,"executed_historical_bank_rows_confirmed":0,
    "bid1192_account_series_2011_2016_preserved":True,"bid1192_fondyf_legal_chain_proved":True,"mypesii_executed_contract_full_body_located":False,
    "bid1192_2015_published_row_sum_ars":"482435943.60","bid1192_2016_published_row_sum_ars":"676322549.15","bid1192_2016_opening_scope_gap_ars":"7171347.97","bid1192_2016_closing_scope_gap_ars":"8750817.97","bid1192_net_movement_gap_ars":"1579470.00",
    "bid1192_note3672_sisio_crosswalk_proved":False,"bid1192_damage_or_appropriation_proved":False,
    "commoncrawl_exact_prefix_queries_v178":0,"commoncrawl_valid_no_capture_v178":0,"commoncrawl_service_errors_v178":0,"commoncrawl_capture_rows_v178":0,
    "commoncrawl_pending_retry_queries":40,"commoncrawl_pending_retry_collections":20,"new_v178_sources":13,"public_web_queries_v178":11,
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V178.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

origins = read_csv(ORIGINS)
by_path = {row["path"]:row for row in origins}
for path in iter_files(HIST_ROOT):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"downloaded/preserved V178","note":"official CGN PDF or Argentina.gob.ar normative HTML; verified"}
for path in iter_files(SYNC):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V178","note":"incremental thirteen-source synchronization"}
for path in HERE.iterdir():
    if path.is_file():
        by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V178","note":"BID1192/FONDYF legal and account checkpoint"}
for path in (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V178.csv", AUDIT / "SOURCE_BACKUP_CENSUS_V178.csv", AUDIT / "SOURCE_PRESERVATION_MISSING_V178.csv", AUDIT / "CURRENT_SOURCE_COMPLETENESS_V178.json"):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V178","note":"643-source completeness"}
write_csv(ORIGINS, list(by_path.values()), ["path","origin","note"])

transparency = CYCLE / "TRANSPARENCY_README.md"
body = transparency.read_text(encoding="utf-8-sig")
if "## V178 · fideicomiso MyPEs II y FONDYF" not in body:
    body += "\n\n## V178 · fideicomiso MyPEs II y FONDYF\n\nSeis Cuentas 2011-2016 y siete normas oficiales cierran la arquitectura del fideicomiso y el FONDYF a nivel normativo/contable. Se cuantificaron gaps de alcance con SIGEN, no daño. El contrato completo, las notas, reportes, Acta 398 y SISIO siguen abiertos. Archivo 643/643; panel 34; solicitudes 0.\n"
    transparency.write_text(body, encoding="utf-8")
(REPO / "BACKUP_ACTUALIZACION_2026-09-01.md").write_text(f"# Backup de actualización · 2026-09-01\n\n- V178; 643/643 fuentes.\n- Cuentas 2011-2016 y cadena fideicomiso MyPEs II→FONDYF preservadas.\n- MP0191 sin cierre documental; partes y responsabilidades delimitadas.\n- Totales 2015/2016 y gaps SIGEN reproducidos, sin inferir daño.\n- Contrato completo, Cuadro 13.3, reportes y SISIO/3672 abiertos.\n- Panel 34, {COVERAGE}%; solicitudes 0.\n", encoding="utf-8")

(HERE / "qa_v178.py").write_text("""from pathlib import Path
import csv,hashlib,json
from decimal import Decimal
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==643
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V178.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==643 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V178.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V178' and co['master_catalog_entries']==643
assert co['bid1192_account_series_2011_2016_preserved'] and co['bid1192_fondyf_legal_chain_proved'] and not co['mypesii_executed_contract_full_body_located']
assert not co['bid1192_note3672_sisio_crosswalk_proved'] and not co['bid1192_damage_or_appropriation_proved']
assert co['requests_submitted']==co['saf355_certifications_located']==co['executed_historical_bank_rows_confirmed']==0
assert len(rows('E0_BID1192_ACCOUNT_TABLE_TOTALS_2011_2016_V178.csv'))==6
t=rows('E0_BID1192_2015_2016_TOTAL_CROSSWALK_V178.csv'); assert len(t)==9 and Decimal(t[8]['amount_ars'])==Decimal('1579470.00')
assert len(rows('E0_BID1192_MP0191_CLOSURE_ATTRIBUTION_CHAIN_V178.csv'))==6
assert len(rows('E0_BID1192_FIDEICOMISO_FONDYF_LEGAL_CHAIN_V178.csv'))==10
assert len(rows('E0_BID1192_BNA_ADMINISTRATION_RESPONSIBILITY_MATRIX_V178.csv'))==8
assert len(rows('E0_BID1192_PUBLIC_DOCUMENT_BOUNDARY_V178.csv'))==8
assert len(rows('V178_PDF_VISUAL_CONTROL.csv'))==6 and all(x['result'].startswith('PASS') for x in rows('V178_PDF_VISUAL_CONTROL.csv'))
assert len(rows('V178_HTML_CONTENT_CONTROL.csv'))==7 and all(x['result'].startswith('PASS') for x in rows('V178_HTML_CONTENT_CONTROL.csv'))
assert len(rows('V178_SOURCE_BUNDLE.csv'))==13
keys=rows('E0_REQUEST_SEARCH_KEY_MATRIX_V178.csv'); assert {f'SK178_{x}' for x in range(50,56)}<={x['key_id'] for x in keys}
obj=rows('E0_V178_REQUEST_OBJECTS.csv'); assert {f'RO178_{x}' for x in range(48,54)}<={x['row_id'] for x in obj} and all(x['status']=='DRAFT_NOT_SENT' for x in obj) and obj==rows('E0_V178_REQUEST_OBJECTS_V178.csv')
panel=rows('FOUR_LEG_PASS_PANEL_V178.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
m=json.loads((H/'MANIFEST_V178.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V178' and m['parent_checkpoint']=='V177' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V178 QA PASS · 643/643 · new=13 · FONDYF-chain=PROVED · contract-body=OPEN · panel=34 · requests=0')
""", encoding="utf-8")

(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")
manifest_files = [{"path":p.name,"bytes":p.stat().st_size,"sha256":sha(p)} for p in sorted(HERE.iterdir(), key=lambda x:x.name.casefold()) if p.is_file() and p.name != "MANIFEST_V178.json"]
manifest = {
    "checkpoint":"V178","parent_checkpoint":"V177","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
    "exact_entities":34,"strict_coverage_pct":COVERAGE,"strict_asset_numerator_million_ars":NUMERATOR,"system_assets_million_ars":ASSETS,
    "new_promotions":[],"source_archive":"643/643; six CGN PDFs and seven normative HTML sources added",
    "historical_finding":"MyPEs II trust/FONDYF legal-account chain and 2011-2016 row totals proved; contract body, total crosswalk, SISIO and damage open",
    "bid1192_2015_row_sum_ars":"482435943.60","bid1192_2016_row_sum_ars":"676322549.15","bid1192_net_movement_gap_ars":"1579470.00",
    "note_3672_target_sisio_rows":"NOT_LOCATED","commoncrawl_queries_v178":0,"commoncrawl_pending":40,
    "closed_network_gate":"NO","saf355_certifications":"0/5","executed_historical_bank_rows":"0/10","requests_submitted":0,"files":manifest_files,
}
(HERE / "MANIFEST_V178.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path":p.relative_to(REPO).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)} for p in iter_files(REPO) if p != global_manifest]
payload = {"checkpoint":"V178","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),"strict_coverage_pct":COVERAGE,"exact_entities":34,"closed_network_gate":"NO","source_audit":"643 master; 643 physical SHA-valid","historical_workstream":"MyPEs II/FONDYF chain and 2011-2016 totals proved; contract/Cuadro13/SISIO/damage open; drafts not sent","file_count_excluding_manifest":len(global_files),"files":global_files}
tmp = global_manifest.with_suffix(".json.V178tmp")
tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
tmp.replace(global_manifest)
print("V178 BUILD PASS · catalog=643/643 · new=13 · FONDYF-chain=PROVED · contract-body=OPEN · panel=34 · requests=0")
