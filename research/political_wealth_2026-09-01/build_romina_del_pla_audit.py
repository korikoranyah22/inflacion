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
HCDN_2024_PATH = ROOT / "sources" / "active_roster" / "hcdn_ddjj_ejercicio_2024_2026-09-03.html"
DATASET_URL = "https://datos.jus.gob.ar/dataset/declaraciones-juradas-patrimoniales-integrales"
HCDN_2024_URL = "https://www.hcdn.gob.ar/institucional/transparencia/declaraciones_juradas/listado/4407dd25-ea1a-11ef-b33c-00505689ffd4"
PERSON_ID = "dip-del-pla-romina"
PERSON = "Romina Del Plá"
DJ_IDS = {2023: "700411", 2024: "820747"}


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
assert HCDN_2024_PATH.is_file(), "Falta la copia local de la nómina HCDN 2024"
hcdn_text = HCDN_2024_PATH.read_text(encoding="utf-8", errors="replace")
assert "DEL PLA" in hcdn_text and "BAJA 2024" in hcdn_text

summaries: dict[int, dict[str, str]] = {}
assets: dict[int, list[dict[str, str]]] = {}
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
        assert assets[year], f"Sin detalle de bienes {year}"


def asset_sum(year: int, period: str, asset_type: str | None = None) -> Decimal:
    selected = [row for row in assets[year] if row["periodo_inicio_cierre"] == period]
    if asset_type:
        selected = [row for row in selected if asset_type in row["bien_tipo"].upper()]
    return sum((decimal(row["bien_importe"]) for row in selected), Decimal("0"))


controls: list[dict[str, object]] = []
for year in (2023, 2024):
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

close_2023 = asset_sum(2023, "C")
open_2024 = asset_sum(2024, "I")
controls.append(
    {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "anio": 2024,
        "control": "cierre_detalle_2023_vs_inicio_detalle_2024",
        "valor_resumen_ars": rounded(close_2023),
        "valor_control_ars": rounded(open_2024),
        "brecha_ars": rounded(open_2024 - close_2023),
        "ratio_resumen_sobre_detalle": rounded(open_2024 / close_2023),
        "resultado": "no_arrastra_cierre_previo",
        "dj_id": DJ_IDS[2024],
        "fuente_url": DATASET_URL,
    }
)

csv_path = DERIVED / "romina_del_pla_source_consistency_audit_2023_2024.csv"
with csv_path.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=controls[0].keys())
    writer.writeheader()
    writer.writerows(controls)

summary_close_2024 = decimal(summaries[2024]["total_bienes_final"])
raw_increase = summary_close_2024 - close_2023
raw_increase_pct = raw_increase / close_2023 * 100
property_close_2023 = asset_sum(2023, "C", "INMUEBLES")
property_close_2024 = asset_sum(2024, "C", "INMUEBLES")
property_increase = property_close_2024 - property_close_2023

with (DERIVED / "macro_deflators_2017_2025.csv").open(encoding="utf-8", newline="") as handle:
    macro = {int(row["anio"]): row for row in csv.DictReader(handle)}
ipc_factor = decimal(macro[2024]["ipc_indice_dic_2016_100"]) / decimal(macro[2023]["ipc_indice_dic_2016_100"])
ipc_pct = (ipc_factor - 1) * 100
property_ipc_value = property_close_2023 * ipc_factor
property_ipc_increase = property_ipc_value - property_close_2023

audit = {
    "metadata": {
        "persona_id": PERSON_ID,
        "persona": PERSON,
        "corte": "2026-09-03",
        "pregunta": "¿El salto 2024 refleja una variación patrimonial comparable o una inconsistencia entre capas de la fuente?",
        "alcance": "El control compara el resumen y las filas de bienes del mismo consolidado oficial OA, y contrasta el tipo de presentación con la nómina oficial de Diputados.",
        "etiqueta": "serie suspendida · inconsistencia de fuente",
        "serie_estado": "suspendida_hasta_conciliar_resumen_y_detalle",
        "benchmark_estado": "suspendido_por_inconsistencia_fuente",
    },
    "periodos": [
        {
            "persona_id": PERSON_ID,
            "persona": PERSON,
            "periodo": "2023-2024",
            "estado_fuente": "oficial_consolidado_oa_inconsistente",
            "bienes_inicio_ars": rounded(close_2023),
            "bienes_cierre_ars": rounded(summary_close_2024),
            "aumento_bienes_ars": rounded(raw_increase),
            "aumento_bienes_pct": rounded(raw_increase_pct),
            "diferencia_valuacion_total_ars": rounded(decimal(summaries[2024]["diferencia_valuacion"])),
            "valuacion_sobre_aumento_bienes_pct": 0.0,
            "inmueble_inicio_ars": rounded(property_close_2023),
            "inmueble_cierre_ars": rounded(property_close_2024),
            "aumento_inmueble_ars": rounded(property_increase),
            "aumento_inmueble_pct": percent(property_increase, property_close_2023),
            "ipc_periodo_pct": rounded(ipc_pct),
            "inmueble_si_solo_ipc_ars": rounded(property_ipc_value),
            "aumento_inmueble_explicado_por_ipc_simple_pct": percent(property_ipc_increase, property_increase),
            "brecha_inmueble_vs_ipc_simple_ars": rounded(property_close_2024 - property_ipc_value),
            "lectura": "El salto de la serie usa el resumen bruto, pero ese resumen es 10 veces la suma de sus propios bienes detallados. No es una tasa interpretable hasta conciliar ambas capas.",
            "fuente_url": DATASET_URL,
        }
    ],
    "controles": {
        "detalle_inicio_2024_ars": rounded(open_2024),
        "resumen_inicio_2024_ars": rounded(decimal(summaries[2024]["total_bienes_inicio"])),
        "detalle_cierre_2024_ars": rounded(asset_sum(2024, "C")),
        "resumen_cierre_2024_ars": rounded(summary_close_2024),
        "factor_resumen_sobre_detalle_2024": 10.0,
        "brecha_cierre_2023_inicio_2024_detalle_ars": rounded(open_2024 - close_2023),
        "tipo_presentacion_oa": summaries[2024]["tipo_declaracion_jurada_descripcion"],
        "tipo_presentacion_hcdn": "Baja 2024",
    },
    "composition": [
        {
            "persona_id": PERSON_ID,
            "persona": PERSON,
            "anio": 2024,
            "categoria": "Inmuebles",
            "importe_ars": str(property_close_2024),
            "dj_id": DJ_IDS[2024],
            "metodo": "Suma de bienes de cierre del detalle oficial; no reemplaza el total resumen inconsistente.",
            "fuente_url": DATASET_URL,
        },
        {
            "persona_id": PERSON_ID,
            "persona": PERSON,
            "anio": 2024,
            "categoria": "Vehículos",
            "importe_ars": str(asset_sum(2024, "C", "AUTOMOTORES")),
            "dj_id": DJ_IDS[2024],
            "metodo": "Suma de bienes de cierre del detalle oficial; no reemplaza el total resumen inconsistente.",
            "fuente_url": DATASET_URL,
        },
    ],
    "lectura_epistemica": {
        "documentado": [
            "En 2023, los totales de inicio y cierre del resumen concilian con la suma del detalle.",
            "En 2024, el resumen informa $288,10 M al inicio y $599,62 M al cierre; el detalle suma $28,81 M y $59,962 M: una diferencia exacta de factor 10 en ambos extremos.",
            "El detalle 2024 contiene el mismo departamento de Morón y el mismo automóvil adquiridos en 2016; Diputados registra una presentación Baja 2024, mientras el consolidado OA etiqueta la fila como Anual.",
        ],
        "compatible_pero_no_probado": [
            "Un corrimiento decimal en la exportación del resumen o una capa de agregación defectuosa podría producir el factor 10 sin que exista un salto económico de esa magnitud.",
            "La diferencia entre cierre 2023 e inicio 2024 puede contener actualización de valuaciones, pero la fuente no la identifica como tal y tampoco arrastra el cierre previo.",
        ],
        "no_documentado": [
            "No está respaldado el formulario individual asociado al dj_id 820747 para decidir cuál capa reproduce lo efectivamente presentado.",
            "No hay una aclaración pública de OA que explique el factor 10 ni la diferencia de tipo de presentación entre OA y Diputados.",
        ],
        "conclusion": "El aumento bruto de 2024 no debe presentarse como enriquecimiento ni como rendimiento: nace de una capa resumen que no concilia con el detalle del mismo archivo. Tampoco corresponde atribuir el error a la persona. La lectura responsable es suspender la tasa y conservar ambos valores hasta obtener el formulario individual o una corrección oficial.",
        "evidencia_para_cerrar": [
            "Formulario público individual OA correspondiente al dj_id 820747 y sus eventuales rectificativas.",
            "Confirmación de OA sobre cuál total —resumen o suma del detalle— representa la presentación original.",
            "Conciliación entre la etiqueta Anual del consolidado y la presentación Baja 2024 publicada por Diputados.",
            "Datos completos 2025 para verificar qué importe reaparece como saldo inicial.",
        ],
    },
    "reconciliation_suspended": {
        "periodo": "2024",
        "lectura": "Resumen y detalle difieren por factor 10; cualquier residual hereda esa inconsistencia y queda suspendido.",
    },
    "alerta_fuente": "En 2024, los totales de inicio y cierre del resumen son exactamente 10 veces las sumas del detalle. Además, el tipo de presentación difiere entre el consolidado OA (Anual) y Diputados (Baja). Se preserva el dato crudo, pero se suspenden la tasa y el benchmark.",
    "fuentes": [
        {
            "tipo": "primaria",
            "titulo": "Consolidado OA 2012–2024",
            "url": DATASET_URL,
            "respaldo": "sources/datos_justicia/declaraciones-juradas-2012-2024.zip",
        },
        {
            "tipo": "primaria",
            "titulo": "Diputados · presentaciones ejercicio 2024",
            "url": HCDN_2024_URL,
            "respaldo": "sources/active_roster/hcdn_ddjj_ejercicio_2024_2026-09-03.html",
        },
    ],
}

json_path = DERIVED / "romina_del_pla_patrimonial_audit_2023_2024.json"
json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

assert controls[2]["ratio_resumen_sobre_detalle"] == 10.0
assert controls[3]["ratio_resumen_sobre_detalle"] == 10.0
assert audit["controles"]["tipo_presentacion_oa"] == "Anual"
print(f"OK: auditoría Romina Del Plá · {len(controls)} controles de consistencia")
