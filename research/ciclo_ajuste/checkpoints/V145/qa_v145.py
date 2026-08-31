from pathlib import Path
import csv, hashlib, json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
AUDIT = REPO / "research" / "ciclo_ajuste" / "source_audit"


def rows(name):
    with (HERE / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def file_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


duties = rows("E0_SLU_BACKUP_RETENTION_DUTY_V145.csv")
migration = rows("E0_SLU_MIGRATION_DOCUMENT_CHAIN_V145.csv")
admin = rows("E0_SLU_LOCAL_ADMIN_HISTORY_AND_C55_V145.csv")
siche = rows("E0_SICHE_SLU_LEGAL_CUSTODY_EXPORT_ROUTE_V145.csv")
objects = rows("E0_SLU_BACKUP_AND_SICHE_REQUEST_OBJECTS_V145.csv")
comparator = rows("E0_2007_BACKUP_COMPARATOR_AND_LIMITS_V145.csv")
visual = rows("E0_V145_PDF_VISUAL_CONTROL.csv")

assert len(duties) == 16
assert any(r["official_rule"] == "Fuentes y bases de datos: perpetuo" for r in duties)
assert any(r["official_rule"].endswith("tres años") for r in duties)
assert any(r["dimension"] == "signed_act" for r in duties)
assert len(migration) == 12 and all(r["status"] == "REQUIRED_RECORD_NOT_LOCATED" for r in migration)
assert {"pre_migration_backup", "database_control", "progress", "responsibles"} <= {r["stage"] for r in migration}
assert len(admin) == 15
assert {"direct_debit", "exchange_difference", "global_correction", "c55_reversal"} <= {r["dimension"] for r in admin}
assert any("no BMOVEXTERNO/AMOV_FORG" in r["inference_limit"] for r in admin)
assert len(siche) == 10 and all(r["status"] == "PROVED_ROUTE_TARGET_EXPORT_NOT_EXECUTED" for r in siche)
assert any("única herramienta" in r["official_or_controlled_rule"] for r in siche)
assert any("sin migración/transformación" in r["official_or_controlled_rule"] for r in siche)
assert len(objects) == 18 and all(r["status"] == "DRAFT_NOT_SENT" for r in objects)
assert {"RO145_04", "RO145_09", "RO145_15", "RO145_16", "RO145_17"} <= {r["object_id"] for r in objects}
assert len(comparator) == 6 and all("no " in r["inference_limit"] for r in comparator)
assert len(visual) == 16 and all(r["result"] == "PASS" for r in visual)
assert {"2140", "2141", "2144", "2145", "2147-2149"} <= {r["pdf_page"] for r in visual}

base_tables = rows("E0_SLU_BASE_TABLE_DICTIONARY_V145.csv")
assert len(base_tables) == 12 and all(r["history"] == "NO" for r in base_tables)
assert {"BMOVEXTERNO", "AMOV_FORG", "ACLB_MOB", "BCODLIBBCO"} <= {r["table_name"] for r in base_tables}
recovery = rows("E0_SLU_HISTORICAL_RECOVERY_STRATEGY_V145.csv")
assert len(recovery) == 16 and all(r["status"] == "DRAFT_NOT_SENT" for r in recovery)
assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V145.csv")) == 260
assert len(rows("E0_FISCAL_METHOD_BREAKS_V145.csv")) == 211
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V145.csv")) == 213
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V145.csv")) == 267

ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V145.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)
register = rows("E0_REQUEST_RESPONSE_REGISTER_V145.csv")
assert len(register) == 6 and all(r["status"] == "DRAFT_NOT_SENT" for r in register)
assert all(r["submitted_on"] == "N/A" and r["receipt_or_case_id"] == "N/A" for r in register)

new_ids = {
    "e0_dgsiaf_slu_admin_local_manual_2007",
    "e0_argentina_resolution_115_2005_financial_systems",
    "e0_cgn_joint_disposition_4_03_backup_recovery",
    "e0_argentina_resolution_7028_2007_backup_comparator",
}
census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V145.csv")}
assert len(census) == 217 and new_ids <= set(census)
for source_id in new_ids:
    row = census[source_id]; path = REPO / row["local_path"].lstrip("/")
    assert path.is_file() and file_sha(path) == row["sha256"]

with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 457 and len({r["id"] for r in catalog}) == 457
assert new_ids <= {r["id"] for r in catalog}

with (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V145.csv").open(encoding="utf-8-sig", newline="") as f:
    hashes = list(csv.DictReader(f))
assert sum(r["exists"] == "True" for r in hashes) == 451
assert sum(r["hash_ok"] == "True" for r in hashes) == 451

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V145.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V145"
assert complete["master_catalog_entries"] == 457
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 451
assert complete["sources_newly_preserved_v145"] == 4
assert complete["e0_primary_sources_preserved"] == 217
assert complete["e0_slu_sources_and_databases_retention_rule"] == "PERPETUAL"
assert complete["e0_slu_user_activity_audit_retention_years"] == 3
assert complete["e0_slu_backup_retention_norm_located"] is True
assert complete["e0_slu_historical_backup_inventory_located"] is False
assert complete["e0_slu_specific_2008_backup_restored"] is False
assert complete["e0_siche_slu_current_legal_route_proved"] is True
assert complete["e0_siche_named_queries_executed"] == 0
assert complete["e0_siche_target_exports_located"] == 0
assert complete["e0_slu_target_2008_populated_table_row_located"] is False
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0

request = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V145.md").read_text(encoding="utf-8-sig")
assert "## Clave V145 · SICHE, retención perpetua y migración" in request
assert all(term in request for term in ("BORRADOR_NO_ENVIADO", "Disposición Conjunta", "Resolución 115/2005", "Resolución 53/2024", "BMOVEXTERNO", "AMOV_FORG", "C55", "conc_01.rep", "conc_02.rep"))
refs = (HERE / "SOURCE_REFERENCES_V145.md").read_text(encoding="utf-8-sig")
assert refs.count("## Fuentes nuevas V145 · resguardo, migración, administrador local y comparador") == 1
assert all(source_id in refs for source_id in new_ids)

manifest = json.loads((HERE / "MANIFEST_V145.json").read_text(encoding="utf-8"))
assert manifest["checkpoint"] == "V145" and manifest["parent_checkpoint"] == "V144"
assert manifest["requests_submitted"] == 0 and manifest["executed_settlement_rows_confirmed"] == 0
for name in ("README_V145.md", "VEREDICTO_V145.md", "E0_FISCAL_RECONSTRUCTION_V145.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V145_A_V146.md"):
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")

combined = "\n".join(p.read_text(encoding="utf-8-sig") for p in HERE.glob("*.csv")) + request
assert "REQUEST_SENT" not in combined and "TARGET_EXTRACT_FOUND" not in combined
print("V145 QA PASS")
