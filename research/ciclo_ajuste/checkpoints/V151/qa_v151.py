from pathlib import Path
import csv
import hashlib
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
AUDIT = REPO / "research" / "ciclo_ajuste" / "source_audit"
BIN = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v151" / "binaries"


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
    "e0_argentina_afg_first_stage_sidif_transaf_architecture",
    "e0_argentina_afg_fifth_stage_legacy_transaf",
    "e0_cgn_circular_2_1999_parameterized_text_file",
    "e0_argentina_dgsiaf_transaf_current_page",
    "e0_dgsiaf_transaf_user_guide_2022",
    "e0_cgn_sigen_instruction_account_2009",
    "e0_cgn_circular_2_2021_uai_closing",
    "e0_sigen_instruction_1_2021_account_certification",
    "e0_sigen_instruction_1_2021_annex_i_bank_movements",
    "e0_sigen_instruction_1_2021_annex_iv_execution_forms",
}

with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as handle:
    catalog = list(csv.DictReader(handle))
assert len(catalog) == 501 and len({row["id"] for row in catalog}) == 501
assert new_ids <= {row["id"] for row in catalog}

census = {row["source_id"]: row for row in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V151.csv")}
provenance = {row["source_id"]: row for row in rows("ARCHIVAL_PROVENANCE_V151.csv")}
assert len(census) == 261 and new_ids <= set(census) and new_ids <= set(provenance)
for source_id in new_ids:
    path = REPO / census[source_id]["local_path"].lstrip("/")
    assert path.is_file() and digest(path) == census[source_id]["sha256"]

bundle = rows("E0_V151_SOURCE_BUNDLE.csv")
assert len(bundle) == 19 and sum(row["catalogued"] == "YES" for row in bundle) == 10
assert all(row["preserved"] == "YES" for row in bundle)
for row in bundle:
    path = BIN / row["filename"]
    assert path.is_file() and path.stat().st_size == int(row["bytes"]) and digest(path) == row["sha256"]

dual = rows("E0_SIDIF_DUAL_DATABASE_AND_TRANSAF_CHAIN_V151.csv")
assert len(dual) == 18
assert {"DUAL_RECORD_EXPECTED", "DUAL_CUSTODIAN_RULE", "NON_CLOSING_ZERO"} <= {row["status"] for row in dual}
assert {"LOCAL_QUERY", "CENTRAL_QUERY", "TRANSMISSION_QUERY", "UAI_QUERY"} <= {row["object"] for row in dual}

transaf = rows("E0_TRANSAF_LOT_AND_LOG_REQUEST_SCHEMA_V151.csv")
assert len(transaf) == 20
assert {"UI_30_DAYS", "BACKEND_ARCHIVE", "NRO_TRANS", "AUTH_RESULT"} <= {row["field_or_control"] for row in transaf}
assert sum(row["temporal_status"] == "DO_NOT_RETROPROJECT" for row in transaf) == 2
assert any(row["temporal_status"] == "UI_NOT_DELETION" for row in transaf)

uai = rows("E0_UAI_2009_2021_THREE_SOURCE_CERTIFICATION_V151.csv")
assert len(uai) == 18
assert {"2009_FORMS", "2009_LOCAL", "2009_CENTRAL", "2009_BANK_SUPPORT", "CERT_NOT_PAYMENT", "TARGET_LIMIT"} <= {row["object"] for row in uai}
assert any(row["status"] == "REQUEST_BY_NAME" for row in uai)

refresh = rows("E0_2008_SPECIFIC_QUERY_AND_SPECIAL_ROUTE_REFRESH_V151.csv")
assert len(refresh) == 14
assert {"2008_SPECIFIC", "SAF355_EXCEPTION", "LOCAL_PARAM", "CENTRAL_PARAM", "SCOPE_LIMIT"} <= {row["object"] for row in refresh}

negative = rows("E0_V151_PUBLIC_SEARCH_NEGATIVE_RESULTS.csv")
assert len(negative) == 10
assert sum(row["status"] == "PUBLIC_BODY_NOT_LOCATED" for row in negative) == 6
assert any(row["status"] == "EXACT_URL_404_NOT_ABSENCE" for row in negative)

objects = rows("E0_V151_REQUEST_OBJECTS.csv")
assert len(objects) == 18 and all(row["status"] == "DRAFT_NOT_SENT" for row in objects)

visual = rows("E0_V151_PDF_VISUAL_CONTROL.csv")
images = rows("E0_V151_IMAGE_VISUAL_CONTROL.csv")
assert len(visual) == 85 and len([row for row in visual if row["control_id"].startswith("PV151_NEW_")]) == 29
assert len(images) == 3 and all(row["result"] == "PASS" for row in images)
assert all(row["result"] == "PASS" for row in visual)

breaks = rows("E0_FISCAL_METHOD_BREAKS_V151.csv")
trace = rows("E0_INFORMATION_REQUEST_TRACEABILITY_V151.csv")
keys = rows("E0_REQUEST_SEARCH_KEY_MATRIX_V151.csv")
required_breaks = {
    "sidif_dual_local_central_records_not_two_events",
    "official_sidif_architecture_not_target_retention_proof",
    "transaf_authentication_signature_not_payment",
    "modern_transaf_lot_schema_not_2008_schema",
    "transaf_30day_ui_not_backend_deletion",
    "uai_three_source_certification_not_target_execution",
    "parameterized_budget_aggregate_not_form_body",
    "uepex_2008_specific_query_not_target_universe",
    "adjacent_2009_instruction_not_2008_target_audit",
}
assert len(breaks) == 258 and required_breaks <= {row["break_id"] for row in breaks}
assert len(trace) == 310 and all(row["status"] == "DRAFT_NOT_SENT" for row in trace)
assert len(keys) == 366
assert {
    "Listado Parametrizado del SIDIF Central", "Listado parametrizado generado en sistema local",
    "consulta específica de movimientos", "SIDIF Central", "TRANSAF", "Certificación UAI",
} <= {row["exact_key"] for row in keys}

register = rows("E0_REQUEST_RESPONSE_REGISTER_V151.csv")
assert len(register) == 6
assert all(row["status"] == "DRAFT_NOT_SENT" and row["submitted_on"] == "N/A" and row["receipt_or_case_id"] == "N/A" for row in register)
for name in [
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V151.md", "REQUEST_BCRA_CRYL_SETTLEMENT_V151.md",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V151.md", "REQUEST_AGN_2018_REPLY_V151.md",
    "REQUEST_CNV_CUSTODY_RECORDS_V151.md", "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V151.md",
]:
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "BORRADOR_NO_ENVIADO" in text or "DRAFT_NOT_SENT" in text

with (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V151.csv").open(encoding="utf-8-sig", newline="") as handle:
    hashes = list(csv.DictReader(handle))
assert sum(row["exists"] == "True" for row in hashes) == 495
assert sum(row["hash_ok"] == "True" for row in hashes) == 495

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V151.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V151" and complete["master_catalog_entries"] == 501
assert complete["e0_primary_sources_preserved"] == 261
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 495
assert complete["remaining_physical_gaps"] == 6
assert complete["e0_sidif_local_central_dual_repository_proved"] is True
assert complete["e0_transaf_authentication_and_lot_route_proved"] is True
assert complete["e0_transaf_2022_schema_valid_for_2008"] is False
assert complete["e0_uai_2009_adjacent_three_source_control_proved"] is True
assert complete["e0_uai_target_certification_located"] is False
assert complete["e0_target_forms_public_bodies_located"] == 0
assert complete["e0_target_transaf_logs_located"] == 0
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0 and complete["e0_request_responses_received"] == 0

manifest = json.loads((HERE / "MANIFEST_V151.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V151" and manifest["parent_checkpoint"] == "V150"
assert manifest["new_preserved_sources"] == 10 and manifest["source_bundle_files"] == 19
assert manifest["sidif_local_central_dual_repository_proved"] is True
assert manifest["transaf_2022_schema_valid_for_2008"] is False
assert manifest["target_forms_public_bodies_located"] == 0 and manifest["target_transaf_logs_located"] == 0
assert manifest["executed_settlement_rows_confirmed"] == 0
assert manifest["requests_submitted"] == 0 and manifest["responses_received"] == 0

for name in [
    "README_V151.md", "VEREDICTO_V151.md", "E0_FISCAL_RECONSTRUCTION_V151.md",
    "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V151_A_V152.md",
]:
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")
assert not list(HERE.glob("*V150*"))
assert not (HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V151_A_V151.md").exists()

combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined and "TARGET_EXTRACT_FOUND" not in combined

print("V151 QA PASS")
