from pathlib import Path
import csv
import hashlib
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
AUDIT = REPO / "research" / "ciclo_ajuste" / "source_audit"


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


new_ids = {
    "e0_mecon_uai_report_24_2019_account_2018",
    "e0_mecon_uai_report_37_2023_account_2022",
    "e0_mecon_uai_report_48_2023_saf355_closure",
    "e0_agn_report_65_2022_sigade_information_system",
    "e0_agn_resolution_86_2021_public_debt_control",
}

with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as handle:
    catalog = list(csv.DictReader(handle))
assert len(catalog) == 469 and len({row["id"] for row in catalog}) == 469
assert new_ids <= {row["id"] for row in catalog}

census = {row["source_id"]: row for row in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V147.csv")}
provenance = {row["source_id"]: row for row in rows("ARCHIVAL_PROVENANCE_V147.csv")}
assert len(census) == 229 and new_ids <= set(census) and new_ids <= set(provenance)
for source_id in new_ids:
    path = REPO / census[source_id]["local_path"].lstrip("/")
    assert path.is_file() and digest(path) == census[source_id]["sha256"]

ladder = rows("E0_AGN_OFFICIAL_SETTLEMENT_AUDIT_LADDER_V147.csv")
branch = rows("E0_ANEXO_K_OFF_CUADRO1A_TARGET_BRANCH_V147.csv")
risks = rows("E0_SIGADE_DATA_QUALITY_AND_SIDECAR_RISK_V147.csv")
truth = rows("E0_CROSS_SYSTEM_PAYMENT_STATE_TRUTH_TABLE_V147.csv")
precision = rows("E0_REPO_DISPLAY_PRECISION_REASSESSMENT_V147.csv")
objects = rows("E0_V147_REQUEST_OBJECTS_V147.csv")
negative = rows("E0_V147_PUBLIC_SEARCH_NEGATIVE_RESULTS_V147.csv")
visual = rows("E0_V147_PDF_VISUAL_CONTROL.csv")

assert len(ladder) == 13
assert "mayorizado_por_sigade" in {row["evidence_object"] for row in ladder}
assert any(row["evidence_object"] == "movimientos_bancarios_tgn" for row in ladder)
assert any(row["evidence_object"] == "custodia_cryl" and "Condicional" in row["target_2008_use"] for row in ladder)

assert len(branch) == 11
branch_values = {row["field_or_rule"]: row["value"] for row in branch}
assert branch_values["sigade_code"] == "83106000"
assert branch_values["description"] == "COMISIONES - BANCO NACION"
assert branch_values["amount_ars"] == "32270.30"
assert {branch_values["sidif_form_1"], branch_values["sidif_form_2"], branch_values["sidif_form_3"]} == {"71597", "152677", "2876"}
assert branch_values["cuadro1a_rule"] == "OUTSIDE_CUADRO_1A"
assert all(row["target_payment_confirmed"] == "FALSE" for row in branch)

assert len(risks) == 15 and any(row["risk_or_capability"] == "shared_spreadsheets" for row in risks)
assert all(row["target_2008_proof"] == "FALSE" for row in risks)
assert len(truth) == 12 and any(row["sigade_state"] == "ABSENT" and "does not negate" in row["permitted_conclusion"] for row in truth)
assert len(precision) == 12
precision_map = {row["datum"]: row["value"] for row in precision}
assert precision_map["displayed_difference"] == "0.45"
assert precision_map["arithmetic_error_proved"] == "FALSE"
assert precision_map["unrounded_components_located"] == "FALSE"
assert len(objects) == 18 and all(row["status"] == "DRAFT_NOT_SENT" for row in objects)
assert len(negative) == 8 and all(row["status"] == "PUBLIC_MANUAL_OR_EXPORT_NOT_LOCATED" for row in negative)
assert len(visual) == 39 and all(row["result"] == "PASS" for row in visual)

legacy_repo = rows("E0_REPO_COMMISSION_ACCOUNT_LEAD_V147.csv")
assert not any(row["datum"] == "published_internal_gap" for row in legacy_repo)
assert any(row["datum"] == "displayed_values_difference" and row["value"] == "0.45" for row in legacy_repo)

breaks = rows("E0_FISCAL_METHOD_BREAKS_V147.csv")
trace = rows("E0_INFORMATION_REQUEST_TRACEABILITY_V147.csv")
keys = rows("E0_REQUEST_SEARCH_KEY_MATRIX_V147.csv")
assert len(breaks) == 224
required_breaks = {
    "target_anexo_k_outside_cuadro1a",
    "sigade_absence_not_nonpayment",
    "siche_public_manual_export_not_located",
    "spreadsheet_sidecar_essential_not_system_row",
    "cryl_conditional_for_commission",
    "later_holdout_mismatch_not_target_2008",
}
assert required_breaks <= {row["break_id"] for row in breaks}
repo_break = next(row for row in breaks if row["break_id"] == "uai_repo_arithmetic_gap_045m")
assert repo_break["dimension"] == "precision" and "no afirmar error" in repo_break["rule"]
assert len(trace) == 247 and all(row["status"] == "DRAFT_NOT_SENT" for row in trace)
assert len(keys) == 303
assert {"mayorizados por SIGADE", "71597", "152677", "2876", "Coordinación de Cuentas Bancarias"} <= {row["exact_key"] for row in keys}

register = rows("E0_REQUEST_RESPONSE_REGISTER_V147.csv")
assert len(register) == 6 and all(row["status"] == "DRAFT_NOT_SENT" for row in register)
assert all(row["submitted_on"] == "N/A" and row["receipt_or_case_id"] == "N/A" for row in register)
request_files = [
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V147.md",
    "REQUEST_BCRA_CRYL_SETTLEMENT_V147.md",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V147.md",
    "REQUEST_AGN_2018_REPLY_V147.md",
    "REQUEST_CNV_CUSTODY_RECORDS_V147.md",
    "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V147.md",
]
for name in request_files:
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "BORRADOR_NO_ENVIADO" in text or "DRAFT_NOT_SENT" in text

with (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V147.csv").open(encoding="utf-8-sig", newline="") as handle:
    hashes = list(csv.DictReader(handle))
assert sum(row["exists"] == "True" for row in hashes) == 463
assert sum(row["hash_ok"] == "True" for row in hashes) == 463

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V147.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V147"
assert complete["master_catalog_entries"] == 469
assert complete["e0_primary_sources_preserved"] == 229
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 463
assert complete["e0_target_anexo_k_outside_cuadro1a"] is True
assert complete["e0_target_sidif_ids"] == ["71597", "152677", "2876"]
assert complete["e0_sigade_absence_proves_nonpayment"] is False
assert complete["e0_siche_public_manual_or_export_located"] is False
assert complete["e0_repo_displayed_components_difference_ars_millions"] == "0.45"
assert complete["e0_repo_arithmetic_error_proved"] is False
assert complete["e0_repo_unrounded_components_located"] is False
assert complete["e0_repo_published_internal_gap_ars_millions"] == "SUPERSEDED_NOT_PROVEN_AS_ERROR"
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0 and complete["e0_request_responses_received"] == 0

manifest = json.loads((HERE / "MANIFEST_V147.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V147" and manifest["parent_checkpoint"] == "V146"
assert manifest["new_preserved_sources"] == 5
assert manifest["repo_arithmetic_error_proved"] is False
assert manifest["executed_settlement_rows_confirmed"] == 0
assert manifest["requests_submitted"] == 0 and manifest["responses_received"] == 0

for name in ("README_V147.md", "VEREDICTO_V147.md", "E0_FISCAL_RECONSTRUCTION_V147.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V147_A_V148.md"):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "0/10" in text
assert "no un error probado" in (HERE / "README_V147.md").read_text(encoding="utf-8-sig")
assert not list(HERE.glob("*V146*"))
assert not (HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V147_A_V147.md").exists()

combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined and "TARGET_EXTRACT_FOUND" not in combined
print("V147 QA PASS")
