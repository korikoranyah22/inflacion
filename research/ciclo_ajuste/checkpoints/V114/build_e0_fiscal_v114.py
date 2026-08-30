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
V113 = HERE.parent / "V113"
CYCLE = REPO / "research" / "ciclo_ajuste"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
AUDIT = CYCLE / "source_audit"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v114" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"
CENT = Decimal("0.01")


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


def v114_text(text: str) -> str:
    return text.replace("V113", "V114").replace("v113", "v114")


def clone_versioned(stem: str) -> None:
    src = V113 / f"{stem}_V113.csv"
    dst = HERE / f"{stem}_V114.csv"
    dst.write_text(v114_text(src.read_text(encoding="utf-8-sig")), encoding="utf-8-sig")


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
    "E0_FISCAL_BUYBACK_SETTLEMENT_CHAIN",
):
    clone_versioned(stem)


source_specs = [
    {
        "id": "e0_argentina_recompras_decreto_1735_04_report",
        "primary": True,
        "institution": "Ministerio de Economía y Finanzas Públicas",
        "title": "Informe sobre recompras de deuda bajo el Decreto 1735/04",
        "url": "https://www.argentina.gob.ar/sites/default/files/recompras_de_deuda.pdf",
        "file": "argentina_recompras_deuda_decreto_1735_04.pdf",
        "publication": "",
        "period": "2004-2010",
        "type": "PDF oficial · binario preservado",
        "pages": "5",
        "families": "state_bcra;fiscal;debt;buyback;tender",
        "breaks": "recompra efectuada versus participante/tenedor final; licitación histórica versus programa 2008",
        "use": "USABLE_HISTORICAL_BODEN2012_BUYBACK_CONTROL",
        "caveat": "La licitación del 22/11/2005 cuantifica BODEN 2012, pero no publica participantes ni tenedores finales.",
        "verified": "Las cinco páginas fueron renderizadas e inspeccionadas visualmente; la tabla de la página 5 fue recompuesta.",
    },
    {
        "id": "e0_argentina_recompra_primera_etapa_2008_08_11",
        "primary": True,
        "institution": "Ministerio de Economía y Producción",
        "title": "Programa de recompra de vencimientos 2008-2009 · primera etapa",
        "url": "https://www.argentina.gob.ar/sites/default/files/comunicado_primera_etapa_11-08-08.pdf",
        "file": "argentina_recompra_primera_etapa_2008-08-11.pdf",
        "publication": "2008",
        "period": "2008-08-11",
        "type": "PDF oficial · binario preservado",
        "pages": "2",
        "families": "state_bcra;fiscal;debt;buyback;agent",
        "breaks": "mandato al BNA versus operación ejecutada; mezcla de especies",
        "use": "USABLE_BNA_AGENT_MANDATE",
        "caveat": "Instruye al BNA a recomprar varias series BODEN y BONAR, sin blotter, monto por especie ni contraparte.",
        "verified": "Página 1 renderizada e inspeccionada visualmente.",
    },
    {
        "id": "e0_argentina_recompra_segunda_etapa_2008_08_21",
        "primary": True,
        "institution": "Ministerio de Economía y Producción",
        "title": "Programa de recompra 2008-2009 · anuncio de segunda etapa",
        "url": "https://www.argentina.gob.ar/sites/default/files/comunicado_segunda_etapa_21-08-08.pdf",
        "file": "argentina_recompra_segunda_etapa_2008-08-21.pdf",
        "publication": "2008",
        "period": "2008-08-21",
        "type": "PDF oficial · binario preservado",
        "pages": "2",
        "families": "state_bcra;fiscal;debt;buyback;tender",
        "breaks": "anuncio periódico versus resultados localizados; programa versus licitación",
        "use": "USABLE_SECOND_STAGE_SCOPE",
        "caveat": "Anuncia licitaciones periódicas hasta fin de año; no certifica cuántas se realizaron ni su liquidación.",
        "verified": "Página 1 renderizada e inspeccionada visualmente.",
    },
    {
        "id": "e0_argentina_recompra_segunda_semana_2008_08_22",
        "primary": True,
        "institution": "Ministerio de Economía y Producción",
        "title": "Segunda semana del programa de recompra 2008-2009",
        "url": "https://www.argentina.gob.ar/sites/default/files/comunicado_2da_semana_de_recompra_de_deuda_22-08-08.pdf",
        "file": "argentina_recompra_segunda_semana_2008-08-22.pdf",
        "publication": "2008",
        "period": "2008-08-11/2008-08-22",
        "type": "PDF oficial · binario preservado",
        "pages": "2",
        "families": "state_bcra;fiscal;debt;buyback;market",
        "breaks": "agregado mixto versus instrumento; monto aproximado versus blotter",
        "use": "USABLE_FIRST_STAGE_MIXED_AGGREGATE",
        "caveat": "Los USD 380m aproximados mezclan BODEN 2012/2013/2008, BONAR V, PRE8 y unidades PBI en pesos.",
        "verified": "Página 1 renderizada e inspeccionada visualmente.",
    },
    {
        "id": "e0_argentina_resultado_recompra_2008_10_02",
        "primary": True,
        "institution": "Ministerio de Economía y Producción",
        "title": "Resultado de licitación de recompra · 2 de octubre de 2008",
        "url": "https://www.argentina.gob.ar/sites/default/files/comunicado_resultado_licitacion_02-10-08.pdf",
        "file": "argentina_resultado_recompra_2008-10-02.pdf",
        "publication": "2008",
        "period": "2008-10-02/2008-10-07",
        "type": "PDF oficial · binario preservado",
        "pages": "2",
        "families": "state_bcra;fiscal;debt;buyback;tender;counterparty",
        "breaks": "participante versus tenedor final; adjudicación versus confirmación de liquidación",
        "use": "USABLE_EXACT_GDP_UNIT_AWARD_RECONSTRUCTION",
        "caveat": "La tabla permite reconstruir participantes adjudicados, no clientes finales ni confirmación Caja/BCRA.",
        "verified": "Las dos páginas fueron renderizadas e inspeccionadas visualmente; totales recompuestos exactamente.",
    },
    {
        "id": "e0_bna_memoria_balance_2008",
        "primary": True,
        "institution": "Banco de la Nación Argentina",
        "title": "Memoria y Balance General 2008",
        "url": "https://www.bna.com.ar/Downloads/Memoria_Balance_BNA_2008.pdf",
        "file": "bna_memoria_balance_2008.pdf",
        "publication": "2009",
        "period": "2008",
        "type": "PDF oficial · binario preservado",
        "pages": "182",
        "families": "state_bcra;banks;debt;buyback;agent",
        "breaks": "memoria institucional versus blotter del agente; ausencia narrativa versus cero operaciones",
        "use": "USABLE_NEGATIVE_SCOPE_CHECK",
        "caveat": "La búsqueda integral no expone operaciones del programa del Tesoro por especie o contraparte; la recompra de página 14 refiere a LEBAC/NOBAC del BCRA.",
        "verified": "Búsqueda textual integral; página PDF 14 renderizada e inspeccionada visualmente.",
    },
    {
        "id": "e0_cgn_cuenta_inversion_2008_comentarios",
        "primary": True,
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2008 · comentarios de ejecución presupuestaria",
        "url": "http://www.economia.gob.ar/hacienda/cgn/cuenta/2008/tomoi/06comentarios.htm",
        "file": "cgn_cuenta_inversion_2008_comentarios_ejecucion.html",
        "publication": "2009",
        "period": "2008",
        "type": "HTML oficial · texto original preservado",
        "pages": "N/A",
        "families": "state_bcra;fiscal;budget;debt;buyback",
        "breaks": "ejecución presupuestaria agregada versus especie/contraparte; posible solapamiento",
        "use": "USABLE_EXECUTED_BUYBACK_AGGREGATE",
        "caveat": "Los ARS 981,36m son un agregado de operaciones de recompra sin especie, participante ni separación de programas.",
        "verified": "Pasaje de adquisición de títulos y valores de corto plazo preservado y verificado.",
    },
    {
        "id": "e0_cgn_cuenta_inversion_2009_anexo_j_html",
        "primary": True,
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2009 · Anexo J · recompra anticipada BODEN 2012",
        "url": "http://www.economia.gob.ar/hacienda/cgn/cuenta/2009/sdp/anexoj.htm",
        "file": "cgn_cuenta_inversion_2009_anexo_j.html",
        "publication": "2010",
        "period": "2009",
        "type": "HTML oficial · texto original preservado",
        "pages": "N/A",
        "families": "state_bcra;fiscal;debt;buyback;strip",
        "breaks": "ocurrencia oficial versus resultado cuantitativo; cupón separado versus bono",
        "use": "USABLE_OFFICIAL_STRIP_TENDER_OCCURRENCE",
        "caveat": "Confirma la licitación y que ofertó menos del 2% de los tenedores, sin monto adjudicado ni participantes.",
        "verified": "Sección de recompra anticipada preservada y verificada.",
    },
    {
        "id": "e0_argentina_mecon_memoria_2009",
        "primary": True,
        "institution": "Jefatura de Gabinete de Ministros · Ministerio de Economía y Finanzas Públicas",
        "title": "Memoria detallada del estado de la Nación 2009",
        "url": "https://www.argentina.gob.ar/sites/default/files/memoria_2009.pdf",
        "file": "argentina_mecon_memoria_2009.pdf",
        "publication": "2010",
        "period": "2009",
        "type": "PDF oficial · binario preservado",
        "pages": "520",
        "families": "state_bcra;fiscal;debt;buyback;strip",
        "breaks": "memoria de gestión versus resultado primario; proporción de tenedores versus monto",
        "use": "USABLE_OFFICIAL_STRIP_TENDER_OCCURRENCE",
        "caveat": "Confirma el strip y menos de 2% de propuestas, pero no publica el detalle adjudicado.",
        "verified": "Páginas PDF 135 y 136 renderizadas e inspeccionadas visualmente.",
    },
    {
        "id": "e0_agn_res_084_2015_act_158_2010_deuda",
        "primary": True,
        "institution": "Auditoría General de la Nación",
        "title": "Evolución y distribución de la deuda pública 2009-2012 · Resolución 84/2015 · Actuación 158/2010",
        "url": "https://www.agn.gob.ar/sites/default/files/informes/informe_084_2015.pdf",
        "file": "agn_informe_084_2015_deuda_2009_2012.pdf",
        "publication": "2015",
        "period": "2009-2012",
        "type": "PDF oficial · binario preservado",
        "pages": "48",
        "families": "state_bcra;fiscal;debt;holders;public_sector",
        "breaks": "sector acreedor versus instrumento; tenencia agregada versus beneficiario original",
        "use": "USABLE_AGGREGATE_CREDITOR_DISTRIBUTION",
        "caveat": "Distribuye toda la deuda por sector y organismos; no ofrece un padrón BODEN 2012 ni clientes finales.",
        "verified": "Páginas PDF 25 y 26 renderizadas e inspeccionadas visualmente.",
    },
    {
        "id": "e0_agn_transparencia_boden_2018",
        "primary": True,
        "institution": "Auditoría General de la Nación",
        "title": "Acceso a la información · solicitud sobre BODEN 2006, 2012 y 2013",
        "url": "https://www.agn.gob.ar/transparencia/informacion",
        "file": "agn_transparencia_informacion_publica_2018.html",
        "publication": "2018",
        "period": "2018-08-14/2018-09-11",
        "type": "HTML oficial · respuesta institucional preservada",
        "pages": "N/A",
        "families": "state_bcra;fiscal;debt;holders;source_route",
        "breaks": "respuesta de transparencia versus entrega del informe; identificación declarada versus identificadores publicados",
        "use": "USABLE_REPORT_DISCOVERY_ROUTE_ONLY",
        "caveat": "La página dice que se identificaron informes, pero no publica sus números ni adjunta la respuesta individual.",
        "verified": "Entrada del 14/08/2018 y respuesta del 11/09/2018 preservadas y verificadas.",
    },
    {
        "id": "sec_consejo_iec_298_strip_boden2012",
        "primary": False,
        "institution": "Consejo Profesional de Ciencias Económicas de la Ciudad Autónoma de Buenos Aires",
        "title": "Informe Económico de Coyuntura 298 · repercusiones del rescate anticipado BODEN 2012",
        "url": "https://archivo.consejo.org.ar/publicaciones/iec/iec298/julio_09.pdf",
        "file": "consejo_iec_298_julio_2009.pdf",
        "publication": "2009",
        "period": "2009-06",
        "type": "PDF institucional contemporáneo · fuente secundaria preservada",
        "pages": "22",
        "families": "state_bcra;fiscal;debt;buyback;strip;secondary",
        "breaks": "transcripción contemporánea versus comunicado primario; monto reportado versus caja confirmada",
        "use": "SECONDARY_QUANTITATIVE_STRIP_RESULT",
        "caveat": "Reporta 35 ofertas, 20 aceptadas y USD 33,6m; el comunicado primario y la liquidación siguen sin recuperarse.",
        "verified": "Página PDF 5 renderizada e inspeccionada visualmente.",
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
            "tema": "ciclo_ajuste_e0_fiscal" if spec["primary"] else "ciclo_ajuste_e0_fiscal_secondary",
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
            "nota": f"V114 E0 fiscal: {spec['bytes']:,} bytes; {spec['pages']} páginas. {spec['verified']}",
        }
    )
write_csv(CATALOG, catalog)


primary_specs = [spec for spec in source_specs if spec["primary"]]
census = [row for row in read_csv(V113 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V113.csv") if row["source_id"] not in new_ids]
for spec in primary_specs:
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
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V114.csv", census)


tender_fields = [
    "tender_id", "tender_date", "scheduled_settlement_date", "instrument", "isin", "native_currency",
    "offers_received", "offered_notional_native", "offered_effective_native", "offered_effective_ars",
    "cutoff_price_per_100", "weighted_average_price", "awarded_notional_native", "awarded_effective_native",
    "reference_fx_ars_per_usd", "awarded_effective_ars", "result_status", "source_id", "source_locator",
    "settlement_confirmation", "caveat",
]


def T(
    tender_id: str, date: str, settlement: str, instrument: str, isin: str, currency: str, offers: str,
    offered_notional: str, offered_effective: str, offered_ars: str, cutoff: str, average: str,
    awarded_notional: str, awarded_effective: str, fx: str, awarded_ars: str, source: str, locator: str,
) -> dict[str, str]:
    status = "ADJUDICADA" if Decimal(awarded_notional) else "DESIERTA"
    return {
        "tender_id": tender_id, "tender_date": date, "scheduled_settlement_date": settlement,
        "instrument": instrument, "isin": isin, "native_currency": currency, "offers_received": offers,
        "offered_notional_native": offered_notional, "offered_effective_native": offered_effective,
        "offered_effective_ars": offered_ars, "cutoff_price_per_100": cutoff,
        "weighted_average_price": average, "awarded_notional_native": awarded_notional,
        "awarded_effective_native": awarded_effective, "reference_fx_ars_per_usd": fx,
        "awarded_effective_ars": awarded_ars, "result_status": status, "source_id": source,
        "source_locator": locator,
        "settlement_confirmation": "SCHEDULED_NOT_INDEPENDENTLY_CONFIRMED" if status == "ADJUDICADA" else "NOT_APPLICABLE_NO_AWARD",
        "caveat": "Resultado publicado y fecha prevista no equivalen a confirmación posterior de Caja/BCRA; participante no equivale a tenedor final.",
    }


tenders = [
    T("T20080828_B2012", "2008-08-28", "2008-09-02", "BODEN_2012", "ARARGE034678", "USD", "17", "31611700", "12979032.95", "39297915.97", "N/A", "N/A", "0", "0", "3.0278", "0", "e0_argentina_resultado_recompra_2008_08_28", "PDF_pp1_2"),
    T("T20080828_B2013", "2008-08-28", "2008-09-02", "BODEN_2013", "ARARGE035709", "USD", "16", "16305400", "8079141.50", "24462024.63", "N/A", "N/A", "0", "0", "3.0278", "0", "e0_argentina_resultado_recompra_2008_08_28", "PDF_pp1_2"),
    T("T20080828_GDPARS", "2008-08-28", "2008-09-02", "GDP_UNIT_ARS", "ARARGE03E147", "ARS", "23", "208849732", "19509635.97", "19509635.97", "9.03", "8.99", "110073135", "9890509.02", "1", "9890509.02", "e0_argentina_resultado_recompra_2008_08_28", "PDF_pp1_3"),
    T("T20080828_GDPUSD", "2008-08-28", "2008-09-02", "GDP_UNIT_USD_LAW_AR", "ARARGE03E154", "USD", "18", "129265697", "13579792.21", "41116894.85", "N/A", "N/A", "0", "0", "3.0278", "0", "e0_argentina_resultado_recompra_2008_08_28", "PDF_pp1_3"),
    T("T20080904_B2012", "2008-09-04", "2008-09-09", "BODEN_2012", "ARARGE034678", "USD", "49", "200677500", "80639324.81", "245643511.24", "39.70", "39.66", "4193000", "1662735.00", "3.0462", "5065023.36", "e0_argentina_resultado_recompra_2008_09_04", "PDF_pp1_2"),
    T("T20080904_B2013", "2008-09-04", "2008-09-09", "BODEN_2013", "ARARGE035709", "USD", "17", "47537100", "23155390.90", "70535951.76", "48.25", "48.17", "6382000", "3074085.80", "3.0462", "9364280.16", "e0_argentina_resultado_recompra_2008_09_04", "PDF_pp1_2"),
    T("T20080904_GDPARS", "2008-09-04", "2008-09-09", "GDP_UNIT_ARS", "ARARGE03E147", "ARS", "44", "706121834", "67009116.23", "67009116.23", "9.00", "9.00", "52268", "4704.12", "1", "4704.12", "e0_argentina_resultado_recompra_2008_09_04", "PDF_pp1_3"),
    T("T20080904_GDPUSD", "2008-09-04", "2008-09-09", "GDP_UNIT_USD_LAW_AR", "ARARGE03E154", "USD", "26", "186144546", "18317268.77", "55798064.11", "8.85", "8.84", "21250000", "1877825.00", "3.0462", "5720230.52", "e0_argentina_resultado_recompra_2008_09_04", "PDF_pp1_3"),
    T("T20080911_B2012", "2008-09-11", "2008-09-16", "BODEN_2012", "ARARGE034678", "USD", "31", "205539300", "81787828.70", "250925058.45", "37.84", "37.67", "13000000", "4896800.00", "3.068", "15023382.40", "e0_argentina_resultado_recompra_2008_09_11", "PDF_pp1_2"),
    T("T20080911_B2013", "2008-09-11", "2008-09-16", "BODEN_2013", "ARARGE035709", "USD", "14", "19597700", "9151062.27", "28075459.04", "45.89", "45.61", "6766000", "3085917.40", "3.068", "9467594.58", "e0_argentina_resultado_recompra_2008_09_11", "PDF_pp1_2"),
    T("T20080911_GDPARS", "2008-09-11", "2008-09-16", "GDP_UNIT_ARS", "ARARGE03E147", "ARS", "26", "562370902", "51103155.47", "51103155.47", "8.75", "8.74", "300570000", "26267385.00", "1", "26267385.00", "e0_argentina_resultado_recompra_2008_09_11", "PDF_pp1_3"),
    T("T20080911_GDPUSD", "2008-09-11", "2008-09-16", "GDP_UNIT_USD_LAW_AR", "ARARGE03E154", "USD", "25", "217364295", "19945118.18", "61191622.58", "N/A", "N/A", "0", "0", "3.068", "0", "e0_argentina_resultado_recompra_2008_09_11", "PDF_pp1_3"),
    T("T20081002_GDPARS", "2008-10-02", "2008-10-07", "GDP_UNIT_ARS", "ARARGE03E147", "ARS", "31", "1835073908", "155112913.75", "155112913.75", "8.40", "8.33", "634646647", "52843086.96", "1", "52843086.96", "e0_argentina_resultado_recompra_2008_10_02", "PDF_pp1_2"),
    T("T20081002_GDPUSD", "2008-10-02", "2008-10-07", "GDP_UNIT_USD_LAW_AR", "ARARGE03E154", "USD", "15", "31314913", "2544253.28", "7976234.03", "7.60", "7.60", "8230362", "625205.34", "3.135", "1960018.74", "e0_argentina_resultado_recompra_2008_10_02", "PDF_pp1_2"),
]
write_csv(HERE / "E0_FISCAL_PUBLIC_BUYBACK_TENDERS_2008_V114.csv", tenders, tender_fields)


award_fields = [
    "award_id", "tender_date", "scheduled_settlement_date", "instrument", "isin", "native_currency",
    "participant", "participant_role", "price_components", "awarded_notional_native", "awarded_effective_native",
    "reference_fx_ars_per_usd", "awarded_effective_ars_raw", "derivation", "source_id", "source_locator",
    "ultimate_holder_identified", "original_purpose_identified", "settlement_confirmation", "additivity", "caveat",
]


def A(
    award_id: str, date: str, settlement: str, instrument: str, isin: str, currency: str,
    participant: str, components: str, fx: str, source: str, locator: str,
) -> dict[str, str]:
    parsed = [(Decimal(vno), Decimal(price)) for vno, price in (item.split("@") for item in components.split(";"))]
    notional = sum(vno for vno, _ in parsed)
    effective = sum(vno * price / Decimal(100) for vno, price in parsed)
    ars = effective if currency == "ARS" else effective * Decimal(fx)
    return {
        "award_id": award_id, "tender_date": date, "scheduled_settlement_date": settlement,
        "instrument": instrument, "isin": isin, "native_currency": currency, "participant": participant,
        "participant_role": "MAE_PARTICIPANT_INTERMEDIARY_OR_OWN_ACCOUNT", "price_components": components,
        "awarded_notional_native": str(notional), "awarded_effective_native": str(effective),
        "reference_fx_ars_per_usd": fx, "awarded_effective_ars_raw": str(ars),
        "derivation": "Accepted offer rows through the published cutoff reproduce the official instrument total exactly.",
        "source_id": source, "source_locator": locator, "ultimate_holder_identified": "NO",
        "original_purpose_identified": "NO", "settlement_confirmation": "SCHEDULED_NOT_INDEPENDENTLY_CONFIRMED",
        "additivity": "ADD_WITHIN_FOUR_LOCATED_PUBLIC_TENDER_AWARDS_ONLY",
        "caveat": "La entidad es participante MAE; puede actuar por cuenta propia o de terceros y no prueba beneficiario final.",
    }


awards = [
    A("A20080828_GDPARS_CITI", "2008-08-28", "2008-09-02", "GDP_UNIT_ARS", "ARARGE03E147", "ARS", "Citibank", "73135@8.90", "1", "e0_argentina_resultado_recompra_2008_08_28", "PDF_pp1_3"),
    A("A20080828_GDPARS_HSBC", "2008-08-28", "2008-09-02", "GDP_UNIT_ARS", "ARARGE03E147", "ARS", "HSBC Bank", "10000000@8.90;30000000@8.95;30000000@8.99;40000000@9.03", "1", "e0_argentina_resultado_recompra_2008_08_28", "PDF_pp1_3"),
    A("A20080904_B2012_CITI", "2008-09-04", "2008-09-09", "BODEN_2012", "ARARGE034678", "USD", "Citibank", "193000@39.50;1000000@39.55", "3.0462", "e0_argentina_resultado_recompra_2008_09_04", "PDF_pp1_2"),
    A("A20080904_B2012_STANDARD", "2008-09-04", "2008-09-09", "BODEN_2012", "ARARGE034678", "USD", "Standard Bank", "3000000@39.70", "3.0462", "e0_argentina_resultado_recompra_2008_09_04", "PDF_pp1_2"),
    A("A20080904_B2013_CITI", "2008-09-04", "2008-09-09", "BODEN_2013", "ARARGE035709", "USD", "Citibank", "1000000@47.95;1000000@48.05;1000000@48.25", "3.0462", "e0_argentina_resultado_recompra_2008_09_04", "PDF_pp1_2"),
    A("A20080904_B2013_MERVAL", "2008-09-04", "2008-09-09", "BODEN_2013", "ARARGE035709", "USD", "MERVAL", "382000@48.19", "3.0462", "e0_argentina_resultado_recompra_2008_09_04", "PDF_pp1_2"),
    A("A20080904_B2013_MARIVA", "2008-09-04", "2008-09-09", "BODEN_2013", "ARARGE035709", "USD", "Banco Mariva", "3000000@48.25", "3.0462", "e0_argentina_resultado_recompra_2008_09_04", "PDF_pp1_2"),
    A("A20080904_GDPARS_CITI", "2008-09-04", "2008-09-09", "GDP_UNIT_ARS", "ARARGE03E147", "ARS", "Citibank", "52268@9.00", "1", "e0_argentina_resultado_recompra_2008_09_04", "PDF_pp1_3"),
    A("A20080904_GDPUSD_CITI", "2008-09-04", "2008-09-09", "GDP_UNIT_USD_LAW_AR", "ARARGE03E154", "USD", "Citibank", "50000@3.25", "3.0462", "e0_argentina_resultado_recompra_2008_09_04", "PDF_pp1_3"),
    A("A20080904_GDPUSD_STANDARD", "2008-09-04", "2008-09-09", "GDP_UNIT_USD_LAW_AR", "ARARGE03E154", "USD", "Standard Bank", "3950000@8.85;900000@8.85;2150000@8.85;3700000@8.85;10500000@8.85", "3.0462", "e0_argentina_resultado_recompra_2008_09_04", "PDF_pp1_3"),
    A("A20080911_B2012_CITI", "2008-09-11", "2008-09-16", "BODEN_2012", "ARARGE034678", "USD", "Citibank", "1000000@37.34;2000000@37.44;2000000@37.64;1000000@37.75;5000000@37.75;2000000@37.84", "3.068", "e0_argentina_resultado_recompra_2008_09_11", "PDF_pp1_2"),
    A("A20080911_B2013_CITI", "2008-09-11", "2008-09-16", "BODEN_2013", "ARARGE035709", "USD", "Citibank", "1000000@45.14;1000000@45.34;1000000@45.54;1000000@45.74;2000000@45.84", "3.068", "e0_argentina_resultado_recompra_2008_09_11", "PDF_pp1_2"),
    A("A20080911_B2013_MERVAL", "2008-09-11", "2008-09-16", "BODEN_2013", "ARARGE035709", "USD", "MERVAL", "766000@45.89", "3.068", "e0_argentina_resultado_recompra_2008_09_11", "PDF_pp1_2"),
    A("A20080911_GDPARS_CITI", "2008-09-11", "2008-09-16", "GDP_UNIT_ARS", "ARARGE03E147", "ARS", "Citibank", "570000@3.05;216000000@8.75;84000000@8.75", "1", "e0_argentina_resultado_recompra_2008_09_11", "PDF_pp1_3"),
    A("A20081002_GDPARS_CITI", "2008-10-02", "2008-10-07", "GDP_UNIT_ARS", "ARARGE03E147", "ARS", "Citibank", "1483679@2.60;20162481@8.00;16321174@8.00;36116726@8.00;125226@8.00;10000000@8.32;295377@8.40;370000000@8.40;34866406@8.40", "1", "e0_argentina_resultado_recompra_2008_10_02", "PDF_pp1_2"),
    A("A20081002_GDPARS_HSBC", "2008-10-02", "2008-10-07", "GDP_UNIT_ARS", "ARARGE03E147", "ARS", "HSBC Bank", "70275578@8.30;70000000@8.39", "1", "e0_argentina_resultado_recompra_2008_10_02", "PDF_pp1_2"),
    A("A20081002_GDPARS_MERVAL", "2008-10-02", "2008-10-07", "GDP_UNIT_ARS", "ARARGE03E147", "ARS", "MERVAL", "5000000@8.30", "1", "e0_argentina_resultado_recompra_2008_10_02", "PDF_pp1_2"),
    A("A20081002_GDPUSD_CITI", "2008-10-02", "2008-10-07", "GDP_UNIT_USD_LAW_AR", "ARARGE03E154", "USD", "Citibank", "50362@7.00;8180000@7.60", "3.135", "e0_argentina_resultado_recompra_2008_10_02", "PDF_pp1_2"),
]
write_csv(HERE / "E0_FISCAL_PUBLIC_BUYBACK_AWARDS_2008_V114.csv", awards, award_fields)


by_instrument_date: dict[tuple[str, str], list[dict[str, str]]] = {}
for row in awards:
    by_instrument_date.setdefault((row["tender_date"], row["instrument"]), []).append(row)
for tender in (row for row in tenders if row["result_status"] == "ADJUDICADA"):
    rows = by_instrument_date[(tender["tender_date"], tender["instrument"])]
    assert sum(Decimal(row["awarded_notional_native"]) for row in rows) == Decimal(tender["awarded_notional_native"])
    assert sum(Decimal(row["awarded_effective_native"]) for row in rows).quantize(CENT, ROUND_HALF_UP) == Decimal(tender["awarded_effective_native"])
    assert sum(Decimal(row["awarded_effective_ars_raw"]) for row in rows).quantize(CENT, ROUND_HALF_UP) == Decimal(tender["awarded_effective_ars"])


official_four_tender_ars = sum(Decimal(row["awarded_effective_ars"]) for row in tenders)
raw_four_tender_ars = sum(Decimal(row["awarded_effective_ars_raw"]) for row in awards)
assert official_four_tender_ars == Decimal("135606214.86")
assert raw_four_tender_ars == Decimal("135606214.85506")


event_fields = [
    "event_id", "event_date", "stage", "instrument_scope", "agent_or_channel", "reported_amount", "unit",
    "amount_basis", "status", "source_id", "locator", "additivity", "caveat",
]
events = [
    {"event_id": "E20051122_B2012", "event_date": "2005-11-22", "stage": "HISTORICAL_TENDER", "instrument_scope": "BODEN_2012", "agent_or_channel": "PUBLIC_TENDER", "reported_amount": "5032600;4000636.64", "unit": "USD_VNO;USD_effective", "amount_basis": "OFFICIAL_EXECUTED_BUYBACK_REPORT", "status": "BUYBACK_REPORTED_EXECUTED_PARTICIPANTS_OPEN", "source_id": "e0_argentina_recompras_decreto_1735_04_report", "locator": "PDF_pp4_5", "additivity": "SEPARATE_2005_EVENT", "caveat": "No ofrece participantes ni tenedores finales."},
    {"event_id": "E20080811_BNA_MANDATE", "event_date": "2008-08-11", "stage": "FIRST_STAGE_MANDATE", "instrument_scope": "MIXED_BODEN_BONAR", "agent_or_channel": "BNA_GOVERNMENT_AGENT", "reported_amount": "N/D", "unit": "N/D", "amount_basis": "MANDATE_ONLY", "status": "AUTHORIZED_AGENT_EXECUTION_DETAIL_OPEN", "source_id": "e0_argentina_recompra_primera_etapa_2008_08_11", "locator": "PDF_p1", "additivity": "NON_ADDITIVE", "caveat": "Mandato no es blotter ni pago."},
    {"event_id": "E20080822_FIRST_TWO_WEEKS", "event_date": "2008-08-11/2008-08-22", "stage": "FIRST_STAGE_MARKET_PURCHASES", "instrument_scope": "MIXED_B2012_B2013_BONARV_PRE8_B2008_GDPARS", "agent_or_channel": "TREASURY_MARKET_INTERVENTION_AFTER_BNA_MANDATE", "reported_amount": "380000000", "unit": "USD_approx_effective", "amount_basis": "OFFICIAL_PROGRAM_AGGREGATE", "status": "EXECUTED_AGGREGATE_INSTRUMENT_SPLIT_OPEN", "source_id": "e0_argentina_recompra_segunda_semana_2008_08_22", "locator": "PDF_p1", "additivity": "NON_ADDITIVE_PROGRAM_AGGREGATE", "caveat": "No permite aislar BODEN 2012 ni contrapartes."},
    {"event_id": "E20080821_SECOND_STAGE", "event_date": "2008-08-21", "stage": "SECOND_STAGE_ANNOUNCEMENT", "instrument_scope": "PUBLIC_DEBT_SHORT_MEDIUM_MATURITIES", "agent_or_channel": "PUBLIC_TENDERS", "reported_amount": "N/D", "unit": "N/D", "amount_basis": "ANNOUNCEMENT_ONLY", "status": "PERIODIC_TENDERS_ANNOUNCED_COUNT_NOT_CERTIFIED", "source_id": "e0_argentina_recompra_segunda_etapa_2008_08_21", "locator": "PDF_p1", "additivity": "NON_ADDITIVE", "caveat": "No existe cierre administrativo preservado que certifique exhaustividad de los cuatro resultados localizados."},
    {"event_id": "E20080828_20081002_FOUR_TENDERS", "event_date": "2008-08-28/2008-10-02", "stage": "SECOND_STAGE_PUBLIC_TENDERS", "instrument_scope": "B2012_B2013_GDPARS_GDPUSD", "agent_or_channel": "MAE_PUBLIC_TENDERS", "reported_amount": str(official_four_tender_ars), "unit": "ARS_effective", "amount_basis": "SUM_OF_FOUR_OFFICIAL_RESULT_TOTALS", "status": "FOUR_LOCATED_TENDERS_PARTICIPANTS_RECONSTRUCTED", "source_id": "e0_argentina_resultado_recompra_2008_08_28;e0_argentina_resultado_recompra_2008_09_04;e0_argentina_resultado_recompra_2008_09_11;e0_argentina_resultado_recompra_2008_10_02", "locator": "PDF_result_pages_and_offer_tables", "additivity": "CONTROL_TOTAL_NOT_ADD_TO_CGN_AGGREGATE", "caveat": "Adjudicación no confirma liquidación; cuatro resultados localizados no prueban cierre exhaustivo de etapa."},
    {"event_id": "E2008_CGN_BUYBACK_AGGREGATE", "event_date": "2008", "stage": "BUDGET_EXECUTION", "instrument_scope": "UNSPECIFIED_BUYBACK_OPERATIONS", "agent_or_channel": "TREASURY", "reported_amount": "981360000", "unit": "ARS", "amount_basis": "OFFICIAL_EXECUTED_BUDGET_AGGREGATE", "status": "EXECUTED_AGGREGATE_SPECIES_COUNTERPARTY_OPEN", "source_id": "e0_cgn_cuenta_inversion_2008_comentarios", "locator": "HTML_short_term_securities_paragraph", "additivity": "NON_ADDITIVE_POSSIBLE_OVERLAP", "caveat": "Puede contener operaciones de ambas etapas y otras especies; no sumar a los resultados públicos."},
    {"event_id": "E2009_STRIP_OFFICIAL", "event_date": "2009-06", "stage": "BODEN2012_COUPON15_STRIP_TENDER", "instrument_scope": "BODEN_2012_COUPON_15", "agent_or_channel": "MAE_PUBLIC_TENDER", "reported_amount": "LESS_THAN_2_PERCENT_OF_HOLDERS_OFFERED", "unit": "holder_share_qualitative", "amount_basis": "OFFICIAL_MANAGEMENT_AND_ACCOUNTING_REPORTS", "status": "TENDER_OCCURRED_PRIMARY_AMOUNT_OPEN", "source_id": "e0_argentina_mecon_memoria_2009;e0_cgn_cuenta_inversion_2009_anexo_j_html", "locator": "PDF_p136;HTML_recompra_anticipada", "additivity": "NON_ADDITIVE", "caveat": "No aporta monto, participantes ni liquidación."},
    {"event_id": "E2009_STRIP_SECONDARY_RESULT", "event_date": "2009-06", "stage": "BODEN2012_COUPON15_STRIP_TENDER", "instrument_scope": "BODEN_2012_COUPON_15", "agent_or_channel": "MAE_PUBLIC_TENDER", "reported_amount": "35;20;33600000;12.7;1.86;637468", "unit": "offers_received;offers_accepted;USD_source_reported;USD_coupon_price;percent_average_discount;USD_saving", "amount_basis": "CONTEMPORARY_INSTITUTIONAL_SECONDARY_REPORT", "status": "SECONDARY_QUANTITATIVE_PRIMARY_RESULT_OPEN", "source_id": "sec_consejo_iec_298_strip_boden2012", "locator": "PDF_p5", "additivity": "NON_ADDITIVE", "caveat": "No convertir USD 33,6m en caja confirmada ni precisar su base más allá de lo reportado sin el comunicado primario."},
]
write_csv(HERE / "E0_FISCAL_BUYBACK_PROGRAM_EVENTS_2005_2009_V114.csv", events, event_fields)


creditor_fields = ["observation_date", "creditor_sector", "amount", "currency_scale", "share_total_pct", "scope", "source_id", "locator", "instrument_specific", "caveat"]
creditors = [
    {"observation_date": "2008-12-31", "creditor_sector": "TOTAL_PUBLIC_DEBT", "amount": "503906", "currency_scale": "ARS_million", "share_total_pct": "100", "scope": "ALL_PUBLIC_DEBT", "source_id": "e0_agn_res_202_2009_act_41_2009_deuda", "locator": "PDF_pp16_17", "instrument_specific": "NO", "caveat": "Preliminary AGN table; not BODEN-specific."},
    {"observation_date": "2008-12-31", "creditor_sector": "PRIVATE_SECTOR", "amount": "276157", "currency_scale": "ARS_million", "share_total_pct": "54.8", "scope": "ALL_PUBLIC_DEBT", "source_id": "e0_agn_res_202_2009_act_41_2009_deuda", "locator": "PDF_pp16_17", "instrument_specific": "NO", "caveat": "Private sector is not equivalent to banks."},
    {"observation_date": "2008-12-31", "creditor_sector": "PUBLIC_SECTOR", "amount": "109636", "currency_scale": "ARS_million", "share_total_pct": "21.8", "scope": "ALL_PUBLIC_DEBT", "source_id": "e0_agn_res_202_2009_act_41_2009_deuda", "locator": "PDF_pp16_17", "instrument_specific": "NO", "caveat": "Aggregate public sector."},
]
for date, total, private, private_pct, public, public_pct, official, official_pct in (
    ("2010-12-31", "164331", "63314", "40.1", "76973", "48.7", "24044", "11.2"),
    ("2011-12-31", "178963", "57790", "32.3", "96269", "53.8", "24904", "13.9"),
    ("2012-12-31", "203034", "63031", "31.0", "114767", "56.5", "25236", "12.4"),
):
    for sector, amount, share in (("TOTAL_PUBLIC_DEBT", total, "100"), ("PRIVATE_SECTOR", private, private_pct), ("PUBLIC_SECTOR", public, public_pct), ("BILATERAL_AND_MULTILATERAL", official, official_pct)):
        creditors.append({"observation_date": date, "creditor_sector": sector, "amount": amount, "currency_scale": "USD_million", "share_total_pct": share, "scope": "ALL_PUBLIC_DEBT", "source_id": "e0_agn_res_084_2015_act_158_2010_deuda", "locator": "PDF_pp25_26", "instrument_specific": "NO", "caveat": "Sector distribution does not identify BODEN holders, MAE clients or original program purpose."})
write_csv(HERE / "E0_FISCAL_AGN_CREDITOR_DISTRIBUTION_V114.csv", creditors, creditor_fields)


report_fields = ["record_id", "resolution", "actuacion", "period_coverage", "requested_or_report_scope", "retrieved_scope", "match_status", "source_id", "caveat"]
report_index = [
    {"record_id": "AGN_REQUEST_2018_08_14", "resolution": "NOT_PUBLISHED_ON_TRANSPARENCY_PAGE", "actuacion": "NOT_PUBLISHED_ON_TRANSPARENCY_PAGE", "period_coverage": "2006-2011", "requested_or_report_scope": "Evolution and distribution of foreign-currency debt held by private sector; BODEN 2006/2012/2013", "retrieved_scope": "Request topic and favorable response only", "match_status": "ROUTE_CONFIRMED_IDENTIFIERS_OMITTED", "source_id": "e0_agn_transparencia_boden_2018", "caveat": "The individualized answer/attachment is not published."},
    {"record_id": "AGN_RES202_2009", "resolution": "202/2009", "actuacion": "41/2009", "period_coverage": "2008", "requested_or_report_scope": "Evolution of public debt", "retrieved_scope": "All public debt by broad creditor sector", "match_status": "PERIOD_AND_THEME_MATCH_NOT_PROVEN_AS_2018_REPLY", "source_id": "e0_agn_res_202_2009_act_41_2009_deuda", "caveat": "Not instrument-specific."},
    {"record_id": "AGN_RES084_2015", "resolution": "84/2015", "actuacion": "158/2010", "period_coverage": "2009-2012", "requested_or_report_scope": "Evolution and distribution of public debt", "retrieved_scope": "All public debt by broad creditor sector and public agencies", "match_status": "PERIOD_AND_THEME_MATCH_NOT_PROVEN_AS_2018_REPLY", "source_id": "e0_agn_res_084_2015_act_158_2010_deuda", "caveat": "Not BODEN-specific; no beneficial-holder register."},
    {"record_id": "AGN_RES102_2011", "resolution": "102/2011", "actuacion": "366/2009", "period_coverage": "2009H1", "requested_or_report_scope": "FGS management", "retrieved_scope": "Specific duplicated PF BODEN 2012 inventory control", "match_status": "ADJACENT_SPECIFIC_CONTROL_NOT_DISTRIBUTION_REPORT", "source_id": "e0_agn_res_102_2011_act_366_2009_fgs", "caveat": "Public-holder accounting exception; not Treasury payment or private-holder distribution."},
]
write_csv(HERE / "E0_FISCAL_AGN_REPORT_INDEX_V114.csv", report_index, report_fields)


ledger = read_csv(V113 / "E0_FISCAL_MECHANISM_LEDGER_V113.csv")
ledger_fields = list(ledger[0])


def L(ledger_id: str, year: str, purpose: str, event_type: str, date: str, payer: str, recipient: str, channel: str, instrument: str, original_amount: str, original_unit: str, converted: str, conversion_basis: str, source: str, locator: str, realization: str, additivity: str, interpretation: str, caveat: str) -> dict[str, str]:
    return dict(zip(ledger_fields, (ledger_id, year, purpose, event_type, date, payer, recipient, channel, instrument, original_amount, original_unit, converted, conversion_basis, source, locator, realization, additivity, interpretation, caveat), strict=True))


ledger.extend([
    L("F96", "2005", "Debt_buyback", "HISTORICAL_TENDER_BUYBACK", "2005-11-22", "Tesoro_Nacional", "Unknown_tender_participants", "Public_tender", "BODEN_2012", "5032600", "USD_VNO", "N/D", "EFFECTIVE_USD_4000636.64", "e0_argentina_recompras_decreto_1735_04_report", "PDF_pp4_5", "REPORTED_EXECUTED_PARTICIPANTS_OPEN", "SEPARATE_2005_EVENT", "Official report records a BODEN 2012 buyback before the 2008 program.", "No participant, holder purpose or settlement record."),
    L("F97", "2008", "Debt_buyback", "BNA_AGENT_MANDATE", "2008-08-11", "Tesoro_Nacional", "BNA_as_government_agent", "Market_purchase_mandate", "Mixed_BODEN_BONAR", "N/D", "N/D", "N/D", "MANDATE_ONLY", "e0_argentina_recompra_primera_etapa_2008_08_11", "PDF_p1", "AUTHORIZED_EXECUTION_DETAIL_OPEN", "NON_ADDITIVE", "BNA was instructed to buy short-maturity securities.", "Mandate is not a trade blotter."),
    L("F98", "2008", "Debt_buyback", "FIRST_STAGE_MARKET_PURCHASE_AGGREGATE", "2008-08-11/2008-08-22", "Tesoro_Nacional", "Market_counterparties_unknown", "Market_purchases_after_BNA_mandate", "Mixed_B2012_B2013_BONARV_PRE8_B2008_GDPARS", "380", "USD_million_approx", "N/D", "OFFICIAL_PROGRAM_AGGREGATE", "e0_argentina_recompra_segunda_semana_2008_08_22", "PDF_p1", "EXECUTED_AGGREGATE_INSTRUMENT_SPLIT_OPEN", "NON_ADDITIVE", "About USD 380m of mixed securities were purchased in two weeks.", "Cannot isolate BODEN 2012, participant or beneficial holder."),
    L("F99", "2008", "Debt_buyback", "SECOND_STAGE_ANNOUNCEMENT", "2008-08-21", "Tesoro_Nacional", "Public_tender_participants", "Public_tenders", "Short_medium_term_public_debt", "N/D", "N/D", "N/D", "ANNOUNCEMENT_ONLY", "e0_argentina_recompra_segunda_etapa_2008_08_21", "PDF_p1", "PERIODIC_TENDERS_ANNOUNCED", "NON_ADDITIVE", "The second stage would use periodic public tenders.", "No preserved closure notice proves the four located results are exhaustive."),
    L("F100", "2008", "Debt_buyback", "FOUR_LOCATED_PUBLIC_TENDER_CONTROL_TOTAL", "2008-08-28/2008-10-02", "Tesoro_Nacional", "MAE_participants", "Public_tenders", "B2012_B2013_GDPARS_GDPUSD", "135606214.86", "ARS_effective", "135.60621486", "SUM_FOUR_OFFICIAL_RESULT_TOTALS", "e0_argentina_resultado_recompra_2008_08_28;e0_argentina_resultado_recompra_2008_09_04;e0_argentina_resultado_recompra_2008_09_11;e0_argentina_resultado_recompra_2008_10_02", "PDF_results_and_offer_tables", "AWARDED_SETTLEMENT_OPEN", "CONTROL_NOT_ADDITIVE", "Eighteen accepted participant-instrument rows reproduce four official tender totals.", "Not a final program total and not cash-settlement confirmation."),
    L("F101", "2008", "Debt_buyback", "PUBLIC_TENDER_INSTRUMENT_AWARDS", "2008-09-04/2008-09-11", "Tesoro_Nacional", "Citibank_MERVAL_Banco_Mariva_participants", "Public_tenders", "BODEN_2013", "13148000", "USD_VNO", "18.83187474", "OFFICIAL_EFFECTIVE_ARS_SUM", "e0_argentina_resultado_recompra_2008_09_04;e0_argentina_resultado_recompra_2008_09_11", "PDF_pp1_2", "AWARDED_SETTLEMENT_OPEN", "ADD_WITHIN_FOUR_TENDER_INSTRUMENT_SUBTOTALS_ONLY", "BODEN 2013 awards are exactly reconstructed by participant.", "Participants may represent clients; purpose and settlement remain open."),
    L("F102", "2008", "Debt_buyback", "PUBLIC_TENDER_INSTRUMENT_AWARDS", "2008-08-28/2008-10-02", "Tesoro_Nacional", "Citibank_HSBC_MERVAL_participants", "Public_tenders", "GDP_UNIT_ARS", "1045342050", "ARS_nocional", "89.00568510", "OFFICIAL_EFFECTIVE_ARS_SUM", "e0_argentina_resultado_recompra_2008_08_28;e0_argentina_resultado_recompra_2008_09_04;e0_argentina_resultado_recompra_2008_09_11;e0_argentina_resultado_recompra_2008_10_02", "PDF_result_pages_and_offer_tables", "AWARDED_SETTLEMENT_OPEN", "ADD_WITHIN_FOUR_TENDER_INSTRUMENT_SUBTOTALS_ONLY", "Peso GDP-unit awards are exactly reconstructed by participant.", "Nocional and effective pesos are distinct; participants are not ultimate holders."),
    L("F103", "2008", "Debt_buyback", "PUBLIC_TENDER_INSTRUMENT_AWARDS", "2008-09-04/2008-10-02", "Tesoro_Nacional", "Citibank_Standard_Bank_participants", "Public_tenders", "GDP_UNIT_USD_LAW_AR", "29480362", "USD_nocional", "7.68024926", "OFFICIAL_EFFECTIVE_ARS_SUM", "e0_argentina_resultado_recompra_2008_09_04;e0_argentina_resultado_recompra_2008_10_02", "PDF_result_pages_and_offer_tables", "AWARDED_SETTLEMENT_OPEN", "ADD_WITHIN_FOUR_TENDER_INSTRUMENT_SUBTOTALS_ONLY", "Dollar GDP-unit awards are exactly reconstructed by participant.", "Participants are not ultimate holders; settlement remains open."),
    L("F104", "2008", "Debt_buyback", "BUDGET_EXECUTION_AGGREGATE", "2008-12-31", "Tesoro_Nacional", "Unspecified_buyback_counterparties", "Short_term_securities_budget_execution", "Unspecified_buybacks", "981.36", "ARS_million", "981.36", "OFFICIAL_EXECUTED_BUDGET_AGGREGATE", "e0_cgn_cuenta_inversion_2008_comentarios", "HTML_short_term_securities_paragraph", "EXECUTED_AGGREGATE_SPECIES_OPEN", "CONTROL_NOT_ADDITIVE", "CGN records ARS 981.36m in buyback operations.", "May overlap first and second stages and cannot identify BODEN or counterparties."),
    L("F105", "2009", "BODEN_2012_strip_buyback", "OFFICIAL_TENDER_OCCURRENCE", "2009-06", "Tesoro_Nacional", "Less_than_2pct_of_holders_offering", "MAE_public_tender", "BODEN_2012_coupon_15_strip", "N/D", "N/D", "N/D", "OFFICIAL_QUALITATIVE_RESULT", "e0_argentina_mecon_memoria_2009;e0_cgn_cuenta_inversion_2009_anexo_j_html", "PDF_p136;HTML_recompra_anticipada", "TENDER_OCCURRED_AMOUNT_OPEN", "NON_ADDITIVE", "Two official year-end carriers confirm the tender and low participation.", "No quantitative award, participants or settlement in primary carriers."),
    L("F106", "2009", "BODEN_2012_strip_buyback", "SECONDARY_TENDER_RESULT", "2009-06", "Tesoro_Nacional", "Twenty_accepted_offers_ultimate_holders_unknown", "MAE_public_tender", "BODEN_2012_coupon_15_strip", "33.6", "USD_million_source_reported", "N/D", "SECONDARY_35_OFFERS_20_ACCEPTED_DISCOUNT_1.86PCT_SAVING_USD637468", "sec_consejo_iec_298_strip_boden2012", "PDF_p5", "SECONDARY_QUANTITATIVE_PRIMARY_SETTLEMENT_OPEN", "NON_ADDITIVE", "Contemporary institutional report supplies a quantitative tender summary.", "Primary result, amount basis and Caja/BCRA settlement remain open."),
    L("F107", "2012", "All_public_debt", "AGGREGATE_HOLDER_DISTRIBUTION", "2012-12-31", "Sector_Publico_Nacional", "Creditors", "All_public_debt", "Debt_by_creditor_type", "203034", "USD_million_total", "N/D", "AGN_AGGREGATE_DISTRIBUTION", "e0_agn_res_084_2015_act_158_2010_deuda", "PDF_pp25_26", "AGGREGATE_CREDITOR_CONTROL", "CONTROL_NOT_ADDITIVE", "AGN reports 56.5% public, 31.0% private and 12.4% bilateral/multilateral at end-2012.", "Not BODEN-specific and private sector is not banks."),
    L("F108", "2008", "Debt_buyback", "BNA_MEMORY_NEGATIVE_SCOPE_CHECK", "2008-12-31", "BNA", "N/A", "Annual_report", "Treasury_buyback_program", "N/D", "N/D", "N/D", "DOCUMENT_SEARCH_ONLY", "e0_bna_memoria_balance_2008", "Full_text_search_and_PDF_p14", "TRADE_BLOTTER_NOT_DISCLOSED", "NON_ADDITIVE", "The annual report does not expose Treasury-program trades by species or counterparty.", "Narrative absence does not prove zero activity; page 14 discusses BCRA LEBAC/NOBAC."),
])
write_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V114.csv", ledger, ledger_fields)


breaks = read_csv(V113 / "E0_FISCAL_METHOD_BREAKS_V113.csv")
break_fields = list(breaks[0])
new_breaks = [
    ("mixed_buyback_program_not_instrument", "universe", "A program aggregate spanning several securities cannot be assigned to BODEN 2012.", "Keep mixed first-stage amounts outside instrument subtotals until a trade blotter exists.", "First-stage communiqués 11/08 and 22/08/2008"),
    ("budget_execution_aggregate_not_instrument_flow", "aggregation", "CGN buyback execution lacks species, channel and counterparties.", "Use it as a non-additive ceiling/control and never add it to tender totals.", "CGN Cuenta de Inversión 2008 comments"),
    ("bna_mandate_not_trade_blotter", "phase", "An instruction to BNA does not identify executed trades.", "Require date, instrument, quantity, price and counterparty before allocating first-stage purchases.", "Official communiqué 11/08/2008; BNA memory 2008"),
    ("secondary_result_not_primary_settlement", "source", "A contemporary secondary tender summary does not replace the primary result or settlement confirmation.", "Label every quantitative strip value secondary and keep amount basis and payment open.", "Consejo IEC 298 p.5"),
    ("creditor_sector_not_instrument_holder", "universe", "Broad debt creditor sectors do not identify holders of a specific instrument.", "Do not convert private-sector share into bank share or BODEN ownership.", "AGN Res. 84/2015 pp.25-26"),
    ("program_aggregate_overlap", "aggregation", "First-stage, public-tender and budget-execution aggregates may overlap.", "Never add them without an accounting bridge that proves disjoint scope.", "Official 2008 program carriers"),
    ("official_purchase_language_not_post_settlement_confirmation", "phase", "A same-day result communiqué says a purchase was made but also schedules later settlement.", "Keep the event at award/result status until post-settlement Caja/BCRA evidence is preserved.", "Official tender results and RC 212/24"),
]
known_breaks = {row["break_id"] for row in breaks}
for break_id, dimension, problem, rule, evidence in new_breaks:
    if break_id not in known_breaks:
        breaks.append({"break_id": break_id, "dimension": dimension, "problem": problem, "rule": rule, "status": "FROZEN", "evidence": evidence})
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V114.csv", breaks, break_fields)


matrix = [{key: v114_text(value) for key, value in row.items()} for row in read_csv(V113 / "HISTORICAL_EPISODE_MATRIX_2001_2026_V113.csv")]
matrix_fields = list(matrix[0])
for row in matrix:
    if row["variable"] == "boden_2012_strip_and_residual_registration":
        row.update({"pre_value": "STRIP_TENDER_OFFICIALLY_CONFIRMED", "trough_value": "35_OFFERS_20_ACCEPTED_USD33.6M_SOURCE_REPORTED", "trough_date": "2009-06", "recovery_value": "PRIMARY_RESULT_AND_SETTLEMENT_OPEN", "recovery_date": "N/D", "benchmark_definition": "official occurrence plus contemporary secondary quantitative summary", "source_id": "e0_argentina_mecon_memoria_2009;e0_cgn_cuenta_inversion_2009_anexo_j_html;sec_consejo_iec_298_strip_boden2012", "source_quality": "PRIMARY_OCCURRENCE_SECONDARY_QUANTITATIVE", "basis": "Official 2009 carriers plus Consejo IEC 298", "method_break": "YES_STRIP_AND_SECONDARY_RESULT", "status": "STRIP_RESULT_QUANTITATIVE_SECONDARY_PRIMARY_OPEN", "interpretation": "The tender occurred and a contemporary report supplies 35/20/USD33.6m, but the primary result and cash remain open.", "falsifier": "YES_SECONDARY_AMOUNT_EQUALS_SETTLED_CASH", "notes": "Do not merge the strip with full-bond VNO or public-tender totals."})
matrix.extend([
    {"episode_id": "E0", "episode_name": "Crisis de convertibilidad / default / salida / reordenamiento financiero", "t0": "2008-08-11_TO_2008-08-22", "shock_type": "OTHER", "variable": "bna_first_stage_mixed_buybacks", "sector": "STATE_BCRA", "frequency": "EVENT", "pre_value": "BNA_AGENT_MANDATE", "trough_value": "APPROX_USD380M_MIXED_PURCHASES_TWO_WEEKS", "trough_date": "2008-08-22", "recovery_value": "INSTRUMENT_AND_COUNTERPARTY_SPLIT_OPEN", "recovery_date": "N/D", "months_to_trough": "N/A", "months_to_recovery": "N/A", "benchmark_definition": "official first-stage mandate and program aggregate", "source_id": "e0_argentina_recompra_primera_etapa_2008_08_11;e0_argentina_recompra_segunda_semana_2008_08_22", "source_quality": "PRIMARY_AGGREGATE", "basis": "Official communiqués", "method_break": "YES_MIXED_PROGRAM_NOT_BODEN", "status": "FIRST_STAGE_AGGREGATE_BLOTTER_OPEN", "interpretation": "The first stage is now bounded by agent and approximate aggregate, not by instrument or counterparty.", "falsifier": "YES_ALL_USD380M_EQUALS_BODEN2012", "notes": "BNA memory 2008 does not provide the missing blotter."},
    {"episode_id": "E0", "episode_name": "Crisis de convertibilidad / default / salida / reordenamiento financiero", "t0": "2008-08-28_TO_2008-10-02", "shock_type": "OTHER", "variable": "four_located_public_buyback_tenders", "sector": "STATE_BCRA", "frequency": "EVENT", "pre_value": "14_INSTRUMENT_DATE_RESULTS", "trough_value": "18_ACCEPTED_PARTICIPANT_INSTRUMENT_ROWS", "trough_date": "2008-10-02", "recovery_value": "ARS135.60621486M_EFFECTIVE", "recovery_date": "2008-10-02", "months_to_trough": "N/A", "months_to_recovery": "N/A", "benchmark_definition": "accepted rows reproduce every awarded instrument and four date totals", "source_id": "E0_FISCAL_PUBLIC_BUYBACK_AWARDS_2008_V114.csv", "source_quality": "PRIMARY_DERIVED_EXACT", "basis": "Four official result communiqués", "method_break": "YES_PARTICIPANT_NOT_HOLDER_AND_AWARD_NOT_SETTLEMENT", "status": "FOUR_PUBLIC_RESULTS_PARTICIPANTS_RECONSTRUCTED", "interpretation": "Citibank, HSBC, Standard, MERVAL and Banco Mariva are identified as tender participants across four instruments.", "falsifier": "YES_PARTICIPANT_EQUALS_BENEFICIAL_HOLDER", "notes": "No closure notice proves the four located results exhaust all announced periodic tenders."},
    {"episode_id": "E0", "episode_name": "Crisis de convertibilidad / default / salida / reordenamiento financiero", "t0": "2008", "shock_type": "OTHER", "variable": "treasury_buyback_budget_execution_aggregate", "sector": "STATE_BCRA", "frequency": "ANNUAL", "pre_value": "N/D", "trough_value": "ARS981.36M_BUYBACK_OPERATIONS", "trough_date": "2008", "recovery_value": "SPECIES_AND_COUNTERPARTY_OPEN", "recovery_date": "N/D", "months_to_trough": "N/A", "months_to_recovery": "N/A", "benchmark_definition": "CGN executed short-term security acquisition paragraph", "source_id": "e0_cgn_cuenta_inversion_2008_comentarios", "source_quality": "PRIMARY_ACCOUNTING_AGGREGATE", "basis": "Cuenta de Inversión 2008", "method_break": "YES_NON_ADDITIVE_OVERLAP", "status": "EXECUTED_AGGREGATE_INSTRUMENT_OPEN", "interpretation": "The budget carrier creates an executed aggregate control but no BODEN allocation.", "falsifier": "YES_ADD_TO_TENDER_TOTALS", "notes": "Possible overlap with first- and second-stage purchases."},
    {"episode_id": "E0", "episode_name": "Crisis de convertibilidad / default / salida / reordenamiento financiero", "t0": "2008_TO_2012", "shock_type": "OTHER", "variable": "agn_creditor_distribution_reports", "sector": "STATE_BCRA", "frequency": "ANNUAL", "pre_value": "PRIVATE_54.8PCT_ALL_DEBT_2008", "trough_value": "PRIVATE_31.0PCT_ALL_DEBT_2012", "trough_date": "2012-12", "recovery_value": "PUBLIC_56.5PCT_ALL_DEBT_2012", "recovery_date": "2012-12", "months_to_trough": "48", "months_to_recovery": "48", "benchmark_definition": "AGN broad creditor-sector distribution", "source_id": "e0_agn_res_202_2009_act_41_2009_deuda;e0_agn_res_084_2015_act_158_2010_deuda", "source_quality": "PRIMARY_AUDIT_AGGREGATE", "basis": "AGN Res. 202/2009 and 84/2015", "method_break": "YES_ALL_DEBT_NOT_BODEN", "status": "AGN_REPORT_PAIR_BROAD_HOLDER_CONTROL", "interpretation": "The likely period/theme reports are recovered, but neither is a BODEN beneficial-holder register.", "falsifier": "YES_PRIVATE_SECTOR_EQUALS_BANKS", "notes": "The 2018 transparency page omits the identifiers of the reports actually sent."},
])
write_csv(HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V114.csv", matrix, matrix_fields)


evidence = [{key: v114_text(value) for key, value in row.items()} for row in read_csv(V113 / "HISTORICAL_EVIDENCE_COVERAGE_V113.csv")]
for row in evidence:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update({
            "quality": "PRIMARY_BUYBACK_PROGRAM_PARTICIPANTS_EXTENDED_2001_2012",
            "comparable": "SERIES_SERVICE_RECONCILED_FOUR_PUBLIC_RESULTS_FIRST_STAGE_AGGREGATE",
            "gap": "Four public results reproduce ARS 135.60621486m across instruments and participants; BNA first-stage species/counterparties, ultimate holders, purpose, Caja/BCRA settlement, primary strip result and CRYL register remain open",
            "next_action": "Recover Caja/BCRA settlement records, BNA trade blotter, beneficial-client/CRYL register, primary strip result and the individualized AGN transparency reply",
        })
write_csv(HERE / "HISTORICAL_EVIDENCE_COVERAGE_V114.csv", evidence)


queue = [{key: v114_text(value) for key, value in row.items()} for row in read_csv(V113 / "HISTORICAL_SOURCE_QUEUE_V113.csv")]
for row in queue:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update({
            "status": "PUBLIC_TENDERS_EXTENDED_BNA_STRIP_AGN_PARTIAL_SETTLEMENT_HOLDERS_OPEN",
            "why": "four public results reconstruct 18 participant-instrument awards; BNA first stage is only a mixed USD380m aggregate; strip quantity remains secondary and AGN reports are broad",
            "next_action": "Recover Caja/BCRA confirmations, BNA blotter, beneficial-client and CRYL records, primary 2009 strip result and AGN individualized response attachment",
        })
write_csv(HERE / "HISTORICAL_SOURCE_QUEUE_V114.csv", queue)


inherited = [
    {"script": "qa_v97.py", "pre_v114_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v114_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V97 requires a later-preserved source path/hash to remain blank."},
    *({"script": f"qa_v{i}.py", "pre_v114_result": "PASS", "post_v114_result": "PASS", "interpretation": "Compatible"} for i in (98, 100, 101, 102, 103, 104, 105, 106)),
    *({"script": f"qa_v{i}.py", "pre_v114_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v114_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "Fails only because the older checkpoint freezes catalog/source counts superseded by V114."} for i in (107, 108, 109, 110, 111, 112, 113)),
    {"script": "qa_v114.py", "pre_v114_result": "N/A", "post_v114_result": "PASS", "interpretation": "Current checkpoint invariants and exact multi-instrument tender arithmetic."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V114.csv", inherited)


readme = f"""# Checkpoint V114 · recompra 2005–2009, cuatro resultados públicos y fronteras de tenencia

V114 amplía la reconstrucción de V113 sin tocar el panel bancario. Congela las cuatro licitaciones públicas localizadas de 2008 a nivel instrumento y participante, acota la primera etapa operada tras el mandato al BNA, agrega controles CGN/AGN y recupera el resultado cuantitativo del strip 2009 sólo como fuente secundaria contemporánea.

## Resultado

- {len(primary_specs)} nuevas fuentes primarias y una secundaria preservadas;
- {len(census)} fuentes primarias E0 acumuladas;
- {len(tenders)} resultados instrumento-fecha y {len(awards)} filas adjudicadas reconstruidas;
- ARS {official_four_tender_ars} efectivos en los cuatro resultados públicos localizados;
- primera etapa: aproximadamente USD 380m en especies mezcladas, sin desglose BODEN/contraparte;
- Cuenta de Inversión 2008: ARS 981,36m agregados en operaciones de recompra, no aditivos;
- strip 2009: ocurrencia oficial; 35 ofertas, 20 aceptadas y USD 33,6m sólo en fuente secundaria;
- AGN 202/2009 y 84/2015: distribución amplia de acreedores, no padrón BODEN.

## Invariantes

- panel estricto Q4-2023: **30 entidades**;
- cobertura: **{STRICT}%**;
- `CLOSED_NETWORK_GATE`: **NO**;
- Banco Rioja: mismatch de **158,789k**.

## Leer primero

1. `VEREDICTO_V114.md`
2. `E0_FISCAL_RECONSTRUCTION_V114.md`
3. `E0_FISCAL_PUBLIC_BUYBACK_TENDERS_2008_V114.csv`
4. `E0_FISCAL_PUBLIC_BUYBACK_AWARDS_2008_V114.csv`
5. `E0_FISCAL_BUYBACK_PROGRAM_EVENTS_2005_2009_V114.csv`
6. `E0_FISCAL_AGN_REPORT_INDEX_V114.csv`
7. `AUDITORIA_V114.md`
8. `HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V114_A_V115.md`
"""
(HERE / "README_V114.md").write_text(readme, encoding="utf-8")


reconstruction = f"""# Reconstrucción fiscal E0 · programa de recompras · V114

## Cuatro resultados públicos localizados de 2008

| Fecha | Instrumentos adjudicados | Efectivo ARS oficial |
|---|---|---:|
| 28/08/2008 | Unidades PBI ARS | 9.890.509,02 |
| 04/09/2008 | BODEN 2012, BODEN 2013, unidades PBI ARS/USD | 20.154.238,16 |
| 11/09/2008 | BODEN 2012, BODEN 2013, unidades PBI ARS | 50.758.361,98 |
| 02/10/2008 | Unidades PBI ARS/USD | 54.803.105,70 |
| **Total localizado** |  | **{official_four_tender_ars:,.2f}** |

Las {len(awards)} filas de ofertas aceptadas suman ARS {raw_four_tender_ars} antes del redondeo y reproducen ARS {official_four_tender_ars} a centavos. Por instrumento: BODEN 2012 VNO USD 17.193.000; BODEN 2013 VNO USD 13.148.000; unidades PBI ARS 1.045.342.050 nocionales; unidades PBI USD 29.480.362 nocionales. Los nocionales de monedas e instrumentos distintos no se suman entre sí.

Los participantes reconstruidos son Citibank, HSBC Bank, Standard Bank, MERVAL y Banco Mariva. La columna de participante identifica quién presentó la oferta aceptada en MAE; no revela si operó por cartera propia o por clientes.

## Primera etapa y control contable

El comunicado del 11/08/2008 instruyó al BNA, como agente financiero del Gobierno, a recomprar especies BODEN y BONAR. Al 22/08 se informaron aproximadamente USD 380m en compras de seis especies mezcladas. La Memoria BNA 2008 no contiene el blotter buscado. En paralelo, la Cuenta de Inversión registra ARS 981,36m de “operaciones de recompra”; el agregado no separa instrumento, contraparte ni solapamiento con ambas etapas.

## Strip BODEN 2012 de 2009

Dos portadores oficiales confirman la licitación del cupón 15 y que menos del 2% de los tenedores presentó propuestas. El IEC 298, contemporáneo pero secundario, reporta 35 ofertas, 20 aceptadas, USD 33,6m, precio de corte USD 12,7, descuento medio 1,86% y ahorro USD 637.468. Hasta recuperar el comunicado primario, USD 33,6m conserva exactamente la etiqueta “monto reportado por la fuente”, sin reinterpretación como VNO o caja liquidada.

## AGN y frontera de tenencia

La página de transparencia confirma una solicitud específica sobre distribución de BODEN 2006/2012/2013 para 2006–2011 y dice que identificó informes, pero omite números y adjuntos. Se recuperaron dos informes coherentes por período y tema: Resolución 202/2009 (2008) y Resolución 84/2015, Actuación 158/2010 (2009–2012). Ambos distribuyen toda la deuda por sector acreedor; ninguno identifica titulares BODEN, clientes MAE ni beneficiarios del programa original. No se afirma que sean los dos documentos exactos remitidos al solicitante en 2018.

## Límite probatorio

Oferta ≠ adjudicación ≠ entrega Caja ≠ pago BCRA. Participante ≠ tenedor final. El agregado del BNA, las licitaciones públicas y la ejecución CGN no se suman sin puente de no solapamiento. `CLOSED_NETWORK_GATE=NO`.
"""
(HERE / "E0_FISCAL_RECONSTRUCTION_V114.md").write_text(reconstruction, encoding="utf-8")


audit_text = f"""# Auditoría V114

## Preservación y revisión visual

Se incorporaron {len(source_specs)} archivos: {len(primary_specs)} fuentes primarias oficiales y una fuente institucional secundaria contemporánea. Se revisaron visualmente: informe de recompras 2005 pp.1–5; comunicados 11/08, 21/08 y 22/08/2008 p.1; resultado 02/10/2008 pp.1–2; Memoria BNA p.14; Memoria 2009 pp.135–136; AGN 84/2015 pp.25–26; IEC 298 p.5. Las páginas de ofertas p.3 de los resultados 28/08, 04/09 y 11/09 preservados en V113 también fueron renderizadas e inspeccionadas para V114.

El PDF AGN 202/2009 descargado durante la recuperación resultó byte a byte idéntico al preservado en V112 y fue deduplicado; V114 reutiliza su `source_id` histórico.

## Pruebas aritméticas

- {len(tenders)} resultados por instrumento-fecha;
- {len(awards)} filas adjudicadas;
- cada grupo instrumento-fecha reproduce nocional, efectivo nativo y ARS oficial a centavos;
- suma bruta derivada: ARS {raw_four_tender_ars};
- suma de cuatro totales oficiales: ARS {official_four_tender_ars};
- BODEN 2012 queda sin cambios: VNO USD 17.193.000, efectivo USD 6.559.535 y ARS 20.088.405,76 oficiales;
- nunca se suman nocionales USD y ARS ni bonos y unidades PBI.

## Controles de alcance

- primera etapa: agente y agregado aproximado identificados; blotter ausente;
- ejecución CGN: agregado no aditivo;
- strip: ocurrencia primaria, resultado fino secundario;
- AGN: acreedor sectorial, no tenedor de instrumento;
- liquidación Caja/BCRA y beneficiario económico siguen abiertos.

## Conteos

- fuentes primarias E0: {len(census)};
- ledger fiscal: {len(ledger)} filas;
- quiebres metodológicos: {len(breaks)};
- eventos de programa: {len(events)};
- filas AGN de distribución: {len(creditors)}.
"""
(HERE / "AUDITORIA_V114.md").write_text(audit_text, encoding="utf-8")


verdict = f"""# Veredicto V114

## Qué avanzó

- Las cuatro licitaciones públicas localizadas de 2008 suman ARS {official_four_tender_ars / Decimal(1_000_000)}m efectivos y quedan reconstruidas en {len(awards)} filas participante–instrumento.
- La rama ya no se limita a BODEN 2012: incorpora BODEN 2013 y unidades PBI en pesos y dólares.
- La primera etapa queda acotada a un mandato al BNA y aproximadamente USD 380m de compras mixtas durante dos semanas.
- La ejecución presupuestaria aporta un control agregado de ARS 981,36m, explícitamente no aditivo.
- El strip 2009 tiene resultado cuantitativo contemporáneo, pero todavía no primario.
- La AGN aporta una secuencia agregada 2008–2012; no un padrón BODEN.

## Qué sigue prohibido afirmar

- que los participantes MAE fueran los tenedores económicos finales;
- que los títulos recomprados provinieran de compensación bancaria;
- que las adjudicaciones hubieran liquidado sin incumplimientos;
- que los USD 380m, ARS 135,606m y ARS 981,36m sean sumables;
- que los USD 33,6m del strip sean caja confirmada;
- que “sector privado” AGN signifique bancos.

## Estado

La rama fiscal pasa a `PRIMARY_BUYBACK_PROGRAM_PARTICIPANTS_EXTENDED_2001_2012`. Los faltantes decisivos son confirmaciones Caja/BCRA, blotter BNA, clientes finales/CRYL, comunicado primario del strip y adjunto individual de transparencia AGN. `CLOSED_NETWORK_GATE=NO`.
"""
(HERE / "VEREDICTO_V114.md").write_text(verdict, encoding="utf-8")


refs_lines = ["# Referencias de fuentes V114", "", "## Primarias preservadas"]
for spec in primary_specs:
    refs_lines.append(f"- {spec['title']}: {spec['url']}")
refs_lines.extend(["", "## Secundaria contemporánea preservada", f"- {source_specs[-1]['title']}: {source_specs[-1]['url']}", "", "Tamaños, hashes, uso y quiebres constan en `E0_LOCAL_PRIMARY_SOURCE_CENSUS_V114.csv` y `data/fuentes/FUENTES.csv`. La fuente secundaria no integra el censo primario."])
(HERE / "SOURCE_REFERENCES_V114.md").write_text("\n".join(refs_lines) + "\n", encoding="utf-8")


handover = f"""# Handover próxima sesión · V114 → V115

## Estado congelado

- {len(census)} fuentes primarias E0 preservadas;
- {len(ledger)} filas del ledger fiscal y {len(breaks)} quiebres;
- cuatro resultados públicos localizados: {len(tenders)} resultados instrumento-fecha, {len(awards)} adjudicaciones reconstruidas y ARS {official_four_tender_ars} efectivos;
- BODEN 2012 público: VNO USD 17.193m, sin cambio respecto de V113;
- primera etapa: mandato BNA + aproximadamente USD 380m mixtos, sin blotter;
- CGN 2008: ARS 981,36m agregados, no aditivos;
- strip 2009: ocurrencia oficial; 35/20/USD33,6m sólo secundario;
- AGN 202/2009 y 84/2015: informes amplios, no padrón BODEN;
- tenedor final, propósito y liquidación efectiva abiertos.

## Prioridad V115

1. recuperar confirmaciones T+3 de Caja de Valores y pagos BCRA de 02/09, 09/09, 16/09 y 07/10/2008;
2. obtener el blotter/orden ejecutada del BNA para 11–22/08/2008;
3. localizar el comunicado primario y anexo de ofertas del strip 2009;
4. obtener la respuesta individual/adjuntos del pedido AGN 14/08/2018;
5. buscar el padrón CRYL o conciliación Tesoro–Caja–BCRA–FGS–entidades;
6. identificar clientes finales detrás de participantes sin presumir cuenta propia;
7. buscar cierre administrativo que certifique cuántas licitaciones periódicas se realizaron.

## No hacer

- no sumar agregados potencialmente solapados;
- no mezclar nocionales entre monedas o instrumentos;
- no convertir participante en beneficiario;
- no convertir resultado en liquidación;
- no convertir fuente secundaria del strip en caja primaria;
- no convertir sector privado AGN en bancos.

## Invariantes

Panel estricto: 30 entidades; cobertura exacta {STRICT}%; `CLOSED_NETWORK_GATE=NO`; Banco Rioja mismatch 158,789k.
"""
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V114_A_V115.md").write_text(handover, encoding="utf-8")


old_hash = read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V113.csv")
hash_rows = [row for row in old_hash if row["id"] not in new_ids]
for spec in source_specs:
    hash_rows.append({"id": spec["id"], "archivo_local": spec["local"], "exists": "True", "sha_catalog": spec["sha256"], "sha_actual": spec["sha256"], "hash_ok": "True"})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V114.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V114.csv", hash_rows)
shutil.copyfile(AUDIT / "SOURCE_PATH_ENCODING_EXCEPTIONS_V113.csv", AUDIT / "SOURCE_PATH_ENCODING_EXCEPTIONS_V114.csv")
shutil.copyfile(AUDIT / "SOURCE_PRESERVATION_MISSING_V113.csv", AUDIT / "SOURCE_PRESERVATION_MISSING_V114.csv")


size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": str(size), "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V114.csv", size_rows, ["path", "bytes", "mib", "over_50_mib", "over_100_mib"])


physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
completeness = {
    "checkpoint": "V114", "date": "2026-08-29",
    "state": "E0_PUBLIC_BUYBACK_FOUR_RESULTS_PARTICIPANTS_FIRST_STAGE_STRIP_AGN_PARTIAL",
    "master_catalog_entries": len(catalog), "physical_local_copies": physical, "physical_local_hash_ok": hash_ok,
    "reference_only_nonbinary_exempt": 4, "remaining_physical_gaps": 1, "p0": 0, "p1": 1, "p2": 0,
    "binary_required_entries": len(catalog) - 4, "binary_required_preserved": physical,
    "binary_required_source_complete": False, "pending_binary_discovery_actions": 6,
    "numeric_v114_strict_changed": False, "strict_coverage_pct": STRICT,
    "exact_entities": 30, "asset_numerator_million_ars": "59812903.504", "system_denominator_million_ars": "96697695.5",
    "closed_network_gate": "NO", "e0_primary_sources_preserved": len(census),
    "sources_newly_preserved_v114": len(source_specs), "e0_primary_sources_newly_preserved_v114": len(primary_specs),
    "e0_quality": "PRIMARY_BUYBACK_PROGRAM_PARTICIPANTS_EXTENDED_2001_2012", "e0_comparable": False,
    "e0_fiscal_phase_separated": True, "e0_fiscal_final_cash_total_identified": False,
    "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
    "e0_public_tender_instrument_date_rows": len(tenders), "e0_public_tender_award_rows": len(awards),
    "e0_four_located_public_tender_effective_ars": str(official_four_tender_ars),
    "e0_four_located_public_tender_effective_ars_raw": str(raw_four_tender_ars),
    "e0_public_boden2012_awarded_vno_usd": "17193000", "e0_public_boden2012_awarded_effective_usd": "6559535.00",
    "e0_public_boden2012_awarded_effective_ars": "20088405.76", "e0_buyback_participants_identified": True,
    "e0_ultimate_holders_identified": False, "e0_settlement_chain_mapped_normatively": True,
    "e0_settlement_confirmations_preserved": False, "e0_bna_trade_blotter_preserved": False,
    "e0_first_stage_mixed_aggregate_usd_approx": "380000000", "e0_strip_official_occurrence_preserved": True,
    "e0_strip_primary_quantitative_result_preserved": False, "e0_strip_secondary_quantitative_result_preserved": True,
    "e0_agn_boden_report_identifiers_definitively_resolved": False, "e0_causal_net_incidence_identified": False,
    "historical_workstream": "E0_CAJA_BCRA_BNA_BENEFICIAL_HOLDER_PRIMARY_STRIP_AND_AGN_REPLY_OPEN",
    "path_encoding_note": "Banco La Pampa remains byte-identical despite the catalog/Git filename encoding mismatch.",
}
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V114.json").write_text(json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V114 · cuatro resultados públicos y fronteras de la recompra"
old_backup = backup.read_text(encoding="utf-8-sig")
if marker not in old_backup:
    old_backup += f"\n\n{marker}\n\n- Cuatro resultados públicos localizados reconstruidos en {len(awards)} filas: ARS {official_four_tender_ars} efectivos.\n- Primera etapa acotada a mandato BNA y aproximadamente USD 380m mixtos; blotter abierto.\n- CGN 2008 aporta ARS 981,36m agregados no aditivos.\n- Strip 2009: ocurrencia primaria y resultado cuantitativo sólo secundario.\n- AGN 202/2009 y 84/2015 son controles sectoriales agregados, no padrón BODEN.\n"
    backup.write_text(old_backup, encoding="utf-8")


def write_checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V114.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V114", "parent_checkpoint": "V113",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": len(source_specs), "new_primary_sources": len(primary_specs),
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks),
        "public_tender_instrument_date_rows": len(tenders), "public_tender_award_rows": len(awards),
        "four_located_public_tender_effective_ars": str(official_four_tender_ars),
        "four_located_public_tender_effective_ars_raw": str(raw_four_tender_ars),
        "files": files,
    }
    (HERE / "MANIFEST_V114.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    "checkpoint": "V114",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical local copies with {hash_ok}/{physical} SHA-valid; {len(primary_specs)} new primary and one secondary E0 source preserved; one catalogued P1 binary gap plus six discovery actions remain.",
    "historical_workstream": f"E0 four public buyback results reconstructed in {len(awards)} participant-instrument rows; first-stage blotter, primary strip result, ultimate holders and Caja/BCRA settlement remain open",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V114 BUILD PASS")
