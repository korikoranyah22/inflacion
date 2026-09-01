from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / "sources"
sys.stdout.reconfigure(encoding="utf-8")


def compact(value: object) -> object:
    if pd.isna(value):
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def inspect_deposit_workbook() -> None:
    path = SOURCES / "bcra_cuentas_saldos_estrato.xlsm"
    workbook = pd.ExcelFile(path)
    print(json.dumps({"workbook": path.name, "sheets": workbook.sheet_names}, ensure_ascii=False))
    for sheet_name in workbook.sheet_names[1:-1]:
        frame = pd.read_excel(path, sheet_name=sheet_name, header=None)
        preview = [[compact(value) for value in row] for row in frame.iloc[:14, :12].values.tolist()]
        last_columns = [[compact(value) for value in row] for row in frame.iloc[:14, -8:].values.tolist()]
        matches: list[dict[str, object]] = []
        for row_index in range(min(30, frame.shape[0])):
            for column_index in range(frame.shape[1]):
                value = frame.iat[row_index, column_index]
                if not isinstance(value, str):
                    continue
                normalized = value.lower()
                if any(term in normalized for term in ("dollar", "individual", "legal entit", "persona", "dólar")):
                    matches.append({"row": row_index, "column": column_index, "value": value})
        dollar_headers: list[dict[str, object]] = []
        for row_index in range(min(30, frame.shape[0])):
            for column_index in range(160, frame.shape[1]):
                value = frame.iat[row_index, column_index]
                if isinstance(value, str) and value.strip():
                    dollar_headers.append({"row": row_index, "column": column_index, "value": value})
        latest_rows: list[dict[str, object]] = []
        for row_index in range(frame.shape[0]):
            if frame.iat[row_index, 0] == 2026 and frame.iat[row_index, 1] == 6:
                values = {
                    str(column_index): compact(frame.iat[row_index, column_index])
                    for column_index in range(160, frame.shape[1])
                    if not pd.isna(frame.iat[row_index, column_index])
                }
                latest_rows.append({"row": row_index, "values": values})
        print(
            json.dumps(
                {
                    "sheet": sheet_name,
                    "shape": list(frame.shape),
                    "preview": preview,
                    "last_columns": last_columns,
                    "header_matches": matches,
                    "dollar_headers": dollar_headers,
                    "latest_rows": latest_rows,
                },
                ensure_ascii=False,
                default=str,
            )
        )


def inspect_deposit_tail() -> None:
    path = SOURCES / "bcra_cuentas_saldos_estrato.xlsm"
    sheets = ("Aho.cant.$ y u$s", "Pla.cant.$ y u$s", "Aho.sal.$ y u$s", "Pla.sal.$ y u$s")
    for sheet_name in sheets:
        frame = pd.read_excel(path, sheet_name=sheet_name, header=None)
        rows = []
        for row_index in range(max(0, frame.shape[0] - 30), frame.shape[0]):
            values = [compact(value) for value in frame.iloc[row_index, :5].tolist()]
            if any(value is not None for value in values):
                rows.append({"row": row_index, "values": values})
        print(json.dumps({"sheet": sheet_name, "tail": rows}, ensure_ascii=False, default=str))


def inspect_deposit_slice() -> None:
    path = SOURCES / "bcra_cuentas_saldos_estrato.xlsm"
    sheets = ("Aho.cant.$ y u$s", "Pla.cant.$ y u$s", "Aho.sal.$ y u$s", "Pla.sal.$ y u$s")
    for sheet_name in sheets:
        frame = pd.read_excel(path, sheet_name=sheet_name, header=None)
        populated = []
        for column_index in range(220, min(310, frame.shape[1])):
            headers = []
            for row_index in range(0, 26):
                value = compact(frame.iat[row_index, column_index])
                if value not in (None, ""):
                    headers.append({"row": row_index, "value": value})
            latest = compact(frame.iat[502, column_index])
            if headers or latest is not None:
                populated.append({"column": column_index, "headers": headers, "latest": latest})
        print(json.dumps({"sheet": sheet_name, "slice": populated}, ensure_ascii=False, default=str))


def calculate_deposit_concentration() -> None:
    path = SOURCES / "bcra_cuentas_saldos_estrato.xlsm"
    row_index = 502  # Junio de 2026, último trimestre disponible en el archivo al 31/08/2026.
    definitions = {
        "cajas_ahorro": {
            "count_sheet": "Aho.cant.$ y u$s",
            "count_start": 243,
            "balance_sheet": "Aho.sal.$ y u$s",
            "balance_start": 255,
        },
        "plazos_fijos": {
            "count_sheet": "Pla.cant.$ y u$s",
            "count_start": 243,
            "balance_sheet": "Pla.sal.$ y u$s",
            "balance_start": 263,
        },
    }
    results: dict[str, object] = {}
    combined = {"accounts_total": 0.0, "accounts_ge_10k": 0.0, "accounts_ge_100k": 0.0, "balance_total_reported": 0.0, "balance_ge_10k_reported": 0.0, "balance_ge_100k_reported": 0.0}
    for key, definition in definitions.items():
        counts = pd.read_excel(path, sheet_name=definition["count_sheet"], header=None)
        balances = pd.read_excel(path, sheet_name=definition["balance_sheet"], header=None)
        count_values = [float(counts.iat[row_index, definition["count_start"] + offset]) for offset in range(16)]
        balance_values = [float(balances.iat[row_index, definition["balance_start"] + offset]) for offset in range(16)]
        item = {
            "accounts_total": count_values[0],
            "accounts_bucket_sum": sum(count_values[1:]),
            "accounts_ge_10k": sum(count_values[5:]),
            "accounts_ge_100k": sum(count_values[11:]),
            "balance_total_reported": balance_values[0],
            "balance_bucket_sum_reported": sum(balance_values[1:]),
            "balance_ge_10k_reported": sum(balance_values[5:]),
            "balance_ge_100k_reported": sum(balance_values[11:]),
        }
        item["accounts_ge_10k_pct"] = 100 * item["accounts_ge_10k"] / item["accounts_total"]
        item["accounts_ge_100k_pct"] = 100 * item["accounts_ge_100k"] / item["accounts_total"]
        item["balance_ge_10k_pct"] = 100 * item["balance_ge_10k_reported"] / item["balance_total_reported"]
        item["balance_ge_100k_pct"] = 100 * item["balance_ge_100k_reported"] / item["balance_total_reported"]
        results[key] = item
        for combined_key in combined:
            combined[combined_key] += item[combined_key]
    combined["accounts_ge_10k_pct"] = 100 * combined["accounts_ge_10k"] / combined["accounts_total"]
    combined["accounts_ge_100k_pct"] = 100 * combined["accounts_ge_100k"] / combined["accounts_total"]
    combined["balance_ge_10k_pct"] = 100 * combined["balance_ge_10k_reported"] / combined["balance_total_reported"]
    combined["balance_ge_100k_pct"] = 100 * combined["balance_ge_100k_reported"] / combined["balance_total_reported"]
    results["combined_instruments"] = combined
    print(json.dumps({"period": "2026-06", "population": "resident private-sector individual accounts", "currency": "foreign-currency deposit strata; balances are peso-valued in the workbook, so only dimensionless balance shares are used", "results": results}, ensure_ascii=False, indent=2))


def calculate_deposit_concentration_history() -> None:
    path = SOURCES / "bcra_cuentas_saldos_estrato.xlsm"
    definitions = {
        "savings_accounts": ("Aho.cant.$ y u$s", 243, "Aho.sal.$ y u$s", 255),
        "time_deposits": ("Pla.cant.$ y u$s", 243, "Pla.sal.$ y u$s", 263),
    }
    frames = {
        sheet_name: pd.read_excel(path, sheet_name=sheet_name, header=None)
        for definition in definitions.values()
        for sheet_name in (definition[0], definition[2])
    }
    period_rows: list[tuple[str, int]] = []
    reference = frames["Aho.cant.$ y u$s"]
    for row_index in range(reference.shape[0]):
        value = reference.iat[row_index, 0]
        if not isinstance(value, (int, float)) or not (2023.12 <= float(value) <= 2026.06):
            continue
        month_label = str(reference.iat[row_index, 1]).strip().lower()
        if month_label not in {"mar.", "jun.", "set.", "dic."}:
            continue
        year = int(float(value))
        month = {"mar.": 3, "jun.": 6, "set.": 9, "dic.": 12}[month_label]
        period_rows.append((f"{year:04d}-{month:02d}", row_index))

    results: list[dict[str, object]] = []
    for period, row_index in period_rows:
        combined = {
            "accounts_total": 0.0,
            "accounts_ge_10k": 0.0,
            "accounts_ge_100k": 0.0,
            "balance_total": 0.0,
            "balance_ge_10k": 0.0,
            "balance_ge_100k": 0.0,
        }
        instruments: dict[str, dict[str, float]] = {}
        for instrument, (count_sheet, count_start, balance_sheet, balance_start) in definitions.items():
            count_values = [float(frames[count_sheet].iat[row_index, count_start + offset]) for offset in range(16)]
            balance_values = [float(frames[balance_sheet].iat[row_index, balance_start + offset]) for offset in range(16)]
            item = {
                "accounts_total": count_values[0],
                "accounts_ge_10k": sum(count_values[5:]),
                "accounts_ge_100k": sum(count_values[11:]),
                "balance_total": balance_values[0],
                "balance_ge_10k": sum(balance_values[5:]),
                "balance_ge_100k": sum(balance_values[11:]),
            }
            item["accounts_ge_10k_pct"] = 100 * item["accounts_ge_10k"] / item["accounts_total"]
            item["accounts_ge_100k_pct"] = 100 * item["accounts_ge_100k"] / item["accounts_total"]
            item["balance_ge_10k_pct"] = 100 * item["balance_ge_10k"] / item["balance_total"]
            item["balance_ge_100k_pct"] = 100 * item["balance_ge_100k"] / item["balance_total"]
            instruments[instrument] = item
            for key in combined:
                combined[key] += item[key]
        combined["accounts_ge_10k_pct"] = 100 * combined["accounts_ge_10k"] / combined["accounts_total"]
        combined["accounts_ge_100k_pct"] = 100 * combined["accounts_ge_100k"] / combined["accounts_total"]
        combined["balance_ge_10k_pct"] = 100 * combined["balance_ge_10k"] / combined["balance_total"]
        combined["balance_ge_100k_pct"] = 100 * combined["balance_ge_100k"] / combined["balance_total"]
        results.append({"period": period, "combined_account_instruments": combined, "instruments": instruments})
    print(json.dumps({"population": "resident private-sector individual accounts", "results": results}, ensure_ascii=False, indent=2))


def analyze_usd_credit_lines_and_rates() -> None:
    files = {
        "total": ("bcra_api_usd_private_loans_total_1355.json", "Total private-sector USD loans"),
        "other_advances": ("bcra_api_usd_private_loans_other_advances_1358.json", "Other advances"),
        "notes": ("bcra_api_usd_private_loans_notes_1359.json", "Single-name notes"),
        "mortgages": ("bcra_api_usd_private_loans_mortgages_1362.json", "Mortgages"),
        "pledged": ("bcra_api_usd_private_loans_pledged_1363.json", "Pledged loans"),
        "cards": ("bcra_api_usd_private_loans_cards_1365.json", "Credit cards"),
        "other": ("bcra_api_usd_private_loans_other_1367.json", "Other loans"),
    }

    def observations(filename: str) -> dict[str, float]:
        payload = json.loads((SOURCES / filename).read_text(encoding="utf-8"))
        return {row["fecha"]: float(row["valor"]) for row in payload["results"][0]["detalle"]}

    series = {key: observations(filename) for key, (filename, _) in files.items()}
    snapshots = {"2023-12-29": {}, "2026-08-27": {}}
    for date in snapshots:
        total = series["total"][date]
        disclosed_sum = 0.0
        for key, (_, label) in files.items():
            if key == "total":
                continue
            value = series[key][date]
            disclosed_sum += value
            snapshots[date][key] = {"label": label, "value_usd_millions": value, "share_of_total_pct": 100 * value / total}
        snapshots[date]["residual"] = {
            "label": "Other disclosed lines not downloaded separately",
            "value_usd_millions": total - disclosed_sum,
            "share_of_total_pct": 100 * (total - disclosed_sum) / total,
        }
        snapshots[date]["total"] = total

    total_change = snapshots["2026-08-27"]["total"] - snapshots["2023-12-29"]["total"]
    contributions = []
    for key in (*[key for key in files if key != "total"], "residual"):
        start = snapshots["2023-12-29"][key]["value_usd_millions"]
        end = snapshots["2026-08-27"][key]["value_usd_millions"]
        contributions.append(
            {
                "line": snapshots["2026-08-27"][key]["label"],
                "start_usd_millions": start,
                "end_usd_millions": end,
                "change_usd_millions": end - start,
                "contribution_to_total_change_pct": 100 * (end - start) / total_change,
            }
        )

    rates_path = SOURCES / "bcra_informe_monetario_indicadores_julio_2026.xlsx"
    rates = pd.read_excel(rates_path, sheet_name="Tasas", header=None)
    assert "Dep" in str(rates.iat[31, 0]) and "d" in str(rates.iat[31, 0])
    assert "Documentos" in str(rates.iat[32, 0])
    periods = {"2025-07": 6, "2025-12": 5, "2026-05": 4, "2026-06": 3, "2026-07": 1}
    rate_history = []
    for period, column in periods.items():
        deposit_rate = float(rates.iat[31, column])
        loan_rate = float(rates.iat[32, column])
        rate_history.append(
            {
                "period": period,
                "usd_time_deposit_30_44d_tna_pct": deposit_rate,
                "usd_single_name_notes_tna_pct": loan_rate,
                "gross_rate_gap_pp": loan_rate - deposit_rate,
            }
        )
    july_deposit = rate_history[-1]["usd_time_deposit_30_44d_tna_pct"]
    july_loan = rate_history[-1]["usd_single_name_notes_tna_pct"]
    utilization_scenarios = [
        {
            "loanable_share_pct": share,
            "illustrative_gross_carry_per_deposit_pp": july_loan * share / 100 - july_deposit,
        }
        for share in (61, 65, 75)
    ]
    print(
        json.dumps(
            {
                "snapshots": snapshots,
                "total_change_usd_millions": total_change,
                "contributions": contributions,
                "rate_history": rate_history,
                "utilization_scenarios": utilization_scenarios,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def inspect_text_series() -> None:
    for filename in ("bcra_cuentas_saldos_estrato_vol5.txt", "bcra_prestamos_actividad_provincia_vol3.txt"):
        path = SOURCES / filename
        latest: dict[str, tuple[str, str]] = {}
        counts: dict[str, int] = {}
        with path.open(encoding="latin-1") as handle:
            for line in handle:
                fields = line.rstrip("\r\n").split(";")
                if len(fields) != 3:
                    continue
                series_id, date, value = fields
                latest[series_id] = (date, value)
                counts[series_id] = counts.get(series_id, 0) + 1
        sample = [
            {"series_id": series_id, "observations": counts[series_id], "latest_date": latest[series_id][0], "latest_value": latest[series_id][1]}
            for series_id in sorted(latest, key=int)[:20]
        ]
        print(json.dumps({"file": filename, "series_count": len(latest), "sample": sample}, ensure_ascii=False))


if __name__ == "__main__":
    if "--tail" in sys.argv:
        inspect_deposit_tail()
    elif "--slice" in sys.argv:
        inspect_deposit_slice()
    elif "--concentration" in sys.argv:
        calculate_deposit_concentration()
    elif "--history" in sys.argv:
        calculate_deposit_concentration_history()
    elif "--credit" in sys.argv:
        analyze_usd_credit_lines_and_rates()
    else:
        inspect_deposit_workbook()
        inspect_text_series()
