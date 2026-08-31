from pathlib import Path
import re
import pdfplumber


path = Path("research/ciclo_ajuste/inputs/source_sync/v161/binaries/banco_rioja_eeff_fy2023.pdf")
terms = [
    "pase",
    "14.409.056",
    "14,409,056",
    "158.789",
    "14.250.267",
    "24.048.826",
    "24.207.615",
    "anexo q",
    "apertura de resultados",
    "banco central de la república argentina",
]
with pdfplumber.open(path) as pdf:
    print(f"pages={len(pdf.pages)}")
    for index, page in enumerate(pdf.pages, 1):
        text = page.extract_text() or ""
        normalized = text.lower()
        hits = [term for term in terms if term in normalized]
        if hits:
            print(f"\n--- PHYSICAL_PAGE {index} hits={hits} ---")
            lines = text.splitlines()
            for line_index, line in enumerate(lines):
                if any(term in line.lower() for term in terms):
                    start = max(0, line_index - 3)
                    end = min(len(lines), line_index + 7)
                    print("\n".join(lines[start:end]))
                    print("...")
