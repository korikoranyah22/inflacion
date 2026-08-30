from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import csv
import hashlib
import html
import json
import re


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
V125 = HERE.parent / "V125"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


source_specs = {
    "e0_caja_archive_recompra_2008_query": ("caja_archive_recompra_2008.html", "ebe50392348978745c22cd29d1e35ae49b1c1712bb042a58e9efc29af1e9a417", 28574),
    "e0_caja_archive_window_2008_09_12_2008_10_10_query": ("caja_archive_window_2008-09-12_2008-10-10.html", "86b99286f08393a60185f79c3cd819614a6b97da2ac5a9c44316e7b324546b83", 56094),
    "e0_argentina_deuda_publica_2008_q3": ("deuda_publica_30-09-08.xls", "9e986552e6a6b37662046b0b808b78878b52bc885595ed3d0f75eca58f4d0b82", 2236928),
    "e0_argentina_deuda_publica_2008_q4": ("deuda_publica_31-12-2008.xls", "7eae7145e29214a2aaae75384e38f592ce8367a94f920978187417ceef8c2e31", 6036992),
}

catalog = read_csv(REPO / "data" / "fuentes" / "FUENTES.csv")
assert len(catalog) == 302 and len({row["id"] for row in catalog}) == 302
catalog_by_id = {row["id"]: row for row in catalog}
assert set(source_specs) <= catalog_by_id.keys()

census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V126.csv")
census_v125 = read_csv(V125 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V125.csv")
assert len(census) == 103 and len(census_v125) == 99
assert {row["source_id"] for row in census} - {row["source_id"] for row in census_v125} == set(source_specs)

binary_dir = CYCLE / "inputs" / "historical_retrieval" / "v126" / "binaries"
for source_id, (file_name, expected_hash, expected_bytes) in source_specs.items():
    path = binary_dir / file_name
    assert path.is_file() and path.stat().st_size == expected_bytes
    assert digest(path) == expected_hash == catalog_by_id[source_id]["sha256"]
    row = next(item for item in census if item["source_id"] == source_id)
    assert row["primary_source"] == "YES" and row["preserved"] == "YES" and row["sha256"] == expected_hash


def archive_rows(text: str) -> list[tuple[str, str, str]]:
    pattern = re.compile(
        r'<td align="right">(\d+)</td><td align="left">(.*?)</td><td align="center"[^>]*>(\d{2}/\d{2}/\d{4})</td>',
        re.S,
    )
    return [(number, html.unescape(re.sub(r"<[^>]+>", "", title)).strip(), date) for number, title, date in pattern.findall(text)]


annual = archive_rows((binary_dir / source_specs["e0_caja_archive_recompra_2008_query"][0]).read_text(encoding="utf-8", errors="replace"))
window = archive_rows((binary_dir / source_specs["e0_caja_archive_window_2008_09_12_2008_10_10_query"][0]).read_text(encoding="utf-8", errors="replace"))
assert [row[0] for row in annual] == ["4873", "4861", "4857"]
assert [row[0] for row in window] == [str(number) for number in range(4903, 4876, -1)]
assert all("recompra" not in row[1].casefold() for row in window)
assert next(row for row in window if row[0] == "4895")[2] == "02/10/2008"

archive_audit = read_csv(HERE / "E0_CAJA_ARCHIVE_FOURTH_ROUND_SEARCH_AUDIT_V126.csv")
assert len(archive_audit) == 2
assert next(row for row in archive_audit if row["audit_id"] == "CA126_01")["returned_numbers"] == "4873;4861;4857"
assert next(row for row in archive_audit if row["audit_id"] == "CA126_02")["returned_numbers"] == "4877-4903_CONTINUOUS"
assert all("exist" in row["forbidden_interpretation"].casefold() or "agota" in row["forbidden_interpretation"].casefold() for row in archive_audit)

bridge = read_csv(HERE / "E0_FISCAL_BUYBACK_DEBT_ACCOUNTING_BRIDGE_2008_V126.csv")
assert len(bridge) == 4 and len({row["bridge_id"] for row in bridge}) == 4
q3 = next(row for row in bridge if row["bridge_id"] == "AB126_Q3_BODEN")
assert Decimal(q3["boden2012_awarded_vno_usd"]) * Decimal(q3["boden2012_residual_factor"]) / 1000 == Decimal(q3["boden2012_residual_thousand_usd"])
assert Decimal(q3["boden2013_awarded_vno_usd"]) * Decimal(q3["boden2013_residual_factor"]) / 1000 == Decimal(q3["boden2013_residual_thousand_usd"])
assert Decimal(q3["boden2012_residual_thousand_usd"]) + Decimal(q3["boden2013_residual_thousand_usd"]) == Decimal(q3["official_amount_thousand_usd"]) == Decimal("16814")
assert Decimal(q3["delta_thousand_usd"]) == 0
q4 = next(row for row in bridge if row["bridge_id"] == "AB126_Q4_CANJE")
annual_total = next(row for row in bridge if row["bridge_id"] == "AB126_2008_TOTAL")
assert Decimal(q3["official_amount_thousand_usd"]) + Decimal(q4["official_amount_thousand_usd"]) == Decimal(annual_total["official_amount_thousand_usd"]) == Decimal("1523524.11")
assert next(row for row in bridge if row["bridge_id"] == "AB126_GDP_EXCLUSION")["evidence_status"] == "OFFICIAL_ACCOUNTING_ACKNOWLEDGMENT_AMOUNT_EXCLUDED"

ledger = read_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V126.csv")
breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V126.csv")
assert len(ledger) == 129 and len({row["ledger_id"] for row in ledger}) == 129
assert {"F126", "F127", "F128", "F129"} <= {row["ledger_id"] for row in ledger}
assert next(row for row in ledger if row["ledger_id"] == "F126")["realization_status"] == "ACCOUNTED_AGGREGATE_DEBT_REDUCTION_EXACT_MATCH"
assert not any(row["realization_status"] == "CASH_SETTLED" for row in ledger if row["ledger_id"] in {"F126", "F127", "F128", "F129"})
assert len(breaks) == 94 and len({row["break_id"] for row in breaks}) == 94
assert {
    "current_public_archive_absence_not_historical_nonexistence",
    "aggregate_debt_reduction_not_per_round_settlement",
    "tender_vno_not_residual_debt_stock",
    "gdp_units_excluded_not_zero_or_unexecuted",
    "q4_exchange_bond_aggregate_not_target_tenders",
} <= {row["break_id"] for row in breaks}

for name in (
    "E0_FISCAL_PUBLIC_BUYBACK_TENDERS_2008_V126.csv",
    "E0_FISCAL_BODEN_BUYBACK_TENDERS_2008_V126.csv",
    "E0_FISCAL_PUBLIC_BUYBACK_AWARDS_2008_V126.csv",
    "E0_FISCAL_BODEN_BUYBACK_AWARDS_2008_V126.csv",
):
    rows = read_csv(HERE / name)
    target_rows = [row for row in rows if row.get("instrument") in {"BODEN_2012", "BODEN_2013"} and row.get("tender_date") in {"2008-09-04", "2008-09-11"}]
    assert target_rows and all(row["settlement_confirmation"].startswith("AGGREGATE_Q3_DEBT_REDUCTION_EXACT_MATCH") for row in target_rows)
    assert all("pago BCRA" in row["caveat"] for row in target_rows)

trace = read_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V126.csv")
closures = read_csv(HERE / "E0_REQUEST_CLOSURE_CRITERIA_V126.csv")
search_keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V126.csv")
attachments = read_csv(HERE / "E0_REQUEST_ATTACHMENT_MINIMUM_V126.csv")
assert len(trace) == 78 and len({row["trace_id"] for row in trace}) == 78
assert len(closures) == 9 and len({row["gap_id"] for row in closures}) == 9
assert len(search_keys) == 59 and len({row["key_id"] for row in search_keys}) == 59
assert len(attachments) == 8
assert next(row for row in trace if row["trace_id"] == "TR126_078")["gap_id"] == "CL126_DEBT_ACCOUNTING"
assert {row["gap_id"] for row in trace} <= {row["gap_id"] for row in closures}
assert all(row["status"] == "DRAFT_NOT_SENT" for row in trace)
assert any("16814" in row["exact_key"] for row in search_keys) and any("1506710.11" in row["exact_key"] for row in search_keys)
assert any(row["attach_file"] == "E0_FISCAL_BUYBACK_DEBT_ACCOUNTING_BRIDGE_2008_V126.csv" for row in attachments)

responses = read_csv(HERE / "E0_REQUEST_RESPONSE_REGISTER_V126.csv")
assert len(responses) == 6 and all(row["status"] == "DRAFT_NOT_SENT" for row in responses)
assert all(row["submitted_on"] == "N/A" and row["receipt_or_case_id"] == "N/A" for row in responses)
economia = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V126.md").read_text(encoding="utf-8")
assert all(token in economia for token in ("Boden - Recompras", "1.506.710,11", "GDP Units", "r) detalle y conciliación"))
package = (HERE / "E0_INSTITUTIONAL_REQUEST_PACKAGE_V126.md").read_text(encoding="utf-8")
assert "59 claves" in package and "78 objetos" in package

coverage = read_csv(HERE / "HISTORICAL_EVIDENCE_COVERAGE_V126.csv")
state = next(row for row in coverage if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra")
assert state["quality"] == "PRIMARY_BUYBACK_ACCOUNTING_EXACT_Q3_BODEN_REDUCTION_AND_DIRECT_CAJA_ROUTE_PRESERVED"
assert "baja contable" in state["gap"].casefold() and "pago bcra" in state["gap"].casefold()
queue = read_csv(HERE / "HISTORICAL_SOURCE_QUEUE_V126.csv")
state_queue = [row for row in queue if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra"]
assert len(state_queue) == 2 and all(row["status"].startswith("PUBLIC_ACCOUNTING_WRITE_DOWN_BRIDGE") for row in state_queue)

current = read_csv(HERE / "CURRENT_STATE_V126.csv")
coverage_panel = read_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V126.csv")
assert len(current) == 39 and sum(row["strict_panel_status"] == "ELIGIBLE" for row in current) == 30
assert STRICT in " ".join(" ".join(row.values()) for row in coverage_panel)

hash_rows = read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V126.csv")
assert len(hash_rows) == 302
assert sum(row["exists"] == "True" for row in hash_rows) == 297
assert sum(row["hash_ok"] == "True" for row in hash_rows) == 297

completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V126.json").read_text(encoding="utf-8"))
assert completeness["checkpoint"] == "V126"
assert completeness["master_catalog_entries"] == 302
assert completeness["physical_local_copies"] == 297 and completeness["physical_local_hash_ok"] == 297
assert completeness["e0_primary_sources_preserved"] == 103
assert completeness["sources_newly_preserved_v126"] == 4
assert completeness["e0_fiscal_ledger_rows"] == 129 and completeness["e0_fiscal_method_breaks_frozen"] == 94
assert completeness["e0_request_traceability_rows"] == 78 and completeness["e0_request_closure_rules"] == 9
assert completeness["e0_request_search_keys"] == 59 and completeness["e0_request_attachment_rows"] == 8
assert completeness["e0_buyback_accounting_bridge_rows"] == 4 and completeness["e0_caja_archive_fourth_round_search_rows"] == 2
assert completeness["e0_requests_submitted"] == 0 and completeness["e0_request_responses_received"] == 0
assert completeness["closed_network_gate"] == "NO" and completeness["strict_coverage_pct"] == STRICT

manifest = json.loads((HERE / "MANIFEST_V126.json").read_text(encoding="utf-8"))
assert manifest["checkpoint"] == "V126" and manifest["parent_checkpoint"] == "V125"
assert manifest["e0_primary_sources"] == 103 and manifest["new_primary_sources"] == 4
assert manifest["fiscal_ledger_rows"] == 129 and manifest["fiscal_method_breaks"] == 94
assert manifest["buyback_accounting_bridge_rows"] == 4 and manifest["caja_archive_fourth_round_search_rows"] == 2
assert manifest["request_traceability_rows"] == 78 and manifest["request_search_keys"] == 59
assert manifest["requests_submitted"] == 0 and manifest["responses_received"] == 0
for item in manifest["files"]:
    path = HERE / item["path"]
    assert path.stat().st_size == item["bytes"] and digest(path) == item["sha256"]

global_manifest = json.loads((CYCLE / "MANIFEST_SHA256.json").read_text(encoding="utf-8"))
assert global_manifest["checkpoint"] == "V126"
assert global_manifest["exact_entities"] == 30 and global_manifest["strict_coverage_pct"] == STRICT
assert "exact Q3 BODEN accounting reduction" in global_manifest["source_audit"]
assert "none submitted" in global_manifest["source_audit"]

backup = (REPO / "BACKUP_ACTUALIZACION_2026-08-29.md").read_text(encoding="utf-8-sig")
assert "## V126 · baja contable exacta de recompras BODEN 2008" in backup
assert "Los seis pedidos siguen DRAFT_NOT_SENT" in backup

print("V126 QA PASS")
