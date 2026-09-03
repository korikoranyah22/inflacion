from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "political_wealth_2026-09-01"


def rows(name: str) -> list[dict[str, str]]:
    with (RESEARCH / "derived" / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


index = (ROOT / "index.html").read_text(encoding="utf-8")
asset = (ROOT / "assets" / "political-wealth-tab.js").read_text(encoding="utf-8")
bootstrap_asset = (ROOT / "assets" / "political-wealth-data.js").read_text(encoding="utf-8")

assert index.count('<script src="assets/political-wealth-tab.js?v=20260903-38"></script>') == 1
assert index.count('<script src="assets/political-wealth-data.js?v=20260903-38"></script>') == 1
assert index.index('assets/political-wealth-data.js') < index.index('assets/political-wealth-tab.js')
assert "'tab-meli-benefits','tab-political-wealth','tab-casta']" in index
assert asset.count('<button class="tab-btn" type="button" data-tab="tab-political-wealth">') == 1
assert asset.count('id="tab-political-wealth"') == 1
assert "OA 2017–2024" in asset
assert "N/D no es cero" in asset
assert "El residual no implica irregularidad" in asset
assert "¿Se puede comparar por partido?" in asset and "sin ranking" in asset
assert "contrafactual, no explicación" in asset
assert "CAGR" in asset and "sin apalancamiento" in asset.lower()
assert "active_politicians_coverage_2026-09-01.json" in asset
assert "document.currentScript?.src" in asset
assert "async function fetchJson" in asset
assert "for(const delay of [0,180,650])" in asset
assert "window.__POLITICAL_WEALTH_BOOTSTRAP__" in asset
assert "dataset.pwDataSource = hasBootstrap?'bootstrap':'fetch'" in asset
assert bootstrap_asset.startswith("window.__POLITICAL_WEALTH_BOOTSTRAP__=")
assert 'id="pwRosterSearch"' in asset and 'id="pwActiveRosterBody"' in asset
assert 'id="pwProvincialCoverageBody"' in asset and 'id="pwProvincialIndexed"' in asset
assert "cubrir a quienes están en actividad" in asset
assert "Todos los cargos (789)" in asset
assert 'id="pwPersonViewButton"' in asset
assert "setView('coverage')" in asset
assert 'id="pwResearchQueueStatus"' in asset
assert "researchQueueById" in asset and "<th>Investigación</th>" in asset
assert "identidad_confirmada_cruce_oficial" in asset
assert "active_politician_identity_audit_iteration_1_2026-09-01.csv" in asset
assert "active_politician_identity_audit_iteration_5_2026-09-01.csv" in asset
assert "active_politician_identity_audit_iteration_6_2026-09-01.csv" in asset
assert "active_politician_identity_audit_iteration_7_2026-09-01.csv" in asset
assert "active_politician_identity_audit_iteration_8_2026-09-01.csv" in asset
assert "active_politician_identity_audit_iteration_9_2026-09-01.csv" in asset
assert "active_politician_identity_audit_iteration_10_2026-09-01.csv" in asset
assert "active_politician_identity_audit_iteration_11_2026-09-01.csv" in asset
assert "active_politician_identity_audit_iteration_12_2026-09-01.csv" in asset
assert "active_politician_identity_audit_iteration_13_2026-09-01.csv" in asset
assert "active_politician_identity_audit_iteration_14_2026-09-01.csv" in asset
assert "active_politician_identity_audit_iteration_15_2026-09-01.csv" in asset
assert "active_politician_homonymy_candidate_audit_2026-09-01.csv" in asset
assert "active_politician_homonymy_resolutions_iteration_13_2026-09-01.csv" in asset
assert "active_politician_homonymy_resolutions_iteration_14_2026-09-01.csv" in asset
assert "active_politician_homonymy_resolutions_iteration_15_2026-09-01.csv" in asset
assert "active_politician_homonymy_resolutions_iteration_17_2026-09-01.csv" in asset
assert "active_politician_homonymy_exclusions_iteration_15_2026-09-01.csv" in asset
assert "active_politician_homonymy_exclusions_iteration_16_2026-09-01.csv" in asset
assert "active_politician_homonymy_exclusions_iteration_17_2026-09-01.csv" in asset
assert "active_politician_pen_identity_resolutions_iteration_18_2026-09-01.csv" in asset
assert "active_politician_identity_audit_iteration_18_2026-09-01.csv" in asset
assert "active_politician_cross_institution_resolutions_iteration_19_2026-09-01.csv" in asset
assert "active_politician_identity_audit_iteration_19_2026-09-01.csv" in asset
assert "sin_registro_oa_2017_2024_identidad_desambiguada" in asset
assert "no representan una DDJJ del mandato provincial actual" in asset
assert 'id="pwPersonSearch"' in asset and 'id="pwPersonSelect"' in asset
assert 'id="pwPersonSearchStatus"' in asset and 'aria-live="polite"' in asset
assert "function renderPersonDirectory" in asset and "function choosePerson" in asset
assert ".pw-person-directory" in asset and "max-height:min(52svh,460px)" in asset
assert ".pw-controls{grid-template-columns:1fr;max-height:min(52svh,460px)" in asset
assert "scroll-snap-type:x proximity" not in asset
assert "overscroll-behavior:contain" in asset
assert "-webkit-overflow-scrolling:touch" in asset
assert ".pw-roster-wrap{max-height:min(65svh,540px)}" in asset
assert "window.addEventListener('resize'" not in asset
assert "window.renderPoliticalWealth = ()=>" in asset
assert "no equivalen por sí solos a la DDJJ del mandato actual" in asset
assert "789 cargos: 366 de Nación/gobernaciones y 423 bancas provinciales nominalizadas" in asset
assert 'id="pwCaseAudit"' in asset
assert "function renderCaseAudit" in asset
assert "Valuación ≠ absolución" in asset
assert "Investigación freezada" in asset
assert "karina_milei_revaluation_audit_2023_2025.json" in asset
assert "javier_milei_revaluation_audit_2023_2025.json" in asset
assert "romina_del_pla_patrimonial_audit_2023_2024.json" in asset
assert "gabriela_estevez_patrimonial_audit_2022_2024.json" in asset
assert "natalia_gadano_patrimonial_audit_2023_2024.json" in asset
assert "yolanda_vega_patrimonial_audit_2023_2024.json" in asset
assert "alejandro_bongiovanni_patrimonial_audit_2023_2024.json" in asset
assert "facundo_correa_llano_patrimonial_audit_2023_2024.json" in asset
assert "patricia_vasquez_patrimonial_audit_2023_2024.json" in asset
assert "decreto-127-1996-33500/actualizacion" in asset
assert "override.subtitulo" in asset
assert "benchmark_suspension_note" in asset
assert "benchmark_nota" in asset
assert 'id="pwCaseMetricLabel0"' in asset and 'id="pwCaseMetricValue4"' in asset
assert "audit.metricas_destacadas?.length === 5" in asset
assert "audit.columnas_puente?.length === 5" in asset
assert "active_series_source_consistency_summary_2022_2024.json" in asset
assert "function sourceConsistencyIssue" in asset
assert 'id="pwQualitySourceConsistency"' in asset
assert 'id="pwSourceControlled"' in asset and 'id="pwSourceReconciled"' in asset
assert 'id="pwSourceAssetScale"' in asset and 'id="pwSourceDebtReview"' in asset
assert 'id="pwSourceQualityCallout"' in asset
assert "sourceCheck.assetIssues.length" in asset and "sourceCheck.anyIssues" in asset
assert "function analyzeSeriesQuality" in asset
assert "benchmark_estado?.startsWith('suspendido')" in asset

series = rows("person_series_2017_2025.csv")
assert len(series) == 72
assert Counter(row["persona_id"] for row in series) == {key: 9 for key in (
    "maximo", "cristina", "massa", "macri", "caputo", "javier", "martin", "karina"
)}
assert all(row["total_bienes_ars"] == "" for row in series if row["estado_fuente"] == "no_localizada")

maximo_first = next(row for row in series if row["persona_id"] == "maximo" and row["anio"] == "2017")
maximo_last = next(row for row in series if row["persona_id"] == "maximo" and row["anio"] == "2025")
assert maximo_first["estado_fuente"] == "oficial_consolidado_oa"
assert maximo_last["estado_fuente"] == "publicado_pdf_oa_pendiente"
assert abs(float(maximo_last["indice_real_base"]) - 113.54) < 0.01
assert abs(float(maximo_last["indice_usd_base"]) - 118.46) < 0.01
javier_last = next(row for row in series if row["persona_id"] == "javier" and row["anio"] == "2025")
assert javier_last["estado_fuente"] == "publicado_pdf_oa_pendiente"
assert abs(float(javier_last["total_bienes_ars"]) - 295_182_652.87) < 0.01
assert abs(float(javier_last["deudas_ars"]) - 586_357.00) < 0.01

coverage = {row["persona_id"]: row for row in rows("cohort_coverage_2017_2025.csv")}
assert sum(int(row["anios_oficiales_2017_2024"]) for row in coverage.values()) == 39
assert coverage["maximo"]["anios_faltantes_2017_2024"] == "ninguno"
assert coverage["caputo"]["anios_faltantes_2017_2024"] == "2019|2020|2021|2022"
assert coverage["karina"]["primer_anio_con_dato"] == "2023"
assert coverage["javier"]["ultimo_anio_con_dato"] == "2025"
assert coverage["javier"]["dato_2025"] == "provisional_publicado"
assert abs(float(coverage["maximo"]["cagr_real_anual_pct"]) - 1.60) < 0.01
assert abs(float(coverage["maximo"]["cagr_usd_anual_pct"]) - 2.14) < 0.01

macro = rows("macro_deflators_2017_2025.csv")
assert len(macro) == 9
assert macro[0]["anio"] == "2017" and macro[-1]["anio"] == "2025"
assert abs(float(macro[0]["a3500_ars_por_usd"]) - 18.7742) < 0.0001
assert abs(float(macro[-1]["ipc_indice_dic_2016_100"]) - 10121.3715) < 0.0001

benchmark_annual = rows("benchmark_annual_returns_2017_2025.csv")
assert len(benchmark_annual) == 27
assert Counter(row["benchmark_id"] for row in benchmark_annual) == {
    "tbill_3m_proxy": 9,
    "vbiax_60_40": 9,
    "msci_acwi_net": 9,
}
assert next(row for row in benchmark_annual if row["benchmark_id"] == "vbiax_60_40" and row["anio"] == "2025")["retorno_total_usd_pct"] == "13.58"
assert next(row for row in benchmark_annual if row["benchmark_id"] == "msci_acwi_net" and row["anio"] == "2017")["retorno_total_usd_pct"] == "23.97"

benchmark_comparisons = rows("person_investment_benchmarks_2017_2025.csv")
assert len(benchmark_comparisons) == 24
annual_return_lookup = {
    (row["benchmark_id"], int(row["anio"])): float(row["retorno_total_usd_pct"])
    for row in benchmark_annual
}
series_by_person = defaultdict(list)
for row in series:
    if row["total_bienes_ars"]:
        series_by_person[row["persona_id"]].append(row)
for row in benchmark_comparisons:
    observed = series_by_person[row["persona_id"]]
    first, last = observed[0], observed[-1]
    start_year, end_year = int(first["anio"]), int(last["anio"])
    assert int(row["anio_inicio"]) == start_year
    assert int(row["anio_fin"]) == end_year
    assert int(row["anios_transcurridos"]) == end_year - start_year
    factor = 1.0
    for year in range(start_year + 1, end_year + 1):
        factor *= 1 + annual_return_lookup[(row["benchmark_id"], year)] / 100
    expected_cumulative = (factor - 1) * 100
    expected_cagr = (factor ** (1 / (end_year - start_year)) - 1) * 100
    expected_final_ars = (
        float(first["total_bienes_ars"])
        / float(first["a3500_ars_por_usd"])
        * factor
        * float(last["a3500_ars_por_usd"])
    )
    assert abs(float(row["benchmark_retorno_acumulado_usd_pct"]) - expected_cumulative) < 0.01
    assert abs(float(row["benchmark_cagr_usd_pct"]) - expected_cagr) < 0.01
    assert abs(float(row["capital_final_contrafactual_ars_a3500"]) - expected_final_ars) < 1.00
    assert "Sin aportes ni retiros" in row["supuesto"]
maximo_benchmarks = {row["benchmark_id"]: row for row in benchmark_comparisons if row["persona_id"] == "maximo"}
assert abs(float(maximo_benchmarks["tbill_3m_proxy"]["benchmark_cagr_usd_pct"]) - 2.69) < 0.01
assert abs(float(maximo_benchmarks["vbiax_60_40"]["benchmark_cagr_usd_pct"]) - 9.05) < 0.01
assert abs(float(maximo_benchmarks["msci_acwi_net"]["benchmark_cagr_usd_pct"]) - 10.77) < 0.01
assert all(row["anio_inicio"] == "2017" and row["anio_fin"] == "2025" for row in maximo_benchmarks.values())

composition = rows("asset_composition_2022_2024.csv")
assert len(composition) == 103
composition_totals: dict[tuple[str, str], float] = defaultdict(float)
for row in composition:
    composition_totals[(row["persona_id"], row["anio"])] += float(row["importe_ars"])
series_totals = {
    (row["persona_id"], row["anio"]): float(row["total_bienes_ars"])
    for row in series if row["total_bienes_ars"]
}
for key, total in composition_totals.items():
    assert abs(total - series_totals[key]) < 0.02

reconciliation = rows("annual_reconciliation_2017_2024.csv")
assert len(reconciliation) == 39
assert any(row["estado_calculo"] == "dato_origen_malformado" for row in reconciliation)

dashboard = json.loads((RESEARCH / "derived" / "dashboard_data_2017_2025.json").read_text(encoding="utf-8"))
assert len(dashboard["people"]) == 8
assert len(dashboard["series"]) == len(series)
assert len(dashboard["composition"]) == len(composition)
assert len(dashboard["benchmark_annual_returns"]) == len(benchmark_annual)
assert len(dashboard["benchmark_comparisons"]) == len(benchmark_comparisons)
assert dashboard["metadata"]["oficial_hasta"] == 2024

active_roster = rows("active_politicians_roster_2026-09-01.csv")
assert len(active_roster) == 789
assert len({row["persona_id"] for row in active_roster}) == 789
assert Counter(row["nivel_cargo"] for row in active_roster) == {
    "Diputados nacionales": 257,
    "Senado nacional": 72,
    "Conducción superior PEN": 13,
    "Gobernaciones": 24,
    "Legislaturas provinciales": 423,
}
active_coverage = json.loads(
    (RESEARCH / "derived" / "active_politicians_coverage_2026-09-01.json").read_text(encoding="utf-8")
)
assert len(active_coverage["rows"]) == 789
assert active_coverage["summary"]["cargos_activos"] == 789
assert active_coverage["summary"]["presentaciones_camara_localizadas"] == 229
assert active_coverage["summary"]["personas_con_nombre_compatible_unico_oa_2017_2024"] == 359
assert active_coverage["summary"]["coincidencias_oa_ambiguas"] == 18
assert active_coverage["summary"]["personas_con_serie_curada_tab"] == 5
assert active_coverage["summary"]["legisladores_provinciales_nominales"] == 423
assert active_coverage["summary"]["bancas_provinciales_suma_fichas_dne"] == 1199
assert active_coverage["summary"]["bancas_provinciales_total_intro_dne"] == 1201
assert active_coverage["summary"]["intendencias_total_dne"] == 1275
assert len(active_coverage["provincial_coverage"]) == 24
assert sum(row["bancas_total_ficha_dne"] for row in active_coverage["provincial_coverage"]) == 1199
assert sum(row["intendencias_ficha_dne"] for row in active_coverage["provincial_coverage"]) == 1275
assert sum(row["legisladores_nominales_incorporados"] for row in active_coverage["provincial_coverage"]) == 423
provincial_matrix = rows("provincial_coverage_matrix_2026-09-01.csv")
assert len(provincial_matrix) == 24
assert "no existe un padrón federal único" in active_coverage["scope"]["reason"].lower()

research_queue = rows("active_politician_research_queue_2026-09-01.csv")
identity_review = rows("active_politician_oa_identity_review_2026-09-01.csv")
candidate_series = rows("active_politician_oa_candidate_series_2017_2024.csv")
identity_audit_iteration_1 = rows("active_politician_identity_audit_iteration_1_2026-09-01.csv")
verified_series_iteration_1 = rows("active_politician_verified_series_iteration_1_2017_2024.csv")
verified_benchmarks_iteration_1 = rows("active_politician_verified_benchmarks_iteration_1_2017_2024.csv")
identity_audit_iteration_2 = rows("active_politician_identity_audit_iteration_2_2026-09-01.csv")
verified_series_iteration_2 = rows("active_politician_verified_series_iteration_2_2017_2024.csv")
verified_benchmarks_iteration_2 = rows("active_politician_verified_benchmarks_iteration_2_2017_2024.csv")
identity_audit_iteration_3 = rows("active_politician_identity_audit_iteration_3_2026-09-01.csv")
verified_series_iteration_3 = rows("active_politician_verified_series_iteration_3_2017_2024.csv")
verified_benchmarks_iteration_3 = rows("active_politician_verified_benchmarks_iteration_3_2017_2024.csv")
identity_audit_iteration_4 = rows("active_politician_identity_audit_iteration_4_2026-09-01.csv")
verified_series_iteration_4 = rows("active_politician_verified_series_iteration_4_2017_2024.csv")
verified_benchmarks_iteration_4 = rows("active_politician_verified_benchmarks_iteration_4_2017_2024.csv")
identity_audit_iteration_5 = rows("active_politician_identity_audit_iteration_5_2026-09-01.csv")
verified_series_iteration_5 = rows("active_politician_verified_series_iteration_5_2017_2024.csv")
verified_benchmarks_iteration_5 = rows("active_politician_verified_benchmarks_iteration_5_2017_2024.csv")
identity_audit_iteration_6 = rows("active_politician_identity_audit_iteration_6_2026-09-01.csv")
verified_series_iteration_6 = rows("active_politician_verified_series_iteration_6_2017_2024.csv")
verified_benchmarks_iteration_6 = rows("active_politician_verified_benchmarks_iteration_6_2017_2024.csv")
identity_audit_iteration_7 = rows("active_politician_identity_audit_iteration_7_2026-09-01.csv")
verified_series_iteration_7 = rows("active_politician_verified_series_iteration_7_2017_2024.csv")
verified_benchmarks_iteration_7 = rows("active_politician_verified_benchmarks_iteration_7_2017_2024.csv")
identity_audit_iteration_8 = rows("active_politician_identity_audit_iteration_8_2026-09-01.csv")
verified_series_iteration_8 = rows("active_politician_verified_series_iteration_8_2017_2024.csv")
verified_benchmarks_iteration_8 = rows("active_politician_verified_benchmarks_iteration_8_2017_2024.csv")
identity_audit_iteration_9 = rows("active_politician_identity_audit_iteration_9_2026-09-01.csv")
verified_series_iteration_9 = rows("active_politician_verified_series_iteration_9_2017_2024.csv")
verified_benchmarks_iteration_9 = rows("active_politician_verified_benchmarks_iteration_9_2017_2024.csv")
identity_audit_iteration_10 = rows("active_politician_identity_audit_iteration_10_2026-09-01.csv")
verified_series_iteration_10 = rows("active_politician_verified_series_iteration_10_2017_2024.csv")
verified_benchmarks_iteration_10 = rows("active_politician_verified_benchmarks_iteration_10_2017_2024.csv")
identity_audit_iteration_11 = rows("active_politician_identity_audit_iteration_11_2026-09-01.csv")
verified_series_iteration_11 = rows("active_politician_verified_series_iteration_11_2017_2024.csv")
verified_benchmarks_iteration_11 = rows("active_politician_verified_benchmarks_iteration_11_2017_2024.csv")
identity_audit_iteration_12 = rows("active_politician_identity_audit_iteration_12_2026-09-01.csv")
verified_series_iteration_12 = rows("active_politician_verified_series_iteration_12_2017_2024.csv")
verified_benchmarks_iteration_12 = rows("active_politician_verified_benchmarks_iteration_12_2017_2024.csv")
identity_audit_iteration_13 = rows("active_politician_identity_audit_iteration_13_2026-09-01.csv")
verified_series_iteration_13 = rows("active_politician_verified_series_iteration_13_2017_2024.csv")
verified_benchmarks_iteration_13 = rows("active_politician_verified_benchmarks_iteration_13_2017_2024.csv")
identity_audit_iteration_14 = rows("active_politician_identity_audit_iteration_14_2026-09-01.csv")
verified_series_iteration_14 = rows("active_politician_verified_series_iteration_14_2017_2024.csv")
verified_benchmarks_iteration_14 = rows("active_politician_verified_benchmarks_iteration_14_2017_2024.csv")
identity_audit_iteration_15 = rows("active_politician_identity_audit_iteration_15_2026-09-01.csv")
verified_series_iteration_15 = rows("active_politician_verified_series_iteration_15_2017_2024.csv")
verified_benchmarks_iteration_15 = rows("active_politician_verified_benchmarks_iteration_15_2017_2024.csv")
homonym_candidate_audit = rows("active_politician_homonymy_candidate_audit_2026-09-01.csv")
homonym_resolutions_13 = rows("active_politician_homonymy_resolutions_iteration_13_2026-09-01.csv")
homonym_resolutions_14 = rows("active_politician_homonymy_resolutions_iteration_14_2026-09-01.csv")
homonym_resolutions_15 = rows("active_politician_homonymy_resolutions_iteration_15_2026-09-01.csv")
homonym_resolutions_17 = rows("active_politician_homonymy_resolutions_iteration_17_2026-09-01.csv")
homonym_exclusions_15 = rows("active_politician_homonymy_exclusions_iteration_15_2026-09-01.csv")
homonym_exclusions_16 = rows("active_politician_homonymy_exclusions_iteration_16_2026-09-01.csv")
homonym_exclusions_17 = rows("active_politician_homonymy_exclusions_iteration_17_2026-09-01.csv")
identity_audit_iteration_17 = rows("active_politician_identity_audit_iteration_17_2026-09-01.csv")
verified_series_iteration_17 = rows("active_politician_verified_series_iteration_17_2017_2024.csv")
verified_benchmarks_iteration_17 = rows("active_politician_verified_benchmarks_iteration_17_2017_2024.csv")
pen_identity_resolutions_18 = rows("active_politician_pen_identity_resolutions_iteration_18_2026-09-01.csv")
identity_audit_iteration_18 = rows("active_politician_identity_audit_iteration_18_2026-09-01.csv")
verified_series_iteration_18 = rows("active_politician_verified_series_iteration_18_2017_2024.csv")
verified_benchmarks_iteration_18 = rows("active_politician_verified_benchmarks_iteration_18_2017_2024.csv")
cross_institution_resolutions_19 = rows("active_politician_cross_institution_resolutions_iteration_19_2026-09-01.csv")
identity_audit_iteration_19 = rows("active_politician_identity_audit_iteration_19_2026-09-01.csv")
verified_series_iteration_19 = rows("active_politician_verified_series_iteration_19_2017_2024.csv")
verified_benchmarks_iteration_19 = rows("active_politician_verified_benchmarks_iteration_19_2017_2024.csv")
research_summary = json.loads(
    (RESEARCH / "derived" / "active_politician_research_summary_2026-09-01.json").read_text(
        encoding="utf-8"
    )
)
karina_audit = json.loads(
    (RESEARCH / "derived" / "karina_milei_revaluation_audit_2023_2025.json").read_text(
        encoding="utf-8"
    )
)
karina_bridge = rows("karina_milei_revaluation_bridge_2024_2025.csv")
karina_source_audit = rows("karina_milei_source_consistency_audit_2023_2025.csv")
javier_audit = json.loads(
    (RESEARCH / "derived" / "javier_milei_revaluation_audit_2023_2025.json").read_text(
        encoding="utf-8"
    )
)
javier_bridge = rows("javier_milei_patrimonial_bridge_2023_2025.csv")
javier_components = rows("javier_milei_revaluation_components_2025.csv")
javier_source_audit = rows("javier_milei_source_consistency_audit_2023_2025.csv")
assert len(research_queue) == 789
assert len(identity_review) == 372
assert len(candidate_series) == 1417
assert research_summary["universo_cargos"] == 789
assert research_summary["personas_con_candidato_oa_unico"] == 372
assert research_summary["filas_persona_anio_oa_preseleccionadas"] == 1417
assert research_summary["preclasificaciones_fuertes_misma_institucion"] == 149
assert research_summary["homonimias_resueltas_preclasificadas"] == 14
assert research_summary["homonimias_auditadas_con_descartes"] == 7
assert research_summary["homonimias_descartadas_sin_registro_oa_compatible"] == 7
assert research_summary["homonimias_depuradas_parcialmente"] == 0
assert research_summary["primera_iteracion_revision_manual"] == 30
assert research_summary["primera_iteracion_identidades_confirmadas"] == 30
assert research_summary["segunda_iteracion_identidades_confirmadas"] == 30
assert research_summary["tercera_iteracion_identidades_confirmadas"] == 30
assert research_summary["cuarta_iteracion_identidades_confirmadas"] == 30
assert research_summary["quinta_iteracion_identidades_confirmadas"] == 29
assert research_summary["sexta_iteracion_identidades_confirmadas"] == 11
assert research_summary["septima_iteracion_identidades_confirmadas"] == 21
assert research_summary["octava_iteracion_identidades_confirmadas"] == 44
assert research_summary["novena_iteracion_identidades_confirmadas"] == 16
assert research_summary["decima_iteracion_identidades_confirmadas"] == 13
assert research_summary["undecima_iteracion_identidades_confirmadas"] == 7
assert research_summary["duodecima_iteracion_identidades_confirmadas"] == 6
assert research_summary["decimotercera_iteracion_identidades_confirmadas"] == 7
assert research_summary["decimocuarta_iteracion_identidades_confirmadas"] == 5
assert research_summary["decimoquinta_iteracion_identidades_confirmadas"] == 1
assert research_summary["decimoctava_iteracion_identidades_confirmadas"] == 8
assert research_summary["decimonovena_iteracion_identidades_confirmadas"] == 4
assert research_summary["iteraciones_completadas"] == 18
assert research_summary["ultima_iteracion_auditoria"] == 19
assert research_summary["identidades_confirmadas_por_iteracion"]["17"] == 1
assert research_summary["identidades_confirmadas_por_iteracion"]["18"] == 8
assert research_summary["identidades_confirmadas_por_iteracion"]["19"] == 4
assert research_summary["identidades_confirmadas_total"] == 293
assert research_summary["trayectorias_auditadas_dashboard"] == 301
assert research_summary["trayectorias_auditadas_activas"] == 298
assert research_summary["expansion_universo_estado"] == "freezada"
assert research_summary["expansion_universo_fecha"] == "2026-09-02"
assert research_summary["cargos_freezados"] == 491
assert research_summary["cargos_publicables"] == 298
assert Counter(row["estado_investigacion"] for row in research_queue) == {
    "cerrado_publicable": 298,
    "freezado": 491,
}
assert all(row["fecha_estado_investigacion"] == "2026-09-02" for row in research_queue)
assert research_summary["por_estado_busqueda"].get("homonimia_oa_por_resolver", 0) == 0
assert research_summary["por_estado_busqueda"].get("historial_oa_posible_cargo_nacional_previo", 0) == 0
assert research_summary["por_estado_busqueda"]["sin_registro_oa_2017_2024_identidad_desambiguada"] == 7
assert sum(int(value) for value in research_summary["por_iteracion_sugerida"].values()) == 789
assert len(karina_bridge) == 2
assert len(karina_source_audit) == 3
karina_2025 = next(row for row in karina_bridge if row["periodo"] == "2024-2025")
assert abs(float(karina_2025["valuacion_sobre_aumento_bienes_pct"]) - 102.02) < 0.01
assert abs(float(karina_2025["aumento_inmueble_pct"]) - 605.33) < 0.01
assert abs(float(karina_2025["ipc_periodo_pct"]) - 31.55) < 0.01
assert abs(float(karina_2025["aumento_inmueble_explicado_por_ipc_simple_pct"]) - 5.21) < 0.01
assert karina_audit["metadata"]["estado_2025"] == "provisional_hasta_respaldar_pdf_oa_individual"
assert "tampoco prueba corrupción" in karina_audit["lectura_epistemica"]["conclusion"].lower()
assert Counter(row["resultado"] for row in karina_source_audit) == {
    "no_concilia_factor_10": 2,
    "no_arrastra_cierre_previo": 1,
}
assert len(javier_bridge) == 3
assert len(javier_components) == 4
assert len(javier_source_audit) == 4
javier_2025 = next(row for row in javier_bridge if row["periodo"] == "2024-2025")
assert abs(float(javier_2025["aumento_bienes_real_ipc_pct"]) - 8.90) < 0.01
assert abs(float(javier_2025["valuacion_sobre_aumento_bienes_pct"]) - 81.90) < 0.01
assert abs(float(javier_2025["aumento_inmueble_pct"]) - 91.50) < 0.01
assert abs(float(javier_2025["ipc_periodo_pct"]) - 31.55) < 0.01
assert abs(float(javier_2025["residual_ajustado_fuente_ars"])) < 0.01
assert abs(sum(float(row["importe_ars"]) for row in javier_components) - 73_005_241.07) < 0.01
assert abs(sum(float(row["importe_ars"]) for row in javier_components[:3]) / 73_005_241.07 * 100 - 97.01) < 0.01
assert Counter(row["resultado"] for row in javier_source_audit) == {
    "no_concilia_factor_10": 2,
    "campo_omitido_en_consolidado": 1,
    "transcripciones_secundarias_no_coinciden": 1,
}
assert javier_audit["metadata"]["estado_2025"] == "provisional_hasta_respaldar_pdf_oa_individual"
assert abs(float(javier_audit["reconciliation_override"]["residual_ajustado_ars"])) < 0.01
assert len(identity_audit_iteration_1) == 30
assert all(row["estado_revision_identidad"] == "identidad_confirmada_cruce_oficial" for row in identity_audit_iteration_1)
assert all(row["publicable_en_tab"] == "sí" for row in identity_audit_iteration_1)
assert len(verified_series_iteration_1) == 270
assert sum(bool(row["total_bienes_ars"]) for row in verified_series_iteration_1) == 127
assert len(verified_benchmarks_iteration_1) == 72
assert Counter(row["persona_id"] for row in verified_series_iteration_1) == {
    row["persona_id"]: 9 for row in identity_audit_iteration_1
}
assert len(identity_audit_iteration_2) == 30
assert all(row["estado_revision_identidad"] == "identidad_confirmada_cruce_oficial" for row in identity_audit_iteration_2)
assert all(row["publicable_en_tab"] == "sí" for row in identity_audit_iteration_2)
assert len(verified_series_iteration_2) == 270
assert sum(bool(row["total_bienes_ars"]) for row in verified_series_iteration_2) == 140
assert len(verified_benchmarks_iteration_2) == 78
assert Counter(row["persona_id"] for row in verified_series_iteration_2) == {
    row["persona_id"]: 9 for row in identity_audit_iteration_2
}
assert len(identity_audit_iteration_3) == 30
assert all(row["estado_revision_identidad"] == "identidad_confirmada_cruce_oficial" for row in identity_audit_iteration_3)
assert all(row["publicable_en_tab"] == "sí" for row in identity_audit_iteration_3)
assert len(verified_series_iteration_3) == 270
assert sum(bool(row["total_bienes_ars"]) for row in verified_series_iteration_3) == 118
assert len(verified_benchmarks_iteration_3) == 81
assert Counter(row["persona_id"] for row in verified_series_iteration_3) == {
    row["persona_id"]: 9 for row in identity_audit_iteration_3
}
assert len(identity_audit_iteration_4) == 30
assert all(row["estado_revision_identidad"] == "identidad_confirmada_cruce_oficial" for row in identity_audit_iteration_4)
assert all(row["publicable_en_tab"] == "sí" for row in identity_audit_iteration_4)
assert Counter(row["camara"] for row in identity_audit_iteration_4) == {"Diputados": 19, "Senado": 11}
assert len(verified_series_iteration_4) == 270
assert sum(bool(row["total_bienes_ars"]) for row in verified_series_iteration_4) == 138
assert len(verified_benchmarks_iteration_4) == 75
assert Counter(row["persona_id"] for row in verified_series_iteration_4) == {
    row["persona_id"]: 9 for row in identity_audit_iteration_4
}
assert len(identity_audit_iteration_5) == 29
assert all(row["estado_revision_identidad"] == "identidad_confirmada_cruce_oficial" for row in identity_audit_iteration_5)
assert all(row["publicable_en_tab"] == "sí" for row in identity_audit_iteration_5)
assert Counter(row["camara"] for row in identity_audit_iteration_5) == {"Senado": 29}
assert Counter(row["coincidencia_nombre_presentacion"] for row in identity_audit_iteration_5) == {"exacta": 29}
assert len(verified_series_iteration_5) == 261
assert sum(bool(row["total_bienes_ars"]) for row in verified_series_iteration_5) == 118
assert len(verified_benchmarks_iteration_5) == 84
assert Counter(row["persona_id"] for row in verified_series_iteration_5) == {
    row["persona_id"]: 9 for row in identity_audit_iteration_5
}
assert len(identity_audit_iteration_6) == 11
assert all(row["estado_revision_identidad"] == "identidad_confirmada_cruce_oficial" for row in identity_audit_iteration_6)
assert all(row["publicable_en_tab"] == "sí" for row in identity_audit_iteration_6)
assert Counter(row["camara"] for row in identity_audit_iteration_6) == {"Gobernaciones": 11}
assert Counter(row["coincidencia_nombre_fuente_actual"] for row in identity_audit_iteration_6) == {"exacta_por_tokens": 11}
assert Counter(row["alcance_serie"] for row in identity_audit_iteration_6) == {
    "historial_federal_previo_no_ddjj_provincial_actual": 11
}
assert len(verified_series_iteration_6) == 99
assert sum(bool(row["total_bienes_ars"]) for row in verified_series_iteration_6) == 41
assert len(verified_benchmarks_iteration_6) == 27
assert Counter(row["persona_id"] for row in verified_series_iteration_6) == {
    row["persona_id"]: 9 for row in identity_audit_iteration_6
}
assert len(identity_audit_iteration_7) == 21
assert all(row["estado_revision_identidad"] == "identidad_confirmada_cruce_oficial" for row in identity_audit_iteration_7)
assert all(row["publicable_en_tab"] == "sí" for row in identity_audit_iteration_7)
assert Counter(row["camara"] for row in identity_audit_iteration_7) == {"Legislatura CABA": 21}
assert Counter(row["coincidencia_nombre_fuente_actual"] for row in identity_audit_iteration_7) == {
    "compatible_con_nombres_adicionales_en_oa": 13,
    "exacta_por_tokens": 8,
}
assert Counter(row["alcance_serie"] for row in identity_audit_iteration_7) == {
    "historial_publico_oa_previo_no_equivale_ddjj_mandato_actual": 21
}
assert len(verified_series_iteration_7) == 189
assert sum(bool(row["total_bienes_ars"]) for row in verified_series_iteration_7) == 77
assert len(verified_benchmarks_iteration_7) == 42
assert Counter(row["persona_id"] for row in verified_series_iteration_7) == {
    row["persona_id"]: 9 for row in identity_audit_iteration_7
}
assert len(identity_audit_iteration_8) == 45
assert Counter(row["publicable_en_tab"] for row in identity_audit_iteration_8) == {"sí": 44, "no": 1}
assert Counter(row["camara"] for row in identity_audit_iteration_8) == {"Diputados PBA": 26, "Senado PBA": 19}
assert Counter(row["coincidencia_nombre_fuente_actual"] for row in identity_audit_iteration_8) == {
    "exacta_por_tokens": 41,
    "compatible_con_nombres_adicionales_en_oa": 4,
}
assert Counter(row["alcance_serie"] for row in identity_audit_iteration_8) == {
    "historial_publico_oa_previo_no_equivale_ddjj_mandato_actual": 45
}
pba_pending = next(row for row in identity_audit_iteration_8 if row["publicable_en_tab"] == "no")
assert pba_pending["persona_id"] == "prov-ba-dip-fernandez-maria-laura"
assert pba_pending["cuit_unico_en_consolidado"] == "no"
assert len(verified_series_iteration_8) == 396
assert sum(bool(row["total_bienes_ars"]) for row in verified_series_iteration_8) == 132
assert len(verified_benchmarks_iteration_8) == 75
assert Counter(row["persona_id"] for row in verified_series_iteration_8) == {
    row["persona_id"]: 9 for row in identity_audit_iteration_8 if row["publicable_en_tab"] == "sí"
}
assert len(identity_audit_iteration_9) == 16
assert all(row["estado_revision_identidad"] == "identidad_confirmada_cruce_oficial" for row in identity_audit_iteration_9)
assert all(row["publicable_en_tab"] == "sí" for row in identity_audit_iteration_9)
assert Counter(row["camara"] for row in identity_audit_iteration_9) == {
    "Diputados Santa Fe": 15,
    "Senado Santa Fe": 1,
}
assert Counter(row["coincidencia_nombre_fuente_actual"] for row in identity_audit_iteration_9) == {
    "compatible_con_nombres_adicionales_en_oa": 9,
    "exacta_por_tokens": 7,
}
assert Counter(row["alcance_serie"] for row in identity_audit_iteration_9) == {
    "historial_publico_oa_previo_no_equivale_ddjj_mandato_actual": 16
}
assert len(verified_series_iteration_9) == 144
assert sum(bool(row["total_bienes_ars"]) for row in verified_series_iteration_9) == 46
assert len(verified_benchmarks_iteration_9) == 30
assert Counter(row["persona_id"] for row in verified_series_iteration_9) == {
    row["persona_id"]: 9 for row in identity_audit_iteration_9
}
assert len(identity_audit_iteration_10) == 14
assert Counter(row["publicable_en_tab"] for row in identity_audit_iteration_10) == {"sí": 13, "no": 1}
assert Counter(row["camara"] for row in identity_audit_iteration_10) == {"Legislatura Río Negro": 14}
assert Counter(row["coincidencia_nombre_fuente_actual"] for row in identity_audit_iteration_10) == {
    "exacta_por_tokens": 14
}
assert Counter(row["alcance_serie"] for row in identity_audit_iteration_10) == {
    "historial_publico_oa_previo_no_equivale_ddjj_mandato_actual": 14
}
rio_negro_pending = next(row for row in identity_audit_iteration_10 if row["publicable_en_tab"] == "no")
assert rio_negro_pending["persona_id"] == "prov-rn-leg-martin-juan-carlos"
assert rio_negro_pending["cuit_unico_en_consolidado"] == "no"
assert len(verified_series_iteration_10) == 117
assert sum(bool(row["total_bienes_ars"]) for row in verified_series_iteration_10) == 32
assert len(verified_benchmarks_iteration_10) == 18
assert Counter(row["persona_id"] for row in verified_series_iteration_10) == {
    row["persona_id"]: 9 for row in identity_audit_iteration_10 if row["publicable_en_tab"] == "sí"
}
assert len(identity_audit_iteration_11) == 7
assert all(row["estado_revision_identidad"] == "identidad_confirmada_cruce_oficial" for row in identity_audit_iteration_11)
assert all(row["publicable_en_tab"] == "sí" for row in identity_audit_iteration_11)
assert Counter(row["camara"] for row in identity_audit_iteration_11) == {"Legislatura Córdoba": 7}
assert Counter(row["coincidencia_nombre_fuente_actual"] for row in identity_audit_iteration_11) == {
    "exacta_por_tokens": 5,
    "compatible_con_nombres_adicionales_en_oa": 2,
}
assert Counter(row["alcance_serie"] for row in identity_audit_iteration_11) == {
    "historial_publico_oa_previo_no_equivale_ddjj_mandato_actual": 7
}
assert len(verified_series_iteration_11) == 63
assert sum(bool(row["total_bienes_ars"]) for row in verified_series_iteration_11) == 22
assert len(verified_benchmarks_iteration_11) == 9
assert Counter(row["persona_id"] for row in verified_series_iteration_11) == {
    row["persona_id"]: 9 for row in identity_audit_iteration_11
}
assert len(identity_audit_iteration_12) == 7
assert Counter(row["publicable_en_tab"] for row in identity_audit_iteration_12) == {"sí": 6, "no": 1}
assert Counter(row["camara"] for row in identity_audit_iteration_12) == {
    "Cámara de Representantes de Misiones": 7
}
assert Counter(row["coincidencia_nombre_fuente_actual"] for row in identity_audit_iteration_12) == {
    "exacta_por_tokens": 7
}
assert Counter(row["alcance_serie"] for row in identity_audit_iteration_12) == {
    "historial_publico_oa_previo_no_equivale_ddjj_mandato_actual": 7
}
misiones_pending = next(row for row in identity_audit_iteration_12 if row["publicable_en_tab"] == "no")
assert misiones_pending["persona_id"] == "prov-mis-leg-rodriguez-juan-manuel"
assert misiones_pending["cuit_unico_en_consolidado"] == "no"
assert len(verified_series_iteration_12) == 54
assert sum(bool(row["total_bienes_ars"]) for row in verified_series_iteration_12) == 8
assert len(verified_benchmarks_iteration_12) == 3
assert Counter(row["persona_id"] for row in verified_series_iteration_12) == {
    row["persona_id"]: 9 for row in identity_audit_iteration_12 if row["publicable_en_tab"] == "sí"
}
assert len(homonym_candidate_audit) == 121
assert all(len(row["oa_person_key"]) == 16 for row in homonym_candidate_audit)
assert all(row["publicable"] == "no" for row in homonym_candidate_audit)
assert len(homonym_resolutions_13) == 7
assert all(row["publicable_tras_auditoria"] == "sí" for row in homonym_resolutions_13)
assert {row["persona_id"] for row in homonym_resolutions_13} == {
    row["persona_id"] for row in identity_audit_iteration_13
}
assert len(identity_audit_iteration_13) == 7
assert all(row["estado_revision_identidad"] == "identidad_confirmada_cruce_oficial" for row in identity_audit_iteration_13)
assert all(row["publicable_en_tab"] == "sí" for row in identity_audit_iteration_13)
assert Counter(row["camara"] for row in identity_audit_iteration_13) == {
    "Diputados": 5,
    "Senado": 1,
    "Legislatura Río Negro": 1,
}
assert Counter(row["coincidencia_nombre_fuente_actual"] for row in identity_audit_iteration_13) == {
    "exacta": 5,
    "exacta_por_tokens": 2,
}
assert Counter(row["alcance_serie"] for row in identity_audit_iteration_13) == {
    "homonimia_resuelta_con_fuente_oficial": 7
}
assert len(verified_series_iteration_13) == 63
assert sum(bool(row["total_bienes_ars"]) for row in verified_series_iteration_13) == 29
assert len(verified_benchmarks_iteration_13) == 15
assert Counter(row["persona_id"] for row in verified_series_iteration_13) == {
    row["persona_id"]: 9 for row in identity_audit_iteration_13
}
assert len(homonym_resolutions_14) == 5
assert all(row["publicable_tras_auditoria"] == "sí" for row in homonym_resolutions_14)
assert {row["persona_id"] for row in homonym_resolutions_14} == {
    row["persona_id"] for row in identity_audit_iteration_14
}
assert len(identity_audit_iteration_14) == 5
assert all(row["estado_revision_identidad"] == "identidad_confirmada_cruce_oficial" for row in identity_audit_iteration_14)
assert all(row["publicable_en_tab"] == "sí" for row in identity_audit_iteration_14)
assert Counter(row["camara"] for row in identity_audit_iteration_14) == {"Diputados": 5}
assert Counter(row["coincidencia_nombre_fuente_actual"] for row in identity_audit_iteration_14) == {"exacta": 5}
assert Counter(row["alcance_serie"] for row in identity_audit_iteration_14) == {
    "homonimia_resuelta_con_fuente_oficial": 5
}
assert len(verified_series_iteration_14) == 45
assert sum(bool(row["total_bienes_ars"]) for row in verified_series_iteration_14) == 23
assert len(verified_benchmarks_iteration_14) == 15
assert Counter(row["persona_id"] for row in verified_series_iteration_14) == {
    row["persona_id"]: 9 for row in identity_audit_iteration_14
}
assert len(homonym_resolutions_15) == 1
assert homonym_resolutions_15[0]["persona_id"] == "prov-caba-leg-alonso-laura"
assert homonym_resolutions_15[0]["publicable_tras_auditoria"] == "sí"
assert len(homonym_exclusions_15) == 5
assert Counter(row["alcance_descarte"] for row in homonym_exclusions_15) == {
    "total_sin_candidato_oa_compatible": 3,
    "parcial_candidato_abreviado_permanece": 2,
}
assert all(row["publicable_en_tab"] == "no" for row in homonym_exclusions_15)
assert {row["persona_id"] for row in homonym_exclusions_15 if row["alcance_descarte"].startswith("total_")} == {
    "dip-rodriguez-miguel",
    "prov-ba-sen-lopez-roxana",
    "prov-sf-dip-rojas-sergio",
}
assert len(homonym_exclusions_16) == 3
assert all(row["alcance_descarte"] == "total_sin_candidato_oa_compatible" for row in homonym_exclusions_16)
assert all(row["cotejo_identificador_reservado"] == "sin_coincidencia" for row in homonym_exclusions_16)
assert {row["persona_id"] for row in homonym_exclusions_16} == {
    "dip-fernandez-jorge",
    "prov-sf-dip-gonzalez-marcelo",
    "prov-mis-leg-rodriguez-juan-manuel",
}
assert len(homonym_resolutions_17) == 1
assert homonym_resolutions_17[0]["persona_id"] == "dip-garcia-alvaro"
assert homonym_resolutions_17[0]["oa_nombre_resuelto"] == "GARCIA ALVARO"
assert homonym_resolutions_17[0]["publicable_tras_auditoria"] == "sí"
assert len(homonym_exclusions_17) == 1
assert all(row["alcance_descarte"] == "total_sin_candidato_oa_compatible" for row in homonym_exclusions_17)
assert all(row["cotejo_identificador_reservado"] == "sin_coincidencia" for row in homonym_exclusions_17)
assert all(row["publicable_en_tab"] == "no" for row in homonym_exclusions_17)
assert {row["persona_id"] for row in homonym_exclusions_17} == {
    "prov-ba-dip-fernandez-maria-laura",
}
exclusions_17_text = (
    RESEARCH / "derived" / "active_politician_homonymy_exclusions_iteration_17_2026-09-01.csv"
).read_text(encoding="utf-8")
assert not re.search(r"(?<![A-Za-z0-9])\d{7,11}(?![A-Za-z0-9])", exclusions_17_text)
assert len(identity_audit_iteration_15) == 1
assert identity_audit_iteration_15[0]["persona_id"] == "prov-caba-leg-alonso-laura"
assert identity_audit_iteration_15[0]["estado_revision_identidad"] == "identidad_confirmada_cruce_oficial"
assert identity_audit_iteration_15[0]["publicable_en_tab"] == "sí"
assert identity_audit_iteration_15[0]["coincidencia_nombre_fuente_actual"] == "exacta_por_tokens"
assert len(verified_series_iteration_15) == 9
assert sum(bool(row["total_bienes_ars"]) for row in verified_series_iteration_15) == 3
assert len(verified_benchmarks_iteration_15) == 3
assert len(identity_audit_iteration_17) == 1
assert identity_audit_iteration_17[0]["persona_id"] == "dip-garcia-alvaro"
assert identity_audit_iteration_17[0]["estado_revision_identidad"] == "identidad_confirmada_cruce_oficial"
assert identity_audit_iteration_17[0]["publicable_en_tab"] == "sí"
assert len(verified_series_iteration_17) == 9
assert sum(bool(row["total_bienes_ars"]) for row in verified_series_iteration_17) == 5
assert len(verified_benchmarks_iteration_17) == 3
assert len(pen_identity_resolutions_18) == 8
assert Counter(row["identificador_oficial_vs_oa"].split(" · ")[0] for row in pen_identity_resolutions_18) == {
    "sí": 7,
    "no": 1,
}
assert {row["persona_id"] for row in pen_identity_resolutions_18} == {
    row["persona_id"] for row in identity_audit_iteration_18
}
pen_resolution_text = (
    RESEARCH / "derived" / "active_politician_pen_identity_resolutions_iteration_18_2026-09-01.csv"
).read_text(encoding="utf-8")
assert not re.search(r"(?<![A-Za-z0-9])\d{7,11}(?![A-Za-z0-9])", pen_resolution_text)
assert len(identity_audit_iteration_18) == 8
assert all(row["estado_revision_identidad"] == "identidad_confirmada_cruce_oficial" for row in identity_audit_iteration_18)
assert all(row["publicable_en_tab"] == "sí" for row in identity_audit_iteration_18)
assert Counter(row["camara"] for row in identity_audit_iteration_18) == {"Conducción superior PEN": 8}
assert Counter(row["alcance_serie"] for row in identity_audit_iteration_18) == {
    "autoridad_pen_actual_con_historial_oa_2017_2024": 8
}
assert len(verified_series_iteration_18) == 72
assert sum(bool(row["total_bienes_ars"]) for row in verified_series_iteration_18) == 33
assert len(verified_benchmarks_iteration_18) == 24
assert len(cross_institution_resolutions_19) == 4
assert all(row["identificador_oficial_vs_oa"].startswith("sí") for row in cross_institution_resolutions_19)
assert {row["persona_id"] for row in cross_institution_resolutions_19} == {
    row["persona_id"] for row in identity_audit_iteration_19
}
cross_institution_text = (
    RESEARCH / "derived" / "active_politician_cross_institution_resolutions_iteration_19_2026-09-01.csv"
).read_text(encoding="utf-8")
assert not re.search(r"(?<![A-Za-z0-9])\d{7,11}(?![A-Za-z0-9])", cross_institution_text)
assert len(identity_audit_iteration_19) == 4
assert all(row["estado_revision_identidad"] == "identidad_confirmada_cruce_oficial" for row in identity_audit_iteration_19)
assert all(row["publicable_en_tab"] == "sí" for row in identity_audit_iteration_19)
assert Counter(row["camara"] for row in identity_audit_iteration_19) == {"Diputados": 2, "Senado": 2}
assert Counter(row["alcance_serie"] for row in identity_audit_iteration_19) == {
    "legislador_nacional_actual_con_historial_oa_otro_organismo": 4
}
assert len(verified_series_iteration_19) == 36
assert sum(bool(row["total_bienes_ars"]) for row in verified_series_iteration_19) == 21
assert len(verified_benchmarks_iteration_19) == 12
confirmed_audits = (
    identity_audit_iteration_1
    + identity_audit_iteration_2
    + identity_audit_iteration_3
    + identity_audit_iteration_4
    + identity_audit_iteration_5
    + identity_audit_iteration_6
    + identity_audit_iteration_7
    + [row for row in identity_audit_iteration_8 if row["publicable_en_tab"] == "sí"]
    + identity_audit_iteration_9
    + [row for row in identity_audit_iteration_10 if row["publicable_en_tab"] == "sí"]
    + identity_audit_iteration_11
    + [row for row in identity_audit_iteration_12 if row["publicable_en_tab"] == "sí"]
    + identity_audit_iteration_13
    + identity_audit_iteration_14
    + identity_audit_iteration_15
    + identity_audit_iteration_17
    + identity_audit_iteration_18
    + identity_audit_iteration_19
)
confirmed_ids = {row["persona_id"] for row in confirmed_audits}
assert len(confirmed_ids) == 293
assert sum(row["publicable_en_tab"] == "sí · identidad confirmada" for row in candidate_series if row["persona_id"] in confirmed_ids) == 1113
assert sum(row["estado_busqueda_patrimonial"] == "identidad_confirmada_cruce_oficial" for row in research_queue) == 293

bootstrap_payload = json.loads(
    bootstrap_asset.removeprefix("window.__POLITICAL_WEALTH_BOOTSTRAP__=").rstrip(";\n")
)
assert len(bootstrap_payload["data"]["people"]) == 301
assert len(bootstrap_payload["data"]["series"]) == 2709
assert len(bootstrap_payload["data"]["benchmark_comparisons"]) == 690
assert bootstrap_payload["data"]["metadata"]["ultima_iteracion_integrada"] == 19
assert bootstrap_payload["data"]["case_audits"]["karina"]["hallazgos"]["valuacion_total_sobre_aumento_bienes_2025_pct"] == 102.02
assert bootstrap_payload["data"]["case_audits"]["javier"]["hallazgos"]["valuacion_sobre_aumento_bienes_2025_pct"] == 81.9
assert bootstrap_payload["data"]["case_audits"]["dip-del-pla-romina"]["controles"]["factor_resumen_sobre_detalle_2024"] == 10.0
assert bootstrap_payload["data"]["case_audits"]["dip-estevez-gabriela-beatriz"]["controles"]["factor_resumen_sobre_detalle_cierre_2023"] == 10.0
assert bootstrap_payload["data"]["case_audits"]["dip-estevez-gabriela-beatriz"]["controles"]["cambio_nominal_detalle_2022_2023_pct"] == 646.84
assert bootstrap_payload["data"]["case_audits"]["sen-gadano-natalia-elena"]["controles"]["factor_resumen_sobre_detalle_cierre_2024"] == 10.0
assert bootstrap_payload["data"]["case_audits"]["sen-gadano-natalia-elena"]["periodos"][0]["ingreso_sobre_aumento_pct"] == 116.74
assert bootstrap_payload["data"]["case_audits"]["dip-vega-yolanda"]["controles"]["factor_resumen_sobre_detalle_inicio_2024"] == 10.0
assert bootstrap_payload["data"]["case_audits"]["dip-vega-yolanda"]["periodos"][0]["deuda_sobre_aumento_bienes_pct"] == 248.21
assert bootstrap_payload["data"]["case_audits"]["dip-bongiovanni-alejandro"]["controles"]["continuidad_cierre_inicio_brecha_ars"] == 0.0
assert bootstrap_payload["data"]["case_audits"]["dip-bongiovanni-alejandro"]["controles"]["cambio_real_2024_pct"] == 573.79
assert bootstrap_payload["data"]["case_audits"]["dip-bongiovanni-alejandro"]["periodos"][0]["ingreso_neto_sobre_aumento_pct"] == 229.49
assert bootstrap_payload["data"]["case_audits"]["dip-correa-llano-facundo"]["controles"]["valuacion_sobre_aumento_bienes_pct"] == 84.89
assert bootstrap_payload["data"]["case_audits"]["dip-correa-llano-facundo"]["controles"]["residual_puente_patrimonio_ars"] == 0.0
assert bootstrap_payload["data"]["case_audits"]["dip-correa-llano-facundo"]["reconciliation_override"]["residual_ajustado_ars"] == 0.0
assert bootstrap_payload["data"]["case_audits"]["dip-vasquez-patricia"]["controles"]["inmueble_sobre_aumento_bienes_pct"] == 87.94
assert bootstrap_payload["data"]["case_audits"]["dip-vasquez-patricia"]["controles"]["residual_valuacion_ingreso_ars"] == 0.0
assert len(bootstrap_payload["data"]["composition"]) == 133
assert len(bootstrap_payload["data"]["source_consistency"]) == 545
assert bootstrap_payload["data"]["source_consistency_summary"]["personas_controladas"] == 248
assert bootstrap_payload["data"]["source_consistency_summary"]["declaraciones_que_concilian"] == 340
assert bootstrap_payload["data"]["source_consistency_summary"]["declaraciones_bienes_con_quiebre_escala"] == 91
assert bootstrap_payload["data"]["source_consistency_summary"]["personas_bienes_con_quiebre_escala"] == 64

with (RESEARCH / "source_manifest.csv").open(encoding="utf-8", newline="") as handle:
    manifest = list(csv.DictReader(handle))
assert len(manifest) == 88
for row in manifest:
    source = RESEARCH / row["local_path"]
    assert source.stat().st_size == int(row["bytes"])
    assert sha256(source) == row["sha256"]
assert any(row["id"] == "datos_justicia_2012_2024" and int(row["bytes"]) > 100_000_000 for row in manifest)
assert any(
    row["id"] == "oa_javier_milei_ddjj_2024_mirror"
    and row["local_path"] == "sources/oa/javier_milei_ddjj_anual_2024_copia_espejo_2026-09-02.pdf"
    and int(row["bytes"]) > 100_000
    for row in manifest
)
assert any(
    row["id"] == "hcdn_ddjj_2024"
    and row["local_path"] == "sources/active_roster/hcdn_ddjj_ejercicio_2024_2026-09-03.html"
    and int(row["bytes"]) > 50_000
    for row in manifest
)
assert any(
    row["id"] == "decreto_127_1996_nuda_propiedad"
    and row["local_path"] == "sources/legal/decreto_127_1996_bienes_personales_usufructo_2026-09-03.html"
    and int(row["bytes"]) > 70_000
    for row in manifest
)
assert any(
    row["id"] == "oa_javier_milei_ddjj_2023_mirror"
    and row["local_path"] == "sources/oa/javier_milei_ddjj_anual_2023_copia_espejo_2026-09-02.pdf"
    and int(row["bytes"]) > 100_000
    for row in manifest
)

for download in (
    "person_series_2017_2025.csv",
    "cohort_coverage_2017_2025.csv",
    "macro_deflators_2017_2025.csv",
    "benchmark_annual_returns_2017_2025.csv",
    "person_investment_benchmarks_2017_2025.csv",
    "asset_composition_2022_2024.csv",
    "annual_reconciliation_2017_2024.csv",
    "dashboard_data_2017_2025.json",
    "asset_persistence_audit.csv",
    "viral_claim_audit.csv",
    "active_politicians_roster_2026-09-01.csv",
    "active_politicians_coverage_2026-09-01.json",
    "provincial_coverage_matrix_2026-09-01.csv",
    "active_politician_research_queue_2026-09-01.csv",
    "active_politician_oa_identity_review_2026-09-01.csv",
    "active_politician_oa_candidate_series_2017_2024.csv",
    "active_politician_research_summary_2026-09-01.json",
    "karina_milei_revaluation_bridge_2024_2025.csv",
    "karina_milei_source_consistency_audit_2023_2025.csv",
    "karina_milei_revaluation_audit_2023_2025.json",
    "javier_milei_patrimonial_bridge_2023_2025.csv",
    "javier_milei_revaluation_components_2025.csv",
    "javier_milei_source_consistency_audit_2023_2025.csv",
    "javier_milei_revaluation_audit_2023_2025.json",
    "romina_del_pla_source_consistency_audit_2023_2024.csv",
    "romina_del_pla_patrimonial_audit_2023_2024.json",
    "gabriela_estevez_source_consistency_audit_2022_2024.csv",
    "gabriela_estevez_patrimonial_audit_2022_2024.json",
    "natalia_gadano_source_consistency_audit_2023_2024.csv",
    "natalia_gadano_patrimonial_audit_2023_2024.json",
    "yolanda_vega_source_consistency_audit_2023_2024.csv",
    "yolanda_vega_patrimonial_audit_2023_2024.json",
    "alejandro_bongiovanni_source_consistency_audit_2023_2024.csv",
    "alejandro_bongiovanni_patrimonial_audit_2023_2024.json",
    "facundo_correa_llano_source_consistency_audit_2023_2024.csv",
    "facundo_correa_llano_patrimonial_audit_2023_2024.json",
    "patricia_vasquez_source_consistency_audit_2023_2024.csv",
    "patricia_vasquez_patrimonial_audit_2023_2024.json",
    "active_series_source_consistency_audit_2022_2024.csv",
    "active_series_source_consistency_summary_2022_2024.json",
    "active_politician_identity_audit_iteration_1_2026-09-01.csv",
    "active_politician_verified_series_iteration_1_2017_2024.csv",
    "active_politician_verified_benchmarks_iteration_1_2017_2024.csv",
    "active_politician_identity_audit_iteration_2_2026-09-01.csv",
    "active_politician_verified_series_iteration_2_2017_2024.csv",
    "active_politician_verified_benchmarks_iteration_2_2017_2024.csv",
    "active_politician_identity_audit_iteration_3_2026-09-01.csv",
    "active_politician_verified_series_iteration_3_2017_2024.csv",
    "active_politician_verified_benchmarks_iteration_3_2017_2024.csv",
    "active_politician_identity_audit_iteration_4_2026-09-01.csv",
    "active_politician_verified_series_iteration_4_2017_2024.csv",
    "active_politician_verified_benchmarks_iteration_4_2017_2024.csv",
    "active_politician_identity_audit_iteration_5_2026-09-01.csv",
    "active_politician_verified_series_iteration_5_2017_2024.csv",
    "active_politician_verified_benchmarks_iteration_5_2017_2024.csv",
    "active_politician_identity_audit_iteration_6_2026-09-01.csv",
    "active_politician_verified_series_iteration_6_2017_2024.csv",
    "active_politician_verified_benchmarks_iteration_6_2017_2024.csv",
    "active_politician_identity_audit_iteration_7_2026-09-01.csv",
    "active_politician_verified_series_iteration_7_2017_2024.csv",
    "active_politician_verified_benchmarks_iteration_7_2017_2024.csv",
    "active_politician_identity_audit_iteration_8_2026-09-01.csv",
    "active_politician_verified_series_iteration_8_2017_2024.csv",
    "active_politician_verified_benchmarks_iteration_8_2017_2024.csv",
    "active_politician_identity_audit_iteration_9_2026-09-01.csv",
    "active_politician_verified_series_iteration_9_2017_2024.csv",
    "active_politician_verified_benchmarks_iteration_9_2017_2024.csv",
    "active_politician_identity_audit_iteration_10_2026-09-01.csv",
    "active_politician_verified_series_iteration_10_2017_2024.csv",
    "active_politician_verified_benchmarks_iteration_10_2017_2024.csv",
    "active_politician_identity_audit_iteration_11_2026-09-01.csv",
    "active_politician_verified_series_iteration_11_2017_2024.csv",
    "active_politician_verified_benchmarks_iteration_11_2017_2024.csv",
    "active_politician_identity_audit_iteration_12_2026-09-01.csv",
    "active_politician_verified_series_iteration_12_2017_2024.csv",
    "active_politician_verified_benchmarks_iteration_12_2017_2024.csv",
    "active_politician_homonymy_candidate_audit_2026-09-01.csv",
    "active_politician_homonymy_resolutions_iteration_13_2026-09-01.csv",
    "active_politician_identity_audit_iteration_13_2026-09-01.csv",
    "active_politician_verified_series_iteration_13_2017_2024.csv",
    "active_politician_verified_benchmarks_iteration_13_2017_2024.csv",
    "active_politician_homonymy_resolutions_iteration_14_2026-09-01.csv",
    "active_politician_identity_audit_iteration_14_2026-09-01.csv",
    "active_politician_verified_series_iteration_14_2017_2024.csv",
    "active_politician_verified_benchmarks_iteration_14_2017_2024.csv",
    "active_politician_homonymy_resolutions_iteration_15_2026-09-01.csv",
    "active_politician_homonymy_resolutions_iteration_17_2026-09-01.csv",
    "active_politician_homonymy_exclusions_iteration_15_2026-09-01.csv",
    "active_politician_homonymy_exclusions_iteration_16_2026-09-01.csv",
    "active_politician_homonymy_exclusions_iteration_17_2026-09-01.csv",
    "active_politician_identity_audit_iteration_15_2026-09-01.csv",
    "active_politician_verified_series_iteration_15_2017_2024.csv",
    "active_politician_verified_benchmarks_iteration_15_2017_2024.csv",
    "active_politician_identity_audit_iteration_17_2026-09-01.csv",
    "active_politician_verified_series_iteration_17_2017_2024.csv",
    "active_politician_verified_benchmarks_iteration_17_2017_2024.csv",
    "active_politician_pen_identity_resolutions_iteration_18_2026-09-01.csv",
    "active_politician_identity_audit_iteration_18_2026-09-01.csv",
    "active_politician_verified_series_iteration_18_2017_2024.csv",
    "active_politician_verified_benchmarks_iteration_18_2017_2024.csv",
    "active_politician_cross_institution_resolutions_iteration_19_2026-09-01.csv",
    "active_politician_identity_audit_iteration_19_2026-09-01.csv",
    "active_politician_verified_series_iteration_19_2017_2024.csv",
    "active_politician_verified_benchmarks_iteration_19_2017_2024.csv",
    "source_registry.csv",
    "source_manifest.csv",
):
    assert download in asset

print("OK: tab Patrimonio político 2017–2025 validado")
