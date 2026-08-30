from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import csv
import hashlib
import json

from pypdf import PdfReader


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v115" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"
CENT = Decimal("0.01")
PCT = Decimal("0.00000001")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


source_ids = {
    "e0_argentina_finanzas_archive_recompras_voluntarias",
    "e0_argentina_llamado_recompra_2008_08_27",
    "e0_argentina_llamado_recompra_2008_09_03",
    "e0_argentina_llamado_recompra_2008_09_10",
    "e0_argentina_llamado_recompra_2008_10_01",
}


catalog = read_csv(REPO / "data" / "fuentes" / "FUENTES.csv")
assert len(catalog) == 269, len(catalog)
assert len({row["id"] for row in catalog}) == len(catalog)
catalog_by_id = {row["id"]: row for row in catalog}
assert source_ids <= catalog_by_id.keys()


census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V115.csv")
assert len(census) == 70, len(census)
assert len({row["source_id"] for row in census}) == len(census)
assert source_ids <= {row["source_id"] for row in census}
for source_id in source_ids:
    source = catalog_by_id[source_id]
    local = REPO / source["archivo_local"].lstrip("/")
    assert local.is_file(), local
    assert digest(local) == source["sha256"]
    row = next(item for item in census if item["source_id"] == source_id)
    assert row["primary_source"] == "YES" and row["preserved"] == "YES"
    assert row["sha256"] == source["sha256"]


pdfs = sorted(BIN.glob("*.pdf"))
htmls = sorted(BIN.glob("*.html"))
assert len(pdfs) == 4 and len(htmls) == 1, (len(pdfs), len(htmls))
for pdf in pdfs:
    assert pdf.read_bytes().startswith(b"%PDF"), pdf
    assert len(PdfReader(str(pdf)).pages) == 2, pdf
archive = htmls[0].read_text(encoding="utf-8")
for marker in (
    "Recompras voluntarias",
    "comunicado_resultado_licitacion_02-10-08.pdf",
    "comunicado_llamado_licitacion_01-10-08.pdf",
    "comunicado_resultado11-09-08.pdf",
    "comunicado_llamado_licitacion_10-09-08.pdf",
    "comunicado_de_prensa_resultado_04-09-08.pdf",
    "comunicado_llamado_licitacion_03-09-08.pdf",
    "comunicado_de_prensa_resultado_28-08-08.pdf",
    "comunicado_llamado_licitacion_27-08-08.pdf",
):
    assert marker in archive, marker
assert not (REPO / "tmp" / "pdfs" / "v115_calls").exists()


calls = read_csv(HERE / "E0_FISCAL_PUBLIC_BUYBACK_CALLS_2008_V115.csv")
assert len(calls) == 4
assert [row["round_number"] for row in calls] == ["1", "2", "3", "4"]
assert [row["call_date"] for row in calls] == ["2008-08-27", "2008-09-03", "2008-09-10", "2008-10-01"]
assert [row["tender_date"] for row in calls] == ["2008-08-28", "2008-09-04", "2008-09-11", "2008-10-02"]
assert [row["settlement_due_t_plus_3"] for row in calls] == ["2008-09-02", "2008-09-09", "2008-09-16", "2008-10-07"]
assert [row["announced_ceiling_ars"] for row in calls] == ["150000000", "200000000", "100000000", "100000000"]
assert all(row["caja_depositante"] == "0306" and row["caja_comitente"] == "40000" for row in calls)
assert all(row["actual_transfer_confirmation"] == "NO" and row["actual_payment_confirmation"] == "NO" for row in calls)
assert sum(Decimal(row["announced_ceiling_ars"]) for row in calls) == Decimal("550000000")
assert sum(Decimal(row["awarded_effective_ars"]) for row in calls) == Decimal("135606214.86")
assert (
    sum(Decimal(row["awarded_effective_ars"]) for row in calls)
    / sum(Decimal(row["announced_ceiling_ars"]) for row in calls)
    * Decimal(100)
).quantize(PCT, ROUND_HALF_UP) == Decimal("24.65567543")


tenders = read_csv(HERE / "E0_FISCAL_PUBLIC_BUYBACK_TENDERS_2008_V115.csv")
awards = read_csv(HERE / "E0_FISCAL_PUBLIC_BUYBACK_AWARDS_2008_V115.csv")
assert len(tenders) == 14 and len(awards) == 18
assert sum(Decimal(row["awarded_effective_ars"]) for row in tenders) == Decimal("135606214.86")
assert sum(Decimal(row["awarded_effective_ars_raw"]) for row in awards) == Decimal("135606214.85506")
assert sum(Decimal(row["awarded_effective_ars_raw"]) for row in awards).quantize(CENT, ROUND_HALF_UP) == Decimal("135606214.86")
assert all(row["settlement_confirmation"] == "SCHEDULED_NOT_INDEPENDENTLY_CONFIRMED" for row in awards)
assert all(row["ultimate_holder_identified"] == "NO" for row in awards)


settlement = read_csv(HERE / "E0_FISCAL_BUYBACK_SETTLEMENT_CHAIN_V115.csv")
assert len(settlement) == 7
step5 = next(row for row in settlement if row["step"] == "5")
step7 = next(row for row in settlement if row["step"] == "7")
assert step5["account_or_system"] == "Caja_de_Valores_depositante_0306_comitente_40000"
assert step5["evidence_status"] == "NORMATIVE_ROUTE_PLUS_FOUR_NUMBERED_CALLS_ACTUAL_TRANSFER_FILES_OPEN"
assert step7["timing"] == "T_PLUS_3_2008_09_02_09_09_09_16_10_07"
assert step7["evidence_status"] == "NORMATIVE_ROUTE_PLUS_FOUR_NUMBERED_CALLS_ACTUAL_PAYMENT_OPEN"


events = read_csv(HERE / "E0_FISCAL_BUYBACK_PROGRAM_EVENTS_2005_2009_V115.csv")
assert len(events) == 9
event_by_id = {row["event_id"]: row for row in events}
assert event_by_id["E20080821_SECOND_STAGE"]["status"] == "FOUR_CALL_AND_RESULT_PAIRS_IN_OFFICIAL_ARCHIVE"
assert event_by_id["E20080827_20081001_FOUR_CALLS"]["reported_amount"] == "550000000"
assert event_by_id["E20080827_20081001_FOUR_CALLS"]["additivity"] == "NON_ADDITIVE_CEILING_CONTROL"


ledger = read_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V115.csv")
assert len(ledger) == 114, len(ledger)
assert len({row["ledger_id"] for row in ledger}) == len(ledger)
assert {f"F{i}" for i in range(109, 115)} <= {row["ledger_id"] for row in ledger}
assert all(row["realization_status"] != "CASH_SETTLED" for row in ledger if row["ledger_id"] in {f"F{i}" for i in range(109, 115)})
assert next(row for row in ledger if row["ledger_id"] == "F114")["amount_original"] == "550000000"
assert next(row for row in ledger if row["ledger_id"] == "F114")["additivity"] == "CONTROL_NOT_ADDITIVE"


breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V115.csv")
assert len(breaks) == 54, len(breaks)
assert len({row["break_id"] for row in breaks}) == len(breaks)
assert {
    "announced_ceiling_not_award_or_cash",
    "archive_inventory_not_settlement_confirmation",
    "fiduciary_account_not_transfer_confirmation",
} <= {row["break_id"] for row in breaks}


matrix = read_csv(HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V115.csv")
round_row = next(row for row in matrix if row["variable"] == "four_official_archive_buyback_rounds")
assert round_row["status"] == "FOUR_ARCHIVED_ROUNDS_CALLS_RESULTS_ACCOUNT_ROUTE_MAPPED"
assert "24.65567543PCT" in round_row["recovery_value"]
assert not any(row["variable"] == "four_located_public_buyback_tenders" for row in matrix)


evidence = read_csv(HERE / "HISTORICAL_EVIDENCE_COVERAGE_V115.csv")
state = next(row for row in evidence if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra")
assert state["quality"] == "PRIMARY_BUYBACK_FOUR_ARCHIVED_ROUNDS_ACCOUNT_ROUTE_EXACT_2001_2012"
assert "0306/40000" in state["gap"] and "Caja/BCRA" in state["gap"]


queue = read_csv(HERE / "HISTORICAL_SOURCE_QUEUE_V115.csv")
state_queue = [row for row in queue if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra"]
assert len(state_queue) == 2
assert all(row["status"] == "FOUR_ARCHIVED_ROUNDS_ACCOUNT_ROUTE_EXACT_SETTLEMENT_HOLDERS_OPEN" for row in state_queue)


current = read_csv(HERE / "CURRENT_STATE_V115.csv")
assert len(current) == 39
assert sum(row["strict_panel_status"] == "ELIGIBLE" for row in current) == 30
coverage = read_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V115.csv")
assert STRICT in " ".join(" ".join(row.values()) for row in coverage)


hash_rows = read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V115.csv")
assert len(hash_rows) == 269
assert sum(row["exists"] == "True" for row in hash_rows) == 264
assert sum(row["hash_ok"] == "True" for row in hash_rows) == 264


completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V115.json").read_text(encoding="utf-8"))
assert completeness["checkpoint"] == "V115"
assert completeness["master_catalog_entries"] == 269
assert completeness["physical_local_copies"] == completeness["physical_local_hash_ok"] == 264
assert completeness["e0_primary_sources_preserved"] == 70
assert completeness["sources_newly_preserved_v115"] == 5
assert completeness["e0_primary_sources_newly_preserved_v115"] == 5
assert completeness["pending_binary_discovery_actions"] == 5
assert completeness["e0_four_archived_rounds_confirmed"] is True
assert completeness["e0_four_call_announced_ceiling_ars"] == "550000000"
assert completeness["e0_four_round_awarded_effective_ars"] == "135606214.86"
assert completeness["e0_award_utilization_pct_of_announced_ceilings"] == "24.65567543"
assert completeness["e0_fiduciary_account_route_identified"] is True
assert completeness["e0_settlement_confirmations_preserved"] is False
assert completeness["strict_coverage_pct"] == STRICT
assert completeness["closed_network_gate"] == "NO"


inherited = read_csv(HERE / "INHERITED_QA_STATUS_V115.csv")
assert next(row for row in inherited if row["script"] == "qa_v114.py")["post_v115_result"] == "EXPECTED_SUPERSEDED_ASSERTION"
assert next(row for row in inherited if row["script"] == "qa_v115.py")["post_v115_result"] == "PASS"


manifest = json.loads((HERE / "MANIFEST_V115.json").read_text(encoding="utf-8"))
assert manifest["checkpoint"] == "V115" and manifest["parent_checkpoint"] == "V114"
assert manifest["e0_primary_sources"] == 70 and manifest["new_preserved_sources"] == 5
assert manifest["fiscal_ledger_rows"] == 114 and manifest["fiscal_method_breaks"] == 54
assert manifest["public_tender_call_rows"] == 4
assert manifest["four_call_announced_ceiling_ars"] == "550000000"
assert manifest["four_round_awarded_effective_ars"] == "135606214.86"
assert manifest["award_utilization_pct_of_announced_ceilings"] == "24.65567543"
for item in manifest["files"]:
    path = HERE / item["path"]
    assert path.stat().st_size == item["bytes"]
    assert digest(path) == item["sha256"]


global_manifest = json.loads((CYCLE / "MANIFEST_SHA256.json").read_text(encoding="utf-8"))
assert global_manifest["checkpoint"] == "V115"
assert global_manifest["exact_entities"] == 30
assert global_manifest["strict_coverage_pct"] == STRICT
assert global_manifest["closed_network_gate"] == "NO"

print("V115 QA PASS")
