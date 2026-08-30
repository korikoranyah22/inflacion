from __future__ import annotations

from pathlib import Path
import csv
import hashlib
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
V118 = HERE.parent / "V118"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


catalog = read_csv(REPO / "data" / "fuentes" / "FUENTES.csv")
assert len(catalog) == 274
assert len({row["id"] for row in catalog}) == 274


census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V119.csv")
census_v118 = read_csv(V118 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V118.csv")
assert len(census) == len(census_v118) == 75
assert {row["source_id"] for row in census} == {row["source_id"] for row in census_v118}
assert all(row["primary_source"] == "YES" and row["preserved"] == "YES" for row in census)


ledger = read_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V119.csv")
breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V119.csv")
assert len(ledger) == 125 and len({row["ledger_id"] for row in ledger}) == 125
assert len(breaks) == 67 and len({row["break_id"] for row in breaks}) == 67
assert {
    "pre_gde_record_not_gde_identifier",
    "reproduction_eligibility_not_destruction",
    "retention_minimum_elapsed_not_proof_of_destruction",
    "current_retention_rule_not_retroactive_2008",
    "public_archive_date_scope_not_operational_search",
    "repealed_archival_rule_not_current_duty",
} <= {row["break_id"] for row in breaks}
assert not any(
    row["realization_status"] == "CASH_SETTLED" for row in ledger if row["ledger_id"] in {"F122", "F123", "F124", "F125"}
)


current = read_csv(HERE / "CURRENT_STATE_V119.csv")
coverage = read_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V119.csv")
assert len(current) == 39
assert sum(row["strict_panel_status"] == "ELIGIBLE" for row in current) == 30
assert STRICT in " ".join(" ".join(row.values()) for row in coverage)


channels = read_csv(HERE / "CURRENT_OFFICIAL_SUBMISSION_CHANNELS_V119.csv")
assert len(channels) == 7
assert len({row["channel_id"] for row in channels}) == 7
assert all(row["verified_on"] == "2026-08-29" for row in channels)
assert all("VERIFIED" in row["status"] for row in channels)
channels_by_institution = {row["institution"]: row for row in channels}
assert channels_by_institution["Banco Central de la República Argentina / CRyL"]["email_or_contact"] == "aip@bcra.gob.ar"
assert channels_by_institution["Banco de la Nación Argentina"]["email_or_contact"] == "accesoalainformacionpublica@bna.com.ar"
assert channels_by_institution["Caja de Valores S.A."]["status"] == "OFFICIAL_INSTITUTIONAL_CONTACT_VERIFIED"
assert "no se presume" in channels_by_institution["Caja de Valores S.A."]["caveat"].lower()


responses = read_csv(HERE / "E0_REQUEST_RESPONSE_REGISTER_V119.csv")
assert len(responses) == 6
assert len({row["request_id"] for row in responses}) == 6
assert all(row["status"] == "DRAFT_NOT_SENT" for row in responses)
assert all(row["submitted_on"] == "N/A" and row["receipt_or_case_id"] == "N/A" for row in responses)
assert all(row["response_class"] == "NO_RESPONSE_EXPECTED_BEFORE_SUBMISSION" for row in responses)


expected_counts = {
    "REQ119_ECON": 10,
    "REQ119_BCRA": 9,
    "REQ119_BNA": 8,
    "REQ119_AGN": 6,
    "REQ119_CNV": 7,
    "REQ119_CAJA": 6,
}
trace = read_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V119.csv")
assert len(trace) == 46
assert len({row["trace_id"] for row in trace}) == 46
assert {row["request_id"] for row in trace} == set(expected_counts)
for request_id, count in expected_counts.items():
    assert sum(row["request_id"] == request_id for row in trace) == count
assert all(row["status"] == "DRAFT_NOT_SENT" for row in trace)
assert any("ARARGE03G415" in row["identifiers"] for row in trace)
assert any("0306/40000" in row["identifiers"] for row in trace)
assert any("2074c3d9-a535-497e-a97d-d74340ff49fb" in row["identifiers"] for row in trace)


system_map = read_csv(HERE / "E0_DOCUMENT_SYSTEM_TEMPORAL_MAP_V119.csv")
authorities = read_csv(HERE / "E0_ARCHIVAL_RETENTION_AUTHORITY_MATRIX_V119.csv")
negative_adequacy = read_csv(HERE / "E0_NEGATIVE_RESPONSE_ADEQUACY_V119.csv")
assert len(system_map) == 6 and len({row["institution"] for row in system_map}) == 6
assert "COMDOC" in next(row for row in system_map if row["institution"] == "Ministerio de Economía / Tesoro")["contemporaneous_route"]
assert "1991" in next(row for row in system_map if row["institution"] == "BCRA / CRyL")["temporal_caveat"]
assert len(authorities) == 10
assert any("deroga" in row["operative_point"] for row in authorities)
assert any("retroactiva" in row["prohibited_inference"] for row in authorities)
assert len(negative_adequacy) == 14
assert {row["adequacy_id"] for row in negative_adequacy} == {f"NR119_{i:02d}" for i in range(1, 15)}
assert sum(row["effect_on_gap"] == "NO_CIERRA" for row in negative_adequacy) == 13


closures = read_csv(HERE / "E0_REQUEST_CLOSURE_CRITERIA_V119.csv")
assert len(closures) == 6
assert len({row["gap_id"] for row in closures}) == 6
assert {row["gap_id"] for row in trace} <= {row["gap_id"] for row in closures}
assert all(row["initial_status"].startswith("OPEN_") for row in closures)
assert all(row["minimum_positive_evidence"] and row["does_not_close"] for row in closures)
assert "Fecha T+3" in next(row for row in closures if row["gap_id"] == "CL119_SETTLEMENT_2008")["does_not_close"]
assert "no producción no equivale a tenencias cero" in next(
    row for row in closures if row["gap_id"] == "CL119_CUSTODY_HOLDINGS"
)["minimum_negative_route_evidence"]


drafts = [HERE / row["draft_file"] for row in responses]
assert all(path.is_file() for path in drafts)
for path in drafts:
    text = path.read_text(encoding="utf-8")
    assert "BORRADOR_NO_ENVIADO" in text
    assert "[NOMBRE Y APELLIDO / RAZÓN SOCIAL]" in text
    assert any(token in text.lower() for token in ("tacha", "testad", "disoci", "agregad"))
    assert any(token in text.lower() for token in ("expurgo", "conservación", "retención"))
    assert "Atentamente" in text

economia = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V119.md").read_text(encoding="utf-8")
bcra = (HERE / "REQUEST_BCRA_CRYL_SETTLEMENT_V119.md").read_text(encoding="utf-8")
bna = (HERE / "REQUEST_BNA_FIRST_STAGE_BLOTTER_V119.md").read_text(encoding="utf-8")
agn = (HERE / "REQUEST_AGN_2018_REPLY_V119.md").read_text(encoding="utf-8")
cnv = (HERE / "REQUEST_CNV_CUSTODY_RECORDS_V119.md").read_text(encoding="utf-8")
caja = (HERE / "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V119.md").read_text(encoding="utf-8")
assert "2, 9 y 16 de septiembre y 7 de octubre" in economia
assert "CRyL" in bcra and "ARARGE03G415" in bcra
assert "11–22/08/2008" in bna and "USD 380 millones" in bna
assert "18814" in agn and "18821" in agn and "11/09/2018" in agn
assert "19/11/2014" in cnv and "Resolución AGN 41/2016" in cnv
assert "consulta voluntaria" in caja.lower() and "no se solicitan datos personales" in caja.lower()
assert "COMDOC" in economia and "mero transcurso" in economia
assert "hasta 1991" in bcra and "sistemas operativos históricos" in bcra
assert "actas de apertura y cierre" in bna and "no equivale a prueba de destrucción" in bna
assert "almacenamiento de archivos adjuntos" in agn and "copias de seguridad" in agn
assert "no prueba destrucción" in cnv and "regla históricamente aplicable" in cnv
assert "plazo mínimo de conservación" in caja and "acceso irrestricto" in caja


package = (HERE / "E0_INSTITUTIONAL_REQUEST_PACKAGE_V119.md").read_text(encoding="utf-8")
checklist = (HERE / "REQUEST_SUBMISSION_CHECKLIST_V119.md").read_text(encoding="utf-8")
assert "Estado general: **BORRADOR_NO_ENVIADO**" in package
assert "NINGÚN_PEDIDO_ENVIADO" in checklist
assert "No marcar ninguna brecha como cerrada por el solo envío" in package
assert "no anotar `ENVIADO` hasta contar con constancia" in checklist
assert "E0_NEGATIVE_RESPONSE_ADEQUACY_V119.csv" in package
assert "no haya sido limitada a GDE" in checklist


evidence = read_csv(HERE / "HISTORICAL_EVIDENCE_COVERAGE_V119.csv")
state = next(row for row in evidence if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra")
assert state["quality"].endswith("REQUEST_ARCHIVAL_SCOPE_HARDENED")
assert "no fueron enviados" in state["gap"]

queue = read_csv(HERE / "HISTORICAL_SOURCE_QUEUE_V119.csv")
state_queue = [row for row in queue if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra"]
assert len(state_queue) == 2
assert all(row["status"] == "INSTITUTIONAL_REQUEST_ARCHIVAL_SCOPE_HARDENED_NOT_SENT" for row in state_queue)
assert all("autorización expresa" in row["next_action"] for row in state_queue)


hash_rows = read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V119.csv")
assert len(hash_rows) == 274
assert sum(row["exists"] == "True" for row in hash_rows) == 269
assert sum(row["hash_ok"] == "True" for row in hash_rows) == 269


completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V119.json").read_text(encoding="utf-8"))
assert completeness["checkpoint"] == "V119"
assert completeness["master_catalog_entries"] == 274
assert completeness["physical_local_copies"] == 269
assert completeness["e0_primary_sources_preserved"] == 75
assert completeness["sources_newly_preserved_v119"] == 0
assert completeness["e0_fiscal_ledger_rows"] == 125
assert completeness["e0_fiscal_method_breaks_frozen"] == 67
assert completeness["e0_request_drafts"] == 6
assert completeness["e0_request_traceability_rows"] == 46
assert completeness["e0_request_closure_rules"] == 6
assert completeness["e0_document_system_temporal_routes"] == 6
assert completeness["e0_archival_retention_authorities"] == 10
assert completeness["e0_negative_response_adequacy_controls"] == 14
assert completeness["e0_official_submission_channels_verified"] == 7
assert completeness["e0_requests_submitted"] == 0
assert completeness["e0_request_responses_received"] == 0
assert completeness["e0_request_package_status"] == "DRAFT_NOT_SENT"
assert completeness["closed_network_gate"] == "NO"
assert completeness["strict_coverage_pct"] == STRICT


inherited = read_csv(HERE / "INHERITED_QA_STATUS_V119.csv")
assert next(row for row in inherited if row["script"] == "qa_v118.py")["post_v119_result"] == "EXPECTED_SUPERSEDED_ASSERTION"
assert next(row for row in inherited if row["script"] == "qa_v119.py")["post_v119_result"] == "PASS"
assert all(
    next(row for row in inherited if row["script"] == f"qa_v{i}.py")["post_v119_result"] == "PASS"
    for i in (98, 100, 101, 102, 103, 104, 105, 106)
)


manifest = json.loads((HERE / "MANIFEST_V119.json").read_text(encoding="utf-8"))
assert manifest["checkpoint"] == "V119" and manifest["parent_checkpoint"] == "V118"
assert manifest["e0_primary_sources"] == 75 and manifest["new_primary_sources"] == 0
assert manifest["fiscal_ledger_rows"] == 125 and manifest["fiscal_method_breaks"] == 67
assert manifest["request_drafts"] == 6 and manifest["official_submission_channels"] == 7
assert manifest["request_traceability_rows"] == 46 and manifest["request_closure_rules"] == 6
assert manifest["document_system_temporal_routes"] == 6
assert manifest["archival_retention_authorities"] == 10
assert manifest["negative_response_adequacy_controls"] == 14
assert manifest["requests_submitted"] == 0 and manifest["responses_received"] == 0
for item in manifest["files"]:
    path = HERE / item["path"]
    assert path.stat().st_size == item["bytes"], path
    assert digest(path) == item["sha256"], path


global_manifest = json.loads((CYCLE / "MANIFEST_SHA256.json").read_text(encoding="utf-8"))
assert global_manifest["checkpoint"] == "V119"
assert global_manifest["exact_entities"] == 30
assert global_manifest["strict_coverage_pct"] == STRICT
assert global_manifest["closed_network_gate"] == "NO"
assert "none submitted" in global_manifest["source_audit"]


backup = (REPO / "BACKUP_ACTUALIZACION_2026-08-29.md").read_text(encoding="utf-8-sig")
assert "## V119 · alcance archivístico endurecido" in backup
assert "Todos los pedidos permanecen DRAFT_NOT_SENT" in backup

print("V119 QA PASS")
