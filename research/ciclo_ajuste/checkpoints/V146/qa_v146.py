from pathlib import Path
import csv, hashlib, json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
AUDIT = REPO / "research" / "ciclo_ajuste" / "source_audit"


def rows(name):
    with (HERE / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


new_ids = {
    "e0_argentina_sidif_link_historical_integration",
    "e0_dgsiaf_trajectory_sidif_link",
    "e0_mecon_uai_plan_2019_sigade_sidif_link",
    "e0_mecon_uai_report_13_2020_repo_commission",
    "e0_dgsiaf_siche_sidif_central_q2_2022",
    "e0_cgn_chart_accounts_2018",
    "e0_cgn_account_1999_repo_portfolio",
}

with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as handle:
    catalog = list(csv.DictReader(handle))
assert len(catalog) == 464 and len({row["id"] for row in catalog}) == 464
assert new_ids <= {row["id"] for row in catalog}

census = {row["source_id"]: row for row in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V146.csv")}
provenance = {row["source_id"]: row for row in rows("ARCHIVAL_PROVENANCE_V146.csv")}
assert len(census) == 224 and new_ids <= set(census) and new_ids <= set(provenance)
for source_id in new_ids:
    path = REPO / census[source_id]["local_path"].lstrip("/")
    assert path.is_file() and digest(path) == census[source_id]["sha256"]

chain = rows("E0_SAF355_SIGADE_SIDIF_LINK_SYSTEM_CHAIN_V146.csv")
route = rows("E0_SICHE_SIDIF_CENTRAL_TARGET_ROUTE_V146.csv")
repo = rows("E0_REPO_COMMISSION_ACCOUNT_LEAD_V146.csv")
objects = rows("E0_SIDIF_LINK_SICHE_REQUEST_OBJECTS_V146.csv")
strategy = rows("E0_SIDIF_LINK_HISTORICAL_RECOVERY_STRATEGY_V146.csv")
visual = rows("E0_V146_PDF_VISUAL_CONTROL.csv")
assert len(chain) == 12 and any(row["system"] == "SLU" and "condicional" in row["official_fact_or_target"] for row in chain)
assert len(route) == 14 and {"Formulario por Pda. Presupuestaria y Sigade", "Deuda Exigible hasta 2008 / Gastos por Beneficiarios"} <= {row["object_or_query"] for row in route}
assert len(repo) == 10 and all(row["target_2008_identity"] == "FALSE" for row in repo)
assert next(row["value"] for row in repo if row["datum"] == "published_components_sum") == "563.61"
assert next(row["value"] for row in repo if row["datum"] == "published_internal_gap") == "0.45"
assert len(objects) == 16 and all(row["status"] == "DRAFT_NOT_SENT" for row in objects)
assert len(strategy) == 10 and all(row["status"] == "DRAFT_NOT_SENT" for row in strategy)
assert len(visual) == 24 and all(row["result"] == "PASS" for row in visual)

breaks = rows("E0_FISCAL_METHOD_BREAKS_V146.csv")
trace = rows("E0_INFORMATION_REQUEST_TRACEABILITY_V146.csv")
keys = rows("E0_REQUEST_SEARCH_KEY_MATRIX_V146.csv")
assert len(breaks) == 217 and {"saf355_slu_not_primary_without_deployment", "sidif_accounting_not_bank_settlement", "uai_repo_arithmetic_gap_045m"} <= {row["break_id"] for row in breaks}
assert len(trace) == 229 and all(row["status"] == "DRAFT_NOT_SENT" for row in trace)
assert len(keys) == 285 and {"SIDIF-LINK", "2.1.2.01.02.99.00", "563,61"} <= {row["exact_key"] for row in keys}

register = rows("E0_REQUEST_RESPONSE_REGISTER_V146.csv")
assert len(register) == 6 and all(row["status"] == "DRAFT_NOT_SENT" for row in register)
assert all(row["submitted_on"] == "N/A" and row["receipt_or_case_id"] == "N/A" for row in register)
request_files = [
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V146.md", "REQUEST_BCRA_CRYL_SETTLEMENT_V146.md",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V146.md", "REQUEST_AGN_2018_REPLY_V146.md",
    "REQUEST_CNV_CUSTODY_RECORDS_V146.md", "REQUEST_CAJA_SETTLEMENT_HOLDINGS_V146.md",
]
for name in request_files:
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "BORRADOR_NO_ENVIADO" in text or "DRAFT_NOT_SENT" in text

with (AUDIT / "MASTER_LOCAL_HASH_VALIDATION_V146.csv").open(encoding="utf-8-sig", newline="") as handle:
    hashes = list(csv.DictReader(handle))
assert sum(row["exists"] == "True" for row in hashes) == 458
assert sum(row["hash_ok"] == "True" for row in hashes) == 458

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V146.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"] == "V146"
assert complete["master_catalog_entries"] == 464
assert complete["e0_primary_sources_preserved"] == 224
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 458
assert complete["e0_primary_target_route"] == "SIGADE_SIDIF_LINK_SIDIF_CENTRAL_SICHE"
assert complete["e0_siche_named_queries_executed"] == 0 and complete["e0_siche_target_exports_located"] == 0
assert complete["e0_repo_commission_2019_lead_located"] is True
assert complete["e0_repo_commission_target_2008_identity_proved"] is False
assert complete["e0_repo_published_internal_gap_ars_millions"] == "0.45"
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0

manifest = json.loads((HERE / "MANIFEST_V146.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"] == "V146" and manifest["parent_checkpoint"] == "V145"
assert manifest["new_preserved_sources"] == 7 and manifest["requests_submitted"] == 0
assert manifest["executed_settlement_rows_confirmed"] == 0 and manifest["repo_target_2008_identity_proved"] is False
for name in ("README_V146.md", "VEREDICTO_V146.md", "E0_FISCAL_RECONSTRUCTION_V146.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V146_A_V147.md"):
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")

assert not list(HERE.glob("*V145*"))
combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined and "TARGET_EXTRACT_FOUND" not in combined
print("V146 QA PASS")
