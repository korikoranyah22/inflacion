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
V163 = CYCLE / "checkpoints" / "V163"
SYNC = CYCLE / "inputs" / "source_sync" / "v164"
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
        dirnames[:] = sorted((name for name in dirnames if name not in EXCLUDED_DIRS), key=str.casefold)
        for filename in sorted(filenames, key=str.casefold):
            yield Path(dirpath) / filename


def clone_parent():
    excluded = {
        "build_V163.py", "qa_v163.py", "MANIFEST_V163.json", "CURRENT_STATE_V163.csv",
        "FOUR_LEG_PASS_PANEL_V163.csv", "STRICT_Q4_FOUR_LEG_COVERAGE_V163.csv",
        "README_V163.md", "VEREDICTO_V163.md", "AUDITORIA_V163.md",
        "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V163_A_V164.md", "CORRECTION_LOG_V163.md",
        "BANCO_RIOJA_ADJUSTING_ENTRY_HYPOTHESIS_V163.md",
        "BANCO_RIOJA_DUAL_RESIDUAL_RECONCILIATION_V163.csv",
        "BANCO_RIOJA_MISMATCH_ANALYTIC_NOTE_V163.md",
        "BANCO_RIOJA_PUBLIC_ROUTE_EXHAUSTION_V163.csv",
        "BANCO_RIOJA_Q4_SCENARIO_BOUND_V163.csv",
        "BANCO_RIOJA_STOCK_AND_RESULT_RECONCILIATION_V163.csv",
        "V163_PDF_VISUAL_CONTROL.csv", "V163_PUBLIC_SEARCH_LOG.csv", "V163_SOURCE_BUNDLE.csv",
    }
    for source in sorted(V163.iterdir(), key=lambda path: path.name.casefold()):
        if not source.is_file() or source.name in excluded:
            continue
        target = HERE / source.name.replace("V163", "V164")
        target.write_text(source.read_text(encoding="utf-8-sig").replace("V163", "V164"), encoding="utf-8")


clone_parent()

# 1. Validate and catalogue the five newly preserved official PDFs.
new_specs = [
    {
        "id":"banco_rioja_disciplina_mercado_q1_2023_v164", "institucion":"Banco Rioja S.A.U.",
        "titulo":"Banco Rioja · Disciplina de mercado · 31/03/2023",
        "url":"https://bancorioja.com.ar/pdf/disciplina-de-mercado/DM-31-03-23.pdf",
        "filename":"banco_rioja_disciplina_mercado_q1_2023.pdf", "period":"2023-03",
        "bytes":213194, "sha":"4c8caebb71af84ddfc2ace677ce709014c2489cce15891f4ce8b6a747743a6f8",
        "note":"V164: página física 7, pases 4.445.150k; publicación y supervisión iguales. Control de trayectoria de stock, no apertura de resultados.",
    },
    {
        "id":"banco_rioja_disciplina_mercado_6m2023_v164", "institucion":"Banco Rioja S.A.U.",
        "titulo":"Banco Rioja · Disciplina de mercado · 30/06/2023",
        "url":"https://bancorioja.com.ar/pdf/disciplina-de-mercado/DM-30-06-23.pdf",
        "filename":"banco_rioja_disciplina_mercado_6m2023.pdf", "period":"2023-06",
        "bytes":212823, "sha":"6a84eb1f98ff869dbd971ee73db804f7ce636ff6d0937b89cf4052a00ddb0fd1",
        "note":"V164: página física 7, pases 8.231.958k; publicación y supervisión iguales. Control de trayectoria de stock, no apertura de resultados.",
    },
    {
        "id":"banco_rioja_disciplina_mercado_fy2023_v164", "institucion":"Banco Rioja S.A.U.",
        "titulo":"Banco Rioja · Disciplina de mercado · 31/12/2023",
        "url":"https://bancorioja.com.ar/pdf/disciplina-de-mercado/DM-31-12-23.pdf",
        "filename":"banco_rioja_disciplina_mercado_fy2023.pdf", "period":"2023-12",
        "bytes":213039, "sha":"018214110b6402c52320b22e4df1a94f25c5c7f297b1d609540ff3ea011ec4af",
        "note":"V164: página física 7, pases 29.217.148k en publicación y supervisión. Confirma la diferencia de capa de cierre contra raw; no explica el asiento ni abre resultados.",
    },
    {
        "id":"bcra_comunicacion_a6358_plan_cuentas_v164", "institucion":"Banco Central de la República Argentina",
        "titulo":"Comunicación A 6358 · Plan de cuentas y correspondencia con estados para publicación",
        "url":"https://www.bcra.gob.ar/archivos/Pdfs/comytexord/A6358.pdf",
        "filename":"bcra_comunicacion_a6358.pdf", "period":"2018-01",
        "bytes":997703, "sha":"c6146313fd9047beef3bea53d4444a8c45b09bb63d4f4fdb9e4c61853c0765fd",
        "note":"V164: define 141144, 141222, 511108 y 521108; páginas físicas 3, 12 y 15. Páginas 32 y 38 mapean stock y resultados a los estados para publicación.",
    },
    {
        "id":"bcra_comunicacion_a6402_supervision_publicacion_v164", "institucion":"Banco Central de la República Argentina",
        "titulo":"Comunicación A 6402 · Correspondencia del plan de cuentas con supervisión y publicación",
        "url":"https://www.bcra.gob.ar/archivos/Pdfs/comytexord/A6402.pdf",
        "filename":"bcra_comunicacion_a6402.pdf", "period":"2018-01",
        "bytes":763621, "sha":"19847118057162239bd82876d722beb0095c3d4757018a185ca661f388af3b26",
        "note":"V164: páginas físicas 19, 24, 25, 29 y 31 documentan correspondencia de 141144/141222/511108/521108 en supervisión y publicación.",
    },
]
for spec in new_specs:
    path = SYNC / "binaries" / spec["filename"]
    assert path.is_file() and path.read_bytes().startswith(b"%PDF-")
    assert path.stat().st_size == spec["bytes"] and sha256(path) == spec["sha"]

catalog = read_csv(CATALOG)
catalog_fields = list(catalog[0])
catalog_by_id = {row["id"]: row for row in catalog}
for spec in new_specs:
    path = SYNC / "binaries" / spec["filename"]
    catalog_by_id[spec["id"]] = {
        "id":spec["id"], "tema":"ciclo_ajuste_bancos", "institucion":spec["institucion"],
        "titulo":spec["titulo"], "url_original":spec["url"],
        "archivo_local":"/"+path.relative_to(REPO).as_posix(), "fecha_descarga":"2026-08-31",
        "fecha_publicacion":"", "codigo_serie":"", "periodo_utilizado":spec["period"],
        "tipo":"PDF oficial · binario preservado", "sha256":spec["sha"], "nota":spec["note"],
    }
catalog = list(catalog_by_id.values())
write_csv(CATALOG, catalog, catalog_fields)
assert len(catalog) == 584

# 2. Rebuild catalog-relative source preservation audit.
audit_rows = []
for row in catalog:
    local = REPO / row["archivo_local"].lstrip("/")
    exists = local.is_file()
    actual = sha256(local) if exists else ""
    audit_rows.append({
        "id":row["id"], "archivo_local":row["archivo_local"], "exists":str(exists),
        "sha_catalog":row["sha256"].lower(), "sha_actual":actual,
        "hash_ok":str(exists and bool(row["sha256"]) and actual == row["sha256"].lower()),
    })
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V164.csv", audit_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V164.csv", audit_rows)
missing = [row for row in audit_rows if row["exists"] != "True" or row["hash_ok"] != "True"]
write_csv(AUDIT / "SOURCE_PRESERVATION_MISSING_V164.csv", missing, list(audit_rows[0]))
assert len(audit_rows) == 584 and not missing

# 3. Document the quarterly stock trajectory and the now-proven account crosswalk.
trajectory = [
    {"period":"2023-03-31","issuer_publication_stock_thousand_ars":"4445150","issuer_supervision_stock_thousand_ars":"4445150","raw_stock_thousand_ars":"N/A_NOT_PRESERVED","issuer_minus_raw":"N/A","quarter_change_issuer":"N/A","verdict":"PUBLICATION_EQUALS_SUPERVISION_STOCK"},
    {"period":"2023-06-30","issuer_publication_stock_thousand_ars":"8231958","issuer_supervision_stock_thousand_ars":"8231958","raw_stock_thousand_ars":"N/A_NOT_PRESERVED","issuer_minus_raw":"N/A","quarter_change_issuer":"3786808","verdict":"PUBLICATION_EQUALS_SUPERVISION_STOCK"},
    {"period":"2023-09-30","issuer_publication_stock_thousand_ars":"14191142","issuer_supervision_stock_thousand_ars":"14191142","raw_stock_thousand_ars":"14191142","issuer_minus_raw":"0","quarter_change_issuer":"5959184","verdict":"EXACT_PUBLICATION_SUPERVISION_RAW_STOCK"},
    {"period":"2023-12-31","issuer_publication_stock_thousand_ars":"29217148","issuer_supervision_stock_thousand_ars":"29217148","raw_stock_thousand_ars":"29058359","issuer_minus_raw":"158789","quarter_change_issuer":"15026006","verdict":"CLOSING_LAYER_DIFFERENCE_CONFIRMED_STOCK"},
]
write_csv(HERE / "BANCO_RIOJA_QUARTERLY_STOCK_TRAJECTORY_V164.csv", trajectory)

crosswalk = [
    {"account":"141144","account_meaning":"Active repos of monetary-regulation instruments with BCRA - capital","publication_mapping":"Operaciones de pase","supervision_mapping":"OCIF / BCRA / Deudores por venta contado a liquidar y pases activos","primary_support":"A6358 pp3,32; A6402 pp19,29","decision":"INCLUDE_IN_ACTIVE_REPO_STOCK"},
    {"account":"141222","account_meaning":"Accrued interest receivable on active repos with BCRA","publication_mapping":"Operaciones de pase","supervision_mapping":"OCIF / BCRA / Deudores por venta contado a liquidar y pases activos","primary_support":"A6358 pp3,32; A6402 pp19,29","decision":"INCLUDE_IN_ACTIVE_REPO_STOCK"},
    {"account":"511108","account_meaning":"Interest on active repos with BCRA","publication_mapping":"Ingresos por intereses","supervision_mapping":"Otros ingresos financieros","primary_support":"A6358 pp12,38; A6402 pp24,31","decision":"ENTITY_SPECIFIC_BCRA_INCOME_LEG"},
    {"account":"521108","account_meaning":"Interest on passive repos with BCRA","publication_mapping":"Egresos por intereses","supervision_mapping":"Otros egresos financieros","primary_support":"A6358 pp15,38; A6402 pp25,31","decision":"ENTITY_SPECIFIC_BCRA_EXPENSE_LEG"},
]
write_csv(HERE / "BCRA_ACCOUNT_AND_REPORTING_CROSSWALK_V164.csv", crosswalk)

publication_supervision = [
    {"period":"2023-03-31","line_item":"Instrumentos de pase","publication_thousand_ars":"4445150","supervision_thousand_ars":"4445150","difference":"0","source_page":"DM 31-03-23 physical 7"},
    {"period":"2023-06-30","line_item":"Instrumentos de pase","publication_thousand_ars":"8231958","supervision_thousand_ars":"8231958","difference":"0","source_page":"DM 30-06-23 physical 7"},
    {"period":"2023-09-30","line_item":"Instrumentos de pase","publication_thousand_ars":"14191142","supervision_thousand_ars":"14191142","difference":"0","source_page":"DM 30-09-23 physical 7"},
    {"period":"2023-12-31","line_item":"Instrumentos de pase","publication_thousand_ars":"29217148","supervision_thousand_ars":"29217148","difference":"0","source_page":"DM 31-12-23 physical 7"},
]
write_csv(HERE / "BANCO_RIOJA_PUBLICATION_SUPERVISION_CROSSWALK_V164.csv", publication_supervision)

timeline = [
    {"sequence":"1","event":"BCRA raw entity-detail member timestamp","date_or_timestamp":"2024-03-04 14:18:17.8813456","evidence":"202312d.7z / Entfin/Tec_Cont/baldet/00309.txt member metadata","interpretation":"Raw detail predates the signed audit; timestamp is archive-member metadata, not proof of submission date."},
    {"sequence":"2","event":"Independent auditor report date","date_or_timestamp":"2024-03-11","evidence":"Banco Rioja FY2023 audited financial statement","interpretation":"Audited package contains stock and income each 158789k above raw."},
    {"sequence":"3","event":"Annual discipline-market PDF creation metadata","date_or_timestamp":"2024-04-23 11:04:54","evidence":"DM-31-12-23.pdf metadata","interpretation":"Later issuer disclosure copies audited 29217148k into both publication and supervision columns; metadata is not formal publication-date proof."},
]
write_csv(HERE / "BANCO_RIOJA_CLOSING_LAYER_TIMELINE_V164.csv", timeline)

# 4. Carry the corrected reconciliation forward and add the closing disclosure layer.
recon = read_csv(V163 / "BANCO_RIOJA_STOCK_AND_RESULT_RECONCILIATION_V163.csv")
for index, row in enumerate(recon, start=1):
    row["control_id"] = f"BR164_{index:02d}"
    if row["measure"] == "active_repo_stock" and row["period"] == "FY-2023":
        row["verdict"] = "CLOSING_LAYER_DIFFERENCE_CONFIRMED_STOCK"
        row["analytic_use"] = "A6358/A6402 prove the account mapping; annual discipline disclosure reports 29217148 in publication and supervision, while raw detail sums 29058359. Cause and journal remain unauthenticated."
recon.append({
    "control_id":"BR164_09","period":"FY-2023","measure":"active_repo_stock_publication_vs_supervision",
    "issuer_value_thousand_ars":"29217148","raw_account_set":"DISCIPLINE_MARKET_PUBLICATION_COLUMN_VS_SUPERVISION_COLUMN",
    "raw_values_thousand_ars":"29217148_vs_29217148","raw_sum_thousand_ars":"29217148",
    "difference_issuer_minus_raw":"0","verdict":"EXACT_PUBLICATION_SUPERVISION_CLOSING_DISCLOSURE",
    "analytic_use":"Confirms the later closing disclosure layer uses the audited stock on both perimeters; does not authenticate the 158789 journal or 9M result flow.",
})
write_csv(HERE / "BANCO_RIOJA_STOCK_AND_RESULT_RECONCILIATION_V164.csv", recon)
write_csv(HERE / "BANCO_RIOJA_DUAL_RESIDUAL_RECONCILIATION_V164.csv", recon[1:4])

q4_raw_income = Decimal("14250267") - Decimal("5712151") * FACTOR
q4_adjusted_income = Decimal("14409056") - Decimal("5712151") * FACTOR
q4_expense = Decimal("7844") - Decimal("5117") * FACTOR
scenarios = [
    {"scenario":"REGULATORY_RAW_TO_RAW","q4_income_bcra_thousand_ars":str(q4_raw_income),"q4_expense_bcra_thousand_ars":str(q4_expense),"panel_use":"NO","remaining_gate":"Issuer 9M result opening absent."},
    {"scenario":"AUDITED_CLOSING_LAYER","q4_income_bcra_thousand_ars":str(q4_adjusted_income),"q4_expense_bcra_thousand_ars":str(q4_expense),"panel_use":"NO","remaining_gate":"Stock layer difference is confirmed; result adjustment and journal remain unauthenticated."},
]
write_csv(HERE / "BANCO_RIOJA_Q4_SCENARIO_BOUND_V164.csv", scenarios)

(HERE / "CORRECTION_LOG_V164.md").write_text("""# Historial de corrección V164

V164 conserva y refuerza la fe de erratas de V163: diciembre contiene `141222 = 79.394k`; el stock raw completo es `29.058.359k` y el residuo contra el cierre es `158.789k`, no `238.183k`.

La novedad es documental. A6358 y A6402 prueban que `141144 + 141222` alimentan la partida de pases en publicación y el subrubro supervisor con BCRA. La Disciplina de Mercado anual informa `29.217.148k` tanto en publicación como en supervisión. Por ello, V164 ya no trata la diferencia como una duda de mapeo: la clasifica como una **diferencia de capa de cierre confirmada en stock**. La causa y el asiento siguen sin autenticar.
""", encoding="utf-8")

(HERE / "BANCO_RIOJA_CLOSING_LAYER_NOTE_V164.md").write_text(f"""# Banco Rioja: diferencia de capa de cierre V164

## Qué quedó probado

Las comunicaciones A6358 y A6402 eliminan la ambigüedad del mapeo. `141144` es capital de pases activos con BCRA; `141222`, su interés devengado a cobrar; ambas cuentas integran la partida pública de operaciones de pase y el subrubro de supervisión BCRA. `511108` y `521108` son, respectivamente, ingreso por pases activos y egreso por pases pasivos con BCRA, y se incorporan a los resultados de publicación y supervisión.

Los cuatro estados trimestrales de Disciplina de Mercado de 2023 presentan el mismo stock en las columnas de publicación y supervisión: 4.445.150k, 8.231.958k, 14.191.142k y 29.217.148k. Septiembre coincide además con el raw. En diciembre, el raw completo suma 29.058.359k y la divulgación de cierre muestra 29.217.148k: diferencia exacta de 158.789k.

## Qué permite inferir

El archivo detallado de la entidad tiene sello interno del 4 de marzo de 2024; el informe de auditoría está fechado el 11 de marzo; la Disciplina de Mercado anual fue creada el 23 de abril y replica el valor auditado en publicación y supervisión. La secuencia es compatible con una incorporación posterior del ajuste al paquete de cierre. Los sellos de archivo y PDF sirven para ordenar evidencias, no prueban por sí solos la fecha de registración ni la naturaleza del asiento.

## Qué sigue abierto

El residuo de ingreso es también 158.789k y un asiento débito-activo/crédito-ingreso sigue siendo la explicación mínima. Pero la nueva documentación sólo autentica la **capa de stock de cierre**; no exhibe diario, comprobante, conciliación firmada ni apertura 9M de resultados. El ingreso Q4 permanece acotado entre {q4_raw_income}k y {q4_adjusted_income}k. No hay promoción.
""", encoding="utf-8")

(HERE / "BANCO_RIOJA_ADJUSTING_ENTRY_HYPOTHESIS_V164.md").write_text((HERE / "BANCO_RIOJA_CLOSING_LAYER_NOTE_V164.md").read_text(encoding="utf-8"), encoding="utf-8")
(HERE / "BANCO_RIOJA_MISMATCH_ANALYTIC_NOTE_V164.md").write_text((HERE / "BANCO_RIOJA_CLOSING_LAYER_NOTE_V164.md").read_text(encoding="utf-8"), encoding="utf-8")

# 5. Update state and strict panel without a numeric promotion.
state = read_csv(V163 / "CURRENT_STATE_V163.csv")
state_by_entity = {row["entity"]: row for row in state}
state_by_entity["Banco Rioja S.A.U."].update({
    "fy_status":"OFFICIAL_FY_AUDITED_AND_DISCIPLINE_MARKET_PUBLICATION_EQUALS_SUPERVISION_29217148K_RAW_STOCK_AND_INCOME_DUAL_RESIDUAL_158789K_V164",
    "nine_month_status":"OFFICIAL_QUARTERLY_DISCIPLINE_MARKET_STOCK_TRAJECTORY_Q1_Q2_Q3_PRESERVED_Q3_EXACT_RAW_NO_RESULT_OPENING_V164",
    "q4_four_leg_status":"N/D_STRICT_RESULT_RECONCILIATION_ABSENT_STOCK_LAYER_DIFFERENCE_CONFIRMED",
    "strict_panel_status":"PENDING", "priority":"HOLD_V164_AUTHENTICATED_RESULT_ADJUSTMENT_OR_9M_RESULT_OPENING",
    "next_action":"obtain issuer 9M-2023 result opening or signed result-side closing reconciliation/journal; stock mapping and closing publication-supervision layer are now proven",
})
write_csv(HERE / "CURRENT_STATE_V164.csv", state)

panel = read_csv(V163 / "FOUR_LEG_PASS_PANEL_V163.csv")
for row in panel:
    if row["entity"] == "Banco Rioja S.A.U.":
        row.update({
            "income_bcra":f"N/D_BOUND_RAW_{q4_raw_income}_TO_CLOSING_{q4_adjusted_income}",
            "expense_bcra":str(q4_expense), "net_bcra":"N/D", "net_otherfi":"N/D",
            "quality":"STOCK_LAYER_DIFFERENCE_CONFIRMED_RESULT_ADJUSTMENT_UNAUTHENTICATED",
            "target_basis_compatible":"YES_BASIS_STOCK_CROSSWALK_PROVEN_BUT_RESULT_BRIDGE_OPEN",
            "system_panel_eligible_v72":"NO",
            "v72_note":"V164: A6358/A6402 prove account mapping; annual DM reports 29,217,148k in publication and supervision versus raw 29,058,359k. Stock layer difference confirmed, result journal/9M opening absent; no promotion.",
        })
write_csv(HERE / "FOUR_LEG_PASS_PANEL_V164.csv", panel)

coverage = read_csv(V163 / "STRICT_Q4_FOUR_LEG_COVERAGE_V163.csv")
coverage[0]["coverage_set"] = "V164 strict 33-entity set; Banco Rioja stock layer proven but result bridge open"
if "v161_change" in coverage[0]:
    coverage[0]["v161_change"] = "V164: no numeric change; Rioja publication-supervision stock layer and account crosswalk proven, result adjustment still unauthenticated."
write_csv(HERE / "STRICT_Q4_FOUR_LEG_COVERAGE_V164.csv", coverage)

# 6. Source, endpoint and visual controls.
route_rows = [
    {"control_id":"WEB164_01","institution":"Banco Rioja","url":"https://bancorioja.com.ar/institucional/disciplina-de-mercado","result":"OFFICIAL_INDEX_EXPOSES_ALL_FOUR_2023_QUARTERS","decision":"USE_AND_ARCHIVE_MISSING_Q1_Q2_FY"},
    {"control_id":"WEB164_02","institution":"BCRA","url":"https://www.bcra.gob.ar/buscador-de-comunicaciones/","result":"OFFICIAL_SEARCH_RESULTS_LOCATED_A6358_AND_A6402","decision":"USE_AND_ARCHIVE_BOTH_QUEUE_CLOSED"},
    {"control_id":"WEB164_03","institution":"BCRA","url":"https://www.bcra.gob.ar/archivos/Pdfs/comytexord/A6358.pdf","result":"OFFICIAL_PLAN_AND_PUBLICATION_CROSSWALK_PRESERVED","decision":"USE"},
    {"control_id":"WEB164_04","institution":"BCRA","url":"https://www.bcra.gob.ar/archivos/Pdfs/comytexord/A6402.pdf","result":"OFFICIAL_SUPERVISION_AND_PUBLICATION_CROSSWALK_PRESERVED","decision":"USE"},
    {"control_id":"WEB164_05","institution":"BCRA","url":"https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Entidades/202303d.7z","result":"BINARY_DIRECT_NAVIGATION_BLOCKED_BY_CLIENT","decision":"NO_WORKAROUND_RAW_Q1_NOT_PRESERVED"},
]
write_csv(HERE / "BANCO_RIOJA_PUBLIC_ROUTE_EXHAUSTION_V164.csv", route_rows)
write_csv(HERE / "V164_PUBLIC_SEARCH_LOG.csv", route_rows)

rioja_dm9 = CYCLE / "inputs/source_sync/v162/binaries/banco_rioja_disciplina_mercado_9m2023.pdf"
rioja_fy = CYCLE / "inputs/source_sync/v161/binaries/banco_rioja_eeff_fy2023.pdf"
raw9 = CYCLE / "inputs/bcra/2023-09/informacion_entidades_financieras_open_data/202309d.7z"
rawfy = REPO / "data/fuentes/credito_consumo/bcra_entidades/historico_2023_2026/202312d.7z"
bundle_specs = [("RIOJA_DM_Q1", SYNC/"binaries"/new_specs[0]["filename"], new_specs[0]["url"]),
                ("RIOJA_DM_Q2", SYNC/"binaries"/new_specs[1]["filename"], new_specs[1]["url"]),
                ("RIOJA_DM_Q3", rioja_dm9, "https://bancorioja.com.ar/pdf/disciplina-de-mercado/DM-30-09-23.pdf"),
                ("RIOJA_DM_FY", SYNC/"binaries"/new_specs[2]["filename"], new_specs[2]["url"]),
                ("RIOJA_AUDITED_FY", rioja_fy, "https://bancorioja.com.ar/pdf/EEFF-BR-2023.pdf"),
                ("BCRA_A6358", SYNC/"binaries"/new_specs[3]["filename"], new_specs[3]["url"]),
                ("BCRA_A6402", SYNC/"binaries"/new_specs[4]["filename"], new_specs[4]["url"]),
                ("BCRA_RAW_9M", raw9, "OFFICIAL_LOCAL_ARCHIVE_ALREADY_CATALOGUED"),
                ("BCRA_RAW_FY", rawfy, "OFFICIAL_LOCAL_ARCHIVE_ALREADY_CATALOGUED")]
bundle = []
for role, path, url in bundle_specs:
    assert path.is_file()
    bundle.append({"role":role,"path":"/"+path.relative_to(REPO).as_posix(),"url":url,"bytes":str(path.stat().st_size),"sha256":sha256(path),"analytic_use":"Rioja stock-layer/account-crosswalk V164"})
write_csv(HERE / "V164_SOURCE_BUNDLE.csv", bundle)

visual = [
    {"control_id":"PV164_01","artifact":"DM-31-03-23.pdf","page":"7","result":"PASS","observation":"Pases 4,445,150 in publication and supervision."},
    {"control_id":"PV164_02","artifact":"DM-30-06-23.pdf","page":"7","result":"PASS","observation":"Pases 8,231,958 in publication and supervision."},
    {"control_id":"PV164_03","artifact":"DM-31-12-23.pdf","page":"7","result":"PASS","observation":"Pases 29,217,148 in publication and supervision."},
    {"control_id":"PV164_04","artifact":"A6358.pdf","page":"3","result":"PASS","observation":"Plan definitions for 141144 and 141222."},
    {"control_id":"PV164_05","artifact":"A6358.pdf","page":"12","result":"PASS","observation":"Plan definition for 511108."},
    {"control_id":"PV164_06","artifact":"A6358.pdf","page":"15","result":"PASS","observation":"Plan definition for 521108."},
    {"control_id":"PV164_07","artifact":"A6358.pdf","page":"32","result":"PASS","observation":"141144/141222 mapped to public repo operations."},
    {"control_id":"PV164_08","artifact":"A6358.pdf","page":"38","result":"PASS","observation":"511108/521108 mapped into public interest income/expense."},
    {"control_id":"PV164_09","artifact":"A6402.pdf","page":"19","result":"PASS","observation":"141144/141222 mapped to supervisory BCRA OCIF subrubric."},
    {"control_id":"PV164_10","artifact":"A6402.pdf","page":"24","result":"PASS","observation":"511108 appears in supervisory other financial income."},
    {"control_id":"PV164_11","artifact":"A6402.pdf","page":"25","result":"PASS","observation":"521108 appears in supervisory other financial expense."},
    {"control_id":"PV164_12","artifact":"A6402.pdf","page":"29","result":"PASS","observation":"Public repo-operation mapping includes 141144/141222."},
    {"control_id":"PV164_13","artifact":"A6402.pdf","page":"31","result":"PASS","observation":"Public interest mapping includes 511108/521108."},
]
for row in visual:
    row["method"] = "Poppler render + original-detail visual inspection"
write_csv(HERE / "V164_PDF_VISUAL_CONTROL.csv", visual)

# 7. Incremental source-sync controls.
sync_manifest = []
for spec in new_specs:
    path = SYNC / "binaries" / spec["filename"]
    sync_manifest.append({
        "role":"OFFICIAL_PDF_BINARY", "relative_path":"/"+path.relative_to(REPO).as_posix(),
        "source_url":spec["url"], "size_bytes":str(spec["bytes"]), "sha256":spec["sha"],
        "format_verification":"PDF_MAGIC_VALID_AND_RELEVANT_PAGES_VISUALLY_INSPECTED",
    })
write_csv(SYNC / "SOURCE_SYNC_FILE_MANIFEST_V164.csv", sync_manifest)
write_csv(SYNC / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V164.csv", route_rows)
(SYNC / "SOURCE_SYNC_REPORT_V164.md").write_text("""# Sincronización incremental de fuentes — V164

- Catálogo maestro: **584/584** copias locales con SHA-256 válido; brecha catalogada: **0**.
- Nuevas copias: tres Disciplina de Mercado de Banco Rioja (Q1, Q2 y FY 2023) y dos comunicaciones BCRA (A6358/A6402).
- La cola de recuperación binaria A6358/A6402 queda cerrada: **0 pendientes**.
- El raw BCRA Q1-2023 no fue preservado: la navegación directa del binario fue bloqueada y no se intentaron desvíos.
- Ninguna solicitud fue enviada; seis borradores siguen `DRAFT_NOT_SENT`.
""", encoding="utf-8")

# 8. Human-readable checkpoint.
(HERE / "README_V164.md").write_text(f"""# Checkpoint V164

- Archivo fuente catalogado: 584/584 copias locales con hash válido.
- Banco Rioja: trayectoria de stock 2023 completa en las cuatro divulgaciones oficiales.
- Cierre: 29.217.148k tanto en publicación como supervisión; raw completo 29.058.359k; diferencia 158.789k.
- A6358/A6402 prueban el mapeo de 141144, 141222, 511108 y 521108; la duda de clasificación queda cerrada.
- La diferencia de capa de cierre queda confirmada en stock, pero el asiento y el ajuste de resultado no están autenticados.
- Panel sin cambio: 33 entidades exactas; cobertura {COVERAGE}%.
- Fuentes BCRA antes pendientes: recuperadas; cola binaria 0.
- SAF355 0/5; ejecución histórica 0/10; seis borradores no enviados.
""", encoding="utf-8")
(HERE / "VEREDICTO_V164.md").write_text(f"""# Veredicto V164

V164 transforma la diferencia de Banco Rioja de una sospecha de mapeo en una diferencia de capa de cierre demostrada para el stock. Las normas BCRA ubican inequívocamente capital e interés devengado dentro de pases y vinculan los códigos de resultado con publicación y supervisión. La divulgación anual, posterior al raw y al informe de auditoría, presenta 29.217.148k en ambas columnas, 158.789k por encima del detalle raw. Pero los formularios no abren el resultado de pases ni exhiben el asiento. Por eso la explicación de débito al activo y crédito al ingreso sigue siendo la hipótesis mínima, no un hecho autenticado. Banco Rioja continúa fuera del panel; 33 entidades y {COVERAGE}%.
""", encoding="utf-8")
(HERE / "AUDITORIA_V164.md").write_text(f"""# Auditoría V164

- Catálogo/copia/hash: 584/584; huecos catalogados: 0.
- Fuentes nuevas: 5 PDF oficiales; 3 de Banco Rioja y 2 del BCRA.
- Visual: 13 páginas relevantes inspeccionadas en resolución original.
- Trayectoria: 4 cierres trimestrales; publicación = supervisión en los cuatro.
- Crosswalk: 4 cuentas con definición, mapeo público y supervisor documentados.
- Cola A6358/A6402: 2 → 0.
- Decisión: diferencia de capa de stock confirmada; ajuste de resultado no autenticado; 0 promociones.
- Panel: 33 exactas, {COVERAGE}%; pedidos/respuestas 0/0.
""", encoding="utf-8")
(HERE / "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V164_A_V165.md").write_text(f"""# Handover V164 → V165

## Cerrado en V164

- Banco Rioja: cuatro stocks trimestrales 2023 preservados; publicación y supervisión idénticas.
- A6358/A6402 preservadas; mapeo de cuentas probado; cola binaria en cero.
- Cierre stock: divulgación 29.217.148k versus raw 29.058.359k, residuo 158.789k.
- Panel sin cambio: 33 entidades, cobertura {COVERAGE}%.

## Prioridad V165

1. Buscar apertura 9M-2023 de resultados de Banco Rioja o conciliación firmada del resultado de cierre.
2. Buscar diario, comprobante o papel de trabajo del ajuste de 158.789k, ya sin dedicar esfuerzo a la clasificación contable resuelta.
3. Evaluar si existe versión revisada del detalle BCRA 202312 o una presentación rectificativa, sin eludir bloqueos de descarga.
4. Retomar Plan SIGEN 2009, Nota 3672/09 y crosswalk UAI-entidad-proyecto-informe.
5. Mantener SAF355 0/5, ejecución 0/10 y seis borradores no enviados hasta evidencia primaria o autorización.
""", encoding="utf-8")

source_refs = HERE / "SOURCE_REFERENCES_V164.md"
with source_refs.open("a", encoding="utf-8") as handle:
    for spec in new_specs:
        local = "/"+(SYNC/"binaries"/spec["filename"]).relative_to(REPO).as_posix()
        handle.write(f"\n- `{spec['id']}` · {spec['titulo']} · {spec['url']} · `{local}` · `{spec['sha']}`\n")

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V163.json").read_text(encoding="utf-8-sig"))
complete.update({
    "checkpoint":"V164", "date":"2026-08-31", "master_catalog_entries":584,
    "physical_local_copies":584, "physical_local_hash_ok":584,
    "remaining_catalog_physical_or_hash_gaps":0,
    "state":"SOURCE_ARCHIVE_COMPLETE_RIOJA_STOCK_CLOSING_LAYER_CONFIRMED_RESULT_ADJUSTMENT_UNAUTHENTICATED",
    "analytical_promotion":"NONE_V164_STOCK_LAYER_AND_ACCOUNT_CROSSWALK_ONLY",
    "exact_entities":33, "strict_asset_numerator_million_ars":str(NUMERATOR),
    "system_assets_million_ars":str(SYSTEM_ASSETS), "strict_coverage_pct":str(COVERAGE),
    "strict_coverage_increment_v163_pp":"0", "request_drafts_status":"DRAFT_NOT_SENT",
    "requests_submitted":0, "responses_received":0, "saf355_certifications_located":0,
    "executed_historical_bank_rows_confirmed":0, "discovered_official_binary_recovery_queue":0,
})
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V164.json").write_text(json.dumps(complete, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

# 9. Provenance, transparency, trees and manifests.
origin_rows = read_csv(ORIGINS)
origin_by_path = {row["path"]: row for row in origin_rows}
for path in iter_files(SYNC):
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path":rel,"origin":"generated/recovered V164","note":"Rioja quarterly disclosure or BCRA account/reporting crosswalk source"}
for path in sorted(HERE.iterdir(), key=lambda item:item.name.casefold()):
    if path.is_file():
        rel = path.relative_to(CYCLE).as_posix()
        origin_by_path[rel] = {"path":rel,"origin":"generated/updated V164","note":"V164 closing-layer and regulatory-crosswalk checkpoint"}
for path in [AUDIT/"MASTER_LOCAL_HASH_VALIDATION_V164.csv", AUDIT/"SOURCE_BACKUP_CENSUS_V164.csv", AUDIT/"SOURCE_PRESERVATION_MISSING_V164.csv", AUDIT/"CURRENT_SOURCE_COMPLETENESS_V164.json"]:
    rel = path.relative_to(CYCLE).as_posix()
    origin_by_path[rel] = {"path":rel,"origin":"generated/updated V164","note":"584-source physical/hash completeness control"}
write_csv(ORIGINS, list(origin_by_path.values()), ["path","origin","note"])

transparency = CYCLE / "TRANSPARENCY_README.md"
transparency_text = transparency.read_text(encoding="utf-8-sig")
if "## V164 · Capa de cierre Banco Rioja" not in transparency_text:
    transparency_text += """

## V164 · Capa de cierre Banco Rioja

Se preservaron las divulgaciones Q1, Q2 y FY 2023 de Banco Rioja y las comunicaciones A6358/A6402. Las cuatro divulgaciones trimestrales muestran saldos idénticos en publicación y supervisión. El cierre usa 29.217.148k, frente a 29.058.359k en el detalle raw: diferencia 158.789k. Las normas resuelven el mapeo de cuentas; no autentican el asiento ni el ajuste de resultado. El archivo queda 584/584 y la cola binaria A6358/A6402 baja a cero.
"""
    transparency.write_text(transparency_text, encoding="utf-8")

(REPO / "BACKUP_ACTUALIZACION_2026-08-31.md").write_text(f"""# Backup de actualización · 2026-08-31

- Checkpoint: V164.
- Fuentes catalogadas: 584/584 local y SHA-válido; cola binaria pendiente: 0.
- Banco Rioja: trayectoria trimestral completa; capa de cierre de stock confirmada; resultado/asiento no autenticados.
- Panel: 33 entidades, {COVERAGE}% de activos; promociones 0.
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

files = [{"path":path.name,"bytes":path.stat().st_size,"sha256":sha256(path)} for path in sorted(HERE.iterdir(), key=lambda item:item.name.casefold()) if path.is_file() and path.name != "MANIFEST_V164.json"]
manifest = {
    "checkpoint":"V164","parent_checkpoint":"V163","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
    "exact_entities":33,"strict_coverage_pct":str(COVERAGE),"strict_asset_numerator_million_ars":str(NUMERATOR),"system_assets_million_ars":str(SYSTEM_ASSETS),
    "new_promotions":[],"negative_controls":["Banco Rioja stock layer confirmed, result bridge open","HSBC counterparty split open"],
    "rioja_finding":"Publication and supervision stock both 29217148k; raw detail 29058359k; closing-layer difference 158789k",
    "source_archive":"584/584 catalogued physical SHA-valid; discovered BCRA binary queue closed 0",
    "closed_network_gate":"NO","saf355_certifications":"0/5","executed_historical_bank_rows":"0/10","requests_submitted":0,"files":files,
}
(HERE / "MANIFEST_V164.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

global_manifest = CYCLE / "MANIFEST_SHA256.json"
global_files = [{"path":path.relative_to(REPO).as_posix(),"bytes":path.stat().st_size,"sha256":sha256(path)} for path in iter_files(REPO) if path != global_manifest]
global_payload = {
    "checkpoint":"V164","created_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
    "strict_coverage_pct":str(COVERAGE),"exact_entities":33,"closed_network_gate":"NO",
    "source_audit":"584 master; 584 physical SHA-valid; Rioja stock closing layer confirmed but result adjustment open; BCRA binary queue 0",
    "historical_workstream":"Plan SIGEN 2009, Nota 3672/09, SAF355 and bank execution remain open; six drafts not sent",
    "file_count_excluding_manifest":len(global_files),"files":global_files,
}
tmp = global_manifest.with_suffix(".json.V164tmp")
tmp.write_text(json.dumps(global_payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
tmp.replace(global_manifest)

print(f"V164 BUILD PASS · exact=33 · coverage={COVERAGE} · catalog=584/584 · queue=0 · promotions=0")
