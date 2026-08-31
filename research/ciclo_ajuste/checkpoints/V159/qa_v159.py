from pathlib import Path
import csv
import hashlib
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v159" / "binaries"


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
    "e0_sigen_memoria_2003_gsepfye_area_and_note_suffix",
    "e0_sigen_memoria_2004_supervision_structure_and_record_systems",
    "e0_sigen_memoria_2006_uai_and_output_measure_denominators",
    "e0_eras_act_09_2010_gsepypf_note_report_and_recipient_file",
}

with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as handle:
    catalog = list(csv.DictReader(handle))
assert len(catalog) == 537 and len({row["id"] for row in catalog}) == 537
assert new_ids <= {row["id"] for row in catalog}

census = {row["source_id"]: row for row in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V159.csv")}
provenance = {row["source_id"]: row for row in rows("ARCHIVAL_PROVENANCE_V159.csv")}
assert len(census) == 297 and new_ids <= set(census) and new_ids <= set(provenance)
for source_id in new_ids:
    path = REPO / census[source_id]["local_path"].lstrip("/")
    assert path.is_file() and digest(path) == census[source_id]["sha256"]
    assert "/v159/binaries/" in census[source_id]["local_path"]
assert census["e0_sigen_memoria_2003_gsepfye_area_and_note_suffix"]["use_status"] == "E0_USABLE_CONTEMPORARY_LONG_NAME_AND_GSEPFYE_NOTE_SUFFIX"
assert census["e0_sigen_memoria_2006_uai_and_output_measure_denominators"]["use_status"] == "E0_USABLE_DENOMINATOR_TYPE_COMPARATOR_NOT_2009_CENSUS"

bundle = rows("E0_V159_SOURCE_BUNDLE.csv")
assert len(bundle) == 4 and all(row["catalogued"] == "YES" and row["preserved"] == "YES" for row in bundle)
assert {row["role"] for row in bundle} == {
    "CONTEMPORARY_LONG_NAME_GSEPFYE_AND_STRUCTURE",
    "EXPLICIT_GSEPFYE_STRUCTURE_AND_RECORD_SYSTEM_CAPABILITY",
    "UAI_PROJECT_REPORT_DENOMINATOR_COMPARATOR",
    "NOTE_REPORT_RECIPIENT_FILE_INTERNAL_ROUTING_COMPARATOR",
}
for row in bundle:
    path = BIN / row["filename"]
    assert path.is_file() and path.stat().st_size == int(row["bytes"])
    assert digest(path) == row["sha256"]

acronyms = rows("E0_SIGEN_SUPERVISION_AREA_ACRONYM_TIMELINE_V159.csv")
assert len(acronyms) == 12
assert {"CONTEMPORARY_ASSOCIATION", "EXPLICIT_EXPANSION", "TARGET_TOKEN_ONLY",
        "DISTINCT_INVENTORY_TOKEN", "DISTINCT_NOTE_TOKEN", "POSTERIOR_EXPANSION_ONLY",
        "REQUEST_TARGET", "METHOD_LIMIT"} <= {row["status"] for row in acronyms}
assert any(row["observed_token"] == "GSEyP" and row["status"] == "TARGET_TOKEN_ONLY" for row in acronyms)
assert any(row["observed_token"] == "GSEPFyE; GSEyP; GSEPyPF; GSEPYPF" for row in acronyms)

denominators = rows("E0_UAI_COUNT_REPORT_DENOMINATOR_CONTROL_V159.csv")
assert len(denominators) == 14
assert {"UNIT_COUNT_COMPARATOR", "PROJECT_COUNT_COMPARATOR", "REPORT_CLASS_COMPARATOR",
        "OFFICIAL_COUNT_A", "OFFICIAL_COUNT_B", "DENOMINATOR_SEPARATION",
        "CONFLICT_FROZEN", "TARGET_OPEN", "METHOD_LIMIT"} <= {row["status"] for row in denominators}
assert any(row["published_value"] == "145" and row["unit_of_count"] == "Unidades de Auditoría Interna supervisadas" for row in denominators)
assert any(row["published_value"] == "119" and "Informes de Evaluación" in row["unit_of_count"] for row in denominators)

lifecycle = rows("E0_SUPERVISION_NOTE_RECIPIENT_LIFECYCLE_V159.csv")
assert len(lifecycle) == 12
assert {"COMPARATOR_STAGE", "FOLLOWUP_STAGE", "CUSTODY_RULE", "TARGET_OPEN", "METHOD_LIMIT"} <= {row["status"] for row in lifecycle}
assert any(row["documented_comparator"] == "Nota SIGEN 4712/2010-GSEPYPF" for row in lifecycle)
assert any(row["identifier_or_link"] == "Acta vincula nota, informe y expediente" for row in lifecycle)

nontrans = rows("E0_SAF355_EXCEPTION_CERTIFICATION_NONTRANSPOSITION_V159.csv")
assert len(nontrans) == 12
assert {"SCOPE_EXCEPTION", "TARGET_PERIOD_EXCEPTION", "NEGATIVE_LIMIT", "SPECIAL_ROUTE",
        "CERTIFICATION_OPEN", "NEGATIVE_CONTROL", "CUSTODY_ROUTE", "EVIDENCE_GAP",
        "BANK_GATE", "METHOD_LIMIT"} <= {row["status"] for row in nontrans}
assert any(row["layer"] == "Certificación UAI A4" and "C41, C42, C43, C55" in row["scope"] for row in nontrans)
assert any(row["layer"] == "Resultado actual" and row["scope"] == "0 de 5 certificados ejecutados" for row in nontrans)

assert len(rows("E0_PLAN_2009_PRELIMINARY_FINAL_APPROVAL_WORKFLOW_V159.csv")) == 20
assert len(rows("E0_UAI_ECONOMY_2009_REORGANIZATION_VERSION_CHAIN_V159.csv")) == 16
assert len(rows("E0_PLANNING_SUPERVISION_COUNT_CONFLICT_V159.csv")) == 12
assert len(rows("E0_SUPERVISION_REPORT_DELIVERY_METADATA_V159.csv")) == 12
assert len(rows("E0_2008_2009_PLAN_SISIO_APPROVAL_CHAIN_V159.csv")) == 22
assert len(rows("E0_ACCOUNT_AUDIT_HORIZONTAL_PROGRAM_2008_2010_V159.csv")) == 18
assert len(rows("E0_SISIO_SISPE_SYSTEM_SEPARATION_V159.csv")) == 12
assert len(rows("E0_PLANNING_SUPERVISION_REPORT_INVENTORY_V159.csv")) == 15
assert len(rows("E0_ARCHIVE_DIGITAL_REORDERING_AND_DISPOSITION_V159.csv")) == 12

negative = rows("E0_V159_PUBLIC_SEARCH_NEGATIVE_RESULTS.csv")
assert len(negative) == 17 and negative == rows("E0_V159_PUBLIC_SEARCH_NEGATIVE_RESULTS_V159.csv")
assert {"ACRONYM_IDENTITY_OPEN", "DENOMINATOR_OPEN", "COMPARATOR_FOLLOWUP_OPEN",
        "TARGET_CERTIFICATES_NOT_LOCATED", "BANK_EXECUTION_NOT_LOCATED",
        "DRAFT_NOT_SENT"} <= {row["status"] for row in negative}

breaks = rows("E0_FISCAL_METHOD_BREAKS_V159.csv")
trace = rows("E0_INFORMATION_REQUEST_TRACEABILITY_V159.csv")
keys = rows("E0_REQUEST_SEARCH_KEY_MATRIX_V159.csv")
objects = rows("E0_V159_REQUEST_OBJECTS.csv")
assert len(breaks) == 341
assert {
    "gsepfye_2003_not_gseyp_2009", "gsepypf_2010_not_gseyp_2009",
    "structure_2004_not_structure_2009", "name_variant_not_silent_normalization",
    "uai_count_not_report_count", "project_count_not_report_count",
    "uai_2006_not_uai_2009_census", "recipient_internal_routing_not_response",
    "note_area_suffix_not_report_body", "saf355_general_table_exception_not_registration_exemption",
    "saf355_general_table_exception_not_uai_certificate_exception", "one_custodian_negative_not_chain_closure",
} <= {row["break_id"] for row in breaks}
assert len(trace) == 441 and all(row["status"] == "DRAFT_NOT_SENT" for row in trace)
assert {"CL159_GSEYP_IDENTITY", "CL159_STRUCTURE_SUCCESSION", "CL159_UAI_2009_CENSUS",
        "CL159_COUNT_DICTIONARY", "CL159_COUNT_INVENTORY", "CL159_ECONOMY_ROW",
        "CL159_NOTE_REPORT_FILE_CHAIN", "CL159_RECIPIENT_FILE_CHAIN", "CL159_INTERNAL_RESPONSE",
        "CL159_SAF355_EXCEPTION_SCOPE", "CL159_SAF355_A1", "CL159_SAF355_A4",
        "CL159_DUAL_CUSTODY_NEGATIVE", "CL159_FINAL_BANK_GATE"} <= {row["gap_id"] for row in trace}
assert len(keys) == 530
assert {"GSEyP Nota SIGEN 3672/09", "GSEPYPF Nota 4712/2010",
        "145 Unidades Auditoría Interna planeamientos 2007",
        "aproximadamente 120 cerca de 160 Supervisión Planeamiento 2009",
        "SAF355 Anexo IV C41 C42 C55 71597 152677 2876",
        "71597 152677 2876 C41 C42 C55 banco reversa"} <= {row["exact_key"] for row in keys}
assert len(objects) == 79 and objects == rows("E0_V159_REQUEST_OBJECTS_V159.csv")
assert all(row["status"] == "DRAFT_NOT_SENT" for row in objects)
assert {"SIGEN_GSEYP_2009_IDENTITY_ACT", "SIGEN_UAI_2009_CENSUS",
        "SIGEN_PLANNING_COUNT_DICTIONARY_2009", "SIGEN_PLANNING_REPORT_INVENTORY_2009",
        "SIGEN_ECONOMY_NOTE_REPORT_RECIPIENT_LIFECYCLE", "SAF355_CLOSING_EXCEPTION_SCOPE_CERTIFICATE",
        "SAF355_UAI_ANNEX_I_EXECUTION", "SAF355_UAI_ANNEX_IV_EXECUTION",
        "DUAL_CUSTODY_TESTED_NEGATIVE"} <= {row["object_id"] for row in objects}

visual = rows("E0_V159_PDF_VISUAL_CONTROL.csv")
images = rows("E0_V159_IMAGE_VISUAL_CONTROL.csv")
assert len(visual) == 148 and len(images) == 3
new_visual = [row for row in visual if row["control_id"].startswith("PV159_")]
assert len(new_visual) == 6 and all(row["result"] == "PASS" for row in visual + images)
assert {(row["source_id"], row["pdf_page"]) for row in new_visual} == {
    ("e0_sigen_memoria_2003_gsepfye_area_and_note_suffix", "3"),
    ("e0_sigen_memoria_2003_gsepfye_area_and_note_suffix", "7"),
    ("e0_sigen_memoria_2004_supervision_structure_and_record_systems", "8"),
    ("e0_sigen_memoria_2004_supervision_structure_and_record_systems", "9"),
    ("e0_sigen_memoria_2006_uai_and_output_measure_denominators", "3"),
    ("e0_eras_act_09_2010_gsepypf_note_report_and_recipient_file", "5"),
}

register = rows("E0_REQUEST_RESPONSE_REGISTER_V159.csv")
assert len(register) == 6
assert all(row["status"] == "DRAFT_NOT_SENT" and row["submitted_on"] == "N/A"
           and row["submission_channel"] == "N/A" and row["receipt_or_case_id"] == "N/A"
           and row["response_date"] == "N/A" for row in register)
assert all("V159.md" in row["draft_file"] for row in register)
for name in [
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V159.md", "REQUEST_BCRA_CRYL_SETTLEMENT_V159.md",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V159.md", "REQUEST_AGN_2018_REPLY_V159.md",
    "REQUEST_CNV_CUSTODY_RECORDS_V159.md", "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V159.md",
]:
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "BORRADOR_NO_ENVIADO" in text or "DRAFT_NOT_SENT" in text
econ = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V159.md").read_text(encoding="utf-8-sig")
assert all(token in econ for token in ["GSEPFyE", "GSEyP", "GSEPyPF", "GSEPYPF"])
assert "censo de UAI 2009" in econ and "Anexo IV" in econ and "0/10" in econ

with (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V159.csv").open(encoding="utf-8-sig", newline="") as handle:
    hashes = list(csv.DictReader(handle))
assert len(hashes) == 537
assert sum(row["exists"] == "True" for row in hashes) == 531
assert sum(row["hash_ok"] == "True" for row in hashes) == 531

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V159.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V159" and complete["master_catalog_entries"] == 537
assert complete["e0_primary_sources_preserved"] == 297
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 531
assert complete["remaining_physical_gaps"] == 6
assert complete["e0_fiscal_method_breaks_frozen"] == 341
assert complete["e0_request_traceability_rows"] == 441 and complete["e0_request_search_keys"] == 530
assert complete["e0_V159_pdf_visual_controls"] == 148 and complete["e0_V159_new_pdf_visual_controls"] == 6
assert complete["e0_V159_total_visual_controls"] == 151 and complete["e0_V159_source_bundle_files"] == 4
assert complete["e0_V159_acronym_timeline_rows"] == 12
assert complete["e0_V159_denominator_control_rows"] == 14
assert complete["e0_V159_recipient_lifecycle_rows"] == 12
assert complete["e0_V159_saf355_nontransposition_rows"] == 12
for flag in [
    "e0_gsepfye_2003_2004_long_name_expansion_located",
    "e0_uai_2006_supervised_count_145_located",
    "e0_uai_project_report_denominator_separation_proven",
    "e0_eras_2010_note_report_file_internal_routing_comparator_located",
    "e0_saf355_general_closing_exception_nontransposition_frozen",
]:
    assert complete[flag] is True
for flag in [
    "e0_gseyp_2009_contemporary_expansion_located", "e0_sigen_supervision_structure_2009_located",
    "e0_uai_2009_census_located", "e0_supervision_2009_count_inventory_located",
    "e0_uai_economy_planning_supervision_report_2009_located",
    "e0_uai_economy_planning_supervision_delivery_note_located",
    "e0_uai_economy_planning_supervision_recipient_file_located",
]:
    assert complete[flag] is False
assert complete["e0_uai_saf355_target_certifications_located_count"] == 0
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == complete["e0_request_responses_received"] == 0

manifest = json.loads((HERE / "MANIFEST_V159.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V159" and manifest["parent_checkpoint"] == "V158"
assert manifest["new_preserved_sources"] == 4 and manifest["source_bundle_files"] == 4
assert manifest["fiscal_method_breaks"] == 341 and manifest["request_traceability_rows"] == 441
assert manifest["request_search_keys"] == 530 and manifest["request_objects"] == 79
assert manifest["pdf_visual_controls_total"] == 148 and manifest["pdf_visual_controls_new"] == 6
assert manifest["acronym_timeline_rows"] == 12 and manifest["denominator_control_rows"] == 14
assert manifest["recipient_lifecycle_rows"] == 12 and manifest["saf355_nontransposition_rows"] == 12
assert manifest["gseyp_2009_contemporary_expansion_located"] is False
assert manifest["executed_settlement_rows_confirmed"] == 0
assert manifest["requests_submitted"] == manifest["responses_received"] == 0

for item in manifest["files"]:
    path = HERE / item["path"]
    assert path.is_file() and path.stat().st_size == item["bytes"] and digest(path) == item["sha256"]

for name in ["README_V159.md", "VEREDICTO_V159.md", "E0_FISCAL_RECONSTRUCTION_V159.md",
             "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V159_A_V160.md"]:
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")
assert not (HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V159_A_V159.md").exists()

combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined and "TARGET_EXTRACT_FOUND" not in combined

print("V159 QA PASS")
