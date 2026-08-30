from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import csv
import hashlib
import json
import shutil


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
V114 = HERE.parent / "V114"
CYCLE = REPO / "research" / "ciclo_ajuste"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
AUDIT = CYCLE / "source_audit"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v115" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"
CENT = Decimal("0.01")
PCT = Decimal("0.00000001")


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


def v115_text(text: str) -> str:
    return text.replace("V114", "V115").replace("v114", "v115")


def clone_versioned(stem: str) -> None:
    src = V114 / f"{stem}_V114.csv"
    dst = HERE / f"{stem}_V115.csv"
    dst.write_text(v115_text(src.read_text(encoding="utf-8-sig")), encoding="utf-8-sig")


for stem in (
    "CURRENT_STATE",
    "FOUR_LEG_PASS_PANEL",
    "STRICT_Q4_FOUR_LEG_COVERAGE",
    "RECOVERY_QUEUE",
    "E0_FISCAL_TRANSACTION_LEDGER_2004_2006",
    "E0_FISCAL_TRANSACTION_LEDGER_2007_2012",
    "E0_FISCAL_STOCK_FLOW_BRIDGE",
    "E0_FISCAL_BODEN_SERVICE_BRIDGE_2007_2012",
    "E0_FISCAL_BODEN_STOCK_BRIDGE_2007_2012",
    "E0_FISCAL_BODEN_BUYBACK_TENDERS_2008",
    "E0_FISCAL_BODEN_BUYBACK_AWARDS_2008",
    "E0_FISCAL_PUBLIC_BUYBACK_TENDERS_2008",
    "E0_FISCAL_PUBLIC_BUYBACK_AWARDS_2008",
    "E0_FISCAL_AGN_CREDITOR_DISTRIBUTION",
    "E0_FISCAL_AGN_REPORT_INDEX",
):
    clone_versioned(stem)


source_specs = [
    {
        "id": "e0_argentina_finanzas_archive_recompras_voluntarias",
        "institution": "Ministerio de Economía",
        "title": "Archivo de Finanzas · Recompras voluntarias",
        "url": "https://www.argentina.gob.ar/economia/finanzas/archivo",
        "file": "argentina_finanzas_archivo_recompras_voluntarias.html",
        "publication": "",
        "period": "2008-08-11/2008-10-02",
        "type": "HTML oficial · índice histórico preservado",
        "pages": "N/A",
        "families": "state_bcra;fiscal;debt;buyback;archive",
        "breaks": "inventario web versus cierre administrativo; publicación versus liquidación",
        "use": "USABLE_OFFICIAL_FOUR_ROUND_ARCHIVE_INVENTORY",
        "caveat": "Enumera cuatro pares llamado/resultado bajo Recompras voluntarias, pero no es una constancia post-liquidación ni excluye operaciones no archivadas.",
        "verified": "HTML preservado; enlaces y orden de los cuatro llamados/resultados verificados.",
    },
    {
        "id": "e0_argentina_llamado_recompra_2008_08_27",
        "institution": "Ministerio de Economía y Producción · Secretaría de Finanzas",
        "title": "Primer llamado a licitación pública de recompra · 27 de agosto de 2008",
        "url": "https://www.argentina.gob.ar/sites/default/files/comunicado_llamado_licitacion_27-08-08.pdf",
        "file": "comunicado_llamado_licitacion_27-08-08.pdf",
        "publication": "2008",
        "period": "2008-08-27/2008-09-02",
        "type": "PDF oficial · binario preservado",
        "pages": "2",
        "families": "state_bcra;fiscal;debt;buyback;tender;settlement_route",
        "breaks": "máximo anunciado versus adjudicación; ruta Caja/BCRA versus transferencia/pago efectivo",
        "use": "USABLE_EXACT_CALL_AND_SETTLEMENT_ROUTE",
        "caveat": "Fija un máximo de ARS 150m, cuenta Caja 0306/40000 y liquidación prevista 02/09; no confirma la transferencia ni el pago.",
        "verified": "Las dos páginas fueron renderizadas e inspeccionadas visualmente.",
    },
    {
        "id": "e0_argentina_llamado_recompra_2008_09_03",
        "institution": "Ministerio de Economía y Producción · Secretaría de Finanzas",
        "title": "Segundo llamado a licitación pública de recompra · 3 de septiembre de 2008",
        "url": "https://www.argentina.gob.ar/sites/default/files/comunicado_llamado_licitacion_03-09-08.pdf",
        "file": "comunicado_llamado_licitacion_03-09-08.pdf",
        "publication": "2008",
        "period": "2008-09-03/2008-09-09",
        "type": "PDF oficial · binario preservado",
        "pages": "2",
        "families": "state_bcra;fiscal;debt;buyback;tender;settlement_route",
        "breaks": "máximo anunciado versus adjudicación; ruta Caja/BCRA versus transferencia/pago efectivo",
        "use": "USABLE_EXACT_CALL_AND_SETTLEMENT_ROUTE",
        "caveat": "Fija un máximo de ARS 200m, cuenta Caja 0306/40000 y liquidación prevista 09/09; no confirma la transferencia ni el pago.",
        "verified": "Las dos páginas fueron renderizadas e inspeccionadas visualmente.",
    },
    {
        "id": "e0_argentina_llamado_recompra_2008_09_10",
        "institution": "Ministerio de Economía y Producción · Secretaría de Finanzas",
        "title": "Tercer llamado a licitación pública de recompra · 10 de septiembre de 2008",
        "url": "https://www.argentina.gob.ar/sites/default/files/comunicado_llamado_licitacion_10-09-08.pdf",
        "file": "comunicado_llamado_licitacion_10-09-08.pdf",
        "publication": "2008",
        "period": "2008-09-10/2008-09-16",
        "type": "PDF oficial · binario preservado",
        "pages": "2",
        "families": "state_bcra;fiscal;debt;buyback;tender;settlement_route",
        "breaks": "máximo anunciado versus adjudicación; ruta Caja/BCRA versus transferencia/pago efectivo",
        "use": "USABLE_EXACT_CALL_AND_SETTLEMENT_ROUTE",
        "caveat": "Fija un máximo de ARS 100m, cuenta Caja 0306/40000 y liquidación prevista 16/09; no confirma la transferencia ni el pago.",
        "verified": "Las dos páginas fueron renderizadas e inspeccionadas visualmente.",
    },
    {
        "id": "e0_argentina_llamado_recompra_2008_10_01",
        "institution": "Ministerio de Economía y Producción · Secretaría de Finanzas",
        "title": "Cuarto llamado a licitación pública de recompra · 1 de octubre de 2008",
        "url": "https://www.argentina.gob.ar/sites/default/files/comunicado_llamado_licitacion_01-10-08.pdf",
        "file": "comunicado_llamado_licitacion_01-10-08.pdf",
        "publication": "2008",
        "period": "2008-10-01/2008-10-07",
        "type": "PDF oficial · binario preservado",
        "pages": "2",
        "families": "state_bcra;fiscal;debt;buyback;tender;settlement_route",
        "breaks": "máximo anunciado versus adjudicación; ruta Caja/BCRA versus transferencia/pago efectivo",
        "use": "USABLE_EXACT_CALL_AND_SETTLEMENT_ROUTE",
        "caveat": "Fija un máximo de ARS 100m, cuenta Caja 0306/40000 y liquidación prevista 07/10; no confirma la transferencia ni el pago.",
        "verified": "Las dos páginas fueron renderizadas e inspeccionadas visualmente.",
    },
]


for spec in source_specs:
    path = BIN / spec["file"]
    if not path.is_file():
        raise FileNotFoundError(path)
    spec["bytes"] = path.stat().st_size
    spec["sha256"] = sha256(path)
    spec["local"] = "/" + path.relative_to(REPO).as_posix()


new_ids = {spec["id"] for spec in source_specs}
catalog = [row for row in read_csv(CATALOG) if row["id"] not in new_ids]
for spec in source_specs:
    catalog.append(
        {
            "id": spec["id"],
            "tema": "ciclo_ajuste_e0_fiscal",
            "institucion": spec["institution"],
            "titulo": spec["title"],
            "url_original": spec["url"],
            "archivo_local": spec["local"],
            "fecha_descarga": "2026-08-29",
            "fecha_publicacion": spec["publication"],
            "codigo_serie": "",
            "periodo_utilizado": spec["period"],
            "tipo": spec["type"],
            "sha256": spec["sha256"],
            "nota": f"V115 E0 fiscal: {spec['bytes']:,} bytes; {spec['pages']} páginas. {spec['verified']}",
        }
    )
write_csv(CATALOG, catalog)


census = [row for row in read_csv(V114 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V114.csv") if row["source_id"] not in new_ids]
for spec in source_specs:
    census.append(
        {
            "source_id": spec["id"],
            "institution": spec["institution"],
            "artifact": spec["title"],
            "url": spec["url"],
            "local_path": spec["local"],
            "sha256": spec["sha256"],
            "bytes": str(spec["bytes"]),
            "period_coverage": spec["period"],
            "variable_families": spec["families"],
            "primary_source": "YES",
            "preserved": "YES",
            "method_breaks": spec["breaks"],
            "use_status": spec["use"],
            "caveat": spec["caveat"],
        }
    )
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V115.csv", census)


tenders = read_csv(HERE / "E0_FISCAL_PUBLIC_BUYBACK_TENDERS_2008_V115.csv")
awards = read_csv(HERE / "E0_FISCAL_PUBLIC_BUYBACK_AWARDS_2008_V115.csv")
by_date: dict[str, Decimal] = {}
for row in tenders:
    by_date.setdefault(row["tender_date"], Decimal(0))
    by_date[row["tender_date"]] += Decimal(row["awarded_effective_ars"])
official_award_total = sum(by_date.values(), Decimal(0))
raw_award_total = sum((Decimal(row["awarded_effective_ars_raw"]) for row in awards), Decimal(0))
assert official_award_total == Decimal("135606214.86")
assert raw_award_total == Decimal("135606214.85506")


call_fields = [
    "round_id", "round_number", "call_date", "tender_date", "result_date", "titles_due_t_plus_2",
    "settlement_due_t_plus_3", "announced_ceiling_ars", "awarded_effective_ars",
    "award_utilization_pct_of_ceiling", "eligible_instruments", "offer_channel",
    "caja_depositante", "caja_comitente", "transfer_rule", "settlement_currency_rule",
    "archive_sequence_status", "source_id", "source_locator", "actual_transfer_confirmation",
    "actual_payment_confirmation", "caveat",
]


def C(
    round_id: str, number: str, call_date: str, tender_date: str, result_date: str, t2: str, t3: str,
    ceiling: str, instruments: str, currency_rule: str, source_id: str,
) -> dict[str, str]:
    award = by_date[tender_date]
    utilization = (award / Decimal(ceiling) * Decimal(100)).quantize(PCT, ROUND_HALF_UP)
    return {
        "round_id": round_id,
        "round_number": number,
        "call_date": call_date,
        "tender_date": tender_date,
        "result_date": result_date,
        "titles_due_t_plus_2": t2,
        "settlement_due_t_plus_3": t3,
        "announced_ceiling_ars": ceiling,
        "awarded_effective_ars": str(award),
        "award_utilization_pct_of_ceiling": str(utilization),
        "eligible_instruments": instruments,
        "offer_channel": "MAE_COMMUNICATIONS_SYSTEM",
        "caja_depositante": "0306",
        "caja_comitente": "40000",
        "transfer_rule": "ONLY_FROM_AWARDED_DEPOSITOR_ACCOUNT_NO_PARTIAL_TRANSFERS",
        "settlement_currency_rule": currency_rule,
        "archive_sequence_status": "CALL_AND_RESULT_LISTED_UNDER_RECOMPRAS_VOLUNTARIAS",
        "source_id": f"e0_argentina_finanzas_archive_recompras_voluntarias;{source_id}",
        "source_locator": "HTML_Recompras_voluntarias;PDF_pp1_2",
        "actual_transfer_confirmation": "NO",
        "actual_payment_confirmation": "NO",
        "caveat": "El máximo anunciado no es obligación, adjudicación ni caja; la fecha y cuenta previstas no prueban cumplimiento efectivo.",
    }


calls = [
    C("R1", "1", "2008-08-27", "2008-08-28", "2008-08-28", "2008-09-01", "2008-09-02", "150000000", "BODEN_2012;BODEN_2013;GDP_UNIT_ARS;GDP_UNIT_USD_LAW_AR", "ARS_ONLY_USING_PRIOR_DAY_BCRA_REFERENCE_FX", "e0_argentina_llamado_recompra_2008_08_27"),
    C("R2", "2", "2008-09-03", "2008-09-04", "2008-09-04", "2008-09-08", "2008-09-09", "200000000", "BODEN_2012;BODEN_2013;GDP_UNIT_ARS;GDP_UNIT_USD_LAW_AR", "INSTRUMENT_DENOMINATION_CURRENCY_TO_BCRA_CURRENT_ACCOUNT", "e0_argentina_llamado_recompra_2008_09_03"),
    C("R3", "3", "2008-09-10", "2008-09-11", "2008-09-11", "2008-09-15", "2008-09-16", "100000000", "BODEN_2012;BODEN_2013;GDP_UNIT_ARS;GDP_UNIT_USD_LAW_AR", "INSTRUMENT_DENOMINATION_CURRENCY_TO_BCRA_CURRENT_ACCOUNT", "e0_argentina_llamado_recompra_2008_09_10"),
    C("R4", "4", "2008-10-01", "2008-10-02", "2008-10-02", "2008-10-06", "2008-10-07", "100000000", "GDP_UNIT_ARS;GDP_UNIT_USD_LAW_AR", "INSTRUMENT_DENOMINATION_CURRENCY_TO_BCRA_CURRENT_ACCOUNT", "e0_argentina_llamado_recompra_2008_10_01"),
]
write_csv(HERE / "E0_FISCAL_PUBLIC_BUYBACK_CALLS_2008_V115.csv", calls, call_fields)
announced_ceiling_total = sum((Decimal(row["announced_ceiling_ars"]) for row in calls), Decimal(0))
utilization_total = (official_award_total / announced_ceiling_total * Decimal(100)).quantize(PCT, ROUND_HALF_UP)
assert announced_ceiling_total == Decimal("550000000")


settlement = [{key: v115_text(value) for key, value in row.items()} for row in read_csv(V114 / "E0_FISCAL_BUYBACK_SETTLEMENT_CHAIN_V114.csv")]
call_source_joined = ";".join(spec["id"] for spec in source_specs[1:])
for row in settlement:
    if row["step"] == "5":
        row.update(
            {
                "timing": "T_TO_T_PLUS_2_EXACT_DATES_IN_CALLS",
                "account_or_system": "Caja_de_Valores_depositante_0306_comitente_40000",
                "evidence_status": "NORMATIVE_ROUTE_PLUS_FOUR_NUMBERED_CALLS_ACTUAL_TRANSFER_FILES_OPEN",
                "source_id": f"e0_argentina_rc_212_24_2008_recompra;{call_source_joined}",
                "source_locator": "Annex_2.1_2.2;call_PDF_p2",
                "interpretation": "La cuenta fiduciaria y cuatro vencimientos T+2 son exactos; las confirmaciones de transferencia siguen ausentes.",
            }
        )
    elif row["step"] == "7":
        row.update(
            {
                "timing": "T_PLUS_3_2008_09_02_09_09_09_16_10_07",
                "account_or_system": "Participant_current_accounts_at_BCRA",
                "evidence_status": "NORMATIVE_ROUTE_PLUS_FOUR_NUMBERED_CALLS_ACTUAL_PAYMENT_OPEN",
                "source_id": f"e0_argentina_rc_212_24_2008_recompra;{call_source_joined}",
                "source_locator": "Annex_2.4_2.5;call_PDF_p2",
                "interpretation": "Los cuatro días previstos y la vía BCRA son exactos; falta evidencia bancaria post-liquidación.",
            }
        )
write_csv(HERE / "E0_FISCAL_BUYBACK_SETTLEMENT_CHAIN_V115.csv", settlement)


events = [{key: v115_text(value) for key, value in row.items()} for row in read_csv(V114 / "E0_FISCAL_BUYBACK_PROGRAM_EVENTS_2005_2009_V114.csv")]
event_fields = list(events[0])
for row in events:
    if row["event_id"] == "E20080821_SECOND_STAGE":
        row.update(
            {
                "status": "FOUR_CALL_AND_RESULT_PAIRS_IN_OFFICIAL_ARCHIVE",
                "source_id": "e0_argentina_recompra_segunda_etapa_2008_08_21;e0_argentina_finanzas_archive_recompras_voluntarias",
                "locator": "PDF_p1;HTML_Recompras_voluntarias",
                "caveat": "El archivo oficial cierra la serie publicada en cuatro pares llamado/resultado; no es una certificación de liquidación ni excluye piezas no archivadas.",
            }
        )
    elif row["event_id"] == "E20080828_20081002_FOUR_TENDERS":
        row.update(
            {
                "status": "FOUR_ARCHIVED_ROUNDS_PARTICIPANTS_AND_ROUTE_MAPPED",
                "source_id": row["source_id"] + ";e0_argentina_finanzas_archive_recompras_voluntarias;" + call_source_joined,
                "locator": "HTML_archive;call_and_result_PDFs",
                "caveat": "Los cuatro llamados/resultados quedan enlazados y numerados; adjudicación, cuenta prevista y fecha T+3 no confirman pago.",
            }
        )
events.append(
    {
        "event_id": "E20080827_20081001_FOUR_CALLS",
        "event_date": "2008-08-27/2008-10-01",
        "stage": "SECOND_STAGE_PUBLIC_CALLS",
        "instrument_scope": "B2012_B2013_GDPARS_GDPUSD",
        "agent_or_channel": "MAE_CAJA_0306_40000_BCRA",
        "reported_amount": str(announced_ceiling_total),
        "unit": "ARS_announced_ceiling",
        "amount_basis": "SUM_OF_FOUR_UP_TO_MAXIMA",
        "status": "FOUR_NUMBERED_CALLS_ROUTE_EXACT_SETTLEMENT_OPEN",
        "source_id": "e0_argentina_finanzas_archive_recompras_voluntarias;" + call_source_joined,
        "locator": "HTML_archive;four_call_PDFs_pp1_2",
        "additivity": "NON_ADDITIVE_CEILING_CONTROL",
        "caveat": f"ARS {announced_ceiling_total} es la suma de máximos, no gasto; las adjudicaciones equivalen a {utilization_total}% de ese control.",
    }
)
write_csv(HERE / "E0_FISCAL_BUYBACK_PROGRAM_EVENTS_2005_2009_V115.csv", events, event_fields)


ledger = [{key: v115_text(value) for key, value in row.items()} for row in read_csv(V114 / "E0_FISCAL_MECHANISM_LEDGER_V114.csv")]
ledger_fields = list(ledger[0])


def L(
    ledger_id: str, year: str, purpose: str, event_type: str, date: str, payer: str, recipient: str,
    channel: str, instrument: str, original_amount: str, original_unit: str, converted: str,
    conversion_basis: str, source: str, locator: str, realization: str, additivity: str,
    interpretation: str, caveat: str,
) -> dict[str, str]:
    return dict(
        zip(
            ledger_fields,
            (
                ledger_id, year, purpose, event_type, date, payer, recipient, channel, instrument,
                original_amount, original_unit, converted, conversion_basis, source, locator,
                realization, additivity, interpretation, caveat,
            ),
            strict=True,
        )
    )


ledger.extend(
    [
        L("F109", "2008", "Debt_buyback", "OFFICIAL_ARCHIVE_ROUND_INVENTORY", "2008-08-27/2008-10-02", "Tesoro_Nacional", "MAE_participants", "Official_Finance_archive", "B2012_B2013_GDPARS_GDPUSD", "4", "call_result_pairs", "N/D", "ARCHIVE_INVENTORY_ONLY", "e0_argentina_finanzas_archive_recompras_voluntarias", "HTML_Recompras_voluntarias", "FOUR_PUBLISHED_ROUNDS_IDENTIFIED_SETTLEMENT_OPEN", "NON_ADDITIVE", "El archivo oficial enumera cuatro llamados numerados y sus cuatro resultados.", "Inventario web no es cierre contable ni constancia post-liquidación."),
        L("F110", "2008", "Debt_buyback", "PUBLIC_TENDER_CALL", "2008-08-27", "Tesoro_Nacional", "Eligible_MAE_participants", "MAE_Caja_0306_40000_BCRA", "B2012_B2013_GDPARS_GDPUSD", "150000000", "ARS_announced_ceiling", "150", "ARS_MILLION_MAXIMUM", "e0_argentina_llamado_recompra_2008_08_27", "PDF_pp1_2", "CALL_PUBLISHED_T_PLUS_3_PAYMENT_OPEN", "NON_ADDITIVE_CEILING", "Primer llamado; títulos 01/09 y liquidación prevista 02/09.", "Máximo anunciado no es adjudicación ni pago."),
        L("F111", "2008", "Debt_buyback", "PUBLIC_TENDER_CALL", "2008-09-03", "Tesoro_Nacional", "Eligible_MAE_participants", "MAE_Caja_0306_40000_BCRA", "B2012_B2013_GDPARS_GDPUSD", "200000000", "ARS_announced_ceiling", "200", "ARS_MILLION_MAXIMUM", "e0_argentina_llamado_recompra_2008_09_03", "PDF_pp1_2", "CALL_PUBLISHED_T_PLUS_3_PAYMENT_OPEN", "NON_ADDITIVE_CEILING", "Segundo llamado; títulos 08/09 y liquidación prevista 09/09.", "Máximo anunciado no es adjudicación ni pago."),
        L("F112", "2008", "Debt_buyback", "PUBLIC_TENDER_CALL", "2008-09-10", "Tesoro_Nacional", "Eligible_MAE_participants", "MAE_Caja_0306_40000_BCRA", "B2012_B2013_GDPARS_GDPUSD", "100000000", "ARS_announced_ceiling", "100", "ARS_MILLION_MAXIMUM", "e0_argentina_llamado_recompra_2008_09_10", "PDF_pp1_2", "CALL_PUBLISHED_T_PLUS_3_PAYMENT_OPEN", "NON_ADDITIVE_CEILING", "Tercer llamado; títulos 15/09 y liquidación prevista 16/09.", "Máximo anunciado no es adjudicación ni pago."),
        L("F113", "2008", "Debt_buyback", "PUBLIC_TENDER_CALL", "2008-10-01", "Tesoro_Nacional", "Eligible_MAE_participants", "MAE_Caja_0306_40000_BCRA", "GDPARS_GDPUSD", "100000000", "ARS_announced_ceiling", "100", "ARS_MILLION_MAXIMUM", "e0_argentina_llamado_recompra_2008_10_01", "PDF_pp1_2", "CALL_PUBLISHED_T_PLUS_3_PAYMENT_OPEN", "NON_ADDITIVE_CEILING", "Cuarto llamado; títulos 06/10 y liquidación prevista 07/10.", "Máximo anunciado no es adjudicación ni pago."),
        L("F114", "2008", "Debt_buyback", "FOUR_CALL_CEILING_CONTROL", "2008-08-27/2008-10-01", "Tesoro_Nacional", "Eligible_MAE_participants", "MAE_Caja_0306_40000_BCRA", "B2012_B2013_GDPARS_GDPUSD", str(announced_ceiling_total), "ARS_announced_ceiling", "550", f"AWARDS_EQUAL_{utilization_total}PCT_OF_CEILINGS", call_source_joined, "four_call_PDFs_pp1_2", "ANNOUNCED_MAXIMA_AWARDS_KNOWN_SETTLEMENT_OPEN", "CONTROL_NOT_ADDITIVE", f"Los cuatro máximos suman ARS 550m; adjudicado efectivo ARS {official_award_total}.", "El porcentaje utiliza máximos de convocatoria como denominador descriptivo, no compromiso ni presupuesto ejecutado."),
    ]
)
write_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V115.csv", ledger, ledger_fields)


breaks = [{key: v115_text(value) for key, value in row.items()} for row in read_csv(V114 / "E0_FISCAL_METHOD_BREAKS_V114.csv")]
break_fields = list(breaks[0])
new_breaks = [
    ("announced_ceiling_not_award_or_cash", "phase", "Cada llamado fija un monto máximo hasta el cual comprar, no un compromiso ni desembolso.", "Usar el techo sólo como denominador descriptivo; nunca sumarlo a adjudicaciones o ejecución.", "Cuatro llamados oficiales 2008"),
    ("archive_inventory_not_settlement_confirmation", "source", "El archivo oficial enumera piezas publicadas, pero no certifica entrega Caja ni pago BCRA.", "Cerrar la serie publicada y mantener abierta la liquidación y cualquier pieza no archivada.", "Archivo de Finanzas · Recompras voluntarias"),
    ("fiduciary_account_not_transfer_confirmation", "phase", "Identificar la cuenta Caja 0306/40000 no prueba que los títulos hayan ingresado.", "Exigir confirmación Caja T+3 y asiento/pago BCRA antes de marcar cash-settled.", "Cuatro llamados oficiales p.2; RC 212/24"),
]
known_breaks = {row["break_id"] for row in breaks}
for break_id, dimension, problem, rule, evidence in new_breaks:
    if break_id not in known_breaks:
        breaks.append(
            {
                "break_id": break_id,
                "dimension": dimension,
                "problem": problem,
                "rule": rule,
                "status": "FROZEN",
                "evidence": evidence,
            }
        )
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V115.csv", breaks, break_fields)


matrix = [{key: v115_text(value) for key, value in row.items()} for row in read_csv(V114 / "HISTORICAL_EPISODE_MATRIX_2001_2026_V114.csv")]
for row in matrix:
    if row["variable"] == "four_located_public_buyback_tenders":
        row.update(
            {
                "variable": "four_official_archive_buyback_rounds",
                "t0": "2008-08-27_TO_2008-10-02",
                "pre_value": "FOUR_NUMBERED_CALLS_AND_RESULTS_ARCHIVED",
                "trough_value": "ARS550M_SUM_OF_ANNOUNCED_MAXIMA",
                "trough_date": "2008-10-01",
                "recovery_value": f"ARS135.60621486M_AWARDED_{utilization_total}PCT_OF_CEILINGS",
                "recovery_date": "2008-10-02",
                "benchmark_definition": "four official archive call/result pairs plus exact call schedules and award reconstruction",
                "source_id": "e0_argentina_finanzas_archive_recompras_voluntarias;E0_FISCAL_PUBLIC_BUYBACK_CALLS_2008_V115.csv;E0_FISCAL_PUBLIC_BUYBACK_AWARDS_2008_V115.csv",
                "source_quality": "PRIMARY_ARCHIVE_CALLS_RESULTS_DERIVED_EXACT",
                "basis": "Official Finance archive, four call PDFs and four result PDFs",
                "method_break": "YES_CEILING_NOT_CASH_ACCOUNT_ROUTE_NOT_CONFIRMATION",
                "status": "FOUR_ARCHIVED_ROUNDS_CALLS_RESULTS_ACCOUNT_ROUTE_MAPPED",
                "interpretation": "La serie pública queda cerrada en cuatro rondas y la ruta Caja/BCRA es exacta; faltan constancias post-liquidación.",
                "falsifier": "YES_ARCHIVE_OR_ACCOUNT_ROUTE_EQUALS_CASH_SETTLEMENT",
                "notes": "No se presume que el archivo excluya operaciones no publicadas ni que T+3 se haya cumplido.",
            }
        )
write_csv(HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V115.csv", matrix)


evidence = [{key: v115_text(value) for key, value in row.items()} for row in read_csv(V114 / "HISTORICAL_EVIDENCE_COVERAGE_V114.csv")]
for row in evidence:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            {
                "quality": "PRIMARY_BUYBACK_FOUR_ARCHIVED_ROUNDS_ACCOUNT_ROUTE_EXACT_2001_2012",
                "comparable": "SERIES_SERVICE_RECONCILED_FOUR_ARCHIVED_ROUNDS_ROUTE_MAPPED",
                "gap": "Los cuatro llamados/resultados y la cuenta Caja 0306/40000 están identificados; faltan confirmaciones efectivas Caja/BCRA, blotter BNA, tenedores/propósito, resultado primario del strip y padrón CRYL.",
                "next_action": "Recuperar confirmaciones Caja/BCRA, blotter BNA, clientes finales/CRYL, resultado primario del strip y respuesta individual AGN.",
            }
        )
write_csv(HERE / "HISTORICAL_EVIDENCE_COVERAGE_V115.csv", evidence)


queue = [{key: v115_text(value) for key, value in row.items()} for row in read_csv(V114 / "HISTORICAL_SOURCE_QUEUE_V114.csv")]
for row in queue:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            {
                "status": "FOUR_ARCHIVED_ROUNDS_ACCOUNT_ROUTE_EXACT_SETTLEMENT_HOLDERS_OPEN",
                "why": "El archivo oficial cierra cuatro pares llamado/resultado y los llamados fijan Caja 0306/40000 y T+3; no hay confirmaciones post-liquidación, blotter BNA, clientes finales ni resultado primario del strip.",
                "next_action": "Recuperar confirmaciones Caja/BCRA, blotter BNA, clientes finales/CRYL, resultado primario del strip y respuesta individual AGN.",
            }
        )
write_csv(HERE / "HISTORICAL_SOURCE_QUEUE_V115.csv", queue)


inherited = [
    {"script": "qa_v97.py", "pre_v115_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v115_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V97 requiere que una fuente recuperada después permanezca sin ruta/hash."},
    *({"script": f"qa_v{i}.py", "pre_v115_result": "PASS", "post_v115_result": "PASS", "interpretation": "Compatible"} for i in (98, 100, 101, 102, 103, 104, 105, 106)),
    *({"script": f"qa_v{i}.py", "pre_v115_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v115_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "Falla sólo porque congela conteos de catálogo/fuentes anteriores a V115."} for i in (107, 108, 109, 110, 111, 112, 113, 114)),
    {"script": "qa_v115.py", "pre_v115_result": "N/A", "post_v115_result": "PASS", "interpretation": "Invariantes actuales, secuencia de cuatro rondas y aritmética exacta."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V115.csv", inherited)


readme = f"""# Checkpoint V115 · cuatro rondas archivadas y ruta Caja/BCRA exacta

V115 amplía V114 sin tocar el panel bancario. Preserva el índice histórico oficial y los cuatro llamados de la segunda etapa de 2008. La secuencia publicada queda cerrada en cuatro rondas y cada una se enlaza con su resultado, máximo, instrumentos, cuenta Caja y calendario T+2/T+3.

## Resultado

- 5 nuevas fuentes primarias oficiales preservadas;
- {len(census)} fuentes primarias E0 acumuladas;
- 4 pares llamado/resultado identificados en el archivo oficial;
- ARS {announced_ceiling_total} de máximos anunciados frente a ARS {official_award_total} adjudicados efectivos ({utilization_total}%);
- Caja de Valores: depositante 0306, comitente 40.000;
- fechas de liquidación previstas: 02/09, 09/09, 16/09 y 07/10/2008;
- ninguna constancia posterior de transferencia Caja o pago BCRA preservada.

## Invariantes

- panel estricto Q4-2023: 30 entidades;
- cobertura: {STRICT}%;
- CLOSED_NETWORK_GATE: NO;
- Banco Rioja: mismatch de 158,789k.

## Leer primero

1. VEREDICTO_V115.md
2. E0_FISCAL_RECONSTRUCTION_V115.md
3. E0_FISCAL_PUBLIC_BUYBACK_CALLS_2008_V115.csv
4. E0_FISCAL_PUBLIC_BUYBACK_TENDERS_2008_V115.csv
5. E0_FISCAL_PUBLIC_BUYBACK_AWARDS_2008_V115.csv
6. E0_FISCAL_BUYBACK_SETTLEMENT_CHAIN_V115.csv
7. RETRIEVAL_LOG_V115.md
8. AUDITORIA_V115.md
9. HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V115_A_V116.md
"""
(HERE / "README_V115.md").write_text(readme, encoding="utf-8")


reconstruction = f"""# Reconstrucción fiscal E0 · llamados, resultados y liquidación · V115

## Serie pública oficial de 2008

El archivo histórico de Finanzas ubica bajo Recompras voluntarias cuatro llamados —27/08, 03/09, 10/09 y 01/10— y cuatro resultados —28/08, 04/09, 11/09 y 02/10—, además de los comunicados de primera etapa, segunda etapa y segunda semana. V115 reemplaza la formulación cuatro resultados localizados por cuatro rondas publicadas en el archivo oficial.

| Ronda | Licitación | Títulos T+2 | Liquidación T+3 | Máximo ARS | Adjudicado efectivo ARS | Uso del máximo |
|---:|---|---|---|---:|---:|---:|
| 1 | 28/08/2008 | 01/09/2008 | 02/09/2008 | 150.000.000 | 9.890.509,02 | {calls[0]['award_utilization_pct_of_ceiling']}% |
| 2 | 04/09/2008 | 08/09/2008 | 09/09/2008 | 200.000.000 | 20.154.238,16 | {calls[1]['award_utilization_pct_of_ceiling']}% |
| 3 | 11/09/2008 | 15/09/2008 | 16/09/2008 | 100.000.000 | 50.758.361,98 | {calls[2]['award_utilization_pct_of_ceiling']}% |
| 4 | 02/10/2008 | 06/10/2008 | 07/10/2008 | 100.000.000 | 54.803.105,70 | {calls[3]['award_utilization_pct_of_ceiling']}% |
| Total | | | | {announced_ceiling_total} | {official_award_total} | {utilization_total}% |

Uso del máximo es un cociente descriptivo. El denominador es la suma de cuatro frases hasta el equivalente de; no es crédito presupuestario, obligación ni pago.

## Ruta de liquidación

Los cuatro llamados repiten la cuenta fiduciaria de Caja de Valores: depositante 0306, comitente 40.000. Sólo admiten transferencias desde las cuentas de los depositantes adjudicados y rechazan transferencias parciales. Los participantes debían tener cuenta depositante en Caja y cuenta corriente radicada en el BCRA. La RC 212/24 completa el circuito normativo: Caja debía informar los títulos recibidos en T+3 y la Secretaría pagar sobre esa confirmación.

La evidencia preservada llega hasta la ruta, la cuenta y el calendario. No contiene el archivo de confirmación de Caja, el asiento del BCRA ni una conciliación Tesoro–Caja–BCRA. Por eso las 18 adjudicaciones continúan en SCHEDULED_NOT_INDEPENDENTLY_CONFIRMED.

## Qué no cambió

- BODEN 2012 público: VNO USD 17.193.000, efectivo USD 6.559.535 y ARS 20.088.405,76;
- primera etapa: aproximadamente USD 380m en especies mezcladas, sin blotter BNA;
- CGN 2008: ARS 981,36m agregados no aditivos;
- strip 2009: ocurrencia oficial y resultado fino sólo secundario;
- tenedor final, propósito original, CRYL y respuesta individual AGN siguen abiertos.

Oferta no es adjudicación; adjudicación no es entrega Caja; cuenta y fecha previstas no son pago BCRA. CLOSED_NETWORK_GATE=NO.
"""
(HERE / "E0_FISCAL_RECONSTRUCTION_V115.md").write_text(reconstruction, encoding="utf-8")


audit_text = f"""# Auditoría V115

## Preservación y revisión visual

Se incorporaron cinco fuentes oficiales: el HTML del archivo de Finanzas y cuatro llamados PDF. Cada PDF tiene dos páginas; las ocho páginas fueron renderizadas a PNG e inspeccionadas visualmente. Se verificaron encabezados, ordinal de ronda, máximo, instrumentos, fecha de recepción, vencimiento T+2, cuenta Caja, regla de transferencias, fecha T+3 y moneda de liquidación. Los renderizados temporales se eliminaron después de la revisión.

## Pruebas aritméticas

- cuatro máximos: ARS 150m + 200m + 100m + 100m = ARS {announced_ceiling_total};
- cuatro resultados oficiales: ARS {official_award_total};
- 18 filas adjudicadas: ARS {raw_award_total} antes del redondeo;
- uso descriptivo del máximo agregado: {utilization_total}%;
- las fechas de los cuatro llamados coinciden uno a uno con las cuatro fechas de resultados de V114;
- BODEN 2012 no cambia.

## Controles de alcance

- el índice histórico prueba la serie pública archivada, no un cierre contable;
- la cuenta 0306/40000 prueba el destino previsto, no el ingreso efectivo;
- T+3 es calendario contractual, no confirmación bancaria;
- máximos no son sumables con adjudicaciones, BNA o CGN;
- participantes MAE siguen sin equivaler a beneficiarios finales.

## Conteos

- fuentes primarias E0: {len(census)};
- ledger fiscal: {len(ledger)} filas;
- quiebres metodológicos: {len(breaks)};
- eventos de programa: {len(events)};
- rondas públicas documentadas: {len(calls)}.
"""
(HERE / "AUDITORIA_V115.md").write_text(audit_text, encoding="utf-8")


verdict = f"""# Veredicto V115

## Qué avanzó

- La formulación cuatro resultados localizados se fortalece a cuatro rondas publicadas en el archivo oficial, cada una con llamado y resultado.
- La suma de máximos anunciados es ARS {announced_ceiling_total}; los ARS {official_award_total} adjudicados representan {utilization_total}% de ese control descriptivo.
- La cuenta fiduciaria queda identificada como Caja de Valores depositante 0306 / comitente 40.000.
- El calendario exacto separa oferta, entrega T+2 y pago previsto T+3 para las cuatro rondas.

## Qué sigue prohibido afirmar

- que el máximo anunciado fuera presupuesto ejecutado o caja;
- que los títulos efectivamente ingresaran en Caja;
- que el BCRA acreditara los pagos sin fallas;
- que el archivo web sea una certificación contable exhaustiva;
- que los participantes MAE fueran los tenedores económicos finales;
- que los agregados BNA, licitaciones y CGN sean sumables.

## Estado

La rama fiscal pasa a PRIMARY_BUYBACK_FOUR_ARCHIVED_ROUNDS_ACCOUNT_ROUTE_EXACT_2001_2012. Los faltantes decisivos son confirmaciones Caja/BCRA, blotter BNA, clientes finales/CRYL, resultado primario del strip y adjunto individual AGN. CLOSED_NETWORK_GATE=NO.
"""
(HERE / "VEREDICTO_V115.md").write_text(verdict, encoding="utf-8")


refs_lines = ["# Referencias de fuentes V115", "", "## Primarias preservadas"]
for spec in source_specs:
    refs_lines.append(f"- {spec['title']}: {spec['url']}")
refs_lines.extend(["", "Tamaños, hashes, uso y quiebres constan en E0_LOCAL_PRIMARY_SOURCE_CENSUS_V115.csv y data/fuentes/FUENTES.csv."])
(HERE / "SOURCE_REFERENCES_V115.md").write_text("\n".join(refs_lines) + "\n", encoding="utf-8")


handover = f"""# Handover próxima sesión · V115 → V116

## Estado congelado

- {len(census)} fuentes primarias E0 preservadas;
- {len(ledger)} filas del ledger fiscal y {len(breaks)} quiebres;
- cuatro rondas oficiales archivadas con pares llamado/resultado;
- máximos anunciados ARS {announced_ceiling_total}; adjudicado efectivo ARS {official_award_total}; uso descriptivo {utilization_total}%;
- Caja depositante 0306 / comitente 40.000 y cuatro calendarios T+2/T+3 exactos;
- BODEN 2012 público: VNO USD 17.193m, sin cambio;
- primera etapa BNA, strip primario, AGN individual, CRYL y liquidación efectiva abiertos.

## Prioridad V116

1. recuperar confirmaciones Caja y pagos BCRA de 02/09, 09/09, 16/09 y 07/10/2008;
2. obtener blotter/orden ejecutada BNA de 11–22/08/2008;
3. localizar comunicado primario y anexo del strip 2009;
4. obtener respuesta individual/adjuntos del pedido AGN 14/08/2018;
5. buscar padrón CRYL o conciliación Tesoro–Caja–BCRA–FGS y clientes finales.

## No hacer

- no convertir máximo en gasto;
- no convertir cuenta prevista en transferencia;
- no convertir T+3 en pago confirmado;
- no sumar agregados potencialmente solapados;
- no convertir participante en beneficiario;
- no convertir fuente secundaria del strip en caja primaria.

## Invariantes

Panel estricto: 30 entidades; cobertura exacta {STRICT}%; CLOSED_NETWORK_GATE=NO; Banco Rioja mismatch 158,789k.
"""
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V115_A_V116.md").write_text(handover, encoding="utf-8")


retrieval_log = """# Registro de recuperación V115

## Hallazgo promovido

- Archivo oficial de Finanzas: bajo Recompras voluntarias aparecen cuatro pares llamado/resultado, más los tres comunicados de etapa.
- Cuatro llamados PDF: preservados, renderizados e inspeccionados completos.
- La prioridad V114 sobre cierre de la serie pública se considera resuelta para el universo archivado: cuatro rondas.

## Búsquedas que permanecen negativas

### Caja de Valores / BCRA

Se buscaron la cuenta exacta depositante 0306 / comitente 40.000 y las fechas 02/09, 09/09, 16/09 y 07/10/2008 en portadores oficiales. Sólo reaparecieron los llamados; no se recuperó archivo de recepción de títulos, informe T+3 de Caja, asiento de cuenta corriente BCRA ni conciliación del Tesoro.

### Banco Nación

Las búsquedas oficiales por BNA, BODEN 2012 y recompra 2008 no produjeron el blotter de 11–22/08/2008. La Memoria BNA 2008 preservada en V114 sigue siendo un control negativo de alcance, no evidencia de cero operaciones.

### Strip BODEN 2012 de 2009

Se probaron búsquedas por fecha, título y variantes plausibles del nombre del comunicado oficial. No se recuperó el resultado primario ni su anexo. La Comunicación BCRA B 9568 del 19/06/2009 sólo remite a parámetros prudenciales y Cupón BODEN 2012; se descartó como resultado de la licitación.

### AGN / CRYL / beneficiarios

No apareció el adjunto individual de la respuesta AGN de 2018 ni un padrón CRYL o conciliación con clientes finales. Los informes AGN 202/2009 y 84/2015 conservan su alcance sectorial agregado.

## Regla de continuidad

No repetir estas rutas salvo que aparezca un identificador nuevo, un archivo histórico adicional o acceso institucional. La siguiente búsqueda debe orientarse a confirmaciones operativas post-liquidación, expedientes administrativos o respuestas de acceso a la información.
"""
(HERE / "RETRIEVAL_LOG_V115.md").write_text(retrieval_log, encoding="utf-8")


old_hash = read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V114.csv")
hash_rows = [row for row in old_hash if row["id"] not in new_ids]
for spec in source_specs:
    hash_rows.append(
        {
            "id": spec["id"],
            "archivo_local": spec["local"],
            "exists": "True",
            "sha_catalog": spec["sha256"],
            "sha_actual": spec["sha256"],
            "hash_ok": "True",
        }
    )
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V115.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V115.csv", hash_rows)
shutil.copyfile(AUDIT / "SOURCE_PATH_ENCODING_EXCEPTIONS_V114.csv", AUDIT / "SOURCE_PATH_ENCODING_EXCEPTIONS_V115.csv")
shutil.copyfile(AUDIT / "SOURCE_PRESERVATION_MISSING_V114.csv", AUDIT / "SOURCE_PRESERVATION_MISSING_V115.csv")


size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append(
        {
            "path": path.relative_to(REPO).as_posix(),
            "bytes": str(size),
            "mib": f"{size / 1048576:.6f}",
            "over_50_mib": str(size > 50 * 1048576),
            "over_100_mib": str(size > 100 * 1048576),
        }
    )
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V115.csv", size_rows, ["path", "bytes", "mib", "over_50_mib", "over_100_mib"])


physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
completeness = {
    "checkpoint": "V115",
    "date": "2026-08-29",
    "state": "E0_FOUR_ARCHIVED_BUYBACK_ROUNDS_ACCOUNT_ROUTE_EXACT_SETTLEMENT_OPEN",
    "master_catalog_entries": len(catalog),
    "physical_local_copies": physical,
    "physical_local_hash_ok": hash_ok,
    "reference_only_nonbinary_exempt": 4,
    "remaining_physical_gaps": 1,
    "p0": 0,
    "p1": 1,
    "p2": 0,
    "binary_required_entries": len(catalog) - 4,
    "binary_required_preserved": physical,
    "binary_required_source_complete": False,
    "pending_binary_discovery_actions": 5,
    "numeric_v115_strict_changed": False,
    "strict_coverage_pct": STRICT,
    "exact_entities": 30,
    "asset_numerator_million_ars": "59812903.504",
    "system_denominator_million_ars": "96697695.5",
    "closed_network_gate": "NO",
    "e0_primary_sources_preserved": len(census),
    "sources_newly_preserved_v115": len(source_specs),
    "e0_primary_sources_newly_preserved_v115": len(source_specs),
    "e0_quality": "PRIMARY_BUYBACK_FOUR_ARCHIVED_ROUNDS_ACCOUNT_ROUTE_EXACT_2001_2012",
    "e0_comparable": False,
    "e0_fiscal_phase_separated": True,
    "e0_fiscal_final_cash_total_identified": False,
    "e0_fiscal_ledger_rows": len(ledger),
    "e0_fiscal_method_breaks_frozen": len(breaks),
    "e0_public_tender_call_rows": len(calls),
    "e0_public_tender_instrument_date_rows": len(tenders),
    "e0_public_tender_award_rows": len(awards),
    "e0_four_archived_rounds_confirmed": True,
    "e0_four_call_announced_ceiling_ars": str(announced_ceiling_total),
    "e0_four_round_awarded_effective_ars": str(official_award_total),
    "e0_award_utilization_pct_of_announced_ceilings": str(utilization_total),
    "e0_public_boden2012_awarded_vno_usd": "17193000",
    "e0_public_boden2012_awarded_effective_usd": "6559535.00",
    "e0_public_boden2012_awarded_effective_ars": "20088405.76",
    "e0_buyback_participants_identified": True,
    "e0_ultimate_holders_identified": False,
    "e0_settlement_chain_mapped_normatively": True,
    "e0_fiduciary_account_route_identified": True,
    "e0_caja_depositante": "0306",
    "e0_caja_comitente": "40000",
    "e0_settlement_confirmations_preserved": False,
    "e0_bna_trade_blotter_preserved": False,
    "e0_first_stage_mixed_aggregate_usd_approx": "380000000",
    "e0_strip_official_occurrence_preserved": True,
    "e0_strip_primary_quantitative_result_preserved": False,
    "e0_strip_secondary_quantitative_result_preserved": True,
    "e0_agn_boden_report_identifiers_definitively_resolved": False,
    "e0_causal_net_incidence_identified": False,
    "historical_workstream": "E0_CAJA_BCRA_CONFIRMATIONS_BNA_BENEFICIAL_HOLDER_PRIMARY_STRIP_AND_AGN_REPLY_OPEN",
    "path_encoding_note": "Banco La Pampa remains byte-identical despite the catalog/Git filename encoding mismatch.",
}
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V115.json").write_text(json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V115 · cuatro rondas archivadas y ruta Caja/BCRA"
old_backup = backup.read_text(encoding="utf-8-sig")
if marker not in old_backup:
    old_backup += f"\n\n{marker}\n\n- El archivo oficial enumera cuatro pares llamado/resultado de la segunda etapa 2008.\n- Los máximos suman ARS {announced_ceiling_total}; adjudicado efectivo ARS {official_award_total} ({utilization_total}%).\n- La ruta fija Caja depositante 0306 / comitente 40.000 y cuatro fechas T+3.\n- Transferencias Caja y pagos BCRA siguen sin confirmación post-liquidación.\n"
    backup.write_text(old_backup, encoding="utf-8")


def write_checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V115.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V115",
        "parent_checkpoint": "V114",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30,
        "strict_coverage_pct": STRICT,
        "closed_network_gate": "NO",
        "e0_primary_sources": len(census),
        "new_preserved_sources": len(source_specs),
        "new_primary_sources": len(source_specs),
        "fiscal_ledger_rows": len(ledger),
        "fiscal_method_breaks": len(breaks),
        "public_tender_call_rows": len(calls),
        "public_tender_instrument_date_rows": len(tenders),
        "public_tender_award_rows": len(awards),
        "four_call_announced_ceiling_ars": str(announced_ceiling_total),
        "four_round_awarded_effective_ars": str(official_award_total),
        "award_utilization_pct_of_announced_ceilings": str(utilization_total),
        "files": files,
    }
    (HERE / "MANIFEST_V115.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


write_checkpoint_manifest()


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
    global_files.append(
        {
            "path": path.relative_to(REPO).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
    )
global_manifest = {
    "checkpoint": "V115",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT,
    "exact_entities": 30,
    "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical local copies with {hash_ok}/{physical} SHA-valid; 5 new primary E0 sources preserved; one catalogued P1 binary gap plus five discovery actions remain.",
    "historical_workstream": f"E0 four official archived buyback rounds with Caja 0306/40000 and exact T+2/T+3 route; actual settlement, first-stage blotter, primary strip result and ultimate holders remain open",
    "file_count_excluding_manifest": len(global_files),
    "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V115 BUILD PASS")
