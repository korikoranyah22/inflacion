from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

import openpyxl


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_DIR = ROOT / "tmp"
OUTPUT = ROOT / "assets" / "productive-audit-data.json"

SOURCES = {
    "ipi": {
        "file": "sh_ipi_manufacturero_2026.xls",
        "url": "https://www.indec.gob.ar/ftp/cuadros/economia/sh_ipi_manufacturero_2026.xls",
        "report": "https://www.indec.gob.ar/uploads/informesdeprensa/ipi_manufacturero_09_26B810401E77.pdf",
    },
    "isac": {
        "file": "sh_isac_2026.xls",
        "url": "https://www.indec.gob.ar/ftp/cuadros/economia/sh_isac_2026.xls",
        "report": "https://www.indec.gob.ar/uploads/informesdeprensa/isac_09_263EF0E9CDDD.pdf",
    },
    "tourism_in": {
        "file": "serie_turismo_receptivo_total_vias.xlsx",
        "url": "https://www.indec.gob.ar/ftp/cuadros/economia/serie_turismo_receptivo_total_vias.xlsx",
        "report": "https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-13-55",
    },
    "tourism_out": {
        "file": "serie_turismo_emisivo_total_vias.xlsx",
        "url": "https://www.indec.gob.ar/ftp/cuadros/economia/serie_turismo_emisivo_total_vias.xlsx",
        "report": "https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-13-55",
    },
    "trade": {
        "file": "ica_cuadros_20_08_26.xls",
        "url": "https://www.indec.gob.ar/ftp/cuadros/economia/ica_cuadros_20_08_26.xls",
        "report": "https://www.indec.gob.ar/ftp/ica_digital/ica_d_08_26E158B1D119/",
    },
}

MONTHS = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}


def normalized(value: object) -> str:
    text = str(value or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(char for char in text if not unicodedata.combining(char))


def as_number(value: object) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return round(float(value), 6)
    return None


def date_key(year: int, month_name: object) -> str | None:
    month = MONTHS.get(normalized(month_name))
    return f"{year:04d}-{month:02d}" if month else None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_xlrd():
    try:
        import xlrd  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            "Falta xlrd para leer los .xls oficiales. Instalalo con: pip install xlrd>=2.0.2"
        ) from exc
    return xlrd


def require_sources(source_dir: Path) -> dict[str, Path]:
    resolved = {key: source_dir / item["file"] for key, item in SOURCES.items()}
    missing = [key for key, path in resolved.items() if not path.is_file()]
    if missing:
        detail = "\n".join(f"- {SOURCES[key]['url']}" for key in missing)
        raise SystemExit(f"Faltan fuentes en {source_dir}:\n{detail}")
    return resolved


def parse_activity(path: Path, kind: str, xlrd) -> dict:
    sheet = xlrd.open_workbook(path).sheet_by_name("Cuadro 1")
    if kind == "industry":
        year_col, month_col, original_col, yoy_col, cum_col, sa_col, mom_col, trend_col, trend_mom_col = (
            1, 2, 3, 4, 5, 7, 8, 10, 11
        )
    else:
        year_col, month_col, original_col, yoy_col, cum_col, sa_col, mom_col, trend_col, trend_mom_col = (
            0, 1, 2, 3, 4, 6, 7, 9, 10
        )

    year: int | None = None
    rows: list[dict] = []
    for row_index in range(sheet.nrows):
        year_match = re.search(r"(20\d{2})", str(sheet.cell_value(row_index, year_col)))
        if year_match:
            year = int(year_match.group(1))
        date = date_key(year or 0, sheet.cell_value(row_index, month_col))
        sa = as_number(sheet.cell_value(row_index, sa_col))
        if not date or sa is None:
            continue
        rows.append(
            {
                "date": date,
                "original": as_number(sheet.cell_value(row_index, original_col)),
                "yoy_pct": as_number(sheet.cell_value(row_index, yoy_col)),
                "cumulative_yoy_pct": as_number(sheet.cell_value(row_index, cum_col)),
                "seasonally_adjusted": sa,
                "mom_pct": as_number(sheet.cell_value(row_index, mom_col)),
                "trend_cycle": as_number(sheet.cell_value(row_index, trend_col)),
                "trend_mom_pct": as_number(sheet.cell_value(row_index, trend_mom_col)),
            }
        )

    latest = rows[-1]
    sa_values = [row["seasonally_adjusted"] for row in rows]
    latest["percentile_in_available_series"] = round(
        100 * sum(value <= latest["seasonally_adjusted"] for value in sa_values) / len(sa_values), 1
    )
    latest["available_min"] = round(min(sa_values), 3)
    latest["available_max"] = round(max(sa_values), 3)
    return {"series": rows, "latest": latest}


def parse_tourism(path: Path) -> list[dict]:
    sheet = openpyxl.load_workbook(path, read_only=True, data_only=True).active
    year: int | None = None
    rows: list[dict] = []
    for values in sheet.iter_rows(values_only=True):
        year_match = re.search(r"(20\d{2})", str(values[0] or ""))
        if year_match:
            year = int(year_match.group(1))
        date = date_key(year or 0, values[0])
        tourists = as_number(values[10] if len(values) > 10 else None)
        tourists_yoy = as_number(values[11] if len(values) > 11 else None)
        visitors = as_number(values[1] if len(values) > 1 else None)
        if date and tourists is not None:
            rows.append(
                {
                    "date": date,
                    "visitors_thousands": visitors,
                    "tourists_thousands": tourists,
                    "tourists_yoy_pct": tourists_yoy,
                }
            )
    return rows


def find_row(sheet, text: str, column: int = 1) -> int:
    target = normalized(text)
    for row_index in range(sheet.nrows):
        if target in normalized(sheet.cell_value(row_index, column)):
            return row_index
    raise ValueError(f"No se encontró {text!r} en {sheet.name}")


def parse_trade(path: Path, xlrd) -> dict:
    workbook = xlrd.open_workbook(path)
    categories_sheet = workbook.sheet_by_name("c12")
    categories = []
    for key, label, short in (
        ("pp", "Productos primarios", "PP"),
        ("moa", "Manufacturas de origen agropecuario", "MOA"),
        ("moi", "Manufacturas de origen industrial", "MOI"),
        ("cye", "Combustibles y energía", "CyE"),
    ):
        row_index = find_row(categories_sheet, label)
        categories.append(
            {
                "id": key,
                "label": label,
                "short": short,
                "current_usd_millions": as_number(categories_sheet.cell_value(row_index, 6)),
                "previous_usd_millions": as_number(categories_sheet.cell_value(row_index, 7)),
                "value_yoy_pct": as_number(categories_sheet.cell_value(row_index, 8)),
            }
        )

    index_sheet = workbook.sheet_by_name("c4")
    moi_index = find_row(index_sheet, "Manufacturas de origen industrial")
    moi_decomposition = {
        "value_yoy_pct": as_number(index_sheet.cell_value(moi_index, 2)),
        "price_yoy_pct": as_number(index_sheet.cell_value(moi_index, 3)),
        "quantity_yoy_pct": as_number(index_sheet.cell_value(moi_index, 4)),
    }

    exports_sheet = workbook.sheet_by_name("c2")
    july_row = find_row(exports_sheet, "Julio", 1)
    exports_latest = {
        "seasonally_adjusted_mom_pct": as_number(exports_sheet.cell_value(july_row, 2)),
        "trend_mom_pct": as_number(exports_sheet.cell_value(july_row, 3)),
    }

    broad_energy_exports = next(row for row in categories if row["id"] == "cye")["current_usd_millions"]
    imports_sheet = workbook.sheet_by_name("c14")
    energy_imports_row = find_row(imports_sheet, "Combustibles y lubricantes")
    broad_energy_imports = as_number(imports_sheet.cell_value(energy_imports_row, 6))

    chapter_sheet = workbook.sheet_by_name("c8")
    chapter_balance = {
        "exports_usd_millions": as_number(chapter_sheet.cell_value(7, 6)),
        "imports_usd_millions": as_number(chapter_sheet.cell_value(14, 6)),
        "balance_usd_millions": as_number(chapter_sheet.cell_value(6, 6)),
    }
    return {
        "period": "enero-julio de 2026",
        "categories": categories,
        "moi_decomposition": moi_decomposition,
        "exports_latest": exports_latest,
        "energy": {
            "broad_classification": {
                "label": "Grandes rubros del ICA: CyE menos CyL",
                "exports_usd_millions": broad_energy_exports,
                "imports_usd_millions": broad_energy_imports,
                "balance_usd_millions": round(broad_energy_exports - broad_energy_imports, 6),
            },
            "chapter_27": {
                "label": "Capítulo 27 de la NCM",
                **chapter_balance,
            },
        },
    }


def build(source_dir: Path) -> dict:
    paths = require_sources(source_dir)
    xlrd = load_xlrd()
    industry = parse_activity(paths["ipi"], "industry", xlrd)
    construction = parse_activity(paths["isac"], "construction", xlrd)
    inbound = parse_tourism(paths["tourism_in"])
    outbound = parse_tourism(paths["tourism_out"])
    outbound_by_date = {row["date"]: row for row in outbound}
    tourism = []
    for row in inbound:
        other = outbound_by_date.get(row["date"])
        if not other:
            continue
        tourism.append(
            {
                "date": row["date"],
                "inbound_tourists_thousands": row["tourists_thousands"],
                "inbound_yoy_pct": row["tourists_yoy_pct"],
                "outbound_tourists_thousands": other["tourists_thousands"],
                "outbound_yoy_pct": other["tourists_yoy_pct"],
                "tourist_balance_thousands": round(
                    row["tourists_thousands"] - other["tourists_thousands"], 6
                ),
            }
        )

    trade = parse_trade(paths["trade"], xlrd)
    sources = [
        {
            "id": key,
            "institution": "INDEC",
            "title": {
                "ipi": "IPI manufacturero · julio de 2026",
                "isac": "ISAC · julio de 2026",
                "tourism_in": "Turismo receptivo · total de vías",
                "tourism_out": "Turismo emisivo · total de vías",
                "trade": "Intercambio comercial argentino · julio de 2026",
            }[key],
            "url": item["report"],
            "data_url": item["url"],
            "file": item["file"],
            "sha256": sha256(paths[key]),
        }
        for key, item in SOURCES.items()
    ]
    sources.extend(
        [
            {
                "id": "regional_exports",
                "institution": "Secretaría de Agricultura",
                "title": "Exportaciones de 37 producciones regionales · enero-mayo de 2026",
                "url": "https://www.argentina.gob.ar/noticias/las-exportaciones-del-conjunto-de-producciones-regionales-alcanzaron-un-record-en-valor-de",
            },
            {
                "id": "oil_july",
                "institution": "Secretaría de Energía",
                "title": "Producción de petróleo y gas · julio de 2026",
                "url": "https://www.argentina.gob.ar/noticias/la-produccion-de-petroleo-registro-otro-mes-de-crecimiento-en-julio",
            },
        ]
    )

    latest_tourism = tourism[-1]
    return {
        "version": "1.0.0",
        "updated": "2026-09-10",
        "scope": "Auditoría del comunicado oficial sobre construcción, industria, turismo, economías regionales y energía.",
        "activity": {"industry": industry, "construction": construction},
        "tourism": {"series": tourism, "latest": latest_tourism},
        "trade": trade,
        "regional_exports": {
            "period": "enero-mayo de 2026",
            "complexes": 37,
            "value_usd_millions": 4032,
            "value_yoy_pct": 13.3,
            "volume_tonnes": 3124835,
            "volume_yoy_pct": 8.5,
            "average_price_usd_per_tonne": 1290.2,
            "average_price_yoy_pct": 4.4,
            "record_value_since": 2004,
            "record_volume_since": 2013,
        },
        "oil": {
            "period": "julio de 2026",
            "barrels_per_day": 916200,
            "yoy_pct": 17.2,
            "vaca_muerta_barrels_per_day": 643100,
            "vaca_muerta_yoy_pct": 26.4,
        },
        "claims": [
            {
                "id": "construction",
                "topic": "Construcción",
                "claim": "Un primer semestre positivo descarta un derrumbe histórico.",
                "status": "partial",
                "verdict": "Recorte temporal",
                "finding": "El +2,8% acumulado a junio era correcto, pero julio ya estaba publicado: el acumulado bajó a +1,7%, mientras el mes cayó 4,5% interanual y 4,6% desestacionalizado.",
                "tests": {"phenomenon": True, "period": False, "unit": True, "inference": False},
            },
            {
                "id": "industry",
                "topic": "Industria",
                "claim": "Más exportaciones MOI prueban que la industria no está cayendo.",
                "status": "mismatch",
                "verdict": "Indicador cambiado",
                "finding": "MOI son exportaciones clasificadas por origen y medidas en dólares. El IPI mide producción fabril: en julio cayó 4,9% interanual y 5,0% mensual desestacionalizado; el acumulado cedió 2,6%.",
                "tests": {"phenomenon": False, "period": True, "unit": False, "inference": False},
            },
            {
                "id": "tourism",
                "topic": "Turismo",
                "claim": "Más turistas extranjeros prueban que el turismo no cae.",
                "status": "partial",
                "verdict": "Universo recortado",
                "finding": "En julio entraron 466,2 mil turistas no residentes (+9,1%), pero salieron 697,1 mil residentes y el saldo fue -230,9 mil. Además, turismo receptivo internacional no mide turismo interno.",
                "tests": {"phenomenon": False, "period": True, "unit": True, "inference": False},
            },
            {
                "id": "regional",
                "topic": "Economías regionales",
                "claim": "El récord exportador descarta la caída de las economías regionales.",
                "status": "partial",
                "verdict": "Alcance limitado",
                "finding": "El récord es real para una canasta oficial de 37 complejos exportadores: +13,3% en valor y +8,5% en volumen. No mide por sí solo actividad, empleo, márgenes ni todas las economías regionales.",
                "tests": {"phenomenon": False, "period": True, "unit": True, "inference": False},
            },
            {
                "id": "energy",
                "topic": "Energía",
                "claim": "Producción récord y superávit prueban que Argentina no es dependiente.",
                "status": "unsupported",
                "verdict": "Salto de conclusión",
                "finding": "La producción petrolera récord y el superávit comercial son datos confirmados. No alcanzan para demostrar independencia energética: eso exige definir autoabastecimiento, estacionalidad, productos e infraestructura.",
                "tests": {"phenomenon": True, "period": True, "unit": True, "inference": False},
            },
            {
                "id": "comparison_2013",
                "topic": "Comparación con 2013",
                "claim": "La diferencia con 2013 demuestra la responsabilidad de una gestión individual.",
                "status": "mismatch",
                "verdict": "Período y causalidad",
                "finding": "El comunicado compara el año completo 2013 con enero-julio de 2026 y atribuye el cambio a una persona. Períodos distintos no prueban magnitud comparable, y una comparación antes-después no identifica causalidad.",
                "tests": {"phenomenon": True, "period": False, "unit": True, "inference": False},
            },
        ],
        "sources": sources,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Construye el dataset del tab Chequeo productivo.")
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    payload = build(args.source_dir.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"OK: {args.output} · {len(payload['activity']['industry']['series'])} meses IPI · {len(payload['activity']['construction']['series'])} meses ISAC")


if __name__ == "__main__":
    main()
