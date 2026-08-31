from decimal import Decimal
from pathlib import Path
import csv
import hashlib
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
AUDIT = REPO / "research" / "ciclo_ajuste" / "source_audit"

def rows(name):
    with (HERE / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

bridge = rows("E0_AGN_2008_DEBT_AUDIT_PROJECT_BRIDGE_V131.csv")
assert len(bridge) == 5
assert bridge[0]["identifier"] == "48 0237/09" and bridge[0]["published_fact"] == "27% de avance"
assert any(r["link_status"] == "SAME_PERIOD_AND_SUBJECT_PROBABLE_LINEAGE_NOT_EXPLICITLY_CROSSWALKED" for r in bridge)

flow = {r["audit_id"]: r for r in rows("E0_AGN_2008_DEBT_FLOW_ARITHMETIC_AUDIT_V131.csv")}
assert Decimal(flow["AF131_03"]["recomputed_value"]) == Decimal("1630")
assert Decimal(flow["AF131_04"]["published_value"]) == Decimal("2399")
assert Decimal(flow["AF131_05"]["residual"]) == Decimal("769")

fees = rows("E0_ANNUAL_SERVICE_FEE_SCOPE_AUDIT_V131.csv")
assert len(fees) == 7 and all(r["buyback_specific"] == "NO" for r in fees)
assert sum(Decimal(r["amount_ars"]) for r in fees[:3]) == Decimal("10215714.74")

bna = rows("E0_BNA_2008_BUYBACK_PUBLIC_DISCLOSURE_SCOPE_AUDIT_V131.csv")
assert len(bna) == 5 and all(r["status"] == "NEGATIVE_SCOPE_CONTROL_ONLY" for r in bna)

ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V131.csv")
assert len(ladder) == 10
assert sum(r["bcra_account_candidate"] == "EXACT_DIRECTORY_CANDIDATE" for r in ladder) == 9
assert all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)
summary = {r["stage"]: r for r in rows("E0_SETTLEMENT_EVIDENCE_LADDER_SUMMARY_V131.csv")}
assert summary["PUBLISHED_AWARD"]["closed_rows"] == "10"
assert summary["BCRA_ACCOUNT_CANDIDATE"]["closed_rows"] == "9"
for stage in ("ONCP_PREADJUDICATION_BODY", "CAJA_T2_TRANSFER", "CAJA_T3_REPORT", "FINANCE_ORDER_BCRA_CREDIT", "CRYL_CANCELLATION", "ULTIMATE_HOLDER"):
    assert summary[stage]["closed_rows"] == "0"

targets = rows("E0_REFERENCE_2006_PAYMENT_RECORD_TARGET_MATRIX_V131.csv")
assert len(targets) == 10
assert all(r["oncp_preaward_record"] == "TARGET_IDENTIFIED_BODY_NOT_LOCATED_PUBLICLY" for r in targets)
assert all(r["caja_t2_transfer_record"] == r["bcra_credit_record"] == r["cryl_cancellation_record"] == "OPEN" for r in targets)
assert len(rows("E0_PUBLIC_SETTLEMENT_RECORD_EXHAUSTION_V131.csv")) == 8
assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V131.csv")) == 148
assert len(rows("E0_FISCAL_METHOD_BREAKS_V131.csv")) == 109
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V131.csv")) == 96
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V131.csv")) == 80

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V131.csv")}
assert len(census) == 111
assert census["e0_agn_informe_segundo_trimestre_2009_act_48_0237_09"]["use_status"] == "USABLE_PROJECT_LOCATOR_PROGRESS_ONLY"
assert census["e0_agn_res_202_2009_act_41_2009_deuda"]["use_status"] == "USABLE_AGGREGATE_DEBT_CONTROL_NOT_SETTLEMENT_AUDIT"

with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 351 and len({r["id"] for r in catalog}) == 351
source = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v131" / "binaries" / "agn_2009_191_avance_2t_2009.pdf"
assert source.stat().st_size == 1534297
assert hashlib.sha256(source.read_bytes()).hexdigest() == "a702a4a9b1252fae6f837ca1ac76cd1a3dd5d3a2f685deebb01c111db692e7e3"

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V131.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V131"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 345
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v131_strict_changed"] is False

markers = {
    "REQUEST_AGN_2018_REPLY_V131.md": "## Clave V131 · proyecto 48 0237/09 y actuación final",
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V131.md": "## Clave V131 · expediente productor y submayores SIGADE/SIDIF",
    "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V131.md": "## Clave V131 · diez filas y ausencia del informe ejecutado en la vista pública",
    "REQUEST_BCRA_CRYL_SETTLEMENT_V131.md": "## Clave V131 · cero créditos confirmados no significa cero pagos",
    "REQUEST_CNV_CUSTODY_RECORDS_V131.md": "## Clave V131 · ruta MERVAL preservada como incógnita",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V131.md": "## Clave V131 · la memoria anual no sustituye el mandato ni el blotter",
}
for filename, marker in markers.items():
    text = (HERE / filename).read_text(encoding="utf-8-sig")
    assert marker in text and "BORRADOR_NO_ENVIADO" in text

for name in ("README_V131.md", "VEREDICTO_V131.md", "E0_FISCAL_RECONSTRUCTION_V131.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V131_A_V132.md"):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "0/10" in text and "48 0237/09" in text

print("V131 QA PASS")
