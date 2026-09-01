from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, getcontext
from pathlib import Path
import csv
import hashlib
import io
import json
import os
import subprocess


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
V164 = CYCLE / "checkpoints" / "V164"
AUDIT = CYCLE / "source_audit"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"
RAW_FY = REPO / "data/fuentes/credito_consumo/bcra_entidades/historico_2023_2026/202312d.7z"
RAW_9M = CYCLE / "inputs/bcra/2023-09/informacion_entidades_financieras_open_data/202309d.7z"
IEF_FY = CYCLE / "inputs/bcra/2023-12/informacion_entidades_financieras_open_data/202312e.pdf"
IEF_9M = CYCLE / "inputs/bcra/2023-09/informacion_entidades_financieras_open_data/202309e.pdf"
RIOJA_FY = CYCLE / "inputs/source_sync/v161/binaries/banco_rioja_eeff_fy2023.pdf"
FACTOR = Decimal("1.532908152197492")
NUMERATOR = Decimal("61248719.753")
SYSTEM_ASSETS = Decimal("96697695.5")
getcontext().prec = 120
COVERAGE = NUMERATOR / SYSTEM_ASSETS * Decimal(100)
EXCLUDED_DIRS = {".git", "__pycache__", "tmp", "node_modules"}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows, fields=None):
    fields = fields or (list(rows[0]) if rows else [])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted((name for name in dirnames if name not in EXCLUDED_DIRS), key=str.casefold)
        for filename in sorted(filenames, key=str.casefold):
            yield Path(dirpath) / filename


def clone_parent():
    excluded = {
        "build_V164.py", "qa_v164.py", "MANIFEST_V164.json", "CURRENT_STATE_V164.csv",
        "FOUR_LEG_PASS_PANEL_V164.csv", "STRICT_Q4_FOUR_LEG_COVERAGE_V164.csv",
        "README_V164.md", "VEREDICTO_V164.md", "AUDITORIA_V164.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V164_A_V165.md", "CORRECTION_LOG_V164.md",
        "BANCO_RIOJA_ADJUSTING_ENTRY_HYPOTHESIS_V164.md",
        "BANCO_RIOJA_CLOSING_LAYER_NOTE_V164.md",
        "BANCO_RIOJA_MISMATCH_ANALYTIC_NOTE_V164.md",
        "BANCO_RIOJA_CLOSING_LAYER_TIMELINE_V164.csv",
        "BANCO_RIOJA_STOCK_AND_RESULT_RECONCILIATION_V164.csv",
        "BANCO_RIOJA_DUAL_RESIDUAL_RECONCILIATION_V164.csv",
        "BANCO_RIOJA_Q4_SCENARIO_BOUND_V164.csv",
        "BANCO_RIOJA_PUBLIC_ROUTE_EXHAUSTION_V164.csv",
        "V164_PDF_VISUAL_CONTROL.csv", "V164_PUBLIC_SEARCH_LOG.csv", "V164_SOURCE_BUNDLE.csv",
    }
    for source in sorted(V164.iterdir(), key=lambda path: path.name.casefold()):
        if not source.is_file() or source.name in excluded:
            continue
        target = HERE / source.name.replace("V164", "V165")
        target.write_text(source.read_text(encoding="utf-8-sig").replace("V164", "V165"), encoding="utf-8")


def raw_accounts(archive: Path):
    member = "Entfin/Tec_Cont/baldet/00309.txt"
    result = subprocess.run(["tar", "-xOf", str(archive), member], capture_output=True)
    assert result.returncode == 0 and result.stdout
    text = result.stdout.decode("cp1252", errors="replace")
    rows = list(csv.reader(io.StringIO(text), delimiter="\t"))
    return {row[3]: {"description": row[4], "debit": Decimal(row[5]), "credit": Decimal(row[6])} for row in rows}


def whole(value: Decimal):
    assert value == value.to_integral_value()
    return str(int(value))


clone_parent()

# 1. Revalidate the complete source catalogue and read the raw closing layer directly.
catalog = read_csv(CATALOG)
assert len(catalog) == 584 and len({row["id"] for row in catalog}) == 584
audit_rows = []
for row in catalog:
    local = REPO / row["archivo_local"].lstrip("/")
    exists = local.is_file()
    actual = sha256(local) if exists else ""
    audit_rows.append({
        "id": row["id"], "archivo_local": row["archivo_local"], "exists": str(exists),
        "sha_catalog": row["sha256"].lower(), "sha_actual": actual,
        "hash_ok": str(exists and bool(row["sha256"]) and actual == row["sha256"].lower()),
    })
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V165.csv", audit_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V165.csv", audit_rows)
missing = [row for row in audit_rows if row["exists"] != "True" or row["hash_ok"] != "True"]
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V165.csv", missing, list(audit_rows[0]))
assert not missing

for source in (RAW_FY, RAW_9M, IEF_FY, IEF_9M, RIOJA_FY):
    assert source.is_file()

raw = raw_accounts(RAW_FY)
expected_raw = {
    "100000": (Decimal("96882462"), Decimal("0")),
    "300000": (Decimal("0"), Decimal("62510206")),
    "400000": (Decimal("0"), Decimal("35589212")),
    "500000": (Decimal("1216956"), Decimal("0")),
    "141144": (Decimal("28978965"), Decimal("0")),
    "141222": (Decimal("79394"), Decimal("0")),
    "511108": (Decimal("0"), Decimal("14250267")),
    "521108": (Decimal("7844"), Decimal("0")),
}
for account, values in expected_raw.items():
    assert (raw[account]["debit"], raw[account]["credit"]) == values

# 2. Reconcile the complete closing package, not only the repo line.
raw_assets = raw["100000"]["debit"]
audited_assets = Decimal("96944768")
raw_liabilities = raw["300000"]["credit"]
audited_liabilities = Decimal("62510206")
raw_pre_result_equity = raw["400000"]["credit"]
audited_pre_result_equity = sum(map(Decimal, ["1642672", "23704471", "8624732", "1617337"]))
raw_result = -raw["500000"]["debit"]
audited_result = Decimal("-1154650")
raw_net_equity = raw_assets - raw_liabilities
audited_net_equity = audited_assets - audited_liabilities
assert audited_assets - raw_assets == Decimal("62306")
assert audited_result - raw_result == Decimal("62306")
assert audited_liabilities == raw_liabilities
assert audited_pre_result_equity == raw_pre_result_equity
assert raw_net_equity == Decimal("34372256") and audited_net_equity == Decimal("34434562")

full_closing = [
    {"control_id":"BR165_01","measure":"total_assets","raw_thousand_ars":whole(raw_assets),"audited_thousand_ars":whole(audited_assets),"audited_minus_raw":whole(audited_assets-raw_assets),"verdict":"EXACT_CLOSING_LAYER_DELTA"},
    {"control_id":"BR165_02","measure":"total_liabilities","raw_thousand_ars":whole(raw_liabilities),"audited_thousand_ars":whole(audited_liabilities),"audited_minus_raw":"0","verdict":"EXACT_UNCHANGED"},
    {"control_id":"BR165_03","measure":"equity_before_current_result","raw_thousand_ars":whole(raw_pre_result_equity),"audited_thousand_ars":whole(audited_pre_result_equity),"audited_minus_raw":"0","verdict":"EXACT_UNCHANGED"},
    {"control_id":"BR165_04","measure":"current_result","raw_thousand_ars":whole(raw_result),"audited_thousand_ars":whole(audited_result),"audited_minus_raw":whole(audited_result-raw_result),"verdict":"EXACT_CLOSING_LAYER_DELTA"},
    {"control_id":"BR165_05","measure":"net_equity","raw_thousand_ars":whole(raw_net_equity),"audited_thousand_ars":whole(audited_net_equity),"audited_minus_raw":whole(audited_net_equity-raw_net_equity),"verdict":"EXACT_CLOSING_LAYER_DELTA"},
]
write_csv(HERE / "BANCO_RIOJA_FULL_CLOSING_BALANCE_RECONCILIATION_V165.csv", full_closing)

raw_repo_stock = raw["141144"]["debit"] + raw["141222"]["debit"]
audited_repo_stock = Decimal("29217148")
raw_nonrepo_assets = raw_assets - raw_repo_stock
audited_nonrepo_assets = audited_assets - audited_repo_stock
raw_repo_income = raw["511108"]["credit"]
audited_repo_income = Decimal("14409056")
raw_nonrepo_result = raw_result - raw_repo_income
audited_nonrepo_result = audited_result - audited_repo_income
assert audited_repo_stock - raw_repo_stock == Decimal("158789")
assert audited_repo_income - raw_repo_income == Decimal("158789")
assert audited_nonrepo_assets - raw_nonrepo_assets == Decimal("-96483")
assert audited_nonrepo_result - raw_nonrepo_result == Decimal("-96483")

decomposition = [
    {"control_id":"BR165_D01","side":"assets","component":"repo_stock","raw_thousand_ars":whole(raw_repo_stock),"audited_thousand_ars":whole(audited_repo_stock),"delta":whole(audited_repo_stock-raw_repo_stock),"identity_role":"POSITIVE_REPO_COMPONENT"},
    {"control_id":"BR165_D02","side":"assets","component":"all_nonrepo_assets","raw_thousand_ars":whole(raw_nonrepo_assets),"audited_thousand_ars":whole(audited_nonrepo_assets),"delta":whole(audited_nonrepo_assets-raw_nonrepo_assets),"identity_role":"OFFSET_COMPONENT"},
    {"control_id":"BR165_D03","side":"assets","component":"total_assets","raw_thousand_ars":whole(raw_assets),"audited_thousand_ars":whole(audited_assets),"delta":whole(audited_assets-raw_assets),"identity_role":"NET_CLOSING_DELTA"},
    {"control_id":"BR165_D04","side":"result","component":"repo_income","raw_thousand_ars":whole(raw_repo_income),"audited_thousand_ars":whole(audited_repo_income),"delta":whole(audited_repo_income-raw_repo_income),"identity_role":"POSITIVE_REPO_COMPONENT"},
    {"control_id":"BR165_D05","side":"result","component":"all_nonrepo_net_result","raw_thousand_ars":whole(raw_nonrepo_result),"audited_thousand_ars":whole(audited_nonrepo_result),"delta":whole(audited_nonrepo_result-raw_nonrepo_result),"identity_role":"OFFSET_COMPONENT"},
    {"control_id":"BR165_D06","side":"result","component":"current_result","raw_thousand_ars":whole(raw_result),"audited_thousand_ars":whole(audited_result),"delta":whole(audited_result-raw_result),"identity_role":"NET_CLOSING_DELTA"},
]
write_csv(HERE / "BANCO_RIOJA_CLOSING_ADJUSTMENT_DECOMPOSITION_V165.csv", decomposition)

ief_control = [
    {"period":"2023-09","source":"BCRA IEF 202309e.pdf","physical_page":"261","printed_page":"260","total_assets_million_ars":"71886.2","current_result_million_ars":"1258.6","audit_marker":"8_SIN_OBSERVACIONES","use":"PUBLIC_ROUNDED_9M_CONTROL_NOT_REPO_RESULT_OPENING"},
    {"period":"2023-12","source":"BCRA IEF 202312e.pdf","physical_page":"261","printed_page":"260","total_assets_million_ars":"96882.5","current_result_million_ars":"-1217.0","audit_marker":"NO_MARKER_IN_TABLE","use":"PUBLIC_ROUNDED_RENDER_OF_RAW_CLOSING_LAYER"},
]
write_csv(HERE / "BANCO_RIOJA_BCRA_IEF_PUBLICATION_CONTROL_V165.csv", ief_control)

timeline = [
    {"sequence":"1","event":"BCRA raw entity-detail member timestamp","date_or_timestamp":"2024-03-04 14:18:17.8813456","evidence":"202312d.7z / Entfin/Tec_Cont/baldet/00309.txt member metadata","interpretation":"Archive-member metadata, not proof of submission date."},
    {"sequence":"2","event":"BCRA monthly IEF PDF creation metadata","date_or_timestamp":"2024-03-08 15:50:09","evidence":"202312e.pdf metadata and printed Banco Rioja page 260","interpretation":"Public report reproduces the raw 96882462k asset total and -1216956k result after rounding; creation metadata is not formal publication-date proof."},
    {"sequence":"3","event":"Independent auditor report date","date_or_timestamp":"2024-03-11","evidence":"Banco Rioja FY2023 audited financial statements","interpretation":"Signed package contains a +62306k net asset/result closing delta and a +158789k repo stock/income component."},
    {"sequence":"4","event":"Annual discipline-market PDF creation metadata","date_or_timestamp":"2024-04-23 11:04:54","evidence":"DM-31-12-23.pdf metadata","interpretation":"Later disclosure copies the audited repo stock into publication and supervision; metadata is not formal publication-date proof."},
]
write_csv(HERE / "BANCO_RIOJA_CLOSING_LAYER_TIMELINE_V165.csv", timeline)

recon = read_csv(V164 / "BANCO_RIOJA_STOCK_AND_RESULT_RECONCILIATION_V164.csv")
for index, row in enumerate(recon, start=1):
    row["control_id"] = f"BR165_{index:02d}"
recon.extend([
    {"control_id":"BR165_10","period":"FY-2023","measure":"total_asset_and_current_result_closing_delta","issuer_value_thousand_ars":"62306","raw_account_set":"100000_AND_500000","raw_values_thousand_ars":"96882462_assets_and_-1216956_result","raw_sum_thousand_ars":"N/A","difference_issuer_minus_raw":"62306","verdict":"EXACT_FULL_CLOSING_PACKAGE_DUAL_DELTA","analytic_use":"Audited assets and current result each improve by 62306; liabilities and pre-result equity remain exact."},
    {"control_id":"BR165_11","period":"FY-2023","measure":"nonrepo_offset_component","issuer_value_thousand_ars":"-96483","raw_account_set":"TOTAL_MINUS_REPO_COMPONENT","raw_values_thousand_ars":"62306-158789","raw_sum_thousand_ars":"-96483","difference_issuer_minus_raw":"-96483","verdict":"EXACT_RESIDUAL_DECOMPOSITION_NOT_JOURNAL_AUTHENTICATION","analytic_use":"Shows the repo +158789 component is offset by -96483 elsewhere; does not identify the number or nature of underlying entries."},
])
write_csv(HERE / "BANCO_RIOJA_STOCK_AND_RESULT_RECONCILIATION_V165.csv", recon)
write_csv(HERE / "BANCO_RIOJA_DUAL_RESIDUAL_RECONCILIATION_V165.csv", [row for row in recon if row["control_id"] in {"BR165_02","BR165_03","BR165_10","BR165_11"}])

q4_raw_income = Decimal("14250267") - Decimal("5712151") * FACTOR
q4_adjusted_income = Decimal("14409056") - Decimal("5712151") * FACTOR
q4_expense = Decimal("7844") - Decimal("5117") * FACTOR
write_csv(HERE / "BANCO_RIOJA_Q4_SCENARIO_BOUND_V165.csv", [
    {"scenario":"REGULATORY_RAW_TO_RAW","q4_income_bcra_thousand_ars":str(q4_raw_income),"q4_expense_bcra_thousand_ars":str(q4_expense),"panel_use":"NO","remaining_gate":"Issuer 9M result opening absent."},
    {"scenario":"AUDITED_CLOSING_LAYER","q4_income_bcra_thousand_ars":str(q4_adjusted_income),"q4_expense_bcra_thousand_ars":str(q4_expense),"panel_use":"NO","remaining_gate":"Full closing package reconciled arithmetically; journal and issuer 9M result opening remain absent."},
])

# 3. Human interpretation, with an explicit line between identity and journal evidence.
note = f"""# Banco Rioja: paquete de cierre reconciliado V165

## Identidades demostradas

El detalle BCRA cierra con activo por 96.882.462k, pasivo por 62.510.206k, patrimonio previo al resultado por 35.589.212k y resultado corriente de -1.216.956k. Los estados auditados conservan exactamente pasivos y patrimonio previo al resultado, pero elevan activo y resultado corriente en 62.306k: activo 96.944.768k y pérdida -1.154.650k.

Dentro de ese movimiento neto, operaciones de pase e ingreso por pases suben exactamente 158.789k. Al excluir pases en ambos lados, el resto de activos y el resto del resultado se reducen exactamente 96.483k. Por construcción: `158.789 - 96.483 = 62.306`.

La coincidencia activo/resultado, junto con pasivos y patrimonio previo invariables, demuestra un paquete de cierre aritméticamente equilibrado con efecto neto débito-activo/crédito-resultado por 62.306k. También demuestra que el componente de pases de 158.789k no fue el único cambio entre capas.

## Qué no demuestra

La aritmética no revela si existió un asiento compuesto o varios asientos, ni identifica las cuentas que forman el offset no-pases de -96.483k. Tampoco sustituye diario, comprobante, papel de trabajo, conciliación firmada o apertura 9M del resultado de pases. El rango Q4 sigue entre {q4_raw_income}k y {q4_adjusted_income}k; no hay promoción al panel.
"""
(HERE / "BANCO_RIOJA_CLOSING_PACKAGE_NOTE_V165.md").write_text(note, encoding="utf-8")
(HERE / "BANCO_RIOJA_CLOSING_LAYER_NOTE_V165.md").write_text(note, encoding="utf-8")
(HERE / "BANCO_RIOJA_ADJUSTING_ENTRY_HYPOTHESIS_V165.md").write_text(note, encoding="utf-8")
(HERE / "BANCO_RIOJA_MISMATCH_ANALYTIC_NOTE_V165.md").write_text(note, encoding="utf-8")
(HERE / "CORRECTION_LOG_V165.md").write_text("""# Historial de corrección V165

V165 mantiene la corrección de V163/V164: el stock raw de pases es 29.058.359k y su diferencia contra el cierre auditado es 158.789k, no 238.183k.

La novedad es la reconciliación de todo el balance: activo y resultado corriente cambian 62.306k; pasivos y patrimonio previo al resultado no cambian. El componente pases aporta +158.789k y el resto aporta -96.483k. Esto autentica la identidad del paquete de cierre, no el diario ni la cantidad de asientos.
""", encoding="utf-8")

# 4. Preserve the strict gate and panel denominator.
state = read_csv(V164 / "CURRENT_STATE_V164.csv")
rioja = next(row for row in state if row["entity"] == "Banco Rioja S.A.U.")
rioja.update({
    "fy_status":"OFFICIAL_FY_FULL_CLOSING_PACKAGE_RECONCILED_ASSETS_RESULT_DELTA_62306K_REPO_COMPONENT_158789K_NONREPO_OFFSET_MINUS96483K_V165",
    "nine_month_status":"BCRA_IEF_9M_PUBLIC_TOTAL_RESULT_CONTROL_AVAILABLE_NO_ISSUER_REPO_RESULT_OPENING_V165",
    "q4_four_leg_status":"N/D_STRICT_CLOSING_PACKAGE_RECONCILED_JOURNAL_AND_9M_OPENING_ABSENT",
    "strict_panel_status":"PENDING","priority":"HOLD_V165_SIGNED_JOURNAL_OR_ISSUER_9M_REPO_RESULT_OPENING",
    "next_action":"obtain journal/workpaper or compatible issuer 9M repo-result opening; full closing-package arithmetic is now exhausted",
})
write_csv(HERE / "CURRENT_STATE_V165.csv", state)

panel = read_csv(V164 / "FOUR_LEG_PASS_PANEL_V164.csv")
for row in panel:
    if row["entity"] == "Banco Rioja S.A.U.":
        row.update({
            "quality":"FULL_CLOSING_PACKAGE_RECONCILED_JOURNAL_AND_9M_OPENING_ABSENT",
            "target_basis_compatible":"YES_BASIS_AND_CLOSING_PACKAGE_PROVEN_RESULT_FLOW_GATE_OPEN",
            "system_panel_eligible_v72":"NO",
            "v72_note":"V165: raw-to-audited assets and current result each change +62,306k; liabilities and pre-result equity are unchanged. Repo contributes +158,789k and nonrepo residual -96,483k. Journal/9M issuer opening absent; no promotion.",
        })
write_csv(HERE / "FOUR_LEG_PASS_PANEL_V165.csv", panel)

coverage = read_csv(V164 / "STRICT_Q4_FOUR_LEG_COVERAGE_V164.csv")
coverage[0]["coverage_set"] = "V165 strict 33-entity set; Banco Rioja full closing package reconciled but result-flow gate open"
if "v161_change" in coverage[0]:
    coverage[0]["v161_change"] = "V165: no numeric change; Rioja full closing-package arithmetic closed, journal and 9M result opening absent."
write_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V165.csv", coverage)

# 5. Source, route, and visual controls.
routes = [
    {"control_id":"WEB165_01","institution":"BCRA","url":"https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Entidades/202309e.pdf","result":"OFFICIAL_9M_IEF_PUBLIC_TOTALS_LOCALLY_PRESERVED","decision":"USE_AS_ROUNDED_PUBLIC_CONTROL_NOT_REPO_OPENING"},
    {"control_id":"WEB165_02","institution":"BCRA","url":"https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Entidades/202312e.pdf","result":"OFFICIAL_FY_IEF_PUBLIC_TOTALS_LOCALLY_PRESERVED","decision":"USE_AS_PUBLIC_RAW_LAYER_CONTROL"},
    {"control_id":"WEB165_03","institution":"Banco Rioja","url":"https://bancorioja.com.ar/pdf/EEFF-BR-2023.pdf","result":"OFFICIAL_AUDITED_CLOSING_PACKAGE_LOCALLY_PRESERVED","decision":"USE_AS_SIGNED_CLOSING_LAYER"},
    {"control_id":"WEB165_04","institution":"Banco Rioja","url":"https://bancorioja.com.ar/institucional/disciplina-de-mercado","result":"NO_ISSUER_9M_REPO_RESULT_OPENING_IN_PUBLIC_DISCIPLINE_FILES","decision":"HOLD_RESULT_FLOW_GATE"},
]
write_csv(HERE / "BANCO_RIOJA_PUBLIC_ROUTE_EXHAUSTION_V165.csv", routes)
write_csv(HERE / "V165_PUBLIC_SEARCH_LOG.csv", routes)

bundle_specs = [
    ("BCRA_IEF_9M", IEF_9M, routes[0]["url"]),
    ("BCRA_IEF_FY", IEF_FY, routes[1]["url"]),
    ("BCRA_RAW_9M", RAW_9M, "OFFICIAL_LOCAL_ARCHIVE_ALREADY_CATALOGUED"),
    ("BCRA_RAW_FY", RAW_FY, "OFFICIAL_LOCAL_ARCHIVE_ALREADY_CATALOGUED"),
    ("RIOJA_AUDITED_FY", RIOJA_FY, routes[2]["url"]),
]
bundle = []
for role, path, url in bundle_specs:
    bundle.append({"role":role,"path":"/"+path.relative_to(REPO).as_posix(),"url":url,"bytes":str(path.stat().st_size),"sha256":sha256(path),"analytic_use":"Banco Rioja full closing-package reconciliation V165"})
write_csv(HERE / "V165_SOURCE_BUNDLE.csv", bundle)

visual = [
    {"control_id":"PV165_01","artifact":"202309e.pdf","page":"261","result":"PASS","observation":"Banco Rioja 9M public totals; printed page 260; 71,886.2m assets and 1,258.6m accumulated result."},
    {"control_id":"PV165_02","artifact":"202312e.pdf","page":"261","result":"PASS","observation":"Banco Rioja raw/public closing layer; printed page 260; 96,882.5m assets and -1,217.0m result."},
    {"control_id":"PV165_03","artifact":"EEFF-BR-2023.pdf","page":"3","result":"PASS","observation":"Audited total assets 96,944,768k and repo stock 29,217,148k."},
    {"control_id":"PV165_04","artifact":"EEFF-BR-2023.pdf","page":"4","result":"PASS","observation":"Audited liabilities 62,510,206k, net equity 34,434,562k, and current result -1,154,650k."},
    {"control_id":"PV165_05","artifact":"EEFF-BR-2023.pdf","page":"5","result":"PASS","observation":"Audited statement of results confirms current result -1,154,650k."},
]
for row in visual:
    row["method"] = "Poppler render + original-detail visual inspection"
write_csv(HERE / "V165_PDF_VISUAL_CONTROL.csv", visual)

# 6. Checkpoint summaries and handover.
(HERE / "README_V165.md").write_text(f"""# Checkpoint V165

- Archivo fuente: 584/584 copias locales con hash válido; fuentes nuevas 0.
- Banco Rioja: activo raw 96.882.462k versus auditado 96.944.768k; delta +62.306k.
- Resultado raw -1.216.956k versus auditado -1.154.650k; delta +62.306k.
- Pasivos 62.510.206k y patrimonio previo al resultado 35.589.212k: exactos e invariantes entre capas.
- Descomposición: pases +158.789k; resto de activos/resultado -96.483k; neto +62.306k.
- Esto prueba el paquete de cierre aritmético, no el diario ni la cantidad de asientos.
- Panel sin cambio: 33 entidades exactas; cobertura {COVERAGE}%.
- SAF355 0/5; ejecución histórica 0/10; seis borradores no enviados.
""", encoding="utf-8")
(HERE / "VEREDICTO_V165.md").write_text(f"""# Veredicto V165

V165 demuestra que la diferencia de Banco Rioja forma parte de un paquete de cierre completo y equilibrado. Entre el detalle BCRA y los estados auditados, activo y resultado corriente mejoran 62.306k; pasivos y patrimonio anterior al resultado no cambian. El componente de pases aporta +158.789k y el conjunto no-pases compensa -96.483k. Esta igualdad confirma capas contables distintas y un efecto neto débito-activo/crédito-resultado, pero no autentica diario, comprobante ni número de asientos. Sin apertura 9M del resultado de pases, Banco Rioja permanece fuera del panel: 33 entidades y {COVERAGE}%.
""", encoding="utf-8")
(HERE / "AUDITORIA_V165.md").write_text(f"""# Auditoría V165

- Catálogo/copia/hash: 584/584; huecos: 0; fuentes nuevas: 0.
- Visual: 5 páginas relevantes inspeccionadas en resolución original.
- Raw leído directamente desde `202312d.7z/Entfin/Tec_Cont/baldet/00309.txt`.
- Identidades: activo/result +62.306k; pasivos/pre-result equity 0; repo +158.789k; no-repo -96.483k.
- Decisión: paquete de cierre reconciliado; diario y flujo 9M no autenticados; promociones 0.
- Panel: 33 exactas, {COVERAGE}%; pedidos/respuestas 0/0.
""", encoding="utf-8")
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V165_A_V166.md").write_text(f"""# Handover V165 → V166

## Cerrado en V165

- Banco Rioja: paquete raw-auditado reconciliado completamente por totales.
- Activo y resultado +62.306k; pasivos y patrimonio previo sin cambio.
- Componente pases +158.789k; offset no-pases -96.483k.
- Panel sin cambio: 33 entidades, cobertura {COVERAGE}%.

## Prioridad V166

1. Buscar diario, comprobante, papel de trabajo o conciliación firmada del paquete de cierre.
2. Buscar apertura 9M-2023 del resultado de pases; el IEF sólo da total acumulado.
3. Identificar, si una fuente primaria lo permite, la composición del offset no-pases de -96.483k.
4. Retomar Plan SIGEN 2009, Nota 3672/09 y crosswalk UAI-entidad-proyecto-informe si las rutas públicas bancarias quedan agotadas.
5. Mantener SAF355 0/5, ejecución 0/10 y seis borradores no enviados hasta evidencia o autorización.
""", encoding="utf-8")

source_refs = HERE / "SOURCE_REFERENCES_V165.md"
with source_refs.open("a", encoding="utf-8") as handle:
    handle.write(f"\n- `bcra_entidades_sep2023_hist` · IEF septiembre 2023 · {routes[0]['url']} · `/{IEF_9M.relative_to(REPO).as_posix()}` · `{sha256(IEF_9M)}`\n")
    handle.write(f"- `bcra_entidades_dic2023_red_pases` · IEF diciembre 2023 · {routes[1]['url']} · `/{IEF_FY.relative_to(REPO).as_posix()}` · `{sha256(IEF_FY)}`\n")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V164.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint":"V165","date":"2026-08-31","master_catalog_entries":584,
    "physical_local_copies":584,"physical_local_hash_ok":584,"remaining_catalog_physical_or_hash_gaps":0,
    "state":"SOURCE_ARCHIVE_COMPLETE_RIOJA_FULL_CLOSING_PACKAGE_RECONCILED_JOURNAL_AND_9M_OPENING_ABSENT",
    "analytical_promotion":"NONE_V165_FULL_CLOSING_PACKAGE_IDENTITY_ONLY",
    "exact_entities":33,"strict_asset_numerator_million_ars":str(NUMERATOR),
    "system_assets_million_ars":str(SYSTEM_ASSETS),"strict_coverage_pct":str(COVERAGE),
    "strict_coverage_increment_v164_pp":"0","request_drafts_status":"DRAFT_NOT_SENT",
    "requests_submitted":0,"responses_received":0,"saf355_certifications_located":0,
    "executed_historical_bank_rows_confirmed":0,"discovered_official_binary_recovery_queue":0,
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V165.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

# 7. Provenance, transparency, trees, and manifests.
origin_rows = read_csv(ORIGINS)
origin_by_path = {row["path"]: row for row in origin_rows}
for path in sorted(HERE.iterdir(), key=lambda item: item.name.casefold()):
    if path.is_file():
        rel = path.relative_to(CYCLE).as_posix()
        origin_by_path[rel] = {"path":rel,"origin":"generated/updated V165","note":"Banco Rioja full closing-package reconciliation checkpoint"}
for path in [AUDIT/"MASTER_LOCAL_HASH_VALIDATION_V165.csv", AUDIT/"SOURCE_BACKUP_CENSUS_V165.csv", AUDIT/"SOURCE_PRESERVATION_MISSING_V165.csv", AUDIT/"CURRENT_SOURCE_COMPLETENESS_V165.json"]:
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path":rel,"origin":"generated/updated V165","note":"584-source physical/hash completeness control"}
write_csv(ORIGINS, list(origin_by_path.values()), ["path","origin","note"])

transparency = CYCLE / "TRANSPARENCY_README.md"
transparency_text = transparency.read_text(encoding="utf-8-sig")
if "## V165 · Paquete de cierre Banco Rioja" not in transparency_text:
    transparency_text += """

## V165 · Paquete de cierre Banco Rioja

El activo y el resultado corriente pasan del raw al auditado con el mismo delta de +62.306k; pasivos y patrimonio previo al resultado quedan invariantes. Pases aporta +158.789k y el resto compensa -96.483k. La identidad prueba un paquete de cierre equilibrado, pero no autentica diario, comprobante, número de asientos ni apertura 9M. El panel permanece en 33 entidades.
"""
    transparency.write_text(transparency_text, encoding="utf-8")

(REPO / "BACKUP_ACTUALIZACION_2026-08-31.md").write_text(f"""# Backup de actualización · 2026-08-31

- Checkpoint: V165.
- Fuentes catalogadas: 584/584 local y SHA-válido; cola binaria pendiente: 0.
- Banco Rioja: paquete de cierre reconciliado por totales; diario y apertura 9M pendientes.
- Panel: 33 entidades, {COVERAGE}% de activos; promociones 0.
- Solicitudes: 0 enviadas; seis borradores DRAFT_NOT_SENT.
""", encoding="utf-8")


def tree(root: Path):
    lines = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted((name for name in dirnames if name not in EXCLUDED_DIRS), key=str.casefold)
        base = Path(dirpath)
        lines.extend((base/name).relative_to(root).as_posix()+"/" for name in dirnames)
        lines.extend((base/name).relative_to(root).as_posix() for name in sorted(filenames, key=str.casefold))
    return "\n".join(lines)+"\n"


(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")

files = [{"path":path.name,"bytes":path.stat().st_size,"sha256":sha256(path)} for path in sorted(HERE.iterdir(), key=lambda item:item.name.casefold()) if path.is_file() and path.name != "MANIFEST_V165.json"]
manifest = {
    "checkpoint":"V165","parent_checkpoint":"V164","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
    "exact_entities":33,"strict_coverage_pct":str(COVERAGE),"strict_asset_numerator_million_ars":str(NUMERATOR),"system_assets_million_ars":str(SYSTEM_ASSETS),
    "new_promotions":[],"negative_controls":["Banco Rioja full closing package reconciled, journal and 9M opening absent","HSBC counterparty split open"],
    "rioja_finding":"Raw-to-audited assets and current result +62306k; liabilities and pre-result equity unchanged; repo +158789k; nonrepo -96483k",
    "source_archive":"584/584 catalogued physical SHA-valid; new sources 0; BCRA binary queue 0",
    "closed_network_gate":"NO","saf355_certifications":"0/5","executed_historical_bank_rows":"0/10","requests_submitted":0,"files":files,
}
(HERE / "MANIFEST_V165.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path":path.relative_to(REPO).as_posix(),"bytes":path.stat().st_size,"sha256":sha256(path)} for path in iter_files(REPO) if path != global_manifest]
global_payload = {
    "checkpoint":"V165","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
    "strict_coverage_pct":str(COVERAGE),"exact_entities":33,"closed_network_gate":"NO",
    "source_audit":"584 master; 584 physical SHA-valid; Rioja full closing package reconciled, journal and 9M opening absent",
    "historical_workstream":"Plan SIGEN 2009, Nota 3672/09, SAF355 and bank execution remain open; six drafts not sent",
    "file_count_excluding_manifest":len(global_files),"files":global_files,
}
tmp = global_manifest.with_suffix(".json.V165tmp")
tmp.write_text(json.dumps(global_payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
tmp.replace(global_manifest)

print(f"V165 BUILD PASS · exact=33 · coverage={COVERAGE} · catalog=584/584 · promotions=0")
