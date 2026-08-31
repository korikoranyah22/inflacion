"""Extract CNV attachment metadata embedded in archived public-view pages."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BINARY_DIR = ROOT / "binaries"
PROPERTY_RE = re.compile(
    r'<propiedad\s+id="([^"]+)"[^>]*uploader="[^"]+"[^>]*>(\[.*?\])</propiedad>',
    re.DOTALL,
)


def main() -> None:
    pages = sorted(BINARY_DIR.glob("cnv_*_publicview.html"))
    print(f"pages={len(pages)}")
    for page in pages:
        source = page.read_text(encoding="utf-8", errors="replace")
        count = 0
        for match in PROPERTY_RE.finditer(source):
            try:
                attachments = json.loads(html.unescape(match.group(2)))
            except json.JSONDecodeError:
                continue
            for attachment in attachments:
                if not isinstance(attachment, dict) or not attachment.get("guid"):
                    continue
                fields = (
                    page.name,
                    match.group(1),
                    attachment.get("nombreArchivo", ""),
                    attachment.get("guid", ""),
                    attachment.get("tamano", ""),
                    attachment.get("hash", ""),
                )
                print(" | ".join(str(field) for field in fields))
                count += 1
        print(f"attachments={count} page={page.name}")


if __name__ == "__main__":
    main()
