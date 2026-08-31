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

finddoc = rows("E0_COMDOC_FINDDOC_CAPABILITY_V135.csv")
assert len(finddoc) == 5 and finddoc[-1]["status"] == "TARGET_QUERY_UNEXECUTED_ADMINISTRATIVE_EXPORT_REQUIRED"
assert "origen" in finddoc[1]["output_schema"] and "fecha de recepción" in finddoc[1]["output_schema"]
comdoc = rows("E0_COMDOC_LEGACY_QUERY_ROUTE_V135.csv")
assert len(comdoc) == 5 and comdoc[-1]["body_query_executed"] == "NO"

c41 = rows("E0_C41_PAYMENT_EXECUTION_CHAIN_V135.csv")
assert len(c41) == 12 and c41[0]["stage"] == "C41_ISSUED" and c41[-1]["target_status"] == "OPEN"
assert "71597" in c41[-1]["required_or_visible_fields"]
bicameral = rows("E0_BICAMERAL_PUBLIC_INVENTORY_AUDIT_V135.csv")
assert len(bicameral) == 7 and bicameral[-1]["status"] == "CONTEMPORANEOUS_CUSTODY_COMPARATOR_NOT_TARGET_RULE"

alignment = rows("E0_2008_ANEXO_K_VISUAL_ALIGNMENT_CONTROL_V135.csv")
assert len(alignment) == 4 and alignment[1]["sidif_ids"] == "71597;152677;2876"
assert alignment[2]["sidif_ids"] == "171761"
payment = rows("E0_SIDIF_PAID_BENEFICIARY_FILE_SCHEMA_V135.csv")
assert len(payment) == 8 and payment[2]["field_or_code"] == "P;R;A"
records = rows("E0_TGN_BCRA_2008_PAYMENT_RECORD_CLASSES_V135.csv")
assert len(records) == 6 and records[0]["direction"] == "TGN→BCRA"
custody = rows("E0_COMDOC_CUSTODY_AND_DEBT_INSTRUCTION_COMPARATOR_V135.csv")
assert len(custody) == 8 and custody[-1]["scope_status"] == "OTHER_DEBT_PROCEDURE_COMPARATOR"

assert len(rows("E0_EXPEDIENT_PUBLIC_SEARCH_EXHAUSTION_V135.csv")) == 13
assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V135.csv")) == 166
assert len(rows("E0_FISCAL_METHOD_BREAKS_V135.csv")) == 127
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V135.csv")) == 118
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V135.csv")) == 122
ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V135.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V135.csv")}
new_ids = {"e0_cgn_cuenta_inversion_2008_tomo_ii_tgn_system_files", "e0_cgn_tgn_disposicion_conjunta_47_10_2008_external_payments", "e0_cgn_circular_34_1997_sdpgb_paid_beneficiary_schema", "e0_tgn_circular_7_1997_daily_paid_files", "e0_economia_digesto_chapter_3_tgn_index", "e0_minplan_resolution_1522_2006_comdoc_custody", "e0_debt_joint_resolution_216_26_2008_instruction_chain", "e0_hcdn_historic_plenary_index_negative_control"}
assert len(census) == 137 and new_ids <= set(census)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 377 and len({r["id"] for r in catalog}) == 377

expected = {
    "cgn_circular_34_1997_archivo_pagado_beneficiario.html": (23844, "d4019e3d1fb5ed2a426ab729e5c2512ff23a7eabc52d41fd910a0ae0a56fdd64"),
    "cgn_cuenta_inversion_2008_tomo_ii.pdf": (3450121, "a4047cec54c88efeff97d5f6602c45277cd4e813c71f3df1d8bab45dd40594ae"),
    "cgn_tgn_disposicion_conjunta_47_10_2008_pagos_exterior.html": (10869, "785381b2ae7ce14970b6f609264ba6a06a05e07aebd3645bcf163a2a49370874"),
    "deuda_resolucion_conjunta_216_26_2008_comdoc_instruccion.html": (59049, "f040e86ae5a1aa18ce11467d70b1559bb2a820303ad0912aab6c159fd280ab47"),
    "economia_digesto_capitulo_3_indice.html": (40882, "52d810ec5efffaaf3fbef071e2683648dcfce2398553a10ec5f64ad6d4142ea2"),
    "hcdn_indice_reuniones_historicas.html": (3653023, "ead063451f983ba1eff810c28dd1330c968684470a73aca8181226c2d106df3b"),
    "minplan_resolucion_1522_2006_comdoc_custodia.html": (93449, "fda42ee250f8989a97122e38ef7c7e4a3527e1de46afeeb9696dceb2ed04f0e9"),
    "tgn_circular_7_1997_pagado_diario.html": (3362, "b24b54c462369508e47ead79c87b11618ac7796c581b3b5775658fdc6a40105e"),
}
bin_dir = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v135" / "binaries"
assert len(list(bin_dir.iterdir())) == 8
for name, (size, digest) in expected.items():
    path = bin_dir / name
    assert path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest() == digest

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V135.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V135"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 371
assert complete["e0_c41_target_payment_state_rows_located"] == 0
assert complete["e0_sidif_payment_state_schema_rows"] == 8
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v135_strict_changed"] is False

for name, marker in {
    "REQUEST_AGN_2018_REPLY_V135.md": "## Clave V135 · inventario público y nota de archivo",
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V135.md": "## Clave V135 · salida FindDoc y cadena C-41",
}.items():
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert marker in text and "BORRADOR_NO_ENVIADO" in text

for name in ("README_V135.md", "VEREDICTO_V135.md", "E0_FISCAL_RECONSTRUCTION_V135.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V135_A_V136.md"):
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")

print("V135 QA PASS")
