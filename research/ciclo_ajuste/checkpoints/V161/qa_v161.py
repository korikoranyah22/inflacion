from decimal import Decimal, getcontext
from pathlib import Path
import csv
import hashlib
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
getcontext().prec = 120
EXPECTED_COVERAGE = Decimal("63.3404130639287055191506606276878645985932518939916205138518528603403997357930830936917209159343409585184995437662731063")
FACTOR = Decimal("1.532908152197492")


def rows(name):
    with (HERE / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


state = rows("CURRENT_STATE_V161.csv")
by_entity = {row["entity"]: row for row in state}
promoted = {
    "Banco BMA S.A.U. (antes Banco Itaú Argentina S.A.)",
    "Banco Mariva S.A.",
    "Banco de Corrientes S.A.",
}
assert promoted <= set(by_entity)
for entity in promoted:
    row = by_entity[entity]
    assert row["q4_four_leg_status"] == "EXACT"
    assert row["strict_panel_status"] == "ELIGIBLE"
    assert row["priority"] == "CLOSED_V161"
assert by_entity["HSBC Bank Argentina S.A."]["q4_four_leg_status"] == "N/D_STRICT"
assert by_entity["HSBC Bank Argentina S.A."]["strict_panel_status"] == "PENDING"
assert sum(row["q4_four_leg_status"] == "EXACT" for row in state) == 33
assert sum(row["strict_panel_status"] == "ELIGIBLE" for row in state) == 33


expected_promotions = {
    "BMA_Q4_FOUR_LEG_PROMOTION_V161.csv": (
        Decimal("35209590.954531658679876"),
        Decimal("0"),
        Decimal("70273.326348214771540"),
        Decimal("5741782.969369604148776"),
    ),
    "MARIVA_Q4_FOUR_LEG_PROMOTION_V161.csv": (
        Decimal("0"),
        Decimal("0"),
        Decimal("9961441.940170943606396"),
        Decimal("871.839125341665972"),
    ),
    "CORRIENTES_Q4_FOUR_LEG_PROMOTION_V161.csv": (
        Decimal("14858818.603366745496452"),
        Decimal("0"),
        Decimal("0"),
        Decimal("0"),
    ),
}
for name, expected in expected_promotions.items():
    data = rows(name)
    assert len(data) == 3 and [row["period"] for row in data] == ["9M-2023", "FY-2023", "Q4-2023"]
    q4 = data[-1]
    actual = tuple(Decimal(q4[key]) for key in ["income_bcra", "expense_bcra", "income_otherfi", "expense_otherfi"])
    assert actual == expected
    nine_month, fy = data[0], data[1]
    for key in ["income_bcra", "expense_bcra", "income_otherfi", "expense_otherfi"]:
        assert Decimal(q4[key]) == Decimal(fy[key]) - Decimal(nine_month[key]) * FACTOR


assert len(rows("BMA_ENTITY_SPECIFIC_CROSSWALK_V161.csv")) == 8
assert len(rows("MARIVA_ENTITY_SPECIFIC_CROSSWALK_V161.csv")) == 6
assert len(rows("CORRIENTES_ENTITY_SPECIFIC_CROSSWALK_V161.csv")) == 4
all_cross = rows("BMA_ENTITY_SPECIFIC_CROSSWALK_V161.csv") + rows("MARIVA_ENTITY_SPECIFIC_CROSSWALK_V161.csv") + rows("CORRIENTES_ENTITY_SPECIFIC_CROSSWALK_V161.csv")
assert all("only" in row["scope_limit"].lower() or "not a universal" in row["scope_limit"].lower() for row in all_cross)


hsbc = rows("HSBC_COUNTERPARTY_SPLIT_LIMIT_V161.csv")
assert len(hsbc) == 3 and all(row["four_leg_status"] == "N/D_STRICT" for row in hsbc)
assert Decimal(hsbc[-1]["pass_income_total_thousand_ars"]) == Decimal("99749193.003601044382524")
assert Decimal(hsbc[-1]["pass_expense_total_thousand_ars"]) == Decimal("281966.781725888375636")


panel = rows("FOUR_LEG_PASS_PANEL_V161.csv")
for entity in promoted:
    matches = [row for row in panel if row["entity"] == entity and row["period"] == "Q4-2023"]
    assert len(matches) == 1 and matches[0]["system_panel_eligible_v72"] == "YES_EXACT_Q4_TARGET_BASIS"
hsbc_panel = [row for row in panel if row["entity"] == "HSBC Bank Argentina S.A."]
assert len(hsbc_panel) == 1 and hsbc_panel[0]["system_panel_eligible_v72"] == "NO"


coverage = rows("STRICT_Q4_FOUR_LEG_COVERAGE_V161.csv")
assert len(coverage) == 1
assert Decimal(coverage[0]["asset_numerator_million_ars"]) == Decimal("61248719.753")
assert Decimal(coverage[0]["system_assets_million_ars"]) == Decimal("96697695.5")
assert Decimal(coverage[0]["asset_coverage_pct"]) == EXPECTED_COVERAGE
assert coverage[0]["quality"] == "ALL_FOUR_LEGS_EXACT_THIRTY_THREE_ENTITIES"


review = rows("CNV_ATTACHMENT_ANALYTIC_REVIEW_V161.csv")
assert len(review) == 4
assert {row["q4_decision"] for row in review} == {"PROMOTE_EXACT", "PROMOTE_EXACT_ENTITY_SPECIFIC", "KEEP_ND_STRICT"}
visual = rows("V161_PDF_VISUAL_AND_TEXT_CONTROL.csv")
assert len(visual) == 11
assert sum(row["method"].startswith("Poppler") for row in visual) == 9
assert {row["result"] for row in visual} == {"PASS", "PASS_LIMIT", "ABSENT_CONFIRMED"}


bundle = rows("V161_BANK_ANALYTIC_SOURCE_BUNDLE.csv")
assert len(bundle) == 9
for row in bundle:
    path = REPO / row["path"].lstrip("/")
    assert path.is_file()
    assert path.stat().st_size == int(row["bytes"])
    assert digest(path) == row["sha256"]


with (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V161.csv").open(encoding="utf-8-sig", newline="") as handle:
    master = list(csv.DictReader(handle))
assert len(master) == 577
assert sum(row["exists"] == "True" for row in master) == 577
assert sum(row["hash_ok"] == "True" for row in master) == 577
complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V161.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V161" and complete["exact_entities"] == 33
assert Decimal(complete["strict_coverage_pct"]) == EXPECTED_COVERAGE
assert complete["request_drafts_status"] == "DRAFT_NOT_SENT"
assert complete["requests_submitted"] == complete["responses_received"] == 0


register = rows("E0_REQUEST_RESPONSE_REGISTER_V161.csv")
assert len(register) == 6
assert all(row["status"] == "DRAFT_NOT_SENT" and row["submitted_on"] == "N/A" for row in register)
assert all("V161.md" in row["draft_file"] for row in register)


manifest = json.loads((HERE / "MANIFEST_V161.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V161" and manifest["parent_checkpoint"] == "V160"
assert manifest["exact_entities"] == 33
assert Decimal(manifest["strict_coverage_pct"]) == EXPECTED_COVERAGE
assert manifest["source_archive"] == "577/577 physical SHA-valid"
assert manifest["requests_submitted"] == 0
for item in manifest["files"]:
    path = HERE / item["path"]
    assert path.is_file() and path.stat().st_size == item["bytes"] and digest(path) == item["sha256"]


for name in [
    "README_V161.md",
    "VEREDICTO_V161.md",
    "AUDITORIA_V161.md",
    "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V161_A_V162.md",
    "CNV_ATTACHMENT_ANALYTIC_REVIEW_V161.md",
    "HSBC_COUNTERPARTY_SPLIT_LIMIT_V161.md",
]:
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "HSBC" in text or name == "AUDITORIA_V161.md"
combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined

print("V161 QA PASS")
