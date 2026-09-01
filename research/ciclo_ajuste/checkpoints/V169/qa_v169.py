from pathlib import Path
import csv
import hashlib
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
COVERAGE = "63.4406041403540997520463142785031521252747951992299547614348265414453439585848248058817492708499966268585997481191265825"
NEW_IDS = {
    "infoleg_actos_gobierno_index_2008_2010_v169",
    "wayback_sigen_planannualpdfs_late_inventory_2013_2020_v169",
    "enargas_informe_anual_2009_index_v169",
    "enargas_informe_anual_2009_capitulo1_v169",
    "enargas_informe_anual_2009_full_mirror_v169",
}


def rows(name):
    with (HERE / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


with (REPO / "data/fuentes/FUENTES.csv").open(encoding="utf-8-sig", newline="") as handle:
    catalog = list(csv.DictReader(handle))
assert len(catalog) == 596 and len({row["id"] for row in catalog}) == 596
assert NEW_IDS <= {row["id"] for row in catalog}
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    assert path.is_file() and sha256(path) == row["sha256"].lower()

audit = list(csv.DictReader((AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V169.csv").open(encoding="utf-8-sig", newline="")))
assert len(audit) == 596
assert all(row["exists"] == "True" and row["hash_ok"] == "True" for row in audit)
assert (AUDIT / "SOURCE_PRESERVATION_MISSING_V169.csv").read_text(encoding="utf-8-sig").count("\n") == 1

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V169.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V169"
assert complete["master_catalog_entries"] == complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 596
assert complete["remaining_catalog_physical_or_hash_gaps"] == 0
assert complete["infoleg_actos_issues_checked"] == 78
assert complete["wayback_late_directory_pdf_rows"] == 25
assert complete["contemporary_sigen_note_recipient_id_pairs"] == 6
assert complete["plan_sigen_2009_body_located"] is False
assert complete["plan_sigen_2009_approval_act_located"] is False
assert complete["note_3672_09_body_located"] is False
assert complete["note_3672_recipient_identifier_located"] is False
assert complete["requests_submitted"] == 0 and complete["responses_received"] == 0
assert complete["saf355_certifications_located"] == 0 and complete["executed_historical_bank_rows_confirmed"] == 0

scan = rows("E0_PLAN_2009_LATE_ARCHIVE_COLLECTION_SCAN_V169.csv")
assert len(scan) == 6
assert sum(row["classification"] == "SERVICE_UNAVAILABLE_NOT_NEGATIVE" for row in scan) == 1
assert next(row for row in scan if row["scan_id"] == "LA169_04")["service_state"] == "ERROR"
assert any(row["classification"] == "EDITORIAL_SURFACE_NEGATIVE_SCOPED" for row in scan)

publication = rows("E0_PLAN_2009_PUBLICATION_SURFACE_COMPARATOR_V169.csv")
assert len(publication) == 6
assert {row["status"] for row in publication} >= {
    "PRECEDING_PUBLICATION_CONTROL", "TARGET_EXISTENCE_CONFIRMED", "EDITORIAL_SURFACE_GAP",
    "FOLLOWING_PUBLICATION_CONTROL", "LATE_DIRECTORY_CONTINUITY_TARGET_ABSENT",
}

dual = rows("E0_NOTE_3672_DUAL_IDENTIFIER_ROUTE_V169.csv")
assert len(dual) == 6
assert {row["sigen_note"] for row in dual} == {"1368/09", "1927/09", "2668/09", "3159/09", "4986/09", "5086/09"}
assert {row["recipient_record"] for row in dual} == {"8833/09", "11884/09", "16395/09", "19970/09", "30571/09", "30680/09"}
assert all(row["status"] == "COMPARATOR_ONLY" and "No identifica" in row["target_limit"] for row in dual)

note_route = rows("E0_NOTE_3672_ARCHIVAL_SEARCH_V169.csv")
assert {"RECIPIENT_DUAL_IDENTIFIER_PATTERN_PROVED", "RECIPIENT_IDENTIFIER_OPEN"} <= {row["status"] for row in note_route}
assert any(row["route_id"] == "N169_07" and "no localizado" in row["result"] for row in note_route)

body = rows("E0_PLAN_2009_BODY_RECOVERY_STATUS_V169.csv")
assert len(body) == 5
assert sum(row["local_copy"] == "YES" for row in body) == 1
assert all(row["local_copy"] == "NO" for row in body if row["object"] != "plananual2009.asp")

pdf_controls = rows("V169_PDF_VISUAL_AND_TEXT_CONTROL.csv")
assert len(pdf_controls) == 3
assert {row["result"] for row in pdf_controls} == {"TEXT_CONFIRMED_VISUAL_CLIPPING", "PASS", "CONTENT_MATCH"}

bundle = rows("V169_SOURCE_BUNDLE.csv")
assert len(bundle) == 5
for row in bundle:
    path = REPO / row["path"].lstrip("/")
    assert path.is_file() and path.stat().st_size == int(row["bytes"]) and sha256(path) == row["sha256"]

sync = CYCLE / "inputs/source_sync/v169"
sync_rows = list(csv.DictReader((sync / "SOURCE_SYNC_FILE_MANIFEST_V169.csv").open(encoding="utf-8-sig", newline="")))
assert len(sync_rows) == 5

method_breaks = rows("E0_FISCAL_METHOD_BREAKS_V169.csv")
required_breaks = {
    "actos_gobierno_gap_not_universal_nonpublication", "late_directory_absence_not_deletion_date",
    "recipient_dual_id_comparator_not_target_id", "common_crawl_timeout_not_negative",
    "official_split_pdf_render_defect_mirror_not_emitter",
}
assert required_breaks <= {row["break_id"] for row in method_breaks}

keys = rows("E0_REQUEST_SEARCH_KEY_MATRIX_V169.csv")
assert {"SK169_01", "SK169_02", "SK169_03"} <= {row["key_id"] for row in keys}
objects = rows("E0_V169_REQUEST_OBJECTS.csv")
assert {"RO169_01", "RO169_02", "RO169_03"} <= {row["row_id"] for row in objects}
assert all(row["status"] == "DRAFT_NOT_SENT" for row in objects)
assert rows("E0_V169_REQUEST_OBJECTS.csv") == rows("E0_V169_REQUEST_OBJECTS_V169.csv")

for name in (
    "REQUEST_AGN_2018_REPLY_V169.md", "REQUEST_BCRA_CRYL_SETTLEMENT_V169.md",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V169.md", "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V169.md",
    "REQUEST_CNV_CUSTODY_RECORDS_V169.md", "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V169.md",
):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "DRAFT_NOT_SENT" in text or "BORRADOR_NO_ENVIADO" in text
assert "Adenda V169 · doble identificador documental" in (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V169.md").read_text(encoding="utf-8-sig")
assert "Adenda V169 · doble identificador documental" in (HERE / "REQUEST_SUBMISSION_CHECKLIST_V169.md").read_text(encoding="utf-8-sig")

panel = rows("FOUR_LEG_PASS_PANEL_V169.csv")
assert len(panel) == 45
assert sum(row["system_panel_eligible_v72"] == "YES_EXACT_Q4_TARGET_BASIS" for row in panel) == 34
coverage = rows("STRICT_Q4_FOUR_LEG_COVERAGE_V169.csv")
assert len(coverage) == 1 and coverage[0]["asset_coverage_pct"] == COVERAGE
assert coverage[0]["asset_numerator_million_ars"] == "61345602.215"
assert coverage[0]["system_assets_million_ars"] == "96697695.5"

manifest = json.loads((HERE / "MANIFEST_V169.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V169" and manifest["parent_checkpoint"] == "V168"
assert manifest["exact_entities"] == 34 and manifest["strict_coverage_pct"] == COVERAGE
assert manifest["requests_submitted"] == 0 and manifest["new_promotions"] == []
assert manifest["plan_sigen_2009_body"] == "NOT_LOCATED"
assert manifest["note_3672_recipient_identifier"] == "NOT_LOCATED"
for row in manifest["files"]:
    path = HERE / row["path"]
    assert path.is_file() and path.stat().st_size == row["bytes"] and sha256(path) == row["sha256"]

readme = (HERE / "README_V169.md").read_text(encoding="utf-8-sig")
assert "596/596" in readme and "78 ediciones" in readme and "25 PDFs" in readme
assert "seis borradores no enviados" in readme and "solicitudes enviadas 0" in readme
assert "SAF355 0/5" in readme and "ejecución 0/10" in readme

print("V169 QA PASS · 596/596 · infoleg=78 · wayback=25 · dual_pairs=6 · panel=34 · requests=0 · SAF355=0/5 · execution=0/10")
