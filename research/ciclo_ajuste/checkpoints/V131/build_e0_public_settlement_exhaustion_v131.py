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
V130 = HERE.parent / "V130"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
TMP = REPO / "tmp" / "v131_downloads"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v131" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"

SOURCE = {
    "id": "e0_agn_informe_segundo_trimestre_2009_act_48_0237_09",
    "filename": "agn_2009_191_avance_2t_2009.pdf",
    "url": "https://www.agn.gob.ar/sites/default/files/informes/2009_191info_0.pdf",
    "title": "Informe del Segundo Trimestre de 2009 · proyecto 48 0237/09 Cuenta de Inversión 2008 - Deuda Pública",
    "publication": "2009",
    "period": "2009-06-30",
    "bytes": 1534297,
    "sha256": "a702a4a9b1252fae6f837ca1ac76cd1a3dd5d3a2f685deebb01c111db692e7e3",
}


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
    text = text.replace("V130", "V131")
    for prefix in (
        "GPS", "REQ", "GS", "GT", "GP", "AB", "CA", "CL", "DM", "EG", "ID",
        "SG", "SK", "SM", "ST", "TR", "VB", "MA", "IM", "XLS", "PAY",
    ):
        text = text.replace(f"{prefix}130_", f"{prefix}131_")
    return text


def clone_parent() -> None:
    skip = {
        "build_e0_participant_payment_route_v130.py",
        "qa_v130.py",
        "MANIFEST_V130.json",
        "INHERITED_QA_STATUS_V130.csv",
    }
    for source in V130.iterdir():
        if not source.is_file() or source.name in skip or source.name.startswith("HANDOVER_PROXIMA_SESION"):
            continue
        target = HERE / source.name.replace("V130", "V131")
        target.write_text(bump_text(source.read_text(encoding="utf-8-sig")), encoding="utf-8")


clone_parent()

# Preserve the new official AGN project locator.
BIN.mkdir(parents=True, exist_ok=True)
source_bin = BIN / SOURCE["filename"]
source_input = TMP / SOURCE["filename"] if (TMP / SOURCE["filename"]).is_file() else source_bin
assert source_input.is_file()
assert source_input.stat().st_size == SOURCE["bytes"]
assert sha256(source_input) == SOURCE["sha256"]
if source_input != source_bin:
    shutil.copy2(source_input, source_bin)
assert source_bin.stat().st_size == SOURCE["bytes"] and sha256(source_bin) == SOURCE["sha256"]
SOURCE["local"] = "/" + source_bin.relative_to(REPO).as_posix()

# Master catalog and E0 census.
catalog = [row for row in read_csv(CATALOG) if row["id"] != SOURCE["id"]]
for row in catalog:
    if row["id"] == "e0_agn_res_202_2009_act_41_2009_deuda":
        row["nota"] = (
            "V131 E0 fiscal: informe final agregado de la deuda 2008. La página 9 publica aumentos USD 21.830m, "
            "disminuciones USD 20.200m y colocaciones netas USD 2.399m; la resta literal da USD 1.630m, brecha USD 769m. "
            "No contiene un registro por recompra, participante o liquidación."
        )
catalog.append(
    {
        "id": SOURCE["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": "Auditoría General de la Nación",
        "titulo": SOURCE["title"], "url_original": SOURCE["url"], "archivo_local": SOURCE["local"],
        "fecha_descarga": "2026-08-30", "fecha_publicacion": SOURCE["publication"], "codigo_serie": "48 0237/09",
        "periodo_utilizado": SOURCE["period"], "tipo": "PDF oficial · binario preservado", "sha256": SOURCE["sha256"],
        "nota": (
            "V131 E0 fiscal: página física 22/impresa 21 identifica el proyecto 48 0237/09, Cuenta de Inversión 2008 - "
            "Deuda Pública Moneda Extranjera y Pesos, con avance 27% al 30/06/2009. Es localizador de proyecto, no informe final ni liquidación."
        ),
    }
)
assert len(catalog) == 351 and len({row["id"] for row in catalog}) == 351
write_csv(CATALOG, catalog)

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V131.csv"
census = [row for row in read_csv(census_path) if row["source_id"] != SOURCE["id"]]
for row in census:
    if row["source_id"] == "e0_agn_res_202_2009_act_41_2009_deuda":
        row["variable_families"] = "state_bcra;fiscal;debt;holders;public_private_split;aggregate_flows;audit_scope"
        row["method_breaks"] = "agregado versus recompra; flujo publicado con tensión aritmética; actuación final versus código de proyecto"
        row["use_status"] = "USABLE_AGGREGATE_DEBT_CONTROL_NOT_SETTLEMENT_AUDIT"
        row["caveat"] = "No identifica la recompra por especie, participante, cuenta o liquidación; la filiación con 48 0237/09 no está explicitada en los dos PDF."
census.append(
    {
        "source_id": SOURCE["id"], "institution": "Auditoría General de la Nación", "artifact": SOURCE["title"],
        "url": SOURCE["url"], "local_path": SOURCE["local"], "sha256": SOURCE["sha256"], "bytes": str(SOURCE["bytes"]),
        "period_coverage": SOURCE["period"], "variable_families": "fiscal;debt;audit_project;archival_locator",
        "primary_source": "YES", "preserved": "YES", "method_breaks": "avance de proyecto versus informe final; código de proyecto versus actuación",
        "use_status": "USABLE_PROJECT_LOCATOR_PROGRESS_ONLY",
        "caveat": "Prueba título, código y avance 27% al 30/06/2009; no prueba conclusión, hallazgo, papel de trabajo ni ejecución de recompras.",
    }
)
assert len(census) == 111 and len({row["source_id"] for row in census}) == 111
write_csv(census_path, census)

# AGN project/final-report bridge, deliberately stopping short of an undocumented identity assertion.
agn_bridge = [
    {
        "bridge_id": "AB131_01", "record_role": "PROJECT_TRACKER", "source_id": SOURCE["id"],
        "identifier": "48 0237/09", "title_or_scope": "CUENTA DE INVERSIÓN 2008 - DEUDA PÚBLICA MONEDA EXTRANJERA Y PESOS - 2008",
        "date_or_cutoff": "2009-06-30", "published_fact": "27% de avance", "locator": "PDF_physical_22_printed_21",
        "link_status": "EXACT_PROJECT_LOCATOR", "permitted_use": "Pedir actuación, expediente, informe final y papeles de trabajo por clave exacta.",
        "prohibited_use": "Afirmar que la AGN auditó o confirmó una liquidación bancaria concreta.",
    },
    {
        "bridge_id": "AB131_02", "record_role": "FINAL_REPORT_CANDIDATE", "source_id": "e0_agn_res_202_2009_act_41_2009_deuda",
        "identifier": "Resolución 202/2009; Actuación 41/2009", "title_or_scope": "Informe de Estudio Especial de la Deuda Pública · Cuenta de Inversión 2008",
        "date_or_cutoff": "2008-12-31", "published_fact": "Evalúa evolución, composición, vencimientos, costo y capacidad de pago.", "locator": "PDF_pp1_3_9_36",
        "link_status": "SAME_PERIOD_AND_SUBJECT_PROBABLE_LINEAGE_NOT_EXPLICITLY_CROSSWALKED",
        "permitted_use": "Usarlo como control agregado y pedir a AGN la equivalencia documental con 48 0237/09.",
        "prohibited_use": "Tratar coincidencia temática como prueba de identidad entre códigos.",
    },
    {
        "bridge_id": "AB131_03", "record_role": "OFFICIAL_BINARY_REVALIDATION", "source_id": "e0_agn_res_202_2009_act_41_2009_deuda",
        "identifier": "2009_202info_0.pdf", "title_or_scope": "Copia oficial actual versus copia preservada V112",
        "date_or_cutoff": "2026-08-30", "published_fact": "SHA-256 idéntico 14053bc9c6c51382b28fe7a854c926ac776701e43534b5ad6438a903165332f8; 418450 bytes",
        "locator": "official_URL_and_local_hash", "link_status": "BYTE_IDENTICAL_OFFICIAL_REVALIDATION",
        "permitted_use": "Confirmar autenticidad e integridad de la copia preservada.", "prohibited_use": "Extender el alcance sustantivo del informe.",
    },
    {
        "bridge_id": "AB131_04", "record_role": "TERM_SCOPE", "source_id": "e0_agn_res_202_2009_act_41_2009_deuda",
        "identifier": "full_text_36_pages", "title_or_scope": "recompra; programa de recompras; licitación; Caja de Valores; CRyL; Citibank; HSBC; Standard",
        "date_or_cutoff": "2008", "published_fact": "0 páginas con términos objetivo; Banco Nación sólo aparece en contexto agregado/capitalización.",
        "locator": "full_text_term_audit", "link_status": "NEGATIVE_SCOPE_CONTROL_ONLY",
        "permitted_use": "Documentar que el informe público no cierra la cadena operativa buscada.",
        "prohibited_use": "Afirmar que la AGN no recibió papeles de trabajo o que las recompras no ocurrieron.",
    },
    {
        "bridge_id": "AB131_05", "record_role": "AUDITEE_NOTICE", "source_id": "e0_agn_res_202_2009_act_41_2009_deuda",
        "identifier": "Nota 203/09 GCDP", "title_or_scope": "Puesta en conocimiento del Ministerio de Economía",
        "date_or_cutoff": "2009-06-29", "published_fact": "El organismo auditado no había remitido respuesta formal al vencer el plazo.",
        "locator": "PDF_p31", "link_status": "EXACT_REPORT_PROCESS_FACT",
        "permitted_use": "Pedir nota, constancia de remisión y eventual respuesta tardía.", "prohibited_use": "Inferir aceptación del informe o de una operación concreta.",
    },
]
write_csv(HERE / "E0_AGN_2008_DEBT_AUDIT_PROJECT_BRIDGE_V131.csv", agn_bridge)

# The AGN aggregate contains a literal arithmetic tension; freeze it instead of silently repairing it.
increases = Decimal("21830")
decreases = Decimal("20200")
literal_net = increases - decreases
published_net = Decimal("2399")
flow_gap = published_net - literal_net
assert literal_net == Decimal("1630") and flow_gap == Decimal("769")
agn_flow = [
    {"audit_id": "AF131_01", "source_id": "e0_agn_res_202_2009_act_41_2009_deuda", "locator": "PDF_p9", "item": "Aumentos de instrumentos", "published_value": "21830", "unit": "USD_million", "recomputed_value": "N/A", "residual": "N/A", "status": "PUBLISHED_COMPONENT", "rule": "No asignar automáticamente a colocaciones o recompras particulares."},
    {"audit_id": "AF131_02", "source_id": "e0_agn_res_202_2009_act_41_2009_deuda", "locator": "PDF_p9", "item": "Disminuciones de instrumentos", "published_value": "20200", "unit": "USD_million", "recomputed_value": "N/A", "residual": "N/A", "status": "PUBLISHED_COMPONENT", "rule": "No identificar la disminución agregada con las recompras 2008."},
    {"audit_id": "AF131_03", "source_id": "e0_agn_res_202_2009_act_41_2009_deuda", "locator": "PDF_p9", "item": "Neto literal aumentos menos disminuciones", "published_value": "N/A", "unit": "USD_million", "recomputed_value": str(literal_net), "residual": "N/A", "status": "RECOMPUTED_LITERAL", "rule": "Conservar la resta verificable sin corregir el original."},
    {"audit_id": "AF131_04", "source_id": "e0_agn_res_202_2009_act_41_2009_deuda", "locator": "PDF_pp9_11", "item": "Colocaciones netas publicadas", "published_value": str(published_net), "unit": "USD_million", "recomputed_value": str(literal_net), "residual": str(flow_gap), "status": "INTERNAL_ARITHMETIC_TENSION", "rule": "Pedir papel de trabajo; no elegir una cifra como corrección sin fuente."},
    {"audit_id": "AF131_05", "source_id": "e0_agn_res_202_2009_act_41_2009_deuda", "locator": "PDF_pp9_11", "item": "Brecha no explicada por la resta literal", "published_value": "N/A", "unit": "USD_million", "recomputed_value": str(flow_gap), "residual": str(flow_gap), "status": "UNEXPLAINED_IN_PUBLIC_REPORT", "rule": "Puede ser omisión, clasificación o errata; no es por sí sola hallazgo de irregularidad."},
    {"audit_id": "AF131_06", "source_id": "e0_agn_res_202_2009_act_41_2009_deuda", "locator": "PDF_pp9_11", "item": "Variación total anual de deuda", "published_value": "1246", "unit": "USD_million", "recomputed_value": "N/A", "residual": "N/A", "status": "AGGREGATE_WITH_VALUATION_COMPONENTS", "rule": "No usar para demostrar pago, beneficiario o cancelación de recompras."},
]
write_csv(HERE / "E0_AGN_2008_DEBT_FLOW_ARITHMETIC_AUDIT_V131.csv", agn_flow)

# Annual provider fees are exact accounting keys but not transaction-specific settlement evidence.
service_fees = [
    {"fee_id": "SF131_01", "provider": "Caja de Valores", "sigade": "83006000", "sidif": "VARIOS", "amount_ars": "183556.00", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "locator": "PDF_p67_Anexo_K", "scope": "ANNUAL_SERVICE_FEE", "buyback_specific": "NO", "use": "Exact SIGADE key for detail request."},
    {"fee_id": "SF131_02", "provider": "Caja de Valores", "sigade": "83008000", "sidif": "VARIOS", "amount_ars": "8245946.42", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "locator": "PDF_p67_Anexo_K", "scope": "ANNUAL_SERVICE_FEE", "buyback_specific": "NO", "use": "Exact SIGADE key for detail request."},
    {"fee_id": "SF131_03", "provider": "Caja de Valores", "sigade": "83095000", "sidif": "VARIOS", "amount_ars": "1786212.32", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "locator": "PDF_p67_Anexo_K", "scope": "ANNUAL_SERVICE_FEE", "buyback_specific": "NO", "use": "Exact SIGADE key for detail request."},
    {"fee_id": "SF131_04", "provider": "Citibank", "sigade": "83020000", "sidif": "VARIOS", "amount_ars": "122940.67", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "locator": "PDF_p67_Anexo_K", "scope": "ANNUAL_COMMISSION", "buyback_specific": "NO", "use": "Exact SIGADE key for detail request; participant name alone does not link it to the tenders."},
    {"fee_id": "SF131_05", "provider": "Banco Nación", "sigade": "83106000", "sidif": "71597-152677-2876", "amount_ars": "32270.30", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "locator": "PDF_p67_Anexo_K", "scope": "ANNUAL_COMMISSION", "buyback_specific": "NO", "use": "Exact SIGADE/SIDIF key for detail request; not proof of first-stage mandate payment."},
    {"fee_id": "SF131_06", "provider": "Caja de Valores total", "sigade": "83006000+83008000+83095000", "sidif": "VARIOS", "amount_ars": "10215714.74", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "locator": "PDF_p67_Anexo_K", "scope": "RECOMPUTED_ANNUAL_PROVIDER_TOTAL", "buyback_specific": "NO", "use": "Control sum only; never allocate to buybacks without subledger."},
    {"fee_id": "SF131_07", "provider": "Anexo K total", "sigade": "MULTIPLE", "sidif": "MULTIPLE", "amount_ars": "107159337.66", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "locator": "PDF_p67_Anexo_K", "scope": "PUBLISHED_ANNUAL_TABLE_TOTAL", "buyback_specific": "NO", "use": "Table control total only."},
]
assert sum(Decimal(row["amount_ars"]) for row in service_fees[:3]) == Decimal("10215714.74")
write_csv(HERE / "E0_ANNUAL_SERVICE_FEE_SCOPE_AUDIT_V131.csv", service_fees)

# Banco Nación's public annual report has only unrelated hits for the target terms.
bna_scope = [
    {"audit_id": "BN131_01", "term_or_key": "recompra", "hit_pages": "14", "public_context": "BCRA open-market repurchase of LEBAC-NOBAC", "target_relation": "UNRELATED_MONETARY_OPERATION", "status": "NEGATIVE_SCOPE_CONTROL_ONLY", "forbidden_inference": "BNA did not execute the Treasury mandate."},
    {"audit_id": "BN131_02", "term_or_key": "Caja de Valores", "hit_pages": "115", "public_context": "Accreditation of 2005 exchange Discount bonds and accrued interest", "target_relation": "UNRELATED_2005_EXCHANGE", "status": "NEGATIVE_SCOPE_CONTROL_ONLY", "forbidden_inference": "No 2008 settlement records exist internally."},
    {"audit_id": "BN131_03", "term_or_key": "Citibank", "hit_pages": "121", "public_context": "2001 JPY/USD swap and collateral", "target_relation": "UNRELATED_DERIVATIVE", "status": "NEGATIVE_SCOPE_CONTROL_ONLY", "forbidden_inference": "Citibank did not receive tender payments."},
    {"audit_id": "BN131_04", "term_or_key": "HSBC", "hit_pages": "147", "public_context": "Pledged certificates of deposit in New York attachment matter", "target_relation": "UNRELATED_COLLATERAL", "status": "NEGATIVE_SCOPE_CONTROL_ONLY", "forbidden_inference": "HSBC did not participate in the tenders."},
    {"audit_id": "BN131_05", "term_or_key": "Standard Bank; ARARGE03E147; ARARGE03E154; S01:0342455/2008", "hit_pages": "0", "public_context": "No full-text hit", "target_relation": "TARGET_NOT_DISCLOSED_IN_ANNUAL_REPORT", "status": "NEGATIVE_SCOPE_CONTROL_ONLY", "forbidden_inference": "The mandate, trades, payment or internal records did not exist."},
]
write_csv(HERE / "E0_BNA_2008_BUYBACK_PUBLIC_DISCLOSURE_SCOPE_AUDIT_V131.csv", bna_scope)

# Evidence ladder: public awards are exact; no executed settlement stage is closed.
targets_path = HERE / "E0_REFERENCE_2006_PAYMENT_RECORD_TARGET_MATRIX_V131.csv"
targets = read_csv(targets_path)
assert len(targets) == 10
for row in targets:
    row["oncp_preaward_record"] = "TARGET_IDENTIFIED_BODY_NOT_LOCATED_PUBLICLY"
write_csv(targets_path, targets)

ladder = []
for row in targets:
    account_known = row["bcra_credit_account_candidate"] != "UNKNOWN"
    ladder.append(
        {
            "target_id": row["target_id"], "award_id": row["award_id"], "scheduled_settlement_date": row["scheduled_settlement_date"],
            "participant": row["participant"], "isin": row["isin"], "published_award": "EXACT",
            "published_participant": "EXACT", "bcra_account_candidate": "EXACT_DIRECTORY_CANDIDATE" if account_known else "OPEN_MERVAL_ROUTING",
            "oncp_preaward_body": "NOT_LOCATED_IN_PUBLIC_ROUTES", "caja_t2_transfer": "OPEN", "caja_t3_report": "OPEN",
            "finance_payment_order": "OPEN", "bcra_credit": "OPEN", "cryl_cancellation": "OPEN", "ultimate_holder": "OPEN",
            "executed_settlement_status": "NOT_CONFIRMED", "caveat": "Public-route absence is not nonexistence; every executed stage needs its own record.",
        }
    )
write_csv(HERE / "E0_SETTLEMENT_EVIDENCE_LADDER_V131.csv", ladder)

ladder_summary = [
    {"stage": "PUBLISHED_AWARD", "closed_rows": "10", "total_rows": "10", "status": "CLOSED", "meaning": "Ten participant-instrument award rows are exact."},
    {"stage": "PUBLISHED_PARTICIPANT", "closed_rows": "10", "total_rows": "10", "status": "CLOSED", "meaning": "Named participant, not ultimate holder."},
    {"stage": "BCRA_ACCOUNT_CANDIDATE", "closed_rows": "9", "total_rows": "10", "status": "PARTIAL", "meaning": "Nine rows map to bank accounts; MERVAL routing open; candidate is not credit."},
    {"stage": "ONCP_PREADJUDICATION_BODY", "closed_rows": "0", "total_rows": "10", "status": "OPEN", "meaning": "Exact target exists; body not located publicly."},
    {"stage": "CAJA_T2_TRANSFER", "closed_rows": "0", "total_rows": "10", "status": "OPEN", "meaning": "No executed transfer record recovered."},
    {"stage": "CAJA_T3_REPORT", "closed_rows": "0", "total_rows": "10", "status": "OPEN", "meaning": "No post-settlement report recovered."},
    {"stage": "FINANCE_ORDER_BCRA_CREDIT", "closed_rows": "0", "total_rows": "10", "status": "OPEN", "meaning": "No order, debit or credit recovered."},
    {"stage": "CRYL_CANCELLATION", "closed_rows": "0", "total_rows": "10", "status": "OPEN", "meaning": "No target cancellation record recovered."},
    {"stage": "ULTIMATE_HOLDER", "closed_rows": "0", "total_rows": "10", "status": "OPEN", "meaning": "Participant may be intermediary."},
]
write_csv(HERE / "E0_SETTLEMENT_EVIDENCE_LADDER_SUMMARY_V131.csv", ladder_summary)

public_exhaustion = [
    {"route_id": "PE131_01", "institution_route": "Economía / ONCP / DADP", "exact_keys": "S01:0342455/2008;ten award IDs;two ISIN", "public_record_located": "Procedure and results only", "executed_record_located": "NO", "status": "EXPEDIENT_BODY_NOT_LOCATED_PUBLICLY", "usable_result": "Exact producer, expediente and requested fields fixed.", "still_needed": "Index, preaward list, orders and preserved file body.", "forbidden_inference": "The expediente or execution never existed."},
    {"route_id": "PE131_02", "institution_route": "Caja de Valores public communications", "exact_keys": "4857;4861;4873;4877-4903;02/09;09/09;16/09;07/10/2008", "public_record_located": "Three target announcements and continuous fourth-round window", "executed_record_located": "NO", "status": "CURRENT_PUBLIC_INDEX_EXHAUSTED_POST_SETTLEMENT_OPEN", "usable_result": "Current public view does not publish T+2/T+3 execution records.", "still_needed": "Transfer lots, T+3 reports and fourth-round internal correspondence.", "forbidden_inference": "The fourth round failed or no internal communication existed."},
    {"route_id": "PE131_03", "institution_route": "Economía public finance archive", "exact_keys": "2008-2009 buyback filenames;48 unique PDF digests", "public_record_located": "Calls and results", "executed_record_located": "NO", "status": "PUBLIC_CALL_RESULT_UNIVERSE_NO_POST_SETTLEMENT_FILE", "usable_result": "Public archive scope documented.", "still_needed": "Administrative and accounting records outside public PDF archive.", "forbidden_inference": "No payment occurred."},
    {"route_id": "PE131_04", "institution_route": "BCRA current-account directory", "exact_keys": "016;150;015;80016;80150;80015", "public_record_located": "Contemporaneous account candidates", "executed_record_located": "NO", "status": "ACCOUNT_RAIL_ONLY", "usable_result": "Nine award rows have target account candidates.", "still_needed": "Debit/credit entries and MERVAL routing.", "forbidden_inference": "Account existence proves payment."},
    {"route_id": "PE131_05", "institution_route": "BCRA CRyL public specifications", "exact_keys": "CGAEEEEE.NN;FT/FTC;ARARGE03E147;ARARGE03E154", "public_record_located": "Schemas and validation stages", "executed_record_located": "NO", "status": "RECORD_PATTERN_ONLY", "usable_result": "Exact lot/message types can be requested.", "still_needed": "Target CGA/response/matching/cancellation records.", "forbidden_inference": "A valid schema proves a target lot was submitted or settled."},
    {"route_id": "PE131_06", "institution_route": "CGN Cuenta de Inversión 2008", "exact_keys": "programa ARS1128m;SIGADE 83006000;83008000;83095000;83020000;83106000", "public_record_located": "Program aggregates and annual provider fees", "executed_record_located": "NO_OPERATION_LEVEL", "status": "AGGREGATE_ACCOUNTING_KEYS_ONLY", "usable_result": "Exact subledger keys identified.", "still_needed": "Fee/payment detail tied to expediente, ISIN, date and participant.", "forbidden_inference": "Annual Caja/Citibank/BNA fees are buyback consideration."},
    {"route_id": "PE131_07", "institution_route": "AGN project tracker and final public report", "exact_keys": "48 0237/09;Res.202/2009;Act.41/2009;Nota203/09GCDP", "public_record_located": "Project locator and aggregate final report candidate", "executed_record_located": "NO", "status": "AUDIT_SCOPE_AGGREGATE_SETTLEMENT_OPEN", "usable_result": "Precise archival keys and aggregate audit limits fixed.", "still_needed": "Identifier crosswalk, audit file, workpapers and source data.", "forbidden_inference": "Aggregate debt decreases identify the tenders or banks."},
    {"route_id": "PE131_08", "institution_route": "Banco Nación 2008 annual report", "exact_keys": "recompra;Caja;Citibank;HSBC;two ISIN;expediente", "public_record_located": "Only unrelated term contexts", "executed_record_located": "NO", "status": "ANNUAL_REPORT_NEGATIVE_SCOPE_CONTROL", "usable_result": "Public annual disclosure cannot substitute for the trade blotter.", "still_needed": "Board mandate, Treasury instructions, blotter and settlement records.", "forbidden_inference": "BNA did not execute the mandate."},
]
write_csv(HERE / "E0_PUBLIC_SETTLEMENT_RECORD_EXHAUSTION_V131.csv", public_exhaustion)

# Promote ledger with non-additive controls only.
ledger_path = HERE / "E0_FISCAL_MECHANISM_LEDGER_V131.csv"
ledger = read_csv(ledger_path)
ledger.extend(
    [
        {"ledger_id": "F145", "window": "2009-06-30/2009-11-23", "mechanism": "Debt_audit_2008", "phase": "AGN_PROJECT_TO_FINAL_REPORT_BRIDGE", "as_of_date": "2009", "payer": "N/A", "recipient": "N/A", "universe": "All_public_debt_2008", "instrument": "AGN_48_0237_09_Res202_Act41", "amount_original": "27", "original_unit": "PCT_PROJECT_PROGRESS", "normalized_ars_million": "N/D", "valuation_basis": "AGN_Q2_PROJECT_TRACKER", "source_id": f"{SOURCE['id']};e0_agn_res_202_2009_act_41_2009_deuda", "source_locator": "tracker_p22;final_report_pp1_36", "realization_status": "PROJECT_LOCATOR_AND_PROBABLE_FINAL_LINEAGE_CROSSWALK_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "Exact project code and same-subject final report are public; explicit identifier bridge is not.", "caveat": "Neither source is operation-level settlement evidence."},
        {"ledger_id": "F146", "window": "2008", "mechanism": "Debt_audit_2008", "phase": "AGN_AGGREGATE_FLOW_ARITHMETIC", "as_of_date": "2008-12-31", "payer": "N/A", "recipient": "N/A", "universe": "All_public_debt_2008", "instrument": "Aggregate_placements", "amount_original": str(flow_gap), "original_unit": "USD_million_unexplained_literal_gap", "normalized_ars_million": "N/D", "valuation_basis": "21830_MINUS_20200_VS_PUBLISHED_2399", "source_id": "e0_agn_res_202_2009_act_41_2009_deuda", "source_locator": "PDF_pp9_11", "realization_status": "PUBLIC_REPORT_INTERNAL_ARITHMETIC_TENSION", "additivity": "NON_ADDITIVE", "status_interpretation": "Literal components net to USD1630m, USD769m below the published USD2399m net.", "caveat": "Do not repair, accuse or allocate the gap without workpapers."},
        {"ledger_id": "F147", "window": "2008", "mechanism": "Debt_buyback_support_services", "phase": "ANNUAL_PROVIDER_FEE_ACCOUNT_KEYS", "as_of_date": "2008-12-31", "payer": "Tesoro_Nacional", "recipient": "Caja_Citibank_BNA_mixed_annual_services", "universe": "Anexo_K_other_budget_operations", "instrument": "SIGADE_SIDIF_service_rows", "amount_original": "10215714.74", "original_unit": "ARS_Caja_annual_recomputed", "normalized_ars_million": "10.21571474", "valuation_basis": "SUM_THREE_CAJA_ROWS", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "source_locator": "PDF_p67_Anexo_K", "realization_status": "ANNUAL_PROVIDER_FEES_EXACT_BUYBACK_ALLOCATION_OPEN", "additivity": "CONTROL_NOT_ADDITIVE", "status_interpretation": "Three Caja rows supply exact SIGADE keys and sum to ARS10.216m.", "caveat": "Not attributable to the buyback program without the subledger."},
        {"ledger_id": "F148", "window": "2008-09-02/2008-10-07", "mechanism": "Debt_buyback_excess_GDP", "phase": "EXECUTED_SETTLEMENT_EVIDENCE_LADDER", "as_of_date": "FOUR_SCHEDULED_SETTLEMENT_DATES", "payer": "Tesoro_Nacional", "recipient": "Named_participants_ultimate_holders_open", "universe": "Ten_GDP_participant_instrument_rows", "instrument": "ONCP_Caja_Finance_BCRA_CRyL_chain", "amount_original": "0/10", "original_unit": "EXECUTED_ROWS_CONFIRMED", "normalized_ars_million": "N/D", "valuation_basis": "PUBLIC_ROUTE_AUDIT", "source_id": "multiple_primary_sources", "source_locator": "E0_SETTLEMENT_EVIDENCE_LADDER_SUMMARY_V131.csv", "realization_status": "ZERO_EXECUTED_STAGES_CONFIRMED_NOT_ZERO_EXECUTION", "additivity": "NON_ADDITIVE", "status_interpretation": "Awards 10/10 and account candidates 9/10; ONCP body, Caja, payment and CRyL execution 0/10 confirmed.", "caveat": "Zero confirmed is an evidence status, not a zero realized amount."},
    ]
)
assert len(ledger) == 148 and len({row["ledger_id"] for row in ledger}) == 148
write_csv(ledger_path, ledger)

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V131.csv"
breaks = read_csv(breaks_path)
for row in breaks:
    if row["break_id"] == "current_public_archive_absence_not_historical_nonexistence":
        row["evidence"] = "Caja CA131_01/02; V131 public settlement exhaustion"
breaks.extend(
    [
        {"break_id": "agn_project_code_not_automatic_final_act_crosswalk", "dimension": "identity", "problem": "The Q2 tracker uses project 48 0237/09 while the same-subject final public report is catalogued as Resolution 202/2009, Actuación 41/2009.", "rule": "Call the lineage probable and request the official crosswalk, audit file and workpapers before asserting identity.", "status": "FROZEN", "evidence": "AGN 2009 second-quarter report p21; Res.202/2009 report"},
        {"break_id": "agn_aggregate_debt_decrease_not_buyback_settlement", "dimension": "aggregation", "problem": "AGN publishes all-debt increases and decreases, with an internal USD769m literal arithmetic tension, but no target transaction register.", "rule": "Keep the figures aggregate, freeze the discrepancy and never allocate decreases to buybacks or banks without workpapers.", "status": "FROZEN", "evidence": "AGN Res.202/2009 pp9,11"},
        {"break_id": "annual_service_fee_not_buyback_specific_consideration", "dimension": "scope", "problem": "CGN lists annual Caja service fees and bank commissions without operation, ISIN, date or expediente allocation.", "rule": "Use SIGADE/SIDIF as search keys only; require subledger reconciliation before attributing any amount to the buyback program.", "status": "FROZEN", "evidence": "CGN Cuenta de Inversión 2008 Anexo K p67"},
    ]
)
assert len(breaks) == 109 and len({row["break_id"] for row in breaks}) == 109
write_csv(breaks_path, breaks)

trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V131.csv"
trace = read_csv(trace_path)
trace.extend(
    [
        {"trace_id": "TR131_093", "request_id": "REQ131_AGN", "institution": "Auditoría General de la Nación", "gap_id": "CL131_AGN_REPLY", "requested_record": "Equivalencia documental, expediente, informe final y papeles de trabajo del proyecto 48 0237/09", "period_or_date": "2009", "identifiers": "48 0237/09;Resolución 202/2009;Actuación 41/2009;Nota 203/09 GCDP", "minimum_usable_fields": "código proyecto;actuación;resolución;índice;fuentes;papeles de trabajo;respuesta auditado", "confidentiality_fallback": "índice y cuadros agregados con terceros testados", "status": "DRAFT_NOT_SENT"},
        {"trace_id": "TR131_094", "request_id": "REQ131_ECON", "institution": "Ministerio de Economía / ONCP / DADP", "gap_id": "CL131_DEBT_ACCOUNTING", "requested_record": "Índice y cuerpo del expediente productor, incluido listado ONCP de preadjudicación", "period_or_date": "2008-08-27/2008-10-07", "identifiers": "S01:0342455/2008;ten awards;ARARGE03E147;ARARGE03E154", "minimum_usable_fields": "foja;fecha;tipo;participante;ISIN;VNO;precio;efectivo;estado", "confidentiality_fallback": "índice completo y cuadro por participante con titulares testados", "status": "DRAFT_NOT_SENT"},
        {"trace_id": "TR131_095", "request_id": "REQ131_ECON", "institution": "Ministerio de Economía / DADP / CGN", "gap_id": "CL131_DEBT_ACCOUNTING", "requested_record": "Submayor y comprobantes de servicios/comisiones por claves SIGADE/SIDIF 2008", "period_or_date": "2008", "identifiers": "83006000;83008000;83095000;83020000;83106000;71597-152677-2876", "minimum_usable_fields": "fecha;proveedor;concepto;expediente;SIDIF;SIGADE;importe;orden;programa", "confidentiality_fallback": "totales mensuales por clave y vínculo de expediente", "status": "DRAFT_NOT_SENT"},
        {"trace_id": "TR131_096", "request_id": "REQ131_BNA", "institution": "Banco de la Nación Argentina", "gap_id": "CL131_BNA_TRADE_BLOTTER", "requested_record": "Mandato, resolución de Directorio, instrucciones del Tesoro y blotter de la primera etapa 2008", "period_or_date": "2008-08-11/2008-08-22", "identifiers": "annual report negative-scope;ARARGE03E147;ARARGE03E154;programa ARS1374m", "minimum_usable_fields": "fecha;orden;especie;nominal;precio;efectivo;contraparte testada;liquidación", "confidentiality_fallback": "totales diarios por especie y copia testada del mandato", "status": "DRAFT_NOT_SENT"},
    ]
)
assert len(trace) == 96 and len({row["trace_id"] for row in trace}) == 96
write_csv(trace_path, trace)

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V131.csv"
keys = read_csv(keys_path)
keys.extend(
    [
        {"key_id": "SK131_76", "request_id": "REQ131_AGN", "key_group": "project_to_final_crosswalk", "exact_key": "48 0237/09;Resolución 202/2009;Actuación 41/2009;Nota 203/09 GCDP", "search_purpose": "vincular proyecto, actuación, informe final, vista y papeles de trabajo", "source_or_basis": "AGN Q2 2009 p21;AGN Res.202/2009 pp1,31", "caveat": "Coincidencia de período/tema no basta para afirmar identidad."},
        {"key_id": "SK131_77", "request_id": "REQ131_ECON", "key_group": "producer_file", "exact_key": "S01:0342455/2008;ONCP;DADP;preadjudicación por participante", "search_purpose": "localizar índice, cuerpo y listado productor", "source_or_basis": "RC 212/2008-24/2008", "caveat": "La resolución sólo prueba que el expediente existía al dictarse."},
        {"key_id": "SK131_78", "request_id": "REQ131_ECON", "key_group": "caja_fee_accounts", "exact_key": "SIGADE 83006000;83008000;83095000;ARS 183556.00;8245946.42;1786212.32", "search_purpose": "obtener submayor anual de Caja y vínculo con expedientes", "source_or_basis": "CGN 2008 Anexo K p67", "caveat": "Servicios anuales, no recompra específica."},
        {"key_id": "SK131_79", "request_id": "REQ131_ECON", "key_group": "bank_commission_accounts", "exact_key": "Citibank SIGADE83020000 ARS122940.67;Banco Nación SIGADE83106000 SIDIF71597-152677-2876 ARS32270.30", "search_purpose": "obtener comprobantes y concepto de comisiones", "source_or_basis": "CGN 2008 Anexo K p67", "caveat": "Coincidencia de entidad no prueba vínculo con licitaciones o mandato."},
        {"key_id": "SK131_80", "request_id": "REQ131_AGN", "key_group": "aggregate_flow_workpaper", "exact_key": "USD21830m aumentos;USD20200m disminuciones;USD2399m neto;brecha literal USD769m", "search_purpose": "pedir conciliación y papel de trabajo del flujo agregado", "source_or_basis": "AGN Res.202/2009 pp9,11", "caveat": "No asignar la brecha a recompra, error o irregularidad sin respaldo."},
    ]
)
assert len(keys) == 80 and len({row["key_id"] for row in keys}) == 80
write_csv(keys_path, keys)

# Add exact request branches. The markers are unique, avoiding the over-broad V130 heading test.
request_addenda = {
    "REQUEST_AGN_2018_REPLY_V131.md": """

## Clave V131 · proyecto 48 0237/09 y actuación final

Se solicita además la ficha, actuación, expediente, índice, informe final y papeles de trabajo del proyecto `48 0237/09`, titulado `CUENTA DE INVERSIÓN 2008 - DEUDA PÚBLICA MONEDA EXTRANJERA Y PESOS - 2008`, registrado con 27% de avance al 30/06/2009. Pido que se informe si corresponde total o parcialmente a la Resolución 202/2009, Actuación 41/2009, y se entregue la tabla de equivalencias entre ambos identificadores, junto con la Nota 203/09 GCDP del 29/06/2009, su constancia de remisión y cualquier respuesta posterior del auditado.

Para la página 9/11 del informe final, pido el papel de trabajo que concilia aumentos por USD 21.830 millones, disminuciones por USD 20.200 millones y colocaciones netas publicadas por USD 2.399 millones. La resta literal da USD 1.630 millones, con diferencia de USD 769 millones. No atribuyo la brecha a error o irregularidad: solicito componentes, fórmulas y reclasificaciones que la expliquen, y todo detalle disponible de las recompras 2008 por fecha, especie, participante, transferencia y liquidación.
""",
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V131.md": """

## Clave V131 · expediente productor y submayores SIGADE/SIDIF

La norma identifica el expediente `S01:0342455/2008`, a ONCP como productora del listado de preadjudicación por participante y a DADP como custodio documental. Se solicita el índice completo y el cuerpo del expediente, sin limitar la búsqueda a GDE, con relación por fecha, participante, ISIN, VNO, precio, efectivo y estado.

El Anexo K de la Cuenta de Inversión 2008 publica tres filas de servicios de Caja de Valores bajo SIGADE `83006000`, `83008000` y `83095000`; una comisión Citibank `83020000`; y una comisión Banco Nación `83106000`, SIDIF `71597-152677-2876`. Se solicitan submayores, órdenes, comprobantes, conceptos y expedientes de esas claves. Son llaves de búsqueda: no afirmo que esos importes anuales correspondan a las recompras.
""",
    "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V131.md": """

## Clave V131 · diez filas y ausencia del informe ejecutado en la vista pública

Se adjunta `E0_SETTLEMENT_EVIDENCE_LADDER_V131.csv`. Las diez adjudicaciones están publicadas, pero no se localizó en la vista pública ninguna transferencia T+2 ni informe T+3 ejecutado. Se solicitan por las fechas `02/09`, `09/09`, `16/09` y `07/10/2008`, participante, ISIN, nominal, lote, estado, origen testado y cuenta `0306/40000`. La ausencia pública no se interpreta como inexistencia interna ni como fracaso de la ronda.
""",
    "REQUEST_BCRA_CRYL_SETTLEMENT_V131.md": """

## Clave V131 · cero créditos confirmados no significa cero pagos

Nueve de diez filas poseen candidato de cuenta contemporáneo (`016/80016`, `150/80150`, `015/80015`); MERVAL permanece abierta. No se recuperó ningún débito, crédito ni cancelación individual. Se solicitan los registros por fecha, moneda, importe, orden y referencia CRyL. El estado `0/10 confirmado` describe evidencia pública recuperada, no un monto realizado igual a cero.
""",
    "REQUEST_CNV_CUSTODY_RECORDS_V131.md": """

## Clave V131 · ruta MERVAL preservada como incógnita

La matriz conserva una sola fila sin cuenta candidata: MERVAL, `02/10/2008`, liquidación prevista `07/10/2008`, `ARARGE03E147`, VNO ARS 5.000.000, efectivo ARS 415.000. Se solicita identificar agente, depositante y entidad de cobro con datos personales testados, sin sustituir la incógnita por una cuenta MAE/Interbanking no documentada.
""",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V131.md": """

## Clave V131 · la memoria anual no sustituye el mandato ni el blotter

La búsqueda integral en la Memoria y Balance BNA 2008 sólo localizó `recompra` en el contexto de LEBAC-NOBAC del BCRA; las menciones a Caja, Citibank y HSBC corresponden a operaciones distintas. Se solicita por ello el mandato del Tesoro, resolución de Directorio, instrucciones, registro diario de operaciones y liquidaciones de la etapa `11–22/08/2008`. Este control negativo de alcance no se presenta como prueba de que los registros internos no existan.
""",
}
for filename, addendum in request_addenda.items():
    path = HERE / filename
    marker = addendum.strip().splitlines()[0]
    text = path.read_text(encoding="utf-8-sig")
    if marker not in text:
        path.write_text(text.rstrip() + addendum, encoding="utf-8")

closures_path = HERE / "E0_REQUEST_CLOSURE_CRITERIA_V131.csv"
closures = read_csv(closures_path)
for row in closures:
    if row["gap_id"] == "CL131_DEBT_ACCOUNTING":
        row["does_not_close"] = "Informe AGN agregado, arancel anual, cuenta candidata o ausencia en vista pública no cierran transferencia, crédito ni cancelación."
        row["initial_status"] = "PUBLIC_ROUTES_EXHAUSTED_EXACT_ARCHIVAL_KEYS_READY_ZERO_EXECUTED_ROWS_CONFIRMED_NOT_SENT"
write_csv(closures_path, closures)

episode_path = HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V131.csv"
episode = read_csv(episode_path)
for row in episode:
    if row["variable"] == "gdp_units_excess_gdp_repurchase_scope":
        row["source_id"] += f";{SOURCE['id']};e0_agn_res_202_2009_act_41_2009_deuda;e0_cgn_cuenta_inversion_2008_sdp"
        row["source_quality"] = "PRIMARY_AWARDS_EXACT_PUBLIC_ROUTE_EXHAUSTION_AND_ARCHIVAL_KEYS"
        row["status"] = "AWARDS_CLOSED_ACCOUNTS_NINE_ROWS_PUBLIC_ROUTES_EXHAUSTED_EXECUTED_SETTLEMENT_ZERO_CONFIRMED"
        row["interpretation"] = "Public evidence closes ten awards and nine account candidates; no ONCP body, Caja transfer/report, BCRA credit or CRyL cancellation row is confirmed."
        row["notes"] = "AGN project and accounting keys sharpen requests; aggregate debt flows and annual fees are not transaction settlement evidence."
write_csv(episode_path, episode)

coverage_path = HERE / "HISTORICAL_EVIDENCE_COVERAGE_V131.csv"
coverage = read_csv(coverage_path)
for row in coverage:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row["quality"] = "PRIMARY_REFERENCE_2006_AWARDS_EXACT_PLUS_PUBLIC_ROUTE_EXHAUSTION"
        row["comparable"] = "TEN_AWARDS_NINE_ACCOUNT_CANDIDATES_ZERO_EXECUTED_ROWS_CONFIRMED"
        row["gap"] = "Faltan expediente/preaward ONCP, Caja T+2/T+3, órdenes/créditos, ruta MERVAL, CRyL, titulares finales y blotter directo."
        row["next_action"] = "Recuperar equivalencia AGN 48 0237/09↔Act.41/2009, expediente S01:0342455/2008 y submayores SIGADE/SIDIF; no enviar sin autorización."
write_csv(coverage_path, coverage)

queue_path = HERE / "HISTORICAL_SOURCE_QUEUE_V131.csv"
queue = read_csv(queue_path)
for row in queue:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row["status"] = "PUBLIC_ROUTES_EXHAUSTED_EXACT_ARCHIVAL_KEYS_READY_EXECUTED_CHAIN_OPEN_NOT_SENT"
        row["why"] = "AGN project/final identifiers and CGN SIGADE/SIDIF keys now make the missing files individually targetable."
        row["next_action"] = "Recover AGN workpapers/crosswalk, DADP expediente index, provider subledgers and settlement messages; preserve no-request gate."
write_csv(queue_path, queue)

reconstruction = """# Reconstrucción fiscal E0 · V131

## Qué cambia

V131 no suma un pago nuevo: demuestra con mayor precisión dónde termina la evidencia pública. Las diez adjudicaciones y sus participantes siguen exactos; nueve filas tienen cuenta BCRA candidata. Sin embargo, no se recuperó el cuerpo de preadjudicación ONCP, transferencia Caja T+2, informe T+3, orden/crédito BCRA ni cancelación CRyL para ninguna de las diez filas. `0/10 confirmado` es estado probatorio, no importe realizado igual a cero.

## Nueva ruta AGN

El Informe del Segundo Trimestre de 2009 identifica el proyecto `48 0237/09`, `CUENTA DE INVERSIÓN 2008 - DEUDA PÚBLICA MONEDA EXTRANJERA Y PESOS - 2008`, con avance 27% al 30/06/2009. El corpus ya preservaba la Resolución 202/2009, Actuación 41/2009, sobre el mismo período y tema. La filiación es probable, pero los PDF no contienen una tabla que vincule ambos códigos; por eso V131 solicita el crosswalk y los papeles de trabajo.

El informe final es agregado y no menciona recompra, licitación, Caja, CRyL ni los participantes objetivo. Además, su página 9 publica aumentos por USD 21.830 millones y disminuciones por USD 20.200 millones, que restan USD 1.630 millones, mientras el neto publicado es USD 2.399 millones: brecha USD 769 millones. Se congela la tensión sin corregirla ni atribuirla a una irregularidad.

## Nuevas claves contables

El Anexo K de la Cuenta de Inversión 2008 enumera tres filas anuales de Caja de Valores por ARS 10.215.714,74 en total, una comisión Citibank por ARS 122.940,67 y otra Banco Nación por ARS 32.270,30. Sus claves SIGADE/SIDIF sirven para pedir submayores y comprobantes. No prueban que esos importes correspondan al programa de recompras.

El archivo público queda agotado en su alcance actual, no en la existencia histórica de registros. Seis pedidos permanecen `DRAFT_NOT_SENT`; `CLOSED_NETWORK_GATE=NO`.
"""
(HERE / "E0_FISCAL_RECONSTRUCTION_V131.md").write_text(reconstruction, encoding="utf-8")

readme = """# V131 · agotamiento público y claves archivísticas

V131 preserva el localizador AGN `48 0237/09`, vincula con cautela el informe final agregado, detecta una tensión aritmética de USD 769m y extrae claves SIGADE/SIDIF de servicios anuales. La escalera queda en 10/10 adjudicaciones, 9/10 cuentas candidatas y 0/10 filas con liquidación ejecutada confirmada. Esto no equivale a cero pagos. Seis pedidos siguen `DRAFT_NOT_SENT`; panel estricto sin cambios.
"""
(HERE / "README_V131.md").write_text(readme, encoding="utf-8")

verdict = """# Veredicto V131

La investigación pública ya distingue tres capas sin mezclarlas: adjudicación publicada, ruta de pago pesquisable y ejecución comprobada. Las dos primeras están cerradas para 10/10 y 9/10 filas respectivamente; la tercera permanece en 0/10 confirmadas.

La AGN aporta el nuevo localizador exacto `48 0237/09` y un informe final agregado, no una auditoría de liquidación. La CGN aporta importes anuales y claves contables, no la asignación a estas operaciones. La Memoria BNA sólo arroja menciones ajenas al programa. Por eso no corresponde afirmar ni que los bancos cobraron esas diez filas ni que no cobraron: corresponde pedir los registros preexistentes con los identificadores ahora fijados.

`CLOSED_NETWORK_GATE=NO`; seis borradores `DRAFT_NOT_SENT`, ninguno enviado.
"""
(HERE / "VEREDICTO_V131.md").write_text(verdict, encoding="utf-8")

retrieval = """# Registro de recuperación V131

Fecha: 2026-08-30.

1. Se buscó el expediente exacto `S01:0342455/2008`; la web oficial devuelve la norma y resultados, no su cuerpo ni el listado ONCP.
2. Se agotó la vista pública de Caja alrededor de la cuarta ronda y se conservaron los límites ya documentados: no apareció un registro T+2/T+3 ejecutado.
3. Se preservó y verificó visualmente el Informe AGN del Segundo Trimestre de 2009; página física 22/impresa 21, proyecto `48 0237/09`, avance 27%.
4. La copia oficial actual del informe AGN 202/2009 es byte-idéntica a la preservada: SHA-256 `14053bc9c6c51382b28fe7a854c926ac776701e43534b5ad6438a903165332f8`.
5. Se auditaron visualmente la CGN 2008, la Memoria BNA 2008 y el informe AGN de custodios. Los aranceles anuales y los hits de la memoria se clasificaron sin extender su alcance.
6. La escalera probatoria conserva 0/10 liquidaciones confirmadas como estado de evidencia, nunca como monto cero.
7. No se envió ningún pedido ni se realizó presentación externa.
"""
(HERE / "RETRIEVAL_LOG_V131.md").write_text(retrieval, encoding="utf-8")

refs_path = HERE / "SOURCE_REFERENCES_V131.md"
refs = refs_path.read_text(encoding="utf-8-sig").rstrip()
refs += (
    "\n- AGN Informe del Segundo Trimestre de 2009: https://www.agn.gob.ar/sites/default/files/informes/2009_191info_0.pdf\n"
    "- AGN Resolución 202/2009 · Actuación 41/2009: https://www.agn.gob.ar/sites/default/files/informes/2009_202info_0.pdf\n"
    "- Resolución Conjunta 212/2008 y 24/2008: https://www.argentina.gob.ar/normativa/nacional/norma-143759/texto\n\n"
    "El primer PDF es un localizador de proyecto; el segundo es un informe agregado. Ninguno sustituye los registros de liquidación.\n"
)
refs_path.write_text(refs, encoding="utf-8")

handover = """# Handover V131 → V132

## Estado congelado

- Diez adjudicaciones participante–instrumento GDP exactas; nueve cuentas BCRA candidatas; ruta MERVAL abierta.
- `0/10` filas con preadjudicación ejecutada, transferencia Caja, informe T+3, crédito BCRA o cancelación CRyL confirmados. Es cobertura probatoria, no realización cero.
- Nuevo localizador AGN: proyecto `48 0237/09`, Cuenta de Inversión 2008 - Deuda Pública, 27% al 30/06/2009.
- Informe público candidato de cierre: Resolución 202/2009, Actuación 41/2009. Filiación probable por período/tema; crosswalk documental abierto.
- AGN p9/p11: aumentos USD 21.830m menos disminuciones USD 20.200m = USD 1.630m, frente a neto publicado USD 2.399m; brecha USD 769m congelada sin imputación.
- CGN Anexo K: Caja ARS 10.215.714,74 anual; Citibank ARS 122.940,67; BNA ARS 32.270,30. Son claves SIGADE/SIDIF, no pagos de recompra.
- Memoria BNA no divulga el mandato/blotter objetivo; control negativo de alcance, no inexistencia.
- Seis pedidos `DRAFT_NOT_SENT`, ninguno enviado; panel estricto sin cambios.

## Prioridad V132

1. Recuperar la tabla AGN que vincule `48 0237/09` con Resolución 202/2009 / Actuación 41/2009, y sus papeles de trabajo/fuentes.
2. Recuperar índice y cuerpo de `S01:0342455/2008`, en especial el listado ONCP por las diez filas.
3. Pedir submayores de SIGADE `83006000`, `83008000`, `83095000`, `83020000`, `83106000` y SIDIF `71597-152677-2876` sólo con autorización expresa.
4. Buscar lotes Caja T+2/T+3, órdenes/créditos BCRA y asientos CRyL por fecha/ISIN/participante.
5. Mantener separado el blotter BNA de compras directas y no inferir titulares finales.
"""
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V131_A_V132.md").write_text(handover, encoding="utf-8")

audit_md = f"""# Auditoría V131

- Fuentes maestras: {len(catalog)}; una fuente AGN oficial nueva preservada.
- Fuentes primarias E0: {len(census)}.
- Ledger fiscal: {len(ledger)} filas; cortes metodológicos: {len(breaks)}.
- AGN: proyecto exacto `48 0237/09`; informe final candidato revalidado; crosswalk abierto; tensión aritmética USD {flow_gap}m.
- Servicios anuales: tres filas Caja suman ARS 10.215.714,74; no asignadas a recompra.
- Escalera: 10 adjudicaciones; 9 cuentas candidatas; 0 filas con liquidación ejecutada confirmada.
- Pedidos: 6 borradores, 0 enviados; {len(trace)} objetos y {len(keys)} claves.
- Panel estricto: 30 entidades; {STRICT}% sin cambios.
"""
(HERE / "AUDITORIA_V131.md").write_text(audit_md, encoding="utf-8")

# Source-audit layer.
for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    shutil.copyfile(AUDIT / f"{stem}_V130.csv", AUDIT / f"{stem}_V131.csv")

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
assert len(hash_rows) == 351
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V131.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V131.csv", hash_rows)

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V131.csv"
provenance = [row for row in read_csv(provenance_path) if row["source_id"] != SOURCE["id"]]
provenance.append(
    {"source_id": SOURCE["id"], "original_url": SOURCE["url"], "retrieval_url": SOURCE["url"],
     "capture_timestamp": "20260830", "cdx_digest": "N/A_DIRECT_OFFICIAL", "local_path": SOURCE["local"],
     "sha256": SOURCE["sha256"], "bytes": str(SOURCE["bytes"]),
     "provenance_note": "Descarga directa del portador oficial AGN; binario preservado, hasheado y página objetivo verificada visualmente en V131."}
)
write_csv(provenance_path, provenance)

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or "tmp" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": str(size), "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V131.csv", size_rows)

physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
assert physical == hash_ok == 345
completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V130.json").read_text(encoding="utf-8"))
for key in list(completeness):
    if key.endswith("_v130") or "newly_preserved_v130" in key:
        completeness.pop(key, None)
completeness.update(
    {
        "checkpoint": "V131", "date": "2026-08-30",
        "state": "E0_PUBLIC_ROUTES_EXHAUSTED_EXACT_ARCHIVAL_KEYS_ZERO_EXECUTED_ROWS_CONFIRMED_NOT_SENT",
        "numeric_v131_strict_changed": False, "master_catalog_entries": len(catalog),
        "physical_local_copies": physical, "physical_local_hash_ok": hash_ok,
        "binary_required_entries": len(catalog) - 5, "binary_required_preserved": physical,
        "e0_primary_sources_preserved": len(census),
        "e0_quality": "PRIMARY_PUBLIC_ROUTE_EXHAUSTION_EXACT_ARCHIVAL_KEYS",
        "sources_newly_preserved_v131": 1, "e0_primary_sources_newly_preserved_v131": 1,
        "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
        "e0_request_traceability_rows": len(trace), "e0_request_search_keys": len(keys),
        "e0_agn_project_locator": "48 0237/09", "e0_agn_project_progress_pct": 27,
        "e0_agn_final_candidate": "RES202_2009_ACT41_2009_CROSSWALK_OPEN",
        "e0_agn_aggregate_arithmetic_gap_usd_million": str(flow_gap),
        "e0_settlement_award_rows_exact": 10, "e0_settlement_account_candidate_rows": 9,
        "e0_settlement_executed_rows_confirmed": 0,
        "e0_annual_caja_service_rows_ars": "10215714.74",
        "e0_requests_submitted": 0, "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
        "historical_workstream": "Public routes exhausted and exact archival/accounting keys fixed; execution and ultimate holders remain open; no request submitted",
    }
)
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V131.json").write_text(json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V131 · agotamiento público y claves archivísticas"
old_backup = backup.read_text(encoding="utf-8-sig")
if marker not in old_backup:
    old_backup += (
        f"\n\n{marker}\n\n"
        "- Localizador AGN `48 0237/09` preservado; informe final candidato Res.202/2009 Act.41/2009, crosswalk abierto.\n"
        "- Brecha aritmética agregada AGN USD 769m congelada sin imputación.\n"
        "- CGN Anexo K aporta claves SIGADE/SIDIF; importes anuales no asignados a recompra.\n"
        "- Escalera: 10 adjudicaciones, 9 cuentas candidatas, 0 liquidaciones ejecutadas confirmadas; no equivale a cero pagos.\n"
        "- Seis pedidos DRAFT_NOT_SENT; panel estricto sin cambios.\n"
    )
    backup.write_text(old_backup, encoding="utf-8")

inherited = []
for row in read_csv(V130 / "INHERITED_QA_STATUS_V130.csv"):
    post_result = row["post_v130_result"]
    interpretation = row["interpretation"]
    if row["script"] == "qa_v130.py":
        post_result = "EXPECTED_SUPERSEDED_ASSERTION"
        interpretation = "V130 congela conteos previos al nuevo localizador AGN y no contiene la escalera probatoria V131."
    inherited.append(
        {"script": row["script"], "pre_v131_result": row["post_v130_result"],
         "post_v131_result": post_result, "interpretation": interpretation}
    )
inherited.append(
    {"script": "qa_v131.py", "pre_v131_result": "N/A", "post_v131_result": "PASS",
     "interpretation": "Project locator, arithmetic boundary, fee scope and public settlement evidence ladder verified."}
)
write_csv(HERE / "INHERITED_QA_STATUS_V131.csv", inherited)

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

bridge = rows("E0_AGN_2008_DEBT_AUDIT_PROJECT_BRIDGE_V131.csv")
assert len(bridge) == 5
assert bridge[0]["identifier"] == "48 0237/09" and bridge[0]["published_fact"] == "27% de avance"
assert any(r["link_status"] == "SAME_PERIOD_AND_SUBJECT_PROBABLE_LINEAGE_NOT_EXPLICITLY_CROSSWALKED" for r in bridge)

flow = {r["audit_id"]: r for r in rows("E0_AGN_2008_DEBT_FLOW_ARITHMETIC_AUDIT_V131.csv")}
assert Decimal(flow["AF131_03"]["recomputed_value"]) == Decimal("1630")
assert Decimal(flow["AF131_04"]["published_value"]) == Decimal("2399")
assert Decimal(flow["AF131_05"]["residual"]) == Decimal("769")

fees = rows("E0_ANNUAL_SERVICE_FEE_SCOPE_AUDIT_V131.csv")
assert len(fees) == 7 and all(r["buyback_specific"] == "NO" for r in fees)
assert sum(Decimal(r["amount_ars"]) for r in fees[:3]) == Decimal("10215714.74")

bna = rows("E0_BNA_2008_BUYBACK_PUBLIC_DISCLOSURE_SCOPE_AUDIT_V131.csv")
assert len(bna) == 5 and all(r["status"] == "NEGATIVE_SCOPE_CONTROL_ONLY" for r in bna)

ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V131.csv")
assert len(ladder) == 10
assert sum(r["bcra_account_candidate"] == "EXACT_DIRECTORY_CANDIDATE" for r in ladder) == 9
assert all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)
summary = {r["stage"]: r for r in rows("E0_SETTLEMENT_EVIDENCE_LADDER_SUMMARY_V131.csv")}
assert summary["PUBLISHED_AWARD"]["closed_rows"] == "10"
assert summary["BCRA_ACCOUNT_CANDIDATE"]["closed_rows"] == "9"
for stage in ("ONCP_PREADJUDICATION_BODY", "CAJA_T2_TRANSFER", "CAJA_T3_REPORT", "FINANCE_ORDER_BCRA_CREDIT", "CRYL_CANCELLATION", "ULTIMATE_HOLDER"):
    assert summary[stage]["closed_rows"] == "0"

targets = rows("E0_REFERENCE_2006_PAYMENT_RECORD_TARGET_MATRIX_V131.csv")
assert len(targets) == 10
assert all(r["oncp_preaward_record"] == "TARGET_IDENTIFIED_BODY_NOT_LOCATED_PUBLICLY" for r in targets)
assert all(r["caja_t2_transfer_record"] == r["bcra_credit_record"] == r["cryl_cancellation_record"] == "OPEN" for r in targets)
assert len(rows("E0_PUBLIC_SETTLEMENT_RECORD_EXHAUSTION_V131.csv")) == 8
assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V131.csv")) == 148
assert len(rows("E0_FISCAL_METHOD_BREAKS_V131.csv")) == 109
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V131.csv")) == 96
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V131.csv")) == 80

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V131.csv")}
assert len(census) == 111
assert census["e0_agn_informe_segundo_trimestre_2009_act_48_0237_09"]["use_status"] == "USABLE_PROJECT_LOCATOR_PROGRESS_ONLY"
assert census["e0_agn_res_202_2009_act_41_2009_deuda"]["use_status"] == "USABLE_AGGREGATE_DEBT_CONTROL_NOT_SETTLEMENT_AUDIT"

with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 351 and len({r["id"] for r in catalog}) == 351
source = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v131" / "binaries" / "agn_2009_191_avance_2t_2009.pdf"
assert source.stat().st_size == 1534297
assert hashlib.sha256(source.read_bytes()).hexdigest() == "a702a4a9b1252fae6f837ca1ac76cd1a3dd5d3a2f685deebb01c111db692e7e3"

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V131.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V131"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 345
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v131_strict_changed"] is False

markers = {
    "REQUEST_AGN_2018_REPLY_V131.md": "## Clave V131 · proyecto 48 0237/09 y actuación final",
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V131.md": "## Clave V131 · expediente productor y submayores SIGADE/SIDIF",
    "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V131.md": "## Clave V131 · diez filas y ausencia del informe ejecutado en la vista pública",
    "REQUEST_BCRA_CRYL_SETTLEMENT_V131.md": "## Clave V131 · cero créditos confirmados no significa cero pagos",
    "REQUEST_CNV_CUSTODY_RECORDS_V131.md": "## Clave V131 · ruta MERVAL preservada como incógnita",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V131.md": "## Clave V131 · la memoria anual no sustituye el mandato ni el blotter",
}
for filename, marker in markers.items():
    text = (HERE / filename).read_text(encoding="utf-8-sig")
    assert marker in text and "BORRADOR_NO_ENVIADO" in text

for name in ("README_V131.md", "VEREDICTO_V131.md", "E0_FISCAL_RECONSTRUCTION_V131.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V131_A_V132.md"):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "0/10" in text and "48 0237/09" in text

print("V131 QA PASS")
'''
(HERE / "qa_v131.py").write_text(qa_source, encoding="utf-8")


def checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V131.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V131", "parent_checkpoint": "V130",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": 1, "new_primary_sources": 1,
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks),
        "agn_project_locator": "48 0237/09", "agn_final_candidate": "RES202_2009_ACT41_2009_CROSSWALK_OPEN",
        "agn_aggregate_arithmetic_gap_usd_million": str(flow_gap),
        "award_rows_exact": 10, "account_candidate_rows": 9, "executed_settlement_rows_confirmed": 0,
        "public_settlement_routes_audited": len(public_exhaustion), "annual_service_fee_rows": len(service_fees),
        "request_drafts": 6, "request_traceability_rows": len(trace), "request_search_keys": len(keys),
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V131.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


checkpoint_manifest()

def build_tree(root: Path) -> str:
    lines = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix().casefold()):
        if ".git" in path.parts or "__pycache__" in path.parts or "tmp" in path.parts:
            continue
        lines.append(path.relative_to(root).as_posix() + ("/" if path.is_dir() else ""))
    return "\n".join(lines) + "\n"

(REPO / "TREE.txt").write_text(build_tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(build_tree(CYCLE), encoding="utf-8")

global_manifest_path = CYCLE / "MANIFEST_SHA256.json"
global_files = []
for path in sorted(REPO.rglob("*"), key=lambda item: item.relative_to(REPO).as_posix().casefold()):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or "tmp" in path.parts or path == global_manifest_path:
        continue
    global_files.append({"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})
global_manifest = {
    "checkpoint": "V131", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical local copies with {hash_ok}/{physical} SHA-valid; AGN project locator and exact accounting keys added; zero of ten executed settlement rows confirmed; six requests drafted and none submitted.",
    "historical_workstream": "Public routes exhausted; AGN crosswalk, DADP file, provider subledgers and executed settlement remain open; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V131 BUILD PASS")
