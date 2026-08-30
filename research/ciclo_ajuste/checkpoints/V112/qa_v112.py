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
    "README_V112.md",
    "AUDITORIA_V112.md",
    "VEREDICTO_V112.md",
    "SOURCE_REFERENCES_V112.md",
    "CURRENT_STATE_V112.csv",
    "FOUR_LEG_PASS_PANEL_V112.csv",
    "STRICT_Q4_FOUR_LEG_COVERAGE_V112.csv",
    "RECOVERY_QUEUE_V112.csv",
    "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V112.csv",
    "E0_FISCAL_RECONSTRUCTION_V112.md",
    "E0_FISCAL_MECHANISM_LEDGER_V112.csv",
    "E0_FISCAL_TRANSACTION_LEDGER_2004_2006_V112.csv",
    "E0_FISCAL_TRANSACTION_LEDGER_2007_2012_V112.csv",
    "E0_FISCAL_STOCK_FLOW_BRIDGE_V112.csv",
    "E0_FISCAL_BODEN_SERVICE_BRIDGE_2007_2012_V112.csv",
    "E0_FISCAL_BODEN_STOCK_BRIDGE_2007_2012_V112.csv",
    "E0_FISCAL_METHOD_BREAKS_V112.csv",
    "HISTORICAL_EPISODE_MATRIX_2001_2026_V112.csv",
    "HISTORICAL_EVIDENCE_COVERAGE_V112.csv",
    "HISTORICAL_SOURCE_QUEUE_V112.csv",
    "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V112_A_V113.md",
    "INHERITED_QA_STATUS_V112.csv",
    "build_e0_fiscal_v112.py",
    "qa_v112.py",
    "MANIFEST_V112.json",
]
for name in required:
    assert (p / name).exists(), name


inherited = rows(p / "INHERITED_QA_STATUS_V112.csv")
assert any(r["script"] == "qa_v111.py" and r["post_v112_result"] == "EXPECTED_SUPERSEDED_ASSERTION" for r in inherited)
assert any(r["script"] == "qa_v112.py" and r["post_v112_result"] == "PASS" for r in inherited)


coverage = rows(p / "STRICT_Q4_FOUR_LEG_COVERAGE_V112.csv")[0]
expected_numerator = Decimal("59812903.504")
expected_denominator = Decimal("96697695.5")
expected_pct = Decimal("61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549")
assert Decimal(coverage["asset_numerator_million_ars"]) == expected_numerator
assert Decimal(coverage["system_assets_million_ars"]) == expected_denominator
assert Decimal(coverage["asset_coverage_pct"]) == expected_pct
assert abs(expected_numerator / expected_denominator * Decimal(100) - expected_pct) < Decimal("1e-98")
assert coverage["closed_network_gate"] == "NO_MAJORITY_COVERAGE_BUT_NETWORK_STILL_OPEN"
state = rows(p / "CURRENT_STATE_V112.csv")
assert len([r for r in state if r["strict_panel_status"] == "ELIGIBLE"]) == 30
rioja = next(r for r in state if r["entity"] == "Banco Rioja S.A.U.")
assert "MISMATCH" in rioja["q4_four_leg_status"]


new_sources = {
    "e0_agn_res_102_2011_act_366_2009_fgs": (10521239, "8025d4fc331b9256072baef0827eb03ae4f12a0c9d987f980364c40fe0da7481"),
    "e0_agn_res_202_2009_act_41_2009_deuda": (418450, "14053bc9c6c51382b28fe7a854c926ac776701e43534b5ad6438a903165332f8"),
    "e0_cgn_cuenta_inversion_2007_sdp": (1042529, "90303a1e0526971bec25b8d1f17c2be7b1decc390d356287c9c6879304b98e6b"),
    "e0_cgn_cuenta_inversion_2008_sdp": (1995800, "aa51ee0f6c292bd070900716d34a9ceca42a12b94e1b0845bb915d04c25f9084"),
    "e0_cgn_cuenta_inversion_2009_sdp": (764356, "8de64854c33d0d4291e94826a536eed5eca4055fd2159eb7ca23189cb1c406c1"),
    "e0_cgn_cuenta_inversion_2010_sdp": (569175, "678cd9942b6015459e7ef23dca6b2098e67aeb8a8713d7703ed9883d632157d2"),
    "e0_cgn_cuenta_inversion_2011_sdp": (1105867, "2ccd64bcc4f439fd64788201563de3ff406b37a911ef7624a9f5d4594ac85111"),
    "e0_cgn_cuenta_inversion_2012_sdp": (3149094, "612f97761b950bfeb9bc12df21c6135ca3eb31a226cd6ed403a1569cc8ea4d4b"),
}
catalog = rows(repo / "data" / "fuentes" / "FUENTES.csv")
assert len(catalog) == 246
catalog_by_id = {r["id"]: r for r in catalog}
for source_id, (size, digest) in new_sources.items():
    source = catalog_by_id[source_id]
    assert source["fecha_descarga"] == "2026-08-29"
    assert source["sha256"] == digest
    local = repo / source["archivo_local"].lstrip("/")
    assert local.exists() and local.stat().st_size == size
    assert local.read_bytes()[:5] == b"%PDF-"
    assert hashlib.sha256(local.read_bytes()).hexdigest() == digest


census = rows(p / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V112.csv")
assert len(census) == 48
assert len({r["source_id"] for r in census}) == 48
assert set(new_sources) <= {r["source_id"] for r in census}
assert all(r["primary_source"] == "YES" and r["preserved"] == "YES" for r in census)
for row in census:
    local = repo / row["local_path"].lstrip("/")
    assert local.exists(), local
    assert local.stat().st_size == int(row["bytes"])
    assert hashlib.sha256(local.read_bytes()).hexdigest() == row["sha256"]


source_audit = repo / "research" / "ciclo_ajuste" / "source_audit"
hash_rows = rows(source_audit / "MASTER_LOCAL_HASH_VALIDATION_V112.csv")
assert len(hash_rows) == 246
assert sum(r["exists"] == "True" for r in hash_rows) == 241
assert sum(r["hash_ok"] == "True" for r in hash_rows) == 241
for source_id in new_sources:
    row = next(r for r in hash_rows if r["id"] == source_id)
    assert row["exists"] == "True" and row["hash_ok"] == "True"

completeness = json.loads((source_audit / "CURRENT_SOURCE_COMPLETENESS_V112.json").read_text(encoding="utf-8"))
assert completeness["master_catalog_entries"] == 246
assert completeness["physical_local_copies"] == 241
assert completeness["physical_local_hash_ok"] == 241
assert completeness["e0_primary_sources_preserved"] == 48
assert completeness["e0_quality"] == "PRIMARY_FISCAL_SERVICE_BRIDGE_EXTENDED_2001_2012"
assert completeness["e0_boden_2007_matured"] is True
assert completeness["e0_boden_2012_matured"] is True
assert completeness["e0_fiscal_final_cash_total_identified"] is False
assert completeness["e0_series_service_purpose_allocated"] is False
assert completeness["e0_holder_register_complete"] is False
assert completeness["e0_agn_holder_controls_partial"] is True
assert completeness["e0_causal_net_incidence_identified"] is False

missing = rows(source_audit / "SOURCE_PRESERVATION_MISSING_V112.csv")
assert len(missing) == 8
assert not any(r["priority"] == "P0" for r in missing)
assert sum(r["priority"] == "P1" for r in missing) == 1
assert sum(r["priority"] == "DISCOVERY" for r in missing) == 7


ledger = rows(p / "E0_FISCAL_MECHANISM_LEDGER_V112.csv")
assert len(ledger) == 88
assert {r["ledger_id"] for r in ledger} == {f"F{i:02d}" for i in range(1, 89)}
L = {r["ledger_id"]: r for r in ledger}
assert Decimal(L["F59"]["amount_original"]) == Decimal("356805700")
assert Decimal(L["F60"]["amount_original"]) == Decimal("2208223712.50")
assert Decimal(L["F61"]["amount_original"]) == Decimal("-39.9")
assert Decimal(L["F62"]["amount_original"]) == Decimal("-3.3")
assert Decimal(L["F63"]["amount_original"]) == Decimal("110.2")
assert Decimal(L["F64"]["normalized_ars_million"]) == Decimal("9102.996")
assert Decimal(L["F65"]["normalized_ars_million"]) == Decimal("7031.799")
assert Decimal(L["F66"]["normalized_ars_million"]) == Decimal("12625.525")
assert Decimal(L["F67"]["amount_original"]) == Decimal("10898.291")
assert Decimal(L["F69"]["amount_original"]) == Decimal("-6.6")
assert Decimal(L["F71"]["amount_original"]) == Decimal("-0.0179")
assert Decimal(L["F72"]["amount_original"]) == Decimal("1.9")
assert Decimal(L["F73"]["normalized_ars_million"]) == Decimal("1374")
assert Decimal(L["F74"]["normalized_ars_million"]) == Decimal("1128")
assert Decimal(L["F76"]["amount_original"]) == Decimal("-25")
assert Decimal(L["F77"]["amount_original"]) == Decimal("61")
assert Decimal(L["F81"]["amount_original"]) == Decimal("2197791900")
assert Decimal(L["F82"]["amount_original"]) == Decimal("276157")
assert Decimal(L["F83"]["amount_original"]) == Decimal("60")
assert Decimal(L["F88"]["amount_original"]) == Decimal("0")
assert all("CASH_PAID" not in r["realization_status"] for r in ledger)
assert all(L[k]["additivity"] == "EXCLUDE_FROM_BANK_COMPENSATION_TOTAL" for k in ("F59", "F60", "F68", "F75", "F79", "F80", "F81"))


transactions = rows(p / "E0_FISCAL_TRANSACTION_LEDGER_2007_2012_V112.csv")
assert len(transactions) == 30
assert {r["transaction_id"] for r in transactions} == {f"T{i:02d}" for i in range(59, 89)}
assert all(r["bank_compensation_aggregation"] == "NO_AUTOMATIC_AGGREGATION" for r in transactions)


service = rows(p / "E0_FISCAL_BODEN_SERVICE_BRIDGE_2007_2012_V112.csv")
assert len(service) == 7
assert all(r["flow_equation_check"] == "TRUE" for r in service)
assert all(r["purpose_allocation"] == "NOT_AVAILABLE_AT_SERIES_SERVICE_LEVEL" for r in service)
D = {r["service_id"]: r for r in service}
assert Decimal(D["D01"]["closing_original_unit"]) == 0
assert Decimal(D["D07"]["closing_original_unit"]) == 0
assert Decimal(D["D03"]["opening_adjustment_vs_prior_close"]) == Decimal("-4168625")
assert Decimal(D["D04"]["opening_adjustment_vs_prior_close"]) == Decimal("-12289800")
assert Decimal(D["D05"]["opening_adjustment_vs_prior_close"]) == Decimal("-2717812.5")
b2012 = [r for r in service if r["series"] == "BODEN_2012"]
assert sum(Decimal(r["principal_reduction_original_unit"]) for r in b2012) / Decimal(1_000_000) == Decimal("13285.8062125")
assert sum(Decimal(r["principal_accounting_ars"]) for r in b2012) / Decimal(1_000_000) == Decimal("52253.64973061")
assert sum(Decimal(r["interest_accounting_ars"]) for r in b2012) / Decimal(1_000_000) == Decimal("4970.64200805")


stock = rows(p / "E0_FISCAL_BODEN_STOCK_BRIDGE_2007_2012_V112.csv")
assert len(stock) == 11
K = {r["stock_id"]: r for r in stock}
assert Decimal(K["K06"]["updated_vno_million_usd"]) == Decimal("10898.291")
assert Decimal(K["K06"]["updated_value_million_ars"]) == Decimal("34318.720")
assert Decimal(K["K11"]["updated_vno_million_usd"]) == 0
assert Decimal(K["K01"]["updated_vno_million_usd"]) + Decimal(K["K02"]["updated_vno_million_usd"]) + Decimal(K["K03"]["updated_vno_million_usd"]) + Decimal(K["K04"]["updated_vno_million_usd"]) + Decimal(K["K05"]["updated_vno_million_usd"]) == Decimal(K["K06"]["updated_vno_million_usd"])


breaks = rows(p / "E0_FISCAL_METHOD_BREAKS_V112.csv")
assert len(breaks) == 37
assert all(r["status"] == "FROZEN" for r in breaks)
assert {r["break_id"] for r in breaks} >= {
    "annual_series_service_not_purpose",
    "modified_opening_requires_bridge",
    "mixed_buyback_not_series_allocable",
    "maturity_zero_not_holder_reconciliation",
    "agn_aggregate_holder_not_boden",
    "fgs_duplicate_not_treasury_flow",
}


evidence = rows(p / "HISTORICAL_EVIDENCE_COVERAGE_V112.csv")
fiscal = next(r for r in evidence if r["episode"] == "E0_2001_2003" and r["variable_family"] == "state_bcra")
assert fiscal["quality"] == "PRIMARY_FISCAL_SERVICE_BRIDGE_EXTENDED_2001_2012"
assert fiscal["comparable"] == "SERIES_SERVICE_RECONCILED_PURPOSE_HOLDER_ALLOCATION_OPEN"

queue = rows(p / "HISTORICAL_SOURCE_QUEUE_V112.csv")
assert any(r["episode"] == "E0_2001_2003" and r["variable_family"] == "state_bcra" and r["status"] == "BODEN_2007_2012_SERIES_MATURITY_RECONCILED_HOLDER_PURPOSE_OPEN" for r in queue)

historical = rows(p / "HISTORICAL_EPISODE_MATRIX_2001_2026_V112.csv")
assert {r["episode_id"] for r in historical} == {"E0", "E1", "E2", "E3", "E4", "E5", "E6"}
e0 = [r for r in historical if r["episode_id"] == "E0"]
assert len(e0) == 29
assert any(r["variable"] == "boden_2012_series_principal_service" and r["status"] == "SERIES_MATURITY_RECONCILED" for r in e0)
assert any(r["variable"] == "post_2006_purpose_adjustments" and r["status"] == "PURPOSE_ADJUSTMENTS_IDENTIFIED" for r in e0)
assert any(r["variable"] == "holder_controls" and r["status"] == "INDEPENDENT_HOLDER_CONTROLS_PARTIAL" for r in e0)
assert not any(r["status"] == "CAUSAL" for r in historical)


manifest = json.loads((p / "MANIFEST_V112.json").read_text(encoding="utf-8"))
assert manifest["checkpoint"] == "V112" and manifest["parent_checkpoint"] == "V111"
assert manifest["exact_entities"] == 30
assert manifest["e0_primary_sources"] == 48
assert manifest["new_official_sources"] == 8
assert manifest["fiscal_ledger_rows"] == 88
assert manifest["fiscal_transaction_rows_2007_2012"] == 30
assert manifest["fiscal_service_bridge_rows"] == 7
assert manifest["fiscal_stock_bridge_rows_2007_2012"] == 11
assert manifest["fiscal_method_breaks"] == 37
for item in manifest["files"]:
    local = p / item["path"]
    assert local.exists(), local
    assert local.stat().st_size == item["bytes"]
    assert hashlib.sha256(local.read_bytes()).hexdigest() == item["sha256"]

global_manifest = json.loads((repo / "research" / "ciclo_ajuste" / "MANIFEST_SHA256.json").read_text(encoding="utf-8"))
assert global_manifest["checkpoint"] == "V112"
assert global_manifest["exact_entities"] == 30
assert global_manifest["closed_network_gate"] == "NO"
assert global_manifest["file_count_excluding_manifest"] == len(global_manifest["files"])
for item in global_manifest["files"]:
    local = repo / item["path"]
    assert local.exists(), local
    assert local.stat().st_size == item["bytes"]
    assert hashlib.sha256(local.read_bytes()).hexdigest() == item["sha256"]

print("V112 QA PASS")
