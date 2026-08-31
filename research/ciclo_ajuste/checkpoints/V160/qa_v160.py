from pathlib import Path
import csv
import hashlib
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v160" / "binaries"


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
    "e0_infoleg_plan_sigen_2010_annex_g_debt_consolidation_acronyms",
    "e0_infoleg_plan_sigen_2010_annex_g_gseyp_gspf_exact_expansions",
    "e0_infoleg_plan_sigen_2010_annex_g_treasury_debt_service_acronyms",
    "e0_infoleg_plan_sigen_2010_annex_h_multi_entity_uai_crosswalk",
    "e0_decree_1366_2009_transitional_uai_economy_multi_ministry_control",
}

with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as handle:
    catalog = list(csv.DictReader(handle))
assert len(catalog) == 542 and len({row["id"] for row in catalog}) == 542
assert new_ids <= {row["id"] for row in catalog}

census = {row["source_id"]: row for row in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V160.csv")}
provenance = {row["source_id"]: row for row in rows("ARCHIVAL_PROVENANCE_V160.csv")}
assert len(census) == 302 and new_ids <= set(census) and new_ids <= set(provenance)
for source_id in new_ids:
    path = REPO / census[source_id]["local_path"].lstrip("/")
    assert path.is_file() and digest(path) == census[source_id]["sha256"]
    assert "/v160/binaries/" in census[source_id]["local_path"]
assert census["e0_infoleg_plan_sigen_2010_annex_g_gseyp_gspf_exact_expansions"]["use_status"] == "E0_USABLE_NEAR_CONTEMPORARY_EXACT_GSEYP_AND_GSPF_EXPANSIONS"
assert census["e0_infoleg_plan_sigen_2010_annex_h_multi_entity_uai_crosswalk"]["use_status"] == "E0_USABLE_EXACT_UAI_TO_MULTIPLE_ENTITIES_CROSSWALK"
assert census["e0_decree_1366_2009_transitional_uai_economy_multi_ministry_control"]["use_status"] == "E0_USABLE_EXACT_2009_TRANSITIONAL_UAI_CONTROL_SCOPE"

bundle = rows("E0_V160_SOURCE_BUNDLE.csv")
assert len(bundle) == 5 and all(row["catalogued"] == "YES" and row["preserved"] == "YES" for row in bundle)
assert {row["role"] for row in bundle} == {
    "DEBT_CONSOLIDATION_AND_FINANCIAL_ENTITY_GLOSSARY",
    "EXACT_GSEYP_GSPF_OFFICIAL_EXPANSIONS",
    "OT_SDP_SJ_OFFICIAL_GLOSSARY",
    "UAI_TO_MULTIPLE_ENTITIES_CROSSWALK",
    "TRANSITIONAL_UAI_ECONOMY_LEGAL_SCOPE",
}
for row in bundle:
    path = BIN / row["filename"]
    assert path.is_file() and path.stat().st_size == int(row["bytes"])
    assert digest(path) == row["sha256"]

glossary = rows("E0_GSEYP_GSPF_OFFICIAL_GLOSSARY_CROSSWALK_V160.csv")
assert len(glossary) == 15
assert any(row["official_token"] == "GSEyP" and row["official_expansion"] == "Gerencia de Supervisión Economía y Producción" for row in glossary)
assert any(row["official_token"] == "GSPF" and row["official_expansion"] == "Gerencia de Supervisión Planificación Federal" for row in glossary)
assert any(row["status"] == "GLOSSARY_GAP_CLOSED_DOCUMENT_GAP_OPEN" for row in glossary)

multi = rows("E0_UAI_MULTI_ENTITY_DENOMINATOR_CROSSWALK_V160.csv")
assert len(multi) == 14
assert {"MEyFP", "ONCCA", "MAGyP", "MIyT", "YCRT"} <= {row["entity_token"] for row in multi}
assert any(row["uai_heading"] == "Total Plan 2010" and row["entity_token"] == "154 UAI" for row in multi)
assert any(row["uai_heading"] == "Total productos" and row["entity_token"] == "más de 4550" for row in multi)

routes = rows("E0_TARGET_PRODUCER_ACRONYM_AND_ENTITY_ROUTE_V160.csv")
assert len(routes) == 14
assert {"GSEyP", "SJ", "UAI MEyFP", "MEyFP", "OT", "SDP", "CASCPP", "BNA"} <= {row["token"] for row in routes}
assert any(row["token"] == "BNA" and row["status"] == "BANK_ROUTE" for row in routes)

gate = rows("E0_PLAN_2009_ANNEX_G_PUBLIC_NEGATIVE_AND_EXACT_DATE_GATE_V160.csv")
assert len(gate) == 10
assert any(row["question"] == "¿Se halló Plan SIGEN 2009 completo?" and row["public_result"] == "No en búsqueda pública oficial" for row in gate)
assert any(row["question"] == "¿La nueva evidencia prueba banco?" and row["public_result"] == "No" for row in gate)

assert len(rows("E0_SIGEN_SUPERVISION_AREA_ACRONYM_TIMELINE_V160.csv")) == 12
assert len(rows("E0_UAI_COUNT_REPORT_DENOMINATOR_CONTROL_V160.csv")) == 14
assert len(rows("E0_SUPERVISION_NOTE_RECIPIENT_LIFECYCLE_V160.csv")) == 12
assert len(rows("E0_SAF355_EXCEPTION_CERTIFICATION_NONTRANSPOSITION_V160.csv")) == 12
assert len(rows("E0_PLAN_2009_PRELIMINARY_FINAL_APPROVAL_WORKFLOW_V160.csv")) == 20
assert len(rows("E0_UAI_ECONOMY_2009_REORGANIZATION_VERSION_CHAIN_V160.csv")) == 16
assert len(rows("E0_PLANNING_SUPERVISION_COUNT_CONFLICT_V160.csv")) == 12
assert len(rows("E0_SUPERVISION_REPORT_DELIVERY_METADATA_V160.csv")) == 12
assert len(rows("E0_2008_2009_PLAN_SISIO_APPROVAL_CHAIN_V160.csv")) == 22

negative = rows("E0_V160_PUBLIC_SEARCH_NEGATIVE_RESULTS.csv")
assert len(negative) == 21 and negative == rows("E0_V160_PUBLIC_SEARCH_NEGATIVE_RESULTS_V160.csv")
assert {"NEAR_CONTEMPORARY_EXPANSION_LOCATED", "PLAN_2009_BODY_STILL_OPEN", "MULTI_ENTITY_UAI_PROVED",
        "LEGAL_SCOPE_LOCATED", "TARGET_CERTIFICATES_NOT_LOCATED", "BANK_EXECUTION_NOT_LOCATED",
        "DRAFT_NOT_SENT"} <= {row["status"] for row in negative}

breaks = rows("E0_FISCAL_METHOD_BREAKS_V160.csv")
trace = rows("E0_INFORMATION_REQUEST_TRACEABILITY_V160.csv")
keys = rows("E0_REQUEST_SEARCH_KEY_MATRIX_V160.csv")
objects = rows("E0_V160_REQUEST_OBJECTS.csv")
assert len(breaks) == 354
assert {
    "gseyp_plan2010_expansion_not_exact_note_date", "gseyp_not_gspf",
    "official_glossary_not_note_body", "uai_count_not_entity_count",
    "multi_entity_uai_not_multiple_reports", "plan_cutoff_not_final_plan",
    "uai_economy_2010_scope_not_full_2009_custody", "transitional_control_not_project_inclusion",
    "ot_not_sdp", "debt_consolidation_not_buyback", "uai_bna_not_bank_execution",
    "glossary_token_not_record_producer", "annex_image_not_complete_organizational_act",
} <= {row["break_id"] for row in breaks}
assert len(trace) == 451 and all(row["status"] == "DRAFT_NOT_SENT" for row in trace)
assert {"CL160_GSEYP_EXACT_DATE_ACT", "CL160_NOTE_3672_BODY", "CL160_PLAN2009_ANNEX_G",
        "CL160_UAI_ENTITY_CROSSWALK", "CL160_UAI_PROJECT_REPORT_CROSSWALK",
        "CL160_TRANSITIONAL_SCOPE", "CL160_OT_SDP_CROSSWALK",
        "CL160_UAI_BANK_LAYER_SEPARATION"} <= {row["gap_id"] for row in trace}
assert len(keys) == 545
assert {"GSEyP Gerencia de Supervisión Economía y Producción",
        "GSPF Gerencia de Supervisión Planificación Federal",
        "Decreto 1366/2009 artículo 7 UAI Economía control interno Industria Agricultura",
        "154 UAI más de 4550 productos SISIO 16/12/2009",
        "OT Obligaciones a cargo del Tesoro", "SDP Servicio de la Deuda Pública"} <= {row["exact_key"] for row in keys}
assert len(objects) == 86 and objects == rows("E0_V160_REQUEST_OBJECTS_V160.csv")
assert all(row["status"] == "DRAFT_NOT_SENT" for row in objects)
assert {"SIGEN_GSEYP_EXACT_DATE_ORGANIC_ACT", "SIGEN_NOTE_3672_2009_FULL_BODY",
        "SIGEN_PLAN_2009_ANNEX_G", "SIGEN_UAI_ENTITY_PROJECT_REPORT_CROSSWALK_2009",
        "ECONOMY_UAI_DECREE_1366_SCOPE_TABLE", "TREASURY_OT_SDP_TARGET_CROSSWALK",
        "BNA_UAI_EXECUTION_LAYER_CROSSWALK"} <= {row["object_id"] for row in objects}

visual = rows("E0_V160_PDF_VISUAL_CONTROL.csv")
images = rows("E0_V160_IMAGE_VISUAL_CONTROL.csv")
assert len(visual) == 148 and len(images) == 7
new_images = [row for row in images if row["control_id"].startswith("IV160_")]
assert len(new_images) == 4 and all(row["result"] == "PASS" for row in visual + images)
assert {row["artifact"] for row in new_images} == {
    "infoleg_plan_sigen_2010_annex_g_debt_consolidation_acronyms_image15.jpg",
    "infoleg_plan_sigen_2010_annex_g_supervision_area_acronyms_image16.jpg",
    "infoleg_plan_sigen_2010_annex_g_treasury_debt_service_acronyms_image17.jpg",
    "infoleg_plan_sigen_2010_annex_h_multi_entity_uai_image19.jpg",
}

register = rows("E0_REQUEST_RESPONSE_REGISTER_V160.csv")
assert len(register) == 6
assert all(row["status"] == "DRAFT_NOT_SENT" and row["submitted_on"] == "N/A"
           and row["submission_channel"] == "N/A" and row["receipt_or_case_id"] == "N/A"
           and row["response_date"] == "N/A" for row in register)
assert all("V160.md" in row["draft_file"] for row in register)
for name in [
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V160.md", "REQUEST_BCRA_CRYL_SETTLEMENT_V160.md",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V160.md", "REQUEST_AGN_2018_REPLY_V160.md",
    "REQUEST_CNV_CUSTODY_RECORDS_V160.md", "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V160.md",
]:
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "BORRADOR_NO_ENVIADO" in text or "DRAFT_NOT_SENT" in text
econ = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V160.md").read_text(encoding="utf-8-sig")
assert all(token in econ for token in ["GSEyP", "GSPF", "Decreto 1366/2009", "154 UAI", "0/10"])

with (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V160.csv").open(encoding="utf-8-sig", newline="") as handle:
    hashes = list(csv.DictReader(handle))
assert len(hashes) == 542
assert sum(row["exists"] == "True" for row in hashes) == 536
assert sum(row["hash_ok"] == "True" for row in hashes) == 536

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V160.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V160" and complete["master_catalog_entries"] == 542
assert complete["e0_primary_sources_preserved"] == 302
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 536
assert complete["remaining_physical_gaps"] == 6
assert complete["e0_fiscal_method_breaks_frozen"] == 354
assert complete["e0_request_traceability_rows"] == 451 and complete["e0_request_search_keys"] == 545
assert complete["e0_V160_pdf_visual_controls"] == 148 and complete["e0_V160_new_pdf_visual_controls"] == 0
assert complete["e0_V160_image_visual_controls"] == 7 and complete["e0_V160_new_image_visual_controls"] == 4
assert complete["e0_V160_total_visual_controls"] == 155 and complete["e0_V160_source_bundle_files"] == 5
assert complete["e0_V160_official_glossary_rows"] == 15
assert complete["e0_V160_multi_entity_uai_rows"] == 14
assert complete["e0_V160_producer_route_rows"] == 14
assert complete["e0_V160_exact_date_gate_rows"] == 10
for flag in [
    "e0_gseyp_near_contemporary_official_expansion_located",
    "e0_gseyp_and_gspf_distinct_in_plan_2010_glossary",
    "e0_plan_sigen_2010_annex_g_official_glossary_located",
    "e0_plan_sigen_2010_annex_h_multi_entity_uai_located",
    "e0_decree_1366_2009_transitional_uai_economy_scope_located",
    "e0_uai_count_not_entity_count_proven",
]:
    assert complete[flag] is True
for flag in [
    "e0_gseyp_2009_contemporary_expansion_located",
    "e0_gseyp_note_3672_2009_issue_date_expansion_located",
    "e0_plan_sigen_2009_annex_g_located",
    "e0_sigen_supervision_structure_2009_located",
    "e0_uai_2009_census_located", "e0_supervision_2009_count_inventory_located",
]:
    assert complete[flag] is False
assert complete["e0_uai_saf355_target_certifications_located_count"] == 0
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == complete["e0_request_responses_received"] == 0

manifest = json.loads((HERE / "MANIFEST_V160.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V160" and manifest["parent_checkpoint"] == "V159"
assert manifest["new_preserved_sources"] == 5 and manifest["source_bundle_files"] == 5
assert manifest["fiscal_method_breaks"] == 354 and manifest["request_traceability_rows"] == 451
assert manifest["request_search_keys"] == 545 and manifest["request_objects"] == 86
assert manifest["pdf_visual_controls_total"] == 148 and manifest["pdf_visual_controls_new"] == 0
assert manifest["image_visual_controls_total"] == 7 and manifest["image_visual_controls_new"] == 4
assert manifest["official_glossary_rows"] == 15 and manifest["multi_entity_uai_rows"] == 14
assert manifest["producer_route_rows"] == 14 and manifest["exact_date_gate_rows"] == 10
assert manifest["gseyp_near_contemporary_official_expansion_located"] is True
assert manifest["gseyp_note_3672_2009_issue_date_expansion_located"] is False
assert manifest["executed_settlement_rows_confirmed"] == 0
assert manifest["requests_submitted"] == manifest["responses_received"] == 0

for item in manifest["files"]:
    path = HERE / item["path"]
    assert path.is_file() and path.stat().st_size == item["bytes"] and digest(path) == item["sha256"]

for name in ["README_V160.md", "VEREDICTO_V160.md", "E0_FISCAL_RECONSTRUCTION_V160.md",
             "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V160_A_V161.md"]:
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")
assert not (HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V160_A_V160.md").exists()

combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined and "TARGET_EXTRACT_FOUND" not in combined

print("V160 QA PASS")
