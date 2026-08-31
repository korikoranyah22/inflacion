#!/usr/bin/env python3
"""Reproduce y amplía las estrategias de manutención de la EPH.

Lee exclusivamente los TXT oficiales extraídos de los ZIP archivados en
``sources/indec_eph``.  Las salidas distinguen incidencias superpuestas de
perfiles mutuamente excluyentes.  No interpreta ausencia de estrategias como
prueba presupuestaria de que el ingreso alcance para todos los gastos.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "derived" / "eph_raw"
OUT = ROOT / "derived"

FILE_PERIOD = {
    "T125": "2025-Q1",
    "T225": "2025-Q2",
    "T325": "2025-Q3",
    "T425": "2025-Q4",
    "T126": "2026-Q1",
}

PERIOD_GROUPS = {
    "2025-Q1": {"2025-Q1"},
    "2025-Q2": {"2025-Q2"},
    "2025-S1": {"2025-Q1", "2025-Q2"},
    "2025-Q3": {"2025-Q3"},
    "2025-Q4": {"2025-Q4"},
    "2025-S2": {"2025-Q3", "2025-Q4"},
    "2025": {"2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4"},
    "2026-Q1": {"2026-Q1"},
}

STRATEGY_VARS = ("V13", "V14", "V15", "V16", "V17")
CURRENT_CASH_VARS = (
    "V1",      # trabajo
    "V2",      # jubilación o pensión (pregunta paraguas)
    "V3",      # indemnización
    "V4",      # seguro de desempleo
    "V5_01",   # AUH / asignación embarazo / Alimentar
    "V5_02",   # otros planes y subsidios monetarios
    "V5_03",   # ayuda monetaria de organizaciones
    "V8",      # alquileres
    "V9",      # ganancias de negocio donde no trabaja
    "V10",     # intereses y rentas
    "V11_01",  # beca pública
    "V11_02",  # otra beca
    "V12",     # cuota alimentaria / ayuda monetaria
    "V18",     # otros ingresos en efectivo
)


def is_yes(row: dict[str, str], var: str) -> bool:
    return row.get(var, "").strip().strip('"') == "1"


def is_no(row: dict[str, str], var: str) -> bool:
    return row.get(var, "").strip().strip('"') == "2"


def number(row: dict[str, str], var: str) -> float:
    value = row.get(var, "").strip().strip('"')
    return float(value) if value else 0.0


def load_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted(RAW.rglob("usu_hogar*.txt")):
        code = next((code for code in FILE_PERIOD if code in path.name), None)
        if code is None:
            raise ValueError(f"No se reconoce el período en {path}")
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=";")
            for row in reader:
                if row.get("REALIZADA", "1").strip().strip('"') != "1":
                    continue
                row["_period"] = FILE_PERIOD[code]
                # PONDIH es el ponderador de hogares ajustado por no respuesta
                # de ingresos que reproduce los cuadros por estrato del dosier.
                row["_weight"] = str(number(row, "PONDIH"))
                rows.append(row)
    return rows


def income_stratum(row: dict[str, str]) -> str:
    itf = number(row, "ITF")
    decile_raw = row.get("DECCFR", "").strip().strip('"')
    try:
        decile = int(decile_raw)
    except ValueError:
        decile = 0
    if itf == 0 or 1 <= decile <= 4:
        return "bajo"
    if 5 <= decile <= 8:
        return "medio"
    if 9 <= decile <= 10:
        return "alto"
    return "sin_clasificar"


def strategy_flags(row: dict[str, str]) -> dict[str, bool]:
    flags = {
        "gasto_ahorros": is_yes(row, "V13"),
        "prestamo_familia_amigos": is_yes(row, "V14"),
        "prestamo_banco_financiera": is_yes(row, "V15"),
        "cuotas_o_fiado": is_yes(row, "V16"),
        "venta_pertenencias": is_yes(row, "V17"),
    }
    flags["cualquier_prestamo"] = (
        flags["prestamo_familia_amigos"] or flags["prestamo_banco_financiera"]
    )
    flags["ahorro_o_venta"] = flags["gasto_ahorros"] or flags["venta_pertenencias"]
    flags["cualquier_estrategia_v13_v17"] = any(
        flags[name]
        for name in (
            "gasto_ahorros",
            "prestamo_familia_amigos",
            "prestamo_banco_financiera",
            "cuotas_o_fiado",
            "venta_pertenencias",
        )
    )
    flags["sin_estrategias_v13_v17"] = not flags["cualquier_estrategia_v13_v17"]
    flags["solo_recursos_monetarios_corrientes_proxy"] = (
        any(is_yes(row, var) for var in CURRENT_CASH_VARS)
        and is_no(row, "V6")
        and is_no(row, "V7")
        and all(is_no(row, var) for var in STRATEGY_VARS)
    )
    flags["solo_ingreso_laboral_proxy"] = (
        is_yes(row, "V1")
        and all(is_no(row, var) for var in CURRENT_CASH_VARS if var != "V1")
        and is_no(row, "V6")
        and is_no(row, "V7")
        and all(is_no(row, var) for var in STRATEGY_VARS)
    )
    return flags


def exclusive_profile(row: dict[str, str]) -> str:
    channels = {
        "ahorro": is_yes(row, "V13"),
        "prestamos": is_yes(row, "V14") or is_yes(row, "V15"),
        "cuotas_fiado": is_yes(row, "V16"),
        "venta": is_yes(row, "V17"),
    }
    active = [name for name, value in channels.items() if value]
    if not active:
        return "ninguna_v13_v17"
    if len(active) == 1:
        return f"solo_{active[0]}"
    return "combinacion_de_2_o_mas_canales"


def bitmask_profile(row: dict[str, str]) -> str:
    names = ("ahorro", "prestamo_familia", "prestamo_banco", "cuotas_fiado", "venta")
    active = [name for name, var in zip(names, STRATEGY_VARS) if is_yes(row, var)]
    return "+".join(active) if active else "ninguna"


def weighted_summaries(rows: list[dict[str, str]]) -> None:
    metric_names = list(strategy_flags(rows[0]).keys())
    summary_rows: list[dict[str, object]] = []
    exclusive_rows: list[dict[str, object]] = []
    bitmask_rows: list[dict[str, object]] = []

    for label, component_periods in PERIOD_GROUPS.items():
        period_rows = [row for row in rows if row["_period"] in component_periods]
        for stratum in ("total", "bajo", "medio", "alto", "sin_clasificar"):
            selected = (
                period_rows
                if stratum == "total"
                else [row for row in period_rows if income_stratum(row) == stratum]
            )
            total_weight = sum(float(row["_weight"]) for row in selected)
            if total_weight == 0:
                continue

            for metric in metric_names:
                numerator = sum(
                    float(row["_weight"])
                    for row in selected
                    if strategy_flags(row)[metric]
                )
                summary_rows.append(
                    {
                        "periodo": label,
                        "estrato_ipcf": stratum,
                        "metrica": metric,
                        "porcentaje_ponderado": round(100 * numerator / total_weight, 3),
                        "hogares_expandidos_numerador": round(numerator),
                        "hogares_expandidos_denominador": round(total_weight),
                        "n_muestral": len(selected),
                    }
                )

            profile_weight: dict[str, float] = defaultdict(float)
            bitmask_weight: dict[str, float] = defaultdict(float)
            for row in selected:
                weight = float(row["_weight"])
                profile_weight[exclusive_profile(row)] += weight
                bitmask_weight[bitmask_profile(row)] += weight
            for profile, weight in sorted(profile_weight.items()):
                exclusive_rows.append(
                    {
                        "periodo": label,
                        "estrato_ipcf": stratum,
                        "perfil_exclusivo": profile,
                        "porcentaje_ponderado": round(100 * weight / total_weight, 3),
                        "hogares_expandidos": round(weight),
                        "hogares_expandidos_denominador": round(total_weight),
                        "n_muestral": len(selected),
                    }
                )
            for profile, weight in sorted(bitmask_weight.items(), key=lambda item: -item[1]):
                bitmask_rows.append(
                    {
                        "periodo": label,
                        "estrato_ipcf": stratum,
                        "combinacion_exacta": profile,
                        "porcentaje_ponderado": round(100 * weight / total_weight, 3),
                        "hogares_expandidos": round(weight),
                        "hogares_expandidos_denominador": round(total_weight),
                        "n_muestral": len(selected),
                    }
                )

    write_csv(OUT / "eph_strategy_summary.csv", summary_rows)
    write_csv(OUT / "eph_exclusive_profiles.csv", exclusive_rows)
    write_csv(OUT / "eph_exact_bitmasks.csv", bitmask_rows)

    indexed = {
        (row["periodo"], row["estrato_ipcf"], row["metrica"]): row["porcentaje_ponderado"]
        for row in summary_rows
    }
    published_checks = {
        "gasto_ahorros": 37.4,
        "cualquier_prestamo": 25.5,
        "cuotas_o_fiado": 50.9,
        "ahorro_o_venta": 40.8,
    }
    for metric, expected in published_checks.items():
        actual = float(indexed[("2025-S1", "total", metric)])
        if abs(actual - expected) > 0.15:
            raise AssertionError(
                f"La réplica 2025-S1 de {metric} dio {actual:.3f}%, "
                f"lejos del {expected:.1f}% publicado"
            )


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Sin filas para {path}")
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = load_rows()
    if not rows:
        raise RuntimeError("No se encontraron hogares EPH")
    weighted_summaries(rows)
    print(f"OK: {len(rows):,} registros hogar procesados")
    print("OK: réplica 2025-S1 dentro de 0,15 puntos porcentuales")


if __name__ == "__main__":
    main()
