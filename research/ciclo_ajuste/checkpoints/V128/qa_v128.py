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
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def by(rows: list[dict[str, str]], field: str, value: str) -> dict[str, str]:
    return next(row for row in rows if row[field] == value)


source_specs = {
    "e0_argentina_2005_prospectus_supplement": (956554, "ffec6c453fddf7d4a9ca99c8e53e8cd0af630cfa4a9f4212c679c343b74dfe17"),
    "e0_argentina_resolution_115_323_2005_buyback_procedure": (54348, "9ea2b24c84833cd05b19fd5d0f37ec472f5eb05a6fea6933883b216820ad527d"),
    "e0_argentina_gdp_units_third_payment_2008": (59024, "64a18c8d9473cc6d61bc41333c6c9f230524617d84a3eb816f2bd31957bb0ced"),
}

# Catálogo y preservación.
catalog = read_csv(REPO / "data" / "fuentes" / "FUENTES.csv")
assert len(catalog) == 306 and len({row["id"] for row in catalog}) == 306
for source_id, (size, expected_hash) in source_specs.items():
    row = by(catalog, "id", source_id)
    path = REPO / row["archivo_local"].lstrip("/")
    assert path.is_file() and path.stat().st_size == size
    assert digest(path) == row["sha256"] == expected_hash
    assert row["fecha_descarga"] == "2026-08-30"

census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V128.csv")
assert len(census) == 107 and len({row["source_id"] for row in census}) == 107
for source_id, (size, expected_hash) in source_specs.items():
    row = by(census, "source_id", source_id)
    assert row["primary_source"] == row["preserved"] == "YES"
    assert row["bytes"] == str(size) and row["sha256"] == expected_hash

hash_rows = read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V128.csv")
assert len(hash_rows) == 306 and len({row["id"] for row in hash_rows}) == 306
assert sum(row["exists"] == "True" for row in hash_rows) == 301
assert sum(row["hash_ok"] == "True" for row in hash_rows) == 301
assert len(read_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V128.csv")) == 306
for source_id in source_specs:
    assert by(hash_rows, "id", source_id)["hash_ok"] == "True"

# Alcance económico: subtotal GDP y total con Discount.
scope = read_csv(HERE / "E0_FISCAL_GDP_UNITS_REPURCHASE_SCOPE_BRIDGE_V128.csv")
assert len(scope) == 5 and len({row["scope_id"] for row in scope}) == 5
gdp_ars = by(scope, "scope_id", "GS128_01")
gdp_usd = by(scope, "scope_id", "GS128_02")
gdp_total = by(scope, "scope_id", "GS128_GDP_SUBTOTAL")
discount = by(scope, "scope_id", "GS128_03")
official_total = by(scope, "scope_id", "GS128_TOTAL")
assert gdp_ars["isin"] == "ARARGE03E147" and Decimal(gdp_ars["vno_native_million"]) == Decimal("43824.10")
assert gdp_usd["isin"] == "ARARGE03E154" and Decimal(gdp_usd["vno_native_million"]) == Decimal("260.90")
assert Decimal(gdp_ars["effective_value_million_ars"]) + Decimal(gdp_usd["effective_value_million_ars"]) == Decimal(gdp_total["effective_value_million_ars"]) == Decimal("1886.10")
assert Decimal(gdp_total["effective_value_million_ars"]) + Decimal(discount["effective_value_million_ars"]) == Decimal(official_total["effective_value_million_ars"]) == Decimal("3301.60")
assert gdp_total["vno_native_million"] == official_total["vno_native_million"] == "N/A_MIXED_CURRENCIES"

report = read_csv(HERE / "E0_FISCAL_EXCESS_GROWTH_BUYBACK_REFERENCE_2006_V128.csv")
assert len(report) == 4
assert all("CONTRACTUAL_TIMELINE_BRIDGED" in row["evidence_status"] for row in report if row["isin"] in {"ARARGE03E147", "ARARGE03E154"})

# Cronología contractual y separación de eventos/mecanismos.
timeline = read_csv(HERE / "E0_GDP_UNITS_CONTRACTUAL_TIMELINE_V128.csv")
assert len(timeline) == 8 and len({row["timeline_id"] for row in timeline}) == 8
assert by(timeline, "timeline_id", "GT128_02")["date_or_window"] == "2007-11-01"
assert by(timeline, "timeline_id", "GT128_03")["date_or_window"] == "2008-01-01/2008-12-31"
assert "No reducir la ventana a Q4" in by(timeline, "timeline_id", "GT128_03")["prohibited_inference"]
assert by(timeline, "timeline_id", "GT128_04")["evidence_status"] == "CONTRACTUAL_CANCELLATION_OBLIGATION"
assert "ausencia de una fila de principal" in by(timeline, "timeline_id", "GT128_05")["allowed_inference"]
assert by(timeline, "timeline_id", "GT128_07")["source_locator"] == "A.5.1!B63;A.5.4!B62"

separation = read_csv(HERE / "E0_GDP_UNITS_PAYMENT_VS_REPURCHASE_SEPARATION_V128.csv")
assert len(separation) == 2
assert by(separation, "comparison_id", "GPS128_REPURCHASE")["reference_year"] == "2006"
coupon = by(separation, "comparison_id", "GPS128_COUPON")
assert coupon["reference_year"] == "2007" and coupon["calculation_date"] == "2008-11-01"
assert "ARARGE03E147 0.0245480 ARS" in coupon["isin_or_variant"]

procedure = read_csv(HERE / "E0_EXCESS_GDP_VS_PAYMENT_CAPACITY_PROCEDURE_V128.csv")
assert len(procedure) == 2
assert by(procedure, "comparison_id", "GP128_EXCESS_GDP")["application_to_reference_2006"] == "CONTRACTUAL_AND_RETROSPECTIVELY_REPORTED"
schema = by(procedure, "comparison_id", "GP128_PAYMENT_CAPACITY")
assert schema["application_to_reference_2006"] == "PROCEDURAL_SCHEMA_ONLY_NOT_PROVEN"
assert "T+2" in schema["selection_or_process"] and "T+3" in schema["selection_or_process"] and "T+6" in schema["selection_or_process"]

# Ledger, cortes e identificadores.
ledger = read_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V128.csv")
assert len(ledger) == 135 and len({row["ledger_id"] for row in ledger}) == 135
f132, f133, f134, f135 = (by(ledger, "ledger_id", item) for item in ("F132", "F133", "F134", "F135"))
assert Decimal(f132["normalized_ars_million"]) == Decimal("1858.10")
assert Decimal(f133["normalized_ars_million"]) == Decimal("28.00")
assert Decimal(f134["normalized_ars_million"]) == Decimal("1886.10")
assert f134["additivity"] == "TOTAL_DO_NOT_ADD_TO_F132_F133"
assert f135["realization_status"] == "OFFICIAL_COUPON_ANNOUNCEMENT_SEPARATE_FROM_REPURCHASE"
assert not any(row["realization_status"] == "CASH_SETTLED" for row in (f132, f133, f134, f135))

breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V128.csv")
assert len(breaks) == 100 and len({row["break_id"] for row in breaks}) == 100
for break_id in (
    "gdp_notional_no_principal_stock",
    "gdp_reference_year_not_transaction_date",
    "gdp_coupon_payment_not_repurchase_consideration",
    "excess_payment_capacity_procedure_not_excess_gdp_transaction",
):
    assert by(breaks, "break_id", break_id)["status"] == "FROZEN"

crosswalk = read_csv(HERE / "E0_SECURITY_IDENTIFIER_CROSSWALK_V128.csv")
assert len(crosswalk) == 6 and len({row["crosswalk_id"] for row in crosswalk}) == 6
for isin in ("ARARGE03E147", "ARARGE03E154"):
    row = by(crosswalk, "isin", isin)
    assert "CONTRACTUAL_ROUTE" in row["evidence_status"] and "cupón referencia 2007" in row["prohibited_inference"]

# Paquete institucional: más preciso, todavía no enviado.
trace = read_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V128.csv")
keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V128.csv")
attachments = read_csv(HERE / "E0_REQUEST_ATTACHMENT_MINIMUM_V128.csv")
closures = read_csv(HERE / "E0_REQUEST_CLOSURE_CRITERIA_V128.csv")
assert len(trace) == 85 and len({row["trace_id"] for row in trace}) == 85
assert len(keys) == 67 and len({row["key_id"] for row in keys}) == 67
assert len(attachments) == 9 and len(closures) == 9
assert {row["gap_id"] for row in trace} <= {row["gap_id"] for row in closures}
assert all(row["status"] == "DRAFT_NOT_SENT" for row in trace)
assert {"TR128_082", "TR128_083", "TR128_084", "TR128_085"} <= {row["trace_id"] for row in trace}
assert {"SK128_63", "SK128_64", "SK128_65", "SK128_66", "SK128_67"} <= {row["key_id"] for row in keys}
assert any(row["attach_file"] == "E0_FISCAL_GDP_UNITS_REPURCHASE_SCOPE_BRIDGE_V128.csv" for row in attachments)
assert "CANCELLATION_PAYMENT_OPEN_NOT_SENT" in by(closures, "gap_id", "CL128_DEBT_ACCOUNTING")["initial_status"]

responses = read_csv(HERE / "E0_REQUEST_RESPONSE_REGISTER_V128.csv")
assert len(responses) == 6 and len({row["request_id"] for row in responses}) == 6
assert all(row["status"] == "DRAFT_NOT_SENT" for row in responses)
assert all(row["submitted_on"] == "N/A" and row["receipt_or_case_id"] == "N/A" for row in responses)
for filename in (
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V128.md",
    "REQUEST_BCRA_CRYL_SETTLEMENT_V128.md",
    "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V128.md",
):
    request = (HERE / filename).read_text(encoding="utf-8")
    assert "Clave adicional V128" in request and "ARARGE03E147" in request and "ARARGE03E154" in request
package = (HERE / "E0_INSTITUTIONAL_REQUEST_PACKAGE_V128.md").read_text(encoding="utf-8")
assert "85 objetos trazados y 67 claves exactas" in package and "DRAFT_NOT_SENT" in package
checklist = (HERE / "REQUEST_SUBMISSION_CHECKLIST_V128.md").read_text(encoding="utf-8")
assert "tercer cupón referencia 2007" in checklist and "NINGÚN_PEDIDO_ENVIADO" in checklist

# Matriz histórica y panel estricto sin contaminación numérica.
episode = read_csv(HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V128.csv")
gdp_episode = by(episode, "variable", "gdp_units_excess_gdp_repurchase_scope")
assert gdp_episode["status"] == "AGGREGATE_SCOPE_AND_2008_WINDOW_CLOSED_INDIVIDUAL_CANCELLATION_PAYMENT_OPEN"
assert gdp_episode["falsifier"] == "YES_AGAINST_GDP_EXCLUSION_MEANS_ZERO_OR_UNEXECUTED"

coverage = read_csv(HERE / "HISTORICAL_EVIDENCE_COVERAGE_V128.csv")
state = next(row for row in coverage if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra")
assert "REFERENCE_2006_GDP_SCOPE" in state["quality"] and "asientos de cancelación" in state["gap"]
queue = read_csv(HERE / "HISTORICAL_SOURCE_QUEUE_V128.csv")
state_queue = [row for row in queue if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra"]
assert len(state_queue) == 2
assert all("67 claves y 85 objetos" in row["why"] and "GS128/GT128" in row["next_action"] for row in state_queue)

current = read_csv(HERE / "CURRENT_STATE_V128.csv")
strict_panel = read_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V128.csv")
assert len(current) == 39 and sum(row["strict_panel_status"] == "ELIGIBLE" for row in current) == 30
assert STRICT in " ".join(" ".join(row.values()) for row in strict_panel)

# Metadatos, manifiestos y limpieza.
completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V128.json").read_text(encoding="utf-8"))
assert completeness["checkpoint"] == "V128"
assert completeness["master_catalog_entries"] == 306
assert completeness["physical_local_copies"] == completeness["physical_local_hash_ok"] == 301
assert completeness["e0_primary_sources_preserved"] == 107
assert completeness["e0_fiscal_ledger_rows"] == 135 and completeness["e0_fiscal_method_breaks_frozen"] == 100
assert completeness["e0_request_traceability_rows"] == 85 and completeness["e0_request_search_keys"] == 67
assert completeness["e0_request_attachment_rows"] == 9
assert completeness["e0_gdp_units_scope_bridge_rows"] == 5 and completeness["e0_gdp_contractual_timeline_rows"] == 8
assert completeness["e0_requests_submitted"] == completeness["e0_request_responses_received"] == 0
assert completeness["numeric_v128_strict_changed"] is False
assert completeness["closed_network_gate"] == "NO" and completeness["strict_coverage_pct"] == STRICT

manifest = json.loads((HERE / "MANIFEST_V128.json").read_text(encoding="utf-8"))
assert manifest["checkpoint"] == "V128" and manifest["parent_checkpoint"] == "V127"
assert manifest["e0_primary_sources"] == 107 and manifest["new_primary_sources"] == 3
assert manifest["fiscal_ledger_rows"] == 135 and manifest["fiscal_method_breaks"] == 100
assert manifest["request_traceability_rows"] == 85 and manifest["request_search_keys"] == 67
assert manifest["gdp_units_scope_bridge_rows"] == 5 and manifest["gdp_contractual_timeline_rows"] == 8
assert manifest["requests_submitted"] == manifest["responses_received"] == 0
assert any(item["path"] == "qa_v128.py" for item in manifest["files"])
for item in manifest["files"]:
    path = HERE / item["path"]
    assert path.stat().st_size == item["bytes"] and digest(path) == item["sha256"]

global_manifest = json.loads((CYCLE / "MANIFEST_SHA256.json").read_text(encoding="utf-8"))
assert global_manifest["checkpoint"] == "V128"
assert global_manifest["exact_entities"] == 30 and global_manifest["strict_coverage_pct"] == STRICT
assert "reference-2006 GDP/Discount scope" in global_manifest["source_audit"]
assert "none submitted" in global_manifest["source_audit"]

backup = (REPO / "BACKUP_ACTUALIZACION_2026-08-29.md").read_text(encoding="utf-8-sig")
assert "## V128 · puente contractual y GDP Units referencia 2006" in backup
assert "Cálculo contractual 01/11/2007" in backup
assert not (REPO / "tmp" / "pdfs" / "v128").exists()
assert not (REPO / "tmp" / "spreadsheets" / "v128").exists()

print("V128 QA PASS")
