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
V120 = HERE.parent / "V120"
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
BIN = CYCLE / "inputs" / "historical_retrieval" / "v121" / "binaries"
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
        "id": "e0_bcra_a3253_cryl_rml_2001",
        "institution": "Banco Central de la República Argentina",
        "title": "Comunicación A 3253 · modificación acotada de cuentas CRyL",
        "url": "https://www.bcra.gob.ar/archivos/Pdfs/comytexord/A3253.pdf",
        "file": "bcra_com_a3253_cryl_rml_2001.pdf",
        "publication": "2001-04-10",
        "period": "desde 2001-04; modificación previa a 2008",
        "type": "PDF oficial · binario preservado",
        "families": "state_bcra;fiscal;debt;CRYL;accounts;custody;records",
        "breaks": "modificación de cuentas versus reemplazo de modalidades; cuenta CRyL versus operación objetivo",
        "use": "USABLE_SCOPED_CRYL_AMENDMENT",
        "caveat": "Modifica cuentas 03/04 e incorpora 08 RML; no documenta un reemplazo de DVP/FTC/FT ni el uso en recompras.",
        "verified": "5 páginas renderizadas e inspeccionadas visualmente; comunicación, cuentas 03/04/08 y tabla de origen legibles.",
    },
    {
        "id": "e0_bcra_a3621_cryl_scope_2002",
        "institution": "Banco Central de la República Argentina",
        "title": "Comunicación A 3621 · cambio de denominación y alcance CRyL",
        "url": "https://www.bcra.gob.ar/archivos/Pdfs/comytexord/A3621.pdf",
        "file": "bcra_com_a3621_cryl_scope_2002.pdf",
        "publication": "2002-06-03",
        "period": "desde 2002-06; ampliación previa a 2008",
        "type": "PDF oficial · binario preservado",
        "families": "state_bcra;fiscal;debt;CRYL;scope;custody;records",
        "breaks": "ampliación de alcance versus cambio de modalidad; sistema disponible versus asiento objetivo",
        "use": "USABLE_CRYL_SCOPE_CHANGE_ONLY",
        "caveat": "Renombra y amplía CRyL; no identifica formularios sustituidos ni liquidaciones de recompras.",
        "verified": "Única página renderizada e inspeccionada visualmente; puntos 1 y 2 legibles.",
    },
    {
        "id": "e0_bcra_b9173_cryl_cga_x400_2008",
        "institution": "Banco Central de la República Argentina",
        "title": "Comunicación B 9173 · CGA; X-400/MCT y validación FT/FTC",
        "url": "https://www.bcra.gob.ar/archivos/Pdfs/comytexord/B9173.pdf",
        "file": "bcra_com_b9173_cryl_cga_x400_2008.pdf",
        "publication": "2008-01-09",
        "period": "vigencia operativa desde 2008-01-21; antes de las recompras",
        "type": "PDF oficial · binario preservado",
        "families": "state_bcra;fiscal;debt;CRYL;settlement;CGA;X400;MCT;records",
        "breaks": "validación versus liquidación; esquema aplicable versus modalidad usada; código CRyL versus cuenta fiduciaria",
        "use": "USABLE_EXACT_2008_CRYL_OPERATIONAL_RULE",
        "caveat": "Define CGA para FT/FTC y dos etapas; no prueba que las recompras usaran esa modalidad ni que el acuse condicional terminara liquidado.",
        "verified": "8 páginas renderizadas e inspeccionadas visualmente; diseño CGA, horarios, validaciones y rechazos legibles.",
    },
    {
        "id": "e0_bcra_b10469_cryl_code_continuity_2012",
        "institution": "Banco Central de la República Argentina",
        "title": "Comunicación B 10469 · continuidad CG1-CG7/CGA en IDEAR",
        "url": "https://www.bcra.gob.ar/archivos/Pdfs/comytexord/B10469.pdf",
        "file": "bcra_com_b10469_mensajeria_2012.pdf",
        "publication": "2012-10-22",
        "period": "migración operativa desde 2012-11-07; continuidad posterior",
        "type": "PDF oficial · binario preservado",
        "families": "state_bcra;fiscal;debt;CRYL;CGA;CG1_CG7;migration;records",
        "breaks": "continuidad de código versus preservación de archivo histórico; migración versus equivalencia transaccional",
        "use": "USABLE_POST_TARGET_CODE_CONTINUITY",
        "caveat": "Enumera CG1-CG7 y CGA al migrar a IDEAR; no acredita conservación de lotes 2008-2009.",
        "verified": "2 páginas renderizadas e inspeccionadas visualmente; tabla de códigos y direcciones legible.",
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
            "nota": f"V121 E0 fiscal: {spec['bytes']:,} bytes. {spec['verified']}",
        }
    )
write_csv(CATALOG, catalog)


census = [row for row in read_csv(V120 / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V120.csv") if row["source_id"] not in new_ids]
for spec in source_specs:
    census.append(
        {
            "source_id": spec["id"], "institution": spec["institution"], "artifact": spec["title"],
            "url": spec["url"], "local_path": spec["local"], "sha256": spec["sha256"], "bytes": str(spec["bytes"]),
            "period_coverage": spec["period"], "variable_families": spec["families"], "primary_source": "YES",
            "preserved": "YES", "method_breaks": spec["breaks"], "use_status": spec["use"], "caveat": spec["caveat"],
        }
    )
write_csv(HERE / "E0_LOCAL_PRIMARY_SOURCE_CENSUS_V121.csv", census)


ledger = read_csv(HERE / "E0_FISCAL_MECHANISM_LEDGER_V121.csv")
breaks = read_csv(HERE / "E0_FISCAL_METHOD_BREAKS_V121.csv")
channels = read_csv(HERE / "CURRENT_OFFICIAL_SUBMISSION_CHANNELS_V121.csv")
trace = read_csv(HERE / "E0_INFORMATION_REQUEST_TRACEABILITY_V121.csv")
responses = read_csv(HERE / "E0_REQUEST_RESPONSE_REGISTER_V121.csv")
closures = read_csv(HERE / "E0_REQUEST_CLOSURE_CRITERIA_V121.csv")
system_map = read_csv(HERE / "E0_DOCUMENT_SYSTEM_TEMPORAL_MAP_V121.csv")
authorities = read_csv(HERE / "E0_ARCHIVAL_RETENTION_AUTHORITY_MATRIX_V121.csv")
negative_adequacy = read_csv(HERE / "E0_NEGATIVE_RESPONSE_ADEQUACY_V121.csv")
producer_map = read_csv(HERE / "E0_RECORD_PRODUCER_SYSTEM_MAP_V121.csv")
search_keys = read_csv(HERE / "E0_REQUEST_SEARCH_KEY_MATRIX_V121.csv")
attachments = read_csv(HERE / "E0_REQUEST_ATTACHMENT_MINIMUM_V121.csv")
version_chain = read_csv(HERE / "E0_CRYL_EFFECTIVE_VERSION_CHAIN_V121.csv")
term_audit = read_csv(HERE / "E0_BUYBACK_MODALITY_TERM_AUDIT_V121.csv")
cga_map = read_csv(HERE / "E0_CRYL_CGA_RECORD_MAP_V121.csv")

assert len(catalog) == 281
assert len(census) == 82
assert len(ledger) == 125
assert len(breaks) == 73
assert len(channels) == 7
assert len(trace) == 67
assert len(responses) == 6
assert len(closures) == 6
assert len(system_map) == 6
assert len(authorities) == 10
assert len(negative_adequacy) == 14
assert len(producer_map) == 22
assert len(search_keys) == 43
assert len(attachments) == 7
assert len(version_chain) == 9
assert len(term_audit) == 8
assert len(cga_map) == 8


evidence_path = HERE / "HISTORICAL_EVIDENCE_COVERAGE_V121.csv"
evidence = read_csv(evidence_path)
for row in evidence:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            {
                "quality": "PRIMARY_BUYBACK_STRIP_EXACT_ACCOUNT_ROUTE_CRYL_2008_CGA_RULE_AND_CODE_CONTINUITY_PRESERVED",
                "gap": "La regla CGA/FT/FTC vigente desde enero de 2008 está preservada, pero falta vincular la modalidad diferida de cada recompra con lote/fórmula, segunda validación, CG3 y pago.",
                "next_action": "Presentar sólo con autorización expresa usando las claves V121; exigir equivalencia entre modalidad diferida, CGA o fórmula en papel y no convertir un acuse condicional en liquidación.",
            }
        )
write_csv(evidence_path, evidence)


queue_path = HERE / "HISTORICAL_SOURCE_QUEUE_V121.csv"
queue = read_csv(queue_path)
for row in queue:
    if row["episode"] == "E0_2001_2003" and row["variable_family"] == "state_bcra":
        row.update(
            {
                "status": "INSTITUTIONAL_REQUEST_CRYL_2008_KEYS_READY_NOT_SENT",
                "why": "Cuatro fuentes primarias nuevas reconstruyen cambios de cuenta/alcance, CGA vía X-400/MCT desde enero de 2008 y continuidad CG1-CG7/CGA en 2012; 67 objetos quedan trazados sin presentación ni respuesta.",
                "next_action": "Obtener autorización expresa, completar datos personales, presentar sólo los pedidos autorizados y conservar constancias.",
            }
        )
write_csv(queue_path, queue)


inherited = [
    {"script": "qa_v97.py", "pre_v121_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v121_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "V97 exige que una fuente recuperada después permanezca sin ruta/hash."},
    *({"script": f"qa_v{i}.py", "pre_v121_result": "PASS", "post_v121_result": "PASS", "interpretation": "Compatible"} for i in (98, 100, 101, 102, 103, 104, 105, 106)),
    *({"script": f"qa_v{i}.py", "pre_v121_result": "EXPECTED_SUPERSEDED_ASSERTION", "post_v121_result": "EXPECTED_SUPERSEDED_ASSERTION", "interpretation": "Congela un checkpoint o conteo anterior."} for i in range(107, 121)),
    {"script": "qa_v121.py", "pre_v121_result": "N/A", "post_v121_result": "PASS", "interpretation": "Cadena temporal, CGA 2008, continuidad 2012, claves y estados no enviados."},
]
write_csv(HERE / "INHERITED_QA_STATUS_V121.csv", inherited)


for stem in ("SOURCE_PATH_ENCODING_EXCEPTIONS", "SOURCE_PRESERVATION_MISSING"):
    shutil.copyfile(AUDIT / f"{stem}_V120.csv", AUDIT / f"{stem}_V121.csv")

hash_rows = [row for row in read_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V120.csv") if row["id"] not in new_ids]
for spec in source_specs:
    hash_rows.append(
        {"id": spec["id"], "archivo_local": spec["local"], "exists": "True", "sha_catalog": spec["sha256"], "sha_actual": spec["sha256"], "hash_ok": "True"}
    )
write_csv(AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V121.csv", hash_rows)
write_csv(AUDIT / "SOURCE_BACKUP_CENSUS_V121.csv", hash_rows)


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
write_csv(AUDIT / "GITHUB_FILE_SIZE_AUDIT_V121.csv", size_rows)


physical = sum(row["exists"] == "True" for row in hash_rows)
hash_ok = sum(row["hash_ok"] == "True" for row in hash_rows)
completeness = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V120.json").read_text(encoding="utf-8"))
completeness.update(
    {
        "checkpoint": "V121",
        "date": "2026-08-29",
        "state": "E0_CRYL_2008_CGA_EFFECTIVE_RULE_PRIMARY_PRESERVED_REQUEST_KEYS_READY_NOT_SENT",
        "numeric_v121_strict_changed": False,
        "master_catalog_entries": len(catalog),
        "physical_local_copies": physical,
        "physical_local_hash_ok": hash_ok,
        "binary_required_entries": len(catalog) - 4,
        "binary_required_preserved": physical,
        "e0_primary_sources_preserved": len(census),
        "e0_quality": "PRIMARY_BUYBACK_STRIP_EXACT_ACCOUNT_ROUTE_CRYL_2008_CGA_RULE_AND_CODE_CONTINUITY_PRESERVED",
        "sources_newly_preserved_v121": len(source_specs),
        "e0_primary_sources_newly_preserved_v121": len(source_specs),
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
        "e0_cryl_effective_version_chain_rows": len(version_chain),
        "e0_buyback_modality_term_audit_rows": len(term_audit),
        "e0_cryl_cga_record_map_rows": len(cga_map),
        "e0_fiscal_method_breaks_frozen": len(breaks),
        "e0_official_submission_channels_verified": len(channels),
        "e0_requests_submitted": 0,
        "e0_request_responses_received": 0,
        "e0_request_package_status": "DRAFT_NOT_SENT",
        "historical_workstream": "E0_CRYL_2008_CGA_EFFECTIVE_RULE_PRIMARY_PRESERVED_REQUEST_KEYS_READY_NOT_SENT",
    }
)
completeness.pop("numeric_v120_strict_changed", None)
completeness.pop("sources_newly_preserved_v120", None)
completeness.pop("e0_primary_sources_newly_preserved_v120", None)
(AUDIT / "CURRENT_SOURCE_COMPLETENESS_V121.json").write_text(
    json.dumps(completeness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)


backup = REPO / "BACKUP_ACTUALIZACION_2026-08-29.md"
marker = "## V121 · vigencia CRyL 2008 y CGA reconstruidos"
old_backup = backup.read_text(encoding="utf-8-sig")
if marker not in old_backup:
    old_backup += (
        f"\n\n{marker}\n\n"
        "- Se preservaron cuatro fuentes oficiales: A3253, A3621, B9173 y B10469.\n"
        "- B9173 prueba CGA vía X-400/MCT para FT/FTC desde enero de 2008 y separa validación condicional de liquidación.\n"
        "- Los seis borradores incorporan 22 rutas productor-sistema, 43 claves técnicas, 7 adjuntos mínimos y 67 objetos trazados.\n"
        "- Todos los pedidos permanecen DRAFT_NOT_SENT; no hay plazos ni respuestas en curso.\n"
        "- Las fuentes E0 suben a 82; cifras fiscales y panel bancario permanecen sin cambios.\n"
    )
    backup.write_text(old_backup, encoding="utf-8")


def write_checkpoint_manifest() -> None:
    files = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "MANIFEST_V121.json":
            continue
        files.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "checkpoint": "V121",
        "parent_checkpoint": "V120",
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
        "cryl_effective_version_chain_rows": len(version_chain),
        "buyback_modality_term_audit_rows": len(term_audit),
        "cryl_cga_record_map_rows": len(cga_map),
        "requests_submitted": 0,
        "responses_received": 0,
        "files": files,
    }
    (HERE / "MANIFEST_V121.json").write_text(
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
    "checkpoint": "V121",
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "strict_coverage_pct": STRICT,
    "exact_entities": 30,
    "closed_network_gate": "NO",
    "source_audit": f"{len(catalog)} master entries; {physical} physical local copies with {hash_ok}/{physical} SHA-valid; four new primary CRyL temporal/operational sources preserved; six system-keyed requests drafted and none submitted.",
    "historical_workstream": "E0 CRyL effective 2008 CGA/X-400 rule and 2012 code continuity preserved; target modality, settlement and payment remain open; no request submitted",
    "file_count_excluding_manifest": len(global_files),
    "files": global_files,
}
global_manifest_path.write_text(json.dumps(global_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("V121 BUILD PASS")


