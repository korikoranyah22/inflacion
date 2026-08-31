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
BIN = CYCLE / "inputs" / "historical_retrieval" / "v157" / "binaries"
V156 = CYCLE / "checkpoints" / "V156"
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
        "id": "e0_sigen_memory_2008_plan_2009_approval_and_uai_supervision",
        "institution": "Sindicatura General de la Nación",
        "title": "Memoria SIGEN 2008 · Cuenta, SISIO, supervisión UAI y aprobación del Plan SIGEN 2009",
        "url": "https://www.argentina.gob.ar/sites/default/files/memoria_sigen_2008.pdf",
        "filename": "sigen_memoria_2008_plan_2009_approval.pdf",
        "period": "2008; Plan 2009 aprobado 2008-12-15",
        "series": "Memoria SIGEN 2008 · 14 páginas",
        "kind": "PDF oficial preservado y controlado visualmente",
        "variables": "Cuenta2007;UAI;planning_supervision;SISIO;PlanSIGEN2009;SISPE;archive_digital",
        "breaks": "plan agregado/subplan; supervisión/auditoría; SISIO/SISPE; archivo digital/cuerpo target",
        "status": "E0_USABLE_CONTEMPORARY_PLAN_APPROVAL_SUPERVISION_AND_ARCHIVE_CHAIN",
        "note": "Prueba instructivos Cuenta, unos 120 informes de Supervisión del Planeamiento, mejoras SISIO, aprobación del Plan SIGEN 2009 el 15/12/2008 y avances de Archivo Digital. No contiene el subplan UAI Economía ni el cuerpo target.",
    },
    {
        "id": "e0_infoleg_plan_sigen_2008_target_account_horizontal_program",
        "institution": "Sindicatura General de la Nación / InfoLEG",
        "title": "Plan SIGEN 2008 · programa horizontal Cuenta de Inversión y actividades UAI",
        "url": "https://www.infoleg.gob.ar/basehome/actos_gobierno/actosdegobierno15-9-2008-5.htm",
        "filename": "infoleg_plan_sigen_2008_target_control_program.html",
        "period": "Plan 2008; publicación oficial 2008-09-15",
        "series": "Suplemento Actos de Gobierno · Plan 2008",
        "kind": "HTML oficial preservado",
        "variables": "Plan2008;UAI;CuentaInversion;horizontal_audit;7000_products;debt_consolidation;archive_digital",
        "breaks": "plan/ejecución; Cuenta horizontal/certificado SAF355; agregado/producto individual",
        "status": "E0_USABLE_TARGET_PERIOD_CONTROL_PROGRAM_AND_RECORD_CLASS",
        "note": "Prueba que Cuenta de Inversión fue auditoría horizontal planificada en 2008, que los planes UAI reunían más de 7000 productos y que SIGEN proyectó instructivos y Archivo Digital. No prueba emisión individual ni banco.",
    },
    {
        "id": "e0_infoleg_plan_sigen_2010_part1_risk_and_archive_digital",
        "institution": "Sindicatura General de la Nación / InfoLEG",
        "title": "Plan SIGEN 2010 · primera parte, mapa de riesgos 2009 y Archivo Digital",
        "url": "https://www.infoleg.gob.ar/basehome/actos_gobierno/actosdegobierno22-2-2010-1.htm",
        "filename": "infoleg_plan_sigen_2010_part_1.html",
        "period": "2010; usa mapa de riesgos 2009",
        "series": "Suplemento Actos de Gobierno 76 · Plan SIGEN 2010 primera parte",
        "kind": "HTML oficial preservado",
        "variables": "Plan2010;risk_map2009;SIGEN;UAI;digital_archive;planning",
        "breaks": "plan 2010/hecho 2009; archivo institucional/cuerpo target; riesgo/ejecución",
        "status": "E0_USABLE_NEAR_TARGET_PLANNING_AND_ARCHIVE_COMPARATOR",
        "note": "Prueba uso del mapa de riesgos 2009 y continuidad del Archivo Digital iniciado por Resolución 41/2007. No individualiza Economía ni la nota target.",
    },
    {
        "id": "e0_infoleg_plan_sigen_2010_part2_sisio_snapshot_and_account_horizontal",
        "institution": "Sindicatura General de la Nación / InfoLEG",
        "title": "Plan SIGEN 2010 · segunda parte, corte SISIO 16/12/2009 y auditoría horizontal Cuenta 2009",
        "url": "https://www.infoleg.gob.ar/basehome/actos_gobierno/actosdegobierno1-3-2010-1.htm",
        "filename": "infoleg_plan_sigen_2010_part_2_sisio_cutoff.html",
        "period": "corte SISIO 2009-12-16; Plan 2010",
        "series": "Suplemento Actos de Gobierno 77 · Plan SIGEN 2010 segunda parte",
        "kind": "HTML oficial preservado",
        "variables": "SISIO_WEB_II;cutoff;UAI_plans;4550_products;horizontal_audit;Cuenta2009;annex_D",
        "breaks": "corte/plan final; plan/ejecución; Cuenta2009/Cuenta2008; anexo referido/cuerpo recuperado",
        "status": "E0_USABLE_EXACT_SISIO_PLANNING_SNAPSHOT_SCHEMA_AND_DATE",
        "note": "Prueba que la consolidación de planes UAI 2010 salió de SISIO WEB II al 16/12/2009 y qué campos tenían los cuadros de detalle. Los anexos D/E completos siguen ausentes.",
    },
    {
        "id": "e0_cgn_account_2010_sigen_output_and_planning_supervision",
        "institution": "Contaduría General de la Nación / SIGEN",
        "title": "Cuenta de Inversión 2010 · producción SIGEN y 140 informes de Supervisión del Planeamiento",
        "url": "https://www.economia.gob.ar/hacienda/cgn/cuenta/2010/tomoii/05jur20.htm",
        "filename": "cgn_cuenta_2010_sigen_physical_output_and_planning_supervision.html",
        "period": "2010; comparador inmediato posterior",
        "series": "Cuenta de Inversión 2010 · Jurisdicción 20 · SIGEN",
        "kind": "HTML oficial preservado",
        "variables": "planning_supervision;140_reports;424_audits;1690_debt_files;physical_outputs",
        "breaks": "2010/2009; informe de supervisión/informe de auditoría; agregado/cuerpo target",
        "status": "E0_USABLE_PLANNING_SUPERVISION_RECORD_CONTINUITY_COMPARATOR",
        "note": "Confirma continuidad de la clase Informe de Supervisión del Planeamiento: aproximadamente 140 en 2010. Es comparador posterior y no identifica el informe de Economía 2009.",
    },
]


catalog = read_csv(CATALOG)
census = read_csv(V156 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V156.csv")
provenance = read_csv(V156 / "ARCHIVAL_PROVENANCE_V156.csv")
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
    "sha256": source["sha"], "nota": "V157: " + source["note"],
} for source in source_rows], "id")
write_csv(CATALOG, catalog, list(catalog[0]))

census = upsert(census, [{
    "source_id": source["id"], "institution": source["institution"], "artifact": source["title"],
    "url": source["url"], "local_path": source["local"], "sha256": source["sha"], "bytes": source["bytes"],
    "period_coverage": source["period"], "variable_families": source["variables"],
    "primary_source": "YES", "preserved": "YES", "method_breaks": source["breaks"],
    "use_status": source["status"], "caveat": source["note"],
} for source in source_rows], "source_id")
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V157.csv", census, list(census[0]))

provenance = upsert(provenance, [{
    "source_id": source["id"], "original_url": source["url"], "retrieval_url": source["url"],
    "capture_timestamp": "2026-08-31", "cdx_digest": "N/A_OFFICIAL_DIRECT",
    "local_path": source["local"], "sha256": source["sha"], "bytes": source["bytes"],
    "provenance_note": "Captura directa de fuente oficial; alcance y quiebres congelados en V157.",
} for source in source_rows], "source_id")
write_csv(HERE / "ARCHIVAL_PROVENANCE_V157.csv", provenance, list(provenance[0]))


plan_fields = ["row_id", "date_or_period", "source", "documented_event", "expected_record", "target_value", "limit", "status"]
plan_chain = matrix("E0_2008_2009_PLAN_SISIO_APPROVAL_CHAIN_V157.csv", plan_fields, """
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
22|Regla final|Método V157|Plan, aprobación, snapshot y supervisión son piezas separadas|Cuatro cuerpos vinculados por ids y fechas|Evita respuestas genéricas|Ninguna acredita banco|METHOD_LIMIT
""", "PC157_")


account_fields = ["row_id", "year", "program_or_output", "modality", "record_producer", "expected_body", "probative_use", "limit", "status"]
account_program = matrix("E0_ACCOUNT_AUDIT_HORIZONTAL_PROGRAM_2008_2010_V157.csv", account_fields, """
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
systems = matrix("E0_SISIO_SISPE_SYSTEM_SEPARATION_V157.csv", system_fields, """
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
supervision = matrix("E0_PLANNING_SUPERVISION_REPORT_INVENTORY_V157.csv", supervision_fields, """
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
archive = matrix("E0_ARCHIVE_DIGITAL_REORDERING_AND_DISPOSITION_V157.csv", archive_fields, """
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


negative_fields = ["row_id", "query_or_route", "result", "interpretation", "next_step", "status"]
negative = matrix("E0_V157_PUBLIC_SEARCH_NEGATIVE_RESULTS.csv", negative_fields, """
1|Plan SIGEN 2009 cuerpo completo|No localizado públicamente|Aprobación y fecha sí están probadas|Pedir cuerpo y acto|PLAN_BODY_NOT_LOCATED
2|Número del acto aprobatorio 15/12/2008|No localizado|Fecha no sustituye identificador formal|Pedir resolución, disposición o nota|APPROVAL_ACT_NOT_LOCATED
3|Subplan UAI Economía 2009|No localizado|Plan consolidado prueba que debía integrarlo|Pedir plan, versión y aprobación|UAI_SUBPLAN_NOT_LOCATED
4|Informe de Supervisión del Planeamiento UAI Economía 2009|No localizado|La clase y volumen están probados|Pedir inventario y cuerpo|SUPERVISION_REPORT_NOT_LOCATED
5|Snapshot SISIO Plan 2009|No localizado|Uso SISIO probado, salida target no|Pedir exportación y logs|SYSTEM_SNAPSHOT_NOT_LOCATED
6|Anexos D y E Plan SIGEN 2010|No recuperados|La publicación refiere cuadros detallados fuera del suplemento|Buscar archivo y pedir copia|REFERRED_ANNEX_NOT_LOCATED
7|Pautas gerenciales 2009 para Economía|No localizadas|Pueden contener objeto y código|Pedir por gerencia y fecha|PARTICULAR_GUIDANCE_NOT_LOCATED
8|Registro Archivo Digital de notas target|No localizado|Capacidad y programa no prueban ingreso|Pedir índice y metadatos|ARCHIVE_ENTRY_NOT_LOCATED
9|Registro de reordenamiento o depuración target|No localizado|Proceso general no prueba destino|Pedir actas y series|DISPOSITION_RECORD_NOT_LOCATED
10|Certificados SAF355|0 de 5|Plan horizontal e instructivos no sustituyen cuerpos|Pedir por SAF y anexo|TARGET_CERTIFICATES_NOT_LOCATED
11|Filas bancarias target|0 de 10|Plan, SISIO y archivo son capas administrativas|Cerrar con banco y reversas|BANK_EXECUTION_NOT_LOCATED
12|Seis solicitudes|No enviadas|No corre plazo ni existe acuse|Mantener borradores|DRAFT_NOT_SENT
""", "NR157_")
write_csv(HERE / "E0_V157_PUBLIC_SEARCH_NEGATIVE_RESULTS_V157.csv", negative, negative_fields)


breaks = read_csv(V156 / "E0_FISCAL_METHOD_BREAKS_V156.csv")
break_fields = list(breaks[0])
break_add = pipe_rows("""
plan_sigen_2009_approval_not_uai_economy_subplan_body|document|La aprobación del plan consolidado no aporta el subplan UAI Economía.|Pedir consolidado, subplan y comunicación individual.|FROZEN|Memoria SIGEN 2008
umbrella_plan_not_project_execution|phase|Un plan aprobado no prueba ejecución del proyecto.|Exigir registro de ejecución, informe y papeles.|FROZEN|Plan SIGEN 2008 y Memorias
horizontal_account_audit_not_target_saf355_certificate|scope|La auditoría horizontal Cuenta no sustituye certificados SAF355.|Mantener contribuyentes y global separados.|FROZEN|Plan SIGEN 2008
sisio_plan_snapshot_not_observation_entry|system|El snapshot de planes SISIO no equivale a entrada de observaciones.|Pedir módulos y ids por separado.|FROZEN|Plan SIGEN 2010 parte 2
sisio_not_sispe|system|SISIO y SISPE soportan objetos institucionales distintos.|No fundir consultas ni ceros.|FROZEN|Memoria SIGEN 2008
planning_supervision_report_not_audit_report|document|Un Informe de Supervisión del Planeamiento evalúa el plan, no el objeto auditado.|Pedir ambos cuerpos.|FROZEN|Memorias 2008-2009 y Cuenta 2010
aggregate_product_count_not_inventoried_products|aggregation|7000 o 4550 productos agregados no son inventario individual.|Pedir cuadros y filas por UAI.|FROZEN|Planes SIGEN 2008 y 2010
archive_digital_project_not_target_digitization|archive|La existencia de Archivo Digital no prueba digitalización target.|Exigir entrada, imagen, metadatos y logs.|FROZEN|Memoria SIGEN 2008 y Plan 2010
archive_reordering_not_retention|archive|Reordenar y registrar no prueba retención actual.|Pedir transferencia, ubicación o disposición.|FROZEN|Memoria SIGEN 2009
depuration_process_not_proof_of_destruction|archive|Un proceso de depuración proyectado no prueba destrucción de una pieza.|Exigir acto, serie, fecha y destino.|FROZEN|Memoria SIGEN 2009
""", break_fields, "")
breaks = upsert(breaks, break_add, "break_id")
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V157.csv", breaks, break_fields)


trace = read_csv(V156 / "E0_INFORMATION_REQUEST_TRACEABILITY_V156.csv")
trace_fields = list(trace[0])
trace_add = pipe_rows("""
REQ157_SIGEN|SIGEN|CL157_PLAN_2009_BODY|Plan SIGEN 2009 consolidado|2008-2009|aprobado 15/12/2008|acto; versión; UAI; proyectos; anexos|cuerpo testado e índice|DRAFT_NOT_SENT
REQ157_SIGEN|SIGEN|CL157_PLAN_2009_ACT|Acto de aprobación Plan SIGEN 2009|15/12/2008|fecha exacta|tipo; número; firma; anexos; notificación|copia o certificado fundado|DRAFT_NOT_SENT
REQ157_ECON|UAI Economía|CL157_UAI_ECON_PLAN|Subplan UAI Economía 2009|2009|Cuenta 2008; SAF355|proyecto; código; período; horas; producto; versión|plan testado|DRAFT_NOT_SENT
REQ157_SIGEN|SIGEN|CL157_PLANNING_SUPERVISION|Informe Supervisión Planeamiento UAI Economía|2008-2009|120;160 informes agregados|número; fecha; UAI; observaciones; aprobación|cuerpo testado|DRAFT_NOT_SENT
REQ157_SIGEN|SIGEN|CL157_SISIO_PLAN_SNAPSHOT|Snapshot SISIO del plan UAI Economía|2008-2009|SISIO WEB|corte; versión; ids; proyectos; estados; hash|exportación reproducible|DRAFT_NOT_SENT
REQ157_SIGEN|SIGEN|CL157_SISIO_2010_CUTOFF|Exportación SISIO WEB II de planes 2010|16/12/2009|corte exacto|parámetros; UAI; responsable; período; horas; informes|exportación o cuadro|DRAFT_NOT_SENT
REQ157_SIGEN|SIGEN|CL157_LINEAMIENTS_2009|Lineamientos Planeamiento 2009|2008|SIGEN; UAI|fecha; pautas; firma; distribución|cuerpo e índice|DRAFT_NOT_SENT
REQ157_SIGEN|SIGEN|CL157_MANAGER_GUIDANCE|Pautas particulares gerenciales Economía|2008-2009|Cuenta; deuda; GSEyP|gerencia; fecha; objeto; proyectos; destinatarios|cuerpo o cero fundado|DRAFT_NOT_SENT
REQ157_SIGEN|SIGEN/UAI|CL157_HORIZONTAL_PROJECT|Proyecto horizontal Cuenta de Inversión 2008|2008-2009|Cuenta 2008|código; responsables; contribuyentes; horas; informes|ficha y cuerpos|DRAFT_NOT_SENT
REQ157_SIGEN|SIGEN|CL157_GLOBAL_ACCOUNT_BODY|Informe global Cuenta de Inversión 2008|2009|Memoria SIGEN 2009|número; fecha; cuerpo; anexos; referencias|cuerpo testado|DRAFT_NOT_SENT
REQ157_SIGEN|Mesa de Entradas/Archivo|CL157_DIGITAL_ARCHIVE_INDEX|Índice Archivo Digital target|2008-2010|0120/09; 3672/09; Cuenta 2008|id; fecha; imagen; metadatos; serie; logs|índice y consulta certificada|DRAFT_NOT_SENT
REQ157_SIGEN|Archivo general|CL157_REORDERING_REGISTER|Registro de revisión y clasificación 2009|2009-2010|archivo general SIGEN|fondo; serie; caja; fecha; ubicación; responsable|inventario testado|DRAFT_NOT_SENT
REQ157_SIGEN|SIGEN|CL157_DEPURATION_PROCESS|Plan y actas de depuración|2009-2011|archivo general|criterio; serie; acto; fecha; destino|acto o certificado de no aplicación|DRAFT_NOT_SENT
REQ157_SIGEN|SIGEN Sistemas|CL157_SISPE_EXPORT|Consulta SISPE Plan SIGEN 2009|2008-2009|SISPE; Cuenta 2008|actividad; responsable; estado; producto; fecha|exportación reproducible|DRAFT_NOT_SENT
REQ157_SIGEN|SIGEN Sistemas|CL157_SYSTEM_CROSSWALK|Crosswalk SISIO-SISPE-Archivo Digital|2008-2009|plan; proyecto; informe|ids; sistema; vínculo; fecha; documento|diccionario o certificación técnica|DRAFT_NOT_SENT
REQ157_ECON|Tesoro/Finanzas|CL157_FINAL_BANK_GATE|Conciliación final con banco y reversas|2008-2009|71597;152677;2876;C41;C42;C55|id; cuenta; valor; fecha; débito; reversa|fila testada|DRAFT_NOT_SENT
""", trace_fields, "TR157_")
trace = upsert(trace, trace_add, "trace_id")
write_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V157.csv", trace, trace_fields)


keys = read_csv(V156 / "E0_REQUEST_SEARCH_KEY_MATRIX_V156.csv")
key_fields = list(keys[0])
key_add = pipe_rows("""
REQ157_SIGEN|record_type|Plan SIGEN 2009 aprobado 15/12/2008|recuperar consolidado|Memoria SIGEN 2008|Fecha sin acto.
REQ157_SIGEN|record_type|acto aprobación Plan SIGEN 2009|recuperar firma y número|Memoria SIGEN 2008|No localizado.
REQ157_ECON|record_type|Plan UAI Ministerio de Economía 2009|subplan exacto|Plan consolidado|No localizado.
REQ157_SIGEN|record_type|Informe de Supervisión del Planeamiento UAI Economía 2009|evaluación del subplan|Memoria SIGEN 2009|No es auditoría.
REQ157_SIGEN|system|SISIO WEB planeamiento UAI Economía 2009|snapshot plan|Memorias 2008-2009|No entrada observación.
REQ157_SIGEN|system|SISIO WEB II corte 16-12-2009|exportación exacta|Plan SIGEN 2010|Plan 2010.
REQ157_SIGEN|record_type|Lineamientos para el Planeamiento 2009 SIGEN UAI|pautas generales|Memoria SIGEN 2008|No localizados.
REQ157_SIGEN|record_type|pautas particulares gerencia supervisión Economía 2009|pautas gerenciales|Plan SIGEN 2008|GSEyP abierto.
REQ157_SIGEN|record_type|auditoría horizontal Cuenta de Inversión 2008|proyecto target|Plan SIGEN 2008|Plan no ejecución.
REQ157_SIGEN|record_type|informe global Cuenta de Inversión año 2008 SIGEN|cuerpo target|Memoria SIGEN 2009|No localizado.
REQ157_SIGEN|record_type|Cuadro 10 11 12 13 Anexo D Plan SIGEN 2010|detalle planes|Plan SIGEN 2010|Anexo referido.
REQ157_SIGEN|system|SISPE Plan SIGEN 2009 Cuenta de Inversión|plan SIGEN interno|Memoria SIGEN 2008|No SISIO.
REQ157_SIGEN|system|Archivo Digital SIGEN 0120/09 3672/09|imagen y metadatos|Memoria SIGEN 2008|No prueba ingreso.
REQ157_SIGEN|archive|Mesa de Entradas Salidas y Archivo 2009|unidad custodia|Memoria SIGEN 2009|No cuerpo.
REQ157_SIGEN|archive|revisión clasificación registro documentación archivo general 2009|inventario|Memoria SIGEN 2009|No retención.
REQ157_SIGEN|archive|depuración archivo general SIGEN 2010|disposición|Memoria SIGEN 2009|Proyecto no destrucción.
REQ157_SIGEN|crosswalk|SISIO SISPE Archivo Digital plan proyecto informe|vincular sistemas|V157|No asumir mismo id.
REQ157_ECON|record_type|certificaciones Cuenta de Inversión SAF 355 Plan UAI 2009|cerrar 0/5|Memorias y Res 10/2006|No banco.
REQ157_SIGEN|counts|120 160 140 Informes Supervisión Planeamiento|inventario por año|Fuentes 2008-2010|Conteos aproximados.
REQ157_ECON|target_ids|71597 152677 2876 C41 C42 C55 banco reversa|cierre final|Matriz acumulada|0 filas.
""", key_fields, "SK157_")
keys = upsert(keys, key_add, "key_id")
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V157.csv", keys, key_fields)


objects = read_csv(V156 / "E0_V156_REQUEST_OBJECTS.csv")
object_fields = list(objects[0])
object_add = pipe_rows("""
PLAN_SIGEN_2009_BODY|SIGEN|Plan SIGEN 2009 consolidado|2008-2009|acto; versión; UAI; proyectos; anexos|Cuerpo e índice|DRAFT_NOT_SENT
PLAN_SIGEN_2009_APPROVAL_ACT|SIGEN|Acto aprobatorio del 15/12/2008|2008-12-15|tipo; número; firma; anexos; notificación|Copia o búsqueda fundada|DRAFT_NOT_SENT
UAI_ECONOMY_PLAN_2009_SUBPLAN|UAI Economía/SIGEN|Subplan UAI Economía|2009|proyecto; código; horas; producto; versión|Plan y aprobación|DRAFT_NOT_SENT
SISIO_PLAN_2009_SNAPSHOT|SIGEN Sistemas|Snapshot SISIO de UAI Economía|2008-2009|corte; versión; ids; proyectos; estados|Exportación reproducible|DRAFT_NOT_SENT
PLANNING_SUPERVISION_REPORT_ECONOMY_2009|SIGEN|Informe Supervisión del Planeamiento|2009|número; fecha; UAI; observaciones; aprobación|Cuerpo testado|DRAFT_NOT_SENT
LINEAMIENTOS_PLANEAMIENTO_2009|SIGEN|Lineamientos generales y particulares|2008-2009|fecha; emisor; pautas; distribución|Cuerpos e índice|DRAFT_NOT_SENT
ARCHIVE_DIGITAL_INDEX_2008_2009|SIGEN Archivo|Índice Archivo Digital|2008-2009|id; imagen; fecha; metadatos; serie; logs|Entrada o cero certificado|DRAFT_NOT_SENT
ARCHIVE_REORDERING_REGISTER_2009|SIGEN Archivo|Registro de revisión y clasificación|2009-2010|fondo; serie; caja; ubicación; responsable|Inventario testado|DRAFT_NOT_SENT
ARCHIVE_DEPURATION_PROCESS_2010|SIGEN Archivo|Plan, criterios y actas de depuración|2009-2011|serie; acto; fecha; destino; responsable|Disposición formal|DRAFT_NOT_SENT
SISIO_SISPE_ARCHIVE_CROSSWALK|SIGEN Sistemas/Archivo|Vínculo plan-proyecto-informe-documento|2008-2009|ids; sistemas; fechas; vínculos|Diccionario o certificación|DRAFT_NOT_SENT
""", object_fields, "RO157_")
objects = upsert(objects, object_add, "row_id")
write_csv(HERE / "E0_V157_REQUEST_OBJECTS.csv", objects, object_fields)
write_csv(HERE / "E0_V157_REQUEST_OBJECTS_V157.csv", objects, object_fields)


catalog_map = {source["filename"]: source["id"] for source in SOURCES}
roles = {
    "sigen_memoria_2008_plan_2009_approval.pdf": "TARGET_PLAN_APPROVAL_SUPERVISION_AND_ARCHIVE",
    "infoleg_plan_sigen_2008_target_control_program.html": "TARGET_PERIOD_HORIZONTAL_ACCOUNT_PROGRAM",
    "infoleg_plan_sigen_2010_part_1.html": "NEAR_TARGET_RISK_AND_ARCHIVE_COMPARATOR",
    "infoleg_plan_sigen_2010_part_2_sisio_cutoff.html": "EXACT_SISIO_PLANNING_CUTOFF_AND_SCHEMA",
    "cgn_cuenta_2010_sigen_physical_output_and_planning_supervision.html": "PLANNING_SUPERVISION_RECORD_CONTINUITY",
}
bundle_fields = ["row_id", "filename", "role", "catalogued", "catalog_source_id", "bytes", "sha256", "preserved"]
bundle = []
for index, path in enumerate(sorted(BIN.iterdir(), key=lambda value: value.name.casefold()), 1):
    if path.is_file():
        bundle.append(dict(zip(bundle_fields, [f"B157_{index:02d}", path.name, roles[path.name],
                                               "YES", catalog_map[path.name], path.stat().st_size,
                                               sha256(path), "YES"])))
write_csv(HERE / "E0_V157_SOURCE_BUNDLE.csv", bundle, bundle_fields)


visual = read_csv(V156 / "E0_V156_PDF_VISUAL_CONTROL.csv")
visual_fields = list(visual[0])
visual_add = pipe_rows("""
e0_sigen_memory_2008_plan_2009_approval_and_uai_supervision|5|6|Cuenta, instructivos, informe 2007, 120 supervisiones y mejoras SISIO|PASS|Agregado y continuidad; no cuerpo target
e0_sigen_memory_2008_plan_2009_approval_and_uai_supervision|9|10|Lineamientos 2009, aprobación 15/12/2008 y SISPE|PASS|Fecha y sistemas; no subplan Economía
e0_sigen_memory_2008_plan_2009_approval_and_uai_supervision|12|13|Archivo Digital y convocatoria de archivo móvil|PASS|Capacidad general; no entrada target
""", visual_fields, "PV157_")
visual += visual_add
write_csv(HERE / "E0_V157_PDF_VISUAL_CONTROL.csv", visual, visual_fields)
images = read_csv(V156 / "E0_V156_IMAGE_VISUAL_CONTROL.csv")
write_csv(HERE / "E0_V157_IMAGE_VISUAL_CONTROL.csv", images, list(images[0]))


append_section(HERE / "SOURCE_REFERENCES_V157.md", "## V157 · Plan SIGEN 2009, supervisión, SISIO/SISPE y archivo", """
- Memoria SIGEN 2008: https://www.argentina.gob.ar/sites/default/files/memoria_sigen_2008.pdf
- Plan SIGEN 2008: https://www.infoleg.gob.ar/basehome/actos_gobierno/actosdegobierno15-9-2008-5.htm
- Plan SIGEN 2010, primera parte: https://www.infoleg.gob.ar/basehome/actos_gobierno/actosdegobierno22-2-2010-1.htm
- Plan SIGEN 2010, segunda parte: https://www.infoleg.gob.ar/basehome/actos_gobierno/actosdegobierno1-3-2010-1.htm
- Cuenta de Inversión 2010, SIGEN: https://www.economia.gob.ar/hacienda/cgn/cuenta/2010/tomoii/05jur20.htm

Alcance: se prueba la aprobación del Plan SIGEN 2009 el 15/12/2008, la existencia de Informes de Supervisión del Planeamiento, el uso de SISIO para planes UAI, SISPE para actividades SIGEN y programas de Archivo Digital/reordenamiento. No se recuperaron el plan, subplan, informe individual, snapshot o entrada archivística target.
""")

request_section = """
V157 individualiza una cadena adicional: Plan SIGEN 2009 aprobado el 15/12/2008; subplan UAI Economía integrado al consolidado; Informe de Supervisión del Planeamiento; alta y versiones SISIO; y producto de auditoría horizontal Cuenta de Inversión. Se solicitan el acto aprobatorio, plan completo, subplan Economía, lineamientos y pautas gerenciales, informe de supervisión, snapshot SISIO y cruces con SISPE. Como SIGEN mantenía Archivo Digital y en 2009 inició revisión, clasificación y registro del archivo general, también se piden índice digital, libros de Mesa de Entradas, inventario físico y cualquier acto de depuración o transferencia. SISIO, SISPE y Archivo Digital se consultan separadamente. Plan, supervisión y archivo no prueban pago; el cierre sigue exigiendo banco y reversas. Estado BORRADOR_NO_ENVIADO / DRAFT_NOT_SENT.
"""
append_section(HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V157.md", "## V157 · Plan 2009, supervisión y triple sistema", request_section)
append_section(HERE / "REQUEST_SUBMISSION_CHECKLIST_V157.md", "## Control previo V157 · plan, supervisión y archivo", request_section)

register = read_csv(V156 / "E0_REQUEST_RESPONSE_REGISTER_V156.csv")
for row in register:
    row.update({"draft_file": row["draft_file"].replace("V156", "V157"),
                "status": "DRAFT_NOT_SENT", "submitted_on": "N/A", "submission_channel": "N/A",
                "receipt_or_case_id": "N/A", "response_date": "N/A"})
write_csv(HERE / "E0_REQUEST_RESPONSE_REGISTER_V157.csv", register, list(register[0]))


(HERE / "README_V157.md").write_text(f"""# Checkpoint V157

- Fuentes maestras: {len(catalog)}; E0: {len(census)}; nuevas: {len(source_rows)}.
- Plan SIGEN 2009 aprobado el 15/12/2008; cuerpo y acto todavía abiertos.
- Cuenta de Inversión fue programa horizontal en 2008; informe global Cuenta 2008 emitido en 2009.
- Informes de Supervisión del Planeamiento: cerca de 120 en 2008, 160 en 2009 y 140 en 2010.
- SISIO, SISPE y Archivo Digital separados; corte SISIO Plan 2010 probado al 16/12/2009.
- SAF355 0/5; ejecución 0/10; seis borradores no enviados.
""", encoding="utf-8")
(HERE / "VEREDICTO_V157.md").write_text("""# Veredicto V157

V157 transforma el plan anual en una cadena de objetos recuperables: acto de aprobación, plan consolidado, subplan UAI Economía, Informe de Supervisión, snapshot SISIO, actividad SISPE y registro de Archivo Digital. La aprobación del Plan SIGEN 2009 el 15/12/2008 y la condición horizontal de Cuenta de Inversión quedan probadas. También queda una ruta de disposición: SIGEN revisó, clasificó y registró su archivo general en 2009 y proyectó depuración. Aun así, no apareció ningún cuerpo target ni banco. Resultado 0/10; SAF355 0/5; seis borradores no enviados.
""", encoding="utf-8")
(HERE / "E0_FISCAL_RECONSTRUCTION_V157.md").write_text("""# Reconstrucción fiscal E0 V157

La reconstrucción incorpora planeamiento y custodia: programa horizontal Cuenta, aprobación, supervisión, SISIO, SISPE y Archivo Digital. Estas piezas pueden identificar códigos y contenedores del informe Cuenta 2008 y sus contribuyentes, pero siguen siendo capas administrativas. Documento, sistema, banco y reversas permanecen como cierre. Estado 0/10.
""", encoding="utf-8")
(HERE / "RETRIEVAL_LOG_V157.md").write_text("""# Retrieval log V157

- Recuperada y controlada visualmente Memoria SIGEN 2008, páginas PDF 6, 10 y 13.
- Confirmada aprobación Plan SIGEN 2009 el 15/12/2008.
- Confirmados 120/160/140 informes aproximados de Supervisión del Planeamiento en 2008/2009/2010.
- Confirmada Cuenta de Inversión como auditoría horizontal planificada en 2008.
- Confirmado corte SISIO WEB II de planes UAI al 16/12/2009 y aprobación Plan 2010 al 22/12/2009.
- Separados SISIO, SISPE y Archivo Digital; congelada ruta de reordenamiento/depuración.
- Sin cuerpos, SAF355 ni banco; seis DRAFT_NOT_SENT; 0/10.
""", encoding="utf-8")

stale = HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V157_A_V157.md"
if stale.exists():
    stale.unlink()
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V157_A_V158.md").write_text("""# Handover V157 → V158

## Estado

- Plan SIGEN 2009 aprobado 15/12/2008; cuerpo, acto y subplan Economía abiertos.
- Cuenta de Inversión era auditoría horizontal 2008; informe global Cuenta 2008 emitido 2009.
- Informes de Supervisión del Planeamiento probados como clase estable 2008-2010.
- SISIO para planes UAI, SISPE para plan SIGEN y Archivo Digital permanecen separados.
- Corte SISIO WEB II al 16/12/2009; Plan 2010 aprobado 22/12/2009.
- Reordenamiento, clasificación, registro y depuración de archivo crean una ruta documental adicional.
- SAF355 0/5; banco 0/10; seis DRAFT_NOT_SENT.

## Prioridad V158

1. Recuperar Plan SIGEN 2009 y acto aprobatorio.
2. Recuperar subplan UAI Economía e Informe de Supervisión 2009.
3. Recuperar snapshot SISIO y código del proyecto horizontal Cuenta 2008.
4. Buscar índice Archivo Digital, registro físico y disposición.
5. Cerrar notas 0120/09 y 3672/09, SAF355, banco y reversas.
6. No enviar solicitudes sin autorización expresa.
""", encoding="utf-8")

append_section(REPO / "BACKUP_ACTUALIZACION_2026-08-29.md", "## V157 · Plan SIGEN 2009, supervisión y archivo", """
- Plan SIGEN 2009 aprobado el 15/12/2008; plan y acto todavía no recuperados.
- Cuenta de Inversión congelada como auditoría horizontal 2008.
- Confirmados Informes de Supervisión del Planeamiento y corte SISIO 16/12/2009.
- Separados SISIO, SISPE y Archivo Digital; agregada ruta de reordenamiento/depuración.
- Cinco fuentes nuevas; tres páginas PDF nuevas controladas.
- SAF355 0/5; ejecución 0/10; seis borradores no enviados.
""")

write_csv(HERE / "INHERITED_QA_STATUS_V157.csv", [
    {"script": "qa_v156.py", "pre_v157_result": "PASS", "post_v157_result": "PASS_BASELINE", "interpretation": "V156 íntegra; V157 agrega cadena de planeamiento sin alterar 0/10."},
    {"script": "qa_v157.py", "pre_v157_result": "N/A", "post_v157_result": "PASS", "interpretation": "Verifica cinco fuentes, matrices, controles y límites V157."},
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
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V157.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V157.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)

size_rows = []
for path in iter_files(REPO):
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": size,
                      "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576),
                      "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V157.csv", size_rows)

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V156.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint": "V157", "date": "2026-08-31",
    "state": "E0_PLAN_2009_APPROVAL_SUPERVISION_AND_ARCHIVE_CHAIN_LOCATED_TARGET_BODIES_OPEN_NOT_SENT",
    "master_catalog_entries": len(catalog), "physical_local_copies": physical,
    "physical_local_hash_ok": hash_ok, "remaining_physical_gaps": len(catalog) - physical,
    "e0_primary_sources_preserved": len(census), "numeric_v157_strict_changed": False,
    "sources_newly_preserved_v157": len(source_rows), "e0_primary_sources_newly_preserved_v157": len(source_rows),
    "e0_fiscal_method_breaks_frozen": len(breaks), "e0_request_traceability_rows": len(trace),
    "e0_request_search_keys": len(keys), "e0_v157_pdf_visual_controls": len(visual),
    "e0_v157_new_pdf_visual_controls": len(visual_add), "e0_v157_image_visual_controls": len(images),
    "e0_v157_total_visual_controls": len(visual) + len(images), "e0_v157_source_bundle_files": len(bundle),
    "e0_v157_plan_chain_rows": len(plan_chain), "e0_v157_account_program_rows": len(account_program),
    "e0_v157_system_separation_rows": len(systems), "e0_v157_supervision_inventory_rows": len(supervision),
    "e0_v157_archive_route_rows": len(archive), "e0_v157_public_search_rows": len(negative),
    "e0_v157_request_objects": len(objects), "e0_plan_sigen_2009_approval_date_located": True,
    "e0_plan_sigen_2009_body_located": False, "e0_plan_sigen_2009_approval_act_located": False,
    "e0_uai_economy_plan_2009_subplan_located": False,
    "e0_uai_economy_planning_supervision_report_2009_located": False,
    "e0_sisio_2010_plan_cutoff_date_located": True, "e0_sisio_target_plan_snapshot_located": False,
    "e0_account_2008_horizontal_program_located": True, "e0_account_2008_global_report_body_located": False,
    "e0_sigen_archive_digital_program_located": True, "e0_target_archive_entry_located": False,
    "e0_uai_saf355_target_certifications_located_count": 0, "e0_settlement_executed_rows_confirmed": 0,
    "e0_requests_submitted": 0, "e0_request_responses_received": 0,
    "e0_request_package_status": "DRAFT_NOT_SENT",
    "historical_workstream": "Recover Plan SIGEN 2009, Economy subplan, supervision report, SISIO/SISPE/archive ids, notes, SAF355, bank and reversals; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V157.json").write_text(
    json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

(HERE / "AUDITORIA_V157.md").write_text(f"""# Auditoría V157

- Fuentes maestras: {len(catalog)}; E0: {len(census)}; nuevas: {len(source_rows)}.
- Copias/hash: {physical}/{hash_ok}; brechas: {len(catalog) - physical}.
- Quiebres: {len(breaks)}; trazas: {len(trace)}; claves: {len(keys)}; objetos: {len(objects)}.
- Visuales: {len(visual)} PDF ({len(visual_add)} nuevos) + {len(images)} imágenes = {len(visual) + len(images)}.
- Bundle: {len(bundle)}; cadena plan: {len(plan_chain)}; programa Cuenta: {len(account_program)}; sistemas: {len(systems)}; supervisión: {len(supervision)}; archivo: {len(archive)}.
- Plan/acto/subplan/supervisión: 0/4 cuerpos; SAF355 0/5; ejecución 0/10; pedidos/respuestas 0/0.
""", encoding="utf-8")


def checkpoint_manifest():
    files = [{"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
             for path in sorted(HERE.iterdir()) if path.is_file() and path.name != "MANIFEST_V157.json"]
    payload = {
        "checkpoint": "V157", "parent_checkpoint": "V156",
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
        "plan_sigen_2009_approval_date_located": True, "plan_sigen_2009_body_located": False,
        "plan_sigen_2009_approval_act_located": False, "uai_economy_subplan_2009_located": False,
        "uai_economy_supervision_report_2009_located": False, "sisio_2010_cutoff_date_located": True,
        "sisio_target_plan_snapshot_located": False, "account_2008_horizontal_program_located": True,
        "account_2008_global_report_body_located": False, "target_archive_entry_located": False,
        "uai_saf355_target_certification_located": False, "executed_settlement_rows_confirmed": 0,
        "request_drafts": 6, "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V157.json").write_text(
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
    "checkpoint": "V157",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master; {physical} physical SHA-valid; {len(source_rows)} new sources; plan and target bodies open; 0/10; six drafts not submitted.",
    "historical_workstream": "Recover plan/subplan/supervision/SISIO/archive records, notes, SAF355, bank and reversals; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
temporary = global_manifest.with_suffix(".json.v157tmp")
temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
temporary.replace(global_manifest)

print(f"V157 BUILD PASS · catalog={len(catalog)} · E0={len(census)} · physical={physical} · hash_ok={hash_ok} · breaks={len(breaks)} · trace={len(trace)} · keys={len(keys)} · objects={len(objects)} · visual={len(visual) + len(images)}")
