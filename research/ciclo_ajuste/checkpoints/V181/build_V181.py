from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import csv
import hashlib
import json
import os


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
PARENT = CYCLE / "checkpoints" / "V180"
AUDIT = CYCLE / "source_audit"
SYNC = CYCLE / "inputs" / "source_sync" / "v181"
HIST_ROOT = CYCLE / "inputs" / "historical_retrieval" / "v181"
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


def append_note_once(row, sentence: str):
    note = (row.get("nota") or "").strip()
    if sentence not in note:
        row["nota"] = (note + " " + sentence).strip()


def collapse_sentence_duplicates(row, sentence: str):
    note = (row.get("nota") or "").strip()
    doubled = sentence + " " + sentence
    while doubled in note:
        note = note.replace(doubled, sentence)
    row["nota"] = note


def clone_parent():
    skip = {
        "MANIFEST_V180.json", "README_V180.md", "VEREDICTO_V180.md", "AUDITORIA_V180.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V180_A_V181.md", "V180_SOURCE_BUNDLE.csv",
        "V180_PUBLIC_SEARCH_LOG.csv", "V180_PDF_VISUAL_CONTROL.csv", "V180_HTML_CONTENT_CONTROL.csv",
        "CORRECTION_LOG_V180.md",
    }
    HERE.mkdir(parents=True, exist_ok=True)
    for src in sorted(PARENT.iterdir(), key=lambda p: p.name.casefold()):
        if not src.is_file() or src.name in skip or src.name.startswith(("build_", "qa_")):
            continue
        dst = HERE / src.name.replace("V180", "V181")
        dst.write_bytes(src.read_bytes())


EXPECTED = {
    "banco_macro_20f_2007.pdf": (1849779, "9950041285e3a8e636f09ec120b183c9db9934245c637d08c3715a1e2239afdd"),
    "banco_macro_20f_2009.pdf": (1813257, "5e74c787a985c8eaf1250efa2e98c1fc900df8ca88c3565b5fc61ef67f266c15"),
    "banco_macro_20f_2010.pdf": (1815120, "2914cac0e23d84637f4fa81aaad85514fef18bdcdf37768a9953ef7ada338aa9"),
    "banco_macro_20f_2011.pdf": (2139688, "4fc6b68eee42f64c68b0f8a5500354cd55fc4444cbe1e15aa552b621894f3cef"),
    "bcra_entidades_no_financieras_2011_s2.pdf": (3011265, "8c84f1025ee12a2fc4c16b0a4f40bf57dcb296d62bea55cd5e15d44d4490afb2"),
    "bcra_entidades_no_financieras_2012_s1.pdf": (2631557, "cf66a40f292bc464e832482af260ce51132fe59d0f9f75afb9241c2ebbedc1cf"),
    "sec_banco_macro_20f_2012.html": (5974426, "3d660683472f94a9bf6556480a9ccd4825e7d1bf00fd4d0ed860dc675ecb09cc"),
    "sec_banco_macro_20f_2013.html": (4342755, "a669cca15f659987216b8697ec0fc9a5493a565d0f68dcbc6e6ecad611f12142"),
    "sec_banco_macro_20f_2014.html": (4381710, "4835aa6c08c41ebeb419c03bae2a8fae5bb9454b9606e0c71dbf22711710c881"),
    "sec_banco_macro_20f_2015.html": (4655828, "62ac146b10556f4df6c086952d65e9184e016bc569a1560dab1f1ed234dfd6a7"),
    "sec_banco_macro_submissions_2026-09-01.json": (163773, "f4f2db3d4ff1bdd162d9712099ee91ae8d1136c352913917f31cd23ea75bdec3"),
}


SPECS = [
    ("e0_macro_20f_2007_mypes_collateral_v181", "Banco Macro S.A.", "Form 20-F 2007 · garantías y activos administrados MyPES II", "https://www.macro.com.ar/relaciones-inversores/documento/1493316419832/bma_20f_2007_eng.pdf", "banco_macro_20f_2007.pdf", "2008", "Form 20-F · ejercicio 2007 · PDF 143 y 161", "2006-2007", "PDF corporativo oficial preservado · control visual de páginas relevantes", "En miles de pesos: préstamos afectados a MyPES II 19.241 en 2006 y 12.801 en 2007. El valor 18.634 de activos administrados usa una base distinta y no se suma ni resta a la garantía."),
    ("e0_macro_20f_2009_mypes_collateral_v181", "Banco Macro S.A.", "Form 20-F 2009 · garantías MyPES II", "https://www.macro.com.ar/relaciones-inversores/documento/1517358335677/bma_20f_2009_eng.pdf", "banco_macro_20f_2009.pdf", "2010", "Form 20-F · ejercicio 2009 · PDF 236", "2008-2009", "PDF corporativo oficial preservado · control visual de página relevante", "En miles de pesos: préstamos afectados a MyPES II 20.367 en 2008 y 9.876 en 2009; prueba garantía contable, no comisión ni utilidad."),
    ("e0_macro_20f_2010_mypes_collateral_v181", "Banco Macro S.A.", "Form 20-F 2010 · garantías MyPES II", "https://www.macro.com.ar/relaciones-inversores/documento/1517358335382/bma_20f_2010_eng.pdf", "banco_macro_20f_2010.pdf", "2011", "Form 20-F · ejercicio 2010 · PDF 155", "2009-2010", "PDF corporativo oficial preservado · control visual de página relevante", "En miles de pesos: préstamos afectados a MyPES II 9.876 en 2009 y 2.599 en 2010."),
    ("e0_macro_20f_2011_mypes_collateral_v181", "Banco Macro S.A.", "Form 20-F 2011 · último saldo explícito de garantía MyPES II", "https://www.macro.com.ar/relaciones-inversores/documento/1517358335198/bma_20f_2011_eng.pdf", "banco_macro_20f_2011.pdf", "2012", "Form 20-F · ejercicio 2011 · PDF 207", "2010-2011", "PDF corporativo oficial preservado · control visual de página relevante", "En miles de pesos: préstamos afectados a MyPES II 2.599 en 2010 y 163 en 2011; no informa el reclamo administrativo posterior de 2014."),
    ("e0_sec_macro_20f_2012_restricted_assets_v181", "U.S. Securities and Exchange Commission / Banco Macro", "Form 20-F 2012 · cierre de la línea de garantía MyPES II", "https://www.sec.gov/Archives/edgar/data/1347426/000119312513178117/d526406d20f.htm", "sec_banco_macro_20f_2012.html", "2013-04-26", "SEC accession 0001193125-13-178117 · Note 7", "2011-2012", "HTML oficial SEC preservado · texto completo", "La nota de activos restringidos muestra Loans/Other 163 para 2011 y cero para 2012. MyPES no se nombra expresamente; la identificación del comparativo surge del 20-F 2011. No prueba extinción de una obligación por comisión."),
    ("e0_sec_macro_20f_2013_contingency_control_v181", "U.S. Securities and Exchange Commission / Banco Macro", "Form 20-F 2013 · control de divulgación posterior MyPES II", "https://www.sec.gov/Archives/edgar/data/1347426/000119312514167653/d713664d20f.htm", "sec_banco_macro_20f_2013.html", "2014-04-29", "SEC accession 0001193125-14-167653", "2013", "HTML oficial SEC preservado · texto completo", "Control posterior: sin mención exacta MyPES/Macro Fiducia/Resolución 1406. La ausencia puede obedecer a materialidad, agrupación o alcance y no prueba inexistencia de reclamo."),
    ("e0_sec_macro_20f_2014_contingency_control_v181", "U.S. Securities and Exchange Commission / Banco Macro", "Form 20-F 2014 · control contemporáneo a Resolución 1406", "https://www.sec.gov/Archives/edgar/data/1347426/000119312515152311/d912561d20f.htm", "sec_banco_macro_20f_2014.html", "2015-04-28", "SEC accession 0001193125-15-152311", "2014", "HTML oficial SEC preservado · texto completo", "Control contemporáneo: sin mención exacta MyPES/Macro Fiducia/Resolución 1406; no sustituye el acto, el recurso ni el análisis de materialidad contable."),
    ("e0_sec_macro_20f_2015_contingency_control_v181", "U.S. Securities and Exchange Commission / Banco Macro", "Form 20-F 2015 · control posterior a Resolución 1406", "https://www.sec.gov/Archives/edgar/data/1347426/000119312516563512/d176736d20f.htm", "sec_banco_macro_20f_2015.html", "2016-04-28", "SEC accession 0001193125-16-563512", "2015", "HTML oficial SEC preservado · texto completo", "Control posterior: sin mención exacta MyPES/Macro Fiducia/Resolución 1406. No prueba pago, rechazo ni falta de provisión específica."),
    ("e0_sec_macro_submission_index_v181", "U.S. Securities and Exchange Commission", "Índice oficial de presentaciones Banco Macro CIK 0001347426", "https://data.sec.gov/submissions/CIK0001347426.json", "sec_banco_macro_submissions_2026-09-01.json", "2026-09-01", "SEC submissions JSON · CIK 0001347426", "2006-2026", "JSON oficial preservado · procedencia e índice", "Enumera la serie 20-F y sus accessions; es prueba de procedencia, no del contenido sustantivo de cada presentación."),
    ("e0_bcra_nonfinancial_entities_2011s2_mypes_v181", "Banco Central de la República Argentina", "Información de Entidades no Financieras · MyPES II al segundo semestre 2011", "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/EntidadesNo/enf022011.pdf", "bcra_entidades_no_financieras_2011_s2.pdf", "2012", "Fideicomiso financiero 10155 · PDF 582", "2010-2011", "PDF oficial BCRA preservado · control visual de página relevante", "Identifica Macro Fiducia S.A. y deuda total en miles de pesos: 3.331,10 (dic-2010), 630,30 (jun-2011) y 39,60 (dic-2011), un registro, 100% situación normal."),
    ("e0_bcra_nonfinancial_entities_2012s1_registry_exit_v181", "Banco Central de la República Argentina", "Información de Entidades no Financieras · salida registral MyPES II en primer semestre 2012", "https://www.bcra.gob.ar/archivos/Pdfs/Publicaciones/EntidadesNo/enf012012.pdf", "bcra_entidades_no_financieras_2012_s1.pdf", "2014-02", "Primer semestre 2012 · índice PDF 13", "2012", "PDF oficial BCRA preservado · control visual del tramo alfabético del índice", "En el índice alfabético MyPES II ya no aparece entre Mercobank y Nues. Prueba ausencia en esa publicación, no por sí sola acto jurídico de liquidación o baja."),
]


clone_parent()
for name, (size, digest) in EXPECTED.items():
    path = HIST / name
    assert path.is_file() and path.stat().st_size == size and sha(path) == digest

sources = []
for sid, inst, title, url, name, publication, code, period, typ, note in SPECS:
    path = HIST / name
    sources.append({
        "id": sid, "tema": "ciclo_ajuste_e0_fiscal", "institucion": inst, "titulo": title,
        "url_original": url, "archivo_local": "/" + path.relative_to(REPO).as_posix(),
        "fecha_descarga": "2026-09-01", "fecha_publicacion": publication,
        "codigo_serie": code, "periodo_utilizado": period, "tipo": typ,
        "sha256": EXPECTED[name][1], "nota": note,
    })

catalog = read_csv(CATALOG)
catalog_fields = list(catalog[0])
by_id = {row["id"]: row for row in catalog}
for sid, sentence in (
    ("e0_bo_res967_2006_full_annex_contract_v179", "V180 acredita que el modelo Res. 967 no estaba perfeccionado al 22/02/2008; no se lo trata como régimen operativo."),
    ("e0_norm_res967_2006_mypesii_trust_v178", "AGN 14/2010 informa que el contrato aprobado por Res. 967/2006 no estaba perfeccionado al 22/02/2008."),
):
    if sid in by_id:
        collapse_sentence_duplicates(by_id[sid], sentence)
for sid in ("e0_sigen_account2016_bid1192_high_impact_observations_v177", "e0_sigen_account2017_bid1192_high_impact_observations_v177"):
    if sid in by_id:
        append_note_once(by_id[sid], "V181: SIGEN informa que la Resolución 1406 de noviembre de 2014 intimó a Macro y Credicoop por comisión de compromiso; bancos y fiduciario recurrieron y la liquidación seguía sin resolverse en las compilaciones 2017/2019.")
for source in sources:
    by_id[source["id"]] = source
catalog = list(by_id.values())
write_csv(CATALOG, catalog, catalog_fields)
assert len(catalog) == len({row["id"] for row in catalog}) == 684

audit = []
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    actual = sha(path) if path.is_file() else ""
    audit.append({"id": row["id"], "archivo_local": row["archivo_local"], "exists": str(path.is_file()), "sha_catalog": row["sha256"].lower(), "sha_actual": actual, "hash_ok": str(path.is_file() and bool(row["sha256"]) and actual == row["sha256"].lower())})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V181.csv", audit)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V181.csv", audit)
missing = [row for row in audit if row["hash_ok"] != "True"]
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V181.csv", missing, list(audit[0]))
assert not missing


write_csv(HERE / "E0_BID1192_COMMITMENT_COMMISSION_DISPUTE_CHAIN_2005_2019_V181.csv", [
    {"row_id":"CC181_01","date":"2005-08-19","event":"nuevo contrato ejecutado","proved":"mínimo USD 8m cada tres meses; 0,75% anual sobre saldo no desembolsado; pago semestral","source":"AGN 160/2006 pp.13,80","legal_state":"OPERATIVE_CLAUSE_CORROBORATED","open":"contraparte firmada"},
    {"row_id":"CC181_02","date":"2005-12-27","event":"UCP remite instructivo al administrador fiduciario","proved":"existieron metodología y fórmula complementarias","source":"AGN 160/2006 p.81","legal_state":"INSTRUCTIVE_EXISTENCE_CORROBORATED","open":"instructivo, anexos y constancia de recepción"},
    {"row_id":"CC181_03","date":"2005-12-31","event":"primer período incompleto","proved":"USD 831.246,65 ejecutados frente a mínimo USD 8m; brecha bruta USD 7.168.753,35","source":"AGN 160/2006 pp.13,80","legal_state":"RAW_SHORTFALL_PROVED","open":"base temporal, imputación por banco, excesos y ajustes"},
    {"row_id":"CC181_04","date":"2006","event":"propuesta UCP de implementación","proved":"imputación a cada banco; percepción diferida; arrastre de defectos/excesos hasta cierre 2006","source":"AGN 160/2006 pp.81-82","legal_state":"PROPOSED_METHOD_REPORTED","open":"acto de aprobación, liquidaciones y notificaciones"},
    {"row_id":"CC181_05","date":"2006","event":"auditoría de registros 2005","proved":"los registros/estados no reflejaban aplicación de penalidad","source":"AGN 160/2006 pp.13,80","legal_state":"NO_2005_LEDGER_APPLICATION_VERIFIED","open":"devengamiento/pago posterior"},
    {"row_id":"CC181_06","date":"2014-11","event":"Resolución 1406","proved":"SIGEN informa intimación a Macro y Credicoop al pago de comisión de compromiso","source":"SIGEN Cuenta 2016/2017 · PDF 89/88","legal_state":"ADMINISTRATIVE_INTIMATION_REPORTED","open":"acto, monto, autoridad, cálculo y notificación"},
    {"row_id":"CC181_07","date":"2014-2017","event":"impugnación administrativa","proved":"bancos y fiduciario interpusieron reconsideración con jerárquico en subsidio","source":"SIGEN Cuenta 2016/2017","legal_state":"CONTESTED_CLAIM_REPORTED","open":"recursos, dictámenes y decisión"},
    {"row_id":"CC181_08","date":"2017-2019","event":"liquidación no resuelta","proved":"observación recurrente/sin acción correctiva; estados 2015 faltantes","source":"SIGEN octubre 2017 y febrero 2019","legal_state":"UNRESOLVED_AT_LAST_PUBLIC_AUDIT","open":"firmeza, pago, baja, balance final y destino"},
])

write_csv(HERE / "E0_BID1192_RES1406_EVIDENCE_LADDER_V181.csv", [
    {"row_id":"EL181_01","proposition":"existió una Resolución 1406 en noviembre de 2014","status":"SUPPORTED_BY_REPEATED_SIGEN_REPORT","proof":"dos compilaciones oficiales reproducen número, mes y objeto","not_proved":"texto íntegro, emisor, expediente"},
    {"row_id":"EL181_02","proposition":"Macro y Credicoop fueron intimados","status":"SUPPORTED_BY_REPEATED_SIGEN_REPORT","proof":"contrapartes nominadas","not_proved":"recepción válida y monto individual"},
    {"row_id":"EL181_03","proposition":"existió una obligación contractual de comisión","status":"SUPPORTED_BY_AGN_QUOTED_CLAUSE","proof":"0,75% anual sobre saldo no desembolsado; semestral","not_proved":"fórmula ejecutada y obligación final por IFI"},
    {"row_id":"EL181_04","proposition":"la pretensión quedó firme","status":"NOT_PROVED_CONTRADICTED_BY_PENDING_APPEALS","proof":"recursos reportados pendientes","not_proved":"decisión final y notificación"},
    {"row_id":"EL181_05","proposition":"hubo pago o cobro","status":"NOT_PROVED","proof":"ninguna fuente pública localizada","not_proved":"tesorería, banco, fiduciario y contabilidad"},
    {"row_id":"EL181_06","proposition":"el Estado sufrió daño cuantificado","status":"NOT_PROVED","proof":"hay brecha de ejecución y reclamo, no nexo/importe firme","not_proved":"cálculo, compensaciones, prescripción, decisión y cobro"},
])

write_csv(HERE / "E0_BID1192_MACRO_COLLATERAL_TRAJECTORY_2006_2012_V181.csv", [
    {"year":"2006","restricted_loans_thousand_ars":"19241","source":"Macro 20-F 2007 PDF 143","status":"REPORTED_COMPARATIVE","limit":"garantía contable; no deuda por comisión"},
    {"year":"2007","restricted_loans_thousand_ars":"12801","source":"Macro 20-F 2007 PDF 143","status":"REPORTED","limit":"garantía contable; no activos administrados"},
    {"year":"2008","restricted_loans_thousand_ars":"20367","source":"Macro 20-F 2009 PDF 236","status":"REPORTED_COMPARATIVE","limit":"salto interanual requiere ledger"},
    {"year":"2009","restricted_loans_thousand_ars":"9876","source":"Macro 20-F 2009 PDF 236 / 2010 PDF 155","status":"CROSS_REPORTED","limit":"métrica de préstamos afectados"},
    {"year":"2010","restricted_loans_thousand_ars":"2599","source":"Macro 20-F 2010 PDF 155 / 2011 PDF 207","status":"CROSS_REPORTED","limit":"métrica de préstamos afectados"},
    {"year":"2011","restricted_loans_thousand_ars":"163","source":"Macro 20-F 2011 PDF 207 / 2012 Note 7","status":"CROSS_REPORTED","limit":"20-F 2012 lo reclasifica como Other comparativo"},
    {"year":"2012","restricted_loans_thousand_ars":"0","source":"Macro 20-F 2012 Note 7","status":"REPORTED_ZERO","limit":"cero garantía no extingue reclamo histórico"},
])

write_csv(HERE / "E0_BID1192_BCRA_TRUST_CLOSURE_CROSSCHECK_2010_2012_V181.csv", [
    {"date":"2010-12","bcra_trust_debt_thousand_ars":"3331.10","records":"","risk_status":"100% normal","macro_restricted_loans_thousand_ars":"2599","source":"BCRA 2011S2 p.582; Macro 20-F 2011 p.207","safe_reading":"dos métricas cercanas pero no idénticas; no restar"},
    {"date":"2011-06","bcra_trust_debt_thousand_ars":"630.30","records":"","risk_status":"100% normal","macro_restricted_loans_thousand_ars":"","source":"BCRA 2011S2 p.582","safe_reading":"amortización registral intermedia"},
    {"date":"2011-12","bcra_trust_debt_thousand_ars":"39.60","records":"1","risk_status":"100% normal","macro_restricted_loans_thousand_ars":"163","source":"BCRA 2011S2 p.582; Macro 20-F 2011 p.207","safe_reading":"remanentes en bases distintas"},
    {"date":"2012-06","bcra_trust_debt_thousand_ars":"","records":"","risk_status":"no listado","macro_restricted_loans_thousand_ars":"0 at 2012-12","source":"BCRA 2012S1 index p.13; Macro 20-F 2012 Note 7","safe_reading":"cierre registral/contable convergente; falta acto jurídico"},
])

write_csv(HERE / "E0_BID1192_MACRO_DISCLOSURE_LIMITS_V181.csv", [
    {"control":"20-F 2007-2011","proved":"serie de préstamos afectados a garantía y fiduciario/activos administrados 2007","not_proved":"beneficio, pérdida, tasa, comisión de compromiso o reclamo firme"},
    {"control":"20-F 2012","proved":"línea comparativa 163 pasa a cero","not_proved":"razón jurídica de baja y liquidación del fideicomiso"},
    {"control":"20-F 2013-2015","proved":"no se localiza mención exacta MyPES/Macro Fiducia/Resolución 1406","not_proved":"inexistencia de contingencia por materialidad, agrupación o criterio contable"},
    {"control":"SIGEN 2017/2019","proved":"reclamo administrativo y recursos pendientes","not_proved":"monto, firmeza, pago y registro en Banco Macro/Credicoop"},
])

shortfall = Decimal("8000000") - Decimal("831246.65")
sens = []
for label, numerator, denominator, note in (
    ("trimestre fijo 90/360", Decimal("90"), Decimal("360"), "convención discreta ilustrativa"),
    ("días reales 134/360", Decimal("134"), Decimal("360"), "19/08 a 31/12 sin incluir día inicial"),
    ("días reales 134/365", Decimal("134"), Decimal("365"), "alternativa Act/365"),
    ("días inclusivos 135/360", Decimal("135"), Decimal("360"), "sensibilidad inclusiva"),
):
    amount = (shortfall * Decimal("0.0075") * numerator / denominator).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    sens.append({"scenario":label,"minimum_usd":"8000000.00","actual_disbursement_usd":"831246.65","raw_shortfall_usd":str(shortfall),"annual_rate":"0.0075","time_fraction":str(numerator/denominator),"illustrative_charge_usd":str(amount),"legal_status":"SENSITIVITY_NOT_DEBT","missing":note+"; faltan instructivo, asignación, arrastres, dispensa y acto final"})
write_csv(HERE / "E0_BID1192_COMMISSION_ILLUSTRATIVE_SENSITIVITY_V181.csv", sens)

write_csv(HERE / "E0_BID1192_COMMISSION_CALCULATION_REQUIREMENTS_V181.csv", [
    {"variable":"contrato y versión","known":"ejecutado 19/08/2005 según AGN","needed":"contraparte firmada y anexos","why":"identificar obligados y prelación"},
    {"variable":"mínimo trimestral","known":"USD 8m","needed":"calendario de trimestres y regla del primer período","why":"definir base exigible"},
    {"variable":"desembolso efectivo","known":"USD 831.246,65 al 31/12/2005","needed":"fecha valor y cartera por IFI","why":"saldo/ponderación temporal"},
    {"variable":"tasa","known":"0,75% anual","needed":"day-count, redondeo y devengamiento","why":"convertir tasa anual a semestre/trimestre"},
    {"variable":"imputación","known":"UCP propuso monto por banco","needed":"instructivo 27/12/2005 y liquidaciones","why":"separar Macro, Credicoop y fiduciario"},
    {"variable":"compensación","known":"UCP propuso arrastrar defectos/excesos hasta fin 2006","needed":"ledger trimestral 2006","why":"evitar sobreestimar cargo"},
    {"variable":"demora/dispensa","known":"UCP consideró demorar percepción","needed":"acto competente y fundamento","why":"exigibilidad, intereses y prescripción"},
    {"variable":"acto 2014","known":"SIGEN reporta Res. 1406","needed":"acto, anexos, notificación y expediente","why":"monto intimado y motivación"},
    {"variable":"recursos","known":"reconsideración con jerárquico en subsidio","needed":"escritos, dictámenes y decisión","why":"firmeza y agotamiento administrativo"},
    {"variable":"pago/contabilidad","known":"no localizado","needed":"mayores, extractos, provisiones, cobros y baja","why":"daño residual y satisfacción"},
])

write_csv(HERE / "E0_BID1192_TERMINATION_LIQUIDATION_TIMELINE_V181.csv", [
    {"row_id":"TL181_01","date":"2007-08-13","event":"BCRA suspende nuevos proyectos","record":"Com. B 9056","state":"FUNDS_FULLY_COMMITTED","open_item":"inventario definitivo"},
    {"row_id":"TL181_02","date":"2008-09-26","event":"causal de terminación","record":"AGN 14/2010","state":"TERMINATION_TRIGGERED","open_item":"resolución y balance"},
    {"row_id":"TL181_03","date":"2009-09-14","event":"sin resolución ministerial","record":"Nota UCP 112/09","state":"LIQUIDATION_PENDING","open_item":"acto posterior"},
    {"row_id":"TL181_04","date":"2011-12-31","event":"remanente registral mínimo","record":"BCRA fideicomiso 10155; Macro 20-F","state":"ONE_NORMAL_RECORD_AND_RESTRICTED_COLLATERAL","open_item":"conciliación 39,6 vs 163 mil"},
    {"row_id":"TL181_05","date":"2012-06/12","event":"MyPES sale del índice BCRA y garantía Macro pasa a cero","record":"BCRA 2012S1; Macro 20-F 2012","state":"REGISTRY_AND_COLLATERAL_EXIT","open_item":"acto jurídico y balance final"},
    {"row_id":"TL181_06","date":"2012-08-03","event":"Decreto 1273 crea FONDYF con recuperos","record":"Decreto 1273/2012","state":"LEGAL_SUCCESSION_FRAMEWORK","open_item":"puente contable"},
    {"row_id":"TL181_07","date":"2014-11","event":"Res. 1406 intima comisión","record":"SIGEN","state":"ADMINISTRATIVE_CLAIM","open_item":"acto y cálculo"},
    {"row_id":"TL181_08","date":"2017-2019","event":"recursos pendientes; liquidación no resuelta","record":"SIGEN","state":"CONTESTED_UNRESOLVED","open_item":"decisión, pago y cierre"},
])


pdf_controls = [
    ("e0_macro_20f_2007_mypes_collateral_v181","239","143;161","garantía y activos administrados","PASS_RELEVANT_PAGES_VISUALLY_INSPECTED"),
    ("e0_macro_20f_2009_mypes_collateral_v181","333","236","garantía comparativa 2008-2009","PASS_RELEVANT_PAGE_VISUALLY_INSPECTED"),
    ("e0_macro_20f_2010_mypes_collateral_v181","233","155","garantía comparativa 2009-2010","PASS_RELEVANT_PAGE_VISUALLY_INSPECTED"),
    ("e0_macro_20f_2011_mypes_collateral_v181","293","207","garantía comparativa 2010-2011","PASS_RELEVANT_PAGE_VISUALLY_INSPECTED"),
    ("e0_bcra_nonfinancial_entities_2011s2_mypes_v181","591","582","fideicomiso 10155 y deuda","PASS_RELEVANT_PAGE_VISUALLY_INSPECTED"),
    ("e0_bcra_nonfinancial_entities_2012s1_registry_exit_v181","527","13","índice alfabético sin MyPES II","PASS_RELEVANT_PAGE_VISUALLY_INSPECTED"),
]
write_csv(HERE / "V181_PDF_VISUAL_CONTROL.csv", [
    {"control_id":f"PDF181_{i:02d}","source_id":sid,"pdf_pages":pages,"inspected_pdf_pages":inspected,"target":target,"method":"high-resolution rendering and visual inspection","result":result,"limit":"relevant-page integrity; absence controls retain scope limits"}
    for i,(sid,pages,inspected,target,result) in enumerate(pdf_controls,1)
])

html_rows = []
for i, s in enumerate(sources[4:9], 1):
    path = REPO / s["archivo_local"].lstrip("/")
    body = path.read_text(encoding="utf-8-sig", errors="ignore")
    target = "0001347426" if path.suffix == ".json" else ("RESTRICTED AND PLEDGED ASSETS" if "2012" in path.name else "FORM 20-F")
    assert target.lower() in body.lower()
    html_rows.append({"control_id":f"HTML181_{i:02d}","source_id":s["id"],"target_string":target,"target_count":str(body.lower().count(target.lower())),"mypes_exact_count":str(body.lower().count("mypes")),"result":"PASS_CONTENT_CONTROL","limit":"exact-string absence is a scoped search result, not proof of substantive nonexistence"})
write_csv(HERE / "V181_HTML_CONTENT_CONTROL.csv", html_rows)

write_csv(HERE / "V181_SOURCE_BUNDLE.csv", [
    {"source_id":s["id"],"institution":s["institucion"],"title":s["titulo"],"url":s["url_original"],"local_path":s["archivo_local"],"sha256":s["sha256"],"bytes":str((REPO/s["archivo_local"].lstrip("/")).stat().st_size),"evidentiary_role":"bank-side collateral / registry / filing-control / provenance","limit":s["nota"]}
    for s in sources
])

write_csv(HERE / "V181_PUBLIC_SEARCH_LOG.csv", [
    {"query_id":"PS181_01","query":"SIGEN Res. 1406 Banco Macro Credicoop comisión de compromiso","result":"dos reportes oficiales localizados","artifact":"SIGEN octubre 2017 y febrero 2019","limit":"acto no publicado/localizado"},
    {"query_id":"PS181_02","query":"Boletín Oficial Res. 1406 noviembre 2014 + comisión","result":"sin resultado correspondiente","artifact":"control de búsqueda","limit":"posible acto interno/no publicado"},
    {"query_id":"PS181_03","query":"SAIJ/PJN/CSJN MyPES II Macro Credicoop","result":"sin decisión pública localizada","artifact":"control de búsqueda","limit":"no prueba ausencia de expediente"},
    {"query_id":"PS181_04","query":"Banco Macro 20-F 2007/2009/2010/2011","result":"serie de garantías localizada","artifact":"cuatro PDF corporativos","limit":"contabilidad del banco, no acto administrativo"},
    {"query_id":"PS181_05","query":"SEC Banco Macro CIK 1347426 20-F 2012-2015","result":"serie oficial y accessions localizadas","artifact":"cuatro HTML + índice JSON","limit":"criterio de materialidad"},
    {"query_id":"PS181_06","query":"BCRA Entidades no Financieras MyPES II 2011/2012","result":"fideicomiso 10155 presente a dic-2011 y ausente en índice 2012S1","artifact":"dos PDF oficiales","limit":"falta acto de baja/liquidación"},
])

objects = read_csv(HERE / "E0_V181_REQUEST_OBJECTS.csv")
new_objects = [
    ("RO181_69","MYPESII_RES1406_FULL_ACT","Secretaría PyME / Ministerio de Economía","Resolución 1406 de noviembre de 2014 íntegra, anexos y expediente de origen","2014","autoridad; fecha; número; vistos; fundamentos; parte dispositiva; monto por sujeto; firma","acto auténtico e íntegro"),
    ("RO181_70","MYPESII_COMMISSION_METHOD","UCP / Secretaría PyME","Instructivo UCP remitido al fiduciario el 27/12/2005 y metodología completa","2005-2006","fórmula; day-count; trimestres; saldos; defectos; excesos; asignación; redondeo","reproducción del cálculo por período y banco"),
    ("RO181_71","MYPESII_RES1406_NOTICES","Ministerio / Macro / Credicoop / Macro Fiducia","notificaciones, cédulas, constancias de recepción e intimaciones Res. 1406","2014","fecha; destinatario; domicilio; monto; plazo; apercibimiento; recepción","notificación válida por sujeto"),
    ("RO181_72","MYPESII_RES1406_APPEALS","Ministerio / Asuntos Jurídicos","recursos de reconsideración con jerárquico en subsidio de bancos y fiduciario","2014-2019","presentante; personería; agravios; prueba; fecha; efecto; expediente","escritos íntegros y foliatura"),
    ("RO181_73","MYPESII_RES1406_FINAL_DECISION","Ministerio / Jefatura de Gabinete","dictámenes jurídicos y decisión final de recursos","2014-2026","dictamen; competencia; prescripción; cálculo; decisión; notificación; firmeza","acto final o certificación de pendencia"),
    ("RO181_74","MYPESII_COMMISSION_PAYMENT_LEDGER","TGN / CGN / bancos / fiduciario","mayores, provisiones, pagos, cobros, compensaciones y baja de comisión","2005-2026","fecha; moneda; importe; sujeto; cuenta; asiento; extracto; comprobante; saldo","conciliación de cuatro puntas"),
    ("RO181_75","MYPESII_BCRA_REGISTRY_EXIT","BCRA","acto y reporte de baja del fideicomiso financiero 10155 entre dic-2011 y jun-2012","2011-2012","fecha; motivo; saldo; fiduciario; resolución; balance; destino","acto de salida registral y balance"),
    ("RO181_76","MYPESII_MACRO_FIDUCIA_FINAL_ACCOUNTS","Macro Fiducia / fiduciario sucesor","balance final, rendición, cartera, remanente y transferencia del fideicomiso 10155","2010-2014","crédito; cobro; mora; garantía; cuenta; gasto; comisión; remanente; destino","balance final auditado y conciliado"),
]
for row_id, object_id, custodian, record, period, fields, closure in new_objects:
    objects.append({"row_id":row_id,"object_id":object_id,"custodian":custodian,"exact_record":record,"period":period,"minimum_fields":fields,"closure_rule":closure,"status":"DRAFT_NOT_SENT"})
objects = list({x["row_id"]:x for x in objects}.values())
write_csv(HERE / "E0_V181_REQUEST_OBJECTS.csv", objects)
write_csv(HERE / "E0_V181_REQUEST_OBJECTS_V181.csv", objects)

keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V181.csv")
new_keys = [
    ("SK181_70","REQ181_RES1406","resolution","Resolución 1406; noviembre 2014; MyPES II","acto, anexos y notificación","SIGEN 2017/2019","no confundir con otras resoluciones 1406"),
    ("SK181_71","REQ181_RES1406","party","Banco Macro; Banco Credicoop; Macro Fiducia; SIASA","recursos y cálculo por sujeto","SIGEN + BCRA","normalizar cambios de razón social"),
    ("SK181_72","REQ181_RES1406","trust_id","10155 - FIDEICOMISO MYPES II (A)","baja registral y balance","BCRA 2011S2","buscar por código además de nombre"),
    ("SK181_73","REQ181_RES1406","date","27/12/2005","instructivo comisión","AGN 160/2006 p.81","pedir adjuntos y acuse"),
    ("SK181_74","REQ181_RES1406","formula","0,75% anual; USD 8.000.000 trimestral; saldo no desembolsado","liquidaciones y sensibilidades","AGN 160/2006","no convertir sensibilidad en deuda"),
    ("SK181_75","REQ181_RES1406","record_family","reconsideración con jerárquico en subsidio","decisión final","SIGEN","pedir dictámenes y notificaciones"),
]
for key_id, request_id, group, exact, purpose, basis, caveat in new_keys:
    keys.append({"key_id":key_id,"request_id":request_id,"key_group":group,"exact_key":exact,"search_purpose":purpose,"source_or_basis":basis,"caveat":caveat})
keys = list({x["key_id"]:x for x in keys}.values())
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V181.csv", keys)

(HERE / "CORRECTION_LOG_V181.md").write_text("""# Correcciones V181

1. **SIGEN reauditable:** las notas de catálogo V177 omitían el pasaje de la Resolución 1406. Se incorporó sin modificar el hash de los PDF originales.
2. **Estado jurídico:** queda probado un reclamo administrativo intimado y recurrido; no una deuda firme, pagada ni un daño cuantificado.
3. **Cierre contable:** la garantía de Macro cae a 163 mil pesos en 2011 y cero en 2012; esto no extingue por sí solo una comisión histórica.
4. **Dos métricas:** deuda total del fideicomiso BCRA y préstamos restringidos del banco se presentan separadas; no se restan ni concilian sin ledger.
5. **Cálculo:** las cifras de sensibilidad del primer período son ilustrativas y no se presentan como deuda. Faltan instructivo, imputación, arrastres y acto final.
6. **Reproducibilidad:** se hizo idempotente el enriquecimiento de notas de V180 y se eliminaron repeticiones acumuladas del catálogo.
""", encoding="utf-8")

local_census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V181.csv")
for s in sources:
    p = REPO / s["archivo_local"].lstrip("/")
    local_census.append({"source_id":s["id"],"institution":s["institucion"],"artifact":s["titulo"],"url":s["url_original"],"local_path":s["archivo_local"],"sha256":s["sha256"],"bytes":str(p.stat().st_size),"period_coverage":s["periodo_utilizado"],"variable_families":"BID1192;trust;commission;collateral;registry;appeal;closure","primary_source":"YES","preserved":"YES","method_breaks":"bank collateral/trust debt; claim/final debt; presence/absence","use_status":"E0_USABLE_WITH_STATED_LIMITS","caveat":s["nota"]})
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V181.csv", list({x["source_id"]:x for x in local_census}.values()))

prov = read_csv(HERE / "ARCHIVAL_PROVENANCE_V181.csv")
for s in sources:
    p = REPO / s["archivo_local"].lstrip("/")
    prov.append({"source_id":s["id"],"original_url":s["url_original"],"retrieval_url":s["url_original"],"capture_timestamp":"2026-09-01","cdx_digest":"N/A_OFFICIAL_DIRECT_DOWNLOAD","local_path":s["archivo_local"],"sha256":s["sha256"],"bytes":str(p.stat().st_size),"provenance_note":s["nota"]})
write_csv(HERE / "ARCHIVAL_PROVENANCE_V181.csv", list({x["source_id"]:x for x in prov}.values()))

with (HERE / "SOURCE_REFERENCES_V181.md").open("a", encoding="utf-8") as f:
    f.write("\n## V181 · Resolución 1406, garantía Macro y cierre registral BCRA\n")
    for s in sources:
        f.write(f"\n- `{s['id']}` · {s['titulo']} · {s['url_original']} · `{s['archivo_local']}` · `{s['sha256']}`\n")
with (HERE / "RETRIEVAL_LOG_V181.md").open("a", encoding="utf-8") as f:
    f.write("""
## V181

- La reauditoría visual de SIGEN recuperó la Resolución 1406/2014, la intimación a Macro y Credicoop, los recursos y la liquidación todavía pendiente.
- Se preservó la serie Banco Macro 20-F 2007-2015 y el índice SEC. Los préstamos afectados a MyPES II pasan de 19.241 mil pesos en 2006 a 163 mil en 2011 y cero en 2012.
- BCRA identifica al fideicomiso 10155/Macro Fiducia: deuda 3.331,10 mil en dic-2010, 630,30 mil en jun-2011 y 39,60 mil en dic-2011; no figura en el índice 2012S1.
- La comisión contractual es 0,75% anual sobre saldo no desembolsado frente a mínimo USD 8m trimestral. Las sensibilidades no son liquidación ni deuda.
- No se localizaron el acto 1406, su cálculo, los recursos ni la decisión final; ocho pedidos quedan DRAFT_NOT_SENT.
""")

SYNC.mkdir(parents=True, exist_ok=True)
sync_rows = [{"source_id":s["id"],"local_path":s["archivo_local"],"sha256":s["sha256"],"bytes":str((REPO/s["archivo_local"].lstrip("/")).stat().st_size)} for s in sources]
write_csv(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V181.csv", sync_rows)
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V181.csv", [{"source_id":s["id"],"url":s["url_original"],"retrieval":"DIRECT_OFFICIAL","status":"PRESERVED"} for s in sources])
(SYNC / "SOURCE_SYNC_REPORT_V181.md").write_text("# Sincronización V181\n\n- Catálogo 684/684; hashes válidos; brecha física 0.\n- 11 artefactos nuevos preservados: 6 PDF, 4 HTML SEC y 1 JSON SEC.\n- Seis PDF controlados visualmente en las páginas relevantes.\n- La ausencia en registros/20-F se conserva como control acotado, no como prueba de inexistencia jurídica.\n", encoding="utf-8")
(SYNC / "qa_source_sync_v181.py").write_text("""from pathlib import Path
import csv,hashlib
H=Path(__file__).resolve().parent; R=H.parents[4]
rows=list(csv.DictReader((H/'SOURCE_SYNC_FILE_MANIFEST_V181.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==11
for x in rows:
 p=R/x['local_path'].lstrip('/'); assert p.is_file() and p.stat().st_size==int(x['bytes']) and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
print('SOURCE SYNC V181 PASS · 11/11')
""", encoding="utf-8")

(HERE / "README_V181.md").write_text("""# Checkpoint V181

## Hallazgo principal

V181 convierte una mención enterrada en dos informes de SIGEN en una cadena probatoria separada: en noviembre de 2014 se habría emitido la Resolución 1406, intimando a Banco Macro y Banco Credicoop a pagar la comisión de compromiso de MyPES II. Los bancos y el fiduciario interpusieron reconsideración con jerárquico en subsidio; la liquidación seguía sin resolverse en los informes públicos de 2017/2019.

Esto prueba **intimación administrativa y controversia**, no deuda firme. No están preservados el acto, el monto, la fórmula aplicada, las notificaciones, los recursos, los dictámenes, la decisión final, el pago ni la provisión.

## Fórmula y límite matemático

AGN transcribe la cláusula ejecutada: el fiduciario debía solicitar al menos USD 8 millones cada tres meses y, ante incumplimiento, resarcir con 0,75% anual sobre el saldo no desembolsado, pagadero semestralmente. Al 31/12/2005 se habían ejecutado USD 831.246,65: brecha bruta USD 7.168.753,35. Según convención temporal, una sensibilidad simple arroja entre USD 13.441,41 y USD 20.162,12. **No es una deuda calculada**: faltan el instructivo UCP del 27/12/2005, la imputación por banco, el arrastre de defectos/excesos, las dispensas y el acto final.

## Cierre bancario y registral

- Banco Macro informa préstamos afectados a MyPES II (miles de pesos): 19.241 (2006), 12.801 (2007), 20.367 (2008), 9.876 (2009), 2.599 (2010), 163 (2011) y 0 (2012).
- El BCRA identifica al fideicomiso 10155/Macro Fiducia con deuda total de 3.331,10 mil pesos en diciembre 2010, 630,30 mil en junio 2011 y 39,60 mil en diciembre 2011, un único registro en situación normal.
- MyPES II ya no aparece en el índice BCRA del primer semestre 2012. La convergencia sugiere cierre de cartera/garantía, pero no sustituye el acto de liquidación.
- La métrica BCRA de deuda del fideicomiso y la métrica Macro de préstamos restringidos tienen bases distintas; no se restan.

## Estado probatorio seguro

- Cláusula y brecha bruta 2005: probadas por AGN.
- Resolución 1406/intimación/recursos: reportados reiteradamente por SIGEN.
- Deuda firme, daño, cobro, pago o responsabilidad indemnizatoria: no probados.
- Archivo: 684/684 fuentes físicas con SHA-256 válido; 11 nuevas.
- Solicitudes enviadas: 0; ocho objetos nuevos DRAFT_NOT_SENT.
- Panel bancario: 34 entidades; cobertura estricta 63,440604%.
""", encoding="utf-8")

(HERE / "VEREDICTO_V181.md").write_text("""# Veredicto V181

La afirmación defendible sube un escalón: existió una pretensión administrativa concreta por comisión de compromiso contra Macro y Credicoop y fue recurrida; además, la cartera/garantía MyPES II puede seguirse hasta su extinción contable y salida registral en 2012. La pretensión parece referirse a incumplimientos históricos, no a una garantía aún vigente en 2014. Sin Resolución 1406, instructivo, liquidaciones, recursos y decisión final no puede calificarse el monto como deuda firme ni daño. El expediente correcto ya no es una búsqueda genérica: son ocho paquetes documentales exactos y conciliables.
""", encoding="utf-8")

(HERE / "AUDITORIA_V181.md").write_text("""# Auditoría V181

- 684/684 fuentes físicas y SHA-256 válido; 11 artefactos nuevos.
- 6 PDF nuevos controlados visualmente en páginas relevantes; 4 HTML SEC y 1 JSON SEC con control de contenido.
- Reauditoría SIGEN: páginas 89 (octubre 2017) y 88 (febrero 2019).
- Serie Macro: 2006-2012; garantía 19.241 → 0 miles de pesos.
- Serie BCRA fideicomiso 10155: 3.331,10 → 630,30 → 39,60 miles de pesos; salida del índice 2012S1.
- Res. 1406: intimación y recursos reportados; acto/monto/firmeza/pago no localizados.
- Sensibilidades matemáticas marcadas SENSITIVITY_NOT_DEBT.
- Panel 34; cobertura 63,440604%; solicitudes 0; daño no probado.
""", encoding="utf-8")

(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V181_A_V182.md").write_text("""# Handover V181 → V182

## Cerrado
- Resolución 1406, intimación a Macro/Credicoop y recursos recuperados de SIGEN.
- Fórmula contractual de comisión y brecha bruta 2005 reconstruidas con límites.
- Serie de garantías Macro 2006-2012 preservada.
- Fideicomiso BCRA 10155/Macro Fiducia trazado hasta salida registral 2012.
- Ocho paquetes de prueba específicos definidos; ninguno enviado.

## Prioridad V182
1. Recuperar acto íntegro Res. 1406/2014 y expediente de origen.
2. Recuperar instructivo UCP 27/12/2005, liquidaciones por banco y arrastre 2006.
3. Recuperar notificaciones, recursos, dictámenes y decisión final.
4. Conciliar pagos/provisiones/cobros entre TGN, CGN, bancos y fiduciario.
5. Recuperar acto BCRA de baja y balance final del fideicomiso 10155.
6. Continuar el puente contable BID1192 → FONDYF/BNA sin mezclar métricas.
7. Mantener separados reclamo, deuda firme, pago, daño y responsabilidad.
""", encoding="utf-8")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V180.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint":"V181","date":"2026-09-01","master_catalog_entries":684,"physical_local_copies":684,"physical_local_hash_ok":684,"remaining_catalog_physical_or_hash_gaps":0,
    "state":"MYPESII_RES1406_INTIMATION_AND_APPEALS_REPORTED_MACRO_COLLATERAL_AND_BCRA_REGISTRY_EXIT_RECONSTRUCTED_FINAL_ACT_AMOUNT_DECISION_PAYMENT_OPEN",
    "analytical_promotion":"ADMINISTRATIVE_CLAIM_AND_REGISTRY_CLOSURE_ONLY_NO_FIRM_DEBT_OR_DAMAGE_PROMOTION_V181",
    "mypesii_res1406_reported_by_repeated_sigen":True,"mypesii_res1406_full_act_located":False,"mypesii_res1406_amount_located":False,"mypesii_res1406_appeals_reported":True,"mypesii_res1406_final_decision_located":False,"mypesii_res1406_payment_proved":False,
    "mypesii_commitment_clause_formula_corroborated":True,"mypesii_ucp_2005_instruction_located":False,"mypesii_2005_raw_shortfall_usd":"7168753.35","mypesii_sensitivity_is_debt":False,
    "mypesii_macro_collateral_series_2006_2012_reconstructed":True,"mypesii_macro_collateral_2012_thousand_ars":"0","mypesii_bcra_trust_10155_exit_2012_supported":True,"mypesii_bcra_registry_exit_legal_act_located":False,
    "mypesii_final_liquidation_balance_located":False,"bid1192_damage_or_appropriation_proved":False,"requests_submitted":0,"responses_received":0,
    "new_v181_sources":11,"v181_pdf_documents":6,"v181_pdf_relevant_pages_visually_inspected":7,"public_web_queries_v181":6,"strict_coverage_increment_v181_pp":"0",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V181.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

origins = read_csv(ORIGINS)
by_path = {row["path"]:row for row in origins}
for path in iter_files(HIST_ROOT):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"downloaded/preserved V181","note":"official Macro/SEC/BCRA artifact; verified"}
for path in iter_files(SYNC):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V181","note":"11-source synchronization"}
for path in HERE.iterdir():
    if path.is_file():
        by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V181","note":"Res1406/commission/collateral/registry checkpoint"}
for path in (AUDIT/"MASTER_LOCAL_HASH_VALIDATION_V181.csv", AUDIT/"SOURCE_BACKUP_CENSUS_V181.csv", AUDIT/"SOURCE_PRESERVATION_MISSING_V181.csv", AUDIT/"CURRENT_SOURCE_COMPLETENESS_V181.json"):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V181","note":"684-source completeness"}
write_csv(ORIGINS, list(by_path.values()), ["path","origin","note"])

transparency = CYCLE / "TRANSPARENCY_README.md"
body = transparency.read_text(encoding="utf-8-sig")
if "## V181 · Resolución 1406 y cierre registral MyPES II" not in body:
    body += "\n\n## V181 · Resolución 1406 y cierre registral MyPES II\n\nSIGEN reporta una intimación administrativa de noviembre de 2014 contra Macro y Credicoop por comisión de compromiso, recurrida por bancos y fiduciario y todavía sin liquidación resuelta en 2017/2019. Macro y BCRA permiten seguir la cartera/garantía hasta 2012. El acto 1406, monto, cálculo, recursos, decisión y pago siguen abiertos; no se promueve deuda firme ni daño. Archivo 684/684; solicitudes 0.\n"
    transparency.write_text(body, encoding="utf-8")
(REPO / "BACKUP_ACTUALIZACION_2026-09-01.md").write_text("# Backup de actualización · 2026-09-01\n\n- V181; 684/684 fuentes; 11 nuevas.\n- Res. 1406/2014: intimación Macro/Credicoop y recursos reportados por SIGEN; acto/monto/decisión/pago abiertos.\n- Comisión: mínimo USD 8m trimestral, 0,75% anual; brecha bruta 2005 USD 7.168.753,35; sensibilidad no es deuda.\n- Macro garantía 2006-2012: 19.241 → 0 miles de pesos.\n- BCRA fideicomiso 10155: 3.331,10 → 630,30 → 39,60 miles y salida del índice 2012S1.\n- Daño no probado; panel 34; cobertura 63,440604%; solicitudes 0.\n", encoding="utf-8")

(HERE / "qa_v181.py").write_text("""from pathlib import Path
import csv,hashlib,json
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==684
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
for sid,sentence in (("e0_bo_res967_2006_full_annex_contract_v179","V180 acredita que el modelo Res. 967 no estaba perfeccionado al 22/02/2008; no se lo trata como régimen operativo."),("e0_norm_res967_2006_mypesii_trust_v178","AGN 14/2010 informa que el contrato aprobado por Res. 967/2006 no estaba perfeccionado al 22/02/2008.")):
 note=next(x['nota'] for x in cat if x['id']==sid); assert note.count(sentence)==1
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V181.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==684 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V181.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V181' and co['master_catalog_entries']==684
assert co['mypesii_res1406_reported_by_repeated_sigen'] and co['mypesii_res1406_appeals_reported'] and not co['mypesii_res1406_full_act_located'] and not co['mypesii_res1406_final_decision_located'] and not co['mypesii_res1406_payment_proved']
assert co['mypesii_commitment_clause_formula_corroborated'] and not co['mypesii_ucp_2005_instruction_located'] and not co['mypesii_sensitivity_is_debt']
assert co['mypesii_macro_collateral_series_2006_2012_reconstructed'] and co['mypesii_bcra_trust_10155_exit_2012_supported'] and not co['mypesii_bcra_registry_exit_legal_act_located'] and not co['bid1192_damage_or_appropriation_proved']
assert len(rows('V181_SOURCE_BUNDLE.csv'))==11 and len(rows('V181_PDF_VISUAL_CONTROL.csv'))==6 and all(x['result'].startswith('PASS_RELEVANT_') for x in rows('V181_PDF_VISUAL_CONTROL.csv'))
assert len(rows('V181_HTML_CONTENT_CONTROL.csv'))==5 and all(x['result']=='PASS_CONTENT_CONTROL' for x in rows('V181_HTML_CONTENT_CONTROL.csv'))
assert len(rows('E0_BID1192_COMMITMENT_COMMISSION_DISPUTE_CHAIN_2005_2019_V181.csv'))==8
assert len(rows('E0_BID1192_RES1406_EVIDENCE_LADDER_V181.csv'))==6
assert len(rows('E0_BID1192_MACRO_COLLATERAL_TRAJECTORY_2006_2012_V181.csv'))==7
assert len(rows('E0_BID1192_BCRA_TRUST_CLOSURE_CROSSCHECK_2010_2012_V181.csv'))==4
assert len(rows('E0_BID1192_COMMISSION_ILLUSTRATIVE_SENSITIVITY_V181.csv'))==4 and all(x['legal_status']=='SENSITIVITY_NOT_DEBT' for x in rows('E0_BID1192_COMMISSION_ILLUSTRATIVE_SENSITIVITY_V181.csv'))
obj=rows('E0_V181_REQUEST_OBJECTS.csv'); assert {f'RO181_{x}' for x in range(69,77)}<={x['row_id'] for x in obj}; assert all(x['status']=='DRAFT_NOT_SENT' for x in obj); assert obj==rows('E0_V181_REQUEST_OBJECTS_V181.csv')
keys=rows('E0_REQUEST_SEARCH_KEY_MATRIX_V181.csv'); assert {f'SK181_{x}' for x in range(70,76)}<={x['key_id'] for x in keys}
panel=rows('FOUR_LEG_PASS_PANEL_V181.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
m=json.loads((H/'MANIFEST_V181.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V181' and m['parent_checkpoint']=='V180' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V181 QA PASS · 684/684 · new=11 · PDF=6 relevant-page visual · RES1406=REPORTED_CONTESTED · MACRO_COLLATERAL=2006-2012 · damage=NO · panel=34 · requests=0')
""", encoding="utf-8")

(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")
manifest_files = [{"path":p.name,"bytes":p.stat().st_size,"sha256":sha(p)} for p in sorted(HERE.iterdir(), key=lambda x:x.name.casefold()) if p.is_file() and p.name!="MANIFEST_V181.json"]
manifest = {
    "checkpoint":"V181","parent_checkpoint":"V180","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
    "exact_entities":34,"strict_coverage_pct":COVERAGE,"strict_asset_numerator_million_ars":NUMERATOR,"system_assets_million_ars":ASSETS,
    "new_promotions":[],"source_archive":"684/684; 11 new official artifacts","historical_finding":"Res1406 intimation/appeals reported; Macro collateral and BCRA registry closure reconstructed; act/amount/final decision/payment open",
    "mypesii_res1406":"REPORTED_CONTESTED_NOT_FINAL","mypesii_macro_collateral":"2006_2012_RECONSTRUCTED","mypesii_bcra_trust_10155":"EXIT_SUPPORTED_ACT_OPEN","commitment_sensitivity":"NOT_DEBT",
    "closed_network_gate":"NO","saf355_certifications":"0/5","executed_historical_bank_rows":"0/10","requests_submitted":0,"files":manifest_files,
}
(HERE / "MANIFEST_V181.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path":p.relative_to(REPO).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)} for p in iter_files(REPO) if p != global_manifest]
payload = {"checkpoint":"V181","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),"strict_coverage_pct":COVERAGE,"exact_entities":34,"closed_network_gate":"NO","source_audit":"684 master; 684 physical SHA-valid","historical_workstream":"Res1406/commission/collateral/registry reconstructed; act/amount/decision/payment/damage open; drafts not sent","file_count_excluding_manifest":len(global_files),"files":global_files}
tmp = global_manifest.with_suffix(".json.V181tmp")
tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
tmp.replace(global_manifest)
print("V181 BUILD PASS · catalog=684/684 · new=11 · PDF=6 relevant visual · RES1406=REPORTED_CONTESTED · MACRO_COLLATERAL=2006-2012 · panel=34 · requests=0")
