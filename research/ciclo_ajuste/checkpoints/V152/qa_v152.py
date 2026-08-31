from pathlib import Path
import csv
import hashlib
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v152" / "binaries"


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
    "e0_cgn_disposition_28_2008_midyear_closing_axt",
    "e0_enre_annual_2009_uai_account_2008_certifications",
    "e0_sigen_memory_2009_account_2008_global_control_report",
    "e0_cgn_disposition_35_2002_parameterized_inconsistency_procedure",
}

with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as handle:
    catalog = list(csv.DictReader(handle))
assert len(catalog) == 505 and len({row["id"] for row in catalog}) == 505
assert new_ids <= {row["id"] for row in catalog}

census = {row["source_id"]: row for row in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V152.csv")}
provenance = {row["source_id"]: row for row in rows("ARCHIVAL_PROVENANCE_V152.csv")}
assert len(census) == 265 and new_ids <= set(census) and new_ids <= set(provenance)
for source_id in new_ids:
    path = REPO / census[source_id]["local_path"].lstrip("/")
    assert path.is_file() and digest(path) == census[source_id]["sha256"]
assert all("v151/binaries" in census[source_id]["local_path"] for source_id in {
    "e0_argentina_afg_first_stage_sidif_transaf_architecture",
    "e0_cgn_sigen_instruction_account_2009",
})

bundle = rows("E0_V152_SOURCE_BUNDLE.csv")
assert len(bundle) == 10 and sum(row["catalogued"] == "YES" for row in bundle) == 4
assert all(row["preserved"] == "YES" for row in bundle)
for row in bundle:
    path = BIN / row["filename"]
    assert path.is_file() and path.stat().st_size == int(row["bytes"])
    assert digest(path) == row["sha256"]

uai = rows("E0_UAI_2008_INSTRUCTIVE_AND_EXECUTED_CERTIFICATION_ROUTE_V152.csv")
assert len(uai) == 20
assert {"INSTR_02_EXISTENCE", "NOTE_84749", "NOTE_86232", "SIGEN_GLOBAL_REPORT", "LIMIT_CERT"} <= {row["object_code"] for row in uai}
assert any(row["status"] == "INSTRUCTIVE_BODY_NOT_LOCATED" for row in uai)
assert any(row["status"] == "NOT_PAYMENT_PROOF" for row in uai)

closing = rows("E0_2008_CLOSING_RECONCILIATION_AND_ARCHIVE_DUTY_V152.csv")
assert len(closing) == 22
closing_text = "\n".join(row["finding"] for row in closing)
assert "listados definitivos" in closing_text and "sistema local" in closing_text
assert "detalle AXT" in closing_text and "archivo oficial" in closing_text
assert any(row["status"] == "NOT_PAYMENT_PROOF" for row in closing)

axt = rows("E0_SAF355_MIDYEAR_AXT_AND_EXCEPTION_ROUTE_V152.csv")
assert len(axt) == 16
assert {"CUT", "OBJECT", "TARGET_IDS", "EXCEPTION", "BRIDGE_BANK"} <= {row["object_code"] for row in axt}
assert any(row["status"] == "DRAFT_NOT_SENT" for row in axt)

param = rows("E0_2008_PARAMETERIZED_INCONSISTENCY_RESPONSE_CHAIN_V152.csv")
assert len(param) == 20
param_text = "\n".join(row["finding"] for row in param)
assert "72 horas" in param_text and "param+código" in param_text
assert "inconsis+código" in param_text and "N° SIDIF" in param_text
assert any("N° SIDIF" in row["finding"] and "N° SAF" in row["finding"] for row in param)

negative = rows("E0_V152_PUBLIC_SEARCH_NEGATIVE_RESULTS.csv")
assert len(negative) == 12
assert {"INSTRUCTIVE_BODY_NOT_LOCATED", "TARGET_CERT_NOT_LOCATED", "AXT_DETAIL_NOT_LOCATED", "TARGET_ROWS_NOT_LOCATED"} <= {row["status"] for row in negative}
assert negative == rows("E0_V152_PUBLIC_SEARCH_NEGATIVE_RESULTS_V152.csv")

objects = rows("E0_V152_REQUEST_OBJECTS.csv")
assert len(objects) == 18 and all(row["status"] == "DRAFT_NOT_SENT" for row in objects)
assert {"INSTR_02", "UAI_CERT_IV", "SIGEN_GLOBAL", "FINAL_LISTS", "AXT_DETAIL", "PARAM_EMAIL"} <= {row["object_id"] for row in objects}
assert objects == rows("E0_V152_REQUEST_OBJECTS_V152.csv")

visual = rows("E0_V152_PDF_VISUAL_CONTROL.csv")
images = rows("E0_V152_IMAGE_VISUAL_CONTROL.csv")
assert len(visual) == 98 and len(visual) - 85 == 13
assert len([row for row in visual if row["control_id"].startswith("PV152_")]) == 13
assert len(images) == 3
assert all(row["result"] == "PASS" for row in visual + images)

breaks = rows("E0_FISCAL_METHOD_BREAKS_V152.csv")
trace = rows("E0_INFORMATION_REQUEST_TRACEABILITY_V152.csv")
keys = rows("E0_REQUEST_SEARCH_KEY_MATRIX_V152.csv")
required_breaks = {
    "uai_02_2008_existence_not_saf355_certification",
    "enre_internal_note_ids_not_saf355_ids",
    "uai_certification_not_bank_execution",
    "sigen_global_account_report_not_target_audit",
    "midyear_axt_balance_not_yearend_transaction",
    "saf355_midyear_table_exception_not_record_absence",
    "signed_conformity_or_archive_certificate_not_payment",
    "adjustment_form_not_new_economic_event",
    "instruction_1_2009_audit_not_02_2008_certification",
}
assert len(breaks) == 267 and required_breaks <= {row["break_id"] for row in breaks}
assert len(trace) == 326 and all(row["status"] == "DRAFT_NOT_SENT" for row in trace)
assert len(keys) == 382
assert {"Instructivo de Trabajo SGN N° 02/2008", "param355", "inconsis355", "N° SIDIF; N° SAF", "83106000"} <= {row["exact_key"] for row in keys}

register = rows("E0_REQUEST_RESPONSE_REGISTER_V152.csv")
assert len(register) == 6
assert all(row["status"] == "DRAFT_NOT_SENT" and row["submitted_on"] == "N/A" and row["receipt_or_case_id"] == "N/A" for row in register)
for name in [
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V152.md",
    "REQUEST_BCRA_CRYL_SETTLEMENT_V152.md",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V152.md",
    "REQUEST_AGN_2018_REPLY_V152.md",
    "REQUEST_CNV_CUSTODY_RECORDS_V152.md",
    "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V152.md",
]:
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "BORRADOR_NO_ENVIADO" in text or "DRAFT_NOT_SENT" in text

with (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V152.csv").open(encoding="utf-8-sig", newline="") as handle:
    hashes = list(csv.DictReader(handle))
assert sum(row["exists"] == "True" for row in hashes) == 499
assert sum(row["hash_ok"] == "True" for row in hashes) == 499

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V152.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V152" and complete["master_catalog_entries"] == 505
assert complete["e0_primary_sources_preserved"] == 265
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 499
assert complete["remaining_physical_gaps"] == 6
assert complete["e0_uai_instruction_02_2008_existence_proved"] is True
assert complete["e0_uai_instruction_02_2008_body_located"] is False
assert complete["e0_uai_saf355_target_certification_located"] is False
assert complete["e0_sigen_account_2008_global_report_existence_proved"] is True
assert complete["e0_sigen_account_2008_global_report_body_located"] is False
assert complete["e0_saf355_midyear_axt_duty_proved"] is True
assert complete["e0_parameterized_signed_inconsistency_schema_proved"] is True
assert complete["e0_target_forms_public_bodies_located"] == 0
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == complete["e0_request_responses_received"] == 0

manifest = json.loads((HERE / "MANIFEST_V152.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V152" and manifest["parent_checkpoint"] == "V151"
assert manifest["new_preserved_sources"] == 4 and manifest["source_bundle_files"] == 10
assert manifest["pdf_visual_controls_new"] == 13
assert manifest["uai_instruction_02_2008_existence_proved"] is True
assert manifest["uai_instruction_02_2008_body_located"] is False
assert manifest["target_forms_public_bodies_located"] == 0
assert manifest["executed_settlement_rows_confirmed"] == 0
assert manifest["requests_submitted"] == manifest["responses_received"] == 0

for name in [
    "README_V152.md", "VEREDICTO_V152.md", "E0_FISCAL_RECONSTRUCTION_V152.md",
    "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V152_A_V153.md",
]:
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")
assert not (HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V152_A_V152.md").exists()

combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined and "TARGET_EXTRACT_FOUND" not in combined

print("V152 QA PASS")
