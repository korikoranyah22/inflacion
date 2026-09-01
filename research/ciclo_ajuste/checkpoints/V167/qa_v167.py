from pathlib import Path
import csv
import gzip
import hashlib
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
GENERIC = CYCLE / "inputs/historical_retrieval/v167/binaries/sigen_planannual_generic_20081006.arc.gz"
PLAN2008 = CYCLE / "inputs/historical_retrieval/v167/binaries/sigen_planannual_2008_20080705.arc.gz"
GENERIC_SHA = "aa4b44de448d93e9fb0e79533439c2ed1df7b6a11896fa20fef6483672219a21"
PLAN2008_SHA = "6506ba4ecb9b28d463d45bc62108ba06225704234c2f27da43eba3cbbe6fe444"
COVERAGE = "63.4406041403540997520463142785031521252747951992299547614348265414453439585848248058817492708499966268585997481191265825"


def rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def arc_text(path):
    with gzip.open(path, "rb") as handle:
        return handle.read().decode("cp1252", errors="replace")


assert GENERIC.is_file() and GENERIC.stat().st_size == 4619 and digest(GENERIC) == GENERIC_SHA
assert PLAN2008.is_file() and PLAN2008.stat().st_size == 4978 and digest(PLAN2008) == PLAN2008_SHA
generic = arc_text(GENERIC)
specific = arc_text(PLAN2008)
assert generic.startswith("http://www.sigen.gov.ar/plananual.asp 190.139.97.169 20081006152047")
assert "Plan Sigen 2007" in generic and "documentos_pdf/Plan_SIGEN_2007.pdf" in generic
assert specific.startswith("http://www.sigen.gov.ar/plananual2008.asp")
assert "Plan Sigen 2008" in specific and "documentacion/plananualpdfs/Plan SIGEN 2008.pdf" in specific
assert all(f"documentacion/plananualpdfs/Anexo D - Cuadro {number}.pdf" in specific for number in range(5, 16))

grammar = rows(HERE / "E0_SIGEN_HISTORICAL_ROUTE_GRAMMAR_V167.csv")
assert len(grammar) == 4
by_id = {row["control_id"]: row for row in grammar}
assert by_id["RG167_01"]["result"] == "GENERIC_PAGE_STALE_STILL_PLAN_2007"
assert by_id["RG167_02"]["result"] == "SPECIFIC_PAGE_AND_NEW_NAMING_GRAMMAR_CONFIRMED"
assert by_id["RG167_03"]["result"] == "COMMON_CRAWL_2010_CONTROL_CAPTURED"
assert by_id["RG167_04"]["result"] == "HIGH_PRECISION_CANDIDATE_NOT_CAPTURED"

links = rows(HERE / "E0_SIGEN_ARCHIVED_PAGE_LINKS_V167.csv")
assert any(row["href"] == "documentos_pdf/Plan_SIGEN_2007.pdf" for row in links)
assert any(row["href"] == "documentacion/plananualpdfs/Plan SIGEN 2008.pdf" for row in links)
assert sum(row["href"].startswith("documentacion/plananualpdfs/Anexo D - Cuadro") for row in links) == 11

search = rows(HERE / "V167_PUBLIC_SEARCH_LOG.csv")
assert len(search) == 9
classes = {row["search_id"]: row["classification"] for row in search}
assert classes["PS167_02"] == "CAPTURE_RECOVERED_STALE_GENERIC"
assert classes["PS167_03"] == "CAPTURE_RECOVERED_ROUTE_GRAMMAR"
assert classes["PS167_04"] == classes["PS167_05"] == "INDEX_NEGATIVE_SCOPED"
assert classes["PS167_08"] == "LIVE_ROUTE_NEGATIVE"
assert classes["PS167_09"] == "SERVICE_UNAVAILABLE_NOT_NEGATIVE"

gate = rows(HERE / "E0_PLAN_2009_ANNEX_G_PUBLIC_NEGATIVE_AND_EXACT_DATE_GATE_V167.csv")
assert len(gate) == 13
gate_by_id = {row["row_id"]: row for row in gate}
assert gate_by_id["DG167_11"]["status"] == "ARCHIVAL_LOCATOR_CLOSED"
assert gate_by_id["DG167_12"]["status"] == "SCOPED_INDEX_NEGATIVE"
assert gate_by_id["DG167_13"]["status"] == "METHOD_GUARDRAIL"

bridge = rows(HERE / "E0_UAI_ENTITY_PROJECT_PRODUCT_REPORT_CROSSWALK_V167.csv")
assert len(bridge) == 9
bridge_by_layer = {row["layer"]: row for row in bridge}
assert bridge_by_layer["nota_3672"]["status"] == "NOTE_BODY_OPEN"
assert bridge_by_layer["observacion_SISIO"]["status"] == "SYSTEM_ENTRY_OPEN"
assert bridge_by_layer["ejecucion_bancaria"]["status"] == "BANK_GATE_0_OF_10"
assert all(row["missing_identifier"] for row in bridge)

method_breaks = rows(HERE / "E0_FISCAL_METHOD_BREAKS_V167.csv")
breaks = {row["break_id"]: row for row in method_breaks}
for identifier in ("archived_route_grammar_not_target_document", "stale_generic_page_not_target_year", "common_crawl_no_capture_not_nonexistence"):
    assert breaks[identifier]["status"] == "FROZEN_V167"
    assert breaks[identifier]["dimension"] and breaks[identifier]["problem"] and breaks[identifier]["rule"] and breaks[identifier]["evidence"]

state = rows(HERE / "CURRENT_STATE_V167.csv")
assert sum(row["q4_four_leg_status"] == "EXACT" for row in state) == 34
assert sum(row["strict_panel_status"] == "ELIGIBLE" for row in state) == 34
panel = rows(HERE / "FOUR_LEG_PASS_PANEL_V167.csv")
assert sum(row["system_panel_eligible_v72"] == "YES_EXACT_Q4_TARGET_BASIS" for row in panel) == 34
coverage = rows(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V167.csv")
assert len(coverage) == 1 and coverage[0]["asset_coverage_pct"] == COVERAGE
assert coverage[0]["asset_numerator_million_ars"] == "61345602.215"

catalog = rows(CATALOG)
assert len(catalog) == 587 and len({row["id"] for row in catalog}) == 587
catalog_by_id = {row["id"]: row for row in catalog}
assert catalog_by_id["sigen_planannual_generic_cc_20081006_v167"]["sha256"] == GENERIC_SHA
assert catalog_by_id["sigen_planannual_2008_cc_20080705_v167"]["sha256"] == PLAN2008_SHA
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    assert path.is_file() and digest(path) == row["sha256"].lower()

master = rows(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V167.csv")
assert len(master) == 587 and all(row["exists"] == "True" and row["hash_ok"] == "True" for row in master)
assert not rows(AUDIT / "SOURCE_PRESERVATION_MISSING_V167.csv")
complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V167.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V167" and complete["exact_entities"] == 34
assert complete["master_catalog_entries"] == complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 587
assert complete["new_archival_captures"] == 2
assert complete["plan_sigen_2009_body_located"] is False and complete["note_3672_09_body_located"] is False

bundle = rows(HERE / "V167_SOURCE_BUNDLE.csv")
assert len(bundle) == 9
for row in bundle:
    path = REPO / row["path"].lstrip("/")
    assert path.is_file() and path.stat().st_size == int(row["bytes"]) and digest(path) == row["sha256"]

sync = rows(CYCLE / "inputs/source_sync/v167/SOURCE_SYNC_FILE_MANIFEST_V167.csv")
assert len(sync) == 2 and {row["sha256"] for row in sync} == {GENERIC_SHA, PLAN2008_SHA}
assert all(row["format_verification"] == "GZIP_MAGIC_ARC_RECORD_DECOMPRESSED_AND_CONTENT_ASSERTED" for row in sync)

archival = rows(HERE / "ARCHIVAL_PROVENANCE_V167.csv")
archival_by_id = {row["source_id"]: row for row in archival}
assert archival_by_id["sigen_planannual_generic_cc_20081006_v167"]["capture_timestamp"] == "20081006152047"
assert archival_by_id["sigen_planannual_2008_cc_20080705_v167"]["capture_timestamp"] == "20080705175930"
assert archival_by_id["sigen_planannual_generic_cc_20081006_v167"]["cdx_digest"] == "DVGOTYMYBIVN73RE2KQYMH3L6TXGOK33"
assert archival_by_id["sigen_planannual_2008_cc_20080705_v167"]["cdx_digest"] == "MNSAM5KY7KSS3FFR2KU5WOV6SPBPJDMZ"

register = rows(HERE / "E0_REQUEST_RESPONSE_REGISTER_V167.csv")
assert len(register) == 6 and all(row["status"] == "DRAFT_NOT_SENT" and row["submitted_on"] == "N/A" for row in register)
combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined

manifest = json.loads((HERE / "MANIFEST_V167.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V167" and manifest["parent_checkpoint"] == "V166"
assert manifest["exact_entities"] == 34 and manifest["new_promotions"] == []
assert manifest["plan_sigen_2009_body"] == "NOT_LOCATED" and manifest["note_3672_09_body"] == "NOT_LOCATED"
for item in manifest["files"]:
    path = HERE / item["path"]
    assert path.is_file() and path.stat().st_size == item["bytes"] and digest(path) == item["sha256"]

global_manifest = json.loads((CYCLE / "MANIFEST_SHA256.json").read_text(encoding="utf-8-sig"))
assert global_manifest["checkpoint"] == "V167" and global_manifest["exact_entities"] == 34
assert global_manifest["strict_coverage_pct"] == COVERAGE
assert global_manifest["file_count_excluding_manifest"] == len(global_manifest["files"])

print("V167 QA PASS")
print("catalog=587 local=587 hash_ok=587 archival_captures=2 route_grammar=closed target_bodies=open")
print("exact_entities=34 coverage_unchanged plan2009=NOT_LOCATED note3672=NOT_LOCATED execution=0/10 requests=0")
