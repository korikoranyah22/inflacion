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

authority = rows("E0_SICHE_LEGACY_QUERY_AUTHORITY_V138.csv")
types = rows("E0_SLU_SIDIF_DOCUMENT_TYPE_NARROWING_V138.csv")
c55 = rows("E0_C55_DIRECT_DEBIT_HYPOTHESIS_TEST_V138.csv")
foreign = rows("E0_FOREIGN_PAYMENT_COMMISSION_CHAIN_V138.csv")
schema = rows("E0_SLU_LEGACY_REPORT_EXPORT_SCHEMA_V138.csv")
plan = rows("E0_SICHE_TARGET_QUERY_PLAN_V138.csv")
assert len(authority) == 8 and authority[0]["status"] == "PROVED"
assert len(types) == 7 and types[1]["candidate"] == "C55_DIRECT_DEBIT"
assert types[1]["status"] == "PRIORITY_HYPOTHESIS_NOT_PROVED"
assert len(c55) == 12 and len(foreign) == 10 and len(schema) == 8 and len(plan) == 10
assert all(r["status"] == "DRAFT_NOT_SENT" for r in plan)
assert {r["report_or_function"] for r in schema} >= {"gastos_01.rep", "pagos_04.rep / F80", "conc_01.rep", "conc_02.rep"}

assert len(rows("E0_FISCAL_MECHANISM_LEDGER_V138.csv")) == 195
assert len(rows("E0_FISCAL_METHOD_BREAKS_V138.csv")) == 153
assert len(rows("E0_INFORMATION_REQUEST_TRACEABILITY_V138.csv")) == 148
assert len(rows("E0_REQUEST_SEARCH_KEY_MATRIX_V138.csv")) == 160
c41 = rows("E0_C41_PAYMENT_EXECUTION_CHAIN_V138.csv")
assert len(c41) == 34 and c41[-1]["stage"] == "TARGET_TYPE_AND_PAYMENT_CLOSE"

ladder = rows("E0_SETTLEMENT_EVIDENCE_LADDER_V138.csv")
assert len(ladder) == 10 and all(r["executed_settlement_status"] == "NOT_CONFIRMED" for r in ladder)

census = {r["source_id"]: r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V138.csv")}
new_ids = {'e0_cgn_tgn_disposition_47_10_2008_foreign_payments_annex', 'e0_dgsiaf_slu_payment_reports_2003', 'e0_cgn_account_2010_saf355_esidif_deployment', 'e0_dgsiaf_esidif_payment_queries_2013', 'e0_cgn_tgn_disposition_47_10_2008_foreign_payments', 'e0_cgn_circular_22_2004_note_regularization', 'e0_dgsiaf_slu_bank_reconciliation_reports_2002', 'e0_dgsiaf_esidif_payments_landing', 'e0_dgsiaf_slu_sidif_number_input_2003', 'e0_dgsiaf_siche_landing', 'e0_dgsiaf_slu_landing', 'e0_dgsiaf_slu_expense_reports_2003', 'e0_dgsiaf_slu_note_payment_2001', 'e0_cgn_circular_05_2000_c55_regularization', 'e0_cgn_circular_13_2002_foreign_payments', 'e0_dgsiaf_slu_payment_query_2004', 'e0_cgn_disposition_31_2006_parameterized_reports', 'e0_argentina_resolution_53_2024_siche', 'e0_dgsiaf_slu_global_regularization_2004'}
assert len(census) == 182 and new_ids <= set(census)
with (REPO / "data" / "fuentes" / "FUENTES.csv").open(encoding="utf-8-sig", newline="") as f:
    catalog = list(csv.DictReader(f))
assert len(catalog) == 422 and len({r["id"] for r in catalog}) == 422

expected = {'argentina_dgsiaf_siche_landing.html': (28514, 'b3b406e2fc8c877697c5079c9b5c93602cbeee4bb942687f50441cfb918d8643'), 'argentina_dgsiaf_slu_landing.html': (60179, '47cdbd46df0303a4ff3ba93a2ef5df7d596584843447d2c67cdd46f1520524a9'), 'argentina_esidif_consultas_reportes_pagos_2013.pdf': (933107, '85de6b2645a11b2001575be1e4afa71783598227707d7a80bc073eb1786696a3'), 'argentina_esidif_pagos_landing.html': (35485, '8854496b7955c45487a16750c66ecfa6541429a1239137467618a3e21de2be0a'), 'argentina_resolucion_53_2024_siche.pdf': (166521, '1ad76881f500202c2557df9164e1b77a1c7222f9e40a20d430174038041c4a47'), 'cgn_circular_05_2000_c55_regularization.html': (11277, '33ff6f2e0846d6ecddb3df183a4a48ee33aad0154a13538969c89cd63c78260a'), 'cgn_circular_13_2002_foreign_payments.html': (9206, '88b09113bdbdb39ea9d90175d3c889e052c9d24649fdb4c38ecb7be35597357a'), 'cgn_circular_22_2004_note_regularization.html': (8534, '626d6c57662055cc96756f9f203e843631f9ac9e5c144952e7ec7a8fe62cd3c7'), 'cgn_cuenta_2010_esidif_saf355_deployment.html': (58482, 'd0959a23bf1fd016f5ed38d07403201826b634613e55e4910680ab7c06848fc1'), 'cgn_disposition_31_2006_parameterized_reports.html': (16804, '3b54ab0cee1c6b0f3e1644f7f5eaf671fadc08758235f64444aea180189fa9df'), 'cgn_tgn_disposition_47_10_2008_foreign_payments_annex.html': (10869, '785381b2ae7ce14970b6f609264ba6a06a05e07aebd3645bcf163a2a49370874'), 'cgn_tgn_disposition_47_10_2008_foreign_payments.html': (8398, '3d318e6b41f02116cb9cd68560e65a048cb5fe167d6d87a0d594a23c8e9e25e8'), 'dgsiaf_slu_emite_consulta_pagos.doc': (161280, '05771a154e294999a86b4dc5c5f28429876e17e4c68adf15f1bfb060422d72cb'), 'dgsiaf_slu_gastos_ingreso_numero_sidif.doc': (313856, '7a04b63200dbe5503d98f8975f6a4eef0f4960ab5e80bf2004c8f1747c4f6a51'), 'dgsiaf_slu_nota_de_pago.doc': (996864, 'cbc3861a11178583cede1161ab1f43fbb9eb05d59c5a7c1069fbaec452834eb4'), 'dgsiaf_slu_regularizacion_global.doc': (617984, '389e2081612dfdad0efc4dba3355b993698fb0ea302ac3e42a32c8794c2b4f42'), 'dgsiaf_slu_reportes_conciliacion_bancaria.doc': (730624, '141cf858a16714cf282a4d823b77b823d57f7038b63cdf627b5ae33a98e2472e'), 'dgsiaf_slu_reportes_gastos.doc': (1448960, '9764c7ddff9ceeb2055f85e95b465ed8664ba16571df53fea0b1d78d1b5633a4'), 'dgsiaf_slu_reportes_pagos.doc': (1211392, '90ddd573ef7bd967ea4e89cf0852a3300dbd54abde913bee3050ee845af0b9d1')}
bin_dir = REPO / "research" / "ciclo_ajuste" / "inputs" / "historical_retrieval" / "v138" / "binaries"
assert len(list(bin_dir.iterdir())) == 19
for name, (size, digest) in expected.items():
    path = bin_dir / name
    assert path.stat().st_size == size and hashlib.sha256(path.read_bytes()).hexdigest() == digest

complete = json.loads((AUDIT / "CURRENT_SOURCE_COMPLETENESS_V138.json").read_text(encoding="utf-8"))
assert complete["checkpoint"] == "V138"
assert complete["physical_local_copies"] == complete["physical_local_hash_ok"] == 416
assert complete["e0_siche_unique_legacy_query_route_proved"] is True
assert complete["e0_c55_direct_debit_priority_hypothesis"] is True
assert complete["e0_sidif_target_document_types_located"] == 0
assert complete["e0_c55_target_rows_located"] == 0
assert complete["e0_settlement_executed_rows_confirmed"] == 0
assert complete["e0_requests_submitted"] == 0
assert complete["numeric_v138_strict_changed"] is False

request = (HERE / "REQUEST_ECONOMIA_TESORO_SETTLEMENT_V138.md").read_text(encoding="utf-8-sig")
assert "## Clave V138 · exportación SICHE y prueba C-55 por débito directo" in request
assert "BORRADOR_NO_ENVIADO" in request and "gastos_01.rep" in request and "conc_02.rep" in request
assert request.count("## Clave V138 · salida FindDoc y cadena C-41") == 1
assert "se solicitan los C-41 completos" not in request
register = rows("E0_REQUEST_RESPONSE_REGISTER_V138.csv")
assert len(register) == 6 and all(r.get("status") == "DRAFT_NOT_SENT" for r in register)
for name in ("README_V138.md", "VEREDICTO_V138.md", "E0_FISCAL_RECONSTRUCTION_V138.md", "HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V138_A_V139.md"):
    assert "0/10" in (HERE / name).read_text(encoding="utf-8-sig")

print("V138 QA PASS")
