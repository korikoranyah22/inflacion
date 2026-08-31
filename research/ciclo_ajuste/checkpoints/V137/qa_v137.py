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

remit = rows("E0_AMIDDF_REMITTANCE_INDEX_SCHEMA_V137.csv")
assert len(remit) == 15 and remit[1]["target_value"].startswith("SAF 355")
assert remit[7]["official_field"] == "N° caja" and remit[7]["status"] == "OPEN_CRITICAL"
assert remit[8]["status"] == "OPEN_CRITICAL" and remit[9]["target_value"] == "71597;152677;2876"

custody = rows("E0_AMIDDF_CUSTODY_RESPONSIBILITY_ROUTE_V137.csv")
access = rows("E0_ACCESS_INFORMATION_LEGAL_FIT_V137.csv")
paper = rows("E0_C41_PAPER_OBLIGATION_TEMPORAL_MATRIX_V137.csv")
negative = rows("E0_FORM_SCOPE_NEGATIVE_CONTROLS_V137.csv")
first = rows("E0_TARGET_FIRST_STAGE_REQUEST_OBJECTS_V137.csv")
doctype = rows("E0_SIDIF_TARGET_DOCUMENT_TYPE_AUDIT_V137.csv")
stages = rows("E0_PAYMENT_STAGE_SEPARATION_V137.csv")
saf = rows("E0_SAF355_PRODUCER_CROSSWALK_V137.csv")
assert len(custody) == 10 and len(access) == 11 and len(paper) == 8
assert len(negative) == 4 and len(first) == 10 and len(doctype) == 5
assert len(stages) == 10 and len(saf) == 5
assert doctype[0]["status"] == "EXACT_LOCATORS_DOCUMENT_TYPE_OPEN"
assert any(r["stage"] == "DÉBITO_AUTOMÁTICO" for r in stages)
assert any(r["stage"] == "MEDIO_NOTA" for r in stages)

c41 = rows("E0_C41_PAYMENT_EXECUTION_CHAIN_V137.csv")
assert len(c41) == 25 and c41[0]["stage"] == "SIDIF_RECORD_REFERENCE"
assert c41[-1]["stage"] == "TARGET_BIFURCATED_CLOSE" and c41[-1]["target_status"] == "OPEN"
assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V137.csv")) == 182
assert len(rows("E0_FISCAL_METHOD_BREAKS_V137.csv")) == 141
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V137.csv")) == 136
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V137.csv")) == 146

ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V137.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V137.csv")}
new_ids = {
    "e0_cgn_disposition_46_1998_amiddf_procedure", "e0_cgn_disposition_46_1998_amiddf_annex",
    "e0_cgn_disposition_46_1998_amiddf_remittance_form", "e0_cgn_circular_30_1994_supporting_document_archive",
    "e0_cgn_circular_33_1995_paper_form_scope", "e0_cgn_disposition_28_2001_c43_negative_control",
    "e0_cgn_circular_16_2000_c43_negative_control", "e0_cgn_circular_19_1995_transaf_paper_timing",
    "e0_cgn_circular_05_2013_c41_paper_ordering", "e0_argentina_decree_1344_2007_original_finance_rule",
    "e0_argentina_law_27275_updated_access", "e0_argentina_economia_access_channel_2026",
    "e0_argentina_tad_public_information_route", "e0_tgn_manual_system_treasury_v1",
    "e0_cgn_account_2008_saf355_356_crosswalk",
}
assert len(census) == 163 and new_ids <= set(census)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 403 and len({r["id"] for r in catalog}) == 403

expected = {'argentina_decreto_1344_2007_texto_original.html': (160339, '255480068e5a0758c1f5ae42731ecab4dd09a926785ae8688f3e28705c23bca2'), 'argentina_economia_solicitud_informacion_publica_2026.html': (35830, 'aff6f649eb8eb0bb2308ba924c437d5b5d00660e19e0e37725b5be464618d03a'), 'argentina_ley_27275_texto_actualizado.html': (78213, '87843d5f34a283dce489d0a35e97f52a826a80783fb521226dbd1ff971d98bd8'), 'argentina_solicitar_informacion_publica_tad.html': (53363, '817890de7fbda959664cd66f35e318f62dfb758ba373794c7ae1619f03e10868'), 'cgn_circular_05_2013_c41_paper_ordering.html': (8399, '8be4a42e138fd550fd664001734bb9dbd3450e7a32f723a41aacb5468d91a214'), 'cgn_circular_16_2000_form_c_flows.html': (170076, '32af05052e4f0074a4eff9835bc6398510e99b5659974d98778fdfbb13a10642'), 'cgn_circular_19_1995_c41_transaf_paper_timing.html': (3581, '6c0899ca32f603eb0bb4f826d7cdcd87a174a14c43ab5f3902a55bcac9a16852'), 'cgn_circular_30_1994_valid_supporting_documentation.html': (24867, 'd855a80c08ba0832cfdf1ff724eb1316889901875fe4b95b2017fec54dcd88e5'), 'cgn_circular_33_1995_bna_bcra_external_payment_exception.html': (10058, '3a919aeb29ee25eef9aebb5fb90cd9bb49747e3ab1d3d7ee1dc934f545475458'), 'cgn_cuenta_2008_saf355_356_crosswalk.html': (53229, '3244a20ebf2356ad63422017bcd66be7eae2954fe8e3d8ff01ff1c6b9465b71a'), 'cgn_disposicion_28_2001_formulario_c_archive_flow.html': (42737, '9a4fea8dfae4512de3fce130815529d67f9a966fe545453187df84ec5ec71def'), 'cgn_disposicion_46_1998_amiddf_annex.html': (53282, '1fe54fe96949625a1f6df57a986bd036b1e34ecf21e4ca1e4cfa4df978a0f033'), 'cgn_disposicion_46_1998_amiddf_procedure.html': (5429, '3eeefabb14659306496238edd09d7e85ae2845160e01c3598f140f22967ccb59'), 'cgn_disposicion_46_1998_remittance_form.pdf': (42715, '43ede7a9afb026adaf06f081d72b815a68708b58062ad48a56e8cc4970cc2b4f'), 'tgn_manual_sistema_tesoreria_v1.pdf': (3102369, '3af4050e4d00f75ea0cbf49b3c8d84226b1debb58e65a39d167aaea65da02845')}
bin_dir = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v137" / "binaries"
assert len(list(bin_dir.iterdir())) == 15
for name, (size, digest) in expected.items():
    path = bin_dir / name
    assert path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest() == digest

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V137.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V137"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 397
assert complete["e0_target_producer_saf355_proved"] is True
assert complete["e0_sidif_target_document_types_located"] == 0
assert complete["e0_amiddf_target_box_located"] is False
assert complete["e0_automatic_debit_target_rows_located"] == 0
assert complete["e0_bcra_note_target_rows_located"] == 0
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v137_strict_changed"] is False

for name, marker in {
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V137.md": "## Clave V137 · productor exacto, índice AMIDDF y bifurcación de comisiones",
    "REQUEST_BNA_FIRST_STAGE_BLOTTER_V137.md": "## Clave V137 · eventual débito de comisiones",
    "REQUEST_BCRA_CRYL_SETTLEMENT_V137.md": "## Clave V137 · Archivos de Notas y acuses BCRA",
}.items():
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert marker in text and "BORRADOR_NO_ENVIADO" in text

assert all(r.get("status") == "DRAFT_NOT_SENT" for r in rows("E0_REQUEST_RESPONSE_REGISTER_V137.csv"))
for name in ("README_V137.md", "VEREDICTO_V137.md", "E0_FISCAL_RECONSTRUCTION_V137.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V137_A_V138.md"):
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")

print("V137 QA PASS")
