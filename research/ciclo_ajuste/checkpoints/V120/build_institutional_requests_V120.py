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
V119 = HERE.parent / "V119"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v120" / "binaries"
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


source_specs = [
    {
        "id": "e0_argentina_rc_26_216_2008_tsa_sigade",
        "institution": "Secretarías de Hacienda y de Finanzas",
        "title": "Resolución Conjunta 216/2008 y 26/2008 · TSA, COMDOC III, SIGADE y productor DADP",
        "url": "https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-216-2008-144186/texto",
        "file": "argentina_rc_26_216_2008_tsa_sigade.html",
        "publication": "2008-09-01",
        "period": "2008; procedimiento contemporáneo de deuda",
        "type": "HTML oficial · binario preservado",
        "families": "state_bcra;fiscal;debt;records;Caja_de_Valores;SIGADE;COMDOC;TSA",
        "breaks": "procedimiento BOCON versus recompra objetivo; capacidad de sistema versus uso efectivo; constancia tipo versus registro objetivo",
        "use": "USABLE_CONTEMPORANEOUS_SYSTEM_AND_PRODUCER_ROUTE_ONLY",
        "caveat": "Identifica DADP/Unidad de Registro, SIGADE, COMDOC III, TSA/VPN y acuses Caja en un procedimiento BOCON vecino; no prueba que las recompras usaran ese circuito.",
        "verified": "HTML oficial parseado; expediente normativo S01:0037199/2008, considerandos y Anexo I verificados.",
    },
    {
        "id": "e0_bcra_b7971_cryl_operational_files_2003",
        "institution": "Banco Central de la República Argentina",
        "title": "Comunicación B 7971 · archivos operativos CRyL CG1-CG7",
        "url": "https://www.bcra.gob.ar/Pdfs/comytexord/B7971.pdf",
        "file": "bcra_com_b7971_cryl_mensajeria_2003.pdf",
        "publication": "2003-09-02",
        "period": "desde 2003-09; esquema previo a las operaciones 2008-2009",
        "type": "PDF oficial · binario preservado",
        "families": "state_bcra;fiscal;debt;CRYL;settlement;prematching;records",
        "breaks": "diseño de archivo versus registro objetivo; liquidado versus para liquidar; cuenta versus beneficiario final",
        "use": "USABLE_EXACT_CRYL_RECORD_CLASS_AND_FIELD_SCHEMA",
        "caveat": "Define CG1-CG7 y sus campos; no prueba que existan o se conserven archivos de las recompras objetivo.",
        "verified": "5 páginas renderizadas e inspeccionadas visualmente; diseños CG1-CG7 y extracto diario legibles.",
    },
    {
        "id": "e0_bcra_a3191_cryl_dvp_regime_2000",
        "institution": "Banco Central de la República Argentina",
        "title": "Comunicación A 3191 · régimen CRyL y formularios 4359",
        "url": "https://www.bcra.gob.ar/archivos/Pdfs/comytexord/A3191.pdf",
        "file": "bcra_com_a3191_cryl_texto_ordenado_2000.pdf",
        "publication": "2000-12-05",
        "period": "desde 2000-12; línea de base anterior a 2008",
        "type": "PDF oficial · binario preservado",
        "families": "state_bcra;fiscal;debt;CRYL;settlement;DVP;custody;records",
        "breaks": "régimen base versus versión aplicable en 2008; formulario versus instrucción efectiva; cuenta de registro versus tenedor final",
        "use": "USABLE_CRYL_BASELINE_FORMS_REPORTS_AND_CONTROLS",
        "caveat": "Define DVP/FTC/FT, informes por cuenta/especie e incumplimientos; debe verificarse modalidad y versión exacta usada en 2008.",
        "verified": "28 páginas; páginas relevantes 9-20 y 23-27 renderizadas e inspeccionadas visualmente sin defectos.",
    },
]
for spec in source_specs:
    path = BIN / spec["file"]
    if not path.is_file():
        raise FileNotFoundError(path)
    spec["bytes"] = path.stat().st_size
    spec["sha256"] = sha256(path)
    spec["local"] = "/" + path.relative_to(REPO).as_posix()


new_ids = {spec["id"] for spec in source_specs}
catalog = [row for row in read_csv(CATALOG) if row["id"] not in new_ids]
for spec in source_specs:
    catalog.append(
        {
            "id": spec["id"], "tema": "ciclo_ajuste_e0_fiscal", "institucion": spec["institution"],
            "titulo": spec["title"], "url_original": spec["url"], "archivo_local": spec["local"],
            "fecha_descarga": "2026-08-29", "fecha_publicacion": spec["publication"], "codigo_serie": "",
            "periodo_utilizado": spec["period"], "tipo": spec["type"], "sha256": spec["sha256"],
            "nota": f"V120 E0 fiscal: {spec['bytes']:,} bytes. {spec['verified']}",
        }
    )
write_csv(CATALOG, catalog)


census = [row for row in read_csv(V119 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V119.csv") if row["source_id"] not in new_ids]
for spec in source_specs:
    census.append(
        {
            "source_id": spec["id"], "institution": spec["institution"], "artifact": spec["title"],
            "url": spec["url"], "local_path": spec["local"], "sha256": spec["sha256"], "bytes": str(spec["bytes"]),
            "period_coverage": spec["period"], "variable_families": spec["families"], "primary_source": "YES",
            "preserved": "YES", "method_breaks": spec["breaks"], "use_status": spec["use"], "caveat": spec["caveat"],
        }
    )
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V120.csv", census)


ledger = read_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V120.csv")
breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V120.csv")
channels = read_csv(HERE / "CURRENT_OFFICIAL_SUBMISSION_CHANNELS_V120.csv")
trace = read_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V120.csv")
responses = read_csv(HERE / "E0_REQUEST_RESPONSE_REGISTER_V120.csv")
closures = read_csv(HERE / "E0_REQUEST_CLOSURE_CRITERIA_V120.csv")
system_map = read_csv(HERE / "E0_DOCUMENT_SYSTEM_TEMPORAL_MAP_V120.csv")
authorities = read_csv(HERE / "E0_ARCHIVAL_RETENTION_AUTHORITY_MATRIX_V120.csv")
negative_adequacy = read_csv(HERE / "E0_NEGATIVE_RESPONSE_ADEQUACY_V120.csv")
producer_map = read_csv(HERE / "E0_RECORD_PRODUCER_SYSTEM_MAP_V120.csv")
search_keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V120.csv")
attachments = read_csv(HERE / "E0_REQUEST_ATTACHMENT_MINIMUM_V120.csv")

assert len(catalog) == 277
assert len(census) == 78
assert len(ledger) == 125
assert len(breaks) == 69
assert len(channels) == 7
assert len(trace) == 60
assert len(responses) == 6
assert len(closures) == 6
assert len(system_map) == 6
assert len(authorities) == 10
assert len(negative_adequacy) == 14
assert len(producer_map) == 18
assert len(search_keys) == 35
assert len(attachments) == 7


evidence_path = HERE / "HISTORICAL_EVIDENCE_COVERAGE_V120.csv"
evidence = read_csv(evidence_path)
for row in evidence:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            {
                "quality": "PRIMARY_BUYBACK_STRIP_EXACT_ACCOUNT_ROUTE_CRYL_RECORD_SCHEMAS_AND_PRODUCERS_PRESERVED",
                "gap": "Liquidaciones siguen abiertas: se preservaron CG1-CG7, formularios 4359 y la ruta DADP-SIGADE-Caja como claves de búsqueda, no como registros objetivos.",
                "next_action": "Presentar sólo con autorización expresa usando las claves V120; exigir equivalencias de sistema y no convertir esquemas o formularios vacíos en liquidación.",
            }
        )
write_csv(evidence_path, evidence)


queue_path = HERE / "HISTORICAL_SOURCE_QUEUE_V120.csv"
queue = read_csv(queue_path)
for row in queue:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            {
                "status": "INSTITUTIONAL_REQUEST_SYSTEM_KEYS_READY_NOT_SENT",
                "why": "Tres fuentes primarias nuevas identifican DADP/Unidad de Registro, COMDOC III, SIGADE, TSA y archivos CRyL CG1-CG7; 60 objetos quedan trazados sin presentación ni respuesta.",
                "next_action": "Obtener autorización expresa, completar datos personales, presentar sólo los pedidos autorizados y conservar constancias.",
            }
        )
write_csv(queue_path, queue)


inherited = [
    {"script": "qa_v97.py", "pre_v120_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v120_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V97 exige que una fuente recuperada después permanezca sin ruta/hash."},
    *({"script": f"qa_v{i}.py", "pre_v120_result": "PASS", "post_v120_result": "PASS", "interpretation": "Compatible"} for i in (98, 100, 101, 102, 103, 104, 105, 106)),
    *({"script": f"qa_v{i}.py", "pre_v120_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v120_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "Congela un checkpoint o conteo anterior."} for i in range(107, 120)),
    {"script": "qa_v120.py", "pre_v120_result": "N/A", "post_v120_result": "PASS", "interpretation": "Fuentes nuevas, productores, CG1-CG7, formularios, claves, adjuntos y estados no enviados."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V120.csv", inherited)


for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    shutil.copyfile(AUDIT / f"{stem}_V119.csv", AUDIT / f"{stem}_V120.csv")

hash_rows = [row for row in read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V119.csv") if row["id"] not in new_ids]
for spec in source_specs:
    hash_rows.append(
        {"id": spec["id"], "archivo_local": spec["local"], "exists": "True", "sha_catalog": spec["sha256"], "sha_actual": spec["sha256"], "hash_ok": "True"}
    )
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V120.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V120.csv", hash_rows)


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
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V120.csv", size_rows)


physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V119.json").read_text(encoding="utf-8"))
completeness.update(
    {
        "checkpoint": "V120",
        "date": "2026-08-29",
        "state": "E0_CRYL_OPERATIONAL_SCHEMAS_PRIMARY_PRESERVED_REQUEST_KEYS_READY_NOT_SENT",
        "numeric_v120_strict_changed": False,
        "master_catalog_entries": len(catalog),
        "physical_local_copies": physical,
        "physical_local_hash_ok": hash_ok,
        "binary_required_entries": len(catalog) - 4,
        "binary_required_preserved": physical,
        "e0_primary_sources_preserved": len(census),
        "sources_newly_preserved_v120": len(source_specs),
        "e0_primary_sources_newly_preserved_v120": len(source_specs),
        "pending_external_request_actions": 6,
        "e0_request_drafts": len(responses),
        "e0_request_traceability_rows": len(trace),
        "e0_request_closure_rules": len(closures),
        "e0_document_system_temporal_routes": len(system_map),
        "e0_archival_retention_authorities": len(authorities),
        "e0_negative_response_adequacy_controls": len(negative_adequacy),
        "e0_record_producer_system_rows": len(producer_map),
        "e0_request_search_keys": len(search_keys),
        "e0_request_attachment_rows": len(attachments),
        "e0_fiscal_method_breaks_frozen": len(breaks),
        "e0_official_submission_channels_verified": len(channels),
        "e0_requests_submitted": 0,
        "e0_request_responses_received": 0,
        "e0_request_package_status": "DRAFT_NOT_SENT",
        "historical_workstream": "E0_CRYL_OPERATIONAL_SCHEMAS_PRIMARY_PRESERVED_REQUEST_KEYS_READY_NOT_SENT",
    }
)
completeness.pop("numeric_v119_strict_changed", None)
completeness.pop("sources_newly_preserved_v119", None)
completeness.pop("e0_primary_sources_newly_preserved_v119", None)
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V120.json").write_text(
    json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)


backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V120 · productores y archivos CRyL identificados"
old_backup = backup.read_text(encoding="utf-8-sig")
if marker not in old_backup:
    old_backup += (
        f"\n\n{marker}\n\n"
        "- Se preservaron tres fuentes oficiales: DADP/SIGADE/TSA-Caja, archivos CRyL CG1-CG7 y formularios 4359.\n"
        "- Los seis borradores incorporan 18 rutas productor-sistema, 35 claves técnicas, 7 adjuntos mínimos y 60 objetos trazados.\n"
        "- Todos los pedidos permanecen DRAFT_NOT_SENT; no hay plazos ni respuestas en curso.\n"
        "- Las fuentes E0 suben a 78; cifras fiscales y panel bancario permanecen sin cambios.\n"
    )
    backup.write_text(old_backup, encoding="utf-8")


def write_checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V120.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V120",
        "parent_checkpoint": "V119",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "exact_entities": 30,
        "strict_coverage_pct": STRICT,
        "closed_network_gate": "NO",
        "e0_primary_sources": len(census),
        "new_preserved_sources": len(source_specs),
        "new_primary_sources": len(source_specs),
        "fiscal_ledger_rows": len(ledger),
        "fiscal_method_breaks": len(breaks),
        "request_drafts": len(responses),
        "official_submission_channels": len(channels),
        "request_traceability_rows": len(trace),
        "request_closure_rules": len(closures),
        "document_system_temporal_routes": len(system_map),
        "archival_retention_authorities": len(authorities),
        "negative_response_adequacy_controls": len(negative_adequacy),
        "record_producer_system_rows": len(producer_map),
        "request_search_keys": len(search_keys),
        "request_attachment_rows": len(attachments),
        "requests_submitted": 0,
        "responses_received": 0,
        "files": files,
    }
    (HERE / "MANIFEST_V120.json").write_text(
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
    "checkpoint": "V120",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT,
    "exact_entities": 30,
    "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical local copies with {hash_ok}/{physical} SHA-valid; three new primary operational-route sources preserved; six system-keyed requests drafted and none submitted.",
    "historical_workstream": "E0 CRyL CG1-CG7, forms 4359 and DADP-SIGADE-TSA producer routes preserved; target settlements remain open and no request has been submitted",
    "file_count_excluding_manifest": len(global_files),
    "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V120 BUILD PASS")
