from __future__ import annotations

import csv
import io
import json
import zipfile
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DERIVED = ROOT / "derived"
ZIP_PATH = ROOT / "sources" / "datos_justicia" / "declaraciones-juradas-2012-2024.zip"
SERIES_PATH = DERIVED / "active_politician_oa_candidate_series_2017_2024.csv"
DATASET_URL = "https://datos.jus.gob.ar/dataset/declaraciones-juradas-patrimoniales-integrales"
YEARS = (2022, 2023, 2024)


def decimal(value: str | None) -> Decimal:
    return Decimal(value or "0")


def rounded(value: Decimal, digits: str = "0.01") -> float:
    return float(value.quantize(Decimal(digits), rounding=ROUND_HALF_UP))


def clean(row: dict[str, str]) -> dict[str, str]:
    return {str(key).strip(): value for key, value in row.items()}


def ratio_status(summary: Decimal, detail: Decimal, rows_found: int) -> tuple[Decimal | None, str]:
    if detail == 0:
        if summary == 0:
            return None, "concilia_cero"
        return None, "detalle_ausente" if rows_found == 0 else "detalle_cero_resumen_positivo"
    ratio = summary / detail
    if abs(ratio - Decimal("1")) <= Decimal("0.0001"):
        return ratio, "concilia"
    for factor, label in (
        (Decimal("10"), "resumen_10x_detalle"),
        (Decimal("100"), "resumen_100x_detalle"),
        (Decimal("0.1"), "resumen_0_1x_detalle"),
        (Decimal("0.01"), "resumen_0_01x_detalle"),
    ):
        if abs(ratio - factor) <= Decimal("0.0001"):
            return ratio, label
    return ratio, "no_concilia_otro"


assert ZIP_PATH.is_file(), "Falta el ZIP oficial OA 2012–2024"
with SERIES_PATH.open(encoding="utf-8", newline="") as handle:
    candidates = [
        row
        for row in csv.DictReader(handle)
        if row["publicable_en_tab"].startswith("sí")
        and row["dj_id"]
        and int(row["anio"]) in YEARS
    ]

targets: dict[int, dict[str, dict[str, str]]] = defaultdict(dict)
for row in candidates:
    year = int(row["anio"])
    assert year in YEARS
    assert row["dj_id"] not in targets[year], f"dj_id duplicado en {year}: {row['dj_id']}"
    targets[year][row["dj_id"]] = row

summaries: dict[tuple[int, str], dict[str, str]] = {}
asset_sums: dict[tuple[int, str, str], Decimal] = defaultdict(Decimal)
asset_counts: Counter[tuple[int, str, str]] = Counter()
debt_sums: dict[tuple[int, str, str], Decimal] = defaultdict(Decimal)
debt_counts: Counter[tuple[int, str, str]] = Counter()

with zipfile.ZipFile(ZIP_PATH) as archive:
    for year in YEARS:
        year_targets = targets[year]
        with archive.open(f"declaraciones-juradas-{year}-consolidado-al-20251222.csv") as binary:
            with io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as text:
                for raw in csv.DictReader(text, skipinitialspace=True):
                    dj_id = raw.get("dj_id", "")
                    if dj_id in year_targets:
                        summaries[(year, dj_id)] = clean(raw)
        with archive.open(f"declaraciones-juradas-bienes-{year}-consolidado-al-20251222.csv") as binary:
            with io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as text:
                for raw in csv.DictReader(text, skipinitialspace=True):
                    dj_id = raw.get("dj_id", "")
                    if dj_id not in year_targets:
                        continue
                    row = clean(raw)
                    period = row["periodo_inicio_cierre"]
                    key = (year, dj_id, period)
                    asset_sums[key] += decimal(row["bien_importe"])
                    asset_counts[key] += 1
        with archive.open(f"declaraciones-juradas-deudas-{year}-consolidado-al-20251222.csv") as binary:
            with io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as text:
                for raw in csv.DictReader(text, skipinitialspace=True):
                    dj_id = raw.get("dj_id", "")
                    if dj_id not in year_targets:
                        continue
                    row = clean(raw)
                    period = row["periodo_inicio_cierre"]
                    key = (year, dj_id, period)
                    debt_sums[key] += decimal(row["deuda_importe"])
                    debt_counts[key] += 1

output: list[dict[str, object]] = []
for candidate in candidates:
    year = int(candidate["anio"])
    dj_id = candidate["dj_id"]
    summary = summaries[(year, dj_id)]
    period = "I" if summary["tipo_declaracion_jurada_descripcion"] == "Inicial" else "C"
    asset_field = "total_bienes_inicio" if period == "I" else "total_bienes_final"
    debt_field = "deudas_inicio" if period == "I" else "total_deudas_final"
    asset_summary = decimal(summary[asset_field])
    asset_detail = asset_sums[(year, dj_id, period)]
    debt_summary = decimal(summary[debt_field])
    debt_detail = debt_sums[(year, dj_id, period)]
    asset_ratio, asset_status = ratio_status(
        asset_summary,
        asset_detail,
        asset_counts[(year, dj_id, period)],
    )
    debt_ratio, debt_status = ratio_status(
        debt_summary,
        debt_detail,
        debt_counts[(year, dj_id, period)],
    )
    statuses = (asset_status, debt_status)
    if any("10x_detalle" in status or "100x_detalle" in status or "0_1x_detalle" in status or "0_01x_detalle" in status for status in statuses):
        source_quality = "quiebre_escala_decimal"
    elif any(status in {"detalle_ausente", "detalle_cero_resumen_positivo"} for status in statuses):
        source_quality = "detalle_ausente_o_cero"
    elif any(status == "no_concilia_otro" for status in statuses):
        source_quality = "inconsistencia_otro"
    else:
        source_quality = "concilia"
    output.append(
        {
            "persona_id": candidate["persona_id"],
            "persona": candidate["persona"],
            "anio": year,
            "tipo_ddjj": summary["tipo_declaracion_jurada_descripcion"],
            "rectificativa": summary["rectificativa"],
            "dj_id": dj_id,
            "periodo_controlado": "inicio" if period == "I" else "cierre",
            "bienes_resumen_ars": rounded(asset_summary),
            "bienes_detalle_ars": rounded(asset_detail),
            "bienes_ratio_resumen_detalle": rounded(asset_ratio) if asset_ratio is not None else "",
            "bienes_estado": asset_status,
            "deudas_resumen_ars": rounded(debt_summary),
            "deudas_detalle_ars": rounded(debt_detail),
            "deudas_ratio_resumen_detalle": rounded(debt_ratio) if debt_ratio is not None else "",
            "deudas_estado": debt_status,
            "calidad_fuente": source_quality,
            "fuente_url": DATASET_URL,
        }
    )

csv_path = DERIVED / "active_series_source_consistency_audit_2022_2024.csv"
with csv_path.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=output[0].keys())
    writer.writeheader()
    writer.writerows(output)

quality_counts = Counter(str(row["calidad_fuente"]) for row in output)
issue_rows = [row for row in output if row["calidad_fuente"] != "concilia"]
issue_people = sorted({str(row["persona_id"]) for row in issue_rows})
decimal_people = sorted(
    {str(row["persona_id"]) for row in output if row["calidad_fuente"] == "quiebre_escala_decimal"}
)
asset_issue_rows = [
    row for row in output if row["bienes_estado"] not in {"concilia", "concilia_cero"}
]
debt_issue_rows = [
    row for row in output if row["deudas_estado"] not in {"concilia", "concilia_cero"}
]
by_year = {}
for year in YEARS:
    rows_year = [row for row in output if row["anio"] == year]
    by_year[str(year)] = {
        "declaraciones": len(rows_year),
        "concilian": sum(row["calidad_fuente"] == "concilia" for row in rows_year),
        "con_observacion": sum(row["calidad_fuente"] != "concilia" for row in rows_year),
        "quiebre_escala_decimal": sum(row["calidad_fuente"] == "quiebre_escala_decimal" for row in rows_year),
    }

summary_payload = {
    "metadata": {
        "corte": "2026-09-03",
        "universo": "Declaraciones 2022–2024 de las trayectorias activas publicables con cruce de identidad auditado; son los años para los que el paquete oficial incluye detalle de bienes y deudas.",
        "metodo": "Para la declaración elegida por persona-año se compara el total de bienes y deudas del resumen con la suma de sus filas de detalle en el mismo período (inicio para Inicial; cierre para Anual/Baja).",
        "fuente_url": DATASET_URL,
        "respaldo": "sources/datos_justicia/declaraciones-juradas-2012-2024.zip",
    },
    "resumen": {
        "declaraciones_controladas": len(output),
        "personas_controladas": len({row["persona_id"] for row in output}),
        "declaraciones_que_concilian": quality_counts["concilia"],
        "declaraciones_con_observacion": len(issue_rows),
        "personas_con_observacion": len(issue_people),
        "declaraciones_con_quiebre_escala_decimal": quality_counts["quiebre_escala_decimal"],
        "personas_con_quiebre_escala_decimal": len(decimal_people),
        "declaraciones_con_detalle_ausente_o_cero": quality_counts["detalle_ausente_o_cero"],
        "declaraciones_con_otra_inconsistencia": quality_counts["inconsistencia_otro"],
        "declaraciones_bienes_con_quiebre_escala": len(asset_issue_rows),
        "personas_bienes_con_quiebre_escala": len({row["persona_id"] for row in asset_issue_rows}),
        "declaraciones_deudas_con_observacion": len(debt_issue_rows),
        "personas_deudas_con_observacion": len({row["persona_id"] for row in debt_issue_rows}),
        "declaraciones_deudas_sin_detalle_con_total_positivo": sum(row["deudas_estado"] == "detalle_ausente" for row in output),
    },
    "por_anio": by_year,
    "filas": output,
    "lectura": "Una observación de consistencia describe el archivo, no a la persona. Un factor decimal suspende tasas y benchmarks que usen ese total; una falta de detalle impide verificar el resumen, pero no demuestra que sea falso.",
}
json_path = DERIVED / "active_series_source_consistency_summary_2022_2024.json"
json_path.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

assert len(output) == len(candidates) == 545
assert len({row["persona_id"] for row in output}) == 248
assert any(row["persona_id"] == "dip-estevez-gabriela-beatriz" and row["anio"] == 2023 and row["calidad_fuente"] == "quiebre_escala_decimal" for row in output)
assert any(row["persona_id"] == "sen-gadano-natalia-elena" and row["anio"] == 2024 and row["calidad_fuente"] == "quiebre_escala_decimal" for row in output)
print(
    "OK: consistencia global · "
    f"{len(output)} declaraciones · {len(issue_people)} personas con observación · "
    f"{len(decimal_people)} con quiebre decimal"
)
