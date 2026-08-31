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

finddoc = rows("E0_COMDOC_FINDDOC_CAPABILITY_V136.csv")
assert len(finddoc) == 5 and finddoc[-1]["status"] == "TARGET_QUERY_UNEXECUTED_ADMINISTRATIVE_EXPORT_REQUIRED"
assert "origen" in finddoc[1]["output_schema"] and "fecha de recepción" in finddoc[1]["output_schema"]
comdoc = rows("E0_COMDOC_LEGACY_QUERY_ROUTE_V136.csv")
assert len(comdoc) == 5 and comdoc[-1]["body_query_executed"] == "NO"

c41 = rows("E0_C41_PAYMENT_EXECUTION_CHAIN_V136.csv")
assert len(c41) == 17 and c41[0]["stage"] == "C41_ISSUED" and c41[-1]["target_status"] == "OPEN"
assert "71597" in c41[-1]["required_or_visible_fields"]
bicameral = rows("E0_BICAMERAL_PUBLIC_INVENTORY_AUDIT_V136.csv")
assert len(bicameral) == 7 and bicameral[-1]["status"] == "CONTEMPORANEOUS_CUSTODY_COMPARATOR_NOT_TARGET_RULE"

alignment = rows("E0_2008_ANEXO_K_VISUAL_ALIGNMENT_CONTROL_V136.csv")
assert len(alignment) == 4 and alignment[1]["sidif_ids"] == "71597;152677;2876"
assert alignment[2]["sidif_ids"] == "171761"
payment = rows("E0_SIDIF_PAID_BENEFICIARY_FILE_SCHEMA_V136.csv")
assert len(payment) == 8 and payment[2]["field_or_code"] == "P;R;A"
records = rows("E0_TGN_BCRA_2008_PAYMENT_RECORD_CLASSES_V136.csv")
assert len(records) == 6 and records[0]["direction"] == "TGN→BCRA"
custody = rows("E0_COMDOC_CUSTODY_AND_DEBT_INSTRUCTION_COMPARATOR_V136.csv")
assert len(custody) == 8 and custody[-1]["scope_status"] == "OTHER_DEBT_PROCEDURE_COMPARATOR"

timeline = rows("E0_SIDIF_ESIDIF_TEMPORAL_DEPLOYMENT_V136.csv")
assert len(timeline) == 11 and timeline[-1]["inference_status"].endswith("LITERAL_FILENAME_OPEN")
agan = rows("E0_AGAN_C41_ARCHIVAL_ROUTE_V136.csv")
assert len(agan) == 8 and agan[-1]["status"] == "PUBLISHED_CONTACT_NOT_VERIFIED_NOT_CONTACTED"
daily = rows("E0_DAILY_PAYMENT_SELECTION_RECORDS_V136.csv")
assert len(daily) == 7 and daily[-1]["temporal_status"].endswith("NON_REPEAL_ONLY")
partial = rows("E0_C41_PARTIAL_PAYMENT_EXPIRY_STATE_V136.csv")
assert len(partial) == 5 and partial[-1]["status"] == "REQUIRED_TO_CLOSE_EXECUTION"
external = rows("E0_C41_EXTERNAL_CLASSIFICATION_V136.csv")
assert len(external) == 4 and all(r["classification"] in {"OPEN", "EXTERNAL_PAYMENT_CLASSIFICATION_OPEN"} for r in external)

assert len(rows("E0_EXPEDIENT_PUBLIC_SEARCH_EXHAUSTION_V136.csv")) == 16
assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V136.csv")) == 172
assert len(rows("E0_FISCAL_METHOD_BREAKS_V136.csv")) == 133
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V136.csv")) == 126
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V136.csv")) == 132
ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V136.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V136.csv")}
new_ids = {"e0_agan_current_archive_services", "e0_amiddf_financial_document_images", "e0_cgn_circular_07_2008_transaf_entes_transition", "e0_cgn_account_2008_esidif_module_scope", "e0_cgn_account_2009_esidif_payments_development", "e0_cgn_account_2010_esidif_spending_rollout", "e0_cgn_account_2011_esidif_saf356_first_spending", "e0_cgn_disposition_20_2007_agan_quality", "e0_cgn_disposition_54_2008_order_expiry_partial", "e0_cgn_tgn_joint_disposition_13_16_2009_payment_records", "e0_agan_current_coordination_contact"}
assert len(census) == 148 and new_ids <= set(census)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 388 and len({r["id"] for r in catalog}) == 388

expected = {
    "argentina_agan_archivo_general_actual.html": (34804, "f2077fcaf5b8aa354ff64871e8a14cad8af069053d6562de1975e60328df6c51"),
    "argentina_amiddf_imagenes_documentacion_financiera.html": (43313, "2a82c85ded72c4a008463646d205d8e702227390d46c9b768c186c5ca804a692"),
    "cgn_circular_07_2008_transaf_entes.html": (17653, "abc3bacbef9b4d86adebc41256c7513fce69a841f6aa35228c27e44621c2f108"),
    "cgn_cuenta_2008_jur50_esidif_modules.html": (569635, "ce9f5e48de18c4aff2664afc368e71fea2f200507f93c03666dd4cd7b6eca3ac"),
    "cgn_cuenta_2009_aspectos_esidif_pagos.html": (55544, "2318e0f7dfb633f568b6f8dc589b03665846aec8e07caab2079783465ff4f5a0"),
    "cgn_cuenta_2010_aspectos_esidif_gastos.html": (58482, "d0959a23bf1fd016f5ed38d07403201826b634613e55e4910680ab7c06848fc1"),
    "cgn_cuenta_2011_jur50_esidif_gastos_saf356.html": (198342, "0e56b77da1c227d45e5850ff75efe65e08d5a030dcd6b3f1d4ae9c8fc9610754"),
    "cgn_disposicion_20_2007_agan_archivo_financiero.html": (15590, "fa157d8fe62b982b6d6e3df0a485462fe53e574f79fbfde577223d79c1a0d300"),
    "cgn_disposicion_54_2008_caducidad_ordenes.html": (37565, "cd3fb95b812bca412c07cfe9de72bbb29bca7f0c1ed2c35c6ff8adec2450497f"),
    "cgn_tgn_disposicion_13_16_2009_ordenes_pago.html": (13664, "42292773a13c2e42cfd4aa6c8652d47a8c95137429192fc65a52f4a56b9b4237"),
    "economia_agan_competencia_contacto.html": (3454, "01986c35b5439694cff2e793fa658141c47f0484a0154dc43aedd2afa366669d"),
}
bin_dir = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v136" / "binaries"
assert len(list(bin_dir.iterdir())) == 11
for name, (size, digest) in expected.items():
    path = bin_dir / name
    assert path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest() == digest

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V136.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V136"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 382
assert complete["e0_c41_target_payment_state_rows_located"] == 0
assert complete["e0_sidif_payment_state_schema_rows"] == 8
assert complete["e0_sidif_esidif_timeline_rows"] == 11
assert complete["e0_agan_archival_route_rows"] == 8
assert complete["e0_agan_target_holdings_located"] == 0
assert complete["e0_2008_legacy_sidif_environment_proved"] is True
assert complete["e0_2008_sdpgb_sdpag_literal_filename_proved"] is False
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v136_strict_changed"] is False

for name, marker in {
    "REQUEST_AGN_2018_REPLY_V136.md": "## Clave V136 · inventario público y nota de archivo",
    "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V136.md": "## Clave V136 · AGAN/AMIDDF, sistema productor y pago parcial",
}.items():
    text = (HERE / name).read_text(encoding="utf-8-sig")
    assert marker in text and "BORRADOR_NO_ENVIADO" in text

for name in ("README_V136.md", "VEREDICTO_V136.md", "E0_FISCAL_RECONSTRUCTION_V136.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V136_A_V137.md"):
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")

print("V136 QA PASS")
