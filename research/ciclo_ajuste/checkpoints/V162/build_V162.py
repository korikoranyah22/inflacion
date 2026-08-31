from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, getcontext
from pathlib import Path
import csv
import hashlib
import json
import os


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
V161 = CYCLE / "checkpoints" / "V161"
SYNC = CYCLE / "inputs" / "source_sync" / "v162"
AUDIT = CYCLE / "source_audit"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"
FACTOR = Decimal("1.532908152197492")
NUMERATOR = Decimal("61248719.753")
SYSTEM_ASSETS = Decimal("96697695.5")
getcontext().prec = 120
COVERAGE = NUMERATOR / SYSTEM_ASSETS * Decimal(100)
EXCLUDED_DIRS = {".git", "__pycache__", "tmp", "node_modules"}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows, fields=None):
    fields = fields or (list(rows[0]) if rows else [])
    path.parent.mkdir(parents=True, exist_ok=True)
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


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted((n for n in dirnames if n not in EXCLUDED_DIRS), key=str.casefold)
        for filename in sorted(filenames, key=str.casefold):
            yield Path(dirpath) / filename


def clone_parent():
    excluded = {
        "build_V161.py", "qa_v161.py", "MANIFEST_V161.json", "CURRENT_STATE_V161.csv",
        "FOUR_LEG_PASS_PANEL_V161.csv", "STRICT_Q4_FOUR_LEG_COVERAGE_V161.csv",
        "README_V161.md", "VEREDICTO_V161.md", "AUDITORIA_V161.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V161_A_V162.md",
    }
    for source in sorted(V161.iterdir(), key=lambda p: p.name.casefold()):
        if not source.is_file() or source.name in excluded:
            continue
        target = HERE / source.name.replace("V161", "V162")
        text = source.read_text(encoding="utf-8-sig").replace("V161", "V162")
        target.write_text(text, encoding="utf-8")


clone_parent()

# 1. Preserve and catalogue the newly recovered official Banco Rioja disclosure.
rioja_dm = SYNC / "binaries" / "banco_rioja_disciplina_mercado_9m2023.pdf"
assert rioja_dm.is_file() and rioja_dm.read_bytes().startswith(b"%PDF-")
rioja_hash = sha256(rioja_dm)
assert rioja_hash == "1437b71e7ae282956c756bbd78d62fff2dd24bbdf879ff8eb3f5b2dc076f5357"

catalog = read_csv(CATALOG)
new_source = {
    "id": "banco_rioja_disciplina_mercado_9m2023_v162",
    "tema": "ciclo_ajuste_bancos",
    "institucion": "Banco Rioja S.A.U.",
    "titulo": "Banco Rioja · Disciplina de mercado · 30/09/2023",
    "url_original": "https://bancorioja.com.ar/pdf/disciplina-de-mercado/DM-30-09-23.pdf",
    "archivo_local": "/research/ciclo_ajuste/inputs/source_sync/v162/binaries/banco_rioja_disciplina_mercado_9m2023.pdf",
    "fecha_descarga": "2026-08-31",
    "fecha_publicacion": "",
    "codigo_serie": "",
    "periodo_utilizado": "2023-09",
    "tipo": "PDF oficial · binario preservado",
    "sha256": rioja_hash,
    "nota": "V162: página física 7, Instrumentos de pase 14.191.142k. Reconciliación exacta con raw BCRA Sep entidad 00309: 141144=14.148.116k + 141222=43.026k. Es control de stock; no publica apertura de resultados ni sustituye el flujo.",
}
by_id = {row["id"]: row for row in catalog}
by_id[new_source["id"]] = new_source
catalog = list(by_id.values())
write_csv(CATALOG, catalog, list(new_source))
assert len(catalog) == 578

# 2. Rebuild physical/hash census for every catalogued source.
audit_rows = []
for row in catalog:
    local = REPO / row["archivo_local"].lstrip("/")
    exists = local.is_file()
    actual = sha256(local) if exists else ""
    audit_rows.append({
        "id": row["id"], "archivo_local": row["archivo_local"], "exists": str(exists),
        "sha_catalog": row["sha256"].lower(), "sha_actual": actual,
        "hash_ok": str(exists and bool(row["sha256"]) and actual == row["sha256"].lower()),
    })
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V162.csv", audit_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V162.csv", audit_rows)
missing = [row for row in audit_rows if row["exists"] != "True" or row["hash_ok"] != "True"]
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V162.csv", missing, list(audit_rows[0]))
assert len(audit_rows) == 578 and not missing

# 3. Update entity state without promoting an underidentified four-leg result.
state = read_csv(V161 / "CURRENT_STATE_V161.csv")
state_by_entity = {row["entity"]: row for row in state}
state_by_entity["Banco Rioja S.A.U."].update({
    "fy_status": "OFFICIAL_FY_ANNEXQ_DIRECT_BCRA_ONLY_BINARY_PRESERVED_V161_RAW_INCOME_MISMATCH_158789K_AND_STOCK_MISMATCH_238183K",
    "nine_month_status": "OFFICIAL_DISCIPLINE_MARKET_STOCK_14191142K_BINARY_PRESERVED_V162_EXACT_RAW_141144_PLUS_141222_RECONCILIATION_NO_RESULT_OPENING",
    "q4_four_leg_status": "N/D_STRICT_MISMATCH",
    "strict_panel_status": "PENDING",
    "priority": "HOLD_V162_ISSUER_9M_RESULT_OPENING",
    "next_action": "seek issuer 9M Annex Q/result opening or authenticated audited-to-regulatory reconciliation; Sep stock bridge is exact but stock is not result flow; do not promote",
})
state_by_entity["HSBC Bank Argentina S.A."].update({
    "fy_status": "OFFICIAL_FY_TOTAL_PASS_INCOME_AND_EXPENSE_EXACT_SECTOR_FINANCIERO_UNSPLIT_BINARY_PRESERVED_V161_SUPPLEMENTAL_BUNDLE_EXHAUSTED_V162",
    "nine_month_status": "OFFICIAL_SEPARATED_9M_BASIS_BINARY_PRESERVED_NO_RESULT_OPENING_RAW_TOTAL_RECONCILIATION_SUPPLEMENTAL_BUNDLE_EXHAUSTED_V162",
    "priority": "COUNTERPARTY_SPLIT_LIMIT_V162",
    "next_action": "seek a regulatory or issuer output that expressly separates BCRA from other financial institutions; all eight supplemental CNV attachments were searched without a result-flow split",
})
write_csv(HERE / "CURRENT_STATE_V162.csv", state)

# 4. Banco Rioja exact stock bridge and explicit result mismatches.
q4_raw_income = Decimal("14250267") - Decimal("5712151") * FACTOR
q4_mixed_income = Decimal("14409056") - Decimal("5712151") * FACTOR
q4_expense = Decimal("7844") - Decimal("5117") * FACTOR
recon_fields = ["control_id", "period", "measure", "issuer_value_thousand_ars", "raw_account_set", "raw_values_thousand_ars", "raw_sum_thousand_ars", "difference_issuer_minus_raw", "verdict", "analytic_use"]
recon = [
    {"control_id":"BR162_01","period":"9M-2023","measure":"active_repo_stock","issuer_value_thousand_ars":"14191142","raw_account_set":"141144+141222","raw_values_thousand_ars":"14148116+43026","raw_sum_thousand_ars":"14191142","difference_issuer_minus_raw":"0","verdict":"EXACT_STOCK_RECONCILIATION","analytic_use":"Validates Sep entity/account stock bridge only; not a result-flow allocation."},
    {"control_id":"BR162_02","period":"FY-2023","measure":"active_repo_stock","issuer_value_thousand_ars":"29217148","raw_account_set":"141144+141222(absent)","raw_values_thousand_ars":"28978965+0","raw_sum_thousand_ars":"28978965","difference_issuer_minus_raw":"238183","verdict":"AUDITED_VS_RAW_STOCK_MISMATCH","analytic_use":"Shows a broader closing presentation/timing difference is possible; cause remains unproven."},
    {"control_id":"BR162_03","period":"FY-2023","measure":"repo_income_bcra","issuer_value_thousand_ars":"14409056","raw_account_set":"511108","raw_values_thousand_ars":"14250267","raw_sum_thousand_ars":"14250267","difference_issuer_minus_raw":"158789","verdict":"AUDITED_VS_RAW_RESULT_MISMATCH","analytic_use":"Blocks income-leg promotion."},
    {"control_id":"BR162_04","period":"FY-2023","measure":"repo_expense_bcra","issuer_value_thousand_ars":"7844","raw_account_set":"521108","raw_values_thousand_ars":"7844","raw_sum_thousand_ars":"7844","difference_issuer_minus_raw":"0","verdict":"EXACT_ENTITY_SPECIFIC_FY","analytic_use":"Supports the expense account for Rioja only; insufficient for four-leg promotion."},
    {"control_id":"BR162_05","period":"9M-2023","measure":"repo_income_bcra","issuer_value_thousand_ars":"N/A_NO_ISSUER_RESULT_OPENING","raw_account_set":"511108","raw_values_thousand_ars":"5712151","raw_sum_thousand_ars":"5712151","difference_issuer_minus_raw":"N/A","verdict":"RAW_ONLY","analytic_use":"Cannot substitute stock disclosure for issuer result opening."},
    {"control_id":"BR162_06","period":"9M-2023","measure":"repo_expense_bcra","issuer_value_thousand_ars":"N/A_NO_ISSUER_RESULT_OPENING","raw_account_set":"521108","raw_values_thousand_ars":"5117","raw_sum_thousand_ars":"5117","difference_issuer_minus_raw":"N/A","verdict":"RAW_ONLY_WITH_FY_ENTITY_CROSSCHECK","analytic_use":"Expense mapping is supported at FY but full four-leg gate remains open."},
    {"control_id":"BR162_07","period":"Q4-2023","measure":"repo_income_bcra_raw_to_raw","issuer_value_thousand_ars":"N/A","raw_account_set":"14250267-5712151*1.532908152197492","raw_values_thousand_ars":str(q4_raw_income),"raw_sum_thousand_ars":str(q4_raw_income),"difference_issuer_minus_raw":"N/A","verdict":"ARITHMETIC_ONLY_NOT_PROMOTED","analytic_use":"Regulatory raw-to-raw candidate conflicts with issuer FY presentation."},
    {"control_id":"BR162_08","period":"Q4-2023","measure":"repo_income_bcra_issuer_fy_minus_raw_9m","issuer_value_thousand_ars":str(q4_mixed_income),"raw_account_set":"14409056-5712151*1.532908152197492","raw_values_thousand_ars":str(q4_mixed_income),"raw_sum_thousand_ars":str(q4_mixed_income),"difference_issuer_minus_raw":str(Decimal("158789")),"verdict":"MIXED_PRESENTATION_NOT_PROMOTABLE","analytic_use":"Do not mix audited FY with unmatched regulatory 9M."},
    {"control_id":"BR162_09","period":"Q4-2023","measure":"repo_expense_bcra","issuer_value_thousand_ars":str(q4_expense),"raw_account_set":"7844-5117*1.532908152197492","raw_values_thousand_ars":str(q4_expense),"raw_sum_thousand_ars":str(q4_expense),"difference_issuer_minus_raw":"0","verdict":"EXACT_ARITHMETIC_NOT_PANEL_PROMOTION","analytic_use":"One resolved leg does not satisfy the four-leg gate."},
]
write_csv(HERE / "BANCO_RIOJA_STOCK_AND_RESULT_RECONCILIATION_V162.csv", recon, recon_fields)

(HERE / "BANCO_RIOJA_MISMATCH_ANALYTIC_NOTE_V162.md").write_text(f"""# Banco Rioja: conciliación de stock y límite de resultado V162

## Hallazgo nuevo

La publicación oficial de Disciplina de Mercado al 30/09/2023 informa **14.191.142 miles de pesos** en instrumentos de pase. Ese saldo coincide exactamente con las cuentas crudas de la entidad 00309: `141144 = 14.148.116` más `141222 = 43.026`. Esto valida, para Banco Rioja y septiembre de 2023, la suma capital más interés devengado del stock.

## Qué sigue sin cerrar

El estado anual informa stock activo con Letras de Liquidez del BCRA por **29.217.148**, mientras el archivo regulatorio de diciembre contiene `141144 = 28.978.965` y no registra `141222`: diferencia **238.183**. En resultados, el Anexo Q anual informa ingreso BCRA por **14.409.056**, frente a `511108 = 14.250.267`: diferencia **158.789**. El egreso anual sí concilia: **7.844 = 7.844**.

La coexistencia de una diferencia de stock y otra de resultado vuelve plausible —pero no demuestra— una diferencia de presentación, corte, reexpresión o ajuste entre el estado anual auditado y la salida regulatoria cruda. No identifica cuál causa opera ni autoriza trasladar el diferencial a septiembre.

## Decisión estricta

El Q4 raw-to-raw de ingreso sería **{q4_raw_income}**; mezclar FY auditado con 9M raw daría **{q4_mixed_income}**. La distancia entre ambos es exactamente **158.789**, el desacople anual no explicado. El egreso Q4 aritmético es **{q4_expense}**, pero una pata resuelta no satisface el requisito de cuatro patas. Banco Rioja permanece `N/D_STRICT_MISMATCH`; el stock no se usa como sustituto del flujo.
""", encoding="utf-8")

# 5. Exhaust the non-state HSBC attachments as a documented negative control.
hsbc_supplemental = []
for period in ("hsbc_9m2023", "hsbc_fy2023"):
    for role, filename in (
        ("memoria", "memoria.pdf"),
        ("informe_auditor", "informe_auditor_independiente.pdf"),
        ("informe_fiscalizacion", "informe_comision_fiscalizadora_sindico.pdf"),
        ("resena", "resena_informativa.pdf"),
    ):
        path = CYCLE / "inputs" / "source_sync" / "v161" / "binaries" / "cnv_attachments" / period / filename
        assert path.is_file()
        hsbc_supplemental.append({
            "period": period.replace("hsbc_", ""), "attachment_role": role,
            "path": "/" + path.relative_to(REPO).as_posix(), "sha256": sha256(path),
            "method": "full-document text search plus exact-total search",
            "repo_result_terms_found": "0", "exact_pass_total_hits": "0",
            "bcra_vs_otherfi_flow_split_found": "NO", "decision": "NEGATIVE_CONTROL_KEEP_ND_STRICT",
        })
write_csv(HERE / "HSBC_SUPPLEMENTAL_ATTACHMENT_EXHAUSTION_V162.csv", hsbc_supplemental)
(HERE / "HSBC_SUPPLEMENTAL_ATTACHMENT_EXHAUSTION_V162.md").write_text("""# HSBC: agotamiento de adjuntos complementarios V162

Se buscaron en documento completo las memorias, informes de auditor, informes de fiscalización y reseñas de septiembre y diciembre: ocho adjuntos oficiales CNV, además de los dos estados contables ya analizados. Ninguno publica una apertura de resultados de pases entre BCRA y otras entidades financieras ni reproduce los totales exactos de la Nota 26 como desglose alternativo.

El estado intermedio sí muestra el stock activo de pases —capital más interés devengado—, pero ese saldo no asigna los ingresos y egresos del período. El anual mantiene el rótulo agregado “sector financiero”. La búsqueda complementaria refuerza el control negativo: HSBC sigue `N/D_STRICT`.
""", encoding="utf-8")

# 6. Carry the strict panel forward and add Banco Rioja as an explicit excluded row.
panel = read_csv(V161 / "FOUR_LEG_PASS_PANEL_V161.csv")
for row in panel:
    if row["entity"] == "HSBC Bank Argentina S.A.":
        row["v72_note"] = "V162 negative control: eight supplemental CNV attachments add no BCRA/Other-FI result split; exact totals and repo stock still cannot allocate flows."
panel.append({
    "entity": "Banco Rioja S.A.U.", "basis": "INDIVIDUAL_ENTITY_ISSUER_TARGET", "period": "Q4-2023",
    "income_bcra": "N/D_MISMATCH_RAW_TO_RAW_5494064.165516943874708_VS_MIXED_5652853.165516943874708",
    "expense_bcra": str(q4_expense), "income_otherfi": "0_ISSUER_FY_ONLY_NOT_9M_OPENING", "expense_otherfi": "0_ISSUER_FY_ONLY_NOT_9M_OPENING",
    "net_bcra": "N/D", "net_otherfi": "N/D", "quality": "ISSUER_FY_VS_RAW_MISMATCH_AND_9M_RESULT_OPENING_ABSENT",
    "target_basis_compatible": "YES_BASIS_BUT_NOT_HOMOGENEOUS_RESULT_BRIDGE", "system_panel_eligible_v72": "NO",
    "v72_note": "V162: Sep stock reconciles exactly, but stock is not flow. FY issuer/raw income differs 158,789k; FY/raw stock differs 238,183k. No promotion.",
})
write_csv(HERE / "FOUR_LEG_PASS_PANEL_V162.csv", panel)

coverage = read_csv(V161 / "STRICT_Q4_FOUR_LEG_COVERAGE_V161.csv")
coverage[0]["coverage_set"] = "V162 strict 33-entity set; Banco Rioja and HSBC remain excluded"
coverage[0]["v161_change"] = "V162: no numeric change; Banco Rioja Sep stock bridge exact but result mismatch unresolved; HSBC supplemental bundle exhausted without counterparty split."
write_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V162.csv", coverage)

# 7. Document source bundle, visual controls, and web/public endpoint status.
source_paths = [
    ("RIOJA_9M_DISCIPLINE_MARKET", rioja_dm, new_source["url_original"]),
    ("RIOJA_FY_FINANCIAL_STATEMENT", CYCLE / "inputs/source_sync/v161/binaries/banco_rioja_eeff_fy2023.pdf", "https://bancorioja.com.ar/pdf/EEFF-BR-2023.pdf"),
    ("BCRA_RAW_9M_ARCHIVE", CYCLE / "inputs/bcra/2023-09/informacion_entidades_financieras_open_data/202309d.7z", "OFFICIAL_LOCAL_ARCHIVE_ALREADY_CATALOGUED"),
    ("BCRA_RAW_FY_ARCHIVE", REPO / "data/fuentes/credito_consumo/bcra_entidades/historico_2023_2026/202312d.7z", "OFFICIAL_LOCAL_ARCHIVE_ALREADY_CATALOGUED"),
    ("HSBC_9M_STATE", CYCLE / "inputs/source_sync/v161/binaries/cnv_attachments/hsbc_9m2023/estado_contable.pdf", "https://aif2.cnv.gov.ar/presentations/publicview/7a0d9e04-142e-4b79-b27c-a3bd617334fd"),
    ("HSBC_FY_STATE", CYCLE / "inputs/source_sync/v161/binaries/cnv_attachments/hsbc_fy2023/estado_contable.pdf", "https://aif2.cnv.gov.ar/presentations/publicview/39f37eb9-5637-4cb3-ab6b-715da7830bd1"),
]
bundle = []
for role, path, url in source_paths:
    assert path.is_file()
    bundle.append({"role":role,"path":"/"+path.relative_to(REPO).as_posix(),"url":url,"bytes":str(path.stat().st_size),"sha256":sha256(path),"analytic_use":"Rioja reconciliation or HSBC strict negative control"})
write_csv(HERE / "V162_SOURCE_BUNDLE.csv", bundle)

visual = [
    {"control_id":"PV162_01","artifact":"banco_rioja_eeff_fy2023.pdf","page":"25 / printed 23","method":"Poppler 150 dpi + original-detail visual inspection","target":"FY repo stock and counterparty","result":"PASS_LIMIT","observation":"BCRA LELIQ active repos 29,217,148; no passive repos; stock is not flow."},
    {"control_id":"PV162_02","artifact":"banco_rioja_eeff_fy2023.pdf","page":"79 / printed 77","method":"Poppler 150 dpi + original-detail visual inspection","target":"FY Annex Q result split","result":"PASS","observation":"BCRA repo income 14,409,056 and expense 7,844; other-FI absent."},
    {"control_id":"PV162_03","artifact":"banco_rioja_disciplina_mercado_9m2023.pdf","page":"7","method":"Poppler 150 dpi + original-detail visual inspection","target":"9M repo stock","result":"PASS_LIMIT","observation":"Instrumentos de pase 14,191,142; no result-flow opening."},
    {"control_id":"PV162_04","artifact":"hsbc_9m2023/estado_contable.pdf","page":"29","method":"Poppler 150 dpi + original-detail visual inspection","target":"9M repo stock","result":"PASS_LIMIT","observation":"Capital 182,670,273 plus accrued interest 1,111,036 = 183,781,309; no result split."},
    {"control_id":"PV162_05","artifact":"hsbc_fy2023/estado_contable.pdf","page":"36","method":"Poppler 150 dpi + original-detail visual inspection","target":"FY pass results","result":"PASS_LIMIT","observation":"Income 204,724,664 and expense 542,204, both sector financiero unsplit."},
]
write_csv(HERE / "V162_PDF_VISUAL_CONTROL.csv", visual)

endpoint_rows = [
    {"control_id":"WEB162_01","institution":"Banco Rioja","url":"https://bancorioja.com.ar/institucional/disciplina-de-mercado","public_fact":"Official index exposes the 30/09/2023 disclosure","local_status":"INDEX_URL_RECORDED_BINARY_ARCHIVED","decision":"USE"},
    {"control_id":"WEB162_02","institution":"Banco Rioja","url":new_source["url_original"],"public_fact":"Official 9M disclosure, 9 pages","local_status":"ARCHIVED_SHA256_VALID","decision":"USE_STOCK_CONTROL_ONLY"},
    {"control_id":"WEB162_03","institution":"BCRA","url":"https://www.bcra.gob.ar/archivos/Pdfs/comytexord/A6358.pdf","public_fact":"Plan de Cuentas effective 2018 defines 141144 and 141222 as active repo stock with BCRA","local_status":"LOCAL_BINARY_PENDING_SERVER_RESET; operative labels also preserved inside official 2023 raw archives","decision":"PUBLIC_CORROBORATION_NOT_PROMOTION_BASIS"},
    {"control_id":"WEB162_04","institution":"BCRA","url":"https://www.bcra.gob.ar/archivos/Pdfs/comytexord/A6402.pdf","public_fact":"Plan de Cuentas effective 2018 defines 511108 as interest on active repos with BCRA and 521108 as interest on passive repos with BCRA","local_status":"LOCAL_BINARY_PENDING_SERVER_RESET; operative labels also preserved inside official 2023 raw archives","decision":"PUBLIC_CORROBORATION_NOT_PROMOTION_BASIS"},
]
write_csv(HERE / "V162_PUBLIC_SEARCH_LOG.csv", endpoint_rows)

# 8. Source-sync control files; completeness remains explicitly catalog-relative.
sync_manifest = [{
    "role":"OFFICIAL_DISCLOSURE_BINARY", "relative_path":"/"+rioja_dm.relative_to(REPO).as_posix(),
    "source_url":new_source["url_original"], "size_bytes":str(rioja_dm.stat().st_size),
    "sha256":rioja_hash, "format_verification":"PDF_MAGIC_VALID_PAGES_9_VISUALLY_INSPECTED_PAGE_7",
}]
write_csv(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V162.csv", sync_manifest)
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V162.csv", endpoint_rows)
(SYNC / "SOURCE_SYNC_REPORT_V162.md").write_text("""# Sincronización incremental de fuentes — V162

- Catálogo maestro: **578/578** copias locales con SHA-256 válido; brecha catalogada: **0**.
- Fuente nueva: Disciplina de Mercado de Banco Rioja al 30/09/2023, PDF oficial de 9 páginas.
- Uso: control de stock exacto; no sustituye una apertura de resultados.
- Dos comunicaciones del Plan de Cuentas del BCRA fueron verificadas en el sitio oficial, pero el servidor reinició las descargas directas. No se las incorporó al catálogo ni se simuló una copia local. Sus rótulos operativos ya están preservados en los archivos oficiales BCRA 2023; los dos binarios quedan en cola de recuperación.
- Ninguna solicitud fue enviada; seis borradores siguen `DRAFT_NOT_SENT`.
""", encoding="utf-8")

# 9. Human-readable checkpoint.
(HERE / "README_V162.md").write_text(f"""# Checkpoint V162

- Archivo fuente catalogado: 578/578 copias locales con hash válido.
- Banco Rioja: stock 9M oficial de 14.191.142k reconciliado exactamente; resultado 9M no abierto.
- Banco Rioja: diferencias FY issuer/raw de 158.789k en ingreso y 238.183k en stock; sigue N/D_STRICT_MISMATCH.
- HSBC: ocho adjuntos complementarios agotados sin separación BCRA/otras entidades; sigue N/D_STRICT.
- Panel sin cambio: 33 entidades exactas; cobertura {COVERAGE}%.
- No se usa stock como flujo, no se mezclan presentaciones incompatibles y no se generalizan códigos.
- SAF355 0/5; ejecución histórica 0/10; seis borradores no enviados.
""", encoding="utf-8")
(HERE / "VEREDICTO_V162.md").write_text(f"""# Veredicto V162

V162 mejora la certeza sin inflar la cobertura. La nueva publicación oficial de Banco Rioja prueba que el stock de septiembre coincide exactamente con capital más interés devengado en la salida BCRA. A la vez, el cierre anual mantiene dos diferencias no explicadas frente al raw: 238.183k en stock y 158.789k en ingreso. Esto impide construir un Q4 homogéneo de ingreso y confirma que un saldo de balance no puede reemplazar un flujo de resultados. HSBC tampoco ofrece la separación de contraparte en sus ocho adjuntos complementarios. Ambos permanecen excluidos. El panel conserva 33 entidades y {COVERAGE}% de activos.
""", encoding="utf-8")
(HERE / "AUDITORIA_V162.md").write_text(f"""# Auditoría V162

- Catálogo/copia/hash: 578/578; huecos catalogados: 0.
- Fuente nueva: 1 PDF oficial, 212.506 bytes, 9 páginas, SHA-256 {rioja_hash}.
- Banco Rioja: 9 controles contables/aritméticos; 1 conciliación de stock 9M exacta, 2 diferencias FY explícitas, sin promoción.
- HSBC: 8 adjuntos complementarios, 0 aperturas de flujo BCRA/otras entidades.
- Control visual: 5 páginas relevantes inspeccionadas.
- Plan BCRA: 2 endpoints oficiales registrados; copia binaria pendiente por reinicio del servidor, sin falsa marca de preservación.
- Panel: 33 exactas, {COVERAGE}%; SAF355 0/5; ejecución 0/10; pedidos/respuestas 0/0.
""", encoding="utf-8")
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V162_A_V163.md").write_text(f"""# Handover V162 → V163

## Cerrado en V162

- Banco Rioja: 9M stock exacto contra raw; FY stock +238.183k e ingreso +158.789k contra raw; N/D_STRICT_MISMATCH.
- HSBC: ocho adjuntos complementarios sin apertura; N/D_STRICT.
- Archivo catalogado: 578/578 local y hash-válido.
- Panel: 33 entidades; cobertura {COVERAGE}%.

## Prioridad V163

1. Buscar Banco Rioja 9M Anexo Q/apertura de resultados o conciliación auditada-regulatoria autenticada.
2. Recuperar localmente A6358/A6402 del BCRA cuando el endpoint deje de reiniciar conexiones; hasta entonces no marcarlas preservadas.
3. Revisar los 24 adjuntos CNV restantes por aperturas nuevas, manteniendo límites entidad-año-base.
4. Retomar Plan SIGEN 2009, Nota 3672/09 y crosswalk UAI-entidad-proyecto-informe.
5. Mantener SAF355 0/5, ejecución 0/10 y seis DRAFT_NOT_SENT hasta evidencia primaria o autorización de envío.
""", encoding="utf-8")

source_refs = HERE / "SOURCE_REFERENCES_V162.md"
with source_refs.open("a", encoding="utf-8") as handle:
    handle.write(f"\n- `banco_rioja_disciplina_mercado_9m2023_v162` · Banco Rioja · Disciplina de mercado 30/09/2023 · {new_source['url_original']} · `{new_source['archivo_local']}` · `{rioja_hash}`\n")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V161.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint":"V162", "date":"2026-08-31", "master_catalog_entries":578,
    "physical_local_copies":578, "physical_local_hash_ok":578,
    "remaining_catalog_physical_or_hash_gaps":0,
    "state":"SOURCE_ARCHIVE_CATALOG_COMPLETE_RIOJA_STOCK_BRIDGE_EXACT_RESULT_MISMATCH_OPEN_HSBC_SUPPLEMENTAL_EXHAUSTED",
    "analytical_promotion":"NONE_V162_NEGATIVE_CONTROL_AND_RECONCILIATION_ONLY",
    "exact_entities":33, "strict_asset_numerator_million_ars":str(NUMERATOR),
    "system_assets_million_ars":str(SYSTEM_ASSETS), "strict_coverage_pct":str(COVERAGE),
    "strict_coverage_increment_v161_pp":"0", "request_drafts_status":"DRAFT_NOT_SENT",
    "requests_submitted":0, "responses_received":0, "saf355_certifications_located":0,
    "executed_historical_bank_rows_confirmed":0,
    "discovered_official_binary_recovery_queue":2,
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V162.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

# Keep provenance explicit for every new V162 artifact.
origin_rows = read_csv(ORIGINS)
origin_by_path = {row["path"]: row for row in origin_rows}
for path in iter_files(SYNC):
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path":rel,"origin":"generated/recovered V162","note":"Banco Rioja incremental source sync or V162 source-control artifact"}
for path in sorted(HERE.iterdir(), key=lambda p:p.name.casefold()):
    if path.is_file():
        rel = path.relative_to(CYCLE).as_posix()
        origin_by_path[rel] = {"path":rel,"origin":"generated/updated V162","note":"V162 analytical checkpoint: Rioja reconciliation and HSBC negative control"}
for path in [
    AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V162.csv", AUDIT / "SOURCE_BACKUP_CENSUS_V162.csv",
    AUDIT / "SOURCE_PRESERVATION_MISSING_V162.csv", AUDIT / "CURRENT_SOURCE_COMPLETENESS_V162.json",
]:
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path":rel,"origin":"generated/updated V162","note":"578-source physical/hash completeness control"}
write_csv(ORIGINS, list(origin_by_path.values()), ["path","origin","note"])

transparency = CYCLE / "TRANSPARENCY_README.md"
transparency_text = transparency.read_text(encoding="utf-8-sig")
if "## V162 · Banco Rioja" not in transparency_text:
    transparency_text += """

## V162 · Banco Rioja y control negativo HSBC

Se preservó la Disciplina de Mercado de Banco Rioja al 30/09/2023 y se obtuvo una conciliación exacta del stock con capital más interés devengado en el raw BCRA. La apertura de resultados 9M no aparece y el cierre anual difiere del raw en stock e ingreso; por eso no hay promoción. Los ocho adjuntos complementarios HSBC tampoco separan BCRA de otras entidades. El archivo catalogado queda 578/578; dos comunicaciones BCRA verificadas públicamente permanecen en cola binaria por reinicios del servidor.
"""
    transparency.write_text(transparency_text, encoding="utf-8")

backup = REPO / "BACKUP_ACTUALIZACION_2026-08-31.md"
backup.write_text(f"""# Backup de actualización · 2026-08-31

- Checkpoint: V162.
- Fuentes catalogadas: 578/578 local y SHA-válido.
- Banco Rioja: stock 9M exacto; diferencias FY raw/issuer preservadas; sin promoción.
- HSBC: adjuntos complementarios agotados; sin promoción.
- Panel: 33 entidades, {COVERAGE}% de activos.
- Solicitudes: 0 enviadas; seis borradores DRAFT_NOT_SENT.
""", encoding="utf-8")

def tree(root: Path):
    lines=[]
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted((n for n in dirnames if n not in EXCLUDED_DIRS), key=str.casefold)
        base=Path(dirpath)
        lines.extend((base/n).relative_to(root).as_posix()+"/" for n in dirnames)
        lines.extend((base/n).relative_to(root).as_posix() for n in sorted(filenames,key=str.casefold))
    return "\n".join(lines)+"\n"

(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")

files = [{"path":p.name,"bytes":p.stat().st_size,"sha256":sha256(p)} for p in sorted(HERE.iterdir(),key=lambda x:x.name.casefold()) if p.is_file() and p.name!="MANIFEST_V162.json"]
manifest = {
    "checkpoint":"V162","parent_checkpoint":"V161","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
    "exact_entities":33,"strict_coverage_pct":str(COVERAGE),"strict_asset_numerator_million_ars":str(NUMERATOR),"system_assets_million_ars":str(SYSTEM_ASSETS),
    "new_promotions":[],"negative_controls":["Banco Rioja S.A.U. N/D_STRICT_MISMATCH","HSBC Bank Argentina S.A. N/D_STRICT"],
    "source_archive":"578/578 catalogued physical SHA-valid; 2 discovered BCRA binaries pending server recovery",
    "closed_network_gate":"NO","saf355_certifications":"0/5","executed_historical_bank_rows":"0/10","requests_submitted":0,"files":files,
}
(HERE / "MANIFEST_V162.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

global_manifest=CYCLE/"MANIFEST_SHA256.json"
global_files=[{"path":p.relative_to(REPO).as_posix(),"bytes":p.stat().st_size,"sha256":sha256(p)} for p in iter_files(REPO) if p!=global_manifest]
global_payload={
    "checkpoint":"V162","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
    "strict_coverage_pct":str(COVERAGE),"exact_entities":33,"closed_network_gate":"NO",
    "source_audit":"578 master; 578 physical SHA-valid; Banco Rioja result mismatch and HSBC counterparty split remain open; 2 discovered BCRA binaries queued",
    "historical_workstream":"Plan SIGEN 2009, Nota 3672/09, SAF355 and bank execution remain open; six drafts not sent",
    "file_count_excluding_manifest":len(global_files),"files":global_files,
}
tmp=global_manifest.with_suffix(".json.V162tmp")
tmp.write_text(json.dumps(global_payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
tmp.replace(global_manifest)

print(f"V162 BUILD PASS · exact=33 · coverage={COVERAGE} · catalog=578/578 · promotions=0")
