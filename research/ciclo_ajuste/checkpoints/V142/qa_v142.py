from pathlib import Path
import csv
import hashlib
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
AUDIT = REPO / "research" / "ciclo_ajuste" / "source_audit"

def rows(name):
    with (HERE / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

repo = rows("E0_SICHE_CUT_HISTORICAL_REPOSITORY_V142.csv")
fields = rows("E0_CUT_EXTRACT_FIELD_CROSSWALK_V142.csv")
chain = rows("E0_CUT_AUDITOR_EVIDENCE_CHAIN_V142.csv")
runbook = rows("E0_CUT_TARGET_QUERY_RUNBOOK_V142.csv")
zero = rows("E0_CUT_ZERO_RESULT_AND_CONCILIATION_LIMITS_V142.csv")
visual = rows("E0_V142_PDF_VISUAL_CONTROL.csv")
plan = rows("E0_SICHE_TARGET_QUERY_PLAN_V142.csv")
codes = rows("E0_CUT_EVENT_CODE_DICTIONARY_V142.csv")
continuity = rows("E0_CUT_EVENT_CODE_CONTINUITY_V142.csv")
accounts = rows("E0_CUT_OPERATION_ACCOUNT_EQUATIONS_V142.csv")
discriminators = rows("E0_CUT_TARGET_CODE_DISCRIMINATION_V142.csv")
route = rows("E0_CUT_RECONCILIATION_EVIDENCE_ROUTE_V142.csv")
assert len(repo) == 10
assert repo[1]["proved_scope"] == "incluye ejercicio 2008"
assert {"Entidades Básicas", "Saldos por Tipo de Apertura de Cuenta de Operación", "Extractos", "Logs de Impacto"} <= {r["evidence"] for r in repo}
assert len(fields) == 20
assert {"Cod. Mov.", "Comprobante Respaldo", "Comprobante Origen", "Comprobante Relacionado"} <= {r["source_field"] for r in fields}
assert all("2008" in r["legacy_status"] for r in fields)
assert len(chain) == 12 and any("diferencia" in r["proof"].casefold() for r in chain)
assert len(runbook) == 19 and all(r["status"] == "DRAFT_NOT_SENT" for r in runbook)
assert len(zero) == 8 and all(r["status"] == "FROZEN" for r in zero)
assert len(visual) == 13 and all(r["result"] == "PASS" for r in visual)
assert len(plan) == 15 and all(r["status"] == "DRAFT_NOT_SENT" for r in plan)
assert len(codes) == 69 and {"AUTO", "DBAUTO", "CRAUTO", "PAGO", "PGTR"} <= {r["movement_code"] for r in codes}
assert len(continuity) == 28
assert sum(r["continuity_class"] == "SAME_CODE_CHANGED_DESCRIPTION" for r in continuity) == 2
assert any(r["code_2013"] == "AUTO" and r["continuity_class"] == "SPLIT_BY_SIGN" for r in continuity)
assert len(accounts) == 19 and sum(r["account_or_equation"] == "230" for r in accounts) == 2
assert all("gastos bancarios" in r["official_function"] for r in accounts if r["account_or_equation"] == "230")
assert len(discriminators) == 15 and {"LIB", "APL", "EXB", "MAN"} <= {r["code_or_key"] for r in discriminators}
assert len(route) == 15 and any(r["layer"] == "Gasto bancario" for r in route)

assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V142.csv")) == 238
assert len(rows("E0_FISCAL_METHOD_BREAKS_V142.csv")) == 188
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V142.csv")) == 178
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V142.csv")) == 206

ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V142.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)
register = rows("E0_REQUEST_RESPONSE_REGISTER_V142.csv")
assert len(register) == 6 and all(r["status"] == "DRAFT_NOT_SENT" for r in register)
assert all(r["submitted_on"] == "N/A" and r["submission_channel"] == "N/A" and r["receipt_or_case_id"] == "N/A" for r in register)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V142.csv")}
new_ids = set()
assert len(census) == 198 and new_ids <= set(census)
for row in census.values():
    local = row["local_path"]
    assert local and (REPO / local.lstrip("/")).is_file(), (row["source_id"], local)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 438 and len({r["id"] for r in catalog}) == 438

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V142.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V142"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 432
assert complete["binary_required_entries"] == 369 and complete["binary_required_preserved"] == 368
assert complete["e0_siche_cut_period_start"] == 2007 and complete["e0_siche_cut_period_end"] == 2014
assert complete["e0_siche_cut_includes_2008"] is True
assert complete["e0_siche_cut_target_extract_rows_located"] == 0
assert complete["e0_siche_cut_target_impact_log_rows_located"] == 0
assert complete["e0_siche_named_queries_executed"] == 0
assert complete["e0_siche_target_exports_located"] == 0
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v142_strict_changed"] is False
assert complete["sources_newly_preserved_v142"] == 0
assert complete["e0_cut_event_code_rows"] == 69 and complete["e0_cut_code_continuity_rows"] == 28
assert complete["e0_cut_operation_account_rows"] == 19 and complete["e0_cut_discriminator_rows"] == 15
assert complete["e0_cut_reconciliation_route_rows"] == 15
assert complete["e0_cut_account_230_functional_continuity_2013_2022"] is True
assert complete["e0_cut_target_2008_code_dictionary_located"] is False

request = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V142.md").read_text(encoding="utf-8-sig")
assert "## Clave V142 · cuenta 230, códigos automáticos y conciliación" in request
assert all(term in request for term in ("AUTO", "DBAUTO", "CRAUTO", "LIB", "APL", "EXB", "MAN", "BORRADOR_NO_ENVIADO"))
refs = (HERE / "SOURCE_REFERENCES_V142.md").read_text(encoding="utf-8-sig")
assert refs.count("## Fuentes reexplotadas V142 · código CUT y conciliación") == 1
combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv")) + "\n" + request
assert "TARGET_EXTRACT_FOUND" not in combined and "TARGET_IMPACT_LOG_FOUND" not in combined
assert "REQUEST_SENT" not in combined
for name in ("README_V142.md", "VEREDICTO_V142.md", "E0_FISCAL_RECONSTRUCTION_V142.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V142_A_V143.md"):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "0/10" in text
assert "Ninguna consulta fue ejecutada ni enviada" in (HERE / "README_V142.md").read_text(encoding="utf-8-sig")

print("V142 QA PASS")
