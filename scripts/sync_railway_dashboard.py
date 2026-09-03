from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path

from build_political_wealth_bootstrap import build_bootstrap


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "railway-dashboard"
MAX_BUNDLE_BYTES = 25 * 1024 * 1024

PUBLIC_FILES = (
    "index.html",
    "assets/epica-super-tabs.js",
    "assets/epica-stage2-tabs.js",
    "assets/political-wealth-data.js",
    "assets/political-wealth-tab.js",
    "research/epica_dashito_2026/deep_dive_2026-08-31/derived/eph_exclusive_profiles.csv",
    "research/epica_dashito_2026/deep_dive_2026-08-31/derived/eph_strategy_summary.csv",
    "research/epica_dashito_2026/deep_dive_2026-08-31/derived/bcra_reserve_liquidity_bridge.csv",
    "research/epica_dashito_2026/deep_dive_2026-08-31/derived/reserve_measure_definitions_2026-09-01.csv",
    "research/epica_dashito_2026/deep_dive_2026-08-31/derived/debt_service_2026_2031.csv",
    "research/epica_dashito_2026/deep_dive_2026-08-31/derived/rigi_summary.csv",
    "research/epica_dashito_2026/deep_dive_2026-08-31/derived/rigi_investment_schedule.csv",
    "research/epica_dashito_2026/deep_dive_2026-08-31/derived/public_capital_accounting_inventory.csv",
    "research/epica_dashito_2026/deep_dive_2026-08-31/gap_resolution_matrix.csv",
    "research/epica_dashito_2026/fiscal_desarrollo/matriz_incidencia.csv",
    "research/epica_dashito_2026/fiscal_desarrollo/hallazgos_cuantitativos.csv",
    "research/epica_dashito_2026/hogares_credito/matriz_evidencia.csv",
    "research/epica_dashito_2026/claims_registry.csv",
    "research/epica_dashito_2026/execution_matrix.csv",
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/income_distribution_2026_q1.csv",
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/channel_comparison.csv",
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/channel_break_even_scenarios.csv",
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/bank_usd_transmission_map.csv",
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/usd_bank_intermediation_2023_2026.csv",
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/usd_channel_observed_july_2026.csv",
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/usd_prudential_framework_2026.csv",
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/policy_questions_matrix.csv",
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/deposit_account_concentration_2026_q2.json",
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/deposit_concentration_history_2023_2026.json",
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/usd_credit_line_composition_and_rates_2023_2026.json",
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/usd_credit_activity_borrower_tenor_2026.json",
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/percentage_denominator_audit.json",
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/a8467_post_policy_tracker_2026-08-31.json",
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/source_manifest.csv",
    "research/political_wealth_2026-09-01/derived/person_series_2017_2025.csv",
    "research/political_wealth_2026-09-01/derived/cohort_coverage_2017_2025.csv",
    "research/political_wealth_2026-09-01/derived/macro_deflators_2017_2025.csv",
    "research/political_wealth_2026-09-01/derived/benchmark_annual_returns_2017_2025.csv",
    "research/political_wealth_2026-09-01/derived/person_investment_benchmarks_2017_2025.csv",
    "research/political_wealth_2026-09-01/derived/asset_composition_2022_2024.csv",
    "research/political_wealth_2026-09-01/derived/annual_reconciliation_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/dashboard_data_2017_2025.json",
    "research/political_wealth_2026-09-01/derived/karina_milei_revaluation_bridge_2024_2025.csv",
    "research/political_wealth_2026-09-01/derived/karina_milei_source_consistency_audit_2023_2025.csv",
    "research/political_wealth_2026-09-01/derived/karina_milei_revaluation_audit_2023_2025.json",
    "research/political_wealth_2026-09-01/derived/javier_milei_patrimonial_bridge_2023_2025.csv",
    "research/political_wealth_2026-09-01/derived/javier_milei_revaluation_components_2025.csv",
    "research/political_wealth_2026-09-01/derived/javier_milei_source_consistency_audit_2023_2025.csv",
    "research/political_wealth_2026-09-01/derived/javier_milei_revaluation_audit_2023_2025.json",
    "research/political_wealth_2026-09-01/derived/asset_persistence_audit.csv",
    "research/political_wealth_2026-09-01/derived/viral_claim_audit.csv",
    "research/political_wealth_2026-09-01/derived/active_politicians_roster_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politicians_coverage_2026-09-01.json",
    "research/political_wealth_2026-09-01/derived/provincial_coverage_matrix_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_research_queue_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_oa_identity_review_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_oa_candidate_series_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_research_summary_2026-09-01.json",
    "research/political_wealth_2026-09-01/derived/active_politician_homonymy_candidate_audit_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_homonymy_resolutions_iteration_13_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_homonymy_resolutions_iteration_14_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_homonymy_resolutions_iteration_15_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_homonymy_resolutions_iteration_17_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_homonymy_exclusions_iteration_15_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_homonymy_exclusions_iteration_16_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_homonymy_exclusions_iteration_17_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_pen_identity_resolutions_iteration_18_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_cross_institution_resolutions_iteration_19_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_1_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_1_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_1_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_2_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_2_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_2_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_3_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_3_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_3_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_4_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_4_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_4_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_5_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_5_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_5_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_6_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_6_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_6_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_7_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_7_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_7_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_8_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_8_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_8_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_9_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_9_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_9_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_10_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_10_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_10_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_11_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_11_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_11_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_12_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_12_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_12_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_13_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_13_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_13_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_14_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_14_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_14_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_15_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_15_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_15_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_17_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_17_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_17_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_18_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_18_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_18_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_identity_audit_iteration_19_2026-09-01.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_series_iteration_19_2017_2024.csv",
    "research/political_wealth_2026-09-01/derived/active_politician_verified_benchmarks_iteration_19_2017_2024.csv",
    "research/political_wealth_2026-09-01/source_registry.csv",
    "research/political_wealth_2026-09-01/source_manifest.csv",
)

STALE_PUBLIC_FILES = (
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/policy_claims_audit.csv",
    "research/political_wealth_2026-09-01/derived/person_series.csv",
    "research/political_wealth_2026-09-01/derived/political_group_coverage.csv",
)


def digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def atomic_copy(source: Path, target: Path) -> None:
    """Publish a file without exposing a partially copied response to the web server."""
    temporary = target.with_name(f".{target.name}.{os.getpid()}.sync-tmp")
    try:
        shutil.copy2(source, temporary)
        temporary.replace(target)
    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_write_text(target: Path, content: str) -> None:
    temporary = target.with_name(f".{target.name}.{os.getpid()}.sync-tmp")
    try:
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(target)
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> None:
    build_bootstrap(quiet=True)
    for relative in STALE_PUBLIC_FILES:
        stale = BUNDLE / relative
        if stale.is_file():
            stale.unlink()

    manifest: list[dict[str, object]] = []
    for relative in PUBLIC_FILES:
        source = ROOT / relative
        target = BUNDLE / relative
        assert source.is_file(), f"Falta archivo público requerido: {source}"
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.is_file() or digest(source) != digest(target):
            atomic_copy(source, target)
        manifest.append(
            {
                "path": relative,
                "bytes": target.stat().st_size,
                "sha256": digest(target),
            }
        )

    total = sum(int(row["bytes"]) for row in manifest)
    assert total < MAX_BUNDLE_BYTES, f"El paquete creció demasiado: {total} bytes"
    payload = {
        "generated_from": "dashboard source tree",
        "public_file_count": len(manifest),
        "public_bytes": total,
        "files": manifest,
    }
    atomic_write_text(
        BUNDLE / ".bundle-manifest.json",
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    )
    print(f"OK: paquete Railway sincronizado · {len(manifest)} archivos · {total / 1024 / 1024:.2f} MiB")


if __name__ == "__main__":
    main()
