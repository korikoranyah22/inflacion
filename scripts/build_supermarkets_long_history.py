"""Build the annual long-run supermarket real-sales view without splicing eras.

The legacy XLS is the official INDEC 1996-2013 archive (base April 2008=100).
The modern CSV is the project's audited 2017-2026 series (base average 2017=100).
Each era is normalized to 100 at its own first annual average. The break is
deliberate: INDEC states that the pre-2014 and later series cannot be spliced.
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

try:
    import xlrd
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Falta xlrd para leer el XLS histórico: python -m pip install xlrd==2.0.2"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
LEGACY_XLS = (
    ROOT
    / "data"
    / "fuentes"
    / "supermercados"
    / "indec"
    / "indec_supermercados_historico_1996_2013.xls"
)
MODERN_CSV = (
    ROOT
    / "data"
    / "derivados"
    / "supermercados"
    / "supermercados_moderno_2017_2026.csv"
)
OUTPUT_CSV = (
    ROOT
    / "data"
    / "derivados"
    / "supermercados"
    / "supermercados_historia_larga_1996_2026.csv"
)


def legacy_years() -> list[dict[str, object]]:
    sheet = xlrd.open_workbook(LEGACY_XLS).sheet_by_index(0)
    values: dict[int, list[float]] = defaultdict(list)
    current_year: int | None = None

    for row in range(6, sheet.nrows):
        period = str(sheet.cell_value(row, 0)).strip()
        match = re.search(r"\b(19|20)\d{2}\b", period)
        if match:
            current_year = int(match.group(0))
        real_index = sheet.cell_value(row, 4)
        if current_year and isinstance(real_index, (int, float)):
            values[current_year].append(float(real_index))

    base = sum(values[1996]) / len(values[1996])
    rows: list[dict[str, object]] = []
    for year in sorted(values):
        mean = sum(values[year]) / len(values[year])
        rows.append(
            {
                "era": "1996-2013",
                "year": year,
                "months": len(values[year]),
                "source_real_index_mean": mean,
                "real_index_era_base100": mean / base * 100,
                "base_definition": "promedio 1996=100",
                "status": "observado INDEC; promedio anual derivado",
            }
        )
    return rows


def modern_years() -> list[dict[str, object]]:
    values: dict[int, list[float]] = defaultdict(list)
    with MODERN_CSV.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            values[int(row["year"])].append(float(row["real_index"]))

    base = sum(values[2017]) / len(values[2017])
    rows: list[dict[str, object]] = []
    for year in sorted(values):
        mean = sum(values[year]) / len(values[year])
        rows.append(
            {
                "era": "2017-2026",
                "year": year,
                "months": len(values[year]),
                "source_real_index_mean": mean,
                "real_index_era_base100": mean / base * 100,
                "base_definition": "promedio 2017=100",
                "status": (
                    "parcial enero-junio; promedio anual derivado"
                    if year == 2026
                    else "observado/derivado identificado; promedio anual derivado"
                ),
            }
        )
    return rows


def main() -> None:
    rows = legacy_years() + modern_years()
    fieldnames = [
        "era",
        "year",
        "months",
        "source_real_index_mean",
        "real_index_era_base100",
        "base_definition",
        "status",
    ]
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            row["source_real_index_mean"] = f"{float(row['source_real_index_mean']):.6f}"
            row["real_index_era_base100"] = f"{float(row['real_index_era_base100']):.6f}"
            writer.writerow(row)

    assert len(rows) == 28
    assert [row["year"] for row in rows[:18]] == list(range(1996, 2014))
    assert [row["year"] for row in rows[18:]] == list(range(2017, 2027))
    assert all(row["months"] == 12 for row in rows[:-1])
    assert rows[-1]["months"] == 6
    print(f"wrote {OUTPUT_CSV} ({len(rows)} annual rows)")


if __name__ == "__main__":
    main()
