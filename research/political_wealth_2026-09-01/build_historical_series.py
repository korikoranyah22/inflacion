from __future__ import annotations

import csv
import io
import json
import math
import re
import zipfile
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ZIP_PATH = ROOT / "sources" / "datos_justicia" / "declaraciones-juradas-2012-2024.zip"
IPC_PATH = ROOT / "sources" / "indec" / "serie_ipc_divisiones_2016_2026.csv"
FX_PATH = ROOT / "sources" / "bcra" / "a3500_2017_2025_2026-09-01.json"
TBILL_PATH = ROOT / "sources" / "benchmarks" / "fred_gs3m_2017_2025_2026-09-01.csv"
DERIVED = ROOT / "derived"

DATASET_URL = "https://datos.jus.gob.ar/dataset/declaraciones-juradas-patrimoniales-integrales"

PEOPLE = {
    "maximo": ("KIRCHNER MAXIMO CARLOS", "Máximo Kirchner"),
    "cristina": ("FERNANDEZ CRISTINA ELISABET", "Cristina Fernández de Kirchner"),
    "massa": ("MASSA SERGIO TOMAS", "Sergio Massa"),
    "macri": ("MACRI MAURICIO", "Mauricio Macri"),
    "caputo": ("CAPUTO LUIS ANDRES", "Luis Caputo"),
    "javier": ("MILEI JAVIER GERARDO", "Javier Milei"),
    "martin": ("MENEM MARTIN ALEXIS", "Martín Menem"),
    "karina": ("MILEI KARINA ELIZABETH", "Karina Milei"),
}

PROVISIONAL_2025 = {
    "maximo": {
        "total_bienes_ars": Decimal("11085027375.28"),
        "url": "https://www.cronista.com/economia-politica/maximo-kirchner-presento-su-declaracion-jurada-cuanto-crecio-el-patrimonio-del-hijo-de-la-expresidenta/",
        "note": "Valor publicado atribuido a la DJPI 2025; PDF OA individual pendiente.",
    },
    "karina": {
        "total_bienes_ars": Decimal("35312784.57"),
        "url": "https://www.lanacion.com.ar/politica/declaracion-jurada-de-karina-milei-uno-por-uno-todos-los-bienes-informados-de-la-secretaria-general-nid01092026/",
        "note": "Valor publicado atribuido a la DJPI 2025; PDF OA individual pendiente.",
    },
    "javier": {
        "total_bienes_ars": Decimal("295182652.87"),
        "deudas_ars": Decimal("586357.00"),
        "url": "https://www.cronista.com/economia-politica/cuanto-crecieron-los-patrimonios-de-javier-y-karina-milei-en-el-ultimo-ano-bienes-dolares-y-deudas/",
        "note": "Valor publicado atribuido a la DJPI 2025 y controlado contra una segunda transcripción; PDF OA individual pendiente.",
    },
}

TYPE_PRIORITY = {"Anual": 3, "Baja": 2, "Inicial": 1}

# Retornos totales anuales transcritos de las tablas oficiales respaldadas.
# Vanguard: prospecto VBIAX, página PDF 8 / página impresa 5.
# MSCI: factsheet ACWI USD Net Returns, página 1.
VBIAX_TOTAL_RETURN_PCT = {
    2017: Decimal("13.89"), 2018: Decimal("-2.86"), 2019: Decimal("21.79"),
    2020: Decimal("16.40"), 2021: Decimal("14.22"), 2022: Decimal("-16.90"),
    2023: Decimal("17.58"), 2024: Decimal("14.59"), 2025: Decimal("13.58"),
}
MSCI_ACWI_NET_RETURN_USD_PCT = {
    2017: Decimal("23.97"), 2018: Decimal("-9.41"), 2019: Decimal("26.60"),
    2020: Decimal("16.25"), 2021: Decimal("18.54"), 2022: Decimal("-18.36"),
    2023: Decimal("22.20"), 2024: Decimal("17.49"), 2025: Decimal("22.34"),
}


def decimal_or_none(value: str | None) -> Decimal | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    if cleaned.startswith(".") and cleaned.count(".") > 1:
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def to_text(value: Decimal | None, digits: int = 2) -> str:
    if value is None:
        return ""
    quantizer = Decimal(1).scaleb(-digits)
    return format(value.quantize(quantizer), "f")


def percent_change(final: Decimal, initial: Decimal) -> Decimal | None:
    if initial == 0:
        return None
    return (final / initial - 1) * 100


def cagr(final: Decimal, initial: Decimal, years: int) -> Decimal | None:
    if initial <= 0 or final < 0 or years <= 0:
        return None
    return Decimal(str((float(final / initial) ** (1 / years) - 1) * 100))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    assert rows, f"No hay filas para {path.name}"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


ipc_index: dict[int, Decimal] = {}
with IPC_PATH.open(encoding="cp1252", newline="") as handle:
    for row in csv.DictReader(handle, delimiter=";"):
        if row["Codigo"] != "0" or row["Region"] != "Nacional":
            continue
        period = row["Periodo"]
        if not period.endswith("12"):
            continue
        year = int(period[:4])
        if 2017 <= year <= 2025:
            ipc_index[year] = Decimal(row["Indice_IPC"].replace(",", "."))

fx_payload = json.loads(FX_PATH.read_text(encoding="utf-8"))
fx_detail = fx_payload["results"][0]["detalle"]
fx_candidates: dict[int, list[tuple[str, Decimal]]] = defaultdict(list)
for item in fx_detail:
    year = int(item["fecha"][:4])
    if 2017 <= year <= 2025:
        fx_candidates[year].append((item["fecha"], Decimal(str(item["valor"]))))
fx_year_end = {year: max(values, key=lambda item: item[0]) for year, values in fx_candidates.items()}

assert set(ipc_index) == set(range(2017, 2026)), "Faltan índices IPC diciembre"
assert set(fx_year_end) == set(range(2017, 2026)), "Faltan cierres A 3500"

raw_rows: list[dict[str, str]] = []
with zipfile.ZipFile(ZIP_PATH) as archive:
    for year in range(2017, 2025):
        member = f"declaraciones-juradas-{year}-consolidado-al-20251222.csv"
        with archive.open(member) as binary:
            with io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as text:
                for row in csv.DictReader(text):
                    if row["funcionario_apellido_nombre"] in {item[0] for item in PEOPLE.values()}:
                        raw_rows.append(row)

person_key_by_name = {official: key for key, (official, _) in PEOPLE.items()}
grouped: dict[tuple[str, int], list[dict[str, str]]] = defaultdict(list)
for row in raw_rows:
    key = person_key_by_name[row["funcionario_apellido_nombre"]]
    grouped[(key, int(row["anio"]))].append(row)


def selection_key(row: dict[str, str]) -> tuple[int, int, int]:
    return (
        TYPE_PRIORITY.get(row["tipo_declaracion_jurada_descripcion"], 0),
        int(row["rectificativa"] or 0),
        int(row["dj_id"] or 0),
    )


selected: dict[tuple[str, int], dict[str, str]] = {
    key: max(rows, key=selection_key) for key, rows in grouped.items()
}

macro_rows = []
for year in range(2017, 2026):
    fx_date, fx_value = fx_year_end[year]
    macro_rows.append(
        {
            "anio": year,
            "ipc_indice_dic_2016_100": to_text(ipc_index[year], 4),
            "ipc_variacion_interanual_pct": to_text(percent_change(ipc_index[year], Decimal("100") if year == 2017 else ipc_index[year - 1]), 2),
            "a3500_fecha_cierre": fx_date,
            "a3500_ars_por_usd": to_text(fx_value, 4),
            "fuente_ipc": "INDEC serie IPC nacional nivel general",
            "fuente_fx": "BCRA API variable 5 A 3500",
        }
    )
write_csv(DERIVED / "macro_deflators_2017_2025.csv", macro_rows)

tbill_monthly: dict[int, list[Decimal]] = defaultdict(list)
with TBILL_PATH.open(encoding="utf-8-sig", newline="") as handle:
    for row in csv.DictReader(handle):
        year = int(row["observation_date"][:4])
        if 2017 <= year <= 2025 and row["GS3M"] not in ("", "."):
            tbill_monthly[year].append(Decimal(row["GS3M"]))
assert all(len(tbill_monthly[year]) == 12 for year in range(2017, 2026)), "Faltan meses GS3M"

tbill_proxy_return_pct: dict[int, Decimal] = {}
for year, rates in tbill_monthly.items():
    factor = Decimal("1")
    for annualized_rate in rates:
        factor *= Decimal("1") + annualized_rate / Decimal("1200")
    tbill_proxy_return_pct[year] = (factor - Decimal("1")) * 100

benchmark_annual_rows = []
for year in range(2017, 2026):
    benchmark_annual_rows.extend(
        [
            {
                "benchmark_id": "tbill_3m_proxy",
                "benchmark": "T-bill EE.UU. 3 meses · rollover proxy",
                "riesgo": "poco",
                "anio": year,
                "retorno_total_usd_pct": to_text(tbill_proxy_return_pct[year], 4),
                "metodo": "Producto mensual de 1 + GS3M/1200; proxy mecánico, no retorno exacto de un fondo.",
                "fuente_url": "https://fred.stlouisfed.org/series/GS3M",
            },
            {
                "benchmark_id": "vbiax_60_40",
                "benchmark": "Vanguard Balanced Index · 60/40",
                "riesgo": "medio",
                "anio": year,
                "retorno_total_usd_pct": to_text(VBIAX_TOTAL_RETURN_PCT[year], 2),
                "metodo": "Retorno total antes de impuestos; distribuciones reinvertidas; neto de gastos del fondo.",
                "fuente_url": "https://personal1.vanguard.com/pub/Pdf/p502.pdf",
            },
            {
                "benchmark_id": "msci_acwi_net",
                "benchmark": "MSCI ACWI · net return USD",
                "riesgo": "mucho",
                "anio": year,
                "retorno_total_usd_pct": to_text(MSCI_ACWI_NET_RETURN_USD_PCT[year], 2),
                "metodo": "Índice de acciones globales; retorno neto en USD publicado por MSCI.",
                "fuente_url": "https://www.msci.com/documents/10199/a71b65b5-d0ea-4b5c-a709-24b1213bc3c5",
            },
        ]
    )
write_csv(DERIVED / "benchmark_annual_returns_2017_2025.csv", benchmark_annual_rows)

annual_return_by_benchmark: dict[str, dict[int, Decimal]] = defaultdict(dict)
for row in benchmark_annual_rows:
    annual_return_by_benchmark[str(row["benchmark_id"])][int(row["anio"])] = Decimal(
        str(row["retorno_total_usd_pct"])
    )

series_rows: list[dict[str, object]] = []
numeric_by_person: dict[str, list[dict[str, object]]] = defaultdict(list)

for key, (_, display) in PEOPLE.items():
    for year in range(2017, 2026):
        record = selected.get((key, year))
        gross: Decimal | None = None
        debt: Decimal | None = None
        source_state = "no_localizada"
        declaration_type = ""
        rectification = ""
        dj_id = ""
        source_url = DATASET_URL
        note = "No se localizó una DJPI consolidada para esta persona y año."
        if record:
            declaration_type = record["tipo_declaracion_jurada_descripcion"]
            rectification = record["rectificativa"]
            dj_id = record["dj_id"]
            if declaration_type == "Inicial":
                gross = decimal_or_none(record["total_bienes_inicio"])
                debt = decimal_or_none(record["deudas_inicio"])
            else:
                gross = decimal_or_none(record["total_bienes_final"])
                debt = decimal_or_none(record["total_deudas_final"])
            source_state = "oficial_consolidado_oa"
            note = "Selección: Anual > Baja > Inicial; luego mayor rectificativa y dj_id."
        elif year == 2025 and key in PROVISIONAL_2025:
            provisional = PROVISIONAL_2025[key]
            gross = provisional["total_bienes_ars"]
            debt = provisional.get("deudas_ars")
            source_state = "publicado_pdf_oa_pendiente"
            source_url = provisional["url"]
            note = provisional["note"]

        fx_value = fx_year_end[year][1]
        real_2025 = gross * ipc_index[2025] / ipc_index[year] if gross is not None else None
        usd_equivalent = gross / fx_value if gross is not None else None
        net = gross - debt if gross is not None and debt is not None else None
        row = {
            "persona_id": key,
            "persona": display,
            "anio": year,
            "estado_fuente": source_state,
            "tipo_ddjj": declaration_type,
            "rectificativa": rectification,
            "dj_id": dj_id,
            "total_bienes_ars": to_text(gross),
            "deudas_ars": to_text(debt),
            "patrimonio_neto_ars": to_text(net),
            "total_bienes_real_ars_2025": to_text(real_2025),
            "total_bienes_usd_a3500": to_text(usd_equivalent),
            "ipc_indice": to_text(ipc_index[year], 4),
            "a3500_ars_por_usd": to_text(fx_value, 4),
            "indice_nominal_base": "",
            "indice_real_base": "",
            "indice_usd_base": "",
            "fuente_url": source_url,
            "nota": note,
        }
        series_rows.append(row)
        if gross is not None:
            numeric_by_person[key].append(
                {"row": row, "gross": gross, "real": real_2025, "usd": usd_equivalent}
            )

for key, values in numeric_by_person.items():
    base = min(values, key=lambda item: int(item["row"]["anio"]))
    for item in values:
        item["row"]["indice_nominal_base"] = to_text(item["gross"] / base["gross"] * 100)
        item["row"]["indice_real_base"] = to_text(item["real"] / base["real"] * 100)
        item["row"]["indice_usd_base"] = to_text(item["usd"] / base["usd"] * 100)

write_csv(DERIVED / "person_series_2017_2025.csv", series_rows)

reconciliation_rows: list[dict[str, object]] = []
for (key, year), record in sorted(selected.items()):
    if record["tipo_declaracion_jurada_descripcion"] == "Inicial":
        continue
    fields = {
        "valuacion": decimal_or_none(record["diferencia_valuacion"]),
        "ingreso_neto": decimal_or_none(record["ingresos_neto_gastos"]),
        "ingreso_no_alcanzado": decimal_or_none(record["ingresos_no_alcanzados"]),
        "herencia": decimal_or_none(record["bienes_por_herencia"]),
        "deducciones_sin_erogacion": decimal_or_none(record["importes_deducidos"]),
        "gastos_no_deducibles": decimal_or_none(record["gastos_no_deducibles"]),
        "gastos_personales": decimal_or_none(record["gastos_personales"]),
    }
    start_assets = decimal_or_none(record["total_bienes_inicio"])
    start_debt = decimal_or_none(record["deudas_inicio"])
    end_assets = decimal_or_none(record["total_bienes_final"])
    end_debt = decimal_or_none(record["total_deudas_final"])
    complete = all(value is not None for value in [start_assets, start_debt, end_assets, end_debt, *fields.values()])
    delta_net = (end_assets - end_debt) - (start_assets - start_debt) if complete else None
    known = (
        fields["valuacion"]
        + fields["ingreso_neto"]
        + fields["ingreso_no_alcanzado"]
        + fields["herencia"]
        + fields["deducciones_sin_erogacion"]
        - fields["gastos_no_deducibles"]
        - fields["gastos_personales"]
        if complete
        else None
    )
    residual = delta_net - known if complete else None
    reconciliation_rows.append(
        {
            "persona_id": key,
            "persona": PEOPLE[key][1],
            "anio": year,
            "tipo_ddjj": record["tipo_declaracion_jurada_descripcion"],
            "dj_id": record["dj_id"],
            "delta_patrimonio_neto_ars": to_text(delta_net),
            "diferencia_valuacion_ars": to_text(fields["valuacion"]),
            "ingresos_netos_ars": to_text(fields["ingreso_neto"]),
            "ingresos_no_alcanzados_ars": to_text(fields["ingreso_no_alcanzado"]),
            "herencias_donaciones_ars": to_text(fields["herencia"]),
            "deducciones_sin_erogacion_ars": to_text(fields["deducciones_sin_erogacion"]),
            "gastos_no_deducibles_ars": to_text(fields["gastos_no_deducibles"]),
            "gastos_personales_ars": to_text(fields["gastos_personales"]),
            "suma_componentes_ars": to_text(known),
            "residual_ars": to_text(residual),
            "estado_calculo": "calculable" if complete else "dato_origen_malformado",
            "fuente_url": DATASET_URL,
        }
    )
write_csv(DERIVED / "annual_reconciliation_2017_2024.csv", reconciliation_rows)


def asset_category(asset_type: str, description: str) -> str:
    text = f"{asset_type} {description}".upper()
    if "DOLAR" in text or "EURO" in text or "MONEDA EXTRANJERA" in text:
        return "Moneda extranjera"
    if "INMUEBLE" in text:
        return "Inmuebles"
    if any(token in text for token in ("ACCIONES", "PARTICIPACIONES", "TITULOS", "FONDO", "OBLIGACIONES")):
        return "Sociedades y títulos"
    if any(token in text for token in ("AUTOMOTOR", "AERONAVE", "EMBARCACION")):
        return "Vehículos"
    if "CREDITO" in text:
        return "Créditos"
    if "DEPOSITO" in text or "EFECTIVO" in text or "DINERO" in text:
        return "Liquidez ARS"
    return "Otros"


composition: dict[tuple[str, int, str], Decimal] = defaultdict(Decimal)
selected_ids = {record["dj_id"]: (key, year) for (key, year), record in selected.items()}
with zipfile.ZipFile(ZIP_PATH) as archive:
    for year in range(2022, 2025):
        member = f"declaraciones-juradas-bienes-{year}-consolidado-al-20251222.csv"
        with archive.open(member) as binary:
            with io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as text:
                reader = csv.DictReader(text, skipinitialspace=True)
                for raw_row in reader:
                    row = {name.strip(): value for name, value in raw_row.items()}
                    # El diccionario oficial codifica el cierre del periodo con "C".
                    if row["dj_id"] not in selected_ids or row["periodo_inicio_cierre"] != "C":
                        continue
                    amount = decimal_or_none(row["bien_importe"])
                    if amount is None:
                        continue
                    key, selected_year = selected_ids[row["dj_id"]]
                    assert selected_year == year
                    category = asset_category(row["bien_tipo"], row["bien_descripcion"])
                    composition[(key, year, category)] += amount

composition_rows = []
for (key, year, category), amount in sorted(composition.items()):
    composition_rows.append(
        {
            "persona_id": key,
            "persona": PEOPLE[key][1],
            "anio": year,
            "categoria": category,
            "importe_ars": to_text(amount),
            "dj_id": selected[(key, year)]["dj_id"],
            "metodo": "Suma de bienes de cierre; categorías analíticas reproducibles.",
            "fuente_url": DATASET_URL,
        }
    )
write_csv(DERIVED / "asset_composition_2022_2024.csv", composition_rows)

coverage_rows = []
for key, (_, display) in PEOPLE.items():
    official_years = sorted(year for person, year in selected if person == key)
    first_numeric = min(int(item["row"]["anio"]) for item in numeric_by_person[key])
    last_numeric = max(int(item["row"]["anio"]) for item in numeric_by_person[key])
    missing = [year for year in range(2017, 2025) if year not in official_years]
    first_item = min(numeric_by_person[key], key=lambda item: int(item["row"]["anio"]))
    last_item = max(numeric_by_person[key], key=lambda item: int(item["row"]["anio"]))
    elapsed_years = int(last_item["row"]["anio"]) - int(first_item["row"]["anio"])
    coverage_rows.append(
        {
            "persona_id": key,
            "persona": display,
            "primer_anio_con_dato": first_numeric,
            "ultimo_anio_con_dato": last_numeric,
            "anios_oficiales_2017_2024": len(official_years),
            "cobertura_oficial_pct": to_text(Decimal(len(official_years)) / Decimal(8) * 100, 1),
            "anios_faltantes_2017_2024": "|".join(map(str, missing)) or "ninguno",
            "dato_2025": "provisional_publicado" if key in PROVISIONAL_2025 else "no_disponible",
            "cambio_nominal_primero_ultimo_pct": to_text(percent_change(last_item["gross"], first_item["gross"])),
            "cambio_real_primero_ultimo_pct": to_text(percent_change(last_item["real"], first_item["real"])),
            "cambio_usd_primero_ultimo_pct": to_text(percent_change(last_item["usd"], first_item["usd"])),
            "cagr_real_anual_pct": to_text(cagr(last_item["real"], first_item["real"], elapsed_years)),
            "cagr_usd_anual_pct": to_text(cagr(last_item["usd"], first_item["usd"], elapsed_years)),
            "nota": "La ausencia de dato no se interpola ni se interpreta como patrimonio cero.",
        }
    )
write_csv(DERIVED / "cohort_coverage_2017_2025.csv", coverage_rows)

benchmark_lookup = {
    "tbill_3m_proxy": ("T-bill EE.UU. 3 meses · rollover proxy", "poco"),
    "vbiax_60_40": ("Vanguard Balanced Index · 60/40", "medio"),
    "msci_acwi_net": ("MSCI ACWI · net return USD", "mucho"),
}
benchmark_comparison_rows = []
for key, values in numeric_by_person.items():
    first_item = min(values, key=lambda item: int(item["row"]["anio"]))
    last_item = max(values, key=lambda item: int(item["row"]["anio"]))
    first_year = int(first_item["row"]["anio"])
    last_year = int(last_item["row"]["anio"])
    elapsed_years = last_year - first_year
    observed_usd_cagr = cagr(last_item["usd"], first_item["usd"], elapsed_years)
    observed_real_cagr = cagr(last_item["real"], first_item["real"], elapsed_years)
    for benchmark_id, (label, risk) in benchmark_lookup.items():
        factor = Decimal("1")
        for year in range(first_year + 1, last_year + 1):
            factor *= Decimal("1") + annual_return_by_benchmark[benchmark_id][year] / Decimal("100")
        benchmark_cagr = Decimal(str((float(factor) ** (1 / elapsed_years) - 1) * 100))
        hypothetical_end_ars = first_item["gross"] / fx_year_end[first_year][1] * factor * fx_year_end[last_year][1]
        benchmark_comparison_rows.append(
            {
                "persona_id": key,
                "persona": PEOPLE[key][1],
                "anio_inicio": first_year,
                "anio_fin": last_year,
                "anios_transcurridos": elapsed_years,
                "benchmark_id": benchmark_id,
                "benchmark": label,
                "riesgo": risk,
                "patrimonio_cagr_real_pct": to_text(observed_real_cagr),
                "patrimonio_cagr_usd_a3500_pct": to_text(observed_usd_cagr),
                "benchmark_retorno_acumulado_usd_pct": to_text((factor - Decimal("1")) * 100),
                "benchmark_cagr_usd_pct": to_text(benchmark_cagr),
                "brecha_cagr_vs_patrimonio_usd_pp": to_text(observed_usd_cagr - benchmark_cagr),
                "patrimonio_final_observado_ars": to_text(last_item["gross"]),
                "capital_final_contrafactual_ars_a3500": to_text(hypothetical_end_ars),
                "estado_ultimo_dato": last_item["row"]["estado_fuente"],
                "supuesto": "Sin aportes ni retiros; retorno total reinvertido; antes de impuestos; sin apalancamiento.",
            }
        )
write_csv(DERIVED / "person_investment_benchmarks_2017_2025.csv", benchmark_comparison_rows)

dashboard_payload = {
    "metadata": {
        "corte": "2026-09-01",
        "serie": "2017-2025",
        "oficial_hasta": 2024,
        "nota_2025": "Máximo Kirchner, Javier Milei y Karina Milei tienen un valor provisional publicado; el PDF OA individual sigue pendiente.",
        "criterio_seleccion": "Anual > Baja > Inicial; luego mayor rectificativa y dj_id.",
        "advertencia": "Los años sin DJPI localizada quedan N/D: no se interpolan ni equivalen a patrimonio cero.",
    },
    "people": [
        {"persona_id": key, "persona": display}
        for key, (_, display) in PEOPLE.items()
    ],
    "series": series_rows,
    "coverage": coverage_rows,
    "macro": macro_rows,
    "benchmark_annual_returns": benchmark_annual_rows,
    "benchmark_comparisons": benchmark_comparison_rows,
    "composition": composition_rows,
    "reconciliation": reconciliation_rows,
}
(DERIVED / "dashboard_data_2017_2025.json").write_text(
    json.dumps(dashboard_payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

print(
    "OK: serie 2017-2025 construida · "
    f"{len(series_rows)} filas · {len(reconciliation_rows)} conciliaciones · "
    f"{len(composition_rows)} filas de composición"
)
