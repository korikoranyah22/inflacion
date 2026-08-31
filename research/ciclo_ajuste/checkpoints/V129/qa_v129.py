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

def d(value):
    return Decimal(value)

awards = rows("E0_REFERENCE_2006_PUBLIC_TENDER_AWARDS_V129.csv")
assert len(awards) == 6
ars = [r for r in awards if r["isin"] == "ARARGE03E147"]
usd = [r for r in awards if r["isin"] == "ARARGE03E154"]
assert len(ars) == 4 and len(usd) == 2
assert sum((d(r["awarded_vno_native"]) for r in ars), d(0)) == d("1045342050")
assert sum((d(r["awarded_vno_native"]) for r in usd), d(0)) == d("29480362")
assert sum((d(r["awarded_effective_ars"]) for r in awards), d(0)) == d("96685934.36")
assert all(r["settlement_status"] == "SCHEDULED_NOT_INDEPENDENTLY_CONFIRMED" for r in awards)

allocation = {r["allocation_id"]: r for r in rows("E0_REFERENCE_2006_MODALITY_ALLOCATION_V129.csv")}
assert len(allocation) == 5
assert d(allocation["MA129_GDP_SUBTOTAL"]["public_tender_effective_million_ars"]) == d("96.68593436")
assert d(allocation["MA129_GDP_SUBTOTAL"]["residual_effective_central_million_ars"]) == d("1789.41406564")
assert d(allocation["MA129_TOTAL"]["residual_effective_central_million_ars"]) == d("3204.91406564")
assert d(allocation["MA129_TOTAL"]["residual_effective_lower_million_ars"]) == d("3204.90906564")
assert d(allocation["MA129_TOTAL"]["residual_effective_upper_million_ars"]) == d("3204.91906564")
assert d(allocation["MA129_GDP_SUBTOTAL"]["tender_share_of_official_effective_pct"]).quantize(d("0.01")) == d("5.13")
assert d(allocation["MA129_TOTAL"]["tender_share_of_official_effective_pct"]).quantize(d("0.01")) == d("2.93")

assert len(rows("E0_REFERENCE_2006_IMPUTATION_CHAIN_V129.csv")) == 6
assert len(rows("E0_OFFICIAL_2008_PLACEMENTS_XLS_SCOPE_AUDIT_V129.csv")) == 2
assert all(r["scope_result"] == "NOT_BUYBACK_LEDGER" for r in rows("E0_OFFICIAL_2008_PLACEMENTS_XLS_SCOPE_AUDIT_V129.csv"))
assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V129.csv")) == 140
assert len(rows("E0_FISCAL_METHOD_BREAKS_V129.csv")) == 103
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V129.csv")) == 88
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V129.csv")) == 71

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V129.csv")}
assert len(census) == 108
assert census["e0_argentina_recompras_decreto_1735_04_report"]["use_status"] == "USABLE_EXECUTED_REPURCHASE_OCCURRENCE_MODALITY_CLASS_THREE_ISIN_TOTAL"
assert census["e0_cgn_cuenta_inversion_2008_sdp"]["use_status"] == "USABLE_PROGRAM_TO_EXCESS_GDP_ACCOUNTING_IMPUTATION_BRIDGE"
assert census["e0_argentina_colocaciones_deuda_2008_xls"]["use_status"] == "NEGATIVE_SCOPE_EMISSIONS_ONLY_NOT_BUYBACK_LEDGER"

catalog = rows(str(REPO / "data" / "fuentes" / "FUENTES.csv")) if False else None
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    cat = list(csv.DictReader(f))
assert len(cat) == 348 and len({r["id"] for r in cat}) == 348
source = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v129" / "binaries" / "coloc2008_castellano_con_letras.xls"
assert source.stat().st_size == 83456
assert hashlib.sha256(source.read_bytes()).hexdigest() == "08077e8abac8a714e2d28b10a85d8f7b0510b0015c73cb94144569905d7e0fab"

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V129.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V129"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 342
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v129_strict_changed"] is False

for name in ("README_V129.md", "VEREDICTO_V129.md", "E0_FISCAL_RECONSTRUCTION_V129.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V129_A_V130.md"):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "96.68593436" in text
    assert "DRAFT_NOT_SENT" in text or name == "VEREDICTO_V129.md"

print("V129 QA PASS")
