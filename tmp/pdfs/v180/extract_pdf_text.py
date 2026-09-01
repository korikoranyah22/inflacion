from pathlib import Path
from pypdf import PdfReader

source_dir = Path(r"C:\Github\inflacion\research\ciclo_ajuste\inputs\historical_retrieval\v180\binaries")
output_dir = Path(r"C:\Github\inflacion\tmp\pdfs\v180\agn_text")
output_dir.mkdir(parents=True, exist_ok=True)

for name in (
    "agn_res023_2005_fideicomisos_publicos.pdf",
    "agn_res160_2006_bid1192_ejercicio2005.pdf",
    "agn_res014_2010_bid1192_ejercicio2008.pdf",
    "bid_ar0127_informe_terminacion_proyecto.pdf",
    "bid_ar0127_evaluacion_intermedia.pdf",
    "bid_ar0127_propuesta_prestamo_407194.pdf",
):
    source = source_dir / name
    reader = PdfReader(source)
    parts = []
    for page_number, page in enumerate(reader.pages, start=1):
        parts.append(f"\n\n===== PDF PAGE {page_number} =====\n\n")
        parts.append(page.extract_text() or "")
    target = output_dir / f"{source.stem}.txt"
    target.write_text("".join(parts), encoding="utf-8")
    print(f"{name}\t{len(reader.pages)}\t{target.stat().st_size}")
