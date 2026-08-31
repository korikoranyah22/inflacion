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

named = rows("E0_SICHE_NAMED_QUERY_TARGET_MAP_V140.csv")
crosswalk = rows("E0_SIGADE_PAYMENT_ATTRIBUTE_CROSSWALK_V140.csv")
runbook = rows("E0_EXACT_SICHE_QUERY_RUNBOOK_V140.csv")
zero = rows("E0_QUERY_ZERO_RESULT_INTERPRETATION_V140.csv")
visual = rows("E0_V140_PDF_VISUAL_CONTROL.csv")
plan = rows("E0_SICHE_TARGET_QUERY_PLAN_V140.csv")
assert len(named) == 10
assert named[0]["query_name"] == "Formulario por Pda. Presupuestaria y Sigade"
assert named[0]["target_input"] == "7.2.8;83106000;ejercicio2008;SAF355"
assert all("NOT_RUN" in r["status"] or r["status"].endswith("TARGET_ROWS_OPEN") for r in named)
assert len(crosswalk) == 10
assert {"EPP", "PG", "NPG", "CMR-DP", "TCE/RTCE"} <= {r["record"] for r in crosswalk}
assert all("LEGACY" in r["status"] or "NOT_TARGET_ROUTE" in r["status"] for r in crosswalk)
assert len(runbook) == 12 and all(r["status"] == "DRAFT_NOT_SENT" for r in runbook)
assert len(zero) == 8 and all(r["status"] == "FROZEN" for r in zero)
assert all("pag" in r["zero_forbids"].casefold() or r["rule_id"] not in {"ZR140_01", "ZR140_03", "ZR140_05"} for r in zero)
assert len(visual) == 2 and all(r["result"] == "PASS" for r in visual)
assert len(plan) == 10 and all(r["status"] == "DRAFT_NOT_SENT" for r in plan)

assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V140.csv")) == 218
assert len(rows("E0_FISCAL_METHOD_BREAKS_V140.csv")) == 171
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V140.csv")) == 164
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V140.csv")) == 182

ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V140.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)
register = rows("E0_REQUEST_RESPONSE_REGISTER_V140.csv")
assert len(register) == 6 and all(r["status"] == "DRAFT_NOT_SENT" for r in register)
assert all(r["submitted_on"] == "N/A" and r["submission_channel"] == "N/A" and r["receipt_or_case_id"] == "N/A" for r in register)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V140.csv")}
new_ids = {'e0_dgsiaf_siche_special_queries_2022_q3', 'e0_dgsiaf_esidif_line33_landing_2020', 'e0_dgsiaf_esidif_line33_sigade_payments_2020', 'e0_dgsiaf_execution_webservice_current'}
assert len(census) == 194 and new_ids <= set(census)
for row in census.values():
    local = row["local_path"]
    assert local and (REPO / local.lstrip("/")).is_file(), (row["source_id"], local)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 434 and len({r["id"] for r in catalog}) == 434

expected = {'argentina_dgsiaf_esidif_line33_landing_2020.html': (31448, '8467e602b9e94773099cbe6c2a271c9c9aa720b9c2381d31be249f78c888fc67'), 'argentina_dgsiaf_esidif_line33_sigade_payments_2020.pdf': (305243, 'fe4b2382623d04bd313422b9fb72593a4d1e9ce1b8906770d81b4639581ae319'), 'argentina_dgsiaf_execution_webservice.html': (30159, 'd33b4a32fff38b7479b4ce1528d8cff8ba7cf386196e74c80a983a6eed7c557d'), 'argentina_dgsiaf_siche_special_queries_2022_q3.html': (34162, 'a368fb11936b716c4a03b5c708edc9bac50ed70d883551f4ac00d56dd0b344f0')}
bin_dir = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v140" / "binaries"
assert len(list(bin_dir.iterdir())) == 4
for name, (size, digest) in expected.items():
    path = bin_dir / name
    assert path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest() == digest

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V140.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V140"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 428
assert complete["binary_required_entries"] == 365 and complete["binary_required_preserved"] == 364
assert complete["e0_siche_named_query_target_rows"] == 10
assert complete["e0_payment_sigade_crosswalk_rows"] == 10
assert complete["e0_exact_siche_query_runbook_rows"] == 12
assert complete["e0_siche_named_queries_executed"] == 0
assert complete["e0_sidif_target_document_types_located"] == 0
assert complete["e0_siche_target_exports_located"] == 0
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v140_strict_changed"] is False

request = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V140.md").read_text(encoding="utf-8-sig")
assert "## Clave V140 · consultas SICHE nombradas y runbook exacto" in request
assert "Formulario por Pda. Presupuestaria y Sigade" in request
assert "BORRADOR_NO_ENVIADO" in request and "resultado cero" in request
refs = (HERE / "SOURCE_REFERENCES_V140.md").read_text(encoding="utf-8-sig")
assert refs.count("## Fuentes nuevas V140 · consultas SICHE nombradas y SIGADE en Pagos") == 1
combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv")) + "\n" + request
assert "QUERY_EXECUTED_TARGET_FOUND" not in combined
assert "REQUEST_SENT" not in combined
for name in ("README_V140.md", "VEREDICTO_V140.md", "E0_FISCAL_RECONSTRUCTION_V140.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V140_A_V141.md"):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "0/10" in text
assert "ninguna consulta fue ejecutada" in (HERE / "README_V140.md").read_text(encoding="utf-8-sig")

print("V140 QA PASS")
