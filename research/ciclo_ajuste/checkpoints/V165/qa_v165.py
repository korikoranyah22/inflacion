from decimal import Decimal, getcontext
from pathlib import Path
import csv
import hashlib
import json
import subprocess


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
EXPECTED = Decimal("63.3404130639287055191506606276878645985932518939916205138518528603403997357930830936917209159343409585184995437662731063")
getcontext().prec = 120


def rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


state = rows(HERE / "CURRENT_STATE_V165.csv")
by_entity = {row["entity"]: row for row in state}
assert sum(row["q4_four_leg_status"] == "EXACT" for row in state) == 33
assert sum(row["strict_panel_status"] == "ELIGIBLE" for row in state) == 33
rioja = by_entity["Banco Rioja S.A.U."]
assert rioja["q4_four_leg_status"] == "N/D_STRICT_CLOSING_PACKAGE_RECONCILED_JOURNAL_AND_9M_OPENING_ABSENT"
assert "ASSETS_RESULT_DELTA_62306K" in rioja["fy_status"]
assert "NO_ISSUER_REPO_RESULT_OPENING" in rioja["nine_month_status"]

closing = rows(HERE / "BANCO_RIOJA_FULL_CLOSING_BALANCE_RECONCILIATION_V165.csv")
assert len(closing) == 5
by_measure = {row["measure"]: row for row in closing}
assert by_measure["total_assets"] == {
    "control_id":"BR165_01","measure":"total_assets","raw_thousand_ars":"96882462",
    "audited_thousand_ars":"96944768","audited_minus_raw":"62306","verdict":"EXACT_CLOSING_LAYER_DELTA",
}
assert by_measure["total_liabilities"]["raw_thousand_ars"] == by_measure["total_liabilities"]["audited_thousand_ars"] == "62510206"
assert by_measure["equity_before_current_result"]["raw_thousand_ars"] == by_measure["equity_before_current_result"]["audited_thousand_ars"] == "35589212"
assert by_measure["current_result"]["raw_thousand_ars"] == "-1216956"
assert by_measure["current_result"]["audited_thousand_ars"] == "-1154650"
assert by_measure["current_result"]["audited_minus_raw"] == "62306"
assert by_measure["net_equity"]["raw_thousand_ars"] == "34372256"
assert by_measure["net_equity"]["audited_thousand_ars"] == "34434562"

decomp = rows(HERE / "BANCO_RIOJA_CLOSING_ADJUSTMENT_DECOMPOSITION_V165.csv")
assert len(decomp) == 6
by_component = {(row["side"], row["component"]): row for row in decomp}
assert by_component[("assets","repo_stock")]["delta"] == "158789"
assert by_component[("result","repo_income")]["delta"] == "158789"
assert by_component[("assets","all_nonrepo_assets")]["delta"] == "-96483"
assert by_component[("result","all_nonrepo_net_result")]["delta"] == "-96483"
assert by_component[("assets","total_assets")]["delta"] == "62306"
assert by_component[("result","current_result")]["delta"] == "62306"
assert Decimal("158789") + Decimal("-96483") == Decimal("62306")

ief = rows(HERE / "BANCO_RIOJA_BCRA_IEF_PUBLICATION_CONTROL_V165.csv")
assert len(ief) == 2
assert ief[0]["period"] == "2023-09" and ief[0]["audit_marker"] == "8_SIN_OBSERVACIONES"
assert ief[1]["period"] == "2023-12" and ief[1]["total_assets_million_ars"] == "96882.5"
assert ief[1]["current_result_million_ars"] == "-1217.0"

timeline = rows(HERE / "BANCO_RIOJA_CLOSING_LAYER_TIMELINE_V165.csv")
assert len(timeline) == 4 and [row["sequence"] for row in timeline] == ["1","2","3","4"]
assert timeline[0]["date_or_timestamp"].startswith("2024-03-04")
assert timeline[1]["date_or_timestamp"].startswith("2024-03-08")
assert timeline[2]["date_or_timestamp"] == "2024-03-11"
assert timeline[3]["date_or_timestamp"].startswith("2024-04-23")
assert "not proof" in timeline[0]["interpretation"] and "not formal" in timeline[3]["interpretation"]

recon = rows(HERE / "BANCO_RIOJA_STOCK_AND_RESULT_RECONCILIATION_V165.csv")
assert len(recon) == 11
controls = {row["control_id"]: row for row in recon}
assert controls["BR165_02"]["difference_issuer_minus_raw"] == "158789"
assert controls["BR165_03"]["difference_issuer_minus_raw"] == "158789"
assert controls["BR165_10"]["difference_issuer_minus_raw"] == "62306"
assert controls["BR165_10"]["verdict"] == "EXACT_FULL_CLOSING_PACKAGE_DUAL_DELTA"
assert controls["BR165_11"]["difference_issuer_minus_raw"] == "-96483"

note = (HERE / "BANCO_RIOJA_CLOSING_PACKAGE_NOTE_V165.md").read_text(encoding="utf-8-sig")
assert "158.789 - 96.483 = 62.306" in note
assert "no revela si existió un asiento compuesto o varios asientos" in note
assert "no hay promoción" in note
correction = (HERE / "CORRECTION_LOG_V165.md").read_text(encoding="utf-8-sig")
assert "29.058.359k" in correction and "158.789k" in correction and "238.183k" in correction

panel = rows(HERE / "FOUR_LEG_PASS_PANEL_V165.csv")
assert sum(row["system_panel_eligible_v72"] == "YES_EXACT_Q4_TARGET_BASIS" for row in panel) == 33
rioja_panel = [row for row in panel if row["entity"] == "Banco Rioja S.A.U."]
assert len(rioja_panel) == 1 and rioja_panel[0]["system_panel_eligible_v72"] == "NO"
assert rioja_panel[0]["quality"] == "FULL_CLOSING_PACKAGE_RECONCILED_JOURNAL_AND_9M_OPENING_ABSENT"
coverage = rows(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V165.csv")
assert len(coverage) == 1
assert Decimal(coverage[0]["asset_coverage_pct"]) == EXPECTED
assert Decimal(coverage[0]["asset_numerator_million_ars"]) == Decimal("61248719.753")

visual = rows(HERE / "V165_PDF_VISUAL_CONTROL.csv")
assert len(visual) == 5 and all(row["result"] == "PASS" for row in visual)
assert {row["artifact"] for row in visual} == {"202309e.pdf","202312e.pdf","EEFF-BR-2023.pdf"}
routes = rows(HERE / "V165_PUBLIC_SEARCH_LOG.csv")
assert len(routes) == 4
assert sum("LOCALLY_PRESERVED" in row["result"] for row in routes) == 3
assert routes[-1]["decision"] == "HOLD_RESULT_FLOW_GATE"

catalog = rows(CATALOG)
assert len(catalog) == 584 and len({row["id"] for row in catalog}) == 584
required_ids = {"bcra_entidades_sep2023_hist", "bcra_entidades_dic2023_red_pases"}
catalog_ids = {row["id"] for row in catalog}
assert required_ids <= catalog_ids
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    assert path.is_file() and digest(path) == row["sha256"].lower()

expected_pages = {
    "bcra_entidades_sep2023_hist":401,
    "bcra_entidades_dic2023_red_pases":401,
}
for row in catalog:
    if row["id"] not in expected_pages:
        continue
    path = REPO / row["archivo_local"].lstrip("/")
    info = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, errors="replace")
    assert info.returncode == 0 and f"Pages:           {expected_pages[row['id']]}" in info.stdout

master = rows(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V165.csv")
assert len(master) == 584 and all(row["exists"] == "True" and row["hash_ok"] == "True" for row in master)
assert not rows(AUDIT / "SOURCE_PRESERVATION_MISSING_V165.csv")
complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V165.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V165" and complete["exact_entities"] == 33
assert complete["master_catalog_entries"] == complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 584
assert complete["discovered_official_binary_recovery_queue"] == 0
assert complete["request_drafts_status"] == "DRAFT_NOT_SENT"

bundle = rows(HERE / "V165_SOURCE_BUNDLE.csv")
assert len(bundle) == 5
for row in bundle:
    path = REPO / row["path"].lstrip("/")
    assert path.is_file() and digest(path) == row["sha256"]

register = rows(HERE / "E0_REQUEST_RESPONSE_REGISTER_V165.csv")
assert len(register) == 6 and all(row["status"] == "DRAFT_NOT_SENT" and row["submitted_on"] == "N/A" for row in register)
combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined

manifest = json.loads((HERE / "MANIFEST_V165.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V165" and manifest["parent_checkpoint"] == "V164"
assert manifest["exact_entities"] == 33 and manifest["new_promotions"] == []
assert "+62306k" in manifest["rioja_finding"] and "+158789k" in manifest["rioja_finding"] and "-96483k" in manifest["rioja_finding"]
for item in manifest["files"]:
    path = HERE / item["path"]
    assert path.is_file() and path.stat().st_size == item["bytes"] and digest(path) == item["sha256"]

global_manifest = json.loads((CYCLE / "MANIFEST_SHA256.json").read_text(encoding="utf-8-sig"))
assert global_manifest["checkpoint"] == "V165" and global_manifest["exact_entities"] == 33
assert global_manifest["file_count_excluding_manifest"] == len(global_manifest["files"])

print("V165 QA PASS")
print(f"catalog=584 local=584 hash_ok=584 exact_entities=33 coverage={EXPECTED}")
print("rioja_full_closing_delta=62306 repo_component=158789 nonrepo_offset=-96483 promotions=0 requests=0")
