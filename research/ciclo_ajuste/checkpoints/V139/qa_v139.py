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

timeline = rows("E0_SICHE_DEPLOYMENT_CAPABILITY_TIMELINE_V139.csv")
comparators = rows("E0_83106000_DOCUMENT_TYPE_COMPARATORS_V139.csv")
reconciliation = rows("E0_BANK_COMMISSION_RECONCILIATION_SIGNATURE_V139.csv")
hypotheses = rows("E0_DOCUMENT_TYPE_HYPOTHESIS_BALANCE_V139.csv")
visual = rows("E0_V139_PDF_VISUAL_CONTROL.csv")
types = rows("E0_SLU_SIDIF_DOCUMENT_TYPE_NARROWING_V139.csv")
plan = rows("E0_SICHE_TARGET_QUERY_PLAN_V139.csv")
assert len(timeline) == 9 and len(comparators) == 10 and len(reconciliation) == 10
assert len(hypotheses) == 5 and len(visual) == 13 and all(r["result"] == "PASS" for r in visual)
assert len(types) == 7 and types[-1]["status"] == "DUAL_PRIORITY_NO_TARGET_PROOF"
assert {r["candidate"] for r in hypotheses} == {"C41", "C55", "C42", "C35", "UNCLASSIFIED"}
assert len(plan) == 10 and all(r["status"] == "DRAFT_NOT_SENT" for r in plan)
assert any("Conciliación Bancaria" in r["system"] for r in plan)

assert len(rows("E0_SIGADE_SIDIF_DISCLOSURE_LADDER_V139.csv")) == 29
assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V139.csv")) == 208
assert len(rows("E0_FISCAL_METHOD_BREAKS_V139.csv")) == 163
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V139.csv")) == 156
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V139.csv")) == 170

ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V139.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)
register = rows("E0_REQUEST_RESPONSE_REGISTER_V139.csv")
assert len(register) == 6 and all(r["status"] == "DRAFT_NOT_SENT" for r in register)
assert all(r["submitted_on"] == "N/A" and r["receipt_or_case_id"] == "N/A" for r in register)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V139.csv")}
new_ids = {'e0_dgsiaf_siche_deployment_2021_q2', 'e0_cgn_cuenta_inversion_2015_sdp', 'e0_dgsiaf_slu_system_description_v3', 'e0_cgn_cuenta_inversion_2013_sdp', 'e0_dgsiaf_siche_deployment_2020_q1', 'e0_dgsiaf_sidif_forms_decommission_2025', 'e0_cgn_cuenta_inversion_2014_sdp', 'e0_dgsiaf_siche_deployment_2020_q4'}
assert len(census) == 190 and new_ids <= set(census)
for row in census.values():
    local = row["local_path"]
    assert local and (REPO / local.lstrip("/")).is_file(), (row["source_id"], local)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 430 and len({r["id"] for r in catalog}) == 430

expected = {'argentina_dgsiaf_bulletin_2020_q1_siche.pdf': (353161, '926acc816b62f79eaca371b0e96d9a19a311a6e87b639db6808293c8c46d978d'), 'argentina_dgsiaf_bulletin_2020_q4_siche.pdf': (258310, '9f3406b988266b653715f1304290703ee56c212c65e275234805da7df8960917'), 'argentina_dgsiaf_bulletin_2021_q2_siche.pdf': (616928, 'cda39b14f258923bcca12c24f0863c949be12dac62dd631ae7c0dd8fed481e26'), 'argentina_dgsiaf_sidif_c35_c41_c55_decommission_2025.html': (33116, 'bf85256fefbfa1e64c0b52f98c1cc73d0d79412df4ca2843b30ede2cda37771b'), 'argentina_slu_system_description_v3.pdf': (2078779, 'b988cf5525df07966fa877c40baf8782a2ece70b50a33298168a45aa71cc228d'), 'cgn_cuenta_2011_separata_deuda_publica.pdf': (1105867, '2ccd64bcc4f439fd64788201563de3ff406b37a911ef7624a9f5d4594ac85111'), 'cgn_cuenta_2012_separata_deuda_publica.pdf': (3149094, '612f97761b950bfeb9bc12df21c6135ca3eb31a226cd6ed403a1569cc8ea4d4b'), 'cgn_cuenta_2013_separata_deuda_publica.pdf': (963610, 'a8a08355939622cec6d8b46ab8e5d4d17ee86081d915d71aa7660b262e4f7517'), 'cgn_cuenta_2014_separata_deuda_publica.pdf': (1071658, '20f413fd6a3585a041a8e7c49d3cf546e57f2de8f36d8d46e91e68738eee6fd0'), 'cgn_cuenta_2015_separata_deuda_publica.pdf': (1068951, 'cee3a13179a4dd162c2cbcefbc5b70ce2d15c793c540258210da0c3ddbe85d9c')}
bin_dir = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v139" / "binaries"
assert len(list(bin_dir.iterdir())) == 10
for name, (size, digest) in expected.items():
    path = bin_dir / name
    assert path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest() == digest
assert expected["cgn_cuenta_2011_separata_deuda_publica.pdf"][1] == census["e0_cgn_cuenta_inversion_2011_sdp"]["sha256"]
assert expected["cgn_cuenta_2012_separata_deuda_publica.pdf"][1] == census["e0_cgn_cuenta_inversion_2012_sdp"]["sha256"]

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V139.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V139"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 424
assert complete["e0_duplicate_recaptures_v139"] == 2
assert complete["e0_document_type_hypothesis_status"] == "DUAL_PRIORITY_NO_TARGET_PROOF"
assert complete["e0_sidif_target_document_types_located"] == 0
assert complete["e0_siche_target_exports_located"] == 0
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v139_strict_changed"] is False

request = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V139.md").read_text(encoding="utf-8-sig")
assert "## Clave V139 · capacidad SICHE demostrada y doble prioridad C-41/C-55" in request
assert "BORRADOR_NO_ENVIADO" in request and "Conciliación Bancaria" in request
combined = "\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv")) + request
for stale in ("recuperar tres C-41 2008", "Cuerpo y estado de tres formularios C-41 2008", "Búsqueda y copia de los tres cuerpos C-41", "C-41 71597;152677;2876", "DOCUMENT_CLASS_AND_CHAIN_PROVED_TARGET_BODIES_OPEN", "THREE_C41_APPLICABILITY_CONTROL"):
    assert stale not in combined, stale
assert "C-55 Débito Directo como hipótesis prioritaria" not in (HERE / "REQUEST_SUBMISSION_CHECKLIST_V139.md").read_text(encoding="utf-8-sig")
refs = (HERE / "SOURCE_REFERENCES_V139.md").read_text(encoding="utf-8-sig")
assert "## Fuentes nuevas V138 · SICHE, SLU y C-55" in refs
assert refs.count("## Fuentes nuevas V139 · capacidad SICHE, conciliación y comparadores 2013-2015") == 1
for name in ("README_V139.md", "VEREDICTO_V139.md", "E0_FISCAL_RECONSTRUCTION_V139.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V139_A_V140.md"):
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")

print("V139 QA PASS")
