from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
ASSET = (ROOT / "assets" / "epica-super-tabs.js").read_text(encoding="utf-8")
RESEARCH = ROOT / "research" / "epica_dashito_2026" / "caputo_colchon_2026-08-31"
DERIVED = RESEARCH / "derived"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


assert ASSET.count('id="tab-epica-caputo-colchon"') == 1
assert ASSET.count('data-tab="tab-epica-caputo-colchon"') >= 1
assert "window.renderEpicaCaputo" in ASSET
assert "Punto de partida del storytelling" in ASSET
assert "paráfrasis de trabajo" in ASSET
assert "¿Qué preguntas permanecen abiertas?" in ASSET
assert '<section id="story-hypotheses"' in INDEX
assert "Hipótesis de Miyu · Caputo" in INDEX

for adversarial_label in (
    "Hipótesis que sobrevive",
    "Probado ·",
    "No probado ·",
    "Veredicto",
    "¿Está desesperado?",
):
    assert adversarial_label not in ASSET, f"Quedó una etiqueta adversarial: {adversarial_label}"

for fragment in (
    "featured:['tab-story','tab-epica-households','tab-epica-dollars','tab-epica-incidence','tab-epica-development','tab-epica-narratives','tab-epica-caputo-colchon'",
    "households:['tab-epica-households','tab-epica-incidence','tab-epica-narratives','tab-epica-caputo-colchon'",
    "prices:['tab-epica-dollars','tab-epica-narratives','tab-epica-caputo-colchon'",
    "state:['tab-epica-dollars','tab-epica-incidence','tab-epica-development','tab-epica-narratives','tab-epica-caputo-colchon'",
):
    assert fragment in INDEX, f"Falta navegación temática: {fragment}"

required_downloads = (
    "income_distribution_2026_q1.csv",
    "channel_comparison.csv",
    "channel_break_even_scenarios.csv",
    "bank_usd_transmission_map.csv",
    "usd_bank_intermediation_2023_2026.csv",
    "usd_channel_observed_july_2026.csv",
    "usd_prudential_framework_2026.csv",
    "policy_questions_matrix.csv",
    "deposit_account_concentration_2026_q2.json",
    "deposit_concentration_history_2023_2026.json",
    "usd_credit_line_composition_and_rates_2023_2026.json",
    "usd_credit_activity_borrower_tenor_2026.json",
    "percentage_denominator_audit.json",
    "a8467_post_policy_tracker_2026-08-31.json",
)
for name in required_downloads:
    path = DERIVED / name
    assert path.is_file(), f"Falta dataset: {path}"
    relative = path.relative_to(ROOT).as_posix()
    assert f'href="{relative}"' in ASSET, f"Falta descarga: {relative}"

income = rows(DERIVED / "income_distribution_2026_q1.csv")
shares = [float(row["participacion_ingreso_pct"]) for row in income]
assert len(shares) == 10
assert abs(sum(shares[:4]) - 14.5) < 0.001
assert abs(sum(shares[-2:]) - 50.1) < 0.001
assert "50,1%" in ASSET

channels = rows(DERIVED / "channel_comparison.csv")
rate_by_channel = {row["canal"]: float(row["tasa_anual_referencia_pct"]) for row in channels}
assert rate_by_channel["Plazo fijo bancario USD · 60 días o más"] == 2.05
assert rate_by_channel["Letra del Tesoro de EE.UU. a 52 semanas"] == 4.14
assert "2,09 p.p." in ASSET

questions = rows(DERIVED / "policy_questions_matrix.csv")
assert any(row["tipo_de_evidencia"] == "fuera del alcance" for row in questions)
assert any("USD 5,8" in row["lectura_actual"] for row in questions)
assert all(row["limite_o_pregunta_abierta"] for row in questions)

break_even = rows(DERIVED / "channel_break_even_scenarios.csv")
assert any(float(row["costo_incremental_anual_comitente_pct_escenario"]) == 2.09 and float(row["brecha_vs_plazo_fijo_pct"]) == 0 for row in break_even)
assert "Punto de equilibrio" in ASSET
assert "epicaCaputoBrokerCost" in ASSET

transmission = rows(DERIVED / "bank_usd_transmission_map.csv")
assert len(transmission) == 7
assert any("USD 5.800" in row["evidencia_disponible"] for row in transmission)

intermediation = rows(DERIVED / "usd_bank_intermediation_2023_2026.csv")
assert any(row["metrica"] == "préstamos / depósitos" and float(row["valor"]) == 61 for row in intermediation)
assert any(row["metrica"] == "margen hasta referencia prudente" and float(row["valor"]) == 1595 for row in intermediation)
assert "Dos techos, dos lecturas" in ASSET

observed_channels = rows(DERIVED / "usd_channel_observed_july_2026.csv")
assert sum(1 for row in observed_channels if float(row["valor_usd_millones"]) == 1000) == 2
assert "banco local y activos externos coexistieron" in ASSET

prudential = rows(DERIVED / "usd_prudential_framework_2026.csv")
assert any(row["valor"] == "15" for row in prudential)
assert any(row["valor"] == "125" for row in prudential)
assert any(row["valor"] == "1.25" for row in prudential)

concentration = json.loads((DERIVED / "deposit_account_concentration_2026_q2.json").read_text(encoding="utf-8"))
combined = next(row for row in concentration["results"] if row["instrument"] == "Combined account-instruments")
assert combined["accounts_ge_10000_pct"] == 1.1369
assert combined["balance_share_ge_10000_pct"] == 77.8873
assert "Cuentas ≥10.000 ME" in ASSET
assert "Cuentas no son personas" in ASSET

concentration_history = json.loads((DERIVED / "deposit_concentration_history_2023_2026.json").read_text(encoding="utf-8"))
history_change = concentration_history["change_2023_12_to_2026_06"]
history_end = concentration_history["results"][-1]
assert history_change["share_of_net_account_change_below_10000_pct"] == 98.8112
assert history_end["balance_share_ge_10000_pct"] == 77.8873
assert "98,81% debajo de 10.000" in ASSET

credit = json.loads((DERIVED / "usd_credit_line_composition_and_rates_2023_2026.json").read_text(encoding="utf-8"))
notes = next(row for row in credit["loan_stock_bridge"]["lines"] if row["line"] == "Single-name notes")
latest_rate = credit["rate_history"][-1]
assert notes["end_share_pct"] == 74.0726
assert notes["contribution_to_change_pct"] == 75.6229
assert latest_rate["gross_rate_gap_pp"] == 2.7001
assert "Documentos a sola firma · 74,07%" in ASSET
assert "Brecha cotizada" in ASSET

activity_credit = json.loads((DERIVED / "usd_credit_activity_borrower_tenor_2026.json").read_text(encoding="utf-8"))
activity = activity_credit["activity_stock"]
activity_shares = {row["activity"]: row["share_pct"] for row in activity["top_level_activities"]}
assert activity["combined_primary_and_manufacturing_share_pct"] == 73.7214
assert activity_shares["Primary production"] == 42.3766
assert activity_shares["Construction"] == 0.6017

borrowers = activity_credit["new_operations_by_borrower_type"]
all_flow = {row["borrower_type"]: row for row in borrowers["all_cash_loan_lines"]["borrowers"]}
notes_flow = {row["borrower_type"]: row for row in borrowers["single_name_notes"]["borrowers"]}
assert all_flow["Other legal persons"]["share_pct"] == 74.5857
assert notes_flow["Other legal persons"]["share_pct"] == 77.7173
assert notes_flow["Other legal persons"]["average_term_days"] == 150
assert notes_flow["Other legal persons"]["share_below_90_days_pct"] == 53.486
assert activity_credit["credit_conditions_survey_context"]["observed_demand_diffusion_index_pct"]["smes"] == -29.7
assert "Primaria + industria · 73,72%" in ASSET
assert "Otras personas jurídicas" in ASSET
assert "Demanda PyME · ID −29,7%" in ASSET

denominators = json.loads((DERIVED / "percentage_denominator_audit.json").read_text(encoding="utf-8"))
values = [row["value_pct"] for row in denominators["indicators"]]
assert values.count(75) == 2
assert all(value in values for value in (17, 48.6, 61, 65, 80))
assert "75% → ≈80%" in ASSET
assert "La comitente también aparece en el diagnóstico oficial" in ASSET

tracker = json.loads((DERIVED / "a8467_post_policy_tracker_2026-08-31.json").read_text(encoding="utf-8"))
regulation = tracker["regulation"]
window = tracker["observed_window"]
stocks = window["stocks_usd_millions"]
ratio = window["loan_deposit_ratio_pct"]
assert regulation["communication"] == "A 8467"
assert regulation["issuance_date"] == "2026-08-18"
assert regulation["households_eligible_under_new_bucket"] is False
assert regulation["public_bucket_identifier_in_communication"] is False
assert stocks["private_loans_total"]["change_usd_millions"] == 150
assert stocks["private_deposits_total"]["change_usd_millions"] == 188
assert stocks["private_deposits_term"]["change_usd_millions"] == 187
assert stocks["private_deposits_savings"]["change_usd_millions"] == -5
assert ratio["start"] == 62.0268
assert ratio["end"] == 62.1086
assert window["month_to_date_context"]["share_accumulated_by_issuance_pct"] == 81.9928
assert "Primer corte posterior: qué vemos y qué no" in ASSET
assert "Calendario de prueba" in ASSET
assert "+USD 188 M" in ASSET
assert "62,03% → 62,11%" in ASSET

manifest_path = RESEARCH / "source_manifest.csv"
manifest = rows(manifest_path)
assert len(manifest) == 48
for row in manifest:
    path = RESEARCH / "sources" / row["ruta_relativa"]
    assert path.is_file()
    assert path.stat().st_size == int(row["bytes"])
    assert path.stat().st_size < 100_000_000, f"Archivo incompatible con GitHub: {path}"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == row["sha256"]

assert (RESEARCH / "sources" / "bcra_tasas_depositos_series.zip").is_file()
assert not (RESEARCH / "sources" / "bcra_tasas_depositos_series.txt").exists()
assert (RESEARCH / "CAPUTO_COLCHON_RESULTS.md").is_file()

print("OK: tab Caputo/colchón conectado, seguimiento A 8467 auditado y 48 fuentes respaldadas")
