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
V162 = CYCLE / "checkpoints" / "V162"
SYNC = CYCLE / "inputs" / "source_sync" / "v163"
AUDIT = CYCLE / "source_audit"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"
FACTOR = Decimal("1.532908152197492")
NUMERATOR = Decimal("61248719.753")
SYSTEM_ASSETS = Decimal("96697695.5")
RIOJA_ASSETS = Decimal("96882.462")
getcontext().prec = 120
COVERAGE = NUMERATOR / SYSTEM_ASSETS * Decimal(100)
COUNTERFACTUAL_COVERAGE = (NUMERATOR + RIOJA_ASSETS) / SYSTEM_ASSETS * Decimal(100)
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
        "build_V162.py", "qa_v162.py", "MANIFEST_V162.json", "CURRENT_STATE_V162.csv",
        "FOUR_LEG_PASS_PANEL_V162.csv", "STRICT_Q4_FOUR_LEG_COVERAGE_V162.csv",
        "README_V162.md", "VEREDICTO_V162.md", "AUDITORIA_V162.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V162_A_V163.md",
        "BANCO_RIOJA_MISMATCH_ANALYTIC_NOTE_V162.md",
        "BANCO_RIOJA_STOCK_AND_RESULT_RECONCILIATION_V162.csv",
        "V162_PDF_VISUAL_CONTROL.csv", "V162_PUBLIC_SEARCH_LOG.csv", "V162_SOURCE_BUNDLE.csv",
    }
    for source in sorted(V162.iterdir(), key=lambda p: p.name.casefold()):
        if not source.is_file() or source.name in excluded:
            continue
        target = HERE / source.name.replace("V162", "V163")
        text = source.read_text(encoding="utf-8-sig").replace("V162", "V163")
        target.write_text(text, encoding="utf-8")


clone_parent()

# 1. Preserve and catalogue the official 30/09/2024 negative comparator.
rioja_dm24 = SYNC / "binaries" / "banco_rioja_disciplina_mercado_9m2024.pdf"
assert rioja_dm24.is_file() and rioja_dm24.read_bytes().startswith(b"%PDF-")
rioja_dm24_hash = sha256(rioja_dm24)
assert rioja_dm24_hash == "e54b65196abfbb1801667d22dca54dd383b35ee81b772d3489d82ce0d6fb2f27"
assert rioja_dm24.stat().st_size == 351576

catalog = read_csv(CATALOG)
fields = list(catalog[0])
new_source = {
    "id": "banco_rioja_disciplina_mercado_9m2024_v163",
    "tema": "ciclo_ajuste_bancos",
    "institucion": "Banco Rioja S.A.U.",
    "titulo": "Banco Rioja · Disciplina de mercado · 30/09/2024",
    "url_original": "https://bancorioja.com.ar/pdf/disciplina-de-mercado/DM-30-09-24.pdf",
    "archivo_local": "/research/ciclo_ajuste/inputs/source_sync/v163/binaries/banco_rioja_disciplina_mercado_9m2024.pdf",
    "fecha_descarga": "2026-08-31",
    "fecha_publicacion": "2024-12-05",
    "codigo_serie": "",
    "periodo_utilizado": "2024-09",
    "tipo": "PDF oficial · binario preservado",
    "sha256": rioja_dm24_hash,
    "nota": "V163: página física 7, Operaciones de pase y cauciones 0 al 30/09/2024. Control temporal negativo; no contiene comparativo de resultados 2023 ni resuelve el puente FY/9M de 2023.",
}
by_id = {row["id"]: row for row in catalog}
by_id[new_source["id"]] = new_source
catalog = list(by_id.values())
write_csv(CATALOG, catalog, fields)
assert len(catalog) == 579

# 2. Rebuild catalog-relative preservation audit.
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
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V163.csv", audit_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V163.csv", audit_rows)
missing = [row for row in audit_rows if row["exists"] != "True" or row["hash_ok"] != "True"]
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V163.csv", missing, list(audit_rows[0]))
assert len(audit_rows) == 579 and not missing

# 3. Correct V162's December extraction explicitly; do not promote the entity.
state = read_csv(V162 / "CURRENT_STATE_V162.csv")
state_by_entity = {row["entity"]: row for row in state}
state_by_entity["Banco Rioja S.A.U."].update({
    "fy_status": "OFFICIAL_FY_ANNEXQ_DIRECT_BCRA_ONLY_BINARY_PRESERVED_V161_RAW_INCOME_AND_STOCK_DUAL_RESIDUAL_158789K_V163_CORRECTED",
    "nine_month_status": "OFFICIAL_DISCIPLINE_MARKET_STOCK_14191142K_BINARY_PRESERVED_V162_EXACT_RAW_141144_PLUS_141222_NO_RESULT_OPENING_DM2024_NEGATIVE_COMPARATOR_PRESERVED_V163",
    "q4_four_leg_status": "N/D_STRICT_ADJUSTING_ENTRY_UNAUTHENTICATED",
    "strict_panel_status": "PENDING",
    "priority": "HOLD_V163_AUTHENTICATED_CLOSING_ENTRY_OR_9M_RESULT_OPENING",
    "next_action": "obtain issuer 9M-2023 Annex Q/result opening or an authenticated audited-to-regulatory closing reconciliation; V163 proves equal 158789k stock/income residuals but the single adjusting-entry explanation remains a hypothesis",
})
state_by_entity["HSBC Bank Argentina S.A."].update({
    "fy_status": state_by_entity["HSBC Bank Argentina S.A."]["fy_status"].replace("V162", "V163_INHERITED_FROM_V162"),
    "nine_month_status": state_by_entity["HSBC Bank Argentina S.A."]["nine_month_status"].replace("V162", "V163_INHERITED_FROM_V162"),
    "priority": "COUNTERPARTY_SPLIT_LIMIT_V163_INHERITED",
})
write_csv(HERE / "CURRENT_STATE_V163.csv", state)

raw_stock_sep = Decimal("14148116") + Decimal("43026")
raw_stock_fy = Decimal("28978965") + Decimal("79394")
issuer_stock_fy = Decimal("29217148")
raw_income_fy = Decimal("14250267")
issuer_income_fy = Decimal("14409056")
dual_residual = Decimal("158789")
q4_raw_income = raw_income_fy - Decimal("5712151") * FACTOR
q4_adjusted_income = issuer_income_fy - Decimal("5712151") * FACTOR
q4_expense = Decimal("7844") - Decimal("5117") * FACTOR
assert raw_stock_sep == Decimal("14191142")
assert issuer_stock_fy - raw_stock_fy == dual_residual
assert issuer_income_fy - raw_income_fy == dual_residual
assert q4_adjusted_income - q4_raw_income == dual_residual

recon_fields = ["control_id", "period", "measure", "issuer_value_thousand_ars", "raw_account_set", "raw_values_thousand_ars", "raw_sum_thousand_ars", "difference_issuer_minus_raw", "verdict", "analytic_use"]
recon = [
    {"control_id":"BR163_01","period":"9M-2023","measure":"active_repo_stock","issuer_value_thousand_ars":"14191142","raw_account_set":"141144+141222","raw_values_thousand_ars":"14148116+43026","raw_sum_thousand_ars":"14191142","difference_issuer_minus_raw":"0","verdict":"EXACT_STOCK_RECONCILIATION","analytic_use":"Validates September capital-plus-accrued-interest stock; not a result-flow allocation."},
    {"control_id":"BR163_02","period":"FY-2023","measure":"active_repo_stock","issuer_value_thousand_ars":"29217148","raw_account_set":"141144+141222","raw_values_thousand_ars":"28978965+79394","raw_sum_thousand_ars":"29058359","difference_issuer_minus_raw":"158789","verdict":"EXACT_DUAL_SIDED_RESIDUAL","analytic_use":"Corrects V162: 141222 exists. The 238183 figure was only the gap against capital, not against total raw stock."},
    {"control_id":"BR163_03","period":"FY-2023","measure":"repo_income_bcra","issuer_value_thousand_ars":"14409056","raw_account_set":"511108","raw_values_thousand_ars":"14250267","raw_sum_thousand_ars":"14250267","difference_issuer_minus_raw":"158789","verdict":"EXACT_DUAL_SIDED_RESIDUAL","analytic_use":"Same residual as the asset-side stock bridge; supports but does not authenticate a closing entry."},
    {"control_id":"BR163_04","period":"FY-2023","measure":"repo_expense_bcra","issuer_value_thousand_ars":"7844","raw_account_set":"521108","raw_values_thousand_ars":"7844","raw_sum_thousand_ars":"7844","difference_issuer_minus_raw":"0","verdict":"EXACT_ENTITY_SPECIFIC_FY","analytic_use":"Expense leg reconciles."},
    {"control_id":"BR163_05","period":"Q4-2023","measure":"repo_income_bcra_raw_to_raw","issuer_value_thousand_ars":"N/A","raw_account_set":"14250267-5712151*1.532908152197492","raw_values_thousand_ars":str(q4_raw_income),"raw_sum_thousand_ars":str(q4_raw_income),"difference_issuer_minus_raw":"N/A","verdict":"ARITHMETIC_ONLY_NOT_PROMOTED","analytic_use":"Homogeneous regulatory candidate; not issuer-authenticated at 9M."},
    {"control_id":"BR163_06","period":"Q4-2023","measure":"repo_income_bcra_adjusted_closing_hypothesis","issuer_value_thousand_ars":str(q4_adjusted_income),"raw_account_set":"14409056-5712151*1.532908152197492","raw_values_thousand_ars":str(q4_adjusted_income),"raw_sum_thousand_ars":str(q4_adjusted_income),"difference_issuer_minus_raw":"158789","verdict":"SINGLE_ADJUSTING_ENTRY_HYPOTHESIS_UNAUTHENTICATED","analytic_use":"Upper scenario if the equal debit/credit residual is a closing accrual; not panel evidence."},
    {"control_id":"BR163_07","period":"Q4-2023","measure":"repo_expense_bcra","issuer_value_thousand_ars":str(q4_expense),"raw_account_set":"7844-5117*1.532908152197492","raw_values_thousand_ars":str(q4_expense),"raw_sum_thousand_ars":str(q4_expense),"difference_issuer_minus_raw":"0","verdict":"EXACT_ARITHMETIC_NOT_PANEL_PROMOTION","analytic_use":"One resolved leg does not satisfy the four-leg gate."},
    {"control_id":"BR163_08","period":"9M-2024","measure":"active_repo_stock","issuer_value_thousand_ars":"0","raw_account_set":"N/A_NOT_USED","raw_values_thousand_ars":"N/A","raw_sum_thousand_ars":"N/A","difference_issuer_minus_raw":"N/A","verdict":"OFFICIAL_NEGATIVE_TEMPORAL_COMPARATOR","analytic_use":"Shows zero repo stock a year later; no comparative 2023 result opening."},
]
write_csv(HERE / "BANCO_RIOJA_STOCK_AND_RESULT_RECONCILIATION_V163.csv", recon, recon_fields)
write_csv(HERE / "BANCO_RIOJA_DUAL_RESIDUAL_RECONCILIATION_V163.csv", recon[1:4], recon_fields)

raw_rows = [
    {"period":"2023-09","entity_code":"00309","account":"141144","side":"DEBIT","value_thousand_ars":"14148116","description":"Deudores financieros por pases activos con el BCRA - capital","source_member":"Entfin/Tec_Cont/baldet/00309.txt"},
    {"period":"2023-09","entity_code":"00309","account":"141222","side":"DEBIT","value_thousand_ars":"43026","description":"Intereses devengados a cobrar por pases activos con el BCRA","source_member":"Entfin/Tec_Cont/baldet/00309.txt"},
    {"period":"2023-09","entity_code":"00309","account":"511108","side":"CREDIT","value_thousand_ars":"5712151","description":"Intereses por pases activos con el BCRA","source_member":"Entfin/Tec_Cont/baldet/00309.txt"},
    {"period":"2023-09","entity_code":"00309","account":"521108","side":"DEBIT","value_thousand_ars":"5117","description":"Intereses por pases pasivos con el BCRA","source_member":"Entfin/Tec_Cont/baldet/00309.txt"},
    {"period":"2023-12","entity_code":"00309","account":"141144","side":"DEBIT","value_thousand_ars":"28978965","description":"Deudores financieros por pases activos con el BCRA - capital","source_member":"Entfin/Tec_Cont/baldet/00309.txt"},
    {"period":"2023-12","entity_code":"00309","account":"141222","side":"DEBIT","value_thousand_ars":"79394","description":"Intereses devengados a cobrar por pases activos con el BCRA","source_member":"Entfin/Tec_Cont/baldet/00309.txt"},
    {"period":"2023-12","entity_code":"00309","account":"511108","side":"CREDIT","value_thousand_ars":"14250267","description":"Intereses por pases activos con el BCRA","source_member":"Entfin/Tec_Cont/baldet/00309.txt"},
    {"period":"2023-12","entity_code":"00309","account":"521108","side":"DEBIT","value_thousand_ars":"7844","description":"Intereses por pases pasivos con el BCRA","source_member":"Entfin/Tec_Cont/baldet/00309.txt"},
]
write_csv(HERE / "BANCO_RIOJA_RAW_ACCOUNT_EXTRACTION_V163.csv", raw_rows)

scenario_rows = [
    {"scenario":"REGULATORY_RAW_TO_RAW","q4_income_bcra_thousand_ars":str(q4_raw_income),"q4_expense_bcra_thousand_ars":str(q4_expense),"adjustment_thousand_ars":"0","panel_use":"NO","reason":"Issuer 9M result opening absent; raw codes are entity-specific candidates only."},
    {"scenario":"AUDITED_CLOSING_ADJUSTMENT_HYPOTHESIS","q4_income_bcra_thousand_ars":str(q4_adjusted_income),"q4_expense_bcra_thousand_ars":str(q4_expense),"adjustment_thousand_ars":"158789","panel_use":"NO","reason":"Equal asset/income residual suggests one closing entry but no authenticated journal or reconciliation was found."},
    {"scenario":"COUNTERFACTUAL_COVERAGE_IF_EVENTUALLY_PROMOTED","q4_income_bcra_thousand_ars":"N/A","q4_expense_bcra_thousand_ars":"N/A","adjustment_thousand_ars":"N/A","panel_use":"COUNTERFACTUAL_ONLY","reason":f"Coverage would be {COUNTERFACTUAL_COVERAGE}%, an increment of {COUNTERFACTUAL_COVERAGE-COVERAGE} pp; strict coverage remains {COVERAGE}%."},
]
write_csv(HERE / "BANCO_RIOJA_Q4_SCENARIO_BOUND_V163.csv", scenario_rows)

(HERE / "CORRECTION_LOG_V163.md").write_text("""# Fe de erratas y corrección metodológica V163

V162 afirmó que la cuenta `141222` no aparecía en diciembre de 2023 y calculó una diferencia de stock de **238.183 miles de pesos** contra `141144` solamente. La extracción completa de `00309.txt` demuestra que `141222 = 79.394` sí existe. Por lo tanto:

- stock crudo de diciembre: `28.978.965 + 79.394 = 29.058.359`;
- stock auditado: `29.217.148`;
- diferencia correcta de stock: **158.789**;
- ingreso crudo `511108`: `14.250.267`;
- ingreso auditado: `14.409.056`;
- diferencia de ingreso: **158.789**.

Los **238.183** de V162 eran la distancia entre el stock auditado y el capital crudo aislado, no una conciliación completa de stock. Los controles `BR162_02`, el README y el veredicto V162 quedan supersedidos por V163. Se conserva V162 como registro histórico del error; no se reescribe retroactivamente.

La igualdad de ambos residuos hace algebraicamente coherente un único asiento de cierre —débito al activo de pases y crédito al ingreso por 158.789—, pero no prueba que ese asiento haya existido. Sin diario, papel de trabajo, conciliación firmada o apertura de resultados 9M del emisor, la causa sigue sin autenticar y no hay promoción.
""", encoding="utf-8")

(HERE / "BANCO_RIOJA_ADJUSTING_ENTRY_HYPOTHESIS_V163.md").write_text(f"""# Banco Rioja: hipótesis de asiento de cierre V163

## Hecho demostrado

La salida regulatoria de diciembre contiene `141144 = 28.978.965`, `141222 = 79.394`, `511108 = 14.250.267` y `521108 = 7.844` miles de pesos. El estado anual auditado informa stock de pases activos con BCRA por `29.217.148`, ingreso por `14.409.056` y egreso por `7.844`. El residuo auditado menos regulatorio es **158.789** tanto en el activo como en el ingreso; el egreso concilia exactamente.

## Inferencia contable acotada

Una explicación mínima compatible con la ecuación es un asiento de cierre por 158.789:

    Debe: activo por operaciones de pase       158.789
    Haber: ingreso por operaciones de pase     158.789

La política contable anual indica que la diferencia de compra y venta de los pases se devenga durante la operación por el método de la tasa de interés efectiva y se imputa a resultados. Además, el archivo regulatorio fue fechado antes de la firma del informe de auditoría. Ambas circunstancias vuelven plausible un ajuste de cierre o auditoría, pero no identifican su causa ni prueban el asiento.

## Límite probatorio y decisión

No apareció un comprobante, diario, papel de trabajo, nota de ajuste ni apertura de resultados 9M del emisor. Tampoco corresponde atribuir el residuo a reexpresión por inflación: la política anual dice que las partidas monetarias no se reexpresan al cierre. Los dos valores Q4 admisibles como escenarios son **{q4_raw_income}** raw-to-raw y **{q4_adjusted_income}** si el ajuste se autentica. La diferencia es exactamente 158.789. Banco Rioja queda `N/D_STRICT_ADJUSTING_ENTRY_UNAUTHENTICATED`.
""", encoding="utf-8")

(HERE / "BANCO_RIOJA_MISMATCH_ANALYTIC_NOTE_V163.md").write_text(f"""# Banco Rioja: conciliación corregida y límite V163

V163 corrige la extracción de diciembre: `141222 = 79.394` estaba presente. Al sumar capital e interés devengado, el stock crudo asciende a `29.058.359` y queda **158.789** por debajo del stock auditado de `29.217.148`. Ese residuo coincide exactamente con la diferencia entre ingreso auditado (`14.409.056`) e ingreso crudo (`14.250.267`).

La coincidencia en las dos caras es evidencia estructural mucho más fuerte que las diferencias independientes descriptas en V162. Permite formular una hipótesis de asiento balanceado por 158.789, pero no reemplaza su autenticación. El ingreso Q4 queda acotado entre **{q4_raw_income}** y **{q4_adjusted_income}** miles de pesos según se excluya o incluya el ajuste. El egreso Q4 es **{q4_expense}**. Sin apertura 9M del emisor o conciliación de cierre firmada, no se promueve.
""", encoding="utf-8")

# 4. Keep the strict panel unchanged and expose the counterfactual separately.
panel = read_csv(V162 / "FOUR_LEG_PASS_PANEL_V162.csv")
for row in panel:
    if row["entity"] == "Banco Rioja S.A.U.":
        row.update({
            "income_bcra": f"N/D_BOUND_RAW_{q4_raw_income}_TO_ADJUSTED_{q4_adjusted_income}",
            "expense_bcra": str(q4_expense),
            "income_otherfi": "0_ISSUER_FY_ONLY_NOT_9M_OPENING",
            "expense_otherfi": "0_ISSUER_FY_ONLY_NOT_9M_OPENING",
            "net_bcra": "N/D", "net_otherfi": "N/D",
            "quality": "EXACT_DUAL_RESIDUAL_158789K_BUT_ADJUSTING_ENTRY_UNAUTHENTICATED",
            "target_basis_compatible": "YES_BASIS_BUT_9M_RESULT_OPENING_OR_CLOSING_RECONCILIATION_ABSENT",
            "system_panel_eligible_v72": "NO",
            "v72_note": "V163 correction: Dec 141222=79,394k. Stock and income each have the same 158,789k issuer-minus-raw residual. Single-entry hypothesis is coherent but unauthenticated; no promotion.",
        })
    elif row["entity"] == "HSBC Bank Argentina S.A.":
        row["v72_note"] = row["v72_note"].replace("V162", "V163 inherited from V162")
write_csv(HERE / "FOUR_LEG_PASS_PANEL_V163.csv", panel)

coverage = read_csv(V162 / "STRICT_Q4_FOUR_LEG_COVERAGE_V162.csv")
coverage[0]["coverage_set"] = "V163 strict 33-entity set; Banco Rioja and HSBC remain excluded"
if "v161_change" in coverage[0]:
    coverage[0]["v161_change"] = f"V163: no numeric change. Rioja residual corrected to equal 158789k on stock and income; entry unauthenticated. Counterfactual only: {COUNTERFACTUAL_COVERAGE}%."
write_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V163.csv", coverage)

# 5. Public-route and source controls.
route_rows = [
    {"control_id":"WEB163_01","route":"Banco Rioja · Disciplina de mercado index","url":"https://bancorioja.com.ar/institucional/disciplina-de-mercado","result":"OFFICIAL_QUARTERLY_INDEX","evidentiary_use":"Locates 30/09/2023 and 30/09/2024 official PDFs."},
    {"control_id":"WEB163_02","route":"Banco Rioja · DM 30/09/2024","url":new_source["url_original"],"result":"OFFICIAL_PDF_ARCHIVED","evidentiary_use":"Physical page 7 reports repo and securities-lending operations equal to zero."},
    {"control_id":"WEB163_03","route":"Banco Rioja · Balances","url":"https://bancorioja.com.ar/institucional/balances","result":"ROUTE_REDIRECTS_TO_EEFF_BR_PDF_2021","evidentiary_use":"Did not expose a 2023 9M result opening or 2024 annual statement index."},
    {"control_id":"WEB163_04","route":"Focused 2024 annual filename probe","url":"https://bancorioja.com.ar/pdf/EEFF-BR-2024.pdf","result":"HTTP_404","evidentiary_use":"Single targeted negative probe; no filename iteration used."},
    {"control_id":"WEB163_05","route":"Boletín Oficial La Rioja 07/03/2025","url":"https://www.boletinoflarioja.com.ar/pdf/2025/2025-03-07.pdf","result":"ASSEMBLY_NOTICE_REFERENCES_2024_STATEMENTS_WITHOUT_ATTACHING_THEM","evidentiary_use":"Corroborates existence only; not used for values."},
    {"control_id":"WEB163_06","route":"Moody's Local Banco Rioja 26/05/2025","url":"https://moodyslocal.com.ar/wp-content/uploads/2025/05/MLAR_Banco-Rioja_26052025.pdf","result":"SECONDARY_REPORT_SAYS_AUDITED_2024_BALANCE_USED","evidentiary_use":"Discovery lead only; not accounting evidence."},
]
write_csv(HERE / "BANCO_RIOJA_PUBLIC_ROUTE_EXHAUSTION_V163.csv", route_rows)
write_csv(HERE / "V163_PUBLIC_SEARCH_LOG.csv", route_rows)

rioja_dm23 = CYCLE / "inputs/source_sync/v162/binaries/banco_rioja_disciplina_mercado_9m2023.pdf"
rioja_fy = CYCLE / "inputs/source_sync/v161/binaries/banco_rioja_eeff_fy2023.pdf"
raw_sep_archive = CYCLE / "inputs/bcra/2023-09/informacion_entidades_financieras_open_data/202309d.7z"
raw_fy_archive = REPO / "data/fuentes/credito_consumo/bcra_entidades/historico_2023_2026/202312d.7z"
source_paths = [
    ("RIOJA_FY_FINANCIAL_STATEMENT", rioja_fy, "https://bancorioja.com.ar/pdf/EEFF-BR-2023.pdf", "FY stock, accounting policy, Note 6 and Annex Q"),
    ("RIOJA_9M2023_DISCIPLINE_MARKET", rioja_dm23, "https://bancorioja.com.ar/pdf/disciplina-de-mercado/DM-30-09-23.pdf", "Exact 9M stock control"),
    ("RIOJA_9M2024_DISCIPLINE_MARKET", rioja_dm24, new_source["url_original"], "Negative temporal comparator"),
    ("BCRA_RAW_9M_ARCHIVE", raw_sep_archive, "OFFICIAL_LOCAL_ARCHIVE_ALREADY_CATALOGUED", "Entity 00309 Sep raw accounts"),
    ("BCRA_RAW_FY_ARCHIVE", raw_fy_archive, "OFFICIAL_LOCAL_ARCHIVE_ALREADY_CATALOGUED", "Entity 00309 Dec raw accounts and corrected 141222"),
]
bundle = []
for role, path, url, use in source_paths:
    assert path.is_file()
    bundle.append({"role":role,"path":"/"+path.relative_to(REPO).as_posix(),"url":url,"bytes":str(path.stat().st_size),"sha256":sha256(path),"analytic_use":use})
write_csv(HERE / "V163_SOURCE_BUNDLE.csv", bundle)

visual = [
    {"control_id":"PV163_01","artifact":"banco_rioja_eeff_fy2023.pdf","page":"3","method":"Poppler 150 dpi + original-detail visual inspection","target":"FY balance repo stock","result":"PASS","observation":"Operaciones de pase 29,217,148."},
    {"control_id":"PV163_02","artifact":"banco_rioja_eeff_fy2023.pdf","page":"18","method":"Poppler 150 dpi + original-detail visual inspection","target":"repo accounting policy","result":"PASS_LIMIT","observation":"Purchase-sale difference accrues by effective-interest method and is posted to interest results; this supports plausibility, not the journal's existence."},
    {"control_id":"PV163_03","artifact":"banco_rioja_eeff_fy2023.pdf","page":"25 / printed 23","method":"Poppler 150 dpi + original-detail visual inspection","target":"FY repo stock and counterparty","result":"PASS","observation":"BCRA LELIQ active repos 29,217,148; no passive repos."},
    {"control_id":"PV163_04","artifact":"banco_rioja_eeff_fy2023.pdf","page":"79 / printed 77","method":"Poppler 150 dpi + original-detail visual inspection","target":"FY Annex Q result split","result":"PASS","observation":"BCRA repo income 14,409,056 and expense 7,844; other-FI absent."},
    {"control_id":"PV163_05","artifact":"banco_rioja_disciplina_mercado_9m2023.pdf","page":"7","method":"Poppler 150 dpi + original-detail visual inspection","target":"9M-2023 repo stock","result":"PASS_LIMIT","observation":"Repo instruments 14,191,142; no result-flow opening."},
    {"control_id":"PV163_06","artifact":"banco_rioja_disciplina_mercado_9m2024.pdf","page":"7","method":"Poppler 150 dpi + original-detail visual inspection","target":"9M-2024 repo stock","result":"PASS_LIMIT","observation":"Repo and securities-lending operations 0; no comparative 2023 result opening."},
]
write_csv(HERE / "V163_PDF_VISUAL_CONTROL.csv", visual)

# 6. Incremental source-sync records.
sync_manifest = [{
    "role":"OFFICIAL_NEGATIVE_COMPARATOR_BINARY",
    "relative_path":"/"+rioja_dm24.relative_to(REPO).as_posix(),
    "source_url":new_source["url_original"],
    "size_bytes":str(rioja_dm24.stat().st_size),
    "sha256":rioja_dm24_hash,
    "format_verification":"PDF_MAGIC_VALID_PAGES_9_VISUALLY_INSPECTED_PHYSICAL_PAGE_7",
}]
write_csv(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V163.csv", sync_manifest)
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V163.csv", route_rows)
(SYNC / "SOURCE_SYNC_REPORT_V163.md").write_text("""# Sincronización incremental de fuentes — V163

- Catálogo maestro: **579/579** copias locales con SHA-256 válido; brecha catalogada: **0**.
- Fuente nueva: Disciplina de Mercado de Banco Rioja al 30/09/2024, PDF oficial de 9 páginas.
- Uso: control temporal negativo; la página física 7 informa operaciones de pase y cauciones iguales a cero.
- La fuente no reemplaza la apertura de resultados 9M-2023 ni autentica el ajuste de cierre inferido.
- Ninguna solicitud fue enviada; seis borradores siguen `DRAFT_NOT_SENT`.
""", encoding="utf-8")

# 7. Human-readable checkpoint and explicit correction.
(HERE / "README_V163.md").write_text(f"""# Checkpoint V163

- Archivo fuente catalogado: 579/579 copias locales con hash válido.
- Fe de erratas V162: diciembre sí contiene `141222 = 79.394k`; el residuo correcto de stock es 158.789k, no 238.183k.
- Banco Rioja: el residuo auditado menos raw es exactamente 158.789k tanto en stock como en ingreso.
- Hipótesis mínima: un asiento de cierre balanceado por 158.789k; algebraicamente coherente, documentalmente no autenticado.
- Rango Q4 de ingreso BCRA: {q4_raw_income}k a {q4_adjusted_income}k; no se promueve.
- Control 9M-2024 preservado: stock de pases 0, sin apertura comparativa del resultado 2023.
- Panel sin cambio: 33 entidades exactas; cobertura {COVERAGE}%.
- Contrafactual, no panel: si Rioja se promoviera con evidencia futura, cobertura {COUNTERFACTUAL_COVERAGE}%.
- SAF355 0/5; ejecución histórica 0/10; seis borradores no enviados.
""", encoding="utf-8")
(HERE / "VEREDICTO_V163.md").write_text(f"""# Veredicto V163

V163 corrige un error de extracción de V162 y estrecha sustancialmente el caso Banco Rioja. La cuenta 141222 de diciembre sí existe por 79.394k. Sumada al capital, deja un residuo de stock de 158.789k, exactamente igual al residuo de ingreso. Esa identidad permite una hipótesis contable parsimoniosa de débito al activo y crédito al ingreso por el mismo monto. Sin embargo, la identidad algebraica no autentica el asiento ni determina si fue un ajuste de cierre, auditoría u otra registración. Como falta la apertura de resultados 9M del emisor o una conciliación firmada, el rango Q4 no se colapsa y la entidad permanece excluida. El panel conserva 33 entidades y {COVERAGE}% de activos.
""", encoding="utf-8")
(HERE / "AUDITORIA_V163.md").write_text(f"""# Auditoría V163

- Catálogo/copia/hash: 579/579; huecos catalogados: 0.
- Fuente nueva: 1 PDF oficial, 351.576 bytes, 9 páginas, SHA-256 {rioja_dm24_hash}.
- Corrección: `141222` diciembre = 79.394k; stock raw = 29.058.359k; residuo stock = residuo ingreso = 158.789k.
- Banco Rioja: 8 controles contables, 8 filas raw, 3 escenarios y 6 páginas relevantes inspeccionadas.
- Decisión: hipótesis de asiento no autenticada; 0 promociones.
- Panel: 33 exactas, {COVERAGE}%; contrafactual Rioja {COUNTERFACTUAL_COVERAGE}%.
- SAF355 0/5; ejecución 0/10; pedidos/respuestas 0/0.
""", encoding="utf-8")
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V163_A_V164.md").write_text(f"""# Handover V163 → V164

## Cerrado en V163

- Fe de erratas: `141222 = 79.394k` en diciembre; el residuo completo de stock es 158.789k.
- Stock e ingreso presentan el mismo residuo de 158.789k; hipótesis de un asiento balanceado documentada, no autenticada.
- Fuente 9M-2024 preservada como control negativo; archivo 579/579 local y hash-válido.
- Panel sin cambio: 33 entidades; cobertura {COVERAGE}%.

## Prioridad V164

1. Obtener Banco Rioja 9M-2023 Anexo Q/apertura de resultados o conciliación auditada-regulatoria firmada.
2. Buscar diario, comprobante o papel de trabajo del posible ajuste de cierre por 158.789k sin atribuirle una causa antes de la evidencia.
3. Recuperar A6358/A6402 del BCRA cuando el endpoint permita descarga estable.
4. Retomar Plan SIGEN 2009, Nota 3672/09 y crosswalk UAI-entidad-proyecto-informe.
5. Mantener SAF355 0/5, ejecución 0/10 y seis `DRAFT_NOT_SENT` hasta evidencia primaria o autorización.
""", encoding="utf-8")

source_refs = HERE / "SOURCE_REFERENCES_V163.md"
with source_refs.open("a", encoding="utf-8") as handle:
    handle.write(f"\n- `banco_rioja_disciplina_mercado_9m2024_v163` · Banco Rioja · Disciplina de mercado 30/09/2024 · {new_source['url_original']} · `{new_source['archivo_local']}` · `{rioja_dm24_hash}`\n")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V162.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint":"V163", "date":"2026-08-31", "master_catalog_entries":579,
    "physical_local_copies":579, "physical_local_hash_ok":579,
    "remaining_catalog_physical_or_hash_gaps":0,
    "state":"SOURCE_ARCHIVE_COMPLETE_RIOJA_DUAL_RESIDUAL_CORRECTED_ADJUSTING_ENTRY_UNAUTHENTICATED",
    "analytical_promotion":"NONE_V163_CORRECTION_AND_BOUND_ONLY",
    "exact_entities":33, "strict_asset_numerator_million_ars":str(NUMERATOR),
    "system_assets_million_ars":str(SYSTEM_ASSETS), "strict_coverage_pct":str(COVERAGE),
    "strict_coverage_increment_v162_pp":"0", "rioja_counterfactual_coverage_pct":str(COUNTERFACTUAL_COVERAGE),
    "request_drafts_status":"DRAFT_NOT_SENT", "requests_submitted":0, "responses_received":0,
    "saf355_certifications_located":0, "executed_historical_bank_rows_confirmed":0,
    "discovered_official_binary_recovery_queue":2,
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V163.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

# 8. Provenance, transparency, inventories and manifests.
origin_rows = read_csv(ORIGINS)
origin_by_path = {row["path"]: row for row in origin_rows}
for path in iter_files(SYNC):
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path":rel,"origin":"generated/recovered V163","note":"Banco Rioja 9M-2024 official source or V163 source-control artifact"}
for path in sorted(HERE.iterdir(), key=lambda p:p.name.casefold()):
    if path.is_file():
        rel = path.relative_to(CYCLE).as_posix()
        origin_by_path[rel] = {"path":rel,"origin":"generated/updated V163","note":"V163 correction, dual-residual reconciliation and strict no-promotion control"}
for path in [
    AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V163.csv", AUDIT / "SOURCE_BACKUP_CENSUS_V163.csv",
    AUDIT / "SOURCE_PRESERVATION_MISSING_V163.csv", AUDIT / "CURRENT_SOURCE_COMPLETENESS_V163.json",
]:
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path":rel,"origin":"generated/updated V163","note":"579-source physical/hash completeness control"}
write_csv(ORIGINS, list(origin_by_path.values()), ["path","origin","note"])

transparency = CYCLE / "TRANSPARENCY_README.md"
transparency_text = transparency.read_text(encoding="utf-8-sig")
if "## V163 · Fe de erratas Banco Rioja" not in transparency_text:
    transparency_text += """

## V163 · Fe de erratas Banco Rioja

V162 omitió por error la cuenta 141222 de diciembre. V163 conserva el error histórico y lo corrige explícitamente: 141222 = 79.394k, stock raw completo = 29.058.359k y diferencia contra el auditado = 158.789k. El mismo residuo aparece en ingreso. Se documenta una hipótesis de asiento balanceado, pero no se la trata como hecho ni se promueve la entidad sin conciliación autenticada. Se preservó además la Disciplina de Mercado 9M-2024; el archivo catalogado queda 579/579.
"""
    transparency.write_text(transparency_text, encoding="utf-8")

backup = REPO / "BACKUP_ACTUALIZACION_2026-08-31.md"
backup.write_text(f"""# Backup de actualización · 2026-08-31

- Checkpoint: V163.
- Fuentes catalogadas: 579/579 local y SHA-válido.
- Banco Rioja: fe de erratas 141222; residuo dual exacto de 158.789k; hipótesis de asiento no autenticada; sin promoción.
- Fuente 9M-2024 preservada como control negativo.
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

files = [{"path":p.name,"bytes":p.stat().st_size,"sha256":sha256(p)} for p in sorted(HERE.iterdir(),key=lambda x:x.name.casefold()) if p.is_file() and p.name!="MANIFEST_V163.json"]
manifest = {
    "checkpoint":"V163","parent_checkpoint":"V162","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
    "exact_entities":33,"strict_coverage_pct":str(COVERAGE),"strict_asset_numerator_million_ars":str(NUMERATOR),"system_assets_million_ars":str(SYSTEM_ASSETS),
    "rioja_counterfactual_coverage_pct":str(COUNTERFACTUAL_COVERAGE),"new_promotions":[],
    "negative_controls":["Banco Rioja S.A.U. N/D_STRICT_ADJUSTING_ENTRY_UNAUTHENTICATED","HSBC Bank Argentina S.A. N/D_STRICT"],
    "correction":"V162 omitted Dec account 141222=79394k; corrected complete stock and income residuals both equal 158789k",
    "source_archive":"579/579 catalogued physical SHA-valid; 2 discovered BCRA binaries pending server recovery",
    "closed_network_gate":"NO","saf355_certifications":"0/5","executed_historical_bank_rows":"0/10","requests_submitted":0,"files":files,
}
(HERE / "MANIFEST_V163.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

global_manifest=CYCLE/"MANIFEST_SHA256.json"
global_files=[{"path":p.relative_to(REPO).as_posix(),"bytes":p.stat().st_size,"sha256":sha256(p)} for p in iter_files(REPO) if p!=global_manifest]
global_payload={
    "checkpoint":"V163","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
    "strict_coverage_pct":str(COVERAGE),"exact_entities":33,"closed_network_gate":"NO",
    "source_audit":"579 master; 579 physical SHA-valid; Banco Rioja dual residual corrected but adjusting entry unauthenticated; HSBC split open; 2 BCRA binaries queued",
    "historical_workstream":"Plan SIGEN 2009, Nota 3672/09, SAF355 and bank execution remain open; six drafts not sent",
    "file_count_excluding_manifest":len(global_files),"files":global_files,
}
tmp=global_manifest.with_suffix(".json.V163tmp")
tmp.write_text(json.dumps(global_payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
tmp.replace(global_manifest)

print(f"V163 BUILD PASS · exact=33 · coverage={COVERAGE} · catalog=579/579 · promotions=0")
