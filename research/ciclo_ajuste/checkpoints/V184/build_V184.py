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
PARENT = CYCLE / "checkpoints" / "V183"
AUDIT = CYCLE / "source_audit"
SYNC = CYCLE / "inputs" / "source_sync" / "v184"
HIST_ROOT = CYCLE / "inputs" / "historical_retrieval" / "v184"
HIST = HIST_ROOT / "binaries"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"
EXCLUDED = {".git", "__pycache__", "tmp", "node_modules"}
COVERAGE = "63.440604"
NUMERATOR = "61345602.215"
ASSETS = "96697695.5"


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows, fields=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or (list(rows[0]) if rows else [])
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def iter_files(root):
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted((name for name in dirs if name not in EXCLUDED), key=str.casefold)
        for name in sorted(files, key=str.casefold):
            yield Path(directory) / name


def tree(root):
    out = []
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted((name for name in dirs if name not in EXCLUDED), key=str.casefold)
        base = Path(directory)
        out += [(base / name).relative_to(root).as_posix() + "/" for name in dirs]
        out += [(base / name).relative_to(root).as_posix() for name in sorted(files, key=str.casefold)]
    return "\n".join(out) + "\n"


def append_once(path, marker, text):
    body = path.read_text(encoding="utf-8-sig") if path.exists() else ""
    if marker not in body:
        path.write_text(body.rstrip() + "\n\n" + text.strip() + "\n", encoding="utf-8")


def clone_parent():
    skip = {
        "MANIFEST_V183.json", "README_V183.md", "VEREDICTO_V183.md", "AUDITORIA_V183.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V183_A_V184.md", "V183_SOURCE_BUNDLE.csv",
        "V183_PUBLIC_SEARCH_LOG.csv", "V183_PDF_VISUAL_CONTROL.csv", "V183_PDF_TEXT_CONTROL.csv",
        "V183_XLSX_CONTENT_CONTROL.csv", "V183_HTML_CONTENT_CONTROL.csv", "CORRECTION_LOG_V183.md",
    }
    HERE.mkdir(parents=True, exist_ok=True)
    for source in sorted(PARENT.iterdir(), key=lambda path: path.name.casefold()):
        if not source.is_file() or source.name in skip or source.name.startswith(("build_", "qa_")):
            continue
        target = HERE / source.name.replace("V183", "V184")
        target.write_bytes(source.read_bytes())


SOURCE_SPECS = [
    {
        "id": "e0_cgn_account2020_annex437_my4002_active_fondyf_v184",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta de Inversión 2020 · Anexo 4.37 · MY4002 activa bajo FONDyF",
        "url": "https://www.argentina.gob.ar/sites/default/files/separatai-ejec.presupuestaria-cuenta2020.pdf",
        "file": "cgn_cuenta_inversion_2020_separata_i_ejecucion_presupuestaria.pdf",
        "published": "2021", "period": "2018-2020", "type": "PDF oficial preservado · extracción estructurada y control visual",
        "note": "PDF 236 / Anexo 4.37 p.21/40: MY4002 conserva como referencia el saldo 2018 USD 15.182,68 / ARS 569.350,57; los campos 2020 están vacíos. La nota NO-2021-16359825-APN-DNFP#MDP dice que la operatoria terminó, FONDyF estaba en liquidación y esta cuenta continuaba activa y manejada por FONDyF. No prueba saldo 2020, convenio ejecutado, pagador, deuda ni pago.",
    },
    {
        "id": "e0_hcdn_jgm_0032_2021_account2020_my4002_v184",
        "institution": "Honorable Cámara de Diputados de la Nación / Jefatura de Gabinete de Ministros",
        "title": "JGM 0032-JGM-2021 · copia legislativa de Cuenta 2020 con MY4002",
        "url": "https://www4.hcdn.gob.ar/dependencias/dsecretaria/Periodo2021/PDF2021/TP2021/0032-JGM-2021.pdf",
        "file": "hcdn_jgm_cuenta_inversion_2020_anexo_4_37_fondyf_active_accounts.pdf",
        "published": "2021", "period": "2018-2020", "type": "PDF oficial legislativo preservado · copia de transmisión y control visual",
        "note": "PDF 1874 / Anexo 4.37 p.21/40 reproduce la fila MY4002, la nota NO-2021-16359825-APN-DNFP#MDP y el identificador IF-2021-57375822-APN-SSP#MEC. Corrobora la copia CGN; no agrega mayor, extracto o convenio ejecutado.",
    },
    {
        "id": "e0_cgn_account2020_annex437_index_label_mismatch_v184",
        "institution": "Contaduría General de la Nación",
        "title": "Cuenta 2020 · índice oficial del Anexo 4.37 y discrepancia del XLSX servido",
        "url": "https://www.argentina.gob.ar/economia/sechacienda/cgn/cuentainversion/2020/separatai/movimientosfinancieros",
        "file": "argentina_cgn_cuenta2020_movimientosfinancieros_index.html",
        "published": "2021", "period": "2020", "type": "HTML oficial preservado · control de enlace y rotulado",
        "note": "El índice rotula Anexo 4.37 Cuadro de Cuentas Bancarias y enlaza cuenta2020-separatai-anexo-4.37-cuentas_bancarias.xlsx. El archivo servido contiene internamente ANEXO 4.36, hoja F21 A1:BJ51; por ello su ausencia de MY4002 no es una prueba válida sobre el verdadero cuadro bancario.",
    },
    {
        "id": "e0_bcra_b11368_dt1_fiduciary_transfer_code_v184",
        "institution": "Banco Central de la República Argentina / Boletín Oficial",
        "title": "Comunicación BCRA B 11368 · código DT1 Fideicomiso PyMEs",
        "url": "https://www.boletinoficial.gob.ar/detalleAviso/primera/152527/20161021",
        "file": "boletin_oficial_bcra_com_b11368_dt1_fideicomiso_pymes.html",
        "published": "2016-10-21", "period": "2016", "type": "HTML oficial preservado · diccionario operativo",
        "note": "El código DT1 clasifica transferencias del fiduciario Fideicomiso PyMEs por cancelación de deuda en garantía, gastos, comisiones, impuestos, remuneraciones e inversiones transitorias. Es una clave posible para pedir el ledger; no demuestra que MY4002 haya usado DT1.",
    },
    {
        "id": "e0_tgn_sireco_official_account_closure_route_v184",
        "institution": "Tesorería General de la Nación",
        "title": "SIRECO Web · registro y prueba del cierre de cuentas oficiales",
        "url": "https://www.argentina.gob.ar/economia/tesoreria-general-de-la-nacion/soporte/cuentas-bancarias-sireco-web",
        "file": "argentina_tgn_sireco_cierre_cuentas_oficiales.html",
        "published": "2024-02-08; actualizado 2025-12-02", "period": "2021-2025", "type": "HTML oficial preservado · ruta de custodia contemporánea",
        "note": "La página vigente exige informar el cierre a TGN con copia del extracto o constancia bancaria que permita verificarlo y describe SIRECO como Registro de Cuentas Oficiales, incluyendo programas con financiamiento externo. Sirve para pedir la prueba de cierre/continuidad; no se aplica retroactivamente como prueba del estado 2020.",
    },
]


clone_parent()
SYNC.mkdir(parents=True, exist_ok=True)
for spec in SOURCE_SPECS:
    assert (HIST / spec["file"]).is_file(), spec["file"]

catalog = read_csv(CATALOG)
catalog_fields = list(catalog[0])
by_id = {row["id"]: row for row in catalog}

# Corrige un falso negativo heredado: el endpoint rotulado 4.37 sirve un libro cuyo contenido interno es 4.36.
mislabel_id = "e0_cgn_account2020_bank_accounts_mypes_absence_v182"
mislabel = by_id[mislabel_id]
mislabel["titulo"] = "Cuenta de Inversión 2020 · archivo publicado como Anexo 4.37; contenido interno Anexo 4.36"
mislabel["codigo_serie"] = mislabel["titulo"]
mislabel["tipo"] = "XLSX oficial preservado · discrepancia índice/nombre versus contenido interno"
mislabel["nota"] = (
    "El índice y la URL oficiales lo rotulan Anexo 4.37, pero la hoja F21 A1:BJ51 dice ANEXO 4.36 "
    "(Unidades Ejecutoras de Transferencias Externas). La ausencia de BID1192/MY4002 no prueba ausencia "
    "del cuadro bancario. Corrección V184; el verdadero Anexo 4.37 se verifica en la separata PDF."
)

new_sources = []
for spec in SOURCE_SPECS:
    path = HIST / spec["file"]
    row = {
        "id": spec["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": spec["institution"],
        "titulo": spec["title"], "url_original": spec["url"],
        "archivo_local": "/" + path.relative_to(REPO).as_posix(), "fecha_descarga": "2026-09-01",
        "fecha_publicacion": spec["published"], "codigo_serie": spec["title"], "periodo_utilizado": spec["period"],
        "tipo": spec["type"], "sha256": sha(path), "nota": spec["note"],
    }
    by_id[row["id"]] = row
    new_sources.append(row)
catalog = list(by_id.values())
write_csv(CATALOG, catalog, catalog_fields)
assert len(catalog) == len({row["id"] for row in catalog}) == 708

audit = []
for row in catalog:
    path = REPO / row["archivo_local"].lstrip("/")
    actual = sha(path) if path.is_file() else ""
    audit.append({
        "id": row["id"], "archivo_local": row["archivo_local"], "exists": str(path.is_file()),
        "sha_catalog": row["sha256"].lower(), "sha_actual": actual,
        "hash_ok": str(path.is_file() and bool(row["sha256"]) and actual == row["sha256"].lower()),
    })
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V184.csv", audit)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V184.csv", audit)
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V184.csv", [row for row in audit if row["hash_ok"] != "True"], list(audit[0]))
assert all(row["hash_ok"] == "True" for row in audit)

write_csv(HERE / "E0_BID1192_CGN_TRANSITION_2018_2021_V184.csv", [
    {"cutoff":"2018-12-31","publication":"Cuenta 2018","program_flow_state":"UEPEX_DECLARED_ZERO_CGN_RECONSTRUCTION","bank_account_state":"MY4002_REFERENCE_USD_15182_68_ARS_569350_57_UNCERTIFIED","proved":"CGN reconstruye la cifra y explica que el respaldo no identificaba banco/fecha","not_proved":"extracto BCRA, contraparte, pago o deuda","source":"Cuenta 2018 PDF 249"},
    {"cutoff":"2019-12-31","publication":"Cuenta 2019","program_flow_state":"NO_INFORMATION_SUBMITTED","bank_account_state":"2018_REFERENCE_BALANCES_REPEATED","proved":"CGN repite saldos de referencia 2018","not_proved":"saldo, movimientos, cierre o destino 2019","source":"Cuenta 2019 Anexo bancario PDF 167-169"},
    {"cutoff":"2020-12-31","publication":"Cuenta 2020 · Anexo 4.21","program_flow_state":"ALL_PROGRAM_FLOW_RUBRICS_ZERO_CLOSURE_UNCERTIFIED","bank_account_state":"NOT_A_BANK_ACCOUNT_TEST","proved":"cuadro del programa en cero y nota de cierre definitivo no certificado","not_proved":"cero, baja o extinción de MY4002","source":"Cuenta 2020 Anexo 4.21 y nota 3"},
    {"cutoff":"2020-12-31","publication":"Cuenta 2020 · Anexo 4.37","program_flow_state":"SEPARATE_BANK_ACCOUNT_DISCLOSURE","bank_account_state":"MY4002_REPORTED_ACTIVE_UNDER_FONDYF_2020_FIELDS_BLANK","proved":"fila MY4002; referencia 2018; nota dice cuenta activa/manejada por FONDyF y describe transferencias BCRA por convenios","not_proved":"saldo 2020, transferencia efectuada, destino fiduciario, extracto o cierre","source":"Cuenta 2020 PDF 236 / IF-2021-57375822-APN-SSP#MEC"},
    {"cutoff":"2021-12-31","publication":"Cuenta 2021","program_flow_state":"BID1192_COLUMN_ABSENT","bank_account_state":"MY4002_NOT_FOUND_IN_PUBLISHED_TABLE","proved":"ausencia en anexos publicados 2021","not_proved":"fecha/causa de transferencia, cierre o extinción","source":"Cuenta 2021 Anexos 4.20 y 4.35"},
])

write_csv(HERE / "E0_BID1192_FONDYF_ACTIVE_ACCOUNT_TRANSITION_2018_2021_V184.csv", [
    {"record":"MY 4002","denomination":"Fondo Comisión de Compromiso","bank":"BCRA","branch":"Casa Central","funding_source":"13","2018_reference_foreign":"15182.68","2018_reference_ars":"569350.57","2020_numeric_fields":"BLANK","2020_narrative_state":"CONTINUES_ACTIVE_AND_MANAGED_BY_FONDYF","transfer_statement":"BCRA balances are transferred through loan-transfer agreements to fiduciary funds","destination_identified":"NO","executed_agreement_located":"NO","legal_limit":"continuidad administrativa declarada; no saldo 2020, pago, deuda ni responsabilidad","source":"Cuenta 2020 Anexo 4.37 PDF 236"},
    {"record":"MY 4003","denomination":"Fondo para Cobertura Incobrab. IFIs","bank":"BCRA","branch":"Casa Central","funding_source":"13","2018_reference_foreign":"12838.50","2018_reference_ars":"481443.72","2020_numeric_fields":"BLANK","2020_narrative_state":"CONTINUES_ACTIVE_AND_MANAGED_BY_FONDYF","transfer_statement":"same standardized narrative","destination_identified":"NO","executed_agreement_located":"NO","legal_limit":"comparator only","source":"Cuenta 2020 Anexo 4.37 PDF 236"},
])

write_csv(HERE / "E0_BID1192_NO_2021_16359825_EVIDENCE_CHAIN_V184.csv", [
    {"step":"1","document":"NO-2021-16359825-APN-DNFP#MDP","status":"BODY_NOT_LOCATED_PUBLICLY","proved_by_secondary_official_reproduction":"CGN quotes its content in Anexo 4.37","missing":"full signed note, attachments, recipients and metadata"},
    {"step":"2","document":"IF-2021-57375822-APN-SSP#MEC","status":"LOCATED_AS_FOOTER_OF_ACCOUNT_ANNEX","proved_by_secondary_official_reproduction":"identifies compiled official annex containing MY4002 row","missing":"GDE package and remittance metadata"},
    {"step":"3","document":"Convenios de Transferencias de préstamos","status":"REPORTED_NOT_LOCATED","proved_by_secondary_official_reproduction":"CGN says BCRA balances are transferred by these agreements","missing":"executed agreement, date, parties, account map, amount, destination fund and receipts"},
    {"step":"4","document":"MY4002 BCRA/BNA migration ledger","status":"NOT_LOCATED","proved_by_secondary_official_reproduction":"account reported active under FONDyF","missing":"BCRA extract, transfer order, BNA credit, e-SIDIF/SIGADE/SIRECO identifiers and reconciliations"},
])

write_csv(HERE / "E0_BID1192_ACCOUNT_MIGRATION_VS_CLOSURE_V184.csv", [
    {"proposition":"la operatoria del préstamo BID1192 finalizó","status":"SUPPORTED_BY_CGN_QUOTE_OF_NOTE","does_not_mean":"cada cuenta quedó cerrada o con saldo cero"},
    {"proposition":"FONDyF se integró parcialmente con recuperos BID 643/867/1192","status":"SUPPORTED_BY_NOTE_AND_PRIOR_DECREE_CHAIN","does_not_mean":"MY4002 fue transferida por un monto identificable"},
    {"proposition":"FONDyF estaba en proceso de liquidación y no otorgaba nuevos préstamos","status":"SUPPORTED_AS_OF_2020_CLOSING_PACKAGE","does_not_mean":"liquidación terminada o patrimonio extinguido"},
    {"proposition":"fondos recuperados estaban en cuentas del BNA","status":"SUPPORTED_AT_AGGREGATE_NARRATIVE_LEVEL","does_not_mean":"destino individual MY4002 probado"},
    {"proposition":"saldos BCRA se transfieren por convenios a fondos fiduciarios","status":"SUPPORTED_AS_REPORTED_PROCESS","does_not_mean":"convenio específico MY4002 ejecutado"},
    {"proposition":"MY4002 continuaba activa y manejada por FONDyF","status":"SUPPORTED_ADMINISTRATIVE_STATE","does_not_mean":"saldo 2020 cuantificado, extracto BCRA válido o deuda bancaria"},
    {"proposition":"MY4002 desaparece de la tabla publicada 2021","status":"SUPPORTED_PUBLICATION_ABSENCE","does_not_mean":"cierre, pago o extinción"},
])

write_csv(HERE / "E0_BID1192_2020_PUBLISHED_XLSX_LABEL_MISMATCH_V184.csv", [
    {"layer":"official_index","label":"Anexo 4.37 · Cuadro de Cuentas Bancarias","target":"cuenta2020-separatai-anexo-4.37-cuentas_bancarias.xlsx","result":"PUBLISHED_AS_BANK_TABLE"},
    {"layer":"downloaded_workbook","sheet":"F21","range":"A1:BJ51","internal_title":"ANEXO 4.36 · Unidades Ejecutoras de Transferencias Externas","result":"SERVER_FILE_CONTENT_DOES_NOT_MATCH_LABEL"},
    {"layer":"prior_inference","test":"no MY4002 match in downloaded XLSX","result":"INVALID_AS_BANK_TABLE_ABSENCE_TEST","correction":"use official separata PDF Anexo 4.37"},
    {"layer":"verified_pdf","page":"236","internal_annex_page":"21/40","row":"MY 4002","result":"MATCH_ACTIVE_FONDYF_NARRATIVE"},
])

write_csv(HERE / "E0_BID1192_BCRA_TRANSFER_LEDGER_CODE_MATRIX_V184.csv", [
    {"code_or_key":"DT1","official_description":"Operaciones propias - Fiduciario Fideicomiso PyMEs","official_use":"cancelación de deuda por fiduciario en garantía; gastos, comisiones, impuestos, remuneraciones e inversiones transitorias/resultados","relevance":"possible ledger filter for fiduciary transfers","status_for_my4002":"NOT_PROVED_USED","request_fields":"date; amount; currency; debit account; credit account; originator; beneficiary; concept; message/reference; linked agreement"},
    {"code_or_key":"MY 4002","official_description":"Fondo Comisión de Compromiso","official_use":"account identifier in CGN tables","relevance":"primary account key","status_for_my4002":"PROVED_IDENTIFIER_NOT_TRANSACTION_CODE","request_fields":"full account number/CBU; ledger; extracts; authorization; transfer and closure records"},
    {"code_or_key":"NO-2021-16359825-APN-DNFP#MDP","official_description":"note quoted by CGN","official_use":"explains FONDyF liquidation/account transition","relevance":"document join key","status_for_my4002":"QUOTED_BODY_NOT_LOCATED","request_fields":"signed body; attachments; recipients; linked EE/EX; transfer agreements"},
])

write_csv(HERE / "E0_BID1192_SIRECO_CLOSURE_PROOF_ROUTE_V184.csv", [
    {"fact":"SIRECO is the Registro de Cuentas Oficiales","period":"current framework","application_to_my4002":"request any historical/current registration, account status and change log","limit":"current publication does not prove MY4002 was registered in 2020"},
    {"fact":"closure notice must include bank extract and/or bank certificate verifying closure","period":"Disposición TGN 2/2022 as updated","application_to_my4002":"request closure certificate or certify nonexistence","limit":"evidentiary route; not retroactive proof"},
    {"fact":"program accounts with external financing/donations were included in registration campaign","period":"Resolución SH 85/2021 framework","application_to_my4002":"request crosswalk MY4002→official account/CBU and holder","limit":"identifier mapping remains open"},
])

write_csv(HERE / "E0_BID1192_MY4002_EVIDENCE_LADDER_V184.csv", [
    {"level":"1","proposition":"existió MY4002 denominada Fondo Comisión de Compromiso","status":"SUPPORTED","proof":"serie CGN 2006-2020","missing":"none for accounting identity"},
    {"level":"2","proposition":"el saldo de referencia 2018 fue USD 15182.68 / ARS 569350.57","status":"SUPPORTED_AS_CGN_RECONSTRUCTION","proof":"Cuenta 2018 y Cuenta 2020 Anexo 4.37","missing":"bank-identifiable 2018 extract"},
    {"level":"3","proposition":"MY4002 continuaba activa y manejada por FONDyF al cierre 2020","status":"SUPPORTED_ADMINISTRATIVE_NARRATIVE","proof":"Cuenta 2020 PDF 236 quoting NO-2021-16359825","missing":"full note and account register"},
    {"level":"4","proposition":"MY4002 tenía saldo 2020 distinto de cero","status":"NOT_PROVED","proof":"2020 numeric fields are blank, not zero","missing":"2020 extract, ledger and reconciliation"},
    {"level":"5","proposition":"MY4002 fue efectivamente transferida a un fondo/BNA","status":"NOT_PROVED","proof":"CGN reports a general transfer mechanism","missing":"executed agreement, BCRA debit, BNA/fund credit and account map"},
    {"level":"6","proposition":"Macro o Credicoop originaron los importes","status":"NOT_PROVED","proof":"no counterparty in public rows","missing":"transfer/receipt/asiento espejo"},
    {"level":"7","proposition":"MY4002 correspondía a la liquidación Res1406","status":"NOT_PROVED","proof":"nominal thematic coincidence only","missing":"act, calculation, expediente and accounting linkage"},
    {"level":"8","proposition":"existió deuda firme, pago, daño or responsabilidad","status":"NOT_PROVED","proof":"administrative account continuity is insufficient","missing":"final decision, payment evidence, causation and damage quantification"},
])

write_csv(HERE / "E0_BID1192_MY4002_CLAIM_SEPARATION_V184.csv", [
    {"claim":"account identity","status":"PROVED","source":"CGN annual tables"},
    {"claim":"2018 reference accounting amount","status":"PROVED_AS_RECONSTRUCTION_NOT_BANK_BALANCE","source":"Cuenta 2018/2020"},
    {"claim":"administrative continuity in 2020","status":"PROVED_AS_REPORTED","source":"Cuenta 2020 Anexo 4.37"},
    {"claim":"2020 monetary balance","status":"OPEN_FIELDS_BLANK","source":"Cuenta 2020 Anexo 4.37"},
    {"claim":"executed transfer BCRA→fiduciary/BNA","status":"OPEN","source":"general mechanism only"},
    {"claim":"Res1406 linkage or bank counterparty","status":"OPEN","source":"no join record"},
    {"claim":"firm debt/payment/damage/liability","status":"OPEN","source":"required legal and transactional records absent"},
])

requests = read_csv(HERE / "E0_V184_REQUEST_OBJECTS.csv")
requests += [
    {"row_id":"RO184_83","object_id":"NO_2021_16359825_FULL_GDE_PACKAGE","custodian":"Ministerio de Desarrollo Productivo/Economía · DNFP · Secretaría PyME","exact_record":"NO-2021-16359825-APN-DNFP#MDP, anexos, pases y expediente electrónico","period":"2021","minimum_fields":"firmante; fecha; destinatario; EE/EX; anexos; cuentas; saldos; convenios; destino","closure_rule":"obtener cuerpo firmado y vincular cada cuenta, incluida MY4002, con su estado y acto","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO184_84","object_id":"BID1192_EXECUTED_LOAN_TRANSFER_AGREEMENTS","custodian":"Secretaría PyME · FONDyF · BNA · BCRA · TGN","exact_record":"Convenios de Transferencias de préstamos citados en Anexo 4.37","period":"2012-2021","minimum_fields":"fecha; partes; fondo origen/destino; cuenta/CBU; moneda; monto; derecho cedido; firmas; comprobantes","closure_rule":"conciliar convenio, débito BCRA, crédito destino y asiento contable cuenta por cuenta","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO184_85","object_id":"MY4002_SIRECO_ACCOUNT_STATUS_AND_CLOSURE","custodian":"TGN · DACB · SIRECO · SAF362","exact_record":"alta, modificaciones, titularidad, estado, cierre y respaldos de MY4002","period":"2004-current","minimum_fields":"identificador; cuenta/CBU; banco; titular; fechas; estado; extracto/constancia de cierre; GDE","closure_rule":"probar continuidad, transferencia o cierre con constancia bancaria verificable","status":"DRAFT_NOT_SENT"},
    {"row_id":"RO184_86","object_id":"MY4002_BCRA_TRANSFER_LEDGER_DT1_AND_ALTERNATIVES","custodian":"BCRA · BNA · FONDyF · SAF362","exact_record":"ledger de transferencias MY4002 y códigos STAF/MEP aplicables, incluyendo DT1 si correspondiera","period":"2012-2021","minimum_fields":"fecha; código; moneda; monto; cuenta débito; cuenta crédito; ordenante; beneficiario; concepto; referencia; convenio","closure_rule":"identificar o descartar cada transferencia sin inferir DT1 por analogía","status":"DRAFT_NOT_SENT"},
]
write_csv(HERE / "E0_V184_REQUEST_OBJECTS.csv", requests)
write_csv(HERE / "E0_V184_REQUEST_OBJECTS_V184.csv", requests)

keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V184.csv")
keys += [
    {"key_id":"SK184_82","request_id":"RO184_83","key_group":"gde_note","exact_key":"NO-2021-16359825-APN-DNFP#MDP; IF-2021-57375822-APN-SSP#MEC","search_purpose":"recover note and package","source_or_basis":"Cuenta 2020 Anexo 4.37","caveat":"CGN quote is not full note"},
    {"key_id":"SK184_83","request_id":"RO184_84","key_group":"transfer_agreement","exact_key":"Convenios de Transferencias de préstamos; BID 1192/OC-AR; FONDyF; MY 4002","search_purpose":"recover executed account migration","source_or_basis":"Cuenta 2020 Anexo 4.37","caveat":"general mechanism not execution proof"},
    {"key_id":"SK184_84","request_id":"RO184_85","key_group":"official_account_register","exact_key":"MY 4002; Fondo Comisión de Compromiso; BCRA; SAF 362; SIRECO","search_purpose":"map account and closure state","source_or_basis":"CGN + TGN SIRECO","caveat":"current route may not contain full historic migration"},
    {"key_id":"SK184_85","request_id":"RO184_86","key_group":"transfer_ledger","exact_key":"DT1; OP. PROP-FIDUC. FIDEIC. PYMES; MY 4002","search_purpose":"filter fiduciary-transfer ledger","source_or_basis":"BCRA B 11368","caveat":"DT1 use by MY4002 not proved"},
]
write_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V184.csv", keys)

write_csv(HERE / "V184_PUBLIC_SEARCH_LOG.csv", [
    {"query_id":"PS184_01","query":"NO-2021-16359825-APN-DNFP#MDP + exact variants","result":"only CGN/HCDN official reproduction located","limit":"signed note and attachments open"},
    {"query_id":"PS184_02","query":"Convenios de Transferencias de préstamos + FONDyF + MY4002","result":"general process located in Cuenta 2020","limit":"executed agreements not indexed"},
    {"query_id":"PS184_03","query":"Notas 04854651SSFP#MP/2017 and 7813292/SSFP#MP/2017","result":"only SIGEN compilation indexed","limit":"note bodies and annexes open"},
    {"query_id":"PS184_04","query":"Resolución 1406 November 2014 Macro Credicoop MYPES II","result":"no exact act beyond SIGEN compilations","limit":"act, file, appeals and final decision open"},
    {"query_id":"PS184_05","query":"Cuenta 2020 Anexo 4.37 MY4002","result":"direct CGN PDF and HCDN legislative copy located and preserved","limit":"2020 numeric fields blank"},
    {"query_id":"PS184_06","query":"BCRA B11368 DT1 + TGN SIRECO closure","result":"official transaction-code and account-closure routes preserved","limit":"routes only, not historical execution proof"},
])

bundle = []
for row in new_sources:
    path = REPO / row["archivo_local"].lstrip("/")
    bundle.append({"source_id":row["id"],"file":path.name,"bytes":path.stat().st_size,"sha256":sha(path),"status":"CATALOGUED_SHA_VALID"})
write_csv(HERE / "V184_SOURCE_BUNDLE.csv", bundle)
write_csv(HERE / "V184_PDF_VISUAL_CONTROL.csv", [
    {"file":"cgn_cuenta_inversion_2020_separata_i_ejecucion_presupuestaria.pdf","pages":"236","result":"PASS_MY4002_ACTIVE_FONDYF_2020_FIELDS_BLANK"},
    {"file":"hcdn_jgm_cuenta_inversion_2020_anexo_4_37_fondyf_active_accounts.pdf","pages":"1874","result":"PASS_LEGISLATIVE_COPY_AND_IF_IDENTIFIER"},
])
write_csv(HERE / "V184_PDF_TEXT_CONTROL.csv", [
    {"file":"cgn_cuenta_inversion_2020_separata_i_ejecucion_presupuestaria.pdf","pages_scanned":"268","needle":"MY 4002; NO-2021-16359825; continúa activa","result":"MATCH_PDF_236"},
    {"file":"hcdn_jgm_cuenta_inversion_2020_anexo_4_37_fondyf_active_accounts.pdf","pages_scanned":"1907","needle":"MY 4002; NO-2021-16359825; continúa activa","result":"MATCH_PDF_1874"},
])
write_csv(HERE / "V184_XLSX_CONTENT_CONTROL.csv", [
    {"file":"cgn_account_2020_annex_4_37_bank_accounts.xlsx","sheet":"F21","range":"A1:BJ51","published_label":"Anexo 4.37","internal_title":"ANEXO 4.36","result":"FAIL_LABEL_CONTENT_MATCH_PRIOR_ABSENCE_TEST_RETRACTED"},
    {"file":"cgn_account_2021_annex_4_35_bank_accounts.xlsx","sheet":"ctas","range":"A1:P1041","published_label":"Anexo 4.35","internal_title":"CUADRO DE CUENTAS BANCARIAS - UEPEX","result":"PASS_NO_MY4002_MATCH_PUBLICATION_ABSENCE_ONLY"},
])
write_csv(HERE / "V184_HTML_CONTENT_CONTROL.csv", [
    {"file":"argentina_cgn_cuenta2020_movimientosfinancieros_index.html","needle":"Anexo 4.37; Cuadro de Cuentas Bancarias; cuenta2020-separatai-anexo-4.37-cuentas_bancarias.xlsx","result":"MATCH_PUBLISHED_LABEL_AND_TARGET"},
    {"file":"boletin_oficial_bcra_com_b11368_dt1_fideicomiso_pymes.html","needle":"DT1; Fiduciario Fideicomiso PyMEs","result":"MATCH_POSSIBLE_LEDGER_CODE_NOT_EXECUTION_PROOF"},
    {"file":"argentina_tgn_sireco_cierre_cuentas_oficiales.html","needle":"extracto bancario y/o constancia bancaria; SIRECO","result":"MATCH_CURRENT_CLOSURE_EVIDENCE_ROUTE"},
])

archival = read_csv(HERE / "ARCHIVAL_PROVENANCE_V184.csv")
for row in new_sources:
    path = REPO / row["archivo_local"].lstrip("/")
    archival.append({"source_id":row["id"],"original_url":row["url_original"],"retrieval_url":row["url_original"],"capture_timestamp":"2026-09-01","cdx_digest":"N/A_OFFICIAL_DIRECT_DOWNLOAD","local_path":row["archivo_local"],"sha256":row["sha256"],"bytes":path.stat().st_size,"provenance_note":row["nota"]})
write_csv(HERE / "ARCHIVAL_PROVENANCE_V184.csv", archival)

census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V184.csv")
for row in new_sources:
    path = REPO / row["archivo_local"].lstrip("/")
    census.append({"source_id":row["id"],"institution":row["institucion"],"artifact":row["titulo"],"url":row["url_original"],"local_path":row["archivo_local"],"sha256":row["sha256"],"bytes":path.stat().st_size,"period_coverage":row["periodo_utilizado"],"variable_families":"BID1192;MY4002;FONDyF;account migration;closure evidence","primary_source":"YES","preserved":"YES","method_breaks":"program-flow zero vs bank-account blank fields vs administrative active state","use_status":"USABLE_WITH_EXPLICIT_LIMIT","caveat":row["nota"]})
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V184.csv", census)

append_once(HERE / "SOURCE_REFERENCES_V184.md", "## V184 · MY4002 activa y transición FONDyF", """
## V184 · MY4002 activa y transición FONDyF

- La separata CGN 2020 y su copia legislativa HCDN reproducen la fila MY4002 y la nota NO-2021-16359825-APN-DNFP#MDP.
- La operatoria BID1192 había terminado, FONDyF estaba en liquidación, los recuperos se encontraban en cuentas BNA y los saldos BCRA se transferían por convenios; MY4002 seguía reportada como activa y manejada por FONDyF.
- Los campos numéricos 2020 están vacíos. La fuente prueba continuidad administrativa declarada, no saldo 2020 ni transferencia ejecutada.
- La planilla publicada bajo el nombre Anexo 4.37 contiene internamente Anexo 4.36; se retrae el falso negativo de V182/V183.
""")
append_once(HERE / "RETRIEVAL_LOG_V184.md", "## V184 · búsqueda 2026-09-01", """
## V184 · búsqueda 2026-09-01

- Preservadas la separata CGN 2020, la transmisión legislativa JGM/HCDN, el índice CGN, la Comunicación BCRA B11368 y la ruta TGN/SIRECO.
- No se localizaron públicamente el cuerpo firmado de NO-2021-16359825, los convenios ejecutados, Res1406 ni las Notas SSFP.
- Se incorporaron cuatro objetos de evidencia DRAFT_NOT_SENT; solicitudes enviadas: 0.
""")

(HERE / "CORRECTION_LOG_V184.md").write_text("""# Registro de correcciones V184

## Corrección 1 · falso negativo del XLSX 2020

El archivo descargado desde el enlace oficial rotulado “Anexo 4.37 · Cuadro de Cuentas Bancarias” contiene internamente `ANEXO 4.36` en la hoja `F21` (`A1:BJ51`). Por lo tanto, la ausencia de MY4002 en ese libro no era evidencia sobre el verdadero cuadro bancario.

## Corrección 2 · cero del programa ≠ cero de la cuenta

El Anexo 4.21 registra en cero los movimientos financieros del programa y señala que el cierre definitivo no estaba certificado. Ese dato no extingue MY4002. El verdadero Anexo 4.37 en la separata PDF conserva la fila MY4002, deja vacíos los campos numéricos 2020 y declara que la cuenta continuaba activa y manejada por FONDyF.

## Estado corregido

Se reemplaza `ZERO_ACCOUNT_EXTINGUISHED` o cualquier lectura equivalente por `ACTIVE_REPORTED_UNDER_FONDYF_2020_BALANCE_NOT_PUBLISHED`. Siguen abiertos: saldo 2020, cuenta/CBU, convenio ejecutado, destino fiduciario, extractos, contraparte, vínculo Res1406, deuda firme, pago, daño y responsabilidad.
""", encoding="utf-8")

(HERE / "README_V184.md").write_text("""# Checkpoint V184

## Hallazgo principal

V184 corrige la transición 2018-2021 de MY4002. La Cuenta de Inversión 2020, Anexo 4.37, identifica `MY 4002 – Fondo Comisión de Compromiso`, BCRA Casa Central, y reproduce como referencia el saldo 2018 de USD 15.182,68 / ARS 569.350,57. Los campos numéricos 2020 están vacíos, pero el comentario basado en `NO-2021-16359825-APN-DNFP#MDP` declara que esa cuenta continuaba activa y manejada por FONDyF.

La misma nota dice que la operatoria del préstamo había finalizado, FONDyF estaba en proceso de liquidación, ya no otorgaba préstamos, los recuperos se encontraban en cuentas BNA y los saldos BCRA se transferían mediante convenios a fondos fiduciarios. Esto abre una ruta documental precisa, pero no demuestra que MY4002 haya sido transferida ni cuál fue su saldo en 2020.

## Corrección metodológica

El XLSX previamente tratado como Anexo 4.37 contiene internamente el Anexo 4.36. Además, el cero del Anexo 4.21 es un cero de movimientos del programa, no un certificado de saldo/cierre de MY4002. Se retrae esa inferencia.

## Consecuencia probatoria

- Continuidad administrativa declarada de MY4002 bajo FONDyF en 2020: probada.
- Saldo 2020, transferencia ejecutada, destino y cierre: no probados.
- Vínculo con Res1406, Macro/Credicoop, deuda firme, pago, daño o responsabilidad: no probados.
- Archivo: 708/708 fuentes catalogadas, físicas y SHA-256 válidas; cinco nuevas.
- Solicitudes enviadas: 0.
""", encoding="utf-8")

(HERE / "VEREDICTO_V184.md").write_text("""# Veredicto V184

MY4002 no puede considerarse extinguida en 2020. La formulación defendible es más precisa: la operatoria del préstamo terminó, pero la cuenta fue reportada como todavía activa y administrada por FONDyF, dentro de un proceso de liquidación y transferencia de saldos por convenios. Como los campos monetarios 2020 están vacíos y no se localizaron nota completa, convenio, extracto ni ledger, no puede afirmarse saldo 2020, transferencia efectiva, pago de una IFI, deuda firme, daño o responsabilidad.
""", encoding="utf-8")

(HERE / "AUDITORIA_V184.md").write_text("""# Auditoría V184

- 708/708 fuentes catalogadas, físicas y SHA-256 válidas; cinco nuevas.
- Dos PDF oficiales inspeccionados integralmente por texto y visualmente en las páginas relevantes.
- Discrepancia reproducida: índice/URL “Anexo 4.37” versus contenido XLSX interno “ANEXO 4.36”.
- Fila MY4002 verificada en CGN PDF 236 y HCDN PDF 1874; campos numéricos 2020 vacíos.
- Estado promovido: `ACTIVE_REPORTED_UNDER_FONDYF_2020_BALANCE_NOT_PUBLISHED`.
- DT1 y SIRECO se incorporan como rutas de pedido, no como prueba histórica.
- Res1406, Notas SSFP, convenio, ledger, pago y daño siguen abiertos; solicitudes enviadas 0.
""", encoding="utf-8")

(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V184_A_V185.md").write_text("""# Handover V184 → V185

## Cerrado

- Corregido el falso negativo del XLSX 2020 mal rotulado.
- Separados el cero de movimientos del programa y el estado de la cuenta MY4002.
- Verificada continuidad administrativa declarada de MY4002 bajo FONDyF en 2020.
- Preservadas copias CGN/HCDN y rutas BCRA DT1/TGN SIRECO; archivo 708/708.

## Prioridad V185

1. Recuperar `NO-2021-16359825-APN-DNFP#MDP` completa, anexos y expediente GDE.
2. Recuperar los Convenios de Transferencias de préstamos y conciliar BCRA→BNA/fondo fiduciario.
3. Pedir historial SIRECO/TGN de MY4002, cuenta/CBU, titularidad y constancia de cierre si existe.
4. Recuperar Res1406, expediente, intimaciones, recursos, dictámenes y decisión final.
5. Recuperar Notas SSFP 04854651 y 7813292/2017 con anexos.
6. Mantener separados cuenta, saldo, transferencia, reclamo, deuda firme, pago, daño y responsabilidad.
""", encoding="utf-8")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V183.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint":"V184", "date":"2026-09-01", "master_catalog_entries":708,
    "physical_local_copies":708, "physical_local_hash_ok":708, "remaining_catalog_physical_or_hash_gaps":0,
    "state":"MY4002_ACTIVE_REPORTED_UNDER_FONDYF_2020_BALANCE_TRANSFER_RES1406_PAYMENT_DAMAGE_OPEN",
    "analytical_promotion":"ADMINISTRATIVE_CONTINUITY_ONLY_NO_2020_BALANCE_EXECUTED_TRANSFER_FIRM_DEBT_PAYMENT_DAMAGE_OR_LIABILITY_V184",
    "my4002_2020_administrative_active_reported":True, "my4002_2020_numeric_fields_blank":True,
    "my4002_2020_balance_proved":False, "my4002_executed_transfer_agreement_located":False,
    "no_2021_16359825_full_body_located":False, "if_2021_57375822_annex_located":True,
    "my4002_counterparty_proved":False, "bid1192_my4002_link_to_res1406_proved":False,
    "mypesii_res1406_full_act_located":False, "mypesii_res1406_payment_proved":False,
    "bid1192_damage_or_appropriation_proved":False, "requests_submitted":0, "responses_received":0,
    "new_v184_sources":5, "v184_pdf_visual_pages":2, "v184_xlsx_label_content_mismatch_corrected":True,
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V184.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

origins = read_csv(ORIGINS)
by_path = {row["path"]:row for row in origins}
for path in iter_files(HIST_ROOT):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"downloaded/preserved V184","note":"official CGN/HCDN/BCRA/TGN source or retrieval metadata"}
for path in HERE.iterdir():
    if path.is_file():
        by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V184","note":"MY4002 FONDyF transition and correction checkpoint"}
for path in (AUDIT/"MASTER_LOCAL_HASH_VALIDATION_V184.csv",AUDIT/"SOURCE_BACKUP_CENSUS_V184.csv",AUDIT/"SOURCE_PRESERVATION_MISSING_V184.csv",AUDIT/"CURRENT_SOURCE_COMPLETENESS_V184.json"):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V184","note":"708-source completeness"}
write_csv(ORIGINS, list(by_path.values()), ["path","origin","note"])

append_once(CYCLE / "TRANSPARENCY_README.md", "## V184 · corrección MY4002/FONDyF", """
## V184 · corrección MY4002/FONDyF

La planilla publicada bajo el nombre Anexo 4.37 contiene internamente Anexo 4.36; se retrae el falso negativo de V182/V183. En la separata PDF auténtica, MY4002 conserva la referencia 2018, tiene campos 2020 vacíos y se declara activa/manejada por FONDyF. El cero del Anexo 4.21 corresponde al programa, no certifica la extinción de la cuenta. No se promueven saldo 2020, transferencia, deuda, pago, daño o responsabilidad. Archivo 708/708; solicitudes 0.
""")

(REPO / "BACKUP_ACTUALIZACION_2026-09-01.md").write_text("""# Backup de actualización · 2026-09-01

- V184; 708/708 fuentes catalogadas, físicas y SHA-256 válidas; cinco nuevas.
- Corrección: el XLSX rotulado Anexo 4.37 contiene internamente Anexo 4.36; su ausencia de MY4002 era un falso negativo.
- Cuenta 2020 PDF 236: MY4002 fue reportada activa y manejada por FONDyF; campos monetarios 2020 vacíos.
- Operatoria BID1192 finalizada no equivale a cuenta cerrada: FONDyF seguía en liquidación y se describen transferencias por convenios aún no recuperados.
- Saldo 2020, convenio, ledger, Res1406, pago y daño abiertos; solicitudes enviadas 0.
""", encoding="utf-8")

(SYNC / "SOURCE_SYNC_REPORT_V184.md").write_text("""# Source sync V184

- Cinco fuentes oficiales nuevas catalogadas: CGN, HCDN/JGM, índice CGN, BCRA/Boletín Oficial y TGN/SIRECO.
- 708/708 fuentes físicas y SHA-256 válidas; brecha 0.
- Metadata del XLSX 2020 corregida para registrar la discrepancia 4.37/4.36.
""", encoding="utf-8")
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V184.csv", [
    {"id":"PS184_01","endpoint":"CGN Cuenta 2020 separata","result":"MY4002 active under FONDyF; 2020 fields blank","preserved":"YES","limit":"balance/transfer open"},
    {"id":"PS184_02","endpoint":"HCDN JGM 0032-JGM-2021","result":"legislative copy and IF identifier","preserved":"YES","limit":"duplicate content, no ledger"},
    {"id":"PS184_03","endpoint":"CGN movement-financial index","result":"4.37 link label versus 4.36 internal content mismatch","preserved":"YES","limit":"server publication defect"},
    {"id":"PS184_04","endpoint":"BCRA B11368 / TGN SIRECO","result":"ledger-code and closure-evidence routes","preserved":"YES","limit":"not execution proof"},
])

(SYNC / "qa_source_sync_v184.py").write_text("""from pathlib import Path
import csv
R=Path(__file__).resolve().parents[5]
rows=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==708 and len({x['id'] for x in rows})==708
print('SOURCE SYNC V184 PASS · 5 new · 708/708')
""", encoding="utf-8")

(HERE / "qa_v184.py").write_text("""from pathlib import Path
import csv,hashlib,json
H=Path(__file__).resolve().parent; R=H.parents[3]; C=R/'research/ciclo_ajuste'; A=C/'source_audit'
def rows(n): return list(csv.DictReader((H/n).open(encoding='utf-8-sig',newline='')))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cat=list(csv.DictReader((R/'data/fuentes/FUENTES.csv').open(encoding='utf-8-sig',newline=''))); assert len(cat)==len({x['id'] for x in cat})==708
for x in cat:
 p=R/x['archivo_local'].lstrip('/'); assert p.is_file() and sha(p)==x['sha256'].lower()
mis=next(x for x in cat if x['id']=='e0_cgn_account2020_bank_accounts_mypes_absence_v182'); assert 'contenido interno Anexo 4.36' in mis['titulo']
aud=list(csv.DictReader((A/'MASTER_LOCAL_HASH_VALIDATION_V184.csv').open(encoding='utf-8-sig',newline=''))); assert len(aud)==708 and all(x['hash_ok']=='True' for x in aud)
co=json.loads((A/'CURRENT_SOURCE_COMPLETENESS_V184.json').read_text(encoding='utf-8-sig')); assert co['checkpoint']=='V184' and co['master_catalog_entries']==708
assert co['my4002_2020_administrative_active_reported'] and co['my4002_2020_numeric_fields_blank'] and not co['my4002_2020_balance_proved']
assert not co['my4002_executed_transfer_agreement_located'] and not co['bid1192_my4002_link_to_res1406_proved'] and not co['bid1192_damage_or_appropriation_proved']
trans=rows('E0_BID1192_CGN_TRANSITION_2018_2021_V184.csv'); assert len(trans)==5 and any(x['bank_account_state']=='MY4002_REPORTED_ACTIVE_UNDER_FONDYF_2020_FIELDS_BLANK' for x in trans)
ladder=rows('E0_BID1192_MY4002_EVIDENCE_LADDER_V184.csv'); assert len(ladder)==8 and any(x['status']=='SUPPORTED_ADMINISTRATIVE_NARRATIVE' for x in ladder)
assert len(rows('V184_SOURCE_BUNDLE.csv'))==5 and len(rows('V184_PDF_VISUAL_CONTROL.csv'))==2 and len(rows('V184_HTML_CONTENT_CONTROL.csv'))==3
obj=rows('E0_V184_REQUEST_OBJECTS.csv'); assert {'RO184_83','RO184_84','RO184_85','RO184_86'}<={x['row_id'] for x in obj}; assert all(x['status']=='DRAFT_NOT_SENT' for x in obj); assert obj==rows('E0_V184_REQUEST_OBJECTS_V184.csv')
panel=rows('FOUR_LEG_PASS_PANEL_V184.csv'); assert len(panel)==45 and sum(x['system_panel_eligible_v72']=='YES_EXACT_Q4_TARGET_BASIS' for x in panel)==34
m=json.loads((H/'MANIFEST_V184.json').read_text(encoding='utf-8-sig')); assert m['checkpoint']=='V184' and m['parent_checkpoint']=='V183' and m['requests_submitted']==0
for x in m['files']:
 p=H/x['path']; assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
print('V184 QA PASS · 708/708 · MY4002_ACTIVE_REPORTED · 2020_BALANCE=OPEN · transfer=OPEN · damage=NO · requests=0')
""", encoding="utf-8")

# Refresco de procedencia tras crear sincronización y QA.
origins = read_csv(ORIGINS)
by_path = {row["path"]:row for row in origins}
for path in iter_files(SYNC):
    by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V184","note":"five-source synchronization"}
for path in HERE.iterdir():
    if path.is_file():
        by_path[path.relative_to(CYCLE).as_posix()] = {"path":path.relative_to(CYCLE).as_posix(),"origin":"generated/updated V184","note":"MY4002 FONDyF transition and correction checkpoint"}
write_csv(ORIGINS, list(by_path.values()), ["path","origin","note"])

(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")

manifest_files = [{"path":path.name,"bytes":path.stat().st_size,"sha256":sha(path)} for path in sorted(HERE.iterdir(), key=lambda item:item.name.casefold()) if path.is_file() and path.name != "MANIFEST_V184.json"]
manifest = {
    "checkpoint":"V184", "parent_checkpoint":"V183", "created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
    "exact_entities":34, "strict_coverage_pct":COVERAGE, "strict_asset_numerator_million_ars":NUMERATOR, "system_assets_million_ars":ASSETS,
    "new_promotions":[], "source_archive":"708/708; 5 new catalogued official sources",
    "historical_finding":"MY4002 reported active under FONDyF in 2020; numeric fields blank; XLSX 4.37/4.36 false negative corrected; transfer/Res1406/payment/damage open",
    "my4002":"ACTIVE_REPORTED_UNDER_FONDYF_2020_BALANCE_NOT_PUBLISHED",
    "my4002_transfer":"GENERAL_PROCESS_REPORTED_EXECUTED_AGREEMENT_NOT_LOCATED",
    "mypesii_res1406":"REPORTED_CONTESTED_FINAL_ACT_OPEN", "closed_network_gate":"NO", "saf355_certifications":"0/5", "executed_historical_bank_rows":"0/10", "requests_submitted":0,
    "files":manifest_files,
}
(HERE / "MANIFEST_V184.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path":path.relative_to(REPO).as_posix(),"bytes":path.stat().st_size,"sha256":sha(path)} for path in iter_files(REPO) if path != global_manifest]
payload = {
    "checkpoint":"V184", "created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
    "strict_coverage_pct":COVERAGE, "exact_entities":34, "closed_network_gate":"NO",
    "source_audit":"708 master; 708 physical SHA-valid",
    "historical_workstream":"MY4002 active under FONDyF reported in 2020; balance/transfer/Res1406/payment/damage open; drafts not sent",
    "file_count_excluding_manifest":len(global_files), "files":global_files,
}
temporary = global_manifest.with_suffix(".json.V184tmp")
temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
temporary.replace(global_manifest)
print("V184 BUILD PASS · catalog=708/708 · new=5 · MY4002_ACTIVE_REPORTED · 2020_BALANCE=OPEN · requests=0")
