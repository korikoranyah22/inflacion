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
PARENT = CYCLE / "checkpoints" / "V178"
AUDIT = CYCLE / "source_audit"
SYNC = CYCLE / "inputs" / "source_sync" / "v179"
HIST_ROOT = CYCLE / "inputs" / "historical_retrieval" / "v179"
HIST = HIST_ROOT / "binaries"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"
COVERAGE = "63.440604"
NUMERATOR = "61345602.215"
ASSETS = "96697695.5"
EXCLUDED = {".git", "__pycache__", "tmp", "node_modules"}


def read_csv(path: Path | str):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path | str, rows, fields=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or (list(rows[0]) if rows else [])
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path | str):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def iter_files(root: Path):
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted((x for x in dirs if x not in EXCLUDED), key=str.casefold)
        for name in sorted(files, key=str.casefold):
            yield Path(directory) / name


def tree(root: Path):
    out = []
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted((x for x in dirs if x not in EXCLUDED), key=str.casefold)
        base = Path(directory)
        out += [(base / x).relative_to(root).as_posix() + "/" for x in dirs]
        out += [(base / x).relative_to(root).as_posix() for x in sorted(files, key=str.casefold)]
    return "\n".join(out) + "\n"


def clone_parent():
    skip = {
        "MANIFEST_V178.json", "README_V178.md", "VEREDICTO_V178.md", "AUDITORIA_V178.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V178_A_V179.md", "V178_SOURCE_BUNDLE.csv",
        "V178_PUBLIC_SEARCH_LOG.csv", "V178_PDF_VISUAL_CONTROL.csv", "V178_HTML_CONTENT_CONTROL.csv",
    }
    for src in sorted(PARENT.iterdir(), key=lambda p: p.name.casefold()):
        if not src.is_file() or src.name in skip or src.name.startswith(("build_", "qa_")):
            continue
        dst = HERE / src.name.replace("V178", "V179")
        dst.write_text(src.read_text(encoding="utf-8-sig").replace("V178", "V179"), encoding="utf-8")


FILES = {
    "pdf": HIST / "bo_resolucion_967_2006_anexo_contrato_fideicomiso.pdf",
    "notice": HIST / "bo_resolucion_967_2006_detalle_aviso_9095705.html",
    "protocol": HIST / "bo_download_pdf_protocol_2026.js",
    "d1118": HIST / "decreto_1118_2003_programa_fideicomisos.html",
    "r347": HIST / "resolucion_347_2004_modelo_fideicomiso.html",
    "r389": HIST / "resolucion_389_2005_modificacion_fideicomiso.html",
}

EXPECTED = {
    FILES["pdf"]: (6811172, "0b6653618f26a044a8be5fe5e3f728d0261ca2a5b879811d36c2af5d5240c553"),
    FILES["notice"]: (148915, "36635db71532430f9e83b730abcc7317275e534e933f0356fe19e5972c6695a2"),
    FILES["protocol"]: (6658, "17068e5f131abc3ebabdff01f7c0b169e0b4b32b3dad6e839b2e3c429469655c"),
    FILES["d1118"]: (44366, "9ebedba84f47a642575dd5aefeef9add532ed59f39713ef1452103ae8ec216e9"),
    FILES["r347"]: (39792, "aa764a54b6e82fd70cdf45e8959ebde3386f993aba6f8bd8816d77e98c4d87fa"),
    FILES["r389"]: (40686, "9e9ab494ceaa40f3a92f207fb8fbdd7d9bc062ffb76860b70a57511bbf7cde34"),
}


HERE.mkdir(parents=True, exist_ok=True)
clone_parent()
for path, (size, digest) in EXPECTED.items():
    assert path.is_file() and path.stat().st_size == size and sha(path) == digest


source_specs = [
    {
        "id": "e0_bo_res967_2006_full_annex_contract_v179", "institution": "Boletín Oficial de la República Argentina",
        "title": "Resolución 967/2006 · anexo completo del modelo de Contrato de Fideicomiso MyPES II(a)",
        "url": "https://www.boletinoficial.gob.ar/detalleAviso/primera/9095705/20061211?busqueda=1&anexos=1",
        "path": FILES["pdf"], "publication": "2006-12-11", "code": "Aviso 9095705 · Anexo 1 · idAnexo 00345809",
        "period": "1999-2006", "type": "PDF oficial escaneado preservado · 99 páginas · control visual integral",
        "note": "Recupera el modelo contractual aprobado y sus Anexos I-V: contrato base, crédito, desembolso, garantía e indemnidad, auditores y pagaré. La Resolución menciona 74 hojas; el objeto digital contiene 99 páginas. No equivale a contraparte ejecutada ni prueba cumplimiento.",
    },
    {
        "id": "e0_bo_res967_2006_notice_endpoint_v179", "institution": "Boletín Oficial de la República Argentina",
        "title": "Detalle oficial del aviso 9095705 y localizador del Anexo 00345809",
        "url": "https://www.boletinoficial.gob.ar/detalleAviso/primera/9095705/20061211?busqueda=1&anexos=1",
        "path": FILES["notice"], "publication": "2006-12-11", "code": "Aviso 9095705 · primera sección",
        "period": "2006", "type": "HTML oficial preservado · procedencia técnica",
        "note": "Conserva aviso, fecha, identificador interno del anexo y llamada oficial de descarga. Es prueba de procedencia, no del cumplimiento contractual.",
    },
    {
        "id": "e0_bo_download_annex_protocol_v179", "institution": "Boletín Oficial de la República Argentina",
        "title": "Protocolo público de descarga de anexos del Boletín Oficial",
        "url": "https://www.boletinoficial.gob.ar/js/downloadPdf.js", "path": FILES["protocol"],
        "publication": "2026-09-01", "code": "downloadPdf.js · descargarPDFAnexo", "period": "consulta 2026",
        "type": "JavaScript oficial preservado · procedencia técnica",
        "note": "Documenta el POST /pdf/download_anexo y los parámetros seccion, nroAnexo, idAnexo y fechaPublicacion usados para recuperar el PDF oficial.",
    },
    {
        "id": "e0_norm_decree1118_2003_mypesii_trust_v179", "institution": "Poder Ejecutivo Nacional",
        "title": "Decreto 1118/2003 · Programa de Fideicomisos BID 1192/OC-AR",
        "url": "https://www.argentina.gob.ar/normativa/nacional/decreto-1118-2003-84963/texto", "path": FILES["d1118"],
        "publication": "2003-05-12", "code": "Decreto 1118/2003", "period": "1999-2003",
        "type": "HTML oficial preservado · texto normativo completo",
        "note": "Prueba dos fideicomisos, integración con desembolsos y recuperos BID 643/867/1192, modelo de 9 capítulos y 28 cláusulas y control/supervisión del BCRA.",
    },
    {
        "id": "e0_norm_res347_2004_mypesii_two_ifis_v179", "institution": "Ministerio de Economía y Producción",
        "title": "Resolución 347/2004 · modelo MyPES II(a) con dos IFI",
        "url": "https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-347-2004-95029/texto", "path": FILES["r347"],
        "publication": "2004-05-12", "code": "Resolución 347/2004", "period": "2003-2004",
        "type": "HTML oficial preservado · texto normativo completo",
        "note": "Prueba el cambio del modelo para permitir dos entidades financieras intermedias. El texto normalizado se publica sin anexo.",
    },
    {
        "id": "e0_norm_res389_2005_mypesii_paripassu_v179", "institution": "Ministerio de Economía y Producción",
        "title": "Resolución 389/2005 · pari passu y comisión de compromiso MyPES II(a)",
        "url": "https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-389-2005-107695/texto", "path": FILES["r389"],
        "publication": "2005-07-07", "code": "Resolución 389/2005", "period": "2004-2005",
        "type": "HTML oficial preservado · texto normativo completo",
        "note": "Prueba la suscripción del 26/05/2004, modificaciones al pari passu y una comisión de compromiso a cargo de las IFI; aprobó un modelo de 89 hojas.",
    },
]

sources = []
for spec in source_specs:
    sources.append({
        "id": spec["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": spec["institution"],
        "titulo": spec["title"], "url_original": spec["url"],
        "archivo_local": "/" + spec["path"].relative_to(REPO).as_posix(),
        "fecha_descarga": "2026-09-01", "fecha_publicacion": spec["publication"],
        "codigo_serie": spec["code"], "periodo_utilizado": spec["period"], "tipo": spec["type"],
        "sha256": EXPECTED[spec["path"]][1], "nota": spec["note"],
    })

catalog = read_csv(CATALOG)
catalog_fields = list(catalog[0])
by_id = {row["id"]: row for row in catalog}
if "e0_norm_res967_2006_mypesii_trust_v178" in by_id:
    by_id["e0_norm_res967_2006_mypesii_trust_v178"]["nota"] = "Prueba modificación del préstamo, suscripción estatal de 2004 y participación de Credicoop, Macro y Nuevo Banco Suquía. El texto normalizado no incorpora el anexo; V179 recupera el objeto oficial desde el detalle del Boletín Oficial."
for source in sources:
    by_id[source["id"]] = source
catalog = list(by_id.values())
write_csv(CATALOG, catalog, catalog_fields)
assert len(catalog) == len({row["id"] for row in catalog}) == 649

audit = []
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    actual = sha(path) if path.is_file() else ""
    audit.append({"id": row["id"], "archivo_local": row["archivo_local"], "exists": str(path.is_file()), "sha_catalog": row["sha256"].lower(), "sha_actual": actual, "hash_ok": str(path.is_file() and bool(row["sha256"]) and actual == row["sha256"].lower())})
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V179.csv", audit)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V179.csv", audit)
missing = [row for row in audit if row["hash_ok"] != "True"]
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V179.csv", missing, list(audit[0]))
assert not missing


write_csv(HERE / "E0_BID1192_RES967_DIGITAL_PACKAGE_STRUCTURE_V179.csv", [
    {"row_id": "DS179_01", "component": "Contrato de Fideicomiso", "pdf_pages": "1-53", "digital_pages": "53", "content": "9 capítulos; 28 cláusulas; partes, patrimonio, administración, control, pagos y extinción", "evidence_state": "FULL_APPROVED_MODEL_RECOVERED"},
    {"row_id": "DS179_02", "component": "Anexo I · Reglamento de Crédito", "pdf_pages": "54-61", "digital_pages": "8", "content": "financiamiento, elegibilidad, tasas, límites, documentación y control", "evidence_state": "FULL_APPROVED_MODEL_RECOVERED"},
    {"row_id": "DS179_03", "component": "Anexo II · Reglamento de Desembolso", "pdf_pages": "62-74", "digital_pages": "13", "content": "condiciones previas, solicitudes, cuentas, certificación, garantías y desembolso", "evidence_state": "FULL_APPROVED_MODEL_RECOVERED"},
    {"row_id": "DS179_04", "component": "Anexo III · Garantía Bancaria e Indemnidad", "pdf_pages": "75-97", "digital_pages": "23", "content": "garantía solidaria, aportes por insuficiencia, débito automático, intereses, renuncias y acciones", "evidence_state": "FULL_APPROVED_MODEL_RECOVERED"},
    {"row_id": "DS179_05", "component": "Anexo IV · Auditores Externos", "pdf_pages": "98", "digital_pages": "1", "content": "lista de siete firmas de auditoría", "evidence_state": "FULL_APPROVED_MODEL_RECOVERED"},
    {"row_id": "DS179_06", "component": "Anexo V · Modelo de Pagaré", "pdf_pages": "99", "digital_pages": "1", "content": "interés compensatorio y punitorio equivalente al 50% del compensatorio", "evidence_state": "FULL_APPROVED_MODEL_RECOVERED"},
])

write_csv(HERE / "E0_BID1192_2006_ROLE_RESPONSIBILITY_MATRIX_V179.csv", [
    {"row_id": "RR179_01", "actor": "Estado Nacional / Ministerio", "role": "Fiduciante-Beneficiario y fideicomisario", "proved_duty_or_right": "aporta recursos, es beneficiario, imparte controles e instrucciones por las vías contractuales", "source": "Contrato, cláusulas 3, 19-20", "limit": "modelo aprobado; ejecución pendiente"},
    {"row_id": "RR179_02", "actor": "SSEPYMEYDR/UCP", "role": "Organismo Ejecutor", "proved_duty_or_right": "evalúa sostenibilidad, controla administración/destino, supervisa, puede suspender desembolsos e instruir sanciones", "source": "Contrato, cláusulas 19-20", "limit": "faltan expedientes de control"},
    {"row_id": "RR179_03", "actor": "SUD Inversiones y Análisis S.A.", "role": "Fiduciario", "proved_duty_or_right": "administra patrimonio separado, adquiere créditos, lleva contabilidad/registros, conserva documentación, cobra, ejecuta y rinde cuentas", "source": "Contrato, cláusulas 10-16", "limit": "faltan reportes y contraparte ejecutada"},
    {"row_id": "RR179_04", "actor": "SUD / delegados", "role": "Fiduciario y administradores delegados", "proved_duty_or_right": "puede delegar administración de créditos sin desprenderse de la responsabilidad contractual por actos u omisiones de delegados", "source": "Contrato, cláusula 14", "limit": "alcance exacto sujeto al instrumento ejecutado"},
    {"row_id": "RR179_05", "actor": "BCRA", "role": "Agente financiero y órgano de control/fiscalización", "proved_duty_or_right": "controla la gestión fiduciaria y recibe información periódica y archivos mensuales de deudores", "source": "Decreto 1118 art. 6; Contrato cláusulas 16 y 18", "limit": "faltan informes producidos"},
    {"row_id": "RR179_06", "actor": "Banco Credicoop", "role": "IFI, originante/administrador y garante", "proved_duty_or_right": "aporta contraparte, origina créditos, cede créditos/garantías y responde por los que genera", "source": "Contrato cláusula 3; Anexos I-III", "limit": "modelo no prueba cartera ni pagos concretos"},
    {"row_id": "RR179_07", "actor": "Banco Macro-Bansud", "role": "IFI, originante/administrador, garante y designante de SUD", "proved_duty_or_right": "mismas obligaciones IFI y garantía específica por obligaciones de SUD y sus dependientes", "source": "Anexo III, cláusulas 3-6", "limit": "modelo no prueba activación de garantía"},
    {"row_id": "RR179_08", "actor": "Credicoop y Macro", "role": "garantes solidarios/coobligados", "proved_duty_or_right": "garantizan obligaciones definidas, aportan ante insuficiencia y autorizan débitos automáticos", "source": "Anexo III, cláusulas 3-9", "limit": "faltan saldos, avisos, débitos y ejecuciones"},
    {"row_id": "RR179_09", "actor": "Subprestatarios MiPyME", "role": "deudores finales elegibles", "proved_duty_or_right": "reciben crédito sujeto a elegibilidad, documentación, garantías, destino y límites", "source": "Anexo I", "limit": "datos personales y legajos no localizados"},
    {"row_id": "RR179_10", "actor": "Auditor externo", "role": "control independiente", "proved_duty_or_right": "audita y emite informes especiales periódicos", "source": "Contrato cláusulas 16.4 y 16.8; Anexo IV", "limit": "informes no localizados"},
])

write_csv(HERE / "E0_BID1192_IFI_GUARANTEE_INDEMNITY_MATRIX_V179.csv", [
    {"row_id": "GI179_01", "mechanism": "garantía solidaria", "obligor": "Credicoop y Macro", "scope": "obligaciones garantizadas del fiduciario/fideicomiso según el contrato", "trigger_or_term": "incumplimiento; carácter de principales pagadores", "source": "Anexo III, cláusula 3", "proof_limit": "término aprobado, no incumplimiento probado"},
    {"row_id": "GI179_02", "mechanism": "garantía por cartera propia", "obligor": "cada IFI", "scope": "créditos originados o adquiridos por esa IFI", "trigger_or_term": "obligaciones ligadas a cada crédito", "source": "Anexo III, cláusula 4", "proof_limit": "falta padrón de créditos"},
    {"row_id": "GI179_03", "mechanism": "garantía de obligaciones generales", "obligor": "IFI conforme distribución contractual", "scope": "costos, pagarés, transferencia, comisión de compromiso y demás conceptos definidos", "trigger_or_term": "exigibilidad contractual", "source": "Anexo III, cláusula 4", "proof_limit": "falta ledger de conceptos"},
    {"row_id": "GI179_04", "mechanism": "garantía del fiduciario designado", "obligor": "Macro-Bansud", "scope": "obligaciones de SUD, sus empleados y agentes", "trigger_or_term": "incumplimiento atribuible al fiduciario", "source": "Anexo III, cláusulas 4 y 6", "proof_limit": "no se acredita incumplimiento"},
    {"row_id": "GI179_05", "mechanism": "aporte por insuficiencia patrimonial", "obligor": "IFI pertinente", "scope": "fondos necesarios y suficientes para cubrir obligaciones garantizadas", "trigger_or_term": "insuficiencia del patrimonio; aviso de 48 horas", "source": "Anexo III, cláusula 5", "proof_limit": "faltan avisos y movimientos"},
    {"row_id": "GI179_06", "mechanism": "supervivencia", "obligor": "IFI", "scope": "garantía no extinguida por remoción/cese del fiduciario ni terminación hasta pago total", "trigger_or_term": "vigencia hasta satisfacción completa", "source": "Anexo III, cláusulas 6-7", "proof_limit": "falta fecha de extinción efectiva"},
    {"row_id": "GI179_07", "mechanism": "débito automático irrevocable", "obligor": "Credicoop y Macro", "scope": "cuentas en BCRA u otras entidades para obligaciones garantizadas", "trigger_or_term": "aviso; plazos de 5 o 15 días hábiles según concepto", "source": "Anexo III, cláusula 8", "proof_limit": "no prueba que se debitó"},
    {"row_id": "GI179_08", "mechanism": "mora automática e intereses", "obligor": "IFI incumplidora", "scope": "compensatorio más punitorio equivalente al 50% del compensatorio, con reglas de capitalización", "trigger_or_term": "vencimiento por mero transcurso del tiempo", "source": "Anexo III, cláusula 9", "proof_limit": "no cuantificado"},
    {"row_id": "GI179_09", "mechanism": "renuncia a defensas", "obligor": "IFI", "scope": "defensas y recursos enumerados en el instrumento", "trigger_or_term": "acción de cobro", "source": "Anexo III, cláusula 12", "proof_limit": "aplicación judicial no examinada"},
    {"row_id": "GI179_10", "mechanism": "acción directa", "obligor": "IFI", "scope": "Fiduciante puede accionar directamente por obligaciones que el fiduciario debía perseguir", "trigger_or_term": "incumplimiento garantizado", "source": "Anexo III, cláusula 19", "proof_limit": "no prueba acción ejercida"},
    {"row_id": "GI179_11", "mechanism": "subordinación", "obligor": "IFI", "scope": "derechos de IFI subordinados a satisfacción previa del Fiduciante", "trigger_or_term": "distribución de patrimonio/remanente", "source": "Anexo III, cláusula 20", "proof_limit": "falta liquidación"},
])

write_csv(HERE / "E0_BID1192_CONTRACTUAL_REPORTING_DATA_INVENTORY_V179.csv", [
    {"row_id": "DR179_01", "record": "rendición trimestral", "producer": "Fiduciario", "recipient": "Fiduciante/BCRA/UCP según circuito", "minimum_fields": "estado patrimonial; movimientos; cuentas; conciliación; firma", "source": "Contrato cláusula 16", "evidentiary_use": "reconstruir patrimonio y desempeño"},
    {"row_id": "DR179_02", "record": "detalle de operaciones de crédito", "producer": "Fiduciario/IFI administradora", "recipient": "control contractual", "minimum_fields": "cantidad; monto; tasa; financiamiento; IFI; crédito", "source": "Contrato cláusula 16", "evidentiary_use": "padrón y tasa efectivamente aplicada"},
    {"row_id": "DR179_03", "record": "cartera en mora y previsiones", "producer": "Fiduciario/IFI", "recipient": "control contractual", "minimum_fields": "crédito; días de mora; saldo; previsión; garantía; gestión", "source": "Contrato cláusula 16", "evidentiary_use": "riesgo, pérdidas y activación de garantías"},
    {"row_id": "DR179_04", "record": "gastos, cobranzas y acciones judiciales", "producer": "Fiduciario", "recipient": "Fiduciante/BCRA", "minimum_fields": "fecha; concepto; importe; crédito; acción; resultado", "source": "Contrato cláusula 16", "evidentiary_use": "costos, recuperos y enforcement"},
    {"row_id": "DR179_05", "record": "sistema de gestión y registros", "producer": "Fiduciario", "recipient": "auditor/control", "minimum_fields": "sistema; claves; altas; modificaciones; trazabilidad; respaldo", "source": "Contrato cláusulas 11 y 16", "evidentiary_use": "cadena de custodia y completitud"},
    {"row_id": "DR179_06", "record": "informes especiales trimestrales", "producer": "Auditor externo", "recipient": "partes y control", "minimum_fields": "alcance; pruebas; excepciones; saldos; opinión; firma", "source": "Contrato cláusula 16.4", "evidentiary_use": "validación independiente"},
    {"row_id": "DR179_07", "record": "archivo mensual de deudores", "producer": "Fiduciario/IFI", "recipient": "BCRA", "minimum_fields": "deudor; CUIT; situación; saldo; clasificación; fecha", "source": "Contrato cláusula 16.5", "evidentiary_use": "crosswalk con Central de Deudores"},
    {"row_id": "DR179_08", "record": "documentación original y respaldo digital", "producer": "Fiduciario/IFI", "recipient": "custodia y auditoría", "minimum_fields": "contrato; pagaré; cesión; garantía; desembolso; cobro; índice", "source": "Contrato cláusula 11", "evidentiary_use": "probar existencia y titularidad de cada crédito"},
    {"row_id": "DR179_09", "record": "cuentas bancarias del fideicomiso", "producer": "Fiduciario/BCRA/banco depositario", "recipient": "control y auditoría", "minimum_fields": "cuenta; fecha valor; débito; crédito; contraparte; saldo; instrucción", "source": "Contrato cláusula 11", "evidentiary_use": "reconciliar flujos y garantías"},
    {"row_id": "DR179_10", "record": "garantías y débitos IFI", "producer": "IFI/BCRA/Fiduciario", "recipient": "Fiduciante", "minimum_fields": "aviso; obligación; monto; plazo; cuenta; débito; moneda; resultado", "source": "Anexo III cláusulas 3-9", "evidentiary_use": "probar cumplimiento o incumplimiento material"},
])

write_csv(HERE / "E0_BID1192_2006_VS_2013_ROLE_NONTRANSPOSITION_V179.csv", [
    {"row_id": "NT179_01", "dimension": "instrumento", "mypes_2006": "fideicomiso BID 1192 con SUD y dos IFI", "fondyf_bna_2013": "convenio de administración BNA-FONDYF", "safe_conclusion": "regímenes jurídicos distintos"},
    {"row_id": "NT179_02", "dimension": "función bancaria", "mypes_2006": "IFI origina/administra créditos y aporta contraparte", "fondyf_bna_2013": "BNA administra fondos y operaciones por cuenta del FONDYF", "safe_conclusion": "no homologar funciones"},
    {"row_id": "NT179_03", "dimension": "riesgo crediticio", "mypes_2006": "IFI garantiza créditos propios y obligaciones definidas", "fondyf_bna_2013": "modelo dice que BNA no asume riesgo de crédito", "safe_conclusion": "oposición expresa"},
    {"row_id": "NT179_04", "dimension": "garantía/indemnidad", "mypes_2006": "Anexo III contiene garantía solidaria e indemnidad", "fondyf_bna_2013": "no localizada garantía equivalente en modelo público", "safe_conclusion": "no trasladar Anexo III"},
    {"row_id": "NT179_05", "dimension": "débito automático", "mypes_2006": "autorización irrevocable sobre cuentas IFI", "fondyf_bna_2013": "no localizada obligación equivalente", "safe_conclusion": "exige instrumento específico"},
    {"row_id": "NT179_06", "dimension": "remuneración", "mypes_2006": "retribución fiduciaria/spread y costos según contrato", "fondyf_bna_2013": "2% de créditos efectivamente otorgados más gastos taxativos", "safe_conclusion": "precios y bases diferentes"},
    {"row_id": "NT179_07", "dimension": "información", "mypes_2006": "régimen trimestral, auditoría y archivo mensual BCRA", "fondyf_bna_2013": "informes mensuales de operación/cobranza/mora/saldos", "safe_conclusion": "pedir ambos archivos por separado"},
    {"row_id": "NT179_08", "dimension": "transición", "mypes_2006": "patrimonio y recuperos del fideicomiso", "fondyf_bna_2013": "recuperos integrados al FONDYF por Decreto 1273/2012", "safe_conclusion": "falta crosswalk, novación, liquidación o transferencia ejecutada"},
    {"row_id": "NT179_09", "dimension": "atribución", "mypes_2006": "obligaciones aprobadas para Macro/Credicoop", "fondyf_bna_2013": "obligaciones aprobadas para BNA/Programa", "safe_conclusion": "ninguna imputación individual cruza períodos sin prueba de continuidad"},
])

write_csv(HERE / "E0_BID1192_EXECUTED_MODEL_STATUS_V179.csv", [
    {"row_id": "ES179_01", "event": "Decreto 1118/2003", "proved": "modelo originario de 9 capítulos, 28 cláusulas y seis anexos", "open": "anexo originario y contraparte ejecutada"},
    {"row_id": "ES179_02", "event": "Resolución 347/2004", "proved": "modelo modificado para dos IFI", "open": "anexo 2004"},
    {"row_id": "ES179_03", "event": "26/05/2004", "proved": "Res. 389/2005 y Res. 967/2006 afirman que el Estado suscribió el contrato", "open": "ejemplar firmado, fecha y anexos finales"},
    {"row_id": "ES179_04", "event": "Resolución 389/2005", "proved": "modelo de 89 hojas, pari passu y comisión de compromiso", "open": "anexo 2005 y addenda ejecutada"},
    {"row_id": "ES179_05", "event": "Resolución 967/2006 + BO Anexo 00345809", "proved": "modelo aprobado completo recuperado en objeto oficial de 99 páginas digitales", "open": "reconciliar 74 hojas normativas con paginación digital; contraparte ejecutada"},
    {"row_id": "ES179_06", "event": "firmas del objeto BO", "proved": "identifica representantes y contiene espacios/líneas de firma del modelo", "open": "espacios no completados: no tratar como original firmado"},
    {"row_id": "ES179_07", "event": "desempeño contractual", "proved": "define registros, controles, garantías y acciones que debían existir", "open": "reportes, carteras, avisos, débitos, pagos, auditorías y liquidación"},
])

write_csv(HERE / "V179_BO_ENDPOINT_PROVENANCE.csv", [{
    "notice_id": "9095705", "publication_date": "20061211", "section": "primera", "annex_number": "1",
    "annex_id": "00345809", "endpoint": "https://www.boletinoficial.gob.ar/pdf/download_anexo",
    "method": "POST JSON response with pdfBase64", "bytes": "6811172", "sha256": EXPECTED[FILES["pdf"]][1],
    "pdf_pages": "99", "normative_folios": "74", "provenance_result": "PASS_OFFICIAL_NOTICE_ENDPOINT_HASHED_LOCAL_COPY",
}])

write_csv(HERE / "V179_PDF_VISUAL_CONTROL.csv", [{
    "control_id": "PDF179_01", "source_id": source_specs[0]["id"], "pdf_pages": "1-99",
    "target": "contrato base y Anexos I-V completos", "method": "páginas 1,2,3,20,40,60,74,75,90,99 a alta resolución + 99 miniaturas en 11 hojas de contacto",
    "result": "PASS_ALL_99_PAGES_VISUALLY_INSPECTED", "text_layer": "NONE_SCAN", "limit": "modelo aprobado; no contraparte ejecutada ni desempeño",
}])

html_checks = [
    ("HTML179_01", source_specs[1], 'descargarPDFAnexo("primera","1", "00345809", "20061211", "/pdf/download_anexo")'),
    ("HTML179_02", source_specs[2], "function descargarPDFAnexo"),
    ("HTML179_03", source_specs[3], "El BANCO CENTRAL DE LA REPÚBLICA ARGENTINA actuará en carácter de Agente Financiero"),
    ("HTML179_04", source_specs[4], "DOS (2) Entidades Financieras"),
    ("HTML179_05", source_specs[5], "Pari-passu"),
]
for _, spec, needle in html_checks:
    assert needle.casefold() in spec["path"].read_text(encoding="utf-8").casefold()
write_csv(HERE / "V179_HTML_CONTENT_CONTROL.csv", [
    {"control_id": cid, "source_id": spec["id"], "target_string": needle, "result": "PASS_EXACT_STRING", "limit": "integridad de contenido local; no desempeño material"}
    for cid, spec, needle in html_checks
])

write_csv(HERE / "V179_SOURCE_BUNDLE.csv", [
    {"source_id": s["id"], "local_path": s["archivo_local"], "sha256": s["sha256"], "bytes": str((REPO / s["archivo_local"].lstrip("/")).stat().st_size), "url": s["url_original"], "role": "new V179 official source or technical provenance"}
    for s in sources
])

# Correct the six V178 request/search rows whose values were written with superseded field names,
# then add six new contract-performance objects. No request is sent by this build.
objects = read_csv(HERE / "E0_V179_REQUEST_OBJECTS.csv")
object_repairs = {
    "RO178_48": ("BID1192_MP0191_LEGACY_NOTE_BODIES", "BCRA · CGN/DAIF · programa", "Notas 466/1796/08 y 88/14, anexos y rutas", "2008-2014", "cuerpo; firmante; destinatario; cuenta; programa; estado; cierre; anexos; expediente", "copia certificada y constancia bancaria de estado/cierre"),
    "RO178_49": ("MYPESII_EXECUTED_TRUST_CONTRACT", "Registro Oficial · Economía · fiduciario", "contrato 26/05/2004 y modificaciones 2005-2006 ejecutadas", "2004-2006", "partes; fecha; firmas; versión; cuentas; patrimonio; IFI; riesgo; anexos", "contraparte ejecutada íntegra o negativo de custodia"),
    "RO178_50": ("FONDYF_EXECUTED_COLLABORATION_AGREEMENT", "Secretaría PyME · Hacienda · BNA · BICE", "convenio Res. 206/2012 suscripto 28/12/2012", "2012", "firmas; fecha; obligaciones; Comité; anexos; expediente; vigencia", "contraparte firmada y anexos"),
    "RO178_51": ("FONDYF_BNA_EXECUTED_ADMIN_PACKAGE", "BNA · Secretaría PyME", "convenio Res. 48/2013, cuenta, informes mensuales, legajos y facturación 2%", "2013-2019", "firma; fecha; cuenta; préstamo; CUIT; desembolso; cobro; mora; saldo; reporte; comisión; factura", "ledger y reportes conciliables con Cuentas"),
    "RO178_52": ("FONDYF_ACT398_HANDOFF_FILE", "Comité FONAPYME · Secretaría PyME", "Acta 398 del 08/08/2014 y expediente de transferencia", "2014-2016", "asistentes; decisión; inventario; cuentas; responsables; pendientes; entrega; recepción", "acta y traspaso con inventario"),
    "RO178_53": ("BID1192_CUADRO13_TOTAL_RECONCILIATION", "CGN · UAI · SAF362 · programa", "Cuadros 13.2/13.3, mayores, conciliaciones y estados", "2015-2016", "cuenta; apertura; debe; haber; cierre; alcance; ajuste; total; certificante; respaldo", "reconciliar gaps 7171347.97, 8750817.97 y 1579470.00"),
}
for row in objects:
    if row["row_id"] in object_repairs:
        vals = object_repairs[row["row_id"]]
        row.update({"object_id": vals[0], "custodian": vals[1], "exact_record": vals[2], "period": vals[3], "minimum_fields": vals[4], "closure_rule": vals[5], "status": "DRAFT_NOT_SENT"})
objects += [
    {"row_id": "RO179_54", "object_id": "MYPESII_2006_EXECUTED_COUNTERPART", "custodian": "Economía · Registro Oficial · SUD/Macro sucesores", "exact_record": "contraparte ejecutada del modelo Res. 967/2006 y cadena de versiones", "period": "2004-2007", "minimum_fields": "fecha; firmas; personería; versión; anexos; altas/bajas IFI; vigencia; expediente", "closure_rule": "copia íntegra firmada y certificada o negativo fundado por archivo", "status": "DRAFT_NOT_SENT"},
    {"row_id": "RO179_55", "object_id": "MYPESII_CLAUSE16_REPORTING_ARCHIVE", "custodian": "SUD/Macro · Credicoop · BCRA · UCP", "exact_record": "rendiciones, reportes trimestrales, archivos mensuales de deudores y auditorías", "period": "2004-extinción", "minimum_fields": "período; crédito; IFI; tasa; mora; previsión; gasto; cobro; juicio; saldo; firma; auditor", "closure_rule": "serie completa, inventario de faltantes y conciliación", "status": "DRAFT_NOT_SENT"},
    {"row_id": "RO179_56", "object_id": "MYPESII_IFI_GUARANTEE_EXECUTION", "custodian": "BCRA · SUD/Macro · Credicoop · Economía", "exact_record": "garantías, avisos de insuficiencia, aportes, débitos y acciones del Anexo III", "period": "2004-extinción", "minimum_fields": "obligación; IFI; fecha; aviso; monto; cuenta; débito; moneda; interés; resultado; soporte", "closure_rule": "ledger de cada garantía activada/no activada y respaldo bancario", "status": "DRAFT_NOT_SENT"},
    {"row_id": "RO179_57", "object_id": "MYPESII_CREDIT_COLLATERAL_LEDGER", "custodian": "SUD/Macro · Credicoop · BCRA/UCP", "exact_record": "padrón de créditos, cesiones, pagarés, garantías y contraparte local", "period": "2004-extinción", "minimum_fields": "crédito; CUIT testado; IFI; principal; tasa; fecha; cesión; garantía; desembolso; cobro; saldo", "closure_rule": "padrón conciliado con cuentas y reportes, con datos personales testados", "status": "DRAFT_NOT_SENT"},
    {"row_id": "RO179_58", "object_id": "MYPESII_FIDUCIARY_ACCOUNTS_AND_FEES", "custodian": "SUD/Macro · BCRA · Economía", "exact_record": "extractos de cuentas fiduciarias, instrucciones, retribución, gastos e impuestos", "period": "2004-extinción", "minimum_fields": "cuenta; fecha valor; débito; crédito; contraparte; concepto; comisión; gasto; impuesto; saldo", "closure_rule": "conciliación bancaria-contable completa", "status": "DRAFT_NOT_SENT"},
    {"row_id": "RO179_59", "object_id": "MYPESII_TO_FONDYF_TRANSITION", "custodian": "Economía · BCRA · BNA · BICE · fiduciario", "exact_record": "liquidación, cesión, novación o transferencia del fideicomiso 2006 al FONDYF/BNA", "period": "2011-2014", "minimum_fields": "instrumento; fecha; patrimonio; cuentas; cartera; garantías; saldo; entrega; recepción; responsables", "closure_rule": "crosswalk firmado de activos, pasivos, derechos y obligaciones", "status": "DRAFT_NOT_SENT"},
]
write_csv(HERE / "E0_V179_REQUEST_OBJECTS.csv", objects)
write_csv(HERE / "E0_V179_REQUEST_OBJECTS_V179.csv", objects)
assert all(row["status"] == "DRAFT_NOT_SENT" for row in objects)

keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V179.csv")
key_repairs = {
    "SK178_50": ("REQ133_ECON/BCRA", "legacy_notes", "466/1796/08; Nota 88/14; MP0191", "cerrar atribución y estado de MP0191", "Cuentas 2011-2013", "cita no sustituye cuerpo"),
    "SK178_51": ("DNR/BO/REQ133_ECON", "contract", "Resolución 967/2006; idAnexo 00345809; contrato 26/05/2004", "recuperar contraparte ejecutada", "modelo BO recuperado", "modelo no es original firmado"),
    "SK178_52": ("BNA/Secretaría PyME/Hacienda/BICE", "agreement", "Resolución 206/2012; convenio 28/12/2012", "recuperar convenio firmado", "Res. 4/2016", "recital no reemplaza ejemplar"),
    "SK178_53": ("BNA/Secretaría PyME", "admin_reports", "Resolución 48/2013; informes mensuales; comisión 2%", "recuperar ejecución y reportes", "Res. 48/2013", "datos personales pueden testarse"),
    "SK178_54": ("Secretaría PyME/Comité", "handoff", "Acta 398 08/08/2014; Resolución 1417/2014", "cerrar transferencia", "Res. 4/2016", "estructura no prueba cumplimiento"),
    "SK178_55": ("CGN/UAI/SAF362", "crosswalk", "482435943.60; 489607291.57; 676322549.15; 685073367.12", "reconciliar Cuadro 13.3", "Cuentas/SIGEN", "gap no equivale a daño"),
}
for row in keys:
    if row["key_id"] in key_repairs:
        vals = key_repairs[row["key_id"]]
        row.update({"request_id": vals[0], "key_group": vals[1], "exact_key": vals[2], "search_purpose": vals[3], "source_or_basis": vals[4], "caveat": vals[5]})
keys += [
    {"key_id": "SK179_56", "request_id": "REQ179_ECON_BO", "key_group": "executed_contract", "exact_key": "S01:0076739/2005; Resolución 967/2006; 00345809; contrato 26/05/2004", "search_purpose": "contraparte firmada y versiones", "source_or_basis": "BO anexo completo", "caveat": "modelo aprobado no prueba firma"},
    {"key_id": "SK179_57", "request_id": "REQ179_BCRA", "key_group": "clause16_reports", "exact_key": "rendición trimestral; Deudores del Sistema Financiero; Estado de Situación de Deudores", "search_purpose": "serie de reportes y cartera", "source_or_basis": "Contrato cláusula 16", "caveat": "admitir testado de datos personales"},
    {"key_id": "SK179_58", "request_id": "REQ179_IFI", "key_group": "guarantee", "exact_key": "Anexo III; garantía bancaria; indemnidad; débito automático; insuficiencia 48 horas", "search_purpose": "ejecución de garantías", "source_or_basis": "Anexo III cláusulas 3-9", "caveat": "cláusula no prueba activación"},
    {"key_id": "SK179_59", "request_id": "REQ179_IFI", "key_group": "credit_ledger", "exact_key": "cesión en garantía; pagarés; contraparte IFI; cartera MyPES II(a)", "search_purpose": "padrón conciliable", "source_or_basis": "Contrato y Anexos I-II", "caveat": "testar CUIT/nombres cuando corresponda"},
    {"key_id": "SK179_60", "request_id": "REQ179_ECON_BCRA", "key_group": "fiduciary_accounts", "exact_key": "cuentas fideicomiso; retribución fiduciaria; comisión compromiso; extractos", "search_purpose": "reconstruir flujos y costos", "source_or_basis": "Contrato cláusulas 10-16", "caveat": "no inferir ganancia sin ledger"},
    {"key_id": "SK179_61", "request_id": "REQ179_TRANSITION", "key_group": "novation_transfer", "exact_key": "Decreto 1273/2012; FONDYF; liquidación MyPES II(a); cesión; novación; BNA", "search_purpose": "separar obligaciones 2006 y 2013", "source_or_basis": "cadena normativa V178/V179", "caveat": "prohibida la transposición sin instrumento"},
]
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V179.csv", keys)

trace = read_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V179.csv")
trace += [
    {"trace_id": "TR179_01", "request_id": "REQ179_ECON_BO", "institution": "Economía/Registro Oficial", "gap_id": "CL179_EXECUTED_CONTRACT", "requested_record": "contraparte ejecutada Res. 967/2006", "period_or_date": "2004-2007", "identifiers": "9095705;00345809;S01:0076739/2005", "minimum_usable_fields": "fecha;firmas;versión;anexos;vigencia", "confidentiality_fallback": "índice y metadatos certificados", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR179_02", "request_id": "REQ179_BCRA", "institution": "BCRA", "gap_id": "CL179_REPORTS", "requested_record": "informes y archivos cláusula 16", "period_or_date": "2004-extinción", "identifiers": "BID1192;MyPES II(a);SUD;Macro;Credicoop", "minimum_usable_fields": "período;cuenta;crédito;tasa;mora;saldo;firma", "confidentiality_fallback": "agregados más diccionario y hashes", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR179_03", "request_id": "REQ179_IFI", "institution": "Macro/Credicoop/sucesores", "gap_id": "CL179_GUARANTEE", "requested_record": "garantías, avisos, aportes y débitos", "period_or_date": "2004-extinción", "identifiers": "Anexo III cláusulas 3-9", "minimum_usable_fields": "obligación;fecha;monto;cuenta;resultado", "confidentiality_fallback": "registro agregado con soporte testado", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR179_04", "request_id": "REQ179_IFI", "institution": "Fiduciario/IFI/UCP", "gap_id": "CL179_CREDIT_LEDGER", "requested_record": "padrón de créditos y garantías", "period_or_date": "2004-extinción", "identifiers": "MyPES II(a);BID1192", "minimum_usable_fields": "id;IFI;fecha;principal;tasa;saldo;garantía", "confidentiality_fallback": "seudonimización estable", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR179_05", "request_id": "REQ179_ECON_BCRA", "institution": "Economía/BCRA/Fiduciario", "gap_id": "CL179_ACCOUNTS", "requested_record": "extractos, retribuciones, gastos e impuestos", "period_or_date": "2004-extinción", "identifiers": "cuentas fiduciarias;comisión compromiso", "minimum_usable_fields": "fecha valor;concepto;importe;saldo;contraparte", "confidentiality_fallback": "mayor contable y totales por período", "status": "DRAFT_NOT_SENT"},
    {"trace_id": "TR179_06", "request_id": "REQ179_TRANSITION", "institution": "Economía/BCRA/BNA/BICE", "gap_id": "CL179_TRANSITION", "requested_record": "liquidación/cesión/novación hacia FONDYF", "period_or_date": "2011-2014", "identifiers": "Decreto 1273/2012;Res.206/2012;Res.48/2013", "minimum_usable_fields": "instrumento;fecha;inventario;saldo;entrega;recepción", "confidentiality_fallback": "acta e inventario agregado", "status": "DRAFT_NOT_SENT"},
]
write_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V179.csv", trace)

(HERE / "E0_REQUEST_PACKAGE_V179.md").write_text("""# Paquete de pedidos V179 · BORRADOR_NO_ENVIADO

No fue remitido. El anexo oficial recuperado permite pedir objetos ya definidos por el propio contrato: contraparte ejecutada y cadena de versiones; rendiciones e informes de la cláusula 16; archivos mensuales de deudores; informes de auditor externo; padrón de créditos, cesiones, pagarés y garantías; avisos, aportes y débitos del Anexo III; extractos, retribuciones y gastos fiduciarios; e instrumento de liquidación/novación/transferencia hacia FONDYF/BNA. Toda respuesta debe conservar identificadores, diccionario, período, responsable y conciliación; los datos personales pueden testarse o seudonimizarse sin suprimir totales y trazabilidad.
""", encoding="utf-8")

write_csv(HERE / "V179_PUBLIC_SEARCH_LOG.csv", [
    {"query_id": "PS179_01", "query": "Boletín Oficial búsqueda avanzada Resolución 967/2006", "result": "aviso 9095705 localizado", "artifact": "detalle oficial preservado", "limit": "búsqueda pública no prueba ejecución"},
    {"query_id": "PS179_02", "query": "anexos=1 aviso 9095705", "result": "idAnexo 00345809 y fecha 20061211", "artifact": "HTML oficial", "limit": "identificador técnico"},
    {"query_id": "PS179_03", "query": "downloadPdf.js descargarPDFAnexo", "result": "POST /pdf/download_anexo y parámetros localizados", "artifact": "JS oficial preservado", "limit": "protocolo de recuperación"},
    {"query_id": "PS179_04", "query": "POST primera/1/00345809/20061211", "result": "PDF oficial 6811172 bytes, SHA-256 validado, 99 páginas", "artifact": "anexo completo preservado", "limit": "modelo aprobado, no contraparte firmada"},
    {"query_id": "PS179_05", "query": "Decreto 1118/2003", "result": "dos fideicomisos, recursos y control BCRA", "artifact": "HTML oficial preservado", "limit": "anexo originario no recuperado"},
    {"query_id": "PS179_06", "query": "Resoluciones 347/2004 y 389/2005", "result": "dos IFI, firma 26/05/2004, pari passu y comisión", "artifact": "dos HTML oficiales", "limit": "anexos históricos anteriores abiertos"},
])

# Amend the inherited legal/public-boundary rows to reflect the recovered official annex.
legal = read_csv(HERE / "E0_BID1192_FIDEICOMISO_FONDYF_LEGAL_CHAIN_V179.csv")
for row in legal:
    if row["row_id"] == "LC179_04":
        row.update({"proved": "modelo 2006 completo recuperado: 99 páginas digitales con contrato base y Anexos I-V", "open": "contraparte ejecutada, versiones previas y desempeño", "source": "Resolución 967/2006 + BO Aviso 9095705/Anexo 00345809"})
write_csv(HERE / "E0_BID1192_FIDEICOMISO_FONDYF_LEGAL_CHAIN_V179.csv", legal)

boundary = read_csv(HERE / "E0_BID1192_PUBLIC_DOCUMENT_BOUNDARY_V179.csv")
for row in boundary:
    if row["row_id"] == "PB179_04":
        row.update({"public_result": "anexo oficial completo recuperado mediante el detalle BO y endpoint público", "proved": "texto íntegro del modelo 2006 y Anexos I-V", "next": "contraparte ejecutada, reportes y cumplimiento"})
write_csv(HERE / "E0_BID1192_PUBLIC_DOCUMENT_BOUNDARY_V179.csv", boundary)

(HERE / "CORRECTION_LOG_V179.md").write_text("""# Correcciones V179

- Se corrige la formulación V178 «el anexo de 74 hojas no fue publicado». El texto normalizado de Argentina.gob.ar aparece sin anexo, pero el detalle oficial del Boletín Oficial conserva un descargable asociado (Aviso 9095705, Anexo 00345809). Se recuperaron 99 páginas digitales.
- Se corrigen seis filas de pedidos y seis claves V178 que habían quedado vacías por un desacople de nombres de columnas al serializar; V179 conserva sus contenidos completos.
- Se reemplaza «contrato completo» por «modelo contractual aprobado completo» cuando corresponde. Las líneas de firma no completadas impiden tratar el objeto como contraparte ejecutada.
- Se separan expresamente las obligaciones de Macro/Credicoop bajo MyPES II(a) 2006 de la administración BNA-FONDYF 2013.
""", encoding="utf-8")

local_census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V179.csv")
for s in sources:
    p = REPO / s["archivo_local"].lstrip("/")
    local_census.append({
        "source_id": s["id"], "institution": s["institucion"], "artifact": s["titulo"], "url": s["url_original"],
        "local_path": s["archivo_local"], "sha256": s["sha256"], "bytes": str(p.stat().st_size),
        "period_coverage": s["periodo_utilizado"], "variable_families": "BID1192;trust;roles;guarantees;reporting;provenance",
        "primary_source": "YES", "preserved": "YES", "method_breaks": "approved model versus executed counterpart",
        "use_status": "E0_USABLE_CONTRACTUAL_ARCHITECTURE", "caveat": s["nota"],
    })
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V179.csv", list({x["source_id"]: x for x in local_census}.values()))

SYNC.mkdir(parents=True, exist_ok=True)
sync_rows = [{"source_id": s["id"], "local_path": s["archivo_local"], "sha256": s["sha256"], "bytes": str((REPO / s["archivo_local"].lstrip("/")).stat().st_size)} for s in sources]
write_csv(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V179.csv", sync_rows)
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V179.csv", [{"source_id": s["id"], "url": s["url_original"], "retrieval": "DIRECT_OFFICIAL_TLS_OR_BO_PUBLIC_POST", "status": "PRESERVED"} for s in sources])
(SYNC / "SOURCE_SYNC_REPORT_V179.md").write_text("# Sincronización V179\n\n- Catálogo 649/649; hashes válidos; brecha 0.\n- Seis artefactos oficiales nuevos: anexo PDF, detalle BO, protocolo de descarga y tres normas.\n- Las 99 páginas del PDF fueron inspeccionadas visualmente; cinco artefactos web pasaron control de contenido.\n- El modelo contractual está completo; contraparte ejecutada y desempeño siguen abiertos.\n", encoding="utf-8")
(SYNC / "qa_source_sync_v179.py").write_text("""from pathlib import Path
import csv,hashlib
H=Path(__file__).resolve().parent; R=H.parents[4]
rows=list(csv.DictReader((H/'SOURCE_SYNC_FILE_MANIFEST_V179.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==6
for x in rows:
 p=R/x['local_path'].lstrip('/'); assert p.is_file() and p.stat().st_size==int(x['bytes']) and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
print('SOURCE SYNC V179 PASS · 6/6')
""", encoding="utf-8")

prov = read_csv(HERE / "ARCHIVAL_PROVENANCE_V179.csv")
for row in prov:
    if row["source_id"] == "e0_norm_res967_2006_mypesii_trust_v178":
        row["provenance_note"] = "Texto normativo oficial preservado sin anexo embebido; V179 recupera el anexo asociado desde el detalle oficial del Boletín Oficial."
for s in sources:
    p = REPO / s["archivo_local"].lstrip("/")
    prov.append({"source_id": s["id"], "original_url": s["url_original"], "retrieval_url": s["url_original"], "capture_timestamp": "2026-09-01", "cdx_digest": "N/A_OFFICIAL_DIRECT_DOWNLOAD", "local_path": s["archivo_local"], "sha256": s["sha256"], "bytes": str(p.stat().st_size), "provenance_note": s["nota"]})
write_csv(HERE / "ARCHIVAL_PROVENANCE_V179.csv", list({row["source_id"]: row for row in prov}.values()))

with (HERE / "SOURCE_REFERENCES_V179.md").open("a", encoding="utf-8") as f:
    f.write("\n## V179 · anexo contractual completo MyPES II(a)\n")
    for s in sources:
        f.write(f"\n- `{s['id']}` · {s['titulo']} · {s['url_original']} · `{s['archivo_local']}` · `{s['sha256']}`\n")
with (HERE / "RETRIEVAL_LOG_V179.md").open("a", encoding="utf-8") as f:
    f.write("\n## V179\n\n- El buscador avanzado del Boletín Oficial devolvió el Aviso 9095705 y Anexo 00345809.\n- La función oficial `descargarPDFAnexo` documentó el endpoint POST y permitió preservar el PDF de 6.811.172 bytes.\n- Se inspeccionaron visualmente las 99 páginas: contrato base (1-53), Anexos I (54-61), II (62-74), III (75-97), IV (98) y V (99).\n- El Anexo III prueba una arquitectura de garantías/indemnidad de Macro y Credicoop en el modelo aprobado; no prueba activación ni pago.\n- La contraparte ejecutada y la transición hacia FONDYF/BNA permanecen abiertas.\n")

recovery = f"""# Recuperación archivística · V179

La serie 2011-2016 y los gaps contables de V178 se mantienen sin imputación de daño. V179 recupera desde el Boletín Oficial el modelo contractual aprobado completo de la Resolución 967/2006: 99 páginas digitales con contrato base y Anexos I-V. El paquete prueba a nivel contractual la distribución de funciones, la garantía/indemnidad de Macro y Credicoop y el archivo periódico que debía producirse. No es una contraparte ejecutada y no prueba activación, incumplimiento ni pago. Falta obtener firmas, reportes, cartera, auditorías, débitos y el instrumento de transición hacia FONDYF/BNA. Archivo 649/649; panel 34 y {COVERAGE}%; solicitudes 0.
"""
for name in ("E0_PLAN_2009_ARCHIVE_RECOVERY_NOTE_V179.md", "E0_SIGEN_ARCHIVAL_INDEX_RECOVERY_NOTE_V179.md", "E0_FISCAL_RECONSTRUCTION_V179.md"):
    (HERE / name).write_text(recovery, encoding="utf-8")
(HERE / "CNV_ATTACHMENT_ANALYTIC_REVIEW_V179.md").write_text(f"# Revisión acumulada V179\n\nPanel 34 y {COVERAGE}% congelado. El modelo contractual Res. 967/2006 y sus Anexos I-V están preservados; la contraparte ejecutada, MP0191, Cuadro 13.3, reportes, transición FONDYF, SISIO/3672 y daño siguen abiertos. Solicitudes 0.\n", encoding="utf-8")

(HERE / "README_V179.md").write_text(f"""# Checkpoint V179

## Hallazgo principal

- Se recuperó del Boletín Oficial el anexo oficial completo de la Resolución 967/2006: 6.811.172 bytes, SHA-256 `{EXPECTED[FILES['pdf']][1]}` y 99 páginas digitales.
- La estructura es completa: contrato base (1-53), Reglamento de Crédito (54-61), Reglamento de Desembolso (62-74), Garantía Bancaria e Indemnidad (75-97), auditores (98) y pagaré (99).
- La norma dice 74 hojas; el objeto digital tiene 99 páginas. Se registra la diferencia sin declararla error hasta reconciliar foliatura y digitalización.

## Qué cambia

- Macro y Credicoop, bajo el modelo MyPES II(a) 2006, no eran simples administradores: aparecen como IFI originantes/administradoras, aportantes de contraparte y garantes de obligaciones definidas.
- El Anexo III contempla garantía solidaria, obligación de aportar ante insuficiencia, autorización de débito automático, mora, intereses, renuncias y acción directa del Fiduciante.
- Macro asume además una garantía específica por obligaciones de SUD, fiduciaria designada por esa entidad.
- La cláusula 16 define el archivo probatorio que debería existir: rendiciones, cartera, tasas, mora, previsiones, gastos, cobranzas, juicios, auditorías y archivos mensuales de deudores remitidos al BCRA.

## Límite probatorio

- El PDF es el modelo aprobado, con espacios/líneas de firma sin completar. No es todavía la contraparte ejecutada.
- Las cláusulas prueban asignación jurídica prevista; no prueban por sí solas que hubo incumplimiento, activación de garantías, débito, daño o apropiación.
- No se trasladan estas obligaciones a BNA-FONDYF 2013: ese modelo dice que BNA no asume riesgo crediticio. Falta el instrumento de liquidación, cesión, novación o transferencia entre regímenes.

## Estado

- Archivo 649/649; seis fuentes oficiales nuevas; hashes válidos.
- PDF: 99/99 páginas inspeccionadas visualmente. Web: 5/5 controles de contenido.
- Panel 34; {NUMERATOR}/{ASSETS}; {COVERAGE}%; solicitudes efectivas 0; SAF355 0/5; ejecución histórica 0/10.
- Sin promoción monetaria ni imputación de daño.
""", encoding="utf-8")

(HERE / "VEREDICTO_V179.md").write_text("""# Veredicto V179

Avance probatorio mayor. El anexo oficial recuperado sustituye una inferencia institucional por cláusulas concretas: identifica a las partes, distribuye administración y control, establece información periódica y crea una garantía e indemnidad robusta a cargo de las IFI del esquema 2006. Esto vuelve cerrables los pedidos de evidencia de desempeño. Aún no permite afirmar responsabilidad material: falta la contraparte ejecutada, el padrón de créditos, rendiciones, auditorías, avisos, débitos y el instrumento que conectó o extinguió esta arquitectura al crearse FONDYF. La conclusión jurídicamente segura es contractual, no indemnizatoria.
""", encoding="utf-8")

(HERE / "AUDITORIA_V179.md").write_text(f"""# Auditoría V179

- 649/649 fuentes; huecos 0; seis artefactos oficiales nuevos.
- Anexo BO: 99/99 páginas inspeccionadas visualmente; ausencia de capa de texto registrada.
- Controles web: 5/5 PASS; procedencia endpoint/hash documentada.
- Matrices nuevas: estructura 6; roles 10; garantías 11; inventario de datos 10; no transposición 9; estado de ejecución 7.
- Se repararon seis objetos y seis claves de pedido que habían quedado vacíos en V178; se agregaron seis objetos cerrables. Todos DRAFT_NOT_SENT.
- Panel 34; {COVERAGE}%; solicitudes 0; SAF355 0/5; ejecución 0/10; daño no probado.
""", encoding="utf-8")

(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V179_A_V180.md").write_text("""# Handover V179 → V180

## Cerrado
- Anexo oficial completo Res. 967/2006 recuperado y preservado con procedencia/hash.
- 99 páginas inspeccionadas y estructura contrato + Anexos I-V inventariada.
- Roles de Estado, UCP, BCRA, SUD, Macro y Credicoop delimitados.
- Garantía/indemnidad IFI y archivo contractual de reportes convertidos en matrices y pedidos cerrables.
- Separación jurídica MyPES II(a) 2006 versus BNA-FONDYF 2013 explicitada.

## Prioridad V180
1. Recuperar contraparte ejecutada del 26/05/2004 y modificaciones ejecutadas 2005-2006.
2. Recuperar rendiciones cláusula 16, archivos mensuales BCRA e informes de auditor externo.
3. Recuperar padrón de créditos, cesiones, pagarés, garantías, contraparte local y tasas efectivas.
4. Recuperar avisos de insuficiencia, aportes, débitos y acciones del Anexo III.
5. Recuperar liquidación/cesión/novación/transferencia hacia FONDYF y convenio BNA ejecutado.
6. Continuar Notas BCRA 466/1796/08, 88/14, Acta 398, Cuadro 13.3 y SISIO/3672.
7. No convertir cláusula en incumplimiento ni gap en daño sin registros de desempeño.
""", encoding="utf-8")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V178.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint": "V179", "date": "2026-09-01", "master_catalog_entries": 649, "physical_local_copies": 649,
    "physical_local_hash_ok": 649, "remaining_catalog_physical_or_hash_gaps": 0,
    "state": "RES967_FULL_APPROVED_MODEL_AND_ANNEXES_RECOVERED_IFI_GUARANTEE_CHAIN_PROVED_EXECUTED_COUNTERPART_AND_PERFORMANCE_OPEN",
    "analytical_promotion": "CONTRACTUAL_ARCHITECTURE_ONLY_NO_MONETARY_OR_DAMAGE_PROMOTION_V179",
    "mypesii_approved_contract_full_body_located": True, "mypesii_executed_contract_full_body_located": False,
    "mypesii_res967_official_pdf_pages": 99, "mypesii_res967_normative_folios": 74,
    "mypesii_ifi_guarantee_indemnity_model_proved": True, "mypesii_ifi_guarantee_execution_proved": False,
    "mypesii_clause16_reporting_duties_proved": True, "mypesii_clause16_reports_located": False,
    "mypesii_2006_to_fondyf_2013_transition_instrument_located": False,
    "bid1192_damage_or_appropriation_proved": False, "requests_submitted": 0, "responses_received": 0,
    "saf355_certifications_located": 0, "executed_historical_bank_rows_confirmed": 0,
    "new_v179_sources": 6, "public_web_queries_v179": 6, "strict_coverage_increment_v179_pp": "0",
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V179.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

origins = read_csv(ORIGINS)
by_path = {row["path"]: row for row in origins}
for path in iter_files(HIST_ROOT):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path": path.relative_to(CYCLE).as_posix(), "origin": "downloaded/preserved V179", "note": "official BO/Argentina.gob.ar artifact; verified"}
for path in iter_files(SYNC):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path": path.relative_to(CYCLE).as_posix(), "origin": "generated/updated V179", "note": "six-source synchronization"}
for path in HERE.iterdir():
    if path.is_file():
        by_path[path.relative_to(CYCLE).as_posix()] = {"path": path.relative_to(CYCLE).as_posix(), "origin": "generated/updated V179", "note": "Res. 967 contractual checkpoint"}
for path in (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V179.csv", AUDIT / "SOURCE_BACKUP_CENSUS_V179.csv", AUDIT / "SOURCE_PRESERVATION_MISSING_V179.csv", AUDIT / "CURRENT_SOURCE_COMPLETENESS_V179.json"):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path": path.relative_to(CYCLE).as_posix(), "origin": "generated/updated V179", "note": "649-source completeness"}
write_csv(ORIGINS, list(by_path.values()), ["path", "origin", "note"])

transparency = CYCLE / "TRANSPARENCY_README.md"
body = transparency.read_text(encoding="utf-8-sig")
if "## V179 · anexo completo Resolución 967/2006" not in body:
    body += "\n\n## V179 · anexo completo Resolución 967/2006\n\nEl Boletín Oficial conservaba el Anexo 00345809: 99 páginas con el modelo completo y Anexos I-V. La arquitectura de garantías de Macro/Credicoop y los reportes exigibles quedan probados a nivel contractual. No se confunde modelo con contraparte ejecutada ni garantía con incumplimiento. Archivo 649/649; panel 34; solicitudes 0.\n"
    transparency.write_text(body, encoding="utf-8")
(REPO / "BACKUP_ACTUALIZACION_2026-09-01.md").write_text(f"# Backup de actualización · 2026-09-01\n\n- V179; 649/649 fuentes.\n- Anexo oficial Res. 967/2006 completo: 99 páginas y Anexos I-V.\n- Garantías/indemnidad Macro-Credicoop y deberes de reporte probados como arquitectura contractual.\n- Contraparte ejecutada, desempeño y transición FONDYF abiertos; daño no probado.\n- Panel 34, {COVERAGE}%; solicitudes 0.\n", encoding="utf-8")

(HERE / "qa_v179.py").write_text("""from pathlib import Path
import csv,hashlib,json
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==649
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V179.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==649 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V179.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V179' and co['master_catalog_entries']==649
assert co['mypesii_approved_contract_full_body_located'] and not co['mypesii_executed_contract_full_body_located']
assert co['mypesii_ifi_guarantee_indemnity_model_proved'] and not co['mypesii_ifi_guarantee_execution_proved']
assert co['mypesii_clause16_reporting_duties_proved'] and not co['mypesii_clause16_reports_located']
assert not co['mypesii_2006_to_fondyf_2013_transition_instrument_located'] and not co['bid1192_damage_or_appropriation_proved']
assert co['requests_submitted']==co['saf355_certifications_located']==co['executed_historical_bank_rows_confirmed']==0
assert len(rows('E0_BID1192_RES967_DIGITAL_PACKAGE_STRUCTURE_V179.csv'))==6
assert len(rows('E0_BID1192_2006_ROLE_RESPONSIBILITY_MATRIX_V179.csv'))==10
assert len(rows('E0_BID1192_IFI_GUARANTEE_INDEMNITY_MATRIX_V179.csv'))==11
assert len(rows('E0_BID1192_CONTRACTUAL_REPORTING_DATA_INVENTORY_V179.csv'))==10
assert len(rows('E0_BID1192_2006_VS_2013_ROLE_NONTRANSPOSITION_V179.csv'))==9
assert len(rows('E0_BID1192_EXECUTED_MODEL_STATUS_V179.csv'))==7
assert rows('V179_PDF_VISUAL_CONTROL.csv')[0]['result']=='PASS_ALL_99_PAGES_VISUALLY_INSPECTED'
assert len(rows('V179_HTML_CONTENT_CONTROL.csv'))==5 and all(x['result']=='PASS_EXACT_STRING' for x in rows('V179_HTML_CONTENT_CONTROL.csv'))
assert len(rows('V179_SOURCE_BUNDLE.csv'))==6
keys=rows('E0_REQUEST_SEARCH_KEY_MATRIX_V179.csv'); target_keys={f'SK178_{x}' for x in range(50,56)}|{f'SK179_{x}' for x in range(56,62)}; assert target_keys<={x['key_id'] for x in keys}; assert all(x['exact_key'] for x in keys if x['key_id'] in target_keys)
obj=rows('E0_V179_REQUEST_OBJECTS.csv'); target_objects={f'RO178_{x}' for x in range(48,54)}|{f'RO179_{x}' for x in range(54,60)}; assert target_objects<={x['row_id'] for x in obj}; assert all(x['status']=='DRAFT_NOT_SENT' for x in obj); assert all(x['object_id'] and x['exact_record'] for x in obj if x['row_id'] in target_objects); assert obj==rows('E0_V179_REQUEST_OBJECTS_V179.csv')
panel=rows('FOUR_LEG_PASS_PANEL_V179.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
m=json.loads((H/'MANIFEST_V179.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V179' and m['parent_checkpoint']=='V178' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V179 QA PASS · 649/649 · RES967=99/99 VISUAL · IFI-GUARANTEE=MODEL_PROVED · EXECUTION=OPEN · panel=34 · requests=0')
""", encoding="utf-8")

(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")
manifest_files = [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha(p)} for p in sorted(HERE.iterdir(), key=lambda x: x.name.casefold()) if p.is_file() and p.name != "MANIFEST_V179.json"]
manifest = {
    "checkpoint": "V179", "parent_checkpoint": "V178", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "exact_entities": 34, "strict_coverage_pct": COVERAGE, "strict_asset_numerator_million_ars": NUMERATOR, "system_assets_million_ars": ASSETS,
    "new_promotions": [], "source_archive": "649/649; official Res. 967/2006 annex package plus five provenance/normative artifacts added",
    "historical_finding": "full approved MyPES II(a) 2006 model recovered; IFI guarantee/indemnity and reporting architecture proved; executed counterpart, performance, transition and damage open",
    "mypesii_res967_pdf_pages": 99, "mypesii_res967_normative_folios": 74, "mypesii_approved_model": "LOCATED", "mypesii_executed_counterpart": "NOT_LOCATED",
    "ifi_guarantee_model": "PROVED", "ifi_guarantee_execution": "NOT_PROVED", "note_3672_target_sisio_rows": "NOT_LOCATED",
    "closed_network_gate": "NO", "saf355_certifications": "0/5", "executed_historical_bank_rows": "0/10", "requests_submitted": 0, "files": manifest_files,
}
(HERE / "MANIFEST_V179.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path": p.relative_to(REPO).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)} for p in iter_files(REPO) if p != global_manifest]
payload = {"checkpoint": "V179", "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"), "strict_coverage_pct": COVERAGE, "exact_entities": 34, "closed_network_gate": "NO", "source_audit": "649 master; 649 physical SHA-valid", "historical_workstream": "Res967 full approved model and IFI guarantees proved; executed counterpart/performance/transition/damage open; drafts not sent", "file_count_excluding_manifest": len(global_files), "files": global_files}
tmp = global_manifest.with_suffix(".json.V179tmp")
tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
tmp.replace(global_manifest)
print("V179 BUILD PASS · catalog=649/649 · new=6 · RES967=99 pages · IFI-GUARANTEE=MODEL_PROVED · EXECUTION=OPEN · panel=34 · requests=0")
