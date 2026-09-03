from __future__ import annotations

import csv
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "research" / "political_wealth_2026-09-01" / "derived"
OUTPUT = ROOT / "assets" / "political-wealth-data.js"


def build_bootstrap(*, quiet: bool = False) -> Path:
    with (DERIVED / "active_politician_research_queue_2026-09-01.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        research_queue = list(csv.DictReader(handle))
    dashboard_data = json.loads(
        (DERIVED / "dashboard_data_2017_2025.json").read_text(encoding="utf-8")
    )
    source_consistency = json.loads(
        (DERIVED / "active_series_source_consistency_summary_2022_2024.json").read_text(
            encoding="utf-8"
        )
    )
    dashboard_data["source_consistency"] = source_consistency["filas"]
    dashboard_data["source_consistency_summary"] = source_consistency["resumen"]
    audit_files = {
        "karina": "karina_milei_revaluation_audit_2023_2025.json",
        "javier": "javier_milei_revaluation_audit_2023_2025.json",
        "dip-del-pla-romina": "romina_del_pla_patrimonial_audit_2023_2024.json",
        "dip-estevez-gabriela-beatriz": "gabriela_estevez_patrimonial_audit_2022_2024.json",
        "sen-gadano-natalia-elena": "natalia_gadano_patrimonial_audit_2023_2024.json",
        "dip-vega-yolanda": "yolanda_vega_patrimonial_audit_2023_2024.json",
        "dip-bongiovanni-alejandro": "alejandro_bongiovanni_patrimonial_audit_2023_2024.json",
        "dip-correa-llano-facundo": "facundo_correa_llano_patrimonial_audit_2023_2024.json",
        "dip-vasquez-patricia": "patricia_vasquez_patrimonial_audit_2023_2024.json",
    }
    for person_id, filename in audit_files.items():
        audit = json.loads((DERIVED / filename).read_text(encoding="utf-8"))
        dashboard_data.setdefault("case_audits", {})[person_id] = audit
        existing_composition = {
            (row["persona_id"], int(row["anio"]), row["categoria"])
            for row in dashboard_data["composition"]
        }
        dashboard_data["composition"].extend(
            row
            for row in audit.get("composition", [])
            if (row["persona_id"], int(row["anio"]), row["categoria"])
            not in existing_composition
        )
    verified_batches = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in DERIVED.glob("active_politician_verified_dashboard_iteration_*.json")
    ]
    for verified in sorted(verified_batches, key=lambda item: int(item["metadata"]["lote"])):
        existing_ids = {row["persona_id"] for row in dashboard_data["people"]}
        additions = [row for row in verified["people"] if row["persona_id"] not in existing_ids]
        addition_ids = {row["persona_id"] for row in additions}
        dashboard_data["people"].extend(additions)
        dashboard_data["series"].extend(
            row for row in verified["series"] if row["persona_id"] in addition_ids
        )
        dashboard_data["coverage"].extend(
            row for row in verified["coverage"] if row["persona_id"] in addition_ids
        )
        dashboard_data["benchmark_comparisons"].extend(
            row for row in verified["benchmark_comparisons"] if row["persona_id"] in addition_ids
        )
    if verified_batches:
        dashboard_data["metadata"]["trayectorias_auditadas"] = len(dashboard_data["people"])
        dashboard_data["metadata"]["ultima_iteracion_integrada"] = max(
            int(item["metadata"]["lote"]) for item in verified_batches
        )
    payload = {
        "data": dashboard_data,
        "roster": json.loads(
            (DERIVED / "active_politicians_coverage_2026-09-01.json").read_text(
                encoding="utf-8"
            )
        ),
        "research": json.loads(
            (DERIVED / "active_politician_research_summary_2026-09-01.json").read_text(
                encoding="utf-8"
            )
        ),
        "queue": research_queue,
    }
    content = (
        "window.__POLITICAL_WEALTH_BOOTSTRAP__="
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + ";\n"
    )
    temporary = OUTPUT.with_name(f".{OUTPUT.name}.{os.getpid()}.build-tmp")
    try:
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(OUTPUT)
    finally:
        if temporary.exists():
            temporary.unlink()
    if not quiet:
        print(f"OK: bootstrap patrimonial · {OUTPUT.stat().st_size / 1024 / 1024:.2f} MiB")
    return OUTPUT


if __name__ == "__main__":
    build_bootstrap()
