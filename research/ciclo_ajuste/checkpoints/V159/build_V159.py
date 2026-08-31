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
BIN = CYCLE / "inputs" / "historical_retrieval" / "v159" / "binaries"
V158 = CYCLE / "checkpoints" / "V158"
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
        "id": "e0_sigen_memoria_2003_gsepfye_area_and_note_suffix",
        "institution": "Sindicatura General de la Nación",
        "title": "Memoria SIGEN 2003 · nombre largo del área y sufijo de nota GSEPFyE",
        "url": "https://www.argentina.gob.ar/sites/default/files/memoria_sigen_2003.pdf",
        "filename": "sigen_memoria_2003_gsepfye_note_suffix_and_area.pdf",
        "period": "2003",
        "series": "Memoria SIGEN 2003 · páginas PDF 3 y 7",
        "kind": "PDF oficial preservado y controlado visualmente",
        "variables": "SIGEN;supervision_area;Economy;Federal_Planning;Entities;GSEPFyE;note_suffix;organizational_structure",
        "breaks": "nombre largo/sigla; 2003/2009; GSEPFyE/GSEyP/GSEPyPF/GSEPYPF; área/unidad productora",
        "status": "E0_USABLE_CONTEMPORARY_LONG_NAME_AND_GSEPFYE_NOTE_SUFFIX",
        "note": "En la misma página oficial identifica a la Gerencia de Supervisión de Economía, Planificación Federal y Entidades y usa GSEPFyE en las Notas 4997/03 y 5152/03-5154/03. La asociación es válida para 2003; no prueba que GSEyP de 2009 sea la misma unidad.",
    },
    {
        "id": "e0_sigen_memoria_2004_supervision_structure_and_record_systems",
        "institution": "Sindicatura General de la Nación",
        "title": "Memoria SIGEN 2004 · estructura de supervisión y sistemas documentales",
        "url": "https://www.argentina.gob.ar/sites/default/files/memoria_sigen_2004.pdf",
        "filename": "sigen_memoria_2004_supervision_structure_and_record_systems.pdf",
        "period": "2004",
        "series": "Memoria SIGEN 2004 · páginas PDF 8 y 9",
        "kind": "PDF oficial preservado y controlado visualmente",
        "variables": "Resolution_58_2004;Resolution_91_2004;subgerencias;GSEPFyE;fiduciary_funds;entry_desk;consolidation_bonds;electronic_file",
        "breaks": "estructura/custodia target; sistema disponible/asiento existente; Fondo Fiduciario/deuda; variantes del nombre del área",
        "status": "E0_USABLE_EXACT_2004_STRUCTURE_AND_RECORD_SYSTEM_CAPABILITY",
        "note": "Documenta dos Subgerencias, asignación del control directo de Fondos Fiduciarios a la Gerencia de Supervisión y sistemas para Mesa de Entradas y Bonos de Consolidación, con avance hacia legajo electrónico. No prueba que el cuerpo target haya sido digitalizado o conservado.",
    },
    {
        "id": "e0_sigen_memoria_2006_uai_and_output_measure_denominators",
        "institution": "Sindicatura General de la Nación",
        "title": "Memoria SIGEN 2006 · 145 UAI y separación entre unidades, proyectos e informes",
        "url": "https://www.argentina.gob.ar/sites/default/files/memoria_sigen_2006.pdf",
        "filename": "sigen_memoria_2006_uai_universe_145.pdf",
        "period": "2006; planeamiento 2007",
        "series": "Memoria SIGEN 2006 · página PDF 3",
        "kind": "PDF oficial preservado y controlado visualmente",
        "variables": "145_UAI;143_Red_Federal_projects;318_completed_projects;119_internal_control_reports;planning_2007;count_denominator",
        "breaks": "UAI/proyecto/informe; 2006/2009; planeamiento/supervisión/evaluación; stock/flujo",
        "status": "E0_USABLE_DENOMINATOR_TYPE_COMPARATOR_NOT_2009_CENSUS",
        "note": "Distingue en una misma memoria 145 UAI supervisadas, 143 proyectos previstos de la Red Federal, 318 proyectos concluidos y 119 informes de evaluación. Prueba que las unidades de conteo no son intercambiables; no aporta el universo ni la regla de 2009.",
    },
    {
        "id": "e0_eras_act_09_2010_gsepypf_note_report_and_recipient_file",
        "institution": "Ente Regulador de Agua y Saneamiento / SIGEN",
        "title": "Acta ERAS 09/2010 · Nota 4712/2010-GSEPYPF, informe 2009 y expediente receptor",
        "url": "https://www.argentina.gob.ar/sites/default/files/contrataciones/2010/acta%200910.pdf",
        "filename": "eras_act_09_2010_gsepypf_note_recipient_file.pdf",
        "period": "2010; informe sobre 2009",
        "series": "Acta ERAS 09/2010 · punto 19 · Expediente 1085-10",
        "kind": "PDF oficial preservado y controlado visualmente",
        "variables": "GSEPYPF;SIGEN_note;internal_control_report_2009;recipient_file;board;internal_routing;response_cycle",
        "breaks": "nota/informe/expediente; emisor/receptor; GSEPYPF/GSEyP; comparador/target; conocimiento/tratamiento",
        "status": "E0_USABLE_EXACT_NOTE_REPORT_RECIPIENT_FILE_LIFECYCLE_COMPARATOR",
        "note": "Prueba que la Nota 4712/2010-GSEPYPF remitió un informe 2009, que el receptor abrió el Expediente 1085-10 y giró las actuaciones a áreas competentes para expedirse y volver al Directorio. Es comparador, no el informe de Economía ni equivalencia con GSEyP.",
    },
]


catalog = read_csv(CATALOG)
census = read_csv(V158 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V158.csv")
provenance = read_csv(V158 / "ARCHIVAL_PROVENANCE_V158.csv")
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
    "sha256": source["sha"], "nota": "V159: " + source["note"],
} for source in source_rows], "id")
write_csv(CATALOG, catalog, list(catalog[0]))

census = upsert(census, [{
    "source_id": source["id"], "institution": source["institution"], "artifact": source["title"],
    "url": source["url"], "local_path": source["local"], "sha256": source["sha"], "bytes": source["bytes"],
    "period_coverage": source["period"], "variable_families": source["variables"],
    "primary_source": "YES", "preserved": "YES", "method_breaks": source["breaks"],
    "use_status": source["status"], "caveat": source["note"],
} for source in source_rows], "source_id")
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V159.csv", census, list(census[0]))

provenance = upsert(provenance, [{
    "source_id": source["id"], "original_url": source["url"], "retrieval_url": source["url"],
    "capture_timestamp": "2026-08-31", "cdx_digest": "N/A_OFFICIAL_DIRECT",
    "local_path": source["local"], "sha256": source["sha"], "bytes": source["bytes"],
    "provenance_note": "Captura directa de fuente oficial; alcance y quiebres congelados en V159.",
} for source in source_rows], "source_id")
write_csv(HERE / "ARCHIVAL_PROVENANCE_V159.csv", provenance, list(provenance[0]))


plan_fields = ["row_id", "date_or_period", "source", "documented_event", "expected_record", "target_value", "limit", "status"]
plan_chain = matrix("E0_2008_2009_PLAN_SISIO_APPROVAL_CHAIN_V159.csv", plan_fields, """
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
22|Regla final|Método V159|Plan, aprobación, snapshot y supervisión son piezas separadas|Cuatro cuerpos vinculados por ids y fechas|Evita respuestas genéricas|Ninguna acredita banco|METHOD_LIMIT
""", "PC157_")


account_fields = ["row_id", "year", "program_or_output", "modality", "record_producer", "expected_body", "probative_use", "limit", "status"]
account_program = matrix("E0_ACCOUNT_AUDIT_HORIZONTAL_PROGRAM_2008_2010_V159.csv", account_fields, """
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
systems = matrix("E0_SISIO_SISPE_SYSTEM_SEPARATION_V159.csv", system_fields, """
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
supervision = matrix("E0_PLANNING_SUPERVISION_REPORT_INVENTORY_V159.csv", supervision_fields, """
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
archive = matrix("E0_ARCHIVE_DIGITAL_REORDERING_AND_DISPOSITION_V159.csv", archive_fields, """
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
workflow = matrix("E0_PLAN_2009_PRELIMINARY_FINAL_APPROVAL_WORKFLOW_V159.csv", workflow_fields, """
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
20|Regla V159|Control de versiones|Todas las unidades|Cada etapa debe vincular versión, fecha, actor y soporte|Cadena probatoria completa|Solicitar índice y relación entre todas las piezas|Ninguna etapa prueba ejecución bancaria|METHOD_LIMIT
""", "WF158_")


reorg_fields = ["row_id", "date_or_period", "event", "legal_source", "effect_on_target", "record_to_recover", "allowed_inference", "forbidden_inference", "status"]
reorganization = matrix("E0_UAI_ECONOMY_2009_REORGANIZATION_VERSION_CHAIN_V159.csv", reorg_fields, """
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
15|2008-2009|Crosswalk organizacional|Método V159|Relacionar denominación pre-reforma, post-reforma, función y sistema|Tabla unidad-fecha-proyecto-id|Evita falsos negativos por nombre|No reemplaza cuerpo documental|REQUEST_TARGET
16|Regla final|No traslado automático|Método V159|La reforma explica riesgo de versión, no prueba desplazamiento del target|Exigir acto, registro o metadatos|Mantiene deuda/finanzas en Economía|No atribuir a Producción sin evidencia|METHOD_LIMIT
""", "RG158_")


count_fields = ["row_id", "source", "period", "published_expression", "normalized_reading", "comparison", "required_resolution", "limit", "status"]
count_conflict = matrix("E0_PLANNING_SUPERVISION_COUNT_CONFLICT_V159.csv", count_fields, """
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
12|Regla V159|No seleccionar cifra|Método de contradicción congelada|Conservar 120 y 160 con sus fuentes|Resolver sólo con inventario/metodología|Evita falsa precisión|No altera 0/10|CONFLICT_FROZEN
""", "CF158_")


delivery_fields = ["row_id", "date_or_period", "source_or_actor", "record", "identifier", "relationship", "target_analogue", "limit", "status"]
delivery = matrix("E0_SUPERVISION_REPORT_DELIVERY_METADATA_V159.csv", delivery_fields, """
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
12|Regla final|Método V159|Separación de objetos|N/A|No colapsar nota, informe y expediente|Certificar búsqueda en ambos custodios|Ninguno prueba banco|METHOD_LIMIT
""", "DL158_")


acronym_fields = ["row_id", "date_or_period", "official_source", "observed_name_or_record", "observed_token", "proved_relationship", "allowed_use", "forbidden_use", "status"]
acronym_timeline = matrix("E0_SIGEN_SUPERVISION_AREA_ACRONYM_TIMELINE_V159.csv", acronym_fields, """
1|2003|Memoria SIGEN 2003 p.3|Gerencia de Supervisión de Economía, Planificación Federal y Entidades|GSEPFyE|El mismo documento vincula área y sufijo de notas|Buscar GSEPFyE y nombre largo en series 2003|Trasladar identidad a 2009|CONTEMPORARY_ASSOCIATION
2|2003|Memoria SIGEN 2003 p.7|Subgerencia de Economía y Planificación Federal|N/A|La Resolución 87/03 organizó seis Sindicaturas bajo esa Subgerencia|Reconstruir nivel Gerencia-Subgerencia-Sindicatura|Convertir Subgerencia en sufijo de nota|STRUCTURE_ONLY
3|2004|Memoria SIGEN 2004 p.8|Subgerencia de Economía y Planificación Federal; Subgerencia de Entidades y Sociedades|N/A|La Resolución 58/04 redujo la estructura a dos Subgerencias|Delimitar estructura 2004|Presumir estructura idéntica en 2009|STRUCTURE_ONLY
4|2004|Memoria SIGEN 2004 p.9|Gerencia de Supervisión Económica, Planificación Federal y Entidades|GSEPFyE|Expansión entre paréntesis en fuente oficial|Equivalencia exacta para el acto 2004|Corregir variantes editoriales sin conservar literal|EXPLICIT_EXPANSION
5|2008|Plan SIGEN 2008|Gerencia de Supervisión Economía, Planificación Federal y Entes Reguladores|N/A|Nombre largo contemporáneo del plan|Agregar nombre largo a la búsqueda 2008|Inferir sigla o sucesión sin acto|LONG_NAME_ONLY
6|2009|Cuenta de Inversión 2009 UEPEX|Nota SIGEN 3672/09|GSEyP|Sufijo exacto del documento target referido|Buscar literal GSEyP y número de nota|Expandirlo por similitud|TARGET_TOKEN_ONLY
7|2009 referido después|Libro Blanco SIGEN 2012|Informe global Cuenta 2008 del Ministerio de Economía|GSEPyPF|Área consignada en inventario posterior|Buscar ese token como ruta separada|Equipararlo a GSEyP|DISTINCT_INVENTORY_TOKEN
8|2010|Acta ERAS 09/2010 p.5|Nota SIGEN 4712/2010|GSEPYPF|Sufijo exacto unido a nota e informe 2009|Buscar literal mayúsculo en 2010|Convertirlo en expansión contemporánea|DISTINCT_NOTE_TOKEN
9|2013|Resolución SIGEN 93/2013|Gerencia de Supervisión de Economía, Producción y Planificación Federal|GSEPyPF|Expansión oficial posterior|Desambiguar el token largo de 2013|Retrotraer identidad a Nota 3672/09|POSTERIOR_EXPANSION_ONLY
10|2003-2013|Cruce controlado|Cuatro formas documentadas|GSEPFyE; GSEyP; GSEPyPF; GSEPYPF|Serie de variantes y cambios institucionales|Consulta por tokens separados y fechas|Normalizar a una sigla canónica|TOKEN_SEPARATION_RULE
11|2008-2010|Target de archivo|Gerencia/Subgerencia/Sindicatura competente|N/A|Falta acto contemporáneo que encadene unidades|Pedir organigrama, responsabilidades, firmas y sucesión|Designar productor final por inferencia|REQUEST_TARGET
12|Regla final|Método V159|Similitud ortográfica no es identidad administrativa|N/A|Sólo una fuente coetánea explícita puede unir token y unidad|Mantener rutas paralelas|Cerrar el gap nominativo|METHOD_LIMIT
""", "AT159_")


denominator_fields = ["row_id", "year_or_period", "official_source", "published_value", "unit_of_count", "controlled_interpretation", "comparison_limit", "required_record", "status"]
denominator_control = matrix("E0_UAI_COUNT_REPORT_DENOMINATOR_CONTROL_V159.csv", denominator_fields, """
1|2006; plan 2007|Memoria SIGEN 2006 p.3|145|Unidades de Auditoría Interna supervisadas|Censo operativo de UAI en esa memoria|No es universo 2009|Inventario anual de UAI 2009|UNIT_COUNT_COMPARATOR
2|plan 2007|Memoria SIGEN 2006 p.3|143|Proyectos de auditoría de la Red Federal previstos|Proyectos no equivalen a UAI ni informes|Subuniverso Red Federal|Inventario de proyectos y programa|PROJECT_COUNT_COMPARATOR
3|2006|Memoria SIGEN 2006 p.3|318|Proyectos de auditoría concluidos|Flujo de proyectos anual|Puede haber varios por UAI|Registro de proyectos|PROJECT_COUNT_COMPARATOR
4|2006|Memoria SIGEN 2006 p.3|119|Informes de Evaluación del Sistema de Control Interno|Clase específica de informe|No son Informes de Supervisión del Planeamiento|Inventario por clase|REPORT_CLASS_COMPARATOR
5|2008|Memoria SIGEN 2008|cerca de 120|Informes de Supervisión del Planeamiento|Flujo aproximado de una clase documental|No dividir por UAI sin inventario|Inventario 2008|PLANNING_REPORT_COUNT
6|2009|Cuenta de Inversión 2009|aproximadamente 120|Informes de Supervisión del Planeamiento|Primer agregado oficial del año target|Redondeado y sin universo|Inventario y ficha del indicador|OFFICIAL_COUNT_A
7|2009|Memoria SIGEN 2009|cerca de 160|Informes de Supervisión del Planeamiento|Segundo agregado oficial del año target|Redondeado y discordante|Inventario y metodología|OFFICIAL_COUNT_B
8|2010|Cuenta de Inversión 2010|aproximadamente 140|Informes de Supervisión del Planeamiento|Continuidad posterior de la clase|No resuelve 2009|Inventario 2010 sólo comparador|PLANNING_REPORT_COUNT
9|Cruce 2006|Una fuente, misma página|145; 143; 318; 119|Cuatro denominadores distintos|Prueba que SIGEN publicaba unidades, proyectos e informes por separado|No define la metodología 2009|Diccionario de indicadores|DENOMINATOR_SEPARATION
10|Cruce 2009|Dos fuentes oficiales|120; 160|Informes aproximados|La brecha nominal es 40 y no una diferencia de UAI|Extremos no exactos|Cifras sin redondeo|CONFLICT_FROZEN
11|Hipótesis abierta|Método V159|N/A|Fecha de corte o estado del informe|Emitido, aprobado, remitido o cerrado podrían contar distinto|No elegir hipótesis|Regla de estado y corte|HYPOTHESIS_ONLY
12|Hipótesis abierta|Método V159|N/A|Cobertura institucional|Una serie podría cubrir subconjunto o revisión|No elegir hipótesis|Lista de organismos y exclusiones|HYPOTHESIS_ONLY
13|Target Economía|2009|1 fila esperada, no localizada|Informe de Supervisión UAI Economía|Debe identificarse por metadatos, no por prorrateo|Ningún agregado prueba inclusión|Fila del inventario y cuerpo|TARGET_OPEN
14|Regla final|Método V159|N/A|Unidad de observación|No comparar UAI, proyecto e informe como magnitudes homogéneas|No altera 0/10|Inventario, diccionario y corte|METHOD_LIMIT
""", "DC159_")


lifecycle_fields = ["row_id", "stage", "documented_comparator", "record_producer", "recipient_or_custodian", "identifier_or_link", "target_request", "limit", "status"]
recipient_lifecycle = matrix("E0_SUPERVISION_NOTE_RECIPIENT_LIFECYCLE_V159.csv", lifecycle_fields, """
1|Producción|Informe de Supervisión UAI ERAS enero-junio 2009|SIGEN|SIGEN|Título y período|Informe de Supervisión UAI Economía 2009|Comparador ERAS|COMPARATOR_STAGE
2|Remisión|Nota SIGEN 5095/2009-GSPF|SIGEN|ERAS|Nota más ejemplar adjunto|Nota equivalente y acuse Economía|No es target|COMPARATOR_STAGE
3|Apertura receptora|Expediente ERAS 878-09|ERAS|ERAS|Número local|Expediente receptor Economía|No es legajo SIGEN|COMPARATOR_STAGE
4|Producción|Informe de Evaluación del Sistema de Control Interno - Año 2009 ERAS|SIGEN|SIGEN|Título completo|Cuerpo, anexos y papeles|Otra clase documental|COMPARATOR_STAGE
5|Remisión|Nota SIGEN 4712/2010-GSEPYPF|SIGEN|ERAS|Número, año y área|Buscar número/área/fecha/destino target|No equipara GSEyP|COMPARATOR_STAGE
6|Apertura receptora|Expediente ERAS 1085-10|ERAS|ERAS|Acta vincula nota, informe y expediente|Número local target, índice y copia|No es número SIGEN|COMPARATOR_STAGE
7|Circulación interna|Giro a Gerencias y Departamentos involucrados|Directorio ERAS|Áreas competentes|Pases internos|Pases y responsables en Economía|No prueba respuesta|COMPARATOR_STAGE
8|Respuesta esperada|Áreas deben expedirse|Áreas ERAS|Directorio ERAS|Tratamiento en próxima reunión|Informes internos y nueva elevación|Acta no contiene desenlace|FOLLOWUP_STAGE
9|Custodia doble|Nota/cuerpo en SIGEN y expediente/copia en receptor|SIGEN y ERAS|Dos custodios|Acuse y fojas|Certificar búsquedas en ambos fondos|Una negativa no cierra la otra|CUSTODY_RULE
10|Target 2009|Nota 3672/09 GSEyP y cuerpo referido|SIGEN|Áreas pertinentes|Cuenta dice envío y carga SISIO|Nota, cuerpo, anexos, distribución, acuses y SISIO|No banco|TARGET_OPEN
11|Target Economía|Informe global Cuenta 2008 e informe UAI|SIGEN/UAI|Economía/CGN/SIGEN|Inventario posterior|Cruzar nota, informe, expediente y seguimiento|No asumir un único expediente|TARGET_OPEN
12|Regla final|Cada transición exige identificador|Todos|Todos|número, fecha, fojas, pase, acuse y resultado|Solicitar cadena completa y testada|Comparador no acredita existencia target|METHOD_LIMIT
""", "LC159_")


saf_nontrans_fields = ["row_id", "layer", "official_rule_or_record", "scope", "allowed_inference", "forbidden_inference", "target_action", "status"]
saf_nontransposition = matrix("E0_SAF355_EXCEPTION_CERTIFICATION_NONTRANSPOSITION_V159.csv", saf_nontrans_fields, """
1|Cierre general|Disposición CGN 49/02 art.1|SAF 355 y 356 exceptuados de cuadros estándar|Existe excepción de ruta y producto|No registración de operaciones|Conservar ruta especial|SCOPE_EXCEPTION
2|Aplicación 2008|Cuenta de Inversión 2008 UEPEX|CGN aplica excepción a 355/356|Es contemporánea al target|No cierre de todos los objetos UAI|Citar alcance exacto|TARGET_PERIOD_EXCEPTION
3|Cuadro general|Caja y Bancos del cierre estándar|Producto exceptuado para SAF355|Su ausencia es esperable en esa vía|No inexistencia de cuenta o movimiento|No usar cero general como cierre|NEGATIVE_LIMIT
4|Consulta especial|Listados parametrizados SIDIF|CGN suministró salidas para conciliación|Ruta alternativa verificable|No cuerpo de pago por sí solo|Pedir salida, parámetros, fecha y hash|SPECIAL_ROUTE
5|Consulta especial|Consultas específicas de movimientos|Movimientos individualizables|Posible reconstrucción|No identidad target sin filtros|Pedir consulta reproducible|SPECIAL_ROUTE
6|Certificación UAI A1|Instructivo 2/2008 Anexo I|Caja y Bancos, registros, C43, extractos y arqueo|Rama material de alta relevancia|No ejecutada para SAF355 por el mero modelo|Pedir certificado o no aplicabilidad|CERTIFICATION_OPEN
7|Certificación UAI A4|Instructivo 2/2008 Anexo IV|C35, C41, C42, C43, C55, C75 y C10 fuera de fecha|Rama central para comprobantes target|No queda anulada por excepción de cuadros CGN|Pedir universo y filtros 71597/152677/2876|CERTIFICATION_OPEN
8|Certificación UAI A3|Instructivo 2/2008 Anexo III|Cuadro 5.4 por UEPEX|Sólo si una UEPEX de SAF355 quedó incluida|No universalizar UEPEX a todo SAF355|Pedir índice y no aplicabilidad|NEGATIVE_CONTROL
9|Ruta paralela|Copia a SIGEN por Síndico/Representante|Certificaciones UAI|Segundo custodio potencial|No prueba recepción concreta|Pedir ingreso y ubicación|CUSTODY_ROUTE
10|Resultado actual|Matriz SAF355|0 de 5 certificados ejecutados|Gap permanece abierto|La excepción no convierte 0/5 en inexistencia|Mantener cinco ramas|EVIDENCE_GAP
11|Pago bancario|Documento, sistema, banco y reversas|Ejecución target|Certificado sólo agrega capa documental|No acredita débito ni ausencia de reversa|Conservar 0/10|BANK_GATE
12|Regla final|Método V159|No transposición entre productos|Cada excepción se limita al cuadro expresamente exceptuado|No extenderla a certificados, SIDIF, banco o archivo|Pedir base normativa por objeto|METHOD_LIMIT
""", "NT159_")


negative_fields = ["row_id", "query_or_route", "result", "interpretation", "next_step", "status"]
negative = matrix("E0_V159_PUBLIC_SEARCH_NEGATIVE_RESULTS.csv", negative_fields, """
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
15|Acto contemporáneo que expanda GSEyP en 2009|No localizado|GSEPFyE, GSEPyPF y GSEPYPF no prueban identidad|Pedir organigrama, firma o registro 2008-2009|ACRONYM_IDENTITY_OPEN
16|Universo de UAI e inventario de informes 2009|No localizado|145 UAI corresponde a 2006 y no resuelve 120/160|Pedir censo, inventario y diccionario del indicador|DENOMINATOR_OPEN
17|Respuesta final del expediente ERAS 1085-10|No localizada en esta pieza|El acta sólo documenta giro y obligación de expedirse|Usarlo como modelo de lifecycle, no desenlace|COMPARATOR_FOLLOWUP_OPEN
""", "NR159_")
write_csv(HERE / "E0_V159_PUBLIC_SEARCH_NEGATIVE_RESULTS_V159.csv", negative, negative_fields)


breaks = read_csv(V158 / "E0_FISCAL_METHOD_BREAKS_V158.csv")
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
gsepfye_2003_not_gseyp_2009|identifier|La expansión GSEPFyE en 2003 no identifica por sí sola el token GSEyP de 2009.|Exigir acto, firma o registro contemporáneo 2008-2009.|FROZEN|Memoria SIGEN 2003
gsepypf_2010_not_gseyp_2009|identifier|El sufijo GSEPYPF de una nota 2010 no prueba equivalencia con GSEyP de la Nota 3672/09.|Mantener búsquedas separadas.|FROZEN|Acta ERAS 09/2010
structure_2004_not_structure_2009|organization|La estructura documentada por Resoluciones 58/04 y 91/04 puede haber cambiado antes del target.|Pedir organigrama y responsabilidades vigentes 2008-2009.|FROZEN|Memoria SIGEN 2004
name_variant_not_silent_normalization|identifier|Las variantes Economía/Económica y Entidades/Entidad/Entes Reguladores deben conservarse literalmente.|Buscar cada forma y registrar fecha/fuente.|FROZEN|Memorias 2003-2004 y Plan 2008
uai_count_not_report_count|denominator|Cantidad de UAI no equivale a cantidad de informes.|Definir unidad de observación para cada agregado.|FROZEN|Memoria SIGEN 2006
project_count_not_report_count|denominator|Proyecto previsto o concluido no equivale a informe emitido o remitido.|Pedir diccionario de estados y productos.|FROZEN|Memoria SIGEN 2006
uai_2006_not_uai_2009_census|time|Las 145 UAI supervisadas en 2006 no son un censo de 2009.|Pedir inventario institucional del año target.|FROZEN|Memoria SIGEN 2006
recipient_internal_routing_not_response|phase|El giro a áreas para expedirse no acredita que respondieron ni que el Directorio cerró el asunto.|Pedir pases, respuestas y acta posterior.|FROZEN|Expediente ERAS 1085-10
note_area_suffix_not_report_body|document|El sufijo GSEPYPF identifica metadato de nota, no contenido ni firmante del informe adjunto.|Pedir nota y cuerpo completos.|FROZEN|Nota SIGEN 4712/2010-GSEPYPF
saf355_general_table_exception_not_registration_exemption|scope|La excepción a cuadros estándar no elimina registros, consultas especiales o movimientos.|Mantener rutas SIDIF, UAI, archivo y banco.|FROZEN|Disposición CGN 49/02 y Cuenta 2008
saf355_general_table_exception_not_uai_certificate_exception|scope|La excepción de cierre general no demuestra no aplicabilidad de los Anexos I-V UAI.|Pedir certificado o fundamento por anexo.|FROZEN|Instructivo 2/2008
one_custodian_negative_not_chain_closure|custody|Una búsqueda negativa en SIGEN o receptor no cierra la copia del otro custodio.|Exigir respuestas testadas de ambos fondos.|FROZEN|Comparadores ERAS 2009-2010
""", break_fields, "")
breaks = upsert(breaks, break_add, "break_id")
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V159.csv", breaks, break_fields)


trace = read_csv(V158 / "E0_INFORMATION_REQUEST_TRACEABILITY_V158.csv")
trace_fields = list(trace[0])
trace_add = pipe_rows("""
REQ159_SIGEN|SIGEN Organización/Archivo|CL159_GSEYP_IDENTITY|Acto contemporáneo que expanda GSEyP|2008-2009|Nota 3672/09; variantes 2003-2013|acto; organigrama; unidad; vigencia; firma; dependencia|copia testada o certificación|DRAFT_NOT_SENT
REQ159_SIGEN|SIGEN Organización/Archivo|CL159_STRUCTURE_SUCCESSION|Sucesión Gerencia-Subgerencia-Sindicatura Economía|2003-2010|Resoluciones 87/03;58/04;91/04 y Plan 2008|unidad; responsabilidad; vigencia; antecesora; sucesora|crosswalk cronológico|DRAFT_NOT_SENT
REQ159_SIGEN|SIGEN|CL159_TOKEN_SEARCH|Búsqueda literal por cuatro tokens|2003-2010|GSEPFyE;GSEyP;GSEPyPF;GSEPYPF|serie; fecha; nota; informe; firmante; destinatario|resultado separado por token|DRAFT_NOT_SENT
REQ159_SIGEN|SIGEN|CL159_UAI_2009_CENSUS|Inventario de UAI supervisadas|2009|145 corresponde sólo a 2006|UAI; jurisdicción; alta; baja; período; gerencia|censo testado|DRAFT_NOT_SENT
REQ159_SIGEN|SIGEN Planificación|CL159_COUNT_DICTIONARY|Diccionario de indicadores|2009|120 versus 160|unidad; estado; cobertura; corte; redondeo; fuente|metodología certificada|DRAFT_NOT_SENT
REQ159_SIGEN|SIGEN Planificación|CL159_COUNT_INVENTORY|Inventario de Informes de Supervisión|2009|dos agregados oficiales discordantes|número; UAI; fecha; período; estado; anulación|inventario deduplicable|DRAFT_NOT_SENT
REQ159_SIGEN|SIGEN Planificación|CL159_ECONOMY_ROW|Fila UAI Economía en el inventario|2009|target individual|número; título; gerencia; nota; destinatario; estado|fila y cuerpo vinculados|DRAFT_NOT_SENT
REQ159_SIGEN|SIGEN Mesa/Archivo|CL159_NOTE_REPORT_FILE_CHAIN|Nota, informe y legajo interno|2009-2010|modelos ERAS 5095/09 y 4712/10|números; fecha; fojas; adjuntos; pases; acuse|cadena testada|DRAFT_NOT_SENT
REQ159_ECON|Economía Mesa/UAI|CL159_RECIPIENT_FILE_CHAIN|Expediente receptor y copia recibida|2009-2010|modelos ERAS 878-09 y 1085-10|carátula; índice; copia; pases; áreas; respuestas|expediente completo|DRAFT_NOT_SENT
REQ159_ECON|Economía áreas competentes|CL159_INTERNAL_RESPONSE|Informes internos y tratamiento final|2009-2010|giro a áreas como comparador|pase; responsable; dictamen; elevación; acta; cierre|cuerpos y acto final|DRAFT_NOT_SENT
REQ159_CGN|CGN|CL159_SAF355_EXCEPTION_SCOPE|Alcance exacto de excepción SAF355|2008-2009|Disposición 49/02 y Cuenta 2008|cuadro exceptuado; base; sustituto; consulta; custodio|certificación normativa|DRAFT_NOT_SENT
REQ159_ECON|UAI Economía/SAF355|CL159_SAF355_A1|Certificación Caja y Bancos o no aplicabilidad|2008-2009|Instructivo 2/2008 Anexo I|certificado; fuentes; firma; fecha; remisión; acuse|copia y papeles|DRAFT_NOT_SENT
REQ159_ECON|UAI Economía/SAF355|CL159_SAF355_A4|Certificación formularios fuera de fecha|2008-2009|Instructivo 2/2008 Anexo IV|universo; C41; C42; C55; ids target; estado final|listado y certificado|DRAFT_NOT_SENT
REQ159_SIGEN|SIGEN y Economía|CL159_DUAL_CUSTODY_NEGATIVE|Búsqueda negativa testada en ambos fondos|2008-2010|cadena nota-informe-expediente|repositorio; consulta; parámetros; fecha; resultado; disposición|actas o certificados|DRAFT_NOT_SENT
REQ159_ECON|Tesoro/Finanzas/Banco|CL159_FINAL_BANK_GATE|Conciliación final y reversas|2008-2009|71597;152677;2876;C41;C42;C55|id; cuenta; importe; moneda; fecha valor; débito; reversa|fila testada|DRAFT_NOT_SENT
""", trace_fields, "TR159_")
trace = upsert(trace, trace_add, "trace_id")
write_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V159.csv", trace, trace_fields)


keys = read_csv(V158 / "E0_REQUEST_SEARCH_KEY_MATRIX_V158.csv")
key_fields = list(keys[0])
key_add = pipe_rows("""
REQ159_SIGEN|acronym|GSEPFyE Gerencia Supervisión Economía Planificación Federal Entidades|expansión 2003-2004|Memorias SIGEN 2003-2004|No trasladar a 2009.
REQ159_SIGEN|acronym|GSEyP Nota SIGEN 3672/09|token target literal|Cuenta de Inversión 2009 UEPEX|Expansión abierta.
REQ159_SIGEN|acronym|GSEPyPF Cuenta 2008 Ministerio Economía 2009|token de inventario|Libro Blanco SIGEN 2012|Buscar separado.
REQ159_SIGEN|acronym|GSEPYPF Nota 4712/2010|token de nota|Acta ERAS 09/2010|No equivale a GSEyP.
REQ159_SIGEN|organization|Gerencia Supervisión Economía Planificación Federal Entes Reguladores|nombre largo contemporáneo|Plan SIGEN 2008|Sigla no indicada.
REQ159_SIGEN|legal_act|Resolución SGN 87/03 58/04 91/04 estructura supervisión|sucesión organizacional|Memorias SIGEN|Pedir actos completos.
REQ159_SIGEN|record_type|organigrama responsabilidades primarias acciones SIGEN 2008 2009|unidad competente target|Método V159|No localizado.
REQ159_SIGEN|counts|145 Unidades Auditoría Interna planeamientos 2007|comparador de unidades|Memoria SIGEN 2006 p.3|No universo 2009.
REQ159_SIGEN|counts|143 proyectos 318 proyectos 119 informes 145 UAI|separación denominadores|Memoria SIGEN 2006 p.3|No mezclar magnitudes.
REQ159_SIGEN|counts|aproximadamente 120 cerca de 160 Supervisión Planeamiento 2009|conflicto target|Cuenta y Memoria SIGEN 2009|Inventario abierto.
REQ159_SIGEN|method|unidad observación estado corte redondeo cobertura Informes Supervisión 2009|diccionario del indicador|Método V159|No localizado.
REQ159_SIGEN|record_type|inventario UAI supervisadas 2009 jurisdicción gerencia|censo target|Método V159|No localizado.
REQ159_SIGEN|record_type|inventario Informes Supervisión Planeamiento 2009 número UAI fecha estado|resolver 120/160|Método V159|No localizado.
REQ159_SIGEN|identifier|Nota 4712/2010 GSEPYPF Expediente 1085-10|modelo nota-informe-expediente|Acta ERAS 09/2010|Comparador no target.
REQ159_ECON|record_type|expediente receptor informe SIGEN UAI Economía 2009 pases respuestas acta|lifecycle target|Comparadores ERAS|Número local abierto.
REQ159_CGN|scope|SAF355 356 exceptuados cuadros estándar Disposición 49/02|alcance excepción|Cuenta 2008 UEPEX|No exención registral.
REQ159_ECON|record_type|SAF355 Anexo I Caja Bancos certificado no aplicabilidad 2008|certificación UAI|Instructivo 2/2008|0/5.
REQ159_ECON|record_type|SAF355 Anexo IV C41 C42 C55 71597 152677 2876|comprobantes fuera de fecha|Instructivo 2/2008|0 filas.
REQ159_SIGEN|crosswalk|nota informe expediente receptor pases respuesta SISIO|cadena documental|V159|Objetos separados.
REQ159_ECON|target_ids|71597 152677 2876 C41 C42 C55 banco reversa|cierre final|Matriz acumulada|0/10.
""", key_fields, "SK159_")
keys = upsert(keys, key_add, "key_id")
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V159.csv", keys, key_fields)


objects = read_csv(V158 / "E0_V158_REQUEST_OBJECTS.csv")
object_fields = list(objects[0])
object_add = pipe_rows("""
SIGEN_GSEYP_2009_IDENTITY_ACT|SIGEN Organización/Archivo|Acto que expanda GSEyP y ubique la unidad|2008-2009|acto; vigencia; dependencia; responsable; firma|Copia testada|DRAFT_NOT_SENT
SIGEN_SUPERVISION_STRUCTURE_SUCCESSION|SIGEN Organización/Archivo|Crosswalk GSEPFyE-GSEyP-GSEPyPF-GSEPYPF|2003-2013|token; nombre; unidad; antecesora; sucesora; fecha|Tabla certificada|DRAFT_NOT_SENT
SIGEN_UAI_2009_CENSUS|SIGEN Planificación|Inventario de UAI supervisadas|2009|UAI; jurisdicción; gerencia; alta; baja; período|CSV testado|DRAFT_NOT_SENT
SIGEN_PLANNING_COUNT_DICTIONARY_2009|SIGEN Planificación|Diccionario y regla de conteo 120/160|2009|unidad; universo; estado; corte; redondeo; exclusiones|Metodología certificada|DRAFT_NOT_SENT
SIGEN_PLANNING_REPORT_INVENTORY_2009|SIGEN Planificación|Inventario de Informes de Supervisión|2009|número; UAI; título; fecha; estado; anulación|CSV deduplicable|DRAFT_NOT_SENT
SIGEN_ECONOMY_SUPERVISION_REPORT_ROW|SIGEN/UAI Economía|Fila y cuerpo del informe Economía|2009|número; título; gerencia; nota; destinatario; estado|Fila y PDF vinculados|DRAFT_NOT_SENT
SIGEN_ECONOMY_NOTE_REPORT_RECIPIENT_LIFECYCLE|SIGEN/Economía|Nota, informe, expediente, pases y respuesta|2009-2010|números; fechas; fojas; acuses; áreas; acto final|Cadena completa|DRAFT_NOT_SENT
SAF355_CLOSING_EXCEPTION_SCOPE_CERTIFICATE|CGN|Alcance normativo y sustitutos de la excepción|2008-2009|cuadros; base; listados; consultas; responsables|Certificación testada|DRAFT_NOT_SENT
SAF355_UAI_ANNEX_I_EXECUTION|UAI Economía/SAF355|Certificado Caja y Bancos o no aplicabilidad|2008-2009|cifras; fuentes; firma; remisión; acuse; papeles|Copia y anexos|DRAFT_NOT_SENT
SAF355_UAI_ANNEX_IV_EXECUTION|UAI Economía/SAF355|Certificado formularios fuera de fecha|2008-2009|C41; C42; C55; ids; importe; estado; fuentes|Listado y certificado|DRAFT_NOT_SENT
DUAL_CUSTODY_TESTED_NEGATIVE|SIGEN/Economía|Búsqueda negativa en emisor y receptor|2008-2010|repositorio; consulta; parámetros; fecha; resultado; disposición|Actas o certificados|DRAFT_NOT_SENT
""", object_fields, "RO159_")
objects = upsert(objects, object_add, "row_id")
write_csv(HERE / "E0_V159_REQUEST_OBJECTS.csv", objects, object_fields)
write_csv(HERE / "E0_V159_REQUEST_OBJECTS_V159.csv", objects, object_fields)


catalog_map = {source["filename"]: source["id"] for source in SOURCES}
roles = {
    "sigen_memoria_2003_gsepfye_note_suffix_and_area.pdf": "CONTEMPORARY_LONG_NAME_GSEPFYE_AND_STRUCTURE",
    "sigen_memoria_2004_supervision_structure_and_record_systems.pdf": "EXPLICIT_GSEPFYE_STRUCTURE_AND_RECORD_SYSTEM_CAPABILITY",
    "sigen_memoria_2006_uai_universe_145.pdf": "UAI_PROJECT_REPORT_DENOMINATOR_COMPARATOR",
    "eras_act_09_2010_gsepypf_note_recipient_file.pdf": "NOTE_REPORT_RECIPIENT_FILE_INTERNAL_ROUTING_COMPARATOR",
}
bundle_fields = ["row_id", "filename", "role", "catalogued", "catalog_source_id", "bytes", "sha256", "preserved"]
bundle = []
for index, path in enumerate(sorted(BIN.iterdir(), key=lambda value: value.name.casefold()), 1):
    if path.is_file():
        bundle.append(dict(zip(bundle_fields, [f"B159_{index:02d}", path.name, roles[path.name],
                                               "YES", catalog_map[path.name], path.stat().st_size,
                                               sha256(path), "YES"])))
write_csv(HERE / "E0_V159_SOURCE_BUNDLE.csv", bundle, bundle_fields)


visual = read_csv(V158 / "E0_V158_PDF_VISUAL_CONTROL.csv")
visual_fields = list(visual[0])
visual_add = pipe_rows("""
e0_sigen_memoria_2003_gsepfye_area_and_note_suffix|3|3|Nombre largo de Gerencia y Notas 4997/03, 5152/03-5154/03 con sufijo GSEPFyE|PASS|Asociación 2003; no identidad con GSEyP 2009
e0_sigen_memoria_2003_gsepfye_area_and_note_suffix|7|7|Resolución 87/03, Subgerencia Economía y Planificación Federal y seis Sindicaturas|PASS|Estructura 2003; no organigrama 2009
e0_sigen_memoria_2004_supervision_structure_and_record_systems|8|8|Resoluciones 58/04 y 91/04, dos Subgerencias y control de Fondos Fiduciarios|PASS|Estructura 2004; no custodia target
e0_sigen_memoria_2004_supervision_structure_and_record_systems|9|9|Mesa de Entradas, Bonos de Consolidación, legajo electrónico y expansión GSEPFyE|PASS|Capacidad general; no asiento target
e0_sigen_memoria_2006_uai_and_output_measure_denominators|3|3|145 UAI, 143 proyectos previstos, 318 concluidos y 119 informes|PASS|Denominadores distintos; no censo 2009
e0_eras_act_09_2010_gsepypf_note_report_and_recipient_file|5|5|Nota 4712/2010-GSEPYPF, informe 2009, Expediente 1085-10 y giro a áreas|PASS|Comparador de lifecycle; no target Economía
""", visual_fields, "PV159_")
visual += visual_add
write_csv(HERE / "E0_V159_PDF_VISUAL_CONTROL.csv", visual, visual_fields)
images = read_csv(V158 / "E0_V158_IMAGE_VISUAL_CONTROL.csv")
write_csv(HERE / "E0_V159_IMAGE_VISUAL_CONTROL.csv", images, list(images[0]))


append_section(HERE / "SOURCE_REFERENCES_V159.md", "## V159 · siglas, denominadores y lifecycle receptor", """
- Memoria SIGEN 2003: https://www.argentina.gob.ar/sites/default/files/memoria_sigen_2003.pdf
- Memoria SIGEN 2004: https://www.argentina.gob.ar/sites/default/files/memoria_sigen_2004.pdf
- Memoria SIGEN 2006: https://www.argentina.gob.ar/sites/default/files/memoria_sigen_2006.pdf
- Plan SIGEN 2008: https://www.infoleg.gob.ar/basehome/actos_gobierno/actosdegobierno15-9-2008-5.htm
- Cuenta de Inversión 2009, UEPEX: https://www.economia.gob.ar/hacienda/cgn/cuenta/2009/sep/uepex.htm
- Memoria SIGEN 2009: https://www.argentina.gob.ar/sites/default/files/memoria_sigen_2009.pdf
- Libro Blanco SIGEN 2012: https://www.argentina.gob.ar/sites/default/files/libro_blanco_sigen2012.pdf
- Acta ERAS 09/2010: https://www.argentina.gob.ar/sites/default/files/contrataciones/2010/acta%200910.pdf
- Resolución SIGEN 93/2013: https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-93-2013-218161/texto

Alcance: GSEPFyE queda expandida en 2003-2004, pero GSEyP, GSEPyPF y GSEPYPF continúan como tokens separados hasta hallar un acto contemporáneo que los encadene. Las 145 UAI de 2006 no reconcilian los 120/160 informes de 2009: la misma memoria separa UAI, proyectos e informes como denominadores distintos. El Acta ERAS 09/2010 prueba un ciclo nota-informe-expediente-pases-respuesta esperada, sólo como comparador. La excepción SAF355 a cuadros estándar no se transpone a los certificados UAI, consultas SIDIF ni prueba bancaria.
""")

request_section = """
V159 agrega una búsqueda institucional testable por cuatro tokens separados —GSEPFyE, GSEyP, GSEPyPF y GSEPYPF— y solicita el acto, organigrama, firma o registro 2008-2009 que identifique la unidad de la Nota 3672/09. La asociación nombre largo/GSEPFyE está probada para 2003-2004, pero no se retrotrae ni proyecta a otros tokens. Para el conflicto 120/160 se piden tres cuerpos distintos: censo de UAI 2009; inventario de Informes de Supervisión, una fila por documento; y diccionario del indicador con universo, estado, fecha de corte, redondeo y exclusiones. Las 145 UAI de 2006 son sólo comparador de denominador. El lifecycle receptor se solicita como nota, informe adjunto, expediente, pases a áreas, respuestas y acto final, con acuses y fojas en SIGEN y Economía. La excepción SAF355 se limita a los cuadros estándar: deben certificarse separadamente Anexo I Caja y Bancos y Anexo IV formularios fuera de fecha —incluidos C41/C42/C55 e identificadores 71597, 152677 y 2876— o explicarse su no aplicabilidad. Todo continúa BORRADOR_NO_ENVIADO / DRAFT_NOT_SENT; SAF355 0/5 y ejecución bancaria 0/10.
"""
append_section(HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V159.md", "## V159 · siglas, denominadores, lifecycle y no transposición SAF355", request_section)
append_section(HERE / "REQUEST_SUBMISSION_CHECKLIST_V159.md", "## Control previo V159 · siglas, denominadores, lifecycle y no transposición SAF355", request_section)

register = read_csv(V158 / "E0_REQUEST_RESPONSE_REGISTER_V158.csv")
for row in register:
    row.update({"draft_file": row["draft_file"].replace("V158", "V159"),
                "status": "DRAFT_NOT_SENT", "submitted_on": "N/A", "submission_channel": "N/A",
                "receipt_or_case_id": "N/A", "response_date": "N/A"})
write_csv(HERE / "E0_REQUEST_RESPONSE_REGISTER_V159.csv", register, list(register[0]))


(HERE / "README_V159.md").write_text(f"""# Checkpoint V159

- Fuentes maestras: {len(catalog)}; E0: {len(census)}; nuevas: {len(source_rows)}.
- GSEPFyE queda expandida por fuentes 2003-2004; GSEyP, GSEPyPF y GSEPYPF permanecen separados.
- Falta el acto contemporáneo 2008-2009 que identifique la unidad productora de la Nota 3672/09.
- Memoria 2006 separa 145 UAI, 143 proyectos previstos, 318 concluidos y 119 informes: son denominadores distintos.
- El conflicto 120/160 de 2009 exige censo UAI, inventario de informes y diccionario de estados/corte; no un prorrateo.
- Acta ERAS 09/2010 prueba nota, informe, expediente receptor y giro a áreas como ciclo documental comparador.
- La excepción SAF355 a cuadros estándar no elimina certificados UAI, SIDIF, banco ni reversas.
- SAF355 0/5; ejecución 0/10; seis borradores no enviados.
""", encoding="utf-8")
(HERE / "VEREDICTO_V159.md").write_text("""# Veredicto V159

V159 estrecha la búsqueda sin cerrar indebidamente la identidad institucional. GSEPFyE tiene expansión oficial en 2003-2004, pero no existe todavía un puente contemporáneo hacia GSEyP de la Nota 3672/09. Las 145 UAI de 2006 no resuelven 120/160: unidad, proyecto e informe son magnitudes distintas y el año target requiere inventario y regla de conteo. El Acta ERAS 09/2010 fortalece la ruta del receptor porque vincula Nota 4712/2010-GSEPYPF, informe 2009, Expediente 1085-10 y pases internos, sin demostrar el desenlace ni el target Economía. La excepción SAF355 sigue siendo de producto/ruta, no de registración ni de prueba bancaria. Resultado 0/10; SAF355 0/5; seis borradores no enviados.
""", encoding="utf-8")
(HERE / "E0_FISCAL_RECONSTRUCTION_V159.md").write_text("""# Reconstrucción fiscal E0 V159

La reconstrucción incorpora una cronología de unidades y tokens SIGEN, un control de denominadores y un lifecycle de recepción. Se piden por separado el acto que expanda GSEyP, el censo de UAI 2009, el inventario de informes, la metodología 120/160, la fila Economía, la nota de remisión, el expediente receptor, sus pases, respuestas y acto final. Para SAF355, la excepción de cuadros generales no se transpone a los certificados Anexo I/IV ni a listados SIDIF. Estas capas permiten hallar el cuerpo y sus custodios; documento, sistema, banco y reversas continúan siendo necesarios para la ejecución. Estado 0/10.
""", encoding="utf-8")
(HERE / "RETRIEVAL_LOG_V159.md").write_text("""# Retrieval log V159

- Recuperada Memoria SIGEN 2003; control visual de páginas PDF 3 y 7: nombre largo, GSEPFyE, Resolución 87/03 y estructura.
- Recuperada Memoria SIGEN 2004; control visual de páginas PDF 8 y 9: Resoluciones 58/04 y 91/04, dos Subgerencias, sistemas documentales y expansión GSEPFyE.
- Recuperada Memoria SIGEN 2006; control visual de página PDF 3: 145 UAI, 143 proyectos previstos, 318 concluidos y 119 informes.
- Recuperada Acta ERAS 09/2010; control visual de página PDF 5: Nota 4712/2010-GSEPYPF, informe 2009, Expediente 1085-10 y giro a áreas.
- Congelada la no equivalencia automática GSEPFyE/GSEyP/GSEPyPF/GSEPYPF y la separación UAI/proyecto/informe.
- Reforzada la no transposición de la excepción SAF355; certificados 0/5, banco 0/10 y seis DRAFT_NOT_SENT.
""", encoding="utf-8")

stale = HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V159_A_V159.md"
if stale.exists():
    stale.unlink()
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V159_A_V160.md").write_text("""# Handover V159 → V160

## Estado

- GSEPFyE expandida oficialmente en 2003-2004; GSEyP, GSEPyPF y GSEPYPF siguen separados.
- Falta acto/organigrama/firma 2008-2009 que identifique la unidad de Nota 3672/09.
- 145 UAI es dato 2006; 120/160 son informes aproximados 2009 y requieren inventario/metodología.
- ERAS 2010 prueba Nota 4712/2010-GSEPYPF, informe 2009, Expediente 1085-10 y giro a áreas.
- Excepción SAF355 a cuadros estándar no cierra Anexos I/IV, SIDIF, banco ni reversas.
- SAF355 0/5; banco 0/10; seis DRAFT_NOT_SENT.

## Prioridad V160

1. Recuperar Resoluciones 87/03, 58/04, 91/04 y organigrama/responsabilidades 2008-2009 completos.
2. Hallar expansión o firma contemporánea de GSEyP y separar resultados por cuatro tokens.
3. Recuperar censo UAI 2009, inventario 120/160, diccionario de indicador y fila Economía.
4. Buscar Nota 3672/09, cuerpo, expediente receptor, pases, respuestas y acto final en ambos custodios.
5. Ejecutar ramas SAF355 Anexo I/IV, SISIO, banco y reversas sin usar la excepción como cierre.
6. No enviar solicitudes sin autorización expresa.
""", encoding="utf-8")

append_section(REPO / "BACKUP_ACTUALIZACION_2026-08-29.md", "## V159 · siglas, denominadores, lifecycle y no transposición SAF355", """
- GSEPFyE queda expandida en 2003-2004; otros tres tokens permanecen separados.
- La estructura 2003-2004 y el nombre largo del Plan 2008 amplían claves sin demostrar productor target.
- 145 UAI, 143 proyectos, 318 proyectos y 119 informes prueban denominadores distintos.
- ERAS 2010 agrega expediente receptor, pases a áreas y respuesta esperada al modelo de remisión.
- La excepción SAF355 a cuadros generales no se extiende a certificados UAI ni banco.
- Cuatro fuentes nuevas; seis páginas PDF nuevas controladas.
- SAF355 0/5; ejecución 0/10; seis borradores no enviados.
""")

write_csv(HERE / "INHERITED_QA_STATUS_V159.csv", [
    {"script": "qa_v158.py", "pre_v159_result": "PASS", "post_v159_result": "PASS_BASELINE", "interpretation": "V158 íntegra; V159 agrega siglas, denominadores y lifecycle sin alterar 0/10."},
    {"script": "qa_v159.py", "pre_v159_result": "N/A", "post_v159_result": "PASS", "interpretation": "Verifica cuatro fuentes, cuatro matrices nuevas, seis controles PDF y límites V159."},
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
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V159.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V159.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)

size_rows = []
for path in iter_files(REPO):
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": size,
                      "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576),
                      "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V159.csv", size_rows)

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V158.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint": "V159", "date": "2026-08-31",
    "state": "E0_SIGEN_ACRONYM_TIMELINE_DENOMINATOR_SEPARATION_RECIPIENT_LIFECYCLE_AND_SAF355_NONTRANSPOSITION_FROZEN_TARGET_BODIES_OPEN_NOT_SENT",
    "master_catalog_entries": len(catalog), "physical_local_copies": physical,
    "physical_local_hash_ok": hash_ok, "remaining_physical_gaps": len(catalog) - physical,
    "e0_primary_sources_preserved": len(census), "numeric_V159_strict_changed": False,
    "sources_newly_preserved_V159": len(source_rows), "e0_primary_sources_newly_preserved_V159": len(source_rows),
    "e0_fiscal_method_breaks_frozen": len(breaks), "e0_request_traceability_rows": len(trace),
    "e0_request_search_keys": len(keys), "e0_V159_pdf_visual_controls": len(visual),
    "e0_V159_new_pdf_visual_controls": len(visual_add), "e0_V159_image_visual_controls": len(images),
    "e0_V159_total_visual_controls": len(visual) + len(images), "e0_V159_source_bundle_files": len(bundle),
    "e0_V159_plan_chain_rows": len(plan_chain), "e0_V159_account_program_rows": len(account_program),
    "e0_V159_system_separation_rows": len(systems), "e0_V159_supervision_inventory_rows": len(supervision),
    "e0_V159_archive_route_rows": len(archive), "e0_V159_public_search_rows": len(negative),
    "e0_V159_preliminary_final_workflow_rows": len(workflow),
    "e0_V159_reorganization_version_rows": len(reorganization),
    "e0_V159_supervision_count_conflict_rows": len(count_conflict),
    "e0_V159_supervision_delivery_metadata_rows": len(delivery),
    "e0_V159_acronym_timeline_rows": len(acronym_timeline),
    "e0_V159_denominator_control_rows": len(denominator_control),
    "e0_V159_recipient_lifecycle_rows": len(recipient_lifecycle),
    "e0_V159_saf355_nontransposition_rows": len(saf_nontransposition),
    "e0_V159_request_objects": len(objects), "e0_plan_sigen_2009_approval_date_located": True,
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
    "e0_gsepfye_2003_2004_long_name_expansion_located": True,
    "e0_gseyp_2009_contemporary_expansion_located": False,
    "e0_sigen_supervision_structure_2009_located": False,
    "e0_uai_2006_supervised_count_145_located": True,
    "e0_uai_2009_census_located": False,
    "e0_uai_project_report_denominator_separation_proven": True,
    "e0_eras_2010_note_report_file_internal_routing_comparator_located": True,
    "e0_saf355_general_closing_exception_nontransposition_frozen": True,
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
    "historical_workstream": "Recover contemporary GSEyP identity and 2009 structure; obtain UAI census, 120/160 inventory/method and Economy row; recover note, report, recipient file, passes and response; then SAF355 Annex I/IV, SISIO, bank and reversals; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V159.json").write_text(
    json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

(HERE / "AUDITORIA_V159.md").write_text(f"""# Auditoría V159

- Fuentes maestras: {len(catalog)}; E0: {len(census)}; nuevas: {len(source_rows)}.
- Copias/hash: {physical}/{hash_ok}; brechas: {len(catalog) - physical}.
- Quiebres: {len(breaks)}; trazas: {len(trace)}; claves: {len(keys)}; objetos: {len(objects)}.
- Visuales: {len(visual)} PDF ({len(visual_add)} nuevos) + {len(images)} imágenes = {len(visual) + len(images)}.
- Bundle: {len(bundle)}; cadena histórica: {len(plan_chain)}; programa Cuenta: {len(account_program)}; sistemas: {len(systems)}; supervisión heredada: {len(supervision)}; archivo: {len(archive)}.
- Matrices V159: circuito preliminar-final {len(workflow)}; reforma/versiones {len(reorganization)}; contradicción 120/160 {len(count_conflict)}; entrega de supervisión {len(delivery)}; negativos {len(negative)}.
- Nuevas V159: cronología de siglas {len(acronym_timeline)}; control de denominadores {len(denominator_control)}; lifecycle receptor {len(recipient_lifecycle)}; no transposición SAF355 {len(saf_nontransposition)}.
- Plan/acto/legajo/versiones/subplan/supervisión: 0 cuerpos target; SAF355 0/5; ejecución 0/10; pedidos/respuestas 0/0.
""", encoding="utf-8")


def checkpoint_manifest():
    files = [{"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
             for path in sorted(HERE.iterdir()) if path.is_file() and path.name != "MANIFEST_V159.json"]
    payload = {
        "checkpoint": "V159", "parent_checkpoint": "V158",
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
        "acronym_timeline_rows": len(acronym_timeline),
        "denominator_control_rows": len(denominator_control),
        "recipient_lifecycle_rows": len(recipient_lifecycle),
        "saf355_nontransposition_rows": len(saf_nontransposition),
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
        "gsepfye_2003_2004_long_name_expansion_located": True,
        "gseyp_2009_contemporary_expansion_located": False,
        "sigen_supervision_structure_2009_located": False,
        "uai_2006_supervised_count_145_located": True,
        "uai_2009_census_located": False,
        "uai_project_report_denominator_separation_proven": True,
        "eras_2010_note_report_file_internal_routing_comparator_located": True,
        "saf355_general_closing_exception_nontransposition_frozen": True,
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
    (HERE / "MANIFEST_V159.json").write_text(
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
    "checkpoint": "V159",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master; {physical} physical SHA-valid; {len(source_rows)} new sources; plan/version/supervision target bodies open; 120/160 conflict frozen; 0/10; six drafts not submitted.",
    "historical_workstream": "Recover plan file and version/approval chain; reconcile supervision counts; recover delivery note, report and recipient file; then SISIO, notes, SAF355, bank and reversals; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
temporary = global_manifest.with_suffix(".json.V159tmp")
temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
temporary.replace(global_manifest)

print(f"V159 BUILD PASS · catalog={len(catalog)} · E0={len(census)} · physical={physical} · hash_ok={hash_ok} · breaks={len(breaks)} · trace={len(trace)} · keys={len(keys)} · objects={len(objects)} · visual={len(visual) + len(images)}")
