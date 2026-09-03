from __future__ import annotations

import hashlib
import json
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "railway-dashboard"
MAX_BUNDLE_BYTES = 25 * 1024 * 1024


def digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


manifest = json.loads((BUNDLE / ".bundle-manifest.json").read_text(encoding="utf-8"))
assert manifest["public_file_count"] == 140
assert manifest["public_bytes"] < MAX_BUNDLE_BYTES

for row in manifest["files"]:
    bundled = BUNDLE / row["path"]
    source = ROOT / row["path"]
    assert bundled.is_file(), f"Falta en el paquete: {bundled}"
    assert source.is_file(), f"Falta en el origen: {source}"
    assert bundled.stat().st_size == row["bytes"]
    assert digest(bundled) == row["sha256"]
    assert digest(bundled) == digest(source), f"Copia desactualizada: {bundled}"

assert (BUNDLE / "package.json").is_file()
assert (BUNDLE / "server.mjs").is_file()
assert (BUNDLE / "netlify.toml").is_file()
root_netlify = tomllib.loads((ROOT / "netlify.toml").read_text(encoding="utf-8"))
assert root_netlify["build"]["base"] == "railway-dashboard"
assert root_netlify["build"]["publish"] == "."
assert not (BUNDLE / "data").exists()
assert not (BUNDLE / "tmp").exists()
assert not (BUNDLE / "Mora").exists()
assert not (BUNDLE / "Reclamo colectivo").exists()
assert not (BUNDLE / "research" / "ciclo_ajuste").exists()
assert not (
    BUNDLE / "research" / "political_wealth_2026-09-01" / "sources"
).exists()
assert not (
    BUNDLE / "research" / "political_wealth_2026-09-01" / "derived" / "person_series.csv"
).exists()
assert not (
    BUNDLE / "research" / "political_wealth_2026-09-01" / "derived" / "political_group_coverage.csv"
).exists()
assert not (
    BUNDLE
    / "research"
    / "epica_dashito_2026"
    / "caputo_colchon_2026-08-31"
    / "derived"
    / "policy_claims_audit.csv"
).exists()

asset = (BUNDLE / "index.html").read_text(encoding="utf-8")
asset += (BUNDLE / "assets" / "epica-super-tabs.js").read_text(encoding="utf-8")
asset += (BUNDLE / "assets" / "epica-stage2-tabs.js").read_text(encoding="utf-8")
asset += (BUNDLE / "assets" / "political-wealth-tab.js").read_text(encoding="utf-8")
for row in manifest["files"]:
    relative = str(row["path"])
    if relative.startswith("research/"):
        assert f'href="{relative}"' in asset or f"'{relative}'" in asset, f"Descarga no enlazada: {relative}"

print(f"OK: paquete Railway autocontenido · {manifest['public_bytes'] / 1024 / 1024:.2f} MiB")
