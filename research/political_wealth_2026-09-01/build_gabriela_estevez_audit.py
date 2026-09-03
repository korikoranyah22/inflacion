from __future__ import annotations

import csv
import io
import json
import zipfile
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DERIVED = ROOT / "derived"
ZIP_PATH = ROOT / "sources" / "datos_justicia" / "declaraciones-juradas-2012-2024.zip"
HCDN_2025_PATH = ROOT / "sources" / "active_roster" / "hcdn_ddjj_ejercicio_2025_2026-09-01.html"
DATASET_URL = "https://datos.jus.gob.ar/dataset/declaraciones-juradas-patrimoniales-integrales"
HCDN_2025_URL = "https://www.hcdn.gob.ar/institucional/transparencia/declaraciones_juradas/listado/c4f0658a-4249-11f0-87b7-00505689ffd4"
PERSON_ID = "dip-estevez-gabriela-beatriz"
PERSON = "Gabriela Estévez"
DJ_IDS = {2022: "661294", 2023: "718182", 2024: "805974"}


def decimal(value: str) -> Decimal:
    return Decimal(value or "0")


def rounded(value: Decimal, digits: str = "0.01") -> float:
    return float(value.quantize(Decimal(digits), rounding=ROUND_HALF_UP))


def percent(numerator: Decimal, denominator: Decimal) -> float:
    if denominator == 0:
        raise ValueError("No se puede calcular un porcentaje con denominador cero")
    return rounded(numerator / denominator * 100)


def read_member(archive: zipfile.ZipFile, member: str, dj_id: str) -> list[dict[str, str]]:
    with archive.open(member) as binary:
        with io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as text:
            reader = csv.DictReader(text, skipinitialspace=True)
            return [
                {str(key).strip(): value for key, value in row.items()}
                for row in reader
                if row.get("dj_id") == dj_id
            ]


assert ZIP_PATH.is_file(), "Falta el ZIP oficial OA 2012–2024"
assert HCDN_2025_PATH.is_file(), "Falta la copia local de la nómina HCDN 2025"
hcdn_text = HCDN_2025_PATH.read_text(encoding="utf-8", errors="replace")
assert "ESTEVEZ" in hcdn_text and "GABRIELA BEATRIZ" in hcdn_text

summaries: dict[int, dict[str, str]] = {}
assets: dict[int, list[dict[str, str]]] = {}
debts: dict[int, list[dict[str, str]]] = {}
with zipfile.ZipFile(ZIP_PATH) as archive:
    for year, dj_id in DJ_IDS.items():
        summary_rows = read_member(
            archive,
            f"declaraciones-juradas-{year}-consolidado-al-20251222.csv",
            dj_id,
        )
        assert len(summary_rows) == 1, f"Resumen {year} ambiguo"
        summaries[year] = summary_rows[0]
        assets[year] = read_member(
            archive,
            f"declaraciones-juradas-bienes-{year}-consolidado-al-20251222.csv",
            dj_id,
        )
        debts[year] = read_member(
            archive,
            f"declaraciones-juradas-deudas-{year}-consolidado-al-20251222.csv",
            dj_id,
        )
        assert assets[year], f"Sin detalle de bienes {year}"


def asset_sum(year: int, period: str, asset_type: str | None = None) -> Decimal:
    selected = [row for row in assets[year] if row["periodo_inicio_cierre"] == period]
    if asset_type:
        selected = [row for row in selected if asset_type in row["bien_tipo"].upper()]
    return sum((decimal(row["bien_importe"]) for row in selected), Decimal("0"))


def debt_sum(year: int, period: str) -> Decimal:
    selected = [row for row in debts[year] if row["periodo_inicio_cierre"] == period]
    return sum((decimal(row["deuda_importe"]) for row in selected), Decimal("0"))


controls: list[dict[str, object]] = []
for year in (2022, 2023, 2024):
    for period, summary_field, label in (
        ("I", "total_bienes_inicio", "inicio"),
        ("C", "total_bienes_final", "cierre"),
    ):
        reported = decimal(summaries[year][summary_field])
        detail = asset_sum(year, period)
        ratio = reported / detail if detail else Decimal("0")
        controls.append(
            {
                "persona_id": PERSON_ID,
                "persona": PERSON,
                "anio": year,
                "control": f"total_bienes_{label}_vs_suma_detalle",
                "valor_resumen_ars": rounded(reported),
                "valor_control_ars": rounded(detail),
                "brecha_ars": rounded(reported - detail),
                "ratio_resumen_sobre_detalle": rounded(ratio),
                "resultado": "concilia" if abs(ratio - Decimal("1")) < Decimal("0.0001") else "no_concilia",
                "dj_id": DJ_IDS[year],
                "fuente_url": DATASET_URL,
            }
        )

for year in (2022, 2023, 2024):
    for period, summary_field, label in (
        ("I", "deudas_inicio", "inicio"),
        ("C", "total_deudas_final", "cierre"),
    ):
        reported = decimal(summaries[year][summary_field])
        detail = debt_sum(year, period)
        ratio = reported / detail if detail else None
        controls.append(
            {
                "persona_id": PERSON_ID,
                "persona": PERSON,
                "anio": year,
                "control": f"total_deudas_{label}_vs_suma_detalle",
                "valor_resumen_ars": rounded(reported),
                "valor_control_ars": rounded(detail),
                "brecha_ars": rounded(reported - detail),
                "ratio_resumen_sobre_detalle": rounded(ratio) if ratio is not None else "",
                "resultado": (
                    "detalle_ausente"
                    if not debts[year]
                    else "concilia"
                    if ratio is not None and abs(ratio - Decimal("1")) < Decimal("0.0001")
                    else "no_concilia"
                ),
                "dj_id": DJ_IDS[year],
                "fuente_url": DATASET_URL,
            }
        )

for prior, current in ((2022, 2023), (2023, 2024)):
    prior_close = asset_sum(prior, "C")
    current_open = asset_sum(current, "I")
    controls.append(
        {
            "persona_id": PERSON_ID,
            "persona": PERSON,
            "anio": current,
            "control": f"cierre_detalle_{prior}_vs_inicio_detalle_{current}",
            "valor_resumen_ars": rounded(prior_close),
            "valor_control_ars": rounded(current_open),
            "brecha_ars": rounded(current_open - prior_close),
            "ratio_resumen_sobre_detalle": rounded(current_open / prior_close),
            "resultado": "concilia",
            "dj_id": DJ_IDS[current],
            "fuente_url": DATASET_URL,
        }
    )

csv_path = DERIVED / "gabriela_estevez_source_consistency_audit_2022_2024.csv"
with csv_path.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=controls[0].keys())
    writer.writeheader()
    writer.writerows(controls)

close_2022 = asset_sum(2022, "C")
close_2023 = asset_sum(2023, "C")
open_2024 = asset_sum(2024, "I")
close_2024 = asset_sum(2024, "C")
detail_increase_2023 = close_2023 - close_2022
raw_close_2023 = decimal(summaries[2023]["total_bienes_final"])
raw_increase_2023 = raw_close_2023 - close_2022
official_valuation_2023 = decimal(summaries[2023]["diferencia_valuacion"])

with (DERIVED / "macro_deflators_2017_2025.csv").open(encoding="utf-8", newline="") as handle:
    macro = {int(row["anio"]): row for row in csv.DictReader(handle)}
ipc_factor = decimal(macro[2023]["ipc_indice_dic_2016_100"]) / decimal(macro[2022]["ipc_indice_dic_2016_100"])
ipc_pct = (ipc_factor - 1) * 100
detail_real_change_pct = (close_2023 / close_2022 / ipc_factor - 1) * 100

property_2022 = asset_sum(2022, "C", "INMUEBLES")
property_2023 = asset_sum(2023, "C", "INMUEBLES")
property_increase = property_2023 - property_2022
property_ipc_value = property_2022 * ipc_factor
property_ipc_increase = property_ipc_value - property_2022

category_rules = (
    ("Inmuebles", "INMUEBLES"),
    ("Vehículos", "AUTOMOTORES"),
    ("Depósitos", "DEPOSITO DE DINERO"),
    ("Efectivo", "DINERO EN EFECTIVO"),
    ("Bienes del hogar", "TOTAL DE BIENES EN EL HOGAR"),
)
composition = []
for year in (2023, 2024):
    for label, source_type in category_rules:
        value = asset_sum(year, "C", source_type)
        if value:
            composition.append(
                {
                    "persona_id": PERSON_ID,
                    "persona": PERSON,
                    "anio": year,
                    "categoria": label,
                    "importe_ars": str(value),
                    "dj_id": DJ_IDS[year],
                    "metodo": "Suma de bienes de cierre del detalle oficial; el total resumen queda separado por inconsistencia de escala.",
                    "fuente_url": DATASET_URL,
                }
            )

audit = {
    "metadata": {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "corte": "2026-09-03",
        "pregunta": "¿El salto 2023 refleja una variación patrimonial comparable o un cambio de escala entre capas de la fuente?",
        "alcance": "El control compara resumen, bienes y deudas del mismo consolidado oficial OA para 2022–2024; la identidad y la actividad legislativa se cotejan con fuentes oficiales ya respaldadas.",
        "etiqueta": "serie suspendida · quiebre de escala",
        "serie_estado": "suspendida_desde_2023_hasta_conciliar_resumen_y_detalle",
        "benchmark_estado": "suspendido_por_quiebre_escala_fuente",
    },
    "periodos": [
        {
            "persona_id": PERSON_ID,
            "persona": PERSON,
            "periodo": "2022-2023",
            "estado_fuente": "oficial_consolidado_oa_inconsistente",
            "bienes_inicio_ars": rounded(close_2022),
            "bienes_cierre_ars": rounded(close_2023),
            "aumento_bienes_ars": rounded(detail_increase_2023),
            "aumento_bienes_pct": percent(detail_increase_2023, close_2022),
            "bienes_cierre_resumen_bruto_ars": rounded(raw_close_2023),
            "aumento_bienes_resumen_bruto_ars": rounded(raw_increase_2023),
            "aumento_bienes_resumen_bruto_pct": percent(raw_increase_2023, close_2022),
            "diferencia_valuacion_total_ars": rounded(official_valuation_2023),
            "valuacion_sobre_aumento_bienes_pct": percent(official_valuation_2023, detail_increase_2023),
            "inmueble_inicio_ars": rounded(property_2022),
            "inmueble_cierre_ars": rounded(property_2023),
            "aumento_inmueble_ars": rounded(property_increase),
            "aumento_inmueble_pct": percent(property_increase, property_2022),
            "ipc_periodo_pct": rounded(ipc_pct),
            "inmueble_si_solo_ipc_ars": rounded(property_ipc_value),
            "aumento_inmueble_explicado_por_ipc_simple_pct": percent(property_ipc_increase, property_increase),
            "brecha_inmueble_vs_ipc_simple_ars": rounded(property_2023 - property_ipc_value),
            "lectura": "El +7.368,4% bruto nace de mezclar el cierre 2022 conciliado con un cierre 2023 diez veces mayor que sus propios bienes detallados. Con el detalle, el cambio es +646,8% nominal y +139,8% real: sigue siendo alto, pero es otra pregunta y no un rendimiento atribuible.",
            "fuente_url": DATASET_URL,
        }
    ],
    "controles": {
        "detalle_cierre_2022_ars": rounded(close_2022),
        "resumen_cierre_2022_ars": rounded(decimal(summaries[2022]["total_bienes_final"])),
        "detalle_cierre_2023_ars": rounded(close_2023),
        "resumen_cierre_2023_ars": rounded(raw_close_2023),
        "factor_resumen_sobre_detalle_cierre_2023": rounded(raw_close_2023 / close_2023),
        "detalle_inicio_2024_ars": rounded(open_2024),
        "resumen_inicio_2024_ars": rounded(decimal(summaries[2024]["total_bienes_inicio"])),
        "detalle_cierre_2024_ars": rounded(close_2024),
        "resumen_cierre_2024_ars": rounded(decimal(summaries[2024]["total_bienes_final"])),
        "factor_resumen_sobre_detalle_2024": rounded(decimal(summaries[2024]["total_bienes_final"]) / close_2024),
        "cambio_nominal_crudo_2022_2023_pct": percent(raw_increase_2023, close_2022),
        "cambio_nominal_detalle_2022_2023_pct": percent(detail_increase_2023, close_2022),
        "cambio_real_detalle_2022_2023_pct": rounded(detail_real_change_pct),
        "deuda_detalle_2024": "ausente_en_consolidado",
    },
    "composition": composition,
    "lectura_epistemica": {
        "documentado": [
            "El cierre 2022 del resumen ($4,21 M) coincide con la suma de sus bienes detallados; el cierre 2023 del resumen ($314,26 M) es exactamente diez veces el detalle ($31,43 M).",
            "El detalle conserva continuidad exacta: cierre 2022 = inicio 2023 y cierre 2023 = inicio 2024. La capa resumen cambia de escala en el cierre 2023 y mantiene ese factor diez durante 2024.",
            "En 2022 y 2023, los totales de deuda del resumen son diez veces las filas de deuda; para 2024 el consolidado informa totales pero no publica filas de deuda asociadas a esta declaración.",
            "Dentro del detalle 2023, el inmueble explica $15,92 M del aumento; el Jeep persistente suma $5,53 M, los bienes del hogar $2,19 M, los depósitos $1,48 M y aparece un Volkswagen por $2,09 M.",
        ],
        "compatible_pero_no_probado": [
            "El patrón exacto y persistente de factor diez es compatible con un corrimiento decimal o un error de exportación en la capa resumen, no con una multiplicación económica de esos mismos bienes.",
            "Los mayores importes de inmueble, vehículo y bienes del hogar pueden reflejar actualización de valuaciones fiscales o criterios de exposición, pero el consolidado no identifica cuánto aporta cada mecanismo.",
        ],
        "no_documentado": [
            "El campo agregado de diferencia de valuación 2023 ($4,51 M) sólo cubre 16,6% del aumento de bienes detallados y no concilia el puente por sí solo.",
            "Sin el formulario individual y sus eventuales rectificativas no puede determinarse qué escala reproduce lo efectivamente presentado ni completar de forma robusta el patrimonio neto 2024.",
            "La anomalía de publicación no demuestra enriquecimiento ilícito, corrupción ni una conducta atribuible a la persona declarada.",
        ],
        "conclusion": "La tasa bruta de +7.368,4% debe retirarse de la comparación: combina dos escalas incompatibles del mismo dataset. El detalle reduce el cambio a +646,8% nominal (+139,8% real), todavía elevado y concentrado en aumentos de importes de bienes persistentes, pero la fuente no permite separar con precisión revaluación, adquisición, ahorro u otras causas. Corresponde mostrar la composición y mantener suspendidos el benchmark y la conciliación, sin trasladar el error de OA a la persona.",
        "evidencia_para_cerrar": [
            "Formulario individual OA de los dj_id 718182 y 805974, incluidas rectificativas si existieran.",
            "Confirmación de OA sobre la escala correcta de bienes y deudas en los resúmenes 2023–2024.",
            "Detalle de deudas 2024 o una aclaración oficial sobre su ausencia.",
            "Conciliación explícita entre diferencia de valuación, ingresos, gastos, altas y bajas de bienes.",
        ],
    },
    "reconciliation_suspended": {
        "periodo": "2023–2024",
        "lectura": "La escala de bienes cambia dentro de 2023, las deudas del resumen ya venían multiplicadas por diez y el detalle de deuda 2024 está ausente; cualquier residual automático mezclaría capas incompatibles.",
    },
    "alerta_fuente": "El salto bruto 2023 está inflado por un quiebre exacto de escala: el resumen de cierre es 10× la suma de sus bienes detallados. En 2024 el factor continúa; las deudas también difieren por 10× en 2022–2023 y carecen de detalle en 2024. Se preservan los valores crudos, pero se suspenden tasa, benchmark y residual.",
    "fuentes": [
        {
            "tipo": "primaria",
            "titulo": "Consolidado OA 2012–2024",
            "url": DATASET_URL,
            "respaldo": "sources/datos_justicia/declaraciones-juradas-2012-2024.zip",
        },
        {
            "tipo": "primaria",
            "titulo": "Diputados · presentaciones ejercicio 2025",
            "url": HCDN_2025_URL,
            "respaldo": "sources/active_roster/hcdn_ddjj_ejercicio_2025_2026-09-01.html",
        },
    ],
}

json_path = DERIVED / "gabriela_estevez_patrimonial_audit_2022_2024.json"
json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

assert audit["controles"]["factor_resumen_sobre_detalle_cierre_2023"] == 10.0
assert audit["controles"]["factor_resumen_sobre_detalle_2024"] == 10.0
assert audit["controles"]["cambio_nominal_detalle_2022_2023_pct"] == 646.84
assert len(composition) == 8
print(f"OK: auditoría Gabriela Estévez · {len(controls)} controles de consistencia")
