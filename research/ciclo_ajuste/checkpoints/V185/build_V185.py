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
PARENT = CYCLE / "checkpoints" / "V184"
AUDIT = CYCLE / "source_audit"
SYNC = CYCLE / "inputs" / "source_sync" / "v185"
HIST = CYCLE / "inputs" / "historical_retrieval" / "v185"
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
        "MANIFEST_V184.json", "README_V184.md", "VEREDICTO_V184.md", "AUDITORIA_V184.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V184_A_V185.md", "V184_SOURCE_BUNDLE.csv",
        "V184_PUBLIC_SEARCH_LOG.csv", "V184_PDF_VISUAL_CONTROL.csv", "V184_PDF_TEXT_CONTROL.csv",
        "V184_XLSX_CONTENT_CONTROL.csv", "V184_HTML_CONTENT_CONTROL.csv", "CORRECTION_LOG_V184.md",
    }
    HERE.mkdir(parents=True, exist_ok=True)
    for source in sorted(PARENT.iterdir(), key=lambda path: path.name.casefold()):
        if not source.is_file() or source.name in skip or source.name.startswith(("build_", "qa_")):
            continue
        target = HERE / source.name.replace("V184", "V185")
        target.write_bytes(source.read_bytes())


SOURCE_SPECS = [
    {
        "id": "e0_uai_saf362_change_admin_2023_fondyf_account_54395_v185",
        "institution": "Unidad de Auditoría Interna · Secretaría de Industria y Desarrollo Productivo",
        "title": "Informe UAI 22/2023 · cierre por cambio de administración · SAF 362",
        "url": "https://www.argentina.gob.ar/sites/default/files/inf._22_2023_cierre_por_cambio_de_administracion_-_saf_362.pdf",
        "file": "uai_saf362_informe_22_2023_cierre_cambio_administracion.pdf",
        "published": "2023-12-07", "period": "2023-10-31",
        "type": "PDF oficial preservado · control textual y visual",
        "note": "Programa 67 Actividad 4 FONDYF: crédito vigente ARS 3.094.874, devengado y pagado cero. Cuenta BNA 54395/36 SEPYMEYDR-FOND Y F Rec. FF13: certificación BNA cero, saldo bancario e-SIDIF cero y saldo escritural e-SIDIF -ARS 36.600.000. El informe registra partidas pendientes de conciliación y observaciones anteriores vigentes. No prueba que el saldo escritural sea faltante de caja, deuda bancaria, daño, ganancia privada ni que corresponda a MY4002/BID1192.",
    },
    {
        "id": "e0_uai_saf362_closure_2021_report_3_2022_v185",
        "institution": "Unidad de Auditoría Interna · Ministerio de Desarrollo Productivo",
        "title": "Informe UAI 3/2022 · cierre del ejercicio 2021 · SAF 362",
        "url": "https://www.argentina.gob.ar/sites/default/files/informe_de_auditoria_2022-03_-_mdp.pdf",
        "file": "uai_informe_3_2022_cierre_ejercicio_2021_saf362.pdf",
        "published": "2022", "period": "2021",
        "type": "PDF oficial preservado · control textual y visual",
        "note": "Informa partidas pendientes de conciliación en cuentas corrientes con antigüedad superior a un año y debilidad del registro de convenios. La pieza contiene una inconsistencia interna de fechas entre título/firma y período de trabajo de campo; se usa sólo para la observación publicada, no para una cronología fina.",
    },
    {
        "id": "e0_uai_saf362_account_2021_report_9_2022_v185",
        "institution": "Unidad de Auditoría Interna · Ministerio de Desarrollo Productivo",
        "title": "Informe UAI 9/2022 · Cuenta de Inversión 2021 · SAF 362",
        "url": "https://www.argentina.gob.ar/sites/default/files/informe_de_auditoria_2022-09_-_mdp.pdf",
        "file": "uai_informe_9_2022_cuenta_inversion_2021_saf362.pdf",
        "published": "2022", "period": "2021",
        "type": "PDF oficial preservado · control textual y visual",
        "note": "Registra partidas pendientes de conciliación en las cuentas informadas en el Cuadro 1. El resumen público no individualiza la cuenta 54395/36 ni permite atribuirle continuidad.",
    },
    {
        "id": "e0_uai_saf362_closure_2022_report_2_2023_v185",
        "institution": "Unidad de Auditoría Interna · Secretaría de Industria y Desarrollo Productivo",
        "title": "Informe UAI 2/2023 · cierre del ejercicio 2022 · SAF 362",
        "url": "https://www.argentina.gob.ar/sites/default/files/informe_uai_n_2-2023_-_cierre_de_ejercicio_siydp_raip_1.pdf",
        "file": "uai_informe_2_2023_cierre_ejercicio_2022_saf362.pdf",
        "published": "2023", "period": "2022",
        "type": "PDF oficial preservado · control textual y visual",
        "note": "Registra saldos inconsistentes, partidas sin conciliar con antigüedad superior a un año, anticipos pendientes y falta de centralización completa de convenios. Es evidencia de una debilidad general de cierre, no de una cuenta o daño específicos.",
    },
    {
        "id": "e0_uai_saf362_account_2022_report_3_2023_v185",
        "institution": "Unidad de Auditoría Interna · Secretaría de Industria y Desarrollo Productivo",
        "title": "Informe UAI 3/2023 · Cuenta de Inversión 2022 · SAF 362",
        "url": "https://www.argentina.gob.ar/sites/default/files/inf_3-2023_-_cuenta_de_inversion_siydp_-_raip_1.pdf",
        "file": "uai_informe_3_2023_cuenta_inversion_2022_saf362.pdf",
        "published": "2023", "period": "2022",
        "type": "PDF oficial preservado · control textual y visual",
        "note": "Señala partidas pendientes de conciliación en cuentas bancarias del Cuadro 1. La observación sobre BID 2923 es ajena a BID1192 y se conserva como control negativo de identidad.",
    },
    {
        "id": "e0_uai_fondep_2020_2022_report_17_2023_v185",
        "institution": "Unidad de Auditoría Interna · Secretaría de Industria y Desarrollo Productivo",
        "title": "Informe UAI 17/2023 · Fondo Nacional de Desarrollo Productivo (FONDEP)",
        "url": "https://www.argentina.gob.ar/sites/default/files/inf_nro_17-2023_-_fondep_-_raip.pdf",
        "file": "uai_informe_17_2023_fondep.pdf",
        "published": "2023", "period": "2020-2022",
        "type": "PDF oficial preservado · control textual y visual",
        "note": "Documenta inconsistencias en pases entre cuentas informadas por BICE Fideicomisos, controles débiles sobre fondos/inversiones, transferencias sin justificación clara e inconsistencias en rendiciones. Es un comparador de control del fondo sucesor; no prueba transferencia desde FONDYF ni vinculación con MY4002/BID1192.",
    },
    {
        "id": "e0_uai_saf362_closure_2023_report_1_2024_v185",
        "institution": "Unidad de Auditoría Interna · Secretaría de Industria y Desarrollo Productivo",
        "title": "Informe UAI 1/2024 · cierre del ejercicio 2023 · SAF 362",
        "url": "https://www.argentina.gob.ar/sites/default/files/informe_asidp_1_2023-_cierre_de_ejercicio_2023_-_saf_362_raip.pdf",
        "file": "uai_informe_1_2024_cierre_ejercicio_2023_saf362.pdf",
        "published": "2024", "period": "2023",
        "type": "PDF oficial preservado · control textual y visual",
        "note": "Informa partidas pendientes de conciliación en distintas cuentas del SAF, todas de ejercicios anteriores, y remite el detalle a fs. 16 no incluido en el resumen público. No permite afirmar que la cuenta 54395/36 continuara incluida.",
    },
    {
        "id": "e0_uai_saf362_account_2023_report_4_2024_v185",
        "institution": "Unidad de Auditoría Interna · Secretaría de Industria y Desarrollo Productivo",
        "title": "Informe UAI 4/2024 · Cuenta de Inversión 2023 · SAF 362",
        "url": "https://www.argentina.gob.ar/sites/default/files/informe_de_auditoria_n_4_cuenta_de_inversion_-_saf_362_aip.pdf",
        "file": "uai_informe_4_2024_cuenta_inversion_2023_saf362.pdf",
        "published": "2024", "period": "2023",
        "type": "PDF oficial preservado · control textual y visual",
        "note": "Registra partidas pendientes de conciliación y un saldo de cuenta incorrectamente expuesto; además informa falta de estados contables 2023 de FONDEP. El resumen no identifica 54395/36.",
    },
    {
        "id": "e0_uai_saf362_closure_2024_report_2_2025_v185",
        "institution": "Unidad de Auditoría Interna · Secretaría de Industria y Desarrollo Productivo",
        "title": "Informe UAI 2/2025 · cierre del ejercicio 2024 · SAF 362",
        "url": "https://www.argentina.gob.ar/sites/default/files/inf_2-2025_-_cierre_de_ejercicio_2024_362_-_raip.pdf",
        "file": "uai_informe_2_2025_cierre_ejercicio_2024_saf362.pdf",
        "published": "2025", "period": "2024",
        "type": "PDF oficial preservado · control textual y visual",
        "note": "Vuelve a registrar partidas no conciliadas en distintas cuentas del SAF, todas de ejercicios anteriores. No identifica las cuentas ni demuestra la persistencia de 54395/36.",
    },
    {
        "id": "e0_uai_saf362_account_2024_report_2025_v185",
        "institution": "Unidad de Auditoría Interna · Secretaría de Industria y Desarrollo Productivo",
        "title": "Informe UAI 2025 · Cuenta de Inversión 2024 · SAF 362",
        "url": "https://www.argentina.gob.ar/sites/default/files/cuenta_de_inversion_-_saf_362.pdf",
        "file": "uai_cuenta_inversion_2024_saf362_2025.pdf",
        "published": "2025", "period": "2024",
        "type": "PDF oficial preservado · control textual y visual",
        "note": "Registra partidas pendientes de conciliación en el Cuadro 1 y diferencias en otros rubros. El resumen no individualiza la cuenta 54395/36.",
    },
]


clone_parent()
SYNC.mkdir(parents=True, exist_ok=True)
for spec in SOURCE_SPECS:
    assert (HIST / spec["file"]).is_file(), spec["file"]

catalog = read_csv(CATALOG)
catalog_fields = list(catalog[0])
by_id = {row["id"]: row for row in catalog}
new_sources = []
for spec in SOURCE_SPECS:
    path = HIST / spec["file"]
    row = {
        "id": spec["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": spec["institution"],
        "titulo": spec["title"], "url_original": spec["url"],
        "archivo_local": "/" + path.relative_to(REPO).as_posix(), "fecha_descarga": "2026-09-01",
        "fecha_publicacion": spec["published"], "codigo_serie": spec["title"],
        "periodo_utilizado": spec["period"], "tipo": spec["type"], "sha256": sha(path),
        "nota": spec["note"],
    }
    by_id[row["id"]] = row
    new_sources.append(row)
catalog = list(by_id.values())
write_csv(CATALOG, catalog, catalog_fields)
assert len(catalog) == len({row["id"] for row in catalog}) == 718

audit = []
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    actual = sha(path) if path.is_file() else ""
    audit.append({
        "id": row["id"], "archivo_local": row["archivo_local"], "exists": str(path.is_file()),
        "sha_catalog": row["sha256"].lower(), "sha_actual": actual,
        "hash_ok": str(path.is_file() and bool(row["sha256"]) and actual == row["sha256"].lower()),
    })
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V185.csv", audit)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V185.csv", audit)
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V185.csv", [row for row in audit if row["hash_ok"] != "True"], list(audit[0]))
assert all(row["hash_ok"] == "True" for row in audit)

write_csv(HERE / "E0_FONDYF_54395_36_ACCOUNT_GAP_V185.csv", [
    {"field":"account","value":"54395/36","source_state":"PUBLISHED","interpretation":"BNA account within non-Fondo Rotatorio accounts","limit":"not crosswalked to MY4002"},
    {"field":"name","value":"SEPYMEYDR - FOND Y F Rec. FF13","source_state":"PUBLISHED","interpretation":"FONDYF recovery account funded with FF13","limit":"does not identify each recovery or loan"},
    {"field":"BNA_certification","value":"0","source_state":"PUBLISHED","interpretation":"bank-certified balance at cutoff","limit":"certificate/extract itself not included in public report"},
    {"field":"eSIDIF_bank_balance","value":"0","source_state":"PUBLISHED","interpretation":"bank-side balance in e-SIDIF","limit":"does not resolve ledger-side discrepancy"},
    {"field":"eSIDIF_ledger_balance","value":"-36600000","source_state":"PUBLISHED","interpretation":"negative escritural balance requiring ledger/accounting explanation","limit":"not cash missing, bank debt, damage or private gain by itself"},
    {"field":"difference","value":"-36600000","source_state":"DERIVED_FROM_PUBLISHED_FIELDS","interpretation":"ledger minus bank/certificate","limit":"sign and economic nature depend on account design and entries"},
    {"field":"opening_entry_and_movements","value":"NOT_PUBLIC","source_state":"OPEN","interpretation":"essential to identify origin and age","limit":"cannot assign BID1192/MY4002 provenance"},
    {"field":"reconciliation_and_adjustment","value":"NOT_PUBLIC","source_state":"OPEN","interpretation":"essential to determine whether corrected, reclassified or outstanding","limit":"later summaries do not identify this account"},
])

write_csv(HERE / "E0_FONDYF_BUDGET_OPERATIONAL_STATUS_2023_V185.csv", [
    {"program":"67","activity":"4","name":"FONDYF","credit_ars":"3094874","accrued_ars":"0","paid_ars":"0","execution_pct":"0","classification":"RESIDUAL_BUDGET_ACTIVITY_PRESENT_ZERO_EXECUTION","limit":"budget presence is not proof of new lending or positive bank balance"},
    {"program":"67","activity":"10","name":"FONDEP","credit_ars":"40848479101","accrued_ars":"19731916396","paid_ars":"0","execution_pct":"48.31","classification":"ACTIVE_BUDGET_EXECUTION_COMPARATOR","limit":"does not prove FONDYF assets were transferred to FONDEP"},
])

write_csv(HERE / "E0_SAF362_RECONCILIATION_TIMELINE_2021_2024_V185.csv", [
    {"exercise":"2021","report":"UAI 3/2022 cierre","finding":"current-account items pending reconciliation older than one year","account_named":"NO","continuity_for_54395_36":"NOT_TESTABLE","caveat":"source-internal fieldwork date inconsistency"},
    {"exercise":"2021","report":"UAI 9/2022 Cuenta de Inversión","finding":"Cuadro 1 accounts with pending reconciliation items","account_named":"NO","continuity_for_54395_36":"NOT_TESTABLE","caveat":"executive summary only"},
    {"exercise":"2022","report":"UAI 2/2023 cierre","finding":"balances inconsistent and items older than one year pending reconciliation","account_named":"NO","continuity_for_54395_36":"NOT_TESTABLE","caveat":"general SAF observation"},
    {"exercise":"2022","report":"UAI 3/2023 Cuenta de Inversión","finding":"Cuadro 1 bank accounts with pending reconciliation items","account_named":"NO","continuity_for_54395_36":"NOT_TESTABLE","caveat":"BID2923 issue is not BID1192"},
    {"exercise":"2023-10-31","report":"UAI 22/2023 change of administration","finding":"54395/36: BNA 0; e-SIDIF bank 0; e-SIDIF ledger -36.6m","account_named":"YES","continuity_for_54395_36":"EXACT_AT_CUTOFF","caveat":"origin and reconciliation not public"},
    {"exercise":"2023","report":"UAI 1/2024 cierre","finding":"unreconciled items in several accounts, all from prior exercises; detail at fs. 16","account_named":"NO","continuity_for_54395_36":"NOT_TESTABLE","caveat":"fs. 16 not in public summary"},
    {"exercise":"2023","report":"UAI 4/2024 Cuenta de Inversión","finding":"Cuadro 1 items pending reconciliation and one balance misstated","account_named":"NO","continuity_for_54395_36":"NOT_TESTABLE","caveat":"executive summary only"},
    {"exercise":"2024","report":"UAI 2/2025 cierre","finding":"unreconciled items in several accounts, all from prior exercises","account_named":"NO","continuity_for_54395_36":"NOT_TESTABLE","caveat":"executive summary only"},
    {"exercise":"2024","report":"UAI 2025 Cuenta de Inversión","finding":"Cuadro 1 accounts with pending reconciliation items","account_named":"NO","continuity_for_54395_36":"NOT_TESTABLE","caveat":"executive summary only"},
])

write_csv(HERE / "E0_FONDYF_MY4002_ACCOUNT_SEPARATION_V185.csv", [
    {"proposition":"MY4002 was reported active and managed by FONDYF at 2020 cutoff","status":"SUPPORTED_AS_ADMINISTRATIVE_NARRATIVE","source":"Cuenta 2020 Anexo 4.37","missing":"2020 ledger, balance and full note"},
    {"proposition":"BNA 54395/36 is named as FONDYF recoveries FF13 at 2023-10-31","status":"SUPPORTED","source":"UAI 22/2023","missing":"bank certificate, extracts and ledger"},
    {"proposition":"MY4002 and 54395/36 are the same or directly linked accounts","status":"NOT_PROVED","source":"no public crosswalk","missing":"transfer agreement, account map and mirror entries"},
    {"proposition":"the -36.6m is composed of BID1192 recoveries","status":"NOT_PROVED","source":"generic recovery-account denomination only","missing":"transaction-level origin and loan identifiers"},
    {"proposition":"the -36.6m is missing cash, bank debt, loss or private gain","status":"NOT_PROVED_AND_ACCOUNTING_SIGN_AMBIGUOUS","source":"bank and certificate both zero; ledger negative","missing":"account nature, entries, reconciliation and adjustment"},
    {"proposition":"later generic findings prove 54395/36 remained unreconciled through 2024","status":"NOT_PROVED","source":"later executive summaries omit account IDs","missing":"full Cuadro 1, Annex A and analytical workpapers"},
])

write_csv(HERE / "E0_FONDYF_SUCCESSOR_CONTROL_CONTEXT_V185.csv", [
    {"entity":"FONDYF","period":"2023-10-31","fact":"budget activity present with zero execution; recovery account 54395/36 disclosed","evidentiary_use":"residual administrative/accounting status","non_inference":"not current lending operation or transfer to successor"},
    {"entity":"FONDEP","period":"2020-2022","fact":"UAI reports inconsistent inter-account passes, weak fund/investment controls and insufficiently justified transfers","evidentiary_use":"successor-fund control-risk comparator","non_inference":"not proof that FONDYF/MY4002 resources entered FONDEP"},
    {"entity":"FONDEP","period":"2023","fact":"UAI reports closing financial statements not presented","evidentiary_use":"follow-up transparency gap","non_inference":"not proof of asset diversion or BID1192 link"},
])

write_csv(HERE / "E0_REQUEST_OBJECTS_DELTA_V185.csv", [
    {"row_id":"RO185_87","object_id":"FONDYF_BNA_54395_36_ESIDIF_LEDGER_AND_RECONCILIATION","custodian":"SAF 362 · BNA · CGN · TGN","period":"account opening-2025","exact_record":"full ledger, bank statements/certificates, reconciliations and adjustment entries for BNA 54395/36","closure_rule":"explain every component of -ARS 36.6m and reconcile bank/certificate/e-SIDIF without attribution by inference"},
    {"row_id":"RO185_88","object_id":"SAF362_FULL_CUADRO1_AND_ANNEX_A_2021_2024","custodian":"SAF 362 · UAI · CGN","period":"2021-2024","exact_record":"complete Cuadro 1, Annex A and e-SIDIF Saldo Disponible query for every bank and escritural account","closure_rule":"identify which accounts and amounts persisted or were corrected each year"},
    {"row_id":"RO185_89","object_id":"UAI_ANALYTICAL_WORKPAPERS_FS16_CLOSURE_2023","custodian":"UAI Secretaría de Industria y Desarrollo Productivo","period":"2023","exact_record":"full report/workpaper page fs. 16 and support for prior-year unreconciled items","closure_rule":"test whether 54395/36 appears in the 2023 closing detail"},
    {"row_id":"RO185_90","object_id":"FONDYF_ACTIVITY4_BUDGET_CREDIT_COMPOSITION_2023","custodian":"ONP · SAF 362","period":"2023","exact_record":"composition and purpose of ARS 3,094,874 current credit for Program 67 Activity 4 FONDYF","closure_rule":"classify residual administrative costs versus operational lending or settlement"},
    {"row_id":"RO185_91","object_id":"FONDYF_TO_FONDEP_TRANSFER_NEGATIVE_TEST","custodian":"Secretaría PyME · SAF 362 · BICE Fideicomisos · BNA · BCRA","period":"2016-2024","exact_record":"all asset/rights/account transfer instruments between FONDYF and FONDEP, plus express certification if none exist","closure_rule":"prove or disprove transfer with executed instrument and mirror accounting/bank entries"},
    {"row_id":"RO185_92","object_id":"FONDEP_BICE_RENDITIONS_AND_INTERACCOUNT_PASSES_2020_2022","custodian":"BICE Fideicomisos · FONDEP · UAI","period":"2020-2022","exact_record":"renditions, bank-account passes, authorizations, investment records and UAI support referenced in Report 17/2023","closure_rule":"quantify control observations and test any explicit FONDYF/BID1192 origin separately"},
])

requests = read_csv(HERE / "E0_V185_REQUEST_OBJECTS.csv")
existing_request_ids = {row["row_id"] for row in requests}
for row in read_csv(HERE / "E0_REQUEST_OBJECTS_DELTA_V185.csv"):
    if row["row_id"] not in existing_request_ids:
        requests.append({
            **row,
            "minimum_fields":"date; account; CBU; currency; amount; entry; documentary support; authorizer; counterparty; status",
            "status":"DRAFT_NOT_SENT",
        })
write_csv(HERE / "E0_V185_REQUEST_OBJECTS.csv", requests)
write_csv(HERE / "E0_V185_REQUEST_OBJECTS_V185.csv", requests)

write_csv(HERE / "V185_PUBLIC_SEARCH_LOG.csv", [
    {"query_id":"PS185_01","query":"exact NO-2021-16359825 and IF-2021-57375822","result":"no standalone signed note/package located; only official CGN/HCDN reproduction","limit":"full note and attachments remain open"},
    {"query_id":"PS185_02","query":"54395/36 FONDYF 36.600.000 exact variants","result":"only UAI 22/2023 official report located","limit":"no public ledger, extract or reconciliation"},
    {"query_id":"PS185_03","query":"FONDYF transfer agreement FONDEP BNA BCRA BID1192","result":"no executed transfer instrument located","limit":"connection remains a hypothesis to test negatively"},
    {"query_id":"PS185_04","query":"SAF 362 cierre Cuenta de Inversión 2021 2022 2023 2024 UAI","result":"official UAI series preserved; generic reconciliation issue repeats","limit":"later executive summaries omit account IDs"},
    {"query_id":"PS185_05","query":"Resolución 1406 SSFP MYPES II Macro Credicoop exact variants","result":"no exact act/body or account crosswalk located","limit":"no new Res1406 promotion"},
])

bundle = []
for row in new_sources:
    path = REPO / row["archivo_local"].lstrip("/")
    bundle.append({"source_id":row["id"],"file":path.name,"bytes":path.stat().st_size,"sha256":sha(path),"status":"CATALOGUED_SHA_VALID"})
write_csv(HERE / "V185_SOURCE_BUNDLE.csv", bundle)
write_csv(HERE / "V185_PDF_VISUAL_CONTROL.csv", [
    {"file":"uai_saf362_informe_22_2023_cierre_cambio_administracion.pdf","pages":"6;11;20;21","result":"PASS_BUDGET_ACCOUNT_AND_SUCCESSOR_CONTEXT"},
    {"file":"uai_informe_3_2022_cierre_ejercicio_2021_saf362.pdf","pages":"2","result":"PASS_RECONCILIATION_FINDING_DATE_CAVEAT"},
    {"file":"uai_informe_9_2022_cuenta_inversion_2021_saf362.pdf","pages":"4","result":"PASS_CUADRO1_RECONCILIATION"},
    {"file":"uai_informe_2_2023_cierre_ejercicio_2022_saf362.pdf","pages":"2","result":"PASS_OLD_UNRECONCILED_ITEMS"},
    {"file":"uai_informe_3_2023_cuenta_inversion_2022_saf362.pdf","pages":"2","result":"PASS_CUADRO1_AND_BID2923_NEGATIVE_CONTROL"},
    {"file":"uai_informe_17_2023_fondep.pdf","pages":"2","result":"PASS_FONDEP_CONTROL_COMPARATOR"},
    {"file":"uai_informe_1_2024_cierre_ejercicio_2023_saf362.pdf","pages":"2","result":"PASS_PRIOR_YEAR_ITEMS_FS16_GAP"},
    {"file":"uai_informe_4_2024_cuenta_inversion_2023_saf362.pdf","pages":"2-3","result":"PASS_CUADRO1_AND_FONDEP_STATEMENTS_GAP"},
    {"file":"uai_informe_2_2025_cierre_ejercicio_2024_saf362.pdf","pages":"2-3","result":"PASS_PRIOR_YEAR_ITEMS_GENERIC"},
    {"file":"uai_cuenta_inversion_2024_saf362_2025.pdf","pages":"2-3","result":"PASS_CUADRO1_RECONCILIATION_GENERIC"},
])

archival = read_csv(HERE / "ARCHIVAL_PROVENANCE_V185.csv")
existing_archival_ids = {row["source_id"] for row in archival}
for row in new_sources:
    if row["id"] in existing_archival_ids:
        continue
    path = REPO / row["archivo_local"].lstrip("/")
    archival.append({"source_id":row["id"],"original_url":row["url_original"],"retrieval_url":row["url_original"],"capture_timestamp":"2026-09-01","cdx_digest":"N/A_OFFICIAL_DIRECT_DOWNLOAD","local_path":row["archivo_local"],"sha256":row["sha256"],"bytes":path.stat().st_size,"provenance_note":row["nota"]})
write_csv(HERE / "ARCHIVAL_PROVENANCE_V185.csv", archival)

census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V185.csv")
existing_census_ids = {row["source_id"] for row in census}
for row in new_sources:
    if row["id"] in existing_census_ids:
        continue
    path = REPO / row["archivo_local"].lstrip("/")
    census.append({"source_id":row["id"],"institution":row["institucion"],"artifact":row["titulo"],"url":row["url_original"],"local_path":row["archivo_local"],"sha256":row["sha256"],"bytes":path.stat().st_size,"period_coverage":row["periodo_utilizado"],"variable_families":"FONDYF;SAF362;54395/36;bank reconciliation;budget status;FONDEP comparator","primary_source":"YES","preserved":"YES","method_breaks":"generic reconciliation finding versus account-specific 2023 disclosure","use_status":"USABLE_WITH_EXPLICIT_LIMIT","caveat":row["nota"]})
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V185.csv", census)

append_once(HERE / "SOURCE_REFERENCES_V185.md", "## V185 · FONDYF 54395/36 y conciliaciones SAF 362", """
## V185 · FONDYF 54395/36 y conciliaciones SAF 362

- El Informe UAI 22/2023 individualiza la cuenta BNA 54395/36 `SEPYMEYDR - FOND Y F Rec. FF13`: certificación BNA cero, saldo bancario e-SIDIF cero y saldo escritural e-SIDIF negativo por ARS 36,6 millones al 31/10/2023.
- En ese corte, Programa 67 Actividad 4 FONDYF tenía crédito vigente ARS 3.094.874 y ejecución devengada/pagada cero. Se clasifica como presencia presupuestaria residual con ejecución nula, no como operatoria crediticia activa.
- Los informes UAI de cierre y Cuenta de Inversión documentan partidas pendientes de conciliación desde 2021 hasta 2024. Sólo el informe 22/2023 nombra 54395/36; la continuidad individual posterior queda abierta.
- El saldo escritural negativo no equivale por sí solo a faltante de caja, deuda bancaria, daño o ganancia privada: se necesitan el mayor, naturaleza de la cuenta, asiento de origen, conciliaciones y ajustes.
- El informe FONDEP 17/2023 es un comparador de debilidades de control del fondo sucesor. No prueba transferencia FONDYF→FONDEP ni conexión MY4002/BID1192.
""")
append_once(HERE / "RETRIEVAL_LOG_V185.md", "## V185 · búsqueda 2026-09-01", """
## V185 · búsqueda 2026-09-01

- Diez informes oficiales UAI 2022-2025 preservados y controlados visualmente.
- Localizada una divulgación contable exacta para FONDYF/BNA 54395/36 al 31/10/2023; no se localizaron el mayor, extractos, conciliación ni asiento de origen.
- No se localizaron el cuerpo firmado de NO-2021-16359825, convenios ejecutados FONDYF→fondo sucesor, ni una conexión pública 54395/36↔MY4002↔BID1192.
- Se crean seis objetos probatorios adicionales, todos DRAFT_NOT_SENT. Solicitudes enviadas: 0.
""")

(HERE / "README_V185.md").write_text("""# Checkpoint V185

V185 abre una nueva veta contable de FONDYF sin sobreinterpretarla. El Informe UAI 22/2023 del SAF 362 individualiza la cuenta BNA `54395/36`, denominada `SEPYMEYDR - FOND Y F Rec. FF13`: tanto la certificación del BNA como el saldo bancario e-SIDIF son cero, mientras el saldo escritural e-SIDIF es negativo por ARS 36.600.000 al 31 de octubre de 2023.

En el mismo corte, Programa 67 Actividad 4 FONDYF conserva crédito vigente por ARS 3.094.874 pero no registra devengado ni pagado. Se clasifica como presencia presupuestaria residual de ejecución cero; no como prueba de préstamos nuevos, fondos líquidos ni deuda.

La serie UAI 2021-2024 documenta de forma repetida partidas bancarias pendientes de conciliación y, en algunos cierres, antigüedad de ejercicios anteriores. Sin embargo, sólo UAI 22/2023 identifica públicamente 54395/36. Los resúmenes posteriores no permiten afirmar que esa cuenta siguiera integrando el universo observado.

## Estado probatorio

- **Sí probado:** identidad y tres saldos publicados de 54395/36 al corte; actividad presupuestaria FONDYF con ejecución cero; recurrencia general de problemas de conciliación del SAF 362.
- **No probado:** equivalencia 54395/36=MY4002; composición BID1192 de los ARS 36,6 millones; transferencia a FONDEP; faltante de caja, deuda bancaria, daño, apropiación o ganancia privada.
- **Próximo cierre material:** mayor e-SIDIF, extractos/certificación BNA, conciliaciones y ajustes de 54395/36; Cuadro 1/Anexo A completos; fs. 16 del cierre 2023; convenios y asientos espejo.

Fuentes archivadas: **718/718 físicas y SHA-256 válidas**. Diez fuentes oficiales nuevas. Solicitudes enviadas: **0**.
""", encoding="utf-8")

(HERE / "VEREDICTO_V185.md").write_text("""# Veredicto V185

**Promoción parcial y estrecha.** Existe evidencia oficial suficiente para afirmar que al 31/10/2023 una cuenta BNA de recuperos FONDYF FF13, 54395/36, tenía saldo bancario/certificado cero y saldo escritural e-SIDIF negativo por ARS 36,6 millones, y que el SAF 362 presentaba problemas de conciliación reiterados.

La evidencia **no alcanza** para tratar esos ARS 36,6 millones como dinero faltante, deuda, daño o beneficio bancario, ni para unir la cuenta con MY4002/BID1192. El hallazgo promueve un requerimiento contable dirigido; no una imputación.

Estado: `ACCOUNT_SPECIFIC_RECONCILIATION_GAP_PROVED_AT_2023_CUTOFF`; `MY4002_BID1192_LINK_OPEN`; `DAMAGE_OR_LIABILITY_NOT_PROVED`.
""", encoding="utf-8")

(HERE / "AUDITORIA_V185.md").write_text("""# Auditoría V185

- Catálogo maestro: 718 entradas únicas.
- Preservación: 718/718 archivos presentes y SHA-256 válidos.
- Incorporaciones: 10 PDFs oficiales UAI; todos controlados visualmente.
- Cuenta 54395/36: identidad y saldos exactos publicados al 31/10/2023.
- Continuidad individual 2024: no demostrable con resúmenes ejecutivos.
- Vinculación MY4002/BID1192/FONDEP: abierta.
- Solicitudes enviadas: 0; seis borradores nuevos.
""", encoding="utf-8")

(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V185_A_V186.md").write_text("""# Handover V185 → V186

## Cierre V185

Se identificó la cuenta BNA FONDYF 54395/36 al 31/10/2023: BNA 0, saldo bancario e-SIDIF 0 y saldo escritural e-SIDIF -ARS 36,6 millones. La actividad presupuestaria FONDYF tenía crédito ARS 3.094.874 y ejecución cero. La serie UAI mantiene observaciones generales de conciliación 2021-2024, pero sólo el corte 2023 individualiza la cuenta.

## Prioridad V186

1. Recuperar el Cuadro 1, Anexo A, consulta `Saldo Disponible` y fs. 16 completos del cierre 2023.
2. Obtener mayor, asiento de apertura/origen, conciliaciones, ajustes, certificado y extractos BNA 54395/36.
3. Ejecutar prueba negativa FONDYF→FONDEP y exigir convenio/asientos espejo o certificación de inexistencia.
4. Cruzar 54395/36 con MY4002/BID643/867/1192 sólo mediante identificadores transaccionales.
5. Mantener separadas discrepancia contable, faltante, deuda, daño y responsabilidad.

No enviar solicitudes sin autorización. Solicitudes enviadas: 0.
""", encoding="utf-8")

complete = {
    "checkpoint":"V185", "master_catalog_entries":718, "physical_sha_valid":718,
    "new_sources":10, "account_54395_36_exact_disclosure":True,
    "account_54395_36_bna_balance":0, "account_54395_36_esidif_bank_balance":0,
    "account_54395_36_esidif_ledger_balance":-36600000,
    "fondyf_budget_credit_2023":3094874, "fondyf_accrued_2023":0, "fondyf_paid_2023":0,
    "generic_reconciliation_findings_2021_2024":True,
    "account_54395_36_continuity_after_2023_proved":False,
    "account_54395_36_my4002_crosswalk_proved":False,
    "bid1192_composition_proved":False, "fondyf_to_fondep_transfer_proved":False,
    "damage_or_liability_proved":False, "requests_submitted":0,
}
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V185.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

append_once(CYCLE / "TRANSPARENCY_README.md", "## V185 · FONDYF 54395/36 y brecha de conciliación", """
## V185 · FONDYF 54395/36 y brecha de conciliación

UAI 22/2023 publica para BNA 54395/36 `FOND Y F Rec. FF13` saldos BNA/e-SIDIF bancario cero y e-SIDIF escritural -ARS 36,6 millones. La serie UAI registra conciliaciones pendientes 2021-2024, pero no individualiza esa cuenta después del corte 2023. Se promueve una brecha contable dirigida, no una imputación: MY4002/BID1192, transferencia, daño y responsabilidad continúan abiertos. Archivo 718/718; solicitudes 0.
""")

(REPO / "BACKUP_ACTUALIZACION_2026-09-01.md").write_text("""# Backup de actualización · 2026-09-01

- V185; 718/718 fuentes catalogadas, físicas y SHA-256 válidas; diez nuevas.
- Cuenta BNA FONDYF 54395/36 al 31/10/2023: BNA 0; e-SIDIF bancario 0; e-SIDIF escritural -ARS 36,6 millones.
- Actividad presupuestaria FONDYF: crédito ARS 3.094.874; devengado/pagado 0.
- Observaciones generales de conciliación SAF 362 repetidas 2021-2024; continuidad individual de 54395/36 no demostrada.
- MY4002/BID1192, transferencia FONDEP, faltante, daño y responsabilidad abiertos; solicitudes enviadas 0.
""", encoding="utf-8")

(SYNC / "SOURCE_SYNC_REPORT_V185.md").write_text("""# Source sync V185

- Diez informes oficiales UAI 2022-2025 incorporados.
- 718/718 fuentes físicas y SHA-256 válidas; brecha 0.
- Todos los PDFs nuevos fueron inspeccionados visualmente y catalogados con límites probatorios explícitos.
""", encoding="utf-8")
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V185.csv", [
    {"id":"PS185_01","endpoint":"UAI SAF 362 change of administration 22/2023","result":"exact FONDYF 54395/36 disclosure","preserved":"YES","limit":"ledger/reconciliation absent"},
    {"id":"PS185_02","endpoint":"UAI closure/account series 2021-2024","result":"generic repeated reconciliation findings","preserved":"YES","limit":"later account IDs absent"},
    {"id":"PS185_03","endpoint":"UAI FONDEP 17/2023","result":"successor control comparator","preserved":"YES","limit":"no FONDYF transfer proof"},
])

(HERE / "qa_v185.py").write_text("""from pathlib import Path
import csv,hashlib,json
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==718
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V185.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==718 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V185.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V185' and co['account_54395_36_esidif_ledger_balance']==-36600000
assert not co['account_54395_36_my4002_crosswalk_proved'] and not co['bid1192_composition_proved'] and not co['damage_or_liability_proved']
gap=rows('E0_FONDYF_54395_36_ACCOUNT_GAP_V185.csv'); assert len(gap)==8 and any(x['field']=='eSIDIF_ledger_balance' and x['value']=='-36600000' for x in gap)
tl=rows('E0_SAF362_RECONCILIATION_TIMELINE_2021_2024_V185.csv'); assert len(tl)==9 and sum(x['account_named']=='YES' for x in tl)==1
sep=rows('E0_FONDYF_MY4002_ACCOUNT_SEPARATION_V185.csv'); assert len(sep)==6 and sum(x['status']=='NOT_PROVED' for x in sep)>=3
assert len(rows('V185_SOURCE_BUNDLE.csv'))==10 and len(rows('V185_PDF_VISUAL_CONTROL.csv'))==10
obj=rows('E0_V185_REQUEST_OBJECTS.csv'); assert {'RO185_87','RO185_88','RO185_89','RO185_90','RO185_91','RO185_92'}<={x['row_id'] for x in obj}; assert all(x['status']=='DRAFT_NOT_SENT' for x in obj)
m=json.loads((H/'MANIFEST_V185.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V185' and m['parent_checkpoint']=='V184' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V185 QA PASS · 718/718 · 54395/36=-36.6m ESIDIF LEDGER · MY4002/BID1192=OPEN · damage=NO · requests=0')
""", encoding="utf-8")

(SYNC / "qa_source_sync_v185.py").write_text("""from pathlib import Path
import csv
R=Path(__file__).resolve().parents[5]
rows=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==718 and len({x['id'] for x in rows})==718
print('SOURCE SYNC V185 PASS · 10 new · 718/718')
""", encoding="utf-8")

origins = read_csv(ORIGINS)
by_path = {row["path"]:row for row in origins}
for path in iter_files(HIST):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"downloaded/preserved V185","note":"official UAI SAF 362/FONDEP source"}
for path in iter_files(SYNC):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V185","note":"ten-source synchronization"}
for path in HERE.iterdir():
    if path.is_file():
        by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V185","note":"FONDYF 54395/36 reconciliation checkpoint"}
for path in (AUDIT/"MASTER_LOCAL_HASH_VALIDATION_V185.csv",AUDIT/"SOURCE_BACKUP_CENSUS_V185.csv",AUDIT/"SOURCE_PRESERVATION_MISSING_V185.csv",AUDIT/"CURRENT_SOURCE_COMPLETENESS_V185.json"):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V185","note":"718-source completeness"}
write_csv(ORIGINS, list(by_path.values()), ["path","origin","note"])

(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")

manifest_files = [{"path":path.name,"bytes":path.stat().st_size,"sha256":sha(path)} for path in sorted(HERE.iterdir(), key=lambda item:item.name.casefold()) if path.is_file() and path.name != "MANIFEST_V185.json"]
manifest = {
    "checkpoint":"V185", "parent_checkpoint":"V184", "created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
    "exact_entities":34, "strict_coverage_pct":COVERAGE, "strict_asset_numerator_million_ars":NUMERATOR, "system_assets_million_ars":ASSETS,
    "new_promotions":["ACCOUNT_SPECIFIC_RECONCILIATION_GAP_PROVED_AT_2023_CUTOFF"],
    "source_archive":"718/718; 10 new catalogued official UAI sources",
    "historical_finding":"FONDYF BNA 54395/36 disclosed at 2023-10-31 with bank/certificate 0 and e-SIDIF ledger -ARS36.6m; generic SAF362 reconciliation findings 2021-2024",
    "account_54395_36":"EXACT_DISCLOSURE_ORIGIN_AND_RECONCILIATION_OPEN",
    "my4002_bid1192_crosswalk":"OPEN", "fondyf_fondep_transfer":"OPEN", "damage_or_liability":"NOT_PROVED",
    "closed_network_gate":"NO", "saf355_certifications":"0/5", "executed_historical_bank_rows":"0/10", "requests_submitted":0,
    "files":manifest_files,
}
(HERE / "MANIFEST_V185.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path":path.relative_to(REPO).as_posix(),"bytes":path.stat().st_size,"sha256":sha(path)} for path in iter_files(REPO) if path != global_manifest]
payload = {
    "checkpoint":"V185", "created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
    "strict_coverage_pct":COVERAGE, "exact_entities":34, "closed_network_gate":"NO",
    "source_audit":"718 master; 718 physical SHA-valid",
    "historical_workstream":"FONDYF 54395/36 exact 2023 disclosure; ledger reconciliation/MY4002/BID1192/FONDEP/damage open; drafts not sent",
    "file_count_excluding_manifest":len(global_files), "files":global_files,
}
temporary = global_manifest.with_suffix(".json.V185tmp")
temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
temporary.replace(global_manifest)
print("V185 BUILD PASS · catalog=718/718 · new=10 · 54395/36=-36.6m ESIDIF LEDGER · MY4002/BID1192=OPEN · requests=0")
