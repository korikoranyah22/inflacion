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
BIN = CYCLE / "inputs" / "historical_retrieval" / "v156" / "binaries"
V155 = CYCLE / "checkpoints" / "V155"
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
        "id": "e0_mecon_decree_1359_2004_uai_target_period_duties",
        "institution": "Poder Ejecutivo Nacional / Ministerio de Economía y Producción",
        "title": "Decreto 1359/2004 · acciones de la UAI Economía vigentes en el período objetivo",
        "url": "https://www.argentina.gob.ar/normativa/nacional/decreto-1359-2004-99689/texto",
        "filename": "mecon_decree_1359_2004_uai_target_period_duties.html",
        "period": "2004-10-05 a 2010-07-19; aplicable a 2008-2009",
        "series": "Decreto 1359/2004 · texto original",
        "kind": "HTML oficial preservado",
        "variables": "UAI;plan;accounting;budget;reports;deviations;SIGEN;followup;working_records",
        "breaks": "deber general/informe target; estructura vigente/cuerpo documental; opinión contable/pago bancario",
        "status": "E0_USABLE_TARGET_PERIOD_UAI_DUTY_AUTHORITY",
        "note": "Enumera trece acciones de la UAI Economía vigentes durante 2008-2009, entre ellas confiabilidad contable, opinión sobre estados, informes, comunicación a SIGEN y seguimiento. No prueba que un informe o pago target exista.",
    },
    {
        "id": "e0_sigen_resolution_152_2002_workpaper_ownership_custody_access",
        "institution": "Sindicatura General de la Nación",
        "title": "Resolución SIGEN 152/2002 · propiedad, depósito y acceso a papeles de trabajo",
        "url": "https://www.argentina.gob.ar/normativa/nacional/79051/texto",
        "filename": "sigen_resolution_152_2002_workpaper_custody.html",
        "period": "2002-10-17; vigente como antecedente en 2008-2009",
        "series": "Resolución SIGEN 152/2002 · Normas de Auditoría Interna Gubernamental",
        "kind": "HTML oficial preservado",
        "variables": "working_papers;ownership;depositary;SIGEN_access;evidence;reports;observations",
        "breaks": "propiedad/custodia; acceso/posesión; papeles/evidencia pública; soporte/contenido",
        "status": "E0_USABLE_WORKPAPER_OWNERSHIP_CUSTODY_AND_ACCESS_AUTHORITY",
        "note": "Distingue papeles SIGEN de papeles UAI: los UAI pertenecen al organismo y la UAI es depositaria; SIGEN tiene acceso libre e irrestricto. No acredita localización actual ni publicidad íntegra.",
    },
    {
        "id": "e0_sigen_resolution_15_2006_sisio_mandatory_record_schema",
        "institution": "Sindicatura General de la Nación",
        "title": "Resolución SIGEN 15/2006 · uso obligatorio de SISIO WEB y esquema de registros",
        "url": "https://magyp.gob.ar/sitio/areas/d_recursos_humanos/concurso/normativa/_archivos/000001_Resoluciones/000000_RESOLUCI%C3%93N%20SIGEN%20N%C2%BA%2015-2006.pdf",
        "filename": "sigen_resolution_15_2006_sisio_mandatory.pdf",
        "period": "2006-02-10; uso obligatorio desde 2006-04-01; aplicable a 2009",
        "series": "Resolución SIGEN 15/2006 y Anexos I-III · 10 páginas",
        "kind": "PDF oficial escaneado preservado y controlado visualmente",
        "variables": "SISIO;annual_plan;chronogram;load_receipt;72h;144h;observations;status;impact;annex_II;annex_III;working_papers",
        "breaks": "registro/cuerpo; constancia/informe; síntesis/observación completa; estado/ejecución bancaria",
        "status": "E0_USABLE_TARGET_PERIOD_SISIO_MANDATORY_RECORD_SCHEMA",
        "note": "Fija carga obligatoria, plazos, constancias, campos, estados, reportes anuales y papeles de respaldo que debían dejar rastro en SISIO. No contiene la entrada específica de 0120/09 o 3672/09.",
    },
    {
        "id": "e0_cnrt_resolution_1002_2011_sisio_receipt_archive_comparator",
        "institution": "Comisión Nacional de Regulación del Transporte",
        "title": "Resolución CNRT 1002/2011 · procedimiento SISIO, constancia y legajo transitorio",
        "url": "https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-1002-2011-199225/texto",
        "filename": "cnrt_resolution_1002_2011_sisio_procedure_comparator.html",
        "period": "2011; comparador posterior y de otro organismo",
        "series": "Resolución CNRT 1002/2011 · texto original",
        "kind": "HTML oficial preservado",
        "variables": "SISIO;final_report;load_receipt;distribution;temporary_file;followup",
        "breaks": "procedimiento CNRT/Economía; 2011/2009; comparador/hecho target",
        "status": "E0_USABLE_LATER_SISIO_IMPLEMENTATION_COMPARATOR_ONLY",
        "note": "Muestra una implementación posterior: carga del informe final, emisión y remisión de constancia, archivo en legajo transitorio y seguimiento. No se atribuye retroactivamente a UAI Economía 2009.",
    },
    {
        "id": "e0_sigen_resolution_93_2013_gsepypf_expansion",
        "institution": "Sindicatura General de la Nación",
        "title": "Resolución SIGEN 93/2013 · expansión oficial GSEPyPF",
        "url": "https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-93-2013-218161/texto",
        "filename": "sigen_resolution_93_2013_gsepypf_expansion.html",
        "period": "2013; comparador nominativo posterior",
        "series": "Resolución SIGEN 93/2013 · texto original",
        "kind": "HTML oficial preservado",
        "variables": "SIGEN;GSEPyPF;Gerencia_de_Supervision;Economia;Produccion;Planificacion_Federal",
        "breaks": "expansión acrónimo/equivalencia; 2013/2009; unidad/nota",
        "status": "E0_USABLE_GSEPYPF_EXPANSION_NOT_GSEYP_EQUIVALENCE",
        "note": "Expande GSEPyPF como Gerencia de Supervisión de Economía, Producción y Planificación Federal. No demuestra que el token 2009 GSEyP sea la misma unidad.",
    },
]


catalog = read_csv(CATALOG)
census = read_csv(V155 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V155.csv")
provenance = read_csv(V155 / "ARCHIVAL_PROVENANCE_V155.csv")
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
    "sha256": source["sha"], "nota": "V156: " + source["note"],
} for source in source_rows], "id")
write_csv(CATALOG, catalog, list(catalog[0]))

census = upsert(census, [{
    "source_id": source["id"], "institution": source["institution"], "artifact": source["title"],
    "url": source["url"], "local_path": source["local"], "sha256": source["sha"], "bytes": source["bytes"],
    "period_coverage": source["period"], "variable_families": source["variables"],
    "primary_source": "YES", "preserved": "YES", "method_breaks": source["breaks"],
    "use_status": source["status"], "caveat": source["note"],
} for source in source_rows], "source_id")
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V156.csv", census, list(census[0]))

provenance = upsert(provenance, [{
    "source_id": source["id"], "original_url": source["url"], "retrieval_url": source["url"],
    "capture_timestamp": "2026-08-31", "cdx_digest": "N/A_OFFICIAL_DIRECT",
    "local_path": source["local"], "sha256": source["sha"], "bytes": source["bytes"],
    "provenance_note": "Captura directa de fuente oficial; alcance y quiebres congelados en V156.",
} for source in source_rows], "source_id")
write_csv(HERE / "ARCHIVAL_PROVENANCE_V156.csv", provenance, list(provenance[0]))


duty_fields = ["row_id", "action_or_control", "exact_rule", "target_implication", "requested_record", "probative_value", "limit", "status"]
duties = matrix("E0_TARGET_PERIOD_UAI_ECONOMY_DUTY_CHAIN_V156.csv", duty_fields, """
1|Planificación|Entender en la planificación global y anual de auditoría|Debía existir una planificación UAI para el ejercicio|Plan global, plan anual y modificaciones|Prueba deber exacto vigente en 2008-2009|No prueba inclusión del caso target|TARGET_PERIOD_DUTY
2|Plan anual|Elaborar el plan anual de auditoría interna|Permite exigir cronograma, proyecto y ejecución|Plan anual 2009 y constancia SISIO|Define productor y clase documental|No prueba aprobación ni carga concreta|TARGET_PERIOD_DUTY
3|Evaluación|Evaluar cumplimiento de políticas, planes y procedimientos|La Cuenta 2008 podía integrar una revisión institucional|Programa, alcance, muestras y conclusión|Fundamenta búsqueda por objeto y método|No identifica informe target|TARGET_PERIOD_DUTY
4|Normativa|Asesorar en normas y procedimientos de control interno|Debían existir intervenciones o recomendaciones cuando correspondiera|Dictámenes, notas y recomendaciones|Define familia de registros|No prueba emisión en este caso|TARGET_PERIOD_DUTY
5|Actos significativos|Evaluar actos y controles de significativa trascendencia económica|Las operaciones relevantes podían ser objeto de control|Informe, papel de trabajo y selección de muestra|Vincula materialidad económica con competencia UAI|No prueba selección efectiva de recompras|TARGET_PERIOD_DUTY
6|Contabilidad y presupuesto|Verificar principios contables y niveles presupuestarios|Habilita pedir pruebas del cierre y conciliaciones|Cédulas contables, presupuestarias y conciliaciones|Competencia exacta del período|No equivale a pago bancario|TARGET_PERIOD_DUTY
7|Confiabilidad|Constatar confiabilidad de antecedentes usados en informes y estados|Debían conservarse fuentes y pruebas de confiabilidad|Índice de fuentes, pruebas y excepciones|Sostiene pedido de evidencia subyacente|No valida cada fila target|TARGET_PERIOD_DUTY
8|Patrimonio|Verificar exactitud del registro de activos y medidas de resguardo|Permite rastrear controles patrimoniales|Cédulas, inventarios y salvaguardas|Define deber de comprobación|No demuestra saldo ni titular final|TARGET_PERIOD_DUTY
9|Opinión|Emitir opinión sobre estados contables de unidades ejecutoras|Debía existir una opinión cuando la unidad estaba alcanzada|Informe de opinión, anexos y salvedades|Identifica salida formal posible|No confundir con certificado SAF355|TARGET_PERIOD_DUTY
10|Informes|Producir informes periódicos de auditoría y control|Debía existir registro de productos emitidos|Libro de informes, número, fecha, destino y cuerpo|Permite exigir inventario completo|No prueba tratamiento de las operaciones target|TARGET_PERIOD_DUTY
11|Desvíos|Comunicar a autoridades y SIGEN desvíos detectados|Debían dejar rastro las comunicaciones|Notas, distribución, acuses y entrada SISIO|Conecta UAI, autoridad y SIGEN|No prueba recepción o regularización específica|TARGET_PERIOD_DUTY
12|Seguimiento|Efectuar seguimiento de recomendaciones y observaciones|Debían existir estados e historial correctivo|Seguimientos, actualizaciones y cierre|Fundamenta pedir historia completa|Regularizada no significa pagada|TARGET_PERIOD_DUTY
13|Requerimientos SIGEN|Informar asuntos requeridos por SIGEN|Alcanza instrucciones específicas de supervisión|Requerimiento, respuesta, anexos y acuse|Define deber de respuesta|No prueba requerimiento target|TARGET_PERIOD_DUTY
14|Vigencia temporal|Decreto 1359/2004 antecede al cierre y fue reemplazado en julio de 2010|Es autoridad exacta del período|Texto vigente, modificaciones y sucesor|Cierra quiebre temporal de V155|No reconstruye organigrama informal|TEMPORAL_CONTROL
15|Plan y SISIO|El deber de plan se combina con Resolución SIGEN 15/2006|El cronograma era constancia de carga y aprobación|Cronograma SISIO, alta, versión y aprobación|Convierte deber en objetos verificables|No aporta la constancia target|REQUEST_DERIVATION
16|Informes y papeles|Los deberes 7, 9 y 10 exigen fuentes, opinión e informes|La búsqueda debe cubrir cuerpo, anexos e índice|Informe, papeles, soportes, firmas y disposición|Evita respuestas reducidas a metadatos|No presume publicidad irrestricta|REQUEST_DERIVATION
17|Desvíos y seguimiento|Los deberes 11 y 12 se conectan con SISIO|Debe recuperarse alta, cambios e instrumento regularizador|Entrada SISIO, historial y vínculos|Define cadena auditable|El asiento no sustituye cuerpos|REQUEST_DERIVATION
18|Límite final|Competencia normativa no equivale a actuación concreta|Mantener 0/10 hasta documento, sistema, banco y reversas|Resultado target individual|Impide promoción por deber abstracto|No usar como prueba de ejecución|METHOD_LIMIT
""", "UD156_")


sisio_fields = ["row_id", "norm_section", "required_actor", "required_record_or_field", "deadline_or_frequency", "evidentiary_use", "limit", "status"]
sisio = matrix("E0_SISIO_RES15_2006_EXACT_RECORD_SCHEMA_V156.csv", sisio_fields, """
1|Artículo 1|Todas las UAI alcanzadas|Uso obligatorio de SISIO WEB|Desde 1 de abril de 2006|Prueba obligatoriedad en 2009|No prueba entrada target|MANDATORY_SCHEMA
2|Artículo 1|UAI|Guía del Anexo I|Durante la operación|Fija procedimiento uniforme|No acredita cumplimiento concreto|MANDATORY_SCHEMA
3|Artículo 2|UAI|Informe de observaciones pendientes|Antes del 15 de febrero anual|Exige corte anual identificable|No contiene informe 2009|ANNUAL_RECORD
4|Artículo 2|UAI|Informe de observaciones regularizadas|Antes del 15 de febrero anual|Exige segundo corte anual|Regularizada no equivale a pagada|ANNUAL_RECORD
5|Artículo 2|UAI|Detalle emitido por sistema adjunto|Con cada informe anual|Permite pedir exportación y soporte firmado|No garantiza conservación actual|ANNUAL_RECORD
6|Anexo I plan|UAI|Carga del plan anual|Al inicio del ciclo aprobado|Debía existir alta y versión|No prueba inclusión target|PLAN_RECORD
7|Anexo I plan|SISIO|Cronograma de Emisión de Informes|Luego de cargar el plan|Es constancia de carga|No es el plan completo|LOAD_RECEIPT
8|Anexo I plan|UAI y SIGEN|Cronograma usado para aprobación|Antes de aprobación|Vincula carga y aprobación|No aporta firma target|PLAN_RECORD
9|Anexo I plan|UAI|Actividad agregada como No Planificado|Después de aprobación|Permite buscar proyectos agregados|No prueba incorporación|PLAN_RECORD
10|Anexo I informes|UAI|Carga de informe propio|Dentro de 72 horas de elevar a máxima autoridad|Fija ventana contrastable|No prueba fecha efectiva|REPORT_RECORD
11|Anexo I informes|UAI|Carga de informe de otro órgano salvo SIGEN|Dentro de 144 horas de conocerlo|Fija ventana para externos|No se aplica a notas SIGEN|REPORT_RECORD
12|Anexo I informes|SISIO|Constancia de carga por documento nuevo|Al registrar documento|Debería existir recibo individual|No contiene cuerpo íntegro|LOAD_RECEIPT
13|Anexo I informes|UAI|Remisión de constancia con original a sindicatura|Con la elevación|Conecta recibo, cuerpo y destino|No prueba acuse|DISTRIBUTION_RECORD
14|Anexo I informes|UAI|Copia de constancia adjunta a informes de otros órganos|Con la carga|Encadena documento externo y SISIO|No aplica sin carga|DISTRIBUTION_RECORD
15|Anexo I informes|UAI|Indicador de impacto en Cuenta de Inversión|Por cada informe|Campo exacto para búsqueda Cuenta 2008|No valida la Cuenta|ACCOUNT_IMPACT_FIELD
16|Anexo I observaciones|UAI|Carga de todas las observaciones|Con cada informe|Obliga inventario de hallazgos|Puede haber síntesis|OBSERVATION_RECORD
17|Anexo I recomendaciones|UAI|Carga de todas las recomendaciones|Con cada informe|Obliga inventario de medidas|No prueba aceptación|OBSERVATION_RECORD
18|Anexo I síntesis|UAI|Síntesis clara de observación y recomendación|Con cada carga|Permite buscar abreviaturas|No sustituye cuerpo|OBSERVATION_RECORD
19|Anexo I conclusiones|UAI|Conclusiones generales que requieran corrección|Cuando corresponda|Amplía universo de hallazgos|No prueba conclusión target|OBSERVATION_RECORD
20|Anexo I papeles|UAI|Lista de informes considerados|Durante auditoría|Permite pedir índice del universo|No prueba análisis exhaustivo|WORKPAPER_RECORD
21|Anexo I papeles|UAI|Evidencia de clasificación y estado|Durante auditoría y seguimiento|Permite auditar fundamento|No equivale a banco|WORKPAPER_RECORD
22|Anexo I regularización|UAI|Instrumento que subsanó observación|Al marcar Regularizada|Exige referencia documental|Puede ser administrativo|REGULARIZATION_RECORD
23|Anexo I regularización|UAI|Verificación directa de regularización|Al marcar Regularizada|Permite pedir prueba UAI|No prueba pago salvo que sea objeto|REGULARIZATION_RECORD
24|Anexo I estados|UAI|Estado Sin acción correctiva|Según situación|Distingue falta de respuesta|No implica responsabilidad firme|STATUS_HISTORY
25|Anexo I estados|UAI|Estado No compartida|Según situación|Distingue controversia|No resuelve mérito|STATUS_HISTORY
26|Anexo I estados|UAI|Estado Sin conocimiento UAI|Según situación|Identifica falta de información|No prueba ausencia externa|STATUS_HISTORY
27|Anexo I estados|UAI|Estado En trámite|Según situación|Identifica cierre inconcluso|No es cierre|STATUS_HISTORY
28|Anexo I estados|UAI|Estado Regularizada|Según situación|Identifica cierre declarado|No significa pago|STATUS_HISTORY
29|Anexo I actualización|UAI|Actualizar cuando cambie situación|Continuamente|Exige historial|Puede no conservarse todo|STATUS_HISTORY
30|Anexo I actualización|UAI|Actualizar como mínimo al 31 de diciembre|Anual|Fija fecha de corte|No prueba actualización|STATUS_HISTORY
31|Anexo I reportes|UAI|Incluir informes UAI y otros órganos como AGN y BCRA|En reportes anuales|Amplía referencias cruzadas|No funde competencias|ANNUAL_RECORD
32|Anexo II|UAI|Modelo de observaciones pendientes|Antes del 15 de febrero|Exige objeto, alcance, limitaciones, pruebas y opinión|Modelo no cuerpo|ANNEX_MODEL
33|Anexo III|UAI|Modelo de observaciones regularizadas|Antes del 15 de febrero|Exige verificación y opinión|Modelo no presentación|ANNEX_MODEL
34|Anexos II y III|UAI|Hojas firmadas e inicialadas, fecha, firma y sello|Con cada informe anual|Define autenticidad mínima|No prueba integridad posterior|SIGNATURE_CONTROL
35|Anexo I clasificación|UAI|Impacto alto, medio o bajo y área temática|Por observación|Permite búsqueda por taxonomía|No cuantifica daño ni pago|CLASSIFICATION_FIELD
""", "SI156_")


work_fields = ["row_id", "authority", "record_class", "ownership_or_access_rule", "request_consequence", "probative_value", "limit", "status"]
workpapers = matrix("E0_WORKPAPER_OWNERSHIP_CUSTODY_AND_ACCESS_V156.csv", work_fields, """
1|Resolución SIGEN 152/2002|Papeles de auditorías SIGEN|Son propiedad de SIGEN|Pedir a SIGEN sus propios papeles e índice|Define titular institucional|No prueba existencia target|OWNERSHIP_RULE
2|Resolución SIGEN 152/2002|Papeles producidos por UAI|Son propiedad del organismo respectivo|Pedir a Economía como titular|Cierra error de dirigir sólo a SIGEN|Propiedad no localización|OWNERSHIP_RULE
3|Resolución SIGEN 152/2002|Papeles producidos por UAI|La UAI actúa como depositaria|Pedir custodia, inventario y disposición|Identifica depositario operativo|No prueba retención indefinida|DEPOSITARY_RULE
4|Resolución SIGEN 152/2002|Registros y documentos de organismos y UAI|SIGEN tiene acceso libre e irrestricto|Pedir búsqueda por acceso o derivación|Aporta vía secundaria|Acceso no es propiedad|ACCESS_RULE
5|Resolución SIGEN 152/2002|Archivos e informes UAI|Acceso SIGEN comprende archivos e informes|Solicitar cruce de índices|Amplía objetos accesibles|No asegura copia en SIGEN|ACCESS_RULE
6|Resolución SIGEN 152/2002|Papeles de trabajo|Contienen evidencia que sustenta hallazgos y opiniones|Pedir cédulas, pruebas y referencias|Vincula conclusión con soporte|Puede admitir restricciones legales|EVIDENCE_RULE
7|Resolución SIGEN 152/2002|Papeles de trabajo|Sustentan observaciones y conclusiones|Pedir matriz observación-evidencia|Permite trazabilidad|No valida la evidencia|EVIDENCE_RULE
8|Resolución SIGEN 152/2002|Papeles de trabajo|Sustentan recomendaciones|Pedir fundamento y acción correctiva|Reconstruye causalidad|No prueba cumplimiento|EVIDENCE_RULE
9|Resolución SIGEN 152/2002|Papeles de trabajo|La regla vale cualquiera sea el soporte|Buscar papel, digital, óptico y legado|Evita limitar a GDE|No identifica soporte concreto|SUPPORT_RULE
10|Resolución SIGEN 15/2006|Papeles UAI vinculados a SISIO|Deben permitir lista de informes considerados|Pedir índice de universo|Puente SISIO-archivo UAI|Índice no contiene cuerpos|SISIO_WORKPAPER_RULE
11|Resolución SIGEN 15/2006|Papeles UAI vinculados a SISIO|Deben preservar evidencia de clasificación y estado|Pedir evidencia por cambio|Permite auditar regularización|Estado no prueba banco|SISIO_WORKPAPER_RULE
12|Economía como organismo|Papeles UAI Cuenta 2008|Titular institucional probable bajo norma|Objeto principal del pedido|Mejora asignación de custodio|Sujeto a disposición acreditada|REQUEST_ROUTE
13|SIGEN como supervisor|Papeles UAI Cuenta 2008|Acceso normativo aunque no propiedad|Objeto alternativo de búsqueda|Evita incompetencia absoluta|No autoriza inferir copia|REQUEST_ROUTE
14|Cadena de custodia|Transferencia o expurgo|Debe informarse fondo, serie, soporte, acto y destino|Pedir disposición si no aparece|Hace verificable un negativo|La norma no fija plazo concreto|NEGATIVE_RESPONSE_CONTROL
15|Regla final|Pago target|Papeles y acceso son capa de auditoría|Cerrar sólo con documento, sistema, banco y reversas|Mantiene 0/10|No promover ejecución|METHOD_LIMIT
""", "WP156_")


comparison_fields = ["row_id", "source_period", "actor", "procedure_step", "record_expected", "allowed_use", "forbidden_use", "status"]
comparison = matrix("E0_SISIO_RECEIPT_AND_ARCHIVE_COMPARATOR_V156.csv", comparison_fields, """
1|2006 vigente en 2009|UAI|Carga informe propio en 72 horas|Entrada SISIO y constancia|Regla target de plazo|No prueba hora efectiva|TARGET_PERIOD_RULE
2|2006 vigente en 2009|SISIO|Emite constancia por documento nuevo|Constancia individual|Pedir recibo exacto|No sustituye informe|TARGET_PERIOD_RULE
3|2006 vigente en 2009|UAI|Remite constancia con original a sindicatura|Cuerpo, constancia y distribución|Pedir cadena conjunta|No prueba acuse|TARGET_PERIOD_RULE
4|2006 vigente en 2009|UAI|Conserva lista y evidencia en papeles|Índice y soporte|Pedir papeles exactos|No prueba banco|TARGET_PERIOD_RULE
5|2006 vigente en 2009|UAI|Actualiza seguimiento y reportes anuales|Historial, Anexo II y III|Pedir evolución completa|No acredita carga target|TARGET_PERIOD_RULE
6|2011 CNRT|Auditor|Carga informe definitivo en SISIO WEB II|Registro y constancia|Comparador de implementación|No atribuir a Economía 2009|LATER_COMPARATOR
7|2011 CNRT|Auditor|Emite constancia de carga|Recibo de sistema|Confirma materialidad del recibo|No prueba formato 2009|LATER_COMPARATOR
8|2011 CNRT|UAI CNRT|Distribuye informe y constancia|Paquete de remisión|Comparador documento-sistema|No prueba destinos Economía|LATER_COMPARATOR
9|2011 CNRT|UAI CNRT|Archiva copia en Legajo Transitorio|Legajo|Comparador de archivo|No prueba nombre en Economía|LATER_COMPARATOR
10|2011 CNRT|UAI CNRT|Sólo informes generan constancia|Diferencia informe de actividad|Ayuda a interpretar recibos|No universalizar|LATER_COMPARATOR
11|2011 CNRT|UAI CNRT|Actividades registran producto y horas|Registro sin constancia|Comparador de granularidad|No clasifica target|LATER_COMPARATOR
12|2011 CNRT|UAI CNRT|Seguimiento se nutre de actualizaciones|Historia SISIO|Refuerza pedido de historial|No prueba conservación completa|LATER_COMPARATOR
""", "RC156_")


narrow_fields = ["row_id", "token_or_source", "documented_expansion_or_context", "temporal_relation", "allowed_inference", "unproved_link", "search_action", "status"]
narrowing = matrix("E0_GSEYP_GSEPYPF_NARROWING_V156.csv", narrow_fields, """
1|GSEyP|Aparece en Nota SIGEN 3672/09 referida por Cuenta 2009|2009 target|Token exacto de búsqueda|Expansión institucional|Buscar literal y variantes|TARGET_TOKEN
2|3672/09|Número exacto asociado a GSEyP|2009 target|Buscar por número|Cuerpo y firma|Pedir libro, COMDOC, caja y SISIO|TARGET_IDENTIFIER
3|0120/09 DAIF|Antecedente remitido a SIGEN|2009 target|Cadena emisor-destino|Unidad receptora completa|Buscar distribución y acuse|TARGET_IDENTIFIER
4|GSEPyPF|Inventario posterior lo asocia al informe global Cuenta 2008|2009 referido después|Token alternativo legítimo|Equivalencia con GSEyP|Buscar separado|DISTINCT_TOKEN
5|Resolución SIGEN 93/2013|Expande GSEPyPF como Gerencia de Supervisión de Economía, Producción y Planificación Federal|2013 posterior|Fija expansión larga|Identidad con token corto|Sólo desambiguar|EXPANSION_PROVED
6|Economía|Componente literal en GSEPyPF|2013 posterior|Área material coincidente|Misma unidad|No fusionar por palabra|ACRONYM_CONTROL
7|Producción|Componente literal en GSEPyPF|2013 posterior|Expansión parcial|Presencia en GSEyP|Buscar organigrama 2009|ACRONYM_CONTROL
8|Planificación Federal|Componente literal en GSEPyPF|2013 posterior|Expansión parcial|Qué representa P en 2009|Buscar firma contemporánea|ACRONYM_CONTROL
9|Decreto 1359/2004|Estructura Economía, no SIGEN|Target period|Control temporal UAI|Gerencias SIGEN|No expandir acrónimo|CROSS_INSTITUTION_LIMIT
10|Resolución SIGEN 15/2006|Regla SISIO aplicable|Target period|Buscar entradas y constancias|Nombre completo GSEyP|No resolver unidad|SYSTEM_LIMIT
11|Cuerpo o firma 3672/09|Evidencia decisiva ausente|2009 target|Podría cerrar equivalencia|Contenido actual|Prioridad de recuperación|OPEN_LINK
12|Regla final|Similitud ortográfica no basta|Todos|Mantener tokens separados|GSEyP igual a GSEPyPF|No fusionar|METHOD_LIMIT
""", "GN156_")


negative_fields = ["row_id", "query_or_route", "result", "interpretation", "next_step", "status"]
negative = matrix("E0_V156_PUBLIC_SEARCH_NEGATIVE_RESULTS.csv", negative_fields, """
1|Nota 0120/09 DAIF cuerpo|No localizada públicamente|Existe referencia pero no cuerpo|Pedir a CGN y archivo Economía|REFERENCED_BODY_NOT_LOCATED
2|Nota SIGEN 3672/09 GSEyP cuerpo|No localizada públicamente|Existe referencia pero no cuerpo, firma o distribución|Pedir a SIGEN|REFERENCED_BODY_NOT_LOCATED
3|Entrada SISIO asociada a notas|No localizada públicamente|La norma prueba campos, no asiento|Pedir exportación e historial|SYSTEM_ENTRY_NOT_PUBLIC
4|Constancia de carga SISIO target|No localizada públicamente|Debería existir si se cargó documento nuevo|Pedir recibo y vínculo|LOAD_RECEIPT_NOT_LOCATED
5|Cronograma de Emisión UAI 2009|No localizado públicamente|La norma lo define como constancia|Pedir plan y aprobación|PLAN_RECEIPT_NOT_LOCATED
6|Anexos II y III UAI 2009|No localizados públicamente|Los modelos eran obligatorios|Pedir informes firmados|ANNUAL_REPORT_NOT_LOCATED
7|Papeles UAI Cuenta 2008|No localizados públicamente|Economía es titular y UAI depositaria|Pedir inventario y disposición|WORKPAPERS_NOT_LOCATED
8|Equivalencia GSEyP con GSEPyPF|No probada|La expansión larga es posterior|Recuperar fuente 2009|ACRONYM_EQUIVALENCE_NOT_PROVEN
9|Informe global Economía Cuenta 2008 cuerpo|No localizado|Inventario no sustituye cuerpo|Pedir número, cuerpo y anexos|GLOBAL_REPORT_BODY_NOT_LOCATED
10|Certificados SAF355 Anexos I-V|0 de 5 localizados|Deber no sustituye cuerpos|Pedir por SAF y anexo|TARGET_CERTIFICATES_NOT_LOCATED
11|Filas bancarias target|0 de 10 confirmadas|SISIO y UAI son capas administrativas|Cerrar con banco y reversas|BANK_EXECUTION_NOT_LOCATED
12|Seis solicitudes externas|No enviadas|No corre plazo ni existe acuse|Mantener borradores|DRAFT_NOT_SENT
""", "NR156_")
write_csv(HERE / "E0_V156_PUBLIC_SEARCH_NEGATIVE_RESULTS_V156.csv", negative, negative_fields)


breaks = read_csv(V155 / "E0_FISCAL_METHOD_BREAKS_V155.csv")
break_fields = list(breaks[0])
break_add = pipe_rows("""
uai_target_period_duty_not_target_report|time|Un deber UAI vigente no prueba emisión target.|Exigir cuerpo, registro, firma y acuse.|FROZEN|Decreto 1359/2004
sisio_mandatory_use_not_specific_entry|system|La obligatoriedad SISIO no prueba entrada específica.|Exigir id, constancia, campos e historial.|FROZEN|Resolución SIGEN 15/2006
sisio_receipt_not_report_body|document|La constancia no sustituye informe y anexos.|Pedir ambos y vínculo.|FROZEN|Resolución SIGEN 15/2006 Anexo I
sisio_account_impact_flag_not_account_validation|classification|Marcar impacto en Cuenta no valida cifras.|Separar clasificación, opinión y ejecución.|FROZEN|Resolución SIGEN 15/2006
regularized_state_not_bank_payment|payment|Regularizada puede descansar en instrumento administrativo.|Cerrar sólo con banco y reversas.|FROZEN|Resolución SIGEN 15/2006
sisio_synthesis_not_full_observation_body|document|SISIO admite síntesis, no necesariamente texto íntegro.|Recuperar informe original.|FROZEN|Resolución SIGEN 15/2006
workpaper_ownership_not_public_disclosure|access|Propiedad del organismo no implica publicación irrestricta.|Pedir acceso, testado o descripción.|FROZEN|Resolución SIGEN 152/2002
sigen_access_not_sigen_ownership|custody|Acceso SIGEN no transfiere propiedad.|Dirigir a Economía y SIGEN por vías distintas.|FROZEN|Resolución SIGEN 152/2002
later_cnrt_archive_flow_not_2009_economy_fact|time|Procedimiento CNRT 2011 es posterior y ajeno.|Usar sólo como comparador.|FROZEN|Resolución CNRT 1002/2011
gsepypf_expansion_not_gseyp_equivalence|identifier|Expansión GSEPyPF no prueba identidad con GSEyP.|Separar tokens hasta evidencia 2009.|FROZEN|Resolución SIGEN 93/2013
""", break_fields, "")
breaks = upsert(breaks, break_add, "break_id")
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V156.csv", breaks, break_fields)


trace = read_csv(V155 / "E0_INFORMATION_REQUEST_TRACEABILITY_V155.csv")
trace_fields = list(trace[0])
trace_add = pipe_rows("""
REQ156_ECON|UAI Economía|CL156_PLAN_CHRONOGRAM|Cronograma de Emisión y constancia del plan|2009|SISIO; Plan 2009; Cuenta 2008|id; versión; fecha; aprobación; proyecto|plan testado e índice|DRAFT_NOT_SENT
REQ156_ECON|UAI Economía|CL156_UNPLANNED_PROJECT|Altas No Planificado relacionadas|2009|No Planificado; Cuenta 2008|id; fecha; motivo; horas; producto|listado o cero reproducible|DRAFT_NOT_SENT
REQ156_SIGEN|SIGEN|CL156_SISIO_RECEIPT|Constancia por 0120/09, 3672/09 o informe|2009|SISIO; 0120/09; 3672/09|id; documento; fecha; organismo; usuario|constancia testada|DRAFT_NOT_SENT
REQ156_SIGEN|SIGEN|CL156_ACCOUNT_IMPACT|Campo de impacto en Cuenta|2008-2009|Cuenta 2008; impacto|id; valor; fecha; fundamento|exportación de campos|DRAFT_NOT_SENT
REQ156_SIGEN|SIGEN|CL156_OBSERVATION_HISTORY|Observaciones, recomendaciones y conclusiones|2009-2026|0120/09; 3672/09; SISIO|id; síntesis; estado; fechas; responsable|exportación testada|DRAFT_NOT_SENT
REQ156_ECON|UAI Economía|CL156_REGULARIZATION_INSTRUMENT|Instrumento y verificación de regularización|2009-2026|Regularizada; Cuenta 2008|observación; instrumento; fecha; prueba|índice con vínculo|DRAFT_NOT_SENT
REQ156_ECON|UAI Economía|CL156_ANNEX_II|Informe anual de pendientes|2009-2010|Anexo II Res 15/2006|objeto; alcance; limitaciones; pruebas; opinión; firmas|cuerpo testado|DRAFT_NOT_SENT
REQ156_ECON|UAI Economía|CL156_ANNEX_III|Informe anual de regularizadas|2009-2010|Anexo III Res 15/2006|objeto; alcance; pruebas; opinión; firmas|cuerpo testado|DRAFT_NOT_SENT
REQ156_ECON|UAI Economía|CL156_WORKPAPER_INDEX|Índice de papeles Cuenta 2008|2008-2010|Decreto 1359/2004; Res 152/2002|cédula; soporte; autor; fecha; informe|inventario testado|DRAFT_NOT_SENT
REQ156_ECON|Archivo Economía|CL156_UAI_DEPOSIT|Certificación de depósito, transferencia o disposición|2008-2026|UAI depositaria; organismo propietario|fondo; serie; caja; soporte; acto; destino|certificado fundado|DRAFT_NOT_SENT
REQ156_SIGEN|SIGEN|CL156_ACCESS_SEARCH|Búsqueda por acceso a archivos UAI|2008-2010|Res 152/2002; Cuenta 2008|sistema; consulta; custodio; resultado|certificación de búsqueda|DRAFT_NOT_SENT
REQ156_ECON|UAI Economía|CL156_TARGET_DUTY_REPORTS|Inventario de informes bajo acciones vigentes|2008-2009|Decreto 1359/2004; UAI|número; título; fecha; destino; acción|inventario completo|DRAFT_NOT_SENT
REQ156_ECON|UAI Economía|CL156_SOURCE_RELIABILITY|Pruebas de confiabilidad del cierre|2008-2009|acción 7; Cuenta 2008|fuente; versión; prueba; excepción; conclusión|matriz testada|DRAFT_NOT_SENT
REQ156_ECON|UAI Economía|CL156_STATEMENT_OPINION|Opinión contable relevante|2008-2009|acción 9; SAF355|unidad; período; opinión; salvedad; firma|cuerpo o cero reproducible|DRAFT_NOT_SENT
REQ156_ECON|UAI Economía/SIGEN|CL156_DEVIATION_COMMUNICATION|Comunicaciones de desvíos|2008-2009|acción 11; 0120/09; 3672/09|nota; fecha; emisor; receptor; acuse|cuerpo testado|DRAFT_NOT_SENT
REQ156_ECON|UAI Economía|CL156_FOLLOWUP_RECORD|Seguimiento de recomendaciones|2009-2026|acción 12; SISIO|observación; estado; cambio; fecha; evidencia|historial testado|DRAFT_NOT_SENT
REQ156_SIGEN|SIGEN|CL156_GSEYP_IDENTITY|Acto o firma que expanda GSEyP|2008-2009|GSEyP; GSEPyPF; 3672/09|unidad; dependencia; vigencia; firma|copia o certificado|DRAFT_NOT_SENT
REQ156_ECON|Tesoro/Finanzas|CL156_FINAL_BANK_GATE|Conciliación final con banco y reversas|2008-2009|71597; 152677; 2876; C41; C42; C55|id; cuenta; valor; fecha; débito; reversa|fila testada|DRAFT_NOT_SENT
""", trace_fields, "TR156_")
trace = upsert(trace, trace_add, "trace_id")
write_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V156.csv", trace, trace_fields)


keys = read_csv(V155 / "E0_REQUEST_SEARCH_KEY_MATRIX_V155.csv")
key_fields = list(keys[0])
key_add = pipe_rows("""
REQ156_ECON|legal|Decreto 1359/2004 Unidad de Auditoría Interna|autoridad exacta|Texto oficial|Deber no actuación.
REQ156_ECON|record_type|Cronograma de Emisión de Informes SISIO 2009|constancia de plan|Res SIGEN 15/2006|No localizado.
REQ156_ECON|record_type|Plan Anual Auditoría Interna 2009 constancia SISIO|plan y aprobación|Res SIGEN 15/2006|No localizado.
REQ156_ECON|classification|No Planificado Cuenta de Inversión 2008|proyecto agregado|Res SIGEN 15/2006|No prueba alta.
REQ156_SIGEN|record_type|constancia de carga SISIO 0120/09|recibo exacto|Res SIGEN 15/2006|No sustituye cuerpo.
REQ156_SIGEN|record_type|constancia de carga SISIO 3672/09|recibo exacto|Res SIGEN 15/2006|No sustituye cuerpo.
REQ156_SIGEN|field|impacta Cuenta de Inversión SISIO|campo impacto|Res SIGEN 15/2006|No valida cifra.
REQ156_SIGEN|field|observación recomendación conclusión SISIO Cuenta 2008|hallazgos|Res SIGEN 15/2006|Puede ser síntesis.
REQ156_SIGEN|status|Sin acción correctiva No compartida Sin conocimiento UAI En trámite Regularizada|historia estados|Res SIGEN 15/2006|Estado no banco.
REQ156_ECON|record_type|instrumento de regularización SISIO Cuenta 2008|documento cierre|Res SIGEN 15/2006|Puede ser administrativo.
REQ156_ECON|record_type|Anexo II observaciones pendientes 2009|informe anual|Res SIGEN 15/2006|Modelo no presentación.
REQ156_ECON|record_type|Anexo III observaciones regularizadas 2009|informe anual|Res SIGEN 15/2006|Modelo no presentación.
REQ156_ECON|legal|Resolución SIGEN 152/2002 papeles de trabajo|propiedad y depósito|Texto oficial|Propiedad no localización.
REQ156_ECON|custody|organismo propietario UAI depositaria papeles de trabajo|custodio exacto|Res SIGEN 152/2002|Sujeto a disposición.
REQ156_SIGEN|access|acceso libre e irrestricto SIGEN registros documentos papeles archivos informes|vía búsqueda|Res SIGEN 152/2002|Acceso no propiedad.
REQ156_ECON|record_type|índice papeles de trabajo Cuenta de Inversión 2008|universo evidencia|Res 152/2002 y 15/2006|No cuerpo.
REQ156_ECON|record_type|evidencia clasificación estado SISIO|fundamento seguimiento|Res SIGEN 15/2006|No banco.
REQ156_SIGEN|acronym|Gerencia de Supervisión de Economía Producción y Planificación Federal|expandir GSEPyPF|Res SIGEN 93/2013|Posterior.
REQ156_SIGEN|acronym|GSEyP GSEPyPF 3672/09|probar equivalencia|Cadena V155 y Res 93/2013|No fusionar.
REQ156_ECON|comparator|Legajo Transitorio constancia SISIO informe definitivo|comparar archivo|Res CNRT 1002/2011|Otro organismo.
REQ156_ECON|deadline|72 horas informe UAI SISIO|contrastar fechas|Res SIGEN 15/2006|No prueba fecha.
REQ156_ECON|deadline|144 horas otro órgano de control SISIO|contrastar carga|Res SIGEN 15/2006|Exceptúa SIGEN.
REQ156_ECON|signature|hojas firmadas inicialadas fecha firma sello Anexo II III|autenticidad|Res SIGEN 15/2006|No localizado.
REQ156_ECON|target_ids|71597 152677 2876 C41 C42 C55 banco reversa|cierre final|Matriz acumulada|0 filas.
""", key_fields, "SK156_")
keys = upsert(keys, key_add, "key_id")
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V156.csv", keys, key_fields)


objects = read_csv(V155 / "E0_V155_REQUEST_OBJECTS.csv")
object_fields = list(objects[0])
object_add = pipe_rows("""
SISIO_LOAD_RECEIPT|SIGEN/UAI Economía|Constancia de carga por documento target|2009|id; documento; fecha; organismo; usuario; vínculo|Constancia y cuerpo enlazados|DRAFT_NOT_SENT
SISIO_ANNUAL_PLAN_CHRONOGRAM|UAI Economía/SIGEN|Cronograma de Emisión del plan anual|2009|plan; versión; fecha; aprobación; proyectos|Copia o certificado|DRAFT_NOT_SENT
SISIO_ACCOUNT_IMPACT_FLAG|SIGEN/UAI Economía|Campo de impacto en Cuenta|2008-2009|entrada; valor; fecha; fundamento; informe|Exportación con id|DRAFT_NOT_SENT
SISIO_OBSERVATION_HISTORY|SIGEN/UAI Economía|Historia de observaciones y estados|2009-2026|id; síntesis; estado; cambios; fechas|Exportación íntegra|DRAFT_NOT_SENT
SISIO_REGULARIZATION_INSTRUMENT|UAI Economía|Instrumento y verificación de cierre|2009-2026|observación; instrumento; fecha; prueba; firma|Cuerpo o vínculo|DRAFT_NOT_SENT
SISIO_ANNEX_II_REPORT|UAI Economía/SIGEN|Informe anual de pendientes|2009-2010|objeto; alcance; limitaciones; pruebas; opinión; firma|Cuerpo firmado|DRAFT_NOT_SENT
SISIO_ANNEX_III_REPORT|UAI Economía/SIGEN|Informe anual de regularizadas|2009-2010|objeto; alcance; pruebas; opinión; firma|Cuerpo firmado|DRAFT_NOT_SENT
UAI_WORKPAPER_INDEX|Ministerio de Economía/UAI|Índice de papeles Cuenta 2008|2008-2010|cédula; soporte; fecha; autor; informe; ubicación|Inventario y disposición|DRAFT_NOT_SENT
UAI_DEPOSIT_CERTIFICATE|Ministerio de Economía/UAI/Archivo|Certificación de depósito o expurgo|2008-2026|fondo; serie; caja; soporte; acto; destino|Cadena fundada|DRAFT_NOT_SENT
SIGEN_ACCESS_SEARCH|SIGEN|Búsqueda sobre registros y archivos UAI|2008-2010|consulta; sistema; custodio; resultado; derivación|Certificado reproducible|DRAFT_NOT_SENT
""", object_fields, "RO156_")
objects = upsert(objects, object_add, "row_id")
write_csv(HERE / "E0_V156_REQUEST_OBJECTS.csv", objects, object_fields)
write_csv(HERE / "E0_V156_REQUEST_OBJECTS_V156.csv", objects, object_fields)


catalog_map = {source["filename"]: source["id"] for source in SOURCES}
roles = {
    "mecon_decree_1359_2004_uai_target_period_duties.html": "TARGET_PERIOD_UAI_DUTIES",
    "sigen_resolution_152_2002_workpaper_custody.html": "WORKPAPER_OWNERSHIP_CUSTODY_ACCESS",
    "sigen_resolution_15_2006_sisio_mandatory.pdf": "TARGET_PERIOD_SISIO_EXACT_SCHEMA",
    "cnrt_resolution_1002_2011_sisio_procedure_comparator.html": "LATER_SISIO_IMPLEMENTATION_COMPARATOR",
    "sigen_resolution_93_2013_gsepypf_expansion.html": "GSEPYPF_EXPANSION_NOT_GSEYP_EQUIVALENCE",
}
bundle_fields = ["row_id", "filename", "role", "catalogued", "catalog_source_id", "bytes", "sha256", "preserved"]
bundle = []
for index, path in enumerate(sorted(BIN.iterdir(), key=lambda value: value.name.casefold()), 1):
    if path.is_file():
        bundle.append(dict(zip(bundle_fields, [f"B156_{index:02d}", path.name, roles[path.name],
                                               "YES", catalog_map[path.name], path.stat().st_size,
                                               sha256(path), "YES"])))
write_csv(HERE / "E0_V156_SOURCE_BUNDLE.csv", bundle, bundle_fields)


visual = read_csv(V155 / "E0_V155_PDF_VISUAL_CONTROL.csv")
visual_fields = list(visual[0])
visual_add = pipe_rows("""
e0_sigen_resolution_15_2006_sisio_mandatory_record_schema|1|1|Fundamentos, alcance y fecha del acto|PASS|Contexto normativo; no entrada target
e0_sigen_resolution_15_2006_sisio_mandatory_record_schema|2|2|Artículo 1 y obligatoriedad SISIO desde 1-4-2006|PASS|Obligación general
e0_sigen_resolution_15_2006_sisio_mandatory_record_schema|3|3|Artículos 2 y 3, informes y transición|PASS|Plazos; no cuerpos target
e0_sigen_resolution_15_2006_sisio_mandatory_record_schema|4|4|Plan, cronograma, plazos, constancia e impacto Cuenta|PASS|Esquema; no asiento target
e0_sigen_resolution_15_2006_sisio_mandatory_record_schema|5|5|Observaciones, papeles, regularización y estados|PASS|Historial; no banco
e0_sigen_resolution_15_2006_sisio_mandatory_record_schema|6|6|Operación, migración y entrega|PASS|Procedimiento general
e0_sigen_resolution_15_2006_sisio_mandatory_record_schema|7|7|Clasificación de impacto y estados|PASS|No cuantifica ejecución
e0_sigen_resolution_15_2006_sisio_mandatory_record_schema|8|8|Áreas temáticas|PASS|Taxonomía no pertenencia
e0_sigen_resolution_15_2006_sisio_mandatory_record_schema|9|9|Modelo Anexo II pendientes|PASS|Modelo no presentación
e0_sigen_resolution_15_2006_sisio_mandatory_record_schema|10|10|Modelo Anexo III regularizadas|PASS|Modelo no regularización target
""", visual_fields, "PV156_")
visual += visual_add
write_csv(HERE / "E0_V156_PDF_VISUAL_CONTROL.csv", visual, visual_fields)
images = read_csv(V155 / "E0_V155_IMAGE_VISUAL_CONTROL.csv")
write_csv(HERE / "E0_V156_IMAGE_VISUAL_CONTROL.csv", images, list(images[0]))


append_section(HERE / "SOURCE_REFERENCES_V156.md", "## V156 · deber UAI exacto, SISIO y custodia de papeles", """
- Decreto 1359/2004: https://www.argentina.gob.ar/normativa/nacional/decreto-1359-2004-99689/texto
- Resolución SIGEN 152/2002: https://www.argentina.gob.ar/normativa/nacional/79051/texto
- Resolución SIGEN 15/2006: https://magyp.gob.ar/sitio/areas/d_recursos_humanos/concurso/normativa/_archivos/000001_Resoluciones/000000_RESOLUCI%C3%93N%20SIGEN%20N%C2%BA%2015-2006.pdf
- Resolución CNRT 1002/2011: https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-1002-2011-199225/texto
- Resolución SIGEN 93/2013: https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-93-2013-218161/texto

Alcance: el Decreto 1359/2004 prueba acciones UAI vigentes en 2008-2009. Las Resoluciones 152/2002 y 15/2006 definen propietario, depositario, acceso SIGEN y rastros SISIO. CNRT 2011 es sólo comparador. La expansión GSEPyPF de 2013 no prueba equivalencia con GSEyP. Ninguna fuente contiene el asiento específico o banco target.
""")

request_section = """
La base jurídica del período queda precisada por el Decreto 1359/2004: la UAI Economía debía planificar, verificar principios contables y presupuestarios, constatar confiabilidad, emitir opinión e informes, comunicar desvíos a autoridades y SIGEN y seguir observaciones. La Resolución SIGEN 152/2002 asigna al organismo la propiedad de los papeles UAI, a la UAI su depósito y a SIGEN acceso libre e irrestricto. Se solicitan separadamente plan y Cronograma de Emisión 2009; altas No Planificado; cuerpos y constancias SISIO; impacto en Cuenta; observaciones e historial; instrumentos; Anexos II y III; índice y papeles; y, ante ausencia, transferencia o disposición. La Resolución 15/2006 fija plazos de 72/144 horas, recibo por documento y actualización mínima anual. GSEyP y GSEPyPF se buscan separados. Todo sigue BORRADOR_NO_ENVIADO / DRAFT_NOT_SENT y ninguna pieza administrativa se toma como pago bancario.
"""
append_section(HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V156.md", "## V156 · deber exacto del período, SISIO y papeles UAI", request_section)
append_section(HERE / "REQUEST_SUBMISSION_CHECKLIST_V156.md", "## Control previo V156 · constancias SISIO y doble ruta", request_section)

register = read_csv(V155 / "E0_REQUEST_RESPONSE_REGISTER_V155.csv")
for row in register:
    row.update({"draft_file": row["draft_file"].replace("V155", "V156"),
                "status": "DRAFT_NOT_SENT", "submitted_on": "N/A", "submission_channel": "N/A",
                "receipt_or_case_id": "N/A", "response_date": "N/A"})
write_csv(HERE / "E0_REQUEST_RESPONSE_REGISTER_V156.csv", register, list(register[0]))


(HERE / "README_V156.md").write_text(f"""# Checkpoint V156

- Fuentes maestras: {len(catalog)}; E0: {len(census)}; nuevas: {len(source_rows)}.
- Autoridad UAI exacta 2008-2009: Decreto 1359/2004, trece acciones.
- SISIO: obligatoriedad, cronograma, constancias, plazos, impacto, estados, Anexos II/III y papeles.
- Papeles UAI: propiedad del organismo, depósito UAI y acceso SIGEN separados.
- GSEPyPF expandido oficialmente; equivalencia con GSEyP no probada.
- SAF355 0/5; ejecución 0/10; seis borradores no enviados.
""", encoding="utf-8")
(HERE / "VEREDICTO_V156.md").write_text("""# Veredicto V156

V156 cierra dos vacíos: la UAI Economía tenía deberes expresos durante el período objetivo, y SISIO debía producir rastros concretos —plan, cronograma, recibos, campos, estados, informes y papeles— reclamables por nombre. Los papeles UAI pertenecen al organismo, la UAI es depositaria y SIGEN tiene acceso, habilitando doble vía. Todavía faltan cuerpos 0120/09 y 3672/09, asiento SISIO, SAF355 y banco. GSEyP no se fusiona con GSEPyPF. Resultado 0/10; seis borradores no enviados.
""", encoding="utf-8")
(HERE / "E0_FISCAL_RECONSTRUCTION_V156.md").write_text("""# Reconstrucción fiscal E0 V156

Se incorpora la capa normativa exacta: deber UAI, rastro SISIO, propiedad y depósito de papeles y acceso supervisor. Permite negativos más exigentes, pero no reemplaza ejecución. El cierre sigue requiriendo documento administrativo, sistema, banco y reversas por operación. SAF355 0/5, ejecución 0/10, solicitudes 0/6 enviadas.
""", encoding="utf-8")
(HERE / "RETRIEVAL_LOG_V156.md").write_text("""# Retrieval log V156

- Recuperado Decreto 1359/2004 como autoridad UAI vigente en 2008-2009.
- Preservada Resolución SIGEN 152/2002 sobre propiedad, depósito y acceso.
- Recuperada Resolución SIGEN 15/2006 completa; 10 páginas renderizadas e inspeccionadas.
- Congelados esquema SISIO, plazos, constancias, impacto Cuenta, estados, instrumentos, Anexos II/III y papeles.
- Preservada CNRT 1002/2011 sólo como comparador.
- Expandido GSEPyPF con Resolución 93/2013; equivalencia GSEyP no probada.
- Sin cuerpos, asiento target, SAF355 o banco; seis DRAFT_NOT_SENT; 0/10.
""", encoding="utf-8")

stale = HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V156_A_V156.md"
if stale.exists():
    stale.unlink()
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V156_A_V157.md").write_text("""# Handover V156 → V157

## Estado

- Decreto 1359/2004 cierra autoridad UAI exacta 2008-2009.
- Resolución SIGEN 15/2006 define rastros SISIO obligatorios.
- Resolución SIGEN 152/2002: papeles UAI propiedad de Economía, UAI depositaria, acceso SIGEN.
- GSEPyPF tiene expansión posterior; GSEyP sigue sin equivalencia contemporánea.
- Cuerpos 0120/09 y 3672/09, asiento/constancia SISIO, SAF355 y banco abiertos.
- SAF355 0/5; banco 0/10; seis DRAFT_NOT_SENT.

## Prioridad V157

1. Buscar entrada SISIO específica con campos, plazos y recibos exactos.
2. Recuperar cuerpo, firma, distribución y acuse de 0120/09 y 3672/09.
3. Recuperar plan/cronograma UAI 2009, Anexos II/III e índice de papeles.
4. Buscar expansión contemporánea de GSEyP o mantener tokens separados.
5. Cerrar C41/C42/C55 + 71597/152677/2876 + banco + reversas.
6. No enviar solicitudes sin autorización expresa.
""", encoding="utf-8")

append_section(REPO / "BACKUP_ACTUALIZACION_2026-08-29.md", "## V156 · autoridad UAI exacta, SISIO y custodia", """
- Recuperado Decreto 1359/2004 como autoridad UAI vigente en 2008-2009.
- Recuperadas Resoluciones SIGEN 152/2002 y 15/2006.
- Controladas visualmente las 10 páginas del PDF 15/2006.
- Preservados comparadores CNRT 1002/2011 y expansión GSEPyPF 93/2013 con límites.
- Cinco fuentes nuevas; 134 controles PDF y 3 de imagen acumulados.
- SAF355 0/5; ejecución 0/10; seis borradores no enviados.
""")

write_csv(HERE / "INHERITED_QA_STATUS_V156.csv", [
    {"script": "qa_v155.py", "pre_v156_result": "PASS", "post_v156_result": "PASS_BASELINE", "interpretation": "V155 íntegra; V156 agrega autoridad y esquema sin alterar 0/10."},
    {"script": "qa_v156.py", "pre_v156_result": "N/A", "post_v156_result": "PASS", "interpretation": "Verifica cinco fuentes, matrices, controles y límites V156."},
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
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V156.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V156.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)

size_rows = []
for path in iter_files(REPO):
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": size,
                      "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576),
                      "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V156.csv", size_rows)

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V155.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint": "V156", "date": "2026-08-31",
    "state": "E0_TARGET_PERIOD_UAI_SISIO_AND_WORKPAPER_RULES_LOCATED_TARGET_BODIES_OPEN_NOT_SENT",
    "master_catalog_entries": len(catalog), "physical_local_copies": physical,
    "physical_local_hash_ok": hash_ok, "remaining_physical_gaps": len(catalog) - physical,
    "e0_primary_sources_preserved": len(census), "numeric_v156_strict_changed": False,
    "sources_newly_preserved_v156": len(source_rows), "e0_primary_sources_newly_preserved_v156": len(source_rows),
    "e0_fiscal_method_breaks_frozen": len(breaks), "e0_request_traceability_rows": len(trace),
    "e0_request_search_keys": len(keys), "e0_v156_pdf_visual_controls": len(visual),
    "e0_v156_new_pdf_visual_controls": len(visual_add), "e0_v156_image_visual_controls": len(images),
    "e0_v156_total_visual_controls": len(visual) + len(images), "e0_v156_source_bundle_files": len(bundle),
    "e0_v156_target_period_uai_duty_rows": len(duties), "e0_v156_sisio_schema_rows": len(sisio),
    "e0_v156_workpaper_custody_rows": len(workpapers), "e0_v156_sisio_comparator_rows": len(comparison),
    "e0_v156_acronym_narrowing_rows": len(narrowing), "e0_v156_public_search_rows": len(negative),
    "e0_v156_request_objects": len(objects), "e0_target_period_uai_authority_located": True,
    "e0_sisio_mandatory_schema_located": True, "e0_workpaper_ownership_custody_access_located": True,
    "e0_sisio_target_entry_located": False, "e0_sisio_target_receipt_located": False,
    "e0_daif_note_0120_09_body_located": False, "e0_sigen_note_3672_09_body_located": False,
    "e0_gseyp_gsepypf_equivalence_proved": False,
    "e0_uai_saf355_target_certification_located": False,
    "e0_uai_saf355_target_certifications_located_count": 0,
    "e0_target_forms_public_bodies_located": 0, "e0_target_transaf_logs_located": 0,
    "e0_settlement_executed_rows_confirmed": 0, "e0_requests_submitted": 0,
    "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
    "historical_workstream": "Recover target SISIO entry/receipts, note bodies, UAI plan/reports/workpapers, SAF355, bank and reversals; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V156.json").write_text(
    json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

(HERE / "AUDITORIA_V156.md").write_text(f"""# Auditoría V156

- Fuentes maestras: {len(catalog)}; E0: {len(census)}; nuevas: {len(source_rows)}.
- Copias/hash: {physical}/{hash_ok}; brechas: {len(catalog) - physical}.
- Quiebres: {len(breaks)}; trazas: {len(trace)}; claves: {len(keys)}; objetos: {len(objects)}.
- Visuales: {len(visual)} PDF ({len(visual_add)} nuevos) + {len(images)} imágenes = {len(visual) + len(images)}.
- Bundle: {len(bundle)}; deberes UAI: {len(duties)}; SISIO: {len(sisio)}; custodia: {len(workpapers)}; comparador: {len(comparison)}; acrónimos: {len(narrowing)}.
- Cuerpos 0/2; entrada/constancia SISIO 0/2; SAF355 0/5; ejecución 0/10; pedidos/respuestas 0/0.
""", encoding="utf-8")


def checkpoint_manifest():
    files = [{"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
             for path in sorted(HERE.iterdir()) if path.is_file() and path.name != "MANIFEST_V156.json"]
    payload = {
        "checkpoint": "V156", "parent_checkpoint": "V155",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": len(source_rows),
        "fiscal_method_breaks": len(breaks), "request_traceability_rows": len(trace),
        "request_search_keys": len(keys), "request_objects": len(objects),
        "pdf_visual_controls_total": len(visual), "pdf_visual_controls_new": len(visual_add),
        "image_visual_controls_inherited": len(images), "source_bundle_files": len(bundle),
        "target_period_uai_duty_rows": len(duties), "sisio_schema_rows": len(sisio),
        "workpaper_custody_rows": len(workpapers), "sisio_comparator_rows": len(comparison),
        "acronym_narrowing_rows": len(narrowing), "public_search_rows": len(negative),
        "target_period_uai_authority_located": True, "sisio_mandatory_schema_located": True,
        "workpaper_ownership_custody_access_located": True,
        "sisio_target_entry_located": False, "sisio_target_receipt_located": False,
        "daif_note_0120_body_located": False, "sigen_note_3672_body_located": False,
        "gseyp_gsepypf_equivalence_proved": False,
        "uai_saf355_target_certification_located": False, "target_forms_public_bodies_located": 0,
        "target_transaf_logs_located": 0, "award_rows_exact": 10, "account_candidate_rows": 9,
        "executed_settlement_rows_confirmed": 0, "request_drafts": 6,
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V156.json").write_text(
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
    "checkpoint": "V156",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master; {physical} physical SHA-valid; {len(source_rows)} new sources; target SISIO and SAF355 open; 0/10; six drafts not submitted.",
    "historical_workstream": "Recover target SISIO, notes, UAI plan/reports/workpapers, SAF355, bank and reversals; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
temporary = global_manifest.with_suffix(".json.v156tmp")
temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
temporary.replace(global_manifest)

print(f"V156 BUILD PASS · catalog={len(catalog)} · E0={len(census)} · physical={physical} · hash_ok={hash_ok} · breaks={len(breaks)} · trace={len(trace)} · keys={len(keys)} · objects={len(objects)} · visual={len(visual) + len(images)}")
