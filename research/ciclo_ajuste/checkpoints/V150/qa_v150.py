from pathlib import Path
import csv, hashlib, json

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
AUDIT=REPO/"research"/"ciclo_ajuste"/"source_audit"

def rows(name):
    with (HERE/name).open(encoding="utf-8-sig",newline="") as handle: return list(csv.DictReader(handle))

def digest(path):
    value=hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b""): value.update(chunk)
    return value.hexdigest()

new_ids={
    "e0_mecon_resolution_sh_47_1996_c42_authorization",
    "e0_cgn_disposition_52_1996_c42_debt_payment",
    "e0_cgn_disposition_52_1996_c42_instructions",
    "e0_cgn_disposition_52_1996_c42_procedure",
    "e0_cgn_disposition_52_1996_c42_form",
    "e0_cgn_disposition_52_1996_c42_flow",
    "e0_cgn_circular_16_1996_c42_presentation",
    "e0_argentina_resolution_81_2012_original_expense_circuit",
}
with (REPO/"data/fuentes/FUENTES.csv").open(encoding="utf-8-sig",newline="") as handle: catalog=list(csv.DictReader(handle))
assert len(catalog)==491 and len({r["id"] for r in catalog})==491 and new_ids<={r["id"] for r in catalog}
census={r["source_id"]:r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V150.csv")}
provenance={r["source_id"]:r for r in rows("ARCHIVAL_PROVENANCE_V150.csv")}
assert len(census)==251 and new_ids<=set(census) and new_ids<=set(provenance)
for sid in new_ids:
    path=REPO/census[sid]["local_path"].lstrip("/")
    assert path.is_file() and digest(path)==census[sid]["sha256"]

bundle=rows("E0_C42_SOURCE_BUNDLE_V150.csv")
assert len(bundle)==11 and all(r["preserved"]=="YES" for r in bundle)
for row in bundle:
    path=REPO/"research/ciclo_ajuste/inputs/historical_retrieval/v150/binaries"/row["filename"]
    assert path.is_file() and digest(path)==row["sha256"] and path.stat().st_size==int(row["bytes"])

branch=rows("E0_C42_1996_2008_TARGET_BRANCH_V150.csv")
assert len(branch)==18 and all(r["target_payment_confirmed"]=="FALSE" for r in branch)
assert {"OPERATIVE_2008","SEVEN_DIGIT","SPECIAL_ROUTE","TARGET_GAP"}<={r["object"] for r in branch}
assert any(r["status"]=="PUBLIC_BODY_NOT_LOCATED" for r in branch)
fields=rows("E0_C42_FIELD_AND_CUSTODY_MAP_V150.csv")
assert len(fields)==22 and {"BENEFICIARY_ACCOUNT","RESPONSIBLE_ACCOUNT","SIGADE_NUMBER","TGN_PAYMENT"}<={r["field_or_record"] for r in fields}
assert sum(r["payment_proof_alone"]=="YES_IF_COMPLETE_CHAIN" for r in fields)==1
padded=rows("E0_C42_ZERO_PADDED_KEY_MATRIX_V150.csv")
assert len(padded)==12 and {"0071597","0152677","0002876"}<={r["seven_digit_variant"] for r in padded}
assert all(r["status"] in {"SEARCH_KEY_ONLY","TYPE_OPEN"} for r in padded)
tree=rows("E0_THREE_PAYMENT_MECHANISM_DECISION_TREE_V150.csv")
assert len(tree)==15 and {"C41","C42","C55","ALL"}=={r["branch"] for r in tree} and all(r["target_status"]=="OPEN" for r in tree)
cross=rows("E0_RES81_LEGACY_TO_ESIDIF_CROSSWALK_V150.csv")
assert len(cross)==12 and all("posterior" in r["temporal_break"] for r in cross)
visual=rows("E0_V150_IMAGE_VISUAL_CONTROL.csv")
assert len(visual)==3 and all(r["result"]=="PASS" for r in visual)
negative=rows("E0_V150_PUBLIC_SEARCH_NEGATIVE_RESULTS_V150.csv")
assert len(negative)==10 and sum(r["status"]=="PUBLIC_BODY_NOT_LOCATED" for r in negative)==8
objects=rows("E0_V150_REQUEST_OBJECTS_V150.csv")
assert len(objects)==18 and all(r["status"]=="DRAFT_NOT_SENT" for r in objects)

breaks=rows("E0_FISCAL_METHOD_BREAKS_V150.csv")
trace=rows("E0_INFORMATION_REQUEST_TRACEABILITY_V150.csv")
keys=rows("E0_REQUEST_SEARCH_KEY_MATRIX_V150.csv")
required={
    "c42_public_debt_branch_operative_2008_not_target_type",
    "c42_expiration_at_close_not_nonpayment_proof",
    "c42_sidif_7digit_zero_padding_not_identity_proof",
    "c42_paper_screen_transaf_chain_not_payment",
    "c42_beneficiary_bank_not_financing_account",
    "circular16_general_route_excludes_saf355",
    "res81_esidif_crosswalk_not_2008_schema",
    "c42_then_c55_regularization_not_double_payment",
}
assert len(breaks)==249 and required<={r["break_id"] for r in breaks}
assert len(trace)==295 and all(r["status"]=="DRAFT_NOT_SENT" for r in trace)
assert len(keys)==351 and {"0071597","0152677","0002876","C-42","TRANSAF","SIGADE"}<={r["exact_key"] for r in keys}

register=rows("E0_REQUEST_RESPONSE_REGISTER_V150.csv")
assert len(register)==6 and all(r["status"]=="DRAFT_NOT_SENT" and r["submitted_on"]=="N/A" and r["receipt_or_case_id"]=="N/A" for r in register)
for name in ["REQUEST_ECONOMIA_TESORO_SETTLEMENT_V150.md","REQUEST_BCRA_CRYL_SETTLEMENT_V150.md","REQUEST_BNA_FIRST_STAGE_BLOTTER_V150.md","REQUEST_AGN_2018_REPLY_V150.md","REQUEST_CNV_CUSTODY_RECORDS_V150.md","REQUEST_CAJA_SETTLEMENT_HOLDINGS_V150.md"]:
    text=(HERE/name).read_text(encoding="utf-8-sig")
    assert "BORRADOR_NO_ENVIADO" in text or "DRAFT_NOT_SENT" in text

with (AUDIT/"MASTER_LOCAL_HASH_VALIDATION_V150.csv").open(encoding="utf-8-sig",newline="") as handle: hashes=list(csv.DictReader(handle))
assert sum(r["exists"]=="True" for r in hashes)==485 and sum(r["hash_ok"]=="True" for r in hashes)==485
complete=json.loads((AUDIT/"CURRENT_SOURCE_COMPLETENESS_V150.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"]=="V150" and complete["master_catalog_entries"]==491 and complete["e0_primary_sources_preserved"]==251
assert complete["physical_local_copies"]==complete["physical_local_hash_ok"]==485 and complete["remaining_physical_gaps"]==6
assert complete["e0_c42_public_debt_branch_operative_2008"] is True and complete["e0_c42_target_form_type_proved"] is False
assert complete["e0_c42_legacy_sidif_7digit_numbering_proved"] is True and complete["e0_three_branch_payment_tree_active"] is True
assert complete["e0_c42_target_bodies_located"]==0 and complete["e0_target_forms_public_bodies_located"]==0
assert complete["e0_settlement_executed_rows_confirmed"]==0 and complete["e0_requests_submitted"]==0 and complete["e0_request_responses_received"]==0

manifest=json.loads((HERE/"MANIFEST_V150.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"]=="V150" and manifest["parent_checkpoint"]=="V149" and manifest["new_preserved_sources"]==8
assert manifest["c42_public_debt_branch_operative_2008"] is True and manifest["c42_target_form_type_proved"] is False
assert manifest["target_forms_public_bodies_located"]==0 and manifest["executed_settlement_rows_confirmed"]==0
assert manifest["requests_submitted"]==0 and manifest["responses_received"]==0
for name in ["README_V150.md","VEREDICTO_V150.md","E0_FISCAL_RECONSTRUCTION_V150.md","HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V150_A_V151.md"]:
    assert "0/10" in (HERE/name).read_text(encoding="utf-8-sig")
assert not list(HERE.glob("*V149*")) and not (HERE/"HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V150_A_V150.md").exists()
combined="\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined and "TARGET_EXTRACT_FOUND" not in combined
print("V150 QA PASS")
