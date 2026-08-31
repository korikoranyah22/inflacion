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
PARENT = HERE.parent / "V140"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v141" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


EXPECTED = {
    "argentina_dgsiaf_bulletin_2020_q2_landing.html": (31982, "aa08a67cd5bb9fea508033b94686416cefde50773726eb590a5c264a4ca39701"),
    "argentina_dgsiaf_bulletin_2020_q2_siche_cut_2007_2014.pdf": (334840, "6d70b056f5a2ecd5bdbf847ac9139866ec18c9a2136a7f364333c08f7e16fb20"),
    "argentina_tgn_disposition_10_2025_cut_auditor.pdf": (1134786, "0b0382cfdfff7a7e1442789e3f0f2d83a3725b2d73e3582aacf93eee134cc669"),
    "argentina_tgn_treasury_system_v3_2022.pdf": (2910883, "5ebd3991747b9c4af619b5208ee2047348ff34b7bc85aefc3f8a614509f53186"),
}


SOURCES = [
    {
        "id": "e0_dgsiaf_bulletin_2020_q2_landing", "filename": "argentina_dgsiaf_bulletin_2020_q2_landing.html",
        "institution": "Dirección General de Sistemas Informáticos de Administración Financiera",
        "title": "Boletín trimestral DGSIAF II 2020 · página de publicación",
        "url": "https://www.argentina.gob.ar/noticias/boletin-trimestral-dgsiaf-ii-2020",
        "publication": "2020-07-01", "code": "Boletín DGSIAF II-2020",
        "families": "SICHE;publication_date;CUT;historical_repository",
        "breaks": "fecha de publicación versus fecha de implementación mayo 2020",
        "use": "USABLE_OFFICIAL_PUBLICATION_CONTROL",
        "caveat": "Prueba la publicación y el vínculo al boletín; el alcance técnico surge del PDF.",
        "note": "V141 E0: fija oficialmente la publicación del boletín que documenta el repositorio CUT histórico.",
    },
    {
        "id": "e0_dgsiaf_siche_cut_repository_2020_q2", "filename": "argentina_dgsiaf_bulletin_2020_q2_siche_cut_2007_2014.pdf",
        "institution": "Dirección General de Sistemas Informáticos de Administración Financiera",
        "title": "SICHE · repositorio histórico CUT-SIDIF Central 2007-2014",
        "url": "https://www.argentina.gob.ar/sites/default/files/2020-abr-may-jun-boletin-dgsiaf.pdf",
        "publication": "2020-05", "code": "SICHE CUT SIDIF Central 2007-2014",
        "families": "SICHE;CUT;SIDIF_Central;basic_entities;operation_account_balances;extracts;impact_logs",
        "breaks": "repositorio consultable versus fila target recuperada; órganos rectores versus acceso público",
        "use": "USABLE_EXACT_2008_CUT_EXTRACT_AND_IMPACT_LOG_ROUTE",
        "caveat": "Prueba cobertura 2007-2014 y clases consultables, no que el movimiento target esté localizado.",
        "note": "V141 E0: prueba en página 9 que SICHE contiene Entidades Básicas, saldos por apertura de cuenta, Extractos y Logs de Impacto CUT-SIDIF Central para 2007-2014.",
    },
    {
        "id": "e0_tgn_treasury_system_v3_2022_cut_extract", "filename": "argentina_tgn_treasury_system_v3_2022.pdf",
        "institution": "Tesorería General de la Nación",
        "title": "El Sistema de Tesorería v3 · auditor CUT y modelo de extracto escritural",
        "url": "https://www.argentina.gob.ar/sites/default/files/el-sistema-tesoreria-v3-2022.pdf",
        "publication": "2022-12", "code": "Manual TGN v3; sección 4.4.1.3-4.4.1.4",
        "families": "CUT;auditor;Libro_Banco;extract;operation_account;movement_code;supporting_form",
        "breaks": "modelo 2022 versus estructura histórica 2008",
        "use": "USABLE_CURRENT_CUT_EXTRACT_FIELD_AND_LINK_CROSSWALK",
        "caveat": "Aporta estructura funcional posterior; no prueba que todos esos campos existan en SICHE 2008.",
        "note": "V141 E0: página 63 vincula pagos autorizados y formularios respaldatorios con cada movimiento y muestra campos del extracto CUT.",
    },
    {
        "id": "e0_tgn_cut_auditor_instruction_2025", "filename": "argentina_tgn_disposition_10_2025_cut_auditor.pdf",
        "institution": "Tesorería General de la Nación",
        "title": "Disposición TGN 10/2025 · Instructivo para el Control del Auditor CUT",
        "url": "https://www.argentina.gob.ar/sites/default/files/di-2025-10-apn-tgn-mec.pdf",
        "publication": "2025-11-17", "code": "DI-2025-10-APN-TGN#MEC; IF-2025-126993383-APN-TGN#MEC",
        "families": "CUT;BNA;bank_statement;Libro_Banco;reconciliation;movement_detail;bank_voucher;finding_report",
        "breaks": "auditor e-SIDIF 2025 versus repositorio SICHE 2007-2014",
        "use": "USABLE_CURRENT_AUDITOR_QUERY_AND_EVIDENCE_SCHEMA",
        "caveat": "Define campos y lógica actuales; se usa como crosswalk y no como prueba retroactiva.",
        "note": "V141 E0: prueba cruce BNA-Libro Banco-Cuentas de Operación, campos de movimiento y reglas para documentar diferencias.",
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


def clone_parent() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    skip = {"build_e0_siche_named_queries_v140.py", "qa_v140.py", "MANIFEST_V140.json", "INHERITED_QA_STATUS_V140.csv"}
    for item in PARENT.iterdir():
        if not item.is_file() or item.name in skip or item.name.startswith("HANDOVER_PROXIMA_SESION"):
            continue
        target = HERE / item.name.replace("V140", "V141")
        text = item.read_text(encoding="utf-8-sig")
        placeholder = "historical_retrieval/__PARENT_V140__/"
        text = text.replace("historical_retrieval/v140/", placeholder)
        text = text.replace("_V140", "_V141").replace("_v140", "_v141")
        text = text.replace(placeholder, "historical_retrieval/v140/")
        if item.name.startswith("REQUEST_") or item.name in {
            "CURRENT_STATE_V140.csv", "E0_INSTITUTIONAL_REQUEST_PACKAGE_V140.md", "RETRIEVAL_LOG_V140.md",
        }:
            text = text.replace("V140", "V141").replace("v140", "v141")
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
assert len(catalog) == 434
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

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V141.csv"
census = [row for row in read_csv(census_path) if row["source_id"] not in source_ids]
assert len(census) == 194
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

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V141.csv"
provenance = [row for row in read_csv(provenance_path) if row["source_id"] not in source_ids]
assert len(provenance) == 97
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
    {"row_id": "CR141_08", "evidence": "Combinación 7.2.8/83106000 con CUT", "proved_scope": "cruce metodológico V141", "target_application": "formulario→impacto→extracto", "required_output": "identificador compartido;fecha;importe;cuenta", "inference_limit": "el PDF no publica esa combinación", "status": "CROSSWALK_PROPOSED_NOT_EXECUTED", "source_id": "E0_SICHE_NAMED_QUERY_TARGET_MAP_V141.csv;e0_dgsiaf_siche_cut_repository_2020_q2", "locator": "matriz V141"},
    {"row_id": "CR141_09", "evidence": "Cuenta CUT 3855/19 en manuales posteriores", "proved_scope": "ejemplo/entorno posterior", "target_application": "clave de control, no filtro inicial", "required_output": "cuenta histórica surgida de Entidades Básicas", "inference_limit": "no atribuir 3855/19 retroactivamente", "status": "CURRENT_IDENTIFIER_ONLY_LEGACY_OPEN", "source_id": "e0_tgn_treasury_system_v3_2022_cut_extract;e0_tgn_cut_auditor_instruction_2025", "locator": "PDF p.63; PDF p.15"},
    {"row_id": "CR141_10", "evidence": "Cadena mínima", "proved_scope": "formulario;log;extracto;Libro Banco;conciliación", "target_application": "cierre de ejecución", "required_output": "cinco vínculos concordantes", "inference_limit": "ninguna capa sustituye a las restantes", "status": "CLOSE_TEST_FROZEN_TARGET_OPEN", "source_id": "e0_dgsiaf_siche_cut_repository_2020_q2;e0_tgn_treasury_system_v3_2022_cut_extract;e0_tgn_cut_auditor_instruction_2025", "locator": "PDF p.9;p.63;p.5-39"},
]
write_csv(HERE / "E0_SICHE_CUT_HISTORICAL_REPOSITORY_V141.csv", cut_repo)

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
write_csv(HERE / "E0_CUT_EXTRACT_FIELD_CROSSWALK_V141.csv", extract_fields)

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
write_csv(HERE / "E0_CUT_AUDITOR_EVIDENCE_CHAIN_V141.csv", auditor_chain)

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
cut_runbook = [{
    "step_id": f"CQ141_{number:02d}", "sequence": str(number), "query": query, "filters": filters,
    "requested_output": output, "decision": decision, "status": "DRAFT_NOT_SENT",
} for number, query, filters, output, decision in run_steps]
write_csv(HERE / "E0_CUT_TARGET_QUERY_RUNBOOK_V141.csv", cut_runbook)

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
write_csv(HERE / "E0_CUT_ZERO_RESULT_AND_CONCILIATION_LIMITS_V141.csv", zero_limits)

pdf_visual = [
    {"control_id": "PV141_01", "source_id": "e0_dgsiaf_siche_cut_repository_2020_q2", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v141/binaries/argentina_dgsiaf_bulletin_2020_q2_siche_cut_2007_2014.pdf", "pdf_page": "9", "rendered_check": "SICHE CUT-SIDIF Central 2007-2014; Entidades, Saldos, Extractos y Logs", "result": "PASS"},
    {"control_id": "PV141_02", "source_id": "e0_tgn_treasury_system_v3_2022_cut_extract", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v141/binaries/argentina_tgn_treasury_system_v3_2022.pdf", "pdf_page": "63", "rendered_check": "auditor CUT; formulario respaldatorio; modelo de extracto y campos", "result": "PASS"},
    {"control_id": "PV141_03", "source_id": "e0_tgn_cut_auditor_instruction_2025", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v141/binaries/argentina_tgn_disposition_10_2025_cut_auditor.pdf", "pdf_page": "7", "rendered_check": "BNA versus Libro Banco y cuentas de operación", "result": "PASS"},
    {"control_id": "PV141_04", "source_id": "e0_tgn_cut_auditor_instruction_2025", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v141/binaries/argentina_tgn_disposition_10_2025_cut_auditor.pdf", "pdf_page": "21", "rendered_check": "semántica de grilla vacía y atributos del auditor", "result": "PASS"},
    {"control_id": "PV141_05", "source_id": "e0_tgn_cut_auditor_instruction_2025", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v141/binaries/argentina_tgn_disposition_10_2025_cut_auditor.pdf", "pdf_page": "36", "rendered_check": "detalle de movimiento de extracto y comprobante bancario", "result": "PASS"},
    {"control_id": "PV141_06", "source_id": "e0_tgn_cut_auditor_instruction_2025", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v141/binaries/argentina_tgn_disposition_10_2025_cut_auditor.pdf", "pdf_page": "41", "rendered_check": "formulario defectuoso, diferencia neta y documentación del hallazgo", "result": "PASS"},
]
write_csv(HERE / "E0_V141_PDF_VISUAL_CONTROL.csv", pdf_visual)

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
]
query_plan = [{
    "query_id": f"SQ141_{number:02d}", "sequence": str(number), "system": system,
    "filter_set": filters, "requested_output": output, "success_test": decision,
    "fallback": "derivación al órgano rector y equivalente legacy documentado", "status": "DRAFT_NOT_SENT",
} for number, system, filters, output, decision in plan_specs]
write_csv(HERE / "E0_SICHE_TARGET_QUERY_PLAN_V141.csv", query_plan)

ledger_path = HERE / "E0_FISCAL_MECHANISM_LEDGER_V141.csv"
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
        "source_locator": "matrices V141", "realization_status": status, "additivity": "NON_ADDITIVE",
        "status_interpretation": interpretation, "caveat": "No convertir repositorio, campo, log o diferencia en pago ejecutado.",
    })
assert len(ledger) == 228
write_csv(ledger_path, ledger)

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V141.csv"
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
    ("cut_basic_entity_not_historical_account_identity", "identity", "Cuenta actual no fija cuenta 2008.", "Descubrirla en Entidades Básicas.", "E0_SICHE_CUT_HISTORICAL_REPOSITORY_V141.csv"),
    ("cut_balance_not_movement", "phase", "Saldo de cuenta no identifica débito/crédito.", "Exigir extracto y log.", "e0_dgsiaf_siche_cut_repository_2020_q2"),
    ("cut_extract_not_cause", "causality", "Movimiento externo sin comprobante no identifica comisión.", "Cruzar formulario y log.", "e0_tgn_treasury_system_v3_2022_cut_extract"),
    ("cut_impact_log_not_reconciliation", "phase", "Log de impacto no prueba conciliación.", "Cruzar Libro Banco, extracto y estado.", "e0_tgn_cut_auditor_instruction_2025"),
    ("current_cut_field_not_legacy_field", "system", "Campo 2022/2025 no se presume idéntico en 2008.", "Pedir equivalente funcional y diccionario.", "e0_tgn_treasury_system_v3_2022_cut_extract;e0_tgn_cut_auditor_instruction_2025"),
    ("auditor_net_difference_not_target_amount", "arithmetic", "Diferencia neta puede combinar factores.", "Desagregar movimientos; no atribuir total.", "e0_tgn_cut_auditor_instruction_2025"),
]
for break_id, dimension, problem, rule, evidence in break_specs:
    breaks.append({"break_id": break_id, "dimension": dimension, "problem": problem, "rule": rule, "status": "FROZEN_V141", "evidence": evidence})
assert len(breaks) == 180
write_csv(breaks_path, breaks)

trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V141.csv"
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

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V141.csv"
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
        "source_or_basis": "E0_SICHE_CUT_HISTORICAL_REPOSITORY_V141.csv;E0_CUT_TARGET_QUERY_RUNBOOK_V141.csv",
        "caveat": "Clave o clase probada; no confirma fila.",
    })
assert len(keys) == 194
write_csv(keys_path, keys)

register_path = HERE / "E0_REQUEST_RESPONSE_REGISTER_V141.csv"
register = read_csv(register_path)
for row in register:
    row["status"] = "DRAFT_NOT_SENT"
    row["submitted_on"] = "N/A"
    row["submission_channel"] = "N/A"
    row["receipt_or_case_id"] = "N/A"
write_csv(register_path, register)

request_path = HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V141.md"
request_text = request_path.read_text(encoding="utf-8-sig")
request_marker = "## Clave V141 · repositorio histórico CUT 2007-2014"
if request_marker not in request_text:
    request_text += f"""

{request_marker}

El Boletín Trimestral DGSIAF II-2020 documenta que en mayo de 2020 se implementó en SICHE el repositorio histórico de la Cuenta Única del Tesoro del SIDIF Central con datos de `2007 a 2014`. El período incluye expresamente el ejercicio 2008 y el repositorio permite consultar cuatro clases: `Entidades Básicas`, `Saldos por Tipo de Apertura de Cuenta de Operación`, `Extractos` y `Logs de Impacto`. Su alcance publicado son los Órganos Rectores. Esta prueba permite dirigir el pedido a DGSIAF/TGN, pero no significa que ya se haya ejecutado una consulta ni localizado un movimiento.

Se solicita ejecutar las cuatro clases por separado. Primero, `Entidades Básicas` para identificar —sin prefijar la cuenta actual— banco, sucursal, cuenta, moneda, titular, SAF, vigencia y cuentas de operación aplicables a `SAF 355` durante 2008. Luego, obtener los saldos por tipo de apertura y el universo completo de Extractos y Logs de Impacto del 1 de enero al 31 de diciembre de 2008. Sólo después se deberán aplicar `71597`, `152677`, `2876`, `83106000`, partida `7.2.8`, concepto `COMISIONES - BANCO NACION`, importe agregado `$32.270,30`, eventuales componentes y las fechas que arroje `Formulario por Pda. Presupuestaria y Sigade`.

Para cada movimiento candidato se piden, en la nomenclatura histórica disponible o su equivalente funcional: fecha, secuencia, código de movimiento externo e interno y descripciones; crédito/débito; importe; comprobante bancario; cuenta de operación; fuente y clase de gasto; formulario de respaldo; comprobante origen y relacionado; referencia de Libro Banco/Extracto; estado de conciliación; historial; regularización, rechazo o anulación. El manual TGN v3 muestra que el modelo de extracto puede enlazar cada movimiento con comprobantes de respaldo, origen, relacionado y Libro Banco/Extracto; el Instructivo del Auditor CUT 2025 detalla fecha, secuencia, códigos, comprobante bancario, importe pendiente y estado. Ambos se usan como diccionario posterior: se solicita el equivalente 2008 y no se presume identidad de esquema.

Debe entregarse también el historial de conciliación y, si obra, el informe diario del Auditor de la fecha, con saldos de Libro Banco, Extracto y Cuentas de Operación, diferencia, movimientos involucrados, posible causa y seguimiento. Una diferencia es neta y puede combinar varios factores; no se atribuirá íntegramente al target. Del mismo modo, una grilla vacía sólo acredita que esos filtros no devolvieron filas en ese dataset: para evaluarla se requieren nombre de módulo y dataset, modelo, filtros, fecha de ejecución, cobertura temporal, cantidad de filas, exclusiones, diccionario y regla de retención. **Estado: BORRADOR_NO_ENVIADO.**
"""
request_path.write_text(request_text, encoding="utf-8")

checklist_path = HERE / "REQUEST_SUBMISSION_CHECKLIST_V141.md"
checklist = checklist_path.read_text(encoding="utf-8-sig")
check_marker = "## Control V141 · repositorio CUT histórico"
if check_marker not in checklist:
    checklist += f"""

{check_marker}

- [ ] Identificar la cuenta CUT histórica en Entidades Básicas antes de usar 3855/19.
- [ ] Ejecutar por separado Saldos, Extractos y Logs de Impacto para todo 2008.
- [ ] Cruzar el formulario SICHE con log, extracto, Libro Banco y conciliación.
- [ ] Pedir ambos signos y componentes; no limitar al agregado 32.270,30.
- [ ] Pedir comprobante bancario, respaldo, origen, relacionado e historial.
- [ ] No atribuir una diferencia neta íntegra al target.
- [ ] Exigir metadatos y diccionario para toda grilla vacía.
- [ ] Confirmar autorización expresa antes de presentar cualquiera de los seis borradores.
"""
checklist_path.write_text(checklist, encoding="utf-8")

source_refs_path = HERE / "SOURCE_REFERENCES_V141.md"
source_refs = source_refs_path.read_text(encoding="utf-8-sig")
canonical_lines = []
for line in source_refs.splitlines():
    match = re.match(r"^- `([^`]+)`", line)
    if match and match.group(1) in catalog_by_id:
        canonical = catalog_by_id[match.group(1)]["archivo_local"]
        line = re.sub(r"`/[^`]+`", f"`{canonical}`", line)
    canonical_lines.append(line)
source_refs = "\n".join(canonical_lines) + "\n"
refs_marker = "## Fuentes nuevas V141 · repositorio CUT histórico y Auditor"
if refs_marker not in source_refs:
    source_refs += "\n" + refs_marker + "\n\n"
    for item in SOURCES:
        source_refs += f"- `{item['id']}` · {item['title']} · {item['url']} · `{item['local']}` · `{item['sha256']}`\n"
source_refs_path.write_text(source_refs, encoding="utf-8")

(HERE / "README_V141.md").write_text("""# V141 · repositorio CUT histórico 2007-2014

V141 prueba una ruta bancaria histórica directamente aplicable a 2008: SICHE contiene un repositorio CUT-SIDIF Central para 2007-2014 con Entidades Básicas, saldos por tipo de apertura de cuenta, Extractos y Logs de Impacto. La búsqueda ya no termina en el formulario: puede continuar hacia el impacto en cuenta y el extracto.

Los manuales TGN posteriores aportan el diccionario de cruce: código y fecha de movimiento, crédito/débito, comprobantes de respaldo/origen/relacionado, Libro Banco/Extracto, referencia bancaria, importe y estado de conciliación. Se usan como equivalentes funcionales a solicitar, no como prueba de que el esquema 2008 sea idéntico. Ninguna consulta fue ejecutada ni enviada. Balance: 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas; seis pedidos DRAFT_NOT_SENT.
""", encoding="utf-8")

(HERE / "VEREDICTO_V141.md").write_text("""# Veredicto V141

La ruta bancaria dejó de ser una inferencia genérica. DGSIAF publicó que SICHE conserva Extractos y Logs de Impacto CUT-SIDIF Central entre 2007 y 2014. Por tanto, 2008 está dentro de un repositorio consultable por los Órganos Rectores. Esta ruta puede cruzar `7.2.8 + 83106000`, los SIDIF `71597/152677/2876` y sus importes con un movimiento bancario y su impacto interno.

El cierre exige concordancia entre formulario, log, extracto, Libro Banco y conciliación. La cuenta `3855/19` aparece en manuales posteriores pero no se proyecta hacia 2008: la cuenta histórica debe surgir de Entidades Básicas. Una grilla vacía no prueba inexistencia o pago; una diferencia del Auditor es neta y puede combinar movimientos; un log no prueba conciliación.

No se recuperó una fila target, extracto, log, Libro Banco, informe del Auditor ni cuerpo AMIDDF. Permanecen 10 adjudicaciones exactas, 9 cuentas candidatas y 0/10 ejecuciones confirmadas. Los seis pedidos siguen sin enviar.
""", encoding="utf-8")

(HERE / "E0_FISCAL_RECONSTRUCTION_V141.md").write_text("""# Reconstrucción fiscal E0 V141

La secuencia probatoria pasa a ser: formulario por partida/SIGADE → entidad y cuenta CUT histórica → log de impacto → movimiento de extracto BNA → Libro Banco → estado e historial de conciliación → respaldo AMIDDF. Cada capa controla a la anterior. Hasta obtener una concordancia individual y verificable, el numerador permanece en 0/10 ejecuciones confirmadas.
""", encoding="utf-8")

(HERE / "AUDITORIA_V141.md").write_text(f"""# Auditoría V141

- Fuentes maestras: 438; cuatro fuentes oficiales nuevas.
- Fuentes primarias E0: 198; copias catalogadas SHA-válidas esperadas: 432.
- Repositorio CUT histórico: {len(cut_repo)} controles; campos de extracto: {len(extract_fields)}.
- Cadena del Auditor: {len(auditor_chain)} filas; runbook CUT: {len(cut_runbook)} pasos.
- Resultados cero/conciliación: {len(zero_limits)} reglas; control visual PDF: {len(pdf_visual)} páginas.
- Ledger fiscal: {len(ledger)} filas; cortes metodológicos: {len(breaks)}.
- Trazabilidad: {len(trace)} objetos; claves: {len(keys)}.
- Escalera: 10 adjudicaciones; 9 cuentas candidatas; 0 ejecuciones confirmadas.
- Pedidos: 6 borradores, 0 enviados; panel estricto {STRICT}% sin cambios.
""", encoding="utf-8")

(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V141_A_V142.md").write_text("""# Handover V141 → V142

## Estado

- QA V141: ejecutar y exigir PASS.
- SICHE conserva CUT-SIDIF Central 2007-2014: Entidades Básicas, Saldos por Apertura, Extractos y Logs de Impacto.
- Cobertura temporal exacta: incluye 2008; acceso publicado para Órganos Rectores.
- Cadena target: formulario 7.2.8/83106000 → log → extracto → Libro Banco → conciliación → AMIDDF.
- Campos posteriores útiles: fecha, secuencia, códigos, débito/crédito, referencia bancaria, comprobantes y estado.
- Cuenta 3855/19 no se presume para 2008; debe surgir de Entidades Básicas.
- Ninguna fila target recuperada; seis pedidos DRAFT_NOT_SENT; 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas.

## Prioridad V142

1. Mantener los seis pedidos como borradores salvo autorización expresa.
2. Buscar manual o pantalla específica del módulo CUT histórico de SICHE.
3. Buscar catálogo/diccionario de códigos de movimiento CUT-SIDIF Central 2008.
4. Intentar localizar identidad histórica de cuenta CUT y cuentas de operación sin proyectar 3855/19.
5. Explorar si publicaciones TGN/CGN preservan informes, logs o conciliaciones 2008.
6. Mantener formulario, log, extracto, Libro Banco y conciliación como capas separadas.
""", encoding="utf-8")

# Auditoría de preservación acumulada.
for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    source_path = AUDIT / f"{stem}_V140.csv"
    target_path = AUDIT / f"{stem}_V141.csv"
    target_path.write_text(
        source_path.read_text(encoding="utf-8-sig").replace("V140", "V141").replace("v140", "v141"),
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
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V141.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V141.csv", hash_rows)
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
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V141.csv", size_rows)

completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V140.json").read_text(encoding="utf-8"))
for key in list(completeness):
    if key.endswith("_v140") or "newly_preserved_v140" in key or "duplicate_recaptures_v140" in key:
        completeness.pop(key, None)
completeness.update({
    "checkpoint": "V141", "date": "2026-08-30",
    "state": "E0_SICHE_CUT_2007_2014_EXTRACT_LOG_ROUTE_PROVED_TARGET_MOVEMENT_NOT_LOCATED_NOT_SENT",
    "numeric_v141_strict_changed": False,
    "master_catalog_entries": len(catalog), "physical_local_copies": physical,
    "physical_local_hash_ok": hash_ok, "binary_required_entries": 369,
    "binary_required_preserved": 368, "binary_required_source_complete": False,
    "remaining_physical_gaps": 1, "e0_primary_sources_preserved": len(census),
    "e0_quality": "PRIMARY_SICHE_CUT_HISTORICAL_EXTRACT_LOG_AND_AUDITOR_CROSSWALK",
    "sources_newly_preserved_v141": 4, "e0_primary_sources_newly_preserved_v141": 4,
    "e0_duplicate_recaptures_v141": 0,
    "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
    "e0_request_traceability_rows": len(trace), "e0_request_search_keys": len(keys),
    "e0_siche_cut_repository_rows": len(cut_repo), "e0_cut_extract_field_rows": len(extract_fields),
    "e0_cut_auditor_chain_rows": len(auditor_chain), "e0_cut_query_runbook_rows": len(cut_runbook),
    "e0_cut_zero_limit_rows": len(zero_limits), "e0_pdf_visual_controls": len(pdf_visual),
    "e0_siche_query_plan_rows": len(query_plan),
    "e0_siche_cut_period_start": 2007, "e0_siche_cut_period_end": 2014,
    "e0_siche_cut_includes_2008": True, "e0_siche_cut_target_extract_rows_located": 0,
    "e0_siche_cut_target_impact_log_rows_located": 0, "e0_siche_named_queries_executed": 0,
    "e0_sidif_target_document_types_located": 0, "e0_siche_target_exports_located": 0,
    "e0_settlement_award_rows_exact": 10, "e0_settlement_account_candidate_rows": 9,
    "e0_settlement_executed_rows_confirmed": 0, "e0_requests_submitted": 0,
    "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
    "historical_workstream": "SICHE CUT-SIDIF Central 2007-2014 repository with basic entities, balances, extracts and impact logs proved; current TGN field/auditor schema provides crosswalk only; target movement, historical account identity, reconciliation and AMIDDF body remain open; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V141.json").write_text(
    json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
backup_text = backup.read_text(encoding="utf-8-sig")
backup_marker = "## V141 · repositorio CUT histórico 2007-2014"
if backup_marker not in backup_text:
    backup_text += f"""

{backup_marker}

- SICHE conserva CUT-SIDIF Central 2007-2014: Entidades Básicas, Saldos, Extractos y Logs de Impacto.
- La cobertura incluye exactamente 2008 y abre una ruta bancaria independiente.
- Manuales TGN posteriores fijan campos para comprobantes, códigos, Libro Banco y conciliación como crosswalk.
- Cuenta 3855/19 no se proyecta retroactivamente; identidad histórica pendiente.
- 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas; seis borradores no enviados.
"""
backup.write_text(backup_text, encoding="utf-8")

inherited = [
    {"script": "qa_v140.py", "pre_v141_result": "PASS", "post_v141_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V140 queda supersedida por la ruta histórica CUT, campos de extracto y Auditor V141."},
    {"script": "qa_v141.py", "pre_v141_result": "N/A", "post_v141_result": "PASS", "interpretation": "Fuentes, hashes, alcance temporal, límites, trazabilidad y no envío verificados."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V141.csv", inherited)

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

repo = rows("E0_SICHE_CUT_HISTORICAL_REPOSITORY_V141.csv")
fields = rows("E0_CUT_EXTRACT_FIELD_CROSSWALK_V141.csv")
chain = rows("E0_CUT_AUDITOR_EVIDENCE_CHAIN_V141.csv")
runbook = rows("E0_CUT_TARGET_QUERY_RUNBOOK_V141.csv")
zero = rows("E0_CUT_ZERO_RESULT_AND_CONCILIATION_LIMITS_V141.csv")
visual = rows("E0_V141_PDF_VISUAL_CONTROL.csv")
plan = rows("E0_SICHE_TARGET_QUERY_PLAN_V141.csv")
assert len(repo) == 10
assert repo[1]["proved_scope"] == "incluye ejercicio 2008"
assert {"Entidades Básicas", "Saldos por Tipo de Apertura de Cuenta de Operación", "Extractos", "Logs de Impacto"} <= {r["evidence"] for r in repo}
assert len(fields) == 20
assert {"Cod. Mov.", "Comprobante Respaldo", "Comprobante Origen", "Comprobante Relacionado"} <= {r["source_field"] for r in fields}
assert all("2008" in r["legacy_status"] for r in fields)
assert len(chain) == 12 and any("diferencia" in r["proof"].casefold() for r in chain)
assert len(runbook) == 14 and all(r["status"] == "DRAFT_NOT_SENT" for r in runbook)
assert len(zero) == 8 and all(r["status"] == "FROZEN" for r in zero)
assert len(visual) == 6 and all(r["result"] == "PASS" for r in visual)
assert len(plan) == 12 and all(r["status"] == "DRAFT_NOT_SENT" for r in plan)

assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V141.csv")) == 228
assert len(rows("E0_FISCAL_METHOD_BREAKS_V141.csv")) == 180
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V141.csv")) == 172
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V141.csv")) == 194

ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V141.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)
register = rows("E0_REQUEST_RESPONSE_REGISTER_V141.csv")
assert len(register) == 6 and all(r["status"] == "DRAFT_NOT_SENT" for r in register)
assert all(r["submitted_on"] == "N/A" and r["submission_channel"] == "N/A" and r["receipt_or_case_id"] == "N/A" for r in register)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V141.csv")}
new_ids = ''' + repr(source_ids) + r'''
assert len(census) == 198 and new_ids <= set(census)
for row in census.values():
    local = row["local_path"]
    assert local and (REPO / local.lstrip("/")).is_file(), (row["source_id"], local)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 438 and len({r["id"] for r in catalog}) == 438

expected = ''' + repr(EXPECTED) + r'''
bin_dir = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v141" / "binaries"
assert len(list(bin_dir.iterdir())) == 4
for name, (size, digest) in expected.items():
    path = bin_dir / name
    assert path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest() == digest

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V141.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V141"
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
assert complete["numeric_v141_strict_changed"] is False

request = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V141.md").read_text(encoding="utf-8-sig")
assert "## Clave V141 · repositorio histórico CUT 2007-2014" in request
assert all(term in request for term in ("Entidades Básicas", "Extractos", "Logs de Impacto", "BORRADOR_NO_ENVIADO"))
refs = (HERE / "SOURCE_REFERENCES_V141.md").read_text(encoding="utf-8-sig")
assert refs.count("## Fuentes nuevas V141 · repositorio CUT histórico y Auditor") == 1
combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv")) + "\n" + request
assert "TARGET_EXTRACT_FOUND" not in combined and "TARGET_IMPACT_LOG_FOUND" not in combined
assert "REQUEST_SENT" not in combined
for name in ("README_V141.md", "VEREDICTO_V141.md", "E0_FISCAL_RECONSTRUCTION_V141.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V141_A_V142.md"):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "0/10" in text
assert "Ninguna consulta fue ejecutada ni enviada" in (HERE / "README_V141.md").read_text(encoding="utf-8-sig")

print("V141 QA PASS")
'''
(HERE / "qa_v141.py").write_text(qa, encoding="utf-8")


def checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V141.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V141", "parent_checkpoint": "V140",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": 4, "duplicate_recaptures": 0,
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks),
        "siche_cut_repository_rows": len(cut_repo), "cut_extract_field_rows": len(extract_fields),
        "cut_auditor_chain_rows": len(auditor_chain), "cut_query_runbook_rows": len(cut_runbook),
        "cut_period": "2007-2014", "cut_includes_2008": True,
        "cut_target_extract_rows_located": 0, "cut_target_impact_log_rows_located": 0,
        "siche_named_queries_executed": 0, "siche_target_exports_located": 0,
        "award_rows_exact": 10, "account_candidate_rows": 9, "executed_settlement_rows_confirmed": 0,
        "request_drafts": 6, "request_traceability_rows": len(trace), "request_search_keys": len(keys),
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V141.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    "checkpoint": "V141",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical catalog copies SHA-valid; 4 new official sources; SICHE CUT-SIDIF Central 2007-2014 extracts and impact logs route proved but not run; zero of ten executed settlement rows confirmed; six requests drafted and none submitted.",
    "historical_workstream": "Obtain exact SICHE CUT basic entities, operation-account balances, extracts and impact logs for 2008; cross with form, Libro Banco, reconciliation and AMIDDF; current TGN manuals are field crosswalks only; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V141 BUILD PASS")
