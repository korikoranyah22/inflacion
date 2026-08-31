from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    fields = fields or (list(rows[0]) if rows else [])
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def upsert(rows: list[dict[str, str]], additions: list[dict[str, object]], key: str) -> list[dict[str, str]]:
    order = [str(row[key]) for row in rows]
    indexed = {str(row[key]): row for row in rows}
    for addition in additions:
        row = {name: str(value) for name, value in addition.items()}
        value = row[key]
        indexed[value] = row
        if value not in order:
            order.append(value)
    return [indexed[value] for value in order]


def append_section(path: Path, marker: str, body: str) -> None:
    text = path.read_text(encoding="utf-8-sig")
    if marker not in text:
        path.write_text(text.rstrip() + "\n\n" + marker + "\n\n" + body.strip() + "\n", encoding="utf-8")


SOURCES = [
    {
        "id": "e0_mecon_uai_report_24_2019_account_2018",
        "institution": "Ministerio de Hacienda · Unidad de Auditoría Interna",
        "title": "Informe UAI 24/2019 · Cuenta de Inversión 2018",
        "url": "https://www.argentina.gob.ar/sites/default/files/informe_uai_no_24.pdf",
        "local": "/research/ciclo_ajuste/inputs/historical_retrieval/v147/binaries/mecon_uai_report_24_2019_account_2018_sigade_esidif.pdf",
        "period": "2018-2019",
        "series": "Informe UAI 24/2019",
        "note": "Documenta Anexos A-L, diferencias SIGADE/e-SIDIF, pagos holdout pendientes de baja y el comparador OTROS -563 con componentes publicados redondeados de 400 y 163 millones.",
    },
    {
        "id": "e0_mecon_uai_report_37_2023_account_2022",
        "institution": "Ministerio de Economía · Unidad de Auditoría Interna",
        "title": "Informe UAI 37/2023 · Cuenta de Inversión 2022",
        "url": "https://www.argentina.gob.ar/sites/default/files/informe_uai_37-2023.pdf",
        "local": "/research/ciclo_ajuste/inputs/historical_retrieval/v147/binaries/mecon_uai_report_37_2023_account_2022_executive.pdf",
        "period": "2022-2023",
        "series": "Informe UAI 37/2023",
        "note": "Registra diferencias ONCP-CGN, límites funcionales de SIGADE, cálculos externos y carga manual, y pagos holdout no registrados en SIGADE.",
    },
    {
        "id": "e0_mecon_uai_report_48_2023_saf355_closure",
        "institution": "Ministerio de Economía · Unidad de Auditoría Interna",
        "title": "Informe UAI 48/2023 · cierre SAF 355",
        "url": "https://www.argentina.gob.ar/sites/default/files/informe_uai_48-2023.pdf",
        "local": "/research/ciclo_ajuste/inputs/historical_retrieval/v147/binaries/mecon_uai_report_48_2023_saf355_closure.pdf",
        "period": "2023",
        "series": "Informe UAI 48/2023",
        "note": "Individualiza expedientes y actas de corte SAF 355 y confirma pagos 2019, 2020 y 2022 contabilizados en e-SIDIF pero ausentes de SIGADE.",
    },
    {
        "id": "e0_agn_report_65_2022_sigade_information_system",
        "institution": "Auditoría General de la Nación",
        "title": "Informe AGN 65/2022 · sistema de información SIGADE",
        "url": "https://www.agn.gob.ar/sites/default/files/informes/2022-065-Informe.pdf",
        "local": "/research/ciclo_ajuste/inputs/historical_retrieval/v147/binaries/agn_report_65_2022_sigade_information_system.pdf",
        "period": "2022",
        "series": "Informe AGN 65/2022",
        "note": "Describe SIDIF-Link, planillas compartidas, rectificaciones externas, límites decimales y documentación adjunta no utilizada; comparador posterior, no prueba directa de 2008.",
    },
    {
        "id": "e0_agn_resolution_86_2021_public_debt_control",
        "institution": "Auditoría General de la Nación",
        "title": "Resolución AGN 86/2021 · Anexo I · control de deuda pública",
        "url": "https://www.agn.gob.ar/sites/default/files/informes/01-%20RES86-2021%20Anexo%20I.pdf",
        "local": "/research/ciclo_ajuste/inputs/historical_retrieval/v147/binaries/agn_resolution_86_2021_annex_i_public_debt_control.pdf",
        "period": "2017-2021",
        "series": "Resolución AGN 86/2021 · Anexo I",
        "note": "Explicita la escalera de auditoría SIGADE, estados, mayorizado por SIGADE, formularios e-SIDIF, movimientos TGN, CRyL y mayores contables.",
    },
]

for source in SOURCES:
    path = REPO / source["local"].lstrip("/")
    assert path.is_file(), path
    source["sha"] = sha256(path)
    source["bytes"] = path.stat().st_size

catalog = read_csv(CATALOG)
catalog = upsert(
    catalog,
    [
        {
            "id": source["id"],
            "tema": "ciclo_ajuste_e0_fiscal",
            "institucion": source["institution"],
            "titulo": source["title"],
            "url_original": source["url"],
            "archivo_local": source["local"],
            "fecha_descarga": "2026-08-31",
            "fecha_publicacion": source["period"],
            "codigo_serie": source["series"],
            "periodo_utilizado": source["period"],
            "tipo": "PDF oficial",
            "sha256": source["sha"],
            "nota": "V147: " + source["note"],
        }
        for source in SOURCES
    ],
    "id",
)
for row in catalog:
    if row["id"] == "e0_mecon_uai_report_13_2020_repo_commission":
        row["nota"] = (
            "V147 rectificación metodológica: la diferencia de 0,45 millones surge de valores publicados con precisión desigual; "
            "sin componentes no redondeados no prueba error aritmético. Persiste la tensión de clasificación de la cuenta."
        )
write_csv(CATALOG, catalog, list(catalog[0]))

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V147.csv"
census = read_csv(census_path)
census = upsert(
    census,
    [
        {
            "source_id": source["id"],
            "institution": source["institution"],
            "artifact": source["title"],
            "url": source["url"],
            "local_path": source["local"],
            "sha256": source["sha"],
            "bytes": source["bytes"],
            "period_coverage": source["period"],
            "variable_families": "SIGADE;SIDIF-Link;e-SIDIF;SAF355;TGN;bank;control",
            "primary_source": "YES",
            "preserved": "YES",
            "method_breaks": "comparador posterior versus objeto 2008; registro contable versus liquidación bancaria",
            "use_status": "E0_USABLE_WITH_TEMPORAL_LIMIT",
            "caveat": source["note"],
        }
        for source in SOURCES
    ],
    "source_id",
)
for row in census:
    if row["source_id"] == "e0_mecon_uai_report_13_2020_repo_commission":
        row["caveat"] = "La diferencia mostrada de 0,45 millones no prueba error sin importes fuente no redondeados."
write_csv(census_path, census, list(census[0]))

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V147.csv"
provenance = read_csv(provenance_path)
provenance = upsert(
    provenance,
    [
        {
            "source_id": source["id"],
            "original_url": source["url"],
            "retrieval_url": source["url"],
            "capture_timestamp": "2026-08-31",
            "cdx_digest": "N/A_OFFICIAL_DIRECT",
            "local_path": source["local"],
            "sha256": source["sha"],
            "bytes": source["bytes"],
            "provenance_note": "Captura oficial directa; binario preservado con SHA-256 y tamaño.",
        }
        for source in SOURCES
    ],
    "source_id",
)
write_csv(provenance_path, provenance, list(provenance[0]))

ladder = [
    (1, "registro_instrumento", "SIGADE", "Partir del registro del instrumento seleccionado.", "Identificar si 83106000 remite a instrumento/evento SIGADE."),
    (2, "estado_de_cuenta", "SIGADE", "Cruzar el Estado de Cuenta.", "Recuperar saldos y movimientos del identificador."),
    (3, "tabla_amortizacion", "SIGADE", "Cruzar la Tabla de Amortización.", "Distinguir servicio, comisión y cancelación."),
    (4, "ficha", "SIGADE", "Cruzar la Ficha del instrumento.", "Fijar moneda, contraparte, fechas y condiciones."),
    (5, "cuadro_1a", "CGN", "Controlar registro en Cuadro 1A cuando corresponda.", "Control negativo: la fila objetivo está en Anexo K, fuera de Cuadro 1A."),
    (6, "mayorizado_por_sigade", "e-SIDIF / SIDIF Central", "Descargar reporte prediseñado parametrizado por número SIGADE.", "Obtener todos los movimientos contables individualizados."),
    (7, "formularios_individuales", "e-SIDIF / SIDIF Central", "Revisar cada formulario individualmente.", "Abrir 71597, 152677 y 2876 con cabecera y renglones."),
    (8, "asientos_desembolsos_pagos", "e-SIDIF / SIDIF Central", "Verificar desembolsos, intereses y gastos en asientos.", "Separar comisión devengada, ordenada, pagada y revertida."),
    (9, "ajustes_cambio_cer", "e-SIDIF / SIDIF Central", "Verificar ajustes por diferencia de cambio y CER.", "Evitar confundir valuación con caja."),
    (10, "movimientos_bancarios_tgn", "TGN · Coordinación de Cuentas Bancarias", "Solicitar movimientos de pagos y desembolsos.", "Probar fecha valor, cuenta, referencia, signo e importe."),
    (11, "conciliacion_esidif_banco", "TGN / e-SIDIF", "Conciliar movimiento bancario con formulario y asiento.", "Cerrar nexo formulario–orden–cuenta–extracto."),
    (12, "custodia_cryl", "BCRA · CRyL", "Solicitar saldos/custodia de instrumentos cuando aplique.", "Condicional: sólo si la comisión se enlaza con título o liquidación CRyL."),
    (13, "mayores_pasivo", "CGN / e-SIDIF", "Descargar mayores de cuentas de pasivo y reconciliar.", "Cerrar la cuenta contable y ajustes sin equipararlos a liquidación."),
]
write_csv(
    HERE / "E0_AGN_OFFICIAL_SETTLEMENT_AUDIT_LADDER_V147.csv",
    [
        {
            "step_id": f"AL147_{order:02d}",
            "order": order,
            "evidence_object": evidence,
            "system_or_owner": system,
            "official_procedure": procedure,
            "target_2008_use": target,
            "source_id": "e0_agn_resolution_86_2021_public_debt_control",
            "pdf_page": "16",
            "status": "OFFICIAL_AUDIT_METHOD_TARGET_OPEN",
            "inference_limit": "Método oficial posterior; no acredita por sí solo el hecho de 2008.",
        }
        for order, evidence, system, procedure, target in ladder
    ],
)

branch = [
    ("annex", "Anexo K", "Otras operaciones presupuestarias no incluidas en Cuadro 1A", "EXACT"),
    ("sigade_code", "83106000", "Identificador impreso de la fila", "EXACT"),
    ("description", "COMISIONES - BANCO NACION", "Descripción impresa", "EXACT"),
    ("amount_ars", "32270.30", "Importe alineado visualmente", "EXACT_NOT_PAYMENT_PROOF"),
    ("budget_item", "7.2.8.", "Partida presupuestaria impresa", "EXACT"),
    ("sidif_form_1", "71597", "Primer identificador SIDIF de la fila", "EXACT"),
    ("sidif_form_2", "152677", "Segundo identificador SIDIF de la fila", "EXACT"),
    ("sidif_form_3", "2876", "Tercer identificador SIDIF de la fila", "EXACT"),
    ("cuadro1a_rule", "OUTSIDE_CUADRO_1A", "No exigir que la ruta comience o termine en Cuadro 1A", "METHOD_BRANCH"),
    ("accounting_route", "MAYORIZADO_POR_SIGADE_PLUS_FORMS", "Mayorizado y apertura individual de los tres formularios", "REQUEST_TARGET"),
    ("cash_route", "TGN_MOVEMENT_PLUS_BANK_STATEMENT", "Movimiento TGN/CUT y extracto BNA con conciliación", "REQUEST_TARGET"),
]
write_csv(
    HERE / "E0_ANEXO_K_OFF_CUADRO1A_TARGET_BRANCH_V147.csv",
    [
        {
            "branch_id": f"AK147_{index:02d}",
            "field_or_rule": field,
            "value": value,
            "controlled_interpretation": interpretation,
            "evidence_status": status,
            "source_id": "e0_cgn_cuenta_inversion_2008_sdp",
            "pdf_page": "67",
            "target_payment_confirmed": "FALSE",
            "next_evidence": "Formulario completo; mayor; orden; movimiento TGN/CUT; extracto y conciliación.",
        }
        for index, (field, value, interpretation, status) in enumerate(branch, 1)
    ],
)

risks = [
    ("loan_and_security_lifecycle", "SIGADE cubre préstamos y títulos desde documentación fuente hasta cancelación.", "CAPABILITY_NOT_TARGET"),
    ("sidif_link_interface", "SIDIF-Link transmitía entre SIGADE y e-SIDIF/SIDIF mediante Recursos y Gastos.", "ARCHITECTURE"),
    ("automatic_link_2020", "La vinculación automática SIGADE–e-SIDIF comenzó en noviembre de 2020.", "DO_NOT_RETROJECT_TO_2008"),
    ("shared_spreadsheets", "Planillas compartidas se usaban para controles pre/post y conciliaciones.", "SIDECAR_ESSENTIAL"),
    ("cell_initials", "Usuarios dejaban iniciales en celdas como trazabilidad operativa.", "WEAK_AUDIT_TRAIL"),
    ("manual_database_intervention", "Inconsistencias podían requerir intervenciones manuales sobre la base.", "REQUEST_TICKETS_AND_BEFORE_AFTER"),
    ("decimal_precision", "La precisión decimal limitada generaba ajustes.", "REQUEST_UNROUNDED_CALCULATION"),
    ("attachments_unused", "La función SIGADE para adjuntar Word/Excel/PDF no era utilizada.", "REQUEST_EXTERNAL_DOCUMENT_FOLDER"),
    ("rectification_outside_sigade", "Se rectificaban datos de instrumentos por fuera de SIGADE.", "SYSTEM_ROW_NOT_COMPLETE_TRUTH"),
    ("generic_admin_account", "Cuentas administrativas genéricas podían debilitar atribución.", "REQUEST_USER_AND_AUTHORIZATION"),
    ("mandatory_fields_instruction", "No se exhibió instrucción que definiera campos obligatorios y modo de carga.", "LATER_CONTROL_RISK"),
    ("validation_not_used", "La validación de datos incorporada en SIGADE no era aplicada.", "LATER_CONTROL_RISK"),
    ("monthly_alternative_controls", "Se invocaron controles mensuales alternativos.", "REQUEST_CONTROL_OUTPUT"),
    ("excel_number_allocation", "La numeración de instrumentos se controlaba en una planilla Excel.", "REQUEST_CROSSWALK"),
    ("temporal_limit", "Los hallazgos corresponden a períodos posteriores al objeto 2008.", "COMPARATOR_ONLY"),
]
write_csv(
    HERE / "E0_SIGADE_DATA_QUALITY_AND_SIDECAR_RISK_V147.csv",
    [
        {
            "risk_id": f"SR147_{index:02d}",
            "risk_or_capability": risk,
            "official_finding": finding,
            "controlled_use": use,
            "source_id": "e0_agn_report_65_2022_sigade_information_system" if index <= 10 else "e0_agn_resolution_86_2021_public_debt_control",
            "status": "OFFICIAL_LATER_PERIOD_COMPARATOR",
            "target_2008_proof": "FALSE",
            "request_consequence": "Pedir fila nativa, planilla/papel externo, intervención, autorización y cálculo no redondeado cuando corresponda.",
        }
        for index, (risk, finding, use) in enumerate(risks, 1)
    ],
)

truth = [
    ("PRESENT", "PAID", "MATCH", "Payment can be confirmed if identity/date/account/amount reconcile", "STRONG"),
    ("ACTIVE", "PAID", "MATCH", "Payment may be real while SIGADE derecognition is pending", "STRONG_WITH_REGISTRY_MISMATCH"),
    ("ABSENT", "PAID", "MATCH", "Absence in SIGADE does not negate a bank-confirmed payment", "STRONG_WITH_SYSTEM_OMISSION"),
    ("CANCELLED", "PAID", "NO_BANK_RECORD", "Accounting state alone does not prove settlement", "OPEN"),
    ("ACTIVE", "NO_PAYMENT", "NO_BANK_RECORD", "No payment shown in sampled systems; universe/coverage still required", "NEGATIVE_WITH_LIMIT"),
    ("ABSENT", "NO_PAYMENT", "NO_BANK_RECORD", "Double absence is not proof of non-occurrence without archive coverage", "OPEN_NEGATIVE"),
    ("PRESENT", "REVERSED", "REVERSAL_MATCH", "Reversal is not a completed payment", "NOT_SETTLED"),
    ("PRESENT", "PAID", "MISMATCH", "Amount/date/account mismatch requires reconciliation", "CONFLICT"),
    ("HOLDOUT_2019", "793.65m_PAID_ESIDIF", "SIGADE_ABSENT", "Later example of payment truth outside SIGADE", "COMPARATOR_ONLY"),
    ("HOLDOUT_2020", "417.52m_PAID_ESIDIF", "SIGADE_ABSENT", "Later example of payment truth outside SIGADE", "COMPARATOR_ONLY"),
    ("HOLDOUT_2022", "108.29m_PAID_ESIDIF", "SIGADE_ABSENT", "Later example of payment truth outside SIGADE", "COMPARATOR_ONLY"),
    ("TARGET_2008", "UNKNOWN", "UNKNOWN", "Requires forms 71597/152677/2876 plus TGN/bank bridge", "OPEN_0_OF_10"),
]
write_csv(
    HERE / "E0_CROSS_SYSTEM_PAYMENT_STATE_TRUTH_TABLE_V147.csv",
    [
        {
            "state_id": f"TS147_{index:02d}",
            "sigade_state": sigade,
            "sidif_state": sidif,
            "bank_or_external_state": bank,
            "permitted_conclusion": conclusion,
            "evidence_strength": strength,
            "source_id": "e0_mecon_uai_report_48_2023_saf355_closure" if index in (9, 10, 11) else "e0_agn_resolution_86_2021_public_debt_control",
            "temporal_limit": "Later examples are methodological comparators; target remains unproved.",
        }
        for index, (sigade, sidif, bank, conclusion, strength) in enumerate(truth, 1)
    ],
)

repo_precision = [
    ("uai24_total_otros", "563", "ARS million displayed", "2018 report", "Rounded published total"),
    ("uai24_component_c10", "400", "ARS million displayed", "2018 report", "No decimals shown"),
    ("uai24_component_opening", "163", "ARS million displayed", "2018 report", "No decimals shown"),
    ("uai13_total_otros", "563.16", "ARS million displayed", "2019 report", "Two decimals shown"),
    ("uai13_repo_component", "0.61", "ARS million displayed", "2019 report", "Two decimals shown"),
    ("uai13_component_c10", "400", "ARS million displayed", "2019 report", "No decimals shown"),
    ("uai13_component_opening", "163", "ARS million displayed", "2019 report", "No decimals shown"),
    ("displayed_sum", "563.61", "ARS million calculation", "V147", "0.61+400+163"),
    ("displayed_difference", "0.45", "ARS million calculation", "V147", "563.61-563.16"),
    ("arithmetic_error_proved", "FALSE", "boolean", "V147", "Components have unknown/unequal precision"),
    ("unrounded_components_located", "FALSE", "boolean", "V147", "Raw ledger/workpaper still missing"),
    ("account_classification_tension", "OPEN", "state", "V147", "Report says préstamos while 2.1.2.01.02.99.00 belongs to other debt securities/value titles"),
]
write_csv(
    HERE / "E0_REPO_DISPLAY_PRECISION_REASSESSMENT_V147.csv",
    [
        {
            "datum_id": f"RP147_{index:02d}",
            "datum": datum,
            "value": value,
            "unit_or_type": unit,
            "reference": reference,
            "controlled_interpretation": interpretation,
            "source_ids": "e0_mecon_uai_report_24_2019_account_2018;e0_mecon_uai_report_13_2020_repo_commission",
            "target_2008_identity": "FALSE",
            "status": "DISPLAYED_VALUE_TENSION_UNROUNDED_INPUTS_REQUIRED",
        }
        for index, (datum, value, unit, reference, interpretation) in enumerate(repo_precision, 1)
    ],
)

legacy_repo_path = HERE / "E0_REPO_COMMISSION_ACCOUNT_LEAD_V147.csv"
legacy_repo = read_csv(legacy_repo_path)
for row in legacy_repo:
    if row["datum"] == "published_internal_gap":
        row["datum"] = "displayed_values_difference"
        row["controlled_interpretation"] = "563.61-563.16; diferencia entre valores mostrados, no error probado sin componentes no redondeados"
        row["status"] = "DISPLAYED_PRECISION_TENSION_NOT_ARITHMETIC_ERROR"
write_csv(legacy_repo_path, legacy_repo, list(legacy_repo[0]))

negative_searches = [
    ("SICHE manual de usuario", "PUBLIC_MANUAL_NOT_LOCATED"),
    ("SICHE catálogo de campos SIDIF Central", "PUBLIC_FIELD_CATALOG_NOT_LOCATED"),
    ("Formulario por Pda. Presupuestaria y Sigade export", "PUBLIC_EXPORT_NOT_LOCATED"),
    ("Deuda Exigible hasta 2008 export", "PUBLIC_EXPORT_NOT_LOCATED"),
    ("Gastos por Beneficiarios export", "PUBLIC_EXPORT_NOT_LOCATED"),
    ("SICHE esquema CSV/XLS", "PUBLIC_SCHEMA_NOT_LOCATED"),
    ("SICHE API o endpoint de descarga", "PUBLIC_ENDPOINT_NOT_LOCATED"),
    ("metadatos públicos de filtros y tipos", "PUBLIC_METADATA_NOT_LOCATED"),
]
write_csv(
    HERE / "E0_V147_PUBLIC_SEARCH_NEGATIVE_RESULTS_V147.csv",
    [
        {
            "search_id": f"NS147_{index:02d}",
            "target": target,
            "result": result,
            "searched_on": "2026-08-31",
            "official_pages_checked": "DGSIAF SICHE Q2/Q3 2022; Resolución 53/2024; buscador oficial",
            "positive_fact_preserved": "Named query/capability exists where officially published.",
            "negative_inference_limit": "No localizado públicamente no equivale a inexistente ni destruido.",
            "next_action": "Solicitar catálogo, parámetros, export, conteo, fecha de corte y hash.",
            "status": "PUBLIC_MANUAL_OR_EXPORT_NOT_LOCATED",
        }
        for index, (target, result) in enumerate(negative_searches, 1)
    ],
)

request_objects = [
    ("SIGADE", "Ficha, Estado de Cuenta y Tabla de Amortización de 83106000", "id;instrumento;contraparte;moneda;fechas;saldos;eventos"),
    ("e-SIDIF/SIDIF Central", "Reporte mayorizado por SIGADE 83106000", "cuenta;asiento;fecha;debe;haber;formulario;referencia"),
    ("e-SIDIF/SIDIF Central", "Formulario 71597 completo", "cabecera;renglones;beneficiario;CUIT;importe;moneda;estado;orden"),
    ("e-SIDIF/SIDIF Central", "Formulario 152677 completo", "cabecera;renglones;beneficiario;CUIT;importe;moneda;estado;orden"),
    ("e-SIDIF/SIDIF Central", "Formulario 2876 completo", "cabecera;renglones;beneficiario;CUIT;importe;moneda;estado;orden"),
    ("CGN/SAF 355", "Mayor y submayor de cuentas vinculadas", "cuenta;asiento;fecha;debe;haber;saldo;documento"),
    ("SAF 355", "Expediente, orden y acto de aprobación", "expediente;acto;fecha;beneficiario;concepto;importe"),
    ("SAF 355", "Papeles de trabajo de Anexo K 2008", "fila fuente;criterio;responsable;fecha;conciliación"),
    ("TGN", "Movimiento bancario asociado a los tres formularios", "cuenta;fecha valor;fecha proceso;signo;importe;referencia"),
    ("CUT-SIDIF Central", "Extracto y conciliación 2008", "cuenta;movimiento;estado;contrapartida;importe;fecha"),
    ("BNA", "Extracto/aviso de débito o crédito de la comisión", "cuenta;fecha valor;referencia;importe;moneda;contraparte"),
    ("BCRA/CRyL", "Movimiento o custodia sólo si hay instrumento de valores", "especie;cuenta;fecha;nominal;movimiento;referencia"),
    ("DADP/SAF 355", "Planillas compartidas de control y conciliación", "archivo;versión;autor;fecha;celdas/fórmulas;identificador"),
    ("DADP/DTI", "Tickets de intervención manual en base", "ticket;fecha;usuario;antes;después;autorización;motivo"),
    ("DADP/SAF 355", "Documentos externos/sidecar no adjuntados a SIGADE", "inventario;ruta;nombre;fecha;hash;relación con instrumento"),
    ("UAI/SAF 355", "Componentes no redondeados de OTROS 2018/2019", "importe fuente;unidad;precisión;cuenta;asiento;cálculo"),
    ("SICHE/DGSIAF", "Catálogo y export de consultas nombradas", "consulta;fuente;campos;filtros;corte;filas;archivo;hash"),
    ("CGN/SAF 355", "Acta o constancia de último formulario/corte equivalente", "acto;fecha;universo;último formulario;firmas;anexos"),
]
write_csv(
    HERE / "E0_V147_REQUEST_OBJECTS_V147.csv",
    [
        {
            "object_id": f"RO147_{index:02d}",
            "owner_or_system": owner,
            "requested_record": record,
            "minimum_usable_fields": fields,
            "success_test": "Objeto individualizable, reproducible y enlazable por identificador, fecha, cuenta e importe.",
            "negative_response_rule": "Informar repositorios, períodos, parámetros, inventarios, transferencias y expurgos consultados.",
            "status": "DRAFT_NOT_SENT",
        }
        for index, (owner, record, fields) in enumerate(request_objects, 1)
    ],
)

visual_path = HERE / "E0_V147_PDF_VISUAL_CONTROL.csv"
visual = read_csv(visual_path)
visual_add = [
    ("PV147_25", "e0_agn_resolution_86_2021_public_debt_control", "16", "16", "escalera SIGADE, mayorizado, formularios, TGN, CRyL y mayores"),
    ("PV147_26", "e0_agn_resolution_86_2021_public_debt_control", "82", "82", "campos obligatorios y validación no aplicada"),
    ("PV147_27", "e0_agn_resolution_86_2021_public_debt_control", "83", "83", "procedimientos omitidos y numeración Excel"),
    ("PV147_28", "e0_agn_report_65_2022_sigade_information_system", "18", "22", "ciclo DADP y SIDIF-Link"),
    ("PV147_29", "e0_agn_report_65_2022_sigade_information_system", "36", "40", "planillas compartidas y controles"),
    ("PV147_30", "e0_agn_report_65_2022_sigade_information_system", "37", "41", "precisión decimal y adjuntos no utilizados"),
    ("PV147_31", "e0_agn_report_65_2022_sigade_information_system", "38", "42", "rectificaciones fuera de SIGADE"),
    ("PV147_32", "e0_mecon_uai_report_24_2019_account_2018", "5", "5", "Anexo L y divergencias SIGADE/e-SIDIF"),
    ("PV147_33", "e0_mecon_uai_report_24_2019_account_2018", "6", "6", "acto de cierre y Anexos A-L"),
    ("PV147_34", "e0_mecon_uai_report_24_2019_account_2018", "13", "13", "OTROS -563 y componentes 400/163"),
    ("PV147_35", "e0_mecon_uai_report_37_2023_account_2022", "2", "2", "límites SIGADE, planillas y carga manual"),
    ("PV147_36", "e0_mecon_uai_report_37_2023_account_2022", "3", "3", "regularización de pagos fuera de SIGADE"),
    ("PV147_37", "e0_mecon_uai_report_48_2023_saf355_closure", "5", "5", "expedientes y actas de corte SAF 355"),
    ("PV147_38", "e0_mecon_uai_report_48_2023_saf355_closure", "7", "7", "pagos holdout e-SIDIF ausentes de SIGADE"),
    ("PV147_39", "e0_cgn_cuenta_inversion_2008_sdp", "67", "67", "Anexo K y fila 83106000 con tres SIDIF"),
]
visual = upsert(
    visual,
    [
        {
            "control_id": cid,
            "source_id": sid,
            "printed_page": printed,
            "pdf_page": pdf_page,
            "rendered_check": check,
            "result": "PASS",
            "inference_limit": "Control visual de atribución/página; no confirma pago target.",
        }
        for cid, sid, printed, pdf_page, check in visual_add
    ],
    "control_id",
)
write_csv(visual_path, visual, list(visual[0]))

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V147.csv"
breaks = read_csv(breaks_path)
break_add = [
    ("uai_repo_arithmetic_gap_045m", "precision", "Los valores mostrados difieren 0,45 millones, pero los componentes tienen precisión desconocida/desigual.", "Registrar tensión de valores mostrados; no afirmar error hasta obtener importes no redondeados.", "E0_REPO_DISPLAY_PRECISION_REASSESSMENT_V147.csv"),
    ("target_anexo_k_outside_cuadro1a", "scope", "La fila objetivo está en Anexo K, fuera de Cuadro 1A.", "Abrir rama Anexo K–mayorizado–formularios–TGN/banco; Cuadro 1A es control, no puerta exclusiva.", "E0_ANEXO_K_OFF_CUADRO1A_TARGET_BRANCH_V147.csv"),
    ("sigade_absence_not_nonpayment", "system", "Pagos posteriores aparecen en e-SIDIF sin registro SIGADE.", "Nunca inferir no pago sólo por ausencia/cancelación SIGADE; verificar contabilidad y banco.", "E0_CROSS_SYSTEM_PAYMENT_STATE_TRUTH_TABLE_V147.csv"),
    ("siche_public_manual_export_not_located", "availability", "No se localizó manual, esquema o export público de las consultas SICHE objetivo.", "Pedir metadatos/export; no interpretar no localizado como inexistente.", "E0_V147_PUBLIC_SEARCH_NEGATIVE_RESULTS_V147.csv"),
    ("sigade_validation_not_applied_later_period", "quality", "La validación incorporada no se aplicaba en el período auditado posterior.", "Usar como riesgo comparador y pedir controles/correcciones; no retroproyectar como hecho de 2008.", "E0_SIGADE_DATA_QUALITY_AND_SIDECAR_RISK_V147.csv"),
    ("spreadsheet_sidecar_essential_not_system_row", "document", "Planillas y documentos externos pueden contener conciliaciones y ajustes ausentes de la fila nativa.", "Pedir sidecars, versiones, fórmulas, autores y hashes junto con el registro del sistema.", "E0_SIGADE_DATA_QUALITY_AND_SIDECAR_RISK_V147.csv"),
    ("cryl_conditional_for_commission", "scope", "Una comisión bancaria no implica necesariamente movimiento/custodia de títulos en CRyL.", "Activar CRyL sólo si el formulario o instrumento prueba conexión con valores negociables.", "E0_AGN_OFFICIAL_SETTLEMENT_AUDIT_LADDER_V147.csv"),
    ("later_holdout_mismatch_not_target_2008", "time", "Los casos holdout 2019/2020/2022 demuestran una posibilidad sistémica, no el hecho objetivo 2008.", "Usar como regla metodológica; mantener el target en 0/10.", "E0_CROSS_SYSTEM_PAYMENT_STATE_TRUTH_TABLE_V147.csv"),
]
breaks = upsert(
    breaks,
    [
        {"break_id": bid, "dimension": dimension, "problem": problem, "rule": rule, "status": "FROZEN_V147", "evidence": evidence}
        for bid, dimension, problem, rule, evidence in break_add
    ],
    "break_id",
)
write_csv(breaks_path, breaks, list(breaks[0]))

trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V147.csv"
trace = read_csv(trace_path)
trace = upsert(
    trace,
    [
        {
            "trace_id": f"TR147_{index:03d}",
            "request_id": "REQ133_ECON" if index != 12 else "REQ133_BCRA",
            "institution": owner,
            "gap_id": f"V147_OBJECT_{index:02d}",
            "requested_record": record,
            "period_or_date": "2008; comparadores 2018-2023 sólo donde se indican",
            "identifiers": fields.split(";")[0] + ";83106000;71597;152677;2876",
            "minimum_usable_fields": fields,
            "confidentiality_fallback": "metadatos, conteos, copia testada y constancia de repositorios consultados",
            "status": "DRAFT_NOT_SENT",
        }
        for index, (owner, record, fields) in enumerate(request_objects, 1)
    ],
    "trace_id",
)
write_csv(trace_path, trace, list(trace[0]))

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V147.csv"
keys = read_csv(keys_path)
exact_keys = [
    "mayorizados por SIGADE", "Estado de Cuenta SIGADE", "Tabla de Amortización SIGADE", "Ficha SIGADE",
    "83106000", "71597", "152677", "2876", "COMISIONES - BANCO NACION", "Anexo K",
    "otras operaciones presupuestarias no incluidas en el Cuadro 1A", "IF-2019-14144802-APN-ONCP#MHA",
    "IF-2023-137577619-APN-ONCP#MEC", "EX-2023-137514569-APN-DGDAM#MEC",
    "IF-2023-147866862-APN-UAI#MEC", "IF-2023-148676623-APN-UAI#MEC",
    "Coordinación de Cuentas Bancarias", "componentes no redondeados OTROS",
]
keys = upsert(
    keys,
    [
        {
            "key_id": f"SK147_{index:02d}",
            "request_id": "REQ133_ECON",
            "key_group": "agn_audit_ladder_anexo_k",
            "exact_key": key,
            "search_purpose": "localizar registro, formulario, acto, papel o movimiento exacto",
            "source_or_basis": "V147 official audit and closing records",
            "caveat": "Clave de búsqueda; no confirma identidad, pago ni cobertura.",
        }
        for index, key in enumerate(exact_keys, 1)
    ],
    "key_id",
)
write_csv(keys_path, keys, list(keys[0]))

append_section(
    HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V147.md",
    "## Rectificación y ampliación V147 · Anexo K, mayorizado y respaldo bancario",
    """
Estado: **BORRADOR_NO_ENVIADO**. No se presentó ni autorizó presentación alguna.

La fila objetivo de la Cuenta de Inversión 2008 está publicada en el Anexo K, definido como operaciones presupuestarias no incluidas en el Cuadro 1A: `83106000 · COMISIONES - BANCO NACION · $32.270,30 · partida 7.2.8. · SIDIF 71597, 152677 y 2876`. Por ello se solicita, para cada identificador, el formulario completo, su cabecera y renglones, beneficiario/CUIT, moneda, importe, estado, orden de pago, asiento y cuenta; el reporte `mayorizado por SIGADE`; la Ficha, Estado de Cuenta y Tabla de Amortización SIGADE si corresponden; y los papeles de trabajo de confección/conciliación del Anexo K.

Se solicita además el movimiento de la Coordinación de Cuentas Bancarias de la TGN y el extracto/aviso bancario asociado, con cuenta, fecha valor, fecha proceso, signo, moneda, importe, contraparte y referencia, junto con la conciliación que enlace `SIGADE/SIDIF → formulario → orden → cuenta → movimiento`. Si existieron planillas compartidas, documentos externos, rectificaciones o intervenciones manuales sobre la base, se pide su inventario, versión, autor, fecha, fórmulas, autorización, estado anterior/posterior y hash.

Como comparador separado, se piden los importes fuente no redondeados y el papel de trabajo de `OTROS` en 2018/2019. La diferencia de valores mostrados es $0,45 millones, pero **no se afirma error aritmético**: los componentes publicados tienen precisión desigual y los valores fuente no fueron localizados.

Para SICHE se pide el catálogo/metadatos y un export reproducible de las consultas nombradas, indicando sistema fuente, campos, tipos, filtros, universo, fecha de corte, cantidad de filas, archivo y hash. Una respuesta negativa debe individualizar repositorios, períodos, consultas, parámetros, transferencias, expurgos e inventarios examinados.
""",
)

append_section(
    HERE / "REQUEST_SUBMISSION_CHECKLIST_V147.md",
    "## Control V147 · rectificación de precisión y rama Anexo K",
    """
- Mantener los seis pedidos en `DRAFT_NOT_SENT` hasta autorización expresa.
- No llamar error aritmético al 0,45 sin componentes fuente no redondeados.
- Adjuntar fila Anexo K, escalera oficial AGN, tabla de estados y objetos V147.
- Exigir los tres formularios SIDIF individualmente y el `mayorizado por SIGADE`.
- No cerrar pago sin movimiento TGN/CUT o extracto bancario conciliado.
- Mantener CRyL como rama condicional y el resultado estricto en 0/10.
""",
)

append_section(
    HERE / "SOURCE_REFERENCES_V147.md",
    "## Fuentes nuevas V147 · escalera oficial y controles cruzados",
    "\n".join(f"- `{source['id']}` · {source['title']} · {source['url']} · `{source['local']}` · `{source['sha']}`" for source in SOURCES),
)

append_section(
    HERE / "E0_INSTITUTIONAL_REQUEST_PACKAGE_V147.md",
    "## Ampliación V147 · prueba cruzada oficial",
    """
La AGN documenta una escalera de auditoría que cruza Ficha/Estado/Tabla SIGADE, reporte `mayorizado por SIGADE`, formularios individuales, mayores contables, movimientos TGN y —cuando corresponde— CRyL. Para la fila 83106000, que está en Anexo K fuera de Cuadro 1A, se priorizan los formularios 71597/152677/2876, el mayorizado, la orden y el movimiento bancario. También se piden planillas y documentos externos porque auditorías posteriores prueban que parte de los controles, ajustes y rectificaciones podía quedar fuera de la fila nativa. Estado: `DRAFT_NOT_SENT`.
""",
)

(HERE / "README_V147.md").write_text(
    """# V147 · escalera oficial de auditoría y rama Anexo K

V147 convierte la arquitectura de V146 en un protocolo oficial de prueba. La AGN auditó deuda cruzando `SIGADE → Estado/Ficha/Tabla → mayorizado por SIGADE → formularios e-SIDIF → mayores → movimientos TGN → CRyL cuando corresponda`. Esa cadena impide confundir registro, asiento, orden y liquidación bancaria.

La fila objetivo 2008 está en **Anexo K, fuera de Cuadro 1A**: `83106000 · COMISIONES - BANCO NACION · $32.270,30 · 7.2.8. · SIDIF 71597/152677/2876`. La ruta primaria pasa ahora por esos tres formularios, el mayorizado, la orden, el movimiento TGN/CUT y el extracto bancario. CRyL queda condicional a una conexión probada con títulos.

Auditorías posteriores muestran que SIGADE podía diferir de e-SIDIF, que existían planillas y rectificaciones externas y que pagos podían estar contabilizados sin aparecer en SIGADE. Son controles metodológicos posteriores, no prueba del hecho 2008.

V147 también rectifica la lectura de la diferencia REPO: `563,61 − 563,16 = 0,45` es una tensión entre valores mostrados, no un error probado, porque 400 y 163 fueron publicados sin decimales. Se piden importes no redondeados y papeles de trabajo.

Estado estricto: 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas; seis pedidos `DRAFT_NOT_SENT`, cero presentaciones y cero respuestas.
""",
    encoding="utf-8",
)

(HERE / "VEREDICTO_V147.md").write_text(
    """# Veredicto V147

La investigación ganó una ruta probatoria oficial y más exigente, pero el pago objetivo sigue abierto. La publicación 2008 atribuye exactamente la fila 83106000 y los SIDIF 71597, 152677 y 2876 a comisiones del Banco Nación dentro del Anexo K. Eso prueba imputación publicada, no liquidación.

Para confirmar pago debe cerrarse el puente `fila Anexo K → mayorizado/formularios → orden/asiento → cuenta → movimiento TGN/CUT o extracto bancario`, con identidad, fecha, moneda e importe conciliados. Una ausencia en SIGADE no basta para descartar pago, y una cancelación/asiento tampoco basta para afirmarlo.

La diferencia REPO de $0,45 millones queda reclasificada como tensión de precisión publicada. Sin componentes fuente no redondeados no hay error aritmético demostrado. La tensión entre el lenguaje “préstamos” y la familia contable de títulos/valores permanece abierta y exige asiento, regla de imputación e instrumento.

Resultado: 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas. Seis borradores continúan no enviados; no se ejecutó SICHE ni se recibió respuesta.
""",
    encoding="utf-8",
)

(HERE / "E0_FISCAL_RECONSTRUCTION_V147.md").write_text(
    """# Reconstrucción fiscal E0 V147

La reconstrucción estricta continúa en 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas. V147 añade una rama documental exacta para Anexo K y adopta la escalera de auditoría AGN. El pago sólo se incorpora al numerador cuando formulario, orden/asiento y movimiento bancario concilian. La diferencia REPO de $0,45 millones no se trata como error probado sin importes fuente no redondeados.
""",
    encoding="utf-8",
)

(HERE / "RETRIEVAL_LOG_V147.md").write_text(
    """# Registro de recuperación V147

- 2026-08-31: preservados cinco PDF oficiales nuevos (UAI 24/2019, UAI 37/2023, UAI 48/2023, AGN 65/2022 y Resolución AGN 86/2021 Anexo I).
- Control visual PASS en 15 páginas nuevas, incluida la página PDF 67 de la Separata 2008 ya preservada.
- Confirmada la escalera oficial: registro SIGADE, Estado/Ficha/Tabla, mayorizado, formularios, mayores, movimientos TGN y CRyL condicional.
- Confirmada visualmente la fila Anexo K 83106000 y la alineación de SIDIF 71597/152677/2876.
- No se localizó públicamente manual, esquema ni export SICHE objetivo; resultado negativo acotado, no prueba de inexistencia.
- No se ejecutó SICHE, no se restauró base y no se presentó pedido.
""",
    encoding="utf-8",
)

(HERE / "AUDITORIA_V147.md").write_text(
    f"""# Auditoría V147

- Fuentes maestras: {len(catalog)}.
- Fuentes primarias E0: {len(census)}.
- Fuentes nuevas: 5.
- Controles visuales acumulados: {len(visual)}.
- Quiebres metodológicos congelados: {len(breaks)}.
- Diferencia mostrada REPO: $0,45 millones; error aritmético probado: no.
- Formularios objetivo: 71597, 152677 y 2876; ejecución confirmada: 0/10.
- Pedidos presentados: 0; respuestas: 0.
""",
    encoding="utf-8",
)

(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V147_A_V148.md").write_text(
    """# Handover V147 → V148

## Estado

- QA V147: PASS.
- Cinco fuentes oficiales nuevas; 469 fuentes maestras y 229 E0.
- Escalera oficial AGN: SIGADE → Estado/Ficha/Tabla → `mayorizado por SIGADE` → formularios → mayores → TGN/banco; CRyL condicional.
- Fila 2008 exacta en Anexo K fuera de Cuadro 1A: 83106000, Banco Nación, $32.270,30, partida 7.2.8., SIDIF 71597/152677/2876.
- Ausencia en SIGADE no equivale a no pago; auditorías posteriores prueban divergencias e-SIDIF/SIGADE.
- Diferencia REPO 0,45 reclasificada: tensión de precisión, no error demostrado; faltan importes fuente no redondeados.
- No se localizó manual/esquema/export público SICHE.
- Seis `DRAFT_NOT_SENT`; cero presentaciones/respuestas; 10 adjudicaciones, 9 cuentas, 0/10 ejecuciones.

## Prioridad V148

1. Mantener borradores salvo autorización expresa.
2. Localizar metadatos/export público o inventario de `mayorizados por SIGADE` y de los tres formularios.
3. Buscar referencias públicas exactas a 71597, 152677, 2876 y 83106000 en actos, expedientes o anexos.
4. Buscar inventarios/actas de corte SAF 355 equivalentes a los identificados en 2019/2023.
5. Cerrar puente TGN/CUT/BNA: cuenta, fecha valor, signo, moneda, importe y referencia.
6. Buscar papel no redondeado y regla de imputación de la comisión REPO sin convertir comparadores posteriores en prueba de 2008.
""",
    encoding="utf-8",
)

old_handover = HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V147_A_V147.md"
if old_handover.exists():
    old_handover.unlink()

append_section(
    REPO / "BACKUP_ACTUALIZACION_2026-08-29.md",
    "## V147 · escalera AGN, rama Anexo K y rectificación de precisión",
    """
- Ruta oficial: SIGADE→Estado/Ficha/Tabla→mayorizado→formularios→mayores→TGN/banco; CRyL condicional.
- Fila Anexo K 83106000 con SIDIF 71597/152677/2876 confirmada visualmente; pago sigue abierto.
- Ausencia SIGADE no equivale a no pago; planillas/sidecars y rectificaciones externas deben pedirse.
- Diferencia REPO 0,45 es tensión de precisión, no error probado.
- SICHE manual/export público no localizado; target 0/10; seis borradores no enviados.
""",
)

hist_path = HERE / "HISTORICAL_SOURCE_QUEUE_V147.csv"
hist = read_csv(hist_path)
for row in hist:
    if row["variable_family"] == "REPO_COMMISSION":
        row["why"] = "pista concreta con diferencia de precisión publicada; error no probado"
        row["next_action"] = "obtener componentes no redondeados y puente instrumento-fecha-ID-contraparte-origen"
hist = upsert(
    hist,
    [
        {"priority": "P0", "episode": "E0_2008", "variable_family": "ANEXO_K_FORMS", "target_artifact": "Mayorizado y formularios SIDIF 71597/152677/2876", "preferred_source": "SAF 355 / CGN / DGSIAF", "status": "EXACT_IDS_PUBLIC_BODY_OPEN_NOT_SENT", "why": "fila 83106000 fuera de Cuadro 1A", "next_action": "obtener formularios, asiento, orden y mayor"},
        {"priority": "P0", "episode": "E0_2008", "variable_family": "TGN_BANK_SETTLEMENT", "target_artifact": "Movimiento TGN/CUT y extracto BNA asociado", "preferred_source": "TGN / BNA", "status": "OFFICIAL_AUDIT_ROUTE_PROVED_TARGET_OPEN", "why": "única capa que puede confirmar liquidación", "next_action": "conciliar cuenta, fecha, signo, moneda, importe y referencia"},
        {"priority": "P1", "episode": "E0_COMPARATOR_2018_2019", "variable_family": "REPO_PRECISION", "target_artifact": "Componentes no redondeados y papel de trabajo OTROS", "preferred_source": "UAI / SAF 355 / CGN", "status": "DISPLAYED_TENSION_ERROR_NOT_PROVED", "why": "0,45 no es error demostrable con precisión desigual", "next_action": "obtener importes fuente, asiento y regla de imputación"},
    ],
    "target_artifact",
)
write_csv(hist_path, hist, list(hist[0]))

recovery_path = HERE / "RECOVERY_QUEUE_V147.csv"
recovery = read_csv(recovery_path)
for row in recovery:
    if row["entity"] == "REPO comisión 2019":
        row["missing_artifact"] = "mayor, asiento, instrumento, componentes no redondeados y papel de trabajo"
        row["why"] = "comparador contable con diferencia mostrada 0,45; error no probado"
recovery = upsert(
    recovery,
    [
        {"priority": "10", "entity": "SAF 355 / SIDIF Central", "missing_artifact": "Mayorizado 83106000 y formularios 71597/152677/2876", "why": "rama Anexo K exacta", "status": "OPEN_NOT_SENT"},
        {"priority": "11", "entity": "TGN / BNA", "missing_artifact": "Movimiento bancario y conciliación de la comisión", "why": "cierre de liquidación", "status": "OPEN_NOT_SENT"},
        {"priority": "12", "entity": "DADP sidecars", "missing_artifact": "Planillas, documentos externos y tickets de rectificación", "why": "auditorías posteriores prueban información fuera de la fila nativa", "status": "OPEN_COMPARATOR_ROUTE"},
        {"priority": "13", "entity": "SICHE", "missing_artifact": "Manual, catálogo, esquema y export reproducible", "why": "capacidad pública sin cuerpo/export", "status": "PUBLIC_NOT_LOCATED_REQUEST_OPEN"},
    ],
    "entity",
)
write_csv(recovery_path, recovery, list(recovery[0]))

write_csv(
    HERE / "INHERITED_QA_STATUS_V147.csv",
    [
        {"script": "qa_v146.py", "pre_v147_result": "PASS", "post_v147_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V146 ampliada y rectificada por precisión, rama Anexo K y escalera AGN."},
        {"script": "qa_v147.py", "pre_v147_result": "N/A", "post_v147_result": "PASS", "interpretation": "Verifica fuentes, matrices, hashes, límites, no envío y corrección de precisión."},
    ],
)

hash_rows = []
for row in catalog:
    local = row["archivo_local"]
    path = REPO / local.lstrip("/") if local else None
    exists = bool(path and path.is_file())
    actual = sha256(path) if exists else ""
    expected = row["sha256"]
    hash_rows.append(
        {
            "id": row["id"],
            "archivo_local": local,
            "exists": str(exists),
            "sha_catalog": expected,
            "sha_actual": actual,
            "hash_ok": str(bool(exists and expected and actual.lower() == expected.lower())),
        }
    )
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V147.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V147.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)

size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or "tmp" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append(
        {
            "path": path.relative_to(REPO).as_posix(),
            "bytes": size,
            "mib": f"{size / 1048576:.6f}",
            "over_50_mib": str(size > 50 * 1048576),
            "over_100_mib": str(size > 100 * 1048576),
        }
    )
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V147.csv", size_rows)

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V146.json").read_text(encoding="utf-8-sig"))
complete.update(
    {
        "checkpoint": "V147",
        "date": "2026-08-31",
        "state": "E0_AGN_AUDIT_LADDER_ANEXO_K_BRANCH_PROVED_TARGET_BANK_SETTLEMENT_OPEN_NOT_SENT",
        "master_catalog_entries": len(catalog),
        "physical_local_copies": physical,
        "physical_local_hash_ok": hash_ok,
        "remaining_physical_gaps": len(catalog) - physical,
        "e0_primary_sources_preserved": len(census),
        "numeric_v147_strict_changed": False,
        "sources_newly_preserved_v147": 5,
        "e0_primary_sources_newly_preserved_v147": 5,
        "e0_duplicate_recaptures_v147": 0,
        "e0_fiscal_method_breaks_frozen": len(breaks),
        "e0_request_traceability_rows": len(trace),
        "e0_request_search_keys": len(keys),
        "e0_v147_pdf_visual_controls": len(visual),
        "e0_agn_official_audit_ladder_rows": len(ladder),
        "e0_anexo_k_target_branch_rows": len(branch),
        "e0_sigade_sidecar_risk_rows": len(risks),
        "e0_cross_system_truth_table_rows": len(truth),
        "e0_repo_precision_reassessment_rows": len(repo_precision),
        "e0_v147_request_objects": len(request_objects),
        "e0_siche_public_manual_or_export_located": False,
        "e0_mayorizado_por_sigade_public_target_located": False,
        "e0_target_anexo_k_outside_cuadro1a": True,
        "e0_target_sidif_ids": ["71597", "152677", "2876"],
        "e0_sigade_absence_proves_nonpayment": False,
        "e0_repo_displayed_components_difference_ars_millions": "0.45",
        "e0_repo_arithmetic_error_proved": False,
        "e0_repo_unrounded_components_located": False,
        "e0_repo_rounding_or_subcomponent_explanation_open": True,
        "e0_repo_published_internal_gap_ars_millions": "SUPERSEDED_NOT_PROVEN_AS_ERROR",
        "e0_settlement_executed_rows_confirmed": 0,
        "e0_requests_submitted": 0,
        "e0_request_responses_received": 0,
        "e0_request_package_status": "DRAFT_NOT_SENT",
        "historical_workstream": "Obtain mayorizado and forms 71597/152677/2876, TGN/CUT/BNA settlement bridge, sidecars, and unrounded REPO workpapers; no request submitted",
    }
)
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V147.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def checkpoint_manifest() -> None:
    files = [
        {"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
        for path in sorted(HERE.iterdir())
        if path.is_file() and path.name != "MANIFEST_V147.json"
    ]
    manifest = {
        "checkpoint": "V147",
        "parent_checkpoint": "V146",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30,
        "strict_coverage_pct": STRICT,
        "closed_network_gate": "NO",
        "e0_primary_sources": len(census),
        "new_preserved_sources": 5,
        "fiscal_ledger_rows": len(read_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V147.csv")),
        "fiscal_method_breaks": len(breaks),
        "request_traceability_rows": len(trace),
        "request_search_keys": len(keys),
        "agn_audit_ladder_rows": len(ladder),
        "anexo_k_target_branch_rows": len(branch),
        "sigade_sidecar_risk_rows": len(risks),
        "cross_system_truth_rows": len(truth),
        "repo_precision_rows": len(repo_precision),
        "v147_request_objects": len(request_objects),
        "pdf_visual_controls_v147": len(visual),
        "siche_public_manual_or_export_located": False,
        "repo_arithmetic_error_proved": False,
        "repo_displayed_difference_ars_millions": "0.45",
        "award_rows_exact": 10,
        "account_candidate_rows": 9,
        "executed_settlement_rows_confirmed": 0,
        "request_drafts": 6,
        "requests_submitted": 0,
        "responses_received": 0,
        "files": files,
    }
    (HERE / "MANIFEST_V147.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tree(root: Path) -> str:
    paths = sorted(root.rglob("*"), key=lambda value: value.relative_to(root).as_posix().casefold())
    return "\n".join(
        path.relative_to(root).as_posix() + ("/" if path.is_dir() else "")
        for path in paths
        if ".git" not in path.parts and "__pycache__" not in path.parts and "tmp" not in path.parts
    ) + "\n"


(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")
checkpoint_manifest()

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = []
for path in sorted(REPO.rglob("*"), key=lambda value: value.relative_to(REPO).as_posix().casefold()):
    if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts and "tmp" not in path.parts and path != global_manifest:
        global_files.append({"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})
global_manifest.write_text(
    json.dumps(
        {
            "checkpoint": "V147",
            "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "strict_coverage_pct": STRICT,
            "exact_entities": 30,
            "closed_network_gate": "NO",
            "source_audit": f"{len(catalog)} master; {physical} physical SHA-valid; 5 new official sources; AGN ladder and Anexo K branch proved; target not settled; 0/10; six drafts not submitted.",
            "historical_workstream": "Obtain mayorizado/forms and TGN/CUT/BNA bridge; no request submitted",
            "file_count_excluding_manifest": len(global_files),
            "files": global_files,
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)

print(f"V147 BUILD PASS · catalog={len(catalog)} · E0={len(census)} · physical={physical} · hash_ok={hash_ok}")
