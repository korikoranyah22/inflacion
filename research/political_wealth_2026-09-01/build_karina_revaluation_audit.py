from __future__ import annotations

import csv
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DERIVED = ROOT / "derived"
MACRO_PATH = DERIVED / "macro_deflators_2017_2025.csv"
JSON_PATH = DERIVED / "karina_milei_revaluation_audit_2023_2025.json"
BRIDGE_PATH = DERIVED / "karina_milei_revaluation_bridge_2024_2025.csv"
DEBT_PATH = DERIVED / "karina_milei_source_consistency_audit_2023_2025.csv"

OA_DATASET_URL = "https://datos.jus.gob.ar/dataset/declaraciones-juradas-patrimoniales-integrales"
OA_MANUAL_URL = "https://www.argentina.gob.ar/sites/default/files/instructivo_-arca-_presentacion_ddjj_anuales_f.1245.pdf"
LAW_URL = "https://www.argentina.gob.ar/normativa/nacional/ley-23966-365/actualizacion"
ARCA_2025_URL = "https://www.arca.gob.ar/gananciasYBienes/bienes-personales/valuaciones/periodo-fiscal-2025.asp"
LANACION_URL = "https://www.lanacion.com.ar/politica/declaracion-jurada-de-karina-milei-uno-por-uno-todos-los-bienes-informados-de-la-secretaria-general-nid01092026/"
CRONISTA_URL = "https://www.cronista.com/economia-politica/cuanto-crecieron-los-patrimonios-de-javier-y-karina-milei-en-el-ultimo-ano-bienes-dolares-y-deudas/"


def q(value: Decimal, digits: int = 2) -> Decimal:
    return value.quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP)


def number(value: Decimal, digits: int = 2) -> float:
    return float(q(value, digits))


def pct(numerator: Decimal, denominator: Decimal) -> Decimal:
    return numerator / denominator * Decimal("100")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


ipc: dict[int, Decimal] = {}
with MACRO_PATH.open(encoding="utf-8", newline="") as handle:
    for row in csv.DictReader(handle):
        ipc[int(row["anio"])] = Decimal(row["ipc_indice_dic_2016_100"])

assets_2023 = Decimal("3548270.42")
assets_2024 = Decimal("11401021.93")
assets_2025 = Decimal("35312784.57")
property_2023 = Decimal("1833559.24")
property_2024 = Decimal("3992825.14")
property_2025 = Decimal("28162492.74")
revaluation_2024 = Decimal("2196455.77")
revaluation_2025 = Decimal("24394137.87")

bridge_rows: list[dict[str, object]] = []
for start_year, end_year, start_assets, end_assets, start_property, end_property, revaluation, state, source in (
    (
        2023,
        2024,
        assets_2023,
        assets_2024,
        property_2023,
        property_2024,
        revaluation_2024,
        "oficial_consolidado_oa",
        OA_DATASET_URL,
    ),
    (
        2024,
        2025,
        assets_2024,
        assets_2025,
        property_2024,
        property_2025,
        revaluation_2025,
        "transcripcion_periodistica_pdf_oa_pendiente",
        CRONISTA_URL,
    ),
):
    asset_delta = end_assets - start_assets
    property_delta = end_property - start_property
    ipc_change = ipc[end_year] / ipc[start_year] - Decimal("1")
    property_if_only_ipc = start_property * (Decimal("1") + ipc_change)
    simple_ipc_delta = property_if_only_ipc - start_property
    bridge_rows.append(
        {
            "persona_id": "karina",
            "persona": "Karina Milei",
            "periodo": f"{start_year}-{end_year}",
            "estado_fuente": state,
            "bienes_inicio_ars": number(start_assets),
            "bienes_cierre_ars": number(end_assets),
            "aumento_bienes_ars": number(asset_delta),
            "aumento_bienes_pct": number(pct(asset_delta, start_assets)),
            "diferencia_valuacion_total_ars": number(revaluation),
            "valuacion_sobre_aumento_bienes_pct": number(pct(revaluation, asset_delta)),
            "inmueble_inicio_ars": number(start_property),
            "inmueble_cierre_ars": number(end_property),
            "aumento_inmueble_ars": number(property_delta),
            "aumento_inmueble_pct": number(pct(property_delta, start_property)),
            "inmueble_sobre_valuacion_total_pct": number(pct(property_delta, revaluation)),
            "ipc_periodo_pct": number(ipc_change * Decimal("100")),
            "inmueble_si_solo_ipc_ars": number(property_if_only_ipc),
            "aumento_inmueble_explicado_por_ipc_simple_pct": number(pct(simple_ipc_delta, property_delta)),
            "brecha_inmueble_vs_ipc_simple_ars": number(end_property - property_if_only_ipc),
            "fuente_url": source,
        }
    )

write_csv(BRIDGE_PATH, bridge_rows)

debt_rows = [
    {
        "anio_campo": "2023 cierre",
        "campo_consolidado_ars": "10908660.00",
        "control_independiente_ars": "1090866.00",
        "origen_control": "suma de 5 filas del archivo oficial de deudas 2023",
        "resultado": "no_concilia_factor_10",
        "lectura": "El total resumen es diez veces la suma de su propio detalle.",
        "fuente_url": OA_DATASET_URL,
    },
    {
        "anio_campo": "2024 inicio",
        "campo_consolidado_ars": "0.00",
        "control_independiente_ars": "1090866.00",
        "origen_control": "cierre detallado oficial 2023",
        "resultado": "no_arrastra_cierre_previo",
        "lectura": "El inicio 2024 no conserva la deuda detallada al cierre 2023.",
        "fuente_url": OA_DATASET_URL,
    },
    {
        "anio_campo": "2024 cierre",
        "campo_consolidado_ars": "8419610.00",
        "control_independiente_ars": "841961.00",
        "origen_control": "inicio 2025 transcripto del PDF OA por dos medios",
        "resultado": "no_concilia_factor_10",
        "lectura": "El total resumen es diez veces el importe que reaparece como apertura 2025.",
        "fuente_url": CRONISTA_URL,
    },
]
write_csv(DEBT_PATH, debt_rows)

row_2024, row_2025 = bridge_rows
audit = {
    "metadata": {
        "persona_id": "karina",
        "persona": "Karina Milei",
        "corte": "2026-09-02",
        "pregunta": "¿Qué parte del salto declarado explica la valuación y qué parte sigue necesitando respaldo documental?",
        "alcance": "2023–2024 usa el consolidado oficial OA; 2025 usa transcripciones coincidentes del PDF difundido, todavía sin copia primaria individual en el repositorio.",
        "estado_2025": "provisional_hasta_respaldar_pdf_oa_individual",
    },
    "periodos": bridge_rows,
    "hallazgos": {
        "valuacion_total_sobre_aumento_bienes_2025_pct": row_2025["valuacion_sobre_aumento_bienes_pct"],
        "inmueble_sobre_valuacion_total_2025_pct": row_2025["inmueble_sobre_valuacion_total_pct"],
        "aumento_inmueble_2025_pct": row_2025["aumento_inmueble_pct"],
        "ipc_2025_pct": row_2025["ipc_periodo_pct"],
        "aumento_inmueble_explicado_por_ipc_simple_pct": row_2025["aumento_inmueble_explicado_por_ipc_simple_pct"],
        "brecha_inmueble_vs_ipc_simple_ars": row_2025["brecha_inmueble_vs_ipc_simple_ars"],
        "otros_bienes_variacion_2025_ars": number(
            (assets_2025 - property_2025) - (assets_2024 - property_2024)
        ),
        "lectura_2024": "La valuación explicó 28,0% del aumento bruto. En el inmueble, el cambio 2023–2024 coincide prácticamente con el IPC del período.",
        "lectura_2025": "La diferencia de valuación declarada equivale a 102,0% del aumento bruto; el inmueble concentra 99,1% de esa valuación. La aritmética explica dónde aparece el salto, no por qué el insumo fiscal o metodológico cambió tanto.",
    },
    "lectura_epistemica": {
        "documentado": [
            "Es el mismo departamento con cochera, declarado desde 2011, sin una compra nueva en 2025.",
            "La diferencia de valuación declarada supera levemente todo el aumento de bienes 2025; los demás bienes, netos, bajaron.",
            "La valuación 2024 del inmueble siguió aproximadamente el IPC; la de 2025 subió 605,3% frente a 31,5% de IPC anual.",
        ],
        "compatible_pero_no_probado": [
            "Una corrección de la base fiscal 2017, un cambio catastral, una rectificación previa o la aplicación de otro piso legal podrían producir un salto sin compra ni ingreso nuevo.",
            "La Ley 23.966 obliga a comparar reglas y pisos de valuación; por eso una diferencia superior al IPC no es, por sí sola, ilícita.",
        ],
        "no_documentado": [
            "No se publicó junto con la cifra la valuación fiscal base, la boleta catastral, el costo computable ni la hoja de cálculo que llevan de $3,99 M a $28,16 M.",
            "Las transcripciones del PDF describen el resultado, pero no identifican cuál de las explicaciones posibles lo causó.",
        ],
        "conclusion": "Decir 'no es corrupción porque fue sólo una revaluación' excede la evidencia: la revaluación explica el asiento contable, pero no valida sus insumos ni audita el origen lícito. El salto tampoco prueba corrupción por sí solo. La conclusión neutral es una anomalía documental pendiente de trazabilidad, sin conclusión penal.",
        "evidencia_para_cerrar": [
            "PDF público OA 2025 individual y, si existió, su rectificativa.",
            "Valuación fiscal o base imponible del inmueble al 31/12/2017 y al cierre 2025.",
            "Cálculo aplicado bajo el artículo 22 de la Ley 23.966, con costo, amortización y piso fiscal comparados.",
            "Explicación de cualquier cambio catastral o corrección respecto de la valuación usada en 2024.",
        ],
    },
    "alertas_calidad_fuente": debt_rows,
    "fuentes": [
        {"tipo": "primaria", "titulo": "Consolidado OA 2012–2024", "url": OA_DATASET_URL, "respaldo": "sources/datos_justicia/declaraciones-juradas-2012-2024.zip"},
        {"tipo": "primaria", "titulo": "Manual F.1245 2025", "url": OA_MANUAL_URL, "respaldo": "sources/oa/instructivo_f1245_2025_2026-09-02.pdf"},
        {"tipo": "primaria", "titulo": "Ley 23.966, artículo 22", "url": LAW_URL, "respaldo": "sources/normativa/ley_23966_actualizada.html"},
        {"tipo": "primaria", "titulo": "ARCA · valuaciones 2025", "url": ARCA_2025_URL, "respaldo": "sources/arca/valuaciones_bienes_personales_2025_2026-09-02.html"},
        {"tipo": "secundaria", "titulo": "LA NACION · detalle Karina 2025", "url": LANACION_URL, "respaldo": "sources/descubrimiento/lanacion_karina_2025_2026-09-01.html"},
        {"tipo": "secundaria", "titulo": "El Cronista · puente patrimonial 2025", "url": CRONISTA_URL, "respaldo": "sources/descubrimiento/cronista_karina_revaluacion_2025_2026-09-02.html"},
    ],
}
JSON_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(
    "OK: auditoría Karina · "
    f"valuación 2025 = {row_2025['valuacion_sobre_aumento_bienes_pct']}% del aumento · "
    f"IPC simple explica {row_2025['aumento_inmueble_explicado_por_ipc_simple_pct']}% del salto del inmueble"
)
