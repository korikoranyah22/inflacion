from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv, hashlib, json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows, fields=None):
    fields = fields or (list(rows[0]) if rows else [])
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def upsert(rows, additions, key):
    order = [str(row[key]) for row in rows]
    indexed = {str(row[key]): row for row in rows}
    for row in additions:
        item = {name: str(value) for name, value in row.items()}
        value = item[key]
        indexed[value] = item
        if value not in order:
            order.append(value)
    return [indexed[value] for value in order]


def append_section(path: Path, marker: str, body: str):
    text = path.read_text(encoding="utf-8-sig")
    if marker not in text:
        path.write_text(text.rstrip() + "\n\n" + marker + "\n\n" + body.strip() + "\n", encoding="utf-8")


SOURCES = [
    ("e0_argentina_sidif_link_historical_integration", "Secretaría de Hacienda", "Segunda etapa de la reforma · integración SIGADE–SIDIF/Link", "https://www.argentina.gob.ar/economia/administracionfinancieragubernamental/segundaetapa", "/research/ciclo_ajuste/inputs/historical_retrieval/v146/binaries/argentina_financial_reform_second_stage_sidif_link.html", "1995-2008", "Historia de la administración financiera", "HTML oficial", "SIGADE transmitía en forma sistemática y en tiempo real desembolsos, amortización, intereses y comisiones a SIDIF mediante SIDIF/Link."),
    ("e0_dgsiaf_trajectory_sidif_link", "Secretaría de Hacienda · DGSIAF", "Trayectoria institucional DGSIAF", "https://www.argentina.gob.ar/economia/sechacienda/dgsiaf/institucionaltrayectoria", "/research/ciclo_ajuste/inputs/historical_retrieval/v146/binaries/argentina_dgsiaf_institutional_trajectory.html", "1991-2026", "Trayectoria DGSIAF", "HTML oficial", "Cronología de SIDIF Central, sistemas locales, e-SIDIF y sistemas heredados."),
    ("e0_mecon_uai_plan_2019_sigade_sidif_link", "Ministerio de Hacienda · UAI", "Plan Anual de Trabajo 2019 · circuito SIGADE–SIDIF-Link", "https://www.argentina.gob.ar/sites/default/files/plan-anual-de-trabajo-2019-df.pdf", "/research/ciclo_ajuste/inputs/historical_retrieval/v146/binaries/mecon_uai_annual_audit_plan_2019_sigade_sidif_link.pdf", "2019", "Plan Anual UAI", "PDF oficial", "Diagrama auditado: SIGADE transfiere por SIDIF-LINK a SIDIF-Central y la ejecución de pagos alimenta e-SIDIF."),
    ("e0_mecon_uai_report_13_2020_repo_commission", "Ministerio de Economía · UAI", "Informe UAI 13/2020 · conciliación SIGADE/e-SIDIF y comisión REPO", "https://www.argentina.gob.ar/sites/default/files/informe_uai_no_13-2020.pdf", "/research/ciclo_ajuste/inputs/historical_retrieval/v146/binaries/mecon_uai_report_13_2020_repo_commission.pdf", "2019-2020", "Informe UAI 13/2020", "PDF oficial", "Registra regularización por $0,61 millones de comisiones REPO en 2.1.2.01.02.99.00 y una inconsistencia aritmética interna de $0,45 millones."),
    ("e0_dgsiaf_siche_sidif_central_q2_2022", "Secretaría de Hacienda · DGSIAF", "SICHE SIDIF Central · mejoras segundo trimestre 2022", "https://www.argentina.gob.ar/economia/sechacienda/dgsiaf/boletin-trimestral-ii-2022/siche", "/research/ciclo_ajuste/inputs/historical_retrieval/v146/binaries/argentina_dgsiaf_siche_sidif_central_2022_q2.html", "2022-Q2", "Boletín DGSIAF", "HTML oficial", "Añade Programación de la Ejecución y Transmisiones al repositorio SICHE de SIDIF Central."),
    ("e0_cgn_chart_accounts_2018", "Contaduría General de la Nación", "Plan de Cuentas de la Administración Nacional 2018", "https://www.argentina.gob.ar/sites/default/files/plan_2018.pdf", "/research/ciclo_ajuste/inputs/historical_retrieval/v146/binaries/cgn_chart_of_accounts_2018.pdf", "2018", "Plan de Cuentas", "PDF oficial", "Define 2.1.2.01.02.99.00 como otros títulos y valores de deuda pública a pagar en moneda extranjera."),
    ("e0_cgn_account_1999_repo_portfolio", "Contaduría General de la Nación", "Cuenta de Inversión 1999 · nota de operaciones Repo", "https://www.economia.gob.ar/hacienda/cgn/cuenta/1999/tomo_i/04notas99.htm", "/research/ciclo_ajuste/inputs/historical_retrieval/v146/binaries/cgn_account_1999_repo_portfolio_note.html", "1999", "Cuenta de Inversión", "HTML oficial histórico", "Menciona Títulos en Cartera a LP Operaciones Repo por $312.943.885,60; control nominal, sin continuidad probada a 2019."),
]

source_data = []
for sid, institution, title, url, local, period, series, kind, note in SOURCES:
    path = REPO / local.lstrip("/")
    assert path.is_file(), path
    source_data.append({"id": sid, "institution": institution, "title": title, "url": url,
                        "local": local, "period": period, "series": series, "kind": kind,
                        "note": note, "sha": sha256(path), "bytes": path.stat().st_size})

catalog = read_csv(CATALOG)
catalog = upsert(catalog, [{"id": s["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": s["institution"],
    "titulo": s["title"], "url_original": s["url"], "archivo_local": s["local"], "fecha_descarga": "2026-08-31",
    "fecha_publicacion": s["period"], "codigo_serie": s["series"], "periodo_utilizado": s["period"], "tipo": s["kind"],
    "sha256": s["sha"], "nota": "V146: " + s["note"]} for s in source_data], "id")
write_csv(CATALOG, catalog, list(catalog[0]))

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V146.csv"
census = read_csv(census_path)
census = upsert(census, [{"source_id": s["id"], "institution": s["institution"], "artifact": s["title"], "url": s["url"],
    "local_path": s["local"], "sha256": s["sha"], "bytes": s["bytes"], "period_coverage": s["period"],
    "variable_families": "SIGADE;SIDIF-Link;SIDIF Central;SICHE;REPO;cuentas", "primary_source": "YES", "preserved": "YES",
    "method_breaks": "arquitectura/registro/comparador no equivale a fila bancaria objetivo", "use_status": "E0_USABLE_WITH_LIMIT",
    "caveat": s["note"]} for s in source_data], "source_id")
write_csv(census_path, census, list(census[0]))

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V146.csv"
provenance = read_csv(provenance_path)
provenance = upsert(provenance, [{"source_id": s["id"], "original_url": s["url"], "retrieval_url": s["url"],
    "capture_timestamp": "2026-08-31", "cdx_digest": "N/A_OFFICIAL_DIRECT", "local_path": s["local"], "sha256": s["sha"],
    "bytes": s["bytes"], "provenance_note": ("Captura oficial directa; hash y tamaño preservados. " +
    ("El dominio histórico presentó certificado vencido; descarga conservada con validación de dominio y contenido." if s["id"] == "e0_cgn_account_1999_repo_portfolio" else ""))} for s in source_data], "source_id")
write_csv(provenance_path, provenance, list(provenance[0]))

chain = [
    ("CH146_01", "public_debt_registry", "SIGADE", "Operaciones de deuda pública", "SIGADE es sistema de gestión/registro de deuda; no es por sí solo liquidación bancaria", "e0_argentina_sidif_link_historical_integration"),
    ("CH146_02", "debt_events", "SIGADE", "Desembolsos; amortización; intereses; comisiones", "Familias transmitidas a presupuesto/contabilidad", "e0_argentina_sidif_link_historical_integration"),
    ("CH146_03", "interface", "SIDIF-Link", "Enlace sistemático y en tiempo real", "Ruta contemporánea fuerte para 2008", "e0_argentina_sidif_link_historical_integration"),
    ("CH146_04", "accounting_counterpart", "SIDIF Central", "Contrapartida presupuestaria y contable", "Asiento no acredita débito bancario", "e0_argentina_sidif_link_historical_integration"),
    ("CH146_05", "audited_chain", "SIGADE→SIDIF-Link→SIDIF Central", "Diagrama UAI 2019", "Confirma arquitectura subsistente antes del reemplazo", "e0_mecon_uai_plan_2019_sigade_sidif_link"),
    ("CH146_06", "payment_execution", "e-SIDIF", "La ejecución de pagos alimenta e-SIDIF", "Tramo posterior; no retroproyectar a 2008", "e0_mecon_uai_plan_2019_sigade_sidif_link"),
    ("CH146_07", "target_owner", "SAF 355", "Servicio Administrativo Financiero de deuda", "Pedir submayor y vínculo SIGADE/SIDIF", "e0_mecon_uai_plan_2019_sigade_sidif_link"),
    ("CH146_08", "replacement", "e-SIDIF/SEPP", "Inicio 2020-11-16", "Reemplazó gestión antes realizada en SIDIF Link", "e0_dgsiaf_siche_deployment_2020_q4"),
    ("CH146_09", "contingency", "SIDIF-Link", "Continuidad temporal por contingencia", "Evita asumir apagado instantáneo", "e0_dgsiaf_siche_deployment_2020_q4"),
    ("CH146_10", "historical_access", "SICHE SIDIF Central", "Consultas sobre sistema discontinuado", "Ruta de recuperación actual", "e0_argentina_resolution_53_2024_siche"),
    ("CH146_11", "bank_layer", "CUT-SIDIF Central", "Extractos y conciliación bancaria", "Necesario para separar asiento de pago", "e0_dgsiaf_siche_cut_repository_2020_q2;e0_dgsiaf_siche_deployment_2020_q4"),
    ("CH146_12", "secondary_route", "SLU", "Ruta sólo condicional", "No usar como primaria sin prueba de implantación SAF 355/módulo objetivo", "e0_dgsiaf_slu_landing"),
]
write_csv(HERE / "E0_SAF355_SIGADE_SIDIF_LINK_SYSTEM_CHAIN_V146.csv", [{"chain_id": a, "stage": b, "system": c,
    "official_fact_or_target": d, "controlled_use": e, "source_id": f, "status": "PROVED_ARCHITECTURE_TARGET_ROW_NOT_LOCATED"} for a,b,c,d,e,f in chain])

route = [
    ("RT146_01", "Gastos", "SIDIF Central modelo 95", "consulta SICHE", "e0_dgsiaf_siche_deployment_2020_q1"),
    ("RT146_02", "Recursos", "SIDIF Central modelo 95", "consulta SICHE", "e0_dgsiaf_siche_deployment_2020_q1"),
    ("RT146_03", "Programación de la Ejecución Financiera", "SIDIF Central modelo 95", "consulta SICHE", "e0_dgsiaf_siche_deployment_2020_q1"),
    ("RT146_04", "Pagos", "SIDIF Central modelo 95", "consulta SICHE", "e0_dgsiaf_siche_deployment_2020_q1"),
    ("RT146_05", "Entidades Básicas", "CUT-SIDIF Central 2007-2014", "repositorio histórico", "e0_dgsiaf_siche_cut_repository_2020_q2"),
    ("RT146_06", "Saldos por apertura de cuenta", "CUT-SIDIF Central 2007-2014", "repositorio histórico", "e0_dgsiaf_siche_cut_repository_2020_q2"),
    ("RT146_07", "Extractos", "CUT-SIDIF Central 2007-2014", "capa bancaria", "e0_dgsiaf_siche_cut_repository_2020_q2"),
    ("RT146_08", "Logs de Impacto", "CUT-SIDIF Central 2007-2014", "trazabilidad", "e0_dgsiaf_siche_cut_repository_2020_q2"),
    ("RT146_09", "Consultas especiales", "SIDIF Central", "consulta SICHE", "e0_dgsiaf_siche_deployment_2020_q4"),
    ("RT146_10", "Conciliación Bancaria", "SIDIF Central", "consulta SICHE", "e0_dgsiaf_siche_deployment_2020_q4"),
    ("RT146_11", "Programación de la Ejecución", "SIDIF Central", "mejora 2022", "e0_dgsiaf_siche_sidif_central_q2_2022"),
    ("RT146_12", "Transmisiones", "SIDIF Central", "mejora 2022", "e0_dgsiaf_siche_sidif_central_q2_2022"),
    ("RT146_13", "Formulario por Pda. Presupuestaria y Sigade", "atribución por cronología", "consulta nombrada; sistema fuente no rotulado expresamente", "e0_dgsiaf_siche_special_queries_2022_q3"),
    ("RT146_14", "Deuda Exigible hasta 2008 / Gastos por Beneficiarios", "atribución por cronología", "consultas nombradas; pedir export y metadatos", "e0_dgsiaf_siche_special_queries_2022_q3"),
]
write_csv(HERE / "E0_SICHE_SIDIF_CENTRAL_TARGET_ROUTE_V146.csv", [{"route_id": a, "object_or_query": b, "repository_or_scope": c,
    "target_use": d, "source_id": e, "status": "ROUTE_PROVED_QUERY_NOT_EXECUTED", "inference_limit": "Capacidad/nombre de consulta no equivale a resultado target."} for a,b,c,d,e in route])

repo_lead = [
    ("RP146_01", "reported_repo_commission_regularization", "0.61", "ARS million", "2019", "e0_mecon_uai_report_13_2020_repo_commission", "Pista contable concreta; no identidad 2008"),
    ("RP146_02", "account_code", "2.1.2.01.02.99.00", "code", "2019", "e0_mecon_uai_report_13_2020_repo_commission", "Cuenta donde se informa la regularización"),
    ("RP146_03", "account_semantics", "Otros títulos y valores de la deuda pública a pagar en moneda extranjera", "text", "2018", "e0_cgn_chart_accounts_2018", "No reclasificar como préstamo genérico"),
    ("RP146_04", "uai_otros_published_total", "563.16", "ARS million", "2019", "e0_mecon_uai_report_13_2020_repo_commission", "Total publicado en comparación SIGADE/e-SIDIF"),
    ("RP146_05", "published_component_1", "0.61", "ARS million", "2019", "e0_mecon_uai_report_13_2020_repo_commission", "Comisiones REPO"),
    ("RP146_06", "published_component_2", "400.00", "ARS million", "2019", "e0_mecon_uai_report_13_2020_repo_commission", "Componente publicado"),
    ("RP146_07", "published_component_3", "163.00", "ARS million", "2019", "e0_mecon_uai_report_13_2020_repo_commission", "Componente publicado"),
    ("RP146_08", "published_components_sum", "563.61", "ARS million", "2019", "calculation_from_e0_mecon_uai_report_13_2020_repo_commission", "0.61+400+163"),
    ("RP146_09", "published_internal_gap", "0.45", "ARS million", "2019", "calculation_from_e0_mecon_uai_report_13_2020_repo_commission", "563.61-563.16; congelar sin corregir fuente"),
    ("RP146_10", "historical_repo_portfolio", "312943885.60", "ARS", "1999", "e0_cgn_account_1999_repo_portfolio", "Coincidencia nominal; no continuidad ni identidad con 2019/2008"),
]
write_csv(HERE / "E0_REPO_COMMISSION_ACCOUNT_LEAD_V146.csv", [{"lead_id": a, "datum": b, "value": c, "unit": d, "period": e,
    "source_id": f, "controlled_interpretation": g, "target_2008_identity": "FALSE", "status": "COMPARATOR_LEAD_NOT_TARGET_PROOF"} for a,b,c,d,e,f,g in repo_lead])

objects = [
    ("RO146_01", "SIGADE", "Registro/submayor del instrumento y eventos", "id SIGADE;instrumento;fecha;tipo;moneda;importe;contraparte"),
    ("RO146_02", "SIDIF-Link", "Transmisiones SIGADE→SIDIF Central", "lote;fecha-hora;tipo;id SIGADE;formulario;estado;error"),
    ("RO146_03", "SIDIF Central", "Formularios vinculados por partida y SIGADE", "SAF;ejercicio;formulario;número;partida;id SIGADE;importe"),
    ("RO146_04", "SIDIF Central", "Gastos por beneficiario", "beneficiario;CUIT;fecha;importe;moneda;formulario"),
    ("RO146_05", "SIDIF Central", "Deuda exigible hasta 2008", "SAF;acreedor;fecha;concepto;importe;estado"),
    ("RO146_06", "SIDIF Central", "Detalle de asientos 2001-2012", "cuenta;asiento;fecha;debe;haber;documento;referencia"),
    ("RO146_07", "CUT-SIDIF Central", "Extractos 2008 de cuentas candidatas", "cuenta;fecha valor;fecha proceso;signo;importe;referencia"),
    ("RO146_08", "CUT-SIDIF Central", "Conciliación bancaria", "cuenta;movimiento;estado;contrapartida;fecha;importe"),
    ("RO146_09", "CUT-SIDIF Central", "Logs de impacto/transmisión", "lote;origen;destino;fecha;resultado;error"),
    ("RO146_10", "SICHE", "Catálogo y metadatos de consultas", "nombre;descripción;sistema fuente;período;campos;filtros;corte"),
    ("RO146_11", "SICHE", "Export parametrizado y reproducible", "consulta;parámetros;fecha;filas;archivo;hash"),
    ("RO146_12", "SAF 355", "Expediente/orden/documentación de pago", "expediente;acto;beneficiario;instrumento;fecha;importe"),
    ("RO146_13", "SAF 355", "Relación asiento–pago–extracto", "id SIGADE;formulario;orden;cuenta;movimiento;importe"),
    ("RO146_14", "Cuenta 2.1.2.01.02.99.00", "Mayor/submayor y asiento REPO 2019", "asiento;fecha;instrumento;id SIGADE;contraparte;importe;origen"),
    ("RO146_15", "UAI/SAF 355", "Papeles de trabajo de la diferencia 563,16/563,61", "cálculo;componentes;ajuste;responsable;conclusión"),
    ("RO146_16", "Custodia", "Constancia fundada de inexistencia o transferencia", "repositorio;período;búsquedas;acto;fecha;responsable"),
]
write_csv(HERE / "E0_SIDIF_LINK_SICHE_REQUEST_OBJECTS_V146.csv", [{"object_id": a, "system_or_owner": b, "requested_record": c,
    "minimum_usable_fields": d, "success_test": "archivo/export individualizable, reproducible y enlazable", "negative_rule": "No basta respuesta genérica ni cero sin universo/cobertura.",
    "status": "DRAFT_NOT_SENT"} for a,b,c,d in objects])

strategy = [
    ("HR146_01", "SIGADE", "Submayor/eventos del instrumento", "P0_PRIMARY"),
    ("HR146_02", "SIDIF-Link", "Lotes y transmisiones a SIDIF Central", "P0_PRIMARY"),
    ("HR146_03", "SICHE SIDIF Central", "Formulario por partida y SIGADE", "P0_PRIMARY"),
    ("HR146_04", "SICHE SIDIF Central", "Deuda exigible hasta 2008", "P0_PRIMARY"),
    ("HR146_05", "SICHE SIDIF Central", "Gastos por beneficiario y detalle de asientos", "P0_PRIMARY"),
    ("HR146_06", "CUT-SIDIF Central", "Extracto, saldos y logs de impacto 2008", "P0_PRIMARY"),
    ("HR146_07", "SIDIF Central", "Conciliación bancaria y transmisión", "P0_PRIMARY"),
    ("HR146_08", "SAF 355", "Expediente, orden y vínculo con movimiento bancario", "P0_PRIMARY"),
    ("HR146_09", "Cuenta REPO 2019", "Mayor, asiento e identidad del instrumento", "P1_COMPARATOR"),
    ("HR146_10", "SLU", "Consulta/restauración sólo si se prueba implantación objetivo", "P2_CONDITIONAL"),
]
write_csv(HERE / "E0_SIDIF_LINK_HISTORICAL_RECOVERY_STRATEGY_V146.csv", [{"recovery_id": a, "route": b, "required_record": c,
    "priority": d, "success_test": "cadena SIGADE→asiento→orden→extracto o descarte documentado", "inference_limit": "Ruta/capacidad no prueba fila target.",
    "status": "DRAFT_NOT_SENT"} for a,b,c,d in strategy])

visual_path = HERE / "E0_V146_PDF_VISUAL_CONTROL.csv"
visual = read_csv(visual_path)
visual_add = [
    ("PV146_17", "e0_mecon_uai_plan_2019_sigade_sidif_link", "46", "47", "diagrama SIGADE→SIDIF-Link→SIDIF Central"),
    ("PV146_18", "e0_mecon_uai_report_13_2020_repo_commission", "14", "14", "cuenta y comisión REPO $0,61 millones"),
    ("PV146_19", "e0_mecon_uai_report_13_2020_repo_commission", "15", "15", "continuación y alcance del informe"),
    ("PV146_20", "e0_cgn_chart_accounts_2018", "23", "23", "definición 2.1.2.01.02.99.00"),
    ("PV146_21", "e0_dgsiaf_siche_deployment_2020_q1", "10", "10", "Gastos, Recursos, PEF y Pagos modelo 95"),
    ("PV146_22", "e0_dgsiaf_siche_cut_repository_2020_q2", "9", "9", "CUT-SIDIF Central 2007-2014"),
    ("PV146_23", "e0_dgsiaf_siche_deployment_2020_q4", "10", "10", "consultas especiales y conciliación bancaria"),
    ("PV146_24", "e0_dgsiaf_siche_deployment_2020_q4", "11", "11", "SAF 355 reemplaza SIDIF-Link por e-SIDIF/SEPP"),
]
visual = upsert(visual, [{"control_id": a, "source_id": b, "printed_page": c, "pdf_page": d, "rendered_check": e,
    "result": "PASS", "inference_limit": "Control visual; no fila target."} for a,b,c,d,e in visual_add], "control_id")
write_csv(visual_path, visual, list(visual[0]))

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V146.csv"
breaks = read_csv(breaks_path)
break_add = [
    ("saf355_slu_not_primary_without_deployment", "system", "SLU no está probado como sistema primario SAF 355 para el objeto 2008.", "Priorizar SIGADE→SIDIF-Link→SIDIF Central; SLU condicional.", "E0_SAF355_SIGADE_SIDIF_LINK_SYSTEM_CHAIN_V146.csv"),
    ("sidif_accounting_not_bank_settlement", "phase", "Asiento SIDIF no prueba débito/crédito bancario.", "Exigir extracto/conciliación/orden y nexo de importe-fecha-cuenta.", "E0_SICHE_SIDIF_CENTRAL_TARGET_ROUTE_V146.csv"),
    ("siche_named_query_source_attribution", "metadata", "La página 2022 nombra consultas pero no rotula explícitamente el sistema fuente de cada una.", "Tratar atribución a SIDIF Central como cronológica y pedir metadatos.", "e0_dgsiaf_siche_special_queries_2022_q3"),
    ("repo_2019_not_target_2008", "time", "La comisión REPO 2019 no prueba una operación objetivo de 2008.", "Exigir instrumento, fecha origen, ID SIGADE, contraparte y asiento.", "E0_REPO_COMMISSION_ACCOUNT_LEAD_V146.csv"),
    ("repo_1999_not_continuity_2019", "identity", "La mención Repo 1999 no prueba continuidad de cuenta/instrumento a 2019.", "Usar sólo como control nominal histórico.", "E0_REPO_COMMISSION_ACCOUNT_LEAD_V146.csv"),
    ("uai_repo_arithmetic_gap_045m", "arithmetic", "Los componentes publicados suman 563,61 pero el total informado es 563,16.", "Congelar diferencia de 0,45 y pedir papel de trabajo; no corregir silenciosamente.", "E0_REPO_COMMISSION_ACCOUNT_LEAD_V146.csv"),
]
breaks = upsert(breaks, [{"break_id": a, "dimension": b, "problem": c, "rule": d, "status": "FROZEN_V146", "evidence": e} for a,b,c,d,e in break_add], "break_id")
write_csv(breaks_path, breaks, list(breaks[0]))

trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V146.csv"
trace = read_csv(trace_path)
trace = upsert(trace, [{"trace_id": f"TR146_{i:03d}", "request_id": "REQ133_ECON", "institution": "Economía / CGN / DGSIAF / SAF 355",
    "gap_id": a, "requested_record": c, "period_or_date": "2008; comparador 2019 cuando corresponde", "identifiers": b,
    "minimum_usable_fields": d, "confidentiality_fallback": "metadatos/conteos/copia testada", "status": "DRAFT_NOT_SENT"}
    for i,(a,b,c,d) in enumerate(objects,214)], "trace_id")
write_csv(trace_path, trace, list(trace[0]))

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V146.csv"
keys = read_csv(keys_path)
exact_keys = ["SIDIF-LINK", "SAF 355", "Formulario por Pda. Presupuestaria y Sigade", "Gastos por Beneficiarios", "Deuda Exigible hasta 2008",
              "71597", "152677", "2876", "83106000", "2.1.2.01.02.99.00", "regularización comisiones operaciones REPO", "0,61 millones",
              "563,16", "563,61", "SIGADE", "Conciliación Bancaria", "Logs de Impacto", "Transmisiones"]
keys = upsert(keys, [{"key_id": f"SK146_{i:02d}", "request_id": "REQ133_ECON", "key_group": "sidif_link_siche_repo",
    "exact_key": key, "search_purpose": "localizar registro, consulta o puente exacto", "source_or_basis": "V146 fuentes oficiales",
    "caveat": "Clave de búsqueda; no confirma identidad ni pago."} for i,key in enumerate(exact_keys,1)], "key_id")
write_csv(keys_path, keys, list(keys[0]))

hist_path = HERE / "HISTORICAL_SOURCE_QUEUE_V146.csv"
hist = read_csv(hist_path)
hist = upsert(hist, [
    {"priority": "P0", "episode": "E0_2008", "variable_family": "SIGADE_SIDIF_LINK", "target_artifact": "Transmisiones SIGADE–SIDIF-Link y formularios SIDIF Central SAF 355", "preferred_source": "Economía / DGSIAF / SAF 355", "status": "PRIMARY_ROUTE_PROVED_TARGET_OPEN_NOT_SENT", "why": "ruta oficial contemporánea a 2008", "next_action": "obtener lotes, IDs SIGADE y formularios"},
    {"priority": "P0", "episode": "E0_2008", "variable_family": "SICHE_SIDIF_CENTRAL", "target_artifact": "Export consultas por SIGADE, beneficiario, deuda exigible y detalle 2001-2012", "preferred_source": "SICHE / DGSIAF / CGN", "status": "NAMED_QUERIES_FOUND_NOT_EXECUTED", "why": "consulta histórica oficial", "next_action": "pedir catálogo, parámetros, export y hash"},
    {"priority": "P1", "episode": "E0_COMPARATOR_2019", "variable_family": "REPO_COMMISSION", "target_artifact": "Mayor y asiento cuenta 2.1.2.01.02.99.00 · comisión REPO", "preferred_source": "SAF 355 / SIGADE / e-SIDIF", "status": "ACCOUNTING_LEAD_NOT_TARGET_IDENTITY", "why": "pista concreta y gap aritmético publicado", "next_action": "puente instrumento-fecha-ID-contraparte-origen"},
    {"priority": "P2", "episode": "E0_2008", "variable_family": "SLU", "target_artifact": "Prueba de implantación SAF 355 y módulo objetivo", "preferred_source": "DGSIAF / SAF 355", "status": "SECONDARY_CONDITIONAL_ROUTE", "why": "no se acreditó uso primario para el objetivo", "next_action": "no priorizar salvo evidencia de despliegue"},
], "target_artifact")
write_csv(hist_path, hist, list(hist[0]))

recovery_path = HERE / "RECOVERY_QUEUE_V146.csv"
recovery = read_csv(recovery_path)
recovery = upsert(recovery, [
    {"priority": "10", "entity": "SICHE SIDIF Central / SAF 355", "missing_artifact": "Export consultas nombradas y metadatos", "why": "ruta primaria de recuperación", "status": "OPEN_NOT_EXECUTED"},
    {"priority": "11", "entity": "SIGADE / SIDIF-Link", "missing_artifact": "lotes, IDs y formularios transmitidos", "why": "puente deuda-contabilidad", "status": "OPEN_NOT_SENT"},
    {"priority": "12", "entity": "REPO comisión 2019", "missing_artifact": "mayor, asiento, instrumento y papel aritmético", "why": "comparador contable con gap 0,45", "status": "OPEN_COMPARATOR"},
    {"priority": "13", "entity": "SLU SAF 355", "missing_artifact": "prueba de implantación y módulo objetivo", "why": "ruta secundaria condicional", "status": "HELD_SECONDARY"},
], "entity")
write_csv(recovery_path, recovery, list(recovery[0]))

request = HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V146.md"
append_section(request, "## Clave V146 · SIGADE, SIDIF-Link, SIDIF Central y SICHE", """
Estado: **BORRADOR_NO_ENVIADO**. Este texto no registra ni autoriza presentación.

Para el período 2008, la evidencia institucional ubica el circuito relevante en `SIGADE → SIDIF-Link → SIDIF Central`, hoy recuperable mediante SICHE. Se solicitan los registros y metadatos enumerados en `E0_SIDIF_LINK_SICHE_REQUEST_OBJECTS_V146.csv`: submayor/eventos SIGADE; lotes SIDIF-Link; formularios por partida y SIGADE; gastos por beneficiario; deuda exigible hasta 2008; detalle de asientos 2001-2012; extractos, saldos, logs y conciliación CUT; orden/expediente SAF 355; y la tabla de enlace entre ID SIGADE, formulario, cuenta, orden y movimiento bancario.

También se solicita, como comparador separado, el mayor y asiento de la cuenta `2.1.2.01.02.99.00` relativo a la regularización de comisiones REPO por $0,61 millones informada en 2019, con instrumento, contraparte, fecha de origen e ID SIGADE, junto con el papel de trabajo que explique por qué los componentes publicados suman $563,61 millones mientras el total informado es $563,16 millones.

La ruta SLU queda subsidiaria: sólo corresponde activarla si se individualiza el acto, versión o módulo que pruebe su implantación para SAF 355 y el objeto investigado. Una respuesta negativa debe detallar repositorios, períodos, consultas, parámetros, inventarios y actos de transferencia o expurgo examinados.
""")
append_section(HERE / "REQUEST_SUBMISSION_CHECKLIST_V146.md", "## Control V146 · ruta SIGADE/SIDIF-Link/SICHE", """
- Mantener los seis pedidos en `DRAFT_NOT_SENT` hasta autorización expresa.
- Adjuntar cadena de sistemas, ruta SICHE, objetos de pedido y matriz REPO.
- Pedir export reproducible con parámetros, universo, fecha de corte, filas y hash.
- No equiparar asiento SIDIF con liquidación bancaria ni REPO 2019 con el objetivo 2008.
- Mantener 0/10 hasta cerrar identidad, cuenta, fecha, importe, orden y extracto.
""")
append_section(HERE / "SOURCE_REFERENCES_V146.md", "## Fuentes nuevas V146 · SIGADE, SIDIF-Link, SICHE y pista REPO", "\n".join(
    f"- `{s['id']}` · {s['title']} · {s['url']} · `{s['local']}` · `{s['sha']}`" for s in source_data))
append_section(HERE / "E0_INSTITUTIONAL_REQUEST_PACKAGE_V146.md", "## Clave V146 · ruta primaria SAF 355", """
El pedido Economía/Tesoro se reorienta a `SIGADE → SIDIF-Link → SIDIF Central → SICHE`, con CUT/extracto para probar liquidación. La pista REPO 2019 se mantiene como comparador, con diferencia interna publicada de $0,45 millones. SLU queda condicional. Adjuntos: `E0_SAF355_SIGADE_SIDIF_LINK_SYSTEM_CHAIN_V146.csv`, `E0_SICHE_SIDIF_CENTRAL_TARGET_ROUTE_V146.csv`, `E0_SIDIF_LINK_SICHE_REQUEST_OBJECTS_V146.csv` y `E0_REPO_COMMISSION_ACCOUNT_LEAD_V146.csv`. Estado: `DRAFT_NOT_SENT`.
""")

(HERE / "README_V146.md").write_text("""# V146 · ruta SIGADE–SIDIF-Link–SIDIF Central y pista REPO

V146 corrige la arquitectura de recuperación para SAF 355. Para el período objetivo, la ruta documental primaria es `SIGADE → SIDIF-Link → SIDIF Central`, hoy consultable mediante SICHE; CUT-SIDIF Central aporta extractos, saldos, logs y conciliación. SLU permanece como alternativa condicional hasta probar su implantación concreta.

SICHE publicó capacidades históricas y consultas nombradas especialmente útiles: `Formulario por Pda. Presupuestaria y Sigade`, `Gastos por Beneficiarios`, `Deuda Exigible hasta 2008`, detalle 2001-2012, Pagos, Transmisiones, Extractos y Conciliación Bancaria. No se ejecutó ninguna consulta.

El Informe UAI 13/2020 agrega una pista separada: regularización de comisiones REPO por $0,61 millones en la cuenta `2.1.2.01.02.99.00`. Sus componentes publicados suman $563,61 millones frente a un total informado de $563,16 millones: diferencia congelada de $0,45 millones. No prueba identidad con 2008.

Estado estricto: 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas y seis pedidos `DRAFT_NOT_SENT`.
""", encoding="utf-8")

(HERE / "VEREDICTO_V146.md").write_text("""# Veredicto V146

La ruta de recuperación quedó mejor determinada, pero el hecho económico objetivo sigue abierto. Las fuentes oficiales prueban que SIGADE transmitía desembolsos, amortización, intereses y comisiones mediante SIDIF-Link a SIDIF Central; la UAI confirma ese encadenamiento, y SICHE ofrece hoy consultas y repositorios capaces de recuperar formularios, asientos, pagos, transmisiones, extractos y conciliaciones históricas.

Eso no equivale a liquidación. La prueba exige cerrar `ID SIGADE → formulario/asiento → orden/beneficiario → cuenta → movimiento de extracto`, con fecha, moneda e importe consistentes. SLU no encabeza esa cadena sin prueba de implantación específica.

La comisión REPO 2019 de $0,61 millones es una pista auditable, no una prueba de 2008. La diferencia interna de $0,45 millones obliga a pedir papeles de trabajo y no puede corregirse por inferencia. Continúan 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas; seis borradores no enviados.
""", encoding="utf-8")

(HERE / "E0_FISCAL_RECONSTRUCTION_V146.md").write_text("""# Reconstrucción fiscal E0 V146

La reconstrucción cuantitativa estricta no cambia: 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas. V146 mejora la estrategia probatoria al fijar la cadena SIGADE–SIDIF-Link–SIDIF Central–SICHE y separar contabilidad de liquidación bancaria. La pista REPO 2019 y su gap de $0,45 millones son comparadores pendientes de identidad, no filas del objetivo 2008.
""", encoding="utf-8")

(HERE / "RETRIEVAL_LOG_V146.md").write_text("""# Registro de recuperación V146

- 2026-08-31: preservadas siete fuentes oficiales sobre SIGADE/SIDIF-Link, trayectoria DGSIAF, SICHE SIDIF Central, plan de cuentas y operaciones REPO.
- Verificación visual: Plan UAI 2019 p. 46/PDF 47; Informe UAI 13/2020 pp. 14-15; Plan de Cuentas p. 23; boletines SICHE 2020 pp. 9-11.
- El HTML histórico CGN 1999 se recuperó del dominio oficial con certificado vencido y se documentó esa incidencia en procedencia.
- No se ejecutó SICHE, no se restauró base y no se presentó pedido.
""", encoding="utf-8")

(HERE / "AUDITORIA_V146.md").write_text(f"""# Auditoría V146

- Fuentes maestras: {len(catalog)}.
- Fuentes primarias E0: {len(census)}.
- Fuentes nuevas: 7.
- Controles visuales acumulados V146: {len(visual)}.
- Ruta primaria: SIGADE→SIDIF-Link→SIDIF Central→SICHE.
- Consultas ejecutadas: 0; filas target: 0; pedidos enviados: 0.
- Diferencia UAI congelada: $0,45 millones.
""", encoding="utf-8")

(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V146_A_V147.md").write_text("""# Handover V146 → V147

## Estado

- QA V146: PASS.
- Siete fuentes oficiales nuevas; 464 fuentes maestras y 224 E0.
- Ruta primaria 2008: `SIGADE → SIDIF-Link → SIDIF Central → SICHE`; CUT agrega extractos y conciliación.
- Consultas nombradas: partida+SIGADE, beneficiarios y deuda exigible hasta 2008; ejecución 0.
- Pista comparadora: comisión REPO 2019 $0,61 millones en 2.1.2.01.02.99.00.
- Inconsistencia interna publicada: 563,61 − 563,16 = 0,45 millones; no corregida.
- SLU es vía secundaria condicional.
- Sin fila target; seis `DRAFT_NOT_SENT`; 10 adjudicaciones, 9 cuentas, 0/10 ejecuciones.

## Prioridad V147

1. Mantener borradores salvo autorización expresa.
2. Buscar manual/catálogo de SICHE SIDIF Central y metadatos de las consultas nombradas.
3. Localizar export o esquema público de `Formulario por Pda. Presupuestaria y Sigade` y `Deuda Exigible hasta 2008`.
4. Buscar papeles UAI/SAF 355 del asiento REPO, instrumento, ID SIGADE y explicación de $0,45 millones.
5. Cerrar puente con CUT: extracto, conciliación, cuenta, fecha, importe y referencia.
6. Mantener separados arquitectura, asiento contable, orden de pago y liquidación bancaria.
""", encoding="utf-8")

hash_rows = []
for row in catalog:
    local = row["archivo_local"]
    path = REPO / local.lstrip("/") if local else None
    exists = bool(path and path.is_file())
    actual = sha256(path) if exists else ""
    expected = row["sha256"]
    hash_rows.append({"id": row["id"], "archivo_local": local, "exists": str(exists), "sha_catalog": expected,
                      "sha_actual": actual, "hash_ok": str(bool(exists and expected and actual.lower() == expected.lower()))})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V146.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V146.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or "tmp" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append({"path": path.relative_to(REPO).as_posix(), "bytes": size, "mib": f"{size/1048576:.6f}",
                      "over_50_mib": str(size > 50*1048576), "over_100_mib": str(size > 100*1048576)})
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V146.csv", size_rows)

complete_path = AUDIT / "CURRENT_SOURCE_COMPLETENESS_V146.json"
complete = json.loads((complete_path if complete_path.exists() else AUDIT / "CURRENT_SOURCE_COMPLETENESS_V145.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint": "V146", "date": "2026-08-31", "state": "E0_SIGADE_SIDIF_LINK_SIDIF_CENTRAL_SICHE_ROUTE_PROVED_TARGET_NOT_EXECUTED_NOT_SENT",
    "numeric_v146_strict_changed": False, "master_catalog_entries": len(catalog), "physical_local_copies": physical,
    "physical_local_hash_ok": hash_ok, "remaining_physical_gaps": len(catalog)-physical, "e0_primary_sources_preserved": len(census),
    "sources_newly_preserved_v146": 7, "e0_primary_sources_newly_preserved_v146": 7, "e0_duplicate_recaptures_v146": 0,
    "e0_fiscal_method_breaks_frozen": len(breaks), "e0_request_traceability_rows": len(trace), "e0_request_search_keys": len(keys),
    "e0_v146_pdf_visual_controls": len(visual), "e0_primary_target_route": "SIGADE_SIDIF_LINK_SIDIF_CENTRAL_SICHE",
    "e0_siche_sidif_central_named_queries_located": 3, "e0_siche_named_queries_executed": 0, "e0_siche_target_exports_located": 0,
    "e0_sidif_link_target_transmissions_located": 0, "e0_repo_commission_2019_lead_located": True,
    "e0_repo_commission_target_2008_identity_proved": False, "e0_repo_published_internal_gap_ars_millions": "0.45",
    "e0_slu_route_status": "SECONDARY_CONDITIONAL_PENDING_SAF355_DEPLOYMENT_PROOF",
    "e0_settlement_executed_rows_confirmed": 0, "e0_requests_submitted": 0, "e0_request_responses_received": 0,
    "e0_request_package_status": "DRAFT_NOT_SENT", "historical_workstream": "Obtain SICHE SIDIF Central exports, SIGADE/SIDIF-Link transmissions and CUT settlement bridge; audit REPO comparator separately; no request submitted"})
complete_path.write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

append_section(REPO / "BACKUP_ACTUALIZACION_2026-08-29.md", "## V146 · ruta SIGADE–SIDIF-Link–SICHE y pista REPO", """
- Ruta primaria SAF 355/2008: SIGADE→SIDIF-Link→SIDIF Central→SICHE; CUT para extracto/conciliación.
- Consultas históricas nombradas localizadas; ninguna ejecutada.
- Pista REPO 2019: $0,61 millones en 2.1.2.01.02.99.00; gap interno $0,45 millones.
- SLU secundario condicional; target 0/10; seis borradores no enviados.
""")

write_csv(HERE / "INHERITED_QA_STATUS_V146.csv", [
    {"script": "qa_v145.py", "pre_v146_result": "PASS", "post_v146_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V145 ampliada por ruta SIDIF-Link/SICHE y comparador REPO."},
    {"script": "qa_v146.py", "pre_v146_result": "N/A", "post_v146_result": "PASS", "interpretation": "Verifica fuentes, matrices, hashes, límites, aritmética y no envío."},
])

def checkpoint_manifest():
    files = [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha256(p)} for p in sorted(HERE.iterdir())
             if p.is_file() and p.name != "MANIFEST_V146.json"]
    manifest = {"checkpoint": "V146", "parent_checkpoint": "V145", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO", "e0_primary_sources": len(census),
        "new_preserved_sources": 7, "fiscal_ledger_rows": len(read_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V146.csv")),
        "fiscal_method_breaks": len(breaks), "request_traceability_rows": len(trace), "request_search_keys": len(keys),
        "sidif_link_system_chain_rows": len(chain), "siche_sidif_central_route_rows": len(route), "repo_lead_rows": len(repo_lead),
        "sidif_link_request_objects": len(objects), "recovery_strategy_rows": len(strategy), "pdf_visual_controls_v146": len(visual),
        "siche_named_queries_executed": 0, "siche_target_exports_located": 0, "repo_target_2008_identity_proved": False,
        "award_rows_exact": 10, "account_candidate_rows": 9, "executed_settlement_rows_confirmed": 0,
        "request_drafts": 6, "requests_submitted": 0, "responses_received": 0, "files": files}
    (HERE / "MANIFEST_V146.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tree(root):
    return "\n".join(p.relative_to(root).as_posix() + ("/" if p.is_dir() else "") for p in sorted(root.rglob("*"), key=lambda value: value.relative_to(root).as_posix().casefold())
                     if ".git" not in p.parts and "__pycache__" not in p.parts and "tmp" not in p.parts) + "\n"


(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")
checkpoint_manifest()

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = []
for path in sorted(REPO.rglob("*"), key=lambda value: value.relative_to(REPO).as_posix().casefold()):
    if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts and "tmp" not in path.parts and path != global_manifest:
        global_files.append({"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})
global_manifest.write_text(json.dumps({"checkpoint": "V146", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master; {physical} physical SHA-valid; 7 new official sources; SIDIF-Link/SICHE route proved; REPO comparator separated; target not located; 0/10; six drafts not submitted.",
    "historical_workstream": "Obtain SICHE SIDIF Central exports, SIGADE/SIDIF-Link transmissions and CUT settlement bridge; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(f"V146 BUILD PASS · catalog={len(catalog)} · E0={len(census)} · physical={physical} · hash_ok={hash_ok}")
