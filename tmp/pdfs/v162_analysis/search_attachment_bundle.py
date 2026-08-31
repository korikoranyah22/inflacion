from pathlib import Path
import sys
import pdfplumber


sys.stdout.reconfigure(encoding="utf-8", errors="replace")
root = Path("research/ciclo_ajuste/inputs/source_sync/v161/binaries/cnv_attachments")
terms = ("pase", "sector financiero", "204.724.664", "68.481.253", "169.767", "542.204")
for path in sorted(root.rglob("*")):
    if (
        path.suffix.lower() != ".pdf"
        or not path.parent.name.startswith("hsbc_")
        or path.name in {"estado_contable.pdf", "informe_auditor_independiente.pdf", "informe_comision_fiscalizadora_sindico.pdf"}
    ):
        continue
    hits = []
    try:
        with pdfplumber.open(path) as pdf:
            for page_no, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                lines = text.splitlines()
                for index, line in enumerate(lines):
                    if any(term in line.lower() for term in terms):
                        context = " | ".join(lines[max(0, index - 1): min(len(lines), index + 2)])
                        hits.append((page_no, context))
    except Exception as exc:
        print(f"ERROR {path}: {exc}")
        continue
    print(f"\n### {path.as_posix()} hits={len(hits)}")
    for page_no, context in hits[:60]:
        print(f"p{page_no}: {context}")
