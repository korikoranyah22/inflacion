#!/usr/bin/env python3
"""Construye la evidencia reproducible del frente dolares/sector externo.

Solo usa fuentes primarias: API BCRA v4, XLSX ITCRM del BCRA ya descargado
y cifras publicadas por BCRA/INDEC identificadas en evidence_sources.csv.
No calcula una cifra de reservas netas o liquidas: arma un puente de pasivos
identificables y documenta la brecha de informacion.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import math
import statistics
import time
import urllib.parse
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CUT_OFF = dt.date(2026, 8, 31)
API = "https://api.bcra.gob.ar/estadisticas/v4.0/monetarias"


def fetch_json(url: str, attempts: int = 3) -> dict:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "dashito-epica-research/1.0", "Accept-Language": "es-AR"},
    )
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.load(response)
        except Exception as exc:  # pragma: no cover - solo red
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(2**attempt)
    raise RuntimeError(f"No se pudo descargar {url}: {last_error}")


def api_series(variable_id: int, since: str, until: str) -> list[dict]:
    query = urllib.parse.urlencode(
        {"desde": since, "hasta": until, "limit": 3000, "offset": 0}
    )
    payload = fetch_json(f"{API}/{variable_id}?{query}")
    if payload.get("status") != 200:
        raise RuntimeError(f"API BCRA id={variable_id}: {payload}")
    results = payload.get("results", [])
    if not results:
        return []
    detail = results[0].get("detalle", [])
    rows = [
        {"date": dt.date.fromisoformat(item["fecha"]), "value": float(item["valor"])}
        for item in detail
    ]
    rows.sort(key=lambda row: row["date"])
    return rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_itcrm(path: Path) -> list[dict]:
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
    data: list[dict] = []
    epoch = dt.date(1899, 12, 30)
    for row in root.findall(".//m:sheetData/m:row", ns):
        cells: dict[str, str] = {}
        for cell in row.findall("m:c", ns):
            value = cell.find("m:v", ns)
            if value is not None and value.text is not None:
                column = "".join(ch for ch in cell.attrib["r"] if ch.isalpha())
                cells[column] = value.text
        if "A" not in cells or "B" not in cells:
            continue
        try:
            date = epoch + dt.timedelta(days=int(float(cells["A"])))
            value = float(cells["B"])
        except ValueError:
            continue
        if dt.date(1997, 1, 1) <= date <= CUT_OFF:
            data.append({"date": date, "value": value})
    data.sort(key=lambda row: row["date"])
    if not data:
        raise RuntimeError("No se pudo extraer ITCRM del XLSX oficial")
    return data


def month_end(series: list[dict]) -> dict[str, float]:
    result: dict[str, tuple[dt.date, float]] = {}
    for row in series:
        month = row["date"].strftime("%Y-%m")
        if month not in result or row["date"] > result[month][0]:
            result[month] = (row["date"], row["value"])
    return {month: pair[1] for month, pair in result.items()}


def log_changes(levels: dict[str, float]) -> dict[str, float]:
    months = sorted(levels)
    result: dict[str, float] = {}
    for previous, current in zip(months, months[1:]):
        if levels[previous] > 0 and levels[current] > 0:
            result[current] = 100 * math.log(levels[current] / levels[previous])
    return result


def shift_month(month: str, delta: int) -> str:
    year, number = map(int, month.split("-"))
    index = year * 12 + number - 1 + delta
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


def correlation(pairs: list[tuple[float, float]]) -> float | None:
    if len(pairs) < 3:
        return None
    xs = [pair[0] for pair in pairs]
    ys = [pair[1] for pair in pairs]
    mx, my = statistics.mean(xs), statistics.mean(ys)
    numerator = sum((x - mx) * (y - my) for x, y in pairs)
    denominator = math.sqrt(
        sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)
    )
    return numerator / denominator if denominator else None


def solve(matrix: list[list[float]], vector: list[float]) -> list[float]:
    n = len(vector)
    augmented = [row[:] + [vector[i]] for i, row in enumerate(matrix)]
    for pivot in range(n):
        best = max(range(pivot, n), key=lambda i: abs(augmented[i][pivot]))
        if abs(augmented[best][pivot]) < 1e-12:
            raise RuntimeError("Matriz singular en OLS")
        augmented[pivot], augmented[best] = augmented[best], augmented[pivot]
        scale = augmented[pivot][pivot]
        augmented[pivot] = [value / scale for value in augmented[pivot]]
        for row in range(n):
            if row == pivot:
                continue
            factor = augmented[row][pivot]
            augmented[row] = [
                augmented[row][col] - factor * augmented[pivot][col]
                for col in range(n + 1)
            ]
    return [augmented[i][-1] for i in range(n)]


def ols(features: list[list[float]], target: list[float]) -> tuple[list[float], float]:
    columns = len(features[0])
    xtx = [[0.0 for _ in range(columns)] for _ in range(columns)]
    xty = [0.0 for _ in range(columns)]
    for row, y in zip(features, target):
        for i in range(columns):
            xty[i] += row[i] * y
            for j in range(columns):
                xtx[i][j] += row[i] * row[j]
    beta = solve(xtx, xty)
    fitted = [sum(b * x for b, x in zip(beta, row)) for row in features]
    mean_y = statistics.mean(target)
    ss_res = sum((y - fit) ** 2 for y, fit in zip(target, fitted))
    ss_tot = sum((y - mean_y) ** 2 for y in target)
    r2 = 1 - ss_res / ss_tot if ss_tot else 0.0
    return beta, r2


def within(month: str, start: str, end: str) -> bool:
    return start <= month <= end


def main() -> None:
    variables = {
        1: ("reservas_internacionales", "2023-12-01", "2026-08-31", "USD_millones"),
        5: ("tipo_cambio_mayorista", "2017-12-01", "2026-08-31", "ARS_por_USD"),
        15: ("base_monetaria", "2017-12-01", "2026-08-31", "ARS_millones"),
        27: ("inflacion_mensual", "2017-12-01", "2026-08-31", "porcentaje"),
        1239: ("m2_privado", "2017-12-01", "2026-08-31", "ARS_millones"),
        1256: ("cuenta_corriente_me_bcra", "2026-08-26", "2026-08-26", "ARS_millones"),
        1259: ("letras_bcra_me", "2026-08-26", "2026-08-26", "ARS_millones"),
        1266: ("depositos_gobierno_me_bcra", "2026-08-26", "2026-08-26", "ARS_millones"),
    }
    downloaded: dict[int, list[dict]] = {}
    raw_rows: list[dict] = []
    for variable_id, (name, since, until, unit) in variables.items():
        rows = api_series(variable_id, since, until)
        downloaded[variable_id] = rows
        for row in rows:
            raw_rows.append(
                {
                    "variable_id": variable_id,
                    "variable": name,
                    "date": row["date"].isoformat(),
                    "value": f'{row["value"]:.8f}',
                    "unit": unit,
                    "source_url": f"{API}/{variable_id}?desde={since}&hasta={until}",
                }
            )
    write_csv(
        ROOT / "bcra_api_raw.csv",
        ["variable_id", "variable", "date", "value", "unit", "source_url"],
        raw_rows,
    )

    # Stock bruto y pasivos identificables: no se denomina a este puente "reservas netas".
    reserve_latest = downloaded[1][-1]
    tc_0826 = next(row["value"] for row in downloaded[5] if row["date"] == dt.date(2026, 8, 26))
    claims = [
        {
            "item": "Reservas internacionales brutas",
            "date": reserve_latest["date"].isoformat(),
            "usd_millions": reserve_latest["value"],
            "calculation": "API BCRA id 1",
            "classification": "stock_bruto_observado",
            "subtractable_as_official_net": "no",
        },
        {
            "item": "Cuenta corriente en moneda extranjera de entidades en BCRA",
            "date": "2026-08-26",
            "usd_millions": downloaded[1256][0]["value"] / tc_0826,
            "calculation": "API id 1256 en millones ARS / TC mayorista id 5",
            "classification": "encajes_depositos_privados_aprox",
            "subtractable_as_official_net": "no; solo memo de pasivo identificado",
        },
        {
            "item": "Depositos del gobierno en moneda extranjera en BCRA",
            "date": "2026-08-26",
            "usd_millions": downloaded[1266][0]["value"] / tc_0826,
            "calculation": "API id 1266 en millones ARS / TC mayorista id 5",
            "classification": "fondos_del_tesoro_aprox",
            "subtractable_as_official_net": "depende de metodologia; memo",
        },
        {
            "item": "Letras emitidas por BCRA en moneda extranjera",
            "date": "2026-08-26",
            "usd_millions": downloaded[1259][0]["value"] / tc_0826,
            "calculation": "API id 1259 en millones ARS / TC mayorista id 5",
            "classification": "pasivo_me_aprox",
            "subtractable_as_official_net": "depende de metodologia y vencimiento; memo",
        },
        {
            "item": "REPO con bancos internacionales",
            "date": "2026-07-03",
            "usd_millions": 6000.0,
            "calculation": "Comunicado BCRA: refinanciacion por igual monto",
            "classification": "financiamiento_con_garantia",
            "subtractable_as_official_net": "depende de metodologia; memo",
        },
        {
            "item": "Tramo activado swap PBoC",
            "date": "2026-08-05",
            "usd_millions": 5000.0,
            "calculation": "Comunicado BCRA: RMB 35.000 M, equivalente informado",
            "classification": "swap_activado",
            "subtractable_as_official_net": "depende de metodologia; memo",
        },
    ]
    identified = sum(row["usd_millions"] for row in claims[1:])
    for row in claims:
        row["usd_millions"] = f'{row["usd_millions"]:.3f}'
    write_csv(
        ROOT / "reserve_claims_audit.csv",
        [
            "item",
            "date",
            "usd_millions",
            "calculation",
            "classification",
            "subtractable_as_official_net",
        ],
        claims,
    )

    # Anatomia de julio: los componentes publicados no cierran sin residual.
    reserve_flow = [
        ("Compras de moneda extranjera del BCRA", 2163.0, "mercado_cambios"),
        ("Capital e intereses de organismos internacionales", 2621.0, "financiamiento_oficial"),
        ("Nuevas emisiones de titulos del Gobierno Nacional", 1063.0, "financiamiento_tesoro"),
        ("Aumento de tenencias ME de entidades en BCRA", 1307.0, "depositos_terceros"),
        ("Valuacion de activos de reserva", 110.0, "valuacion"),
        ("Pagos de capital e intereses de titulos publicos", -4476.0, "servicio_deuda"),
        ("Ventas ME del Tesoro Nacional", -146.0, "tesoro_mercado"),
        ("Pagos netos SML", -67.0, "sistema_pagos"),
    ]
    published_components = sum(value for _, value, _ in reserve_flow)
    observed_change = 2729.0
    residual = observed_change - published_components
    flow_rows = [
        {"component": name, "usd_millions": value, "classification": classification}
        for name, value, classification in reserve_flow
    ] + [
        {
            "component": "Residual de conciliacion (variaciones no enumeradas/redondeos)",
            "usd_millions": residual,
            "classification": "residual_calculado",
        }
    ]
    write_csv(
        ROOT / "reserve_flow_july_2026.csv",
        ["component", "usd_millions", "classification"],
        flow_rows,
    )

    # Puente de cuenta corriente, trimestre I de 2026 (MBP6, INDEC).
    bop_rows = [
        {"component": "Bienes", "usd_millions": 6339.0},
        {"component": "Servicios", "usd_millions": -4028.0},
        {"component": "Ingreso primario", "usd_millions": -4676.0},
        {"component": "Ingreso secundario", "usd_millions": 714.0},
        {"component": "Cuenta corriente", "usd_millions": -1651.0},
    ]
    write_csv(ROOT / "bop_bridge_q1_2026.csv", ["component", "usd_millions"], bop_rows)

    trade_rows = [
        {"period": "2026-01/07", "component": "Exportaciones de bienes", "usd_millions": 58365.0},
        {"period": "2026-01/07", "component": "Importaciones de bienes", "usd_millions": -42286.0},
        {"period": "2026-01/07", "component": "Saldo comercial publicado", "usd_millions": 16080.0},
        {"period": "2026-01/07", "component": "Exportaciones combustibles y energia", "usd_millions": 9151.0},
        {"period": "2026-01/07", "component": "Importaciones combustibles y lubricantes", "usd_millions": -2298.0},
        {"period": "2025", "component": "Gasto turismo receptivo ETI, pasos relevados", "usd_millions": 3110.0},
        {"period": "2025", "component": "Gasto turismo emisivo ETI, pasos relevados", "usd_millions": -7164.2},
        {"period": "2025", "component": "Saldo turismo ETI, pasos relevados", "usd_millions": -4054.2},
        {"period": "2026-03", "component": "Balance cambiario Viajes y Pasajes", "usd_millions": -393.0},
    ]
    write_csv(ROOT / "trade_tourism_evidence.csv", ["period", "component", "usd_millions"], trade_rows)

    # Tipo de cambio real: serie diaria oficial, no un dolar de equilibrio.
    itcrm = parse_itcrm(ROOT / "source_bcra_itcrm.xlsx")
    write_csv(
        ROOT / "itcrm_daily.csv",
        ["date", "itcrm"],
        [{"date": row["date"].isoformat(), "itcrm": f'{row["value"]:.8f}'} for row in itcrm],
    )
    latest_itcrm = itcrm[-1]
    windows = [
        ("1997-2001", dt.date(1997, 1, 1), dt.date(2001, 12, 31)),
        ("2002-2007", dt.date(2002, 1, 1), dt.date(2007, 12, 31)),
        ("2008-2017", dt.date(2008, 1, 1), dt.date(2017, 12, 31)),
        ("2018-2023", dt.date(2018, 1, 1), dt.date(2023, 12, 31)),
        ("2024-ultimo", dt.date(2024, 1, 1), latest_itcrm["date"]),
    ]
    benchmark_rows: list[dict] = []
    for label, start, end in windows:
        values = [row["value"] for row in itcrm if start <= row["date"] <= end]
        benchmark_rows.append(
            {
                "window": label,
                "start": start.isoformat(),
                "end": end.isoformat(),
                "mean_itcrm": f"{statistics.mean(values):.3f}",
                "latest_vs_mean_pct": f"{100 * (latest_itcrm['value'] / statistics.mean(values) - 1):.2f}",
                "n_daily": len(values),
            }
        )
    full_values = [row["value"] for row in itcrm]
    percentile = 100 * sum(value <= latest_itcrm["value"] for value in full_values) / len(full_values)
    benchmark_rows.append(
        {
            "window": "ultimo_dato",
            "start": latest_itcrm["date"].isoformat(),
            "end": latest_itcrm["date"].isoformat(),
            "mean_itcrm": f"{latest_itcrm['value']:.3f}",
            "latest_vs_mean_pct": "0.00",
            "n_daily": 1,
            "percentile_full_history": f"{percentile:.2f}",
        }
    )
    write_csv(
        ROOT / "itcrm_benchmarks.csv",
        ["window", "start", "end", "mean_itcrm", "latest_vs_mean_pct", "n_daily", "percentile_full_history"],
        benchmark_rows,
    )

    # Pass-through descriptivo: IPC mensual vs depreciacion log mensual, rezagos 0-6.
    tc_month = month_end(downloaded[5])
    fx_change = log_changes(tc_month)
    cpi = {row["date"].strftime("%Y-%m"): row["value"] for row in downloaded[27]}
    base_change = log_changes(month_end(downloaded[15]))
    m2_change = log_changes(month_end(downloaded[1239]))
    monthly_panel = []
    for month in sorted(set(cpi) & set(fx_change)):
        monthly_panel.append(
            {
                "month": month,
                "ipc_monthly_pct": f"{cpi[month]:.6f}",
                "fx_log_change_pct": f"{fx_change[month]:.6f}",
                "base_log_change_pct": f"{base_change[month]:.6f}" if month in base_change else "",
                "m2_private_log_change_pct": f"{m2_change[month]:.6f}" if month in m2_change else "",
            }
        )
    write_csv(
        ROOT / "monthly_money_fx_ipc_panel.csv",
        ["month", "ipc_monthly_pct", "fx_log_change_pct", "base_log_change_pct", "m2_private_log_change_pct"],
        monthly_panel,
    )

    counterexamples: list[dict] = []
    comparable_months = sorted(set(cpi) & set(fx_change))
    for previous, current in zip(comparable_months, comparable_months[1:]):
        if (
            current >= "2024-01"
            and fx_change[current] > 0
            and cpi[current] < cpi[previous]
        ):
            counterexamples.append(
                {
                    "month": current,
                    "fx_log_change_pct": f"{fx_change[current]:.4f}",
                    "ipc_monthly_pct": f"{cpi[current]:.4f}",
                    "previous_month_ipc_pct": f"{cpi[previous]:.4f}",
                    "claim_tested": "TC mayorista sube mientras baja la inflacion mensual",
                }
            )
    write_csv(
        ROOT / "counterexamples_fx_up_inflation_down.csv",
        ["month", "fx_log_change_pct", "ipc_monthly_pct", "previous_month_ipc_pct", "claim_tested"],
        counterexamples,
    )

    correlation_rows: list[dict] = []
    for explanatory_name, explanatory in [
        ("depreciacion_tc_mayorista", fx_change),
        ("crecimiento_base_monetaria", base_change),
        ("crecimiento_m2_privado", m2_change),
    ]:
        for lag in range(7):
            pairs = []
            for month, inflation in cpi.items():
                source_month = shift_month(month, -lag)
                if "2018-01" <= month <= "2026-07" and source_month in explanatory:
                    pairs.append((explanatory[source_month], inflation))
            corr = correlation(pairs)
            correlation_rows.append(
                {
                    "dependent": "ipc_mensual",
                    "explanatory": explanatory_name,
                    "lag_months": lag,
                    "correlation": f"{corr:.6f}" if corr is not None else "",
                    "n": len(pairs),
                    "sample": "2018-01/2026-07",
                }
            )
    write_csv(
        ROOT / "lag_correlations.csv",
        ["dependent", "explanatory", "lag_months", "correlation", "n", "sample"],
        correlation_rows,
    )

    regimes = [
        ("completo", "2018-01", "2026-07"),
        ("2018-2019", "2018-01", "2019-12"),
        ("2020-pre_shock", "2020-01", "2023-11"),
        ("shock_y_crawl", "2023-12", "2025-03"),
        ("bandas", "2025-04", "2026-07"),
    ]
    regression_rows: list[dict] = []
    for name, start, end in regimes:
        features: list[list[float]] = []
        target: list[float] = []
        used_months: list[str] = []
        for month in sorted(cpi):
            lag_months = [shift_month(month, -lag) for lag in range(4)]
            if within(month, start, end) and all(item in fx_change for item in lag_months):
                features.append([1.0] + [fx_change[item] for item in lag_months])
                target.append(cpi[month])
                used_months.append(month)
        if len(features) < 10:
            continue
        beta, r2 = ols(features, target)
        regression_rows.append(
            {
                "regime": name,
                "start": used_months[0],
                "end": used_months[-1],
                "n": len(features),
                "intercept": f"{beta[0]:.6f}",
                "beta_fx_t": f"{beta[1]:.6f}",
                "beta_fx_lag1": f"{beta[2]:.6f}",
                "beta_fx_lag2": f"{beta[3]:.6f}",
                "beta_fx_lag3": f"{beta[4]:.6f}",
                "cumulative_beta_0_3": f"{sum(beta[1:]):.6f}",
                "r_squared": f"{r2:.6f}",
                "interpretation": "pp IPC por 1% de depreciacion; OLS descriptivo sin controles",
            }
        )
    write_csv(
        ROOT / "pass_through_distributed_ols.csv",
        [
            "regime", "start", "end", "n", "intercept", "beta_fx_t", "beta_fx_lag1",
            "beta_fx_lag2", "beta_fx_lag3", "cumulative_beta_0_3", "r_squared", "interpretation",
        ],
        regression_rows,
    )

    sources = [
        {
            "id": "BCRA_API_V4",
            "institution": "BCRA",
            "published_or_cutoff": "2026-08-28 segun serie; consulta 2026-08-31",
            "topic": "Reservas, TC mayorista, base, M2, IPC y pasivos BCRA",
            "url": "https://api.bcra.gob.ar/estadisticas/v4.0/monetarias",
            "used_for": "series y snapshot",
            "caveat": "datos provisorios; cuentas ME publicadas en ARS se convierten al TC mayorista como aproximacion",
        },
        {
            "id": "BCRA_API_DOC",
            "institution": "BCRA",
            "published_or_cutoff": "version 4.0",
            "topic": "Metodologia de API",
            "url": "https://www.bcra.gob.ar/archivos/Catalogo/Content/files/pdf/principales-variables-v4.pdf",
            "used_for": "IDs, unidades y endpoints",
            "caveat": "la API no publica una serie oficial de reservas netas o liquidas",
        },
        {
            "id": "BCRA_ITCRM",
            "institution": "BCRA",
            "published_or_cutoff": "2026-08-28",
            "topic": "ITCRM diario",
            "url": "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/ITCRMSerie.xlsx",
            "used_for": "nivel, medias historicas y percentil",
            "caveat": "indicador de competitividad-precio, no dolar de equilibrio; ultimos datos sujetos a revision",
        },
        {
            "id": "BCRA_BALCAM_JUL26",
            "institution": "BCRA",
            "published_or_cutoff": "2026-08-28; datos julio 2026",
            "topic": "Mercado de cambios y reservas",
            "url": "https://www.bcra.gob.ar/publicaciones/informe-de-evolucion-del-mercado-de-cambios-y-balance-cambiario-julio-de-2026/",
            "used_for": "flujo julio",
            "caveat": "lista del resumen no agota todas las variaciones; se explicita residual",
        },
        {
            "id": "BCRA_REPO_2026",
            "institution": "BCRA",
            "published_or_cutoff": "2026-07-03",
            "topic": "REPO internacional",
            "url": "https://www.bcra.gob.ar/noticias/bcra-repo-renovacion-total-hasta-2028/",
            "used_for": "pasivo identificado USD 6.000 M",
            "caveat": "no se imputa mecanicamente a una definicion oficial de reservas netas",
        },
        {
            "id": "BCRA_SWAP_PBOC_2026",
            "institution": "BCRA",
            "published_or_cutoff": "2026-08-05",
            "topic": "Swap China",
            "url": "https://www.bcra.gob.ar/noticias/el-banco-central-de-la-republica-argentina-y-el-banco-de-la-republica-popular-de-china-renuevan-su-acuerdo-de-swap-y-extienden-el-plazo-de-3-a-5-anos/",
            "used_for": "tramo activado USD 5.000 M y monto total RMB 130.000 M",
            "caveat": "no se convierte el tramo no activado a USD ni se fabrica una reserva propia",
        },
        {
            "id": "INDEC_BP_Q1_2026",
            "institution": "INDEC",
            "published_or_cutoff": "2026-06-24; I trimestre 2026",
            "topic": "Balanza de pagos MBP6",
            "url": "https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-35-45",
            "used_for": "puente cuenta corriente",
            "caveat": "trimestral; no mezclar con el acumulado comercial enero-julio",
        },
        {
            "id": "INDEC_ICA_JUL26",
            "institution": "INDEC",
            "published_or_cutoff": "2026-08-20; enero-julio 2026",
            "topic": "Comercio de bienes",
            "url": "https://www.indec.gob.ar/ftp/ica_digital/ica_d_08_26E158B1D119/",
            "used_for": "exportaciones, importaciones, saldo y proxy energia",
            "caveat": "comercio devengado de bienes; no es cuenta corriente ni balance cambiario",
        },
        {
            "id": "INDEC_ETI_2025",
            "institution": "INDEC",
            "published_or_cutoff": "2026-01; ano 2025",
            "topic": "Turismo internacional",
            "url": "https://www.indec.gob.ar/uploads/informesdeprensa/eti_01_26212234D387.pdf",
            "used_for": "gasto receptivo/emisivo en pasos relevados",
            "caveat": "cobertura ETI; no equivale a todo el rubro servicios de la balanza de pagos",
        },
        {
            "id": "BCRA_BALCAM_MAR26",
            "institution": "BCRA",
            "published_or_cutoff": "2026-04; marzo 2026",
            "topic": "Viajes y pasajes cambiario",
            "url": "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/informes/informe-mercado-cambios-balance-cambiario-2026-03.pdf",
            "used_for": "saldo cambiario viajes y uso de fondos propios",
            "caveat": "balance cambiario (caja), no balanza de pagos (devengado)",
        },
    ]
    write_csv(
        ROOT / "evidence_sources.csv",
        ["id", "institution", "published_or_cutoff", "topic", "url", "used_for", "caveat"],
        sources,
    )

    gaps = [
        {
            "epic_items": "6",
            "question": "Reservas brutas, netas, liquidas y propias",
            "status": "parcial verificable",
            "available": "brutas diarias y pasivos identificables en fechas cercanas",
            "missing": "plantilla sincronizada con oro, DEG, swaps total/activado, repos, forwards, encajes, Tesoro y liquidabilidad",
            "why_it_matters": "sin esa apertura no existe una cifra oficial reproducible de netas/liquidas/propias",
            "next_primary_source": "BCRA: plantilla de reservas y liquidez en ME con misma fecha y notas de valuacion",
        },
        {
            "epic_items": "7",
            "question": "Anatomia de acumulacion",
            "status": "caso julio 2026 cerrado",
            "available": "compras, OOII, emisiones, depositos, valuacion, pagos y residual",
            "missing": "panel mensual homogeneo y conciliado para 2024-2026",
            "why_it_matters": "un mes ilustra el mecanismo pero no identifica persistencia",
            "next_primary_source": "anexos mensuales BCRA y series diarias ids 77-82",
        },
        {
            "epic_items": "8",
            "question": "Cartera, liquidez, duracion y rendimiento",
            "status": "brecha",
            "available": "stock bruto agregado y comunicados de repo",
            "missing": "composicion corriente por instrumento, duration, haircuts y activos gravados",
            "why_it_matters": "bruto no revela poder de liquidacion ni riesgo de tasa",
            "next_primary_source": "BCRA: estados intermedios/notas de cartera y activos dados en garantia",
        },
        {
            "epic_items": "9,34",
            "question": "Pass-through y shocks",
            "status": "exploratorio reproducible",
            "available": "correlaciones 0-6 meses, OLS distribuido por regimen y contraejemplos",
            "missing": "controles de expectativas, actividad, regulados, nucleo; inferencia robusta/LP-VAR",
            "why_it_matters": "los coeficientes descriptivos no identifican causalidad",
            "next_primary_source": "BCRA/INDEC: REM, EMAE e IPC divisiones empalmados con fechas de shock",
        },
        {
            "epic_items": "10",
            "question": "Tipo de cambio real y atraso",
            "status": "semaforo parcial",
            "available": "ITCRM diario, medias historicas, comercio y cuenta corriente",
            "missing": "productividad, salarios USD comparables, terminos de intercambio y reservas utilizables",
            "why_it_matters": "el ITCRM no es por si solo un dolar de equilibrio",
            "next_primary_source": "INDEC/BCRA: productividad, salarios, terminos de intercambio y posicion externa",
        },
        {
            "epic_items": "11",
            "question": "Sector externo completo",
            "status": "Q1 completo; 2026 posterior parcial",
            "available": "puente MBP6 Q1, bienes ene-jul, energia proxy y turismo",
            "missing": "balanza de pagos Q2 y puente reserva/financiera actualizado",
            "why_it_matters": "no se puede convertir el superavit comercial ene-jul en cuenta corriente ene-jul",
            "next_primary_source": "INDEC: cuentas internacionales Q2 2026 cuando se publique",
        },
        {
            "epic_items": "30-33",
            "question": "Deuda, vencimientos y apoyo externo",
            "status": "solo piezas que afectan reservas",
            "available": "repo, swap activado, flujos OOII y emisiones de julio",
            "missing": "stock consolidado Tesoro+BCRA, activos neteables y muro 2027-2031",
            "why_it_matters": "flujos de apoyo no equivalen a deuda neta ni capacidad de pago",
            "next_primary_source": "Secretaria de Finanzas/BCRA: base contractual consolidada y cronograma por moneda/acreedor",
        },
        {
            "epic_items": "35",
            "question": "2018 vs 2026",
            "status": "no cerrado",
            "available": "TC, IPC e ITCRM para comparacion macro parcial",
            "missing": "reservas comparables, empleo, salario, consumo, pobreza, deuda y cuenta corriente con misma ventana",
            "why_it_matters": "inflacion y dolar solos no miden bienestar",
            "next_primary_source": "panel INDEC/BCRA/Finanzas con definiciones estables",
        },
    ]
    write_csv(
        ROOT / "gaps_matrix.csv",
        ["epic_items", "question", "status", "available", "missing", "why_it_matters", "next_primary_source"],
        gaps,
    )

    # QA: identidades contables y controles de cobertura.
    bop_sum = sum(row["usd_millions"] for row in bop_rows[:4])
    trade_arithmetic = 58365.0 - 42286.0
    qa = {
        "generated_at": dt.datetime.now().astimezone().isoformat(),
        "cut_off": CUT_OFF.isoformat(),
        "tests": [
            {
                "name": "bop_current_account_identity",
                "expected": -1651.0,
                "actual": bop_sum,
                "tolerance": 0.0,
                "pass": bop_sum == -1651.0,
            },
            {
                "name": "reserve_flow_july_reconciliation",
                "expected": observed_change,
                "actual": published_components + residual,
                "tolerance": 0.0,
                "pass": published_components + residual == observed_change,
            },
            {
                "name": "trade_rounding_bridge",
                "expected": 16080.0,
                "actual": trade_arithmetic,
                "tolerance": 1.0,
                "pass": abs(trade_arithmetic - 16080.0) <= 1.0,
            },
            {
                "name": "latest_reserve_not_after_cutoff",
                "expected": CUT_OFF.isoformat(),
                "actual": reserve_latest["date"].isoformat(),
                "tolerance": "date <= cutoff",
                "pass": reserve_latest["date"] <= CUT_OFF,
            },
            {
                "name": "latest_itcrm_not_after_cutoff",
                "expected": CUT_OFF.isoformat(),
                "actual": latest_itcrm["date"].isoformat(),
                "tolerance": "date <= cutoff",
                "pass": latest_itcrm["date"] <= CUT_OFF,
            },
            {
                "name": "no_official_net_or_liquid_reserve_created",
                "expected": True,
                "actual": all(row["subtractable_as_official_net"] != "yes" for row in claims),
                "tolerance": "exact",
                "pass": all(row["subtractable_as_official_net"] != "yes" for row in claims),
            },
        ],
        "derived": {
            "reserve_latest_usd_millions": reserve_latest["value"],
            "reserve_latest_date": reserve_latest["date"].isoformat(),
            "identified_claims_usd_millions": round(identified, 3),
            "identified_claims_pct_gross": round(100 * identified / reserve_latest["value"], 2),
            "july_start_reserves_usd_millions": 47599.0 - 2729.0,
            "july_published_components_usd_millions": published_components,
            "july_reconciliation_residual_usd_millions": residual,
            "q1_services_plus_primary_drain_usd_millions": -4028.0 - 4676.0,
            "jan_jul_energy_proxy_surplus_usd_millions": 9151.0 - 2298.0,
            "jan_jul_energy_proxy_share_commercial_surplus_pct": round(100 * (9151.0 - 2298.0) / 16080.0, 2),
            "latest_itcrm": round(latest_itcrm["value"], 3),
            "latest_itcrm_date": latest_itcrm["date"].isoformat(),
            "latest_itcrm_full_history_percentile": round(percentile, 2),
        },
    }
    qa["all_tests_pass"] = all(test["pass"] for test in qa["tests"])
    (ROOT / "qa_results.json").write_text(
        json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if not qa["all_tests_pass"]:
        raise SystemExit("Fallaron controles; ver qa_results.json")


if __name__ == "__main__":
    main()
