from __future__ import annotations

import csv
import hashlib
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
    "featured:['tab-story','tab-epica-households','tab-epica-dollars','tab-epica-caputo-colchon'",
    "households:['tab-epica-households','tab-epica-caputo-colchon'",
    "prices:['tab-epica-dollars','tab-epica-caputo-colchon'",
    "state:['tab-epica-dollars','tab-epica-caputo-colchon'",
):
    assert fragment in INDEX, f"Falta navegación temática: {fragment}"

required_downloads = (
    "income_distribution_2026_q1.csv",
    "channel_comparison.csv",
    "policy_questions_matrix.csv",
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
assert "50,1%" in ASSET and "14,5%" in ASSET

channels = rows(DERIVED / "channel_comparison.csv")
rate_by_channel = {row["canal"]: float(row["tasa_anual_referencia_pct"]) for row in channels}
assert rate_by_channel["Plazo fijo bancario USD · 60 días o más"] == 2.05
assert rate_by_channel["Letra del Tesoro de EE.UU. a 52 semanas"] == 4.14
assert "2,09 p.p." in ASSET

questions = rows(DERIVED / "policy_questions_matrix.csv")
assert any(row["tipo_de_evidencia"] == "fuera del alcance" for row in questions)
assert any("USD 5,8" in row["lectura_actual"] for row in questions)
assert all(row["limite_o_pregunta_abierta"] for row in questions)

manifest_path = RESEARCH / "source_manifest.csv"
manifest = rows(manifest_path)
assert len(manifest) == 13
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

print("OK: tab Caputo/colchón conectado, cifras consistentes y 13 fuentes respaldadas")
