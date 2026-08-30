from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import csv
import hashlib
import json

from pypdf import PdfReader


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v117" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


source_ids = {
    "e0_agn_res_041_2016_deuda_custodian_gap",
    "e0_agn_api_boden_request_2018_record",
}


catalog = read_csv(REPO / "data" / "fuentes" / "FUENTES.csv")
assert len(catalog) == 274, len(catalog)
assert len({row["id"] for row in catalog}) == len(catalog)
catalog_by_id = {row["id"]: row for row in catalog}
assert source_ids <= catalog_by_id.keys()


census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V117.csv")
assert len(census) == 75, len(census)
assert len({row["source_id"] for row in census}) == len(census)
assert source_ids <= {row["source_id"] for row in census}
for source_id in source_ids:
    source = catalog_by_id[source_id]
    local = REPO / source["archivo_local"].lstrip("/")
    assert local.is_file(), local
    assert digest(local) == source["sha256"]
    census_row = next(row for row in census if row["source_id"] == source_id)
    assert census_row["primary_source"] == "YES" and census_row["preserved"] == "YES"
    assert census_row["sha256"] == source["sha256"]


pdf = BIN / "agn_informe_041_2016_deuda_tenencias_custodios.pdf"
assert pdf.read_bytes().startswith(b"%PDF")
reader = PdfReader(str(pdf))
assert len(reader.pages) == 138
page20 = reader.pages[19].extract_text() or ""
page21 = reader.pages[20].extract_text() or ""
page101 = reader.pages[100].extract_text() or ""
assert "19/11/2014" in page20
assert "Caja de Valores" in page20 and "Comisi" in page20
assert "Ley 24.156" in page21 and "Principio 11" in page21
assert "CRyL" in page101 and "Caja de Valores" in page101
assert not (REPO / "tmp" / "pdfs" / "v117_agn").exists()


api_path = BIN / "agn_api_webform_boden_request_2018.json"
api = json.loads(api_path.read_text(encoding="utf-8"))
data = api["data"]
attributes = data["attributes"]
assert data["id"] == "2074c3d9-a535-497e-a97d-d74340ff49fb"
assert attributes["drupal_internal__nid"] == 18814 and attributes["drupal_internal__vid"] == 18821
assert attributes["ingreso"] == "2018-08-14" and attributes["respuesta"] == "2018-09-11"
assert "Boden 2006, 2012 y 2013" in attributes["tema"]
assert sorted(data["relationships"]) == ["node_type", "revision_uid", "uid"]
assert not api.get("included")


schema = read_csv(HERE / "E0_AGN_BODEN_REQUEST_PUBLIC_SCHEMA_V117.csv")
assert len(schema) == 1
assert schema[0]["node_uuid"] == data["id"]
assert schema[0]["file_relationship_present"] == "NO"
assert schema[0]["included_resource_count"] == "0"
assert schema[0]["individual_response_file_published"] == "NO"
assert schema[0]["match_status"] == "EXACT_PUBLIC_API_RECORD_NO_FILE_RELATIONSHIP"


gaps = read_csv(HERE / "E0_FISCAL_CUSTODIAN_INFORMATION_GAPS_V117.csv")
assert len(gaps) == 6
gaps_by_id = {row["gap_id"]: row for row in gaps}
assert gaps_by_id["CG02"]["status"] == "PRIMARY_AUDIT_REQUEST_NONPRODUCTION"
assert gaps_by_id["CG03"]["period"] == "2014-11-19"
assert "CRyL" in gaps_by_id["CG04"]["evidence"]
assert "USD 3.937bn" in gaps_by_id["CG05"]["evidence"]
assert gaps_by_id["CG06"]["status"] == "PRIMARY_PUBLIC_SCHEMA_NO_ATTACHMENT"
assert "zero" in gaps_by_id["CG02"]["prohibited_inference"].lower()
assert "not proof" in gaps_by_id["CG04"]["prohibited_inference"].lower()


cdx_input = json.loads((BIN / "wayback_cdx_mecon_finance_pdfs_2008_2009.json").read_text(encoding="utf-8"))
assert len(cdx_input) == 49
archive = read_csv(HERE / "E0_FINANCE_ARCHIVE_PDF_CENSUS_2008_2009_V117.csv")
assert len(archive) == 48
assert len({(row["timestamp"], row["original_url"], row["cdx_digest"]) for row in archive}) == 48
assert all(row["mimetype"] == "application/pdf" and row["statuscode"] == "200" for row in archive)
assert not any(row["post_settlement_confirmation_filename_candidate"] == "YES" for row in archive)
assert any("comunicado_llamado_licitacion_27-08-08.pdf" in row["original_url"] for row in archive)
assert any("comunicado_de_prensa_resultado_con%20anexo.pdf" in row["original_url"] for row in archive)


routes = read_csv(HERE / "E0_PUBLIC_ROUTE_EXHAUSTION_V117.csv")
assert len(routes) == 4
routes_by_id = {row["route_id"]: row for row in routes}
assert routes_by_id["R117_01"]["records_examined"] == "48"
assert routes_by_id["R117_02"]["positive_operational_confirmation_hits"] == "0"
assert routes_by_id["R117_03"]["positive_operational_confirmation_hits"] == "0 file relationships"
assert routes_by_id["R117_04"]["status"] == "NO_POST_SETTLEMENT_CONFIRMATION_IDENTIFIED"


agn_index = read_csv(HERE / "E0_FISCAL_AGN_REPORT_INDEX_V117.csv")
request = next(row for row in agn_index if row["record_id"] == "AGN_REQUEST_2018_08_14")
assert request["match_status"] == "EXACT_PUBLIC_API_RECORD_NO_FILE_RELATIONSHIP"
assert "e0_agn_api_boden_request_2018_record" in request["source_id"]
res41 = next(row for row in agn_index if row["record_id"] == "AGN_RES041_2016")
assert res41["resolution"] == "41/2016"
assert res41["match_status"] == "PRIMARY_CUSTODIAN_DISCLOSURE_GAP_CONTROL"


ledger = read_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V117.csv")
assert len(ledger) == 125, len(ledger)
assert len({row["ledger_id"] for row in ledger}) == len(ledger)
assert {f"F{i}" for i in range(122, 126)} <= {row["ledger_id"] for row in ledger}
assert all(row["realization_status"] != "CASH_SETTLED" for row in ledger if row["ledger_id"] in {f"F{i}" for i in range(122, 126)})
assert next(row for row in ledger if row["ledger_id"] == "F123")["realization_status"] == "CUSTODIAN_DATA_NOT_OBTAINED"
assert next(row for row in ledger if row["ledger_id"] == "F125")["amount_original"] == "3937"
assert next(row for row in ledger if row["ledger_id"] == "F125")["additivity"] == "CONTROL_NOT_ADDITIVE"


breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V117.csv")
assert len(breaks) == 61, len(breaks)
assert len({row["break_id"] for row in breaks}) == len(breaks)
assert {
    "public_api_record_not_individual_response",
    "custodian_nonproduction_not_zero_holdings",
    "custodian_audit_period_not_2008_transaction",
    "intrasector_discrepancy_not_buyback_allocation",
} <= {row["break_id"] for row in breaks}


events = read_csv(HERE / "E0_FISCAL_BUYBACK_PROGRAM_EVENTS_2005_2009_V117.csv")
assert len(events) == 10
assert next(row for row in events if row["event_id"] == "E2009_STRIP_OFFICIAL")["status"] == "PRIMARY_RESULT_EXACT_SETTLEMENT_OPEN"


matrix = read_csv(HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V117.csv")
holder_gap = next(row for row in matrix if row["variable"] == "custodian_holder_information_gap")
assert holder_gap["status"] == "STRUCTURAL_CUSTODY_DISCLOSURE_GAP_DOCUMENTED"
assert holder_gap["source_quality"] == "PRIMARY_AUDIT_AND_PRIMARY_API_SCHEMA"


evidence = read_csv(HERE / "HISTORICAL_EVIDENCE_COVERAGE_V117.csv")
state = next(row for row in evidence if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra")
assert state["quality"] == "PRIMARY_BUYBACK_STRIP_EXACT_ACCOUNT_ROUTE_CUSTODIAN_GAP_DOCUMENTED_2001_2013"
assert "Caja/CNV" in state["gap"] and "BNA" in state["gap"]


queue = read_csv(HERE / "HISTORICAL_SOURCE_QUEUE_V117.csv")
state_queue = [row for row in queue if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra"]
assert len(state_queue) == 2
assert all(row["status"] == "TRANSACTIONS_PRIMARY_EXACT_CUSTODIAN_GAP_PRIMARY_DOCUMENTED" for row in state_queue)
assert all("evitar repetir rutas web" in row["next_action"] for row in state_queue)


current = read_csv(HERE / "CURRENT_STATE_V117.csv")
assert len(current) == 39
assert sum(row["strict_panel_status"] == "ELIGIBLE" for row in current) == 30
coverage = read_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V117.csv")
assert STRICT in " ".join(" ".join(row.values()) for row in coverage)


hash_rows = read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V117.csv")
assert len(hash_rows) == 274
assert sum(row["exists"] == "True" for row in hash_rows) == 269
assert sum(row["hash_ok"] == "True" for row in hash_rows) == 269


completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V117.json").read_text(encoding="utf-8"))
assert completeness["checkpoint"] == "V117"
assert completeness["master_catalog_entries"] == 274
assert completeness["physical_local_copies"] == completeness["physical_local_hash_ok"] == 269
assert completeness["e0_primary_sources_preserved"] == 75
assert completeness["sources_newly_preserved_v117"] == 2
assert completeness["pending_binary_discovery_actions"] == 3
assert completeness["pending_external_request_actions"] == 1
assert completeness["e0_agn_public_boden_record_exact"] is True
assert completeness["e0_agn_public_record_file_relationship_present"] is False
assert completeness["e0_agn_individual_offline_response_excluded"] is False
assert completeness["e0_custodian_information_gap_primary_documented"] is True
assert completeness["e0_custodian_nonproduction_interpreted_as_zero"] is False
assert completeness["e0_mecon_wayback_pdf_unique_2008_2009"] == 48
assert completeness["closed_network_gate"] == "NO"
assert completeness["strict_coverage_pct"] == STRICT


inherited = read_csv(HERE / "INHERITED_QA_STATUS_V117.csv")
assert next(row for row in inherited if row["script"] == "qa_v116.py")["post_v117_result"] == "EXPECTED_SUPERSEDED_ASSERTION"
assert next(row for row in inherited if row["script"] == "qa_v117.py")["post_v117_result"] == "PASS"


manifest = json.loads((HERE / "MANIFEST_V117.json").read_text(encoding="utf-8"))
assert manifest["checkpoint"] == "V117" and manifest["parent_checkpoint"] == "V116"
assert manifest["e0_primary_sources"] == 75 and manifest["new_preserved_sources"] == 2
assert manifest["fiscal_ledger_rows"] == 125 and manifest["fiscal_method_breaks"] == 61
assert manifest["custodian_gap_rows"] == 6 and manifest["agn_public_schema_rows"] == 1
assert manifest["mecon_archive_pdf_census_rows"] == 48
for item in manifest["files"]:
    path = HERE / item["path"]
    assert path.stat().st_size == item["bytes"], path
    assert digest(path) == item["sha256"], path


global_manifest = json.loads((CYCLE / "MANIFEST_SHA256.json").read_text(encoding="utf-8"))
assert global_manifest["checkpoint"] == "V117"
assert global_manifest["exact_entities"] == 30
assert global_manifest["strict_coverage_pct"] == STRICT
assert global_manifest["closed_network_gate"] == "NO"

print("V117 QA PASS")
