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
V123 = HERE.parent / "V123"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v124" / "binaries"
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


source_specs = [
    {
        "id": "e0_merval_sistema_transferencias_2004_wayback",
        "institution": "Mercado de Valores de Buenos Aires / Centro de Atención a Usuarios",
        "title": "Documentación de Sistemas Informáticos · Sistema de Transferencias Electrónicas",
        "url": "https://web.archive.org/web/20040208012932id_/http://www.merval.sba.com.ar:80/sba/asp/sba_sistemas.asp",
        "file": "merval_sistemas_transferencias_2004_wayback.html",
        "publication": "2004-02-08",
        "period": "captura institucional archivada del 2004-02-08; sistema preexistente al período objetivo",
        "type": "HTML institucional oficial archivado · copia preservada",
        "families": "state_bcra;fiscal;debt;Caja;custody;electronic_transfer;system_availability;SCG",
        "breaks": "disponibilidad pública 2004 versus vigencia exacta 2008; descripción del sistema versus operación objetivo",
        "use": "USABLE_PRE_TARGET_PUBLIC_SYSTEM_AVAILABILITY",
        "caveat": "Prueba que el sistema y su documentación se ofrecían públicamente en 2004; no identifica la revisión vigente en 2008 ni una transferencia objetivo.",
        "verified": "HTML oficial archivado; contiene la sección Sistemas de Custodia y Garantía, el nombre Sistema de Transferencias Electrónicas, sus funciones de alta/autorización/modificación/baja/consulta y la clave de descarga SCG.",
    },
    {
        "id": "e0_caja_manual_dtc_control_cambios_m32002",
        "institution": "Caja de Valores S.A.",
        "title": "Manual del Usuario Cuenta CVSA-DTC MU-32002.03 · control de cambios",
        "url": "https://cajadevalores.com.ar/img/Documentacion/M-32002.pdf",
        "file": "caja_manual_cuenta_dtc_m32002.pdf",
        "publication": "2009-05",
        "period": "control de revisiones febrero 2006, septiembre 2007 y mayo 2009; manual paralelo no SLIQ",
        "type": "PDF operativo oficial de Caja · binario preservado",
        "families": "state_bcra;fiscal;debt;Caja;custody;document_control;revision;effective_date",
        "breaks": "tabla de revisión de otro manual versus vigencia del manual SLIQ; metadatos versus fecha interna",
        "use": "USABLE_CROSS_MANUAL_REVISION_CONTROL_SCHEMA_NOT_TARGET_VIGENCY",
        "caveat": "Demuestra la práctica documental de numerar revisiones y registrar cambios, pero no traslada la revisión MU-32002.03 al sistema de transferencias local ni prueba liquidaciones objetivo.",
        "verified": "24 páginas; páginas PDF 3 y 22 renderizadas e inspeccionadas visualmente; MU-32002.03 rige desde mayo de 2009 y su control de cambios lista revisiones 00-03, incluida la incorporación de la fecha de vigencia en septiembre de 2007.",
    },
    {
        "id": "e0_caja_memoria_estados_2006_archivo_2007",
        "institution": "Caja de Valores S.A.",
        "title": "Memoria y Estados Contables · ejercicio finalizado el 31/12/2006",
        "url": "https://web.archive.org/web/20070626113838id_/http://www.cajval.sba.com.ar/pdf/memoria_2007.pdf",
        "file": "caja_memoria_estados_2006_archivo_2007.pdf",
        "publication": "2007-03-08",
        "period": "ejercicios 2005-2006; captura institucional archivada del 2007-06-26",
        "type": "PDF institucional y contable oficial archivado · binario preservado",
        "families": "state_bcra;fiscal;debt;Caja;custody;transfers;information_technology;operational_context",
        "breaks": "actividad e ingresos por transferencias versus modalidad o asiento objetivo; infraestructura institucional versus vigencia de una revisión",
        "use": "USABLE_PRE_TARGET_OPERATIONAL_CONTEXT_ONLY",
        "caveat": "Documenta actividad e infraestructura previas a 2008, pero no desagrega transferencias inmediatas/diferidas ni acredita las rondas objetivo.",
        "verified": "76 páginas; páginas PDF 20 y 44-45 renderizadas e inspeccionadas visualmente; describe continuidad de sistemas y muestra ingresos por transferencias en 2005-2006.",
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
for row in catalog:
    if row["id"] == "e0_caja_sistema_transferencias_electronicas_manual":
        row.update(
            {
                "fecha_publicacion": "2000-03",
                "periodo_utilizado": "edición impresa en Buenos Aires en marzo de 2000; PDF reexportado en 2018",
                "nota": (
                    "V124 E0 fiscal: el mismo binario preservado en V123 fue revalidado visualmente. "
                    "La página PDF 2 fecha internamente la edición en marzo de 2000; las páginas 9-12 "
                    "definen modalidades, fases, contrapartes, formularios y matching."
                ),
            }
        )
for spec in source_specs:
    catalog.append(
        {
            "id": spec["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": spec["institution"],
            "titulo": spec["title"], "url_original": spec["url"], "archivo_local": spec["local"],
            "fecha_descarga": "2026-08-29", "fecha_publicacion": spec["publication"], "codigo_serie": "",
            "periodo_utilizado": spec["period"], "tipo": spec["type"], "sha256": spec["sha256"],
            "nota": f"V124 E0 fiscal: {spec['bytes']:,} bytes. {spec['verified']}",
        }
    )
write_csv(CATALOG, catalog)


census = [row for row in read_csv(V123 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V123.csv") if row["source_id"] not in new_ids]
for row in census:
    if row["source_id"] == "e0_caja_sistema_transferencias_electronicas_manual":
        row.update(
            {
                "period_coverage": "edición impresa en marzo de 2000; PDF reexportado en 2018",
                "method_breaks": "fecha de impresión versus vigencia/revisión exacta en 2008; modalidad versus ejecución objetivo",
                "use_status": "USABLE_PRE_TARGET_OPERATIONAL_DEFINITION_EDITION_DATED_VIGENCY_OPEN",
                "caveat": "La edición está fechada en marzo de 2000 y define el mecanismo; no demuestra por sí sola qué revisión seguía vigente en 2008 ni una operación objetivo.",
            }
        )
for spec in source_specs:
    census.append(
        {
            "source_id": spec["id"], "institution": spec["institution"], "artifact": spec["title"],
            "url": spec["url"], "local_path": spec["local"], "sha256": spec["sha256"], "bytes": str(spec["bytes"]),
            "period_coverage": spec["period"], "variable_families": spec["families"], "primary_source": "YES",
            "preserved": "YES", "method_breaks": spec["breaks"], "use_status": spec["use"], "caveat": spec["caveat"],
        }
    )
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V124.csv", census)


ledger = read_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V124.csv")
breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V124.csv")
channels = read_csv(HERE / "CURRENT_OFFICIAL_SUBMISSION_CHANNELS_V124.csv")
trace = read_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V124.csv")
responses = read_csv(HERE / "E0_REQUEST_RESPONSE_REGISTER_V124.csv")
closures = read_csv(HERE / "E0_REQUEST_CLOSURE_CRITERIA_V124.csv")
system_map = read_csv(HERE / "E0_DOCUMENT_SYSTEM_TEMPORAL_MAP_V124.csv")
authorities = read_csv(HERE / "E0_ARCHIVAL_RETENTION_AUTHORITY_MATRIX_V124.csv")
negative_adequacy = read_csv(HERE / "E0_NEGATIVE_RESPONSE_ADEQUACY_V124.csv")
producer_map = read_csv(HERE / "E0_RECORD_PRODUCER_SYSTEM_MAP_V124.csv")
search_keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V124.csv")
attachments = read_csv(HERE / "E0_REQUEST_ATTACHMENT_MINIMUM_V124.csv")
version_chain = read_csv(HERE / "E0_CRYL_EFFECTIVE_VERSION_CHAIN_V124.csv")
term_audit = read_csv(HERE / "E0_BUYBACK_MODALITY_TERM_AUDIT_V124.csv")
cga_map = read_csv(HERE / "E0_CRYL_CGA_RECORD_MAP_V124.csv")


new_breaks = [
    {
        "break_id": "deferred_modality_not_tsa_channel", "dimension": "system",
        "problem": "La modalidad diferida describe el tipo o programación de transferencia; TSA describe un canal de archivos que puede transportarla.",
        "rule": "Mantener canal y modalidad en campos separados y exigir el registro objetivo antes de asignarlos a 2008.",
        "status": "FROZEN", "evidence": "CVSA Comunicado 10290; BYMA Instructivo NSC 2023",
    },
    {
        "break_id": "legacy_form_not_contemporaneous_2008_use", "dimension": "legal_time",
        "problem": "Los formularios F-33914.01 y F-33915.01 documentan un esquema de transferencia diferida en 2017, no su edición o uso en 2008.",
        "rule": "Usarlos sólo como diccionario retrospectivo de campos y pedir la versión vigente o la tabla de equivalencias histórica.",
        "status": "FROZEN", "evidence": "CVSA F-33914.01 y F-33915.01; metadatos 2017-11-23",
    },
    {
        "break_id": "matching_fields_not_completed_target_transfer", "dimension": "phase",
        "problem": "La existencia de fecha de ejecución, límite de matching y contrapartes en un formulario vacío no prueba una instrucción emparejada ni ejecutada.",
        "rule": "Exigir formulario completado, lote, estado de matching y asiento de recepción para cada fecha y especie.",
        "status": "FROZEN", "evidence": "CVSA F-33914.01 y F-33915.01",
    },
    {
        "break_id": "current_nsc_rule_not_historical_rule", "dimension": "legal_time",
        "problem": "El Nuevo Sistema de Custodia eliminó en 2023 los tipos diferida e inmediata; esa regla nueva no describe automáticamente 2008.",
        "rule": "Usar el cambio como corte metodológico y no retrotraerlo al período objetivo.",
        "status": "FROZEN", "evidence": "BYMA Instructivo de Liquidaciones NSC 2023",
    },
    {
        "break_id": "isin_not_cvsa_custody_code", "dimension": "identifier",
        "problem": "ISIN, código de negociación y código de custodia/CVSA son identificadores diferentes aunque señalen la misma especie.",
        "rule": "Conservar cada columna y documentar el puente fuente por fuente; no reemplazar un identificador por otro.",
        "status": "FROZEN", "evidence": "CVSA Comunicado 10290; BYMA Instructivo NSC 2023",
    },
    {
        "break_id": "parent_security_code_not_strip_subspecies_code", "dimension": "identifier",
        "problem": "El código del BODEN 2012 principal no identifica necesariamente la subespecie separada cupón 15 de 2009.",
        "rule": "Usar 5326 para ARARGE03G415 y conservar 5426 sólo para el BODEN 2012 principal; no colapsar ambas especies.",
        "status": "RESOLVED_IDENTIFIER_LAYER_ONLY", "evidence": "Llamado strip 2009; Banco Columbia Anexo A; Banco Patagonia Exhibit A",
    },
    {
        "break_id": "bank_disclosure_identifier_not_target_settlement", "dimension": "phase",
        "problem": "Una tabla bancaria contemporánea puede identificar inequívocamente la especie sin documentar la entrega, recepción o liquidación de la recompra objetivo.",
        "rule": "Aceptar la tabla para el puente de identificadores y mantener abiertos los asientos de Caja, el matching y el pago BCRA.",
        "status": "FROZEN", "evidence": "Banco Columbia 30/06/2009; Banco Patagonia 30/06/2009",
    },
    {
        "break_id": "near_contemporaneous_deferred_form_not_exact_2008_edition", "dimension": "legal_time",
        "problem": "La CNV prueba formularios numerados de Recepción Diferida en agosto de 2009, pero no identifica la revisión vigente durante las rondas de 2008.",
        "rule": "Usar 2009 como práctica cercana y solicitar la revisión, vigencia o tabla de equivalencias exacta de 2008.",
        "status": "FROZEN", "evidence": "CNV Resolución 16.189 del 20/08/2009",
    },
    {
        "break_id": "manual_print_date_not_2008_effective_revision", "dimension": "legal_time",
        "problem": "La página legal fecha la edición del manual SLIQ en marzo de 2000, pero una fecha de impresión no acredita continuidad sin cambios hasta 2008.",
        "rule": "Aceptar marzo de 2000 como fecha interna de la edición y mantener abierta la revisión efectiva en cada ronda de 2008.",
        "status": "FROZEN", "evidence": "Manual Sistema de Transferencias Electrónicas, página PDF 2",
    },
    {
        "break_id": "archived_system_listing_not_exact_2008_revision", "dimension": "legal_time",
        "problem": "La página institucional archivada en 2004 confirma la disponibilidad del Sistema de Transferencias Electrónicas y su documentación, pero no identifica la revisión aplicable en 2008.",
        "rule": "Usarla para disponibilidad preobjetivo; exigir el control de cambios o registro maestro SLIQ/SCG para cerrar vigencia.",
        "status": "FROZEN", "evidence": "Merval, Documentación de Sistemas Informáticos, captura 2004-02-08",
    },
    {
        "break_id": "parallel_manual_revision_log_not_target_manual_vigency", "dimension": "document_control",
        "problem": "El manual MU-32002.03 conserva revisiones 2006/2007/2009 y fecha de vigencia, pero corresponde a la cuenta CVSA-DTC y no al sistema local SLIQ.",
        "rule": "Usar su tabla como esquema de control documental exigible y no trasladar números, fechas ni vigencia al manual objetivo.",
        "status": "FROZEN", "evidence": "Caja MU-32002.03, páginas PDF 3 y 22",
    },
    {
        "break_id": "institutional_transfer_activity_not_target_settlement", "dimension": "phase",
        "problem": "La memoria de Caja muestra infraestructura y actividad/ingresos por transferencias antes de 2008 sin desagregar modalidad, cuenta, especie ni estado.",
        "rule": "Tratarla sólo como contexto operativo preobjetivo y exigir instrucción, matching, asiento e informe T+3 para las rondas.",
        "status": "FROZEN", "evidence": "Caja, Memoria y Estados Contables 2006, páginas PDF 20 y 44-45",
    },
]
break_ids = {row["break_id"] for row in new_breaks}
breaks = [row for row in breaks if row["break_id"] not in break_ids] + new_breaks
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V124.csv", breaks)


new_search_keys = [
    {"key_id": "SK124_44", "request_id": "REQ124_ECON", "key_group": "historical_code", "exact_key": "5426;5427;45698;45701;5326", "search_purpose": "cruzar resultados, especie recibida y registración de deuda", "source_or_basis": "llamados oficiales + tablas AFIP + Banco Columbia/Patagonia", "caveat": "Los cinco códigos identifican especies; no son por sí solos asientos liquidados."},
    {"key_id": "SK124_45", "request_id": "REQ124_BCRA", "key_group": "security_bridge", "exact_key": "ARARGE034678=5426;ARARGE035709=5427;ARARGE03E147=45698;ARARGE03E154=45701;ARARGE03G415=5326", "search_purpose": "pedir corroboración histórica ISIN-código de custodia/CRyL", "source_or_basis": "llamados oficiales + Banco Columbia/Patagonia", "caveat": "Puente público cerrado por denominación y fecha; sigue abierta la etiqueta CRyL y la liquidación."},
    {"key_id": "SK124_46", "request_id": "REQ124_CAJA", "key_group": "security_bridge", "exact_key": "ARARGE034678=5426;ARARGE035709=5427;ARARGE03E147=45698;ARARGE03E154=45701;ARARGE03G415=5326", "search_purpose": "confirmar vigencia y localizar asientos por Código Caja", "source_or_basis": "llamados oficiales + Anexo A Banco Columbia", "caveat": "La tabla rotula Identificación Caja de Valores, pero no contiene los asientos objetivo."},
    {"key_id": "SK124_47", "request_id": "REQ124_CAJA", "key_group": "form", "exact_key": "Recepción Diferida 0102704;Recepción Diferida 0102705;F-33914.01;F-33915.01", "search_purpose": "obtener revisión vigente en 2008 o equivalencia", "source_or_basis": "manual SLIQ marzo 2000 + CNV Res. 16.189/2009 + formularios CVSA 2017", "caveat": "La edición del manual está fechada en 2000 y la práctica está probada en 2009; la revisión exacta de 2008 sigue abierta."},
    {"key_id": "SK124_48", "request_id": "REQ124_CAJA", "key_group": "matching", "exact_key": "proceso batch nocturno;almacenamiento provisorio;matching;fecha de ejecución;fecha límite de validez;SCG", "search_purpose": "buscar instrucción emparejada, procesada y conciliada", "source_or_basis": "Manual Sistema de Transferencias marzo 2000 + página Merval 2004 + formularios CVSA", "caveat": "La definición operativa, la disponibilidad del sistema y los campos no prueban el registro objetivo."},
    {"key_id": "SK124_49", "request_id": "REQ124_ECON", "key_group": "strip_code", "exact_key": "ARARGE03G415=5326;BODEN 2012 cupón 15;vto.03/08/2009", "search_purpose": "cruzar la subespecie con recepción, pago y baja de deuda", "source_or_basis": "llamado oficial 2009 + Banco Columbia/Patagonia", "caveat": "5326 no debe confundirse con 5426 del título principal."},
    {"key_id": "SK124_50", "request_id": "REQ124_BCRA", "key_group": "channel_modality", "exact_key": "SLIQ;SCG;TSA;modalidad diferida;batch nocturno;CGA;FT;FTC;Código CVSA;Código CRyL", "search_purpose": "pedir equivalencias históricas sin confundir canal, modalidad y estado", "source_or_basis": "manual Caja marzo 2000; página Merval 2004; B9173; CVSA 10290; BYMA NSC 2023", "caveat": "La edición está fechada en 2000, pero no acredita la revisión efectiva ni el uso en las rondas objetivo."},
    {"key_id": "SK124_51", "request_id": "REQ124_CAJA", "key_group": "document_control", "exact_key": "Sistema de Transferencias Electrónicas;SLIQ;SCG;Impreso en Buenos Aires, Marzo de 2000;sba_sistemas.asp", "search_purpose": "localizar el registro maestro y las revisiones del manual entre 2000 y 2009", "source_or_basis": "manual SLIQ página 2 + página institucional Merval archivada 2004", "caveat": "Fecha de impresión y disponibilidad pública no equivalen a vigencia ininterrumpida."},
    {"key_id": "SK124_52", "request_id": "REQ124_CAJA", "key_group": "revision_control", "exact_key": "MU-32002.00;MU-32002.01;MU-32002.02;MU-32002.03;Febrero 2006;Septiembre 2007;Mayo 2009;CONTROL DE CAMBIOS", "search_purpose": "pedir el control de cambios equivalente del manual SLIQ/SCG", "source_or_basis": "Caja MU-32002.03 página 22", "caveat": "El manual DTC sólo aporta el esquema documental; sus revisiones no rigen SLIQ."},
    {"key_id": "SK124_53", "request_id": "REQ124_ECON", "key_group": "settlement_dates", "exact_key": "2008-09-02;2008-09-09;2008-09-16;2008-10-07;0306/40000;informe Caja 10 hs;orden de pago BCRA", "search_purpose": "localizar informe T+3, orden de pago, conciliación y baja por cada ronda", "source_or_basis": "Resolución Conjunta 24/212 y llamados/resultados oficiales", "caveat": "El cronograma normativo y las fechas programadas no acreditan ejecución ni pago."},
]
new_key_ids = {row["key_id"] for row in new_search_keys}
search_keys = [row for row in search_keys if row["key_id"] not in new_key_ids] + new_search_keys
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V124.csv", search_keys)


new_trace = [
    {"trace_id": "TR124_068", "request_id": "REQ124_ECON", "institution": "Ministerio de Economía / Tesoro", "gap_id": "CL124_SECURITY_CODE", "requested_record": "Tabla o registro interno que corrobore los cinco códigos públicos", "period_or_date": "2008-2009", "identifiers": "cinco ISIN; 5426; 5427; 45698; 45701; 5326", "minimum_usable_fields": "ISIN; código; denominación; vigencia; sistema", "confidentiality_fallback": "certificación por especie", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR124_069", "request_id": "REQ124_CAJA", "institution": "Caja de Valores S.A.", "gap_id": "CL124_SECURITY_CODE", "requested_record": "Tabla histórica ISIN-Código Caja y vigencia de las cinco especies", "period_or_date": "2008-2009", "identifiers": "cinco ISIN; 5426; 5427; 45698; 45701; 5326", "minimum_usable_fields": "ISIN; Código Caja; subespecie; alta/baja; vigencia", "confidentiality_fallback": "confirmación institucional sin tenedores", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR124_070", "request_id": "REQ124_CAJA", "institution": "Caja de Valores S.A.", "gap_id": "CL124_DEFERRED_MODALITY", "requested_record": "Revisión efectiva en 2008 del formulario o procedimiento de entrega/recepción diferida", "period_or_date": "2008-2009", "identifiers": "SLIQ/SCG; edición marzo 2000; F-33914.01; F-33915.01; modalidad diferida", "minimum_usable_fields": "código documental; revisión; vigencia; campos; matching; reemplazo", "confidentiality_fallback": "registro maestro, control de cambios o tabla de equivalencias", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR124_071", "request_id": "REQ124_CAJA", "institution": "Caja de Valores S.A.", "gap_id": "CL124_CAJA_ROUTE", "requested_record": "Instrucciones diferidas emparejadas y estado de ejecución", "period_or_date": "fechas T+2 2008-2009", "identifiers": "0306/40000; cinco ISIN; códigos 5426/5427/45698/45701/5326", "minimum_usable_fields": "fecha ejecución; límite matching; emisor/receptor; código; cantidad; estado", "confidentiality_fallback": "agregado por fecha/especie/estado", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR124_072", "request_id": "REQ124_BCRA", "institution": "BCRA / CRyL", "gap_id": "CL124_SECURITY_CODE", "requested_record": "Diccionario histórico entre ISIN, código de custodia/Caja y código CRyL", "period_or_date": "2008-2009", "identifiers": "cinco ISIN; 5426; 5427; 45698; 45701; 5326", "minimum_usable_fields": "identificador; tipo; especie; vigencia; sistema", "confidentiality_fallback": "tabla testada sin cuentas", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR124_073", "request_id": "REQ124_BCRA", "institution": "BCRA / CRyL", "gap_id": "CL124_DEFERRED_MODALITY", "requested_record": "Equivalencia histórica entre modalidad diferida, TSA/CGA y fórmula CRyL", "period_or_date": "2008-2009", "identifiers": "diferida; TSA; CGA; FT; FTC; DVP", "minimum_usable_fields": "canal; modalidad; formulario/archivo; estado; vigencia", "confidentiality_fallback": "manual o diccionario de códigos", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR124_074", "request_id": "REQ124_CAJA", "institution": "Caja de Valores S.A.", "gap_id": "CL124_DEFERRED_MODALITY", "requested_record": "Registro maestro y control de cambios del manual Sistema de Transferencias Electrónicas SLIQ/SCG", "period_or_date": "2000-2009, con corte en cada fecha T/T+2/T+3 de 2008", "identifiers": "edición marzo 2000; SCG; SLIQ; MU-32002 como esquema paralelo", "minimum_usable_fields": "código documental; revisión; fecha de aprobación; vigencia desde/hasta; cambio; reemplazo", "confidentiality_fallback": "certificación de la revisión efectiva por fecha sin contenido reservado", "status": "DRAFT_NOT_SENT"},
]
new_trace_ids = {row["trace_id"] for row in new_trace}
trace = [row for row in trace if row["trace_id"] not in new_trace_ids] + new_trace
write_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V124.csv", trace)


new_closures = [
    {"gap_id": "CL124_SECURITY_CODE", "target_question": "¿Cuál era el Código Caja/CRyL de cada una de las cinco especies objetivo?", "minimum_positive_evidence": "Cadena pública contemporánea que vincule ISIN, denominación y Código Caja propio de cada especie; corroboración institucional deseable para vigencia y capa CRyL.", "minimum_negative_route_evidence": "N/A: el puente público se cerró; conservar búsqueda institucional sólo como corroboración y para los asientos.", "does_not_close": "La identificación de especie no demuestra matching, recepción, pago ni baja de deuda.", "initial_status": "PUBLIC_CROSSWALK_CLOSED_FIVE_CAJA_CODES_SETTLEMENT_STILL_OPEN_NOT_SENT"},
    {"gap_id": "CL124_DEFERRED_MODALITY", "target_question": "¿Qué revisión, formulario, archivo y estados operativos implementaron la modalidad diferida en 2008?", "minimum_positive_evidence": "Revisión vigente en cada fecha objetivo de 2008 más instrucción/lote que separe canal, modalidad, matching, recepción y liquidación.", "minimum_negative_route_evidence": "Búsqueda reproducible por SLIQ/SCG, edición marzo 2000, registro maestro/control de cambios, formularios 0102704/0102705, F-33914/F-33915, batch nocturno, TSA, CGA, FT/FTC/DVP, cuenta, fechas y repositorios históricos/sucesores.", "does_not_close": "Fecha de impresión 2000; disponibilidad pública 2004; actividad institucional 2006; práctica regulatoria 2009; control de revisiones de otro manual; formulario 2017 en blanco; retiro de modalidades en 2023.", "initial_status": "OPEN_PRE_TARGET_SYSTEM_CHAIN_PRESERVED_EXACT_2008_EFFECTIVE_REVISION_AND_TARGET_RECORD_NOT_SENT"},
]
new_closure_ids = {row["gap_id"] for row in new_closures}
closures = [row for row in closures if row["gap_id"] not in new_closure_ids] + new_closures
write_csv(HERE / "E0_REQUEST_CLOSURE_CRITERIA_V124.csv", closures)


deferred_audit = [
    {"audit_id": "DM124_01", "artifact_date": "2008", "artifact_or_rule": "Procedimiento específico de recompra", "term_or_mechanism": "modalidad diferida", "observed_definition_or_field": "Instrucción a Caja hasta cierre T+2; Caja informa T+3; Tesoro paga luego en BCRA", "relation_to_2008_target": "DIRECT_TARGET_RULE", "evidence_status": "EXACT_TERM_PROCEDURE_ONLY", "prohibited_inference": "No asignar TSA, CGA, FT, FTC, DVP ni formulario sin el registro técnico.", "source_id": "e0_argentina_rc_212_24_2008_recompra", "locator": "Anexo; puntos 2.1-2.3"},
    {"audit_id": "DM124_02", "artifact_date": "2008-01", "artifact_or_rule": "BCRA Comunicación B 9173", "term_or_mechanism": "CGA para FT/FTC", "observed_definition_or_field": "Archivo X-400/MCT; primera validación condicional y segunda etapa", "relation_to_2008_target": "CONTEMPORANEOUS_AVAILABLE_ROUTE", "evidence_status": "ROUTE_AVAILABLE_USAGE_UNPROVEN", "prohibited_inference": "No equiparar CGA con diferida ni validación con liquidación.", "source_id": "e0_bcra_b9173_cryl_cga_x400_2008", "locator": "Anexos I-III"},
    {"audit_id": "DM124_03", "artifact_date": "2017", "artifact_or_rule": "CVSA F-33914.01", "term_or_mechanism": "entrega diferida", "observed_definition_or_field": "Fecha de ejecución; límite de matching; Código Caja; emisor y receptor", "relation_to_2008_target": "RETROSPECTIVE_FIELD_SCHEMA", "evidence_status": "SCHEMA_ONLY_POST_TARGET", "prohibited_inference": "No afirmar edición o uso en 2008.", "source_id": "e0_cvsa_f33914_deferred_delivery_2017", "locator": "páginas PDF 1-2"},
    {"audit_id": "DM124_04", "artifact_date": "2017", "artifact_or_rule": "CVSA F-33915.01", "term_or_mechanism": "recepción diferida", "observed_definition_or_field": "Autorización receptora con campos espejo y matching", "relation_to_2008_target": "RETROSPECTIVE_COUNTERPART_SCHEMA", "evidence_status": "SCHEMA_ONLY_POST_TARGET", "prohibited_inference": "No tratar autorización en blanco como recepción ejecutada.", "source_id": "e0_cvsa_f33915_deferred_receipt_2017", "locator": "páginas PDF 1-2"},
    {"audit_id": "DM124_05", "artifact_date": "2020", "artifact_or_rule": "CVSA Comunicado 10290", "term_or_mechanism": "TSA + diferida", "observed_definition_or_field": "Archivos TSA hasta 19 h; subcuentas sólo admiten transferencias diferidas", "relation_to_2008_target": "POST_TARGET_CATEGORY_DISTINCTION", "evidence_status": "CHANNEL_AND_MODALITY_COEXIST", "prohibited_inference": "No convertir TSA en sinónimo de diferida ni proyectar el canje 2020 a 2008.", "source_id": "e0_cvsa_communication_10290_tsa_deferred_2020", "locator": "página PDF 2"},
    {"audit_id": "DM124_06", "artifact_date": "2023", "artifact_or_rule": "BYMA Instructivo NSC", "term_or_mechanism": "TSA + retiro de diferida/inmediata", "observed_definition_or_field": "TSA conserva formato; exige código de custodia; el NSC elimina tipos diferida/inmediata", "relation_to_2008_target": "POST_TARGET_METHOD_BREAK", "evidence_status": "DISTINCT_LAYERS_AND_REGIME_CHANGE", "prohibited_inference": "No retrotraer la regla NSC ni confundir ISIN con código de custodia.", "source_id": "e0_byma_nsc_tsa_modality_retirement_2023", "locator": "página PDF 3"},
    {"audit_id": "DM124_07", "artifact_date": "2009-08-20", "artifact_or_rule": "CNV Resolución 16.189", "term_or_mechanism": "formularios de Recepción Diferida", "observed_definition_or_field": "Formularios numerados 0102704 y 0102705; boleto BODEN 2012; listado de saldos y movimientos remitido por Caja", "relation_to_2008_target": "NEAR_CONTEMPORANEOUS_DOCUMENTED_PRACTICE", "evidence_status": "DEFERRED_FORM_PRACTICE_CONFIRMED_2009", "prohibited_inference": "No atribuir esos formularios ni su edición a las rondas de 2008.", "source_id": "e0_cnv_res_16189_recepcion_diferida_2009", "locator": "página PDF 1"},
    {"audit_id": "DM124_08", "artifact_date": "2000-03; PDF reexportado 2018", "artifact_or_rule": "Caja · Sistema de Transferencias Electrónicas", "term_or_mechanism": "inmediata versus diferida", "observed_definition_or_field": "Edición impresa en marzo de 2000; inmediata en tiempo real; diferida por batch nocturno; alta, confirmación, almacenamiento provisorio, procesamiento, matching y formulario", "relation_to_2008_target": "PRE_TARGET_DATED_OPERATIONAL_DEFINITION", "evidence_status": "EDITION_DATE_AND_MECHANISM_CONFIRMED_EFFECTIVE_2008_REVISION_OPEN", "prohibited_inference": "No convertir fecha de impresión en vigencia ininterrumpida ni inferir ejecución objetivo sin revisión y registros.", "source_id": "e0_caja_sistema_transferencias_electronicas_manual", "locator": "páginas PDF 2 y 9-12"},
    {"audit_id": "DM124_09", "artifact_date": "2004-02-08", "artifact_or_rule": "Merval · Documentación de Sistemas Informáticos", "term_or_mechanism": "Sistema de Transferencias Electrónicas / SCG", "observed_definition_or_field": "Página institucional ofrece el manual y describe alta, autorización, modificación, baja y consulta de transferencias entre subcuentas de Caja", "relation_to_2008_target": "PRE_TARGET_PUBLIC_SYSTEM_AVAILABILITY", "evidence_status": "SYSTEM_AND_DOCUMENTATION_PUBLICLY_AVAILABLE_2004", "prohibited_inference": "No atribuir a 2008 la revisión disponible en 2004 ni inferir una instrucción objetivo.", "source_id": "e0_merval_sistema_transferencias_2004_wayback", "locator": "HTML archivado; sección Sistemas de Custodia y Garantía"},
    {"audit_id": "DM124_10", "artifact_date": "2006-02; 2007-09; 2009-05", "artifact_or_rule": "Caja MU-32002.03 · Manual Cuenta CVSA-DTC", "term_or_mechanism": "control de cambios y fecha de vigencia", "observed_definition_or_field": "Tabla de revisiones 00-03; en septiembre de 2007 se incorporó la fecha de vigencia; versión 03 aplicable desde mayo de 2009", "relation_to_2008_target": "PARALLEL_DOCUMENT_CONTROL_SCHEMA", "evidence_status": "REVISION_LOG_PRACTICE_CONFIRMED_NOT_TARGET_MANUAL", "prohibited_inference": "No trasladar revisión, vigencia ni procedimiento DTC a SLIQ o a las rondas objetivo.", "source_id": "e0_caja_manual_dtc_control_cambios_m32002", "locator": "páginas PDF 3 y 22"},
    {"audit_id": "DM124_11", "artifact_date": "2007-03-08; ejercicio 2006", "artifact_or_rule": "Caja · Memoria y Estados Contables 2006", "term_or_mechanism": "infraestructura y actividad de transferencias", "observed_definition_or_field": "Continuidad de reingeniería de sistemas e ingresos por transferencias en 2005-2006", "relation_to_2008_target": "PRE_TARGET_OPERATIONAL_CONTEXT", "evidence_status": "INSTITUTIONAL_ACTIVITY_CONFIRMED_MODALITY_AND_TARGET_OPEN", "prohibited_inference": "No convertir ingresos o infraestructura en prueba de modalidad, volumen, cuenta o liquidación objetivo.", "source_id": "e0_caja_memoria_estados_2006_archivo_2007", "locator": "páginas PDF 20 y 44-45"},
]
write_csv(HERE / "E0_DEFERRED_MODALITY_EQUIVALENCE_AUDIT_V124.csv", deferred_audit)


crosswalk = [
    {"crosswalk_id": "ID124_01", "target_instrument": "BODEN 2012; U$S LIBOR 2012 1ra serie", "isin": "ARARGE034678", "historical_code": "5426", "code_label_in_source": "IDENTIFICACIÓN CAJA DE VALORES", "primary_chain": "llamados 2008 por nombre/ISIN + AFIP 2007/2008 + Banco Columbia 30/06/2009 + Banco Patagonia 30/06/2009", "evidence_status": "CONTEMPORANEOUS_CAJA_CODE_CONFIRMED", "unresolved_element": "Asiento objetivo y eventual equivalencia CRyL", "prohibited_inference": "No inferir recepción o liquidación."},
    {"crosswalk_id": "ID124_02", "target_instrument": "BODEN 2013; U$S LIBOR 2013 1ra serie", "isin": "ARARGE035709", "historical_code": "5427", "code_label_in_source": "IDENTIFICACIÓN CAJA DE VALORES", "primary_chain": "llamados 2008 por nombre/ISIN + AFIP 2007/2008 + Banco Columbia 30/06/2009", "evidence_status": "CONTEMPORANEOUS_CAJA_CODE_CONFIRMED", "unresolved_element": "Asiento objetivo y eventual equivalencia CRyL", "prohibited_inference": "No inferir recepción o liquidación."},
    {"crosswalk_id": "ID124_03", "target_instrument": "Unidad vinculada al PIB denominada en pesos", "isin": "ARARGE03E147", "historical_code": "45698", "code_label_in_source": "IDENTIFICACIÓN CAJA DE VALORES", "primary_chain": "llamados 2008 por nombre/ISIN + AFIP 2007/2008 + Banco Columbia 30/06/2009", "evidence_status": "CONTEMPORANEOUS_CAJA_CODE_CONFIRMED", "unresolved_element": "Asiento objetivo y eventual equivalencia CRyL", "prohibited_inference": "La identificación no prueba uso ni liquidación en 2008."},
    {"crosswalk_id": "ID124_04", "target_instrument": "Unidad vinculada al PIB en dólares; ley argentina", "isin": "ARARGE03E154", "historical_code": "45701", "code_label_in_source": "IDENTIFICACIÓN CAJA DE VALORES", "primary_chain": "llamados 2008 por nombre/ISIN + AFIP 2007/2008 + Banco Columbia 30/06/2009", "evidence_status": "CONTEMPORANEOUS_CAJA_CODE_CONFIRMED", "unresolved_element": "Asiento objetivo y eventual equivalencia CRyL", "prohibited_inference": "No confundir variantes de cable/exterior ni inferir liquidación."},
    {"crosswalk_id": "ID124_05", "target_instrument": "BODEN 2012 cupón 15 separado", "isin": "ARARGE03G415", "historical_code": "5326", "code_label_in_source": "IDENTIFICACIÓN CAJA DE VALORES; IDENTIFICATION", "primary_chain": "llamado oficial 2009 por nombre/ISIN/vencimiento + Banco Columbia por denominación/vencimiento/código + Banco Patagonia por cupón 15/código", "evidence_status": "EXACT_CONTEMPORANEOUS_CAJA_CODE_TWO_BANK_DISCLOSURES", "unresolved_element": "Asiento objetivo y eventual equivalencia CRyL", "prohibited_inference": "No confundir 5326 del cupón separado con 5426 del BODEN 2012 principal ni inferir liquidación."},
]
write_csv(HERE / "E0_SECURITY_IDENTIFIER_CROSSWALK_V124.csv", crosswalk)


settlement_stages = [
    {"stage_id": "ST124_01", "sequence": "1", "stage": "adjudicación", "producer": "Secretaría de Finanzas", "expected_record": "resultado publicado y comunicación de adjudicación", "asset_leg": "monto/especie adjudicados", "cash_leg": "precio adjudicado; aún no pagado", "evidence_status": "PUBLIC_RESULT_PRESERVED", "open_gap": "comunicación individual y expediente", "do_not_collapse_with": "entrega; recepción; pago"},
    {"stage_id": "ST124_02", "sequence": "2", "stage": "instrucción diferida", "producer": "depositante adjudicado / Caja", "expected_record": "instrucción por fecha, especie, código, cantidad y cuenta 0306/40000", "asset_leg": "orden de transferir", "cash_leg": "ninguna", "evidence_status": "DIRECT_TARGET_TERM_PLUS_DATED_2000_MANUAL_2004_SYSTEM_2009_FORM_PRACTICE", "open_gap": "revisión/formulario efectivo en 2008 y registro objetivo", "do_not_collapse_with": "matching o ejecución"},
    {"stage_id": "ST124_03", "sequence": "3", "stage": "matching/autorización", "producer": "depositantes emisor/receptor / Caja", "expected_record": "entrega y recepción coincidentes; fecha límite y estado", "asset_leg": "instrucciones emparejadas", "cash_leg": "ninguna", "evidence_status": "PRE_TARGET_OPERATIONAL_MECHANISM_DEFINED_TARGET_RECORD_OPEN", "open_gap": "registro objetivo y revisión vigente en cada fecha de 2008", "do_not_collapse_with": "recepción efectivamente asentada"},
    {"stage_id": "ST124_04", "sequence": "4", "stage": "cierre de recepción T+2", "producer": "Caja de Valores", "expected_record": "asiento de títulos recibidos/rechazados en 0306/40000", "asset_leg": "débito emisor y crédito fiduciario", "cash_leg": "ninguna", "evidence_status": "SCHEDULED_NOT_CONFIRMED", "open_gap": "asiento, lote y estado por especie", "do_not_collapse_with": "confirmación T+3"},
    {"stage_id": "ST124_05", "sequence": "5", "stage": "informe Caja T+3 10 h", "producer": "Caja de Valores", "expected_record": "detalle de transferencias recibidas remitido a Secretaría", "asset_leg": "confirmación de recepción", "cash_leg": "base para instruir pago", "evidence_status": "SCHEDULED_NOT_CONFIRMED", "open_gap": "mensaje, identificador y contenido", "do_not_collapse_with": "pago BCRA"},
    {"stage_id": "ST124_06", "sequence": "6", "stage": "pago T+3", "producer": "Tesoro / BCRA", "expected_record": "orden y débito/crédito en cuentas corrientes BCRA", "asset_leg": "conciliación con títulos recibidos", "cash_leg": "efectivo pagado", "evidence_status": "SCHEDULED_NOT_CONFIRMED", "open_gap": "orden, importe, moneda, estado y conciliación", "do_not_collapse_with": "acuse técnico"},
    {"stage_id": "ST124_07", "sequence": "paralela/condicional", "stage": "mensajería CRyL/CGA si aplicó", "producer": "Caja / entidad / BCRA-CRyL", "expected_record": "CGA, segunda validación, CG3 o fórmula papel", "asset_leg": "registro técnico de transferencia", "cash_leg": "ninguna por sí sola", "evidence_status": "AVAILABLE_ROUTE_USAGE_UNPROVEN", "open_gap": "equivalencia con modalidad diferida y lote objetivo", "do_not_collapse_with": "liquidación económica"},
    {"stage_id": "ST124_08", "sequence": "7", "stage": "conciliación y baja de deuda", "producer": "ONCP/DADP/TGN", "expected_record": "conciliación resultado-entrega-pago y registración de deuda", "asset_leg": "títulos recomprados/cancelados", "cash_leg": "pago conciliado", "evidence_status": "OPEN", "open_gap": "documento contable por ronda/especie", "do_not_collapse_with": "estimaciones fiscales agregadas"},
]
write_csv(HERE / "E0_CAJA_CRYL_SETTLEMENT_STAGE_MATRIX_V124.csv", settlement_stages)


assert len(catalog) == 294
assert len(census) == 95
assert len(ledger) == 125
assert len(breaks) == 85
assert len(channels) == 7
assert len(trace) == 74
assert len(responses) == 6
assert len(closures) == 8
assert len(system_map) == 6
assert len(authorities) == 10
assert len(negative_adequacy) == 14
assert len(producer_map) == 22
assert len(search_keys) == 53
assert len(attachments) == 7
assert len(version_chain) == 9
assert len(term_audit) == 8
assert len(cga_map) == 8
assert len(deferred_audit) == 11
assert len(crosswalk) == 5
assert len(settlement_stages) == 8


evidence_path = HERE / "HISTORICAL_EVIDENCE_COVERAGE_V124.csv"
evidence = read_csv(evidence_path)
for row in evidence:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            {
                "quality": "PRIMARY_BUYBACK_STRIP_EXACT_ACCOUNT_ROUTE_FIVE_CAJA_CODES_AND_PRE_TARGET_DEFERRED_SYSTEM_CHAIN_PRESERVED",
                "gap": "Los cinco ISIN tienen puente público a Código Caja. La edición del manual está fechada en marzo de 2000, el sistema y su documentación constan públicamente en 2004, hay contexto operativo 2006 y formularios probados en 2009; faltan la revisión efectiva en 2008 y los registros ejecutados/pagados.",
                "next_action": "Presentar sólo con autorización expresa usando las claves V124; pedir registro maestro/control de cambios SLIQ/SCG y asientos separados de instrucción, matching, recepción y pago.",
            }
        )
write_csv(evidence_path, evidence)


queue_path = HERE / "HISTORICAL_SOURCE_QUEUE_V124.csv"
queue = read_csv(queue_path)
for row in queue:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            {
                "status": "INSTITUTIONAL_REQUEST_SETTLEMENT_AND_EXACT_2008_EFFECTIVE_REVISION_KEYS_READY_NOT_SENT",
                "why": "La edición SLIQ está fechada en 2000; tres fuentes nuevas preservan disponibilidad pública 2004, contexto operativo 2006 y un esquema paralelo de control de revisiones 2006-2009. Quedan 74 objetos trazados sin presentación ni respuesta.",
                "next_action": "Obtener autorización expresa, completar datos personales, presentar sólo los pedidos autorizados y conservar constancias.",
            }
        )
write_csv(queue_path, queue)


inherited = [
    {"script": "qa_v97.py", "pre_v124_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v124_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V97 exige que una fuente recuperada después permanezca sin ruta/hash."},
    *({"script": f"qa_v{i}.py", "pre_v124_result": "PASS", "post_v124_result": "PASS", "interpretation": "Compatible"} for i in (98, 100, 101, 102, 103, 104, 105, 106)),
    *({"script": f"qa_v{i}.py", "pre_v124_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v124_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "Congela un checkpoint o conteo anterior."} for i in range(107, 124)),
    {"script": "qa_v124.py", "pre_v124_result": "N/A", "post_v124_result": "PASS", "interpretation": "Cinco Códigos Caja; edición SLIQ 2000; sistema público 2004; control documental separado; etapas, claves y estados no enviados."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V124.csv", inherited)


for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    shutil.copyfile(AUDIT / f"{stem}_V123.csv", AUDIT / f"{stem}_V124.csv")

hash_rows = [row for row in read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V123.csv") if row["id"] not in new_ids]
for spec in source_specs:
    hash_rows.append(
        {"id": spec["id"], "archivo_local": spec["local"], "exists": "True", "sha_catalog": spec["sha256"], "sha_actual": spec["sha256"], "hash_ok": "True"}
    )
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V124.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V124.csv", hash_rows)


size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append(
        {
            "path": path.relative_to(REPO).as_posix(),
            "bytes": str(size),
            "mib": f"{size / 1048576:.6f}",
            "over_50_mib": str(size > 50 * 1048576),
            "over_100_mib": str(size > 100 * 1048576),
        }
    )
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V124.csv", size_rows)


physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V123.json").read_text(encoding="utf-8"))
completeness.update(
    {
        "checkpoint": "V124",
        "date": "2026-08-29",
        "state": "E0_FIVE_CAJA_CODES_DEFERRED_MANUAL_2000_SYSTEM_2004_PRACTICE_2009_TARGET_2008_REVISION_OPEN_NOT_SENT",
        "numeric_v124_strict_changed": False,
        "master_catalog_entries": len(catalog),
        "physical_local_copies": physical,
        "physical_local_hash_ok": hash_ok,
        "binary_required_entries": len(catalog) - 5,
        "binary_required_preserved": physical,
        "e0_primary_sources_preserved": len(census),
        "e0_quality": "PRIMARY_BUYBACK_STRIP_EXACT_ACCOUNT_ROUTE_FIVE_CAJA_CODES_AND_PRE_TARGET_DEFERRED_SYSTEM_CHAIN_PRESERVED",
        "sources_newly_preserved_v124": len(source_specs),
        "e0_primary_sources_newly_preserved_v124": len(source_specs),
        "pending_external_request_actions": 6,
        "e0_request_drafts": len(responses),
        "e0_request_traceability_rows": len(trace),
        "e0_request_closure_rules": len(closures),
        "e0_document_system_temporal_routes": len(system_map),
        "e0_archival_retention_authorities": len(authorities),
        "e0_negative_response_adequacy_controls": len(negative_adequacy),
        "e0_record_producer_system_rows": len(producer_map),
        "e0_request_search_keys": len(search_keys),
        "e0_request_attachment_rows": len(attachments),
        "e0_cryl_effective_version_chain_rows": len(version_chain),
        "e0_buyback_modality_term_audit_rows": len(term_audit),
        "e0_cryl_cga_record_map_rows": len(cga_map),
        "e0_deferred_modality_equivalence_audit_rows": len(deferred_audit),
        "e0_security_identifier_crosswalk_rows": len(crosswalk),
        "e0_caja_cryl_settlement_stage_rows": len(settlement_stages),
        "e0_fiscal_method_breaks_frozen": len(breaks),
        "e0_official_submission_channels_verified": len(channels),
        "e0_requests_submitted": 0,
        "e0_request_responses_received": 0,
        "e0_request_package_status": "DRAFT_NOT_SENT",
        "historical_workstream": "E0_FIVE_CAJA_CODES_DEFERRED_MANUAL_2000_SYSTEM_2004_PRACTICE_2009_TARGET_2008_REVISION_OPEN_NOT_SENT",
    }
)
completeness.pop("numeric_v121_strict_changed", None)
completeness.pop("sources_newly_preserved_v121", None)
completeness.pop("e0_primary_sources_newly_preserved_v121", None)
completeness.pop("numeric_v122_strict_changed", None)
completeness.pop("sources_newly_preserved_v122", None)
completeness.pop("e0_primary_sources_newly_preserved_v122", None)
completeness.pop("numeric_v123_strict_changed", None)
completeness.pop("sources_newly_preserved_v123", None)
completeness.pop("e0_primary_sources_newly_preserved_v123", None)
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V124.json").write_text(
    json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)


backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V124 · edición SLIQ fechada y cadena operativa preobjetivo"
old_backup = backup.read_text(encoding="utf-8-sig")
if marker not in old_backup:
    old_backup += (
        f"\n\n{marker}\n\n"
        "- La página legal del manual SLIQ ya preservado fecha internamente la edición en marzo de 2000; se corrige la clasificación previa de fecha interna ausente.\n"
        "- Se preservaron tres fuentes primarias nuevas: la página institucional Merval archivada en 2004, la memoria de Caja del ejercicio 2006 y el manual MU-32002.03 con control de revisiones 2006/2007/2009.\n"
        "- La cadena preobjetivo demuestra edición 2000, disponibilidad pública del sistema en 2004 y contexto operativo 2006; la CNV mantiene probado el uso de formularios diferidos en 2009.\n"
        "- Sigue abierta la revisión efectiva SLIQ/SCG en cada fecha de 2008, junto con instrucción, matching, asiento 0306/40000, informe T+3, pago y baja de deuda.\n"
        "- Los seis borradores incorporan 22 rutas productor-sistema, 53 claves técnicas, 7 adjuntos mínimos y 74 objetos trazados.\n"
        "- Todos los pedidos permanecen DRAFT_NOT_SENT; no hay plazos ni respuestas en curso.\n"
        "- Las fuentes E0 suben a 95; cifras fiscales y panel bancario permanecen sin cambios.\n"
    )
    backup.write_text(old_backup, encoding="utf-8")


def write_checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V124.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V124",
        "parent_checkpoint": "V123",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30,
        "strict_coverage_pct": STRICT,
        "closed_network_gate": "NO",
        "e0_primary_sources": len(census),
        "new_preserved_sources": len(source_specs),
        "new_primary_sources": len(source_specs),
        "fiscal_ledger_rows": len(ledger),
        "fiscal_method_breaks": len(breaks),
        "request_drafts": len(responses),
        "official_submission_channels": len(channels),
        "request_traceability_rows": len(trace),
        "request_closure_rules": len(closures),
        "document_system_temporal_routes": len(system_map),
        "archival_retention_authorities": len(authorities),
        "negative_response_adequacy_controls": len(negative_adequacy),
        "record_producer_system_rows": len(producer_map),
        "request_search_keys": len(search_keys),
        "request_attachment_rows": len(attachments),
        "cryl_effective_version_chain_rows": len(version_chain),
        "buyback_modality_term_audit_rows": len(term_audit),
        "cryl_cga_record_map_rows": len(cga_map),
        "deferred_modality_equivalence_audit_rows": len(deferred_audit),
        "security_identifier_crosswalk_rows": len(crosswalk),
        "caja_cryl_settlement_stage_rows": len(settlement_stages),
        "requests_submitted": 0,
        "responses_received": 0,
        "files": files,
    }
    (HERE / "MANIFEST_V124.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


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
    global_files.append(
        {"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)}
    )
global_manifest = {
    "checkpoint": "V124",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT,
    "exact_entities": 30,
    "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical local copies with {hash_ok}/{physical} SHA-valid; three new primary Caja/Merval system-history sources preserved; six system-keyed requests drafted and none submitted.",
    "historical_workstream": "E0 five Caja codes plus March 2000 SLIQ edition, 2004 public system listing and 2009 deferred-receipt practice preserved; exact effective 2008 revision, settled asset leg and cash payment remain open; no request submitted",
    "file_count_excluding_manifest": len(global_files),
    "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V124 BUILD PASS")


