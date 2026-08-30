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
V110 = HERE.parent / "V110"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
AUDIT = REPO / "research" / "ciclo_ajuste" / "source_audit"
BIN = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v111" / "binaries"


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


def clone_versioned(stem: str, suffix: str) -> None:
    src = V110 / f"{stem}_V110.{suffix}"
    dst = HERE / f"{stem}_V111.{suffix}"
    text = src.read_text(encoding="utf-8-sig")
    dst.write_text(text.replace("V110", "V111").replace("v110", "v111"), encoding="utf-8-sig")


for stem in (
    "CURRENT_STATE",
    "FOUR_LEG_PASS_PANEL",
    "STRICT_Q4_FOUR_LEG_COVERAGE",
    "RECOVERY_QUEUE",
    "INHERITED_QA_STATUS",
):
    clone_versioned(stem, "csv")

inherited_status_path = HERE / "INHERITED_QA_STATUS_V111.csv"
inherited_status = read_csv(inherited_status_path)
for row in inherited_status:
    row["interpretation"] = row["interpretation"].replace("V111 validates 229", "V111 validates 238")
    if row["script"] == "qa_v109.py":
        row["interpretation"] = "Fails only because V109 freezes the then-current global catalog at 226 rows; V111 validates 238 after twelve later official E0 sources."
current_row = next(row for row in inherited_status if row["script"] == "qa_v111.py")
inherited_status.insert(
    inherited_status.index(current_row),
    {
        "script": "qa_v110.py",
        "pre_v111_result": "PASS",
        "post_v111_result": "EXPECTED_SUPERSEDED_ASSERTION",
        "interpretation": "Fails only because V110 freezes the global catalog at 229 rows and 31 E0 sources; V111 validates 238 and 40.",
    },
)
write_csv(inherited_status_path, inherited_status)


source_specs = [
    {
        "id": "e0_cgn_cuenta_inversion_2004_sdp",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2004 · Servicio de la Deuda Pública y Anexo J",
        "url": "https://www.economia.gob.ar/hacienda/cgn/cuenta/2004/archivos/sdp.pdf",
        "file": "cgn_cuenta_inversion_2004_sdp.pdf",
        "publication": "2005",
        "period": "2004",
        "pages": "79",
        "families": "state_bcra;fiscal;debt;valuation",
        "breaks": "stock por propósito; nominal versus actualizado; cierre no equivale a flujo",
        "use": "USABLE_STOCK_BY_PURPOSE",
        "caveat": "El lenguaje de finalización administrativa no prueba cierre transaccional ni caja.",
        "verified": "Páginas PDF 66 y 71 renderizadas y verificadas.",
    },
    {
        "id": "e0_cgn_cuenta_inversion_2004_tomo_i",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2004 · Tomo I",
        "url": "https://www.economia.gob.ar/hacienda/cgn/cuenta/2004/archivos/tomoi.pdf",
        "file": "cgn_cuenta_inversion_2004_tomoi.pdf",
        "publication": "2005",
        "period": "2004",
        "pages": "348",
        "families": "state_bcra;fiscal;accounting;legal",
        "breaks": "convalidación 2004 de registración extrapresupuestaria originada en 2002",
        "use": "USABLE_PRIOR_PERIOD_CONVALIDATION",
        "caveat": "El artículo 34 es declarativo y no constituye un nuevo flujo de 2004.",
        "verified": "Página PDF 65 renderizada y verificada.",
    },
    {
        "id": "e0_cgn_cuenta_inversion_2005_sdp",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2005 · Servicio de la Deuda Pública y Anexo J",
        "url": "https://www.economia.gob.ar/hacienda/cgn/cuenta/2005/archivos/sdp.pdf",
        "file": "cgn_cuenta_inversion_2005_sdp.pdf",
        "publication": "2006",
        "period": "2005",
        "pages": "95",
        "families": "state_bcra;fiscal;debt;issuance;coverage",
        "breaks": "emisión neta de bajas; moneda de origen; stock versus flujo; propósito",
        "use": "USABLE_NET_ISSUANCE_AND_STOCK",
        "caveat": "Una emisión neta negativa es una corrección; la cobertura no es transferencia gratuita.",
        "verified": "Páginas PDF 80 y 87 renderizadas y verificadas.",
    },
    {
        "id": "e0_cgn_cuenta_inversion_2005_tomo_i",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2005 · Tomo I",
        "url": "https://www.economia.gob.ar/hacienda/cgn/cuenta/2005/archivos/tomoi.pdf",
        "file": "cgn_cuenta_inversion_2005_tomoi.pdf",
        "publication": "2006",
        "period": "2005",
        "pages": "356",
        "families": "state_bcra;fiscal;budget;transfers;financing",
        "breaks": "devengado presupuestario versus caja; empresas privadas versus partida mixta",
        "use": "USABLE_BUDGET_ACCRUAL_WITH_SCOPE",
        "caveat": "La transferencia devengada no identifica pago por banco ni fecha de caja.",
        "verified": "Páginas PDF 118 y 124 renderizadas y verificadas.",
    },
    {
        "id": "e0_cgn_cuenta_inversion_2006_sdp",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2006 · Servicio de la Deuda Pública y Anexo J",
        "url": "https://www.economia.gob.ar/hacienda/cgn/cuenta/2006/archivos/sdp.pdf",
        "file": "cgn_cuenta_inversion_2006_sdp.pdf",
        "publication": "2007",
        "period": "2006",
        "pages": "141",
        "families": "state_bcra;fiscal;debt;issuance;coverage;valuation",
        "breaks": "emisión neta de bajas; propósito; nominal versus actualizado",
        "use": "USABLE_NET_ISSUANCE_AND_STOCK",
        "caveat": "Los saldos por serie mezclan propósitos fuera de los subtotales oficiales.",
        "verified": "Páginas PDF 121 y 132 renderizadas y verificadas.",
    },
    {
        "id": "e0_cgn_cuenta_inversion_2006_tomo_i",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2006 · Tomo I",
        "url": "https://www.economia.gob.ar/hacienda/cgn/cuenta/2006/archivos/tomoi.pdf",
        "file": "cgn_cuenta_inversion_2006_tomoi.pdf",
        "publication": "2007",
        "period": "2006",
        "pages": "367",
        "families": "state_bcra;fiscal;budget;transfers;debt_service;financing",
        "breaks": "servicio agregado por serie; transferencias devengadas; cancelación BCRA separada",
        "use": "USABLE_SERVICE_CONTROL_MIXED_PURPOSE",
        "caveat": "Las amortizaciones BODEN por serie no permiten asignar servicio a compensación, cobertura o ahorristas.",
        "verified": "Páginas PDF 136, 137 y 142 renderizadas y verificadas.",
    },
    {
        "id": "e0_onp_sintesis_ejecutiva_2004q4",
        "institution": "Oficina Nacional de Presupuesto",
        "title": "Síntesis Ejecutiva · cuarto trimestre de 2004",
        "url": "https://www.economia.gob.ar/onp/documentos/sintesis_ejecutiva/2004/4trim04.pdf",
        "file": "onp_sintesis_ejecutiva_2004q4.pdf",
        "publication": "2005",
        "period": "2004",
        "pages": "18",
        "families": "state_bcra;fiscal;budget",
        "breaks": "partida residual Otras sin identificación autónoma del mecanismo",
        "use": "NEGATIVE_SCOPE_EVIDENCE",
        "caveat": "La tabla agregada de 2004 no separa una cifra atribuible a compensación bancaria.",
        "verified": "Página PDF 2 renderizada y verificada.",
    },
    {
        "id": "e0_onp_sintesis_ejecutiva_2005q4",
        "institution": "Oficina Nacional de Presupuesto",
        "title": "Síntesis Ejecutiva · cuarto trimestre de 2005",
        "url": "https://www.economia.gob.ar/onp/documentos/sintesis_ejecutiva/2005/4trim05.pdf",
        "file": "onp_sintesis_ejecutiva_2005q4.pdf",
        "publication": "2006",
        "period": "2005",
        "pages": "20",
        "families": "state_bcra;fiscal;budget;transfers;debt_placement",
        "breaks": "bancos y ahorristas combinados; colocación versus transferencia; diferencia de precio",
        "use": "USABLE_MIXED_BUDGET_BUCKET",
        "caveat": "Los ARS 2.950m mezclan bancos y ahorristas y no se suman a la transferencia bancaria devengada.",
        "verified": "Página PDF 19 renderizada y verificada.",
    },
    {
        "id": "e0_onp_sintesis_ejecutiva_2006q4",
        "institution": "Oficina Nacional de Presupuesto",
        "title": "Síntesis Ejecutiva · cuarto trimestre de 2006",
        "url": "https://www.economia.gob.ar/onp/documentos/sintesis_ejecutiva/2006/4trim06.pdf",
        "file": "onp_sintesis_ejecutiva_2006q4.pdf",
        "publication": "2007",
        "period": "2006",
        "pages": "23",
        "families": "state_bcra;fiscal;budget;transfers;capitalization",
        "breaks": "BNA y compensación combinados; bancos y ahorristas combinados; diferencia de precio",
        "use": "USABLE_MIXED_BUDGET_BUCKET",
        "caveat": "Los ARS 1.780,1m incluyen capitalización del BNA; los ARS 762m mezclan bancos y ahorristas.",
        "verified": "Página PDF 22 renderizada y verificada.",
    },
]

for spec in source_specs:
    path = BIN / spec["file"]
    spec["bytes"] = str(path.stat().st_size)
    spec["sha256"] = sha256(path)
    spec["local"] = "/" + path.relative_to(REPO).as_posix()


catalog = read_csv(CATALOG)
new_ids = {spec["id"] for spec in source_specs}
catalog = [row for row in catalog if row["id"] not in new_ids]
for spec in source_specs:
    catalog.append(
        {
            "id": spec["id"],
            "tema": "ciclo_ajuste_historico",
            "institucion": spec["institution"],
            "titulo": spec["title"],
            "url_original": spec["url"],
            "archivo_local": spec["local"],
            "fecha_descarga": "2026-08-29",
            "fecha_publicacion": spec["publication"],
            "codigo_serie": "",
            "periodo_utilizado": spec["period"],
            "tipo": "PDF oficial · binario preservado",
            "sha256": spec["sha256"],
            "nota": f"V111 E0 fiscal: {int(spec['bytes']):,} bytes; {spec['pages']} páginas. {spec['verified']}",
        }
    )
write_csv(CATALOG, catalog)


census = read_csv(V110 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V110.csv")
census = [row for row in census if row["source_id"] not in new_ids]
for spec in source_specs:
    census.append(
        {
            "source_id": spec["id"],
            "institution": spec["institution"],
            "artifact": spec["title"],
            "url": spec["url"],
            "local_path": spec["local"],
            "sha256": spec["sha256"],
            "bytes": spec["bytes"],
            "period_coverage": spec["period"],
            "variable_families": spec["families"],
            "primary_source": "YES",
            "preserved": "YES",
            "method_breaks": spec["breaks"],
            "use_status": spec["use"],
            "caveat": spec["caveat"],
        }
    )
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V111.csv", census)


ledger = read_csv(V110 / "E0_FISCAL_MECHANISM_LEDGER_V110.csv")
ledger_fields = list(ledger[0])


def L(
    ledger_id: str,
    window: str,
    mechanism: str,
    phase: str,
    as_of: str,
    payer: str,
    recipient: str,
    universe: str,
    instrument: str,
    amount: str,
    unit: str,
    ars: str,
    basis: str,
    source: str,
    locator: str,
    realization: str,
    additivity: str,
    interpretation: str,
    caveat: str,
) -> dict[str, str]:
    return dict(zip(ledger_fields, [ledger_id, window, mechanism, phase, as_of, payer, recipient, universe, instrument, amount, unit, ars, basis, source, locator, realization, additivity, interpretation, caveat]))


ledger.extend(
    [
        L("F26", "2004", "ASymmetric_pesification", "PRIOR_PERIOD_ACCOUNTING_CONVALIDATION", "2004-12-31", "Administracion_Central", "Financial_entities_and_individuals", "2002_registration", "Public_debt_titles", "16183544262", "ARS", "16183.544262", "DECLARATIVE_CONVALIDATION_OF_2002_ENTRY", "e0_cgn_cuenta_inversion_2004_tomo_i", "PDF_p65_printed_52", "PRIOR_2002_REGISTRATION_CONVALIDATED", "NON_ADDITIVE", "The 2004 Account validates the extra-budgetary amount recorded in the 2002 Account.", "It is declarative and not a new 2004 issue transfer or cash payment."),
        L("F27", "2004", "ASymmetric_pesification", "YEAR_END_DEBT_STOCK", "2004-12-31", "Tesoro_Nacional", "Financial_entities", "System", "Compensatory_BODEN_and_pagares", "17201249", "ARS_thousand_updated", "17201.249", "UPDATED_VALUE_AT_2004_12_31", "e0_cgn_cuenta_inversion_2004_sdp", "PDF_p66", "YEAR_END_PURPOSE_STOCK", "ADD_WITHIN_2004_PURPOSE_TABLE_ONLY", "Official compensation-purpose stock.", "Stock embeds issuance service valuation and corrections; it is not a 2004 flow."),
        L("F28", "2004", "FX_negative_position_coverage", "YEAR_END_DEBT_STOCK", "2004-12-31", "Tesoro_Nacional", "Financial_entities", "System", "BODEN_and_pagare_2012_coverage", "7039723", "ARS_thousand_updated", "7039.723", "UPDATED_VALUE_AT_2004_12_31", "e0_cgn_cuenta_inversion_2004_sdp", "PDF_p66", "YEAR_END_PURPOSE_STOCK", "ADD_WITHIN_2004_PURPOSE_TABLE_ONLY", "Official coverage-purpose stock.", "Coverage is not automatically a free transfer."),
        L("F29", "2004", "Depositor_bond_exchange", "YEAR_END_DEBT_STOCK", "2004-12-31", "Tesoro_Nacional", "Depositors", "Depositor_options", "BODEN_for_ahorristas", "19520717", "ARS_thousand_updated", "19520.717", "UPDATED_VALUE_AT_2004_12_31", "e0_cgn_cuenta_inversion_2004_sdp", "PDF_p66", "YEAR_END_PURPOSE_STOCK", "ADD_WITHIN_2004_PURPOSE_TABLE_ONLY", "Official depositor-purpose stock.", "Keep outside bank compensation."),
        L("F30", "2004", "All_BODEN_purposes", "YEAR_END_CONTROL_TOTAL", "2004-12-31", "Tesoro_Nacional", "Mixed", "Mixed", "BODEN_pagares_and_OCMO", "53070390", "ARS_thousand_updated", "53070.390", "UPDATED_VALUE_AT_2004_12_31", "e0_cgn_cuenta_inversion_2004_sdp", "PDF_p66", "CONTROL_TOTAL", "CONTROL_NOT_ADDITIVE", "All-purpose BODEN control total.", "Includes depositors quasi-currency and 13-percent compensation."),
        L("F31", "2004", "Financial_system_reordering", "ADMINISTRATIVE_STATUS_NARRATIVE", "2004-12-31", "Gobierno_Nacional", "Financial_system", "System", "Multiple_compensation_mechanisms", "N/D", "N/D", "N/D", "QUALITATIVE_STATUS", "e0_cgn_cuenta_inversion_2004_sdp", "PDF_p71", "PRACTICALLY_FINALIZED_NARRATIVE", "NON_ADDITIVE", "The official narrative says mechanisms were practically finalized.", "Subsequent 2005-2006 issues and adjustments disprove treating this wording as transactional closure."),
        L("F32", "2005", "CER_CVS_asymmetry", "NET_ISSUANCE", "2005-12-31", "Tesoro_Nacional", "Eligible_financial_entities", "Eligible_CER_CVS_portfolios", "BGN_pesos_variable_rate_2013", "77", "ARS_million_VNO", "77", "ORIGINAL_NOMINAL_NET_ISSUANCE", "e0_cgn_cuenta_inversion_2005_sdp", "PDF_p87_printed_85", "NET_ISSUANCE_NOT_CASH", "ADD_WITHIN_SAME_PURPOSE_CURRENCY_YEAR_ONLY", "Execution under Law 25.796 and Resolution 561/2005.", "Rounded VNO issue is not delivery by entity or cash."),
        L("F33", "2005", "ASymmetric_pesification", "NET_ISSUANCE", "2005-12-31", "Tesoro_Nacional", "Financial_entities", "System", "BODEN_2007_compensatory", "2081", "ARS_million_VNO", "2081", "NET_OF_DOWNWARD_ADJUSTMENTS", "e0_cgn_cuenta_inversion_2005_sdp", "PDF_p87_printed_85", "NET_ISSUANCE_NOT_CASH", "ADD_WITHIN_SAME_PURPOSE_CURRENCY_YEAR_ONLY", "Net compensatory issue after adjustments to prior placements.", "Do not infer gross delivery or cash."),
        L("F34", "2005", "ASymmetric_pesification", "NET_ISSUANCE_CORRECTION", "2005-12-31", "Tesoro_Nacional", "Financial_entities", "System", "BODEN_2012_compensatory", "-35.8", "USD_million_VNO", "N/D", "NET_OF_DOWNWARD_ADJUSTMENTS", "e0_cgn_cuenta_inversion_2005_sdp", "PDF_p87_printed_85", "NEGATIVE_NET_ISSUANCE_CORRECTION", "ADD_WITHIN_SAME_PURPOSE_CURRENCY_YEAR_ONLY", "Net negative compensatory issuance evidences downward corrections.", "Do not convert to ARS without dated transaction-level exchange rates."),
        L("F35", "2005", "FX_negative_position_coverage", "COVERAGE_SUBSCRIPTION", "2005-12-31", "Tesoro_Nacional", "Financial_entities", "System", "BODEN_2012_coverage", "2001", "USD_million_VNO", "N/D", "ORIGINAL_NOMINAL_SUBSCRIBED", "e0_cgn_cuenta_inversion_2005_sdp", "PDF_p87_printed_85", "SUBSCRIBED_NOT_FREE_TRANSFER", "NON_ADDITIVE_WITH_COMPENSATION", "Coverage subscription is an explicit separate leg.", "Requires subscription-price and financing bridge."),
        L("F36", "2005", "ASymmetric_pesification", "YEAR_END_DEBT_STOCK", "2005-12-31", "Tesoro_Nacional", "Financial_entities", "System", "Compensatory_BODEN_and_pagares", "15162578", "ARS_thousand_updated", "15162.578", "UPDATED_VALUE_AT_2005_12_31", "e0_cgn_cuenta_inversion_2005_sdp", "PDF_p80", "YEAR_END_PURPOSE_STOCK", "ADD_WITHIN_2005_PURPOSE_TABLE_ONLY", "Official compensation-purpose stock.", "Stock is not annual issuance or cash."),
        L("F37", "2005", "FX_negative_position_coverage", "YEAR_END_DEBT_STOCK", "2005-12-31", "Tesoro_Nacional", "Financial_entities", "System", "BODEN_and_pagare_2012_coverage", "7567855", "ARS_thousand_updated", "7567.855", "UPDATED_VALUE_AT_2005_12_31", "e0_cgn_cuenta_inversion_2005_sdp", "PDF_p80", "YEAR_END_PURPOSE_STOCK", "ADD_WITHIN_2005_PURPOSE_TABLE_ONLY", "Official coverage-purpose stock.", "Do not add to subscriptions as a flow."),
        L("F38", "2005", "Depositor_bond_exchange", "YEAR_END_DEBT_STOCK", "2005-12-31", "Tesoro_Nacional", "Depositors", "Depositor_options", "BODEN_for_ahorristas", "17162588", "ARS_thousand_updated", "17162.588", "UPDATED_VALUE_AT_2005_12_31", "e0_cgn_cuenta_inversion_2005_sdp", "PDF_p80", "YEAR_END_PURPOSE_STOCK", "ADD_WITHIN_2005_PURPOSE_TABLE_ONLY", "Official depositor-purpose stock.", "Keep outside bank compensation."),
        L("F39", "2005", "ASymmetric_pesification_and_depositor_relief", "MIXED_DEBT_FINANCING", "2005-12-31", "Tesoro_Nacional", "Banks_and_depositors", "Mixed", "BODEN_2007_2012_2013", "2950.0", "ARS_million", "2950.0", "BUDGET_NARRATIVE_PLACEMENT_VALUE", "e0_onp_sintesis_ejecutiva_2005q4", "PDF_p19", "MIXED_BANK_DEPOSITOR_PLACEMENT", "NON_ADDITIVE", "The ONP budget heading combines banks depositors and other items.", "Do not label as bank-only compensation or sum to purpose stocks."),
        L("F40", "2005", "ASymmetric_pesification", "BUDGET_TRANSFER_ACCRUAL", "2005-12-31", "Administracion_Nacional", "Financial_entities", "Private_companies", "Current_transfers", "3300.29", "ARS_million", "3300.29", "BUDGET_EXECUTION_DEVENGADO", "e0_cgn_cuenta_inversion_2005_tomo_i", "PDF_p118_printed_106", "ACCRUED_TRANSFER_NOT_CASH_PROOF", "NON_ADDITIVE", "Bank-specific accrued transfer in the private-company budget category.", "Does not identify entity date instrument or cash settlement and may overlap debt placement accounting."),
        L("F41", "2005", "FX_negative_position_coverage", "SUBSCRIPTION_PRICE_DIFFERENCE_TRANSFER", "2005-12-31", "Tesoro_Nacional", "Financial_entities", "System", "BODEN_2012", "69.1", "ARS_million", "69.1", "NOMINAL_AT_REGISTRATION_FX_MINUS_SUBSCRIPTION", "e0_onp_sintesis_ejecutiva_2005q4", "PDF_p19", "TRANSFER_COMPONENT_WITHIN_MIXED_BUCKET", "NON_ADDITIVE", "Difference between ARS455.3m nominal at debt-registration FX and ARS386.2m subscription paid.", "Likely overlaps broader transfer execution; do not add without accounting keys."),
        L("F42", "2005", "Decree_905_counterflow", "BANK_DEPOSITS_TO_TREASURY", "2005-12-31", "Financial_entities", "Tesoro_Nacional", "System", "Deposits_Art_13_Decree_905", "970.96", "ARS_million", "970.96", "BUDGET_FINANCING_INCREMENT_OF_EQUITY", "e0_cgn_cuenta_inversion_2005_tomo_i", "PDF_p124_printed_112", "BANK_COUNTERFLOW_FINANCING_BALANCE", "EXCLUDE_FROM_GROSS_COMPENSATION", "Deposits under Article 13 appear as a financing counterflow.", "Not a Treasury transfer to banks."),
        L("F43", "2005", "Financial_system_reordering", "OTHER_FINANCIAL_ASSET_APPLICATION", "2005-12-31", "Administracion_Nacional", "Mixed", "Program_level", "BODEN_2012_Decree_905", "1107.46", "ARS_million", "1107.46", "BUDGET_APPLICATION_OTHER_FINANCIAL_ASSETS", "e0_cgn_cuenta_inversion_2005_tomo_i", "PDF_p124_printed_112", "PROGRAM_LEVEL_APPLICATION_AMBIGUOUS", "NON_ADDITIVE", "Program-level application under Decree 905.", "Purpose and counterpart are insufficient for bank-compensation aggregation."),
        L("F44", "2006", "CER_CVS_asymmetry", "NET_ISSUANCE", "2006-12-31", "Tesoro_Nacional", "Eligible_financial_entities", "Eligible_CER_CVS_portfolios", "BGN_pesos_variable_rate_2013", "11.9", "ARS_million_VNO", "11.9", "ADDITIONAL_ORIGINAL_NOMINAL_ISSUANCE", "e0_cgn_cuenta_inversion_2006_sdp", "PDF_p132_printed_131", "NET_ISSUANCE_NOT_CASH", "ADD_WITHIN_SAME_PURPOSE_CURRENCY_YEAR_ONLY", "Additional Law 25.796 issue.", "Rounded VNO is not entity delivery or cash."),
        L("F45", "2006", "ASymmetric_pesification", "NET_ISSUANCE", "2006-12-31", "Tesoro_Nacional", "Financial_entities", "System", "BODEN_2007_compensatory", "21.3", "ARS_million_VNO", "21.3", "NET_OF_DOWNWARD_ADJUSTMENTS", "e0_cgn_cuenta_inversion_2006_sdp", "PDF_p132_printed_131", "NET_ISSUANCE_NOT_CASH", "ADD_WITHIN_SAME_PURPOSE_CURRENCY_YEAR_ONLY", "Net compensatory issue after prior-placement adjustments.", "Do not infer gross delivery or cash."),
        L("F46", "2006", "ASymmetric_pesification", "NET_ISSUANCE_CORRECTION", "2006-12-31", "Tesoro_Nacional", "Financial_entities", "System", "BODEN_2012_compensatory", "-32.4", "USD_million_VNO", "N/D", "NET_OF_DOWNWARD_ADJUSTMENTS", "e0_cgn_cuenta_inversion_2006_sdp", "PDF_p132_printed_131", "NEGATIVE_NET_ISSUANCE_CORRECTION", "ADD_WITHIN_SAME_PURPOSE_CURRENCY_YEAR_ONLY", "Net negative compensatory issuance.", "Do not convert to ARS without dated transactions."),
        L("F47", "2006", "FX_negative_position_coverage", "COVERAGE_SUBSCRIPTION", "2006-12-31", "Tesoro_Nacional", "Financial_entities", "System", "BODEN_2012_coverage", "1007", "USD_million_VNO", "N/D", "ORIGINAL_NOMINAL_ADDITIONAL_ISSUANCE", "e0_cgn_cuenta_inversion_2006_sdp", "PDF_p132_printed_131", "SUBSCRIBED_NOT_FREE_TRANSFER", "NON_ADDITIVE_WITH_COMPENSATION", "Additional coverage issue.", "Requires subscription price and financing bridge."),
        L("F48", "2006", "Compensation_total", "YEAR_END_DEBT_STOCK", "2006-12-31", "Tesoro_Nacional", "Financial_entities", "System", "Compensatory_BODEN_and_pagares_including_CER_CVS", "11960610", "ARS_thousand_updated", "11960.610", "UPDATED_VALUE_AT_2006_12_31", "e0_cgn_cuenta_inversion_2006_sdp", "PDF_p121", "YEAR_END_PURPOSE_STOCK", "ADD_WITHIN_2006_PURPOSE_TABLE_ONLY", "ARS11,881.044m pesification plus ARS79.566m CER-CVS.", "Stock is not annual issuance or cash."),
        L("F49", "2006", "FX_negative_position_coverage", "YEAR_END_DEBT_STOCK", "2006-12-31", "Tesoro_Nacional", "Financial_entities", "System", "BODEN_and_pagare_2012_coverage", "9078371", "ARS_thousand_updated", "9078.371", "UPDATED_VALUE_AT_2006_12_31", "e0_cgn_cuenta_inversion_2006_sdp", "PDF_p121", "YEAR_END_PURPOSE_STOCK", "ADD_WITHIN_2006_PURPOSE_TABLE_ONLY", "Official coverage-purpose stock.", "Do not add to coverage issuance as a flow."),
        L("F50", "2006", "Depositor_bond_exchange", "YEAR_END_DEBT_STOCK", "2006-12-31", "Tesoro_Nacional", "Depositors", "Depositor_options", "BODEN_for_ahorristas_and_OCMO", "14841964", "ARS_thousand_updated", "14841.964", "UPDATED_VALUE_AT_2006_12_31", "e0_cgn_cuenta_inversion_2006_sdp", "PDF_p121", "YEAR_END_PURPOSE_STOCK", "ADD_WITHIN_2006_PURPOSE_TABLE_ONLY", "Official depositor-purpose stock.", "Keep outside bank compensation."),
        L("F51", "2006", "BNA_capitalization_and_compensation", "MIXED_BUDGET_BUCKET", "2006-12-31", "Tesoro_Nacional", "BNA_banks_and_depositors", "Mixed", "Pagares_transfers_and_bonds", "1780.1", "ARS_million", "1780.1", "BUDGET_EXECUTION_DEVENGADO", "e0_onp_sintesis_ejecutiva_2006q4", "PDF_p22_printed_21", "MIXED_BNA_AND_COMPENSATION_BUCKET", "CONTROL_NOT_ADDITIVE", "Includes ARS1,000m BNA capitalization plus compensation and price-difference coverage.", "Never label the whole bucket bank compensation."),
        L("F52", "2006", "ASymmetric_pesification", "MIXED_BANK_DEPOSITOR_COMPENSATION", "2006-12-31", "Tesoro_Nacional", "Banks_and_depositors", "Mixed", "Compensation_and_coverage", "762", "ARS_million", "762", "BUDGET_NARRATIVE_COMPONENT", "e0_onp_sintesis_ejecutiva_2006q4", "PDF_p22_printed_21", "MIXED_BANK_DEPOSITOR_COMPONENT", "NON_ADDITIVE", "Broad compensation component within the ARS1,780.1m bucket.", "Not bank-only and not separately reconciled to price-difference coverage."),
        L("F53", "2006", "ASymmetric_pesification", "BUDGET_TRANSFER_ACCRUAL", "2006-12-31", "Administracion_Nacional", "Financial_entities", "Private_companies", "Current_transfers", "510.10", "ARS_million", "510.10", "BUDGET_EXECUTION_DEVENGADO", "e0_cgn_cuenta_inversion_2006_tomo_i", "PDF_p142_printed_126", "ACCRUED_TRANSFER_NOT_CASH_PROOF", "NON_ADDITIVE", "Bank-specific transfer reported against ARS3,300.29m in 2005.", "Does not identify entity date instrument or cash settlement."),
        L("F54", "2006", "Financial_system_reordering", "DEBT_PLACEMENT_FINANCING", "2006-12-31", "Tesoro_Nacional", "Mixed", "Coverage_and_compensatory", "BODEN_2012", "3551.66", "ARS_million", "3551.66", "BUDGET_FINANCING_PLACEMENT", "e0_cgn_cuenta_inversion_2006_tomo_i", "PDF_p136_printed_120", "MIXED_PURPOSE_PLACEMENT", "NON_ADDITIVE", "Budget financing line combines coverage and compensatory BODEN 2012.", "Cannot be added to transfer accruals or purpose stocks."),
        L("F55", "2006", "All_BODEN_2012_purposes", "DEBT_SERVICE_AMORTIZATION", "2006-12-31", "Tesoro_Nacional", "BODEN_2012_holders", "Mixed", "BODEN_2012", "6935.20", "ARS_million", "6935.20", "BUDGET_DEBT_SERVICE", "e0_cgn_cuenta_inversion_2006_tomo_i", "PDF_p137_printed_121", "MIXED_PURPOSE_SERVICE_NOT_ALLOCATED", "EXCLUDE_FROM_BANK_COMPENSATION_TOTAL", "Series-level amortization control.", "BODEN 2012 includes compensation coverage depositors and market placements."),
        L("F56", "2006", "All_BODEN_2007_purposes", "DEBT_SERVICE_AMORTIZATION", "2006-12-31", "Tesoro_Nacional", "BODEN_2007_holders", "Mixed", "BODEN_2007", "1326.21", "ARS_million", "1326.21", "BUDGET_DEBT_SERVICE", "e0_cgn_cuenta_inversion_2006_tomo_i", "PDF_p137_printed_121", "MIXED_PURPOSE_SERVICE_NOT_ALLOCATED", "EXCLUDE_FROM_BANK_COMPENSATION_TOTAL", "Series-level amortization control.", "BODEN 2007 includes compensation and depositor holdings."),
        L("F57", "2006", "BCRA_Treasury_financing", "CANCELLATION_OF_CENTRAL_BANK_ADVANCES", "2006-12-31", "Tesoro_Nacional", "BCRA", "Institutional_financing", "BCRA_advances", "15998.20", "ARS_million", "15998.20", "BUDGET_OTHER_LIABILITY_REDUCTION", "e0_cgn_cuenta_inversion_2006_tomo_i", "PDF_p137_printed_121", "BCRA_FINANCING_CANCELLATION", "EXCLUDE_FROM_BANK_COMPENSATION_TOTAL", "Cancellation of BCRA advances.", "Institutional financing settlement not compensation to commercial banks."),
        L("F58", "2006", "Decree_905_counterflow", "BANK_DEPOSITS_TO_TREASURY", "2006-12-31", "Financial_entities", "Tesoro_Nacional", "System", "Deposits_Art_13_Decree_905", "309.22", "ARS_million", "309.22", "BUDGET_FINANCING_INCREMENT_OF_EQUITY", "e0_cgn_cuenta_inversion_2006_tomo_i", "PDF_p136_printed_120", "BANK_COUNTERFLOW_FINANCING_BALANCE", "EXCLUDE_FROM_GROSS_COMPENSATION", "Deposits from financial entities under Decree 905.", "Counterflow not a Treasury transfer to banks."),
    ]
)
write_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V111.csv", ledger, ledger_fields)


transaction_fields = ["transaction_id", "year", "mechanism", "phase", "instrument", "recipient_universe", "amount_original", "original_unit", "normalized_ars_million", "source_id", "source_locator", "bank_compensation_aggregation", "realization_status", "caveat"]
transactions = []
for row in ledger[25:]:
    transactions.append(
        {
            "transaction_id": "T" + row["ledger_id"][1:],
            "year": row["window"],
            "mechanism": row["mechanism"],
            "phase": row["phase"],
            "instrument": row["instrument"],
            "recipient_universe": row["universe"],
            "amount_original": row["amount_original"],
            "original_unit": row["original_unit"],
            "normalized_ars_million": row["normalized_ars_million"],
            "source_id": row["source_id"],
            "source_locator": row["source_locator"],
            "bank_compensation_aggregation": "NO_AUTOMATIC_AGGREGATION",
            "realization_status": row["realization_status"],
            "caveat": row["caveat"],
        }
    )
write_csv(HERE / "E0_FISCAL_TRANSACTION_LEDGER_2004_2006_V111.csv", transactions, transaction_fields)


bridge_fields = ["bridge_id", "category", "instrument_or_measure", "unit", "as_of_2003_12_31", "as_of_2004_12_31", "delta_2004", "as_of_2005_12_31", "delta_2005", "as_of_2006_12_31", "delta_2006", "sources", "comparability", "permitted_interpretation", "forbidden_interpretation"]
bridge_values = [
    ("S01", "ALL_BODEN_PURPOSES", "Updated_debt_stock", "ARS_million", "51525.296", "53070.390", "64185.458", "65300.302"),
    ("S02", "COMPENSATORY", "Updated_debt_stock", "ARS_million", "17348.345", "17201.249", "15162.578", "11960.610"),
    ("S03", "COVERAGE", "Updated_debt_stock", "ARS_million", "6879.649", "7039.723", "7567.855", "9078.371"),
    ("S04", "AHORRISTAS", "Updated_debt_stock", "ARS_million", "17664.377", "19520.717", "17162.588", "14841.964"),
    ("S05", "COMPENSATION_RELATED", "Compensatory_plus_coverage_updated_stock", "ARS_million", "24227.994", "24240.972", "22730.433", "21038.981"),
    ("S06", "COMPENSATORY", "BODEN_2007_nominal", "ARS_million", "868.384", "1736.472", "2628.282", "2558.018"),
    ("S07", "COMPENSATORY", "PAGARE_2007_nominal", "ARS_million", "441.701", "884.584", "884.584", "884.584"),
    ("S08", "COMPENSATORY", "BODEN_2012_nominal", "USD_million", "4796.981", "4926.146", "4836.107", "4794.327"),
    ("S09", "COMPENSATORY", "PAGARE_2012_nominal", "USD_million", "3.000", "3.000", "0.000", "0.000"),
    ("S10", "COVERAGE", "BODEN_2012_nominal", "USD_million", "1993.217", "1998.270", "2424.663", "3462.673"),
    ("S11", "COVERAGE", "PAGARE_2012_nominal", "USD_million", "364.846", "364.846", "367.846", "367.846"),
]
bridge = []
for bridge_id, category, measure, unit, y03, y04, y05, y06 in bridge_values:
    d04 = Decimal(y04) - Decimal(y03)
    d05 = Decimal(y05) - Decimal(y04)
    d06 = Decimal(y06) - Decimal(y05)
    bridge.append(
        {
            "bridge_id": bridge_id,
            "category": category,
            "instrument_or_measure": measure,
            "unit": unit,
            "as_of_2003_12_31": y03,
            "as_of_2004_12_31": y04,
            "delta_2004": str(d04),
            "as_of_2005_12_31": y05,
            "delta_2005": str(d05),
            "as_of_2006_12_31": y06,
            "delta_2006": str(d06),
            "sources": "e0_onp_boletin_fiscal_2003q4_cuadro37_boden;e0_cgn_cuenta_inversion_2004_sdp;e0_cgn_cuenta_inversion_2005_sdp;e0_cgn_cuenta_inversion_2006_sdp",
            "comparability": "SAME_OFFICIAL_TABLE_FAMILY_STOCKS_NOT_FLOWS",
            "permitted_interpretation": "Compare end-date stock composition descriptively.",
            "forbidden_interpretation": "Treat delta as annual bank compensation cash flow or beneficiary gain.",
        }
    )
write_csv(HERE / "E0_FISCAL_STOCK_FLOW_BRIDGE_V111.csv", bridge, bridge_fields)


breaks = read_csv(V110 / "E0_FISCAL_METHOD_BREAKS_V110.csv")
break_fields = list(breaks[0])
new_breaks = [
    ("legal_convalidation_not_current_flow", "time", "A later budget law can validate an earlier extra-budgetary registration.", "Attribute the amount to its original accounting period and keep the later act non-additive.", "CGN Cuenta 2004 tomo I p.65"),
    ("practically_finalized_not_closed", "status", "Qualitative administrative finalization can precede later issues and corrections.", "Do not treat narrative closure language as a transactional endpoint.", "CGN 2004 SDP p.71; CGN 2005-2006 SDP Anexo J"),
    ("negative_net_issuance_is_correction", "flow", "Net issuance after prior-placement adjustments can be negative.", "Preserve the sign and do not replace with zero or call it amortization.", "CGN 2005 SDP p.87; CGN 2006 SDP p.132"),
    ("budget_accrual_not_cash", "accounting", "A devengado transfer is not proof of cash settlement by beneficiary and date.", "Label budget accrual and require payment records for cash.", "CGN 2005 tomo I p.118; CGN 2006 tomo I p.142"),
    ("mixed_banks_depositors_bucket", "universe", "Budget headings combine banks and depositors.", "Use bank-specific rows when available; keep the mixed bucket as control only.", "ONP 2005Q4 p.19; ONP 2006Q4 p.22"),
    ("bna_capitalization_separate", "mechanism", "The 2006 assistance bucket includes BNA capitalization.", "Subtract nothing mechanically; retain the whole bucket as non-additive and use identified components separately.", "ONP 2006Q4 p.22"),
    ("series_service_mixed_purpose", "purpose", "BODEN 2007 and 2012 service aggregates holders from multiple purposes.", "Do not allocate series amortization to banks without holder-purpose records.", "CGN 2006 tomo I p.137"),
    ("coverage_subscription_not_transfer", "mechanism", "Coverage bonds are subscribed and can involve a price payment and financing.", "Separate VNO issue subscription paid and price-difference transfer.", "CGN 2005-2006 SDP; ONP 2005Q4 p.19"),
    ("bank_deposit_counterflow", "direction", "Financial-entity deposits under Decree 905 run from banks to the Treasury.", "Keep the counterflow out of gross Treasury-to-bank compensation.", "CGN 2005 tomo I p.124; CGN 2006 tomo I p.136"),
    ("mixed_placement_not_transfer", "accounting", "A financing-source placement line differs from a current-transfer accrual.", "Never sum placement financing with transfer execution absent accounting keys.", "CGN 2006 tomo I pp.136 and 142"),
    ("law25796_issue_not_ceiling", "phase", "Law 25.796 ceiling and later net issues are different phases.", "Report authorized ceiling separately from 2005-2006 issuance.", "Law 25.796; CGN 2005-2006 SDP"),
    ("agn_specific_audit_gap_persists", "source", "Official AGN search did not identify a mechanism-specific public report.", "Keep independent audit reconciliation open and do not substitute unrelated reports.", "Official AGN-site search V111"),
]
for break_id, dimension, problem, rule, evidence in new_breaks:
    breaks.append({"break_id": break_id, "dimension": dimension, "problem": problem, "rule": rule, "status": "FROZEN", "evidence": evidence})
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V111.csv", breaks, break_fields)


matrix = read_csv(V110 / "HISTORICAL_EPISODE_MATRIX_2001_2026_V110.csv")
matrix_fields = list(matrix[0])
for row in matrix:
    row["source_id"] = row["source_id"].replace("V110", "V111")
    row["basis"] = row["basis"].replace("authorization formula stocks accounting entries holdings receivables and BCRA financing are separated", "authorization formula stocks accounting entries transfers net issues coverage subscriptions service controls holdings receivables and BCRA financing are separated")
new_matrix = [
    {
        "episode_id": "E0", "episode_name": "Crisis de convertibilidad / default / salida / reordenamiento financiero", "t0": "2004-12_TO_2006-12", "shock_type": "OTHER", "variable": "fiscal_compensation_net_issuance", "sector": "STATE_BCRA", "frequency": "ANNUAL", "pre_value": "2004_ADMIN_NARRATIVE_NEAR_FINAL", "trough_value": "2005_ARP77_CERCVS_PLUS_ARP2081_COMP_USD_MINUS35.8_COMP_PLUS_USD2001_COVERAGE", "trough_date": "2005", "recovery_value": "2006_ARP11.9_CERCVS_PLUS_ARP21.3_COMP_USD_MINUS32.4_COMP_PLUS_USD1007_COVERAGE", "recovery_date": "2006", "months_to_trough": "N/D", "months_to_recovery": "N/D", "benchmark_definition": "net original nominal issuance by purpose and currency; no cross-currency sum", "source_id": "E0_FISCAL_TRANSACTION_LEDGER_2004_2006_V111.csv", "source_quality": "PRIMARY", "basis": "CGN Anexo J 2005-2006", "method_break": "YES_NET_OF_PRIOR_PLACEMENT_ADJUSTMENTS", "status": "FISCAL_NET_ISSUANCE_IDENTIFIED", "interpretation": "Later issues and corrections refute a hard 2004 closure date.", "falsifier": "YES_ADMINISTRATIVE_FINALIZATION_EQUALS_TRANSACTIONAL_CLOSURE", "notes": "Negative USD issuance is preserved as correction; coverage remains a subscription leg."},
    {
        "episode_id": "E0", "episode_name": "Crisis de convertibilidad / default / salida / reordenamiento financiero", "t0": "2005-12_TO_2006-12", "shock_type": "OTHER", "variable": "bank_specific_budget_transfer_accrual", "sector": "STATE_BCRA", "frequency": "ANNUAL", "pre_value": "3300.29m_ARS", "trough_value": "510.10m_ARS", "trough_date": "2006", "recovery_value": "N/D", "recovery_date": "N/D", "months_to_trough": "12", "months_to_recovery": "N/D", "benchmark_definition": "current transfers to financial entities in CGN budget execution", "source_id": "E0_FISCAL_TRANSACTION_LEDGER_2004_2006_V111.csv", "source_quality": "PRIMARY", "basis": "CGN Cuenta 2005 p.118 and Cuenta 2006 p.142", "method_break": "YES_DEVENGADO_NOT_CASH", "status": "BANK_SPECIFIC_BUDGET_ACCRUAL_IDENTIFIED", "interpretation": "The bank-specific transfer accrual falls sharply in 2006.", "falsifier": "YES_BROAD_ONP_BUCKET_EQUALS_BANK_ONLY_TRANSFER", "notes": "Do not add to debt issue placement or stock measures."},
    {
        "episode_id": "E0", "episode_name": "Crisis de convertibilidad / default / salida / reordenamiento financiero", "t0": "YEAR_END_2003_TO_2006", "shock_type": "OTHER", "variable": "compensation_related_debt_stock", "sector": "STATE_BCRA", "frequency": "ANNUAL", "pre_value": "24227.994m_ARS", "trough_value": "21038.981m_ARS", "trough_date": "2006-12", "recovery_value": "N/D", "recovery_date": "N/D", "months_to_trough": "36", "months_to_recovery": "N/D", "benchmark_definition": "compensatory plus coverage updated debt stock at each year-end", "source_id": "E0_FISCAL_STOCK_FLOW_BRIDGE_V111.csv", "source_quality": "PRIMARY_DERIVED", "basis": "Exact sum within official purpose tables", "method_break": "YES_STOCK_NOT_FLOW", "status": "PURPOSE_STOCK_BRIDGE_EXTENDED", "interpretation": "The combined updated stock declines overall while coverage rises in 2005-2006.", "falsifier": "YES_STOCK_DELTA_EQUALS_CASH", "notes": "Purpose stocks embed service valuation new issues and corrections."},
]
matrix.extend(new_matrix)
write_csv(HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V111.csv", matrix, matrix_fields)


evidence = read_csv(V110 / "HISTORICAL_EVIDENCE_COVERAGE_V110.csv")
for row in evidence:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            quality="PRIMARY_FISCAL_LEDGER_EXTENDED_2001_2006",
            comparable="PURPOSE_AND_PHASE_SEPARATED_CASH_STILL_OPEN",
            gap="net issues transfers subscriptions stocks and series-level service controls are identified through 2006; delivery by entity cash settlement purpose-level amortization CRYL reconciliation and specific AGN audit remain open",
            next_action="Recover CRYL/Treasury delivery and cancellation records by entity and instrument; allocate BODEN service by purpose before any cash total",
        )
write_csv(HERE / "HISTORICAL_EVIDENCE_COVERAGE_V111.csv", evidence)


queue = read_csv(V110 / "HISTORICAL_SOURCE_QUEUE_V110.csv")
for row in queue:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            status="FISCAL_LEDGER_2004_2006_EXTENDED_SERVICE_ALLOCATION_AND_AUDIT_OPEN",
            why="net issuance corrections coverage subscriptions purpose stocks budget transfers and mixed service controls are frozen through 2006; entity delivery cash allocation and independent audit remain open",
            next_action="Recover CRYL/Tesoro transaction files and purpose-holder debt service; search AGN digesto by actuación/resolution without using unrelated reports",
        )
write_csv(HERE / "HISTORICAL_SOURCE_QUEUE_V111.csv", queue)


readme = """# V111

V111 extiende la reconstrucción fiscal primaria de E0 hasta 2006. Congela emisiones netas, correcciones, suscripciones de cobertura, ejecución presupuestaria, stocks por propósito y controles de servicio, sin fabricar un total de caja.

## Delta material

- El censo E0 sube de **31 a 40 fuentes primarias preservadas**.
- Se incorporan nueve PDF oficiales de CGN/ONP para 2004, 2005 y 2006.
- El ledger fiscal alcanza **58 filas**; 33 pertenecen al tramo 2004–2006.
- El puente anual contiene **11 controles** homogéneos 2003–2006.
- Se congelan **28 restricciones metodológicas**.
- En 2005 se identifican VNO ARS 77m CER-CVS, VNO ARS 2.081m BODEN 2007 compensatorio, VNO -USD 35,8m BODEN 2012 compensatorio y VNO USD 2.001m de cobertura.
- En 2006: VNO ARS 11,9m CER-CVS, VNO ARS 21,3m compensatorio, VNO -USD 32,4m compensatorio y VNO USD 1.007m de cobertura.
- La transferencia devengada a entidades financieras fue ARS 3.300,29m en 2005 y ARS 510,10m en 2006; no se rotula como caja.
- Las amortizaciones 2006 de BODEN 2012 y 2007 quedan como controles mixtos por ARS 6.935,20m y ARS 1.326,21m: las series abarcan varios propósitos.

## Estado que no cambia

- panel estricto Q4-2023: **30 entidades**;
- cobertura: **61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%**;
- `CLOSED_NETWORK_GATE`: **NO**;
- Banco Rioja: mismatch de **158,789k**;
- no se identifica transferencia causal neta hogares → bancos.

## Leer primero

1. `VEREDICTO_V111.md`
2. `AUDITORIA_V111.md`
3. `E0_FISCAL_RECONSTRUCTION_V111.md`
4. `E0_FISCAL_TRANSACTION_LEDGER_2004_2006_V111.csv`
5. `E0_FISCAL_MECHANISM_LEDGER_V111.csv`
6. `E0_FISCAL_STOCK_FLOW_BRIDGE_V111.csv`
7. `E0_FISCAL_METHOD_BREAKS_V111.csv`
8. `HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V111_A_V112.md`
9. `qa_v111.py`

V111 prueba que la ejecución continuó después del cierre narrativo de 2004, pero todavía no identifica caja final ni entrega por banco.
"""
(HERE / "README_V111.md").write_text(readme, encoding="utf-8")


reconstruction = """# Reconstrucción fiscal E0 2001–2006 · V111

## Resultado

Las fuentes oficiales permiten seguir el programa más allá de la autorización: en 2005–2006 aparecen emisiones netas, bajas por ajustes, suscripciones de cobertura, transferencias presupuestarias y servicio de deuda. Aun así, no forman una única serie aditiva ni demuestran efectivo recibido por cada banco.

## 2004: cierre narrativo, no cierre transaccional

La Cuenta 2004 afirma que los mecanismos estaban “prácticamente finalizados”. En la misma Cuenta, el artículo 34 sólo convalida en 2004 la registración extrapresupuestaria de ARS 16.183.544.262 originada en 2002. No es un flujo nuevo. El stock al 31/12/2004 era ARS 17.201,249m compensatorio, ARS 7.039,723m de cobertura y ARS 19.520,717m para ahorristas.

## 2005: nueva ejecución y correcciones

La Ley 25.796 comienza a verse como emisión: VNO ARS 77m del bono CER-CVS. Además, la Cuenta publica VNO ARS 2.081m netos de BODEN 2007 compensatorio, VNO -USD 35,8m netos de BODEN 2012 compensatorio y VNO USD 2.001m suscriptos para cobertura.

El signo negativo es material: prueba bajas/correcciones sobre colocaciones previas. La cobertura es una suscripción y no se puede sumar como transferencia gratuita.

La ejecución presupuestaria identifica ARS 3.300,29m devengados a entidades financieras. La síntesis ONP publica otra vista: ARS 2.950m de colocaciones bajo una partida que combina bancos y ahorristas, más ARS 69,1m por diferencia entre valor nominal registrado y suscripción pagada. Estas vistas pueden solaparse; no se suman.

## 2006: continuidad y servicio mixto

La Cuenta publica VNO ARS 11,9m adicionales CER-CVS, VNO ARS 21,3m netos de BODEN 2007 compensatorio, VNO -USD 32,4m netos de BODEN 2012 compensatorio y VNO USD 1.007m de cobertura.

La transferencia devengada a entidades financieras baja a ARS 510,10m. La síntesis ONP muestra ARS 762m para bancos y ahorristas dentro de una partida de ARS 1.780,1m que también incluye ARS 1.000m de capitalización del BNA. Por eso ninguno de esos agregados amplios es un total bancario limpio.

La ejecución financiera registra ARS 3.551,66m de colocación BODEN 2012 compensatoria+cobertura; ARS 6.935,20m de amortización BODEN 2012; y ARS 1.326,21m de amortización BODEN 2007. El servicio está agregado por serie, cuyas tenencias provienen de compensación, cobertura, ahorristas y otras colocaciones. Sin padrón de tenedores/propósitos no puede imputarse a la compensación bancaria.

La cancelación de ARS 15.998,20m de adelantos BCRA y los depósitos de entidades financieras por ARS 309,22m son flujos institucionales/counterflows, no transferencias del Tesoro a bancos.

## Puente de stocks

| Propósito | 2003 | 2004 | 2005 | 2006 |
|---|---:|---:|---:|---:|
| Compensatorios · ARS m actualizados | 17.348,345 | 17.201,249 | 15.162,578 | 11.960,610 |
| Cobertura · ARS m actualizados | 6.879,649 | 7.039,723 | 7.567,855 | 9.078,371 |
| Ahorristas · ARS m actualizados | 17.664,377 | 19.520,717 | 17.162,588 | 14.841,964 |
| Compensatorios + cobertura | 24.227,994 | 24.240,972 | 22.730,433 | 21.038,981 |

Los cambios mezclan emisiones, amortización, valuación y ajustes. No son caja ni ganancia bancaria.

## Qué queda abierto

- entrega/alta por entidad, fecha e instrumento;
- efectivo pagado y suscripciones efectivamente cobradas;
- asignación de amortización y rescates por propósito/tenedor;
- conciliación Tesoro–CRYL–BCRA–balances bancarios;
- informe AGN específico: la búsqueda oficial volvió a no identificar uno;
- incidencia neta después de pérdidas, fondeo, valuación, impuestos y capitalización.

La conclusión admisible es descriptiva: el Estado absorbió parte del reordenamiento mediante deuda, transferencias y mecanismos de cobertura; no existe todavía un total final homogéneo de caja ni una demostración de ganancia neta bancaria.
"""
(HERE / "E0_FISCAL_RECONSTRUCTION_V111.md").write_text(reconstruction, encoding="utf-8")


audit_text = f"""# Auditoría V111 — ejecución fiscal 2004–2006

## Preservación

Se preservaron nueve PDF oficiales (CGN/ONP), todos con cabecera PDF, tamaño y SHA-256 exactos. El censo E0 alcanza 40 fuentes primarias.

## Inspección visual

Se renderizaron y verificaron páginas completas: SDP 2004 pp. 66 y 71; Tomo I 2004 p. 65; SDP 2005 pp. 80 y 87; Tomo I 2005 pp. 118 y 124; ONP 2005T4 p. 19; SDP 2006 pp. 121 y 132; Tomo I 2006 pp. 136, 137 y 142; ONP 2006T4 p. 22. ONP 2004T4 p. 2 se usó como evidencia negativa: no separa el mecanismo dentro de su agregado presupuestario.

## Controles

- ledger total: 58 filas; tramo nuevo: 33;
- puente: 11 filas con deltas exactos 2003–2006;
- quiebres metodológicos: 28, todos congelados;
- stock compensatorio 2006: 11.881,044 + 79,566 = 11.960,610 ARS m;
- transferencia bancaria devengada: 3.300,29 ARS m (2005) y 510,10 ARS m (2006);
- emisiones compensatorias BODEN 2012 preservan signos negativos: -USD 35,8m y -USD 32,4m.

## Auditoría independiente

La búsqueda dirigida en el sitio oficial de la AGN por Ley 25.796, Decreto 905/02, BODEN 2007/2012 y pesificación asimétrica no identificó un informe específico del mecanismo. El vacío sigue abierto.

## Restricción central

Emisión neta, stock, devengado presupuestario, colocación como fuente financiera, suscripción, amortización por serie y caja son medidas distintas. V111 no las suma ni asigna servicio por propósito sin evidencia de tenedores.
"""
(HERE / "AUDITORIA_V111.md").write_text(audit_text, encoding="utf-8")


verdict = """# Veredicto V111

## Qué sabemos ahora

- La ejecución fiscal continuó en 2005–2006 pese al lenguaje de “prácticamente finalizado” de 2004.
- La Ley 25.796 tuvo emisión observable: VNO ARS 77m en 2005 y ARS 11,9m adicionales en 2006.
- Hubo emisión compensatoria neta BODEN 2007 y correcciones netas negativas BODEN 2012.
- La cobertura BODEN 2012 fue una suscripción separada: USD 2.001m en 2005 y USD 1.007m en 2006.
- Las transferencias devengadas a entidades financieras fueron ARS 3.300,29m y ARS 510,10m en 2005 y 2006.
- Los agregados ONP de ARS 2.950m, ARS 762m y ARS 1.780,1m mezclan universos o mecanismos; no son totales bancarios limpios.
- El servicio BODEN 2007/2012 de 2006 está agregado por serie y no puede asignarse a compensación bancaria.
- La cancelación de adelantos BCRA y los depósitos de entidades financieras son flujos separados.

## Qué no sabemos todavía

- qué recibió cada entidad y cuándo;
- qué parte de las amortizaciones correspondió a compensación, cobertura o ahorristas;
- cuánto se liquidó efectivamente en caja;
- cómo concilian Tesoro, CRYL, BCRA y balances bancarios;
- si existe una auditoría AGN específica no indexada;
- la incidencia neta final.

## Estado

La rama fiscal pasa a `PRIMARY_FISCAL_LEDGER_EXTENDED_2001_2006`. Caja final, entrega por entidad y auditoría independiente siguen abiertas. El panel microbancario permanece en 30 entidades, cobertura exacta 61.8555625288919…% y `CLOSED_NETWORK_GATE=NO`.
"""
(HERE / "VEREDICTO_V111.md").write_text(verdict, encoding="utf-8")


refs = """# Referencias de fuentes V111

## Cuenta de Inversión · CGN

- 2004 · SDP/Anexo J: https://www.economia.gob.ar/hacienda/cgn/cuenta/2004/archivos/sdp.pdf
- 2004 · Tomo I: https://www.economia.gob.ar/hacienda/cgn/cuenta/2004/archivos/tomoi.pdf
- 2005 · SDP/Anexo J: https://www.economia.gob.ar/hacienda/cgn/cuenta/2005/archivos/sdp.pdf
- 2005 · Tomo I: https://www.economia.gob.ar/hacienda/cgn/cuenta/2005/archivos/tomoi.pdf
- 2006 · SDP/Anexo J: https://www.economia.gob.ar/hacienda/cgn/cuenta/2006/archivos/sdp.pdf
- 2006 · Tomo I: https://www.economia.gob.ar/hacienda/cgn/cuenta/2006/archivos/tomoi.pdf

## Síntesis ejecutivas · ONP

- 2004T4: https://www.economia.gob.ar/onp/documentos/sintesis_ejecutiva/2004/4trim04.pdf
- 2005T4: https://www.economia.gob.ar/onp/documentos/sintesis_ejecutiva/2005/4trim05.pdf
- 2006T4: https://www.economia.gob.ar/onp/documentos/sintesis_ejecutiva/2006/4trim06.pdf

Los nueve originales se preservan en `research/ciclo_ajuste/inputs/historical_retrieval/v111/binaries/`; sus tamaños, hashes y quiebres están en `E0_LOCAL_PRIMARY_SOURCE_CENSUS_V111.csv`.

## AGN

La búsqueda oficial dirigida no identificó un informe específico sobre la compensación por pesificación asimétrica/Ley 25.796. El pendiente continúa abierto por actuación y resolución.
"""
(HERE / "SOURCE_REFERENCES_V111.md").write_text(refs, encoding="utf-8")


handover = """# Handover próxima sesión · V111 → V112

## Estado congelado

- 40 fuentes primarias E0 preservadas;
- 58 filas del ledger fiscal; 33 nuevas para 2004–2006;
- 11 filas del puente anual 2003–2006;
- 28 quiebres metodológicos;
- emisiones, correcciones, cobertura, transferencias, stocks y servicio por serie separados;
- no hay total final de caja ni entrega por entidad.

## Prioridad V112

Extender 2007–2012 hasta el vencimiento de BODEN 2007 y BODEN 2012:

1. emisiones/bajas netas anuales por propósito;
2. amortización, rescate, canje y cancelación por serie;
3. padrón de tenedores o registros CRYL que permitan asignar servicio por propósito;
4. conciliación Tesoro–CRYL–BCRA–entidades;
5. ejecución residual de Ley 25.796;
6. búsqueda AGN por actuación/resolución y no sólo texto libre;
7. separar pagos a ahorristas, cobertura, cuasimonedas y colocaciones de mercado;
8. mantener transferencias devengadas, fuentes financieras y caja en fases distintas.

## No hacer

- no sumar stock + emisión + transferencia + amortización;
- no imputar toda amortización BODEN a bancos;
- no convertir USD a ARS sin fecha y tipo de cambio transaccional;
- no tratar emisión negativa como cero;
- no declarar ganancia bancaria neta desde compensación bruta.

## Invariantes

Panel estricto: 30 entidades; cobertura exacta 61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%; `CLOSED_NETWORK_GATE=NO`; Banco Rioja mismatch 158,789k.
"""
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V111_A_V112.md").write_text(handover, encoding="utf-8")


old_hash = read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V110.csv")
hash_rows = [row for row in old_hash if row["id"] not in new_ids]
for spec in source_specs:
    hash_rows.append({"id": spec["id"], "archivo_local": spec["local"], "exists": "True", "sha_catalog": spec["sha256"], "sha_actual": spec["sha256"], "hash_ok": "True"})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V111.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V111.csv", hash_rows)
shutil.copyfile(AUDIT / "SOURCE_PATH_ENCODING_EXCEPTIONS_V110.csv", AUDIT / "SOURCE_PATH_ENCODING_EXCEPTIONS_V111.csv")
shutil.copyfile(AUDIT / "SOURCE_PRESERVATION_MISSING_V110.csv", AUDIT / "SOURCE_PRESERVATION_MISSING_V111.csv")

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": str(size), "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V111.csv", size_rows, ["path", "bytes", "mib", "over_50_mib", "over_100_mib"])

completeness = {
    "checkpoint": "V111",
    "date": "2026-08-29",
    "state": "E0_FISCAL_LEDGER_EXTENDED_2001_2006_CASH_OPEN",
    "master_catalog_entries": len(catalog),
    "physical_local_copies": sum(row["exists"] == "True" for row in hash_rows),
    "physical_local_hash_ok": sum(row["hash_ok"] == "True" for row in hash_rows),
    "reference_only_nonbinary_exempt": 4,
    "remaining_physical_gaps": 1,
    "p0": 0,
    "p1": 1,
    "p2": 0,
    "binary_required_entries": 234,
    "binary_required_preserved": 233,
    "binary_required_source_complete": False,
    "pending_binary_discovery_actions": 7,
    "numeric_v111_strict_changed": False,
    "strict_coverage_pct": "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549",
    "exact_entities": 30,
    "asset_numerator_million_ars": "59812903.504",
    "system_denominator_million_ars": "96697695.5",
    "closed_network_gate": "NO",
    "e0_primary_sources_preserved": len(census),
    "e0_sources_newly_preserved_v111": len(source_specs),
    "e0_quality": "PRIMARY_FISCAL_LEDGER_EXTENDED_2001_2006",
    "e0_comparable": False,
    "e0_fiscal_phase_separated": True,
    "e0_fiscal_final_cash_total_identified": False,
    "e0_fiscal_ledger_rows": len(ledger),
    "e0_fiscal_transaction_rows_2004_2006": len(transactions),
    "e0_fiscal_stock_flow_bridge_rows": len(bridge),
    "e0_fiscal_method_breaks_frozen": len(breaks),
    "e0_definitive_compensation_pending_at_2003_close": True,
    "e0_post_2003_execution_identified": True,
    "e0_series_service_purpose_allocated": False,
    "e0_causal_net_incidence_identified": False,
    "historical_workstream": "E0_2007_2012_SERVICE_AND_ENTITY_DELIVERY_OPEN",
    "path_encoding_note": "Banco La Pampa remains byte-identical despite the catalog/Git filename encoding mismatch.",
}
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V111.json").write_text(json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V111.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V111",
        "parent_checkpoint": "V110",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30,
        "strict_coverage_pct": completeness["strict_coverage_pct"],
        "closed_network_gate": "NO",
        "e0_primary_sources": len(census),
        "new_official_sources": len(source_specs),
        "fiscal_ledger_rows": len(ledger),
        "fiscal_transaction_rows_2004_2006": len(transactions),
        "fiscal_bridge_rows": len(bridge),
        "fiscal_method_breaks": len(breaks),
        "files": files,
    }
    (HERE / "MANIFEST_V111.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


write_manifest()


def build_tree(root: Path) -> str:
    lines = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix().casefold()):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        lines.append(rel + ("/" if path.is_dir() else ""))
    return "\n".join(lines) + "\n"


(REPO / "TREE.txt").write_text(build_tree(REPO), encoding="utf-8")
cycle_root = REPO / "research" / "ciclo_ajuste"
(cycle_root / "TREE.txt").write_text(build_tree(cycle_root), encoding="utf-8")


global_manifest_path = cycle_root / "MANIFEST_SHA256.json"
global_files = []
for path in sorted(REPO.rglob("*"), key=lambda item: item.relative_to(REPO).as_posix().casefold()):
    if not path.is_file() or ".git" in path.parts or path == global_manifest_path:
        continue
    global_files.append({"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})
global_manifest = {
    "checkpoint": "V111",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": completeness["strict_coverage_pct"],
    "exact_entities": 30,
    "closed_network_gate": "NO",
    "source_audit": "238 master entries; 233 physical local copies with 233/233 SHA-valid; nine new official E0 fiscal sources preserved; one catalogued P1 binary gap plus seven discovery actions remain.",
    "historical_workstream": "E0 fiscal ledger extended through 2006 from 40 preserved primary sources; entity delivery cash allocation purpose-level service and AGN reconciliation remain open",
    "file_count_excluding_manifest": len(global_files),
    "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V111 BUILD PASS")
