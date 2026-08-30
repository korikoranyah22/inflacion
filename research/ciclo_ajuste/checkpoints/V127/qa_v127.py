from __future__ import annotations

from decimal import Decimal, getcontext
from pathlib import Path
import csv
import hashlib
import json
import zipfile


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"
SIGADE_ID = "e0_argentina_sigade_2008_q3"
SIGADE_SHA = "aa5aa1ebe852c91c1bdaa63be2324a8c7b9a8aded9c5653a46b19b056bfd851a"
SIGADE_MEMBER = "2003-Para el Sitio basesigade 2008-09-30.mdb"

getcontext().prec = 50


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def by(rows: list[dict[str, str]], field: str, value: str) -> dict[str, str]:
    return next(row for row in rows if row[field] == value)


# Catálogo, preservación y fuente SIGADE nueva.
catalog = read_csv(REPO / "data" / "fuentes" / "FUENTES.csv")
assert len(catalog) == 303 and len({row["id"] for row in catalog}) == 303
sigade_catalog = by(catalog, "id", SIGADE_ID)
sigade_zip = REPO / sigade_catalog["archivo_local"].lstrip("/")
assert sigade_zip.is_file() and sigade_zip.stat().st_size == 6_172_758
assert digest(sigade_zip) == sigade_catalog["sha256"] == SIGADE_SHA
with zipfile.ZipFile(sigade_zip) as archive:
    members = archive.infolist()
    assert len(members) == 1
    assert members[0].filename == SIGADE_MEMBER and members[0].file_size == 57_245_696
assert list(sigade_zip.parent.iterdir()) == [sigade_zip]

census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V127.csv")
assert len(census) == 104 and len({row["source_id"] for row in census}) == 104
sigade_census = by(census, "source_id", SIGADE_ID)
assert sigade_census["primary_source"] == sigade_census["preserved"] == "YES"
assert sigade_census["sha256"] == SIGADE_SHA and sigade_census["bytes"] == "6172758"

hash_rows = read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V127.csv")
assert len(hash_rows) == 303 and len({row["id"] for row in hash_rows}) == 303
assert sum(row["exists"] == "True" for row in hash_rows) == 298
assert sum(row["hash_ok"] == "True" for row in hash_rows) == 298
assert by(hash_rows, "id", SIGADE_ID)["hash_ok"] == "True"
assert len(read_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V127.csv")) == 303


# Puente de stock nominal Q3→Q4: sólo Discount en Pesos tiene una baja nativa.
stock = read_csv(HERE / "E0_FISCAL_Q4_EXCHANGE_BOND_STOCK_MOVEMENTS_V127.csv")
assert len(stock) == 3 and len({row["movement_id"] for row in stock}) == 3
for row in stock:
    q3_native = Decimal(row["q3_nominal_residual_thousand_usd"]) * Decimal(row["q3_fx_ars_per_usd"]) / 1000
    q4_native = Decimal(row["q4_nominal_residual_thousand_usd"]) * Decimal(row["q4_fx_ars_per_usd"]) / 1000
    assert q3_native == Decimal(row["q3_nominal_residual_million_ars"])
    assert q4_native == Decimal(row["q4_nominal_residual_million_ars"])
    assert q3_native - q4_native == Decimal(row["derived_nominal_reduction_million_ars"])

par = by(stock, "movement_id", "SM127_PAR_EN_PESOS")
discount = by(stock, "movement_id", "SM127_DISCOUNT_EN_PESOS")
cuasipar = by(stock, "movement_id", "SM127_CUASIPAR_EN_PESOS")
assert abs(Decimal(par["derived_nominal_reduction_million_ars"])) < Decimal("1e-9")
assert abs(Decimal(cuasipar["derived_nominal_reduction_million_ars"])) < Decimal("1e-9")
assert Decimal(discount["derived_nominal_reduction_million_ars"]) == Decimal("2748.4782690000057042")
assert Decimal(discount["report_vno_repurchase_million_ars"]) == Decimal("2748.50")
assert abs(Decimal(discount["delta_to_report_million_ars"])) < Decimal("0.03")
assert discount["isin"] == "ARARGE03E121"


# VNO, valor efectivo y reducción contable son magnitudes separadas y conciliadas.
valuation = read_csv(HERE / "E0_FISCAL_Q4_DISCOUNT_PESOS_VALUATION_BRIDGE_V127.csv")
assert len(valuation) == 3 and len({row["bridge_id"] for row in valuation}) == 3
assert abs(Decimal(by(valuation, "bridge_id", "VB127_VNO_REPORT")["result"])) < Decimal("0.03")
assert abs(Decimal(by(valuation, "bridge_id", "VB127_ACCOUNTING_ARS")["result"])) < Decimal("0.02")
assert abs(Decimal(by(valuation, "bridge_id", "VB127_ACCOUNTING_USD")["result"])) < Decimal("0.005")
assert Decimal("4723536.19") / Decimal("3.135") - Decimal("1506710.11") == Decimal(
    by(valuation, "bridge_id", "VB127_ACCOUNTING_USD")["result"]
)
assert (Decimal("4723536.19") / Decimal("3.135")).quantize(Decimal("0.01")) == Decimal("1506710.11")

report = read_csv(HERE / "E0_FISCAL_EXCESS_GROWTH_BUYBACK_REFERENCE_2006_V127.csv")
assert len(report) == 4 and len({row["row_id"] for row in report}) == 4
components = [row for row in report if row["additivity"] == "COMPONENT" or row["additivity"].startswith("COMPONENT_")]
assert sum(Decimal(row["effective_value_million_ars"]) for row in components) == Decimal("3301.60")
discount_report = by(report, "row_id", "EG127_03")
assert discount_report["isin"] == "ARARGE03E121"
assert Decimal(discount_report["vno_original_million_native"]) == Decimal("2748.50")
assert Decimal(discount_report["effective_value_million_ars"]) == Decimal("1415.50")

sigade = read_csv(HERE / "E0_SIGADE_Q3_EXCHANGE_BOND_EXTRACT_V127.csv")
assert len(sigade) == 4 and len({row["record_id"] for row in sigade}) == 4
sigade_discount = by(sigade, "record_id", "SG127_DISCOUNT_ARS")
assert Decimal(sigade_discount["balance_loan_currency"]) == Decimal("11803648176.77")
assert Decimal(sigade_discount["balance_usd"]) == Decimal("8229799942.95")
assert Decimal(by(sigade, "record_id", "SG127_FX_ARS")["exchange_rate"]) == Decimal("3.135")
assert abs(Decimal(sigade_discount["balance_usd"]) / 1000 - Decimal("8229799.94")) == Decimal("0.00295")


# Integración fiscal, quiebres metodológicos e identificadores.
accounting = read_csv(HERE / "E0_FISCAL_BUYBACK_DEBT_ACCOUNTING_BRIDGE_2008_V127.csv")
assert len(accounting) == 4 and len({row["bridge_id"] for row in accounting}) == 4
q3 = by(accounting, "bridge_id", "AB127_Q3_BODEN")
q4 = by(accounting, "bridge_id", "AB127_Q4_CANJE")
annual = by(accounting, "bridge_id", "AB127_2008_TOTAL")
assert Decimal(q3["official_amount_thousand_usd"]) + Decimal(q4["official_amount_thousand_usd"]) == Decimal(
    annual["official_amount_thousand_usd"]
) == Decimal("1523524.11")
assert q4["evidence_status"] == "EXACT_CROSS_SOURCE_ALLOCATION_TO_DISCOUNT_PESOS_REFERENCE_2006_AGGREGATE"
assert "No prueba cada operación" in q4["caveat"]

ledger = read_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V127.csv")
assert len(ledger) == 131 and len({row["ledger_id"] for row in ledger}) == 131
f127, f130, f131 = (by(ledger, "ledger_id", value) for value in ("F127", "F130", "F131"))
assert f127["instrument"] == f130["instrument"] == f131["instrument"] == "Discount_en_pesos_5.83_2033_ARARGE03E121"
assert Decimal(f127["amount_original"]) == Decimal("1506.71011")
assert Decimal(f127["normalized_ars_million"]) == Decimal("4723.53619")
assert Decimal(f130["amount_original"]) == Decimal("2748.50")
assert Decimal(f131["amount_original"]) == Decimal("1415.50")
assert not any(row["realization_status"] == "CASH_SETTLED" for row in (f127, f130, f131))

breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V127.csv")
assert len(breaks) == 96 and len({row["break_id"] for row in breaks}) == 96
assert by(breaks, "break_id", "q4_exchange_bond_aggregate_not_target_tenders")["status"].startswith("SUPERSEDED_BY_V127")
assert by(breaks, "break_id", "q4_instrument_allocation_not_individual_settlement")["status"] == "FROZEN"
assert by(breaks, "break_id", "vno_effective_value_accounting_reduction_nonadditive")["status"] == "FROZEN"

crosswalk = read_csv(HERE / "E0_SECURITY_IDENTIFIER_CROSSWALK_V127.csv")
assert len(crosswalk) == 6 and len({row["crosswalk_id"] for row in crosswalk}) == 6
assert by(crosswalk, "crosswalk_id", "ID127_06")["isin"] == "ARARGE03E121"


# Trazabilidad institucional: todo sigue en borrador y los cierres pendientes son explícitos.
trace = read_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V127.csv")
closures = read_csv(HERE / "E0_REQUEST_CLOSURE_CRITERIA_V127.csv")
keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V127.csv")
attachments = read_csv(HERE / "E0_REQUEST_ATTACHMENT_MINIMUM_V127.csv")
assert len(trace) == 81 and len({row["trace_id"] for row in trace}) == 81
assert len(closures) == 9 and len({row["gap_id"] for row in closures}) == 9
assert len(keys) == 62 and len({row["key_id"] for row in keys}) == 62
assert len(attachments) == 8
assert {row["gap_id"] for row in trace} <= {row["gap_id"] for row in closures}
assert all(row["status"] == "DRAFT_NOT_SENT" for row in trace)
assert {"TR127_079", "TR127_080", "TR127_081"} <= {row["trace_id"] for row in trace}
assert {"SK127_60", "SK127_61", "SK127_62"} <= {row["key_id"] for row in keys}
assert by(closures, "gap_id", "CL127_DEBT_ACCOUNTING")["initial_status"].startswith("Q3_BODEN_AND_Q4_DISCOUNT_PESOS")
assert any(row["attach_file"] == "E0_FISCAL_Q4_DISCOUNT_PESOS_VALUATION_BRIDGE_V127.csv" for row in attachments)

responses = read_csv(HERE / "E0_REQUEST_RESPONSE_REGISTER_V127.csv")
assert len(responses) == 6 and len({row["request_id"] for row in responses}) == 6
assert all(row["status"] == "DRAFT_NOT_SENT" for row in responses)
assert all(row["submitted_on"] == "N/A" and row["receipt_or_case_id"] == "N/A" for row in responses)
for filename in (
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V127.md",
    "REQUEST_BCRA_CRYL_SETTLEMENT_V127.md",
    "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V127.md",
):
    request = (HERE / filename).read_text(encoding="utf-8")
    assert "ARARGE03E121" in request and "Clave adicional V127" in request
package = (HERE / "E0_INSTITUTIONAL_REQUEST_PACKAGE_V127.md").read_text(encoding="utf-8")
assert "81 objetos trazados y 62 claves exactas" in package and "DRAFT_NOT_SENT" in package
checklist = (HERE / "REQUEST_SUBMISSION_CHECKLIST_V127.md").read_text(encoding="utf-8")
assert "ARARGE03E121" in checklist and "NINGÚN_PEDIDO_ENVIADO" in checklist


# Cobertura histórica y panel estricto: el avance es documental, no altera la estimación numérica.
episode = read_csv(HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V127.csv")
q4_episode = next(row for row in episode if row["variable"] == "public_debt_repurchase_accounting_scope" and row["t0"] == "2008Q4")
assert q4_episode["status"] == "ACCOUNTED_AGGREGATE_DISCOUNT_PESOS_REPURCHASE_INDIVIDUAL_SETTLEMENT_OPEN"
assert q4_episode["falsifier"] == "YES_AGAINST_UNALLOCATED_Q4_EXCHANGE_BOND_AGGREGATE"

coverage = read_csv(HERE / "HISTORICAL_EVIDENCE_COVERAGE_V127.csv")
state = next(row for row in coverage if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra")
assert "Q4_DISCOUNT_PESOS_ALLOCATION" in state["quality"]
assert "Q4 Discount en Pesos" in state["gap"] and "pago BCRA" in state["gap"]
queue = read_csv(HERE / "HISTORICAL_SOURCE_QUEUE_V127.csv")
state_queue = [row for row in queue if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra"]
assert len(state_queue) == 2
assert all("62 claves y 81 objetos" in row["why"] and "AB127" in row["next_action"] for row in state_queue)

current = read_csv(HERE / "CURRENT_STATE_V127.csv")
strict_panel = read_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V127.csv")
assert len(current) == 39 and sum(row["strict_panel_status"] == "ELIGIBLE" for row in current) == 30
assert STRICT in " ".join(" ".join(row.values()) for row in strict_panel)


# Metadatos y manifiestos finales.
completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V127.json").read_text(encoding="utf-8"))
assert completeness["checkpoint"] == "V127"
assert completeness["master_catalog_entries"] == 303
assert completeness["physical_local_copies"] == completeness["physical_local_hash_ok"] == 298
assert completeness["e0_primary_sources_preserved"] == 104
assert completeness["e0_fiscal_ledger_rows"] == 131 and completeness["e0_fiscal_method_breaks_frozen"] == 96
assert completeness["e0_request_traceability_rows"] == 81 and completeness["e0_request_search_keys"] == 62
assert completeness["e0_security_identifier_crosswalk_rows"] == 6
assert completeness["e0_requests_submitted"] == completeness["e0_request_responses_received"] == 0
assert completeness["numeric_v127_strict_changed"] is False
assert completeness["closed_network_gate"] == "NO" and completeness["strict_coverage_pct"] == STRICT

manifest = json.loads((HERE / "MANIFEST_V127.json").read_text(encoding="utf-8"))
assert manifest["checkpoint"] == "V127" and manifest["parent_checkpoint"] == "V126"
assert manifest["e0_primary_sources"] == 104 and manifest["new_primary_sources"] == 1
assert manifest["fiscal_ledger_rows"] == 131 and manifest["fiscal_method_breaks"] == 96
assert manifest["request_traceability_rows"] == 81 and manifest["request_search_keys"] == 62
assert manifest["q4_exchange_bond_stock_movement_rows"] == 3
assert manifest["q4_discount_valuation_bridge_rows"] == 3
assert manifest["requests_submitted"] == manifest["responses_received"] == 0
assert any(item["path"] == "qa_v127.py" for item in manifest["files"])
for item in manifest["files"]:
    path = HERE / item["path"]
    assert path.stat().st_size == item["bytes"] and digest(path) == item["sha256"]

global_manifest = json.loads((CYCLE / "MANIFEST_SHA256.json").read_text(encoding="utf-8"))
assert global_manifest["checkpoint"] == "V127"
assert global_manifest["exact_entities"] == 30 and global_manifest["strict_coverage_pct"] == STRICT
assert "Q4 Discount en Pesos" in global_manifest["source_audit"]
assert "none submitted" in global_manifest["source_audit"]

backup = (REPO / "BACKUP_ACTUALIZACION_2026-08-29.md").read_text(encoding="utf-8-sig")
assert "## V127 · Q4 asignado al Discount en Pesos" in backup
assert "Fecha/contraparte individual, Caja, BCRA y GDP Units siguen abiertos" in backup

print("V127 QA PASS")
