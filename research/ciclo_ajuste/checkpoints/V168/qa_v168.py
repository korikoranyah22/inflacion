from pathlib import Path
import csv
import gzip
import hashlib
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
HIST = CYCLE / "inputs" / "historical_retrieval" / "v168" / "binaries"
SYNC = CYCLE / "inputs" / "source_sync" / "v168"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
COVERAGE = "63.4406041403540997520463142785031521252747951992299547614348265414453439585848248058817492708499966268585997481191265825"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


expected = {
    "sigen_planannual_2009_wayback_20090221_v168": ("sigen_planannual_2009_20090221.html", 23667, "665f4b67f1295096cfa8f0921b360963cc56fcdf26caed106e9aa062f3907866"),
    "sigen_resolutions_index_cc_20100729_v168": ("sigen_resolutions_index_20100729.arc.gz", 5762, "c9eb44dc4b260e3aba8173c8a96ccf0b02777703aff9474704d6c17390759586"),
    "sigen_normative_index_cc_20100729_v168": ("sigen_normative_index_20100729.arc.gz", 4451, "f9df6c7ec242b81734446bf9b8b46e2a50ce619ddc170871c1c379403a1c6687"),
    "sigen_resolutions_index_cc_20120205_v168": ("sigen_resolutions_index_20120205.arc.gz", 6005, "89d267552b9e3e6f155f812bb680b7827dfacc730b46e61263ae02ce39781bdc"),
}

# Catalog, local copies and master audit.
catalog = read_csv(CATALOG)
assert len(catalog) == 591 and len({row["id"] for row in catalog}) == 591
by_id = {row["id"]: row for row in catalog}
for source_id, (name, size, digest) in expected.items():
    assert source_id in by_id
    path = HIST / name
    assert path.is_file() and path.stat().st_size == size and sha256(path) == digest
    assert by_id[source_id]["sha256"] == digest

audit = read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V168.csv")
assert len(audit) == 591
assert all(row["exists"] == "True" and row["hash_ok"] == "True" for row in audit)
assert read_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V168.csv") == []

# Target page is located, but bodies remain open.
page = (HIST / "sigen_planannual_2009_20090221.html").read_bytes().decode("cp1252", errors="replace")
assert "Plan Sigen 2009" in page
links = read_csv(HERE / "E0_SIGEN_PLAN_2009_ARCHIVED_PAGE_LINKS_V168.csv")
assert len(links) == 14
assert sum(row["document_class"] == "PLAN_MAIN" for row in links) == 1
assert sum(row["document_class"] == "ANNEX_F_TABLE" for row in links) == 11
assert {int(row["table_number"]) for row in links if row["table_number"]} == set(range(8, 19))
assert sum(row["document_class"] == "ANNEX_G" for row in links) == 1
assert sum(row["document_class"] == "RED_FEDERAL_PLAN" for row in links) == 1
assert all(row["body_preserved"] == "NO" for row in links)

status = {row["object"]: row for row in read_csv(HERE / "E0_PLAN_2009_BODY_RECOVERY_STATUS_V168.csv")}
assert status["plananual2009.asp"]["status"] == "PAGE_LOCATED"
assert status["Plan SIGEN 2009"]["status"] == "BODY_NOT_LOCATED"
assert status["Anexo F cuadros 8-18"]["local_copy"] == "NO"
assert status["Anexo G capacitación"]["local_copy"] == "NO"

grammar = {row["control_id"]: row for row in read_csv(HERE / "E0_SIGEN_HISTORICAL_ROUTE_GRAMMAR_V168.csv")}
assert grammar["RG168_03"]["result"] == "TARGET_YEAR_PAGE_AND_EXACT_LINK_INVENTORY_RECOVERED"
assert grammar["RG168_03"]["document_route"].endswith("Plan SIGEN 2009.pdf")

# Resolution/normative index schema is real but not promoted to results.
res_2010 = gzip.open(HIST / "sigen_resolutions_index_20100729.arc.gz", "rb").read().decode("cp1252", errors="replace")
res_2012 = gzip.open(HIST / "sigen_resolutions_index_20120205.arc.gz", "rb").read().decode("cp1252", errors="replace")
norm = gzip.open(HIST / "sigen_normative_index_20100729.arc.gz", "rb").read().decode("cp1252", errors="replace")
for text in (res_2010, res_2012):
    assert 'action="Result_resoluciones.asp"' in text
    assert "txtNumero" in text and "txtKeywords" in text and "value='2008'" in text
assert all(f"normas{i:02}.asp" in norm for i in range(1, 6))
schema = read_csv(HERE / "E0_SIGEN_RESOLUTION_INDEX_SCHEMA_V168.csv")
assert len(schema) == 8
assert any(row["name_or_value"] == "txtNumero" for row in schema)
assert any("POST" in row["limit"] for row in schema)

# Approval inference and Note 3672 limits.
approval = {row["test_id"]: row for row in read_csv(HERE / "E0_PLAN_2009_APPROVAL_ACT_SEARCH_V168.csv")}
assert approval["AA168_01"]["classification"] == "FACT_CONFIRMED"
assert "15/12/2008" in approval["AA168_01"]["result"]
assert approval["AA168_03"]["classification"] == "DATE_SCOPED_PUBLICATION_NEGATIVE"
assert approval["AA168_05"]["classification"] == "INFERENCE_NOT_FACT"

note = read_csv(HERE / "E0_NOTE_3672_ARCHIVAL_SEARCH_V168.csv")
assert len(note) == 5
assert note[0]["status"] == "REFERENCE_LOCATED_BODY_OPEN"
assert sum("NEGATIVE_SCOPED" in row["status"] for row in note) == 3
assert note[-1]["status"] == "SYSTEM_ENTRY_NOT_LOCATED"

search = {row["search_id"]: row for row in read_csv(HERE / "V168_PUBLIC_SEARCH_LOG.csv")}
assert len(search) == 11
assert search["PS168_01"]["classification"] == "TARGET_PAGE_CAPTURES_LOCATED"
assert search["PS168_03"]["classification"] == "BODY_ARCHIVE_NEGATIVE_SCOPED"
assert search["PS168_05"]["classification"] == "DYNAMIC_RESULT_NOT_ARCHIVED"
assert search["PS168_08"]["classification"] == "PUBLICATION_NEGATIVE_DATE_SCOPED"
assert search["PS168_11"]["classification"] == "SERVICE_UNAVAILABLE_NOT_NEGATIVE"

# Unchanged panel and execution gates.
panel = read_csv(HERE / "FOUR_LEG_PASS_PANEL_V168.csv")
assert len(panel) == 45
assert sum(row["system_panel_eligible_v72"] == "YES_EXACT_Q4_TARGET_BASIS" for row in panel) == 34
coverage = read_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V168.csv")
assert len(coverage) == 1 and COVERAGE in coverage[0].values()
assert coverage[0]["coverage_set"].startswith("V168 strict 34-entity set")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V168.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V168"
assert complete["master_catalog_entries"] == 591 and complete["physical_local_hash_ok"] == 591
assert complete["plan_sigen_2009_page_located"] is True
assert complete["plan_sigen_2009_link_inventory_count"] == 14
assert complete["plan_sigen_2009_body_located"] is False
assert complete["plan_sigen_2009_approval_act_located"] is False
assert complete["note_3672_09_body_located"] is False
assert complete["requests_submitted"] == 0 and complete["responses_received"] == 0
assert complete["saf355_certifications_located"] == 0
assert complete["executed_historical_bank_rows_confirmed"] == 0

request_objects = read_csv(HERE / "E0_V168_REQUEST_OBJECTS.csv")
assert request_objects and all(row["status"] == "DRAFT_NOT_SENT" for row in request_objects)

# Sync, summaries and manifests.
sync = read_csv(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V168.csv")
assert len(sync) == 4 and len({row["sha256"] for row in sync}) == 4
for row in sync:
    path = REPO / row["relative_path"].lstrip("/")
    assert path.is_file() and path.stat().st_size == int(row["size_bytes"])
    assert sha256(path) == row["sha256"]

readme = (HERE / "README_V168.md").read_text(encoding="utf-8-sig")
assert "591/591" in readme and "14 enlaces" in readme
assert "no capturados" in readme and "0/10" in readme and "no enviados" in readme

manifest = json.loads((HERE / "MANIFEST_V168.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V168" and manifest["parent_checkpoint"] == "V167"
assert manifest["plan_sigen_2009_page"] == "LOCATED"
assert manifest["plan_sigen_2009_body"] == "NOT_LOCATED"
assert manifest["approval_act"] == "NOT_LOCATED"
assert manifest["note_3672_09_body"] == "NOT_LOCATED"
assert manifest["requests_submitted"] == 0 and manifest["exact_entities"] == 34

global_manifest = json.loads((CYCLE / "MANIFEST_SHA256.json").read_text(encoding="utf-8-sig"))
assert global_manifest["checkpoint"] == "V168"
assert "591 master" in global_manifest["source_audit"]

print("V168 QA PASS · 591/591 · plan page 1 · links 14 · bodies open · exact 34 · requests 0")
