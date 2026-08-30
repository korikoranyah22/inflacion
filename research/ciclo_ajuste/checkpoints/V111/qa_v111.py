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
    "README_V111.md",
    "AUDITORIA_V111.md",
    "VEREDICTO_V111.md",
    "SOURCE_REFERENCES_V111.md",
    "CURRENT_STATE_V111.csv",
    "FOUR_LEG_PASS_PANEL_V111.csv",
    "STRICT_Q4_FOUR_LEG_COVERAGE_V111.csv",
    "RECOVERY_QUEUE_V111.csv",
    "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V111.csv",
    "E0_FISCAL_RECONSTRUCTION_V111.md",
    "E0_FISCAL_MECHANISM_LEDGER_V111.csv",
    "E0_FISCAL_TRANSACTION_LEDGER_2004_2006_V111.csv",
    "E0_FISCAL_STOCK_FLOW_BRIDGE_V111.csv",
    "E0_FISCAL_METHOD_BREAKS_V111.csv",
    "HISTORICAL_EPISODE_MATRIX_2001_2026_V111.csv",
    "HISTORICAL_EVIDENCE_COVERAGE_V111.csv",
    "HISTORICAL_SOURCE_QUEUE_V111.csv",
    "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V111_A_V112.md",
    "INHERITED_QA_STATUS_V111.csv",
    "build_e0_fiscal_v111.py",
    "MANIFEST_V111.json",
]
for name in required:
    assert (p / name).exists(), name

inherited = rows(p / "INHERITED_QA_STATUS_V111.csv")
assert any(r["script"] == "qa_v110.py" and r["post_v111_result"] == "EXPECTED_SUPERSEDED_ASSERTION" for r in inherited)
assert any(r["script"] == "qa_v111.py" and r["post_v111_result"] == "PASS" for r in inherited)


coverage = rows(p / "STRICT_Q4_FOUR_LEG_COVERAGE_V111.csv")[0]
expected_numerator = Decimal("59812903.504")
expected_denominator = Decimal("96697695.5")
expected_pct = Decimal("61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549")
assert Decimal(coverage["asset_numerator_million_ars"]) == expected_numerator
assert Decimal(coverage["system_assets_million_ars"]) == expected_denominator
assert Decimal(coverage["asset_coverage_pct"]) == expected_pct
assert abs(expected_numerator / expected_denominator * Decimal(100) - expected_pct) < Decimal("1e-98")
assert coverage["closed_network_gate"] == "NO_MAJORITY_COVERAGE_BUT_NETWORK_STILL_OPEN"
state = rows(p / "CURRENT_STATE_V111.csv")
assert len([r for r in state if r["strict_panel_status"] == "ELIGIBLE"]) == 30
rioja = next(r for r in state if r["entity"] == "Banco Rioja S.A.U.")
assert "MISMATCH" in rioja["q4_four_leg_status"]


new_sources = {
    "e0_cgn_cuenta_inversion_2004_sdp": (900875, "a076e0fbcc6f620f542dd5d1e96f5ba07831897a3c44da71867f355aed57811e"),
    "e0_cgn_cuenta_inversion_2004_tomo_i": (1871030, "35c2db9e9bb4ba02fc6133c73af1f6fe683a7d99170e66f9737636cb6f420ec3"),
    "e0_cgn_cuenta_inversion_2005_sdp": (1034530, "96b849dde2a9ac83f6fd65e5700bae74e12ac4f4d3b558c368cf2005203a7e56"),
    "e0_cgn_cuenta_inversion_2005_tomo_i": (3189485, "15785a47c6846bf93c1089c72c8ac888e1adbbf5814ba757ecbf59b64380e498"),
    "e0_cgn_cuenta_inversion_2006_sdp": (660227, "677b1fa51056bbc7b5f6cd420e3de123b5c93b968e0a8f33bf87a6ab620331a7"),
    "e0_cgn_cuenta_inversion_2006_tomo_i": (2011257, "ad7029b9f40d0847f2221266df441fea2a5da0933400bb233bed38e245ae7ebb"),
    "e0_onp_sintesis_ejecutiva_2004q4": (381932, "b4ec8c5cc12af639d413aaa0266d0a8a182ae1b77996b20dc855b32d5beda2d0"),
    "e0_onp_sintesis_ejecutiva_2005q4": (140275, "ef5b60a4ea7641b9ec15eb99d50bca3254fa2e36ae555675dd2ce8e4640614ea"),
    "e0_onp_sintesis_ejecutiva_2006q4": (328149, "79bb73538be3a545f3bb00f4e67c2f2f3cf6091e7173a6f4eca8a7e8d8c93890"),
}
catalog = rows(repo / "data" / "fuentes" / "FUENTES.csv")
assert len(catalog) == 238
catalog_by_id = {r["id"]: r for r in catalog}
for source_id, (size, digest) in new_sources.items():
    source = catalog_by_id[source_id]
    assert source["fecha_descarga"] == "2026-08-29"
    assert source["sha256"] == digest
    local = repo / source["archivo_local"].lstrip("/")
    assert local.exists() and local.stat().st_size == size
    assert local.read_bytes()[:5] == b"%PDF-"
    assert hashlib.sha256(local.read_bytes()).hexdigest() == digest


census = rows(p / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V111.csv")
assert len(census) == 40
assert len({r["source_id"] for r in census}) == 40
assert set(new_sources) <= {r["source_id"] for r in census}
assert all(r["primary_source"] == "YES" and r["preserved"] == "YES" for r in census)
for row in census:
    local = repo / row["local_path"].lstrip("/")
    assert local.exists(), local
    assert local.stat().st_size == int(row["bytes"])
    assert hashlib.sha256(local.read_bytes()).hexdigest() == row["sha256"]


source_audit = repo / "research" / "ciclo_ajuste" / "source_audit"
hash_rows = rows(source_audit / "MASTER_LOCAL_HASH_VALIDATION_V111.csv")
assert len(hash_rows) == 238
assert sum(r["exists"] == "True" for r in hash_rows) == 233
assert sum(r["hash_ok"] == "True" for r in hash_rows) == 233
for source_id in new_sources:
    row = next(r for r in hash_rows if r["id"] == source_id)
    assert row["exists"] == "True" and row["hash_ok"] == "True"

completeness = json.loads((source_audit / "CURRENT_SOURCE_COMPLETENESS_V111.json").read_text(encoding="utf-8"))
assert completeness["master_catalog_entries"] == 238
assert completeness["physical_local_copies"] == 233
assert completeness["physical_local_hash_ok"] == 233
assert completeness["e0_primary_sources_preserved"] == 40
assert completeness["e0_quality"] == "PRIMARY_FISCAL_LEDGER_EXTENDED_2001_2006"
assert completeness["e0_fiscal_final_cash_total_identified"] is False
assert completeness["e0_post_2003_execution_identified"] is True
assert completeness["e0_series_service_purpose_allocated"] is False
assert completeness["e0_causal_net_incidence_identified"] is False

missing = rows(source_audit / "SOURCE_PRESERVATION_MISSING_V111.csv")
assert len(missing) == 8
assert not any(r["priority"] == "P0" for r in missing)
assert sum(r["priority"] == "P1" for r in missing) == 1
assert sum(r["priority"] == "DISCOVERY" for r in missing) == 7


ledger = rows(p / "E0_FISCAL_MECHANISM_LEDGER_V111.csv")
assert len(ledger) == 58
assert {r["ledger_id"] for r in ledger} == {f"F{i:02d}" for i in range(1, 59)}
L = {r["ledger_id"]: r for r in ledger}
assert Decimal(L["F26"]["normalized_ars_million"]) == Decimal("16183.544262")
assert L["F26"]["realization_status"] == "PRIOR_2002_REGISTRATION_CONVALIDATED"
assert Decimal(L["F27"]["normalized_ars_million"]) == Decimal("17201.249")
assert Decimal(L["F28"]["normalized_ars_million"]) == Decimal("7039.723")
assert Decimal(L["F29"]["normalized_ars_million"]) == Decimal("19520.717")
assert Decimal(L["F30"]["normalized_ars_million"]) == Decimal("53070.390")
assert Decimal(L["F32"]["normalized_ars_million"]) == Decimal("77")
assert Decimal(L["F33"]["normalized_ars_million"]) == Decimal("2081")
assert Decimal(L["F34"]["amount_original"]) == Decimal("-35.8")
assert Decimal(L["F35"]["amount_original"]) == Decimal("2001")
assert Decimal(L["F40"]["normalized_ars_million"]) == Decimal("3300.29")
assert L["F40"]["realization_status"] == "ACCRUED_TRANSFER_NOT_CASH_PROOF"
assert Decimal(L["F44"]["normalized_ars_million"]) == Decimal("11.9")
assert Decimal(L["F45"]["normalized_ars_million"]) == Decimal("21.3")
assert Decimal(L["F46"]["amount_original"]) == Decimal("-32.4")
assert Decimal(L["F47"]["amount_original"]) == Decimal("1007")
assert Decimal(L["F48"]["normalized_ars_million"]) == Decimal("11960.610")
assert Decimal("11881.044") + Decimal("79.566") == Decimal(L["F48"]["normalized_ars_million"])
assert Decimal(L["F49"]["normalized_ars_million"]) == Decimal("9078.371")
assert Decimal(L["F50"]["normalized_ars_million"]) == Decimal("14841.964")
assert Decimal(L["F51"]["normalized_ars_million"]) == Decimal("1780.1")
assert L["F51"]["realization_status"] == "MIXED_BNA_AND_COMPENSATION_BUCKET"
assert Decimal(L["F53"]["normalized_ars_million"]) == Decimal("510.10")
assert Decimal(L["F55"]["normalized_ars_million"]) == Decimal("6935.20")
assert Decimal(L["F56"]["normalized_ars_million"]) == Decimal("1326.21")
assert all("CASH_PAID" not in r["realization_status"] for r in ledger)
assert all(L[k]["additivity"] == "EXCLUDE_FROM_BANK_COMPENSATION_TOTAL" for k in ("F55", "F56", "F57"))


transactions = rows(p / "E0_FISCAL_TRANSACTION_LEDGER_2004_2006_V111.csv")
assert len(transactions) == 33
assert {r["transaction_id"] for r in transactions} == {f"T{i:02d}" for i in range(26, 59)}
assert all(r["bank_compensation_aggregation"] == "NO_AUTOMATIC_AGGREGATION" for r in transactions)


bridge = rows(p / "E0_FISCAL_STOCK_FLOW_BRIDGE_V111.csv")
assert len(bridge) == 11
B = {r["bridge_id"]: r for r in bridge}
for row in bridge:
    assert Decimal(row["as_of_2004_12_31"]) - Decimal(row["as_of_2003_12_31"]) == Decimal(row["delta_2004"])
    assert Decimal(row["as_of_2005_12_31"]) - Decimal(row["as_of_2004_12_31"]) == Decimal(row["delta_2005"])
    assert Decimal(row["as_of_2006_12_31"]) - Decimal(row["as_of_2005_12_31"]) == Decimal(row["delta_2006"])
assert Decimal(B["S02"]["delta_2006"]) == Decimal("-3201.968")
assert Decimal(B["S03"]["delta_2006"]) == Decimal("1510.516")
assert Decimal(B["S05"]["as_of_2006_12_31"]) == Decimal("21038.981")


breaks = rows(p / "E0_FISCAL_METHOD_BREAKS_V111.csv")
assert len(breaks) == 28
assert all(r["status"] == "FROZEN" for r in breaks)
assert {r["break_id"] for r in breaks} >= {
    "budget_accrual_not_cash",
    "negative_net_issuance_is_correction",
    "series_service_mixed_purpose",
    "mixed_banks_depositors_bucket",
    "agn_specific_audit_gap_persists",
}


evidence = rows(p / "HISTORICAL_EVIDENCE_COVERAGE_V111.csv")
fiscal = next(r for r in evidence if r["episode"] == "E0_2001_2003" and r["variable_family"] == "state_bcra")
assert fiscal["quality"] == "PRIMARY_FISCAL_LEDGER_EXTENDED_2001_2006"
assert fiscal["comparable"] == "PURPOSE_AND_PHASE_SEPARATED_CASH_STILL_OPEN"

queue = rows(p / "HISTORICAL_SOURCE_QUEUE_V111.csv")
assert any(r["episode"] == "E0_2001_2003" and r["variable_family"] == "state_bcra" and r["status"] == "FISCAL_LEDGER_2004_2006_EXTENDED_SERVICE_ALLOCATION_AND_AUDIT_OPEN" for r in queue)

historical = rows(p / "HISTORICAL_EPISODE_MATRIX_2001_2026_V111.csv")
assert {r["episode_id"] for r in historical} == {"E0", "E1", "E2", "E3", "E4", "E5", "E6"}
e0 = [r for r in historical if r["episode_id"] == "E0"]
assert len(e0) == 26
assert any(r["variable"] == "fiscal_compensation_net_issuance" and r["status"] == "FISCAL_NET_ISSUANCE_IDENTIFIED" for r in e0)
assert any(r["variable"] == "bank_specific_budget_transfer_accrual" and r["pre_value"] == "3300.29m_ARS" for r in e0)
assert any(r["variable"] == "compensation_related_debt_stock" and r["trough_value"] == "21038.981m_ARS" for r in e0)
assert not any(r["status"] == "CAUSAL" for r in historical)


manifest = json.loads((p / "MANIFEST_V111.json").read_text(encoding="utf-8"))
assert manifest["checkpoint"] == "V111" and manifest["parent_checkpoint"] == "V110"
assert manifest["exact_entities"] == 30
assert manifest["e0_primary_sources"] == 40
assert manifest["new_official_sources"] == 9
assert manifest["fiscal_ledger_rows"] == 58
assert manifest["fiscal_transaction_rows_2004_2006"] == 33
assert manifest["fiscal_bridge_rows"] == 11
assert manifest["fiscal_method_breaks"] == 28
for item in manifest["files"]:
    local = p / item["path"]
    assert local.exists(), local
    assert local.stat().st_size == item["bytes"]
    assert hashlib.sha256(local.read_bytes()).hexdigest() == item["sha256"]

global_manifest = json.loads((repo / "research" / "ciclo_ajuste" / "MANIFEST_SHA256.json").read_text(encoding="utf-8"))
assert global_manifest["checkpoint"] == "V111"
assert global_manifest["exact_entities"] == 30
assert global_manifest["closed_network_gate"] == "NO"
assert global_manifest["file_count_excluding_manifest"] == len(global_manifest["files"])
for item in global_manifest["files"]:
    local = repo / item["path"]
    assert local.exists(), local
    assert local.stat().st_size == item["bytes"]
    assert hashlib.sha256(local.read_bytes()).hexdigest() == item["sha256"]

print("V111 QA PASS")
