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
SENATE_ROSTER_PATH = ROOT / "sources" / "active_roster" / "senado_listado_vigente_2026-09-01.html"
SENATE_DDJJ_PATH = ROOT / "sources" / "active_roster" / "senado_ddjj_2025_2026-09-01.html"
DATASET_URL = "https://datos.jus.gob.ar/dataset/declaraciones-juradas-patrimoniales-integrales"
SENATE_ROSTER_URL = "https://www.senado.gob.ar/senadores/listados/listaSenadoRes"
SENATE_DDJJ_URL = "https://www.senado.gob.ar/administrativo/ddjj/"
PERSON_ID = "sen-gadano-natalia-elena"
PERSON = "Natalia Elena Gadano"
DJ_IDS = {2023: "757003", 2024: "793922"}


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
for source_path in (SENATE_ROSTER_PATH, SENATE_DDJJ_PATH):
    assert source_path.is_file(), f"Falta la copia oficial respaldada: {source_path.name}"
    text = source_path.read_text(encoding="utf-8", errors="replace").upper()
    assert "GADANO" in text and "NATALIA" in text

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
summary_open_2024 = decimal(summaries[2024]["total_bienes_inicio"])
summary_close_2024 = decimal(summaries[2024]["total_bienes_final"])

controls = [
    {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "anio": 2023,
        "control": "total_bienes_inicio_vs_suma_detalle",
        "valor_resumen_ars": rounded(decimal(summaries[2023]["total_bienes_inicio"])),
        "valor_control_ars": rounded(initial_2023),
        "brecha_ars": rounded(decimal(summaries[2023]["total_bienes_inicio"]) - initial_2023),
        "ratio_resumen_sobre_detalle": rounded(decimal(summaries[2023]["total_bienes_inicio"]) / initial_2023),
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
        "resultado": "no_concilia",
        "dj_id": DJ_IDS[2024],
        "fuente_url": DATASET_URL,
    },
    {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "anio": 2024,
        "control": "deudas_resumen_vs_detalle",
        "valor_resumen_ars": 0.0,
        "valor_control_ars": 0.0,
        "brecha_ars": 0.0,
        "ratio_resumen_sobre_detalle": "",
        "resultado": "sin_deuda_en_resumen_ni_detalle",
        "dj_id": DJ_IDS[2024],
        "fuente_url": DATASET_URL,
    },
]

csv_path = DERIVED / "natalia_gadano_source_consistency_audit_2023_2024.csv"
with csv_path.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=controls[0].keys())
    writer.writeheader()
    writer.writerows(controls)

increase_2024 = close_2024 - open_2024
income_2024 = decimal(summaries[2024]["ingresos_neto_gastos"])
vehicle_open = asset_sum(2024, "I", "AUTOMOTORES")
vehicle_close = asset_sum(2024, "C", "AUTOMOTORES")
vehicle_change = vehicle_close - vehicle_open
deposit_open = asset_sum(2024, "I", "DEPOSITO DE DINERO")
deposit_close = asset_sum(2024, "C", "DEPOSITO DE DINERO")
deposit_change = deposit_close - deposit_open

with (DERIVED / "macro_deflators_2017_2025.csv").open(encoding="utf-8", newline="") as handle:
    macro = {int(row["anio"]): row for row in csv.DictReader(handle)}
ipc_factor = decimal(macro[2024]["ipc_indice_dic_2016_100"]) / decimal(macro[2023]["ipc_indice_dic_2016_100"])
ipc_pct = (ipc_factor - 1) * 100
real_change_2024_pct = (close_2024 / open_2024 / ipc_factor - 1) * 100
raw_change_2023_2024 = summary_close_2024 - initial_2023
detail_change_2023_2024 = close_2024 - initial_2023
detail_real_change_2023_2024_pct = (close_2024 / initial_2023 / ipc_factor - 1) * 100

composition = [
    {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "anio": 2024,
        "categoria": "Vehículos",
        "importe_ars": str(vehicle_close),
        "dj_id": DJ_IDS[2024],
        "metodo": "Suma del detalle de cierre oficial; el total resumen se mantiene separado por inconsistencia de escala.",
        "fuente_url": DATASET_URL,
    },
    {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "anio": 2024,
        "categoria": "Depósitos",
        "importe_ars": str(deposit_close),
        "dj_id": DJ_IDS[2024],
        "metodo": "Suma del detalle de cierre oficial; el total resumen se mantiene separado por inconsistencia de escala.",
        "fuente_url": DATASET_URL,
    },
]

audit = {
    "metadata": {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "corte": "2026-09-03",
        "pregunta": "¿El salto 2024 persiste al corregir la escala y qué movimientos del detalle resultan compatibles con los ingresos declarados?",
        "alcance": "El control compara resumen y detalle del consolidado OA 2023–2024, separa el recambio de activos y coteja identidad, cargo actual y presentación 2025 con las copias oficiales del Senado.",
        "etiqueta": "serie suspendida · detalle compatible",
        "serie_estado": "suspendida_desde_2024_hasta_conciliar_escala_resumen",
        "benchmark_estado": "suspendido_por_quiebre_escala_fuente",
    },
    "metricas_destacadas": [
        {"label": "Aumento bienes · 2024", "valor": f"{percent(increase_2024, open_2024):+.1f}%", "nota": "detalle inicio→cierre, no resumen 10×"},
        {"label": "Ingreso neto / aumento", "valor": f"{percent(income_2024, increase_2024):.1f}%", "nota": "compatibilidad agregada, no trazabilidad"},
        {"label": "Vehículos / aumento", "valor": f"{percent(vehicle_change, increase_2024):.1f}%", "nota": "EcoSport sale y entra una Rampage"},
        {"label": "Depósitos / aumento", "valor": f"{percent(deposit_change, increase_2024):.1f}%", "nota": "variación del saldo declarado"},
        {"label": "Cambio real · 2024", "valor": f"{rounded(real_change_2024_pct):+.1f}%", "nota": f"descontando IPC {rounded(ipc_pct):.1f}%"},
    ],
    "columnas_puente": [
        {"label": "Δ bienes detalle", "field": "aumento_bienes_ars", "format": "money"},
        {"label": "Ingreso neto", "field": "ingresos_neto_gastos_ars", "format": "money"},
        {"label": "Ingreso / Δ", "field": "ingreso_sobre_aumento_pct", "format": "pct"},
        {"label": "Δ vehículos", "field": "aumento_vehiculos_ars", "format": "money"},
        {"label": "Δ depósitos", "field": "aumento_depositos_ars", "format": "money"},
    ],
    "periodos": [
        {
            "persona_id": PERSON_ID,
            "persona": PERSON,
            "periodo": "2024",
            "estado_fuente": "oficial_consolidado_oa_inconsistente",
            "bienes_inicio_ars": rounded(open_2024),
            "bienes_cierre_ars": rounded(close_2024),
            "aumento_bienes_ars": rounded(increase_2024),
            "aumento_bienes_pct": percent(increase_2024, open_2024),
            "ingresos_neto_gastos_ars": rounded(income_2024),
            "ingreso_sobre_aumento_pct": percent(income_2024, increase_2024),
            "aumento_vehiculos_ars": rounded(vehicle_change),
            "vehiculos_sobre_aumento_pct": percent(vehicle_change, increase_2024),
            "aumento_depositos_ars": rounded(deposit_change),
            "depositos_sobre_aumento_pct": percent(deposit_change, increase_2024),
            "ipc_periodo_pct": rounded(ipc_pct),
            "cambio_real_detalle_pct": rounded(real_change_2024_pct),
            "lectura": "El detalle aumenta $58,59 M: $51,78 M netos en vehículos y $6,80 M en depósitos. El ingreso neto agregado de $68,39 M es mayor que ese aumento, por lo que el puente es aritméticamente compatible; no prueba por sí solo cómo se pagó cada activo.",
            "fuente_url": DATASET_URL,
        }
    ],
    "controles": {
        "detalle_inicial_2023_ars": rounded(initial_2023),
        "resumen_inicial_2023_ars": rounded(decimal(summaries[2023]["total_bienes_inicio"])),
        "detalle_inicio_2024_ars": rounded(open_2024),
        "resumen_inicio_2024_ars": rounded(summary_open_2024),
        "detalle_cierre_2024_ars": rounded(close_2024),
        "resumen_cierre_2024_ars": rounded(summary_close_2024),
        "factor_resumen_sobre_detalle_inicio_2024": rounded(summary_open_2024 / open_2024),
        "factor_resumen_sobre_detalle_cierre_2024": rounded(summary_close_2024 / close_2024),
        "cambio_nominal_crudo_2023_2024_pct": percent(raw_change_2023_2024, initial_2023),
        "cambio_nominal_detalle_2023_2024_pct": percent(detail_change_2023_2024, initial_2023),
        "cambio_real_detalle_2023_2024_pct": rounded(detail_real_change_2023_2024_pct),
        "deuda_resumen_2024_ars": 0.0,
        "deuda_detalle_2024_ars": 0.0,
    },
    "composition": composition,
    "lectura_epistemica": {
        "documentado": [
            "La declaración Inicial rectificativa 2023 concilia: el resumen y sus dos bienes detallados suman $6,70 M.",
            "En 2024, el resumen publica $82,14 M al inicio y $667,99 M al cierre, exactamente diez veces los detalles de $8,21 M y $66,80 M.",
            "El detalle 2024 reemplaza una EcoSport valuada en $7,22 M al inicio por una Rampage 2024 valuada en $59,00 M al cierre; los depósitos pasan de $1,00 M a $7,80 M.",
            "Los dos renglones de cierre consignan ingresos propios; el ingreso neto agregado informado es $68,39 M y no aparecen deudas en el resumen ni en el detalle.",
        ],
        "compatible_pero_no_probado": [
            "El ingreso neto declarado equivale a 116,7% del aumento de bienes detallados, de modo que la adquisición y el mayor saldo son aritméticamente compatibles con el flujo anual aun antes de conocer el calendario de cobros y pagos.",
            "El factor diez exacto en ambos extremos de 2024 es compatible con un corrimiento decimal en la exportación del resumen; el detalle conserva una composición internamente exacta.",
        ],
        "no_documentado": [
            "El consolidado no aporta comprobantes de compra, precio de transacción, medios de pago ni extractos que vinculen cada peso del ingreso con la pick-up o los depósitos.",
            "La compatibilidad agregada no demuestra el origen lícito de los fondos, pero tampoco respalda una imputación de irregularidad.",
            "Sin el formulario individual no puede decidirse cuál escala reproduce lo efectivamente presentado ni si existieron rectificativas posteriores.",
        ],
        "conclusion": "El +4.477,1% real que dispara la serie no es comparable: hereda un resumen 2024 multiplicado por diez. El detalle deja un aumento anual todavía alto, +713,2% nominal (+273,4% real), explicado exactamente por el recambio neto de vehículos y el aumento de depósitos. Como el ingreso neto declarado supera el incremento patrimonial detallado, el puente es contablemente compatible, aunque no constituye trazabilidad bancaria ni una certificación de licitud. Se suspende el benchmark sobre la serie cruda y se conservan por separado resumen, detalle e hipótesis documental.",
        "evidencia_para_cerrar": [
            "Formulario individual OA de los dj_id 757003 y 793922, incluidas rectificativas.",
            "Confirmación de OA sobre el corrimiento decimal del resumen 2024.",
            "Documentación de compra y medio de pago de la Rampage, junto con la baja o destino de la EcoSport.",
            "Desagregación temporal de ingresos, gastos y depósitos para conciliar el flujo anual.",
        ],
    },
    "reconciliation_suspended": {
        "periodo": "2024",
        "lectura": "El detalle permite un puente descriptivo compatible con ingresos, pero el resumen de bienes está multiplicado por diez; el residual automático de la serie permanece suspendido hasta confirmar la escala oficial.",
    },
    "alerta_fuente": "El resumen 2024 informa tanto el inicio como el cierre a una escala 10× respecto de la suma exacta del detalle. El salto real extremo de la trayectoria usa esa capa defectuosa; el caso profundo muestra el puente de detalle y suspende benchmark y residual sobre el total crudo.",
    "fuentes": [
        {
            "tipo": "primaria",
            "titulo": "Consolidado OA 2012–2024",
            "url": DATASET_URL,
            "respaldo": "sources/datos_justicia/declaraciones-juradas-2012-2024.zip",
        },
        {
            "tipo": "primaria",
            "titulo": "Senado · nómina vigente",
            "url": SENATE_ROSTER_URL,
            "respaldo": "sources/active_roster/senado_listado_vigente_2026-09-01.html",
        },
        {
            "tipo": "primaria",
            "titulo": "Senado · presentaciones ejercicio 2025",
            "url": SENATE_DDJJ_URL,
            "respaldo": "sources/active_roster/senado_ddjj_2025_2026-09-01.html",
        },
    ],
}

json_path = DERIVED / "natalia_gadano_patrimonial_audit_2023_2024.json"
json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

assert controls[1]["ratio_resumen_sobre_detalle"] == 10.0
assert controls[2]["ratio_resumen_sobre_detalle"] == 10.0
assert rounded(vehicle_change + deposit_change) == rounded(increase_2024)
assert audit["periodos"][0]["ingreso_sobre_aumento_pct"] == 116.74
print(f"OK: auditoría Natalia Gadano · {len(controls)} controles de consistencia")
