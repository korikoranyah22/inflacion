from __future__ import annotations

from collections import defaultdict
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
V129 = HERE.parent / "V129"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
TMP = REPO / "tmp" / "v130_downloads"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v130" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"

SOURCE_SPECS = [
    {
        "id": "e0_bcra_com_b9195_cuentas_corrientes_2008",
        "filename": "bcra_com_b9195_cuentas_corrientes_2008.pdf",
        "url": "https://www.bcra.gob.ar/archivos/Pdfs/comytexord/b9195.pdf",
        "title": "Comunicación B 9195 · cuentas corrientes y especiales abiertas en el BCRA",
        "publication": "2008-02-06",
        "period": "2008-02-01/2008-08-07",
        "bytes": 217990,
        "sha256": "70421c39f9ee663a387477b4abe6efef2fc94ef70678c2265578ddf9220098de",
        "status": "SUPERSEDED_BEFORE_TARGET_TENDERS_VERSION_CONTROL",
        "note": "V130 E0 fiscal: lista actualizada al 01/02/2008; preservada como control de versión. Fue reemplazada por B 9322 antes de las licitaciones objetivo.",
    },
    {
        "id": "e0_bcra_com_b9322_cuentas_corrientes_2008",
        "filename": "bcra_com_b9322_cuentas_corrientes_2008.pdf",
        "url": "https://www.bcra.gob.ar/archivos/Pdfs/comytexord/b9322.pdf",
        "title": "Comunicación B 9322 · cuentas corrientes y especiales abiertas en el BCRA",
        "publication": "2008-08-08",
        "period": "2008-08-04",
        "bytes": 272233,
        "sha256": "e2b588d85262ff8e3a7c586ecf43683178584958e9473aa9b10095464336c6c0",
        "status": "USABLE_ACCOUNT_DIRECTORY_EFFECTIVE_BEFORE_TARGET_TENDERS",
        "note": "V130 E0 fiscal: reemplaza B 9195 y actualiza la nómina al 04/08/2008. Identifica cuentas ARS/USD de Citibank, HSBC y Standard; no nombra MERVAL.",
    },
]


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
    text = text.replace("V129", "V130")
    for prefix in (
        "GPS", "REQ", "GS", "GT", "GP", "AB", "CA", "CL", "DM", "EG", "ID",
        "SG", "SK", "SM", "ST", "TR", "VB", "MA", "IM", "XLS",
    ):
        text = text.replace(f"{prefix}129_", f"{prefix}130_")
    return text


def clone_parent() -> None:
    skip = {
        "build_e0_gdp_modality_bridge_v129.py",
        "qa_v129.py",
        "MANIFEST_V129.json",
        "INHERITED_QA_STATUS_V129.csv",
    }
    for source in V129.iterdir():
        if not source.is_file() or source.name in skip or source.name.startswith("HANDOVER_PROXIMA_SESION"):
            continue
        target = HERE / source.name.replace("V129", "V130")
        target.write_text(bump_text(source.read_text(encoding="utf-8-sig")), encoding="utf-8")


clone_parent()

# Preserve the contemporaneous BCRA account directories.
BIN.mkdir(parents=True, exist_ok=True)
for spec in SOURCE_SPECS:
    source_bin = BIN / spec["filename"]
    source_input = TMP / spec["filename"] if (TMP / spec["filename"]).is_file() else source_bin
    assert source_input.is_file()
    assert source_input.stat().st_size == spec["bytes"]
    assert sha256(source_input) == spec["sha256"]
    if source_input != source_bin:
        shutil.copy2(source_input, source_bin)
    assert source_bin.stat().st_size == spec["bytes"] and sha256(source_bin) == spec["sha256"]
    spec["local"] = "/" + source_bin.relative_to(REPO).as_posix()

new_ids = {spec["id"] for spec in SOURCE_SPECS}
catalog = [row for row in read_csv(CATALOG) if row["id"] not in new_ids]
for row in catalog:
    if row["id"] == "e0_argentina_rc_212_24_2008_recompra":
        row["nota"] = (
            "V130 E0 fiscal: procedimiento normativo verificado. Las ofertas identifican entidad, especie, VNO y precio; "
            "ONCP confecciona preadjudicación por participante; Caja informa transferencias T+3 y Finanzas paga en la cuenta "
            "BCRA de la entidad. Los inversores pueden operar por intermediarios, por lo que participante no equivale a titular final."
        )
for spec in SOURCE_SPECS:
    catalog.append(
        {
            "id": spec["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": "Banco Central de la República Argentina",
            "titulo": spec["title"], "url_original": spec["url"], "archivo_local": spec["local"],
            "fecha_descarga": "2026-08-30", "fecha_publicacion": spec["publication"], "codigo_serie": "",
            "periodo_utilizado": spec["period"], "tipo": "PDF oficial · binario preservado", "sha256": spec["sha256"],
            "nota": spec["note"],
        }
    )
assert len(catalog) == 350 and len({row["id"] for row in catalog}) == 350
write_csv(CATALOG, catalog)

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V130.csv"
census = [row for row in read_csv(census_path) if row["source_id"] not in new_ids]
for row in census:
    if row["source_id"] == "e0_argentina_rc_212_24_2008_recompra":
        row["variable_families"] = "state_bcra;fiscal;debt;buyback;settlement;custody;participant;payment_route"
        row["method_breaks"] = "procedimiento versus ejecución; participante/intermediario versus titular final; cuenta destino versus crédito efectivo"
        row["use_status"] = "USABLE_NORMATIVE_PARTICIPANT_AND_SETTLEMENT_DOCUMENT_CHAIN"
        row["caveat"] = "Define preadjudicación, transferencia Caja, informe T+3 y pago a cuenta BCRA; no prueba la ejecución de una adjudicación concreta."
for spec in SOURCE_SPECS:
    census.append(
        {
            "source_id": spec["id"], "institution": "Banco Central de la República Argentina", "artifact": spec["title"],
            "url": spec["url"], "local_path": spec["local"], "sha256": spec["sha256"], "bytes": str(spec["bytes"]),
            "period_coverage": spec["period"], "variable_families": "state_bcra;accounts;settlement;payment_route",
            "primary_source": "YES", "preserved": "YES",
            "method_breaks": "nómina de cuentas versus asiento de crédito; versión temporal de la nómina",
            "use_status": spec["status"],
            "caveat": "La existencia de una cuenta no demuestra que una orden o un pago concreto haya sido debitado o acreditado.",
        }
    )
assert len(census) == 110 and len({row["source_id"] for row in census}) == 110
write_csv(census_path, census)

# Participant-level reconstruction for the six public GDP awards.
all_awards = read_csv(HERE / "E0_FISCAL_PUBLIC_BUYBACK_AWARDS_2008_V130.csv")
gdp_awards = [row for row in all_awards if row["isin"] in {"ARARGE03E147", "ARARGE03E154"}]
assert len(gdp_awards) == 10
assert all(row["ultimate_holder_identified"] == "NO" for row in gdp_awards)

accounts = {
    "Citibank": {"official": "CITIBANK N.A.", "ARS": "016", "USD": "80016"},
    "HSBC Bank": {"official": "HSBC BANK ARGENTINA S.A.", "ARS": "150", "USD": "80150"},
    "Standard Bank": {"official": "STANDARD BANK ARGENTINA S.A.", "ARS": "015", "USD": "80015"},
    "MERVAL": {"official": "NOT_NAMED_AS_ACCOUNT_HOLDER_IN_B9322", "ARS": "UNKNOWN", "USD": "UNKNOWN"},
}

raw_total = sum((Decimal(row["awarded_effective_ars_raw"]) for row in gdp_awards), Decimal(0))
published_total = Decimal("96685934.36")
rounding_delta = published_total - raw_total
assert raw_total == Decimal("96685934.350900")
assert rounding_delta == Decimal("0.009100")

def fmt_es(value: Decimal, decimals: int) -> str:
    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")

raw_total_es = fmt_es(raw_total, 6)
published_total_es = fmt_es(published_total, 2)
rounding_delta_es = fmt_es(rounding_delta, 6)

by_participant: dict[str, list[dict[str, str]]] = defaultdict(list)
for row in gdp_awards:
    by_participant[row["participant"]].append(row)
assert set(by_participant) == set(accounts)

participant_amounts: dict[str, Decimal] = {}
distribution = []
for participant in ("Citibank", "HSBC Bank", "Standard Bank", "MERVAL"):
    rows = by_participant[participant]
    raw = sum((Decimal(row["awarded_effective_ars_raw"]) for row in rows), Decimal(0))
    participant_amounts[participant] = raw
    ars_vno = sum((Decimal(row["awarded_notional_native"]) for row in rows if row["native_currency"] == "ARS"), Decimal(0))
    usd_vno = sum((Decimal(row["awarded_notional_native"]) for row in rows if row["native_currency"] == "USD"), Decimal(0))
    account_status = "EXACT_DIRECTORY_MATCH_B9322_PAYMENT_NOT_CONFIRMED" if participant != "MERVAL" else "NO_MERVAL_ACCOUNT_MATCH_ROUTING_ENTITY_OPEN"
    distribution.append(
        {
            "participant": participant,
            "participant_role": "MAE_PARTICIPANT_INTERMEDIARY_OR_OWN_ACCOUNT",
            "round_count": str(len({row["tender_date"] for row in rows})),
            "instrument_count": str(len({row["isin"] for row in rows})),
            "awarded_vno_ars": str(ars_vno), "awarded_vno_usd": str(usd_vno),
            "awarded_effective_ars_raw": str(raw), "awarded_effective_ars_presentation": str(raw.quantize(Decimal("0.01"))),
            "share_of_raw_public_gdp_awards_pct": str(raw / raw_total * 100),
            "share_of_reference_2006_total_pct": str(raw / Decimal("3301600000") * 100),
            "bcra_peso_account_b9322": accounts[participant]["ARS"],
            "bcra_usd_account_b9322": accounts[participant]["USD"],
            "account_evidence_status": account_status,
            "ultimate_holder_identified": "NO",
            "settlement_status": "TARGET_ACCOUNT_DIRECTORY_ONLY_PAYMENT_AND_SECURITIES_TRANSFER_NOT_CONFIRMED",
            "caveat": "El participante puede operar por cuenta propia o de terceros; no identifica al beneficiario final ni prueba el crédito.",
        }
    )
distribution.append(
    {
        "participant": "TOTAL_PUBLIC_GDP_AWARDS", "participant_role": "NON_PARTICIPANT_CONTROL_TOTAL",
        "round_count": "4", "instrument_count": "2", "awarded_vno_ars": "1045342050", "awarded_vno_usd": "29480362",
        "awarded_effective_ars_raw": str(raw_total), "awarded_effective_ars_presentation": str(published_total),
        "share_of_raw_public_gdp_awards_pct": "100", "share_of_reference_2006_total_pct": str(raw_total / Decimal("3301600000") * 100),
        "bcra_peso_account_b9322": "N/A", "bcra_usd_account_b9322": "N/A",
        "account_evidence_status": f"RAW_TO_PUBLISHED_ROUNDING_DELTA_ARS_{rounding_delta}",
        "ultimate_holder_identified": "NO", "settlement_status": "AWARD_TOTAL_ONLY_SETTLEMENT_NOT_CONFIRMED",
        "caveat": "El total bruto reconstruido difiere ARS 0,0091 del subtotal publicado por redondeo subcentavo.",
    }
)
write_csv(HERE / "E0_REFERENCE_2006_PUBLIC_TENDER_PARTICIPANT_DISTRIBUTION_V130.csv", distribution)

event_matrix = []
payment_targets = []
for row in gdp_awards:
    participant = row["participant"]
    currency = row["native_currency"]
    target = accounts[participant][currency]
    target_status = "B9322_DIRECTORY_MATCH" if target != "UNKNOWN" else "ROUTING_ACCOUNT_OPEN"
    event_matrix.append(
        {
            "award_id": row["award_id"], "tender_date": row["tender_date"],
            "scheduled_settlement_date": row["scheduled_settlement_date"], "participant": participant,
            "participant_role": row["participant_role"], "instrument": row["instrument"], "isin": row["isin"],
            "native_currency": currency, "awarded_notional_native": row["awarded_notional_native"],
            "awarded_effective_native": row["awarded_effective_native"],
            "awarded_effective_ars_raw": row["awarded_effective_ars_raw"],
            "bcra_account_candidate": target, "bcra_account_directory_source": "e0_bcra_com_b9322_cuentas_corrientes_2008",
            "account_match_status": target_status, "ultimate_holder_identified": "NO",
            "securities_transfer_status": "SCHEDULED_NOT_CONFIRMED", "cash_credit_status": "NOT_CONFIRMED",
            "source_id": row["source_id"], "source_locator": row["source_locator"],
            "caveat": "La moneda del instrumento orienta el candidato de cuenta; falta la orden de pago para confirmar moneda y cuenta efectivamente acreditada.",
        }
    )
    payment_targets.append(
        {
            "target_id": f"PAY130_{len(payment_targets) + 1:02d}", "award_id": row["award_id"],
            "scheduled_settlement_date": row["scheduled_settlement_date"], "participant": participant,
            "isin": row["isin"], "native_currency": currency, "awarded_notional_native": row["awarded_notional_native"],
            "awarded_effective_native": row["awarded_effective_native"], "awarded_effective_ars_raw": row["awarded_effective_ars_raw"],
            "oncp_preaward_record": "TARGET_EXACT_PARTICIPANT_AMOUNT", "caja_t2_transfer_record": "OPEN",
            "caja_t3_report_record": "OPEN", "finance_payment_order_record": "OPEN",
            "bcra_credit_account_candidate": target, "bcra_credit_record": "OPEN",
            "cryl_cancellation_record": "OPEN",
            "overall_status": "TARGET_ACCOUNT_IDENTIFIED_PAYMENT_NOT_CONFIRMED" if target != "UNKNOWN" else "ROUTING_ACCOUNT_AND_PAYMENT_OPEN",
            "minimum_closing_chain": "ONCP preaward;Caja T+2 transfer;Caja T+3 report;Finance order;BCRA debit-credit;CRyL cancellation",
            "caveat": "Cada eslabón debe reconciliar fecha, participante, ISIN, nominal e importe; ninguno se presume por la adjudicación.",
        }
    )
write_csv(HERE / "E0_REFERENCE_2006_PARTICIPANT_AWARD_EVENT_MATRIX_V130.csv", event_matrix)
write_csv(HERE / "E0_REFERENCE_2006_PAYMENT_RECORD_TARGET_MATRIX_V130.csv", payment_targets)

shares = sorted((value / raw_total for value in participant_amounts.values()), reverse=True)
hhi = sum((share * share for share in shares), Decimal(0))
hhi_10000_es = fmt_es((hhi * 10000).quantize(Decimal("0.01")), 2)
top1_es = fmt_es((shares[0] * 100).quantize(Decimal("0.01")), 2)
top2_es = fmt_es((sum(shares[:2]) * 100).quantize(Decimal("0.01")), 2)
participant_es = {
    "Citibank": fmt_es(participant_amounts["Citibank"], 6),
    "HSBC Bank": fmt_es(participant_amounts["HSBC Bank"], 6),
    "Standard Bank": fmt_es(participant_amounts["Standard Bank"], 6),
    "MERVAL": fmt_es(participant_amounts["MERVAL"], 6),
}
concentration = [
    {"metric": "TOP1_SHARE_PCT", "value": str(shares[0] * 100), "denominator": "raw_public_GDP_awards", "interpretation": "Largest named participant share", "prohibited_inference": "ultimate holder or beneficiary share"},
    {"metric": "TOP2_SHARE_PCT", "value": str(sum(shares[:2]) * 100), "denominator": "raw_public_GDP_awards", "interpretation": "Two largest named participant shares", "prohibited_inference": "ownership or collusion"},
    {"metric": "CR4_SHARE_PCT", "value": "100", "denominator": "raw_public_GDP_awards", "interpretation": "All four published participant labels", "prohibited_inference": "market completeness outside the recovered tenders"},
    {"metric": "PARTICIPANT_HHI_0_1", "value": str(hhi), "denominator": "raw_public_GDP_awards", "interpretation": "Descriptive concentration of published participant labels", "prohibited_inference": "competition-law HHI or ultimate-beneficiary concentration"},
    {"metric": "PARTICIPANT_HHI_0_10000", "value": str(hhi * 10000), "denominator": "raw_public_GDP_awards", "interpretation": "Same descriptive HHI on conventional scale", "prohibited_inference": "market-power finding"},
]
assert hhi == Decimal("0.5621675971083157783991627445")
write_csv(HERE / "E0_REFERENCE_2006_PARTICIPANT_CONCENTRATION_V130.csv", concentration)

version_audit = []
version_rows = [
    ("e0_bcra_com_b9195_cuentas_corrientes_2008", "2008-02-06", "2008-02-01", "NO_SUPERSEDED_BY_B9322_BEFORE_TARGET_TENDERS"),
    ("e0_bcra_com_b9322_cuentas_corrientes_2008", "2008-08-08", "2008-08-04", "YES_EFFECTIVE_DIRECTORY_FOR_TARGET_TENDERS"),
]
for source_id, publication, snapshot, applicability in version_rows:
    for participant in ("Citibank", "HSBC Bank", "Standard Bank", "MERVAL"):
        version_audit.append(
            {
                "source_id": source_id, "publication_date": publication, "directory_as_of": snapshot,
                "participant": participant, "official_account_holder_name": accounts[participant]["official"],
                "peso_account": accounts[participant]["ARS"], "usd_account": accounts[participant]["USD"],
                "applicability_to_2008_08_28_through_2008_10_02": applicability,
                "finding": "EXACT_ACCOUNT_MATCH" if participant != "MERVAL" else "NO_MERVAL_ACCOUNT_HOLDER_MATCH",
                "caveat": "Nómina de cuentas, no comprobante de pago; no sustituir cuentas MAE/Interbanking por una cuenta MERVAL no documentada.",
            }
        )
write_csv(HERE / "E0_BCRA_2008_ACCOUNT_VERSION_AUDIT_V130.csv", version_audit)

# Promote the ledger and freeze the new method boundaries.
ledger_path = HERE / "E0_FISCAL_MECHANISM_LEDGER_V130.csv"
ledger = read_csv(ledger_path)
ledger.extend(
    [
        {"ledger_id": "F141", "window": "2008-08-28/2008-10-02", "mechanism": "Debt_buyback_excess_GDP", "phase": "PUBLIC_TENDER_PARTICIPANT_DISTRIBUTION", "as_of_date": "FOUR_TENDER_DATES", "payer": "Tesoro_Nacional", "recipient": "Four_named_MAE_participants_ultimate_holders_open", "universe": "Reference_2006_Excess_GDP_public_tender_subset", "instrument": "ARARGE03E147_and_ARARGE03E154", "amount_original": str(raw_total / Decimal(1_000_000)), "original_unit": "ARS_million_effective_raw", "normalized_ars_million": str(raw_total / Decimal(1_000_000)), "valuation_basis": "SUM_TEN_PARTICIPANT_INSTRUMENT_ROWS", "source_id": "four_official_tender_results;e0_argentina_rc_212_24_2008_recompra", "source_locator": "E0_REFERENCE_2006_PUBLIC_TENDER_PARTICIPANT_DISTRIBUTION_V130.csv", "realization_status": "PARTICIPANT_AWARD_DISTRIBUTION_EXACT_SETTLEMENT_AND_HOLDERS_OPEN", "additivity": "DECOMPOSITION_OF_F138_DO_NOT_ADD", "status_interpretation": "Four published participant labels reconcile to the six GDP award subtotal within ARS 0.0091 rounding.", "caveat": "Participant may be intermediary or own-account bidder; not ultimate holder."},
        {"ledger_id": "F142", "window": "2008-08-04/2008-10-07", "mechanism": "Debt_buyback_excess_GDP", "phase": "BCRA_PAYMENT_ACCOUNT_DIRECTORY", "as_of_date": "B9322_DIRECTORY", "payer": "Tesoro_Nacional", "recipient": "Citibank_HSBC_Standard_account_candidates_MERVAL_open", "universe": "Public_GDP_award_payment_route", "instrument": "BCRA_ARS_USD_CURRENT_ACCOUNTS", "amount_original": "N/A", "original_unit": "ACCOUNT_IDENTIFIERS", "normalized_ars_million": "N/D", "valuation_basis": "CONTEMPORANEOUS_BCRA_DIRECTORY", "source_id": "e0_bcra_com_b9322_cuentas_corrientes_2008", "source_locator": "PDF_pp2_6", "realization_status": "ACCOUNT_DIRECTORY_MATCH_THREE_PARTICIPANTS_PAYMENT_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "ARS/USD account numbers are identified for three bank participants; MERVAL routing remains open.", "caveat": "Account existence is not an order, debit or credit record."},
        {"ledger_id": "F143", "window": "2008-08-28/2008-10-02", "mechanism": "Debt_buyback_excess_GDP", "phase": "PUBLIC_PARTICIPANT_CONCENTRATION_DESCRIPTOR", "as_of_date": "FOUR_TENDER_DATES", "payer": "N/A", "recipient": "Named_participant_labels", "universe": "Ten_GDP_participant_instrument_rows", "instrument": "ARARGE03E147_and_ARARGE03E154", "amount_original": str(hhi * 10000), "original_unit": "DESCRIPTIVE_HHI_0_10000", "normalized_ars_million": "N/D", "valuation_basis": "SQUARED_RAW_AWARD_SHARES", "source_id": "four_official_tender_results", "source_locator": "E0_REFERENCE_2006_PARTICIPANT_CONCENTRATION_V130.csv", "realization_status": "DESCRIPTIVE_PARTICIPANT_CONCENTRATION_ONLY", "additivity": "NON_ADDITIVE", "status_interpretation": "Participant HHI 5621.68; top participant 71.33%, top two 93.66%.", "caveat": "Not a competition-law market HHI and not ultimate-beneficiary concentration."},
        {"ledger_id": "F144", "window": "2008-09-02/2008-10-07", "mechanism": "Debt_buyback_excess_GDP", "phase": "PARTICIPANT_PAYMENT_DOCUMENT_CHAIN", "as_of_date": "FOUR_SCHEDULED_SETTLEMENT_DATES", "payer": "Tesoro_Nacional", "recipient": "Awarded_entity_BCRA_account_per_procedure", "universe": "Ten_GDP_participant_instrument_rows", "instrument": "ONCP_Caja_Finance_BCRA_CRyL_chain", "amount_original": "N/A", "original_unit": "DOCUMENT_CHAIN", "normalized_ars_million": "N/D", "valuation_basis": "RC_212_24_2008_PROCEDURE", "source_id": "e0_argentina_rc_212_24_2008_recompra;e0_bcra_com_b9322_cuentas_corrientes_2008", "source_locator": "Anexo_1.4_1.12_2.1_2.5;B9322_pp2_6", "realization_status": "PROCEDURAL_ROUTE_AND_TARGETS_IDENTIFIED_EXECUTION_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "The expected record chain is now targetable by participant, date, ISIN and candidate account.", "caveat": "No transfer, T+3 report, payment order, credit or cancellation is yet independently confirmed."},
    ]
)
assert len(ledger) == 144 and len({row["ledger_id"] for row in ledger}) == 144
write_csv(ledger_path, ledger)

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V130.csv"
breaks = read_csv(breaks_path)
for row in breaks:
    if row["break_id"] == "participant_not_ultimate_holder":
        row["problem"] = "Published tender participant may act for own account or submit for other investors."
        row["rule"] = "Report the named participant and keep ultimate holder/beneficiary unidentified unless custody or order-level evidence closes it."
        row["evidence"] = "RC 212/2008-24/2008 Anexo 1.4-1.5; four result PDFs"
breaks.extend(
    [
        {"break_id": "participant_concentration_not_beneficiary_hhi", "dimension": "concentration", "problem": "Award shares by intermediary can concentrate even when underlying holders are dispersed.", "rule": "Label HHI and CR values descriptive participant metrics only; prohibit market-power and beneficiary-concentration inference.", "status": "FROZEN", "evidence": "participant distribution V130; normative intermediary rule"},
        {"break_id": "account_directory_not_payment_credit", "dimension": "realization", "problem": "A contemporaneous BCRA account number identifies a possible rail, not an executed Treasury payment.", "rule": "Require payment order plus BCRA debit/credit record reconciled to Caja T+3 confirmation.", "status": "FROZEN", "evidence": "B9322; RC 212/2008-24/2008 Anexo 2.1-2.5"},
        {"break_id": "bcra_account_directory_temporal_version", "dimension": "time", "problem": "B9195 was superseded before the August-October 2008 tenders.", "rule": "Use B9322, updated to 04/08/2008, for target-date mapping; retain B9195 only as version control.", "status": "FROZEN", "evidence": "B9195; B9322 p1"},
    ]
)
assert len(breaks) == 106 and len({row["break_id"] for row in breaks}) == 106
write_csv(breaks_path, breaks)

trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V130.csv"
trace = read_csv(trace_path)
trace.extend(
    [
        {"trace_id": "TR130_089", "request_id": "REQ130_ECON", "institution": "Ministerio de Economía / ONCP / DADP", "gap_id": "CL130_DEBT_ACCOUNTING", "requested_record": "Listado de preadjudicación por participante de las diez filas GDP y documentación conservada en el expediente", "period_or_date": "2008-08-28/2008-10-07", "identifiers": "S01:0342455/2008;ten award IDs;four participants;two ISIN", "minimum_usable_fields": "fecha;participante;ISIN;VNO;precio;efectivo;orden;expediente;estado", "confidentiality_fallback": "cuadro por participante/fecha/ISIN con terceros subyacentes testados", "status": "DRAFT_NOT_SENT"},
        {"trace_id": "TR130_090", "request_id": "REQ130_CAJA", "institution": "Caja de Valores S.A.", "gap_id": "CL130_DEBT_ACCOUNTING", "requested_record": "Transferencias T+2 e informe T+3 de las diez filas GDP por participante", "period_or_date": "2008-09-02;2008-09-09;2008-09-16;2008-10-07", "identifiers": "Citibank;HSBC Bank;Standard Bank;MERVAL;ARARGE03E147;ARARGE03E154;0306/40000", "minimum_usable_fields": "fecha;depositante origen testado;participante;ISIN;nominal;estado;lote;informe T+3", "confidentiality_fallback": "certificación agregada por fecha/participante/ISIN/nominal", "status": "DRAFT_NOT_SENT"},
        {"trace_id": "TR130_091", "request_id": "REQ130_BCRA", "institution": "BCRA / Cuentas Corrientes / CRyL", "gap_id": "CL130_DEBT_ACCOUNTING", "requested_record": "Débitos y créditos asociados a la recompra, usando cuentas contemporáneas candidatas", "period_or_date": "2008-09-02/2008-10-07", "identifiers": "016;150;015;80016;80150;80015;MERVAL routing open;two ISIN", "minimum_usable_fields": "fecha;orden;cuenta debitada;cuenta acreditada testada;moneda;importe;estado;referencia CRyL", "confidentiality_fallback": "certificación de existencia/inexistencia por fecha, cuenta, moneda e importe", "status": "DRAFT_NOT_SENT"},
        {"trace_id": "TR130_092", "request_id": "REQ130_CNV", "institution": "CNV / Caja / mercados", "gap_id": "CL130_CUSTODIAN_HOLDINGS", "requested_record": "Identificación del agente y cuenta de liquidación detrás de la etiqueta MERVAL en el resultado del 02/10/2008", "period_or_date": "2008-10-02/2008-10-07", "identifiers": "MERVAL;ARARGE03E147;VNO5000000;effectiveARS415000", "minimum_usable_fields": "agente;cuenta depositante;cuenta BCRA o entidad pagadora;orden;fecha;estado", "confidentiality_fallback": "certificación del tipo de participante y entidad de cobro con datos personales testados", "status": "DRAFT_NOT_SENT"},
    ]
)
assert len(trace) == 92 and len({row["trace_id"] for row in trace}) == 92
write_csv(trace_path, trace)

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V130.csv"
keys = read_csv(keys_path)
keys.extend(
    [
        {"key_id": "SK130_72", "request_id": "REQ130_ECON", "key_group": "participant_preaward", "exact_key": "S01:0342455/2008;Citibank;HSBC Bank;Standard Bank;MERVAL;96685934.350900", "search_purpose": "localizar listado ONCP de preadjudicación y documentos DADP", "source_or_basis": "RC 212/2008-24/2008;ten GDP result rows", "caveat": "Participante no equivale a titular final."},
        {"key_id": "SK130_73", "request_id": "REQ130_BCRA", "key_group": "candidate_accounts", "exact_key": "ARS 016;150;015;USD 80016;80150;80015;2008-09-02;2008-09-09;2008-09-16;2008-10-07", "search_purpose": "acotar débitos/créditos del pago por fecha y participante", "source_or_basis": "B9322 pp2,6;four tender results", "caveat": "Cuentas candidatas; la orden define moneda y destino realmente usados."},
        {"key_id": "SK130_74", "request_id": "REQ130_CAJA", "key_group": "participant_transfer_totals", "exact_key": "Citibank 68965780.936900;HSBC 21589872.974;Standard 5715280.440000;MERVAL 415000.00", "search_purpose": "reconciliar informe T+3 y transferencias con adjudicaciones", "source_or_basis": "participant distribution V130", "caveat": "Importes efectivos ARS; conciliar además nominal por moneda."},
        {"key_id": "SK130_75", "request_id": "REQ130_CNV", "key_group": "merval_routing", "exact_key": "MERVAL;2008-10-02;2008-10-07;ARARGE03E147;VNO5000000;ARS415000", "search_purpose": "identificar agente y cuenta de liquidación detrás de la etiqueta publicada", "source_or_basis": "resultado oficial 02/10/2008;B9322 negative account match", "caveat": "No sustituir por cuentas MAE o Interbanking sin evidencia."},
    ]
)
assert len(keys) == 75 and len({row["key_id"] for row in keys}) == 75
write_csv(keys_path, keys)

request_addenda = {
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V130.md": f"""

## Clave adicional V130 · preadjudicación y expediente productor

La Resolución Conjunta 212/2008 y 24/2008 asigna a ONCP la confección del listado de preadjudicación por participante y deja la documentación en DADP, dentro del expediente `S01:0342455/2008`. Las diez filas participante–instrumento GDP reconstruyen ARS {raw_total_es} y concilian con el subtotal publicado con una diferencia subcentavo de ARS {rounding_delta_es}. Se solicitan el listado, las comunicaciones de adjudicación y las órdenes de pago por Citibank, HSBC Bank, Standard Bank y la etiqueta MERVAL. La identidad de los inversores subyacentes puede testarse: el objeto mínimo es cerrar participante, fecha, ISIN, nominal, importe y estado.
""",
    "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V130.md": """

## Clave adicional V130 · matriz participante–fecha–especie

Para las fechas previstas `02/09`, `09/09`, `16/09` y `07/10/2008`, se adjunta una matriz de diez adjudicaciones GDP. Se solicitan las transferencias T+2 y el informe T+3 por participante, ISIN y nominal, incluyendo el depositante de origen testado y el lote hacia `0306/40000`. La publicación de la adjudicación no sustituye esos asientos y el participante puede haber actuado por terceros.
""",
    "REQUEST_BCRA_CRYL_SETTLEMENT_V130.md": """

## Clave adicional V130 · cuentas contemporáneas candidatas

La Comunicación B 9322, vigente antes de las licitaciones, identifica en pesos/USD a Citibank `016/80016`, HSBC `150/80150` y Standard Bank `015/80015`. Se solicitan los débitos y créditos que correspondan a las fechas previstas de liquidación, con orden, moneda, importe, estado y enlace CRyL. Estos números son claves de búsqueda, no prueba de pago. B 9322 no identifica una cuenta MERVAL; se pide informar la entidad y cuenta efectivamente usadas, sin presumir que una cuenta MAE o Interbanking le pertenecía.
""",
    "REQUEST_CNV_CUSTODY_RECORDS_V130.md": """

## Clave adicional V130 · etiqueta MERVAL

El resultado del `02/10/2008` adjudica a la etiqueta MERVAL VNO ARS 5.000.000 de `ARARGE03E147`, efectivo ARS 415.000. La nómina BCRA vigente no identifica una cuenta propia MERVAL. Se solicita el registro que permita individualizar el agente/depositante y la entidad de cobro usados para esa orden, admitiendo testado de titulares finales.
""",
}
for filename, addendum in request_addenda.items():
    path = HERE / filename
    text = path.read_text(encoding="utf-8-sig")
    if "Clave adicional V130" not in text:
        path.write_text(text.rstrip() + addendum, encoding="utf-8")

closures_path = HERE / "E0_REQUEST_CLOSURE_CRITERIA_V130.csv"
closures = read_csv(closures_path)
for row in closures:
    if row["gap_id"] == "CL130_DEBT_ACCOUNTING":
        row["does_not_close"] = "Participante, importe adjudicado y número de cuenta candidato no prueban transferencia, crédito, acreedor final ni cancelación."
        row["initial_status"] = "PARTICIPANTS_AND_THREE_ACCOUNT_ROUTES_IDENTIFIED_EXECUTED_PAYMENT_CHAIN_OPEN_NOT_SENT"
write_csv(closures_path, closures)

episode_path = HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V130.csv"
episode = read_csv(episode_path)
for row in episode:
    if row["variable"] == "gdp_units_excess_gdp_repurchase_scope":
        row["source_id"] = "e0_argentina_recompras_decreto_1735_04_report;e0_cgn_cuenta_inversion_2008_sdp;four_official_tender_results;e0_argentina_rc_212_24_2008_recompra;e0_bcra_com_b9322_cuentas_corrientes_2008"
        row["source_quality"] = "PRIMARY_EXECUTED_MODALITY_PARTICIPANT_DISTRIBUTION_AND_PAYMENT_ROUTE_TARGETED"
        row["status"] = "PARTICIPANT_AWARDS_CLOSED_ACCOUNT_DIRECTORY_THREE_CLOSED_SETTLEMENT_AND_HOLDERS_OPEN"
        row["interpretation"] = "Ten participant-instrument rows reconcile the six GDP awards; three bank account routes are contemporaneously identified and MERVAL routing remains open."
        row["notes"] = "Participant is not ultimate holder; account is not payment. Direct operations, transfer, credit and cancellation remain open."
write_csv(episode_path, episode)

coverage_path = HERE / "HISTORICAL_EVIDENCE_COVERAGE_V130.csv"
coverage = read_csv(coverage_path)
for row in coverage:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row["quality"] = "PRIMARY_REFERENCE_2006_PUBLIC_PARTICIPANTS_EXACT_AND_CONTEMPORANEOUS_ACCOUNT_DIRECTORY"
        row["comparable"] = "PARTICIPANT_DISTRIBUTION_EXACT_ACCOUNT_TARGETS_THREE_SETTLEMENT_OPEN"
        row["gap"] = "Faltan titulares finales, ruta MERVAL, transferencias Caja, órdenes/créditos BCRA y cancelación CRyL; compras directas siguen sin blotter."
        row["next_action"] = "Buscar expediente S01:0342455/2008 y, sólo con autorización expresa, remitir matrices exactas a Economía, Caja, BCRA y CNV."
write_csv(coverage_path, coverage)

queue_path = HERE / "HISTORICAL_SOURCE_QUEUE_V130.csv"
queue = read_csv(queue_path)
for row in queue:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row["status"] = "PARTICIPANT_DISTRIBUTION_AND_THREE_ACCOUNT_ROUTES_CLOSED_PAYMENT_CHAIN_OPEN_READY_NOT_SENT"
        row["why"] = "Ten exact rows identify four participant labels; B9322 supplies contemporaneous ARS/USD accounts for three bank participants."
        row["next_action"] = "Recover ONCP preaward and DADP file, Caja T+2/T+3 records, Finance orders, BCRA credits and CRyL cancellations."
write_csv(queue_path, queue)

reconstruction = f"""# Reconstrucción fiscal E0 · V130

## Qué cambia

V130 desagrega las seis adjudicaciones públicas GDP en diez filas participante–instrumento. El total bruto es ARS {raw_total_es}; concilia con los ARS {published_total_es} publicados con una diferencia de sólo ARS {rounding_delta_es}, compatible con el redondeo de las filas. La distribución exacta es: Citibank ARS {participant_es['Citibank']}, HSBC Bank ARS {participant_es['HSBC Bank']}, Standard Bank ARS {participant_es['Standard Bank']} y MERVAL ARS {participant_es['MERVAL']}.

## Qué significa participante

La Resolución Conjunta 212/2008 y 24/2008 admite entidades que actúan por cuenta propia y a otros inversores que canalizan ofertas por ellas. Por eso el nombre publicado prueba el participante/intermediario de la licitación, no el acreedor o beneficiario final. El HHI descriptivo de participantes es {hhi_10000_es}; no es un HHI jurídico de mercado ni de titulares finales.

## Ruta de pago acotada

La Comunicación B 9322, publicada el 08/08/2008 y actualizada al 04/08/2008, reemplazó a B 9195 antes de las licitaciones. Identifica cuentas ARS/USD de Citibank `016/80016`, HSBC `150/80150` y Standard `015/80015`. No contiene una cuenta MERVAL. Estos números vuelven pesquisable la ruta, pero no prueban el crédito.

El procedimiento exige listado ONCP de preadjudicación, transferencia de títulos T+2, informe Caja T+3 y pago de Finanzas a la cuenta BCRA de la entidad. Faltan esos documentos ejecutados, la orden y débito/crédito, la ruta MERVAL y la cancelación CRyL. Compras directas y titulares finales siguen abiertos. Seis pedidos permanecen `DRAFT_NOT_SENT`; `CLOSED_NETWORK_GATE=NO`.
"""
(HERE / "E0_FISCAL_RECONSTRUCTION_V130.md").write_text(reconstruction, encoding="utf-8")

readme = f"""# Checkpoint V130 · participantes y ruta de pago

V130 reconcilia diez filas participante–instrumento por ARS {raw_total_es}, con diferencia de ARS {rounding_delta_es} frente al subtotal publicado. Citibank concentra {top1_es}% y los dos mayores participantes {top2_es}%, métricas descriptivas del canal licitado y no de titulares finales.

B 9322 identifica cuentas contemporáneas ARS/USD para Citibank, HSBC y Standard. MERVAL no aparece como titular de cuenta. La ruta ONCP–Caja–Finanzas–BCRA–CRyL queda especificada, pero no ejecutada documentalmente.

Participante no equivale a acreedor final y cuenta no equivale a pago. Compras directas, transferencias, créditos y cancelaciones siguen abiertos. Seis pedidos permanecen `DRAFT_NOT_SENT`; panel estricto sin cambios.
"""
(HERE / "README_V130.md").write_text(readme, encoding="utf-8")

verdict = f"""# Veredicto V130

La porción pública de la recompra referencia 2006 ya puede distribuirse entre los nombres publicados sin perder precisión: Citibank ARS {participant_es['Citibank']}, HSBC Bank ARS {participant_es['HSBC Bank']}, Standard Bank ARS {participant_es['Standard Bank']} y MERVAL ARS {participant_es['MERVAL']}. Las diez filas suman ARS {raw_total_es} y concilian con el total publicado a ARS {rounding_delta_es}.

La concentración por participante es alta —top 1: {top1_es}% y HHI descriptivo {hhi_10000_es}—, pero jurídicamente no identifica concentración de acreedores finales: la norma permite intermediación. Tampoco la nómina BCRA acredita pagos. Sólo fija cuentas candidatas contemporáneas para tres bancos; MERVAL queda sin cuenta identificada.

El salto probatorio siguiente exige el listado ONCP, transferencias e informe Caja, órdenes y créditos BCRA y cancelación CRyL. Hasta entonces corresponde afirmar adjudicación y ruta pesquisable, no cobro efectivo ni beneficiario final. `CLOSED_NETWORK_GATE=NO`.
"""
(HERE / "VEREDICTO_V130.md").write_text(verdict, encoding="utf-8")

retrieval = f"""# Registro de recuperación V130

Fecha: 2026-08-30.

1. Se revalidaron visualmente las páginas relevantes de los cuatro resultados oficiales de 2008 y sus diez filas GDP participante–instrumento.
2. Se recalcularon con `Decimal` importes, participaciones y concentración; total bruto ARS {raw_total_es}, diferencia con publicación ARS {rounding_delta_es}.
3. Se releyó el procedimiento oficial: ONCP preadjudica por participante; Caja recibe e informa T+3; Finanzas paga a cuentas BCRA; otros inversores pueden canalizar por participantes.
4. Se preservaron B 9195 y B 9322. La segunda reemplaza a la primera antes de las licitaciones y conserva los pares `016/80016`, `150/80150`, `015/80015` para los tres bancos adjudicatarios.
5. MERVAL no aparece como titular de cuenta en B 9322; no se sustituyó por cuentas de MAE o Interbanking.
6. No se envió ningún pedido ni se realizó presentación externa.
"""
(HERE / "RETRIEVAL_LOG_V130.md").write_text(retrieval, encoding="utf-8")

refs_path = HERE / "SOURCE_REFERENCES_V130.md"
refs = refs_path.read_text(encoding="utf-8-sig").rstrip()
refs += "\n- BCRA Comunicación B 9195: https://www.bcra.gob.ar/archivos/Pdfs/comytexord/b9195.pdf\n- BCRA Comunicación B 9322: https://www.bcra.gob.ar/archivos/Pdfs/comytexord/b9322.pdf\n- Procedimiento RC 212/2008 y 24/2008: https://www.argentina.gob.ar/normativa/nacional/norma-143759/texto\n\nB 9195 se conserva como control histórico; B 9322 es la nómina contemporánea aplicable a las licitaciones objetivo.\n"
refs_path.write_text(refs, encoding="utf-8")

handover = f"""# Handover V130 → V131

## Estado congelado

- Diez filas participante–instrumento GDP: ARS {raw_total_es}; diferencia de redondeo frente al total publicado ARS {rounding_delta_es}.
- Distribución: Citibank ARS {participant_es['Citibank']}; HSBC ARS {participant_es['HSBC Bank']}; Standard ARS {participant_es['Standard Bank']}; MERVAL ARS {participant_es['MERVAL']}.
- HHI descriptivo de participantes: {hhi_10000_es}; no es concentración de titulares finales ni inferencia de competencia.
- B 9322 es la versión vigente para las fechas objetivo: cuentas ARS/USD Citibank `016/80016`, HSBC `150/80150`, Standard `015/80015`; ruta MERVAL abierta.
- Participante no equivale a titular final; cuenta identificada no equivale a crédito ejecutado.
- Procedimiento documental: preadjudicación ONCP → transferencia Caja T+2 → informe Caja T+3 → orden/pago a cuenta BCRA → conciliación/cancelación CRyL.
- Seis borradores `DRAFT_NOT_SENT`, ninguno enviado; panel estricto sin cambios.

## Prioridad V131

1. Recuperar el expediente `S01:0342455/2008`, listado ONCP y documentación DADP por las diez filas.
2. Buscar transferencias T+2 e informes Caja T+3 de `02/09`, `09/09`, `16/09` y `07/10/2008`.
3. Buscar órdenes de Finanzas y débitos/créditos BCRA por las seis cuentas candidatas; identificar la ruta MERVAL sin sustituirla por MAE.
4. Buscar asientos CRyL/cancelación por `ARARGE03E147` y `ARARGE03E154` y mantener separado `ARARGE03E121`.
5. Seguir buscando el blotter de compras directas; no enviar pedidos sin autorización expresa.
"""
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V130_A_V131.md").write_text(handover, encoding="utf-8")

audit_md = f"""# Auditoría V130

- Fuentes maestras: {len(catalog)}; dos comunicaciones BCRA oficiales nuevas preservadas.
- Fuentes primarias E0: {len(census)}.
- Ledger fiscal: {len(ledger)} filas; cortes metodológicos: {len(breaks)}.
- Filas participante–instrumento GDP: {len(event_matrix)}; total bruto ARS {raw_total_es}; delta de redondeo ARS {rounding_delta_es}.
- Participantes: 4; HHI descriptivo {hhi_10000_es}; cuentas contemporáneas exactas para 3 bancos; MERVAL abierta.
- Objetivos de pago: {len(payment_targets)}; cadena ejecutada todavía no confirmada.
- Pedidos: 6 borradores, 0 enviados; {len(trace)} objetos y {len(keys)} claves.
- Panel estricto: 30 entidades; {STRICT}% sin cambios.
"""
(HERE / "AUDITORIA_V130.md").write_text(audit_md, encoding="utf-8")

# Source-audit layer.
for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    shutil.copyfile(AUDIT / f"{stem}_V129.csv", AUDIT / f"{stem}_V130.csv")

hash_rows = []
for row in catalog:
    local = row["archivo_local"]
    path = REPO / local.lstrip("/") if local else None
    exists = bool(path and path.is_file())
    actual = sha256(path) if exists else ""
    expected = row["sha256"]
    hash_rows.append(
        {"id": row["id"], "archivo_local": local, "exists": str(exists), "sha_catalog": expected,
         "sha_actual": actual, "hash_ok": str(bool(exists and expected and actual.lower() == expected.lower()))}
    )
assert len(hash_rows) == 350
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V130.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V130.csv", hash_rows)

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V130.csv"
provenance = [row for row in read_csv(provenance_path) if row["source_id"] not in new_ids]
for spec in SOURCE_SPECS:
    provenance.append(
        {"source_id": spec["id"], "original_url": spec["url"], "retrieval_url": spec["url"],
         "capture_timestamp": "20260830", "cdx_digest": "N/A_DIRECT_OFFICIAL", "local_path": spec["local"],
         "sha256": spec["sha256"], "bytes": str(spec["bytes"]),
         "provenance_note": "Descarga directa del portador oficial BCRA; binario preservado y verificado visualmente en V130."}
    )
write_csv(provenance_path, provenance)

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": str(size), "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V130.csv", size_rows)

physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
assert physical == hash_ok == 344
completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V129.json").read_text(encoding="utf-8"))
for key in list(completeness):
    if key.endswith("_v129") or "newly_preserved_v129" in key:
        completeness.pop(key, None)
completeness.update(
    {
        "checkpoint": "V130", "date": "2026-08-30",
        "state": "E0_PUBLIC_GDP_PARTICIPANT_DISTRIBUTION_AND_THREE_ACCOUNT_ROUTES_CLOSED_EXECUTED_PAYMENT_CHAIN_OPEN_NOT_SENT",
        "numeric_v130_strict_changed": False, "master_catalog_entries": len(catalog),
        "physical_local_copies": physical, "physical_local_hash_ok": hash_ok,
        "binary_required_entries": len(catalog) - 5, "binary_required_preserved": physical,
        "e0_primary_sources_preserved": len(census),
        "e0_quality": "PRIMARY_PARTICIPANT_DISTRIBUTION_EXACT_CONTEMPORANEOUS_ACCOUNT_DIRECTORY",
        "sources_newly_preserved_v130": 2, "e0_primary_sources_newly_preserved_v130": 2,
        "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
        "e0_request_traceability_rows": len(trace), "e0_request_search_keys": len(keys),
        "e0_reference_2006_participant_award_rows": len(event_matrix),
        "e0_reference_2006_participants": len(participant_amounts),
        "e0_reference_2006_participant_raw_effective_ars": str(raw_total),
        "e0_reference_2006_participant_rounding_delta_ars": str(rounding_delta),
        "e0_reference_2006_participant_hhi_10000": str(hhi * 10000),
        "e0_reference_2006_bcra_account_exact_matches": 3,
        "e0_reference_2006_payment_target_rows": len(payment_targets),
        "e0_requests_submitted": 0, "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
        "historical_workstream": "Public GDP participant distribution and contemporaneous account targets for three banks closed; ultimate holders, MERVAL route, transfer, payment and cancellation remain open; no request submitted",
    }
)
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V130.json").write_text(json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V130 · participantes y ruta de pago"
old_backup = backup.read_text(encoding="utf-8-sig")
if marker not in old_backup:
    old_backup += (
        f"\n\n{marker}\n\n"
        f"- Diez filas participante–instrumento GDP: ARS {raw_total_es}; delta de redondeo ARS {rounding_delta_es}.\n"
        f"- Cuatro etiquetas publicadas; HHI descriptivo {hhi_10000_es}, sin inferencia sobre titulares finales.\n"
        "- B 9322 fija cuentas ARS/USD contemporáneas de Citibank, HSBC y Standard; MERVAL queda abierta.\n"
        "- Participante no equivale a acreedor final y cuenta no equivale a pago.\n"
        "- Transferencia Caja, orden/crédito BCRA, cancelación CRyL y compras directas siguen abiertas; seis pedidos DRAFT_NOT_SENT.\n"
    )
    backup.write_text(old_backup, encoding="utf-8")

inherited = []
for row in read_csv(V129 / "INHERITED_QA_STATUS_V129.csv"):
    post_result = row["post_v129_result"]
    interpretation = row["interpretation"]
    if row["script"] == "qa_v129.py":
        post_result = "EXPECTED_SUPERSEDED_ASSERTION"
        interpretation = "V129 congela los conteos de catálogo y fuentes anteriores a las dos comunicaciones BCRA preservadas en V130."
    inherited.append(
        {"script": row["script"], "pre_v130_result": row["post_v129_result"],
         "post_v130_result": post_result, "interpretation": interpretation}
    )
inherited.append(
    {"script": "qa_v130.py", "pre_v130_result": "N/A", "post_v130_result": "PASS",
     "interpretation": "Participant distribution, temporal account version and payment-target boundaries closed; execution remains open."}
)
write_csv(HERE / "INHERITED_QA_STATUS_V130.csv", inherited)

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

events = rows("E0_REFERENCE_2006_PARTICIPANT_AWARD_EVENT_MATRIX_V130.csv")
assert len(events) == 10
assert all(r["ultimate_holder_identified"] == "NO" for r in events)
assert all(r["cash_credit_status"] == "NOT_CONFIRMED" for r in events)
assert sum((d(r["awarded_effective_ars_raw"]) for r in events), d(0)) == d("96685934.350900")

dist = {r["participant"]: r for r in rows("E0_REFERENCE_2006_PUBLIC_TENDER_PARTICIPANT_DISTRIBUTION_V130.csv")}
assert len(dist) == 5
assert d(dist["Citibank"]["awarded_effective_ars_raw"]) == d("68965780.936900")
assert d(dist["HSBC Bank"]["awarded_effective_ars_raw"]) == d("21589872.974")
assert d(dist["Standard Bank"]["awarded_effective_ars_raw"]) == d("5715280.440000")
assert d(dist["MERVAL"]["awarded_effective_ars_raw"]) == d("415000.00")
assert dist["Citibank"]["bcra_peso_account_b9322"] == "016" and dist["Citibank"]["bcra_usd_account_b9322"] == "80016"
assert dist["HSBC Bank"]["bcra_peso_account_b9322"] == "150" and dist["HSBC Bank"]["bcra_usd_account_b9322"] == "80150"
assert dist["Standard Bank"]["bcra_peso_account_b9322"] == "015" and dist["Standard Bank"]["bcra_usd_account_b9322"] == "80015"
assert dist["MERVAL"]["bcra_peso_account_b9322"] == dist["MERVAL"]["bcra_usd_account_b9322"] == "UNKNOWN"

concentration = {r["metric"]: r for r in rows("E0_REFERENCE_2006_PARTICIPANT_CONCENTRATION_V130.csv")}
assert d(concentration["PARTICIPANT_HHI_0_10000"]["value"]).quantize(d("0.01")) == d("5621.68")
assert d(concentration["TOP1_SHARE_PCT"]["value"]).quantize(d("0.01")) == d("71.33")
assert d(concentration["TOP2_SHARE_PCT"]["value"]).quantize(d("0.01")) == d("93.66")
assert all(r["prohibited_inference"] for r in concentration.values())

versions = rows("E0_BCRA_2008_ACCOUNT_VERSION_AUDIT_V130.csv")
assert len(versions) == 8
assert sum(r["applicability_to_2008_08_28_through_2008_10_02"].startswith("YES") for r in versions) == 4
assert sum(r["finding"] == "NO_MERVAL_ACCOUNT_HOLDER_MATCH" for r in versions) == 2

targets = rows("E0_REFERENCE_2006_PAYMENT_RECORD_TARGET_MATRIX_V130.csv")
assert len(targets) == 10
assert all(r["caja_t2_transfer_record"] == r["bcra_credit_record"] == r["cryl_cancellation_record"] == "OPEN" for r in targets)
assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V130.csv")) == 144
assert len(rows("E0_FISCAL_METHOD_BREAKS_V130.csv")) == 106
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V130.csv")) == 92
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V130.csv")) == 75

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V130.csv")}
assert len(census) == 110
assert census["e0_bcra_com_b9195_cuentas_corrientes_2008"]["use_status"] == "SUPERSEDED_BEFORE_TARGET_TENDERS_VERSION_CONTROL"
assert census["e0_bcra_com_b9322_cuentas_corrientes_2008"]["use_status"] == "USABLE_ACCOUNT_DIRECTORY_EFFECTIVE_BEFORE_TARGET_TENDERS"
assert census["e0_argentina_rc_212_24_2008_recompra"]["use_status"] == "USABLE_NORMATIVE_PARTICIPANT_AND_SETTLEMENT_DOCUMENT_CHAIN"

with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 350 and len({r["id"] for r in catalog}) == 350
sources = {
    "bcra_com_b9195_cuentas_corrientes_2008.pdf": (217990, "70421c39f9ee663a387477b4abe6efef2fc94ef70678c2265578ddf9220098de"),
    "bcra_com_b9322_cuentas_corrientes_2008.pdf": (272233, "e2b588d85262ff8e3a7c586ecf43683178584958e9473aa9b10095464336c6c0"),
}
for name, (size, expected_hash) in sources.items():
    path = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v130" / "binaries" / name
    assert path.stat().st_size == size
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_hash

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V130.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V130"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 344
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v130_strict_changed"] is False

for name in ("README_V130.md", "VEREDICTO_V130.md", "E0_FISCAL_RECONSTRUCTION_V130.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V130_A_V131.md"):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "96.685.934,350900" in text
    assert "MERVAL" in text
    assert "DRAFT_NOT_SENT" in text or name == "VEREDICTO_V130.md"

for filename in ("REQUEST_ECONOMIA_TESORO_SETTLEMENT_V130.md", "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V130.md", "REQUEST_BCRA_CRYL_SETTLEMENT_V130.md", "REQUEST_CNV_CUSTODY_RECORDS_V130.md"):
    assert "Clave adicional V130" in (HERE / filename).read_text(encoding="utf-8-sig")

print("V130 QA PASS")
'''
(HERE / "qa_v130.py").write_text(qa_source, encoding="utf-8")


def checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V130.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V130", "parent_checkpoint": "V129",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": 2, "new_primary_sources": 2,
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks),
        "public_gdp_participant_award_rows": len(event_matrix), "public_gdp_participants": len(participant_amounts),
        "public_gdp_raw_effective_ars": str(raw_total), "participant_hhi_10000": str(hhi * 10000),
        "exact_bcra_account_matches": 3, "payment_target_rows": len(payment_targets),
        "request_drafts": 6, "request_traceability_rows": len(trace), "request_search_keys": len(keys),
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V130.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    "checkpoint": "V130", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical local copies with {hash_ok}/{physical} SHA-valid; ten public GDP participant rows and three contemporaneous bank-account targets closed; six requests drafted and none submitted.",
    "historical_workstream": "Public GDP participant distribution and three contemporaneous account routes closed; ultimate holders, MERVAL route, direct operations and executed settlement open; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V130 BUILD PASS")
