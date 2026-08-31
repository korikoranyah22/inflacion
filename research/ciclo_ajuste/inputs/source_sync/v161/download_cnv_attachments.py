"""Archive every attachment exposed by six public CNV filing pages.

The AIF public-view frontend obtains a short-lived public valet key and then
submits it to CNV's blob service.  This script reproduces that public contract,
stores no valet keys, and records both the CNV-declared digest and the digest of
the bytes actually served.
"""

from __future__ import annotations

import base64
import csv
import hashlib
import html
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parent
BINARY_DIR = ROOT / "binaries"
ATTACHMENT_DIR = BINARY_DIR / "cnv_attachments"
MANIFEST = ROOT / "SOURCE_SYNC_CNV_ATTACHMENTS_V161.csv"

PUBLICVIEW_GUIDS = {
    "bma_9m2023": "9d3ded55-6d87-4ca2-9feb-920d961f3acd",
    "bma_fy2023": "36d0f59a-8e3f-42cd-bf18-db44e023f18d",
    "hsbc_9m2023": "d483d33a-5c86-4fbb-ab9c-6528bf43f572",
    "hsbc_fy2023": "39f37eb9-5637-4cb3-ab6b-715da7830bd1",
    "mariva_9m2023": "c23edd68-9bf4-4b3d-a1d8-9cde4770d45c",
    "mariva_fy2023": "d28fcf1a-28dc-465b-8478-aad95e0d4539",
}

PROPERTY_BASENAMES = {
    "ABEstadoContable": "estado_contable",
    "ABMemoria": "memoria",
    "ABInformeAuditorIndependiente": "informe_auditor_independiente",
    "ABInformeComisionFiscalizadoraSindico": "informe_comision_fiscalizadora_sindico",
    "ABResenaInformativa": "resena_informativa",
}

PROPERTY_RE = re.compile(
    r'<propiedad\s+id="([^"]+)"[^>]*uploader="[^"]+"[^>]*>(\[.*?\])</propiedad>',
    re.DOTALL,
)
CSRF_RE = re.compile(r'id="RequestVerificationToken"[^>]*value="([^"]+)"')


def sha256(data: bytes) -> tuple[str, str]:
    digest = hashlib.sha256(data).digest()
    return digest.hex(), base64.b64encode(digest).decode("ascii")


def valid_magic(path: Path) -> bool:
    data = path.read_bytes()[:8]
    if path.suffix.lower() == ".pdf":
        return data.startswith(b"%PDF-")
    if path.suffix.lower() == ".docx":
        return data.startswith(b"PK")
    return bool(data)


def extract(page: Path) -> list[tuple[str, dict[str, str]]]:
    source = page.read_text(encoding="utf-8", errors="replace")
    result: list[tuple[str, dict[str, str]]] = []
    for match in PROPERTY_RE.finditer(source):
        try:
            attachments = json.loads(html.unescape(match.group(2)))
        except json.JSONDecodeError:
            continue
        for attachment in attachments:
            if isinstance(attachment, dict) and attachment.get("guid"):
                result.append((match.group(1), attachment))
    return result


def fetch_attachment(
    session: requests.Session,
    publicview_url: str,
    csrf: str,
    blob_guid: str,
    target: Path,
) -> None:
    valet_url = (
        "https://aif2.cnv.gov.ar/api/ValetKeyProvider/GetPublicValetKey/"
        f"{blob_guid}?operation=DownloadBlob"
    )
    blob_url = f"https://blob.cnv.gov.ar/BlobWebService.svc/DownloadBlob/{blob_guid}"
    headers = {"Referer": publicview_url}
    for attempt in range(1, 4):
        try:
            valet_response = session.get(valet_url, headers=headers, timeout=60)
            valet_response.raise_for_status()
            valet_key = valet_response.json()["valetKeyData"]
            response = session.post(
                blob_url,
                data={"ValetKey": valet_key},
                headers={"Referer": publicview_url, "X-CSRF-TOKEN": csrf},
                timeout=180,
            )
            response.raise_for_status()
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_suffix(target.suffix + ".part")
            temporary.write_bytes(response.content)
            if not valid_magic(temporary):
                raise RuntimeError(f"unexpected file signature for {blob_guid}")
            temporary.replace(target)
            return
        except Exception:
            if attempt == 3:
                raise
            time.sleep(attempt * 2)


def main() -> None:
    rows: list[dict[str, str | int]] = []
    for key, publicview_guid in PUBLICVIEW_GUIDS.items():
        page = BINARY_DIR / f"cnv_{key}_publicview.html"
        publicview_url = (
            "https://aif2.cnv.gov.ar/presentations/publicview/" + publicview_guid
        )
        session = requests.Session()
        page_response = session.get(publicview_url, timeout=90)
        page_response.raise_for_status()
        csrf_match = CSRF_RE.search(page_response.text)
        if not csrf_match:
            raise RuntimeError(f"missing CSRF token on {publicview_url}")
        csrf = csrf_match.group(1)

        for property_id, attachment in extract(page):
            original_name = attachment["nombreArchivo"]
            extension = Path(original_name).suffix.lower() or ".bin"
            basename = PROPERTY_BASENAMES.get(property_id, property_id.lower())
            target = ATTACHMENT_DIR / key / f"{basename}{extension}"
            if not target.exists() or not valid_magic(target):
                fetch_attachment(
                    session,
                    publicview_url,
                    csrf,
                    attachment["guid"],
                    target,
                )
            data = target.read_bytes()
            digest_hex, digest_b64 = sha256(data)
            declared_b64 = attachment.get("hash", "")
            try:
                declared_hex = base64.b64decode(declared_b64).hex()
            except Exception:
                declared_hex = ""
            rows.append(
                {
                    "filing_key": key,
                    "publicview_url": publicview_url,
                    "archived_publicview": page.relative_to(ROOT).as_posix(),
                    "property_id": property_id,
                    "original_filename": original_name,
                    "declared_size": attachment.get("tamano", ""),
                    "blob_guid": attachment["guid"],
                    "cnv_declared_sha256_base64": declared_b64,
                    "cnv_declared_sha256_hex": declared_hex,
                    "local_path": target.relative_to(ROOT).as_posix(),
                    "size_bytes": len(data),
                    "served_sha256_base64": digest_b64,
                    "served_sha256_hex": digest_hex,
                    "declared_hash_matches_served_bytes": str(
                        bool(declared_b64) and declared_b64 == digest_b64
                    ).lower(),
                    "magic_valid": str(valid_magic(target)).lower(),
                    "archived_at_utc": datetime.now(timezone.utc).isoformat(),
                }
            )
            print(f"{key}: {property_id}: {len(data)} bytes")

    fieldnames = list(rows[0])
    with MANIFEST.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"manifest={MANIFEST} rows={len(rows)}")


if __name__ == "__main__":
    main()
