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
HCDN_ROSTER_PATH = ROOT / "sources" / "active_roster" / "hcdn_diputados_vigentes_2026-09-01.html"
DATASET_URL = "https://datos.jus.gob.ar/dataset/declaraciones-juradas-patrimoniales-integrales"
HCDN_ROSTER_URL = "https://www.hcdn.gob.ar/diputados/"
PERSON_ID = "dip-correa-llano-facundo"
PERSON = "Facundo Correa Llano"
DJ_IDS = {2023: "734662", 2024: "789410"}


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
assert HCDN_ROSTER_PATH.is_file(), "Falta la copia oficial de la nómina HCDN"
roster_text = HCDN_ROSTER_PATH.read_text(encoding="utf-8", errors="replace").upper()
assert "CORREA LLANO, FACUNDO" in roster_text

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
    return sum(
        (decimal(row["deuda_importe"]) for row in debts[year] if row["periodo_inicio_cierre"] == period),
        Decimal("0"),
    )


def household_sum(year: int, period: str) -> Decimal:
    return sum(
        (
            decimal(row["bien_importe"])
            for row in assets[year]
            if row["periodo_inicio_cierre"] == period
            and "HOGAR" in f'{row["bien_tipo"]} {row["bien_descripcion"]}'.upper()
        ),
        Decimal("0"),
    )


close_2023 = asset_sum(2023, "C")
open_2024 = asset_sum(2024, "I")
close_2024 = asset_sum(2024, "C")
summary_close_2023 = decimal(summaries[2023]["total_bienes_final"])
summary_open_2024 = decimal(summaries[2024]["total_bienes_inicio"])
summary_close_2024 = decimal(summaries[2024]["total_bienes_final"])
debt_close_2023 = decimal(summaries[2023]["total_deudas_final"])
debt_detail_close_2023 = debt_sum(2023, "C")
debt_open_2024 = decimal(summaries[2024]["deudas_inicio"])
debt_close_2024 = decimal(summaries[2024]["total_deudas_final"])
debt_detail_close_2024 = debt_sum(2024, "C")

controls = [
    {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "anio": 2023,
        "control": "total_bienes_cierre_vs_suma_detalle",
        "valor_resumen_ars": rounded(summary_close_2023),
        "valor_control_ars": rounded(close_2023),
        "brecha_ars": rounded(summary_close_2023 - close_2023),
        "ratio_resumen_sobre_detalle": rounded(summary_close_2023 / close_2023),
        "resultado": "concilia",
        "dj_id": DJ_IDS[2023],
        "fuente_url": DATASET_URL,
    },
    {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "anio": 2023,
        "control": "deudas_cierre_resumen_vs_detalle",
        "valor_resumen_ars": rounded(debt_close_2023),
        "valor_control_ars": rounded(debt_detail_close_2023),
        "brecha_ars": rounded(debt_close_2023 - debt_detail_close_2023),
        "ratio_resumen_sobre_detalle": rounded(debt_close_2023 / debt_detail_close_2023),
        "resultado": "concilia",
        "dj_id": DJ_IDS[2023],
        "fuente_url": DATASET_URL,
    },
    {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "anio": 2024,
        "control": "total_bienes_inicio_vs_suma_detalle",
        "valor_resumen_ars": rounded(summary_open_2024),
        "valor_control_ars": rounded(open_2024),
        "brecha_ars": rounded(summary_open_2024 - open_2024),
        "ratio_resumen_sobre_detalle": rounded(summary_open_2024 / open_2024),
        "resultado": "concilia",
        "dj_id": DJ_IDS[2024],
        "fuente_url": DATASET_URL,
    },
    {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "anio": 2024,
        "control": "continuidad_cierre_2023_vs_inicio_2024",
        "valor_resumen_ars": rounded(summary_close_2023),
        "valor_control_ars": rounded(summary_open_2024),
        "brecha_ars": rounded(summary_open_2024 - summary_close_2023),
        "ratio_resumen_sobre_detalle": rounded(summary_open_2024 / summary_close_2023),
        "resultado": "no_concilia_reexpresion_apertura",
        "dj_id": DJ_IDS[2024],
        "fuente_url": DATASET_URL,
    },
    {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "anio": 2024,
        "control": "total_bienes_cierre_vs_suma_detalle",
        "valor_resumen_ars": rounded(summary_close_2024),
        "valor_control_ars": rounded(close_2024),
        "brecha_ars": rounded(summary_close_2024 - close_2024),
        "ratio_resumen_sobre_detalle": rounded(summary_close_2024 / close_2024),
        "resultado": "concilia",
        "dj_id": DJ_IDS[2024],
        "fuente_url": DATASET_URL,
    },
    {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "anio": 2024,
        "control": "deudas_cierre_resumen_vs_detalle",
        "valor_resumen_ars": rounded(debt_close_2024),
        "valor_control_ars": rounded(debt_detail_close_2024),
        "brecha_ars": rounded(debt_close_2024 - debt_detail_close_2024),
        "ratio_resumen_sobre_detalle": "",
        "resultado": "detalle_ausente",
        "dj_id": DJ_IDS[2024],
        "fuente_url": DATASET_URL,
    },
]

csv_path = DERIVED / "facundo_correa_llano_source_consistency_audit_2023_2024.csv"
with csv_path.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=controls[0].keys())
    writer.writeheader()
    writer.writerows(controls)

asset_change = close_2024 - open_2024
series_asset_change = close_2024 - close_2023
opening_restatement = open_2024 - close_2023
debt_reduction = debt_open_2024 - debt_close_2024
net_worth_open = open_2024 - debt_open_2024
net_worth_close = close_2024 - debt_close_2024
net_worth_change = net_worth_close - net_worth_open

shares_close_2023 = asset_sum(2023, "C", "ACCIONES -CUOTAS")
shares_open = asset_sum(2024, "I", "ACCIONES -CUOTAS")
shares_close = asset_sum(2024, "C", "ACCIONES -CUOTAS")
vehicle_close_2023 = asset_sum(2023, "C", "AUTOMOTORES")
vehicle_open = asset_sum(2024, "I", "AUTOMOTORES")
vehicle_close = asset_sum(2024, "C", "AUTOMOTORES")
household_close_2023 = household_sum(2023, "C")
household_open = household_sum(2024, "I")
household_close = household_sum(2024, "C")
credits_close_2023 = asset_sum(2023, "C", "CREDITOS")
credits_open = asset_sum(2024, "I", "CREDITOS")
credits_close = asset_sum(2024, "C", "CREDITOS")
deposits_close_2023 = asset_sum(2023, "C", "DEPOSITO DE DINERO")
deposits_open = asset_sum(2024, "I", "DEPOSITO DE DINERO")
deposits_close = asset_sum(2024, "C", "DEPOSITO DE DINERO")

revaluation_components = (
    (shares_close - shares_open)
    + (vehicle_close - vehicle_open)
    + (household_close - household_open)
)
opening_restatement_components = (
    (shares_open - shares_close_2023)
    + (vehicle_open - vehicle_close_2023)
    + (household_open - household_close_2023)
)
monetary_asset_change = (credits_close - credits_open) + (deposits_close - deposits_open)

valuation_total = decimal(summaries[2024]["diferencia_valuacion"])
income_net = decimal(summaries[2024]["ingresos_neto_gastos"])
income_not_taxed = decimal(summaries[2024]["ingresos_no_alcanzados"])
personal_expenses = decimal(summaries[2024]["gastos_personales"])
non_deductible_expenses = decimal(summaries[2024]["gastos_no_deducibles"])
resources = income_net + income_not_taxed
financial_uses = monetary_asset_change + debt_reduction + personal_expenses + non_deductible_expenses
financial_saving = resources - personal_expenses - non_deductible_expenses
bridge_components = valuation_total + financial_saving
bridge_residual = net_worth_change - bridge_components

with (DERIVED / "macro_deflators_2017_2025.csv").open(encoding="utf-8", newline="") as handle:
    macro = {int(row["anio"]): row for row in csv.DictReader(handle)}
ipc_factor = decimal(macro[2024]["ipc_indice_dic_2016_100"]) / decimal(macro[2023]["ipc_indice_dic_2016_100"])
ipc_pct = (ipc_factor - 1) * 100
series_real_change_pct = (close_2024 / close_2023 / ipc_factor - 1) * 100
annual_real_change_pct = (close_2024 / open_2024 / ipc_factor - 1) * 100

composition = [
    {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "anio": 2024,
        "categoria": category,
        "importe_ars": str(amount),
        "dj_id": DJ_IDS[2024],
        "metodo": "Suma del detalle de cierre oficial; el total concilia exactamente y la valuación se controla por separado.",
        "fuente_url": DATASET_URL,
    }
    for category, amount in (
        ("Participaciones societarias", shares_close),
        ("Vehículos", vehicle_close),
        ("Depósitos", deposits_close),
        ("Créditos", credits_close),
        ("Bienes del hogar", household_close),
    )
]

audit = {
    "metadata": {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "corte": "2026-09-03",
        "pregunta": "¿Cuánto del salto 2024 corresponde a valuación, cuánto a flujos y qué parte nace de una reexpresión entre el cierre anterior y la nueva apertura?",
        "alcance": "El control separa continuidad interanual, movimiento dentro de la DDJJ Anual 2024 y patrimonio neto; recompone valuación, ingresos, gastos, activos monetarios y deuda con los campos del consolidado OA.",
        "etiqueta": "puente exacto · valuación dominante",
        "serie_estado": "auditada_con_reexpresion_de_apertura_documentada",
        "benchmark_estado": "comparable_solo_como_contrafactual_no_rendimiento",
        "benchmark_nota": "Los totales de cierre concilian, pero el salto combina una reexpresión de apertura y una diferencia de valuación que explica la mayor parte del cambio; no representa el rendimiento observado de una cartera.",
    },
    "metricas_destacadas": [
        {"label": "Salto real de la serie", "valor": f"{rounded(series_real_change_pct):+.1f}%", "nota": "cierre 2023 → cierre 2024"},
        {"label": "Cambio real 2024", "valor": f"{rounded(annual_real_change_pct):+.1f}%", "nota": "apertura reexpresada → cierre"},
        {"label": "Valuación / Δ bienes", "valor": f"{percent(valuation_total, asset_change):.1f}%", "nota": "coincide con activos no monetarios"},
        {"label": "Reexpresión de apertura", "valor": f"$ {rounded(opening_restatement / Decimal('1000000')):.2f} M", "nota": "vs. cierre 2023"},
        {"label": "Residual del puente", "valor": "$ 0,00", "nota": "identidad agregada exacta"},
    ],
    "columnas_puente": [
        {"label": "Δ patrimonio neto", "field": "aumento_patrimonio_neto_ars", "format": "money"},
        {"label": "Valuación", "field": "diferencia_valuacion_ars", "format": "money"},
        {"label": "Ingresos totales", "field": "recursos_declarados_ars", "format": "money"},
        {"label": "Gastos declarados", "field": "gastos_declarados_ars", "format": "money"},
        {"label": "Residual", "field": "residual_puente_ars", "format": "money"},
    ],
    "periodos": [
        {
            "persona_id": PERSON_ID,
            "persona": PERSON,
            "periodo": "2024",
            "estado_fuente": "oficial_consolidado_oa_control_agregado",
            "bienes_inicio_ars": rounded(open_2024),
            "bienes_cierre_ars": rounded(close_2024),
            "aumento_bienes_ars": rounded(asset_change),
            "aumento_bienes_pct": percent(asset_change, open_2024),
            "aumento_patrimonio_neto_ars": rounded(net_worth_change),
            "diferencia_valuacion_ars": rounded(valuation_total),
            "recursos_declarados_ars": rounded(resources),
            "gastos_declarados_ars": rounded(personal_expenses + non_deductible_expenses),
            "ahorro_financiero_ars": rounded(financial_saving),
            "aumento_activos_monetarios_ars": rounded(monetary_asset_change),
            "reduccion_deuda_ars": rounded(debt_reduction),
            "residual_puente_ars": rounded(bridge_residual),
            "ipc_periodo_pct": rounded(ipc_pct),
            "cambio_real_pct": rounded(annual_real_change_pct),
            "lectura": "La valuación de $105,25 M más el ahorro financiero neto de $27,29 M explican exactamente el aumento de patrimonio neto de $132,54 M. Ese ahorro se usa exactamente en $18,73 M de activos monetarios y $8,56 M de reducción de deuda.",
            "fuente_url": DATASET_URL,
        }
    ],
    "controles": {
        "bienes_cierre_2023_ars": rounded(close_2023),
        "bienes_inicio_2024_ars": rounded(open_2024),
        "reexpresion_apertura_ars": rounded(opening_restatement),
        "reexpresion_componentes_no_monetarios_ars": rounded(opening_restatement_components),
        "bienes_cierre_2024_ars": rounded(close_2024),
        "aumento_bienes_2024_ars": rounded(asset_change),
        "diferencia_valuacion_2024_ars": rounded(valuation_total),
        "valuacion_componentes_no_monetarios_ars": rounded(revaluation_components),
        "valuacion_sobre_aumento_bienes_pct": percent(valuation_total, asset_change),
        "aumento_activos_monetarios_ars": rounded(monetary_asset_change),
        "reduccion_deuda_ars": rounded(debt_reduction),
        "recursos_declarados_ars": rounded(resources),
        "gastos_declarados_ars": rounded(personal_expenses + non_deductible_expenses),
        "usos_financieros_mas_gastos_ars": rounded(financial_uses),
        "residual_recursos_usos_ars": rounded(resources - financial_uses),
        "aumento_patrimonio_neto_ars": rounded(net_worth_change),
        "residual_puente_patrimonio_ars": rounded(bridge_residual),
        "cambio_real_serie_2023_2024_pct": rounded(series_real_change_pct),
        "cambio_real_intra_2024_pct": rounded(annual_real_change_pct),
        "deuda_cierre_resumen_2024_ars": rounded(debt_close_2024),
        "deuda_cierre_detalle_2024_ars": rounded(debt_detail_close_2024),
    },
    "composition": composition,
    "lectura_epistemica": {
        "documentado": [
            "Los totales de bienes concilian con el detalle tanto al cierre 2023 como al inicio y cierre 2024. La deuda 2023 también concilia y la apertura 2024 repite exactamente su cierre.",
            "El inicio 2024 conserva las mismas sociedades, el mismo modelo y fecha de compra del vehículo y los bienes del hogar, y eleva su valuación agregada en $29,64 M; depósitos y créditos mantienen exactamente sus saldos. El año de fabricación del Corolla cambia de 2022 a 2023 entre archivos.",
            "Dentro de 2024, las participaciones societarias aumentan $98,57 M, el vehículo $6,32 M y los bienes del hogar $0,37 M. La suma, $105,25 M, coincide centavo por centavo con la diferencia de valuación informada.",
            "Los créditos y depósitos aumentan $18,73 M y la deuda cae $8,56 M. Ambos usos suman $27,29 M.",
            "Ingreso neto de gastos más ingresos no alcanzados suman $49,27 M; al restar gastos personales y no deducibles por $21,97 M quedan exactamente los mismos $27,29 M.",
        ],
        "compatible_pero_no_probado": [
            "El puente agregado cierra con residual cero: valuación de $105,25 M más ahorro financiero de $27,29 M explican el aumento de patrimonio neto de $132,54 M.",
            "La diferencia de valuación es compatible con la actualización de las participaciones en Boedo Center y Sankalpa, del Corolla Cross y de los bienes del hogar porque sus cambios suman exactamente el campo informado.",
            "La conciliación demuestra coherencia interna del consolidado; no verifica los criterios contables, balances societarios, valor fiscal del vehículo ni movimientos bancarios subyacentes.",
        ],
        "no_documentado": [
            "No se publican balances ni método de valuación de Boedo Center S.A. y Sankalpa S.A., responsables del 93,7% de la diferencia de valuación.",
            "La deuda final de $5,63 M no tiene renglones en el archivo 2024, por lo que no pueden identificarse acreedores ni comprobarse qué obligaciones fueron canceladas.",
            "El consolidado no explica por qué la apertura 2024 reexpresa en $29,64 M esos activos respecto del cierre 2023, ni si el cambio de año del vehículo es una corrección descriptiva o una sustitución.",
            "Un residual cero prueba una identidad aritmética con los campos publicados; no certifica licitud, valor económico ni ausencia de omisiones.",
        ],
        "conclusion": "El +490,3% real de cierre a cierre está correctamente sumado, pero mezcla una reexpresión de apertura de $29,64 M con el movimiento del ejercicio. Usando la apertura 2024, el aumento real es +79,5% y la diferencia de valuación explica 84,9% de los bienes incorporados. El resto forma un puente financiero exacto con ingresos, gastos, créditos, depósitos y reducción de deuda. Es el caso más conciliado hasta ahora: la explicación agregada cierra, mientras quedan abiertas la justificación económica de las valuaciones societarias, la reexpresión inicial y el detalle de acreedores; ninguna de esas preguntas equivale por sí sola a una imputación de irregularidad.",
        "evidencia_para_cerrar": [
            "Formulario individual OA de los dj_id 734662 y 789410 para confirmar la base de apertura y sus anexos.",
            "Balances y método de valuación aplicados a Boedo Center S.A. y Sankalpa S.A. en ambos extremos de 2024.",
            "Tabla fiscal o documentación usada para valuar el Corolla Cross y los bienes del hogar.",
            "Desglose de la deuda final 2024 y constancias agregadas de cancelación de las obligaciones existentes al inicio.",
        ],
    },
    "reconciliation_override": {
        "periodo": "2024",
        "subtitulo": "puente agregado exacto con campos del consolidado OA",
        "delta_patrimonio_neto_ars": rounded(net_worth_change),
        "componentes_disponibles_ars": rounded(bridge_components),
        "residual_ajustado_ars": rounded(bridge_residual),
        "lectura": "Valuación ($105,25 M) + ingresos netos y no alcanzados − gastos personales y no deducibles ($27,29 M netos) = aumento de patrimonio neto ($132,54 M). El componente financiero coincide con activos monetarios nuevos más reducción de deuda. La identidad es exacta, aunque la deuda final carece de desglose por acreedor.",
    },
    "alerta_fuente": "Resumen y detalle de bienes concilian en ambos extremos, y el puente agregado cierra con residual cero. Se conservan dos reservas documentales: la apertura 2024 reexpresa los mismos activos $29,64 M por encima del cierre 2023 y la deuda final de $5,63 M no tiene desglose en el archivo correspondiente.",
    "fuentes": [
        {
            "tipo": "primaria",
            "titulo": "Consolidado OA 2012–2024",
            "url": DATASET_URL,
            "respaldo": "sources/datos_justicia/declaraciones-juradas-2012-2024.zip",
        },
        {
            "tipo": "primaria",
            "titulo": "Cámara de Diputados · nómina vigente",
            "url": HCDN_ROSTER_URL,
            "respaldo": "sources/active_roster/hcdn_diputados_vigentes_2026-09-01.html",
        },
    ],
}

json_path = DERIVED / "facundo_correa_llano_patrimonial_audit_2023_2024.json"
json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

assert controls[0]["ratio_resumen_sobre_detalle"] == 1.0
assert controls[1]["ratio_resumen_sobre_detalle"] == 1.0
assert controls[2]["ratio_resumen_sobre_detalle"] == 1.0
assert controls[4]["ratio_resumen_sobre_detalle"] == 1.0
assert controls[5]["resultado"] == "detalle_ausente"
assert rounded(opening_restatement_components) == rounded(opening_restatement)
assert rounded(revaluation_components) == rounded(valuation_total)
assert rounded(valuation_total + monetary_asset_change) == rounded(asset_change)
assert rounded(resources) == rounded(financial_uses)
assert rounded(bridge_residual) == 0.0
assert rounded(sum((Decimal(row["importe_ars"]) for row in composition), Decimal("0"))) == rounded(close_2024)
assert audit["controles"]["cambio_real_serie_2023_2024_pct"] == 490.28
print(f"OK: auditoría Facundo Correa Llano · {len(controls)} controles de consistencia")
