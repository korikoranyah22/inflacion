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

parliament = rows("E0_AGN_PARLIAMENTARY_ARCHIVE_CROSSWALK_V133.csv")
assert len(parliament) == 2 and {r["senate_exp"] for r in parliament} == {"OV 366/09", "OV 44/10"}
assert all(r["archive_date"] == "2012-05-28" and r["original_text_public_state"] == "EN_PROCESO_DE_CARGA" for r in parliament)
quarterly = rows("E0_AGN_QUARTERLY_ANNEX_AVAILABILITY_V133.csv")
assert all("PARLIAMENTARY_EXPEDIENT" in r["status"] for r in quarterly[1:])
comdoc = rows("E0_COMDOC_LEGACY_QUERY_ROUTE_V133.csv")
assert comdoc[0]["test_result"] == "CONNECTION_REFUSED" and comdoc[0]["body_query_executed"] == "NO"
assert len(rows("E0_EXPEDIENT_PUBLIC_SEARCH_EXHAUSTION_V133.csv")) == 6

disclosure = rows("E0_SIGADE_SIDIF_DISCLOSURE_LADDER_V133.csv")
assert len(disclosure) == 24
assert sum(r["year"] == "2007" for r in disclosure) == 5
assert sum(r["year"] == "2009" and r["disclosure_level"] == "BLANK" for r in disclosure) == 5
transitions = rows("E0_SIGADE_SIDIF_TARGET_DISCLOSURE_TRANSITIONS_V133.csv")
assert len(transitions) == 5
assert next(r for r in transitions if r["sigade"] == "83020000")["transition"] == "ITEMIZED → AGGREGATED → BLANK → ITEMIZED"

assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V133.csv")) == 157
assert len(rows("E0_FISCAL_METHOD_BREAKS_V133.csv")) == 117
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V133.csv")) == 104
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V133.csv")) == 98
ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V133.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V133.csv")}
new_ids = {"e0_senado_exp_366_09_agn_res211_t3", "e0_senado_exp_44_10_agn_res44_t4", "e0_economia_consulta_expedientes_comdoc_gde"}
assert len(census) == 121 and new_ids <= set(census)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 361 and len({r["id"] for r in catalog}) == 361

expected = {
    "senado_exp_366_09_agn_res211_t3.html": (48711, "f74fbe0afdc64f2417b33812dbf68696df7b70e73b65b0fe1e4f2eb69720574c"),
    "senado_exp_44_10_agn_res44_t4.html": (48707, "b8ba499ccb21798d392d4c8e8499d51c6057bb076c6f8d41c08d773e201beed2"),
    "economia_consulta_expedientes_comdoc_gde.html": (35065, "ffa7137f0ff2405d504b64e06cc522420384400164d23838256bff443c3d4ec2"),
}
bin_dir = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v133" / "binaries"
assert len(list(bin_dir.iterdir())) == 3
for name, (size, digest) in expected.items():
    path = bin_dir / name
    assert path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest() == digest

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V133.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V133"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 355
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v133_strict_changed"] is False

for name, marker in {
    "REQUEST_AGN_2018_REPLY_V133.md": "## Clave V133 · remisión parlamentaria y archivo",
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V133.md": "## Clave V133 · ruta COMDOC y comparadores contiguos",
}.items():
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert marker in text and "BORRADOR_NO_ENVIADO" in text

for name in ("README_V133.md", "VEREDICTO_V133.md", "E0_FISCAL_RECONSTRUCTION_V133.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V133_A_V134.md"):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "0/10" in text

print("V133 QA PASS")
