from __future__ import annotations

from pathlib import Path
import csv
import hashlib
import html as html_lib
import json
import re

from pypdf import PdfReader


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
V123 = HERE.parent / "V123"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pdf_text(path: Path) -> str:
    extracted = "\n".join((page.extract_text() or "") for page in PdfReader(path).pages).replace("\u25a1", " ")
    return re.sub(r"\s+", " ", extracted)


def visible_html(path: Path) -> str:
    data = path.read_bytes()
    try:
        raw = data.decode("utf-8")
    except UnicodeDecodeError:
        raw = data.decode("latin-1")
    raw = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", raw)
    raw = re.sub(r"(?is)<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html_lib.unescape(raw))


catalog = read_csv(REPO / "data" / "fuentes" / "FUENTES.csv")
assert len(catalog) == 294
assert len({row["id"] for row in catalog}) == 294
catalog_by_id = {row["id"]: row for row in catalog}
new_source_ids = {
    "e0_merval_sistema_transferencias_2004_wayback",
    "e0_caja_manual_dtc_control_cambios_m32002",
    "e0_caja_memoria_estados_2006_archivo_2007",
}
assert new_source_ids <= catalog_by_id.keys()


census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V124.csv")
census_v123 = read_csv(V123 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V123.csv")
assert len(census) == 95 and len(census_v123) == 92
assert {row["source_id"] for row in census_v123} < {row["source_id"] for row in census}
assert {row["source_id"] for row in census} - {row["source_id"] for row in census_v123} == new_source_ids
assert all(row["primary_source"] == "YES" and row["preserved"] == "YES" for row in census)
source_text: dict[str, str] = {}
for source_id in new_source_ids:
    source = catalog_by_id[source_id]
    local = REPO / source["archivo_local"].lstrip("/")
    assert local.is_file() and digest(local) == source["sha256"]
    assert next(row for row in census if row["source_id"] == source_id)["sha256"] == source["sha256"]
    source_text[source_id] = visible_html(local) if local.suffix.lower() == ".html" else pdf_text(local)
manual = catalog_by_id["e0_caja_sistema_transferencias_electronicas_manual"]
manual_path = REPO / manual["archivo_local"].lstrip("/")
assert manual_path.is_file() and digest(manual_path) == "27110add87fdf7ec658ccf5a94671e4ea4e3ca514f6b4a30343b6589d22c4d20"
manual_text = pdf_text(manual_path)
assert all(token in manual_text for token in ("Marzo de 2000", "TRANSFERENCIAS DIFERIDAS", "batch nocturno", "matching"))
assert all(token in source_text["e0_merval_sistema_transferencias_2004_wayback"] for token in ("Sistema de Transferencias Electr", "autorizar", "modificar", "baja"))
assert b"SCG" in (REPO / catalog_by_id["e0_merval_sistema_transferencias_2004_wayback"]["archivo_local"].lstrip("/")).read_bytes()
assert all(token in source_text["e0_caja_manual_dtc_control_cambios_m32002"] for token in ("CONTROL DE CAMBIOS", "Septiembre 2007", "Mayo 2009", "fecha de vigencia"))
assert all(token in source_text["e0_caja_memoria_estados_2006_archivo_2007"] for token in ("TECNOLOGÍA DE INFORMACIÓN", "Transferencias", "31 de diciembre de 2006"))
assert catalog_by_id["e0_merval_sistema_transferencias_2004_wayback"]["sha256"] == "3a7c5d5f476e5e8ac0266f17e37fe50115e7af2c7c263bc728365df2a7a8e339"
assert catalog_by_id["e0_caja_manual_dtc_control_cambios_m32002"]["sha256"] == "ca36c92b1c39f3be03fd097a643bc48975a43802075ddeb5dcc6625f9d57df8a"
assert catalog_by_id["e0_caja_memoria_estados_2006_archivo_2007"]["sha256"] == "95a89dd4a614adbe6cd1e52d05fab9e00f65efb6196ea997f8ebb1edd2752163"


chain = read_csv(HERE / "E0_CRYL_EFFECTIVE_VERSION_CHAIN_V124.csv")
terms = read_csv(HERE / "E0_BUYBACK_MODALITY_TERM_AUDIT_V124.csv")
cga_map = read_csv(HERE / "E0_CRYL_CGA_RECORD_MAP_V124.csv")
assert len(chain) == 9 and len({row["chain_id"] for row in chain}) == 9
assert {"A 3191", "A 3253", "A 3621", "B 7971", "B 9173", "B 10469"} <= {
    re.sub(r"^Comunicación ", "", row["norm_or_artifact"]) for row in chain
}
target_2008 = next(row for row in chain if row["chain_id"] == "CH122_07")
assert target_2008["evidence_status"] == "TARGET_PROCEDURE_EXACT_MODALITY_UNRESOLVED"
assert "silencio" in target_2008["prohibited_inference"].lower()
assert len(terms) == 8 and len({row["audit_id"] for row in terms}) == 8
assert next(row for row in terms if row["audit_id"] == "TA122_01")["visible_count"] == "0"
assert next(row for row in terms if row["audit_id"] == "TA122_03")["visible_count"] == "8"
assert next(row for row in terms if row["audit_id"] == "TA122_06")["visible_count"] == "1"
assert len(cga_map) == 8 and len({row["record_id"] for row in cga_map}) == 8
assert {"CGAEEEEE.NN", "CGAEEEEE.INN"} <= {row["exact_file_pattern"] for row in cga_map}
assert next(row for row in cga_map if row["record_id"] == "CGA122_05")["caveat"] == "CONDITIONAL_NOT_SETTLED"


procedure_2008 = visible_html(
    REPO / catalog_by_id["e0_argentina_rc_212_24_2008_recompra"]["archivo_local"].lstrip("/")
)
procedure_2009 = visible_html(
    REPO / catalog_by_id["e0_argentina_rc_113_34_2009_boden12_strip"]["archivo_local"].lstrip("/")
)
for token in ("DVP", "FD&P", "FTC", "CRYL", "X-400", "CGA", "MCT", "TSA", "SIGADE"):
    assert re.search(re.escape(token), procedure_2008, re.I) is None
    assert re.search(re.escape(token), procedure_2009, re.I) is None
assert len(re.findall("Caja de Valores", procedure_2008, re.I)) == 8
assert len(re.findall("BANCO CENTRAL DE LA REPUBLICA ARGENTINA", procedure_2008, re.I)) == 7
assert len(re.findall("cuenta corriente", procedure_2008, re.I)) == 4
assert len(re.findall("modalidad diferida", procedure_2008, re.I)) == 1
assert "Resolución Conjunta Nº 212" in procedure_2009


ledger = read_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V124.csv")
breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V124.csv")
assert len(ledger) == 125 and len({row["ledger_id"] for row in ledger}) == 125
assert len(breaks) == 85 and len({row["break_id"] for row in breaks}) == 85
assert {
    "adjacent_debt_procedure_not_target_buyback_usage",
    "record_schema_not_target_record",
    "historical_regime_chain_not_target_modality",
    "cga_validation_not_liquidation",
    "cga_code_continuity_not_record_preservation",
    "procedure_silence_not_negative_use",
    "deferred_modality_not_tsa_channel",
    "legacy_form_not_contemporaneous_2008_use",
    "matching_fields_not_completed_target_transfer",
    "current_nsc_rule_not_historical_rule",
    "isin_not_cvsa_custody_code",
    "parent_security_code_not_strip_subspecies_code",
    "bank_disclosure_identifier_not_target_settlement",
    "near_contemporaneous_deferred_form_not_exact_2008_edition",
    "manual_print_date_not_2008_effective_revision",
    "archived_system_listing_not_exact_2008_revision",
    "parallel_manual_revision_log_not_target_manual_vigency",
    "institutional_transfer_activity_not_target_settlement",
} <= {row["break_id"] for row in breaks}
assert not any(
    row["realization_status"] == "CASH_SETTLED"
    for row in ledger
    if row["ledger_id"] in {"F122", "F123", "F124", "F125"}
)


current = read_csv(HERE / "CURRENT_STATE_V124.csv")
coverage = read_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V124.csv")
assert len(current) == 39
assert sum(row["strict_panel_status"] == "ELIGIBLE" for row in current) == 30
assert STRICT in " ".join(" ".join(row.values()) for row in coverage)


channels = read_csv(HERE / "CURRENT_OFFICIAL_SUBMISSION_CHANNELS_V124.csv")
assert len(channels) == 7 and len({row["channel_id"] for row in channels}) == 7
assert all(row["verified_on"] == "2026-08-29" and "VERIFIED" in row["status"] for row in channels)

responses = read_csv(HERE / "E0_REQUEST_RESPONSE_REGISTER_V124.csv")
assert len(responses) == 6 and len({row["request_id"] for row in responses}) == 6
assert {row["request_id"] for row in responses} == {
    "REQ124_ECON", "REQ124_BCRA", "REQ124_BNA", "REQ124_AGN", "REQ124_CNV", "REQ124_CAJA"
}
assert all(row["status"] == "DRAFT_NOT_SENT" for row in responses)
assert all(row["submitted_on"] == "N/A" and row["receipt_or_case_id"] == "N/A" for row in responses)
assert all(row["response_class"] == "NO_RESPONSE_EXPECTED_BEFORE_SUBMISSION" for row in responses)

expected_counts = {
    "REQ124_ECON": 16,
    "REQ124_BCRA": 21,
    "REQ124_BNA": 9,
    "REQ124_AGN": 7,
    "REQ124_CNV": 8,
    "REQ124_CAJA": 13,
}
trace = read_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V124.csv")
assert len(trace) == 74 and len({row["trace_id"] for row in trace}) == 74
assert {row["request_id"] for row in trace} == set(expected_counts)
for request_id, count in expected_counts.items():
    assert sum(row["request_id"] == request_id for row in trace) == count
assert all(row["status"] == "DRAFT_NOT_SENT" for row in trace)
assert any("CGAEEEEE.NN" in row["identifiers"] for row in trace)
assert any("modalidad diferida" in row["identifiers"] for row in trace)

system_map = read_csv(HERE / "E0_DOCUMENT_SYSTEM_TEMPORAL_MAP_V124.csv")
assert len(system_map) == 6 and len({row["institution"] for row in system_map}) == 6
bcra_route = next(row for row in system_map if row["institution"] == "BCRA / CRyL")
assert "CGA" in bcra_route["contemporaneous_route"] and "X-400" in bcra_route["contemporaneous_route"]
assert "IDEAR" in bcra_route["later_route_or_migration"]

authorities = read_csv(HERE / "E0_ARCHIVAL_RETENTION_AUTHORITY_MATRIX_V124.csv")
negative = read_csv(HERE / "E0_NEGATIVE_RESPONSE_ADEQUACY_V124.csv")
assert len(authorities) == 10
assert len(negative) == 14 and {row["adequacy_id"] for row in negative} == {f"NR122_{i:02d}" for i in range(1, 15)}
assert sum(row["effect_on_gap"] == "NO_CIERRA" for row in negative) == 13

producer_map = read_csv(HERE / "E0_RECORD_PRODUCER_SYSTEM_MAP_V124.csv")
search_keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V124.csv")
attachments = read_csv(HERE / "E0_REQUEST_ATTACHMENT_MINIMUM_V124.csv")
assert len(producer_map) == 22 and len({row["map_id"] for row in producer_map}) == 22
assert {"CG1", "CG2", "CG3", "CG4", "CG5 y CG6", "CG7", "CGAEEEEE.NN", "CGAEEEEE.INN"} <= {
    row["system_or_record"] for row in producer_map
}
assert len(search_keys) == 53 and len({row["key_id"] for row in search_keys}) == 53
assert {row["request_id"] for row in search_keys} == {row["request_id"] for row in responses}
assert any(row["exact_key"] == "CGA;CGAEEEEE.NN;CGAEEEEE.INN" for row in search_keys)
assert any("CONDICIONAL" in row["exact_key"] for row in search_keys)
assert any(row["exact_key"] == "5426;5427;45698;45701;5326" for row in search_keys)
assert any("F-33914.01" in row["exact_key"] and "F-33915.01" in row["exact_key"] for row in search_keys)
assert any("Marzo de 2000" in row["exact_key"] and "SLIQ" in row["exact_key"] for row in search_keys)
assert any("CONTROL DE CAMBIOS" in row["exact_key"] and "Mayo 2009" in row["exact_key"] for row in search_keys)
assert any("2008-09-02" in row["exact_key"] and "0306/40000" in row["exact_key"] for row in search_keys)
assert len(attachments) == 7 and {row["request_id"] for row in attachments} == {row["request_id"] for row in responses}

closures = read_csv(HERE / "E0_REQUEST_CLOSURE_CRITERIA_V124.csv")
assert len(closures) == 8 and len({row["gap_id"] for row in closures}) == 8
assert {row["gap_id"] for row in trace} <= {row["gap_id"] for row in closures}
assert all(row["initial_status"].startswith(("OPEN_", "PUBLIC_CROSSWALK_")) for row in closures)

deferred = read_csv(HERE / "E0_DEFERRED_MODALITY_EQUIVALENCE_AUDIT_V124.csv")
crosswalk = read_csv(HERE / "E0_SECURITY_IDENTIFIER_CROSSWALK_V124.csv")
stages = read_csv(HERE / "E0_CAJA_CRYL_SETTLEMENT_STAGE_MATRIX_V124.csv")
assert len(deferred) == 11 and len({row["audit_id"] for row in deferred}) == 11
assert next(row for row in deferred if row["audit_id"] == "DM124_05")["evidence_status"] == "CHANNEL_AND_MODALITY_COEXIST"
assert next(row for row in deferred if row["audit_id"] == "DM124_07")["evidence_status"] == "DEFERRED_FORM_PRACTICE_CONFIRMED_2009"
assert next(row for row in deferred if row["audit_id"] == "DM124_08")["evidence_status"] == "EDITION_DATE_AND_MECHANISM_CONFIRMED_EFFECTIVE_2008_REVISION_OPEN"
assert next(row for row in deferred if row["audit_id"] == "DM124_09")["evidence_status"] == "SYSTEM_AND_DOCUMENTATION_PUBLICLY_AVAILABLE_2004"
assert next(row for row in deferred if row["audit_id"] == "DM124_10")["evidence_status"] == "REVISION_LOG_PRACTICE_CONFIRMED_NOT_TARGET_MANUAL"
assert next(row for row in deferred if row["audit_id"] == "DM124_11")["evidence_status"] == "INSTITUTIONAL_ACTIVITY_CONFIRMED_MODALITY_AND_TARGET_OPEN"
assert len(crosswalk) == 5 and len({row["isin"] for row in crosswalk}) == 5
assert {row["historical_code"] for row in crosswalk} == {"5426", "5427", "45698", "45701", "5326"}
assert next(row for row in crosswalk if row["isin"] == "ARARGE03G415")["evidence_status"] == "EXACT_CONTEMPORANEOUS_CAJA_CODE_TWO_BANK_DISCLOSURES"
assert "5426" in next(row for row in crosswalk if row["isin"] == "ARARGE03G415")["prohibited_inference"]
assert len(stages) == 8 and len({row["stage_id"] for row in stages}) == 8
assert {"instrucción diferida", "matching/autorización", "cierre de recepción T+2", "informe Caja T+3 10 h", "pago T+3"} <= {row["stage"] for row in stages}

drafts = [HERE / row["draft_file"] for row in responses]
assert all(path.is_file() for path in drafts)
for path in drafts:
    text = path.read_text(encoding="utf-8")
    assert "BORRADOR_NO_ENVIADO" in text
    assert "[NOMBRE Y APELLIDO / RAZÓN SOCIAL]" in text
    assert "Atentamente" in text
bcra = (HERE / "REQUEST_BCRA_CRYL_SETTLEMENT_V124.md").read_text(encoding="utf-8")
economia = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V124.md").read_text(encoding="utf-8")
caja = (HERE / "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V124.md").read_text(encoding="utf-8")
assert all(token in bcra for token in ("CGAEEEEE.NN", "CGAEEEEE.INN", "X-400/MCT", "condicional a futura liquidación", "IDEAR"))
assert "modalidad diferida" in economia and "confirmación T+3" in economia and "no nombra" in economia
assert all(token in caja for token in ("CGAEEEEE.NN", "CGAEEEEE.INN", "1001", "cuenta 04", "condicional a futura liquidación"))
for text in (bcra, economia, caja):
    assert all(token in text for token in ("5426", "5427", "45698", "45701", "ARARGE03G415"))
assert all(token in caja for token in ("F-33914.01", "F-33915.01", "fecha límite de matching"))
assert all(token in caja for token in ("SLIQ/SCG", "marzo de 2000", "registro maestro", "control de cambios", "MU-32002"))

package = (HERE / "E0_INSTITUTIONAL_REQUEST_PACKAGE_V124.md").read_text(encoding="utf-8")
checklist = (HERE / "REQUEST_SUBMISSION_CHECKLIST_V124.md").read_text(encoding="utf-8")
assert "Estado general: **BORRADOR_NO_ENVIADO**" in package
assert all(name in package for name in (
    "E0_CRYL_EFFECTIVE_VERSION_CHAIN_V124.csv",
    "E0_BUYBACK_MODALITY_TERM_AUDIT_V124.csv",
    "E0_CRYL_CGA_RECORD_MAP_V124.csv",
    "E0_DEFERRED_MODALITY_EQUIVALENCE_AUDIT_V124.csv",
    "E0_SECURITY_IDENTIFIER_CROSSWALK_V124.csv",
    "E0_CAJA_CRYL_SETTLEMENT_STAGE_MATRIX_V124.csv",
))
assert "22 productores" in package and "53 claves" in package and "once pruebas" in package
assert "NINGÚN_PEDIDO_ENVIADO" in checklist
assert "CGAEEEEE.INN" in checklist and "condicional a futura liquidación" in checklist

evidence = read_csv(HERE / "HISTORICAL_EVIDENCE_COVERAGE_V124.csv")
state = next(row for row in evidence if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra")
assert state["quality"].endswith("FIVE_CAJA_CODES_AND_PRE_TARGET_DEFERRED_SYSTEM_CHAIN_PRESERVED")
assert "cinco isin" in state["gap"].lower() and "revisión efectiva" in state["gap"].lower()
queue = read_csv(HERE / "HISTORICAL_SOURCE_QUEUE_V124.csv")
state_queue = [row for row in queue if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra"]
assert len(state_queue) == 2
assert all(row["status"] == "INSTITUTIONAL_REQUEST_SETTLEMENT_AND_EXACT_2008_EFFECTIVE_REVISION_KEYS_READY_NOT_SENT" for row in state_queue)

hash_rows = read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V124.csv")
assert len(hash_rows) == 294
assert sum(row["exists"] == "True" for row in hash_rows) == 289
assert sum(row["hash_ok"] == "True" for row in hash_rows) == 289

completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V124.json").read_text(encoding="utf-8"))
assert completeness["checkpoint"] == "V124"
assert completeness["state"] == "E0_FIVE_CAJA_CODES_DEFERRED_MANUAL_2000_SYSTEM_2004_PRACTICE_2009_TARGET_2008_REVISION_OPEN_NOT_SENT"
assert completeness["master_catalog_entries"] == 294
assert completeness["physical_local_copies"] == 289
assert completeness["physical_local_hash_ok"] == 289
assert completeness["e0_primary_sources_preserved"] == 95
assert completeness["e0_quality"].endswith("FIVE_CAJA_CODES_AND_PRE_TARGET_DEFERRED_SYSTEM_CHAIN_PRESERVED")
assert completeness["sources_newly_preserved_v124"] == 3
assert completeness["e0_fiscal_ledger_rows"] == 125
assert completeness["e0_fiscal_method_breaks_frozen"] == 85
assert completeness["e0_request_drafts"] == 6
assert completeness["e0_request_traceability_rows"] == 74
assert completeness["e0_record_producer_system_rows"] == 22
assert completeness["e0_request_search_keys"] == 53
assert completeness["e0_cryl_effective_version_chain_rows"] == 9
assert completeness["e0_buyback_modality_term_audit_rows"] == 8
assert completeness["e0_cryl_cga_record_map_rows"] == 8
assert completeness["e0_deferred_modality_equivalence_audit_rows"] == 11
assert completeness["e0_security_identifier_crosswalk_rows"] == 5
assert completeness["e0_caja_cryl_settlement_stage_rows"] == 8
assert completeness["e0_requests_submitted"] == 0
assert completeness["e0_request_responses_received"] == 0
assert completeness["e0_request_package_status"] == "DRAFT_NOT_SENT"
assert completeness["closed_network_gate"] == "NO" and completeness["strict_coverage_pct"] == STRICT

inherited = read_csv(HERE / "INHERITED_QA_STATUS_V124.csv")
assert next(row for row in inherited if row["script"] == "qa_v120.py")["post_v124_result"] == "EXPECTED_SUPERSEDED_ASSERTION"
assert next(row for row in inherited if row["script"] == "qa_v121.py")["post_v124_result"] == "EXPECTED_SUPERSEDED_ASSERTION"
assert next(row for row in inherited if row["script"] == "qa_v122.py")["post_v124_result"] == "EXPECTED_SUPERSEDED_ASSERTION"
assert next(row for row in inherited if row["script"] == "qa_v123.py")["post_v124_result"] == "EXPECTED_SUPERSEDED_ASSERTION"
assert next(row for row in inherited if row["script"] == "qa_v124.py")["post_v124_result"] == "PASS"
assert all(
    next(row for row in inherited if row["script"] == f"qa_v{i}.py")["post_v124_result"] == "PASS"
    for i in (98, 100, 101, 102, 103, 104, 105, 106)
)

manifest = json.loads((HERE / "MANIFEST_V124.json").read_text(encoding="utf-8"))
assert manifest["checkpoint"] == "V124" and manifest["parent_checkpoint"] == "V123"
assert manifest["e0_primary_sources"] == 95 and manifest["new_primary_sources"] == 3
assert manifest["fiscal_ledger_rows"] == 125 and manifest["fiscal_method_breaks"] == 85
assert manifest["request_traceability_rows"] == 74 and manifest["record_producer_system_rows"] == 22
assert manifest["request_search_keys"] == 53 and manifest["request_attachment_rows"] == 7
assert manifest["cryl_effective_version_chain_rows"] == 9
assert manifest["buyback_modality_term_audit_rows"] == 8
assert manifest["cryl_cga_record_map_rows"] == 8
assert manifest["deferred_modality_equivalence_audit_rows"] == 11
assert manifest["security_identifier_crosswalk_rows"] == 5
assert manifest["caja_cryl_settlement_stage_rows"] == 8
assert manifest["requests_submitted"] == 0 and manifest["responses_received"] == 0
for item in manifest["files"]:
    path = HERE / item["path"]
    assert path.stat().st_size == item["bytes"], path
    assert digest(path) == item["sha256"], path

global_manifest = json.loads((CYCLE / "MANIFEST_SHA256.json").read_text(encoding="utf-8"))
assert global_manifest["checkpoint"] == "V124"
assert global_manifest["exact_entities"] == 30 and global_manifest["strict_coverage_pct"] == STRICT
assert global_manifest["closed_network_gate"] == "NO"
assert "three new primary Caja/Merval system-history sources" in global_manifest["source_audit"]
assert "none submitted" in global_manifest["source_audit"]

backup = (REPO / "BACKUP_ACTUALIZACION_2026-08-29.md").read_text(encoding="utf-8-sig")
assert "## V124 · edición SLIQ fechada y cadena operativa preobjetivo" in backup
assert "Todos los pedidos permanecen DRAFT_NOT_SENT" in backup

print("V124 QA PASS")
