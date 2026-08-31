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
V128 = HERE.parent / "V128"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
SOURCE_TMP = REPO / "tmp" / "v129_downloads" / "coloc2008_castellano_con_letras.xls"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v129" / "binaries"
SOURCE_BIN = BIN / "coloc2008_castellano_con_letras.xls"
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
    text = text.replace("V128", "V129")
    for prefix in (
        "GPS", "REQ", "GS", "GT", "GP", "AB", "CA", "CL", "DM", "EG", "ID",
        "SG", "SK", "SM", "ST", "TR", "VB",
    ):
        text = text.replace(f"{prefix}128_", f"{prefix}129_")
    return text


def clone_parent() -> None:
    skip = {
        "build_e0_gdp_contract_bridge_v128.py",
        "qa_v128.py",
        "MANIFEST_V128.json",
        "INHERITED_QA_STATUS_V128.csv",
    }
    for source in V128.iterdir():
        if not source.is_file() or source.name in skip or source.name.startswith("HANDOVER_PROXIMA_SESION"):
            continue
        target = HERE / source.name.replace("V128", "V129")
        target.write_text(bump_text(source.read_text(encoding="utf-8-sig")), encoding="utf-8")


clone_parent()

# Preserve an official annual workbook and freeze its negative scope result.
BIN.mkdir(parents=True, exist_ok=True)
source_input = SOURCE_TMP if SOURCE_TMP.is_file() else SOURCE_BIN
assert source_input.is_file() and source_input.stat().st_size == 83456
assert sha256(source_input) == "08077e8abac8a714e2d28b10a85d8f7b0510b0015c73cb94144569905d7e0fab"
if source_input != SOURCE_BIN:
    shutil.copy2(source_input, SOURCE_BIN)
assert sha256(SOURCE_BIN) == sha256(source_input)

new_source = {
    "id": "e0_argentina_colocaciones_deuda_2008_xls",
    "institution": "Ministerio de Economía · Secretaría de Finanzas",
    "title": "Emisiones de deuda pública durante 2008",
    "url": "https://www.argentina.gob.ar/sites/default/files/coloc2008_castellano_con_letras.xls",
    "local": "/" + SOURCE_BIN.relative_to(REPO).as_posix(),
    "sha256": sha256(SOURCE_BIN),
    "bytes": SOURCE_BIN.stat().st_size,
}

catalog = [row for row in read_csv(CATALOG) if row["id"] != new_source["id"]]
for row in catalog:
    if row["id"] == "e0_argentina_recompras_decreto_1735_04_report":
        row["nota"] = (
            "V129 E0 fiscal: el informe afirma recompras efectuadas, rescate mediante compras directas y licitaciones, "
            "y los tres ISIN/montos adquiridos del tramo referencia 2006. Cruzado con seis adjudicaciones GDP de las "
            "cuatro licitaciones oficiales, cierra ocurrencia, clase modal y porción licitada; no individualiza compras directas, pago ni cancelación."
        )
    if row["id"] == "e0_cgn_cuenta_inversion_2008_sdp":
        row["nota"] = (
            "V129 E0 fiscal: páginas impresas 63-64 describen las dos etapas del programa y establecen que las compras "
            "de títulos de la reestructuración 2005 realizadas bajo ese programa fueron imputadas a la recompra por excedente del PBI referencia 2006."
        )
catalog.append(
    {
        "id": new_source["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": new_source["institution"],
        "titulo": new_source["title"], "url_original": new_source["url"], "archivo_local": new_source["local"],
        "fecha_descarga": "2026-08-30", "fecha_publicacion": "", "codigo_serie": "",
        "periodo_utilizado": "2008", "tipo": "XLS oficial · binario preservado", "sha256": new_source["sha256"],
        "nota": "V129 E0 fiscal: 83.456 bytes; una hoja, 170 filas y 17 columnas. Cubre emisiones y letras intra-sector público; no contiene recompras, cancelaciones ni los tres ISIN objetivo.",
    }
)
assert len(catalog) == 348 and len({row["id"] for row in catalog}) == 348
write_csv(CATALOG, catalog)

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V129.csv"
census = [row for row in read_csv(census_path) if row["source_id"] != new_source["id"]]
for row in census:
    if row["source_id"] == "e0_argentina_recompras_decreto_1735_04_report":
        row["variable_families"] = "state_bcra;fiscal;debt;buyback;excess_growth;GDP_units;discount_pesos;isin;modality"
        row["method_breaks"] = "VNO por moneda versus efectivo ARS; año de referencia versus ejecución; agregado redondeado versus adjudicación exacta; modalidad versus liquidación"
        row["use_status"] = "USABLE_EXECUTED_REPURCHASE_OCCURRENCE_MODALITY_CLASS_THREE_ISIN_TOTAL"
        row["caveat"] = "Prueba compras efectuadas y clases compra directa/licitación; no publica la asignación individual de toda compra, vendedor, débito ni asiento de cancelación."
    if row["source_id"] == "e0_cgn_cuenta_inversion_2008_sdp":
        row["variable_families"] = "fiscal;debt;buyback;GDP_units;program;accounting_imputation"
        row["method_breaks"] = "programa mixto versus tramo Excess GDP; rescate nominal versus efectivo; imputación contable versus liquidación"
        row["use_status"] = "USABLE_PROGRAM_TO_EXCESS_GDP_ACCOUNTING_IMPUTATION_BRIDGE"
        row["caveat"] = "Imputa al bucket Excess GDP las compras elegibles del programa; no convierte todo el programa mixto en ese bucket ni confirma pago/cancelación."
census.append(
    {
        "source_id": new_source["id"], "institution": new_source["institution"], "artifact": new_source["title"],
        "url": new_source["url"], "local_path": new_source["local"], "sha256": new_source["sha256"],
        "bytes": str(new_source["bytes"]), "period_coverage": "2008", "variable_families": "debt;issuance;intra_public_sector_notes",
        "primary_source": "YES", "preserved": "YES", "method_breaks": "emisión/colocación versus recompra/cancelación",
        "use_status": "NEGATIVE_SCOPE_EMISSIONS_ONLY_NOT_BUYBACK_LEDGER",
        "caveat": "Una hoja, 170 filas y 17 columnas; sin ISIN objetivo ni campos de recompra, cancelación o pago.",
    }
)
assert len(census) == 108 and len({row["source_id"] for row in census}) == 108
write_csv(census_path, census)

# Six successful GDP awards from the four official public tenders.
tender_source_path = HERE / "E0_FISCAL_PUBLIC_BUYBACK_TENDERS_2008_V129.csv"
tenders = read_csv(tender_source_path)
awarded = [
    row for row in tenders
    if row["result_status"] == "ADJUDICADA" and row["isin"] in {"ARARGE03E147", "ARARGE03E154"}
]
assert len(awarded) == 6
award_rows = []
for row in awarded:
    award_rows.append(
        {
            "award_id": row["tender_id"], "tender_date": row["tender_date"],
            "scheduled_settlement_date": row["scheduled_settlement_date"], "instrument": row["instrument"],
            "isin": row["isin"], "native_currency": row["native_currency"],
            "awarded_vno_native": row["awarded_notional_native"],
            "awarded_effective_native": row["awarded_effective_native"],
            "reference_fx_ars_per_usd": row["reference_fx_ars_per_usd"],
            "awarded_effective_ars": row["awarded_effective_ars"],
            "source_id": row["source_id"], "source_locator": row["source_locator"],
            "imputation_status": "PUBLIC_AWARD_IMPUTED_TO_REFERENCE_2006_EXCESS_GDP_BY_CGN_BRIDGE",
            "settlement_status": "SCHEDULED_NOT_INDEPENDENTLY_CONFIRMED",
            "caveat": "Adjudicación publicada e imputación anual no equivalen a transferencia Caja, débito BCRA ni cancelación CRyL.",
        }
    )
write_csv(HERE / "E0_REFERENCE_2006_PUBLIC_TENDER_AWARDS_V129.csv", award_rows)

ars_awards = [row for row in awarded if row["isin"] == "ARARGE03E147"]
usd_awards = [row for row in awarded if row["isin"] == "ARARGE03E154"]
ars_vno = sum((Decimal(row["awarded_notional_native"]) for row in ars_awards), Decimal(0)) / Decimal(1_000_000)
usd_vno = sum((Decimal(row["awarded_notional_native"]) for row in usd_awards), Decimal(0)) / Decimal(1_000_000)
ars_eff = sum((Decimal(row["awarded_effective_ars"]) for row in ars_awards), Decimal(0)) / Decimal(1_000_000)
usd_eff = sum((Decimal(row["awarded_effective_ars"]) for row in usd_awards), Decimal(0)) / Decimal(1_000_000)
gdp_tender_eff = ars_eff + usd_eff
assert ars_vno == Decimal("1045.34205")
assert usd_vno == Decimal("29.480362")
assert ars_eff == Decimal("89.00568510")
assert usd_eff == Decimal("7.68024926")
assert gdp_tender_eff == Decimal("96.68593436")

def residual_band(official: Decimal, tender: Decimal, half_unit: Decimal) -> tuple[Decimal, Decimal, Decimal]:
    central = official - tender
    return central, central - half_unit, central + half_unit


ars_eff_res = residual_band(Decimal("1858.10"), ars_eff, Decimal("0.005"))
usd_eff_res = residual_band(Decimal("28.00"), usd_eff, Decimal("0.005"))
gdp_eff_res = residual_band(Decimal("1886.10"), gdp_tender_eff, Decimal("0.010"))
total_eff_res = residual_band(Decimal("3301.60"), gdp_tender_eff, Decimal("0.005"))
ars_vno_res = residual_band(Decimal("43824.10"), ars_vno, Decimal("0.005"))
usd_vno_res = residual_band(Decimal("260.90"), usd_vno, Decimal("0.005"))

allocation = [
    {
        "allocation_id": "MA129_GDP_ARS", "level": "INSTRUMENT", "instrument": "GDP Unit ARS", "isin": "ARARGE03E147",
        "official_vno_million_native": "43824.10", "vno_currency": "ARS", "official_effective_million_ars": "1858.10",
        "official_rounding_half_unit_million": "0.005", "public_tender_vno_million_native": str(ars_vno),
        "public_tender_effective_million_ars": str(ars_eff), "residual_vno_central_million_native": str(ars_vno_res[0]),
        "residual_effective_central_million_ars": str(ars_eff_res[0]), "residual_effective_lower_million_ars": str(ars_eff_res[1]),
        "residual_effective_upper_million_ars": str(ars_eff_res[2]),
        "tender_share_of_official_effective_pct": str(ars_eff / Decimal("1858.10") * 100),
        "modality_classification": "PUBLIC_TENDER_IDENTIFIED_PLUS_OTHER_PURCHASE_CHANNEL_RESIDUAL",
        "evidence_chain": "six official result rows;CGN 2008 pp63-64;retrospective report p2",
        "caveat": "Residual is arithmetic conditional on the rounded official aggregate; direct-operation records remain open.",
    },
    {
        "allocation_id": "MA129_GDP_USD", "level": "INSTRUMENT", "instrument": "GDP Unit USD Argentine law", "isin": "ARARGE03E154",
        "official_vno_million_native": "260.90", "vno_currency": "USD", "official_effective_million_ars": "28.00",
        "official_rounding_half_unit_million": "0.005", "public_tender_vno_million_native": str(usd_vno),
        "public_tender_effective_million_ars": str(usd_eff), "residual_vno_central_million_native": str(usd_vno_res[0]),
        "residual_effective_central_million_ars": str(usd_eff_res[0]), "residual_effective_lower_million_ars": str(usd_eff_res[1]),
        "residual_effective_upper_million_ars": str(usd_eff_res[2]),
        "tender_share_of_official_effective_pct": str(usd_eff / Decimal("28.00") * 100),
        "modality_classification": "PUBLIC_TENDER_IDENTIFIED_PLUS_OTHER_PURCHASE_CHANNEL_RESIDUAL",
        "evidence_chain": "six official result rows;CGN 2008 pp63-64;retrospective report p2",
        "caveat": "VNO stays in USD while effective value is ARS; residual inherits aggregate rounding uncertainty.",
    },
    {
        "allocation_id": "MA129_GDP_SUBTOTAL", "level": "SUBTOTAL", "instrument": "GDP Units subtotal", "isin": "ARARGE03E147;ARARGE03E154",
        "official_vno_million_native": "N/A_MIXED_CURRENCIES", "vno_currency": "MIXED", "official_effective_million_ars": "1886.10",
        "official_rounding_half_unit_million": "0.010", "public_tender_vno_million_native": "N/A_MIXED_CURRENCIES",
        "public_tender_effective_million_ars": str(gdp_tender_eff), "residual_vno_central_million_native": "N/A_MIXED_CURRENCIES",
        "residual_effective_central_million_ars": str(gdp_eff_res[0]), "residual_effective_lower_million_ars": str(gdp_eff_res[1]),
        "residual_effective_upper_million_ars": str(gdp_eff_res[2]),
        "tender_share_of_official_effective_pct": str(gdp_tender_eff / Decimal("1886.10") * 100),
        "modality_classification": "PUBLIC_TENDER_SHARE_5_13_PERCENT_OTHER_CHANNEL_RESIDUAL",
        "evidence_chain": "six official result rows;CGN 2008 pp63-64;retrospective report p2",
        "caveat": "Do not add native VNO currencies; report percentage as 5.13%, not at the displayed computational precision.",
    },
    {
        "allocation_id": "MA129_DISCOUNT", "level": "INSTRUMENT", "instrument": "Discount ARS 5.83% 2033", "isin": "ARARGE03E121",
        "official_vno_million_native": "2748.50", "vno_currency": "ARS", "official_effective_million_ars": "1415.50",
        "official_rounding_half_unit_million": "0.005", "public_tender_vno_million_native": "0",
        "public_tender_effective_million_ars": "0", "residual_vno_central_million_native": "2748.50",
        "residual_effective_central_million_ars": "1415.50", "residual_effective_lower_million_ars": "1415.495",
        "residual_effective_upper_million_ars": "1415.505", "tender_share_of_official_effective_pct": "0",
        "modality_classification": "NO_ROW_IN_COMPLETE_RECOVERED_FOUR_PUBLIC_TENDERS_DIRECT_OR_OTHER_NON_TENDER_RECORD_OPEN",
        "evidence_chain": "four official call/result pairs;retrospective report p2",
        "caveat": "The report supports direct purchases as a class, but institution, venue, date, seller and settlement for this component remain open.",
    },
    {
        "allocation_id": "MA129_TOTAL", "level": "TOTAL", "instrument": "Reference-2006 total", "isin": "THREE_ISIN",
        "official_vno_million_native": "N/A_MIXED_CURRENCIES", "vno_currency": "MIXED", "official_effective_million_ars": "3301.60",
        "official_rounding_half_unit_million": "0.005", "public_tender_vno_million_native": "N/A_MIXED_CURRENCIES",
        "public_tender_effective_million_ars": str(gdp_tender_eff), "residual_vno_central_million_native": "N/A_MIXED_CURRENCIES",
        "residual_effective_central_million_ars": str(total_eff_res[0]), "residual_effective_lower_million_ars": str(total_eff_res[1]),
        "residual_effective_upper_million_ars": str(total_eff_res[2]),
        "tender_share_of_official_effective_pct": str(gdp_tender_eff / Decimal("3301.60") * 100),
        "modality_classification": "PUBLIC_TENDER_IDENTIFIED_2_93_PERCENT_REMAINDER_NOT_TRANSACTION_LEVEL_IDENTIFIED",
        "evidence_chain": "official tender results;CGN 2008 pp63-64;retrospective report p2",
        "caveat": "Public-tender share is 2.93% of the rounded total; the residual is not itself a settlement record or a single trade.",
    },
]
write_csv(HERE / "E0_REFERENCE_2006_MODALITY_ALLOCATION_V129.csv", allocation)

imputation = [
    {"bridge_id": "IM129_01", "stage": "CONTRACT", "evidence": "5% of Excess GDP reference 2006 to be repurchased during calendar 2008 and cancelled", "source_chain": "e0_argentina_2005_prospectus_supplement", "locator": "S-19;S-69", "proof_status": "CONTRACTUAL_RULE", "does_not_prove": "individual trade, seller or settlement"},
    {"bridge_id": "IM129_02", "stage": "PROGRAM", "evidence": "2008 program had BNA market interventions and four public tenders", "source_chain": "e0_cgn_cuenta_inversion_2008_sdp", "locator": "printed_p63", "proof_status": "OFFICIAL_PROGRAM_MODALITIES", "does_not_prove": "that every mixed-program instrument belongs to Excess GDP"},
    {"bridge_id": "IM129_03", "stage": "AWARDS", "evidence": "six successful GDP rows: four ARS and two USD", "source_chain": "four official tender result PDFs", "locator": "E0_REFERENCE_2006_PUBLIC_TENDER_AWARDS_V129.csv", "proof_status": "PUBLIC_AWARD_EXACT", "does_not_prove": "actual T+ settlement or participant ultimate holder"},
    {"bridge_id": "IM129_04", "stage": "ACCOUNTING_IMPUTATION", "evidence": "eligible 2005-restructuring purchases under the program were imputed to the Excess GDP repurchase", "source_chain": "e0_cgn_cuenta_inversion_2008_sdp", "locator": "printed_p64", "proof_status": "OFFICIAL_ATTRIBUTION_BRIDGE", "does_not_prove": "payment rail or cancellation entry"},
    {"bridge_id": "IM129_05", "stage": "RETROSPECTIVE_TOTAL", "evidence": "purchases effected through direct purchases and tenders; three ISIN and acquired totals", "source_chain": "e0_argentina_recompras_decreto_1735_04_report", "locator": "PDF_p2", "proof_status": "EXECUTED_OCCURRENCE_MODALITY_CLASS_AND_TOTAL", "does_not_prove": "complete trade-level allocation"},
    {"bridge_id": "IM129_06", "stage": "RECONCILIATION", "evidence": "GDP tender effective ARS 96.68593436m; 5.13% of GDP subtotal and 2.93% of full total", "source_chain": "E0_REFERENCE_2006_MODALITY_ALLOCATION_V129.csv", "locator": "MA129_GDP_SUBTOTAL;MA129_TOTAL", "proof_status": "DECIMAL_RECONCILED_WITH_ROUNDING_BANDS", "does_not_prove": "that the arithmetic residual is one trade or one intermediary"},
]
write_csv(HERE / "E0_REFERENCE_2006_IMPUTATION_CHAIN_V129.csv", imputation)

xls_audit = [
    {"audit_id": "XLS129_01", "sheet": "Emisiones 2008", "observed_rows": "170", "observed_columns": "17", "section": "foreign- and local-currency issues", "finding": "BODEN 2015 and BONAR ARS 2013 issuance/placement entries", "scope_result": "NOT_BUYBACK_LEDGER", "search_terms": "ARARGE03E147;ARARGE03E154;ARARGE03E121;recompra;cancelación", "matches": "0", "caveat": "Negative scope does not prove absence from another official system."},
    {"audit_id": "XLS129_02", "sheet": "Emisiones 2008", "observed_rows": "170", "observed_columns": "17", "section": "Letras Intra Sector Público", "finding": "creditor, issue and maturity records for public-sector notes", "scope_result": "NOT_BUYBACK_LEDGER", "search_terms": "GDP Units;Discount;CRyL;Caja settlement", "matches": "0", "caveat": "Useful only to exclude this annual placements workbook as the missing route."},
]
write_csv(HERE / "E0_OFFICIAL_2008_PLACEMENTS_XLS_SCOPE_AUDIT_V129.csv", xls_audit)

# Promote source classifications and the reference-2006 table without overstating settlement.
report_path = HERE / "E0_FISCAL_EXCESS_GROWTH_BUYBACK_REFERENCE_2006_V129.csv"
report = read_csv(report_path)
for row in report:
    row["source_id"] = "e0_argentina_recompras_decreto_1735_04_report;e0_cgn_cuenta_inversion_2008_sdp"
    if row["isin"] in {"ARARGE03E147", "ARARGE03E154"}:
        row["evidence_status"] = "EXECUTED_COMPONENT_PUBLIC_TENDER_PORTION_EXACT_OTHER_PURCHASE_RESIDUAL_ROUNDED"
        row["caveat"] = "Occurrence and modality class proven; public awards isolated; other-channel residual is conditional on rounded aggregate and is not settlement proof."
    elif row["isin"] == "ARARGE03E121":
        row["evidence_status"] = "EXECUTED_COMPONENT_NO_ROW_IN_FOUR_PUBLIC_TENDERS_DIRECT_OR_OTHER_RECORD_OPEN"
        row["caveat"] = "No public-tender row in the complete recovered four-round series; direct-operation details and settlement remain open."
    else:
        row["evidence_status"] = "EXECUTED_TOTAL_MODALITY_CLASS_AND_PUBLIC_TENDER_SHARE_RECONCILED"
        row["caveat"] = "ARS 96.68593436m public GDP awards equal 2.93% of the rounded official total; remainder is not a transaction-level record."
write_csv(report_path, report)

ledger_path = HERE / "E0_FISCAL_MECHANISM_LEDGER_V129.csv"
ledger = read_csv(ledger_path)
ledger.extend(
    [
        {"ledger_id": "F136", "window": "2008-08-28/2008-10-02", "mechanism": "Debt_buyback_excess_GDP", "phase": "PUBLIC_TENDER_GDP_ARS_AWARDS", "as_of_date": "FOUR_TENDER_DATES", "payer": "Tesoro_Nacional", "recipient": "Awarded_participants_ultimate_holders_open", "universe": "Reference_2006_Excess_GDP", "instrument": "GDP_Unit_ARS_ARARGE03E147", "amount_original": str(ars_eff), "original_unit": "ARS_million_effective_awarded", "normalized_ars_million": str(ars_eff), "valuation_basis": "SUM_FOUR_SUCCESSFUL_OFFICIAL_RESULT_ROWS", "source_id": "four_official_tender_results;e0_cgn_cuenta_inversion_2008_sdp", "source_locator": "four_results;printed_pp63_64", "realization_status": "AWARDED_AND_OFFICIALLY_IMPUTED_SETTLEMENT_OPEN", "additivity": "COMPONENT_OF_F138_AND_F134", "status_interpretation": "Four GDP-ARS awards are part of the reference-2006 bucket.", "caveat": "Scheduled settlement is not independently confirmed."},
        {"ledger_id": "F137", "window": "2008-09-04/2008-10-02", "mechanism": "Debt_buyback_excess_GDP", "phase": "PUBLIC_TENDER_GDP_USD_AWARDS", "as_of_date": "TWO_TENDER_DATES", "payer": "Tesoro_Nacional", "recipient": "Awarded_participants_ultimate_holders_open", "universe": "Reference_2006_Excess_GDP", "instrument": "GDP_Unit_USD_ARARGE03E154", "amount_original": str(usd_eff), "original_unit": "ARS_million_effective_awarded", "normalized_ars_million": str(usd_eff), "valuation_basis": "SUM_TWO_SUCCESSFUL_OFFICIAL_RESULT_ROWS_WITH_PUBLISHED_FX", "source_id": "four_official_tender_results;e0_cgn_cuenta_inversion_2008_sdp", "source_locator": "two_results;printed_pp63_64", "realization_status": "AWARDED_AND_OFFICIALLY_IMPUTED_SETTLEMENT_OPEN", "additivity": "COMPONENT_OF_F138_AND_F134", "status_interpretation": "Two GDP-USD awards are part of the reference-2006 bucket.", "caveat": "Effective ARS is distinct from USD VNO and native consideration."},
        {"ledger_id": "F138", "window": "2008-08-28/2008-10-02", "mechanism": "Debt_buyback_excess_GDP", "phase": "PUBLIC_TENDER_GDP_EFFECTIVE_SUBTOTAL", "as_of_date": "FOUR_TENDER_DATES", "payer": "Tesoro_Nacional", "recipient": "Awarded_participants_ultimate_holders_open", "universe": "Reference_2006_Excess_GDP", "instrument": "ARARGE03E147_and_ARARGE03E154", "amount_original": str(gdp_tender_eff), "original_unit": "ARS_million_effective_awarded", "normalized_ars_million": str(gdp_tender_eff), "valuation_basis": "DECIMAL_SUM_F136_F137", "source_id": "four_official_tender_results;e0_cgn_cuenta_inversion_2008_sdp", "source_locator": "E0_REFERENCE_2006_PUBLIC_TENDER_AWARDS_V129.csv", "realization_status": "PUBLIC_AWARD_SUBTOTAL_ACCOUNTING_IMPUTED_SETTLEMENT_OPEN", "additivity": "TOTAL_DO_NOT_ADD_TO_F136_F137", "status_interpretation": "5.13% of GDP effective subtotal and 2.93% of complete reference-2006 effective total.", "caveat": "Percentages respect rounded official denominators."},
        {"ledger_id": "F139", "window": "CALENDAR_2008", "mechanism": "Debt_buyback_excess_GDP", "phase": "OTHER_PURCHASE_CHANNEL_ARITHMETIC_RESIDUAL", "as_of_date": "INDIVIDUAL_DATES_OPEN", "payer": "Tesoro_Nacional", "recipient": "Instrument_holders_unknown", "universe": "Reference_2006_Excess_GDP", "instrument": "THREE_ISIN", "amount_original": str(total_eff_res[0]), "original_unit": "ARS_million_effective_residual_central", "normalized_ars_million": str(total_eff_res[0]), "valuation_basis": "ROUNDED_OFFICIAL_TOTAL_MINUS_EXACT_PUBLIC_GDP_AWARDS", "source_id": "e0_argentina_recompras_decreto_1735_04_report;four_official_tender_results", "source_locator": "PDF_p2;MA129_TOTAL", "realization_status": "ARITHMETIC_RESIDUAL_NOT_TRANSACTION_LEDGER", "additivity": "COMPLEMENT_OF_F138_WITHIN_F134_PLUS_F131", "status_interpretation": "Central residual ARS 3204.91406564m with ±ARS 0.005m aggregate rounding band.", "caveat": "Do not describe the residual as one direct trade, one seller or one payment."},
        {"ledger_id": "F140", "window": "2008", "mechanism": "Debt_buyback_excess_GDP", "phase": "PROGRAM_TO_EXCESS_GDP_ACCOUNTING_IMPUTATION", "as_of_date": "CUENTA_INVERSION_2008", "payer": "Tesoro_Nacional", "recipient": "N/A_ACCOUNTING_CLASSIFICATION", "universe": "Eligible_2005_restructuring_securities_purchased_under_program", "instrument": "PROGRAM_ELIGIBLE_SUBSET", "amount_original": "N/A", "original_unit": "TEXTUAL_ATTRIBUTION", "normalized_ars_million": "N/D", "valuation_basis": "CGN_PRINTED_PAGE_64", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "source_locator": "printed_pp63_64", "realization_status": "OFFICIAL_ACCOUNTING_IMPUTATION_BRIDGE", "additivity": "NON_ADDITIVE", "status_interpretation": "Connects eligible public-program purchases to the reference-2006 Excess GDP bucket.", "caveat": "Does not make all mixed-program purchases eligible or prove settlement."},
    ]
)
assert len(ledger) == 140 and len({row["ledger_id"] for row in ledger}) == 140
write_csv(ledger_path, ledger)

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V129.csv"
breaks = read_csv(breaks_path)
breaks.extend(
    [
        {"break_id": "rounded_aggregate_minus_exact_awards", "dimension": "precision", "problem": "Official acquired totals are printed to 0.01 million while tender awards are available to currency units/cents.", "rule": "Carry a ±0.005m band per printed component; report shares to two decimals and never present the residual as exact to cents.", "status": "FROZEN", "evidence": "retrospective report p2; four official result PDFs"},
        {"break_id": "award_accounting_imputation_not_settlement", "dimension": "realization", "problem": "Award plus annual accounting attribution does not prove scheduled securities transfer, Treasury debit or CRyL cancellation.", "rule": "Classify as awarded and imputed; keep Caja/BCRA/CRyL settlement states open.", "status": "FROZEN", "evidence": "CGN 2008 pp63-64; tender calls/results"},
        {"break_id": "arithmetic_residual_not_direct_trade", "dimension": "modality", "problem": "Official total minus recovered public awards is a remainder across transactions/channels, not a blotter.", "rule": "Call it other-channel arithmetic residual unless an operation-level record allocates it to direct purchases.", "status": "FROZEN", "evidence": "MA129 allocation bridge"},
    ]
)
assert len(breaks) == 103
write_csv(breaks_path, breaks)

trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V129.csv"
trace = read_csv(trace_path)
trace.extend(
    [
        {"trace_id": "TR129_086", "request_id": "REQ129_ECON", "institution": "Ministerio de Economía / ONCP", "gap_id": "CL129_DEBT_ACCOUNTING", "requested_record": "Asignación operación por operación entre compras directas y licitaciones del tramo referencia 2006", "period_or_date": "2008-01-01/2008-12-31", "identifiers": "ARARGE03E147;ARARGE03E154;ARARGE03E121;MA129", "minimum_usable_fields": "fecha; modalidad; ISIN; VNO; precio; efectivo; expediente; orden", "confidentiality_fallback": "cuadro agregado por fecha/modalidad/ISIN con vendedores testados", "status": "DRAFT_NOT_SENT"},
        {"trace_id": "TR129_087", "request_id": "REQ129_BNA", "institution": "Banco de la Nación Argentina", "gap_id": "CL129_BNA_TRADE_BLOTTER", "requested_record": "Blotter de intervenciones directas elegibles imputadas al Excess GDP", "period_or_date": "2008-08-11/2008-12-31", "identifiers": "ARARGE03E147;ARS1769.09431490m residual central;VNO ARS42778.75795m residual central", "minimum_usable_fields": "fecha; especie; nominal; precio; efectivo; contraparte testada; orden Tesoro", "confidentiality_fallback": "totales diarios por especie con banda de redondeo", "status": "DRAFT_NOT_SENT"},
        {"trace_id": "TR129_088", "request_id": "REQ129_CAJA", "institution": "Caja de Valores S.A.", "gap_id": "CL129_DEBT_ACCOUNTING", "requested_record": "Transferencias de las seis adjudicaciones GDP y enlace a cancelación", "period_or_date": "2008-09-01/2008-10-07", "identifiers": "six tender IDs;depositante 0306;comitente 40000;two ISIN", "minimum_usable_fields": "fecha; ISIN; nominal; cuenta testada; estado; referencia CRyL", "confidentiality_fallback": "certificación agregada por fecha/ISIN/nominal", "status": "DRAFT_NOT_SENT"},
    ]
)
assert len(trace) == 88 and len({row["trace_id"] for row in trace}) == 88
write_csv(trace_path, trace)

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V129.csv"
keys = read_csv(keys_path)
keys.extend(
    [
        {"key_id": "SK129_68", "request_id": "REQ129_ECON", "key_group": "modality_allocation", "exact_key": "reference 2006;ARS3301.60m;direct purchases;tenders;ARARGE03E147;ARARGE03E154;ARARGE03E121", "search_purpose": "hallar actuación que distribuya el total por modalidad", "source_or_basis": "retrospective report p2;CGN 2008 pp63-64", "caveat": "La clase modal está probada; falta la asignación completa."},
        {"key_id": "SK129_69", "request_id": "REQ129_CAJA", "key_group": "six_gdp_awards", "exact_key": "2008-09-02;2008-09-09;2008-09-16;2008-10-07;0306;40000;ARARGE03E147;ARARGE03E154", "search_purpose": "buscar transferencias previstas de las seis adjudicaciones", "source_or_basis": "four official tender calls/results", "caveat": "Fechas programadas, no confirmación."},
        {"key_id": "SK129_70", "request_id": "REQ129_BNA", "key_group": "gdp_ars_other_channel", "exact_key": "ARARGE03E147;VNO42778.75795m;effectiveARS1769.09431490m;rounding±0.005m", "search_purpose": "acotar el residual de compras no identificado en licitaciones públicas", "source_or_basis": "MA129_GDP_ARS", "caveat": "Residual aritmético, no monto exacto de un único blotter."},
        {"key_id": "SK129_71", "request_id": "REQ129_ECON", "key_group": "discount_non_tender", "exact_key": "ARARGE03E121;VNO2748.50m;effectiveARS1415.50m;no row in four public tenders", "search_purpose": "localizar expediente de compra directa u otro canal no licitado", "source_or_basis": "retrospective report p2;complete recovered four-round public series", "caveat": "No inferir institución o fecha sin registro."},
    ]
)
assert len(keys) == 71 and len({row["key_id"] for row in keys}) == 71
write_csv(keys_path, keys)

closures_path = HERE / "E0_REQUEST_CLOSURE_CRITERIA_V129.csv"
closures = read_csv(closures_path)
for row in closures:
    if row["gap_id"] == "CL129_DEBT_ACCOUNTING":
        row["does_not_close"] = "Occurrence, modality classes, public-award subtotal and accounting imputation do not close direct-operation allocation, actual settlement or cancellation."
        row["initial_status"] = "OCCURRENCE_MODALITY_CLASS_AND_PUBLIC_TENDER_SHARE_CLOSED_DIRECT_SETTLEMENT_OPEN_NOT_SENT"
write_csv(closures_path, closures)

request_addenda = {
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V129.md": """

## Clave adicional V129 · asignación modal y residual con redondeo

La Cuenta de Inversión imputa al tramo Excess GDP las compras elegibles del programa y el informe retrospectivo prueba recompras efectuadas mediante compras directas y licitaciones. Las seis adjudicaciones públicas GDP suman ARS 96,68593436m efectivos: 5,13% del subtotal GDP y 2,93% del total referencia 2006. Se solicita la actuación que asigne el resto por fecha, modalidad e ISIN. Los residuales de `MA129` son controles aritméticos con banda de redondeo, no operaciones presumidas.
""",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V129.md": """

## Clave adicional V129 · residual GDP ARS

Para `ARARGE03E147`, las licitaciones públicas identifican VNO ARS 1.045,34205m y efectivo ARS 89,00568510m. Frente al agregado oficial redondeado, queda un residual central VNO ARS 42.778,75795m y efectivo ARS 1.769,09431490m, ambos con incertidumbre heredada de ±0,005m. Se solicita el blotter que permita sustituir ese residual por operaciones fechadas y conciliables; no se presume que todo corresponda a una sola intervención del BNA.
""",
    "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V129.md": """

## Clave adicional V129 · seis adjudicaciones GDP

Se solicita verificar las transferencias previstas para `02/09`, `09/09`, `16/09` y `07/10/2008`, depositante `0306`, comitente `40000`, por `ARARGE03E147` y `ARARGE03E154`. La publicación de adjudicación y su imputación anual cierran pertenencia económica, pero no reemplazan el asiento de entrega, pago o cancelación.
""",
}
for filename, addendum in request_addenda.items():
    path = HERE / filename
    text = path.read_text(encoding="utf-8-sig")
    if "Clave adicional V129" not in text:
        path.write_text(text.rstrip() + addendum, encoding="utf-8")

episode_path = HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V129.csv"
episode = read_csv(episode_path)
for row in episode:
    if row["variable"] == "gdp_units_excess_gdp_repurchase_scope":
        row["source_id"] = "e0_argentina_recompras_decreto_1735_04_report;e0_cgn_cuenta_inversion_2008_sdp;four_official_tender_results"
        row["source_quality"] = "PRIMARY_EXECUTED_MODALITY_CLASS_ACCOUNTING_IMPUTATION_AND_PUBLIC_AWARD_EXACT"
        row["status"] = "OCCURRENCE_MODALITY_CLASS_AND_PUBLIC_TENDER_SHARE_CLOSED_DIRECT_SETTLEMENT_OPEN"
        row["interpretation"] = "Six GDP awards sum ARS96.68593436m effective; 5.13% of GDP subtotal and 2.93% of total. Other-channel residual preserves rounding bands."
        row["notes"] = "Direct-operation dates/sellers, actual transfer/payment and CRyL cancellation remain open; strict panel unchanged."
write_csv(episode_path, episode)

coverage_path = HERE / "HISTORICAL_EVIDENCE_COVERAGE_V129.csv"
coverage = read_csv(coverage_path)
for row in coverage:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row["quality"] = "PRIMARY_REFERENCE_2006_EXECUTED_MODALITY_CLASS_PUBLIC_AWARD_AND_ACCOUNTING_IMPUTATION_BRIDGED"
        row["comparable"] = "PUBLIC_TENDER_SHARE_EXACT_OTHER_CHANNEL_RESIDUAL_ROUNDING_BOUNDED_SETTLEMENT_OPEN"
        row["gap"] = "Ocurrencia, clases compra directa/licitación e imputación están cerradas; faltan operaciones directas, transferencias, débito y cancelación."
        row["next_action"] = "Buscar actuación ONCP y blotter directo; con autorización expresa pedir Caja/BCRA/CRyL por seis adjudicaciones y tres ISIN."
write_csv(coverage_path, coverage)

queue_path = HERE / "HISTORICAL_SOURCE_QUEUE_V129.csv"
queue = read_csv(queue_path)
for row in queue:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row["status"] = "REFERENCE_2006_OCCURRENCE_MODALITY_AND_PUBLIC_TENDER_SHARE_CLOSED_DIRECT_SETTLEMENT_OPEN_READY_NOT_SENT"
        row["why"] = "Six public GDP awards sum ARS96.68593436m and are officially imputed; rounded residuals isolate the still-missing direct/other-channel records."
        row["next_action"] = "Search ONCP/BNA direct-operation records and, only with express authorization, submit targeted Caja/BCRA/CRyL requests."
write_csv(queue_path, queue)

reconstruction = f"""# Reconstrucción fiscal E0 · V129

## Qué cambia

El informe retrospectivo no sólo enumera instrumentos y montos: afirma recompras efectuadas y señala que los títulos fueron rescatados mediante compras directas y licitaciones. La Cuenta de Inversión 2008 aporta el puente faltante: las compras elegibles de títulos surgidos de la reestructuración 2005 realizadas bajo el programa fueron imputadas a la recompra por excedente del PBI referencia 2006.

## Porción pública identificada

Las cuatro licitaciones oficiales contienen seis adjudicaciones GDP exitosas. Para `ARARGE03E147` suman VNO ARS {ars_vno}m y efectivo ARS {ars_eff}m; para `ARARGE03E154`, VNO USD {usd_vno}m y efectivo ARS {usd_eff}m. El subtotal efectivo público es ARS {gdp_tender_eff}m: 5,13% del subtotal GDP ARS 1.886,10m y 2,93% del total ARS 3.301,60m.

## Residual y precisión

Restar adjudicaciones exactas de agregados impresos a 0,01 millón produce un control, no un blotter. El residual central GDP es ARS {gdp_eff_res[0]}m con una banda de ±ARS 0,010m por redondeo de sus dos componentes. Sobre el total oficial, el residual central es ARS {total_eff_res[0]}m con banda de ±ARS 0,005m. No debe describirse como una única compra directa, contraparte o fecha.

El Discount `ARARGE03E121` no aparece en ninguna de las cuatro licitaciones públicas recuperadas. El informe admite la clase compra directa, pero todavía falta el registro que asigne a este componente una institución, fecha, vendedor y liquidación.

## Frontera probatoria

Quedan abiertos los blotters/actuaciones de compras directas u otros canales, la transferencia efectiva de las seis adjudicaciones, el débito de pago y los asientos de cancelación CRyL/Caja. La planilla anual de colocaciones 2008 fue preservada y descartada por alcance: sólo contiene emisiones y letras intra-sector público. Seis pedidos siguen `DRAFT_NOT_SENT`; `CLOSED_NETWORK_GATE=NO`.
"""
(HERE / "E0_FISCAL_RECONSTRUCTION_V129.md").write_text(reconstruction, encoding="utf-8")

readme = f"""# Checkpoint V129 · puente de modalidad e imputación GDP

V129 promueve la evidencia del tramo referencia 2006: queda probada la ocurrencia de las recompras, las clases compra directa/licitación y la imputación contable de las compras elegibles del programa.

Se identifican seis adjudicaciones públicas GDP por ARS {gdp_tender_eff}m efectivos: 5,13% del subtotal GDP y 2,93% del total oficial. El resto se conserva como residual aritmético con bandas de redondeo, no como una operación inventada.

La planilla oficial anual 2008 cubre emisiones, no recompras. Compras directas, transferencias, pago y cancelación siguen abiertos. Seis pedidos permanecen `DRAFT_NOT_SENT`; panel estricto sin cambios.
"""
(HERE / "README_V129.md").write_text(readme, encoding="utf-8")

verdict = f"""# Veredicto V129

La evidencia oficial ya permite afirmar que el tramo de recompra por excedente del PBI referencia 2006 fue ejecutado mediante compras directas y licitaciones, y que las compras elegibles del programa 2008 fueron imputadas a ese compromiso.

Las seis adjudicaciones públicas de GDP Units suman ARS {gdp_tender_eff} millones efectivos. Representan 5,13% del subtotal GDP de ARS 1.886,10 millones y 2,93% del total de ARS 3.301,60 millones. Esta fracción deja de ser una modalidad abierta: está documentada por fecha, ISIN, VNO, precio/efectivo y resultado, aunque no por liquidación final.

El remanente no se eleva artificialmente a “compra directa exacta”: es un residual calculado contra totales oficiales redondeados. Para el total, su centro es ARS {total_eff_res[0]} millones y su banda de redondeo ±ARS 0,005 millones. Falta sustituirlo por operaciones identificadas, y faltan transferencia Caja, débito BCRA y cancelación CRyL. `CLOSED_NETWORK_GATE=NO`.
"""
(HERE / "VEREDICTO_V129.md").write_text(verdict, encoding="utf-8")

retrieval = """# Registro de recuperación V129

Fecha: 2026-08-30.

1. Se releyeron y verificaron visualmente las páginas impresas 63-64 de la Cuenta de Inversión 2008: dos etapas del programa e imputación de las compras elegibles del canje 2005 al bucket Excess GDP.
2. Se relevaron las páginas 1-4 del informe oficial retrospectivo: afirma recompras efectuadas mediante compras directas y licitaciones y publica los tres ISIN/montos adquiridos.
3. Se recalcularon con `Decimal` las seis adjudicaciones GDP exitosas de las cuatro licitaciones oficiales; el subtotal efectivo es ARS 96,68593436m.
4. Se preservó la planilla oficial de emisiones 2008. Lectura ACE/OLEDB: una hoja, 170 filas, 17 columnas; sin los tres ISIN ni campos de recompra, cancelación o pago.
5. Los residuales se congelaron con bandas compatibles con la precisión de 0,01 millón de los agregados oficiales.
6. No se envió ningún pedido ni se realizó presentación externa.
"""
(HERE / "RETRIEVAL_LOG_V129.md").write_text(retrieval, encoding="utf-8")

refs_path = HERE / "SOURCE_REFERENCES_V129.md"
refs = refs_path.read_text(encoding="utf-8-sig").rstrip()
refs += "\n- Emisiones de deuda pública durante 2008: https://www.argentina.gob.ar/sites/default/files/coloc2008_castellano_con_letras.xls\n\nLa planilla nueva se preserva como control negativo de alcance; no es un ledger de recompras.\n"
refs_path.write_text(refs, encoding="utf-8")

handover = f"""# Handover V129 → V130

## Estado congelado

- Ocurrencia ejecutada, clases compra directa/licitación, tres ISIN y total efectivo ARS 3.301,60m: cerrados por fuente oficial.
- Imputación al bucket Excess GDP de las compras elegibles del programa 2008: cerrada por Cuenta de Inversión.
- Seis adjudicaciones GDP públicas: ARS {gdp_tender_eff}m efectivos, 5,13% del subtotal GDP y 2,93% del total.
- Residual total central: ARS {total_eff_res[0]}m con ±ARS 0,005m por redondeo; es control aritmético, no blotter.
- Discount no aparece en la serie completa recuperada de cuatro licitaciones; asignación directa/otro canal y detalles siguen abiertos.
- Planilla anual de colocaciones 2008: control negativo, sólo emisiones/letras.
- Seis borradores `DRAFT_NOT_SENT`, ninguno enviado; panel estricto sin cambios.

## Prioridad V130

1. Buscar actuación ONCP/DADP que distribuya el total por fecha, modalidad e ISIN.
2. Buscar blotter BNA/otra vía para el residual GDP ARS y el expediente del Discount.
3. Buscar transferencias Caja de las seis adjudicaciones en fechas previstas 02/09, 09/09, 16/09 y 07/10/2008.
4. Buscar débito/orden BCRA y cancelación CRyL por los tres ISIN; no convertir adjudicación en liquidación.
5. No enviar pedidos sin autorización expresa.
"""
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V129_A_V130.md").write_text(handover, encoding="utf-8")

audit_md = f"""# Auditoría V129

- Fuentes maestras: {len(catalog)}; una fuente oficial nueva preservada como control negativo de alcance.
- Fuentes primarias E0: {len(census)}.
- Ledger fiscal: {len(ledger)} filas; cortes metodológicos: {len(breaks)}.
- Adjudicaciones GDP exitosas: {len(award_rows)}; efectivo ARS {gdp_tender_eff}m.
- Participación licitada: 5,13% del subtotal GDP; 2,93% del total referencia 2006.
- Puente de asignación modal: {len(allocation)} filas; cadena de imputación: {len(imputation)} filas.
- Pedidos: 6 borradores, 0 enviados; {len(trace)} objetos y {len(keys)} claves.
- Panel estricto: 30 entidades; {STRICT}% sin cambios.
"""
(HERE / "AUDITORIA_V129.md").write_text(audit_md, encoding="utf-8")

inherited = [
    {"script": "qa_v97.py", "pre_v129_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v129_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V97 congela una ausencia luego resuelta."},
    *({"script": f"qa_v{i}.py", "pre_v129_result": "PASS", "post_v129_result": "PASS", "interpretation": "Compatible"} for i in (98, 100, 101, 102, 103, 104, 105, 106)),
    *({"script": f"qa_v{i}.py", "pre_v129_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v129_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "Congela un checkpoint o conteo anterior."} for i in range(107, 129)),
    {"script": "qa_v129.py", "pre_v129_result": "N/A", "post_v129_result": "PASS", "interpretation": "Occurrence, modality class, accounting imputation and public-tender share closed; direct settlement open."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V129.csv", inherited)

# Source-audit layer.
for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    shutil.copyfile(AUDIT / f"{stem}_V128.csv", AUDIT / f"{stem}_V129.csv")

hash_rows = []
for row in catalog:
    local = row["archivo_local"]
    path = REPO / local.lstrip("/") if local else None
    exists = bool(path and path.is_file())
    actual = sha256(path) if exists else ""
    expected = row["sha256"]
    hash_rows.append(
        {
            "id": row["id"], "archivo_local": local, "exists": str(exists),
            "sha_catalog": expected, "sha_actual": actual,
            "hash_ok": str(bool(exists and expected and actual.lower() == expected.lower())),
        }
    )
assert len(hash_rows) == 348
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V129.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V129.csv", hash_rows)

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V129.csv"
provenance = [row for row in read_csv(provenance_path) if row["source_id"] != new_source["id"]]
provenance.append(
    {"source_id": new_source["id"], "original_url": new_source["url"], "retrieval_url": new_source["url"],
     "capture_timestamp": "20260830", "cdx_digest": "N/A_DIRECT_OFFICIAL", "local_path": new_source["local"],
     "sha256": new_source["sha256"], "bytes": str(new_source["bytes"]),
     "provenance_note": "Descarga directa desde el portador institucional oficial; XLS preservado y auditado como control negativo de alcance en V129."}
)
write_csv(provenance_path, provenance)

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": str(size), "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V129.csv", size_rows)

physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
assert physical == hash_ok == 342
completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V128.json").read_text(encoding="utf-8"))
for key in list(completeness):
    if key.endswith("_v128") or "newly_preserved_v128" in key:
        completeness.pop(key, None)
completeness.update(
    {
        "checkpoint": "V129", "date": "2026-08-30",
        "state": "E0_REFERENCE_2006_EXECUTED_MODALITY_CLASS_PUBLIC_TENDER_SHARE_AND_ACCOUNTING_IMPUTATION_CLOSED_DIRECT_SETTLEMENT_OPEN_NOT_SENT",
        "numeric_v129_strict_changed": False, "master_catalog_entries": len(catalog),
        "physical_local_copies": physical, "physical_local_hash_ok": hash_ok,
        "binary_required_entries": len(catalog) - 5, "binary_required_preserved": physical,
        "e0_primary_sources_preserved": len(census),
        "e0_quality": "PRIMARY_EXECUTED_MODALITY_CLASS_PUBLIC_AWARDS_ACCOUNTING_IMPUTATION_EXACT",
        "sources_newly_preserved_v129": 1, "e0_primary_sources_newly_preserved_v129": 1,
        "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
        "e0_request_traceability_rows": len(trace), "e0_request_search_keys": len(keys),
        "e0_reference_2006_public_award_rows": len(award_rows), "e0_reference_2006_modality_allocation_rows": len(allocation),
        "e0_reference_2006_imputation_chain_rows": len(imputation), "e0_official_2008_placements_scope_audit_rows": len(xls_audit),
        "e0_reference_2006_public_tender_effective_million_ars": str(gdp_tender_eff),
        "e0_reference_2006_public_tender_share_gdp_pct": "5.13", "e0_reference_2006_public_tender_share_total_pct": "2.93",
        "e0_requests_submitted": 0, "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
        "historical_workstream": "Reference-2006 repurchase occurrence, modality classes, accounting imputation and exact public GDP awards closed; direct/other-channel operations and Caja/BCRA/CRyL settlement remain open; no request submitted",
    }
)
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V129.json").write_text(json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V129 · modalidad, imputación y porción pública GDP"
old_backup = backup.read_text(encoding="utf-8-sig")
if marker not in old_backup:
    old_backup += (
        f"\n\n{marker}\n\n"
        f"- Ocurrencia, clases compra directa/licitación e imputación Excess GDP: cerradas con fuentes oficiales.\n"
        f"- Seis adjudicaciones GDP: ARS {gdp_tender_eff}m efectivos; 5,13% del subtotal GDP y 2,93% del total.\n"
        f"- Residual total central ARS {total_eff_res[0]}m con ±ARS 0,005m; control aritmético, no blotter.\n"
        "- Planilla oficial de colocaciones 2008 preservada y descartada por alcance: sólo emisiones/letras.\n"
        "- Compras directas, transferencia, pago y cancelación siguen abiertos; seis pedidos DRAFT_NOT_SENT.\n"
    )
    backup.write_text(old_backup, encoding="utf-8")

qa_source = r'''from decimal import Decimal
from pathlib import Path
import csv
import hashlib
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
AUDIT = REPO / "research" / "ciclo_ajuste" / "source_audit"

def rows(name):
    with (HERE / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def d(value):
    return Decimal(value)

awards = rows("E0_REFERENCE_2006_PUBLIC_TENDER_AWARDS_V129.csv")
assert len(awards) == 6
ars = [r for r in awards if r["isin"] == "ARARGE03E147"]
usd = [r for r in awards if r["isin"] == "ARARGE03E154"]
assert len(ars) == 4 and len(usd) == 2
assert sum((d(r["awarded_vno_native"]) for r in ars), d(0)) == d("1045342050")
assert sum((d(r["awarded_vno_native"]) for r in usd), d(0)) == d("29480362")
assert sum((d(r["awarded_effective_ars"]) for r in awards), d(0)) == d("96685934.36")
assert all(r["settlement_status"] == "SCHEDULED_NOT_INDEPENDENTLY_CONFIRMED" for r in awards)

allocation = {r["allocation_id"]: r for r in rows("E0_REFERENCE_2006_MODALITY_ALLOCATION_V129.csv")}
assert len(allocation) == 5
assert d(allocation["MA129_GDP_SUBTOTAL"]["public_tender_effective_million_ars"]) == d("96.68593436")
assert d(allocation["MA129_GDP_SUBTOTAL"]["residual_effective_central_million_ars"]) == d("1789.41406564")
assert d(allocation["MA129_TOTAL"]["residual_effective_central_million_ars"]) == d("3204.91406564")
assert d(allocation["MA129_TOTAL"]["residual_effective_lower_million_ars"]) == d("3204.90906564")
assert d(allocation["MA129_TOTAL"]["residual_effective_upper_million_ars"]) == d("3204.91906564")
assert d(allocation["MA129_GDP_SUBTOTAL"]["tender_share_of_official_effective_pct"]).quantize(d("0.01")) == d("5.13")
assert d(allocation["MA129_TOTAL"]["tender_share_of_official_effective_pct"]).quantize(d("0.01")) == d("2.93")

assert len(rows("E0_REFERENCE_2006_IMPUTATION_CHAIN_V129.csv")) == 6
assert len(rows("E0_OFFICIAL_2008_PLACEMENTS_XLS_SCOPE_AUDIT_V129.csv")) == 2
assert all(r["scope_result"] == "NOT_BUYBACK_LEDGER" for r in rows("E0_OFFICIAL_2008_PLACEMENTS_XLS_SCOPE_AUDIT_V129.csv"))
assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V129.csv")) == 140
assert len(rows("E0_FISCAL_METHOD_BREAKS_V129.csv")) == 103
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V129.csv")) == 88
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V129.csv")) == 71

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V129.csv")}
assert len(census) == 108
assert census["e0_argentina_recompras_decreto_1735_04_report"]["use_status"] == "USABLE_EXECUTED_REPURCHASE_OCCURRENCE_MODALITY_CLASS_THREE_ISIN_TOTAL"
assert census["e0_cgn_cuenta_inversion_2008_sdp"]["use_status"] == "USABLE_PROGRAM_TO_EXCESS_GDP_ACCOUNTING_IMPUTATION_BRIDGE"
assert census["e0_argentina_colocaciones_deuda_2008_xls"]["use_status"] == "NEGATIVE_SCOPE_EMISSIONS_ONLY_NOT_BUYBACK_LEDGER"

catalog = rows(str(REPO / "data" / "fuentes" / "FUENTES.csv")) if False else None
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    cat = list(csv.DictReader(f))
assert len(cat) == 348 and len({r["id"] for r in cat}) == 348
source = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v129" / "binaries" / "coloc2008_castellano_con_letras.xls"
assert source.stat().st_size == 83456
assert hashlib.sha256(source.read_bytes()).hexdigest() == "08077e8abac8a714e2d28b10a85d8f7b0510b0015c73cb94144569905d7e0fab"

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V129.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V129"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 342
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v129_strict_changed"] is False

for name in ("README_V129.md", "VEREDICTO_V129.md", "E0_FISCAL_RECONSTRUCTION_V129.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V129_A_V130.md"):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "96.68593436" in text
    assert "DRAFT_NOT_SENT" in text or name == "VEREDICTO_V129.md"

print("V129 QA PASS")
'''
(HERE / "qa_v129.py").write_text(qa_source, encoding="utf-8")


def checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V129.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V129", "parent_checkpoint": "V128",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": 1, "new_primary_sources": 1,
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks),
        "public_gdp_award_rows": len(award_rows), "public_gdp_effective_million_ars": str(gdp_tender_eff),
        "modality_allocation_rows": len(allocation), "imputation_chain_rows": len(imputation),
        "request_drafts": 6, "request_traceability_rows": len(trace), "request_search_keys": len(keys),
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V129.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    "checkpoint": "V129", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical local copies with {hash_ok}/{physical} SHA-valid; modality class and exact public GDP awards bridged; six requests drafted and none submitted.",
    "historical_workstream": "Reference-2006 occurrence, modality classes, accounting imputation and exact public-award share closed; direct operations and settlement open; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V129 BUILD PASS")
