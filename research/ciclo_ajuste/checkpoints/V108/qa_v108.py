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
    "README_V108.md",
    "AUDITORIA_V108.md",
    "VEREDICTO_V108.md",
    "SOURCE_REFERENCES_V108.md",
    "CURRENT_STATE_V108.csv",
    "FOUR_LEG_PASS_PANEL_V108.csv",
    "STRICT_Q4_FOUR_LEG_COVERAGE_V108.csv",
    "RECOVERY_QUEUE_V108.csv",
    "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V108.csv",
    "E0_SOCIAL_RECONSTRUCTION_V108.md",
    "E0_SOCIAL_CLOCKS_V108.csv",
    "E0_SOCIAL_RECOVERY_SUMMARY_V108.csv",
    "E0_SOCIAL_METHOD_BREAKS_V108.csv",
    "E0_REAL_RIPTE_MONTHLY_V108.csv",
    "build_e0_real_ripte_v108.ps1",
    "HISTORICAL_EPISODE_MATRIX_2001_2026_V108.csv",
    "HISTORICAL_EVIDENCE_COVERAGE_V108.csv",
    "HISTORICAL_SOURCE_QUEUE_V108.csv",
    "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V108_A_V109.md",
    "MANIFEST_V108.json",
]
for name in required:
    assert (p / name).exists(), name

# Frozen V106/V107 microbank arithmetic.
coverage = rows(p / "STRICT_Q4_FOUR_LEG_COVERAGE_V108.csv")[0]
expected_numerator = Decimal("59812903.504")
expected_denominator = Decimal("96697695.5")
expected_pct = Decimal("61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549")
assert Decimal(coverage["asset_numerator_million_ars"]) == expected_numerator
assert Decimal(coverage["system_assets_million_ars"]) == expected_denominator
assert Decimal(coverage["asset_coverage_pct"]) == expected_pct
assert abs(expected_numerator / expected_denominator * Decimal(100) - expected_pct) < Decimal("1e-98")
assert coverage["closed_network_gate"] == "NO_MAJORITY_COVERAGE_BUT_NETWORK_STILL_OPEN"

state = rows(p / "CURRENT_STATE_V108.csv")
assert len([r for r in state if r["strict_panel_status"] == "ELIGIBLE"]) == 30
rioja = next(r for r in state if r["entity"] == "Banco Rioja S.A.U.")
assert "MISMATCH" in rioja["q4_four_leg_status"]

# Master source inventory after ten new official social sources.
catalog = rows(repo / "data" / "fuentes" / "FUENTES.csv")
assert len(catalog) == 225
catalog_by_id = {r["id"]: r for r in catalog}

census = rows(p / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V108.csv")
assert len(census) == 27
assert len({r["source_id"] for r in census}) == 27
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

new_ids = {
    "e0_indec_eph_puntual_tasas_1974_2003",
    "e0_indec_eph_continua_tasas_2003_2007",
    "e0_indec_pobreza_puntual_2001_2003",
    "e0_indec_pobreza_continua_2003_2007",
    "e0_indec_pobreza_metodo_historico",
    "e0_indec_pobreza_metodologia_22_2016",
    "e0_indec_cgi_mano_obra_privada_1993_2007",
    "e0_argentina_ripte_page_2026_08_29",
    "e0_argentina_ripte_serie_junio_2026",
    "e0_indec_ipc_gba_empalme_1943_2008",
}
assert new_ids <= {r["source_id"] for r in census}
for source_id in new_ids:
    source = catalog_by_id[source_id]
    local = repo / source["archivo_local"].lstrip("/")
    head = local.read_bytes()[:32].lower()
    if local.suffix.lower() == ".pdf":
        assert head.startswith(b"%pdf-")
    elif local.suffix.lower() == ".html":
        assert b"html" in head or head.startswith(b"<!doctype")
    else:
        assert local.suffix.lower() == ".xls" and head.startswith(bytes.fromhex("d0cf11e0a1b11ae1"))
    assert source["fecha_descarga"] == "2026-08-29"

source_audit = repo / "research" / "ciclo_ajuste" / "source_audit"
hash_rows = rows(source_audit / "MASTER_LOCAL_HASH_VALIDATION_V108.csv")
assert len(hash_rows) == 225
assert sum(r["exists"] == "True" for r in hash_rows) == 220
assert sum(r["hash_ok"] == "True" for r in hash_rows) == 220
for source_id in new_ids:
    audit = next(r for r in hash_rows if r["id"] == source_id)
    assert audit["exists"] == "True" and audit["hash_ok"] == "True"

completeness = json.loads((source_audit / "CURRENT_SOURCE_COMPLETENESS_V108.json").read_text(encoding="utf-8"))
assert completeness["master_catalog_entries"] == 225
assert completeness["physical_local_copies"] == 220
assert completeness["physical_local_hash_ok"] == 220
assert completeness["e0_primary_sources_preserved"] == 27
assert completeness["e0_quality"] == "PRIMARY_SOCIAL_CLOCKS_PARTIAL"
assert completeness["e0_social_clock_rows"] == 51
assert completeness["e0_real_ripte_months"] == 66
assert completeness["e0_causal_net_incidence_identified"] is False

missing = rows(source_audit / "SOURCE_PRESERVATION_MISSING_V108.csv")
assert len(missing) == 8
assert not any(r["priority"] == "P0" for r in missing)
assert sum(r["priority"] == "P1" for r in missing) == 1
assert sum(r["priority"] == "DISCOVERY" for r in missing) == 7

# Social clocks and method regime discipline.
social = rows(p / "E0_SOCIAL_CLOCKS_V108.csv")
assert len(social) == 51
social_key = {(r["indicator"], r["period"], r["regime"]): Decimal(r["value"]) for r in social}
assert social_key[("employment_rate", "2002-05", "EPH_PUNCTUAL")] == Decimal("32.8")
assert social_key[("unemployment_rate", "2002-05", "EPH_PUNCTUAL")] == Decimal("21.5")
assert social_key[("poverty_persons", "2002-10", "EPH_PUNCTUAL_HISTORICAL_METHOD")] == Decimal("57.5")
assert social_key[("indigence_persons", "2003-05", "EPH_PUNCTUAL_HISTORICAL_METHOD")] == Decimal("26.3")
assert social_key[("poverty_persons", "2003-S2", "EPH_CONTINUOUS_HISTORICAL_METHOD")] == Decimal("47.8")

breaks = rows(p / "E0_SOCIAL_METHOD_BREAKS_V108.csv")
assert len(breaks) == 8
assert {r["impact"] for r in breaks} >= {"CRITICAL", "HIGH", "MEDIUM"}
assert any(r["break_id"] == "poverty_historical_to_2016" and r["impact"] == "CRITICAL" for r in breaks)
assert any(r["break_id"] == "ripte_population_scope" and r["impact"] == "CRITICAL" for r in breaks)

ripte = rows(p / "E0_REAL_RIPTE_MONTHLY_V108.csv")
assert len(ripte) == 66
ripte_by_period = {r["period"]: r for r in ripte}
assert Decimal(ripte_by_period["2001-12"]["real_ripte_dec2001_100"]) == Decimal("100.000000")
assert Decimal(ripte_by_period["2003-04"]["real_ripte_dec2001_100"]) == Decimal("70.730514")
assert Decimal(ripte_by_period["2003-12"]["real_ripte_dec2001_100"]) == Decimal("81.825643")
assert Decimal(ripte_by_period["2006-12"]["real_ripte_dec2001_100"]) == Decimal("100.476721")
assert Decimal(ripte_by_period["2006-12"]["real_ripte_nov2001_100"]) == Decimal("99.943539")
post_base_recoveries = [r for r in ripte if r["period"] > "2001-12" and Decimal(r["real_ripte_dec2001_100"]) >= 100]
assert [r["period"] for r in post_base_recoveries] == ["2006-12"]

recovery = rows(p / "E0_SOCIAL_RECOVERY_SUMMARY_V108.csv")
assert len(recovery) == 6
assert any(r["clock_id"] == "real_ripte_dec2001_base" and r["months_to_recovery"] == "60" for r in recovery)
assert any(r["clock_id"] == "real_ripte_nov2001_sensitivity" and r["recovery_status"] == "NOT_RECOVERED_BY_2006_12" for r in recovery)

evidence = rows(p / "HISTORICAL_EVIDENCE_COVERAGE_V108.csv")
e0_evidence = [r for r in evidence if r["episode"] == "E0_2001_2003"]
assert len(e0_evidence) == 6
households = next(r for r in e0_evidence if r["variable_family"] == "households")
assert households["quality"] == "PRIMARY_SOCIAL_CLOCKS_PARTIAL"
assert households["comparable"] == "WITHIN_REGIME_ONLY"

historical = rows(p / "HISTORICAL_EPISODE_MATRIX_2001_2026_V108.csv")
assert {r["episode_id"] for r in historical} == {"E0", "E1", "E2", "E3", "E4", "E5", "E6"}
e0 = [r for r in historical if r["episode_id"] == "E0"]
assert len(e0) == 12
assert any(r["variable"] == "real_RIPTE_stable_registered" and r["recovery_date"] == "2006-12" for r in e0)
assert any(r["variable"] == "poverty_persons" and r["status"] == "NOT_RECOVERED_BY_END" for r in e0)
assert not any(r["status"] == "CAUSAL" for r in historical)

queue = rows(p / "HISTORICAL_SOURCE_QUEUE_V108.csv")
assert any(r["episode"] == "E0_2001_2003" and r["status"] == "SOCIAL_CLOCKS_BUILT_SCOPE_GAPS_OPEN" for r in queue)

# Checkpoint-local manifest excludes itself and must match every listed byte.
manifest = json.loads((p / "MANIFEST_V108.json").read_text(encoding="utf-8"))
assert manifest["checkpoint"] == "V108" and manifest["parent_checkpoint"] == "V107"
assert manifest["exact_entities"] == 30
assert manifest["e0_primary_sources"] == 27
assert manifest["new_official_sources"] == 10
for item in manifest["files"]:
    local = p / item["path"]
    assert local.exists(), local
    assert local.stat().st_size == item["bytes"]
    assert hashlib.sha256(local.read_bytes()).hexdigest() == item["sha256"]

print("V108 QA PASS")
