from pathlib import Path
from decimal import Decimal, getcontext
import csv
import hashlib

p = Path(__file__).parent
repo = p.parents[3]
getcontext().prec = 120


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


required = [
    "README_V106.md",
    "AUDITORIA_V106.md",
    "VEREDICTO_V106.md",
    "CURRENT_STATE_V106.csv",
    "FOUR_LEG_PASS_PANEL_V106.csv",
    "STRICT_Q4_FOUR_LEG_COVERAGE_V106.csv",
    "RECOVERY_QUEUE_V106.csv",
    "P0_ISSUER_SOURCE_INGEST_V106.csv",
    "P0_SIX_ENTITY_Q4_FOUR_LEG_PROMOTION_V106.csv",
    "HISTORICAL_WORKSTREAM_BOOTSTRAP_V106.md",
    "HISTORICAL_EPISODE_MATRIX_2001_2026_V106.csv",
    "HISTORICAL_EVIDENCE_COVERAGE_V106.csv",
    "HISTORICAL_SOURCE_QUEUE_V106.csv",
    "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V106_A_V107.md",
    "MANIFEST_V106.json",
]
for name in required:
    assert (p / name).exists(), name

coverage = rows(p / "STRICT_Q4_FOUR_LEG_COVERAGE_V106.csv")[0]
expected_numerator = Decimal("59812903.504")
expected_denominator = Decimal("96697695.5")
expected_pct = Decimal("61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549")
assert Decimal(coverage["asset_numerator_million_ars"]) == expected_numerator
assert Decimal(coverage["system_assets_million_ars"]) == expected_denominator
assert Decimal(coverage["asset_coverage_pct"]) == expected_pct
recomputed_pct = expected_numerator / expected_denominator * Decimal(100)
assert abs(recomputed_pct - expected_pct) < Decimal("1e-98")
assert coverage["closed_network_gate"] == "NO_MAJORITY_COVERAGE_BUT_NETWORK_STILL_OPEN"

state = rows(p / "CURRENT_STATE_V106.csv")
eligible = [r for r in state if r["strict_panel_status"] == "ELIGIBLE"]
assert len(eligible) == 30
promoted_names = {
    "Banco Hipotecario S.A.",
    "Banco Columbia S.A.",
    "BACS Banco de Credito y Securitizacion S.A.",
    "Banco Municipal de Rosario",
    "Banco Provincia de Tierra del Fuego",
    "Banco VOII S.A.",
}
for name in promoted_names:
    row = next(r for r in state if r["entity"] == name)
    assert row["q4_four_leg_status"] == "EXACT"
    assert row["strict_panel_status"] == "ELIGIBLE"
    assert row["priority"] == "CLOSED_V106"
rioja = next(r for r in state if r["entity"] == "Banco Rioja S.A.U.")
assert "MISMATCH" in rioja["q4_four_leg_status"]

panel = rows(p / "FOUR_LEG_PASS_PANEL_V106.csv")
strict_panel = [r for r in panel if r["system_panel_eligible_v72"] == "YES_EXACT_Q4_TARGET_BASIS"]
assert len(strict_panel) == 30
assert promoted_names <= {r["entity"] for r in strict_panel}
voii = next(r for r in strict_panel if r["entity"] == "Banco VOII S.A.")
assert Decimal(voii["expense_otherfi"]) == Decimal("-2.848019436825984")

promotions = rows(p / "P0_SIX_ENTITY_Q4_FOUR_LEG_PROMOTION_V106.csv")
assert len(promotions) == 6
assert {r["entity"] for r in promotions} == promoted_names
assert sum(Decimal(r["dec2023_asset_million_ars"]) for r in promotions) == Decimal("2009345.992")
assert Decimal("57803557.512") + Decimal("2009345.992") == expected_numerator

ingest = rows(p / "P0_ISSUER_SOURCE_INGEST_V106.csv")
assert len(ingest) == 11
ingest_by_id = {r["source_id"]: r for r in ingest}
for row in ingest:
    path = repo / row["local_path"].lstrip("/")
    assert path.exists(), path
    assert path.stat().st_size == int(row["bytes"])
    with path.open("rb") as stream:
        assert stream.read(5) == b"%PDF-"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
    assert row["pdfinfo_ok"] == "YES"
    assert row["duplicate_catalog_hash_before_ingest"] == "NO_MATCH"

catalog = rows(repo / "data" / "fuentes" / "FUENTES.csv")
catalog_by_id = {r["id"]: r for r in catalog}
for source_id, ingest_row in ingest_by_id.items():
    source = catalog_by_id[source_id]
    assert source["archivo_local"] == ingest_row["local_path"]
    assert source["sha256"] == ingest_row["sha256"]
    assert source["fecha_descarga"] == "2026-08-29"
    assert "preservado" in source["tipo"]

source_audit = repo / "research" / "ciclo_ajuste" / "source_audit"
hash_rows = rows(source_audit / "MASTER_LOCAL_HASH_VALIDATION_V106.csv")
assert len(hash_rows) == 205
assert sum(r["exists"] == "True" for r in hash_rows) == 200
assert sum(r["hash_ok"] == "True" for r in hash_rows) == 200
for source_id, ingest_row in ingest_by_id.items():
    audit = next(r for r in hash_rows if r["id"] == source_id)
    assert audit["exists"] == "True" and audit["hash_ok"] == "True"
    assert audit["sha_actual"] == ingest_row["sha256"]

missing = rows(source_audit / "SOURCE_PRESERVATION_MISSING_V106.csv")
assert len(missing) == 8
assert not any(r["priority"] == "P0" for r in missing)
assert sum(r["priority"] == "P1" for r in missing) == 1

targets = rows(p / "CNV_EXACT_PRESENTATION_TARGETS_V105.csv")
assert {r["presentation_id"] for r in targets} == {"3122483", "3165651", "3121099", "3163537", "3119515", "3171909"}
assert "3177414" not in {r["presentation_id"] for r in targets}

historical = rows(p / "HISTORICAL_EPISODE_MATRIX_2001_2026_V106.csv")
assert {r["episode_id"] for r in historical} == {"E0", "E1", "E2", "E3", "E4", "E5", "E6"}
e0 = next(r for r in historical if r["episode_id"] == "E0")
assert e0["status"] == "NOT_ENOUGH_EVIDENCE"
e1 = next(r for r in historical if r["episode_id"] == "E1")
assert e1["shock_type"] == "GLOBAL_FINANCIAL_SHOCK" and e1["status"] == "FALSIFIER"
e5 = next(r for r in historical if r["episode_id"] == "E5")
assert e5["shock_type"] == "HEALTH_EXCEPTION" and e5["status"] == "SPECIAL_REGIME"
e4_mora = next(r for r in historical if r["episode_id"] == "E4" and r["variable"] == "mora_first_sustained")
assert e4_mora["status"] == "FAILS_ONSET" and e4_mora["months_to_trough"] == "-4"
assert not any(r["status"] == "CAUSAL" for r in historical)

print("V106 QA PASS")
