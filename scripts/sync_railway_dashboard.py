from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "railway-dashboard"
MAX_BUNDLE_BYTES = 25 * 1024 * 1024

PUBLIC_FILES = (
    "index.html",
    "assets/epica-super-tabs.js",
    "research/epica_dashito_2026/deep_dive_2026-08-31/derived/eph_exclusive_profiles.csv",
    "research/epica_dashito_2026/deep_dive_2026-08-31/derived/eph_strategy_summary.csv",
    "research/epica_dashito_2026/deep_dive_2026-08-31/derived/bcra_reserve_liquidity_bridge.csv",
    "research/epica_dashito_2026/deep_dive_2026-08-31/derived/debt_service_2026_2031.csv",
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/income_distribution_2026_q1.csv",
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/channel_comparison.csv",
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/policy_questions_matrix.csv",
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/source_manifest.csv",
)

STALE_PUBLIC_FILES = (
    "research/epica_dashito_2026/caputo_colchon_2026-08-31/derived/policy_claims_audit.csv",
)


def digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def main() -> None:
    for relative in STALE_PUBLIC_FILES:
        stale = BUNDLE / relative
        if stale.is_file():
            stale.unlink()

    manifest: list[dict[str, object]] = []
    for relative in PUBLIC_FILES:
        source = ROOT / relative
        target = BUNDLE / relative
        assert source.is_file(), f"Falta archivo público requerido: {source}"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        manifest.append(
            {
                "path": relative,
                "bytes": target.stat().st_size,
                "sha256": digest(target),
            }
        )

    total = sum(int(row["bytes"]) for row in manifest)
    assert total < MAX_BUNDLE_BYTES, f"El paquete creció demasiado: {total} bytes"
    payload = {
        "generated_from": "dashboard source tree",
        "public_file_count": len(manifest),
        "public_bytes": total,
        "files": manifest,
    }
    (BUNDLE / ".bundle-manifest.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"OK: paquete Railway sincronizado · {len(manifest)} archivos · {total / 1024 / 1024:.2f} MiB")


if __name__ == "__main__":
    main()
