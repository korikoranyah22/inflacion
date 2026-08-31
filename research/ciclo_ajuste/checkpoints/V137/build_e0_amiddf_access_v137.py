from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import shutil


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
PARENT = HERE.parent / "V136"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v137" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


EXPECTED = {
    "argentina_decreto_1344_2007_texto_original.html": (160339, "255480068e5a0758c1f5ae42731ecab4dd09a926785ae8688f3e28705c23bca2"),
    "argentina_economia_solicitud_informacion_publica_2026.html": (35830, "aff6f649eb8eb0bb2308ba924c437d5b5d00660e19e0e37725b5be464618d03a"),
    "argentina_ley_27275_texto_actualizado.html": (78213, "87843d5f34a283dce489d0a35e97f52a826a80783fb521226dbd1ff971d98bd8"),
    "argentina_solicitar_informacion_publica_tad.html": (53363, "817890de7fbda959664cd66f35e318f62dfb758ba373794c7ae1619f03e10868"),
    "cgn_circular_05_2013_c41_paper_ordering.html": (8399, "8be4a42e138fd550fd664001734bb9dbd3450e7a32f723a41aacb5468d91a214"),
    "cgn_circular_16_2000_form_c_flows.html": (170076, "32af05052e4f0074a4eff9835bc6398510e99b5659974d98778fdfbb13a10642"),
    "cgn_circular_19_1995_c41_transaf_paper_timing.html": (3581, "6c0899ca32f603eb0bb4f826d7cdcd87a174a14c43ab5f3902a55bcac9a16852"),
    "cgn_circular_30_1994_valid_supporting_documentation.html": (24867, "d855a80c08ba0832cfdf1ff724eb1316889901875fe4b95b2017fec54dcd88e5"),
    "cgn_circular_33_1995_bna_bcra_external_payment_exception.html": (10058, "3a919aeb29ee25eef9aebb5fb90cd9bb49747e3ab1d3d7ee1dc934f545475458"),
    "cgn_cuenta_2008_saf355_356_crosswalk.html": (53229, "3244a20ebf2356ad63422017bcd66be7eae2954fe8e3d8ff01ff1c6b9465b71a"),
    "cgn_disposicion_28_2001_formulario_c_archive_flow.html": (42737, "9a4fea8dfae4512de3fce130815529d67f9a966fe545453187df84ec5ec71def"),
    "cgn_disposicion_46_1998_amiddf_annex.html": (53282, "1fe54fe96949625a1f6df57a986bd036b1e34ecf21e4ca1e4cfa4df978a0f033"),
    "cgn_disposicion_46_1998_amiddf_procedure.html": (5429, "3eeefabb14659306496238edd09d7e85ae2845160e01c3598f140f22967ccb59"),
    "cgn_disposicion_46_1998_remittance_form.pdf": (42715, "43ede7a9afb026adaf06f081d72b815a68708b58062ad48a56e8cc4970cc2b4f"),
    "tgn_manual_sistema_tesoreria_v1.pdf": (3102369, "3af4050e4d00f75ea0cbf49b3c8d84226b1debb58e65a39d167aaea65da02845"),
}


def source(source_id, filename, institution, title, url, publication, period, code,
           families, breaks, use, caveat, note):
    size, digest = EXPECTED[filename]
    return {
        "id": source_id, "filename": filename, "institution": institution,
        "title": title, "url": url, "publication": publication, "period": period,
        "code": code, "families": families, "breaks": breaks, "use": use,
        "caveat": caveat, "note": note, "bytes": size, "sha256": digest,
        "type": ("PDF oficial · captura preservada" if filename.endswith(".pdf") else "HTML oficial · captura preservada"),
    }


SOURCES = [
    source("e0_cgn_disposition_46_1998_amiddf_procedure", "cgn_disposicion_46_1998_amiddf_procedure.html", "Contaduría General de la Nación", "Disposición CGN 46/1998 · procedimiento AMIDDF", "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/1998/disp46/dis46.htm", "1998-11-03", "1998; documentos desde 1992", "Disposición 46/98; AMIDDF", "AMIDDF;financial_archive;remittance;custody;digitization", "regla general de archivo versus remisión efectiva del SAF 355", "USABLE_CONTEMPORANEOUS_AMIDDF_AUTHORITY", "La norma crea la ruta; no prueba que los documentos target hayan sido remitidos.", "V137 E0: aprueba el procedimiento de envío, recepción, consulta, retiro y devolución de documentación financiera en AMIDDF."),
    source("e0_cgn_disposition_46_1998_amiddf_annex", "cgn_disposicion_46_1998_amiddf_annex.html", "Contaduría General de la Nación", "Anexo Disposición CGN 46/1998 · remisión, consulta y custodia AMIDDF", "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/1998/disp46/adis46.htm", "1998-11-03", "1998; documentos desde 1992", "Anexo Disposición 46/98", "SAF;Rendiciones_de_Cuentas;Otros_Gastos;box;document_number;retention", "esquema de remisión versus índice target aún no obtenido", "USABLE_EXACT_AMIDDF_RETRIEVAL_SCHEMA", "La consulta interna de 1998 no sustituye el derecho ciudadano vigente de la Ley 27.275.", "V137 E0: fija productor/remitente, serie, subserie, ejercicio, caja, tipo y número documental, desafectación y responsabilidades de custodia."),
    source("e0_cgn_disposition_46_1998_amiddf_remittance_form", "cgn_disposicion_46_1998_remittance_form.pdf", "Contaduría General de la Nación", "Planilla de remisión de documentación al AMIDDF", "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/1998/disp46/anexo46.pdf", "1998-11-03", "1998; documentos desde 1992", "Planilla de Remisión AMIDDF", "remittance_form;SAF;series;subseries;box;exercise;document_type;document_number", "formulario vacío versus planillas completadas del SAF 355", "USABLE_EXACT_ARCHIVAL_ACCESSION_FIELDS", "El formulario prueba los campos del índice, no sus valores target.", "V137 E0: formulario oficial visualmente verificado con los campos necesarios para pedir primero el índice de remisión preexistente."),
    source("e0_cgn_circular_30_1994_supporting_document_archive", "cgn_circular_30_1994_valid_supporting_documentation.html", "Contaduría General de la Nación", "Circular CGN 30/1994 · archivo de documentación respaldatoria", "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/1994/cir30.htm", "1994-09-16", "1994; regla general", "Circular 30/94", "supporting_documents;accounting_registry;archive;integrity", "deber general versus ubicación target", "USABLE_GENERAL_SAF_ARCHIVE_DUTY", "No individualiza SAF 355 ni los tres registros.", "V137 E0: las unidades de registro deben archivar el respaldo para rápida localización y responden por su integridad."),
    source("e0_cgn_circular_33_1995_paper_form_scope", "cgn_circular_33_1995_bna_bcra_external_payment_exception.html", "Contaduría General de la Nación", "Circular CGN 33/1995 · alcance de formularios en papel", "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/1995/cir33.htm", "1995-08-16", "1995-2009", "Circular 33/95; C-41; SAF 355/356", "C41;paper;funding_source;amount;SAF355;SAF356", "texto de cierre amplio colocado luego del apartado C-43", "USABLE_WITH_SCOPE_PLACEMENT_CAVEAT", "La frase SAF 355/356 para toda fuente y monto es textual, pero su ubicación impide proyectarla sin reserva a cada C-41.", "V137 E0: regla vigente hasta su derogación expresa en marzo de 2009; conserva una ambigüedad de alcance que se congela como tal."),
    source("e0_cgn_disposition_28_2001_c43_negative_control", "cgn_disposicion_28_2001_formulario_c_archive_flow.html", "Contaduría General de la Nación", "Disposición CGN 28/2001 · formulario C-43", "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/2001/disp28/disp28_c43.htm", "2001", "2001", "Disposición 28/01; C-43", "C43;revolving_fund;negative_scope_control", "C-43 versus C-41", "EXCLUDED_ADJACENT_FORM_NOT_C41", "Describe sólo Fondo Rotatorio; no prueba campos ni flujo de una C-41.", "V137 control negativo: se preserva para impedir que un formulario C-43 se presente como evidencia C-41."),
    source("e0_cgn_circular_16_2000_c43_negative_control", "cgn_circular_16_2000_form_c_flows.html", "Contaduría General de la Nación", "Circular CGN 16/2000 · flujos C-43 SIDIF/SAF", "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/2000/cir16.htm", "2000", "2000", "Circular 16/00; C-43", "C43;SIDIF;SAF;file_flow;negative_scope_control", "flujo C-43 versus flujo C-41", "EXCLUDED_ADJACENT_FORM_NOT_C41", "Sus archivos y estados no deben trasladarse a la C-41 target.", "V137 control negativo: el título y contenido limitan la fuente al C-43."),
    source("e0_cgn_circular_19_1995_transaf_paper_timing", "cgn_circular_19_1995_c41_transaf_paper_timing.html", "Contaduría General de la Nación", "Circular CGN 19/1995 · plazo papel posterior a TRANSAF", "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/1995/cir19.htm", "1995-04-20", "1995; continuidad 2008 no cerrada", "Circular 19/95; C-41; TRANSAF", "C41;paper;TRANSAF;timing;automatic_cancellation", "plazo de presentación versus aplicabilidad material a cada C-41 2008", "USABLE_HISTORIC_PAPER_TIMING_RULE", "Prueba plazo para formularios alcanzados; no prueba por sí sola que cada target estuviera alcanzado.", "V137 E0: los formularios alcanzados debían presentarse el primer día hábil tras confirmar TRANSAF o se daba de baja la transmisión."),
    source("e0_cgn_circular_05_2013_c41_paper_ordering", "cgn_circular_05_2013_c41_paper_ordering.html", "Contaduría General de la Nación", "Circular CGN 05/2013 · orden físico de C-41", "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/2013/cir05.htm", "2013-04-11", "2013", "Circular 05/13; C-41", "C41;paper;type;number;CGN;TGN", "práctica 2013 versus target 2008", "USABLE_LATER_PAPER_TRAIL_CONTROL", "Sólo prueba un control posterior de localización y envío.", "V137 E0: las C-41 papel presentadas debían ordenarse por tipo y número para su ubicación y posterior envío a TGN."),
    source("e0_argentina_decree_1344_2007_original_finance_rule", "argentina_decreto_1344_2007_texto_original.html", "Poder Ejecutivo Nacional", "Decreto 1344/2007 · reglamento financiero original aplicable en 2008", "https://www.argentina.gob.ar/normativa/nacional/decreto-1344-2007-133006/texto", "2007-10-04", "2007-2008", "Decreto 1344/07; arts. 6, 9, 31, 35", "SAF;supporting_documents;Jurisdiction90;payment_order;paid_stage;public_debt", "orden/devengado versus cancelación/pagado", "USABLE_EXACT_2008_FINANCIAL_RULE", "La regla de etapa pagado no identifica el medio ni los movimientos target.", "V137 E0: fija SAF 355/Jurisdicción 90, archivo de respaldos, orden formal y que pagado opera sólo al cancelar la orden."),
    source("e0_argentina_law_27275_updated_access", "argentina_ley_27275_texto_actualizado.html", "Congreso de la Nación / InfoLEG", "Ley 27.275 · texto actualizado de acceso a la información", "https://www.argentina.gob.ar/normativa/nacional/265949/actualizacion", "texto actualizado consultado 2026-08-30", "vigente 2026", "Ley 27.275; arts. 1, 4, 5, 9-15", "public_access;transfer;deadline;partial_release;reasoned_denial;complaint", "acceso a registros existentes versus obligación de crear un análisis", "USABLE_CURRENT_ACCESS_LEGAL_ROUTE", "El organismo entrega lo existente; no está obligado a crear cuadros o clasificaciones nuevas.", "V137 E0: habilita pedir índices y documentos preexistentes, transferencia en cinco días, tachas parciales y denegación fundada."),
    source("e0_argentina_economia_access_channel_2026", "argentina_economia_solicitud_informacion_publica_2026.html", "Ministerio de Economía", "Canal de acceso a información pública del Ministerio de Economía", "https://www.argentina.gob.ar/economia/transparencia/pedirinformacion", "actualizada 2026-06", "vigente 2026", "RAIP; TAD; ciudadano@mecon.gov.ar", "submission_channel;TAD;email;physical;deadline;complaint", "canal disponible versus presentación efectiva", "USABLE_CURRENT_CHANNEL_NOT_CONTACTED", "El canal fue verificado pero no utilizado.", "V137 E0: TAD, correo RAIP y mesa de entradas; 15 días hábiles, prórroga escrita y reclamo en 40 días."),
    source("e0_argentina_tad_public_information_route", "argentina_solicitar_informacion_publica_tad.html", "Administración Pública Nacional", "Trámite nacional de solicitud de información pública", "https://www.argentina.gob.ar/solicitar-informacion-publica", "consulta 2026-08-30", "vigente 2026", "TAD; Ley 27.275", "TAD;public_information;free;no_motive;no_lawyer", "ruta general versus organismo custodio específico", "USABLE_GENERAL_TAD_ROUTE_NOT_USED", "No se inició el trámite.", "V137 E0: cualquier persona puede pedir información sin motivar, sin abogado, gratuitamente y en cualquier formato disponible."),
    source("e0_tgn_manual_system_treasury_v1", "tgn_manual_sistema_tesoreria_v1.pdf", "Tesorería General de la Nación", "El Sistema de Tesorería · Manual TGN versión 1.0", "https://capacitacion.mecon.gob.ar/manuales/Tesoreria_manual_TGN.pdf", "2013-02", "reglas 2007 y operatoria documentada 2013", "Manual TGN v1; Resolución 374/2007", "payer;public_debt;total_partial;selection;confirmation;payment_medium;bank_return;reconciliation", "manual posterior versus registro target 2008", "USABLE_OFFICIAL_PROCEDURAL_INTERPRETATION", "Interpreta el régimen y clases documentales; no contiene las tres operaciones target.", "V137 E0: deuda pública es Pagador TGN cualquiera sea el monto y el pago se descompone en selección, confirmación, medio, envío, rendición y conciliación."),
    source("e0_cgn_account_2008_saf355_356_crosswalk", "cgn_cuenta_2008_saf355_356_crosswalk.html", "Contaduría General de la Nación", "Cuenta de Inversión 2008 · identificación SAF 355/356", "https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/sep/uepex.htm", "2009", "2008", "SAF 355; SAF 356", "SAF355;public_debt;SAF356;treasury_obligations", "identidad institucional versus documento target", "USABLE_EXACT_2008_SAF_CROSSWALK", "No contiene los tres documentos ni sus cajas.", "V137 E0: identifica SAF 355 como Dirección de Administración de la Deuda Pública y SAF 356 como Obligaciones a cargo del Tesoro."),
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


def clone_parent() -> None:
    skip = {"build_e0_legacy_sidif_agan_v136.py", "qa_v136.py", "MANIFEST_V136.json", "INHERITED_QA_STATUS_V136.csv"}
    for item in PARENT.iterdir():
        if not item.is_file() or item.name in skip or item.name.startswith("HANDOVER_PROXIMA_SESION"):
            continue
        target = HERE / item.name.replace("V136", "V137")
        text = item.read_text(encoding="utf-8-sig").replace("V136", "V137").replace("v136", "v137")
        target.write_text(text, encoding="utf-8")


clone_parent()

for item in SOURCES:
    path = BIN / item["filename"]
    assert path.is_file() and path.stat().st_size == item["bytes"], path
    assert sha256(path) == item["sha256"], path
    item["local"] = "/" + path.relative_to(REPO).as_posix()

source_ids = {item["id"] for item in SOURCES}

# Catálogo, censo y proveniencia.
catalog = [row for row in read_csv(CATALOG) if row["id"] not in source_ids]
for item in SOURCES:
    catalog.append({
        "id": item["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": item["institution"],
        "titulo": item["title"], "url_original": item["url"], "archivo_local": item["local"],
        "fecha_descarga": "2026-08-30", "fecha_publicacion": item["publication"],
        "codigo_serie": item["code"], "periodo_utilizado": item["period"], "tipo": item["type"],
        "sha256": item["sha256"], "nota": item["note"],
    })
assert len(catalog) == 403 and len({row["id"] for row in catalog}) == 403
write_csv(CATALOG, catalog)

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V137.csv"
census = [row for row in read_csv(census_path) if row["source_id"] not in source_ids]
for item in SOURCES:
    census.append({
        "source_id": item["id"], "institution": item["institution"], "artifact": item["title"],
        "url": item["url"], "local_path": item["local"], "sha256": item["sha256"],
        "bytes": str(item["bytes"]), "period_coverage": item["period"],
        "variable_families": item["families"], "primary_source": "YES", "preserved": "YES",
        "method_breaks": item["breaks"], "use_status": item["use"], "caveat": item["caveat"],
    })
assert len(census) == 163 and len({row["source_id"] for row in census}) == 163
write_csv(census_path, census)

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V137.csv"
provenance = [row for row in read_csv(provenance_path) if row["source_id"] not in source_ids]
for item in SOURCES:
    provenance.append({
        "source_id": item["id"], "original_url": item["url"], "retrieval_url": item["url"],
        "capture_timestamp": "20260830", "cdx_digest": "N/A_DIRECT_OFFICIAL", "local_path": item["local"],
        "sha256": item["sha256"], "bytes": str(item["bytes"]),
        "provenance_note": f"Captura oficial directa {item['type'].split()[0]} preservada y hasheada en V137.",
    })
assert len(provenance) == 66
write_csv(provenance_path, provenance)

# Índice de remisión: primero se pide el registro existente; la caja todavía es una salida, no una entrada conocida.
remittance = [
    {"field_id": "RI137_01", "official_field": "Organismo remitente", "target_value": "DESCONOCIDO", "request_role": "salida a obtener", "source_id": "e0_cgn_disposition_46_1998_amiddf_annex;e0_cgn_disposition_46_1998_amiddf_remittance_form", "status": "OPEN"},
    {"field_id": "RI137_02", "official_field": "Organismo productor", "target_value": "SAF 355 · Dirección de Administración de la Deuda Pública", "request_role": "clave exacta", "source_id": "e0_cgn_cuenta_inversion_2008_sdp;e0_cgn_account_2008_saf355_356_crosswalk", "status": "EXACT"},
    {"field_id": "RI137_03", "official_field": "Serie", "target_value": "Rendiciones de Cuentas", "request_role": "clave exacta", "source_id": "e0_cgn_disposition_46_1998_amiddf_annex", "status": "EXACT_SCHEMA"},
    {"field_id": "RI137_04", "official_field": "Subserie", "target_value": "Otros Gastos", "request_role": "clave exacta por exclusión de Gastos en Personal", "source_id": "e0_cgn_disposition_46_1998_amiddf_annex;e0_cgn_cuenta_inversion_2008_sdp", "status": "EXACT_CLASSIFICATION"},
    {"field_id": "RI137_05", "official_field": "Ejercicio", "target_value": "2008", "request_role": "clave exacta", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "status": "EXACT"},
    {"field_id": "RI137_06", "official_field": "Fechas extremas", "target_value": "2008", "request_role": "salida a obtener", "source_id": "e0_cgn_disposition_46_1998_amiddf_annex", "status": "OPEN"},
    {"field_id": "RI137_07", "official_field": "Cantidad de unidades de conservación", "target_value": "DESCONOCIDO", "request_role": "salida a obtener", "source_id": "e0_cgn_disposition_46_1998_amiddf_remittance_form", "status": "OPEN"},
    {"field_id": "RI137_08", "official_field": "N° caja", "target_value": "DESCONOCIDO", "request_role": "objetivo primario de la primera respuesta", "source_id": "e0_cgn_disposition_46_1998_amiddf_annex", "status": "OPEN_CRITICAL"},
    {"field_id": "RI137_09", "official_field": "Tipo documental", "target_value": "SIDIF; identificar especie exacta antes de asumir C-41", "request_role": "objetivo primario", "source_id": "e0_cgn_disposition_46_1998_amiddf_annex;e0_cgn_cuenta_inversion_2008_sdp", "status": "OPEN_CRITICAL"},
    {"field_id": "RI137_10", "official_field": "N° documento", "target_value": "71597;152677;2876", "request_role": "claves exactas", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "status": "EXACT_SIDIF_LOCATORS"},
    {"field_id": "RI137_11", "official_field": "Fecha de desafectación", "target_value": "DESCONOCIDO", "request_role": "salida; no equivale a destrucción", "source_id": "e0_cgn_disposition_46_1998_amiddf_annex", "status": "OPEN"},
    {"field_id": "RI137_12", "official_field": "Observaciones", "target_value": "DESCONOCIDO", "request_role": "salida sobre guarda/no desafectable", "source_id": "e0_cgn_disposition_46_1998_amiddf_annex", "status": "OPEN"},
    {"field_id": "RI137_13", "official_field": "Tejuelo · N° y nombre SAF", "target_value": "355 · Dirección de Administración de la Deuda Pública", "request_role": "clave de caja", "source_id": "e0_cgn_disposition_46_1998_amiddf_annex", "status": "EXACT_SCHEMA"},
    {"field_id": "RI137_14", "official_field": "Tejuelo · período/subserie/orden", "target_value": "2008;Otros Gastos;N° orden desconocido", "request_role": "salida a obtener", "source_id": "e0_cgn_disposition_46_1998_amiddf_annex", "status": "PARTIAL"},
    {"field_id": "RI137_15", "official_field": "Firma recepción AMIDDF", "target_value": "DESCONOCIDO", "request_role": "prueba de transferencia/recepción", "source_id": "e0_cgn_disposition_46_1998_amiddf_remittance_form", "status": "OPEN"},
]
write_csv(HERE / "E0_AMIDDF_REMITTANCE_INDEX_SCHEMA_V137.csv", remittance)

custody_route = [
    {"route_id": "CR137_01", "phase": "PRODUCTION", "responsible": "SAF 355", "record_or_action": "ordenar, clasificar, conservar y depurar", "condition": "mientras está en su poder", "target_result": "responsable exacto probado; tenencia actual abierta", "source_id": "e0_cgn_disposition_46_1998_amiddf_annex;e0_argentina_decree_1344_2007_original_finance_rule"},
    {"route_id": "CR137_02", "phase": "AUTHORIZATION", "responsible": "SAF 355 + máxima autoridad AMIDDF", "record_or_action": "conformes escritos y decisión sobre digitalización", "condition": "antes del envío", "target_result": "actos preexistentes a solicitar", "source_id": "e0_cgn_disposition_46_1998_amiddf_annex"},
    {"route_id": "CR137_03", "phase": "REMITTANCE", "responsible": "archivo SAF 355", "record_or_action": "planilla, cajas/biblioratos y tejuelo", "condition": "después de aprobación de rendición y cronograma", "target_result": "planilla target no localizada", "source_id": "e0_cgn_disposition_46_1998_amiddf_annex;e0_cgn_disposition_46_1998_amiddf_remittance_form"},
    {"route_id": "CR137_04", "phase": "DIGITIZATION", "responsible": "AMIDDF", "record_or_action": "asume responsabilidad", "condition": "sólo si la entrega tuvo objeto de digitalización", "target_result": "autorización e imágenes target abiertas", "source_id": "e0_cgn_disposition_46_1998_amiddf_annex"},
    {"route_id": "CR137_05", "phase": "PAPER_CUSTODY", "responsible": "SAF 355", "record_or_action": "mantiene responsabilidad", "condition": "si el envío fue sólo para guarda", "target_result": "tipo de transferencia abierto", "source_id": "e0_cgn_disposition_46_1998_amiddf_annex"},
    {"route_id": "CR137_06", "phase": "NON_DIGITIZED_LOCAL", "responsible": "SAF 355", "record_or_action": "conservación propia dos años adicionales", "condition": "si no autorizó digitalización", "target_result": "cronograma/transferencia posterior a solicitar", "source_id": "e0_cgn_disposition_46_1998_amiddf_annex"},
    {"route_id": "CR137_07", "phase": "ORIGINALS", "responsible": "SAF 355 / AMIDDF", "record_or_action": "originales; copia autenticada sólo si falta o está deteriorado", "condition": "preparación del envío", "target_result": "original/copia target abierto", "source_id": "e0_cgn_disposition_46_1998_amiddf_annex"},
    {"route_id": "CR137_08", "phase": "EXPURGO", "responsible": "SAF 355 + AMIDDF + AGN", "record_or_action": "expurgo previo a desafectación", "condition": "al vencer guarda", "target_result": "fecha de desafectación no prueba destrucción", "source_id": "e0_cgn_disposition_46_1998_amiddf_annex"},
    {"route_id": "CR137_09", "phase": "HISTORIC_QUERY", "responsible": "SAF/control/Poder Judicial", "record_or_action": "nota escrita y retiro por ejercicio/caja/expediente", "condition": "procedimiento 1998", "target_result": "no era vía ciudadana directa", "source_id": "e0_cgn_disposition_46_1998_amiddf_annex"},
    {"route_id": "CR137_10", "phase": "CURRENT_PUBLIC_ACCESS", "responsible": "RAIP Ministerio de Economía", "record_or_action": "Ley 27.275; TAD/email/mesa", "condition": "cualquier persona, sin motivo ni abogado", "target_result": "ruta lista; no enviada", "source_id": "e0_argentina_law_27275_updated_access;e0_argentina_economia_access_channel_2026;e0_argentina_tad_public_information_route"},
]
write_csv(HERE / "E0_AMIDDF_CUSTODY_RESPONSIBILITY_ROUTE_V137.csv", custody_route)

access_fit = [
    {"rule_id": "AI137_01", "legal_rule": "Presunción de publicidad y máximo acceso", "draft_instruction": "pedir índice, remisión y cuerpos existentes con máxima desagregación", "anti_overreach": "no afirmar existencia target", "source_id": "e0_argentina_law_27275_updated_access", "status": "READY_NOT_SENT"},
    {"rule_id": "AI137_02", "legal_rule": "Cualquier persona; sin interés legítimo ni abogado", "draft_instruction": "no justificar la investigación como requisito", "anti_overreach": "identificar claramente lo pedido", "source_id": "e0_argentina_law_27275_updated_access;e0_argentina_tad_public_information_route", "status": "READY_NOT_SENT"},
    {"rule_id": "AI137_03", "legal_rule": "Entrega en el estado en que se encuentre", "draft_instruction": "pedir copia/exportación del índice o planilla preexistente", "anti_overreach": "no exigir que creen un cuadro certificado", "source_id": "e0_argentina_law_27275_updated_access", "status": "READY_NOT_SENT"},
    {"rule_id": "AI137_04", "legal_rule": "Solicitud simple + constancia", "draft_instruction": "incluir identidad, información y contacto; conservar acuse", "anti_overreach": "ninguna presentación ocurrió", "source_id": "e0_argentina_law_27275_updated_access", "status": "READY_NOT_SENT"},
    {"rule_id": "AI137_05", "legal_rule": "Transferencia en cinco días", "draft_instruction": "si Economía no posee, remitir a custodio conocido e informar", "anti_overreach": "no tratar la falta de tenencia como inexistencia", "source_id": "e0_argentina_law_27275_updated_access", "status": "READY_NOT_SENT"},
    {"rule_id": "AI137_06", "legal_rule": "15 días + prórroga excepcional fundada de 15", "draft_instruction": "registrar fecha sólo después de presentar", "anti_overreach": "no hay vencimiento mientras sea borrador", "source_id": "e0_argentina_law_27275_updated_access;e0_argentina_economia_access_channel_2026", "status": "READY_NOT_SENT"},
    {"rule_id": "AI137_07", "legal_rule": "Información parcial/tachas", "draft_instruction": "pedir copia disociada que conserve metadatos operativos", "anti_overreach": "no reclamar datos personales innecesarios", "source_id": "e0_argentina_law_27275_updated_access", "status": "READY_NOT_SENT"},
    {"rule_id": "AI137_08", "legal_rule": "Denegatoria sólo fundada", "draft_instruction": "si no existe, pedir acto y alcance de búsqueda", "anti_overreach": "no pedir producir lo inexistente", "source_id": "e0_argentina_law_27275_updated_access", "status": "READY_NOT_SENT"},
    {"rule_id": "AI137_09", "legal_rule": "Silencio, ambigüedad o entrega incompleta", "draft_instruction": "registrar como denegatoria injustificada una vez vencido el plazo", "anti_overreach": "no anticipar incumplimiento", "source_id": "e0_argentina_law_27275_updated_access", "status": "READY_NOT_SENT"},
    {"rule_id": "AI137_10", "legal_rule": "Reclamo dentro de 40 días hábiles", "draft_instruction": "activar sólo tras solicitud real y constancia", "anti_overreach": "no iniciar seguimiento ahora", "source_id": "e0_argentina_law_27275_updated_access;e0_argentina_economia_access_channel_2026", "status": "READY_NOT_SENT"},
    {"rule_id": "AI137_11", "legal_rule": "Canales Ministerio de Economía", "draft_instruction": "TAD, ciudadano@mecon.gov.ar o Balcarce 186 piso 1 oficina 148", "anti_overreach": "canal verificado, no contactado", "source_id": "e0_argentina_economia_access_channel_2026", "status": "READY_NOT_SENT"},
]
write_csv(HERE / "E0_ACCESS_INFORMATION_LEGAL_FIT_V137.csv", access_fit)

paper_matrix = [
    {"row_id": "PO137_01", "date_or_period": "1995-04-20", "rule": "C-41 alcanzada se presenta primer día hábil tras confirmación TRANSAF; incumplimiento baja transmisión", "target_fit": "entorno TRANSAF compatible; alcance material por orden abierto", "source_id": "e0_cgn_circular_19_1995_transaf_paper_timing", "status": "HISTORIC_RULE_EXACT_TARGET_SCOPE_OPEN"},
    {"row_id": "PO137_02", "date_or_period": "1995-08-16", "rule": "FF11: papel si >=50.000, clases especiales o exterior BNA/BCRA", "target_fit": "agregado ARS32.270,30 no supera umbral; fuente y clase individual abiertas", "source_id": "e0_cgn_circular_33_1995_paper_form_scope", "status": "CONDITIONAL"},
    {"row_id": "PO137_03", "date_or_period": "1995-2009", "rule": "frase final SAF355/356: formularios para toda fuente y monto", "target_fit": "productor SAF355 exacto, pero frase ubicada tras apartado C-43", "source_id": "e0_cgn_circular_33_1995_paper_form_scope;e0_cgn_tgn_joint_disposition_13_16_2009_payment_records", "status": "TEXT_EXACT_SCOPE_PLACEMENT_AMBIGUOUS"},
    {"row_id": "PO137_04", "date_or_period": "2007-10-04", "rule": "toda salida Tesoro requiere orden formal; deuda pública menor al umbral sigue por TGN bajo fuentes enumeradas", "target_fit": "SAF355/J90 exacto; tipo/fuente de los tres registros abierta", "source_id": "e0_argentina_decree_1344_2007_original_finance_rule", "status": "CONTEMPORANEOUS_PAYER_RULE_STRONG"},
    {"row_id": "PO137_05", "date_or_period": "2007-10-12 interpreted 2013", "rule": "deuda pública = PAGADOR TGN cualquiera sea el monto", "target_fit": "evita excluir por ARS32.270,30; clasificación individual aún debe recuperarse", "source_id": "e0_tgn_manual_system_treasury_v1", "status": "OFFICIAL_LATER_INTERPRETATION"},
    {"row_id": "PO137_06", "date_or_period": "2009-03-12", "rule": "papel para Administración Central cuando PAGADOR TGN; deroga Circular 33/95", "target_fit": "sucesor inmediato; no prueba presentación target 2008", "source_id": "e0_cgn_tgn_joint_disposition_13_16_2009_payment_records", "status": "POST_TARGET_COMPARATOR"},
    {"row_id": "PO137_07", "date_or_period": "2013-04-11", "rule": "C-41 papel ordenada por tipo/número y enviada CGN→TGN", "target_fit": "práctica posterior de localización", "source_id": "e0_cgn_circular_05_2013_c41_paper_ordering", "status": "LATER_CONTROL_ONLY"},
    {"row_id": "PO137_08", "date_or_period": "V137 conclusion", "rule": "probabilidad alta de rastro papel, prueba estricta target no cerrada", "target_fit": "pedir planilla/índice, tipo documental, caja y copia", "source_id": "multiple_primary_sources", "status": "PAPER_ROUTE_PRIORITIZED_NOT_ASSERTED"},
]
write_csv(HERE / "E0_C41_PAPER_OBLIGATION_TEMPORAL_MATRIX_V137.csv", paper_matrix)

negative_controls = [
    {"control_id": "NC137_01", "artifact": "Disposición 28/2001 · C-43", "literal_scope": "Fondo Rotatorio", "cannot_prove": "tipo, campos o flujo C-41", "source_id": "e0_cgn_disposition_28_2001_c43_negative_control", "status": "EXCLUDED_FROM_C41_INFERENCE"},
    {"control_id": "NC137_02", "artifact": "Circular 16/2000 · flujos C-43", "literal_scope": "archivos C-43 SIDIF Central↔SAF", "cannot_prove": "nombre o continuidad de archivos C-41", "source_id": "e0_cgn_circular_16_2000_c43_negative_control", "status": "EXCLUDED_FROM_C41_INFERENCE"},
    {"control_id": "NC137_03", "artifact": "Anexo K 2008 · columna SIDIF", "literal_scope": "tres referencias SIDIF alineadas a 83106000", "cannot_prove": "que sean números C-41 y no otra especie documental", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "status": "DOCUMENT_TYPE_OPEN"},
    {"control_id": "NC137_04", "artifact": "Manual TGN v1", "literal_scope": "procedimiento oficial posterior", "cannot_prove": "contenido de registros 2008", "source_id": "e0_tgn_manual_system_treasury_v1", "status": "PROCEDURAL_COMPARATOR"},
]
write_csv(HERE / "E0_FORM_SCOPE_NEGATIVE_CONTROLS_V137.csv", negative_controls)

first_stage = [
    {"priority": "1", "record_object": "Planillas de Remisión SAF355 ejercicio 2008 subserie Otros Gastos", "exact_keys": "SAF355;2008;Rendiciones de Cuentas;Otros Gastos;71597;152677;2876", "minimum_output": "copia/exportación existente; caja;tipo;número;desafectación;observaciones;firmas", "fallback": "índice en el estado en que obre, con tachas parciales", "status": "DRAFT_NOT_SENT"},
    {"priority": "2", "record_object": "Tejuelos e inventario de cajas", "exact_keys": "SAF355;2008;Otros Gastos", "minimum_output": "período;número de orden;caja", "fallback": "metadatos de ubicación", "status": "DRAFT_NOT_SENT"},
    {"priority": "3", "record_object": "Tipo documental de cada referencia SIDIF", "exact_keys": "71597;152677;2876;83106000", "minimum_output": "especie;fecha;importe;beneficiario;expediente;vínculos", "fallback": "salida preexistente de índice", "status": "DRAFT_NOT_SENT"},
    {"priority": "4", "record_object": "Original o copia autenticada y cuerpos relacionados", "exact_keys": "caja+tipo+número obtenidos", "minimum_output": "todos los folios y anexos", "fallback": "imagen digital o copia disociada", "status": "DRAFT_NOT_SENT"},
    {"priority": "5", "record_object": "Clasificación de pagador, fuente y clase de gasto", "exact_keys": "SAF355;71597;152677;2876", "minimum_output": "PAGADOR TGN/SAF;fuente;partida;concepto", "fallback": "registro preexistente de sistema", "status": "DRAFT_NOT_SENT"},
    {"priority": "6", "record_object": "Reporte de Distribución Diaria de Pagos", "exact_keys": "tres SIDIF;2008", "minimum_output": "total/parcial;importe distribuido;fecha;selección", "fallback": "filas existentes sin datos personales", "status": "DRAFT_NOT_SENT"},
    {"priority": "7", "record_object": "Confirmación y medio de pago", "exact_keys": "tres SIDIF;identificador bancario", "minimum_output": "confirmación;saldo;medio;lote;archivo", "fallback": "metadatos del evento", "status": "DRAFT_NOT_SENT"},
    {"priority": "8", "record_object": "Rama débito automático de comisiones BNA", "exact_keys": "83106000;ARS32270.30;CUT;gastos bancarios", "minimum_output": "código movimiento;extracto;fecha valor;regularización;conciliación", "fallback": "movimientos agregados por fecha/importe", "status": "DRAFT_NOT_SENT"},
    {"priority": "9", "record_object": "Rama Nota de Pago deuda pública", "exact_keys": "SAF355;BCRA;Archivos de Notas", "minimum_output": "lote;archivo;instrucción;acuse BCRA;registro Libro Banco", "fallback": "metadatos de lote/acuse", "status": "DRAFT_NOT_SENT"},
    {"priority": "10", "record_object": "Rendición bancaria y conciliación", "exact_keys": "BNA/BCRA;tres SIDIF;importe/fecha", "minimum_output": "aceptado/rechazado;acreditación/débito;saldo;conciliación", "fallback": "respuesta disociada", "status": "DRAFT_NOT_SENT"},
]
write_csv(HERE / "E0_TARGET_FIRST_STAGE_REQUEST_OBJECTS_V137.csv", first_stage)

document_type_audit = [
    {"row_id": "DT137_01", "printed_object": "Anexo K", "printed_label": "SIDIF", "target_values": "71597;152677;2876", "directly_proves": "identificadores SIDIF alineados a 83106000", "does_not_prove": "tipo C-41", "status": "EXACT_LOCATORS_DOCUMENT_TYPE_OPEN"},
    {"row_id": "DT137_02", "printed_object": "Cuadro 1-A", "printed_label": "SAF N°355", "target_values": "Dirección de Administración de la Deuda Pública", "directly_proves": "productor institucional", "does_not_prove": "caja o formulario", "status": "PRODUCER_EXACT"},
    {"row_id": "DT137_03", "printed_object": "Decreto 1344/2007", "printed_label": "salida del Tesoro requiere orden", "target_values": "Jurisdicción90;Deuda Pública", "directly_proves": "debe existir una orden en el circuito", "does_not_prove": "que el número impreso en Anexo K sea el de esa orden", "status": "ORDER_REQUIRED_NUMBER_LINK_OPEN"},
    {"row_id": "DT137_04", "printed_object": "Manual TGN", "printed_label": "débito automático", "target_values": "gastos bancarios;regularización", "directly_proves": "ruta alternativa para comisiones bancarias", "does_not_prove": "que se usó en los tres target", "status": "ALTERNATIVE_BRANCH_OPEN"},
    {"row_id": "DT137_05", "printed_object": "Cierre V137", "printed_label": "hipótesis bifurcada", "target_values": "orden/C41 o regularización/débito", "directly_proves": "dos paquetes documentales buscables", "does_not_prove": "ejecución", "status": "DO_NOT_PREJUDGE_DOCUMENT_TYPE"},
]
write_csv(HERE / "E0_SIDIF_TARGET_DOCUMENT_TYPE_AUDIT_V137.csv", document_type_audit)

payment_stages = [
    {"stage_id": "PS137_01", "stage": "DEVENGADO", "event": "surge obligación y se liquida; cuando corresponde se emite orden", "target_record": "comprobante/orden y respaldo", "not_equivalent_to": "pagado", "source_id": "e0_argentina_decree_1344_2007_original_finance_rule"},
    {"stage_id": "PS137_02", "stage": "PROGRAMACIÓN", "event": "escenario/distribución total o parcial", "target_record": "Reporte de Distribución Diaria", "not_equivalent_to": "selección o pago", "source_id": "e0_tgn_manual_system_treasury_v1"},
    {"stage_id": "PS137_03", "stage": "SELECCIÓN", "event": "reserva comprobante y consume cuota", "target_record": "selección/lista diaria", "not_equivalent_to": "confirmación", "source_id": "e0_tgn_manual_system_treasury_v1"},
    {"stage_id": "PS137_04", "stage": "CONFIRMACIÓN", "event": "funcionario habilitado confirma y se genera medio", "target_record": "confirmación; identificador; saldos", "not_equivalent_to": "recepción bancaria final", "source_id": "e0_tgn_manual_system_treasury_v1"},
    {"stage_id": "PS137_05", "stage": "MEDIO_RED_CUT", "event": "lote/archivo a BNA", "target_record": "archivo;operaciones;monto;fecha compensación", "not_equivalent_to": "acreditación aceptada", "source_id": "e0_tgn_manual_system_treasury_v1"},
    {"stage_id": "PS137_06", "stage": "MEDIO_NOTA", "event": "deuda pública vía lotes/archivos BCRA", "target_record": "nota;lote;archivo;acuse recepción", "not_equivalent_to": "cancelación CRYL", "source_id": "e0_tgn_manual_system_treasury_v1"},
    {"stage_id": "PS137_07", "stage": "DÉBITO_AUTOMÁTICO", "event": "gasto bancario en extracto CUT con código específico", "target_record": "extracto;código;regularización", "not_equivalent_to": "C-41 target sin clasificar", "source_id": "e0_tgn_manual_system_treasury_v1"},
    {"stage_id": "PS137_08", "stage": "RENDICIÓN_BANCARIA", "event": "BNA informa acreditación o rechazo / BCRA confirma recepción", "target_record": "rendición;rechazo;acuse", "not_equivalent_to": "mera transmisión", "source_id": "e0_tgn_manual_system_treasury_v1"},
    {"stage_id": "PS137_09", "stage": "CONCILIACIÓN", "event": "procesa rendiciones y completa proceso bancario", "target_record": "conciliación;Libro Banco;saldo", "not_equivalent_to": "Cuenta de Inversión agregada", "source_id": "e0_tgn_manual_system_treasury_v1"},
    {"stage_id": "PS137_10", "stage": "PAGADO", "event": "cancelación de la orden con independencia del medio", "target_record": "cadena coherente de importe original, pagos y saldo cero", "not_equivalent_to": "SIDIF listado en Anexo K", "source_id": "e0_argentina_decree_1344_2007_original_finance_rule"},
]
write_csv(HERE / "E0_PAYMENT_STAGE_SEPARATION_V137.csv", payment_stages)

saf_crosswalk = [
    {"row_id": "SF137_01", "evidence": "Cuenta de Inversión 2008 Cuadro 1-A", "value": "SAF N°355 · Dirección de Administración de la Deuda Pública", "target_effect": "cierra productor del Anexo K", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "status": "EXACT"},
    {"row_id": "SF137_02", "evidence": "Cuenta de Inversión 2008 UEPEX", "value": "SAF355 Dirección de Administración de la Deuda Pública; SAF356 Obligaciones a cargo del Tesoro", "target_effect": "control independiente del cruce", "source_id": "e0_cgn_account_2008_saf355_356_crosswalk", "status": "EXACT_CORROBORATION"},
    {"row_id": "SF137_03", "evidence": "Decreto 1344/2007 art.9", "value": "Jurisdicción90 Servicio de la Deuda Pública", "target_effect": "contexto presupuestario exacto", "source_id": "e0_argentina_decree_1344_2007_original_finance_rule", "status": "EXACT"},
    {"row_id": "SF137_04", "evidence": "Anexo K", "value": "83106000;COMISIONES-BANCO NACION;ARS32270.30;71597;152677;2876;7.2.8", "target_effect": "renglón y claves exactas", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "status": "EXACT_ROW"},
    {"row_id": "SF137_05", "evidence": "Conclusión", "value": "SAF355;2008;Otros Gastos;tres SIDIF", "target_effect": "reduce búsqueda sin inventar caja ni especie", "source_id": "multiple_primary_sources", "status": "RETRIEVAL_KEY_CLOSED_EXCEPT_BOX_AND_TYPE"},
]
write_csv(HERE / "E0_SAF355_PRODUCER_CROSSWALK_V137.csv", saf_crosswalk)

# Corrige la inferencia previa: la columna impresa dice SIDIF, no C-41.
c41_path = HERE / "E0_C41_PAYMENT_EXECUTION_CHAIN_V137.csv"
c41 = read_csv(c41_path)
c41[0].update({
    "stage": "SIDIF_RECORD_REFERENCE", "record": "Anexo K · columna SIDIF",
    "required_or_visible_fields": "71597;152677;2876; cuenta 83106000; importe agregado; tipo documental abierto",
    "execution_meaning": "Localizador exacto, no especie ni ejecución",
    "target_status": "THREE_EXACT_SIDIF_LOCATORS_DOCUMENT_TYPE_OPEN",
    "permitted_inference": "Los números permiten buscar el tipo documental y sus vínculos.",
    "forbidden_inference": "Llamarlos C-41/OB sin recuperar el registro o diccionario correspondiente.",
})
c41.extend([
    {"stage_id": "CP137_18", "stage": "TARGET_PRODUCER", "record": "SAF 355 · Dirección de Administración de la Deuda Pública", "required_or_visible_fields": "SAF355;Jurisdicción90;ejercicio2008", "execution_meaning": "Productor archivístico exacto", "source_id": "e0_cgn_cuenta_inversion_2008_sdp;e0_cgn_account_2008_saf355_356_crosswalk;e0_argentina_decree_1344_2007_original_finance_rule", "target_status": "CLOSED", "permitted_inference": "Buscar en el fondo SAF355, no SAF356 alternativo.", "forbidden_inference": "Que el custodio actual sea necesariamente el SAF."},
    {"stage_id": "CP137_19", "stage": "AMIDDF_REMITTANCE_INDEX", "record": "Planilla de Remisión y tejuelo", "required_or_visible_fields": "productor;serie;subserie;ejercicio;caja;tipo;número;desafectación;firmas", "execution_meaning": "Convierte localizador SIDIF en signatura/caja", "source_id": "e0_cgn_disposition_46_1998_amiddf_annex;e0_cgn_disposition_46_1998_amiddf_remittance_form", "target_status": "SCHEMA_PROVED_TARGET_INDEX_OPEN", "permitted_inference": "Pedir primero la copia/exportación existente de planillas SAF355/2008/Otros Gastos.", "forbidden_inference": "Inventar N° de caja o expediente."},
    {"stage_id": "CP137_20", "stage": "PAGADOR_CLASSIFICATION", "record": "Pagador, fuente y clase de gasto", "required_or_visible_fields": "PAGADOR TGN/SAF;fuente;partida;concepto;importe individual", "execution_meaning": "Determina circuito aplicable", "source_id": "e0_argentina_decree_1344_2007_original_finance_rule;e0_tgn_manual_system_treasury_v1", "target_status": "PUBLIC_DEBT_RULE_PROVED_TARGET_FIELDS_OPEN", "permitted_inference": "Deuda pública va por TGN cualquiera sea el monto bajo el régimen probado.", "forbidden_inference": "Que el título agregado de la cuenta clasifique por sí solo cada registro."},
    {"stage_id": "CP137_21", "stage": "PAPER_TRAIL", "record": "C-41/formulario papel si correspondía", "required_or_visible_fields": "TRANSAF;fecha confirmación;recepción CGN;tipo;número;caja", "execution_meaning": "Respaldo material condicionado", "source_id": "e0_cgn_circular_19_1995_transaf_paper_timing;e0_cgn_circular_33_1995_paper_form_scope;e0_cgn_tgn_joint_disposition_13_16_2009_payment_records", "target_status": "HIGH_PRIORITY_TARGET_APPLICABILITY_NOT_CLOSED", "permitted_inference": "Buscar el papel y su remisión.", "forbidden_inference": "Afirmar presentación individual sin planilla o sello."},
    {"stage_id": "CP137_22", "stage": "TOTAL_PARTIAL_DISTRIBUTION", "record": "Reporte de Distribución Diaria de Pagos", "required_or_visible_fields": "importe devengado;total/parcial;monto/porcentaje;fecha", "execution_meaning": "Define denominador y fracción seleccionada", "source_id": "e0_tgn_manual_system_treasury_v1", "target_status": "RECORD_CLASS_PROVED_TARGET_OPEN", "permitted_inference": "Exigir reporte y saldo antes de calificar pago total.", "forbidden_inference": "Estado P aislado equivale a saldo cero."},
    {"stage_id": "CP137_23", "stage": "BANK_FEE_AUTOMATIC_DEBIT_BRANCH", "record": "Extracto CUT + código de movimiento + regularización", "required_or_visible_fields": "fecha valor;código;débito;importe;cuenta;formulario;conciliación", "execution_meaning": "Ruta propia de gastos bancarios", "source_id": "e0_tgn_manual_system_treasury_v1", "target_status": "ALTERNATIVE_TARGET_BRANCH_OPEN", "permitted_inference": "Buscar esta rama por tratarse de COMISIONES BANCO NACION.", "forbidden_inference": "Sustituirla por una C-41 presumida."},
    {"stage_id": "CP137_24", "stage": "PUBLIC_DEBT_NOTE_BCRA_BRANCH", "record": "Lote/Archivo de Notas de Pago y acuse BCRA", "required_or_visible_fields": "nota;lote;archivo;fecha;importe;acuse;Libro Banco", "execution_meaning": "Ruta de obligaciones de deuda pública", "source_id": "e0_tgn_manual_system_treasury_v1", "target_status": "ALTERNATIVE_TARGET_BRANCH_OPEN", "permitted_inference": "Buscar si el concepto individual fue obligación de deuda.", "forbidden_inference": "Confundir recepción de archivo con cancelación final."},
    {"stage_id": "CP137_25", "stage": "TARGET_BIFURCATED_CLOSE", "record": "Tipo documental + rama aplicable + pago/regularización + conciliación", "required_or_visible_fields": "71597;152677;2876;tipo;importe original;pagos/débitos;estado;saldo;medio;rendición;conciliación", "execution_meaning": "Cierre verificable sin prejuzgar formulario", "source_id": "multiple_primary_sources", "target_status": "OPEN", "permitted_inference": "La primera respuesta debe clasificar especie y circuito; luego se cierra ejecución.", "forbidden_inference": "Confundir renglón anual, orden, selección, transmisión o débito no conciliado con pago total."},
])
assert len(c41) == 25
write_csv(c41_path, c41)

# Ledger: diez avances documentales no monetarios.
ledger_path = HERE / "E0_FISCAL_MECHANISM_LEDGER_V137.csv"
ledger = read_csv(ledger_path)

def ledger_row(number, window, mechanism, phase, payer, recipient, universe, instrument, amount,
               source_id, locator, realization, interpretation, caveat):
    return {"ledger_id": f"F{number}", "window": window, "mechanism": mechanism, "phase": phase,
            "as_of_date": "2026-08-30", "payer": payer, "recipient": recipient, "universe": universe,
            "instrument": instrument, "amount_original": amount, "original_unit": "N/D",
            "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE",
            "source_id": source_id, "source_locator": locator, "realization_status": realization,
            "additivity": "NON_ADDITIVE", "status_interpretation": interpretation, "caveat": caveat}

ledger.extend([
    ledger_row(173, "1998-2026", "Financial_archive", "AMIDDF_ACCESSION_SCHEMA", "SAF355", "AMIDDF", "2008_Otros_Gastos", "remittance_index", "15_FIELDS", "e0_cgn_disposition_46_1998_amiddf_annex;e0_cgn_disposition_46_1998_amiddf_remittance_form", "Planilla_and_instructions", "ACCESSION_FIELDS_PROVED_TARGET_INDEX_OPEN", "The exact archival query can now start from producer/year/subseries/document numbers.", "Box, type and holdings are not yet recovered."),
    ledger_row(174, "2008", "Debt_accounting", "SAF_PRODUCER_IDENTITY", "SAF355", "N/A", "Anexo_K", "institutional_crosswalk", "1", "e0_cgn_cuenta_inversion_2008_sdp;e0_cgn_account_2008_saf355_356_crosswalk", "Cuadro1A_and_UEPEX", "TARGET_PRODUCER_EXACT", "The target producer is SAF355, not an unresolved 355/356 alternative.", "Current custodian remains open."),
    ledger_row(175, "2008", "SIDIF_record", "DOCUMENT_TYPE_CONTROL", "SAF355", "Unknown", "71597_152677_2876", "SIDIF_locator", "3", "e0_cgn_cuenta_inversion_2008_sdp", "Anexo_K", "EXACT_LOCATORS_DOCUMENT_TYPE_OPEN", "The printed column proves SIDIF references only.", "C41 classification is not printed."),
    ledger_row(176, "1995-2009", "Paper_payment_records", "TEMPORAL_SCOPE", "SAF355", "CGN_TGN", "paper_forms", "C41_or_other", "N/D", "e0_cgn_circular_19_1995_transaf_paper_timing;e0_cgn_circular_33_1995_paper_form_scope;e0_cgn_tgn_joint_disposition_13_16_2009_payment_records", "paper_rules", "PAPER_ROUTE_PRIORITY_SCOPE_NOT_FULLY_CLOSED", "A paper trail is strongly targetable and Circular33 remained until March 2009.", "The SAF355/356 final phrase has placement ambiguity."),
    ledger_row(177, "2007-2013", "Treasury_payment", "PAGADOR_TGN_RULE", "TGN", "Public_debt_creditor", "public_debt", "payment_order", "ANY_AMOUNT", "e0_argentina_decree_1344_2007_original_finance_rule;e0_tgn_manual_system_treasury_v1", "Decree35g5;Manual_pp104_105", "PAYER_RULE_PROVED_TARGET_CLASSIFICATION_OPEN", "Public-debt payments are not excluded from TGN by the ARS100k threshold.", "Each target record still needs source/class fields."),
    ledger_row(178, "2007-2013", "Treasury_payment", "TOTAL_PARTIAL_CLASSIFICATION", "TGN_or_SAF", "Beneficiary", "payment_records", "daily_distribution_report", "TOTAL_OR_PARTIAL", "e0_tgn_manual_system_treasury_v1", "Manual_pp105_106_113_114", "RECORD_CLASS_PROVED_TARGET_VALUES_OPEN", "The daily report carries the total/partial decision.", "No target report is located."),
    ledger_row(179, "2008-2013", "Bank_commissions", "AUTOMATIC_DEBIT_BRANCH", "TGN", "BNA", "bank_fees", "CUT_debit_regularization", "32270.30_AGGREGATE", "e0_tgn_manual_system_treasury_v1;e0_cgn_cuenta_inversion_2008_sdp", "Manual_p112;AnexoK", "ALTERNATIVE_EXECUTION_ROUTE_IDENTIFIED", "Bank charges may leave an extract-code and regularization trail.", "The manual does not assign the target row to this route."),
    ledger_row(180, "2008-2013", "Public_debt_payment", "BCRA_NOTE_BRANCH", "TGN", "BCRA", "public_debt_obligations", "note_batch_file_ack", "N/D", "e0_tgn_manual_system_treasury_v1", "Manual_pp109_110_115_118", "ALTERNATIVE_EXECUTION_ROUTE_IDENTIFIED", "Debt obligations can be followed through note batches, files and BCRA acknowledgments.", "No target batch or acknowledgment is located."),
    ledger_row(181, "2016-2026", "Public_information", "LEGAL_REQUEST_FIT", "N/A", "Economy_RAIP", "existing_records", "index_copy_export", "11_RULES", "e0_argentina_law_27275_updated_access;e0_argentina_economia_access_channel_2026;e0_argentina_tad_public_information_route", "Law_arts1_4_5_9_15", "REQUEST_LEGALLY_REFINED_NOT_SENT", "The request now asks for existing indices and documents, transfer and partial release.", "No request was submitted."),
    ledger_row(182, "2008-2026", "Executed_settlement_evidence", "V137_REVALIDATION", "Treasury", "Named_participants", "ten_award_rows", "full_execution_chain", "0/10", "multiple_primary_sources", "V137_matrices", "UNCHANGED_ZERO_CONFIRMED_NOT_ZERO_EXECUTION", "Producer and request keys improved but no execution row closed.", "Evidence status is not a monetary zero."),
])
assert len(ledger) == 182
write_csv(ledger_path, ledger)

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V137.csv"
breaks = read_csv(breaks_path)
breaks.extend([
    {"break_id": "amiddf_competence_not_target_holding", "dimension": "archive", "problem": "AMIDDF competence and schema do not prove a target remittance.", "rule": "Require the completed remittance/index row and box before asserting custody.", "status": "FROZEN", "evidence": "Disposición 46/98; Planilla de Remisión"},
    {"break_id": "historic_query_route_not_current_public_right", "dimension": "access", "problem": "The 1998 SAF/control/judicial query procedure is not the current citizen route.", "rule": "Use Law 27.275 through the Ministry RAIP and keep the historic rule only for custody mechanics.", "status": "FROZEN", "evidence": "Disposición 46/98; Ley 27.275"},
    {"break_id": "sidif_number_not_c41_type", "dimension": "document_type", "problem": "Anexo K labels the column SIDIF, not C-41.", "rule": "Call 71597, 152677 and 2876 SIDIF locators until the type field is recovered.", "status": "FROZEN", "evidence": "Cuenta de Inversión 2008 Anexo K"},
    {"break_id": "c43_not_c41", "dimension": "form_scope", "problem": "C-43 form and file-flow sources are adjacent but different.", "rule": "Never use C-43 fields or filenames to establish C-41 behavior.", "status": "FROZEN", "evidence": "Disposición 28/01; Circular 16/00"},
    {"break_id": "paper_obligation_conditional_temporal", "dimension": "paper_record", "problem": "Paper rules vary by source, amount, payer and date.", "rule": "Request the paper trail but mark target applicability open until form/payer/source or remittance is returned.", "status": "FROZEN", "evidence": "Circulares 19/95, 33/95; Disposición conjunta 13/16-2009"},
    {"break_id": "existing_record_not_custom_certification", "dimension": "public_access", "problem": "Law 27.275 does not require the agency to create or classify a new table.", "rule": "Ask for copies/exports of existing indices and records; use a custom table only if it already exists.", "status": "FROZEN", "evidence": "Ley 27.275 art.5"},
    {"break_id": "bank_name_not_payment_route", "dimension": "execution", "problem": "COMISIONES BANCO NACION does not identify Red CUT, Nota, exterior or automatic debit.", "rule": "Run the branches in parallel and select only from the recovered document type and movement.", "status": "FROZEN", "evidence": "Anexo K; Manual TGN"},
    {"break_id": "selection_confirmation_transmission_not_reconciliation", "dimension": "payment_stage", "problem": "Selection, confirmation, file generation, transmission, bank response and reconciliation are distinct.", "rule": "Do not close payment until amount history and the applicable bank/regularization chain reconcile.", "status": "FROZEN", "evidence": "Manual TGN pp.104-118; Decreto 1344/07 art.31"},
])
assert len(breaks) == 141
write_csv(breaks_path, breaks)

trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V137.csv"
trace = read_csv(trace_path)
trace.extend([
    {"trace_id": "TR137_127", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / CGN / AGAN-AMIDDF", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Planillas de Remisión preexistentes del productor SAF 355", "period_or_date": "2008", "identifiers": "SAF355;Rendiciones de Cuentas;Otros Gastos;71597;152677;2876", "minimum_usable_fields": "remitente;productor;serie;subserie;ejercicio;caja;tipo;número;desafectación;observaciones;firmas", "confidentiality_fallback": "copia/exportación en el estado en que obre con tachas parciales", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR137_128", "request_id": "REQ134_ECON", "institution": "SAF 355 / AGAN-AMIDDF", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Tejuelo, inventario y constancia de recepción de cajas", "period_or_date": "2008-2011", "identifiers": "SAF355;2008;Otros Gastos", "minimum_usable_fields": "período;orden;caja;agente;fecha;firma", "confidentiality_fallback": "metadatos de ubicación y transferencia", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR137_129", "request_id": "REQ134_ECON", "institution": "SAF 355 / CGN / TGN", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Identificación del tipo documental de cada referencia SIDIF", "period_or_date": "2008", "identifiers": "71597;152677;2876;83106000", "minimum_usable_fields": "tipo;fecha;importe;beneficiario;expediente;formulario vinculado", "confidentiality_fallback": "salida preexistente del índice o diccionario", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR137_130", "request_id": "REQ134_ECON", "institution": "SAF 355 / TGN", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Pagador, fuente, clase de gasto y Reporte de Distribución Diaria", "period_or_date": "2008", "identifiers": "71597;152677;2876;Resolución374/2007", "minimum_usable_fields": "pagador;fuente;clase;devengado;total/parcial;importe;fecha", "confidentiality_fallback": "filas existentes testadas", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR137_131", "request_id": "REQ134_ECON", "institution": "SAF 355 / CGN / TGN", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Confirmación, saldo y medio de pago", "period_or_date": "2008-2010", "identifiers": "71597;152677;2876;identificador bancario", "minimum_usable_fields": "selección;confirmación;importe;saldo;medio;lote;archivo", "confidentiality_fallback": "metadatos del evento", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR137_132", "request_id": "REQ134_ECON", "institution": "TGN / BNA", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Rama de débito automático por gastos bancarios", "period_or_date": "2008", "identifiers": "83106000;COMISIONES BANCO NACION;ARS32270.30;CUT", "minimum_usable_fields": "cuenta;código movimiento;fecha valor;débito;regularización;conciliación", "confidentiality_fallback": "movimientos agregados por fecha e importe", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR137_133", "request_id": "REQ134_BNA", "institution": "Banco de la Nación Argentina", "gap_id": "CL134_PAYMENT", "requested_record": "Rendición o soporte del eventual débito de comisiones", "period_or_date": "2008", "identifiers": "83106000;ARS32270.30;71597;152677;2876", "minimum_usable_fields": "fecha;importe;cuenta origen;concepto;código;aceptación/rechazo;referencia", "confidentiality_fallback": "registro disociado", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR137_134", "request_id": "REQ134_BCRA", "institution": "TGN / BCRA", "gap_id": "CL134_PAYMENT", "requested_record": "Rama de Nota de Pago de deuda pública", "period_or_date": "2008", "identifiers": "SAF355;71597;152677;2876;Archivo de Notas", "minimum_usable_fields": "nota;lote;archivo;fecha;importe;acuse;Libro Banco", "confidentiality_fallback": "metadatos de lote y confirmación", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR137_135", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / RAIP", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Transferencia al custodio si el receptor no posee la información", "period_or_date": "cinco días desde presentación futura", "identifiers": "Ley27275 art10", "minimum_usable_fields": "fecha;organismo receptor;organismo derivado;constancia", "confidentiality_fallback": "N/A", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR137_136", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / RAIP", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Respuesta parcial o denegatoria fundada", "period_or_date": "15+15 días desde presentación futura", "identifiers": "Ley27275 arts5,11,12,13,15", "minimum_usable_fields": "documentos existentes;tachas;fundamento;alcance búsqueda;fecha", "confidentiality_fallback": "versión disociada", "status": "DRAFT_NOT_SENT"},
])
assert len(trace) == 136
write_csv(trace_path, trace)

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V137.csv"
keys = read_csv(keys_path)
keys.extend([
    {"key_id": "SK137_133", "request_id": "REQ134_ECON", "key_group": "producer_exact", "exact_key": "SAF355;Dirección de Administración de la Deuda Pública", "search_purpose": "cerrar organismo productor", "source_or_basis": "Cuenta de Inversión 2008 Cuadro1A", "caveat": "Custodio actual abierto."},
    {"key_id": "SK137_134", "request_id": "REQ134_ECON", "key_group": "archive_series", "exact_key": "Rendiciones de Cuentas;Otros Gastos;Ejercicio2008", "search_purpose": "filtrar planillas AMIDDF", "source_or_basis": "Disposición46/98", "caveat": "Caja desconocida."},
    {"key_id": "SK137_135", "request_id": "REQ134_ECON", "key_group": "remittance_document_numbers", "exact_key": "71597;152677;2876", "search_purpose": "buscar N° documento", "source_or_basis": "AnexoK 2008", "caveat": "Tipo documental abierto."},
    {"key_id": "SK137_136", "request_id": "REQ134_ECON", "key_group": "remittance_fields", "exact_key": "remitente;productor;serie;subserie;ejercicio;caja;tipo;número;desafectación;observaciones", "search_purpose": "pedir índice preexistente", "source_or_basis": "Planilla AMIDDF", "caveat": "No pedir crear cuadro."},
    {"key_id": "SK137_137", "request_id": "REQ134_ECON", "key_group": "box_label", "exact_key": "SAF355;2008;periodo;Otros Gastos;número de orden", "search_purpose": "localizar tejuelo", "source_or_basis": "Disposición46/98", "caveat": "Orden/caja abiertos."},
    {"key_id": "SK137_138", "request_id": "REQ134_ECON", "key_group": "document_type", "exact_key": "SIDIF;C-41;C-55;regularización;débito automático", "search_purpose": "clasificar la especie antes de seguir circuito", "source_or_basis": "AnexoK + ManualTGN", "caveat": "No asumir C-41."},
    {"key_id": "SK137_139", "request_id": "REQ134_ECON", "key_group": "payer_rule", "exact_key": "PAGADOR TGN;Pago de Deuda Pública;cualquier monto", "search_purpose": "identificar pagador", "source_or_basis": "Decreto1344/07 + ManualTGN", "caveat": "Fuente/clase individual abiertas."},
    {"key_id": "SK137_140", "request_id": "REQ134_ECON", "key_group": "distribution_report", "exact_key": "Reporte de Distribución Diaria de Pagos;Total;Parcial;Monto Distribuido", "search_purpose": "separar pago total/parcial", "source_or_basis": "ManualTGN", "caveat": "Reporte target abierto."},
    {"key_id": "SK137_141", "request_id": "REQ134_ECON", "key_group": "automatic_debit", "exact_key": "Débito Automático;gastos bancarios;código de movimiento;extracto CUT;regularización", "search_purpose": "seguir rama comisiones BNA", "source_or_basis": "ManualTGN p112", "caveat": "Aplicabilidad target abierta."},
    {"key_id": "SK137_142", "request_id": "REQ134_BNA", "key_group": "bna_return", "exact_key": "rendición bancaria;acreditado;rechazado;fecha compensación;monto procesado", "search_purpose": "cerrar resultado bancario", "source_or_basis": "ManualTGN pp117-118", "caveat": "Rama RedCUT/débito a clasificar."},
    {"key_id": "SK137_143", "request_id": "REQ134_BCRA", "key_group": "bcra_note", "exact_key": "Lote de Notas;Archivo de Notas;confirmación de recepción;Libro Banco", "search_purpose": "seguir rama deuda BCRA", "source_or_basis": "ManualTGN pp116-118", "caveat": "Acuse no equivale a cancelación."},
    {"key_id": "SK137_144", "request_id": "REQ134_ECON", "key_group": "law_existing_records", "exact_key": "Ley27275 art5;estado en que se encuentre;formato digital abierto", "search_purpose": "evitar pedido de elaboración nueva", "source_or_basis": "Ley27275", "caveat": "Sólo registros existentes."},
    {"key_id": "SK137_145", "request_id": "REQ134_ECON", "key_group": "law_transfer_partial", "exact_key": "art10 transferencia5d;art12 tachas;art13 acto fundado", "search_purpose": "prever derivación y respuesta parcial", "source_or_basis": "Ley27275", "caveat": "Sólo tras presentación."},
    {"key_id": "SK137_146", "request_id": "REQ134_ECON", "key_group": "current_channel", "exact_key": "TAD;ciudadano@mecon.gov.ar;Balcarce186 piso1 oficina148;4349-8705", "search_purpose": "canal actual Ministerio", "source_or_basis": "Economía actualizado junio2026", "caveat": "No contactado."},
])
assert len(keys) == 146
write_csv(keys_path, keys)

# Canal vigente y borradores: ningún envío.
channels_path = HERE / "CURRENT_OFFICIAL_SUBMISSION_CHANNELS_V137.csv"
channels = read_csv(channels_path)
for row in channels:
    if row["channel_id"] == "CH118_00":
        row.update({"verified_on": "2026-08-30", "caveat": "Ruta TAD general verificada; no iniciada. Toda persona puede solicitar sin motivo ni abogado."})
    if row["channel_id"] == "CH118_01":
        row.update({"email_or_contact": "ciudadano@mecon.gov.ar; (54-11) 4349-8705", "physical_route": "Balcarce 186 piso 1 oficina 148 CABA; 10:00–17:00", "verified_on": "2026-08-30", "page_freshness": "Actualizada junio 2026", "caveat": "TAD/email/mesa verificados; no enviar sin autorización expresa."})
write_csv(channels_path, channels)

econ_path = HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V137.md"
econ_path.write_text(econ_path.read_text(encoding="utf-8-sig").rstrip() + """

## Clave V137 · productor exacto, índice AMIDDF y bifurcación de comisiones

La Cuenta de Inversión 2008 identifica en su propio Cuadro 1-A al productor como `SAF 355 · Dirección de Administración de la Deuda Pública`; queda descartado `SAF 356` como alternativa para este renglón. El Anexo K sólo titula su última columna `SIDIF`: confirma que `71597`, `152677` y `2876` son localizadores exactos de `83106000 COMISIONES - BANCO NACION`, pero no imprime que sean números de formulario `C-41`. Donde versiones anteriores del borrador dicen “OB” o “C-41” para esos tres números, debe leerse como hipótesis de búsqueda pendiente de clasificación documental.

Como primera capa solicito copia o exportación de las **Planillas de Remisión preexistentes**, en el estado en que obren, que correspondan a: organismo productor `SAF 355`, serie `Rendiciones de Cuentas`, subserie `Otros Gastos`, ejercicio `2008` y números documentales `71597`, `152677` o `2876`. Sus campos oficiales son remitente, productor, serie, subserie, ejercicio, fechas extremas, número de caja, tipo documental, número documental, fecha de desafectación, observaciones y firmas de Administración/Archivo/recepción AMIDDF. Solicito también el tejuelo e inventario de la caja y la constancia de recepción. No conozco el número de caja y por eso no lo invento: debe surgir del índice.

Con el tipo documental identificado, solicito el original o copia autenticada, todos los cuerpos, folios y anexos y la cadena aplicable. La Disposición 46/1998 exige originales —o sustitutos autenticados si el original falta o está deteriorado— y separa la responsabilidad según el envío haya sido para digitalización o mera guarda. Una fecha de desafectación en la planilla no prueba destrucción: si se invoca baja, solicito el acto individualizable y el registro de expurgo/desafectación.

Para cada referencia se solicitan pagador, fuente, clase de gasto, importe individual, beneficiario, expediente, fecha, estado y vínculos. El régimen de 2007 y su interpretación oficial posterior establecen que el pago de deuda pública es `PAGADOR TGN` cualquiera sea el monto; por eso el agregado de ARS 32.270,30 no excluye el circuito TGN por estar debajo de un umbral. Sin embargo, la clasificación individual debe provenir del registro, no del título agregado.

La búsqueda debe abrir dos ramas y cerrar la que corresponda:

1. Si se trató de una orden/comprobante pasible de pago: Reporte de Distribución Diaria que marque total o parcial, selección, confirmación, identificador bancario, medio, lote/archivo, rendición bancaria, pagos acumulados, saldo y conciliación. Si fue deuda cancelada por Nota: lote y Archivo de Notas a BCRA, confirmación de recepción e impacto en Libro Banco.
2. Si se trató de comisiones debitadas automáticamente por BNA: extracto de la CUT, código específico de movimiento, fecha valor, cuenta, débito individual, formulario de regularización, conciliación bancaria y afectación de la cuenta escritural. La propia denominación “comisiones” vuelve esta rama necesaria; no demuestra que haya sido la utilizada.

La regla papel se mantiene como objetivo probatorio y no como hecho target: Circular 19/1995 fija el plazo posterior a TRANSAF; Circular 33/1995 siguió vigente hasta su derogación expresa en marzo de 2009, pero su frase final sobre SAF 355/356 está ubicada después del apartado C-43 y se preserva con esa reserva de alcance. Se solicitan la planilla, el sello de recepción y el papel si existieron, sin afirmar anticipadamente que cada registro fue C-41.

Este pedido no exige producir análisis, clasificaciones o cuadros nuevos. Pide copias y exportaciones de registros existentes conforme al artículo 5 de la Ley 27.275. Si el Ministerio no los posee, solicito la transferencia prevista por el artículo 10 dentro de cinco días; si parte está exceptuada, versión disociada conforme al artículo 12; y si no existe o se deniega, acto fundado con alcance de búsqueda conforme al artículo 13. Canal vigente verificado: TAD, `ciudadano@mecon.gov.ar`, o Balcarce 186, piso 1, oficina 148. Estado: **BORRADOR_NO_ENVIADO**.
""", encoding="utf-8")

bna_path = HERE / "REQUEST_BNA_FIRST_STAGE_BLOTTER_V137.md"
bna_path.write_text(bna_path.read_text(encoding="utf-8-sig").rstrip() + """

## Clave V137 · eventual débito de comisiones

Además del blotter de recompra, si obran registros vinculados a `83106000 COMISIONES - BANCO NACION`, SIDIF `71597`, `152677`, `2876` y agregado anual ARS `32.270,30`, se solicita la copia/exportación preexistente de cada débito, con fecha valor, cuenta de origen, concepto, código de movimiento, importe, referencia, resultado y rendición o conciliación remitida a TGN. Se pide esta rama porque el Manual oficial de Tesorería identifica gastos bancarios debitados automáticamente y regularizados después; no se afirma que sea la ruta target. Puede entregarse con datos personales disociados. Estado: **BORRADOR_NO_ENVIADO**.
""", encoding="utf-8")

bcra_path = HERE / "REQUEST_BCRA_CRYL_SETTLEMENT_V137.md"
bcra_path.write_text(bcra_path.read_text(encoding="utf-8-sig").rstrip() + """

## Clave V137 · Archivos de Notas y acuses BCRA

Si alguno de los registros SIDIF `71597`, `152677` o `2876` corresponde a una obligación de deuda pública cancelada por Nota, se solicita la copia/exportación preexistente del lote y Archivo de Notas de Pago recibido desde TGN, fecha/hora, importe, referencia, confirmación de recepción, movimiento financiero y conciliación. El acuse de archivo debe mantenerse separado de la cancelación final y de cualquier movimiento CRYL específico. Si la ruta no fue aplicable, se pide el registro existente que identifique el medio efectivamente usado, no una certificación nueva. Estado: **BORRADOR_NO_ENVIADO**.
""", encoding="utf-8")

checklist_path = HERE / "REQUEST_SUBMISSION_CHECKLIST_V137.md"
checklist_path.write_text(checklist_path.read_text(encoding="utf-8-sig").rstrip() + """

## Control V137 previo a cualquier autorización

- llamar `71597`, `152677` y `2876` “referencias SIDIF” hasta recibir el tipo documental;
- comenzar por Planilla de Remisión/tejuelo del productor `SAF 355`, ejercicio 2008, subserie `Otros Gastos`;
- pedir copias o exportaciones preexistentes, no la elaboración de un cuadro certificado nuevo;
- abrir en paralelo la rama orden/Nota BCRA y la rama débito automático/regularización BNA;
- registrar por separado programación, selección, confirmación, medio, envío, rendición, conciliación y saldo;
- si el receptor no posee, pedir transferencia del artículo 10; si hay excepción parcial, tachas del artículo 12;
- no calcular plazos ni reclamos mientras los seis pedidos continúen `DRAFT_NOT_SENT`.
""", encoding="utf-8")

# Síntesis.
(HERE / "README_V137.md").write_text("""# V137 · índice AMIDDF, SAF 355 y doble ruta de comisiones

V137 cierra el productor exacto del Anexo K como `SAF 355` y convierte la ruta AGAN/AMIDDF en una consulta reproducible: `SAF 355 + ejercicio 2008 + Rendiciones de Cuentas + Otros Gastos + 71597/152677/2876`, dejando caja y tipo documental como salidas a obtener. Corrige una inferencia previa: la columna oficial dice `SIDIF`, no `C-41`; hasta recuperar la especie, los tres números son localizadores. La investigación abre dos rutas verificables para `COMISIONES - BANCO NACION`: orden/Nota de deuda por TGN-BCRA o débito automático/regularización BNA-CUT. La Ley 27.275 refina el pedido hacia índices y copias existentes, transferencia, tachas y denegación fundada. Resultado estricto sin cambio: 10/10 adjudicaciones, 9/10 cuentas candidatas y 0/10 ejecuciones confirmadas; seis pedidos DRAFT_NOT_SENT.
""", encoding="utf-8")

(HERE / "VEREDICTO_V137.md").write_text("""# Veredicto V137

La búsqueda histórica ya no parte de `SAF 355/356`: el productor exacto es `SAF 355 · Dirección de Administración de la Deuda Pública`. Tampoco debe presentar como hecho que `71597`, `152677` y `2876` sean C-41: el Anexo K sólo los rotula como SIDIF. La Planilla AMIDDF ofrece la vía más corta para resolver caja, tipo documental y remisión.

El umbral monetario no descarta TGN cuando el concepto individual sea deuda pública; pero `COMISIONES BANCO NACION` también exige investigar la ruta de débito automático, extracto CUT, regularización y conciliación. Sólo el registro recuperado decide entre las ramas.

No apareció todavía ningún movimiento target, pago total, débito conciliado, Archivo de Notas, acuse BCRA ni ejecución CRYL. El balance permanece en 10 adjudicaciones exactas, 9 cuentas candidatas y 0/10 ejecuciones confirmadas. Los seis pedidos continúan sin enviar.
""", encoding="utf-8")

(HERE / "E0_FISCAL_RECONSTRUCTION_V137.md").write_text("""# Reconstrucción fiscal E0 · V137

El avance de V137 es probatorio y no agrega magnitudes. Cierra el productor SAF 355, congela el tipo documental como abierto y define el índice AMIDDF exacto que debe obtenerse. Se preservan dos rutas de ejecución alternativas: orden/Nota de deuda y débito automático de gastos bancarios. Ninguna se atribuye a los target sin registro. La cobertura estricta permanece en 61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%; 0/10 ejecuciones confirmadas.
""", encoding="utf-8")

handover = """# Handover V137 → V138

## Estado

- QA V137: ejecutar y exigir PASS.
- Fuentes nuevas: 15 oficiales preservadas; Planilla AMIDDF y Manual TGN inspeccionados visualmente.
- Productor target: `SAF 355` exacto; `SAF 356` descartado para el Anexo K.
- Clave archivística: `SAF355 + 2008 + Rendiciones de Cuentas + Otros Gastos + 71597/152677/2876`.
- Caja, tipo documental, remisión e imágenes target: abiertos.
- Corrección: la columna impresa dice `SIDIF`; C-41 es hipótesis, no hecho.
- Rutas abiertas: orden/Nota TGN-BCRA o débito automático/regularización BNA-CUT.
- Ley 27.275: pedir registros existentes; transferencia en 5 días; tachas; acto fundado; 15+15; reclamo 40 días sólo tras envío.
- Seis pedidos `DRAFT_NOT_SENT`; ninguno enviado.
- Escalera: 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas.

## Prioridad V138

1. Mantener los seis pedidos como borradores salvo autorización expresa.
2. Si se autoriza, presentar primero Economía/RAIP con la Planilla de Remisión como objeto prioritario.
3. Obtener N° caja y tipo documental antes de volver a llamar C-41 a los tres SIDIF.
4. Recuperar Reporte de Distribución Diaria, confirmación, medio, rendición y saldo.
5. Ejecutar rama BNA de débito automático/regularización y rama BCRA de Archivos de Notas sin mezclarlas.
6. Verificar papel 2008 mediante remisión/sello, no por retroproyección del procedimiento 2009.
7. Mantener separados Caja, pago bancario, baja SIGADE y cancelación CRYL.
"""
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V137_A_V138.md").write_text(handover, encoding="utf-8")

(HERE / "AUDITORIA_V137.md").write_text(f"""# Auditoría V137

- Fuentes maestras: {len(catalog)}; quince fuentes oficiales nuevas preservadas.
- Fuentes primarias E0: {len(census)}.
- Índice AMIDDF: {len(remittance)} campos; productor exacto, caja y tipo abiertos.
- Cadena de custodia: {len(custody_route)} etapas; acceso legal: {len(access_fit)} reglas.
- Papel C-41: {len(paper_matrix)} controles temporales; aplicabilidad target no afirmada.
- Separación de pago: {len(payment_stages)} etapas y dos ramas target.
- Ledger fiscal: {len(ledger)} filas; cortes metodológicos: {len(breaks)}.
- Trazabilidad: {len(trace)} objetos; claves: {len(keys)}.
- Escalera: 10 adjudicaciones; 9 cuentas candidatas; 0 ejecuciones confirmadas.
- Pedidos: 6 borradores, 0 enviados; panel estricto {STRICT}% sin cambios.
""", encoding="utf-8")

# Registro de respuesta y estado: congelar no envío.
register_path = HERE / "E0_REQUEST_RESPONSE_REGISTER_V137.csv"
register = read_csv(register_path)
for row in register:
    if "status" in row:
        row["status"] = "DRAFT_NOT_SENT"
write_csv(register_path, register)

for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    shutil.copyfile(AUDIT / f"{stem}_V136.csv", AUDIT / f"{stem}_V137.csv")

hash_rows = []
for row in catalog:
    local = row["archivo_local"]
    path = REPO / local.lstrip("/") if local else None
    exists = bool(path and path.is_file())
    actual = sha256(path) if exists else ""
    expected = row["sha256"]
    hash_rows.append({"id": row["id"], "archivo_local": local, "exists": str(exists), "sha_catalog": expected, "sha_actual": actual, "hash_ok": str(bool(exists and expected and actual.lower() == expected.lower()))})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V137.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V137.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
assert physical == hash_ok == 397

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or "tmp" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": str(size), "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V137.csv", size_rows)

completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V136.json").read_text(encoding="utf-8"))
for key in list(completeness):
    if key.endswith("_v136") or "newly_preserved_v136" in key:
        completeness.pop(key, None)
completeness.update({
    "checkpoint": "V137", "date": "2026-08-30",
    "state": "E0_SAF355_AMIDDF_INDEX_AND_BIFURCATED_PAYMENT_ROUTE_PROVED_TARGET_RECORDS_OPEN_NOT_SENT",
    "numeric_v137_strict_changed": False, "master_catalog_entries": len(catalog),
    "physical_local_copies": physical, "physical_local_hash_ok": hash_ok,
    "e0_primary_sources_preserved": len(census), "e0_quality": "PRIMARY_ARCHIVAL_INDEX_PAYMENT_STAGE_AND_ACCESS_LAW_CONTROLS",
    "sources_newly_preserved_v137": 15, "e0_primary_sources_newly_preserved_v137": 15,
    "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
    "e0_request_traceability_rows": len(trace), "e0_request_search_keys": len(keys),
    "e0_c41_chain_rows": len(c41), "e0_sidif_target_ids": 3, "e0_sidif_target_document_types_located": 0,
    "e0_c41_target_bodies_located": 0, "e0_c41_target_payment_state_rows_located": 0,
    "e0_target_producer_saf355_proved": True, "e0_target_saf356_excluded_as_producer": True,
    "e0_amiddf_remittance_schema_rows": len(remittance), "e0_amiddf_target_box_located": False,
    "e0_amiddf_target_remittance_rows_located": 0, "e0_amiddf_target_holdings_located": 0,
    "e0_access_legal_fit_rows": len(access_fit), "e0_paper_temporal_rows": len(paper_matrix),
    "e0_payment_stage_rows": len(payment_stages), "e0_automatic_debit_target_rows_located": 0,
    "e0_bcra_note_target_rows_located": 0, "e0_cryl_specific_2008_movement_route_proved": False,
    "e0_settlement_award_rows_exact": 10, "e0_settlement_account_candidate_rows": 9,
    "e0_settlement_executed_rows_confirmed": 0, "e0_requests_submitted": 0,
    "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
    "historical_workstream": "SAF355 producer exact; AMIDDF accession schema and current legal access route proved; SIDIF document type, target box/body, total/partial history, automatic-debit or BCRA-note branch, bank reconciliation, CRYL and executed settlement remain open; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V137.json").write_text(json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V137 · índice AMIDDF, SAF 355 y bifurcación bancaria"
backup_text = backup.read_text(encoding="utf-8-sig")
if marker not in backup_text:
    backup_text += f"\n\n{marker}\n\n- Productor exacto: SAF 355; clave archivística AMIDDF reconstruida hasta caja/tipo documental.\n- Corrección estricta: 71597, 152677 y 2876 son referencias SIDIF; C-41 permanece hipótesis.\n- Dos rutas: orden/Nota TGN-BCRA o débito automático/regularización BNA-CUT.\n- Ley 27.275 aplicada a registros existentes, transferencia, tachas y acto fundado.\n- 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas; seis borradores no enviados.\n"
    backup.write_text(backup_text, encoding="utf-8")

inherited = [
    {"script": "qa_v136.py", "pre_v137_result": "PASS", "post_v137_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V136 queda supersedido por fuentes, conteos y corrección documental V137."},
    {"script": "qa_v137.py", "pre_v137_result": "N/A", "post_v137_result": "PASS", "interpretation": "SAF355, índice AMIDDF, Ley 27.275, bifurcación bancaria, hashes y no envío verificados."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V137.csv", inherited)

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

remit = rows("E0_AMIDDF_REMITTANCE_INDEX_SCHEMA_V137.csv")
assert len(remit) == 15 and remit[1]["target_value"].startswith("SAF 355")
assert remit[7]["official_field"] == "N° caja" and remit[7]["status"] == "OPEN_CRITICAL"
assert remit[8]["status"] == "OPEN_CRITICAL" and remit[9]["target_value"] == "71597;152677;2876"

custody = rows("E0_AMIDDF_CUSTODY_RESPONSIBILITY_ROUTE_V137.csv")
access = rows("E0_ACCESS_INFORMATION_LEGAL_FIT_V137.csv")
paper = rows("E0_C41_PAPER_OBLIGATION_TEMPORAL_MATRIX_V137.csv")
negative = rows("E0_FORM_SCOPE_NEGATIVE_CONTROLS_V137.csv")
first = rows("E0_TARGET_FIRST_STAGE_REQUEST_OBJECTS_V137.csv")
doctype = rows("E0_SIDIF_TARGET_DOCUMENT_TYPE_AUDIT_V137.csv")
stages = rows("E0_PAYMENT_STAGE_SEPARATION_V137.csv")
saf = rows("E0_SAF355_PRODUCER_CROSSWALK_V137.csv")
assert len(custody) == 10 and len(access) == 11 and len(paper) == 8
assert len(negative) == 4 and len(first) == 10 and len(doctype) == 5
assert len(stages) == 10 and len(saf) == 5
assert doctype[0]["status"] == "EXACT_LOCATORS_DOCUMENT_TYPE_OPEN"
assert any(r["stage"] == "DÉBITO_AUTOMÁTICO" for r in stages)
assert any(r["stage"] == "MEDIO_NOTA" for r in stages)

c41 = rows("E0_C41_PAYMENT_EXECUTION_CHAIN_V137.csv")
assert len(c41) == 25 and c41[0]["stage"] == "SIDIF_RECORD_REFERENCE"
assert c41[-1]["stage"] == "TARGET_BIFURCATED_CLOSE" and c41[-1]["target_status"] == "OPEN"
assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V137.csv")) == 182
assert len(rows("E0_FISCAL_METHOD_BREAKS_V137.csv")) == 141
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V137.csv")) == 136
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V137.csv")) == 146

ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V137.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V137.csv")}
new_ids = {
    "e0_cgn_disposition_46_1998_amiddf_procedure", "e0_cgn_disposition_46_1998_amiddf_annex",
    "e0_cgn_disposition_46_1998_amiddf_remittance_form", "e0_cgn_circular_30_1994_supporting_document_archive",
    "e0_cgn_circular_33_1995_paper_form_scope", "e0_cgn_disposition_28_2001_c43_negative_control",
    "e0_cgn_circular_16_2000_c43_negative_control", "e0_cgn_circular_19_1995_transaf_paper_timing",
    "e0_cgn_circular_05_2013_c41_paper_ordering", "e0_argentina_decree_1344_2007_original_finance_rule",
    "e0_argentina_law_27275_updated_access", "e0_argentina_economia_access_channel_2026",
    "e0_argentina_tad_public_information_route", "e0_tgn_manual_system_treasury_v1",
    "e0_cgn_account_2008_saf355_356_crosswalk",
}
assert len(census) == 163 and new_ids <= set(census)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 403 and len({r["id"] for r in catalog}) == 403

expected = ''' + repr(EXPECTED) + r'''
bin_dir = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v137" / "binaries"
assert len(list(bin_dir.iterdir())) == 15
for name, (size, digest) in expected.items():
    path = bin_dir / name
    assert path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest() == digest

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V137.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V137"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 397
assert complete["e0_target_producer_saf355_proved"] is True
assert complete["e0_sidif_target_document_types_located"] == 0
assert complete["e0_amiddf_target_box_located"] is False
assert complete["e0_automatic_debit_target_rows_located"] == 0
assert complete["e0_bcra_note_target_rows_located"] == 0
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v137_strict_changed"] is False

for name, marker in {
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V137.md": "## Clave V137 · productor exacto, índice AMIDDF y bifurcación de comisiones",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V137.md": "## Clave V137 · eventual débito de comisiones",
    "REQUEST_BCRA_CRYL_SETTLEMENT_V137.md": "## Clave V137 · Archivos de Notas y acuses BCRA",
}.items():
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert marker in text and "BORRADOR_NO_ENVIADO" in text

assert all(r.get("status") == "DRAFT_NOT_SENT" for r in rows("E0_REQUEST_RESPONSE_REGISTER_V137.csv"))
for name in ("README_V137.md", "VEREDICTO_V137.md", "E0_FISCAL_RECONSTRUCTION_V137.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V137_A_V138.md"):
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")

print("V137 QA PASS")
'''
(HERE / "qa_v137.py").write_text(qa, encoding="utf-8")

def checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V137.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V137", "parent_checkpoint": "V136",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": 15, "new_primary_sources": 15,
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks),
        "amiddf_remittance_schema_rows": len(remittance), "amiddf_target_box_located": False,
        "target_producer_saf355_proved": True, "sidif_target_document_types_located": 0,
        "c41_chain_rows": len(c41), "automatic_debit_target_rows_located": 0, "bcra_note_target_rows_located": 0,
        "award_rows_exact": 10, "account_candidate_rows": 9, "executed_settlement_rows_confirmed": 0,
        "request_drafts": 6, "request_traceability_rows": len(trace), "request_search_keys": len(keys),
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V137.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    "checkpoint": "V137", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical copies SHA-valid; SAF355 and AMIDDF accession schema proved; SIDIF document type and both execution branches open; zero of ten executed settlement rows confirmed; six requests drafted and none submitted.",
    "historical_workstream": "Target AMIDDF box/type/body, distribution report, automatic debit or BCRA note, bank reconciliation, CRYL and executed settlement remain open; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V137 BUILD PASS")
