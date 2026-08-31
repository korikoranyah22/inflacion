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

finddoc = rows("E0_COMDOC_FINDDOC_CAPABILITY_V134.csv")
assert len(finddoc) == 5 and finddoc[-1]["status"] == "TARGET_QUERY_UNEXECUTED_ADMINISTRATIVE_EXPORT_REQUIRED"
assert "origen" in finddoc[1]["output_schema"] and "fecha de recepción" in finddoc[1]["output_schema"]
comdoc = rows("E0_COMDOC_LEGACY_QUERY_ROUTE_V134.csv")
assert len(comdoc) == 5 and comdoc[-1]["body_query_executed"] == "NO"

c41 = rows("E0_C41_PAYMENT_EXECUTION_CHAIN_V134.csv")
assert len(c41) == 8 and c41[0]["stage"] == "C41_ISSUED" and c41[-1]["target_status"] == "OPEN"
assert "71597" in c41[-1]["required_or_visible_fields"]
bicameral = rows("E0_BICAMERAL_PUBLIC_INVENTORY_AUDIT_V134.csv")
assert len(bicameral) == 5 and bicameral[-1]["status"] == "EXACT_NOTE_BODY_OPEN"

assert len(rows("E0_EXPEDIENT_PUBLIC_SEARCH_EXHAUSTION_V134.csv")) == 10
assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V134.csv")) == 161
assert len(rows("E0_FISCAL_METHOD_BREAKS_V134.csv")) == 121
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V134.csv")) == 110
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V134.csv")) == 108
ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V134.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V134.csv")}
new_ids = {"e0_agenda_digital_finddoc_comdoc_architecture", "e0_agn_informe_254_2013_finddoc_control", "e0_cgn_circular_2_1997_c41_due_date", "e0_cgn_circular_13_2002_external_payments_c41", "e0_cgn_circular_6_1995_c41_tgn", "e0_cgn_circular_22_2004_c55_bank_debit", "e0_senado_bicameral_revisora_current_documents", "e0_hcdn_session_summary_2012_05_23_mass_archive"}
assert len(census) == 129 and new_ids <= set(census)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 369 and len({r["id"] for r in catalog}) == 369

expected = {
    "agenda_digital_argentina_2003_2011_br1018.pdf": (3550343, "1d76b6d563aea0d6dd7fa67e22a53b36e269849b3ef6ecd0508e8e16f156d68b"),
    "agn_informe_254_2013.pdf": (23877781, "99028db4627cc1190bab7d2282ae9330bca08846676b3bdf4cf4a64a969e23be"),
    "cgn_circular_13_2002_pagos_exterior.html": (9206, "88b09113bdbdb39ea9d90175d3c889e052c9d24649fdb4c38ecb7be35597357a"),
    "cgn_circular_2_1997_c41.html": (3126, "52ef4c74fdd4d9ff27bb694e9b0a01e60580054df22c02574669a5c274e0da29"),
    "cgn_circular_22_2004_c55.html": (8534, "626d6c57662055cc96756f9f203e843631f9ac9e5c144952e7ec7a8fe62cd3c7"),
    "cgn_circular_6_1995_c41_tgn.html": (15107, "9d6b17a57c0c394b51cc35adb59d8b95f33c5f32c8819b67b7353c82876e0fac"),
    "hcdn_sumario_reunion_8_23_mayo_2012.html": (77763, "de52eedd2056e896f8cc231fb5cc586218f22a2417c8f0cf810f80f9919d39c9"),
    "senado_bicameral_revisora_documentacion_actual.html": (152197, "597df2f9f87da7f828072189f21d65f7aa186e18e8318d0b50cfaa6ec7a15ff8"),
}
bin_dir = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v134" / "binaries"
assert len(list(bin_dir.iterdir())) == 8
for name, (size, digest) in expected.items():
    path = bin_dir / name
    assert path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest() == digest

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V134.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V134"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 363
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v134_strict_changed"] is False

for name, marker in {
    "REQUEST_AGN_2018_REPLY_V134.md": "## Clave V134 · inventario público y nota de archivo",
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V134.md": "## Clave V134 · salida FindDoc y cadena C-41",
}.items():
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert marker in text and "BORRADOR_NO_ENVIADO" in text

for name in ("README_V134.md", "VEREDICTO_V134.md", "E0_FISCAL_RECONSTRUCTION_V134.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V134_A_V135.md"):
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")

print("V134 QA PASS")
