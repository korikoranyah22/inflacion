from pathlib import Path
import csv
import hashlib
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
AUDIT = REPO / "research" / "ciclo_ajuste" / "source_audit"


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


new_ids = {
    "e0_cgn_disposition_49_2002_saf355_closing_exception",
    "e0_cgn_account_2008_uepex_closing_exception",
    "e0_mecon_uai_report_03_2022_saf355_closure_2021",
    "e0_mecon_uai_report_51_2022_account_2021",
    "e0_argentina_mecon_uai_audit_catalog_2022",
}

with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as handle:
    catalog = list(csv.DictReader(handle))
assert len(catalog) == 474 and len({row["id"] for row in catalog}) == 474
assert new_ids <= {row["id"] for row in catalog}

census = {row["source_id"]: row for row in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V148.csv")}
provenance = {row["source_id"]: row for row in rows("ARCHIVAL_PROVENANCE_V148.csv")}
assert len(census) == 234 and new_ids <= set(census) and new_ids <= set(provenance)
for source_id in new_ids:
    path = REPO / census[source_id]["local_path"].lstrip("/")
    assert path.is_file() and digest(path) == census[source_id]["sha256"]

closing = rows("E0_SAF355_CLOSING_EXCEPTION_AND_SPECIAL_ROUTE_V148.csv")
tgn = rows("E0_TGN_BNA_LEGAL_CUSTODY_AND_MOVEMENT_ROUTE_V148.csv")
executive = rows("E0_PUBLIC_EXECUTIVE_ONLY_ACT_BODY_GAP_V148.csv")
searches = rows("E0_EXACT_TARGET_ID_PUBLIC_SEARCH_V148.csv")
continuity = rows("E0_83106000_DISCLOSURE_TYPE_CONTINUITY_2005_2010_V148.csv")
decision = rows("E0_DUAL_PAYMENT_MECHANISM_DECISION_TREE_V148.csv")
repo = rows("E0_REPO_PUBLIC_UNROUNDED_SEARCH_V148.csv")
objects = rows("E0_V148_REQUEST_OBJECTS_V148.csv")
visual = rows("E0_V148_PDF_VISUAL_CONTROL.csv")

assert len(closing) == 12
assert any(row["element"] == "EXCEPTION" and "355" in row["record_or_rule"] for row in closing)
assert any(row["element"] == "EXCLUDED_PRESUMPTION" for row in closing)
assert all(row["target_payment_confirmed"] == "FALSE" for row in closing)

assert len(tgn) == 12
assert any(row["stage"] == "PRE_CANCELLATION" and row["legal_locator"] == "Art.74(k)" for row in tgn)
assert any(row["stage"] == "POST_CANCELLATION" and row["legal_locator"] == "Art.74(k)" for row in tgn)
assert any(row["stage"] == "BANK_INFORMATION" and row["legal_locator"] == "Art.78.7.4" for row in tgn)
assert all(row["target_payment_confirmed"] == "FALSE" for row in tgn)

assert len(executive) == 10
assert sum(row["status"] == "ANALYTIC_BODY_NOT_LOCATED" for row in executive) == 2
assert any(row["status"] == "PUBLIC_ACT_BODY_NOT_LOCATED" for row in executive)
assert len(searches) == 12
assert sum(row["status"] == "EXACT_PUBLIC_REFERENCE_ROW_ONLY" for row in searches) == 5
assert any(row["status"] == "CONTROLLED_NEGATIVE" for row in searches)

assert len(continuity) == 8
signals = {row["document_signal"] for row in continuity}
assert {"NUMBERED_SIDIF", "AGGREGATED", "TARGET_TYPE_OPEN", "NO_PRINTED_DOCUMENT_SIGNAL", "C41_EXPLICIT"} <= signals
assert len(decision) == 10 and {"SETTLED_A", "SETTLED_B", "OPEN_0_OF_10"} <= {row["next_state"] for row in decision}
assert all(row["current_target_state"] == "OPEN_0_OF_10" for row in decision)

assert len(repo) == 6
assert all(row["arithmetic_error_proved"] == "FALSE" and row["unrounded_components_located"] == "FALSE" for row in repo)
assert len(objects) == 18 and all(row["status"] == "DRAFT_NOT_SENT" for row in objects)
assert len(visual) == 44 and all(row["result"] == "PASS" for row in visual)

breaks = rows("E0_FISCAL_METHOD_BREAKS_V148.csv")
trace = rows("E0_INFORMATION_REQUEST_TRACEABILITY_V148.csv")
keys = rows("E0_REQUEST_SEARCH_KEY_MATRIX_V148.csv")
assert len(breaks) == 231
required_breaks = {
    "saf355_general_closing_tables_exempt_2008",
    "standard_caja_bancos_route_not_target_repository",
    "public_executive_not_analytic_report",
    "closing_integrity_not_final_before_definitive_close",
    "tgn_bna_statutory_access_not_target_movement",
    "tgn_custody_before_cancellation_cgn_after",
    "later_debit_direct_rule_not_target_type",
}
assert required_breaks <= {row["break_id"] for row in breaks}
assert len(trace) == 262 and all(row["status"] == "DRAFT_NOT_SENT" for row in trace)
assert len(keys) == 318
assert {"Disposición CGN 49/2002", "TGN hasta cancelación", "CGN después de cancelación", "artículo 78.7.4 Decreto 1344/2007"} <= {row["exact_key"] for row in keys}

register = rows("E0_REQUEST_RESPONSE_REGISTER_V148.csv")
assert len(register) == 6 and all(row["status"] == "DRAFT_NOT_SENT" for row in register)
assert all(row["submitted_on"] == "N/A" and row["receipt_or_case_id"] == "N/A" for row in register)
request_files = [
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V148.md",
    "REQUEST_BCRA_CRYL_SETTLEMENT_V148.md",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V148.md",
    "REQUEST_AGN_2018_REPLY_V148.md",
    "REQUEST_CNV_CUSTODY_RECORDS_V148.md",
    "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V148.md",
]
for name in request_files:
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "BORRADOR_NO_ENVIADO" in text or "DRAFT_NOT_SENT" in text

with (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V148.csv").open(encoding="utf-8-sig", newline="") as handle:
    hashes = list(csv.DictReader(handle))
assert sum(row["exists"] == "True" for row in hashes) == 468
assert sum(row["hash_ok"] == "True" for row in hashes) == 468

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V148.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V148"
assert complete["master_catalog_entries"] == 474 and complete["e0_primary_sources_preserved"] == 234
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 468
assert complete["remaining_physical_gaps"] == 6
assert complete["e0_saf355_standard_closing_tables_required_2008"] is False
assert complete["e0_saf355_special_closing_route_proved_2008"] is True
assert complete["e0_tgn_can_require_bna_movements_original_2007"] is True
assert complete["e0_tgn_custody_before_cancellation_cgn_after"] is True
assert complete["e0_target_forms_public_bodies_located"] == 0
assert complete["e0_public_uai_analytic_reports_located"] == 0
assert complete["e0_repo_unrounded_components_located"] is False
assert complete["e0_repo_arithmetic_error_proved"] is False
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0 and complete["e0_request_responses_received"] == 0

manifest = json.loads((HERE / "MANIFEST_V148.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V148" and manifest["parent_checkpoint"] == "V147"
assert manifest["new_preserved_sources"] == 5
assert manifest["saf355_standard_closing_tables_required_2008"] is False
assert manifest["tgn_can_require_bna_movements_original_2007"] is True
assert manifest["target_forms_public_bodies_located"] == 0
assert manifest["public_uai_analytic_reports_located"] == 0
assert manifest["repo_arithmetic_error_proved"] is False
assert manifest["executed_settlement_rows_confirmed"] == 0
assert manifest["requests_submitted"] == 0 and manifest["responses_received"] == 0

for name in ("README_V148.md", "VEREDICTO_V148.md", "E0_FISCAL_RECONSTRUCTION_V148.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V148_A_V149.md"):
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")
assert not list(HERE.glob("*V147*"))
assert not (HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V148_A_V148.md").exists()

combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined and "TARGET_EXTRACT_FOUND" not in combined
print("V148 QA PASS")
