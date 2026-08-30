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
    "README_V110.md",
    "AUDITORIA_V110.md",
    "VEREDICTO_V110.md",
    "SOURCE_REFERENCES_V110.md",
    "CURRENT_STATE_V110.csv",
    "FOUR_LEG_PASS_PANEL_V110.csv",
    "STRICT_Q4_FOUR_LEG_COVERAGE_V110.csv",
    "RECOVERY_QUEUE_V110.csv",
    "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V110.csv",
    "E0_FISCAL_RECONSTRUCTION_V110.md",
    "E0_FISCAL_MECHANISM_LEDGER_V110.csv",
    "E0_FISCAL_STOCK_FLOW_BRIDGE_V110.csv",
    "E0_FISCAL_METHOD_BREAKS_V110.csv",
    "HISTORICAL_EPISODE_MATRIX_2001_2026_V110.csv",
    "HISTORICAL_EVIDENCE_COVERAGE_V110.csv",
    "HISTORICAL_SOURCE_QUEUE_V110.csv",
    "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V110_A_V111.md",
    "INHERITED_QA_STATUS_V110.csv",
    "MANIFEST_V110.json",
]
for name in required:
    assert (p / name).exists(), name

# Frozen V106+ microbank arithmetic.
coverage = rows(p / "STRICT_Q4_FOUR_LEG_COVERAGE_V110.csv")[0]
expected_numerator = Decimal("59812903.504")
expected_denominator = Decimal("96697695.5")
expected_pct = Decimal("61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549")
assert Decimal(coverage["asset_numerator_million_ars"]) == expected_numerator
assert Decimal(coverage["system_assets_million_ars"]) == expected_denominator
assert Decimal(coverage["asset_coverage_pct"]) == expected_pct
assert abs(expected_numerator / expected_denominator * Decimal(100) - expected_pct) < Decimal("1e-98")
assert coverage["closed_network_gate"] == "NO_MAJORITY_COVERAGE_BUT_NETWORK_STILL_OPEN"
state = rows(p / "CURRENT_STATE_V110.csv")
assert len([r for r in state if r["strict_panel_status"] == "ELIGIBLE"]) == 30
rioja = next(r for r in state if r["entity"] == "Banco Rioja S.A.U.")
assert "MISMATCH" in rioja["q4_four_leg_status"]

# Source inventory and newly preserved primary PDFs.
catalog = rows(repo / "data" / "fuentes" / "FUENTES.csv")
assert len(catalog) == 229
catalog_by_id = {r["id"]: r for r in catalog}
new_sources = {
    "e0_cgn_cuenta_inversion_2002_tomo_i": (4215238, "f94a50a6681f367453a0b17c2846fae791b945a7fd311273aac85bddb8704529"),
    "e0_cgn_cuenta_inversion_2003_tomo_i": (1967195, "be739fa0f13a017c1a38c9f97f03fd3a724fdf300f9c1a3d07b46dafb7717f98"),
    "e0_onp_boletin_fiscal_2003q4_cuadro37_boden": (12714, "f75dc6555d8d5f5ace56e150d7cece3be8110049b727c296b94fa30b700a01eb"),
}
for source_id, (size, digest) in new_sources.items():
    source = catalog_by_id[source_id]
    assert source["fecha_descarga"] == "2026-08-29"
    assert source["sha256"] == digest
    local = repo / source["archivo_local"].lstrip("/")
    assert local.exists() and local.stat().st_size == size
    assert local.read_bytes()[:5] == b"%PDF-"
    assert hashlib.sha256(local.read_bytes()).hexdigest() == digest

census = rows(p / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V110.csv")
assert len(census) == 31
assert len({r["source_id"] for r in census}) == 31
assert all(r["primary_source"] == "YES" and r["preserved"] == "YES" for r in census)
assert set(new_sources) <= {r["source_id"] for r in census}
for row in census:
    assert row["source_id"] in catalog_by_id
    local = repo / row["local_path"].lstrip("/")
    assert local.exists(), local
    assert local.stat().st_size == int(row["bytes"])
    assert hashlib.sha256(local.read_bytes()).hexdigest() == row["sha256"]

source_audit = repo / "research" / "ciclo_ajuste" / "source_audit"
hash_rows = rows(source_audit / "MASTER_LOCAL_HASH_VALIDATION_V110.csv")
assert len(hash_rows) == 229
assert sum(r["exists"] == "True" for r in hash_rows) == 224
assert sum(r["hash_ok"] == "True" for r in hash_rows) == 224
for source_id in new_sources:
    row = next(r for r in hash_rows if r["id"] == source_id)
    assert row["exists"] == "True" and row["hash_ok"] == "True"

completeness = json.loads((source_audit / "CURRENT_SOURCE_COMPLETENESS_V110.json").read_text(encoding="utf-8"))
assert completeness["master_catalog_entries"] == 229
assert completeness["physical_local_copies"] == 224
assert completeness["physical_local_hash_ok"] == 224
assert completeness["e0_primary_sources_preserved"] == 31
assert completeness["e0_quality"] == "PRIMARY_FISCAL_LEDGER_PARTIAL"
assert completeness["e0_fiscal_final_cash_total_identified"] is False
assert completeness["e0_definitive_compensation_pending_at_2003_close"] is True
assert completeness["e0_causal_net_incidence_identified"] is False

missing = rows(source_audit / "SOURCE_PRESERVATION_MISSING_V110.csv")
assert len(missing) == 8
assert not any(r["priority"] == "P0" for r in missing)
assert sum(r["priority"] == "P1" for r in missing) == 1
assert sum(r["priority"] == "DISCOVERY" for r in missing) == 7

# Fiscal phase ledger.
ledger = rows(p / "E0_FISCAL_MECHANISM_LEDGER_V110.csv")
assert len(ledger) == 25
assert {r["ledger_id"] for r in ledger} == {f"F{i:02d}" for i in range(1, 26)}
L = {r["ledger_id"]: r for r in ledger}
assert Decimal(L["F03"]["normalized_ars_million"]) == Decimal("2800")
assert Decimal(L["F05"]["normalized_ars_million"]) == Decimal("22035.916")
assert Decimal(L["F06"]["normalized_ars_million"]) == Decimal("8120.833")
assert Decimal(L["F07"]["normalized_ars_million"]) == Decimal("18078.963")
assert Decimal(L["F08"]["normalized_ars_million"]) == Decimal("48235.713")
assert Decimal(L["F09"]["normalized_ars_million"]) == Decimal("16183.54426211")
assert Decimal(L["F10"]["normalized_ars_million"]) == Decimal("17348.345")
assert Decimal(L["F11"]["normalized_ars_million"]) == Decimal("6879.649")
assert Decimal(L["F12"]["normalized_ars_million"]) == Decimal("17664.377")
assert Decimal(L["F13"]["normalized_ars_million"]) == Decimal("7086.660")
assert Decimal(L["F14"]["normalized_ars_million"]) == Decimal("2546.266")
assert Decimal(L["F15"]["normalized_ars_million"]) == Decimal("51525.296")
assert Decimal(L["F16"]["normalized_ars_million"]) + Decimal(L["F17"]["normalized_ars_million"]) + Decimal(L["F18"]["normalized_ars_million"]) == Decimal("3923.73653360")
assert Decimal(L["F20"]["normalized_ars_million"]) == Decimal("14573")
assert L["F20"]["realization_status"] == "RECOGNIZED_RECEIVABLE_NOT_RECEIVED"
assert L["F24"]["realization_status"] == "FINAL_AMOUNT_PENDING_VALIDATION"
assert L["F25"]["realization_status"] == "NOT_A_COMPENSATION"
assert not any("CASH_PAID" in r["realization_status"] for r in ledger)
assert Decimal(L["F05"]["normalized_ars_million"]) + Decimal(L["F06"]["normalized_ars_million"]) + Decimal(L["F07"]["normalized_ars_million"]) - Decimal(L["F08"]["normalized_ars_million"]) == Decimal("-0.001")
assert sum(Decimal(L[k]["normalized_ars_million"]) for k in ("F10", "F11", "F12", "F13", "F14")) - Decimal(L["F15"]["normalized_ars_million"]) == Decimal("0.001")

bridge = rows(p / "E0_FISCAL_STOCK_FLOW_BRIDGE_V110.csv")
assert len(bridge) == 12
B = {r["bridge_id"]: r for r in bridge}
for row in bridge:
    assert Decimal(row["as_of_2003_12_31"]) - Decimal(row["as_of_2002_12_31"]) == Decimal(row["delta_2003_minus_2002"])
assert Decimal(B["B02"]["delta_2003_minus_2002"]) == Decimal("-4687.571")
assert Decimal(B["B03"]["delta_2003_minus_2002"]) == Decimal("-1241.184")
assert Decimal(B["B12"]["delta_2003_minus_2002"]) == Decimal("-5928.755")

breaks = rows(p / "E0_FISCAL_METHOD_BREAKS_V110.csv")
assert len(breaks) == 16
assert {r["break_id"] for r in breaks} >= {
    "authorization_not_realization",
    "issuance_not_cash",
    "receivable_not_received",
    "mixed_boden_origins",
    "final_validation_pending",
    "compensation_not_net_gain",
}
assert all(r["status"] == "FROZEN" for r in breaks)

evidence = rows(p / "HISTORICAL_EVIDENCE_COVERAGE_V110.csv")
fiscal = next(r for r in evidence if r["episode"] == "E0_2001_2003" and r["variable_family"] == "state_bcra")
assert fiscal["quality"] == "PRIMARY_FISCAL_LEDGER_PARTIAL"
assert fiscal["comparable"] == "PHASE_SEPARATED_NOT_CASH_COMPLETE"

queue = rows(p / "HISTORICAL_SOURCE_QUEUE_V110.csv")
assert any(r["episode"] == "E0_2001_2003" and r["variable_family"] == "state_bcra" and r["status"] == "FISCAL_LEDGER_BUILT_PAYMENT_AND_AUDIT_OPEN" for r in queue)

historical = rows(p / "HISTORICAL_EPISODE_MATRIX_2001_2026_V110.csv")
assert {r["episode_id"] for r in historical} == {"E0", "E1", "E2", "E3", "E4", "E5", "E6"}
e0 = [r for r in historical if r["episode_id"] == "E0"]
assert len(e0) == 23
assert any(r["variable"] == "compensatory_debt_stock_updated" and r["recovery_value"] == "17348.345m_ARS" for r in e0)
assert any(r["variable"] == "bank_compensation_receivable" and r["status"] == "FINAL_AMOUNT_PENDING_VALIDATION" for r in e0)
assert not any(r["status"] == "CAUSAL" for r in historical)

# Checkpoint-local manifest excludes itself and must match every listed byte.
manifest = json.loads((p / "MANIFEST_V110.json").read_text(encoding="utf-8"))
assert manifest["checkpoint"] == "V110" and manifest["parent_checkpoint"] == "V109"
assert manifest["exact_entities"] == 30
assert manifest["e0_primary_sources"] == 31
assert manifest["new_official_sources"] == 3
assert manifest["fiscal_ledger_rows"] == 25
assert manifest["fiscal_bridge_rows"] == 12
assert manifest["fiscal_method_breaks"] == 16
for item in manifest["files"]:
    local = p / item["path"]
    assert local.exists(), local
    assert local.stat().st_size == item["bytes"]
    assert hashlib.sha256(local.read_bytes()).hexdigest() == item["sha256"]

print("V110 QA PASS")
