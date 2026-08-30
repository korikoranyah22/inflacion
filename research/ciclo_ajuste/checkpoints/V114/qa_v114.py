from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import csv
import hashlib
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v114" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"
CENT = Decimal("0.01")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


source_ids = {
    "e0_argentina_recompras_decreto_1735_04_report",
    "e0_argentina_recompra_primera_etapa_2008_08_11",
    "e0_argentina_recompra_segunda_etapa_2008_08_21",
    "e0_argentina_recompra_segunda_semana_2008_08_22",
    "e0_argentina_resultado_recompra_2008_10_02",
    "e0_bna_memoria_balance_2008",
    "e0_cgn_cuenta_inversion_2008_comentarios",
    "e0_cgn_cuenta_inversion_2009_anexo_j_html",
    "e0_argentina_mecon_memoria_2009",
    "e0_agn_res_084_2015_act_158_2010_deuda",
    "e0_agn_transparencia_boden_2018",
    "sec_consejo_iec_298_strip_boden2012",
}
primary_ids = source_ids - {"sec_consejo_iec_298_strip_boden2012"}


catalog = read_csv(REPO / "data" / "fuentes" / "FUENTES.csv")
assert len(catalog) == 264, len(catalog)
assert len({row["id"] for row in catalog}) == len(catalog)
catalog_by_id = {row["id"]: row for row in catalog}
assert source_ids <= catalog_by_id.keys()


census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V114.csv")
assert len(census) == 65, len(census)
assert len({row["source_id"] for row in census}) == len(census)
assert primary_ids <= {row["source_id"] for row in census}
assert "sec_consejo_iec_298_strip_boden2012" not in {row["source_id"] for row in census}
for source_id in source_ids:
    row = catalog_by_id[source_id]
    local = REPO / row["archivo_local"].lstrip("/")
    assert local.is_file(), local
    assert digest(local) == row["sha256"]
for row in census:
    if row["source_id"] in primary_ids:
        assert row["primary_source"] == "YES" and row["preserved"] == "YES"
        assert digest(REPO / row["local_path"].lstrip("/")) == row["sha256"]


pdfs = sorted(BIN.glob("*.pdf"))
htmls = sorted(BIN.glob("*.html"))
assert len(pdfs) == 9 and len(htmls) == 3, (len(pdfs), len(htmls))
for pdf in pdfs:
    assert pdf.read_bytes().startswith(b"%PDF"), pdf
for html in htmls:
    data = html.read_bytes()
    assert len(data) > 40000, html
assert (BIN / "bna_memoria_balance_2008.pdf").stat().st_size > 17_000_000
assert b"Boden 2006, 2012 y 2013" in (BIN / "agn_transparencia_informacion_publica_2018.html").read_bytes()


legacy_tenders = read_csv(HERE / "E0_FISCAL_BODEN_BUYBACK_TENDERS_2008_V114.csv")
legacy_awards = read_csv(HERE / "E0_FISCAL_BODEN_BUYBACK_AWARDS_2008_V114.csv")
assert len(legacy_tenders) == 3 and len(legacy_awards) == 3
assert sum(Decimal(row["awarded_vno_usd"]) for row in legacy_awards) == Decimal("17193000")
assert sum(Decimal(row["awarded_effective_usd"]) for row in legacy_awards) == Decimal("6559535.00")


tenders = read_csv(HERE / "E0_FISCAL_PUBLIC_BUYBACK_TENDERS_2008_V114.csv")
awards = read_csv(HERE / "E0_FISCAL_PUBLIC_BUYBACK_AWARDS_2008_V114.csv")
assert len(tenders) == 14 and len(awards) == 18
assert len({row["tender_id"] for row in tenders}) == len(tenders)
assert len({row["award_id"] for row in awards}) == len(awards)
assert {row["tender_date"] for row in tenders} == {"2008-08-28", "2008-09-04", "2008-09-11", "2008-10-02"}


def component_value(components: str) -> tuple[Decimal, Decimal]:
    notional = Decimal(0)
    effective = Decimal(0)
    for component in components.split(";"):
        vno, price = component.split("@")
        notional += Decimal(vno)
        effective += Decimal(vno) * Decimal(price) / Decimal(100)
    return notional, effective


for row in awards:
    notional, effective = component_value(row["price_components"])
    assert notional == Decimal(row["awarded_notional_native"])
    assert effective == Decimal(row["awarded_effective_native"])
    expected_ars = effective if row["native_currency"] == "ARS" else effective * Decimal(row["reference_fx_ars_per_usd"])
    assert expected_ars == Decimal(row["awarded_effective_ars_raw"])
    assert row["ultimate_holder_identified"] == "NO"
    assert row["original_purpose_identified"] == "NO"
    assert row["settlement_confirmation"] == "SCHEDULED_NOT_INDEPENDENTLY_CONFIRMED"


by_group: dict[tuple[str, str], list[dict[str, str]]] = {}
for row in awards:
    by_group.setdefault((row["tender_date"], row["instrument"]), []).append(row)
for tender in (row for row in tenders if row["result_status"] == "ADJUDICADA"):
    rows = by_group[(tender["tender_date"], tender["instrument"])]
    assert sum(Decimal(row["awarded_notional_native"]) for row in rows) == Decimal(tender["awarded_notional_native"])
    assert sum(Decimal(row["awarded_effective_native"]) for row in rows).quantize(CENT, ROUND_HALF_UP) == Decimal(tender["awarded_effective_native"])
    assert sum(Decimal(row["awarded_effective_ars_raw"]) for row in rows).quantize(CENT, ROUND_HALF_UP) == Decimal(tender["awarded_effective_ars"])


official_ars = sum(Decimal(row["awarded_effective_ars"]) for row in tenders)
raw_ars = sum(Decimal(row["awarded_effective_ars_raw"]) for row in awards)
assert official_ars == Decimal("135606214.86")
assert raw_ars == Decimal("135606214.85506")
assert raw_ars.quantize(CENT, ROUND_HALF_UP) == official_ars


instrument_vno = {}
for row in awards:
    instrument_vno.setdefault(row["instrument"], Decimal(0))
    instrument_vno[row["instrument"]] += Decimal(row["awarded_notional_native"])
assert instrument_vno == {
    "BODEN_2012": Decimal("17193000"),
    "BODEN_2013": Decimal("13148000"),
    "GDP_UNIT_ARS": Decimal("1045342050"),
    "GDP_UNIT_USD_LAW_AR": Decimal("29480362"),
}


def participant_vno(instrument: str, participant: str) -> Decimal:
    return sum(Decimal(row["awarded_notional_native"]) for row in awards if row["instrument"] == instrument and row["participant"] == participant)


assert participant_vno("BODEN_2012", "Citibank") == Decimal("14193000")
assert participant_vno("BODEN_2012", "Standard Bank") == Decimal("3000000")
assert participant_vno("BODEN_2013", "Citibank") == Decimal("9000000")
assert participant_vno("BODEN_2013", "MERVAL") == Decimal("1148000")
assert participant_vno("BODEN_2013", "Banco Mariva") == Decimal("3000000")
assert participant_vno("GDP_UNIT_ARS", "Citibank") == Decimal("790066472")
assert participant_vno("GDP_UNIT_ARS", "HSBC Bank") == Decimal("250275578")
assert participant_vno("GDP_UNIT_ARS", "MERVAL") == Decimal("5000000")
assert participant_vno("GDP_UNIT_USD_LAW_AR", "Citibank") == Decimal("8280362")
assert participant_vno("GDP_UNIT_USD_LAW_AR", "Standard Bank") == Decimal("21200000")


events = read_csv(HERE / "E0_FISCAL_BUYBACK_PROGRAM_EVENTS_2005_2009_V114.csv")
assert len(events) == 8
event_by_id = {row["event_id"]: row for row in events}
assert event_by_id["E20080822_FIRST_TWO_WEEKS"]["reported_amount"] == "380000000"
assert event_by_id["E2008_CGN_BUYBACK_AGGREGATE"]["reported_amount"] == "981360000"
assert event_by_id["E2009_STRIP_OFFICIAL"]["status"] == "TENDER_OCCURRED_PRIMARY_AMOUNT_OPEN"
assert event_by_id["E2009_STRIP_SECONDARY_RESULT"]["source_id"] == "sec_consejo_iec_298_strip_boden2012"


creditors = read_csv(HERE / "E0_FISCAL_AGN_CREDITOR_DISTRIBUTION_V114.csv")
assert len(creditors) == 15
assert all(row["instrument_specific"] == "NO" for row in creditors)
assert next(row for row in creditors if row["observation_date"] == "2008-12-31" and row["creditor_sector"] == "PRIVATE_SECTOR")["share_total_pct"] == "54.8"
assert next(row for row in creditors if row["observation_date"] == "2012-12-31" and row["creditor_sector"] == "PUBLIC_SECTOR")["share_total_pct"] == "56.5"


report_index = read_csv(HERE / "E0_FISCAL_AGN_REPORT_INDEX_V114.csv")
assert len(report_index) == 4
assert report_index[0]["match_status"] == "ROUTE_CONFIRMED_IDENTIFIERS_OMITTED"
assert all("NOT_PROVEN" in row["match_status"] for row in report_index[1:3])


ledger = read_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V114.csv")
assert len(ledger) == 108, len(ledger)
assert len({row["ledger_id"] for row in ledger}) == len(ledger)
assert {f"F{i}" for i in range(96, 109)} <= {row["ledger_id"] for row in ledger}
assert all(row["realization_status"] != "CASH_SETTLED" for row in ledger if row["ledger_id"] in {f"F{i}" for i in range(96, 109)})
assert next(row for row in ledger if row["ledger_id"] == "F104")["additivity"] == "CONTROL_NOT_ADDITIVE"


breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V114.csv")
assert len(breaks) == 51, len(breaks)
assert len({row["break_id"] for row in breaks}) == len(breaks)
assert {
    "mixed_buyback_program_not_instrument",
    "budget_execution_aggregate_not_instrument_flow",
    "bna_mandate_not_trade_blotter",
    "secondary_result_not_primary_settlement",
    "creditor_sector_not_instrument_holder",
    "program_aggregate_overlap",
    "official_purchase_language_not_post_settlement_confirmation",
} <= {row["break_id"] for row in breaks}


matrix = read_csv(HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V114.csv")
assert any(row["variable"] == "four_located_public_buyback_tenders" and row["status"] == "FOUR_PUBLIC_RESULTS_PARTICIPANTS_RECONSTRUCTED" for row in matrix)
assert any(row["variable"] == "bna_first_stage_mixed_buybacks" and row["status"] == "FIRST_STAGE_AGGREGATE_BLOTTER_OPEN" for row in matrix)
strip = next(row for row in matrix if row["variable"] == "boden_2012_strip_and_residual_registration")
assert strip["status"] == "STRIP_RESULT_QUANTITATIVE_SECONDARY_PRIMARY_OPEN"


evidence = read_csv(HERE / "HISTORICAL_EVIDENCE_COVERAGE_V114.csv")
state = next(row for row in evidence if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra")
assert state["quality"] == "PRIMARY_BUYBACK_PROGRAM_PARTICIPANTS_EXTENDED_2001_2012"
assert "Caja/BCRA" in state["gap"] and "CRYL" in state["gap"]


current = read_csv(HERE / "CURRENT_STATE_V114.csv")
assert len(current) == 39
assert sum(row["strict_panel_status"] == "ELIGIBLE" for row in current) == 30
coverage = read_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V114.csv")
assert STRICT in " ".join(" ".join(row.values()) for row in coverage)


completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V114.json").read_text(encoding="utf-8"))
assert completeness["checkpoint"] == "V114"
assert completeness["master_catalog_entries"] == 264
assert completeness["physical_local_copies"] == completeness["physical_local_hash_ok"] == 259
assert completeness["e0_primary_sources_preserved"] == 65
assert completeness["sources_newly_preserved_v114"] == 12
assert completeness["e0_primary_sources_newly_preserved_v114"] == 11
assert completeness["e0_four_located_public_tender_effective_ars"] == "135606214.86"
assert completeness["e0_four_located_public_tender_effective_ars_raw"] == "135606214.855060"
assert completeness["e0_strip_primary_quantitative_result_preserved"] is False
assert completeness["e0_strip_secondary_quantitative_result_preserved"] is True
assert completeness["e0_agn_boden_report_identifiers_definitively_resolved"] is False
assert completeness["e0_ultimate_holders_identified"] is False
assert completeness["e0_settlement_confirmations_preserved"] is False
assert completeness["strict_coverage_pct"] == STRICT
assert completeness["closed_network_gate"] == "NO"


inherited = read_csv(HERE / "INHERITED_QA_STATUS_V114.csv")
assert next(row for row in inherited if row["script"] == "qa_v113.py")["post_v114_result"] == "EXPECTED_SUPERSEDED_ASSERTION"
assert next(row for row in inherited if row["script"] == "qa_v114.py")["post_v114_result"] == "PASS"


manifest = json.loads((HERE / "MANIFEST_V114.json").read_text(encoding="utf-8"))
assert manifest["checkpoint"] == "V114" and manifest["parent_checkpoint"] == "V113"
assert manifest["e0_primary_sources"] == 65 and manifest["new_preserved_sources"] == 12
assert manifest["public_tender_instrument_date_rows"] == 14 and manifest["public_tender_award_rows"] == 18
assert manifest["four_located_public_tender_effective_ars"] == "135606214.86"
for item in manifest["files"]:
    path = HERE / item["path"]
    assert path.stat().st_size == item["bytes"]
    assert digest(path) == item["sha256"]


global_manifest = json.loads((CYCLE / "MANIFEST_SHA256.json").read_text(encoding="utf-8"))
assert global_manifest["checkpoint"] == "V114"
assert global_manifest["exact_entities"] == 30
assert global_manifest["strict_coverage_pct"] == STRICT
assert global_manifest["closed_network_gate"] == "NO"

print("V114 QA PASS")
