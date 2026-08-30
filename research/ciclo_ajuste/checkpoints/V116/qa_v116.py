from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import csv
import hashlib
import json

from pypdf import PdfReader


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v116" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


source_ids = {
    "e0_mecon_strip_boden2012_call_2009_06_10",
    "e0_mecon_strip_boden2012_result_2009_06_12",
    "e0_bcra_inflation_report_q4_2008_buyback_control",
}


catalog = read_csv(REPO / "data" / "fuentes" / "FUENTES.csv")
assert len(catalog) == 272, len(catalog)
assert len({row["id"] for row in catalog}) == len(catalog)
catalog_by_id = {row["id"]: row for row in catalog}
assert source_ids <= catalog_by_id.keys()


census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V116.csv")
assert len(census) == 73, len(census)
assert len({row["source_id"] for row in census}) == len(census)
assert source_ids <= {row["source_id"] for row in census}
for source_id in source_ids:
    source = catalog_by_id[source_id]
    local = REPO / source["archivo_local"].lstrip("/")
    assert local.is_file(), local
    assert digest(local) == source["sha256"]
    census_row = next(row for row in census if row["source_id"] == source_id)
    assert census_row["primary_source"] == "YES" and census_row["preserved"] == "YES"
    assert census_row["sha256"] == source["sha256"]


expected_pages = {
    "mecon_strip_boden2012_llamado_2009-06-10_wayback.pdf": 2,
    "mecon_strip_boden2012_resultado_2009-06-12_wayback.pdf": 3,
    "bcra_informe_inflacion_4t_2008.pdf": 80,
}
assert {path.name for path in BIN.glob("*.pdf")} == set(expected_pages)
for name, pages in expected_pages.items():
    pdf = BIN / name
    assert pdf.read_bytes().startswith(b"%PDF"), pdf
    assert len(PdfReader(str(pdf)).pages) == pages, pdf
assert not (REPO / "tmp" / "pdfs" / "v116_wayback").exists()


provenance = read_csv(HERE / "ARCHIVAL_PROVENANCE_V116.csv")
assert len(provenance) == 3
assert {row["source_id"] for row in provenance} == source_ids
wayback = [row for row in provenance if row["capture_timestamp"]]
assert len(wayback) == 2
assert {row["capture_timestamp"] for row in wayback} == {"20090619202926", "20090619203017"}
assert all(row["cdx_digest"] and row["retrieval_url"].startswith("https://web.archive.org/") for row in wayback)


offers = read_csv(HERE / "E0_FISCAL_STRIP_BUYBACK_OFFERS_2009_V116.csv")
assert len(offers) == 35
assert [int(row["offer_number"]) for row in offers] == list(range(1, 36))
accepted = [row for row in offers if row["accepted"] == "YES"]
rejected = [row for row in offers if row["accepted"] == "NO"]
assert len(accepted) == 20 and len(rejected) == 15
assert all(Decimal(row["price_per_100_usd"]) <= Decimal("12.70") for row in accepted)
assert all(Decimal(row["price_per_100_usd"]) > Decimal("12.70") for row in rejected)
assert sum(Decimal(row["underlying_boden2012_vno_usd"]) for row in offers) == Decimal("348994100")
assert sum(Decimal(row["effective_coupon_value_usd"]) for row in offers) == Decimal("44367798.74")
assert sum(Decimal(row["underlying_boden2012_vno_usd"]) for row in accepted) == Decimal("265707100")
assert sum(Decimal(row["effective_coupon_value_usd"]) for row in accepted) == Decimal("33691889.24")
assert all(row["settlement_confirmation"] == "SCHEDULED_NOT_INDEPENDENTLY_CONFIRMED" for row in offers)
assert all(row["ultimate_holder_identified"] == "NO" for row in offers)


awards = read_csv(HERE / "E0_FISCAL_STRIP_BUYBACK_AWARDS_2009_V116.csv")
assert len(awards) == 7
assert sum(int(row["accepted_offer_count"]) for row in awards) == 20
assert sum(Decimal(row["underlying_boden2012_vno_usd"]) for row in awards) == Decimal("265707100")
assert sum(Decimal(row["effective_coupon_value_usd"]) for row in awards) == Decimal("33691889.24")
assert {row["participant"] for row in awards} == {
    "Citibank", "Standard Bank", "BBVA Banco Francés", "MERVAL", "Nuevo Banco Bisel S.A.", "Banco de Galicia", "Banco Morgan"
}


summary = read_csv(HERE / "E0_FISCAL_STRIP_BUYBACK_SUMMARY_2009_V116.csv")
assert len(summary) == 1
strip = summary[0]
assert strip["isin"] == "ARARGE03G415"
assert strip["offers_received"] == "35" and strip["offers_accepted"] == "20"
assert strip["offered_effective_usd"] == "44367798.74"
assert strip["awarded_effective_usd"] == "33691889.24"
assert strip["awarded_underlying_vno_usd"] == "265707100"
assert strip["accepted_participants"] == "7"
assert strip["caja_depositante"] == "0306" and strip["caja_comitente"] == "40000"
assert strip["settlement_due_t_plus_3"] == "2009-06-18"
assert strip["settlement_confirmation"] == "SCHEDULED_NOT_INDEPENDENTLY_CONFIRMED"


bridge = read_csv(HERE / "E0_FISCAL_BUYBACK_APPROX_AGGREGATE_BRIDGE_V116.csv")
bridge_by_id = {row["row_id"]: row for row in bridge}
assert len(bridge) == 9
public_total = Decimal(bridge_by_id["PUBLIC_TOTAL_USD_EQ"]["usd_equivalent"])
synthetic = Decimal(bridge_by_id["SYNTHETIC_SUM"]["usd_equivalent"])
gap = Decimal(bridge_by_id["BRIDGE_GAP"]["usd_equivalent"])
assert public_total == Decimal("43908257.20821723865781304819327998261945")
assert synthetic == Decimal("423908257.2082172386578130481932799826194")
assert gap == Decimal("3908257.2082172386578130481932799826194")
assert bridge_by_id["SYNTHETIC_SUM"]["additivity"] == "CONTROL_NOT_ADDITIVE"
assert bridge_by_id["BCRA_CONTROL"]["amount"] == "420000000"


events = read_csv(HERE / "E0_FISCAL_BUYBACK_PROGRAM_EVENTS_2005_2009_V116.csv")
assert len(events) == 10
events_by_id = {row["event_id"]: row for row in events}
assert events_by_id["E2009_STRIP_OFFICIAL"]["status"] == "PRIMARY_RESULT_EXACT_SETTLEMENT_OPEN"
assert events_by_id["E2009_STRIP_SECONDARY_RESULT"]["status"] == "SECONDARY_QUANTITATIVE_CORROBORATED_BY_PRIMARY"
assert events_by_id["E2008_BCRA_APPROX_PROGRAM_CONTROL"]["additivity"] == "CONTROL_NOT_ADDITIVE"


ledger = read_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V116.csv")
assert len(ledger) == 121, len(ledger)
assert len({row["ledger_id"] for row in ledger}) == len(ledger)
assert {f"F{i}" for i in range(115, 122)} <= {row["ledger_id"] for row in ledger}
assert all(row["realization_status"] != "CASH_SETTLED" for row in ledger if row["ledger_id"] in {f"F{i}" for i in range(115, 122)})
assert next(row for row in ledger if row["ledger_id"] == "F117")["amount_original"] == "33691889.24"
assert next(row for row in ledger if row["ledger_id"] == "F121")["additivity"] == "CONTROL_NOT_ADDITIVE"


breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V116.csv")
assert len(breaks) == 57, len(breaks)
assert len({row["break_id"] for row in breaks}) == len(breaks)
assert {
    "strip_effective_not_underlying_vno",
    "archival_capture_preserves_primary_provenance",
    "approximate_program_aggregate_not_exact_reconciliation",
} <= {row["break_id"] for row in breaks}


matrix = read_csv(HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V116.csv")
matrix_strip = next(row for row in matrix if row["variable"] == "boden_2012_strip_and_residual_registration")
assert matrix_strip["status"] == "STRIP_PRIMARY_RESULT_EXACT_PARTICIPANTS_MAPPED_SETTLEMENT_OPEN"
assert "USD33.69188924M" in matrix_strip["recovery_value"]


evidence = read_csv(HERE / "HISTORICAL_EVIDENCE_COVERAGE_V116.csv")
state = next(row for row in evidence if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra")
assert state["quality"] == "PRIMARY_BUYBACK_FOUR_ARCHIVED_ROUNDS_STRIP_PRIMARY_EXACT_ACCOUNT_ROUTE_2001_2012"
assert "strip 2009" in state["gap"] and "confirmaciones" in state["gap"]


queue = read_csv(HERE / "HISTORICAL_SOURCE_QUEUE_V116.csv")
state_queue = [row for row in queue if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra"]
assert len(state_queue) == 2
assert all(row["status"] == "FOUR_ROUNDS_AND_STRIP_PRIMARY_EXACT_SETTLEMENT_HOLDERS_OPEN" for row in state_queue)
assert all("resultado primario del strip" not in row["next_action"] for row in state_queue)


current = read_csv(HERE / "CURRENT_STATE_V116.csv")
assert len(current) == 39
assert sum(row["strict_panel_status"] == "ELIGIBLE" for row in current) == 30
coverage = read_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V116.csv")
assert STRICT in " ".join(" ".join(row.values()) for row in coverage)


hash_rows = read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V116.csv")
assert len(hash_rows) == 272
assert sum(row["exists"] == "True" for row in hash_rows) == 267
assert sum(row["hash_ok"] == "True" for row in hash_rows) == 267


completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V116.json").read_text(encoding="utf-8"))
assert completeness["checkpoint"] == "V116"
assert completeness["master_catalog_entries"] == 272
assert completeness["physical_local_copies"] == completeness["physical_local_hash_ok"] == 267
assert completeness["e0_primary_sources_preserved"] == 73
assert completeness["sources_newly_preserved_v116"] == 3
assert completeness["pending_binary_discovery_actions"] == 4
assert completeness["e0_strip_primary_quantitative_result_preserved"] is True
assert completeness["e0_strip_awarded_effective_usd"] == "33691889.24"
assert completeness["e0_strip_settlement_confirmed"] is False
assert completeness["closed_network_gate"] == "NO"
assert completeness["strict_coverage_pct"] == STRICT


inherited = read_csv(HERE / "INHERITED_QA_STATUS_V116.csv")
assert next(row for row in inherited if row["script"] == "qa_v115.py")["post_v116_result"] == "EXPECTED_SUPERSEDED_ASSERTION"
assert next(row for row in inherited if row["script"] == "qa_v116.py")["post_v116_result"] == "PASS"


manifest = json.loads((HERE / "MANIFEST_V116.json").read_text(encoding="utf-8"))
assert manifest["checkpoint"] == "V116" and manifest["parent_checkpoint"] == "V115"
assert manifest["e0_primary_sources"] == 73 and manifest["new_preserved_sources"] == 3
assert manifest["fiscal_ledger_rows"] == 121 and manifest["fiscal_method_breaks"] == 57
assert manifest["strip_offer_rows"] == 35 and manifest["strip_accepted_offer_rows"] == 20
assert manifest["strip_participant_rows"] == 7
for item in manifest["files"]:
    path = HERE / item["path"]
    assert path.stat().st_size == item["bytes"], path
    assert digest(path) == item["sha256"], path


global_manifest = json.loads((CYCLE / "MANIFEST_SHA256.json").read_text(encoding="utf-8"))
assert global_manifest["checkpoint"] == "V116"
assert global_manifest["exact_entities"] == 30
assert global_manifest["strict_coverage_pct"] == STRICT
assert global_manifest["closed_network_gate"] == "NO"

print("V116 QA PASS")
