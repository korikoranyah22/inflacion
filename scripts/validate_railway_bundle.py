from __future__ import annotations

import hashlib
import json
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
assert manifest["public_file_count"] == 10
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
assert not (BUNDLE / "data").exists()
assert not (BUNDLE / "tmp").exists()
assert not (BUNDLE / "Mora").exists()
assert not (BUNDLE / "Reclamo colectivo").exists()
assert not (BUNDLE / "research" / "ciclo_ajuste").exists()

asset = (BUNDLE / "assets" / "epica-super-tabs.js").read_text(encoding="utf-8")
for row in manifest["files"]:
    relative = str(row["path"])
    if relative.startswith("research/"):
        assert f'href="{relative}"' in asset, f"Descarga no enlazada: {relative}"

print(f"OK: paquete Railway autocontenido · {manifest['public_bytes'] / 1024 / 1024:.2f} MiB")
