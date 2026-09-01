from pathlib import Path
import csv
import gzip
import hashlib


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
CATALOG = REPO / "data" / "fuentes" / "FUENTES.csv"
EXPECTED = {
    "sigen_planannual_generic_cc_20081006_v167": ("aa4b44de448d93e9fb0e79533439c2ed1df7b6a11896fa20fef6483672219a21", 4619, "Plan Sigen 2007"),
    "sigen_planannual_2008_cc_20080705_v167": ("6506ba4ecb9b28d463d45bc62108ba06225704234c2f27da43eba3cbbe6fe444", 4978, "Plan Sigen 2008"),
}


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
assert len(catalog) == 587 and len({row["id"] for row in catalog}) == 587
catalog_by_id = {row["id"]: row for row in catalog}
for source_id, (expected_sha, expected_bytes, token) in EXPECTED.items():
    row = catalog_by_id[source_id]
    path = REPO / row["archivo_local"].lstrip("/")
    assert path.is_file() and path.stat().st_size == expected_bytes
    assert row["sha256"] == expected_sha and digest(path) == expected_sha
    with gzip.open(path, "rb") as handle:
        text = handle.read().decode("cp1252", errors="replace")
    assert token in text and "http://www.sigen.gov.ar/plananual" in text

manifest = rows(HERE / "SOURCE_SYNC_FILE_MANIFEST_V167.csv")
assert len(manifest) == 2 and {row["sha256"] for row in manifest} == {value[0] for value in EXPECTED.values()}
assert all(row["format_verification"] == "GZIP_MAGIC_ARC_RECORD_DECOMPRESSED_AND_CONTENT_ASSERTED" for row in manifest)
endpoints = rows(HERE / "SOURCE_SYNC_PUBLIC_ENDPOINTS_V167.csv")
assert len(endpoints) == 9
assert endpoints[-1]["classification"] == "SERVICE_UNAVAILABLE_NOT_NEGATIVE"

print("V167 SOURCE SYNC QA PASS · 2 ARC records decompressed, content-asserted and SHA-valid")
