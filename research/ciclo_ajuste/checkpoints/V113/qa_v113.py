from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import csv
import hashlib
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v113" / "binaries"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


strict = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"

source_ids = {
    "e0_argentina_resultado_recompra_2008_08_28",
    "e0_argentina_resultado_recompra_2008_09_04",
    "e0_argentina_resultado_recompra_2008_09_11",
    "e0_argentina_rc_212_24_2008_recompra",
    "e0_argentina_rc_113_34_2009_boden12_strip",
    "e0_argentina_dnu_1801_2009_boden12",
}

catalog = read_csv(REPO / "data" / "fuentes" / "FUENTES.csv")
assert len(catalog) == 252, len(catalog)
assert len({row["id"] for row in catalog}) == len(catalog)
catalog_by_id = {row["id"]: row for row in catalog}
assert source_ids <= catalog_by_id.keys()

census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V113.csv")
assert len(census) == 54, len(census)
assert len({row["source_id"] for row in census}) == len(census)
for row in census:
    if row["source_id"] in source_ids:
        local = REPO / row["local_path"].lstrip("/")
        assert local.is_file(), local
        assert digest(local) == row["sha256"] == catalog_by_id[row["source_id"]]["sha256"]
        assert row["primary_source"] == "YES" and row["preserved"] == "YES"

pdfs = sorted(BIN.glob("*.pdf"))
htmls = sorted(BIN.glob("*.html"))
assert len(pdfs) == 3 and len(htmls) == 3
for pdf in pdfs:
    assert pdf.read_bytes().startswith(b"%PDF"), pdf
for html in htmls:
    text = html.read_text(encoding="utf-8", errors="replace")
    assert "argentina.gob.ar" in text and len(text) > 30000, html

tenders = read_csv(HERE / "E0_FISCAL_BODEN_BUYBACK_TENDERS_2008_V113.csv")
awards = read_csv(HERE / "E0_FISCAL_BODEN_BUYBACK_AWARDS_2008_V113.csv")
chain = read_csv(HERE / "E0_FISCAL_BUYBACK_SETTLEMENT_CHAIN_V113.csv")
assert len(tenders) == 3 and len(awards) == 3 and len(chain) == 7
assert tenders[0]["result_status"] == "DESIERTA"
assert Decimal(tenders[0]["awarded_vno_usd"]) == 0


def component_value(components: str) -> Decimal:
    total = Decimal(0)
    for component in components.split(";"):
        vno, price = component.split("@")
        total += Decimal(vno) * Decimal(price) / Decimal(100)
    return total


for row in awards:
    assert component_value(row["price_components"]) == Decimal(row["awarded_effective_usd"])
    assert Decimal(row["awarded_effective_usd"]) * Decimal(row["reference_fx_ars_per_usd"]) == Decimal(row["awarded_effective_ars"])
    assert row["ultimate_holder_identified"] == "NO"
    assert row["original_purpose_identified"] == "NO"
    assert row["settlement_confirmation"] == "SCHEDULED_NOT_INDEPENDENTLY_CONFIRMED"

by_date: dict[str, list[dict[str, str]]] = {}
for row in awards:
    by_date.setdefault(row["tender_date"], []).append(row)
for tender in tenders[1:]:
    rows = by_date[tender["tender_date"]]
    assert sum(Decimal(row["awarded_vno_usd"]) for row in rows) == Decimal(tender["awarded_vno_usd"])
    assert sum(Decimal(row["awarded_effective_usd"]) for row in rows) == Decimal(tender["awarded_effective_usd"])
    assert sum(Decimal(row["awarded_effective_ars"]) for row in rows).quantize(Decimal("0.01")) == Decimal(tender["awarded_effective_ars"])

total_vno = sum(Decimal(row["awarded_vno_usd"]) for row in awards)
total_usd = sum(Decimal(row["awarded_effective_usd"]) for row in awards)
total_ars = sum(Decimal(row["awarded_effective_ars"]) for row in awards)
assert total_vno == Decimal("17193000")
assert total_usd == Decimal("6559535.00")
assert total_ars == Decimal("20088405.7570")
assert sum(Decimal(row["awarded_effective_ars"]) for row in tenders if row["result_status"] == "ADJUDICADA") == Decimal("20088405.76")
assert sum(Decimal(row["awarded_vno_usd"]) for row in awards if row["participant"] == "Citibank") == Decimal("14193000")
assert sum(Decimal(row["awarded_vno_usd"]) for row in awards if row["participant"] == "Standard Bank") == Decimal("3000000")
assert chain[-1]["account_or_system"] == "Participant current accounts at BCRA"
assert all("NORMATIVE" in row["evidence_status"] or "OPEN" in row["evidence_status"] for row in chain)

ledger = read_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V113.csv")
assert len(ledger) == 95, len(ledger)
assert len({row["ledger_id"] for row in ledger}) == len(ledger)
assert {f"F{i}" for i in range(89, 96)} <= {row["ledger_id"] for row in ledger}
assert all(row["realization_status"] != "CASH_SETTLED" for row in ledger if row["ledger_id"] in {"F91", "F92", "F93"})

breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V113.csv")
assert len(breaks) == 44, len(breaks)
assert len({row["break_id"] for row in breaks}) == len(breaks)
assert {"participant_not_ultimate_holder", "award_not_settlement", "offer_not_award"} <= {row["break_id"] for row in breaks}

matrix = read_csv(HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V113.csv")
assert any(row["variable"] == "boden_2012_public_buyback_tenders" and row["status"] == "PUBLIC_AWARDS_COUNTERPARTY_PARTIAL" for row in matrix)
evidence = read_csv(HERE / "HISTORICAL_EVIDENCE_COVERAGE_V113.csv")
state = next(row for row in evidence if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra")
assert state["quality"] == "PRIMARY_BUYBACK_COUNTERPARTIES_PARTIAL_2001_2012"
assert "ultimate holders" in state["gap"]

current = read_csv(HERE / "CURRENT_STATE_V113.csv")
assert len(current) == 39
assert sum(row["strict_panel_status"] == "ELIGIBLE" for row in current) == 30
coverage = read_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V113.csv")
joined = " ".join(" ".join(row.values()) for row in coverage)
assert strict in joined

completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V113.json").read_text(encoding="utf-8"))
assert completeness["checkpoint"] == "V113"
assert completeness["master_catalog_entries"] == 252
assert completeness["physical_local_copies"] == completeness["physical_local_hash_ok"] == 247
assert completeness["e0_primary_sources_preserved"] == 54
assert completeness["e0_public_boden2012_awarded_vno_usd"] == "17193000"
assert completeness["e0_public_boden2012_awarded_effective_ars"] == "20088405.76"
assert completeness["e0_ultimate_holders_identified"] is False
assert completeness["e0_settlement_confirmations_preserved"] is False
assert completeness["strict_coverage_pct"] == strict
assert completeness["closed_network_gate"] == "NO"

inherited = read_csv(HERE / "INHERITED_QA_STATUS_V113.csv")
old_current = next(row for row in inherited if row["script"] == "qa_v112.py")
assert old_current["post_v113_result"] == "EXPECTED_SUPERSEDED_ASSERTION"
assert next(row for row in inherited if row["script"] == "qa_v113.py")["post_v113_result"] == "PASS"

manifest = json.loads((HERE / "MANIFEST_V113.json").read_text(encoding="utf-8"))
assert manifest["checkpoint"] == "V113" and manifest["parent_checkpoint"] == "V112"
assert manifest["e0_primary_sources"] == 54 and manifest["new_official_sources"] == 6
assert manifest["public_boden2012_awarded_vno_usd"] == "17193000"
for item in manifest["files"]:
    path = HERE / item["path"]
    assert path.stat().st_size == item["bytes"]
    assert digest(path) == item["sha256"]

global_manifest = json.loads((CYCLE / "MANIFEST_SHA256.json").read_text(encoding="utf-8"))
assert global_manifest["checkpoint"] == "V113"
assert global_manifest["exact_entities"] == 30
assert global_manifest["strict_coverage_pct"] == strict
assert global_manifest["closed_network_gate"] == "NO"

print("V113 QA PASS")
