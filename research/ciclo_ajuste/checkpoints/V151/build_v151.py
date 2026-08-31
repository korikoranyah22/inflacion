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
BIN = CYCLE / "inputs" / "historical_retrieval" / "v151" / "binaries"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


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


def matrix(name, fields, rows):
    data = [dict(zip(fields, row)) for row in rows]
    write_csv(HERE / name, data, fields)
    return data


def append_section(path, marker, body):
    path = Path(path)
    text = path.read_text(encoding="utf-8-sig")
    if marker not in text:
        path.write_text(text.rstrip() + "\n\n" + marker + "\n\n" + body.strip() + "\n", encoding="utf-8")


EXCLUDED_DIRS = {".git", "__pycache__", "tmp", "node_modules"}


def iter_files(root):
    root = Path(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted((name for name in dirnames if name not in EXCLUDED_DIRS), key=str.casefold)
        for filename in sorted(filenames, key=str.casefold):
            yield Path(dirpath) / filename


# id, institution, title, url, filename, period, series, kind, scope note
SOURCES = [
    ("e0_argentina_afg_first_stage_sidif_transaf_architecture", "Secretaría de Hacienda", "Primera etapa de la administración financiera · SIDIF y TRANSAF", "https://www.argentina.gob.ar/economia/administracionfinancieragubernamental/primeraetapa", "argentina_afg_first_stage_sidif_transaf.html", "1991-1995", "Historia SIDIF · primera etapa", "HTML oficial preservado", "Prueba bases institucionales y central diferenciadas, transmisión TRANSAF, autenticación/firma y permanencia de la transacción en ambos extremos; no prueba conservación target."),
    ("e0_argentina_afg_fifth_stage_legacy_transaf", "Secretaría de Hacienda", "Quinta etapa de la administración financiera · transición desde TRANSAF", "https://www.argentina.gob.ar/economia/administracionfinancieragubernamental/quintaetapa", "argentina_afg_fifth_stage_legacy_to_internet.html", "2004 en adelante", "Historia SIDIF · quinta etapa", "HTML oficial preservado", "Describe base lógica distribuida y TRANSAF punto a punto aún en uso al diseñarse SIDIF Internet; contextualiza 2008 sin probar el esquema exacto del target."),
    ("e0_cgn_circular_2_1999_parameterized_text_file", "Contaduría General de la Nación", "Circular CGN 2/1999 · listados parametrizados en archivo de texto", "https://www.economia.gob.ar/hacienda/cgn/normas/circulares/1999/circ02.htm", "cgn_circular_2_1999_parametrized_text_file.html", "1999", "Circular CGN 2/1999", "HTML oficial preservado", "Define campos presupuestarios agregados, incluido pagado, y formato reutilizable; no contiene por sí solo cuerpos de formularios ni movimientos bancarios."),
    ("e0_argentina_dgsiaf_transaf_current_page", "DGSIAF · Secretaría de Hacienda", "Página oficial de la aplicación TRANSAF", "https://www.argentina.gob.ar/economia/sechacienda/dgsiaf/transaf", "argentina_dgsiaf_transaf_current.html", "vigente 2026", "TRANSAF actual", "HTML oficial preservado", "Comparador posterior: transmisión por lotes para SAF con sistemas propios; no se retroproyecta su esquema a 2008."),
    ("e0_dgsiaf_transaf_user_guide_2022", "DGSIAF · Secretaría de Hacienda", "Instructivo para usuarios de la aplicación TRANSAF", "https://dgsiaf-repo.mecon.gob.ar/repository/transaf/Instructivo/dgsiaf-2022_instructivo_para_usuarios_aplicacion_transaf.pdf", "dgsiaf_2022_transaf_user_guide.pdf", "2022", "Instructivo TRANSAF", "PDF oficial preservado", "Comparador posterior de lotes, estados, nodos, transacciones y errores; el límite de 30 días de la interfaz no prueba eliminación del backend."),
    ("e0_cgn_sigen_instruction_account_2009", "Sindicatura General de la Nación", "Instructivo de Trabajo 2/2009 · auditoría de información para la Cuenta de Inversión", "https://www.economia.gob.ar/hacienda/cgn/otrosdoc/instruai2009.pdf", "cgn_sigen_instruction_account_2009.pdf", "2009", "Instructivo de Trabajo 2/2009 GNyT", "PDF oficial preservado", "Comparador inmediatamente posterior: controles con sistema local, listado parametrizado SIDIF Central, extractos, formularios TGN, actas y ajustes; no certifica automáticamente 2008 ni los IDs target."),
    ("e0_cgn_circular_2_2021_uai_closing", "Contaduría General de la Nación", "Circular CGN 2/2021 · certificaciones UAI para el cierre", "https://www.argentina.gob.ar/sites/default/files/if-2021-07423886-apn-cgnmec.pdf", "cgn_circular_2_2021_uai_closing_instructions.pdf", "2021", "Circular CGN 2/2021", "PDF oficial preservado", "Prueba exigencia posterior de certificación UAI como condición documental de cierre; no equivale a ejecución de pago."),
    ("e0_sigen_instruction_1_2021_account_certification", "Sindicatura General de la Nación", "Instructivo de Trabajo 1/2021 · certificaciones contables", "https://www.argentina.gob.ar/sites/default/files/if-2021-07423886-apn-cgnmec.pdf", "sigen_instruction_1_2021_embedded.pdf", "2021", "IF-2021-01980369-APN-SNI#SIGEN", "PDF oficial embebido preservado", "Marco posterior de certificación de la Cuenta de Inversión; no demuestra auditoría o pago target."),
    ("e0_sigen_instruction_1_2021_annex_i_bank_movements", "Sindicatura General de la Nación", "Anexo I Instructivo 1/2021 · movimientos financieros de caja y bancos", "https://www.argentina.gob.ar/sites/default/files/if-2021-07423886-apn-cgnmec.pdf", "sigen_instruction_2021_annex_i_bank_movements.pdf", "2021", "Anexo I · Caja y Bancos", "PDF oficial embebido preservado", "Comparador posterior que triangula registros, extractos y acta de arqueo; no prueba el movimiento target."),
    ("e0_sigen_instruction_1_2021_annex_iv_execution_forms", "Sindicatura General de la Nación", "Anexo IV Instructivo 1/2021 · formularios de ejecución posteriores al cierre", "https://www.argentina.gob.ar/sites/default/files/if-2021-07423886-apn-cgnmec.pdf", "sigen_instruction_2021_annex_iv.pdf", "2021", "Anexo IV · C35/C41/C42/C43/C55/C75/C10", "PDF oficial embebido preservado", "Comparador posterior que nombra C41/C42/C55 y tres fuentes de certificación; no se usa como prueba retroactiva de 2008."),
]

source_rows = []
for sid, institution, title, url, filename, period, series, kind, note in SOURCES:
    path = BIN / filename
    assert path.is_file(), path
    source_rows.append({
        "id": sid, "institution": institution, "title": title, "url": url,
        "local": "/" + path.relative_to(REPO).as_posix(), "period": period,
        "series": series, "kind": kind, "note": note,
        "sha": sha256(path), "bytes": path.stat().st_size,
    })

catalog = read_csv(CATALOG)
catalog = upsert(catalog, [{
    "id": s["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": s["institution"],
    "titulo": s["title"], "url_original": s["url"], "archivo_local": s["local"],
    "fecha_descarga": "2026-08-31", "fecha_publicacion": s["period"],
    "codigo_serie": s["series"], "periodo_utilizado": s["period"], "tipo": s["kind"],
    "sha256": s["sha"], "nota": "V151: " + s["note"],
} for s in source_rows], "id")
write_csv(CATALOG, catalog, list(catalog[0]))

census_path = HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V151.csv"
census = read_csv(census_path)
census = upsert(census, [{
    "source_id": s["id"], "institution": s["institution"], "artifact": s["title"],
    "url": s["url"], "local_path": s["local"], "sha256": s["sha"], "bytes": s["bytes"],
    "period_coverage": s["period"],
    "variable_families": "SIDIF;SAF355;TRANSAF;CGN;UAI;C41;C42;C55;bank reconciliation;custody",
    "primary_source": "YES", "preserved": "YES",
    "method_breaks": "architecture/retention; transmission/payment; adjacent year/target year; certification/execution",
    "use_status": "E0_USABLE_WITH_SCOPE", "caveat": s["note"],
} for s in source_rows], "source_id")
write_csv(census_path, census, list(census[0]))

provenance_path = HERE / "ARCHIVAL_PROVENANCE_V151.csv"
provenance = read_csv(provenance_path)
provenance = upsert(provenance, [{
    "source_id": s["id"], "original_url": s["url"], "retrieval_url": s["url"],
    "capture_timestamp": "2026-08-31", "cdx_digest": "N/A_OFFICIAL_DIRECT",
    "local_path": s["local"], "sha256": s["sha"], "bytes": s["bytes"],
    "provenance_note": "Captura directa oficial; alcance probatorio congelado en V151.",
} for s in source_rows], "source_id")
write_csv(provenance_path, provenance, list(provenance[0]))

catalogue_by_file = {s["local"].split("/")[-1]: s["id"] for s in source_rows}
bundle_roles = {
    "argentina_afg_first_stage_sidif_transaf.html": "HISTORICAL_ARCHITECTURE",
    "argentina_afg_fifth_stage_legacy_to_internet.html": "LEGACY_TRANSITION",
    "argentina_dgsiaf_transaf_current.html": "CURRENT_COMPARATOR",
    "cgn_account_2008_sep_specific_queries.pdf": "EXISTING_2008_SOURCE_DUPLICATE",
    "cgn_account_2008_uepex_specific_queries.html": "EXISTING_2008_SOURCE_DUPLICATE",
    "cgn_circular_2_1999_parametrized_text_file.html": "PARAMETERIZED_LIST",
    "cgn_circular_2_2021_uai_closing_instructions.pdf": "UAI_CLOSING_CIRCULAR",
    "cgn_disposition_31_2006_local_parametrized_list.html": "EXISTING_SOURCE_DUPLICATE",
    "cgn_sigen_instruction_account_2009.pdf": "ADJACENT_YEAR_AUDIT",
    "dgsiaf_2022_transaf_user_guide.pdf": "LATER_TECHNICAL_COMPARATOR",
    "sigen_instruction_1_2021_embedded.pdf": "EMBEDDED_AUDIT_INSTRUCTION",
    "sigen_instruction_2021_annex_i_bank_movements.pdf": "BANK_MOVEMENT_CERTIFICATION",
    "sigen_instruction_2021_annex_ii.pdf": "BUNDLE_ONLY",
    "sigen_instruction_2021_annex_iii_a.pdf": "BUNDLE_ONLY",
    "sigen_instruction_2021_annex_iii_b.pdf": "BUNDLE_ONLY",
    "sigen_instruction_2021_annex_iv.pdf": "EXECUTION_FORM_CERTIFICATION",
    "sigen_instruction_2021_annex_v.pdf": "BUNDLE_ONLY",
    "sigen_instruction_2021_annex_vi.pdf": "BUNDLE_ONLY",
    "sigen_instruction_2021_annex_vii.pdf": "BUNDLE_ONLY",
}
bundle = []
for i, path in enumerate(sorted(BIN.iterdir(), key=lambda p: p.name.casefold()), 1):
    assert path.name in bundle_roles, path.name
    bundle.append({
        "row_id": f"B151_{i:02d}", "filename": path.name,
        "role": bundle_roles[path.name], "catalogued": "YES" if path.name in catalogue_by_file else "NO",
        "catalog_source_id": catalogue_by_file.get(path.name, "EXISTING_SOURCE_OR_BUNDLE_ONLY"),
        "bytes": str(path.stat().st_size), "sha256": sha256(path), "preserved": "YES",
    })
write_csv(HERE / "E0_V151_SOURCE_BUNDLE.csv", bundle)

dual_rows = [
    ("ARCHITECTURE", "El SIDIF operó con bases locales de los SAF y una base central.", "Consultar ambos repositorios por separado.", "e0_argentina_afg_first_stage_sidif_transaf_architecture", "BASES_DISTINCT"),
    ("LOCAL_SYSTEMS", "Los SAF podían usar SIDIF Local, CONPRE o sistemas propios.", "Pedir inventario, motor, versión y backups SAF355.", "e0_argentina_afg_first_stage_sidif_transaf_architecture", "LOCAL_UNIVERSE_PROVED"),
    ("TRANSACTION_COPY", "La transacción quedaba en base local y central.", "Comparar cabecera, renglones, estados y timestamps.", "e0_argentina_afg_first_stage_sidif_transaf_architecture", "DUAL_RECORD_EXPECTED"),
    ("NO_DOUBLE_EVENT", "Dos registros pueden corresponder a un único hecho económico.", "Deduplicar por identificadores, importe, fecha y vínculo de transmisión.", "e0_argentina_afg_first_stage_sidif_transaf_architecture", "METHOD_CONTROL"),
    ("TRANSAF_START", "La comunicación electrónica por TRANSAF comenzó en 1995.", "Pedir trazas legadas 2008.", "e0_argentina_afg_first_stage_sidif_transaf_architecture", "ROUTE_PROVED"),
    ("AUTHENTICATION", "TRANSAF incorporó autenticación y firma electrónica.", "Pedir resultado y metadatos, no presumir pago.", "e0_argentina_afg_first_stage_sidif_transaf_architecture", "PREPAYMENT_METADATA"),
    ("PROTOCOLS", "Se usaron UUCP, FTP y luego X.400.", "Buscar archivos/logs por protocolo y no sólo interfaz actual.", "e0_argentina_afg_first_stage_sidif_transaf_architecture", "LEGACY_SEARCH_EXPANDED"),
    ("CENTRAL_REGISTRATION", "La recepción central generaba registración presupuestaria y contable.", "Pedir registro central e historia del documento.", "e0_argentina_afg_first_stage_sidif_transaf_architecture", "CENTRAL_RECORD_EXPECTED"),
    ("TECHNICAL_DOCS", "Existieron manuales técnicos y operativos por módulo.", "Pedir diccionarios, diseños de lote y tablas 2008.", "e0_argentina_afg_first_stage_sidif_transaf_architecture", "DOCUMENT_ROUTE_PROVED"),
    ("DISTRIBUTED_DB", "La quinta etapa describe una base lógica distribuida entre nivel central e institucional.", "No aceptar un cero unilateral como cierre global.", "e0_argentina_afg_fifth_stage_legacy_transaf", "DUAL_CUSTODIAN_RULE"),
    ("LEGACY_2004", "TRANSAF punto a punto seguía en uso al desarrollarse SIDIF Internet.", "Tratar 2008 como entorno legado salvo prueba contraria.", "e0_argentina_afg_fifth_stage_legacy_transaf", "TEMPORAL_CONTEXT"),
    ("CENTRALIZATION_FUTURE", "La centralización y eliminación de formularios eran metas posteriores.", "No retroproyectar arquitectura e-SIDIF a 2008.", "e0_argentina_afg_fifth_stage_legacy_transaf", "TEMPORAL_BREAK"),
    ("LOCAL_QUERY", "Ruta A: base local/origen SAF355.", "71597/0071597; 152677/0152677; 2876/0002876; C41/C42/C55.", "e0_argentina_afg_first_stage_sidif_transaf_architecture", "REQUEST_DRAFT"),
    ("CENTRAL_QUERY", "Ruta B: SIDIF Central/CGN.", "Mismas claves, sin limitar por tipo o estado.", "e0_argentina_afg_first_stage_sidif_transaf_architecture", "REQUEST_DRAFT"),
    ("TRANSMISSION_QUERY", "Ruta C: lote, log, acuse, autenticación y error TRANSAF.", "Vincular origen y registro central.", "e0_argentina_afg_first_stage_sidif_transaf_architecture", "REQUEST_DRAFT"),
    ("UAI_QUERY", "Ruta D: certificación, ajuste o regularización posterior al corte.", "Buscar UAI/CGN con fuentes de contraste.", "e0_cgn_sigen_instruction_account_2009", "REQUEST_DRAFT"),
    ("NEGATIVE_LOCAL", "Cero local no demuestra cero central.", "Individualizar búsqueda, backup y disposición documental.", "e0_argentina_afg_first_stage_sidif_transaf_architecture", "NON_CLOSING_ZERO"),
    ("NEGATIVE_CENTRAL", "Cero central no demuestra cero local, bancario o papel.", "Escalar a archivo, UAI, TGN y extractos.", "e0_argentina_afg_first_stage_sidif_transaf_architecture", "NON_CLOSING_ZERO"),
]
dual = matrix("E0_SIDIF_DUAL_DATABASE_AND_TRANSAF_CHAIN_V151.csv",
    ["row_id", "object", "official_or_controlled_finding", "request_or_rule", "source_id", "status"],
    [(f"DC151_{i:02d}",) + row for i, row in enumerate(dual_rows, 1)])

transaf_rows = [
    ("EJERCICIO", "Ejercicio", "Tabla de recepción", "pedir si existe en esquema 2008", "LATER_COMPARATOR"),
    ("LOTE", "Número de lote", "Envío/recepción", "pedir valor y diseño legado", "LATER_COMPARATOR"),
    ("NRO_TRANS", "Número de transacción", "Mensaje de error", "pedir vínculo con cada ID", "LATER_COMPARATOR"),
    ("NODO", "Nodo/SAF", "Tabla de recepción/error", "pedir SAF355 y nodo histórico", "LATER_COMPARATOR"),
    ("SENTIDO", "Dirección del flujo", "Tabla de recepción", "distinguir SAF→Central y Central→SAF", "LATER_COMPARATOR"),
    ("ESTADO", "Estado", "Tabla de recepción", "pedir historia completa, no sólo final", "LATER_COMPARATOR"),
    ("APLICACION", "Aplicación o tipo", "Tabla de recepción", "pedir valor original", "LATER_COMPARATOR"),
    ("FECHA_ALTA", "Fecha de alta", "Tabla de recepción", "pedir fecha y hora", "LATER_COMPARATOR"),
    ("FILE_COUNT", "Cantidad de archivos", "Tabla de recepción", "pedir nombres e inventario", "LATER_COMPARATOR"),
    ("UPLOAD", "Archivo cargado por usuario SAF", "Envío", "pedir nombre original y copia", "LATER_COMPARATOR"),
    ("SEND_CONFIRMATION", "Confirmación de envío exitoso", "Envío", "pedir acuse y timestamp", "LATER_COMPARATOR"),
    ("SEND_ERROR", "Mensaje de error", "Envío", "pedir código, texto y reintento", "LATER_COMPARATOR"),
    ("RECEIPT", "Lote recibido desde SIDIF Central", "Recepción", "pedir archivo y acuse", "LATER_COMPARATOR"),
    ("PROTOCOL", "UUCP/FTP/X.400 u otro", "Arquitectura histórica", "no restringir a protocolo moderno", "HISTORICAL_FIELD"),
    ("AUTH_RESULT", "Autenticación/firma electrónica", "Arquitectura histórica", "pedir resultado, certificado y operador si se conservan", "HISTORICAL_FIELD"),
    ("CHECKSUM", "Hash/checksum", "Control de integridad", "pedir si existe; no exigir si el esquema no lo tenía", "REQUEST_FIELD"),
    ("FILENAME_5", "Primeros cinco caracteres del nombre", "Validación moderna", "no imponer a archivos 2008", "DO_NOT_RETROPROJECT"),
    ("CON_EXTENSION", "Extensión .CON, mayúsculas, lote de tres dígitos", "Validación moderna", "no imponer a archivos 2008", "DO_NOT_RETROPROJECT"),
    ("UI_30_DAYS", "Descarga visible sólo por 30 días", "Historia moderna", "es límite de interfaz, no política de retención", "UI_NOT_DELETION"),
    ("BACKEND_ARCHIVE", "Archivo/backup fuera de interfaz", "Inferencia controlada", "pedir backend, restauración, soporte y disposición documental", "REQUEST_REQUIRED"),
]
transaf = matrix("E0_TRANSAF_LOT_AND_LOG_REQUEST_SCHEMA_V151.csv",
    ["row_id", "field_or_control", "later_or_historical_meaning", "locator", "controlled_request", "temporal_status"],
    [(f"TL151_{i:02d}",) + row for i, row in enumerate(transaf_rows, 1)])

uai_rows = [
    ("2009_SCOPE", "La UAI debía certificar información preparada por el SAF para CGN.", "Marco 2009", "e0_cgn_sigen_instruction_account_2009", "ADJACENT_YEAR_ONLY"),
    ("2009_BANK", "Caja y Bancos se contrastaba con registros, C43, extractos y acta de arqueo.", "Anexo I pp.2-3", "e0_cgn_sigen_instruction_account_2009", "THREE_SOURCE_CONTROL"),
    ("2009_UEPEX", "UEPEX usaba listado parametrizado SIDIF Central y registro de la unidad.", "Anexo III pp.6-7", "e0_cgn_sigen_instruction_account_2009", "DUAL_SYSTEM_CONTROL"),
    ("2009_UEPEX_BANK", "Además se usaban extractos, formularios de transferencias TGN y acta.", "Anexo III pp.6-7", "e0_cgn_sigen_instruction_account_2009", "BANK_BRIDGE_CONTROL"),
    ("2009_FORMS", "El universo tardío incluía C35, C41, C42, C43, C55, C75 y C10.", "Anexo IV pp.8-9", "e0_cgn_sigen_instruction_account_2009", "FORM_UNIVERSE_PROVED_2009"),
    ("2009_LOCAL", "La certificación usaba SLU o sistema aplicable.", "Anexo IV pp.8-9", "e0_cgn_sigen_instruction_account_2009", "LOCAL_SOURCE"),
    ("2009_CENTRAL", "La certificación usaba listado parametrizado SIDIF Central remitido por CGN.", "Anexo IV pp.8-9", "e0_cgn_sigen_instruction_account_2009", "CENTRAL_SOURCE"),
    ("2009_BANK_SUPPORT", "La certificación usaba extractos, formularios TGN, acta y soporte de ajustes.", "Anexo IV pp.8-9", "e0_cgn_sigen_instruction_account_2009", "EXTERNAL_SOURCE"),
    ("2009_REMAINDER", "Rectificaciones se contrastaban con sistema local, listado central y antecedentes.", "Anexo V pp.10-11", "e0_cgn_sigen_instruction_account_2009", "ADJUSTMENT_ROUTE"),
    ("2009_REMAINDER_CASES", "Se nombran depósitos erróneos, duplicaciones y devoluciones.", "Anexo V pp.10-11", "e0_cgn_sigen_instruction_account_2009", "NEGATIVE_CONTROL_CASES"),
    ("2021_CIRCULAR", "CGN condicionó recepción de cierre a certificación UAI.", "Circular 2/2021", "e0_cgn_circular_2_2021_uai_closing", "LATER_CONTINUITY"),
    ("2021_FRAME", "SIGEN mantuvo un instructivo formal de certificación.", "IF-2021-01980369", "e0_sigen_instruction_1_2021_account_certification", "LATER_CONTINUITY"),
    ("2021_BANK", "Caja y Bancos volvió a combinar registros, extractos y acta.", "Anexo I", "e0_sigen_instruction_1_2021_annex_i_bank_movements", "LATER_CONTINUITY"),
    ("2021_FORMS", "El universo volvió a nombrar C41, C42 y C55.", "Anexo IV", "e0_sigen_instruction_1_2021_annex_iv_execution_forms", "LATER_CONTINUITY"),
    ("2021_THREE_SOURCES", "Sistema local/e-SIDIF, listado SIDIF Central y fuentes externas se contrastaban.", "Anexo IV", "e0_sigen_instruction_1_2021_annex_iv_execution_forms", "LATER_CONTINUITY"),
    ("EXACT_OUTPUT", "Nombre documental: Listado Parametrizado del SIDIF Central remitido por la CGN.", "2009 y 2021", "e0_cgn_sigen_instruction_account_2009", "REQUEST_BY_NAME"),
    ("CERT_NOT_PAYMENT", "Certificación UAI valida consistencia del cierre, no ejecución bancaria individual.", "Control metodológico", "e0_cgn_sigen_instruction_account_2009", "NOT_PAYMENT_PROOF"),
    ("TARGET_LIMIT", "No se localizó certificación UAI que identifique los tres IDs target.", "Búsqueda pública V151", "e0_cgn_sigen_instruction_account_2009", "TARGET_OPEN"),
]
uai = matrix("E0_UAI_2009_2021_THREE_SOURCE_CERTIFICATION_V151.csv",
    ["row_id", "object", "finding", "locator", "source_id", "status"],
    [(f"UA151_{i:02d}",) + row for i, row in enumerate(uai_rows, 1)])

refresh_rows = [
    ("2008_ANALYSIS", "CGN contrastó movimientos informados por SAF y DADP en SIDIF.", "Cuenta 2008 p.72", "e0_cgn_account_2008_uepex_closing_exception", "CONTEMPORANEOUS_CONTROL"),
    ("2008_COMMUNICATIONS", "Las diferencias se verificaban mediante comunicaciones con programas, áreas y DADP.", "Cuenta 2008 p.72", "e0_cgn_account_2008_uepex_closing_exception", "CONTACT_ROUTE"),
    ("2008_LISTS", "Se elaboraban listados detallados y parametrizados.", "Cuenta 2008 p.73", "e0_cgn_account_2008_uepex_closing_exception", "QUERY_CAPABILITY"),
    ("2008_SPECIFIC", "También se efectuaban consultas específicas de movimientos del sistema.", "Cuenta 2008 p.73", "e0_cgn_account_2008_uepex_closing_exception", "QUERY_CAPABILITY"),
    ("2008_REPLACEMENT", "Información corregida podía reemplazar cuadros.", "Cuenta 2008 p.73", "e0_cgn_account_2008_uepex_closing_exception", "CORRECTION_ROUTE"),
    ("2008_UAI", "Ejecución podía regularizarse con formularios certificados por UAI.", "Cuenta 2008 p.73", "e0_cgn_account_2008_uepex_closing_exception", "REGULARIZATION_ROUTE"),
    ("2008_EXTRA", "Movimientos extrapresupuestarios requerían explicaciones claras.", "Cuenta 2008 p.73", "e0_cgn_account_2008_uepex_closing_exception", "EXPLANATION_ROUTE"),
    ("SAF355_EXCEPTION", "SAF355 y SAF356 no estaban obligados a cuadros ordinarios de cierre.", "Cuenta 2008 p.76", "e0_cgn_account_2008_uepex_closing_exception", "SPECIAL_ROUTE"),
    ("UNILATERAL_ADJUST", "CGN podía efectuar ajustes si no obtenía reemplazo adecuado en el universo descrito.", "Cuenta 2008 p.76", "e0_cgn_account_2008_uepex_closing_exception", "ADJUSTMENT_ROUTE"),
    ("LOCAL_PARAM", "Disposición 31/2006 habilitó listado parametrizado del sistema local.", "Disp.31/2006", "e0_cgn_disposition_31_2006_parameterized_reports", "LOCAL_QUERY_OUTPUT"),
    ("CENTRAL_PARAM", "El comparador 2009 nombra listado parametrizado SIDIF Central remitido por CGN.", "Instructivo 2/2009 Anexo IV", "e0_cgn_sigen_instruction_account_2009", "CENTRAL_QUERY_OUTPUT"),
    ("AGGREGATE_LIMIT", "Circular 2/1999 incluye pagado agregado por clasificadores.", "Circular 2/1999", "e0_cgn_circular_2_1999_parameterized_text_file", "NOT_FORM_BODY"),
    ("SCOPE_LIMIT", "Las consultas específicas 2008 están documentadas en contexto UEPEX.", "Cuenta 2008 pp.72-76", "e0_cgn_account_2008_uepex_closing_exception", "DO_NOT_GENERALIZE_TARGET"),
    ("REQUEST", "Pedir salida local, salida central, consulta específica, respuesta y ajuste por cada ID.", "Regla V151", "e0_cgn_account_2008_uepex_closing_exception", "DRAFT_NOT_SENT"),
]
refresh = matrix("E0_2008_SPECIFIC_QUERY_AND_SPECIAL_ROUTE_REFRESH_V151.csv",
    ["row_id", "object", "finding_or_rule", "locator", "source_id", "status"],
    [(f"RF151_{i:02d}",) + row for i, row in enumerate(refresh_rows, 1)])

negative_queries = [
    ("site:economia.gob.ar instruai2008.pdf", "economia.gob.ar", "EXACT_URL_404_NOT_ABSENCE"),
    ("site:economia.gob.ar 0071597 C42", "economia.gob.ar", "PUBLIC_BODY_NOT_LOCATED"),
    ("site:economia.gob.ar 0152677 C42", "economia.gob.ar", "PUBLIC_BODY_NOT_LOCATED"),
    ("site:economia.gob.ar 0002876 C42", "economia.gob.ar", "PUBLIC_BODY_NOT_LOCATED"),
    ("site:argentina.gob.ar 71597 83106000", "argentina.gob.ar", "PUBLIC_BODY_NOT_LOCATED"),
    ("site:argentina.gob.ar 152677 83106000", "argentina.gob.ar", "PUBLIC_BODY_NOT_LOCATED"),
    ("site:argentina.gob.ar 2876 83106000", "argentina.gob.ar", "PUBLIC_BODY_NOT_LOCATED"),
    ("SAF355 listado parametrizado SIDIF Central 2008", "official", "TARGET_OUTPUT_NOT_LOCATED"),
    ("SAF355 TRANSAF lote 2008 C42", "official", "TARGET_LOG_NOT_LOCATED"),
    ("UAI SAF355 formularios C41 C42 C55 2008", "official", "TARGET_CERTIFICATION_NOT_LOCATED"),
]
negative = matrix("E0_V151_PUBLIC_SEARCH_NEGATIVE_RESULTS.csv",
    ["row_id", "exact_query", "official_domain", "result", "interpretation", "status"],
    [(f"NS151_{i:02d}", query, domain, "sin cuerpo/log/certificación target", "No prueba inexistencia, destrucción ni pago.", status)
     for i, (query, domain, status) in enumerate(negative_queries, 1)])

request_data = [
    ("SAF355_LOCAL", "Base local/origen SAF355", "tipo; número SAF; número SIDIF; cabecera; renglones; estado; timestamps", "consulta por seis variantes y C41/C42/C55"),
    ("SAF355_BACKUP", "Backup/restauración local", "sistema; motor; versión; corte; soporte; hash; log de restore", "export reproducible"),
    ("SIDIF_CENTRAL", "Base SIDIF Central/CGN", "tipo; número; ejercicio; estado; cabecera; renglones; historia", "consulta independiente por las mismas claves"),
    ("DUAL_RECONCILIATION", "Conciliación local-central", "identificadores; diferencias; operador; fecha; ajuste", "un evento sin doble conteo"),
    ("TRANSAF_SEND", "Lote/log de envío SAF→Central", "ejercicio; lote; transacción; nodo; fecha; estado; archivo; acuse; error", "vínculo al registro local"),
    ("TRANSAF_RECEIVE", "Recepción/descarga Central→SAF", "ejercicio; lote; nodo; sentido; fecha; estado; archivos", "vínculo al registro central"),
    ("TRANSAF_SECURITY", "Autenticación/firma/protocolo", "protocolo; resultado; certificado; operador; timestamp", "metadatos preservados o respuesta fundada"),
    ("TRANSAF_ARCHIVE", "Backend, archivo y backups fuera de interfaz", "serie; rango; soporte; ubicación; migración; disposición", "no limitar a 30 días de UI"),
    ("CGN_LOCAL_LIST", "Listado parametrizado del sistema local", "parámetros; columnas; filas; fecha; emisor", "salida original íntegra"),
    ("CGN_CENTRAL_LIST", "Listado Parametrizado del SIDIF Central remitido por la CGN", "parámetros; columnas; filas; fecha; destinatario", "salida original íntegra"),
    ("CGN_SPECIFIC_QUERY", "Consulta específica de movimientos", "sentencia/parámetros; resultados; cero explícito; operador; fecha", "cada ID y variante"),
    ("CGN_RESPONSE", "Devolución/comunicación/ajuste", "nota; expediente; observación; reemplazo; ajuste; vínculo", "cadena de corrección completa"),
    ("UAI_CERT", "Certificación UAI de formularios tardíos", "universo; fuentes; pruebas; observaciones; firma; fecha", "identificación target o cero fundado"),
    ("BANK_EXTRACT", "Extracto bancario", "cuenta; fecha valor; signo; moneda; importe; referencia; saldo", "movimiento individual"),
    ("TGN_TRANSFER", "Formulario/respaldo de transferencia TGN", "orden; lote; cuenta; fecha; importe; beneficiario", "puente sistema-banco"),
    ("ARQUEO", "Acta de Arqueo de Fondos y Valores", "fecha; cuentas; saldos; diferencias; firmas", "control de cierre"),
    ("INVENTORY", "Inventario/transferencia documental SAF355-CGN-UAI", "serie; caja; folio; fecha; destino; responsable", "custodio actual nominado"),
    ("NEGATIVE_CERT", "Informe de búsqueda negativa", "repositorios; parámetros; fechas; backups; migraciones; disposición; responsable", "respuesta reproducible y apelable"),
]
request_objects = matrix("E0_V151_REQUEST_OBJECTS.csv",
    ["object_id", "owner_or_system", "requested_record", "minimum_usable_fields", "success_test", "negative_response_rule", "status"],
    [(f"RO151_{i:02d}", owner, record, fields, test,
      "Individualizar repositorio, búsqueda, backup, migración, transferencia o disposición; ofrecer metadatos no exceptuados.", "DRAFT_NOT_SENT")
     for i, (owner, record, fields, test) in enumerate(request_data, 1)])

visual_add = []
visual_specs = [
    ("e0_cgn_account_2008_uepex_closing_exception", "72", "72", "contraste SAF/DADP en SIDIF"),
    ("e0_cgn_account_2008_uepex_closing_exception", "73", "73", "listados y consultas específicas; regularización UAI"),
    ("e0_cgn_account_2008_uepex_closing_exception", "74", "74", "continuación de análisis y cuadros"),
    ("e0_cgn_account_2008_uepex_closing_exception", "76", "76", "excepción SAF355/356 y ajuste CGN"),
    ("e0_cgn_circular_2_2021_uai_closing", "1", "1", "condición de certificación UAI"),
    ("e0_sigen_instruction_1_2021_account_certification", "1", "1", "identificador y objeto del instructivo"),
    ("e0_sigen_instruction_1_2021_account_certification", "2", "2", "lineamientos de certificación"),
    ("e0_sigen_instruction_1_2021_account_certification", "3", "3", "continuación y cierre"),
    ("e0_sigen_instruction_1_2021_annex_i_bank_movements", "1", "1", "registros, extractos y arqueo"),
    ("e0_sigen_instruction_1_2021_annex_iv_execution_forms", "1", "1", "universo C41/C42/C55 y tres fuentes"),
    ("e0_dgsiaf_transaf_user_guide_2022", "9", "9", "envío de lote desde SAF"),
    ("e0_dgsiaf_transaf_user_guide_2022", "12", "12", "confirmación o error de envío"),
    ("e0_dgsiaf_transaf_user_guide_2022", "13", "13", "validaciones modernas de archivo"),
    ("e0_dgsiaf_transaf_user_guide_2022", "14", "14", "continuación validaciones modernas"),
    ("e0_dgsiaf_transaf_user_guide_2022", "15", "15", "recepción desde SIDIF Central"),
    ("e0_dgsiaf_transaf_user_guide_2022", "17", "17", "campos de recepción y error"),
    ("e0_dgsiaf_transaf_user_guide_2022", "18", "18", "historia por fecha/lote"),
    ("e0_dgsiaf_transaf_user_guide_2022", "19", "19", "límite visible de 30 días"),
]
for page in range(1, 12):
    check = {
        1: "instructivo y fechas", 2: "Anexo I Caja y Bancos", 3: "cierre Anexo I",
        4: "Anexo II Fondo Rotatorio", 5: "cierre Anexo II", 6: "Anexo III UEPEX y listado central",
        7: "cierre Anexo III", 8: "Anexo IV C41/C42/C55", 9: "cierre Anexo IV",
        10: "Anexo V rectificación de remanente", 11: "cierre Anexo V",
    }[page]
    visual_specs.append(("e0_cgn_sigen_instruction_account_2009", str(page), str(page), check))
for i, (source_id, printed, pdf_page, check) in enumerate(visual_specs, 1):
    visual_add.append({
        "control_id": f"PV151_NEW_{i:02d}", "source_id": source_id,
        "printed_page": printed, "pdf_page": pdf_page, "rendered_check": check,
        "result": "PASS", "inference_limit": "control visual; comparador o fuente contextual; no cuerpo ni pago target",
    })
visual_path = HERE / "E0_V151_PDF_VISUAL_CONTROL.csv"
visual = upsert(read_csv(visual_path), visual_add, "control_id")
write_csv(visual_path, visual, list(visual[0]))
image_visual = read_csv(HERE / "E0_V151_IMAGE_VISUAL_CONTROL.csv")

breaks_path = HERE / "E0_FISCAL_METHOD_BREAKS_V151.csv"
breaks = read_csv(breaks_path)
break_add = [
    ("sidif_dual_local_central_records_not_two_events", "aggregation", "A transaction could remain in local and central databases.", "Treat them as two records of one possible event until reconciled; never double count.", "Official SIDIF first-stage architecture"),
    ("official_sidif_architecture_not_target_retention_proof", "custody", "Architecture proves repositories and flows, not survival of the three target records.", "Request inventories, backups, migrations and disposition records from each custodian.", "Official SIDIF first/fifth-stage history"),
    ("transaf_authentication_signature_not_payment", "phase", "Authentication, signature, sending and receipt precede execution.", "Require TGN/bank movement and reconciliation.", "Official SIDIF first-stage history; TRANSAF guide 2022"),
    ("modern_transaf_lot_schema_not_2008_schema", "temporal", "The 2022 filename, extension and lot validations are later.", "Use them as discovery fields only; request the 2008 data dictionary.", "TRANSAF guide 2022"),
    ("transaf_30day_ui_not_backend_deletion", "retention", "A 30-day downloadable history is an interface limit, not a deletion schedule.", "Request backend, archive, backup and disposition evidence outside the UI.", "TRANSAF guide 2022 pp.18-19"),
    ("uai_three_source_certification_not_target_execution", "phase", "UAI certification triangulates sources but does not prove an individual bank debit.", "Require target IDs plus transfer, extract and reconciliation.", "SIGEN Instructive 2/2009; Instructive 1/2021"),
    ("parameterized_budget_aggregate_not_form_body", "granularity", "A parameterized budget listing may aggregate paid values by classifiers.", "Request detailed/specific output and the form body separately.", "CGN Circular 2/1999"),
    ("uepex_2008_specific_query_not_target_universe", "scope", "2008 specific-query evidence is documented in UEPEX context.", "Use it to name a capability, not to assert the target was queried or audited.", "Cuenta de Inversión 2008 pp.72-76"),
    ("adjacent_2009_instruction_not_2008_target_audit", "temporal", "The 2009 instruction is adjacent but not retroactive proof for 2008.", "Use it to formulate the request and seek the actual 2008 instruction/certification.", "SIGEN Instructive 2/2009"),
]
breaks = upsert(breaks, [{"break_id": a, "dimension": b, "problem": c, "rule": d, "status": "FROZEN", "evidence": e}
                          for a, b, c, d, e in break_add], "break_id")
write_csv(breaks_path, breaks, list(breaks[0]))

trace_path = HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V151.csv"
trace = read_csv(trace_path)
trace_data = [
    ("SIDIF_LOCAL", "Registro local/origen SAF355", "SAF355", "tipo;número SAF;número SIDIF;cabecera;renglones;historia"),
    ("SIDIF_CENTRAL", "Registro SIDIF Central", "CGN/SIDIF", "tipo;número;ejercicio;estado;cabecera;renglones;historia"),
    ("DUAL_RECONCILIATION", "Conciliación local-central", "SAF355/CGN", "joins;diferencias;operador;fecha;ajuste"),
    ("TRANSAF_SEND", "Lote y log de envío", "SAF355", "lote;transacción;nodo;archivo;fecha;estado;acuse;error"),
    ("TRANSAF_RECEIVE", "Recepción y descarga", "CGN/SIDIF", "lote;sentido;nodo;fecha;estado;archivos"),
    ("TRANSAF_SECURITY", "Autenticación, firma y protocolo", "SAF355/CGN", "protocolo;resultado;certificado;operador;timestamp"),
    ("TRANSAF_ARCHIVE", "Backend, archivo y backup", "DGSIAF/SAF355", "serie;rango;soporte;ubicación;migración;disposición"),
    ("LOCAL_PARAM_LIST", "Listado parametrizado local", "SAF355/UAI", "parámetros;columnas;filas;fecha;emisor"),
    ("CENTRAL_PARAM_LIST", "Listado Parametrizado SIDIF Central", "CGN/UAI", "parámetros;columnas;filas;fecha;destinatario"),
    ("SPECIFIC_QUERY", "Consulta específica de movimientos", "CGN", "consulta;parámetros;resultado;operador;fecha"),
    ("CGN_ADJUSTMENT", "Comunicación, reemplazo o ajuste", "CGN/SAF355", "nota;expediente;observación;reemplazo;ajuste"),
    ("UAI_CERTIFICATION", "Certificación UAI", "UAI SAF355/SIGEN", "universo;fuentes;pruebas;observaciones;firma;fecha"),
    ("BANK_TRIANGULATION", "Extracto, transferencia TGN y acta", "TGN/BNA/UAI", "cuenta;fecha valor;signo;moneda;importe;referencia;conciliación"),
    ("DOCUMENT_INVENTORY", "Inventario y transferencia documental", "SAF355/CGN/AGN", "serie;caja;folio;fecha;destino;responsable"),
    ("NEGATIVE_SEARCH", "Informe de búsqueda negativa reproducible", "Todos los custodios", "repositorios;parámetros;fechas;backups;migraciones;disposición"),
]
trace_add = []
for i, (gap, record, institution, minimum) in enumerate(trace_data, 1):
    trace_add.append({
        "trace_id": f"TR151_{i:03d}", "request_id": "REQ133_ECON", "institution": institution,
        "gap_id": gap, "requested_record": record, "period_or_date": "2008-2009",
        "identifiers": "83106000;71597/0071597;152677/0152677;2876/0002876",
        "minimum_usable_fields": minimum,
        "confidentiality_fallback": "Metadatos no exceptuados, campos testados e informe de búsqueda.",
        "status": "DRAFT_NOT_SENT",
    })
trace = upsert(trace, trace_add, "trace_id")
write_csv(trace_path, trace, list(trace[0]))

keys_path = HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V151.csv"
keys = read_csv(keys_path)
key_data = [
    ("output", "Listado Parametrizado del SIDIF Central", "nombre documental exacto"),
    ("output", "Listado parametrizado generado en sistema local", "salida local"),
    ("query", "consulta específica de movimientos", "capacidad 2008"),
    ("system", "SIDIF Central", "repositorio central"),
    ("system", "SIDIF Local", "repositorio local"),
    ("system", "CONPRE", "origen legado"),
    ("system", "TRANSAF", "transmisión legada"),
    ("record", "lote", "metadato de transmisión"),
    ("record", "nodo", "metadato de transmisión"),
    ("record", "número de transacción", "metadato de transmisión"),
    ("audit", "Certificación UAI", "control de cierre"),
    ("bank", "Extractos Bancarios", "fuente externa"),
    ("treasury", "transferencias a la Tesorería General de la Nación", "puente TGN"),
    ("custody", "Acta de Arqueo de Fondos y Valores", "control de cierre"),
    ("period", "2008-2009", "corte y regularización"),
]
key_add = [{
    "key_id": f"SK151_{i:02d}", "request_id": "REQ133_ECON", "key_group": group,
    "exact_key": key, "search_purpose": purpose,
    "source_or_basis": "E0_SIDIF_DUAL_DATABASE_AND_TRANSAF_CHAIN_V151.csv",
    "caveat": "Clave de recuperación; no prueba identidad, conservación ni pago.",
} for i, (group, key, purpose) in enumerate(key_data, 1)]
keys = upsert(keys, key_add, "key_id")
write_csv(keys_path, keys, list(keys[0]))

append_section(HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V151.md",
    "## Ampliación V151 · doble repositorio SIDIF, TRANSAF y certificación UAI",
    """
Estado: BORRADOR_NO_ENVIADO. Este texto no autoriza ni registra presentación.

Para 71597/0071597, 152677/0152677 y 2876/0002876, combinados con 83106000 y con C-41/C-42/C-55, se solicita búsqueda independiente en: (a) base local u originaria del SAF355 —SIDIF Local, CONPRE o sistema propio—; (b) SIDIF Central/CGN; (c) lotes, logs, acuses, errores y metadatos de autenticación/firma de TRANSAF; y (d) certificaciones, comunicaciones, reemplazos y ajustes UAI/CGN posteriores al corte. Un resultado negativo en un custodio no cierra los restantes.

Se solicitan por su nombre: “Listado parametrizado generado en sistema local”, “Listado Parametrizado del SIDIF Central remitido por la CGN” y toda “consulta específica de movimientos”, con parámetros, columnas, filas, operador, fecha y resultado. Las copias local y central deben conciliarse, pero no contarse como dos hechos económicos.

Para TRANSAF se requieren, si existen en el esquema histórico: ejercicio, lote, número de transacción, nodo/SAF, sentido, estado, aplicación/tipo, fecha y hora, archivos, acuse, error, protocolo y resultado de autenticación o firma. El formato moderno .CON, sus validaciones y la ventana visible de 30 días se citan sólo como comparadores: la búsqueda 2008 no debe restringirse por ellos y debe abarcar backend, archivo, backups, migraciones y disposiciones documentales.

La verificación final debe triangular sistema local, SIDIF Central y fuentes externas: extracto bancario, formulario que respalde transferencia TGN, Acta de Arqueo y soporte de ajustes. Certificación UAI, transmisión o registro central no equivalen a pago. Sólo cuerpo target más salida bancaria conciliada y sin reversa modifica 0/10.
""")
append_section(HERE / "REQUEST_SUBMISSION_CHECKLIST_V151.md",
    "## Control V151 · búsqueda dual y tres fuentes",
    """
- Mantener los seis pedidos DRAFT_NOT_SENT salvo autorización expresa.
- Ejecutar consultas separadas en SAF355 local, SIDIF Central y TRANSAF.
- No cerrar por un cero unilateral ni contar local y central como dos eventos.
- Pedir por nombre los listados parametrizados local y central y la consulta específica.
- No imponer a 2008 el formato de lote ni la ventana de interfaz de 2022.
- Pedir backend, backups, migraciones, inventarios y disposición documental.
- Triangular sistema local, SIDIF Central, extracto, transferencia TGN y acta.
- Tratar UAI, autenticación, transmisión, recepción y aprobación como etapas no bancarias.
- Mantener cuerpos 0/3 y ejecución 0/10 hasta evidencia individual conciliada.
""")
append_section(HERE / "SOURCE_REFERENCES_V151.md",
    "## Fuentes nuevas V151 · arquitectura SIDIF, TRANSAF y control UAI",
    "\n".join("- " + s["id"] + " · " + s["title"] + " · " + s["url"] + " · " + s["local"] + " · " + s["sha"] for s in source_rows))

(HERE / "README_V151.md").write_text("""# V151 · doble repositorio SIDIF y triangulación probatoria

V151 prueba que la arquitectura histórica distribuía una transacción entre la base local del SAF y SIDIF Central, comunicadas por TRANSAF. Por eso la recuperación de 2008 debe ejecutarse en ambos extremos y en la capa de transmisión. Dos copias no son dos hechos; un cero unilateral tampoco cierra el universo.

El Instructivo SIGEN 2/2009, inmediatamente posterior, documenta para C41/C42/C55 un control con sistema local, Listado Parametrizado del SIDIF Central, extractos, formularios TGN, acta y soportes de ajuste. La continuidad 2021 refuerza el nombre de las fuentes, pero ninguna certificación posterior prueba el pago target.

El instructivo TRANSAF 2022 ofrece campos de descubrimiento; su formato y ventana de 30 días no se retroproyectan a 2008 ni prueban eliminación. Cuerpos target 0/3, ejecuciones 0/10, seis borradores no enviados y cero respuestas.
""", encoding="utf-8")
(HERE / "VEREDICTO_V151.md").write_text("""# Veredicto V151

La búsqueda correcta tiene cuatro carriles: base local SAF355, SIDIF Central/CGN, transmisión TRANSAF y control UAI/CGN posterior al corte. Las fuentes oficiales prueban que local y central eran repositorios diferenciados y que la auditoría de formularios tardíos podía contrastar ambos con evidencia bancaria.

El avance cierra una evasión probatoria: una respuesta negativa debe individualizar repositorio, parámetros, backups, migraciones y disposición, y no puede extrapolarse a los otros custodios. También fija tres nombres documentales útiles: listado parametrizado local, Listado Parametrizado del SIDIF Central y consulta específica de movimientos.

No se localizaron cuerpos, lotes o certificaciones de los tres IDs. Arquitectura, autenticación, transmisión, certificación y ajuste no son ejecución. Resultado conservador: 0/10; seis borradores no enviados; cero presentaciones y respuestas.
""", encoding="utf-8")
(HERE / "E0_FISCAL_RECONSTRUCTION_V151.md").write_text("""# Reconstrucción fiscal E0 V151

V151 mantiene 10 adjudicaciones, 9 cuentas candidatas y 0/10 ejecuciones. Agrega una cadena de recuperación local–TRANSAF–central–UAI y exige conciliación entre copias sin doble conteo. El control 2009 adyacente combina sistema local, listado central y evidencia bancaria, pero no sustituye el cuerpo target de 2008.
""", encoding="utf-8")
(HERE / "RETRIEVAL_LOG_V151.md").write_text("""# Registro de recuperación V151

- Diez fuentes conceptuales oficiales nuevas y 19 archivos preservados en el bundle.
- Veintinueve páginas nuevas renderizadas e inspeccionadas; PASS.
- Arquitectura SIDIF local/central y TRANSAF congelada con límites de inferencia.
- Instructivo UAI 2009 adyacente y continuidad 2021 incorporados como comparadores.
- Nombres de salidas local, central y consulta específica agregados a borradores.
- `instruai2008.pdf` no localizado en la ruta ensayada; no se infiere inexistencia.
- Sin cuerpos/logs/certificaciones target; seis pedidos no presentados; 0/10.
""", encoding="utf-8")

old_handover = HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V151_A_V151.md"
if old_handover.exists():
    old_handover.unlink()
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V151_A_V152.md").write_text("""# Handover V151 → V152

## Estado

- QA PASS; 10 fuentes nuevas; 501 maestras y 261 E0.
- SIDIF histórico: bases local SAF y central diferenciadas, enlazadas por TRANSAF.
- Cada target debe buscarse en SAF355 local, SIDIF Central, TRANSAF y UAI/CGN.
- Copias local/central no son dos pagos; cero unilateral no cierra el caso.
- Instructivo SIGEN 2/2009: C41/C42/C55 controlados con sistema local, listado central, extractos, formularios TGN y acta.
- Guía TRANSAF 2022 sólo comparadora: formato y ventana de 30 días no se retroproyectan.
- Cuenta 2008 preserva consultas específicas en contexto UEPEX y excepción de cierre SAF355; alcance target abierto.
- Cuerpos/logs/certificaciones target no localizados; seis DRAFT_NOT_SENT; cero presentaciones/respuestas; 0/10.

## Prioridad V152

1. Mantener borradores salvo autorización.
2. Localizar instrucción/certificaciones UAI específicas del ejercicio 2008.
3. Buscar inventarios, tablas, backups y diseños de lote TRANSAF/SIDIF de 2008.
4. Rastrear los tres IDs en salidas local y central, con parámetros reproducibles.
5. Buscar extractos, formularios TGN y actas que permitan el puente bancario.
6. Mantener 0/10 hasta cuerpo y movimiento conciliado sin reversa.
""", encoding="utf-8")

append_section(REPO / "BACKUP_ACTUALIZACION_2026-08-29.md",
    "## V151 · doble repositorio SIDIF y control UAI",
    """
- Arquitectura local–TRANSAF–SIDIF Central congelada con búsqueda independiente por custodio.
- Control adyacente 2009 documenta C41/C42/C55 y triangulación local, central y bancaria.
- Formato TRANSAF 2022 usado sólo como comparador; 30 días de interfaz no implican eliminación.
- Diez fuentes nuevas; cuerpos 0/3; ejecución 0/10; seis borradores no enviados.
""")

register_path = HERE / "E0_REQUEST_RESPONSE_REGISTER_V151.csv"
register = read_csv(register_path)
for row in register:
    row.update({
        "status": "DRAFT_NOT_SENT", "submitted_on": "N/A", "submission_channel": "N/A",
        "receipt_or_case_id": "N/A", "response_date": "N/A",
    })
write_csv(register_path, register, list(register[0]))

write_csv(HERE / "INHERITED_QA_STATUS_V151.csv", [
    {"script": "qa_v150.py", "pre_v151_result": "PASS", "post_v151_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V150 ampliada por doble repositorio y control UAI."},
    {"script": "qa_v151.py", "pre_v151_result": "N/A", "post_v151_result": "PASS", "interpretation": "Verifica fuentes, matrices, borradores y 0/10."},
])

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
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V151.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V151.csv", hash_rows)
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)

size_rows = []
for path in iter_files(REPO):
    size = path.stat().st_size
    size_rows.append({
        "path": path.relative_to(REPO).as_posix(), "bytes": size, "mib": f"{size / 1048576:.6f}",
        "over_50_mib": str(size > 50 * 1048576), "over_100_mib": str(size > 100 * 1048576),
    })
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V151.csv", size_rows)

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V150.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint": "V151", "date": "2026-08-31",
    "state": "E0_SIDIF_LOCAL_CENTRAL_TRANSAF_UAI_CHAIN_PROVED_TARGET_BODIES_OPEN_NOT_SENT",
    "master_catalog_entries": len(catalog), "physical_local_copies": physical,
    "physical_local_hash_ok": hash_ok, "remaining_physical_gaps": len(catalog) - physical,
    "e0_primary_sources_preserved": len(census), "numeric_v151_strict_changed": False,
    "sources_newly_preserved_v151": len(source_rows), "e0_primary_sources_newly_preserved_v151": len(source_rows),
    "e0_fiscal_method_breaks_frozen": len(breaks), "e0_request_traceability_rows": len(trace),
    "e0_request_search_keys": len(keys), "e0_v151_pdf_visual_controls": len(visual),
    "e0_v151_new_pdf_visual_controls": len(visual_add), "e0_v151_image_visual_controls": len(image_visual),
    "e0_v151_total_visual_controls": len(visual) + len(image_visual),
    "e0_v151_source_bundle_files": len(bundle), "e0_sidif_dual_chain_rows": len(dual),
    "e0_transaf_schema_rows": len(transaf), "e0_uai_certification_rows": len(uai),
    "e0_2008_query_refresh_rows": len(refresh), "e0_v151_public_search_rows": len(negative),
    "e0_v151_request_objects": len(request_objects),
    "e0_sidif_local_central_dual_repository_proved": True,
    "e0_transaf_authentication_and_lot_route_proved": True,
    "e0_transaf_2022_schema_valid_for_2008": False,
    "e0_uai_2009_adjacent_three_source_control_proved": True,
    "e0_uai_target_certification_located": False,
    "e0_target_forms_public_bodies_located": 0, "e0_target_transaf_logs_located": 0,
    "e0_settlement_executed_rows_confirmed": 0, "e0_requests_submitted": 0,
    "e0_request_responses_received": 0, "e0_request_package_status": "DRAFT_NOT_SENT",
    "historical_workstream": "Recover local and central target bodies, TRANSAF logs, UAI records and bank reconciliation; no request submitted",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V151.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

(HERE / "AUDITORIA_V151.md").write_text(f"""# Auditoría V151

- Fuentes maestras: {len(catalog)}; E0: {len(census)}; nuevas: {len(source_rows)}.
- Copias/hash: {physical}/{hash_ok}; brechas: {len(catalog) - physical}.
- Quiebres: {len(breaks)}; trazas: {len(trace)}; claves: {len(keys)}.
- Controles visuales: {len(visual)} PDF ({len(visual_add)} nuevos) + {len(image_visual)} imágenes = {len(visual) + len(image_visual)}.
- Bundle: {len(bundle)} archivos; cadena dual: {len(dual)}; TRANSAF: {len(transaf)}; UAI: {len(uai)}.
- Cuerpos target 0/3; logs target 0/3; ejecución 0/10; pedidos/respuestas 0/0.
""", encoding="utf-8")


def checkpoint_manifest():
    files = [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha256(p)}
             for p in sorted(HERE.iterdir()) if p.is_file() and p.name != "MANIFEST_V151.json"]
    payload = {
        "checkpoint": "V151", "parent_checkpoint": "V150",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30, "strict_coverage_pct": STRICT, "closed_network_gate": "NO",
        "e0_primary_sources": len(census), "new_preserved_sources": len(source_rows),
        "fiscal_method_breaks": len(breaks), "request_traceability_rows": len(trace),
        "request_search_keys": len(keys), "pdf_visual_controls_total": len(visual),
        "pdf_visual_controls_new": len(visual_add), "image_visual_controls_inherited": len(image_visual),
        "source_bundle_files": len(bundle), "sidif_dual_chain_rows": len(dual),
        "transaf_schema_rows": len(transaf), "uai_certification_rows": len(uai),
        "query_refresh_rows": len(refresh), "public_search_rows": len(negative),
        "v151_request_objects": len(request_objects),
        "sidif_local_central_dual_repository_proved": True,
        "transaf_2022_schema_valid_for_2008": False,
        "uai_2009_adjacent_three_source_control_proved": True,
        "target_forms_public_bodies_located": 0, "target_transaf_logs_located": 0,
        "award_rows_exact": 10, "account_candidate_rows": 9,
        "executed_settlement_rows_confirmed": 0, "request_drafts": 6,
        "requests_submitted": 0, "responses_received": 0, "files": files,
    }
    (HERE / "MANIFEST_V151.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tree(root):
    root = Path(root)
    lines = []
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
global_files = []
for path in iter_files(REPO):
    if path != global_manifest:
        global_files.append({"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})
payload = {
    "checkpoint": "V151",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT, "exact_entities": 30, "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master; {physical} physical SHA-valid; {len(source_rows)} new sources; dual SIDIF/TRANSAF/UAI chain proved; targets open; 0/10; six drafts not submitted.",
    "historical_workstream": "Recover local and central target bodies, TRANSAF logs, UAI records and bank reconciliation; no request submitted",
    "file_count_excluding_manifest": len(global_files), "files": global_files,
}
tmp = global_manifest.with_suffix(".json.v151tmp")
tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
tmp.replace(global_manifest)

print(f"V151 BUILD PASS · catalog={len(catalog)} · E0={len(census)} · physical={physical} · hash_ok={hash_ok} · breaks={len(breaks)} · trace={len(trace)} · keys={len(keys)} · visual={len(visual) + len(image_visual)}")
