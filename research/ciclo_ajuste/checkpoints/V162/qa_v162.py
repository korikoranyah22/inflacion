from decimal import Decimal, getcontext
from pathlib import Path
import csv
import hashlib
import json
import subprocess

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
CYCLE=REPO/"research/ciclo_ajuste"
AUDIT=CYCLE/"source_audit"
CATALOG=REPO/"data/fuentes/FUENTES.csv"
FACTOR=Decimal("1.532908152197492")
EXPECTED=Decimal("63.3404130639287055191506606276878645985932518939916205138518528603403997357930830936917209159343409585184995437662731063")
getcontext().prec=120

def rows(path):
    with Path(path).open(encoding="utf-8-sig",newline="") as h:return list(csv.DictReader(h))

def digest(path):
    d=hashlib.sha256()
    with Path(path).open("rb") as h:
        for chunk in iter(lambda:h.read(1024*1024),b""):d.update(chunk)
    return d.hexdigest()

state=rows(HERE/"CURRENT_STATE_V162.csv")
by={r["entity"]:r for r in state}
assert sum(r["q4_four_leg_status"]=="EXACT" for r in state)==33
assert sum(r["strict_panel_status"]=="ELIGIBLE" for r in state)==33
assert by["Banco Rioja S.A.U."]["q4_four_leg_status"]=="N/D_STRICT_MISMATCH"
assert "14191142" in by["Banco Rioja S.A.U."]["nine_month_status"]
assert by["HSBC Bank Argentina S.A."]["q4_four_leg_status"]=="N/D_STRICT"
assert "SUPPLEMENTAL_BUNDLE_EXHAUSTED_V162" in by["HSBC Bank Argentina S.A."]["fy_status"]

recon=rows(HERE/"BANCO_RIOJA_STOCK_AND_RESULT_RECONCILIATION_V162.csv")
assert len(recon)==9
ri={r["control_id"]:r for r in recon}
assert ri["BR162_01"]["difference_issuer_minus_raw"]=="0"
assert ri["BR162_02"]["difference_issuer_minus_raw"]=="238183"
assert ri["BR162_03"]["difference_issuer_minus_raw"]=="158789"
assert Decimal(ri["BR162_07"]["raw_sum_thousand_ars"])==Decimal("5494064.165516943874708")
assert Decimal(ri["BR162_08"]["issuer_value_thousand_ars"])==Decimal("5652853.165516943874708")
assert Decimal(ri["BR162_09"]["issuer_value_thousand_ars"])==Decimal("0.108985205433436")
assert Decimal("14409056")-Decimal("5712151")*FACTOR==Decimal("5652853.165516943874708")

hsbc=rows(HERE/"HSBC_SUPPLEMENTAL_ATTACHMENT_EXHAUSTION_V162.csv")
assert len(hsbc)==8 and all(r["bcra_vs_otherfi_flow_split_found"]=="NO" for r in hsbc)
for r in hsbc:
    path=REPO/r["path"].lstrip("/")
    assert path.is_file() and digest(path)==r["sha256"]

panel=rows(HERE/"FOUR_LEG_PASS_PANEL_V162.csv")
assert sum(r["system_panel_eligible_v72"]=="YES_EXACT_Q4_TARGET_BASIS" for r in panel)==33
for entity in ("Banco Rioja S.A.U.","HSBC Bank Argentina S.A."):
    found=[r for r in panel if r["entity"]==entity]
    assert len(found)==1 and found[0]["system_panel_eligible_v72"]=="NO"
coverage=rows(HERE/"STRICT_Q4_FOUR_LEG_COVERAGE_V162.csv")
assert len(coverage)==1 and Decimal(coverage[0]["asset_coverage_pct"])==EXPECTED
assert Decimal(coverage[0]["asset_numerator_million_ars"])==Decimal("61248719.753")

visual=rows(HERE/"V162_PDF_VISUAL_CONTROL.csv")
assert len(visual)==5 and all(r["result"] in {"PASS","PASS_LIMIT"} for r in visual)
endpoints=rows(HERE/"V162_PUBLIC_SEARCH_LOG.csv")
assert len(endpoints)==4
assert sum("PENDING_SERVER_RESET" in r["local_status"] for r in endpoints)==2

catalog=rows(CATALOG)
assert len(catalog)==578 and len({r["id"] for r in catalog})==578
rioja=[r for r in catalog if r["id"]=="banco_rioja_disciplina_mercado_9m2023_v162"]
assert len(rioja)==1
for r in catalog:
    path=REPO/r["archivo_local"].lstrip("/")
    assert path.is_file() and digest(path)==r["sha256"].lower()
master=rows(AUDIT/"MASTER_LOCAL_HASH_VALIDATION_V162.csv")
assert len(master)==578 and all(r["exists"]=="True" and r["hash_ok"]=="True" for r in master)
assert not rows(AUDIT/"SOURCE_PRESERVATION_MISSING_V162.csv")
complete=json.loads((AUDIT/"CURRENT_SOURCE_COMPLETENESS_V162.json").read_text(encoding="utf-8-sig"))
assert complete["checkpoint"]=="V162" and complete["exact_entities"]==33
assert complete["master_catalog_entries"]==complete["physical_local_copies"]==complete["physical_local_hash_ok"]==578
assert complete["discovered_official_binary_recovery_queue"]==2
assert complete["request_drafts_status"]=="DRAFT_NOT_SENT"

dm=REPO/rioja[0]["archivo_local"].lstrip("/")
assert dm.read_bytes().startswith(b"%PDF-") and dm.stat().st_size==212506
info=subprocess.run(["pdfinfo",str(dm)],capture_output=True,text=True,errors="replace")
assert info.returncode==0 and "Pages:           9" in info.stdout

sync=rows(CYCLE/"inputs/source_sync/v162/SOURCE_SYNC_FILE_MANIFEST_V162.csv")
assert len(sync)==1
for r in sync:
    path=REPO/r["relative_path"].lstrip("/")
    assert path.is_file() and digest(path)==r["sha256"]

register=rows(HERE/"E0_REQUEST_RESPONSE_REGISTER_V162.csv")
assert len(register)==6 and all(r["status"]=="DRAFT_NOT_SENT" and r["submitted_on"]=="N/A" for r in register)
combined="\n".join(p.read_text(encoding="utf-8-sig") for p in HERE.glob("*.csv"))
assert "REQUEST_SENT" not in combined

manifest=json.loads((HERE/"MANIFEST_V162.json").read_text(encoding="utf-8-sig"))
assert manifest["checkpoint"]=="V162" and manifest["parent_checkpoint"]=="V161"
assert manifest["exact_entities"]==33 and manifest["new_promotions"]==[]
for item in manifest["files"]:
    path=HERE/item["path"]
    assert path.is_file() and path.stat().st_size==item["bytes"] and digest(path)==item["sha256"]

global_manifest=json.loads((CYCLE/"MANIFEST_SHA256.json").read_text(encoding="utf-8-sig"))
assert global_manifest["checkpoint"]=="V162" and global_manifest["exact_entities"]==33
assert global_manifest["file_count_excluding_manifest"]==len(global_manifest["files"])

print("V162 QA PASS")
print(f"catalog=578 local=578 hash_ok=578 exact_entities=33 coverage={EXPECTED}")
print("rioja_stock_bridge=EXACT result_mismatch=OPEN hsbc_supplemental=8_NO_SPLIT requests=0")
