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
PARENT = CYCLE / "checkpoints" / "V176"
AUDIT = CYCLE / "source_audit"
SYNC = CYCLE / "inputs" / "source_sync" / "v177"
HIST_ROOT = CYCLE / "inputs" / "historical_retrieval" / "v177"
HIST = HIST_ROOT / "binaries"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"
COVERAGE = "63.4406041403540997520463142785031521252747951992299547614348265414453439585848248058817492708499966268585997481191265825"
NUMERATOR = "61345602.215"
ASSETS = "96697695.5"
EXCLUDED = {".git", "__pycache__", "tmp", "node_modules"}


FILES = {
    "sigen2017": HIST / "hacienda_sigen_observations_october_2017.pdf",
    "sigen2019": HIST / "hacienda_sigen_observations_february_2019.pdf",
    "cgn2019": HIST / "cgn_cuenta_inversion_2019_ejecucion_presupuestaria.pdf",
}
EXPECTED = {
    FILES["sigen2017"]: (3214357, "1df21a1cdb3bc57dbcfa299ac5c9b5e693e58ead535c338b9df70189be36011e"),
    FILES["sigen2019"]: (4587378, "9cca55c35e920fd4fe290e6f069cc800166d96d3dfeafa08d00cefcd8f2ed14b"),
    FILES["cgn2019"]: (4121927, "9078603aa0f3ad78c4a8292be5130f25fe2aece5748fe87c67a1405f18a36101"),
}
OLD_2008 = CYCLE / "inputs" / "historical_retrieval" / "v148" / "binaries" / "cgn_account_2008_uepex_closing_exception.pdf"
OLD_2009 = CYCLE / "inputs" / "historical_retrieval" / "v155" / "binaries" / "cgn_cuenta_2009_uepex_note_sisio_chain.pdf"


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
        "MANIFEST_V176.json", "README_V176.md", "VEREDICTO_V176.md", "AUDITORIA_V176.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V176_A_V177.md", "V176_SOURCE_BUNDLE.csv",
        "V176_PUBLIC_SEARCH_LOG.csv", "V176_PDF_VISUAL_CONTROL.csv", "V176_PDF_VISUAL_AND_TEXT_CONTROL.csv",
    }
    for src in sorted(PARENT.iterdir(), key=lambda p: p.name.casefold()):
        if not src.is_file() or src.name in skip or src.name.startswith(("build_", "qa_")):
            continue
        dst = HERE / src.name.replace("V176", "V177")
        dst.write_text(src.read_text(encoding="utf-8-sig").replace("V176", "V177"), encoding="utf-8")


HERE.mkdir(parents=True, exist_ok=True)
clone_parent()
for path, (size, digest) in EXPECTED.items():
    assert path.is_file() and path.stat().st_size == size and sha(path) == digest
assert OLD_2008.is_file() and OLD_2009.is_file()

source_specs = [
    {
        "id":"e0_sigen_account2016_bid1192_high_impact_observations_v177",
        "institucion":"Sindicatura General de la Nación",
        "titulo":"Cuenta de Inversión 2016 · observaciones de alto impacto del BID 1192/OC-AR",
        "url":"https://www.argentina.gob.ar/sites/default/files/informe_sigen_octubre_2017.pdf",
        "path":FILES["sigen2017"], "publication":"2017-10", "code":"SIGEN · Cuenta de Inversión 2016 · PDF 87-89 y 92",
        "period":"2014-2017",
        "note":"Prueba observaciones recurrentes y sin acción correctiva del programa BID 1192/OC-AR, ausencia de estados 2015, información contable desactualizada desde agosto de 2014 y falta de verificación del Cuadro 13.3 pese a movimientos 2016.",
    },
    {
        "id":"e0_sigen_account2017_bid1192_high_impact_observations_v177",
        "institucion":"Sindicatura General de la Nación",
        "titulo":"Cuenta de Inversión 2017 · persistencia de observaciones del BID 1192/OC-AR",
        "url":"https://www.argentina.gob.ar/sites/default/files/informe_sigen_febrero_2019.pdf",
        "path":FILES["sigen2019"], "publication":"2019-02", "code":"SIGEN · Cuenta de Inversión 2017 · PDF 85 y 88",
        "period":"2014-2018",
        "note":"Reitera ausencia de respaldo de cierre de MP0191 y falta de estados 2015; conserva la acción Sin acción correctiva y muestra que la etiqueta recurrente puede cambiar entre compilaciones.",
    },
    {
        "id":"e0_cgn_account2019_bid1192_missing_information_accounts_v177",
        "institucion":"Contaduría General de la Nación",
        "titulo":"Cuenta de Inversión 2019 · BID 1192/OC-AR sin información y saldos de referencia 2018",
        "url":"https://www.argentina.gob.ar/sites/default/files/separatai-ejec.presupuestaria-cuenta2019.pdf",
        "path":FILES["cgn2019"], "publication":"2020", "code":"Cuenta de Inversión 2019 · PDF 76-77 y 167-169",
        "period":"2017-2019",
        "note":"Prueba que desde 2017 se observaban aspectos sin respuesta, que al cierre 2019 no se presentó información del programa y preserva 16 cuentas con saldos de referencia 2018 por ARS 824.861.366,21.",
    },
]

sources = []
for spec in source_specs:
    sources.append({
        "id":spec["id"], "tema":"ciclo_ajuste_e0_fiscal", "institucion":spec["institucion"],
        "titulo":spec["titulo"], "url_original":spec["url"],
        "archivo_local":"/" + spec["path"].relative_to(REPO).as_posix(),
        "fecha_descarga":"2026-09-01", "fecha_publicacion":spec["publication"],
        "codigo_serie":spec["code"], "periodo_utilizado":spec["period"],
        "tipo":"PDF oficial preservado · control visual de páginas relevantes",
        "sha256":EXPECTED[spec["path"]][1], "nota":spec["note"],
    })

catalog = read_csv(CATALOG)
catalog_fields = list(catalog[0])
by_id = {row["id"]:row for row in catalog}
for source in sources:
    by_id[source["id"]] = source
catalog = list(by_id.values())
write_csv(CATALOG, catalog, catalog_fields)
assert len(catalog) == len({row["id"] for row in catalog}) == 630

audit = []
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    actual = sha(path) if path.is_file() else ""
    audit.append({
        "id":row["id"], "archivo_local":row["archivo_local"], "exists":str(path.is_file()),
        "sha_catalog":row["sha256"].lower(), "sha_actual":actual,
        "hash_ok":str(path.is_file() and bool(row["sha256"]) and actual == row["sha256"].lower()),
    })
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V177.csv", audit)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V177.csv", audit)
missing = [row for row in audit if row["hash_ok"] != "True"]
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V177.csv", missing, list(audit[0]))
assert not missing

write_csv(HERE / "E0_BID1192_LONGITUDINAL_EVIDENCE_CHAIN_V177.csv", [
    {"row_id":"BL177_01","date_or_period":"31/12/2008","record":"Cuenta 2008 Anexo 4.28","actor":"CGN/SAF 357","finding":"BID 1192 con información rezagada desde cierre 2005; múltiples cuentas con incoherencias, faltas de extracto y tipos de cambio no reglamentarios","action_or_state":"hallazgos financieros individualizados","causal_status":"TARGET_CANDIDATE_NOT_JOINED_TO_3672","source":"Cuenta 2008 PDF 118-120"},
    {"row_id":"BL177_02","date_or_period":"2009","record":"Notas 0120/09 y 3672/09","actor":"CGN/SIGEN/UAI","finding":"informe pormenorizado de gestión UEPEX; SIGEN ordena incorporar sus hallazgos a SISIO","action_or_state":"seguimiento y regularización por UAI","causal_status":"PROGRAM_ROW_CROSSWALK_OPEN","source":"Cuenta 2009 PDF 77-78"},
    {"row_id":"BL177_03","date_or_period":"31/12/2009","record":"Cuenta 2009 Anexo 4.28","actor":"CGN/SAF 362","finding":"continúan 14 cuentas exactas de la lista observada en 2008; errores de saldo inicial y consistencia, MP0191 sin cierre confirmado","action_or_state":"inconsistencias preservadas por cuenta","causal_status":"EXACT_ACCOUNT_CONTINUITY_PROVED","source":"Cuenta 2009 PDF 143-145"},
    {"row_id":"BL177_04","date_or_period":"2014-2015","record":"observación compilada Cuenta 2016","actor":"UAI/SIGEN/Ministerio de Producción","finding":"estados 2015 no emitidos; información contable desactualizada desde agosto 2014","action_or_state":"Sin acción correctiva informada; recurrente SI","causal_status":"PERSISTENT_REPORTING_FAILURE","source":"SIGEN 2017 PDF 89"},
    {"row_id":"BL177_05","date_or_period":"ejercicio 2016","record":"observación de alto impacto","actor":"UAI/SIGEN/Ministerio de Producción","finding":"sin estados patrimoniales; saldo total 489607291.57→685073367.12; no pudo verificarse Cuadro 13.3","action_or_state":"área alega préstamo finalizado; movimientos comprobados","causal_status":"UNVERIFIED_REPORTED_BALANCE_NOT_DAMAGE","source":"SIGEN 2017 PDF 92"},
    {"row_id":"BL177_06","date_or_period":"Cuenta 2017 / auditoría 2018","record":"compilación SIGEN febrero 2019","actor":"UAI/SIGEN/Ministerio de Producción","finding":"MP0191 sin respaldo de cierre y estados 2015 aún ausentes","action_or_state":"Sin acción correctiva","causal_status":"PERSISTENT_CONTROL_GAP","source":"SIGEN 2019 PDF 85 y 88"},
    {"row_id":"BL177_07","date_or_period":"29/08/2019","record":"reunión DAIF","actor":"CGN; programa; SAF 362; UAI","finding":"observaciones desde 2017 sin respuestas; clasificación UEPEX versus Fondo Fiduciario sin resolver","action_or_state":"convocatoria interáreas","causal_status":"ESCALATED_UNRESOLVED_CLASSIFICATION","source":"Cuenta 2019 PDF 76-77"},
    {"row_id":"BL177_08","date_or_period":"31/12/2019","record":"Cuenta 2019 Anexo 4.35","actor":"CGN/SAF 362/programa","finding":"no se presentó información 2019; se preservan 16 saldos de referencia 2018 por ARS 824861366.21","action_or_state":"movimientos 2019 vacíos; última referencia anterior","causal_status":"MISSING_CURRENT_INFORMATION_WITH_PRIOR_BALANCE","source":"Cuenta 2019 PDF 167-169"},
])

account_values = [
    ("2119/45","22384741.80","YES","YES"), ("54451/95","45925902.21","NO","NO"),
    ("210010000","3066718.24","YES","NO"), ("MI 4285","19659140.06","YES","YES"),
    ("MS 4285","240397198.95","YES","YES"), ("MY 4002","569350.57","YES","YES"),
    ("MY 4003","481443.72","YES","YES"), ("MY 4004","1183046.44","YES","YES"),
    ("MY 4005","7995.84","YES","YES"), ("MY 4006","959708.51","YES","YES"),
    ("MYUEC 1","160399286.55","YES","YES"), ("MYUEC","0.00","YES","YES"),
    ("COBCAP","176877658.03","YES","YES"), ("COBINT","138589654.14","YES","YES"),
    ("FP1192","14359521.15","YES","YES"), ("FDOGTOS","0.00","YES","YES"),
]
account_rows = []
for index, (account, value, p2008, p2009) in enumerate(account_values, 1):
    account_rows.append({
        "row_id":f"AC177_{index:02d}", "program":"BID 1192/OC-AR", "account_id":account,
        "present_2008":p2008, "present_2009":p2009, "present_reference_2018":"YES",
        "reference_2018_ars":value, "reported_2019_current_data":"NO",
        "identity_rule":"exact account code within same loan/program; SAF reorganization does not break program identity",
        "limit":"2018 amount is a prior-period reference printed in Cuenta 2019; not a verified 2019 closing balance",
    })
write_csv(HERE / "E0_BID1192_ACCOUNT_ID_CONTINUITY_V177.csv", account_rows)
assert len(account_rows) == 16
assert sum(row["present_2008"] == "YES" for row in account_rows) == 15
assert sum(row["present_2009"] == "YES" for row in account_rows) == 14
assert sum(row["present_2008"] == row["present_2009"] == "YES" for row in account_rows) == 14

balance_total = sum(Decimal(row["reference_2018_ars"]) for row in account_rows)
assert balance_total == Decimal("824861366.21")
write_csv(HERE / "E0_BID1192_QUANTIFIED_UNVERIFIED_BALANCES_V177.csv", [
    {"row_id":"QB177_01","period":"2016 opening","amount_ars":"489607291.57","meaning":"saldo total declarado al inicio; hubo movimientos","verification":"no verificable por ausencia de estados patrimoniales","calculation":"source value","limit":"no es daño ni saldo bancario certificado"},
    {"row_id":"QB177_02","period":"2016 closing","amount_ars":"685073367.12","meaning":"saldo total declarado al cierre","verification":"Cuadro 13.3 no pudo verificarse","calculation":"source value","limit":"no es daño ni saldo bancario certificado"},
    {"row_id":"QB177_03","period":"2016 movement in reported total","amount_ars":"195466075.55","meaning":"cierre menos apertura","verification":"aritmética reproducida; sustancia no verificada","calculation":"685073367.12-489607291.57","limit":"variación nominal; no apropiación"},
    {"row_id":"QB177_04","period":"2018 references printed in Cuenta 2019","amount_ars":"824861366.21","meaning":"suma de 16 saldos por cuenta informados por referentes para 2018","verification":"suma reproducida; información 2019 ausente","calculation":"sumatorio 16 cuentas","limit":"no tratar como cierre 2019 ni comparar causalmente sin homogeneizar alcance"},
    {"row_id":"QB177_05","period":"2018 reference minus 2016 closing","amount_ars":"139787999.09","meaning":"diferencia nominal descriptiva entre agregados publicados","verification":"aritmética reproducida","calculation":"824861366.21-685073367.12","limit":"comparabilidad de alcance, valuación y corte no probada"},
])

write_csv(HERE / "E0_BID1192_RECURRENT_FLAG_TRAJECTORY_V177.csv", [
    {"row_id":"RF177_01","observation_key":"Cuenta 2015 · cierre MP0191 sin respaldo","snapshot":"Cuenta 2016 / SIGEN octubre 2017","action":"Sin acción correctiva informada","recurrent":"SI","interpretation":"falla recurrente explícita"},
    {"row_id":"RF177_02","observation_key":"Cuenta 2015 · cierre MP0191 sin respaldo","snapshot":"Cuenta 2017 / SIGEN febrero 2019","action":"Sin acción correctiva","recurrent":"SI","interpretation":"persistencia textual y de clasificación"},
    {"row_id":"RF177_03","observation_key":"estados 2015 no emitidos; contabilidad desactualizada desde agosto 2014","snapshot":"Cuenta 2016 / SIGEN octubre 2017","action":"Sin acción correctiva informada","recurrent":"SI","interpretation":"falla recurrente explícita"},
    {"row_id":"RF177_04","observation_key":"estados 2015 no emitidos; contabilidad desactualizada desde agosto 2014","snapshot":"Cuenta 2017 / SIGEN febrero 2019","action":"Sin acción correctiva","recurrent":"NO","interpretation":"la etiqueta cambió aunque el texto subsiste; no usar recurrente como ID durable"},
    {"row_id":"RF177_05","observation_key":"2016 sin estados; Cuadro 13.3 no verificable","snapshot":"Cuenta 2016 / SIGEN octubre 2017","action":"Sin acción correctiva informada en el grupo","recurrent":"NO","interpretation":"observación nueva del ejercicio; no contradice las recurrencias anteriores"},
])

write_csv(HERE / "E0_BID1192_RESPONSIBILITY_AND_EVIDENCE_LIMITS_V177.csv", [
    {"row_id":"RL177_01","proposition":"responsabilidad de información primaria","evidence":"Decreto 1344/07 art. 6 citado por CGN: SAF actúa como nexo y eleva documentación requerida para Cuenta","proved":"YES","not_proved":"responsabilidad personal individual"},
    {"row_id":"RL177_02","proposition":"deber de veracidad y verificabilidad","evidence":"marco SIGEN Cuenta 2016: responsables de veracidad, objetividad, verificabilidad, integridad, razonabilidad y confiabilidad","proved":"YES","not_proved":"dolo o culpa individual"},
    {"row_id":"RL177_03","proposition":"préstamo finalizado no extingue deber de rendición","evidence":"en 2016 hubo movimientos y saldo variable; SIGEN no pudo verificar sin estados","proved":"CONTROL_DUTY_PERSISTS_FOR_REPORTED_MOVEMENTS","not_proved":"ilegalidad sustantiva de cada movimiento"},
    {"row_id":"RL177_04","proposition":"continuidad objetiva del programa","evidence":"mismo BID 1192 y 14 IDs de cuenta comunes en 2008, 2009 y referencia 2018","proved":"YES","not_proved":"misma observación SISIO o mismo responsable orgánico"},
    {"row_id":"RL177_05","proposition":"vínculo con Nota 3672","evidence":"2008 tiene hallazgos; 3672 ordenó incorporar los hallazgos del informe 0120/09","proved":"CANDIDATE_SCOPE_ONLY","not_proved":"crosswalk fila por fila, alta SISIO, usuario, fecha y disposición"},
    {"row_id":"RL177_06","proposition":"daño o apropiación","evidence":"hay diferencias, falta de respaldo y datos no verificables","proved":"NO","not_proved":"daño, beneficiario, apropiación, enriquecimiento o nexo causal bancario"},
])

write_csv(HERE / "E0_NOTE_3672_BID1192_TARGET_CROSSWALK_REQUEST_V177.csv", [
    {"field_group":"origin","required_fields":"Nota 0120/09; informe y anexos; página/fila; hallazgo; cuenta; importe","known_anchor":"BID 1192; SAF 357; cuentas Anexo 4.28 2008","closure_rule":"documento original o índice archivístico con unión inequívoca"},
    {"field_group":"instruction","required_fields":"Nota 3672/09; cuerpo; fecha; destinatarios; adjuntos; área/persona firmante","known_anchor":"cargo firmante Síndico General; orden SISIO","closure_rule":"cuerpo firmado y remito/acuse"},
    {"field_group":"SISIO","required_fields":"entidad; UAI; informe número/fecha; observación; título; sector; hallazgo; recomendación","known_anchor":"programa BID 1192 y 14 cuentas persistentes","closure_rule":"exportación exacta, no búsqueda por texto resumido"},
    {"field_group":"history","required_fields":"estado; motivo; comentario; acción; cada fecha; usuario; soporte; cierre","known_anchor":"recurrencia y acción cambian entre compilaciones","closure_rule":"historial no sobrescrito de todos los estados"},
    {"field_group":"financial","required_fields":"SAF; programa; cuenta; moneda; saldo; debe; haber; extracto; cuadro 13.2/13.3; SIDIF","known_anchor":"2008, 2009 y 16 referencias 2018","closure_rule":"ledger antes/después conciliable por cuenta"},
    {"field_group":"outcome","required_fields":"corregida; pendiente; no regularizable; sin acción; razón; acto; fecha","known_anchor":"préstamo finalizado no equivale a corrección","closure_rule":"categorías mutuamente excluyentes y soporte de cierre"},
])

search_keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V177.csv")
search_keys += [
    {"key_id":"SK177_45","request_id":"REQ155_SIGEN","key_group":"program_contract","exact_key":"Programa Global de Crédito MiPyME + BID 1192/OC-AR + Decreto 1273/2012 FONDYF","search_purpose":"identificar filas del mismo programa pese a cambio SAF 357→362","source_or_basis":"Cuenta 2008/2009; SIGEN 2017/2019; Cuenta 2019","caveat":"programa común no prueba misma observación"},
    {"key_id":"SK177_46","request_id":"REQ155_SIGEN","key_group":"account_ids","exact_key":"2119/45;210010000;MI4285;MS4285;MY4002-4006;MYUEC1;MYUEC;COBCAP;COBINT;FP1192;FDOGTOS","search_purpose":"buscar alta SISIO y expedientes por cuenta exacta","source_or_basis":"14 cuentas comunes 2008/2009/2018","caveat":"normalizar espacios, guiones y ceros"},
    {"key_id":"SK177_47","request_id":"REQ133_ECON","key_group":"2017_notes","exact_key":"04854651SSFP#MP/2017;7813292/SSFP#MP/2017","search_purpose":"recuperar explicación préstamo finalizado y anexos","source_or_basis":"SIGEN Cuenta 2016 PDF 92","caveat":"texto citado no sustituye notas"},
    {"key_id":"SK177_48","request_id":"REQ133_ECON","key_group":"meeting","exact_key":"reunión DAIF 29/08/2019 BID 1192 CGN SAF362 UAI","search_purpose":"recuperar minuta, convocatoria, asistentes y compromisos","source_or_basis":"Cuenta 2019 PDF 76-77","caveat":"mención narrativa no prueba resultado"},
    {"key_id":"SK177_49","request_id":"REQ155_SIGEN","key_group":"observation_text","exact_key":"MP0191 cierre sin respaldo; estados 2015 no emitidos; contabilidad desactualizada agosto 2014; saldo 489607291.57→685073367.12","search_purpose":"localizar informes UAI fuente y filas SISIO","source_or_basis":"SIGEN 2017/2019","caveat":"buscar importes con variantes de separador"},
]
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V177.csv", search_keys)

objects = read_csv(HERE / "E0_V177_REQUEST_OBJECTS.csv")
objects += [
    {"row_id":"RO177_44","object_id":"SIGEN_BID1192_SISIO_2008_CROSSWALK","custodian":"SIGEN · SISIO/UAI Producción/Archivo","exact_record":"filas SISIO vinculadas al BID 1192/OC-AR y hallazgos Cuenta 2008/Nota 3672","period":"2008-último estado","minimum_fields":"clave compuesta; cuenta; hallazgo; recomendación; origen 0120/09/3672; historial; soporte","closure_rule":"exportación íntegra o negativo técnico por tablas/campos","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO177_45","object_id":"UAI_BID1192_SOURCE_REPORTS","custodian":"UAI Ministerio de Producción/Economía · SIGEN","exact_record":"informes UAI fuente de las observaciones BID 1192 compiladas en Cuentas 2016 y 2017","period":"2014-2018","minimum_fields":"número; fecha; alcance; papeles; observaciones; responsables; descargos; acciones; anexos","closure_rule":"cuerpo y anexos completos, no sólo compilación SIGEN","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO177_46","object_id":"CGN_BID1192_2019_MEETING_FILE","custodian":"CGN · DAIF/Mesa/Archivo","exact_record":"convocatoria, minuta y seguimiento de reunión 29/08/2019 BID 1192","period":"2017-2020","minimum_fields":"convocatoria; asistentes; agenda; clasificación UEPEX/Fondo; compromisos; plazos; respuestas; cierre","closure_rule":"expediente/minuta y resultado o negativo fundado","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO177_47","object_id":"BID1192_BANK_LEDGER_AND_STATEMENTS","custodian":"SAF 362 · programa · BCRA/TGN/CGN","exact_record":"ledger y extractos de 16 cuentas BID 1192 referenciadas para 2018 y omitidas en 2019","period":"2008-2019","minimum_fields":"cuenta; moneda; saldo inicial; debe; haber; saldo final; extracto; conciliación; fecha; firmante","closure_rule":"ledger por cuenta conciliable con extracto y Cuadro 13","status":"DRAFT_NOT_SENT"},
]
write_csv(HERE / "E0_V177_REQUEST_OBJECTS.csv", objects)
write_csv(HERE / "E0_V177_REQUEST_OBJECTS_V177.csv", objects)

request_package = HERE / "E0_REQUEST_PACKAGE_V177.md"
with request_package.open("a", encoding="utf-8") as f:
    f.write("\n## V177 · candidato BID 1192/OC-AR\n\nLa continuidad del programa y 14 cuentas quedó probada entre 2008, 2009 y las referencias 2018. Solicitar crosswalk exacto 0120/09→3672/09→SISIO; informes UAI fuente; notas 04854651 y 7813292; expediente de la reunión 29/08/2019; contrato/clasificación UEPEX-Fondo; y ledger/extractos de las 16 cuentas. No equiparar préstamo finalizado, no recurrente o ausencia de información con corrección. Estado: DRAFT_NOT_SENT.\n")

public_log = [
    {"query_id":"PS177_01","query":"sitio oficial + BID 1192 + Cuenta de Inversión 2008 + SISIO","result":"sin fila SISIO 2008 exacta; localizó compilaciones posteriores","artifact":"SIGEN 2017/2019","limit":"no crosswalk 3672"},
    {"query_id":"PS177_02","query":"sitio oficial + BID 1192 + Sin acción correctiva","result":"localizó observaciones SIGEN Cuentas 2016 y 2017","artifact":"dos PDF oficiales preservados","limit":"compilaciones, no informes UAI fuente"},
    {"query_id":"PS177_03","query":"sitio oficial + BID 1192 + desde el año 2017","result":"localizó Cuenta 2019, reunión 29/08/2019 y omisión informativa","artifact":"Cuenta 2019 preservada","limit":"sin minuta ni respuesta"},
    {"query_id":"PS177_04","query":"sitio oficial + incoherencias entre movimientos y saldo final","result":"reconstrucción desde anexos 2008/2009 ya preservados","artifact":"Anexos 4.28","limit":"no índice SISIO"},
    {"query_id":"PS177_05","query":"sitio oficial + 1192/OC-AR + Cuenta de Inversión","result":"cadena normativa y contable localizada","artifact":"Decreto 1273/12 y Cuentas","limit":"norma no prueba cumplimiento"},
    {"query_id":"PS177_06","query":"sitio oficial + 1192/OC-AR + no se dio cumplimiento","result":"saldo 2016 y falta de estados localizada","artifact":"SIGEN 2017 PDF 92","limit":"no daño probado"},
]
write_csv(HERE / "V177_PUBLIC_SEARCH_LOG.csv", public_log)

visual = [
    {"control_id":"PDF177_01","source_id":"e0_cgn_account_2008_uepex_closing_exception","pdf_pages":"118-121","target":"BID 1192 · cuentas y comentarios 31/12/2008","result":"PASS_LEGIBLE_COMPLETE","limit":"candidate rows; no SISIO ID"},
    {"control_id":"PDF177_02","source_id":"e0_cgn_account_2009_uepex_note_sisio_chain","pdf_pages":"77-78;143-145","target":"Notas 0120/3672, circuito SISIO y cuentas BID 1192 en 2009","result":"PASS_LEGIBLE_COMPLETE","limit":"crosswalk fila por fila ausente"},
    {"control_id":"PDF177_03","source_id":sources[0]["id"],"pdf_pages":"87-89;92","target":"recurrencia, acción y saldo no verificable 2016","result":"PASS_LEGIBLE_COMPLETE","limit":"compilación SIGEN"},
    {"control_id":"PDF177_04","source_id":sources[1]["id"],"pdf_pages":"85;88","target":"persistencia 2017 y cambio de bandera recurrente","result":"PASS_LEGIBLE_COMPLETE","limit":"no historial SISIO"},
    {"control_id":"PDF177_05","source_id":sources[2]["id"],"pdf_pages":"76-77;167-169","target":"reunión 2019, omisión y 16 saldos 2018","result":"PASS_LEGIBLE_COMPLETE","limit":"2019 sin movimientos informados"},
]
write_csv(HERE / "V177_PDF_VISUAL_CONTROL.csv", visual)

bundle = [
    {"role":"V177_PREEXISTING_TARGET_SOURCE","path":"/" + OLD_2008.relative_to(REPO).as_posix(),"url":"https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/sep/uepex.htm","bytes":str(OLD_2008.stat().st_size),"sha256":sha(OLD_2008),"analytic_use":"filas bancarias BID 1192 al cierre 2008"},
    {"role":"V177_PREEXISTING_TARGET_SOURCE","path":"/" + OLD_2009.relative_to(REPO).as_posix(),"url":"https://www.economia.gob.ar/hacienda/cgn/cuenta/2009/sep/uepex.htm","bytes":str(OLD_2009.stat().st_size),"sha256":sha(OLD_2009),"analytic_use":"Notas 0120/3672, método y filas BID 1192 al cierre 2009"},
]
for source in sources:
    path = REPO / source["archivo_local"].lstrip("/")
    bundle.append({"role":"V177_NEW_OFFICIAL_SOURCE","path":source["archivo_local"],"url":source["url_original"],"bytes":str(path.stat().st_size),"sha256":source["sha256"],"analytic_use":source["nota"]})
write_csv(HERE / "V177_SOURCE_BUNDLE.csv", bundle)

SYNC.mkdir(parents=True, exist_ok=True)
sync = []
for source in sources:
    path = REPO / source["archivo_local"].lstrip("/")
    sync.append({"role":"V177_PUBLIC_SOURCE","relative_path":source["archivo_local"],"source_url":source["url_original"],"size_bytes":str(path.stat().st_size),"sha256":source["sha256"],"format_verification":"PDF_VISUAL_PASS_TLS_VALID"})
write_csv(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V177.csv", sync)
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V177.csv", public_log)
(SYNC / "SOURCE_SYNC_REPORT_V177.md").write_text("# Sincronización V177\n\n- Catálogo 630/630; hash válido; brecha 0.\n- Tres PDF oficiales nuevos preservados.\n- Veinte páginas relevantes de cinco PDF controladas visualmente.\n- Cadena BID 1192 2008→2019 y 14 cuentas comunes probadas; enlace SISIO/3672 abierto.\n", encoding="utf-8")
(SYNC / "qa_source_sync_v177.py").write_text("""from pathlib import Path
import csv,hashlib
root=Path(__file__).resolve().parents[5]
rows=list(csv.DictReader(Path(__file__).with_name('SOURCE_SYNC_FILE_MANIFEST_V177.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==3
for r in rows:
 p=root/r['relative_path'].lstrip('/'); assert p.is_file() and p.stat().st_size==int(r['size_bytes']) and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
print('SOURCE SYNC V177 PASS · 3/3')
""", encoding="utf-8")

census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V177.csv")
for source in sources:
    path = REPO / source["archivo_local"].lstrip("/")
    census.append({"source_id":source["id"],"institution":source["institucion"],"artifact":source["titulo"],"url":source["url_original"],"local_path":source["archivo_local"],"sha256":source["sha256"],"bytes":str(path.stat().st_size),"period_coverage":source["periodo_utilizado"],"variable_families":"UEPEX;BID1192;account_ids;recurrence;actions;balances;responsibility","primary_source":"YES","preserved":"YES","method_breaks":"compiled observations and prior-period references; no SISIO crosswalk","use_status":"E0_USABLE_LONGITUDINAL_TARGET_CANDIDATE","caveat":source["nota"]})
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V177.csv", list({row["source_id"]:row for row in census}.values()))

prov = read_csv(HERE / "ARCHIVAL_PROVENANCE_V177.csv")
for source in sources:
    path = REPO / source["archivo_local"].lstrip("/")
    prov.append({"source_id":source["id"],"original_url":source["url_original"],"retrieval_url":source["url_original"],"capture_timestamp":"2026-09-01","cdx_digest":"N/A_OFFICIAL_DIRECT_TLS_VALID","local_path":source["archivo_local"],"sha256":source["sha256"],"bytes":str(path.stat().st_size),"provenance_note":source["nota"]})
write_csv(HERE / "ARCHIVAL_PROVENANCE_V177.csv", list({row["source_id"]:row for row in prov}.values()))

with (HERE / "SOURCE_REFERENCES_V177.md").open("a", encoding="utf-8") as f:
    f.write("\n## V177 · continuidad BID 1192/OC-AR\n")
    for source in sources:
        f.write(f"\n- `{source['id']}` · {source['titulo']} · {source['url_original']} · `{source['archivo_local']}` · `{source['sha256']}`\n")
with (HERE / "RETRIEVAL_LOG_V177.md").open("a", encoding="utf-8") as f:
    f.write("\n## V177\n\n- Tres PDF oficiales nuevos preservados.\n- BID 1192 trazado entre anexos 2008/2009, observaciones SIGEN 2016/2017 y Cuenta 2019.\n- Catorce cuentas exactas comunes a 2008, 2009 y referencias 2018.\n- Suma 2018 de 16 referencias: ARS 824.861.366,21; datos corrientes 2019 ausentes.\n- No se localizó la fila SISIO que una este candidato a Nota 3672.\n")

recovery = f"""# Recuperación archivística · V177

La búsqueda por programa y cuentas exactas localizó una cadena material del BID 1192/OC-AR: hallazgos bancarios 2008, continuidad en 2009, observaciones de alto impacto y sin acción correctiva en 2017/2019, y ausencia de información corriente en Cuenta 2019. Catorce cuentas coinciden en 2008, 2009 y las referencias 2018; dieciséis referencias 2018 suman ARS 824.861.366,21. La cadena prueba persistencia del objeto y del déficit de rendición, no que cada fila provenga de Nota 3672 ni daño o apropiación. Deben recuperarse crosswalk SISIO, informes UAI, notas 2017, reunión 29/08/2019, contrato/clasificación y extractos. Archivo 630/630; panel 34 y {COVERAGE}%; solicitudes 0; SAF355 0/5; ejecución 0/10.
"""
for name in ("E0_PLAN_2009_ARCHIVE_RECOVERY_NOTE_V177.md", "E0_SIGEN_ARCHIVAL_INDEX_RECOVERY_NOTE_V177.md", "E0_FISCAL_RECONSTRUCTION_V177.md"):
    (HERE / name).write_text(recovery, encoding="utf-8")
(HERE / "CNV_ATTACHMENT_ANALYTIC_REVIEW_V177.md").write_text(f"# Revisión acumulada V177\n\nPanel 34 y {COVERAGE}% congelado. La cadena BID 1192 identifica un candidato concreto con 14 cuentas persistentes y omisiones de rendición posteriores, pero el crosswalk SISIO/3672 y el daño siguen abiertos. Solicitudes 0; SAF355 0/5; ejecución 0/10.\n", encoding="utf-8")

(HERE / "README_V177.md").write_text(f"""# Checkpoint V177

- Archivo 630/630; tres PDF oficiales nuevos; hashes válidos.
- BID 1192/OC-AR trazado desde filas bancarias 2008/2009 hasta observaciones SIGEN y Cuenta 2019.
- Catorce IDs de cuenta exactos aparecen en 2008, 2009 y las referencias 2018; el cambio SAF 357→362 no rompe la identidad del programa.
- SIGEN: estados 2015 no emitidos, contabilidad desactualizada desde agosto 2014 y observaciones sin acción correctiva.
- En 2016 hubo movimientos y el saldo declarado varió 489607291.57→685073367.12; sin estados, no pudo verificarse Cuadro 13.3.
- CGN: el 29/08/2019 reunió programa, SAF 362 y UAI por observaciones sin respuesta desde 2017 y clasificación UEPEX/Fondo no resuelta.
- Cuenta 2019: no se presentó información; 16 saldos de referencia 2018 suman ARS 824861366.21.
- Préstamo finalizado, bandera no recurrente o ausencia de datos no equivalen a corrección.
- El candidato todavía no está unido fila por fila a Nota 3672/SISIO; no se prueba daño, apropiación ni beneficiario.
- Panel 34; {NUMERATOR}/{ASSETS}; {COVERAGE}%; solicitudes 0; SAF355 0/5; ejecución 0/10.
""", encoding="utf-8")
(HERE / "VEREDICTO_V177.md").write_text("# Veredicto V177\n\nAvance probatorio material. El universo abstracto de hallazgos 2008 ahora contiene un candidato nominal y bancario persistente: BID 1192/OC-AR, con 14 cuentas comunes en tres cortes y déficits de rendición documentados hasta 2019. La evidencia prueba continuidad y falta de verificación/corrección, pero aún no el enlace 0120/09→3672→fila SISIO, ni daño o apropiación. No promover al panel bancario ni atribuir causalidad hasta recuperar ese crosswalk y los extractos.\n", encoding="utf-8")
(HERE / "AUDITORIA_V177.md").write_text(f"# Auditoría V177\n\n- 630/630 fuentes; huecos 0; nuevas 3 oficiales.\n- PDF visual: 20 páginas relevantes de 5 documentos, PASS.\n- BID 1192: 16 cuentas referencia 2018; 15 presentes en 2008; 14 en 2009; 14 comunes en los tres cortes.\n- Suma ARS 824861366.21; variación 2016 reproducida ARS 195466075.55.\n- Matrices nuevas: cadena 8; cuentas 16; importes 5; recurrencia 5; límites 6; pedido crosswalk 6.\n- Panel 34, {COVERAGE}%; solicitudes 0; SAF355 0/5; ejecución 0/10.\n", encoding="utf-8")
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V177_A_V178.md").write_text("""# Handover V177 → V178

## Cerrado
- Archivo 630/630; tres PDF oficiales nuevos.
- BID 1192 trazado 2008→2019 con 14 cuentas comunes exactas.
- Observaciones sin acción correctiva y saldos no verificables preservados.
- Reunión 29/08/2019 y ausencia de información 2019 probadas.
- 16 referencias 2018 suman ARS 824.861.366,21.

## Prioridad V178
1. Buscar filas SISIO/UAI por BID 1192 y los 14 códigos exactos; unir 0120/09→3672→alta.
2. Recuperar informes UAI fuente de las compilaciones SIGEN 2017 y 2019.
3. Recuperar Notas 04854651SSFP#MP/2017 y 7813292/SSFP#MP/2017 con anexos.
4. Recuperar convocatoria/minuta/resultado de reunión DAIF 29/08/2019.
5. Obtener contrato MYPES II y decisión documentada UEPEX versus Fondo Fiduciario.
6. Obtener ledger/extractos 2008-2019 de las 16 cuentas y reconciliar Cuadros 13.2/13.3.
7. Mantener diferencias, omisiones y no verificabilidad separadas de daño o apropiación.
8. Common Crawl sólo tras control válido; borradores DRAFT_NOT_SENT; solicitudes 0.
""", encoding="utf-8")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V176.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint":"V177", "date":"2026-09-01", "master_catalog_entries":630, "physical_local_copies":630, "physical_local_hash_ok":630, "remaining_catalog_physical_or_hash_gaps":0,
    "state":"SOURCE_ARCHIVE_COMPLETE_BID1192_LONGITUDINAL_TARGET_CANDIDATE_PROVED_SISIO_CROSSWALK_OPEN", "analytical_promotion":"NONE_V177_TARGET_CANDIDATE_NOT_CAUSAL_JOIN", "exact_entities":34,
    "strict_coverage_pct":COVERAGE, "strict_asset_numerator_million_ars":NUMERATOR, "system_assets_million_ars":ASSETS, "strict_coverage_increment_v176_pp":"0",
    "requests_submitted":0, "responses_received":0, "saf355_certifications_located":0, "executed_historical_bank_rows_confirmed":0,
    "bid1192_program_continuity_2008_2019_proved":True, "bid1192_exact_account_ids_common_2008_2009_2018":14,
    "bid1192_reference_2018_account_count":16, "bid1192_reference_2018_total_ars":"824861366.21",
    "bid1192_2016_opening_reported_ars":"489607291.57", "bid1192_2016_closing_reported_ars":"685073367.12", "bid1192_2016_reported_variation_ars":"195466075.55",
    "bid1192_2016_statement_verification_possible":False, "bid1192_2019_current_information_submitted":False,
    "bid1192_note3672_sisio_crosswalk_proved":False, "bid1192_damage_or_appropriation_proved":False,
    "note_3672_target_sisio_rows_located":False, "note_3672_specific_causal_attribution_proved":False, "note_3672_specific_monetary_attribution_proved":False,
    "commoncrawl_exact_prefix_queries_v177":0, "commoncrawl_valid_no_capture_v177":0, "commoncrawl_service_errors_v177":0, "commoncrawl_capture_rows_v177":0,
    "commoncrawl_pending_retry_queries":40, "commoncrawl_pending_retry_collections":20, "new_v177_sources":3, "public_web_queries_v177":6,
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V177.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

origins = read_csv(ORIGINS)
by_path = {row["path"]:row for row in origins}
for path in iter_files(HIST_ROOT):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"downloaded/preserved V177","note":"official SIGEN/CGN PDF; visually verified"}
for path in iter_files(SYNC):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V177","note":"incremental three-source synchronization"}
for path in HERE.iterdir():
    if path.is_file():
        by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V177","note":"BID1192 longitudinal checkpoint"}
for path in (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V177.csv", AUDIT / "SOURCE_BACKUP_CENSUS_V177.csv", AUDIT / "SOURCE_PRESERVATION_MISSING_V177.csv", AUDIT / "CURRENT_SOURCE_COMPLETENESS_V177.json"):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V177","note":"630-source completeness"}
write_csv(ORIGINS, list(by_path.values()), ["path", "origin", "note"])

transparency = CYCLE / "TRANSPARENCY_README.md"
body = transparency.read_text(encoding="utf-8-sig")
if "## V177 · candidato longitudinal BID 1192" not in body:
    body += "\n\n## V177 · candidato longitudinal BID 1192\n\nTres PDF oficiales nuevos permiten trazar el BID 1192 desde hallazgos 2008/2009 hasta observaciones sin acción correctiva y ausencia de información 2019. Hay 14 cuentas comunes y ARS 824.861.366,21 en 16 referencias 2018. Es continuidad de objeto y déficit de rendición, no crosswalk SISIO/3672 ni daño. Archivo 630/630; panel 34; solicitudes 0.\n"
    transparency.write_text(body, encoding="utf-8")
(REPO / "BACKUP_ACTUALIZACION_2026-09-01.md").write_text(f"# Backup de actualización · 2026-09-01\n\n- V177; 630/630 fuentes.\n- BID 1192 trazado 2008→2019; 14 cuentas comunes; 16 referencias 2018 por ARS 824861366.21.\n- Observaciones sin acción correctiva y ausencia de información 2019 probadas.\n- Crosswalk SISIO/3672, extractos y daño abiertos.\n- Panel 34, {COVERAGE}%; solicitudes 0; SAF355 0/5; ejecución 0/10.\n", encoding="utf-8")

(HERE / "qa_v177.py").write_text("""from pathlib import Path
import csv,hashlib,json
from decimal import Decimal
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==630
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V177.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==630 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V177.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V177' and co['master_catalog_entries']==630
assert co['bid1192_program_continuity_2008_2019_proved'] and co['bid1192_exact_account_ids_common_2008_2009_2018']==14
assert co['bid1192_reference_2018_account_count']==16 and Decimal(co['bid1192_reference_2018_total_ars'])==Decimal('824861366.21')
assert not co['bid1192_2016_statement_verification_possible'] and not co['bid1192_2019_current_information_submitted']
assert not co['bid1192_note3672_sisio_crosswalk_proved'] and not co['bid1192_damage_or_appropriation_proved'] and not co['note_3672_target_sisio_rows_located']
assert co['requests_submitted']==co['saf355_certifications_located']==co['executed_historical_bank_rows_confirmed']==0 and co['commoncrawl_pending_retry_queries']==40
chain=rows('E0_BID1192_LONGITUDINAL_EVIDENCE_CHAIN_V177.csv'); assert len(chain)==8
ac=rows('E0_BID1192_ACCOUNT_ID_CONTINUITY_V177.csv'); assert len(ac)==16 and sum(x['present_2008']=='YES' for x in ac)==15 and sum(x['present_2009']=='YES' for x in ac)==14 and sum(x['present_2008']==x['present_2009']=='YES' for x in ac)==14
assert sum(Decimal(x['reference_2018_ars']) for x in ac)==Decimal('824861366.21')
qb=rows('E0_BID1192_QUANTIFIED_UNVERIFIED_BALANCES_V177.csv'); assert len(qb)==5 and Decimal(qb[2]['amount_ars'])==Decimal(qb[1]['amount_ars'])-Decimal(qb[0]['amount_ars'])
assert len(rows('E0_BID1192_RECURRENT_FLAG_TRAJECTORY_V177.csv'))==5
assert len(rows('E0_BID1192_RESPONSIBILITY_AND_EVIDENCE_LIMITS_V177.csv'))==6
assert len(rows('E0_NOTE_3672_BID1192_TARGET_CROSSWALK_REQUEST_V177.csv'))==6
assert len(rows('V177_PDF_VISUAL_CONTROL.csv'))==5 and all(x['result'].startswith('PASS') for x in rows('V177_PDF_VISUAL_CONTROL.csv'))
keys=rows('E0_REQUEST_SEARCH_KEY_MATRIX_V177.csv'); assert {'SK177_45','SK177_46','SK177_47','SK177_48','SK177_49'}<={x['key_id'] for x in keys}
obj=rows('E0_V177_REQUEST_OBJECTS.csv'); assert {'RO177_44','RO177_45','RO177_46','RO177_47'}<={x['row_id'] for x in obj} and all(x['status']=='DRAFT_NOT_SENT' for x in obj) and obj==rows('E0_V177_REQUEST_OBJECTS_V177.csv')
for n in ('REQUEST_AGN_2018_REPLY_V177.md','REQUEST_BCRA_CRYL_SETTLEMENT_V177.md','REQUEST_BNA_FIRST_STAGE_BLOTTER_V177.md','REQUEST_CAJA_SETTLEMENT_HOLDINGS_V177.md','REQUEST_CNV_CUSTODY_RECORDS_V177.md','REQUEST_ECONOMIA_TESORO_SETTLEMENT_V177.md'):
 s=(H/n).read_text(encoding='utf-8-sig'); assert 'DRAFT_NOT_SENT' in s or 'BORRADOR_NO_ENVIADO' in s
panel=rows('FOUR_LEG_PASS_PANEL_V177.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
assert len(rows('V177_SOURCE_BUNDLE.csv'))==5
m=json.loads((H/'MANIFEST_V177.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V177' and m['parent_checkpoint']=='V176' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V177 QA PASS · 630/630 · new=3 · BID1192-chain=PROVED · SISIO-crosswalk=OPEN · panel=34 · requests=0')
""", encoding="utf-8")

(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")
manifest_files = [{"path":p.name,"bytes":p.stat().st_size,"sha256":sha(p)} for p in sorted(HERE.iterdir(), key=lambda x:x.name.casefold()) if p.is_file() and p.name != "MANIFEST_V177.json"]
manifest = {
    "checkpoint":"V177", "parent_checkpoint":"V176", "created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "exact_entities":34, "strict_coverage_pct":COVERAGE, "strict_asset_numerator_million_ars":NUMERATOR, "system_assets_million_ars":ASSETS,
    "new_promotions":[], "source_archive":"630/630; three official SIGEN/CGN PDFs added",
    "historical_finding":"BID 1192 longitudinal target candidate and 14 exact common accounts proved; SISIO/3672 crosswalk and damage open",
    "bid1192_reference_2018_total_ars":"824861366.21", "bid1192_common_accounts":14,
    "note_3672_target_sisio_rows":"NOT_LOCATED", "commoncrawl_queries_v177":0, "commoncrawl_pending":40,
    "closed_network_gate":"NO", "saf355_certifications":"0/5", "executed_historical_bank_rows":"0/10", "requests_submitted":0,
    "files":manifest_files,
}
(HERE / "MANIFEST_V177.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path":p.relative_to(REPO).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)} for p in iter_files(REPO) if p != global_manifest]
payload = {"checkpoint":"V177","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),"strict_coverage_pct":COVERAGE,"exact_entities":34,"closed_network_gate":"NO","source_audit":"630 master; 630 physical SHA-valid","historical_workstream":"BID1192 candidate chain proved; SISIO crosswalk/damage open; CC pending 40; drafts not sent","file_count_excluding_manifest":len(global_files),"files":global_files}
tmp = global_manifest.with_suffix(".json.V177tmp")
tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
tmp.replace(global_manifest)
print("V177 BUILD PASS · catalog=630/630 · new=3 · BID1192-chain=PROVED · SISIO-crosswalk=OPEN · panel=34 · requests=0")
