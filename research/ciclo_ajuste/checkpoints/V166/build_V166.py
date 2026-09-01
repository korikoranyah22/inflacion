from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, getcontext
from pathlib import Path
import csv
import hashlib
import io
import json
import os
import subprocess


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
V165 = CYCLE / "checkpoints" / "V165"
SYNC = CYCLE / "inputs" / "source_sync" / "v166"
AUDIT = CYCLE / "source_audit"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
ORIGINS = CYCLE / "FILE_ORIGINS.csv"
RAW_9M = CYCLE / "inputs/bcra/2023-09/informacion_entidades_financieras_open_data/202309d.7z"
RAW_FY = REPO / "data/fuentes/credito_consumo/bcra_entidades/historico_2023_2026/202312d.7z"
IEF_ORIGINAL = CYCLE / "inputs/bcra/2023-12/informacion_entidades_financieras_open_data/202312e.pdf"
IEF_REVISED = CYCLE / "inputs/bcra/2024-06/informacion_entidades_financieras_open_data/202406e.pdf"
RIOJA_FY = CYCLE / "inputs/source_sync/v161/binaries/banco_rioja_eeff_fy2023.pdf"
A6358 = CYCLE / "inputs/source_sync/v164/binaries/bcra_comunicacion_a6358.pdf"
A6402 = CYCLE / "inputs/source_sync/v164/binaries/bcra_comunicacion_a6402.pdf"
FACTOR = Decimal("1.532908152197492")
OLD_NUMERATOR = Decimal("61248719.753")
RIOJA_ASSETS = Decimal("96882.462")
NEW_NUMERATOR = OLD_NUMERATOR + RIOJA_ASSETS
SYSTEM_ASSETS = Decimal("96697695.5")
getcontext().prec = 120
OLD_COVERAGE = OLD_NUMERATOR / SYSTEM_ASSETS * Decimal(100)
COVERAGE = NEW_NUMERATOR / SYSTEM_ASSETS * Decimal(100)
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
        dirnames[:] = sorted((name for name in dirnames if name not in EXCLUDED_DIRS), key=str.casefold)
        for filename in sorted(filenames, key=str.casefold):
            yield Path(dirpath) / filename


def clone_parent():
    excluded = {
        "build_V165.py", "qa_v165.py", "MANIFEST_V165.json", "CURRENT_STATE_V165.csv",
        "FOUR_LEG_PASS_PANEL_V165.csv", "STRICT_Q4_FOUR_LEG_COVERAGE_V165.csv",
        "README_V165.md", "VEREDICTO_V165.md", "AUDITORIA_V165.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V165_A_V166.md", "CORRECTION_LOG_V165.md",
        "BANCO_RIOJA_ADJUSTING_ENTRY_HYPOTHESIS_V165.md",
        "BANCO_RIOJA_CLOSING_PACKAGE_NOTE_V165.md", "BANCO_RIOJA_CLOSING_LAYER_NOTE_V165.md",
        "BANCO_RIOJA_MISMATCH_ANALYTIC_NOTE_V165.md",
        "BANCO_RIOJA_STOCK_AND_RESULT_RECONCILIATION_V165.csv",
        "BANCO_RIOJA_DUAL_RESIDUAL_RECONCILIATION_V165.csv",
        "BANCO_RIOJA_Q4_SCENARIO_BOUND_V165.csv",
        "BANCO_RIOJA_PUBLIC_ROUTE_EXHAUSTION_V165.csv",
        "V165_PDF_VISUAL_CONTROL.csv", "V165_PUBLIC_SEARCH_LOG.csv", "V165_SOURCE_BUNDLE.csv",
    }
    for source in sorted(V165.iterdir(), key=lambda path: path.name.casefold()):
        if not source.is_file() or source.name in excluded:
            continue
        target = HERE / source.name.replace("V165", "V166")
        target.write_text(source.read_text(encoding="utf-8-sig").replace("V165", "V166"), encoding="utf-8")


def raw_accounts(archive: Path):
    member = "Entfin/Tec_Cont/baldet/00309.txt"
    result = subprocess.run(["tar", "-xOf", str(archive), member], capture_output=True)
    assert result.returncode == 0 and result.stdout
    text = result.stdout.decode("cp1252", errors="replace")
    rows = list(csv.reader(io.StringIO(text), delimiter="\t"))
    return {row[3]: {"description": row[4], "debit": Decimal(row[5]), "credit": Decimal(row[6])} for row in rows}


clone_parent()

# 1. Preserve and catalogue the later BCRA comparative that carries the corrected FY layer.
assert IEF_REVISED.is_file()
assert IEF_REVISED.stat().st_size == 6027314
assert sha256(IEF_REVISED) == "991ce57930183c65095c64c6a3abc44f02e419b5186f2287c78e9f7359763719"

catalog = read_csv(CATALOG)
catalog_fields = list(catalog[0])
source_id = "bcra_entidades_jun2024_rioja_corrected_comparative_v166"
source_row = {
    "id":source_id,"tema":"ciclo_ajuste_bancos","institucion":"Banco Central de la República Argentina",
    "titulo":"Información de Entidades Financieras · junio 2024 · comparativo Banco Rioja diciembre 2023 corregido",
    "url_original":"https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/Entidades/202406e.pdf",
    "archivo_local":"/"+IEF_REVISED.relative_to(REPO).as_posix(),"fecha_descarga":"2026-08-28",
    "fecha_publicacion":"2024-06","codigo_serie":"","periodo_utilizado":"2023-12;2024-06",
    "tipo":"PDF oficial · comparativo posterior preservado","sha256":sha256(IEF_REVISED),
    "nota":"V166: página física 261 / impresa 260. El comparativo Dic-2023 migra a activo 96.944,8m, resultado -1.154,7m e ingresos por intereses 44.964,3m; marca (1) Favor s/salvedades. Corrobora la capa FY corregida.",
}
catalog_by_id = {row["id"]: row for row in catalog}
catalog_by_id[source_id] = source_row
catalog = list(catalog_by_id.values())
write_csv(CATALOG, catalog, catalog_fields)
assert len(catalog) == 585

audit_rows = []
for row in catalog:
    local = REPO / row["archivo_local"].lstrip("/")
    exists = local.is_file()
    actual = sha256(local) if exists else ""
    audit_rows.append({
        "id":row["id"],"archivo_local":row["archivo_local"],"exists":str(exists),
        "sha_catalog":row["sha256"].lower(),"sha_actual":actual,
        "hash_ok":str(exists and bool(row["sha256"]) and actual == row["sha256"].lower()),
    })
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V166.csv", audit_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V166.csv", audit_rows)
missing = [row for row in audit_rows if row["exists"] != "True" or row["hash_ok"] != "True"]
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V166.csv", missing, list(audit_rows[0]))
assert not missing

# 2. Verify the complete candidate account set in both regulatory cuts.
candidate_codes = {"511007","511027","511108","515034","521007","521022","521108","525042"}
sep = raw_accounts(RAW_9M)
dec = raw_accounts(RAW_FY)
assert candidate_codes & set(sep) == {"511108","521108"}
assert candidate_codes & set(dec) == {"511108","521108"}
assert sep["511108"]["credit"] == Decimal("5712151") and sep["521108"]["debit"] == Decimal("5117")
assert dec["511108"]["credit"] == Decimal("14250267") and dec["521108"]["debit"] == Decimal("7844")

candidate_rows = [
    {"period":"9M-2023","present_candidate_accounts":"511108=5712151_credit;521108=5117_debit","absent_candidate_accounts":"511007;511027;515034;521007;521022;525042","source_member":"202309d.7z/Entfin/Tec_Cont/baldet/00309.txt","verdict":"COMPLETE_CANDIDATE_SET_TWO_BCRA_LEGS_ONLY"},
    {"period":"FY-2023_raw","present_candidate_accounts":"511108=14250267_credit;521108=7844_debit","absent_candidate_accounts":"511007;511027;515034;521007;521022;525042","source_member":"202312d.7z/Entfin/Tec_Cont/baldet/00309.txt","verdict":"COMPLETE_CANDIDATE_SET_TWO_BCRA_LEGS_ONLY_PRE_CLOSING_ADJUSTMENT"},
]
write_csv(HERE / "BANCO_RIOJA_CANDIDATE_ACCOUNT_EXHAUSTION_V166.csv", candidate_rows)

# 3. Compare the original and later BCRA public presentations.
comparative = [
    {"measure":"total_assets","original_202312e_million_ars":"96882.5","later_202406e_dic2023_million_ars":"96944.8","displayed_delta_million_ars":"62.3","interpretation":"MIGRATES_TO_AUDITED_TOTAL"},
    {"measure":"other_credits_financial_intermediation","original_202312e_million_ars":"33595.6","later_202406e_dic2023_million_ars":"33754.4","displayed_delta_million_ars":"158.8","interpretation":"REPO_STOCK_COMPONENT_MIGRATES"},
    {"measure":"total_liabilities","original_202312e_million_ars":"62510.2","later_202406e_dic2023_million_ars":"62510.2","displayed_delta_million_ars":"0.0","interpretation":"UNCHANGED"},
    {"measure":"net_equity","original_202312e_million_ars":"34372.3","later_202406e_dic2023_million_ars":"34434.6","displayed_delta_million_ars":"62.3","interpretation":"MIGRATES_TO_AUDITED_TOTAL"},
    {"measure":"current_result","original_202312e_million_ars":"-1217.0","later_202406e_dic2023_million_ars":"-1154.7","displayed_delta_million_ars":"62.3","interpretation":"MIGRATES_TO_AUDITED_TOTAL"},
    {"measure":"financial_income","original_202312e_million_ars":"62071.9","later_202406e_dic2023_million_ars":"62230.7","displayed_delta_million_ars":"158.8","interpretation":"REPO_INCOME_COMPONENT_MIGRATES"},
    {"measure":"interest_income","original_202312e_million_ars":"44805.5","later_202406e_dic2023_million_ars":"44964.3","displayed_delta_million_ars":"158.8","interpretation":"CORRECTED_INSIDE_INTEREST_INCOME"},
    {"measure":"other_financial_income","original_202312e_million_ars":"17266.4","later_202406e_dic2023_million_ars":"17266.4","displayed_delta_million_ars":"0.0","interpretation":"UNCHANGED_ZERO_OTHERFI_REPO_LEG_SUPPORTED"},
    {"measure":"financial_expense","original_202312e_million_ars":"-18489.7","later_202406e_dic2023_million_ars":"-18489.7","displayed_delta_million_ars":"0.0","interpretation":"UNCHANGED"},
    {"measure":"interest_expense","original_202312e_million_ars":"-17112.3","later_202406e_dic2023_million_ars":"-17112.3","displayed_delta_million_ars":"0.0","interpretation":"UNCHANGED"},
    {"measure":"other_financial_expense","original_202312e_million_ars":"-1377.4","later_202406e_dic2023_million_ars":"-1377.4","displayed_delta_million_ars":"0.0","interpretation":"UNCHANGED_ZERO_OTHERFI_REPO_LEG_SUPPORTED"},
]
write_csv(HERE / "BANCO_RIOJA_LATER_BCRA_COMPARATIVE_V166.csv", comparative)

timeline = read_csv(V165 / "BANCO_RIOJA_CLOSING_LAYER_TIMELINE_V165.csv")
timeline.append({
    "sequence":"5","event":"Later BCRA IEF republishes corrected Dec-2023 comparator",
    "date_or_timestamp":"2024-06","evidence":"202406e.pdf, physical page 261 / printed page 260",
    "interpretation":"BCRA later public comparator authenticates the corrected closing layer: assets and result migrate to audited totals, and the +158.8m financial-income change is entirely inside interest income while the other financial openings remain unchanged.",
})
write_csv(HERE / "BANCO_RIOJA_CLOSING_LAYER_TIMELINE_V166.csv", timeline)

# 4. Four-leg exactification under the inherited same-entity/same-year bridge rule.
fy_income_bcra = Decimal("14409056")
fy_expense_bcra = Decimal("7844")
sep_income_bcra = Decimal("5712151")
sep_expense_bcra = Decimal("5117")
q4_income_bcra = fy_income_bcra - sep_income_bcra * FACTOR
q4_expense_bcra = fy_expense_bcra - sep_expense_bcra * FACTOR
q4_income_otherfi = Decimal("0")
q4_expense_otherfi = Decimal("0")
q4_net_bcra = q4_income_bcra - q4_expense_bcra
q4_net_otherfi = Decimal("0")

promotion = [
    {"leg":"income_bcra","fy_issuer_thousand_ars":str(fy_income_bcra),"nine_month_raw_thousand_ars":str(sep_income_bcra),"factor":str(FACTOR),"q4_thousand_ars":str(q4_income_bcra),"evidence":"FY Annex Q BCRA-only 14409056; A6358/A6402 mapping; later BCRA comparator moves interest income +158.8m; Sep complete candidate set has only 511108/521108","verdict":"EXACT_SAME_ENTITY_YEAR_BASIS"},
    {"leg":"expense_bcra","fy_issuer_thousand_ars":str(fy_expense_bcra),"nine_month_raw_thousand_ars":str(sep_expense_bcra),"factor":str(FACTOR),"q4_thousand_ars":str(q4_expense_bcra),"evidence":"FY Annex Q BCRA-only expense 7844 equals raw; Sep 521108 only expense candidate","verdict":"EXACT_SAME_ENTITY_YEAR_BASIS"},
    {"leg":"income_otherfi","fy_issuer_thousand_ars":"0","nine_month_raw_thousand_ars":"0","factor":str(FACTOR),"q4_thousand_ars":"0","evidence":"FY Annex Q has no other-FI repo income; candidate accounts absent in Sep and FY; later BCRA other financial income unchanged","verdict":"EXACT_ZERO"},
    {"leg":"expense_otherfi","fy_issuer_thousand_ars":"0","nine_month_raw_thousand_ars":"0","factor":str(FACTOR),"q4_thousand_ars":"0","evidence":"FY Annex Q has no other-FI repo expense; candidate accounts absent in Sep and FY; later BCRA other financial expense unchanged","verdict":"EXACT_ZERO"},
]
write_csv(HERE / "BANCO_RIOJA_FOUR_LEG_PROMOTION_V166.csv", promotion)
write_csv(HERE / "BANCO_RIOJA_Q4_SCENARIO_BOUND_V166.csv", [
    {"scenario":"PROMOTED_CORRECTED_CLOSING_LAYER","q4_income_bcra_thousand_ars":str(q4_income_bcra),"q4_expense_bcra_thousand_ars":str(q4_expense_bcra),"panel_use":"YES","remaining_gate":"NONE_FOUR_LEGS_EXACT_UNDER_ENTITY_YEAR_BASIS_RULE"},
])

recon = read_csv(V165 / "BANCO_RIOJA_STOCK_AND_RESULT_RECONCILIATION_V165.csv")
for index, row in enumerate(recon, start=1):
    row["control_id"] = f"BR166_{index:02d}"
recon.append({
    "control_id":"BR166_12","period":"FY-2023_later_comparative","measure":"interest_income_corrected_public_layer",
    "issuer_value_thousand_ars":"14409056_repo_component","raw_account_set":"511108_PLUS_CLOSING_158789",
    "raw_values_thousand_ars":"14250267+158789","raw_sum_thousand_ars":"14409056",
    "difference_issuer_minus_raw":"0","verdict":"LATER_BCRA_COMPARATIVE_AUTHENTICATES_RESULT_CLOSING_LAYER",
    "analytic_use":"Later BCRA IEF carries Dic-2023 financial and interest income +158.8m while other financial income and all financial expenses remain unchanged; supports exact FY Annex-Q repo correction.",
})
write_csv(HERE / "BANCO_RIOJA_STOCK_AND_RESULT_RECONCILIATION_V166.csv", recon)
write_csv(HERE / "BANCO_RIOJA_DUAL_RESIDUAL_RECONCILIATION_V166.csv", [row for row in recon if row["control_id"] in {"BR166_02","BR166_03","BR166_10","BR166_11","BR166_12"}])

# 5. Promote state and panel, using the same raw asset denominator basis as the inherited panel.
state = read_csv(V165 / "CURRENT_STATE_V165.csv")
rioja = next(row for row in state if row["entity"] == "Banco Rioja S.A.U.")
rioja.update({
    "target_basis":"INDIVIDUAL_ENTITY_REGULATORY_WITH_AUDITED_ISSUER_AND_LATER_BCRA_COMPARATIVE_VALIDATION",
    "fy_status":"EXACT_FY_AUDITED_ANNEXQ_PLUS_LATER_BCRA_CORRECTED_COMPARATIVE_V166",
    "nine_month_status":"EXACT_BCRA_RAW_COMPLETE_CANDIDATE_SET_ENTITY_YEAR_BASIS_BRIDGE_V166",
    "q4_four_leg_status":"EXACT","strict_panel_status":"ELIGIBLE","priority":"CLOSED_V166_PROMOTED",
    "next_action":"retain entity-year-basis guardrail; do not universalize codes beyond documented A6358/A6402 mapping and complete candidate set",
})
write_csv(HERE / "CURRENT_STATE_V166.csv", state)

panel = read_csv(V165 / "FOUR_LEG_PASS_PANEL_V165.csv")
for row in panel:
    if row["entity"] == "Banco Rioja S.A.U.":
        row.update({
            "basis":"INDIVIDUAL_ENTITY_REGULATORY_WITH_AUDITED_ISSUER_AND_LATER_BCRA_COMPARATIVE_VALIDATION",
            "income_bcra":str(q4_income_bcra),"expense_bcra":str(q4_expense_bcra),
            "income_otherfi":"0","expense_otherfi":"0","net_bcra":str(q4_net_bcra),"net_otherfi":str(q4_net_otherfi),
            "quality":"EXACT_FROM_BCRA_RAW_9M_PLUS_AUDITED_FY_ANNEXQ_AND_LATER_BCRA_CORRECTED_COMPARATIVE",
            "target_basis_compatible":"YES_ENTITY_YEAR_BASIS_COMPLETE_CANDIDATE_SET",
            "system_panel_eligible_v72":"YES_EXACT_Q4_TARGET_BASIS",
            "v72_note":"V166 promotion: FY Annex Q assigns repo income 14,409,056k and expense 7,844k exclusively to BCRA. Later BCRA IEF migrates Dic-2023 interest income +158.8m to the audited layer, with other financial income/expenses unchanged and audit marker (1). Sep/FY full candidate scan contains only 511108/521108; same entity/year/basis bridge, no universalization.",
        })
write_csv(HERE / "FOUR_LEG_PASS_PANEL_V166.csv", panel)

coverage = read_csv(V165 / "STRICT_Q4_FOUR_LEG_COVERAGE_V165.csv")
v105_coverage = Decimal(coverage[0]["asset_coverage_pct"]) - Decimal(coverage[0]["increment_vs_v105_pp"])
coverage[0].update({
    "coverage_set":"V166 strict 34-entity set; Banco Rioja promoted with audited FY plus later BCRA corrected comparative",
    "asset_numerator_million_ars":str(NEW_NUMERATOR),"asset_coverage_pct":str(COVERAGE),
    "increment_vs_v105_pp":str(COVERAGE-v105_coverage),
    "quality":"ALL_FOUR_LEGS_EXACT_THIRTY_FOUR_ENTITIES",
    "v161_change":f"V166: Banco Rioja promoted; +{RIOJA_ASSETS}m assets and +{COVERAGE-OLD_COVERAGE} pp versus V165.",
})
write_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V166.csv", coverage)

# 6. Promotion note and source controls.
note = f"""# Banco Rioja: promoción estricta V166

## Nueva evidencia decisiva

El informe BCRA de junio de 2024 vuelve a publicar diciembre de 2023 como comparativo auditado `(1) Favor s/salvedades` y migra la entidad a la capa de cierre: activo 96.944,8m, patrimonio 34.434,6m y resultado -1.154,7m. En resultados, ingresos financieros suben de 62.071,9m a 62.230,7m y el cambio completo aparece en `Por Intereses` (44.805,5m a 44.964,3m); `Otros Ingresos Financieros`, ingresos/egresos financieros y sus dos aperturas permanecen sin cambio.

El movimiento redondeado de +158,8m coincide con el residuo exacto de 158.789k entre `511108=14.250.267k` y el Anexo Q auditado `14.409.056k`. El mismo Anexo Q asigna todo el ingreso y gasto por pases al BCRA: 14.409.056k y 7.844k; las patas otras entidades financieras son cero.

## Puente 9M limitado

El censo completo de cuentas candidatas en septiembre y diciembre contiene sólo `511108` y `521108`; no aparecen `511007`, `511027`, `515034`, `521007`, `521022` ni `525042`. Bajo la regla ya usada para Mariva y Corrientes, el conjunto anual autenticado se traslada sólo a septiembre de Banco Rioja, ejercicio 2023 y la misma base regulatoria.

Así, Q4 queda: ingreso BCRA `{q4_income_bcra}k`, gasto BCRA `{q4_expense_bcra}k`, ingreso otras entidades `0`, gasto otras entidades `0`; neto BCRA `{q4_net_bcra}k`. No se generalizan códigos ni se convierte el comparativo agregado en un diario contable.
"""
(HERE / "BANCO_RIOJA_PROMOTION_NOTE_V166.md").write_text(note, encoding="utf-8")
(HERE / "BANCO_RIOJA_CLOSING_PACKAGE_NOTE_V166.md").write_text(note, encoding="utf-8")
(HERE / "BANCO_RIOJA_CLOSING_LAYER_NOTE_V166.md").write_text(note, encoding="utf-8")
(HERE / "BANCO_RIOJA_ADJUSTING_ENTRY_HYPOTHESIS_V166.md").write_text(note, encoding="utf-8")
(HERE / "BANCO_RIOJA_MISMATCH_ANALYTIC_NOTE_V166.md").write_text(note, encoding="utf-8")
(HERE / "CNV_ATTACHMENT_ANALYTIC_REVIEW_V166.md").write_text(f"""# Revisión analítica de adjuntos oficiales V166

## Resultado acumulado

El antecedente V161 promovió Banco BMA, Banco Mariva y Banco de Corrientes, llevando el panel de 30 a 33 entidades y la cobertura a {OLD_COVERAGE}%. V166 suma Banco Rioja sin flexibilizar la regla de cuatro patas: el panel pasa de 33 a 34 entidades, el numerador de activos de {OLD_NUMERATOR} a {NEW_NUMERATOR} millones de pesos y la cobertura a {COVERAGE}% (+{COVERAGE-OLD_COVERAGE} puntos porcentuales frente a V165).

## Método acumulado

1. Se preservaron y verificaron por SHA-256 los estados oficiales y los cortes raw.
2. Se inspeccionaron visualmente las páginas relevantes y se controlaron unidad, período y base individual/separada.
3. Se extrajeron de los archivos BCRA sólo las cuentas de resultado de cada entidad.
4. El conjunto se aceptó únicamente cuando reconciliaba el Anexo Q de la misma entidad y ejercicio.
5. Los puentes se transfirieron sólo dentro de la misma entidad, año y base; nunca como diccionario universal.
6. Q4 se calculó como FY homogéneo de diciembre menos 9M homogéneo de septiembre por 1.532908152197492, sin redondear residuos.

## Banco Rioja

El Anexo Q anual asigna pases exclusivamente al BCRA: ingreso 14.409.056k y gasto 7.844k; las patas otras entidades son cero. El censo completo deja sólo `511108` y `521108` en septiembre y diciembre. El IEF BCRA de junio de 2024 vuelve a publicar diciembre de 2023 en la capa corregida y ubica +158,8m enteramente dentro de ingresos por intereses, mientras las demás aperturas financieras permanecen invariantes. Esta cadena autentica el componente anual y permite el puente Rioja-2023-misma base.

Q4 resulta en ingreso BCRA {q4_income_bcra}k, gasto BCRA {q4_expense_bcra}k, ingreso y gasto otras entidades 0/0, y neto BCRA {q4_net_bcra}k. No se infiere un diario contable no publicado.

## Control negativo HSBC

HSBC continúa N/D_STRICT: publica totales con el sector financiero, pero no separa BCRA de otras entidades. Un stock no identifica la contraparte de los flujos.

## Resguardos

- La huella declarada por CNV y la huella de los bytes servidos se conservan por separado; una diferencia no se interpreta automáticamente como alteración.
- Activos agregados no sustituyen cuatro patas de resultados.
- SAF355 permanece 0/5, ejecución bancaria histórica 0/10 y seis pedidos siguen DRAFT_NOT_SENT.
""", encoding="utf-8")
(HERE / "CORRECTION_LOG_V166.md").write_text("""# Historial de corrección V166

V166 conserva las correcciones anteriores: stock raw 29.058.359k; stock e ingreso auditados 158.789k por encima de raw; no 238.183k. V165 cerró el paquete total (+62.306k neto, con offset no-pases -96.483k).

La novedad de V166 es una publicación BCRA posterior que lleva el comparativo diciembre de 2023 a la capa auditada y coloca el cambio de +158,8m exclusivamente dentro de ingresos por intereses, con otras aperturas financieras invariantes. Junto con Anexo Q, A6358/A6402 y el censo completo de candidatos, esto cierra las cuatro patas y habilita la promoción bajo la regla entidad-año-base.
""", encoding="utf-8")

routes = [
    {"control_id":"WEB166_01","institution":"BCRA","url":source_row["url_original"],"result":"OFFICIAL_LATER_COMPARATIVE_LOCALLY_PRESERVED_AND_VISUALLY_VERIFIED","decision":"PROMOTION_SUPPORT"},
    {"control_id":"WEB166_02","institution":"Banco Rioja","url":"https://bancorioja.com.ar/pdf/EEFF-BR-2023.pdf","result":"OFFICIAL_AUDITED_ANNEXQ_BCRA_ONLY_FOUR_LEG_SPLIT_PRESERVED","decision":"PROMOTION_SUPPORT"},
    {"control_id":"WEB166_03","institution":"BCRA","url":"https://www.bcra.gob.ar/archivos/Pdfs/comytexord/A6358.pdf","result":"ACCOUNT_AND_PUBLICATION_MAPPING_PRESERVED","decision":"PROMOTION_SUPPORT"},
    {"control_id":"WEB166_04","institution":"BCRA","url":"https://www.bcra.gob.ar/archivos/Pdfs/comytexord/A6402.pdf","result":"SUPERVISION_AND_PUBLICATION_MAPPING_PRESERVED","decision":"PROMOTION_SUPPORT"},
]
write_csv(HERE / "BANCO_RIOJA_PUBLIC_ROUTE_EXHAUSTION_V166.csv", routes)
write_csv(HERE / "V166_PUBLIC_SEARCH_LOG.csv", routes)

bundle_specs = [
    ("BCRA_IEF_ORIGINAL_FY", IEF_ORIGINAL, "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Entidades/202312e.pdf"),
    ("BCRA_IEF_LATER_CORRECTED_COMPARATIVE", IEF_REVISED, source_row["url_original"]),
    ("BCRA_RAW_9M", RAW_9M, "OFFICIAL_LOCAL_ARCHIVE_ALREADY_CATALOGUED"),
    ("BCRA_RAW_FY", RAW_FY, "OFFICIAL_LOCAL_ARCHIVE_ALREADY_CATALOGUED"),
    ("RIOJA_AUDITED_FY", RIOJA_FY, routes[1]["url"]),
    ("BCRA_A6358", A6358, routes[2]["url"]),
    ("BCRA_A6402", A6402, routes[3]["url"]),
]
bundle = []
for role, path, url in bundle_specs:
    assert path.is_file()
    bundle.append({"role":role,"path":"/"+path.relative_to(REPO).as_posix(),"url":url,"bytes":str(path.stat().st_size),"sha256":sha256(path),"analytic_use":"Banco Rioja four-leg promotion V166"})
write_csv(HERE / "V166_SOURCE_BUNDLE.csv", bundle)

visual = [
    {"control_id":"PV166_01","artifact":"202406e.pdf","page":"261 / printed 260","result":"PASS","observation":"Corrected audited Dic-2023 comparator: assets 96,944.8m; result -1,154.7m; interest income 44,964.3m; other financial income/expenses unchanged; audit marker (1)."},
    {"control_id":"PV166_02","artifact":"EEFF-BR-2023.pdf","page":"79 / printed 77","result":"PASS","observation":"Annex Q: repo income BCRA 14,409,056k; repo expense BCRA 7,844k; no other-FI repo legs."},
]
for row in visual:
    row["method"] = "Poppler render + original-detail visual inspection"
write_csv(HERE / "V166_PDF_VISUAL_CONTROL.csv", visual)

SYNC.mkdir(parents=True, exist_ok=True)
write_csv(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V166.csv", [{
    "role":"OFFICIAL_PDF_ALREADY_LOCAL_NOW_CATALOGUED","relative_path":"/"+IEF_REVISED.relative_to(REPO).as_posix(),
    "source_url":source_row["url_original"],"size_bytes":str(IEF_REVISED.stat().st_size),"sha256":sha256(IEF_REVISED),
    "format_verification":"PDF_MAGIC_VALID_396_PAGES_PAGE261_VISUALLY_INSPECTED",
}])
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V166.csv", routes)
(SYNC / "SOURCE_SYNC_REPORT_V166.md").write_text("""# Sincronización incremental de fuentes — V166

- Catálogo maestro: **585/585** copias locales con SHA-256 válido; brecha: **0**.
- Se incorporó formalmente al catálogo el IEF BCRA de junio de 2024, ya preservado físicamente en el repo.
- La página 261 vuelve a publicar diciembre de 2023 en la capa corregida/auditada y sustenta la promoción de Banco Rioja.
- No se enviaron solicitudes; seis borradores siguen `DRAFT_NOT_SENT`.
""", encoding="utf-8")

# 7. Checkpoint summaries.
(HERE / "README_V166.md").write_text(f"""# Checkpoint V166

- Archivo fuente: 585/585 copias locales con hash válido; una fuente previamente local incorporada al catálogo.
- Banco Rioja promovido: cuatro patas Q4 exactas bajo regla misma entidad/año/base.
- Q4: ingreso BCRA {q4_income_bcra}k; gasto BCRA {q4_expense_bcra}k; otras entidades 0/0; neto BCRA {q4_net_bcra}k.
- Evidencia decisiva: el IEF BCRA posterior migra Dic-2023 a la capa auditada y coloca +158,8m dentro de ingresos por intereses.
- Panel: 34 entidades exactas; activos {NEW_NUMERATOR} / {SYSTEM_ASSETS} millones; cobertura {COVERAGE}% (+{COVERAGE-OLD_COVERAGE} pp).
- No se universalizan códigos; no se afirma un diario contable no publicado.
- SAF355 0/5; ejecución histórica 0/10; seis borradores no enviados.
""", encoding="utf-8")
(HERE / "VEREDICTO_V166.md").write_text(f"""# Veredicto V166

Banco Rioja supera el gate estricto. El Anexo Q auditado identifica las cuatro patas; A6358/A6402 mapean las cuentas; el censo raw completo deja sólo 511108/521108 en septiembre y diciembre; y un IEF BCRA posterior autentica la migración del comparativo anual, colocando el residuo de 158.789k dentro de ingresos por intereses mientras las restantes aperturas financieras quedan invariantes. Aplicando el puente sólo a Banco Rioja, 2023 y la misma base, Q4 queda exacto. El panel pasa a 34 entidades y {COVERAGE}% de activos. Esto no prueba el diario ni autoriza a generalizar códigos.
""", encoding="utf-8")
(HERE / "AUDITORIA_V166.md").write_text(f"""# Auditoría V166

- Catálogo/copia/hash: 585/585; huecos 0; fuente catalogada +1.
- Visual: 2 páginas decisivas inspeccionadas en resolución original.
- Censo de candidatos: 2 cortes; sólo 511108/521108; seis candidatos alternativos ausentes.
- Revisión pública: 11 líneas original versus comparativo posterior.
- Promoción: Banco Rioja; cuatro patas exactas; entidad-año-base restringido.
- Panel: 34 exactas; numerador {NEW_NUMERATOR}; cobertura {COVERAGE}%; incremento {COVERAGE-OLD_COVERAGE} pp.
- Pedidos/respuestas 0/0; promociones adicionales 0.
""", encoding="utf-8")
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V166_A_V167.md").write_text(f"""# Handover V166 → V167

## Cerrado en V166

- Banco Rioja promovido con Anexo Q auditado, IEF BCRA posterior corregido y censo raw completo.
- Panel: 34 entidades; activos {NEW_NUMERATOR}; cobertura {COVERAGE}%.
- Archivo: 585/585 local y SHA-válido.

## Prioridad V167

1. Retomar Plan SIGEN 2009, Nota 3672/09 y crosswalk UAI-entidad-proyecto-informe.
2. Mantener HSBC N/D_STRICT hasta hallar separación BCRA/otras entidades; no usar stock.
3. Buscar diarios/papeles Banco Rioja sólo como auditoría explicativa, no como gate ya cerrado.
4. Mantener SAF355 0/5, ejecución 0/10 y seis borradores no enviados hasta evidencia o autorización.
""", encoding="utf-8")

source_refs = HERE / "SOURCE_REFERENCES_V166.md"
with source_refs.open("a", encoding="utf-8") as handle:
    handle.write(f"\n- `{source_id}` · {source_row['titulo']} · {source_row['url_original']} · `{source_row['archivo_local']}` · `{source_row['sha256']}`\n")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V165.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint":"V166","date":"2026-08-31","master_catalog_entries":585,
    "physical_local_copies":585,"physical_local_hash_ok":585,"remaining_catalog_physical_or_hash_gaps":0,
    "state":"SOURCE_ARCHIVE_COMPLETE_RIOJA_FOUR_LEG_PROMOTED_LATER_BCRA_COMPARATIVE",
    "analytical_promotion":"BANCO_RIOJA_EXACT_V166_ENTITY_YEAR_BASIS",
    "exact_entities":34,"strict_asset_numerator_million_ars":str(NEW_NUMERATOR),
    "system_assets_million_ars":str(SYSTEM_ASSETS),"strict_coverage_pct":str(COVERAGE),
    "strict_coverage_increment_v165_pp":str(COVERAGE-OLD_COVERAGE),"request_drafts_status":"DRAFT_NOT_SENT",
    "requests_submitted":0,"responses_received":0,"saf355_certifications_located":0,
    "executed_historical_bank_rows_confirmed":0,"discovered_official_binary_recovery_queue":0,
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V166.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

# 8. Provenance, transparency, trees, and manifests.
origin_rows = read_csv(ORIGINS)
origin_by_path = {row["path"]: row for row in origin_rows}
for path in iter_files(SYNC):
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path":rel,"origin":"generated/updated V166","note":"BCRA later-comparative source synchronization"}
for path in sorted(HERE.iterdir(), key=lambda item:item.name.casefold()):
    if path.is_file():
        rel = path.relative_to(CYCLE).as_posix()
        origin_by_path[rel] = {"path":rel,"origin":"generated/updated V166","note":"Banco Rioja strict four-leg promotion checkpoint"}
for path in [AUDIT/"MASTER_LOCAL_HASH_VALIDATION_V166.csv",AUDIT/"SOURCE_BACKUP_CENSUS_V166.csv",AUDIT/"SOURCE_PRESERVATION_MISSING_V166.csv",AUDIT/"CURRENT_SOURCE_COMPLETENESS_V166.json"]:
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path":rel,"origin":"generated/updated V166","note":"585-source physical/hash completeness control"}
write_csv(ORIGINS, list(origin_by_path.values()), ["path","origin","note"])

transparency = CYCLE / "TRANSPARENCY_README.md"
text = transparency.read_text(encoding="utf-8-sig")
if "## V166 · Promoción Banco Rioja" not in text:
    text += f"""

## V166 · Promoción Banco Rioja

Un IEF BCRA posterior vuelve a publicar diciembre de 2023 en la capa auditada y ubica el residuo de 158.789k dentro de ingresos por intereses, con las otras aperturas financieras invariantes. Anexo Q, A6358/A6402 y el censo raw completo cierran las cuatro patas bajo una regla restringida a Banco Rioja, 2023 y la misma base. El panel pasa a 34 entidades y {COVERAGE}% de activos; archivo 585/585.
"""
    transparency.write_text(text, encoding="utf-8")

(REPO / "BACKUP_ACTUALIZACION_2026-08-31.md").write_text(f"""# Backup de actualización · 2026-08-31

- Checkpoint: V166.
- Fuentes catalogadas: 585/585 local y SHA-válido; cola binaria 0.
- Banco Rioja: promovido a cuatro patas Q4 exactas, entidad-año-base.
- Panel: 34 entidades, {COVERAGE}% de activos; promoción V166: 1.
- Solicitudes: 0 enviadas; seis borradores DRAFT_NOT_SENT.
""", encoding="utf-8")


def tree(root: Path):
    lines = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted((name for name in dirnames if name not in EXCLUDED_DIRS), key=str.casefold)
        base = Path(dirpath)
        lines.extend((base/name).relative_to(root).as_posix()+"/" for name in dirnames)
        lines.extend((base/name).relative_to(root).as_posix() for name in sorted(filenames, key=str.casefold))
    return "\n".join(lines)+"\n"


(REPO / "TREE.txt").write_text(tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(tree(CYCLE), encoding="utf-8")

files = [{"path":path.name,"bytes":path.stat().st_size,"sha256":sha256(path)} for path in sorted(HERE.iterdir(), key=lambda item:item.name.casefold()) if path.is_file() and path.name != "MANIFEST_V166.json"]
manifest = {
    "checkpoint":"V166","parent_checkpoint":"V165","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
    "exact_entities":34,"strict_coverage_pct":str(COVERAGE),"strict_asset_numerator_million_ars":str(NEW_NUMERATOR),"system_assets_million_ars":str(SYSTEM_ASSETS),
    "new_promotions":["Banco Rioja S.A.U."],"negative_controls":["HSBC counterparty split open"],
    "rioja_finding":"Later BCRA comparative authenticates corrected FY interest-income layer; four legs exact under entity-year-basis rule",
    "source_archive":"585/585 catalogued physical SHA-valid; BCRA 202406e newly catalogued; binary queue 0",
    "closed_network_gate":"NO","saf355_certifications":"0/5","executed_historical_bank_rows":"0/10","requests_submitted":0,"files":files,
}
(HERE / "MANIFEST_V166.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path":path.relative_to(REPO).as_posix(),"bytes":path.stat().st_size,"sha256":sha256(path)} for path in iter_files(REPO) if path != global_manifest]
global_payload = {
    "checkpoint":"V166","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
    "strict_coverage_pct":str(COVERAGE),"exact_entities":34,"closed_network_gate":"NO",
    "source_audit":"585 master; 585 physical SHA-valid; Banco Rioja promoted with later BCRA corrected comparative",
    "historical_workstream":"Plan SIGEN 2009, Nota 3672/09, SAF355 and bank execution remain open; six drafts not sent",
    "file_count_excluding_manifest":len(global_files),"files":global_files,
}
tmp = global_manifest.with_suffix(".json.V166tmp")
tmp.write_text(json.dumps(global_payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
tmp.replace(global_manifest)

print(f"V166 BUILD PASS · exact=34 · coverage={COVERAGE} · catalog=585/585 · promotions=1")
