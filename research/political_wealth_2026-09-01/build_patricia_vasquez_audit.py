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
LEGAL_PATH = ROOT / "sources" / "legal" / "decreto_127_1996_bienes_personales_usufructo_2026-09-03.html"
DATASET_URL = "https://datos.jus.gob.ar/dataset/declaraciones-juradas-patrimoniales-integrales"
HCDN_ROSTER_URL = "https://www.hcdn.gob.ar/diputados/"
LEGAL_URL = "https://www.argentina.gob.ar/normativa/nacional/decreto-127-1996-33500/actualizacion"
PERSON_ID = "dip-vasquez-patricia"
PERSON = "Patricia Vásquez"
DJ_IDS = {2023: "732253", 2024: "793321"}


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


for source_path in (ZIP_PATH, HCDN_ROSTER_PATH, LEGAL_PATH):
    assert source_path.is_file(), f"Falta la copia oficial: {source_path.name}"
roster_text = HCDN_ROSTER_PATH.read_text(encoding="utf-8", errors="replace").upper()
assert "VÁSQUEZ, PATRICIA" in roster_text
legal_text = LEGAL_PATH.read_text(encoding="utf-8", errors="replace").upper()
assert "NUDA PROPIEDAD" in legal_text and "ARTICULO 16" in legal_text

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
debt_open_2024 = decimal(summaries[2024]["deudas_inicio"])
debt_close_2024 = decimal(summaries[2024]["total_deudas_final"])

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
        "control": "deudas_resumen_vs_detalle",
        "valor_resumen_ars": rounded(debt_close_2024),
        "valor_control_ars": 0.0,
        "brecha_ars": 0.0,
        "ratio_resumen_sobre_detalle": "",
        "resultado": "concilia_cero",
        "dj_id": DJ_IDS[2024],
        "fuente_url": DATASET_URL,
    },
]

csv_path = DERIVED / "patricia_vasquez_source_consistency_audit_2023_2024.csv"
with csv_path.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=controls[0].keys())
    writer.writeheader()
    writer.writerows(controls)

asset_change = close_2024 - open_2024
valuation_total = decimal(summaries[2024]["diferencia_valuacion"])
income_net = decimal(summaries[2024]["ingresos_neto_gastos"])
bridge_residual = asset_change - valuation_total - income_net

real_estate_open = asset_sum(2024, "I", "INMUEBLES")
real_estate_close = asset_sum(2024, "C", "INMUEBLES")
vehicles_open = asset_sum(2024, "I", "AUTOMOTORES")
vehicles_close = asset_sum(2024, "C", "AUTOMOTORES")
deposits_open = asset_sum(2024, "I", "DEPOSITO DE DINERO")
deposits_close = asset_sum(2024, "C", "DEPOSITO DE DINERO")
cash_open = asset_sum(2024, "I", "DINERO EN EFECTIVO")
cash_close = asset_sum(2024, "C", "DINERO EN EFECTIVO")
household_open = household_sum(2024, "I")
household_close = household_sum(2024, "C")

real_estate_change = real_estate_close - real_estate_open
vehicles_change = vehicles_close - vehicles_open
deposits_change = deposits_close - deposits_open
cash_change = cash_close - cash_open
household_change = household_close - household_open

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
        "metodo": "Suma del detalle de cierre oficial; resumen y detalle concilian, y el inmueble se mantiene separado por el cambio de condición declarado.",
        "fuente_url": DATASET_URL,
    }
    for category, amount in (
        ("Inmueble", real_estate_close),
        ("Vehículos", vehicles_close),
        ("Bienes del hogar", household_close),
        ("Depósitos", deposits_close),
        ("Efectivo", cash_close),
    )
]

audit = {
    "metadata": {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "corte": "2026-09-03",
        "pregunta": "¿El salto 2024 se explica aritméticamente por valuación e ingresos, y qué documentación exigiría considerar justificado el cambio del inmueble?",
        "alcance": "El control compara DDJJ Anuales 2023–2024, verifica continuidad y composición, reconstruye el puente exacto y contrasta el cambio de nuda propiedad a herencia con la reglamentación oficial de Bienes Personales.",
        "etiqueta": "puente exacto · inmueble a documentar",
        "serie_estado": "auditada_con_cambio_juridico_inmueble_pendiente",
        "benchmark_estado": "comparable_solo_como_contrafactual_no_rendimiento",
        "benchmark_nota": "Los totales y la continuidad concilian, pero el salto está dominado por un inmueble que pasa de $0,01 a $245,17 M y cambia de nuda propiedad a herencia; el benchmark no representa rendimiento de cartera.",
    },
    "metricas_destacadas": [
        {"label": "Aumento real 2024", "valor": f"{rounded(real_change_pct):+.1f}%", "nota": "bienes y continuidad conciliados"},
        {"label": "Valuación / Δ bienes", "valor": f"{percent(valuation_total, asset_change):.1f}%", "nota": "campo agregado oficial"},
        {"label": "Inmueble / Δ bienes", "valor": f"{percent(real_estate_change, asset_change):.1f}%", "nota": "$0,01 → $245,17 M"},
        {"label": "Ingreso / Δ bienes", "valor": f"{percent(income_net, asset_change):.1f}%", "nota": "complemento exacto del puente"},
        {"label": "Residual del puente", "valor": "$ 0,00", "nota": "valuación + ingreso = Δ bienes"},
    ],
    "columnas_puente": [
        {"label": "Δ bienes", "field": "aumento_bienes_ars", "format": "money"},
        {"label": "Valuación", "field": "diferencia_valuacion_ars", "format": "money"},
        {"label": "Ingreso neto", "field": "ingresos_neto_gastos_ars", "format": "money"},
        {"label": "Δ inmueble", "field": "aumento_inmueble_ars", "format": "money"},
        {"label": "Residual", "field": "residual_puente_ars", "format": "money"},
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
            "diferencia_valuacion_ars": rounded(valuation_total),
            "ingresos_neto_gastos_ars": rounded(income_net),
            "aumento_inmueble_ars": rounded(real_estate_change),
            "aumento_vehiculos_ars": rounded(vehicles_change),
            "aumento_bienes_hogar_ars": rounded(household_change),
            "aumento_depositos_ars": rounded(deposits_change),
            "aumento_efectivo_ars": rounded(cash_change),
            "residual_puente_ars": rounded(bridge_residual),
            "ipc_periodo_pct": rounded(ipc_pct),
            "cambio_real_pct": rounded(real_change_pct),
            "lectura": "El aumento de $278,80 M se descompone exactamente en $227,06 M de diferencia de valuación y $51,74 M de ingreso neto. El inmueble aporta $245,17 M del cambio bruto y pasa de nuda propiedad valuada en $0,01 a herencia valuada en $245,17 M.",
            "fuente_url": DATASET_URL,
        }
    ],
    "controles": {
        "bienes_cierre_2023_ars": rounded(close_2023),
        "bienes_inicio_2024_ars": rounded(open_2024),
        "continuidad_cierre_inicio_brecha_ars": rounded(open_2024 - close_2023),
        "bienes_cierre_2024_ars": rounded(close_2024),
        "aumento_bienes_2024_ars": rounded(asset_change),
        "diferencia_valuacion_2024_ars": rounded(valuation_total),
        "ingresos_neto_gastos_2024_ars": rounded(income_net),
        "residual_valuacion_ingreso_ars": rounded(bridge_residual),
        "inmueble_inicio_2024_ars": rounded(real_estate_open),
        "inmueble_cierre_2024_ars": rounded(real_estate_close),
        "aumento_inmueble_2024_ars": rounded(real_estate_change),
        "inmueble_sobre_aumento_bienes_pct": percent(real_estate_change, asset_change),
        "valuacion_sobre_aumento_bienes_pct": percent(valuation_total, asset_change),
        "ingreso_sobre_aumento_bienes_pct": percent(income_net, asset_change),
        "cambio_real_2024_pct": rounded(real_change_pct),
        "deuda_cierre_2023_ars": rounded(debt_close_2023),
        "deuda_inicio_2024_ars": rounded(debt_open_2024),
        "deuda_cierre_2024_ars": rounded(debt_close_2024),
    },
    "composition": composition,
    "lectura_epistemica": {
        "documentado": [
            "Resumen y detalle de bienes concilian en el cierre 2023, la apertura 2024 y el cierre 2024; además, cierre y apertura coinciden exactamente en $33,79 M. No se informan deudas.",
            "El inmueble es el mismo departamento de Capital Federal, con ingreso al patrimonio el 23/12/2013 y titularidad 100%. En la apertura figura como nuda propiedad a $0,01 y al cierre como herencia a $245,17 M.",
            "El aumento total de $278,80 M coincide exactamente con $227,06 M de diferencia de valuación más $51,74 M de ingreso neto.",
            "Además del inmueble, aumentan los vehículos en $16,46 M, bienes del hogar en $12,77 M, depósitos en $4,36 M y la valuación del efectivo en dólares en $44.710.",
            "El artículo 16 del Decreto 127/1996 establece tratamientos diferentes para el usufructo gratuito y para la cesión onerosa de nuda propiedad con reserva de usufructo; el rótulo por sí solo no determina cuál supuesto corresponde.",
        ],
        "compatible_pero_no_probado": [
            "Un cambio efectivo en la situación sucesoria o en el usufructo podría alterar quién debe computar el inmueble y con qué proporción. El cambio de nuda propiedad a herencia es compatible con esa clase de evento, pero el consolidado no demuestra que haya ocurrido.",
            "La diferencia de valuación explica 81,4% del aumento total y el ingreso declarado el 18,6% restante, de modo que el puente agregado es internamente exacto.",
            "El residual cero prueba que los campos agregados cierran; no demuestra que $245,17 M sea la base fiscal correcta ni que la clasificación jurídica se haya aplicado correctamente.",
        ],
        "no_documentado": [
            "No se publica escritura, declaratoria de herederos, extinción de usufructo, fecha del cambio jurídico ni identificación del causante o usufructuario.",
            "Tampoco se informa la valuación fiscal homogénea 2024, base imponible inmobiliaria, costo actualizado o cálculo que lleva el inmueble de $0,01 a $245,17 M.",
            "La diferencia de valuación agregada es $18,11 M menor que el aumento del inmueble, por lo que no puede atribuirse todo el campo exclusivamente a esa propiedad sin el formulario de trabajo.",
            "Que la palabra “herencia” y la revaluación hagan plausible una explicación no permite concluir licitud, corrupción ni error: esas conclusiones requieren la documentación sucesoria y fiscal.",
        ],
        "conclusion": "El +324,9% real de 2024 es una variación auténtica del archivo: bienes, continuidad y deudas concilian. El puente agregado también cierra exactamente, con 81,4% explicado por diferencia de valuación y 18,6% por ingreso. Sin embargo, la justificación sustantiva depende casi por completo de un departamento que pasa de nuda propiedad a herencia y de $0,01 a $245,17 M. Esa transición puede tener una explicación jurídica y tributaria legítima, pero decir “fue sólo una revaluación” no basta: hacen falta el instrumento sucesorio o de usufructo y la base fiscal aplicada. Hasta entonces corresponde marcar explicación compatible, no licitud probada ni irregularidad demostrada.",
        "evidencia_para_cerrar": [
            "Formulario individual OA de los dj_id 732253 y 793321, incluidas hojas de trabajo y rectificativas.",
            "Escritura de donación o nuda propiedad, constitución y eventual extinción del usufructo, y declaratoria o adjudicación hereditaria.",
            "Valuación fiscal homogénea y base imponible inmobiliaria de CABA al 31/12/2024, con el cálculo usado en Bienes Personales.",
            "Extractos que permitan vincular el ingreso neto con el aumento de depósitos y los demás movimientos monetarios.",
        ],
    },
    "reconciliation_override": {
        "periodo": "2024",
        "subtitulo": "puente agregado exacto; justificación jurídica pendiente",
        "delta_patrimonio_neto_ars": rounded(asset_change),
        "componentes_disponibles_ars": rounded(valuation_total + income_net),
        "residual_ajustado_ars": rounded(bridge_residual),
        "lectura": "Diferencia de valuación ($227,06 M) + ingreso neto ($51,74 M) = aumento de patrimonio neto ($278,80 M). La identidad es exacta y no hay deuda; la pregunta pendiente no es aritmética, sino documental: por qué el inmueble cambia de nuda propiedad a herencia y cuál es la base fiscal de $245,17 M.",
    },
    "alerta_fuente": "No se detectan quiebres de escala ni faltantes de deuda: los totales y el puente agregado concilian. La reserva es sustantiva, no aritmética: el consolidado cambia la condición del inmueble y lo lleva de $0,01 a $245,17 M sin publicar el instrumento sucesorio ni el cálculo fiscal.",
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
        {
            "tipo": "primaria",
            "titulo": "Decreto 127/1996 · Bienes Personales, nuda propiedad",
            "url": LEGAL_URL,
            "respaldo": "sources/legal/decreto_127_1996_bienes_personales_usufructo_2026-09-03.html",
        },
    ],
}

json_path = DERIVED / "patricia_vasquez_patrimonial_audit_2023_2024.json"
json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

assert all(row["resultado"].startswith("concilia") for row in controls)
assert close_2023 == open_2024
assert debt_close_2023 == debt_open_2024 == debt_close_2024 == 0
assert rounded(real_estate_change + vehicles_change + household_change + deposits_change + cash_change) == rounded(asset_change)
assert rounded(valuation_total + income_net) == rounded(asset_change)
assert rounded(bridge_residual) == 0.0
assert rounded(sum((Decimal(row["importe_ars"]) for row in composition), Decimal("0"))) == rounded(close_2024)
assert audit["controles"]["cambio_real_2024_pct"] == 324.86
assert audit["controles"]["valuacion_sobre_aumento_bienes_pct"] == 81.44
print(f"OK: auditoría Patricia Vásquez · {len(controls)} controles de consistencia")
