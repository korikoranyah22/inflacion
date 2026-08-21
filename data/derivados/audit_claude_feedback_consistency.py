"""Controles de regresión para los hallazgos de las tres auditorías de Claude.

El script no recalcula todo el dashboard: verifica que las cifras observadas por
Claude salgan de sus estructuras de datos, que las ventanas temporales estén
rotuladas sin ambigüedad y que no reaparezcan textos/unidades obsoletos.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


REPO = Path(__file__).resolve().parents[2]
ROOT_HTML = REPO / "index.html"
VERSION_HTML = REPO / "data" / "dashboard_kawaii_133_aporte_grandes_fortunas.html"


class AuditFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditFailure(message)


def extract_json_array(html: str, variable: str) -> list[dict[str, object]]:
    match = re.search(rf"const\s+{re.escape(variable)}=(\[.*?\]);", html, re.DOTALL)
    require(match is not None, f"No se encontró el array {variable}.")
    return json.loads(match.group(1))


def extract_numeric_array(block: str, key: str) -> list[float]:
    match = re.search(rf"\b{re.escape(key)}:\[([^\]]+)\]", block)
    require(match is not None, f"No se encontró {key} en castaInflationVsSalary.")
    return [float(value.strip()) for value in match.group(1).split(",")]


def normalize_version(html: str) -> str:
    return (
        html.replace('href="fuentes/grandes_fortunas/', 'href="data/fuentes/grandes_fortunas/')
        .replace('href="derivados/grandes_fortunas/', 'href="data/derivados/grandes_fortunas/')
        .replace("\r\n", "\n")
    )


def audit_html(path: Path) -> list[str]:
    require(path.exists(), f"Falta {path.relative_to(REPO)}.")
    html = path.read_text(encoding="utf-8")
    app_html = html[html.find("<style") :]
    checks: list[str] = []

    stale_fragments = {
        "5,2% debajo": "FBCF 2025 todavía usa el valor obsoleto de 5,2%.",
        "≈ $ 218,95 mil M": "Mercado Libre todavía muestra $218,95 mil M.",
        "$218,95 mil millones": "La prosa de Mercado Libre todavía muestra $218,95 mil M.",
        "Inflación dic-23 → jul-26": "La casta conserva el rótulo temporal ambiguo.",
        "+241.5%": "La casta conserva el IPC obsoleto de +241,5%.",
        "+241,5%": "La casta conserva el IPC obsoleto de +241,5%.",
        "≈241,7%": "La sensibilidad presidencial conserva el redondeo obsoleto de 241,7%.",
        "−31,4% real": "La casta conserva el redondeo obsoleto de −31,4%.",
        "-31.4%": "La casta conserva un porcentaje real pegado a mano.",
    }
    for fragment, error in stale_fragments.items():
        require(fragment not in app_html, error)

    investment = extract_json_array(html, "investmentReal")
    levels = {int(row["year"]): float(row["level"]) for row in investment}
    growth = {int(row["year"]): float(row["growth"]) for row in investment}
    level_change = levels[2025] / levels[2023] * 100 - 100
    require(abs(level_change - (-3.786)) < 1e-9, f"FBCF 2025 vs 2023 inesperada: {level_change:.6f}%.")
    require(abs(growth[2024] - (-17.2)) < 1e-9 and abs(growth[2025] - 16.2) < 1e-9, "Cambió la secuencia FBCF auditada.")
    for marker in ("investment2024GrowthKpi", "investment2025GrowthKpi", "investment2025LevelContext", "renderInvestmentSummary"):
        require(marker in app_html, f"La card de inversión no deriva su dato: falta {marker}.")
    checks.append("FBCF: 96,214 con base 2023=100 → −3,786%, card derivada")

    for marker in ("meliRecentTotalKpi", "meliRecentTotalProse", "const recent=meliRecentConversion()"):
        require(marker in app_html, f"Mercado Libre no comparte una única salida derivada: falta {marker}.")
    require("≈ $ 223,08 mil M" not in app_html and "$223,08 mil millones" not in app_html, "Mercado Libre volvió a hardcodear el total derivado.")
    checks.append("Mercado Libre: KPI, prosa, tabla y cuenta madre comparten meliRecentConversion()")

    casta_match = re.search(r"const\s+castaInflationVsSalary=(\{.*?\});", html, re.DOTALL)
    require(casta_match is not None, "No se encontró castaInflationVsSalary.")
    casta_block = casta_match.group(1)
    cpi = extract_numeric_array(casta_block, "cpi")[-1]
    authorities = extract_numeric_array(casta_block, "authorities")[-1]
    nominal_change = authorities - 100
    inflation_change = cpi - 100
    real_change = authorities / cpi * 100 - 100
    require(abs(nominal_change - 134.2089) < 1e-9, "Cambió la suba nominal auditada de autoridades PEN.")
    require(abs(inflation_change - 241.7984) < 1e-9, "Cambió el IPC cierre dic-23→jul-26 auditado.")
    require(abs(real_change - (-31.477474)) < 1e-6, f"Resultado real PEN inesperado: {real_change:.6f}%.")
    for marker in ("castaSummary", "castaPct", "castaNominalChangeKpi", "castaInflationChangeKpi", "castaRealChangeKpi", "penRealText"):
        require(marker in app_html, f"La casta no deriva todos sus resultados: falta {marker}.")
    checks.append("La casta: +134,2% nominal, +241,8% IPC y −31,5% real derivados")

    time_labels = (
        "dic-2019 → nov-2023",
        "dic-2023 → jul-2026",
        "IPC jul-26 vs dic-23 = 100",
        "Milei ene-2024→jul-2026",
        "meses completos",
    )
    for label in time_labels:
        require(label in app_html, f"Falta documentar la convención temporal: {label}.")
    checks.append("Ventanas: dic-2019 asignado a Alberto; mandato, cierre dic-23 y BCRA diferenciados")

    ambiguous_money = re.compile(r"\$\s*(?:\d[\d.,]*|%\{[^}]+\})\s*B\b")
    matches = sorted(set(ambiguous_money.findall(app_html)))
    require(not matches, "Notación monetaria ambigua con B: " + ", ".join(matches[:5]))
    checks.append("Unidades: no hay montos visibles expresados con la B ambigua")

    require("56 meses calendario · 55 variaciones" in app_html, "Néstor volvió a quedar rotulado como ≈55 meses sin distinguir intervalos.")
    require("13,8 M de asalariados urbanos" in app_html and "salario-base nov-2023 inferido" in app_html, "Falta la cautela sobre la escala salarial de 13,8 M.")
    checks.append("Feedback inicial: intervalos de Néstor y escala de 13,8 M documentados")

    return checks


def main() -> int:
    try:
        all_checks: list[str] = []
        for path in (ROOT_HTML, VERSION_HTML):
            all_checks.extend(f"{path.name}: {check}" for check in audit_html(path))

        root_text = ROOT_HTML.read_text(encoding="utf-8").replace("\r\n", "\n")
        version_text = normalize_version(VERSION_HTML.read_text(encoding="utf-8"))
        require(root_text == version_text, "index.html y la copia v133 difieren más allá de sus rutas relativas.")

        for check in all_checks:
            print(f"OK · {check}")
        print("OK · index.html y v133 están sincronizados")
        return 0
    except (AuditFailure, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR · {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
