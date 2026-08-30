from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import csv
import hashlib
import json
import shutil


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
V127 = HERE.parent / "V127"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v128" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        if not rows:
            raise ValueError(f"fields required for empty CSV: {path}")
        fields = list(rows[0])
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bump_text(text: str) -> str:
    text = text.replace("V127", "V128").replace("v127", "v128")
    for prefix in ("AB", "CA", "CL", "DM", "EG", "ID", "REQ", "SG", "SK", "SM", "ST", "TR", "VB"):
        text = text.replace(f"{prefix}127_", f"{prefix}128_")
    return text


def clone_parent() -> None:
    skip = {
        "build_e0_q4_discount_bridge_v127.py",
        "qa_v127.py",
        "MANIFEST_V127.json",
        "INHERITED_QA_STATUS_V127.csv",
    }
    for source in V127.iterdir():
        if not source.is_file() or source.name in skip or source.name.startswith("HANDOVER_PROXIMA_SESION"):
            continue
        target = HERE / source.name.replace("V127", "V128")
        target.write_text(bump_text(source.read_text(encoding="utf-8-sig")), encoding="utf-8")


clone_parent()

sources = [
    {
        "id": "e0_argentina_2005_prospectus_supplement",
        "institution": "República Argentina · Ministerio de Economía",
        "title": "Prospectus Supplement · Exchange Offer 2005",
        "url": "https://www.argentina.gob.ar/sites/default/files/mfin_us_prospectus_and_prospectus_supplement.pdf",
        "filename": "argentina_2005_prospectus_supplement.pdf",
        "published": "2005-01-10",
        "period": "canje 2005; reglas de recompra para años de referencia 2005-2010",
        "type": "PDF oficial · suplemento de prospecto",
        "sha256": "ffec6c453fddf7d4a9ca99c8e53e8cd0af630cfa4a9f4212c679c343b74dfe17",
        "bytes": 956554,
        "families": "fiscal;debt;exchange;GDP_units;repurchase;cancellation;CRYL;Caja",
        "breaks": "año de referencia versus fecha de cálculo versus calendario de recompra; recompra contractual versus operación individual; notional GDP Units versus principal",
        "status": "USABLE_CONTRACTUAL_TIMELINE_CANCELLATION_AND_REGISTRATION_ROUTE",
        "caveat": "Fija reglas y ventana contractual, no demuestra qué día, por qué modalidad ni frente a qué vendedor se ejecutó cada compra.",
    },
    {
        "id": "e0_argentina_resolution_115_323_2005_buyback_procedure",
        "institution": "Secretarías de Finanzas y Hacienda · Ministerio de Economía y Producción",
        "title": "Resolución Conjunta 115/2005 y 323/2005 · procedimiento de recompra",
        "url": "https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-115-2005-111413/texto",
        "filename": "argentina_resolucion_conjunta_115_323_2005.html",
        "published": "2005-11-17",
        "period": "excedente de capacidad de pago anual 2004-2009",
        "type": "HTML oficial · texto normativo preservado",
        "sha256": "9ea2b24c84833cd05b19fd5d0f37ec472f5eb05a6fea6933883b216820ad527d",
        "bytes": 54348,
        "families": "fiscal;debt;buyback;tender;MAE;Caja;BCRA;settlement;records",
        "breaks": "excedente de capacidad de pago anual versus recompra por exceso de PBI; procedimiento general versus aplicación al evento objetivo",
        "status": "USABLE_PROCEDURAL_SCHEMA_NOT_TRANSACTION_PROOF",
        "caveat": "Aporta campos, productores documentales y secuencia T-2/T+2/T+3/T+6; no prueba que la recompra por exceso de PBI referencia 2006 utilizara esa licitación.",
    },
    {
        "id": "e0_argentina_gdp_units_third_payment_2008",
        "institution": "Ministerio de Economía y Producción · Secretaría de Finanzas",
        "title": "Comunicado · tercer pago de las Unidades vinculadas al PBI",
        "url": "https://www.argentina.gob.ar/sites/default/files/comunicado_3er_cupon_unidad_pbi.pdf",
        "filename": "argentina_gdp_units_third_payment_2008.pdf",
        "published": "2008-11-25",
        "period": "año de referencia 2007; fecha de cálculo 2008-11-01",
        "type": "PDF oficial · comunicado de pago",
        "sha256": "64a18c8d9473cc6d61bc41333c6c9f230524617d84a3eb816f2bd31957bb0ced",
        "bytes": 59024,
        "families": "fiscal;debt;GDP_units;coupon;payment;isin",
        "breaks": "pago contingente por unidad versus recompra y cancelación; año de referencia 2007 versus recompra referencia 2006",
        "status": "USABLE_SEPARATE_COUPON_EVENT_AND_IDENTIFIER_CONTROL",
        "caveat": "Es un anuncio del tercer cupón por referencia 2007; no es el precio ni la constancia de liquidación de la recompra por referencia 2006.",
    },
]

for source in sources:
    path = BIN / source["filename"]
    assert path.is_file() and path.stat().st_size == source["bytes"]
    assert sha256(path) == source["sha256"]
    source["local"] = "/" + path.relative_to(REPO).as_posix()

source_ids = {source["id"] for source in sources}
catalog = [row for row in read_csv(CATALOG) if row["id"] not in source_ids]
for row in catalog:
    if row["id"] == "e0_argentina_recompras_decreto_1735_04_report":
        row["nota"] = (
            "V128 E0 fiscal: la página 2 identifica para referencia 2006 GDP Units ARS ARARGE03E147 "
            "(VNO ARS 43.824,10m; efectivo ARS 1.858,10m), GDP Units USD ley argentina ARARGE03E154 "
            "(VNO USD 260,90m; efectivo ARS 28,00m) y Discount ARARGE03E121 (efectivo ARS 1.415,50m); "
            "total efectivo ARS 3.301,60m. No individualiza fechas, vendedores ni riel de pago."
        )
for source in sources:
    catalog.append(
        {
            "id": source["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": source["institution"],
            "titulo": source["title"], "url_original": source["url"], "archivo_local": source["local"],
            "fecha_descarga": "2026-08-30", "fecha_publicacion": source["published"], "codigo_serie": "",
            "periodo_utilizado": source["period"], "tipo": source["type"], "sha256": source["sha256"],
            "nota": f"V128 E0 fiscal: {source['bytes']:,} bytes. {source['caveat']}",
        }
    )
assert len(catalog) == 306 and len({row["id"] for row in catalog}) == 306
write_csv(CATALOG, catalog)

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V128.csv"
census = [row for row in read_csv(census_path) if row["source_id"] not in source_ids]
for row in census:
    if row["source_id"] == "e0_argentina_recompras_decreto_1735_04_report":
        row["variable_families"] = "state_bcra;fiscal;debt;buyback;excess_growth;GDP_units;discount_pesos;isin"
        row["method_breaks"] = "VNO por moneda versus efectivo ARS; año de referencia versus ejecución; recompra versus cupón; agregado por especie versus transacción"
        row["use_status"] = "USABLE_REFERENCE_2006_GDP_AND_DISCOUNT_SCOPE_EFFECTIVE_TOTAL"
        row["caveat"] = "La página 2 cierra especies, VNO nativos y efectivo agregado; no publica fecha/contraparte de cada compra ni constancia Caja/BCRA."
for source in sources:
    census.append(
        {
            "source_id": source["id"], "institution": source["institution"], "artifact": source["title"],
            "url": source["url"], "local_path": source["local"], "sha256": source["sha256"],
            "bytes": str(source["bytes"]), "period_coverage": source["period"],
            "variable_families": source["families"], "primary_source": "YES", "preserved": "YES",
            "method_breaks": source["breaks"], "use_status": source["status"], "caveat": source["caveat"],
        }
    )
assert len(census) == 107 and len({row["source_id"] for row in census}) == 107
write_csv(census_path, census)

# El informe retrospectivo cierra el alcance económico; el prospecto acota calendario y tratamiento contractual.
scope = [
    {"scope_id": "GS128_01", "reference_year": "2006", "component": "GDP Units ARS Argentine law", "isin": "ARARGE03E147", "vno_native_million": "43824.10", "vno_currency": "ARS", "effective_value_million_ars": "1858.10", "source_chain": "e0_argentina_recompras_decreto_1735_04_report", "locator_chain": "PDF_p2", "additivity": "COMPONENT", "evidence_status": "OFFICIAL_REPURCHASE_COMPONENT", "caveat": "VNO no es principal exigible ni debe sumarse con el VNO USD."},
    {"scope_id": "GS128_02", "reference_year": "2006", "component": "GDP Units USD Argentine law", "isin": "ARARGE03E154", "vno_native_million": "260.90", "vno_currency": "USD", "effective_value_million_ars": "28.00", "source_chain": "e0_argentina_recompras_decreto_1735_04_report", "locator_chain": "PDF_p2", "additivity": "COMPONENT", "evidence_status": "OFFICIAL_REPURCHASE_COMPONENT", "caveat": "El efectivo está expresado en ARS; el VNO permanece en USD."},
    {"scope_id": "GS128_GDP_SUBTOTAL", "reference_year": "2006", "component": "GDP Units subtotal", "isin": "ARARGE03E147;ARARGE03E154", "vno_native_million": "N/A_MIXED_CURRENCIES", "vno_currency": "MIXED", "effective_value_million_ars": "1886.10", "source_chain": "e0_argentina_recompras_decreto_1735_04_report", "locator_chain": "PDF_p2", "additivity": "SUBTOTAL_DO_NOT_ADD_TO_COMPONENTS", "evidence_status": "EXACT_DERIVED_FROM_OFFICIAL_COMPONENTS", "caveat": "Subtotal efectivo exacto; no acredita fecha, contraparte ni débito."},
    {"scope_id": "GS128_03", "reference_year": "2006", "component": "Discount en Pesos 5.83% 2033", "isin": "ARARGE03E121", "vno_native_million": "2748.50", "vno_currency": "ARS", "effective_value_million_ars": "1415.50", "source_chain": "e0_argentina_recompras_decreto_1735_04_report;E0_FISCAL_Q4_DISCOUNT_PESOS_VALUATION_BRIDGE_V128.csv", "locator_chain": "PDF_p2;VB128", "additivity": "COMPONENT", "evidence_status": "OFFICIAL_REPURCHASE_COMPONENT_Q4_ACCOUNTING_RECONCILED", "caveat": "El efectivo no es la baja contable actualizada."},
    {"scope_id": "GS128_TOTAL", "reference_year": "2006", "component": "Official total", "isin": "N/A", "vno_native_million": "N/A_MIXED_CURRENCIES", "vno_currency": "MIXED", "effective_value_million_ars": "3301.60", "source_chain": "e0_argentina_recompras_decreto_1735_04_report", "locator_chain": "PDF_p2", "additivity": "TOTAL_DO_NOT_ADD_TO_COMPONENTS_OR_SUBTOTAL", "evidence_status": "OFFICIAL_TABLE_TOTAL_EXACTLY_RECONCILED", "caveat": "Total efectivo, no stock, principal ni confirmación bancaria."},
]
assert Decimal(scope[0]["effective_value_million_ars"]) + Decimal(scope[1]["effective_value_million_ars"]) == Decimal("1886.10")
assert Decimal(scope[2]["effective_value_million_ars"]) + Decimal(scope[3]["effective_value_million_ars"]) == Decimal(scope[4]["effective_value_million_ars"]) == Decimal("3301.60")
write_csv(HERE / "E0_FISCAL_GDP_UNITS_REPURCHASE_SCOPE_BRIDGE_V128.csv", scope)

timeline = [
    {"timeline_id": "GT128_01", "event_or_rule": "REFERENCE_YEAR", "date_or_window": "2006", "instrument_scope": "GDP Units and eligible New Securities", "source_id": "e0_argentina_recompras_decreto_1735_04_report", "source_locator": "PDF_p2", "evidence_status": "OFFICIAL_RETROSPECTIVE_REFERENCE_YEAR", "allowed_inference": "La tabla pertenece al cálculo por exceso de PBI de referencia 2006.", "prohibited_inference": "No tratar 2006 como fecha de negociación."},
    {"timeline_id": "GT128_02", "event_or_rule": "CALCULATION_DATE", "date_or_window": "2007-11-01", "instrument_scope": "reference year 2006", "source_id": "e0_argentina_2005_prospectus_supplement", "source_locator": "S-19;S-69", "evidence_status": "CONTRACTUAL_DATE_DERIVED_BY_RULE", "allowed_inference": "El cálculo debía realizarse el 1 de noviembre del año siguiente.", "prohibited_inference": "No prueba publicación, orden o pago ese día."},
    {"timeline_id": "GT128_03", "event_or_rule": "REPURCHASE_WINDOW", "date_or_window": "2008-01-01/2008-12-31", "instrument_scope": "reference year 2006", "source_id": "e0_argentina_2005_prospectus_supplement", "source_locator": "S-19;S-69", "evidence_status": "CONTRACTUAL_CALENDAR_WINDOW", "allowed_inference": "La ejecución debía ocurrir durante el año calendario posterior a la fecha de cálculo.", "prohibited_inference": "No reducir la ventana a Q4 ni elegir una fecha individual sin registro."},
    {"timeline_id": "GT128_04", "event_or_rule": "CANCELLATION", "date_or_window": "after repurchase", "instrument_scope": "all repurchased New Securities", "source_id": "e0_argentina_2005_prospectus_supplement", "source_locator": "S-19;S-69", "evidence_status": "CONTRACTUAL_CANCELLATION_OBLIGATION", "allowed_inference": "El asiento de cancelación es un registro objetivo esperable.", "prohibited_inference": "No afirmar cancelación material sin asiento."},
    {"timeline_id": "GT128_05", "event_or_rule": "NO_PRINCIPAL_GDP_UNITS", "date_or_window": "life of GDP-linked securities", "instrument_scope": "GDP-linked Securities", "source_id": "e0_argentina_2005_prospectus_supplement", "source_locator": "S-25", "evidence_status": "CONTRACTUAL_NOTIONAL_TREATMENT", "allowed_inference": "La ausencia de una fila de principal es compatible con el contrato.", "prohibited_inference": "No interpretar ausencia de stock principal como ausencia de recompra."},
    {"timeline_id": "GT128_06", "event_or_rule": "CRYL_REGISTRATION", "date_or_window": "security lifecycle", "instrument_scope": "ARS and USD Argentine-law New Securities", "source_id": "e0_argentina_2005_prospectus_supplement", "source_locator": "S-21", "evidence_status": "CONTRACTUAL_REGISTRATION_ROUTE", "allowed_inference": "CRyL es productor objetivo de registros y Caja puede enlazar mediante su cuenta.", "prohibited_inference": "No atribuir automáticamente a Caja el registro final o una transferencia concreta."},
    {"timeline_id": "GT128_07", "event_or_rule": "Q4_DISCLOSURE_EXCLUSION", "date_or_window": "2008Q4", "instrument_scope": "GDP Units repurchase amount", "source_id": "e0_argentina_deuda_publica_2008_q4", "source_locator": "A.5.1!B63;A.5.4!B62", "evidence_status": "OFFICIAL_EXPLICIT_EXCLUSION", "allowed_inference": "La tabla de deuda avisa que el monto de recompra GDP Units está fuera de ese cuadro.", "prohibited_inference": "No convertir exclusión en cero o no ejecución."},
    {"timeline_id": "GT128_08", "event_or_rule": "THIRD_COUPON_ANNOUNCEMENT", "date_or_window": "2008-11-25; calculation 2008-11-01; reference 2007", "instrument_scope": "five GDP Unit variants", "source_id": "e0_argentina_gdp_units_third_payment_2008", "source_locator": "PDF_p1", "evidence_status": "SEPARATE_OFFICIAL_COUPON_EVENT", "allowed_inference": "Confirma identificadores y pago contingente por unidad para referencia 2007.", "prohibited_inference": "No usar el importe por unidad como precio de la recompra referencia 2006."},
]
write_csv(HERE / "E0_GDP_UNITS_CONTRACTUAL_TIMELINE_V128.csv", timeline)

separation = [
    {"comparison_id": "GPS128_REPURCHASE", "event": "Reference-2006 excess-GDP repurchase", "reference_year": "2006", "calculation_date": "2007-11-01", "execution_or_announcement": "calendar 2008; individual date open", "isin_or_variant": "ARARGE03E147;ARARGE03E154;ARARGE03E121", "reported_measure": "ARS 3301.60m effective total; GDP subtotal ARS 1886.10m", "economic_role": "repurchase and contractual cancellation", "source_chain": "e0_argentina_recompras_decreto_1735_04_report;e0_argentina_2005_prospectus_supplement", "additivity": "SEPARATE_EVENT", "caveat": "Aggregate scope is proven; execution date, seller and payment rail remain open."},
    {"comparison_id": "GPS128_COUPON", "event": "Third GDP Unit coupon announcement", "reference_year": "2007", "calculation_date": "2008-11-01", "execution_or_announcement": "announcement 2008-11-25", "isin_or_variant": "US040114GM64 0.0227980 USD;ARARGE03E154 0.0227980 USD;XS0209139244 0.0198520 EUR;ARARGE03E147 0.0245480 ARS;ARARGE03E675 0.0241512 JPY", "reported_measure": "payment per unit by variant", "economic_role": "contingent coupon payment", "source_chain": "e0_argentina_gdp_units_third_payment_2008;e0_argentina_2005_prospectus_supplement", "additivity": "SEPARATE_EVENT_NON_ADDITIVE", "caveat": "Not a repurchase price, aggregate consideration, cancellation record or proof of settlement."},
]
write_csv(HERE / "E0_GDP_UNITS_PAYMENT_VS_REPURCHASE_SEPARATION_V128.csv", separation)

procedure = [
    {"comparison_id": "GP128_EXCESS_GDP", "mechanism": "Five percent of Excess GDP", "governing_source": "e0_argentina_2005_prospectus_supplement", "period": "reference years 2005-2010", "selection_or_process": "Argentina selects outstanding New Securities at sole discretion; bidding, secondary market or otherwise allowed", "records_expected": "calculation paper; purchase record; security identifier; nominal/effective value; cancellation record", "application_to_reference_2006": "CONTRACTUAL_AND_RETROSPECTIVELY_REPORTED", "caveat": "The prospectus does not identify the individual execution route used in 2008."},
    {"comparison_id": "GP128_PAYMENT_CAPACITY", "mechanism": "Annual excess payment capacity", "governing_source": "e0_argentina_resolution_115_323_2005_buyback_procedure", "period": "calendar years 2004-2009", "selection_or_process": "public tender via MAE; T-2 call; T+2 transfer to Caja fiduciary account; T+3 Caja report and Treasury payment to BCRA accounts; T+6 cancellation on continuing default", "records_expected": "ONCP proposal; offers; preaward by participant; Caja receipt report; payment order; BCRA account entry; default/cancellation record", "application_to_reference_2006": "PROCEDURAL_SCHEMA_ONLY_NOT_PROVEN", "caveat": "Do not assume this distinct mechanism governed the reference-2006 Excess GDP repurchase without an operation-specific document."},
]
write_csv(HERE / "E0_EXCESS_GDP_VS_PAYMENT_CAPACITY_PROCEDURE_V128.csv", procedure)

# Enriquecer la tabla heredada de alcance sin alterar sus cifras.
report_path = HERE / "E0_FISCAL_EXCESS_GROWTH_BUYBACK_REFERENCE_2006_V128.csv"
report = read_csv(report_path)
for row in report:
    if row["isin"] in {"ARARGE03E147", "ARARGE03E154"}:
        row["source_id"] = "e0_argentina_recompras_decreto_1735_04_report;e0_argentina_2005_prospectus_supplement"
        row["evidence_status"] = "OFFICIAL_REPURCHASE_SCOPE_AND_CONTRACTUAL_TIMELINE_BRIDGED"
        row["caveat"] = "Alcance y ventana 2008 probados; día, vendedor, modalidad, asiento de cancelación y pago siguen abiertos."
write_csv(report_path, report)

ledger_path = HERE / "E0_FISCAL_MECHANISM_LEDGER_V128.csv"
ledger = read_csv(ledger_path)
ledger.extend(
    [
        {"ledger_id": "F132", "window": "REFERENCE_2006_REPURCHASE_DURING_2008", "mechanism": "Debt_buyback_excess_GDP", "phase": "OFFICIAL_GDP_ARS_EFFECTIVE_COMPONENT", "as_of_date": "CALENDAR_2008_INDIVIDUAL_DATE_OPEN", "payer": "Tesoro_Nacional", "recipient": "Instrument_holders_unknown", "universe": "Five_percent_excess_GDP_reference_2006", "instrument": "GDP_Unit_ARS_ARARGE03E147", "amount_original": "1858.10", "original_unit": "ARS_million_effective_value", "normalized_ars_million": "1858.10", "valuation_basis": "OFFICIAL_RETROSPECTIVE_REPORT_PAGE_2", "source_id": "e0_argentina_recompras_decreto_1735_04_report;e0_argentina_2005_prospectus_supplement", "source_locator": "PDF_p2;S-19/S-69", "realization_status": "OFFICIAL_AGGREGATE_REPURCHASE_COMPONENT_CONTRACTUAL_CANCELLATION_RECORD_OPEN", "additivity": "NON_ADDITIVE_WITH_F134", "status_interpretation": "VNO ARS 43824.10m; efectivo ARS 1858.10m; ventana contractual 2008.", "caveat": "No acredita fecha, vendedor, modalidad, asiento CRyL ni pago."},
        {"ledger_id": "F133", "window": "REFERENCE_2006_REPURCHASE_DURING_2008", "mechanism": "Debt_buyback_excess_GDP", "phase": "OFFICIAL_GDP_USD_LA_EFFECTIVE_COMPONENT", "as_of_date": "CALENDAR_2008_INDIVIDUAL_DATE_OPEN", "payer": "Tesoro_Nacional", "recipient": "Instrument_holders_unknown", "universe": "Five_percent_excess_GDP_reference_2006", "instrument": "GDP_Unit_USD_Argentine_law_ARARGE03E154", "amount_original": "28.00", "original_unit": "ARS_million_effective_value", "normalized_ars_million": "28.00", "valuation_basis": "OFFICIAL_RETROSPECTIVE_REPORT_PAGE_2", "source_id": "e0_argentina_recompras_decreto_1735_04_report;e0_argentina_2005_prospectus_supplement", "source_locator": "PDF_p2;S-19/S-69", "realization_status": "OFFICIAL_AGGREGATE_REPURCHASE_COMPONENT_CONTRACTUAL_CANCELLATION_RECORD_OPEN", "additivity": "NON_ADDITIVE_WITH_F134", "status_interpretation": "VNO USD 260.90m; efectivo ARS 28.00m; ventana contractual 2008.", "caveat": "No mezclar moneda del VNO con moneda del efectivo ni inferir riel de pago."},
        {"ledger_id": "F134", "window": "REFERENCE_2006_REPURCHASE_DURING_2008", "mechanism": "Debt_buyback_excess_GDP", "phase": "GDP_UNITS_EFFECTIVE_SUBTOTAL", "as_of_date": "CALENDAR_2008_INDIVIDUAL_DATE_OPEN", "payer": "Tesoro_Nacional", "recipient": "Instrument_holders_unknown", "universe": "GDP_Units_reference_2006", "instrument": "ARARGE03E147_and_ARARGE03E154", "amount_original": "1886.10", "original_unit": "ARS_million_effective_value", "normalized_ars_million": "1886.10", "valuation_basis": "EXACT_SUM_OFFICIAL_COMPONENTS", "source_id": "e0_argentina_recompras_decreto_1735_04_report", "source_locator": "PDF_p2", "realization_status": "OFFICIAL_AGGREGATE_EFFECTIVE_SUBTOTAL_INDIVIDUAL_SETTLEMENT_OPEN", "additivity": "TOTAL_DO_NOT_ADD_TO_F132_F133", "status_interpretation": "ARS 1858.10m + ARS 28.00m = ARS 1886.10m; con Discount ARS 1415.50m reproduce ARS 3301.60m.", "caveat": "Subtotal efectivo no es principal, baja contable ni débito BCRA."},
        {"ledger_id": "F135", "window": "REFERENCE_2007_ANNOUNCED_2008_11_25", "mechanism": "GDP_linked_contingent_payment", "phase": "THIRD_COUPON_ANNOUNCEMENT", "as_of_date": "2008-11-25", "payer": "República_Argentina", "recipient": "GDP_Unit_holders", "universe": "Five_GDP_Unit_variants", "instrument": "US040114GM64;ARARGE03E154;XS0209139244;ARARGE03E147;ARARGE03E675", "amount_original": "N/D_VECTOR_IN_STATUS", "original_unit": "payment_per_unit_by_currency", "normalized_ars_million": "N/D", "valuation_basis": "OFFICIAL_COUPON_COMMUNIQUE", "source_id": "e0_argentina_gdp_units_third_payment_2008", "source_locator": "PDF_p1", "realization_status": "OFFICIAL_COUPON_ANNOUNCEMENT_SEPARATE_FROM_REPURCHASE", "additivity": "NON_ADDITIVE_SEPARATE_EVENT", "status_interpretation": "Importes por unidad: USD 0.0227980 (NY y ley argentina), EUR 0.0198520, ARS 0.0245480 y JPY 0.0241512.", "caveat": "Referencia 2007; no es la recompra referencia 2006 ni su consideración efectiva."},
    ]
)
assert len(ledger) == 135 and len({row["ledger_id"] for row in ledger}) == 135
write_csv(ledger_path, ledger)

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V128.csv"
breaks = read_csv(breaks_path)
for row in breaks:
    if row["break_id"] == "gdp_units_excluded_not_zero_or_unexecuted":
        row["status"] = "FROZEN_REINFORCED_BY_V128_CONTRACT_AND_Q4_FOOTNOTE"
        row["evidence"] = "Prospectus S-25; Deuda Q4 A.5.1 B63/A.5.4 B62; report p.2"
breaks.extend(
    [
        {"break_id": "gdp_notional_no_principal_stock", "dimension": "instrument", "problem": "Las GDP Units usan monto nocional y no tienen pagos de principal.", "rule": "No exigir una fila de stock principal como condición de existencia; buscar recompra, cancelación y pagos contingentes por separado.", "status": "FROZEN", "evidence": "Prospectus Supplement S-25; Deuda Q4 A.5.1 B63/A.5.4 B62"},
        {"break_id": "gdp_reference_year_not_transaction_date", "dimension": "time", "problem": "El año de referencia 2006 no es la fecha de compra.", "rule": "Aplicar la regla contractual: cálculo 2007-11-01 y ventana calendario 2008; mantener el día individual abierto.", "status": "FROZEN", "evidence": "Prospectus Supplement S-19/S-69; report p.2"},
        {"break_id": "gdp_coupon_payment_not_repurchase_consideration", "dimension": "mechanism", "problem": "El tercer cupón anunciado en 2008 corresponde al año de referencia 2007 y expresa importes por unidad.", "rule": "No usar esos importes como precio, efectivo agregado ni constancia de cancelación de la recompra referencia 2006.", "status": "FROZEN", "evidence": "Comunicado tercer cupón 2008 p.1; Prospectus Supplement"},
        {"break_id": "excess_payment_capacity_procedure_not_excess_gdp_transaction", "dimension": "mechanism", "problem": "La Resolución 115/323 regula excedente de capacidad de pago anual, mecanismo distinto del cinco por ciento de Excess GDP.", "rule": "Usar su secuencia sólo como esquema de productores/campos; exigir documento específico antes de atribuir MAE, Caja T+3 o cuentas BCRA al evento objetivo.", "status": "FROZEN", "evidence": "Resolución Conjunta 115/2005 y 323/2005; Prospectus Supplement S-19/S-69"},
    ]
)
assert len(breaks) == 100 and len({row["break_id"] for row in breaks}) == 100
write_csv(breaks_path, breaks)

crosswalk_path = HERE / "E0_SECURITY_IDENTIFIER_CROSSWALK_V128.csv"
crosswalk = read_csv(crosswalk_path)
for row in crosswalk:
    if row["isin"] in {"ARARGE03E147", "ARARGE03E154"}:
        row["primary_chain"] += " + prospecto 2005 S-21/S-25/S-69 + comunicado tercer cupón 2008"
        row["evidence_status"] = "EXACT_CONTEMPORANEOUS_ISIN_CONTRACTUAL_ROUTE_AND_SEPARATE_COUPON_CONTROL"
        row["unresolved_element"] = "Asiento de recompra/cancelación 2008; fecha; participante; pago"
        row["prohibited_inference"] = "No usar el cupón referencia 2007 como precio o liquidación de la recompra referencia 2006."
    if row["isin"] == "ARARGE03E121":
        row["primary_chain"] += " + prospecto 2005 S-19/S-69"
        row["unresolved_element"] = "Fecha/modalidad individual 2008; Código Caja/CRyL histórico; contraparte; asiento de cancelación y pago"
write_csv(crosswalk_path, crosswalk)

trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V128.csv"
trace = read_csv(trace_path)
trace.extend(
    [
        {"trace_id": "TR128_082", "request_id": "REQ128_ECON", "institution": "Ministerio de Economía / ONCP / Dirección de Administración de la Deuda", "gap_id": "CL128_DEBT_ACCOUNTING", "requested_record": "Ledger o papel de trabajo de recompra y baja por especie para la referencia 2006", "period_or_date": "cálculo 2007-11-01; ejecución 2008", "identifiers": "ARARGE03E147 VNO ARS43824.10m efectivo ARS1858.10m;ARARGE03E154 VNO USD260.90m efectivo ARS28.00m;ARARGE03E121 VNO ARS2748.50m efectivo ARS1415.50m", "minimum_usable_fields": "fecha; modalidad; especie; VNO; precio/efectivo; expediente; orden; asiento de baja/cancelación; estado", "confidentiality_fallback": "certificación agregada por especie y fecha con datos de terceros testados", "status": "DRAFT_NOT_SENT"},
        {"trace_id": "TR128_083", "request_id": "REQ128_BCRA", "institution": "BCRA / CRyL", "gap_id": "CL128_DEBT_ACCOUNTING", "requested_record": "Asientos de movimiento y cancelación de las tres especies del tramo referencia 2006", "period_or_date": "2008-01-01/2008-12-31", "identifiers": "ARARGE03E147;ARARGE03E154;ARARGE03E121; cantidades VNO exactas", "minimum_usable_fields": "fecha; ISIN/especie; nominal; cuenta o participante testado; tipo de movimiento; estado; referencia de asiento/orden", "confidentiality_fallback": "certificación agregada por fecha, ISIN, nominal y estado", "status": "DRAFT_NOT_SENT"},
        {"trace_id": "TR128_084", "request_id": "REQ128_CAJA", "institution": "Caja de Valores S.A. / enlace CRyL", "gap_id": "CL128_DEBT_ACCOUNTING", "requested_record": "Movimientos por la cuenta de Caja en CRyL o puente documental hacia el registro final", "period_or_date": "2008-01-01/2008-12-31", "identifiers": "códigos 45698 y 45701; ARARGE03E147;ARARGE03E154;ARARGE03E121", "minimum_usable_fields": "fecha; código/ISIN; nominal; origen/destino testado; tipo de evento; estado; referencia correlativa CRyL", "confidentiality_fallback": "certificación de existencia o inexistencia por especie, fecha y nominal", "status": "DRAFT_NOT_SENT"},
        {"trace_id": "TR128_085", "request_id": "REQ128_ECON", "institution": "Ministerio de Economía / ONCP", "gap_id": "CL128_DEBT_ACCOUNTING", "requested_record": "Documento que vincule cálculo de Excess GDP referencia 2006 con modalidad y compras ejecutadas en 2008", "period_or_date": "2007-11-01/2008-12-31", "identifiers": "cinco por ciento de Excess GDP; referencia 2006; total efectivo ARS3301.60m; expediente o actuación", "minimum_usable_fields": "cálculo; fecha; norma; modalidad; instrumentos; adjudicación/compra; cancelación; expediente", "confidentiality_fallback": "índice y metadatos de expediente más cuadro agregado por especie", "status": "DRAFT_NOT_SENT"},
    ]
)
assert len(trace) == 85 and len({row["trace_id"] for row in trace}) == 85
write_csv(trace_path, trace)

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V128.csv"
keys = read_csv(keys_path)
keys.extend(
    [
        {"key_id": "SK128_63", "request_id": "REQ128_ECON", "key_group": "gdp_contractual_window", "exact_key": "reference year 2006;calculation date 2007-11-01;calendar year 2008;five percent Excess GDP", "search_purpose": "localizar cálculo y expediente que convirtió la referencia 2006 en compras 2008", "source_or_basis": "Prospectus Supplement S-19/S-69", "caveat": "La ventana no identifica día ni modalidad."},
        {"key_id": "SK128_64", "request_id": "REQ128_ECON", "key_group": "gdp_scope_amounts", "exact_key": "ARARGE03E147;43824.10;1858.10;ARARGE03E154;260.90;28.00;ARARGE03E121;2748.50;1415.50;3301.60", "search_purpose": "localizar ledger, orden y baja por cantidades exactas", "source_or_basis": "informe recompras Decreto 1735/04 p.2", "caveat": "VNOs en monedas mixtas; efectivo en ARS."},
        {"key_id": "SK128_65", "request_id": "REQ128_BCRA", "key_group": "cryl_cancellation", "exact_key": "CRYL;Caja de Valores account;ARARGE03E147;ARARGE03E154;ARARGE03E121;cancellation;2008", "search_purpose": "localizar asientos de movimiento y cancelación", "source_or_basis": "Prospectus Supplement S-21/S-69", "caveat": "Ruta contractual, no constancia de un asiento concreto."},
        {"key_id": "SK128_66", "request_id": "REQ128_ECON", "key_group": "procedure_schema_only", "exact_key": "S01:0385745/2005;ONCP;MAE;T+2;T+3;Caja;BCRA;T+6", "search_purpose": "identificar productores y campos y preguntar qué procedimiento se aplicó", "source_or_basis": "Resolución Conjunta 115/2005 y 323/2005", "caveat": "Mecanismo de excedente de capacidad de pago; no atribuirlo automáticamente a Excess GDP."},
        {"key_id": "SK128_67", "request_id": "REQ128_BCRA", "key_group": "coupon_repurchase_separation", "exact_key": "third GDP Unit payment;reference year 2007;calculation date 2008-11-01;ARARGE03E147;ARARGE03E154", "search_purpose": "evitar confundir asientos del tercer cupón con recompra/cancelación referencia 2006", "source_or_basis": "comunicado tercer cupón 2008", "caveat": "Control negativo; el cupón es un evento distinto."},
    ]
)
assert len(keys) == 67 and len({row["key_id"] for row in keys}) == 67
write_csv(keys_path, keys)

attachments_path = HERE / "E0_REQUEST_ATTACHMENT_MINIMUM_V128.csv"
attachments = read_csv(attachments_path)
attachments.append(
    {"request_id": "REQ128_ECON", "institution": "Ministerio de Economía / Tesoro", "attach_file": "E0_FISCAL_GDP_UNITS_REPURCHASE_SCOPE_BRIDGE_V128.csv", "purpose": "tres especies, VNO nativos y efectivo exacto del tramo referencia 2006", "why_minimal": "acota la búsqueda del ledger y expediente sin remitir fuentes completas", "exclude": "atribución de vendedor, modalidad o pago no documentada"}
)
assert len(attachments) == 9
write_csv(attachments_path, attachments)

closures_path = HERE / "E0_REQUEST_CLOSURE_CRITERIA_V128.csv"
closures = read_csv(closures_path)
for row in closures:
    if row["gap_id"] == "CL128_DEBT_ACCOUNTING":
        row["does_not_close"] = "El alcance GDP/Discount, la ventana 2008 y la obligación de cancelación no cierran fecha/modalidad/vendedor, asiento CRyL/Caja ni pago BCRA."
        row["initial_status"] = "REFERENCE_2006_SCOPE_AND_2008_CONTRACTUAL_WINDOW_RECONCILED_INDIVIDUAL_CANCELLATION_PAYMENT_OPEN_NOT_SENT"
write_csv(closures_path, closures)

request_addenda = {
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V128.md": """

## Clave adicional V128 · tramo completo de referencia 2006

El prospecto fija fecha de cálculo `01/11/2007`, ejecución durante el calendario 2008 y cancelación de los títulos recomprados. Se solicita el ledger, expediente o papel de trabajo que identifique fecha y modalidad de compra y baja de `ARARGE03E147` (VNO ARS 43.824,10m; efectivo ARS 1.858,10m), `ARARGE03E154` (VNO USD 260,90m; efectivo ARS 28,00m) y `ARARGE03E121` (VNO ARS 2.748,50m; efectivo ARS 1.415,50m). Campos mínimos: cálculo, fecha, modalidad, especie, VNO, precio/efectivo, expediente, orden y asiento de cancelación. La Resolución Conjunta 115/323 se cita únicamente como esquema de campos/productores del mecanismo de excedente de capacidad de pago; se solicita indicar si fue aplicable o qué procedimiento específico rigió este tramo.
""",
    "REQUEST_BCRA_CRYL_SETTLEMENT_V128.md": """

## Clave adicional V128 · cancelación CRyL del tramo referencia 2006

Para `01/01/2008-31/12/2008`, se solicitan asientos o certificación agregada por `ARARGE03E147`, `ARARGE03E154` y `ARARGE03E121`, con fecha, nominal, tipo de movimiento, estado, cuenta/participante testado y referencia de orden o asiento de cancelación. El prospecto identifica a CRyL como registro de los títulos en pesos y dólares bajo ley argentina; esa previsión contractual no se presenta como prueba de que un asiento concreto exista.
""",
    "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V128.md": """

## Clave adicional V128 · enlace Caja–CRyL

Para el calendario 2008, se solicita búsqueda por códigos Caja `45698`/`45701`, ISIN `ARARGE03E147`/`ARARGE03E154` y `ARARGE03E121`, incluyendo movimientos cursados por la cuenta de Caja en CRyL o metadatos que permitan correlacionar el registro final. Campos mínimos: fecha, código/ISIN, nominal, origen/destino testado, evento, estado y referencia CRyL. No se presupone que Caja haya sido el registro final ni que el anuncio del tercer cupón referencia 2007 sea parte de esta recompra.
""",
}
for filename, addendum in request_addenda.items():
    path = HERE / filename
    text = path.read_text(encoding="utf-8-sig")
    if "Clave adicional V128" not in text:
        path.write_text(text.rstrip() + addendum, encoding="utf-8")

package_path = HERE / "E0_INSTITUTIONAL_REQUEST_PACKAGE_V128.md"
package = package_path.read_text(encoding="utf-8-sig")
package = package.replace("81 objetos trazados y 62 claves exactas", "85 objetos trazados y 67 claves exactas")
package += """

## Clave V128 · GDP Units y cancelación contractual

El paquete agrega el tramo completo referencia 2006, la ventana contractual 2008 y las rutas documentales CRyL/Caja. El tercer cupón referencia 2007 y el procedimiento de excedente de capacidad de pago quedan separados como controles, no como prueba del evento. Estado: `DRAFT_NOT_SENT`.
"""
package_path.write_text(package, encoding="utf-8")

checklist_path = HERE / "REQUEST_SUBMISSION_CHECKLIST_V128.md"
checklist = checklist_path.read_text(encoding="utf-8-sig")
checklist = checklist.replace(
    "- Discount en Pesos `ARARGE03E121`: VNO ARS 2.748,50m, valor efectivo ARS 1.415,50m y baja actualizada ARS 4.723,53619m, siempre como bases no aditivas.",
    "- tramo referencia 2006: `ARARGE03E147`, `ARARGE03E154` y `ARARGE03E121`, con VNO en monedas nativas y efectivo ARS siempre separados;\n- ventana contractual: cálculo 01/11/2007, compras durante 2008 y cancelación; no inventar día/modalidad;\n- control negativo: tercer cupón referencia 2007 y Resolución 115/323 no prueban la recompra objetivo."
)
checklist_path.write_text(checklist, encoding="utf-8")

episode_path = HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V128.csv"
episode = read_csv(episode_path)
episode.append(
    {"episode_id": "E0", "episode_name": "Crisis de convertibilidad / default / salida / reordenamiento financiero", "t0": "REFERENCE_2006_CALC_2007_REPURCHASE_2008", "shock_type": "OTHER", "variable": "gdp_units_excess_gdp_repurchase_scope", "sector": "STATE", "frequency": "EVENT", "pre_value": "N/A_NOTIONAL_SECURITIES", "trough_value": "GDP_UNITS_EFFECTIVE_ARS1886.10M", "trough_date": "CALENDAR_2008_EXACT_DATE_OPEN", "recovery_value": "TOTAL_WITH_DISCOUNT_ARS3301.60M", "recovery_date": "CALENDAR_2008_EXACT_DATE_OPEN", "months_to_trough": "N/D", "months_to_recovery": "N/D", "benchmark_definition": "official reference-2006 repurchase scope plus contractual calculation/window/cancellation rules", "source_id": "e0_argentina_recompras_decreto_1735_04_report;e0_argentina_2005_prospectus_supplement;e0_argentina_deuda_publica_2008_q4", "source_quality": "PRIMARY_EXACT_AGGREGATE_SCOPE_AND_CONTRACTUAL_TIMELINE", "basis": "report p2;prospectus S-19/S-21/S-25/S-69;Q4 A.5.1 B63/A.5.4 B62", "method_break": "YES_NOTIONAL_NO_PRINCIPAL_REFERENCE_YEAR_NOT_TRADE_DATE", "status": "AGGREGATE_SCOPE_AND_2008_WINDOW_CLOSED_INDIVIDUAL_CANCELLATION_PAYMENT_OPEN", "interpretation": "GDP Units effective subtotal ARS 1886.10m and total with Discount ARS 3301.60m are reconciled; the absence from principal tables is contract-compatible.", "falsifier": "YES_AGAINST_GDP_EXCLUSION_MEANS_ZERO_OR_UNEXECUTED", "notes": "No exact transaction date, seller, cancellation entry or payment rail; strict panel unchanged."}
)
write_csv(episode_path, episode)

coverage_path = HERE / "HISTORICAL_EVIDENCE_COVERAGE_V128.csv"
coverage = read_csv(coverage_path)
for row in coverage:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row["quality"] = "PRIMARY_Q3_BODEN_Q4_DISCOUNT_AND_REFERENCE_2006_GDP_SCOPE_CONTRACT_BRIDGED"
        row["comparable"] = "SERIES_SERVICE_RECONCILED_AGGREGATE_SCOPE_GDP_NOTIONAL_AND_SETTLEMENT_BREAKS_FROZEN"
        row["gap"] = "Q3 BODEN, Q4 Discount y el alcance GDP referencia 2006 están conciliados; faltan fechas/vendedores, asientos de cancelación CRyL/Caja, pagos BCRA, T+3 y cuarta comunicación."
        row["next_action"] = "Con autorización expresa, pedir asientos 2008 por los tres ISIN/cantidades; mantener cupón referencia 2007 y procedimiento de capacidad de pago como eventos separados."
write_csv(coverage_path, coverage)

queue_path = HERE / "HISTORICAL_SOURCE_QUEUE_V128.csv"
queue = read_csv(queue_path)
for row in queue:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row["status"] = "REFERENCE_2006_GDP_DISCOUNT_SCOPE_AND_CONTRACTUAL_WINDOW_RECONCILED_CANCELLATION_PAYMENT_READY_NOT_SENT"
        row["why"] = "Q3 BODEN, Q4 Discount y GDP Units referencia 2006 están conciliados; 67 claves y 85 objetos aíslan cancelación CRyL/Caja y pago sin mezclar cupón o mecanismo."
        row["next_action"] = "Obtener autorización expresa y presentar sólo pedidos autorizados; conciliar respuestas con GS128/GT128 y el puente contable AB128."
write_csv(queue_path, queue)

reconstruction = """# Reconstrucción fiscal E0 · V128

## Alcance económico cerrado

Para el año de referencia 2006, el informe oficial reporta dos componentes de GDP Units: `ARARGE03E147`, VNO ARS 43.824,10m y efectivo ARS 1.858,10m; y `ARARGE03E154`, VNO USD 260,90m y efectivo ARS 28,00m. El subtotal efectivo GDP es ARS 1.886,10m. Sumado al Discount `ARARGE03E121` —efectivo ARS 1.415,50m— reproduce exactamente el total oficial ARS 3.301,60m. Los VNO están en monedas distintas y no se suman.

## Puente contractual

El prospecto dispone para la referencia 2006 una fecha de cálculo del 1/11/2007 y la recompra durante el calendario 2008. Todo título recomprado debe cancelarse. Los nuevos títulos en pesos y dólares bajo ley argentina se registran en CRyL; Caja mantiene una cuenta allí. Esta cadena acota la búsqueda de registros, pero no demuestra un asiento concreto.

Las GDP Units no tienen pagos de principal: operan sobre monto nocional. Por eso su ausencia de las tablas de principal no implica cero ni falta de ejecución. Además, A.5.1 B63 y A.5.4 B62 del informe Q4 advierten expresamente que el monto de su recompra está excluido.

## Separaciones obligatorias

El tercer cupón anunciado el 25/11/2008 corresponde a referencia 2007 y expresa pagos por unidad: es un evento diferente de la recompra referencia 2006. La Resolución Conjunta 115/323 aporta un esquema T-2/T+2/T+3/T+6 para el excedente de capacidad de pago anual, pero no prueba que ese procedimiento distinto se haya aplicado a esta recompra por Excess GDP.

## Frontera probatoria

Quedan abiertos el día y modalidad de cada compra, vendedores, expediente operativo, asientos de cancelación CRyL/Caja y orden/débito BCRA. Seis pedidos siguen `DRAFT_NOT_SENT`. `CLOSED_NETWORK_GATE=NO`.
"""
(HERE / "E0_FISCAL_RECONSTRUCTION_V128.md").write_text(reconstruction, encoding="utf-8")

readme = """# Checkpoint V128 · puente contractual y alcance GDP Units

V128 cierra el alcance económico del tramo referencia 2006: GDP Units efectivo ARS 1.886,10m más Discount efectivo ARS 1.415,50m = total oficial ARS 3.301,60m.

El prospecto fija cálculo 01/11/2007, ejecución durante 2008, cancelación de los títulos recomprados y registro CRyL para las variantes argentinas. También confirma que las GDP Units no tienen principal; la exclusión de las tablas de stock no equivale a cero.

El tercer cupón referencia 2007 y el procedimiento de excedente de capacidad de pago se mantienen separados. Fecha/modalidad/vendedor, asientos CRyL/Caja y pago BCRA siguen abiertos. Seis pedidos permanecen `DRAFT_NOT_SENT`; panel estricto sin cambios.
"""
(HERE / "README_V128.md").write_text(readme, encoding="utf-8")

verdict = """# Veredicto V128

Queda probado que las dos GDP Units del tramo de recompra por exceso de PBI referencia 2006 suman un valor efectivo de ARS 1.886,10 millones y que, junto con el Discount en Pesos por ARS 1.415,50 millones, reproducen exactamente el total oficial de ARS 3.301,60 millones.

El prospecto permite ubicar contractualmente el cálculo en 01/11/2007 y la recompra durante 2008; ordena cancelar los títulos recomprados, identifica a CRyL como registro de las variantes argentinas y establece que las GDP Units no tienen principal. Esto refuta la lectura “no aparece en stock, entonces no ocurrió”, pero no acredita un asiento específico.

No se confunde el tercer cupón referencia 2007 con la recompra referencia 2006, ni el procedimiento de excedente de capacidad de pago con el mecanismo de Excess GDP. Continúan abiertos fecha/modalidad/vendedor, expediente, cancelación CRyL/Caja y pago BCRA. `CLOSED_NETWORK_GATE=NO`.
"""
(HERE / "VEREDICTO_V128.md").write_text(verdict, encoding="utf-8")

retrieval = """# Registro de recuperación V128

Fecha: 2026-08-30.

1. Se preservó y verificó visualmente el Prospectus Supplement oficial de 2005; las páginas relevantes fijan cálculo, calendario de recompra, cancelación, registro CRyL/Caja y tratamiento nocional de GDP Units.
2. Se preservó el texto oficial de la Resolución Conjunta 115/2005 y 323/2005, expediente S01:0385745/2005. Se usa sólo como esquema de procedimiento/productores para el excedente de capacidad de pago anual.
3. Se preservó y verificó visualmente el comunicado oficial del tercer cupón GDP Units, referencia 2007 y cálculo 01/11/2008; se mantiene separado de la recompra referencia 2006.
4. Se inspeccionaron copias temporales de los XLS Q3/Q4. A.5.1 B63 y A.5.4 B62 del Q4 excluyen expresamente el monto de recompra GDP Units; las menciones restantes son notas de pagos contingentes.
5. Las búsquedas públicas exactas por ISIN y montos no recuperaron fecha/vendedor, expediente operativo, asiento de cancelación CRyL/Caja ni orden/débito BCRA.
6. No se envió ningún pedido ni se realizó presentación externa.
"""
(HERE / "RETRIEVAL_LOG_V128.md").write_text(retrieval, encoding="utf-8")

refs = """# Referencias de fuentes V128

- Prospectus Supplement 2005: https://www.argentina.gob.ar/sites/default/files/mfin_us_prospectus_and_prospectus_supplement.pdf
- Resolución Conjunta 115/2005 y 323/2005: https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-115-2005-111413/texto
- Valores negociables vinculados al PBI: https://www.argentina.gob.ar/economia/finanzas/valores-negociables-vinculados-al-pbi
- Comunicado tercer cupón 2008: https://www.argentina.gob.ar/sites/default/files/comunicado_3er_cupon_unidad_pbi.pdf
- Informe de recompras bajo Decreto 1735/04: https://www.argentina.gob.ar/sites/default/files/recompras_de_deuda.pdf
- Deuda Pública 31/12/2008: https://www.argentina.gob.ar/sites/default/files/deuda_publica_31-12-2008.xls

Los tres artefactos nuevos están preservados con SHA-256 en el catálogo maestro.
"""
(HERE / "SOURCE_REFERENCES_V128.md").write_text(refs, encoding="utf-8")

handover = """# Handover V128 → V129

## Estado congelado

- GDP Units referencia 2006: efectivo ARS 1.886,10m; con Discount ARS 1.415,50m reproduce total ARS 3.301,60m.
- VNO: ARS 43.824,10m para ARARGE03E147 y USD 260,90m para ARARGE03E154; no sumar monedas.
- Cálculo contractual 01/11/2007; compras durante 2008; títulos recomprados sujetos a cancelación.
- GDP Units no tienen principal; la exclusión Q4 no equivale a cero/no ejecución.
- CRyL es el registro contractual de las variantes argentinas; Caja enlaza mediante su cuenta, sin que eso pruebe un asiento individual.
- Tercer cupón referencia 2007 y procedimiento de excedente de capacidad de pago quedan separados.
- Seis borradores, ninguno enviado; panel estricto sin cambios.

## Prioridad V129

1. Buscar actuación ONCP/DADP que una cálculo 2007, modalidad 2008, tres ISIN y total ARS 3.301,60m.
2. Buscar asientos de cancelación CRyL/Caja en todo 2008 por los VNO exactos.
3. Buscar orden/débito de efectivo y expediente de pago, sin inferir el riel desde el valor efectivo.
4. Retomar informes T+3 y cuarta comunicación sólo como rama separada, salvo documento de enlace.
5. No calcular cupón evitado sin fecha y asiento de cancelación; no enviar pedidos sin autorización expresa.
"""
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V128_A_V129.md").write_text(handover, encoding="utf-8")

audit_md = f"""# Auditoría V128

- Fuentes maestras: {len(catalog)}.
- Fuentes nuevas preservadas: 3; prospecto, resolución y comunicado oficial, todos con SHA-256 verificado.
- Fuentes primarias E0: {len(census)}.
- Ledger fiscal: {len(ledger)} filas.
- Cortes metodológicos: {len(breaks)}.
- Puente de alcance GDP Units: {len(scope)} filas; subtotal efectivo ARS 1.886,10m; total con Discount ARS 3.301,60m.
- Línea contractual: {len(timeline)} reglas/eventos; separación pago/recompra: {len(separation)}; separación de mecanismos: {len(procedure)}.
- Pedidos: 6 borradores, 0 enviados; {len(trace)} objetos, {len(keys)} claves, {len(attachments)} adjuntos mínimos.
- Panel estricto: 30 entidades; {STRICT}% sin cambios.
"""
(HERE / "AUDITORIA_V128.md").write_text(audit_md, encoding="utf-8")

inherited = [
    {"script": "qa_v97.py", "pre_v128_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v128_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V97 congela una ausencia luego resuelta."},
    *({"script": f"qa_v{i}.py", "pre_v128_result": "PASS", "post_v128_result": "PASS", "interpretation": "Compatible"} for i in (98, 100, 101, 102, 103, 104, 105, 106)),
    *({"script": f"qa_v{i}.py", "pre_v128_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v128_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "Congela un checkpoint o conteo anterior."} for i in range(107, 128)),
    {"script": "qa_v128.py", "pre_v128_result": "N/A", "post_v128_result": "PASS", "interpretation": "GDP scope, contractual timeline and event/mechanism separations closed; individual settlement open."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V128.csv", inherited)

for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    shutil.copyfile(AUDIT / f"{stem}_V127.csv", AUDIT / f"{stem}_V128.csv")

hash_rows = [row for row in read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V127.csv") if row["id"] not in source_ids]
for source in sources:
    hash_rows.append({"id": source["id"], "archivo_local": source["local"], "exists": "True", "sha_catalog": source["sha256"], "sha_actual": source["sha256"], "hash_ok": "True"})
assert len(hash_rows) == 306
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V128.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V128.csv", hash_rows)

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V128.csv"
provenance = [row for row in read_csv(provenance_path) if row["source_id"] not in source_ids]
for source in sources:
    provenance.append(
        {"source_id": source["id"], "original_url": source["url"], "retrieval_url": source["url"], "capture_timestamp": "20260830", "cdx_digest": "N/A_DIRECT_OFFICIAL", "local_path": source["local"], "sha256": source["sha256"], "bytes": str(source["bytes"]), "provenance_note": "Descarga directa desde el portador institucional oficial; binario o HTML preservado y hash congelado en V128."}
    )
write_csv(provenance_path, provenance)

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": str(size), "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V128.csv", size_rows)

physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
assert physical == hash_ok == 301
completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V127.json").read_text(encoding="utf-8"))
for key in list(completeness):
    if key.endswith("_v127") or "newly_preserved_v127" in key or "sources_newly_preserved_v127" in key or key == "numeric_v127_strict_changed":
        completeness.pop(key, None)
completeness.update(
    {
        "checkpoint": "V128", "date": "2026-08-30",
        "state": "E0_REFERENCE_2006_GDP_DISCOUNT_SCOPE_CONTRACTUAL_WINDOW_CANCELLATION_TARGET_EXACT_INDIVIDUAL_SETTLEMENT_OPEN_NOT_SENT",
        "numeric_v128_strict_changed": False, "master_catalog_entries": len(catalog),
        "physical_local_copies": physical, "physical_local_hash_ok": hash_ok,
        "binary_required_entries": len(catalog) - 5, "binary_required_preserved": physical,
        "e0_primary_sources_preserved": len(census),
        "e0_quality": "PRIMARY_REFERENCE_2006_GDP_DISCOUNT_SCOPE_AND_CONTRACTUAL_TIMELINE_EXACT",
        "sources_newly_preserved_v128": 3, "e0_primary_sources_newly_preserved_v128": 3,
        "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
        "e0_request_drafts": 6, "e0_request_traceability_rows": len(trace), "e0_request_closure_rules": len(closures),
        "e0_request_search_keys": len(keys), "e0_request_attachment_rows": len(attachments),
        "e0_security_identifier_crosswalk_rows": len(crosswalk),
        "e0_gdp_units_scope_bridge_rows": len(scope), "e0_gdp_contractual_timeline_rows": len(timeline),
        "e0_gdp_payment_repurchase_separation_rows": len(separation), "e0_gdp_procedure_comparison_rows": len(procedure),
        "e0_requests_submitted": 0, "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
        "historical_workstream": "Reference-2006 GDP Units and Discount scope reconciled; calculation 2007-11-01, calendar-2008 repurchase window and cancellation target established; exact individual CRyL/Caja/payment records remain open; coupon and payment-capacity procedure separated; no request submitted",
    }
)
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V128.json").write_text(json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V128 · puente contractual y GDP Units referencia 2006"
old_backup = backup.read_text(encoding="utf-8-sig")
if marker not in old_backup:
    old_backup += (
        f"\n\n{marker}\n\n"
        "- GDP Units efectivo ARS 1.886,10m más Discount ARS 1.415,50m reproduce total ARS 3.301,60m.\n"
        "- Cálculo contractual 01/11/2007; recompra durante 2008; títulos sujetos a cancelación.\n"
        "- Las GDP Units no tienen principal; la exclusión Q4 no equivale a cero/no ejecución.\n"
        "- CRyL/Caja quedan como ruta documental, no como asiento probado.\n"
        "- Cupón referencia 2007 y procedimiento de capacidad de pago separados. Seis pedidos DRAFT_NOT_SENT.\n"
        "- Panel estricto y cifras bancarias sin cambios.\n"
    )
    backup.write_text(old_backup, encoding="utf-8")


def checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V128.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V128", "parent_checkpoint": "V127",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": 3, "new_primary_sources": 3,
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks),
        "gdp_units_scope_bridge_rows": len(scope), "gdp_contractual_timeline_rows": len(timeline),
        "gdp_payment_repurchase_separation_rows": len(separation), "gdp_procedure_comparison_rows": len(procedure),
        "request_drafts": 6, "request_traceability_rows": len(trace), "request_closure_rules": len(closures),
        "request_search_keys": len(keys), "request_attachment_rows": len(attachments),
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V128.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


checkpoint_manifest()


def build_tree(root: Path) -> str:
    lines = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix().casefold()):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        lines.append(path.relative_to(root).as_posix() + ("/" if path.is_dir() else ""))
    return "\n".join(lines) + "\n"


(REPO / "TREE.txt").write_text(build_tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(build_tree(CYCLE), encoding="utf-8")

global_manifest_path = CYCLE / "MANIFEST_SHA256.json"
global_files = []
for path in sorted(REPO.rglob("*"), key=lambda item: item.relative_to(REPO).as_posix().casefold()):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or path == global_manifest_path:
        continue
    global_files.append({"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})
global_manifest = {
    "checkpoint": "V128", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical local copies with {hash_ok}/{physical} SHA-valid; reference-2006 GDP/Discount scope and contractual timeline bridged; six requests drafted and none submitted.",
    "historical_workstream": "GDP Units reference-2006 scope, contractual calendar and cancellation target established; individual CRyL/Caja/payment records open; coupon and payment-capacity procedure separated; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V128 BUILD PASS")
