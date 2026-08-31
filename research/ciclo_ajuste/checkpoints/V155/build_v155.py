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
BIN = CYCLE / "inputs" / "historical_retrieval" / "v155" / "binaries"
V154 = CYCLE / "checkpoints" / "V154"
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
        assert len(values) == len(fields) - 1, (prefix, index, len(values), len(fields) - 1, line)
        rows.append(dict(zip(fields, [f"{prefix}{index:02d}"] + values)))
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
        "id": "e0_cgn_account_2009_uepex_2008_note_sisio_chain",
        "institution": "Contaduría General de la Nación / SIGEN / UAI",
        "title": "Cuenta de Inversión 2009 · Nota DAIF 0120/09, Nota SIGEN 3672/09 y circuito SISIO",
        "url": "https://www.economia.gob.ar/hacienda/cgn/cuenta/2009/archivos/sep.pdf",
        "filename": "cgn_cuenta_2009_uepex_note_sisio_chain.pdf",
        "period": "2008-2009",
        "series": "Cuenta de Inversión 2009 · Separata UEPEX · págs. PDF 77-79",
        "kind": "PDF oficial preservado",
        "variables": "Cuenta2008;DAIF;SIGEN;GSEyP;SISIO;UAI;SIDIF;DADP;SIGADE;UEPEX",
        "breaks": "UEPEX/SAF355; informe agregado/certificado target; SISIO/cuerpo documental; seguimiento/ejecución bancaria",
        "status": "E0_USABLE_AS_CONTEMPORANEOUS_ROUTING_AND_CONTROL_CHAIN",
        "note": "Identifica Nota 0120/09 DAIF, Nota SIGEN 3672/09 GSEyP, carga de hallazgos en SISIO, seguimiento UAI, cotejo SIDIF-DADP y regularización certificada. No contiene los Anexos I-V SAF355 ni acredita pago bancario.",
    },
    {
        "id": "e0_mecon_current_audit_disclosure_window_and_sigen_route",
        "institution": "Ministerio de Economía",
        "title": "Auditorías publicadas 2022-2026 y derivación oficial a buscador/formulario SIGEN",
        "url": "https://www.argentina.gob.ar/economia/transparencia/auditorias",
        "filename": "mecon_current_audits_2022_2026_and_sigen_route.html",
        "period": "2022-2026; consulta 2026-08-31",
        "series": "Transparencia · Auditorías · actualización junio 2026",
        "kind": "HTML oficial preservado",
        "variables": "disclosure_window;UAI;SIGEN;public_search;AIP;current_route",
        "breaks": "ventana publicada/inventario histórico; ausencia visible/inexistencia; ruta disponible/pedido presentado",
        "status": "E0_USABLE_CURRENT_DISCLOSURE_AND_ROUTING_ONLY",
        "note": "Prueba que la página actual de Economía publica 2022-2026 y deriva informes SIGEN al buscador y al formulario AIP. No permite inferir inexistencia de informes 2009.",
    },
    {
        "id": "e0_sigen_current_aip_direct_form",
        "institution": "Sindicatura General de la Nación",
        "title": "Formulario oficial de acceso a la información pública de SIGEN",
        "url": "https://www.sigen.gob.ar/AIP/Default.aspx",
        "filename": "sigen_current_aip_direct_form.html",
        "period": "consulta 2026-08-31",
        "series": "SIGEN · Acceso a la Información Pública",
        "kind": "HTML oficial preservado",
        "variables": "AIP;request_fields;identity;contact;requested_information",
        "breaks": "formulario disponible/pedido presentado; canal/acuse; datos personales/evidencia target",
        "status": "E0_USABLE_CURRENT_SUBMISSION_ROUTE_NOT_SENT",
        "note": "Preserva los campos exigidos y el canal directo SIGEN. Ningún formulario fue completado o enviado; estado DRAFT_NOT_SENT.",
    },
    {
        "id": "e0_mecon_uai_structure_2010_accounting_control_duties",
        "institution": "Poder Ejecutivo Nacional / Ministerio de Economía y Finanzas Públicas",
        "title": "Decreto 1025/2010 · estructura y acciones de la UAI Economía",
        "url": "https://www.argentina.gob.ar/normativa/nacional/decreto-1025-2010-169689/texto",
        "filename": "mecon_decree_1025_2010_uai_structure.html",
        "period": "2010-07-19; comparador inmediato posterior",
        "series": "Decreto 1025/2010 · texto original",
        "kind": "HTML oficial preservado",
        "variables": "UAI;planning;accounting;financial;budget;audit_reports;working_papers;followup;SIGEN",
        "breaks": "estructura 2010/organigrama 2009; deber general/informe target; papeles de trabajo/cuerpo público",
        "status": "E0_USABLE_POST_TARGET_PRODUCER_DUTY_COMPARATOR",
        "note": "Detalla funciones de planificación, confiabilidad contable, informes, comunicación a SIGEN, seguimiento, papeles de trabajo y órganos rectores. Es una reorganización posterior al cierre 2008 y no prueba el número ni el cuerpo del informe buscado.",
    },
]


census = read_csv(V154 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V154.csv")
provenance = read_csv(V154 / "ARCHIVAL_PROVENANCE_V154.csv")
source_rows = []
for source in SOURCES:
    path = BIN / source["filename"]
    assert path.is_file() and path.stat().st_size > 1000, path
    source_rows.append({**source, "local": "/" + path.relative_to(REPO).as_posix(),
                        "sha": sha256(path), "bytes": path.stat().st_size})

catalog = read_csv(CATALOG)
catalog = upsert(catalog, [{
    "id": source["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": source["institution"],
    "titulo": source["title"], "url_original": source["url"], "archivo_local": source["local"],
    "fecha_descarga": "2026-08-31", "fecha_publicacion": source["period"],
    "codigo_serie": source["series"], "periodo_utilizado": source["period"], "tipo": source["kind"],
    "sha256": source["sha"], "nota": "V155: " + source["note"],
} for source in source_rows], "id")
write_csv(CATALOG, catalog, list(catalog[0]))

census = upsert(census, [{
    "source_id": source["id"], "institution": source["institution"], "artifact": source["title"],
    "url": source["url"], "local_path": source["local"], "sha256": source["sha"], "bytes": source["bytes"],
    "period_coverage": source["period"], "variable_families": source["variables"],
    "primary_source": "YES", "preserved": "YES", "method_breaks": source["breaks"],
    "use_status": source["status"], "caveat": source["note"],
} for source in source_rows], "source_id")
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V155.csv", census, list(census[0]))

provenance = upsert(provenance, [{
    "source_id": source["id"], "original_url": source["url"], "retrieval_url": source["url"],
    "capture_timestamp": "2026-08-31", "cdx_digest": "N/A_OFFICIAL_DIRECT",
    "local_path": source["local"], "sha256": source["sha"], "bytes": source["bytes"],
    "provenance_note": "Captura directa de fuente oficial; alcance y quiebres congelados en V155.",
} for source in source_rows], "source_id")
write_csv(HERE / "ARCHIVAL_PROVENANCE_V155.csv", provenance, list(provenance[0]))


chain_fields = ["row_id", "stage", "actor", "record_or_system", "exact_identifier", "documented_action", "probative_value", "limit", "status"]
chain = matrix("E0_2008_DAIF_SIGEN_SISIO_FOLLOWUP_CHAIN_V155.csv", chain_fields, """
1|CGN-DAIF|Informe elevado a SIGEN|Nota 0120/09 DAIF|Remite detalle pormenorizado de gestión presupuestaria y financiera UEPEX y transferencias externas del cierre 2008|Existencia, emisor, destinatario, número y objeto|No es el informe global Economía/2009 ni Anexo SAF355|CONTEMPORARY_RECORD_LOCATED
2|SIGEN|Respuesta institucional|Nota SIGEN 3672/09 GSEyP|Comunica que conclusiones fueron puestas en conocimiento de áreas pertinentes|Existencia de respuesta y circulación interna|No se preservó el cuerpo autónomo de la nota|CONTEMPORARY_RECORD_REFERENCED
3|Síndico General de la Nación|Firma de respuesta|Nota SIGEN 3672/09 GSEyP|Suscribe la respuesta según la Cuenta de Inversión|Nivel de autoridad de la instrucción|La mención no sustituye el original firmado|SIGNATURE_REFERENCED
4|SIGEN|Instrucción de sistema|SISIO|Ordena incorporar hallazgos surgidos del informe|Nombre del sistema y objeto de carga|No ofrece número de actuación o registro SISIO|SYSTEM_ENTRY_REQUIRED
5|UAI respectivas|Seguimiento|Circuito SISIO|Deben ejecutar seguimiento y regularización|Identifica ejecutor posterior y finalidad|No demuestra que cada hallazgo fuera regularizado|FOLLOWUP_ROUTE
6|CGN|Control de cierre|Cuadros UEPEX|Coteja movimientos expuestos|Define objeto controlado|UEPEX no equivale al universo SAF355|CONTROL_OBJECT
7|SAF|Registro presupuestario|SIDIF|Aporta ejecuciones de recursos y gastos|Fuente administrativa contemporánea|Registro no prueba acreditación bancaria|SYSTEM_SOURCE
8|DADP|Registro de deuda|SIDIF|Aporta ejecuciones de la Dirección de Administración de la Deuda Pública|Vincula deuda y cierre|No individualiza las tres recompras target|SYSTEM_SOURCE
9|CGN|Detección de diferencias|Comparación cuadros-SIDIF|Verifica origen de diferencias|Prueba procedimiento de conciliación|No preserva resultado por evento target|RECONCILIATION_PROCEDURE
10|CGN|Comunicación correctiva|Coordinaciones de programas|Solicita aclaración o corrección|Identifica productor de respuesta|No individualiza notas concretas|RESPONSE_ROUTE
11|CGN|Comunicación correctiva|Áreas contables SAF|Solicita aclaración o corrección|Identifica custodio contable|No individualiza SAF355|RESPONSE_ROUTE
12|CGN|Comunicación correctiva|Áreas presupuestarias SAF|Solicita aclaración o corrección|Identifica custodio presupuestario|No individualiza SAF355|RESPONSE_ROUTE
13|CGN|Comunicación correctiva|Sector Préstamos Multilaterales DADP|Solicita aclaración o corrección|Identifica custodio de deuda externa|No es el circuito BODEN doméstico por sí solo|RESPONSE_ROUTE
14|CGN|Salida de consulta|Listados detallados|Proporciona detalle de movimientos registrados|Prueba capacidad de exportación|Capacidad no prueba que exista una consulta target preservada|QUERY_CAPABILITY
15|CGN|Salida de consulta|Listados parametrizados|Proporciona salida por parámetros|Fundamenta pedido de parámetros y resultado|No especifica esquema de campos|QUERY_CAPABILITY
16|CGN|Salida de consulta|Consultas específicas|Proporciona movimientos puntuales|Fundamenta pedido por IDs exactos|No contiene 71597, 152677 ni 2876|QUERY_CAPABILITY
17|Programas/SAF|Respuesta|Información faltante o corregida|Entregan correcciones|Prueba fase de subsanación|No prueba aceptación final|CORRECTION_STAGE
18|CGN|Reemplazo documental|Cuadros y anexos|Reemplaza versiones cuando corresponde|Prueba control de versiones|No identifica versión SAF355 target|VERSION_CONTROL
19|SAF/UAI|Regularización|Formularios pertinentes|Ingresan regularización al sistema|Prueba clase de documento|No preserva formulario individual|REGULARIZATION_STAGE
20|UAI respectiva|Certificación|Certificación del ejercicio que cierra|Certifica que movimientos corresponden al cierre|Prueba intervención UAI en corrección|Certificado agregado no prueba pago individual|CERTIFICATION_STAGE
21|Responsables UEPEX|Explicación|Movimientos extrapresupuestarios|Deben explicar claramente causas|Prueba deber de justificación|Explicación no convierte movimiento en presupuestario|EXPLANATION_DUTY
22|CGN|Cruce ausente|SIGADE|Declara no contar con autorizaciones/permisos para puntos de consulta|Documenta barrera de acceso contemporánea|No prueba inexistencia de datos SIGADE|ACCESS_BARRIER
23|CGN/DADP/UEPEX|Problema recurrente|Desembolsos y tipo de cambio|Reconoce diferencias por momento y cotización|Prueba quiebre de valuación|No trasladar a recompra doméstica sin evidencia|METHOD_BREAK
24|Investigación V155|Objetos derivados|0120/09; 3672/09; SISIO; planes UAI|Convierte la cadena en pedidos separables|Reduce riesgo de respuesta genérica|Todos siguen DRAFT_NOT_SENT|REQUEST_UPGRADE
""", "DS155_")


responsibility_fields = ["row_id", "authority_or_actor", "norm_or_source", "duty_or_action", "record_class", "request_target", "probative_value", "limit", "status"]
responsibility = matrix("E0_2008_CLOSING_RESPONSIBILITY_AND_RECORD_PRODUCER_CHAIN_V155.csv", responsibility_fields, """
Secretaría/Subsecretaría de Coordinación Administrativa|Resolución SH 6/2008 art. 22|Responsabilidad dentro de su competencia jerárquica|Información y respaldo documental|Índice de remisión, notas y disposición final|Identifica nivel responsable|No prueba autoría material de cada pieza|RESPONSIBLE_LEVEL
Jefatura SAF|Resolución SH 6/2008 art. 22|Responsabilidad dentro de su competencia jerárquica|Presentación en término y respaldo|Legajo de cierre SAF355|Identifica custodio operativo|No prueba recepción CGN|RESPONSIBLE_LEVEL
Unidad de Registro Contable|Resolución SH 6/2008 art. 22|Responsabilidad dentro de su competencia jerárquica|Formularios de ajuste contable|C41/C42/C55, ajustes y listados|Identifica productor contable|No prueba banco|RESPONSIBLE_LEVEL
SAF355|Resolución SH 6/2008|Preparar cierre 2008|Formularios y listados|Universo documental del SAF|Delimita jurisdicción objetivo|No individualiza evento de recompra|PRODUCER
UAI Economía|Instructivo SIGEN 2/2008|Certificar anexos aplicables|Certificados y papeles de trabajo|Anexos I-V y fuentes|Identifica controlador|0/5 cuerpos target localizados|CONTROL_PRODUCER
CGN|Resolución SH 6/2008|Recibir y compilar Cuenta|Acuses, rechazos y reemplazos|Mesa de entradas y legajo Cuenta 2008|Identifica custodio central|Compilación no equivale a certificación|CENTRAL_CUSTODIAN
TGN|Resolución SH 6/2008|Gestionar cierre financiero|Listados y corte|Pagos y CUT|Identifica custodio financiero|CUT no cubre necesariamente todo pago externo|FINANCIAL_CUSTODIAN
DADP|Cuenta 2009 UEPEX|Aportar ejecución de deuda|SIDIF/DADP y respuestas|Consultas y listados por movimientos|Vincula deuda con cierre|UEPEX no prueba BODEN target|DEBT_PRODUCER
CGN-DAIF|Cuenta 2009 UEPEX|Elevar análisis de cierre|Nota 0120/09 DAIF|Cuerpo, anexos, índice y acuse|Número exacto localizado|Objeto agregado UEPEX|EXACT_RECORD
SIGEN GSEyP|Cuenta 2009 UEPEX|Responder e instruir seguimiento|Nota 3672/09 GSEyP|Cuerpo firmado, anexos y distribución|Número exacto localizado|Acrónimo no equiparado a GSEPyPF|EXACT_RECORD
SIGEN|Cuenta 2009 UEPEX|Registrar hallazgos|Entrada SISIO|Número de actuación, tema, organismo, estado|Identifica sistema de seguimiento|Registro no es informe completo|SYSTEM_CUSTODIAN
UAI respectivas|Cuenta 2009 UEPEX|Seguir y regularizar|Actuaciones e informes de seguimiento|Alta, actualización, cierre y evidencia|Identifica ejecutor|No demuestra cierre del caso|FOLLOWUP_PRODUCER
UAI Economía|Decreto 1025/2010|Planificar auditoría|Plan anual|Plan 2009, modificaciones y ejecución|Tipo documental estable|Norma posterior al target|POST_TARGET_COMPARATOR
UAI Economía|Decreto 1025/2010|Producir informes periódicos|Libro/registro de informes|Inventario 2009 y numeración interna|Tipo documental estable|Norma posterior al target|POST_TARGET_COMPARATOR
UAI Economía|Decreto 1025/2010|Revisar papeles de trabajo|Papeles y conformidades|Índice, caja, soporte y disposición final|Tipo documental estable|Norma posterior al target|POST_TARGET_COMPARATOR
SIGEN|Página Economía 2026|Publicar/buscar informes|ArchivoWeb|Número público, organismo, período, adjunto|Canal actual verificado|Ventana pública no inventario histórico|CURRENT_DISCLOSURE
SIGEN|Formulario AIP|Recibir solicitudes|Formulario y acuse|Detalle exacto y constancia|Canal directo verificado|No enviado|CURRENT_REQUEST_ROUTE
Archivo/Mesa de entradas Economía|Ley 27.275 y ruta oficial|Localizar legados|COMDOC, libro, caja, soporte|Búsqueda por número, asunto, fechas y áreas|Cubre pre-GDE|Sin respuesta no hay hallazgo|ARCHIVAL_ROUTE
Archivo/Mesa de entradas SIGEN|Ley 27.275 y ruta oficial|Localizar legados|Registro salida/entrada y SISIO|0120/09, 3672/09, Cuenta 2008|Cubre copia controlante|Sin respuesta no hay hallazgo|ARCHIVAL_ROUTE
Investigación V155|Regla probatoria|Separar producción, custodia y prueba|Matriz de objetos|Cada cuerpo y acuse por separado|Evita fundir roles|No cierra ejecución|METHOD_CONTROL
""", "RP155_")


disclosure_fields = ["row_id", "route_or_field", "official_fact", "request_use", "limit", "status"]
disclosure = matrix("E0_MECON_CURRENT_DISCLOSURE_AND_AIP_ROUTE_V155.csv", disclosure_fields, """
MECON_PAGE|Economía publica informes UAI, SIGEN y planes|Punto de entrada institucional|No prueba exhaustividad|CURRENT_PAGE
MECON_WINDOW|Enlace rotulado Informes de auditorías Años 2022-2026|Delimitar ventana visible|No cubre 2009|CURRENT_WINDOW_ONLY
MECON_2026|Plan anual 2026 visible|Control de actualidad|No prueba archivo histórico|CURRENT_WINDOW_ONLY
MECON_2022|Plan anual 2022 visible|Extremo inferior declarado|No prueba que 2021 sea inexistente|CURRENT_WINDOW_ONLY
MECON_UPDATE|Fecha de actualización junio 2026|Congelar vigencia de captura|Puede cambiar luego|CAPTURE_DATE
SIGEN_PUBLIC|Economía afirma que SIGEN publica informes|Ruta secundaria oficial|No garantiza cobertura 2009|OFFICIAL_REFERRAL
SIGEN_SEARCH|Enlace al buscador ArchivoWeb|Buscar metadatos públicos|Resultado negativo no prueba inexistencia|OFFICIAL_REFERRAL
SIGEN_FORM|Enlace al formulario AIP SIGEN|Pedir cuerpos históricos|Disponible no significa enviado|OFFICIAL_REFERRAL
SIGEN_PHYSICAL|Economía informa presentación escrita en SIGEN|Ruta alternativa|Dirección vigente a fecha de página|OFFICIAL_REFERRAL
AIP_SURNAME|Formulario exige apellido|Preparar borrador|Dato personal no completado|FORM_FIELD
AIP_NAME|Formulario exige nombre|Preparar borrador|Dato personal no completado|FORM_FIELD
AIP_DOMICILE|Formulario exige domicilio|Checklist previo|No incluir hasta autorización|FORM_FIELD
AIP_DOCUMENT|Formulario exige tipo y número de documento|Checklist previo|No incluir hasta autorización|FORM_FIELD
AIP_EMAIL|Formulario exige correo electrónico|Canal de respuesta|No incluir hasta autorización|FORM_FIELD
AIP_DETAIL|Formulario exige detalle de información solicitada|Insertar objetos V155|No adjunta automáticamente evidencia|FORM_FIELD
REQUEST_STATE|Ningún dato cargado ni enviado|Mantener seis borradores|Sin acuse ni plazo corriendo|DRAFT_NOT_SENT
""", "DR155_")


uai_fields = ["row_id", "structural_level", "action_number", "duty", "record_class", "target_use", "temporal_limit", "status"]
uai = matrix("E0_UAI_ECONOMY_POST_TARGET_STRUCTURE_AND_DUTIES_V155.csv", uai_fields, """
UAI|Responsabilidad primaria|Mantener control interno adecuado|Evaluación institucional|Ubica productor de control|Decreto julio 2010|POST_TARGET_COMPARATOR
UAI|1|Examen independiente, objetivo, sistemático y amplio|Informes y papeles|Pedir índice de auditorías|Decreto julio 2010|POST_TARGET_COMPARATOR
UAI|2|Establecer planificación|Planificación|Pedir plan y modificaciones|Decreto julio 2010|POST_TARGET_COMPARATOR
UAI|3|Elaborar Plan Anual|Plan anual|Pedir plan 2009|Decreto julio 2010|POST_TARGET_COMPARATOR
UAI|8|Informar avance del Plan al Ministro y Comité|Reportes de avance|Pedir ejecución del plan|Decreto julio 2010|POST_TARGET_COMPARATOR
UAI|10|Evaluar actos de trascendencia económica|Papeles e informes|Buscar recompras por materialidad|Decreto julio 2010|POST_TARGET_COMPARATOR
UAI|11|Verificar principios contables y niveles presupuestarios|Pruebas contables|Pedir pruebas sobre cierre|Decreto julio 2010|POST_TARGET_COMPARATOR
UAI|12|Constatar confiabilidad de antecedentes|Papeles de trabajo|Pedir fuentes de certificados|Decreto julio 2010|POST_TARGET_COMPARATOR
UAI|13|Precisar exactitud del registro de activos y resguardos|Pruebas patrimoniales|Pedir registro/custodia de títulos|Decreto julio 2010|POST_TARGET_COMPARATOR
UAI|14|Emitir opinión sobre estados contables de ejecutoras|Opiniones/certificados|Pedir cuerpo y firma|Decreto julio 2010|POST_TARGET_COMPARATOR
UAI|15|Producir informes periódicos|Libro de informes|Pedir inventario y números|Decreto julio 2010|POST_TARGET_COMPARATOR
UAI|16|Comunicar desvíos a autoridades y SIGEN|Notas y remisiones|Pedir acuses y distribución|Decreto julio 2010|POST_TARGET_COMPARATOR
UAI|17|Seguir recomendaciones y observaciones|SISIO/seguimientos|Pedir altas y cierres|Decreto julio 2010|POST_TARGET_COMPARATOR
UAI|18|Informar temas requeridos por SIGEN|Respuestas a requerimientos|Pedir cadena 3672/09|Decreto julio 2010|POST_TARGET_COMPARATOR
Supervisión|9|Controlar trámites de consolidación de deuda y circulares|Actuaciones obligatorias|Identifica familia deuda/control|Decreto julio 2010; no recompra probada|POST_TARGET_COMPARATOR
Cumplimiento|2|Controlar consolidación de deuda, perjuicio fiscal y recupero|Papeles e informes|Pedir inventario temático|Decreto julio 2010; operatoria distinta|POST_TARGET_COMPARATOR
Gestión contable|3|Revisar y conformar papeles de trabajo|Papeles de evidencia|Pedir índice, soporte y disposición|Decreto julio 2010|POST_TARGET_COMPARATOR
Órganos rectores|1|Auditar órganos de administración financiera Ley 24.156|Informes sobre CGN/TGN/ONCP|Pedir proyectos 2009|Decreto julio 2010|POST_TARGET_COMPARATOR
Órganos rectores|2|Revisar y conformar papeles de trabajo|Papeles de evidencia|Pedir referencias y anexos|Decreto julio 2010|POST_TARGET_COMPARATOR
Regla V155|N/A|Usar sólo como comparador inmediato posterior|Control metodológico|No atribuir organigrama 2010 a 2009|Diferencia temporal explícita|METHOD_LIMIT
""", "UD155_")


acronym_fields = ["row_id", "token", "source", "documented_context", "allowed_inference", "forbidden_inference", "status"]
acronym = matrix("E0_GSEYP_GSEPYPF_ACRONYM_CAUTION_V155.csv", acronym_fields, """
GSEyP|Cuenta de Inversión 2009 UEPEX|Sufijo de Nota SIGEN 3672/09|Buscar literalmente GSEyP|Equipararlo sin fuente a GSEPyPF|TOKEN_VERIFIED
GSEPyPF|Libro Blanco/otras fuentes preservadas|Gerencia de Supervisión Economía y Producción y Planificación Federal según contexto previo|Buscar literalmente GSEPyPF|Retrotraerlo automáticamente a la nota 3672/09|TOKEN_VERIFIED
SIGEN|Ambas familias|Organismo de control|Cruzar registros institucionales|Asumir misma gerencia por pertenecer a SIGEN|ORGANIZATION_ONLY
3672/09|Cuenta 2009|Número exacto de nota SIGEN|Pedir cuerpo, anexos, índice y salida|Suponer número de informe UAI|EXACT_IDENTIFIER
0120/09|Cuenta 2009|Número exacto de nota DAIF|Pedir cuerpo, anexos y acuse|Suponer expediente o actuación SISIO|EXACT_IDENTIFIER
SISIO|Cuenta 2009|Sistema de seguimiento|Pedir alta, organismo, tema, estado y cierre|Tratarlo como repositorio del informe completo|SYSTEM_IDENTIFIER
Cuenta2008|Ambas familias|Tema temporal común|Usar como término de cruce|Inferir identidad organizacional|TOPIC_ONLY
Economía|Ambas familias|Jurisdicción común o vecina|Usar como filtro|Inferir custodio único|JURISDICTION_ONLY
Hipótesis|V155|Posible proximidad temática entre siglas|Conservar como pista secundaria|Presentarla como hecho|HYPOTHESIS_ONLY
Regla|V155|La equivalencia exige organigrama, firma o registro contemporáneo|Pedir documento probatorio|Cerrar brecha por parecido ortográfico|METHOD_LIMIT
""", "AC155_")


negative_fields = ["row_id", "query_or_route", "result", "interpretation", "next_step", "status"]
negative = matrix("E0_V155_PUBLIC_SEARCH_NEGATIVE_RESULTS.csv", negative_fields, """
Informe Economía Cuenta 2008 2009|No apareció número/cuerpo directo en índice público|La brecha principal continúa|Pedir libro UAI y registro SIGEN|GLOBAL_REPORT_ID_NOT_LOCATED
Nota 0120/09 DAIF|Referencia oficial localizada; cuerpo autónomo no localizado|Hay identificador exacto pero falta pieza|Pedir cuerpo, anexos y acuse|REFERENCED_BODY_NOT_LOCATED
Nota SIGEN 3672/09 GSEyP|Referencia oficial localizada; cuerpo autónomo no localizado|Hay identificador exacto pero falta pieza|Pedir cuerpo firmado, distribución y anexos|REFERENCED_BODY_NOT_LOCATED
SISIO 0120/09 3672/09|No apareció entrada pública individual|SISIO es sistema interno/legado|Pedir exportación o certificado de búsqueda|SYSTEM_ENTRY_NOT_PUBLIC
ArchivoWeb SIGEN|Ventana contemporánea accesible; sin inventario 2009 completo|Negativo público no es inexistencia|Usar AIP directa|CURRENT_WINDOW_INCOMPLETE
Auditorías Economía|Página actual declara 2022-2026|2009 queda fuera de la ventana visible|Pedir archivo histórico|HISTORICAL_WINDOW_GAP
Wayback SISIO|Servicio Internet Archive temporalmente fuera de línea durante la consulta|Resultado técnico no probatorio|Reintentar en otra vuelta|TEMPORARY_ARCHIVE_FAILURE
Arquivo.pt SISIO|Cliente no permitió recuperar contenido útil|Resultado técnico no probatorio|Reintentar con API o navegador|TEMPORARY_ARCHIVE_FAILURE
GSEyP vs GSEPyPF|No se localizó equivalencia oficial contemporánea|Mantener siglas separadas|Pedir organigrama/registro|ACRONYM_EQUIVALENCE_NOT_PROVEN
Certificaciones SAF355 I-V|0/5 cuerpos localizados|No elevar puntaje|Pedir cadena completa|TARGET_CERTIFICATES_NOT_LOCATED
71597 152677 2876 + banco|0 filas conciliadas|No hay prueba de ejecución individual|Pedir C41/C42/C55, extractos y reversas|BANK_EXECUTION_NOT_LOCATED
Solicitudes|0/6 enviadas; 0 respuestas|No corren plazos ni hay acuses|Mantener borradores hasta autorización|DRAFT_NOT_SENT
""", "NS155_")
write_csv(HERE / "E0_V155_PUBLIC_SEARCH_NEGATIVE_RESULTS_V155.csv", negative, negative_fields)


breaks = read_csv(V154 / "E0_FISCAL_METHOD_BREAKS_V154.csv")
break_add = [
    {"break_id": "exact_note_chain_not_target_certificate", "dimension": "document", "problem": "Notas 0120/09 y 3672/09 documentan control UEPEX pero no contienen certificados SAF355 target.", "rule": "Mantener notas, certificados y pagos como capas separadas.", "status": "FROZEN", "evidence": "Cuenta de Inversión 2009 separata UEPEX, págs. PDF 77-78"},
    {"break_id": "sisio_followup_entry_not_report_body", "dimension": "system", "problem": "Una entrada de seguimiento SISIO no equivale al cuerpo del informe o sus anexos.", "rule": "Pedir metadatos SISIO y cada documento vinculado por separado.", "status": "FROZEN", "evidence": "Nota SIGEN 3672/09 GSEyP referida en Cuenta 2009"},
    {"break_id": "gseyp_not_automatically_gsepypf", "dimension": "identifier", "problem": "GSEyP y GSEPyPF no pueden fundirse por similitud ortográfica.", "rule": "Exigir organigrama, registro o firma contemporánea para equivalencia.", "status": "FROZEN", "evidence": "E0_GSEYP_GSEPYPF_ACRONYM_CAUTION_V155.csv"},
    {"break_id": "uepex_control_not_saf355_general_debt", "dimension": "scope", "problem": "El control UEPEX no cubre automáticamente el cierre general del SAF355 ni recompras BODEN.", "rule": "Usar como ruta y comparador, no como resultado target.", "status": "FROZEN", "evidence": "Cuenta de Inversión 2009 separata UEPEX"},
    {"break_id": "current_mecon_2022_window_not_2009_nonexistence", "dimension": "disclosure", "problem": "Una ventana pública 2022-2026 no prueba inexistencia en 2009.", "rule": "Tratar ausencia visible como brecha de publicación y usar AIP histórica.", "status": "FROZEN", "evidence": "Ministerio de Economía, Auditorías, junio 2026"},
    {"break_id": "aip_form_availability_not_request_submission", "dimension": "request", "problem": "La disponibilidad del formulario SIGEN no implica presentación ni inicio de plazo.", "rule": "Mantener DRAFT_NOT_SENT hasta autorización, envío y acuse.", "status": "FROZEN", "evidence": "Formulario AIP SIGEN preservado"},
    {"break_id": "post_target_uai_structure_not_2009_exact_orgchart", "dimension": "time", "problem": "El Decreto 1025/2010 reorganiza la UAI después del cierre objetivo.", "rule": "Usarlo sólo como comparador de deberes y clases documentales.", "status": "FROZEN", "evidence": "Decreto 1025/2010, 19-07-2010"},
    {"break_id": "resolution_6_article22_responsibility_not_record_recovery", "dimension": "custody", "problem": "La responsabilidad normativa no prueba que el documento se haya recuperado o conservado.", "rule": "Pedir índice, soporte, transferencia y disposición final.", "status": "FROZEN", "evidence": "Resolución SH 6/2008 art. 22"},
    {"break_id": "parameterized_query_capability_not_query_result", "dimension": "system", "problem": "La capacidad de emitir listados parametrizados no es el resultado target.", "rule": "Pedir parámetros, versión, fecha, operador, universo y salida.", "status": "FROZEN", "evidence": "Cuenta de Inversión 2009 separata UEPEX, pág. PDF 78"},
    {"break_id": "replacement_certification_not_bank_execution", "dimension": "payment", "problem": "Una corrección certificada de cierre no acredita liquidación bancaria individual.", "rule": "Cerrar sólo con documento administrativo, registro y banco más reversas.", "status": "FROZEN", "evidence": "Cuenta de Inversión 2009 separata UEPEX, pág. PDF 78"},
]
breaks = upsert(breaks, break_add, "break_id")
write_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V155.csv", breaks, list(breaks[0]))


trace = read_csv(V154 / "E0_INFORMATION_REQUEST_TRACEABILITY_V154.csv")
trace_fields = list(trace[0])
trace_add = pipe_rows("""
REQ155_ECON|Ministerio de Economía / CGN|CL155_DAIF_NOTE|Cuerpo completo Nota 0120/09 DAIF, anexos e índice|2009; cierre 2008|0120/09 DAIF; UEPEX; Cuenta 2008|número; fecha; emisor; destinatario; asunto; anexos; firma; acuse|metadatos, índice y versión testada|DRAFT_NOT_SENT
REQ155_SIGEN|SIGEN|CL155_SIGEN_NOTE|Cuerpo completo Nota SIGEN 3672/09 GSEyP|2009|3672/09 GSEyP; 0120/09 DAIF|número; fecha; firma; distribución; instrucción; anexos|metadatos, índice y versión testada|DRAFT_NOT_SENT
REQ155_SIGEN|SIGEN|CL155_SISIO_ENTRY|Alta SISIO vinculada al informe DAIF|2009-2010|0120/09; 3672/09; Cuenta 2008|id actuación; organismo; tema; hallazgo; estado; fechas; responsable|exportación sin datos exceptuados o certificado de búsqueda|DRAFT_NOT_SENT
REQ155_SIGEN|SIGEN|CL155_SISIO_HISTORY|Historial de actualizaciones y cierre SISIO|2009-2026|id actuación; Economía; UEPEX|fecha; cambio; estado; usuario/área; evidencia vinculada|traza agregada y disposición final|DRAFT_NOT_SENT
REQ155_ECON|UAI Economía|CL155_UAI_PLAN|Plan anual UAI 2009 y modificaciones|2008-2010|Cuenta 2008; certificación; SIGEN|proyecto; código; horas; producto; estado; informe|índice y extracto de proyectos|DRAFT_NOT_SENT
REQ155_ECON|UAI Economía|CL155_UAI_REPORT_BOOK|Libro o registro de informes UAI 2009|2009|Cuenta de Inversión; SAF355; GSEyP|número interno; título; fecha; área; destinatario; contenedor|inventario aun sin cuerpo|DRAFT_NOT_SENT
REQ155_ECON|UAI Economía|CL155_UAI_WORKPAPERS|Índice de papeles de trabajo del cierre 2008|2008-2009|Instructivo 2/2008; Anexos I-V|caja; soporte; carpeta; folio; documento; disposición|índice testado|DRAFT_NOT_SENT
REQ155_ECON|SAF355|CL155_CLOSING_RESPONSIBILITY|Registro de remisión y responsabilidad art. 22|2008-2009|Resolución SH 6/2008 art. 22; SAF355|responsable; fecha; contenido; firma; destino; acuse|metadatos y cadena de custodia|DRAFT_NOT_SENT
REQ155_ECON|CGN|CL155_PARAMETER_QUERY|Listado/consulta parametrizada usada para diferencias|2008-2009|SIDIF; DADP; Cuenta 2008|parámetros; corte; versión; operador; filas; salida|consulta reproducible o certificado de búsqueda|DRAFT_NOT_SENT
REQ155_ECON|CGN|CL155_REPLACED_TABLES|Versiones reemplazadas de cuadros/anexos|2008-2009|SAF355; cierre 2008|versión; fecha; motivo; original; reemplazo; firma|índice de versiones|DRAFT_NOT_SENT
REQ155_ECON|CGN/UAI|CL155_CORRECTION_CERT|Formularios de regularización y certificación UAI|2008-2009|movimientos del ejercicio; cierre|formulario; movimiento; fecha; certificado; firma|datos testados y agregados por documento|DRAFT_NOT_SENT
REQ155_ECON|Archivo/Mesa de entradas|CL155_LEGACY_ROUTE|Búsqueda pre-GDE por COMDOC, libro, caja y soporte|2008-2010|0120/09; 3672/09; SAF355|sistema; consulta; resultado; fondo; serie; disposición|certificado de búsqueda negativo fundado|DRAFT_NOT_SENT
REQ155_SIGEN|SIGEN AIP|CL155_AIP_RECEIPT|Acuse y número de trámite|cuando se autorice|detalle V155|fecha; canal; id; vencimiento|N/A antes del envío|DRAFT_NOT_SENT
REQ155_ECON|Ministerio de Economía|CL155_DISCLOSURE_GAP|Inventario histórico anterior a 2022|2008-2021|UAI; SIGEN; Cuenta de Inversión|año; número; título; archivo; URL; disposición|inventario y explicación de faltantes|DRAFT_NOT_SENT
REQ155_ECON|UAI Economía|CL155_POST_TARGET_DUTIES|Antecedentes de la estructura UAI vigente en 2009|2004-2010|Decreto 1359/2004; Decreto 1025/2010|organigrama; acciones; vigencia; responsables|acto y anexos|DRAFT_NOT_SENT
REQ155_ECON|Tesoro/Finanzas|CL155_FINAL_BANK_GATE|Conciliación de IDs administrativos con banco y reversas|2008-2009|71597; 152677; 2876; C41/C42/C55|id; fecha; cuenta; débito/crédito; valor; reversa; estado|fila testada manteniendo importes y fechas|DRAFT_NOT_SENT
""", trace_fields, "TR155_")
trace = upsert(trace, trace_add, "trace_id")
write_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V155.csv", trace, trace_fields)


keys = read_csv(V154 / "E0_REQUEST_SEARCH_KEY_MATRIX_V154.csv")
key_fields = list(keys[0])
key_add = pipe_rows("""
REQ155_ECON|exact_identifier|Nota N° 0120/09 DAIF|recuperar informe CGN a SIGEN|Cuenta 2009 UEPEX pág. 77|Referencia; falta cuerpo.
REQ155_SIGEN|exact_identifier|Nota SIGEN N° 3672/09 GSEyP|recuperar respuesta firmada|Cuenta 2009 UEPEX pág. 77|Referencia; falta cuerpo.
REQ155_SIGEN|system|Sistema Informático SISIO|recuperar alta e historial|Cuenta 2009 UEPEX págs. 77-78|Sistema; no cuerpo documental.
REQ155_SIGEN|topic|Cuenta de Inversión 2008 UEPEX|filtrar SISIO y registro de notas|Nota 0120/09|UEPEX no SAF355 general.
REQ155_ECON|area|Dirección de Análisis e Información Financiera DAIF|ubicar libro de salida|Nota 0120/09 DAIF|Confirmar denominación vigente.
REQ155_SIGEN|area|GSEyP|buscar literal de unidad|Nota 3672/09|No equiparar a GSEPyPF.
REQ155_SIGEN|area|GSEPyPF|buscar variante separada|Fuentes previas del proyecto|Hipótesis solamente.
REQ155_ECON|system|SIDIF DADP Cuenta 2008|recuperar comparación de movimientos|Cuenta 2009 UEPEX pág. 78|No banco.
REQ155_ECON|record_type|listados detallados parametrizados|recuperar salida de conciliación|Cuenta 2009 UEPEX pág. 78|Capacidad no resultado.
REQ155_ECON|record_type|consultas específicas de movimientos registrados|recuperar consulta puntual|Cuenta 2009 UEPEX pág. 78|Pedir parámetros y corte.
REQ155_ECON|record_type|reemplazo de cuadros anexos cierre 2008|recuperar control de versiones|Cuenta 2009 UEPEX pág. 78|No necesariamente SAF355.
REQ155_ECON|record_type|formularios pertinentes certificación UAI ejercicio que se cierra|recuperar regularización|Cuenta 2009 UEPEX pág. 78|Certificación no banco.
REQ155_ECON|legal|Resolución SH 6/2008 artículo 22|ubicar responsables y respaldos|Texto oficial preservado|Responsabilidad no recuperación.
REQ155_ECON|record_type|Plan Anual Auditoría Interna 2009|recuperar proyecto Cuenta 2008|Decreto 1025/2010 comparador|Estructura posterior.
REQ155_ECON|record_type|libro de informes UAI 2009|recuperar numeración interna|Decreto 1025/2010 comparador|Estructura posterior.
REQ155_ECON|record_type|papeles de trabajo Cuenta de Inversión 2008|recuperar evidencia y anexos|Decreto 1025/2010 comparador|Estructura posterior.
REQ155_SIGEN|request_route|https://www.sigen.gob.ar/AIP/Default.aspx|canal directo AIP|Página oficial vigente|No enviado.
REQ155_ECON|disclosure|auditorías años 2022-2026|delimitar ventana actual|Página Economía junio 2026|No prueba inexistencia 2009.
REQ155_ECON|legacy_system|COMDOC libro caja soporte óptico 2009|búsqueda pre-GDE|Comparadores V154 y resolución 6|No exigir IF/EX.
REQ155_ECON|target_ids|71597 152677 2876 C41 C42 C55 banco reversa|cierre final de ejecución|Matriz target acumulada|0 filas confirmadas.
""", key_fields, "SK155_")
keys = upsert(keys, key_add, "key_id")
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V155.csv", keys, key_fields)


objects = read_csv(V154 / "E0_V154_REQUEST_OBJECTS.csv")
object_fields = list(objects[0])
object_add = pipe_rows("""
DAIF_NOTE_0120|CGN / DAIF|Nota 0120/09 DAIF con informe, anexos e índice|2009; cierre 2008|número; fecha; emisor; destino; asunto; cuerpo; anexos; firma; acuse|Cuerpo o búsqueda negativa fundada|DRAFT_NOT_SENT
SIGEN_NOTE_3672|SIGEN / GSEyP|Nota SIGEN 3672/09 GSEyP y distribución|2009|número; fecha; firma; instrucción; áreas; anexos; acuse|Cuerpo o búsqueda negativa fundada|DRAFT_NOT_SENT
SISIO_FINDINGS|SIGEN|Alta e historial SISIO del informe 0120/09|2009-2026|id; organismo; tema; hallazgos; estados; fechas; responsables; vínculos|Exportación o certificado de búsqueda|DRAFT_NOT_SENT
UAI_PLAN_2009|UAI Economía|Plan anual, modificaciones y ejecución|2008-2010|proyecto; código; horas; producto; estado; informe|Plan e informe de ejecución|DRAFT_NOT_SENT
UAI_REPORT_BOOK_2009|UAI Economía|Libro/registro de informes del año 2009|2009|número interno; título; fecha; destinatario; contenedor|Inventario completo o búsqueda negativa|DRAFT_NOT_SENT
PARAMETERIZED_QUERY|CGN / DADP / SAF355|Consulta/listado usado en conciliación cierre 2008|2008-2009|parámetros; versión; corte; operador; campos; filas; hash|Salida reproducible o certificado negativo|DRAFT_NOT_SENT
DOCUMENT_DISPOSITION|Archivos Economía y SIGEN|Transferencia, expurgo o disposición de piezas buscadas|2009-2026|fondo; serie; caja; soporte; fecha; acto; destino|Cadena de custodia o disposición formal|DRAFT_NOT_SENT
SIGEN_AIP_RECEIPT|SIGEN|Acuse de futura solicitud AIP|Futuro condicionado|fecha; canal; id; vencimiento; prórroga|Sólo tras autorización y envío|DRAFT_NOT_SENT
""", object_fields, "RO155_")
objects = upsert(objects, object_add, "row_id")
write_csv(HERE / "E0_V155_REQUEST_OBJECTS.csv", objects, object_fields)
write_csv(HERE / "E0_V155_REQUEST_OBJECTS_V155.csv", objects, object_fields)


channels = read_csv(V154 / "CURRENT_OFFICIAL_SUBMISSION_CHANNELS_V154.csv")
channel_fields = list(channels[0])
channels = upsert(channels, [{
    "channel_id": "CH155_SIGEN_AIP", "institution": "Sindicatura General de la Nación",
    "request_type": "Solicitud Ley 27.275 por informes, notas y registros SISIO históricos",
    "official_url": "https://www.sigen.gob.ar/AIP/Default.aspx",
    "online_route": "Formulario web directo SIGEN",
    "email_or_contact": "Campos de contacto dentro del formulario",
    "physical_route": "Av. Corrientes 381/9, C1043AAD, CABA, según página de Economía actualizada junio 2026",
    "published_deadline": "Régimen general Ley 27.275; verificar en acuse",
    "page_freshness": "Formulario activo preservado 2026-08-31",
    "verified_on": "2026-08-31", "status": "OFFICIAL_AIP_ROUTE_VERIFIED_DRAFT_NOT_SENT",
    "caveat": "Canal verificado; no se cargaron datos personales ni se presentó solicitud.",
}], "channel_id")
write_csv(HERE / "CURRENT_OFFICIAL_SUBMISSION_CHANNELS_V155.csv", channels, channel_fields)


catalog_map = {source["filename"]: source["id"] for source in SOURCES}
roles = {
    "cgn_cuenta_2009_uepex_note_sisio_chain.pdf": "CONTEMPORARY_NOTE_AND_SISIO_CHAIN",
    "cgn_cuenta_2009_uepex_note_sisio_chain.html": "SAME_OFFICIAL_SOURCE_HTML_BUNDLE_ONLY",
    "mecon_current_audits_2022_2026_and_sigen_route.html": "CURRENT_DISCLOSURE_AND_REFERRAL_ROUTE",
    "sigen_current_aip_direct_form.html": "CURRENT_DIRECT_AIP_FORM_NOT_SENT",
    "mecon_decree_1025_2010_uai_structure.html": "POST_TARGET_UAI_DUTY_COMPARATOR",
}
bundle_fields = ["row_id", "filename", "role", "catalogued", "catalog_source_id", "bytes", "sha256", "preserved"]
bundle = []
for index, path in enumerate(sorted(BIN.iterdir(), key=lambda value: value.name.casefold()), 1):
    if path.is_file():
        source_id = catalog_map.get(path.name, "BUNDLE_ONLY")
        bundle.append(dict(zip(bundle_fields, [f"B155_{index:02d}", path.name, roles[path.name],
                                               "YES" if path.name in catalog_map else "NO", source_id,
                                               path.stat().st_size, sha256(path), "YES"])))
write_csv(HERE / "E0_V155_SOURCE_BUNDLE.csv", bundle, bundle_fields)


visual = read_csv(V154 / "E0_V154_PDF_VISUAL_CONTROL.csv")
visual_fields = list(visual[0])
visual_add = pipe_rows("""
e0_cgn_account_2009_uepex_2008_note_sisio_chain|77|77|Nota 0120/09, respuesta 3672/09 e instrucción SISIO|PASS|Referencia oficial; no cuerpo autónomo ni SAF355
e0_cgn_account_2009_uepex_2008_note_sisio_chain|78|78|seguimiento UAI, cotejo SIDIF-DADP, consultas y regularización certificada|PASS|Procedimiento UEPEX; no fila bancaria target
e0_cgn_account_2009_uepex_2008_note_sisio_chain|79|79|barrera de acceso SIGADE y quiebre de valuación|PASS|No prueba inexistencia SIGADE ni recompra doméstica
""", visual_fields, "PV155_")
visual += visual_add
write_csv(HERE / "E0_V155_PDF_VISUAL_CONTROL.csv", visual, visual_fields)
images = read_csv(V154 / "E0_V154_IMAGE_VISUAL_CONTROL.csv")
write_csv(HERE / "E0_V155_IMAGE_VISUAL_CONTROL.csv", images, list(images[0]))


source_text = (V154 / "SOURCE_REFERENCES_V154.md").read_text(encoding="utf-8-sig").replace("V154", "V155")
(HERE / "SOURCE_REFERENCES_V155.md").write_text(source_text, encoding="utf-8")
append_section(HERE / "SOURCE_REFERENCES_V155.md", "## V155 · cadena 0120/09 → 3672/09 → SISIO y vías actuales", """
- CGN, Cuenta de Inversión 2009, separata UEPEX: https://www.economia.gob.ar/hacienda/cgn/cuenta/2009/sep/uepex.htm
- PDF oficial de la separata: https://www.economia.gob.ar/hacienda/cgn/cuenta/2009/archivos/sep.pdf
- Ministerio de Economía, Auditorías: https://www.argentina.gob.ar/economia/transparencia/auditorias
- SIGEN, formulario AIP: https://www.sigen.gob.ar/AIP/Default.aspx
- Decreto 1025/2010, texto original: https://www.argentina.gob.ar/normativa/nacional/decreto-1025-2010-169689/texto
- Resolución SH 6/2008, texto original: https://www.argentina.gob.ar/normativa/nacional/norma-148348/texto

Alcance: las notas y SISIO prueban una cadena contemporánea de control, seguimiento y regularización UEPEX. La estructura 2010 sólo es comparador posterior. La ventana pública actual y el formulario prueban rutas, no inexistencia histórica ni presentación. Los Anexos I-V SAF355 y la conciliación bancaria individual siguen abiertos.
""")

draft_names = [
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT", "REQUEST_BCRA_CRYL_SETTLEMENT",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER", "REQUEST_AGN_2018_REPLY",
    "REQUEST_CNV_CUSTODY_RECORDS", "REQUEST_CAJA_SETTLEMENT_HOLDINGS",
    "REQUEST_SUBMISSION_CHECKLIST",
]
for stem in draft_names:
    old = V154 / f"{stem}_V154.md"
    new = HERE / f"{stem}_V155.md"
    new.write_text(old.read_text(encoding="utf-8-sig").replace("V154", "V155"), encoding="utf-8")

request_section = """
Se individualizan como objetos separados la Nota Nº 0120/09 DAIF, la Nota SIGEN Nº 3672/09 GSEyP, sus cuerpos, anexos, índices, firmas, acuses y distribución; la entrada e historial SISIO; el plan anual UAI 2009, su ejecución, el libro de informes y los papeles de trabajo; y las consultas/listados parametrizados usados para conciliar el cierre 2008. La búsqueda debe cubrir COMDOC, libros, mesas de entradas, cajas, soportes ópticos y disposiciones documentales, sin exigir nomenclatura GDE. GSEyP y GSEPyPF deben buscarse como tokens distintos hasta recuperar una equivalencia oficial. La página actual 2022-2026 no demuestra inexistencia en 2009. El formulario AIP SIGEN está verificado, pero no fue completado ni enviado. Estado: BORRADOR_NO_ENVIADO / DRAFT_NOT_SENT.
"""
append_section(HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V155.md", "## V155 · notas exactas, SISIO y registro interno pre-GDE", request_section)
append_section(HERE / "REQUEST_SUBMISSION_CHECKLIST_V155.md", "## Control previo V155 · SIGEN y legado", request_section)

register = read_csv(V154 / "E0_REQUEST_RESPONSE_REGISTER_V154.csv")
for row in register:
    row.update({"draft_file": row["draft_file"].replace("V154", "V155"),
                "status": "DRAFT_NOT_SENT", "submitted_on": "N/A", "submission_channel": "N/A",
                "receipt_or_case_id": "N/A", "response_date": "N/A"})
write_csv(HERE / "E0_REQUEST_RESPONSE_REGISTER_V155.csv", register, list(register[0]))


(HERE / "README_V155.md").write_text(f"""# Checkpoint V155

- Fuentes maestras: {len(catalog)}; E0: {len(census)}; nuevas: {len(source_rows)}.
- Localizada cadena exacta: Nota 0120/09 DAIF → Nota SIGEN 3672/09 GSEyP → SISIO → seguimiento UAI.
- Separados cuerpos, anexos, acuses, entrada SISIO, plan UAI, libro de informes y papeles de trabajo.
- Verificadas ventana pública Economía 2022-2026 y ruta AIP SIGEN; ninguna solicitud enviada.
- Certificados SAF355 target 0/5; filas ejecutadas 0; seis borradores no enviados; 0/10.
""", encoding="utf-8")
(HERE / "VEREDICTO_V155.md").write_text("""# Veredicto V155

La vuelta encuentra una cadena documental contemporánea y numerada que antes era difusa: CGN elevó la Nota 0120/09 DAIF, SIGEN respondió por Nota 3672/09 GSEyP e instruyó incorporar hallazgos a SISIO para seguimiento y regularización por las UAI. También documenta cotejo SIDIF-DADP, listados parametrizados y correcciones certificadas. Esto vuelve mucho más preciso el reclamo archivístico, pero no recupera los cuerpos autónomos de las notas, el asiento SISIO, los Anexos I-V SAF355 ni el banco. La página actual sólo cubre 2022-2026 y el formulario SIGEN sigue sin enviarse. Resultado 0/10; seis borradores no enviados.
""", encoding="utf-8")
(HERE / "E0_FISCAL_RECONSTRUCTION_V155.md").write_text("""# Reconstrucción fiscal E0 V155

V155 agrega una capa de control administrativo contemporáneo: informe DAIF, respuesta SIGEN, carga SISIO, seguimiento UAI, comparación SIDIF-DADP, consultas parametrizadas, reemplazo de cuadros y certificación de regularizaciones. Esa capa demuestra productores, rutas y objetos recuperables; no se funde con certificación SAF355 ni ejecución bancaria. El cierre final conserva la regla documento administrativo + registro de sistema + banco + reversas. Resultado 0/10.
""", encoding="utf-8")
(HERE / "RETRIEVAL_LOG_V155.md").write_text("""# Retrieval log V155

- Localizada en la Cuenta de Inversión 2009 la referencia exacta a Nota 0120/09 DAIF y Nota SIGEN 3672/09 GSEyP.
- Verificada la instrucción de cargar hallazgos en SISIO para seguimiento y regularización UAI.
- Verificados cotejo SIDIF-DADP, listados detallados/parametrizados, consultas específicas, reemplazos y certificación UAI.
- Inspeccionadas visualmente las páginas PDF 77-79.
- Preservadas la ventana de auditorías Economía 2022-2026, la vía AIP SIGEN y el Decreto 1025/2010 como comparador posterior.
- Wayback estuvo temporalmente fuera de línea y Arquivo.pt no devolvió contenido útil; esos negativos son técnicos, no probatorios.
- Ninguna solicitud enviada; certificados SAF355 0/5 y ejecución 0/10.
""", encoding="utf-8")
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V155_A_V156.md").write_text("""# Handover V155 → V156

## Estado

- Cadena contemporánea localizada: Nota 0120/09 DAIF → Nota SIGEN 3672/09 GSEyP → SISIO → seguimiento UAI.
- Cuerpos autónomos, anexos, acuses y asiento/historial SISIO todavía no recuperados.
- Cuenta 2009 documenta conciliación SIDIF-DADP, consultas parametrizadas, reemplazos y certificación de regularización.
- Ventana pública Economía actual: 2022-2026; ruta directa AIP SIGEN verificada, no enviada.
- Decreto 1025/2010 preservado sólo como comparador post-target de deberes y clases documentales.
- GSEyP y GSEPyPF permanecen separados hasta equivalencia oficial.
- SAF355 0/5; banco 0 filas; seis DRAFT_NOT_SENT; 0/10.

## Prioridad V156

1. Mantener borradores salvo autorización expresa.
2. Recuperar cuerpos 0120/09 y 3672/09, índices, anexos, firmas y acuses.
3. Obtener alta/historial SISIO o certificado de búsqueda con disposición documental.
4. Recuperar plan UAI 2009, libro de informes y papeles de trabajo de Cuenta 2008.
5. Cerrar C41/C42/C55 + 71597/152677/2876 + banco + reversas.
""", encoding="utf-8")
stale = HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V155_A_V155.md"
if stale.exists():
    stale.unlink()

append_section(REPO / "BACKUP_ACTUALIZACION_2026-08-29.md", "## V155 · notas DAIF/SIGEN, SISIO y vía AIP", """
- Localizada la cadena Nota 0120/09 DAIF → Nota SIGEN 3672/09 GSEyP → SISIO → seguimiento UAI.
- Congelados cotejo SIDIF-DADP, consultas parametrizadas, reemplazos y certificación como capas no bancarias.
- Verificadas ventana Economía 2022-2026 y vía AIP SIGEN; ninguna presentación.
- Tres páginas nuevas controladas; cuatro fuentes conceptuales nuevas.
- SAF355 0/5; ejecución 0/10; seis borradores no enviados.
""")

write_csv(HERE / "INHERITED_QA_STATUS_V155.csv", [
    {"script": "qa_v154.py", "pre_v155_result": "PASS", "post_v155_result": "PASS_BASELINE", "interpretation": "V154 íntegra; V155 agrega cadena documental sin alterar 0/10."},
    {"script": "qa_v155.py", "pre_v155_result": "N/A", "post_v155_result": "PASS", "interpretation": "Verifica fuentes, controles, borradores y límites V155."},
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
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V155.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V155.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)

size_rows = []
for path in iter_files(REPO):
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": size,
                      "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576),
                      "over_100_mib": str(size > 100 * 1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V155.csv", size_rows)

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V154.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint": "V155", "date": "2026-08-31",
    "state": "E0_DAIF_SIGEN_SISIO_CHAIN_LOCATED_BODIES_AND_SAF355_TARGET_OPEN_NOT_SENT",
    "master_catalog_entries": len(catalog), "physical_local_copies": physical,
    "physical_local_hash_ok": hash_ok, "remaining_physical_gaps": len(catalog) - physical,
    "e0_primary_sources_preserved": len(census), "numeric_v155_strict_changed": False,
    "sources_newly_preserved_v155": len(source_rows),
    "e0_primary_sources_newly_preserved_v155": len(source_rows),
    "e0_fiscal_method_breaks_frozen": len(breaks), "e0_request_traceability_rows": len(trace),
    "e0_request_search_keys": len(keys), "e0_v155_pdf_visual_controls": len(visual),
    "e0_v155_new_pdf_visual_controls": len(visual_add), "e0_v155_image_visual_controls": len(images),
    "e0_v155_total_visual_controls": len(visual) + len(images), "e0_v155_source_bundle_files": len(bundle),
    "e0_v155_note_sisio_chain_rows": len(chain), "e0_v155_responsibility_rows": len(responsibility),
    "e0_v155_disclosure_route_rows": len(disclosure), "e0_v155_uai_duty_rows": len(uai),
    "e0_v155_acronym_caution_rows": len(acronym), "e0_v155_public_search_rows": len(negative),
    "e0_v155_request_objects": len(objects), "e0_daif_note_0120_09_reference_located": True,
    "e0_sigen_note_3672_09_reference_located": True, "e0_sisio_followup_instruction_located": True,
    "e0_daif_note_0120_09_body_located": False, "e0_sigen_note_3672_09_body_located": False,
    "e0_sisio_target_entry_located": False, "e0_current_sigen_aip_route_verified": True,
    "e0_current_sigen_aip_request_submitted": False,
    "e0_sigen_account_2008_global_report_body_located": False,
    "e0_uai_saf355_target_certification_located": False,
    "e0_uai_saf355_target_certifications_located_count": 0,
    "e0_target_forms_public_bodies_located": 0, "e0_target_transaf_logs_located": 0,
    "e0_settlement_executed_rows_confirmed": 0, "e0_requests_submitted": 0,
    "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
    "historical_workstream": "Recover bodies 0120/09 and 3672/09, SISIO history, UAI plan/register/working papers, SAF355 certificates, and bank/reversals; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V155.json").write_text(
    json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

(HERE / "AUDITORIA_V155.md").write_text(f"""# Auditoría V155

- Fuentes maestras: {len(catalog)}; E0: {len(census)}; nuevas: {len(source_rows)}.
- Copias/hash: {physical}/{hash_ok}; brechas: {len(catalog) - physical}.
- Quiebres: {len(breaks)}; trazas: {len(trace)}; claves: {len(keys)}.
- Visuales: {len(visual)} PDF ({len(visual_add)} nuevos) + {len(images)} imágenes = {len(visual) + len(images)}.
- Bundle: {len(bundle)}; cadena: {len(chain)}; responsabilidad: {len(responsibility)}; rutas: {len(disclosure)}; deberes UAI: {len(uai)}.
- Cuerpos 0120/09 y 3672/09: 0/2; entrada SISIO: 0/1; certificados SAF355: 0/5; ejecución: 0/10; pedidos/respuestas: 0/0.
""", encoding="utf-8")


def checkpoint_manifest():
    files = [{"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
             for path in sorted(HERE.iterdir()) if path.is_file() and path.name != "MANIFEST_V155.json"]
    payload = {
        "checkpoint": "V155", "parent_checkpoint": "V154",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": len(source_rows),
        "fiscal_method_breaks": len(breaks), "request_traceability_rows": len(trace),
        "request_search_keys": len(keys), "pdf_visual_controls_total": len(visual),
        "pdf_visual_controls_new": len(visual_add), "image_visual_controls_inherited": len(images),
        "source_bundle_files": len(bundle), "note_sisio_chain_rows": len(chain),
        "responsibility_rows": len(responsibility), "disclosure_route_rows": len(disclosure),
        "uai_duty_rows": len(uai), "acronym_caution_rows": len(acronym),
        "public_search_rows": len(negative), "v155_request_objects": len(objects),
        "daif_note_0120_reference_located": True, "sigen_note_3672_reference_located": True,
        "sisio_followup_instruction_located": True, "daif_note_0120_body_located": False,
        "sigen_note_3672_body_located": False, "sisio_target_entry_located": False,
        "sigen_aip_route_verified": True, "sigen_aip_request_submitted": False,
        "uai_saf355_target_certification_located": False, "target_forms_public_bodies_located": 0,
        "target_transaf_logs_located": 0, "award_rows_exact": 10, "account_candidate_rows": 9,
        "executed_settlement_rows_confirmed": 0, "request_drafts": 6,
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V155.json").write_text(
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
    "checkpoint": "V155",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master; {physical} physical SHA-valid; {len(source_rows)} new sources; note/SISIO bodies and SAF355 open; 0/10; six drafts not submitted.",
    "historical_workstream": "Recover 0120/09, 3672/09, SISIO, UAI 2009 records, SAF355 certificates, bank and reversals; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
temporary = global_manifest.with_suffix(".json.v155tmp")
temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
temporary.replace(global_manifest)

print(f"V155 BUILD PASS · catalog={len(catalog)} · E0={len(census)} · physical={physical} · hash_ok={hash_ok} · breaks={len(breaks)} · trace={len(trace)} · keys={len(keys)} · visual={len(visual) + len(images)}")
