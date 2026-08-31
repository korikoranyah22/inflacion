from pathlib import Path
import csv, hashlib, json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
AUDIT = REPO / "research" / "ciclo_ajuste" / "source_audit"

def rows(name):
    with (HERE / name).open(encoding="utf-8-sig", newline="") as handle: return list(csv.DictReader(handle))

def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024*1024), b""): value.update(chunk)
    return value.hexdigest()

new_ids = {
    "e0_argentina_resolution_6_2008_closing_original","e0_cgn_disposition_28_2008_intermediate_close","e0_cgn_disposition_38_1996_cut_account_3855","e0_cgn_disposition_38_1996_annex_cut_extracts","e0_mecon_uai_report_06_2019_saf355_close_2018","e0_mecon_uai_report_35_2019_saf355_change_close","e0_mecon_uai_report_37_2019_tgn_change_close","e0_mecon_uai_report_02_2019_tgn_close_2018","e0_argentina_resolution_257_2018_closing_original",
}
with (REPO / "data/fuentes/FUENTES.csv").open(encoding="utf-8-sig",newline="") as handle: catalog=list(csv.DictReader(handle))
assert len(catalog)==483 and len({r["id"] for r in catalog})==483 and new_ids <= {r["id"] for r in catalog}
census={r["source_id"]:r for r in rows("E0_LOCAL_PRIMARY_SOURCE_CENSUS_V149.csv")}; provenance={r["source_id"]:r for r in rows("ARCHIVAL_PROVENANCE_V149.csv")}
assert len(census)==243 and new_ids <= set(census) and new_ids <= set(provenance)
for sid in new_ids:
    path=REPO/census[sid]["local_path"].lstrip("/"); assert path.is_file() and digest(path)==census[sid]["sha256"]

closing=rows("E0_2008_CLOSING_FORM_AND_ARCHIVE_ROUTE_V149.csv"); intermediate=rows("E0_2008_INTERMEDIATE_FINAL_LIST_ROUTE_V149.csv"); last=rows("E0_UAI_LAST_FORM_CUT_SCHEMA_V149.csv"); sigade=rows("E0_UAI_SIGADE_BACKUP_CUSTODY_ROUTE_V149.csv"); tgn=rows("E0_TGN_BANK_CUT_OUTPUT_AND_NOTE_CHAIN_V149.csv"); cut=rows("E0_CUT_3855_HISTORICAL_CUSTODY_ROUTE_V149.csv"); dadp=rows("E0_DADP_BUYBACK_DOCUMENT_CUSTODY_V149.csv"); search=rows("E0_V149_EXACT_PUBLIC_SEARCH_V149.csv"); objects=rows("E0_V149_REQUEST_OBJECTS_V149.csv"); visual=rows("E0_V149_PDF_VISUAL_CONTROL.csv")
assert len(closing)==15 and all(r["target_payment_confirmed"]=="FALSE" for r in closing)
assert any(r["object"]=="ORIGINAL_SUPPORT" and r["status"]=="ORIGINAL_ARCHIVE_ROUTE_PROVED" for r in closing)
assert {"C41_DEADLINE","C55_REGULARIZATION"} <= {r["object"] for r in closing}
assert len(intermediate)==10 and {"H1_SEARCH","H2_SEARCH","TARGET_SPLIT"} <= {r["stage"] for r in intermediate}
assert len(last)==13 and {"C41","C55","CRG","SCHEMA","LIMIT"} <= {r["record_type"] for r in last}
assert len(sigade)==10 and any(r["status"]=="NAMED_CUSTODIAN_2019" for r in sigade) and all(r["target_2008_proof"]=="FALSE" for r in sigade)
assert len(tgn)==14 and {"TGN_NOTE","MODULE","NETWORK_PAYMENT","EXTRACT_DELAY"} <= {r["object"] for r in tgn}
assert len(cut)==14 and all(r["target_payment_confirmed"]=="FALSE" for r in cut)
assert any(r["element"]=="ACCOUNT" and r["status"]=="HISTORICAL_CONTINUITY_PROVED" for r in cut)
assert any(r["element"]=="LIMIT" and r["status"]=="TARGET_ACCOUNT_OPEN" for r in cut)
assert len(dadp)==8 and any(r["object"]=="CUSTODIAN" and r["status"]=="NAMED_CUSTODIAN_PROVED" for r in dadp) and all(r["target_commission_proved"]=="FALSE" for r in dadp)
assert len(search)==10 and sum(r["status"]=="EXACT_PUBLIC_REFERENCE_ROW_ONLY" for r in search)==5 and any(r["status"]=="CONTROLLED_NEGATIVE" for r in search)
assert len(objects)==20 and all(r["status"]=="DRAFT_NOT_SENT" for r in objects)
assert len(visual)==56 and all(r["result"]=="PASS" for r in visual)

repo={r["row_id"]:r for r in rows("E0_SICHE_CUT_HISTORICAL_REPOSITORY_V149.csv")}
assert repo["CR141_09"]["status"]=="HISTORICAL_ACCOUNT_CONTINUITY_PROVED_TARGET_USE_OPEN" and "no prueba" in repo["CR141_09"]["inference_limit"]
breaks=rows("E0_FISCAL_METHOD_BREAKS_V149.csv"); trace=rows("E0_INFORMATION_REQUEST_TRACEABILITY_V149.csv"); keys=rows("E0_REQUEST_SEARCH_KEY_MATRIX_V149.csv")
required={"target_support_originals_official_entity_archive_2008","c41_c55_closing_windows_not_target_type","midyear_final_lists_not_yearend_settlement","uai_held_2019_sigade_snapshot_not_2008_snapshot","last_form_cut_crosswalk_not_target_body","3855_historical_account_not_target_account","dual_extract_custody_not_preservation_proof","bank_extract_date_vs_process_date","repo_crg_cancellation_later_not_unrounded_target","buyback_dadp_custody_not_commission_identity"}
assert len(breaks)==241 and required <= {r["break_id"] for r in breaks}
assert len(trace)==280 and all(r["status"]=="DRAFT_NOT_SENT" for r in trace)
assert len(keys)==336 and {"Resolución SH 6/2008 artículo 8","3855/19","Listado Reporte Resumen de Pagos","archivo oficial de la entidad"} <= {r["exact_key"] for r in keys}

register=rows("E0_REQUEST_RESPONSE_REGISTER_V149.csv")
assert len(register)==6 and all(r["status"]=="DRAFT_NOT_SENT" and r["submitted_on"]=="N/A" and r["receipt_or_case_id"]=="N/A" for r in register)
for name in ["REQUEST_ECONOMIA_TESORO_SETTLEMENT_V149.md","REQUEST_BCRA_CRYL_SETTLEMENT_V149.md","REQUEST_BNA_FIRST_STAGE_BLOTTER_V149.md","REQUEST_AGN_2018_REPLY_V149.md","REQUEST_CNV_CUSTODY_RECORDS_V149.md","REQUEST_CAJA_SETTLEMENT_HOLDINGS_V149.md"]:
    text=(HERE/name).read_text(encoding="utf-8-sig"); assert "BORRADOR_NO_ENVIADO" in text or "DRAFT_NOT_SENT" in text

with (AUDIT/"MASTER_LOCAL_HASH_VALIDATION_V149.csv").open(encoding="utf-8-sig",newline="") as handle: hashes=list(csv.DictReader(handle))
assert sum(r["exists"]=="True" for r in hashes)==477 and sum(r["hash_ok"]=="True" for r in hashes)==477
complete=json.loads((AUDIT/"CURRENT_SOURCE_COMPLETENESS_V149.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"]=="V149" and complete["master_catalog_entries"]==483 and complete["e0_primary_sources_preserved"]==243
assert complete["physical_local_copies"]==complete["physical_local_hash_ok"]==477 and complete["remaining_physical_gaps"]==6
assert complete["e0_target_original_support_official_entity_archive_2008"] is True and complete["e0_2008_final_lists_conformity_adjustment_notes_proved"] is True
assert complete["e0_3855_historical_account_continuity_proved"] is True and complete["e0_3855_target_account_proved"] is False
assert complete["e0_uai_sigade_snapshot_custodian_2019"] is True and complete["e0_uai_sigade_snapshot_2008_proved"] is False
assert complete["e0_target_forms_public_bodies_located"]==0 and complete["e0_settlement_executed_rows_confirmed"]==0 and complete["e0_requests_submitted"]==0 and complete["e0_request_responses_received"]==0

manifest=json.loads((HERE/"MANIFEST_V149.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"]=="V149" and manifest["parent_checkpoint"]=="V148" and manifest["new_preserved_sources"]==9
assert manifest["target_original_support_official_entity_archive_2008"] is True and manifest["historical_account_3855_continuity_proved"] is True and manifest["target_account_3855_proved"] is False
assert manifest["target_forms_public_bodies_located"]==0 and manifest["executed_settlement_rows_confirmed"]==0 and manifest["requests_submitted"]==0 and manifest["responses_received"]==0
for name in ["README_V149.md","VEREDICTO_V149.md","E0_FISCAL_RECONSTRUCTION_V149.md","HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V149_A_V150.md"]: assert "0/10" in (HERE/name).read_text(encoding="utf-8-sig")
assert not list(HERE.glob("*V148*")) and not (HERE/"HANDOVER_PROXIMA_SESION_CICLO_AJUSTE_V149_A_V149.md").exists()
combined="\n".join(path.read_text(encoding="utf-8-sig") for path in HERE.glob("*.csv")); assert "REQUEST_SENT" not in combined and "TARGET_EXTRACT_FOUND" not in combined
print("V149 QA PASS")
