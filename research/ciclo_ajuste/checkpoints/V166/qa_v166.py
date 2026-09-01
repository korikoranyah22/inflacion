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
EXPECTED = Decimal("63.4406041403540997520463142785031521252747951992299547614348265414453439585848248058817492708499966268585997481191265825")
INCREMENT = Decimal("0.1001910764253942328956536508152875266815433052383342475829736811049442227917417121900283549156556683401002043528534762")
Q4_INCOME_BCRA = Decimal("5652853.165516943874708")
Q4_EXPENSE_BCRA = Decimal("0.108985205433436")
Q4_NET_BCRA = Decimal("5652853.056531738441272")
SOURCE_ID = "bcra_entidades_jun2024_rioja_corrected_comparative_v166"
SOURCE_SHA = "991ce57930183c65095c64c6a3abc44f02e419b5186f2287c78e9f7359763719"
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


state = rows(HERE / "CURRENT_STATE_V166.csv")
by_entity = {row["entity"]: row for row in state}
assert sum(row["q4_four_leg_status"] == "EXACT" for row in state) == 34
assert sum(row["strict_panel_status"] == "ELIGIBLE" for row in state) == 34
rioja = by_entity["Banco Rioja S.A.U."]
assert rioja["q4_four_leg_status"] == "EXACT"
assert rioja["strict_panel_status"] == "ELIGIBLE"
assert "AUDITED_ANNEXQ_PLUS_LATER_BCRA" in rioja["fy_status"]
assert "COMPLETE_CANDIDATE_SET_ENTITY_YEAR_BASIS" in rioja["nine_month_status"]

candidate = rows(HERE / "BANCO_RIOJA_CANDIDATE_ACCOUNT_EXHAUSTION_V166.csv")
assert len(candidate) == 2
assert {row["period"] for row in candidate} == {"9M-2023", "FY-2023_raw"}
assert all(row["absent_candidate_accounts"] == "511007;511027;515034;521007;521022;525042" for row in candidate)
assert all(row["verdict"].startswith("COMPLETE_CANDIDATE_SET_TWO_BCRA_LEGS_ONLY") for row in candidate)

comparative = rows(HERE / "BANCO_RIOJA_LATER_BCRA_COMPARATIVE_V166.csv")
assert len(comparative) == 11
by_measure = {row["measure"]: row for row in comparative}
assert by_measure["total_assets"]["displayed_delta_million_ars"] == "62.3"
assert by_measure["current_result"]["displayed_delta_million_ars"] == "62.3"
assert by_measure["financial_income"]["displayed_delta_million_ars"] == "158.8"
assert by_measure["interest_income"]["displayed_delta_million_ars"] == "158.8"
for measure in ("total_liabilities", "other_financial_income", "financial_expense", "interest_expense", "other_financial_expense"):
    assert by_measure[measure]["displayed_delta_million_ars"] == "0.0"

timeline = rows(HERE / "BANCO_RIOJA_CLOSING_LAYER_TIMELINE_V166.csv")
assert len(timeline) == 5 and [row["sequence"] for row in timeline] == ["1", "2", "3", "4", "5"]
assert timeline[-1]["date_or_timestamp"] == "2024-06"
assert "corrected closing layer" in timeline[-1]["interpretation"]

promotion = rows(HERE / "BANCO_RIOJA_FOUR_LEG_PROMOTION_V166.csv")
assert len(promotion) == 4
legs = {row["leg"]: row for row in promotion}
assert Decimal(legs["income_bcra"]["q4_thousand_ars"]) == Q4_INCOME_BCRA
assert Decimal(legs["expense_bcra"]["q4_thousand_ars"]) == Q4_EXPENSE_BCRA
assert legs["income_otherfi"]["q4_thousand_ars"] == "0" and legs["income_otherfi"]["verdict"] == "EXACT_ZERO"
assert legs["expense_otherfi"]["q4_thousand_ars"] == "0" and legs["expense_otherfi"]["verdict"] == "EXACT_ZERO"

scenario = rows(HERE / "BANCO_RIOJA_Q4_SCENARIO_BOUND_V166.csv")
assert len(scenario) == 1 and scenario[0]["panel_use"] == "YES"
assert scenario[0]["remaining_gate"] == "NONE_FOUR_LEGS_EXACT_UNDER_ENTITY_YEAR_BASIS_RULE"

recon = rows(HERE / "BANCO_RIOJA_STOCK_AND_RESULT_RECONCILIATION_V166.csv")
assert len(recon) == 12
controls = {row["control_id"]: row for row in recon}
assert controls["BR166_02"]["difference_issuer_minus_raw"] == "158789"
assert controls["BR166_03"]["difference_issuer_minus_raw"] == "158789"
assert controls["BR166_10"]["difference_issuer_minus_raw"] == "62306"
assert controls["BR166_11"]["difference_issuer_minus_raw"] == "-96483"
assert controls["BR166_12"]["difference_issuer_minus_raw"] == "0"
assert controls["BR166_12"]["verdict"] == "LATER_BCRA_COMPARATIVE_AUTHENTICATES_RESULT_CLOSING_LAYER"

closing = rows(HERE / "BANCO_RIOJA_FULL_CLOSING_BALANCE_RECONCILIATION_V166.csv")
assert len(closing) == 5
closing_by_measure = {row["measure"]: row for row in closing}
assert closing_by_measure["total_assets"]["audited_minus_raw"] == "62306"
assert closing_by_measure["current_result"]["audited_minus_raw"] == "62306"
decomp = rows(HERE / "BANCO_RIOJA_CLOSING_ADJUSTMENT_DECOMPOSITION_V166.csv")
assert {row["delta"] for row in decomp if row["component"] == "repo_income"} == {"158789"}
assert {row["delta"] for row in decomp if row["component"] == "all_nonrepo_net_result"} == {"-96483"}

panel = rows(HERE / "FOUR_LEG_PASS_PANEL_V166.csv")
assert sum(row["system_panel_eligible_v72"] == "YES_EXACT_Q4_TARGET_BASIS" for row in panel) == 34
rioja_panel = [row for row in panel if row["entity"] == "Banco Rioja S.A.U."]
assert len(rioja_panel) == 1
rioja_panel = rioja_panel[0]
assert rioja_panel["system_panel_eligible_v72"] == "YES_EXACT_Q4_TARGET_BASIS"
assert Decimal(rioja_panel["income_bcra"]) == Q4_INCOME_BCRA
assert Decimal(rioja_panel["expense_bcra"]) == Q4_EXPENSE_BCRA
assert Decimal(rioja_panel["net_bcra"]) == Q4_NET_BCRA
assert Decimal(rioja_panel["income_otherfi"]) == Decimal(0)
assert Decimal(rioja_panel["expense_otherfi"]) == Decimal(0)

coverage = rows(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V166.csv")
assert len(coverage) == 1
assert Decimal(coverage[0]["asset_numerator_million_ars"]) == Decimal("61345602.215")
assert Decimal(coverage[0]["system_assets_million_ars"]) == Decimal("96697695.5")
assert Decimal(coverage[0]["asset_coverage_pct"]) == EXPECTED
assert Decimal(coverage[0]["asset_coverage_pct"]) - Decimal("63.3404130639287055191506606276878645985932518939916205138518528603403997357930830936917209159343409585184995437662731063") == INCREMENT

visual = rows(HERE / "V166_PDF_VISUAL_CONTROL.csv")
assert len(visual) == 2 and all(row["result"] == "PASS" for row in visual)
assert {row["artifact"] for row in visual} == {"202406e.pdf", "EEFF-BR-2023.pdf"}
routes = rows(HERE / "V166_PUBLIC_SEARCH_LOG.csv")
assert len(routes) == 4 and all(row["decision"] == "PROMOTION_SUPPORT" for row in routes)

catalog = rows(CATALOG)
assert len(catalog) == 585 and len({row["id"] for row in catalog}) == 585
source = next(row for row in catalog if row["id"] == SOURCE_ID)
assert source["sha256"] == SOURCE_SHA
source_path = REPO / source["archivo_local"].lstrip("/")
assert source_path.is_file() and source_path.stat().st_size == 6027314 and digest(source_path) == SOURCE_SHA
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    assert path.is_file() and digest(path) == row["sha256"].lower()

for path, expected_pages in (
    (source_path, 396),
    (CYCLE / "inputs/source_sync/v161/binaries/banco_rioja_eeff_fy2023.pdf", 86),
):
    info = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, errors="replace")
    assert info.returncode == 0 and f"Pages:           {expected_pages}" in info.stdout

master = rows(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V166.csv")
assert len(master) == 585 and all(row["exists"] == "True" and row["hash_ok"] == "True" for row in master)
assert not rows(AUDIT / "SOURCE_PRESERVATION_MISSING_V166.csv")
complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V166.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V166" and complete["exact_entities"] == 34
assert complete["master_catalog_entries"] == complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 585
assert Decimal(complete["strict_coverage_pct"]) == EXPECTED
assert Decimal(complete["strict_coverage_increment_v165_pp"]) == INCREMENT
assert complete["discovered_official_binary_recovery_queue"] == 0

bundle = rows(HERE / "V166_SOURCE_BUNDLE.csv")
assert len(bundle) == 7
for row in bundle:
    path = REPO / row["path"].lstrip("/")
    assert path.is_file() and path.stat().st_size == int(row["bytes"]) and digest(path) == row["sha256"]

sync = rows(CYCLE / "inputs/source_sync/v166/SOURCE_SYNC_FILE_MANIFEST_V166.csv")
assert len(sync) == 1 and sync[0]["sha256"] == SOURCE_SHA
assert sync[0]["format_verification"] == "PDF_MAGIC_VALID_396_PAGES_PAGE261_VISUALLY_INSPECTED"

register = rows(HERE / "E0_REQUEST_RESPONSE_REGISTER_V166.csv")
assert len(register) == 6 and all(row["status"] == "DRAFT_NOT_SENT" and row["submitted_on"] == "N/A" for row in register)
combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined

manifest = json.loads((HERE / "MANIFEST_V166.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V166" and manifest["parent_checkpoint"] == "V165"
assert manifest["exact_entities"] == 34 and manifest["new_promotions"] == ["Banco Rioja S.A.U."]
assert Decimal(manifest["strict_coverage_pct"]) == EXPECTED
for item in manifest["files"]:
    path = HERE / item["path"]
    assert path.is_file() and path.stat().st_size == item["bytes"] and digest(path) == item["sha256"]

global_manifest = json.loads((CYCLE / "MANIFEST_SHA256.json").read_text(encoding="utf-8-sig"))
assert global_manifest["checkpoint"] == "V166" and global_manifest["exact_entities"] == 34
assert Decimal(global_manifest["strict_coverage_pct"]) == EXPECTED
assert global_manifest["file_count_excluding_manifest"] == len(global_manifest["files"])

print("V166 QA PASS")
print(f"catalog=585 local=585 hash_ok=585 exact_entities=34 coverage={EXPECTED}")
print(f"rioja_q4_income_bcra={Q4_INCOME_BCRA} expense_bcra={Q4_EXPENSE_BCRA} otherfi=0/0 promotion=1 requests=0")
