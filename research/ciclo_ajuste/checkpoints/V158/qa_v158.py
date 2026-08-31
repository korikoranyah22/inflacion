from pathlib import Path
import csv
import hashlib
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v158" / "binaries"


def rows(name):
    with (HERE / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


new_ids = {
    "e0_res_sigen_7_2003_uai_plan_preliminary_final_approval_custody",
    "e0_orsna_act_16_2008_plan_2009_approval_workflow_comparator",
    "e0_decree_2025_2008_economy_production_reorganization",
    "e0_decree_2102_2008_transitional_uai_economy_control",
    "e0_cgn_account_2009_sigen_planning_supervision_count_120",
    "e0_eras_2009_supervision_report_delivery_note_and_file",
}

with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as handle:
    catalog = list(csv.DictReader(handle))
assert len(catalog) == 533 and len({row["id"] for row in catalog}) == 533
assert new_ids <= {row["id"] for row in catalog}

census = {row["source_id"]: row for row in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V158.csv")}
provenance = {row["source_id"]: row for row in rows("ARCHIVAL_PROVENANCE_V158.csv")}
assert len(census) == 293 and new_ids <= set(census) and new_ids <= set(provenance)
for source_id in new_ids:
    path = REPO / census[source_id]["local_path"].lstrip("/")
    assert path.is_file() and digest(path) == census[source_id]["sha256"]
    assert "/v158/binaries/" in census[source_id]["local_path"]
assert census["e0_res_sigen_7_2003_uai_plan_preliminary_final_approval_custody"]["use_status"] == "E0_USABLE_EXACT_UAI_PLAN_VERSION_AND_CUSTODY_WORKFLOW"
assert census["e0_cgn_account_2009_sigen_planning_supervision_count_120"]["use_status"] == "E0_USABLE_CONTEMPORARY_OFFICIAL_COUNT_CONFLICT"

bundle = rows("E0_V158_SOURCE_BUNDLE.csv")
assert len(bundle) == 6 and all(row["catalogued"] == "YES" and row["preserved"] == "YES" for row in bundle)
assert {row["role"] for row in bundle} == {
    "EXACT_UAI_PLAN_VERSION_APPROVAL_AND_CUSTODY_WORKFLOW",
    "CONTEMPORARY_PLAN_APPROVAL_WORKFLOW_COMPARATOR",
    "EXACT_REORGANIZATION_DATE_AND_ECONOMY_SCOPE",
    "TRANSITIONAL_UAI_CONTROL_AND_SUCCESSION_RULE",
    "OFFICIAL_120_COUNT_SIDE_OF_FROZEN_CONFLICT",
    "SUPERVISION_NOTE_REPORT_RECIPIENT_FILE_COMPARATOR",
}
for row in bundle:
    path = BIN / row["filename"]
    assert path.is_file() and path.stat().st_size == int(row["bytes"])
    assert digest(path) == row["sha256"]

workflow = rows("E0_PLAN_2009_PRELIMINARY_FINAL_APPROVAL_WORKFLOW_V158.csv")
assert len(workflow) == 20
assert {"RULE_DOCUMENTED", "EXPECTED_TARGET_CONTAINER", "TARGET_ACT_OPEN", "TARGET_CUSTODY_ROUTE",
        "COMPARATOR_ONLY", "METHOD_LIMIT"} <= {row["status"] for row in workflow}
assert any(row["date_or_deadline"] == "antes del 30/10/2008" and "Plan UAI Economía" in row["target_request"] for row in workflow)
assert any(row["date_or_deadline"] == "hasta el 15/12/2008" and "copia magnética" in row["record_or_action"] for row in workflow)
assert any(row["stage"] == "Custodia" and "versión definitiva" in row["record_or_action"] for row in workflow)

reorganization = rows("E0_UAI_ECONOMY_2009_REORGANIZATION_VERSION_CHAIN_V158.csv")
assert len(reorganization) == 16
assert {"EXACT_REORGANIZATION_DATE", "SUBSTANTIVE_SCOPE", "TRANSITIONAL_RULE",
        "TARGET_VERSION_OPEN", "REQUEST_TARGET", "METHOD_LIMIT"} <= {row["status"] for row in reorganization}
assert any(row["date_or_period"] == "25/11/2008" and row["event"] == "Deuda pública" for row in reorganization)
assert any(row["date_or_period"] == "04/12/2008" and row["event"] == "Control UAI transitorio" for row in reorganization)

conflict = rows("E0_PLANNING_SUPERVISION_COUNT_CONFLICT_V158.csv")
assert len(conflict) == 12
assert {"OFFICIAL_COUNT_A", "OFFICIAL_COUNT_B", "DERIVED_DIAGNOSTIC", "HYPOTHESIS_ONLY",
        "REQUEST_TARGET", "CONFLICT_FROZEN"} <= {row["status"] for row in conflict}
assert {(row["source"], row["normalized_reading"]) for row in conflict[:2]} == {
    ("Cuenta de Inversión 2009, Jurisdicción 20 SIGEN", "120 aproximado"),
    ("Memoria SIGEN 2009", "160 aproximado"),
}
assert any(row["status"] == "CONFLICT_FROZEN" and row["period"] == "No seleccionar cifra" for row in conflict)

delivery = rows("E0_SUPERVISION_REPORT_DELIVERY_METADATA_V158.csv")
assert len(delivery) == 12
assert {"COMPARATOR_METADATA", "CUSTODY_ROUTE", "SEARCH_KEY", "METHOD_RULE",
        "TARGET_OPEN", "METHOD_LIMIT"} <= {row["status"] for row in delivery}
assert any(row["identifier"] == "5095/2009-GSPF" for row in delivery)
assert any(row["identifier"] == "878-09" for row in delivery)

assert len(rows("E0_2008_2009_PLAN_SISIO_APPROVAL_CHAIN_V158.csv")) == 22
assert len(rows("E0_ACCOUNT_AUDIT_HORIZONTAL_PROGRAM_2008_2010_V158.csv")) == 18
assert len(rows("E0_SISIO_SISPE_SYSTEM_SEPARATION_V158.csv")) == 12
assert len(rows("E0_PLANNING_SUPERVISION_REPORT_INVENTORY_V158.csv")) == 15
assert len(rows("E0_ARCHIVE_DIGITAL_REORDERING_AND_DISPOSITION_V158.csv")) == 12

negative = rows("E0_V158_PUBLIC_SEARCH_NEGATIVE_RESULTS.csv")
assert len(negative) == 14 and negative == rows("E0_V158_PUBLIC_SEARCH_NEGATIVE_RESULTS_V158.csv")
assert {"PLAN_AND_ACT_NOT_LOCATED", "PLAN_FILE_NOT_LOCATED", "PRELIMINARY_CHAIN_NOT_LOCATED",
        "DUAL_SUPPORT_NOT_LOCATED", "DEFINITIVE_VERSION_NOT_LOCATED",
        "REORGANIZATION_CROSSWALK_NOT_LOCATED", "SUPERVISION_DELIVERY_CHAIN_NOT_LOCATED",
        "COUNT_CONFLICT_UNRESOLVED", "TARGET_CERTIFICATES_NOT_LOCATED",
        "BANK_EXECUTION_NOT_LOCATED", "DRAFT_NOT_SENT"} <= {row["status"] for row in negative}

breaks = rows("E0_FISCAL_METHOD_BREAKS_V158.csv")
trace = rows("E0_INFORMATION_REQUEST_TRACEABILITY_V158.csv")
keys = rows("E0_REQUEST_SEARCH_KEY_MATRIX_V158.csv")
objects = rows("E0_V158_REQUEST_OBJECTS.csv")
assert len(breaks) == 329
assert {
    "uai_plan_submission_not_final_plan", "preliminary_approval_not_final_approval",
    "superior_conformity_not_sigen_final_approval", "paper_plan_not_magnetic_copy",
    "definitive_plan_custodian_not_uai_only", "pre_reorganization_name_not_post_reorganization_version",
    "transitional_uai_control_not_target_scope_transfer", "official_count_120_not_official_count_160",
    "approximate_count_not_exact_inventory", "comparator_act_copy_error_not_target_chronology",
    "supervision_note_not_attached_report_body", "recipient_file_not_sigen_internal_file",
} <= {row["break_id"] for row in breaks}
assert len(trace) == 426 and all(row["status"] == "DRAFT_NOT_SENT" for row in trace)
assert {"CL158_INITIAL_PLAN", "CL158_PLAN_FILE", "CL158_PRELIMINARY_CHAIN", "CL158_DUAL_SUPPORT",
        "CL158_FINAL_ACT_AND_PLAN", "CL158_REORG_CROSSWALK", "CL158_COUNT_INVENTORY",
        "CL158_COUNT_RULE", "CL158_SUPERVISION_NOTE", "CL158_SUPERVISION_BODY",
        "CL158_RECIPIENT_FILE", "CL158_FINAL_BANK_GATE"} <= {row["gap_id"] for row in trace}
assert len(keys) == 510
assert {"legajo plan auditoría UAI Ministerio de Economía 2009",
        "copia magnética plan UAI Economía 2009",
        "Ministerio de Economía y Finanzas Públicas Plan UAI 2009",
        "aproximadamente 120 informes Supervisión Planeamiento 2009",
        "cerca de 160 informes Supervisión Planeamiento 2009",
        "Nota 5095/2009 GSPF Informe Supervisión UAI",
        "71597 152677 2876 C41 C42 C55 banco reversa"} <= {row["exact_key"] for row in keys}
assert len(objects) == 68 and objects == rows("E0_V158_REQUEST_OBJECTS_V158.csv")
assert all(row["status"] == "DRAFT_NOT_SENT" for row in objects)
assert {"UAI_ECONOMY_PLAN_2009_INITIAL_SUBMISSION", "UAI_ECONOMY_PLAN_2009_PLAN_FILE",
        "UAI_ECONOMY_PLAN_2009_PRELIMINARY_APPROVAL", "UAI_ECONOMY_PLAN_2009_SUPERIOR_CONFORMITY",
        "UAI_ECONOMY_PLAN_2009_PAPER_AND_MAGNETIC_SUBMISSION",
        "UAI_ECONOMY_PLAN_2009_DEFINITIVE_VERSION", "UAI_ECONOMY_PLAN_2009_REORGANIZATION_CROSSWALK",
        "PLANNING_SUPERVISION_2009_COUNT_INVENTORY",
        "PLANNING_SUPERVISION_ECONOMY_2009_DELIVERY_CHAIN"} <= {row["object_id"] for row in objects}

visual = rows("E0_V158_PDF_VISUAL_CONTROL.csv")
images = rows("E0_V158_IMAGE_VISUAL_CONTROL.csv")
assert len(visual) == 142 and len(images) == 3
new_visual = [row for row in visual if row["control_id"].startswith("PV158_")]
assert len(new_visual) == 5 and all(row["result"] == "PASS" for row in visual + images)
assert {(row["source_id"], row["pdf_page"]) for row in new_visual} == {
    ("e0_res_sigen_7_2003_uai_plan_preliminary_final_approval_custody", "32"),
    ("e0_res_sigen_7_2003_uai_plan_preliminary_final_approval_custody", "33"),
    ("e0_res_sigen_7_2003_uai_plan_preliminary_final_approval_custody", "34"),
    ("e0_orsna_act_16_2008_plan_2009_approval_workflow_comparator", "4"),
    ("e0_eras_2009_supervision_report_delivery_note_and_file", "1"),
}

register = rows("E0_REQUEST_RESPONSE_REGISTER_V158.csv")
assert len(register) == 6
assert all(row["status"] == "DRAFT_NOT_SENT" and row["submitted_on"] == "N/A"
           and row["submission_channel"] == "N/A" and row["receipt_or_case_id"] == "N/A"
           and row["response_date"] == "N/A" for row in register)
assert all("V158.md" in row["draft_file"] for row in register)
for name in [
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V158.md", "REQUEST_BCRA_CRYL_SETTLEMENT_V158.md",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V158.md", "REQUEST_AGN_2018_REPLY_V158.md",
    "REQUEST_CNV_CUSTODY_RECORDS_V158.md", "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V158.md",
]:
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "BORRADOR_NO_ENVIADO" in text or "DRAFT_NOT_SENT" in text
econ = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V158.md").read_text(encoding="utf-8-sig")
assert "legajo plan auditoría UAI" in econ and "papel" in econ and "copia magnética" in econ
assert "aproximadamente 120" in econ and "cerca de 160" in econ

with (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V158.csv").open(encoding="utf-8-sig", newline="") as handle:
    hashes = list(csv.DictReader(handle))
assert len(hashes) == 533
assert sum(row["exists"] == "True" for row in hashes) == 527
assert sum(row["hash_ok"] == "True" for row in hashes) == 527

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V158.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V158" and complete["master_catalog_entries"] == 533
assert complete["e0_primary_sources_preserved"] == 293
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 527
assert complete["remaining_physical_gaps"] == 6
assert complete["e0_fiscal_method_breaks_frozen"] == 329
assert complete["e0_request_traceability_rows"] == 426 and complete["e0_request_search_keys"] == 510
assert complete["e0_v158_pdf_visual_controls"] == 142 and complete["e0_v158_new_pdf_visual_controls"] == 5
assert complete["e0_v158_total_visual_controls"] == 145 and complete["e0_v158_source_bundle_files"] == 6
assert complete["e0_v158_preliminary_final_workflow_rows"] == 20
assert complete["e0_v158_reorganization_version_rows"] == 16
assert complete["e0_v158_supervision_count_conflict_rows"] == 12
assert complete["e0_v158_supervision_delivery_metadata_rows"] == 12
for flag in [
    "e0_res_sigen_7_2003_plan_workflow_located",
    "e0_uai_plan_initial_deadline_2008_10_30_located",
    "e0_uai_plan_final_deadline_2008_12_15_located",
    "e0_uai_plan_dual_paper_magnetic_support_rule_located",
    "e0_uai_plan_definitive_version_custodian_located",
    "e0_economy_production_reorganization_date_located",
    "e0_public_debt_and_finance_remained_economy_after_reorganization",
    "e0_supervision_2009_official_120_160_count_conflict_frozen",
    "e0_supervision_note_report_recipient_file_separation_proven_by_comparator",
]:
    assert complete[flag] is True
for flag in [
    "e0_plan_sigen_2009_body_located", "e0_plan_sigen_2009_approval_act_located",
    "e0_uai_economy_plan_2009_subplan_located", "e0_uai_economy_plan_2009_plan_file_located",
    "e0_uai_economy_plan_2009_initial_submission_located",
    "e0_uai_economy_plan_2009_preliminary_approval_located",
    "e0_uai_economy_plan_2009_superior_conformity_located",
    "e0_uai_economy_plan_2009_definitive_version_located",
    "e0_uai_economy_plan_2009_reorganization_crosswalk_located",
    "e0_supervision_2009_count_inventory_located",
    "e0_uai_economy_planning_supervision_report_2009_located",
    "e0_uai_economy_planning_supervision_delivery_note_located",
    "e0_uai_economy_planning_supervision_recipient_file_located",
]:
    assert complete[flag] is False
assert complete["e0_uai_saf355_target_certifications_located_count"] == 0
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == complete["e0_request_responses_received"] == 0

manifest = json.loads((HERE / "MANIFEST_V158.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V158" and manifest["parent_checkpoint"] == "V157"
assert manifest["new_preserved_sources"] == 6 and manifest["source_bundle_files"] == 6
assert manifest["fiscal_method_breaks"] == 329 and manifest["request_traceability_rows"] == 426
assert manifest["request_search_keys"] == 510 and manifest["request_objects"] == 68
assert manifest["pdf_visual_controls_total"] == 142 and manifest["pdf_visual_controls_new"] == 5
assert manifest["preliminary_final_workflow_rows"] == 20
assert manifest["reorganization_version_rows"] == 16
assert manifest["supervision_count_conflict_rows"] == 12
assert manifest["supervision_delivery_metadata_rows"] == 12
assert manifest["supervision_2009_official_120_160_count_conflict_frozen"] is True
assert manifest["supervision_2009_count_inventory_located"] is False
assert manifest["uai_economy_definitive_plan_version_2009_located"] is False
assert manifest["executed_settlement_rows_confirmed"] == 0
assert manifest["requests_submitted"] == manifest["responses_received"] == 0

for item in manifest["files"]:
    path = HERE / item["path"]
    assert path.is_file() and path.stat().st_size == item["bytes"] and digest(path) == item["sha256"]

for name in ["README_V158.md", "VEREDICTO_V158.md", "E0_FISCAL_RECONSTRUCTION_V158.md",
             "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V158_A_V159.md"]:
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")
assert not (HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V158_A_V158.md").exists()

combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined and "TARGET_EXTRACT_FOUND" not in combined

print("V158 QA PASS")
