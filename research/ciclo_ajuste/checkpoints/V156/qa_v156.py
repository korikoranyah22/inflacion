from pathlib import Path
import csv
import hashlib
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v156" / "binaries"


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
    "e0_mecon_decree_1359_2004_uai_target_period_duties",
    "e0_sigen_resolution_152_2002_workpaper_ownership_custody_access",
    "e0_sigen_resolution_15_2006_sisio_mandatory_record_schema",
    "e0_cnrt_resolution_1002_2011_sisio_receipt_archive_comparator",
    "e0_sigen_resolution_93_2013_gsepypf_expansion",
}

with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as handle:
    catalog = list(csv.DictReader(handle))
assert len(catalog) == 522 and len({row["id"] for row in catalog}) == 522
assert new_ids <= {row["id"] for row in catalog}

census = {row["source_id"]: row for row in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V156.csv")}
provenance = {row["source_id"]: row for row in rows("ARCHIVAL_PROVENANCE_V156.csv")}
assert len(census) == 282 and new_ids <= set(census) and new_ids <= set(provenance)
for source_id in new_ids:
    path = REPO / census[source_id]["local_path"].lstrip("/")
    assert path.is_file() and digest(path) == census[source_id]["sha256"]
    assert "/v156/binaries/" in census[source_id]["local_path"]
assert census["e0_mecon_decree_1359_2004_uai_target_period_duties"]["use_status"] == "E0_USABLE_TARGET_PERIOD_UAI_DUTY_AUTHORITY"
assert census["e0_sigen_resolution_15_2006_sisio_mandatory_record_schema"]["use_status"] == "E0_USABLE_TARGET_PERIOD_SISIO_MANDATORY_RECORD_SCHEMA"
assert "No demuestra" in census["e0_sigen_resolution_93_2013_gsepypf_expansion"]["caveat"]

bundle = rows("E0_V156_SOURCE_BUNDLE.csv")
assert len(bundle) == 5 and all(row["catalogued"] == "YES" and row["preserved"] == "YES" for row in bundle)
assert {row["role"] for row in bundle} == {
    "TARGET_PERIOD_UAI_DUTIES", "WORKPAPER_OWNERSHIP_CUSTODY_ACCESS",
    "TARGET_PERIOD_SISIO_EXACT_SCHEMA", "LATER_SISIO_IMPLEMENTATION_COMPARATOR",
    "GSEPYPF_EXPANSION_NOT_GSEYP_EQUIVALENCE",
}
for row in bundle:
    path = BIN / row["filename"]
    assert path.is_file() and path.stat().st_size == int(row["bytes"])
    assert digest(path) == row["sha256"]

duties = rows("E0_TARGET_PERIOD_UAI_ECONOMY_DUTY_CHAIN_V156.csv")
assert len(duties) == 18
assert sum(row["status"] == "TARGET_PERIOD_DUTY" for row in duties) == 13
assert {"Planificación", "Contabilidad y presupuesto", "Confiabilidad", "Opinión",
        "Informes", "Desvíos", "Seguimiento"} <= {row["action_or_control"] for row in duties}
assert any(row["status"] == "METHOD_LIMIT" and "0/10" in row["target_implication"] for row in duties)

sisio = rows("E0_SISIO_RES15_2006_EXACT_RECORD_SCHEMA_V156.csv")
assert len(sisio) == 35
required = {row["required_record_or_field"] for row in sisio}
assert {"Uso obligatorio de SISIO WEB", "Cronograma de Emisión de Informes",
        "Constancia de carga por documento nuevo", "Indicador de impacto en Cuenta de Inversión",
        "Instrumento que subsanó observación", "Modelo de observaciones pendientes",
        "Modelo de observaciones regularizadas"} <= required
assert any("72 horas" in row["deadline_or_frequency"] for row in sisio)
assert any("144 horas" in row["deadline_or_frequency"] for row in sisio)
assert {"Sin acción correctiva", "No compartida", "Sin conocimiento UAI", "En trámite", "Regularizada"} <= {
    row["required_record_or_field"].removeprefix("Estado ") for row in sisio if row["status"] == "STATUS_HISTORY"
}
assert any("No significa pago" in row["limit"] for row in sisio)

workpapers = rows("E0_WORKPAPER_OWNERSHIP_CUSTODY_AND_ACCESS_V156.csv")
assert len(workpapers) == 15
assert {"OWNERSHIP_RULE", "DEPOSITARY_RULE", "ACCESS_RULE", "EVIDENCE_RULE",
        "SISIO_WORKPAPER_RULE", "METHOD_LIMIT"} <= {row["status"] for row in workpapers}
assert any("propiedad del organismo" in row["request_consequence"] or "Economía como titular" in row["request_consequence"] for row in workpapers)
assert any("Acceso no es propiedad" in row["limit"] for row in workpapers)

comparison = rows("E0_SISIO_RECEIPT_AND_ARCHIVE_COMPARATOR_V156.csv")
assert len(comparison) == 12
assert sum(row["status"] == "TARGET_PERIOD_RULE" for row in comparison) == 5
assert sum(row["status"] == "LATER_COMPARATOR" for row in comparison) == 7
assert any("No atribuir a Economía 2009" in row["forbidden_use"] for row in comparison)

narrowing = rows("E0_GSEYP_GSEPYPF_NARROWING_V156.csv")
assert len(narrowing) == 12
assert {"GSEyP", "GSEPyPF", "3672/09", "Resolución SIGEN 93/2013"} <= {
    row["token_or_source"] for row in narrowing
}
assert any(row["status"] == "METHOD_LIMIT" and "No fusionar" in row["search_action"] for row in narrowing)

negative = rows("E0_V156_PUBLIC_SEARCH_NEGATIVE_RESULTS.csv")
assert len(negative) == 12 and negative == rows("E0_V156_PUBLIC_SEARCH_NEGATIVE_RESULTS_V156.csv")
assert {"SYSTEM_ENTRY_NOT_PUBLIC", "LOAD_RECEIPT_NOT_LOCATED", "WORKPAPERS_NOT_LOCATED",
        "ACRONYM_EQUIVALENCE_NOT_PROVEN", "TARGET_CERTIFICATES_NOT_LOCATED",
        "BANK_EXECUTION_NOT_LOCATED", "DRAFT_NOT_SENT"} <= {row["status"] for row in negative}

breaks = rows("E0_FISCAL_METHOD_BREAKS_V156.csv")
trace = rows("E0_INFORMATION_REQUEST_TRACEABILITY_V156.csv")
keys = rows("E0_REQUEST_SEARCH_KEY_MATRIX_V156.csv")
objects = rows("E0_V156_REQUEST_OBJECTS.csv")
assert len(breaks) == 307
assert {
    "uai_target_period_duty_not_target_report", "sisio_mandatory_use_not_specific_entry",
    "sisio_receipt_not_report_body", "sisio_account_impact_flag_not_account_validation",
    "regularized_state_not_bank_payment", "sisio_synthesis_not_full_observation_body",
    "workpaper_ownership_not_public_disclosure", "sigen_access_not_sigen_ownership",
    "later_cnrt_archive_flow_not_2009_economy_fact", "gsepypf_expansion_not_gseyp_equivalence",
} <= {row["break_id"] for row in breaks}
assert len(trace) == 392 and all(row["status"] == "DRAFT_NOT_SENT" for row in trace)
assert {"CL156_PLAN_CHRONOGRAM", "CL156_SISIO_RECEIPT", "CL156_ANNEX_II",
        "CL156_WORKPAPER_INDEX", "CL156_ACCESS_SEARCH", "CL156_FINAL_BANK_GATE"} <= {
    row["gap_id"] for row in trace
}
assert len(keys) == 466
assert {"Decreto 1359/2004 Unidad de Auditoría Interna", "Cronograma de Emisión de Informes SISIO 2009",
        "constancia de carga SISIO 0120/09", "Anexo II observaciones pendientes 2009",
        "GSEyP GSEPyPF 3672/09", "71597 152677 2876 C41 C42 C55 banco reversa"} <= {
    row["exact_key"] for row in keys
}
assert len(objects) == 46 and objects == rows("E0_V156_REQUEST_OBJECTS_V156.csv")
assert all(row["status"] == "DRAFT_NOT_SENT" for row in objects)
assert {"SISIO_LOAD_RECEIPT", "SISIO_ANNUAL_PLAN_CHRONOGRAM", "SISIO_ACCOUNT_IMPACT_FLAG",
        "SISIO_OBSERVATION_HISTORY", "SISIO_REGULARIZATION_INSTRUMENT", "SISIO_ANNEX_II_REPORT",
        "SISIO_ANNEX_III_REPORT", "UAI_WORKPAPER_INDEX", "UAI_DEPOSIT_CERTIFICATE",
        "SIGEN_ACCESS_SEARCH"} <= {row["object_id"] for row in objects}

channels = rows("CURRENT_OFFICIAL_SUBMISSION_CHANNELS_V156.csv")
assert len(channels) == 9
assert any("Sindicatura General" in row["institution"] and "DRAFT_NOT_SENT" in row["status"] for row in channels)

visual = rows("E0_V156_PDF_VISUAL_CONTROL.csv")
images = rows("E0_V156_IMAGE_VISUAL_CONTROL.csv")
assert len(visual) == 134 and len(images) == 3
new_visual = [row for row in visual if row["control_id"].startswith("PV156_")]
assert len(new_visual) == 10 and all(row["result"] == "PASS" for row in visual + images)
assert {row["pdf_page"] for row in new_visual} == {str(value) for value in range(1, 11)}
assert all(row["source_id"] == "e0_sigen_resolution_15_2006_sisio_mandatory_record_schema" for row in new_visual)

register = rows("E0_REQUEST_RESPONSE_REGISTER_V156.csv")
assert len(register) == 6
assert all(row["status"] == "DRAFT_NOT_SENT" and row["submitted_on"] == "N/A"
           and row["receipt_or_case_id"] == "N/A" for row in register)
assert all("V156.md" in row["draft_file"] for row in register)
for name in [
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V156.md", "REQUEST_BCRA_CRYL_SETTLEMENT_V156.md",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V156.md", "REQUEST_AGN_2018_REPLY_V156.md",
    "REQUEST_CNV_CUSTODY_RECORDS_V156.md", "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V156.md",
]:
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "BORRADOR_NO_ENVIADO" in text or "DRAFT_NOT_SENT" in text
econ = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V156.md").read_text(encoding="utf-8-sig")
assert "Decreto 1359/2004" in econ and "Resolución SIGEN 152/2002" in econ and "72/144 horas" in econ

with (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V156.csv").open(encoding="utf-8-sig", newline="") as handle:
    hashes = list(csv.DictReader(handle))
assert len(hashes) == 522
assert sum(row["exists"] == "True" for row in hashes) == 516
assert sum(row["hash_ok"] == "True" for row in hashes) == 516

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V156.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V156" and complete["master_catalog_entries"] == 522
assert complete["e0_primary_sources_preserved"] == 282
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 516
assert complete["remaining_physical_gaps"] == 6
assert complete["e0_fiscal_method_breaks_frozen"] == 307
assert complete["e0_request_traceability_rows"] == 392 and complete["e0_request_search_keys"] == 466
assert complete["e0_target_period_uai_authority_located"] is True
assert complete["e0_sisio_mandatory_schema_located"] is True
assert complete["e0_workpaper_ownership_custody_access_located"] is True
assert complete["e0_sisio_target_entry_located"] is False
assert complete["e0_sisio_target_receipt_located"] is False
assert complete["e0_gseyp_gsepypf_equivalence_proved"] is False
assert complete["e0_uai_saf355_target_certifications_located_count"] == 0
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == complete["e0_request_responses_received"] == 0

manifest = json.loads((HERE / "MANIFEST_V156.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V156" and manifest["parent_checkpoint"] == "V155"
assert manifest["new_preserved_sources"] == 5 and manifest["source_bundle_files"] == 5
assert manifest["pdf_visual_controls_total"] == 134 and manifest["pdf_visual_controls_new"] == 10
assert manifest["request_objects"] == 46
assert manifest["target_period_uai_authority_located"] is True
assert manifest["sisio_target_entry_located"] is False and manifest["sisio_target_receipt_located"] is False
assert manifest["gseyp_gsepypf_equivalence_proved"] is False
assert manifest["executed_settlement_rows_confirmed"] == 0
assert manifest["requests_submitted"] == manifest["responses_received"] == 0

for name in ["README_V156.md", "VEREDICTO_V156.md", "E0_FISCAL_RECONSTRUCTION_V156.md",
             "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V156_A_V157.md"]:
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")
assert not (HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V156_A_V156.md").exists()

combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined and "TARGET_EXTRACT_FOUND" not in combined

print("V156 QA PASS")
