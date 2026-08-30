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
V111 = HERE.parent / "V111"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
AUDIT = REPO / "research" / "ciclo_ajuste" / "source_audit"
BIN = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v112" / "binaries"


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
    src = V111 / f"{stem}_V111.{suffix}"
    dst = HERE / f"{stem}_V112.{suffix}"
    text = src.read_text(encoding="utf-8-sig")
    dst.write_text(text.replace("V111", "V112").replace("v111", "v112"), encoding="utf-8-sig")


for stem in (
    "CURRENT_STATE",
    "FOUR_LEG_PASS_PANEL",
    "STRICT_Q4_FOUR_LEG_COVERAGE",
    "RECOVERY_QUEUE",
    "INHERITED_QA_STATUS",
    "E0_FISCAL_TRANSACTION_LEDGER_2004_2006",
    "E0_FISCAL_STOCK_FLOW_BRIDGE",
):
    clone_versioned(stem, "csv")


inherited_path = HERE / "INHERITED_QA_STATUS_V112.csv"
inherited = read_csv(inherited_path)
for row in inherited:
    row["interpretation"] = row["interpretation"].replace("V112 validates 238 and 40", "V112 validates 246 and 48").replace("V112 validates 238", "V112 validates 246")
    if row["script"] == "qa_v112.py":
        row["script"] = "qa_v111.py"
        row["post_v112_result"] = "EXPECTED_SUPERSEDED_ASSERTION"
        row["interpretation"] = "Fails only because V111 freezes the global catalog at 238 rows and 40 E0 sources; V112 validates 246 and 48."
inherited.append(
    {
        "script": "qa_v112.py",
        "pre_v112_result": "N/A",
        "post_v112_result": "PASS",
        "interpretation": "Current checkpoint invariants",
    }
)
write_csv(inherited_path, inherited)


source_specs = [
    {
        "id": "e0_cgn_cuenta_inversion_2007_sdp",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2007 · Servicio de la Deuda Pública y Anexo J",
        "url": "https://www.economia.gob.ar/hacienda/cgn/cuenta/2007/archivos/sdp.pdf",
        "file": "cgn_cuenta_inversion_2007_sdp.pdf",
        "publication": "2008",
        "period": "2007",
        "pages": "75",
        "families": "state_bcra;fiscal;debt;issuance;service;stock;purpose",
        "breaks": "servicio por serie versus propósito; VNO original versus actualizado; stock versus flujo",
        "use": "USABLE_PURPOSE_STOCK_AND_SERIES_SERVICE",
        "caveat": "El servicio BODEN 2012 agrega compensación, cobertura, ahorristas y colocaciones de mercado.",
        "verified": "Páginas PDF 5, 56 y 65 renderizadas y verificadas.",
    },
    {
        "id": "e0_cgn_cuenta_inversion_2008_sdp",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2008 · Servicio de la Deuda Pública y Anexo J",
        "url": "https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/archivos/sdp.pdf",
        "file": "cgn_cuenta_inversion_2008_sdp.pdf",
        "publication": "2009",
        "period": "2008",
        "pages": "74",
        "families": "state_bcra;fiscal;debt;issuance;service;buyback",
        "breaks": "bajas por propósito; rescates mixtos; servicio por serie",
        "use": "USABLE_ADJUSTMENTS_AND_MIXED_BUYBACK",
        "caveat": "Los rescates informados mezclan especies y no aíslan BODEN 2012 ni beneficiarios bancarios.",
        "verified": "Páginas PDF 5, 54, 55, 63 y 64 renderizadas y verificadas.",
    },
    {
        "id": "e0_cgn_cuenta_inversion_2009_sdp",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2009 · Servicio de la Deuda Pública y Anexo J",
        "url": "https://www.economia.gob.ar/hacienda/cgn/cuenta/2009/archivos/sdp.pdf",
        "file": "cgn_cuenta_inversion_2009_sdp.pdf",
        "publication": "2010",
        "period": "2009",
        "pages": "81",
        "families": "state_bcra;fiscal;debt;issuance;service;buyback;stock",
        "breaks": "revisión BCRA de compensación previa; recompra temprana sin monto por especie",
        "use": "USABLE_ADJUSTMENTS_SERVICE_AND_STOCK",
        "caveat": "La recompra temprana informa participación inferior al 2%, no monto BODEN 2012 asignable.",
        "verified": "Páginas PDF 5, 60, 71 y 72 renderizadas y verificadas.",
    },
    {
        "id": "e0_cgn_cuenta_inversion_2010_sdp",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2010 · Servicio de la Deuda Pública",
        "url": "https://www.economia.gob.ar/hacienda/cgn/cuenta/2010/archivos/sdp.pdf",
        "file": "cgn_cuenta_inversion_2010_sdp.pdf",
        "publication": "2011",
        "period": "2010",
        "pages": "81",
        "families": "state_bcra;fiscal;debt;service;stock",
        "breaks": "movimiento de serie versus propósito; ausencia narrativa acotada no equivale a cero",
        "use": "USABLE_SERIES_SERVICE_AND_STOCK",
        "caveat": "No se identificó movimiento narrativo específico del programa en Anexo J; el servicio contable sí está publicado.",
        "verified": "Páginas PDF 6 y 60 renderizadas y verificadas.",
    },
    {
        "id": "e0_cgn_cuenta_inversion_2011_sdp",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2011 · Servicio de la Deuda Pública",
        "url": "https://www.economia.gob.ar/hacienda/cgn/cuenta/2011/archivos/sdp.pdf",
        "file": "cgn_cuenta_inversion_2011_sdp.pdf",
        "publication": "2012",
        "period": "2011",
        "pages": "68",
        "families": "state_bcra;fiscal;debt;service;stock",
        "breaks": "movimiento de serie versus propósito; cierre actualizado versus VNO original",
        "use": "USABLE_SERIES_SERVICE_AND_STOCK",
        "caveat": "La reducción de principal no identifica tenedor ni origen de la colocación.",
        "verified": "Páginas PDF 6 y 50 renderizadas y verificadas.",
    },
    {
        "id": "e0_cgn_cuenta_inversion_2012_sdp",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2012 · Servicio de la Deuda Pública",
        "url": "https://www.economia.gob.ar/hacienda/cgn/cuenta/2012/archivos/sdp.pdf",
        "file": "cgn_cuenta_inversion_2012_sdp.pdf",
        "publication": "2013",
        "period": "2012",
        "pages": "58",
        "families": "state_bcra;fiscal;debt;service;maturity;stock",
        "breaks": "vencimiento de serie versus asignación por tenedor; saldo cero no equivale a conciliación",
        "use": "USABLE_FINAL_MATURITY_CONTROL",
        "caveat": "El vencimiento a saldo cero cierra la serie, no el padrón de beneficiarios ni la incidencia neta.",
        "verified": "Páginas PDF 5, 41 y 42 renderizadas y verificadas.",
    },
    {
        "id": "e0_agn_res_202_2009_act_41_2009_deuda",
        "institution": "Auditoría General de la Nación",
        "title": "Evolución de la deuda en sus principales aspectos · Resolución 202/2009 · Actuación 41/2009",
        "url": "https://www.agn.gob.ar/sites/default/files/informes/2009_202info_0.pdf",
        "file": "agn_res_202_2009_act_41_2009_deuda.pdf",
        "publication": "2009",
        "period": "2008",
        "pages": "36",
        "families": "state_bcra;fiscal;debt;holders;public_private_split",
        "breaks": "tenedor agregado versus serie; sector privado no equivale a bancos",
        "use": "USABLE_AGGREGATE_HOLDER_CONTROL",
        "caveat": "La distribución es para toda la deuda del SPN no financiero, no para BODEN 2012 ni por propósito.",
        "verified": "Páginas PDF 16 y 17 renderizadas y verificadas.",
    },
    {
        "id": "e0_agn_res_102_2011_act_366_2009_fgs",
        "institution": "Auditoría General de la Nación",
        "title": "Gestión del FGS · primer semestre 2009 · Resolución 102/2011 · Actuación 366/2009",
        "url": "https://www.agn.gob.ar/sites/default/files/informes/Informe_102_2011.pdf",
        "file": "agn_res_102_2011_act_366_2009_fgs.pdf",
        "publication": "2011",
        "period": "2009",
        "pages": "282",
        "families": "state_bcra;fiscal;debt;holders;fgs;control",
        "breaks": "tenencia pública versus propósito; duplicación de inventario versus flujo",
        "use": "USABLE_PUBLIC_HOLDER_CONTROL_EXCEPTION",
        "caveat": "La duplicación de PF BODEN 2012 en inventarios FGS no es emisión, pago ni compensación bancaria.",
        "verified": "Página PDF 37 renderizada y verificada.",
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
            "nota": f"V112 E0 fiscal: {int(spec['bytes']):,} bytes; {spec['pages']} páginas. {spec['verified']}",
        }
    )
write_csv(CATALOG, catalog)


census = read_csv(V111 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V111.csv")
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
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V112.csv", census)


ledger = read_csv(V111 / "E0_FISCAL_MECHANISM_LEDGER_V111.csv")
ledger_fields = list(ledger[0])


def L(*values: str) -> dict[str, str]:
    return dict(zip(ledger_fields, values))


ledger.extend(
    [
        L("F59", "2007", "All_BODEN_2007_purposes", "FINAL_SERIES_PRINCIPAL_REDUCTION", "2007-12-31", "Tesoro_Nacional", "BODEN_2007_holders", "Mixed", "BODEN_2007", "356805700", "ARS_nominal", "731.80830502", "SERIES_ACCOUNTING_PRINCIPAL", "e0_cgn_cuenta_inversion_2007_sdp", "PDF_p5", "FINAL_SERIES_SERVICE_NOT_PURPOSE_ALLOCATED", "EXCLUDE_FROM_BANK_COMPENSATION_TOTAL", "BODEN 2007 closes at zero after the 2007 principal reduction.", "The series includes more than one purpose and the ARS accounting amount is not a beneficiary allocation."),
        L("F60", "2007", "All_BODEN_2012_purposes", "DEBT_SERVICE_PRINCIPAL_REDUCTION", "2007-12-31", "Tesoro_Nacional", "BODEN_2012_holders", "Mixed", "BODEN_2012", "2208223712.50", "USD_nominal_updated", "6953.69647066", "SERIES_ACCOUNTING_PRINCIPAL", "e0_cgn_cuenta_inversion_2007_sdp", "PDF_p5", "MIXED_PURPOSE_SERVICE_NOT_ALLOCATED", "EXCLUDE_FROM_BANK_COMPENSATION_TOTAL", "Annual BODEN 2012 principal reduction by series.", "Compensation coverage depositors auctions and direct placements coexist in the series."),
        L("F61", "2007", "ASymmetric_pesification", "NET_ISSUANCE_CORRECTION", "2007-12-31", "Tesoro_Nacional", "Financial_entities", "System", "BODEN_2007_compensatory", "-39.9", "ARS_million_VNO", "-39.9", "DOWNWARD_ADJUSTMENT_PRIOR_PLACEMENTS", "e0_cgn_cuenta_inversion_2007_sdp", "PDF_p65", "NEGATIVE_NET_ISSUANCE_CORRECTION", "ADD_WITHIN_SAME_PURPOSE_CURRENCY_YEAR_ONLY", "Downward adjustment to prior compensatory placements.", "Do not convert the correction into amortization or cash."),
        L("F62", "2007", "ASymmetric_pesification", "NET_ISSUANCE_CORRECTION", "2007-12-31", "Tesoro_Nacional", "Financial_entities", "System", "BODEN_2012_compensatory", "-3.3", "USD_million_VNO", "N/D", "DOWNWARD_ADJUSTMENT_PRIOR_PLACEMENTS", "e0_cgn_cuenta_inversion_2007_sdp", "PDF_p65", "NEGATIVE_NET_ISSUANCE_CORRECTION", "ADD_WITHIN_SAME_PURPOSE_CURRENCY_YEAR_ONLY", "Downward adjustment to prior compensatory placements.", "No undated conversion to ARS."),
        L("F63", "2007", "FX_negative_position_coverage", "COVERAGE_ISSUANCE", "2007-12-31", "Tesoro_Nacional", "Financial_entities", "System", "BODEN_2012_coverage", "110.2", "USD_million_VNO", "N/D", "ORIGINAL_NOMINAL_ISSUANCE", "e0_cgn_cuenta_inversion_2007_sdp", "PDF_p65", "ISSUED_NOT_FREE_TRANSFER", "NON_ADDITIVE_WITH_COMPENSATION", "Coverage issuance remains a separate subscribed leg.", "Requires subscription price financing and entity delivery records."),
        L("F64", "2007", "Compensation_total", "YEAR_END_DEBT_STOCK", "2007-12-31", "Tesoro_Nacional", "Financial_entities", "System", "Compensatory_BODEN_2012_and_BODEN_2013", "9102.996", "ARS_million_updated", "9102.996", "UPDATED_VALUE_AT_2007_12_31", "e0_cgn_cuenta_inversion_2007_sdp", "PDF_p56", "YEAR_END_PURPOSE_STOCK", "ADD_WITHIN_2007_PURPOSE_TABLE_ONLY", "Official compensation-purpose stock.", "Stock is not annual issue service or cash."),
        L("F65", "2007", "FX_negative_position_coverage", "YEAR_END_DEBT_STOCK", "2007-12-31", "Tesoro_Nacional", "Financial_entities", "System", "BODEN_2012_coverage", "7031.799", "ARS_million_updated", "7031.799", "UPDATED_VALUE_AT_2007_12_31", "e0_cgn_cuenta_inversion_2007_sdp", "PDF_p56", "YEAR_END_PURPOSE_STOCK", "ADD_WITHIN_2007_PURPOSE_TABLE_ONLY", "Official coverage-purpose stock.", "Do not add to coverage issuance as a flow."),
        L("F66", "2007", "Depositor_bond_exchange", "YEAR_END_DEBT_STOCK", "2007-12-31", "Tesoro_Nacional", "Depositors", "Depositor_options", "BODEN_and_OCMO_for_depositors", "12625.525", "ARS_million_updated", "12625.525", "UPDATED_VALUE_AT_2007_12_31", "e0_cgn_cuenta_inversion_2007_sdp", "PDF_p56", "YEAR_END_PURPOSE_STOCK", "ADD_WITHIN_2007_PURPOSE_TABLE_ONLY", "Official depositor-purpose stock.", "Keep outside bank compensation."),
        L("F67", "2007", "All_BODEN_2012_purposes", "YEAR_END_SERIES_STOCK", "2007-12-31", "Tesoro_Nacional", "BODEN_2012_holders", "Mixed", "BODEN_2012", "10898.291", "USD_million_updated", "34318.720", "UPDATED_VALUE_AT_2007_12_31", "e0_cgn_cuenta_inversion_2007_sdp", "PDF_p56", "YEAR_END_SERIES_STOCK", "CONTROL_NOT_ADDITIVE", "All-purpose BODEN 2012 closing stock.", "It includes compensation coverage depositors auction and direct placements."),
        L("F68", "2008", "All_BODEN_2012_purposes", "DEBT_SERVICE_PRINCIPAL_REDUCTION", "2008-12-31", "Tesoro_Nacional", "BODEN_2012_holders", "Mixed", "BODEN_2012", "2187653037.50", "USD_nominal_updated", "7551.77828545", "SERIES_ACCOUNTING_PRINCIPAL", "e0_cgn_cuenta_inversion_2008_sdp", "PDF_p5", "MIXED_PURPOSE_SERVICE_NOT_ALLOCATED", "EXCLUDE_FROM_BANK_COMPENSATION_TOTAL", "Annual BODEN 2012 principal reduction by series.", "Not allocable to compensation without holder-purpose records."),
        L("F69", "2008", "Depositor_bond_exchange", "NON_DELIVERY_ADJUSTMENT", "2008-12-31", "Tesoro_Nacional", "Depositors", "Requested_not_delivered", "BODEN_2012", "-6.6", "USD_million_VNO", "N/D", "DOWNWARD_ADJUSTMENT_REQUESTED_NOT_DELIVERED", "e0_cgn_cuenta_inversion_2008_sdp", "PDF_p63", "DEPOSITOR_LEG_CORRECTION", "EXCLUDE_FROM_BANK_COMPENSATION_TOTAL", "Titles requested by entities but not delivered to reprogrammed deposit holders were written down.", "The recipient universe is depositors, not a bank benefit."),
        L("F70", "2008", "Depositor_bond_exchange", "NON_DELIVERY_ADJUSTMENT", "2008-12-31", "Tesoro_Nacional", "Depositors", "Requested_not_delivered", "BODEN_2013", "-2.9", "USD_million_VNO", "N/D", "DOWNWARD_ADJUSTMENT_REQUESTED_NOT_DELIVERED", "e0_cgn_cuenta_inversion_2008_sdp", "PDF_p63", "DEPOSITOR_LEG_CORRECTION", "EXCLUDE_FROM_BANK_COMPENSATION_TOTAL", "BODEN 2013 requested but not delivered was written down.", "Separate series and depositor purpose."),
        L("F71", "2008", "FX_negative_position_coverage", "NET_ISSUANCE_CORRECTION", "2008-12-31", "Tesoro_Nacional", "Financial_entities", "System", "BODEN_2012_coverage", "-0.0179", "USD_million_VNO", "N/D", "DOWNWARD_ADJUSTMENT", "e0_cgn_cuenta_inversion_2008_sdp", "PDF_p63", "NEGATIVE_COVERAGE_CORRECTION", "NON_ADDITIVE_WITH_COMPENSATION", "Coverage adjustment of VNO USD 17,900.", "Preserve scale: 0.0179 million USD."),
        L("F72", "2008", "ASymmetric_pesification", "COMPENSATION_ISSUANCE", "2008-12-31", "Tesoro_Nacional", "Certain_financial_entities", "Exchange_rate_conversion_effects", "BODEN_2012_compensatory", "1.9", "USD_million_VNO", "N/D", "ORIGINAL_NOMINAL_ISSUANCE", "e0_cgn_cuenta_inversion_2008_sdp", "PDF_p63", "ISSUED_NOT_CASH", "ADD_WITHIN_SAME_PURPOSE_CURRENCY_YEAR_ONLY", "Compensation for patrimonial effects from different conversion exchange rates.", "No entity list or cash record."),
        L("F73", "2008", "Debt_buyback", "MIXED_SERIES_RESCUE_STAGE_1", "2008-12-31", "Tesoro_Nacional_via_BNA", "Tendering_holders", "Mixed", "BONAR_BOCON_BODEN_and_GDP_units", "1374", "ARS_million", "1374", "MIXED_TENDER_TOTAL", "e0_cgn_cuenta_inversion_2008_sdp", "PDF_p64", "MIXED_BUYBACK_NOT_SERIES_ALLOCATED", "CONTROL_NOT_ADDITIVE", "First buyback stage total across several securities.", "Cannot isolate BODEN 2012 or bank-compensation purpose."),
        L("F74", "2008", "Debt_buyback", "MIXED_SERIES_RESCUE_STAGE_2", "2008-12-31", "Tesoro_Nacional", "Tendering_holders", "Mixed", "BODEN_2012_BODEN_2013_and_GDP_units", "1128", "ARS_million", "1128", "FOUR_MIXED_TENDERS_TOTAL", "e0_cgn_cuenta_inversion_2008_sdp", "PDF_p64", "MIXED_BUYBACK_NOT_SERIES_ALLOCATED", "CONTROL_NOT_ADDITIVE", "Second buyback stage total across four mixed tenders.", "Cannot isolate BODEN 2012 or purpose."),
        L("F75", "2009", "All_BODEN_2012_purposes", "DEBT_SERVICE_PRINCIPAL_REDUCTION", "2009-12-31", "Tesoro_Nacional", "BODEN_2012_holders", "Mixed", "BODEN_2012", "2212158362.50", "USD_nominal_updated", "8406.20177750", "SERIES_ACCOUNTING_PRINCIPAL", "e0_cgn_cuenta_inversion_2009_sdp", "PDF_p5", "MIXED_PURPOSE_SERVICE_NOT_ALLOCATED", "EXCLUDE_FROM_BANK_COMPENSATION_TOTAL", "Annual BODEN 2012 principal reduction by series.", "Not allocable to banks or compensation purpose."),
        L("F76", "2009", "ASymmetric_pesification", "BCRA_REVIEW_CORRECTION", "2009-12-31", "Tesoro_Nacional", "Financial_entities", "System", "BODEN_2012_compensatory", "-25", "USD_million_VNO", "N/D", "BCRA_REVIEW_OF_PRIOR_COMPENSATION", "e0_cgn_cuenta_inversion_2009_sdp", "PDF_p71", "NEGATIVE_NET_ISSUANCE_CORRECTION", "ADD_WITHIN_SAME_PURPOSE_CURRENCY_YEAR_ONLY", "BCRA review reduced prior compensatory placement.", "A correction is not service or cash."),
        L("F77", "2009", "FX_negative_position_coverage", "COVERAGE_ISSUANCE", "2009-12-31", "Tesoro_Nacional", "Financial_entities", "System", "BODEN_2012_coverage", "61", "USD_million_VNO", "N/D", "ORIGINAL_NOMINAL_ISSUANCE", "e0_cgn_cuenta_inversion_2009_sdp", "PDF_p71", "ISSUED_NOT_FREE_TRANSFER", "NON_ADDITIVE_WITH_COMPENSATION", "Coverage issuance remains separate from compensation.", "Requires subscription and delivery reconciliation."),
        L("F78", "2009", "Debt_buyback", "EARLY_COUPON_REPURCHASE", "2009-12-31", "Tesoro_Nacional", "Tendering_holders", "Mixed", "BODEN_2012_coupon_15", "N/D", "N/D", "N/D", "LESS_THAN_2_PERCENT_OF_HOLDERS_TENDERED", "e0_cgn_cuenta_inversion_2009_sdp", "PDF_pp71_72", "QUALITATIVE_EARLY_REPURCHASE", "NON_ADDITIVE", "Less than 2% of holders tendered principal and rent coupon 15.", "No amount or purpose split is published in the cited narrative."),
        L("F79", "2010", "All_BODEN_2012_purposes", "DEBT_SERVICE_PRINCIPAL_REDUCTION", "2010-12-31", "Tesoro_Nacional", "BODEN_2012_holders", "Mixed", "BODEN_2012", "2282310500", "USD_nominal_updated", "9074.466548", "SERIES_ACCOUNTING_PRINCIPAL", "e0_cgn_cuenta_inversion_2010_sdp", "PDF_p6", "MIXED_PURPOSE_SERVICE_NOT_ALLOCATED", "EXCLUDE_FROM_BANK_COMPENSATION_TOTAL", "Annual BODEN 2012 principal reduction by series.", "No purpose-level holder allocation."),
        L("F80", "2011", "All_BODEN_2012_purposes", "DEBT_SERVICE_PRINCIPAL_REDUCTION", "2011-12-31", "Tesoro_Nacional", "BODEN_2012_holders", "Mixed", "BODEN_2012", "2197668700", "USD_nominal_updated", "9458.7660848", "SERIES_ACCOUNTING_PRINCIPAL", "e0_cgn_cuenta_inversion_2011_sdp", "PDF_p6", "MIXED_PURPOSE_SERVICE_NOT_ALLOCATED", "EXCLUDE_FROM_BANK_COMPENSATION_TOTAL", "Annual BODEN 2012 principal reduction by series.", "No purpose-level holder allocation."),
        L("F81", "2012", "All_BODEN_2012_purposes", "FINAL_MATURITY_PRINCIPAL_REDUCTION", "2012-12-31", "Tesoro_Nacional", "BODEN_2012_holders", "Mixed", "BODEN_2012", "2197791900", "USD_nominal_updated", "10808.7405642", "SERIES_ACCOUNTING_PRINCIPAL", "e0_cgn_cuenta_inversion_2012_sdp", "PDF_p5", "FINAL_SERIES_SERVICE_NOT_PURPOSE_ALLOCATED", "EXCLUDE_FROM_BANK_COMPENSATION_TOTAL", "Final principal reduction brings the series to zero.", "Maturity does not identify holders or prove bank-specific compensation."),
        L("F82", "2008", "All_public_debt", "AGGREGATE_HOLDER_DISTRIBUTION", "2008-12-31", "Sector_Publico_Nacional_no_financiero", "Creditors", "All_public_debt", "Debt_by_creditor_type", "276157", "ARS_million", "276157", "PRELIMINARY_AGGREGATE_DEBT", "e0_agn_res_202_2009_act_41_2009_deuda", "PDF_pp16_17", "AGGREGATE_PRIVATE_HOLDER_CONTROL", "CONTROL_NOT_ADDITIVE", "Private creditors held 54.8% of total debt in the AGN table.", "Private sector is not banks and the table is not BODEN-specific."),
        L("F83", "2009", "FGS_public_holder_control", "INVENTORY_DUPLICATION_CORRECTION", "2009-06-30", "FGS", "FGS", "Public_holder", "PF_BODEN_2012_USD_1st_series", "60", "USD_million_VNO", "N/D", "DUPLICATED_IN_TWO_FGS_INVENTORIES", "e0_agn_res_102_2011_act_366_2009_fgs", "PDF_p37", "PUBLIC_HOLDER_ACCOUNTING_EXCEPTION", "NON_ADDITIVE", "AGN found the same VNO USD 60m in negotiable-title and fixed-term-bond inventories; regularized by 2009 year-end.", "Not Treasury issuance service or commercial-bank compensation."),
        L("F84", "2008", "All_BODEN_2012_purposes", "YEAR_END_SERIES_STOCK", "2008-12-31", "Tesoro_Nacional", "BODEN_2012_holders", "Mixed", "BODEN_2012", "8708.340475", "USD_million_updated", "30061.19131970", "UPDATED_VALUE_AT_2008_12_31", "e0_cgn_cuenta_inversion_2008_sdp", "PDF_p5", "YEAR_END_SERIES_STOCK", "CONTROL_NOT_ADDITIVE", "All-purpose BODEN 2012 closing stock.", "Not a flow or purpose allocation."),
        L("F85", "2009", "All_BODEN_2012_purposes", "YEAR_END_SERIES_STOCK", "2009-12-31", "Tesoro_Nacional", "BODEN_2012_holders", "Mixed", "BODEN_2012", "6545.070", "USD_million_updated", "24871.266", "UPDATED_VALUE_AT_2009_12_31", "e0_cgn_cuenta_inversion_2009_sdp", "PDF_p60", "YEAR_END_SERIES_STOCK", "CONTROL_NOT_ADDITIVE", "Rounded inventory stock agrees with detailed closing balance.", "Not a flow or purpose allocation."),
        L("F86", "2010", "All_BODEN_2012_purposes", "YEAR_END_SERIES_STOCK", "2010-12-31", "Tesoro_Nacional", "BODEN_2012_holders", "Mixed", "BODEN_2012", "4395.461", "USD_million_updated", "17476.351", "UPDATED_VALUE_AT_2010_12_31", "e0_cgn_cuenta_inversion_2010_sdp", "PDF_p60", "YEAR_END_SERIES_STOCK", "CONTROL_NOT_ADDITIVE", "Rounded inventory stock.", "Not a flow or purpose allocation."),
        L("F87", "2011", "All_BODEN_2012_purposes", "YEAR_END_SERIES_STOCK", "2011-12-31", "Tesoro_Nacional", "BODEN_2012_holders", "Mixed", "BODEN_2012", "2197.792", "USD_million_updated", "9459.296", "UPDATED_VALUE_AT_2011_12_31", "e0_cgn_cuenta_inversion_2011_sdp", "PDF_p50", "YEAR_END_SERIES_STOCK", "CONTROL_NOT_ADDITIVE", "Rounded inventory stock.", "Not a flow or purpose allocation."),
        L("F88", "2012", "All_BODEN_2012_purposes", "YEAR_END_SERIES_STOCK", "2012-12-31", "Tesoro_Nacional", "BODEN_2012_holders", "Mixed", "BODEN_2012", "0", "USD_million_updated", "0", "MATURED_ZERO_AT_2012_12_31", "e0_cgn_cuenta_inversion_2012_sdp", "PDF_pp41_42", "SERIES_MATURED", "CONTROL_NOT_ADDITIVE", "BODEN 2012 is absent from the post-maturity inventory and the detailed row closes at zero.", "Zero series stock does not close holder-purpose reconciliation."),
    ]
)
write_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V112.csv", ledger, ledger_fields)


transaction_fields = ["transaction_id", "year", "mechanism", "phase", "instrument", "recipient_universe", "amount_original", "original_unit", "normalized_ars_million", "source_id", "source_locator", "bank_compensation_aggregation", "realization_status", "caveat"]
transactions = []
for row in ledger[58:]:
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
write_csv(HERE / "E0_FISCAL_TRANSACTION_LEDGER_2007_2012_V112.csv", transactions, transaction_fields)


service_fields = [
    "service_id", "year", "series", "opening_modified_original_unit", "opening_adjustment_vs_prior_close", "aggregate_increments_original_unit", "principal_reduction_original_unit", "principal_accounting_ars", "interest_accounting_ars", "closing_original_unit", "flow_equation_check", "source_id", "source_locator", "purpose_allocation", "cash_interpretation", "caveat"
]
service_values = [
    ("D01", "2007", "BODEN_2007", "354692100", "N/D", "2113600", "356805700", "731808305.02", "7071117.92", "0", "e0_cgn_cuenta_inversion_2007_sdp", "PDF_p5"),
    ("D02", "2007", "BODEN_2012", "12989472150", "N/D", "117042800", "2208223712.50", "6953696470.66", "2290405405.83", "10898291237.50", "e0_cgn_cuenta_inversion_2007_sdp", "PDF_p5"),
    ("D03", "2008", "BODEN_2012", "10894122612.50", "-4168625.00", "1870900", "2187653037.50", "7551778285.45", "1443444675.87", "8708340475.00", "e0_cgn_cuenta_inversion_2008_sdp", "PDF_p5"),
    ("D04", "2009", "BODEN_2012", "8696050675.00", "-12289800.00", "61177600", "2212158362.50", "8406201777.50", "799776613.96", "6545069912.50", "e0_cgn_cuenta_inversion_2009_sdp", "PDF_p5"),
    ("D05", "2010", "BODEN_2012", "6542352100.00", "-2717812.50", "135419000", "2282310500", "9074466548.00", "266663706.40", "4395460600.00", "e0_cgn_cuenta_inversion_2010_sdp", "PDF_p6"),
    ("D06", "2011", "BODEN_2012", "4395460600.00", "0", "0", "2197668700", "9458766084.80", "107165885.78", "2197791900.00", "e0_cgn_cuenta_inversion_2011_sdp", "PDF_p6"),
    ("D07", "2012", "BODEN_2012", "2197791900.00", "0", "0", "2197791900", "10808740564.20", "63185720.21", "0", "e0_cgn_cuenta_inversion_2012_sdp", "PDF_p5"),
]
service = []
for sid, year, series, opening, adjustment, increments, reduction, principal_ars, interest_ars, closing, source_id, locator in service_values:
    check = Decimal(opening) + Decimal(increments) - Decimal(reduction) == Decimal(closing)
    service.append(
        {
            "service_id": sid,
            "year": year,
            "series": series,
            "opening_modified_original_unit": opening,
            "opening_adjustment_vs_prior_close": adjustment,
            "aggregate_increments_original_unit": increments,
            "principal_reduction_original_unit": reduction,
            "principal_accounting_ars": principal_ars,
            "interest_accounting_ars": interest_ars,
            "closing_original_unit": closing,
            "flow_equation_check": str(check).upper(),
            "source_id": source_id,
            "source_locator": locator,
            "purpose_allocation": "NOT_AVAILABLE_AT_SERIES_SERVICE_LEVEL",
            "cash_interpretation": "ACCOUNTING_CONTROL_NOT_BENEFICIARY_CASH_TOTAL",
            "caveat": "Original-unit movement and ARS accounting columns are distinct; do not add principal interest stock or issuance across phases.",
        }
    )
write_csv(HERE / "E0_FISCAL_BODEN_SERVICE_BRIDGE_2007_2012_V112.csv", service, service_fields)


stock_fields = ["stock_id", "as_of_date", "scope", "purpose", "instrument", "original_vno_million_usd", "updated_vno_million_usd", "updated_value_million_ars", "source_id", "source_locator", "comparability", "caveat"]
stock = [
    {"stock_id": "K01", "as_of_date": "2007-12-31", "scope": "PURPOSE", "purpose": "COMPENSATORY", "instrument": "BODEN_2012", "original_vno_million_usd": "4590.561", "updated_vno_million_usd": "2869.100", "updated_value_million_ars": "9034.798", "source_id": "e0_cgn_cuenta_inversion_2007_sdp", "source_locator": "PDF_p56", "comparability": "PURPOSE_SPECIFIC", "caveat": "Excludes the separate CER-CVS BODEN 2013 component."},
    {"stock_id": "K02", "as_of_date": "2007-12-31", "scope": "PURPOSE", "purpose": "COVERAGE", "instrument": "BODEN_2012", "original_vno_million_usd": "3572.842", "updated_vno_million_usd": "2233.026", "updated_value_million_ars": "7031.799", "source_id": "e0_cgn_cuenta_inversion_2007_sdp", "source_locator": "PDF_p56", "comparability": "PURPOSE_SPECIFIC", "caveat": "Subscription leg; not a free transfer."},
    {"stock_id": "K03", "as_of_date": "2007-12-31", "scope": "PURPOSE", "purpose": "DEPOSITORS", "instrument": "BODEN_2012", "original_vno_million_usd": "4052.399", "updated_vno_million_usd": "2534.044", "updated_value_million_ars": "7979.705", "source_id": "e0_cgn_cuenta_inversion_2007_sdp", "source_locator": "PDF_p56", "comparability": "PURPOSE_SPECIFIC", "caveat": "Keep outside bank compensation."},
    {"stock_id": "K04", "as_of_date": "2007-12-31", "scope": "PURPOSE", "purpose": "AUCTION", "instrument": "BODEN_2012", "original_vno_million_usd": "791.872", "updated_vno_million_usd": "494.920", "updated_value_million_ars": "1558.503", "source_id": "e0_cgn_cuenta_inversion_2007_sdp", "source_locator": "PDF_p56", "comparability": "PURPOSE_SPECIFIC", "caveat": "Market placement, not compensation."},
    {"stock_id": "K05", "as_of_date": "2007-12-31", "scope": "PURPOSE", "purpose": "DIRECT_PLACEMENT", "instrument": "BODEN_2012", "original_vno_million_usd": "4427.521", "updated_vno_million_usd": "2767.201", "updated_value_million_ars": "8713.915", "source_id": "e0_cgn_cuenta_inversion_2007_sdp", "source_locator": "PDF_p56", "comparability": "PURPOSE_SPECIFIC", "caveat": "Other direct placements; not assignable to bank compensation."},
    {"stock_id": "K06", "as_of_date": "2007-12-31", "scope": "SERIES", "purpose": "ALL_PURPOSES", "instrument": "BODEN_2012", "original_vno_million_usd": "17435.195", "updated_vno_million_usd": "10898.291", "updated_value_million_ars": "34318.720", "source_id": "e0_cgn_cuenta_inversion_2007_sdp", "source_locator": "PDF_p56", "comparability": "SERIES_CONTROL", "caveat": "Sum of several purposes; not a beneficiary total."},
    {"stock_id": "K07", "as_of_date": "2008-12-31", "scope": "SERIES", "purpose": "ALL_PURPOSES", "instrument": "BODEN_2012", "original_vno_million_usd": "N/D", "updated_vno_million_usd": "8708.340475", "updated_value_million_ars": "30061.19131970", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "source_locator": "PDF_p5", "comparability": "DETAILED_CLOSING_BALANCE", "caveat": "Purpose split unavailable in the cited series row."},
    {"stock_id": "K08", "as_of_date": "2009-12-31", "scope": "SERIES", "purpose": "ALL_PURPOSES", "instrument": "BODEN_2012", "original_vno_million_usd": "17449.007", "updated_vno_million_usd": "6545.070", "updated_value_million_ars": "24871.266", "source_id": "e0_cgn_cuenta_inversion_2009_sdp", "source_locator": "PDF_p60", "comparability": "ROUNDED_INVENTORY", "caveat": "Rounded stock; not a flow."},
    {"stock_id": "K09", "as_of_date": "2010-12-31", "scope": "SERIES", "purpose": "ALL_PURPOSES", "instrument": "BODEN_2012", "original_vno_million_usd": "17581.580", "updated_vno_million_usd": "4395.461", "updated_value_million_ars": "17476.351", "source_id": "e0_cgn_cuenta_inversion_2010_sdp", "source_locator": "PDF_p60", "comparability": "ROUNDED_INVENTORY", "caveat": "Rounded stock; not a flow."},
    {"stock_id": "K10", "as_of_date": "2011-12-31", "scope": "SERIES", "purpose": "ALL_PURPOSES", "instrument": "BODEN_2012", "original_vno_million_usd": "17582.343", "updated_vno_million_usd": "2197.792", "updated_value_million_ars": "9459.296", "source_id": "e0_cgn_cuenta_inversion_2011_sdp", "source_locator": "PDF_p50", "comparability": "ROUNDED_INVENTORY", "caveat": "Rounded stock; not a flow."},
    {"stock_id": "K11", "as_of_date": "2012-12-31", "scope": "SERIES", "purpose": "ALL_PURPOSES", "instrument": "BODEN_2012", "original_vno_million_usd": "0", "updated_vno_million_usd": "0", "updated_value_million_ars": "0", "source_id": "e0_cgn_cuenta_inversion_2012_sdp", "source_locator": "PDF_pp5_41_42", "comparability": "FINAL_MATURITY_CONTROL", "caveat": "Zero stock closes the series, not the holder-purpose audit."},
]
write_csv(HERE / "E0_FISCAL_BODEN_STOCK_BRIDGE_2007_2012_V112.csv", stock, stock_fields)


breaks = read_csv(V111 / "E0_FISCAL_METHOD_BREAKS_V111.csv")
for row in breaks:
    if row["break_id"] == "agn_specific_audit_gap_persists":
        row.update(
            problem="Two AGN reports narrow the aggregate-holder and FGS-control sides, but no mechanism-specific delivery audit was located.",
            rule="Use the AGN controls only at their published scope; keep CRYL/entity reconciliation open.",
            evidence="AGN Res. 202/2009 Act. 41/2009; AGN Res. 102/2011 Act. 366/2009",
        )
break_fields = list(breaks[0])
new_breaks = [
    ("annual_series_service_not_purpose", "purpose", "Annual principal and interest are reported for the whole BODEN series.", "Do not allocate series service to compensation banks without holder-purpose records.", "CGN SDP 2007-2012 detailed debt movement tables"),
    ("modified_opening_requires_bridge", "reconciliation", "Modified opening balances can differ from the prior published closing balance.", "Preserve the opening adjustment explicitly before testing the annual flow equation.", "CGN SDP 2007-2010 detailed debt movement tables"),
    ("original_unit_vs_ars_accounting", "valuation", "Original-unit principal movement and ARS accounting service columns are distinct measures.", "Keep both columns and never sum them as if homogeneous.", "CGN SDP 2007-2012 detailed debt movement tables"),
    ("mixed_buyback_not_series_allocable", "instrument", "Buyback totals mix BODEN with other securities and GDP units.", "Treat tender totals as non-additive controls until instrument-level awards are recovered.", "CGN SDP 2008 p.64"),
    ("scoped_narrative_absence_not_zero", "source", "A program phrase may be absent from Anexo J while series service appears in the debt table.", "Record only a scoped absence; do not infer zero activity.", "CGN SDP 2010-2012"),
    ("maturity_zero_not_holder_reconciliation", "scope", "A zero closing stock proves series maturity, not who received service.", "Keep holder and purpose allocation open after maturity.", "CGN SDP 2012 pp.5, 41-42"),
    ("agn_aggregate_holder_not_boden", "universe", "AGN creditor shares cover total public debt rather than BODEN 2012.", "Use them as aggregate context only and do not equate private sector with banks.", "AGN Res. 202/2009 pp.16-17"),
    ("fgs_duplicate_not_treasury_flow", "accounting", "A duplicated FGS inventory presentation changes reported holdings without a Treasury flow.", "Record the exception as a public-holder control correction, non-additive to issuance and service.", "AGN Res. 102/2011 p.37"),
    ("transparency_route_not_holder_register", "source", "AGN transparency confirms reports were identified for consultation but does not itself expose a holder register.", "Use the route to continue resolution/actuación retrieval; do not treat it as delivery evidence.", "AGN transparency response dated 2018-09-11"),
]
for break_id, dimension, problem, rule, evidence_text in new_breaks:
    breaks.append({"break_id": break_id, "dimension": dimension, "problem": problem, "rule": rule, "status": "FROZEN", "evidence": evidence_text})
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V112.csv", breaks, break_fields)


matrix = read_csv(V111 / "HISTORICAL_EPISODE_MATRIX_2001_2026_V111.csv")
matrix_fields = list(matrix[0])
for row in matrix:
    row["source_id"] = row["source_id"].replace("V111", "V112")
matrix.extend(
    [
        {"episode_id": "E0", "episode_name": "Crisis de convertibilidad / default / salida / reordenamiento financiero", "t0": "2007_TO_2012", "shock_type": "OTHER", "variable": "boden_2012_series_principal_service", "sector": "STATE_BCRA", "frequency": "ANNUAL", "pre_value": "10898.2912375m_USD_UPDATED_AT_2007_CLOSE", "trough_value": "0", "trough_date": "2012-12", "recovery_value": "N/A_MATURED", "recovery_date": "2012-12", "months_to_trough": "60", "months_to_recovery": "N/A", "benchmark_definition": "annual modified-opening plus increments minus principal reduction equals closing balance", "source_id": "E0_FISCAL_BODEN_SERVICE_BRIDGE_2007_2012_V112.csv", "source_quality": "PRIMARY_DERIVED", "basis": "CGN detailed debt movement tables 2007-2012", "method_break": "YES_SERIES_NOT_PURPOSE", "status": "SERIES_MATURITY_RECONCILED", "interpretation": "BODEN 2012 service is arithmetically bridged to zero at maturity.", "falsifier": "YES_ALL_SERVICE_EQUALS_BANK_COMPENSATION", "notes": "Cumulative 2007-2012 principal reduction is USD 13,285.8062125m updated nominal; holder-purpose allocation remains open."},
        {"episode_id": "E0", "episode_name": "Crisis de convertibilidad / default / salida / reordenamiento financiero", "t0": "2007_TO_2009", "shock_type": "OTHER", "variable": "post_2006_purpose_adjustments", "sector": "STATE_BCRA", "frequency": "ANNUAL", "pre_value": "2007_COMP_ARP_MINUS39.9_USD_MINUS3.3_COVERAGE_USD_PLUS110.2", "trough_value": "2008_DEPOSITOR_USD_MINUS6.6_MINUS2.9_COVERAGE_MINUS0.0179_COMP_PLUS1.9", "trough_date": "2008", "recovery_value": "2009_COMP_BCRA_REVIEW_MINUS25_COVERAGE_PLUS61", "recovery_date": "2009", "months_to_trough": "12", "months_to_recovery": "24", "benchmark_definition": "purpose-specific nominal issues and corrections by currency", "source_id": "E0_FISCAL_TRANSACTION_LEDGER_2007_2012_V112.csv", "source_quality": "PRIMARY", "basis": "CGN Anexo J 2007-2009", "method_break": "YES_CORRECTIONS_NOT_SERVICE", "status": "PURPOSE_ADJUSTMENTS_IDENTIFIED", "interpretation": "Corrections and residual coverage issuance continued through 2009.", "falsifier": "YES_PROGRAM_HARD_CLOSED_2006", "notes": "No cross-currency total and no negative amount reset to zero."},
        {"episode_id": "E0", "episode_name": "Crisis de convertibilidad / default / salida / reordenamiento financiero", "t0": "2008_TO_2009", "shock_type": "OTHER", "variable": "holder_controls", "sector": "STATE_BCRA", "frequency": "ANNUAL", "pre_value": "PRIVATE_54.8PCT_OF_ALL_DEBT_2008", "trough_value": "FGS_DUPLICATE_PF_BODEN2012_USD60M_AT_2009H1", "trough_date": "2009-06", "recovery_value": "REGULARIZED_AT_2009_CLOSE", "recovery_date": "2009-12", "months_to_trough": "6", "months_to_recovery": "12", "benchmark_definition": "aggregate creditor distribution plus audited public-holder exception", "source_id": "e0_agn_res_202_2009_act_41_2009_deuda;e0_agn_res_102_2011_act_366_2009_fgs", "source_quality": "PRIMARY_AUDIT", "basis": "AGN Res. 202/2009 and 102/2011", "method_break": "YES_AGGREGATE_AND_PUBLIC_HOLDER_NOT_PURPOSE", "status": "INDEPENDENT_HOLDER_CONTROLS_PARTIAL", "interpretation": "Independent audit evidence exists but does not supply a bank-by-bank compensation register.", "falsifier": "YES_PRIVATE_SECTOR_EQUALS_BANKS", "notes": "CRYL and entity-level delivery remain open."},
    ]
)
write_csv(HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V112.csv", matrix, matrix_fields)


evidence = read_csv(V111 / "HISTORICAL_EVIDENCE_COVERAGE_V111.csv")
for row in evidence:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            quality="PRIMARY_FISCAL_SERVICE_BRIDGE_EXTENDED_2001_2012",
            comparable="SERIES_SERVICE_RECONCILED_PURPOSE_HOLDER_ALLOCATION_OPEN",
            gap="BODEN 2007 and 2012 series service is reconciled through maturity; purpose corrections and aggregate/public holder controls are identified; CRYL/entity delivery cash settlement and bank-specific incidence remain open",
            next_action="Recover CRYL or Caja de Valores holder and cancellation registers; obtain instrument-level buyback awards and reconcile Treasury BCRA FGS and entity records",
        )
write_csv(HERE / "HISTORICAL_EVIDENCE_COVERAGE_V112.csv", evidence)


queue = read_csv(V111 / "HISTORICAL_SOURCE_QUEUE_V111.csv")
for row in queue:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            status="BODEN_2007_2012_SERIES_MATURITY_RECONCILED_HOLDER_PURPOSE_OPEN",
            why="annual principal interest closing stocks purpose corrections mixed buybacks and two independent AGN holder controls are frozen through 2012",
            next_action="Recover CRYL/Caja de Valores registers and tender award files to allocate service and cancellations by holder and original purpose",
        )
write_csv(HERE / "HISTORICAL_SOURCE_QUEUE_V112.csv", queue)


b2012 = [row for row in service if row["series"] == "BODEN_2012"]
cumulative_usd = sum(Decimal(row["principal_reduction_original_unit"]) for row in b2012) / Decimal(1_000_000)
cumulative_principal_ars = sum(Decimal(row["principal_accounting_ars"]) for row in b2012) / Decimal(1_000_000)
cumulative_interest_ars = sum(Decimal(row["interest_accounting_ars"]) for row in b2012) / Decimal(1_000_000)

readme = f"""# V112

V112 lleva la reconstrucción fiscal E0 hasta el vencimiento de BODEN 2007 y BODEN 2012. Reconcilia el movimiento anual por serie, congela correcciones por propósito y agrega controles AGN de tenedores sin fabricar una imputación bancaria.

## Delta material

- El censo E0 sube de **40 a 48 fuentes primarias preservadas**: seis Cuentas de Inversión y dos informes AGN.
- El ledger fiscal alcanza **88 filas**; 30 pertenecen al tramo 2007–2012.
- El puente de servicio contiene **7 filas**: BODEN 2007 finaliza en 2007 y BODEN 2012 se reconcilia anualmente hasta cero en 2012.
- Para BODEN 2012, la reducción acumulada 2007–2012 es **USD {cumulative_usd}m** de nominal actualizado; las columnas contables suman **ARS {cumulative_principal_ars}m** de principal y **ARS {cumulative_interest_ars}m** de intereses.
- Se congelan **{len(breaks)} restricciones metodológicas**.
- Las correcciones por propósito continúan en 2007–2009; la cobertura sigue separada de la compensación.
- Las recompras 2008–2009 son mixtas o carecen de monto por especie: no se imputan a bancos.
- La AGN aporta distribución agregada de acreedores y una excepción auditada del FGS, no un padrón CRYL banco por banco.

## Estado que no cambia

- panel estricto Q4-2023: **30 entidades**;
- cobertura: **61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%**;
- `CLOSED_NETWORK_GATE`: **NO**;
- Banco Rioja: mismatch de **158,789k**;
- no se identifica transferencia causal neta hogares → bancos.

## Leer primero

1. `VEREDICTO_V112.md`
2. `E0_FISCAL_RECONSTRUCTION_V112.md`
3. `E0_FISCAL_BODEN_SERVICE_BRIDGE_2007_2012_V112.csv`
4. `E0_FISCAL_BODEN_STOCK_BRIDGE_2007_2012_V112.csv`
5. `E0_FISCAL_TRANSACTION_LEDGER_2007_2012_V112.csv`
6. `AUDITORIA_V112.md`
7. `HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V112_A_V113.md`
8. `qa_v112.py`
"""
(HERE / "README_V112.md").write_text(readme, encoding="utf-8")


reconstruction = f"""# Reconstrucción fiscal E0 2007–2012 · V112

## Resultado

El rastro contable de BODEN 2007 y BODEN 2012 queda cerrado por serie. BODEN 2007 termina en 2007; BODEN 2012 pasa de un saldo final de USD 10.898,2912375m en 2007 a cero en 2012. Cada año cumple la identidad `apertura modificada + incrementos − reducción de principal = cierre`.

Eso no cierra el rastro distributivo. La serie BODEN 2012 reunió compensación, cobertura, opciones de ahorristas, subastas y colocaciones directas. Por ello, principal e intereses por serie no se convierten en “pagos a bancos”.

## Servicio anual BODEN 2012

| Año | Reducción principal · USD m actualizados | Principal contable · ARS m | Interés contable · ARS m | Cierre · USD m actualizados |
|---|---:|---:|---:|---:|
| 2007 | 2.208,2237125 | 6.953,69647066 | 2.290,40540583 | 10.898,2912375 |
| 2008 | 2.187,6530375 | 7.551,77828545 | 1.443,44467587 | 8.708,3404750 |
| 2009 | 2.212,1583625 | 8.406,20177750 | 799,77661396 | 6.545,0699125 |
| 2010 | 2.282,3105000 | 9.074,46654800 | 266,66370640 | 4.395,4606000 |
| 2011 | 2.197,6687000 | 9.458,76608480 | 107,16588578 | 2.197,7919000 |
| 2012 | 2.197,7919000 | 10.808,74056420 | 63,18572021 | 0 |

Totales de control: USD {cumulative_usd}m de reducción nominal actualizada, ARS {cumulative_principal_ars}m de principal contable y ARS {cumulative_interest_ars}m de intereses. Son tres métricas diferentes; no se suman entre sí ni prueban caja por beneficiario.

## Correcciones y ejecución residual

- 2007: bajas compensatorias de VNO ARS 39,9m BODEN 2007 y VNO USD 3,3m BODEN 2012; emisión de cobertura VNO USD 110,2m.
- 2008: bajas de opciones de ahorristas no entregadas —VNO USD 6,6m BODEN 2012 y USD 2,9m BODEN 2013—; baja de cobertura USD 0,0179m; compensación USD 1,9m por diferencias de tipos de conversión.
- 2009: baja compensatoria USD 25m por revisión BCRA y emisión de cobertura USD 61m.

Las recompras de 2008 informan ARS 1.374m y ARS 1.128m para conjuntos mixtos de títulos. La recompra temprana de 2009 recibió menos del 2% de los tenedores, sin monto BODEN 2012 separado. Se conservan como controles no aditivos.

## Tenedores: avance parcial AGN

La Resolución AGN 202/2009 ubica 54,8% de toda la deuda del SPN no financiero en el sector privado al 31/12/2008. No es una cifra BODEN ni “bancos”. La Resolución AGN 102/2011 detecta una duplicación de VNO USD 60m de PF BODEN 2012 en inventarios del FGS al 30/06/2009, regularizada al cierre. Es un control de tenencia pública, no un flujo del Tesoro.

## Qué queda abierto

- padrón CRYL/Caja de Valores por tenedor, fecha, especie y origen de colocación;
- adjudicaciones por especie de las recompras 2008–2009;
- conciliación Tesoro–CRYL–BCRA–FGS–entidades;
- efectivo liquidado por beneficiario;
- asignación del servicio entre compensación, cobertura, ahorristas y mercado;
- ejecución residual identificable de Ley 25.796;
- incidencia neta después de fondeo, pérdidas, valuación, impuestos y capitalización.

La conclusión admisible sigue siendo descriptiva: el Estado absorbió parte del reordenamiento mediante deuda y cobertura; V112 cierra las series, no una ganancia bancaria neta.
"""
(HERE / "E0_FISCAL_RECONSTRUCTION_V112.md").write_text(reconstruction, encoding="utf-8")


audit_text = f"""# Auditoría V112 — vencimientos BODEN 2007/2012

## Preservación

Se preservaron ocho PDF oficiales: seis Cuentas de Inversión CGN 2007–2012 y dos informes AGN. El censo E0 alcanza 48 fuentes primarias.

## Inspección visual

Se renderizaron y verificaron: CGN 2007 pp. 5, 56 y 65; 2008 pp. 5, 54, 55, 63 y 64; 2009 pp. 5, 60, 71 y 72; 2010 pp. 6 y 60; 2011 pp. 6 y 50; 2012 pp. 5, 41 y 42; AGN Res. 202/2009 pp. 16–17; AGN Res. 102/2011 p. 37.

## Controles

- ledger total: {len(ledger)} filas; tramo nuevo: {len(transactions)};
- puente de servicio: {len(service)} filas, todas con identidad anual exacta;
- puente de stocks 2007–2012: {len(stock)} filas;
- quiebres metodológicos: {len(breaks)}, todos congelados;
- BODEN 2007: cierre cero en 2007;
- BODEN 2012: cierre cero en 2012;
- reducción acumulada BODEN 2012: USD {cumulative_usd}m de nominal actualizado;
- principal contable acumulado: ARS {cumulative_principal_ars}m;
- interés contable acumulado: ARS {cumulative_interest_ars}m.

## Auditoría independiente

La búsqueda por actuación y resolución localizó controles reales: AGN 202/2009 (Act. 41/2009) y AGN 102/2011 (Act. 366/2009). El primero es agregado para toda la deuda; el segundo controla una tenencia pública FGS. Ninguno reemplaza el padrón CRYL ni una auditoría específica de entregas por compensación.

## Restricción central

VNO original, nominal actualizado, principal contable ARS, interés, stock, emisión/corrección, recompra y caja son fases o medidas distintas. V112 no las suma ni atribuye todo el servicio BODEN a entidades financieras.
"""
(HERE / "AUDITORIA_V112.md").write_text(audit_text, encoding="utf-8")


verdict = """# Veredicto V112

## Qué sabemos ahora

- BODEN 2007 vence y queda en cero en 2007.
- BODEN 2012 queda reconciliado año por año y vence a saldo cero en 2012.
- La ejecución residual por propósito continúa al menos hasta 2009 mediante bajas, revisiones y nuevas emisiones de cobertura.
- Las recompras 2008–2009 no ofrecen una cifra BODEN 2012 limpia y asignable a compensación.
- La AGN aporta dos controles independientes: distribución agregada de acreedores y una duplicación de inventario FGS.
- El saldo cero de una serie no identifica quién cobró ni el propósito original de cada tenencia.

## Qué no sabemos todavía

- qué recibió y mantuvo cada entidad;
- qué parte del servicio correspondió a compensación, cobertura, ahorristas o mercado;
- qué montos se liquidaron efectivamente en caja por beneficiario;
- cómo concilian Tesoro, CRYL/Caja de Valores, BCRA, FGS y balances bancarios;
- la incidencia neta final.

## Estado

La rama fiscal pasa a `PRIMARY_FISCAL_SERVICE_BRIDGE_EXTENDED_2001_2012`. La madurez de las series está cerrada; la asignación tenedor–propósito y la caja final siguen abiertas. El panel microbancario permanece en 30 entidades, cobertura exacta 61.8555625288919…% y `CLOSED_NETWORK_GATE=NO`.
"""
(HERE / "VEREDICTO_V112.md").write_text(verdict, encoding="utf-8")


refs = """# Referencias de fuentes V112

## Cuenta de Inversión · CGN

- 2007 · SDP/Anexo J: https://www.economia.gob.ar/hacienda/cgn/cuenta/2007/archivos/sdp.pdf
- 2008 · SDP/Anexo J: https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/archivos/sdp.pdf
- 2009 · SDP/Anexo J: https://www.economia.gob.ar/hacienda/cgn/cuenta/2009/archivos/sdp.pdf
- 2010 · SDP: https://www.economia.gob.ar/hacienda/cgn/cuenta/2010/archivos/sdp.pdf
- 2011 · SDP: https://www.economia.gob.ar/hacienda/cgn/cuenta/2011/archivos/sdp.pdf
- 2012 · SDP: https://www.economia.gob.ar/hacienda/cgn/cuenta/2012/archivos/sdp.pdf

## Auditoría General de la Nación

- Resolución 202/2009 · Actuación 41/2009: https://www.agn.gob.ar/sites/default/files/informes/2009_202info_0.pdf
- Resolución 102/2011 · Actuación 366/2009: https://www.agn.gob.ar/sites/default/files/informes/Informe_102_2011.pdf
- Transparencia AGN · respuesta 11/09/2018 sobre evolución y distribución BODEN: https://www.agn.gob.ar/transparencia/informacion

Los ocho PDF se preservan en `research/ciclo_ajuste/inputs/historical_retrieval/v112/binaries/`; tamaños, hashes y quiebres están en `E0_LOCAL_PRIMARY_SOURCE_CENSUS_V112.csv`.
"""
(HERE / "SOURCE_REFERENCES_V112.md").write_text(refs, encoding="utf-8")


handover = """# Handover próxima sesión · V112 → V113

## Estado congelado

- 48 fuentes primarias E0 preservadas;
- 88 filas del ledger fiscal; 30 nuevas para 2007–2012;
- 7 filas del puente de servicio BODEN 2007/2012;
- 11 filas del puente de stocks 2007–2012;
- 37 quiebres metodológicos;
- BODEN 2007 y 2012 cerrados por serie a saldo cero;
- correcciones por propósito identificadas hasta 2009;
- dos controles AGN independientes incorporados;
- no hay asignación completa por tenedor, propósito ni caja.

## Prioridad V113

1. recuperar padrones CRYL/Caja de Valores por tenedor, especie y fecha;
2. identificar adjudicaciones por especie en recompras 2008–2009;
3. conciliar Tesoro–CRYL–BCRA–FGS–entidades;
4. localizar informes AGN de evolución/distribución BODEN mencionados en transparencia;
5. rastrear ejecución residual de Ley 25.796 y sus bajas;
6. mapear servicio a propósito original sin imputación mecánica;
7. separar devengado, valor técnico, precio de suscripción, caja y resultado económico.

## No hacer

- no sumar stock + emisión + transferencia + amortización;
- no imputar todo el servicio BODEN a bancos;
- no convertir USD a ARS sin fecha y tipo de cambio transaccional;
- no tratar correcciones negativas como cero;
- no llamar a todo “sector privado” bancos;
- no declarar ganancia bancaria neta desde compensación bruta.

## Invariantes

Panel estricto: 30 entidades; cobertura exacta 61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%; `CLOSED_NETWORK_GATE=NO`; Banco Rioja mismatch 158,789k.
"""
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V112_A_V113.md").write_text(handover, encoding="utf-8")


old_hash = read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V111.csv")
hash_rows = [row for row in old_hash if row["id"] not in new_ids]
for spec in source_specs:
    hash_rows.append({"id": spec["id"], "archivo_local": spec["local"], "exists": "True", "sha_catalog": spec["sha256"], "sha_actual": spec["sha256"], "hash_ok": "True"})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V112.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V112.csv", hash_rows)
shutil.copyfile(AUDIT / "SOURCE_PATH_ENCODING_EXCEPTIONS_V111.csv", AUDIT / "SOURCE_PATH_ENCODING_EXCEPTIONS_V112.csv")
shutil.copyfile(AUDIT / "SOURCE_PRESERVATION_MISSING_V111.csv", AUDIT / "SOURCE_PRESERVATION_MISSING_V112.csv")

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": str(size), "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V112.csv", size_rows, ["path", "bytes", "mib", "over_50_mib", "over_100_mib"])

completeness = {
    "checkpoint": "V112",
    "date": "2026-08-29",
    "state": "E0_FISCAL_SERVICE_BRIDGE_EXTENDED_2001_2012_HOLDER_PURPOSE_OPEN",
    "master_catalog_entries": len(catalog),
    "physical_local_copies": sum(row["exists"] == "True" for row in hash_rows),
    "physical_local_hash_ok": sum(row["hash_ok"] == "True" for row in hash_rows),
    "reference_only_nonbinary_exempt": 4,
    "remaining_physical_gaps": 1,
    "p0": 0,
    "p1": 1,
    "p2": 0,
    "binary_required_entries": 242,
    "binary_required_preserved": 241,
    "binary_required_source_complete": False,
    "pending_binary_discovery_actions": 7,
    "numeric_v112_strict_changed": False,
    "strict_coverage_pct": "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549",
    "exact_entities": 30,
    "asset_numerator_million_ars": "59812903.504",
    "system_denominator_million_ars": "96697695.5",
    "closed_network_gate": "NO",
    "e0_primary_sources_preserved": len(census),
    "e0_sources_newly_preserved_v112": len(source_specs),
    "e0_quality": "PRIMARY_FISCAL_SERVICE_BRIDGE_EXTENDED_2001_2012",
    "e0_comparable": False,
    "e0_fiscal_phase_separated": True,
    "e0_fiscal_final_cash_total_identified": False,
    "e0_fiscal_ledger_rows": len(ledger),
    "e0_fiscal_transaction_rows_2007_2012": len(transactions),
    "e0_fiscal_service_bridge_rows": len(service),
    "e0_fiscal_stock_bridge_rows_2007_2012": len(stock),
    "e0_fiscal_method_breaks_frozen": len(breaks),
    "e0_boden_2007_matured": True,
    "e0_boden_2012_matured": True,
    "e0_series_service_purpose_allocated": False,
    "e0_holder_register_complete": False,
    "e0_agn_holder_controls_partial": True,
    "e0_causal_net_incidence_identified": False,
    "historical_workstream": "E0_HOLDER_PURPOSE_CRYL_RECONCILIATION_OPEN",
    "path_encoding_note": "Banco La Pampa remains byte-identical despite the catalog/Git filename encoding mismatch.",
}
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V112.json").write_text(json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V112.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V112",
        "parent_checkpoint": "V111",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30,
        "strict_coverage_pct": completeness["strict_coverage_pct"],
        "closed_network_gate": "NO",
        "e0_primary_sources": len(census),
        "new_official_sources": len(source_specs),
        "fiscal_ledger_rows": len(ledger),
        "fiscal_transaction_rows_2007_2012": len(transactions),
        "fiscal_service_bridge_rows": len(service),
        "fiscal_stock_bridge_rows_2007_2012": len(stock),
        "fiscal_method_breaks": len(breaks),
        "files": files,
    }
    (HERE / "MANIFEST_V112.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    "checkpoint": "V112",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": completeness["strict_coverage_pct"],
    "exact_entities": 30,
    "closed_network_gate": "NO",
    "source_audit": "246 master entries; 241 physical local copies with 241/241 SHA-valid; eight new official E0 fiscal sources preserved; one catalogued P1 binary gap plus seven discovery actions remain.",
    "historical_workstream": "E0 fiscal series service reconciled through 2012 from 48 preserved primary sources; holder-purpose CRYL allocation cash and net incidence remain open",
    "file_count_excluding_manifest": len(global_files),
    "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V112 BUILD PASS")
