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

cross = {r["crosswalk_id"]: r for r in rows("E0_AGN_PUBLIC_METADATA_CROSSWALK_V132.csv")}
assert len(cross) == 5
assert cross["CX132_02"]["status"] == "EXACT_FINAL_IDENTITY"
assert cross["CX132_05"]["status"] == "FINAL_IDENTITY_CLOSED_PROJECT_CODE_NOT_LITERAL"
assert len(rows("E0_AGN_2008_DEBT_AUDIT_PROJECT_BRIDGE_V132.csv")) == 6

quarterly = rows("E0_AGN_QUARTERLY_ANNEX_AVAILABILITY_V132.csv")
assert len(quarterly) == 3
assert quarterly[0]["status"] == "PUBLIC_ANNEX_RECOVERED"
assert all(r["status"] == "ANNEX_EXISTENCE_PROVED_PUBLIC_BODY_NOT_LOCATED" for r in quarterly[1:])

disclosure = rows("E0_SIGADE_SIDIF_DISCLOSURE_LADDER_V132.csv")
assert len(disclosure) == 14
assert sum(r["year"] == "2008" for r in disclosure) == 5
assert any(r["year"] == "2004" and r["disclosure_level"] == "ITEMIZED" for r in disclosure)
assert any(r["year"] == "2010" and r["sigade"] == "83106000" and r["disclosure_level"] == "ITEMIZED" for r in disclosure)

producer = rows("E0_ONCP_SIGADE_RECORD_PRODUCER_CONTROL_V132.csv")
assert len(producer) == 7
assert any(r["record_or_process"] == "I.f.2 Recompra de títulos" for r in producer)
assert any(r["record_or_process"] == "I.b.4 Revisión de una recompra de títulos" for r in producer)
assert len(rows("E0_EXPEDIENT_PUBLIC_SEARCH_EXHAUSTION_V132.csv")) == 4

public = {r["route_id"]: r for r in rows("E0_PUBLIC_SETTLEMENT_RECORD_EXHAUSTION_V132.csv")}
assert len(public) == 8
assert public["PE132_01"]["status"] == "PRODUCER_SYSTEM_CONFIRMED_EXPEDIENT_BODY_NOT_PUBLIC"
assert public["PE132_07"]["status"] == "FINAL_IDENTITY_CLOSED_PROJECT_CODE_CONTEXTUAL_NOT_LITERAL"

assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V132.csv")) == 154
assert len(rows("E0_FISCAL_METHOD_BREAKS_V132.csv")) == 114
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V132.csv")) == 101
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V132.csv")) == 90

ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V132.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)
summary = {r["stage"]: r for r in rows("E0_SETTLEMENT_EVIDENCE_LADDER_SUMMARY_V132.csv")}
assert summary["PUBLISHED_AWARD"]["closed_rows"] == "10"
assert summary["BCRA_ACCOUNT_CANDIDATE"]["closed_rows"] == "9"
assert summary["FINANCE_ORDER_BCRA_CREDIT"]["closed_rows"] == "0"

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V132.csv")}
assert len(census) == 118
new_ids = {
    "e0_agn_api_informe_res202_act41_2009", "e0_agn_res_202_2009_act_41_2009_resolution",
    "e0_agn_api_informe_3t_2009_res211", "e0_agn_res_211_2009_3t_activity",
    "e0_agn_api_informe_4t_2009_res44_2010", "e0_agn_res_44_2010_4t_activity",
    "e0_agn_2022_124_oncp_control_interno",
}
assert new_ids <= set(census)

with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 358 and len({r["id"] for r in catalog}) == 358

expected = {
    "agn_api_informe_res202_act41_2009.json": (13002, "8edcc3503af5f3ec0c380788dc70fe3276885e621ce37bfaf00f48f3baacdcfc"),
    "agn_res_202_2009_act_41_2009.pdf": (48191, "52a27534424d10eb631c9852d8ba35222d3448eeefaf583192c745d59d755589"),
    "agn_api_informe_3t_2009_res211.json": (10672, "001a311e62a2ead9649c5ffc0261c2691ed32eeb150388f298ab769ec1076aa5"),
    "agn_res_211_2009_3t_2009.pdf": (30951, "d8408f34fa88c2f4614fcdb30f8a2eed64d57e72f61526e2c886bddc68831b53"),
    "agn_api_informe_4t_2009_res044_2010.json": (10675, "c68a6035ac0bda2df5eb71608572943a0b00230f5fb62f1e1b18730be98ff677"),
    "agn_res_044_2010_4t_2009.pdf": (30142, "a02e317a61221b4b163ff3e2fcf2a4756414c25871abe4886fcc218cd1e38772"),
    "agn_2022_124_oncp_control_interno.pdf": (8305750, "4b61ce2dc5245268a4cb1858e023c202beb08a86425af3710c1a6ff963f9ccc4"),
}
bin_dir = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v132" / "binaries"
assert len(list(bin_dir.iterdir())) == 7
for name, (size, digest) in expected.items():
    path = bin_dir / name
    assert path.stat().st_size == size
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V132.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V132"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 352
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v132_strict_changed"] is False

for name, marker in {
    "REQUEST_AGN_2018_REPLY_V132.md": "## Clave V132 · identidad final cerrada y anexos trimestrales faltantes",
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V132.md": "## Clave V132 · productor, sistemas y formato de salida demostrados",
}.items():
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert marker in text and "BORRADOR_NO_ENVIADO" in text

for name in ("README_V132.md", "VEREDICTO_V132.md", "E0_FISCAL_RECONSTRUCTION_V132.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V132_A_V133.md"):
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert "0/10" in text and "48 0237/09" in text

print("V132 QA PASS")
