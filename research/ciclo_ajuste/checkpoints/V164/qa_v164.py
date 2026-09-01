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


state = rows(HERE / "CURRENT_STATE_V164.csv")
by_entity = {row["entity"]: row for row in state}
assert sum(row["q4_four_leg_status"] == "EXACT" for row in state) == 33
assert sum(row["strict_panel_status"] == "ELIGIBLE" for row in state) == 33
rioja = by_entity["Banco Rioja S.A.U."]
assert rioja["q4_four_leg_status"] == "N/D_STRICT_RESULT_RECONCILIATION_ABSENT_STOCK_LAYER_DIFFERENCE_CONFIRMED"
assert "PUBLICATION_EQUALS_SUPERVISION_29217148K" in rioja["fy_status"]
assert "QUARTERLY_DISCIPLINE_MARKET_STOCK_TRAJECTORY" in rioja["nine_month_status"]

trajectory = rows(HERE / "BANCO_RIOJA_QUARTERLY_STOCK_TRAJECTORY_V164.csv")
assert len(trajectory) == 4
expected_stocks = ["4445150", "8231958", "14191142", "29217148"]
assert [row["issuer_publication_stock_thousand_ars"] for row in trajectory] == expected_stocks
assert all(row["issuer_publication_stock_thousand_ars"] == row["issuer_supervision_stock_thousand_ars"] for row in trajectory)
assert trajectory[2]["raw_stock_thousand_ars"] == "14191142" and trajectory[2]["issuer_minus_raw"] == "0"
assert trajectory[3]["raw_stock_thousand_ars"] == "29058359" and trajectory[3]["issuer_minus_raw"] == "158789"
assert trajectory[3]["quarter_change_issuer"] == "15026006"

crosswalk = rows(HERE / "BCRA_ACCOUNT_AND_REPORTING_CROSSWALK_V164.csv")
assert len(crosswalk) == 4
by_account = {row["account"]: row for row in crosswalk}
assert set(by_account) == {"141144", "141222", "511108", "521108"}
assert by_account["141144"]["decision"] == by_account["141222"]["decision"] == "INCLUDE_IN_ACTIVE_REPO_STOCK"
assert by_account["511108"]["publication_mapping"] == "Ingresos por intereses"
assert by_account["511108"]["supervision_mapping"] == "Otros ingresos financieros"
assert by_account["521108"]["publication_mapping"] == "Egresos por intereses"
assert by_account["521108"]["supervision_mapping"] == "Otros egresos financieros"

pubsup = rows(HERE / "BANCO_RIOJA_PUBLICATION_SUPERVISION_CROSSWALK_V164.csv")
assert len(pubsup) == 4 and all(row["difference"] == "0" for row in pubsup)
assert pubsup[-1]["publication_thousand_ars"] == pubsup[-1]["supervision_thousand_ars"] == "29217148"

timeline = rows(HERE / "BANCO_RIOJA_CLOSING_LAYER_TIMELINE_V164.csv")
assert len(timeline) == 3
assert [row["sequence"] for row in timeline] == ["1", "2", "3"]
assert timeline[0]["date_or_timestamp"].startswith("2024-03-04")
assert timeline[1]["date_or_timestamp"] == "2024-03-11"
assert timeline[2]["date_or_timestamp"].startswith("2024-04-23")
assert "not proof" in timeline[0]["interpretation"] and "not formal" in timeline[2]["interpretation"]

recon = rows(HERE / "BANCO_RIOJA_STOCK_AND_RESULT_RECONCILIATION_V164.csv")
assert len(recon) == 9
controls = {row["control_id"]: row for row in recon}
assert controls["BR164_02"]["raw_values_thousand_ars"] == "28978965+79394"
assert controls["BR164_02"]["difference_issuer_minus_raw"] == "158789"
assert controls["BR164_02"]["verdict"] == "CLOSING_LAYER_DIFFERENCE_CONFIRMED_STOCK"
assert controls["BR164_03"]["difference_issuer_minus_raw"] == "158789"
assert controls["BR164_09"]["difference_issuer_minus_raw"] == "0"
assert controls["BR164_09"]["verdict"] == "EXACT_PUBLICATION_SUPERVISION_CLOSING_DISCLOSURE"

note = (HERE / "BANCO_RIOJA_CLOSING_LAYER_NOTE_V164.md").read_text(encoding="utf-8-sig")
assert "diferencia de capa de cierre" in note and "no prueban" in note
assert "No hay promoción" in note
correction = (HERE / "CORRECTION_LOG_V164.md").read_text(encoding="utf-8-sig")
assert "29.058.359k" in correction and "158.789k" in correction and "238.183k" in correction

panel = rows(HERE / "FOUR_LEG_PASS_PANEL_V164.csv")
assert sum(row["system_panel_eligible_v72"] == "YES_EXACT_Q4_TARGET_BASIS" for row in panel) == 33
rioja_panel = [row for row in panel if row["entity"] == "Banco Rioja S.A.U."]
assert len(rioja_panel) == 1 and rioja_panel[0]["system_panel_eligible_v72"] == "NO"
assert rioja_panel[0]["quality"] == "STOCK_LAYER_DIFFERENCE_CONFIRMED_RESULT_ADJUSTMENT_UNAUTHENTICATED"
coverage = rows(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V164.csv")
assert len(coverage) == 1
assert Decimal(coverage[0]["asset_coverage_pct"]) == EXPECTED
assert Decimal(coverage[0]["asset_numerator_million_ars"]) == Decimal("61248719.753")

visual = rows(HERE / "V164_PDF_VISUAL_CONTROL.csv")
assert len(visual) == 13 and all(row["result"] == "PASS" for row in visual)
assert {row["artifact"] for row in visual} == {"DM-31-03-23.pdf", "DM-30-06-23.pdf", "DM-31-12-23.pdf", "A6358.pdf", "A6402.pdf"}
routes = rows(HERE / "V164_PUBLIC_SEARCH_LOG.csv")
assert len(routes) == 5
assert sum("PRESERVED" in row["result"] for row in routes) == 2
assert any(row["result"] == "BINARY_DIRECT_NAVIGATION_BLOCKED_BY_CLIENT" for row in routes)

catalog = rows(CATALOG)
assert len(catalog) == 584 and len({row["id"] for row in catalog}) == 584
new_ids = {
    "banco_rioja_disciplina_mercado_q1_2023_v164",
    "banco_rioja_disciplina_mercado_6m2023_v164",
    "banco_rioja_disciplina_mercado_fy2023_v164",
    "bcra_comunicacion_a6358_plan_cuentas_v164",
    "bcra_comunicacion_a6402_supervision_publicacion_v164",
}
catalog_ids = {row["id"] for row in catalog}
assert new_ids <= catalog_ids
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    assert path.is_file() and digest(path) == row["sha256"].lower()

expected_pages = {
    "banco_rioja_disciplina_mercado_q1_2023_v164":9,
    "banco_rioja_disciplina_mercado_6m2023_v164":9,
    "banco_rioja_disciplina_mercado_fy2023_v164":9,
    "bcra_comunicacion_a6358_plan_cuentas_v164":40,
    "bcra_comunicacion_a6402_supervision_publicacion_v164":33,
}
for row in catalog:
    if row["id"] not in expected_pages:
        continue
    path = REPO / row["archivo_local"].lstrip("/")
    info = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, errors="replace")
    assert info.returncode == 0 and f"Pages:           {expected_pages[row['id']]}" in info.stdout

master = rows(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V164.csv")
assert len(master) == 584 and all(row["exists"] == "True" and row["hash_ok"] == "True" for row in master)
assert not rows(AUDIT / "SOURCE_PRESERVATION_MISSING_V164.csv")
complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V164.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V164" and complete["exact_entities"] == 33
assert complete["master_catalog_entries"] == complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 584
assert complete["discovered_official_binary_recovery_queue"] == 0
assert complete["request_drafts_status"] == "DRAFT_NOT_SENT"

sync = rows(CYCLE / "inputs/source_sync/v164/SOURCE_SYNC_FILE_MANIFEST_V164.csv")
assert len(sync) == 5
for row in sync:
    path = REPO / row["relative_path"].lstrip("/")
    assert path.is_file() and digest(path) == row["sha256"]

register = rows(HERE / "E0_REQUEST_RESPONSE_REGISTER_V164.csv")
assert len(register) == 6 and all(row["status"] == "DRAFT_NOT_SENT" and row["submitted_on"] == "N/A" for row in register)
combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined

manifest = json.loads((HERE / "MANIFEST_V164.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V164" and manifest["parent_checkpoint"] == "V163"
assert manifest["exact_entities"] == 33 and manifest["new_promotions"] == []
assert "158789" in manifest["rioja_finding"] and "queue closed 0" in manifest["source_archive"]
for item in manifest["files"]:
    path = HERE / item["path"]
    assert path.is_file() and path.stat().st_size == item["bytes"] and digest(path) == item["sha256"]

global_manifest = json.loads((CYCLE / "MANIFEST_SHA256.json").read_text(encoding="utf-8-sig"))
assert global_manifest["checkpoint"] == "V164" and global_manifest["exact_entities"] == 33
assert global_manifest["file_count_excluding_manifest"] == len(global_manifest["files"])

print("V164 QA PASS")
print(f"catalog=584 local=584 hash_ok=584 exact_entities=33 coverage={EXPECTED}")
print("rioja_quarters=4 publication_equals_supervision=4 closing_residual=158789 queue=0 promotions=0 requests=0")
