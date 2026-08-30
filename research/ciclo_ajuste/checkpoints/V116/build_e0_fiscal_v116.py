from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, getcontext
from pathlib import Path
import csv
import hashlib
import json
import shutil


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
V115 = HERE.parent / "V115"
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v116" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"
getcontext().prec = 40


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


def v116_text(text: str) -> str:
    return text.replace("V115", "V116").replace("v115", "v116")


def money(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.01')):.2f}"


# Bootstrap every inherited checkpoint artifact, then overwrite the V116 deltas below.
for source in sorted(V115.iterdir()):
    if not source.is_file() or source.suffix.lower() not in {".csv", ".md"}:
        continue
    if source.name.startswith("HANDOVER_"):
        continue
    target = HERE / v116_text(source.name)
    target.write_text(v116_text(source.read_text(encoding="utf-8-sig")), encoding="utf-8-sig")


source_specs = [
    {
        "id": "e0_mecon_strip_boden2012_call_2009_06_10",
        "institution": "Ministerio de Economía y Finanzas Públicas · Secretaría de Finanzas",
        "title": "Llamado a licitación pública de recompra del cupón 15 de BODEN 2012 · 10 de junio de 2009",
        "url": "http://www.mecon.gov.ar/finanzas/sfinan/documentos/comunicado_de_prensa_boden2012.pdf",
        "file": "mecon_strip_boden2012_llamado_2009-06-10_wayback.pdf",
        "publication": "2009-06-10",
        "period": "2009-06-10/2009-06-18",
        "pages": "2",
        "families": "state_bcra;fiscal;debt;buyback;strip;tender;settlement_route",
        "breaks": "cupón efectivo versus VNO subyacente; ruta Caja/BCRA versus liquidación efectiva; captura archivada versus URL viva",
        "use": "USABLE_EXACT_PRIMARY_STRIP_CALL_AND_SETTLEMENT_ROUTE",
        "caveat": "Fija especie, cuenta Caja 0306/40000 y calendario T+2/T+3; no fija un máximo numérico ni confirma entrega o pago.",
        "verified": "Las dos páginas fueron renderizadas e inspeccionadas visualmente.",
    },
    {
        "id": "e0_mecon_strip_boden2012_result_2009_06_12",
        "institution": "Ministerio de Economía y Finanzas Públicas · Secretaría de Finanzas",
        "title": "Resultado y anexo de recompra del cupón 15 de BODEN 2012 · 12 de junio de 2009",
        "url": "http://www.mecon.gov.ar/finanzas/sfinan/documentos/comunicado_de_prensa_resultado_con%20anexo.pdf",
        "file": "mecon_strip_boden2012_resultado_2009-06-12_wayback.pdf",
        "publication": "2009-06-12",
        "period": "2009-06-12/2009-06-18",
        "pages": "3",
        "families": "state_bcra;fiscal;debt;buyback;strip;tender;participants;settlement_route",
        "breaks": "oferta versus adjudicación; cupón efectivo versus VNO subyacente; participante MAE versus tenedor final; resultado versus pago",
        "use": "USABLE_EXACT_PRIMARY_STRIP_RESULT_AND_ANNEX",
        "caveat": "El anexo identifica ofertas y participantes, no beneficiarios finales; la liquidación del 18/06 sigue prevista y no confirmada independientemente.",
        "verified": "Las tres páginas fueron renderizadas e inspeccionadas visualmente.",
    },
    {
        "id": "e0_bcra_inflation_report_q4_2008_buyback_control",
        "institution": "Banco Central de la República Argentina",
        "title": "Informe de Inflación · Cuarto trimestre de 2008 · control agregado de recompra",
        "url": "https://www.bcra.gob.ar/archivos/Pdfs/publicacionesestadisticas/informe-de-inflacion-trimestre-4-2008.pdf",
        "file": "bcra_informe_inflacion_4t_2008.pdf",
        "publication": "2008-10",
        "period": "2008-08/2008-10",
        "pages": "80",
        "families": "state_bcra;fiscal;debt;buyback;program_aggregate",
        "breaks": "monto cercano versus exacto; agregado de programa versus operaciones identificadas; fecha de informe versus cierre anual",
        "use": "USABLE_APPROXIMATE_INDEPENDENT_OFFICIAL_PROGRAM_CONTROL",
        "caveat": "Informa un monto cercano a USD 420m desde agosto; no identifica especies, contrapartes, cortes ni liquidaciones.",
        "verified": "Portada y página 51 del PDF fueron renderizadas e inspeccionadas visualmente.",
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
            "tipo": "PDF oficial · binario preservado",
            "sha256": spec["sha256"],
            "nota": f"V116 E0 fiscal: {spec['bytes']:,} bytes; {spec['pages']} páginas. {spec['verified']}",
        }
    )
write_csv(CATALOG, catalog)


census = [row for row in read_csv(V115 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V115.csv") if row["source_id"] not in new_ids]
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
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V116.csv", census)


raw_offers = [
    ("Citibank", "175000", "12.12"),
    ("Standard Bank", "2454200", "12.47"),
    ("Standard Bank", "2666000", "12.49"),
    ("BBVA Banco Francés", "40000", "12.59"),
    ("MERVAL", "76000", "12.60"),
    ("Nuevo Banco Bisel S.A.", "435000", "12.60"),
    ("MERVAL", "2532000", "12.64"),
    ("Banco de Galicia", "55000000", "12.65"),
    ("Citibank", "200000", "12.66"),
    ("Banco de Galicia", "55000000", "12.68"),
    ("Standard Bank", "20000", "12.70"),
    ("Banco Morgan", "1708800", "12.70"),
    ("MERVAL", "108900", "12.70"),
    ("Standard Bank", "5000000", "12.70"),
    ("Standard Bank", "5000000", "12.70"),
    ("Citibank", "42220000", "12.70"),
    ("Citibank", "431000", "12.70"),
    ("Citibank", "4680000", "12.70"),
    ("Citibank", "10000200", "12.70"),
    ("Citibank", "77960000", "12.70"),
    ("HSBC", "3000000", "12.74"),
    ("HSBC", "10000000", "12.75"),
    ("Santander Río", "10000", "12.75"),
    ("Banco Credicoop", "400000", "12.75"),
    ("Banco Mariva", "10000000", "12.79"),
    ("HSBC", "10000000", "12.79"),
    ("Banco Mariva", "10000000", "12.80"),
    ("Banco Mariva", "5000000", "12.84"),
    ("Banco Mariva", "5000000", "12.85"),
    ("Banco de la Pampa", "16787000", "12.85"),
    ("MERVAL", "1500000", "12.85"),
    ("MERVAL", "1500000", "12.86"),
    ("Banco Mariva", "5000000", "12.89"),
    ("Banco Mariva", "5000000", "12.90"),
    ("Citibank", "90000", "12.95"),
]
offers = []
for number, (participant, vno_text, price_text) in enumerate(raw_offers, 1):
    vno = Decimal(vno_text)
    price = Decimal(price_text)
    effective = vno * price / Decimal(100)
    offers.append(
        {
            "offer_number": str(number),
            "participant": participant,
            "underlying_boden2012_vno_usd": vno_text,
            "price_per_100_usd": price_text,
            "effective_coupon_value_usd": money(effective),
            "accepted": "YES" if number <= 20 else "NO",
            "cutoff_price_per_100_usd": "12.70",
            "settlement_scheduled": "2009-06-18",
            "source_id": "e0_mecon_strip_boden2012_result_2009_06_12",
            "source_locator": "PDF_annex_pp2_3",
            "ultimate_holder_identified": "NO",
            "settlement_confirmation": "SCHEDULED_NOT_INDEPENDENTLY_CONFIRMED",
            "caveat": "Participante MAE no equivale a tenedor final; adjudicación no prueba entrega Caja ni pago BCRA.",
        }
    )
write_csv(HERE / "E0_FISCAL_STRIP_BUYBACK_OFFERS_2009_V116.csv", offers)


received_vno = sum((Decimal(row[1]) for row in raw_offers), Decimal(0))
received_effective = sum((Decimal(row[1]) * Decimal(row[2]) / Decimal(100) for row in raw_offers), Decimal(0))
accepted_raw = raw_offers[:20]
accepted_vno = sum((Decimal(row[1]) for row in accepted_raw), Decimal(0))
accepted_effective = sum((Decimal(row[1]) * Decimal(row[2]) / Decimal(100) for row in accepted_raw), Decimal(0))
assert received_vno == Decimal("348994100")
assert received_effective == Decimal("44367798.74")
assert accepted_vno == Decimal("265707100")
assert accepted_effective == Decimal("33691889.24")


grouped: dict[str, dict[str, object]] = defaultdict(lambda: {"offers": 0, "vno": Decimal(0), "effective": Decimal(0), "components": []})
for participant, vno_text, price_text in accepted_raw:
    entry = grouped[participant]
    entry["offers"] = int(entry["offers"]) + 1
    entry["vno"] = Decimal(entry["vno"]) + Decimal(vno_text)
    entry["effective"] = Decimal(entry["effective"]) + Decimal(vno_text) * Decimal(price_text) / Decimal(100)
    entry["components"].append(f"{vno_text}@{price_text}")
awards = []
for participant, entry in grouped.items():
    awards.append(
        {
            "participant": participant,
            "accepted_offer_count": str(entry["offers"]),
            "underlying_boden2012_vno_usd": str(entry["vno"]),
            "effective_coupon_value_usd": money(Decimal(entry["effective"])),
            "accepted_components_vno_at_price": ";".join(entry["components"]),
            "participant_share_of_awarded_effective_pct": str((Decimal(entry["effective"]) / accepted_effective * Decimal(100)).quantize(Decimal("0.00000001"))),
            "source_id": "e0_mecon_strip_boden2012_result_2009_06_12",
            "source_locator": "PDF_annex_pp2_3",
            "ultimate_holder_identified": "NO",
            "settlement_confirmation": "SCHEDULED_NOT_INDEPENDENTLY_CONFIRMED",
            "caveat": "Agrupación derivada de ofertas aceptadas; participante MAE no equivale a beneficiario final.",
        }
    )
write_csv(HERE / "E0_FISCAL_STRIP_BUYBACK_AWARDS_2009_V116.csv", awards)


summary = [
    {
        "call_date": "2009-06-10",
        "tender_date": "2009-06-12",
        "titles_due_t_plus_2": "2009-06-17",
        "settlement_due_t_plus_3": "2009-06-18",
        "instrument": "BODEN_2012_COUPON_15",
        "isin": "ARARGE03G415",
        "coupon_payment_date": "2009-08-03",
        "coupon_per_underlying_vno_100_usd": "12.92",
        "coupon_accrued_value_2009_06_12_usd": "12.81",
        "total_payable_at_maturity_usd": "2251362338.92",
        "offers_received": "35",
        "offered_underlying_vno_usd": str(received_vno),
        "offered_effective_usd": money(received_effective),
        "offered_share_total_payable_pct": "1.97",
        "cutoff_price_per_100_usd": "12.70",
        "weighted_average_awarded_price": "12.68",
        "average_discount_pct": "1.86",
        "offers_accepted": "20",
        "awarded_underlying_vno_usd": str(accepted_vno),
        "awarded_effective_usd": money(accepted_effective),
        "awarded_share_of_offered_effective_pct": "75.94",
        "saving_usd": "637468.08",
        "accepted_participants": str(len(awards)),
        "caja_depositante": "0306",
        "caja_comitente": "40000",
        "source_id": "e0_mecon_strip_boden2012_call_2009_06_10;e0_mecon_strip_boden2012_result_2009_06_12",
        "source_locator": "call_PDF_pp1_2;result_PDF_pp1_3",
        "settlement_confirmation": "SCHEDULED_NOT_INDEPENDENTLY_CONFIRMED",
        "caveat": "Valor efectivo del cupón no es VNO subyacente ni caja confirmada; participantes no son tenedores finales.",
    }
]
write_csv(HERE / "E0_FISCAL_STRIP_BUYBACK_SUMMARY_2009_V116.csv", summary)


tenders = read_csv(HERE / "E0_FISCAL_PUBLIC_BUYBACK_TENDERS_2008_V116.csv")
date_totals: dict[str, Decimal] = defaultdict(Decimal)
date_fx: dict[str, Decimal] = defaultdict(Decimal)
for row in tenders:
    date_totals[row["tender_date"]] += Decimal(row["awarded_effective_ars"])
    date_fx[row["tender_date"]] = max(date_fx[row["tender_date"]], Decimal(row["reference_fx_ars_per_usd"]))
public_usd_equivalent = sum((date_totals[date] / date_fx[date] for date in date_totals), Decimal(0))
first_stage = Decimal("380000000")
synthetic_sum = first_stage + public_usd_equivalent
bcra_control = Decimal("420000000")
gap = synthetic_sum - bcra_control
gap_pct = gap / bcra_control * Decimal(100)
gap_pct_8 = gap_pct.quantize(Decimal("0.00000001"))
bridge = []
for date in sorted(date_totals):
    bridge.append(
        {
            "row_id": f"PUBLIC_{date}", "component": "FOUR_PUBLIC_TENDERS", "date_or_period": date,
            "amount": money(date_totals[date]), "unit": "ARS_effective", "fx_or_conversion": str(date_fx[date]),
            "usd_equivalent": str(date_totals[date] / date_fx[date]), "basis": "OFFICIAL_RESULT_AND_REFERENCE_FX",
            "additivity": "COMPONENT_FOR_SENSITIVITY_ONLY", "source_id": "E0_FISCAL_PUBLIC_BUYBACK_TENDERS_2008_V116.csv",
            "caveat": "Conversión de control; no prueba caja ni homogeneidad temporal perfecta.",
        }
    )
bridge.extend(
    [
        {"row_id": "FIRST_STAGE_APPROX", "component": "FIRST_STAGE_MARKET_PURCHASES", "date_or_period": "2008-08-11/2008-08-22", "amount": "380000000", "unit": "USD_approx_effective", "fx_or_conversion": "N/A", "usd_equivalent": "380000000", "basis": "OFFICIAL_APPROXIMATE_PROGRAM_AGGREGATE", "additivity": "NON_ADDITIVE_APPROXIMATE", "source_id": "e0_argentina_recompra_segunda_semana_2008_08_22", "caveat": "Aproximado, especies mezcladas y blotter abierto."},
        {"row_id": "PUBLIC_TOTAL_USD_EQ", "component": "FOUR_PUBLIC_TENDERS", "date_or_period": "2008-08-28/2008-10-02", "amount": "135606214.86", "unit": "ARS_effective", "fx_or_conversion": "DATE_SPECIFIC_REFERENCE_FX", "usd_equivalent": str(public_usd_equivalent), "basis": "DERIVED_DATE_LEVEL_CONVERSION", "additivity": "SENSITIVITY_COMPONENT", "source_id": "E0_FISCAL_PUBLIC_BUYBACK_TENDERS_2008_V116.csv", "caveat": "Equivalente sintético, no total contable USD."},
        {"row_id": "SYNTHETIC_SUM", "component": "FIRST_STAGE_PLUS_PUBLIC_EQUIVALENT", "date_or_period": "2008-08/2008-10", "amount": str(synthetic_sum), "unit": "USD_synthetic", "fx_or_conversion": "N/A", "usd_equivalent": str(synthetic_sum), "basis": "DERIVED_APPROXIMATE_BRIDGE", "additivity": "CONTROL_NOT_ADDITIVE", "source_id": "e0_argentina_recompra_segunda_semana_2008_08_22;E0_FISCAL_PUBLIC_BUYBACK_TENDERS_2008_V116.csv", "caveat": "No afirmar conciliación exacta ni liquidación; combina un aproximado con conversiones de fecha."},
        {"row_id": "BCRA_CONTROL", "component": "BCRA_PROGRAM_AGGREGATE", "date_or_period": "FROM_2008-08", "amount": "420000000", "unit": "USD_approx", "fx_or_conversion": "N/A", "usd_equivalent": "420000000", "basis": "BCRA_MONTO_CERCANO", "additivity": "INDEPENDENT_CONTROL_NOT_ADDITIVE", "source_id": "e0_bcra_inflation_report_q4_2008_buyback_control", "caveat": "Monto cercano; alcance y fecha de corte no se identifican al nivel de operación."},
        {"row_id": "BRIDGE_GAP", "component": "SYNTHETIC_MINUS_BCRA_CONTROL", "date_or_period": "2008-08/2008-10", "amount": str(gap), "unit": "USD_synthetic", "fx_or_conversion": "N/A", "usd_equivalent": str(gap), "basis": f"{gap_pct_8}%_OF_BCRA_APPROX_CONTROL", "additivity": "DIAGNOSTIC_ONLY", "source_id": "E0_FISCAL_BUYBACK_APPROX_AGGREGATE_BRIDGE_V116.csv", "caveat": "Brecha pequeña compatible con redondeo/alcance, pero no demuestra igualdad ni exhaustividad."},
    ]
)
write_csv(HERE / "E0_FISCAL_BUYBACK_APPROX_AGGREGATE_BRIDGE_V116.csv", bridge)


provenance = [
    {
        "source_id": "e0_mecon_strip_boden2012_call_2009_06_10",
        "original_url": source_specs[0]["url"],
        "retrieval_url": "https://web.archive.org/web/20090619202926id_/http://www.mecon.gov.ar/finanzas/sfinan/documentos/comunicado_de_prensa_boden2012.pdf",
        "capture_timestamp": "20090619202926", "cdx_digest": "S7GOXGJQEH56CLSGQ5TXP6Z6U2QCHIYX",
        "local_path": source_specs[0]["local"], "sha256": source_specs[0]["sha256"], "bytes": str(source_specs[0]["bytes"]),
        "provenance_note": "Binario oficial original preservado por Internet Archive; URL institucional histórica ya no es una ruta viva confiable.",
    },
    {
        "source_id": "e0_mecon_strip_boden2012_result_2009_06_12",
        "original_url": source_specs[1]["url"],
        "retrieval_url": "https://web.archive.org/web/20090619203017id_/http://www.mecon.gov.ar/finanzas/sfinan/documentos/comunicado_de_prensa_resultado_con%20anexo.pdf",
        "capture_timestamp": "20090619203017", "cdx_digest": "2J7QZWPHLWKE5A2WQTC4HMWS2IUD44XS",
        "local_path": source_specs[1]["local"], "sha256": source_specs[1]["sha256"], "bytes": str(source_specs[1]["bytes"]),
        "provenance_note": "Binario oficial original preservado por Internet Archive; incluye comunicado y anexo de 35 ofertas.",
    },
    {
        "source_id": "e0_bcra_inflation_report_q4_2008_buyback_control",
        "original_url": source_specs[2]["url"], "retrieval_url": source_specs[2]["url"],
        "capture_timestamp": "", "cdx_digest": "", "local_path": source_specs[2]["local"],
        "sha256": source_specs[2]["sha256"], "bytes": str(source_specs[2]["bytes"]),
        "provenance_note": "Descarga directa actual desde BCRA; control oficial aproximado independiente.",
    },
]
write_csv(HERE / "ARCHIVAL_PROVENANCE_V116.csv", provenance)


events = [{key: v116_text(value) for key, value in row.items()} for row in read_csv(V115 / "E0_FISCAL_BUYBACK_PROGRAM_EVENTS_2005_2009_V115.csv")]
for row in events:
    if row["event_id"] == "E2009_STRIP_OFFICIAL":
        row.update(
            {
                "event_date": "2009-06-10/2009-06-18", "reported_amount": "35;20;44367798.74;33691889.24;265707100;637468.08",
                "unit": "offers_received;offers_accepted;USD_effective_offered;USD_effective_awarded;USD_underlying_VNO_awarded;USD_saving",
                "amount_basis": "OFFICIAL_PRIMARY_CALL_RESULT_AND_ANNEX", "status": "PRIMARY_RESULT_EXACT_SETTLEMENT_OPEN",
                "source_id": "e0_mecon_strip_boden2012_call_2009_06_10;e0_mecon_strip_boden2012_result_2009_06_12",
                "locator": "call_PDF_pp1_2;result_PDF_pp1_3", "additivity": "SEPARATE_STRIP_EVENT_NON_ADDITIVE",
                "caveat": "El efectivo del cupón no es VNO subyacente; 18/06 es fecha prevista, no pago confirmado.",
            }
        )
    elif row["event_id"] == "E2009_STRIP_SECONDARY_RESULT":
        row.update(
            {
                "status": "SECONDARY_QUANTITATIVE_CORROBORATED_BY_PRIMARY",
                "source_id": "sec_consejo_iec_298_strip_boden2012;e0_mecon_strip_boden2012_result_2009_06_12",
                "caveat": "La síntesis secundaria queda corroborada y refinada por el resultado primario; no prueba caja.",
            }
        )
if not any(row["event_id"] == "E2008_BCRA_APPROX_PROGRAM_CONTROL" for row in events):
    events.append(
        {
            "event_id": "E2008_BCRA_APPROX_PROGRAM_CONTROL", "event_date": "2008-08/2008-10", "stage": "PROGRAM_AGGREGATE_CONTROL",
            "instrument_scope": "PUBLIC_DEBT_BUYBACK_PROGRAM", "agent_or_channel": "TREASURY_PROGRAM_REPORTED_BY_BCRA",
            "reported_amount": "420000000", "unit": "USD_approx", "amount_basis": "BCRA_MONTO_CERCANO",
            "status": "INDEPENDENT_APPROXIMATE_AGGREGATE_CONTROL", "source_id": "e0_bcra_inflation_report_q4_2008_buyback_control",
            "locator": "PDF_p51_printed_p50", "additivity": "CONTROL_NOT_ADDITIVE",
            "caveat": "No identifica especies, contrapartes, cortes ni liquidaciones y no debe sumarse a los componentes.",
        }
    )
write_csv(HERE / "E0_FISCAL_BUYBACK_PROGRAM_EVENTS_2005_2009_V116.csv", events)


ledger = [{key: v116_text(value) for key, value in row.items()} for row in read_csv(V115 / "E0_FISCAL_MECHANISM_LEDGER_V115.csv")]
ledger_fields = list(ledger[0])
new_ledger = [
    ("F115", "2008", "Debt_buyback", "BCRA_APPROX_PROGRAM_CONTROL", "2008-10", "Tesoro_Nacional", "Market_counterparties_unknown", "Program_from_August", "Public_debt_unspecified", "420000000", "USD_approx", "N/D", "BCRA_MONTO_CERCANO", "e0_bcra_inflation_report_q4_2008_buyback_control", "PDF_p51_printed_p50", "APPROXIMATE_AGGREGATE_CONTROL", "CONTROL_NOT_ADDITIVE", "BCRA supplies an independent approximate program control.", "No instrument, counterparty or settlement split."),
    ("F116", "2009", "BODEN_2012_strip_buyback", "PRIMARY_CALL_AND_ROUTE", "2009-06-10", "Tesoro_Nacional", "Eligible_MAE_participants", "MAE_Caja_0306_40000_BCRA", "BODEN_2012_coupon_15_strip", "N/D", "TOTAL_COUPON_EMISSION", "N/D", "CALL_MAXIMUM_NON_NUMERIC", "e0_mecon_strip_boden2012_call_2009_06_10", "PDF_pp1_2", "CALL_PUBLISHED_T_PLUS_3_PAYMENT_OPEN", "NON_ADDITIVE", "Call fixes ISIN, T+2, Caja account and T+3.", "Route does not confirm transfer or payment."),
    ("F117", "2009", "BODEN_2012_strip_buyback", "PRIMARY_TENDER_RESULT", "2009-06-12", "Tesoro_Nacional", "Twenty_accepted_offers", "MAE_public_tender", "BODEN_2012_coupon_15_strip", "33691889.24", "USD_effective_coupon_value", "N/D", "OFFICIAL_35_OFFERS_20_ACCEPTED", "e0_mecon_strip_boden2012_result_2009_06_12", "PDF_pp1_3", "AWARDED_SETTLEMENT_OPEN", "NON_ADDITIVE", "Primary result fixes exact offered and awarded effective values.", "Award is not Caja delivery or BCRA payment."),
    ("F118", "2009", "BODEN_2012_strip_buyback", "UNDERLYING_VNO_CONTROL", "2009-06-12", "Tesoro_Nacional", "Twenty_accepted_offers", "MAE_public_tender", "BODEN_2012_underlying", "265707100", "USD_underlying_VNO", "N/D", "SUM_ACCEPTED_ANNEX_ROWS", "e0_mecon_strip_boden2012_result_2009_06_12", "PDF_annex_pp2_3", "DERIVED_EXACT_CONTROL", "CONTROL_NOT_ADDITIVE", "Underlying VNO is reconstructed exactly from accepted rows.", "Do not equate underlying VNO with effective coupon value."),
    ("F119", "2009", "BODEN_2012_strip_buyback", "PRICE_AND_SAVING_CONTROL", "2009-06-12", "Tesoro_Nacional", "Twenty_accepted_offers", "MAE_public_tender", "BODEN_2012_coupon_15_strip", "637468.08", "USD_saving", "N/D", "CUTOFF_12.70_AVERAGE_12.68_DISCOUNT_1.86PCT", "e0_mecon_strip_boden2012_result_2009_06_12", "PDF_p1", "OFFICIAL_RESULT_CONTROL", "CONTROL_NOT_ADDITIVE", "Official result reports cutoff, weighted average, discount and saving.", "Saving is not expenditure or settled cash."),
    ("F120", "2009", "BODEN_2012_strip_buyback", "PARTICIPANT_RECONSTRUCTION", "2009-06-12", "Tesoro_Nacional", "Seven_MAE_participants", "Twenty_accepted_offers", "BODEN_2012_coupon_15_strip", "7", "participants", "N/D", "GROUPED_ACCEPTED_ANNEX_ROWS", "e0_mecon_strip_boden2012_result_2009_06_12", "PDF_annex_pp2_3", "PARTICIPANTS_IDENTIFIED_HOLDERS_OPEN", "NON_ADDITIVE", "Accepted rows group to seven named market participants.", "Participants are not ultimate holders or beneficiaries."),
    ("F121", "2008", "Debt_buyback", "APPROXIMATE_AGGREGATE_BRIDGE", "2008-08/2008-10", "Tesoro_Nacional", "Market_counterparties_unknown", "First_stage_plus_public_tenders", "Mixed_public_debt", str(synthetic_sum), "USD_synthetic", "N/D", f"BCRA_CONTROL_GAP_{gap_pct_8}%", "e0_bcra_inflation_report_q4_2008_buyback_control;E0_FISCAL_BUYBACK_APPROX_AGGREGATE_BRIDGE_V116.csv", "PDF_p51;bridge", "NEAR_AGGREGATE_CONSISTENCY_ONLY", "CONTROL_NOT_ADDITIVE", "Approximate USD380m plus date-converted public results lies near the BCRA USD420m control.", "Approximate inputs and scope differences prohibit exact reconciliation."),
]
known_ledger = {row["ledger_id"] for row in ledger}
for values in new_ledger:
    if values[0] not in known_ledger:
        ledger.append(dict(zip(ledger_fields, values)))
write_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V116.csv", ledger, ledger_fields)


breaks = [{key: v116_text(value) for key, value in row.items()} for row in read_csv(V115 / "E0_FISCAL_METHOD_BREAKS_V115.csv")]
break_fields = list(breaks[0])
new_breaks = [
    ("strip_effective_not_underlying_vno", "unit", "El valor efectivo del cupón y el VNO del BODEN subyacente son bases distintas.", "Conservar ambas columnas y no sumarlas ni sustituir una por otra.", "Resultado primario strip 2009 y anexo"),
    ("archival_capture_preserves_primary_provenance", "source", "Una captura archivada puede preservar el binario oficial aunque la URL institucional histórica deje de resolver.", "Registrar URL original, sello de captura, digest CDX y hash local; no degradar el documento a fuente secundaria.", "ARCHIVAL_PROVENANCE_V116.csv"),
    ("approximate_program_aggregate_not_exact_reconciliation", "aggregation", "Dos montos cercanos y conversiones por fecha no forman una conciliación contable exacta.", "Usar la brecha sólo como control de orden de magnitud y mantener CONTROL_NOT_ADDITIVE.", "Informe BCRA 4T2008 y puente V116"),
]
known_breaks = {row["break_id"] for row in breaks}
for break_id, dimension, problem, rule, evidence_item in new_breaks:
    if break_id not in known_breaks:
        breaks.append({"break_id": break_id, "dimension": dimension, "problem": problem, "rule": rule, "status": "FROZEN", "evidence": evidence_item})
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V116.csv", breaks, break_fields)


matrix = [{key: v116_text(value) for key, value in row.items()} for row in read_csv(V115 / "HISTORICAL_EPISODE_MATRIX_2001_2026_V115.csv")]
for row in matrix:
    if row["variable"] == "boden_2012_strip_and_residual_registration":
        row.update(
            {
                "t0": "2009-06-10_TO_2009-06-18", "pre_value": "PRIMARY_CALL_ISIN_ARARGE03G415",
                "trough_value": "35_OFFERS_USD44.36779874M_EFFECTIVE", "trough_date": "2009-06-12",
                "recovery_value": "20_ACCEPTED_USD33.69188924M_EFFECTIVE_VNO_USD265.7071M", "recovery_date": "2009-06-18_SCHEDULED",
                "benchmark_definition": "primary call, exact result and all 35 annex rows with effective/underlying bases separated",
                "source_id": "e0_mecon_strip_boden2012_call_2009_06_10;e0_mecon_strip_boden2012_result_2009_06_12;E0_FISCAL_STRIP_BUYBACK_OFFERS_2009_V116.csv",
                "source_quality": "PRIMARY_DERIVED_EXACT", "basis": "Official archived Finance call and result annex",
                "method_break": "YES_STRIP_EFFECTIVE_NOT_VNO_PARTICIPANT_NOT_HOLDER_SETTLEMENT_OPEN",
                "status": "STRIP_PRIMARY_RESULT_EXACT_PARTICIPANTS_MAPPED_SETTLEMENT_OPEN",
                "interpretation": "The official annex closes offer, award and participant arithmetic while leaving final holders and cash settlement open.",
                "falsifier": "YES_AWARD_OR_PARTICIPANT_EQUALS_SETTLED_CASH_OR_FINAL_HOLDER",
                "notes": "35 offers; 20 accepted; seven participants; Caja 0306/40000; payment scheduled 18 June 2009, not independently confirmed.",
            }
        )
write_csv(HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V116.csv", matrix)


evidence = [{key: v116_text(value) for key, value in row.items()} for row in read_csv(V115 / "HISTORICAL_EVIDENCE_COVERAGE_V115.csv")]
for row in evidence:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            {
                "quality": "PRIMARY_BUYBACK_FOUR_ARCHIVED_ROUNDS_STRIP_PRIMARY_EXACT_ACCOUNT_ROUTE_2001_2012",
                "comparable": "SERIES_SERVICE_RECONCILED_FOUR_ARCHIVED_ROUNDS_STRIP_EXACT_ROUTES_MAPPED",
                "gap": "Cuatro rondas 2008 y strip 2009 tienen resultados primarios y rutas Caja/BCRA; faltan confirmaciones efectivas, blotter BNA, tenedores/propósito, respuesta individual AGN y padrón CRYL.",
                "next_action": "Recuperar confirmaciones Caja/BCRA, blotter BNA, clientes finales/CRYL y respuesta individual AGN.",
            }
        )
write_csv(HERE / "HISTORICAL_EVIDENCE_COVERAGE_V116.csv", evidence)


queue = [{key: v116_text(value) for key, value in row.items()} for row in read_csv(V115 / "HISTORICAL_SOURCE_QUEUE_V115.csv")]
for row in queue:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            {
                "status": "FOUR_ROUNDS_AND_STRIP_PRIMARY_EXACT_SETTLEMENT_HOLDERS_OPEN",
                "why": "Los cuatro pares 2008 y el strip 2009 tienen resultado primario y ruta 0306/40000; faltan constancias post-liquidación, blotter BNA y clientes finales.",
                "next_action": "Recuperar confirmaciones Caja/BCRA, blotter BNA, clientes finales/CRYL y respuesta individual AGN.",
            }
        )
write_csv(HERE / "HISTORICAL_SOURCE_QUEUE_V116.csv", queue)


inherited = [
    {"script": "qa_v97.py", "pre_v116_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v116_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V97 requiere que una fuente recuperada después permanezca sin ruta/hash."},
    *({"script": f"qa_v{i}.py", "pre_v116_result": "PASS", "post_v116_result": "PASS", "interpretation": "Compatible"} for i in (98, 100, 101, 102, 103, 104, 105, 106)),
    *({"script": f"qa_v{i}.py", "pre_v116_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v116_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "Falla sólo porque congela conteos anteriores a V116."} for i in range(107, 116)),
    {"script": "qa_v116.py", "pre_v116_result": "N/A", "post_v116_result": "PASS", "interpretation": "Invariantes actuales, PDFs, 35 ofertas, agrupación y puente aproximado."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V116.csv", inherited)


readme = f"""# Checkpoint V116 · resultado primario del strip 2009

V116 amplía V115 sin tocar el panel bancario. Preserva el llamado y el resultado oficiales del strip del cupón 15 de BODEN 2012, su anexo completo y un control agregado independiente del BCRA.

## Resultado

- 3 nuevas fuentes primarias oficiales preservadas; {len(census)} fuentes primarias E0 acumuladas;
- 35 ofertas por USD {money(received_effective)} efectivos y VNO USD {received_vno};
- 20 aceptadas por USD {money(accepted_effective)} efectivos y VNO USD {accepted_vno};
- siete participantes MAE reconstruidos, sin convertirlos en tenedores finales;
- Caja 0306/40000, títulos T+2 el 17/06 y liquidación T+3 prevista el 18/06/2009;
- BCRA: programa desde agosto por un monto cercano a USD 420m;
- puente sintético USD {money(synthetic_sum)}, a {gap_pct_8}% del control aproximado; no es conciliación exacta.

## Invariantes

Panel estricto Q4-2023: 30 entidades; cobertura {STRICT}%; CLOSED_NETWORK_GATE=NO; Banco Rioja mismatch 158,789k.

## Leer primero

1. VEREDICTO_V116.md
2. E0_FISCAL_RECONSTRUCTION_V116.md
3. E0_FISCAL_STRIP_BUYBACK_SUMMARY_2009_V116.csv
4. E0_FISCAL_STRIP_BUYBACK_OFFERS_2009_V116.csv
5. E0_FISCAL_STRIP_BUYBACK_AWARDS_2009_V116.csv
6. E0_FISCAL_BUYBACK_APPROX_AGGREGATE_BRIDGE_V116.csv
7. ARCHIVAL_PROVENANCE_V116.csv
8. AUDITORIA_V116.md
9. HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V116_A_V117.md
"""
(HERE / "README_V116.md").write_text(readme, encoding="utf-8")


reconstruction = f"""# Reconstrucción fiscal E0 · strip BODEN 2012 y control agregado · V116

## Resultado primario del 12 de junio de 2009

El llamado oficial identifica el cupón de amortización y renta Nº 15 de BODEN 2012, ISIN ARARGE03G415. Las ofertas se recibieron el 12/06; los títulos debían transferirse a Caja depositante 0306 / comitente 40.000 el 17/06 (T+2), y la liquidación en dólares estaba prevista para el 18/06 (T+3) mediante cuentas corrientes de los participantes en el BCRA.

El resultado y su anexo cierran exactamente 35 ofertas por VNO subyacente USD {received_vno} y valor efectivo USD {money(received_effective)}. Las primeras 20, hasta el corte USD 12,70 por cada VNO 100, fueron aceptadas: VNO USD {accepted_vno} y valor efectivo USD {money(accepted_effective)}. El precio promedio ponderado oficial es USD 12,68, el descuento medio 1,86% y el ahorro USD 637.468,08.

Las ofertas aceptadas se agrupan en siete participantes: Citibank, Standard Bank, BBVA Banco Francés, MERVAL, Nuevo Banco Bisel, Banco de Galicia y Banco Morgan. Son participantes del MAE, no tenedores económicos finales. El valor efectivo del cupón tampoco equivale al VNO del BODEN subyacente.

## Control BCRA de 2008

El Informe de Inflación 4T2008 dice que el programa iniciado en agosto involucró un monto cercano a USD 420m. Como control de sensibilidad, USD 380m aproximados de la primera etapa más USD {money(public_usd_equivalent)} equivalentes de las cuatro rondas públicas da USD {money(synthetic_sum)}; la diferencia es USD {money(gap)}, {gap_pct_8}% del control BCRA.

Esta cercanía no es una conciliación: USD 380m y USD 420m son aproximados, las cuatro rondas se convierten con tipos de cambio de fecha y el alcance puede no coincidir. Ningún monto nuevo se marca como CASH_SETTLED.

## Estado abierto

Persisten las confirmaciones Caja/BCRA de las cuatro rondas 2008 y del strip 2009, el blotter BNA, tenedores finales/CRYL, la respuesta individual AGN y la conciliación Tesoro–Caja–BCRA. CLOSED_NETWORK_GATE=NO.
"""
(HERE / "E0_FISCAL_RECONSTRUCTION_V116.md").write_text(reconstruction, encoding="utf-8")


audit_text = f"""# Auditoría V116

## Preservación y revisión visual

Se preservaron tres PDFs oficiales. El llamado de dos páginas, el resultado de tres páginas y la portada/página pertinente del informe BCRA de 80 páginas fueron renderizados e inspeccionados visualmente. Los renderizados temporales se eliminaron.

## Pruebas exactas

- 35 filas: VNO USD {received_vno}; efectivo USD {money(received_effective)};
- 20 aceptadas: VNO USD {accepted_vno}; efectivo USD {money(accepted_effective)};
- siete participantes aceptados y corte USD 12,70;
- suma por participante igual a la adjudicación exacta;
- control aproximado: USD {money(synthetic_sum)} sintéticos frente a USD 420m cercanos; brecha {gap_pct_8}%.

## Controles de alcance

- cupón efectivo no es VNO subyacente;
- participante no es tenedor final;
- captura archivada conserva procedencia primaria, registrada con timestamp y digest;
- T+3 previsto no es liquidación;
- proximidad entre agregados aproximados no es reconciliación contable.

## Conteos

- fuentes primarias E0: {len(census)};
- ledger fiscal: {len(ledger)} filas;
- quiebres: {len(breaks)};
- eventos: {len(events)}.
"""
(HERE / "AUDITORIA_V116.md").write_text(audit_text, encoding="utf-8")


verdict = f"""# Veredicto V116

## Qué avanzó

- El resultado del strip 2009 pasa de síntesis secundaria a fuente primaria exacta con anexo completo.
- Quedan separados USD {money(accepted_effective)} efectivos del cupón y VNO USD {accepted_vno} subyacente.
- Se identifican siete participantes MAE, sin tratarlos como beneficiarios finales.
- El BCRA aporta un control independiente cercano a USD 420m para el programa de 2008.
- El puente sintético queda a {gap_pct_8}% del control, únicamente como consistencia de orden de magnitud.

## Qué sigue prohibido afirmar

- que adjudicación sea entrega Caja o pago BCRA;
- que participante sea tenedor final;
- que valor efectivo del cupón sea VNO del bono;
- que dos cifras aproximadas formen una conciliación exacta;
- que el control BCRA se sume a BNA, licitaciones o CGN.

## Estado

La rama fiscal pasa a PRIMARY_BUYBACK_FOUR_ARCHIVED_ROUNDS_STRIP_PRIMARY_EXACT_ACCOUNT_ROUTE_2001_2012. Siguen abiertos Caja/BCRA, blotter BNA, tenedores/CRYL y AGN individual. CLOSED_NETWORK_GATE=NO.
"""
(HERE / "VEREDICTO_V116.md").write_text(verdict, encoding="utf-8")


refs = ["# Referencias de fuentes V116", "", "## Primarias preservadas"]
refs.extend(f"- {spec['title']}: {spec['url']}" for spec in source_specs)
refs.extend(["", "La procedencia archivística consta en ARCHIVAL_PROVENANCE_V116.csv; hashes y uso en el censo E0 y el catálogo maestro."])
(HERE / "SOURCE_REFERENCES_V116.md").write_text("\n".join(refs) + "\n", encoding="utf-8")


retrieval = """# Registro de recuperación V116

## Hallazgos promovidos

- Wayback CDX permitió recuperar los binarios oficiales originales del llamado del 10/06/2009 y del resultado con anexo del 12/06/2009.
- El anexo contiene las 35 ofertas y permite reproducir exactamente las 20 adjudicadas.
- El Informe de Inflación BCRA 4T2008 aporta un control agregado cercano a USD 420m para el programa iniciado en agosto.

## Búsquedas que permanecen negativas

- No se recuperaron confirmaciones post-liquidación de Caja de Valores ni asientos/pagos BCRA para 2008 o el 18/06/2009.
- No apareció el blotter BNA del 11–22/08/2008.
- No apareció el adjunto individual de la respuesta AGN de 2018.
- No apareció padrón CRYL, conciliación Tesoro–Caja–BCRA–FGS ni identificación de clientes finales.

## Regla de continuidad

El resultado primario del strip queda resuelto. Las próximas búsquedas deben centrarse en constancias operativas, expedientes administrativos, blotter BNA, AGN individual y tenedores finales.
"""
(HERE / "RETRIEVAL_LOG_V116.md").write_text(retrieval, encoding="utf-8")


handover = f"""# Handover próxima sesión · V116 → V117

## Estado congelado

- {len(census)} fuentes primarias E0; {len(ledger)} filas fiscales; {len(breaks)} quiebres;
- cuatro rondas oficiales 2008 y strip 2009 con resultado primario exacto;
- strip: 35 ofertas, 20 aceptadas, USD {money(accepted_effective)} efectivos, VNO USD {accepted_vno}, siete participantes;
- Caja 0306/40000 y T+3 exactos, pero sin constancia post-liquidación;
- control BCRA cercano a USD 420m y puente aproximado no aditivo;
- panel bancario intacto: 30 entidades, {STRICT}%.

## Prioridad V117

1. confirmaciones Caja/BCRA de 2008 y 18/06/2009;
2. blotter/orden ejecutada BNA de 11–22/08/2008;
3. respuesta individual y adjuntos AGN de 14/08/2018;
4. padrón CRYL, clientes finales o conciliación Tesoro–Caja–BCRA–FGS.

## No hacer

- no convertir adjudicación en pago;
- no convertir participante en beneficiario;
- no mezclar efectivo del cupón con VNO subyacente;
- no convertir cercanía aproximada en reconciliación exacta;
- no sumar controles solapados.

CLOSED_NETWORK_GATE=NO.
"""
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V116_A_V117.md").write_text(handover, encoding="utf-8")


old_hash = read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V115.csv")
hash_rows = [row for row in old_hash if row["id"] not in new_ids]
for spec in source_specs:
    hash_rows.append({"id": spec["id"], "archivo_local": spec["local"], "exists": "True", "sha_catalog": spec["sha256"], "sha_actual": spec["sha256"], "hash_ok": "True"})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V116.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V116.csv", hash_rows)
shutil.copyfile(AUDIT / "SOURCE_PATH_ENCODING_EXCEPTIONS_V115.csv", AUDIT / "SOURCE_PATH_ENCODING_EXCEPTIONS_V116.csv")
shutil.copyfile(AUDIT / "SOURCE_PRESERVATION_MISSING_V115.csv", AUDIT / "SOURCE_PRESERVATION_MISSING_V116.csv")


size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": str(size), "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V116.csv", size_rows, ["path", "bytes", "mib", "over_50_mib", "over_100_mib"])


physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
completeness = {
    "checkpoint": "V116", "date": "2026-08-29", "state": "E0_STRIP_PRIMARY_EXACT_PARTICIPANTS_MAPPED_SETTLEMENT_OPEN",
    "master_catalog_entries": len(catalog), "physical_local_copies": physical, "physical_local_hash_ok": hash_ok,
    "reference_only_nonbinary_exempt": 4, "remaining_physical_gaps": 1, "p0": 0, "p1": 1, "p2": 0,
    "binary_required_entries": len(catalog) - 4, "binary_required_preserved": physical, "binary_required_source_complete": False,
    "pending_binary_discovery_actions": 4, "numeric_v116_strict_changed": False, "strict_coverage_pct": STRICT,
    "exact_entities": 30, "asset_numerator_million_ars": "59812903.504", "system_denominator_million_ars": "96697695.5",
    "closed_network_gate": "NO", "e0_primary_sources_preserved": len(census), "sources_newly_preserved_v116": len(source_specs),
    "e0_primary_sources_newly_preserved_v116": len(source_specs),
    "e0_quality": "PRIMARY_BUYBACK_FOUR_ARCHIVED_ROUNDS_STRIP_PRIMARY_EXACT_ACCOUNT_ROUTE_2001_2012",
    "e0_comparable": False, "e0_fiscal_phase_separated": True, "e0_fiscal_final_cash_total_identified": False,
    "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
    "e0_four_archived_rounds_confirmed": True, "e0_settlement_confirmations_preserved": False,
    "e0_bna_trade_blotter_preserved": False, "e0_first_stage_mixed_aggregate_usd_approx": "380000000",
    "e0_bcra_program_aggregate_usd_approx": "420000000", "e0_approx_bridge_usd": str(synthetic_sum),
    "e0_approx_bridge_gap_pct_of_bcra_control": str(gap_pct_8), "e0_strip_primary_quantitative_result_preserved": True,
    "e0_strip_offers_received": 35, "e0_strip_offers_accepted": 20, "e0_strip_offered_effective_usd": money(received_effective),
    "e0_strip_awarded_effective_usd": money(accepted_effective), "e0_strip_awarded_underlying_vno_usd": str(accepted_vno),
    "e0_strip_accepted_participants": len(awards), "e0_strip_settlement_confirmed": False,
    "e0_ultimate_holders_identified": False, "e0_agn_boden_report_identifiers_definitively_resolved": False,
    "e0_causal_net_incidence_identified": False,
    "historical_workstream": "E0_CAJA_BCRA_CONFIRMATIONS_BNA_BENEFICIAL_HOLDER_AND_AGN_REPLY_OPEN",
    "path_encoding_note": "Banco La Pampa remains byte-identical despite the catalog/Git filename encoding mismatch.",
}
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V116.json").write_text(json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V116 · resultado primario del strip 2009"
old_backup = backup.read_text(encoding="utf-8-sig")
if marker not in old_backup:
    old_backup += f"\n\n{marker}\n\n- Resultado oficial con 35 ofertas y 20 aceptadas; USD {money(accepted_effective)} efectivos y VNO USD {accepted_vno}.\n- Siete participantes MAE reconstruidos; tenedores finales y pago siguen abiertos.\n- BCRA aporta control cercano a USD 420m; el puente aproximado no es conciliación.\n"
    backup.write_text(old_backup, encoding="utf-8")


def write_checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V116.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V116", "parent_checkpoint": "V115",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": len(source_specs), "new_primary_sources": len(source_specs),
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks), "buyback_program_events": len(events),
        "strip_offer_rows": len(offers), "strip_accepted_offer_rows": sum(row["accepted"] == "YES" for row in offers),
        "strip_participant_rows": len(awards), "strip_offered_effective_usd": money(received_effective),
        "strip_awarded_effective_usd": money(accepted_effective), "strip_awarded_underlying_vno_usd": str(accepted_vno),
        "bcra_program_control_usd_approx": "420000000", "approx_bridge_usd": str(synthetic_sum),
        "approx_bridge_gap_pct": str(gap_pct_8), "files": files,
    }
    (HERE / "MANIFEST_V116.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    "checkpoint": "V116", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical local copies with {hash_ok}/{physical} SHA-valid; 3 new primary E0 sources preserved; one catalogued P1 binary gap plus four discovery actions remain.",
    "historical_workstream": "E0 four official 2008 rounds and exact primary 2009 strip result with Caja/BCRA routes; actual settlement, first-stage blotter, AGN reply and ultimate holders remain open",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V116 BUILD PASS")
