from __future__ import annotations

from pathlib import Path
import csv
import hashlib
import json
import re

from pypdf import PdfReader


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
V124 = HERE.parent / "V124"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pdf_text(reader: PdfReader) -> str:
    return re.sub(r"\s+", " ", " ".join(page.extract_text() or "" for page in reader.pages))


source_specs = {
    "e0_caja_comunicado_4857_recompra_2008_08_28": {
        "file": "caja_comunicado_4857_recompra_2008_08_28.pdf",
        "sha256": "6a79299e76486843a5289069ba3acb00c249cf0b8625f1bae7c342cdd60076ef",
        "created": "D:20080828120915",
        "number": "4857",
        "window": ("29/08/08", "01/09/08"),
        "report": "02/09/08",
    },
    "e0_caja_comunicado_4861_recompra_2008_09_04": {
        "file": "caja_comunicado_4861_recompra_2008_09_04.pdf",
        "sha256": "ae7a1fa7a3c21b29fe981576341ee3cb22b39ccc6192880425ad1ab324db661e",
        "created": "D:20080904115727",
        "number": "4861",
        "window": ("05/09/08", "08/09/08"),
        "report": "09/09/08",
    },
    "e0_caja_comunicado_4873_recompra_2008_09_11": {
        "file": "caja_comunicado_4873_recompra_2008_09_11.pdf",
        "sha256": "4d941daccbb32acc6a2b28ed9ba87ebfe4fa86c05852bce271fdff93f2e2ef90",
        "created": "D:20080911131049",
        "number": "4873",
        "window": ("12/09/08", "15/09/08"),
        "report": "16/09/08",
    },
    "e0_caja_comunicado_5152_recompra_strip_2009_06_12": {
        "file": "caja_comunicado_5152_recompra_strip_2009_06_12.pdf",
        "sha256": "a0a3bba2e68fee723873a14bfef631685b4407e21b15dcb1381d4249c28e57ab",
        "created": "D:20090611142358",
        "number": "5152",
        "window": ("12/06/09", "17/06/09"),
        "report": "18/06/09",
    },
}


catalog = read_csv(REPO / "data" / "fuentes" / "FUENTES.csv")
assert len(catalog) == 298 and len({row["id"] for row in catalog}) == 298
catalog_by_id = {row["id"]: row for row in catalog}
assert set(source_specs) <= catalog_by_id.keys()

census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V125.csv")
census_v124 = read_csv(V124 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V124.csv")
assert len(census) == 99 and len(census_v124) == 95
assert {row["source_id"] for row in census} - {row["source_id"] for row in census_v124} == set(source_specs)
assert all(row["primary_source"] == "YES" and row["preserved"] == "YES" for row in census)

binary_dir = CYCLE / "inputs" / "historical_retrieval" / "v125" / "binaries"
for source_id, expected in source_specs.items():
    source = catalog_by_id[source_id]
    path = REPO / source["archivo_local"].lstrip("/")
    assert path == binary_dir / expected["file"]
    assert path.is_file() and digest(path) == expected["sha256"] == source["sha256"]
    census_row = next(row for row in census if row["source_id"] == source_id)
    assert census_row["sha256"] == expected["sha256"]
    reader = PdfReader(path)
    assert len(reader.pages) == 2
    assert reader.metadata.get("/CreationDate") == expected["created"]
    text = pdf_text(reader)
    assert expected["number"] in text
    assert all(token in text for token in expected["window"])
    assert expected["report"] in text
    assert all(token in text for token in (
        "OYM F.89023.00", "Cuenta Depositante", "40.000", "Subcuenta Comitente",
        "matching", "diferidas", "cantidades parciales", "transferencias efectuadas",
    ))
    assert re.search(r"transferencias pendientes de ejecuci", text, re.I)
assert "5326" in pdf_text(PdfReader(binary_dir / source_specs["e0_caja_comunicado_5152_recompra_strip_2009_06_12"]["file"]))


ledger = read_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V125.csv")
breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V125.csv")
assert len(ledger) == 125 and len({row["ledger_id"] for row in ledger}) == 125
assert len(breaks) == 89 and len({row["break_id"] for row in breaks}) == 89
assert {
    "contemporaneous_caja_instruction_not_execution",
    "partial_round_communication_coverage_not_full_program",
    "t3_report_commitment_not_report_delivery",
    "document_footer_code_not_sliq_revision",
} <= {row["break_id"] for row in breaks}
assert not any(
    row["realization_status"] == "CASH_SETTLED"
    for row in ledger
    if row["ledger_id"] in {"F122", "F123", "F124", "F125"}
)

current = read_csv(HERE / "CURRENT_STATE_V125.csv")
coverage = read_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V125.csv")
assert len(current) == 39 and sum(row["strict_panel_status"] == "ELIGIBLE" for row in current) == 30
assert STRICT in " ".join(" ".join(row.values()) for row in coverage)

responses = read_csv(HERE / "E0_REQUEST_RESPONSE_REGISTER_V125.csv")
expected_counts = {
    "REQ125_ECON": 17,
    "REQ125_BCRA": 21,
    "REQ125_BNA": 9,
    "REQ125_AGN": 7,
    "REQ125_CNV": 8,
    "REQ125_CAJA": 15,
}
assert len(responses) == 6 and {row["request_id"] for row in responses} == set(expected_counts)
assert all(row["status"] == "DRAFT_NOT_SENT" for row in responses)
assert all(row["submitted_on"] == "N/A" and row["receipt_or_case_id"] == "N/A" for row in responses)
assert all(row["response_class"] == "NO_RESPONSE_EXPECTED_BEFORE_SUBMISSION" for row in responses)

trace = read_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V125.csv")
assert len(trace) == 77 and len({row["trace_id"] for row in trace}) == 77
for request_id, count in expected_counts.items():
    assert sum(row["request_id"] == request_id for row in trace) == count
assert all(row["status"] == "DRAFT_NOT_SENT" for row in trace)
assert all(not re.search(r"(?:TR|REQ|CL)124_", " ".join(row.values())) for row in trace)
assert any(row["trace_id"] == "TR125_075" and "transferencias efectuadas" in row["minimum_usable_fields"] for row in trace)
assert any(row["trace_id"] == "TR125_077" and "02/10/2008" in row["requested_record"] for row in trace)

search_keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V125.csv")
assert len(search_keys) == 57 and len({row["key_id"] for row in search_keys}) == 57
assert any("Comunicado 4857" in row["exact_key"] and "Comunicado 5152" in row["exact_key"] for row in search_keys)
assert any("transferencias pendientes de ejecución" in row["exact_key"] for row in search_keys)
assert any("Cuenta Depositante 306" in row["exact_key"] and "Subcuenta Comitente 3" in row["exact_key"] for row in search_keys)
assert any("licitación 02/10/2008" in row["exact_key"] for row in search_keys)

closures = read_csv(HERE / "E0_REQUEST_CLOSURE_CRITERIA_V125.csv")
assert len(closures) == 8 and len({row["gap_id"] for row in closures}) == 8
assert {row["gap_id"] for row in trace} <= {row["gap_id"] for row in closures}
caja_closure = next(row for row in closures if row["gap_id"] == "CL125_CAJA_ROUTE")
assert caja_closure["initial_status"] == "DIRECT_TARGET_ROUTE_INSTRUCTIONS_PRESERVED_EXECUTION_RECORDS_OPEN_NOT_SENT"
deferred_closure = next(row for row in closures if row["gap_id"] == "CL125_DEFERRED_MODALITY")
assert "THREE_2008_ROUNDS_AND_2009" in deferred_closure["initial_status"]

deferred = read_csv(HERE / "E0_DEFERRED_MODALITY_EQUIVALENCE_AUDIT_V125.csv")
crosswalk = read_csv(HERE / "E0_SECURITY_IDENTIFIER_CROSSWALK_V125.csv")
stages = read_csv(HERE / "E0_CAJA_CRYL_SETTLEMENT_STAGE_MATRIX_V125.csv")
target = read_csv(HERE / "E0_CAJA_TARGET_COMMUNICATION_MATRIX_V125.csv")
assert len(deferred) == 15 and len({row["audit_id"] for row in deferred}) == 15
assert {row["source_id"] for row in deferred[-4:]} == set(source_specs)
assert all("EXECUTION_OPEN" in row["evidence_status"] for row in deferred[-4:])
assert len(crosswalk) == 5 and {row["historical_code"] for row in crosswalk} == {"5426", "5427", "45698", "45701", "5326"}
assert len(stages) == 8 and len({row["stage_id"] for row in stages}) == 8
assert next(row for row in stages if row["stage_id"] == "ST125_05")["evidence_status"] == "DIRECT_CAJA_T3_REPORT_CONTENT_AND_DATES_PRESERVED_DELIVERY_OPEN"
assert len(target) == 4 and {row["communication_number"] for row in target} == {"4857", "4861", "4873", "5152"}
assert {row["receiver_depositant"] for row in target} == {"306"}
assert {row["receiver_subaccount"] for row in target} == {"40000"}
assert {row["sender_subaccount"] for row in target} == {"3"}
assert all(row["matching_required"] == "YES" and row["modality"] == "deferred" for row in target)
assert all(row["partial_transfers"] == "NOT_ACCEPTED" for row in target)
assert {row["t3_report_date"] for row in target} == {"2008-09-02", "2008-09-09", "2008-09-16", "2009-06-18"}
assert all("EXECUTION_OPEN" in row["evidence_status"] for row in target)

for name, count in {
    "CURRENT_OFFICIAL_SUBMISSION_CHANNELS_V125.csv": 7,
    "E0_DOCUMENT_SYSTEM_TEMPORAL_MAP_V125.csv": 6,
    "E0_ARCHIVAL_RETENTION_AUTHORITY_MATRIX_V125.csv": 10,
    "E0_NEGATIVE_RESPONSE_ADEQUACY_V125.csv": 14,
    "E0_RECORD_PRODUCER_SYSTEM_MAP_V125.csv": 22,
    "E0_REQUEST_ATTACHMENT_MINIMUM_V125.csv": 7,
    "E0_CRYL_EFFECTIVE_VERSION_CHAIN_V125.csv": 9,
    "E0_BUYBACK_MODALITY_TERM_AUDIT_V125.csv": 8,
    "E0_CRYL_CGA_RECORD_MAP_V125.csv": 8,
}.items():
    rows = read_csv(HERE / name)
    assert len(rows) == count, name
    assert all("REQ124_" not in " ".join(row.values()) for row in rows), name

drafts = [HERE / row["draft_file"] for row in responses]
assert all(path.is_file() for path in drafts)
for path in drafts:
    text = path.read_text(encoding="utf-8")
    assert "BORRADOR_NO_ENVIADO" in text
    assert "[NOMBRE Y APELLIDO / RAZÓN SOCIAL]" in text
    assert "Atentamente" in text
assert all("REQ124_" not in path.read_text(encoding="utf-8") for path in drafts)
caja_request = (HERE / "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V125.md").read_text(encoding="utf-8")
economia_request = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V125.md").read_text(encoding="utf-8")
for token in ("4857", "4861", "4873", "5152", "OYM F.89023.00", "306/40000"):
    assert token in caja_request
for token in ("02/09/2008", "09/09/2008", "16/09/2008", "18/06/2009", "transferencias pendientes"):
    assert token in economia_request

package = (HERE / "E0_INSTITUTIONAL_REQUEST_PACKAGE_V125.md").read_text(encoding="utf-8")
checklist = (HERE / "REQUEST_SUBMISSION_CHECKLIST_V125.md").read_text(encoding="utf-8")
assert "Estado general: **BORRADOR_NO_ENVIADO**" in package
assert "E0_CAJA_TARGET_COMMUNICATION_MATRIX_V125.csv" in package
assert "57 claves" in package and "77 objetos" in package
assert "NINGÚN_PEDIDO_ENVIADO" in checklist
assert all(token in checklist for token in ("4857", "4861", "4873", "5152"))

evidence = read_csv(HERE / "HISTORICAL_EVIDENCE_COVERAGE_V125.csv")
state = next(row for row in evidence if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra")
assert state["quality"] == "PRIMARY_BUYBACK_STRIP_EXACT_ACCOUNT_ROUTE_FIVE_CAJA_CODES_AND_DIRECT_TARGET_CAJA_INSTRUCTIONS_PRESERVED"
assert "tres de cuatro rondas" in state["gap"].lower()
queue = read_csv(HERE / "HISTORICAL_SOURCE_QUEUE_V125.csv")
state_queue = [row for row in queue if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra"]
assert len(state_queue) == 2
assert all(row["status"] == "INSTITUTIONAL_REQUEST_EXECUTION_PAYMENT_AND_FOURTH_ROUND_KEYS_READY_NOT_SENT" for row in state_queue)

hash_rows = read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V125.csv")
assert len(hash_rows) == 298
assert sum(row["exists"] == "True" for row in hash_rows) == 293
assert sum(row["hash_ok"] == "True" for row in hash_rows) == 293

completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V125.json").read_text(encoding="utf-8"))
assert completeness["checkpoint"] == "V125"
assert completeness["state"] == "E0_CAJA_DIRECT_TARGET_INSTRUCTIONS_2008_2009_THREE_OF_FOUR_ROUNDS_PRESERVED_EXECUTION_PAYMENT_OPEN_NOT_SENT"
assert completeness["master_catalog_entries"] == 298
assert completeness["physical_local_copies"] == 293 and completeness["physical_local_hash_ok"] == 293
assert completeness["e0_primary_sources_preserved"] == 99
assert completeness["sources_newly_preserved_v125"] == 4
assert completeness["e0_fiscal_ledger_rows"] == 125
assert completeness["e0_fiscal_method_breaks_frozen"] == 89
assert completeness["e0_request_drafts"] == 6
assert completeness["e0_request_traceability_rows"] == 77
assert completeness["e0_record_producer_system_rows"] == 22
assert completeness["e0_request_search_keys"] == 57
assert completeness["e0_deferred_modality_equivalence_audit_rows"] == 15
assert completeness["e0_caja_target_communication_rows"] == 4
assert completeness["e0_requests_submitted"] == 0 and completeness["e0_request_responses_received"] == 0
assert completeness["closed_network_gate"] == "NO" and completeness["strict_coverage_pct"] == STRICT

inherited = read_csv(HERE / "INHERITED_QA_STATUS_V125.csv")
assert next(row for row in inherited if row["script"] == "qa_v124.py")["post_v125_result"] == "EXPECTED_SUPERSEDED_ASSERTION"
assert next(row for row in inherited if row["script"] == "qa_v125.py")["post_v125_result"] == "PASS"
assert all(
    next(row for row in inherited if row["script"] == f"qa_v{i}.py")["post_v125_result"] == "PASS"
    for i in (98, 100, 101, 102, 103, 104, 105, 106)
)

manifest = json.loads((HERE / "MANIFEST_V125.json").read_text(encoding="utf-8"))
assert manifest["checkpoint"] == "V125" and manifest["parent_checkpoint"] == "V124"
assert manifest["e0_primary_sources"] == 99 and manifest["new_primary_sources"] == 4
assert manifest["fiscal_ledger_rows"] == 125 and manifest["fiscal_method_breaks"] == 89
assert manifest["request_traceability_rows"] == 77 and manifest["request_search_keys"] == 57
assert manifest["deferred_modality_equivalence_audit_rows"] == 15
assert manifest["caja_target_communication_rows"] == 4
assert manifest["requests_submitted"] == 0 and manifest["responses_received"] == 0
for item in manifest["files"]:
    path = HERE / item["path"]
    assert path.stat().st_size == item["bytes"], path
    assert digest(path) == item["sha256"], path

global_manifest = json.loads((CYCLE / "MANIFEST_SHA256.json").read_text(encoding="utf-8"))
assert global_manifest["checkpoint"] == "V125"
assert global_manifest["exact_entities"] == 30 and global_manifest["strict_coverage_pct"] == STRICT
assert "four direct contemporary Caja target-communication sources" in global_manifest["source_audit"]
assert "none submitted" in global_manifest["source_audit"]

backup = (REPO / "BACKUP_ACTUALIZACION_2026-08-29.md").read_text(encoding="utf-8-sig")
assert "## V125 · comunicaciones directas de Caja para recompras objetivo" in backup
assert "Todos los pedidos permanecen DRAFT_NOT_SENT" in backup

print("V125 QA PASS")
