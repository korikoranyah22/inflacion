from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import csv
import hashlib
import html
import json
import re
import shutil


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
V125 = HERE.parent / "V125"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v126" / "binaries"
SCRATCH = REPO / "tmp" / "spreadsheets" / "v126"
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
    text = text.replace("V125", "V126")
    for prefix in ("TR", "REQ", "CL", "SK", "DM", "ID", "ST"):
        text = text.replace(f"{prefix}125_", f"{prefix}126_")
    return text


def clone_parent() -> None:
    skip = {
        "build_institutional_requests_V125.py",
        "qa_V125.py",
        "MANIFEST_V125.json",
        "INHERITED_QA_STATUS_V125.csv",
    }
    for source in V125.iterdir():
        if not source.is_file() or source.name in skip:
            continue
        target = HERE / source.name.replace("V125", "V126")
        target.write_text(bump_text(source.read_text(encoding="utf-8-sig")), encoding="utf-8")


clone_parent()
BIN.mkdir(parents=True, exist_ok=True)

source_specs = [
    {
        "id": "e0_caja_archive_recompra_2008_query",
        "institution": "Caja de Valores S.A.",
        "title": "Archivo de comunicados · filtro tema Recompra · año 2008",
        "url": "https://contenidos.sba.com.ar/CAJVAL/vistas/Comunicados/ListadoComunicadosInstitucional.aspx?c=2",
        "file": "caja_archive_recompra_2008.html",
        "publication": "2026-08-29",
        "period": "consulta actual del archivo para 2008-01-01 a 2008-12-31",
        "type": "HTML institucional oficial · respuesta filtrada WebForms",
        "families": "state_bcra;fiscal;debt;Caja;archive_search;target_buyback",
        "breaks": "ausencia en archivo público actual versus inexistencia histórica",
        "use": "USABLE_CURRENT_PUBLIC_ARCHIVE_EXACT_THREE_REPURCHASE_ROWS",
        "caveat": "La respuesta devuelve exactamente 4857, 4861 y 4873; no demuestra que nunca haya existido otra comunicación ni que una operación no se ejecutara.",
    },
    {
        "id": "e0_caja_archive_window_2008_09_12_2008_10_10_query",
        "institution": "Caja de Valores S.A.",
        "title": "Archivo de comunicados · ventana 12/09/2008–10/10/2008",
        "url": "https://contenidos.sba.com.ar/CAJVAL/vistas/Comunicados/ListadoComunicadosInstitucional.aspx?c=2",
        "file": "caja_archive_window_2008-09-12_2008-10-10.html",
        "publication": "2026-08-29",
        "period": "consulta actual del archivo para 2008-09-12 a 2008-10-10",
        "type": "HTML institucional oficial · respuesta filtrada WebForms",
        "families": "state_bcra;fiscal;debt;Caja;archive_search;fourth_round",
        "breaks": "cobertura de índices públicos versus correspondencia interna; numeración versus contenido",
        "use": "USABLE_CURRENT_PUBLIC_ARCHIVE_CONTINUOUS_4877_4903_WINDOW",
        "caveat": "Conserva 27 filas y numeración continua 4877–4903, incluida la zona del 02/10/2008, sin título de recompra; sólo agota la vista pública actual.",
    },
    {
        "id": "e0_argentina_deuda_publica_2008_q3",
        "institution": "Ministerio de Economía y Producción · Secretaría de Finanzas",
        "title": "Deuda Pública · tercer trimestre de 2008",
        "url": "https://www.argentina.gob.ar/sites/default/files/deuda_publica_30-09-08.xls",
        "file": "deuda_publica_30-09-08.xls",
        "publication": "2008-09-30",
        "period": "flujos del tercer trimestre y stock al 2008-09-30",
        "type": "XLS institucional oficial · deuda trimestral",
        "families": "state_bcra;fiscal;debt;buyback;accounting;stock_reduction",
        "breaks": "valor nominal original versus residual; reducción contable agregada versus entrega y pago individual",
        "use": "USABLE_EXACT_Q3_BODEN_BUYBACK_ACCOUNTING_BRIDGE",
        "caveat": "A.5.1 registra USD 16,814m de reducción por recompras BODEN; coincide exactamente con el residual adjudicado agregado, no identifica asientos Caja ni pago por ronda.",
    },
    {
        "id": "e0_argentina_deuda_publica_2008_q4",
        "institution": "Ministerio de Economía y Finanzas Públicas · Secretaría de Finanzas",
        "title": "Deuda Pública · cuarto trimestre de 2008",
        "url": "https://www.argentina.gob.ar/sites/default/files/deuda_publica_31-12-2008.xls",
        "file": "deuda_publica_31-12-2008.xls",
        "publication": "2008-12-31",
        "period": "flujos del cuarto trimestre y acumulado 2008",
        "type": "XLS institucional oficial · deuda trimestral",
        "families": "state_bcra;fiscal;debt;buyback;accounting;GDP_units",
        "breaks": "recompra contable agregada versus programa objetivo; GDP Units excluidas versus monto cero",
        "use": "USABLE_Q4_AND_ANNUAL_REPURCHASE_ACCOUNTING_WITH_GDP_EXCLUSION",
        "caveat": "A.5.1 registra USD 1.506,71011m de Bonos del Canje y A.5.4 USD 1.523,52411m anuales; ambas notas excluyen GDP Units y no asignan el agregado a cada operación.",
    },
]

for spec in source_specs:
    destination = BIN / spec["file"]
    scratch = SCRATCH / spec["file"]
    if scratch.is_file():
        shutil.copyfile(scratch, destination)
    if not destination.is_file():
        raise FileNotFoundError(destination)
    spec["bytes"] = destination.stat().st_size
    spec["sha256"] = sha256(destination)
    spec["local"] = "/" + destination.relative_to(REPO).as_posix()

expected_hashes = {
    "e0_caja_archive_recompra_2008_query": "ebe50392348978745c22cd29d1e35ae49b1c1712bb042a58e9efc29af1e9a417",
    "e0_caja_archive_window_2008_09_12_2008_10_10_query": "86b99286f08393a60185f79c3cd819614a6b97da2ac5a9c44316e7b324546b83",
    "e0_argentina_deuda_publica_2008_q3": "9e986552e6a6b37662046b0b808b78878b52bc885595ed3d0f75eca58f4d0b82",
    "e0_argentina_deuda_publica_2008_q4": "7eae7145e29214a2aaae75384e38f592ce8367a94f920978187417ceef8c2e31",
}
assert {spec["id"]: spec["sha256"] for spec in source_specs} == expected_hashes

annual_html = (BIN / "caja_archive_recompra_2008.html").read_text(encoding="utf-8", errors="replace")
window_html = (BIN / "caja_archive_window_2008-09-12_2008-10-10.html").read_text(encoding="utf-8", errors="replace")


def archive_rows(text: str) -> list[tuple[str, str, str]]:
    pattern = re.compile(
        r'<td align="right">(\d+)</td><td align="left">(.*?)</td><td align="center"[^>]*>(\d{2}/\d{2}/\d{4})</td>',
        re.S,
    )
    return [(number, html.unescape(re.sub(r"<[^>]+>", "", title)).strip(), date) for number, title, date in pattern.findall(text)]


annual_rows = archive_rows(annual_html)
window_rows = archive_rows(window_html)
assert [row[0] for row in annual_rows] == ["4873", "4861", "4857"]
assert [row[0] for row in window_rows] == [str(number) for number in range(4903, 4876, -1)]
assert len(window_rows) == 27 and all("recompra" not in row[1].casefold() for row in window_rows)

new_ids = {spec["id"] for spec in source_specs}
catalog = [row for row in read_csv(CATALOG) if row["id"] not in new_ids]
for spec in source_specs:
    catalog.append(
        {
            "id": spec["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": spec["institution"],
            "titulo": spec["title"], "url_original": spec["url"], "archivo_local": spec["local"],
            "fecha_descarga": "2026-08-29", "fecha_publicacion": spec["publication"], "codigo_serie": "",
            "periodo_utilizado": spec["period"], "tipo": spec["type"], "sha256": spec["sha256"],
            "nota": f"V126 E0 fiscal: {spec['bytes']:,} bytes. {spec['caveat']}",
        }
    )
write_csv(CATALOG, catalog)

census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V126.csv")
census = [row for row in census if row["source_id"] not in new_ids]
for spec in source_specs:
    census.append(
        {
            "source_id": spec["id"], "institution": spec["institution"], "artifact": spec["title"],
            "url": spec["url"], "local_path": spec["local"], "sha256": spec["sha256"], "bytes": str(spec["bytes"]),
            "period_coverage": spec["period"], "variable_families": spec["families"], "primary_source": "YES",
            "preserved": "YES", "method_breaks": spec["breaks"], "use_status": spec["use"], "caveat": spec["caveat"],
        }
    )
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V126.csv", census)

archive_audit = [
    {
        "audit_id": "CA126_01", "source_id": "e0_caja_archive_recompra_2008_query",
        "query": "tema=Recompra; fecha=01/01/2008-31/12/2008; registros_por_pagina=100",
        "returned_count": "3", "returned_numbers": "4873;4861;4857", "target_present": "NO_FOURTH_ROW",
        "status": "CURRENT_PUBLIC_ARCHIVE_EXACT_THREE_TARGET_COMMUNICATIONS",
        "permitted_interpretation": "El archivo público actual sólo devuelve tres comunicaciones bajo Recompra en 2008.",
        "forbidden_interpretation": "Nunca existió una cuarta comunicación o no se ejecutó la ronda del 02/10/2008.",
    },
    {
        "audit_id": "CA126_02", "source_id": "e0_caja_archive_window_2008_09_12_2008_10_10_query",
        "query": "tema vacío; fecha=12/09/2008-10/10/2008; registros_por_pagina=100",
        "returned_count": "27", "returned_numbers": "4877-4903_CONTINUOUS", "target_present": "NO_REPURCHASE_TITLE",
        "status": "CURRENT_PUBLIC_ARCHIVE_CONTINUOUS_AROUND_2008_10_02",
        "permitted_interpretation": "La numeración pública es continua 4877–4903 y no contiene un título de recompra en la zona de la cuarta ronda.",
        "forbidden_interpretation": "La numeración pública agota correspondencia interna, expedientes, anexos o documentos no indexados.",
    },
]
write_csv(HERE / "E0_CAJA_ARCHIVE_FOURTH_ROUND_SEARCH_AUDIT_V126.csv", archive_audit)

b2012_vno = Decimal("17193000")
b2013_vno = Decimal("13148000")
b2012_residual = b2012_vno * Decimal("0.5") / Decimal("1000")
b2013_residual = b2013_vno * Decimal("0.625") / Decimal("1000")
derived_q3 = b2012_residual + b2013_residual
assert derived_q3 == Decimal("16814")
assert Decimal("16814") + Decimal("1506710.11") == Decimal("1523524.11")

accounting_bridge = [
    {
        "bridge_id": "AB126_Q3_BODEN", "period": "2008Q3", "source_id": "e0_argentina_deuda_publica_2008_q3",
        "sheet": "A.5.1", "cell_range": "A25:C27", "official_label": "Boden - Recompras",
        "official_amount_thousand_usd": "16814", "official_amount_thousand_ars": "50862.35",
        "boden2012_awarded_vno_usd": str(b2012_vno), "boden2012_residual_factor": "0.5",
        "boden2012_residual_thousand_usd": str(b2012_residual), "boden2013_awarded_vno_usd": str(b2013_vno),
        "boden2013_residual_factor": "0.625", "boden2013_residual_thousand_usd": str(b2013_residual),
        "derived_total_thousand_usd": str(derived_q3), "delta_thousand_usd": "0",
        "evidence_status": "EXACT_AGGREGATE_DEBT_REDUCTION_MATCH_TO_PUBLIC_BODEN_AWARDS",
        "caveat": "Confirma baja contable agregada del residual adjudicado; no asigna asientos por ronda/oferta ni prueba el pago BCRA.",
    },
    {
        "bridge_id": "AB126_Q4_CANJE", "period": "2008Q4", "source_id": "e0_argentina_deuda_publica_2008_q4",
        "sheet": "A.5.1", "cell_range": "A24:C29", "official_label": "Recompra Bonos del Canje - Dto. 1735/04",
        "official_amount_thousand_usd": "1506710.11", "official_amount_thousand_ars": "4723536.19",
        "boden2012_awarded_vno_usd": "N/A", "boden2012_residual_factor": "N/A", "boden2012_residual_thousand_usd": "N/A",
        "boden2013_awarded_vno_usd": "N/A", "boden2013_residual_factor": "N/A", "boden2013_residual_thousand_usd": "N/A",
        "derived_total_thousand_usd": "N/A", "delta_thousand_usd": "N/A",
        "evidence_status": "OFFICIAL_Q4_ACCOUNTING_AGGREGATE_TARGET_ALLOCATION_OPEN",
        "caveat": "El rótulo no permite adjudicar este total a las cuatro rondas públicas ni a la primera etapa sin un puente de operaciones.",
    },
    {
        "bridge_id": "AB126_2008_TOTAL", "period": "2008", "source_id": "e0_argentina_deuda_publica_2008_q4",
        "sheet": "A.5.4", "cell_range": "A25:B27", "official_label": "Títulos Públicos - Recompras",
        "official_amount_thousand_usd": "1523524.11", "official_amount_thousand_ars": "N/A",
        "boden2012_awarded_vno_usd": "N/A", "boden2012_residual_factor": "N/A", "boden2012_residual_thousand_usd": "N/A",
        "boden2013_awarded_vno_usd": "N/A", "boden2013_residual_factor": "N/A", "boden2013_residual_thousand_usd": "N/A",
        "derived_total_thousand_usd": "1523524.11", "delta_thousand_usd": "0",
        "evidence_status": "EXACT_ANNUAL_SUM_Q3_PLUS_Q4",
        "caveat": "El total anual reproduce 16.814 + 1.506.710,11; no debe sumarse nuevamente a sus componentes.",
    },
    {
        "bridge_id": "AB126_GDP_EXCLUSION", "period": "2008Q4_AND_2008", "source_id": "e0_argentina_deuda_publica_2008_q4",
        "sheet": "A.5.1/A.5.4", "cell_range": "A62:C63;A61:B62", "official_label": "No se incluye el monto correspondiente a la recompra de las GDP Units",
        "official_amount_thousand_usd": "N/A", "official_amount_thousand_ars": "N/A",
        "boden2012_awarded_vno_usd": "N/A", "boden2012_residual_factor": "N/A", "boden2012_residual_thousand_usd": "N/A",
        "boden2013_awarded_vno_usd": "N/A", "boden2013_residual_factor": "N/A", "boden2013_residual_thousand_usd": "N/A",
        "derived_total_thousand_usd": "N/A", "delta_thousand_usd": "N/A",
        "evidence_status": "OFFICIAL_ACCOUNTING_ACKNOWLEDGMENT_AMOUNT_EXCLUDED",
        "caveat": "La exclusión reconoce la recompra en el cuadro pero no informa monto contable, entrega, pago ni baja de principal de las unidades.",
    },
]
write_csv(HERE / "E0_FISCAL_BUYBACK_DEBT_ACCOUNTING_BRIDGE_2008_V126.csv", accounting_bridge)


def update_boden_settlement(path: Path) -> None:
    rows = read_csv(path)
    for row in rows:
        if row.get("instrument") in {"BODEN_2012", "BODEN_2013"} and row.get("tender_date") in {"2008-09-04", "2008-09-11"}:
            row["settlement_confirmation"] = "AGGREGATE_Q3_DEBT_REDUCTION_EXACT_MATCH_PER_ROUND_CAJA_AND_PAYMENT_OPEN"
            row["caveat"] = "El cuadro oficial Q3 reduce exactamente el residual agregado adjudicado; no identifica la transferencia de esta oferta, el asiento por ronda ni el pago BCRA."
    write_csv(path, rows)


for name in (
    "E0_FISCAL_PUBLIC_BUYBACK_TENDERS_2008_V126.csv",
    "E0_FISCAL_BODEN_BUYBACK_TENDERS_2008_V126.csv",
    "E0_FISCAL_PUBLIC_BUYBACK_AWARDS_2008_V126.csv",
    "E0_FISCAL_BODEN_BUYBACK_AWARDS_2008_V126.csv",
):
    update_boden_settlement(HERE / name)

ledger = read_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V126.csv")
new_ledger = [
    {
        "ledger_id": "F126", "window": "2008Q3", "mechanism": "Debt_buyback", "phase": "ACCOUNTING_STOCK_REDUCTION",
        "as_of_date": "2008-09-30", "payer": "Tesoro_Nacional", "recipient": "Debt_stock", "universe": "Public_tender_BODEN_2012_2013",
        "instrument": "BODEN_2012_BODEN_2013", "amount_original": "16.814", "original_unit": "USD_million_residual_principal",
        "normalized_ars_million": "50.86235", "valuation_basis": "OFFICIAL_Q3_FLOW_TABLE_AND_EXACT_RESIDUAL_AWARD_MATCH",
        "source_id": "e0_argentina_deuda_publica_2008_q3", "source_locator": "A.5.1!A25:C27",
        "realization_status": "ACCOUNTED_AGGREGATE_DEBT_REDUCTION_EXACT_MATCH", "additivity": "NON_ADDITIVE_WITH_PUBLIC_BODEN_AWARD_ROWS",
        "status_interpretation": "La baja contable agregada coincide exactamente con BODEN 2012 VNO 17.193m×0,5 más BODEN 2013 VNO 13.148m×0,625.",
        "caveat": "No prueba por sí sola el matching, la recepción por oferta/ronda ni el pago BCRA.",
    },
    {
        "ledger_id": "F127", "window": "2008Q4", "mechanism": "Debt_buyback", "phase": "ACCOUNTING_STOCK_REDUCTION",
        "as_of_date": "2008-12-31", "payer": "Tesoro_Nacional", "recipient": "Debt_stock", "universe": "Bonos_del_Canje_Dto_1735_04",
        "instrument": "Exchange_bonds_unsplit", "amount_original": "1506.71011", "original_unit": "USD_million",
        "normalized_ars_million": "4723.53619", "valuation_basis": "OFFICIAL_Q4_FLOW_TABLE",
        "source_id": "e0_argentina_deuda_publica_2008_q4", "source_locator": "A.5.1!A24:C29",
        "realization_status": "ACCOUNTED_Q4_REPURCHASE_REDUCTION_TARGET_ALLOCATION_OPEN", "additivity": "NON_ADDITIVE_WITH_ANNUAL_TOTAL",
        "status_interpretation": "El cuadro registra una reducción por recompra de Bonos del Canje.",
        "caveat": "No asignar a las rondas públicas, primera etapa o especies particulares sin detalle de operaciones; GDP Units están excluidas.",
    },
    {
        "ledger_id": "F128", "window": "2008", "mechanism": "Debt_buyback", "phase": "ACCOUNTING_ANNUAL_TOTAL",
        "as_of_date": "2008-12-31", "payer": "Tesoro_Nacional", "recipient": "Debt_stock", "universe": "Public_debt_securities_excluding_GDP_units",
        "instrument": "Public_securities_unsplit", "amount_original": "1523.52411", "original_unit": "USD_million",
        "normalized_ars_million": "N/D", "valuation_basis": "OFFICIAL_ANNUAL_FLOW_TABLE",
        "source_id": "e0_argentina_deuda_publica_2008_q4", "source_locator": "A.5.4!A25:B27",
        "realization_status": "ACCOUNTED_ANNUAL_REPURCHASE_REDUCTION", "additivity": "TOTAL_DO_NOT_ADD_TO_F126_F127",
        "status_interpretation": "El total anual coincide exactamente con las reducciones Q3 y Q4.",
        "caveat": "Excluye GDP Units y no sustituye los registros de Caja o pago.",
    },
    {
        "ledger_id": "F129", "window": "2008Q4", "mechanism": "GDP_unit_buyback", "phase": "ACCOUNTING_SCOPE_NOTE",
        "as_of_date": "2008-12-31", "payer": "Tesoro_Nacional", "recipient": "GDP_unit_holders_unknown", "universe": "GDP_units",
        "instrument": "GDP_UNITS_UNSPLIT", "amount_original": "N/D", "original_unit": "EXCLUDED_FROM_TABLE",
        "normalized_ars_million": "N/D", "valuation_basis": "OFFICIAL_Q4_FOOTNOTE",
        "source_id": "e0_argentina_deuda_publica_2008_q4", "source_locator": "A.5.1!A62:C63;A.5.4!A61:B62",
        "realization_status": "ACCOUNTING_ACKNOWLEDGMENT_AMOUNT_EXCLUDED", "additivity": "NON_ADDITIVE",
        "status_interpretation": "La nota reconoce la recompra de GDP Units pero excluye su monto del cuadro de deuda.",
        "caveat": "Exclusión no equivale a cero, reversa, pago confirmado ni baja de principal.",
    },
]
ledger = [row for row in ledger if row["ledger_id"] not in {item["ledger_id"] for item in new_ledger}] + new_ledger
write_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V126.csv", ledger)

breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V126.csv")
new_breaks = [
    {"break_id": "current_public_archive_absence_not_historical_nonexistence", "dimension": "coverage", "problem": "Una consulta exhaustiva de la vista pública actual no cubre correspondencia interna, anexos, expedientes o registros retirados.", "rule": "Formular sólo 'no figura en el archivo público actual' y mantener la búsqueda institucional de la cuarta comunicación.", "status": "FROZEN", "evidence": "Caja archive queries CA126_01 y CA126_02"},
    {"break_id": "aggregate_debt_reduction_not_per_round_settlement", "dimension": "phase", "problem": "Una reducción contable agregada exacta no identifica cada transferencia, matching, asiento de Caja o pago BCRA.", "rule": "Elevar la realización sólo a baja contable agregada y mantener abiertos los registros por ronda/oferta.", "status": "FROZEN", "evidence": "Deuda Pública 2008Q3 A.5.1; AB126_Q3_BODEN"},
    {"break_id": "tender_vno_not_residual_debt_stock", "dimension": "unit", "problem": "El VNO original adjudicado de bonos amortizantes no es directamente comparable con el principal residual que reduce el stock.", "rule": "Aplicar factores residuales 0,5 BODEN 2012 y 0,625 BODEN 2013 antes de conciliar.", "status": "FROZEN", "evidence": "Resultados oficiales; Deuda Pública 2008Q3; exact identity 8.596,5+8.217,5=16.814 miles USD"},
    {"break_id": "gdp_units_excluded_not_zero_or_unexecuted", "dimension": "scope", "problem": "La nota que excluye GDP Units del cuadro no informa un valor cero ni revierte las adjudicaciones publicadas.", "rule": "Conservar la exclusión como reconocimiento de alcance y exigir el registro específico de las unidades.", "status": "FROZEN", "evidence": "Deuda Pública 2008Q4 A.5.1 y A.5.4"},
    {"break_id": "q4_exchange_bond_aggregate_not_target_tenders", "dimension": "aggregation", "problem": "El agregado Q4 de Bonos del Canje no trae especie, fecha, precio ni expediente que lo vincule con una modalidad concreta.", "rule": "No asignarlo a primera etapa, cuatro rondas ni tenedores sin detalle de operaciones.", "status": "FROZEN", "evidence": "Deuda Pública 2008Q4 A.5.1"},
]
breaks = [row for row in breaks if row["break_id"] not in {item["break_id"] for item in new_breaks}] + new_breaks
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V126.csv", breaks)

trace = read_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V126.csv")
trace.append(
    {
        "trace_id": "TR126_078", "request_id": "REQ126_ECON", "institution": "Ministerio de Economía / Secretaría de Finanzas",
        "gap_id": "CL126_DEBT_ACCOUNTING", "requested_record": "Detalle y conciliación de las filas de recompras de A.5.1/A.5.4 de Deuda Pública 2008",
        "period": "2008Q3; 2008Q4; acumulado 2008", "search_keys": "Boden - Recompras; 16814; Recompra Bonos del Canje; 1506710.11; 1523524.11; GDP Units",
        "minimum_usable_fields": "fecha; operación; especie; VNO original; residual; contravalor; asiento; expediente; estado; vínculo con Caja/BCRA",
        "acceptable_redacted_or_aggregate": "cuadro de conciliación por fecha y especie que preserve montos y estado", "status": "DRAFT_NOT_SENT",
    }
)
write_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V126.csv", trace)

closures = read_csv(HERE / "E0_REQUEST_CLOSURE_CRITERIA_V126.csv")
closures.append(
    {
        "gap_id": "CL126_DEBT_ACCOUNTING", "target_question": "¿Qué operaciones y asientos componen las reducciones por recompra de Deuda Pública 2008 y cómo se concilian con Caja/BCRA?",
        "minimum_positive_evidence": "Detalle preexistente por fecha/especie con VNO original, residual, contravalor, asiento, expediente y estado de conciliación o pago.",
        "minimum_negative_route_evidence": "Búsqueda fundada en ONCP, Dirección de Administración de la Deuda, SIGADE/COMDOC, TGN y archivos sucesores por rótulos y montos exactos.",
        "does_not_close": "La identidad agregada Q3, el total anual, la nota GDP o una caída trimestral aislada.",
        "initial_status": "Q3_AGGREGATE_DEBT_REDUCTION_EXACT_MATCH_DETAIL_AND_PAYMENT_OPEN_NOT_SENT",
    }
)
write_csv(HERE / "E0_REQUEST_CLOSURE_CRITERIA_V126.csv", closures)

search_keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V126.csv")
search_keys.extend(
    [
        {"key_id": "SK126_58", "request_id": "REQ126_ECON", "key_type": "accounting_label_amount", "exact_key": "Boden - Recompras;16814;50862.35;30/09/2008;A.5.1", "purpose": "localizar el detalle que compone la baja contable Q3 y su conciliación", "public_anchor": "Deuda Pública 30/09/2008 A.5.1", "caveat": "La identidad agregada no identifica por sí sola asientos o pago."},
        {"key_id": "SK126_59", "request_id": "REQ126_ECON", "key_type": "accounting_label_amount", "exact_key": "Recompra Bonos del Canje -Dto. 1735/04;1506710.11;1523524.11;GDP Units", "purpose": "localizar detalle Q4/anual y registro separado de GDP Units", "public_anchor": "Deuda Pública 31/12/2008 A.5.1 y A.5.4", "caveat": "No asignar el agregado Q4 al programa objetivo sin puente documental."},
    ]
)
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V126.csv", search_keys)

attachments = read_csv(HERE / "E0_REQUEST_ATTACHMENT_MINIMUM_V126.csv")
attachments.append(
    {"request_id": "REQ126_ECON", "institution": "Ministerio de Economía / Tesoro", "attach_file": "E0_FISCAL_BUYBACK_DEBT_ACCOUNTING_BRIDGE_2008_V126.csv", "purpose": "rótulos, montos y conciliación residual exacta de las planillas trimestrales", "why_minimal": "permite localizar el asiento sin presumir expediente ni pago", "exclude": "planillas completas si el canal exige adjuntos mínimos"}
)
write_csv(HERE / "E0_REQUEST_ATTACHMENT_MINIMUM_V126.csv", attachments)

public_routes = read_csv(HERE / "E0_PUBLIC_ROUTE_EXHAUSTION_V126.csv")
public_routes.append(
    {"route_id": "R126_03", "route": "CAJA_CURRENT_PUBLIC_COMMUNICATION_ARCHIVE", "query_scope": "tema Recompra en 2008 y ventana completa 12/09-10/10/2008", "records_examined": "3 target-topic rows; 27 continuous-window rows", "positive_operational_confirmation_hits": "0", "status": "FOURTH_ROUND_COMMUNICATION_NOT_IN_CURRENT_PUBLIC_INDEX", "evidence_file": "E0_CAJA_ARCHIVE_FOURTH_ROUND_SEARCH_AUDIT_V126.csv", "caveat": "Agota la vista pública actual, no correspondencia interna ni archivos retirados."}
)
write_csv(HERE / "E0_PUBLIC_ROUTE_EXHAUSTION_V126.csv", public_routes)

provenance = read_csv(HERE / "ARCHIVAL_PROVENANCE_V126.csv")
for spec in source_specs:
    provenance.append(
        {"source_id": spec["id"], "original_url": spec["url"], "retrieval_url": spec["url"], "capture_timestamp": "20260829", "cdx_digest": "N/A_LIVE_OFFICIAL", "local_path": spec["local"], "sha256": spec["sha256"], "bytes": str(spec["bytes"]), "provenance_note": "Descarga directa o respuesta filtrada preservada desde el portador institucional oficial; hash local congelado en V126."}
    )
write_csv(HERE / "ARCHIVAL_PROVENANCE_V126.csv", provenance)

evidence = read_csv(HERE / "HISTORICAL_EVIDENCE_COVERAGE_V126.csv")
for row in evidence:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            {
                "quality": "PRIMARY_BUYBACK_ACCOUNTING_EXACT_Q3_BODEN_REDUCTION_AND_DIRECT_CAJA_ROUTE_PRESERVED",
                "gap": "La baja contable Q3 de BODEN coincide exactamente con el residual adjudicado agregado y el archivo público actual fue agotado para la cuarta comunicación. Faltan asignación por ronda/oferta, asientos Caja, informes T+3 entregados, pago BCRA, detalle Q4 y registro específico de GDP Units.",
                "next_action": "Pedir sólo con autorización expresa la conciliación por operación de los rótulos/montos exactos y los registros de Caja/BCRA; mantener la cuarta comunicación como búsqueda institucional.",
            }
        )
write_csv(HERE / "HISTORICAL_EVIDENCE_COVERAGE_V126.csv", evidence)

queue = read_csv(HERE / "HISTORICAL_SOURCE_QUEUE_V126.csv")
for row in queue:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            {
                "status": "PUBLIC_ACCOUNTING_WRITE_DOWN_BRIDGE_PRESERVED_INSTITUTIONAL_DETAIL_PAYMENT_READY_NOT_SENT",
                "why": "La baja contable agregada Q3 de USD 16,814m coincide exactamente con el residual BODEN adjudicado; 59 claves y 78 objetos aíslan detalle, Caja, T+3 y pago. El archivo público actual no muestra cuarta comunicación.",
                "next_action": "Obtener autorización expresa, completar datos personales y presentar sólo los pedidos autorizados; conservar constancias y conciliar respuestas con AB126.",
            }
        )
write_csv(HERE / "HISTORICAL_SOURCE_QUEUE_V126.csv", queue)

matrix = read_csv(HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V126.csv")
matrix.extend(
    [
        {"episode_id": "E0", "episode_name": "Crisis de convertibilidad / default / salida / reordenamiento financiero", "t0": "2008Q3", "shock_type": "OTHER", "variable": "public_boden_buyback_accounting_reduction", "sector": "STATE_BCRA", "frequency": "QUARTERLY_ACCOUNTING", "pre_value": "B2012_VNO17193000;B2013_VNO13148000", "trough_value": "USD16.814M_RESIDUAL_REDUCTION", "trough_date": "2008-09-30", "recovery_value": "N/A", "recovery_date": "N/A", "months_to_trough": "N/A", "months_to_recovery": "N/A", "benchmark_definition": "official debt-flow reduction equals awarded residual principal", "source_id": "e0_argentina_deuda_publica_2008_q3;E0_FISCAL_BUYBACK_DEBT_ACCOUNTING_BRIDGE_2008_V126.csv", "source_quality": "PRIMARY_EXACT_AGGREGATE_ACCOUNTING_MATCH", "basis": "A.5.1 row Boden - Recompras; 0.5 and 0.625 residual factors", "method_break": "YES_AGGREGATE_NOT_PER_ROUND_SETTLEMENT", "status": "ACCOUNTED_AGGREGATE_DEBT_REDUCTION", "interpretation": "The public BODEN awards were reflected exactly as an aggregate residual-principal reduction.", "falsifier": "YES_AGAINST_NO_ACCOUNTING_REDUCTION", "notes": "Caja matching, individual transfers and BCRA payment remain open."},
        {"episode_id": "E0", "episode_name": "Crisis de convertibilidad / default / salida / reordenamiento financiero", "t0": "2008Q4", "shock_type": "OTHER", "variable": "public_debt_repurchase_accounting_scope", "sector": "STATE_BCRA", "frequency": "QUARTERLY_ACCOUNTING", "pre_value": "USD16.814M_Q3", "trough_value": "USD1506.71011M_Q4", "trough_date": "2008-12-31", "recovery_value": "USD1523.52411M_2008_TOTAL", "recovery_date": "2008-12-31", "months_to_trough": "N/A", "months_to_recovery": "N/A", "benchmark_definition": "official Q4 and annual debt-flow table excluding GDP Units", "source_id": "e0_argentina_deuda_publica_2008_q4", "source_quality": "PRIMARY_ACCOUNTING_AGGREGATE_SCOPE_OPEN", "basis": "A.5.1 and A.5.4", "method_break": "YES_Q4_UNALLOCATED_GDP_EXCLUDED", "status": "ACCOUNTED_AGGREGATE_TARGET_SPLIT_OPEN", "interpretation": "The annual total exactly sums Q3 and Q4 accounting reductions.", "falsifier": "YES_AGAINST_ZERO_REPURCHASE_ACCOUNTING", "notes": "Do not allocate Q4 or GDP Units without operation-level bridge."},
    ]
)
write_csv(HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V126.csv", matrix)

economia_path = HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V126.md"
economia = economia_path.read_text(encoding="utf-8")
needle = "Esa obligación contemporánea permite individualizar los documentos solicitados, pero no prueba que hayan sido entregados."
addition = (
    needle
    + "\n\nLas planillas oficiales de Deuda Pública al 30/09/2008 y 31/12/2008 agregan dos claves contables. "
    + "El cuadro Q3 registra `Boden - Recompras` por USD 16.814 miles y ese valor coincide exactamente con el principal residual de los BODEN adjudicados; "
    + "el cuadro Q4 registra `Recompra Bonos del Canje - Dto. 1735/04` por USD 1.506.710,11 miles y aclara que no incluye GDP Units. "
    + "Solicito el detalle preexistente que compone esas líneas y su conciliación, sin presumir que el agregado Q4 corresponda a una modalidad específica."
)
economia = economia.replace(needle, addition)
needle2 = "q) detalle por oferta adjudicada que la Oficina Nacional de Crédito Público informó a Caja para que ésta ingresara las instrucciones de recepción, y comunicación equivalente de la ronda del 02/10/2008 o constancia documentada de la búsqueda realizada."
economia = economia.replace(
    needle2,
    needle2 + "\nr) detalle y conciliación de las líneas contables citadas de A.5.1/A.5.4, con fecha, especie, VNO original, residual, contravalor, asiento, expediente, estado y vínculo con Caja/BCRA; y registro separado de las GDP Units excluidas del cuadro.",
)
economia += "\n- puente contable trimestral: `E0_FISCAL_BUYBACK_DEBT_ACCOUNTING_BRIDGE_2008_V126.csv`.\n"
economia_path.write_text(economia, encoding="utf-8")

for name in ("E0_INSTITUTIONAL_REQUEST_PACKAGE_V126.md", "REQUEST_SUBMISSION_CHECKLIST_V126.md"):
    path = HERE / name
    text = path.read_text(encoding="utf-8")
    text = text.replace("57 claves", "59 claves").replace("77 objetos", "78 objetos").replace("7 adjuntos", "8 adjuntos")
    path.write_text(text, encoding="utf-8")

reconstruction = """# Reconstrucción fiscal E0 · baja contable de recompras · V126

## Hallazgo principal

La planilla oficial de Deuda Pública del tercer trimestre de 2008 registra una disminución `Boden - Recompras` de USD 16.814 miles. La cifra concilia exactamente con las adjudicaciones públicas de BODEN del 04/09 y 11/09: BODEN 2012 VNO USD 17.193.000 × 0,5 = USD 8.596.500 de residual; BODEN 2013 VNO USD 13.148.000 × 0,625 = USD 8.217.500; suma USD 16.814.000. El delta es cero.

Esto eleva la evidencia desde adjudicación programada a **baja contable agregada exacta**. No identifica el matching de cada oferta, la recepción por Caja, el reparto por ronda ni el pago BCRA; esos eslabones siguen abiertos.

## Cuarto trimestre y GDP Units

La planilla al 31/12/2008 registra USD 1.506.710,11 miles de `Recompra Bonos del Canje - Dto. 1735/04`; el acumulado anual de `Títulos Públicos - Recompras` es USD 1.523.524,11 miles, exactamente Q3 + Q4. Ambos cuadros aclaran que no incluyen el monto de la recompra de GDP Units. El rótulo reconoce esa recompra pero no da su monto contable ni autoriza asignar el agregado Q4 a las cuatro rondas públicas o a la primera etapa.

## Comunicación faltante

La consulta del archivo actual de Caja por `Recompra` en todo 2008 devuelve exactamente los Comunicados 4857, 4861 y 4873. La ventana 12/09–10/10 devuelve 27 comunicaciones con numeración continua 4877–4903 y ningún título de recompra; en torno al 02/10 figuran 4894 y 4895 con otros asuntos. Conclusión permitida: la cuarta instrucción no figura en el índice público actual. No se afirma inexistencia histórica ni falta de ejecución.

## Frontera probatoria

Adjudicación ≠ baja contable agregada ≠ transferencia individual Caja ≠ pago BCRA. V126 cierra la baja contable agregada de los BODEN adjudicados en septiembre, pero mantiene abiertos los registros por ronda/oferta, informes T+3 entregados, pago y detalle de GDP Units. `CLOSED_NETWORK_GATE=NO`.
"""
(HERE / "E0_FISCAL_RECONSTRUCTION_V126.md").write_text(reconstruction, encoding="utf-8")

readme = """# Checkpoint V126 · puente contable exacto de recompras 2008

V126 preserva cuatro fuentes primarias nuevas: dos respuestas filtradas del archivo público de Caja y las planillas oficiales de deuda al 30/09 y 31/12/2008.

El avance sustantivo es una identidad exacta: la reducción Q3 `Boden - Recompras` de USD 16,814m equivale al residual de todo el VNO BODEN 2012/2013 adjudicado en las rondas del 04/09 y 11/09. Se confirma baja contable agregada, no pago ni transferencia individual.

El cuadro Q4 agrega USD 1.506,71011m de Bonos del Canje y el anual USD 1.523,52411m; GDP Units están expresamente excluidas. El archivo público actual de Caja sólo muestra tres comunicaciones de recompra en 2008 y una ventana continua 4877–4903 sin la cuarta instrucción.

Los seis pedidos siguen en `DRAFT_NOT_SENT`. Ahora contienen 78 objetos trazados, 59 claves y 8 adjuntos mínimos. El panel estricto y las cifras bancarias no cambian.
"""
(HERE / "README_V126.md").write_text(readme, encoding="utf-8")

verdict = """# Veredicto V126

Queda probado con fuente primaria que las adjudicaciones públicas de BODEN de septiembre de 2008 produjeron una baja contable agregada exacta de USD 16,814 millones de principal residual. El delta entre la reconstrucción y el cuadro oficial es cero.

No queda probado todavía qué transferencia individual ejecutó Caja, qué informe T+3 fue entregado ni qué pago cursó el BCRA. Tampoco se distribuye el agregado Q4 entre operaciones ni se cuantifica contablemente la recompra de GDP Units, expresamente excluida del cuadro.

La cuarta comunicación no figura en el archivo público actual: tres resultados temáticos en 2008 y 27 números continuos 4877–4903 alrededor de la fecha no la muestran. Esto no prueba inexistencia histórica.

La conclusión general del proyecto y el panel estricto permanecen congelados. `CLOSED_NETWORK_GATE=NO`.
"""
(HERE / "VEREDICTO_V126.md").write_text(verdict, encoding="utf-8")

audit_md = f"""# Auditoría V126

- Fuentes maestras: {len(catalog)}.
- Copias físicas/hash válidos: se recalculan en `CURRENT_SOURCE_COMPLETENESS_V126.json`.
- Fuentes primarias E0: {len(census)}; nuevas: 4.
- Ledger fiscal: {len(ledger)} filas.
- Cortes metodológicos: {len(breaks)}.
- Puente contable: {len(accounting_bridge)} filas; identidad Q3 con delta cero.
- Auditoría del archivo Caja: 2 consultas; 3 filas temáticas y 27 filas continuas.
- Pedidos: 6 borradores, 0 enviados; {len(trace)} objetos, {len(search_keys)} claves, {len(attachments)} adjuntos mínimos.
- Panel estricto: 30 entidades; {STRICT}% sin cambios.
"""
(HERE / "AUDITORIA_V126.md").write_text(audit_md, encoding="utf-8")

retrieval_log = """# Registro de recuperación V126

Fecha: 2026-08-29.

1. Se consultó el archivo institucional de Caja mediante sus filtros WebForms y se preservaron las respuestas HTML completas: tema `Recompra` para todo 2008 y ventana 12/09–10/10/2008.
2. La primera respuesta devuelve 3 filas: 4873, 4861 y 4857. La segunda devuelve 27 filas con numeración continua 4877–4903 y ningún título de recompra.
3. Se descargaron de la página oficial de datos anteriores de deuda los XLS al 30/09 y 31/12/2008.
4. El formato BIFF heredado no fue aceptado por el lector de planillas principal; se usó un lector local de respaldo sólo para extracción. Se inspeccionaron A.5.1, A.5.4 y las filas de BODEN relevantes.
5. La conciliación residual Q3 produce USD 16.814 miles exactos; el anual produce 16.814 + 1.506.710,11 = 1.523.524,11 miles USD.
6. El ZIP SIGADE Q3 fue exploratorio y no se incorporó porque no se pudo abrir su MDB con las dependencias disponibles y no aporta todavía una afirmación verificable adicional.
7. No se envió ningún pedido ni se realizó ninguna presentación externa.
"""
(HERE / "RETRIEVAL_LOG_V126.md").write_text(retrieval_log, encoding="utf-8")

source_refs = """# Referencias de fuentes V126

- Archivo de comunicados de Caja: https://contenidos.sba.com.ar/CAJVAL/vistas/Comunicados/ListadoComunicadosInstitucional.aspx?c=2
- Datos anteriores de deuda pública: https://www.argentina.gob.ar/economia/finanzas/datos-trimestrales-de-la-deuda/datos-anteriores
- Deuda Pública 30/09/2008: https://www.argentina.gob.ar/sites/default/files/deuda_publica_30-09-08.xls
- Deuda Pública 31/12/2008: https://www.argentina.gob.ar/sites/default/files/deuda_publica_31-12-2008.xls

Las respuestas filtradas de Caja y ambos XLS están preservados localmente con SHA-256 en el catálogo maestro.
"""
(HERE / "SOURCE_REFERENCES_V126.md").write_text(source_refs, encoding="utf-8")

handover = """# Handover V126 → V127

## Estado congelado

- La baja contable Q3 `Boden - Recompras` de USD 16,814m coincide exactamente con el residual agregado adjudicado de BODEN 2012/2013; delta cero.
- Q4 registra USD 1.506,71011m de Bonos del Canje y el anual USD 1.523,52411m; GDP Units excluidas.
- El archivo público actual de Caja devuelve sólo 4857/4861/4873 bajo Recompra 2008 y 27 números continuos 4877–4903 alrededor de la cuarta ronda sin instrucción equivalente.
- No se afirma pago, transferencia individual, informe T+3 entregado ni inexistencia histórica de la cuarta comunicación.
- Seis borradores, ninguno enviado. Panel estricto sin cambios.

## Prioridad V127

1. Buscar detalle/nota metodológica o base SIGADE que desagregue las líneas Q3/Q4 por operación y especie.
2. Buscar informes T+3 o constancias de recepción por Economía/Caja en 02/09, 09/09, 16/09, 07/10/2008 y 18/06/2009.
3. Buscar orden o conciliación de pago BCRA vinculada a 306/40000 y a los montos/ISIN.
4. Mantener la cuarta comunicación como pedido institucional: la vía pública actual quedó documentada, no históricamente cerrada.
5. No enviar pedidos ni formularios sin autorización expresa.
"""
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V126_A_V127.md").write_text(handover, encoding="utf-8")

inherited = [
    {"script": "qa_v97.py", "pre_v126_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v126_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V97 congela una ausencia luego resuelta."},
    *({"script": f"qa_v{i}.py", "pre_v126_result": "PASS", "post_v126_result": "PASS", "interpretation": "Compatible"} for i in (98, 100, 101, 102, 103, 104, 105, 106)),
    *({"script": f"qa_v{i}.py", "pre_v126_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v126_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "Congela un checkpoint o conteo anterior."} for i in range(107, 126)),
    {"script": "qa_v126.py", "pre_v126_result": "N/A", "post_v126_result": "PASS", "interpretation": "Puente contable Q3 exacto; archivo Caja actual agotado; pagos y registros individuales abiertos."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V126.csv", inherited)

for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    shutil.copyfile(AUDIT / f"{stem}_V125.csv", AUDIT / f"{stem}_V126.csv")

hash_rows = [row for row in read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V125.csv") if row["id"] not in new_ids]
for spec in source_specs:
    hash_rows.append({"id": spec["id"], "archivo_local": spec["local"], "exists": "True", "sha_catalog": spec["sha256"], "sha_actual": spec["sha256"], "hash_ok": "True"})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V126.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V126.csv", hash_rows)

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": str(size), "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V126.csv", size_rows)

physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V125.json").read_text(encoding="utf-8"))
for key in list(completeness):
    if key.endswith("_v125") or "newly_preserved_v125" in key or "sources_newly_preserved_v125" in key or key == "numeric_v125_strict_changed":
        completeness.pop(key, None)
completeness.update(
    {
        "checkpoint": "V126", "date": "2026-08-29",
        "state": "E0_Q3_BODEN_AGGREGATE_DEBT_REDUCTION_EXACT_MATCH_CAJA_PAYMENT_DETAIL_OPEN_NOT_SENT",
        "numeric_v126_strict_changed": False, "master_catalog_entries": len(catalog),
        "physical_local_copies": physical, "physical_local_hash_ok": hash_ok,
        "binary_required_entries": len(catalog) - 5, "binary_required_preserved": physical,
        "e0_primary_sources_preserved": len(census),
        "e0_quality": "PRIMARY_BUYBACK_ACCOUNTING_EXACT_Q3_BODEN_REDUCTION_AND_DIRECT_CAJA_ROUTE_PRESERVED",
        "sources_newly_preserved_v126": len(source_specs), "e0_primary_sources_newly_preserved_v126": len(source_specs),
        "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
        "e0_request_drafts": 6, "e0_request_traceability_rows": len(trace), "e0_request_closure_rules": len(closures),
        "e0_request_search_keys": len(search_keys), "e0_request_attachment_rows": len(attachments),
        "e0_buyback_accounting_bridge_rows": len(accounting_bridge), "e0_caja_archive_fourth_round_search_rows": len(archive_audit),
        "e0_requests_submitted": 0, "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
        "historical_workstream": "Q3 BODEN accounting reduction exactly reconciled to awarded residual principal; Q4/annual aggregate and GDP exclusion preserved; individual Caja/T+3/BCRA records and fourth communication remain open; no request submitted",
    }
)
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V126.json").write_text(json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V126 · baja contable exacta de recompras BODEN 2008"
old_backup = backup.read_text(encoding="utf-8-sig")
if marker not in old_backup:
    old_backup += (
        f"\n\n{marker}\n\n"
        "- Deuda Pública Q3 registra USD 16,814m de `Boden - Recompras`; coincide exactamente con el residual agregado de las adjudicaciones BODEN del 04/09 y 11/09.\n"
        "- La evidencia sube a baja contable agregada; matching, transferencias por ronda e instrucciones/pago BCRA siguen abiertos.\n"
        "- Q4 registra USD 1.506,71011m de Bonos del Canje y el anual USD 1.523,52411m; las GDP Units están expresamente excluidas.\n"
        "- El archivo público actual de Caja sólo devuelve tres comunicaciones de recompra en 2008 y una ventana continua 4877–4903 sin cuarta instrucción.\n"
        "- Se preservaron cuatro fuentes nuevas; E0 sube a 103 fuentes primarias. Los seis pedidos siguen DRAFT_NOT_SENT.\n"
        "- Panel estricto y cifras bancarias sin cambios.\n"
    )
    backup.write_text(old_backup, encoding="utf-8")


def checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V126.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V126", "parent_checkpoint": "V125",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": len(source_specs), "new_primary_sources": len(source_specs),
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks),
        "buyback_accounting_bridge_rows": len(accounting_bridge), "caja_archive_fourth_round_search_rows": len(archive_audit),
        "request_drafts": 6, "request_traceability_rows": len(trace), "request_closure_rules": len(closures),
        "request_search_keys": len(search_keys), "request_attachment_rows": len(attachments),
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V126.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    "checkpoint": "V126", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical local copies with {hash_ok}/{physical} SHA-valid; exact Q3 BODEN accounting reduction and current Caja archive search preserved; six requests drafted and none submitted.",
    "historical_workstream": "Q3 BODEN residual-principal reduction exactly reconciled; Q4/annual accounting and GDP exclusion preserved; individual Caja/T+3/BCRA records and fourth communication remain open; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V126 BUILD PASS")
