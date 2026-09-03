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
PERSON_ID = "dip-vega-yolanda"
PERSON = "Yolanda Vega"
DJ_IDS = {2023: "687371", 2024: "809852"}


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
assert "VEGA, YOLANDA" in roster_text

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


initial_2023 = asset_sum(2023, "I")
open_2024 = asset_sum(2024, "I")
close_2024 = asset_sum(2024, "C")
summary_initial_2023 = decimal(summaries[2023]["total_bienes_inicio"])
summary_open_2024 = decimal(summaries[2024]["total_bienes_inicio"])
summary_close_2024 = decimal(summaries[2024]["total_bienes_final"])
debt_open_2024 = decimal(summaries[2024]["deudas_inicio"])
debt_close_2024 = decimal(summaries[2024]["total_deudas_final"])
debt_detail_open_2024 = sum(
    (decimal(row["deuda_importe"]) for row in debts[2024] if row["periodo_inicio_cierre"] == "I"),
    Decimal("0"),
)
debt_detail_close_2024 = sum(
    (decimal(row["deuda_importe"]) for row in debts[2024] if row["periodo_inicio_cierre"] == "C"),
    Decimal("0"),
)

controls = [
    {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "anio": 2023,
        "control": "total_bienes_inicio_vs_suma_detalle",
        "valor_resumen_ars": rounded(summary_initial_2023),
        "valor_control_ars": rounded(initial_2023),
        "brecha_ars": rounded(summary_initial_2023 - initial_2023),
        "ratio_resumen_sobre_detalle": rounded(summary_initial_2023 / initial_2023),
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
        "resultado": "no_concilia",
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
        "control": "deudas_inicio_resumen_vs_detalle",
        "valor_resumen_ars": rounded(debt_open_2024),
        "valor_control_ars": rounded(debt_detail_open_2024),
        "brecha_ars": rounded(debt_open_2024 - debt_detail_open_2024),
        "ratio_resumen_sobre_detalle": "",
        "resultado": "concilia_cero",
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

csv_path = DERIVED / "yolanda_vega_source_consistency_audit_2023_2024.csv"
with csv_path.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=controls[0].keys())
    writer.writeheader()
    writer.writerows(controls)

asset_change_2024 = close_2024 - open_2024
debt_change_2024 = debt_close_2024 - debt_open_2024
net_worth_open_2024 = open_2024 - debt_open_2024
net_worth_close_2024 = close_2024 - debt_close_2024
net_worth_change_2024 = net_worth_close_2024 - net_worth_open_2024
income_2024 = decimal(summaries[2024]["ingresos_neto_gastos"])

vehicle_open = asset_sum(2024, "I", "AUTOMOTORES")
vehicle_close = asset_sum(2024, "C", "AUTOMOTORES")
deposit_open = asset_sum(2024, "I", "DEPOSITO DE DINERO")
deposit_close = asset_sum(2024, "C", "DEPOSITO DE DINERO")
cash_open = asset_sum(2024, "I", "DINERO EN EFECTIVO")
cash_close = asset_sum(2024, "C", "DINERO EFECTIVO")
household_open = sum(
    (decimal(row["bien_importe"]) for row in assets[2024] if row["periodo_inicio_cierre"] == "I" and "HOGAR" in row["bien_tipo"].upper()),
    Decimal("0"),
)
household_close = sum(
    (decimal(row["bien_importe"]) for row in assets[2024] if row["periodo_inicio_cierre"] == "C" and "HOGAR" in row["bien_tipo"].upper()),
    Decimal("0"),
)
share_open = asset_sum(2024, "I", "ACCIONES -CUOTAS")
share_close = asset_sum(2024, "C", "ACCIONES -CUOTAS")

vehicle_change = vehicle_close - vehicle_open
deposit_change = deposit_close - deposit_open
cash_change = cash_close - cash_open
household_change = household_close - household_open
share_change = share_close - share_open

with (DERIVED / "macro_deflators_2017_2025.csv").open(encoding="utf-8", newline="") as handle:
    macro = {int(row["anio"]): row for row in csv.DictReader(handle)}
ipc_factor = decimal(macro[2024]["ipc_indice_dic_2016_100"]) / decimal(macro[2023]["ipc_indice_dic_2016_100"])
ipc_pct = (ipc_factor - 1) * 100
apparent_real_change_pct = (summary_close_2024 / initial_2023 / ipc_factor - 1) * 100
annual_real_detail_change_pct = (close_2024 / open_2024 / ipc_factor - 1) * 100

composition = [
    {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "anio": 2024,
        "categoria": category,
        "importe_ars": str(amount),
        "dj_id": DJ_IDS[2024],
        "metodo": "Suma del detalle de cierre oficial; se separa del total de apertura defectuoso y de la deuda sin desglose.",
        "fuente_url": DATASET_URL,
    }
    for category, amount in (
        ("Vehículos", vehicle_close),
        ("Depósitos", deposit_close),
        ("Efectivo", cash_close),
        ("Bienes del hogar", household_close),
        ("Participación societaria", share_close),
    )
]

audit = {
    "metadata": {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "corte": "2026-09-03",
        "pregunta": "¿El salto 2023–2024 representa un enriquecimiento comparable o combina períodos, escalas y deuda de manera que exige otra lectura?",
        "alcance": "El control coteja resumen y detalle del consolidado OA, distingue la DDJJ Inicial 2023 del ejercicio Anual 2024 y reconstruye bienes, ingresos y deuda sin atribuir causalidad donde falta desglose.",
        "etiqueta": "serie suspendida · apalancamiento sin desglose",
        "serie_estado": "suspendida_por_perimetro_y_apertura_2024_inconsistente",
        "benchmark_estado": "suspendido_por_periodos_no_comparables_y_quiebre_escala",
        "benchmark_suspension_note": "La trayectoria enfrenta una DDJJ Inicial 2023 con un cierre Anual 2024 y atraviesa una apertura 2024 cuyo total resumen está a escala 10× respecto del detalle.",
    },
    "metricas_destacadas": [
        {"label": "Salto aparente real", "valor": f"{rounded(apparent_real_change_pct):+.1f}%", "nota": "Inicial 2023 → cierre 2024"},
        {"label": "Cambio anual real", "valor": f"{rounded(annual_real_detail_change_pct):+.1f}%", "nota": "detalle 2024, descontando IPC"},
        {"label": "Ingreso / Δ bienes", "valor": f"{percent(income_2024, asset_change_2024):.1f}%", "nota": "compatibilidad agregada"},
        {"label": "Nueva deuda / Δ bienes", "valor": f"{percent(debt_change_2024, asset_change_2024):.1f}%", "nota": "resumen; detalle ausente"},
        {"label": "Patrimonio neto cierre", "valor": f"-$ {rounded(abs(net_worth_close_2024) / Decimal('1000000')):.2f} M", "nota": "bienes menos deuda informada"},
    ],
    "columnas_puente": [
        {"label": "Δ bienes detalle", "field": "aumento_bienes_ars", "format": "money"},
        {"label": "Ingreso neto", "field": "ingresos_neto_gastos_ars", "format": "money"},
        {"label": "Ingreso / Δ", "field": "ingreso_sobre_aumento_pct", "format": "pct"},
        {"label": "Δ deuda resumen", "field": "aumento_deuda_ars", "format": "money"},
        {"label": "Δ patrimonio neto", "field": "aumento_patrimonio_neto_ars", "format": "money"},
    ],
    "periodos": [
        {
            "persona_id": PERSON_ID,
            "persona": PERSON,
            "periodo": "2024",
            "estado_fuente": "oficial_consolidado_oa_inconsistente",
            "bienes_inicio_ars": rounded(open_2024),
            "bienes_cierre_ars": rounded(close_2024),
            "aumento_bienes_ars": rounded(asset_change_2024),
            "aumento_bienes_pct": percent(asset_change_2024, open_2024),
            "ingresos_neto_gastos_ars": rounded(income_2024),
            "ingreso_sobre_aumento_pct": percent(income_2024, asset_change_2024),
            "aumento_deuda_ars": rounded(debt_change_2024),
            "deuda_sobre_aumento_bienes_pct": percent(debt_change_2024, asset_change_2024),
            "aumento_patrimonio_neto_ars": rounded(net_worth_change_2024),
            "ipc_periodo_pct": rounded(ipc_pct),
            "cambio_real_detalle_pct": rounded(annual_real_detail_change_pct),
            "lectura": "El detalle de bienes aumenta $60,11 M y concilia al cierre. El resumen agrega $149,21 M de deuda sin ningún renglón de detalle: el patrimonio neto pasa de $12,94 M a -$76,16 M. Es un crecimiento de activos apalancado en el agregado, no un aumento del patrimonio neto.",
            "fuente_url": DATASET_URL,
        }
    ],
    "controles": {
        "detalle_inicial_2023_ars": rounded(initial_2023),
        "resumen_inicial_2023_ars": rounded(summary_initial_2023),
        "detalle_inicio_2024_ars": rounded(open_2024),
        "resumen_inicio_2024_ars": rounded(summary_open_2024),
        "detalle_cierre_2024_ars": rounded(close_2024),
        "resumen_cierre_2024_ars": rounded(summary_close_2024),
        "factor_resumen_sobre_detalle_inicio_2024": rounded(summary_open_2024 / open_2024),
        "factor_resumen_sobre_detalle_cierre_2024": rounded(summary_close_2024 / close_2024),
        "deuda_inicio_resumen_2024_ars": rounded(debt_open_2024),
        "deuda_cierre_resumen_2024_ars": rounded(debt_close_2024),
        "deuda_cierre_detalle_2024_ars": rounded(debt_detail_close_2024),
        "aumento_bienes_detalle_2024_ars": rounded(asset_change_2024),
        "aumento_patrimonio_neto_2024_ars": rounded(net_worth_change_2024),
        "cambio_nominal_aparente_2023_2024_pct": percent(summary_close_2024 - initial_2023, initial_2023),
        "cambio_real_aparente_2023_2024_pct": rounded(apparent_real_change_pct),
        "cambio_nominal_detalle_2024_pct": percent(asset_change_2024, open_2024),
        "cambio_real_detalle_2024_pct": rounded(annual_real_detail_change_pct),
    },
    "composition": composition,
    "lectura_epistemica": {
        "documentado": [
            "La DDJJ Inicial rectificativa 2023 informa $2,22 M de bienes y deuda cero; su resumen concilia exactamente con cuatro renglones de detalle.",
            "La DDJJ Anual 2024 informa $129,41 M de bienes al inicio, pero los siete renglones iniciales suman $12,94 M: el resumen está exactamente a escala 10×. Al cierre, resumen y detalle sí concilian en $73,05 M.",
            "Dentro de 2024 el detalle aumenta $60,11 M: vehículos +$51,79 M, depósitos +$4,28 M, efectivo +$3,90 M y participación societaria +$0,15 M; bienes del hogar no varían.",
            "Al cierre aparece una Toyota SW4 2024 por $62,02 M. El ingreso neto agregado informado es $50,46 M.",
            "La deuda del resumen pasa de cero a $149,21 M, pero el archivo oficial de deudas no contiene renglones para esa declaración.",
        ],
        "compatible_pero_no_probado": [
            "El ingreso declarado cubre 83,9% del aumento de bienes; la nueva deuda agregada es 248,2% de ese aumento. En conjunto hay capacidad aritmética suficiente, pero no trazabilidad de cada compra ni prueba de que el crédito haya financiado la SW4.",
            "Al computar la deuda publicada, el patrimonio neto cae $89,10 M durante 2024 y cierra en -$76,16 M. Por eso el salto de bienes brutos no equivale a enriquecimiento neto.",
            "El factor diez exacto del total de apertura es compatible con un corrimiento decimal en la exportación, aunque sólo el formulario individual u OA pueden confirmar cuál cifra reproduce la presentación original.",
        ],
        "no_documentado": [
            "No se publican acreedor, moneda, finalidad, plazo ni saldo por obligación de los $149,21 M de deuda final.",
            "El consolidado no aporta contrato, precio de transacción, medio de pago ni vinculación bancaria de la SW4.",
            "Tampoco explica por sí solo la sustitución de los automotores declarados ni permite homologar sin reservas la DDJJ Inicial 2023 con el cierre Anual 2024.",
            "Estos archivos no permiten concluir corrupción ni licitud: permiten medir consistencia, compatibilidad contable y vacíos documentales.",
        ],
        "conclusion": "El +1.409,6% real visible entre 2023 y 2024 no es un indicador comparable: enfrenta una DDJJ Inicial con un cierre Anual y atraviesa una apertura 2024 cuyo resumen está multiplicado por diez. El detalle 2024 sí muestra un aumento fuerte de activos, +464,5% nominal (+159,2% real), concentrado en vehículos; pero simultáneamente aparece una deuda de $149,21 M y el patrimonio neto cae. La explicación financiera es plausible en el agregado, no verificable en su destino porque falta todo el detalle de deuda. Corresponde suspender benchmark y residual, y pedir documentación antes de interpretar el salto como inversión, enriquecimiento o irregularidad.",
        "evidencia_para_cerrar": [
            "Formulario individual OA de los dj_id 687371 y 809852, incluidas rectificativas y anexos reservados permitidos.",
            "Confirmación de OA sobre el factor diez del total de bienes al inicio de 2024.",
            "Desglose de los $149,21 M de deuda final: acreedor, moneda, finalidad, plazo y saldo.",
            "Documentación de compra y medio de pago de la SW4, y constancias de venta o baja de los vehículos que dejan de aparecer.",
        ],
    },
    "reconciliation_suspended": {
        "periodo": "2024",
        "lectura": "Puede calcularse que los activos detallados suben $60,11 M y el patrimonio neto agregado cae $89,10 M, pero no un residual explicativo robusto: la apertura de bienes tiene una escala 10× en el resumen y la deuda final de $149,21 M carece por completo de detalle.",
    },
    "alerta_fuente": "El total de cierre 2024 concilia con el detalle; el problema está en la comparación. La trayectoria mezcla una DDJJ Inicial 2023 con un cierre Anual 2024, el total de apertura 2024 está a escala 10× y la deuda final no tiene desglose. El caso conserva cada capa y evita presentar bienes brutos como patrimonio neto.",
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

json_path = DERIVED / "yolanda_vega_patrimonial_audit_2023_2024.json"
json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

assert controls[0]["ratio_resumen_sobre_detalle"] == 1.0
assert controls[1]["ratio_resumen_sobre_detalle"] == 10.0
assert controls[2]["ratio_resumen_sobre_detalle"] == 1.0
assert controls[4]["resultado"] == "detalle_ausente"
assert rounded(vehicle_change + deposit_change + cash_change + household_change + share_change) == rounded(asset_change_2024)
assert rounded(sum((Decimal(row["importe_ars"]) for row in composition), Decimal("0"))) == rounded(close_2024)
assert audit["periodos"][0]["ingreso_sobre_aumento_pct"] == 83.94
assert audit["periodos"][0]["deuda_sobre_aumento_bienes_pct"] == 248.21
print(f"OK: auditoría Yolanda Vega · {len(controls)} controles de consistencia")
