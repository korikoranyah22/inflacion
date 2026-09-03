from __future__ import annotations

import csv
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DERIVED = ROOT / "derived"
MACRO_PATH = DERIVED / "macro_deflators_2017_2025.csv"
BRIDGE_PATH = DERIVED / "javier_milei_patrimonial_bridge_2023_2025.csv"
COMPONENTS_PATH = DERIVED / "javier_milei_revaluation_components_2025.csv"
SOURCE_AUDIT_PATH = DERIVED / "javier_milei_source_consistency_audit_2023_2025.csv"
JSON_PATH = DERIVED / "javier_milei_revaluation_audit_2023_2025.json"

OA_DATASET_URL = "https://datos.jus.gob.ar/dataset/declaraciones-juradas-patrimoniales-integrales"
OA_SERVICE_URL = "https://www.argentina.gob.ar/servicio/consultar-declaraciones-juradas-de-funcionarios-publicos"
LAW_URL = "https://www.argentina.gob.ar/normativa/nacional/ley-23966-365/actualizacion"
CRONISTA_URL = "https://www.cronista.com/economia-politica/cuanto-crecieron-los-patrimonios-de-javier-y-karina-milei-en-el-ultimo-ano-bienes-dolares-y-deudas/"
LANACION_URL = "https://www.lanacion.com.ar/politica/javier-milei-declaro-bienes-y-depositos-por-295-millones-y-registro-una-suba-con-respecto-a-2024-nid31082026/"
PDF_2024_MIRROR_URL = "https://ikona.telesurtv.net/content/uploads/2025/07/declaracion-jurada-14-dac2f10c7a.pdf"
PDF_2023_MIRROR_URL = "https://portada.com.ar/tools/redirect.php?i=40417&s=784dc69555d5fdc5e3363e3e2adaae1f&t=3"

ZIP_PATH = ROOT / "sources" / "datos_justicia" / "declaraciones-juradas-2012-2024.zip"
PDF_2024_PATH = ROOT / "sources" / "oa" / "javier_milei_ddjj_anual_2024_copia_espejo_2026-09-02.pdf"
PDF_2023_PATH = ROOT / "sources" / "oa" / "javier_milei_ddjj_anual_2023_copia_espejo_2026-09-02.pdf"
CRONISTA_PATH = ROOT / "sources" / "descubrimiento" / "cronista_karina_revaluacion_2025_2026-09-02.html"
LANACION_PATH = ROOT / "sources" / "descubrimiento" / "lanacion_milei_karina_2025_2026-09-02.html"


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


assert ZIP_PATH.is_file(), "Falta el consolidado oficial OA respaldado"
assert PDF_2024_PATH.is_file() and PDF_2024_PATH.read_bytes()[:4] == b"%PDF", "Falta el PDF OA 2024"
assert PDF_2023_PATH.is_file() and PDF_2023_PATH.read_bytes()[:4] == b"%PDF", "Falta el PDF OA 2023"
cronista_html = CRONISTA_PATH.read_text(encoding="utf-8")
lanacion_html = LANACION_PATH.read_text(encoding="utf-8")
for needle in ("295.182.652,87", "73.005.241,07", "73.573.546,13", "65.562,10"):
    assert needle in cronista_html, f"El respaldo de El Cronista no contiene {needle}"
for needle in ("295.182.652", "586.357"):
    assert needle in lanacion_html, f"El control de La Nación no contiene {needle}"

ipc: dict[int, Decimal] = {}
with MACRO_PATH.open(encoding="utf-8", newline="") as handle:
    for row in csv.DictReader(handle):
        ipc[int(row["anio"])] = Decimal(row["ipc_indice_dic_2016_100"])

period_inputs = [
    {
        "periodo": "2022-2023",
        "estado_fuente": "oficial_consolidado_oa",
        "start_year": 2022,
        "end_year": 2023,
        "assets_start": Decimal("21101634.54"),
        "assets_end": Decimal("125640891.45"),
        "debt_start": Decimal("0"),
        "debt_end": Decimal("0"),
        "revaluation": Decimal("71886098.96"),
        "income": Decimal("22021827.07"),
        "untaxed_income": Decimal("35434617.00"),
        "non_deductible": Decimal("12296927.01"),
        "personal_spending": Decimal("12506359.11"),
        "exempt_linked_expenses": Decimal("0"),
        "property_start": Decimal("6657569.52"),
        "property_end": Decimal("13657100.16"),
        "raw_residual": Decimal("-318911553.00"),
        "source": OA_DATASET_URL,
        "lectura": "El PDF individual corrige un cero extra del CSV; con $35,43 M de ingresos no alcanzados, el puente cierra exactamente.",
    },
    {
        "periodo": "2023-2024",
        "estado_fuente": "oficial_consolidado_oa",
        "start_year": 2023,
        "end_year": 2024,
        "assets_start": Decimal("125640891.45"),
        "assets_end": Decimal("206046375.48"),
        "debt_start": Decimal("0"),
        "debt_end": Decimal("0"),
        "revaluation": Decimal("54546101.49"),
        "income": Decimal("92157396.22"),
        "untaxed_income": Decimal("0"),
        "non_deductible": Decimal("0"),
        "personal_spending": Decimal("43391712.88"),
        "exempt_linked_expenses": Decimal("22906300.80"),
        "property_start": Decimal("13657100.16"),
        "property_end": Decimal("38419071.20"),
        "raw_residual": Decimal("-22906300.80"),
        "source": PDF_2024_MIRROR_URL,
        "lectura": "El anexo del PDF contiene $22,91 M de gastos que el consolidado no exporta; incorporarlos elimina el residual.",
    },
    {
        "periodo": "2024-2025",
        "estado_fuente": "transcripcion_periodistica_pdf_oa_pendiente",
        "start_year": 2024,
        "end_year": 2025,
        "assets_start": Decimal("206046375.48"),
        "assets_end": Decimal("295182652.87"),
        "debt_start": Decimal("0"),
        "debt_end": Decimal("586357.00"),
        "revaluation": Decimal("73005241.07"),
        "income": Decimal("81806723.92"),
        "untaxed_income": Decimal("0"),
        "non_deductible": Decimal("0"),
        "personal_spending": Decimal("66262044.60"),
        "exempt_linked_expenses": Decimal("0"),
        "property_start": Decimal("38419071.20"),
        "property_end": Decimal("73573546.13"),
        "raw_residual": None,
        "source": CRONISTA_URL,
        "lectura": "El puente publicado cierra al centavo: 81,9% del aumento bruto es valuación y, descontado IPC, los bienes crecen 8,9%.",
    },
]

bridge_rows: list[dict[str, object]] = []
for item in period_inputs:
    asset_delta = item["assets_end"] - item["assets_start"]
    net_delta = (item["assets_end"] - item["debt_end"]) - (item["assets_start"] - item["debt_start"])
    known = (
        item["revaluation"]
        + item["income"]
        + item["untaxed_income"]
        - item["non_deductible"]
        - item["personal_spending"]
        - item["exempt_linked_expenses"]
    )
    property_delta = item["property_end"] - item["property_start"]
    ipc_change = ipc[item["end_year"]] / ipc[item["start_year"]] - Decimal("1")
    property_if_only_ipc = item["property_start"] * (Decimal("1") + ipc_change)
    simple_ipc_delta = property_if_only_ipc - item["property_start"]
    real_change = (item["assets_end"] / item["assets_start"]) / (Decimal("1") + ipc_change) - Decimal("1")
    bridge_rows.append(
        {
            "persona_id": "javier",
            "persona": "Javier Milei",
            "periodo": item["periodo"],
            "estado_fuente": item["estado_fuente"],
            "bienes_inicio_ars": number(item["assets_start"]),
            "bienes_cierre_ars": number(item["assets_end"]),
            "aumento_bienes_ars": number(asset_delta),
            "aumento_bienes_pct": number(pct(asset_delta, item["assets_start"])),
            "aumento_bienes_real_ipc_pct": number(real_change * Decimal("100")),
            "deuda_cierre_ars": number(item["debt_end"]),
            "delta_patrimonio_neto_ars": number(net_delta),
            "diferencia_valuacion_total_ars": number(item["revaluation"]),
            "valuacion_sobre_aumento_bienes_pct": number(pct(item["revaluation"], asset_delta)),
            "inmueble_inicio_ars": number(item["property_start"]),
            "inmueble_cierre_ars": number(item["property_end"]),
            "aumento_inmueble_ars": number(property_delta),
            "aumento_inmueble_pct": number(pct(property_delta, item["property_start"])),
            "inmueble_sobre_valuacion_total_pct": number(pct(property_delta, item["revaluation"])),
            "ipc_periodo_pct": number(ipc_change * Decimal("100")),
            "inmueble_si_solo_ipc_ars": number(property_if_only_ipc),
            "aumento_inmueble_explicado_por_ipc_simple_pct": number(pct(simple_ipc_delta, property_delta)),
            "brecha_inmueble_vs_ipc_simple_ars": number(item["property_end"] - property_if_only_ipc),
            "ingresos_netos_ars": number(item["income"]),
            "ingresos_no_alcanzados_controlados_ars": number(item["untaxed_income"]),
            "gastos_no_deducibles_ars": number(item["non_deductible"]),
            "gastos_personales_ars": number(item["personal_spending"]),
            "gastos_vinculados_exentos_ars": number(item["exempt_linked_expenses"]),
            "residual_csv_sin_control_ars": "" if item["raw_residual"] is None else number(item["raw_residual"]),
            "residual_ajustado_fuente_ars": number(net_delta - known),
            "lectura": item["lectura"],
            "fuente_url": item["source"],
        }
    )

assert all(abs(Decimal(str(row["residual_ajustado_fuente_ars"]))) < Decimal("0.01") for row in bridge_rows)
write_csv(BRIDGE_PATH, bridge_rows)

fx_start = Decimal("1029")
fx_end = Decimal("1446")
usd_deposit_start = Decimal("65542.49")
property_delta_2025 = Decimal("73573546.13") - Decimal("38419071.20")
component_inputs = [
    ("Inmueble", property_delta_2025, "Mismo inmueble; cambio de valuación fiscal informado."),
    ("FX sobre depósito USD preexistente", usd_deposit_start * (fx_end - fx_start), "Saldo inicial en USD por diferencia de cotización declarada."),
    ("FX sobre USD efectivo", Decimal("20000") * (fx_end - fx_start), "Los USD 20.000 físicos no cambian; cambia su equivalente en pesos."),
]
known_components = sum((amount for _, amount, _ in component_inputs), Decimal("0"))
total_revaluation_2025 = Decimal("73005241.07")
component_inputs.append(("Otros componentes / redondeos", total_revaluation_2025 - known_components, "Resto no desagregado por las transcripciones periodísticas."))
component_rows = [
    {
        "persona_id": "javier",
        "persona": "Javier Milei",
        "periodo": "2024-2025",
        "componente": label,
        "importe_ars": number(amount),
        "porcentaje_valuacion_total": number(pct(amount, total_revaluation_2025)),
        "lectura": reading,
        "estado_fuente": "transcripcion_periodistica_pdf_oa_pendiente",
        "fuente_url": CRONISTA_URL,
    }
    for label, amount, reading in component_inputs
]
assert q(sum((Decimal(str(row["importe_ars"])) for row in component_rows), Decimal("0"))) == total_revaluation_2025
write_csv(COMPONENTS_PATH, component_rows)

source_audit_rows = [
    {
        "periodo_campo": "2023 · ingresos no alcanzados",
        "valor_consolidado_ars": "354346170.00",
        "valor_control_ars": "35434617.00",
        "origen_control": "PDF individual OA 2023 localizado y aritmética del puente",
        "resultado": "no_concilia_factor_10",
        "impacto": "El CSV agrega un cero; corregirlo elimina exactamente el residual de -$318.911.553.",
        "fuente_url": PDF_2023_MIRROR_URL,
    },
    {
        "periodo_campo": "2024 · total ingreso neto de 4 categorías",
        "valor_consolidado_ars": "996965100.00",
        "valor_control_ars": "99696510.00",
        "origen_control": "suma de categorías y PDF individual OA 2024",
        "resultado": "no_concilia_factor_10",
        "impacto": "El total auxiliar del CSV agrega un cero; el campo neto usado en el puente sí es correcto.",
        "fuente_url": PDF_2024_MIRROR_URL,
    },
    {
        "periodo_campo": "2024 · gastos vinculados a ingresos exentos / monotributo",
        "valor_consolidado_ars": "",
        "valor_control_ars": "22906300.80",
        "origen_control": "página 5 del PDF individual OA 2024",
        "resultado": "campo_omitido_en_consolidado",
        "impacto": "Es idéntico al residual crudo; incorporarlo hace que la evolución patrimonial cierre al centavo.",
        "fuente_url": PDF_2024_MIRROR_URL,
    },
    {
        "periodo_campo": "2025 · valuación del inmueble",
        "valor_consolidado_ars": "",
        "valor_control_ars": "73573546.13",
        "origen_control": "El Cronista; La Nación conserva por error aparente el valor 2024 de $38.419.071,20",
        "resultado": "transcripciones_secundarias_no_coinciden",
        "impacto": "Se usa el detalle que reconcilia, pero 2025 sigue provisional hasta obtener el PDF OA individual.",
        "fuente_url": CRONISTA_URL,
    },
]
write_csv(SOURCE_AUDIT_PATH, source_audit_rows)

latest = bridge_rows[-1]
fx_known = component_rows[1]["importe_ars"] + component_rows[2]["importe_ars"]
audit = {
    "metadata": {
        "persona_id": "javier",
        "persona": "Javier Milei",
        "corte": "2026-09-02",
        "pregunta": "¿El crecimiento declarado es rendimiento, ingreso nuevo o actualización contable, y la evolución reconcilia?",
        "alcance": "2022–2024 combina el consolidado oficial con los PDF individuales 2023 y 2024 respaldados; 2025 usa transcripciones coincidentes en totales, todavía sin PDF OA individual local.",
        "estado_2025": "provisional_hasta_respaldar_pdf_oa_individual",
        "etiqueta": "puente reconciliado · insumos de valuación pendientes",
    },
    "periodos": bridge_rows,
    "componentes_valuacion_2025": component_rows,
    "hallazgos": {
        "aumento_bienes_2025_pct": latest["aumento_bienes_pct"],
        "aumento_bienes_real_2025_pct": latest["aumento_bienes_real_ipc_pct"],
        "valuacion_sobre_aumento_bienes_2025_pct": latest["valuacion_sobre_aumento_bienes_pct"],
        "inmueble_sobre_valuacion_total_2025_pct": latest["inmueble_sobre_valuacion_total_pct"],
        "fx_conocido_sobre_valuacion_total_2025_pct": number(pct(Decimal(str(fx_known)), total_revaluation_2025)),
        "componentes_inmueble_fx_sobre_valuacion_2025_pct": number(pct(known_components, total_revaluation_2025)),
        "aumento_inmueble_2025_pct": latest["aumento_inmueble_pct"],
        "ipc_2025_pct": latest["ipc_periodo_pct"],
        "aumento_inmueble_explicado_por_ipc_simple_pct": latest["aumento_inmueble_explicado_por_ipc_simple_pct"],
        "brecha_inmueble_vs_ipc_simple_ars": latest["brecha_inmueble_vs_ipc_simple_ars"],
        "residual_ajustado_2025_ars": latest["residual_ajustado_fuente_ars"],
    },
    "lectura_epistemica": {
        "documentado": [
            "En 2025 los bienes brutos aumentan 43,3%, pero sólo 8,9% después de descontar el IPC del año.",
            "La diferencia de valuación explica 81,9% del aumento bruto; inmueble y efecto cambiario conocido explican 97,0% de esa partida.",
            "El puente 2025 reconcilia al centavo: valuación + ingresos netos − gastos personales − nueva deuda = cambio del patrimonio neto.",
        ],
        "compatible_pero_no_probado": [
            "La casa, los vehículos y casi todos los dólares ya existían: una gran parte del salto nominal es actualización de valores, no compra de activos.",
            "El ingreso neto y los gastos declarados explican el componente no atribuible a valuación, bajo el perímetro público del formulario.",
        ],
        "no_documentado": [
            "La copia primaria individual 2025 y su eventual rectificativa todavía no están disponibles en el repositorio.",
            "Faltan la base fiscal y la hoja de cálculo que expliquen por qué el inmueble sube 91,5% frente a 31,5% de IPC.",
            "Dos transcripciones periodísticas discrepan sobre el valor 2025 del inmueble; sólo una de ellas reconcilia con la valuación total publicada.",
        ],
        "conclusion": "El aumento declarado no debe presentarse como rendimiento de una cartera: en 2025 está dominado por valuaciones y, en términos reales, es 8,9%. Los flujos públicos reconciliados vuelven coherente la aritmética, pero no auditan por sí solos las bases fiscales ni prueban el origen lícito de cada ingreso. Tampoco hay en estos números, por sí solos, prueba de corrupción.",
        "evidencia_para_cerrar": [
            "PDF OA 2025 individual y cualquier rectificativa posterior.",
            "Valuación fiscal/base imponible y cálculo del inmueble al cierre 2024 y 2025.",
            "Desagregación primaria de los $2,18 M restantes de la diferencia de valuación 2025.",
            "Confirmación del tratamiento fiscal de los ingresos y gastos que componen el puente público.",
        ],
    },
    "reconciliation_override": {
        "periodo": "2025 · provisional",
        "delta_patrimonio_neto_ars": latest["delta_patrimonio_neto_ars"],
        "componentes_disponibles_ars": latest["delta_patrimonio_neto_ars"],
        "residual_ajustado_ars": latest["residual_ajustado_fuente_ars"],
        "lectura": "La igualdad cierra con la deuda final de $586.357; la verificación sigue siendo documental, no penal.",
    },
    "alertas_calidad_fuente": source_audit_rows,
    "alerta_fuente": "El residual que mostraba el dashboard para 2024 no era una anomalía patrimonial: el PDF contiene $22,91 M de gastos que el CSV abierto omitió. También se corrigieron dos campos multiplicados por diez. Se preservan ambos valores y la corrección queda auditable.",
    "fuentes": [
        {"tipo": "primaria", "titulo": "Consolidado OA 2012–2024", "url": OA_DATASET_URL, "respaldo": "sources/datos_justicia/declaraciones-juradas-2012-2024.zip"},
        {"tipo": "primaria · copia espejo", "titulo": "PDF OA individual 2023", "url": PDF_2023_MIRROR_URL, "respaldo": "sources/oa/javier_milei_ddjj_anual_2023_copia_espejo_2026-09-02.pdf"},
        {"tipo": "primaria · copia espejo", "titulo": "PDF OA individual 2024", "url": PDF_2024_MIRROR_URL, "respaldo": "sources/oa/javier_milei_ddjj_anual_2024_copia_espejo_2026-09-02.pdf"},
        {"tipo": "primaria", "titulo": "Ley 23.966, artículo 22", "url": LAW_URL, "respaldo": "sources/normativa/ley_23966_actualizada.html"},
        {"tipo": "secundaria", "titulo": "El Cronista · puente 2025", "url": CRONISTA_URL, "respaldo": "sources/descubrimiento/cronista_karina_revaluacion_2025_2026-09-02.html"},
        {"tipo": "secundaria", "titulo": "La Nación · control 2025", "url": LANACION_URL, "respaldo": "sources/descubrimiento/lanacion_milei_karina_2025_2026-09-02.html"},
    ],
}
JSON_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(
    "OK: auditoría Javier · "
    f"aumento real 2025 = {latest['aumento_bienes_real_ipc_pct']}% · "
    f"valuación = {latest['valuacion_sobre_aumento_bienes_pct']}% del aumento · "
    "residual ajustado = 0"
)
