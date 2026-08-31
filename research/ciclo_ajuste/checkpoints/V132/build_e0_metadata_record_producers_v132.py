from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import re
import shutil


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
V131 = HERE.parent / "V131"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v132" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


SOURCES = [
    {
        "id": "e0_agn_api_informe_res202_act41_2009",
        "filename": "agn_api_informe_res202_act41_2009.json",
        "institution": "Auditoría General de la Nación",
        "title": "Ficha JSON:API del informe de deuda 2008 · Resolución 202/2009 · Actuación 41/2009",
        "url": "https://webagnapi.agn.gob.ar/api/node/informes/b52e2e9c-90b5-4af1-bf5d-0bab8596606e?include=informe,resolucion_archivo,ficha,anexo",
        "publication": "2009", "period": "2008", "code": "UUID b52e2e9c-90b5-4af1-bf5d-0bab8596606e",
        "type": "JSON:API oficial · binario preservado", "bytes": 13002,
        "sha256": "8edcc3503af5f3ec0c380788dc70fe3276885e621ce37bfaf00f48f3baacdcfc",
        "families": "fiscal;debt;audit_metadata;identity_crosswalk",
        "breaks": "metadato final versus código interno de proyecto",
        "use": "USABLE_FINAL_REPORT_IDENTITY_METADATA",
        "caveat": "Cierra título, período, actuación y resolución del informe final; no publica el código interno 48 0237/09 ni una liquidación.",
        "note": "V132 E0: una búsqueda por Actuación 41/2009 y otra por Resolución 202/año 2009 devuelven este mismo UUID único.",
    },
    {
        "id": "e0_agn_res_202_2009_act_41_2009_resolution",
        "filename": "agn_res_202_2009_act_41_2009.pdf",
        "institution": "Auditoría General de la Nación",
        "title": "Resolución AGN 202/2009 · Actuación 41/2009 · aprobación del estudio de deuda 2008",
        "url": "https://www.agn.gob.ar/sites/default/files/informes/2009_202Reso.pdf",
        "publication": "2009-11-23", "period": "2008", "code": "Resolución 202/2009; Actuación 41/2009",
        "type": "PDF oficial · binario preservado", "bytes": 48191,
        "sha256": "52a27534424d10eb631c9852d8ba35222d3448eeefaf583192c745d59d755589",
        "families": "fiscal;debt;audit_process;identity_crosswalk",
        "breaks": "resolución de aprobación versus informe; actuación versus proyecto",
        "use": "USABLE_ACT_RESOLUTION_PROCEDURAL_CHAIN",
        "caveat": "Aprueba el informe y prueba la actuación, la remisión al auditado y la falta de respuesta formal al vencimiento; no individualiza recompras.",
        "note": "V132 E0: las tres páginas fueron renderizadas; fecha 23/11/2009, Nota 203/09 GCDP de 29/06/2009 y sesión del Colegio de 30/09/2009.",
    },
    {
        "id": "e0_agn_api_informe_3t_2009_res211",
        "filename": "agn_api_informe_3t_2009_res211.json",
        "institution": "Auditoría General de la Nación",
        "title": "Ficha JSON:API · Informe de actividad AGN del tercer trimestre de 2009 · Resolución 211/2009",
        "url": "https://webagnapi.agn.gob.ar/api/node/informes/7c01261c-10a0-40f6-94f6-ae7a02be8b63?include=informe,resolucion_archivo",
        "publication": "2009", "period": "2009Q3", "code": "UUID 7c01261c-10a0-40f6-94f6-ae7a02be8b63",
        "type": "JSON:API oficial · binario preservado", "bytes": 10672,
        "sha256": "001a311e62a2ead9649c5ffc0261c2691ed32eeb150388f298ab769ec1076aa5",
        "families": "audit_activity;quarterly_tracker;archival_locator",
        "breaks": "resolución pública versus anexo de actividad no enlazado",
        "use": "USABLE_QUARTERLY_RESOLUTION_METADATA",
        "caveat": "La ficha enlaza sólo la resolución; el anexo mencionado en soporte magnético no está expuesto.",
        "note": "V132 E0: localiza Res.211/2009; la resolución identifica Actuación 426/09-AGN.",
    },
    {
        "id": "e0_agn_res_211_2009_3t_activity",
        "filename": "agn_res_211_2009_3t_2009.pdf",
        "institution": "Auditoría General de la Nación",
        "title": "Resolución AGN 211/2009 · Informe de actividad del tercer trimestre de 2009",
        "url": "https://www.agn.gob.ar/sites/default/files/informes/resolucion_211_2009.pdf",
        "publication": "2009-11-23", "period": "2009Q3", "code": "Resolución 211/2009; Actuación 426/09-AGN",
        "type": "PDF oficial · binario preservado", "bytes": 30951,
        "sha256": "d8408f34fa88c2f4614fcdb30f8a2eed64d57e72f61526e2c886bddc68831b53",
        "families": "audit_activity;quarterly_tracker;archival_locator",
        "breaks": "resolución versus documento acompañante",
        "use": "USABLE_QUARTERLY_ANNEX_REQUEST_LOCATOR",
        "caveat": "Prueba que el informe y anexo existían; no contiene el anexo ni el avance del proyecto 48 0237/09.",
        "note": "V132 E0: dos páginas renderizadas; el artículo 1 aprueba el informe y dice que el anexo se adjuntó en soporte magnético.",
    },
    {
        "id": "e0_agn_api_informe_4t_2009_res44_2010",
        "filename": "agn_api_informe_4t_2009_res044_2010.json",
        "institution": "Auditoría General de la Nación",
        "title": "Ficha JSON:API · Informe de actividad AGN del cuarto trimestre de 2009 · Resolución 44/2010",
        "url": "https://webagnapi.agn.gob.ar/api/node/informes/616f80c7-65f2-4b5c-a4e9-b8bf4954600e?include=informe,resolucion_archivo",
        "publication": "2010", "period": "2009Q4", "code": "UUID 616f80c7-65f2-4b5c-a4e9-b8bf4954600e",
        "type": "JSON:API oficial · binario preservado", "bytes": 10675,
        "sha256": "c68a6035ac0bda2df5eb71608572943a0b00230f5fb62f1e1b18730be98ff677",
        "families": "audit_activity;quarterly_tracker;archival_locator",
        "breaks": "resolución pública versus anexo de actividad no enlazado",
        "use": "USABLE_QUARTERLY_RESOLUTION_METADATA",
        "caveat": "La ficha enlaza sólo la resolución; el anexo mencionado en soporte magnético no está expuesto.",
        "note": "V132 E0: localiza Res.44/2010 y Actuación 466/2009.",
    },
    {
        "id": "e0_agn_res_44_2010_4t_activity",
        "filename": "agn_res_044_2010_4t_2009.pdf",
        "institution": "Auditoría General de la Nación",
        "title": "Resolución AGN 44/2010 · Informe de actividad del cuarto trimestre de 2009",
        "url": "https://www.agn.gob.ar/sites/default/files/informes/2010_044reso_0.pdf",
        "publication": "2010-04-12", "period": "2009Q4", "code": "Resolución 44/2010; Actuación 466/09-AGN",
        "type": "PDF oficial · binario preservado", "bytes": 30142,
        "sha256": "a02e317a61221b4b163ff3e2fcf2a4756414c25871abe4886fcc218cd1e38772",
        "families": "audit_activity;quarterly_tracker;archival_locator",
        "breaks": "resolución versus documento acompañante",
        "use": "USABLE_QUARTERLY_ANNEX_REQUEST_LOCATOR",
        "caveat": "Prueba que el informe y anexo existían; no contiene el anexo ni el avance final del proyecto 48 0237/09.",
        "note": "V132 E0: dos páginas renderizadas; el artículo 1 aprueba el informe y dice que el anexo se adjuntó en soporte magnético.",
    },
    {
        "id": "e0_agn_2022_124_oncp_control_interno",
        "filename": "agn_2022_124_oncp_control_interno.pdf",
        "institution": "Auditoría General de la Nación",
        "title": "Control interno ONCP · Back office DADP · período 2016-2018 · Informe AGN 124/2022",
        "url": "https://www.agn.gob.ar/sites/default/files/informes/2022-124-Informe_0.pdf",
        "publication": "2022", "period": "2016-2018", "code": "Proyecto 4081020; Actuación 382/2019",
        "type": "PDF oficial · binario preservado", "bytes": 8305750,
        "sha256": "4b61ce2dc5245268a4cb1858e023c202beb08a86425af3710c1a6ff963f9ccc4",
        "families": "debt;record_producer;SIGADE;SIDIF;DADP;internal_control",
        "breaks": "manual 2015/período 2016-2018 versus operación 2008; declaración del auditado versus verificación",
        "use": "USABLE_RECORD_PRODUCER_AND_PROCESS_CONTROL",
        "caveat": "Identifica sistemas, archivos y subprocesos de recompra posteriores; no prueba retroactivamente el contenido ni la ejecución de 2008.",
        "note": "V132 E0: páginas 14,25,26,75,78 y 79 renderizadas; DADP, SIGADE/e-SIDIF, COMDOC, Unidad Compartida y controles de recompra quedan como blancos precisos.",
    },
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        if not rows:
            raise ValueError(f"fields required for {path}")
        fields = list(rows[0])
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bump_text(text: str) -> str:
    text = text.replace("V131", "V132")
    text = re.sub(r"\b([A-Z]{1,8})131_", r"\g<1>132_", text)
    return text


def clone_parent() -> None:
    skip = {
        "build_e0_public_settlement_exhaustion_v131.py", "qa_v131.py",
        "MANIFEST_V131.json", "INHERITED_QA_STATUS_V131.csv",
    }
    for source in V131.iterdir():
        if not source.is_file() or source.name in skip or source.name.startswith("HANDOVER_PROXIMA_SESION"):
            continue
        target = HERE / source.name.replace("V131", "V132")
        target.write_text(bump_text(source.read_text(encoding="utf-8-sig")), encoding="utf-8")


clone_parent()

for source in SOURCES:
    path = BIN / source["filename"]
    assert path.is_file(), path
    assert path.stat().st_size == source["bytes"], path
    assert sha256(path) == source["sha256"], path
    source["local"] = "/" + path.relative_to(REPO).as_posix()

# Master catalog and E0 census.
source_ids = {source["id"] for source in SOURCES}
catalog = [row for row in read_csv(CATALOG) if row["id"] not in source_ids]
for source in SOURCES:
    catalog.append({
        "id": source["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": source["institution"],
        "titulo": source["title"], "url_original": source["url"], "archivo_local": source["local"],
        "fecha_descarga": "2026-08-30", "fecha_publicacion": source["publication"],
        "codigo_serie": source["code"], "periodo_utilizado": source["period"], "tipo": source["type"],
        "sha256": source["sha256"], "nota": source["note"],
    })
assert len(catalog) == 358 and len({row["id"] for row in catalog}) == 358
write_csv(CATALOG, catalog)

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V132.csv"
census = [row for row in read_csv(census_path) if row["source_id"] not in source_ids]
for source in SOURCES:
    census.append({
        "source_id": source["id"], "institution": source["institution"], "artifact": source["title"],
        "url": source["url"], "local_path": source["local"], "sha256": source["sha256"],
        "bytes": str(source["bytes"]), "period_coverage": source["period"],
        "variable_families": source["families"], "primary_source": "YES", "preserved": "YES",
        "method_breaks": source["breaks"], "use_status": source["use"], "caveat": source["caveat"],
    })
assert len(census) == 118 and len({row["source_id"] for row in census}) == 118
write_csv(census_path, census)

# Public AGN identity bridge.
bridge_path = HERE / "E0_AGN_2008_DEBT_AUDIT_PROJECT_BRIDGE_V132.csv"
bridge = read_csv(bridge_path)
bridge[1].update({
    "record_role": "FINAL_REPORT_IDENTITY",
    "source_id": "e0_agn_res_202_2009_act_41_2009_deuda;e0_agn_api_informe_res202_act41_2009;e0_agn_res_202_2009_act_41_2009_resolution",
    "link_status": "ACT_RES_REPORT_IDENTITY_EXACT_PROJECT_CODE_CONTEXTUAL_NOT_LITERAL",
    "permitted_use": "Cerrar título, período, Actuación 41/2009 y Resolución 202/2009; describir el vínculo con 48 0237/09 como contextual fuerte.",
    "prohibited_use": "Afirmar que el código 48 0237/09 figura en la ficha, resolución o informe final.",
})
bridge.append({
    "bridge_id": "AB132_06", "record_role": "OFFICIAL_JSONAPI_IDENTITY", "source_id": "e0_agn_api_informe_res202_act41_2009",
    "identifier": "UUID b52e2e9c-90b5-4af1-bf5d-0bab8596606e", "title_or_scope": "Única ficha que coincide por Actuación 41/2009 y por Resolución 202/año 2009",
    "date_or_cutoff": "2009", "published_fact": "Actuación 41/2009; Resolución 202; período 2008; vínculos a informe y resolución",
    "locator": "JSONAPI_attributes_and_relationships", "link_status": "EXACT_FINAL_REPORT_IDENTITY",
    "permitted_use": "Eliminar la ambigüedad entre actuación, resolución y documento final.",
    "prohibited_use": "Extender esa identidad al código interno 48 0237/09 sin tabla de equivalencias.",
})
assert len(bridge) == 6
write_csv(bridge_path, bridge)

crosswalk = [
    {"crosswalk_id": "CX132_01", "layer": "PROJECT_TRACKER", "identifier": "48 0237/09", "date_or_period": "2009-06-30", "public_fact": "CUENTA DE INVERSIÓN 2008 - DEUDA PÚBLICA MONEDA EXTRANJERA Y PESOS - 2008; avance 27%", "source_id": "e0_agn_informe_segundo_trimestre_2009_act_48_0237_09", "match_basis": "EXACT_PROJECT_CODE", "status": "EXACT_PROJECT_LOCATOR", "remaining_gap": "No imprime actuación o resolución final."},
    {"crosswalk_id": "CX132_02", "layer": "FINAL_METADATA", "identifier": "UUID b52e2e9c-90b5-4af1-bf5d-0bab8596606e", "date_or_period": "2008/2009", "public_fact": "Actuación 41/2009; Resolución 202; período auditado 01/01-31/12/2008; título exacto", "source_id": "e0_agn_api_informe_res202_act41_2009", "match_basis": "UNIQUE_ACTUACION_AND_RESOLUTION_FILTER", "status": "EXACT_FINAL_IDENTITY", "remaining_gap": "El nodo no contiene 48 0237/09."},
    {"crosswalk_id": "CX132_03", "layer": "APPROVAL_RESOLUTION", "identifier": "Res.202/2009; Act.41/2009", "date_or_period": "2009-11-23", "public_fact": "Aprueba el estudio; tareas de campo hasta abril; Nota 203/09 GCDP 29/06; sin respuesta formal al vencer el plazo", "source_id": "e0_agn_res_202_2009_act_41_2009_resolution", "match_basis": "EXACT_RESOLUTION_TEXT", "status": "EXACT_PROCEDURAL_CHAIN", "remaining_gap": "No imprime el código de proyecto."},
    {"crosswalk_id": "CX132_04", "layer": "REPORT_SELF_DESCRIPTION", "identifier": "Informe final 2008", "date_or_period": "2008", "public_fact": "Dice que el informe anual de deuda se incorporó en el contexto del proyecto destinado a evaluar la Cuenta de Inversión 2008", "source_id": "e0_agn_res_202_2009_act_41_2009_deuda", "match_basis": "SAME_CONTEXT_AND_PERIOD", "status": "STRONG_CONTEXTUAL_BRIDGE", "remaining_gap": "La frase no nombra 48 0237/09."},
    {"crosswalk_id": "CX132_05", "layer": "VERDICT", "identifier": "48 0237/09 ↔ Act.41/2009/Res.202", "date_or_period": "2008-2009", "public_fact": "Final report identity is exact; project lineage is single-candidate and strongly contextual", "source_id": "multiple_primary_sources", "match_basis": "TRIANGULATION", "status": "FINAL_IDENTITY_CLOSED_PROJECT_CODE_NOT_LITERAL", "remaining_gap": "Tabla interna de equivalencias o carátula del expediente AGN."},
]
write_csv(HERE / "E0_AGN_PUBLIC_METADATA_CROSSWALK_V132.csv", crosswalk)

quarterly = [
    {"quarter_id": "QT132_01", "quarter": "2009Q2", "resolution": "191/2009", "actuacion": "256/2009", "node_uuid": "12951b1b-d13-49cf-af08-7760e4672a14", "resolution_fact": "Informe de actividad aprobado", "annex_or_report_claimed": "Informe adjunto", "public_file_relation": "YES_2009_191info_0.pdf", "project_48_0237_status": "27%", "search_control": "PUBLIC_PDF_EXACT", "status": "PUBLIC_ANNEX_RECOVERED", "request_key": "N/A"},
    {"quarter_id": "QT132_02", "quarter": "2009Q3", "resolution": "211/2009", "actuacion": "426/09-AGN", "node_uuid": "7c01261c-10a0-40f6-94f6-ae7a02be8b63", "resolution_fact": "Artículo 1 aprueba informe T3", "annex_or_report_claimed": "Anexo adjunto en soporte magnético", "public_file_relation": "NO_ONLY_RESOLUTION", "project_48_0237_status": "NOT_PUBLICLY_RECOVERED", "search_control": "Predicted info URLs return text/html, not PDF; file API has only resolution_211_2009.pdf", "status": "ANNEX_EXISTENCE_PROVED_PUBLIC_BODY_NOT_LOCATED", "request_key": "Actuación 426/09-AGN; informe y anexo T3"},
    {"quarter_id": "QT132_03", "quarter": "2009Q4", "resolution": "44/2010", "actuacion": "466/09-AGN", "node_uuid": "616f80c7-65f2-4b5c-a4e9-b8bf4954600e", "resolution_fact": "Artículo 1 aprueba informe T4", "annex_or_report_claimed": "Anexo adjunto en soporte magnético", "public_file_relation": "NO_ONLY_RESOLUTION", "project_48_0237_status": "NOT_PUBLICLY_RECOVERED", "search_control": "Predicted info URLs return text/html, not PDF; file API has only 2010_044reso_0.pdf", "status": "ANNEX_EXISTENCE_PROVED_PUBLIC_BODY_NOT_LOCATED", "request_key": "Actuación 466/09-AGN; informe y anexo T4"},
]
write_csv(HERE / "E0_AGN_QUARTERLY_ANNEX_AVAILABILITY_V132.csv", quarterly)

disclosure = [
    {"row_id": "DL132_01", "year": "2004", "sigade": "83006000", "provider_or_concept": "Caja de Valores", "amount_ars": "95172.00", "sidif_disclosure": "9309;26358;30629;41811;49879;67481;77089;98287;113996;132066;150479", "disclosure_level": "ITEMIZED", "source_id": "e0_cgn_cuenta_inversion_2004_sdp", "locator": "PDF_p72_Anexo_K", "target_2008_use": "FORMAT_FEASIBILITY_CONTROL", "caveat": "No es una operación 2008."},
    {"row_id": "DL132_02", "year": "2004", "sigade": "83008000", "provider_or_concept": "Caja de Valores", "amount_ars": "8497773.25", "sidif_disclosure": "52 individual SIDIF numbers", "disclosure_level": "ITEMIZED", "source_id": "e0_cgn_cuenta_inversion_2004_sdp", "locator": "PDF_p72_Anexo_K", "target_2008_use": "FORMAT_FEASIBILITY_CONTROL", "caveat": "Lista abreviada aquí; fuente conserva todos los números."},
    {"row_id": "DL132_03", "year": "2004", "sigade": "83095000", "provider_or_concept": "Caja de Valores", "amount_ars": "3609791.69", "sidif_disclosure": "6524;16712;31093;41808;53821;77090;92659;105283;137132;137143;148392", "disclosure_level": "ITEMIZED", "source_id": "e0_cgn_cuenta_inversion_2004_sdp", "locator": "PDF_p72_Anexo_K", "target_2008_use": "FORMAT_FEASIBILITY_CONTROL", "caveat": "No es una operación 2008."},
    {"row_id": "DL132_04", "year": "2004", "sigade": "83020000", "provider_or_concept": "Comisiones Citibank", "amount_ars": "169648.75", "sidif_disclosure": "128281;128282", "disclosure_level": "ITEMIZED", "source_id": "e0_cgn_cuenta_inversion_2004_sdp", "locator": "PDF_p72_Anexo_K", "target_2008_use": "FORMAT_FEASIBILITY_CONTROL", "caveat": "No es una operación 2008."},
    {"row_id": "DL132_05", "year": "2008", "sigade": "83006000", "provider_or_concept": "Caja de Valores", "amount_ars": "183556.00", "sidif_disclosure": "VARIOS", "disclosure_level": "AGGREGATED", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "locator": "PDF_p67_Anexo_K", "target_2008_use": "TARGET_KEY", "caveat": "Servicio anual, no recompra específica."},
    {"row_id": "DL132_06", "year": "2008", "sigade": "83008000", "provider_or_concept": "Caja de Valores", "amount_ars": "8245946.42", "sidif_disclosure": "VARIOS", "disclosure_level": "AGGREGATED", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "locator": "PDF_p67_Anexo_K", "target_2008_use": "TARGET_KEY", "caveat": "Servicio anual, no recompra específica."},
    {"row_id": "DL132_07", "year": "2008", "sigade": "83095000", "provider_or_concept": "Caja de Valores", "amount_ars": "1786212.32", "sidif_disclosure": "VARIOS", "disclosure_level": "AGGREGATED", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "locator": "PDF_p67_Anexo_K", "target_2008_use": "TARGET_KEY", "caveat": "Servicio anual, no recompra específica."},
    {"row_id": "DL132_08", "year": "2008", "sigade": "83020000", "provider_or_concept": "Comisiones Citibank", "amount_ars": "122940.67", "sidif_disclosure": "VARIOS", "disclosure_level": "AGGREGATED", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "locator": "PDF_p67_Anexo_K", "target_2008_use": "TARGET_KEY", "caveat": "Coincidencia de banco no atribuye la comisión a la recompra."},
    {"row_id": "DL132_09", "year": "2008", "sigade": "83106000", "provider_or_concept": "Comisiones Banco Nación", "amount_ars": "32270.30", "sidif_disclosure": "71597;152677;2876", "disclosure_level": "ITEMIZED", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "locator": "PDF_p67_Anexo_K", "target_2008_use": "TARGET_KEY", "caveat": "Tres comprobantes anuales; no prueban mandato o pago de la recompra."},
    {"row_id": "DL132_10", "year": "2010", "sigade": "83006000", "provider_or_concept": "Caja de Valores", "amount_ars": "202292.17", "sidif_disclosure": "VARIOS", "disclosure_level": "AGGREGATED", "source_id": "e0_cgn_cuenta_inversion_2010_sdp", "locator": "PDF_p74_Anexo_K", "target_2008_use": "DISCLOSURE_COMPARATOR", "caveat": "No es una operación 2008."},
    {"row_id": "DL132_11", "year": "2010", "sigade": "83008000", "provider_or_concept": "Caja de Valores", "amount_ars": "11053961.08", "sidif_disclosure": "VARIOS", "disclosure_level": "AGGREGATED", "source_id": "e0_cgn_cuenta_inversion_2010_sdp", "locator": "PDF_p74_Anexo_K", "target_2008_use": "DISCLOSURE_COMPARATOR", "caveat": "No es una operación 2008."},
    {"row_id": "DL132_12", "year": "2010", "sigade": "83095000", "provider_or_concept": "Caja de Valores", "amount_ars": "542582.22", "sidif_disclosure": "VARIOS", "disclosure_level": "AGGREGATED", "source_id": "e0_cgn_cuenta_inversion_2010_sdp", "locator": "PDF_p74_Anexo_K", "target_2008_use": "DISCLOSURE_COMPARATOR", "caveat": "No es una operación 2008."},
    {"row_id": "DL132_13", "year": "2010", "sigade": "83020000", "provider_or_concept": "Comisiones Citibank", "amount_ars": "1154948.47", "sidif_disclosure": "C41 21657;157867;242998;343494;343495", "disclosure_level": "ITEMIZED", "source_id": "e0_cgn_cuenta_inversion_2010_sdp", "locator": "PDF_p74_Anexo_K", "target_2008_use": "FORMAT_FEASIBILITY_CONTROL", "caveat": "Demuestra formato; no vínculo con 2008."},
    {"row_id": "DL132_14", "year": "2010", "sigade": "83106000", "provider_or_concept": "Comisiones Banco Nación", "amount_ars": "1869.45", "sidif_disclosure": "C41 5310;74291;156087;285224", "disclosure_level": "ITEMIZED", "source_id": "e0_cgn_cuenta_inversion_2010_sdp", "locator": "PDF_p74_Anexo_K", "target_2008_use": "FORMAT_FEASIBILITY_CONTROL", "caveat": "Demuestra formato; no vínculo con 2008."},
]
write_csv(HERE / "E0_SIGADE_SIDIF_DISCLOSURE_LADDER_V132.csv", disclosure)

producer = [
    {"producer_id": "RP132_01", "record_or_process": "Documentación de respaldo SIGADE", "institution_or_system": "DADP", "period_of_source": "2016-2018 / declaración 2021", "public_fact": "La DADP informó que cuenta con respaldo de los instrumentos cargados en SIGADE", "source_id": "e0_agn_2022_124_oncp_control_interno", "locator": "PDF_p14", "evidence_status": "AUDITEE_REPRESENTATION_NOT_AUDITOR_VERIFIED", "request_use": "Pedir respaldo por instrumento y expediente", "temporal_caveat": "No demuestra retención o contenido de 2008."},
    {"producer_id": "RP132_02", "record_or_process": "Validación y cierre trimestral", "institution_or_system": "SIGADE↔SIDIF", "period_of_source": "manual vigente auditado 2016-2018", "public_fact": "Proceso periódico de consistencia entre SIGADE y SIDIF", "source_id": "e0_agn_2022_124_oncp_control_interno", "locator": "PDF_p25", "evidence_status": "PROCESS_DESCRIPTION", "request_use": "Pedir conciliación y trazabilidad de comprobantes", "temporal_caveat": "No prueba una conciliación concreta de 2008."},
    {"producer_id": "RP132_03", "record_or_process": "Digitalización y gestión documental", "institution_or_system": "DADP/COMDOC; físico y electrónico", "period_of_source": "manual formalizado 2015", "public_fact": "Identificación, digitalización, registro y archivo de documentos físicos y electrónicos", "source_id": "e0_agn_2022_124_oncp_control_interno", "locator": "PDF_p25", "evidence_status": "PROCESS_DESCRIPTION", "request_use": "No limitar búsqueda del expediente 2008 a GDE", "temporal_caveat": "COMDOC/manual 2015 no prueba migración completa del archivo 2008."},
    {"producer_id": "RP132_04", "record_or_process": "Base SIGADE", "institution_or_system": "SIGADE", "period_of_source": "manual formalizado 2015", "public_fact": "Capacidad de informar desembolsos y pagos históricos, gastos asociados y ciclo de vida", "source_id": "e0_agn_2022_124_oncp_control_interno", "locator": "PDF_p26", "evidence_status": "SYSTEM_CAPABILITY_DESCRIPTION", "request_use": "Pedir extractos históricos y campos de pago/gasto", "temporal_caveat": "Capacidad sistémica no equivale a registro target recuperado."},
    {"producer_id": "RP132_05", "record_or_process": "I.f.2 Recompra de títulos", "institution_or_system": "DADP Unidad Compartida→SIGADE", "period_of_source": "manual formalizado 2015", "public_fact": "Carga manual punto 14 y control manual punto 16", "source_id": "e0_agn_2022_124_oncp_control_interno", "locator": "PDF_p75_Cuadro11", "evidence_status": "EXACT_PROCESS_LOCATOR_POST_2008", "request_use": "Pedir planillas, carga y control por recompra", "temporal_caveat": "No afirmar que esos números de paso regían en 2008."},
    {"producer_id": "RP132_06", "record_or_process": "I.b.4 Revisión de una recompra de títulos", "institution_or_system": "Integridad SIGADE", "period_of_source": "manual formalizado 2015", "public_fact": "Revisión puntos 3/4 y comparación con otra base puntos 6/6.2/7", "source_id": "e0_agn_2022_124_oncp_control_interno", "locator": "PDF_pp78_79_Cuadro11", "evidence_status": "EXACT_CONTROL_LOCATOR_POST_2008", "request_use": "Pedir base comparada, revisión y correcciones", "temporal_caveat": "No prueba una revisión concreta de 2008."},
    {"producer_id": "RP132_07", "record_or_process": "Expediente S01:0342455/2008", "institution_or_system": "ONCP→DADP", "period_of_source": "2008", "public_fact": "La norma ordena listado de preadjudicación ONCP y custodia documental DADP", "source_id": "e0_rc_212_24_2008_procedimiento_recompra", "locator": "Anexo_1.8_1.13", "evidence_status": "EXACT_PRODUCER_AND_CUSTODIAN", "request_use": "Pedir índice, cuerpo, listado y documentación de liquidación", "temporal_caveat": "La norma no publica el cuerpo ni prueba ejecución de cada adjudicación."},
]
write_csv(HERE / "E0_ONCP_SIGADE_RECORD_PRODUCER_CONTROL_V132.csv", producer)

exp_search = [
    {"search_id": "EX132_01", "target": "S01:0342455/2008", "route": "búsqueda web exacta general", "result": "Sólo norma InfoLEG/Argentina.gob.ar y reproducción en Boletín Oficial", "public_body_found": "NO", "status": "NORM_ONLY", "permitted_inference": "El expediente existía al dictarse la norma.", "forbidden_inference": "El cuerpo fue destruido o no existe."},
    {"search_id": "EX132_02", "target": "S01:0342455/2008", "route": "argentina.gob.ar; boletinoficial.gob.ar; economia.gob.ar", "result": "Ningún índice, foja, listado ONCP o comprobante adicional localizado", "public_body_found": "NO", "status": "OFFICIAL_PUBLIC_ROUTES_EXHAUSTED", "permitted_inference": "El cuerpo no está recuperado en las rutas públicas consultadas.", "forbidden_inference": "No hubo preadjudicación o liquidación."},
    {"search_id": "EX132_03", "target": "S01:0342455/2008", "route": "Resolución Conjunta 212/2008-24/2008", "result": "ONCP produce listado; DADP conserva documentación; Caja y BCRA intervienen en liquidación", "public_body_found": "PROCEDURE_ONLY", "status": "EXACT_RECORD_PRODUCER_MAP", "permitted_inference": "El pedido puede dirigirse por objeto, productor y custodio.", "forbidden_inference": "El procedimiento prueba la ejecución de las diez filas."},
    {"search_id": "EX132_04", "target": "SIGADE/SIDIF 2008", "route": "CGN 2004/2008/2010 + AGN 124/2022", "result": "La desagregación SIDIF/C-41 existe en ejercicios comparadores y SIGADE se concilia con SIDIF", "public_body_found": "FORMAT_AND_SYSTEM_ONLY", "status": "REQUEST_FEASIBILITY_DEMONSTRATED", "permitted_inference": "Es razonable pedir submayor y comprobantes por claves exactas.", "forbidden_inference": "Los importes anuales corresponden al programa de recompra."},
]
write_csv(HERE / "E0_EXPEDIENT_PUBLIC_SEARCH_EXHAUSTION_V132.csv", exp_search)

# Update public-route verdicts.
public_path = HERE / "E0_PUBLIC_SETTLEMENT_RECORD_EXHAUSTION_V132.csv"
public = read_csv(public_path)
for row in public:
    if row["route_id"] == "PE132_01":
        row.update({"public_record_located": "Procedure, producer/custodian and later record-system classes", "status": "PRODUCER_SYSTEM_CONFIRMED_EXPEDIENT_BODY_NOT_PUBLIC", "usable_result": "Exact expediente, ONCP/DADP roles and SIGADE/COMDOC record classes fixed.", "still_needed": "Index, body, preaward list, Unidad Compartida/SIGADE extracts and orders."})
    elif row["route_id"] == "PE132_06":
        row.update({"public_record_located": "2008 annual keys plus itemized SIDIF disclosure comparators 2004/2010", "status": "AGGREGATE_2008_KEYS_RECORD_FORMAT_DEMONSTRATED", "usable_result": "Exact keys and feasibility of document-ID production demonstrated.", "still_needed": "2008 subledger and vouchers tied to expediente, date, ISIN and participant."})
    elif row["route_id"] == "PE132_07":
        row.update({"public_record_located": "Exact API identity for report/Act.41/Res.202 plus project-context bridge", "status": "FINAL_IDENTITY_CLOSED_PROJECT_CODE_CONTEXTUAL_NOT_LITERAL", "usable_result": "Final report identity closed; remaining crosswalk is only internal project code and workpapers.", "still_needed": "48 0237/09 equivalence table, T3/T4 activity annexes and audit workpapers."})
write_csv(public_path, public)

# Promote ledger with non-additive evidence controls only.
ledger_path = HERE / "E0_FISCAL_MECHANISM_LEDGER_V132.csv"
ledger = read_csv(ledger_path)
for row in ledger:
    if row["ledger_id"] == "F145":
        row.update({
            "source_id": "e0_agn_informe_segundo_trimestre_2009_act_48_0237_09;e0_agn_res_202_2009_act_41_2009_deuda;e0_agn_api_informe_res202_act41_2009;e0_agn_res_202_2009_act_41_2009_resolution",
            "source_locator": "tracker_p22;report_p3;official_api;resolution_pp1_3",
            "realization_status": "FINAL_REPORT_IDENTITY_CLOSED_PROJECT_CODE_CONTEXTUAL_NOT_LITERAL",
            "status_interpretation": "Actuación 41/2009, Resolución 202/2009 and the final report are one exact public record; 48 0237/09 is a strong contextual project bridge.",
            "caveat": "No public source prints the internal project code together with the final identifiers; none is operation-level settlement evidence.",
        })
ledger.extend([
    {"ledger_id": "F149", "window": "2008-2009", "mechanism": "Debt_audit_2008", "phase": "AGN_FINAL_REPORT_IDENTITY", "as_of_date": "2009", "payer": "N/A", "recipient": "N/A", "universe": "AGN_public_metadata", "instrument": "Act41_Res202_UUID", "amount_original": "1", "original_unit": "EXACT_UNIQUE_RECORD", "normalized_ars_million": "N/D", "valuation_basis": "JSONAPI_EXACT_FILTER", "source_id": "e0_agn_api_informe_res202_act41_2009;e0_agn_res_202_2009_act_41_2009_resolution", "source_locator": "attributes;relationships;resolution_pp1_3", "realization_status": "FINAL_REPORT_IDENTITY_CLOSED", "additivity": "NON_ADDITIVE", "status_interpretation": "Actuación, resolución, título and period identify one final report.", "caveat": "The internal project code is not printed."},
    {"ledger_id": "F150", "window": "2009Q2-2009Q4", "mechanism": "Debt_audit_2008", "phase": "AGN_PROJECT_CONTEXT_AND_QUARTERLY_ANNEX_CHAIN", "as_of_date": "2010-04-12", "payer": "N/A", "recipient": "N/A", "universe": "AGN_activity_reports", "instrument": "48_0237_09_Act426_Act466", "amount_original": "2", "original_unit": "MISSING_PUBLIC_ANNEXES", "normalized_ars_million": "N/D", "valuation_basis": "Q2_TRACKER_PLUS_Q3_Q4_RESOLUTIONS", "source_id": "multiple_agn_primary_sources", "source_locator": "QT132_01_03", "realization_status": "PROJECT_CONTEXT_STRONG_Q3_Q4_ANNEX_BODY_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "Q3 and Q4 resolutions prove accompanying annexes existed but public bodies were not recovered.", "caveat": "No inference about final project percentage from missing annexes."},
    {"ledger_id": "F151", "window": "2004/2008/2010", "mechanism": "Debt_accounting_disclosure", "phase": "SIGADE_SIDIF_DISCLOSURE_LADDER", "as_of_date": "2010-12-31", "payer": "Tesoro_Nacional", "recipient": "Multiple_service_providers", "universe": "CGN_Anexo_K", "instrument": "83006000_83008000_83095000_83020000_83106000", "amount_original": "14", "original_unit": "DISCLOSURE_ROWS", "normalized_ars_million": "N/D", "valuation_basis": "ANNUAL_COMPARATOR", "source_id": "e0_cgn_cuenta_inversion_2004_sdp;e0_cgn_cuenta_inversion_2008_sdp;e0_cgn_cuenta_inversion_2010_sdp", "source_locator": "PDF_p72_p67_p74", "realization_status": "ITEMIZED_FORMAT_FEASIBLE_TARGET_ALLOCATION_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "Same account families can disclose individual SIDIF/C-41 IDs, while some annual rows use VARIOS.", "caveat": "Cross-year disclosure format does not allocate 2008 fees to buybacks."},
    {"ledger_id": "F152", "window": "2016-2018", "mechanism": "Debt_record_production", "phase": "DADP_SIGADE_REPURCHASE_PROCESS_MAP", "as_of_date": "2022", "payer": "N/A", "recipient": "N/A", "universe": "ONCP_DADP_back_office", "instrument": "If2_Ib4_SIGADE_SIDIF_COMDOC", "amount_original": "7", "original_unit": "RECORD_PROCESS_LOCATORS", "normalized_ars_million": "N/D", "valuation_basis": "AGN_124_2022", "source_id": "e0_agn_2022_124_oncp_control_interno", "source_locator": "PDF_pp14_25_26_75_78_79", "realization_status": "PRODUCER_AND_RECORD_CLASSES_CONFIRMED_POST_2008", "additivity": "NON_ADDITIVE", "status_interpretation": "The later manual/audit makes the missing record classes individually targetable.", "caveat": "Manual 2015 and audit period 2016-2018 do not retroactively prove 2008 contents."},
    {"ledger_id": "F153", "window": "2008", "mechanism": "Debt_buyback_excess_GDP", "phase": "EXPEDIENT_PUBLIC_BODY_SEARCH", "as_of_date": "2026-08-30", "payer": "N/A", "recipient": "N/A", "universe": "S01_0342455_2008", "instrument": "ONCP_DADP_exp_file", "amount_original": "0", "original_unit": "PUBLIC_BODY_ROWS_RECOVERED", "normalized_ars_million": "N/D", "valuation_basis": "OFFICIAL_DOMAIN_SEARCH", "source_id": "e0_rc_212_24_2008_procedimiento_recompra", "source_locator": "EX132_01_04", "realization_status": "NORM_ONLY_BODY_NOT_LOCATED_PUBLICLY", "additivity": "NON_ADDITIVE", "status_interpretation": "The public norm proves file identity and custody, not body availability.", "caveat": "Zero public body rows is not zero execution."},
    {"ledger_id": "F154", "window": "2008-09-02/2008-10-07", "mechanism": "Debt_buyback_excess_GDP", "phase": "EXECUTED_SETTLEMENT_EVIDENCE_STATUS_REVALIDATED", "as_of_date": "2026-08-30", "payer": "Tesoro_Nacional", "recipient": "Named_participants_ultimate_holders_open", "universe": "Ten_GDP_rows", "instrument": "full_settlement_chain", "amount_original": "0/10", "original_unit": "EXECUTED_ROWS_CONFIRMED", "normalized_ars_million": "N/D", "valuation_basis": "V132_PUBLIC_RESEARCH", "source_id": "multiple_primary_sources", "source_locator": "E0_SETTLEMENT_EVIDENCE_LADDER_SUMMARY_V132.csv", "realization_status": "UNCHANGED_ZERO_CONFIRMED_NOT_ZERO_PAYMENTS", "additivity": "NON_ADDITIVE", "status_interpretation": "New metadata strengthens requests but does not add a settlement execution row.", "caveat": "Never convert an evidence gap into a monetary zero."},
])
assert len(ledger) == 154 and len({row["ledger_id"] for row in ledger}) == 154
write_csv(ledger_path, ledger)

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V132.csv"
breaks = read_csv(breaks_path)
for row in breaks:
    if row["break_id"] == "agn_project_code_not_automatic_final_act_crosswalk":
        row.update({"problem": "The final report/Act.41/Res.202 identity is now exact, while the internal code 48 0237/09 remains absent from final metadata.", "rule": "Close final identity; describe project lineage as strong contextual bridge until an internal equivalence table is produced.", "status": "PARTIALLY_CLOSED_V132", "evidence": "AGN API UUID; Res.202/2009; Q2 tracker; report self-description"})
breaks.extend([
    {"break_id": "agn_final_identity_not_literal_project_code", "dimension": "identity", "problem": "Exact final metadata does not print 48 0237/09.", "rule": "Do not collapse final identity and internal project-code identity into one claim.", "status": "FROZEN", "evidence": "CX132_01_05"},
    {"break_id": "quarterly_resolution_not_public_activity_annex", "dimension": "document_scope", "problem": "Q3/Q4 resolutions prove reports and magnetic annexes but public nodes expose only resolutions.", "rule": "Treat annex existence as exact and annex contents/progress as open.", "status": "FROZEN", "evidence": "QT132_02_03"},
    {"break_id": "post_2008_dadp_process_not_2008_execution_record", "dimension": "time", "problem": "The DADP manual formalized in 2015 and audit period 2016-2018 identify record classes after the target events.", "rule": "Use them to target records, never as retroactive proof of 2008 execution or retention.", "status": "FROZEN", "evidence": "AGN 124/2022 pp14,25,26,75,78,79"},
    {"break_id": "sidif_itemization_format_not_target_transaction", "dimension": "scope", "problem": "Other years publish individual SIDIF/C-41 IDs for the same account families.", "rule": "Use comparators to demonstrate feasible format, not to allocate 2008 annual fees.", "status": "FROZEN", "evidence": "CGN 2004/2008/2010 Anexo K"},
    {"break_id": "official_exp_reference_not_public_exp_body", "dimension": "realization", "problem": "The norm cites S01:0342455/2008 and custodians but the body is not public.", "rule": "Separate existence/identity of the file from recovery of its contents and from execution.", "status": "FROZEN", "evidence": "RC 212/2008-24/2008; EX132_01_04"},
])
assert len(breaks) == 114 and len({row["break_id"] for row in breaks}) == 114
write_csv(breaks_path, breaks)

trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V132.csv"
trace = read_csv(trace_path)
trace.extend([
    {"trace_id": "TR132_097", "request_id": "REQ132_AGN", "institution": "Auditoría General de la Nación", "gap_id": "CL132_AGN_REPLY", "requested_record": "Tabla de equivalencia entre proyecto 48 0237/09 y Actuación 41/2009 / Resolución 202/2009", "period_or_date": "2009", "identifiers": "48 0237/09;Act.41/2009;Res.202/2009;UUID b52e2e9c-90b5-4af1-bf5d-0bab8596606e", "minimum_usable_fields": "código proyecto;actuación;resolución;fecha;expediente;unidad", "confidentiality_fallback": "certificación de equivalencia sin papeles sustantivos", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR132_098", "request_id": "REQ132_AGN", "institution": "Auditoría General de la Nación", "gap_id": "CL132_AGN_REPLY", "requested_record": "Informe y anexo del tercer trimestre de 2009", "period_or_date": "2009Q3", "identifiers": "Res.211/2009;Act.426/09-AGN;UUID 7c01261c-10a0-40f6-94f6-ae7a02be8b63", "minimum_usable_fields": "proyecto;avance;estado;fecha;observación", "confidentiality_fallback": "filas 48 0237/09 y proyectos conexos", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR132_099", "request_id": "REQ132_AGN", "institution": "Auditoría General de la Nación", "gap_id": "CL132_AGN_REPLY", "requested_record": "Informe y anexo del cuarto trimestre de 2009", "period_or_date": "2009Q4", "identifiers": "Res.44/2010;Act.466/09-AGN;UUID 616f80c7-65f2-4b5c-a4e9-b8bf4954600e", "minimum_usable_fields": "proyecto;avance;estado;fecha;observación", "confidentiality_fallback": "filas 48 0237/09 y proyectos conexos", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR132_100", "request_id": "REQ132_ECON", "institution": "Ministerio de Economía / ONCP / DADP", "gap_id": "CL132_DEBT_ACCOUNTING", "requested_record": "Documentos del subproceso de recompra, respaldo SIGADE y base comparada", "period_or_date": "2008", "identifiers": "S01:0342455/2008;I.f.2;I.b.4;SIGADE;SIDIF;COMDOC;TITULOS;CONTABLE", "minimum_usable_fields": "archivo;fecha;usuario/rol;ISIN;nominal;precio;efectivo;orden;estado;comprobante", "confidentiality_fallback": "índice, log y cuadro agregado por fecha/ISIN con terceros testados", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR132_101", "request_id": "REQ132_ECON", "institution": "Ministerio de Economía / DADP / CGN", "gap_id": "CL132_DEBT_ACCOUNTING", "requested_record": "Desagregación SIDIF/C-41 de las cinco claves SIGADE 2008", "period_or_date": "2008", "identifiers": "83006000;83008000;83095000;83020000;83106000", "minimum_usable_fields": "SIGADE;SIDIF/C41;fecha;proveedor;concepto;importe;expediente;orden", "confidentiality_fallback": "lista de comprobantes y totales mensuales por clave", "status": "DRAFT_NOT_SENT"},
])
assert len(trace) == 101 and len({row["trace_id"] for row in trace}) == 101
write_csv(trace_path, trace)

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V132.csv"
keys = read_csv(keys_path)
keys.extend([
    {"key_id": "SK132_81", "request_id": "REQ132_AGN", "key_group": "final_api_uuid", "exact_key": "b52e2e9c-90b5-4af1-bf5d-0bab8596606e", "search_purpose": "identificar ficha final única", "source_or_basis": "AGN JSON:API", "caveat": "No contiene código de proyecto."},
    {"key_id": "SK132_82", "request_id": "REQ132_AGN", "key_group": "q3_activity_annex", "exact_key": "Res211/2009;Act426/09-AGN;UUID7c01261c-10a0-40f6-94f6-ae7a02be8b63", "search_purpose": "recuperar informe/anexo T3", "source_or_basis": "AGN resolution and API", "caveat": "Resolución no contiene anexo."},
    {"key_id": "SK132_83", "request_id": "REQ132_AGN", "key_group": "q4_activity_annex", "exact_key": "Res44/2010;Act466/09-AGN;UUID616f80c7-65f2-4b5c-a4e9-b8bf4954600e", "search_purpose": "recuperar informe/anexo T4", "source_or_basis": "AGN resolution and API", "caveat": "Resolución no contiene anexo."},
    {"key_id": "SK132_84", "request_id": "REQ132_ECON", "key_group": "dadp_repurchase_subprocess", "exact_key": "I.f.2 Recompra de títulos;puntos14,16", "search_purpose": "localizar planilla de carga y control", "source_or_basis": "AGN 124/2022 p75", "caveat": "Manual 2015 posterior a 2008."},
    {"key_id": "SK132_85", "request_id": "REQ132_ECON", "key_group": "sigade_integrity_review", "exact_key": "I.b.4 Revisión de una recompra;puntos3,4,6,6.2,7", "search_purpose": "localizar revisión, comparación y correcciones", "source_or_basis": "AGN 124/2022 pp78-79", "caveat": "Proceso posterior no prueba revisión target."},
    {"key_id": "SK132_86", "request_id": "REQ132_ECON", "key_group": "document_systems", "exact_key": "COMDOC;SIGADE;e-SIDIF;Unidad Compartida/TITULOS/CONTABLE", "search_purpose": "buscar expediente y respaldos sin limitar a GDE", "source_or_basis": "AGN 124/2022 pp25-26", "caveat": "Migración/retención 2008 no demostrada."},
    {"key_id": "SK132_87", "request_id": "REQ132_ECON", "key_group": "cgn_2004_itemization", "exact_key": "83006000;83008000;83095000;83020000;SIDIF itemizados", "search_purpose": "demostrar formato de salida históricamente publicado", "source_or_basis": "CGN 2004 Anexo K p72", "caveat": "No son comprobantes 2008."},
    {"key_id": "SK132_88", "request_id": "REQ132_ECON", "key_group": "cgn_2010_itemization", "exact_key": "83020000 C41 21657/157867/242998/343494/343495;83106000 C41 5310/74291/156087/285224", "search_purpose": "demostrar desagregación C-41 por mismas claves", "source_or_basis": "CGN 2010 Anexo K p74", "caveat": "No son comprobantes 2008."},
    {"key_id": "SK132_89", "request_id": "REQ132_AGN", "key_group": "auditee_notice", "exact_key": "Nota203/09GCDP 29/06/2009;Act41/2009", "search_purpose": "recuperar remisión y respuesta tardía eventual", "source_or_basis": "Res202/2009 p1-2", "caveat": "Sin respuesta al vencimiento no significa aceptación."},
    {"key_id": "SK132_90", "request_id": "REQ132_ECON", "key_group": "expedient_exact", "exact_key": "S01:0342455/2008;ONCP;DADP;COMDOC;archivo físico", "search_purpose": "localizar índice y cuerpo por todas las rutas documentales", "source_or_basis": "RC212/2008-24/2008;AGN124/2022", "caveat": "El cuerpo no está localizado públicamente."},
])
assert len(keys) == 90 and len({row["key_id"] for row in keys}) == 90
write_csv(keys_path, keys)

# Narrower request addenda; all remain unsent.
request_addenda = {
    "REQUEST_AGN_2018_REPLY_V132.md": """

## Clave V132 · identidad final cerrada y anexos trimestrales faltantes

La ficha pública JSON:API `b52e2e9c-90b5-4af1-bf5d-0bab8596606e` permite cerrar la identidad entre el informe final, la Actuación `41/2009` y la Resolución `202/2009`. Resta únicamente certificar la equivalencia con el código interno `48 0237/09`. Se solicitan esa tabla/carátula y los informes con anexos aprobados por Resolución `211/2009`, Actuación `426/09-AGN` (tercer trimestre), y Resolución `44/2010`, Actuación `466/09-AGN` (cuarto trimestre), cuyas resoluciones dicen que los anexos fueron acompañados en soporte magnético pero la ficha pública no los enlaza.
""",
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V132.md": """

## Clave V132 · productor, sistemas y formato de salida demostrados

El informe AGN 124/2022 identifica a DADP como back office, la conciliación `SIGADE↔SIDIF`, gestión documental física/electrónica y los subprocesos `I.f.2 Recompra de títulos` e `I.b.4 Revisión de una recompra de títulos`. Es un control posterior y no se invoca como prueba de ejecución 2008; se usa para individualizar planillas, respaldos, revisiones, bases comparadas y comprobantes que deben buscarse por `S01:0342455/2008`, incluso fuera de GDE.

Las Cuentas de Inversión 2004 y 2010 publican números SIDIF/C-41 individuales para las mismas familias SIGADE que en 2008 aparecen como `VARIOS`. Por ello se solicita la salida equivalente de 2008 para `83006000`, `83008000`, `83095000`, `83020000` y `83106000`, con fecha, concepto, proveedor, importe, orden y expediente. Los comparadores demuestran formato; no atribuyen esos gastos a las recompras.
""",
}
for filename, addendum in request_addenda.items():
    path = HERE / filename
    path.write_text(path.read_text(encoding="utf-8-sig").rstrip() + addendum, encoding="utf-8")

closures_path = HERE / "E0_REQUEST_CLOSURE_CRITERIA_V132.csv"
closures = read_csv(closures_path)
for row in closures:
    if row["gap_id"] == "CL132_AGN_REPLY":
        row["initial_status"] = "FINAL_REPORT_IDENTITY_CLOSED_PROJECT_CODE_AND_Q3_Q4_ANNEXES_OPEN_NOT_SENT"
    if row["gap_id"] == "CL132_DEBT_ACCOUNTING":
        row["does_not_close"] = "Proceso DADP posterior, formato SIDIF comparador o referencia normativa al expediente no cierran el cuerpo 2008 ni la liquidación."
        row["initial_status"] = "PRODUCER_SYSTEM_AND_FORMAT_CONFIRMED_TARGET_RECORDS_OPEN_NOT_SENT"
write_csv(closures_path, closures)

episode_path = HERE / "HISTORICAL_EPISODE_MATRIX_2001_2026_V132.csv"
episode = read_csv(episode_path)
for row in episode:
    if row["variable"] == "gdp_units_excess_gdp_repurchase_scope":
        row["source_id"] += ";e0_agn_api_informe_res202_act41_2009;e0_agn_2022_124_oncp_control_interno"
        row["source_quality"] = "PRIMARY_AWARDS_EXACT_PUBLIC_ROUTES_EXHAUSTED_RECORD_PRODUCERS_MAPPED"
        row["status"] = "AWARDS_CLOSED_ACCOUNTS_NINE_ROWS_FINAL_AUDIT_IDENTITY_CLOSED_EXECUTED_SETTLEMENT_ZERO_CONFIRMED"
        row["notes"] = "Final AGN identity is exact; internal project code and executed records remain open; later DADP process map is request-target evidence only."
write_csv(episode_path, episode)

coverage_path = HERE / "HISTORICAL_EVIDENCE_COVERAGE_V132.csv"
coverage = read_csv(coverage_path)
for row in coverage:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row["quality"] = "PRIMARY_REFERENCE_2006_AWARDS_EXACT_PLUS_PUBLIC_ROUTE_EXHAUSTION_AND_RECORD_PRODUCER_MAP"
        row["gap"] = "Faltan cuerpo S01, preaward ONCP, Caja T+2/T+3, órdenes/créditos, ruta MERVAL, CRyL, titulares finales, Q3/Q4 AGN y blotter directo."
        row["next_action"] = "Recuperar anexos AGN 426/09 y 466/09, expediente/submayores DADP-SIGADE-SIDIF y ejecución; no enviar sin autorización."
write_csv(coverage_path, coverage)

queue_path = HERE / "HISTORICAL_SOURCE_QUEUE_V132.csv"
queue = read_csv(queue_path)
for row in queue:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row["status"] = "PUBLIC_METADATA_AND_PRODUCER_MAP_EXHAUSTED_EXECUTED_CHAIN_OPEN_NOT_SENT"
        row["why"] = "AGN API closes final identity; DADP/SIGADE/SIDIF/COMDOC and disclosure comparators make missing records individually targetable."
        row["next_action"] = "Recover AGN quarterly annexes, S01 body, DADP process records, 2008 subledgers and settlement messages; preserve no-request gate."
write_csv(queue_path, queue)

reconstruction = """# Reconstrucción fiscal E0 · V132

## Resultado

V132 cierra una identidad documental y estrecha dos vacíos; no agrega una liquidación. La ficha oficial única vincula exactamente el informe final de deuda 2008 con la Actuación 41/2009 y la Resolución 202/2009. El vínculo con el proyecto 48 0237/09 es fuerte y de candidato único porque el informe se autoubica en el proyecto de Cuenta de Inversión 2008, pero ningún documento público imprime ambos códigos juntos.

Las resoluciones 211/2009 y 44/2010 prueban que existieron informes y anexos de actividad para T3 y T4 de 2009. Sus fichas públicas sólo exponen las resoluciones; los anexos, declarados en soporte magnético, no fueron recuperados. Quedan pedidos por Actuaciones 426/09-AGN y 466/09-AGN.

## Expediente y contabilidad

La búsqueda exacta de S01:0342455/2008 devuelve la norma y no el cuerpo. La norma fija a ONCP como productora del listado y a DADP como custodio. AGN 124/2022 identifica, para un período posterior, DADP, SIGADE/e-SIDIF, COMDOC, Unidad Compartida y subprocesos específicos de recompra. Se usan como mapa de productores, no como prueba retroactiva de 2008.

Las Cuentas de Inversión 2004 y 2010 muestran que las mismas familias SIGADE pueden publicarse con números SIDIF/C-41 individuales. En 2008, cuatro filas objetivo están agregadas como VARIOS y Banco Nación enumera tres comprobantes. Esto demuestra que el pedido de desagregación es técnicamente concreto; no asigna los importes anuales a la recompra.

La escalera permanece en 10/10 adjudicaciones, 9/10 cuentas candidatas y 0/10 ejecuciones confirmadas. Cero confirmado es cobertura de evidencia, nunca pago cero. Seis pedidos continúan DRAFT_NOT_SENT y ninguno fue enviado.
"""
(HERE / "E0_FISCAL_RECONSTRUCTION_V132.md").write_text(reconstruction, encoding="utf-8")

(HERE / "README_V132.md").write_text("""# V132 · identidad AGN y productores documentales

V132 cierra exactamente informe final–Actuación 41/2009–Resolución 202/2009, conserva el código 48 0237/09 como vínculo contextual fuerte no literal, identifica los anexos trimestrales faltantes y mapea DADP/SIGADE/SIDIF/COMDOC como productores. Los comparadores CGN demuestran que la desagregación de comprobantes es un formato real. No aparece una liquidación nueva: 10/10 adjudicaciones, 9/10 cuentas candidatas y 0/10 ejecuciones confirmadas. Seis pedidos siguen DRAFT_NOT_SENT.
""", encoding="utf-8")

(HERE / "VEREDICTO_V132.md").write_text("""# Veredicto V132

La ambigüedad entre la Actuación 41/2009, la Resolución 202/2009 y el informe final quedó eliminada por la ficha pública oficial. El único límite que subsiste es el código interno 48 0237/09: la filiación es documentalmente fuerte, pero no literal.

El expediente S01:0342455/2008 sigue sin cuerpo público. Ahora el reclamo puede nombrar productor, custodio, sistemas, carpetas y subprocesos, y puede demostrar con publicaciones CGN que una salida SIDIF/C-41 individualizada es practicable. Eso fortalece el pedido, no demuestra pago ni beneficiario final.

La ejecución continúa abierta en 0/10 filas confirmadas. CLOSED_NETWORK_GATE=NO; seis borradores, ninguno enviado.
""", encoding="utf-8")

(HERE / "RETRIEVAL_LOG_V132.md").write_text("""# Registro de recuperación V132

Fecha: 2026-08-30.

1. Se consultó el catálogo JSON:API de AGN. Los filtros por Actuación 41/2009 y por Resolución 202/año 2009 devolvieron el mismo UUID único.
2. Se preservaron ficha y resolución final; las tres páginas de la resolución fueron renderizadas.
3. Se localizaron T3/2009 (Res.211; Act.426/09) y T4/2009 (Res.44/2010; Act.466/09). Sus resoluciones prueban anexos en soporte magnético; los nodos y el inventario público no exponen esos anexos.
4. Las rutas predichas de informe T3/T4 respondieron HTML, no PDF; se evitó registrarlas como hallazgo positivo.
5. La búsqueda exacta de S01:0342455/2008 en rutas oficiales sólo recuperó la norma, no el cuerpo.
6. Se verificaron visualmente Anexo K 2004, 2008 y 2010: existen desagregaciones SIDIF/C-41 para las mismas familias de claves, alternadas con VARIOS.
7. Se preservó AGN 124/2022 y se verificaron páginas 14,25,26,75,78,79 para DADP, SIGADE/SIDIF, gestión documental y subprocesos de recompra, manteniendo el corte temporal 2015/2016-2018.
8. Dos descargas duplicadas de CGN 2004/2010 en v132 fueron eliminadas tras verificar hashes idénticos; permanecen las copias preservadas v111/v112.
9. No se envió ningún pedido ni se realizó presentación externa.
""", encoding="utf-8")

refs_path = HERE / "SOURCE_REFERENCES_V132.md"
refs = refs_path.read_text(encoding="utf-8-sig").rstrip()
refs += """
- AGN JSON:API informe final: https://webagnapi.agn.gob.ar/api/node/informes/b52e2e9c-90b5-4af1-bf5d-0bab8596606e?include=informe,resolucion_archivo,ficha,anexo
- AGN Resolución 202/2009: https://www.agn.gob.ar/sites/default/files/informes/2009_202Reso.pdf
- AGN Resolución 211/2009: https://www.agn.gob.ar/sites/default/files/informes/resolucion_211_2009.pdf
- AGN Resolución 44/2010: https://www.agn.gob.ar/sites/default/files/informes/2010_044reso_0.pdf
- AGN Control interno ONCP/DADP 124/2022: https://www.agn.gob.ar/sites/default/files/informes/2022-124-Informe_0.pdf
- CGN Cuenta de Inversión 2004: https://www.economia.gob.ar/hacienda/cgn/cuenta/2004/archivos/sdp.pdf
- CGN Cuenta de Inversión 2008: https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/archivos/sdp.pdf
- CGN Cuenta de Inversión 2010: https://www.economia.gob.ar/hacienda/cgn/cuenta/2010/archivos/sdp.pdf

Las fuentes posteriores describen productores y formatos; no se usan como prueba retroactiva de ejecución 2008.
"""
refs_path.write_text(refs, encoding="utf-8")

handover = """# Handover V132 → V133

## Estado congelado

- Diez adjudicaciones participante–instrumento exactas; nueve cuentas BCRA candidatas; MERVAL abierta.
- 0/10 filas con preadjudicación ejecutada, transferencia Caja, informe T+3, crédito BCRA o cancelación CRyL confirmados. Es cobertura probatoria, no importe cero.
- Identidad final AGN cerrada: UUID `b52e2e9c-90b5-4af1-bf5d-0bab8596606e`, Actuación `41/2009`, Resolución `202/2009`, período 2008.
- Proyecto `48 0237/09`: vínculo contextual fuerte y de candidato único; código no literal en ficha/resolución/informe final.
- T3/T4: informes y anexos probados por Res.211/2009 Act.426/09 y Res.44/2010 Act.466/09; cuerpos no recuperados públicamente.
- `S01:0342455/2008`: norma, productor ONCP y custodio DADP exactos; cuerpo público no localizado.
- DADP/SIGADE/e-SIDIF/COMDOC y subprocesos I.f.2/I.b.4 identificados por AGN 124/2022 con corte temporal posterior.
- CGN 2004/2008/2010 demuestra alternancia entre SIDIF/C-41 individualizados y VARIOS; formato de pedido probado, asignación a recompra abierta.
- Brecha aritmética AGN USD 769m continúa congelada sin imputación.
- Seis pedidos DRAFT_NOT_SENT; ninguno enviado; panel estricto sin cambios.

## Prioridad V133

1. Buscar copias archivadas o remisiones parlamentarias de los anexos AGN de Actuaciones 426/09 y 466/09.
2. Buscar índices COMDOC/archivo histórico y referencias GDE de migración para S01:0342455/2008, sin asumir continuidad documental.
3. Intentar localizar salidas públicas o anexos de conciliación SIGADE–SIDIF 2008 por las cinco claves.
4. Mantener separados expediente, submayor, orden de pago, crédito BCRA, transferencia Caja y cancelación CRyL.
5. No enviar los seis pedidos sin autorización expresa.
"""
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V132_A_V133.md").write_text(handover, encoding="utf-8")

(HERE / "AUDITORIA_V132.md").write_text(f"""# Auditoría V132

- Fuentes maestras: {len(catalog)}; siete fuentes oficiales nuevas preservadas.
- Fuentes primarias E0: {len(census)}.
- Ledger fiscal: {len(ledger)} filas; cortes metodológicos: {len(breaks)}.
- AGN final: Act.41/2009/Res.202 exactas; 48 0237/09 contextual fuerte no literal; T3/T4 annex bodies open.
- Expediente: producer/custodian and later record classes mapped; public body not located.
- CGN: itemized SIDIF format demonstrated; target allocation open.
- Escalera: 10 adjudicaciones; 9 cuentas candidatas; 0 ejecuciones confirmadas.
- Pedidos: 6 borradores, 0 enviados; {len(trace)} objetos y {len(keys)} claves.
- Panel estricto: 30 entidades; {STRICT}% sin cambios.
""", encoding="utf-8")

# Source audit.
for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    shutil.copyfile(AUDIT / f"{stem}_V131.csv", AUDIT / f"{stem}_V132.csv")

hash_rows = []
for row in catalog:
    local = row["archivo_local"]
    path = REPO / local.lstrip("/") if local else None
    exists = bool(path and path.is_file())
    actual = sha256(path) if exists else ""
    expected = row["sha256"]
    hash_rows.append({"id": row["id"], "archivo_local": local, "exists": str(exists), "sha_catalog": expected, "sha_actual": actual, "hash_ok": str(bool(exists and expected and actual.lower() == expected.lower()))})
assert len(hash_rows) == 358
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V132.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V132.csv", hash_rows)

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V132.csv"
provenance = [row for row in read_csv(provenance_path) if row["source_id"] not in source_ids]
for source in SOURCES:
    provenance.append({"source_id": source["id"], "original_url": source["url"], "retrieval_url": source["url"], "capture_timestamp": "20260830", "cdx_digest": "N/A_DIRECT_OFFICIAL", "local_path": source["local"], "sha256": source["sha256"], "bytes": str(source["bytes"]), "provenance_note": "Descarga directa oficial; preservada, hasheada y contenido relevante verificado en V132."})
write_csv(provenance_path, provenance)

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or "tmp" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": str(size), "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V132.csv", size_rows)

physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
assert physical == hash_ok == 352
completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V131.json").read_text(encoding="utf-8"))
for key in list(completeness):
    if key.endswith("_v131") or "newly_preserved_v131" in key:
        completeness.pop(key, None)
completeness.update({
    "checkpoint": "V132", "date": "2026-08-30",
    "state": "E0_FINAL_AUDIT_IDENTITY_CLOSED_RECORD_PRODUCERS_MAPPED_EXECUTED_CHAIN_OPEN_NOT_SENT",
    "numeric_v132_strict_changed": False, "master_catalog_entries": len(catalog),
    "physical_local_copies": physical, "physical_local_hash_ok": hash_ok,
    "binary_required_entries": len(catalog) - 5, "binary_required_preserved": physical,
    "e0_primary_sources_preserved": len(census), "e0_quality": "PRIMARY_METADATA_IDENTITY_AND_RECORD_PRODUCER_MAP",
    "sources_newly_preserved_v132": 7, "e0_primary_sources_newly_preserved_v132": 7,
    "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
    "e0_request_traceability_rows": len(trace), "e0_request_search_keys": len(keys),
    "e0_agn_project_locator": "48 0237/09", "e0_agn_project_progress_pct": 27,
    "e0_agn_final_identity": "UUID_B52E_ACT41_RES202_EXACT_PROJECT_CODE_NOT_LITERAL",
    "e0_agn_quarterly_annexes_public_body_open": 2,
    "e0_exp_file": "S01:0342455/2008_BODY_NOT_LOCATED_PUBLICLY",
    "e0_settlement_award_rows_exact": 10, "e0_settlement_account_candidate_rows": 9,
    "e0_settlement_executed_rows_confirmed": 0, "e0_requests_submitted": 0,
    "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
    "historical_workstream": "Final audit identity closed and record producers mapped; project-code literal crosswalk and executed settlement remain open; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V132.json").write_text(json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V132 · identidad AGN y productores documentales"
text = backup.read_text(encoding="utf-8-sig")
if marker not in text:
    text += f"\n\n{marker}\n\n- Identidad informe final–Act.41/2009–Res.202/2009 cerrada por UUID oficial; 48 0237/09 contextual fuerte, no literal.\n- Anexos AGN T3/T4 probados pero cuerpos públicos no localizados.\n- DADP/SIGADE/SIDIF/COMDOC y subprocesos de recompra mapeados con corte temporal posterior.\n- Formato SIDIF/C-41 individualizado demostrado por CGN 2004/2010; asignación 2008 abierta.\n- Escalera sin cambio: 10 adjudicaciones, 9 cuentas candidatas, 0 ejecuciones confirmadas; seis pedidos no enviados.\n"
    backup.write_text(text, encoding="utf-8")

inherited = []
for row in read_csv(V131 / "INHERITED_QA_STATUS_V131.csv"):
    inherited.append({"script": row["script"], "pre_v132_result": row["post_v131_result"], "post_v132_result": "EXPECTED_SUPERSEDED_ASSERTION" if row["script"] == "qa_v131.py" else row["post_v131_result"], "interpretation": "V131 is superseded by seven new sources and V132 counts." if row["script"] == "qa_v131.py" else row["interpretation"]})
inherited.append({"script": "qa_v132.py", "pre_v132_result": "N/A", "post_v132_result": "PASS", "interpretation": "AGN identity, quarterly annex gap, disclosure ladder and DADP producer map verified."})
write_csv(HERE / "INHERITED_QA_STATUS_V132.csv", inherited)

qa = r'''from pathlib import Path
import csv
import hashlib
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
AUDIT = REPO / "research" / "ciclo_ajuste" / "source_audit"

def rows(name):
    with (HERE / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

cross = {r["crosswalk_id"]: r for r in rows("E0_AGN_PUBLIC_METADATA_CROSSWALK_V132.csv")}
assert len(cross) == 5
assert cross["CX132_02"]["status"] == "EXACT_FINAL_IDENTITY"
assert cross["CX132_05"]["status"] == "FINAL_IDENTITY_CLOSED_PROJECT_CODE_NOT_LITERAL"
assert len(rows("E0_AGN_2008_DEBT_AUDIT_PROJECT_BRIDGE_V132.csv")) == 6

quarterly = rows("E0_AGN_QUARTERLY_ANNEX_AVAILABILITY_V132.csv")
assert len(quarterly) == 3
assert quarterly[0]["status"] == "PUBLIC_ANNEX_RECOVERED"
assert all(r["status"] == "ANNEX_EXISTENCE_PROVED_PUBLIC_BODY_NOT_LOCATED" for r in quarterly[1:])

disclosure = rows("E0_SIGADE_SIDIF_DISCLOSURE_LADDER_V132.csv")
assert len(disclosure) == 14
assert sum(r["year"] == "2008" for r in disclosure) == 5
assert any(r["year"] == "2004" and r["disclosure_level"] == "ITEMIZED" for r in disclosure)
assert any(r["year"] == "2010" and r["sigade"] == "83106000" and r["disclosure_level"] == "ITEMIZED" for r in disclosure)

producer = rows("E0_ONCP_SIGADE_RECORD_PRODUCER_CONTROL_V132.csv")
assert len(producer) == 7
assert any(r["record_or_process"] == "I.f.2 Recompra de títulos" for r in producer)
assert any(r["record_or_process"] == "I.b.4 Revisión de una recompra de títulos" for r in producer)
assert len(rows("E0_EXPEDIENT_PUBLIC_SEARCH_EXHAUSTION_V132.csv")) == 4

public = {r["route_id"]: r for r in rows("E0_PUBLIC_SETTLEMENT_RECORD_EXHAUSTION_V132.csv")}
assert len(public) == 8
assert public["PE132_01"]["status"] == "PRODUCER_SYSTEM_CONFIRMED_EXPEDIENT_BODY_NOT_PUBLIC"
assert public["PE132_07"]["status"] == "FINAL_IDENTITY_CLOSED_PROJECT_CODE_CONTEXTUAL_NOT_LITERAL"

assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V132.csv")) == 154
assert len(rows("E0_FISCAL_METHOD_BREAKS_V132.csv")) == 114
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V132.csv")) == 101
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V132.csv")) == 90

ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V132.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)
summary = {r["stage"]: r for r in rows("E0_SETTLEMENT_EVIDENCE_LADDER_SUMMARY_V132.csv")}
assert summary["PUBLISHED_AWARD"]["closed_rows"] == "10"
assert summary["BCRA_ACCOUNT_CANDIDATE"]["closed_rows"] == "9"
assert summary["FINANCE_ORDER_BCRA_CREDIT"]["closed_rows"] == "0"

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V132.csv")}
assert len(census) == 118
new_ids = {
    "e0_agn_api_informe_res202_act41_2009", "e0_agn_res_202_2009_act_41_2009_resolution",
    "e0_agn_api_informe_3t_2009_res211", "e0_agn_res_211_2009_3t_activity",
    "e0_agn_api_informe_4t_2009_res44_2010", "e0_agn_res_44_2010_4t_activity",
    "e0_agn_2022_124_oncp_control_interno",
}
assert new_ids <= set(census)

with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 358 and len({r["id"] for r in catalog}) == 358

expected = {
    "agn_api_informe_res202_act41_2009.json": (13002, "8edcc3503af5f3ec0c380788dc70fe3276885e621ce37bfaf00f48f3baacdcfc"),
    "agn_res_202_2009_act_41_2009.pdf": (48191, "52a27534424d10eb631c9852d8ba35222d3448eeefaf583192c745d59d755589"),
    "agn_api_informe_3t_2009_res211.json": (10672, "001a311e62a2ead9649c5ffc0261c2691ed32eeb150388f298ab769ec1076aa5"),
    "agn_res_211_2009_3t_2009.pdf": (30951, "d8408f34fa88c2f4614fcdb30f8a2eed64d57e72f61526e2c886bddc68831b53"),
    "agn_api_informe_4t_2009_res044_2010.json": (10675, "c68a6035ac0bda2df5eb71608572943a0b00230f5fb62f1e1b18730be98ff677"),
    "agn_res_044_2010_4t_2009.pdf": (30142, "a02e317a61221b4b163ff3e2fcf2a4756414c25871abe4886fcc218cd1e38772"),
    "agn_2022_124_oncp_control_interno.pdf": (8305750, "4b61ce2dc5245268a4cb1858e023c202beb08a86425af3710c1a6ff963f9ccc4"),
}
bin_dir = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v132" / "binaries"
assert len(list(bin_dir.iterdir())) == 7
for name, (size, digest) in expected.items():
    path = bin_dir / name
    assert path.stat().st_size == size
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V132.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V132"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 352
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v132_strict_changed"] is False

for name, marker in {
    "REQUEST_AGN_2018_REPLY_V132.md": "## Clave V132 · identidad final cerrada y anexos trimestrales faltantes",
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V132.md": "## Clave V132 · productor, sistemas y formato de salida demostrados",
}.items():
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert marker in text and "BORRADOR_NO_ENVIADO" in text

for name in ("README_V132.md", "VEREDICTO_V132.md", "E0_FISCAL_RECONSTRUCTION_V132.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V132_A_V133.md"):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "0/10" in text and "48 0237/09" in text

print("V132 QA PASS")
'''
(HERE / "qa_v132.py").write_text(qa, encoding="utf-8")

def checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V132.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V132", "parent_checkpoint": "V131",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": 7, "new_primary_sources": 7,
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks),
        "agn_final_identity": "UUID_B52E_ACT41_RES202_EXACT_PROJECT_CODE_NOT_LITERAL",
        "agn_quarterly_annex_bodies_open": 2, "expedient_body_publicly_located": False,
        "award_rows_exact": 10, "account_candidate_rows": 9, "executed_settlement_rows_confirmed": 0,
        "request_drafts": 6, "request_traceability_rows": len(trace), "request_search_keys": len(keys),
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V132.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    "checkpoint": "V132", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical local copies with {hash_ok}/{physical} SHA-valid; AGN final identity closed and DADP/SIGADE record producers mapped; zero of ten executed settlement rows confirmed; six requests drafted and none submitted.",
    "historical_workstream": "Final audit identity closed; project-code literal crosswalk, quarterly annexes, DADP file, provider subledgers and executed settlement remain open; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V132 BUILD PASS")
