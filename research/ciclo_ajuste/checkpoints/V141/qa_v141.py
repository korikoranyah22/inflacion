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

repo = rows("E0_SICHE_CUT_HISTORICAL_REPOSITORY_V141.csv")
fields = rows("E0_CUT_EXTRACT_FIELD_CROSSWALK_V141.csv")
chain = rows("E0_CUT_AUDITOR_EVIDENCE_CHAIN_V141.csv")
runbook = rows("E0_CUT_TARGET_QUERY_RUNBOOK_V141.csv")
zero = rows("E0_CUT_ZERO_RESULT_AND_CONCILIATION_LIMITS_V141.csv")
visual = rows("E0_V141_PDF_VISUAL_CONTROL.csv")
plan = rows("E0_SICHE_TARGET_QUERY_PLAN_V141.csv")
assert len(repo) == 10
assert repo[1]["proved_scope"] == "incluye ejercicio 2008"
assert {"Entidades Básicas", "Saldos por Tipo de Apertura de Cuenta de Operación", "Extractos", "Logs de Impacto"} <= {r["evidence"] for r in repo}
assert len(fields) == 20
assert {"Cod. Mov.", "Comprobante Respaldo", "Comprobante Origen", "Comprobante Relacionado"} <= {r["source_field"] for r in fields}
assert all("2008" in r["legacy_status"] for r in fields)
assert len(chain) == 12 and any("diferencia" in r["proof"].casefold() for r in chain)
assert len(runbook) == 14 and all(r["status"] == "DRAFT_NOT_SENT" for r in runbook)
assert len(zero) == 8 and all(r["status"] == "FROZEN" for r in zero)
assert len(visual) == 6 and all(r["result"] == "PASS" for r in visual)
assert len(plan) == 12 and all(r["status"] == "DRAFT_NOT_SENT" for r in plan)

assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V141.csv")) == 228
assert len(rows("E0_FISCAL_METHOD_BREAKS_V141.csv")) == 180
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V141.csv")) == 172
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V141.csv")) == 194

ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V141.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)
register = rows("E0_REQUEST_RESPONSE_REGISTER_V141.csv")
assert len(register) == 6 and all(r["status"] == "DRAFT_NOT_SENT" for r in register)
assert all(r["submitted_on"] == "N/A" and r["submission_channel"] == "N/A" and r["receipt_or_case_id"] == "N/A" for r in register)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V141.csv")}
new_ids = {'e0_tgn_cut_auditor_instruction_2025', 'e0_dgsiaf_bulletin_2020_q2_landing', 'e0_dgsiaf_siche_cut_repository_2020_q2', 'e0_tgn_treasury_system_v3_2022_cut_extract'}
assert len(census) == 198 and new_ids <= set(census)
for row in census.values():
    local = row["local_path"]
    assert local and (REPO / local.lstrip("/")).is_file(), (row["source_id"], local)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 438 and len({r["id"] for r in catalog}) == 438

expected = {'argentina_dgsiaf_bulletin_2020_q2_landing.html': (31982, 'aa08a67cd5bb9fea508033b94686416cefde50773726eb590a5c264a4ca39701'), 'argentina_dgsiaf_bulletin_2020_q2_siche_cut_2007_2014.pdf': (334840, '6d70b056f5a2ecd5bdbf847ac9139866ec18c9a2136a7f364333c08f7e16fb20'), 'argentina_tgn_disposition_10_2025_cut_auditor.pdf': (1134786, '0b0382cfdfff7a7e1442789e3f0f2d83a3725b2d73e3582aacf93eee134cc669'), 'argentina_tgn_treasury_system_v3_2022.pdf': (2910883, '5ebd3991747b9c4af619b5208ee2047348ff34b7bc85aefc3f8a614509f53186')}
bin_dir = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v141" / "binaries"
assert len(list(bin_dir.iterdir())) == 4
for name, (size, digest) in expected.items():
    path = bin_dir / name
    assert path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest() == digest

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V141.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V141"
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
assert complete["numeric_v141_strict_changed"] is False

request = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V141.md").read_text(encoding="utf-8-sig")
assert "## Clave V141 · repositorio histórico CUT 2007-2014" in request
assert all(term in request for term in ("Entidades Básicas", "Extractos", "Logs de Impacto", "BORRADOR_NO_ENVIADO"))
refs = (HERE / "SOURCE_REFERENCES_V141.md").read_text(encoding="utf-8-sig")
assert refs.count("## Fuentes nuevas V141 · repositorio CUT histórico y Auditor") == 1
combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv")) + "\n" + request
assert "TARGET_EXTRACT_FOUND" not in combined and "TARGET_IMPACT_LOG_FOUND" not in combined
assert "REQUEST_SENT" not in combined
for name in ("README_V141.md", "VEREDICTO_V141.md", "E0_FISCAL_RECONSTRUCTION_V141.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V141_A_V142.md"):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "0/10" in text
assert "Ninguna consulta fue ejecutada ni enviada" in (HERE / "README_V141.md").read_text(encoding="utf-8-sig")

print("V141 QA PASS")
