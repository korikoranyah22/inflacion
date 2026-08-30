from pathlib import Path
from decimal import Decimal, getcontext
import csv
import hashlib
import json

p = Path(__file__).parent
repo = p.parents[3]
getcontext().prec = 120


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


required = [
    "README_V109.md",
    "AUDITORIA_V109.md",
    "VEREDICTO_V109.md",
    "SOURCE_REFERENCES_V109.md",
    "CURRENT_STATE_V109.csv",
    "FOUR_LEG_PASS_PANEL_V109.csv",
    "STRICT_Q4_FOUR_LEG_COVERAGE_V109.csv",
    "RECOVERY_QUEUE_V109.csv",
    "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V109.csv",
    "E0_BCRA_RISK_RECONSTRUCTION_V109.md",
    "E0_BCRA_DEBTOR_CLASSIFICATION_MONTHLY_V109.csv",
    "E0_BCRA_RISK_CAPITAL_LIQUIDITY_V109.csv",
    "E0_BCRA_RISK_CLOCKS_V109.csv",
    "E0_BCRA_RISK_VINTAGE_RECONCILIATION_V109.csv",
    "E0_BCRA_RISK_METHOD_BREAKS_V109.csv",
    "build_e0_bcra_debtor_classification_v109.ps1",
    "HISTORICAL_EPISODE_MATRIX_2001_2026_V109.csv",
    "HISTORICAL_EVIDENCE_COVERAGE_V109.csv",
    "HISTORICAL_SOURCE_QUEUE_V109.csv",
    "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V109_A_V110.md",
    "INHERITED_QA_STATUS_V109.csv",
    "MANIFEST_V109.json",
]
for name in required:
    assert (p / name).exists(), name

# Frozen V106+ microbank arithmetic.
coverage = rows(p / "STRICT_Q4_FOUR_LEG_COVERAGE_V109.csv")[0]
expected_numerator = Decimal("59812903.504")
expected_denominator = Decimal("96697695.5")
expected_pct = Decimal("61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549")
assert Decimal(coverage["asset_numerator_million_ars"]) == expected_numerator
assert Decimal(coverage["system_assets_million_ars"]) == expected_denominator
assert Decimal(coverage["asset_coverage_pct"]) == expected_pct
assert abs(expected_numerator / expected_denominator * Decimal(100) - expected_pct) < Decimal("1e-98")
assert coverage["closed_network_gate"] == "NO_MAJORITY_COVERAGE_BUT_NETWORK_STILL_OPEN"
state = rows(p / "CURRENT_STATE_V109.csv")
assert len([r for r in state if r["strict_panel_status"] == "ELIGIBLE"]) == 30
rioja = next(r for r in state if r["entity"] == "Banco Rioja S.A.U.")
assert "MISMATCH" in rioja["q4_four_leg_status"]

# Source inventory after the new official BCRA report.
catalog = rows(repo / "data" / "fuentes" / "FUENTES.csv")
assert len(catalog) == 226
catalog_by_id = {r["id"]: r for r in catalog}
new_id = "e0_bcra_informe_bancos_oct_2004_risk"
source = catalog_by_id[new_id]
assert source["sha256"] == "2a92bfc1de9fa86bc60c94d7ef867cf904e7d8713707a993eaf75d91c5c9f1cf"
assert source["fecha_descarga"] == "2026-08-29"
pdf = repo / source["archivo_local"].lstrip("/")
assert pdf.exists() and pdf.stat().st_size == 448224
assert pdf.read_bytes()[:5] == b"%PDF-"
assert hashlib.sha256(pdf.read_bytes()).hexdigest() == source["sha256"]

census = rows(p / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V109.csv")
assert len(census) == 28
assert len({r["source_id"] for r in census}) == 28
assert all(r["primary_source"] == "YES" and r["preserved"] == "YES" for r in census)
assert new_id in {r["source_id"] for r in census}
for row in census:
    assert row["source_id"] in catalog_by_id
    local = repo / row["local_path"].lstrip("/")
    assert local.exists(), local
    assert local.stat().st_size == int(row["bytes"])
    assert hashlib.sha256(local.read_bytes()).hexdigest() == row["sha256"]

source_audit = repo / "research" / "ciclo_ajuste" / "source_audit"
hash_rows = rows(source_audit / "MASTER_LOCAL_HASH_VALIDATION_V109.csv")
assert len(hash_rows) == 226
assert sum(r["exists"] == "True" for r in hash_rows) == 221
assert sum(r["hash_ok"] == "True" for r in hash_rows) == 221
new_hash = next(r for r in hash_rows if r["id"] == new_id)
assert new_hash["exists"] == "True" and new_hash["hash_ok"] == "True"

completeness = json.loads((source_audit / "CURRENT_SOURCE_COMPLETENESS_V109.json").read_text(encoding="utf-8"))
assert completeness["master_catalog_entries"] == 226
assert completeness["physical_local_copies"] == 221
assert completeness["physical_local_hash_ok"] == 221
assert completeness["e0_primary_sources_preserved"] == 28
assert completeness["e0_quality"] == "PRIMARY_RISK_CLOCKS_PARTIAL"
assert completeness["e0_risk_clock_rows"] == 9
assert completeness["e0_causal_net_incidence_identified"] is False

missing = rows(source_audit / "SOURCE_PRESERVATION_MISSING_V109.csv")
assert len(missing) == 8
assert not any(r["priority"] == "P0" for r in missing)
assert sum(r["priority"] == "P1" for r in missing) == 1
assert sum(r["priority"] == "DISCOVERY" for r in missing) == 7

# Monthly detail: the source's five literal dots remain missing.
monthly = rows(p / "E0_BCRA_DEBTOR_CLASSIFICATION_MONTHLY_V109.csv")
assert len(monthly) == 36
available = [r for r in monthly if r["source_status"] == "AVAILABLE"]
missing_months = [r["period"] for r in monthly if r["source_status"] == "PUBLISHED_AS_DOT"]
assert len(available) == 31
assert missing_months == ["2002-01", "2002-02", "2002-03", "2002-04", "2002-05"]
m = {r["period"]: r for r in monthly}
assert Decimal(m["2001-12"]["total_irregular_situations_3_to_6_pct"]) == Decimal("12.545961")
assert Decimal(m["2001-12"]["private_irregular_situations_3_to_6_pct"]) == Decimal("18.035634")
assert Decimal(m["2002-10"]["total_irregular_situations_3_to_6_pct"]) == Decimal("21.770759")
assert Decimal(m["2002-10"]["private_irregular_situations_3_to_6_pct"]) == Decimal("40.285006")
assert Decimal(m["2003-12"]["total_irregular_situations_3_to_6_pct"]) == Decimal("17.789776")
assert Decimal(m["2003-12"]["private_irregular_situations_3_to_6_pct"]) == Decimal("30.777864")
assert max(available, key=lambda r: Decimal(r["total_irregular_situations_3_to_6_pct"]))["period"] == "2002-10"
assert max(available, key=lambda r: Decimal(r["private_irregular_situations_3_to_6_pct"]))["period"] == "2002-10"

# Later-report annual table and exact derived ratios.
annual = rows(p / "E0_BCRA_RISK_CAPITAL_LIQUIDITY_V109.csv")
assert len(annual) == 3
a = {r["period"]: r for r in annual}
assert [Decimal(a[y]["total_irregular_pct"]) for y in ("2001", "2002", "2003")] == [Decimal("13.1"), Decimal("18.1"), Decimal("17.7")]
assert [Decimal(a[y]["provisions_over_irregular_pct"]) for y in ("2001", "2002", "2003")] == [Decimal("66.4"), Decimal("73.8"), Decimal("79.2")]
for year in ("2001", "2002", "2003"):
    row = a[year]
    liquidity = Decimal(row["liquid_assets_million_ars"]) / Decimal(row["total_deposits_million_ars"]) * 100
    capital = Decimal(row["net_worth_million_ars"]) / Decimal(row["net_assets_million_ars"]) * 100
    assert abs(liquidity - Decimal(row["liquid_assets_over_deposits_pct"])) < Decimal("1e-98")
    assert abs(capital - Decimal(row["accounting_net_worth_over_net_assets_pct"])) < Decimal("1e-98")

reconciliation = rows(p / "E0_BCRA_RISK_VINTAGE_RECONCILIATION_V109.csv")
assert len(reconciliation) == 6
assert all(r["status"] == "NOT_EXACTLY_RECONCILED" for r in reconciliation)
for row in reconciliation:
    delta = Decimal(row["later_report_irregular_pct"]) - Decimal(row["detail_workbook_irregular_pct"])
    assert delta == Decimal(row["later_report_minus_detail_pp"])

clocks = rows(p / "E0_BCRA_RISK_CLOCKS_V109.csv")
assert len(clocks) == 9
assert any(r["clock_id"] == "detail_total_irregular" and r["baseline_recovered_by_end"] == "NO" for r in clocks)
assert any(r["clock_id"] == "annual_provision_coverage" and r["baseline_recovered_by_end"] == "YES" for r in clocks)
assert any(r["clock_id"] == "annual_accounting_capitalization_proxy" and r["status"] == "ACCOUNTING_CAPITALIZATION_PROXY_DECLINED" for r in clocks)

breaks = rows(p / "E0_BCRA_RISK_METHOD_BREAKS_V109.csv")
assert len(breaks) == 8
assert {r["break_id"] for r in breaks} >= {"missing_2002_01_05", "publication_vintage_mismatch", "stock_flow_distinction", "capital_definition"}

evidence = rows(p / "HISTORICAL_EVIDENCE_COVERAGE_V109.csv")
risk = next(r for r in evidence if r["episode"] == "E0_2001_2003" and r["variable_family"] == "risk")
assert risk["quality"] == "PRIMARY_RISK_CLOCKS_PARTIAL"
assert risk["comparable"] == "WITHIN_VINTAGE_ONLY"
queue = rows(p / "HISTORICAL_SOURCE_QUEUE_V109.csv")
assert any(r["episode"] == "E0_2001_2003" and r["variable_family"] == "risk" and r["status"] == "RISK_CLOCKS_BUILT_MONTHLY_GAP_AND_VINTAGE_RECONCILIATION_OPEN" for r in queue)

historical = rows(p / "HISTORICAL_EPISODE_MATRIX_2001_2026_V109.csv")
assert {r["episode_id"] for r in historical} == {"E0", "E1", "E2", "E3", "E4", "E5", "E6"}
e0 = [r for r in historical if r["episode_id"] == "E0"]
assert len(e0) == 19
assert any(r["variable"] == "total_irregular_financing" and r["trough_date"] == "2002-10" for r in e0)
assert any(r["variable"] == "net_irregular_exposure_to_net_worth" and r["recovery_value"] == "11.9%" for r in e0)
assert not any(r["status"] == "CAUSAL" for r in historical)

# Checkpoint-local manifest excludes itself and must match every listed byte.
manifest = json.loads((p / "MANIFEST_V109.json").read_text(encoding="utf-8"))
assert manifest["checkpoint"] == "V109" and manifest["parent_checkpoint"] == "V108"
assert manifest["exact_entities"] == 30
assert manifest["e0_primary_sources"] == 28
assert manifest["new_official_sources"] == 1
assert manifest["risk_clock_rows"] == 9
for item in manifest["files"]:
    local = p / item["path"]
    assert local.exists(), local
    assert local.stat().st_size == item["bytes"]
    assert hashlib.sha256(local.read_bytes()).hexdigest() == item["sha256"]

print("V109 QA PASS")
