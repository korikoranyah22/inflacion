from __future__ import annotations

import csv
import html
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / "sources"
DERIVED = ROOT / "derived"
DERIVED.mkdir(exist_ok=True)


def write_csv(name: str, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path = DERIVED / name
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_rigi_schedule() -> None:
    portal_path = SOURCES / "rigi" / "rigi_portal_2026-08-31.html"
    portal = portal_path.read_text(encoding="utf-8", errors="replace")
    match = re.search(
        r'id="raw-data-json".*?<p>(.*?)</p>', portal, flags=re.IGNORECASE | re.DOTALL
    )
    if not match:
        raise RuntimeError("No se encontró raw-data-json en el portal RIGI respaldado")
    raw = re.sub(r"<br\s*/?>", "\n", match.group(1), flags=re.IGNORECASE)
    raw = re.sub(r"<[^>]+>", "", raw)
    payload = json.loads(html.unescape(raw).strip())

    schedule_rows: list[dict[str, object]] = []
    for item in payload:
        year = int(str(item["year"])[:4])
        sectors = {
            key: float(value.get("total", 0))
            for key, value in item.items()
            if key != "year" and isinstance(value, dict)
        }
        schedule_rows.append(
            {
                "anio": year,
                "energia_electrica_usd_m": sectors.get("energia", 0),
                "petroleo_gas_usd_m": sectors.get("petroleo", 0),
                "mineria_usd_m": sectors.get("mineria", 0),
                "siderurgia_usd_m": sectors.get("siderurgia", 0),
                "infraestructura_usd_m": sectors.get("infra", 0),
                "tecnologia_usd_m": sectors.get("tecnologia", 0),
                "total_programado_usd_m": sum(sectors.values()),
                "naturaleza": "plan_de_inversion_no_empleo_observado",
            }
        )
    write_csv(
        "rigi_investment_schedule.csv", list(schedule_rows[0]), schedule_rows
    )


def parse_rigi_projects() -> None:
    path = SOURCES / "rigi" / "rigi_dataset_2026-08-31.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    # El portal repite proyectos compartidos por provincia. La UI oficial deduplica por nombre.
    by_name: dict[str, dict[str, str]] = {}
    provinces: defaultdict[str, list[str]] = defaultdict(list)
    for row in rows:
        name = row["nombre"].strip()
        if not name or name == "Nombre del proyecto":
            continue
        by_name.setdefault(name, row)
        province = row["provincia"].strip()
        if province and province not in provinces[name]:
            provinces[name].append(province)

    projects: list[dict[str, object]] = []
    for name, row in sorted(by_name.items()):
        projects.append(
            {
                "proyecto": name,
                "provincias": " | ".join(provinces[name]),
                "empresa": row["empresa"].strip(),
                "sector": row["sector"].strip(),
                "inversion_comprometida_usd_m": float(row["inv-comprometida"]),
                "empleos_directos_indirectos_proyectados": int(
                    float(row["empleos-generados"])
                ),
                "desglose_temporal_permanente": row[
                    "empleos-generados-texto"
                ].strip()
                or "N/D",
                "resolucion": row["enlace"].strip(),
            }
        )
    write_csv("rigi_projects_deduplicated.csv", list(projects[0]), projects)

    investment = sum(float(row["inversion_comprometida_usd_m"]) for row in projects)
    jobs = sum(int(row["empleos_directos_indirectos_proyectados"]) for row in projects)
    summary = [
        {
            "fecha_corte": "2026-08-31",
            "proyectos_aprobados_deduplicados": len(projects),
            "inversion_comprometida_usd_m": round(investment, 3),
            "empleos_directos_indirectos_proyectados": jobs,
            "empleos_proyectados_por_usd_1000m": round(jobs / investment * 1000, 3),
            "proyectos_con_desglose_temporal_permanente": sum(
                row["desglose_temporal_permanente"] != "N/D" for row in projects
            ),
        }
    ]
    assert summary[0]["proyectos_aprobados_deduplicados"] == 22
    assert round(investment) == 47073
    assert jobs == 95950
    write_csv("rigi_summary.csv", list(summary[0]), summary)


def build_reserve_liquidity_bridge() -> None:
    gross = 47599.19
    rows = [
        {
            "horizonte": "reservas_oficiales_2026-07-31",
            "reservas_oficiales_usd_m": gross,
            "flujo_predeterminado_adicional_usd_m": 0,
            "flujo_predeterminado_acumulado_usd_m": 0,
            "residual_bruto_menos_flujos_usd_m": gross,
            "interpretacion": "activo_oficial_bruto_no_reservas_netas",
        },
        {
            "horizonte": "hasta_1_mes",
            "reservas_oficiales_usd_m": gross,
            "flujo_predeterminado_adicional_usd_m": -37127.82,
            "flujo_predeterminado_acumulado_usd_m": -37127.82,
            "residual_bruto_menos_flujos_usd_m": 10471.37,
            "interpretacion": "estres_estatico_sin_nuevos_flujos_ni_rollover",
        },
        {
            "horizonte": "hasta_3_meses",
            "reservas_oficiales_usd_m": gross,
            "flujo_predeterminado_adicional_usd_m": -243.49,
            "flujo_predeterminado_acumulado_usd_m": -37371.31,
            "residual_bruto_menos_flujos_usd_m": 10227.88,
            "interpretacion": "estres_estatico_sin_nuevos_flujos_ni_rollover",
        },
        {
            "horizonte": "hasta_1_anio",
            "reservas_oficiales_usd_m": gross,
            "flujo_predeterminado_adicional_usd_m": -4408.13,
            "flujo_predeterminado_acumulado_usd_m": -41779.44,
            "residual_bruto_menos_flujos_usd_m": 5819.75,
            "interpretacion": "estres_estatico_sin_nuevos_flujos_ni_rollover",
        },
    ]
    write_csv("bcra_reserve_liquidity_bridge.csv", list(rows[0]), rows)

    composition = [
        {"componente": "reservas_moneda_extranjera", "usd_m": 38433.62},
        {"componente": "posicion_reserva_fmi", "usd_m": 0.00},
        {"componente": "deg", "usd_m": 908.14},
        {"componente": "oro", "usd_m": 8046.37},
        {"componente": "otros_activos_reserva", "usd_m": 211.06},
        {"componente": "total_activos_reserva_oficial", "usd_m": gross},
    ]
    assert abs(sum(row["usd_m"] for row in composition[:-1]) - gross) < 0.01
    write_csv("bcra_reserve_composition.csv", list(composition[0]), composition)


def build_debt_maturity_profile() -> None:
    # Transcripción auditada con artifact-tool de la hoja A.3.6 del XLSX oficial.
    # La unidad original es miles de USD; aquí se expresa en millones de USD.
    raw = [
        (2026, 141738.7220203, 134446.4184551, 7292.3035651),
        (2027, 82711.6401145, 72570.2537571, 10141.3863574),
        (2028, 49790.1898298, 40028.6129100, 9761.5769197),
        (2029, 35216.3039061, 26234.0183499, 8982.2855562),
        (2030, 30428.5842823, 22527.0766891, 7901.5075932),
        (2031, 45040.9695760, 38448.4781716, 6592.4914044),
    ]
    rows = []
    for year, services, capital, interest in raw:
        assert abs(services - capital - interest) < 0.001
        rows.append(
            {
                "anio": year,
                "servicios_usd_m": round(services, 3),
                "capital_usd_m": round(capital, 3),
                "intereses_usd_m": round(interest, 3),
                "perimetro": "Administracion Central; perfil estatico; no consolidado",
                "fecha_corte": "2026-03-31",
                "fuente_hoja": "deuda_publica_2026-03-31.xlsx!A.3.6",
            }
        )
    write_csv("debt_service_2026_2031.csv", list(rows[0]), rows)

    wall = [row for row in rows if 2027 <= int(row["anio"]) <= 2031]
    summary = [
        {
            "periodo": "2027-2031",
            "servicios_usd_m": round(sum(float(row["servicios_usd_m"]) for row in wall), 3),
            "capital_usd_m": round(sum(float(row["capital_usd_m"]) for row in wall), 3),
            "intereses_usd_m": round(sum(float(row["intereses_usd_m"]) for row in wall), 3),
            "anio_pico": max(wall, key=lambda row: float(row["servicios_usd_m"]))["anio"],
            "servicios_anio_pico_usd_m": max(
                float(row["servicios_usd_m"]) for row in wall
            ),
            "perimetro": "Administracion Central; perfil estatico; no consolidado",
        }
    ]
    write_csv("debt_wall_summary.csv", list(summary[0]), summary)


def build_public_capital_accounting_inventory() -> None:
    rows = [
        {
            "concepto": "total_bienes_de_uso",
            "saldo_inicial_ars_m": 694519,
            "movimientos_ars_m": 225927,
            "saldo_cierre_bruto_ars_m": 920447,
            "amortizacion_acumulada_ars_m": 238784,
            "valor_residual_ars_m": 681662,
            "perimetro": "Administracion Central",
            "fecha_corte": "2024-12-31",
        },
        {
            "concepto": "construcciones_en_proceso_dominio_privado",
            "saldo_inicial_ars_m": 70079,
            "movimientos_ars_m": 19817,
            "saldo_cierre_bruto_ars_m": 89896,
            "amortizacion_acumulada_ars_m": 0,
            "valor_residual_ars_m": 89896,
            "perimetro": "Administracion Central",
            "fecha_corte": "2024-12-31",
        },
        {
            "concepto": "construcciones_en_proceso_dominio_publico",
            "saldo_inicial_ars_m": 189072,
            "movimientos_ars_m": -11150,
            "saldo_cierre_bruto_ars_m": 177922,
            "amortizacion_acumulada_ars_m": 0,
            "valor_residual_ars_m": 177922,
            "perimetro": "Administracion Central",
            "fecha_corte": "2024-12-31",
        },
        {
            "concepto": "bienes_de_dominio_publico",
            "saldo_inicial_ars_m": 1085,
            "movimientos_ars_m": 0,
            "saldo_cierre_bruto_ars_m": 1085,
            "amortizacion_acumulada_ars_m": 0,
            "valor_residual_ars_m": 1085,
            "perimetro": "Administracion Central",
            "fecha_corte": "2024-12-31",
        },
    ]
    write_csv("public_capital_accounting_inventory.csv", list(rows[0]), rows)


if __name__ == "__main__":
    parse_rigi_schedule()
    parse_rigi_projects()
    build_reserve_liquidity_bridge()
    build_debt_maturity_profile()
    build_public_capital_accounting_inventory()
    print("OK: RIGI, BCRA, deuda y capital público generados")
