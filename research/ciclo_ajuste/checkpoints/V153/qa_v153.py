from pathlib import Path
import csv
import hashlib
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v153" / "binaries"


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
    "e0_cgn_circular_1_2009_account_2008_uai_certification",
    "e0_sigen_instruction_2_2008_account_2008_certification",
    "e0_sigen_white_book_2012_account_2008_report_inventory",
    "e0_cgn_circular_8_2009_financial_document_archive_iso",
}

with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as handle:
    catalog = list(csv.DictReader(handle))
assert len(catalog) == 509 and len({row["id"] for row in catalog}) == 509
assert new_ids <= {row["id"] for row in catalog}

census = {row["source_id"]: row for row in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V153.csv")}
provenance = {row["source_id"]: row for row in rows("ARCHIVAL_PROVENANCE_V153.csv")}
assert len(census) == 269 and new_ids <= set(census) and new_ids <= set(provenance)
for source_id in new_ids:
    path = REPO / census[source_id]["local_path"].lstrip("/")
    assert path.is_file() and digest(path) == census[source_id]["sha256"]
    assert "/v153/binaries/" in census[source_id]["local_path"]
assert "/v152/binaries/" in census["e0_sigen_memory_2009_account_2008_global_control_report"]["local_path"]

bundle = rows("E0_V153_SOURCE_BUNDLE.csv")
assert len(bundle) == 7 and sum(row["catalogued"] == "YES" for row in bundle) == 4
assert all(row["preserved"] == "YES" for row in bundle)
for row in bundle:
    path = BIN / row["filename"]
    assert path.is_file() and path.stat().st_size == int(row["bytes"])
    assert digest(path) == row["sha256"]
assert {row["role"] for row in bundle} >= {
    "FULL_INSTRUCTION_AND_ANNEXES", "REPORT_ARCHIVE_LOCATOR",
    "CERTIFICATION_RECEIPT_GATE", "NAMED_ARCHIVE_CUSTODY_ROUTE",
    "CURRENT_PUBLIC_ARCHIVE_SCOPE",
}

circular = rows("E0_CGN_CIRCULAR_1_2009_RECEIPT_GATE_V153.csv")
assert len(circular) == 14
assert {"GATE", "INSTRUCTION", "TARGET", "LIMIT_PAYMENT"} <= {row["object_code"] for row in circular}
assert any(row["status"] == "RECEIPT_GATE_PROVED" for row in circular)
assert any(row["status"] == "NOT_PAYMENT_PROOF" for row in circular)

instruction = rows("E0_UAI_INSTRUCTION_2_2008_EXACT_ANNEX_AND_SOURCE_MAP_V153.csv")
assert len(instruction) == 40
codes = {row["object_code"] for row in instruction}
assert {"MODELS", "DEADLINE_I_IV", "A1_BANK", "A2_OBJECT", "A3_OBJECT", "A4_OBJECT", "A5_OBJECT", "LIMIT_PAYMENT"} <= codes
assert {"ANNEX_I", "ANNEX_II", "ANNEX_III_UEPEX", "ANNEX_IV_TARGET_RELEVANT", "ANNEX_V"} <= {row["status"] for row in instruction}
assert any(row["status"] == "MODEL_NOT_EXECUTED_TARGET" for row in instruction)

branch = rows("E0_SAF355_UAI_CERTIFICATION_TARGET_BRANCH_V153.csv")
assert len(branch) == 21
assert {"A1", "A2", "A3", "A4", "A5", "A4_TARGET", "BANK_LINK", "LIMIT"} <= {row["object_code"] for row in branch}
assert any(row["status"] == "NOT_PAYMENT_PROOF" for row in branch)

locator = rows("E0_SIGEN_ACCOUNT_2008_REPORT_ARCHIVE_LOCATOR_V153.csv")
assert len(locator) == 16
loc = {row["object_code"]: row for row in locator}
assert loc["ENTITY"]["value"] == "Ministerio de Economía y Finanzas Públicas"
assert loc["YEAR"]["value"] == "2009" and loc["AREA"]["value"] == "GSEPyPF"
assert "121" in loc["PUBLIC_ARCHIVE"]["value"] and "2020-2026" in loc["PUBLIC_ARCHIVE"]["value"]
assert loc["BODY"]["status"] == "OPEN" and loc["SAF355"]["status"] == "OPEN"

archive = rows("E0_CGN_FINANCIAL_ARCHIVE_CUSTODY_ROUTE_V153.csv")
assert len(archive) == 14
assert {"ARCHIVE", "SCOPE_DIGITIZE", "SCOPE_GUARD", "SCOPE_DESCRIBE", "LEGAL_VALUE", "TARGET_LIMIT"} <= {row["object_code"] for row in archive}
assert any(row["status"] == "METHOD_LIMIT" for row in archive)

uai = rows("E0_UAI_2008_INSTRUCTIVE_AND_EXECUTED_CERTIFICATION_ROUTE_V153.csv")
uai_map = {row["object_code"]: row for row in uai}
assert uai_map["INSTR_BODY"]["status"] == "BODY_LOCATED"
assert uai_map["INSTR_02_EXISTENCE"]["status"] == "BODY_AND_ANNEXES_LOCATED"
assert "INSTRUCTIVE_BODY_NOT_LOCATED" not in {row["status"] for row in uai}
assert uai_map["MINISTRY_CERT"]["status"] == "TARGET_OPEN"

negative = rows("E0_V153_PUBLIC_SEARCH_NEGATIVE_RESULTS.csv")
assert len(negative) == 16
negative_status = {row["status"] for row in negative}
assert {"TARGET_CERT_I_NOT_LOCATED", "TARGET_CERT_IV_NOT_LOCATED", "GLOBAL_REPORT_BODY_NOT_LOCATED",
        "CURRENT_ARCHIVE_2009_NOT_EXPOSED", "ARCHIVE_TARGET_INDEX_NOT_LOCATED"} <= negative_status
assert "INSTRUCTIVE_BODY_NOT_LOCATED" not in negative_status
assert negative == rows("E0_V153_PUBLIC_SEARCH_NEGATIVE_RESULTS_V153.csv")

objects = rows("E0_V153_REQUEST_OBJECTS.csv")
assert len(objects) == 20 and all(row["status"] == "DRAFT_NOT_SENT" for row in objects)
assert {"UAI_CERT_I", "UAI_CERT_IV", "UAI_CERT_V", "SIGEN_GLOBAL_METADATA", "AGDFA_INDEX", "FINAL_LISTS"} <= {row["object_id"] for row in objects}
assert "INSTR_02" not in {row["object_id"] for row in objects}
assert objects == rows("E0_V153_REQUEST_OBJECTS_V153.csv")

visual = rows("E0_V153_PDF_VISUAL_CONTROL.csv")
images = rows("E0_V153_IMAGE_VISUAL_CONTROL.csv")
assert len(visual) == 112 and len(visual) - 98 == 14
assert len([row for row in visual if row["control_id"].startswith("PV153_")]) == 14
assert len(images) == 3 and all(row["result"] == "PASS" for row in visual + images)
instruction_visual = [row for row in visual if row["source_id"] == "e0_sigen_instruction_2_2008_account_2008_certification"]
assert {row["pdf_page"] for row in instruction_visual} == {str(i) for i in range(1, 12)}
assert any(row["source_id"] == "e0_sigen_white_book_2012_account_2008_report_inventory" and row["pdf_page"] == "54" for row in visual)

breaks = rows("E0_FISCAL_METHOD_BREAKS_V153.csv")
trace = rows("E0_INFORMATION_REQUEST_TRACEABILITY_V153.csv")
keys = rows("E0_REQUEST_SEARCH_KEY_MATRIX_V153.csv")
required_breaks = {
    "instruction_body_located_not_executed_saf355_certificate",
    "cgn_receipt_gate_not_received_target_proof",
    "annex_i_balance_certification_not_individual_payment",
    "annex_ii_revolving_fund_not_debt_settlement",
    "annex_iii_uepex_not_general_saf355",
    "annex_iv_late_form_certification_not_bank_execution",
    "annex_v_remainder_certification_not_target_payment",
    "sigen_inventory_entry_not_report_body_or_saf355_validation",
    "cgn_archive_capability_not_target_ingestion",
    "current_sigen_archive_window_not_historical_nonexistence",
}
assert len(breaks) == 277 and required_breaks <= {row["break_id"] for row in breaks}
assert len(trace) == 342 and all(row["status"] == "DRAFT_NOT_SENT" for row in trace)
assert len(keys) == 402
assert {"Instructivo de Trabajo N° 2/2008 GNyPE", "GSEPyPF", "SAF 355 Anexo IV 71597 152677 2876"} <= {row["exact_key"] for row in keys}

register = rows("E0_REQUEST_RESPONSE_REGISTER_V153.csv")
assert len(register) == 6
assert all(row["status"] == "DRAFT_NOT_SENT" and row["submitted_on"] == "N/A" and row["receipt_or_case_id"] == "N/A" for row in register)
for name in [
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V153.md",
    "REQUEST_BCRA_CRYL_SETTLEMENT_V153.md",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V153.md",
    "REQUEST_AGN_2018_REPLY_V153.md",
    "REQUEST_CNV_CUSTODY_RECORDS_V153.md",
    "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V153.md",
]:
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "BORRADOR_NO_ENVIADO" in text or "DRAFT_NOT_SENT" in text

with (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V153.csv").open(encoding="utf-8-sig", newline="") as handle:
    hashes = list(csv.DictReader(handle))
assert sum(row["exists"] == "True" for row in hashes) == 503
assert sum(row["hash_ok"] == "True" for row in hashes) == 503

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V153.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V153" and complete["master_catalog_entries"] == 509
assert complete["e0_primary_sources_preserved"] == 269
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 503
assert complete["remaining_physical_gaps"] == 6
assert complete["e0_uai_instruction_02_2008_body_located"] is True
assert complete["e0_uai_instruction_02_2008_annexes_located"] == 5
assert complete["e0_uai_saf355_target_certification_located"] is False
assert complete["e0_cgn_no_receipt_without_uai_certification_proved"] is True
assert complete["e0_sigen_account_2008_global_report_inventory_locator_proved"] is True
assert complete["e0_sigen_account_2008_global_report_body_located"] is False
assert complete["e0_cgn_financial_archive_capability_proved"] is True
assert complete["e0_cgn_financial_archive_target_ingestion_proved"] is False
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == complete["e0_request_responses_received"] == 0

manifest = json.loads((HERE / "MANIFEST_V153.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V153" and manifest["parent_checkpoint"] == "V152"
assert manifest["new_preserved_sources"] == 4 and manifest["source_bundle_files"] == 7
assert manifest["pdf_visual_controls_new"] == 14
assert manifest["uai_instruction_02_2008_body_located"] is True
assert manifest["uai_instruction_02_2008_annexes_located"] == 5
assert manifest["uai_saf355_target_certification_located"] is False
assert manifest["sigen_account_2008_global_report_body_located"] is False
assert manifest["executed_settlement_rows_confirmed"] == 0
assert manifest["requests_submitted"] == manifest["responses_received"] == 0

for name in [
    "README_V153.md", "VEREDICTO_V153.md", "E0_FISCAL_RECONSTRUCTION_V153.md",
    "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V153_A_V154.md",
]:
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")
assert not (HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V153_A_V153.md").exists()

combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined and "TARGET_EXTRACT_FOUND" not in combined

print("V153 QA PASS")
