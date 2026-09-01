from pathlib import Path
import csv
import hashlib
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
COVERAGE = "63.4406041403540997520463142785031521252747951992299547614348265414453439585848248058817492708499966268585997481191265825"
NEW_ID = "commoncrawl_collection_catalog_2026_08_31_v170"


def rows(name):
    with (HERE / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


with (REPO / "data/fuentes/FUENTES.csv").open(encoding="utf-8-sig", newline="") as handle:
    catalog = list(csv.DictReader(handle))
assert len(catalog) == 597 and len({row["id"] for row in catalog}) == 597
new = next(row for row in catalog if row["id"] == NEW_ID)
new_path = REPO / new["archivo_local"].lstrip("/")
assert new_path.is_file() and new_path.stat().st_size == 34947
assert sha256(new_path) == "c82b50cd071b1491081c794b63f4399782a9dd909c0f24510951c98552dcb3a7"
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    assert path.is_file() and sha256(path) == row["sha256"].lower()

audit = list(csv.DictReader((AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V170.csv").open(encoding="utf-8-sig", newline="")))
assert len(audit) == 597
assert all(row["exists"] == "True" and row["hash_ok"] == "True" for row in audit)
assert (AUDIT / "SOURCE_PRESERVATION_MISSING_V170.csv").read_text(encoding="utf-8-sig").count("\n") == 1

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V170.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V170"
assert complete["master_catalog_entries"] == complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 597
assert complete["remaining_catalog_physical_or_hash_gaps"] == 0
assert complete["commoncrawl_catalog_collections_2013_2020"] == 74
assert complete["commoncrawl_exact_prefix_queries_completed"] == 4
assert complete["commoncrawl_exact_prefix_service_errors"] == 4
assert complete["commoncrawl_evaluable_query_responses_v170"] == 0
assert complete["commoncrawl_false_capture_rows_reclassified"] == 8
assert complete["commoncrawl_prior_negative_invalidated"] is True
assert complete["note_3672_contextual_recipient"] == "CGN"
assert complete["note_3672_formal_addressee_located"] is False
assert complete["note_3672_recipient_identifier_located"] is False
assert complete["plan_sigen_2009_body_located"] is False
assert complete["plan_sigen_2009_approval_act_located"] is False
assert complete["requests_submitted"] == 0 and complete["responses_received"] == 0
assert complete["saf355_certifications_located"] == 0 and complete["executed_historical_bank_rows_confirmed"] == 0

semantics = rows("E0_COMMONCRAWL_QUERY_SEMANTICS_AND_FALSE_POSITIVE_AUDIT_V170.csv")
assert len(semantics) == 7
assert {
    "BROAD_QUERY_INVALID_FOR_FOLDER_CENSUS", "SERVICE_ERROR_FALSE_POSITIVE",
    "DOMAIN_CAPTURE_NOT_FOLDER_CAPTURE", "SERVICE_ERROR_NOT_NEGATIVE",
    "SUPERSEDED_INVALID_QUERY_NEGATIVE", "COLLECTION_UNIVERSE_VERIFIED_QUERY_RESULTS_PENDING",
} <= {row["corrected_classification"] for row in semantics}

collection_coverage = rows("E0_COMMONCRAWL_COLLECTION_COVERAGE_V170.csv")
assert len(collection_coverage) == 74
assert len({row["collection_id"] for row in collection_coverage}) == 74
assert sum(row["exact_prefix_status"] == "SERVICE_ERROR_2_HOSTS" for row in collection_coverage) == 2
assert all(row["evidentiary_effect"] == "NONE_NOT_NEGATIVE" for row in collection_coverage)

raw_dir = CYCLE / "inputs/historical_retrieval/v170/query_logs"
broad = list(csv.DictReader((raw_dir / "commoncrawl_broad_query_raw_superseded.csv").open(encoding="utf-8-sig", newline="")))
exact = list(csv.DictReader((raw_dir / "commoncrawl_exact_prefix_query_raw_2013.csv").open(encoding="utf-8-sig", newline="")))
assert len(broad) == 20 and len(exact) == 4
assert sum(row["classification"] == "CAPTURE_ROWS" for row in broad) == 8
assert sum(row["classification"] == "SERVICE_ERROR" for row in broad) == 12
assert all(row["classification"] == "SERVICE_ERROR" and "matchType=prefix" in row["query_url"] for row in exact)

scan = rows("E0_PLAN_2009_LATE_ARCHIVE_COLLECTION_SCAN_V170.csv")
invalidated = next(row for row in scan if row["scan_id"] == "LA169_03")
assert invalidated["classification"] == "SUPERSEDED_INVALID_QUERY_NEGATIVE" and invalidated["service_state"] == "INVALIDATED"
assert {"LA170_07", "LA170_08", "LA170_09", "LA170_10", "LA170_11", "LA170_12"} <= {row["scan_id"] for row in scan}
assert next(row for row in scan if row["scan_id"] == "LA170_09")["classification"] == "SERVICE_ERRORS_NOT_NEGATIVES"

filename_search = rows("E0_PLAN_2009_EXACT_FILENAME_PUBLIC_SEARCH_V170.csv")
assert len(filename_search) == 4
assert {row["target"] for row in filename_search} == {
    "Plan SIGEN 2009.pdf", "Anexo G - Capacitacion 2009.pdf",
    "planred2009.pdf", "Anexo F - Cuadro 18.pdf",
}
assert all(row["classification"] == "SEARCH_ENGINE_NEGATIVE_SCOPED" for row in filename_search)

pronoun = rows("E0_NOTE_3672_RECIPIENT_PRONOUN_CHAIN_V170.csv")
assert len(pronoun) == 5
recipient_row = next(row for row in pronoun if row["step_id"] == "PR170_04")
assert recipient_row["confidence"] == "HIGH_CONTEXTUAL_INFERENCE" and "CGN" in recipient_row["actor_or_antecedent"]
assert "destinatario nominal" in recipient_row["open_limit"]

note_route = rows("E0_NOTE_3672_ARCHIVAL_SEARCH_V170.csv")
assert {"RECIPIENT_IDENTIFIED_BY_CONTEXT_CGN", "FORMAL_ADDRESSEE_AND_INCOMING_ID_OPEN", "SECONDARY_ROUTING_HYPOTHESIS"} <= {row["status"] for row in note_route}
assert next(row for row in note_route if row["route_id"] == "N170_09")["surface"].startswith("CGN")

approval = rows("E0_PLAN_2009_APPROVAL_ACT_SEARCH_V170.csv")
assert {"AA170_06", "AA170_07"} <= {row["test_id"] for row in approval}
assert next(row for row in approval if row["test_id"] == "AA170_07")["classification"] == "EXISTENCE_DATE_CONFIRMED_ACT_OPEN"

method_breaks = rows("E0_FISCAL_METHOD_BREAKS_V170.csv")
required_breaks = {
    "commoncrawl_wildcard_domain_not_exact_prefix", "curl_exit_zero_html_error_not_capture",
    "commoncrawl_service_error_not_negative_v170", "contextual_recipient_not_formal_addressee",
    "search_engine_absence_not_custody_absence_v170",
}
assert required_breaks <= {row["break_id"] for row in method_breaks}

keys = rows("E0_REQUEST_SEARCH_KEY_MATRIX_V170.csv")
assert {"SK170_01", "SK170_02", "SK170_03", "SK170_04"} <= {row["key_id"] for row in keys}
objects = rows("E0_V170_REQUEST_OBJECTS.csv")
assert {"RO170_01", "RO170_02", "RO170_03"} <= {row["row_id"] for row in objects}
assert all(row["status"] == "DRAFT_NOT_SENT" for row in objects)
assert rows("E0_V170_REQUEST_OBJECTS.csv") == rows("E0_V170_REQUEST_OBJECTS_V170.csv")

for name in (
    "REQUEST_AGN_2018_REPLY_V170.md", "REQUEST_BCRA_CRYL_SETTLEMENT_V170.md",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V170.md", "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V170.md",
    "REQUEST_CNV_CUSTODY_RECORDS_V170.md", "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V170.md",
):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "DRAFT_NOT_SENT" in text or "BORRADOR_NO_ENVIADO" in text
assert "Adenda V170 · receptor contextual CGN" in (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V170.md").read_text(encoding="utf-8-sig")
assert "Adenda V170 · receptor contextual CGN" in (HERE / "REQUEST_SUBMISSION_CHECKLIST_V170.md").read_text(encoding="utf-8-sig")

panel = rows("FOUR_LEG_PASS_PANEL_V170.csv")
assert len(panel) == 45
assert sum(row["system_panel_eligible_v72"] == "YES_EXACT_Q4_TARGET_BASIS" for row in panel) == 34
coverage = rows("STRICT_Q4_FOUR_LEG_COVERAGE_V170.csv")
assert len(coverage) == 1 and coverage[0]["asset_coverage_pct"] == COVERAGE
assert coverage[0]["asset_numerator_million_ars"] == "61345602.215"
assert coverage[0]["system_assets_million_ars"] == "96697695.5"

bundle = rows("V170_SOURCE_BUNDLE.csv")
assert len(bundle) == 4
for row in bundle:
    path = REPO / row["path"].lstrip("/")
    assert path.is_file() and path.stat().st_size == int(row["bytes"]) and sha256(path) == row["sha256"]

sync = CYCLE / "inputs/source_sync/v170"
sync_rows = list(csv.DictReader((sync / "SOURCE_SYNC_FILE_MANIFEST_V170.csv").open(encoding="utf-8-sig", newline="")))
assert len(sync_rows) == 1 and sync_rows[0]["relative_path"] == new["archivo_local"]

manifest = json.loads((HERE / "MANIFEST_V170.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V170" and manifest["parent_checkpoint"] == "V169"
assert manifest["exact_entities"] == 34 and manifest["strict_coverage_pct"] == COVERAGE
assert manifest["requests_submitted"] == 0 and manifest["new_promotions"] == []
assert manifest["commoncrawl_collections_2013_2020"] == 74 and manifest["commoncrawl_evaluable_results_v170"] == 0
assert manifest["note_3672_contextual_recipient"] == "CGN"
assert manifest["note_3672_formal_addressee"] == "NOT_LOCATED"
assert manifest["note_3672_recipient_identifier"] == "NOT_LOCATED"
for row in manifest["files"]:
    path = HERE / row["path"]
    assert path.is_file() and path.stat().st_size == row["bytes"] and sha256(path) == row["sha256"]

readme = (HERE / "README_V170.md").read_text(encoding="utf-8-sig")
assert "597/597" in readme and "74 colecciones" in readme and "4 errores" in readme
assert "CGN identificada como receptora contextual" in readme
assert "seis borradores no enviados" in readme and "solicitudes enviadas 0" in readme
assert "SAF355 0/5" in readme and "ejecución 0/10" in readme

print("V170 QA PASS · 597/597 · cc=74 · exact_queries=4/4_errors · false_positive_rows=8 · recipient=CGN_CONTEXTUAL · panel=34 · requests=0 · SAF355=0/5 · execution=0/10")
