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
PARENT = HERE.parent / "V135"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v136" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


SOURCES = [
    {
        "id": "e0_agan_current_archive_services",
        "filename": "argentina_agan_archivo_general_actual.html",
        "institution": "Contaduría General de la Nación · Archivo General de Administración Nacional",
        "title": "Archivo General de Administración Nacional · alcance, fondos y servicios",
        "url": "https://www.argentina.gob.ar/economia/sechacienda/cgn/archivogeneral",
        "publication": "consulta 2026-08-30",
        "period": "actual; fondos históricos",
        "code": "AGAN; documentación respaldatoria; SAF; investigadores",
        "type": "HTML oficial · captura preservada",
        "bytes": 34804,
        "sha256": "f2077fcaf5b8aa354ff64871e8a14cad8af069053d6562de1975e60328df6c51",
        "families": "AGAN;financial_supporting_documents;SAF;archive;digitization;researcher_service",
        "breaks": "competencia y servicio general versus tenencia de los tres C-41 objetivo",
        "use": "USABLE_DIRECT_FINANCIAL_ARCHIVE_ROUTE",
        "caveat": "Prueba la ruta archivística competente, no que los legajos 71597, 152677 y 2876 hayan sido localizados.",
        "note": "V136 E0: AGAN preserva documentación respaldatoria financiera ejecutada por los SAF y presta servicio de consulta sobre fondos históricos.",
    },
    {
        "id": "e0_amiddf_financial_document_images",
        "filename": "argentina_amiddf_imagenes_documentacion_financiera.html",
        "institution": "Contaduría General de la Nación",
        "title": "AMIDDF · Archivo de Movimiento de Imágenes Digitales de Documentación Financiera",
        "url": "https://www.argentina.gob.ar/economia/administracionfinancieragubernamental/otrossistemas/amiddf",
        "publication": "consulta 2026-08-30",
        "period": "actual; documentación histórica",
        "code": "AMIDDF; originales en papel; expedientes; imágenes; SIDIF",
        "type": "HTML oficial · captura preservada",
        "bytes": 43313,
        "sha256": "2a82c85ded72c4a008463646d205d8e702227390d46c9b768c186c5ca804a692",
        "families": "AMIDDF;paper_originals;fund_movements;expediente_bodies;images;document_index",
        "breaks": "capacidad de imagen e indexación versus existencia de imágenes target",
        "use": "USABLE_DIRECT_DIGITAL_FINANCIAL_DOCUMENT_ROUTE",
        "caveat": "La base puede vincular imágenes y registros, pero la consulta target todavía no fue ejecutada.",
        "note": "V136 E0: AMIDDF recibe, custodia, describe y digitaliza originales en papel de movimientos de fondos y permite recorrer cuerpos de expediente.",
    },
    {
        "id": "e0_cgn_circular_07_2008_transaf_entes_transition",
        "filename": "cgn_circular_07_2008_transaf_entes.html",
        "institution": "Contaduría General de la Nación",
        "title": "Circular CGN 07/2008 · reemplazo del módulo Entes SIDIF Central por e-SIDIF",
        "url": "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/2008/cir07.htm",
        "publication": "2008-10-17",
        "period": "2008",
        "code": "Circular 07/08; Entes; SIDIF Central; e-SIDIF; TRANSAF",
        "type": "HTML oficial · captura preservada",
        "bytes": 17653,
        "sha256": "abc3bacbef9b4d86adebc41256c7513fce69a841f6aa35228c27e44621c2f108",
        "families": "SIDIF_Central;eSIDIF;Entes;TRANSAF;file_designs;error_files",
        "breaks": "reemplazo del módulo Entes versus despliegue del módulo Gastos/pagos",
        "use": "USABLE_EXACT_2008_TRANSITION_CONTROL",
        "caveat": "Sólo prueba el cambio del módulo Entes y la continuidad de diseños TRANSAF allí; no continuidad literal de SDPGB/SDPAG.",
        "note": "V136 E0: el 20/10/2008 sólo Entes fue sustituido; los diseños de archivos propios vía TRANSAF permanecían sin cambios.",
    },
    {
        "id": "e0_cgn_account_2008_esidif_module_scope",
        "filename": "cgn_cuenta_2008_jur50_esidif_modules.html",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2008 · alcance de implantación e-SIDIF",
        "url": "https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/tomoii/11jur50.htm",
        "publication": "2009",
        "period": "2008",
        "code": "Jurisdicción 50; e-SIDIF; módulos implantados; TGN",
        "type": "HTML oficial · captura preservada",
        "bytes": 569635,
        "sha256": "ce9f5e48de18c4aff2664afc368e71fea2f200507f93c03666dd4cd7b6eca3ac",
        "families": "eSIDIF;deployment;budget;payments_scenarios;judicial_measures;TGN_files",
        "breaks": "módulos e-SIDIF implantados versus módulos todavía no desplegados",
        "use": "USABLE_2008_ESIDIF_DEPLOYMENT_SCOPE",
        "caveat": "La omisión de Gastos en la lista de implantación se interpreta junto con despliegues explícitos 2009-2011.",
        "note": "V136 E0: en 2008 e-SIDIF cubría formulación y funciones rectoras listadas, no el módulo Gastos; TGN operaba sus módulos y archivos.",
    },
    {
        "id": "e0_cgn_account_2009_esidif_payments_development",
        "filename": "cgn_cuenta_2009_aspectos_esidif_pagos.html",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2009 · etapas de pagos y desarrollo de Gastos e-SIDIF",
        "url": "https://www.economia.gob.ar/hacienda/cgn/cuenta/2009/tomoi/03aspectos.htm",
        "publication": "2010",
        "period": "2009",
        "code": "e-SIDIF; Pagos Etapa 1; Pagos Etapa 2; Gastos; CRYL",
        "type": "HTML oficial · captura preservada",
        "bytes": 55544,
        "sha256": "2318e0f7dfb633f568b6f8dc589b03665846aec8e07caab2079783465ff4f5a0",
        "families": "eSIDIF;payments;spending;accounting;withholdings;CRYL_movements;archive_digitization",
        "breaks": "despliegue rector 2009 versus operación SAF y target 2008",
        "use": "USABLE_POST_TARGET_DEPLOYMENT_AND_CRYL_CONTROL",
        "caveat": "Es un control temporal posterior; no se aplica retroactivamente a las órdenes 2008.",
        "note": "V136 E0: Pagos Etapa 1/Gastos aparece en mayo de 2009 y Etapa 2 en octubre/noviembre; CRYL se incorpora expresamente a recepción de movimientos en 2009.",
    },
    {
        "id": "e0_cgn_account_2010_esidif_spending_rollout",
        "filename": "cgn_cuenta_2010_aspectos_esidif_gastos.html",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2010 · despliegue del módulo Gastos e-SIDIF",
        "url": "https://www.economia.gob.ar/hacienda/cgn/cuenta/2010/tomoi/03aspectos.htm",
        "publication": "2011",
        "period": "2010",
        "code": "e-SIDIF; Gastos; C-41; C-42; ROP; SAF 355; SAF 356",
        "type": "HTML oficial · captura preservada",
        "bytes": 58482,
        "sha256": "d0959a23bf1fd016f5ed38d07403201826b634613e55e4910680ab7c06848fc1",
        "families": "eSIDIF;Gastos;C41;C42;ROP;SAF355;SAF356;rollout",
        "breaks": "implantación 2010 versus sistema productor 2008",
        "use": "USABLE_EXACT_ESIDIF_SPENDING_ROLLOUT_CHRONOLOGY",
        "caveat": "Prueba cuándo aparece la carga/recepción e-SIDIF; no identifica la salida legacy por nombre.",
        "note": "V136 E0: C-41/C-42 manual aparece en mayo de 2010, recepción física ROP en julio y administración local SAF 355 en septiembre.",
    },
    {
        "id": "e0_cgn_account_2011_esidif_saf356_first_spending",
        "filename": "cgn_cuenta_2011_jur50_esidif_gastos_saf356.html",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2011 · primer Gastos e-SIDIF en SAF 356 y pago virtual",
        "url": "https://www.economia.gob.ar/hacienda/cgn/cuenta/2011/tomoii/jur50.htm",
        "publication": "2012",
        "period": "2011",
        "code": "e-SIDIF; SAF 356; Gastos; orden de pago virtual; 50% SAF",
        "type": "HTML oficial · captura preservada",
        "bytes": 198342,
        "sha256": "0e56b77da1c227d45e5850ff75efe65e08d5a030dcd6b3f1d4ae9c8fc9610754",
        "families": "eSIDIF;virtual_payment_order;SAF356;Gastos;deployment",
        "breaks": "primer despliegue documentado 2011 versus procesamiento legacy 2008",
        "use": "USABLE_LATE_DEPLOYMENT_CONFIRMATION",
        "caveat": "Confirma la transición tardía, no continuidad de todos los nombres de archivo legacy.",
        "note": "V136 E0: en 2011 comienza el modelo virtual y se informa la primera versión de Gastos en SAF 356; sólo 50% de SAF usaba el nuevo sistema de pagos.",
    },
    {
        "id": "e0_cgn_disposition_20_2007_agan_quality",
        "filename": "cgn_disposicion_20_2007_agan_archivo_financiero.html",
        "institution": "Contaduría General de la Nación",
        "title": "Disposición CGN 20/2007 · AGAN, accesibilidad y servicio documental",
        "url": "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/2007/Disp20.htm",
        "publication": "2007-08-13",
        "period": "2007",
        "code": "Disposición 20/2007; AGAN; accesibilidad; confidencialidad",
        "type": "HTML oficial · captura preservada",
        "bytes": 15590,
        "sha256": "fa157d8fe62b982b6d6e3df0a485462fe53e574f79fbfde577223d79c1a0d300",
        "families": "AGAN;archive_competence;accessibility;delivery;confidentiality;quality",
        "breaks": "política general de acceso versus admisibilidad y disponibilidad target",
        "use": "USABLE_CONTEMPORANEOUS_AGAN_AUTHORITY",
        "caveat": "La política de acceso no garantiza que cada pieza target esté conservada o sea de libre entrega.",
        "note": "V136 E0: CGN afirma su competencia sobre AGAN y exige acceso oportuno, preciso, confiable y documentado.",
    },
    {
        "id": "e0_cgn_disposition_54_2008_order_expiry_partial",
        "filename": "cgn_disposicion_54_2008_caducidad_ordenes.html",
        "institution": "Contaduría General de la Nación",
        "title": "Disposición CGN 54/2008 · caducidad y pagos parciales de órdenes",
        "url": "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/2008/disp54/disp54.htm",
        "publication": "2008-12-12",
        "period": "2008",
        "code": "Disposición 54/2008; SIDIF; caducidad; pago parcial",
        "type": "HTML oficial · captura preservada",
        "bytes": 37565,
        "sha256": "cd3fb95b812bca412c07cfe9de72bbb29bca7f0c1ed2c35c6ff8adec2450497f",
        "families": "payment_order;SIDIF;conformity;expiry;partial_payment;closing",
        "breaks": "estado final P/R/A versus historia de pagos parciales y saldo",
        "use": "USABLE_EXACT_2008_PARTIAL_PAYMENT_STATE_RULE",
        "caveat": "No prueba que las tres órdenes target hayan sido pagadas parcial ni totalmente.",
        "note": "V136 E0: la orden conformada caduca al cierre del ejercicio siguiente, con excepción cuando el SAF realizó pagos parciales antes de caducar.",
    },
    {
        "id": "e0_cgn_tgn_joint_disposition_13_16_2009_payment_records",
        "filename": "cgn_tgn_disposicion_13_16_2009_ordenes_pago.html",
        "institution": "Contaduría General de la Nación / Tesorería General de la Nación",
        "title": "Disposición Conjunta CGN 13/2009 y TGN 16/2009 · presentación y selección de órdenes de pago",
        "url": "https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/2009/disp13.htm",
        "publication": "2009-06-26",
        "period": "2009; procedimiento inmediato posterior a 2008",
        "code": "Disposición Conjunta 13/2009 y 16/2009; C-41; lista diaria; CUT",
        "type": "HTML oficial · captura preservada",
        "bytes": 13664,
        "sha256": "42292773a13c2e42cfd4aa6c8652d47a8c95137429192fc65a52f4a56b9b4237",
        "families": "C41;paper_copy;daily_selection_list;payment_authorization;beneficiary;bank_account;signatures",
        "breaks": "procedimiento 2009 sucesor/comparador versus aplicabilidad directa en 2008",
        "use": "USABLE_CONTEMPORANEOUS_PAYMENT_PACKET_COMPARATOR",
        "caveat": "No debe retroproyectarse automáticamente; identifica clases documentales y campos a solicitar.",
        "note": "V136 E0: exige copia papel C-41, listas diarias firmadas y autorizaciones con beneficiario, CUIT, banco/cuenta e importe, según clase de organismo.",
    },
    {
        "id": "e0_agan_current_coordination_contact",
        "filename": "economia_agan_competencia_contacto.html",
        "institution": "Contaduría General de la Nación · Coordinación Archivo General",
        "title": "Coordinación Archivo General · competencia y contacto publicado",
        "url": "https://www.economia.gob.ar/hacienda/cgn/competencia/archivo.htm",
        "publication": "s/f; captura 2026-08-30",
        "period": "página institucional publicada",
        "code": "Coordinación Archivo General; mherri@mecon.gov.ar; 54-11-4349-7824",
        "type": "HTML oficial · captura preservada",
        "bytes": 3454,
        "sha256": "01986c35b5439694cff2e793fa658141c47f0484a0154dc43aedd2afa366669d",
        "families": "AGAN;custody;integrity;control;email;telephone",
        "breaks": "contacto oficial publicado versus vigencia y uso efectivo",
        "use": "USABLE_PUBLISHED_CONTACT_NOT_CONTACTED",
        "caveat": "La página puede ser legada; la vigencia del contacto no fue probada y no se lo utilizó.",
        "note": "V136 E0: la coordinación recibe, custodia, ordena y facilita documentación para control; contacto publicado, no contactado.",
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


def bump(text: str) -> str:
    return text.replace("V135", "V136").replace("v135", "v136")


def clone_parent() -> None:
    skip = {"build_e0_payment_state_v135.py", "qa_v135.py", "MANIFEST_V135.json", "INHERITED_QA_STATUS_V135.csv"}
    for source in PARENT.iterdir():
        if not source.is_file() or source.name in skip or source.name.startswith("HANDOVER_PROXIMA_SESION"):
            continue
        target = HERE / source.name.replace("V135", "V136")
        target.write_text(bump(source.read_text(encoding="utf-8-sig")), encoding="utf-8")


clone_parent()

for source in SOURCES:
    path = BIN / source["filename"]
    assert path.is_file() and path.stat().st_size == source["bytes"], path
    assert sha256(path) == source["sha256"], path
    source["local"] = "/" + path.relative_to(REPO).as_posix()

source_ids = {source["id"] for source in SOURCES}

# Catálogo maestro, censo E0 y proveniencia.
catalog = [row for row in read_csv(CATALOG) if row["id"] not in source_ids]
for source in SOURCES:
    catalog.append({
        "id": source["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": source["institution"],
        "titulo": source["title"], "url_original": source["url"], "archivo_local": source["local"],
        "fecha_descarga": "2026-08-30", "fecha_publicacion": source["publication"],
        "codigo_serie": source["code"], "periodo_utilizado": source["period"], "tipo": source["type"],
        "sha256": source["sha256"], "nota": source["note"],
    })
assert len(catalog) == 388 and len({row["id"] for row in catalog}) == 388
write_csv(CATALOG, catalog)

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V136.csv"
census = [row for row in read_csv(census_path) if row["source_id"] not in source_ids]
for source in SOURCES:
    census.append({
        "source_id": source["id"], "institution": source["institution"], "artifact": source["title"],
        "url": source["url"], "local_path": source["local"], "sha256": source["sha256"],
        "bytes": str(source["bytes"]), "period_coverage": source["period"],
        "variable_families": source["families"], "primary_source": "YES", "preserved": "YES",
        "method_breaks": source["breaks"], "use_status": source["use"], "caveat": source["caveat"],
    })
assert len(census) == 148 and len({row["source_id"] for row in census}) == 148
write_csv(census_path, census)

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V136.csv"
provenance = [row for row in read_csv(provenance_path) if row["source_id"] not in source_ids]
for source in SOURCES:
    provenance.append({
        "source_id": source["id"], "original_url": source["url"], "retrieval_url": source["url"],
        "capture_timestamp": "20260830", "cdx_digest": "N/A_DIRECT_OFFICIAL", "local_path": source["local"],
        "sha256": source["sha256"], "bytes": str(source["bytes"]),
        "provenance_note": "Captura HTML oficial directa preservada y hasheada en V136.",
    })
assert len(provenance) == 51
write_csv(provenance_path, provenance)

# FindDoc/COMDOC: capacidad, salida y control histórico separados del target.
finddoc = [
    {"row_id": "FD134_01", "evidence_type": "DESIGN_SPEC", "target": "Consulta pública FindDoc", "date": "2011", "output_schema": "número o patrón; hoja de ruta; ubicación", "result": "El ciudadano podía conocer ruta y ubicación.", "source_id": "e0_agenda_digital_finddoc_comdoc_architecture", "status": "CAPABILITY_PROVED", "permitted_inference": "FindDoc era el índice público competente para metadatos de ruta.", "forbidden_inference": "FindDoc publicaba el cuerpo completo."},
    {"row_id": "FD134_02", "evidence_type": "DESIGN_SPEC", "target": "Hoja de ruta", "date": "2011", "output_schema": "origen; destino; fecha de envío; fecha de recepción", "result": "Campos explícitos y movimientos desde ingreso en COMDOC.", "source_id": "e0_agenda_digital_finddoc_comdoc_architecture", "status": "OUTPUT_FIELDS_PROVED", "permitted_inference": "Una salida target permitiría reconstruir custodia temporal.", "forbidden_inference": "Los movimientos prueban contenido o pago."},
    {"row_id": "FD134_03", "evidence_type": "ARCHITECTURE", "target": "COMDOC3→FindDoc→Internet", "date": "2011", "output_schema": "COMDOC3/PostgreSQL; importador; FindDoc/MySQL en DMZ; usuario Internet", "result": "Separación técnica entre sistema interno e índice público.", "source_id": "e0_agenda_digital_finddoc_comdoc_architecture", "status": "ARCHITECTURE_PROVED", "permitted_inference": "La caída de FindDoc no implica pérdida de la base COMDOC interna.", "forbidden_inference": "La base interna continúa disponible sin verificación administrativa."},
    {"row_id": "FD134_04", "evidence_type": "HISTORIC_QUERY_CONTROL", "target": "S01:0130656/2008", "date": "2013-03-05", "output_schema": "estado; fecha del último pase; ubicación", "result": "En trámite; desde 11/06/2012 en Gabinete de la Subsecretaría de Obras Públicas.", "source_id": "e0_agn_informe_254_2013_finddoc_control", "status": "HISTORIC_QUERY_OPERATIONAL_CONTROL", "permitted_inference": "El endpoint entregaba datos útiles para un S01 de 2008 en 2013.", "forbidden_inference": "El expediente objetivo tuvo igual ruta o estado."},
    {"row_id": "FD134_05", "evidence_type": "TARGET_STATUS", "target": "S01:0342455/2008", "date": "2026-08-30", "output_schema": "origen; destino; fechas; ubicación esperables", "result": "Endpoint legado no operativo; consulta target no ejecutada.", "source_id": "e0_economia_consulta_expedientes_comdoc_gde;e0_agenda_digital_finddoc_comdoc_architecture;e0_agn_informe_254_2013_finddoc_control", "status": "TARGET_QUERY_UNEXECUTED_ADMINISTRATIVE_EXPORT_REQUIRED", "permitted_inference": "Pedir exportación o consulta administrativa exacta de la hoja de ruta.", "forbidden_inference": "Sin resultado o expediente inexistente."},
]
write_csv(HERE / "E0_COMDOC_FINDDOC_CAPABILITY_V136.csv", finddoc)

comdoc_path = HERE / "E0_COMDOC_LEGACY_QUERY_ROUTE_V136.csv"
comdoc = read_csv(comdoc_path)[:2]
comdoc.extend([
    {"row_id": "CD134_03", "target": "FindDoc public output", "official_rule": "La consulta pública mostraba hoja de ruta y ubicación con origen, destino y fechas", "published_endpoint": "http://expedientes.mecon.gov.ar/finddoc2/finddoc/VerExpediente", "test_date": "2011 design specification", "test_result": "OUTPUT_SCHEMA_PROVED", "body_query_executed": "NOT_APPLICABLE", "source_id": "e0_agenda_digital_finddoc_comdoc_architecture", "status": "ROUTE_METADATA_NOT_BODY", "permitted_inference": "La salida esperable es trazabilidad de pases.", "forbidden_inference": "La consulta reemplaza una copia del cuerpo."},
    {"row_id": "CD134_04", "target": "S01:0130656/2008", "official_rule": "AGN usó VerExpediente para consultar un S01/2008", "published_endpoint": "http://expedientes.mecon.gov.ar/finddoc2/finddoc/VerExpediente", "test_date": "2013-03-05", "test_result": "HISTORIC_QUERY_RETURNED_STATUS_AND_LOCATION", "body_query_executed": "CONTROL_ONLY", "source_id": "e0_agn_informe_254_2013_finddoc_control", "status": "HISTORIC_OPERATIONAL_CONTROL", "permitted_inference": "El servicio era operativo y útil en 2013.", "forbidden_inference": "El control responde por S01:0342455/2008."},
    {"row_id": "CD134_05", "target": "S01:0342455/2008", "official_rule": "Consulta sustitutiva por Dirección de Información Ciudadana/administradores COMDOC", "published_endpoint": "ciudadano@mecon.gov.ar; 0810-333-6326; Balcarce 186 piso 1 oficina 140", "test_date": "2026-08-30", "test_result": "CHANNEL_IDENTIFIED_NOT_CONTACTED", "body_query_executed": "NO", "source_id": "e0_economia_consulta_expedientes_comdoc_gde", "status": "ADMINISTRATIVE_ROUTE_READY_DRAFT_NOT_SENT", "permitted_inference": "Existe vía oficial alternativa para pedir la consulta.", "forbidden_inference": "El pedido fue presentado o contestado."},
])
write_csv(comdoc_path, comdoc)

# La C-41 es una orden; el pago requiere procesamiento y trazas posteriores.
c41_chain = [
    {"stage_id": "CP134_01", "stage": "C41_ISSUED", "record": "Formulario C-41 Orden de Pago", "required_or_visible_fields": "vencimiento contractual original; devengado; beneficiario/observaciones según operatoria", "execution_meaning": "Orden emitida", "source_id": "e0_cgn_circular_2_1997_c41_due_date", "target_status": "THREE_2008_IDS_VISIBLE_ONLY_AS_ANEXO_K_REFERENCES", "permitted_inference": "Los SIDIF 71597, 152677 y 2876 son localizadores de órdenes.", "forbidden_inference": "La orden fue pagada."},
    {"stage_id": "CP134_02", "stage": "C41_PROCESSING", "record": "C-41 presentada/procesada por CGN", "required_or_visible_fields": "crédito; cuota; conformidad", "execution_meaning": "Puede ser rechazada por insuficiencia", "source_id": "e0_cgn_circular_6_1995_c41_tgn", "target_status": "TARGET_BODIES_NOT_PUBLICLY_LOCATED", "permitted_inference": "Hace falta estado de procesamiento por número SIDIF.", "forbidden_inference": "La mera numeración prueba conformidad."},
    {"stage_id": "CP134_03", "stage": "TGN_PREPAYMENT", "record": "C-41 conformada remitida a TGN", "required_or_visible_fields": "formulario conformado; remisión", "execution_meaning": "Se envía 'a efectos de su pago'", "source_id": "e0_cgn_circular_6_1995_c41_tgn", "target_status": "OPEN", "permitted_inference": "Conformidad y pago son etapas separables.", "forbidden_inference": "Remisión a TGN equivale a débito o crédito."},
    {"stage_id": "CP134_04", "stage": "EXTERNAL_PAYMENT_INSTRUCTION", "record": "C-41 más nota a TGN", "required_or_visible_fields": "beneficiario; banco destino; cuenta; SIDIF; moneda; tipo de cambio; divisas; un beneficiario por orden", "execution_meaning": "Instrucción suficientemente individualizada", "source_id": "e0_cgn_circular_13_2002_external_payments_c41", "target_status": "APPLICABILITY_TO_TARGET_NOT_PROVED", "permitted_inference": "Pedir nota e instrucción asociadas si la operatoria fue exterior.", "forbidden_inference": "Las órdenes target fueron pagos al exterior."},
    {"stage_id": "CP134_05", "stage": "BANK_DEBIT", "record": "Débito bancario", "required_or_visible_fields": "banco; cuenta; importe; fecha; documento original", "execution_meaning": "Movimiento monetario posterior a la orden", "source_id": "e0_cgn_circular_22_2004_c55_bank_debit", "target_status": "NO_TARGET_DEBIT_LOCATED", "permitted_inference": "El débito es una evidencia distinta que debe pedirse.", "forbidden_inference": "Devengado C-41 y débito son siempre iguales."},
    {"stage_id": "CP134_06", "stage": "C55_REGULARIZATION", "record": "Formulario C-55 Regularización", "required_or_visible_fields": "débito BNA superior al devengado; banco/cuenta; documento original", "execution_meaning": "Reconcilia diferencia positiva", "source_id": "e0_cgn_circular_22_2004_c55_bank_debit", "target_status": "TARGET_SEARCH_NOT_EXECUTED", "permitted_inference": "Buscar C-55 vinculado a cada C-41.", "forbidden_inference": "Todo pago genera C-55."},
    {"stage_id": "CP134_07", "stage": "C55_DEACTIVATION", "record": "Formulario C-55 Desafectación", "required_or_visible_fields": "débito BNA inferior al devengado; banco/cuenta; documento original", "execution_meaning": "Reconcilia diferencia negativa", "source_id": "e0_cgn_circular_22_2004_c55_bank_debit", "target_status": "TARGET_SEARCH_NOT_EXECUTED", "permitted_inference": "Pedir desafectación/reversa si existe diferencia.", "forbidden_inference": "Ausencia web de C-55 prueba identidad de montos."},
    {"stage_id": "CP134_08", "stage": "TARGET_CLOSE", "record": "C-41 + estado + pago/débito + C-55 si aplica", "required_or_visible_fields": "71597;152677;2876; beneficiario; concepto; importe; moneda; fechas; estado; vínculo bancario", "execution_meaning": "Cadena mínima para atribución", "source_id": "e0_cgn_cuenta_inversion_2008_sdp;e0_cgn_circular_2_1997_c41_due_date;e0_cgn_circular_6_1995_c41_tgn;e0_cgn_circular_22_2004_c55_bank_debit", "target_status": "OPEN", "permitted_inference": "Los tres números reducen el universo de búsqueda.", "forbidden_inference": "Los tres números pertenecen a la recompra o prueban pago."},
    {"stage_id": "CP135_09", "stage": "SIDIF_DAILY_STATE_OUTPUT", "record": "SDPGB por beneficiario y SDPAG por ítem, o sucesor equivalente", "required_or_visible_fields": "OB SIDIF; SAF; beneficiario; importe; estado P/R/A; fecha; banco; cuenta; medio RN/CH/TR/TI/NS", "execution_meaning": "Distingue pagado, rechazado y anulado", "source_id": "e0_tgn_circular_7_1997_daily_paid_files;e0_cgn_circular_34_1997_sdpgb_paid_beneficiary_schema", "target_status": "SCHEMA_PROVED_TARGET_ROWS_NOT_LOCATED", "permitted_inference": "Pedir extracto exacto por 71597, 152677 y 2876 en SDPGB/SDPAG o sucesor.", "forbidden_inference": "La existencia del esquema prueba que las tres órdenes fueron pagadas."},
    {"stage_id": "CP135_10", "stage": "TGN_TO_BCRA_INSTRUCTION_FILE", "record": "Archivo de instrucciones de pago enviado por enlace", "required_or_visible_fields": "identificador de archivo; fecha/hora; orden; importe; moneda; destino; acuse", "execution_meaning": "Instrucción electrónica posterior a la orden", "source_id": "e0_cgn_cuenta_inversion_2008_tomo_ii_tgn_system_files", "target_status": "2008_RECORD_CLASS_PROVED_TARGET_FILE_OPEN", "permitted_inference": "Pedir el archivo o registro equivalente asociado a cada orden.", "forbidden_inference": "La capacidad del enlace prueba envío target."},
    {"stage_id": "CP135_11", "stage": "BCRA_MOVEMENT_AND_BALANCE_RETURN", "record": "Archivos de movimientos y saldos bancarios recibidos", "required_or_visible_fields": "cuenta; fecha valor; débito/crédito; importe; moneda; referencia; saldo", "execution_meaning": "Huella bancaria separada de la instrucción", "source_id": "e0_cgn_cuenta_inversion_2008_tomo_ii_tgn_system_files", "target_status": "2008_RECORD_CLASS_PROVED_TARGET_MOVEMENT_OPEN", "permitted_inference": "Exigir movimiento y saldo que permitan conciliar el eventual pago.", "forbidden_inference": "Todo archivo de movimiento corresponde a la recompra."},
    {"stage_id": "CP135_12", "stage": "TARGET_PAYMENT_STATE_CLOSE", "record": "C-41 + SDPGB/SDPAG + instrucción + movimiento + ajuste", "required_or_visible_fields": "71597;152677;2876; P/R/A; fecha; beneficiario; banco/cuenta; medio; instrucción; movimiento; C-55 si aplica", "execution_meaning": "Cadena mínima reforzada para pago efectivo", "source_id": "e0_cgn_cuenta_inversion_2008_sdp;e0_tgn_circular_7_1997_daily_paid_files;e0_cgn_circular_34_1997_sdpgb_paid_beneficiary_schema;e0_cgn_cuenta_inversion_2008_tomo_ii_tgn_system_files", "target_status": "OPEN", "permitted_inference": "Ahora se conocen los campos y clases documentales exactos a solicitar.", "forbidden_inference": "Esquema y capacidad equivalen a resultado target."},
    {"stage_id": "CP136_13", "stage": "LEGACY_SIDIF_ENVIRONMENT", "record": "SIDIF Central/TRANSAF y salidas legacy o sucesoras", "required_or_visible_fields": "sistema productor; módulo; nombre de archivo; fecha; SAF; OB", "execution_meaning": "Identifica el entorno que procesó la orden", "source_id": "e0_cgn_circular_07_2008_transaf_entes_transition;e0_cgn_account_2008_esidif_module_scope;e0_cgn_account_2009_esidif_payments_development;e0_cgn_account_2010_esidif_spending_rollout;e0_cgn_account_2011_esidif_saf356_first_spending", "target_status": "2008_LEGACY_SIDIF_CENTRAL_ENVIRONMENT_PROVED_FILENAME_CONTINUITY_OPEN", "permitted_inference": "Buscar primero en SIDIF Central/TRANSAF y aceptar el sucesor funcional de SDPGB/SDPAG.", "forbidden_inference": "Afirmar que e-SIDIF Gastos procesó las tres órdenes en 2008 o que el nombre de archivo no cambió."},
    {"stage_id": "CP136_14", "stage": "C41_PAPER_AND_DAILY_LIST", "record": "Copia papel C-41 y lista diaria firmada de selección", "required_or_visible_fields": "fecha; SAF; número de orden; beneficiario; importe; firma responsable", "execution_meaning": "Paquete documental de presentación/selección", "source_id": "e0_cgn_tgn_joint_disposition_13_16_2009_payment_records", "target_status": "2009_SUCCESSOR_RECORD_CLASS_TARGET_2008_APPLICABILITY_OPEN", "permitted_inference": "Pedir esas clases o sus equivalentes contemporáneos en AGAN.", "forbidden_inference": "Aplicar automáticamente a 2008 la disposición de 2009."},
    {"stage_id": "CP136_15", "stage": "PARTIAL_PAYMENT_HISTORY", "record": "Pagos parciales previos a caducidad", "required_or_visible_fields": "importe original; cada pago; fecha; saldo; caducidad; anulación", "execution_meaning": "Distingue pago total, parcial y saldo impago", "source_id": "e0_cgn_disposition_54_2008_order_expiry_partial", "target_status": "EXACT_2008_STATE_RULE_TARGET_HISTORY_OPEN", "permitted_inference": "Exigir serie de movimientos e importe acumulado por OB.", "forbidden_inference": "Un código P aislado prueba cancelación total."},
    {"stage_id": "CP136_16", "stage": "AGAN_AMIDDF_RETRIEVAL", "record": "Originales, imágenes e índice documental financiero", "required_or_visible_fields": "signatura; caja; cuerpo; folios; tipo documental; fecha; SAF; número SIDIF; imagen", "execution_meaning": "Ruta directa al respaldo material", "source_id": "e0_agan_current_archive_services;e0_amiddf_financial_document_images;e0_cgn_disposition_20_2007_agan_quality", "target_status": "DIRECT_CUSTODIAN_ROUTE_PROVED_TARGET_HOLDINGS_NOT_QUERIED", "permitted_inference": "Solicitar búsqueda por los tres SIDIF, cuenta, importe y SAF.", "forbidden_inference": "La competencia general del archivo prueba que conserva esas piezas concretas."},
    {"stage_id": "CP136_17", "stage": "TARGET_EXECUTION_CLOSE", "record": "C-41 + lista + estado + pagos parciales + instrucción + movimiento + respaldo AGAN", "required_or_visible_fields": "71597;152677;2876;importe original;pagos acumulados;saldo;fecha;beneficiario;banco/cuenta;signatura", "execution_meaning": "Cadena suficiente para pago total/parcial o no pago", "source_id": "e0_cgn_disposition_54_2008_order_expiry_partial;e0_cgn_tgn_joint_disposition_13_16_2009_payment_records;e0_agan_current_archive_services;e0_amiddf_financial_document_images", "target_status": "OPEN", "permitted_inference": "La próxima acción útil es archivística y registral, no otra inferencia desde la referencia contable.", "forbidden_inference": "Confundir orden, selección, pago parcial o custodia con ejecución total."},
]
write_csv(HERE / "E0_C41_PAYMENT_EXECUTION_CHAIN_V136.csv", c41_chain)

# Archivo parlamentario: el contexto masivo no sustituye el localizador exacto.
bicameral = [
    {"row_id": "BI134_01", "object": "OV 366/09", "route_checked": "Senado expediente exacto", "result": "Bicameral Revisora; archivo 28/05/2012 por nota 18/05/2012; texto original en carga", "status": "EXACT_METADATA_BODY_OPEN", "source_id": "e0_senado_exp_366_09_agn_res211_t3", "next_locator": "nota 18/05/2012; remito; inventario; depósito"},
    {"row_id": "BI134_02", "object": "OV 44/10", "route_checked": "Senado expediente exacto", "result": "Bicameral Revisora; archivo 28/05/2012 por nota 18/05/2012; texto original en carga", "status": "EXACT_METADATA_BODY_OPEN", "source_id": "e0_senado_exp_44_10_agn_res44_t4", "next_locator": "nota 18/05/2012; remito; inventario; depósito"},
    {"row_id": "BI134_03", "object": "Documentación pública Bicameral", "route_checked": "Sección Documentación y paginación visible", "result": "Documentos recientes visibles; nota 2012 no expuesta en el inventario revisado", "status": "PUBLIC_UI_NEGATIVE_CONTROL_ONLY", "source_id": "e0_senado_bicameral_revisora_current_documents", "next_locator": "REVISORA@SENADO.GOB.AR; internos 2310-2315"},
    {"row_id": "BI134_04", "object": "Lote de archivo parlamentario", "route_checked": "HCDN reunión 8 del 23/05/2012 punto 13", "result": "Amplio lote de archivos de la Revisora; strings exactas OV 366/09 y OV 44/10 no localizadas", "status": "MASS_ARCHIVE_CONTEXT_NOT_TARGET_PROOF", "source_id": "e0_hcdn_session_summary_2012_05_23_mass_archive", "next_locator": "No usar como disposición de los dos expedientes target"},
    {"row_id": "BI134_05", "object": "Nota Bicameral 18/05/2012", "route_checked": "Senado + documentación actual + sumario HCDN", "result": "Cuerpo e inventario de transferencia no localizados públicamente", "status": "EXACT_NOTE_BODY_OPEN", "source_id": "e0_senado_exp_366_09_agn_res211_t3;e0_senado_exp_44_10_agn_res44_t4;e0_senado_bicameral_revisora_current_documents;e0_hcdn_session_summary_2012_05_23_mass_archive", "next_locator": "Solicitud archivística exacta; borrador no enviado"},
    {"row_id": "BI135_06", "object": "OV 366/09 y OV 44/10", "route_checked": "Índice histórico HCDN de reuniones y versiones taquigráficas; variantes 0366-ov-2009, 366-ov-2009, 0044-ov-2010, 44-ov-2010, 366/09 y 44/10", "result": "Sin coincidencias exactas en el índice público preservado", "status": "PUBLIC_INDEX_NEGATIVE_CONTROL_NOT_ABSENCE", "source_id": "e0_hcdn_historic_plenary_index_negative_control", "next_locator": "Fondo interno de la Bicameral; nota, remito, inventario, caja y signatura"},
    {"row_id": "BI135_07", "object": "Custodia material de los dos OV", "route_checked": "Regla COMDOC contemporánea como comparador", "result": "Campos verificables: dos remitos, cuerpos, anexos, último folio, área depositaria; ante pérdida, búsqueda intensiva y reconstrucción certificada", "status": "CONTEMPORANEOUS_CUSTODY_COMPARATOR_NOT_TARGET_RULE", "source_id": "e0_minplan_resolution_1522_2006_comdoc_custody", "next_locator": "Pedir equivalentes aplicables al fondo Bicameral/Economía sin presumir identidad normativa"},
]
write_csv(HERE / "E0_BICAMERAL_PUBLIC_INVENTORY_AUDIT_V136.csv", bicameral)

# Control visual de una tabla horizontal: el renglón renderizado gobierna sobre el texto linealizado.
anexo_k_alignment = [
    {"row_id": "AK135_01", "rendered_row": "83100000 HONORARIOS - BANK OF NEW YORK", "amount_ars": "227910.00", "sidif_ids": "182705;24306", "visual_status": "VISUAL_TABLE_ROW_ALIGNMENT_EXACT", "linear_search_risk": "Puede desplazar identificadores a la fila siguiente", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "permitted_inference": "Los dos SIDIF pertenecen a Bank of New York.", "forbidden_inference": "Asignarlos a Banco Nación por orden de texto extraído."},
    {"row_id": "AK135_02", "rendered_row": "83106000 COMISIONES - BANCO NACION", "amount_ars": "32270.30", "sidif_ids": "71597;152677;2876", "visual_status": "VISUAL_TABLE_ROW_ALIGNMENT_EXACT", "linear_search_risk": "La linealización puede parecer asociarlos a Letras del Tesoro", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "permitted_inference": "Los tres SIDIF son referencias exactas de comisiones BNA.", "forbidden_inference": "La fila prueba pago o vínculo con recompra."},
    {"row_id": "AK135_03", "rendered_row": "81155000 LETRAS DEL TESORO", "amount_ars": "18530136.99", "sidif_ids": "171761", "visual_status": "VISUAL_TABLE_ROW_ALIGNMENT_EXACT", "linear_search_risk": "La extracción puede heredar los tres IDs de la fila anterior", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "permitted_inference": "El único SIDIF visible de esta fila es 171761.", "forbidden_inference": "71597, 152677 o 2876 pertenecen a Letras."},
    {"row_id": "AK135_04", "rendered_row": "Regla de lectura", "amount_ars": "N/A", "sidif_ids": "N/A", "visual_status": "SEARCH_SNIPPET_LINEARIZATION_FALSE_SHIFT_CONTROLLED", "linear_search_risk": "Alta en tablas horizontales con columnas", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "permitted_inference": "La alineación visual renderizada controla la atribución de fila.", "forbidden_inference": "Usar un snippet lineal como sustituto de la tabla."},
]
write_csv(HERE / "E0_2008_ANEXO_K_VISUAL_ALIGNMENT_CONTROL_V136.csv", anexo_k_alignment)

payment_state_schema = [
    {"row_id": "PS135_01", "record": "SDPGBXXX.CON", "field_or_code": "OB SIDIF; SAF; ejercicio; tipo y número de formulario", "meaning": "Identidad de la orden", "target_query": "71597;152677;2876", "source_id": "e0_cgn_circular_34_1997_sdpgb_paid_beneficiary_schema", "status": "EXACT_HISTORIC_SCHEMA_SUCCESSOR_2008_OPEN"},
    {"row_id": "PS135_02", "record": "SDPGBXXX.CON", "field_or_code": "beneficiario; descripción; deducción; importe", "meaning": "Sujeto y cuantía", "target_query": "beneficiario y monto por cada OB", "source_id": "e0_cgn_circular_34_1997_sdpgb_paid_beneficiary_schema", "status": "EXACT_HISTORIC_SCHEMA_SUCCESSOR_2008_OPEN"},
    {"row_id": "PS135_03", "record": "SDPGBXXX.CON", "field_or_code": "P;R;A", "meaning": "Pagado; rechazado; anulado", "target_query": "estado final por cada OB", "source_id": "e0_cgn_circular_34_1997_sdpgb_paid_beneficiary_schema", "status": "EXACT_STATE_CODES_PROVED_TARGET_VALUE_OPEN"},
    {"row_id": "PS135_04", "record": "SDPGBXXX.CON", "field_or_code": "fecha; banco; sucursal; tipo de cuenta; cuenta bancaria", "meaning": "Fecha y rastro bancario", "target_query": "fecha valor y cuenta por cada OB", "source_id": "e0_cgn_circular_34_1997_sdpgb_paid_beneficiary_schema", "status": "EXACT_HISTORIC_FIELDS_PROVED_TARGET_VALUE_OPEN"},
    {"row_id": "PS135_05", "record": "SDPGBXXX.CON", "field_or_code": "RN;CH;TR;TI;NS", "meaning": "Red bancaria; cheque; transferencia CUT; títulos; nota", "target_query": "medio de pago por cada OB", "source_id": "e0_cgn_circular_34_1997_sdpgb_paid_beneficiary_schema", "status": "EXACT_PAYMENT_MEDIA_CODES_PROVED_TARGET_VALUE_OPEN"},
    {"row_id": "PS135_06", "record": "SDPAG", "field_or_code": "pagado por ítem", "meaning": "Desagregación presupuestaria diaria", "target_query": "cruce por ítem de cada OB", "source_id": "e0_tgn_circular_7_1997_daily_paid_files", "status": "DAILY_OUTPUT_AUTHORITY_PROVED_TARGET_VALUE_OPEN"},
    {"row_id": "PS135_07", "record": "SDPGB", "field_or_code": "pagado por beneficiario", "meaning": "Desagregación diaria por sujeto", "target_query": "cruce por beneficiario de cada OB", "source_id": "e0_tgn_circular_7_1997_daily_paid_files", "status": "DAILY_OUTPUT_AUTHORITY_PROVED_TARGET_VALUE_OPEN"},
    {"row_id": "PS135_08", "record": "TRANSAF/SIDIF", "field_or_code": "procesamiento diario 19:30; pagos, anulaciones y rechazos", "meaning": "Corte operativo diario", "target_query": "archivo de la fecha de cada C-41 o sucesor equivalente", "source_id": "e0_tgn_circular_7_1997_daily_paid_files", "status": "HISTORIC_DAILY_PROCESS_PROVED_2008_CONTINUITY_OPEN"},
]
write_csv(HERE / "E0_SIDIF_PAID_BENEFICIARY_FILE_SCHEMA_V136.csv", payment_state_schema)

tgn_system_records = [
    {"row_id": "TS135_01", "2008_record_class": "Archivo de instrucciones de pago", "direction": "TGN→BCRA", "minimum_target_fields": "fecha/hora; orden; importe; moneda; cuenta/destino; acuse", "source_id": "e0_cgn_cuenta_inversion_2008_tomo_ii_tgn_system_files", "target_status": "CLASS_PROVED_TARGET_RECORD_OPEN"},
    {"row_id": "TS135_02", "2008_record_class": "Archivo de movimientos bancarios", "direction": "BCRA→TGN", "minimum_target_fields": "cuenta; fecha valor; débito/crédito; importe; referencia", "source_id": "e0_cgn_cuenta_inversion_2008_tomo_ii_tgn_system_files", "target_status": "CLASS_PROVED_TARGET_RECORD_OPEN"},
    {"row_id": "TS135_03", "2008_record_class": "Archivo de saldos bancarios", "direction": "BCRA→TGN", "minimum_target_fields": "cuenta; fecha; saldo inicial/final; moneda", "source_id": "e0_cgn_cuenta_inversion_2008_tomo_ii_tgn_system_files", "target_status": "CLASS_PROVED_TARGET_RECORD_OPEN"},
    {"row_id": "TS135_04", "2008_record_class": "Nota a TGN para pago exterior", "direction": "SAF355/356→TGN", "minimum_target_fields": "beneficiario; banco; cuenta; tipo de operación; SIDIF; moneda; cambio; divisas", "source_id": "e0_cgn_tgn_disposicion_conjunta_47_10_2008_external_payments", "target_status": "CONDITIONAL_ON_EXTERNAL_PAYMENT"},
    {"row_id": "TS135_05", "2008_record_class": "Boleto de Venta de Cambio y respaldos", "direction": "BNA↔SAF/TGN", "minimum_target_fields": "fecha; moneda; cotización; importe; firmas/poderes", "source_id": "e0_cgn_tgn_disposicion_conjunta_47_10_2008_external_payments", "target_status": "CONDITIONAL_ON_BNA_EXTERNAL_PAYMENT"},
    {"row_id": "TS135_06", "2008_record_class": "Nota conjunta ONCP/TGN + archivo/aceptación SIGADE/Caja", "direction": "ONCP/TGN→agente de registro/pago", "minimum_target_fields": "instrucción; archivo; validación; aceptación; registro", "source_id": "e0_debt_joint_resolution_216_26_2008_instruction_chain", "target_status": "COMPARATOR_OTHER_DEBT_PROCEDURE_NOT_TARGET_EQUIVALENCE"},
]
write_csv(HERE / "E0_TGN_BCRA_2008_PAYMENT_RECORD_CLASSES_V136.csv", tgn_system_records)

sidif_timeline = [
    {"row_id": "ST136_01", "date_or_period": "2008", "level": "SAF", "documented_deployment": "Formulación presupuestaria en 81 SAF", "gastos_payment_status": "NOT_LISTED_AS_DEPLOYED", "source_id": "e0_cgn_account_2008_esidif_module_scope", "inference_status": "2008_ESIDIF_GASTOS_NOT_OPERATIONAL_IN_DOCUMENTED_SCOPE"},
    {"row_id": "ST136_02", "date_or_period": "2008", "level": "órganos rectores", "documented_deployment": "Modificaciones, programación, Entes, escenarios de pago y medidas judiciales", "gastos_payment_status": "GASTOS_NOT_LISTED", "source_id": "e0_cgn_account_2008_esidif_module_scope", "inference_status": "LEGACY_SIDIF_CENTRAL_PAYMENT_ENVIRONMENT_STRONGLY_SUPPORTED"},
    {"row_id": "ST136_03", "date_or_period": "20/10/2008", "level": "SIDIF Central", "documented_deployment": "Sólo módulo Entes sustituido por e-SIDIF", "gastos_payment_status": "UNCHANGED_BY_THIS_CIRCULAR", "source_id": "e0_cgn_circular_07_2008_transaf_entes_transition", "inference_status": "EXACT_MODULE_TRANSITION_CONTROL"},
    {"row_id": "ST136_04", "date_or_period": "20/10/2008", "level": "SAF con sistema propio", "documented_deployment": "Diseños de archivo enviados vía TRANSAF sin cambios para Entes", "gastos_payment_status": "NO_LITERAL_SDPGB_SDPAG_PROOF", "source_id": "e0_cgn_circular_07_2008_transaf_entes_transition", "inference_status": "TRANSAF_CONTINUITY_EXACT_ENTES_ONLY"},
    {"row_id": "ST136_05", "date_or_period": "05/2009", "level": "órganos rectores", "documented_deployment": "Pagos Etapa 1 y Gastos", "gastos_payment_status": "FIRST_EXPLICIT_RECTOR_DEPLOYMENT", "source_id": "e0_cgn_account_2009_esidif_payments_development", "inference_status": "POST_TARGET_DEPLOYMENT"},
    {"row_id": "ST136_06", "date_or_period": "10-11/2009", "level": "órganos rectores", "documented_deployment": "Pagos Etapa 2", "gastos_payment_status": "PAYMENT_ROLLOUT_CONTINUES", "source_id": "e0_cgn_account_2009_esidif_payments_development", "inference_status": "POST_TARGET_DEPLOYMENT"},
    {"row_id": "ST136_07", "date_or_period": "2009", "level": "SAF", "documented_deployment": "Formulación y modificaciones/ejecución; talleres de Gastos/Contabilidad/Retenciones", "gastos_payment_status": "DEVELOPMENT_AND_WORKSHOPS", "source_id": "e0_cgn_account_2009_esidif_payments_development", "inference_status": "SAF_GASTOS_NOT_YET_GENERAL"},
    {"row_id": "ST136_08", "date_or_period": "05/2010", "level": "rectores y SAF 356", "documented_deployment": "Carga manual C-41/C-42", "gastos_payment_status": "EXPLICIT_ROLLOUT", "source_id": "e0_cgn_account_2010_esidif_spending_rollout", "inference_status": "POST_TARGET_EXACT_DATE"},
    {"row_id": "ST136_09", "date_or_period": "07-09/2010", "level": "SAF 356/355", "documented_deployment": "Recepción física ROP; administración local/listados", "gastos_payment_status": "ORGANISM_ROLLOUT", "source_id": "e0_cgn_account_2010_esidif_spending_rollout", "inference_status": "POST_TARGET_EXACT_DATE"},
    {"row_id": "ST136_10", "date_or_period": "2011", "level": "SAF 356/sistema general", "documented_deployment": "Primera versión Gastos; modelo de orden virtual; 50% SAF en nuevo pago", "gastos_payment_status": "TRANSITION_STILL_INCOMPLETE", "source_id": "e0_cgn_account_2011_esidif_saf356_first_spending", "inference_status": "LEGACY_COEXISTENCE_CONFIRMED"},
    {"row_id": "ST136_11", "date_or_period": "conclusión 2008", "level": "target C-41", "documented_deployment": "Entorno SIDIF Central legacy con TRANSAF; e-SIDIF Gastos posterior", "gastos_payment_status": "LEGACY_ENVIRONMENT_PROVED", "source_id": "e0_cgn_circular_07_2008_transaf_entes_transition;e0_cgn_account_2008_esidif_module_scope;e0_cgn_account_2009_esidif_payments_development;e0_cgn_account_2010_esidif_spending_rollout;e0_cgn_account_2011_esidif_saf356_first_spending", "inference_status": "SDPGB_SDPAG_FUNCTIONAL_CONTINUITY_HIGHLY_SUPPORTED_LITERAL_FILENAME_OPEN"},
]
write_csv(HERE / "E0_SIDIF_ESIDIF_TEMPORAL_DEPLOYMENT_V136.csv", sidif_timeline)

agan_route = [
    {"row_id": "AR136_01", "route_component": "Competencia CGN-AGAN", "documented_scope": "mantener el Archivo General de Administración Nacional", "target_query": "C-41 71597;152677;2876", "source_id": "e0_cgn_disposition_20_2007_agan_quality", "status": "DIRECT_AUTHORITY_PROVED_TARGET_OPEN"},
    {"row_id": "AR136_02", "route_component": "Fondo financiero", "documented_scope": "documentación respaldatoria de la gestión financiera ejecutada por los SAF", "target_query": "SAF 355/356; ejercicio 2008", "source_id": "e0_agan_current_archive_services", "status": "DIRECT_SCOPE_PROVED_TARGET_OPEN"},
    {"row_id": "AR136_03", "route_component": "Originales en papel", "documented_scope": "originales surgidos de movimientos de fondos de todos los SAF", "target_query": "C-41; lista diaria; nota; boleto; C-55", "source_id": "e0_amiddf_financial_document_images", "status": "PAPER_CUSTODY_ROUTE_PROVED_TARGET_OPEN"},
    {"row_id": "AR136_04", "route_component": "Índice relacional", "documented_scope": "imágenes enlazadas con registros identificatorios", "target_query": "OB; SAF; fecha; tipo documental; expediente", "source_id": "e0_amiddf_financial_document_images", "status": "DIGITAL_INDEX_ROUTE_PROVED_TARGET_OPEN"},
    {"row_id": "AR136_05", "route_component": "Cuerpos de expediente", "documented_scope": "acceso a todos los cuerpos mediante la aplicación", "target_query": "cuerpo; anexo; folios; signatura; imagen", "source_id": "e0_amiddf_financial_document_images", "status": "BODY_RETRIEVAL_CAPABILITY_PROVED_TARGET_OPEN"},
    {"row_id": "AR136_06", "route_component": "Servicio de consulta", "documented_scope": "usuarios, organismos de control, Poder Judicial, SAF e investigadores", "target_query": "consulta archivística motivada y copia/certificación", "source_id": "e0_agan_current_archive_services;e0_amiddf_financial_document_images;e0_cgn_disposition_20_2007_agan_quality", "status": "SERVICE_ROUTE_PROVED_NOT_CONTACTED"},
    {"row_id": "AR136_07", "route_component": "Integridad y disponibilidad", "documented_scope": "ordenar, custodiar y facilitar documentación para control y auditoría", "target_query": "inventario; custodia; faltantes; transferencia; expurgo si existiera", "source_id": "e0_agan_current_coordination_contact", "status": "OFFICIAL_PUBLISHED_COMPETENCE_TARGET_OPEN"},
    {"row_id": "AR136_08", "route_component": "Contacto publicado", "documented_scope": "mherri@mecon.gov.ar; 54-11-4349-7824", "target_query": "verificar vigencia antes de cualquier presentación", "source_id": "e0_agan_current_coordination_contact", "status": "PUBLISHED_CONTACT_NOT_VERIFIED_NOT_CONTACTED"},
]
write_csv(HERE / "E0_AGAN_C41_ARCHIVAL_ROUTE_V136.csv", agan_route)

daily_records = [
    {"row_id": "DR136_01", "agency_class": "Administración Central, PAGADOR TGN", "record": "Copia papel de orden de pago presentada a CGN", "minimum_fields": "C-41 completo; número; SAF; importe; firmas", "source_id": "e0_cgn_tgn_joint_disposition_13_16_2009_payment_records", "temporal_status": "2009_RULE_SUCCESSOR_COMPARATOR"},
    {"row_id": "DR136_02", "agency_class": "Administración Central sin SLU", "record": "Lista diaria impresa de órdenes seleccionadas para cancelar por CUT", "minimum_fields": "fecha; SAF; órdenes; selección; firma responsable", "source_id": "e0_cgn_tgn_joint_disposition_13_16_2009_payment_records", "temporal_status": "2009_RULE_SUCCESSOR_COMPARATOR"},
    {"row_id": "DR136_03", "agency_class": "Organismo descentralizado sin SLU", "record": "Autorización de pago transmitida", "minimum_fields": "ejercicio; SAF; fecha; número; beneficiario; CUIT; fuente; banco/sucursal; tipo R/B; importe; cuenta", "source_id": "e0_cgn_tgn_joint_disposition_13_16_2009_payment_records", "temporal_status": "2009_RULE_SUCCESSOR_COMPARATOR"},
    {"row_id": "DR136_04", "agency_class": "Organismo descentralizado sin SLU", "record": "Lista diaria de autorizaciones", "minimum_fields": "fecha; SAF; autorización; beneficiario; importe; total; firmas", "source_id": "e0_cgn_tgn_joint_disposition_13_16_2009_payment_records", "temporal_status": "2009_RULE_SUCCESSOR_COMPARATOR"},
    {"row_id": "DR136_05", "agency_class": "responsables firmantes", "record": "Certificación de documentación respaldatoria vista", "minimum_fields": "identidad; cargo; firma; fecha; declaración", "source_id": "e0_cgn_tgn_joint_disposition_13_16_2009_payment_records", "temporal_status": "2009_RULE_SUCCESSOR_COMPARATOR"},
    {"row_id": "DR136_06", "agency_class": "pagos al exterior y casos especiales", "record": "Nota y soporte papel adicionales", "minimum_fields": "beneficiario; destino; moneda; importe; orden", "source_id": "e0_cgn_tgn_joint_disposition_13_16_2009_payment_records", "temporal_status": "CLASS_CONDITIONAL"},
    {"row_id": "DR136_07", "agency_class": "control temporal", "record": "Listado de normas derogadas", "minimum_fields": "artículo 7; normas expresamente derogadas", "source_id": "e0_cgn_tgn_joint_disposition_13_16_2009_payment_records", "temporal_status": "CIRCULAR_TGN_7_1997_NOT_LISTED_SUPPORTING_NON_REPEAL_ONLY"},
]
write_csv(HERE / "E0_DAILY_PAYMENT_SELECTION_RECORDS_V136.csv", daily_records)

partial_state = [
    {"row_id": "PP136_01", "state_component": "Conformidad SIDIF", "rule": "punto de partida para la caducidad", "target_field": "fecha de conformidad", "source_id": "e0_cgn_disposition_54_2008_order_expiry_partial", "status": "RULE_PROVED_TARGET_VALUE_OPEN"},
    {"row_id": "PP136_02", "state_component": "Caducidad", "rule": "cierre del ejercicio siguiente a la conformidad", "target_field": "fecha y causal de caducidad", "source_id": "e0_cgn_disposition_54_2008_order_expiry_partial", "status": "RULE_PROVED_TARGET_VALUE_OPEN"},
    {"row_id": "PP136_03", "state_component": "Excepción", "rule": "pagos parciales del SAF antes de caducar", "target_field": "cada importe y fecha de pago parcial", "source_id": "e0_cgn_disposition_54_2008_order_expiry_partial", "status": "PARTIAL_PAYMENT_STATE_PROVED_TARGET_VALUE_OPEN"},
    {"row_id": "PP136_04", "state_component": "Denominador", "rule": "importe original de la orden", "target_field": "importe ordenado y moneda", "source_id": "e0_cgn_disposition_54_2008_order_expiry_partial", "status": "REQUIRED_TO_CLASSIFY_TOTAL_VS_PARTIAL"},
    {"row_id": "PP136_05", "state_component": "Numerador y saldo", "rule": "suma de movimientos pagados y saldo residual", "target_field": "Σ pagos; saldo; anulación/caducidad", "source_id": "e0_cgn_disposition_54_2008_order_expiry_partial", "status": "REQUIRED_TO_CLOSE_EXECUTION"},
]
write_csv(HERE / "E0_C41_PARTIAL_PAYMENT_EXPIRY_STATE_V136.csv", partial_state)

external_classification = [
    {"row_id": "EC136_01", "sidif_id": "71597", "known_row": "83106000 COMISIONES - BANCO NACION; ARS 32.270,30 aggregate", "classification": "OPEN", "required_evidence": "C-41; observaciones; nota TGN; beneficiario; banco/cuenta; boleto o certificación de no aplicabilidad", "source_id": "e0_cgn_cuenta_inversion_2008_sdp;e0_cgn_tgn_disposicion_conjunta_47_10_2008_external_payments", "forbidden_inference": "Comisión BNA equivale a pago exterior o recompra."},
    {"row_id": "EC136_02", "sidif_id": "152677", "known_row": "83106000 COMISIONES - BANCO NACION; ARS 32.270,30 aggregate", "classification": "OPEN", "required_evidence": "C-41; observaciones; nota TGN; beneficiario; banco/cuenta; boleto o certificación de no aplicabilidad", "source_id": "e0_cgn_cuenta_inversion_2008_sdp;e0_cgn_tgn_disposicion_conjunta_47_10_2008_external_payments", "forbidden_inference": "Comisión BNA equivale a pago exterior o recompra."},
    {"row_id": "EC136_03", "sidif_id": "2876", "known_row": "83106000 COMISIONES - BANCO NACION; ARS 32.270,30 aggregate", "classification": "OPEN", "required_evidence": "C-41; observaciones; nota TGN; beneficiario; banco/cuenta; boleto o certificación de no aplicabilidad", "source_id": "e0_cgn_cuenta_inversion_2008_sdp;e0_cgn_tgn_disposicion_conjunta_47_10_2008_external_payments", "forbidden_inference": "Comisión BNA equivale a pago exterior o recompra."},
    {"row_id": "EC136_04", "sidif_id": "aggregate", "known_row": "tres referencias exactas dentro de un único renglón contable", "classification": "EXTERNAL_PAYMENT_CLASSIFICATION_OPEN", "required_evidence": "clasificación individual por OB; no inferir desde título de cuenta", "source_id": "e0_cgn_cuenta_inversion_2008_sdp;e0_cgn_tgn_disposicion_conjunta_47_10_2008_external_payments", "forbidden_inference": "Distribuir ARS 32.270,30 entre las tres órdenes sin originales."},
]
write_csv(HERE / "E0_C41_EXTERNAL_CLASSIFICATION_V136.csv", external_classification)

comdoc_custody = [
    {"row_id": "CC135_01", "control": "Registro COMDOC o seguimiento alternativo", "requested_field": "número; estado; área depositaria", "source_id": "e0_minplan_resolution_1522_2006_comdoc_custody", "scope_status": "CONTEMPORANEOUS_COMPARATOR", "target_use": "S01:0342455/2008 y anexos"},
    {"row_id": "CC135_02", "control": "Dos remitos", "requested_field": "emisor; receptor; firma; fecha", "source_id": "e0_minplan_resolution_1522_2006_comdoc_custody", "scope_status": "CONTEMPORANEOUS_COMPARATOR", "target_use": "probar entrega y recepción"},
    {"row_id": "CC135_03", "control": "Integridad material", "requested_field": "cantidad de cuerpos; anexos; último folio", "source_id": "e0_minplan_resolution_1522_2006_comdoc_custody", "scope_status": "CONTEMPORANEOUS_COMPARATOR", "target_use": "controlar contenido recibido"},
    {"row_id": "CC135_04", "control": "Pérdida alegada", "requested_field": "circular COMDOC; búsqueda intensiva; áreas consultadas; resultado", "source_id": "e0_minplan_resolution_1522_2006_comdoc_custody", "scope_status": "CONTEMPORANEOUS_COMPARATOR", "target_use": "exigir trazabilidad de búsqueda"},
    {"row_id": "CC135_05", "control": "Reconstrucción", "requested_field": "copias certificadas; informe explicativo; acto de reconstrucción", "source_id": "e0_minplan_resolution_1522_2006_comdoc_custody", "scope_status": "CONTEMPORANEOUS_COMPARATOR", "target_use": "evitar cerrar por mera ausencia"},
    {"row_id": "CC135_06", "control": "Instrucción de deuda contemporánea", "requested_field": "nota conjunta ONCP/TGN; firmantes; fecha; operación", "source_id": "e0_debt_joint_resolution_216_26_2008_instruction_chain", "scope_status": "OTHER_DEBT_PROCEDURE_COMPARATOR", "target_use": "buscar documento funcionalmente análogo sin presumirlo"},
    {"row_id": "CC135_07", "control": "Registro diario COMDOC", "requested_field": "reporte diario; archivo; fecha; identificador", "source_id": "e0_debt_joint_resolution_216_26_2008_instruction_chain", "scope_status": "OTHER_DEBT_PROCEDURE_COMPARATOR", "target_use": "formular búsqueda por sistema"},
    {"row_id": "CC135_08", "control": "Aceptación y registro", "requested_field": "validación; aceptación Caja; registro SIGADE; recibo/acreditación", "source_id": "e0_debt_joint_resolution_216_26_2008_instruction_chain", "scope_status": "OTHER_DEBT_PROCEDURE_COMPARATOR", "target_use": "mapear clases documentales, no adjudicar resultado"},
]
write_csv(HERE / "E0_COMDOC_CUSTODY_AND_DEBT_INSTRUCTION_COMPARATOR_V136.csv", comdoc_custody)

# Rutas agotadas, ledger y cortes metodológicos.
exhaust_path = HERE / "E0_EXPEDIENT_PUBLIC_SEARCH_EXHAUSTION_V136.csv"
exhaust = read_csv(exhaust_path)[:6]
exhaust.extend([
    {"search_id": "EX134_07", "target": "FindDoc capability", "route": "Agenda Digital Argentina pp.206-207", "result": "Esquema de salida y arquitectura exactos", "public_body_found": "DESIGN_SPEC", "status": "ROUTE_METADATA_CAPABILITY_PROVED", "permitted_inference": "El índice histórico mostraba pases y ubicación.", "forbidden_inference": "Mostraba el cuerpo."},
    {"search_id": "EX134_08", "target": "S01:0130656/2008", "route": "AGN Informe 254/2013", "result": "Consulta real al endpoint con estado y ubicación al 05/03/2013", "public_body_found": "CONTROL_QUERY_METADATA", "status": "HISTORIC_OPERATIONAL_CONTROL", "permitted_inference": "FindDoc funcionaba para un S01/2008.", "forbidden_inference": "Responde por el target."},
    {"search_id": "EX134_09", "target": "S01:0342455/2008", "route": "canales oficiales alternativos Economía", "result": "Email, teléfono y atención presencial identificados; no contactados", "public_body_found": "NO", "status": "ADMINISTRATIVE_ROUTE_READY_NOT_SENT", "permitted_inference": "Puede pedirse exportación de hoja de ruta.", "forbidden_inference": "La consulta fue presentada."},
    {"search_id": "EX134_10", "target": "Nota Bicameral 18/05/2012", "route": "inventario actual Senado + sumario HCDN 23/05/2012", "result": "Contexto de archivo masivo; cuerpo exacto no localizado", "public_body_found": "CONTEXT_ONLY", "status": "PUBLIC_INVENTORY_EXHAUSTED_EXACT_NOTE_OPEN", "permitted_inference": "El pedido puede dirigirse al contacto actual con dos OV exactos.", "forbidden_inference": "Los expedientes fueron parte del lote de Cámara o fueron destruidos."},
    {"search_id": "EX135_11", "target": "C-41 71597, 152677 y 2876", "route": "búsquedas oficiales exactas por número, Banco Nación, cuenta 83106000 e importe", "result": "Sólo se recuperó el Anexo K; no cuerpos C-41 ni filas SDPGB/SDPAG", "public_body_found": "REFERENCE_ROW_ONLY", "status": "THREE_C41_IDENTIFIERS_EXACT_PUBLIC_BODIES_AND_STATES_NOT_LOCATED", "permitted_inference": "Los tres números son claves de búsqueda exactas de comisiones BNA.", "forbidden_inference": "Fueron pagados o pertenecen a la recompra."},
    {"search_id": "EX135_12", "target": "OV 366/09 y OV 44/10", "route": "índice histórico HCDN; seis variantes exactas", "result": "Sin coincidencias en el índice público preservado", "public_body_found": "NO_IN_PUBLIC_INDEX", "status": "PUBLIC_INDEX_NEGATIVE_CONTROL_ONLY", "permitted_inference": "La búsqueda archivística debe usar todas las variantes.", "forbidden_inference": "Los expedientes no existen o fueron destruidos."},
    {"search_id": "EX135_13", "target": "Estado efectivo de las tres órdenes", "route": "normativa CGN/TGN y Cuenta de Inversión 2008", "result": "Esquema P/R/A y clases de instrucción/movimiento/saldo localizados; filas target no públicas", "public_body_found": "SYSTEM_SCHEMA_AND_RECORD_CLASSES", "status": "QUERY_SPECIFICATION_CLOSED_TARGET_VALUES_OPEN", "permitted_inference": "El pedido puede exigir campos y archivos concretos.", "forbidden_inference": "La arquitectura del sistema resuelve el estado target."},
    {"search_id": "EX136_14", "target": "C-41 71597, 152677 y 2876 en AGAN/AMIDDF", "route": "páginas oficiales AGAN y AMIDDF", "result": "Ruta competente de originales, imágenes e índices probada; consulta target no ejecutada", "public_body_found": "CUSTODIAN_AND_QUERY_ROUTE_ONLY", "status": "DIRECT_ARCHIVAL_ROUTE_FOUND_TARGET_HOLDINGS_OPEN", "permitted_inference": "Dirigir una búsqueda exacta al custodio financiero.", "forbidden_inference": "Las tres piezas están disponibles o fueron expurgadas."},
    {"search_id": "EX136_15", "target": "Continuidad SDPGB/SDPAG a 2008", "route": "Circular 07/08 y Cuentas de Inversión 2008-2011", "result": "Entorno SIDIF Central legacy probado y e-SIDIF Gastos desplegado después; nombre literal target no hallado", "public_body_found": "TEMPORAL_SYSTEM_BRIDGE", "status": "FUNCTIONAL_CONTINUITY_HIGHLY_SUPPORTED_LITERAL_FILENAME_OPEN", "permitted_inference": "Pedir SDPGB/SDPAG o salida sucesora del SIDIF Central.", "forbidden_inference": "El nombre y formato permanecieron idénticos en 2008."},
    {"search_id": "EX136_16", "target": "Movimiento CRYL específico 2008", "route": "Cuenta de Inversión 2009 como control temporal", "result": "La recepción de movimientos CRYL se documenta como incorporación en 2009", "public_body_found": "POST_TARGET_FIRST_DOCUMENTED_INCORPORATION", "status": "CRYL_2008_ROUTE_NOT_PROVED", "permitted_inference": "Separar archivos bancarios generales 2008 de la recepción CRYL específica.", "forbidden_inference": "Proyectar a 2008 la ruta CRYL incorporada en 2009."},
])
write_csv(exhaust_path, exhaust)

ledger_path = HERE / "E0_FISCAL_MECHANISM_LEDGER_V136.csv"
ledger = read_csv(ledger_path)[:157]
ledger.extend([
    {"ledger_id": "F158", "window": "2011-2013", "mechanism": "Legacy_document_index", "phase": "FINDDOC_CAPABILITY_AND_CONTROL", "as_of_date": "2013-03-05", "payer": "N/A", "recipient": "N/A", "universe": "COMDOC_S01_files", "instrument": "FindDoc_route_metadata", "amount_original": "4", "original_unit": "OUTPUT_FIELD_FAMILIES", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_agenda_digital_finddoc_comdoc_architecture;e0_agn_informe_254_2013_finddoc_control", "source_locator": "Agenda_pp206_207;AGN_254_pp91_93_133", "realization_status": "HISTORIC_CAPABILITY_AND_OPERATIONAL_CONTROL_PROVED", "additivity": "NON_ADDITIVE", "status_interpretation": "FindDoc exposed route/location metadata and was actually used for another 2008 S01 file.", "caveat": "The target query remains unexecuted and body content is outside the proven output schema."},
    {"ledger_id": "F159", "window": "2008-2026", "mechanism": "Debt_buyback_excess_GDP", "phase": "TARGET_FINDDOC_ADMINISTRATIVE_QUERY", "as_of_date": "2026-08-30", "payer": "N/A", "recipient": "N/A", "universe": "S01_0342455_2008", "instrument": "COMDOC_FindDoc", "amount_original": "0", "original_unit": "TARGET_QUERY_RESULTS", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_economia_consulta_expedientes_comdoc_gde;e0_agenda_digital_finddoc_comdoc_architecture", "source_locator": "official_alternative_channels", "realization_status": "ADMINISTRATIVE_EXPORT_REQUIRED_DRAFT_NOT_SENT", "additivity": "NON_ADDITIVE", "status_interpretation": "The expected route fields and official contact channel are known.", "caveat": "No request was submitted and no target route was recovered."},
    {"ledger_id": "F160", "window": "1995-2008", "mechanism": "Debt_accounting_payment_chain", "phase": "C41_TO_BANK_DEBIT_RECONCILIATION", "as_of_date": "2008-12-31", "payer": "Tesoro_Nacional", "recipient": "Unknown_target_beneficiaries", "universe": "SIDIF_71597_152677_2876", "instrument": "C41_C55_bank_debit", "amount_original": "3", "original_unit": "C41_LOCATORS", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_cgn_cuenta_inversion_2008_sdp;e0_cgn_circular_2_1997_c41_due_date;e0_cgn_circular_6_1995_c41_tgn;e0_cgn_circular_13_2002_external_payments_c41;e0_cgn_circular_22_2004_c55_bank_debit", "source_locator": "Anexo_K_and_CGN_procedure_rules", "realization_status": "DOCUMENT_CLASS_AND_CHAIN_PROVED_TARGET_BODIES_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "Three exact identifiers can anchor searches for order, processing, debit and adjustment records.", "caveat": "An order number is not executed payment and is not yet linked to the buyback."},
    {"ledger_id": "F161", "window": "2012-05-18/2012-05-28", "mechanism": "AGN_parliamentary_archive", "phase": "MASS_ARCHIVE_CONTEXT_CONTROL", "as_of_date": "2012-05-28", "payer": "N/A", "recipient": "Parliamentary_archive", "universe": "OV_366_09_OV_44_10", "instrument": "Bicameral_note_and_HCDN_archive_batch", "amount_original": "2", "original_unit": "TARGET_EXPEDIENTS", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_senado_bicameral_revisora_current_documents;e0_hcdn_session_summary_2012_05_23_mass_archive", "source_locator": "current_public_inventory;HCDN_session_summary", "realization_status": "MASS_ARCHIVE_CONTEXT_ONLY_EXACT_NOTE_BODY_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "The period contains mass archival activity but the two target strings were not located in the inspected HCDN summary.", "caveat": "Context does not establish the disposition of either target expediente."},
    {"ledger_id": "F162", "window": "1997-2008", "mechanism": "Debt_accounting_payment_chain", "phase": "SIDIF_DAILY_PAYMENT_STATE_OUTPUT", "as_of_date": "2008-12-31", "payer": "Tesoro_Nacional", "recipient": "Unknown_target_beneficiaries", "universe": "SIDIF_71597_152677_2876", "instrument": "SDPGB_SDPAG_or_successor", "amount_original": "3", "original_unit": "TARGET_ORDER_IDS", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_tgn_circular_7_1997_daily_paid_files;e0_cgn_circular_34_1997_sdpgb_paid_beneficiary_schema", "source_locator": "Circular_TGN_7_97;Anexo_Circular_CGN_34_97", "realization_status": "PAYMENT_STATE_SCHEMA_PROVED_TARGET_ROWS_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "The official historical output distinguishes paid, rejected and annulled orders and exposes bank/payment fields.", "caveat": "Literal continuity of the filenames to 2008 and the three target rows remain unproved."},
    {"ledger_id": "F163", "window": "2008", "mechanism": "Treasury_central_account_payment_system", "phase": "TGN_BCRA_ELECTRONIC_RECORD_CLASSES", "as_of_date": "2008-12-31", "payer": "TGN", "recipient": "BCRA", "universe": "Payment_instructions_movements_balances", "instrument": "Electronic_files_over_communication_link", "amount_original": "3", "original_unit": "RECORD_CLASSES", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_cgn_cuenta_inversion_2008_tomo_ii_tgn_system_files", "source_locator": "Cuenta_Inversion_2008_Tomo_II_printed_p177", "realization_status": "2008_SYSTEM_RECORD_CLASSES_PROVED_TARGET_LINK_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "Payment instruction, movement and balance files existed as system classes in 2008.", "caveat": "No target instruction or movement has been located."},
    {"ledger_id": "F164", "window": "2008", "mechanism": "External_public_debt_payment", "phase": "C41_EXTERNAL_PAYMENT_DOCUMENT_PACKAGE", "as_of_date": "2008-10-14", "payer": "SAF_355_356", "recipient": "Conditional_foreign_beneficiary", "universe": "External_payments_if_applicable", "instrument": "C41_TGN_note_BNA_exchange_documents", "amount_original": "0", "original_unit": "TARGET_APPLICABILITY_PROVED", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_cgn_tgn_disposicion_conjunta_47_10_2008_external_payments", "source_locator": "Joint_Disposition_47_10_2008", "realization_status": "CONTEMPORANEOUS_SCHEMA_PROVED_TARGET_APPLICABILITY_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "If an order was external, the package should identify beneficiary, destination bank/account, currency and SIDIF order.", "caveat": "No target order is classified as external."},
    {"ledger_id": "F165", "window": "2006-2008", "mechanism": "COMDOC_document_custody", "phase": "REMIT_INTEGRITY_LOSS_RECONSTRUCTION_CONTROL", "as_of_date": "2008-12-31", "payer": "N/A", "recipient": "Depositary_area", "universe": "S01_0342455_2008_and_annexes", "instrument": "COMDOC_remits_folios_search_reconstruction", "amount_original": "0", "original_unit": "TARGET_CUSTODY_RECORDS_LOCATED", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_minplan_resolution_1522_2006_comdoc_custody", "source_locator": "Resolution_1522_2006_updated_art34", "realization_status": "CONTEMPORANEOUS_CUSTODY_COMPARATOR_TARGET_RECORDS_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "The comparator yields precise fields for remittance, integrity, intensive search and reconstruction requests.", "caveat": "The MINPLAN rule is not automatically governing for the Economy/ONCP target."},
    {"ledger_id": "F166", "window": "2008", "mechanism": "Public_debt_security_instruction", "phase": "ONCP_TGN_INSTRUCTION_AND_ACCEPTANCE_COMPARATOR", "as_of_date": "2008-06-27", "payer": "ONCP_TGN", "recipient": "Registration_or_payment_agent", "universe": "Consolidation_bond_procedure", "instrument": "Joint_note_COMDOC_file_SIGADE_Caja_acceptance", "amount_original": "0", "original_unit": "TARGET_EQUIVALENCE_PROVED", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_debt_joint_resolution_216_26_2008_instruction_chain", "source_locator": "Joint_Resolution_216_26_2008_art5_annex", "realization_status": "OTHER_DEBT_PROCEDURE_DOCUMENT_CLASS_COMPARATOR", "additivity": "NON_ADDITIVE", "status_interpretation": "A contemporaneous debt procedure generated instruction, data, validation, acceptance and SIGADE records.", "caveat": "It is not the buyback procedure and cannot be substituted for target proof."},
    {"ledger_id": "F167", "window": "2008-2011", "mechanism": "Financial_management_information_system", "phase": "LEGACY_SIDIF_TO_ESIDIF_TEMPORAL_BRIDGE", "as_of_date": "2011-12-31", "payer": "N/A", "recipient": "SAF_355_356", "universe": "C41_payment_processing_environment", "instrument": "SIDIF_Central_TRANSAF_eSIDIF_Gastos", "amount_original": "5", "original_unit": "OFFICIAL_TEMPORAL_CONTROLS", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_cgn_circular_07_2008_transaf_entes_transition;e0_cgn_account_2008_esidif_module_scope;e0_cgn_account_2009_esidif_payments_development;e0_cgn_account_2010_esidif_spending_rollout;e0_cgn_account_2011_esidif_saf356_first_spending", "source_locator": "official_2008_2011_deployment_sequence", "realization_status": "2008_LEGACY_SIDIF_CENTRAL_ENVIRONMENT_PROVED_LITERAL_OUTPUT_FILENAME_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "The target year precedes documented e-SIDIF Gastos deployment and belongs to the legacy SIDIF Central environment.", "caveat": "Functional continuity does not prove the literal SDPGB/SDPAG filename in 2008."},
    {"ledger_id": "F168", "window": "2009", "mechanism": "Treasury_payment_documentation", "phase": "C41_PAPER_AND_DAILY_SELECTION_PACKET", "as_of_date": "2009-06-26", "payer": "SAF_TGN", "recipient": "CGN_TGN", "universe": "payment_orders_and_authorizations", "instrument": "C41_paper_daily_signed_lists_authorizations", "amount_original": "4", "original_unit": "RECORD_CLASSES", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_cgn_tgn_joint_disposition_13_16_2009_payment_records", "source_locator": "Joint_Disposition_CGN13_TGN16_2009", "realization_status": "IMMEDIATE_POST_TARGET_PACKET_SCHEMA_PROVED_2008_APPLICABILITY_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "The successor procedure exposes paper and signed daily records capable of identifying order, beneficiary, account and amount.", "caveat": "The 2009 rule cannot be automatically applied retroactively to 2008."},
    {"ledger_id": "F169", "window": "2008-2009", "mechanism": "Payment_order_expiry", "phase": "PARTIAL_PAYMENT_BEFORE_EXPIRY", "as_of_date": "2008-12-12", "payer": "SAF", "recipient": "Payment_order_beneficiary", "universe": "SIDIF_71597_152677_2876", "instrument": "payment_order_partial_history", "amount_original": "3", "original_unit": "TARGET_ORDER_IDS", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_cgn_disposition_54_2008_order_expiry_partial", "source_locator": "CGN_Disposition_54_2008", "realization_status": "PARTIAL_PAYMENT_STATE_RULE_PROVED_TARGET_VALUES_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "Orders can carry partial payments before expiry, requiring original amount, cumulative payments and residual balance.", "caveat": "A final P/R/A code alone may not demonstrate total cancellation."},
    {"ledger_id": "F170", "window": "2007-2026", "mechanism": "Financial_document_archive", "phase": "AGAN_AMIDDF_CUSTODY_AND_RETRIEVAL", "as_of_date": "2026-08-30", "payer": "N/A", "recipient": "CGN_AGAN", "universe": "SAF_financial_supporting_documents", "instrument": "paper_originals_digital_images_relational_index", "amount_original": "0", "original_unit": "TARGET_C41_HOLDINGS_LOCATED", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_agan_current_archive_services;e0_amiddf_financial_document_images;e0_cgn_disposition_20_2007_agan_quality;e0_agan_current_coordination_contact", "source_locator": "official_AGAN_AMIDDF_pages", "realization_status": "DIRECT_FINANCIAL_CUSTODIAN_ROUTE_PROVED_TARGET_NOT_QUERIED", "additivity": "NON_ADDITIVE", "status_interpretation": "AGAN/AMIDDF is the direct route for original and digitized supporting financial records from SAF operations.", "caveat": "No target holding or image has been recovered and the published contact was not used."},
    {"ledger_id": "F171", "window": "2008-2009", "mechanism": "CRYL_movement_information", "phase": "TEMPORAL_ROUTE_CONTROL", "as_of_date": "2009-12-31", "payer": "BCRA_CRYL", "recipient": "TGN", "universe": "CRYL_movements", "instrument": "movement_information_file", "amount_original": "1", "original_unit": "FIRST_DOCUMENTED_INCORPORATION", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_cgn_account_2009_esidif_payments_development", "source_locator": "Cuenta_Inversion_2009_aspectos", "realization_status": "CRYL_MOVEMENT_RECEIPT_FIRST_DOCUMENTED_2009_TARGET_2008_ROUTE_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "The official 2009 account describes receipt of CRYL movements as an incorporation.", "caveat": "General 2008 BCRA movement files must not be relabeled as CRYL-specific without direct evidence."},
    {"ledger_id": "F172", "window": "2008", "mechanism": "External_payment_classification", "phase": "THREE_C41_APPLICABILITY_CONTROL", "as_of_date": "2008-12-31", "payer": "SAF_355_356", "recipient": "Unknown", "universe": "SIDIF_71597_152677_2876", "instrument": "C41_observations_TGN_note_BNA_documents", "amount_original": "0", "original_unit": "TARGET_ORDERS_CLASSIFIED_EXTERNAL", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_cgn_cuenta_inversion_2008_sdp;e0_cgn_tgn_disposicion_conjunta_47_10_2008_external_payments;e0_agan_current_archive_services", "source_locator": "Anexo_K_and_conditional_external_schema", "realization_status": "EXTERNAL_PAYMENT_CLASSIFICATION_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "Each order must be classified from its body and supporting packet before applying the external-payment schema.", "caveat": "The Banco Nación commission account title does not establish external-payment or buyback attribution."},
])
assert len(ledger) == 172
write_csv(ledger_path, ledger)

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V136.csv"
breaks = read_csv(breaks_path)[:117]
breaks.extend([
    {"break_id": "finddoc_route_metadata_not_expedient_body", "dimension": "document_scope", "problem": "FindDoc's public output is proven for route and location fields.", "rule": "Use it to trace custody; request the body separately.", "status": "FROZEN", "evidence": "Agenda Digital pp.206-207"},
    {"break_id": "historic_control_query_not_target_query", "dimension": "external_validity", "problem": "AGN queried another S01/2008 successfully in 2013.", "rule": "Use as operational control only; keep S01:0342455/2008 unqueried.", "status": "FROZEN", "evidence": "AGN 254/2013 pp.93,133"},
    {"break_id": "c41_order_not_executed_payment", "dimension": "phase", "problem": "C-41 is an order that can require processing, TGN action, debit and adjustment.", "rule": "Require payment/debit status and C-55 or equivalent where applicable.", "status": "FROZEN", "evidence": "CGN Circulares 2/97, 6/95, 13/02, 22/04"},
    {"break_id": "mass_archive_context_not_target_disposition", "dimension": "archival_scope", "problem": "A large HCDN archive batch is temporally adjacent but does not list the two exact target strings.", "rule": "Retain exact Senate metadata as locator and request the 18/05/2012 note.", "status": "FROZEN", "evidence": "HCDN reunión 8; Senate OV 366/09 and OV 44/10"},
    {"break_id": "horizontal_pdf_linearization_not_row_alignment", "dimension": "source_parsing", "problem": "Search snippets can shift identifiers between horizontally aligned table rows.", "rule": "The rendered visual row controls account, amount and SIDIF attribution.", "status": "FROZEN", "evidence": "CGN Cuenta de Inversión 2008 Anexo K, physical PDF page 67"},
    {"break_id": "payment_output_schema_not_target_state", "dimension": "phase", "problem": "SDPGB/SDPAG define paid, rejected and annulled outputs.", "rule": "Require the target row or certified successor extract before assigning a state.", "status": "FROZEN", "evidence": "TGN Circular 7/97; CGN Circular 34/97 annex"},
    {"break_id": "historic_filename_not_automatic_2008_continuity", "dimension": "temporal_scope", "problem": "The exact SDPGB/SDPAG filenames are proved in 1997.", "rule": "Request the named files or their 2008 successor equivalent; do not assert unchanged format.", "status": "FROZEN", "evidence": "TGN Circular 7/97; CGN Circular 34/97 annex"},
    {"break_id": "system_record_class_not_target_record", "dimension": "external_validity", "problem": "TGN/BCRA instruction, movement and balance file classes are documented for 2008.", "rule": "Require identifiers and target linkage for each of the three C-41 orders.", "status": "FROZEN", "evidence": "Cuenta de Inversión 2008 Tomo II, printed p.177"},
    {"break_id": "external_payment_schema_conditional", "dimension": "scope", "problem": "The 2008 external-payment rule provides detailed fields for SAF 355/356.", "rule": "Apply only after an order is classified as an external payment.", "status": "FROZEN", "evidence": "CGN/TGN Joint Disposition 47/10 of 2008"},
    {"break_id": "contemporaneous_comparator_not_target_governing_rule", "dimension": "legal_scope", "problem": "COMDOC custody and another debt-title procedure expose useful document classes.", "rule": "Use as search comparators, never as proof that the target was governed by or generated the same records.", "status": "FROZEN", "evidence": "MINPLAN Resolution 1522/2006; Joint Resolution 216/26 of 2008"},
    {"break_id": "esidif_entes_replacement_not_gastos_deployment", "dimension": "system_scope", "problem": "Circular 07/08 replaces only the Entes module.", "rule": "Do not treat it as deployment of e-SIDIF Gastos or payment processing.", "status": "FROZEN", "evidence": "CGN Circular 07/2008"},
    {"break_id": "deployment_chronology_not_literal_filename_continuity", "dimension": "temporal_scope", "problem": "The 2008-2011 sequence proves a legacy environment and later Gastos rollout.", "rule": "Classify SDPGB/SDPAG continuity as highly supported but request the 2008 name or functional successor.", "status": "FROZEN", "evidence": "Cuentas de Inversión 2008-2011"},
    {"break_id": "final_state_code_not_partial_payment_history", "dimension": "measurement", "problem": "A conforming order may receive partial payments before expiry.", "rule": "Require original amount, each payment, cumulative paid and residual balance.", "status": "FROZEN", "evidence": "CGN Disposition 54/2008"},
    {"break_id": "agan_scope_not_target_holding", "dimension": "archival_scope", "problem": "AGAN/AMIDDF is competent for financial supporting documents.", "rule": "Do not claim target custody until an index result, image, signatura or certified response is obtained.", "status": "FROZEN", "evidence": "AGAN; AMIDDF; CGN Disposition 20/2007"},
    {"break_id": "successor_2009_payment_packet_not_automatic_2008_rule", "dimension": "legal_temporal_scope", "problem": "The 2009 disposition specifies paper and daily signed records.", "rule": "Use it as an immediate successor/comparator unless direct 2008 applicability is proved.", "status": "FROZEN", "evidence": "Joint Disposition CGN 13/2009 and TGN 16/2009"},
    {"break_id": "cryl_2009_incorporation_not_2008_route", "dimension": "temporal_scope", "problem": "The 2009 account describes receipt of CRYL movements as an incorporation.", "rule": "Keep general BCRA movement files in 2008 separate from CRYL-specific movement receipt.", "status": "FROZEN", "evidence": "Cuenta de Inversión 2009"},
])
assert len(breaks) == 133
write_csv(breaks_path, breaks)

# Se enriquecen los seis borradores; nada se envía.
trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V136.csv"
trace = read_csv(trace_path)[:104]
trace.extend([
    {"trace_id": "TR134_105", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / administradores COMDOC", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Exportación de hoja de ruta FindDoc/COMDOC del expediente target", "period_or_date": "2008-actualidad", "identifiers": "S01:0342455/2008;VerExpediente", "minimum_usable_fields": "origen;destino;fecha envío;fecha recepción;ubicación;estado", "confidentiality_fallback": "metadatos de pases sin cuerpo", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR134_106", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / CGN / TGN", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Cuerpo y estado de tres formularios C-41 2008", "period_or_date": "2008", "identifiers": "SIDIF 71597;152677;2876;SIGADE 83106000", "minimum_usable_fields": "SAF;beneficiario;concepto;importe;moneda;emisión;vencimiento;estado", "confidentiality_fallback": "cuadro certificado por número SIDIF", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR134_107", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / TGN / BNA", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Pago, débito, rechazo, reversa o C-55 asociados a cada C-41", "period_or_date": "2008-2009", "identifiers": "71597;152677;2876;C-41;C-55", "minimum_usable_fields": "fecha;importe;moneda;cuenta;estado;documento original;vínculo C-41", "confidentiality_fallback": "estado final y total por orden", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR134_108", "request_id": "REQ134_ECON", "institution": "Dirección de Información Ciudadana / Mesa de Entradas", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Consulta administrativa sustitutiva por caída del endpoint", "period_or_date": "2026-08-30", "identifiers": "ciudadano@mecon.gov.ar;0810-333-6326;Balcarce186 oficina140", "minimum_usable_fields": "acuse;número de gestión;resultado;derivación", "confidentiality_fallback": "derivación al custodio competente", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR134_109", "request_id": "REQ134_AGN", "institution": "Senado / Bicameral Revisora", "gap_id": "CL134_AGN_REPLY", "requested_record": "Nota de archivo del 18/05/2012 e inventario/remito asociado", "period_or_date": "2012-05-18/2012-05-28", "identifiers": "OV366/09;OV44/10;nota18/05/2012", "minimum_usable_fields": "emisor;destinatario;listado;fecha;depósito;signatura", "confidentiality_fallback": "renglones exactos de ambos OV", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR134_110", "request_id": "REQ134_AGN", "institution": "Senado / Bicameral Revisora", "gap_id": "CL134_AGN_REPLY", "requested_record": "Resultado de búsqueda en fondo histórico no expuesto por la UI pública", "period_or_date": "2009-2012", "identifiers": "Res211/2009;Res44/2010;Act426/09;Act466/09", "minimum_usable_fields": "serie;caja;legajo;soporte;estado de conservación", "confidentiality_fallback": "certificación de búsqueda y ruta de transferencia", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR135_111", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / TGN / CGN", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Extracto SDPGB por beneficiario o sucesor 2008", "period_or_date": "2008", "identifiers": "OB SIDIF 71597;152677;2876;SDPGBXXX.CON", "minimum_usable_fields": "SAF;beneficiario;importe;estado P/R/A;fecha;banco;sucursal;tipo y número de cuenta;motivo;medio", "confidentiality_fallback": "cuadro certificado de esos campos por cada OB", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR135_112", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / TGN / CGN", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Extracto SDPAG por ítem o sucesor 2008", "period_or_date": "2008", "identifiers": "OB SIDIF 71597;152677;2876;SDPAG", "minimum_usable_fields": "SAF;ítem;importe;estado;fecha;anulación/rechazo", "confidentiality_fallback": "estado final y total por OB", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR135_113", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / TGN / BCRA", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Archivo o registro de instrucciones de pago TGN→BCRA", "period_or_date": "2008", "identifiers": "71597;152677;2876;archivo instrucciones de pago", "minimum_usable_fields": "identificador;fecha/hora;orden;importe;moneda;destino;acuse;resultado", "confidentiality_fallback": "certificación de existencia/ausencia y estado por orden", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR135_114", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / TGN / BCRA", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Archivos o registros de movimientos y saldos bancarios asociados", "period_or_date": "2008-2009", "identifiers": "71597;152677;2876;cuenta BNA/BCRA;movimiento;saldo", "minimum_usable_fields": "cuenta;fecha valor;débito/crédito;importe;moneda;referencia;saldo", "confidentiality_fallback": "movimiento certificado anonimizado salvo referencia de orden", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR135_115", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / SAF 355/356 / TGN / BNA", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Paquete de pago exterior, únicamente si alguna C-41 fue clasificada así", "period_or_date": "2008", "identifiers": "71597;152677;2876;Disposición Conjunta 47/2008-10/2008", "minimum_usable_fields": "beneficiario exterior;banco;cuenta;tipo operación;SIDIF;moneda;cotización;divisas;boleto de cambio", "confidentiality_fallback": "confirmación de no aplicabilidad por cada OB", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR135_116", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / archivo COMDOC", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Remitos e integridad material del expediente target", "period_or_date": "2008-actualidad", "identifiers": "S01:0342455/2008", "minimum_usable_fields": "remitos;firmas;fechas;cuerpos;anexos;último folio;área depositaria", "confidentiality_fallback": "certificación de custodia y último pase", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR135_117", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / archivo COMDOC", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Actuaciones de búsqueda y reconstrucción si se alega pérdida", "period_or_date": "2008-actualidad", "identifiers": "S01:0342455/2008;circular COMDOC;reconstrucción", "minimum_usable_fields": "áreas consultadas;fechas;resultados;copias certificadas;informe;acto de reconstrucción", "confidentiality_fallback": "certificación motivada del procedimiento realizado", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR135_118", "request_id": "REQ134_AGN", "institution": "Senado / Bicameral Revisora / archivo parlamentario", "gap_id": "CL134_AGN_REPLY", "requested_record": "Remitos, integridad y depósito de OV 366/09 y OV 44/10", "period_or_date": "2009-2012", "identifiers": "0366-OV-2009;0044-OV-2010;nota 18/05/2012", "minimum_usable_fields": "remito;emisor;receptor;fecha;cuerpos;anexos;último folio;caja;signatura", "confidentiality_fallback": "renglones certificados de inventario y ruta de transferencia", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR136_119", "request_id": "REQ134_ECON", "institution": "CGN / AGAN", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Búsqueda y copia de los tres cuerpos C-41 en el fondo financiero", "period_or_date": "2008-2009", "identifiers": "SIDIF71597;SIDIF152677;SIDIF2876;SAF355;SAF356;SIGADE83106000", "minimum_usable_fields": "signatura;caja;cuerpo;folios;C-41;SAF;beneficiario;concepto;importe;estado;firmas", "confidentiality_fallback": "ficha de índice y cuadro certificado por OB", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR136_120", "request_id": "REQ134_ECON", "institution": "CGN / AGAN / AMIDDF", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Índice relacional e imágenes de todos los cuerpos y anexos asociados", "period_or_date": "2008-2009", "identifiers": "71597;152677;2876;83106000;COMISIONES-BANCO NACION;ARS32270.30", "minimum_usable_fields": "identificador imagen;tipo documental;fecha;SAF;OB;expediente;cuerpo;folio;vínculo", "confidentiality_fallback": "metadatos de índice y certificación de existencia", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR136_121", "request_id": "REQ134_ECON", "institution": "CGN / TGN / AGAN", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Lista diaria impresa y firmada de órdenes seleccionadas para cancelar", "period_or_date": "2008; o equivalente contemporáneo", "identifiers": "71597;152677;2876;CUT;PAGADOR TGN", "minimum_usable_fields": "fecha;SAF;orden;beneficiario;importe;total;firmas;hora selección", "confidentiality_fallback": "renglón certificado de cada orden y norma aplicada", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR136_122", "request_id": "REQ134_ECON", "institution": "CGN / TGN / AGAN", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Autorización de pago y lista diaria si la clase de organismo lo hacía aplicable", "period_or_date": "2008; control sucesor 2009", "identifiers": "71597;152677;2876;autorización;lista diaria", "minimum_usable_fields": "ejercicio;SAF;fecha;número;beneficiario;CUIT;fuente;banco;sucursal;tipo;importe;cuenta;firmas", "confidentiality_fallback": "certificación de aplicabilidad o no aplicabilidad", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR136_123", "request_id": "REQ134_ECON", "institution": "CGN / TGN / SAF", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Historia completa de pagos parciales, saldo y caducidad por orden", "period_or_date": "2008-2010", "identifiers": "71597;152677;2876;Disposición54/2008", "minimum_usable_fields": "importe original;moneda;conformidad;cada pago y fecha;Σ pagado;saldo;caducidad;anulación", "confidentiality_fallback": "cuadro certificado con denominador, numerador y saldo", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR136_124", "request_id": "REQ134_ECON", "institution": "CGN / TGN / SAF 355/356 / BNA", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Clasificación individual exterior/no exterior de cada C-41", "period_or_date": "2008", "identifiers": "71597;152677;2876;nota TGN;boleto de cambio", "minimum_usable_fields": "tipo de operación;beneficiario;banco;cuenta;moneda;nota;boleto;fundamento de no aplicabilidad", "confidentiality_fallback": "certificación individual exterior/no exterior", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR136_125", "request_id": "REQ134_BCRA", "institution": "BCRA / CRYL / TGN", "gap_id": "CL134_CRYL_SETTLEMENT", "requested_record": "Ruta y movimientos CRYL específicos de 2008, separados de archivos bancarios generales", "period_or_date": "2008-2009", "identifiers": "CRYL;BODEN;71597;152677;2876;movimientos", "minimum_usable_fields": "sistema productor;fecha de incorporación;archivo;cuenta;especie;nominal;fecha valor;referencia", "confidentiality_fallback": "certificación de si existía recepción CRYL específica en 2008", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR136_126", "request_id": "REQ134_ECON", "institution": "CGN / Coordinación Archivo General", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Verificación del canal AGAN y derivación al custodio competente", "period_or_date": "consulta 2026-08-30", "identifiers": "mherri@mecon.gov.ar;54-11-4349-7824;AGAN;AMIDDF", "minimum_usable_fields": "vigencia;acuse;número de gestión;área;responsable;resultado", "confidentiality_fallback": "canal institucional sustituto", "status": "DRAFT_NOT_SENT"},
])
assert len(trace) == 126
write_csv(trace_path, trace)

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V136.csv"
keys = read_csv(keys_path)[:98]
keys.extend([
    {"key_id": "SK134_99", "request_id": "REQ134_ECON", "key_group": "finddoc_output_schema", "exact_key": "origen;destino;fecha envío;fecha recepción;ubicación", "search_purpose": "pedir exportación COMDOC homogénea", "source_or_basis": "Agenda Digital pp.206-207", "caveat": "No es cuerpo documental."},
    {"key_id": "SK134_100", "request_id": "REQ134_ECON", "key_group": "finddoc_endpoint", "exact_key": "http://expedientes.mecon.gov.ar/finddoc2/finddoc/VerExpediente", "search_purpose": "identificar servicio histórico exacto", "source_or_basis": "AGN 254/2013", "caveat": "Endpoint no operativo en 2026."},
    {"key_id": "SK134_101", "request_id": "REQ134_ECON", "key_group": "historic_control", "exact_key": "S01:0130656/2008;consulta05/03/2013;último pase11/06/2012", "search_purpose": "probar salida histórica y precedente de S01/2008", "source_or_basis": "AGN 254/2013 pp.93,133", "caveat": "No es el expediente target."},
    {"key_id": "SK134_102", "request_id": "REQ134_ECON", "key_group": "target_comdoc", "exact_key": "S01:0342455/2008", "search_purpose": "obtener hoja de ruta target", "source_or_basis": "Resolución conjunta 212/2008-24/2008", "caveat": "Consulta aún no ejecutada."},
    {"key_id": "SK134_103", "request_id": "REQ134_ECON", "key_group": "official_channel", "exact_key": "ciudadano@mecon.gov.ar;0810-333-6326;Balcarce186 piso1 oficina140", "search_purpose": "consulta administrativa sustitutiva", "source_or_basis": "Economía Consulta de expedientes", "caveat": "No contactado."},
    {"key_id": "SK134_104", "request_id": "REQ134_ECON", "key_group": "c41_target_ids", "exact_key": "SIDIF71597;SIDIF152677;SIDIF2876;SIGADE83106000", "search_purpose": "recuperar tres C-41 2008", "source_or_basis": "CGN 2008 Anexo K", "caveat": "No prueban vínculo con recompra."},
    {"key_id": "SK134_105", "request_id": "REQ134_ECON", "key_group": "c41_external_fields", "exact_key": "beneficiario;banco destino;cuenta;SIDIF;moneda;cotización;divisas", "search_purpose": "pedir nota/instrucción asociada si aplica", "source_or_basis": "CGN Circular 13/02", "caveat": "Aplicabilidad target abierta."},
    {"key_id": "SK134_106", "request_id": "REQ134_ECON", "key_group": "c55_reconciliation", "exact_key": "C-55;regularización;desafectación;débito BNA;documento original", "search_purpose": "cerrar diferencia orden-débito", "source_or_basis": "CGN Circular 22/04", "caveat": "No todo pago genera C-55."},
    {"key_id": "SK134_107", "request_id": "REQ134_AGN", "key_group": "bicameral_contact", "exact_key": "REVISORA@SENADO.GOB.AR;2822-3000;internos2310-2315", "search_purpose": "solicitar nota e inventario 2012", "source_or_basis": "Senado Comisión 100", "caveat": "No contactado."},
    {"key_id": "SK134_108", "request_id": "REQ134_AGN", "key_group": "mass_archive_control", "exact_key": "HCDN período130 reunión8 punto13;23/05/2012", "search_purpose": "controlar contexto de archivo masivo", "source_or_basis": "Sumario HCDN", "caveat": "No individualiza los dos OV target."},
    {"key_id": "SK135_109", "request_id": "REQ134_ECON", "key_group": "sidif_paid_file", "exact_key": "SDPGBXXX.CON;Pago a Beneficiarios/Deducciones", "search_purpose": "localizar salida por beneficiario", "source_or_basis": "Anexo Circular CGN 34/97", "caveat": "Pedir sucesor equivalente si el nombre cambió en 2008."},
    {"key_id": "SK135_110", "request_id": "REQ134_ECON", "key_group": "sidif_item_file", "exact_key": "SDPAG;pagado por ítem", "search_purpose": "localizar salida diaria por ítem", "source_or_basis": "Circular TGN 7/97", "caveat": "Continuidad literal a 2008 abierta."},
    {"key_id": "SK135_111", "request_id": "REQ134_ECON", "key_group": "sidif_state_codes", "exact_key": "P=Pagado;R=Rechazado;A=Anulado", "search_purpose": "distinguir estado efectivo", "source_or_basis": "Anexo Circular CGN 34/97", "caveat": "Código target no recuperado."},
    {"key_id": "SK135_112", "request_id": "REQ134_ECON", "key_group": "sidif_payment_media", "exact_key": "RN=Red bancaria;CH=Cheque;TR=Transferencia CUT;TI=Títulos;NS=Nota", "search_purpose": "identificar medio de pago", "source_or_basis": "Anexo Circular CGN 34/97", "caveat": "Medio target abierto."},
    {"key_id": "SK135_113", "request_id": "REQ134_ECON", "key_group": "sidif_order_numbers", "exact_key": "OB71597;OB152677;OB2876", "search_purpose": "consultar tres filas exactas", "source_or_basis": "CGN 2008 Anexo K, alineación visual", "caveat": "Son comisiones BNA, no pago confirmado."},
    {"key_id": "SK135_114", "request_id": "REQ134_ECON", "key_group": "anexo_k_account", "exact_key": "SIGADE83106000;COMISIONES-BANCO NACION;ARS32270.30", "search_purpose": "evitar corrimiento de renglón", "source_or_basis": "CGN 2008 Anexo K renderizado", "caveat": "No atribuye recompra."},
    {"key_id": "SK135_115", "request_id": "REQ134_ECON", "key_group": "tgn_bcra_system_file", "exact_key": "archivo de instrucciones de pago TGN-BCRA", "search_purpose": "localizar instrucción electrónica 2008", "source_or_basis": "Cuenta de Inversión 2008 Tomo II", "caveat": "Clase general, vínculo target abierto."},
    {"key_id": "SK135_116", "request_id": "REQ134_ECON", "key_group": "tgn_bcra_return_files", "exact_key": "archivo de movimientos;archivo de saldos;cuentas bancarias", "search_purpose": "cerrar huella bancaria", "source_or_basis": "Cuenta de Inversión 2008 Tomo II", "caveat": "Clases generales, registros target abiertos."},
    {"key_id": "SK135_117", "request_id": "REQ134_ECON", "key_group": "external_payment_2008", "exact_key": "Transferencia al exterior;Apertura de Carta de Crédito;SAF355;SAF356", "search_purpose": "probar o descartar aplicabilidad", "source_or_basis": "Disposición Conjunta CGN47/TGN10 de 2008", "caveat": "No asumir que las tres órdenes fueron exteriores."},
    {"key_id": "SK135_118", "request_id": "REQ134_ECON", "key_group": "external_payment_note", "exact_key": "beneficiario;banco destino;cuenta;SIDIF;moneda;cotización;divisas;Boleto de Venta de Cambio", "search_purpose": "recuperar paquete exterior si aplica", "source_or_basis": "Disposición Conjunta CGN47/TGN10 de 2008", "caveat": "Condicional."},
    {"key_id": "SK135_119", "request_id": "REQ134_ECON", "key_group": "comdoc_custody", "exact_key": "dos remitos;cuerpos;anexos;último folio;área depositaria", "search_purpose": "probar custodia e integridad", "source_or_basis": "Resolución MINPLAN 1522/2006 actualizada", "caveat": "Comparador contemporáneo, no regla target automática."},
    {"key_id": "SK135_120", "request_id": "REQ134_ECON", "key_group": "comdoc_loss_reconstruction", "exact_key": "búsqueda intensiva;circular COMDOC;copias certificadas;informe explicativo;reconstrucción", "search_purpose": "controlar alegación de pérdida", "source_or_basis": "Resolución MINPLAN 1522/2006 actualizada", "caveat": "Comparador de clases documentales."},
    {"key_id": "SK135_121", "request_id": "REQ134_ECON", "key_group": "debt_instruction_comparator", "exact_key": "nota conjunta ONCP-TGN;archivo de datos;validación;aceptación Caja;registro SIGADE", "search_purpose": "buscar clases análogas de instrucción/aceptación", "source_or_basis": "Resolución Conjunta 216/2008 y 26/2008", "caveat": "Operatoria de consolidación, no recompra target."},
    {"key_id": "SK135_122", "request_id": "REQ134_AGN", "key_group": "hcdn_index_negative_control", "exact_key": "0366-OV-2009;366-OV-2009;0044-OV-2010;44-OV-2010;366/09;44/10", "search_purpose": "repetir búsqueda archivística con variantes exactas", "source_or_basis": "Índice histórico HCDN", "caveat": "Sin coincidencias sólo en el índice público."},
    {"key_id": "SK136_123", "request_id": "REQ134_ECON", "key_group": "financial_archive", "exact_key": "Archivo General de Administración Nacional;AGAN;AMIDDF", "search_purpose": "dirigir búsqueda al custodio financiero", "source_or_basis": "páginas oficiales AGAN/AMIDDF", "caveat": "Ruta probada; holdings target abiertos."},
    {"key_id": "SK136_124", "request_id": "REQ134_ECON", "key_group": "agan_target_bundle", "exact_key": "SIDIF71597;SIDIF152677;SIDIF2876;SAF355;SAF356;83106000;ARS32270.30", "search_purpose": "recuperar originales, imágenes e índice", "source_or_basis": "Anexo K + AGAN/AMIDDF", "caveat": "El importe es agregado del renglón."},
    {"key_id": "SK136_125", "request_id": "REQ134_ECON", "key_group": "agan_index_fields", "exact_key": "signatura;caja;cuerpo;folio;tipo documental;imagen;expediente;SAF;OB", "search_purpose": "pedir salida archivística verificable", "source_or_basis": "AMIDDF", "caveat": "No presupone digitalización target."},
    {"key_id": "SK136_126", "request_id": "REQ134_ECON", "key_group": "daily_selected_order_list", "exact_key": "lista diaria impresa;órdenes seleccionadas;CUT;PAGADOR TGN;firma responsable", "search_purpose": "localizar selección previa al pago", "source_or_basis": "Disposición Conjunta CGN13/TGN16 de 2009", "caveat": "Sucesor/comparador; aplicabilidad 2008 abierta."},
    {"key_id": "SK136_127", "request_id": "REQ134_ECON", "key_group": "payment_authorization_fields", "exact_key": "ejercicio;SAF;fecha;autorización;beneficiario;CUIT;fuente;banco;sucursal;R/B;importe;cuenta", "search_purpose": "recuperar autorización o certificar no aplicabilidad", "source_or_basis": "Disposición Conjunta CGN13/TGN16 de 2009", "caveat": "Depende de la clase del organismo."},
    {"key_id": "SK136_128", "request_id": "REQ134_ECON", "key_group": "partial_payment_state", "exact_key": "importe original;conformidad;pagos parciales;Σpagado;saldo;caducidad;anulación", "search_purpose": "distinguir pago total, parcial y no pago", "source_or_basis": "Disposición CGN 54/2008", "caveat": "P/R/A aislado puede ser insuficiente."},
    {"key_id": "SK136_129", "request_id": "REQ134_ECON", "key_group": "legacy_sidif_environment", "exact_key": "SIDIF Central;TRANSAF;e-SIDIF Gastos;Pagos Etapa 1;Pagos Etapa 2", "search_purpose": "identificar sistema productor correcto", "source_or_basis": "Circular 07/08 + Cuentas 2008-2011", "caveat": "No prueba nombre literal de archivo 2008."},
    {"key_id": "SK136_130", "request_id": "REQ134_ECON", "key_group": "external_classification", "exact_key": "clasificación exterior/no exterior;observaciones C-41;nota TGN;Boleto de Venta de Cambio", "search_purpose": "aplicar o descartar paquete exterior por OB", "source_or_basis": "Disposición Conjunta 47/10 de 2008", "caveat": "No inferir desde 'Comisiones Banco Nación'."},
    {"key_id": "SK136_131", "request_id": "REQ134_BCRA", "key_group": "cryl_temporal_control", "exact_key": "recepción movimientos CRYL;incorporación 2009;archivo específico 2008", "search_purpose": "separar retorno bancario general de CRYL", "source_or_basis": "Cuenta de Inversión 2009", "caveat": "Ruta 2008 no probada."},
    {"key_id": "SK136_132", "request_id": "REQ134_ECON", "key_group": "agan_published_contact", "exact_key": "mherri@mecon.gov.ar;54-11-4349-7824", "search_purpose": "verificar canal antes de presentación", "source_or_basis": "página oficial Coordinación Archivo General", "caveat": "Página posiblemente legada; no contactado."},
])
assert len(keys) == 132
write_csv(keys_path, keys)

agn_request = HERE / "REQUEST_AGN_2018_REPLY_V136.md"
agn_request.write_text(agn_request.read_text(encoding="utf-8-sig").rstrip() + """

## Clave V136 · inventario público y nota de archivo

La interfaz pública actual de la Comisión no expone, entre la documentación visible revisada, la nota de archivo del `18/05/2012` ni su inventario. El sumario de Diputados del `23/05/2012` prueba un contexto de archivo masivo de expedientes de la Revisora, pero no individualiza `OV 366/09` ni `OV 44/10`; no se lo presenta como disposición de estos casos. Tampoco se hallaron las variantes `0366-OV-2009`, `366-OV-2009`, `0044-OV-2010`, `44-OV-2010`, `366/09` o `44/10` en el índice histórico público de reuniones: es un control negativo limitado, no una afirmación de inexistencia.

Se solicita búsqueda en el fondo histórico por ambos OV, resoluciones y actuaciones AGN, y copia de la nota, remito, inventario, depósito y signatura. Para controlar custodia e integridad, se piden emisor, receptor, firma, fecha, número de cuerpos, anexos, último folio, caja y signatura; si se alegara pérdida, también las actuaciones de búsqueda y reconstrucción que resulten aplicables. Contacto público identificado: `REVISORA@SENADO.GOB.AR`, internos `2310-2315`. Estado: **BORRADOR_NO_ENVIADO**.
""", encoding="utf-8")

econ_request = HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V136.md"
econ_request.write_text(econ_request.read_text(encoding="utf-8-sig").rstrip() + """

## Clave V136 · AGAN/AMIDDF, sistema productor y pago parcial

La cronología oficial 2008-2011 ubica las tres órdenes en el entorno legacy de `SIDIF Central` con transmisión `TRANSAF`: en 2008 se sustituyó sólo el módulo Entes; `Pagos Etapa 1 y Gastos` aparece en mayo de 2009, la carga C-41/C-42 en mayo de 2010 y la primera versión de Gastos en SAF 356 en 2011. Esto permite pedir `SDPGB`/`SDPAG` o la salida funcional sucesora del SIDIF Central. No se afirma que el nombre literal de los archivos haya permanecido idéntico hasta 2008.

El custodio directo identificado es el Archivo General de Administración Nacional (`AGAN`) y su sistema `AMIDDF`, que reciben, ordenan, custodian, describen y digitalizan documentación financiera respaldatoria y originales en papel originados en movimientos de fondos de los SAF. Por `71597`, `152677` y `2876`, cuenta `83106000`, renglón `COMISIONES - BANCO NACION` e importe agregado `ARS 32.270,30`, se solicitan ficha de índice, signatura, caja, cuerpo, folios, imágenes y copia de todos los anexos: C-41 original, notas, lista diaria firmada de selección, autorizaciones si correspondían, boletos, débitos, C-55 y demás respaldos. La competencia general del archivo no se presenta como prueba de que esas piezas concretas ya hayan sido localizadas.

La Disposición CGN 54/2008 obliga a separar pago total de pago parcial: para cada OB se requieren importe original y moneda, fecha de conformidad, cada pago y fecha, suma acumulada, saldo, caducidad, anulación o reversa. Un estado `P` aislado no se considerará prueba suficiente de cancelación total. La Disposición Conjunta CGN 13/2009-TGN 16/2009 se usa sólo como sucesor/comparador inmediato para identificar copia papel, listas diarias firmadas y autorizaciones; no se retroproyecta automáticamente a 2008.

Si alguna orden fue un pago exterior, se solicita el paquete correspondiente; si no, certificación individual de no aplicabilidad. La incorporación expresa en 2009 de recepción de movimientos `CRYL` impide confundir sin prueba esos archivos específicos con los movimientos bancarios generales documentados para 2008. Contacto AGAN publicado: `mherri@mecon.gov.ar`, `54-11-4349-7824`; su vigencia no fue verificada y no fue contactado. Estado: **BORRADOR_NO_ENVIADO**.
""", encoding="utf-8")

# Síntesis del checkpoint.
(HERE / "README_V136.md").write_text("""# V136 · SIDIF legacy, AGAN y pagos parciales

V136 prueba que el entorno de las órdenes de 2008 era `SIDIF Central`/`TRANSAF`, anterior al despliegue documentado de e-SIDIF Gastos. Esto fortalece la búsqueda funcional de `SDPGB/SDPAG` sin afirmar continuidad literal del nombre. Identifica además a `AGAN/AMIDDF` como ruta directa de originales, índices e imágenes de documentación financiera de los SAF. La regla exacta de 2008 agrega el estado de pago parcial antes de caducidad: hay que obtener importe original, movimientos acumulados y saldo, no sólo `P/R/A`. El paquete papel y las listas diarias de 2009 son comparadores sucesores, no reglas retroactivas. Resultado estricto sin cambio: 10/10 adjudicaciones, 9/10 cuentas candidatas y 0/10 ejecuciones confirmadas; seis pedidos DRAFT_NOT_SENT.
""", encoding="utf-8")

(HERE / "VEREDICTO_V136.md").write_text("""# Veredicto V136

La secuencia oficial corrige una ambigüedad central: en 2008 e-SIDIF no tenía desplegado el módulo Gastos que luego procesaría C-41/C-42; el target pertenece al entorno legacy `SIDIF Central`/`TRANSAF`. La continuidad funcional de las salidas de pago queda fuertemente respaldada, pero el nombre literal `SDPGB/SDPAG` en 2008 sigue abierto.

La ruta probatoria ya no depende sólo de COMDOC. `AGAN` conserva documentación respaldatoria financiera de los SAF y `AMIDDF` relaciona originales en papel, imágenes y registros identificatorios, incluso cuerpos de expedientes. Es el custodio directo al que debe pedirse la ficha, signatura, cuerpo, folios e imágenes de `71597`, `152677` y `2876`; todavía no hubo consulta ni hallazgo target.

La Disposición 54/2008 demuestra que una orden podía recibir pagos parciales antes de caducar. Por eso `P/R/A` no cierra por sí solo la ejecución: hacen falta importe original, cada pago, suma acumulada y saldo. El paquete papel/lista diaria documentado en 2009 se conserva como comparador sucesor. La recepción de movimientos CRYL aparece como incorporación en 2009, por lo que no se etiqueta retroactivamente como CRYL el archivo bancario general de 2008.

La clasificación exterior de las tres órdenes sigue abierta y no se infiere desde `COMISIONES - BANCO NACION`. La ejecución permanece en 0/10; seis borradores, ninguno enviado.
""", encoding="utf-8")

(HERE / "E0_FISCAL_RECONSTRUCTION_V136.md").write_text("""# Reconstrucción fiscal E0 · V136

## Resultado incremental

1. La cronología 2008-2011 ubica el target en `SIDIF Central` legacy y el despliegue de e-SIDIF Gastos después de 2008.
2. `SDPGB/SDPAG` o su sucesor funcional sigue siendo la salida a pedir; el nombre literal 2008 no se da por probado.
3. `AGAN/AMIDDF` es la ruta directa para originales, índices, imágenes, cuerpos y anexos de documentación financiera SAF.
4. La historia mínima por OB ahora incluye importe original, conformidad, pagos parciales, suma pagada, saldo y caducidad.
5. La copia papel, lista diaria firmada y autorización se piden como clases documentales comparables, con la regla 2009 marcada como sucesora.
6. La clasificación exterior debe probarse individualmente; Banco Nación no basta.
7. La incorporación CRYL documentada en 2009 no se proyecta a 2008.
8. Transferencia Caja, informe T+3, crédito BCRA y cancelación CRYL siguen abiertos: 0/10 ejecuciones confirmadas.
""", encoding="utf-8")

(HERE / "RETRIEVAL_LOG_V136.md").write_text("""# Registro de recuperación V136

Fecha: 2026-08-30.

1. Se preservaron cinco controles oficiales 2008-2011 y se reconstruyó la transición `SIDIF Central`→e-SIDIF Gastos.
2. La Circular 07/08 prueba el reemplazo de Entes y continuidad de diseños TRANSAF sólo en ese módulo; no prueba el nombre literal de archivos de pago.
3. La Cuenta 2009 ubica Pagos/Gastos después del target y documenta como incorporación la recepción de movimientos CRYL.
4. Se preservaron la Disposición CGN 20/2007 y las páginas AGAN/AMIDDF: ruta directa para respaldo financiero, originales, imágenes e índices.
5. Se preservó la Disposición CGN 54/2008: caducidad y excepción por pagos parciales.
6. Se preservó la Disposición Conjunta CGN 13/2009-TGN 16/2009: copia papel, listas diarias firmadas y autorizaciones, usada sólo como sucesor/comparador.
7. Se preservó el contacto oficial publicado de AGAN; su vigencia no se verificó y no fue utilizado.
8. No se localizaron cuerpos, imágenes, estados o pagos target; no se envió ningún pedido ni presentación externa.
""", encoding="utf-8")

refs_path = HERE / "SOURCE_REFERENCES_V136.md"
refs_path.write_text(refs_path.read_text(encoding="utf-8-sig").rstrip() + """

- CGN · Archivo General de Administración Nacional: https://www.argentina.gob.ar/economia/sechacienda/cgn/archivogeneral
- CGN · AMIDDF: https://www.argentina.gob.ar/economia/administracionfinancieragubernamental/otrossistemas/amiddf
- CGN · Circular 07/2008, Entes/TRANSAF: https://www.economia.gob.ar/hacienda/cgn/normas/circulares/2008/cir07.htm
- CGN · Cuenta de Inversión 2008, Jurisdicción 50: https://www.economia.gob.ar/hacienda/cgn/cuenta/2008/tomoii/11jur50.htm
- CGN · Cuenta de Inversión 2009, aspectos metodológicos: https://www.economia.gob.ar/hacienda/cgn/cuenta/2009/tomoi/03aspectos.htm
- CGN · Cuenta de Inversión 2010, aspectos metodológicos: https://www.economia.gob.ar/hacienda/cgn/cuenta/2010/tomoi/03aspectos.htm
- CGN · Cuenta de Inversión 2011, Jurisdicción 50: https://www.economia.gob.ar/hacienda/cgn/cuenta/2011/tomoii/jur50.htm
- CGN · Disposición 20/2007, AGAN: https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/2007/Disp20.htm
- CGN · Disposición 54/2008, caducidad y pagos parciales: https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/2008/disp54/disp54.htm
- CGN/TGN · Disposición Conjunta 13/2009 y 16/2009: https://www.economia.gob.ar/hacienda/cgn/normas/disposiciones/2009/disp13.htm
- CGN · Coordinación Archivo General: https://www.economia.gob.ar/hacienda/cgn/competencia/archivo.htm

La cronología identifica el sistema productor y el archivo competente; las tres historias de pago y sus respaldos siguen sin recuperarse.
""", encoding="utf-8")

handover = """# Handover V136 → V137

## Estado congelado

- Diez adjudicaciones participante-instrumento exactas; nueve cuentas BCRA candidatas; MERVAL abierta; 0/10 ejecuciones confirmadas.
- Alineación visual exacta: cuenta `83106000`, Banco Nación, ARS 32.270,30, SIDIF `71597`, `152677`, `2876`; el corrimiento de snippet es falso.
- Esquema `SDPGB/SDPAG`: identidad OB, beneficiario, importe, `P/R/A`, fecha, banco, cuenta y medio; filas target no localizadas.
- Sistema 2008: clases de archivo de instrucción TGN→BCRA, movimientos y saldos BCRA→TGN probadas; vínculos target abiertos.
- Entorno productor 2008: SIDIF Central/TRANSAF legacy probado; e-SIDIF Gastos se despliega después; nombre literal SDPGB/SDPAG 2008 abierto.
- AGAN/AMIDDF: custodio directo de respaldo financiero, originales, índices e imágenes probado; holdings target no consultados.
- Pago parcial: regla exacta 2008 probada; exigir importe original, pagos acumulados, saldo y caducidad.
- Paquete papel/listas firmadas: esquema sucesor 2009 probado, sin retroproyección automática a 2008.
- CRYL: recepción de movimientos documentada como incorporación en 2009; ruta específica 2008 abierta.
- Pago exterior: paquete documental exacto probado en 2008, sólo condicional a clasificación SAF 355/356.
- COMDOC/deuda: comparadores de remito, folios, búsqueda/reconstrucción, nota, aceptación y SIGADE; no equivalencia target.
- Bicameral: seis variantes exactas de los dos OV sin coincidencia en el índice HCDN; nota 18/05/2012 abierta.
- Seis pedidos DRAFT_NOT_SENT; ninguno enviado; panel estricto sin cambios.

## Prioridad V137

1. Si hay autorización expresa, presentar los seis pedidos; si no, mantenerlos como borradores.
2. Priorizar búsqueda AGAN/AMIDDF por OB `71597`, `152677`, `2876`, cuenta `83106000`, SAF, renglón e importe agregado.
3. Obtener extracto SIDIF Central, estado, importe original, todos los pagos parciales y saldo por OB.
4. Buscar copia papel C-41, lista diaria firmada, autorización si aplica, instrucción TGN→BCRA y movimiento bancario target.
5. Probar o descartar clasificación exterior de cada orden antes de aplicar la Disposición 47/10.
6. Verificar si existía ruta CRYL específica en 2008; no sustituirla por movimientos BCRA generales.
7. Mantener separados orden, selección, pago parcial, pago total, Caja, crédito BCRA y cancelación CRYL.
"""
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V136_A_V137.md").write_text(handover, encoding="utf-8")

(HERE / "AUDITORIA_V136.md").write_text(f"""# Auditoría V136

- Fuentes maestras: {len(catalog)}; once fuentes oficiales nuevas preservadas.
- Fuentes primarias E0: {len(census)}.
- Ledger fiscal: {len(ledger)} filas; cortes metodológicos: {len(breaks)}.
- FindDoc: 5 controles de capacidad/salida/target; target sin consulta ejecutada.
- C-41/estado: {len(c41_chain)} etapas; esquema `P/R/A`, pago parcial y ruta archivística probados; filas target abiertas.
- Controles nuevos: {len(sidif_timeline)} hitos SIDIF/e-SIDIF, {len(agan_route)} rutas AGAN/AMIDDF, {len(daily_records)} registros diarios, {len(partial_state)} estados parciales y {len(external_classification)} clasificaciones target.
- Bicameral: {len(bicameral)} controles; nota exacta e inventario abiertos.
- Escalera: 10 adjudicaciones; 9 cuentas candidatas; 0 ejecuciones confirmadas.
- Pedidos: 6 borradores, 0 enviados; {len(trace)} objetos y {len(keys)} claves.
- Panel estricto: 30 entidades; {STRICT}% sin cambios.
""", encoding="utf-8")

# Auditoría física y estado global.
for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    shutil.copyfile(AUDIT / f"{stem}_V135.csv", AUDIT / f"{stem}_V136.csv")

hash_rows = []
for row in catalog:
    local = row["archivo_local"]
    path = REPO / local.lstrip("/") if local else None
    exists = bool(path and path.is_file())
    actual = sha256(path) if exists else ""
    expected = row["sha256"]
    hash_rows.append({"id": row["id"], "archivo_local": local, "exists": str(exists), "sha_catalog": expected, "sha_actual": actual, "hash_ok": str(bool(exists and expected and actual.lower() == expected.lower()))})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V136.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V136.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
assert physical == hash_ok == 382

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or "tmp" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": str(size), "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V136.csv", size_rows)

completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V135.json").read_text(encoding="utf-8"))
for key in list(completeness):
    if key.endswith("_v135") or "newly_preserved_v135" in key:
        completeness.pop(key, None)
completeness.update({
    "checkpoint": "V136", "date": "2026-08-30",
    "state": "E0_2008_LEGACY_SIDIF_AGAN_AND_PARTIAL_PAYMENT_RULE_PROVED_TARGET_RECORDS_OPEN_NOT_SENT",
    "numeric_v136_strict_changed": False, "master_catalog_entries": len(catalog),
    "physical_local_copies": physical, "physical_local_hash_ok": hash_ok,
    "e0_primary_sources_preserved": len(census), "e0_quality": "PRIMARY_SYSTEM_CHRONOLOGY_FINANCIAL_ARCHIVE_AND_PARTIAL_PAYMENT_CONTROLS",
    "sources_newly_preserved_v136": 11, "e0_primary_sources_newly_preserved_v136": 11,
    "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
    "e0_request_traceability_rows": len(trace), "e0_request_search_keys": len(keys),
    "e0_finddoc_capability_rows": len(finddoc), "e0_finddoc_target_query_executed": False,
    "e0_c41_chain_rows": len(c41_chain), "e0_c41_target_ids": 3, "e0_c41_target_bodies_located": 0,
    "e0_c41_target_payment_state_rows_located": 0,
    "e0_anexo_k_visual_alignment_rows": len(anexo_k_alignment),
    "e0_sidif_payment_state_schema_rows": len(payment_state_schema),
    "e0_tgn_bcra_2008_record_class_rows": len(tgn_system_records),
    "e0_sidif_esidif_timeline_rows": len(sidif_timeline),
    "e0_agan_archival_route_rows": len(agan_route),
    "e0_daily_payment_record_rows": len(daily_records),
    "e0_partial_payment_state_rows": len(partial_state),
    "e0_external_classification_rows": len(external_classification),
    "e0_agan_target_holdings_located": 0,
    "e0_2008_legacy_sidif_environment_proved": True,
    "e0_2008_sdpgb_sdpag_literal_filename_proved": False,
    "e0_cryl_specific_2008_movement_route_proved": False,
    "e0_comdoc_custody_comparator_rows": len(comdoc_custody),
    "e0_bicameral_inventory_control_rows": len(bicameral), "e0_bicameral_exact_note_body_located": False,
    "e0_settlement_award_rows_exact": 10, "e0_settlement_account_candidate_rows": 9,
    "e0_settlement_executed_rows_confirmed": 0, "e0_requests_submitted": 0,
    "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
    "historical_workstream": "2008 legacy SIDIF Central environment, later e-SIDIF Gastos rollout, AGAN/AMIDDF direct custodian route and partial-payment state rule proved; literal 2008 output filename, target bodies/images/history, external classification, CRYL-specific route and executed settlement remain open; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V136.json").write_text(json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V136 · SIDIF legacy, AGAN y pagos parciales"
text = backup.read_text(encoding="utf-8-sig")
if marker not in text:
    text += f"\n\n{marker}\n\n- Cronología oficial: target 2008 en SIDIF Central/TRANSAF; e-SIDIF Gastos desplegado después.\n- AGAN/AMIDDF identificado como custodio directo de respaldo financiero, originales, imágenes e índices; holdings target abiertos.\n- Regla exacta 2008 de pagos parciales: exigir importe original, pagos acumulados, saldo y caducidad.\n- Paquete papel/listas de 2009 usado sólo como sucesor comparador; recepción CRYL 2009 no retroproyectada.\n- Escalera sin cambio: 10 adjudicaciones, 9 cuentas candidatas, 0 ejecuciones confirmadas; seis borradores no enviados.\n"
    backup.write_text(text, encoding="utf-8")

inherited = [
    {"script": "qa_v135.py", "pre_v136_result": "PASS", "post_v136_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V135 queda supersedido por nuevas fuentes y conteos V136."},
    {"script": "qa_v136.py", "pre_v136_result": "N/A", "post_v136_result": "PASS", "interpretation": "Cronología SIDIF, AGAN/AMIDDF, pago parcial, controles temporales, hashes y no ejecución verificados."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V136.csv", inherited)

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

finddoc = rows("E0_COMDOC_FINDDOC_CAPABILITY_V136.csv")
assert len(finddoc) == 5 and finddoc[-1]["status"] == "TARGET_QUERY_UNEXECUTED_ADMINISTRATIVE_EXPORT_REQUIRED"
assert "origen" in finddoc[1]["output_schema"] and "fecha de recepción" in finddoc[1]["output_schema"]
comdoc = rows("E0_COMDOC_LEGACY_QUERY_ROUTE_V136.csv")
assert len(comdoc) == 5 and comdoc[-1]["body_query_executed"] == "NO"

c41 = rows("E0_C41_PAYMENT_EXECUTION_CHAIN_V136.csv")
assert len(c41) == 17 and c41[0]["stage"] == "C41_ISSUED" and c41[-1]["target_status"] == "OPEN"
assert "71597" in c41[-1]["required_or_visible_fields"]
bicameral = rows("E0_BICAMERAL_PUBLIC_INVENTORY_AUDIT_V136.csv")
assert len(bicameral) == 7 and bicameral[-1]["status"] == "CONTEMPORANEOUS_CUSTODY_COMPARATOR_NOT_TARGET_RULE"

alignment = rows("E0_2008_ANEXO_K_VISUAL_ALIGNMENT_CONTROL_V136.csv")
assert len(alignment) == 4 and alignment[1]["sidif_ids"] == "71597;152677;2876"
assert alignment[2]["sidif_ids"] == "171761"
payment = rows("E0_SIDIF_PAID_BENEFICIARY_FILE_SCHEMA_V136.csv")
assert len(payment) == 8 and payment[2]["field_or_code"] == "P;R;A"
records = rows("E0_TGN_BCRA_2008_PAYMENT_RECORD_CLASSES_V136.csv")
assert len(records) == 6 and records[0]["direction"] == "TGN→BCRA"
custody = rows("E0_COMDOC_CUSTODY_AND_DEBT_INSTRUCTION_COMPARATOR_V136.csv")
assert len(custody) == 8 and custody[-1]["scope_status"] == "OTHER_DEBT_PROCEDURE_COMPARATOR"

timeline = rows("E0_SIDIF_ESIDIF_TEMPORAL_DEPLOYMENT_V136.csv")
assert len(timeline) == 11 and timeline[-1]["inference_status"].endswith("LITERAL_FILENAME_OPEN")
agan = rows("E0_AGAN_C41_ARCHIVAL_ROUTE_V136.csv")
assert len(agan) == 8 and agan[-1]["status"] == "PUBLISHED_CONTACT_NOT_VERIFIED_NOT_CONTACTED"
daily = rows("E0_DAILY_PAYMENT_SELECTION_RECORDS_V136.csv")
assert len(daily) == 7 and daily[-1]["temporal_status"].endswith("NON_REPEAL_ONLY")
partial = rows("E0_C41_PARTIAL_PAYMENT_EXPIRY_STATE_V136.csv")
assert len(partial) == 5 and partial[-1]["status"] == "REQUIRED_TO_CLOSE_EXECUTION"
external = rows("E0_C41_EXTERNAL_CLASSIFICATION_V136.csv")
assert len(external) == 4 and all(r["classification"] in {"OPEN", "EXTERNAL_PAYMENT_CLASSIFICATION_OPEN"} for r in external)

assert len(rows("E0_EXPEDIENT_PUBLIC_SEARCH_EXHAUSTION_V136.csv")) == 16
assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V136.csv")) == 172
assert len(rows("E0_FISCAL_METHOD_BREAKS_V136.csv")) == 133
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V136.csv")) == 126
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V136.csv")) == 132
ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V136.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V136.csv")}
new_ids = {"e0_agan_current_archive_services", "e0_amiddf_financial_document_images", "e0_cgn_circular_07_2008_transaf_entes_transition", "e0_cgn_account_2008_esidif_module_scope", "e0_cgn_account_2009_esidif_payments_development", "e0_cgn_account_2010_esidif_spending_rollout", "e0_cgn_account_2011_esidif_saf356_first_spending", "e0_cgn_disposition_20_2007_agan_quality", "e0_cgn_disposition_54_2008_order_expiry_partial", "e0_cgn_tgn_joint_disposition_13_16_2009_payment_records", "e0_agan_current_coordination_contact"}
assert len(census) == 148 and new_ids <= set(census)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 388 and len({r["id"] for r in catalog}) == 388

expected = {
    "argentina_agan_archivo_general_actual.html": (34804, "f2077fcaf5b8aa354ff64871e8a14cad8af069053d6562de1975e60328df6c51"),
    "argentina_amiddf_imagenes_documentacion_financiera.html": (43313, "2a82c85ded72c4a008463646d205d8e702227390d46c9b768c186c5ca804a692"),
    "cgn_circular_07_2008_transaf_entes.html": (17653, "abc3bacbef9b4d86adebc41256c7513fce69a841f6aa35228c27e44621c2f108"),
    "cgn_cuenta_2008_jur50_esidif_modules.html": (569635, "ce9f5e48de18c4aff2664afc368e71fea2f200507f93c03666dd4cd7b6eca3ac"),
    "cgn_cuenta_2009_aspectos_esidif_pagos.html": (55544, "2318e0f7dfb633f568b6f8dc589b03665846aec8e07caab2079783465ff4f5a0"),
    "cgn_cuenta_2010_aspectos_esidif_gastos.html": (58482, "d0959a23bf1fd016f5ed38d07403201826b634613e55e4910680ab7c06848fc1"),
    "cgn_cuenta_2011_jur50_esidif_gastos_saf356.html": (198342, "0e56b77da1c227d45e5850ff75efe65e08d5a030dcd6b3f1d4ae9c8fc9610754"),
    "cgn_disposicion_20_2007_agan_archivo_financiero.html": (15590, "fa157d8fe62b982b6d6e3df0a485462fe53e574f79fbfde577223d79c1a0d300"),
    "cgn_disposicion_54_2008_caducidad_ordenes.html": (37565, "cd3fb95b812bca412c07cfe9de72bbb29bca7f0c1ed2c35c6ff8adec2450497f"),
    "cgn_tgn_disposicion_13_16_2009_ordenes_pago.html": (13664, "42292773a13c2e42cfd4aa6c8652d47a8c95137429192fc65a52f4a56b9b4237"),
    "economia_agan_competencia_contacto.html": (3454, "01986c35b5439694cff2e793fa658141c47f0484a0154dc43aedd2afa366669d"),
}
bin_dir = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v136" / "binaries"
assert len(list(bin_dir.iterdir())) == 11
for name, (size, digest) in expected.items():
    path = bin_dir / name
    assert path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest() == digest

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V136.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V136"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 382
assert complete["e0_c41_target_payment_state_rows_located"] == 0
assert complete["e0_sidif_payment_state_schema_rows"] == 8
assert complete["e0_sidif_esidif_timeline_rows"] == 11
assert complete["e0_agan_archival_route_rows"] == 8
assert complete["e0_agan_target_holdings_located"] == 0
assert complete["e0_2008_legacy_sidif_environment_proved"] is True
assert complete["e0_2008_sdpgb_sdpag_literal_filename_proved"] is False
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v136_strict_changed"] is False

for name, marker in {
    "REQUEST_AGN_2018_REPLY_V136.md": "## Clave V136 · inventario público y nota de archivo",
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V136.md": "## Clave V136 · AGAN/AMIDDF, sistema productor y pago parcial",
}.items():
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert marker in text and "BORRADOR_NO_ENVIADO" in text

for name in ("README_V136.md", "VEREDICTO_V136.md", "E0_FISCAL_RECONSTRUCTION_V136.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V136_A_V137.md"):
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")

print("V136 QA PASS")
'''
(HERE / "qa_v136.py").write_text(qa, encoding="utf-8")

def checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V136.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V136", "parent_checkpoint": "V135",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": 11, "new_primary_sources": 11,
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks),
        "finddoc_capability_rows": len(finddoc), "finddoc_target_query_executed": False,
        "c41_chain_rows": len(c41_chain), "c41_target_ids": 3, "c41_target_bodies_located": 0,
        "c41_target_payment_state_rows_located": 0,
        "anexo_k_visual_alignment_rows": len(anexo_k_alignment),
        "sidif_payment_state_schema_rows": len(payment_state_schema),
        "tgn_bcra_2008_record_class_rows": len(tgn_system_records),
        "sidif_esidif_timeline_rows": len(sidif_timeline),
        "agan_archival_route_rows": len(agan_route),
        "daily_payment_record_rows": len(daily_records),
        "partial_payment_state_rows": len(partial_state),
        "external_classification_rows": len(external_classification),
        "agan_target_holdings_located": 0,
        "comdoc_custody_comparator_rows": len(comdoc_custody),
        "bicameral_control_rows": len(bicameral), "bicameral_exact_note_body_located": False,
        "award_rows_exact": 10, "account_candidate_rows": 9, "executed_settlement_rows_confirmed": 0,
        "request_drafts": 6, "request_traceability_rows": len(trace), "request_search_keys": len(keys),
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V136.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    "checkpoint": "V136", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical copies SHA-valid; 2008 legacy SIDIF environment, AGAN/AMIDDF route and partial-payment rule proved; zero of ten executed settlement rows confirmed; six requests drafted and none submitted.",
    "historical_workstream": "Literal 2008 SDPGB/SDPAG filename, target AGAN holdings/images, payment histories, external classification, CRYL-specific route, Bicameral note and executed settlement remain open; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V136 BUILD PASS")
