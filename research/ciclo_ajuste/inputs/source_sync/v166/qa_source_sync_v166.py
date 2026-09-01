from pathlib import Path
import csv
import hashlib
import subprocess


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
SOURCE_ID = "bcra_entidades_jun2024_rioja_corrected_comparative_v166"
EXPECTED_SHA = "991ce57930183c65095c64c6a3abc44f02e419b5186f2287c78e9f7359763719"


def rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


catalog = rows(CATALOG)
assert len(catalog) == 585 and len({row["id"] for row in catalog}) == 585
source = next(row for row in catalog if row["id"] == SOURCE_ID)
source_path = REPO / source["archivo_local"].lstrip("/")
assert source_path.is_file() and source_path.stat().st_size == 6027314
assert source["sha256"] == EXPECTED_SHA and digest(source_path) == EXPECTED_SHA

manifest = rows(HERE / "SOURCE_SYNC_FILE_MANIFEST_V166.csv")
assert len(manifest) == 1
assert manifest[0]["relative_path"] == "/research/ciclo_ajuste/inputs/bcra/2024-06/informacion_entidades_financieras_open_data/202406e.pdf"
assert manifest[0]["sha256"] == EXPECTED_SHA and manifest[0]["size_bytes"] == "6027314"
assert manifest[0]["format_verification"] == "PDF_MAGIC_VALID_396_PAGES_PAGE261_VISUALLY_INSPECTED"

endpoints = rows(HERE / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V166.csv")
assert len(endpoints) == 4
assert endpoints[0]["result"] == "OFFICIAL_LATER_COMPARATIVE_LOCALLY_PRESERVED_AND_VISUALLY_VERIFIED"
assert all(row["decision"] == "PROMOTION_SUPPORT" for row in endpoints)

info = subprocess.run(["pdfinfo", str(source_path)], capture_output=True, text=True, errors="replace")
assert info.returncode == 0 and "Pages:           396" in info.stdout

print("V166 SOURCE SYNC QA PASS · 202406e.pdf catalogued, SHA-valid, 396 pages")
