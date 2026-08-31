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

events = rows("E0_REFERENCE_2006_PARTICIPANT_AWARD_EVENT_MATRIX_V130.csv")
assert len(events) == 10
assert all(r["ultimate_holder_identified"] == "NO" for r in events)
assert all(r["cash_credit_status"] == "NOT_CONFIRMED" for r in events)
assert sum((d(r["awarded_effective_ars_raw"]) for r in events), d(0)) == d("96685934.350900")

dist = {r["participant"]: r for r in rows("E0_REFERENCE_2006_PUBLIC_TENDER_PARTICIPANT_DISTRIBUTION_V130.csv")}
assert len(dist) == 5
assert d(dist["Citibank"]["awarded_effective_ars_raw"]) == d("68965780.936900")
assert d(dist["HSBC Bank"]["awarded_effective_ars_raw"]) == d("21589872.974")
assert d(dist["Standard Bank"]["awarded_effective_ars_raw"]) == d("5715280.440000")
assert d(dist["MERVAL"]["awarded_effective_ars_raw"]) == d("415000.00")
assert dist["Citibank"]["bcra_peso_account_b9322"] == "016" and dist["Citibank"]["bcra_usd_account_b9322"] == "80016"
assert dist["HSBC Bank"]["bcra_peso_account_b9322"] == "150" and dist["HSBC Bank"]["bcra_usd_account_b9322"] == "80150"
assert dist["Standard Bank"]["bcra_peso_account_b9322"] == "015" and dist["Standard Bank"]["bcra_usd_account_b9322"] == "80015"
assert dist["MERVAL"]["bcra_peso_account_b9322"] == dist["MERVAL"]["bcra_usd_account_b9322"] == "UNKNOWN"

concentration = {r["metric"]: r for r in rows("E0_REFERENCE_2006_PARTICIPANT_CONCENTRATION_V130.csv")}
assert d(concentration["PARTICIPANT_HHI_0_10000"]["value"]).quantize(d("0.01")) == d("5621.68")
assert d(concentration["TOP1_SHARE_PCT"]["value"]).quantize(d("0.01")) == d("71.33")
assert d(concentration["TOP2_SHARE_PCT"]["value"]).quantize(d("0.01")) == d("93.66")
assert all(r["prohibited_inference"] for r in concentration.values())

versions = rows("E0_BCRA_2008_ACCOUNT_VERSION_AUDIT_V130.csv")
assert len(versions) == 8
assert sum(r["applicability_to_2008_08_28_through_2008_10_02"].startswith("YES") for r in versions) == 4
assert sum(r["finding"] == "NO_MERVAL_ACCOUNT_HOLDER_MATCH" for r in versions) == 2

targets = rows("E0_REFERENCE_2006_PAYMENT_RECORD_TARGET_MATRIX_V130.csv")
assert len(targets) == 10
assert all(r["caja_t2_transfer_record"] == r["bcra_credit_record"] == r["cryl_cancellation_record"] == "OPEN" for r in targets)
assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V130.csv")) == 144
assert len(rows("E0_FISCAL_METHOD_BREAKS_V130.csv")) == 106
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V130.csv")) == 92
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V130.csv")) == 75

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V130.csv")}
assert len(census) == 110
assert census["e0_bcra_com_b9195_cuentas_corrientes_2008"]["use_status"] == "SUPERSEDED_BEFORE_TARGET_TENDERS_VERSION_CONTROL"
assert census["e0_bcra_com_b9322_cuentas_corrientes_2008"]["use_status"] == "USABLE_ACCOUNT_DIRECTORY_EFFECTIVE_BEFORE_TARGET_TENDERS"
assert census["e0_argentina_rc_212_24_2008_recompra"]["use_status"] == "USABLE_NORMATIVE_PARTICIPANT_AND_SETTLEMENT_DOCUMENT_CHAIN"

with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 350 and len({r["id"] for r in catalog}) == 350
sources = {
    "bcra_com_b9195_cuentas_corrientes_2008.pdf": (217990, "70421c39f9ee663a387477b4abe6efef2fc94ef70678c2265578ddf9220098de"),
    "bcra_com_b9322_cuentas_corrientes_2008.pdf": (272233, "e2b588d85262ff8e3a7c586ecf43683178584958e9473aa9b10095464336c6c0"),
}
for name, (size, expected_hash) in sources.items():
    path = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v130" / "binaries" / name
    assert path.stat().st_size == size
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_hash

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V130.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V130"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 344
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v130_strict_changed"] is False

for name in ("README_V130.md", "VEREDICTO_V130.md", "E0_FISCAL_RECONSTRUCTION_V130.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V130_A_V131.md"):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "96.685.934,350900" in text
    assert "MERVAL" in text
    assert "DRAFT_NOT_SENT" in text or name == "VEREDICTO_V130.md"

for filename in ("REQUEST_ECONOMIA_TESORO_SETTLEMENT_V130.md", "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V130.md", "REQUEST_BCRA_CRYL_SETTLEMENT_V130.md", "REQUEST_CNV_CUSTODY_RECORDS_V130.md"):
    assert "Clave adicional V130" in (HERE / filename).read_text(encoding="utf-8-sig")

print("V130 QA PASS")
