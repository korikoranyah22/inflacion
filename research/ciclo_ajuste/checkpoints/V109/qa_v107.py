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
    "README_V107.md",
    "AUDITORIA_V107.md",
    "VEREDICTO_V107.md",
    "SOURCE_REFERENCES_V107.md",
    "CURRENT_STATE_V107.csv",
    "FOUR_LEG_PASS_PANEL_V107.csv",
    "STRICT_Q4_FOUR_LEG_COVERAGE_V107.csv",
    "RECOVERY_QUEUE_V107.csv",
    "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V107.csv",
    "E0_LEGAL_MECHANISM_TIMELINE_V107.csv",
    "E0_PRIMARY_SOURCE_MAP_V107.md",
    "HISTORICAL_EPISODE_MATRIX_2001_2026_V107.csv",
    "HISTORICAL_EVIDENCE_COVERAGE_V107.csv",
    "HISTORICAL_SOURCE_QUEUE_V107.csv",
    "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V107_A_V108.md",
    "MANIFEST_V107.json",
]
for name in required:
    assert (p / name).exists(), name

# Frozen V106 microbank arithmetic.
coverage = rows(p / "STRICT_Q4_FOUR_LEG_COVERAGE_V107.csv")[0]
expected_numerator = Decimal("59812903.504")
expected_denominator = Decimal("96697695.5")
expected_pct = Decimal("61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549")
assert Decimal(coverage["asset_numerator_million_ars"]) == expected_numerator
assert Decimal(coverage["system_assets_million_ars"]) == expected_denominator
assert Decimal(coverage["asset_coverage_pct"]) == expected_pct
assert abs(expected_numerator / expected_denominator * Decimal(100) - expected_pct) < Decimal("1e-98")
assert coverage["closed_network_gate"] == "NO_MAJORITY_COVERAGE_BUT_NETWORK_STILL_OPEN"

state = rows(p / "CURRENT_STATE_V107.csv")
assert len([r for r in state if r["strict_panel_status"] == "ELIGIBLE"]) == 30
rioja = next(r for r in state if r["entity"] == "Banco Rioja S.A.U.")
assert "MISMATCH" in rioja["q4_four_leg_status"]

# Master source inventory after ten new official originals.
catalog = rows(repo / "data" / "fuentes" / "FUENTES.csv")
assert len(catalog) == 215
catalog_by_id = {r["id"]: r for r in catalog}

census = rows(p / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V107.csv")
assert len(census) == 17
assert len({r["source_id"] for r in census}) == 17
assert all(r["primary_source"] == "YES" and r["preserved"] == "YES" for r in census)
for row in census:
    assert row["source_id"] in catalog_by_id
    local = repo / row["local_path"].lstrip("/")
    assert local.exists(), local
    assert local.stat().st_size == int(row["bytes"])
    assert hashlib.sha256(local.read_bytes()).hexdigest() == row["sha256"]
    source = catalog_by_id[row["source_id"]]
    assert source["archivo_local"] == row["local_path"]
    assert source["sha256"] == row["sha256"]

new_ids = {r["source_id"] for r in census if r["source_id"].startswith("e0_")}
assert len(new_ids) == 10
for source_id in new_ids:
    source = catalog_by_id[source_id]
    local = repo / source["archivo_local"].lstrip("/")
    head = local.read_bytes()[:32].lower()
    if local.suffix.lower() == ".pdf":
        assert head.startswith(b"%pdf-")
    else:
        assert b"html" in head or head.startswith(b"<!doctype")
    assert source["fecha_descarga"] == "2026-08-29"

source_audit = repo / "research" / "ciclo_ajuste" / "source_audit"
hash_rows = rows(source_audit / "MASTER_LOCAL_HASH_VALIDATION_V107.csv")
assert len(hash_rows) == 215
assert sum(r["exists"] == "True" for r in hash_rows) == 210
assert sum(r["hash_ok"] == "True" for r in hash_rows) == 210
for source_id in new_ids:
    audit = next(r for r in hash_rows if r["id"] == source_id)
    assert audit["exists"] == "True" and audit["hash_ok"] == "True"

completeness = json.loads((source_audit / "CURRENT_SOURCE_COMPLETENESS_V107.json").read_text(encoding="utf-8"))
assert completeness["master_catalog_entries"] == 215
assert completeness["physical_local_copies"] == 210
assert completeness["physical_local_hash_ok"] == 210
assert completeness["e0_primary_sources_preserved"] == 17
assert completeness["e0_quality"] == "PRIMARY_MAP_PARTIAL"
assert completeness["e0_causal_net_incidence_identified"] is False

missing = rows(source_audit / "SOURCE_PRESERVATION_MISSING_V107.csv")
assert len(missing) == 8
assert not any(r["priority"] == "P0" for r in missing)
assert sum(r["priority"] == "P1" for r in missing) == 1
assert sum(r["priority"] == "DISCOVERY" for r in missing) == 7

# E0 evidence gate and mechanism discipline.
timeline = rows(p / "E0_LEGAL_MECHANISM_TIMELINE_V107.csv")
assert len(timeline) == 6
assert {r["instrument"] for r in timeline} == {
    "Decreto 1570/2001",
    "Ley 25561",
    "Decreto 214/2002",
    "Decreto 471/2002",
    "Decreto 905/2002",
    "Ley 25796",
}
assert all(r["net_incidence_status"] == "NOT_IDENTIFIED" for r in timeline)
assert all(r["gross_amount_status"] in {"NOT_QUANTIFIED", "NOT_RECONCILED"} for r in timeline)

evidence = rows(p / "HISTORICAL_EVIDENCE_COVERAGE_V107.csv")
e0_evidence = [r for r in evidence if r["episode"] == "E0_2001_2003"]
assert len(e0_evidence) == 6
assert {r["variable_family"] for r in e0_evidence} == {"shock", "households", "credit", "risk", "banks", "state_bcra"}
assert all(r["quality"] == "PRIMARY_PARTIAL" for r in e0_evidence)
assert all(r["primary_source_present"] == "YES" and r["physical_source_preserved"] == "YES" for r in e0_evidence)
assert all(r["comparable"] == "PARTIAL" for r in e0_evidence)

historical = rows(p / "HISTORICAL_EPISODE_MATRIX_2001_2026_V107.csv")
assert {r["episode_id"] for r in historical} == {"E0", "E1", "E2", "E3", "E4", "E5", "E6"}
e0 = [r for r in historical if r["episode_id"] == "E0"]
assert len(e0) == 5
assert any(r["status"] == "PRIMARY_MAP_PARTIAL" for r in e0)
assert any(r["variable"] == "real_system_deposits" and r["trough_value"] == "-42%" for r in e0)
assert any(r["variable"] == "real_consolidated_net_worth" and r["trough_value"] == "-37%" for r in e0)
assert any(r["variable"] == "compensation_instruments" and r["status"] == "LEGAL_MAP_ONLY" for r in e0)
assert not any(r["status"] == "CAUSAL" for r in historical)

queue = rows(p / "HISTORICAL_SOURCE_QUEUE_V107.csv")
assert any(r["episode"] == "E0_2001_2003" and r["status"] == "LEGAL_MAP_BUILT_AMOUNT_OPEN" for r in queue)
assert any(r["episode"] == "E0_2001_2003" and r["status"] == "OPEN_SOCIAL_GAP" for r in queue)

# Checkpoint-local manifest excludes itself and must match every listed byte.
manifest = json.loads((p / "MANIFEST_V107.json").read_text(encoding="utf-8"))
assert manifest["checkpoint"] == "V107" and manifest["parent_checkpoint"] == "V106"
assert manifest["exact_entities"] == 30
assert manifest["e0_primary_sources"] == 17
assert manifest["new_official_sources"] == 10
for item in manifest["files"]:
    local = p / item["path"]
    assert local.exists(), local
    assert local.stat().st_size == item["bytes"]
    assert hashlib.sha256(local.read_bytes()).hexdigest() == item["sha256"]

print("V107 QA PASS")
