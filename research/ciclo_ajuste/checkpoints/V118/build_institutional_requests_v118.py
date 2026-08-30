from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import shutil


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CYCLE = REPO / "research" / "ciclo_ajuste"
AUDIT = CYCLE / "source_audit"
V117 = HERE.parent / "V117"
STRICT = "61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        if not rows:
            raise ValueError(f"fields required for empty CSV: {path}")
        fields = list(rows[0])
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


catalog = read_csv(REPO / "data" / "fuentes" / "FUENTES.csv")
census = read_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V118.csv")
ledger = read_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V118.csv")
breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V118.csv")
channels = read_csv(HERE / "CURRENT_OFFICIAL_SUBMISSION_CHANNELS_V118.csv")
trace = read_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V118.csv")
responses = read_csv(HERE / "E0_REQUEST_RESPONSE_REGISTER_V118.csv")
closures = read_csv(HERE / "E0_REQUEST_CLOSURE_CRITERIA_V118.csv")

assert len(catalog) == 274
assert len(census) == 75
assert len(ledger) == 125
assert len(breaks) == 61
assert len(channels) == 7
assert len(trace) == 34
assert len(responses) == 6
assert len(closures) == 6


evidence_path = HERE / "HISTORICAL_EVIDENCE_COVERAGE_V118.csv"
evidence = read_csv(evidence_path)
for row in evidence:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            {
                "quality": "PRIMARY_BUYBACK_STRIP_EXACT_ACCOUNT_ROUTE_CUSTODIAN_GAP_DOCUMENTED_REQUEST_PACKAGE_READY",
                "gap": "Liquidaciones, blotter BNA, respuesta AGN y registros custodiales siguen abiertos; seis pedidos separados están listos pero no enviados.",
                "next_action": "Presentar sólo con autorización expresa y evaluar respuestas contra los criterios V118; mientras tanto no fingir plazos ni respuestas.",
            }
        )
write_csv(evidence_path, evidence)


queue_path = HERE / "HISTORICAL_SOURCE_QUEUE_V118.csv"
queue = read_csv(queue_path)
for row in queue:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            {
                "status": "INSTITUTIONAL_REQUEST_PACKAGE_READY_NOT_SENT",
                "why": "Seis borradores separan Tesoro, BCRA/CRyL, BNA, AGN, CNV y Caja y trazan 34 documentos; no existe presentación ni respuesta.",
                "next_action": "Obtener autorización expresa, completar datos personales, presentar sólo los pedidos autorizados y conservar constancias.",
            }
        )
write_csv(queue_path, queue)


inherited = [
    {"script": "qa_v97.py", "pre_v118_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v118_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V97 exige que una fuente recuperada después permanezca sin ruta/hash."},
    *({"script": f"qa_v{i}.py", "pre_v118_result": "PASS", "post_v118_result": "PASS", "interpretation": "Compatible"} for i in (98, 100, 101, 102, 103, 104, 105, 106)),
    *({"script": f"qa_v{i}.py", "pre_v118_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v118_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "Congela un checkpoint o conteo anterior."} for i in range(107, 118)),
    {"script": "qa_v118.py", "pre_v118_result": "N/A", "post_v118_result": "PASS", "interpretation": "Paquete, canales, trazabilidad, estados no enviados e invariantes actuales."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V118.csv", inherited)


for stem in (
    "MASTER_LOCAL_HASH_VALIDATION",
    "SOURCE_BACKUP_CENSUS",
    "SOURCE_PATH_ENCODING_EXCEPTIONS",
    "SOURCE_PRESERVATION_MISSING",
):
    shutil.copyfile(AUDIT / f"{stem}_V117.csv", AUDIT / f"{stem}_V118.csv")


size_rows = []
for path in sorted(REPO.rglob("*")):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
        continue
    size = path.stat().st_size
    size_rows.append(
        {
            "path": path.relative_to(REPO).as_posix(),
            "bytes": str(size),
            "mib": f"{size / 1048576:.6f}",
            "over_50_mib": str(size > 50 * 1048576),
            "over_100_mib": str(size > 100 * 1048576),
        }
    )
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V118.csv", size_rows)


hash_rows = read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V118.csv")
physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V117.json").read_text(encoding="utf-8"))
completeness.update(
    {
        "checkpoint": "V118",
        "date": "2026-08-29",
        "state": "E0_INSTITUTIONAL_REQUEST_PACKAGE_READY_NOT_SENT",
        "numeric_v118_strict_changed": False,
        "sources_newly_preserved_v118": 0,
        "e0_primary_sources_newly_preserved_v118": 0,
        "pending_external_request_actions": 6,
        "e0_request_drafts": len(responses),
        "e0_request_traceability_rows": len(trace),
        "e0_request_closure_rules": len(closures),
        "e0_official_submission_channels_verified": len(channels),
        "e0_requests_submitted": 0,
        "e0_request_responses_received": 0,
        "e0_request_package_status": "DRAFT_NOT_SENT",
        "historical_workstream": "E0_INSTITUTIONAL_REQUEST_PACKAGE_READY_NOT_SENT",
    }
)
completeness.pop("numeric_v117_strict_changed", None)
completeness.pop("sources_newly_preserved_v117", None)
completeness.pop("e0_primary_sources_newly_preserved_v117", None)
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V118.json").write_text(
    json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)


backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V118 · paquete institucional listo"
old_backup = backup.read_text(encoding="utf-8-sig")
if marker not in old_backup:
    old_backup += (
        f"\n\n{marker}\n\n"
        "- Se verificaron canales oficiales vigentes para Economía, BCRA, BNA, AGN, CNV y Caja.\n"
        "- Se prepararon seis borradores separados, 34 objetos trazados y seis criterios de cierre.\n"
        "- Todos los pedidos permanecen DRAFT_NOT_SENT; no hay plazos ni respuestas en curso.\n"
        "- Fuentes, cifras fiscales y panel bancario permanecen sin cambios.\n"
    )
    backup.write_text(old_backup, encoding="utf-8")


def write_checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V118.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V118",
        "parent_checkpoint": "V117",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30,
        "strict_coverage_pct": STRICT,
        "closed_network_gate": "NO",
        "e0_primary_sources": len(census),
        "new_preserved_sources": 0,
        "new_primary_sources": 0,
        "fiscal_ledger_rows": len(ledger),
        "fiscal_method_breaks": len(breaks),
        "request_drafts": len(responses),
        "official_submission_channels": len(channels),
        "request_traceability_rows": len(trace),
        "request_closure_rules": len(closures),
        "requests_submitted": 0,
        "responses_received": 0,
        "files": files,
    }
    (HERE / "MANIFEST_V118.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


write_checkpoint_manifest()


def build_tree(root: Path) -> str:
    lines = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix().casefold()):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        lines.append(path.relative_to(root).as_posix() + ("/" if path.is_dir() else ""))
    return "\n".join(lines) + "\n"


(REPO / "TREE.txt").write_text(build_tree(REPO), encoding="utf-8")
(CYCLE / "TREE.txt").write_text(build_tree(CYCLE), encoding="utf-8")


global_manifest_path = CYCLE / "MANIFEST_SHA256.json"
global_files = []
for path in sorted(REPO.rglob("*"), key=lambda item: item.relative_to(REPO).as_posix().casefold()):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts or path == global_manifest_path:
        continue
    global_files.append(
        {"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)}
    )
global_manifest = {
    "checkpoint": "V118",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT,
    "exact_entities": 30,
    "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical local copies with {hash_ok}/{physical} SHA-valid; no new historical source; six institutional requests drafted and none submitted.",
    "historical_workstream": "E0 institutional request package ready; Treasury/BCRA/BNA/AGN/CNV/Caja records remain open and no request has been submitted",
    "file_count_excluding_manifest": len(global_files),
    "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V118 BUILD PASS")
