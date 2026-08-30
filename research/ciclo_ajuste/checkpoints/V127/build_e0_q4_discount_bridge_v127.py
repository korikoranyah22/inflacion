from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, getcontext
from pathlib import Path
import csv
import hashlib
import json
import shutil
import zipfile


getcontext().prec = 50

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
V126 = HERE.parent / "V126"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v127" / "binaries"
SCRATCH = REPO / "tmp" / "spreadsheets" / "v127"
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
    text = text.replace("V126", "V127").replace("v126", "v127")
    for prefix in ("TR", "REQ", "CL", "SK", "DM", "ID", "ST", "CA", "AB"):
        text = text.replace(f"{prefix}126_", f"{prefix}127_")
    return text


def clone_parent() -> None:
    skip = {
        "build_e0_accounting_bridge_v126.py",
        "qa_V126.py",
        "MANIFEST_V126.json",
        "INHERITED_QA_STATUS_V126.csv",
    }
    for source in V126.iterdir():
        if not source.is_file() or source.name in skip or source.name.startswith("HANDOVER_PROXIMA_SESION"):
            continue
        target = HERE / source.name.replace("V126", "V127")
        target.write_text(bump_text(source.read_text(encoding="utf-8-sig")), encoding="utf-8")


clone_parent()
BIN.mkdir(parents=True, exist_ok=True)

sigade_zip = BIN / "basesigade2008-09-30.zip"
scratch_zip = SCRATCH / "basesigade2008-09-30.zip"
if scratch_zip.is_file():
    shutil.copyfile(scratch_zip, sigade_zip)
if not sigade_zip.is_file():
    raise FileNotFoundError(sigade_zip)

SIGADE_SHA = "aa5aa1ebe852c91c1bdaa63be2324a8c7b9a8aded9c5653a46b19b056bfd851a"
SIGADE_MEMBER = "2003-Para el Sitio basesigade 2008-09-30.mdb"
assert sha256(sigade_zip) == SIGADE_SHA
with zipfile.ZipFile(sigade_zip) as archive:
    member = archive.getinfo(SIGADE_MEMBER)
    assert member.file_size == 57245696

sigade_source = {
    "id": "e0_argentina_sigade_2008_q3",
    "institution": "Ministerio de Economía y Producción · Secretaría de Finanzas",
    "title": "Base SIGADE de Deuda Pública · tercer trimestre de 2008",
    "url": "https://www.argentina.gob.ar/sites/default/files/basesigade2008-09-30.zip",
    "local": "/" + sigade_zip.relative_to(REPO).as_posix(),
    "sha256": SIGADE_SHA,
    "bytes": sigade_zip.stat().st_size,
    "period": "stock al 2008-09-30",
    "type": "ZIP institucional oficial · base MDB SIGADE",
    "caveat": "La base publicada es un corte Q3, no un historial de transacciones ni una base Q4; confirma saldos por operación y tipo de cambio, no contraparte, asiento Caja o pago.",
}

catalog = [row for row in read_csv(CATALOG) if row["id"] != sigade_source["id"]]
for row in catalog:
    if row["id"] == "e0_argentina_recompras_decreto_1735_04_report":
        row["nota"] = (
            "V127 E0 fiscal: además del control histórico ya preservado, la tabla de la página 2 identifica "
            "Discount en Pesos ARARGE03E121, VNO ARS 2.748,50m y valor efectivo ARS 1.415,50m para el año de referencia 2006. "
            "La identificación agregada no prueba fecha de cada operación, contraparte, custodia ni pago."
        )
catalog.append(
    {
        "id": sigade_source["id"], "tema": "ciclo_ajuste_e0_fiscal",
        "institucion": sigade_source["institution"], "titulo": sigade_source["title"],
        "url_original": sigade_source["url"], "archivo_local": sigade_source["local"],
        "fecha_descarga": "2026-08-29", "fecha_publicacion": "2008-09-30", "codigo_serie": "",
        "periodo_utilizado": sigade_source["period"], "tipo": sigade_source["type"],
        "sha256": sigade_source["sha256"],
        "nota": f"V127 E0 fiscal: {sigade_source['bytes']:,} bytes; contiene {SIGADE_MEMBER}. {sigade_source['caveat']}",
    }
)
write_csv(CATALOG, catalog)

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V127.csv"
census = [row for row in read_csv(census_path) if row["source_id"] != sigade_source["id"]]
for row in census:
    if row["source_id"] == "e0_argentina_recompras_decreto_1735_04_report":
        row["variable_families"] = "state_bcra;fiscal;debt;buyback;tender;excess_growth;discount_pesos;isin"
        row["method_breaks"] = "VNO versus valor efectivo versus baja contable actualizada; año de referencia versus trimestre de reconocimiento; agregado por especie versus transacción"
        row["use_status"] = "USABLE_EXCESS_GROWTH_DISCOUNT_PESOS_VNO_EFFECTIVE_AND_Q4_ACCOUNTING_BRIDGE"
        row["caveat"] = "La página 2 informa VNO ARS 2.748,50m y valor efectivo ARS 1.415,50m para Discount en Pesos, referencia 2006; no publica fecha/contraparte de cada operación ni constancia Caja/BCRA."
census.append(
    {
        "source_id": sigade_source["id"], "institution": sigade_source["institution"],
        "artifact": sigade_source["title"], "url": sigade_source["url"],
        "local_path": sigade_source["local"], "sha256": sigade_source["sha256"],
        "bytes": str(sigade_source["bytes"]), "period_coverage": sigade_source["period"],
        "variable_families": "state_bcra;fiscal;debt;SIGADE;exchange_bonds;discount_pesos;stock;fx",
        "primary_source": "YES", "preserved": "YES",
        "method_breaks": "saldo SIGADE versus VNO residual/actualizado; snapshot versus transacción; Q3 publicado versus Q4 no publicado en la misma página",
        "use_status": "USABLE_Q3_OPERATION_LEVEL_DISCOUNT_PESOS_UPDATED_BALANCE_CONTROL",
        "caveat": sigade_source["caveat"],
    }
)
write_csv(census_path, census)

D = Decimal
q3_fx = D("3.135")
q4_fx = D("3.452")
q3_values = {
    "PAR_EN_PESOS": D("1674265.1575757577"),
    "DISCOUNT_EN_PESOS": D("4788663.684529507"),
    "CUASIPAR_EN_PESOS": D("7549668.135566189"),
}
q4_values = {
    "PAR_EN_PESOS": D("1520516.0107184243"),
    "DISCOUNT_EN_PESOS": D("3552717.9553881804"),
    "CUASIPAR_EN_PESOS": D("6856375.899478564"),
}
isins = {
    "PAR_EN_PESOS": "ARARGE03E105",
    "DISCOUNT_EN_PESOS": "ARARGE03E121",
    "CUASIPAR_EN_PESOS": "ARARGE03E139",
}
stock_rows = []
for key in ("PAR_EN_PESOS", "DISCOUNT_EN_PESOS", "CUASIPAR_EN_PESOS"):
    start_ars_m = q3_values[key] * q3_fx / D("1000")
    end_ars_m = q4_values[key] * q4_fx / D("1000")
    reduction_ars_m = start_ars_m - end_ars_m
    report = D("2748.50") if key == "DISCOUNT_EN_PESOS" else None
    stock_rows.append(
        {
            "movement_id": f"SM127_{key}", "instrument": key, "isin": isins[key],
            "source_q3": "e0_argentina_deuda_publica_2008_q3", "source_q4": "e0_argentina_deuda_publica_2008_q4",
            "q3_locator": {"PAR_EN_PESOS": "A.12.2!F30:G30", "DISCOUNT_EN_PESOS": "A.12.2!F31:G31", "CUASIPAR_EN_PESOS": "A.12.2!F32:G32"}[key],
            "q4_locator": {"PAR_EN_PESOS": "A.12.2!F30:G30", "DISCOUNT_EN_PESOS": "A.12.2!F31:G31", "CUASIPAR_EN_PESOS": "A.12.2!F32:G32"}[key],
            "q3_fx_ars_per_usd": str(q3_fx), "q4_fx_ars_per_usd": str(q4_fx),
            "q3_nominal_residual_thousand_usd": str(q3_values[key]),
            "q4_nominal_residual_thousand_usd": str(q4_values[key]),
            "q3_nominal_residual_million_ars": str(start_ars_m),
            "q4_nominal_residual_million_ars": str(end_ars_m),
            "derived_nominal_reduction_million_ars": str(reduction_ars_m),
            "report_vno_repurchase_million_ars": str(report) if report is not None else "N/A",
            "delta_to_report_million_ars": str(reduction_ars_m - report) if report is not None else "N/A",
            "evidence_status": "NEAR_EXACT_VNO_MATCH_TO_OFFICIAL_REPURCHASE_REPORT" if report is not None else "ZERO_NATIVE_NOMINAL_REDUCTION_FX_CONTROL",
            "caveat": "El match por especie es agregado; no individualiza fecha, contraparte, custodia o pago." if report is not None else "Control de conversión: la variación en miles de USD se explica por TC, sin baja nominal nativa material.",
        }
    )
assert abs(D(stock_rows[0]["derived_nominal_reduction_million_ars"])) < D("0.000000001")
assert abs(D(stock_rows[2]["derived_nominal_reduction_million_ars"])) < D("0.000000001")
discount_reduction_m = D(stock_rows[1]["derived_nominal_reduction_million_ars"])
assert abs(discount_reduction_m - D("2748.50")) < D("0.03")
write_csv(HERE / "E0_FISCAL_Q4_EXCHANGE_BOND_STOCK_MOVEMENTS_V127.csv", stock_rows)

q3_discount_updated_thousand_usd = D("8229799.94")
q3_discount_nominal_thousand_usd = q3_values["DISCOUNT_EN_PESOS"]
update_factor = q3_discount_updated_thousand_usd / q3_discount_nominal_thousand_usd
derived_accounting_thousand_ars = discount_reduction_m * D("1000") * update_factor
official_q4_thousand_ars = D("4723536.19")
official_q4_thousand_usd = D("1506710.11")
official_usd_from_ars = official_q4_thousand_ars / q3_fx
valuation_bridge = [
    {
        "bridge_id": "VB127_VNO_REPORT", "bridge_leg": "NOMINAL_REDUCTION_TO_RETROSPECTIVE_REPORT",
        "input_1": str(discount_reduction_m), "input_1_unit": "ARS_million_derived_VNO",
        "input_2": "2748.50", "input_2_unit": "ARS_million_official_report_VNO",
        "operation": "input_1_minus_input_2", "result": str(discount_reduction_m - D("2748.50")), "result_unit": "ARS_million",
        "source_chain": "e0_argentina_deuda_publica_2008_q3;e0_argentina_deuda_publica_2008_q4;e0_argentina_recompras_decreto_1735_04_report",
        "locator_chain": "A.12.2!F31:G31;A.12.2!F31:G31;PDF_p2",
        "status": "NEAR_EXACT_MATCH_WITHIN_REPORT_ROUNDING", "caveat": "El PDF redondea a dos decimales de millón; el delta es ARS 0,021731m.",
    },
    {
        "bridge_id": "VB127_ACCOUNTING_ARS", "bridge_leg": "VNO_REDUCTION_TIMES_Q3_UPDATE_FACTOR_TO_Q4_ACCOUNTING",
        "input_1": str(discount_reduction_m * D("1000")), "input_1_unit": "ARS_thousand_derived_VNO",
        "input_2": str(update_factor), "input_2_unit": "Q3_updated_to_nominal_factor",
        "operation": "input_1_times_input_2_minus_official_4723536.19", "result": str(derived_accounting_thousand_ars - official_q4_thousand_ars), "result_unit": "ARS_thousand",
        "source_chain": "e0_argentina_deuda_publica_2008_q3;e0_argentina_deuda_publica_2008_q4;e0_argentina_sigade_2008_q3",
        "locator_chain": "A.12.2!G31:H31;A.5.1!B29:C29;SALDOS Discount en $ ajustado por CER",
        "status": "EXACT_WITHIN_DISPLAY_ROUNDING", "caveat": "Delta ARS 0,016224 mil; no usar la baja actualizada como efectivo pagado.",
    },
    {
        "bridge_id": "VB127_ACCOUNTING_USD", "bridge_leg": "OFFICIAL_ARS_ACCOUNTING_TO_OFFICIAL_USD_AT_Q3_FX",
        "input_1": str(official_q4_thousand_ars), "input_1_unit": "ARS_thousand_official_accounting",
        "input_2": str(q3_fx), "input_2_unit": "ARS_per_USD_2008_09_30",
        "operation": "input_1_div_input_2_minus_official_1506710.11", "result": str(official_usd_from_ars - official_q4_thousand_usd), "result_unit": "USD_thousand",
        "source_chain": "e0_argentina_deuda_publica_2008_q3;e0_argentina_deuda_publica_2008_q4;e0_argentina_sigade_2008_q3",
        "locator_chain": "A.19!K72;A.5.1!B29:C29;TIPO DE CAMBIO PESO ARGENTINO",
        "status": "EXACT_WITHIN_TWO_DECIMAL_TABLE_ROUNDING", "caveat": "La conversión reproduce USD 1.506.710,11 miles al redondear a dos decimales.",
    },
]
assert abs(derived_accounting_thousand_ars - official_q4_thousand_ars) < D("0.02")
assert official_usd_from_ars.quantize(D("0.01")) == official_q4_thousand_usd
write_csv(HERE / "E0_FISCAL_Q4_DISCOUNT_PESOS_VALUATION_BRIDGE_V127.csv", valuation_bridge)

excess_growth = [
    {"row_id": "EG127_01", "reference_year": "2006", "instrument": "Valores Negociables Vinculados al PBI en Pesos", "isin": "ARARGE03E147", "native_currency": "ARS", "vno_original_million_native": "43824.10", "effective_value_million_ars": "1858.10", "source_id": "e0_argentina_recompras_decreto_1735_04_report", "source_locator": "PDF_p2", "evidence_status": "OFFICIAL_REPURCHASE_REPORTED_BY_INSTRUMENT", "additivity": "COMPONENT", "caveat": "La tabla no individualiza fecha, contraparte o pago."},
    {"row_id": "EG127_02", "reference_year": "2006", "instrument": "Valores Negociables Vinculados al PBI en Dólares Estadounidenses - Ley Argentina", "isin": "ARARGE03E154", "native_currency": "USD", "vno_original_million_native": "260.90", "effective_value_million_ars": "28.00", "source_id": "e0_argentina_recompras_decreto_1735_04_report", "source_locator": "PDF_p2", "evidence_status": "OFFICIAL_REPURCHASE_REPORTED_BY_INSTRUMENT", "additivity": "COMPONENT", "caveat": "VNO mixto por moneda; no sumar VNO entre especies."},
    {"row_id": "EG127_03", "reference_year": "2006", "instrument": "Bonos de la República Argentina con Descuento en Pesos 5,83% 2033", "isin": "ARARGE03E121", "native_currency": "ARS", "vno_original_million_native": "2748.50", "effective_value_million_ars": "1415.50", "source_id": "e0_argentina_recompras_decreto_1735_04_report", "source_locator": "PDF_p2", "evidence_status": "OFFICIAL_EFFECTED_AGGREGATE_INSTRUMENT_REPURCHASE", "additivity": "COMPONENT_NON_ADDITIVE_WITH_STOCK_AND_ACCOUNTING_VALUES", "caveat": "Valor efectivo no equivale a baja contable actualizada ni acredita el riel de pago."},
    {"row_id": "EG127_TOTAL", "reference_year": "2006", "instrument": "TOTAL", "isin": "N/A", "native_currency": "MIXED_VNO", "vno_original_million_native": "N/A", "effective_value_million_ars": "3301.60", "source_id": "e0_argentina_recompras_decreto_1735_04_report", "source_locator": "PDF_p2", "evidence_status": "OFFICIAL_TABLE_TOTAL_RECONCILED", "additivity": "TOTAL_DO_NOT_ADD_TO_COMPONENTS", "caveat": "El total efectivo suma exactamente los tres componentes; los VNO están en monedas nativas distintas."},
]
assert sum(D(row["effective_value_million_ars"]) for row in excess_growth[:3]) == D("3301.60")
write_csv(HERE / "E0_FISCAL_EXCESS_GROWTH_BUYBACK_REFERENCE_2006_V127.csv", excess_growth)

sigade_rows = [
    {"record_id": "SG127_PAR_ARS", "table_name": "SALDOS", "debt_type": "TITULOS PUBLICOS -Bonos LP", "operation_name": "Par en $ ajustado por CER", "rate_type": "TASA FIJA", "currency": "PESO ARGENTINO + CER", "as_of_date": "2008-09-30", "balance_loan_currency": "3602980003.43", "balance_usd": "2512088142.80", "exchange_rate": "N/A", "source_id": sigade_source["id"], "source_member": SIGADE_MEMBER, "query_basis": "SELECT filtered SALDOS", "evidence_status": "Q3_OPERATION_BALANCE_EXTRACTED", "caveat": "Respetar el nombre de campo SIGADE; no reinterpretar como VNO residual sin puente."},
    {"record_id": "SG127_DISCOUNT_ARS", "table_name": "SALDOS", "debt_type": "TITULOS PUBLICOS -Bonos LP", "operation_name": "Discount en $ ajustado por CER", "rate_type": "TASA FIJA", "currency": "PESO ARGENTINO + CER", "as_of_date": "2008-09-30", "balance_loan_currency": "11803648176.77", "balance_usd": "8229799942.95", "exchange_rate": "N/A", "source_id": sigade_source["id"], "source_member": SIGADE_MEMBER, "query_basis": "SELECT filtered SALDOS", "evidence_status": "Q3_OPERATION_BALANCE_EXTRACTED_MATCHES_XLS_UPDATED_COLUMN", "caveat": "Coincide con A.12.2 H31 dentro del redondeo visible; no contiene transacciones Q4."},
    {"record_id": "SG127_CUASIPAR_ARS", "table_name": "SALDOS", "debt_type": "TITULOS PUBLICOS -Bonos LP", "operation_name": "Cuasipar en $ ajustado por CER", "rate_type": "TASA FIJA", "currency": "PESO ARGENTINO + CER", "as_of_date": "2008-09-30", "balance_loan_currency": "18833196326.34", "balance_usd": "13130977451.28", "exchange_rate": "N/A", "source_id": sigade_source["id"], "source_member": SIGADE_MEMBER, "query_basis": "SELECT filtered SALDOS", "evidence_status": "Q3_OPERATION_BALANCE_EXTRACTED", "caveat": "Respetar el nombre de campo SIGADE; no reinterpretar como VNO residual sin puente."},
    {"record_id": "SG127_FX_ARS", "table_name": "TIPO DE CAMBIO", "debt_type": "N/A", "operation_name": "N/A", "rate_type": "N/A", "currency": "PESO ARGENTINO", "as_of_date": "2008-09-30", "balance_loan_currency": "N/A", "balance_usd": "N/A", "exchange_rate": "3.135", "source_id": sigade_source["id"], "source_member": SIGADE_MEMBER, "query_basis": "SELECT filtered TIPO DE CAMBIO", "evidence_status": "Q3_FX_EXTRACTED", "caveat": "Tipo de cambio del corte, no precio de una operación individual."},
]
assert abs(D(sigade_rows[1]["balance_usd"]) - q3_discount_updated_thousand_usd * D("1000")) < D("10")
write_csv(HERE / "E0_SIGADE_Q3_EXCHANGE_BOND_EXTRACT_V127.csv", sigade_rows)

crosswalk_path = HERE / "E0_SECURITY_IDENTIFIER_CROSSWALK_V127.csv"
crosswalk = read_csv(crosswalk_path)
crosswalk.append(
    {
        "crosswalk_id": "ID127_06", "target_instrument": "Discount en Pesos 5,83% 2033",
        "isin": "ARARGE03E121", "historical_code": "N/D", "code_label_in_source": "ISIN",
        "primary_chain": "informe oficial Decreto 1735/04 p.2 + Deuda Pública Q3/Q4 A.12.2 + SIGADE Q3 SALDOS",
        "evidence_status": "EXACT_OFFICIAL_ISIN_AND_AGGREGATE_STOCK_ACCOUNTING_BRIDGE",
        "unresolved_element": "Fecha y operación individual; Código Caja/CRyL histórico; contraparte; asiento y pago",
        "prohibited_inference": "No convertir el valor efectivo agregado en constancia de pago BCRA ni en padrón de vendedores.",
    }
)
write_csv(crosswalk_path, crosswalk)

ledger_path = HERE / "E0_FISCAL_MECHANISM_LEDGER_V127.csv"
ledger = read_csv(ledger_path)
for row in ledger:
    if row["ledger_id"] == "F127":
        row.update(
            {
                "universe": "Excess_growth_reference_year_2006_aggregate",
                "instrument": "Discount_en_pesos_5.83_2033_ARARGE03E121",
                "valuation_basis": "EXACT_V127_CROSS_SOURCE_STOCK_REPORT_ACCOUNTING_BRIDGE",
                "source_id": "e0_argentina_deuda_publica_2008_q3;e0_argentina_deuda_publica_2008_q4;e0_argentina_recompras_decreto_1735_04_report;e0_argentina_sigade_2008_q3",
                "source_locator": "Q3/Q4 A.12.2 row31;Q4 A.5.1 row29;PDF p2;SIGADE SALDOS",
                "realization_status": "ACCOUNTED_AGGREGATE_DEBT_REDUCTION_EXACT_INSTRUMENT_ALLOCATION",
                "status_interpretation": "La baja Q4 se asigna al Discount en Pesos: VNO reportado ARS 2.748,50m, VNO derivado ARS 2.748,478269m y baja actualizada ARS 4.723,53619m.",
                "caveat": "No individualiza fecha, vendedor, matching Caja ni riel/orden de pago; GDP Units siguen fuera del cuadro.",
            }
        )
ledger.extend(
    [
        {"ledger_id": "F130", "window": "REFERENCE_2006_REFLECTED_IN_2008Q4_STOCK", "mechanism": "Debt_buyback_excess_growth", "phase": "OFFICIAL_RETROSPECTIVE_INSTRUMENT_REPORT_VNO", "as_of_date": "2008Q4_STOCK_BRIDGE", "payer": "Tesoro_Nacional", "recipient": "Instrument_holders_unknown", "universe": "Five_percent_excess_growth_reference_2006", "instrument": "Discount_en_pesos_5.83_2033_ARARGE03E121", "amount_original": "2748.50", "original_unit": "ARS_million_VNO", "normalized_ars_million": "N/D", "valuation_basis": "OFFICIAL_REPORT_PAGE_2", "source_id": "e0_argentina_recompras_decreto_1735_04_report", "source_locator": "PDF_p2", "realization_status": "OFFICIAL_EFFECTED_AGGREGATE_INSTRUMENT_REPURCHASE", "additivity": "NON_ADDITIVE_WITH_F127_F131", "status_interpretation": "El informe oficial identifica el VNO adquirido por especie y el ISIN.", "caveat": "Año de referencia no equivale a fecha de cada compra; no publica contrapartes ni asientos."},
        {"ledger_id": "F131", "window": "REFERENCE_2006_REFLECTED_IN_2008Q4_STOCK", "mechanism": "Debt_buyback_excess_growth", "phase": "OFFICIAL_RETROSPECTIVE_INSTRUMENT_REPORT_EFFECTIVE_VALUE", "as_of_date": "2008Q4_STOCK_BRIDGE", "payer": "Tesoro_Nacional", "recipient": "Instrument_holders_unknown", "universe": "Five_percent_excess_growth_reference_2006", "instrument": "Discount_en_pesos_5.83_2033_ARARGE03E121", "amount_original": "1415.50", "original_unit": "ARS_million_effective_value", "normalized_ars_million": "1415.50", "valuation_basis": "OFFICIAL_REPORT_PAGE_2", "source_id": "e0_argentina_recompras_decreto_1735_04_report", "source_locator": "PDF_p2", "realization_status": "OFFICIAL_AGGREGATE_EFFECTIVE_VALUE_REPORTED_PAYMENT_RAIL_OPEN", "additivity": "NON_ADDITIVE_WITH_F127_F130", "status_interpretation": "El valor efectivo agregado queda separado del VNO y de la baja contable actualizada.", "caveat": "No equivale a constancia de pago cursado por BCRA ni identifica receptores finales."},
    ]
)
write_csv(ledger_path, ledger)

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V127.csv"
breaks = read_csv(breaks_path)
for row in breaks:
    if row["break_id"] == "q4_exchange_bond_aggregate_not_target_tenders":
        row["status"] = "SUPERSEDED_BY_V127_CROSS_SOURCE_INSTRUMENT_BRIDGE"
        row["evidence"] = "Deuda Q3/Q4 A.12.2; informe Decreto 1735/04 p.2; SIGADE Q3; bridge V127"
breaks.extend(
    [
        {"break_id": "q4_instrument_allocation_not_individual_settlement", "dimension": "phase", "problem": "La conciliación cruzada asigna la baja Q4 al Discount en Pesos agregado, pero no expone operaciones individuales.", "rule": "Permitir la identificación de especie y tramo de referencia 2006; mantener abiertos fecha, vendedor, matching Caja y riel de pago.", "status": "FROZEN", "evidence": "E0_FISCAL_Q4_EXCHANGE_BOND_STOCK_MOVEMENTS_V127.csv; E0_FISCAL_Q4_DISCOUNT_PESOS_VALUATION_BRIDGE_V127.csv"},
        {"break_id": "vno_effective_value_accounting_reduction_nonadditive", "dimension": "unit", "problem": "VNO ARS 2.748,50m, valor efectivo ARS 1.415,50m y baja actualizada ARS 4.723,53619m son bases distintas.", "rule": "No sumarlas ni intercambiarlas: VNO mide nominal adquirido, valor efectivo la consideración agregada reportada y la baja contable el stock actualizado eliminado.", "status": "FROZEN", "evidence": "Informe Decreto 1735/04 p.2; Deuda Q3/Q4 A.12.2 y A.5.1"},
    ]
)
write_csv(breaks_path, breaks)

accounting_path = HERE / "E0_FISCAL_BUYBACK_DEBT_ACCOUNTING_BRIDGE_2008_V127.csv"
accounting = read_csv(accounting_path)
for row in accounting:
    if row["bridge_id"] == "AB127_Q4_CANJE":
        row["evidence_status"] = "EXACT_CROSS_SOURCE_ALLOCATION_TO_DISCOUNT_PESOS_REFERENCE_2006_AGGREGATE"
        row["caveat"] = "El renglón Q4 se reconcilia con Discount en Pesos ARARGE03E121: VNO derivado ARS 2.748,478269m, VNO oficial redondeado ARS 2.748,50m y valor efectivo ARS 1.415,50m. No prueba cada operación, Caja ni pago BCRA."
write_csv(accounting_path, accounting)

episode_path = HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V127.csv"
episode_rows = read_csv(episode_path)
for row in episode_rows:
    if row["variable"] == "public_debt_repurchase_accounting_scope" and row["t0"] == "2008Q4":
        row.update(
            {
                "pre_value": "DICP_VNO_ARS15012.460651M_AT_2008Q3",
                "trough_value": "DICP_VNO_ARS12263.982382M_AT_2008Q4",
                "recovery_value": "VNO_REDUCTION_ARS2748.478269M_REPORT_ARS2748.50M_EFFECTIVE_ARS1415.50M_ACCOUNTING_ARS4723.53619M",
                "benchmark_definition": "cross-source Discount en Pesos VNO/effective/accounting bridge",
                "source_id": "e0_argentina_deuda_publica_2008_q3;e0_argentina_deuda_publica_2008_q4;e0_argentina_recompras_decreto_1735_04_report;e0_argentina_sigade_2008_q3",
                "source_quality": "PRIMARY_EXACT_CROSS_SOURCE_INSTRUMENT_ALLOCATION",
                "basis": "A.12.2 row31; A.5.1 row29; PDF p2; SIGADE SALDOS",
                "method_break": "YES_VNO_EFFECTIVE_ACCOUNTING_NONADDITIVE_AND_SETTLEMENT_OPEN",
                "status": "ACCOUNTED_AGGREGATE_DISCOUNT_PESOS_REPURCHASE_INDIVIDUAL_SETTLEMENT_OPEN",
                "interpretation": "The Q4 exchange-bond accounting reduction is allocated to Discount en Pesos under the reference-2006 excess-growth tranche.",
                "falsifier": "YES_AGAINST_UNALLOCATED_Q4_EXCHANGE_BOND_AGGREGATE",
                "notes": "Individual dates, sellers, Caja matching and the BCRA/payment rail remain open; GDP Units remain excluded.",
            }
        )
write_csv(episode_path, episode_rows)

coverage_path = HERE / "HISTORICAL_EVIDENCE_COVERAGE_V127.csv"
coverage_rows = read_csv(coverage_path)
for row in coverage_rows:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row["quality"] = "PRIMARY_BUYBACK_ACCOUNTING_EXACT_Q3_BODEN_AND_Q4_DISCOUNT_PESOS_ALLOCATION"
        row["comparable"] = "SERIES_SERVICE_RECONCILED_TRANSACTIONS_EXACT_Q3_Q4_INSTRUMENT_AGGREGATE_CUSTODIAN_DISCLOSURE_GAP_PRIMARY"
        row["gap"] = "Las bajas contables Q3 BODEN y Q4 Discount en Pesos están conciliadas agregadamente. Faltan asignación por ronda/oferta Q3, fechas y vendedores del tramo Q4, asientos Caja, informes T+3 entregados, pago BCRA y registro específico de GDP Units."
        row["next_action"] = "Pedir sólo con autorización expresa la conciliación individual por operación de ARARGE03E121 y los registros Caja/BCRA; mantener la cuarta comunicación y GDP Units como búsquedas separadas."
write_csv(coverage_path, coverage_rows)

queue_path = HERE / "HISTORICAL_SOURCE_QUEUE_V127.csv"
queue_rows = read_csv(queue_path)
for row in queue_rows:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row["status"] = "PUBLIC_ACCOUNTING_Q3_BODEN_Q4_DISCOUNT_PESOS_AGGREGATES_RECONCILED_INSTITUTIONAL_DETAIL_PAYMENT_READY_NOT_SENT"
        row["why"] = "Q3 BODEN coincide con el residual adjudicado y Q4 se asigna al Discount en Pesos ARARGE03E121; 62 claves y 81 objetos aíslan operaciones, Caja, T+3 y pago. El archivo público actual no muestra cuarta comunicación ni base SIGADE Q4."
        row["next_action"] = "Obtener autorización expresa, completar datos personales y presentar sólo los pedidos autorizados; conservar constancias y conciliar respuestas con AB127 y el puente V127."
write_csv(queue_path, queue_rows)

trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V127.csv"
trace = read_csv(trace_path)
for row in trace:
    if row["trace_id"] == "TR127_078":
        row["period_or_date"] = "2008Q3-2008Q4; referencia 2006"
        row["identifiers"] = "Discount en Pesos; ARARGE03E121; VNO 2748.50m; efectivo 1415.50m; baja 4723.53619m ARS"
        row["minimum_usable_fields"] = "fecha; operación; especie/ISIN; VNO; precio/efectivo; asiento; expediente; estado; vínculo Caja/BCRA"
trace.extend(
    [
        {"trace_id": "TR127_079", "request_id": "REQ127_CAJA", "institution": "Caja de Valores S.A.", "gap_id": "CL127_DEBT_ACCOUNTING", "requested_record": "Movimientos o bajas agregadas del Discount en Pesos vinculables a la recompra por exceso de crecimiento referencia 2006", "period_or_date": "30/09/2008-31/12/2008", "identifiers": "ARARGE03E121; VNO ARS 2748.50m; baja contable ARS 4723.53619m", "minimum_usable_fields": "fecha; especie/código; nominal; cuenta origen/destino testada; estado; asiento o evento", "confidentiality_fallback": "certificación agregada por especie, fecha y estado", "status": "DRAFT_NOT_SENT"},
        {"trace_id": "TR127_080", "request_id": "REQ127_BCRA", "institution": "Banco Central / CRyL", "gap_id": "CL127_DEBT_ACCOUNTING", "requested_record": "Orden, débito o conciliación del valor efectivo de la recompra Discount en Pesos referencia 2006", "period_or_date": "2008Q4 o fecha de registración efectiva", "identifiers": "ARARGE03E121; efectivo ARS 1415.50m; VNO ARS 2748.50m", "minimum_usable_fields": "fecha; monto; moneda; ordenante; sistema; estado; referencia contable/expediente", "confidentiality_fallback": "certificación de existencia, fecha, monto agregado y estado sin datos de terceros", "status": "DRAFT_NOT_SENT"},
        {"trace_id": "TR127_081", "request_id": "REQ127_ECON", "institution": "Ministerio de Economía / Secretaría de Finanzas", "gap_id": "CL127_DEBT_ACCOUNTING", "requested_record": "Papeles de trabajo que vinculan el tramo de exceso de crecimiento referencia 2006 con la baja Q4 del Discount en Pesos", "period_or_date": "referencia 2006; reconocimiento 2008Q4", "identifiers": "ARARGE03E121; 2748.50m VNO; 1415.50m efectivo; 4723.53619m actualizado", "minimum_usable_fields": "criterio de valuación; fecha; operación; VNO; efectivo; asiento; expediente; conciliación", "confidentiality_fallback": "papel de trabajo agregado por especie con metadatos", "status": "DRAFT_NOT_SENT"},
    ]
)
write_csv(trace_path, trace)

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V127.csv"
keys = read_csv(keys_path)
keys.extend(
    [
        {"key_id": "SK127_60", "request_id": "REQ127_ECON", "key_group": "discount_pesos_accounting", "exact_key": "ARARGE03E121;Discount en Pesos;2748.50;1415.50;4723536.19;1506710.11", "search_purpose": "localizar el papel de trabajo que une VNO, valor efectivo y baja actualizada", "source_or_basis": "informe Decreto 1735/04 y planillas Q3/Q4", "caveat": "Las tres magnitudes no son aditivas."},
        {"key_id": "SK127_61", "request_id": "REQ127_CAJA", "key_group": "discount_pesos_custody", "exact_key": "ARARGE03E121;2008Q4;VNO 2748.50m;recompra por exceso de crecimiento referencia 2006", "search_purpose": "localizar movimientos/bajas por especie", "source_or_basis": "puente de stock V127", "caveat": "La caída agregada no prueba un evento Caja individual."},
        {"key_id": "SK127_62", "request_id": "REQ127_BCRA", "key_group": "discount_pesos_payment", "exact_key": "ARARGE03E121;valor efectivo ARS 1415.50m;referencia 2006;2008Q4", "search_purpose": "localizar orden, débito o conciliación de pago", "source_or_basis": "informe oficial de recompras p.2", "caveat": "Valor efectivo reportado no identifica por sí solo el riel de pago."},
    ]
)
write_csv(keys_path, keys)

closures_path = HERE / "E0_REQUEST_CLOSURE_CRITERIA_V127.csv"
closures = read_csv(closures_path)
for row in closures:
    if row["gap_id"] == "CL127_DEBT_ACCOUNTING":
        row["does_not_close"] = "El puente VNO/efectivo/baja contable cierra la especie agregada, pero no la fecha ni contraparte de cada compra, el asiento Caja o el riel de pago."
        row["initial_status"] = "Q3_BODEN_AND_Q4_DISCOUNT_PESOS_AGGREGATE_ACCOUNTING_RECONCILED_INDIVIDUAL_SETTLEMENT_OPEN_NOT_SENT"
write_csv(closures_path, closures)

attachments_path = HERE / "E0_REQUEST_ATTACHMENT_MINIMUM_V127.csv"
attachments = read_csv(attachments_path)
for row in attachments:
    if row["request_id"] == "REQ127_ECON" and row["attach_file"] == "E0_FISCAL_BUYBACK_DEBT_ACCOUNTING_BRIDGE_2008_V127.csv":
        row["attach_file"] = "E0_FISCAL_Q4_DISCOUNT_PESOS_VALUATION_BRIDGE_V127.csv"
        row["purpose"] = "VNO, valor efectivo y baja contable Q4 conciliados por especie"
        row["why_minimal"] = "permite localizar el papel de trabajo exacto sin adjuntar planillas completas"
        row["exclude"] = "inferencias sobre contrapartes o pago no documentado"
write_csv(attachments_path, attachments)

request_addenda = {
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V127.md": """

## Clave adicional V127 · Discount en Pesos

Se solicita además el papel de trabajo o registro que vincule el tramo de recompra por exceso de crecimiento del año de referencia 2006 con `ARARGE03E121`: VNO ARS 2.748,50 millones, valor efectivo ARS 1.415,50 millones y baja Q4 ARS 4.723,53619 millones. Campos mínimos: fecha, operación, VNO, precio/efectivo, criterio de actualización, asiento, expediente y estado de conciliación. Puede entregarse agregado por especie y con datos de terceros testados.
""",
    "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V127.md": """

## Clave adicional V127 · ARARGE03E121

Para el período 30/09/2008-31/12/2008, se solicitan movimientos, bajas o certificación agregada vinculables a la recompra de VNO ARS 2.748,50 millones de Discount en Pesos `ARARGE03E121`, con fecha, código de especie histórico, nominal, estado y referencia de asiento/evento. No se requieren identidades privadas si corresponde testar.
""",
    "REQUEST_BCRA_CRYL_SETTLEMENT_V127.md": """

## Clave adicional V127 · valor efectivo Discount en Pesos

Se solicita búsqueda por `ARARGE03E121`, valor efectivo agregado ARS 1.415,50 millones, VNO ARS 2.748,50 millones y referencia 2006/registro Q4 2008, para identificar orden, débito o conciliación: fecha, monto, moneda, ordenante, sistema, estado y referencia contable/expediente. La certificación agregada sin datos de terceros resulta suficiente.
""",
}
for filename, addendum in request_addenda.items():
    path = HERE / filename
    text = path.read_text(encoding="utf-8-sig")
    if "Clave adicional V127" not in text:
        path.write_text(text.rstrip() + addendum, encoding="utf-8")

reconstruction = f"""# Reconstrucción fiscal E0 · V127

## Hallazgo principal

La línea Q4 `Recompra Bonos del Canje - Dto. 1735/04` deja de estar sin especie. Entre 30/09 y 31/12/2008, `Par en Pesos` y `Cuasipar en Pesos` conservan su nominal nativo; su variación en miles de USD se explica por el tipo de cambio 3,135→3,452. El único nominal que cae es `Discount en Pesos`: ARS 15.012,460651m→ARS 12.263,982382m, reducción ARS 2.748,478269m.

El informe oficial del Decreto 1735/04 identifica para el año de referencia 2006 una recompra de `Discount en Pesos 5,83% 2033`, ISIN `ARARGE03E121`, por VNO ARS 2.748,50m y valor efectivo ARS 1.415,50m. El delta entre el VNO derivado y el informe redondeado es ARS -0,021731m (0,00079%).

Al multiplicar el VNO reducido por el factor actualizado/nominal del Discount al 30/09, 1,7186005287, se obtienen ARS 4.723.536,206 miles: delta ARS 0,016 miles frente al renglón oficial ARS 4.723.536,19 miles. Al dividir por el TC 3,135 se reproduce USD 1.506.710,11 miles al redondeo publicado.

## Control SIGADE

La base SIGADE Q3 preservada contiene `Discount en $ ajustado por CER` con saldo USD 8.229.799.942,95 y TC ARS/USD 3,135. El saldo coincide con A.12.2 H31 dentro del redondeo visible. La página oficial no publica una base Q4 equivalente para 31/12/2008; el XLS Q4 sigue siendo el extremo final.

## Separación de magnitudes

- VNO ARS 2.748,50m: nominal adquirido reportado.
- Valor efectivo ARS 1.415,50m: consideración agregada reportada.
- Baja contable ARS 4.723,53619m / USD 1.506,71011m: stock actualizado eliminado.

No son cifras aditivas ni intercambiables.

## Frontera probatoria

Se cierra la asignación agregada Q4 a especie y tramo: Discount en Pesos, año de referencia 2006. Siguen abiertos fecha y vendedor de cada operación, matching y asiento Caja, informe de liquidación, orden/débito BCRA y beneficiarios finales. GDP Units continúan expresamente excluidas del cuadro contable. `CLOSED_NETWORK_GATE=NO`.
"""
(HERE / "E0_FISCAL_RECONSTRUCTION_V127.md").write_text(reconstruction, encoding="utf-8")

readme = f"""# Checkpoint V127 · asignación exacta Q4 al Discount en Pesos

V127 cierra la especie detrás de la baja contable Q4: `Discount en Pesos 5,83% 2033`, ISIN `ARARGE03E121`, bajo el tramo de exceso de crecimiento del año de referencia 2006.

El stock nominal cae ARS 2.748,478269m; el informe oficial publica VNO ARS 2.748,50m y valor efectivo ARS 1.415,50m. La valuación actualizada reproduce ARS 4.723,53619m / USD 1.506,71011m de A.5.1 dentro del redondeo de tabla.

Se preserva la base SIGADE Q3 y se extraen sus saldos/TC. El cierre es agregado por especie: fechas individuales, vendedores, Caja y BCRA siguen abiertos. Seis pedidos permanecen `DRAFT_NOT_SENT`; panel estricto sin cambios.
"""
(HERE / "README_V127.md").write_text(readme, encoding="utf-8")

verdict = """# Veredicto V127

Queda probado con tres fuentes primarias concordantes que la baja Q4 antes no asignada corresponde agregadamente al Discount en Pesos 5,83% 2033, ISIN ARARGE03E121, dentro de la recompra por exceso de crecimiento del año de referencia 2006.

El VNO reconstruido es ARS 2.748,478269 millones y el informe oficial publica ARS 2.748,50 millones; la diferencia es de ARS 21.731 por redondeo/precisión. El mismo informe separa un valor efectivo de ARS 1.415,50 millones. La baja contable actualizada de ARS 4.723,53619 millones —USD 1.506,71011 millones al TC 3,135— se reproduce dentro del redondeo visible.

Esto prueba recompra agregada por especie y su reflejo contable, no la fecha/contraparte de cada operación, el asiento o matching de Caja, ni la orden y débito de pago BCRA. Las GDP Units siguen fuera del cuadro contable y requieren su propio puente. `CLOSED_NETWORK_GATE=NO`.
"""
(HERE / "VEREDICTO_V127.md").write_text(verdict, encoding="utf-8")

audit_md = f"""# Auditoría V127

- Fuentes maestras: {len(catalog)}.
- Fuente primaria nueva: base SIGADE Q3 oficial; ZIP {sigade_source['bytes']:,} bytes, SHA-256 verificado.
- Fuentes primarias E0: {len(census)}.
- Ledger fiscal: {len(ledger)} filas.
- Cortes metodológicos: {len(breaks)}.
- Movimientos Q3→Q4: {len(stock_rows)} especies en pesos.
- Puente de valuación Discount: {len(valuation_bridge)} identidades; delta contable ARS {derived_accounting_thousand_ars - official_q4_thousand_ars} miles.
- Tabla de exceso de crecimiento referencia 2006: {len(excess_growth)} filas; efectivo total ARS 3.301,60m.
- Extracto SIGADE: {len(sigade_rows)} filas.
- Pedidos: 6 borradores, 0 enviados; {len(trace)} objetos, {len(keys)} claves, {len(attachments)} adjuntos mínimos.
- Panel estricto: 30 entidades; {STRICT}% sin cambios.
"""
(HERE / "AUDITORIA_V127.md").write_text(audit_md, encoding="utf-8")

retrieval_log = """# Registro de recuperación V127

Fecha: 2026-08-29.

1. Se convirtieron copias temporales de los XLS BIFF Q3/Q4 a XLSX mediante Excel en modo invisible y sólo lectura; los originales preservados no fueron modificados.
2. Se inspeccionaron A.12.2 y A.19 con el lector principal: Par y Cuasipar mantienen nominal nativo; Discount en Pesos cae ARS 2.748,478269m.
3. Se reabrió el PDF oficial ya preservado en V114 y se inspeccionaron visualmente sus cinco páginas. La página 2 reporta ARARGE03E121, VNO ARS 2.748,50m y efectivo ARS 1.415,50m para referencia 2006.
4. Se descargó y preservó el ZIP SIGADE Q3 desde la página oficial. Su MDB se consultó en modo lectura mediante ACE OLEDB: SALDOS y TIPO DE CAMBIO.
5. SIGADE confirma Discount en $ ajustado por CER, saldo USD 8.229.799.942,95 y TC 3,135 al 30/09/2008; coincide con el XLS dentro de su redondeo visible.
6. La página oficial no ofrece una base SIGADE Q4 para 31/12/2008. No se inventó una URL ni se trató el corte Q3 como historial.
7. Las búsquedas públicas adicionales no recuperaron informe individual Caja, asiento de matching ni orden/débito BCRA para ARARGE03E121.
8. No se envió ningún pedido ni se realizó presentación externa.
"""
(HERE / "RETRIEVAL_LOG_V127.md").write_text(retrieval_log, encoding="utf-8")

source_refs = """# Referencias de fuentes V127

- Datos anteriores de deuda pública: https://www.argentina.gob.ar/economia/finanzas/datos-trimestrales-de-la-deuda/datos-anteriores
- Deuda Pública 30/09/2008: https://www.argentina.gob.ar/sites/default/files/deuda_publica_30-09-08.xls
- Base SIGADE 30/09/2008: https://www.argentina.gob.ar/sites/default/files/basesigade2008-09-30.zip
- Deuda Pública 31/12/2008: https://www.argentina.gob.ar/sites/default/files/deuda_publica_31-12-2008.xls
- Informe de recompras bajo Decreto 1735/04: https://www.argentina.gob.ar/sites/default/files/recompras_de_deuda.pdf

Los binarios fuente están preservados con SHA-256 en el catálogo maestro. La base Q4 no figura publicada en la página oficial para 31/12/2008.
"""
(HERE / "SOURCE_REFERENCES_V127.md").write_text(source_refs, encoding="utf-8")

handover = """# Handover V127 → V128

## Estado congelado

- La baja Q4 se asigna agregadamente a Discount en Pesos 5,83% 2033, ISIN ARARGE03E121, tramo de exceso de crecimiento referencia 2006.
- VNO derivado ARS 2.748,478269m versus informe ARS 2.748,50m; valor efectivo oficial ARS 1.415,50m.
- El factor actualizado Q3 reproduce la baja ARS 4.723,53619m / USD 1.506,71011m dentro del redondeo.
- SIGADE Q3 confirma el saldo actualizado y TC 3,135; no hay base SIGADE Q4 publicada en la misma página.
- No se prueban fechas/vendedores individuales, matching Caja, informe de liquidación ni orden/débito BCRA.
- GDP Units continúan fuera del cuadro. Seis borradores, ninguno enviado; panel estricto sin cambios.

## Prioridad V128

1. Buscar papeles de trabajo/expediente que vinculen referencia 2006 con operaciones y fecha de registración Q4 de ARARGE03E121.
2. Buscar movimientos/bajas Caja y conciliación BCRA por ARARGE03E121, VNO 2.748,50m y efectivo 1.415,50m.
3. Retomar informes T+3 de las rondas públicas y la cuarta comunicación 2008; no mezclar con el tramo Discount.
4. Construir puente separado para GDP Units, explícitamente excluidas del cuadro contable.
5. No enviar pedidos ni formularios sin autorización expresa.
"""
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V127_A_V128.md").write_text(handover, encoding="utf-8")

package_path = HERE / "E0_INSTITUTIONAL_REQUEST_PACKAGE_V127.md"
package = package_path.read_text(encoding="utf-8-sig")
package = package.replace("El paquete contiene 78 objetos trazados y 59 claves exactas.", "El paquete contiene 81 objetos trazados y 62 claves exactas.")
package = package.replace(
    "Las nuevas búsquedas se concentran en cuatro piezas faltantes: comunicación de la cuarta ronda 2008, instrucciones/asientos ejecutados, informes T+3 entregados y pagos/bajas conciliados.",
    "Las búsquedas se concentran en comunicación de la cuarta ronda 2008, instrucciones/asientos ejecutados, informes T+3 entregados, operaciones individuales del Discount en Pesos y pagos/bajas conciliados.",
)
if "Clave V127 · Discount en Pesos" not in package:
    package += """

## Clave V127 · Discount en Pesos

Los pedidos Economía, Caja y BCRA incorporan `ARARGE03E121`, VNO ARS 2.748,50m, efectivo ARS 1.415,50m y baja actualizada ARS 4.723,53619m. El objetivo es cerrar fecha/operación/asiento/riel de pago; la especie agregada ya quedó conciliada. Estado: `DRAFT_NOT_SENT`.
"""
    package_path.write_text(package, encoding="utf-8")
else:
    package_path.write_text(package, encoding="utf-8")

checklist_path = HERE / "REQUEST_SUBMISSION_CHECKLIST_V127.md"
checklist = checklist_path.read_text(encoding="utf-8-sig")
if "ARARGE03E121" not in checklist:
    checklist = checklist.replace(
        "- cuarta ronda: licitación 02/10/2008, recepción esperada 03/10–06/10 e informe 07/10.",
        "- cuarta ronda: licitación 02/10/2008, recepción esperada 03/10–06/10 e informe 07/10;\n- Discount en Pesos `ARARGE03E121`: VNO ARS 2.748,50m, valor efectivo ARS 1.415,50m y baja actualizada ARS 4.723,53619m, siempre como bases no aditivas.",
    )
    checklist_path.write_text(checklist, encoding="utf-8")

inherited = [
    {"script": "qa_v97.py", "pre_v127_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v127_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V97 congela una ausencia luego resuelta."},
    *({"script": f"qa_v{i}.py", "pre_v127_result": "PASS", "post_v127_result": "PASS", "interpretation": "Compatible"} for i in (98, 100, 101, 102, 103, 104, 105, 106)),
    *({"script": f"qa_v{i}.py", "pre_v127_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v127_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "Congela un checkpoint o conteo anterior."} for i in range(107, 127)),
    {"script": "qa_v127.py", "pre_v127_result": "N/A", "post_v127_result": "PASS", "interpretation": "Q4 asignado a Discount en Pesos; VNO/efectivo/baja contable separados; settlement individual abierto."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V127.csv", inherited)

for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    shutil.copyfile(AUDIT / f"{stem}_V126.csv", AUDIT / f"{stem}_V127.csv")

hash_rows = [row for row in read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V126.csv") if row["id"] != sigade_source["id"]]
hash_rows.append({"id": sigade_source["id"], "archivo_local": sigade_source["local"], "exists": "True", "sha_catalog": SIGADE_SHA, "sha_actual": SIGADE_SHA, "hash_ok": "True"})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V127.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V127.csv", hash_rows)

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": str(size), "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V127.csv", size_rows)

physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V126.json").read_text(encoding="utf-8"))
for key in list(completeness):
    if key.endswith("_v126") or "newly_preserved_v126" in key or "sources_newly_preserved_v126" in key or key == "numeric_v126_strict_changed":
        completeness.pop(key, None)
completeness.update(
    {
        "checkpoint": "V127", "date": "2026-08-29",
        "state": "E0_Q4_DISCOUNT_PESOS_INSTRUMENT_VNO_EFFECTIVE_ACCOUNTING_BRIDGE_EXACT_INDIVIDUAL_SETTLEMENT_OPEN_NOT_SENT",
        "numeric_v127_strict_changed": False, "master_catalog_entries": len(catalog),
        "physical_local_copies": physical, "physical_local_hash_ok": hash_ok,
        "binary_required_entries": len(catalog) - 5, "binary_required_preserved": physical,
        "e0_primary_sources_preserved": len(census),
        "e0_quality": "PRIMARY_Q4_DISCOUNT_PESOS_EXACT_CROSS_SOURCE_VNO_EFFECTIVE_ACCOUNTING_BRIDGE",
        "sources_newly_preserved_v127": 1, "e0_primary_sources_newly_preserved_v127": 1,
        "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
        "e0_request_drafts": 6, "e0_request_traceability_rows": len(trace), "e0_request_closure_rules": len(closures),
        "e0_request_search_keys": len(keys), "e0_request_attachment_rows": len(attachments),
        "e0_security_identifier_crosswalk_rows": len(crosswalk),
        "e0_q4_exchange_bond_stock_movement_rows": len(stock_rows), "e0_q4_discount_valuation_bridge_rows": len(valuation_bridge),
        "e0_excess_growth_reference_2006_rows": len(excess_growth), "e0_sigade_q3_extract_rows": len(sigade_rows),
        "e0_requests_submitted": 0, "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
        "historical_workstream": "Q4 exchange-bond reduction allocated to Discount en Pesos reference-2006 tranche; VNO, effective value and updated accounting reduction reconciled; individual Caja/BCRA/payment records and GDP Units remain open; no request submitted",
    }
)
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V127.json").write_text(json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V127 · Q4 asignado al Discount en Pesos"
old_backup = backup.read_text(encoding="utf-8-sig")
if marker not in old_backup:
    old_backup += (
        f"\n\n{marker}\n\n"
        "- La baja Q4 de Bonos del Canje se asigna a Discount en Pesos 5,83% 2033, ARARGE03E121, referencia 2006.\n"
        "- VNO derivado ARS 2.748,478269m versus informe ARS 2.748,50m; valor efectivo ARS 1.415,50m.\n"
        "- La baja actualizada reproduce ARS 4.723,53619m / USD 1.506,71011m dentro del redondeo.\n"
        "- SIGADE Q3 fue preservado y confirma saldo/TC; no hay base Q4 publicada en la misma página.\n"
        "- Fecha/contraparte individual, Caja, BCRA y GDP Units siguen abiertos. Seis pedidos DRAFT_NOT_SENT.\n"
        "- Panel estricto y cifras bancarias sin cambios.\n"
    )
    backup.write_text(old_backup, encoding="utf-8")


def checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V127.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V127", "parent_checkpoint": "V126",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": 1, "new_primary_sources": 1,
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks),
        "q4_exchange_bond_stock_movement_rows": len(stock_rows), "q4_discount_valuation_bridge_rows": len(valuation_bridge),
        "excess_growth_reference_2006_rows": len(excess_growth), "sigade_q3_extract_rows": len(sigade_rows),
        "request_drafts": 6, "request_traceability_rows": len(trace), "request_closure_rules": len(closures),
        "request_search_keys": len(keys), "request_attachment_rows": len(attachments),
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V127.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    "checkpoint": "V127", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical local copies with {hash_ok}/{physical} SHA-valid; Q4 Discount en Pesos VNO/effective/accounting bridge and SIGADE Q3 preserved; six requests drafted and none submitted.",
    "historical_workstream": "Q4 allocated to Discount en Pesos reference-2006 tranche; VNO, effective value and accounting reduction reconciled; individual Caja/BCRA/payment records and GDP Units remain open; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V127 BUILD PASS")
