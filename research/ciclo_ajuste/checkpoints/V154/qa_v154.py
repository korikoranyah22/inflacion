from pathlib import Path
import csv
import hashlib
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v154" / "binaries"


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
    "e0_sigen_public_archive_2020_account_record_family",
    "e0_sigen_if_2020_annex_a_bank_certification_comparator",
    "e0_sigen_if_2020_remainder_certification_cross_reference_comparator",
    "e0_sigen_if_2020_account_control_audit_comparator",
}

with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as handle:
    catalog = list(csv.DictReader(handle))
assert len(catalog) == 513 and len({row["id"] for row in catalog}) == 513
assert new_ids <= {row["id"] for row in catalog}

census = {row["source_id"]: row for row in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V154.csv")}
provenance = {row["source_id"]: row for row in rows("ARCHIVAL_PROVENANCE_V154.csv")}
assert len(census) == 273 and new_ids <= set(census) and new_ids <= set(provenance)
for source_id in new_ids:
    path = REPO / census[source_id]["local_path"].lstrip("/")
    assert path.is_file() and digest(path) == census[source_id]["sha256"]
    assert "/v154/binaries/" in census[source_id]["local_path"]
assert "/v153/binaries/" in census["e0_sigen_instruction_2_2008_account_2008_certification"]["local_path"]

bundle = rows("E0_V154_SOURCE_BUNDLE.csv")
assert len(bundle) == 12 and sum(row["catalogued"] == "YES" for row in bundle) == 4
assert all(row["preserved"] == "YES" for row in bundle)
assert {row["role"] for row in bundle} >= {
    "CURRENT_ACCOUNT_REPORT_FAMILY", "EXECUTED_ANNEX_A_COMPARATOR",
    "EXECUTED_ANNEX_C_COMPARATOR_BUNDLE_ONLY", "EXECUTED_REMAINDER_COMPARATOR",
    "LATER_ACCOUNT_AUDIT_COMPARATOR", "ATTACHMENT_ROUTE_DISCOVERY",
}
for row in bundle:
    path = BIN / row["filename"]
    assert path.is_file() and path.stat().st_size == int(row["bytes"])
    assert digest(path) == row["sha256"]

family = rows("E0_SIGEN_PUBLIC_ACCOUNT_RECORD_FAMILY_AND_IDENTIFIER_CHAIN_V154.csv")
assert len(family) == 29
family_status = {row["status"] for row in family}
assert {"CURRENT_WINDOW_ONLY", "EXECUTED_CERTIFICATE", "IDENTIFIER_SEPARATION",
        "CROSS_REFERENCE", "TARGET_OPEN"} <= family_status
assert {"00394/2020", "00395/2020", "00398/2020", "00399/2020", "00402/2020"} <= {
    row["public_report_no"] for row in family
}
assert any(row["internal_report_no"] == "007/2020-UAI" and row["attachment_id"] == "80644620" for row in family)

chain = rows("E0_EXECUTED_CERTIFICATION_TO_AUDIT_CHAIN_COMPARATOR_V154.csv")
assert len(chain) == 28
codes = {row["object_code"] for row in chain}
assert {"A_BANK", "A_BANK_CERT", "R_PRIOR", "R_MHA", "AUD_TX", "AUD_CGN",
        "TARGET_CERT", "TARGET_PAYMENT"} <= codes
assert any(row["status"] == "TARGET_OPEN" for row in chain)

fields = rows("E0_2008_TARGET_ARCHIVE_REQUEST_FIELD_UPGRADE_V154.csv")
assert len(fields) == 29
assert {"PUBLIC_REPORT_NO", "INTERNAL_REPORT_NO", "EXPEDIENTE", "BANK_STATEMENT",
        "C41_C42_C55", "TARGET_IDS", "REVERSAL", "FORMAT_LIMIT"} <= {
            row["request_field"] for row in fields
        }
assert any(row["status"] == "METHOD_LIMIT" for row in fields)

ladder = rows("E0_ACCOUNT_2008_VALIDATION_TERMINOLOGY_LADDER_V154.csv")
assert len(ladder) == 18
ladder_map = {row["stage_id"]: row for row in ladder}
assert ladder_map["L1"]["status"] == "CONTEXT"
assert ladder_map["L18"]["status"] == "FINAL_GATE"
assert "Única vía" in ladder_map["L18"]["target_implication"]

negative = rows("E0_V154_PUBLIC_SEARCH_NEGATIVE_RESULTS.csv")
assert len(negative) == 14
assert {"GLOBAL_REPORT_ID_NOT_LOCATED", "TARGET_CERT_I_NOT_LOCATED",
        "HISTORICAL_IDENTIFIERS_NOT_LOCATED", "BANK_EXECUTION_NOT_LOCATED"} <= {
            row["status"] for row in negative
        }
assert negative == rows("E0_V154_PUBLIC_SEARCH_NEGATIVE_RESULTS_V154.csv")

objects = rows("E0_V154_REQUEST_OBJECTS.csv")
assert len(objects) == 28 and all(row["status"] == "DRAFT_NOT_SENT" for row in objects)
assert {"SIGEN_PUBLIC_NO", "SIGEN_INTERNAL_NO", "SIGEN_CONTAINER", "SIGEN_ATTACHMENTS",
        "UAI_REMITTANCE_CHAIN", "UAI_SOURCE_INDEX", "UAI_REFERENCE_CHAIN",
        "UAI_EMBEDDED_BODIES"} <= {row["object_id"] for row in objects}
assert objects == rows("E0_V154_REQUEST_OBJECTS_V154.csv")

visual = rows("E0_V154_PDF_VISUAL_CONTROL.csv")
images = rows("E0_V154_IMAGE_VISUAL_CONTROL.csv")
assert len(visual) == 121 and len(images) == 3
new_visual = [row for row in visual if row["control_id"].startswith("PV154_")]
assert len(new_visual) == 9 and all(row["result"] == "PASS" for row in visual + images)
assert {row["source_id"] for row in new_visual} >= {
    "e0_sigen_if_2020_annex_a_bank_certification_comparator",
    "bundle_sigen_if_2020_09438552_annex_c_certification",
    "e0_sigen_if_2020_remainder_certification_cross_reference_comparator",
    "e0_sigen_if_2020_account_control_audit_comparator",
}

breaks = rows("E0_FISCAL_METHOD_BREAKS_V154.csv")
trace = rows("E0_INFORMATION_REQUEST_TRACEABILITY_V154.csv")
keys = rows("E0_REQUEST_SEARCH_KEY_MATRIX_V154.csv")
required_breaks = {
    "public_report_number_not_attachment_identifier",
    "gde_if_identifier_not_retroactive_2009_schema",
    "executed_annex_a_certification_not_target_saf355",
    "bank_statements_as_source_not_target_transaction",
    "remainder_cross_reference_not_individual_payment",
    "later_account_audit_not_annex_certificate",
    "saf109_2019_comparator_not_saf355_2008",
    "embedded_annex_reference_not_public_embedded_body",
    "sidif_validated_compilation_not_uai_or_bank_validation",
    "current_archive_family_not_complete_historical_inventory",
}
assert len(breaks) == 287 and required_breaks <= {row["break_id"] for row in breaks}
assert len(trace) == 358 and all(row["status"] == "DRAFT_NOT_SENT" for row in trace)
assert len(keys) == 422
assert {"INFORME N° 007/2020-UAI", "libro de informes UAI 2009",
        "SAF 355 71597 152677 2876 C41 C42 C55"} <= {row["exact_key"] for row in keys}

register = rows("E0_REQUEST_RESPONSE_REGISTER_V154.csv")
assert len(register) == 6
assert all(row["status"] == "DRAFT_NOT_SENT" and row["submitted_on"] == "N/A"
           and row["receipt_or_case_id"] == "N/A" for row in register)
assert all("V154.md" in row["draft_file"] for row in register)
for name in [
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V154.md", "REQUEST_BCRA_CRYL_SETTLEMENT_V154.md",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V154.md", "REQUEST_AGN_2018_REPLY_V154.md",
    "REQUEST_CNV_CUSTODY_RECORDS_V154.md", "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V154.md",
]:
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "BORRADOR_NO_ENVIADO" in text or "DRAFT_NOT_SENT" in text

with (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V154.csv").open(encoding="utf-8-sig", newline="") as handle:
    hashes = list(csv.DictReader(handle))
assert sum(row["exists"] == "True" for row in hashes) == 507
assert sum(row["hash_ok"] == "True" for row in hashes) == 507

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V154.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V154" and complete["master_catalog_entries"] == 513
assert complete["e0_primary_sources_preserved"] == 273
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 507
assert complete["remaining_physical_gaps"] == 6
assert complete["e0_sigen_modern_public_report_family_located"] is True
assert complete["e0_sigen_modern_executed_annex_a_certification_located"] is True
assert complete["e0_sigen_modern_remainder_cross_reference_located"] is True
assert complete["e0_sigen_modern_later_account_audit_located"] is True
assert complete["e0_sigen_account_2008_global_report_body_located"] is False
assert complete["e0_uai_saf355_target_certification_located"] is False
assert complete["e0_uai_saf355_target_certifications_located_count"] == 0
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == complete["e0_request_responses_received"] == 0

manifest = json.loads((HERE / "MANIFEST_V154.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V154" and manifest["parent_checkpoint"] == "V153"
assert manifest["new_preserved_sources"] == 4 and manifest["source_bundle_files"] == 12
assert manifest["pdf_visual_controls_new"] == 9
assert manifest["modern_annex_a_certification_located"] is True
assert manifest["uai_saf355_target_certification_located"] is False
assert manifest["executed_settlement_rows_confirmed"] == 0
assert manifest["requests_submitted"] == manifest["responses_received"] == 0

for name in ["README_V154.md", "VEREDICTO_V154.md", "E0_FISCAL_RECONSTRUCTION_V154.md",
             "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V154_A_V155.md"]:
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")
assert not (HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V154_A_V154.md").exists()

combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined and "TARGET_EXTRACT_FOUND" not in combined

print("V154 QA PASS")
