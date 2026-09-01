from pathlib import Path
import csv
import hashlib
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
COVERAGE = "63.4406041403540997520463142785031521252747951992299547614348265414453439585848248058817492708499966268585997481191265825"
NEW_IDS = {
    "e0_cgn_disposition_41_1996_mandatory_entry_and_internal_pass_registry_v171",
    "e0_cgn_circular_04_2010_comdoc_transition_and_note_route_v171",
}


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
assert len(catalog) == 599 and len({row["id"] for row in catalog}) == 599
new = [row for row in catalog if row["id"] in NEW_IDS]
assert len(new) == 2
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    assert path.is_file() and sha256(path) == row["sha256"].lower()
for row in new:
    path = REPO / row["archivo_local"].lstrip("/")
    text = path.read_text(encoding="cp1252", errors="replace")
    assert "Contadur" in text and "Mesa de Entradas" in text
assert {Path(row["archivo_local"]).name for row in new} == {
    "cgn_disposition_41_1996_mesa_entradas_registry.html",
    "cgn_circular_04_2010_comdoc_note_routes.html",
}

audit = list(csv.DictReader((AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V171.csv").open(encoding="utf-8-sig", newline="")))
assert len(audit) == 599 and all(row["exists"] == "True" and row["hash_ok"] == "True" for row in audit)
assert (AUDIT / "SOURCE_PRESERVATION_MISSING_V171.csv").read_text(encoding="utf-8-sig").count("\n") == 1

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V171.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V171"
assert complete["master_catalog_entries"] == complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 599
assert complete["remaining_catalog_physical_or_hash_gaps"] == 0
assert complete["commoncrawl_exact_prefix_queries_v171"] == 40
assert complete["commoncrawl_valid_no_capture_v171"] == 4
assert complete["commoncrawl_service_errors_v171"] == 36
assert complete["commoncrawl_capture_rows_v171"] == 0
assert complete["commoncrawl_2016_remaining_queries_deferred"] == 14
assert complete["plan_sigen_2009_exact_filenames_searched_v171"] == 14
assert complete["plan_sigen_2009_bodies_located_v171"] == 0
assert complete["note_3672_primary_recipient_registry_route_located"] is True
assert complete["note_3672_internal_pass_registry_duty_located"] is True
assert complete["comdoc_exclusive_for_2009_rejected"] is True
assert complete["historical_server_tls_certificate_expired_disclosed"] is True
assert complete["note_3672_09_body_located"] is False
assert complete["note_3672_formal_addressee_located"] is False
assert complete["note_3672_recipient_identifier_located"] is False
assert complete["requests_submitted"] == 0 and complete["responses_received"] == 0
assert complete["saf355_certifications_located"] == 0 and complete["executed_historical_bank_rows_confirmed"] == 0

execution = rows("E0_COMMONCRAWL_EXACT_PREFIX_EXECUTION_V171.csv")
assert len(execution) == 40
assert sum(row["classification"] == "NO_CAPTURE_VALID" for row in execution) == 4
assert sum(row["classification"] == "SERVICE_ERROR" for row in execution) == 36
assert sum(row["evidentiary_effect"] == "SCOPED_NO_CAPTURE_FOR_COLLECTION_HOST" for row in execution) == 4
assert {row["run_scope"] for row in execution} == {"2014_FULL", "2015_FULL", "2016_BOUNDARY"}
negatives = [row for row in execution if row["classification"] == "NO_CAPTURE_VALID"]
assert {row["collection"] for row in negatives} == {"CC-MAIN-2014-49", "CC-MAIN-2014-52"}
assert all(row["http_status"] == "404" and "No Captures found" in row["response"] for row in negatives)

summary = rows("E0_COMMONCRAWL_QUERY_COMPLETENESS_V171.csv")
total = next(row for row in summary if row["batch"] == "V171_TOTAL")
assert total["queries"] == "40" and total["valid_no_capture"] == "4" and total["service_errors"] == "36" and total["captures"] == "0"
boundary = next(row for row in summary if row["batch"] == "2016_BOUNDARY")
assert boundary["pending_queries"] == "14" and "DEFERRED" in boundary["decision"]

coverage_rows = rows("E0_COMMONCRAWL_COLLECTION_COVERAGE_V171.csv")
assert len(coverage_rows) == 74 and len({row["collection_id"] for row in coverage_rows}) == 74
assert sum(row["exact_prefix_status"] == "NO_CAPTURE_VALID_2_HOSTS" for row in coverage_rows) == 2
assert sum(row["exact_prefix_status"] == "DEFERRED_AFTER_4_OF_4_BOUNDARY_ERRORS" for row in coverage_rows) == 7

filenames = rows("E0_PLAN_2009_EXACT_FILENAME_PUBLIC_SEARCH_V171.csv")
assert len(filenames) == 14 and len({row["target"] for row in filenames}) == 14
assert all(row["classification"] == "SEARCH_ENGINE_NEGATIVE_SCOPED" for row in filenames)
assert {"Plan SIGEN 2009.pdf", "planred2009.pdf", "Anexo G - Capacitacion 2009.pdf"} <= {row["target"] for row in filenames}
assert sum(row["target"].startswith("Anexo F - Cuadro") for row in filenames) == 11

registry = rows("E0_CGN_LEGACY_NOTE_REGISTRY_ROUTE_V171.csv")
assert len(registry) == 6
assert {"PRIMARY_RECIPIENT_REGISTRY_IDENTIFIED", "INTERNAL_PASS_LOG_DUTY_IDENTIFIED", "COMDOC_TEMPORAL_BOUNDARY", "NOTE_ROUTE_CONTINUITY", "TESTABLE_REGISTRY_QUERY"} <= {row["status"] for row in registry}

note = rows("E0_NOTE_3672_ARCHIVAL_SEARCH_V171.csv")
assert {"PRIMARY_REGISTRY_DUTY_LOCATED_RECORD_OPEN", "PASS_HISTORY_ROUTE_LOCATED", "COMDOC_EXCLUSIVITY_REJECTED"} <= {row["status"] for row in note}
approval = rows("E0_PLAN_2009_APPROVAL_ACT_SEARCH_V171.csv")
assert {"AA171_20", "AA171_21"} <= {row["test_id"] for row in approval}
assert next(row for row in approval if row["test_id"] == "AA171_21")["classification"] == "EXISTENCE_DATE_CONFIRMED_ACT_OPEN"

keys = rows("E0_REQUEST_SEARCH_KEY_MATRIX_V171.csv")
assert {"SK171_20", "SK171_21", "SK171_22", "SK171_23"} <= {row["key_id"] for row in keys}
objects = rows("E0_V171_REQUEST_OBJECTS.csv")
assert {"RO171_20", "RO171_21", "RO171_22"} <= {row["row_id"] for row in objects}
assert all(row["status"] == "DRAFT_NOT_SENT" for row in objects)
assert rows("E0_V171_REQUEST_OBJECTS.csv") == rows("E0_V171_REQUEST_OBJECTS_V171.csv")

breaks = rows("E0_FISCAL_METHOD_BREAKS_V171.csv")
required_breaks = {
    "valid_404_json_no_capture_not_transport_error_v171", "boundary_failure_stops_batch_v171",
    "mandatory_registry_route_not_target_record_v171", "comdoc_2010_not_exclusive_for_2009_v171",
    "tls_expired_transport_must_be_disclosed_v171",
}
assert required_breaks <= {row["break_id"] for row in breaks}

for name in (
    "REQUEST_AGN_2018_REPLY_V171.md", "REQUEST_BCRA_CRYL_SETTLEMENT_V171.md",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V171.md", "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V171.md",
    "REQUEST_CNV_CUSTODY_RECORDS_V171.md", "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V171.md",
):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "DRAFT_NOT_SENT" in text or "BORRADOR_NO_ENVIADO" in text
assert "Adenda V171 · registro obligatorio CGN" in (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V171.md").read_text(encoding="utf-8-sig")
assert "Adenda V171 · registro obligatorio CGN" in (HERE / "REQUEST_SUBMISSION_CHECKLIST_V171.md").read_text(encoding="utf-8-sig")

panel = rows("FOUR_LEG_PASS_PANEL_V171.csv")
assert len(panel) == 45 and sum(row["system_panel_eligible_v72"] == "YES_EXACT_Q4_TARGET_BASIS" for row in panel) == 34
coverage = rows("STRICT_Q4_FOUR_LEG_COVERAGE_V171.csv")
assert len(coverage) == 1 and coverage[0]["asset_coverage_pct"] == COVERAGE
assert coverage[0]["asset_numerator_million_ars"] == "61345602.215"
assert coverage[0]["system_assets_million_ars"] == "96697695.5"

bundle = rows("V171_SOURCE_BUNDLE.csv")
assert len(bundle) == 6
for row in bundle:
    path = REPO / row["path"].lstrip("/")
    assert path.is_file() and path.stat().st_size == int(row["bytes"]) and sha256(path) == row["sha256"]

sync = CYCLE / "inputs/source_sync/v171"
sync_rows = list(csv.DictReader((sync / "SOURCE_SYNC_FILE_MANIFEST_V171.csv").open(encoding="utf-8-sig", newline="")))
assert len(sync_rows) == 2 and {row["relative_path"] for row in sync_rows} == {row["archivo_local"] for row in new}
prov = rows("ARCHIVAL_PROVENANCE_V171.csv")
prov_new = [row for row in prov if row["source_id"] in NEW_IDS]
assert len(prov_new) == 2 and all(row["cdx_digest"] == "N/A_DIRECT_TLS_CERT_EXPIRED_INSECURE_TRANSPORT" for row in prov_new)

manifest = json.loads((HERE / "MANIFEST_V171.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V171" and manifest["parent_checkpoint"] == "V170"
assert manifest["exact_entities"] == 34 and manifest["strict_coverage_pct"] == COVERAGE
assert manifest["requests_submitted"] == 0 and manifest["new_promotions"] == []
assert manifest["commoncrawl_queries_v171"] == 40
assert manifest["commoncrawl_valid_negatives_v171"] == 4
assert manifest["commoncrawl_service_errors_v171"] == 36
assert manifest["commoncrawl_captures_v171"] == 0
assert manifest["note_3672_primary_registry_route"] == "LOCATED"
assert manifest["note_3672_09_body"] == "NOT_LOCATED"
assert manifest["comdoc_2009_exclusivity"] == "REJECTED"
for row in manifest["files"]:
    path = HERE / row["path"]
    assert path.is_file() and path.stat().st_size == row["bytes"] and sha256(path) == row["sha256"]

readme = (HERE / "README_V171.md").read_text(encoding="utf-8-sig")
assert "599/599" in readme and "40 consultas" in readme and "4 negativos" in readme and "36 errores" in readme
assert "14 nombres exactos" in readme and "registro de pases" in readme
assert "seis borradores no enviados" in readme and "solicitudes enviadas 0" in readme
assert "SAF355 0/5" in readme and "ejecución 0/10" in readme

print("V171 QA PASS · 599/599 · new=2 · cc=40/4-valid-negative/36-error/0-capture · filenames=14 · CGN_REGISTRY_ROUTE=LOCATED · panel=34 · requests=0 · SAF355=0/5 · execution=0/10")
