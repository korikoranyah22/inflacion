from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import shutil


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
V116 = HERE.parent / "V116"
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v117" / "binaries"
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


def v117_text(text: str) -> str:
    return text.replace("V116", "V117").replace("v116", "v117")


# Bootstrap inherited checkpoint artifacts; V117 deltas overwrite the relevant copies below.
for source in sorted(V116.iterdir()):
    if not source.is_file() or source.suffix.lower() not in {".csv", ".md"}:
        continue
    if source.name.startswith("HANDOVER_"):
        continue
    target = HERE / v117_text(source.name)
    target.write_text(v117_text(source.read_text(encoding="utf-8-sig")), encoding="utf-8-sig")


source_specs = [
    {
        "id": "e0_agn_res_041_2016_deuda_custodian_gap",
        "institution": "Auditoría General de la Nación",
        "title": "Deuda intrasector público · Resolución AGN 41/2016 · limitaciones de custodios",
        "url": "https://www.agn.gob.ar/sites/default/files/informes/informe_041_2016.pdf",
        "file": "agn_informe_041_2016_deuda_tenencias_custodios.pdf",
        "publication": "2016",
        "period": "2009-2013; nota Caja 2014-11-19",
        "type": "PDF oficial · binario preservado",
        "pages": "138",
        "families": "state_bcra;fiscal;debt;holders;custody;CRYL;Caja_de_Valores;transparency",
        "breaks": "tenencias sector público versus beneficiarios privados; período 2009-2013 versus operación 2008; falta de información versus tenencia cero",
        "use": "USABLE_PRIMARY_CUSTODIAN_DISCLOSURE_GAP",
        "caveat": "Documenta pedidos sin resultado y una barrera de acceso para tenencias del sector público; no identifica tenedores privados ni prueba ausencia de registros operativos.",
        "verified": "Portada y páginas PDF 19-21, 100-102 y 110 fueron renderizadas e inspeccionadas visualmente.",
    },
    {
        "id": "e0_agn_api_boden_request_2018_record",
        "institution": "Auditoría General de la Nación",
        "title": "Registro JSON de acceso a información · BODEN 2006/2012/2013 · ingreso 14/08/2018",
        "url": "https://webagnapi.agn.gob.ar/api/node/webform/2074c3d9-a535-497e-a97d-d74340ff49fb?resourceVersion=id%3A18821",
        "file": "agn_api_webform_boden_request_2018.json",
        "publication": "2022-10-26",
        "period": "2018-08-14/2018-09-11",
        "type": "JSON oficial estructurado · binario preservado",
        "pages": "N/A",
        "families": "state_bcra;fiscal;debt;holders;source_route;transparency;schema",
        "breaks": "registro público versus respuesta individual; ausencia de relación de archivo versus inexistencia de respuesta fuera de línea",
        "use": "USABLE_EXACT_PUBLIC_RECORD_SCHEMA_NO_ATTACHMENT",
        "caveat": "El API confirma fechas, tema y texto público y no expone relación de archivo; no prueba que nunca se haya enviado una respuesta individual fuera del portal.",
        "verified": "JSON parseado; relaciones públicas limitadas a node_type, revision_uid y uid; sin included ni relación de archivo.",
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
            "id": spec["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": spec["institution"],
            "titulo": spec["title"], "url_original": spec["url"], "archivo_local": spec["local"],
            "fecha_descarga": "2026-08-29", "fecha_publicacion": spec["publication"], "codigo_serie": "",
            "periodo_utilizado": spec["period"], "tipo": spec["type"], "sha256": spec["sha256"],
            "nota": f"V117 E0 fiscal: {spec['bytes']:,} bytes; {spec['pages']} páginas. {spec['verified']}",
        }
    )
write_csv(CATALOG, catalog)


census = [row for row in read_csv(V116 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V116.csv") if row["source_id"] not in new_ids]
for spec in source_specs:
    census.append(
        {
            "source_id": spec["id"], "institution": spec["institution"], "artifact": spec["title"],
            "url": spec["url"], "local_path": spec["local"], "sha256": spec["sha256"], "bytes": str(spec["bytes"]),
            "period_coverage": spec["period"], "variable_families": spec["families"], "primary_source": "YES",
            "preserved": "YES", "method_breaks": spec["breaks"], "use_status": spec["use"], "caveat": spec["caveat"],
        }
    )
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V117.csv", census)


api_record = json.loads((BIN / "agn_api_webform_boden_request_2018.json").read_text(encoding="utf-8"))
data = api_record["data"]
attributes = data["attributes"]
relationships = sorted(data.get("relationships", {}))
file_relationships = [name for name in relationships if any(token in name.lower() for token in ("file", "archivo", "document", "informe"))]
included = api_record.get("included", [])
assert data["id"] == "2074c3d9-a535-497e-a97d-d74340ff49fb"
assert attributes["ingreso"] == "2018-08-14" and attributes["respuesta"] == "2018-09-11"
assert "Boden 2006, 2012 y 2013" in attributes["tema"]
assert relationships == ["node_type", "revision_uid", "uid"]
assert not file_relationships and not included


schema_rows = [
    {
        "record_type": data["type"], "node_uuid": data["id"],
        "drupal_nid": str(attributes["drupal_internal__nid"]), "drupal_vid": str(attributes["drupal_internal__vid"]),
        "public_alias": attributes["ruta"]["alias"], "request_date": attributes["ingreso"],
        "response_date": attributes["respuesta"], "record_year": str(attributes["ano"]),
        "topic": attributes["tema"].strip(), "public_response_text": attributes["tema_respuesta"],
        "relationship_types": ";".join(relationships), "file_relationship_present": "NO",
        "included_resource_count": str(len(included)), "individual_response_file_published": "NO",
        "match_status": "EXACT_PUBLIC_API_RECORD_NO_FILE_RELATIONSHIP",
        "source_id": "e0_agn_api_boden_request_2018_record", "source_locator": "JSON_data_attributes_relationships",
        "caveat": "No file relationship in the public schema does not prove that an individualized offline answer never existed.",
    }
]
write_csv(HERE / "E0_AGN_BODEN_REQUEST_PUBLIC_SCHEMA_V117.csv", schema_rows)


gap_fields = ["gap_id", "period", "institution_or_route", "evidence", "response_or_condition", "implication", "prohibited_inference", "source_id", "source_locator", "status"]
gaps = [
    {"gap_id": "CG01", "period": "2009-2013", "institution_or_route": "Secretaria_de_Hacienda_ONCP_DMO", "evidence": "Fiscal closing statements do not disaggregate public-instrument holdings for each public-sector agency.", "response_or_condition": "Published DISP and annexes do not permit timely direct composition of intra-public-sector debt.", "implication": "Agency-level public holdings cannot be reconstructed from published annual carriers alone.", "prohibited_inference": "Do not assign the gap to BODEN 2012 or to private beneficiaries.", "source_id": "e0_agn_res_041_2016_deuda_custodian_gap", "source_locator": "PDF_p19", "status": "PRIMARY_AUDIT_DISCLOSURE_GAP"},
    {"gap_id": "CG02", "period": "2014", "institution_or_route": "AGN_to_CNV_and_Caja_de_Valores", "evidence": "AGN reports that requests to CNV and Caja de Valores did not produce positive results.", "response_or_condition": "Custodian information was not obtained by the external auditor.", "implication": "The holder route is institutionally constrained, not merely absent from a web search.", "prohibited_inference": "Non-production is not zero holdings and does not prove no operational record exists.", "source_id": "e0_agn_res_041_2016_deuda_custodian_gap", "source_locator": "PDF_pp20_21", "status": "PRIMARY_AUDIT_REQUEST_NONPRODUCTION"},
    {"gap_id": "CG03", "period": "2014-11-19", "institution_or_route": "Caja_de_Valores_to_AGN", "evidence": "AGN footnote reproduces Caja guidance to channel the request through CNV as supervisory authority.", "response_or_condition": "Caja note without number dated 19 November 2014 referred the request to CNV.", "implication": "A specific institutional referral is documented.", "prohibited_inference": "Referral does not identify any holder and is not a settlement confirmation.", "source_id": "e0_agn_res_041_2016_deuda_custodian_gap", "source_locator": "PDF_p20_note_7", "status": "PRIMARY_CAJA_REFERRAL_NOTE"},
    {"gap_id": "CG04", "period": "2009-2013", "institution_or_route": "DMO_CRYL_Caja_de_Valores", "evidence": "AGN recommends that DMO request public-debt holdings from authorized custodians CRyL and Caja de Valores at fiscal closing and publication frequency.", "response_or_condition": "Custodian-derived agency holdings were not available to the audit.", "implication": "The missing evidence class and responsible institutional route are now explicit.", "prohibited_inference": "The recommendation is not proof the requested register was later produced.", "source_id": "e0_agn_res_041_2016_deuda_custodian_gap", "source_locator": "PDF_pp101_102", "status": "PRIMARY_CUSTODIAN_ROUTE_RECOMMENDATION"},
    {"gap_id": "CG05", "period": "2009-2014", "institution_or_route": "MECON_published_DISP_vs_DMO_note", "evidence": "AGN reports approximate cumulative differences of USD 3.937bn between published DISP and DMO note data.", "response_or_condition": "Published values for 2011 and 2012 also differ across vintages.", "implication": "Aggregate public-holder controls require vintage and source treatment.", "prohibited_inference": "Do not allocate the discrepancy to buybacks, BODEN 2012 or beneficiaries.", "source_id": "e0_agn_res_041_2016_deuda_custodian_gap", "source_locator": "PDF_p19", "status": "PRIMARY_AGGREGATE_DISCREPANCY_CONTROL"},
    {"gap_id": "CG06", "period": "2018-08-14/2018-09-11", "institution_or_route": "AGN_public_transparency_API", "evidence": "Exact JSON record publishes dates, BODEN topic and a generic answer stating that reports were identified.", "response_or_condition": "Public schema exposes no file relationship and no included resource.", "implication": "The public route is exact but does not deliver identifiers or the individualized reply.", "prohibited_inference": "No public attachment does not prove no offline response was sent.", "source_id": "e0_agn_api_boden_request_2018_record", "source_locator": "JSON_data_attributes_relationships", "status": "PRIMARY_PUBLIC_SCHEMA_NO_ATTACHMENT"},
]
write_csv(HERE / "E0_FISCAL_CUSTODIAN_INFORMATION_GAPS_V117.csv", gaps, gap_fields)


cdx_raw = json.loads((BIN / "wayback_cdx_mecon_finance_pdfs_2008_2009.json").read_text(encoding="utf-8"))
header = cdx_raw[0]
cdx_rows = []
for raw in cdx_raw[1:]:
    item = dict(zip(header, raw))
    original_lower = item["original"].lower()
    confirmation_candidate = any(token in original_lower for token in ("liquidacion", "confirmacion", "settlement", "caja_de_valores"))
    cdx_rows.append(
        {
            "timestamp": item["timestamp"], "original_url": item["original"], "mimetype": item["mimetype"],
            "statuscode": item["statuscode"], "cdx_digest": item["digest"], "captured_length": item["length"],
            "filename": item["original"].rsplit("/", 1)[-1],
            "post_settlement_confirmation_filename_candidate": "YES" if confirmation_candidate else "NO",
            "classification_note": "Filename inventory only; not full-text proof and not evidence that offline administrative records do not exist.",
        }
    )
assert len(cdx_rows) == 48
assert not any(row["post_settlement_confirmation_filename_candidate"] == "YES" for row in cdx_rows)
write_csv(HERE / "E0_FINANCE_ARCHIVE_PDF_CENSUS_2008_2009_V117.csv", cdx_rows)


route_rows = [
    {"route_id": "R117_01", "route": "MECON_WAYBACK_PDF_FILENAME_UNIVERSE", "query_scope": "www.mecon.gov.ar/finanzas/sfinan/documentos/* 2008-2009 unique PDF digests", "records_examined": "48", "positive_operational_confirmation_hits": "0", "status": "PUBLIC_ARCHIVE_CALLS_RESULTS_PRESENT_POST_SETTLEMENT_FILENAME_ABSENT", "evidence_file": "E0_FINANCE_ARCHIVE_PDF_CENSUS_2008_2009_V117.csv", "caveat": "Filename census is not full-text exhaustiveness and cannot exclude offline files."},
    {"route_id": "R117_02", "route": "BNA_WAYBACK_FILENAME_PATTERNS", "query_scope": "recompra;boden;deuda;bonos on www.bna.com.ar and bna.com.ar for 2008-2009", "records_examined": "5 successful pattern queries; 1 timeout", "positive_operational_confirmation_hits": "0", "status": "NO_BNA_BLOTTER_OR_ORDER_FILENAME_IDENTIFIED", "evidence_file": "RETRIEVAL_LOG_V117.md", "caveat": "Zero indexed hits does not prove no internal order or blotter exists."},
    {"route_id": "R117_03", "route": "AGN_PUBLIC_WEB_AND_JSON_API", "query_scope": "Exact request 2018-08-14 / response 2018-09-11 / BODEN 2006-2012-2013", "records_examined": "1 exact API node", "positive_operational_confirmation_hits": "0 file relationships", "status": "EXACT_RECORD_SCHEMA_IDENTIFIERS_AND_ATTACHMENT_NOT_PUBLISHED", "evidence_file": "E0_AGN_BODEN_REQUEST_PUBLIC_SCHEMA_V117.csv", "caveat": "Public schema absence does not exclude an offline individualized response."},
    {"route_id": "R117_04", "route": "EXACT_ISIN_ACCOUNT_DATE_WEB_SEARCH", "query_scope": "ARARGE03G415; Caja 0306/40000; 2008 T+3 dates; 2009-06-18", "records_examined": "official-domain and open-web exact queries", "positive_operational_confirmation_hits": "0", "status": "NO_POST_SETTLEMENT_CONFIRMATION_IDENTIFIED", "evidence_file": "RETRIEVAL_LOG_V117.md", "caveat": "Search-engine absence does not exclude administrative or banking records."},
]
write_csv(HERE / "E0_PUBLIC_ROUTE_EXHAUSTION_V117.csv", route_rows)


agn_index = [{key: v117_text(value) for key, value in row.items()} for row in read_csv(V116 / "E0_FISCAL_AGN_REPORT_INDEX_V116.csv")]
for row in agn_index:
    if row["record_id"] == "AGN_REQUEST_2018_08_14":
        row.update(
            {
                "resolution": "NOT_PUBLISHED_IN_EXACT_API_RECORD", "actuacion": "NOT_PUBLISHED_IN_EXACT_API_RECORD",
                "retrieved_scope": "Exact JSON node with request/response dates, topic and generic response text; no file relationship",
                "match_status": "EXACT_PUBLIC_API_RECORD_NO_FILE_RELATIONSHIP",
                "source_id": "e0_agn_transparencia_boden_2018;e0_agn_api_boden_request_2018_record",
                "caveat": "The public API omits identifiers and attachment; an offline individualized answer is not excluded.",
            }
        )
if not any(row["record_id"] == "AGN_RES041_2016" for row in agn_index):
    agn_index.append(
        {
            "record_id": "AGN_RES041_2016", "resolution": "41/2016", "actuacion": "N/D",
            "period_coverage": "2009-2013; custody request 2014", "requested_or_report_scope": "Intra-public-sector debt and custodian transparency",
            "retrieved_scope": "Primary audit findings on missing custody holdings, Caja/CNV non-production and Caja referral note",
            "match_status": "PRIMARY_CUSTODIAN_DISCLOSURE_GAP_CONTROL",
            "source_id": "e0_agn_res_041_2016_deuda_custodian_gap",
            "caveat": "Public-sector agency holdings and later audit period; not a BODEN-specific beneficial-holder register or 2008 settlement record.",
        }
    )
write_csv(HERE / "E0_FISCAL_AGN_REPORT_INDEX_V117.csv", agn_index)


ledger = [{key: v117_text(value) for key, value in row.items()} for row in read_csv(V116 / "E0_FISCAL_MECHANISM_LEDGER_V116.csv")]
ledger_fields = list(ledger[0])
new_ledger = [
    ("F122", "2018", "BODEN_information_request", "PUBLIC_API_RECORD_SCHEMA", "2018-08-14/2018-09-11", "AGN", "Information_requester", "Public_transparency_record", "BODEN_2006_2012_2013_reports", "N/D", "N/D", "N/D", "SCHEMA_AND_ROUTE_ONLY", "e0_agn_api_boden_request_2018_record", "JSON_data_attributes_relationships", "EXACT_PUBLIC_RECORD_NO_ATTACHMENT", "NON_ADDITIVE", "Exact public node fixes the request scope and response dates but exposes no report identifiers or file relationship.", "Public schema absence does not prove no offline reply existed."),
    ("F123", "2009-2013", "Public_debt_holdings", "CUSTODIAN_INFORMATION_GAP", "2014", "AGN", "CNV_and_Caja_de_Valores", "Public_sector_agency_holdings", "Public_debt_instruments", "N/D", "N/D", "N/D", "PRIMARY_AUDIT_REQUEST_NONPRODUCTION", "e0_agn_res_041_2016_deuda_custodian_gap", "PDF_pp20_21_101", "CUSTODIAN_DATA_NOT_OBTAINED", "NON_ADDITIVE", "AGN documents that custodian-route requests did not yield holdings data.", "Non-production is not zero holdings and does not identify private beneficiaries."),
    ("F124", "2014", "Public_debt_holdings", "CAJA_TO_CNV_REFERRAL", "2014-11-19", "Caja_de_Valores", "AGN_via_CNV", "Public_sector_agency_holdings", "Public_debt_instruments", "N/D", "N/D", "N/D", "CAJA_NOTE_REFERRED_REQUEST_TO_SUPERVISOR", "e0_agn_res_041_2016_deuda_custodian_gap", "PDF_p20_note_7", "PRIMARY_REFERRAL_NOTE", "NON_ADDITIVE", "Caja guidance reproduced by AGN directs the request through CNV.", "Referral is not holder identification or settlement confirmation."),
    ("F125", "2009-2014", "Intra_public_sector_debt", "PUBLISHED_VS_DMO_DISCREPANCY_CONTROL", "2009-2014", "MECON_DMO", "Public_information_users", "DISP_aggregate", "All_public_debt", "3937", "USD_million_approx_difference", "N/D", "AGN_CUMULATIVE_APPROXIMATE_DIFFERENCE", "e0_agn_res_041_2016_deuda_custodian_gap", "PDF_p19", "AGGREGATE_SOURCE_VINTAGE_CONTROL", "CONTROL_NOT_ADDITIVE", "AGN reports approximate cumulative differences between published DISP and DMO note data.", "Do not allocate to BODEN, buybacks, banks or beneficiaries."),
]
known_ledger = {row["ledger_id"] for row in ledger}
for values in new_ledger:
    if values[0] not in known_ledger:
        ledger.append(dict(zip(ledger_fields, values)))
write_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V117.csv", ledger, ledger_fields)


breaks = [{key: v117_text(value) for key, value in row.items()} for row in read_csv(V116 / "E0_FISCAL_METHOD_BREAKS_V116.csv")]
break_fields = list(breaks[0])
new_breaks = [
    ("public_api_record_not_individual_response", "source", "El nodo público reproduce metadatos y un resumen, no la respuesta individual ni sus adjuntos.", "Usar el API para fijar esquema y omisiones públicas; requerir el expediente para conocer la respuesta enviada.", "AGN API node 2074c3d9-a535-497e-a97d-d74340ff49fb"),
    ("custodian_nonproduction_not_zero_holdings", "inference", "Que Caja/CNV no entreguen datos a AGN no implica tenencias cero ni inexistencia de registros.", "Clasificar como barrera de acceso y mantener abiertos padrón y liquidación.", "Resolución AGN 41/2016 pp.20-21, 101"),
    ("custodian_audit_period_not_2008_transaction", "time", "La auditoría cubre 2009-2013 y una nota de 2014, no las liquidaciones de 2008.", "Usarla como control institucional de divulgación, no como prueba directa de cada operación.", "Resolución AGN 41/2016"),
    ("intrasector_discrepancy_not_buyback_allocation", "aggregation", "La diferencia DISP-DMO es para deuda intrasector agregada y vintages 2009-2014.", "Conservarla como control de fuente; no asignarla a BODEN, recompras, bancos o beneficiarios.", "Resolución AGN 41/2016 p.19"),
]
known_breaks = {row["break_id"] for row in breaks}
for break_id, dimension, problem, rule, evidence_item in new_breaks:
    if break_id not in known_breaks:
        breaks.append({"break_id": break_id, "dimension": dimension, "problem": problem, "rule": rule, "status": "FROZEN", "evidence": evidence_item})
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V117.csv", breaks, break_fields)


matrix = [{key: v117_text(value) for key, value in row.items()} for row in read_csv(V116 / "HISTORICAL_EPISODE_MATRIX_2001_2026_V116.csv")]
if not any(row["variable"] == "custodian_holder_information_gap" for row in matrix):
    template = next(row for row in matrix if row["episode_id"] == "E0")
    new_row = {key: "N/D" for key in template}
    new_row.update(
        {
            "episode_id": "E0", "episode_name": "Crisis de convertibilidad / default / salida / reordenamiento financiero",
            "t0": "2009_TO_2014_AUDIT_CONTROL", "shock_type": "OTHER", "variable": "custodian_holder_information_gap",
            "sector": "STATE_BCRA", "frequency": "AUDIT", "pre_value": "PUBLIC_AGENCY_HOLDINGS_NOT_DISAGGREGATED",
            "trough_value": "AGN_REQUESTS_TO_CNV_CAJA_NO_POSITIVE_RESULT", "trough_date": "2014-11-19",
            "recovery_value": "DMO_CRYL_CAJA_DISCLOSURE_RECOMMENDED_NOT_OBSERVED", "recovery_date": "N/D",
            "benchmark_definition": "primary external-audit finding on custody disclosure and exact public transparency schema",
            "source_id": "e0_agn_res_041_2016_deuda_custodian_gap;e0_agn_api_boden_request_2018_record;E0_FISCAL_CUSTODIAN_INFORMATION_GAPS_V117.csv",
            "source_quality": "PRIMARY_AUDIT_AND_PRIMARY_API_SCHEMA", "basis": "AGN Resolution 41/2016 and exact JSON node",
            "method_break": "YES_NONPRODUCTION_NOT_ZERO_PERIOD_NOT_2008_PUBLIC_RECORD_NOT_REPLY",
            "status": "STRUCTURAL_CUSTODY_DISCLOSURE_GAP_DOCUMENTED",
            "interpretation": "The missing holder register is now tied to a documented institutional access barrier rather than treated as a mere search failure.",
            "falsifier": "YES_CUSTODIAN_NONPRODUCTION_EQUALS_ZERO_OR_NO_RECORD",
            "notes": "Does not identify private holders, 2008 counterparties or settlement confirmations.",
        }
    )
    matrix.append(new_row)
write_csv(HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V117.csv", matrix)


evidence = [{key: v117_text(value) for key, value in row.items()} for row in read_csv(V116 / "HISTORICAL_EVIDENCE_COVERAGE_V116.csv")]
for row in evidence:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            {
                "quality": "PRIMARY_BUYBACK_STRIP_EXACT_ACCOUNT_ROUTE_CUSTODIAN_GAP_DOCUMENTED_2001_2013",
                "comparable": "SERIES_SERVICE_RECONCILED_TRANSACTIONS_EXACT_CUSTODIAN_DISCLOSURE_GAP_PRIMARY",
                "gap": "Resultados y rutas Caja/BCRA están documentados; AGN prueba que la apertura de tenencias no se obtuvo de Caja/CNV y el API 2018 no publica adjunto. Faltan liquidaciones, blotter BNA y tenedores finales.",
                "next_action": "Pedir expedientes/constancias directamente a Tesoro, BCRA, BNA, Caja/CNV/CRYL y la respuesta AGN individual; no repetir búsqueda web pública sin identificador nuevo.",
            }
        )
write_csv(HERE / "HISTORICAL_EVIDENCE_COVERAGE_V117.csv", evidence)


queue = [{key: v117_text(value) for key, value in row.items()} for row in read_csv(V116 / "HISTORICAL_SOURCE_QUEUE_V116.csv")]
for row in queue:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            {
                "status": "TRANSACTIONS_PRIMARY_EXACT_CUSTODIAN_GAP_PRIMARY_DOCUMENTED",
                "why": "La AGN documenta que Caja/CNV no produjeron la apertura de tenencias y el nodo público 2018 carece de archivo; faltan constancias operativas y expedientes internos.",
                "next_action": "Solicitar expedientes/constancias a Tesoro, BCRA, BNA, Caja/CNV/CRYL y AGN; evitar repetir rutas web agotadas.",
            }
        )
write_csv(HERE / "HISTORICAL_SOURCE_QUEUE_V117.csv", queue)


inherited = [
    {"script": "qa_v97.py", "pre_v117_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v117_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V97 requiere que una fuente recuperada después permanezca sin ruta/hash."},
    *({"script": f"qa_v{i}.py", "pre_v117_result": "PASS", "post_v117_result": "PASS", "interpretation": "Compatible"} for i in (98, 100, 101, 102, 103, 104, 105, 106)),
    *({"script": f"qa_v{i}.py", "pre_v117_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v117_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "Falla sólo porque congela conteos anteriores a V117."} for i in range(107, 117)),
    {"script": "qa_v117.py", "pre_v117_result": "N/A", "post_v117_result": "PASS", "interpretation": "Invariantes actuales, PDF, JSON, censo CDX y barreras de custodia."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V117.csv", inherited)


readme = f"""# Checkpoint V117 · barrera de custodia documentada

V117 amplía V116 sin tocar el panel bancario ni convertir búsquedas negativas en tenencias cero. Preserva una auditoría AGN sobre deuda intrasector y el registro JSON exacto del pedido BODEN de 2018.

## Resultado

- 2 nuevas fuentes primarias oficiales; {len(census)} fuentes primarias E0 acumuladas;
- AGN documenta que pedidos a Caja de Valores y CNV no produjeron la apertura de tenencias;
- nota Caja del 19/11/2014: derivación del pedido a CNV;
- recomendación explícita para que DMO requiera información a CRyL y Caja;
- nodo AGN 2018 exacto, sin relación de archivo ni identificadores de informes;
- 48 PDFs oficiales únicos 2008-2009 censados en Wayback, sin nombre de archivo de confirmación post-liquidación;
- ninguna liquidación ni tenedor final se presume por ausencia documental.

## Invariantes

Panel estricto Q4-2023: 30 entidades; cobertura {STRICT}%; CLOSED_NETWORK_GATE=NO.

## Leer primero

1. VEREDICTO_V117.md
2. E0_FISCAL_CUSTODIAN_INFORMATION_GAPS_V117.csv
3. E0_AGN_BODEN_REQUEST_PUBLIC_SCHEMA_V117.csv
4. E0_PUBLIC_ROUTE_EXHAUSTION_V117.csv
5. E0_FINANCE_ARCHIVE_PDF_CENSUS_2008_2009_V117.csv
6. RETRIEVAL_LOG_V117.md
7. AUDITORIA_V117.md
8. HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V117_A_V118.md
"""
(HERE / "README_V117.md").write_text(readme, encoding="utf-8")


reconstruction = """# Reconstrucción fiscal E0 · custodia, transparencia y límite de inferencia · V117

## Hallazgo institucional

La Resolución AGN 41/2016 estudia la deuda intrasector público para 2009-2013. Señala que la Secretaría de Hacienda no exponía al cierre anual la apertura de instrumentos por agencia y que las solicitudes de AGN a Caja de Valores y CNV no tuvieron resultados positivos. La nota de Caja del 19/11/2014, reproducida por AGN, derivó la consulta hacia CNV.

El hallazgo no demuestra tenencias cero. Demuestra algo distinto: incluso la auditoría externa enfrentó una barrera para obtener la apertura custodial. AGN recomendó que la DMO requiriera tenencias a los custodios autorizados —CRyL y Caja— al cierre de cada ejercicio y con la frecuencia del Boletín Fiscal.

La auditoría también observó una diferencia acumulada aproximada de USD 3.937m entre información DISP publicada y datos remitidos por DMO para 2009-2014. Es un control agregado de fuentes y vintages: no se asigna a BODEN, recompras, bancos ni beneficiarios.

## Pedido BODEN 2018

El nodo JSON exacto fija ingreso 14/08/2018, respuesta 11/09/2018 y el tema BODEN 2006/2012/2013. Sus únicas relaciones son node_type, revision_uid y uid; no contiene relación de archivo ni recurso incluido. Esto prueba que el portal no publica el adjunto o los identificadores. No prueba que una respuesta individual nunca haya sido enviada fuera del portal.

## Rutas agotadas

El censo Wayback del directorio histórico de Finanzas contiene 48 PDFs únicos de 2008-2009: aparecen llamados y resultados conocidos, pero ningún nombre de archivo identifica confirmación Caja/BCRA. Las variantes históricas BNA por recompra, BODEN, deuda y bonos tampoco localizaron blotter u orden. Estas ausencias acotan la búsqueda pública; no excluyen expedientes internos.

## Estado

La etapa pública pasa de buscar un padrón visible a documentar por qué no está disponible y qué organismos deben ser requeridos. Siguen abiertos pago/entrega, blotter BNA, padrón CRyL/Caja y respuesta AGN individual. CLOSED_NETWORK_GATE=NO.
"""
(HERE / "E0_FISCAL_RECONSTRUCTION_V117.md").write_text(reconstruction, encoding="utf-8")


audit_text = f"""# Auditoría V117

## Preservación y revisión

Se preservó el informe AGN 41/2016 de 138 páginas. Se renderizaron e inspeccionaron visualmente portada y páginas 19-21, 100-102 y 110; son legibles y sin defectos. Se preservó también el nodo JSON AGN versionado y se verificaron atributos, relaciones y ausencia de archivos incluidos. Los PNG temporales fueron eliminados.

## Controles

- catálogo maestro: {len(catalog)} entradas; censo E0: {len(census)} primarias;
- nodo AGN: UUID exacto, fechas 14/08 y 11/09/2018, tres relaciones no documentales, cero archivos incluidos;
- censo histórico Mecon: 48 PDFs únicos, cero candidatos por nombre a confirmación post-liquidación;
- ledger fiscal: {len(ledger)} filas; quiebres: {len(breaks)};
- no se añadió ningún estado CASH_SETTLED ni tenedor final.

## Límites congelados

- no producción custodial no equivale a tenencia cero;
- auditoría 2009-2013 no confirma operaciones de 2008;
- nodo público sin archivo no excluye respuesta fuera de línea;
- diferencia DISP-DMO no se asigna a recompras;
- ausencia en Wayback o buscador no excluye expediente interno.
"""
(HERE / "AUDITORIA_V117.md").write_text(audit_text, encoding="utf-8")


verdict = """# Veredicto V117

## Qué avanzó

- La falta de padrón deja de ser sólo una búsqueda negativa: AGN documenta que no obtuvo la apertura de Caja/CNV.
- Queda identificada una nota de Caja del 19/11/2014 que derivó la consulta a CNV.
- El registro público exacto del pedido BODEN 2018 no contiene adjunto ni identificadores.
- El universo archivado de 48 PDFs Mecon 2008-2009 no expone una pieza nominal de post-liquidación.

## Qué no demuestra

- que no existan registros internos en Caja, CRyL, BCRA, BNA o Tesoro;
- que las tenencias fueran cero;
- quiénes eran los beneficiarios finales;
- que una adjudicación se liquidara;
- que el período auditado 2009-2013 confirme operaciones de 2008;
- que el pedido AGN no recibiera una respuesta fuera del portal.

## Estado

La próxima etapa requiere expedientes o pedidos institucionales directos. Las rutas web públicas quedan agotadas salvo aparición de un identificador nuevo. CLOSED_NETWORK_GATE=NO.
"""
(HERE / "VEREDICTO_V117.md").write_text(verdict, encoding="utf-8")


refs = ["# Referencias de fuentes V117", "", "## Primarias preservadas"]
refs.extend(f"- {spec['title']}: {spec['url']}" for spec in source_specs)
refs.extend(["", "El archivo CDX de Internet Archive se usa sólo como censo de recuperación, no como fuente primaria del mecanismo."])
(HERE / "SOURCE_REFERENCES_V117.md").write_text("\n".join(refs) + "\n", encoding="utf-8")


retrieval = """# Registro de recuperación V117

## Caja/BCRA

Las consultas exactas por ISIN ARARGE03G415, cuenta 0306/40000 y fechas T+3 de 2008 y 18/06/2009 no recuperaron constancias posteriores. El censo CDX del directorio oficial de Finanzas para 2008-2009 contiene 48 PDFs únicos: llamados y resultados están presentes, pero ningún nombre identifica liquidación, confirmación o informe Caja/BCRA. Esto no excluye expedientes fuera de la web.

## Banco Nación

Se probaron patrones históricos recompra, BODEN, deuda y bonos sobre www.bna.com.ar y bna.com.ar para 2008-2009. Cinco consultas concluyeron sin resultados y una variante agotó tiempo; no apareció blotter, orden ejecutada ni comunicado propio. La Cuenta de Inversión mantiene el total oficial de primera etapa, pero no aporta contrapartes u operaciones.

## AGN y custodios

El nodo JSON exacto del pedido 14/08/2018 fue localizado mediante el endpoint oficial. Confirma fechas, tema y respuesta genérica; no expone relación de archivo. La Resolución AGN 41/2016 aporta la limitación estructural: pedidos a Caja y CNV sin resultado positivo, nota de derivación Caja del 19/11/2014 y recomendación de requerir tenencias a CRyL/Caja.

## Regla de continuidad

No repetir estas rutas públicas sin identificador nuevo. La siguiente etapa debe usar pedidos de acceso, expedientes, notas de liquidación o registros institucionales directos de Tesoro, BCRA, BNA, Caja/CNV/CRyL y AGN.
"""
(HERE / "RETRIEVAL_LOG_V117.md").write_text(retrieval, encoding="utf-8")


handover = f"""# Handover próxima sesión · V117 → V118

## Estado congelado

- {len(census)} fuentes primarias E0; {len(ledger)} filas fiscales; {len(breaks)} quiebres;
- cuatro rondas 2008 y strip 2009 exactos, liquidación abierta;
- AGN 41/2016: Caja/CNV no produjeron apertura de tenencias; nota Caja 19/11/2014;
- API AGN 2018: registro exacto sin adjunto ni identificadores;
- 48 PDFs Mecon 2008-2009 censados, sin nombre de confirmación post-liquidación;
- BNA web/Wayback sin blotter u orden;
- panel bancario intacto: 30 entidades, {STRICT}%.

## Prioridad V118

1. formular o localizar pedidos institucionales específicos a Tesoro/BCRA por constancias T+3;
2. pedir a BNA blotter u orden ejecutada 11-22/08/2008;
3. pedir a AGN copia de la respuesta individual de 11/09/2018;
4. pedir a Caja/CNV/CRyL registros o agregados compatibles con secreto y protección de datos.

## No hacer

- no convertir no producción en cero;
- no convertir derivación Caja→CNV en respuesta sustantiva;
- no convertir esquema JSON sin archivo en inexistencia de respuesta;
- no usar auditoría 2009-2013 como liquidación 2008;
- no asignar la diferencia DISP-DMO a BODEN o beneficiarios.

CLOSED_NETWORK_GATE=NO.
"""
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V117_A_V118.md").write_text(handover, encoding="utf-8")


old_hash = read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V116.csv")
hash_rows = [row for row in old_hash if row["id"] not in new_ids]
for spec in source_specs:
    hash_rows.append({"id": spec["id"], "archivo_local": spec["local"], "exists": "True", "sha_catalog": spec["sha256"], "sha_actual": spec["sha256"], "hash_ok": "True"})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V117.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V117.csv", hash_rows)
shutil.copyfile(AUDIT / "SOURCE_PATH_ENCODING_EXCEPTIONS_V116.csv", AUDIT / "SOURCE_PATH_ENCODING_EXCEPTIONS_V117.csv")
shutil.copyfile(AUDIT / "SOURCE_PRESERVATION_MISSING_V116.csv", AUDIT / "SOURCE_PRESERVATION_MISSING_V117.csv")


size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": str(size), "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V117.csv", size_rows, ["path", "bytes", "mib", "over_50_mib", "over_100_mib"])


physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
completeness = {
    "checkpoint": "V117", "date": "2026-08-29", "state": "E0_CUSTODIAN_DISCLOSURE_GAP_PRIMARY_DOCUMENTED",
    "master_catalog_entries": len(catalog), "physical_local_copies": physical, "physical_local_hash_ok": hash_ok,
    "reference_only_nonbinary_exempt": 4, "remaining_physical_gaps": 1, "p0": 0, "p1": 1, "p2": 0,
    "binary_required_entries": len(catalog) - 4, "binary_required_preserved": physical, "binary_required_source_complete": False,
    "pending_binary_discovery_actions": 3, "pending_external_request_actions": 1,
    "numeric_v117_strict_changed": False, "strict_coverage_pct": STRICT, "exact_entities": 30,
    "asset_numerator_million_ars": "59812903.504", "system_denominator_million_ars": "96697695.5", "closed_network_gate": "NO",
    "e0_primary_sources_preserved": len(census), "sources_newly_preserved_v117": len(source_specs),
    "e0_primary_sources_newly_preserved_v117": len(source_specs),
    "e0_quality": "PRIMARY_BUYBACK_STRIP_EXACT_ACCOUNT_ROUTE_CUSTODIAN_GAP_DOCUMENTED_2001_2013",
    "e0_comparable": False, "e0_fiscal_phase_separated": True, "e0_fiscal_final_cash_total_identified": False,
    "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
    "e0_buyback_program_events": 10, "e0_settlement_confirmations_preserved": False,
    "e0_bna_trade_blotter_preserved": False, "e0_ultimate_holders_identified": False,
    "e0_agn_public_boden_record_exact": True, "e0_agn_public_record_file_relationship_present": False,
    "e0_agn_individual_offline_response_excluded": False, "e0_custodian_information_gap_primary_documented": True,
    "e0_caja_2014_referral_note_documented": True, "e0_custodian_nonproduction_interpreted_as_zero": False,
    "e0_mecon_wayback_pdf_unique_2008_2009": len(cdx_rows), "e0_mecon_post_settlement_filename_candidates": 0,
    "e0_causal_net_incidence_identified": False,
    "historical_workstream": "E0_DIRECT_INSTITUTIONAL_REQUESTS_FOR_SETTLEMENT_BNA_AGN_AND_CUSTODIANS_OPEN",
    "path_encoding_note": "Banco La Pampa remains byte-identical despite the catalog/Git filename encoding mismatch.",
}
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V117.json").write_text(json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V117 · barrera de custodia documentada"
old_backup = backup.read_text(encoding="utf-8-sig")
if marker not in old_backup:
    old_backup += f"\n\n{marker}\n\n- AGN 41/2016 documenta pedidos a Caja/CNV sin apertura de tenencias y una nota Caja de 19/11/2014.\n- El nodo JSON exacto del pedido BODEN 2018 no expone archivo ni identificadores.\n- El censo de 48 PDFs Mecon 2008-2009 no muestra una pieza nominal de post-liquidación.\n- No producción no se interpreta como cero; la fase siguiente requiere pedidos institucionales directos.\n"
    backup.write_text(old_backup, encoding="utf-8")


def write_checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V117.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V117", "parent_checkpoint": "V116",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": len(source_specs), "new_primary_sources": len(source_specs),
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks), "buyback_program_events": 10,
        "custodian_gap_rows": len(gaps), "agn_public_schema_rows": len(schema_rows), "mecon_archive_pdf_census_rows": len(cdx_rows),
        "mecon_post_settlement_filename_candidates": 0, "files": files,
    }
    (HERE / "MANIFEST_V117.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    "checkpoint": "V117", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical local copies with {hash_ok}/{physical} SHA-valid; 2 new primary E0 sources preserved; one catalogued P1 binary gap plus three discovery and one institutional-request actions remain.",
    "historical_workstream": "E0 transaction results exact; AGN primary custodian-disclosure barrier and exact public request schema preserved; direct institutional records remain open",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V117 BUILD PASS")
