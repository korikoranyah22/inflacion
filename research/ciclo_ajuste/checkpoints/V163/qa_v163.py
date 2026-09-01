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
FACTOR = Decimal("1.532908152197492")
EXPECTED = Decimal("63.3404130639287055191506606276878645985932518939916205138518528603403997357930830936917209159343409585184995437662731063")
COUNTERFACTUAL = Decimal("63.4406041403540997520463142785031521252747951992299547614348265414453439585848248058817492708499966268585997481191265825")
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


state = rows(HERE / "CURRENT_STATE_V163.csv")
by_entity = {row["entity"]: row for row in state}
assert sum(row["q4_four_leg_status"] == "EXACT" for row in state) == 33
assert sum(row["strict_panel_status"] == "ELIGIBLE" for row in state) == 33
rioja_state = by_entity["Banco Rioja S.A.U."]
assert rioja_state["q4_four_leg_status"] == "N/D_STRICT_ADJUSTING_ENTRY_UNAUTHENTICATED"
assert "DUAL_RESIDUAL_158789K" in rioja_state["fy_status"]
assert "DM2024_NEGATIVE_COMPARATOR" in rioja_state["nine_month_status"]
assert by_entity["HSBC Bank Argentina S.A."]["q4_four_leg_status"] == "N/D_STRICT"

recon = rows(HERE / "BANCO_RIOJA_STOCK_AND_RESULT_RECONCILIATION_V163.csv")
assert len(recon) == 8
controls = {row["control_id"]: row for row in recon}
assert controls["BR163_01"]["raw_sum_thousand_ars"] == "14191142"
assert controls["BR163_02"]["raw_values_thousand_ars"] == "28978965+79394"
assert controls["BR163_02"]["raw_sum_thousand_ars"] == "29058359"
assert controls["BR163_02"]["difference_issuer_minus_raw"] == "158789"
assert controls["BR163_03"]["difference_issuer_minus_raw"] == "158789"
assert controls["BR163_02"]["verdict"] == controls["BR163_03"]["verdict"] == "EXACT_DUAL_SIDED_RESIDUAL"
assert controls["BR163_04"]["difference_issuer_minus_raw"] == "0"
assert Decimal(controls["BR163_05"]["raw_sum_thousand_ars"]) == Decimal("5494064.165516943874708")
assert Decimal(controls["BR163_06"]["issuer_value_thousand_ars"]) == Decimal("5652853.165516943874708")
assert Decimal(controls["BR163_07"]["issuer_value_thousand_ars"]) == Decimal("0.108985205433436")
assert controls["BR163_08"]["issuer_value_thousand_ars"] == "0"
assert Decimal("29217148") - (Decimal("28978965") + Decimal("79394")) == Decimal("158789")
assert Decimal("14409056") - Decimal("14250267") == Decimal("158789")
assert Decimal("14409056") - Decimal("5712151") * FACTOR == Decimal("5652853.165516943874708")

dual = rows(HERE / "BANCO_RIOJA_DUAL_RESIDUAL_RECONCILIATION_V163.csv")
assert len(dual) == 3 and [row["control_id"] for row in dual] == ["BR163_02", "BR163_03", "BR163_04"]
raw = rows(HERE / "BANCO_RIOJA_RAW_ACCOUNT_EXTRACTION_V163.csv")
assert len(raw) == 8
raw_by_key = {(row["period"], row["account"]): row for row in raw}
assert raw_by_key[("2023-12", "141222")]["value_thousand_ars"] == "79394"
assert raw_by_key[("2023-12", "511108")]["value_thousand_ars"] == "14250267"
assert raw_by_key[("2023-09", "141222")]["value_thousand_ars"] == "43026"

correction = (HERE / "CORRECTION_LOG_V163.md").read_text(encoding="utf-8-sig")
assert "238.183" in correction and "158.789" in correction
assert "supersedidos" in correction and "no se reescribe retroactivamente" in correction
hypothesis = (HERE / "BANCO_RIOJA_ADJUSTING_ENTRY_HYPOTHESIS_V163.md").read_text(encoding="utf-8-sig")
assert "ni prueban el asiento" in hypothesis and "no se reexpresan" in hypothesis

scenarios = rows(HERE / "BANCO_RIOJA_Q4_SCENARIO_BOUND_V163.csv")
assert len(scenarios) == 3 and all(row["panel_use"] != "YES" for row in scenarios)
assert Decimal(scenarios[0]["q4_income_bcra_thousand_ars"]) == Decimal("5494064.165516943874708")
assert Decimal(scenarios[1]["q4_income_bcra_thousand_ars"]) == Decimal("5652853.165516943874708")
assert scenarios[1]["adjustment_thousand_ars"] == "158789"

panel = rows(HERE / "FOUR_LEG_PASS_PANEL_V163.csv")
assert sum(row["system_panel_eligible_v72"] == "YES_EXACT_Q4_TARGET_BASIS" for row in panel) == 33
for entity in ("Banco Rioja S.A.U.", "HSBC Bank Argentina S.A."):
    found = [row for row in panel if row["entity"] == entity]
    assert len(found) == 1 and found[0]["system_panel_eligible_v72"] == "NO"
rioja_panel = next(row for row in panel if row["entity"] == "Banco Rioja S.A.U.")
assert "158789K" in rioja_panel["quality"] and "238183" not in rioja_panel["v72_note"]

coverage = rows(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V163.csv")
assert len(coverage) == 1
assert Decimal(coverage[0]["asset_coverage_pct"]) == EXPECTED
assert Decimal(coverage[0]["asset_numerator_million_ars"]) == Decimal("61248719.753")

visual = rows(HERE / "V163_PDF_VISUAL_CONTROL.csv")
assert len(visual) == 6 and all(row["result"] in {"PASS", "PASS_LIMIT"} for row in visual)
assert any(row["page"] == "7" and row["artifact"].endswith("9m2024.pdf") and " 0" in row["observation"] for row in visual)
routes = rows(HERE / "BANCO_RIOJA_PUBLIC_ROUTE_EXHAUSTION_V163.csv")
assert len(routes) == 6
assert sum(row["result"] == "OFFICIAL_PDF_ARCHIVED" for row in routes) == 1
assert sum(row["result"] == "HTTP_404" for row in routes) == 1

catalog = rows(CATALOG)
assert len(catalog) == 579 and len({row["id"] for row in catalog}) == 579
rioja_dm = [row for row in catalog if row["id"] == "banco_rioja_disciplina_mercado_9m2024_v163"]
assert len(rioja_dm) == 1
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    assert path.is_file() and digest(path) == row["sha256"].lower()

master = rows(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V163.csv")
assert len(master) == 579 and all(row["exists"] == "True" and row["hash_ok"] == "True" for row in master)
assert not rows(AUDIT / "SOURCE_PRESERVATION_MISSING_V163.csv")
complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V163.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V163" and complete["exact_entities"] == 33
assert complete["master_catalog_entries"] == complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 579
assert Decimal(complete["rioja_counterfactual_coverage_pct"]) == COUNTERFACTUAL
assert complete["request_drafts_status"] == "DRAFT_NOT_SENT"

dm_path = REPO / rioja_dm[0]["archivo_local"].lstrip("/")
assert dm_path.read_bytes().startswith(b"%PDF-") and dm_path.stat().st_size == 351576
info = subprocess.run(["pdfinfo", str(dm_path)], capture_output=True, text=True, errors="replace")
assert info.returncode == 0 and "Pages:           9" in info.stdout

sync = rows(CYCLE / "inputs/source_sync/v163/SOURCE_SYNC_FILE_MANIFEST_V163.csv")
assert len(sync) == 1
for row in sync:
    path = REPO / row["relative_path"].lstrip("/")
    assert path.is_file() and digest(path) == row["sha256"]

register = rows(HERE / "E0_REQUEST_RESPONSE_REGISTER_V163.csv")
assert len(register) == 6 and all(row["status"] == "DRAFT_NOT_SENT" and row["submitted_on"] == "N/A" for row in register)
combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined

manifest = json.loads((HERE / "MANIFEST_V163.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V163" and manifest["parent_checkpoint"] == "V162"
assert manifest["exact_entities"] == 33 and manifest["new_promotions"] == []
assert "141222=79394" in manifest["correction"]
for item in manifest["files"]:
    path = HERE / item["path"]
    assert path.is_file() and path.stat().st_size == item["bytes"] and digest(path) == item["sha256"]

global_manifest = json.loads((CYCLE / "MANIFEST_SHA256.json").read_text(encoding="utf-8-sig"))
assert global_manifest["checkpoint"] == "V163" and global_manifest["exact_entities"] == 33
assert global_manifest["file_count_excluding_manifest"] == len(global_manifest["files"])

print("V163 QA PASS")
print(f"catalog=579 local=579 hash_ok=579 exact_entities=33 coverage={EXPECTED}")
print("rioja_dec_141222=79394 dual_residual=158789 adjustment=UNAUTHENTICATED promotions=0 requests=0")
