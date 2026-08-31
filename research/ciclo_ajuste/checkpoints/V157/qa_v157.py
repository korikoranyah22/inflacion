from pathlib import Path
import csv
import hashlib
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v157" / "binaries"


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
    "e0_sigen_memory_2008_plan_2009_approval_and_uai_supervision",
    "e0_infoleg_plan_sigen_2008_target_account_horizontal_program",
    "e0_infoleg_plan_sigen_2010_part1_risk_and_archive_digital",
    "e0_infoleg_plan_sigen_2010_part2_sisio_snapshot_and_account_horizontal",
    "e0_cgn_account_2010_sigen_output_and_planning_supervision",
}

with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as handle:
    catalog = list(csv.DictReader(handle))
assert len(catalog) == 527 and len({row["id"] for row in catalog}) == 527
assert new_ids <= {row["id"] for row in catalog}

census = {row["source_id"]: row for row in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V157.csv")}
provenance = {row["source_id"]: row for row in rows("ARCHIVAL_PROVENANCE_V157.csv")}
assert len(census) == 287 and new_ids <= set(census) and new_ids <= set(provenance)
for source_id in new_ids:
    path = REPO / census[source_id]["local_path"].lstrip("/")
    assert path.is_file() and digest(path) == census[source_id]["sha256"]
    assert "/v157/binaries/" in census[source_id]["local_path"]
assert census["e0_sigen_memory_2008_plan_2009_approval_and_uai_supervision"]["use_status"] == "E0_USABLE_CONTEMPORARY_PLAN_APPROVAL_SUPERVISION_AND_ARCHIVE_CHAIN"
assert census["e0_infoleg_plan_sigen_2010_part2_sisio_snapshot_and_account_horizontal"]["use_status"] == "E0_USABLE_EXACT_SISIO_PLANNING_SNAPSHOT_SCHEMA_AND_DATE"

bundle = rows("E0_V157_SOURCE_BUNDLE.csv")
assert len(bundle) == 5 and all(row["catalogued"] == "YES" and row["preserved"] == "YES" for row in bundle)
assert {row["role"] for row in bundle} == {
    "TARGET_PLAN_APPROVAL_SUPERVISION_AND_ARCHIVE", "TARGET_PERIOD_HORIZONTAL_ACCOUNT_PROGRAM",
    "NEAR_TARGET_RISK_AND_ARCHIVE_COMPARATOR", "EXACT_SISIO_PLANNING_CUTOFF_AND_SCHEMA",
    "PLANNING_SUPERVISION_RECORD_CONTINUITY",
}
for row in bundle:
    path = BIN / row["filename"]
    assert path.is_file() and path.stat().st_size == int(row["bytes"])
    assert digest(path) == row["sha256"]

plan = rows("E0_2008_2009_PLAN_SISIO_APPROVAL_CHAIN_V157.csv")
assert len(plan) == 22
assert {"EXACT_APPROVAL_DATE", "EXACT_SYSTEM_CUTOFF", "TARGET_REPORT_REFERENCE",
        "VERSION_CONTROL", "METHOD_LIMIT"} <= {row["status"] for row in plan}
assert any(row["date_or_period"] == "2008-12-15" and "Plan SIGEN 2009" in row["documented_event"] for row in plan)
assert any(row["date_or_period"] == "2009-12-16" and "SISIO WEB II" in row["documented_event"] for row in plan)
assert any("seis días" in row["documented_event"] for row in plan)

account = rows("E0_ACCOUNT_AUDIT_HORIZONTAL_PROGRAM_2008_2010_V157.csv")
assert len(account) == 18
assert {"PROGRAM_LOCATED", "CONTRIBUTOR_RECORD", "GLOBAL_RECORD", "TARGET_REPORT_REFERENCE",
        "TARGET_CERTIFICATION", "METHOD_LIMIT"} <= {row["status"] for row in account}
assert any(row["year"] == "2008" and row["modality"] == "Auditoría horizontal planificada" for row in account)
assert any(row["year"] == "2008 informado 2009" and row["status"] == "TARGET_REPORT_REFERENCE" for row in account)

systems = rows("E0_SISIO_SISPE_SYSTEM_SEPARATION_V157.csv")
assert len(systems) == 12
assert {"SISIO WEB", "SISIO WEB II", "SISPE", "Archivo Digital",
        "SISIO versus SISPE", "SISIO versus Archivo Digital"} <= {row["system"] for row in systems}
assert any(row["system"] == "Regla final" and row["status"] == "METHOD_LIMIT" for row in systems)

supervision = rows("E0_PLANNING_SUPERVISION_REPORT_INVENTORY_V157.csv")
assert len(supervision) == 15
counts = {(row["year"], row["documented_count"]) for row in supervision if row["status"] == "COUNT_DOCUMENTED"}
assert {("2008", "cerca de 120"), ("2009", "cerca de 160"), ("2010", "aproximadamente 140")} <= counts
assert {"COUNT_DOCUMENTED", "PLAN_RECORD", "CONSOLIDATED_PLAN", "EXECUTION_RECORD",
        "AUDIT_RECORD", "WORKPAPER_RECORD", "METHOD_LIMIT"} <= {
    row["status"] for row in supervision
}

archive = rows("E0_ARCHIVE_DIGITAL_REORDERING_AND_DISPOSITION_V157.csv")
assert len(archive) == 12
assert {"ARCHIVE_CAPABILITY", "ARCHIVE_PROGRAM", "ARCHIVE_EXECUTION", "ARCHIVE_REGISTER",
        "DISPOSITION_CONTROL", "METHOD_LIMIT"} <= {row["status"] for row in archive}
assert any("Proyecto no destrucción" in row["limit"] for row in archive)

negative = rows("E0_V157_PUBLIC_SEARCH_NEGATIVE_RESULTS.csv")
assert len(negative) == 12 and negative == rows("E0_V157_PUBLIC_SEARCH_NEGATIVE_RESULTS_V157.csv")
assert {"PLAN_BODY_NOT_LOCATED", "APPROVAL_ACT_NOT_LOCATED", "UAI_SUBPLAN_NOT_LOCATED",
        "SUPERVISION_REPORT_NOT_LOCATED", "SYSTEM_SNAPSHOT_NOT_LOCATED",
        "ARCHIVE_ENTRY_NOT_LOCATED", "DISPOSITION_RECORD_NOT_LOCATED",
        "TARGET_CERTIFICATES_NOT_LOCATED", "BANK_EXECUTION_NOT_LOCATED", "DRAFT_NOT_SENT"} <= {
    row["status"] for row in negative
}

breaks = rows("E0_FISCAL_METHOD_BREAKS_V157.csv")
trace = rows("E0_INFORMATION_REQUEST_TRACEABILITY_V157.csv")
keys = rows("E0_REQUEST_SEARCH_KEY_MATRIX_V157.csv")
objects = rows("E0_V157_REQUEST_OBJECTS.csv")
assert len(breaks) == 317
assert {
    "plan_sigen_2009_approval_not_uai_economy_subplan_body", "umbrella_plan_not_project_execution",
    "horizontal_account_audit_not_target_saf355_certificate", "sisio_plan_snapshot_not_observation_entry",
    "sisio_not_sispe", "planning_supervision_report_not_audit_report",
    "aggregate_product_count_not_inventoried_products", "archive_digital_project_not_target_digitization",
    "archive_reordering_not_retention", "depuration_process_not_proof_of_destruction",
} <= {row["break_id"] for row in breaks}
assert len(trace) == 408 and all(row["status"] == "DRAFT_NOT_SENT" for row in trace)
assert {"CL157_PLAN_2009_BODY", "CL157_PLAN_2009_ACT", "CL157_UAI_ECON_PLAN",
        "CL157_PLANNING_SUPERVISION", "CL157_SISIO_PLAN_SNAPSHOT", "CL157_DIGITAL_ARCHIVE_INDEX",
        "CL157_DEPURATION_PROCESS", "CL157_FINAL_BANK_GATE"} <= {row["gap_id"] for row in trace}
assert len(keys) == 486
assert {"Plan SIGEN 2009 aprobado 15/12/2008", "Plan UAI Ministerio de Economía 2009",
        "Informe de Supervisión del Planeamiento UAI Economía 2009",
        "SISIO WEB II corte 16-12-2009", "SISPE Plan SIGEN 2009 Cuenta de Inversión",
        "71597 152677 2876 C41 C42 C55 banco reversa"} <= {row["exact_key"] for row in keys}
assert len(objects) == 56 and objects == rows("E0_V157_REQUEST_OBJECTS_V157.csv")
assert all(row["status"] == "DRAFT_NOT_SENT" for row in objects)
assert {"PLAN_SIGEN_2009_BODY", "PLAN_SIGEN_2009_APPROVAL_ACT", "UAI_ECONOMY_PLAN_2009_SUBPLAN",
        "SISIO_PLAN_2009_SNAPSHOT", "PLANNING_SUPERVISION_REPORT_ECONOMY_2009",
        "LINEAMIENTOS_PLANEAMIENTO_2009", "ARCHIVE_DIGITAL_INDEX_2008_2009",
        "ARCHIVE_REORDERING_REGISTER_2009", "ARCHIVE_DEPURATION_PROCESS_2010",
        "SISIO_SISPE_ARCHIVE_CROSSWALK"} <= {row["object_id"] for row in objects}

channels = rows("CURRENT_OFFICIAL_SUBMISSION_CHANNELS_V157.csv")
assert len(channels) == 9
assert any("Sindicatura General" in row["institution"] and "DRAFT_NOT_SENT" in row["status"] for row in channels)

visual = rows("E0_V157_PDF_VISUAL_CONTROL.csv")
images = rows("E0_V157_IMAGE_VISUAL_CONTROL.csv")
assert len(visual) == 137 and len(images) == 3
new_visual = [row for row in visual if row["control_id"].startswith("PV157_")]
assert len(new_visual) == 3 and all(row["result"] == "PASS" for row in visual + images)
assert {row["pdf_page"] for row in new_visual} == {"6", "10", "13"}
assert {row["printed_page"] for row in new_visual} == {"5", "9", "12"}
assert all(row["source_id"] == "e0_sigen_memory_2008_plan_2009_approval_and_uai_supervision" for row in new_visual)

register = rows("E0_REQUEST_RESPONSE_REGISTER_V157.csv")
assert len(register) == 6
assert all(row["status"] == "DRAFT_NOT_SENT" and row["submitted_on"] == "N/A"
           and row["receipt_or_case_id"] == "N/A" for row in register)
assert all("V157.md" in row["draft_file"] for row in register)
for name in [
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V157.md", "REQUEST_BCRA_CRYL_SETTLEMENT_V157.md",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V157.md", "REQUEST_AGN_2018_REPLY_V157.md",
    "REQUEST_CNV_CUSTODY_RECORDS_V157.md", "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V157.md",
]:
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "BORRADOR_NO_ENVIADO" in text or "DRAFT_NOT_SENT" in text
econ = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V157.md").read_text(encoding="utf-8-sig")
assert "15/12/2008" in econ and "SISPE" in econ and "Archivo Digital" in econ

with (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V157.csv").open(encoding="utf-8-sig", newline="") as handle:
    hashes = list(csv.DictReader(handle))
assert len(hashes) == 527
assert sum(row["exists"] == "True" for row in hashes) == 521
assert sum(row["hash_ok"] == "True" for row in hashes) == 521

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V157.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V157" and complete["master_catalog_entries"] == 527
assert complete["e0_primary_sources_preserved"] == 287
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 521
assert complete["remaining_physical_gaps"] == 6
assert complete["e0_fiscal_method_breaks_frozen"] == 317
assert complete["e0_request_traceability_rows"] == 408 and complete["e0_request_search_keys"] == 486
assert complete["e0_plan_sigen_2009_approval_date_located"] is True
assert complete["e0_plan_sigen_2009_body_located"] is False
assert complete["e0_plan_sigen_2009_approval_act_located"] is False
assert complete["e0_uai_economy_plan_2009_subplan_located"] is False
assert complete["e0_sisio_2010_plan_cutoff_date_located"] is True
assert complete["e0_sisio_target_plan_snapshot_located"] is False
assert complete["e0_account_2008_horizontal_program_located"] is True
assert complete["e0_target_archive_entry_located"] is False
assert complete["e0_uai_saf355_target_certifications_located_count"] == 0
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == complete["e0_request_responses_received"] == 0

manifest = json.loads((HERE / "MANIFEST_V157.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V157" and manifest["parent_checkpoint"] == "V156"
assert manifest["new_preserved_sources"] == 5 and manifest["source_bundle_files"] == 5
assert manifest["pdf_visual_controls_total"] == 137 and manifest["pdf_visual_controls_new"] == 3
assert manifest["request_objects"] == 56
assert manifest["plan_sigen_2009_approval_date_located"] is True
assert manifest["plan_sigen_2009_body_located"] is False
assert manifest["sisio_2010_cutoff_date_located"] is True
assert manifest["sisio_target_plan_snapshot_located"] is False
assert manifest["account_2008_horizontal_program_located"] is True
assert manifest["executed_settlement_rows_confirmed"] == 0
assert manifest["requests_submitted"] == manifest["responses_received"] == 0

for name in ["README_V157.md", "VEREDICTO_V157.md", "E0_FISCAL_RECONSTRUCTION_V157.md",
             "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V157_A_V158.md"]:
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")
assert not (HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V157_A_V157.md").exists()

combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined and "TARGET_EXTRACT_FOUND" not in combined

print("V157 QA PASS")
