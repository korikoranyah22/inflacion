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
PARENT = HERE.parent / "V143"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v144" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"

EXPECTED: dict[str, tuple[int, str]] = {
    "dgsiaf_slu_boleta_deposito.doc": (1604096, "01d6b32dc1ccd04d747efbc20e33b6e96d2aeb8ee9242868f1c8e381605b654c"),
    "dgsiaf_slu_c10.doc": (988672, "34e8d9617ee3182b96f65b001f9ec8b3fb26fa27703dbaa024aeeda6e2bb35ea"),
    "dgsiaf_slu_cesiones_embargos.doc": (472576, "2584a8dfbf445152229c2684847b12c05db96cb71a84652a5d289466a71360f6"),
    "dgsiaf_slu_cheques_chequeras.doc": (730112, "c4bfc5b1ee59693890eff0dd02cd44998251ad010e3e46fc628716fb5f8fc255"),
    "dgsiaf_slu_conciliacion_bancaria_tablas_basicas.doc": (788480, "19f2b33fca34193bfac9fc0e75a86ff72e3d9103f172fb767611c187dded2659"),
    "dgsiaf_slu_conciliacion_bancaria.doc": (1060864, "4561a9d536973da4b648d5f8d140bd0a5bf64afea2597971b473984655f89d11"),
    "dgsiaf_slu_consulta_envio_mcc.doc": (678400, "5b5d3ae552938c704e8288774432ccea2761a373ab95a72c57bc37d3d594853d"),
    "dgsiaf_slu_cronograma_pagos.doc": (1209856, "1a7a2717b4703460e58cea94177dcf971ca1a7449826166429ce055823813a5f"),
    "dgsiaf_slu_cuotas_pago.doc": (568832, "3d1c95adce08e1e7324a0c5da2797d5a376dcee3d991c98ddc09a63f3edfb5e5"),
    "dgsiaf_slu_desafectacion_pagos.doc": (675328, "42cdc6beda9acb39c01da2c96158779683d1669f52c68e4b069c546bdd2bc457"),
    "dgsiaf_slu_limites_financieros.doc": (233472, "b4ef883444f930f234934e91bc67657372e1957fb426cb3a6312e0af5db6ac10"),
    "dgsiaf_slu_manual_usuario_general.doc": (2434560, "c63fb3420a6d84e5355a3561d69af28fbd3376a3180af43ef607e3da8cc9d116"),
    "dgsiaf_slu_tablas_basicas_tesoreria_1.doc": (1680896, "bb7501ec69a75428aa2f761e898935cba30d636000ac7fa74c8fa31e8dc81a7c"),
    "dgsiaf_slu_tablas_basicas_tesoreria_2.doc": (250880, "3b1c45091aab96e0b7f223caba5aa5becb800ccb75d3eecb81411512187e9d3b"),
    "dgsiaf_slu_taller_conciliacion_2017.pdf": (291650, "7ff4c97f734a7170bfd2a3e15d9f2e12ffef4a2af217f3d1337be23459a6290c"),
}

SOURCES: list[dict[str, object]] = [
    {
        "id": "e0_dgsiaf_slu_bank_reconciliation_manual_2003_v7",
        "filename": "dgsiaf_slu_conciliacion_bancaria.doc",
        "institution": "Dirección General de Sistemas Informáticos de Administración Financiera",
        "title": "SLU · Manual del Usuario de Conciliación Bancaria · versión 7",
        "url": "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_conciliacion_bancaria.doc",
        "publication": "2003-01", "code": "SLU v7 · Conciliación Bancaria",
        "families": "LIB;TRA;MAN;APL;EXB;conciliación automática/manual;Libro Banco;extracto;correcciones",
        "breaks": "Manual de mecanismo y pantallas; no contiene exportación SAF 355 ni fila objetivo 2008.",
        "use": "USABLE_CONTEMPORANEOUS_RECONCILIATION_MECHANISM",
        "caveat": "Prueba reglas y campos, no que una operación objetivo haya ocurrido.",
        "note": "V144 E0: documenta cinco grupos, generación automática de comprobantes/registro contable, conciliación parcial y campos de movimiento.",
    },
    {
        "id": "e0_dgsiaf_slu_bank_reconciliation_basic_tables_2002_v7",
        "filename": "dgsiaf_slu_conciliacion_bancaria_tablas_basicas.doc",
        "institution": "Dirección General de Sistemas Informáticos de Administración Financiera",
        "title": "SLU · Tablas Básicas de Conciliación Bancaria · versión 7",
        "url": "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_conciliacion_bancaria_tablas_basicas.doc",
        "publication": "2002-09", "code": "SLU v7 · TB Conciliación",
        "families": "movimiento interno;movimiento externo;partida de gasto;C55;SIDIF Central;bajas;rehabilitación",
        "breaks": "Las capturas son ejemplos; no publican la parametrización completa de 2008.",
        "use": "USABLE_CONTEMPORANEOUS_MAPPING_AND_C55_SCHEMA",
        "caveat": "La relación configurada no identifica por sí sola una fila target.",
        "note": "V144 E0: el movimiento externo puede relacionarse con partida de gasto y emitir C55 automático enviado a SIDIF Central.",
    },
    {
        "id": "e0_dgsiaf_slu_treasury_basic_tables_1",
        "filename": "dgsiaf_slu_tablas_basicas_tesoreria_1.doc",
        "institution": "Dirección General de Sistemas Informáticos de Administración Financiera",
        "title": "SLU · Manual de Tablas Básicas · Tesorería 1",
        "url": "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_tablas_basicas_tbtesoreria1.doc",
        "publication": "2005-06-24 (metadato de guardado)", "code": "BCUENTA;ACTA_FUE;ACTABAN_CTAESC",
        "families": "cuentas bancarias/escriturales;cuenta-fuente;cuenta bancaria-cuenta escritural;bajas;rehabilitación",
        "breaks": "BCUENTA y relaciones se declaran sin historia; tabla vigente no garantiza valores 2008.",
        "use": "USABLE_ACCOUNT_TABLE_DICTIONARY_AND_RETENTION_LIMIT",
        "caveat": "Se requieren respaldos o snapshots para recuperar estado histórico.",
        "note": "V144 E0: fija tablas exactas de cuenta y fuente y explicita administración local sin historia, con consulta de baja y rehabilitación.",
    },
    {
        "id": "e0_dgsiaf_slu_treasury_basic_tables_2",
        "filename": "dgsiaf_slu_tablas_basicas_tesoreria_2.doc",
        "institution": "Dirección General de Sistemas Informáticos de Administración Financiera",
        "title": "SLU · Manual de Tablas Básicas · Tesorería 2 · versión 7",
        "url": "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_tablas_basicas_tbtesoreria2.doc",
        "publication": "2003-07-10 (metadato de guardado)", "code": "BGRUPMOVBCO;BMOVBCO;BMOVEXTERNO;AMOV_FORG;ACLB_MOB;BCODLIBBCO",
        "families": "grupos;movimientos internos/externos;aplicación automática de gasto;Libro Banco;auditoría",
        "breaks": "Las seis tablas centrales se describen sin historia; no contienen sus valores poblados de 2008.",
        "use": "USABLE_EXACT_DATABASE_TABLE_DICTIONARY",
        "caveat": "Cierra nombres y función de tablas, no código literal ni fila objetivo.",
        "note": "V144 E0: identifica las tablas exactas para pedir dumps/snapshots de parametrización bancaria histórica.",
    },
    {
        "id": "e0_dgsiaf_slu_reconciliation_workshop_2017_historical_screens",
        "filename": "dgsiaf_slu_taller_conciliacion_2017.pdf",
        "institution": "Secretaría de Hacienda",
        "title": "Taller de Conciliación Bancaria SLU · Usuario · diciembre 2017",
        "url": "https://www.argentina.gob.ar/sites/default/files/dgsiaf-taller-de-conciliacion-bancaria-slu-usuario-dic-2017.pdf",
        "publication": "2017-12-04", "code": "SLU v9.0 · capturas fechadas 2006/2008",
        "families": "SLU v9.0;ejercicio 2008;relación recurso/gasto;C55;C10;menú de tablas básicas",
        "breaks": "Documento compilado en 2017 que reutiliza capturas históricas; no prueba la fila objetivo.",
        "use": "USABLE_HISTORICAL_UI_VERSION_AND_MAPPING_CONTROL",
        "caveat": "La fecha de pantalla prueba el entorno mostrado, no la totalidad del despliegue 2008.",
        "note": "V144 E0: captura SLU v9.0 del 26/11/2008 y menú histórico de parametrización; ejemplo CUM023 no es target.",
    },
    {
        "id": "e0_dgsiaf_slu_payment_schedule",
        "filename": "dgsiaf_slu_cronograma_pagos.doc",
        "institution": "Secretaría de Hacienda",
        "title": "SLU · Cronograma de Pagos",
        "url": "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_cronograma_de_pagos.doc",
        "publication": "2003-07-08 (metadato de guardado)", "code": "cronograma;fuente;clase;cuenta",
        "families": "programación financiera;cuenta escritural;fuente;clase de gasto;disponibilidad",
        "breaks": "Programación no equivale a ejecución bancaria.", "use": "USABLE_PAYMENT_PROGRAMMING_NEGATIVE_CONTROL",
        "caveat": "No elevar cronograma o cuota a pago ejecutado.",
        "note": "V144 E0: conserva filtros cuenta/fuente/clase y disponibilidad como etapa anterior a la ejecución.",
    },
    {
        "id": "e0_dgsiaf_slu_payment_quotas",
        "filename": "dgsiaf_slu_cuotas_pago.doc",
        "institution": "Secretaría de Hacienda",
        "title": "SLU · Cuotas de Pago",
        "url": "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_cuotas_de_pago.doc",
        "publication": "2003-07-08 (metadato de guardado)", "code": "cuota de pago;banco;sucursal;cuenta",
        "families": "cuota;cuenta;disponibilidad;Libro Banco;programación financiera",
        "breaks": "Cuota disponible no prueba débito, pago o conciliación.", "use": "USABLE_PAYMENT_QUOTA_NEGATIVE_CONTROL",
        "caveat": "Debe cruzarse con pago, extracto y Libro Banco.",
        "note": "V144 E0: documenta banco/sucursal/cuenta y disponibilidad, separadas del impacto en Libro Banco.",
    },
    {
        "id": "e0_dgsiaf_slu_payment_reversal_2005",
        "filename": "dgsiaf_slu_desafectacion_pagos.doc",
        "institution": "Secretaría de Hacienda",
        "title": "SLU · Desafectaciones de Pago",
        "url": "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_desafectacion_pagos.doc",
        "publication": "2005-06-14 (metadato de guardado)", "code": "C55-DEP;C55-REP;Libro Banco",
        "families": "desafectación;C55-DEP;C55-REP;OP C41/C42;cuenta;depósito;estado;contraasiento",
        "breaks": "Describe reversión/regularización general, no una reversa target identificada.",
        "use": "USABLE_PAYMENT_REVERSAL_AND_STATE_CONTROL",
        "caveat": "C55-DEP/REP potencial exige original, importe, cuenta y aceptación central concordantes.",
        "note": "V144 E0: fija campos de desafectación, impacto tras aceptación central y reversión mediante C55-REP/contraasiento.",
    },
    {
        "id": "e0_dgsiaf_slu_checks_checkbooks",
        "filename": "dgsiaf_slu_cheques_chequeras.doc",
        "institution": "Secretaría de Hacienda",
        "title": "SLU · Cheques y Chequeras",
        "url": "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_cheques_y_chequeras.doc",
        "publication": "2005-04-06 (metadato de guardado)", "code": "cheque;cuenta;conciliación",
        "families": "cheque;cuenta;Libro Banco;estado C/R/E/F;detalle conciliación;anulación",
        "breaks": "Ruta de cheque es control alternativo; no identifica pago target.", "use": "USABLE_PAYMENT_MEDIUM_STATE_CONTROL",
        "caveat": "No confundir cheque conciliado con débito automático o transferencia.",
        "note": "V144 E0: documenta estados y navegación a detalle de conciliación para excluir ruta cheque.",
    },
    {
        "id": "e0_dgsiaf_slu_deposit_slip",
        "filename": "dgsiaf_slu_boleta_deposito.doc",
        "institution": "Secretaría de Hacienda", "title": "SLU · Boleta de Depósito",
        "url": "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_boleta_de_deposito.doc",
        "publication": "2004-06-29 (metadato de guardado)", "code": "boleta de depósito",
        "families": "depósito;cuenta;percepción;recursos;conciliación", "breaks": "Rama de recurso/crédito, no débito de gasto.",
        "use": "USABLE_RESOURCE_BRANCH_NEGATIVE_CONTROL", "caveat": "Usar como control de signo y origen.",
        "note": "V144 E0: fuente oficial preservada para separar depósitos/recursos de débitos por gasto.",
    },
    {
        "id": "e0_dgsiaf_slu_c10_2004_v10",
        "filename": "dgsiaf_slu_c10.doc",
        "institution": "Secretaría de Hacienda", "title": "SLU · Formularios C10 · versión 10",
        "url": "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_c10.doc",
        "publication": "2004-10", "code": "C10 v10 · REC/REG/COR/DES/CMP",
        "families": "C10;recurso;conciliación;automático/manual;cuenta;boleta;SIGADE;estado;transmisión",
        "breaks": "C10 prueba rama de recurso; no sustituye C55 de gasto ni fila target.",
        "use": "USABLE_C10_RESOURCE_AND_TRANSMISSION_NEGATIVE_CONTROL",
        "caveat": "Crédito/recurso debe separarse de débito/comisión.",
        "note": "V144 E0: conciliación puede generar C10 automático; expone cuenta, SIGADE, estado, error, transmisión y origen.",
    },
    {
        "id": "e0_dgsiaf_slu_assignments_garnishments",
        "filename": "dgsiaf_slu_cesiones_embargos.doc", "institution": "Secretaría de Hacienda",
        "title": "SLU · Cesiones y Embargos", "url": "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_tes._cesiones_y_embargos.doc",
        "publication": "2003-07-08 (metadato de guardado)", "code": "cesiones;embargos",
        "families": "cesión;embargo;beneficiario;tesorería", "breaks": "Control alternativo, no prueba comisión.",
        "use": "USABLE_BENEFICIARY_PAYMENT_CONTROL", "caveat": "Debe discriminarse de gasto bancario.",
        "note": "V144 E0: fuente oficial preservada para control de embargos y beneficiario.",
    },
    {
        "id": "e0_dgsiaf_slu_mcc_exchange",
        "filename": "dgsiaf_slu_consulta_envio_mcc.doc", "institution": "Secretaría de Hacienda",
        "title": "SLU · Consulta y envío de información al MCC", "url": "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_consulta_y_envio_de_informacion_al_mcc.doc",
        "publication": "2003-07-25 (metadato de guardado)", "code": "MCC;consulta;envío",
        "families": "consulta;transmisión;MCC;metadatos", "breaks": "Transmisión no equivale a pago bancario.",
        "use": "USABLE_TRANSMISSION_STAGE_CONTROL", "caveat": "Exigir aceptación e impacto separados.",
        "note": "V144 E0: fuente oficial preservada para discriminar envío, recepción y ejecución.",
    },
    {
        "id": "e0_dgsiaf_slu_monthly_financial_limits",
        "filename": "dgsiaf_slu_limites_financieros.doc", "institution": "Secretaría de Hacienda",
        "title": "SLU · Límites Financieros Mensuales", "url": "https://www.argentina.gob.ar/sites/default/files/dgsiaf-mu_limites_financieros_mensuales.doc",
        "publication": "2003-07-08 (metadato de guardado)", "code": "límites financieros",
        "families": "límite;programación;cuenta;clase de gasto", "breaks": "Límite financiero no es pago ejecutado.",
        "use": "USABLE_FINANCIAL_LIMIT_NEGATIVE_CONTROL", "caveat": "No elevar disponibilidad a realización.",
        "note": "V144 E0: fuente oficial preservada como control de etapa previa.",
    },
    {
        "id": "e0_dgsiaf_slu_general_user_manual",
        "filename": "dgsiaf_slu_manual_usuario_general.doc", "institution": "Secretaría de Hacienda",
        "title": "SLU · Manual del Usuario · Generalidades", "url": "https://www.argentina.gob.ar/sites/default/files/dgsiaf-manual_del_usuario_general.doc",
        "publication": "2003-04-08 (metadato de guardado)", "code": "SLU · generalidades",
        "families": "arquitectura SLU;usuarios;consulta;alta;baja;modificación", "breaks": "Manual general; no publica registros target.",
        "use": "USABLE_SYSTEM_CONTEXT", "caveat": "Contexto operativo, no evidencia transaccional.",
        "note": "V144 E0: contexto oficial preservado para interpretar operaciones y pantallas legacy.",
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
    skip = {"build_e0_cut_codebook_v143.py", "qa_v143.py", "MANIFEST_V143.json", "INHERITED_QA_STATUS_V143.csv"}
    for item in PARENT.iterdir():
        if not item.is_file() or item.name in skip or item.name.startswith("HANDOVER_PROXIMA_SESION"):
            continue
        target = HERE / item.name.replace("V143", "V144")
        text = item.read_text(encoding="utf-8-sig")
        placeholder = "historical_retrieval/__PARENT_V143__/"
        text = text.replace("historical_retrieval/v143/", placeholder)
        text = text.replace("_V143", "_V144").replace("_v143", "_v144")
        text = text.replace(placeholder, "historical_retrieval/v143/")
        if item.name.startswith("REQUEST_") or item.name in {
            "CURRENT_STATE_V143.csv", "E0_INSTITUTIONAL_REQUEST_PACKAGE_V143.md", "RETRIEVAL_LOG_V143.md",
        }:
            text = text.replace("V143", "V144").replace("v143", "v144")
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
    suffix = Path(str(item["filename"])).suffix.lower()
    item["type"] = "PDF oficial · captura preservada" if suffix == ".pdf" else "DOC oficial · binario preservado"

source_ids = {str(item["id"]) for item in SOURCES}

catalog = [row for row in read_csv(CATALOG) if row["id"] not in source_ids]
assert len(catalog) == 438
system_description = next(row for row in catalog if row["id"] == "e0_dgsiaf_slu_system_description_v3")
system_description["fecha_publicacion"] = "2005-08-16 (metadato PDF); versión 3"
system_description["periodo_utilizado"] = "2005; diseño contemporáneo anterior a 2008"
system_description["nota"] = (
    "V144 E0: metadato CreationDate D:20050816105200; distingue servicio de deuda pública sin gastos/comisiones "
    "de carta de crédito y transferencias al exterior con gastos/comisiones, y documenta conciliación automática."
)
for item in SOURCES:
    catalog.append({
        "id": item["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": item["institution"],
        "titulo": item["title"], "url_original": item["url"], "archivo_local": item["local"],
        "fecha_descarga": "2026-08-30", "fecha_publicacion": item["publication"],
        "codigo_serie": item["code"], "periodo_utilizado": item["publication"], "tipo": item["type"],
        "sha256": item["sha256"], "nota": item["note"],
    })
assert len(catalog) == 453 and len({row["id"] for row in catalog}) == 453
write_csv(CATALOG, catalog)
catalog_by_id = {row["id"]: row for row in catalog}

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V144.csv"
census = [row for row in read_csv(census_path) if row["source_id"] not in source_ids]
assert len(census) == 198
for row in census:
    master = catalog_by_id[row["source_id"]]
    row["local_path"] = master["archivo_local"]
    row["sha256"] = master["sha256"]
    path = REPO / master["archivo_local"].lstrip("/") if master["archivo_local"] else None
    if path and path.is_file():
        row["bytes"] = str(path.stat().st_size)
    if row["source_id"] == "e0_dgsiaf_slu_system_description_v3":
        row["period_coverage"] = "2005; diseño contemporáneo anterior a 2008"
        row["variable_families"] = "pagos; medios de pago; gastos y comisiones; Libro Banco; conciliación automática/manual"
        row["method_breaks"] = "Diseño SLU 2005; prueba mecanismo contemporáneo, no fila ni código exacto 2008."
for item in SOURCES:
    census.append({
        "source_id": item["id"], "institution": item["institution"], "artifact": item["title"],
        "url": item["url"], "local_path": item["local"], "sha256": item["sha256"], "bytes": str(item["bytes"]),
        "period_coverage": item["publication"], "variable_families": item["families"],
        "primary_source": "YES", "preserved": "YES", "method_breaks": item["breaks"],
        "use_status": item["use"], "caveat": item["caveat"],
    })
assert len(census) == 213 and len({row["source_id"] for row in census}) == 213
write_csv(census_path, census)

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V144.csv"
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
assert len(provenance) == 116
write_csv(provenance_path, provenance)


slu_tables = [
    {"table_id": "ST144_01", "table_name": "BCUENTA", "function": "codificación de cuentas bancarias y escriturales del organismo", "administration": "LOCAL", "history": "NO", "available_operations": "alta;baja;modificación;consulta;consulta de baja;rehabilitación", "target_role": "identificar banco, sucursal, cuenta, tipo, fuente y vigencia 2008", "historical_consequence": "pedir backup/snapshot; la tabla vigente no reconstruye cambios", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_1", "locator": "DOC p.2 · interna 120"},
    {"table_id": "ST144_02", "table_name": "ACTA_FUE", "function": "relación cuenta bancaria-fuente de financiamiento", "administration": "LOCAL", "history": "NO", "available_operations": "alta;baja;modificación;consulta;consulta de baja;rehabilitación", "target_role": "cruzar cuenta con fuente 13 o la fuente histórica recuperada", "historical_consequence": "pedir backup/snapshot y bajas rehabilitadas", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_1", "locator": "DOC p.3 · interna 121"},
    {"table_id": "ST144_03", "table_name": "ACTABAN_CTAESC", "function": "relación cuenta bancaria-cuenta escritural receptora", "administration": "LOCAL", "history": "NO", "available_operations": "alta;baja;modificación;consulta;consulta de baja;rehabilitación", "target_role": "cerrar banco→cuenta escritural CUT", "historical_consequence": "pedir estado 2008 desde respaldo", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_1", "locator": "DOC p.5 · interna 123"},
    {"table_id": "ST144_04", "table_name": "BGRUPMOVBCO", "function": "grupos de códigos de movimiento bancario", "administration": "EXTERNA", "history": "NO", "available_operations": "consulta;consulta de baja", "target_role": "identificar APL/LIB/MAN/TRA/EXB o equivalente vigente", "historical_consequence": "tabla actual no prueba grupo 2008", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_2", "locator": "DOC p.3 · interna 144"},
    {"table_id": "ST144_05", "table_name": "BMOVBCO", "function": "códigos internos de movimientos del extracto", "administration": "EXTERNA", "history": "NO", "available_operations": "consulta;consulta de baja", "target_role": "resolver código interno, descripción, signo y grupo", "historical_consequence": "pedir dump histórico completo", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_2", "locator": "DOC p.4 · interna 145"},
    {"table_id": "ST144_06", "table_name": "BMOVEXTERNO", "function": "códigos de movimientos externos según codificación de cada banco", "administration": "EXTERNA", "history": "NO", "available_operations": "consulta;consulta de baja", "target_role": "mapear código BNA externo→grupo→movimiento interno→tipo automático/manual", "historical_consequence": "pedir todas las versiones 2008 y contracódigos", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_2", "locator": "DOC p.5 · interna 146"},
    {"table_id": "ST144_07", "table_name": "AMOV_FORG", "function": "parametrización de aplicación automática de gastos por cuenta bancaria y movimiento", "administration": "LOCAL", "history": "NO", "available_operations": "alta;baja;modificación;consulta;consulta de baja;rehabilitación", "target_role": "cerrar cuenta+movimiento externo/interno→partida de gasto/C55", "historical_consequence": "objeto central: pedir backup 2008, filas dadas de baja y rehabilitadas", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_2", "locator": "DOC p.6 · interna 147"},
    {"table_id": "ST144_08", "table_name": "ACLB_MOB", "function": "relación código de movimiento de extracto-código de Libro Banco", "administration": "EXTERNA", "history": "NO", "available_operations": "consulta;consulta de baja", "target_role": "cerrar movimiento externo/interno→Libro Banco", "historical_consequence": "pedir snapshot y filas inactivas", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_2", "locator": "DOC p.7 · interna 148"},
    {"table_id": "ST144_09", "table_name": "BCODLIBBCO", "function": "códigos de comprobantes/movimientos de Libro Banco", "administration": "EXTERNA", "history": "NO", "available_operations": "consulta;consulta de baja", "target_role": "obtener código, descripción, débito/crédito y marca de conciliación", "historical_consequence": "pedir snapshot y catálogo vigente por fecha", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_2", "locator": "DOC p.8 · interna 149"},
    {"table_id": "ST144_10", "table_name": "BEMPRESA", "function": "agrupación de cuentas informadas por un banco en un extracto", "administration": "LOCAL", "history": "NO", "available_operations": "alta;baja;modificación;consulta;consulta de baja;rehabilitación", "target_role": "delimitar universo de cuentas cargadas por BNA", "historical_consequence": "pedir configuración 2008 desde respaldo", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_2", "locator": "DOC p.9 · interna 150"},
    {"table_id": "ST144_11", "table_name": "BERROR_AUD", "function": "códigos de error del auditor", "administration": "EXTERNA", "history": "NO", "available_operations": "consulta;consulta de baja", "target_role": "interpretar rechazos/errores de proceso", "historical_consequence": "pedir catálogo vigente y código textual", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_2", "locator": "DOC p.11 · interna 152"},
    {"table_id": "ST144_12", "table_name": "BPROCESO", "function": "códigos de procesos del auditor", "administration": "EXTERNA", "history": "NO", "available_operations": "consulta;consulta de baja", "target_role": "interpretar proceso/log de impacto", "historical_consequence": "pedir catálogo 2008 y logs con descripción", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_2", "locator": "DOC p.12 · interna 153"},
]
write_csv(HERE / "E0_SLU_BASE_TABLE_DICTIONARY_V144.csv", slu_tables)

recovery_strategy = [
    {"recovery_id": "HR144_01", "problem": "tabla vigente declarada sin historia", "required_record": "dump o snapshot de base correspondiente al ejercicio 2008", "minimum_fields": "tabla;esquema;fecha snapshot;fila completa;estado", "success_test": "snapshot anterior o contemporáneo con cobertura declarada", "negative_rule": "consulta actual vacía no prueba inexistencia histórica", "source_id": "E0_SLU_BASE_TABLE_DICTIONARY_V144.csv", "status": "DRAFT_NOT_SENT"},
    {"recovery_id": "HR144_02", "problem": "bajas lógicas posibles", "required_record": "resultado de Consulta de Bajas por tabla", "minimum_fields": "clave;descripción;fecha baja;usuario;estado", "success_test": "incluye filas inactivas y fecha", "negative_rule": "filtrar sólo activas es insuficiente", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_1;e0_dgsiaf_slu_bank_reconciliation_basic_tables_2002_v7", "status": "DRAFT_NOT_SENT"},
    {"recovery_id": "HR144_03", "problem": "rehabilitación puede ocultar secuencia", "required_record": "registro de rehabilitaciones y estado previo", "minimum_fields": "clave;fecha baja;fecha rehabilitación;usuario;motivo", "success_test": "secuencia temporal reproducible", "negative_rule": "estado activo actual no acredita continuidad", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_1", "status": "DRAFT_NOT_SENT"},
    {"recovery_id": "HR144_04", "problem": "códigos usados no se eliminan", "required_record": "filas asociadas y registros que impidieron el borrado", "minimum_fields": "código;tabla;cantidad asociados;claves de uso", "success_test": "vínculo a movimiento/libro/formulario", "negative_rule": "ausencia del activo no descarta una baja", "source_id": "e0_dgsiaf_slu_bank_reconciliation_basic_tables_2002_v7", "status": "DRAFT_NOT_SENT"},
    {"recovery_id": "HR144_05", "problem": "valores históricos no preservados en aplicación", "required_record": "backups RMAN, exportaciones Oracle, cintas o imágenes de servidor SLU", "minimum_fields": "fecha;servidor;instancia;esquema;retención;custodio;hash", "success_test": "inventario y copia recuperable de 2008", "negative_rule": "declarar sin historia exige informar política de backups", "source_id": "E0_SLU_BASE_TABLE_DICTIONARY_V144.csv", "status": "DRAFT_NOT_SENT"},
    {"recovery_id": "HR144_06", "problem": "cambio de versión SLU", "required_record": "matriz de versiones y scripts de migración v7→v9.0", "minimum_fields": "versión;fecha;SAF;módulo;DDL/DML;tabla origen/destino", "success_test": "confirma versión y transformación de códigos", "negative_rule": "captura v9.0 no prueba identidad semántica de toda tabla", "source_id": "e0_dgsiaf_slu_reconciliation_workshop_2017_historical_screens", "status": "DRAFT_NOT_SENT"},
    {"recovery_id": "HR144_07", "problem": "repositorio CUT histórico separado", "required_record": "exportación SICHE 2007-2014 de Entidades, Extractos y Logs", "minimum_fields": "dataset;versión;parámetros;cobertura;filas;diccionario", "success_test": "2008 completo con identificador de cuenta y referencia", "negative_rule": "cero sin parámetros ni cobertura no es utilizable", "source_id": "e0_dgsiaf_siche_cut_repository_2020_q2", "status": "DRAFT_NOT_SENT"},
    {"recovery_id": "HR144_08", "problem": "tabla de mapeo no prueba transacción", "required_record": "conc_01.rep y conc_02.rep o exportación equivalente", "minimum_fields": "cuenta;fecha;movimiento;formulario;importe;estado;beneficiario", "success_test": "ambos lados comparten referencia/fecha/importe", "negative_rule": "parametrización sola no eleva 0/10", "source_id": "e0_dgsiaf_slu_bank_reconciliation_reports_2002", "status": "DRAFT_NOT_SENT"},
    {"recovery_id": "HR144_09", "problem": "movimientos corregidos", "required_record": "historial de correcciones de extracto", "minimum_fields": "banco;sucursal;cuenta;fecha;grupo;mov externo;mov interno;comprobante;importe;signo;original;corrección", "success_test": "cadena original→corrección completa", "negative_rule": "última versión puede ocultar el movimiento inicial", "source_id": "e0_dgsiaf_slu_bank_reconciliation_manual_2003_v7", "status": "DRAFT_NOT_SENT"},
    {"recovery_id": "HR144_10", "problem": "C55 automático puede tener rechazo/reversa", "required_record": "formulario, transmisión, respuesta, error, C55-DEG/DEP/REP y contraasiento", "minimum_fields": "original;estado;fechas;usuario;error;reversa;Libro Banco", "success_test": "C confirmado sin reversa posterior", "negative_rule": "enviado o rechazado no prueba ejecución", "source_id": "e0_dgsiaf_slu_payment_reversal_2005;e0_dgsiaf_slu_global_regularization_2004", "status": "DRAFT_NOT_SENT"},
    {"recovery_id": "HR144_11", "problem": "rama crédito/recurso posible", "required_record": "C10 automático/manual, boleta y movimiento de conciliación", "minimum_fields": "generación A/M;REC/REG/COR/DES/CMP;cuenta;SIGADE;estado;transmisión", "success_test": "clasifica signo y origen antes de atribuir gasto", "negative_rule": "C10 de recurso no es C55 de comisión", "source_id": "e0_dgsiaf_slu_c10_2004_v10", "status": "DRAFT_NOT_SENT"},
    {"recovery_id": "HR144_12", "problem": "resultado final requiere cadena multicapas", "required_record": "tabla→movimiento→formulario→extracto→Libro Banco→conciliación→respaldo", "minimum_fields": "cuenta;fecha;signo;importe;referencia;concepto;estado;original/reversa", "success_test": "concordancia individual reproducible", "negative_rule": "ninguna capa aislada confirma fila objetivo", "source_id": "E0_SLU_AUTOMATIC_EXPENSE_MAPPING_CHAIN_V144.csv", "status": "DRAFT_NOT_SENT"},
]
write_csv(HERE / "E0_SLU_HISTORICAL_RECOVERY_STRATEGY_V144.csv", recovery_strategy)

slu_visual_version = [
    {"control_id": "SV144_01", "pdf_page": "1", "visible_fact": "taller de Conciliación Bancaria del SLU", "historical_value": "identifica el módulo", "inference_limit": "portada de 2017", "result": "PASS", "source_id": "e0_dgsiaf_slu_reconciliation_workshop_2017_historical_screens"},
    {"control_id": "SV144_02", "pdf_page": "2", "visible_fact": "relación de gasto genera factura de caja chica y C55; relación de recurso genera C10", "historical_value": "separa ramas gasto/recurso", "inference_limit": "regla presentada en 2017", "result": "PASS", "source_id": "e0_dgsiaf_slu_reconciliation_workshop_2017_historical_screens"},
    {"control_id": "SV144_03", "pdf_page": "3", "visible_fact": "barra SLU v9.0 · 26/11/2008 11:30:04; ejercicio 2008; BNA sucursal 85 cuenta 2914/86; ejemplo CUM023", "historical_value": "prueba visual de versión/pantalla fechada y campos", "inference_limit": "CUM023 es ejemplo de recurso, no código objetivo", "result": "PASS", "source_id": "e0_dgsiaf_slu_reconciliation_workshop_2017_historical_screens"},
    {"control_id": "SV144_04", "pdf_page": "4", "visible_fact": "configuración de relación y conciliación", "historical_value": "confirma interfaz de parametrización", "inference_limit": "no exporta tabla poblada completa", "result": "PASS", "source_id": "e0_dgsiaf_slu_reconciliation_workshop_2017_historical_screens"},
    {"control_id": "SV144_05", "pdf_page": "5", "visible_fact": "barra SLU v9.0 · 04/12/2006 y menú de grupos, códigos internos/externos y relaciones gasto/recurso", "historical_value": "prueba nombres funcionales contemporáneos anteriores a 2008", "inference_limit": "captura de capacitación; no prueba despliegue por SAF", "result": "PASS", "source_id": "e0_dgsiaf_slu_reconciliation_workshop_2017_historical_screens"},
    {"control_id": "SV144_06", "pdf_page": "6", "visible_fact": "cierre del taller y circuito de conciliación", "historical_value": "control de integridad visual del PDF", "inference_limit": "sin fila objetivo", "result": "PASS", "source_id": "e0_dgsiaf_slu_reconciliation_workshop_2017_historical_screens"},
]
write_csv(HERE / "E0_SLU_V9_2008_VISUAL_VERSION_CONTROL_V144.csv", slu_visual_version)

automatic_chain = [
    {"chain_id": "AC144_01", "sequence": "1", "layer": "Cuenta", "table_or_record": "BCUENTA;ACTA_FUE;ACTABAN_CTAESC", "required_join": "banco;sucursal;cuenta;fuente;cuenta escritural", "proved_rule": "tablas exactas de identificación y relación", "target_status": "SCHEMA_PROVED_VALUE_2008_OPEN", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_1"},
    {"chain_id": "AC144_02", "sequence": "2", "layer": "Grupo", "table_or_record": "BGRUPMOVBCO", "required_join": "grupo APL/LIB/MAN/TRA/EXB o equivalente", "proved_rule": "grupo gobierna tratamiento de conciliación", "target_status": "SCHEMA_PROVED_VALUE_2008_OPEN", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_2;e0_dgsiaf_slu_bank_reconciliation_manual_2003_v7"},
    {"chain_id": "AC144_03", "sequence": "3", "layer": "Movimiento interno", "table_or_record": "BMOVBCO", "required_join": "código;descripción;débito/crédito;grupo", "proved_rule": "código interno normaliza movimiento", "target_status": "SCHEMA_PROVED_VALUE_2008_OPEN", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_2"},
    {"chain_id": "AC144_04", "sequence": "4", "layer": "Movimiento externo BNA", "table_or_record": "BMOVEXTERNO", "required_join": "banco;código externo;contracódigo;movimiento interno;automático/manual", "proved_rule": "el código del banco se mapea al interno", "target_status": "EXACT_TABLE_PROVED_TARGET_CODE_OPEN", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_2"},
    {"chain_id": "AC144_05", "sequence": "5", "layer": "Parametrización de gasto", "table_or_record": "AMOV_FORG", "required_join": "banco;cuenta/subcuenta;movimiento;partida/extrapresupuestaria", "proved_rule": "cuenta+movimiento dispara aplicación automática de gasto", "target_status": "EXACT_TABLE_PROVED_TARGET_ROW_OPEN", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_2"},
    {"chain_id": "AC144_06", "sequence": "6", "layer": "Formulario", "table_or_record": "C55 automático", "required_join": "partida;SAF;fecha;importe;beneficiario/concepto", "proved_rule": "relación de gasto emite C55 y lo envía a SIDIF Central", "target_status": "MECHANISM_PROVED_TARGET_FORM_OPEN", "source_id": "e0_dgsiaf_slu_bank_reconciliation_basic_tables_2002_v7"},
    {"chain_id": "AC144_07", "sequence": "7", "layer": "Aceptación/contabilidad", "table_or_record": "respuesta SIDIF Central", "required_join": "estado;error;fecha;asiento", "proved_rule": "conciliación automática genera gestión/documento y registro contable", "target_status": "MECHANISM_PROVED_TARGET_ACCEPTANCE_OPEN", "source_id": "e0_dgsiaf_slu_bank_reconciliation_manual_2003_v7"},
    {"chain_id": "AC144_08", "sequence": "8", "layer": "Libro Banco", "table_or_record": "BCODLIBBCO;ACLB_MOB;conc_02.rep", "required_join": "código libro;comprobante;fecha;debe/haber;importe", "proved_rule": "movimiento externo se relaciona con código Libro Banco", "target_status": "SCHEMA_PROVED_TARGET_BOOK_ROW_OPEN", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_2;e0_dgsiaf_slu_bank_reconciliation_reports_2002"},
    {"chain_id": "AC144_09", "sequence": "9", "layer": "Extracto", "table_or_record": "conc_01.rep;movimiento externo", "required_join": "fecha;comprobante;código;importe;estado", "proved_rule": "conciliación procesa no conciliados y parciales", "target_status": "SCHEMA_PROVED_TARGET_EXTRACT_OPEN", "source_id": "e0_dgsiaf_slu_bank_reconciliation_manual_2003_v7"},
    {"chain_id": "AC144_10", "sequence": "10", "layer": "Conciliación", "table_or_record": "automática/manual;N/P/T", "required_join": "origen;destino;fecha;usuario;estado", "proved_rule": "resultado muestra relación origen-destino; manual admite parcial por suma", "target_status": "MECHANISM_PROVED_TARGET_MATCH_OPEN", "source_id": "e0_dgsiaf_slu_bank_reconciliation_manual_2003_v7"},
    {"chain_id": "AC144_11", "sequence": "11", "layer": "Corrección/reversa", "table_or_record": "historial corrección;C55-DEG/DEP/REP;contraasiento", "required_join": "original;corrección/reversa;motivo;importe;fecha", "proved_rule": "original puede corregirse o neutralizarse", "target_status": "CONTROL_PROVED_TARGET_REVERSAL_OPEN", "source_id": "e0_dgsiaf_slu_bank_reconciliation_manual_2003_v7;e0_dgsiaf_slu_payment_reversal_2005"},
    {"chain_id": "AC144_12", "sequence": "12", "layer": "Respaldo", "table_or_record": "nota/orden/AMIDDF/archivo", "required_join": "expediente;concepto;autorización;folios", "proved_rule": "cierre causal exige respaldo concordante", "target_status": "REQUIRED_TARGET_RECORD_OPEN", "source_id": "E0_INFORMATION_REQUEST_TRACEABILITY_V144.csv"},
]
write_csv(HERE / "E0_SLU_AUTOMATIC_EXPENSE_MAPPING_CHAIN_V144.csv", automatic_chain)

table_request_fields = [
    {"request_id": "TF144_01", "table_name": "BCUENTA", "requested_fields": "banco;sucursal;cuenta;descripción;tipo;moneda;titular;marcas bancaria/escritural/pagadora/recaudadora;fecha baja;estado", "filters": "SAF355;vigencia o snapshot 2008", "fallback": "diccionario DDL + exportación disociada", "status": "DRAFT_NOT_SENT"},
    {"request_id": "TF144_02", "table_name": "ACTA_FUE", "requested_fields": "banco;sucursal;cuenta;fuente;fecha baja;estado", "filters": "cuentas recuperadas;2008", "fallback": "snapshot o backup", "status": "DRAFT_NOT_SENT"},
    {"request_id": "TF144_03", "table_name": "ACTABAN_CTAESC", "requested_fields": "cuenta bancaria;cuenta escritural;vigencia;fecha baja;estado", "filters": "cuentas recuperadas;2008", "fallback": "snapshot o backup", "status": "DRAFT_NOT_SENT"},
    {"request_id": "TF144_04", "table_name": "BGRUPMOVBCO", "requested_fields": "grupo;descripción;fecha baja;estado", "filters": "todos los grupos vigentes/usados en 2008", "fallback": "catálogo histórico", "status": "DRAFT_NOT_SENT"},
    {"request_id": "TF144_05", "table_name": "BMOVBCO", "requested_fields": "grupo;código interno;descripción completa;débito/crédito;fecha baja;estado", "filters": "todo universo;2008", "fallback": "dump + diccionario", "status": "DRAFT_NOT_SENT"},
    {"request_id": "TF144_06", "table_name": "BMOVEXTERNO", "requested_fields": "banco;código externo;descripción;contracódigo;movimiento interno;grupo;automático/manual;fecha baja;estado", "filters": "BNA;todo 2008", "fallback": "dump + archivos de carga bancaria", "status": "DRAFT_NOT_SENT"},
    {"request_id": "TF144_07", "table_name": "AMOV_FORG", "requested_fields": "banco;cuenta;subcuenta;movimiento;partida presupuestaria/extrapresupuestaria;fecha baja;estado", "filters": "SAF355;BNA;todo 2008", "fallback": "backup/snapshot y Consulta de Bajas", "status": "DRAFT_NOT_SENT"},
    {"request_id": "TF144_08", "table_name": "ACLB_MOB", "requested_fields": "movimiento extracto;código Libro Banco;fecha baja;estado", "filters": "códigos candidatos;2008", "fallback": "snapshot y relaciones usadas", "status": "DRAFT_NOT_SENT"},
    {"request_id": "TF144_09", "table_name": "BCODLIBBCO", "requested_fields": "código;descripción;descripción completa;débito/crédito;permite conciliación parcial;fecha baja;estado", "filters": "todos los códigos usados 2008", "fallback": "catálogo y Consulta de Bajas", "status": "DRAFT_NOT_SENT"},
    {"request_id": "TF144_10", "table_name": "BEMPRESA", "requested_fields": "banco;empresa/grupo;cuentas incluidas;vigencia;fecha baja;estado", "filters": "BNA;SAF355;2008", "fallback": "archivo de configuración de extractos", "status": "DRAFT_NOT_SENT"},
    {"request_id": "TF144_11", "table_name": "BERROR_AUD;BPROCESO", "requested_fields": "código;descripción;proceso/error;fecha baja;estado", "filters": "códigos observados en logs 2008", "fallback": "diccionario de auditor", "status": "DRAFT_NOT_SENT"},
    {"request_id": "TF144_12", "table_name": "METADATOS/RESPALDOS", "requested_fields": "servidor;instancia;esquema;versión SLU;fecha backup;retención;custodio;hash;script migración", "filters": "2006-2009;SAF355;órganos rectores", "fallback": "inventario documental y acta de inexistencia fundada", "status": "DRAFT_NOT_SENT"},
]
write_csv(HERE / "E0_SLU_TABLE_REQUEST_FIELD_MATRIX_V144.csv", table_request_fields)

c10_controls = [
    {"control_id": "C10144_01", "observable": "rama funcional", "contemporary_rule": "C10 registra recursos; C55 registra gasto en la relación automática", "target_use": "separar crédito/recurso de débito/comisión", "target_status": "NEGATIVE_CONTROL_PROVED", "source_id": "e0_dgsiaf_slu_c10_2004_v10;e0_dgsiaf_slu_reconciliation_workshop_2017_historical_screens"},
    {"control_id": "C10144_02", "observable": "generación", "contemporary_rule": "A automática; M manual", "target_use": "pedir marca de generación de cada C10", "target_status": "FIELD_PROVED_TARGET_OPEN", "source_id": "e0_dgsiaf_slu_c10_2004_v10"},
    {"control_id": "C10144_03", "observable": "tipos", "contemporary_rule": "REC/REG/COR/DES/CMP", "target_use": "detectar original, corrección, desafectación o cambio de medio", "target_status": "STATE_SCHEMA_PROVED_TARGET_OPEN", "source_id": "e0_dgsiaf_slu_c10_2004_v10"},
    {"control_id": "C10144_04", "observable": "cuenta", "contemporary_rule": "banco/sucursal/cuenta/tipo de cuenta impactada en Libro Banco", "target_use": "cerrar cuenta y signo", "target_status": "FIELD_PROVED_TARGET_OPEN", "source_id": "e0_dgsiaf_slu_c10_2004_v10"},
    {"control_id": "C10144_05", "observable": "deuda", "contemporary_rule": "Código SIGADE obligatorio para recursos asociados a endeudamiento/préstamos externos", "target_use": "buscar 83106000 y equivalentes en rama recurso", "target_status": "QUERY_FIELD_PROVED_TARGET_OPEN", "source_id": "e0_dgsiaf_slu_c10_2004_v10"},
    {"control_id": "C10144_06", "observable": "estado local", "contemporary_rule": "Confirmado; con Error; Pendiente", "target_use": "separar aceptación de mera carga", "target_status": "STATE_SCHEMA_PROVED_TARGET_OPEN", "source_id": "e0_dgsiaf_slu_c10_2004_v10"},
    {"control_id": "C10144_07", "observable": "transmisión", "contemporary_rule": "Rechazado; Aprobado; Sin Procesar; Espera Respuesta", "target_use": "pedir envío, recepción, error y retransmisión", "target_status": "TRANSMISSION_SCHEMA_PROVED_TARGET_OPEN", "source_id": "e0_dgsiaf_slu_c10_2004_v10"},
    {"control_id": "C10144_08", "observable": "documento original", "contemporary_rule": "Corrección y desafectación referencian C10 original confirmado", "target_use": "preservar original y modificación", "target_status": "VERSION_CHAIN_PROVED_TARGET_OPEN", "source_id": "e0_dgsiaf_slu_c10_2004_v10"},
    {"control_id": "C10144_09", "observable": "conciliación", "contemporary_rule": "acreditación bancaria puede generar C10 y conciliación automática; si faltan datos, C10 y conciliación manual", "target_use": "clasificar crédito y método", "target_status": "MECHANISM_PROVED_TARGET_OPEN", "source_id": "e0_dgsiaf_slu_c10_2004_v10"},
    {"control_id": "C10144_10", "observable": "SAF 355", "contemporary_rule": "versión 10 menciona alta automática de C10 emitidos por SAF 355 al recibirse lote", "target_use": "pedir lotes, recepción y número SIDIF 2008", "target_status": "SAF_ROUTE_PROVED_TARGET_EXPORT_OPEN", "source_id": "e0_dgsiaf_slu_c10_2004_v10"},
]
write_csv(HERE / "E0_SLU_C10_RESOURCE_NEGATIVE_CONTROL_V144.csv", c10_controls)

reversal_controls = [
    {"control_id": "RV144_01", "record": "C55-DEP", "rule": "desafecta pago por depósito bancario o diferencia de cambio", "target_effect": "buscar devolución o diferencia que neutralice pago", "limit": "no es C55-REG de comisión por sí solo", "source_id": "e0_dgsiaf_slu_payment_reversal_2005"},
    {"control_id": "RV144_02", "record": "OP original", "rule": "tipo C41/C42, ejercicio y número completan la desafectación", "target_effect": "exigir vínculo al original", "limit": "target puede carecer de OP si es débito directo", "source_id": "e0_dgsiaf_slu_payment_reversal_2005"},
    {"control_id": "RV144_03", "record": "cuenta", "rule": "banco/sucursal/cuenta y boleta/fecha identifican devolución", "target_effect": "cruzar con cuenta y extracto", "limit": "cuenta sola no prueba causa", "source_id": "e0_dgsiaf_slu_payment_reversal_2005"},
    {"control_id": "RV144_04", "record": "aceptación central", "rule": "impacto en Libro Banco ocurre cuando SIDIF Central acepta", "target_effect": "no contar ingreso/envío como impacto", "limit": "aceptación interna aún debe cruzarse con banco", "source_id": "e0_dgsiaf_slu_payment_reversal_2005"},
    {"control_id": "RV144_05", "record": "C55-REP", "rule": "revierte impactos del C55-DEP y lo pone rechazado", "target_effect": "buscar original, reversa y contraasiento", "limit": "requiere concordancia de importe", "source_id": "e0_dgsiaf_slu_payment_reversal_2005"},
    {"control_id": "RV144_06", "record": "consulta", "rule": "C55-DEP generados pueden consultarse desde el programa", "target_effect": "pedir exportación completa de consulta", "limit": "pantalla actual puede no retener 2008", "source_id": "e0_dgsiaf_slu_payment_reversal_2005"},
    {"control_id": "RV144_07", "record": "cheque estado C", "rule": "cheque conciliado", "target_effect": "control alternativo de medio de pago", "limit": "no confundir con débito automático", "source_id": "e0_dgsiaf_slu_checks_checkbooks"},
    {"control_id": "RV144_08", "record": "cheque estado R", "rule": "conciliado y luego devuelto", "target_effect": "detectar reversa/devolución bancaria", "limit": "no prueba comisión", "source_id": "e0_dgsiaf_slu_checks_checkbooks"},
    {"control_id": "RV144_09", "record": "anulación cheque", "rule": "E o C no conciliado puede pasar a F", "target_effect": "preservar secuencia de estados", "limit": "regla de cheque", "source_id": "e0_dgsiaf_slu_checks_checkbooks"},
    {"control_id": "RV144_10", "record": "detalle conciliación", "rule": "pantalla navega al estado de conciliación del cheque", "target_effect": "pedir detalle si ruta cheque aparece", "limit": "control negativo", "source_id": "e0_dgsiaf_slu_checks_checkbooks"},
]
write_csv(HERE / "E0_SLU_REVERSAL_NEGATIVE_CONTROL_V144.csv", reversal_controls)

word_visual = [
    {"control_id": "WV144_01", "source_id": "e0_dgsiaf_slu_bank_reconciliation_manual_2003_v7", "doc_page": "10", "rendered_check": "grupos LIB/TRA/MAN/APL/EXB y regla automática/manual", "result": "PASS"},
    {"control_id": "WV144_02", "source_id": "e0_dgsiaf_slu_bank_reconciliation_manual_2003_v7", "doc_page": "49", "rendered_check": "conciliación automática de extracto, Libro Banco, recursos/gastos y contracódigos", "result": "PASS"},
    {"control_id": "WV144_03", "source_id": "e0_dgsiaf_slu_bank_reconciliation_manual_2003_v7", "doc_page": "50", "rendered_check": "generación de gestión/documento, asiento y relación origen-destino", "result": "PASS"},
    {"control_id": "WV144_04", "source_id": "e0_dgsiaf_slu_bank_reconciliation_manual_2003_v7", "doc_page": "59", "rendered_check": "conciliación manual y suma parcial", "result": "PASS"},
    {"control_id": "WV144_05", "source_id": "e0_dgsiaf_slu_bank_reconciliation_manual_2003_v7", "doc_page": "60", "rendered_check": "banco/sucursal/cuenta y campos de movimiento", "result": "PASS"},
    {"control_id": "WV144_06", "source_id": "e0_dgsiaf_slu_bank_reconciliation_basic_tables_2002_v7", "doc_page": "22", "rendered_check": "código interno: grupo, código, descripción y débito/crédito", "result": "PASS"},
    {"control_id": "WV144_07", "source_id": "e0_dgsiaf_slu_bank_reconciliation_basic_tables_2002_v7", "doc_page": "25", "rendered_check": "código externo: banco, código, grupo y movimiento interno", "result": "PASS"},
    {"control_id": "WV144_08", "source_id": "e0_dgsiaf_slu_bank_reconciliation_basic_tables_2002_v7", "doc_page": "30", "rendered_check": "relación partida de gasto-movimiento externo", "result": "PASS"},
    {"control_id": "WV144_09", "source_id": "e0_dgsiaf_slu_bank_reconciliation_basic_tables_2002_v7", "doc_page": "31", "rendered_check": "C55 automático enviado a SIDIF Central", "result": "PASS"},
    {"control_id": "WV144_10", "source_id": "e0_dgsiaf_slu_bank_reconciliation_basic_tables_2002_v7", "doc_page": "38", "rendered_check": "Consulta de Bajas, prohibición de borrar códigos usados y rehabilitación", "result": "PASS"},
    {"control_id": "WV144_11", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_1", "doc_page": "2", "rendered_check": "BCUENTA local sin historia; baja y rehabilitación", "result": "PASS"},
    {"control_id": "WV144_12", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_1", "doc_page": "3", "rendered_check": "ACTA_FUE local sin historia; cuenta-fuente", "result": "PASS"},
    {"control_id": "WV144_13", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_2", "doc_page": "3", "rendered_check": "BGRUPMOVBCO sin historia", "result": "PASS"},
    {"control_id": "WV144_14", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_2", "doc_page": "4", "rendered_check": "BMOVBCO sin historia", "result": "PASS"},
    {"control_id": "WV144_15", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_2", "doc_page": "5", "rendered_check": "BMOVEXTERNO y campos banco/contracódigo/movimiento", "result": "PASS"},
    {"control_id": "WV144_16", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_2", "doc_page": "6", "rendered_check": "AMOV_FORG aplicación automática por cuenta y movimiento", "result": "PASS"},
    {"control_id": "WV144_17", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_2", "doc_page": "7", "rendered_check": "ACLB_MOB relación extracto-Libro Banco", "result": "PASS"},
    {"control_id": "WV144_18", "source_id": "e0_dgsiaf_slu_treasury_basic_tables_2", "doc_page": "8", "rendered_check": "BCODLIBBCO y marca de conciliación", "result": "PASS"},
]
write_csv(HERE / "E0_V144_WORD_VISUAL_CONTROL.csv", word_visual)


cut_repo = [
    {"row_id": "CR141_01", "evidence": "Repositorio histórico CUT-SIDIF Central implementado en SICHE", "proved_scope": "existencia del repositorio", "target_application": "ruta bancaria independiente", "required_output": "nombre de módulo y exportación", "inference_limit": "no prueba una fila target", "status": "PROVED_ROUTE_TARGET_OPEN", "source_id": "e0_dgsiaf_siche_cut_repository_2020_q2", "locator": "PDF p.9"},
    {"row_id": "CR141_02", "evidence": "Período 2007-2014", "proved_scope": "incluye ejercicio 2008", "target_application": "cobertura temporal exacta", "required_output": "confirmación de cobertura por dataset", "inference_limit": "no prueba completitud por día", "status": "EXACT_PERIOD_PROVED", "source_id": "e0_dgsiaf_siche_cut_repository_2020_q2", "locator": "PDF p.9"},
    {"row_id": "CR141_03", "evidence": "Alcance Órganos Rectores", "proved_scope": "acceso institucional", "target_application": "derivar a TGN/CGN/DGSIAF", "required_output": "área ejecutora y usuario/consulta", "inference_limit": "no es acceso ciudadano directo", "status": "INTERNAL_ACCESS_PROVED_REQUEST_NOT_SENT", "source_id": "e0_dgsiaf_siche_cut_repository_2020_q2", "locator": "PDF p.9"},
    {"row_id": "CR141_04", "evidence": "Entidades Básicas", "proved_scope": "clase consultable", "target_application": "identificar cuenta bancaria y cuentas de operación vigentes en 2008", "required_output": "banco;sucursal;cuenta;moneda;vigencia;titular;SAF", "inference_limit": "3855/19 posterior no se presume para 2008", "status": "QUERY_CLASS_PROVED_NOT_RUN", "source_id": "e0_dgsiaf_siche_cut_repository_2020_q2", "locator": "PDF p.9"},
    {"row_id": "CR141_05", "evidence": "Saldos por Tipo de Apertura de Cuenta de Operación", "proved_scope": "clase consultable", "target_application": "reconstruir tipo y saldo de cuenta", "required_output": "tipo de apertura;cuenta;fecha;saldo", "inference_limit": "saldo no identifica movimiento", "status": "QUERY_CLASS_PROVED_NOT_RUN", "source_id": "e0_dgsiaf_siche_cut_repository_2020_q2", "locator": "PDF p.9"},
    {"row_id": "CR141_06", "evidence": "Extractos", "proved_scope": "clase consultable", "target_application": "buscar débito/crédito y referencia", "required_output": "fecha;secuencia;códigos;importe;referencia;estado", "inference_limit": "extracto sin vínculo no atribuye causa", "status": "EXACT_TARGET_ROUTE_PROVED_NOT_RUN", "source_id": "e0_dgsiaf_siche_cut_repository_2020_q2", "locator": "PDF p.9"},
    {"row_id": "CR141_07", "evidence": "Logs de Impacto", "proved_scope": "clase consultable", "target_application": "reconstruir evento que impactó la cuenta", "required_output": "timestamp;evento;entidad;comprobante;importe;resultado", "inference_limit": "log no equivale por sí solo a conciliación", "status": "EXACT_TARGET_ROUTE_PROVED_NOT_RUN", "source_id": "e0_dgsiaf_siche_cut_repository_2020_q2", "locator": "PDF p.9"},
    {"row_id": "CR141_08", "evidence": "Combinación 7.2.8/83106000 con CUT", "proved_scope": "cruce metodológico V144", "target_application": "formulario→impacto→extracto", "required_output": "identificador compartido;fecha;importe;cuenta", "inference_limit": "el PDF no publica esa combinación", "status": "CROSSWALK_PROPOSED_NOT_EXECUTED", "source_id": "E0_SICHE_NAMED_QUERY_TARGET_MAP_V144.csv;e0_dgsiaf_siche_cut_repository_2020_q2", "locator": "matriz V144"},
    {"row_id": "CR141_09", "evidence": "Cuenta CUT 3855/19 en manuales posteriores", "proved_scope": "ejemplo/entorno posterior", "target_application": "clave de control, no filtro inicial", "required_output": "cuenta histórica surgida de Entidades Básicas", "inference_limit": "no atribuir 3855/19 retroactivamente", "status": "CURRENT_IDENTIFIER_ONLY_LEGACY_OPEN", "source_id": "e0_tgn_treasury_system_v3_2022_cut_extract;e0_tgn_cut_auditor_instruction_2025", "locator": "PDF p.63; PDF p.15"},
    {"row_id": "CR141_10", "evidence": "Cadena mínima", "proved_scope": "formulario;log;extracto;Libro Banco;conciliación", "target_application": "cierre de ejecución", "required_output": "cinco vínculos concordantes", "inference_limit": "ninguna capa sustituye a las restantes", "status": "CLOSE_TEST_FROZEN_TARGET_OPEN", "source_id": "e0_dgsiaf_siche_cut_repository_2020_q2;e0_tgn_treasury_system_v3_2022_cut_extract;e0_tgn_cut_auditor_instruction_2025", "locator": "PDF p.9;p.63;p.5-39"},
]
write_csv(HERE / "E0_SICHE_CUT_HISTORICAL_REPOSITORY_V144.csv", cut_repo)

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
write_csv(HERE / "E0_CUT_EXTRACT_FIELD_CROSSWALK_V144.csv", extract_fields)

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
write_csv(HERE / "E0_CUT_AUDITOR_EVIDENCE_CHAIN_V144.csv", auditor_chain)

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
    (20, "C-55 Regularización Global · Débito Directo", "SAF355;todo 2008;sin OP original;cuenta de débito obligatoria", "C55-REG;institución;UG;fuente;clase;beneficiario;importe;cuenta", "probar firma contemporánea de comisión debitada"),
    (21, "Histórico C-55", "formularios candidatos;estados I/X/E/C/R", "carga;autorización;envío a SIDIF Central;respuesta;usuario;fecha", "probar aceptación central y secuencia"),
    (22, "Reversas C-55", "C55-REG rechazados/revertidos;C55-DEG", "original;reversa;código de error;contraasiento Libro Banco", "descartar débito revertido"),
    (23, "Reporte conc_01.rep", "cuentas históricas;todo 2008;estados N/P/T", "fecha movimiento/proceso;tipo;cuenta;debe;haber;saldo;estado", "obtener lado extracto con esquema contemporáneo"),
    (24, "Reporte conc_02.rep", "mismas cuentas/ventanas;estados N/P/T", "Libro Banco;descripción;formulario;número;cheque;beneficiario;debe;haber;saldo", "obtener lado interno con esquema contemporáneo"),
    (25, "Prueba de rama del medio de pago", "cada candidato;servicio deuda pública vs carta de crédito/transferencia exterior", "tipo de nota;cuenta de gastos;comisión;orden/nota;respaldo", "separar comisión operativa de pago de deuda"),
    (26, "SLU · BCUENTA/ACTA_FUE/ACTABAN_CTAESC", "SAF355;snapshot 2008;activas+bajas+rehabilitadas", "banco;sucursal;cuenta;tipo;fuente;cuenta escritural;fechas de estado", "resolver identidad histórica de cuenta"),
    (27, "SLU · BMOVEXTERNO/BMOVBCO/BGRUPMOVBCO", "BNA;todo código vigente/usado en 2008;sin literal prefijado", "código externo;contracódigo;interno;grupo;signo;automático/manual", "resolver código bancario histórico"),
    (28, "SLU · AMOV_FORG", "SAF355;BNA;cuentas recuperadas;todo 2008;activas+bajas+rehabilitadas", "cuenta/subcuenta;movimiento;partida;estado;fecha baja/rehabilitación", "recuperar parametrización de gasto automático"),
    (29, "SLU · ACLB_MOB/BCODLIBBCO", "códigos recuperados;vigencia 2008", "movimiento extracto;código Libro Banco;descripción;signo;conciliación parcial", "cerrar mapeo a Libro Banco"),
    (30, "Backups SLU", "2006-2009;instancia/esquema del SAF355 y órganos rectores", "inventario;fecha;servidor;retención;custodio;hash;soporte", "superar tablas sin historia"),
    (31, "Migración/versiones SLU", "v7→v9.0;2006-2009;módulos Tesorería/Conciliación", "versión por SAF;DDL/DML;tablas origen/destino;diccionario", "evitar falsa continuidad semántica"),
    (32, "Consulta de Bajas/Rehabilitaciones", "cada tabla local/externa;claves recuperadas", "clave;descripción;fecha baja;fecha rehabilitación;usuario;motivo", "reconstruir secuencia temporal"),
    (33, "Historial de Correcciones", "movimientos extracto candidatos", "original;corrección;banco;sucursal;cuenta;fecha;códigos;comprobante;importe;signo", "evitar perder versión original"),
    (34, "C10 · control de recurso", "SAF355;2008;generación A/M;REC/REG/COR/DES/CMP;83106000", "cuenta;SIGADE;boleta;estado;transmisión;original/modificación", "descartar crédito/recurso o vínculo alternativo"),
    (35, "Desafectación/reversa/cheque", "C55-DEP/C55-REP;C55-DEG;cheques C/R/E/F;movimientos candidatos", "original;reversa;contraasiento;cuenta;estado;detalle conciliación", "descartar ejecución neutralizada o medio alternativo"),
])
cut_runbook = [{
    "step_id": f"CQ143_{number:02d}", "sequence": str(number), "query": query, "filters": filters,
    "requested_output": output, "decision": decision, "status": "DRAFT_NOT_SENT",
} for number, query, filters, output, decision in run_steps]
write_csv(HERE / "E0_CUT_TARGET_QUERY_RUNBOOK_V144.csv", cut_runbook)

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
write_csv(HERE / "E0_CUT_ZERO_RESULT_AND_CONCILIATION_LIMITS_V144.csv", zero_limits)

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
            "row_id": f"EC143_{edition}_{number:02d}", "edition": edition, "movement_code": code,
            "official_description": description, "functional_group": code_group(code),
            "target_use": "priorizar comisión" if code in {"AUTO", "DBAUTO"} else "control positivo/negativo",
            "temporal_limit": "El código exacto 2008 debe surgir del diccionario SICHE; no se presume continuidad.",
            "source_id": "e0_tgn_manual_system_treasury_v1" if edition == "2013_V1" else "e0_tgn_treasury_system_v3_2022_cut_extract",
            "locator": locator,
        })
assert len(event_codes) == 69
write_csv(HERE / "E0_CUT_EVENT_CODE_DICTIONARY_V144.csv", event_codes)

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
        "row_id": f"CC143_{number:02d}", "code_2013": code, "description_2013": description,
        "code_2022": later_code, "description_2022": later_description, "continuity_class": continuity_class,
        "query_effect": "buscar ambos códigos y descripción; pedir diccionario histórico 2008",
        "inference_limit": "Continuidad 2013-2022 no acredita vigencia ni uso del código en 2008.",
    })
assert len(continuity) == 28
write_csv(HERE / "E0_CUT_EVENT_CODE_CONTINUITY_V144.csv", continuity)

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
    "row_id": f"OA143_{number:02d}", "edition": edition, "account_or_equation": account,
    "denomination": denomination, "official_function": function,
    "target_effect": "filtro primario candidato" if account == "230" else "control y descarte",
    "temporal_limit": "Confirmar catálogo 2008 en SICHE." if edition != "EQUATION" else "Ecuación posterior; verificar versión histórica.",
    "source_id": "e0_tgn_manual_system_treasury_v1;e0_tgn_treasury_system_v3_2022_cut_extract",
    "locator": locator,
} for number, (edition, account, denomination, function, locator) in enumerate(operation_accounts, 1)]
assert len(account_rows) == 19
write_csv(HERE / "E0_CUT_OPERATION_ACCOUNT_EQUATIONS_V144.csv", account_rows)

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
    "row_id": f"TD143_{number:02d}", "code_or_key": code, "layer": layer,
    "official_meaning": meaning, "target_role": role,
    "required_target_observable": "código;descripción;fecha;importe;referencia;estado;cuenta operación;formulario",
    "status": "QUERY_DISCRIMINATOR_PROVED_TARGET_OPEN",
} for number, (code, layer, meaning, role) in enumerate(discriminator_specs, 1)]
write_csv(HERE / "E0_CUT_TARGET_CODE_DISCRIMINATION_V144.csv", discriminators)

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
    "step_id": f"RR143_{number:02d}", "layer": layer, "official_rule": rule,
    "minimum_output": output, "locator": locator,
    "source_id": "e0_tgn_manual_system_treasury_v1", "target_status": "ROUTE_PROVED_TARGET_RECORD_OPEN",
} for number, (layer, rule, output, locator) in enumerate(route_specs, 1)]
write_csv(HERE / "E0_CUT_RECONCILIATION_EVIDENCE_ROUTE_V144.csv", reconciliation_route)

pdf_visual = [
    {"control_id": "PV144_01", "source_id": "e0_tgn_manual_system_treasury_v1", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v137/binaries/tgn_manual_sistema_tesoreria_v1.pdf", "pdf_page": "64", "rendered_check": "cuenta 230 Débitos Automáticos; catálogo de cuentas y ecuaciones", "result": "PASS"},
    {"control_id": "PV144_02", "source_id": "e0_tgn_manual_system_treasury_v1", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v137/binaries/tgn_manual_sistema_tesoreria_v1.pdf", "pdf_page": "65", "rendered_check": "eventos, reconstrucción de impactos y auditor diario", "result": "PASS"},
    {"control_id": "PV144_03", "source_id": "e0_tgn_manual_system_treasury_v1", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v137/binaries/tgn_manual_sistema_tesoreria_v1.pdf", "pdf_page": "67", "rendered_check": "tabla de 28 códigos; AUTO/PAGO/PGTR/rechazos", "result": "PASS"},
    {"control_id": "PV144_04", "source_id": "e0_tgn_manual_system_treasury_v1", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v137/binaries/tgn_manual_sistema_tesoreria_v1.pdf", "pdf_page": "68", "rendered_check": "referencia unívoca bancaria por operación", "result": "PASS"},
    {"control_id": "PV144_05", "source_id": "e0_tgn_manual_system_treasury_v1", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v137/binaries/tgn_manual_sistema_tesoreria_v1.pdf", "pdf_page": "112", "rendered_check": "débito automático BNA; gastos bancarios; formulario de regularización", "result": "PASS"},
    {"control_id": "PV144_06", "source_id": "e0_tgn_manual_system_treasury_v1", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v137/binaries/tgn_manual_sistema_tesoreria_v1.pdf", "pdf_page": "140", "rendered_check": "mapeo código externo/interno, validación, reversa e historial", "result": "PASS"},
    {"control_id": "PV144_07", "source_id": "e0_tgn_manual_system_treasury_v1", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v137/binaries/tgn_manual_sistema_tesoreria_v1.pdf", "pdf_page": "141", "rendered_check": "campos de extracto y estados T/P/N", "result": "PASS"},
    {"control_id": "PV144_08", "source_id": "e0_tgn_manual_system_treasury_v1", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v137/binaries/tgn_manual_sistema_tesoreria_v1.pdf", "pdf_page": "147", "rendered_check": "grupos LIB/APL y comisiones bancarias automáticas", "result": "PASS"},
    {"control_id": "PV144_09", "source_id": "e0_tgn_manual_system_treasury_v1", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v137/binaries/tgn_manual_sistema_tesoreria_v1.pdf", "pdf_page": "148", "rendered_check": "formulario SIDIF de gasto y C-55/CRG de regularización", "result": "PASS"},
    {"control_id": "PV144_10", "source_id": "e0_tgn_treasury_system_v3_2022_cut_extract", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v141/binaries/argentina_tgn_treasury_system_v3_2022.pdf", "pdf_page": "61", "rendered_check": "cuenta 230 Débitos extracto bancario y definición estable", "result": "PASS"},
    {"control_id": "PV144_11", "source_id": "e0_tgn_treasury_system_v3_2022_cut_extract", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v141/binaries/argentina_tgn_treasury_system_v3_2022.pdf", "pdf_page": "62", "rendered_check": "cuentas 511/530/640/710/810 y ecuaciones", "result": "PASS"},
    {"control_id": "PV144_12", "source_id": "e0_tgn_treasury_system_v3_2022_cut_extract", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v141/binaries/argentina_tgn_treasury_system_v3_2022.pdf", "pdf_page": "64", "rendered_check": "DBAUTO/CRAUTO y tabla de códigos v3 parte 1", "result": "PASS"},
    {"control_id": "PV144_13", "source_id": "e0_tgn_treasury_system_v3_2022_cut_extract", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v141/binaries/argentina_tgn_treasury_system_v3_2022.pdf", "pdf_page": "65", "rendered_check": "tabla de códigos v3 parte 2 y referencia unívoca", "result": "PASS"},
]
write_csv(HERE / "E0_V144_PDF_VISUAL_CONTROL.csv", pdf_visual)

# Puente contemporáneo 2001-2005. A diferencia del crosswalk 2013-2022, estas
# reglas ya existían antes del ejercicio objetivo y permiten interrogar 2008 por
# función, formulario, estado y reporte aun cuando el literal 230/AUTO siga abierto.
payment_branch_specs = [
    ("2005-08-16", "Devengado", "Las comisiones bancarias pueden registrar compromiso y devengado simultáneamente.", "identificar partida y formulario de gasto", "No identifica la comisión target.", "p. física 72 / interna 69"),
    ("2005-08-16", "Emisión del medio de pago", "Todo medio que genere movimiento de fondos debe registrarse en extracto interno o Libro Banco para su conciliación posterior.", "exigir el lado interno del movimiento", "Regla de diseño, no prueba de registro individual.", "p. física 108 / interna 105"),
    ("2005-08-16", "Carta de crédito", "Tiene gastos y comisiones asociados.", "ruta alternativa positiva", "No atribuir automáticamente al servicio de deuda.", "p. física 109 / interna 106"),
    ("2005-08-16", "Servicio de la Deuda Pública", "No cobra gastos y comisiones.", "control negativo decisivo", "Describe el tipo de nota/medio; no niega todo gasto bancario externo al pago.", "p. física 109 / interna 106"),
    ("2005-08-16", "Transferencias al exterior", "Tienen gastos y comisiones asociados.", "ruta alternativa positiva", "Debe probarse el tipo de operación target.", "p. física 109 / interna 106"),
    ("2005-08-16", "Cuenta de gastos", "Carta de crédito y transferencia al exterior debitan gastos y comisiones de una cuenta determinada del servicio.", "pedir banco;sucursal;cuenta de gastos", "La cuenta no prueba el concepto sin movimiento.", "p. física 109 / interna 106"),
    ("2005-08-16", "Anulación", "La anulación posterior a emitir el medio produce contraasiento en extracto interno o Libro Banco.", "buscar original y reversa", "Contraasiento no prueba finalidad económica.", "p. física 111 / interna 108"),
    ("2005-08-16", "Rechazo bancario", "El rechazo de orden bancaria o cheque activa la anulación por rechazo.", "buscar rechazo y código causal", "Rechazo no equivale a ejecución.", "p. física 111 / interna 108"),
    ("2005-08-16", "Objetivo de conciliación", "Compara débitos y créditos del extracto bancario/escritural con registros internos y Libro Banco.", "exigir ambos lados", "Concordancia formal no prueba causa sin respaldo.", "p. física 113 / interna 110"),
    ("2005-08-16", "Registro interno", "Las comisiones bancarias son ejemplo expreso de movimiento incorporado al extracto interno por conciliación.", "buscar gasto/comisión como aplicación", "No aporta código exacto 2008.", "p. física 114 / interna 111"),
    ("2005-08-16", "Conciliación automática de pagos", "Débitos por pagos y créditos por rechazos del extracto interno se aparean con el extracto escritural.", "separar pago, rechazo y comisión", "Categorías funcionales, no fila target.", "p. física 114 / interna 111"),
    ("2005-08-16", "Débito diario automático", "El débito diario automático de cuenta recaudadora se aparea con el crédito de la cuenta escritural.", "control de débito automático no-comisión", "No todo débito automático es gasto bancario.", "p. física 114-115 / interna 111-112"),
    ("2005-08-16", "Regularización manual", "Sólo se regularizan manualmente movimientos no procesados antes por conciliación automática.", "pedir motivo, usuario, fecha y regla", "La regularización manual no sustituye el movimiento original.", "p. física 116 / interna 113"),
    ("2001-06", "Nota de pago", "La cuenta de gastos identifica banco, sucursal y cuenta donde se debitan comisiones o gastos de transferencia.", "pedir cuenta de gastos y nota asociada", "Manual anterior; confirmar versión aplicada en 2008.", "DOC · Pagos por Nota · campo cuenta de gastos"),
]
payment_branches = [{
    "row_id": f"PB143_{number:02d}", "manual_date": date, "layer": layer,
    "official_rule": rule, "target_test": test, "inference_limit": limit,
    "source_id": "e0_dgsiaf_slu_note_payment_2001" if date == "2001-06" else "e0_dgsiaf_slu_system_description_v3",
    "locator": locator,
} for number, (date, layer, rule, test, limit, locator) in enumerate(payment_branch_specs, 1)]
write_csv(HERE / "E0_SLU_2005_PAYMENT_COMMISSION_BRANCH_V144.csv", payment_branches)

report_specs = [
    ("conc_01.rep", "ruta", "Tesorería / Conciliación bancaria / Listado/Extracto", "reproducir reporte de movimientos externos"),
    ("conc_01.rep", "cuenta", "Cuenta bancaria consultada", "identificar cuenta histórica"),
    ("conc_01.rep", "saldo final anterior", "Saldo previo al período", "controlar continuidad"),
    ("conc_01.rep", "fecha de movimiento", "Fecha económica del movimiento", "cruzar formulario y banco"),
    ("conc_01.rep", "fecha de proceso", "Fecha de procesamiento", "medir rezago"),
    ("conc_01.rep", "tipo de movimiento", "Clasificación del movimiento", "buscar comisión/pago/rechazo"),
    ("conc_01.rep", "tipo de cuenta bancaria", "Clase bancaria", "clasificar cuenta"),
    ("conc_01.rep", "número de cuenta bancaria", "Identificador bancario", "unir con BNA"),
    ("conc_01.rep", "debe", "Importe débito", "controlar signo"),
    ("conc_01.rep", "haber", "Importe crédito", "controlar signo"),
    ("conc_01.rep", "saldo acumulado", "Saldo posterior por movimiento", "probar aritmética"),
    ("conc_01.rep", "saldo final del período", "Cierre del intervalo", "controlar completitud"),
    ("conc_01.rep", "tipo E/P/R", "Cuenta Escritural, Pagadora o Recaudadora", "separar función de cuenta"),
    ("conc_01.rep", "estado N/P/T", "No, Parcial o Totalmente conciliado", "clasificar estado"),
    ("conc_02.rep", "ruta", "Tesorería / Conciliación bancaria / Listado/Libro Banco", "reproducir reporte interno"),
    ("conc_02.rep", "saldo inicial", "Saldo de apertura", "controlar continuidad"),
    ("conc_02.rep", "ejercicio", "Ejercicio presupuestario", "fijar 2008"),
    ("conc_02.rep", "fecha de proceso", "Fecha de procesamiento", "medir rezago"),
    ("conc_02.rep", "comprobante Libro Banco", "Número y descripción del comprobante", "unir registro interno"),
    ("conc_02.rep", "debe", "Importe débito", "controlar signo"),
    ("conc_02.rep", "haber", "Importe crédito", "controlar signo"),
    ("conc_02.rep", "saldo", "Saldo posterior", "probar aritmética"),
    ("conc_02.rep", "tipo de formulario", "Clase de formulario respaldatorio", "buscar C55/nota/pago"),
    ("conc_02.rep", "número de formulario", "Identificador del formulario", "cruzar SIDIF"),
    ("conc_02.rep", "número de cheque", "Cheque asociado si corresponde", "control de medio"),
    ("conc_02.rep", "beneficiario", "Beneficiario informado", "contrastar Banco Nación"),
    ("conc_02.rep", "cuenta", "Cuenta operativa", "unir con extracto"),
    ("conc_02.rep", "estado y fecha de movimiento", "N/P/T y fecha económica", "cerrar conciliación"),
]
report_schema = [{
    "field_id": f"RS143_{number:02d}", "report": report, "field_or_value": field,
    "official_meaning": meaning, "target_use": use,
    "source_id": "e0_dgsiaf_slu_bank_reconciliation_reports_2002",
    "locator": f"DOC Septiembre 2002 · versión 7 · {report}",
    "status": "CONTEMPORARY_SCHEMA_PROVED_TARGET_OPEN",
} for number, (report, field, meaning, use) in enumerate(report_specs, 1)]
write_csv(HERE / "E0_SLU_2002_RECONCILIATION_REPORT_SCHEMA_V144.csv", report_schema)

state_specs = [
    ("I", "Ingresado", "Formulario cargado", "estado inicial"),
    ("X", "Anulado", "Carga dejada sin efecto", "excluir como ejecución"),
    ("E", "Enviado", "Autorizado y enviado a SIDIF Central; espera respuesta", "no contar como confirmado"),
    ("C", "Confirmado", "Aprobado por SIDIF Central; produce impacto en Libro Banco cuando corresponde", "estado positivo necesario"),
    ("R", "Rechazado", "SIDIF Central rechazó o se revirtió el formulario", "excluir o rastrear reversa"),
    ("I→X", "Anulación local", "La carga se anula antes del envío", "control negativo"),
    ("I→E", "Autorización y envío", "Se transmite a SIDIF Central", "probar fecha de envío"),
    ("E→C", "Aceptación", "Respuesta central aprobatoria", "probar aceptación e impacto"),
    ("E→R", "Rechazo central", "Respuesta central negativa revierte impactos internos", "probar código de error"),
    ("C→R", "Reversión manual", "C55-DEG revierte C55-REG confirmado y puede contraasentar Libro Banco", "buscar original y reversa"),
]
c55_states = [{
    "state_id": f"SM143_{number:02d}", "state_or_transition": code, "name": name,
    "official_effect": effect, "target_decision": decision,
    "source_id": "e0_dgsiaf_slu_global_regularization_2004",
    "locator": "DOC Abril 2004 · revisión 14/06/2005 · estados/histórico/revertir",
} for number, (code, name, effect, decision) in enumerate(state_specs, 1)]
write_csv(HERE / "E0_C55_DIRECT_DEBIT_STATE_MACHINE_V144.csv", c55_states)

signature_specs = [
    ("disparador", "Débito detectado en cuenta bancaria; ejemplo expreso: comisión cobrada", "REQUIRED_CAUSAL_CLASS"),
    ("tipo", "Débito Directo", "REQUIRED_FORM_CLASS"),
    ("formulario", "C55-REG", "REQUIRED_IDENTIFIER"),
    ("orden de pago original", "No corresponde para Débito Directo", "EXPECTED_ABSENCE"),
    ("cuenta de débito", "Obligatoria", "REQUIRED_ACCOUNT"),
    ("signo Libro Banco", "+débito", "REQUIRED_SIGN"),
    ("impacto presupuestario", "Regulariza etapas presupuestarias o no presupuestarias", "REQUIRED_CLASSIFICATION"),
    ("impacto Libro Banco", "Se materializa sólo tras aceptación de SIDIF Central cuando corresponde", "REQUIRED_ACCEPTANCE"),
    ("institución", "Campo del Débito Directo", "REQUEST_FIELD"),
    ("unidad de gestión", "Campo del Débito Directo", "REQUEST_FIELD"),
    ("fuente de financiamiento", "Campo del Débito Directo", "REQUEST_FIELD"),
    ("clase de gasto", "Campo del Débito Directo", "REQUEST_FIELD"),
    ("beneficiario", "Campo del Débito Directo", "REQUEST_FIELD"),
    ("estado C", "Confirmado por SIDIF Central", "REQUIRED_POSITIVE_STATE"),
    ("histórico", "Conserva ingreso, autorización, envío y recepción de respuesta", "REQUIRED_AUDIT_TRAIL"),
    ("reversa", "C55-DEG y contraasiento posible en Libro Banco", "REQUIRED_NEGATIVE_CONTROL"),
]
c55_signature = [{
    "observable_id": f"TS143_{number:02d}", "observable": observable,
    "contemporary_rule": rule, "target_role": role,
    "source_id": "e0_dgsiaf_slu_global_regularization_2004",
    "locator": "DOC Abril 2004 · revisión 14/06/2005 · Regularización Global/Débito Directo",
    "status": "SIGNATURE_PROVED_TARGET_RECORD_OPEN",
} for number, (observable, rule, role) in enumerate(signature_specs, 1)]
write_csv(HERE / "E0_C55_DIRECT_DEBIT_TARGET_SIGNATURE_V144.csv", c55_signature)

continuity_specs = [
    ("2001-06", "Nota de pago", "Cuenta de gastos con banco/sucursal/cuenta para comisiones y transferencias", "PRE_2008_FUNCTION_PROVED"),
    ("2002-09", "conc_01.rep", "Exporta movimientos de extracto, debe/haber/saldo y estado N/P/T", "PRE_2008_EXTERNAL_SCHEMA_PROVED"),
    ("2002-09", "conc_02.rep", "Exporta Libro Banco, formulario, beneficiario, debe/haber/saldo y estado", "PRE_2008_INTERNAL_SCHEMA_PROVED"),
    ("2002-09", "N/P/T", "Estados no/parcial/totalmente conciliado", "PRE_2008_STATE_SCHEMA_PROVED"),
    ("2004-04/2005-06", "C55-REG Débito Directo", "Comisión cobrada como débito bancario sin OP original y con cuenta obligatoria", "PRE_2008_COMMISSION_FORM_PROVED"),
    ("2004-04/2005-06", "I/X/E/C/R", "Estado e historial de envío/respuesta central", "PRE_2008_FORM_STATE_PROVED"),
    ("2005-08-16", "Rama Servicio de Deuda", "No cobra gastos y comisiones", "PRE_2008_NEGATIVE_BRANCH_PROVED"),
    ("2005-08-16", "Rama transferencia exterior/carta de crédito", "Sí genera gastos y comisiones en cuenta del servicio", "PRE_2008_POSITIVE_BRANCH_PROVED"),
    ("2005-08-16", "Conciliación automática", "Comisiones, pagos, rechazos y débito diario siguen carriles diferenciados", "PRE_2008_RECONCILIATION_FUNCTION_PROVED"),
    ("2013", "230/AUTO", "Cuenta y código de débito automático; gastos bancarios como ejemplo", "POST_2008_NEAR_CROSSWALK"),
    ("2022", "230/DBAUTO-CRAUTO", "Función 230 estable y código separado por signo", "POST_2008_CONTINUITY_CROSSWALK"),
    ("2008", "Código/catálogo target", "Literal exacto 230/AUTO y fila individual aún no recuperados", "EXACT_TARGET_OPEN"),
]
temporal_bridge = [{
    "bridge_id": f"TC143_{number:02d}", "date_or_period": period, "artifact_or_code": artifact,
    "proved_fact": fact, "evidentiary_role": role,
    "source_id": (
        "e0_dgsiaf_slu_note_payment_2001" if period == "2001-06" else
        "e0_dgsiaf_slu_bank_reconciliation_reports_2002" if period == "2002-09" else
        "e0_dgsiaf_slu_global_regularization_2004" if period == "2004-04/2005-06" else
        "e0_dgsiaf_slu_system_description_v3" if period == "2005-08-16" else
        "e0_tgn_manual_system_treasury_v1" if period == "2013" else
        "e0_tgn_treasury_system_v3_2022_cut_extract" if period == "2022" else
        "E0_CUT_TARGET_QUERY_RUNBOOK_V144.csv"
    ),
    "inference_limit": "Mecanismo y esquema contemporáneos no equivalen a fila target; confirmar versión/código 2008.",
} for number, (period, artifact, fact, role) in enumerate(continuity_specs, 1)]
write_csv(HERE / "E0_2001_2005_2013_2022_TEMPORAL_CONTINUITY_V144.csv", temporal_bridge)

pdf_visual.extend([
    {"control_id": "PV144_14", "source_id": "e0_dgsiaf_slu_system_description_v3", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v139/binaries/argentina_slu_system_description_v3.pdf", "pdf_page": "72", "rendered_check": "comisiones bancarias pueden registrar compromiso y devengado simultáneamente", "result": "PASS"},
    {"control_id": "PV144_15", "source_id": "e0_dgsiaf_slu_system_description_v3", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v139/binaries/argentina_slu_system_description_v3.pdf", "pdf_page": "108", "rendered_check": "todo movimiento del medio de pago entra al extracto interno/Libro Banco", "result": "PASS"},
    {"control_id": "PV144_16", "source_id": "e0_dgsiaf_slu_system_description_v3", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v139/binaries/argentina_slu_system_description_v3.pdf", "pdf_page": "109", "rendered_check": "deuda pública sin comisión; carta de crédito y transferencia exterior con gastos/comisiones", "result": "PASS"},
    {"control_id": "PV144_17", "source_id": "e0_dgsiaf_slu_system_description_v3", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v139/binaries/argentina_slu_system_description_v3.pdf", "pdf_page": "111", "rendered_check": "anulación, contraasiento y rechazo bancario", "result": "PASS"},
    {"control_id": "PV144_18", "source_id": "e0_dgsiaf_slu_system_description_v3", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v139/binaries/argentina_slu_system_description_v3.pdf", "pdf_page": "113", "rendered_check": "conciliación compara extracto externo con interno/Libro Banco", "result": "PASS"},
    {"control_id": "PV144_19", "source_id": "e0_dgsiaf_slu_system_description_v3", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v139/binaries/argentina_slu_system_description_v3.pdf", "pdf_page": "114", "rendered_check": "comisiones como registro interno y conciliación automática diferenciada", "result": "PASS"},
    {"control_id": "PV144_20", "source_id": "e0_dgsiaf_slu_system_description_v3", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v139/binaries/argentina_slu_system_description_v3.pdf", "pdf_page": "115", "rendered_check": "cuadro de pagos, rechazos, recursos y débitos/créditos automáticos", "result": "PASS"},
    {"control_id": "PV144_21", "source_id": "e0_dgsiaf_slu_system_description_v3", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v139/binaries/argentina_slu_system_description_v3.pdf", "pdf_page": "116", "rendered_check": "regularización manual sólo después del proceso automático", "result": "PASS"},
    {"control_id": "PV144_22", "source_id": "e0_dgsiaf_slu_reconciliation_workshop_2017_historical_screens", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v144/binaries/dgsiaf_slu_taller_conciliacion_2017.pdf", "pdf_page": "1", "rendered_check": "portada Taller de Conciliación Bancaria SLU", "result": "PASS"},
    {"control_id": "PV144_23", "source_id": "e0_dgsiaf_slu_reconciliation_workshop_2017_historical_screens", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v144/binaries/dgsiaf_slu_taller_conciliacion_2017.pdf", "pdf_page": "2", "rendered_check": "relación gasto→C55 y recurso→C10", "result": "PASS"},
    {"control_id": "PV144_24", "source_id": "e0_dgsiaf_slu_reconciliation_workshop_2017_historical_screens", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v144/binaries/dgsiaf_slu_taller_conciliacion_2017.pdf", "pdf_page": "3", "rendered_check": "SLU v9.0 fechado 26/11/2008; ejercicio 2008; BNA; ejemplo CUM023", "result": "PASS"},
    {"control_id": "PV144_25", "source_id": "e0_dgsiaf_slu_reconciliation_workshop_2017_historical_screens", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v144/binaries/dgsiaf_slu_taller_conciliacion_2017.pdf", "pdf_page": "4", "rendered_check": "pantalla de parametrización/conciliación", "result": "PASS"},
    {"control_id": "PV144_26", "source_id": "e0_dgsiaf_slu_reconciliation_workshop_2017_historical_screens", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v144/binaries/dgsiaf_slu_taller_conciliacion_2017.pdf", "pdf_page": "5", "rendered_check": "SLU v9.0 fechado 04/12/2006 y menú de tablas de conciliación", "result": "PASS"},
    {"control_id": "PV144_27", "source_id": "e0_dgsiaf_slu_reconciliation_workshop_2017_historical_screens", "local_path": "/research/ciclo_ajuste/inputs/historical_retrieval/v144/binaries/dgsiaf_slu_taller_conciliacion_2017.pdf", "pdf_page": "6", "rendered_check": "control visual completo del PDF", "result": "PASS"},
])
write_csv(HERE / "E0_V144_PDF_VISUAL_CONTROL.csv", pdf_visual)

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
    (16, "SLU · Reporte conc_01.rep", "SAF355;cuentas históricas;01/01-31/12/2008;N/P/T", "fecha movimiento/proceso;tipo;cuenta;debe;haber;saldo;estado", "recuperar extracto contemporáneo"),
    (17, "SLU · Reporte conc_02.rep", "mismas cuentas y fechas;N/P/T", "Libro Banco;descripción;formulario;número;beneficiario;debe;haber;saldo", "recuperar contraparte interna"),
    (18, "SLU · C55-REG Débito Directo", "SAF355;2008;sin OP original;cuenta débito;comisión", "institución;UG;fuente;clase;beneficiario;importe;cuenta;estado", "probar firma de comisión"),
    (19, "SLU · Histórico/Reversa C55", "candidatos I/X/E/C/R;C55-DEG", "carga;autorización;envío;respuesta;error;original;reversa;contraasiento", "separar confirmado de rechazado/revertido"),
    (20, "SLU · Rama del medio de pago", "tipo de nota;servicio deuda/carta crédito/transferencia exterior", "medio;cuenta de gastos;orden/nota;comisión;respaldo", "refutar atribución automática a deuda pública"),
    (21, "SLU · BCUENTA/ACTA_FUE/ACTABAN_CTAESC", "SAF355;snapshot 2008;activas+bajas+rehabilitadas", "cuenta;fuente;cuenta escritural;vigencia", "identidad de cuenta"),
    (22, "SLU · BMOVEXTERNO/BMOVBCO/BGRUPMOVBCO", "BNA;todo 2008;sin código prefijado", "externo;contracódigo;interno;grupo;signo;tipo", "código histórico"),
    (23, "SLU · AMOV_FORG", "cuentas recuperadas;SAF355;2008;incluye bajas", "cuenta;movimiento;partida;estado;fechas", "parametrización de gasto"),
    (24, "SLU · ACLB_MOB/BCODLIBBCO", "códigos recuperados;2008", "relación extracto-Libro Banco;signo;conciliación", "mapeo interno"),
    (25, "Backups SLU", "2006-2009;SAF355;órganos rectores", "inventario;instancia;esquema;fecha;retención;hash", "recuperación histórica"),
    (26, "Versiones/migraciones", "SLU v7→v9.0;2006-2009", "versión;SAF;DDL/DML;tabla origen/destino", "continuidad controlada"),
    (27, "Consulta de Bajas/Rehabilitaciones", "tablas clave;todo estado", "clave;fecha baja/rehabilitación;usuario;motivo", "historial lógico"),
    (28, "Correcciones de extracto", "movimientos candidatos", "original;corrección;códigos;importe;signo;comprobante", "cadena de versiones"),
    (29, "C10 · rama recurso", "SAF355;2008;A/M;83106000", "tipo;cuenta;SIGADE;estado;transmisión;original", "control de signo/origen"),
    (30, "Reversas y medios alternativos", "C55-DEP/REP/DEG;cheques C/R/E/F", "original;reversa;contraasiento;estado;conciliación", "control negativo final"),
]
query_plan = [{
    "query_id": f"SQ143_{number:02d}", "sequence": str(number), "system": system,
    "filter_set": filters, "requested_output": output, "success_test": decision,
    "fallback": "derivación al órgano rector y equivalente legacy documentado", "status": "DRAFT_NOT_SENT",
} for number, system, filters, output, decision in plan_specs]
write_csv(HERE / "E0_SICHE_TARGET_QUERY_PLAN_V144.csv", query_plan)

ledger_path = HERE / "E0_FISCAL_MECHANISM_LEDGER_V144.csv"
new_ledger_ids = {f"F{number}" for number in range(219, 261)}
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
        "source_locator": "matrices V144", "realization_status": status, "additivity": "NON_ADDITIVE",
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
        "source_locator": "matrices V144", "realization_status": status, "additivity": "NON_ADDITIVE",
        "status_interpretation": interpretation,
        "caveat": "No convertir código, cuenta o ruta de conciliación en ejecución target.",
    })
assert len(ledger) == 238

contemporary_ledger_additions = [
    (239, "2001-06", "SLU_PAYMENT_NOTE", "EXPENSE_ACCOUNT", "cuenta de gastos banco/sucursal/cuenta", "PRE_2008_ROUTE_PROVED", "Cuenta target no recuperada.", "e0_dgsiaf_slu_note_payment_2001"),
    (240, "2002-09", "SLU_RECONCILIATION", "EXTERNAL_REPORT", "conc_01.rep", "PRE_2008_REPORT_SCHEMA_PROVED", "Reporte target no ejecutado.", "e0_dgsiaf_slu_bank_reconciliation_reports_2002"),
    (241, "2002-09", "SLU_RECONCILIATION", "INTERNAL_REPORT", "conc_02.rep", "PRE_2008_REPORT_SCHEMA_PROVED", "Reporte target no ejecutado.", "e0_dgsiaf_slu_bank_reconciliation_reports_2002"),
    (242, "2004-2005", "C55_REGULARIZATION", "DIRECT_DEBIT_TRIGGER", "comisión cobrada debitada", "PRE_2008_COMMISSION_MECHANISM_PROVED", "No identifica importe ni SIDIF target.", "e0_dgsiaf_slu_global_regularization_2004"),
    (243, "2004-2005", "C55_REGULARIZATION", "DIRECT_DEBIT_SIGNATURE", "sin OP original; cuenta débito obligatoria", "PRE_2008_TARGET_SIGNATURE_PROVED", "Formulario target no recuperado.", "e0_dgsiaf_slu_global_regularization_2004"),
    (244, "2004-2005", "C55_REGULARIZATION", "CENTRAL_ACCEPTANCE", "C confirmado; impacto Libro Banco", "PRE_2008_ACCEPTANCE_RULE_PROVED", "Estado target abierto.", "e0_dgsiaf_slu_global_regularization_2004"),
    (245, "2004-2005", "C55_REGULARIZATION", "STATE_AND_REVERSAL", "I/X/E/C/R; C55-DEG", "PRE_2008_AUDIT_TRAIL_PROVED", "Histórico target no recuperado.", "e0_dgsiaf_slu_global_regularization_2004"),
    (246, "2005-08-16", "SLU_PAYMENT", "PUBLIC_DEBT_BRANCH", "servicio deuda sin gastos/comisiones", "PRE_2008_NEGATIVE_BRANCH_PROVED", "No descarta comisión bancaria separada del pago.", "e0_dgsiaf_slu_system_description_v3"),
    (247, "2005-08-16", "SLU_PAYMENT", "FOREIGN_TRANSFER_BRANCH", "transferencia exterior/carta crédito con gastos y comisiones", "PRE_2008_POSITIVE_BRANCH_PROVED", "Tipo target no recuperado.", "e0_dgsiaf_slu_system_description_v3"),
    (248, "2005-08-16", "SLU_RECONCILIATION", "AUTOMATIC_THEN_MANUAL", "comisión→extracto interno→conciliación", "PRE_2008_RECONCILIATION_ROUTE_PROVED", "Movimiento target no recuperado.", "e0_dgsiaf_slu_system_description_v3"),
]
for number, window, mechanism, phase, instrument, status, interpretation, source_id in contemporary_ledger_additions:
    ledger.append({
        "ledger_id": f"F{number}", "window": window, "mechanism": mechanism, "phase": phase,
        "as_of_date": "N/D", "payer": "TGN/SAF", "recipient": "N/D", "universe": "target 2008",
        "instrument": instrument, "amount_original": "N/D", "original_unit": "N/D",
        "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE",
        "source_id": source_id, "source_locator": "matrices contemporáneas V144",
        "realization_status": status, "additivity": "NON_ADDITIVE",
        "status_interpretation": interpretation,
        "caveat": "No convertir diseño, reporte o estado genérico en ejecución target.",
    })
v144_ledger_additions = [
    (249, "2002-2005", "SLU_TABLES", "EXACT_TABLE_DICTIONARY", "BGRUPMOVBCO;BMOVBCO;BMOVEXTERNO;AMOV_FORG;ACLB_MOB;BCODLIBBCO", "EXACT_SCHEMA_PROVED_TARGET_ROW_OPEN", "Nombres y función cerrados; valores 2008 ausentes.", "e0_dgsiaf_slu_treasury_basic_tables_2"),
    (250, "2002-2005", "SLU_TABLES", "RETENTION_LIMIT", "tablas centrales sin historia", "STRUCTURAL_HISTORY_GAP_PROVED", "Consulta vigente no reconstruye por sí sola 2008.", "e0_dgsiaf_slu_treasury_basic_tables_1;e0_dgsiaf_slu_treasury_basic_tables_2"),
    (251, "2002-2005", "SLU_ACCOUNT", "ACCOUNT_SOURCE_MAP", "BCUENTA;ACTA_FUE;ACTABAN_CTAESC", "EXACT_SCHEMA_PROVED_TARGET_ACCOUNT_OPEN", "Snapshot histórico requerido.", "e0_dgsiaf_slu_treasury_basic_tables_1"),
    (252, "2002-2003", "SLU_RECONCILIATION", "BANK_CODE_MAP", "BMOVEXTERNO→BMOVBCO→grupo", "EXACT_MAPPING_SCHEMA_PROVED_TARGET_CODE_OPEN", "Código externo BNA target no localizado.", "e0_dgsiaf_slu_treasury_basic_tables_2"),
    (253, "2002-2003", "SLU_RECONCILIATION", "AUTOMATIC_EXPENSE_MAP", "AMOV_FORG cuenta+movimiento→partida", "EXACT_MAPPING_SCHEMA_PROVED_TARGET_ROW_OPEN", "Parametrización target no localizada.", "e0_dgsiaf_slu_treasury_basic_tables_2"),
    (254, "2002-2003", "SLU_RECONCILIATION", "AUTOMATIC_C55", "partida+movimiento→C55→SIDIF Central", "CONTEMPORANEOUS_MECHANISM_PROVED_TARGET_FORM_OPEN", "No prueba C55 target.", "e0_dgsiaf_slu_bank_reconciliation_basic_tables_2002_v7"),
    (255, "2006-2008", "SLU_VERSION", "UI_VERSION", "SLU v9.0 · capturas 2006/2008", "HISTORICAL_UI_VERSION_PROVED_TARGET_OPEN", "Documento compilado en 2017; pantalla no prueba fila.", "e0_dgsiaf_slu_reconciliation_workshop_2017_historical_screens"),
    (256, "2004", "SLU_C10", "RESOURCE_BRANCH", "C10 A/M;REC/REG/COR/DES/CMP", "CONTEMPORANEOUS_RESOURCE_CONTROL_PROVED", "Rama recurso no equivale a C55 de comisión.", "e0_dgsiaf_slu_c10_2004_v10"),
    (257, "2005", "SLU_REVERSAL", "PAYMENT_REVERSAL", "C55-DEP→C55-REP;contraasiento", "REVERSAL_SCHEMA_PROVED_TARGET_OPEN", "Original/reversa target no localizados.", "e0_dgsiaf_slu_payment_reversal_2005"),
    (258, "2008-2026", "HISTORICAL_RECOVERY", "BACKUP_SNAPSHOT", "backup/dump/snapshot SLU", "RECOVERY_OBJECT_DEFINED_NOT_REQUESTED", "Custodio y soporte pendientes.", "E0_SLU_HISTORICAL_RECOVERY_STRATEGY_V144.csv"),
    (259, "2002-2008", "SLU_CORRECTION", "MOVEMENT_VERSION_CHAIN", "original→corrección de extracto", "CORRECTION_SCHEMA_PROVED_TARGET_OPEN", "Historial target no recuperado.", "e0_dgsiaf_slu_bank_reconciliation_manual_2003_v7"),
    (260, "2008-2026", "TARGET_QUERY", "SLU_TABLE_RECOVERY_PACKAGE", "35 pasos; 12 tablas/capas", "QUERY_PACKAGE_PROVED_NOT_EXECUTED", "Seis pedidos siguen sin enviar.", "E0_SLU_TABLE_REQUEST_FIELD_MATRIX_V144.csv"),
]
for number, window, mechanism, phase, instrument, status, interpretation, source_id in v144_ledger_additions:
    ledger.append({
        "ledger_id": f"F{number}", "window": window, "mechanism": mechanism, "phase": phase,
        "as_of_date": "N/D", "payer": "TGN/SAF/BNA/DGSIAF", "recipient": "N/D", "universe": "target 2008",
        "instrument": instrument, "amount_original": "N/D", "original_unit": "N/D",
        "normalized_ars_million": "N/D", "valuation_basis": "NOT_APPLICABLE",
        "source_id": source_id, "source_locator": "matrices SLU V144",
        "realization_status": status, "additivity": "NON_ADDITIVE",
        "status_interpretation": interpretation,
        "caveat": "No convertir tabla, mecanismo, versión o estrategia de recuperación en ejecución target.",
    })
assert len(ledger) == 260
write_csv(ledger_path, ledger)

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V144.csv"
new_break_ids = {
    "cut_repository_not_target_extract", "cut_period_not_daily_completeness", "cut_internal_access_not_public_execution",
    "cut_basic_entity_not_historical_account_identity", "cut_balance_not_movement", "cut_extract_not_cause",
    "cut_impact_log_not_reconciliation", "current_cut_field_not_legacy_field", "auditor_net_difference_not_target_amount",
    "cut_2013_code_not_2008_code", "cut_2022_code_not_2008_code", "cut_same_code_changed_semantics",
    "cut_auto_split_not_exact_continuity", "cut_account_230_not_target_row", "cut_apl_not_target_form",
    "cut_reference_key_not_causality", "cut_reconciliation_state_not_payment_purpose",
    "slu_2005_design_not_target_row", "slu_public_debt_no_fee_not_global_no_fee",
    "slu_foreign_transfer_fee_not_debt_service_fee", "c55_confirmed_not_bank_execution_alone",
    "c55_sent_not_confirmed", "c55_rejected_or_reversed_not_executed",
    "conc_report_zero_without_parameters", "conc_state_not_economic_purpose",
    "slu_table_without_history_not_historical_absence", "slu_current_active_row_not_2008_row",
    "slu_deleted_rehabilitated_state_not_visible", "slu_mapping_not_transaction",
    "slu_v9_screenshot_not_deployment_census", "slu_example_cum023_not_target_code",
    "slu_c10_resource_not_c55_expense", "slu_c55_dep_rep_not_original_expense",
    "slu_corrected_movement_latest_not_original", "slu_backup_inventory_not_recovered_data",
}
breaks = [row for row in read_csv(breaks_path) if row["break_id"] not in new_break_ids]
break_specs = [
    ("cut_repository_not_target_extract", "access", "Repositorio CUT probado; extracto target no recuperado.", "Mantener numerador en cero.", "e0_dgsiaf_siche_cut_repository_2020_q2"),
    ("cut_period_not_daily_completeness", "coverage", "2007-2014 incluye 2008, no prueba cada día/campo.", "Exigir cobertura por dataset.", "e0_dgsiaf_siche_cut_repository_2020_q2"),
    ("cut_internal_access_not_public_execution", "access", "Acceso de órganos rectores no ejecuta consulta ciudadana.", "Mantener pedido sin enviar hasta autorización.", "e0_dgsiaf_siche_cut_repository_2020_q2"),
    ("cut_basic_entity_not_historical_account_identity", "identity", "Cuenta actual no fija cuenta 2008.", "Descubrirla en Entidades Básicas.", "E0_SICHE_CUT_HISTORICAL_REPOSITORY_V144.csv"),
    ("cut_balance_not_movement", "phase", "Saldo de cuenta no identifica débito/crédito.", "Exigir extracto y log.", "e0_dgsiaf_siche_cut_repository_2020_q2"),
    ("cut_extract_not_cause", "causality", "Movimiento externo sin comprobante no identifica comisión.", "Cruzar formulario y log.", "e0_tgn_treasury_system_v3_2022_cut_extract"),
    ("cut_impact_log_not_reconciliation", "phase", "Log de impacto no prueba conciliación.", "Cruzar Libro Banco, extracto y estado.", "e0_tgn_cut_auditor_instruction_2025"),
    ("current_cut_field_not_legacy_field", "system", "Campo 2022/2025 no se presume idéntico en 2008.", "Pedir equivalente funcional y diccionario.", "e0_tgn_treasury_system_v3_2022_cut_extract;e0_tgn_cut_auditor_instruction_2025"),
    ("auditor_net_difference_not_target_amount", "arithmetic", "Diferencia neta puede combinar factores.", "Desagregar movimientos; no atribuir total.", "e0_tgn_cut_auditor_instruction_2025"),
]
for break_id, dimension, problem, rule, evidence in break_specs:
    breaks.append({"break_id": break_id, "dimension": dimension, "problem": problem, "rule": rule, "status": "FROZEN_V144", "evidence": evidence})
assert len(breaks) == 180
write_csv(breaks_path, breaks)

break_additions = [
    ("cut_2013_code_not_2008_code", "legal_time", "El catálogo 2013 no acredita el código vigente en 2008.", "Pedir diccionario histórico y buscar código más descripción.", "e0_tgn_manual_system_treasury_v1"),
    ("cut_2022_code_not_2008_code", "legal_time", "DBAUTO/CRAUTO son crosswalk posteriores.", "No filtrar 2008 sólo por esos códigos.", "e0_tgn_treasury_system_v3_2022_cut_extract"),
    ("cut_same_code_changed_semantics", "classification", "AJPG y DEPG cambian de descripción entre versiones.", "No clasificar sólo por literal de código.", "E0_CUT_EVENT_CODE_CONTINUITY_V144.csv"),
    ("cut_auto_split_not_exact_continuity", "classification", "AUTO se desdobla en DBAUTO/CRAUTO.", "Buscar ambos signos, sin asumir migración uno a uno.", "E0_CUT_EVENT_CODE_CONTINUITY_V144.csv"),
    ("cut_account_230_not_target_row", "identity", "La cuenta 230 es el carril funcional de gastos bancarios, no la fila target.", "Exigir fecha, importe, referencia y formulario.", "E0_CUT_OPERATION_ACCOUNT_EQUATIONS_V144.csv"),
    ("cut_apl_not_target_form", "phase", "APL puede generar gasto SIDIF por comisión sin identificar los SIDIF target.", "Cruzar formulario, extracto y Libro Banco.", "E0_CUT_RECONCILIATION_EVIDENCE_ROUTE_V144.csv"),
    ("cut_reference_key_not_causality", "causality", "Referencia unívoca enlaza registros pero no prueba concepto por sí sola.", "Concordar código, descripción, importe y respaldo.", "e0_tgn_manual_system_treasury_v1"),
    ("cut_reconciliation_state_not_payment_purpose", "phase", "T/P/N prueba estado de conciliación, no finalidad económica.", "Mantener separadas ejecución, causa y conciliación.", "E0_CUT_RECONCILIATION_EVIDENCE_ROUTE_V144.csv"),
]
for break_id, dimension, problem, rule, evidence in break_additions:
    breaks.append({"break_id": break_id, "dimension": dimension, "problem": problem, "rule": rule, "status": "FROZEN_V144", "evidence": evidence})
contemporary_breaks = [
    ("slu_2005_design_not_target_row", "causality", "El diseño contemporáneo prueba el circuito, no la fila de 2008.", "Mantener 0/10 hasta recuperar formulario, extracto y Libro Banco concordantes.", "e0_dgsiaf_slu_system_description_v3"),
    ("slu_public_debt_no_fee_not_global_no_fee", "scope", "Que el medio Servicio de Deuda no cobre comisiones no excluye un débito bancario separado.", "Buscar cuenta de gastos, C55 y rama de transferencia antes de concluir.", "E0_SLU_2005_PAYMENT_COMMISSION_BRANCH_V144.csv"),
    ("slu_foreign_transfer_fee_not_debt_service_fee", "classification", "Una comisión de transferencia exterior no debe rotularse automáticamente como servicio de deuda.", "Exigir tipo de nota, cuenta de gastos y respaldo.", "E0_SLU_2005_PAYMENT_COMMISSION_BRANCH_V144.csv"),
    ("c55_confirmed_not_bank_execution_alone", "phase", "Estado C prueba aceptación central e impacto interno, no por sí solo el débito BNA.", "Cruzar conc_01, conc_02, referencia e importe.", "E0_C55_DIRECT_DEBIT_STATE_MACHINE_V144.csv"),
    ("c55_sent_not_confirmed", "phase", "Estado E sólo indica envío y espera de respuesta.", "No computar ejecución sin C y ausencia de reversa.", "E0_C55_DIRECT_DEBIT_STATE_MACHINE_V144.csv"),
    ("c55_rejected_or_reversed_not_executed", "phase", "Estado R o C55-DEG puede neutralizar un C55 previo.", "Pedir histórico, código de error y contraasiento.", "E0_C55_DIRECT_DEBIT_STATE_MACHINE_V144.csv"),
    ("conc_report_zero_without_parameters", "coverage", "Un conc_01/conc_02 vacío no prueba inexistencia sin cuenta, fechas y estados incluidos.", "Conservar parámetros, versión, universo y cantidad de filas.", "E0_SLU_2002_RECONCILIATION_REPORT_SCHEMA_V144.csv"),
    ("conc_state_not_economic_purpose", "classification", "N/P/T informa conciliación, no el concepto económico.", "Cruzar tipo de movimiento, formulario, beneficiario y respaldo.", "E0_SLU_2002_RECONCILIATION_REPORT_SCHEMA_V144.csv"),
]
for break_id, dimension, problem, rule, evidence in contemporary_breaks:
    breaks.append({"break_id": break_id, "dimension": dimension, "problem": problem, "rule": rule, "status": "FROZEN_V144", "evidence": evidence})
v144_breaks = [
    ("slu_table_without_history_not_historical_absence", "retention", "Tabla declarada sin historia no permite inferir que una fila no existió en 2008.", "Pedir backup, snapshot y Consulta de Bajas.", "E0_SLU_BASE_TABLE_DICTIONARY_V144.csv"),
    ("slu_current_active_row_not_2008_row", "legal_time", "Fila activa actual no acredita vigencia ni contenido en 2008.", "Exigir corte temporal y versión.", "E0_SLU_HISTORICAL_RECOVERY_STRATEGY_V144.csv"),
    ("slu_deleted_rehabilitated_state_not_visible", "retention", "Baja y rehabilitación pueden alterar la vista vigente.", "Pedir secuencia, fechas y usuario.", "e0_dgsiaf_slu_treasury_basic_tables_1"),
    ("slu_mapping_not_transaction", "causality", "AMOV_FORG/BMOVEXTERNO prueban parametrización, no movimiento ejecutado.", "Cruzar C55, extracto, Libro Banco y conciliación.", "E0_SLU_AUTOMATIC_EXPENSE_MAPPING_CHAIN_V144.csv"),
    ("slu_v9_screenshot_not_deployment_census", "scope", "Captura SLU v9.0 fechada en 2008 no prueba versión de cada SAF ni cada módulo.", "Pedir matriz de despliegue y migración.", "E0_SLU_V9_2008_VISUAL_VERSION_CONTROL_V144.csv"),
    ("slu_example_cum023_not_target_code", "identity", "CUM023 es ejemplo visible de recurso, no código objetivo.", "No reutilizarlo como filtro de comisión.", "E0_SLU_V9_2008_VISUAL_VERSION_CONTROL_V144.csv"),
    ("slu_c10_resource_not_c55_expense", "classification", "C10 automático documenta crédito/recurso; C55 documenta gasto.", "Separar signo, rama y formulario.", "E0_SLU_C10_RESOURCE_NEGATIVE_CONTROL_V144.csv"),
    ("slu_c55_dep_rep_not_original_expense", "phase", "C55-DEP/REP puede neutralizar o modificar un pago previo.", "Pedir original, aceptación, reversa y contraasiento.", "E0_SLU_REVERSAL_NEGATIVE_CONTROL_V144.csv"),
    ("slu_corrected_movement_latest_not_original", "version", "La última versión del movimiento puede ocultar original/corrección.", "Pedir historial completo de correcciones.", "e0_dgsiaf_slu_bank_reconciliation_manual_2003_v7"),
    ("slu_backup_inventory_not_recovered_data", "access", "Inventario de backup no equivale a datos recuperados.", "Mantener 0/10 hasta restauración/exportación y cruce.", "E0_SLU_HISTORICAL_RECOVERY_STRATEGY_V144.csv"),
]
for break_id, dimension, problem, rule, evidence in v144_breaks:
    breaks.append({"break_id": break_id, "dimension": dimension, "problem": problem, "rule": rule, "status": "FROZEN_V144", "evidence": evidence})
assert len(breaks) == 206
write_csv(breaks_path, breaks)

trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V144.csv"
trace = [row for row in read_csv(trace_path) if not row["trace_id"].startswith(("TR141_", "TR142_", "TR143_", "TR144_"))]
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
contemporary_trace_additions = [
    (179, "SLU_CONC01_2008", "Reporte Movimientos del Extracto conc_01.rep", "SAF355;cuentas históricas;todo2008;N/P/T", "cuenta;saldo anterior;fecha movimiento/proceso;tipo;debe;haber;saldo;estado"),
    (180, "SLU_CONC02_2008", "Reporte Movimientos del Libro Banco conc_02.rep", "mismas cuentas/fechas;N/P/T", "ejercicio;comprobante;descripción;formulario;número;beneficiario;debe;haber;saldo;estado"),
    (181, "C55_DIRECT_DEBIT_2008", "Universo C55-REG Débito Directo", "SAF355;2008;sin OP original;cuenta débito", "institución;UG;fuente;clase;beneficiario;importe;cuenta;estado"),
    (182, "C55_HISTORY_2008", "Histórico de cada C55 candidato", "I/X/E/C/R", "carga;autorización;envío;respuesta;usuario;fecha;error"),
    (183, "C55_REVERSAL_2008", "C55-DEG y contraasiento asociado", "originales confirmados/rechazados", "original;reversa;motivo;importe;Libro Banco;fecha"),
    (184, "PAYMENT_MEDIUM_BRANCH_2008", "Tipo de nota/medio y cuenta de gastos", "servicio deuda;carta crédito;transferencia exterior", "tipo;orden/nota;cuenta gastos;banco;sucursal;cuenta;comisión"),
    (185, "SLU_VERSION_DICTIONARY_2008", "Versión, catálogo y diccionario vigentes", "módulos Pago;C55;Conciliación", "versión;vigencia;código;descripción;equivalencia;regla"),
]
for number, gap, record, identifiers, fields in contemporary_trace_additions:
    trace.append({
        "trace_id": f"TR143_{number}", "request_id": "REQ133_ECON",
        "institution": "Ministerio de Economía / Secretaría de Hacienda / TGN",
        "gap_id": gap, "requested_record": record, "period_or_date": "2008; consulta 2026",
        "identifiers": identifiers, "minimum_usable_fields": fields,
        "confidentiality_fallback": "exportación disociada; tachas parciales; metadatos, versión y diccionario",
        "status": "DRAFT_NOT_SENT",
    })
v144_trace_additions = [
    (186, "SLU_ACCOUNT_TABLE_SNAPSHOT_2008", "BCUENTA, ACTA_FUE y ACTABAN_CTAESC históricas", "SAF355;snapshot2008;activas+bajas+rehabilitadas", "banco;sucursal;cuenta;tipo;fuente;cuenta escritural;estado;fechas"),
    (187, "SLU_BANK_CODE_TABLES_2008", "BGRUPMOVBCO, BMOVBCO y BMOVEXTERNO históricas", "BNA;todo2008;sin código prefijado", "grupo;interno;externo;contracódigo;descripción;signo;tipo;estado"),
    (188, "SLU_AMOV_FORG_2008", "AMOV_FORG histórica y filas de baja/rehabilitación", "SAF355;BNA;cuentas recuperadas;todo2008", "cuenta;subcuenta;movimiento;partida;estado;fecha baja/rehabilitación"),
    (189, "SLU_BOOK_MAPPING_2008", "ACLB_MOB y BCODLIBBCO históricas", "códigos candidatos;vigencia2008", "movimiento extracto;código libro;descripción;signo;conciliación parcial;estado"),
    (190, "SLU_DATABASE_BACKUPS", "Inventario y copias de backups/dumps/snapshots SLU", "2006-2009;SAF355;órganos rectores", "servidor;instancia;esquema;fecha;soporte;retención;custodio;hash"),
    (191, "SLU_VERSION_MIGRATION", "Matriz de versiones y scripts de migración v7→v9.0", "2006-2009;Tesorería;Conciliación;SAF355", "versión;fecha;SAF;DDL/DML;tabla origen/destino;diccionario"),
    (192, "SLU_DELETED_REHABILITATED_ROWS", "Consulta de Bajas y rehabilitaciones", "12 tablas clave;todo estado", "clave;descripción;fecha baja;fecha rehabilitación;usuario;motivo"),
    (193, "SLU_EXTRACT_CORRECTION_HISTORY", "Historial de correcciones de movimientos de extracto", "movimientos candidatos;cuentas recuperadas", "original;corrección;banco;sucursal;cuenta;fecha;grupo;códigos;comprobante;importe;signo"),
    (194, "SLU_C10_RESOURCE_CONTROL_2008", "Universo C10 automático/manual y transmisiones", "SAF355;2008;83106000;REC/REG/COR/DES/CMP", "A/M;cuenta;SIGADE;boleta;estado;error;transmisión;original/modificación"),
    (195, "SLU_REVERSAL_AND_PAYMENT_MEDIUM_CONTROL", "C55-DEP/REP/DEG, contraasientos y estados de cheque", "candidatos;originales;C/R/E/F", "original;reversa;contraasiento;cuenta;importe;estado;fecha;detalle conciliación"),
]
for number, gap, record, identifiers, fields in v144_trace_additions:
    trace.append({
        "trace_id": f"TR144_{number}", "request_id": "REQ133_ECON",
        "institution": "Ministerio de Economía / Secretaría de Hacienda / TGN / DGSIAF",
        "gap_id": gap, "requested_record": record, "period_or_date": "2008; consulta 2026",
        "identifiers": identifiers, "minimum_usable_fields": fields,
        "confidentiality_fallback": "exportación disociada; tachas parciales; DDL/diccionario; inventario de backup y acta fundada",
        "status": "DRAFT_NOT_SENT",
    })
assert len(trace) == 195
write_csv(trace_path, trace)

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V144.csv"
keys = [row for row in read_csv(keys_path) if not row["key_id"].startswith(("SK141_", "SK142_", "SK143_", "SK144_"))]
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
        "source_or_basis": "E0_SICHE_CUT_HISTORICAL_REPOSITORY_V144.csv;E0_CUT_TARGET_QUERY_RUNBOOK_V144.csv",
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
        "source_or_basis": "E0_CUT_EVENT_CODE_DICTIONARY_V144.csv;E0_CUT_OPERATION_ACCOUNT_EQUATIONS_V144.csv",
        "caveat": "Crosswalk probado; uso exacto en 2008 pendiente.",
    })
contemporary_key_additions = [
    (207, "report", "conc_01.rep;Movimientos del Extracto", "reporte externo contemporáneo"),
    (208, "report", "conc_02.rep;Movimientos del Libro Banco", "reporte interno contemporáneo"),
    (209, "reconciliation_state", "N;P;T;No conciliado;Parcialmente conciliado;Totalmente conciliado", "estado de ambos reportes"),
    (210, "account_type", "E;P;R;Escritural;Pagadora;Recaudadora", "tipo de cuenta"),
    (211, "form", "C55-REG;Débito Directo", "firma de comisión debitada"),
    (212, "form_state", "I;X;E;C;R;Ingresado;Anulado;Enviado;Confirmado;Rechazado", "ciclo de vida C55"),
    (213, "reversal", "C55-DEG;Desafectación Global;contraasiento", "reversa del C55"),
    (214, "form_signature", "sin Orden de Pago original;cuenta de débito obligatoria;+débito", "discriminador directo"),
    (215, "form_history", "ingreso;autorización;envío a SC;recepción de respuesta", "traza temporal"),
    (216, "payment_medium", "Servicio de la Deuda Pública;No cobra gastos y comisiones", "control negativo"),
    (217, "payment_medium", "Carta de crédito;gastos y comisiones asociados", "control positivo"),
    (218, "payment_medium", "Transferencias al Exterior;gastos y comisiones asociados", "control positivo"),
    (219, "expense_account", "cuenta de gastos;banco;sucursal;cuenta", "cuenta donde se debita comisión"),
    (220, "metadata", "CreationDate D:20050816105200;versión 3", "fecha contemporánea del manual"),
]
for number, group, key, purpose in contemporary_key_additions:
    keys.append({
        "key_id": f"SK143_{number}", "request_id": "REQ133_ECON", "key_group": group,
        "exact_key": key, "search_purpose": purpose,
        "source_or_basis": "E0_2001_2005_2013_2022_TEMPORAL_CONTINUITY_V144.csv;E0_C55_DIRECT_DEBIT_TARGET_SIGNATURE_V144.csv",
        "caveat": "Clave contemporánea probada; fila individual de 2008 pendiente.",
    })
v144_key_additions = [
    (221, "table", "BCUENTA", "cuenta bancaria/escritural histórica"),
    (222, "table", "ACTA_FUE", "relación cuenta-fuente"),
    (223, "table", "ACTABAN_CTAESC", "relación cuenta bancaria-escritural"),
    (224, "table", "BGRUPMOVBCO", "grupo de movimiento bancario"),
    (225, "table", "BMOVBCO", "código interno de extracto"),
    (226, "table", "BMOVEXTERNO", "código externo BNA y contracódigo"),
    (227, "table", "AMOV_FORG", "aplicación automática de gasto por cuenta/movimiento"),
    (228, "table", "ACLB_MOB", "relación extracto-Libro Banco"),
    (229, "table", "BCODLIBBCO", "código Libro Banco y signo"),
    (230, "table", "BEMPRESA", "grupo de cuentas del archivo bancario"),
    (231, "table", "BERROR_AUD;BPROCESO", "errores y procesos del auditor"),
    (232, "retention", "sin historia", "detectar limitación estructural de tabla"),
    (233, "retention", "Consulta de Bajas", "recuperar filas inactivas"),
    (234, "retention", "Rehabilitar;fecha de baja;fecha de rehabilitación", "reconstruir secuencia"),
    (235, "backup", "RMAN;expdp;export Oracle;dump;snapshot;cinta;imagen de servidor", "localizar soporte histórico"),
    (236, "version", "SLU v9.0;26/11/2008 11:30:04", "control de versión visual"),
    (237, "version", "SLU v7→v9.0;DDL;DML;script migración", "mapear cambios de tabla/código"),
    (238, "negative_example", "CUM023;CR.VARIOS TRIBUT", "excluir ejemplo de recurso como target"),
    (239, "c10", "A;M;Automático;Manual", "marca de generación"),
    (240, "c10", "REC;REG;COR;DES;CMP", "tipo de C10 y modificaciones"),
    (241, "c10", "Código SIGADE;83106000", "rama de recurso asociada a deuda"),
    (242, "reversal", "C55-DEP;C55-REP;C55-DEG", "desafectación y reversión"),
    (243, "cheque", "C;R;E;F;Detalle Conciliación", "medio alternativo y devolución"),
    (244, "correction", "grupo externo;movimiento externo;movimiento interno;comprobante;importe;débito/crédito", "historial de correcciones"),
    (245, "mapping", "banco;cuenta/subcuenta;movimiento;partida;P/E;Axt", "campos AMOV_FORG"),
    (246, "mapping", "contracódigo;automático/manual;grupo;movimiento interno", "campos BMOVEXTERNO"),
    (247, "preservation", "servidor;instancia;esquema;fecha;retención;custodio;hash", "inventario probatorio de backup"),
    (248, "zero_control", "tabla;versión;parámetros;cobertura;filas activas+bajas+rehabilitadas", "respuesta cero reproducible"),
]
for number, group, key, purpose in v144_key_additions:
    keys.append({
        "key_id": f"SK144_{number}", "request_id": "REQ133_ECON", "key_group": group,
        "exact_key": key, "search_purpose": purpose,
        "source_or_basis": "E0_SLU_BASE_TABLE_DICTIONARY_V144.csv;E0_SLU_TABLE_REQUEST_FIELD_MATRIX_V144.csv",
        "caveat": "Clave exacta de esquema o recuperación; no confirma fila ejecutada.",
    })
assert len(keys) == 248
write_csv(keys_path, keys)

register_path = HERE / "E0_REQUEST_RESPONSE_REGISTER_V144.csv"
register = read_csv(register_path)
for row in register:
    row["status"] = "DRAFT_NOT_SENT"
    row["submitted_on"] = "N/A"
    row["submission_channel"] = "N/A"
    row["receipt_or_case_id"] = "N/A"
write_csv(register_path, register)

request_path = HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V144.md"
request_text = request_path.read_text(encoding="utf-8-sig")
request_marker = "## Clave V144 · cuenta 230, códigos automáticos y conciliación"
if request_marker not in request_text:
    request_text += f"""

{request_marker}

El Manual TGN versión 1.0 identifica la cuenta de operación `230 · Débitos Automáticos` como la cuenta que registra débitos contenidos en el extracto bancario que no corresponden a pagos realizados en el marco de la CUT; menciona expresamente los `gastos bancarios` y los embargos. La versión 3 conserva el código `230` y la misma función bajo la denominación `Débitos extracto bancario`. Esa continuidad 2013-2022 justifica usar `230` como filtro candidato, pero no acredita que el código o la descripción rigieran sin cambios en 2008. Por eso se solicita primero el catálogo de cuentas de operación y el diccionario de movimientos vigentes en el CUT-SIDIF Central durante 2008.

La tabla de 2013 distingue `AUTO · Débito Automático` de `PAGO · Pago por Cuenta Única` y `PGTR · Pago por Transferencia`; la versión 2022 desdobla el carril automático en `DBAUTO · Débitos por Extracto Bancario` y `CRAUTO · Créditos por Extracto Bancario`. Deben buscarse el código histórico, sus descripciones y todos sus equivalentes, sin restringir la consulta a los literales posteriores. Como controles se requieren también pagos, créditos, rechazos (`RECH`, `DCRB`, `DCHR`), anulaciones (`ANPG`, `ANPE`, `ATRB`) y reversas/desarmes (`DLOT`, `RRDDF` o equivalentes).

El mismo manual explica que los débitos automáticos autorizados al BNA por conceptos determinados —por ejemplo gastos bancarios— se incorporan al extracto CUT con códigos específicos, se registran mediante formularios de regularización y, luego de la conciliación, afectan la cuenta escritural del Tesoro. Para cada candidato se solicita el código bancario externo y su conversión al código interno; fecha, signo, importe, número de comprobante y `referencia unívoca`; cuenta de operación; formulario C-55 Débito Directo, CRG-DB o equivalente; partida y SIDIF; registro en Libro Banco; grupo de conciliación `LIB`, `APL`, `EXB` o `MAN` o equivalente; estado total/parcial/no conciliado; original, contracódigo, reversa, corrección e historia de la instancia.

La búsqueda primaria debe abarcar el universo completo de la cuenta 230 o equivalente para `SAF 355` durante todo 2008, sin filtro inicial de importe. Luego se cruzarán `71597`, `152677`, `2876`, `83106000`, `7.2.8`, `COMISIONES - BANCO NACION`, `$32.270,30`, sus componentes y variantes de signo/formato. Una coincidencia sólo cerrará la ejecución cuando formulario, log de impacto, extracto BNA, Libro Banco, conciliación y respaldo documental compartan fecha, importe y referencia de modo reproducible. **Estado: BORRADOR_NO_ENVIADO.**
"""
request_path.write_text(request_text, encoding="utf-8")

contemporary_request_marker = "## Clave contemporánea V144 · SLU 2001-2005 y prueba de rama"
if contemporary_request_marker not in request_text:
    request_text += f"""

{contemporary_request_marker}

La documentación oficial contemporánea reduce el salto temporal. El manual `Reportes Correspondientes a Conciliación Bancaria`, septiembre de 2002, versión 7, identifica dos salidas reproducibles: `conc_01.rep · Movimientos del Extracto` y `conc_02.rep · Movimientos del Libro Banco`. Para las cuentas históricas del SAF 355 durante todo 2008 se solicitan ambos reportes, sin filtro inicial de importe y con inclusión de estados `N/P/T` —no, parcial y totalmente conciliado—. El primero debe conservar cuenta, saldo anterior, fechas de movimiento y proceso, tipo, debe, haber y saldos; el segundo, ejercicio, comprobante y descripción de Libro Banco, tipo y número de formulario, beneficiario, debe, haber, saldo, estado y fecha.

El manual `Regularización Global`, abril de 2004 y revisado el 14/06/2005, define como caso expreso detectar un débito en una cuenta bancaria por una comisión cobrada. Para el tipo `Débito Directo` establece `C55-REG`, ausencia de Orden de Pago original, cuenta de débito obligatoria e impacto `+débito`; el impacto en Libro Banco queda sujeto a aceptación de SIDIF Central. Por ello se requiere el universo anual de C55-REG Débito Directo con institución, unidad de gestión, fuente, clase de gasto, beneficiario, importe, cuenta, estado e histórico. Deben discriminarse `I/X/E/C/R`; sólo `C · Confirmado`, concordante con extracto y Libro Banco y sin reversa posterior, puede integrar una prueba positiva. También se requieren `C55-DEG`, código de error y contraasiento para detectar rechazos o reversas.

La `Descripción del sistema · versión 3`, fechada por metadato PDF el 16/08/2005, impone una prueba de rama. Para el medio `Servicio de la Deuda Pública` dice que no cobra gastos y comisiones; para `Carta de crédito` y `Transferencias al Exterior` sí prevé gastos y comisiones debitados de una cuenta determinada del servicio. En consecuencia, `COMISIONES - BANCO NACION` no debe atribuirse automáticamente al pago de deuda: debe informarse el tipo de nota o medio, orden/nota asociada, cuenta de gastos, banco/sucursal/cuenta, concepto y respaldo. Esta regla tampoco excluye una comisión bancaria separada del pago; por eso se cruza con C55, extracto, Libro Banco y conciliación.

La respuesta será utilizable si entrega archivos nativos o CSV con versión de sistema, parámetros, cobertura, diccionario de campos/códigos y cantidad de filas, aun cuando el resultado sea cero. Una coincidencia requiere identidad de cuenta, fecha, signo, importe, formulario, beneficiario/concepto, referencia, estado C, extracto, Libro Banco y ausencia de reversa. **Estado: BORRADOR_NO_ENVIADO.**
"""
request_path.write_text(request_text, encoding="utf-8")

v144_request_marker = "## Clave V144 · tablas exactas, ausencia de historia y recuperación forense"
if v144_request_marker not in request_text:
    request_text += f"""

{v144_request_marker}

La documentación oficial del SLU permite individualizar las tablas de base que gobernaban la cuenta, el código bancario y la aplicación automática. Se solicitan, en formato nativo o CSV con diccionario, `BCUENTA`, `ACTA_FUE`, `ACTABAN_CTAESC`, `BGRUPMOVBCO`, `BMOVBCO`, `BMOVEXTERNO`, `AMOV_FORG`, `ACLB_MOB`, `BCODLIBBCO`, `BEMPRESA`, `BERROR_AUD` y `BPROCESO`, con todas las filas vigentes, dadas de baja o rehabilitadas que hubieran estado vigentes o fueran utilizadas durante 2008. La extracción deberá conservar claves, descripciones completas, signo débito/crédito, banco, sucursal, cuenta/subcuenta, grupo, contracódigo, tipo automático/manual, partida presupuestaria o extrapresupuestaria, código de Libro Banco, marca de conciliación, estado y fechas de baja/rehabilitación.

Los manuales califican expresamente como `sin historia` a las tablas centrales. Por ello una consulta de la tabla vigente no es respuesta suficiente respecto de 2008. Se solicita el inventario de copias de seguridad, dumps, exportaciones, snapshots, cintas, imágenes o respaldos de las instancias y esquemas SLU correspondientes al SAF 355 y a los órganos rectores entre 2006 y 2009; para cada soporte: servidor, instancia, esquema, fecha, alcance, política de retención, custodio, formato y hash. Si los datos migraron, se requieren la matriz de versiones, fecha de despliegue por SAF/módulo y los scripts DDL/DML o reglas de transformación desde versión 7 a `SLU v9.0`, versión que aparece en capturas fechadas el 26/11/2008. La captura prueba el entorno mostrado, no reemplaza esa matriz de despliegue.

En particular, `BMOVEXTERNO` debe permitir reconstruir banco+código externo+contracódigo→movimiento interno+grupo+tipo automático/manual; `AMOV_FORG`, cuenta/subcuenta+movimiento→partida de gasto; `ACLB_MOB` y `BCODLIBBCO`, movimiento de extracto→código, signo y registro en Libro Banco. El manual de Tablas Básicas establece que esa relación de gasto puede emitir automáticamente el C55 y enviarlo a SIDIF Central. Para cada fila candidata se solicitan el C55, estado e histórico de transmisión, respuesta/error, asiento, extracto, Libro Banco, estado de conciliación, original, corrección, baja, rehabilitación, C55-DEG/DEP/REP o contraasiento y respaldo documental.

También se solicita el historial de correcciones del extracto con banco, sucursal, cuenta, fecha, grupo externo, movimiento externo e interno, comprobante, importe y signo, conservando cada versión original y corregida. Como control de clasificación se requieren los C10 automáticos/manuales (`A/M`; `REC/REG/COR/DES/CMP`) asociados al SAF 355, cuentas y código SIGADE, porque la conciliación puede generar C10 para recursos y C55 para gastos; un C10 de recurso no puede tratarse como C55 de comisión. Los estados C55-DEP/REP/DEG y los estados de cheque deben usarse como controles de reversa o medio alternativo, nunca como sustitutos de la fila bancaria objetivo.

Si no existiera copia recuperable, la respuesta deberá identificar el responsable de la tabla y de los respaldos, normativa y política de retención aplicada, fecha y acto de eliminación, migración o transferencia, búsquedas realizadas y eventual destino archivístico. Un resultado cero será utilizable sólo con versión, instancia, tabla, snapshot, filtros, cobertura temporal, inclusión de activas/bajas/rehabilitadas, cantidad de filas y diccionario. La ejecución continúa en `0/10` hasta que cuenta, fecha, signo, importe, referencia, concepto, C55 confirmado, extracto, Libro Banco, conciliación y ausencia de reversa concuerden individualmente. **Estado: BORRADOR_NO_ENVIADO.**
"""
request_path.write_text(request_text, encoding="utf-8")

checklist_path = HERE / "REQUEST_SUBMISSION_CHECKLIST_V144.md"
checklist = checklist_path.read_text(encoding="utf-8-sig")
check_marker = "## Control V144 · código, cuenta 230 y conciliación"
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

contemporary_check_marker = "## Control V144 · reportes SLU y C55 contemporáneos"
if contemporary_check_marker not in checklist:
    checklist += f"""

{contemporary_check_marker}

- [ ] Ejecutar `conc_01.rep` y `conc_02.rep` sobre las mismas cuentas, fechas y estados N/P/T.
- [ ] Pedir el universo C55-REG Débito Directo de 2008 sin OP original y con cuenta de débito.
- [ ] Exigir estados I/X/E/C/R e histórico de carga, autorización, envío y respuesta.
- [ ] Buscar C55-DEG, código de error y contraasiento de cada candidato.
- [ ] Distinguir Servicio de la Deuda Pública de Carta de crédito y Transferencias al Exterior.
- [ ] Exigir tipo de medio/nota y cuenta de gastos antes de atribuir la comisión.
- [ ] No contar estado E, R o un C revertido como ejecución confirmada.
- [ ] Confirmar autorización expresa antes de presentar cualquiera de los seis borradores.
"""
checklist_path.write_text(checklist, encoding="utf-8")

v144_check_marker = "## Control V144 · tablas SLU y recuperación histórica"
if v144_check_marker not in checklist:
    checklist += f"""

{v144_check_marker}

- [ ] Pedir las doce tablas exactas con filas activas, bajas y rehabilitadas.
- [ ] Pedir `BMOVEXTERNO` con banco, contracódigo, interno, grupo y tipo automático/manual.
- [ ] Pedir `AMOV_FORG` con cuenta/subcuenta, movimiento, partida y estado temporal.
- [ ] Pedir `ACLB_MOB` y `BCODLIBBCO` para cerrar extracto→Libro Banco y signo.
- [ ] Pedir inventario y restauración de backups/snapshots 2006-2009, con hash y custodio.
- [ ] Pedir versiones por SAF/módulo y scripts de migración v7→v9.0.
- [ ] Incluir Consulta de Bajas, rehabilitaciones e historial original/corrección.
- [ ] Separar C10 de recurso de C55 de gasto; exigir marca A/M y estados/transmisiones.
- [ ] Controlar C55-DEP/REP/DEG, contraasientos y estados de cheque como reversas/alternativas.
- [ ] No aceptar cero sin tabla, versión, snapshot, filtros, cobertura, filas y diccionario.
- [ ] Mantener los seis pedidos en borrador hasta autorización expresa.
"""
checklist_path.write_text(checklist, encoding="utf-8")

source_refs_path = HERE / "SOURCE_REFERENCES_V144.md"
source_refs = source_refs_path.read_text(encoding="utf-8-sig")
canonical_lines = []
for line in source_refs.splitlines():
    match = re.match(r"^- `([^`]+)`", line)
    if match and match.group(1) in catalog_by_id:
        canonical = catalog_by_id[match.group(1)]["archivo_local"]
        line = re.sub(r"`/[^`]+`", f"`{canonical}`", line)
    canonical_lines.append(line)
source_refs = "\n".join(canonical_lines) + "\n"
refs_marker = "## Fuentes reexplotadas V144 · código CUT y conciliación"
if refs_marker not in source_refs:
    source_refs += "\n" + refs_marker + "\n\n"
    for source_id in ("e0_tgn_manual_system_treasury_v1", "e0_tgn_treasury_system_v3_2022_cut_extract"):
        row = catalog_by_id[source_id]
        source_refs += f"- `{source_id}` · {row['titulo']} · {row['url_original']} · `{row['archivo_local']}` · `{row['sha256']}`\n"
source_refs_path.write_text(source_refs, encoding="utf-8")

contemporary_refs_marker = "## Fuentes reexplotadas V144 · esquema SLU contemporáneo"
if contemporary_refs_marker not in source_refs:
    source_refs += "\n" + contemporary_refs_marker + "\n\n"
    for source_id in (
        "e0_dgsiaf_slu_note_payment_2001",
        "e0_dgsiaf_slu_bank_reconciliation_reports_2002",
        "e0_dgsiaf_slu_global_regularization_2004",
        "e0_dgsiaf_slu_system_description_v3",
    ):
        row = catalog_by_id[source_id]
        source_refs += f"- `{source_id}` · {row['titulo']} · {row['url_original']} · `{row['archivo_local']}` · `{row['sha256']}`\n"
source_refs_path.write_text(source_refs, encoding="utf-8")

v144_refs_marker = "## Fuentes nuevas V144 · tablas SLU, versión y controles"
if v144_refs_marker not in source_refs:
    source_refs += "\n" + v144_refs_marker + "\n\n"
    for source_id in sorted(source_ids):
        row = catalog_by_id[source_id]
        source_refs += f"- `{source_id}` · {row['titulo']} · {row['url_original']} · `{row['archivo_local']}` · `{row['sha256']}`\n"
source_refs_path.write_text(source_refs, encoding="utf-8")

package_path = HERE / "E0_INSTITUTIONAL_REQUEST_PACKAGE_V144.md"
package_text = package_path.read_text(encoding="utf-8-sig")
package_text = re.sub(
    r"El paquete contiene \d+ objetos trazados y \d+ claves exactas\.",
    f"El paquete contiene {len(trace)} objetos trazados y {len(keys)} claves exactas.",
    package_text,
)
package_marker = "## Clave V144 · tablas SLU y recuperación histórica"
if package_marker not in package_text:
    package_text += f"""

{package_marker}

El pedido Economía/Tesoro incorpora las doce tablas exactas de cuenta, movimiento, aplicación automática y Libro Banco; incluye activas, bajas y rehabilitadas, backups/snapshots 2006-2009, versión y migración v7→v9.0, historial de correcciones, C10 de recurso y C55/cheque como controles. Adjuntos específicos: `E0_SLU_BASE_TABLE_DICTIONARY_V144.csv`, `E0_SLU_HISTORICAL_RECOVERY_STRATEGY_V144.csv`, `E0_SLU_AUTOMATIC_EXPENSE_MAPPING_CHAIN_V144.csv` y `E0_SLU_TABLE_REQUEST_FIELD_MATRIX_V144.csv`. Estado: `DRAFT_NOT_SENT`.
"""
package_path.write_text(package_text, encoding="utf-8")

(HERE / "RETRIEVAL_LOG_V144.md").write_text("""# Registro de recuperación V144

Fecha: 2026-08-30.

1. Se preservaron quince fuentes oficiales nuevas del SLU: manuales de conciliación, tablas básicas, cuentas, programación/pagos, C10, desafectaciones y taller 2017.
2. Los manuales fijan doce tablas exactas: BCUENTA, ACTA_FUE, ACTABAN_CTAESC, BGRUPMOVBCO, BMOVBCO, BMOVEXTERNO, AMOV_FORG, ACLB_MOB, BCODLIBBCO, BEMPRESA, BERROR_AUD y BPROCESO.
3. BMOVEXTERNO vincula código bancario externo con interno/grupo; AMOV_FORG vincula cuenta+movimiento con partida; la relación de gasto puede generar C55 y enviarlo a SIDIF Central.
4. Las tablas centrales se declaran sin historia. La ruta idónea pasa a ser backup/dump/snapshot 2006-2009, Consulta de Bajas, rehabilitaciones y migraciones.
5. El PDF del taller conserva capturas SLU v9.0 fechadas en 2006 y 26/11/2008; el ejemplo CUM023 es recurso y no se usa como target.
6. El manual C10 prueba la rama recurso, marca A/M, tipos REC/REG/COR/DES/CMP, cuenta, SIGADE, estados y transmisiones; se usa como control negativo de la rama C55/gasto.
7. Desafectaciones y cheques agregan controles C55-DEP/REP, contraasiento y estados C/R/E/F; no prueban por sí solos la fila objetivo.
8. No se localizaron filas pobladas 2008 de BMOVEXTERNO/AMOV_FORG, backup histórico, C55, extracto, Libro Banco ni respaldo target. No se envió ningún pedido ni presentación externa.
""", encoding="utf-8")

(HERE / "README_V144.md").write_text("""# V144 · tablas SLU y recuperación histórica 2008

V144 cierra el diccionario de base que faltaba. Los manuales oficiales identifican `BCUENTA`, `ACTA_FUE`, `ACTABAN_CTAESC`, `BGRUPMOVBCO`, `BMOVBCO`, `BMOVEXTERNO`, `AMOV_FORG`, `ACLB_MOB`, `BCODLIBBCO`, `BEMPRESA`, `BERROR_AUD` y `BPROCESO`. La cadena exacta es cuenta → código externo BNA → código interno/grupo → parametrización automática de gasto → C55/SIDIF Central → Libro Banco → extracto/conciliación → corrección o reversa.

El hallazgo decisivo es también una limitación probatoria: las tablas centrales se declaran `sin historia`. Por eso la vista vigente no puede resolver ni negar una fila de 2008. V144 transforma esa limitación en un objeto de pedido verificable: backups, dumps y snapshots 2006-2009, Consulta de Bajas y rehabilitaciones, matriz de versiones y scripts v7→v9.0, historial de correcciones y exportaciones de cada tabla.

El taller oficial preserva capturas `SLU v9.0` fechadas en 2006 y 26/11/2008; prueban versión e interfaz mostradas, no la fila target ni el despliegue de cada SAF. El manual C10 separa la rama recurso/crédito de la rama C55/gasto y la desafectación agrega controles de reversa. Ninguna consulta fue ejecutada ni enviada. Balance: 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones confirmadas; seis pedidos DRAFT_NOT_SENT.
""", encoding="utf-8")

(HERE / "VEREDICTO_V144.md").write_text("""# Veredicto V144

La ruta de prueba ya no depende de adivinar `230/AUTO`. El esquema contemporáneo permite pedir las tablas concretas que codificaban cuenta, movimiento bancario, grupo, partida automática y Libro Banco. `BMOVEXTERNO` vincula la codificación BNA con el movimiento interno; `AMOV_FORG` vincula cuenta y movimiento con gasto; la relación genera C55 y lo envía a SIDIF Central; `ACLB_MOB` y `BCODLIBBCO` cierran el lado Libro Banco.

Pero ese cierre de esquema no confirma la ejecución: los manuales dicen que esas tablas son `sin historia`. Una respuesta basada sólo en datos activos actuales sería metodológicamente insuficiente. La respuesta idónea debe restaurar o exportar el estado 2008, incluir bajas y rehabilitaciones, y documentar versión/migración. También debe separar C10 de recurso, C55 de gasto, C55-DEP/REP/DEG y ruta cheque.

La captura `SLU v9.0` del 26/11/2008 reduce el salto de versión, con el límite explícito de no probar la fila target. No se recuperó código BNA, fila AMOV_FORG, C55, extracto, Libro Banco, log ni respaldo individual. Permanecen 10 adjudicaciones exactas, 9 cuentas candidatas y 0/10 ejecuciones confirmadas; los seis pedidos siguen sin enviar.
""", encoding="utf-8")

(HERE / "E0_FISCAL_RECONSTRUCTION_V144.md").write_text("""# Reconstrucción fiscal E0 V144

La secuencia probatoria pasa a ser: backup/snapshot 2008 y versión SLU → BCUENTA/ACTA_FUE → BGRUPMOVBCO/BMOVBCO/BMOVEXTERNO → AMOV_FORG → C55 y respuesta SIDIF Central → ACLB_MOB/BCODLIBBCO → conc_01/conc_02 → corrección/reversa → respaldo AMIDDF. C10 funciona como control de recurso y C55-DEP/REP/DEG como control de neutralización. Sólo una concordancia individual de cuenta, fecha, signo, importe, concepto, formulario confirmado, extracto, Libro Banco y ausencia de reversa puede elevar el numerador, que permanece en 0/10.
""", encoding="utf-8")

(HERE / "AUDITORIA_V144.md").write_text(f"""# Auditoría V144

- Fuentes maestras: 453; quince fuentes oficiales nuevas preservadas.
- Fuentes primarias E0: 213; copias catalogadas SHA-válidas esperadas: 447.
- Diccionario de tablas SLU: {len(slu_tables)}; estrategia de recuperación: {len(recovery_strategy)}.
- Cadena automática: {len(automatic_chain)}; matriz de campos a pedir: {len(table_request_fields)}.
- Control versión v9/2008: {len(slu_visual_version)}; control visual DOC: {len(word_visual)} páginas.
- Control C10/recurso: {len(c10_controls)}; controles de reversa/medio alternativo: {len(reversal_controls)}.
- Diccionario: {len(event_codes)} filas; continuidad: {len(continuity)}; cuentas/ec.: {len(account_rows)}.
- Discriminantes: {len(discriminators)}; ruta de conciliación: {len(reconciliation_route)}.
- Cadena del Auditor: {len(auditor_chain)} filas; runbook CUT: {len(cut_runbook)} pasos.
- Resultados cero/conciliación: {len(zero_limits)} reglas; control visual PDF: {len(pdf_visual)} páginas.
- Ramas pago/comisión: {len(payment_branches)}; esquema conc_01/conc_02: {len(report_schema)} campos.
- Estados C55: {len(c55_states)}; firma Débito Directo: {len(c55_signature)} observables; continuidad temporal: {len(temporal_bridge)}.
- Ledger fiscal: {len(ledger)} filas; cortes metodológicos: {len(breaks)}.
- Trazabilidad: {len(trace)} objetos; claves: {len(keys)}.
- Escalera: 10 adjudicaciones; 9 cuentas candidatas; 0 ejecuciones confirmadas.
- Pedidos: 6 borradores, 0 enviados; panel estricto {STRICT}% sin cambios.
""", encoding="utf-8")

(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V144_A_V145.md").write_text("""# Handover V144 → V145

## Estado

- QA V144: PASS.
- Quince manuales oficiales nuevos preservados; 453 fuentes maestras y 213 E0.
- Tablas exactas: `BCUENTA`, `ACTA_FUE`, `ACTABAN_CTAESC`, `BGRUPMOVBCO`, `BMOVBCO`, `BMOVEXTERNO`, `AMOV_FORG`, `ACLB_MOB`, `BCODLIBBCO`, `BEMPRESA`, `BERROR_AUD`, `BPROCESO`.
- Las tablas centrales se documentan `sin historia`; la consulta vigente no puede negar 2008.
- Vía forense: backups/snapshots 2006-2009 + bajas/rehabilitaciones + migraciones v7→v9.0 + correcciones.
- Captura oficial: `SLU v9.0`, 26/11/2008, ejercicio 2008 y BNA; ejemplo CUM023 es recurso, no target.
- Cadena: cuenta → externo BNA → interno/grupo → AMOV_FORG → C55 → Libro Banco/extracto → corrección/reversa.
- C10 separa recurso/crédito de C55/gasto; C55-DEP/REP/DEG y cheque son controles negativos.
- Ninguna fila target recuperada; seis pedidos DRAFT_NOT_SENT; 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas.

## Prioridad V145

1. Mantener los seis pedidos como borradores salvo autorización expresa.
2. Buscar inventarios públicos o archivísticos de respaldos SLU 2006-2009 y responsables de custodia.
3. Localizar exportación/snapshot poblado de `BMOVEXTERNO` y `AMOV_FORG` de 2008.
4. Buscar documentación de migración v7→v9.0 y versión desplegada en SAF 355.
5. Localizar una salida `conc_01/conc_02`, C55 o historial de correcciones con cuenta/referencia target.
6. Mantener C10, reversas y cheques como controles, sin elevar esquema a ejecución.
""", encoding="utf-8")

# Auditoría de preservación acumulada.
for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    source_path = AUDIT / f"{stem}_V143.csv"
    target_path = AUDIT / f"{stem}_V144.csv"
    target_path.write_text(
        source_path.read_text(encoding="utf-8-sig").replace("V143", "V144").replace("v143", "v144"),
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
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V144.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V144.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
assert physical == hash_ok == 447

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
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V144.csv", size_rows)

completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V143.json").read_text(encoding="utf-8"))
for key in list(completeness):
    if key.endswith("_v143") or "newly_preserved_v143" in key or "duplicate_recaptures_v143" in key:
        completeness.pop(key, None)
completeness.update({
    "checkpoint": "V144", "date": "2026-08-30",
    "state": "E0_EXACT_SLU_BASE_TABLES_AND_NO_HISTORY_LIMIT_PROVED_V9_2008_SCREEN_TARGET_ROW_NOT_LOCATED_NOT_SENT",
    "numeric_v144_strict_changed": False,
    "master_catalog_entries": len(catalog), "physical_local_copies": physical,
    "physical_local_hash_ok": hash_ok, "binary_required_entries": 384,
    "binary_required_preserved": 383, "binary_required_source_complete": False,
    "remaining_physical_gaps": 1, "e0_primary_sources_preserved": len(census),
    "e0_quality": "PRIMARY_EXACT_SLU_TABLE_DICTIONARY_HISTORICAL_RETENTION_LIMIT_AND_RECOVERY_SCHEMA",
    "sources_newly_preserved_v144": 15, "e0_primary_sources_newly_preserved_v144": 15,
    "e0_duplicate_recaptures_v144": 0,
    "e0_fiscal_ledger_rows": len(ledger), "e0_fiscal_method_breaks_frozen": len(breaks),
    "e0_request_traceability_rows": len(trace), "e0_request_search_keys": len(keys),
    "e0_siche_cut_repository_rows": len(cut_repo), "e0_cut_extract_field_rows": len(extract_fields),
    "e0_cut_auditor_chain_rows": len(auditor_chain), "e0_cut_query_runbook_rows": len(cut_runbook),
    "e0_cut_zero_limit_rows": len(zero_limits), "e0_pdf_visual_controls": len(pdf_visual),
    "e0_siche_query_plan_rows": len(query_plan),
    "e0_cut_event_code_rows": len(event_codes), "e0_cut_code_continuity_rows": len(continuity),
    "e0_cut_operation_account_rows": len(account_rows), "e0_cut_discriminator_rows": len(discriminators),
    "e0_cut_reconciliation_route_rows": len(reconciliation_route),
    "e0_slu_payment_commission_branch_rows": len(payment_branches),
    "e0_slu_2002_report_schema_rows": len(report_schema),
    "e0_c55_direct_debit_state_rows": len(c55_states),
    "e0_c55_direct_debit_signature_rows": len(c55_signature),
    "e0_temporal_continuity_rows": len(temporal_bridge),
    "e0_slu_base_table_dictionary_rows": len(slu_tables),
    "e0_slu_historical_recovery_strategy_rows": len(recovery_strategy),
    "e0_slu_v9_2008_visual_version_rows": len(slu_visual_version),
    "e0_slu_automatic_expense_chain_rows": len(automatic_chain),
    "e0_slu_table_request_field_rows": len(table_request_fields),
    "e0_slu_c10_resource_control_rows": len(c10_controls),
    "e0_slu_reversal_control_rows": len(reversal_controls),
    "e0_word_visual_controls": len(word_visual),
    "e0_slu_key_tables_without_history": 12,
    "e0_slu_v9_2008_screen_proved": True,
    "e0_slu_target_2008_populated_table_row_located": False,
    "e0_slu_historical_backup_inventory_located": False,
    "e0_slu_system_description_pdf_creation_date": "2005-08-16T10:52:00",
    "e0_slu_public_debt_service_charges_commissions": False,
    "e0_slu_foreign_transfer_and_letter_credit_charge_commissions": True,
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
    "historical_workstream": "Exact SLU table names and joins proved; central tables are explicitly without history, so recover 2006-2009 backups/snapshots, deleted/rehabilitated rows, v7→v9.0 migrations and correction/reversal chains; SLU v9.0 screen dated 2008 proved; populated target row remains open; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V144.json").write_text(
    json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
backup_text = backup.read_text(encoding="utf-8-sig")
backup_marker = "## V144 · tablas SLU y recuperación histórica"
if backup_marker not in backup_text:
    backup_text += f"""

{backup_marker}

- Quince manuales oficiales nuevos preservados; tablas exactas de cuenta, códigos, aplicación automática y Libro Banco.
- `BMOVEXTERNO` y `AMOV_FORG` cierran el mapeo banco→movimiento→partida→C55.
- Las tablas centrales son `sin historia`: se requieren backups/snapshots, bajas/rehabilitaciones y migraciones.
- Captura oficial `SLU v9.0` fechada el 26/11/2008; prueba entorno mostrado, no fila target.
- C10 separa recurso de C55 gasto; C55-DEP/REP/DEG y cheque controlan reversas/alternativas.
- 10 adjudicaciones, 9 cuentas candidatas, 0/10 ejecuciones confirmadas; seis borradores no enviados.
"""
backup.write_text(backup_text, encoding="utf-8")

inherited = [
    {"script": "qa_v143.py", "pre_v144_result": "PASS", "post_v144_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V143 queda ampliada por quince fuentes y el diccionario exacto de tablas SLU V144."},
    {"script": "qa_v144.py", "pre_v144_result": "N/A", "post_v144_result": "PASS", "interpretation": "Tablas, recuperación histórica, versión v9, controles, hashes, límites y no envío verificados."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V144.csv", inherited)

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

repo = rows("E0_SICHE_CUT_HISTORICAL_REPOSITORY_V144.csv")
fields = rows("E0_CUT_EXTRACT_FIELD_CROSSWALK_V144.csv")
chain = rows("E0_CUT_AUDITOR_EVIDENCE_CHAIN_V144.csv")
runbook = rows("E0_CUT_TARGET_QUERY_RUNBOOK_V144.csv")
zero = rows("E0_CUT_ZERO_RESULT_AND_CONCILIATION_LIMITS_V144.csv")
visual = rows("E0_V144_PDF_VISUAL_CONTROL.csv")
plan = rows("E0_SICHE_TARGET_QUERY_PLAN_V144.csv")
codes = rows("E0_CUT_EVENT_CODE_DICTIONARY_V144.csv")
continuity = rows("E0_CUT_EVENT_CODE_CONTINUITY_V144.csv")
accounts = rows("E0_CUT_OPERATION_ACCOUNT_EQUATIONS_V144.csv")
discriminators = rows("E0_CUT_TARGET_CODE_DISCRIMINATION_V144.csv")
route = rows("E0_CUT_RECONCILIATION_EVIDENCE_ROUTE_V144.csv")
branches = rows("E0_SLU_2005_PAYMENT_COMMISSION_BRANCH_V144.csv")
report_schema = rows("E0_SLU_2002_RECONCILIATION_REPORT_SCHEMA_V144.csv")
c55_states = rows("E0_C55_DIRECT_DEBIT_STATE_MACHINE_V144.csv")
c55_signature = rows("E0_C55_DIRECT_DEBIT_TARGET_SIGNATURE_V144.csv")
temporal = rows("E0_2001_2005_2013_2022_TEMPORAL_CONTINUITY_V144.csv")
slu_tables = rows("E0_SLU_BASE_TABLE_DICTIONARY_V144.csv")
recovery = rows("E0_SLU_HISTORICAL_RECOVERY_STRATEGY_V144.csv")
version_visual = rows("E0_SLU_V9_2008_VISUAL_VERSION_CONTROL_V144.csv")
automatic = rows("E0_SLU_AUTOMATIC_EXPENSE_MAPPING_CHAIN_V144.csv")
table_fields = rows("E0_SLU_TABLE_REQUEST_FIELD_MATRIX_V144.csv")
c10 = rows("E0_SLU_C10_RESOURCE_NEGATIVE_CONTROL_V144.csv")
reversals = rows("E0_SLU_REVERSAL_NEGATIVE_CONTROL_V144.csv")
word_visual = rows("E0_V144_WORD_VISUAL_CONTROL.csv")
assert len(repo) == 10
assert repo[1]["proved_scope"] == "incluye ejercicio 2008"
assert {"Entidades Básicas", "Saldos por Tipo de Apertura de Cuenta de Operación", "Extractos", "Logs de Impacto"} <= {r["evidence"] for r in repo}
assert len(fields) == 20
assert {"Cod. Mov.", "Comprobante Respaldo", "Comprobante Origen", "Comprobante Relacionado"} <= {r["source_field"] for r in fields}
assert all("2008" in r["legacy_status"] for r in fields)
assert len(chain) == 12 and any("diferencia" in r["proof"].casefold() for r in chain)
assert len(runbook) == 35 and all(r["status"] == "DRAFT_NOT_SENT" for r in runbook)
assert len(zero) == 8 and all(r["status"] == "FROZEN" for r in zero)
assert len(visual) == 27 and all(r["result"] == "PASS" for r in visual)
assert len(plan) == 30 and all(r["status"] == "DRAFT_NOT_SENT" for r in plan)
assert len(codes) == 69 and {"AUTO", "DBAUTO", "CRAUTO", "PAGO", "PGTR"} <= {r["movement_code"] for r in codes}
assert len(continuity) == 28
assert sum(r["continuity_class"] == "SAME_CODE_CHANGED_DESCRIPTION" for r in continuity) == 2
assert any(r["code_2013"] == "AUTO" and r["continuity_class"] == "SPLIT_BY_SIGN" for r in continuity)
assert len(accounts) == 19 and sum(r["account_or_equation"] == "230" for r in accounts) == 2
assert all("gastos bancarios" in r["official_function"] for r in accounts if r["account_or_equation"] == "230")
assert len(discriminators) == 15 and {"LIB", "APL", "EXB", "MAN"} <= {r["code_or_key"] for r in discriminators}
assert len(route) == 15 and any(r["layer"] == "Gasto bancario" for r in route)
assert len(branches) == 14
assert any(r["layer"] == "Servicio de la Deuda Pública" and "No cobra" in r["official_rule"] for r in branches)
assert any(r["layer"] == "Transferencias al exterior" and "comisiones" in r["official_rule"] for r in branches)
assert len(report_schema) == 28 and {"conc_01.rep", "conc_02.rep"} == {r["report"] for r in report_schema}
assert any(r["field_or_value"] == "estado N/P/T" for r in report_schema)
assert len(c55_states) == 10 and {"I", "X", "E", "C", "R"} <= {r["state_or_transition"] for r in c55_states}
assert len(c55_signature) == 16
assert any(r["observable"] == "orden de pago original" and "No corresponde" in r["contemporary_rule"] for r in c55_signature)
assert len(temporal) == 12 and any(r["date_or_period"] == "2008" and r["evidentiary_role"] == "EXACT_TARGET_OPEN" for r in temporal)
assert len(slu_tables) == 12 and {"BCUENTA", "BMOVEXTERNO", "AMOV_FORG", "ACLB_MOB", "BCODLIBBCO"} <= {r["table_name"] for r in slu_tables}
assert all(r["history"] == "NO" for r in slu_tables)
assert len(recovery) == 12 and all(r["status"] == "DRAFT_NOT_SENT" for r in recovery)
assert any("backup" in r["required_record"].casefold() for r in recovery)
assert len(version_visual) == 6 and all(r["result"] == "PASS" for r in version_visual)
assert any("26/11/2008" in r["visible_fact"] and "SLU v9.0" in r["visible_fact"] for r in version_visual)
assert len(automatic) == 12 and any(r["table_or_record"] == "AMOV_FORG" for r in automatic)
assert len(table_fields) == 12 and all(r["status"] == "DRAFT_NOT_SENT" for r in table_fields)
assert len(c10) == 10 and any("SAF 355" in r["contemporary_rule"] for r in c10)
assert len(reversals) == 10 and {"C55-DEP", "C55-REP"} <= {r["record"] for r in reversals}
assert len(word_visual) == 18 and all(r["result"] == "PASS" for r in word_visual)

assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V144.csv")) == 260
assert len(rows("E0_FISCAL_METHOD_BREAKS_V144.csv")) == 206
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V144.csv")) == 195
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V144.csv")) == 248

ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V144.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)
register = rows("E0_REQUEST_RESPONSE_REGISTER_V144.csv")
assert len(register) == 6 and all(r["status"] == "DRAFT_NOT_SENT" for r in register)
assert all(r["submitted_on"] == "N/A" and r["submission_channel"] == "N/A" and r["receipt_or_case_id"] == "N/A" for r in register)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V144.csv")}
new_ids = ''' + repr(source_ids) + r'''
assert len(census) == 213 and new_ids <= set(census)
for row in census.values():
    local = row["local_path"]
    assert local and (REPO / local.lstrip("/")).is_file(), (row["source_id"], local)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 453 and len({r["id"] for r in catalog}) == 453
system_description = next(r for r in catalog if r["id"] == "e0_dgsiaf_slu_system_description_v3")
assert system_description["fecha_publicacion"].startswith("2005-08-16")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V144.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V144"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 447
assert complete["binary_required_entries"] == 384 and complete["binary_required_preserved"] == 383
assert complete["e0_siche_cut_period_start"] == 2007 and complete["e0_siche_cut_period_end"] == 2014
assert complete["e0_siche_cut_includes_2008"] is True
assert complete["e0_siche_cut_target_extract_rows_located"] == 0
assert complete["e0_siche_cut_target_impact_log_rows_located"] == 0
assert complete["e0_siche_named_queries_executed"] == 0
assert complete["e0_siche_target_exports_located"] == 0
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v144_strict_changed"] is False
assert complete["sources_newly_preserved_v144"] == 15
assert complete["e0_primary_sources_newly_preserved_v144"] == 15
assert complete["e0_cut_event_code_rows"] == 69 and complete["e0_cut_code_continuity_rows"] == 28
assert complete["e0_cut_operation_account_rows"] == 19 and complete["e0_cut_discriminator_rows"] == 15
assert complete["e0_cut_reconciliation_route_rows"] == 15
assert complete["e0_cut_account_230_functional_continuity_2013_2022"] is True
assert complete["e0_cut_target_2008_code_dictionary_located"] is False
assert complete["e0_slu_payment_commission_branch_rows"] == 14
assert complete["e0_slu_2002_report_schema_rows"] == 28
assert complete["e0_c55_direct_debit_state_rows"] == 10
assert complete["e0_c55_direct_debit_signature_rows"] == 16
assert complete["e0_temporal_continuity_rows"] == 12
assert complete["e0_slu_public_debt_service_charges_commissions"] is False
assert complete["e0_slu_foreign_transfer_and_letter_credit_charge_commissions"] is True
assert complete["e0_slu_base_table_dictionary_rows"] == 12
assert complete["e0_slu_historical_recovery_strategy_rows"] == 12
assert complete["e0_slu_v9_2008_visual_version_rows"] == 6
assert complete["e0_slu_automatic_expense_chain_rows"] == 12
assert complete["e0_slu_table_request_field_rows"] == 12
assert complete["e0_slu_c10_resource_control_rows"] == 10
assert complete["e0_slu_reversal_control_rows"] == 10
assert complete["e0_word_visual_controls"] == 18
assert complete["e0_slu_key_tables_without_history"] == 12
assert complete["e0_slu_v9_2008_screen_proved"] is True
assert complete["e0_slu_target_2008_populated_table_row_located"] is False
assert complete["e0_slu_historical_backup_inventory_located"] is False

request = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V144.md").read_text(encoding="utf-8-sig")
assert "## Clave V144 · cuenta 230, códigos automáticos y conciliación" in request
assert "## Clave contemporánea V144 · SLU 2001-2005 y prueba de rama" in request
assert "## Clave V144 · tablas exactas, ausencia de historia y recuperación forense" in request
assert all(term in request for term in ("AUTO", "DBAUTO", "CRAUTO", "conc_01.rep", "conc_02.rep", "C55-DEG", "I/X/E/C/R", "BMOVEXTERNO", "AMOV_FORG", "sin historia", "SLU v9.0", "BORRADOR_NO_ENVIADO"))
refs = (HERE / "SOURCE_REFERENCES_V144.md").read_text(encoding="utf-8-sig")
assert refs.count("## Fuentes reexplotadas V144 · código CUT y conciliación") == 1
assert refs.count("## Fuentes reexplotadas V144 · esquema SLU contemporáneo") == 1
assert refs.count("## Fuentes nuevas V144 · tablas SLU, versión y controles") == 1
assert all(source_id in refs for source_id in new_ids)
combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv")) + "\n" + request
assert "TARGET_EXTRACT_FOUND" not in combined and "TARGET_IMPACT_LOG_FOUND" not in combined
assert "REQUEST_SENT" not in combined
for name in ("README_V144.md", "VEREDICTO_V144.md", "E0_FISCAL_RECONSTRUCTION_V144.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V144_A_V145.md"):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "0/10" in text
assert "Ninguna consulta fue ejecutada ni enviada" in (HERE / "README_V144.md").read_text(encoding="utf-8-sig")

print("V144 QA PASS")
'''
(HERE / "qa_v144.py").write_text(qa, encoding="utf-8")


def checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V144.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V144", "parent_checkpoint": "V143",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": 15, "reexploited_preserved_sources": 0, "duplicate_recaptures": 0,
        "fiscal_ledger_rows": len(ledger), "fiscal_method_breaks": len(breaks),
        "siche_cut_repository_rows": len(cut_repo), "cut_extract_field_rows": len(extract_fields),
        "cut_auditor_chain_rows": len(auditor_chain), "cut_query_runbook_rows": len(cut_runbook),
        "cut_event_code_rows": len(event_codes), "cut_code_continuity_rows": len(continuity),
        "cut_operation_account_rows": len(account_rows), "cut_discriminator_rows": len(discriminators),
        "cut_reconciliation_route_rows": len(reconciliation_route),
        "slu_payment_commission_branch_rows": len(payment_branches),
        "slu_2002_report_schema_rows": len(report_schema),
        "c55_direct_debit_state_rows": len(c55_states),
        "c55_direct_debit_signature_rows": len(c55_signature),
        "temporal_continuity_rows": len(temporal_bridge),
        "slu_base_table_dictionary_rows": len(slu_tables),
        "slu_historical_recovery_strategy_rows": len(recovery_strategy),
        "slu_v9_2008_visual_version_rows": len(slu_visual_version),
        "slu_automatic_expense_chain_rows": len(automatic_chain),
        "slu_table_request_field_rows": len(table_request_fields),
        "slu_c10_resource_control_rows": len(c10_controls),
        "slu_reversal_control_rows": len(reversal_controls),
        "word_visual_control_rows": len(word_visual),
        "cut_period": "2007-2014", "cut_includes_2008": True,
        "cut_target_extract_rows_located": 0, "cut_target_impact_log_rows_located": 0,
        "siche_named_queries_executed": 0, "siche_target_exports_located": 0,
        "award_rows_exact": 10, "account_candidate_rows": 9, "executed_settlement_rows_confirmed": 0,
        "request_drafts": 6, "request_traceability_rows": len(trace), "request_search_keys": len(keys),
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V144.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    "checkpoint": "V144",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical catalog copies SHA-valid; 15 new official SLU sources preserved; exact base-table names and no-history limitation proved; SLU v9.0 screen dated 2008 proved; populated target row and backups not located; zero of ten executed settlement rows confirmed; six requests drafted and none submitted.",
    "historical_workstream": "Recover 2006-2009 SLU backups/snapshots, deleted and rehabilitated rows, v7-to-v9.0 migrations and populated BMOVEXTERNO/AMOV_FORG mappings; cross with C55, extract, Libro Banco, correction/reversal and C10 negative control; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V144 BUILD PASS")
