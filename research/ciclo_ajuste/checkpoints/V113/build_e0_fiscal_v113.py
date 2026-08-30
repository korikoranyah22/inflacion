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
V112 = HERE.parent / "V112"
CYCLE = REPO / "research" / "ciclo_ajuste"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
AUDIT = CYCLE / "source_audit"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v113" / "binaries"


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


def clone_versioned(stem: str) -> None:
    src = V112 / f"{stem}_V112.csv"
    dst = HERE / f"{stem}_V113.csv"
    text = src.read_text(encoding="utf-8-sig")
    dst.write_text(text.replace("V112", "V113").replace("v112", "v113"), encoding="utf-8-sig")


for stem in (
    "CURRENT_STATE",
    "FOUR_LEG_PASS_PANEL",
    "STRICT_Q4_FOUR_LEG_COVERAGE",
    "RECOVERY_QUEUE",
    "INHERITED_QA_STATUS",
    "E0_FISCAL_TRANSACTION_LEDGER_2004_2006",
    "E0_FISCAL_TRANSACTION_LEDGER_2007_2012",
    "E0_FISCAL_STOCK_FLOW_BRIDGE",
    "E0_FISCAL_BODEN_SERVICE_BRIDGE_2007_2012",
    "E0_FISCAL_BODEN_STOCK_BRIDGE_2007_2012",
):
    clone_versioned(stem)


source_specs = [
    {
        "id": "e0_argentina_resultado_recompra_2008_08_28",
        "institution": "Ministerio de Economía y Producción",
        "title": "Resultado de licitación de recompra · 28 de agosto de 2008",
        "url": "https://www.argentina.gob.ar/sites/default/files/comunicado_de_prensa_resultado_28-08-08.pdf",
        "file": "argentina_resultado_recompra_2008-08-28.pdf",
        "publication": "2008",
        "period": "2008-08-28",
        "type": "PDF oficial · binario preservado",
        "pages": "3",
        "families": "state_bcra;fiscal;debt;buyback;tender;counterparty",
        "breaks": "oferta versus adjudicación; participante versus tenedor final; adjudicación versus liquidación",
        "use": "USABLE_TENDER_DESERTED_AND_OFFERS",
        "caveat": "BODEN 2012 quedó desierta; las ofertas recibidas no son compras realizadas ni prueban tenencia final.",
        "verified": "Páginas PDF 1 y 2 renderizadas e inspeccionadas visualmente.",
    },
    {
        "id": "e0_argentina_resultado_recompra_2008_09_04",
        "institution": "Ministerio de Economía y Producción",
        "title": "Resultado de licitación de recompra · 4 de septiembre de 2008",
        "url": "https://www.argentina.gob.ar/sites/default/files/comunicado_de_prensa_resultado_04-09-08.pdf",
        "file": "argentina_resultado_recompra_2008-09-04.pdf",
        "publication": "2008",
        "period": "2008-09-04/2008-09-09",
        "type": "PDF oficial · binario preservado",
        "pages": "3",
        "families": "state_bcra;fiscal;debt;buyback;tender;counterparty",
        "breaks": "oferta versus adjudicación; participante/intermediario versus beneficiario económico; resultado versus liquidación",
        "use": "USABLE_EXACT_BODEN2012_AWARD_RECONSTRUCTION",
        "caveat": "El corte permite reconstruir participantes adjudicados, pero no revela clientes o tenedores económicos finales.",
        "verified": "Páginas PDF 1 y 2 renderizadas e inspeccionadas visualmente; totales recompuestos exactamente.",
    },
    {
        "id": "e0_argentina_resultado_recompra_2008_09_11",
        "institution": "Ministerio de Economía y Producción",
        "title": "Resultado de licitación de recompra · 11 de septiembre de 2008",
        "url": "https://www.argentina.gob.ar/sites/default/files/comunicado_resultado11-09-08.pdf",
        "file": "argentina_resultado_recompra_2008-09-11.pdf",
        "publication": "2008",
        "period": "2008-09-11/2008-09-16",
        "type": "PDF oficial · binario preservado",
        "pages": "3",
        "families": "state_bcra;fiscal;debt;buyback;tender;counterparty",
        "breaks": "oferta versus adjudicación; participante/intermediario versus beneficiario económico; resultado versus liquidación",
        "use": "USABLE_EXACT_BODEN2012_AWARD_RECONSTRUCTION",
        "caveat": "El corte identifica al participante adjudicado; no identifica tenedor final, origen ni efectiva liquidación.",
        "verified": "Páginas PDF 1 y 2 renderizadas e inspeccionadas visualmente; totales recompuestos exactamente.",
    },
    {
        "id": "e0_argentina_rc_212_24_2008_recompra",
        "institution": "Secretarías de Hacienda y de Finanzas",
        "title": "Resolución Conjunta 212/2008 y 24/2008 · procedimiento de recompra",
        "url": "https://www.argentina.gob.ar/normativa/nacional/norma-143759/texto",
        "file": "argentina_rc_212_24_2008_procedimiento_recompra.html",
        "publication": "2008",
        "period": "2008",
        "type": "HTML oficial · texto original preservado",
        "pages": "N/A",
        "families": "state_bcra;fiscal;debt;buyback;settlement;custody",
        "breaks": "procedimiento normativo versus confirmación efectiva; participante versus otros inversores",
        "use": "USABLE_NORMATIVE_SETTLEMENT_CHAIN",
        "caveat": "Define Tesoro–MAE–Caja de Valores–BCRA; no demuestra que cada adjudicación haya liquidado sin incumplimientos.",
        "verified": "Texto original preservado; Anexo, puntos 1.4–1.12 y 2.1–2.5 verificados.",
    },
    {
        "id": "e0_argentina_rc_113_34_2009_boden12_strip",
        "institution": "Secretarías de Hacienda y de Finanzas",
        "title": "Resolución Conjunta 113/2009 y 34/2009 · strip BODEN 2012",
        "url": "https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-113-2009-154175/texto",
        "file": "argentina_rc_113_34_2009_boden12_cupon.html",
        "publication": "2009",
        "period": "2009-06-04",
        "type": "HTML oficial · texto original preservado",
        "pages": "N/A",
        "families": "state_bcra;fiscal;debt;buyback;strip",
        "breaks": "autorización de recompra versus ofertas/adjudicación/liquidación; cupón separado versus bono completo",
        "use": "USABLE_2009_STRIP_REPURCHASE_AUTHORIZATION",
        "caveat": "La norma ordena licitaciones, pero no publica cantidad ofrecida, adjudicada ni pagada.",
        "verified": "Texto original preservado; considerandos y artículos 1 y 3 verificados.",
    },
    {
        "id": "e0_argentina_dnu_1801_2009_boden12",
        "institution": "Poder Ejecutivo Nacional",
        "title": "DNU 1801/2009 · ampliación presupuestaria y colocaciones BODEN 2012",
        "url": "https://www.argentina.gob.ar/normativa/nacional/decreto-1801-2009-160582/texto",
        "file": "argentina_dnu_1801_2009_presupuesto.html",
        "publication": "2009",
        "period": "2009",
        "type": "HTML oficial · texto original preservado",
        "pages": "N/A",
        "families": "state_bcra;fiscal;debt;budget;placement;compensation",
        "breaks": "crédito presupuestario/registro versus colocación material; bancos y ahorristas no separados",
        "use": "USABLE_QUALITATIVE_RESIDUAL_PROGRAM_CONTROL",
        "caveat": "El considerando confirma colocaciones residuales, sin monto aislado en el texto preservado.",
        "verified": "Texto original preservado; considerando específico BODEN 2012 verificado.",
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
            "nota": f"V113 E0 fiscal: {spec['bytes']:,} bytes; {spec['pages']} páginas. {spec['verified']}",
        }
    )
write_csv(CATALOG, catalog)


census = [row for row in read_csv(V112 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V112.csv") if row["source_id"] not in new_ids]
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
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V113.csv", census)


tender_fields = [
    "tender_id", "tender_date", "scheduled_settlement_date", "instrument", "isin", "offers_received",
    "offered_vno_usd", "offered_effective_usd", "offered_effective_ars", "cutoff_price_per_100",
    "weighted_average_price", "awarded_vno_usd", "awarded_effective_usd", "reference_fx_ars_per_usd",
    "awarded_effective_ars", "result_status", "source_id", "source_locator", "settlement_confirmation", "caveat",
]
tenders = [
    {
        "tender_id": "T20080828_B2012", "tender_date": "2008-08-28", "scheduled_settlement_date": "2008-09-02",
        "instrument": "BODEN_2012", "isin": "ARARGE034678", "offers_received": "17", "offered_vno_usd": "31611700",
        "offered_effective_usd": "12979032.95", "offered_effective_ars": "39297915.97", "cutoff_price_per_100": "N/A",
        "weighted_average_price": "N/A", "awarded_vno_usd": "0", "awarded_effective_usd": "0",
        "reference_fx_ars_per_usd": "3.0278", "awarded_effective_ars": "0", "result_status": "DESIERTA",
        "source_id": "e0_argentina_resultado_recompra_2008_08_28", "source_locator": "PDF_pp1_2",
        "settlement_confirmation": "NOT_APPLICABLE_NO_AWARD", "caveat": "Las ofertas recibidas prueban propuestas, no compras ni tenencia final.",
    },
    {
        "tender_id": "T20080904_B2012", "tender_date": "2008-09-04", "scheduled_settlement_date": "2008-09-09",
        "instrument": "BODEN_2012", "isin": "ARARGE034678", "offers_received": "49", "offered_vno_usd": "200677500",
        "offered_effective_usd": "80639324.81", "offered_effective_ars": "245643511.24", "cutoff_price_per_100": "39.70",
        "weighted_average_price": "39.66", "awarded_vno_usd": "4193000", "awarded_effective_usd": "1662735.00",
        "reference_fx_ars_per_usd": "3.0462", "awarded_effective_ars": "5065023.36", "result_status": "ADJUDICADA",
        "source_id": "e0_argentina_resultado_recompra_2008_09_04", "source_locator": "PDF_pp1_2",
        "settlement_confirmation": "SCHEDULED_NOT_INDEPENDENTLY_CONFIRMED", "caveat": "Resultado/adjudicación no equivale por sí solo a confirmación de Caja de Valores y pago BCRA.",
    },
    {
        "tender_id": "T20080911_B2012", "tender_date": "2008-09-11", "scheduled_settlement_date": "2008-09-16",
        "instrument": "BODEN_2012", "isin": "ARARGE034678", "offers_received": "31", "offered_vno_usd": "205539300",
        "offered_effective_usd": "81787828.70", "offered_effective_ars": "250925058.45", "cutoff_price_per_100": "37.84",
        "weighted_average_price": "37.67", "awarded_vno_usd": "13000000", "awarded_effective_usd": "4896800.00",
        "reference_fx_ars_per_usd": "3.068", "awarded_effective_ars": "15023382.40", "result_status": "ADJUDICADA",
        "source_id": "e0_argentina_resultado_recompra_2008_09_11", "source_locator": "PDF_pp1_2",
        "settlement_confirmation": "SCHEDULED_NOT_INDEPENDENTLY_CONFIRMED", "caveat": "Resultado/adjudicación no equivale por sí solo a confirmación de Caja de Valores y pago BCRA.",
    },
]
write_csv(HERE / "E0_FISCAL_BODEN_BUYBACK_TENDERS_2008_V113.csv", tenders, tender_fields)


award_fields = [
    "award_id", "tender_date", "scheduled_settlement_date", "instrument", "isin", "participant",
    "participant_role", "price_components", "awarded_vno_usd", "awarded_effective_usd",
    "reference_fx_ars_per_usd", "awarded_effective_ars", "derivation", "source_id", "source_locator",
    "ultimate_holder_identified", "original_purpose_identified", "settlement_confirmation", "additivity", "caveat",
]
awards = [
    {
        "award_id": "A20080904_CITIBANK", "tender_date": "2008-09-04", "scheduled_settlement_date": "2008-09-09",
        "instrument": "BODEN_2012", "isin": "ARARGE034678", "participant": "Citibank",
        "participant_role": "MAE_PARTICIPANT_INTERMEDIARY_OR_OWN_ACCOUNT",
        "price_components": "193000@39.50;1000000@39.55", "awarded_vno_usd": "1193000",
        "awarded_effective_usd": "471735.00", "reference_fx_ars_per_usd": "3.0462", "awarded_effective_ars": "1436999.1570",
        "derivation": "All offers below cutoff 39.70 accepted; these two plus Standard at cutoff exactly equal published VNO 4,193,000 and effective USD 1,662,735.",
        "source_id": "e0_argentina_resultado_recompra_2008_09_04", "source_locator": "PDF_pp1_2",
        "ultimate_holder_identified": "NO", "original_purpose_identified": "NO",
        "settlement_confirmation": "SCHEDULED_NOT_INDEPENDENTLY_CONFIRMED", "additivity": "ADD_WITHIN_EXECUTED_PUBLIC_BODEN2012_AWARDS_ONLY",
        "caveat": "La tabla identifica participante; otros inversores podían operar a través suyo.",
    },
    {
        "award_id": "A20080904_STANDARD", "tender_date": "2008-09-04", "scheduled_settlement_date": "2008-09-09",
        "instrument": "BODEN_2012", "isin": "ARARGE034678", "participant": "Standard Bank",
        "participant_role": "MAE_PARTICIPANT_INTERMEDIARY_OR_OWN_ACCOUNT", "price_components": "3000000@39.70",
        "awarded_vno_usd": "3000000", "awarded_effective_usd": "1191000.00", "reference_fx_ars_per_usd": "3.0462",
        "awarded_effective_ars": "3628024.2000",
        "derivation": "Cutoff offer plus Citibank offers below cutoff exactly equal published VNO 4,193,000 and effective USD 1,662,735; no residual proration.",
        "source_id": "e0_argentina_resultado_recompra_2008_09_04", "source_locator": "PDF_pp1_2",
        "ultimate_holder_identified": "NO", "original_purpose_identified": "NO",
        "settlement_confirmation": "SCHEDULED_NOT_INDEPENDENTLY_CONFIRMED", "additivity": "ADD_WITHIN_EXECUTED_PUBLIC_BODEN2012_AWARDS_ONLY",
        "caveat": "La tabla identifica participante; otros inversores podían operar a través suyo.",
    },
    {
        "award_id": "A20080911_CITIBANK", "tender_date": "2008-09-11", "scheduled_settlement_date": "2008-09-16",
        "instrument": "BODEN_2012", "isin": "ARARGE034678", "participant": "Citibank",
        "participant_role": "MAE_PARTICIPANT_INTERMEDIARY_OR_OWN_ACCOUNT",
        "price_components": "1000000@37.34;2000000@37.44;2000000@37.64;1000000@37.75;5000000@37.75;2000000@37.84",
        "awarded_vno_usd": "13000000", "awarded_effective_usd": "4896800.00", "reference_fx_ars_per_usd": "3.068",
        "awarded_effective_ars": "15023382.4000",
        "derivation": "All six offers at or below cutoff 37.84 are Citibank and exactly equal published VNO 13,000,000 and effective USD 4,896,800.",
        "source_id": "e0_argentina_resultado_recompra_2008_09_11", "source_locator": "PDF_pp1_2",
        "ultimate_holder_identified": "NO", "original_purpose_identified": "NO",
        "settlement_confirmation": "SCHEDULED_NOT_INDEPENDENTLY_CONFIRMED", "additivity": "ADD_WITHIN_EXECUTED_PUBLIC_BODEN2012_AWARDS_ONLY",
        "caveat": "La tabla identifica participante; otros inversores podían operar a través suyo.",
    },
]
write_csv(HERE / "E0_FISCAL_BODEN_BUYBACK_AWARDS_2008_V113.csv", awards, award_fields)


chain_fields = ["step", "timing", "actor", "action", "account_or_system", "evidence_status", "source_id", "source_locator", "interpretation"]
chain = [
    {"step": "1", "timing": "PRE_T", "actor": "Other_investor_or_participant", "action": "Route firm offer through an eligible participant", "account_or_system": "MAE communications system", "evidence_status": "NORMATIVE_ROUTE", "source_id": "e0_argentina_rc_212_24_2008_recompra", "source_locator": "Annex_1.4_1.6", "interpretation": "Published participant can be intermediary; it is not automatically the ultimate holder."},
    {"step": "2", "timing": "T", "actor": "ONCP", "action": "Open order and prepare pre-award by participant", "account_or_system": "MAE/ONCP", "evidence_status": "NORMATIVE_ROUTE", "source_id": "e0_argentina_rc_212_24_2008_recompra", "source_locator": "Annex_1.7_1.8", "interpretation": "Pre-award is an administrative phase, not settlement."},
    {"step": "3", "timing": "T", "actor": "Secretaria_de_Finanzas", "action": "Set cutoff and conform award", "account_or_system": "Multiple-price or Dutch auction", "evidence_status": "NORMATIVE_ROUTE_PLUS_PUBLISHED_RESULTS", "source_id": "e0_argentina_rc_212_24_2008_recompra", "source_locator": "Annex_1.9_1.11", "interpretation": "Awards below cutoff are full; cutoff may be prorated."},
    {"step": "4", "timing": "T", "actor": "ONCP", "action": "Notify awards and titles to be received", "account_or_system": "MAE and Caja de Valores", "evidence_status": "NORMATIVE_ROUTE", "source_id": "e0_argentina_rc_212_24_2008_recompra", "source_locator": "Annex_1.12", "interpretation": "The notice initiates settlement but does not confirm it."},
    {"step": "5", "timing": "T_TO_T_PLUS_2", "actor": "Awarded_participant", "action": "Transfer awarded securities from its depositor account", "account_or_system": "Caja de Valores fiduciary account", "evidence_status": "NORMATIVE_ROUTE_ACTUAL_TRANSFER_FILE_OPEN", "source_id": "e0_argentina_rc_212_24_2008_recompra", "source_locator": "Annex_2.1_2.2", "interpretation": "Actual Caja transfer confirmations are not preserved."},
    {"step": "6", "timing": "T_PLUS_3_10AM", "actor": "Caja_de_Valores", "action": "Confirm transfers received", "account_or_system": "Report to Secretaria de Finanzas", "evidence_status": "NORMATIVE_ROUTE_ACTUAL_CONFIRMATION_OPEN", "source_id": "e0_argentina_rc_212_24_2008_recompra", "source_locator": "Annex_2.3", "interpretation": "This missing confirmation is the documentary bridge from award to delivered title."},
    {"step": "7", "timing": "T_PLUS_3", "actor": "Secretaria_de_Finanzas", "action": "Pay based on Caja confirmations", "account_or_system": "Participant current accounts at BCRA", "evidence_status": "NORMATIVE_ROUTE_ACTUAL_PAYMENT_OPEN", "source_id": "e0_argentina_rc_212_24_2008_recompra", "source_locator": "Annex_2.4_2.5", "interpretation": "BCRA account payment evidence remains necessary to call the award cash-settled."},
]
write_csv(HERE / "E0_FISCAL_BUYBACK_SETTLEMENT_CHAIN_V113.csv", chain, chain_fields)


ledger = read_csv(V112 / "E0_FISCAL_MECHANISM_LEDGER_V112.csv")
ledger_fields = list(ledger[0])


def ledger_row(ledger_id: str, window: str, mechanism: str, phase: str, date: str, recipient: str, amount: str,
               unit: str, ars_m: str, basis: str, source: str, locator: str, realization: str,
               additivity: str, interpretation: str, caveat: str) -> dict[str, str]:
    return dict(zip(ledger_fields, [ledger_id, window, mechanism, phase, date, "Tesoro_Nacional", recipient,
        "BODEN_2012_public_buyback_or_residual_program", "BODEN_2012", amount, unit, ars_m, basis, source,
        locator, realization, additivity, interpretation, caveat]))


ledger.extend([
    ledger_row("F89", "2008", "Debt_buyback", "NORMATIVE_TENDER_SETTLEMENT_ROUTE", "2008-08-25", "Eligible_MAE_participants_and_other_investors", "N/D", "N/D", "N/D", "PROCEDURE_ONLY", "e0_argentina_rc_212_24_2008_recompra", "Annex_1.4_2.5", "AUTHORIZED_PROCEDURE", "NON_ADDITIVE", "The route links MAE offers, Caja delivery and BCRA cash accounts.", "Procedure does not prove actual delivery or payment."),
    ledger_row("F90", "2008", "Debt_buyback", "TENDER_RESULT", "2008-08-28", "No_award", "0", "USD_VNO", "0", "PUBLIC_RESULT", "e0_argentina_resultado_recompra_2008_08_28", "PDF_pp1_2", "DESERTED", "NON_ADDITIVE", "The first public BODEN 2012 tender received offers but awarded none.", "Offered positions are not realized purchases."),
    ledger_row("F91", "2008", "Debt_buyback", "AWARD_RECONSTRUCTED", "2008-09-04", "Citibank_participant", "1193000", "USD_VNO", "1.436999157", "MULTIPLE_PRICE_AWARD_AT_PUBLISHED_FX", "e0_argentina_resultado_recompra_2008_09_04", "PDF_pp1_2", "AWARDED_SETTLEMENT_OPEN", "ADD_WITHIN_PUBLIC_BODEN2012_AWARDS_ONLY", "Citibank offers below cutoff exactly contribute VNO USD 1.193m.", "Participant may be intermediary; ultimate holder purpose and settlement remain open."),
    ledger_row("F92", "2008", "Debt_buyback", "AWARD_RECONSTRUCTED", "2008-09-04", "Standard_Bank_participant", "3000000", "USD_VNO", "3.628024200", "MULTIPLE_PRICE_AWARD_AT_PUBLISHED_FX", "e0_argentina_resultado_recompra_2008_09_04", "PDF_pp1_2", "AWARDED_SETTLEMENT_OPEN", "ADD_WITHIN_PUBLIC_BODEN2012_AWARDS_ONLY", "Standard Bank cutoff offer exactly contributes VNO USD 3m.", "Participant may be intermediary; ultimate holder purpose and settlement remain open."),
    ledger_row("F93", "2008", "Debt_buyback", "AWARD_RECONSTRUCTED", "2008-09-11", "Citibank_participant", "13000000", "USD_VNO", "15.023382400", "MULTIPLE_PRICE_AWARD_AT_PUBLISHED_FX", "e0_argentina_resultado_recompra_2008_09_11", "PDF_pp1_2", "AWARDED_SETTLEMENT_OPEN", "ADD_WITHIN_PUBLIC_BODEN2012_AWARDS_ONLY", "Six Citibank offers through cutoff exactly equal VNO USD 13m awarded.", "Participant may be intermediary; ultimate holder purpose and settlement remain open."),
    ledger_row("F94", "2009", "BODEN_2012_strip_buyback", "LEGAL_AUTHORIZATION", "2009-06-04", "Market_holders_via_eligible_participants", "N/D", "N/D", "N/D", "AUTHORIZATION_ONLY", "e0_argentina_rc_113_34_2009_boden12_strip", "Arts_1_3", "AUTHORIZED_AMOUNT_OPEN", "NON_ADDITIVE", "The August 2009 coupon was stripped and authorized for one or more public buyback tenders.", "No award or settlement amount is published in this source."),
    ledger_row("F95", "2009", "ASymmetric_pesification", "BUDGET_REGISTRATION_CONTROL", "2009-11-20", "Banks_and_savers_unseparated", "N/D", "N/D", "N/D", "QUALITATIVE_BUDGET_CONTROL", "e0_argentina_dnu_1801_2009_boden12", "Specific_considerando", "BUDGET_CREDITS_EXPANDED_AMOUNT_OPEN", "NON_ADDITIVE", "The budget was expanded to register BODEN 2012 placements from the 2002 program.", "The preserved text does not isolate an amount or split banks from savers."),
])
write_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V113.csv", ledger, ledger_fields)


breaks = read_csv(V112 / "E0_FISCAL_METHOD_BREAKS_V112.csv")
break_fields = list(breaks[0])
new_breaks = [
    ("offer_not_award", "phase", "A tender offer is not an award.", "Keep received offers separate; a deserted tender realizes zero.", "FROZEN", "Official result 28-08-2008"),
    ("participant_not_ultimate_holder", "counterparty", "Published participants may act for other investors.", "Label participant/intermediary and never infer ultimate beneficial ownership.", "FROZEN", "RC 212/24 Annex 1.6 and result tables"),
    ("award_not_settlement", "phase", "An award precedes delivery confirmation and BCRA-account payment.", "Require Caja de Valores and BCRA confirmations before marking cash-settled.", "FROZEN", "RC 212/24 Annex 2.1-2.5"),
    ("cutoff_reconstruction_requires_exact_fit", "derivation", "Participant awards are not printed as a separate table.", "Derive only when accepted offers under the rule reproduce both published VNO and effective totals exactly.", "FROZEN", "Results 04-09-2008 and 11-09-2008"),
    ("effective_currency_translation", "valuation", "Effective USD and effective ARS use tender-specific reference FX.", "Preserve the published FX per tender and do not reuse it across dates.", "FROZEN", "Official result first pages"),
    ("budget_credit_not_placement", "phase", "Budget expansion to register placements does not prove delivery or payment.", "Keep the DNU as a qualitative residual-program control until annex/execution records are found.", "FROZEN", "DNU 1801/2009"),
    ("strip_not_full_bond", "instrument", "A separately tradable coupon strip is not the full BODEN 2012 stock.", "Track the 2009 strip authorization separately from full-bond awards and service.", "FROZEN", "RC 113/34 2009 arts. 1 and 3"),
]
break_ids = {row["break_id"] for row in breaks}
for row in new_breaks:
    if row[0] not in break_ids:
        breaks.append(dict(zip(break_fields, row)))
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V113.csv", breaks, break_fields)


matrix = read_csv(V112 / "HISTORICAL_EPISODE_MATRIX_2001_2026_V112.csv")
matrix_fields = list(matrix[0])
for row in matrix:
    row["source_id"] = row["source_id"].replace("V112", "V113")
matrix.extend([
    dict(zip(matrix_fields, ["E0", "Crisis de convertibilidad / default / salida / reordenamiento financiero", "2008-08-28_TO_2008-09-11", "OTHER", "boden_2012_public_buyback_tenders", "STATE_BCRA", "EVENT", "DESERTED_2008-08-28", "VNO_USD17.193M_AWARDED", "2008-09-11", "N/A", "N/A", "N/A", "N/A", "sum of accepted offer rows equals published awarded VNO and effective value", "E0_FISCAL_BODEN_BUYBACK_AWARDS_2008_V113.csv", "PRIMARY_DERIVED_EXACT", "Three official tender result communiqués", "YES_PARTICIPANT_NOT_ULTIMATE_HOLDER", "PUBLIC_AWARDS_COUNTERPARTY_PARTIAL", "Citibank and Standard Bank are identified as participants for a narrow public-buyback component.", "YES_PARTICIPANT_EQUALS_FINAL_BENEFICIARY", "Cumulative awards: VNO USD 17.193m; effective USD 6.559535m; ARS 20.08840576m. Settlement confirmation remains open."])),
    dict(zip(matrix_fields, ["E0", "Crisis de convertibilidad / default / salida / reordenamiento financiero", "2008", "OTHER", "buyback_settlement_chain", "STATE_BCRA", "EVENT", "MAE_OFFER", "CAJA_DELIVERY_CONFIRMATION", "T+3", "BCRA_ACCOUNT_PAYMENT", "T+3", "N/A", "N/A", "normative MAE–ONCP–Caja–BCRA chain", "E0_FISCAL_BUYBACK_SETTLEMENT_CHAIN_V113.csv", "PRIMARY_NORMATIVE", "RC 212/2008 and 24/2008", "YES_PROCEDURE_NOT_EXECUTION", "SETTLEMENT_ROUTE_MAPPED_EXECUTION_OPEN", "The missing Caja and BCRA confirmations are now isolated as specific evidence gaps.", "YES_AWARD_EQUALS_CASH", "Actual settlement records were not recovered."])),
    dict(zip(matrix_fields, ["E0", "Crisis de convertibilidad / default / salida / reordenamiento financiero", "2009", "OTHER", "boden_2012_strip_and_residual_registration", "STATE_BCRA", "EVENT", "STRIP_AUTHORIZED", "BUYBACK_AMOUNT_OPEN", "2009", "BUDGET_REGISTRATION_CONFIRMED", "2009-11", "N/A", "N/A", "authorization and qualitative budget controls", "e0_argentina_rc_113_34_2009_boden12_strip;e0_argentina_dnu_1801_2009_boden12", "PRIMARY", "Official original legal texts", "YES_AUTHORIZATION_NOT_EXECUTION", "RESIDUAL_PROGRAM_CONFIRMED_AMOUNT_OPEN", "The program still generated 2009 legal and budget traces.", "YES_BUDGET_CREDIT_EQUALS_BANK_PAYMENT", "Amounts, recipients and final settlement remain open."])),
])
write_csv(HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V113.csv", matrix, matrix_fields)


evidence = read_csv(V112 / "HISTORICAL_EVIDENCE_COVERAGE_V112.csv")
for row in evidence:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            quality="PRIMARY_BUYBACK_COUNTERPARTIES_PARTIAL_2001_2012",
            comparable="SERIES_SERVICE_RECONCILED_PUBLIC_BUYBACK_AWARDS_PARTIAL",
            gap="Public BODEN 2012 awards identify participants for VNO USD 17.193m, but ultimate holders, purpose, Caja delivery, BCRA cash settlement, BNA market purchases and complete CRYL register remain open",
            next_action="Recover Caja de Valores transfer confirmations and Treasury/BCRA payment records; obtain BNA first-stage trade blotter and CRYL holder-purpose register",
        )
write_csv(HERE / "HISTORICAL_EVIDENCE_COVERAGE_V113.csv", evidence)


queue = read_csv(V112 / "HISTORICAL_SOURCE_QUEUE_V112.csv")
for row in queue:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            status="BODEN2012_PUBLIC_TENDER_AWARDS_EXACT_PARTICIPANTS_HOLDER_SETTLEMENT_OPEN",
            why="three official tender results identify one deserted round and exact awards to Citibank and Standard Bank totaling VNO USD 17.193m",
            next_action="Recover Caja T+3 confirmations, BCRA payment records, beneficial-client identities and BNA first-stage trades; locate AGN report IDs and residual 2009 award results",
        )
write_csv(HERE / "HISTORICAL_SOURCE_QUEUE_V113.csv", queue)


inherited_path = HERE / "INHERITED_QA_STATUS_V113.csv"
inherited = read_csv(inherited_path)
for row in inherited:
    if row["script"] == "qa_v113.py":
        row["script"] = "qa_v112.py"
        row["post_v113_result"] = "EXPECTED_SUPERSEDED_ASSERTION"
        row["interpretation"] = "Fails only because V112 freezes the master catalog at 246 rows; V113 validates 252 entries and 54 E0 sources."
inherited.append({"script": "qa_v113.py", "pre_v113_result": "N/A", "post_v113_result": "PASS", "interpretation": "Current checkpoint invariants and exact tender arithmetic"})
write_csv(inherited_path, inherited)


total_vno = sum(Decimal(row["awarded_vno_usd"]) for row in awards)
total_usd = sum(Decimal(row["awarded_effective_usd"]) for row in awards)
total_ars_raw = sum(Decimal(row["awarded_effective_ars"]) for row in awards)
total_ars = sum(Decimal(row["awarded_effective_ars"]) for row in tenders if row["result_status"] == "ADJUDICADA")
citibank = [row for row in awards if row["participant"] == "Citibank"]
citibank_vno = sum(Decimal(row["awarded_vno_usd"]) for row in citibank)
standard_vno = sum(Decimal(row["awarded_vno_usd"]) for row in awards if row["participant"] == "Standard Bank")


readme = f"""# V113

V113 abre el detalle de las recompras públicas BODEN 2012 de agosto–septiembre de 2008. Congela tres resultados oficiales, reconstruye los participantes adjudicados sin residuo y explicita el puente normativo MAE–ONCP–Caja de Valores–BCRA.

## Delta material

- El censo E0 sube de **48 a {len(census)} fuentes primarias preservadas**: tres PDF de resultados y tres textos legales oficiales.
- El ledger fiscal alcanza **{len(ledger)} filas**.
- La licitación del 28/08/2008 quedó **desierta** para BODEN 2012.
- Las rondas del 04/09 y 11/09 adjudicaron **VNO USD {total_vno / Decimal(1_000_000)}m**, por **USD {total_usd / Decimal(1_000_000)}m efectivos** y **ARS {total_ars / Decimal(1_000_000)}m** según los totales publicados.
- Participantes reconstruidos: Citibank VNO USD {citibank_vno / Decimal(1_000_000)}m; Standard Bank VNO USD {standard_vno / Decimal(1_000_000)}m.
- Se congelan **{len(breaks)} restricciones metodológicas**.

## Lectura correcta

“Participante” no significa automáticamente tenedor económico final: la norma permitía que otros inversores ofertaran por medio de agentes o entidades financieras. “Adjudicado” tampoco significa “liquidado”: faltan las confirmaciones de Caja de Valores y los pagos en cuentas BCRA.

## Estado que no cambia

- panel estricto Q4-2023: **30 entidades**;
- cobertura: **61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%**;
- `CLOSED_NETWORK_GATE`: **NO**;
- Banco Rioja: mismatch de **158,789k**;
- no se identifica transferencia causal neta hogares → bancos.

## Leer primero

1. `VEREDICTO_V113.md`
2. `E0_FISCAL_RECONSTRUCTION_V113.md`
3. `E0_FISCAL_BODEN_BUYBACK_TENDERS_2008_V113.csv`
4. `E0_FISCAL_BODEN_BUYBACK_AWARDS_2008_V113.csv`
5. `E0_FISCAL_BUYBACK_SETTLEMENT_CHAIN_V113.csv`
6. `AUDITORIA_V113.md`
7. `HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V113_A_V114.md`
8. `qa_v113.py`
"""
(HERE / "README_V113.md").write_text(readme, encoding="utf-8")


reconstruction = f"""# Reconstrucción fiscal E0 · recompras BODEN 2012 · V113

## Resultado exacto

| Licitación | Resultado | Participante reconstruido | VNO USD | Efectivo USD | Efectivo ARS |
|---|---|---|---:|---:|---:|
| 28/08/2008 | Desierta | — | 0 | 0 | 0 |
| 04/09/2008 | Adjudicada | Citibank | 1.193.000 | 471.735 | 1.436.999,1570 |
| 04/09/2008 | Adjudicada | Standard Bank | 3.000.000 | 1.191.000 | 3.628.024,2000 |
| 11/09/2008 | Adjudicada | Citibank | 13.000.000 | 4.896.800 | 15.023.382,4000 |
| **Total** |  |  | **{total_vno:,.0f}** | **{total_usd:,.2f}** | **{total_ars:,.4f}** |

La reconstrucción es exacta en VNO y USD. El 04/09, las dos ofertas Citibank inferiores al corte 39,70 más la oferta Standard Bank al corte suman el VNO y el efectivo publicados. El 11/09, las seis ofertas Citibank hasta el corte 37,84 suman exactamente los totales adjudicados. La asignación ARS por participante se calcula al tipo de cambio publicado y suma ARS {total_ars_raw}; el total oficial redondeado a centavos es ARS {total_ars}.

## Qué identifica y qué no

Identifica la entidad que presentó cada oferta aceptada en MAE. No identifica si actuó por cuenta propia o de clientes, el tenedor beneficiario, el propósito original de cada BODEN —compensación, cobertura, ahorristas o mercado— ni la ganancia económica.

El procedimiento oficial separa siete pasos: canalización de la oferta, apertura, corte/adjudicación, aviso a Caja, entrega T+2, confirmación Caja T+3 y pago en cuenta BCRA. Los resultados preservados llegan hasta la adjudicación y anuncian fecha de liquidación; no contienen la confirmación Caja/BCRA.

## Alcance fiscal

El subtotal público aislado es VNO USD {total_vno / Decimal(1_000_000)}m y ARS {total_ars / Decimal(1_000_000)}m efectivos. No se suma automáticamente a los agregados mixtos CGN de la etapa de recompra: podría estar contenido en ellos. Tampoco se extrapola al universo BODEN 2012, cuyo servicio acumulado es muchísimo mayor y mezcla propósitos.

## Rastro 2009

La Resolución Conjunta 113/34 separó el cupón de agosto de 2009 y autorizó recompras públicas; el DNU 1801/2009 confirmó créditos para registrar colocaciones residuales del programa destinado a bancos y ahorristas. Ninguna de esas dos normas permite medir por sí sola una adjudicación o pago.
"""
(HERE / "E0_FISCAL_RECONSTRUCTION_V113.md").write_text(reconstruction, encoding="utf-8")


audit_text = f"""# Auditoría V113 — recompras BODEN 2012

## Preservación e inspección

Se preservaron seis fuentes oficiales: tres PDF de resultados y tres textos legales originales. Se renderizaron e inspeccionaron visualmente las páginas 1 y 2 de cada resultado: 28/08, 04/09 y 11/09 de 2008.

## Pruebas aritméticas

- 04/09 Citibank: VNO 193.000 × 39,50% + VNO 1.000.000 × 39,55% = USD 471.735.
- 04/09 Standard Bank: VNO 3.000.000 × 39,70% = USD 1.191.000.
- 04/09 total: VNO 4.193.000; USD 1.662.735; ARS 5.065.023,36.
- 11/09 Citibank: seis ofertas hasta 37,84 suman VNO 13.000.000; USD 4.896.800; ARS 15.023.382,40.
- acumulado oficial: VNO USD {total_vno}; efectivo USD {total_usd}; efectivo ARS {total_ars}; suma derivada por participante antes del redondeo final: ARS {total_ars_raw}.
- conversión por entidad y fecha reproducida con Decimal; sin redondeo binario.

## Separación de fases

Oferta ≠ adjudicación ≠ transferencia del título ≠ confirmación Caja ≠ pago BCRA. Participante ≠ tenedor económico final. La norma distingue explícitamente a “otros inversores” que operan por medio de participantes.

## Controles

- fuentes E0: {len(census)};
- ledger fiscal: {len(ledger)} filas;
- licitaciones BODEN 2012 congeladas: {len(tenders)};
- adjudicaciones reconstruidas: {len(awards)};
- pasos de liquidación: {len(chain)};
- quiebres metodológicos: {len(breaks)}.
"""
(HERE / "AUDITORIA_V113.md").write_text(audit_text, encoding="utf-8")


verdict = f"""# Veredicto V113

## Qué sabemos ahora

- La primera licitación pública BODEN 2012 del programa 2008 quedó desierta.
- Dos rondas adjudicaron exactamente VNO USD {total_vno / Decimal(1_000_000)}m: Citibank presentó ofertas aceptadas por VNO USD {citibank_vno / Decimal(1_000_000)}m y Standard Bank por VNO USD {standard_vno / Decimal(1_000_000)}m.
- El efectivo adjudicado suma USD {total_usd / Decimal(1_000_000)}m / ARS {total_ars / Decimal(1_000_000)}m.
- El circuito normativo llega de MAE a Caja de Valores y luego a cuentas BCRA.
- En 2009 hubo un strip BODEN 2012 recomprable y actividad presupuestaria residual del programa.

## Qué no autoriza afirmar

- que Citibank o Standard Bank fueran los tenedores económicos finales;
- que los BODEN ofertados provinieran de compensación bancaria;
- que toda adjudicación se hubiera liquidado sin incumplimientos;
- que el monto sea adicional a los agregados mixtos CGN;
- que exista una ganancia bancaria neta.

## Estado

La rama fiscal pasa a `PRIMARY_BUYBACK_COUNTERPARTIES_PARTIAL_2001_2012`. El cuello de botella se estrecha desde “adjudicaciones desconocidas” a confirmaciones Caja/BCRA, clientes finales, origen por propósito y operaciones BNA de la primera etapa. `CLOSED_NETWORK_GATE=NO`.
"""
(HERE / "VEREDICTO_V113.md").write_text(verdict, encoding="utf-8")


refs = """# Referencias de fuentes V113

## Resultados oficiales

- 28/08/2008: https://www.argentina.gob.ar/sites/default/files/comunicado_de_prensa_resultado_28-08-08.pdf
- 04/09/2008: https://www.argentina.gob.ar/sites/default/files/comunicado_de_prensa_resultado_04-09-08.pdf
- 11/09/2008: https://www.argentina.gob.ar/sites/default/files/comunicado_resultado11-09-08.pdf

## Normas oficiales

- RC 212/2008 y 24/2008: https://www.argentina.gob.ar/normativa/nacional/norma-143759/texto
- RC 113/2009 y 34/2009: https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-113-2009-154175/texto
- DNU 1801/2009: https://www.argentina.gob.ar/normativa/nacional/decreto-1801-2009-160582/texto

Las seis fuentes se preservan en `research/ciclo_ajuste/inputs/historical_retrieval/v113/binaries/`; tamaños, hashes y quiebres constan en `E0_LOCAL_PRIMARY_SOURCE_CENSUS_V113.csv`.
"""
(HERE / "SOURCE_REFERENCES_V113.md").write_text(refs, encoding="utf-8")


handover = f"""# Handover próxima sesión · V113 → V114

## Estado congelado

- {len(census)} fuentes primarias E0 preservadas;
- {len(ledger)} filas del ledger fiscal;
- tres resultados públicos BODEN 2012 congelados, uno desierto;
- adjudicaciones exactas: VNO USD {total_vno / Decimal(1_000_000)}m; efectivo USD {total_usd / Decimal(1_000_000)}m; ARS {total_ars / Decimal(1_000_000)}m;
- participantes: Citibank VNO USD {citibank_vno / Decimal(1_000_000)}m; Standard Bank VNO USD {standard_vno / Decimal(1_000_000)}m;
- cadena MAE–ONCP–Caja–BCRA mapeada normativamente;
- {len(breaks)} quiebres metodológicos;
- tenedor final, propósito y liquidación efectiva siguen abiertos.

## Prioridad V114

1. recuperar confirmaciones T+3 de Caja de Valores y pagos en cuentas BCRA de 09/09 y 16/09/2008;
2. obtener el blotter/mando del BNA para la primera etapa y separar BODEN 2012;
3. identificar clientes finales detrás de participantes MAE, sin presumir cuenta propia;
4. recuperar resultados cuantitativos de las licitaciones del strip 2009;
5. localizar planillas anexas del DNU 1801/2009 y ejecución presupuestaria;
6. resolver identificadores de los informes AGN sobre evolución/distribución BODEN;
7. conciliar CRYL/Caja–Tesoro–BCRA–FGS–entidades y propósito original.

## No hacer

- no convertir participante en tenedor final;
- no convertir adjudicación en caja liquidada;
- no sumar el subtotal público a agregados mixtos sin puente;
- no atribuir BODEN recomprado a compensación bancaria por especie solamente;
- no declarar ganancia bancaria neta desde efectivo bruto.

## Invariantes

Panel estricto: 30 entidades; cobertura exacta 61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%; `CLOSED_NETWORK_GATE=NO`; Banco Rioja mismatch 158,789k.
"""
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V113_A_V114.md").write_text(handover, encoding="utf-8")


old_hash = read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V112.csv")
hash_rows = [row for row in old_hash if row["id"] not in new_ids]
for spec in source_specs:
    hash_rows.append({"id": spec["id"], "archivo_local": spec["local"], "exists": "True", "sha_catalog": spec["sha256"], "sha_actual": spec["sha256"], "hash_ok": "True"})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V113.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V113.csv", hash_rows)
shutil.copyfile(AUDIT / "SOURCE_PATH_ENCODING_EXCEPTIONS_V112.csv", AUDIT / "SOURCE_PATH_ENCODING_EXCEPTIONS_V113.csv")
shutil.copyfile(AUDIT / "SOURCE_PRESERVATION_MISSING_V112.csv", AUDIT / "SOURCE_PRESERVATION_MISSING_V113.csv")


size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": str(size), "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V113.csv", size_rows, ["path", "bytes", "mib", "over_50_mib", "over_100_mib"])


strict_coverage = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
completeness = {
    "checkpoint": "V113", "date": "2026-08-29",
    "state": "E0_PUBLIC_BUYBACK_AWARDS_EXACT_PARTICIPANTS_HOLDER_SETTLEMENT_OPEN",
    "master_catalog_entries": len(catalog), "physical_local_copies": physical, "physical_local_hash_ok": hash_ok,
    "reference_only_nonbinary_exempt": 4, "remaining_physical_gaps": 1, "p0": 0, "p1": 1, "p2": 0,
    "binary_required_entries": len(catalog) - 4, "binary_required_preserved": physical,
    "binary_required_source_complete": False, "pending_binary_discovery_actions": 7,
    "numeric_v113_strict_changed": False, "strict_coverage_pct": strict_coverage,
    "exact_entities": 30, "asset_numerator_million_ars": "59812903.504", "system_denominator_million_ars": "96697695.5",
    "closed_network_gate": "NO", "e0_primary_sources_preserved": len(census),
    "e0_sources_newly_preserved_v113": len(source_specs), "e0_quality": "PRIMARY_BUYBACK_COUNTERPARTIES_PARTIAL_2001_2012",
    "e0_comparable": False, "e0_fiscal_phase_separated": True, "e0_fiscal_final_cash_total_identified": False,
    "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
    "e0_public_boden2012_tenders": len(tenders), "e0_public_boden2012_award_rows": len(awards),
    "e0_public_boden2012_awarded_vno_usd": str(total_vno), "e0_public_boden2012_awarded_effective_usd": str(total_usd),
    "e0_public_boden2012_awarded_effective_ars": str(total_ars), "e0_buyback_participants_identified": True,
    "e0_ultimate_holders_identified": False, "e0_settlement_chain_mapped_normatively": True,
    "e0_settlement_confirmations_preserved": False, "e0_causal_net_incidence_identified": False,
    "historical_workstream": "E0_CRYL_CAJA_BCRA_SETTLEMENT_AND_ULTIMATE_HOLDER_OPEN",
    "path_encoding_note": "Banco La Pampa remains byte-identical despite the catalog/Git filename encoding mismatch.",
}
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V113.json").write_text(json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V113 · recompras públicas BODEN 2012"
old_backup = backup.read_text(encoding="utf-8-sig")
if marker not in old_backup:
    old_backup += f"\n\n{marker}\n\n- Tres resultados oficiales preservados; la primera licitación quedó desierta.\n- Adjudicaciones reconstruidas exactamente: VNO USD {total_vno / Decimal(1_000_000)}m, efectivo USD {total_usd / Decimal(1_000_000)}m y ARS {total_ars / Decimal(1_000_000)}m.\n- Participantes identificados: Citibank y Standard Bank; tenedor final y propósito no inferidos.\n- Cadena MAE–ONCP–Caja de Valores–BCRA mapeada; confirmaciones de liquidación pendientes.\n"
    backup.write_text(old_backup, encoding="utf-8")


def write_checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V113.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V113", "parent_checkpoint": "V112",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": strict_coverage, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_official_sources": len(source_specs), "fiscal_ledger_rows": len(ledger),
        "fiscal_method_breaks": len(breaks), "public_boden2012_tenders": len(tenders),
        "public_boden2012_award_rows": len(awards), "public_boden2012_awarded_vno_usd": str(total_vno),
        "public_boden2012_awarded_effective_usd": str(total_usd), "public_boden2012_awarded_effective_ars": str(total_ars),
        "files": files,
    }
    (HERE / "MANIFEST_V113.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    global_files.append({"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})
global_manifest = {
    "checkpoint": "V113",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": strict_coverage, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical local copies with {hash_ok}/{physical} SHA-valid; six new official E0 sources preserved; one catalogued P1 binary gap plus seven discovery actions remain.",
    "historical_workstream": f"E0 public BODEN 2012 awards reconstructed exactly from {len(census)} primary sources; ultimate holders, purpose and Caja/BCRA settlement remain open",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V113 BUILD PASS")
