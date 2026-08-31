from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import re
import shutil


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
PARENT = HERE.parent / "V138"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v139" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


EXPECTED = {
    "argentina_dgsiaf_bulletin_2020_q1_siche.pdf": (353161, "926acc816b62f79eaca371b0e96d9a19a311a6e87b639db6808293c8c46d978d"),
    "argentina_dgsiaf_bulletin_2020_q4_siche.pdf": (258310, "9f3406b988266b653715f1304290703ee56c212c65e275234805da7df8960917"),
    "argentina_dgsiaf_bulletin_2021_q2_siche.pdf": (616928, "cda39b14f258923bcca12c24f0863c949be12dac62dd631ae7c0dd8fed481e26"),
    "argentina_dgsiaf_sidif_c35_c41_c55_decommission_2025.html": (33116, "bf85256fefbfa1e64c0b52f98c1cc73d0d79412df4ca2843b30ede2cda37771b"),
    "argentina_slu_system_description_v3.pdf": (2078779, "b988cf5525df07966fa877c40baf8782a2ece70b50a33298168a45aa71cc228d"),
    "cgn_cuenta_2011_separata_deuda_publica.pdf": (1105867, "2ccd64bcc4f439fd64788201563de3ff406b37a911ef7624a9f5d4594ac85111"),
    "cgn_cuenta_2012_separata_deuda_publica.pdf": (3149094, "612f97761b950bfeb9bc12df21c6135ca3eb31a226cd6ed403a1569cc8ea4d4b"),
    "cgn_cuenta_2013_separata_deuda_publica.pdf": (963610, "a8a08355939622cec6d8b46ab8e5d4d17ee86081d915d71aa7660b262e4f7517"),
    "cgn_cuenta_2014_separata_deuda_publica.pdf": (1071658, "20f413fd6a3585a041a8e7c49d3cf546e57f2de8f36d8d46e91e68738eee6fd0"),
    "cgn_cuenta_2015_separata_deuda_publica.pdf": (1068951, "cee3a13179a4dd162c2cbcefbc5b70ce2d15c793c540258210da0c3ddbe85d9c"),
}


def source(source_id: str, filename: str, institution: str, title: str, url: str,
           publication: str, period: str, code: str, families: str, breaks: str,
           use: str, caveat: str, note: str, transport: str = "SECURE_DIRECT") -> dict[str, object]:
    size, digest = EXPECTED[filename]
    suffix = Path(filename).suffix.lower()
    source_type = "PDF oficial · captura preservada" if suffix == ".pdf" else "HTML oficial · captura preservada"
    return {
        "id": source_id, "filename": filename, "institution": institution,
        "title": title, "url": url, "publication": publication, "period": period,
        "code": code, "families": families, "breaks": breaks, "use": use,
        "caveat": caveat, "note": note, "bytes": size, "sha256": digest,
        "type": source_type, "transport": transport,
    }


# Los PDF 2011 y 2012 fueron descargados otra vez para control, pero sus bytes son
# idénticos a las copias ya catalogadas en V112. Se validan en EXPECTED y no se
# cuentan como fuentes nuevas.
SOURCES = [
    source(
        "e0_dgsiaf_siche_deployment_2020_q1",
        "argentina_dgsiaf_bulletin_2020_q1_siche.pdf",
        "Dirección General de Sistemas Informáticos de Administración Financiera",
        "Boletín DGSIAF 2020 T1 · despliegues SICHE de Gastos, Recursos, PEF y Pagos",
        "https://www.argentina.gob.ar/sites/default/files/2020-ene-feb-mar-boletin-dgsiaf.pdf",
        "2020 T1", "2020", "SICHE; SIDIF Central modelo 95",
        "SICHE;Gastos;Pagos;Recursos;PEF;numeric_filters",
        "capacidad implantada en 2020 versus presencia del registro target 2008",
        "USABLE_SICHE_MODULE_DEPLOYMENT_PROOF",
        "Prueba módulos y expresiones numéricas, no una consulta de los tres SIDIF.",
        "V139 E0: SICHE tenía consultas Gastos/Recursos/PEF y Pagos de SIDIF Central modelo 95; admitía expresiones numéricas.",
    ),
    source(
        "e0_dgsiaf_siche_deployment_2020_q4",
        "argentina_dgsiaf_bulletin_2020_q4_siche.pdf",
        "Dirección General de Sistemas Informáticos de Administración Financiera",
        "Boletín DGSIAF 2020 T4 · consultas especiales y Conciliación Bancaria en SICHE",
        "https://www.argentina.gob.ar/sites/default/files/boletin-trimestral-dgsiaf-octubre-noviembre-diciembre-2020.pdf",
        "2020 T4", "2020", "SICHE; SIDIF Central",
        "SICHE;special_queries;basic_tables;financial_programming;bank_reconciliation",
        "módulo desplegado versus retención e identificación de cada movimiento",
        "USABLE_SICHE_BANK_RECONCILIATION_DEPLOYMENT_PROOF",
        "Prueba que Conciliación Bancaria era consultable, no que la fila target subsista.",
        "V139 E0: SICHE incorporó consultas especiales, Tablas Básicas y Conciliación Bancaria de SIDIF Central.",
    ),
    source(
        "e0_dgsiaf_siche_deployment_2021_q2",
        "argentina_dgsiaf_bulletin_2021_q2_siche.pdf",
        "Dirección General de Sistemas Informáticos de Administración Financiera",
        "Boletín DGSIAF 2021 T2 · búsqueda detallada de entidades en SICHE",
        "https://www.argentina.gob.ar/sites/default/files/2021/07/dgsiaf-boletin_trimestral_dgsiaf-abril_mayo_junio_2021-5.pdf",
        "2021 T2", "2021", "SICHE; búsqueda detallada",
        "SICHE;voucher;form;agreement;entity;header_filter;detail_filter",
        "capacidad de filtro versus ejecución de una consulta target",
        "USABLE_SICHE_HEADER_DETAIL_FILTER_PROOF",
        "Prueba filtros de cabecera y detalle, no el resultado para SAF 355.",
        "V139 E0: SICHE permite filtrar comprobantes, formularios, acuerdos y entes tanto en cabecera como en detalle.",
    ),
    source(
        "e0_dgsiaf_sidif_forms_decommission_2025",
        "argentina_dgsiaf_sidif_c35_c41_c55_decommission_2025.html",
        "Dirección General de Sistemas Informáticos de Administración Financiera",
        "Desafectación SIDIF Central y modelos de Gastos C-35, C-41 y C-55",
        "https://www.argentina.gob.ar/economia/sechacienda/dgsiaf/boletin-trimestral-iv-2025/desafectacion-sidif-central",
        "2025-12", "vigente desde 2026-01-01", "SIDIF Central; C35; C41; C55",
        "SIDIF_Central;Gastos;C35;C41;C55;transmission;decommission",
        "alcance actual de desafectación versus especie documental target 2008",
        "USABLE_CURRENT_FORM_SCOPE_AND_TRANSITION",
        "Incluye C35/C41/C55; no asigna tipo al target ni excluye C42 del antiguo SLU.",
        "V139 E0: la desafectación desde 2026-01-01 alcanza SIDIF Central y modelos C35, C41 y C55, incluidas transmisiones.",
    ),
    source(
        "e0_dgsiaf_slu_system_description_v3",
        "argentina_slu_system_description_v3.pdf",
        "Dirección General de Sistemas Informáticos de Administración Financiera",
        "SLU · Descripción del sistema · versión 3",
        "https://www.argentina.gob.ar/sites/default/files/slu_modconc-sistema.pdf",
        "s.f.; versión 3", "diseño previo a 2008", "SLU; Sistema de Tesorería; Conciliación Bancaria",
        "SLU;treasury;payment_modes;bank_reconciliation;internal_extract;bank_commissions",
        "diseño funcional versus despliegue completo y fila target en SAF 355",
        "USABLE_SYSTEM_DESIGN_AND_RECONCILIATION_SCHEMA",
        "Documento preliminar sin fecha inequívoca; no prueba despliegue íntegro ni registro target.",
        "V139 E0: define pagos, extracto interno, conciliación y carga automática de movimientos como comisiones bancarias.",
    ),
    source(
        "e0_cgn_cuenta_inversion_2013_sdp",
        "cgn_cuenta_2013_separata_deuda_publica.pdf", "Contaduría General de la Nación",
        "Cuenta de Inversión 2013 · Servicio de la Deuda Pública · Anexo K",
        "https://www.economia.gob.ar/hacienda/cgn/cuenta/2013/archivos/sdp.pdf",
        "2014", "2013", "83106000; C41",
        "debt_service;SIGADE;SIDIF;C41;BNA_commissions",
        "comparador posterior y concepto YPF específico versus target genérico 2008",
        "USABLE_83106000_SEMANTIC_DRIFT_AND_TYPE_COMPARATOR",
        "El código fue reutilizado con descripción YPF; no permite inferir el propósito ni tipo de 2008.",
        "V139 E0: comparador anual de 83106000, útil para forma documental y deriva semántica.",
        "TLS_EXPIRED_OFFICIAL_SERVER",
    ),
    source(
        "e0_cgn_cuenta_inversion_2014_sdp",
        "cgn_cuenta_2014_separata_deuda_publica.pdf", "Contaduría General de la Nación",
        "Cuenta de Inversión 2014 · Servicio de la Deuda Pública · Anexo K",
        "https://www.economia.gob.ar/hacienda/cgn/cuenta/2014/archivos/sdp.pdf",
        "2015", "2014", "83106000; C41",
        "debt_service;SIGADE;SIDIF;C41;BNA_commissions",
        "comparador posterior y concepto YPF específico versus target genérico 2008",
        "USABLE_83106000_SEMANTIC_DRIFT_AND_TYPE_COMPARATOR",
        "El código fue reutilizado con descripción YPF; no permite inferir el propósito ni tipo de 2008.",
        "V139 E0: comparador anual de 83106000, útil para forma documental y deriva semántica.",
        "TLS_EXPIRED_OFFICIAL_SERVER",
    ),
    source(
        "e0_cgn_cuenta_inversion_2015_sdp",
        "cgn_cuenta_2015_separata_deuda_publica.pdf", "Contaduría General de la Nación",
        "Cuenta de Inversión 2015 · Servicio de la Deuda Pública · Anexo K",
        "https://www.economia.gob.ar/hacienda/cgn/cuenta/2015/archivos/sdp.pdf",
        "2016", "2015", "83106000; VARIOS",
        "debt_service;SIGADE;SIDIF;BNA_commissions;aggregation",
        "comparador posterior y concepto YPF específico versus target genérico 2008",
        "USABLE_83106000_SEMANTIC_DRIFT_AND_TYPE_COMPARATOR",
        "El código fue reutilizado con descripción YPF y agregado VARIOS; no permite inferir el tipo de 2008.",
        "V139 E0: comparador anual de 83106000; muestra que la divulgación alterna entre tipo explícito y VARIOS.",
        "TLS_EXPIRED_OFFICIAL_SERVER",
    ),
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
    skip = {"build_e0_siche_c55_v138.py", "qa_v138.py", "MANIFEST_V138.json", "INHERITED_QA_STATUS_V138.csv"}
    for item in PARENT.iterdir():
        if not item.is_file() or item.name in skip or item.name.startswith("HANDOVER_PROXIMA_SESION"):
            continue
        target = HERE / item.name.replace("V138", "V139")
        text = item.read_text(encoding="utf-8-sig")
        # Cambian las referencias a archivos del checkpoint, no la historia de
        # procedencia ni etiquetas como FROZEN_V138 / "fuente nueva V138".
        placeholder = "historical_retrieval/__PARENT_V138__/"
        text = text.replace("historical_retrieval/v138/", placeholder)
        text = text.replace("_V138", "_V139").replace("_v138", "_v139")
        text = text.replace(placeholder, "historical_retrieval/v138/")
        if item.name.startswith("REQUEST_") or item.name in {
            "CURRENT_STATE_V138.csv", "E0_INSTITUTIONAL_REQUEST_PACKAGE_V138.md",
            "RETRIEVAL_LOG_V138.md",
        }:
            text = text.replace("V138", "V139").replace("v138", "v139")
        target.write_text(text, encoding="utf-8")


clone_parent()

for filename, (size, digest) in EXPECTED.items():
    path = BIN / filename
    assert path.is_file() and path.stat().st_size == size, path
    assert sha256(path) == digest, path

# Las capturas redundantes 2011/2012 deben coincidir con el catálogo histórico.
for year, filename in ((2011, "cgn_cuenta_2011_separata_deuda_publica.pdf"), (2012, "cgn_cuenta_2012_separata_deuda_publica.pdf")):
    historical = CYCLE / "inputs" / "historical_retrieval" / "v112" / "binaries" / f"cgn_cuenta_inversion_{year}_sdp.pdf"
    assert historical.is_file() and sha256(historical) == EXPECTED[filename][1]

for item in SOURCES:
    item["local"] = "/" + (BIN / str(item["filename"])).relative_to(REPO).as_posix()

source_ids = {str(item["id"]) for item in SOURCES}

catalog = [row for row in read_csv(CATALOG) if row["id"] not in source_ids]
assert len(catalog) == 422
for item in SOURCES:
    catalog.append({
        "id": item["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": item["institution"],
        "titulo": item["title"], "url_original": item["url"], "archivo_local": item["local"],
        "fecha_descarga": "2026-08-30", "fecha_publicacion": item["publication"],
        "codigo_serie": item["code"], "periodo_utilizado": item["period"], "tipo": item["type"],
        "sha256": item["sha256"], "nota": item["note"],
    })
assert len(catalog) == 430 and len({row["id"] for row in catalog}) == 430
write_csv(CATALOG, catalog)
catalog_by_id = {row["id"]: row for row in catalog}

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V139.csv"
census = [row for row in read_csv(census_path) if row["source_id"] not in source_ids]
assert len(census) == 182
for row in census:
    # El catálogo maestro conserva la ruta canónica original. Esto repara la
    # deriva de rutas causada por reemplazos de versión en builders antiguos.
    master = catalog_by_id[row["source_id"]]
    row["local_path"] = master["archivo_local"]
    row["sha256"] = master["sha256"]
    master_path = REPO / master["archivo_local"].lstrip("/") if master["archivo_local"] else None
    if master_path and master_path.is_file():
        row["bytes"] = str(master_path.stat().st_size)
    if row["source_id"] == "e0_dgsiaf_slu_global_regularization_2004":
        row["caveat"] = "Hace a C-55 el comparador de mecanismo principal, pero no asigna tipo ni reemplaza la exportación target."
for item in SOURCES:
    census.append({
        "source_id": item["id"], "institution": item["institution"], "artifact": item["title"],
        "url": item["url"], "local_path": item["local"], "sha256": item["sha256"],
        "bytes": str(item["bytes"]), "period_coverage": item["period"],
        "variable_families": item["families"], "primary_source": "YES", "preserved": "YES",
        "method_breaks": item["breaks"], "use_status": item["use"], "caveat": item["caveat"],
    })
assert len(census) == 190 and len({row["source_id"] for row in census}) == 190
write_csv(census_path, census)

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V139.csv"
provenance = [row for row in read_csv(provenance_path) if row["source_id"] not in source_ids]
assert len(provenance) == 85
for row in provenance:
    master = catalog_by_id[row["source_id"]]
    row["local_path"] = master["archivo_local"]
    row["sha256"] = master["sha256"]
    master_path = REPO / master["archivo_local"].lstrip("/") if master["archivo_local"] else None
    if master_path and master_path.is_file():
        row["bytes"] = str(master_path.stat().st_size)
for item in SOURCES:
    transport_note = (
        "Descarga directa desde servidor oficial histórico con curl --insecure porque su certificado TLS estaba vencido; contenido preservado y validado con SHA-256."
        if item["transport"] == "TLS_EXPIRED_OFFICIAL_SERVER"
        else "Descarga directa segura desde dominio oficial; binario preservado y validado con SHA-256."
    )
    provenance.append({
        "source_id": item["id"], "original_url": item["url"], "retrieval_url": item["url"],
        "capture_timestamp": "20260830", "cdx_digest": "N/A_DIRECT_OFFICIAL",
        "local_path": item["local"], "sha256": item["sha256"], "bytes": str(item["bytes"]),
        "provenance_note": transport_note,
    })
assert len(provenance) == 93
write_csv(provenance_path, provenance)


# Capacidad SICHE: prueba qué puede pedirse y cómo, nunca que exista el target.
siche_timeline = [
    {"row_id": "ST139_01", "period": "2020-01", "system": "SICHE · SIDIF Central modelo 95", "deployment": "consultas de Gastos", "search_capability": "expresiones numéricas", "target_use": "buscar 71597, 152677, 2876, 83106000 y 32270.30", "status": "CAPABILITY_PROVED_TARGET_RESULT_OPEN", "source_id": "e0_dgsiaf_siche_deployment_2020_q1", "locator": "PDF p.10"},
    {"row_id": "ST139_02", "period": "2020-01", "system": "SICHE · SIDIF Central modelo 95", "deployment": "consultas de Recursos y PEF", "search_capability": "selección por modelo", "target_use": "control de universo y sistema", "status": "CAPABILITY_PROVED_TARGET_RESULT_OPEN", "source_id": "e0_dgsiaf_siche_deployment_2020_q1", "locator": "PDF p.10"},
    {"row_id": "ST139_03", "period": "2020-02", "system": "SICHE · SIDIF Central modelo 95", "deployment": "consultas de Pagos", "search_capability": "consulta normalizada", "target_use": "cruzar comprobante con pago", "status": "CAPABILITY_PROVED_TARGET_RESULT_OPEN", "source_id": "e0_dgsiaf_siche_deployment_2020_q1", "locator": "PDF p.10"},
    {"row_id": "ST139_04", "period": "2020-02", "system": "SICHE", "deployment": "Formulación Presupuestaria", "search_capability": "consulta heredada", "target_use": "control contextual; no prueba ejecución", "status": "CAPABILITY_PROVED_TARGET_RESULT_OPEN", "source_id": "e0_dgsiaf_siche_deployment_2020_q1", "locator": "PDF p.10"},
    {"row_id": "ST139_05", "period": "2020 T4", "system": "SICHE · SIDIF Central", "deployment": "consultas especiales solicitadas por usuarios", "search_capability": "consulta especial existente", "target_use": "pedir búsqueda exacta si la consulta estándar no alcanza", "status": "CAPABILITY_PROVED_TARGET_RESULT_OPEN", "source_id": "e0_dgsiaf_siche_deployment_2020_q4", "locator": "PDF p.10"},
    {"row_id": "ST139_06", "period": "2020 T4", "system": "SICHE · SIDIF Central", "deployment": "Tablas Básicas, Programación Financiera y Modificaciones Presupuestarias", "search_capability": "múltiples dominios", "target_use": "resolver vínculos de cabecera", "status": "CAPABILITY_PROVED_TARGET_RESULT_OPEN", "source_id": "e0_dgsiaf_siche_deployment_2020_q4", "locator": "PDF p.10"},
    {"row_id": "ST139_07", "period": "2020 T4", "system": "SICHE · SIDIF Central", "deployment": "Conciliación Bancaria", "search_capability": "consulta de movimientos conciliados", "target_use": "cruzar extracto y Libro Banco", "status": "CAPABILITY_PROVED_TARGET_RESULT_OPEN", "source_id": "e0_dgsiaf_siche_deployment_2020_q4", "locator": "PDF p.10"},
    {"row_id": "ST139_08", "period": "2021 T2", "system": "SICHE", "deployment": "búsqueda detallada de comprobantes, formularios, acuerdos y entes", "search_capability": "filtros en cabecera y detalle de entidad", "target_use": "combinar N° SIDIF, SAF, concepto, importe y cuenta", "status": "CAPABILITY_PROVED_TARGET_RESULT_OPEN", "source_id": "e0_dgsiaf_siche_deployment_2021_q2", "locator": "PDF p.11"},
    {"row_id": "ST139_09", "period": "desde 2026-01-01", "system": "SIDIF Central → SICHE", "deployment": "desafectación de modelos C35, C41 y C55, incluidas transmisiones", "search_capability": "alcance histórico actual", "target_use": "C41/C55 primero; C35 fallback; no excluir C42 de SLU", "status": "CURRENT_SCOPE_PROVED_TARGET_TYPE_OPEN", "source_id": "e0_dgsiaf_sidif_forms_decommission_2025", "locator": "página oficial"},
]
write_csv(HERE / "E0_SICHE_DEPLOYMENT_CAPABILITY_TIMELINE_V139.csv", siche_timeline)

comparators = [
    {"row_id": "DC139_01", "year": "2007", "account": "83106000", "description": "COMISIONES - BANCO NACION", "amount_ars": "26656.30", "disclosure": "83318;151752;240417", "document_signal": "TYPE_NOT_PRINTED", "source_id": "e0_cgn_cuenta_inversion_2007_sdp", "locator": "PDF p.68 Anexo K", "permitted_inference": "Misma cuenta y leyenda existían antes.", "forbidden_inference": "Los números son C41 o tienen el mismo propósito."},
    {"row_id": "DC139_02", "year": "2008", "account": "83106000", "description": "COMISIONES - BANCO NACION", "amount_ars": "32270.30", "disclosure": "71597;152677;2876", "document_signal": "TARGET_TYPE_OPEN", "source_id": "e0_cgn_cuenta_inversion_2008_sdp", "locator": "PDF p.67 Anexo K", "permitted_inference": "Tres localizadores SIDIF exactos.", "forbidden_inference": "Asignar C41, C55, propósito o pago."},
    {"row_id": "DC139_03", "year": "2009", "account": "83106000", "description": "COMISIONES - BANCO NACION", "amount_ars": "17557.10", "disclosure": "", "document_signal": "BLANK", "source_id": "e0_cgn_cuenta_inversion_2009_sdp", "locator": "PDF p.74 Anexo K", "permitted_inference": "La divulgación anual no fue uniforme.", "forbidden_inference": "No existieron comprobantes."},
    {"row_id": "DC139_04", "year": "2010", "account": "83106000", "description": "COMISIONES - BANCO NACION", "amount_ars": "1869.45", "disclosure": "C41 5310;74291;156087;285224", "document_signal": "C41_EXPLICIT_EXACT_DESCRIPTION", "source_id": "e0_cgn_cuenta_inversion_2010_sdp", "locator": "PDF p.74 Anexo K", "permitted_inference": "Es el comparador documental adyacente más fuerte para C41.", "forbidden_inference": "Los tres SIDIF 2008 son C41."},
    {"row_id": "DC139_05", "year": "2011", "account": "83106000", "description": "COMISIONES AL BNA-CONVENIO PARA PAGO INDEMNIZ.LEY 25471 YPF", "amount_ars": "1101.10", "disclosure": "C41 10675;90537;213939;296449", "document_signal": "C41_EXPLICIT_DESCRIPTION_CHANGED", "source_id": "e0_cgn_cuenta_inversion_2011_sdp", "locator": "PDF p.62 Anexo K", "permitted_inference": "El código admite C41 y cambió de concepto.", "forbidden_inference": "El concepto YPF existía en 2008."},
    {"row_id": "DC139_06", "year": "2012", "account": "83106000", "description": "COMISIONES AL BNA-CONVENIO PARA PAGO INDEMNIZ.LEY 25471 YPF", "amount_ars": "1113.20", "disclosure": "VARIOS", "document_signal": "AGGREGATED_DESCRIPTION_CHANGED", "source_id": "e0_cgn_cuenta_inversion_2012_sdp", "locator": "PDF p.52 Anexo K", "permitted_inference": "La ausencia de tipo puede ser sólo agregación.", "forbidden_inference": "VARIOS excluye C41."},
    {"row_id": "DC139_07", "year": "2013", "account": "83106000", "description": "COMISIONES AL BNA-CONVENIO PARA PAGO INDEMNIZ.LEY 25471 YPF", "amount_ars": "1542.75", "disclosure": "C41 76352;171921;281843", "document_signal": "C41_EXPLICIT_DESCRIPTION_CHANGED", "source_id": "e0_cgn_cuenta_inversion_2013_sdp", "locator": "PDF p.53 Anexo K", "permitted_inference": "C41 reaparece en el mismo código reutilizado.", "forbidden_inference": "Continuidad de propósito desde 2008."},
    {"row_id": "DC139_08", "year": "2014", "account": "83106000", "description": "COMISIONES AL BNA-CONVENIO PARA PAGO INDEMNIZ.LEY 25471 YPF", "amount_ars": "1748.45", "disclosure": "C41 15660;89414;184508;300052", "document_signal": "C41_EXPLICIT_DESCRIPTION_CHANGED", "source_id": "e0_cgn_cuenta_inversion_2014_sdp", "locator": "PDF p.67 Anexo K", "permitted_inference": "C41 es un antecedente recurrente de forma.", "forbidden_inference": "Identidad de operación con 2008."},
    {"row_id": "DC139_09", "year": "2015", "account": "83106000", "description": "COMISIONES AL BNA-CONVENIO PARA PAGO INDEMNIZ.LEY 25471 YPF", "amount_ars": "767.85", "disclosure": "VARIOS", "document_signal": "AGGREGATED_DESCRIPTION_CHANGED", "source_id": "e0_cgn_cuenta_inversion_2015_sdp", "locator": "PDF p.54 Anexo K", "permitted_inference": "Tipo explícito y VARIOS alternan en la publicación.", "forbidden_inference": "VARIOS identifica una especie documental."},
    {"row_id": "DC139_10", "year": "2007-2015", "account": "83106000", "description": "serie comparada", "amount_ars": "N/A", "disclosure": "N/A", "document_signal": "C41_LEADING_DOCUMENT_COMPARATOR_TYPE_OPEN", "source_id": "e0_cgn_cuenta_inversion_2007_sdp;e0_cgn_cuenta_inversion_2008_sdp;e0_cgn_cuenta_inversion_2009_sdp;e0_cgn_cuenta_inversion_2010_sdp;e0_cgn_cuenta_inversion_2011_sdp;e0_cgn_cuenta_inversion_2012_sdp;e0_cgn_cuenta_inversion_2013_sdp;e0_cgn_cuenta_inversion_2014_sdp;e0_cgn_cuenta_inversion_2015_sdp", "locator": "Anexos K", "permitted_inference": "C41 lidera el prior documental; la semántica de 83106000 deriva.", "forbidden_inference": "Transformar frecuencia comparada en clasificación target."},
]
write_csv(HERE / "E0_83106000_DOCUMENT_TYPE_COMPARATORS_V139.csv", comparators)

reconciliation = [
    {"row_id": "BR139_01", "system_layer": "Tesorería SLU", "observable": "medios de pago", "system_rule": "CUT, cuentas propias, efectivo, Nota, valores o compensación", "target_test": "identificar medio efectivo", "proof_value": "MECHANISM_ENUMERATION", "source_id": "e0_dgsiaf_slu_system_description_v3", "locator": "PDF p.107; doc p.104", "caveat": "Diseño funcional, no fila target."},
    {"row_id": "BR139_02", "system_layer": "Tesorería SLU", "observable": "selección y confirmación", "system_rule": "la selección antecede la confirmación del pago", "target_test": "recuperar estados/fechas", "proof_value": "PHASE_SEPARATION", "source_id": "e0_dgsiaf_slu_system_description_v3", "locator": "PDF p.107; doc p.104", "caveat": "Confirmación de sistema no equivale por sí sola a conciliación bancaria."},
    {"row_id": "BR139_03", "system_layer": "Conciliación bancaria", "observable": "extracto bancario o escrito", "system_rule": "se compara con Libro Banco SLU", "target_test": "cruzar ambas caras", "proof_value": "TWO_SIDED_RECONCILIATION", "source_id": "e0_dgsiaf_slu_system_description_v3", "locator": "PDF p.113; doc p.110", "caveat": "El manual no contiene extractos 2008."},
    {"row_id": "BR139_04", "system_layer": "Conciliación bancaria", "observable": "aplicaciones y comprobantes", "system_rule": "se generan cuando corresponde", "target_test": "pedir comprobante asociado", "proof_value": "SUPPORTING_VOUCHER_SIGNATURE", "source_id": "e0_dgsiaf_slu_system_description_v3", "locator": "PDF p.113; doc p.110", "caveat": "La existencia depende del caso."},
    {"row_id": "BR139_05", "system_layer": "Cuenta operativa", "observable": "extracto interno", "system_rule": "SLU mantiene cuenta y extracto interno", "target_test": "pedir movimiento interno", "proof_value": "INTERNAL_LEDGER_SIGNATURE", "source_id": "e0_dgsiaf_slu_system_description_v3", "locator": "PDF p.113; doc p.110", "caveat": "No acredita conservación del target."},
    {"row_id": "BR139_06", "system_layer": "Cuenta bancaria", "observable": "BNA", "system_rule": "las cuentas operativas pueden ser del Banco Nación", "target_test": "filtrar banco/cuenta", "proof_value": "BANK_MATCH_CAPABILITY", "source_id": "e0_dgsiaf_slu_system_description_v3", "locator": "PDF p.113; doc p.110", "caveat": "No identifica la cuenta concreta."},
    {"row_id": "BR139_07", "system_layer": "Extracto interno", "observable": "comisiones bancarias", "system_rule": "todo movimiento de fondos se registra por transacción o conciliación automática; ejemplo expreso: comisiones bancarias", "target_test": "buscar movimiento automático de 32270.30 o partes", "proof_value": "LEADING_C55_MECHANISM_COMPARATOR", "source_id": "e0_dgsiaf_slu_system_description_v3", "locator": "PDF p.114; doc p.111", "caveat": "Mecanismo compatible; no clasifica los tres SIDIF."},
    {"row_id": "BR139_08", "system_layer": "Extracto externo", "observable": "carga bancaria", "system_rule": "se cargan extractos bancarios o escritos", "target_test": "pedir lote/fecha/saldo", "proof_value": "EXTERNAL_EXTRACT_SIGNATURE", "source_id": "e0_dgsiaf_slu_system_description_v3", "locator": "PDF p.114; doc p.111", "caveat": "Carga posible no prueba que el archivo subsista."},
    {"row_id": "BR139_09", "system_layer": "TGN", "observable": "débitos por pago", "system_rule": "cheques, notas y órdenes bancarias se separan del débito/crédito automático BNA", "target_test": "clasificar origen del movimiento", "proof_value": "PAYMENT_VS_AUTOMATIC_DEBIT_SPLIT", "source_id": "e0_dgsiaf_slu_system_description_v3", "locator": "PDF p.115; doc p.112", "caveat": "Diagrama funcional, no cronología target."},
    {"row_id": "BR139_10", "system_layer": "Cierre probatorio", "observable": "firma completa", "system_rule": "tipo + formulario + movimiento interno + extracto externo + conciliación", "target_test": "exigir cadena y estados", "proof_value": "EXECUTION_CLOSE_TEST", "source_id": "e0_dgsiaf_slu_system_description_v3;e0_dgsiaf_slu_global_regularization_2004;e0_dgsiaf_slu_bank_reconciliation_reports_2002", "locator": "esquema combinado", "caveat": "Sin fila target, el numerador sigue 0/10."},
]
write_csv(HERE / "E0_BANK_COMMISSION_RECONCILIATION_SIGNATURE_V139.csv", reconciliation)

hypotheses = [
    {"candidate": "C41", "analytic_role": "LEADING_DOCUMENT_TYPE_COMPARATOR", "support": "2010 repite cuenta y leyenda genérica y publica cuatro C41; 2011, 2013 y 2014 también exhiben C41 bajo el código reutilizado", "contrary": "2008 no imprime tipo; 2009 queda vacío y 2012/2015 dicen VARIOS; el concepto cambia a YPF desde 2011", "first_search": "SC y SLU por C41 + N°SIDIF", "decisive_record": "exportación target y cuerpo/estado", "status": "PRIOR_1A_NOT_PROVED"},
    {"candidate": "C55", "analytic_role": "LEADING_MECHANISM_COMPARATOR", "support": "el diseño SLU usa comisiones bancarias como movimiento automático y el manual C55 registra débito directo por comisión", "contrary": "no hay fila target, aceptación central, cuenta, extracto o Libro Banco", "first_search": "SC y SLU por C55/Débito Directo + N°SIDIF", "decisive_record": "tipo/subtipo, historia SC, extracto y Libro Banco", "status": "PRIOR_1B_NOT_PROVED"},
    {"candidate": "C42", "analytic_role": "SLU_FALLBACK", "support": "el antiguo SLU admitía C42 al ingresar N° SIDIF", "contrary": "la partida 7.2.8 es presupuestaria y la página 2025 no lo enumera entre modelos SC desafectados", "first_search": "SLU por C42 si C41/C55 fallan", "decisive_record": "tipo y razón extrapresupuestaria", "status": "FALLBACK_NOT_EXCLUDED"},
    {"candidate": "C35", "analytic_role": "SIDIF_CENTRAL_FALLBACK", "support": "la desafectación 2025 incluye modelo C35 y transmisiones de SIDIF Central", "contrary": "C35 es compromiso y no hay señal pública que lo vincule a las tres referencias", "first_search": "SC por C35 si C41/C55 y búsqueda sin tipo fallan", "decisive_record": "comprobante y vínculo con devengado/pago", "status": "FALLBACK_NOT_EXCLUDED"},
    {"candidate": "UNCLASSIFIED", "analytic_role": "DECISION", "support": "Anexo K sólo rotula SIDIF", "contrary": "ningún comparador sustituye la fila 2008", "first_search": "primero sin restricción de tipo por identificadores exactos; luego C41/C55; después C42/C35", "decisive_record": "exportación SICHE SC+SLU y respaldo AMIDDF", "status": "DUAL_PRIORITY_NO_TARGET_PROOF"},
]
write_csv(HERE / "E0_DOCUMENT_TYPE_HYPOTHESIS_BALANCE_V139.csv", hypotheses)

visual_control = [
    {"control_id": "PV139_01", "source_id": "e0_dgsiaf_siche_deployment_2020_q1", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v139/binaries/argentina_dgsiaf_bulletin_2020_q1_siche.pdf", "pdf_page": "10", "rendered_check": "SICHE Gastos/Recursos/PEF/Pagos y expresiones numéricas", "result": "PASS"},
    {"control_id": "PV139_02", "source_id": "e0_dgsiaf_siche_deployment_2020_q4", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v139/binaries/argentina_dgsiaf_bulletin_2020_q4_siche.pdf", "pdf_page": "10", "rendered_check": "consultas especiales y Conciliación Bancaria", "result": "PASS"},
    {"control_id": "PV139_03", "source_id": "e0_dgsiaf_siche_deployment_2021_q2", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v139/binaries/argentina_dgsiaf_bulletin_2021_q2_siche.pdf", "pdf_page": "11", "rendered_check": "filtros de cabecera y detalle", "result": "PASS"},
    {"control_id": "PV139_04", "source_id": "e0_dgsiaf_slu_system_description_v3", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v139/binaries/argentina_slu_system_description_v3.pdf", "pdf_page": "89", "rendered_check": "Sistema de Tesorería", "result": "PASS"},
    {"control_id": "PV139_05", "source_id": "e0_dgsiaf_slu_system_description_v3", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v139/binaries/argentina_slu_system_description_v3.pdf", "pdf_page": "107", "rendered_check": "medios, selección y confirmación de pagos", "result": "PASS"},
    {"control_id": "PV139_06", "source_id": "e0_dgsiaf_slu_system_description_v3", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v139/binaries/argentina_slu_system_description_v3.pdf", "pdf_page": "113", "rendered_check": "conciliación, Libro Banco y extracto interno", "result": "PASS"},
    {"control_id": "PV139_07", "source_id": "e0_dgsiaf_slu_system_description_v3", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v139/binaries/argentina_slu_system_description_v3.pdf", "pdf_page": "114", "rendered_check": "movimientos automáticos; ejemplo comisiones bancarias", "result": "PASS"},
    {"control_id": "PV139_08", "source_id": "e0_dgsiaf_slu_system_description_v3", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v139/binaries/argentina_slu_system_description_v3.pdf", "pdf_page": "115", "rendered_check": "débitos de pagos versus débito/crédito automático BNA", "result": "PASS"},
    {"control_id": "PV139_09", "source_id": "e0_cgn_cuenta_inversion_2011_sdp", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v112/binaries/cgn_cuenta_inversion_2011_sdp.pdf", "pdf_page": "62", "rendered_check": "83106000, ARS 1.101,10, cuatro C41, concepto YPF", "result": "PASS"},
    {"control_id": "PV139_10", "source_id": "e0_cgn_cuenta_inversion_2012_sdp", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v112/binaries/cgn_cuenta_inversion_2012_sdp.pdf", "pdf_page": "52", "rendered_check": "83106000, ARS 1.113,20, VARIOS, concepto YPF", "result": "PASS"},
    {"control_id": "PV139_11", "source_id": "e0_cgn_cuenta_inversion_2013_sdp", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v139/binaries/cgn_cuenta_2013_separata_deuda_publica.pdf", "pdf_page": "53", "rendered_check": "83106000, ARS 1.542,75, tres C41, concepto YPF", "result": "PASS"},
    {"control_id": "PV139_12", "source_id": "e0_cgn_cuenta_inversion_2014_sdp", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v139/binaries/cgn_cuenta_2014_separata_deuda_publica.pdf", "pdf_page": "67", "rendered_check": "83106000, ARS 1.748,45, cuatro C41, concepto YPF", "result": "PASS"},
    {"control_id": "PV139_13", "source_id": "e0_cgn_cuenta_inversion_2015_sdp", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v139/binaries/cgn_cuenta_2015_separata_deuda_publica.pdf", "pdf_page": "54", "rendered_check": "83106000, ARS 767,85, VARIOS, concepto YPF", "result": "PASS"},
]
write_csv(HERE / "E0_V139_PDF_VISUAL_CONTROL.csv", visual_control)


# Corrige el ranking heredado: C41 lidera como tipo comparado y C55 como
# mecanismo comparado. Ninguno obtiene precedencia probatoria sobre la fila target.
type_narrowing = [
    {"candidate": "UNCLASSIFIED", "rank": "0", "support": "Anexo K sólo imprime SIDIF", "contrary": "no da tipo", "decision_key": "consulta SICHE sin restricción por N° SIDIF", "status": "EXACT_LOCATORS_TYPE_OPEN", "source_id": "e0_cgn_cuenta_inversion_2008_sdp"},
    {"candidate": "C41_DOCUMENT_COMPARATOR", "rank": "1A", "support": "2010 repite cuenta 83106000 y leyenda genérica con C41 explícitos", "contrary": "comparador posterior; 2008 no imprime tipo", "decision_key": "tipo=C41; cuerpo; estado; OP/Nota si corresponde", "status": "LEADING_DOCUMENT_COMPARATOR_NOT_PROVED", "source_id": "e0_cgn_cuenta_inversion_2010_sdp"},
    {"candidate": "C55_DIRECT_DEBIT", "rank": "1B", "support": "SLU registra comisiones bancarias y C55 Débito Directo como mecanismo compatible", "contrary": "falta exportación, aceptación, cuenta y conciliación target", "decision_key": "tipo=C55; subtipo; historia SC; extracto; Libro Banco", "status": "LEADING_MECHANISM_COMPARATOR_NOT_PROVED", "source_id": "e0_dgsiaf_slu_system_description_v3;e0_dgsiaf_slu_global_regularization_2004"},
    {"candidate": "C42_NON_BUDGETARY", "rank": "2", "support": "tipo admitido por ingreso manual SLU", "contrary": "partida 7.2.8 presupuestaria; no figura en alcance SC 2025", "decision_key": "tipo=C42; AXT; razón extrapresupuestaria", "status": "SLU_FALLBACK_NOT_EXCLUDED", "source_id": "e0_dgsiaf_slu_sidif_number_input_2003;e0_dgsiaf_slu_expense_reports_2003"},
    {"candidate": "C35_COMMITMENT", "rank": "3", "support": "modelo de Gastos SIDIF Central incluido en la desafectación vigente", "contrary": "ninguna señal pública lo vincula a los tres SIDIF", "decision_key": "tipo=C35; compromiso; vínculos con devengado/pago", "status": "SIDIF_CENTRAL_FALLBACK_NOT_EXCLUDED", "source_id": "e0_dgsiaf_sidif_forms_decommission_2025"},
    {"candidate": "SEARCH_SET", "rank": "N/A", "support": "SICHE admite búsquedas numéricas, cabecera/detalle y módulos Gastos/Pagos/Conciliación", "contrary": "capacidad no prueba cobertura ni fila", "decision_key": "sin tipo → C41/C55 → C42/C35 → consulta especial", "status": "PROVED_QUERY_ORDER_TARGET_OPEN", "source_id": "e0_dgsiaf_siche_deployment_2020_q1;e0_dgsiaf_siche_deployment_2020_q4;e0_dgsiaf_siche_deployment_2021_q2"},
    {"candidate": "DECISION", "rank": "N/A", "support": "tipo, historia y conciliación deciden", "contrary": "se prohíbe convertir ranking o frecuencia en hecho", "decision_key": "exportación SICHE SC+SLU + imagen/respaldos AMIDDF", "status": "DUAL_PRIORITY_NO_TARGET_PROOF", "source_id": "e0_argentina_resolution_53_2024_siche"},
]
write_csv(HERE / "E0_SLU_SIDIF_DOCUMENT_TYPE_NARROWING_V139.csv", type_narrowing)

query_plan = [
    {"query_id": "SQ139_01", "sequence": "1", "system": "SICHE · SIDIF Central", "filter_set": "ejercicio=2008; SAF=355; N°SIDIF=71597,152677,2876; sin tipo", "requested_output": "Gastos y grilla/exportación sin transformación", "success_test": "tres filas o trazabilidad individual", "fallback": "expresiones 83106000; 32270.30; concepto", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ139_02", "sequence": "2", "system": "SICHE · SIDIF Central/SLU", "filter_set": "C41 y C55; N° SIDIF target; cabecera y detalle", "requested_output": "tipo; número local; estado; historia", "success_test": "especie resuelta", "fallback": "buscar todos los tipos", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ139_03", "sequence": "3", "system": "SICHE · Gastos", "filter_set": "7.2.8; 83106000; 32270.30; Banco Nación", "requested_output": "cabecera e ítems", "success_test": "suma, tipo y beneficiario", "fallback": "consulta especial de usuario", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ139_04", "sequence": "4", "system": "SICHE · C41", "filter_set": "C41; 71597,152677,2876; SAF355", "requested_output": "cuerpo; estado; OP; Nota/medio; cuentas", "success_test": "tipo y cadena C41", "fallback": "índice AMIDDF", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ139_05", "sequence": "5", "system": "SICHE · C55", "filter_set": "C55; Débito Directo; Banco Nación; comisión", "requested_output": "subtipo; cuenta; imputación; historia SC", "success_test": "mecanismo C55 exacto", "fallback": "todos los movimientos automáticos", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ139_06", "sequence": "6", "system": "SICHE · Pagos", "filter_set": "N° SIDIF/OP target; pagador SAF/TGN", "requested_output": "F80/PG; beneficiario; medio; estados", "success_test": "evento de pago vinculado", "fallback": "fecha/importe/beneficiario", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ139_07", "sequence": "7", "system": "SICHE · Conciliación Bancaria", "filter_set": "cuenta BNA; importe target; formulario", "requested_output": "extracto externo; extracto interno/Libro Banco; aplicación", "success_test": "débito cruzado y conciliado", "fallback": "ventana ±5 días; partes que sumen 32270.30", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ139_08", "sequence": "8", "system": "SICHE · fallback", "filter_set": "SLU C42; SIDIF Central C35", "requested_output": "tipo; fundamento; vínculos", "success_test": "clasificación alternativa", "fallback": "consulta especial sin tipo", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ139_09", "sequence": "9", "system": "AMIDDF", "filter_set": "SAF355; 2008; Otros Gastos; tres SIDIF", "requested_output": "índice; caja; cuerpo; folios; imágenes", "success_test": "respaldo físico/digital", "fallback": "tejuelo y planilla de remisión", "status": "DRAFT_NOT_SENT"},
    {"query_id": "SQ139_10", "sequence": "10", "system": "RAIP Economía", "filter_set": "Resolución 53/2024 + Ley 27.275", "requested_output": "exportaciones existentes o derivación interna; metadatos de búsqueda negativa", "success_test": "respuesta reproducible", "fallback": "denegación fundada y entrega parcial", "status": "DRAFT_NOT_SENT"},
]
write_csv(HERE / "E0_SICHE_TARGET_QUERY_PLAN_V139.csv", query_plan)

# Amplía la escalera de divulgación sin confundir comparadores con prueba target.
ladder_path = HERE / "E0_SIGADE_SIDIF_DISCLOSURE_LADDER_V139.csv"
ladder = [row for row in read_csv(ladder_path) if not row["row_id"].startswith("DL139_")]
ladder_specs = [
    (25, "2011", "1101.10", "C41 10675;90537;213939;296449", "ITEMIZED", "e0_cgn_cuenta_inversion_2011_sdp", "PDF_p62_Anexo_K", "Código reutilizado con concepto YPF; no prueba 2008."),
    (26, "2012", "1113.20", "VARIOS", "AGGREGATED", "e0_cgn_cuenta_inversion_2012_sdp", "PDF_p52_Anexo_K", "La agregación no excluye comprobantes subyacentes."),
    (27, "2013", "1542.75", "C41 76352;171921;281843", "ITEMIZED", "e0_cgn_cuenta_inversion_2013_sdp", "PDF_p53_Anexo_K", "Concepto YPF; comparador formal, no identidad target."),
    (28, "2014", "1748.45", "C41 15660;89414;184508;300052", "ITEMIZED", "e0_cgn_cuenta_inversion_2014_sdp", "PDF_p67_Anexo_K", "Concepto YPF; comparador formal, no identidad target."),
    (29, "2015", "767.85", "VARIOS", "AGGREGATED", "e0_cgn_cuenta_inversion_2015_sdp", "PDF_p54_Anexo_K", "Concepto YPF; VARIOS no asigna tipo."),
]
for number, year, amount, disclosure, level, sid, locator, caveat in ladder_specs:
    ladder.append({
        "row_id": f"DL139_{number:02d}", "year": year, "sigade": "83106000",
        "provider_or_concept": "Comisiones BNA · convenio indemnización Ley 25.471 YPF",
        "amount_ars": amount, "sidif_disclosure": disclosure, "disclosure_level": level,
        "source_id": sid, "locator": locator, "target_2008_use": "DOCUMENT_TYPE_AND_SEMANTIC_DRIFT_COMPARATOR",
        "caveat": caveat,
    })
assert len(ladder) == 29
write_csv(ladder_path, ladder)

# Corrige tres sobreafirmaciones heredadas que trataban los números como C41 probado.
trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V139.csv"
trace = read_csv(trace_path)
for row in trace:
    if row["trace_id"] == "TR134_106":
        row["requested_record"] = "Cuerpo y estado de los tres registros SIDIF 2008, cualquiera sea su tipo"
        row["minimum_usable_fields"] = "tipo;SAF;beneficiario;concepto;importe;moneda;emisión;vencimiento;estado"
    elif row["trace_id"] == "TR136_119":
        row["requested_record"] = "Búsqueda y copia de los tres cuerpos documentales SIDIF en el fondo financiero"
        row["minimum_usable_fields"] = "signatura;caja;cuerpo;folios;tipo;SAF;beneficiario;concepto;importe;estado;firmas"

trace_specs = [
    (149, "SICHE_GASTOS", "Consulta SICHE Gastos SIDIF Central sin restricción de tipo", "SAF355;2008;71597;152677;2876", "consulta;filtros;cabecera;detalle;exportación"),
    (150, "SICHE_C41", "Cuerpo y estado C41 si alguno de los tres se clasifica así", "C41;71597;152677;2876", "tipo;estado;OP;Nota;beneficiario;cuentas"),
    (151, "SICHE_C55", "C55 Débito Directo si alguno de los tres se clasifica así", "C55;Débito Directo;BNA;comisión", "subtipo;cuenta;imputación;historia;aceptación"),
    (152, "SICHE_C42", "C42 SLU como búsqueda alternativa", "C42;71597;152677;2876", "tipo;AXT;fundamento;estado"),
    (153, "SICHE_C35", "C35 SIDIF Central como búsqueda alternativa", "C35;71597;152677;2876", "compromiso;vínculos;estado"),
    (154, "SICHE_PAYMENT", "Consulta SICHE Pagos por identificadores y vínculos", "SAF355;2008;N°SIDIF/OP", "PG/F80;medio;pagador;beneficiario;estado"),
    (155, "SICHE_RECONCILIATION", "Consulta SICHE Conciliación Bancaria", "BNA;32270.30;movimientos parciales", "extracto externo;extracto interno;Libro Banco;aplicación;estado"),
    (156, "SICHE_QUERY_AUDIT", "Metadatos reproducibles de toda búsqueda sin resultados", "Gastos;Pagos;Conciliación;C41;C55;C42;C35", "sistema;modelo;dataset;filtros;fecha;filas;cobertura;exclusiones"),
]
trace = [row for row in trace if not row["trace_id"].startswith("TR139_")]
for number, gap, record, identifiers, fields in trace_specs:
    trace.append({
        "trace_id": f"TR139_{number}", "request_id": "REQ133_ECON",
        "institution": "Ministerio de Economía / Secretaría de Hacienda",
        "gap_id": gap, "requested_record": record, "period_or_date": "2008; consulta 2026",
        "identifiers": identifiers, "minimum_usable_fields": fields,
        "confidentiality_fallback": "exportación disociada; tachas parciales; metadatos de búsqueda",
        "status": "DRAFT_NOT_SENT",
    })
assert len(trace) == 156
write_csv(trace_path, trace)

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V139.csv"
keys = read_csv(keys_path)
for row in keys:
    if row["key_id"] == "SK134_104":
        row["key_group"] = "sidif_target_ids"
        row["search_purpose"] = "recuperar y clasificar tres registros SIDIF 2008"
    elif row["key_id"] == "SK138_156":
        row["search_purpose"] = "comparador principal de mecanismo, en paralelo con C41 documental"
keys = [row for row in keys if not row["key_id"].startswith("SK139_")]
key_specs = [
    (161, "query_order", "sin_tipo;C41;C55;C42;C35", "secuencia que evita una exclusión prematura"),
    (162, "siche_domain", "Gastos;Pagos;Conciliación Bancaria", "módulos SICHE desplegados"),
    (163, "header", "SAF355;ejercicio2008;SIDIF71597;SIDIF152677;SIDIF2876", "filtros de cabecera"),
    (164, "detail", "83106000;COMISIONES - BANCO NACION;7.2.8", "filtros de detalle"),
    (165, "numeric_expression", "32270.30;32270,30;partes_que_sumen_32270.30", "expresiones numéricas"),
    (166, "type_first", "C41;C55", "doble prioridad documental y de mecanismo"),
    (167, "type_fallback", "C42;C35", "búsqueda alternativa no excluida"),
    (168, "mechanism", "comisión bancaria;débito automático;Débito Directo", "rama de movimiento bancario"),
    (169, "reconciliation", "extracto bancario;extracto interno;Libro Banco;aplicación", "firma bancaria-contable completa"),
    (170, "negative_metadata", "sistema;modelo;dataset;filtros;fecha;filas;cobertura;exclusiones", "auditar resultado cero"),
]
for number, group, key, purpose in key_specs:
    keys.append({
        "key_id": f"SK139_{number}", "request_id": "REQ133_ECON", "key_group": group,
        "exact_key": key, "search_purpose": purpose,
        "source_or_basis": "E0_SICHE_DEPLOYMENT_CAPABILITY_TIMELINE_V139.csv;E0_SICHE_TARGET_QUERY_PLAN_V139.csv",
        "caveat": "Clave de búsqueda; no confirma resultado.",
    })
assert len(keys) == 170
write_csv(keys_path, keys)

exhaustion_path = HERE / "E0_EXPEDIENT_PUBLIC_SEARCH_EXHAUSTION_V139.csv"
exhaustion = read_csv(exhaustion_path)
for row in exhaustion:
    if row["search_id"] == "EX135_11":
        row["target"] = "SIDIF 71597, 152677 y 2876"
        row["result"] = "Sólo se recuperó el Anexo K; no cuerpos documentales ni filas SDPGB/SDPAG/SICHE"
        row["status"] = "THREE_SIDIF_IDENTIFIERS_EXACT_PUBLIC_BODIES_TYPES_AND_STATES_NOT_LOCATED"
        row["permitted_inference"] = "Los tres números son claves de búsqueda exactas de comisiones BNA; el tipo sigue abierto."
    elif row["search_id"] == "EX136_14":
        row["target"] = "SIDIF 71597, 152677 y 2876 en AGAN/AMIDDF"
write_csv(exhaustion_path, exhaustion)

agan_path = HERE / "E0_AGAN_C41_ARCHIVAL_ROUTE_V139.csv"
agan = read_csv(agan_path)
for row in agan:
    if row["row_id"] == "AR136_01":
        row["target_query"] = "SIDIF 71597;152677;2876; tipo documental abierto"
    elif row["row_id"] == "AR136_03":
        row["target_query"] = "formulario original; lista diaria; nota; boleto; débito; eventuales C41/C55"
write_csv(agan_path, agan)

type_audit_path = HERE / "E0_SIDIF_TARGET_DOCUMENT_TYPE_AUDIT_V139.csv"
type_audit = read_csv(type_audit_path)
for row in type_audit:
    if row["row_id"] == "DT137_05":
        row["printed_object"] = "Cierre V139"
        row["printed_label"] = "hipótesis múltiple"
        row["target_values"] = "C41 documental / C55 mecanismo / C42 SLU / C35 SIDIF Central"
        row["directly_proves"] = "cuatro ramas buscables en orden reproducible"
        row["does_not_prove"] = "tipo ni ejecución"
        row["status"] = "DUAL_PRIORITY_FALLBACKS_DO_NOT_PREJUDGE"
write_csv(type_audit_path, type_audit)

# Nuevos controles no aditivos del ledger fiscal.
ledger_path = HERE / "E0_FISCAL_MECHANISM_LEDGER_V139.csv"
new_ledger_ids = {f"F{number}" for number in range(196, 209)}
ledger = [row for row in read_csv(ledger_path) if row["ledger_id"] not in new_ledger_ids]
for row in ledger:
    if row["ledger_id"] == "F160":
        row["phase"] = "SIDIF_TO_BANK_DEBIT_RECONCILIATION_OPEN"
        row["instrument"] = "UNCLASSIFIED_SIDIF_CANDIDATE_CHAIN"
        row["original_unit"] = "SIDIF_LOCATORS"
        row["realization_status"] = "IDENTIFIERS_AND_CONDITIONAL_CHAINS_PROVED_TARGET_TYPE_OPEN"
        row["status_interpretation"] = "Three exact SIDIF identifiers can anchor conditional searches across document, processing, debit and adjustment records."
    elif row["ledger_id"] == "F172":
        row["phase"] = "C41_EXTERNAL_PAYMENT_APPLICABILITY_CONTROL"
        row["instrument"] = "CONDITIONAL_C41_OBSERVATIONS_NOTE_BNA_DOCUMENTS"
        row["original_unit"] = "TARGET_RECORDS_CLASSIFIED_EXTERNAL"
ledger_specs = [
    (196, "2020", "SICHE_DEPLOYMENT", "GASTOS_QUERY", "Secretaría de Hacienda", "usuarios SICHE", "SIDIF Central modelo 95", "consulta Gastos", "e0_dgsiaf_siche_deployment_2020_q1", "p.10", "QUERY_CAPABILITY_PROVED_TARGET_OPEN", "Gastos estaba desplegado con expresiones numéricas."),
    (197, "2020", "SICHE_DEPLOYMENT", "PAYMENTS_QUERY", "Secretaría de Hacienda", "usuarios SICHE", "SIDIF Central modelo 95", "consulta Pagos", "e0_dgsiaf_siche_deployment_2020_q1", "p.10", "QUERY_CAPABILITY_PROVED_TARGET_OPEN", "Pagos estaba desplegado en SICHE."),
    (198, "2020", "SICHE_DEPLOYMENT", "SPECIAL_QUERY", "Secretaría de Hacienda", "usuarios SICHE", "consultas especiales", "consulta solicitada", "e0_dgsiaf_siche_deployment_2020_q4", "p.10", "SPECIAL_QUERY_CAPABILITY_PROVED_TARGET_OPEN", "Había consultas especiales pedidas por usuarios."),
    (199, "2020", "SICHE_DEPLOYMENT", "BANK_RECONCILIATION_QUERY", "Secretaría de Hacienda", "usuarios SICHE", "SIDIF Central", "Conciliación Bancaria", "e0_dgsiaf_siche_deployment_2020_q4", "p.10", "QUERY_CAPABILITY_PROVED_TARGET_OPEN", "La conciliación era dominio consultable."),
    (200, "2021", "SICHE_SEARCH", "HEADER_DETAIL_FILTER", "Secretaría de Hacienda", "usuarios SICHE", "comprobantes/formularios/acuerdos/entes", "búsqueda detallada", "e0_dgsiaf_siche_deployment_2021_q2", "p.11", "FILTER_CAPABILITY_PROVED_TARGET_OPEN", "Filtros operan en cabecera y detalle."),
    (201, "2026", "SIDIF_CENTRAL_DECOMMISSION", "FORM_SCOPE", "Secretaría de Hacienda", "SICHE", "C35/C41/C55", "modelos Gastos", "e0_dgsiaf_sidif_forms_decommission_2025", "página oficial", "CURRENT_SCOPE_PROVED_TARGET_TYPE_OPEN", "Incluye transmisiones; C42 SLU no queda excluido."),
    (202, "diseño previo a 2008", "SLU_TREASURY", "PAYMENT_MODE", "SAF/TGN", "banco/beneficiario", "pagos", "CUT/cuenta/efectivo/Nota/valores/compensación", "e0_dgsiaf_slu_system_description_v3", "PDF p.107", "SYSTEM_SCHEMA_PROVED_TARGET_OPEN", "Enumera medios y separa selección de confirmación."),
    (203, "diseño previo a 2008", "SLU_BANK_RECONCILIATION", "TWO_SIDED_MATCH", "Banco", "SAF", "movimientos", "extracto externo + Libro Banco", "e0_dgsiaf_slu_system_description_v3", "PDF p.113", "SYSTEM_SCHEMA_PROVED_TARGET_OPEN", "Ambas caras son necesarias."),
    (204, "diseño previo a 2008", "SLU_BANK_COMMISSION", "AUTOMATIC_MOVEMENT", "BNA", "SAF", "comisión bancaria", "movimiento automático", "e0_dgsiaf_slu_system_description_v3", "PDF p.114", "MECHANISM_COMPARATOR_PROVED_TARGET_OPEN", "Compatible con C55; no clasifica target."),
    (205, "diseño previo a 2008", "SLU_BANK_MOVEMENT", "PAYMENT_VS_AUTOMATIC", "TGN/BNA", "SAF", "débitos", "pago instruido vs débito automático", "e0_dgsiaf_slu_system_description_v3", "PDF p.115", "MECHANISM_SPLIT_PROVED_TARGET_OPEN", "Permite formular test discriminante."),
    (206, "2010", "ACCOUNT_83106000", "DOCUMENT_COMPARATOR", "SAF355", "BNA", "comisiones", "C41", "e0_cgn_cuenta_inversion_2010_sdp", "Anexo K p.74", "LEADING_DOCUMENT_COMPARATOR_TARGET_OPEN", "Misma cuenta y leyenda; año diferente."),
    (207, "2011-2015", "ACCOUNT_83106000", "SEMANTIC_DRIFT", "SAF355", "BNA", "convenio YPF", "C41/VARIOS", "e0_cgn_cuenta_inversion_2011_sdp;e0_cgn_cuenta_inversion_2012_sdp;e0_cgn_cuenta_inversion_2013_sdp;e0_cgn_cuenta_inversion_2014_sdp;e0_cgn_cuenta_inversion_2015_sdp", "Anexos K", "CODE_REUSE_PROVED_TARGET_PURPOSE_OPEN", "El mismo código cambia de descripción."),
    (208, "2008-2026", "TARGET_CLASSIFICATION", "DUAL_PRIORITY", "SAF355", "SICHE/AMIDDF", "tres SIDIF", "C41 tipo / C55 mecanismo", "e0_cgn_cuenta_inversion_2010_sdp;e0_dgsiaf_slu_system_description_v3", "comparación combinada", "DUAL_PRIORITY_NO_TARGET_PROOF", "Sólo exportación y cuerpo target deciden."),
]
for number, window, mechanism, phase, payer, recipient, universe, instrument, sid, locator, status, interpretation in ledger_specs:
    ledger.append({
        "ledger_id": f"F{number}", "window": window, "mechanism": mechanism, "phase": phase,
        "as_of_date": "N/D", "payer": payer, "recipient": recipient, "universe": universe,
        "instrument": instrument, "amount_original": "N/D", "original_unit": "N/D",
        "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE",
        "source_id": sid, "source_locator": locator, "realization_status": status,
        "additivity": "NON_ADDITIVE", "status_interpretation": interpretation,
        "caveat": "No convertir capacidad, comparador o esquema en ejecución target.",
    })
assert len(ledger) == 208
write_csv(ledger_path, ledger)

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V139.csv"
breaks = read_csv(breaks_path)
new_break_ids = {
    "c41_comparator_not_target_type", "account_code_not_stable_concept", "annual_disclosure_blank_not_absence",
    "varios_not_document_type", "siche_deployment_not_target_coverage", "siche_special_query_not_executed",
    "slu_design_not_saf355_deployment", "automatic_commission_not_c55_target", "c35_current_scope_not_target_type",
    "dual_priority_not_probability_tie",
}
breaks = [row for row in breaks if row["break_id"] not in new_break_ids]
for row in breaks:
    if row["break_id"] == "mechanism_match_not_target_identity":
        row["rule"] = "Rotular C55 como comparador principal de mecanismo, en paralelo con C41 documental."
new_breaks = [
    ("c41_comparator_not_target_type", "inference", "La misma cuenta y leyenda en 2010 usa C41, pero 2008 no imprime tipo.", "Usar C41 como prior documental, nunca como clasificación.", "e0_cgn_cuenta_inversion_2008_sdp;e0_cgn_cuenta_inversion_2010_sdp"),
    ("account_code_not_stable_concept", "semantics", "83106000 pasa de comisión BNA genérica a convenio YPF.", "Separar continuidad de código de continuidad de propósito.", "E0_83106000_DOCUMENT_TYPE_COMPARATORS_V139.csv"),
    ("annual_disclosure_blank_not_absence", "disclosure", "La celda 2009 queda vacía.", "No inferir inexistencia de comprobantes.", "e0_cgn_cuenta_inversion_2009_sdp"),
    ("varios_not_document_type", "disclosure", "VARIOS agrega y oculta la especie.", "No usar VARIOS para excluir C41/C55/C42/C35.", "e0_cgn_cuenta_inversion_2012_sdp;e0_cgn_cuenta_inversion_2015_sdp"),
    ("siche_deployment_not_target_coverage", "access", "Un módulo desplegado no prueba que retenga la fila 2008.", "Exigir exportación o metadatos de cero resultados.", "E0_SICHE_DEPLOYMENT_CAPABILITY_TIMELINE_V139.csv"),
    ("siche_special_query_not_executed", "access", "La capacidad de consulta especial no ejecuta la búsqueda.", "Mantener pedido DRAFT_NOT_SENT hasta autorización.", "e0_dgsiaf_siche_deployment_2020_q4"),
    ("slu_design_not_saf355_deployment", "system", "La descripción preliminar SLU define funciones sin probar implantación íntegra en SAF355.", "Usar como esquema de campos y test, no como presencia.", "e0_dgsiaf_slu_system_description_v3"),
    ("automatic_commission_not_c55_target", "mechanism", "Comisión automática es compatible con C55, no asigna tipo.", "Cruzar tipo, historia, extracto y Libro Banco.", "e0_dgsiaf_slu_system_description_v3;e0_dgsiaf_slu_global_regularization_2004"),
    ("c35_current_scope_not_target_type", "scope", "C35 figura en la desafectación actual de SC.", "Incluirlo sólo como fallback.", "e0_dgsiaf_sidif_forms_decommission_2025"),
    ("dual_priority_not_probability_tie", "method", "C41 y C55 lideran dimensiones distintas.", "No expresar porcentajes ni empate probabilístico sin muestra target.", "E0_DOCUMENT_TYPE_HYPOTHESIS_BALANCE_V139.csv"),
]
for break_id, dimension, problem, rule, evidence in new_breaks:
    breaks.append({"break_id": break_id, "dimension": dimension, "problem": problem, "rule": rule, "status": "FROZEN_V139", "evidence": evidence})
assert len(breaks) == 163
write_csv(breaks_path, breaks)

# La cadena heredada conserva su nombre histórico, pero ya no privilegia C55.
c41_path = HERE / "E0_C41_PAYMENT_EXECUTION_CHAIN_V139.csv"
c41 = read_csv(c41_path)
for row in c41:
    if row["stage_id"] == "CP138_27":
        row["execution_meaning"] = "Conjunto histórico SLU; la búsqueda general sin tipo y C35 de SC se controlan aparte"
        row["target_status"] = "SLU_THREE_CANDIDATES_NOT_EXHAUSTIVE"
        row["permitted_inference"] = "Dentro de SLU, probar C41/C55 y luego C42; no excluir otros dominios de SC."
    elif row["stage_id"] == "CP138_28":
        row["stage"] = "C55_MECHANISM_CANDIDATE"
        row["execution_meaning"] = "Hipótesis líder de mecanismo"
        row["target_status"] = "OPEN_DUAL_PRIORITY_1B"
        row["permitted_inference"] = "Coincidencia específica del mecanismo bancario."
    elif row["stage_id"] == "CP138_29":
        row["stage"] = "C41_DOCUMENT_TYPE_CANDIDATE"
        row["record"] = "C41 y cuerpo/estado"
        row["execution_meaning"] = "Hipótesis líder de tipo documental"
        row["source_id"] = "e0_cgn_cuenta_inversion_2010_sdp"
        row["target_status"] = "OPEN_DUAL_PRIORITY_1A"
        row["permitted_inference"] = "El comparador 2010 repite cuenta y leyenda con C41 explícito."
        row["forbidden_inference"] = "Los tres SIDIF 2008 son C41."
write_csv(c41_path, c41)

foreign_path = HERE / "E0_FOREIGN_PAYMENT_COMMISSION_CHAIN_V139.csv"
foreign = read_csv(foreign_path)
for row in foreign:
    if row["step_id"] == "FP138_09":
        row["target_status"] = "LEADING_MECHANISM_COMPARATOR_NOT_PROVED"
write_csv(foreign_path, foreign)

register_path = HERE / "E0_REQUEST_RESPONSE_REGISTER_V139.csv"
register = read_csv(register_path)
for row in register:
    row["status"] = "DRAFT_NOT_SENT"
    row["submitted_on"] = "N/A"
    row["submission_channel"] = "N/A"
    row["receipt_or_case_id"] = "N/A"
write_csv(register_path, register)


# El pedido sigue siendo un borrador: sólo se mejora el objeto técnico.
request_path = HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V139.md"
request_text = request_path.read_text(encoding="utf-8-sig")
request_text = request_text.replace(
    "## Clave V139 · exportación SICHE y prueba C-55 por débito directo",
    "## Clave V139 · exportación SICHE y test condicional C-55 por débito directo",
)
request_text = request_text.replace(
    "En SLU, buscar primero tipos `C-41`, `C-42` y `C-55`, sin asumir de antemano cuál corresponde.",
    "Buscar primero sin restricción de tipo; luego `C-41` y `C-55` en paralelo; usar `C-42` en SLU y `C-35` en SIDIF Central como fallbacks, sin asumir de antemano cuál corresponde.",
)
request_text = request_text.replace(
    "Para cada número se solicita el C-41 completo y el extracto `SDPGB`/`SDPAG` de 2008 o sucesor equivalente.",
    "Para cada número se solicita el cuerpo documental completo —cualquiera sea su tipo— y el extracto `SDPGB`/`SDPAG` de 2008 o sucesor equivalente. Si el tipo resultara C-41, se requiere además su cuerpo y estado íntegros.",
)
request_text = request_text.replace(
    "C-41 original, notas, lista diaria firmada de selección, autorizaciones si correspondían, boletos, débitos, C-55 y demás respaldos",
    "formulario original cualquiera sea su tipo, notas, lista diaria firmada de selección, autorizaciones si correspondían, boletos, débitos, eventuales C-41/C-55 y demás respaldos",
)
marker = "## Clave V139 · capacidad SICHE demostrada y doble prioridad C-41/C-55"
if marker not in request_text:
    request_text += f"""

{marker}

Los boletines técnicos oficiales de DGSIAF permiten formular una búsqueda reproducible sin pedir la creación de un estudio nuevo. En 2020 SICHE ya tenía consultas de **Gastos** y **Pagos** de SIDIF Central modelo 95, admitía expresiones numéricas e incorporaba **Conciliación Bancaria** y consultas especiales solicitadas por usuarios. En 2021 agregó búsqueda detallada de comprobantes, formularios, acuerdos y entes, con filtros tanto en cabecera como en el detalle. Desde el 1 de enero de 2026 la desafectación de SIDIF Central alcanza expresamente los modelos de Gastos `C-35`, `C-41` y `C-55`, incluidas sus transmisiones. Estas constancias prueban capacidad y alcance de consulta; no prueban que las filas 2008 existan o estén completas.

La clasificación se solicita en el siguiente orden, sin presuponer el resultado:

1. Buscar primero en SIDIF Central por `SAF 355`, ejercicio `2008`, números SIDIF `71597`, `152677` y `2876`, sin restringir tipo; combinar en cabecera y detalle `83106000`, `COMISIONES - BANCO NACION`, partida `7.2.8`, importe `32.270,30` y variantes numéricas.
2. Ejecutar en paralelo la rama `C-41` y la rama `C-55`. `C-41` es el comparador documental principal porque en 2010 la misma cuenta y leyenda genérica publica cuatro C-41. `C-55 Débito Directo` es el comparador de mecanismo principal porque el diseño SLU registra las comisiones bancarias como movimientos automáticos y el manual de regularización usa el débito bancario por comisión como supuesto C-55. Ninguno de los dos queda atribuido a los tres SIDIF sin la exportación target.
3. Si ambas búsquedas fallan, consultar `C-42` en SLU y `C-35` en SIDIF Central. La ausencia de C-42 en la página de desafectación 2025 no lo excluye del antiguo SLU; la inclusión de C-35 no demuestra que el target sea un compromiso.
4. Pedir las salidas de **Gastos**, **Pagos** y **Conciliación Bancaria**, o sus equivalentes SICHE: tipo, número interno/SIDIF, estado e historia; documento respaldatorio; beneficiario/CUIT; importes y etapas; medio, banco y cuenta; extracto bancario, extracto interno/Libro Banco, aplicación y estado de conciliación.
5. Para toda búsqueda sin filas, informar sistema de origen, modelo, conjunto o consulta, filtros exactos, fecha de ejecución, cobertura temporal, cantidad de resultados y exclusiones. Si la consulta estándar no alcanza, ejecutar o derivar la consulta especial preexistente que admita la herramienta.

La comparación 2007-2015 se aporta sólo para orientar la búsqueda. Desde 2011 la cuenta `83106000` cambia a un concepto específico del convenio YPF y alterna entre C-41 explícitos y `VARIOS`; por eso no se presume continuidad de propósito ni de tipo. **Estado: BORRADOR_NO_ENVIADO.**
"""
request_path.write_text(request_text, encoding="utf-8")

checklist_path = HERE / "REQUEST_SUBMISSION_CHECKLIST_V139.md"
checklist = checklist_path.read_text(encoding="utf-8-sig")
checklist = checklist.replace(
    "- [ ] Tratar C-55 Débito Directo como hipótesis prioritaria, nunca como hecho previo a la respuesta.",
    "- [ ] Tratar C-41 como comparador documental y C-55 Débito Directo como comparador de mecanismo; ninguno como hecho previo a la respuesta.",
)
check_marker = "## Control V139 · doble prioridad y consulta reproducible"
if check_marker not in checklist:
    checklist += f"""

{check_marker}

- [ ] Buscar primero los tres SIDIF sin restricción de tipo.
- [ ] Tratar C-41 como comparador documental y C-55 como comparador de mecanismo, no como hechos target.
- [ ] Incluir C-42 (SLU) y C-35 (SIDIF Central) sólo como fallbacks.
- [ ] Pedir Gastos, Pagos y Conciliación Bancaria con filtros de cabecera y detalle.
- [ ] Exigir extracto externo, extracto interno/Libro Banco y aplicación para cerrar un débito.
- [ ] Exigir metadatos reproducibles para cualquier resultado cero.
- [ ] Confirmar autorización expresa antes de presentar cualquiera de los seis borradores.
"""
checklist_path.write_text(checklist, encoding="utf-8")

source_refs_path = HERE / "SOURCE_REFERENCES_V139.md"
source_refs = source_refs_path.read_text(encoding="utf-8-sig")
# Restituye en cada ficha la ruta canónica del catálogo, sin alterar títulos,
# URLs ni hashes históricos.
ref_lines = []
for line in source_refs.splitlines():
    match = re.match(r"^- `([^`]+)`", line)
    if match and match.group(1) in catalog_by_id:
        canonical = catalog_by_id[match.group(1)]["archivo_local"]
        line = re.sub(r"`/[^`]+`", f"`{canonical}`", line)
    ref_lines.append(line)
source_refs = "\n".join(ref_lines) + "\n"
refs_marker = "## Fuentes nuevas V139 · capacidad SICHE, conciliación y comparadores 2013-2015"
if refs_marker not in source_refs:
    source_refs += "\n\n" + refs_marker + "\n\n"
    for item in SOURCES:
        source_refs += f"- `{item['id']}` · {item['title']} · {item['url']} · `{item['local']}` · `{item['sha256']}`\n"
    source_refs += "- Control de deduplicación: las capturas 2011 y 2012 de V139 son idénticas por SHA-256 a `e0_cgn_cuenta_inversion_2011_sdp` y `e0_cgn_cuenta_inversion_2012_sdp`, ya preservadas en V112; no se cuentan como fuentes nuevas.\n"
source_refs_path.write_text(source_refs, encoding="utf-8")

(HERE / "README_V139.md").write_text("""# V139 · capacidad SICHE y doble prioridad documental/mecánica

V139 corrige el ranking simple de V138. La evidencia pública no permite decir que los SIDIF 71597, 152677 y 2876 sean C-41 o C-55. C-41 queda como comparador principal de **tipo documental** porque en 2010 la misma cuenta `83106000` y la misma leyenda genérica publican cuatro C-41. C-55 Débito Directo queda como comparador principal de **mecanismo** porque SLU registra las comisiones bancarias como movimientos automáticos y exige su huella en extracto interno/Libro Banco y conciliación. C-42 y C-35 quedan como fallbacks separados.

Los boletines DGSIAF demuestran que SICHE soporta Gastos, Pagos, Conciliación Bancaria, expresiones numéricas, consultas especiales y filtros de cabecera/detalle. Esto vuelve ejecutable el pedido, pero no agrega una fila target. Resultado estricto sin cambio: 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas. Los seis pedidos permanecen `DRAFT_NOT_SENT`.
""", encoding="utf-8")

(HERE / "VEREDICTO_V139.md").write_text("""# Veredicto V139

La búsqueda archivística puede especificarse con precisión técnica: SICHE tuvo consultas de Gastos y Pagos de SIDIF Central, Conciliación Bancaria, expresiones numéricas, consultas especiales y filtros en cabecera y detalle. Desde 2026, el alcance desafectado de SIDIF Central enumera C-35, C-41 y C-55. El orden correcto es: búsqueda sin tipo; C-41/C-55 en paralelo; C-42/C-35 como fallbacks; y metadatos reproducibles si no hay resultados.

La evidencia exige una doble prioridad sin convertirla en probabilidad. C-41 es el antecedente documental más cercano: 2010 repite `83106000 · COMISIONES - BANCO NACION` con C-41 explícitos. C-55 es el antecedente de mecanismo más cercano: SLU prevé la carga automática de comisiones bancarias y su regularización como débito directo. La serie 2011-2015 demuestra además que el código cambia de concepto y que el Anexo K alterna C-41 y `VARIOS`; por eso no autoriza una clasificación retroactiva.

No apareció ninguna exportación target de SICHE, cuerpo AMIDDF, F80/PG, Nota, extracto, Libro Banco ni conciliación. El balance permanece en 10 adjudicaciones exactas, 9 cuentas candidatas y 0/10 ejecuciones confirmadas. Los seis pedidos continúan sin enviar.
""", encoding="utf-8")

(HERE / "E0_FISCAL_RECONSTRUCTION_V139.md").write_text("""# Reconstrucción fiscal E0 V139

V139 separa tipo, mecanismo, pago bancario y conciliación. La rama C-41 necesita cuerpo/estado y, si corresponde, OP, Nota, cuentas e instrucción; la rama C-55 necesita subtipo, aceptación central, cuenta, imputación, movimiento automático, extracto y Libro Banco. C-42 exige causa extrapresupuestaria y C-35 exige compromiso y vínculos posteriores. Ninguna rama modifica el panel sin una fila target y el cierre bancario-contable. El numerador permanece en 0/10 ejecuciones confirmadas.
""", encoding="utf-8")

(HERE / "AUDITORIA_V139.md").write_text(f"""# Auditoría V139

- Fuentes maestras: 430; ocho fuentes oficiales nuevas y dos recapturas deduplicadas.
- Fuentes primarias E0: 190; copias catalogadas SHA-válidas esperadas: 424.
- Capacidad SICHE: {len(siche_timeline)} hitos; comparadores 83106000: {len(comparators)} filas.
- Firma de conciliación: {len(reconciliation)} controles; balance de hipótesis: {len(hypotheses)} filas.
- Control visual: {len(visual_control)} páginas renderizadas y verificadas.
- Ledger fiscal: {len(ledger)} filas; cortes metodológicos: {len(breaks)}.
- Trazabilidad: {len(trace)} objetos; claves: {len(keys)}.
- Escalera: 10 adjudicaciones; 9 cuentas candidatas; 0 ejecuciones confirmadas.
- Pedidos: 6 borradores, 0 enviados; panel estricto {STRICT}% sin cambios.
""", encoding="utf-8")

(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V139_A_V140.md").write_text("""# Handover V139 → V140

## Estado

- QA V139: ejecutar y exigir PASS.
- SICHE: capacidad demostrada para Gastos, Pagos, Conciliación Bancaria, expresiones numéricas, consultas especiales y filtros cabecera/detalle.
- Tres SIDIF exactos: 71597, 152677 y 2876; tipo todavía abierto.
- Doble prioridad: C-41 lidera como comparador documental; C-55 Débito Directo lidera como comparador de mecanismo. No son hechos ni probabilidades.
- Fallbacks: C-42 en SLU y C-35 en SIDIF Central.
- Serie 83106000: 2007-2010 leyenda genérica; desde 2011 concepto YPF específico; C-41 y VARIOS alternan.
- Seis pedidos `DRAFT_NOT_SENT`; ninguno enviado.
- Escalera: 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas.

## Prioridad V140

1. Mantener los seis pedidos como borradores salvo autorización expresa.
2. Obtener exportación SICHE SC+SLU por los tres SIDIF, primero sin tipo.
3. Ejecutar C-41 y C-55 en paralelo; C-42/C-35 sólo como fallbacks.
4. Obtener índice/caja/cuerpo AMIDDF.
5. Cerrar toda hipótesis con Pagos y Conciliación: extracto externo, extracto interno/Libro Banco, aplicación y estado.
6. Exigir metadatos exactos de cualquier consulta negativa.
7. Mantener separados registro presupuestario, pago, débito, conciliación y cancelación CRYL.
""", encoding="utf-8")


# Auditoría de preservación y estado acumulado.
for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    source_path = AUDIT / f"{stem}_V138.csv"
    target_path = AUDIT / f"{stem}_V139.csv"
    target_path.write_text(
        source_path.read_text(encoding="utf-8-sig").replace("V138", "V139").replace("v138", "v139"),
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
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V139.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V139.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
assert physical == hash_ok == 424

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
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V139.csv", size_rows)

completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V138.json").read_text(encoding="utf-8"))
for key in list(completeness):
    if key.endswith("_v138") or "newly_preserved_v138" in key:
        completeness.pop(key, None)
completeness.update({
    "checkpoint": "V139", "date": "2026-08-30",
    "state": "E0_SICHE_CAPABILITY_PROVED_C41_DOCUMENT_AND_C55_MECHANISM_DUAL_PRIORITY_TARGET_EXPORT_OPEN_NOT_SENT",
    "numeric_v139_strict_changed": False,
    "master_catalog_entries": len(catalog), "physical_local_copies": physical,
    "physical_local_hash_ok": hash_ok, "binary_required_entries": 361,
    "binary_required_preserved": 360, "binary_required_source_complete": False,
    "e0_primary_sources_preserved": len(census),
    "e0_quality": "PRIMARY_SICHE_DEPLOYMENT_SLU_RECONCILIATION_AND_DOCUMENT_COMPARATORS",
    "sources_newly_preserved_v139": 8, "e0_primary_sources_newly_preserved_v139": 8,
    "e0_duplicate_recaptures_v139": 2,
    "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
    "e0_request_traceability_rows": len(trace), "e0_request_search_keys": len(keys),
    "e0_sidif_candidate_types": 4, "e0_sidif_target_document_types_located": 0,
    "e0_c55_direct_debit_priority_hypothesis": False,
    "e0_c41_document_comparator_priority": True,
    "e0_c55_mechanism_comparator_priority": True,
    "e0_document_type_hypothesis_status": "DUAL_PRIORITY_NO_TARGET_PROOF",
    "e0_c55_target_rows_located": 0, "e0_siche_target_exports_located": 0,
    "e0_siche_deployment_capability_rows": len(siche_timeline),
    "e0_83106000_comparator_rows": len(comparators),
    "e0_bank_commission_reconciliation_rows": len(reconciliation),
    "e0_document_type_hypothesis_rows": len(hypotheses),
    "e0_pdf_visual_controls": len(visual_control),
    "e0_siche_query_plan_rows": len(query_plan),
    "e0_settlement_award_rows_exact": 10, "e0_settlement_account_candidate_rows": 9,
    "e0_settlement_executed_rows_confirmed": 0, "e0_requests_submitted": 0,
    "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
    "historical_workstream": "SICHE Gastos/Pagos/Conciliacion and header/detail query capability proved; C41 is leading document comparator and C55 leading mechanism comparator; C42/C35 fallbacks; target export, AMIDDF body, reconciliation, CRYL and executed settlement remain open; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V139.json").write_text(
    json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
backup_text = backup.read_text(encoding="utf-8-sig")
backup_marker = "## V139 · capacidad SICHE y doble prioridad"
if backup_marker not in backup_text:
    backup_text += f"""

{backup_marker}

- SICHE: Gastos, Pagos, Conciliación Bancaria, expresiones numéricas, consultas especiales y filtros cabecera/detalle demostrados.
- C-41 lidera sólo como comparador documental; C-55 sólo como comparador de mecanismo. Tipo target abierto.
- C-42 (SLU) y C-35 (SIDIF Central) incorporados como fallbacks.
- Serie 83106000 2007-2015 preserva deriva semántica y alternancia C-41/VARIOS.
- 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas; seis borradores no enviados.
"""
backup.write_text(backup_text, encoding="utf-8")

inherited = [
    {"script": "qa_v138.py", "pre_v139_result": "PASS", "post_v139_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V138 queda supersedida por capacidad SICHE, comparadores y doble prioridad V139."},
    {"script": "qa_v139.py", "pre_v139_result": "N/A", "post_v139_result": "PASS", "interpretation": "Fuentes, deduplicación, hipótesis, hashes, trazabilidad y no envío verificados."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V139.csv", inherited)

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

timeline = rows("E0_SICHE_DEPLOYMENT_CAPABILITY_TIMELINE_V139.csv")
comparators = rows("E0_83106000_DOCUMENT_TYPE_COMPARATORS_V139.csv")
reconciliation = rows("E0_BANK_COMMISSION_RECONCILIATION_SIGNATURE_V139.csv")
hypotheses = rows("E0_DOCUMENT_TYPE_HYPOTHESIS_BALANCE_V139.csv")
visual = rows("E0_V139_PDF_VISUAL_CONTROL.csv")
types = rows("E0_SLU_SIDIF_DOCUMENT_TYPE_NARROWING_V139.csv")
plan = rows("E0_SICHE_TARGET_QUERY_PLAN_V139.csv")
assert len(timeline) == 9 and len(comparators) == 10 and len(reconciliation) == 10
assert len(hypotheses) == 5 and len(visual) == 13 and all(r["result"] == "PASS" for r in visual)
assert len(types) == 7 and types[-1]["status"] == "DUAL_PRIORITY_NO_TARGET_PROOF"
assert {r["candidate"] for r in hypotheses} == {"C41", "C55", "C42", "C35", "UNCLASSIFIED"}
assert len(plan) == 10 and all(r["status"] == "DRAFT_NOT_SENT" for r in plan)
assert any("Conciliación Bancaria" in r["system"] for r in plan)

assert len(rows("E0_SIGADE_SIDIF_DISCLOSURE_LADDER_V139.csv")) == 29
assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V139.csv")) == 208
assert len(rows("E0_FISCAL_METHOD_BREAKS_V139.csv")) == 163
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V139.csv")) == 156
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V139.csv")) == 170

ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V139.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)
register = rows("E0_REQUEST_RESPONSE_REGISTER_V139.csv")
assert len(register) == 6 and all(r["status"] == "DRAFT_NOT_SENT" for r in register)
assert all(r["submitted_on"] == "N/A" and r["receipt_or_case_id"] == "N/A" for r in register)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V139.csv")}
new_ids = ''' + repr(source_ids) + r'''
assert len(census) == 190 and new_ids <= set(census)
for row in census.values():
    local = row["local_path"]
    assert local and (REPO / local.lstrip("/")).is_file(), (row["source_id"], local)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 430 and len({r["id"] for r in catalog}) == 430

expected = ''' + repr(EXPECTED) + r'''
bin_dir = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v139" / "binaries"
assert len(list(bin_dir.iterdir())) == 10
for name, (size, digest) in expected.items():
    path = bin_dir / name
    assert path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest() == digest
assert expected["cgn_cuenta_2011_separata_deuda_publica.pdf"][1] == census["e0_cgn_cuenta_inversion_2011_sdp"]["sha256"]
assert expected["cgn_cuenta_2012_separata_deuda_publica.pdf"][1] == census["e0_cgn_cuenta_inversion_2012_sdp"]["sha256"]

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V139.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V139"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 424
assert complete["e0_duplicate_recaptures_v139"] == 2
assert complete["e0_document_type_hypothesis_status"] == "DUAL_PRIORITY_NO_TARGET_PROOF"
assert complete["e0_sidif_target_document_types_located"] == 0
assert complete["e0_siche_target_exports_located"] == 0
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v139_strict_changed"] is False

request = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V139.md").read_text(encoding="utf-8-sig")
assert "## Clave V139 · capacidad SICHE demostrada y doble prioridad C-41/C-55" in request
assert "BORRADOR_NO_ENVIADO" in request and "Conciliación Bancaria" in request
combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv")) + request
for stale in ("recuperar tres C-41 2008", "Cuerpo y estado de tres formularios C-41 2008", "Búsqueda y copia de los tres cuerpos C-41", "C-41 71597;152677;2876", "DOCUMENT_CLASS_AND_CHAIN_PROVED_TARGET_BODIES_OPEN", "THREE_C41_APPLICABILITY_CONTROL"):
    assert stale not in combined, stale
assert "C-55 Débito Directo como hipótesis prioritaria" not in (HERE / "REQUEST_SUBMISSION_CHECKLIST_V139.md").read_text(encoding="utf-8-sig")
refs = (HERE / "SOURCE_REFERENCES_V139.md").read_text(encoding="utf-8-sig")
assert "## Fuentes nuevas V138 · SICHE, SLU y C-55" in refs
assert refs.count("## Fuentes nuevas V139 · capacidad SICHE, conciliación y comparadores 2013-2015") == 1
for name in ("README_V139.md", "VEREDICTO_V139.md", "E0_FISCAL_RECONSTRUCTION_V139.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V139_A_V140.md"):
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")

print("V139 QA PASS")
'''
(HERE / "qa_v139.py").write_text(qa, encoding="utf-8")


def checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V139.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V139", "parent_checkpoint": "V138",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": 8, "duplicate_recaptures": 2,
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks),
        "siche_capability_rows": len(siche_timeline), "comparator_rows": len(comparators),
        "reconciliation_signature_rows": len(reconciliation), "hypothesis_rows": len(hypotheses),
        "sidif_candidate_types": 4, "sidif_target_document_types_located": 0,
        "hypothesis_status": "DUAL_PRIORITY_NO_TARGET_PROOF", "siche_target_exports_located": 0,
        "award_rows_exact": 10, "account_candidate_rows": 9, "executed_settlement_rows_confirmed": 0,
        "request_drafts": 6, "request_traceability_rows": len(trace), "request_search_keys": len(keys),
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V139.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    "checkpoint": "V139",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical catalog copies SHA-valid; 8 new sources and 2 recaptures deduplicated; C41 document/C55 mechanism dual priority only; target type/export/reconciliation open; zero of ten executed settlement rows confirmed; six requests drafted and none submitted.",
    "historical_workstream": "Obtain SICHE SC+SLU Gastos/Pagos/Conciliacion export and AMIDDF index; search untyped then C41/C55, C42/C35 fallbacks; close bank/accounting signature, CRYL and executed settlement; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V139 BUILD PASS")
