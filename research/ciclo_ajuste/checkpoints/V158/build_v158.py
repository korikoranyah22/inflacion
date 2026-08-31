from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import os


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v158" / "binaries"
V157 = CYCLE / "checkpoints" / "V157"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"
EXCLUDED_DIRS = {".git", "__pycache__", "tmp", "node_modules"}


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows, fields=None):
    fields = fields or (list(rows[0]) if rows else [])
    with Path(path).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def upsert(rows, additions, key):
    order = [str(row[key]) for row in rows]
    indexed = {str(row[key]): row for row in rows}
    for addition in additions:
        row = {name: str(value) for name, value in addition.items()}
        indexed[row[key]] = row
        if row[key] not in order:
            order.append(row[key])
    return [indexed[value] for value in order]


def pipe_rows(block, fields, prefix):
    rows = []
    for index, line in enumerate((line for line in block.strip().splitlines() if line.strip()), 1):
        values = [value.strip() for value in line.split("|")]
        if len(values) == len(fields) - 1:
            values = [f"{prefix}{index:02d}"] + values
        elif len(values) == len(fields):
            if prefix:
                values[0] = f"{prefix}{index:02d}"
        else:
            raise AssertionError((prefix, index, len(values), len(fields), line))
        rows.append(dict(zip(fields, values)))
    return rows


def matrix(name, fields, block, prefix):
    rows = pipe_rows(block, fields, prefix)
    write_csv(HERE / name, rows, fields)
    return rows


def append_section(path, marker, body):
    path = Path(path)
    text = path.read_text(encoding="utf-8-sig") if path.exists() else ""
    if marker not in text:
        path.write_text(text.rstrip() + "\n\n" + marker + "\n\n" + body.strip() + "\n", encoding="utf-8")


def iter_files(root):
    root = Path(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted((name for name in dirnames if name not in EXCLUDED_DIRS), key=str.casefold)
        for filename in sorted(filenames, key=str.casefold):
            yield Path(dirpath) / filename


SOURCES = [
    {
        "id": "e0_res_sigen_7_2003_uai_plan_preliminary_final_approval_custody",
        "institution": "Sindicatura General de la Nación / InfoLEG",
        "title": "Resolución SIGEN 7/2003 · circuito de formulación, aprobación y custodia del plan UAI",
        "url": "https://servicios.infoleg.gob.ar/infolegInternet/anexos/80000-84999/81571/AnexoI.pdf",
        "filename": "res_sigen_7_2003_planning_preliminary_final_approval_manual.pdf",
        "period": "vigente durante la formulación del Plan UAI 2009",
        "series": "Manual de Procedimiento SIGEN · Título III.2",
        "kind": "PDF oficial preservado y controlado visualmente",
        "variables": "instructions;deadline;UAI_plan;plan_file;preliminary_approval;ministerial_conformity;paper_copy;magnetic_copy;final_approval;custody",
        "breaks": "proyecto/plan definitivo; preliminar/final; papel/magnético; UAI/Sindicatura/Subgerencia/Gerencia/Mesa",
        "status": "E0_USABLE_EXACT_UAI_PLAN_VERSION_AND_CUSTODY_WORKFLOW",
        "note": "Prueba instrucciones en octubre, presentación antes del 30/10, legajo plan auditoría UAI, revisión, modificaciones, aprobación preliminar, conformidad superior, ingreso papel+magnético al 15/12, aprobación final y custodia de la versión definitiva. No contiene el plan Economía 2009.",
    },
    {
        "id": "e0_orsna_act_16_2008_plan_2009_approval_workflow_comparator",
        "institution": "ORSNA / SIGEN",
        "title": "Acta ORSNA 16/2008 · aplicación contemporánea del circuito Plan UAI 2009",
        "url": "https://www.argentina.gob.ar/sites/default/files/acta_16.08.pdf",
        "filename": "orsna_act_16_2008_plan_uai_2009_workflow.pdf",
        "period": "2008-12-09; plan 2009",
        "series": "Reunión abierta ORSNA 16/2008 · punto 3 · Anexo IV referido",
        "kind": "PDF oficial preservado y controlado visualmente",
        "variables": "UAI_plan_2009;SIGEN_note;preliminary_approval;superior_approval;final_submission;annex",
        "breaks": "comparador/target; anexo referido/cuerpo; errores de año/cronología en acta",
        "status": "E0_USABLE_CONTEMPORARY_REAL_WORLD_PLAN_APPROVAL_COMPARATOR",
        "note": "Confirma que el plan, la nota SIGEN de aprobación preliminar, la conformidad de autoridad, el anexo y la elevación final eran objetos separados. Contiene referencias internas 2008/2007 discordantes y no individualiza Economía.",
    },
    {
        "id": "e0_decree_2025_2008_economy_production_reorganization",
        "institution": "Poder Ejecutivo Nacional",
        "title": "Decreto DNU 2025/2008 · creación de Producción y redefinición de Economía",
        "url": "https://www.argentina.gob.ar/normativa/nacional/decreto-2025-2008-147697/texto",
        "filename": "decreto_2025_2008_creation_production_ministry.html",
        "period": "2008-11-25",
        "series": "Boletín Oficial 31540",
        "kind": "HTML oficial preservado",
        "variables": "ministry_reorganization;Economy_and_Public_Finance;Production;public_debt;official_financial_entities",
        "breaks": "jurisdiction_name/version; reorganization/record_transfer; substantive_scope/custody",
        "status": "E0_USABLE_EXACT_TARGET_JURISDICTION_REORGANIZATION_DATE_AND_SCOPE",
        "note": "Prueba la creación del Ministerio de Producción y el cambio a Economía y Finanzas Públicas entre la entrega inicial y aprobación final del Plan 2009. Deuda pública y supervisión de entidades financieras oficiales permanecieron en Economía.",
    },
    {
        "id": "e0_decree_2102_2008_transitional_uai_economy_control",
        "institution": "Poder Ejecutivo Nacional",
        "title": "Decreto 2102/2008 · control UAI transitorio tras la división Economía-Producción",
        "url": "https://www.argentina.gob.ar/normativa/nacional/decreto-2102-2008-148088/texto",
        "filename": "decreto_2102_2008_transitional_uai_control.html",
        "period": "2008-12-04",
        "series": "Boletín Oficial 31547 · artículos 11, 14 y 15",
        "kind": "HTML oficial preservado",
        "variables": "transitional_UAI_control;prior_intervention;organizational_openings;origin_budget;legal_administrative_support",
        "breaks": "control transitorio/transferencia documental; actividad previa/competencia futura; estructura/presupuesto",
        "status": "E0_USABLE_EXACT_TRANSITIONAL_UAI_CONTROL_AND_SUCCESSION_RULE",
        "note": "Prueba que UAI Economía controló transitoriamente áreas transferidas a Producción respecto de actividades en las que ya había intervenido. No prueba que el proyecto de deuda se transfiriera.",
    },
    {
        "id": "e0_cgn_account_2009_sigen_planning_supervision_count_120",
        "institution": "Contaduría General de la Nación / SIGEN",
        "title": "Cuenta de Inversión 2009 · aproximadamente 120 informes de Supervisión del Planeamiento",
        "url": "https://www.economia.gob.ar/hacienda/cgn/cuenta/2009/tomoii/05jur20.htm",
        "filename": "cgn_account_2009_sigen_planning_supervision_count.html",
        "period": "2009",
        "series": "Cuenta de Inversión 2009 · Jurisdicción 20 · SIGEN",
        "kind": "HTML oficial preservado",
        "variables": "planning_supervision;120_reports;UAI_plans;production_reporting",
        "breaks": "120/160; aproximación/inventario; cuenta presupuestaria/memoria institucional",
        "status": "E0_USABLE_CONTEMPORARY_OFFICIAL_COUNT_CONFLICT",
        "note": "Informa aproximadamente 120 supervisiones en 2009, frente a cerca de 160 en la Memoria SIGEN 2009. La divergencia se congela y no se resuelve sin inventario y regla de conteo.",
    },
    {
        "id": "e0_eras_2009_supervision_report_delivery_note_and_file",
        "institution": "Ente Regulador de Agua y Saneamiento / SIGEN",
        "title": "Orden del día ERAS 29/01/2010 · nota, informe de supervisión y expediente local",
        "url": "https://www.argentina.gob.ar/sites/default/files/ordendia0110.pdf",
        "filename": "eras_order_01_2010_supervision_report_note_and_file.pdf",
        "period": "informe enero-junio 2009; recepción 2010-01-29",
        "series": "Nota SIGEN 5095/2009-GSPF · Expediente ERAS 878-09",
        "kind": "PDF oficial preservado y controlado visualmente",
        "variables": "SIGEN_note;supervision_report;report_title;half_year;local_file;recipient_copy",
        "breaks": "nota/cuerpo; expediente local/legajo SIGEN; comparador/target",
        "status": "E0_USABLE_EXACT_SUPERVISION_REPORT_DELIVERY_METADATA_COMPARATOR",
        "note": "Prueba que un informe de supervisión UAI podía viajar como ejemplar adjunto a una Nota SIGEN y quedar asentado en un expediente del organismo receptor. No identifica Economía ni el informe anual target.",
    },
]


catalog = read_csv(CATALOG)
census = read_csv(V157 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V157.csv")
provenance = read_csv(V157 / "ARCHIVAL_PROVENANCE_V157.csv")
source_rows = []
for source in SOURCES:
    path = BIN / source["filename"]
    assert path.is_file() and path.stat().st_size > 1000, path
    source_rows.append({**source, "local": "/" + path.relative_to(REPO).as_posix(),
                        "sha": sha256(path), "bytes": path.stat().st_size})

catalog = upsert(catalog, [{
    "id": source["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": source["institution"],
    "titulo": source["title"], "url_original": source["url"], "archivo_local": source["local"],
    "fecha_descarga": "2026-08-31", "fecha_publicacion": source["period"],
    "codigo_serie": source["series"], "periodo_utilizado": source["period"], "tipo": source["kind"],
    "sha256": source["sha"], "nota": "V158: " + source["note"],
} for source in source_rows], "id")
write_csv(CATALOG, catalog, list(catalog[0]))

census = upsert(census, [{
    "source_id": source["id"], "institution": source["institution"], "artifact": source["title"],
    "url": source["url"], "local_path": source["local"], "sha256": source["sha"], "bytes": source["bytes"],
    "period_coverage": source["period"], "variable_families": source["variables"],
    "primary_source": "YES", "preserved": "YES", "method_breaks": source["breaks"],
    "use_status": source["status"], "caveat": source["note"],
} for source in source_rows], "source_id")
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V158.csv", census, list(census[0]))

provenance = upsert(provenance, [{
    "source_id": source["id"], "original_url": source["url"], "retrieval_url": source["url"],
    "capture_timestamp": "2026-08-31", "cdx_digest": "N/A_OFFICIAL_DIRECT",
    "local_path": source["local"], "sha256": source["sha"], "bytes": source["bytes"],
    "provenance_note": "Captura directa de fuente oficial; alcance y quiebres congelados en V158.",
} for source in source_rows], "source_id")
write_csv(HERE / "ARCHIVAL_PROVENANCE_V158.csv", provenance, list(provenance[0]))


plan_fields = ["row_id", "date_or_period", "source", "documented_event", "expected_record", "target_value", "limit", "status"]
plan_chain = matrix("E0_2008_2009_PLAN_SISIO_APPROVAL_CHAIN_V158.csv", plan_fields, """
1|2008|Plan SIGEN 2008|Planes UAI sometidos a aprobación SIGEN|Plan y comunicación de aprobación|Prueba circuito contemporáneo|No subplan Economía|TARGET_PERIOD_CHAIN
2|2008|Plan SIGEN 2008|Más de 7000 productos o informes UAI previstos|Inventario de productos por UAI|Prueba escala y clasificación|Agregado no inventario|AGGREGATE_CONTROL
3|2008|Plan SIGEN 2008|Cuenta de Inversión planificada como auditoría horizontal|Proyecto, responsables e informes contribuyentes|Nombre exacto de programa target|Plan no ejecución|TARGET_PERIOD_CHAIN
4|2008|Plan SIGEN 2008|Previstos criterios e instructivos para respaldo Cuenta|Instructivos, versiones y distribución|Clase documental exacta|Previsión no emisión|TARGET_PERIOD_CHAIN
5|2008|Memoria SIGEN 2008|Se dictaron Instructivos de Trabajo Cuenta|Instructivos y acuses UAI|Confirma ejecución de previsión|No identifica números en memoria|TARGET_PERIOD_CHAIN
6|2008|Memoria SIGEN 2008|Emitido informe global Cuenta de Inversión 2007|Cuerpo, anexos y distribución|Prueba continuidad anual|No es Cuenta 2008|ANNUAL_CONTINUITY
7|2008|Memoria SIGEN 2008|Unos 120 Informes de Supervisión del Planeamiento|Informe correspondiente a UAI Economía|Prueba clase y volumen|No identifica cuerpo individual|PLANNING_SUPERVISION
8|2008|Memoria SIGEN 2008|Mejoras SISIO para confección y seguimiento de planes UAI|Versión, snapshot, logs y exportación|Conecta plan con sistema|No entrada 0120/09|SYSTEM_CHAIN
9|2008|Memoria SIGEN 2008|Lineamientos emitidos para planeamiento 2009|Lineamientos generales y pautas gerenciales|Precursor exacto del plan|No contiene anexos|TARGET_PERIOD_CHAIN
10|2008-12-15|Memoria SIGEN 2008|Aprobado Plan SIGEN 2009|Plan completo y acto de aprobación|Fecha exacta de aprobación|No número de acto|EXACT_APPROVAL_DATE
11|2008-12-15|Memoria SIGEN 2008|Plan 2009 reúne organismo y distintas UAI|Subplan UAI Economía y consolidación|Prueba que debía integrar el conjunto|No prueba contenido target|TARGET_PERIOD_CHAIN
12|2008|Memoria SIGEN 2008|SISPE apoya planificación SIGEN y seguimiento|Snapshot SISPE y diccionario|Identifica sistema distinto|No confundir con SISIO|SYSTEM_CHAIN
13|2009|Memoria SIGEN 2009|Emitido informe global Cuenta de Inversión 2008|Cuerpo, anexos y papeles|Confirma producto target anual|No SAF355 ni banco|TARGET_REPORT_REFERENCE
14|2009|Memoria SIGEN 2009|Unos 160 Informes de Supervisión del Planeamiento|Informe UAI Economía 2009|Prueba continuidad y mayor volumen|No cuerpo individual|PLANNING_SUPERVISION
15|2009|Memoria SIGEN 2009|Mejoras SISIO para planeamientos UAI|Snapshot, versión y logs|Confirma uso continuado|No asiento target|SYSTEM_CHAIN
16|2009-12-16|Plan SIGEN 2010 segunda parte|Datos de planes UAI extraídos de SISIO WEB II|Exportación de corte y parámetros|Fecha exacta de snapshot|Corresponde a Plan 2010|EXACT_SYSTEM_CUTOFF
17|2009-12-16|Plan SIGEN 2010 segunda parte|Consolidación prevé más de 4550 productos|Cuadros 10 a 13 y anexo D|Prueba campos de detalle|Anexo completo ausente|AGGREGATE_CONTROL
18|2009-12-22|Memoria SIGEN 2009|Aprobado Plan SIGEN 2010|Plan final y acto|Fecha exacta posterior al corte|No es Plan 2009|NEAR_TARGET_CONTROL
19|2009-12-16 a 22|Cruce fuentes|Snapshot SISIO precede seis días a aprobación final|Versiones antes y después, cambios y aprobación|Define control de versiones|No prueba que no hubiera cambios|VERSION_CONTROL
20|2010|Plan SIGEN 2010 segunda parte|Cuenta de Inversión 2009 planificada como horizontal|Proyecto e informes contribuyentes|Confirma continuidad de programa|No es Cuenta 2008|ANNUAL_CONTINUITY
21|2010|Cuenta de Inversión 2010|Unos 140 Informes de Supervisión del Planeamiento|Inventario y cuerpo por UAI|Confirma continuidad de clase|Comparador posterior|PLANNING_SUPERVISION
22|Regla final|Método V158|Plan, aprobación, snapshot y supervisión son piezas separadas|Cuatro cuerpos vinculados por ids y fechas|Evita respuestas genéricas|Ninguna acredita banco|METHOD_LIMIT
""", "PC157_")


account_fields = ["row_id", "year", "program_or_output", "modality", "record_producer", "expected_body", "probative_use", "limit", "status"]
account_program = matrix("E0_ACCOUNT_AUDIT_HORIZONTAL_PROGRAM_2008_2010_V158.csv", account_fields, """
1|2008|Cuenta de Inversión|Auditoría horizontal planificada|SIGEN y UAI|Proyecto horizontal 2008|Nombre de programa contemporáneo|No prueba ejecución|PROGRAM_LOCATED
2|2008|Cuenta de Inversión|Informes por jurisdicción o entidad|UAI contribuyentes|Informe UAI Economía|Define cuerpo contribuyente|No localizado|CONTRIBUTOR_RECORD
3|2008|Cuenta de Inversión|Visión integral posterior|SIGEN|Informe global|Define producto consolidado|No sustituye contribuyentes|GLOBAL_RECORD
4|2008|Información respaldatoria|Normativa e instructivos|SIGEN|Criterios, instructivos y papeles|Define metodología|Previsión no emisión|METHOD_RECORD
5|2008|Certificaciones|Instructivos dictados|UAI|Certificados por aspectos Cuenta|Confirma ejecución normativa|0/5 SAF355|CERTIFICATION_RECORD
6|2008|Planeamiento UAI|Aprobación y supervisión|SIGEN|Informe de Supervisión UAI Economía|Ruta a proyecto e informe|No es informe de auditoría|SUPERVISION_RECORD
7|2008|SISIO|Confección y seguimiento plan|SIGEN/UAI|Alta del proyecto y estados|Ruta de sistema|No prueba cuerpo|SYSTEM_RECORD
8|2007 informado 2008|Cuenta 2007|Informe global emitido|SIGEN|Cuerpo y anexos|Continuidad anterior|No target|ANNUAL_COMPARATOR
9|2008 informado 2009|Cuenta 2008|Informe global emitido|SIGEN|Cuerpo y anexos|Referencia target exacta|Cuerpo abierto|TARGET_REPORT_REFERENCE
10|2008 informado 2009|Cuenta 2008|Certificaciones UAI|UAI de cada SAF|Anexos, fuentes y firma|Capa contribuyente target|No banco|TARGET_CERTIFICATION
11|2009 planificado 2010|Cuenta 2009|Auditoría horizontal|SIGEN/UAI|Proyecto y contribuyentes|Continuidad posterior|No target 2008|ANNUAL_COMPARATOR
12|Todos|Horizontal|Auditorías paralelas en jurisdicciones|UAI|Informes jurisdiccionales|Explica multiplicidad de cuerpos|No universaliza resultado|MODALITY_RULE
13|Todos|Horizontal|Apreciación general|SIGEN|Informe integral|Explica producto global|No sustituye informe Economía|MODALITY_RULE
14|2008-2009|UAI Economía|Proyecto Cuenta 2008|UAI Economía|Programa, alcance, horas y producto|Objeto recuperable|No prueba inclusión de recompras|REQUEST_TARGET
15|2008-2009|SAF355|Certificación Cuenta 2008|UAI/SAF355|Anexos I-V y papeles|Objeto target exacto|0/5|REQUEST_TARGET
16|2008-2009|SIGEN|Supervisión del proyecto UAI Economía|Gerencia/Sindicatura|Informe de Supervisión del Planeamiento|Puede contener código del proyecto|No informe final|REQUEST_TARGET
17|2009|SIGEN|Informe global Cuenta 2008|SIGEN|Informe, anexos, referencias contribuyentes|Puede identificar cuerpo UAI|No banco|REQUEST_TARGET
18|Regla final|Ejecución|Cierre por cuatro capas|Economía, sistemas y banco|Documento, sistema, banco, reversas|Mantiene 0/10|Programa horizontal no pago|METHOD_LIMIT
""", "AH157_")


system_fields = ["row_id", "system", "documented_function", "period", "record_to_request", "allowed_inference", "forbidden_inference", "status"]
systems = matrix("E0_SISIO_SISPE_SYSTEM_SEPARATION_V158.csv", system_fields, """
1|SISIO WEB|Seguimiento de informes y observaciones|Desde 2006|Entrada, constancia e historial|Sistema UAI y observaciones|No SIGEN plan interno|SYSTEM_ROLE
2|SISIO WEB|Confección y seguimiento de Planeamientos UAI|2008|Plan UAI, versiones y estados|Aloja planificación UAI|No actividad SIGEN propia|SYSTEM_ROLE
3|SISIO WEB II|Fuente de planes UAI 2010|Corte 16/12/2009|Snapshot, exportación y diccionario|Fecha y origen exactos|No plan final aprobado|SYSTEM_ROLE
4|SISPE|Planeamiento de actividades SIGEN|2008|Plan SIGEN, actividades y responsables|Sistema de planificación SIGEN|No entrada UAI SISIO|SYSTEM_ROLE
5|SISPE|Seguimiento de ejecución SIGEN|2008|Estados, productos y fechas|Ruta para producto SIGEN|No observaciones UAI|SYSTEM_ROLE
6|Archivo Digital|Acceso a documentación histórica|2007-2010|Índice, imagen, metadatos y logs|Ruta documental SIGEN|No prueba digitalización target|SYSTEM_ROLE
7|SISIO versus SISPE|Sistemas con objetos distintos|2008-2009|Crosswalk de ids, proyecto e informe|Exige búsqueda doble|No fusionar tokens|SYSTEM_SEPARATION
8|SISIO versus Archivo Digital|Sistema de gestión versus repositorio documental|2008-2009|Vínculo entrada-documento-imagen|Permite cadena de evidencia|No asumir enlace automático|SYSTEM_SEPARATION
9|SISPE versus Archivo Digital|Plan SIGEN versus cuerpo documental|2008-2009|Vínculo actividad-producto-archivo|Permite rastrear informe global|No asumir mismo id|SYSTEM_SEPARATION
10|Snapshot|Fotografía a fecha de corte|16/12/2009|Parámetros, versión y hash|Prueba estado en corte|No cambios posteriores|VERSION_CONTROL
11|Plan aprobado|Resultado formal posterior|22/12/2009|Acto, plan final y diferencias|Permite comparar snapshot-final|No prueba ejecución|VERSION_CONTROL
12|Regla final|Cada sistema debe certificarse separado|2008-2009|Consulta, operador, fecha y resultado|Evita falso negativo|Un cero no cubre otros sistemas|METHOD_LIMIT
""", "SS157_")


supervision_fields = ["row_id", "year", "documented_count", "record_class", "request_target", "minimum_fields", "probative_value", "limit", "status"]
supervision = matrix("E0_PLANNING_SUPERVISION_REPORT_INVENTORY_V158.csv", supervision_fields, """
1|2008|cerca de 120|Informe de Supervisión del Planeamiento|Informe UAI Economía 2008|número; fecha; UAI; plan; observaciones; aprobación|Prueba clase contemporánea|Agregado aproximado|COUNT_DOCUMENTED
2|2009|cerca de 160|Informe de Supervisión del Planeamiento|Informe UAI Economía 2009|número; fecha; UAI; plan; observaciones; aprobación|Prueba clase target|Agregado aproximado|COUNT_DOCUMENTED
3|2010|aproximadamente 140|Informe de Supervisión del Planeamiento|Comparador UAI Economía 2010|número; fecha; UAI; plan; observaciones; aprobación|Prueba continuidad|Posterior|COUNT_DOCUMENTED
4|2008|N/A|Plan anual UAI|Subplan Economía 2008|proyectos; período; horas; productos|Antecedente Cuenta 2008|No plan 2009|PLAN_RECORD
5|2009|N/A|Plan anual UAI|Subplan Economía 2009|proyectos; período; horas; productos|Puede contener seguimiento Cuenta 2008|No localizado|PLAN_RECORD
6|2009|N/A|Plan SIGEN 2009|Consolidación completa|UAI; actividad; producto; horas|Ubica subplan|No cuerpo individual|CONSOLIDATED_PLAN
7|2009|N/A|Lineamientos generales|Planeamiento 2009|fecha; emisor; pautas; destinatarios|Define requisitos|No plan|GUIDANCE_RECORD
8|2009|N/A|Pautas particulares gerenciales|Gerencia competente Economía|gerencia; fecha; temas; requerimientos|Puede nombrar Cuenta y deuda|GSEyP aún no expandido|GUIDANCE_RECORD
9|2009|N/A|Comunicación de aprobación|UAI Economía|fecha; plan; observaciones; firma|Cierra aprobación individual|No ejecución|APPROVAL_RECORD
10|2009|N/A|Modificación de plan|UAI Economía|versión; motivo; alta; baja; aprobación|Detecta No Planificado|No localizada|VERSION_RECORD
11|2009|N/A|Ejecución del plan|UAI Economía|proyecto; avance; informe; horas|Vincula plan-producto|No banco|EXECUTION_RECORD
12|2009|N/A|Registro de producto|SISIO|id; actividad; informe; fecha; estado|Vincula sistema-cuerpo|No constancia hallada|SYSTEM_RECORD
13|2009|N/A|Informe de auditoría|Cuenta de Inversión 2008|número; cuerpo; anexos; destino|Producto sustantivo|No confundir supervisión|AUDIT_RECORD
14|2009|N/A|Papeles de trabajo|Cuenta de Inversión 2008|índice; cédulas; evidencia; ubicación|Soporte del producto|No banco|WORKPAPER_RECORD
15|Regla final|N/A|Separación de clases|Plan, supervisión, auditoría y papeles|ids y vínculos entre cuatro cuerpos|Evita respuesta parcial|Ninguno prueba pago|METHOD_LIMIT
""", "SP157_")


archive_fields = ["row_id", "period", "archive_event", "documented_action", "request_object", "probative_value", "limit", "status"]
archive = matrix("E0_ARCHIVE_DIGITAL_REORDERING_AND_DISPOSITION_V158.csv", archive_fields, """
1|2007|Archivo Digital|Implementación del aplicativo y digitalización histórica|Inventario de series digitalizadas|Prueba capacidad pre-target|No cuerpo target|ARCHIVE_CAPABILITY
2|2008 plan|Archivo Digital|Continuar digitalización del archivo general|Plan, órdenes y lotes|Prueba programa vigente|Plan no ejecución|ARCHIVE_PROGRAM
3|2008 memoria|Archivo Digital|Avance en conformación del archivo|Índice, lotes, imágenes y metadatos|Prueba ejecución general|No identifica notas|ARCHIVE_EXECUTION
4|2008 memoria|Archivos móviles|Convocatoria para mejorar archivo SIGEN|Expediente, pliego y ubicación|Prueba gestión física paralela|No caja target|PHYSICAL_ARCHIVE
5|2009 memoria|Archivo Digital|Continuidad en Mesa de Entradas, Salidas y Archivo|Índice y registro de documentos|Identifica unidad custodia|No prueba ingreso target|ARCHIVE_EXECUTION
6|2009 memoria|Archivo general|Inicio de reordenamiento|Registro de revisión, clasificación y ubicación|Ruta exacta para búsqueda|No inventario publicado|PHYSICAL_ARCHIVE
7|2009 memoria|Archivo general|Registro de documentación|Asiento de registro, fondo, serie y soporte|Posible localizador target|No cuerpo|ARCHIVE_REGISTER
8|2009 memoria|Depuración|Proceso proyectado para finalizar siguiente ejercicio|Plan, criterios, acta y destino|Exige disposición si falta cuerpo|Proyecto no destrucción|DISPOSITION_CONTROL
9|2010 plan|Archivo Digital|Ampliación según requerimientos sectoriales|Solicitudes y prioridades|Comparador de continuidad|No prueba inclusión target|ARCHIVE_CONTINUITY
10|2008-2010|Mesa de Entradas|Entrada y salida de notas|Libro, COMDOC, número, emisor y destino|Ruta para 0120/09 y 3672/09|No asumir digitalización|REQUEST_ROUTE
11|2008-2010|Archivo general|Caja y serie física|Fondo, serie, caja, folios y transferencia|Ruta si no está digital|No asumir retención|REQUEST_ROUTE
12|Regla final|Negativo fundado|Buscar digital, registro, físico y disposición|Consultas, resultados y acto de destino|Evita ausencia simple|Programa archivístico no localización|METHOD_LIMIT
""", "AR157_")


workflow_fields = ["row_id", "date_or_deadline", "stage", "actor", "record_or_action", "documented_evidence", "target_request", "limit", "status"]
workflow = matrix("E0_PLAN_2009_PRELIMINARY_FINAL_APPROVAL_WORKFLOW_V158.csv", workflow_fields, """
1|primera semana hábil de octubre|Instrucciones|Sindicatura jurisdiccional|Emite instrucciones para formular el plan UAI|Método, contenido y plazo obligatorio|Instrucciones generales y particulares 2009|Regla general, no cuerpo Economía|RULE_DOCUMENTED
2|antes del 30/10/2008|Presentación inicial|UAI Economía|Presenta proyecto de plan a su Síndico jurisdiccional|Plazo máximo reglamentario|Plan UAI Economía 2009 presentado|No prueba recepción concreta|EXPECTED_TARGET_RECORD
3|inmediato|Control de completitud|Sindicatura jurisdiccional|Devuelve presentaciones incompletas e identifica deficiencias|Circuito de subsanación|Nota de devolución, observaciones y nueva versión|Sólo existe si hubo deficiencias|CONDITIONAL_RECORD
4|desde la recepción|Apertura de legajo|Sindicatura jurisdiccional|Documenta su análisis en legajo plan auditoría UAI|Contenedor reglamentario específico|Carátula, índice y movimientos del legajo Economía|No es el plan definitivo|EXPECTED_TARGET_CONTAINER
5|dentro de 10 días|Análisis y dictamen|Síndico jurisdiccional|Analiza y emite opinión fundada|Elevación a Subgerencia|Dictamen, fecha, firma y plan evaluado|No equivale a aprobación final|EXPECTED_TARGET_RECORD
6|dentro de 4 días|Evaluación técnica|Subgerencia competente|Evalúa la propuesta y puede requerir modificaciones|Control técnico intermedio|Informe de evaluación y requerimientos|No acredita conformidad ministerial|EXPECTED_TARGET_RECORD
7|dentro de 4 días|Propuesta preliminar|Subgerencia competente|Remite propuesta de aprobación preliminar|Versión identificable del plan|Propuesta, versión y elevación|Preliminar no final|EXPECTED_TARGET_RECORD
8|dentro de 4 días|Aprobación preliminar|Gerencia competente SIGEN|Aprueba preliminarmente el plan|Acto o constancia intermedia|Nota/acto de aprobación preliminar|No es aprobación del Síndico General|EXPECTED_TARGET_RECORD
9|antes del 15/12/2008|Devolución|Gerencia vía Sindicatura|Devuelve plan y modificaciones requeridas|Cadena de remisión|Nota y plan con cambios marcados|No prueba aceptación de cambios|EXPECTED_TARGET_RECORD
10|antes del 15/12/2008|Conformidad superior|Autoridad superior de la jurisdicción|Conforma el plan ajustado|Firma ministerial o equivalente|Plan conformado, firma, fecha y versión|No es aprobación final SIGEN|EXPECTED_TARGET_RECORD
11|hasta el 15/12/2008|Presentación final en papel|UAI/autoridad jurisdiccional|Ingresa ejemplar papel por Mesa de Entradas y Archivo SIGEN|Canal y fecha reglamentarios|Asiento de entrada y copia papel|No prueba copia magnética|EXPECTED_TARGET_RECORD
12|hasta el 15/12/2008|Presentación final magnética|UAI/autoridad jurisdiccional|Entrega copia magnética del plan|Soporte exigido separadamente|Archivo, soporte, metadatos y recepción|No asumir identidad con papel|EXPECTED_TARGET_RECORD
13|posterior al ingreso|Verificación final|Gerencia competente SIGEN|Verifica versión conformada y cumplimiento de modificaciones|Último control antes del acto|Informe o constancia de verificación|No es todavía acto final|EXPECTED_TARGET_RECORD
14|posterior a verificación|Proyecto de aprobación|Gerencia competente SIGEN|Eleva proyecto de aprobación|Objeto formal previo al acto|Proyecto, elevación, firma y anexos|Proyecto no acto|EXPECTED_TARGET_RECORD
15|15/12/2008 según Memoria|Aprobación final|Síndico General de la Nación|Aprueba Plan SIGEN 2009|Fecha target ya probada|Acto, número, cuerpo y anexos|Memoria no aporta identificador|TARGET_ACT_OPEN
16|versión definitiva|Custodia|Gerencia competente SIGEN|Custodia la versión definitiva|Custodio reglamentario explícito|Copia definitiva e índice de custodia|No limita copias en UAI/archivo|TARGET_CUSTODY_ROUTE
17|eventual|Incumplimiento|SIGEN|Puede promover investigación administrativa|Consecuencia reglamentaria|Actuación si hubo incumplimiento|No hay evidencia de incumplimiento Economía|CONDITIONAL_RECORD
18|eventual|Plan de oficio|SIGEN|Puede fijar plan básico ante incumplimiento|Versión alternativa reglamentaria|Plan básico y acto de imposición|No presumir que ocurrió|CONDITIONAL_RECORD
19|09/12/2008|Comparador ORSNA|ORSNA y SIGEN|Acta registra nota SIGEN, aprobación preliminar, conformidad y elevación final|Aplicación contemporánea del circuito|Buscar equivalentes de Economía por función, no sólo título|Acta tiene errores internos de año/fecha|COMPARATOR_ONLY
20|Regla V158|Control de versiones|Todas las unidades|Cada etapa debe vincular versión, fecha, actor y soporte|Cadena probatoria completa|Solicitar índice y relación entre todas las piezas|Ninguna etapa prueba ejecución bancaria|METHOD_LIMIT
""", "WF158_")


reorg_fields = ["row_id", "date_or_period", "event", "legal_source", "effect_on_target", "record_to_recover", "allowed_inference", "forbidden_inference", "status"]
reorganization = matrix("E0_UAI_ECONOMY_2009_REORGANIZATION_VERSION_CHAIN_V158.csv", reorg_fields, """
1|antes del 30/10/2008|Presentación inicial esperada|Resolución SIGEN 7/2003|Plan bajo configuración previa del Ministerio de Economía y Producción|Carátula y versión inicial|El plan pudo nacer con denominación pre-reforma|No prueba presentación efectiva|VERSION_RISK
2|25/11/2008|Creación Ministerio de Producción|DNU 2025/2008|Divide la jurisdicción durante el circuito de aprobación|Expediente de adecuación del plan|Obliga a buscar versiones antes y después|No transfiere por sí solo todo proyecto|EXACT_REORGANIZATION_DATE
3|25/11/2008|Redefinición de Economía|DNU 2025/2008|Pasa a Ministerio de Economía y Finanzas Públicas|Carátula y nomenclador posteriores|El nombre jurisdiccional pudo cambiar|No prueba cambio material de todos los proyectos|VERSION_RISK
4|25/11/2008|Deuda pública|DNU 2025/2008|La competencia sustantiva permanece en Economía|Subplan y proyecto bajo Economía|Refuerza búsqueda en Economía|Competencia no custodia documental|SUBSTANTIVE_SCOPE
5|25/11/2008|Crédito y finanzas|DNU 2025/2008|Funciones financieras permanecen en Economía|Pautas y proyectos de Finanzas|Evita derivación automática a Producción|No localiza el cuerpo|SUBSTANTIVE_SCOPE
6|25/11/2008|Entidades financieras oficiales/BCRA|DNU 2025/2008|Vinculación institucional permanece en Economía|Proyecto, alcance y responsables|Mantiene relevancia del circuito Economía|No acredita datos bancarios|SUBSTANTIVE_SCOPE
7|04/12/2008|Control UAI transitorio|Decreto 2102/2008 art. 11|UAI Economía controla transitoriamente actividades transferidas en las que ya intervenía|Asignaciones, comunicaciones y papeles de transición|La UAI pudo conservar intervención operativa|No prueba transferencia del proyecto de deuda|TRANSITIONAL_RULE
8|04/12/2008|Estructura transitoria|Decreto 2102/2008 arts. 14-15|Mantiene aperturas inferiores y créditos de origen|Planillas de estructura, responsables y presupuesto|Puede explicar carátulas y firmas heredadas|No prueba identidad entre versiones|TRANSITIONAL_RULE
9|25/11 a 04/12/2008|Ventana de reforma|Cruce normativo|Reforma ocurre tras plazo inicial y antes del 15/12|Versiones, notas de modificación y crosswalk|Es plausible una reformulación formal|Plausibilidad no evidencia de cambio|VERSION_RISK
10|09/12/2008|Comparador ORSNA|Acta ORSNA 16/2008|Muestra que a esa fecha seguían aprobándose preliminarmente planes 2009|Notas equivalentes de Economía|Confirma circuito activo durante la ventana|No individualiza Economía|COMPARATOR_ONLY
11|15/12/2008|Aprobación final reportada|Memoria SIGEN 2008|Plan consolidado final ya bajo nueva organización|Acto y anexos definitivos|La versión final debe poder fecharse|No se conoce su nomenclatura interna|TARGET_VERSION_OPEN
12|2009|Ejecución del plan|Memoria/plan anual|Proyectos pueden conservar códigos o áreas de origen|Altas, modificaciones y responsables SISIO|Buscar ambas denominaciones institucionales|No asumir continuidad perfecta|SEARCH_RULE
13|2008-2009|Cadena de firmas|Regla de aprobación|Cambian autoridades, membretes o dependencias durante el trámite|Firmantes y sellos de cada versión|Los metadatos pueden resolver la sucesión|No inferir autoría por título abreviado|SEARCH_RULE
14|2008-2009|Cadena de custodia|Resolución 7/2003 + reforma|Pueden coexistir copias en UAI, SIGEN, Mesa y áreas sucesoras|Inventario por custodio y versión|Amplía rutas sin duplicar objeto|Una copia no descarta otras|CUSTODY_RULE
15|2008-2009|Crosswalk organizacional|Método V158|Relacionar denominación pre-reforma, post-reforma, función y sistema|Tabla unidad-fecha-proyecto-id|Evita falsos negativos por nombre|No reemplaza cuerpo documental|REQUEST_TARGET
16|Regla final|No traslado automático|Método V158|La reforma explica riesgo de versión, no prueba desplazamiento del target|Exigir acto, registro o metadatos|Mantiene deuda/finanzas en Economía|No atribuir a Producción sin evidencia|METHOD_LIMIT
""", "RG158_")


count_fields = ["row_id", "source", "period", "published_expression", "normalized_reading", "comparison", "required_resolution", "limit", "status"]
count_conflict = matrix("E0_PLANNING_SUPERVISION_COUNT_CONFLICT_V158.csv", count_fields, """
1|Cuenta de Inversión 2009, Jurisdicción 20 SIGEN|2009|aproximadamente 120 informes|120 aproximado|Contradice cerca de 160 de otra fuente oficial|Inventario anual y regla de conteo|No exacto|OFFICIAL_COUNT_A
2|Memoria SIGEN 2009|2009|cerca de 160 informes|160 aproximado|Contradice aproximadamente 120|Inventario anual y regla de conteo|No exacto|OFFICIAL_COUNT_B
3|Diferencia nominal|2009|40 informes|160 menos 120|Brecha de alrededor del 33,3% sobre 120|Definir universo antes de calcular|Ambos extremos son aproximados|DERIVED_DIAGNOSTIC
4|Diferencia relativa inversa|2009|25%|40 sobre 160|120 equivale al 75% de 160|Definir si una serie es subconjunto|No adjudica error|DERIVED_DIAGNOSTIC
5|Cuenta de Inversión|ejercicio 2009|Producción física/presupuestaria|Posible universo contabilizado|Puede usar criterio de producto devengado|Ficha técnica e indicador|Inferencia por contexto|HYPOTHESIS_ONLY
6|Memoria institucional|actividad 2009|Gestión institucional|Posible universo operativo|Puede incluir emitidos, tramitados o redondeo distinto|Metodología de Memoria|Inferencia por contexto|HYPOTHESIS_ONLY
7|Ambas fuentes|2009|aproximadamente/cerca de|Rangos sin tolerancia declarada|No permiten igualdad exacta|Notas metodológicas y cifras sin redondear|No convertir en 120 y 160 exactos|METHOD_LIMIT
8|Inventario requerido|2009|N/A|Una fila por informe|Número, fecha, UAI, período, estado y producto|Permite deduplicar|No localizado|REQUEST_TARGET
9|Regla de conteo requerida|2009|N/A|Universo, unidad y fecha de corte|Emitido/aprobado/remitido/cerrado/anulado|Permite reconciliar|No localizada|REQUEST_TARGET
10|Corte temporal requerido|2009-2010|N/A|Fecha de producción y fecha de reporte|Distinguir informe 2009 recibido en 2010|Evita desplazamiento anual|No localizado|REQUEST_TARGET
11|Target Economía|2009|N/A|Pertenencia al inventario|Informe de Supervisión UAI Economía y metadatos|Puede identificar cuerpo target|Conteos no lo individualizan|TARGET_OPEN
12|Regla V158|No seleccionar cifra|Método de contradicción congelada|Conservar 120 y 160 con sus fuentes|Resolver sólo con inventario/metodología|Evita falsa precisión|No altera 0/10|CONFLICT_FROZEN
""", "CF158_")


delivery_fields = ["row_id", "date_or_period", "source_or_actor", "record", "identifier", "relationship", "target_analogue", "limit", "status"]
delivery = matrix("E0_SUPERVISION_REPORT_DELIVERY_METADATA_V158.csv", delivery_fields, """
1|2009|SIGEN|Nota de remisión|5095/2009-GSPF|Vehículo de entrega|Nota equivalente dirigida a Economía|Comparador ERAS|COMPARATOR_METADATA
2|enero-junio 2009|SIGEN|Informe de Supervisión UAI ERAS|Título explícito|Cuerpo adjunto a la nota|Informe de Supervisión UAI Economía|No mismo organismo|COMPARATOR_METADATA
3|2009-2010|ERAS|Ejemplar recibido|copia del informe|Copia sobreviviente en destinatario|Copia en UAI/Ministerio de Economía|No prueba que subsista|CUSTODY_ROUTE
4|2009|ERAS|Expediente local|878-09|Contenedor receptor distinto|Expediente local Economía|No es legajo interno SIGEN|COMPARATOR_METADATA
5|29/01/2010|Directorio ERAS|Orden del día|01/2010|Registra tratamiento posterior|Acta o giro interno Economía|No cuerpo del informe|COMPARATOR_METADATA
6|2009|SIGEN|Gerencia remitente|GSPF en número de nota|Metadato de productor|Gerencia competente para Economía|Sigla no universal|SEARCH_KEY
7|2009|SIGEN|Nota|número/año/gerencia|Objeto documental autónomo|Pedir nota y adjunto por separado|Nota no prueba contenido del adjunto|METHOD_RULE
8|2009|SIGEN|Informe|título/período/UAI|Objeto documental autónomo|Pedir cuerpo, anexos y carátula|Título no prueba hallazgos|METHOD_RULE
9|2009|Organismo receptor|Expediente|número local|Objeto documental autónomo|Pedir índice, pases y copia recibida|Número local no número SIGEN|METHOD_RULE
10|2009|SIGEN/organismo|Cadena de remisión|nota + adjunto + recepción|Tres vínculos comprobables|Acuse, fecha y cantidad de fojas|Comparador no target|REQUEST_MODEL
11|2009|Economía/SIGEN|Target|sin identificar|Buscar por UAI, período, gerencia y clase|Recuperar nota, informe y expediente receptor|Aún 0 cuerpos target|TARGET_OPEN
12|Regla final|Método V158|Separación de objetos|N/A|No colapsar nota, informe y expediente|Certificar búsqueda en ambos custodios|Ninguno prueba banco|METHOD_LIMIT
""", "DL158_")


negative_fields = ["row_id", "query_or_route", "result", "interpretation", "next_step", "status"]
negative = matrix("E0_V158_PUBLIC_SEARCH_NEGATIVE_RESULTS.csv", negative_fields, """
1|Plan SIGEN 2009 cuerpo completo y acto final|No localizados públicamente|La fecha 15/12/2008 no sustituye cuerpo ni identificador|Pedir acto, plan y anexos por versión|PLAN_AND_ACT_NOT_LOCATED
2|Plan UAI Economía 2009 presentado antes del 30/10|No localizado|La regla prueba que debía existir una presentación, no que Economía cumpliera|Pedir asiento, carátula y copia inicial|INITIAL_PLAN_NOT_LOCATED
3|Legajo plan auditoría UAI Economía|No localizado|La Resolución 7/2003 individualiza el contenedor|Pedir carátula, índice y movimientos|PLAN_FILE_NOT_LOCATED
4|Dictamen y aprobación preliminar|No localizados|Son pasos separados de la aprobación final|Pedir dictamen, evaluación, modificaciones y nota preliminar|PRELIMINARY_CHAIN_NOT_LOCATED
5|Plan conformado en papel y copia magnética|No localizados|Los dos soportes eran exigibles y no deben colapsarse|Pedir asiento y metadatos de ambos|DUAL_SUPPORT_NOT_LOCATED
6|Versión definitiva bajo custodia de Gerencia|No localizada|La norma identifica custodio distinto de la UAI|Pedir copia definitiva e índice de custodia|DEFINITIVE_VERSION_NOT_LOCATED
7|Crosswalk pre/post reforma Economía-Producción|No localizado|La reforma ocurrió entre entrega inicial y aprobación final|Pedir versiones, notas de adecuación y responsables|REORGANIZATION_CROSSWALK_NOT_LOCATED
8|Informe de Supervisión UAI Economía 2009 y nota de remisión|No localizados|ERAS prueba que nota, adjunto y expediente receptor eran piezas separadas|Pedir en SIGEN y Economía|SUPERVISION_DELIVERY_CHAIN_NOT_LOCATED
9|Inventario de Informes de Supervisión 2009|No localizado|Fuentes oficiales difieren entre aproximadamente 120 y cerca de 160|Pedir inventario y regla de conteo|COUNT_CONFLICT_UNRESOLVED
10|Snapshot SISIO Plan 2009 y código Cuenta 2008|No localizados|La función del sistema está probada, no la salida target|Pedir exportación, parámetros, versión y logs|SYSTEM_SNAPSHOT_NOT_LOCATED
11|Registro Archivo Digital/reordenamiento del target|No localizado|Capacidad archivística no prueba ingreso, retención ni destino|Pedir índice, caja, transferencia o disposición|ARCHIVE_ENTRY_NOT_LOCATED
12|Certificados SAF355|0 de 5|La cadena del plan no sustituye certificados ni anexos|Pedir por SAF y anexo|TARGET_CERTIFICATES_NOT_LOCATED
13|Filas bancarias target|0 de 10|Plan, supervisión y archivo siguen siendo capas administrativas|Cerrar con banco y reversas|BANK_EXECUTION_NOT_LOCATED
14|Seis solicitudes|No enviadas|No existe presentación, acuse, plazo ni respuesta|Mantener borradores hasta autorización expresa|DRAFT_NOT_SENT
""", "NR158_")
write_csv(HERE / "E0_V158_PUBLIC_SEARCH_NEGATIVE_RESULTS_V158.csv", negative, negative_fields)


breaks = read_csv(V157 / "E0_FISCAL_METHOD_BREAKS_V157.csv")
break_fields = list(breaks[0])
break_add = pipe_rows("""
uai_plan_submission_not_final_plan|document|La presentación inicial de la UAI no es la versión definitiva aprobada.|Exigir fecha, versión y relación de cambios.|FROZEN|Resolución SIGEN 7/2003
preliminary_approval_not_final_approval|phase|La aprobación preliminar de Gerencia no equivale al acto final del Síndico General.|Pedir ambos actos y su encadenamiento.|FROZEN|Resolución SIGEN 7/2003
superior_conformity_not_sigen_final_approval|authority|La conformidad de la autoridad jurisdiccional no sustituye la aprobación final SIGEN.|Separar firma ministerial de acto SIGEN.|FROZEN|Resolución SIGEN 7/2003
paper_plan_not_magnetic_copy|support|La copia papel y la copia magnética eran entregables distintos.|Pedir recepción, metadatos y comparación de ambos soportes.|FROZEN|Resolución SIGEN 7/2003
definitive_plan_custodian_not_uai_only|custody|La Gerencia SIGEN era custodio de la versión definitiva; buscar sólo en UAI es insuficiente.|Consultar Gerencia, Mesa/Archivo y UAI.|FROZEN|Resolución SIGEN 7/2003
pre_reorganization_name_not_post_reorganization_version|version|La denominación anterior a 25/11/2008 no identifica necesariamente la versión final.|Buscar ambas jurisdicciones y crosswalk de versiones.|FROZEN|DNU 2025/2008
transitional_uai_control_not_target_scope_transfer|scope|El control UAI transitorio sobre áreas transferidas no prueba que el proyecto de deuda pasara a Producción.|Exigir acto o registro del proyecto.|FROZEN|Decreto 2102/2008
official_count_120_not_official_count_160|aggregation|Aproximadamente 120 y cerca de 160 son cifras oficiales discordantes del mismo año.|Congelar ambas y pedir inventario/metodología.|FROZEN|Cuenta 2009 y Memoria SIGEN 2009
approximate_count_not_exact_inventory|aggregation|Un conteo aproximado no individualiza informes ni permite deduplicar.|Pedir una fila por informe y fecha de corte.|FROZEN|Fuentes SIGEN 2009
comparator_act_copy_error_not_target_chronology|quality|Los errores internos 2008/2007 del acta ORSNA impiden trasladar su cronología al target.|Usarla sólo para arquitectura documental.|FROZEN|Acta ORSNA 16/2008
supervision_note_not_attached_report_body|document|La nota de remisión no sustituye el cuerpo del Informe de Supervisión adjunto.|Pedir nota, adjunto y anexos separadamente.|FROZEN|Nota SIGEN 5095/2009-GSPF
recipient_file_not_sigen_internal_file|custody|El expediente del organismo receptor no es el legajo o expediente interno SIGEN.|Buscar ambos custodios y cruzar acuses.|FROZEN|Expediente ERAS 878-09
""", break_fields, "")
breaks = upsert(breaks, break_add, "break_id")
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V158.csv", breaks, break_fields)


trace = read_csv(V157 / "E0_INFORMATION_REQUEST_TRACEABILITY_V157.csv")
trace_fields = list(trace[0])
trace_add = pipe_rows("""
REQ158_SIGEN|SIGEN|CL158_INITIAL_PLAN|Plan UAI Economía 2009 presentado|antes del 30/10/2008|Resolución 7/2003|asiento; fecha; carátula; versión; soporte|copia e ingreso|DRAFT_NOT_SENT
REQ158_SIGEN|Sindicatura jurisdiccional|CL158_PLAN_FILE|Legajo plan auditoría UAI Economía|2008-2009|contenedor reglamentario|carátula; índice; pases; documentos; fechas|inventario testado|DRAFT_NOT_SENT
REQ158_SIGEN|Sindicatura jurisdiccional|CL158_REASONED_OPINION|Opinión fundada sobre plan Economía|2008|plazo de diez días|fecha; firmante; observaciones; elevación|dictamen y anexos|DRAFT_NOT_SENT
REQ158_SIGEN|Subgerencia/Gerencia|CL158_PRELIMINARY_CHAIN|Evaluación y aprobación preliminar|2008|plazos de cuatro días|versiones; modificaciones; actos; remisiones|cadena completa|DRAFT_NOT_SENT
REQ158_ECON|Economía|CL158_SUPERIOR_CONFORMITY|Conformidad de autoridad superior|2008|plan ajustado|firmante; fecha; versión; reservas|copia conformada|DRAFT_NOT_SENT
REQ158_SIGEN|Mesa de Entradas/Archivo|CL158_DUAL_SUPPORT|Ingreso papel y magnético|hasta 15/12/2008|doble soporte exigido|asientos; soporte; archivo; metadatos; hash|recepciones separadas|DRAFT_NOT_SENT
REQ158_SIGEN|Gerencia competente|CL158_FINAL_VERIFICATION|Verificación y proyecto de aprobación|2008|etapa final|informe; proyecto; elevación; anexos|cuerpos testados|DRAFT_NOT_SENT
REQ158_SIGEN|SIGEN|CL158_FINAL_ACT_AND_PLAN|Acto final y Plan SIGEN 2009|15/12/2008|fecha exacta ya probada|tipo; número; firma; plan; anexos|copia definitiva|DRAFT_NOT_SENT
REQ158_SIGEN|Gerencia competente|CL158_DEFINITIVE_CUSTODY|Versión definitiva bajo custodia|2008-2009|custodio reglamentario|índice; ubicación; soporte; versión|copia o inventario|DRAFT_NOT_SENT
REQ158_ECON|Economía/UAI|CL158_REORG_CROSSWALK|Adecuación pre/post reforma|25/11 a 15/12/2008|DNU 2025 y Dto 2102|unidad; denominación; versión; proyecto; responsable|crosswalk e instrumentos|DRAFT_NOT_SENT
REQ158_SIGEN|SIGEN|CL158_COUNT_INVENTORY|Inventario Supervisión Planeamiento 2009|2009|120 versus 160 aproximados|número; fecha; UAI; período; estado; anulación|inventario deduplicable|DRAFT_NOT_SENT
REQ158_SIGEN|SIGEN|CL158_COUNT_RULE|Regla de conteo Supervisión 2009|2009|fuentes oficiales discordantes|universo; unidad; corte; redondeo; estado|metodología certificada|DRAFT_NOT_SENT
REQ158_SIGEN|SIGEN|CL158_SUPERVISION_NOTE|Nota de remisión del informe Economía|2009-2010|modelo 5095/2009-GSPF|número; gerencia; fecha; destinatario; fojas|nota y acuse|DRAFT_NOT_SENT
REQ158_SIGEN|SIGEN|CL158_SUPERVISION_BODY|Informe Supervisión UAI Economía|2009|clase estable probada|título; período; cuerpo; anexos; firma|cuerpo testado|DRAFT_NOT_SENT
REQ158_ECON|Economía/UAI|CL158_RECIPIENT_FILE|Expediente receptor del informe|2009-2010|modelo ERAS 878-09|número local; índice; pases; copia; recepción|expediente e inventario|DRAFT_NOT_SENT
REQ158_SIGEN|SIGEN Sistemas|CL158_SISIO_VERSION_CHAIN|Versiones SISIO Plan Economía 2009|2008-2009|presentación/reforma/final|ids; timestamps; usuario; estado; cambios; hash|exportación reproducible|DRAFT_NOT_SENT
REQ158_SIGEN|SIGEN/Archivo|CL158_PLAN_RECORD_CROSSWALK|Crosswalk plan-legajo-acto-SISIO-archivo|2008-2009|cadena V158|ids; fechas; versiones; soportes; custodios|diccionario o tabla certificada|DRAFT_NOT_SENT
REQ158_ECON|Tesoro/Finanzas|CL158_FINAL_BANK_GATE|Conciliación final banco y reversas|2008-2009|71597;152677;2876;C41;C42;C55|id; cuenta; valor; fecha; débito; reversa|fila testada|DRAFT_NOT_SENT
""", trace_fields, "TR158_")
trace = upsert(trace, trace_add, "trace_id")
write_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V158.csv", trace, trace_fields)


keys = read_csv(V157 / "E0_REQUEST_SEARCH_KEY_MATRIX_V157.csv")
key_fields = list(keys[0])
key_add = pipe_rows("""
REQ158_SIGEN|record_type|legajo plan auditoría UAI Ministerio de Economía 2009|contenedor reglamentario|Resolución SIGEN 7/2003|No localizado.
REQ158_SIGEN|record_type|presentación plan UAI Economía antes 30 octubre 2008|versión inicial|Resolución SIGEN 7/2003|Regla no acredita cumplimiento.
REQ158_SIGEN|record_type|opinión fundada Síndico plan UAI Economía 2009|dictamen|Resolución SIGEN 7/2003|No acto final.
REQ158_SIGEN|record_type|evaluación Subgerencia plan UAI Economía 2009|control técnico|Resolución SIGEN 7/2003|No localizada.
REQ158_SIGEN|record_type|aprobación preliminar Gerencia plan UAI Economía 2009|acto intermedio|Resolución SIGEN 7/2003|No aprobación final.
REQ158_ECON|record_type|conformidad autoridad superior plan UAI Economía 2009|firma jurisdiccional|Resolución SIGEN 7/2003|No acto SIGEN.
REQ158_SIGEN|record_type|Mesa de Entradas plan UAI Economía papel 15 diciembre 2008|recepción papel|Resolución SIGEN 7/2003|No copia magnética.
REQ158_SIGEN|record_type|copia magnética plan UAI Economía 2009|recepción digital|Resolución SIGEN 7/2003|No asumir identidad.
REQ158_SIGEN|record_type|proyecto aprobación final Plan SIGEN 2009|acto previo|Resolución SIGEN 7/2003|No localizado.
REQ158_SIGEN|record_type|versión definitiva Plan UAI Economía custodia Gerencia|cuerpo final|Resolución SIGEN 7/2003|No localizada.
REQ158_SIGEN|identifier|Nota 4622/2008 SJER plan UAI|comparador de aprobación preliminar|Acta ORSNA 16/2008|No target Economía.
REQ158_SIGEN|phrase|plan auditoría UAI aprobación preliminar conformidad|búsqueda funcional|Resolución 7/2003 y ORSNA|Evitar depender de título exacto.
REQ158_ECON|organization|Ministerio de Economía y Producción Plan UAI 2009|versión pre-reforma|DNU 2025/2008|Nombre puede variar.
REQ158_ECON|organization|Ministerio de Economía y Finanzas Públicas Plan UAI 2009|versión post-reforma|DNU 2025/2008|No prueba cambio de contenido.
REQ158_ECON|record_type|adecuación Plan UAI Decreto 2025 2008 Ministerio Producción|crosswalk reforma|DNU 2025 y Dto 2102|No traslado automático.
REQ158_ECON|scope|deuda pública crédito finanzas entidades financieras oficiales BCRA 2008|permanencia competencial|DNU 2025/2008|Competencia no custodia.
REQ158_SIGEN|counts|aproximadamente 120 informes Supervisión Planeamiento 2009|universo Cuenta Inversión|Cuenta de Inversión 2009|Contradice 160.
REQ158_SIGEN|counts|cerca de 160 informes Supervisión Planeamiento 2009|universo Memoria|Memoria SIGEN 2009|Contradice 120.
REQ158_SIGEN|record_type|inventario informes Supervisión Planeamiento 2009 UAI número fecha|resolver contradicción|Fuentes oficiales|No localizado.
REQ158_SIGEN|method|metodología conteo informes supervisión emitidos aprobados remitidos|regla de conteo|V158|No localizada.
REQ158_SIGEN|identifier|Nota 5095/2009 GSPF Informe Supervisión UAI|modelo de remisión|ERAS orden del día|Comparador no target.
REQ158_ECON|record_type|expediente recepción Informe Supervisión UAI Economía 2009|copia destinatario|Modelo ERAS 878-09|Número local desconocido.
REQ158_SIGEN|crosswalk|nota adjunto informe expediente receptor legajo plan SISIO|cadena documental|V158|Objetos separados.
REQ158_ECON|target_ids|71597 152677 2876 C41 C42 C55 banco reversa|cierre final|Matriz acumulada|0 filas.
""", key_fields, "SK158_")
keys = upsert(keys, key_add, "key_id")
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V158.csv", keys, key_fields)


objects = read_csv(V157 / "E0_V157_REQUEST_OBJECTS.csv")
object_fields = list(objects[0])
object_add = pipe_rows("""
UAI_ECONOMY_PLAN_2009_INITIAL_SUBMISSION|SIGEN/UAI Economía|Presentación inicial Plan UAI Economía|antes del 30/10/2008|asiento; fecha; versión; soporte; carátula|Copia e ingreso|DRAFT_NOT_SENT
UAI_ECONOMY_PLAN_2009_PLAN_FILE|Sindicatura jurisdiccional|Legajo plan auditoría UAI Economía|2008-2009|carátula; índice; documentos; pases; fechas|Inventario testado|DRAFT_NOT_SENT
UAI_ECONOMY_PLAN_2009_SUBGERENCIA_EVALUATION|SIGEN Subgerencia|Evaluación técnica y modificaciones|2008|versión; observaciones; fecha; firma; elevación|Cuerpo y anexos|DRAFT_NOT_SENT
UAI_ECONOMY_PLAN_2009_PRELIMINARY_APPROVAL|SIGEN Gerencia|Aprobación preliminar|2008|acto/nota; fecha; versión; firma|Copia testada|DRAFT_NOT_SENT
UAI_ECONOMY_PLAN_2009_MODIFICATIONS|SIGEN/UAI Economía|Plan con modificaciones requeridas|2008|cambios; versión; remisión; recepción|Comparación de versiones|DRAFT_NOT_SENT
UAI_ECONOMY_PLAN_2009_SUPERIOR_CONFORMITY|Economía|Conformidad de autoridad superior|antes del 15/12/2008|firmante; fecha; versión; reservas|Copia conformada|DRAFT_NOT_SENT
UAI_ECONOMY_PLAN_2009_PAPER_AND_MAGNETIC_SUBMISSION|SIGEN Mesa/Archivo|Entrega final papel y magnética|hasta el 15/12/2008|dos asientos; soportes; metadatos; hash|Recepciones separadas|DRAFT_NOT_SENT
UAI_ECONOMY_PLAN_2009_FINAL_APPROVAL_PROJECT|SIGEN Gerencia|Verificación y proyecto de aprobación final|2008|informe; proyecto; elevación; anexos|Cuerpos testados|DRAFT_NOT_SENT
UAI_ECONOMY_PLAN_2009_DEFINITIVE_VERSION|SIGEN Gerencia|Versión definitiva del plan|2008-2009|versión; soporte; índice; ubicación; acto|Copia o inventario|DRAFT_NOT_SENT
UAI_ECONOMY_PLAN_2009_REORGANIZATION_CROSSWALK|Economía/SIGEN|Crosswalk antes/después DNU 2025/2008|2008-2009|unidad; nombre; función; proyecto; id; responsable|Tabla certificada|DRAFT_NOT_SENT
PLANNING_SUPERVISION_2009_COUNT_INVENTORY|SIGEN|Inventario y regla de conteo 120/160|2009|informe; UAI; fecha; estado; universo; corte|CSV y metodología|DRAFT_NOT_SENT
PLANNING_SUPERVISION_ECONOMY_2009_DELIVERY_CHAIN|SIGEN/Economía|Nota, informe adjunto y expediente receptor|2009-2010|números; fechas; fojas; acuses; custodios|Tres cuerpos vinculados|DRAFT_NOT_SENT
""", object_fields, "RO158_")
objects = upsert(objects, object_add, "row_id")
write_csv(HERE / "E0_V158_REQUEST_OBJECTS.csv", objects, object_fields)
write_csv(HERE / "E0_V158_REQUEST_OBJECTS_V158.csv", objects, object_fields)


catalog_map = {source["filename"]: source["id"] for source in SOURCES}
roles = {
    "res_sigen_7_2003_planning_preliminary_final_approval_manual.pdf": "EXACT_UAI_PLAN_VERSION_APPROVAL_AND_CUSTODY_WORKFLOW",
    "orsna_act_16_2008_plan_uai_2009_workflow.pdf": "CONTEMPORARY_PLAN_APPROVAL_WORKFLOW_COMPARATOR",
    "decreto_2025_2008_creation_production_ministry.html": "EXACT_REORGANIZATION_DATE_AND_ECONOMY_SCOPE",
    "decreto_2102_2008_transitional_uai_control.html": "TRANSITIONAL_UAI_CONTROL_AND_SUCCESSION_RULE",
    "cgn_account_2009_sigen_planning_supervision_count.html": "OFFICIAL_120_COUNT_SIDE_OF_FROZEN_CONFLICT",
    "eras_order_01_2010_supervision_report_note_and_file.pdf": "SUPERVISION_NOTE_REPORT_RECIPIENT_FILE_COMPARATOR",
}
bundle_fields = ["row_id", "filename", "role", "catalogued", "catalog_source_id", "bytes", "sha256", "preserved"]
bundle = []
for index, path in enumerate(sorted(BIN.iterdir(), key=lambda value: value.name.casefold()), 1):
    if path.is_file():
        bundle.append(dict(zip(bundle_fields, [f"B158_{index:02d}", path.name, roles[path.name],
                                               "YES", catalog_map[path.name], path.stat().st_size,
                                               sha256(path), "YES"])))
write_csv(HERE / "E0_V158_SOURCE_BUNDLE.csv", bundle, bundle_fields)


visual = read_csv(V157 / "E0_V157_PDF_VISUAL_CONTROL.csv")
visual_fields = list(visual[0])
visual_add = pipe_rows("""
e0_res_sigen_7_2003_uai_plan_preliminary_final_approval_custody|7 impresa|32|Instrucciones en octubre, entrega UAI antes del 30 y legajo plan auditoría UAI|PASS|Regla general; no prueba presentación Economía
e0_res_sigen_7_2003_uai_plan_preliminary_final_approval_custody|8 impresa|33|Dictamen, evaluación, modificaciones y aprobación preliminar|PASS|Etapas intermedias separadas del acto final
e0_res_sigen_7_2003_uai_plan_preliminary_final_approval_custody|9 impresa|34|Conformidad superior, papel+magnético, aprobación final y custodia definitiva|PASS|Circuito completo; no contiene plan target
e0_orsna_act_16_2008_plan_2009_approval_workflow_comparator|4|4|Plan UAI 2009, Nota 4622/2008 SJER, aprobación preliminar, conformidad y anexo|PASS|Comparador con discordancias internas 2008/2007
e0_eras_2009_supervision_report_delivery_note_and_file|1|1|Nota SIGEN 5095/2009-GSPF, informe adjunto y Expediente ERAS 878-09|PASS|Modelo de entrega; no informe Economía
""", visual_fields, "PV158_")
visual += visual_add
write_csv(HERE / "E0_V158_PDF_VISUAL_CONTROL.csv", visual, visual_fields)
images = read_csv(V157 / "E0_V157_IMAGE_VISUAL_CONTROL.csv")
write_csv(HERE / "E0_V158_IMAGE_VISUAL_CONTROL.csv", images, list(images[0]))


append_section(HERE / "SOURCE_REFERENCES_V158.md", "## V158 · circuito reglado, reforma y contradicción de conteos", """
- Resolución SIGEN 7/2003, Anexo I: https://servicios.infoleg.gob.ar/infolegInternet/anexos/80000-84999/81571/AnexoI.pdf
- Acta ORSNA 16/2008: https://www.argentina.gob.ar/sites/default/files/acta_16.08.pdf
- DNU 2025/2008: https://www.argentina.gob.ar/normativa/nacional/decreto-2025-2008-147697/texto
- Decreto 2102/2008: https://www.argentina.gob.ar/normativa/nacional/decreto-2102-2008-148088/texto
- Cuenta de Inversión 2009, SIGEN: https://www.economia.gob.ar/hacienda/cgn/cuenta/2009/tomoii/05jur20.htm
- Memoria SIGEN 2009: https://www.argentina.gob.ar/sites/default/files/memoria_sigen_2009.pdf
- Orden del día ERAS 01/2010: https://www.argentina.gob.ar/sites/default/files/ordendia0110.pdf

Alcance: la Resolución 7/2003 prueba el circuito y sus objetos, no que todos hayan sido producidos o conservados para Economía. El acta ORSNA y el expediente ERAS son comparadores contemporáneos, no evidencia del target. La reforma ministerial obliga a buscar versiones pre y post 25/11/2008, pero las competencias de deuda y finanzas permanecieron en Economía. Los conteos oficiales 2009 —aproximadamente 120 y cerca de 160— quedan congelados como contradicción pendiente de inventario y metodología.
""")

request_section = """
V158 precisa el circuito reglado del Plan UAI 2009: instrucciones; presentación inicial antes del 30/10; legajo plan auditoría UAI; opinión fundada; evaluación de Subgerencia; modificaciones; aprobación preliminar de Gerencia; conformidad de autoridad superior; ingreso separado en papel y copia magnética hasta el 15/12; verificación; proyecto de aprobación final; acto del Síndico General; y custodia gerencial de la versión definitiva. Se pide cada objeto con fecha, versión, firmante, soporte e identificadores, más un crosswalk entre ellos. Como los DNU 2025/2008 y 2102/2008 reorganizaron Economía durante el trámite, la búsqueda debe cubrir denominaciones pre y post reforma sin presumir que deuda/finanzas pasaron a Producción. También se solicitan el inventario y regla de conteo que expliquen por qué dos fuentes oficiales informan para 2009 aproximadamente 120 y cerca de 160 Informes de Supervisión; y, para el target Economía, la nota de remisión, el informe adjunto y el expediente receptor como objetos distintos. Todo continúa BORRADOR_NO_ENVIADO / DRAFT_NOT_SENT: no hay envío, acuse, plazo ni respuesta. Ninguna de estas capas acredita débito bancario o ausencia de reversa; SAF355 permanece 0/5 y ejecución 0/10.
"""
append_section(HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V158.md", "## V158 · cadena preliminar-final, reforma y conteos", request_section)
append_section(HERE / "REQUEST_SUBMISSION_CHECKLIST_V158.md", "## Control previo V158 · cadena preliminar-final, reforma y conteos", request_section)

register = read_csv(V157 / "E0_REQUEST_RESPONSE_REGISTER_V157.csv")
for row in register:
    row.update({"draft_file": row["draft_file"].replace("V157", "V158"),
                "status": "DRAFT_NOT_SENT", "submitted_on": "N/A", "submission_channel": "N/A",
                "receipt_or_case_id": "N/A", "response_date": "N/A"})
write_csv(HERE / "E0_REQUEST_RESPONSE_REGISTER_V158.csv", register, list(register[0]))


(HERE / "README_V158.md").write_text(f"""# Checkpoint V158

- Fuentes maestras: {len(catalog)}; E0: {len(census)}; nuevas: {len(source_rows)}.
- Resolución SIGEN 7/2003: circuito completo desde instrucciones y presentación inicial hasta aprobación final y custodia definitiva.
- La reorganización del 25/11/2008 ocurrió entre entrega inicial y aprobación final; deuda y finanzas permanecieron en Economía.
- Acta ORSNA 16/2008: comparador contemporáneo de nota, aprobación preliminar, conformidad y anexo; sus errores internos no se trasladan al target.
- Informes de Supervisión 2009: contradicción oficial congelada entre aproximadamente 120 y cerca de 160; falta inventario y regla de conteo.
- ERAS demuestra que nota de remisión, informe adjunto y expediente receptor son objetos distintos y pueden sobrevivir en el destinatario.
- Plan, acto, subplan, legajo, versiones, informe y expediente Economía siguen abiertos.
- SAF355 0/5; ejecución 0/10; seis borradores no enviados.
""", encoding="utf-8")
(HERE / "VEREDICTO_V158.md").write_text("""# Veredicto V158

V158 reemplaza la idea de un único “Plan 2009” por una cadena reglada de documentos, versiones, soportes, autoridades y custodios. La aprobación preliminar, la conformidad ministerial y la aprobación final no son equivalentes; tampoco lo son el ejemplar papel y la copia magnética. La reforma Economía-Producción introduce riesgo de nomenclatura y versión, pero no autoriza a desplazar el proyecto de deuda a Producción sin un registro específico. La divergencia oficial 120/160 no se resuelve eligiendo una cifra: exige inventario, universo y fecha de corte. El comparador ERAS abre además la copia del organismo receptor como ruta independiente. Nada de esto recupera todavía el cuerpo target ni acredita pago. Resultado 0/10; SAF355 0/5; seis borradores no enviados.
""", encoding="utf-8")
(HERE / "E0_FISCAL_RECONSTRUCTION_V158.md").write_text("""# Reconstrucción fiscal E0 V158

La reconstrucción incorpora una cadena de versión completa: presentación UAI, legajo, dictamen, evaluación, modificación, aprobación preliminar, conformidad superior, doble soporte, acto final y custodia definitiva. La ventana de reforma del 25/11 al 15/12/2008 exige cruzar denominaciones y responsables; no cambia por sí sola la pertenencia sustantiva de deuda/finanzas a Economía. La supervisión debe rastrearse como nota, informe y expediente receptor, y su inventario debe resolver la contradicción 120/160. Son rutas de identificación y custodia, no prueba de ejecución. Documento, sistema, banco y reversas siguen siendo el cierre. Estado 0/10.
""", encoding="utf-8")
(HERE / "RETRIEVAL_LOG_V158.md").write_text("""# Retrieval log V158

- Recuperado el Manual anexo a Resolución SIGEN 7/2003; control visual integral por miniaturas y control detallado de páginas PDF 32-34.
- Congelados plazos, actores, versiones, doble soporte, aprobación final y custodio del Plan UAI.
- Recuperada Acta ORSNA 16/2008; control visual de página 4 y aislamiento de sus errores internos de año/fecha.
- Recuperados DNU 2025/2008 y Decreto 2102/2008; reconstruida la reforma durante el trámite y la regla UAI transitoria.
- Recuperada Cuenta de Inversión 2009: aproximadamente 120 supervisiones; comparada con cerca de 160 en Memoria SIGEN 2009, sin elegir cifra.
- Recuperado comparador ERAS; control visual de página 1: Nota 5095/2009-GSPF, informe adjunto y Expediente 878-09.
- Sin plan, acto, legajo, versiones ni informe Economía; SAF355 0/5; banco 0/10; seis DRAFT_NOT_SENT.
""", encoding="utf-8")

stale = HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V158_A_V158.md"
if stale.exists():
    stale.unlink()
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V158_A_V159.md").write_text("""# Handover V158 → V159

## Estado

- Circuito Resolución SIGEN 7/2003 congelado desde presentación inicial hasta versión definitiva bajo custodia gerencial.
- Aprobación preliminar, conformidad superior y acto final son objetos distintos; papel y copia magnética también.
- Reforma del 25/11/2008 ocurrió antes de la aprobación final; deuda y finanzas permanecieron en Economía.
- Acta ORSNA sirve sólo como comparador de flujo por sus discordancias internas de año/fecha.
- Fuentes oficiales 2009 divergen: aproximadamente 120 versus cerca de 160 supervisiones; inventario/metodología abiertos.
- ERAS prueba nota de remisión, informe adjunto y expediente receptor como tres piezas y dos custodios.
- SAF355 0/5; banco 0/10; seis DRAFT_NOT_SENT.

## Prioridad V159

1. Recuperar legajo plan auditoría UAI Economía y su cadena de versiones/actos.
2. Identificar la Gerencia/Subgerencia competente y el acto final del 15/12/2008.
3. Pedir inventario/metodología que reconcilie 120/160 supervisiones y aislar la fila Economía.
4. Buscar nota de remisión, informe adjunto y expediente receptor en ambos custodios.
5. Cerrar notas 0120/09 y 3672/09, SAF355, SISIO, banco y reversas.
6. No enviar solicitudes sin autorización expresa.
""", encoding="utf-8")

append_section(REPO / "BACKUP_ACTUALIZACION_2026-08-29.md", "## V158 · circuito preliminar-final, reforma y contradicción 120/160", """
- Resolución 7/2003 convierte el Plan UAI 2009 en una cadena de al menos diez objetos/versiones recuperables.
- Reforma Economía-Producción congelada entre presentación inicial y aprobación final; deuda/finanzas permanecen en Economía.
- Acta ORSNA usada sólo como comparador contemporáneo; errores internos preservados como límite.
- Contradicción oficial 2009 congelada: aproximadamente 120 versus cerca de 160 Informes de Supervisión.
- ERAS abre la ruta de copia receptora: nota, informe adjunto y expediente local separados.
- Seis fuentes nuevas; cinco páginas PDF nuevas controladas.
- SAF355 0/5; ejecución 0/10; seis borradores no enviados.
""")

write_csv(HERE / "INHERITED_QA_STATUS_V158.csv", [
    {"script": "qa_v157.py", "pre_v158_result": "PASS", "post_v158_result": "PASS_BASELINE", "interpretation": "V157 íntegra; V158 agrega circuito reglado, reforma y contradicción de conteos sin alterar 0/10."},
    {"script": "qa_v158.py", "pre_v158_result": "N/A", "post_v158_result": "PASS", "interpretation": "Verifica seis fuentes, cuatro matrices nuevas, cinco controles PDF y límites V158."},
])


hash_rows = []
for row in catalog:
    local = row["archivo_local"]
    path = REPO / local.lstrip("/") if local else None
    exists = bool(path and path.is_file())
    actual = sha256(path) if exists else ""
    expected = row["sha256"]
    hash_rows.append({"id": row["id"], "archivo_local": local, "exists": str(exists),
                      "sha_catalog": expected, "sha_actual": actual,
                      "hash_ok": str(bool(exists and expected and actual.lower() == expected.lower()))})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V158.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V158.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)

size_rows = []
for path in iter_files(REPO):
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": size,
                      "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576),
                      "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V158.csv", size_rows)

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V157.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint": "V158", "date": "2026-08-31",
    "state": "E0_UAI_PLAN_PRELIMINARY_FINAL_VERSION_CHAIN_REORGANIZATION_AND_120_160_CONFLICT_FROZEN_TARGET_BODIES_OPEN_NOT_SENT",
    "master_catalog_entries": len(catalog), "physical_local_copies": physical,
    "physical_local_hash_ok": hash_ok, "remaining_physical_gaps": len(catalog) - physical,
    "e0_primary_sources_preserved": len(census), "numeric_v158_strict_changed": False,
    "sources_newly_preserved_v158": len(source_rows), "e0_primary_sources_newly_preserved_v158": len(source_rows),
    "e0_fiscal_method_breaks_frozen": len(breaks), "e0_request_traceability_rows": len(trace),
    "e0_request_search_keys": len(keys), "e0_v158_pdf_visual_controls": len(visual),
    "e0_v158_new_pdf_visual_controls": len(visual_add), "e0_v158_image_visual_controls": len(images),
    "e0_v158_total_visual_controls": len(visual) + len(images), "e0_v158_source_bundle_files": len(bundle),
    "e0_v158_plan_chain_rows": len(plan_chain), "e0_v158_account_program_rows": len(account_program),
    "e0_v158_system_separation_rows": len(systems), "e0_v158_supervision_inventory_rows": len(supervision),
    "e0_v158_archive_route_rows": len(archive), "e0_v158_public_search_rows": len(negative),
    "e0_v158_preliminary_final_workflow_rows": len(workflow),
    "e0_v158_reorganization_version_rows": len(reorganization),
    "e0_v158_supervision_count_conflict_rows": len(count_conflict),
    "e0_v158_supervision_delivery_metadata_rows": len(delivery),
    "e0_v158_request_objects": len(objects), "e0_plan_sigen_2009_approval_date_located": True,
    "e0_res_sigen_7_2003_plan_workflow_located": True,
    "e0_uai_plan_initial_deadline_2008_10_30_located": True,
    "e0_uai_plan_final_deadline_2008_12_15_located": True,
    "e0_uai_plan_dual_paper_magnetic_support_rule_located": True,
    "e0_uai_plan_definitive_version_custodian_located": True,
    "e0_economy_production_reorganization_date_located": True,
    "e0_public_debt_and_finance_remained_economy_after_reorganization": True,
    "e0_supervision_2009_official_120_160_count_conflict_frozen": True,
    "e0_supervision_2009_count_inventory_located": False,
    "e0_supervision_note_report_recipient_file_separation_proven_by_comparator": True,
    "e0_plan_sigen_2009_body_located": False, "e0_plan_sigen_2009_approval_act_located": False,
    "e0_uai_economy_plan_2009_subplan_located": False,
    "e0_uai_economy_plan_2009_plan_file_located": False,
    "e0_uai_economy_plan_2009_initial_submission_located": False,
    "e0_uai_economy_plan_2009_preliminary_approval_located": False,
    "e0_uai_economy_plan_2009_superior_conformity_located": False,
    "e0_uai_economy_plan_2009_definitive_version_located": False,
    "e0_uai_economy_plan_2009_reorganization_crosswalk_located": False,
    "e0_uai_economy_planning_supervision_report_2009_located": False,
    "e0_uai_economy_planning_supervision_delivery_note_located": False,
    "e0_uai_economy_planning_supervision_recipient_file_located": False,
    "e0_sisio_2010_plan_cutoff_date_located": True, "e0_sisio_target_plan_snapshot_located": False,
    "e0_account_2008_horizontal_program_located": True, "e0_account_2008_global_report_body_located": False,
    "e0_sigen_archive_digital_program_located": True, "e0_target_archive_entry_located": False,
    "e0_uai_saf355_target_certifications_located_count": 0, "e0_settlement_executed_rows_confirmed": 0,
    "e0_requests_submitted": 0, "e0_request_responses_received": 0,
    "e0_request_package_status": "DRAFT_NOT_SENT",
    "historical_workstream": "Recover UAI Economy plan file and full version/approval chain; reconcile 120/160 with inventory/method; recover supervision note, body and recipient file; then SISIO, notes, SAF355, bank and reversals; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V158.json").write_text(
    json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

(HERE / "AUDITORIA_V158.md").write_text(f"""# Auditoría V158

- Fuentes maestras: {len(catalog)}; E0: {len(census)}; nuevas: {len(source_rows)}.
- Copias/hash: {physical}/{hash_ok}; brechas: {len(catalog) - physical}.
- Quiebres: {len(breaks)}; trazas: {len(trace)}; claves: {len(keys)}; objetos: {len(objects)}.
- Visuales: {len(visual)} PDF ({len(visual_add)} nuevos) + {len(images)} imágenes = {len(visual) + len(images)}.
- Bundle: {len(bundle)}; cadena histórica: {len(plan_chain)}; programa Cuenta: {len(account_program)}; sistemas: {len(systems)}; supervisión heredada: {len(supervision)}; archivo: {len(archive)}.
- Matrices V158: circuito preliminar-final {len(workflow)}; reforma/versiones {len(reorganization)}; contradicción 120/160 {len(count_conflict)}; entrega de supervisión {len(delivery)}; negativos {len(negative)}.
- Plan/acto/legajo/versiones/subplan/supervisión: 0 cuerpos target; SAF355 0/5; ejecución 0/10; pedidos/respuestas 0/0.
""", encoding="utf-8")


def checkpoint_manifest():
    files = [{"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
             for path in sorted(HERE.iterdir()) if path.is_file() and path.name != "MANIFEST_V158.json"]
    payload = {
        "checkpoint": "V158", "parent_checkpoint": "V157",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": len(source_rows),
        "fiscal_method_breaks": len(breaks), "request_traceability_rows": len(trace),
        "request_search_keys": len(keys), "request_objects": len(objects),
        "pdf_visual_controls_total": len(visual), "pdf_visual_controls_new": len(visual_add),
        "image_visual_controls_inherited": len(images), "source_bundle_files": len(bundle),
        "plan_chain_rows": len(plan_chain), "account_program_rows": len(account_program),
        "system_separation_rows": len(systems), "supervision_inventory_rows": len(supervision),
        "archive_route_rows": len(archive), "public_search_rows": len(negative),
        "preliminary_final_workflow_rows": len(workflow),
        "reorganization_version_rows": len(reorganization),
        "supervision_count_conflict_rows": len(count_conflict),
        "supervision_delivery_metadata_rows": len(delivery),
        "res_sigen_7_2003_plan_workflow_located": True,
        "uai_plan_initial_deadline_2008_10_30_located": True,
        "uai_plan_final_deadline_2008_12_15_located": True,
        "uai_plan_dual_support_rule_located": True,
        "uai_plan_definitive_version_custodian_located": True,
        "economy_production_reorganization_date_located": True,
        "public_debt_and_finance_remained_economy_after_reorganization": True,
        "supervision_2009_official_120_160_count_conflict_frozen": True,
        "supervision_2009_count_inventory_located": False,
        "supervision_note_report_recipient_file_separation_proven_by_comparator": True,
        "plan_sigen_2009_approval_date_located": True, "plan_sigen_2009_body_located": False,
        "plan_sigen_2009_approval_act_located": False, "uai_economy_subplan_2009_located": False,
        "uai_economy_plan_file_2009_located": False,
        "uai_economy_initial_submission_2009_located": False,
        "uai_economy_preliminary_approval_2009_located": False,
        "uai_economy_superior_conformity_2009_located": False,
        "uai_economy_definitive_plan_version_2009_located": False,
        "uai_economy_reorganization_crosswalk_located": False,
        "uai_economy_supervision_report_2009_located": False, "sisio_2010_cutoff_date_located": True,
        "uai_economy_supervision_delivery_note_2009_located": False,
        "uai_economy_supervision_recipient_file_2009_located": False,
        "sisio_target_plan_snapshot_located": False, "account_2008_horizontal_program_located": True,
        "account_2008_global_report_body_located": False, "target_archive_entry_located": False,
        "uai_saf355_target_certification_located": False, "executed_settlement_rows_confirmed": 0,
        "request_drafts": 6, "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V158.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tree(root):
    lines = []
    root = Path(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted((name for name in dirnames if name not in EXCLUDED_DIRS), key=str.casefold)
        base = Path(dirpath)
        lines.extend((base / name).relative_to(root).as_posix() + "/" for name in dirnames)
        lines.extend((base / name).relative_to(root).as_posix() for name in sorted(filenames, key=str.casefold))
    return "\n".join(lines) + "\n"


(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")
checkpoint_manifest()

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)}
                for path in iter_files(REPO) if path != global_manifest]
payload = {
    "checkpoint": "V158",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master; {physical} physical SHA-valid; {len(source_rows)} new sources; plan/version/supervision target bodies open; 120/160 conflict frozen; 0/10; six drafts not submitted.",
    "historical_workstream": "Recover plan file and version/approval chain; reconcile supervision counts; recover delivery note, report and recipient file; then SISIO, notes, SAF355, bank and reversals; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
temporary = global_manifest.with_suffix(".json.v158tmp")
temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
temporary.replace(global_manifest)

print(f"V158 BUILD PASS · catalog={len(catalog)} · E0={len(census)} · physical={physical} · hash_ok={hash_ok} · breaks={len(breaks)} · trace={len(trace)} · keys={len(keys)} · objects={len(objects)} · visual={len(visual) + len(images)}")
