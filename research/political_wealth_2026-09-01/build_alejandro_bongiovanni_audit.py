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
PERSON_ID = "dip-bongiovanni-alejandro"
PERSON = "Alejandro Bongiovanni"
DJ_IDS = {2023: "800114", 2024: "802146"}


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
assert "BONGIOVANNI, ALEJANDRO" in roster_text

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


close_2023 = asset_sum(2023, "C")
open_2024 = asset_sum(2024, "I")
close_2024 = asset_sum(2024, "C")
summary_close_2023 = decimal(summaries[2023]["total_bienes_final"])
summary_open_2024 = decimal(summaries[2024]["total_bienes_inicio"])
summary_close_2024 = decimal(summaries[2024]["total_bienes_final"])
debt_open_2024 = decimal(summaries[2024]["deudas_inicio"])
debt_close_2024 = decimal(summaries[2024]["total_deudas_final"])
debt_detail_close_2024 = sum(
    (decimal(row["deuda_importe"]) for row in debts[2024] if row["periodo_inicio_cierre"] == "C"),
    Decimal("0"),
)

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
        "resultado": "concilia",
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

csv_path = DERIVED / "alejandro_bongiovanni_source_consistency_audit_2023_2024.csv"
with csv_path.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=controls[0].keys())
    writer.writeheader()
    writer.writerows(controls)

asset_change = close_2024 - open_2024
debt_change = debt_close_2024 - debt_open_2024
net_worth_change = (close_2024 - debt_close_2024) - (open_2024 - debt_open_2024)
income_net = decimal(summaries[2024]["ingresos_neto_gastos"])
income_not_taxed = decimal(summaries[2024]["ingresos_no_alcanzados"])
personal_expenses = decimal(summaries[2024]["gastos_personales"])

credits_open = asset_sum(2024, "I", "CREDITOS")
credits_close = asset_sum(2024, "C", "CREDITOS")
deposits_open = asset_sum(2024, "I", "DEPOSITO DE DINERO")
deposits_close = asset_sum(2024, "C", "DEPOSITO DE DINERO")
cash_open = asset_sum(2024, "I", "DINERO EN EFECTIVO")
cash_close = asset_sum(2024, "C", "DINERO EFECTIVO")
credits_change = credits_close - credits_open
deposits_change = deposits_close - deposits_open
cash_change = cash_close - cash_open

with (DERIVED / "macro_deflators_2017_2025.csv").open(encoding="utf-8", newline="") as handle:
    macro = {int(row["anio"]): row for row in csv.DictReader(handle)}
ipc_factor = decimal(macro[2024]["ipc_indice_dic_2016_100"]) / decimal(macro[2023]["ipc_indice_dic_2016_100"])
ipc_pct = (ipc_factor - 1) * 100
real_change_pct = (close_2024 / open_2024 / ipc_factor - 1) * 100

composition = [
    {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "anio": 2024,
        "categoria": category,
        "importe_ars": str(amount),
        "dj_id": DJ_IDS[2024],
        "metodo": "Suma del detalle de cierre oficial; el total de bienes concilia exactamente con los tres componentes.",
        "fuente_url": DATASET_URL,
    }
    for category, amount in (
        ("Créditos", credits_close),
        ("Depósitos", deposits_close),
        ("Efectivo", cash_close),
    )
]

audit = {
    "metadata": {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "corte": "2026-09-03",
        "pregunta": "¿El fuerte aumento real de 2024 es consistente con el detalle y se parece más a rendimiento de una cartera o a acumulación de flujos declarados?",
        "alcance": "El control compara dos DDJJ Anuales rectificativas, verifica continuidad cierre–apertura, reconstruye la composición monetaria y contrasta el aumento con ingresos sin presumir una causalidad individual.",
        "etiqueta": "bienes conciliados · flujos compatibles",
        "serie_estado": "auditada_bienes_conciliados_y_continuidad_exacta",
        "benchmark_estado": "comparable_solo_como_contrafactual_no_rendimiento",
        "benchmark_nota": "La comparación matemática es válida porque los bienes concilian y hay continuidad exacta; no debe leerse como rendimiento de una cartera, ya que durante el período aparecen ingresos y créditos nuevos.",
    },
    "metricas_destacadas": [
        {"label": "Aumento nominal", "valor": f"{percent(asset_change, open_2024):+.1f}%", "nota": "bienes detalle 2024"},
        {"label": "Aumento real", "valor": f"{rounded(real_change_pct):+.1f}%", "nota": f"descontando IPC {rounded(ipc_pct):.1f}%"},
        {"label": "Ingreso neto / Δ", "valor": f"{percent(income_net, asset_change):.1f}%", "nota": "compatibilidad agregada"},
        {"label": "No alcanzados / Δ", "valor": f"{percent(income_not_taxed, asset_change):.1f}%", "nota": "campo separado del resumen"},
        {"label": "Activos monetarios", "valor": "100,0%", "nota": "efectivo, depósitos y créditos"},
    ],
    "columnas_puente": [
        {"label": "Δ bienes", "field": "aumento_bienes_ars", "format": "money"},
        {"label": "Ingreso neto", "field": "ingresos_neto_gastos_ars", "format": "money"},
        {"label": "No alcanzados", "field": "ingresos_no_alcanzados_ars", "format": "money"},
        {"label": "Δ créditos", "field": "aumento_creditos_ars", "format": "money"},
        {"label": "Δ efectivo+depósitos", "field": "aumento_efectivo_depositos_ars", "format": "money"},
    ],
    "periodos": [
        {
            "persona_id": PERSON_ID,
            "persona": PERSON,
            "periodo": "2024",
            "estado_fuente": "oficial_consolidado_oa",
            "bienes_inicio_ars": rounded(open_2024),
            "bienes_cierre_ars": rounded(close_2024),
            "aumento_bienes_ars": rounded(asset_change),
            "aumento_bienes_pct": percent(asset_change, open_2024),
            "ingresos_neto_gastos_ars": rounded(income_net),
            "ingresos_no_alcanzados_ars": rounded(income_not_taxed),
            "ingreso_neto_sobre_aumento_pct": percent(income_net, asset_change),
            "aumento_creditos_ars": rounded(credits_change),
            "aumento_depositos_ars": rounded(deposits_change),
            "aumento_efectivo_ars": rounded(cash_change),
            "aumento_efectivo_depositos_ars": rounded(cash_change + deposits_change),
            "aumento_deuda_ars": rounded(debt_change),
            "aumento_patrimonio_neto_ars": rounded(net_worth_change),
            "ipc_periodo_pct": rounded(ipc_pct),
            "cambio_real_pct": rounded(real_change_pct),
            "lectura": "El aumento de $22,27 M se recompone exactamente con créditos +$9,71 M, efectivo +$8,13 M y depósitos +$4,43 M. El ingreso neto declarado equivale a 229,5% del aumento; además figura otro campo de ingresos no alcanzados por $151,70 M. Hay compatibilidad holgada, no trazabilidad peso por peso.",
            "fuente_url": DATASET_URL,
        }
    ],
    "controles": {
        "bienes_cierre_2023_ars": rounded(close_2023),
        "bienes_inicio_2024_ars": rounded(open_2024),
        "continuidad_cierre_inicio_brecha_ars": rounded(open_2024 - close_2023),
        "bienes_cierre_2024_ars": rounded(close_2024),
        "aumento_bienes_2024_ars": rounded(asset_change),
        "cambio_nominal_2024_pct": percent(asset_change, open_2024),
        "cambio_real_2024_pct": rounded(real_change_pct),
        "ingresos_neto_gastos_2024_ars": rounded(income_net),
        "ingresos_no_alcanzados_2024_ars": rounded(income_not_taxed),
        "gastos_personales_2024_ars": rounded(personal_expenses),
        "deuda_cierre_resumen_2024_ars": rounded(debt_close_2024),
        "deuda_cierre_detalle_2024_ars": rounded(debt_detail_close_2024),
    },
    "composition": composition,
    "lectura_epistemica": {
        "documentado": [
            "Las DDJJ Anuales rectificativas 2023 y 2024 usan el mismo identificador nominal; el cierre 2023 y la apertura 2024 coinciden exactamente en $1,63 M y en sus tres depósitos.",
            "El total de cierre 2024, $23,90 M, concilia centavo por centavo con el detalle: $9,71 M en créditos, $8,13 M en efectivo y $6,06 M en depósitos.",
            "El puente del detalle es completo: créditos +$9,71 M, efectivo +$8,13 M y depósitos +$4,43 M explican los $22,27 M de aumento.",
            "El resumen informa $51,10 M de ingreso neto de gastos, $151,70 M de ingresos no alcanzados y $44,09 M de gastos personales.",
            "La deuda final publicada es $0,24 M, pero no existe ningún renglón correspondiente en el archivo consolidado de deudas.",
        ],
        "compatible_pero_no_probado": [
            "El ingreso neto por sí solo equivale a 229,5% del aumento de bienes, por lo que el crecimiento es aritméticamente compatible con los flujos declarados sin recurrir a una rentabilidad extraordinaria.",
            "Que el patrimonio cierre enteramente en efectivo, depósitos y créditos es compatible con ahorro y saldos de corto plazo; no demuestra el recorrido bancario ni el origen concreto de cada saldo.",
            "El benchmark de mercado puede conservarse como contrafactual matemático, pero no mide desempeño de cartera: el supuesto de cero aportes se contradice con la existencia de flujos anuales declarados.",
        ],
        "no_documentado": [
            "El consolidado no desagrega la naturaleza de los $151,70 M de ingresos no alcanzados ni permite verificar si existen solapamientos conceptuales con otros campos.",
            "No se aportan extractos para enlazar ingresos, gastos, efectivo, depósitos, billetera virtual y saldo a favor por retenciones.",
            "Falta el detalle de acreedor y concepto de la deuda final, aunque su monto equivale a sólo 1,1% del aumento de bienes.",
            "La compatibilidad contable no prueba licitud, rendimiento financiero ni ausencia de omisiones; tampoco sustenta por sí sola una imputación de irregularidad.",
        ],
        "conclusion": "A diferencia de los casos con escala rota, este +573,8% real sí parte de totales de bienes conciliados y de una continuidad anual exacta. El salto no se parece a una cartera que rindió esa tasa: aparece como acumulación de activos monetarios y créditos en un año con flujos declarados muy superiores al aumento. La explicación es holgadamente compatible en el agregado, pero no trazable sin formulario individual y extractos; además, la deuda final carece de desglose. Se conserva el benchmark sólo como contrafactual y se suspende el residual explicativo.",
        "evidencia_para_cerrar": [
            "Formulario individual OA de los dj_id 800114 y 802146, incluidas sus rectificativas.",
            "Desglose conceptual y documental de los $151,70 M informados como ingresos no alcanzados.",
            "Extractos de las cuentas, billetera virtual y constancia del saldo a favor por retenciones al cierre.",
            "Detalle de la deuda final de $240.031,48 y confirmación de que no existen rectificativas posteriores.",
        ],
    },
    "reconciliation_suspended": {
        "periodo": "2024",
        "lectura": "Los bienes y sus componentes concilian y los flujos declarados superan el aumento, pero el residual automático no puede presentarse como explicación causal: falta el desglose de la deuda y el campo de ingresos no alcanzados no trae composición ni trazabilidad en el consolidado.",
    },
    "alerta_fuente": "Los bienes superan todos los controles: cierre 2023, apertura 2024, continuidad y cierre 2024 concilian. La observación se limita a una deuda final pequeña sin renglones de detalle y a la falta de desagregación de los ingresos no alcanzados; no invalida el aumento de activos, pero sí una conciliación causal completa.",
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

json_path = DERIVED / "alejandro_bongiovanni_patrimonial_audit_2023_2024.json"
json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

assert all(row["resultado"] == "concilia" for row in controls[:4])
assert controls[4]["resultado"] == "detalle_ausente"
assert rounded(credits_change + deposits_change + cash_change) == rounded(asset_change)
assert rounded(sum((Decimal(row["importe_ars"]) for row in composition), Decimal("0"))) == rounded(close_2024)
assert audit["controles"]["continuidad_cierre_inicio_brecha_ars"] == 0.0
assert audit["controles"]["cambio_real_2024_pct"] == 573.79
assert audit["periodos"][0]["ingreso_neto_sobre_aumento_pct"] == 229.49
print(f"OK: auditoría Alejandro Bongiovanni · {len(controls)} controles de consistencia")
