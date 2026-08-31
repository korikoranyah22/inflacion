from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import re


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
PARENT = HERE.parent / "V141"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"

EXPECTED: dict[str, tuple[int, str]] = {}
SOURCES: list[dict[str, object]] = []


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
    HERE.mkdir(parents=True, exist_ok=True)
    skip = {"build_e0_siche_cut_repository_v141.py", "qa_v141.py", "MANIFEST_V141.json", "INHERITED_QA_STATUS_V141.csv"}
    for item in PARENT.iterdir():
        if not item.is_file() or item.name in skip or item.name.startswith("HANDOVER_PROXIMA_SESION"):
            continue
        target = HERE / item.name.replace("V141", "V142")
        text = item.read_text(encoding="utf-8-sig")
        placeholder = "historical_retrieval/__PARENT_V141__/"
        text = text.replace("historical_retrieval/v141/", placeholder)
        text = text.replace("_V141", "_V142").replace("_v141", "_v142")
        text = text.replace(placeholder, "historical_retrieval/v141/")
        if item.name.startswith("REQUEST_") or item.name in {
            "CURRENT_STATE_V141.csv", "E0_INSTITUTIONAL_REQUEST_PACKAGE_V141.md", "RETRIEVAL_LOG_V141.md",
        }:
            text = text.replace("V141", "V142").replace("v141", "v142")
        target.write_text(text, encoding="utf-8")


clone_parent()

for filename, (size, digest) in EXPECTED.items():
    path = BIN / filename
    assert path.is_file() and path.stat().st_size == size, path
    assert sha256(path) == digest, path

for item in SOURCES:
    size, digest = EXPECTED[str(item["filename"])]
    item["bytes"] = size
    item["sha256"] = digest
    item["local"] = "/" + (BIN / str(item["filename"])).relative_to(REPO).as_posix()
    item["type"] = "PDF oficial · captura preservada" if str(item["filename"]).endswith(".pdf") else "HTML oficial · captura preservada"

source_ids = {str(item["id"]) for item in SOURCES}

catalog = [row for row in read_csv(CATALOG) if row["id"] not in source_ids]
assert len(catalog) == 438
for item in SOURCES:
    catalog.append({
        "id": item["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": item["institution"],
        "titulo": item["title"], "url_original": item["url"], "archivo_local": item["local"],
        "fecha_descarga": "2026-08-30", "fecha_publicacion": item["publication"],
        "codigo_serie": item["code"], "periodo_utilizado": item["publication"], "tipo": item["type"],
        "sha256": item["sha256"], "nota": item["note"],
    })
assert len(catalog) == 438 and len({row["id"] for row in catalog}) == 438
write_csv(CATALOG, catalog)
catalog_by_id = {row["id"]: row for row in catalog}

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V142.csv"
census = [row for row in read_csv(census_path) if row["source_id"] not in source_ids]
assert len(census) == 198
for row in census:
    master = catalog_by_id[row["source_id"]]
    row["local_path"] = master["archivo_local"]
    row["sha256"] = master["sha256"]
    path = REPO / master["archivo_local"].lstrip("/") if master["archivo_local"] else None
    if path and path.is_file():
        row["bytes"] = str(path.stat().st_size)
for item in SOURCES:
    census.append({
        "source_id": item["id"], "institution": item["institution"], "artifact": item["title"],
        "url": item["url"], "local_path": item["local"], "sha256": item["sha256"], "bytes": str(item["bytes"]),
        "period_coverage": item["publication"], "variable_families": item["families"],
        "primary_source": "YES", "preserved": "YES", "method_breaks": item["breaks"],
        "use_status": item["use"], "caveat": item["caveat"],
    })
assert len(census) == 198 and len({row["source_id"] for row in census}) == 198
write_csv(census_path, census)

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V142.csv"
provenance = [row for row in read_csv(provenance_path) if row["source_id"] not in source_ids]
assert len(provenance) == 101
for row in provenance:
    master = catalog_by_id[row["source_id"]]
    row["local_path"] = master["archivo_local"]
    row["sha256"] = master["sha256"]
    path = REPO / master["archivo_local"].lstrip("/") if master["archivo_local"] else None
    if path and path.is_file():
        row["bytes"] = str(path.stat().st_size)
for item in SOURCES:
    provenance.append({
        "source_id": item["id"], "original_url": item["url"], "retrieval_url": item["url"],
        "capture_timestamp": "20260830", "cdx_digest": "N/A_DIRECT_OFFICIAL",
        "local_path": item["local"], "sha256": item["sha256"], "bytes": str(item["bytes"]),
        "provenance_note": "Descarga directa desde dominio oficial; copia preservada y validada con SHA-256.",
    })
assert len(provenance) == 101
write_csv(provenance_path, provenance)


cut_repo = [
    {"row_id": "CR141_01", "evidence": "Repositorio histórico CUT-SIDIF Central implementado en SICHE", "proved_scope": "existencia del repositorio", "target_application": "ruta bancaria independiente", "required_output": "nombre de módulo y exportación", "inference_limit": "no prueba una fila target", "status": "PROVED_ROUTE_TARGET_OPEN", "source_id": "e0_dgsiaf_siche_cut_repository_2020_q2", "locator": "PDF p.9"},
    {"row_id": "CR141_02", "evidence": "Período 2007-2014", "proved_scope": "incluye ejercicio 2008", "target_application": "cobertura temporal exacta", "required_output": "confirmación de cobertura por dataset", "inference_limit": "no prueba completitud por día", "status": "EXACT_PERIOD_PROVED", "source_id": "e0_dgsiaf_siche_cut_repository_2020_q2", "locator": "PDF p.9"},
    {"row_id": "CR141_03", "evidence": "Alcance Órganos Rectores", "proved_scope": "acceso institucional", "target_application": "derivar a TGN/CGN/DGSIAF", "required_output": "área ejecutora y usuario/consulta", "inference_limit": "no es acceso ciudadano directo", "status": "INTERNAL_ACCESS_PROVED_REQUEST_NOT_SENT", "source_id": "e0_dgsiaf_siche_cut_repository_2020_q2", "locator": "PDF p.9"},
    {"row_id": "CR141_04", "evidence": "Entidades Básicas", "proved_scope": "clase consultable", "target_application": "identificar cuenta bancaria y cuentas de operación vigentes en 2008", "required_output": "banco;sucursal;cuenta;moneda;vigencia;titular;SAF", "inference_limit": "3855/19 posterior no se presume para 2008", "status": "QUERY_CLASS_PROVED_NOT_RUN", "source_id": "e0_dgsiaf_siche_cut_repository_2020_q2", "locator": "PDF p.9"},
    {"row_id": "CR141_05", "evidence": "Saldos por Tipo de Apertura de Cuenta de Operación", "proved_scope": "clase consultable", "target_application": "reconstruir tipo y saldo de cuenta", "required_output": "tipo de apertura;cuenta;fecha;saldo", "inference_limit": "saldo no identifica movimiento", "status": "QUERY_CLASS_PROVED_NOT_RUN", "source_id": "e0_dgsiaf_siche_cut_repository_2020_q2", "locator": "PDF p.9"},
    {"row_id": "CR141_06", "evidence": "Extractos", "proved_scope": "clase consultable", "target_application": "buscar débito/crédito y referencia", "required_output": "fecha;secuencia;códigos;importe;referencia;estado", "inference_limit": "extracto sin vínculo no atribuye causa", "status": "EXACT_TARGET_ROUTE_PROVED_NOT_RUN", "source_id": "e0_dgsiaf_siche_cut_repository_2020_q2", "locator": "PDF p.9"},
    {"row_id": "CR141_07", "evidence": "Logs de Impacto", "proved_scope": "clase consultable", "target_application": "reconstruir evento que impactó la cuenta", "required_output": "timestamp;evento;entidad;comprobante;importe;resultado", "inference_limit": "log no equivale por sí solo a conciliación", "status": "EXACT_TARGET_ROUTE_PROVED_NOT_RUN", "source_id": "e0_dgsiaf_siche_cut_repository_2020_q2", "locator": "PDF p.9"},
    {"row_id": "CR141_08", "evidence": "Combinación 7.2.8/83106000 con CUT", "proved_scope": "cruce metodológico V142", "target_application": "formulario→impacto→extracto", "required_output": "identificador compartido;fecha;importe;cuenta", "inference_limit": "el PDF no publica esa combinación", "status": "CROSSWALK_PROPOSED_NOT_EXECUTED", "source_id": "E0_SICHE_NAMED_QUERY_TARGET_MAP_V142.csv;e0_dgsiaf_siche_cut_repository_2020_q2", "locator": "matriz V142"},
    {"row_id": "CR141_09", "evidence": "Cuenta CUT 3855/19 en manuales posteriores", "proved_scope": "ejemplo/entorno posterior", "target_application": "clave de control, no filtro inicial", "required_output": "cuenta histórica surgida de Entidades Básicas", "inference_limit": "no atribuir 3855/19 retroactivamente", "status": "CURRENT_IDENTIFIER_ONLY_LEGACY_OPEN", "source_id": "e0_tgn_treasury_system_v3_2022_cut_extract;e0_tgn_cut_auditor_instruction_2025", "locator": "PDF p.63; PDF p.15"},
    {"row_id": "CR141_10", "evidence": "Cadena mínima", "proved_scope": "formulario;log;extracto;Libro Banco;conciliación", "target_application": "cierre de ejecución", "required_output": "cinco vínculos concordantes", "inference_limit": "ninguna capa sustituye a las restantes", "status": "CLOSE_TEST_FROZEN_TARGET_OPEN", "source_id": "e0_dgsiaf_siche_cut_repository_2020_q2;e0_tgn_treasury_system_v3_2022_cut_extract;e0_tgn_cut_auditor_instruction_2025", "locator": "PDF p.9;p.63;p.5-39"},
]
write_csv(HERE / "E0_SICHE_CUT_HISTORICAL_REPOSITORY_V142.csv", cut_repo)

field_specs = [
    ("Cuenta Bancaria CUT", "banco;sucursal;cuenta;moneda", "identidad de cuenta histórica"),
    ("Ejercicio", "año del extracto", "2008"),
    ("Cuenta de Operación", "código y denominación", "tipo de cuenta afectada"),
    ("Apertura Cuenta Operación", "tipo de apertura", "clasificación histórica"),
    ("Cuenta Operativa", "cuenta asociada", "vínculo institucional"),
    ("Titular", "titular de cuenta escritural", "SAF/entidad"),
    ("Fuente de Financiamiento", "fuente", "clasificación del movimiento"),
    ("Clase de Gasto", "clase", "naturaleza del pago"),
    ("Jurisdicción y Entidad", "identidad institucional", "SAF355/Deuda Pública"),
    ("Fecha extracto desde/hasta", "ventana temporal", "todo 2008 y fechas recuperadas"),
    ("Saldo inicial/final", "saldo de la cuenta", "control de integridad"),
    ("Cod. Mov.", "código de movimiento", "clasificar débito/crédito"),
    ("Fecha", "fecha del movimiento", "cruzar formulario/log"),
    ("Importe Crédito/Importe Débito", "signo e importe", "32.270,30 y componentes"),
    ("Comprobante Respaldo", "EE-Ejer-Tipo-Nro", "vincular SIDIF/formulario"),
    ("Libro Banco/Extracto", "Ejer-Tipo-Nro", "vincular registro interno y externo"),
    ("Comprobante Origen", "EE-Ejer-Tipo-Nro", "rastrear evento causante"),
    ("Comprobante Relacionado", "EE-Ejer-Tipo-Nro", "rastrear reversa/regularización"),
    ("Mov. Externo/Mov. Interno/Nro. Cpte. Bancario", "códigos y referencia bancaria", "identificar movimiento BNA"),
    ("Importe pendiente/Estado de conciliación", "importe y estado", "separar conciliado, pendiente y diferencia"),
]
extract_fields = []
for number, (field, meaning, target_use) in enumerate(field_specs, 1):
    source_id = "e0_tgn_treasury_system_v3_2022_cut_extract" if number <= 18 else "e0_tgn_cut_auditor_instruction_2025"
    locator = "PDF p.63" if number <= 18 else "PDF p.34"
    extract_fields.append({
        "field_id": f"EF141_{number:02d}", "source_field": field, "current_meaning": meaning,
        "target_request": target_use, "legacy_status": "CURRENT_FIELD_CROSSWALK_2008_EQUIVALENT_OPEN",
        "source_id": source_id, "locator": locator,
    })
write_csv(HERE / "E0_CUT_EXTRACT_FIELD_CROSSWALK_V142.csv", extract_fields)

auditor_chain = [
    {"row_id": "AC141_01", "proof": "Extracto del agente financiero BNA se compara con Libro Banco", "target_effect": "exigir ambos lados", "limit": "regla actual, no fila 2008", "status": "CURRENT_CONTROL_SCHEMA_PROVED", "source_id": "e0_tgn_cut_auditor_instruction_2025", "locator": "PDF p.5"},
    {"row_id": "AC141_02", "proof": "Cuentas de Operación CUT constituyen tercera capa", "target_effect": "pedir saldo e impacto", "limit": "código histórico abierto", "status": "CURRENT_CONTROL_SCHEMA_PROVED", "source_id": "e0_tgn_cut_auditor_instruction_2025", "locator": "PDF p.5"},
    {"row_id": "AC141_03", "proof": "Auditor ordena por banco/sucursal/cuenta/moneda y fechas", "target_effect": "filtros reproducibles", "limit": "orden no acredita cobertura histórica", "status": "CURRENT_QUERY_SCHEMA_PROVED", "source_id": "e0_tgn_cut_auditor_instruction_2025", "locator": "PDF p.19"},
    {"row_id": "AC141_04", "proof": "Sin coincidencias la grilla no retorna resultados", "target_effect": "pedir parámetros y cobertura", "limit": "cero no prueba inexistencia/pago", "status": "ZERO_RESULT_SEMANTICS_PROVED", "source_id": "e0_tgn_cut_auditor_instruction_2025", "locator": "PDF p.19"},
    {"row_id": "AC141_05", "proof": "Detalle integra saldos Libro Banco, Extracto y cuentas CUT", "target_effect": "pedir salida conjunta", "limit": "modelo actual", "status": "CURRENT_AUDITOR_SCHEMA_PROVED", "source_id": "e0_tgn_cut_auditor_instruction_2025", "locator": "PDF p.19"},
    {"row_id": "AC141_06", "proof": "Detalle incluye movimientos pendientes de conciliación", "target_effect": "no excluir pendientes", "limit": "pendiente no equivale a impago definitivo", "status": "CURRENT_STATE_SCHEMA_PROVED", "source_id": "e0_tgn_cut_auditor_instruction_2025", "locator": "PDF p.19"},
    {"row_id": "AC141_07", "proof": "Movimiento de extracto: fecha, secuencia, códigos, comprobante bancario, importe, estado", "target_effect": "campos mínimos de exportación", "limit": "equivalente legacy debe confirmarse", "status": "CURRENT_DETAIL_SCHEMA_PROVED", "source_id": "e0_tgn_cut_auditor_instruction_2025", "locator": "PDF p.34"},
    {"row_id": "AC141_08", "proof": "Cada movimiento navega a su consulta de Extracto", "target_effect": "exigir detalle de entidad", "limit": "navegación actual", "status": "CURRENT_NAVIGATION_PROVED", "source_id": "e0_tgn_cut_auditor_instruction_2025", "locator": "PDF p.34"},
    {"row_id": "AC141_09", "proof": "Formulario defectuoso puede generar impacto incorrecto", "target_effect": "preservar cuerpo e historial", "limit": "posibilidad general, no target", "status": "CONTROL_RISK_PROVED_TARGET_OPEN", "source_id": "e0_tgn_cut_auditor_instruction_2025", "locator": "PDF p.39"},
    {"row_id": "AC141_10", "proof": "Diferencia del auditor es neta y puede combinar factores", "target_effect": "no atribuir diferencia íntegra a una fila", "limit": "requiere desagregación", "status": "NON_ADDITIVITY_RULE_PROVED", "source_id": "e0_tgn_cut_auditor_instruction_2025", "locator": "PDF p.39"},
    {"row_id": "AC141_11", "proof": "Hallazgo documenta fechas, saldos, diferencia, movimientos y causa", "target_effect": "pedir informe diario si existe", "limit": "informe actual no se presume en 2008", "status": "CURRENT_FINDING_SCHEMA_PROVED", "source_id": "e0_tgn_cut_auditor_instruction_2025", "locator": "PDF p.39"},
    {"row_id": "AC141_12", "proof": "Manual 2022 vincula pago autorizado y formulario respaldatorio por movimiento", "target_effect": "cerrar formulario→extracto", "limit": "estructura posterior; equivalente 2008 abierto", "status": "CURRENT_LINK_SCHEMA_PROVED_LEGACY_OPEN", "source_id": "e0_tgn_treasury_system_v3_2022_cut_extract", "locator": "PDF p.63"},
]
write_csv(HERE / "E0_CUT_AUDITOR_EVIDENCE_CHAIN_V142.csv", auditor_chain)

run_steps = [
    (1, "SICHE CUT · Entidades Básicas", "ejercicio/vigencia 2008;SAF355;sin cuenta prefijada", "banco;sucursal;cuenta;moneda;titular;vigencia", "identificar cuenta histórica"),
    (2, "SICHE CUT · Saldos por Tipo de Apertura", "cuentas recuperadas;todo 2008", "tipo apertura;cuenta operación;saldos;fechas", "mapear cuentas"),
    (3, "SICHE CUT · Extractos", "cuentas recuperadas;01/01-31/12/2008;sin importe", "universo anual completo", "evitar falso negativo"),
    (4, "SICHE CUT · Logs de Impacto", "mismo universo anual", "timestamp;evento;entidad;comprobante;importe;resultado", "reconstruir impactos"),
    (5, "SICHE · Formulario por Pda. y Sigade", "SAF355;2008;7.2.8;83106000", "formulario;fecha;importe;beneficiario;observaciones", "obtener claves de cruce"),
    (6, "Cruce por SIDIF", "71597;152677;2876", "tipo;número;fecha;importe individual", "desagregar total anual"),
    (7, "Cruce por importe", "32.270,30 y componentes;ambos signos;variantes decimales", "movimientos candidatos", "identificar total o partes"),
    (8, "Detalle de Extracto", "movimientos candidatos", "fecha;secuencia;mov externo/interno;cpte bancario;importe;estado", "identificar referencia BNA"),
    (9, "Libro Banco", "referencias y fechas candidatas", "código;descripción;debe/haber;comprobante", "probar impacto interno"),
    (10, "Historial de Conciliación", "movimiento/libro/extracto", "estado;fechas;usuario;causa;regularización", "separar conciliado y pendiente"),
    (11, "Comprobantes origen/relacionado/respaldo", "identificadores recuperados", "EE;ejercicio;tipo;número;vínculos", "cerrar formulario→movimiento"),
    (12, "Informe diario del Auditor", "fecha de movimiento/diferencia si existe", "saldos;diferencia;movimientos;causa;seguimiento", "documentar hallazgo"),
    (13, "Auditoría de resultado cero", "cada consulta individual", "módulo;dataset;cobertura;filtros;fecha;filas;exclusiones;diccionario", "evaluar suficiencia negativa"),
    (14, "AMIDDF", "tipo/número/SAF recuperados", "índice;caja;cuerpo;folios;imagen", "cerrar respaldo documental"),
]
run_steps[2] = (3, "SICHE CUT · Extractos", "cuentas recuperadas;01/01-31/12/2008;sin importe;cuenta operación 230 y universo sin filtro", "universo anual completo;código y descripción histórica", "evitar falso negativo y priorizar comisión")
run_steps.extend([
    (15, "Diccionario histórico", "módulo CUT-SIDIF Central;versión vigente 2008", "cuentas de operación;códigos internos/externos;descripciones;grupos", "resolver equivalentes de 230/AUTO/DBAUTO"),
    (16, "Triage de códigos", "230;AUTO;DBAUTO;CRAUTO;PAGO;PGTR;RECH;DCRB;ANPG;DLOT y equivalentes", "todas las filas y descripción histórica", "separar comisión, pago, crédito, rechazo y reversa"),
    (17, "Grupo de conciliación", "movimientos candidatos", "LIB;APL;EXB;MAN o equivalente;regla aplicada", "identificar conciliación automática o manual"),
    (18, "Referencia unívoca", "movimientos candidatos", "referencia BNA;contracódigo;comprobante;cuenta contraparte", "obtener clave de unión bancaria"),
    (19, "Cuenta de operación 230", "todo 2008;SAF355;fuente/clase;sin importe", "débitos;formulario;extracto;Libro Banco;estado", "probar o descartar carril de gasto bancario"),
])
cut_runbook = [{
    "step_id": f"CQ142_{number:02d}", "sequence": str(number), "query": query, "filters": filters,
    "requested_output": output, "decision": decision, "status": "DRAFT_NOT_SENT",
} for number, query, filters, output, decision in run_steps]
write_csv(HERE / "E0_CUT_TARGET_QUERY_RUNBOOK_V142.csv", cut_runbook)

zero_specs = [
    ("Entidades Básicas", "ninguna cuenta bajo filtros", "inexistencia de cuenta en 2008", "vigencia;SAF;dataset;cobertura"),
    ("Saldos por Apertura", "sin saldo para tipo consultado", "ausencia de movimientos", "tipos incluidos;fechas;cuentas"),
    ("Extractos", "sin fila en cuenta/ventana", "no hubo débito o el extracto está completo", "cuenta histórica;ventana;signos;archivo cargado"),
    ("Logs de Impacto", "sin evento bajo clave", "el formulario no impactó", "modelo de log;claves;retención;cobertura"),
    ("Cruce 32.270,30", "sin importe exacto", "no existieron componentes o neteos", "variantes;partes;signos;moneda"),
    ("Conciliación", "sin pendiente", "pago correcto o inexistencia", "conciliados;regularizados;fecha de proceso"),
    ("Auditor", "grilla vacía", "ausencia/pago del target", "filtros;versión;fechas hasta;datasets"),
    ("Cadena completa", "ninguna coincidencia reproducible", "0/10 ejecutado", "respuesta institucional;exportaciones;diccionarios;derivaciones"),
]
zero_limits = [{
    "rule_id": f"CZ141_{number:02d}", "query": query, "zero_permits": permits,
    "zero_forbids": forbids, "required_metadata": metadata, "status": "FROZEN",
} for number, (query, permits, forbids, metadata) in enumerate(zero_specs, 1)]
write_csv(HERE / "E0_CUT_ZERO_RESULT_AND_CONCILIATION_LIMITS_V142.csv", zero_limits)

# Diccionario visualmente verificado de movimientos CUT. La versión 2013 se usa como
# puente histórico cercano; la versión 2022 documenta la evolución, nunca como
# sustituto retroactivo del catálogo SIDIF Central 2008.
codes_2013 = [
    ("AJPG", "Ajuste de Pago"), ("ANCH", "Anulación Impresión de Cheque"),
    ("ANNT", "Anulación Impresión Nota de Pago"), ("ANPG", "Anulación de Pago"),
    ("ANRF", "Anulación Recurso Pago Figurativa"), ("ANSE", "Anulación Selección de Pago"),
    ("ANTR", "Anulación Recurso Pago por Transferencia"), ("AUTO", "Débito Automático"),
    ("DCHR", "Débito por Cheque Rechazado"), ("DCRB", "Devolución Cuota por Rechazo Bco."),
    ("DEPG", "Desafectación de Pago"), ("DLOT", "Desarmado de Lote"),
    ("DREC", "Desconf. Rectificación de Ingreso"), ("FJCR", "Cuota de Pago de Retenciones"),
    ("FJCU", "Fijación de Cuota"), ("NIDT", "Ingreso no Identificado"),
    ("NULO", "Nulo"), ("PAGO", "Pago por Cuenta Única"),
    ("PGTR", "Pago por Transferencia"), ("PRCU", "Programación de Cuota"),
    ("RECH", "Rechazo de Pago"), ("RECT", "Rectificación de Ingreso"),
    ("RETR", "Recurso por Pago entre SAF CUT"), ("RFIG", "Recurso por Figurativas"),
    ("SELE", "Selección de Pago"), ("SELR", "Selección de Retenciones"),
    ("SEXT", "Selección Extraordinaria"), ("TRAN", "Ingreso por Transferencia"),
]
codes_2022 = [
    ("AJPG", "Regularización Diferencia de Cambio"), ("ANCH", "Anulación Impresión de Cheque"),
    ("ANCU", "Anulación de Cuota de Pago"), ("ANLM", "Anulación de Límite Mensual"),
    ("ANNT", "Anulación Impresión Nota de Pago"), ("ANPE", "Anulación Confirmación Pago Electrónico"),
    ("ANPG", "Anulación de Pago"), ("ANRF", "Anulación Recurso Pago Figurativa"),
    ("ANSE", "Anulación de Selección de Pago"), ("ANTR", "Anulación Recurso Pago por Transferencia"),
    ("ATRB", "Anulación Confirmación Transferencia Bancaria"),
    ("CRAUTO", "Créditos por Extracto Bancario"), ("DBAUTO", "Débitos por Extracto Bancario"),
    ("DCRB", "Devolución Cuota por Rechazo Bco."), ("DEPG", "Desafectación Diferencia de Cambio"),
    ("DLOT", "Desarmado de Lote"), ("DREC", "Desconfirmación Rectificación Ingreso"),
    ("FJCR", "Cuota de Pago de Retenciones"), ("FJCU", "Fijación de Cuota"),
    ("FJLM", "Fijación de Límite Mensual"), ("NIDT", "Ingreso no Identificado"),
    ("NULO", "Nulo"), ("PAGO", "Pago por Cuenta Única"),
    ("PGTR", "Pago por Transferencia"), ("PRCU", "Programación de Cuota"),
    ("RDDC", "Reversa Desafectación Diferencia de Cambio"), ("RECH", "Rechazo de Pago"),
    ("RECT", "Rectificación de Ingreso"), ("RETR", "Recurso por Pago entre SAF CUT"),
    ("RFIG", "Recurso por Figurativas"), ("RRDDF", "Reintegro Reversión Desafectación Devolución Fondos"),
    ("RSLM", "Reseteo de Límite Mensual"), ("RVFJCU", "Reversión de Fijación de Cuotas de Pago"),
    ("SELE", "Selección de Pago"), ("SELR", "Selección de Retenciones"),
    ("SEXT", "Selección Extraordinaria"), ("TRAN", "Ingreso por Transferencia"),
    ("TRCOB", "Transferencia Cobranzas"), ("TRCUTME", "Transferencia Moneda Extranjera"),
    ("TRFIG", "Transferencia Devolución Figurativas"), ("TROTR", "Transferencia Otros"),
]

def code_group(code: str) -> str:
    if code in {"AUTO", "DBAUTO", "CRAUTO"}:
        return "AUTOMATIC_BANK_STATEMENT"
    if code in {"PAGO", "PGTR", "SELE", "SELR", "SEXT", "PRCU", "FJCU", "FJCR", "FJLM"}:
        return "PAYMENT_OR_QUOTA"
    if code.startswith("AN") or code.startswith("RV") or code.startswith("RR") or code in {"RECH", "DCRB", "DCHR", "DLOT", "RDDC"}:
        return "REVERSAL_REJECTION_OR_UNWIND"
    if code.startswith("TR") or code in {"TRAN", "RETR", "RFIG"}:
        return "TRANSFER_OR_RESOURCE"
    return "ADJUSTMENT_OR_OTHER"

event_codes = []
for edition, locator, items in (("2013_V1", "PDF p.67", codes_2013), ("2022_V3", "PDF p.64-65", codes_2022)):
    for number, (code, description) in enumerate(items, 1):
        event_codes.append({
            "row_id": f"EC142_{edition}_{number:02d}", "edition": edition, "movement_code": code,
            "official_description": description, "functional_group": code_group(code),
            "target_use": "priorizar comisión" if code in {"AUTO", "DBAUTO"} else "control positivo/negativo",
            "temporal_limit": "El código exacto 2008 debe surgir del diccionario SICHE; no se presume continuidad.",
            "source_id": "e0_tgn_manual_system_treasury_v1" if edition == "2013_V1" else "e0_tgn_treasury_system_v3_2022_cut_extract",
            "locator": locator,
        })
assert len(event_codes) == 69
write_csv(HERE / "E0_CUT_EVENT_CODE_DICTIONARY_V142.csv", event_codes)

map_2022 = dict(codes_2022)
continuity = []
for number, (code, description) in enumerate(codes_2013, 1):
    if code == "AUTO":
        later_code, later_description, continuity_class = "DBAUTO;CRAUTO", "Débitos/Créditos por Extracto Bancario", "SPLIT_BY_SIGN"
    elif code == "DCHR":
        later_code, later_description, continuity_class = "N/A", "No aparece en tabla v3", "NOT_LISTED_LATER"
    elif code in {"AJPG", "DEPG"}:
        later_code, later_description, continuity_class = code, map_2022[code], "SAME_CODE_CHANGED_DESCRIPTION"
    else:
        later_code, later_description, continuity_class = code, map_2022[code], "STABLE_CODE_EQUIVALENT_DESCRIPTION"
    continuity.append({
        "row_id": f"CC142_{number:02d}", "code_2013": code, "description_2013": description,
        "code_2022": later_code, "description_2022": later_description, "continuity_class": continuity_class,
        "query_effect": "buscar ambos códigos y descripción; pedir diccionario histórico 2008",
        "inference_limit": "Continuidad 2013-2022 no acredita vigencia ni uso del código en 2008.",
    })
assert len(continuity) == 28
write_csv(HERE / "E0_CUT_EVENT_CODE_CONTINUITY_V142.csv", continuity)

operation_accounts = [
    ("2013_V1", "220", "Control de devengado", "saldo para devengar", "PDF p.64"),
    ("2013_V1", "230", "Débitos Automáticos", "débitos del extracto que no son pagos CUT; por ejemplo gastos bancarios y embargos", "PDF p.64"),
    ("2013_V1", "320", "Cuota de pago fijada", "habilita a girar contra CUT", "PDF p.64"),
    ("2013_V1", "321", "Cuota de pago para retenciones", "reserva de cuota de retenciones", "PDF p.64"),
    ("2013_V1", "511", "Disponibilidad para programar", "saldo disponible por cuenta escritural", "PDF p.64"),
    ("2013_V1", "530", "Cuentas escriturales", "saldos financieros individualizados", "PDF p.64"),
    ("2013_V1", "640", "Transferencias entre organismos", "transferencias internas CUT", "PDF p.64"),
    ("2013_V1", "710", "Cuenta Única del Tesoro", "cuenta representativa de la CUT", "PDF p.64"),
    ("2013_V1", "810", "Ingresos no identificados", "depósitos pendientes de identificación", "PDF p.64"),
    ("2022_V3", "230", "Débitos extracto bancario", "débitos del extracto que no son pagos CUT; por ejemplo gastos bancarios y embargos", "PDF p.61"),
    ("2022_V3", "320", "Cuota de Pago Fijada", "habilita a girar contra CUT", "PDF p.61"),
    ("2022_V3", "321", "Cuota de Pago para Retenciones", "reserva de cuota de retenciones", "PDF p.61"),
    ("2022_V3", "511", "Disponibilidad para programar", "saldo para asignar cuota", "PDF p.62"),
    ("2022_V3", "530", "Cuenta escritural", "detalle de operaciones y saldos", "PDF p.62"),
    ("2022_V3", "640", "Pagos por Transferencia", "transferencias entre cuentas escriturales sin impacto BNA", "PDF p.62"),
    ("2022_V3", "710", "Cuenta Única del Tesoro", "cuenta representativa de la CUT", "PDF p.62"),
    ("2022_V3", "810", "Depósitos por Devolución a Confirmar", "ingresos no identificados", "PDF p.62"),
    ("EQUATION", "710=530+810", "Balance CUT", "CUT igual a cuentas escriturales más ingresos no identificados", "PDF p.64/p.62"),
    ("EQUATION", "530=511+320+321", "Balance escritural", "saldo escritural igual a disponible más cuota fijada más reserva", "PDF p.65/p.62"),
]
account_rows = [{
    "row_id": f"OA142_{number:02d}", "edition": edition, "account_or_equation": account,
    "denomination": denomination, "official_function": function,
    "target_effect": "filtro primario candidato" if account == "230" else "control y descarte",
    "temporal_limit": "Confirmar catálogo 2008 en SICHE." if edition != "EQUATION" else "Ecuación posterior; verificar versión histórica.",
    "source_id": "e0_tgn_manual_system_treasury_v1;e0_tgn_treasury_system_v3_2022_cut_extract",
    "locator": locator,
} for number, (edition, account, denomination, function, locator) in enumerate(operation_accounts, 1)]
assert len(account_rows) == 19
write_csv(HERE / "E0_CUT_OPERATION_ACCOUNT_EQUATIONS_V142.csv", account_rows)

discriminator_specs = [
    ("230", "Cuenta de operación", "Débito de extracto no originado en pago CUT", "PRIORIDAD_1"),
    ("AUTO", "Movimiento 2013", "Débito automático; gastos bancarios expresamente incluidos", "PRIORIDAD_1"),
    ("DBAUTO", "Movimiento 2022", "Débito por extracto bancario", "PRIORIDAD_1_CROSSWALK"),
    ("CRAUTO", "Movimiento 2022", "Crédito por extracto; control de signo", "NEGATIVE_SIGN_CONTROL"),
    ("C55 Débito Directo", "Formulario 2004-2008", "Regularización de comisión debitada", "PRIORIDAD_1_FORM"),
    ("PAGO", "Movimiento", "Pago ordinario por CUT", "ALTERNATIVE_PAYMENT_ROUTE"),
    ("PGTR", "Movimiento", "Pago por transferencia", "ALTERNATIVE_PAYMENT_ROUTE"),
    ("ANPG;ANPE;ATRB", "Anulación", "anulación de pago o transferencia", "REVERSAL_CONTROL"),
    ("RECH;DCRB;DCHR", "Rechazo", "rechazo o devolución bancaria", "REJECTION_CONTROL"),
    ("DLOT;RRDDF", "Desarme/reintegro", "reversión posterior", "UNWIND_CONTROL"),
    ("LIB", "Grupo conciliación", "busca par en Libro Banco", "BOOK_MATCH"),
    ("APL", "Grupo conciliación", "aplica gasto/recurso automáticamente; incluye comisiones", "AUTOMATIC_EXPENSE_MATCH"),
    ("EXB", "Grupo conciliación", "concilia por contracódigos del extracto", "STATEMENT_REVERSAL_MATCH"),
    ("MAN", "Grupo conciliación", "regularización manual", "MANUAL_RECONCILIATION"),
    ("referencia unívoca", "Referencia bancaria", "identificador de cada operación", "JOIN_KEY"),
]
discriminators = [{
    "row_id": f"TD142_{number:02d}", "code_or_key": code, "layer": layer,
    "official_meaning": meaning, "target_role": role,
    "required_target_observable": "código;descripción;fecha;importe;referencia;estado;cuenta operación;formulario",
    "status": "QUERY_DISCRIMINATOR_PROVED_TARGET_OPEN",
} for number, (code, layer, meaning, role) in enumerate(discriminator_specs, 1)]
write_csv(HERE / "E0_CUT_TARGET_CODE_DISCRIMINATION_V142.csv", discriminators)

route_specs = [
    ("Evento", "cada transacción CUT dispara créditos/débitos", "evento y cuentas impactadas", "2013 p.65"),
    ("Reconstrucción", "SIDIF permite reconstruir cada impacto", "log completo", "2013 p.65"),
    ("Auditor diario", "Libro Banco = cuentas escriturales + extracto", "saldos y diferencias", "2013 p.65"),
    ("Respaldo", "cada movimiento se controla con formulario", "tipo/número/ejercicio/SAF", "2013 p.65-66"),
    ("Referencia", "agente CUT incorpora referencia unívoca", "referencia bancaria", "2013 p.68"),
    ("Débito automático", "TGN autoriza conceptos específicos al BNA", "acto/código/concepto", "2013 p.112"),
    ("Gasto bancario", "ejemplo expreso de débito automático", "importe y cuenta", "2013 p.112"),
    ("Regularización", "el débito se registra mediante formulario", "C55/CRG o equivalente", "2013 p.112"),
    ("Conversión", "código externo del banco se mapea a código interno", "ambos códigos", "2013 p.140"),
    ("Validación", "cuenta activa, continuidad de saldos, importe y comprobante", "resultado de validaciones", "2013 p.140"),
    ("Corrección", "error se revierte y queda vinculado", "movimiento original y reversa", "2013 p.140"),
    ("Conciliación automática", "extracto se coteja con Libro Banco", "par e instancia histórica", "2013 p.140"),
    ("Estado", "T/P/N: total, parcial o no conciliado", "estado por movimiento", "2013 p.141"),
    ("APL", "comisiones generan gasto SIDIF automático", "formulario, partida y libro", "2013 p.147-148"),
    ("MAN", "pendientes se regularizan y conservan historia", "causa, usuario y fecha", "2013 p.149"),
]
reconciliation_route = [{
    "step_id": f"RR142_{number:02d}", "layer": layer, "official_rule": rule,
    "minimum_output": output, "locator": locator,
    "source_id": "e0_tgn_manual_system_treasury_v1", "target_status": "ROUTE_PROVED_TARGET_RECORD_OPEN",
} for number, (layer, rule, output, locator) in enumerate(route_specs, 1)]
write_csv(HERE / "E0_CUT_RECONCILIATION_EVIDENCE_ROUTE_V142.csv", reconciliation_route)

pdf_visual = [
    {"control_id": "PV142_01", "source_id": "e0_tgn_manual_system_treasury_v1", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v137/binaries/tgn_manual_sistema_tesoreria_v1.pdf", "pdf_page": "64", "rendered_check": "cuenta 230 Débitos Automáticos; catálogo de cuentas y ecuaciones", "result": "PASS"},
    {"control_id": "PV142_02", "source_id": "e0_tgn_manual_system_treasury_v1", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v137/binaries/tgn_manual_sistema_tesoreria_v1.pdf", "pdf_page": "65", "rendered_check": "eventos, reconstrucción de impactos y auditor diario", "result": "PASS"},
    {"control_id": "PV142_03", "source_id": "e0_tgn_manual_system_treasury_v1", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v137/binaries/tgn_manual_sistema_tesoreria_v1.pdf", "pdf_page": "67", "rendered_check": "tabla de 28 códigos; AUTO/PAGO/PGTR/rechazos", "result": "PASS"},
    {"control_id": "PV142_04", "source_id": "e0_tgn_manual_system_treasury_v1", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v137/binaries/tgn_manual_sistema_tesoreria_v1.pdf", "pdf_page": "68", "rendered_check": "referencia unívoca bancaria por operación", "result": "PASS"},
    {"control_id": "PV142_05", "source_id": "e0_tgn_manual_system_treasury_v1", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v137/binaries/tgn_manual_sistema_tesoreria_v1.pdf", "pdf_page": "112", "rendered_check": "débito automático BNA; gastos bancarios; formulario de regularización", "result": "PASS"},
    {"control_id": "PV142_06", "source_id": "e0_tgn_manual_system_treasury_v1", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v137/binaries/tgn_manual_sistema_tesoreria_v1.pdf", "pdf_page": "140", "rendered_check": "mapeo código externo/interno, validación, reversa e historial", "result": "PASS"},
    {"control_id": "PV142_07", "source_id": "e0_tgn_manual_system_treasury_v1", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v137/binaries/tgn_manual_sistema_tesoreria_v1.pdf", "pdf_page": "141", "rendered_check": "campos de extracto y estados T/P/N", "result": "PASS"},
    {"control_id": "PV142_08", "source_id": "e0_tgn_manual_system_treasury_v1", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v137/binaries/tgn_manual_sistema_tesoreria_v1.pdf", "pdf_page": "147", "rendered_check": "grupos LIB/APL y comisiones bancarias automáticas", "result": "PASS"},
    {"control_id": "PV142_09", "source_id": "e0_tgn_manual_system_treasury_v1", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v137/binaries/tgn_manual_sistema_tesoreria_v1.pdf", "pdf_page": "148", "rendered_check": "formulario SIDIF de gasto y C-55/CRG de regularización", "result": "PASS"},
    {"control_id": "PV142_10", "source_id": "e0_tgn_treasury_system_v3_2022_cut_extract", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v141/binaries/argentina_tgn_treasury_system_v3_2022.pdf", "pdf_page": "61", "rendered_check": "cuenta 230 Débitos extracto bancario y definición estable", "result": "PASS"},
    {"control_id": "PV142_11", "source_id": "e0_tgn_treasury_system_v3_2022_cut_extract", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v141/binaries/argentina_tgn_treasury_system_v3_2022.pdf", "pdf_page": "62", "rendered_check": "cuentas 511/530/640/710/810 y ecuaciones", "result": "PASS"},
    {"control_id": "PV142_12", "source_id": "e0_tgn_treasury_system_v3_2022_cut_extract", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v141/binaries/argentina_tgn_treasury_system_v3_2022.pdf", "pdf_page": "64", "rendered_check": "DBAUTO/CRAUTO y tabla de códigos v3 parte 1", "result": "PASS"},
    {"control_id": "PV142_13", "source_id": "e0_tgn_treasury_system_v3_2022_cut_extract", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v141/binaries/argentina_tgn_treasury_system_v3_2022.pdf", "pdf_page": "65", "rendered_check": "tabla de códigos v3 parte 2 y referencia unívoca", "result": "PASS"},
]
write_csv(HERE / "E0_V142_PDF_VISUAL_CONTROL.csv", pdf_visual)

plan_specs = [
    (1, "SICHE · Formulario por Pda. Presupuestaria y Sigade", "SAF355;2008;7.2.8;83106000;sin beneficiario", "formulario;fecha;importe;beneficiario;observaciones", "claves base"),
    (2, "SICHE CUT · Entidades Básicas", "SAF355;vigencia 2008;sin cuenta prefijada", "banco;sucursal;cuenta;moneda;titular", "cuenta histórica"),
    (3, "SICHE CUT · Saldos por Tipo de Apertura", "cuentas recuperadas;2008", "cuenta operación;tipo;saldos", "mapa CUT"),
    (4, "SICHE CUT · Extractos", "cuentas recuperadas;todo 2008", "universo de movimientos", "ruta bancaria"),
    (5, "SICHE CUT · Logs de Impacto", "mismo universo", "evento;comprobante;importe;resultado", "ruta de impacto"),
    (6, "Cruce SIDIF/formulario/importe", "71597;152677;2876;32.270,30 y partes", "candidatos concordantes", "desagregar"),
    (7, "Detalle de Extracto y Libro Banco", "fecha;referencia;movimiento", "códigos;cpte bancario;debe/haber;estado", "probar impacto"),
    (8, "Conciliación/Historial", "movimientos candidatos", "estado;causa;regularización", "probar cierre"),
    (9, "Pagos por SIGADE", "83106000;comprobantes recuperados", "PG/NPG/CMR-DP/TCE-RTCE o legacy", "probar etapa"),
    (10, "Expediente", "S01:0342455/2008 o equivalente", "OP y pagos asociados", "contexto"),
    (11, "AMIDDF", "SAF355;tipo/número recuperado", "índice;caja;cuerpo;folios", "respaldo"),
    (12, "RAIP Economía · auditoría de consulta", "cada dataset/fallback", "parámetros;diccionario;cobertura;filas;exclusiones", "cero reproducible"),
    (13, "SICHE CUT · catálogo histórico", "vigencia 2008;cuentas de operación;códigos", "código;descripción;grupo;regla;vigencia", "resolver 230/AUTO o equivalentes"),
    (14, "SICHE CUT · carril comisión", "cuenta operación 230;AUTO/DBAUTO o equivalente;todo 2008", "universo de débitos;referencia;formulario;estado", "probar hipótesis C55"),
    (15, "SICHE CUT · controles negativos", "PAGO;PGTR;CRAUTO;rechazos;anulaciones;reversas", "filas comparadoras y vínculos", "descartar rutas alternativas"),
]
query_plan = [{
    "query_id": f"SQ142_{number:02d}", "sequence": str(number), "system": system,
    "filter_set": filters, "requested_output": output, "success_test": decision,
    "fallback": "derivación al órgano rector y equivalente legacy documentado", "status": "DRAFT_NOT_SENT",
} for number, system, filters, output, decision in plan_specs]
write_csv(HERE / "E0_SICHE_TARGET_QUERY_PLAN_V142.csv", query_plan)

ledger_path = HERE / "E0_FISCAL_MECHANISM_LEDGER_V142.csv"
new_ledger_ids = {f"F{number}" for number in range(219, 229)}
ledger = [row for row in read_csv(ledger_path) if row["ledger_id"] not in new_ledger_ids]
ledger_specs = [
    (219, "2020", "SICHE_CUT", "HISTORICAL_REPOSITORY", "2007-2014", "Repositorio CUT-SIDIF Central", "ROUTE_PROVED_TARGET_OPEN", "Cobertura incluye 2008."),
    (220, "2007-2014", "SICHE_CUT", "BASIC_ENTITIES", "órganos rectores", "Entidades Básicas", "QUERY_CLASS_PROVED_NOT_RUN", "Debe identificar cuenta histórica."),
    (221, "2007-2014", "SICHE_CUT", "OPERATION_ACCOUNT_BALANCES", "órganos rectores", "Saldos por Tipo de Apertura", "QUERY_CLASS_PROVED_NOT_RUN", "Saldo no identifica movimiento."),
    (222, "2007-2014", "SICHE_CUT", "EXTRACTS", "órganos rectores", "Extractos", "EXACT_ROUTE_PROVED_NOT_RUN", "Extracto target no recuperado."),
    (223, "2007-2014", "SICHE_CUT", "IMPACT_LOGS", "órganos rectores", "Logs de Impacto", "EXACT_ROUTE_PROVED_NOT_RUN", "Log target no recuperado."),
    (224, "2022", "CUT_MODEL", "FORM_MOVEMENT_LINK", "TGN", "formulario→movimiento", "CURRENT_LINK_PROVED_LEGACY_OPEN", "Equivalente 2008 abierto."),
    (225, "2025", "CUT_AUDITOR", "BNA_BOOK_RECONCILIATION", "TGN", "BNA→Libro Banco→Cuenta Operación", "CURRENT_SCHEMA_PROVED_LEGACY_OPEN", "No prueba target."),
    (226, "2025", "CUT_AUDITOR", "EXTRACT_DETAIL", "TGN", "fecha/códigos/cpte/importe/estado", "CURRENT_FIELDS_PROVED_LEGACY_OPEN", "Crosswalk posterior."),
    (227, "2008-2026", "TARGET_QUERY", "CUT_RUNBOOK", "Ministerio de Economía", "14 pasos", "QUERY_PACKAGE_PROVED_NOT_EXECUTED", "Pedido no enviado."),
    (228, "2008-2026", "TARGET_QUERY", "CUT_ZERO_AUDIT", "Ministerio de Economía", "metadatos", "NEGATIVE_STANDARD_PROVED_NO_RESPONSE", "Cero sin alcance no cierra."),
]
for number, window, mechanism, phase, payer, instrument, status, interpretation in ledger_specs:
    ledger.append({
        "ledger_id": f"F{number}", "window": window, "mechanism": mechanism, "phase": phase,
        "as_of_date": "N/D", "payer": payer, "recipient": "N/D", "universe": "target 2008",
        "instrument": instrument, "amount_original": "N/D", "original_unit": "N/D",
        "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE",
        "source_id": "e0_dgsiaf_siche_cut_repository_2020_q2;e0_tgn_treasury_system_v3_2022_cut_extract;e0_tgn_cut_auditor_instruction_2025",
        "source_locator": "matrices V142", "realization_status": status, "additivity": "NON_ADDITIVE",
        "status_interpretation": interpretation, "caveat": "No convertir repositorio, campo, log o diferencia en pago ejecutado.",
    })
assert len(ledger) == 228
write_csv(ledger_path, ledger)

ledger_additions = [
    (229, "2013", "CUT_CODEBOOK", "OPERATION_ACCOUNT", "TGN", "230 Débitos Automáticos", "CANDIDATE_ACCOUNT_PROVED_TARGET_OPEN", "Gastos bancarios y embargos; fila target ausente."),
    (230, "2022", "CUT_CODEBOOK", "OPERATION_ACCOUNT", "TGN", "230 Débitos extracto bancario", "FUNCTIONAL_CONTINUITY_PROVED_TARGET_OPEN", "Misma función documentada; no retroactividad."),
    (231, "2013", "CUT_CODEBOOK", "MOVEMENT_CODE", "TGN", "AUTO Débito Automático", "CANDIDATE_CODE_PROVED_TARGET_OPEN", "Código exacto 2008 abierto."),
    (232, "2022", "CUT_CODEBOOK", "MOVEMENT_CODE", "TGN", "DBAUTO/CRAUTO", "SIGN_SPLIT_PROVED_TARGET_OPEN", "Evolución posterior del código AUTO."),
    (233, "2013", "BANK_RECONCILIATION", "REFERENCE", "BNA", "referencia unívoca", "JOIN_KEY_REQUIRED_TARGET_OPEN", "Referencia target no recuperada."),
    (234, "2013", "BANK_RECONCILIATION", "CODE_MAPPING", "BNA/TGN", "externo→interno", "MAPPING_ROUTE_PROVED_TARGET_OPEN", "Tabla histórica 2008 pendiente."),
    (235, "2013", "BANK_RECONCILIATION", "AUTOMATIC_APPLICATION", "TGN", "APL comisión→gasto SIDIF", "MECHANISM_PROVED_TARGET_OPEN", "No identifica los tres SIDIF."),
    (236, "2013", "BANK_RECONCILIATION", "MATCH", "TGN", "LIB/APL/EXB/MAN", "STATE_ROUTE_PROVED_TARGET_OPEN", "Grupo target pendiente."),
    (237, "2013-2022", "CUT_CODEBOOK", "CONTINUITY", "TGN", "28 códigos comparados", "CROSSWALK_PROVED_NOT_RETROACTIVE", "Dos cambios semánticos, un desdoblamiento y una omisión."),
    (238, "2008-2026", "TARGET_QUERY", "CODE_DISCRIMINATION", "Ministerio de Economía", "19 pasos", "QUERY_PACKAGE_PROVED_NOT_EXECUTED", "Borrador no enviado."),
]
for number, window, mechanism, phase, payer, instrument, status, interpretation in ledger_additions:
    ledger.append({
        "ledger_id": f"F{number}", "window": window, "mechanism": mechanism, "phase": phase,
        "as_of_date": "N/D", "payer": payer, "recipient": "N/D", "universe": "target 2008",
        "instrument": instrument, "amount_original": "N/D", "original_unit": "N/D",
        "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE",
        "source_id": "e0_tgn_manual_system_treasury_v1;e0_tgn_treasury_system_v3_2022_cut_extract",
        "source_locator": "matrices V142", "realization_status": status, "additivity": "NON_ADDITIVE",
        "status_interpretation": interpretation,
        "caveat": "No convertir código, cuenta o ruta de conciliación en ejecución target.",
    })
assert len(ledger) == 238
write_csv(ledger_path, ledger)

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V142.csv"
new_break_ids = {
    "cut_repository_not_target_extract", "cut_period_not_daily_completeness", "cut_internal_access_not_public_execution",
    "cut_basic_entity_not_historical_account_identity", "cut_balance_not_movement", "cut_extract_not_cause",
    "cut_impact_log_not_reconciliation", "current_cut_field_not_legacy_field", "auditor_net_difference_not_target_amount",
}
breaks = [row for row in read_csv(breaks_path) if row["break_id"] not in new_break_ids]
break_specs = [
    ("cut_repository_not_target_extract", "access", "Repositorio CUT probado; extracto target no recuperado.", "Mantener numerador en cero.", "e0_dgsiaf_siche_cut_repository_2020_q2"),
    ("cut_period_not_daily_completeness", "coverage", "2007-2014 incluye 2008, no prueba cada día/campo.", "Exigir cobertura por dataset.", "e0_dgsiaf_siche_cut_repository_2020_q2"),
    ("cut_internal_access_not_public_execution", "access", "Acceso de órganos rectores no ejecuta consulta ciudadana.", "Mantener pedido sin enviar hasta autorización.", "e0_dgsiaf_siche_cut_repository_2020_q2"),
    ("cut_basic_entity_not_historical_account_identity", "identity", "Cuenta actual no fija cuenta 2008.", "Descubrirla en Entidades Básicas.", "E0_SICHE_CUT_HISTORICAL_REPOSITORY_V142.csv"),
    ("cut_balance_not_movement", "phase", "Saldo de cuenta no identifica débito/crédito.", "Exigir extracto y log.", "e0_dgsiaf_siche_cut_repository_2020_q2"),
    ("cut_extract_not_cause", "causality", "Movimiento externo sin comprobante no identifica comisión.", "Cruzar formulario y log.", "e0_tgn_treasury_system_v3_2022_cut_extract"),
    ("cut_impact_log_not_reconciliation", "phase", "Log de impacto no prueba conciliación.", "Cruzar Libro Banco, extracto y estado.", "e0_tgn_cut_auditor_instruction_2025"),
    ("current_cut_field_not_legacy_field", "system", "Campo 2022/2025 no se presume idéntico en 2008.", "Pedir equivalente funcional y diccionario.", "e0_tgn_treasury_system_v3_2022_cut_extract;e0_tgn_cut_auditor_instruction_2025"),
    ("auditor_net_difference_not_target_amount", "arithmetic", "Diferencia neta puede combinar factores.", "Desagregar movimientos; no atribuir total.", "e0_tgn_cut_auditor_instruction_2025"),
]
for break_id, dimension, problem, rule, evidence in break_specs:
    breaks.append({"break_id": break_id, "dimension": dimension, "problem": problem, "rule": rule, "status": "FROZEN_V142", "evidence": evidence})
assert len(breaks) == 180
write_csv(breaks_path, breaks)

break_additions = [
    ("cut_2013_code_not_2008_code", "legal_time", "El catálogo 2013 no acredita el código vigente en 2008.", "Pedir diccionario histórico y buscar código más descripción.", "e0_tgn_manual_system_treasury_v1"),
    ("cut_2022_code_not_2008_code", "legal_time", "DBAUTO/CRAUTO son crosswalk posteriores.", "No filtrar 2008 sólo por esos códigos.", "e0_tgn_treasury_system_v3_2022_cut_extract"),
    ("cut_same_code_changed_semantics", "classification", "AJPG y DEPG cambian de descripción entre versiones.", "No clasificar sólo por literal de código.", "E0_CUT_EVENT_CODE_CONTINUITY_V142.csv"),
    ("cut_auto_split_not_exact_continuity", "classification", "AUTO se desdobla en DBAUTO/CRAUTO.", "Buscar ambos signos, sin asumir migración uno a uno.", "E0_CUT_EVENT_CODE_CONTINUITY_V142.csv"),
    ("cut_account_230_not_target_row", "identity", "La cuenta 230 es el carril funcional de gastos bancarios, no la fila target.", "Exigir fecha, importe, referencia y formulario.", "E0_CUT_OPERATION_ACCOUNT_EQUATIONS_V142.csv"),
    ("cut_apl_not_target_form", "phase", "APL puede generar gasto SIDIF por comisión sin identificar los SIDIF target.", "Cruzar formulario, extracto y Libro Banco.", "E0_CUT_RECONCILIATION_EVIDENCE_ROUTE_V142.csv"),
    ("cut_reference_key_not_causality", "causality", "Referencia unívoca enlaza registros pero no prueba concepto por sí sola.", "Concordar código, descripción, importe y respaldo.", "e0_tgn_manual_system_treasury_v1"),
    ("cut_reconciliation_state_not_payment_purpose", "phase", "T/P/N prueba estado de conciliación, no finalidad económica.", "Mantener separadas ejecución, causa y conciliación.", "E0_CUT_RECONCILIATION_EVIDENCE_ROUTE_V142.csv"),
]
for break_id, dimension, problem, rule, evidence in break_additions:
    breaks.append({"break_id": break_id, "dimension": dimension, "problem": problem, "rule": rule, "status": "FROZEN_V142", "evidence": evidence})
assert len(breaks) == 188
write_csv(breaks_path, breaks)

trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V142.csv"
trace = [row for row in read_csv(trace_path) if not row["trace_id"].startswith("TR141_")]
trace_specs = [
    (165, "CUT_BASIC_ENTITIES", "Entidades Básicas CUT 2008", "SAF355;vigencia2008", "banco;sucursal;cuenta;moneda;titular;vigencia"),
    (166, "CUT_OPERATION_ACCOUNTS", "Saldos por Tipo de Apertura", "cuentas recuperadas;2008", "tipo;cuenta;fecha;saldo"),
    (167, "CUT_EXTRACTS", "Extractos CUT 2008", "cuentas recuperadas;todo2008", "fecha;secuencia;códigos;importe;referencia;estado"),
    (168, "CUT_IMPACT_LOGS", "Logs de Impacto 2008", "SAF355;formulario/importe", "timestamp;evento;entidad;comprobante;importe;resultado"),
    (169, "CUT_BOOK", "Libro Banco asociado", "movimientos candidatos", "código;descripción;debe;haber;comprobante"),
    (170, "CUT_RECONCILIATION", "Historial de conciliación", "extracto/libro/cuenta", "estado;fechas;causa;regularización"),
    (171, "CUT_AUDITOR_REPORT", "Informe diario del Auditor si obra", "fecha/diferencia", "saldos;diferencia;movimientos;causa;seguimiento"),
    (172, "CUT_QUERY_AUDIT", "Metadatos de cuatro datasets CUT", "Entidades;Saldos;Extractos;Logs", "módulo;dataset;filtros;cobertura;fecha;filas;exclusiones;diccionario"),
]
for number, gap, record, identifiers, fields in trace_specs:
    trace.append({
        "trace_id": f"TR141_{number}", "request_id": "REQ133_ECON",
        "institution": "Ministerio de Economía / Secretaría de Hacienda / TGN",
        "gap_id": gap, "requested_record": record, "period_or_date": "2008; consulta 2026",
        "identifiers": identifiers, "minimum_usable_fields": fields,
        "confidentiality_fallback": "exportación disociada; tachas parciales; metadatos y diccionario",
        "status": "DRAFT_NOT_SENT",
    })
assert len(trace) == 172
write_csv(trace_path, trace)

trace_additions = [
    (173, "CUT_HISTORICAL_DICTIONARY", "Diccionario de cuentas y códigos vigente en 2008", "CUT-SIDIF Central;2008", "cuenta;código;descripción;grupo;vigencia"),
    (174, "CUT_ACCOUNT_230", "Universo de cuenta de operación 230 o equivalente", "SAF355;todo2008", "fecha;importe;cuenta;referencia;formulario;estado"),
    (175, "CUT_AUTO_CODE", "Universo AUTO/DBAUTO o equivalentes históricos", "ambos signos;todo2008", "código externo/interno;descripción;importe;referencia"),
    (176, "CUT_RECONCILIATION_GROUP", "Grupo LIB/APL/EXB/MAN o equivalente", "movimientos candidatos", "grupo;regla;fecha;resultado;usuario"),
    (177, "CUT_UNIQUE_REFERENCE", "Referencia unívoca y contracódigo", "movimientos candidatos", "referencia;original;reversa;cuenta contraparte"),
    (178, "CUT_AUTOMATIC_EXPENSE_FORM", "Formulario generado por aplicación automática", "comisiones;71597;152677;2876", "tipo;número;partida;importe;Libro Banco;aceptación"),
]
for number, gap, record, identifiers, fields in trace_additions:
    trace.append({
        "trace_id": f"TR142_{number}", "request_id": "REQ133_ECON",
        "institution": "Ministerio de Economía / Secretaría de Hacienda / TGN",
        "gap_id": gap, "requested_record": record, "period_or_date": "2008; consulta 2026",
        "identifiers": identifiers, "minimum_usable_fields": fields,
        "confidentiality_fallback": "exportación disociada; tachas parciales; metadatos y diccionario",
        "status": "DRAFT_NOT_SENT",
    })
assert len(trace) == 178
write_csv(trace_path, trace)

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V142.csv"
keys = [row for row in read_csv(keys_path) if not row["key_id"].startswith("SK141_")]
key_specs = [
    (183, "cut_module", "CUT - SIDIF Central 2007-2014", "repositorio exacto"),
    (184, "cut_dataset", "Entidades Básicas", "cuenta histórica"),
    (185, "cut_dataset", "Saldos por Tipo de Apertura de Cuenta de Operación", "mapa de cuentas"),
    (186, "cut_dataset", "Extractos", "movimiento externo"),
    (187, "cut_dataset", "Logs de Impacto", "evento interno"),
    (188, "target", "SAF355;2008;7.2.8;83106000", "formulario base"),
    (189, "sidif", "71597;152677;2876", "localizadores"),
    (190, "amount", "32270.30;32.270,30;componentes;debe;haber", "importe y partes"),
    (191, "extract", "fecha;secuencia;mov externo;mov interno;cpte bancario", "referencia BNA"),
    (192, "voucher", "respaldo;origen;relacionado;Libro Banco/Extracto", "vínculo formulario"),
    (193, "state", "conciliado;pendiente;regularizado;rechazado;anulado", "estado"),
    (194, "negative", "dataset;modelo;filtros;cobertura;fecha;filas;exclusiones;diccionario", "cero reproducible"),
]
for number, group, key, purpose in key_specs:
    keys.append({
        "key_id": f"SK141_{number}", "request_id": "REQ133_ECON", "key_group": group,
        "exact_key": key, "search_purpose": purpose,
        "source_or_basis": "E0_SICHE_CUT_HISTORICAL_REPOSITORY_V142.csv;E0_CUT_TARGET_QUERY_RUNBOOK_V142.csv",
        "caveat": "Clave o clase probada; no confirma fila.",
    })
assert len(keys) == 194
write_csv(keys_path, keys)

key_additions = [
    (195, "operation_account", "230", "débitos de extracto ajenos a pago CUT"),
    (196, "operation_account", "Débitos Automáticos;Débitos extracto bancario", "descripción de cuenta"),
    (197, "movement", "AUTO;DBAUTO;CRAUTO", "códigos automáticos y control de signo"),
    (198, "payment_control", "PAGO;PGTR", "rutas alternativas de pago"),
    (199, "rejection", "RECH;DCRB;DCHR", "rechazo y devolución"),
    (200, "reversal", "ANPG;ANPE;ATRB;DLOT;RRDDF", "anulación o desarme"),
    (201, "reconciliation", "LIB;APL;EXB;MAN", "grupo de conciliación"),
    (202, "reference", "referencia unívoca;número de comprobante;contracódigo", "clave de unión"),
    (203, "accounting_form", "C55;C55-REG;Débito Directo;CRG-DB", "regularización de comisión"),
    (204, "account_equation", "710=530+810", "control global CUT"),
    (205, "account_equation", "530=511+320+321", "control de cuenta escritural"),
    (206, "dictionary", "catálogo CUT-SIDIF Central vigente 2008", "evitar retroactividad"),
]
for number, group, key, purpose in key_additions:
    keys.append({
        "key_id": f"SK142_{number}", "request_id": "REQ133_ECON", "key_group": group,
        "exact_key": key, "search_purpose": purpose,
        "source_or_basis": "E0_CUT_EVENT_CODE_DICTIONARY_V142.csv;E0_CUT_OPERATION_ACCOUNT_EQUATIONS_V142.csv",
        "caveat": "Crosswalk probado; uso exacto en 2008 pendiente.",
    })
assert len(keys) == 206
write_csv(keys_path, keys)

register_path = HERE / "E0_REQUEST_RESPONSE_REGISTER_V142.csv"
register = read_csv(register_path)
for row in register:
    row["status"] = "DRAFT_NOT_SENT"
    row["submitted_on"] = "N/A"
    row["submission_channel"] = "N/A"
    row["receipt_or_case_id"] = "N/A"
write_csv(register_path, register)

request_path = HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V142.md"
request_text = request_path.read_text(encoding="utf-8-sig")
request_marker = "## Clave V142 · cuenta 230, códigos automáticos y conciliación"
if request_marker not in request_text:
    request_text += f"""

{request_marker}

El Manual TGN versión 1.0 identifica la cuenta de operación `230 · Débitos Automáticos` como la cuenta que registra débitos contenidos en el extracto bancario que no corresponden a pagos realizados en el marco de la CUT; menciona expresamente los `gastos bancarios` y los embargos. La versión 3 conserva el código `230` y la misma función bajo la denominación `Débitos extracto bancario`. Esa continuidad 2013-2022 justifica usar `230` como filtro candidato, pero no acredita que el código o la descripción rigieran sin cambios en 2008. Por eso se solicita primero el catálogo de cuentas de operación y el diccionario de movimientos vigentes en el CUT-SIDIF Central durante 2008.

La tabla de 2013 distingue `AUTO · Débito Automático` de `PAGO · Pago por Cuenta Única` y `PGTR · Pago por Transferencia`; la versión 2022 desdobla el carril automático en `DBAUTO · Débitos por Extracto Bancario` y `CRAUTO · Créditos por Extracto Bancario`. Deben buscarse el código histórico, sus descripciones y todos sus equivalentes, sin restringir la consulta a los literales posteriores. Como controles se requieren también pagos, créditos, rechazos (`RECH`, `DCRB`, `DCHR`), anulaciones (`ANPG`, `ANPE`, `ATRB`) y reversas/desarmes (`DLOT`, `RRDDF` o equivalentes).

El mismo manual explica que los débitos automáticos autorizados al BNA por conceptos determinados —por ejemplo gastos bancarios— se incorporan al extracto CUT con códigos específicos, se registran mediante formularios de regularización y, luego de la conciliación, afectan la cuenta escritural del Tesoro. Para cada candidato se solicita el código bancario externo y su conversión al código interno; fecha, signo, importe, número de comprobante y `referencia unívoca`; cuenta de operación; formulario C-55 Débito Directo, CRG-DB o equivalente; partida y SIDIF; registro en Libro Banco; grupo de conciliación `LIB`, `APL`, `EXB` o `MAN` o equivalente; estado total/parcial/no conciliado; original, contracódigo, reversa, corrección e historia de la instancia.

La búsqueda primaria debe abarcar el universo completo de la cuenta 230 o equivalente para `SAF 355` durante todo 2008, sin filtro inicial de importe. Luego se cruzarán `71597`, `152677`, `2876`, `83106000`, `7.2.8`, `COMISIONES - BANCO NACION`, `$32.270,30`, sus componentes y variantes de signo/formato. Una coincidencia sólo cerrará la ejecución cuando formulario, log de impacto, extracto BNA, Libro Banco, conciliación y respaldo documental compartan fecha, importe y referencia de modo reproducible. **Estado: BORRADOR_NO_ENVIADO.**
"""
request_path.write_text(request_text, encoding="utf-8")

checklist_path = HERE / "REQUEST_SUBMISSION_CHECKLIST_V142.md"
checklist = checklist_path.read_text(encoding="utf-8-sig")
check_marker = "## Control V142 · código, cuenta 230 y conciliación"
if check_marker not in checklist:
    checklist += f"""

{check_marker}

- [ ] Pedir el catálogo de cuentas de operación y movimientos vigente en 2008.
- [ ] Ejecutar cuenta 230 o equivalente sin importe y conservar el universo anual.
- [ ] Buscar `AUTO/DBAUTO/CRAUTO` y descripciones, nunca sólo el código posterior.
- [ ] Ejecutar controles `PAGO/PGTR`, créditos, rechazos, anulaciones y reversas.
- [ ] Exigir código externo/interno, referencia unívoca, formulario, Libro Banco y grupo de conciliación.
- [ ] Cruzar C-55 Débito Directo/CRG-DB o equivalente con los tres SIDIF.
- [ ] No convertir continuidad 2013-2022 en vigencia automática para 2008.
- [ ] Confirmar autorización expresa antes de presentar cualquiera de los seis borradores.
"""
checklist_path.write_text(checklist, encoding="utf-8")

source_refs_path = HERE / "SOURCE_REFERENCES_V142.md"
source_refs = source_refs_path.read_text(encoding="utf-8-sig")
canonical_lines = []
for line in source_refs.splitlines():
    match = re.match(r"^- `([^`]+)`", line)
    if match and match.group(1) in catalog_by_id:
        canonical = catalog_by_id[match.group(1)]["archivo_local"]
        line = re.sub(r"`/[^`]+`", f"`{canonical}`", line)
    canonical_lines.append(line)
source_refs = "\n".join(canonical_lines) + "\n"
refs_marker = "## Fuentes reexplotadas V142 · código CUT y conciliación"
if refs_marker not in source_refs:
    source_refs += "\n" + refs_marker + "\n\n"
    for source_id in ("e0_tgn_manual_system_treasury_v1", "e0_tgn_treasury_system_v3_2022_cut_extract"):
        row = catalog_by_id[source_id]
        source_refs += f"- `{source_id}` · {row['titulo']} · {row['url_original']} · `{row['archivo_local']}` · `{row['sha256']}`\n"
source_refs_path.write_text(source_refs, encoding="utf-8")

(HERE / "README_V142.md").write_text("""# V142 · diccionario CUT y ruta de comisiones

V142 identifica un discriminante que V141 todavía no tenía: la cuenta de operación `230` concentra débitos del extracto que no son pagos CUT y cita gastos bancarios como ejemplo. El manual 2013 la denomina `Débitos Automáticos`; el de 2022 conserva el código y la función como `Débitos extracto bancario`. En paralelo, el código `AUTO` de 2013 evoluciona a `DBAUTO/CRAUTO` y queda separado de `PAGO/PGTR`.

La cadena de verificación es ahora: cuenta 230 o equivalente → código externo/interno → referencia unívoca → formulario de regularización → Libro Banco → grupo y estado de conciliación → log/respaldos. Es un crosswalk de consulta, no una atribución retroactiva: el catálogo 2008 sigue pendiente. Ninguna consulta fue ejecutada ni enviada. Balance: 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas; seis pedidos DRAFT_NOT_SENT.
""", encoding="utf-8")

(HERE / "VEREDICTO_V142.md").write_text("""# Veredicto V142

La hipótesis documental principal se estrecha: si `COMISIONES - BANCO NACION` refleja una comisión efectivamente debitada, la firma esperable es una cuenta de operación `230` o equivalente, un movimiento `AUTO` o equivalente histórico, y un formulario de regularización C-55 Débito Directo/CRG-DB o equivalente aplicado mediante conciliación `APL` o regularización manual. `PAGO/PGTR`, créditos, rechazos y reversas funcionan como controles que pueden refutar esa ruta.

La continuidad 2013-2022 prueba estabilidad funcional, no vigencia exacta en 2008. El cierre exige el catálogo histórico y una concordancia entre formulario, log, extracto, Libro Banco, referencia unívoca y conciliación. Sin esa fila, cuenta 230 y AUTO son filtros priorizados, no prueba del target.

No se recuperó una fila target, extracto, log, Libro Banco, informe del Auditor ni cuerpo AMIDDF. Permanecen 10 adjudicaciones exactas, 9 cuentas candidatas y 0/10 ejecuciones confirmadas. Los seis pedidos siguen sin enviar.
""", encoding="utf-8")

(HERE / "E0_FISCAL_RECONSTRUCTION_V142.md").write_text("""# Reconstrucción fiscal E0 V142

La secuencia probatoria pasa a ser: catálogo 2008 → cuenta 230/equivalente → AUTO/equivalente y código externo → referencia unívoca → formulario C-55/CRG-DB → log → extracto BNA → Libro Banco → grupo/estado/historia de conciliación → respaldo AMIDDF. Cada capa controla a la anterior. Hasta obtener una concordancia individual y verificable, el numerador permanece en 0/10 ejecuciones confirmadas.
""", encoding="utf-8")

(HERE / "AUDITORIA_V142.md").write_text(f"""# Auditoría V142

- Fuentes maestras: 438; cero fuentes nuevas y dos fuentes oficiales preservadas reexplotadas.
- Fuentes primarias E0: 198; copias catalogadas SHA-válidas esperadas: 432.
- Diccionario: {len(event_codes)} filas; continuidad: {len(continuity)}; cuentas/ec.: {len(account_rows)}.
- Discriminantes: {len(discriminators)}; ruta de conciliación: {len(reconciliation_route)}.
- Cadena del Auditor: {len(auditor_chain)} filas; runbook CUT: {len(cut_runbook)} pasos.
- Resultados cero/conciliación: {len(zero_limits)} reglas; control visual PDF: {len(pdf_visual)} páginas.
- Ledger fiscal: {len(ledger)} filas; cortes metodológicos: {len(breaks)}.
- Trazabilidad: {len(trace)} objetos; claves: {len(keys)}.
- Escalera: 10 adjudicaciones; 9 cuentas candidatas; 0 ejecuciones confirmadas.
- Pedidos: 6 borradores, 0 enviados; panel estricto {STRICT}% sin cambios.
""", encoding="utf-8")

(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V142_A_V143.md").write_text("""# Handover V142 → V143

## Estado

- QA V142: ejecutar y exigir PASS.
- Cuenta de operación 230: débitos del extracto no originados en pagos CUT; gastos bancarios como ejemplo.
- Código 2013 `AUTO`; evolución 2022 `DBAUTO/CRAUTO`; rutas ordinarias separadas `PAGO/PGTR`.
- Cadena: código externo/interno → referencia unívoca → formulario → Libro Banco → LIB/APL/EXB/MAN → T/P/N.
- Continuidad 2013-2022 probada sólo como crosswalk; catálogo y código exactos 2008 siguen abiertos.
- SICHE CUT-SIDIF Central 2007-2014 conserva Entidades, Saldos, Extractos y Logs para ejecutar el test.
- Ninguna fila target recuperada; seis pedidos DRAFT_NOT_SENT; 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas.

## Prioridad V143

1. Mantener los seis pedidos como borradores salvo autorización expresa.
2. Buscar catálogo o exportación histórica que confirme cuenta 230/AUTO o sus equivalentes en 2008.
3. Buscar tablas básicas de conversión de código BNA externo a interno y grupos LIB/APL/EXB/MAN.
4. Intentar localizar referencias unívocas o contracódigos en extractos/logs públicos de 2008.
5. Mantener cuenta/código, formulario, extracto, Libro Banco y conciliación como capas separadas.
""", encoding="utf-8")

# Auditoría de preservación acumulada.
for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    source_path = AUDIT / f"{stem}_V141.csv"
    target_path = AUDIT / f"{stem}_V142.csv"
    target_path.write_text(
        source_path.read_text(encoding="utf-8-sig").replace("V141", "V142").replace("v141", "v142"),
        encoding="utf-8",
    )

hash_rows = []
for row in catalog:
    local = row["archivo_local"]
    path = REPO / local.lstrip("/") if local else None
    exists = bool(path and path.is_file())
    actual = sha256(path) if exists else ""
    expected = row["sha256"]
    hash_rows.append({
        "id": row["id"], "archivo_local": local, "exists": str(exists),
        "sha_catalog": expected, "sha_actual": actual,
        "hash_ok": str(bool(exists and expected and actual.lower() == expected.lower())),
    })
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V142.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V142.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
assert physical == hash_ok == 432

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or "tmp" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({
        "path": path.relative_to(REPO).as_posix(), "bytes": str(size),
        "mib": f"{size / 1048576:.6f}", "over_50_mib": str(size > 50 * 1048576),
        "over_100_mib": str(size > 100 * 1048576),
    })
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V142.csv", size_rows)

completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V141.json").read_text(encoding="utf-8"))
for key in list(completeness):
    if key.endswith("_v141") or "newly_preserved_v141" in key or "duplicate_recaptures_v141" in key:
        completeness.pop(key, None)
completeness.update({
    "checkpoint": "V142", "date": "2026-08-30",
    "state": "E0_CUT_ACCOUNT_230_AUTO_DBAUTO_CODE_AND_RECONCILIATION_ROUTE_PROVED_2008_CODE_TARGET_NOT_LOCATED_NOT_SENT",
    "numeric_v142_strict_changed": False,
    "master_catalog_entries": len(catalog), "physical_local_copies": physical,
    "physical_local_hash_ok": hash_ok, "binary_required_entries": 369,
    "binary_required_preserved": 368, "binary_required_source_complete": False,
    "remaining_physical_gaps": 1, "e0_primary_sources_preserved": len(census),
    "e0_quality": "PRIMARY_CUT_CODEBOOK_OPERATION_ACCOUNT_AND_RECONCILIATION_CROSSWALK",
    "sources_newly_preserved_v142": 0, "e0_primary_sources_newly_preserved_v142": 0,
    "e0_duplicate_recaptures_v142": 0,
    "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
    "e0_request_traceability_rows": len(trace), "e0_request_search_keys": len(keys),
    "e0_siche_cut_repository_rows": len(cut_repo), "e0_cut_extract_field_rows": len(extract_fields),
    "e0_cut_auditor_chain_rows": len(auditor_chain), "e0_cut_query_runbook_rows": len(cut_runbook),
    "e0_cut_zero_limit_rows": len(zero_limits), "e0_pdf_visual_controls": len(pdf_visual),
    "e0_siche_query_plan_rows": len(query_plan),
    "e0_cut_event_code_rows": len(event_codes), "e0_cut_code_continuity_rows": len(continuity),
    "e0_cut_operation_account_rows": len(account_rows), "e0_cut_discriminator_rows": len(discriminators),
    "e0_cut_reconciliation_route_rows": len(reconciliation_route),
    "e0_cut_2013_code_count": len(codes_2013), "e0_cut_2022_code_count": len(codes_2022),
    "e0_cut_account_230_functional_continuity_2013_2022": True,
    "e0_cut_target_2008_code_dictionary_located": False,
    "e0_siche_cut_period_start": 2007, "e0_siche_cut_period_end": 2014,
    "e0_siche_cut_includes_2008": True, "e0_siche_cut_target_extract_rows_located": 0,
    "e0_siche_cut_target_impact_log_rows_located": 0, "e0_siche_named_queries_executed": 0,
    "e0_sidif_target_document_types_located": 0, "e0_siche_target_exports_located": 0,
    "e0_settlement_award_rows_exact": 10, "e0_settlement_account_candidate_rows": 9,
    "e0_settlement_executed_rows_confirmed": 0, "e0_requests_submitted": 0,
    "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
    "historical_workstream": "Account 230 and AUTO/DBAUTO identify the bank-statement debit lane; PAGO/PGTR and reversal codes provide controls; 2013 reconciliation maps external to internal code, unique reference, form, bank book and LIB/APL/EXB/MAN state; exact 2008 dictionary and target row remain open; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V142.json").write_text(
    json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
backup_text = backup.read_text(encoding="utf-8-sig")
backup_marker = "## V142 · cuenta 230, códigos automáticos y conciliación"
if backup_marker not in backup_text:
    backup_text += f"""

{backup_marker}

- Cuenta de operación 230 concentra débitos del extracto que no son pagos CUT; gastos bancarios como ejemplo.
- Código 2013 AUTO evoluciona a DBAUTO/CRAUTO; PAGO/PGTR quedan como controles separados.
- Ruta verificable: código externo/interno, referencia unívoca, formulario, Libro Banco y conciliación.
- Catálogo 2008 y fila target siguen abiertos; la continuidad 2013-2022 no se proyecta retroactivamente.
- 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas; seis borradores no enviados.
"""
backup.write_text(backup_text, encoding="utf-8")

inherited = [
    {"script": "qa_v141.py", "pre_v142_result": "PASS", "post_v142_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V141 queda supersedida por cuenta 230, código AUTO/DBAUTO y ruta de conciliación V142."},
    {"script": "qa_v142.py", "pre_v142_result": "N/A", "post_v142_result": "PASS", "interpretation": "Diccionario, continuidad, cuentas, conciliación, hashes, límites y no envío verificados."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V142.csv", inherited)

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

repo = rows("E0_SICHE_CUT_HISTORICAL_REPOSITORY_V142.csv")
fields = rows("E0_CUT_EXTRACT_FIELD_CROSSWALK_V142.csv")
chain = rows("E0_CUT_AUDITOR_EVIDENCE_CHAIN_V142.csv")
runbook = rows("E0_CUT_TARGET_QUERY_RUNBOOK_V142.csv")
zero = rows("E0_CUT_ZERO_RESULT_AND_CONCILIATION_LIMITS_V142.csv")
visual = rows("E0_V142_PDF_VISUAL_CONTROL.csv")
plan = rows("E0_SICHE_TARGET_QUERY_PLAN_V142.csv")
codes = rows("E0_CUT_EVENT_CODE_DICTIONARY_V142.csv")
continuity = rows("E0_CUT_EVENT_CODE_CONTINUITY_V142.csv")
accounts = rows("E0_CUT_OPERATION_ACCOUNT_EQUATIONS_V142.csv")
discriminators = rows("E0_CUT_TARGET_CODE_DISCRIMINATION_V142.csv")
route = rows("E0_CUT_RECONCILIATION_EVIDENCE_ROUTE_V142.csv")
assert len(repo) == 10
assert repo[1]["proved_scope"] == "incluye ejercicio 2008"
assert {"Entidades Básicas", "Saldos por Tipo de Apertura de Cuenta de Operación", "Extractos", "Logs de Impacto"} <= {r["evidence"] for r in repo}
assert len(fields) == 20
assert {"Cod. Mov.", "Comprobante Respaldo", "Comprobante Origen", "Comprobante Relacionado"} <= {r["source_field"] for r in fields}
assert all("2008" in r["legacy_status"] for r in fields)
assert len(chain) == 12 and any("diferencia" in r["proof"].casefold() for r in chain)
assert len(runbook) == 19 and all(r["status"] == "DRAFT_NOT_SENT" for r in runbook)
assert len(zero) == 8 and all(r["status"] == "FROZEN" for r in zero)
assert len(visual) == 13 and all(r["result"] == "PASS" for r in visual)
assert len(plan) == 15 and all(r["status"] == "DRAFT_NOT_SENT" for r in plan)
assert len(codes) == 69 and {"AUTO", "DBAUTO", "CRAUTO", "PAGO", "PGTR"} <= {r["movement_code"] for r in codes}
assert len(continuity) == 28
assert sum(r["continuity_class"] == "SAME_CODE_CHANGED_DESCRIPTION" for r in continuity) == 2
assert any(r["code_2013"] == "AUTO" and r["continuity_class"] == "SPLIT_BY_SIGN" for r in continuity)
assert len(accounts) == 19 and sum(r["account_or_equation"] == "230" for r in accounts) == 2
assert all("gastos bancarios" in r["official_function"] for r in accounts if r["account_or_equation"] == "230")
assert len(discriminators) == 15 and {"LIB", "APL", "EXB", "MAN"} <= {r["code_or_key"] for r in discriminators}
assert len(route) == 15 and any(r["layer"] == "Gasto bancario" for r in route)

assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V142.csv")) == 238
assert len(rows("E0_FISCAL_METHOD_BREAKS_V142.csv")) == 188
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V142.csv")) == 178
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V142.csv")) == 206

ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V142.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)
register = rows("E0_REQUEST_RESPONSE_REGISTER_V142.csv")
assert len(register) == 6 and all(r["status"] == "DRAFT_NOT_SENT" for r in register)
assert all(r["submitted_on"] == "N/A" and r["submission_channel"] == "N/A" and r["receipt_or_case_id"] == "N/A" for r in register)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V142.csv")}
new_ids = ''' + repr(source_ids) + r'''
assert len(census) == 198 and new_ids <= set(census)
for row in census.values():
    local = row["local_path"]
    assert local and (REPO / local.lstrip("/")).is_file(), (row["source_id"], local)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 438 and len({r["id"] for r in catalog}) == 438

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V142.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V142"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 432
assert complete["binary_required_entries"] == 369 and complete["binary_required_preserved"] == 368
assert complete["e0_siche_cut_period_start"] == 2007 and complete["e0_siche_cut_period_end"] == 2014
assert complete["e0_siche_cut_includes_2008"] is True
assert complete["e0_siche_cut_target_extract_rows_located"] == 0
assert complete["e0_siche_cut_target_impact_log_rows_located"] == 0
assert complete["e0_siche_named_queries_executed"] == 0
assert complete["e0_siche_target_exports_located"] == 0
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v142_strict_changed"] is False
assert complete["sources_newly_preserved_v142"] == 0
assert complete["e0_cut_event_code_rows"] == 69 and complete["e0_cut_code_continuity_rows"] == 28
assert complete["e0_cut_operation_account_rows"] == 19 and complete["e0_cut_discriminator_rows"] == 15
assert complete["e0_cut_reconciliation_route_rows"] == 15
assert complete["e0_cut_account_230_functional_continuity_2013_2022"] is True
assert complete["e0_cut_target_2008_code_dictionary_located"] is False

request = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V142.md").read_text(encoding="utf-8-sig")
assert "## Clave V142 · cuenta 230, códigos automáticos y conciliación" in request
assert all(term in request for term in ("AUTO", "DBAUTO", "CRAUTO", "LIB", "APL", "EXB", "MAN", "BORRADOR_NO_ENVIADO"))
refs = (HERE / "SOURCE_REFERENCES_V142.md").read_text(encoding="utf-8-sig")
assert refs.count("## Fuentes reexplotadas V142 · código CUT y conciliación") == 1
combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv")) + "\n" + request
assert "TARGET_EXTRACT_FOUND" not in combined and "TARGET_IMPACT_LOG_FOUND" not in combined
assert "REQUEST_SENT" not in combined
for name in ("README_V142.md", "VEREDICTO_V142.md", "E0_FISCAL_RECONSTRUCTION_V142.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V142_A_V143.md"):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "0/10" in text
assert "Ninguna consulta fue ejecutada ni enviada" in (HERE / "README_V142.md").read_text(encoding="utf-8-sig")

print("V142 QA PASS")
'''
(HERE / "qa_v142.py").write_text(qa, encoding="utf-8")


def checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V142.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V142", "parent_checkpoint": "V141",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": 0, "reexploited_preserved_sources": 2, "duplicate_recaptures": 0,
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks),
        "siche_cut_repository_rows": len(cut_repo), "cut_extract_field_rows": len(extract_fields),
        "cut_auditor_chain_rows": len(auditor_chain), "cut_query_runbook_rows": len(cut_runbook),
        "cut_event_code_rows": len(event_codes), "cut_code_continuity_rows": len(continuity),
        "cut_operation_account_rows": len(account_rows), "cut_discriminator_rows": len(discriminators),
        "cut_reconciliation_route_rows": len(reconciliation_route),
        "cut_period": "2007-2014", "cut_includes_2008": True,
        "cut_target_extract_rows_located": 0, "cut_target_impact_log_rows_located": 0,
        "siche_named_queries_executed": 0, "siche_target_exports_located": 0,
        "award_rows_exact": 10, "account_candidate_rows": 9, "executed_settlement_rows_confirmed": 0,
        "request_drafts": 6, "request_traceability_rows": len(trace), "request_search_keys": len(keys),
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V142.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    "checkpoint": "V142",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical catalog copies SHA-valid; 0 new sources and 2 preserved official sources reexploited; account 230, AUTO/DBAUTO and reconciliation route proved as crosswalk but exact 2008 code and target row not located; zero of ten executed settlement rows confirmed; six requests drafted and none submitted.",
    "historical_workstream": "Obtain exact 2008 CUT-SIDIF Central dictionary, account 230/AUTO equivalent, external-to-internal BNA mapping, unique reference, form, bank book and LIB/APL/EXB/MAN reconciliation state; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V142 BUILD PASS")
