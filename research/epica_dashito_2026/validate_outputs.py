from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MATRIX = ROOT / "execution_matrix.csv"
CLAIMS = ROOT / "claims_registry.csv"
EXPECTED_IDS = set(range(1, 41))
EXPECTED_CLAIM_IDS = set(range(1, 28))
VALID_BASELINE = {"gap", "out_of_core", "partial", "scenario_ready", "strong_partial"}
EXPECTED_FRONTS = {"hogares_credito", "dolares_externo", "fiscal_desarrollo"}


def fail(message: str) -> None:
    print(f"ERROR: {message}")


def validate_matrix() -> list[str]:
    errors: list[str] = []
    with MATRIX.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    ids = [int(row["id"]) for row in rows]
    if set(ids) != EXPECTED_IDS or len(ids) != 40:
        errors.append("execution_matrix.csv debe contener exactamente los ids 1..40")
    for row in rows:
        if row["baseline_status"] not in VALID_BASELINE:
            errors.append(
                f"estado inicial inválido en id {row['id']}: {row['baseline_status']}"
            )
        if not row["current_tabs"]:
            errors.append(f"id {row['id']} sin tab existente o marcador explícito")
        if not row["decision_gate"]:
            errors.append(f"id {row['id']} sin gate de decisión")
    return errors


def validate_fronts() -> list[str]:
    errors: list[str] = []
    existing = {path.name for path in ROOT.iterdir() if path.is_dir()}
    for front in sorted(EXPECTED_FRONTS - existing):
        errors.append(f"falta el frente {front}")
    for front in sorted(EXPECTED_FRONTS & existing):
        files = [path for path in (ROOT / front).rglob("*") if path.is_file()]
        if not any(path.suffix.lower() == ".md" for path in files):
            errors.append(f"{front} no contiene informe Markdown")
        if not any(path.suffix.lower() == ".csv" for path in files):
            errors.append(f"{front} no contiene matriz o derivado CSV")
    return errors


def read_json(relative: str) -> dict:
    with (ROOT / relative).open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_qa() -> list[str]:
    errors: list[str] = []
    if not (ROOT / "MASTER_RESULTS.md").is_file():
        errors.append("falta MASTER_RESULTS.md")

    dollars = read_json("dolares_externo/qa_results.json")
    if dollars.get("all_tests_pass") is not True:
        errors.append("QA de dolares_externo no está en PASS")
    if len(dollars.get("tests", [])) != 6:
        errors.append("QA de dolares_externo debe contener 6 controles")

    fiscal = read_json("fiscal_desarrollo/qa_resultados.json")
    if fiscal.get("pass") is not True:
        errors.append("QA de fiscal_desarrollo no está en PASS")
    if len(fiscal.get("checks", {})) != 12 or not all(fiscal.get("checks", {}).values()):
        errors.append("QA fiscal debe contener 12 controles aprobados")

    household_path = ROOT / "hogares_credito/matriz_evidencia.csv"
    with household_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    expected_classes = {"observado": 19, "proxy": 2, "escenario": 1, "no disponible": 5}
    actual_classes = {
        label: sum(row["classification"] == label for row in rows)
        for label in expected_classes
    }
    if len(rows) != 27 or actual_classes != expected_classes:
        errors.append(
            f"matriz hogares inválida: filas={len(rows)}, clases={actual_classes}"
        )
    ids = [row["evidence_id"] for row in rows]
    if len(ids) != len(set(ids)):
        errors.append("matriz hogares contiene evidence_id duplicados")
    if any(not row["source_url"] for row in rows):
        errors.append("matriz hogares contiene fuentes sin URL")

    for csv_path in ROOT.rglob("*.csv"):
        # Los CSV de sources/ son copias byte a byte de fuentes externas y pueden
        # incluir filas descriptivas antes de la cabecera. Se validan por hash en
        # deep_dive_2026-08-31/validate_deep_dive.py, no se reescriben.
        relative_parts = csv_path.relative_to(ROOT).parts
        if "sources" in relative_parts:
            continue
        with csv_path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            try:
                header = next(reader)
            except StopIteration:
                errors.append(f"CSV vacío: {csv_path.relative_to(ROOT)}")
                continue
            if not header or any(not column for column in header):
                errors.append(f"cabecera CSV inválida: {csv_path.relative_to(ROOT)}")
            width = len(header)
            for line_number, row in enumerate(reader, start=2):
                if len(row) != width:
                    errors.append(
                        f"ancho CSV inválido: {csv_path.relative_to(ROOT)}:{line_number}"
                    )
                    break
    return errors


def validate_claims() -> list[str]:
    errors: list[str] = []
    with CLAIMS.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    ids = [int(row["claim_id"]) for row in rows]
    if set(ids) != EXPECTED_CLAIM_IDS or len(ids) != 27:
        errors.append("claims_registry.csv debe contener exactamente los ids 1..27")
    for row in rows:
        if not row["logical_reading"] or not row["evidence_status"]:
            errors.append(f"afirmación {row['claim_id']} sin lectura lógica o estado de evidencia")
        linked = {int(value) for value in row["linked_analysis_ids"].split(";")}
        if not linked <= EXPECTED_IDS:
            errors.append(f"claim {row['claim_id']} enlaza análisis inexistentes")
    return errors


def main() -> int:
    errors = validate_matrix() + validate_claims() + validate_fronts() + validate_qa()
    if errors:
        for error in errors:
            fail(error)
        return 1
    print("OK: 40 preguntas, 27 claims, 3 frentes y QA consolidado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
