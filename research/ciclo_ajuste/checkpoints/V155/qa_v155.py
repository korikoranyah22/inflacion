from pathlib import Path
import csv
import hashlib
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v155" / "binaries"


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
    "e0_cgn_account_2009_uepex_2008_note_sisio_chain",
    "e0_mecon_current_audit_disclosure_window_and_sigen_route",
    "e0_sigen_current_aip_direct_form",
    "e0_mecon_uai_structure_2010_accounting_control_duties",
}

with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as handle:
    catalog = list(csv.DictReader(handle))
assert len(catalog) == 517 and len({row["id"] for row in catalog}) == 517
assert new_ids <= {row["id"] for row in catalog}

census = {row["source_id"]: row for row in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V155.csv")}
provenance = {row["source_id"]: row for row in rows("ARCHIVAL_PROVENANCE_V155.csv")}
assert len(census) == 277 and new_ids <= set(census) and new_ids <= set(provenance)
for source_id in new_ids:
    path = REPO / census[source_id]["local_path"].lstrip("/")
    assert path.is_file() and digest(path) == census[source_id]["sha256"]
    assert "/v155/binaries/" in census[source_id]["local_path"]
assert census["e0_cgn_account_2009_uepex_2008_note_sisio_chain"]["use_status"] == "E0_USABLE_AS_CONTEMPORANEOUS_ROUTING_AND_CONTROL_CHAIN"
assert "post-target" in census["e0_mecon_uai_structure_2010_accounting_control_duties"]["caveat"].lower() or "posterior" in census["e0_mecon_uai_structure_2010_accounting_control_duties"]["caveat"].lower()

bundle = rows("E0_V155_SOURCE_BUNDLE.csv")
assert len(bundle) == 5 and sum(row["catalogued"] == "YES" for row in bundle) == 4
assert all(row["preserved"] == "YES" for row in bundle)
assert {row["role"] for row in bundle} == {
    "CONTEMPORARY_NOTE_AND_SISIO_CHAIN",
    "SAME_OFFICIAL_SOURCE_HTML_BUNDLE_ONLY",
    "CURRENT_DISCLOSURE_AND_REFERRAL_ROUTE",
    "CURRENT_DIRECT_AIP_FORM_NOT_SENT",
    "POST_TARGET_UAI_DUTY_COMPARATOR",
}
for row in bundle:
    path = BIN / row["filename"]
    assert path.is_file() and path.stat().st_size == int(row["bytes"])
    assert digest(path) == row["sha256"]

chain = rows("E0_2008_DAIF_SIGEN_SISIO_FOLLOWUP_CHAIN_V155.csv")
assert len(chain) == 24
chain_ids = {row["exact_identifier"] for row in chain}
assert {"Nota 0120/09 DAIF", "Nota SIGEN 3672/09 GSEyP", "SISIO"} <= chain_ids
assert {"CONTEMPORARY_RECORD_LOCATED", "SYSTEM_ENTRY_REQUIRED", "FOLLOWUP_ROUTE",
        "QUERY_CAPABILITY", "ACCESS_BARRIER", "REQUEST_UPGRADE"} <= {row["status"] for row in chain}
assert any("No es el informe global" in row["limit"] for row in chain)

responsibility = rows("E0_2008_CLOSING_RESPONSIBILITY_AND_RECORD_PRODUCER_CHAIN_V155.csv")
assert len(responsibility) == 20
assert {"Jefatura SAF", "Unidad de Registro Contable", "CGN-DAIF", "SIGEN GSEyP",
        "UAI Economía"} <= {row["authority_or_actor"] for row in responsibility}
assert {"RESPONSIBLE_LEVEL", "EXACT_RECORD", "SYSTEM_CUSTODIAN",
        "POST_TARGET_COMPARATOR", "METHOD_CONTROL"} <= {row["status"] for row in responsibility}

disclosure = rows("E0_MECON_CURRENT_DISCLOSURE_AND_AIP_ROUTE_V155.csv")
assert len(disclosure) == 16
assert {"MECON_WINDOW", "SIGEN_SEARCH", "SIGEN_FORM", "AIP_DETAIL", "REQUEST_STATE"} <= {
    row["route_or_field"] for row in disclosure
}
assert any(row["status"] == "DRAFT_NOT_SENT" for row in disclosure)
assert any("No cubre 2009" in row["limit"] for row in disclosure)

uai = rows("E0_UAI_ECONOMY_POST_TARGET_STRUCTURE_AND_DUTIES_V155.csv")
assert len(uai) == 20 and all(row["status"] in {"POST_TARGET_COMPARATOR", "METHOD_LIMIT"} for row in uai)
assert {"11", "12", "15", "16", "17", "18"} <= {row["action_number"] for row in uai}
assert any(row["status"] == "METHOD_LIMIT" and "No atribuir" in row["target_use"] for row in uai)

acronym = rows("E0_GSEYP_GSEPYPF_ACRONYM_CAUTION_V155.csv")
assert len(acronym) == 10
assert {"GSEyP", "GSEPyPF", "3672/09", "0120/09", "SISIO"} <= {row["token"] for row in acronym}
assert any("Equipararlo" in row["forbidden_inference"] for row in acronym)

negative = rows("E0_V155_PUBLIC_SEARCH_NEGATIVE_RESULTS.csv")
assert len(negative) == 12
assert negative == rows("E0_V155_PUBLIC_SEARCH_NEGATIVE_RESULTS_V155.csv")
assert {"GLOBAL_REPORT_ID_NOT_LOCATED", "REFERENCED_BODY_NOT_LOCATED",
        "SYSTEM_ENTRY_NOT_PUBLIC", "ACRONYM_EQUIVALENCE_NOT_PROVEN",
        "TARGET_CERTIFICATES_NOT_LOCATED", "BANK_EXECUTION_NOT_LOCATED",
        "DRAFT_NOT_SENT"} <= {row["status"] for row in negative}

objects = rows("E0_V155_REQUEST_OBJECTS.csv")
assert len(objects) == 36 and all(row["status"] == "DRAFT_NOT_SENT" for row in objects)
assert objects == rows("E0_V155_REQUEST_OBJECTS_V155.csv")
assert {"DAIF_NOTE_0120", "SIGEN_NOTE_3672", "SISIO_FINDINGS", "UAI_PLAN_2009",
        "UAI_REPORT_BOOK_2009", "PARAMETERIZED_QUERY", "DOCUMENT_DISPOSITION",
        "SIGEN_AIP_RECEIPT"} <= {row["object_id"] for row in objects}

breaks = rows("E0_FISCAL_METHOD_BREAKS_V155.csv")
trace = rows("E0_INFORMATION_REQUEST_TRACEABILITY_V155.csv")
keys = rows("E0_REQUEST_SEARCH_KEY_MATRIX_V155.csv")
assert len(breaks) == 297
assert {
    "exact_note_chain_not_target_certificate",
    "sisio_followup_entry_not_report_body",
    "gseyp_not_automatically_gsepypf",
    "uepex_control_not_saf355_general_debt",
    "current_mecon_2022_window_not_2009_nonexistence",
    "aip_form_availability_not_request_submission",
    "post_target_uai_structure_not_2009_exact_orgchart",
    "resolution_6_article22_responsibility_not_record_recovery",
    "parameterized_query_capability_not_query_result",
    "replacement_certification_not_bank_execution",
} <= {row["break_id"] for row in breaks}
assert len(trace) == 374 and all(row["status"] == "DRAFT_NOT_SENT" for row in trace)
assert {"CL155_DAIF_NOTE", "CL155_SIGEN_NOTE", "CL155_SISIO_ENTRY", "CL155_FINAL_BANK_GATE"} <= {
    row["gap_id"] for row in trace
}
assert len(keys) == 442
assert {"Nota N° 0120/09 DAIF", "Nota SIGEN N° 3672/09 GSEyP",
        "Sistema Informático SISIO", "Plan Anual Auditoría Interna 2009",
        "71597 152677 2876 C41 C42 C55 banco reversa"} <= {row["exact_key"] for row in keys}

channels = rows("CURRENT_OFFICIAL_SUBMISSION_CHANNELS_V155.csv")
assert len(channels) == 9
sigen = next(row for row in channels if row["channel_id"] == "CH155_SIGEN_AIP")
assert sigen["status"] == "OFFICIAL_AIP_ROUTE_VERIFIED_DRAFT_NOT_SENT"
assert "no se cargaron" in sigen["caveat"].lower()

visual = rows("E0_V155_PDF_VISUAL_CONTROL.csv")
images = rows("E0_V155_IMAGE_VISUAL_CONTROL.csv")
assert len(visual) == 124 and len(images) == 3
new_visual = [row for row in visual if row["control_id"].startswith("PV155_")]
assert len(new_visual) == 3 and all(row["result"] == "PASS" for row in visual + images)
assert {row["pdf_page"] for row in new_visual} == {"77", "78", "79"}
assert all(row["source_id"] == "e0_cgn_account_2009_uepex_2008_note_sisio_chain" for row in new_visual)

register = rows("E0_REQUEST_RESPONSE_REGISTER_V155.csv")
assert len(register) == 6
assert all(row["status"] == "DRAFT_NOT_SENT" and row["submitted_on"] == "N/A"
           and row["receipt_or_case_id"] == "N/A" for row in register)
assert all("V155.md" in row["draft_file"] for row in register)
for name in [
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V155.md", "REQUEST_BCRA_CRYL_SETTLEMENT_V155.md",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V155.md", "REQUEST_AGN_2018_REPLY_V155.md",
    "REQUEST_CNV_CUSTODY_RECORDS_V155.md", "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V155.md",
]:
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "BORRADOR_NO_ENVIADO" in text or "DRAFT_NOT_SENT" in text

with (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V155.csv").open(encoding="utf-8-sig", newline="") as handle:
    hashes = list(csv.DictReader(handle))
assert len(hashes) == 517
assert sum(row["exists"] == "True" for row in hashes) == 511
assert sum(row["hash_ok"] == "True" for row in hashes) == 511

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V155.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V155" and complete["master_catalog_entries"] == 517
assert complete["e0_primary_sources_preserved"] == 277
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 511
assert complete["remaining_physical_gaps"] == 6
assert complete["e0_daif_note_0120_09_reference_located"] is True
assert complete["e0_sigen_note_3672_09_reference_located"] is True
assert complete["e0_sisio_followup_instruction_located"] is True
assert complete["e0_daif_note_0120_09_body_located"] is False
assert complete["e0_sigen_note_3672_09_body_located"] is False
assert complete["e0_sisio_target_entry_located"] is False
assert complete["e0_current_sigen_aip_route_verified"] is True
assert complete["e0_current_sigen_aip_request_submitted"] is False
assert complete["e0_uai_saf355_target_certifications_located_count"] == 0
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == complete["e0_request_responses_received"] == 0

manifest = json.loads((HERE / "MANIFEST_V155.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V155" and manifest["parent_checkpoint"] == "V154"
assert manifest["new_preserved_sources"] == 4 and manifest["source_bundle_files"] == 5
assert manifest["pdf_visual_controls_new"] == 3
assert manifest["daif_note_0120_reference_located"] is True
assert manifest["sigen_note_3672_reference_located"] is True
assert manifest["sisio_followup_instruction_located"] is True
assert manifest["daif_note_0120_body_located"] is False
assert manifest["sigen_aip_request_submitted"] is False
assert manifest["executed_settlement_rows_confirmed"] == 0
assert manifest["requests_submitted"] == manifest["responses_received"] == 0

for name in ["README_V155.md", "VEREDICTO_V155.md", "E0_FISCAL_RECONSTRUCTION_V155.md",
             "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V155_A_V156.md"]:
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")
assert not (HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V155_A_V155.md").exists()

combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined and "TARGET_EXTRACT_FOUND" not in combined

print("V155 QA PASS")
