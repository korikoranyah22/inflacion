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
PARENT = HERE.parent / "V133"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v134" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


SOURCES = [
    {
        "id": "e0_agenda_digital_finddoc_comdoc_architecture",
        "filename": "agenda_digital_argentina_2003_2011_br1018.pdf",
        "institution": "Jefatura de Gabinete de Ministros / Ministerio de Economía",
        "title": "Modelo Social de la Agenda Digital Argentina 2003-2011 · arquitectura FindDoc/COMDOC",
        "url": "https://cdi.mecon.gob.ar/bases/docelec/br1018.pdf",
        "publication": "2011-10",
        "period": "2003-2011",
        "code": "pp.206-207; COMDOC3; FINDOC",
        "type": "PDF oficial · binario preservado",
        "bytes": 3550343,
        "sha256": "1d76b6d563aea0d6dd7fa67e22a53b36e269849b3ef6ecd0508e8e16f156d68b",
        "families": "document_management;COMDOC;FindDoc;route_metadata",
        "breaks": "hoja de ruta y ubicación versus cuerpo del expediente",
        "use": "USABLE_EXACT_FINDDOC_OUTPUT_SCHEMA",
        "caveat": "Describe origen, destino y fechas de pases; no afirma que el cuerpo documental sea descargable.",
        "note": "V134 E0: pp.206-207 verificadas visualmente; prueba arquitectura COMDOC3→FindDoc y campos públicos de hoja de ruta.",
    },
    {
        "id": "e0_agn_informe_254_2013_finddoc_control",
        "filename": "agn_informe_254_2013.pdf",
        "institution": "Auditoría General de la Nación",
        "title": "Informe de Auditoría 254/2013 · consulta FindDoc sobre expediente S01 de 2008",
        "url": "https://www.agn.gob.ar/sites/default/files/informes/Informe_254_2013.pdf",
        "publication": "2013",
        "period": "2008-2013",
        "code": "Informe 254/2013; S01:0130656/2008; pp.91,93,133",
        "type": "PDF oficial · binario preservado",
        "bytes": 23877781,
        "sha256": "99028db4627cc1190bab7d2282ae9330bca08846676b3bdf4cf4a64a969e23be",
        "families": "audit;COMDOC;FindDoc;route_metadata;historical_control",
        "breaks": "consulta de expediente de control versus consulta del expediente objetivo",
        "use": "USABLE_HISTORIC_FINDDOC_OPERATIONAL_CONTROL",
        "caveat": "La consulta documentada recae sobre S01:0130656/2008, no sobre S01:0342455/2008.",
        "note": "V134 E0: AGN documenta consulta al endpoint VerExpediente el 05/03/2013 y obtiene estado y ubicación de otro S01/2008.",
    },
    {
        "id": "e0_cgn_circular_2_1997_c41_due_date",
        "filename": "cgn_circular_2_1997_c41.html",
        "institution": "Contaduría General de la Nación",
        "title": "Circular CGN 2/97 · formulario C-41 Orden de Pago y fecha de vencimiento",
        "url": "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/1997/cir2.htm",
        "publication": "1997-02-12",
        "period": "1997",
        "code": "Circular CGN 2/97; C-41",
        "type": "HTML oficial · captura preservada",
        "bytes": 3126,
        "sha256": "52ef4c74fdd4d9ff27bb694e9b0a01e60580054df22c02574669a5c274e0da29",
        "families": "SIDIF;C41;payment_order;due_date",
        "breaks": "orden de pago versus pago ejecutado",
        "use": "USABLE_C41_DOCUMENT_CLASS_RULE",
        "caveat": "Regla general; no individualiza las órdenes 2008 objetivo.",
        "note": "V134 E0: define al C-41 como Orden de Pago y exige vencimiento contractual original.",
    },
    {
        "id": "e0_cgn_circular_13_2002_external_payments_c41",
        "filename": "cgn_circular_13_2002_pagos_exterior.html",
        "institution": "Contaduría General de la Nación",
        "title": "Circular CGN 13/02 · C-41 y pagos a beneficiarios del exterior",
        "url": "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/2002/circ13.htm",
        "publication": "2002-04-26",
        "period": "2002",
        "code": "Circular CGN 13/02; C-41; SAF 355/356",
        "type": "HTML oficial · captura preservada",
        "bytes": 9206,
        "sha256": "88b09113bdbdb39ea9d90175d3c889e052c9d24649fdb4c38ecb7be35597357a",
        "families": "SIDIF;C41;external_payment;beneficiary;BCRA;BNA",
        "breaks": "metadatos de orden versus transferencia bancaria",
        "use": "USABLE_C41_EXTERNAL_PAYMENT_FIELD_SCHEMA",
        "caveat": "No demuestra que los tres SIDIF 2008 fueran pagos al exterior ni recompras.",
        "note": "V134 E0: enumera beneficiario, banco, cuenta, SIDIF, moneda, cotización e importe que acompañan una C-41 exterior.",
    },
    {
        "id": "e0_cgn_circular_6_1995_c41_tgn",
        "filename": "cgn_circular_6_1995_c41_tgn.html",
        "institution": "Contaduría General de la Nación",
        "title": "Circular CGN 6/95 · procesamiento C-41 y remisión a TGN a efectos de pago",
        "url": "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/1995/cir06.htm",
        "publication": "1995-01-26",
        "period": "1995",
        "code": "Circular CGN 6/95; C-41; TGN",
        "type": "HTML oficial · captura preservada",
        "bytes": 15107,
        "sha256": "9d6b17a57c0c394b51cc35adb59d8b95f33c5f32c8819b67b7353c82876e0fac",
        "families": "SIDIF;C41;TGN;payment_processing;rejection",
        "breaks": "conformidad y remisión versus pago efectivo",
        "use": "USABLE_C41_PREPAYMENT_STAGE_RULE",
        "caveat": "Procedimiento general; una C-41 puede rechazarse antes del pago.",
        "note": "V134 E0: una C-41 conformada se remite a TGN 'a efectos de su pago'; el procesamiento y el pago son etapas distintas.",
    },
    {
        "id": "e0_cgn_circular_22_2004_c55_bank_debit",
        "filename": "cgn_circular_22_2004_c55.html",
        "institution": "Contaduría General de la Nación",
        "title": "Circular CGN 22/04 · C-55 ante diferencias entre débito bancario y C-41",
        "url": "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/2004/cir22.htm",
        "publication": "2004-12-29",
        "period": "2004",
        "code": "Circular CGN 22/04; C-41; C-55",
        "type": "HTML oficial · captura preservada",
        "bytes": 8534,
        "sha256": "626d6c57662055cc96756f9f203e843631f9ac9e5c144952e7ec7a8fe62cd3c7",
        "families": "SIDIF;C41;C55;bank_debit;regularization;deactivation",
        "breaks": "devengado C-41 versus débito bancario y regularización",
        "use": "USABLE_C41_C55_BANK_DEBIT_RECONCILIATION_RULE",
        "caveat": "Regla para pagos por nota y contribuciones figurativas; sirve como mapa documental, no como prueba de aplicación al target.",
        "note": "V134 E0: ordena C-55 cuando el débito BNA difiere del devengado C-41 e identifica cuenta y documento original.",
    },
    {
        "id": "e0_senado_bicameral_revisora_current_documents",
        "filename": "senado_bicameral_revisora_documentacion_actual.html",
        "institution": "Honorable Senado de la Nación",
        "title": "Comisión Parlamentaria Mixta Revisora de Cuentas · documentación y contacto públicos",
        "url": "https://www.senado.gob.ar/parlamentario/comisiones/info/100?Documentacion=2&Informacion=2&Reuniones=",
        "publication": "consulta 2026-08-30",
        "period": "1983-2026; documentación visible reciente",
        "code": "Comisión 100; REVISORA@SENADO.GOB.AR",
        "type": "HTML oficial · captura preservada",
        "bytes": 152197,
        "sha256": "597df2f9f87da7f828072189f21d65f7aa186e18e8318d0b50cfaa6ec7a15ff8",
        "families": "parliamentary_archive;commission_contact;public_inventory",
        "breaks": "inventario web visible versus fondo histórico completo",
        "use": "USABLE_CURRENT_COMMISSION_CHANNEL_NEGATIVE_CONTROL",
        "caveat": "No hallar la nota 2012 en la documentación visible no prueba que no exista en el archivo.",
        "note": "V134 E0: preserva contacto oficial e inventario público actual; no expone la nota de 18/05/2012 en las páginas visibles revisadas.",
    },
    {
        "id": "e0_hcdn_session_summary_2012_05_23_mass_archive",
        "filename": "hcdn_sumario_reunion_8_23_mayo_2012.html",
        "institution": "Honorable Cámara de Diputados de la Nación",
        "title": "Sumario de la reunión 8 del 23/05/2012 · archivo masivo de expedientes de la Revisora",
        "url": "https://www4.hcdn.gov.ar/sesionesxml/sumario.php?p=130&r=8",
        "publication": "2012-05-23",
        "period": "2012-05-23",
        "code": "Período 130; Reunión 8; punto 13",
        "type": "HTML oficial · captura preservada",
        "bytes": 77763,
        "sha256": "de52eedd2056e896f8cc231fb5cc586218f22a2417c8f0cf810f80f9919d39c9",
        "families": "parliamentary_archive;mass_archive;negative_control",
        "breaks": "contexto de archivo masivo versus disposición del expediente exacto",
        "use": "USABLE_MASS_ARCHIVE_CONTEXT_ONLY",
        "caveat": "El sumario preservado no individualiza OV 366/09 ni OV 44/10; no permite inferir su tratamiento en esa sesión.",
        "note": "V134 E0: documenta un lote amplio de archivos de la Revisora cinco días antes de la fecha de archivo de Senado; sólo contexto.",
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
    return text.replace("V133", "V134").replace("v133", "v134")


def clone_parent() -> None:
    skip = {"build_e0_archival_routes_v133.py", "qa_v133.py", "MANIFEST_V133.json", "INHERITED_QA_STATUS_V133.csv"}
    for source in PARENT.iterdir():
        if not source.is_file() or source.name in skip or source.name.startswith("HANDOVER_PROXIMA_SESION"):
            continue
        target = HERE / source.name.replace("V133", "V134")
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
assert len(catalog) == 369 and len({row["id"] for row in catalog}) == 369
write_csv(CATALOG, catalog)

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V134.csv"
census = [row for row in read_csv(census_path) if row["source_id"] not in source_ids]
for source in SOURCES:
    census.append({
        "source_id": source["id"], "institution": source["institution"], "artifact": source["title"],
        "url": source["url"], "local_path": source["local"], "sha256": source["sha256"],
        "bytes": str(source["bytes"]), "period_coverage": source["period"],
        "variable_families": source["families"], "primary_source": "YES", "preserved": "YES",
        "method_breaks": source["breaks"], "use_status": source["use"], "caveat": source["caveat"],
    })
assert len(census) == 129 and len({row["source_id"] for row in census}) == 129
write_csv(census_path, census)

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V134.csv"
provenance = [row for row in read_csv(provenance_path) if row["source_id"] not in source_ids]
for source in SOURCES:
    provenance.append({
        "source_id": source["id"], "original_url": source["url"], "retrieval_url": source["url"],
        "capture_timestamp": "20260830", "cdx_digest": "N/A_DIRECT_OFFICIAL", "local_path": source["local"],
        "sha256": source["sha256"], "bytes": str(source["bytes"]),
        "provenance_note": "Descarga directa oficial preservada y hasheada en V134; páginas PDF relevantes renderizadas cuando correspondió.",
    })
assert len(provenance) == 32
write_csv(provenance_path, provenance)

# FindDoc/COMDOC: capacidad, salida y control histórico separados del target.
finddoc = [
    {"row_id": "FD134_01", "evidence_type": "DESIGN_SPEC", "target": "Consulta pública FindDoc", "date": "2011", "output_schema": "número o patrón; hoja de ruta; ubicación", "result": "El ciudadano podía conocer ruta y ubicación.", "source_id": "e0_agenda_digital_finddoc_comdoc_architecture", "status": "CAPABILITY_PROVED", "permitted_inference": "FindDoc era el índice público competente para metadatos de ruta.", "forbidden_inference": "FindDoc publicaba el cuerpo completo."},
    {"row_id": "FD134_02", "evidence_type": "DESIGN_SPEC", "target": "Hoja de ruta", "date": "2011", "output_schema": "origen; destino; fecha de envío; fecha de recepción", "result": "Campos explícitos y movimientos desde ingreso en COMDOC.", "source_id": "e0_agenda_digital_finddoc_comdoc_architecture", "status": "OUTPUT_FIELDS_PROVED", "permitted_inference": "Una salida target permitiría reconstruir custodia temporal.", "forbidden_inference": "Los movimientos prueban contenido o pago."},
    {"row_id": "FD134_03", "evidence_type": "ARCHITECTURE", "target": "COMDOC3→FindDoc→Internet", "date": "2011", "output_schema": "COMDOC3/PostgreSQL; importador; FindDoc/MySQL en DMZ; usuario Internet", "result": "Separación técnica entre sistema interno e índice público.", "source_id": "e0_agenda_digital_finddoc_comdoc_architecture", "status": "ARCHITECTURE_PROVED", "permitted_inference": "La caída de FindDoc no implica pérdida de la base COMDOC interna.", "forbidden_inference": "La base interna continúa disponible sin verificación administrativa."},
    {"row_id": "FD134_04", "evidence_type": "HISTORIC_QUERY_CONTROL", "target": "S01:0130656/2008", "date": "2013-03-05", "output_schema": "estado; fecha del último pase; ubicación", "result": "En trámite; desde 11/06/2012 en Gabinete de la Subsecretaría de Obras Públicas.", "source_id": "e0_agn_informe_254_2013_finddoc_control", "status": "HISTORIC_QUERY_OPERATIONAL_CONTROL", "permitted_inference": "El endpoint entregaba datos útiles para un S01 de 2008 en 2013.", "forbidden_inference": "El expediente objetivo tuvo igual ruta o estado."},
    {"row_id": "FD134_05", "evidence_type": "TARGET_STATUS", "target": "S01:0342455/2008", "date": "2026-08-30", "output_schema": "origen; destino; fechas; ubicación esperables", "result": "Endpoint legado no operativo; consulta target no ejecutada.", "source_id": "e0_economia_consulta_expedientes_comdoc_gde;e0_agenda_digital_finddoc_comdoc_architecture;e0_agn_informe_254_2013_finddoc_control", "status": "TARGET_QUERY_UNEXECUTED_ADMINISTRATIVE_EXPORT_REQUIRED", "permitted_inference": "Pedir exportación o consulta administrativa exacta de la hoja de ruta.", "forbidden_inference": "Sin resultado o expediente inexistente."},
]
write_csv(HERE / "E0_COMDOC_FINDDOC_CAPABILITY_V134.csv", finddoc)

comdoc_path = HERE / "E0_COMDOC_LEGACY_QUERY_ROUTE_V134.csv"
comdoc = read_csv(comdoc_path)
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
]
write_csv(HERE / "E0_C41_PAYMENT_EXECUTION_CHAIN_V134.csv", c41_chain)

# Archivo parlamentario: el contexto masivo no sustituye el localizador exacto.
bicameral = [
    {"row_id": "BI134_01", "object": "OV 366/09", "route_checked": "Senado expediente exacto", "result": "Bicameral Revisora; archivo 28/05/2012 por nota 18/05/2012; texto original en carga", "status": "EXACT_METADATA_BODY_OPEN", "source_id": "e0_senado_exp_366_09_agn_res211_t3", "next_locator": "nota 18/05/2012; remito; inventario; depósito"},
    {"row_id": "BI134_02", "object": "OV 44/10", "route_checked": "Senado expediente exacto", "result": "Bicameral Revisora; archivo 28/05/2012 por nota 18/05/2012; texto original en carga", "status": "EXACT_METADATA_BODY_OPEN", "source_id": "e0_senado_exp_44_10_agn_res44_t4", "next_locator": "nota 18/05/2012; remito; inventario; depósito"},
    {"row_id": "BI134_03", "object": "Documentación pública Bicameral", "route_checked": "Sección Documentación y paginación visible", "result": "Documentos recientes visibles; nota 2012 no expuesta en el inventario revisado", "status": "PUBLIC_UI_NEGATIVE_CONTROL_ONLY", "source_id": "e0_senado_bicameral_revisora_current_documents", "next_locator": "REVISORA@SENADO.GOB.AR; internos 2310-2315"},
    {"row_id": "BI134_04", "object": "Lote de archivo parlamentario", "route_checked": "HCDN reunión 8 del 23/05/2012 punto 13", "result": "Amplio lote de archivos de la Revisora; strings exactas OV 366/09 y OV 44/10 no localizadas", "status": "MASS_ARCHIVE_CONTEXT_NOT_TARGET_PROOF", "source_id": "e0_hcdn_session_summary_2012_05_23_mass_archive", "next_locator": "No usar como disposición de los dos expedientes target"},
    {"row_id": "BI134_05", "object": "Nota Bicameral 18/05/2012", "route_checked": "Senado + documentación actual + sumario HCDN", "result": "Cuerpo e inventario de transferencia no localizados públicamente", "status": "EXACT_NOTE_BODY_OPEN", "source_id": "e0_senado_exp_366_09_agn_res211_t3;e0_senado_exp_44_10_agn_res44_t4;e0_senado_bicameral_revisora_current_documents;e0_hcdn_session_summary_2012_05_23_mass_archive", "next_locator": "Solicitud archivística exacta; borrador no enviado"},
]
write_csv(HERE / "E0_BICAMERAL_PUBLIC_INVENTORY_AUDIT_V134.csv", bicameral)

# Rutas agotadas, ledger y cortes metodológicos.
exhaust_path = HERE / "E0_EXPEDIENT_PUBLIC_SEARCH_EXHAUSTION_V134.csv"
exhaust = read_csv(exhaust_path)
exhaust.extend([
    {"search_id": "EX134_07", "target": "FindDoc capability", "route": "Agenda Digital Argentina pp.206-207", "result": "Esquema de salida y arquitectura exactos", "public_body_found": "DESIGN_SPEC", "status": "ROUTE_METADATA_CAPABILITY_PROVED", "permitted_inference": "El índice histórico mostraba pases y ubicación.", "forbidden_inference": "Mostraba el cuerpo."},
    {"search_id": "EX134_08", "target": "S01:0130656/2008", "route": "AGN Informe 254/2013", "result": "Consulta real al endpoint con estado y ubicación al 05/03/2013", "public_body_found": "CONTROL_QUERY_METADATA", "status": "HISTORIC_OPERATIONAL_CONTROL", "permitted_inference": "FindDoc funcionaba para un S01/2008.", "forbidden_inference": "Responde por el target."},
    {"search_id": "EX134_09", "target": "S01:0342455/2008", "route": "canales oficiales alternativos Economía", "result": "Email, teléfono y atención presencial identificados; no contactados", "public_body_found": "NO", "status": "ADMINISTRATIVE_ROUTE_READY_NOT_SENT", "permitted_inference": "Puede pedirse exportación de hoja de ruta.", "forbidden_inference": "La consulta fue presentada."},
    {"search_id": "EX134_10", "target": "Nota Bicameral 18/05/2012", "route": "inventario actual Senado + sumario HCDN 23/05/2012", "result": "Contexto de archivo masivo; cuerpo exacto no localizado", "public_body_found": "CONTEXT_ONLY", "status": "PUBLIC_INVENTORY_EXHAUSTED_EXACT_NOTE_OPEN", "permitted_inference": "El pedido puede dirigirse al contacto actual con dos OV exactos.", "forbidden_inference": "Los expedientes fueron parte del lote de Cámara o fueron destruidos."},
])
write_csv(exhaust_path, exhaust)

ledger_path = HERE / "E0_FISCAL_MECHANISM_LEDGER_V134.csv"
ledger = read_csv(ledger_path)
ledger.extend([
    {"ledger_id": "F158", "window": "2011-2013", "mechanism": "Legacy_document_index", "phase": "FINDDOC_CAPABILITY_AND_CONTROL", "as_of_date": "2013-03-05", "payer": "N/A", "recipient": "N/A", "universe": "COMDOC_S01_files", "instrument": "FindDoc_route_metadata", "amount_original": "4", "original_unit": "OUTPUT_FIELD_FAMILIES", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_agenda_digital_finddoc_comdoc_architecture;e0_agn_informe_254_2013_finddoc_control", "source_locator": "Agenda_pp206_207;AGN_254_pp91_93_133", "realization_status": "HISTORIC_CAPABILITY_AND_OPERATIONAL_CONTROL_PROVED", "additivity": "NON_ADDITIVE", "status_interpretation": "FindDoc exposed route/location metadata and was actually used for another 2008 S01 file.", "caveat": "The target query remains unexecuted and body content is outside the proven output schema."},
    {"ledger_id": "F159", "window": "2008-2026", "mechanism": "Debt_buyback_excess_GDP", "phase": "TARGET_FINDDOC_ADMINISTRATIVE_QUERY", "as_of_date": "2026-08-30", "payer": "N/A", "recipient": "N/A", "universe": "S01_0342455_2008", "instrument": "COMDOC_FindDoc", "amount_original": "0", "original_unit": "TARGET_QUERY_RESULTS", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_economia_consulta_expedientes_comdoc_gde;e0_agenda_digital_finddoc_comdoc_architecture", "source_locator": "official_alternative_channels", "realization_status": "ADMINISTRATIVE_EXPORT_REQUIRED_DRAFT_NOT_SENT", "additivity": "NON_ADDITIVE", "status_interpretation": "The expected route fields and official contact channel are known.", "caveat": "No request was submitted and no target route was recovered."},
    {"ledger_id": "F160", "window": "1995-2008", "mechanism": "Debt_accounting_payment_chain", "phase": "C41_TO_BANK_DEBIT_RECONCILIATION", "as_of_date": "2008-12-31", "payer": "Tesoro_Nacional", "recipient": "Unknown_target_beneficiaries", "universe": "SIDIF_71597_152677_2876", "instrument": "C41_C55_bank_debit", "amount_original": "3", "original_unit": "C41_LOCATORS", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_cgn_cuenta_inversion_2008_sdp;e0_cgn_circular_2_1997_c41_due_date;e0_cgn_circular_6_1995_c41_tgn;e0_cgn_circular_13_2002_external_payments_c41;e0_cgn_circular_22_2004_c55_bank_debit", "source_locator": "Anexo_K_and_CGN_procedure_rules", "realization_status": "DOCUMENT_CLASS_AND_CHAIN_PROVED_TARGET_BODIES_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "Three exact identifiers can anchor searches for order, processing, debit and adjustment records.", "caveat": "An order number is not executed payment and is not yet linked to the buyback."},
    {"ledger_id": "F161", "window": "2012-05-18/2012-05-28", "mechanism": "AGN_parliamentary_archive", "phase": "MASS_ARCHIVE_CONTEXT_CONTROL", "as_of_date": "2012-05-28", "payer": "N/A", "recipient": "Parliamentary_archive", "universe": "OV_366_09_OV_44_10", "instrument": "Bicameral_note_and_HCDN_archive_batch", "amount_original": "2", "original_unit": "TARGET_EXPEDIENTS", "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE", "source_id": "e0_senado_bicameral_revisora_current_documents;e0_hcdn_session_summary_2012_05_23_mass_archive", "source_locator": "current_public_inventory;HCDN_session_summary", "realization_status": "MASS_ARCHIVE_CONTEXT_ONLY_EXACT_NOTE_BODY_OPEN", "additivity": "NON_ADDITIVE", "status_interpretation": "The period contains mass archival activity but the two target strings were not located in the inspected HCDN summary.", "caveat": "Context does not establish the disposition of either target expediente."},
])
assert len(ledger) == 161
write_csv(ledger_path, ledger)

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V134.csv"
breaks = read_csv(breaks_path)
breaks.extend([
    {"break_id": "finddoc_route_metadata_not_expedient_body", "dimension": "document_scope", "problem": "FindDoc's public output is proven for route and location fields.", "rule": "Use it to trace custody; request the body separately.", "status": "FROZEN", "evidence": "Agenda Digital pp.206-207"},
    {"break_id": "historic_control_query_not_target_query", "dimension": "external_validity", "problem": "AGN queried another S01/2008 successfully in 2013.", "rule": "Use as operational control only; keep S01:0342455/2008 unqueried.", "status": "FROZEN", "evidence": "AGN 254/2013 pp.93,133"},
    {"break_id": "c41_order_not_executed_payment", "dimension": "phase", "problem": "C-41 is an order that can require processing, TGN action, debit and adjustment.", "rule": "Require payment/debit status and C-55 or equivalent where applicable.", "status": "FROZEN", "evidence": "CGN Circulares 2/97, 6/95, 13/02, 22/04"},
    {"break_id": "mass_archive_context_not_target_disposition", "dimension": "archival_scope", "problem": "A large HCDN archive batch is temporally adjacent but does not list the two exact target strings.", "rule": "Retain exact Senate metadata as locator and request the 18/05/2012 note.", "status": "FROZEN", "evidence": "HCDN reunión 8; Senate OV 366/09 and OV 44/10"},
])
assert len(breaks) == 121
write_csv(breaks_path, breaks)

# Se enriquecen los seis borradores; nada se envía.
trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V134.csv"
trace = read_csv(trace_path)
trace.extend([
    {"trace_id": "TR134_105", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / administradores COMDOC", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Exportación de hoja de ruta FindDoc/COMDOC del expediente target", "period_or_date": "2008-actualidad", "identifiers": "S01:0342455/2008;VerExpediente", "minimum_usable_fields": "origen;destino;fecha envío;fecha recepción;ubicación;estado", "confidentiality_fallback": "metadatos de pases sin cuerpo", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR134_106", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / CGN / TGN", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Cuerpo y estado de tres formularios C-41 2008", "period_or_date": "2008", "identifiers": "SIDIF 71597;152677;2876;SIGADE 83106000", "minimum_usable_fields": "SAF;beneficiario;concepto;importe;moneda;emisión;vencimiento;estado", "confidentiality_fallback": "cuadro certificado por número SIDIF", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR134_107", "request_id": "REQ134_ECON", "institution": "Ministerio de Economía / TGN / BNA", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Pago, débito, rechazo, reversa o C-55 asociados a cada C-41", "period_or_date": "2008-2009", "identifiers": "71597;152677;2876;C-41;C-55", "minimum_usable_fields": "fecha;importe;moneda;cuenta;estado;documento original;vínculo C-41", "confidentiality_fallback": "estado final y total por orden", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR134_108", "request_id": "REQ134_ECON", "institution": "Dirección de Información Ciudadana / Mesa de Entradas", "gap_id": "CL134_DEBT_ACCOUNTING", "requested_record": "Consulta administrativa sustitutiva por caída del endpoint", "period_or_date": "2026-08-30", "identifiers": "ciudadano@mecon.gov.ar;0810-333-6326;Balcarce186 oficina140", "minimum_usable_fields": "acuse;número de gestión;resultado;derivación", "confidentiality_fallback": "derivación al custodio competente", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR134_109", "request_id": "REQ134_AGN", "institution": "Senado / Bicameral Revisora", "gap_id": "CL134_AGN_REPLY", "requested_record": "Nota de archivo del 18/05/2012 e inventario/remito asociado", "period_or_date": "2012-05-18/2012-05-28", "identifiers": "OV366/09;OV44/10;nota18/05/2012", "minimum_usable_fields": "emisor;destinatario;listado;fecha;depósito;signatura", "confidentiality_fallback": "renglones exactos de ambos OV", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR134_110", "request_id": "REQ134_AGN", "institution": "Senado / Bicameral Revisora", "gap_id": "CL134_AGN_REPLY", "requested_record": "Resultado de búsqueda en fondo histórico no expuesto por la UI pública", "period_or_date": "2009-2012", "identifiers": "Res211/2009;Res44/2010;Act426/09;Act466/09", "minimum_usable_fields": "serie;caja;legajo;soporte;estado de conservación", "confidentiality_fallback": "certificación de búsqueda y ruta de transferencia", "status": "DRAFT_NOT_SENT"},
])
assert len(trace) == 110
write_csv(trace_path, trace)

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V134.csv"
keys = read_csv(keys_path)
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
])
assert len(keys) == 108
write_csv(keys_path, keys)

agn_request = HERE / "REQUEST_AGN_2018_REPLY_V134.md"
agn_request.write_text(agn_request.read_text(encoding="utf-8-sig").rstrip() + """

## Clave V134 · inventario público y nota de archivo

La interfaz pública actual de la Comisión no expone, entre la documentación visible revisada, la nota de archivo del `18/05/2012` ni su inventario. El sumario de Diputados del `23/05/2012` prueba un contexto de archivo masivo de expedientes de la Revisora, pero no individualiza `OV 366/09` ni `OV 44/10`; no se lo presenta como disposición de estos casos.

Se solicita búsqueda en el fondo histórico por ambos OV, resoluciones y actuaciones AGN, y copia de la nota, remito, inventario, depósito y signatura. Contacto público identificado: `REVISORA@SENADO.GOB.AR`, internos `2310-2315`. Estado: **BORRADOR_NO_ENVIADO**.
""", encoding="utf-8")

econ_request = HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V134.md"
econ_request.write_text(econ_request.read_text(encoding="utf-8-sig").rstrip() + """

## Clave V134 · salida FindDoc y cadena C-41

La especificación oficial de FindDoc prueba que la salida pública era una hoja de ruta: origen, destino, fechas de envío y recepción y ubicación. La AGN documentó una consulta efectiva al mismo endpoint el `05/03/2013` para otro expediente `S01:0130656/2008`, obteniendo estado y ubicación. Estos antecedentes permiten pedir una exportación administrativa equivalente para `S01:0342455/2008`, pero no sustituyen su consulta ni el cuerpo del expediente. Canales oficiales: `ciudadano@mecon.gov.ar`, `0810-333-6326`, Balcarce 186, piso 1, oficina 140.

Para los SIDIF `71597`, `152677` y `2876`, se solicitan los C-41 completos y su estado. Las normas CGN definen la C-41 como Orden de Pago, contemplan rechazo y remisión a TGN “a efectos de su pago”, y muestran trazas posteriores como débito bancario y C-55 cuando existe diferencia. Por eso se piden por cada número: beneficiario, concepto, importe, moneda, fechas, procesamiento, pago/débito, rechazo/reversa y C-55 si aplica. Ningún número se atribuye por anticipado a la recompra. Estado: **BORRADOR_NO_ENVIADO**.
""", encoding="utf-8")

# Síntesis del checkpoint.
(HERE / "README_V134.md").write_text("""# V134 · FindDoc y cadena C-41

V134 prueba qué entregaba el índice FindDoc/COMDOC y documenta un control histórico real de la AGN sobre otro S01/2008. La salida era hoja de ruta y ubicación, no cuerpo del expediente. El target `S01:0342455/2008` sigue sin consulta ejecutada; quedó lista una vía administrativa oficial, no enviada. Cuatro normas CGN separan emisión C-41, procesamiento, remisión a TGN, débito y C-55. Los SIDIF `71597`, `152677` y `2876` son localizadores exactos, no pagos confirmados. La revisión parlamentaria sólo aporta contexto de archivo masivo; la nota del 18/05/2012 continúa abierta. Resultado estricto sin cambio: 10/10 adjudicaciones, 9/10 cuentas candidatas y 0/10 ejecuciones confirmadas; seis pedidos DRAFT_NOT_SENT.
""", encoding="utf-8")

(HERE / "VEREDICTO_V134.md").write_text("""# Veredicto V134

La caída del endpoint ya no deja indeterminado qué podía probar FindDoc: la documentación oficial lo define como índice de hoja de ruta y ubicación, con origen, destino y fechas. La AGN acredita que en 2013 ese endpoint devolvió estado y ubicación para otro expediente S01 iniciado en 2008. Esto fortalece un pedido de exportación target, pero no recupera `S01:0342455/2008` ni su cuerpo.

Los tres SIDIF visibles de Banco Nación tampoco equivalen a pago. La normativa CGN distingue C-41 emitida, posible rechazo, remisión a TGN “a efectos de su pago”, movimiento bancario y regularización/desafectación C-55. Hasta obtener cuerpos y estados, sólo son tres claves de búsqueda exactas.

El archivo parlamentario agrega un control negativo: hubo actividad masiva de archivo en mayo de 2012, pero los dos OV target no fueron localizados en el sumario inspeccionado y la nota de 18/05/2012 no aparece en el inventario público actual. No se infiere destrucción ni tratamiento por Cámara.

La ejecución sigue abierta: 0/10 filas confirmadas. `CLOSED_NETWORK_GATE=NO`; seis borradores, ninguno enviado.
""", encoding="utf-8")

(HERE / "E0_FISCAL_RECONSTRUCTION_V134.md").write_text("""# Reconstrucción fiscal E0 · V134

## Resultado incremental

1. FindDoc queda calibrado como índice de ruta/ubicación; su arquitectura y campos públicos están probados.
2. Un caso AGN demuestra uso real del endpoint para un S01/2008 en 2013, sin trasladar su resultado al target.
3. La cadena C-41→procesamiento→TGN→débito→C-55 distingue orden de pago de pago ejecutado.
4. Los SIDIF `71597`, `152677` y `2876` reducen el universo documental, pero sus cuerpos y estados siguen abiertos.
5. El contexto parlamentario masivo no reemplaza la nota exacta de archivo.
6. No cambian preadjudicación, transferencia Caja, informe T+3, crédito BCRA ni cancelación CRyL: 0/10 ejecuciones confirmadas.
""", encoding="utf-8")

(HERE / "RETRIEVAL_LOG_V134.md").write_text("""# Registro de recuperación V134

Fecha: 2026-08-30.

1. Se preservó y verificó visualmente la doble página 206-207 de la Agenda Digital Argentina: arquitectura COMDOC3/FindDoc y campos de hoja de ruta.
2. Se preservó el Informe AGN 254/2013 y se verificaron las páginas relevantes 91, 93 y 133: consulta efectiva a VerExpediente sobre `S01:0130656/2008`.
3. Se preservaron cuatro normas CGN que documentan C-41, procesamiento previo a pago, campos de transferencias exteriores y C-55 ante diferencias bancarias.
4. Las búsquedas exactas por `71597`, `152677` y `2876` no localizaron los cuerpos de las C-41 ni submayor público adicional.
5. Se preservaron la página actual de la Bicameral y el sumario HCDN del 23/05/2012; la nota exacta del 18/05/2012 no fue localizada.
6. El intento de acceso directo a COMDOC fue bloqueado/no operativo; no se eludieron controles ni se codificó ausencia.
7. No se envió ningún pedido ni se realizó presentación externa.
""", encoding="utf-8")

refs_path = HERE / "SOURCE_REFERENCES_V134.md"
refs_path.write_text(refs_path.read_text(encoding="utf-8-sig").rstrip() + """

- Agenda Digital Argentina · FindDoc/COMDOC: https://cdi.mecon.gob.ar/bases/docelec/br1018.pdf
- AGN Informe 254/2013: https://www.agn.gob.ar/sites/default/files/informes/Informe_254_2013.pdf
- CGN Circular 2/97: https://www.economia.gob.ar/hacienda/cgn/normas/circulares/1997/cir2.htm
- CGN Circular 13/02: https://www.economia.gob.ar/hacienda/cgn/normas/circulares/2002/circ13.htm
- CGN Circular 6/95: https://www.economia.gob.ar/hacienda/cgn/normas/circulares/1995/cir06.htm
- CGN Circular 22/04: https://www.economia.gob.ar/hacienda/cgn/normas/circulares/2004/cir22.htm
- Senado · Bicameral Revisora: https://www.senado.gob.ar/parlamentario/comisiones/info/100
- HCDN · reunión 8 del 23/05/2012: https://www4.hcdn.gov.ar/sesionesxml/sumario.php?p=130&r=8

FindDoc prueba trazabilidad, no cuerpo; C-41 prueba orden, no pago; archivo masivo prueba contexto, no disposición target.
""", encoding="utf-8")

handover = """# Handover V134 → V135

## Estado congelado

- Diez adjudicaciones participante-instrumento exactas; nueve cuentas BCRA candidatas; MERVAL abierta; 0/10 ejecuciones confirmadas.
- FindDoc: arquitectura y salida exactas probadas (hoja de ruta, ubicación, origen, destino y fechas); AGN documenta una consulta real a otro S01/2008 en 2013.
- `S01:0342455/2008`: consulta target todavía no ejecutada; canal administrativo oficial identificado; cuerpo abierto.
- C-41: documento clasificado como Orden de Pago; procesamiento, TGN, débito y C-55 son etapas separadas. SIDIF `71597`, `152677` y `2876` son claves exactas, no pagos confirmados.
- Bicameral: contexto de archivo masivo en mayo de 2012; nota exacta de 18/05/2012 e inventario no localizados públicamente.
- Seis pedidos DRAFT_NOT_SENT; ninguno enviado; panel estricto sin cambios.

## Prioridad V135

1. Si hay autorización expresa, presentar los seis pedidos; si no, mantenerlos como borradores.
2. Buscar exportaciones, manuales o respaldos del índice COMDOC que permitan consulta pasiva del target sin el endpoint caído.
3. Buscar C-41 `71597`, `152677`, `2876`, su estado de pago, débito/reversa y C-55 en CGN/TGN/Archivo.
4. Buscar nota Bicameral 18/05/2012, remito, inventario y depósito por `OV 366/09` y `OV 44/10`.
5. Mantener separados expediente, C-41, procesamiento, débito, transferencia Caja, crédito BCRA y cancelación CRyL.
"""
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V134_A_V135.md").write_text(handover, encoding="utf-8")

(HERE / "AUDITORIA_V134.md").write_text(f"""# Auditoría V134

- Fuentes maestras: {len(catalog)}; ocho fuentes oficiales nuevas preservadas.
- Fuentes primarias E0: {len(census)}.
- Ledger fiscal: {len(ledger)} filas; cortes metodológicos: {len(breaks)}.
- FindDoc: 5 controles de capacidad/salida/target; target sin consulta ejecutada.
- C-41: 8 etapas documentales; tres IDs target; cuerpos y estados abiertos.
- Bicameral: 5 controles; nota exacta e inventario abiertos.
- Escalera: 10 adjudicaciones; 9 cuentas candidatas; 0 ejecuciones confirmadas.
- Pedidos: 6 borradores, 0 enviados; {len(trace)} objetos y {len(keys)} claves.
- Panel estricto: 30 entidades; {STRICT}% sin cambios.
""", encoding="utf-8")

# Auditoría física y estado global.
for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    shutil.copyfile(AUDIT / f"{stem}_V133.csv", AUDIT / f"{stem}_V134.csv")

hash_rows = []
for row in catalog:
    local = row["archivo_local"]
    path = REPO / local.lstrip("/") if local else None
    exists = bool(path and path.is_file())
    actual = sha256(path) if exists else ""
    expected = row["sha256"]
    hash_rows.append({"id": row["id"], "archivo_local": local, "exists": str(exists), "sha_catalog": expected, "sha_actual": actual, "hash_ok": str(bool(exists and expected and actual.lower() == expected.lower()))})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V134.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V134.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
assert physical == hash_ok == 363

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or "tmp" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": str(size), "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V134.csv", size_rows)

completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V133.json").read_text(encoding="utf-8"))
for key in list(completeness):
    if key.endswith("_v133") or "newly_preserved_v133" in key:
        completeness.pop(key, None)
completeness.update({
    "checkpoint": "V134", "date": "2026-08-30",
    "state": "E0_FINDDOC_SCHEMA_AND_C41_CHAIN_PROVED_TARGET_EXECUTION_OPEN_NOT_SENT",
    "numeric_v134_strict_changed": False, "master_catalog_entries": len(catalog),
    "physical_local_copies": physical, "physical_local_hash_ok": hash_ok,
    "e0_primary_sources_preserved": len(census), "e0_quality": "PRIMARY_FINDDOC_AND_C41_PROCEDURE_CONTROLS",
    "sources_newly_preserved_v134": 8, "e0_primary_sources_newly_preserved_v134": 8,
    "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
    "e0_request_traceability_rows": len(trace), "e0_request_search_keys": len(keys),
    "e0_finddoc_capability_rows": len(finddoc), "e0_finddoc_target_query_executed": False,
    "e0_c41_chain_rows": len(c41_chain), "e0_c41_target_ids": 3, "e0_c41_target_bodies_located": 0,
    "e0_bicameral_inventory_control_rows": len(bicameral), "e0_bicameral_exact_note_body_located": False,
    "e0_settlement_award_rows_exact": 10, "e0_settlement_account_candidate_rows": 9,
    "e0_settlement_executed_rows_confirmed": 0, "e0_requests_submitted": 0,
    "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
    "historical_workstream": "FindDoc output schema and historic operation proved; target route/body, C41 states, bank debits, Bicameral note and executed settlement remain open; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V134.json").write_text(json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V134 · FindDoc y cadena C-41"
text = backup.read_text(encoding="utf-8-sig")
if marker not in text:
    text += f"\n\n{marker}\n\n- FindDoc calibrado como índice de ruta/ubicación y validado con control AGN sobre otro S01/2008.\n- Target `S01:0342455/2008` sin consulta ejecutada; vía administrativa oficial lista y no enviada.\n- C-41 separada de procesamiento, pago/débito y C-55; tres SIDIF exactos siguen sin cuerpos ni estados.\n- Nota Bicameral 18/05/2012 abierta; contexto de archivo masivo no se atribuye a los dos OV.\n- Escalera sin cambio: 10 adjudicaciones, 9 cuentas candidatas, 0 ejecuciones confirmadas.\n"
    backup.write_text(text, encoding="utf-8")

inherited = [
    {"script": "qa_v133.py", "pre_v134_result": "PASS", "post_v134_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V133 queda supersedido por nuevas fuentes y conteos V134."},
    {"script": "qa_v134.py", "pre_v134_result": "N/A", "post_v134_result": "PASS", "interpretation": "FindDoc, C-41, Bicameral, hashes y no ejecución verificados."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V134.csv", inherited)

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

finddoc = rows("E0_COMDOC_FINDDOC_CAPABILITY_V134.csv")
assert len(finddoc) == 5 and finddoc[-1]["status"] == "TARGET_QUERY_UNEXECUTED_ADMINISTRATIVE_EXPORT_REQUIRED"
assert "origen" in finddoc[1]["output_schema"] and "fecha de recepción" in finddoc[1]["output_schema"]
comdoc = rows("E0_COMDOC_LEGACY_QUERY_ROUTE_V134.csv")
assert len(comdoc) == 5 and comdoc[-1]["body_query_executed"] == "NO"

c41 = rows("E0_C41_PAYMENT_EXECUTION_CHAIN_V134.csv")
assert len(c41) == 8 and c41[0]["stage"] == "C41_ISSUED" and c41[-1]["target_status"] == "OPEN"
assert "71597" in c41[-1]["required_or_visible_fields"]
bicameral = rows("E0_BICAMERAL_PUBLIC_INVENTORY_AUDIT_V134.csv")
assert len(bicameral) == 5 and bicameral[-1]["status"] == "EXACT_NOTE_BODY_OPEN"

assert len(rows("E0_EXPEDIENT_PUBLIC_SEARCH_EXHAUSTION_V134.csv")) == 10
assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V134.csv")) == 161
assert len(rows("E0_FISCAL_METHOD_BREAKS_V134.csv")) == 121
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V134.csv")) == 110
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V134.csv")) == 108
ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V134.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V134.csv")}
new_ids = {"e0_agenda_digital_finddoc_comdoc_architecture", "e0_agn_informe_254_2013_finddoc_control", "e0_cgn_circular_2_1997_c41_due_date", "e0_cgn_circular_13_2002_external_payments_c41", "e0_cgn_circular_6_1995_c41_tgn", "e0_cgn_circular_22_2004_c55_bank_debit", "e0_senado_bicameral_revisora_current_documents", "e0_hcdn_session_summary_2012_05_23_mass_archive"}
assert len(census) == 129 and new_ids <= set(census)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 369 and len({r["id"] for r in catalog}) == 369

expected = {
    "agenda_digital_argentina_2003_2011_br1018.pdf": (3550343, "1d76b6d563aea0d6dd7fa67e22a53b36e269849b3ef6ecd0508e8e16f156d68b"),
    "agn_informe_254_2013.pdf": (23877781, "99028db4627cc1190bab7d2282ae9330bca08846676b3bdf4cf4a64a969e23be"),
    "cgn_circular_13_2002_pagos_exterior.html": (9206, "88b09113bdbdb39ea9d90175d3c889e052c9d24649fdb4c38ecb7be35597357a"),
    "cgn_circular_2_1997_c41.html": (3126, "52ef4c74fdd4d9ff27bb694e9b0a01e60580054df22c02574669a5c274e0da29"),
    "cgn_circular_22_2004_c55.html": (8534, "626d6c57662055cc96756f9f203e843631f9ac9e5c144952e7ec7a8fe62cd3c7"),
    "cgn_circular_6_1995_c41_tgn.html": (15107, "9d6b17a57c0c394b51cc35adb59d8b95f33c5f32c8819b67b7353c82876e0fac"),
    "hcdn_sumario_reunion_8_23_mayo_2012.html": (77763, "de52eedd2056e896f8cc231fb5cc586218f22a2417c8f0cf810f80f9919d39c9"),
    "senado_bicameral_revisora_documentacion_actual.html": (152197, "597df2f9f87da7f828072189f21d65f7aa186e18e8318d0b50cfaa6ec7a15ff8"),
}
bin_dir = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v134" / "binaries"
assert len(list(bin_dir.iterdir())) == 8
for name, (size, digest) in expected.items():
    path = bin_dir / name
    assert path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest() == digest

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V134.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V134"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 363
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v134_strict_changed"] is False

for name, marker in {
    "REQUEST_AGN_2018_REPLY_V134.md": "## Clave V134 · inventario público y nota de archivo",
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V134.md": "## Clave V134 · salida FindDoc y cadena C-41",
}.items():
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert marker in text and "BORRADOR_NO_ENVIADO" in text

for name in ("README_V134.md", "VEREDICTO_V134.md", "E0_FISCAL_RECONSTRUCTION_V134.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V134_A_V135.md"):
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")

print("V134 QA PASS")
'''
(HERE / "qa_v134.py").write_text(qa, encoding="utf-8")

def checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V134.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V134", "parent_checkpoint": "V133",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": 8, "new_primary_sources": 8,
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks),
        "finddoc_capability_rows": len(finddoc), "finddoc_target_query_executed": False,
        "c41_chain_rows": len(c41_chain), "c41_target_ids": 3, "c41_target_bodies_located": 0,
        "bicameral_control_rows": len(bicameral), "bicameral_exact_note_body_located": False,
        "award_rows_exact": 10, "account_candidate_rows": 9, "executed_settlement_rows_confirmed": 0,
        "request_drafts": 6, "request_traceability_rows": len(trace), "request_search_keys": len(keys),
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V134.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    "checkpoint": "V134", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical copies SHA-valid; FindDoc schema and C41 chain proved; zero of ten executed settlement rows confirmed; six requests drafted and none submitted.",
    "historical_workstream": "Target COMDOC route/body, C41 states, bank debits, Bicameral note and executed settlement remain open; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V134 BUILD PASS")
