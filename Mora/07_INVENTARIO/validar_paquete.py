from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def check_markdown_links() -> None:
    link_re = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    for document in ROOT.rglob("*.md"):
        text = document.read_text(encoding="utf-8")
        for target in link_re.findall(text):
            clean = target.split("#", 1)[0].strip()
            if not clean or clean.startswith(("http://", "https://", "mailto:")):
                continue
            if not (document.parent / clean).resolve().exists():
                errors.append(f"Enlace interno roto: {document.relative_to(ROOT)} -> {target}")


def check_legislative_sources() -> None:
    pdf_dir = ROOT / "02_PROYECTOS_LEGISLATIVOS"
    pdfs = sorted(pdf_dir.glob("*.pdf"))
    texts = sorted((pdf_dir / "texto_extraido").glob("*.txt"))
    if len(pdfs) != 23:
        errors.append(f"Se esperaban 23 proyectos PDF y hay {len(pdfs)}")
    if len(texts) != 23:
        errors.append(f"Se esperaban 23 textos extraídos y hay {len(texts)}")
    for pdf in pdfs:
        if pdf.read_bytes()[:4] != b"%PDF":
            errors.append(f"Firma PDF inválida: {pdf.name}")
        text = pdf_dir / "texto_extraido" / f"{pdf.stem}.txt"
        if not text.exists() or text.stat().st_size < 500:
            errors.append(f"Texto extraído ausente o demasiado corto: {pdf.name}")


def check_link_register() -> None:
    path = ROOT / "06_FUENTES_WEB" / "REGISTRO_DE_ENLACES.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 38:
        errors.append(f"El documento base tenía 38 enlaces; el registro contiene {len(rows)}")


def check_articles() -> None:
    path = ROOT / "00_PROYECTO_DE_LEY" / "PROYECTO_DE_LEY_PROTECCION_HOGARES_Y_SEGUNDA_OPORTUNIDAD_V1.md"
    text = path.read_text(encoding="utf-8")
    numbers = [int(value) for value in re.findall(r"^### Artículo (\d+)", text, flags=re.MULTILINE)]
    expected = list(range(1, 87))
    if numbers != expected:
        errors.append(f"Numeración del articulado inesperada: {numbers}")


def check_required_files() -> None:
    required = [
        "LEEME.md",
        "00_PROYECTO_DE_LEY/RESUMEN_EJECUTIVO.md",
        "00_PROYECTO_DE_LEY/FUNDAMENTOS_Y_EXPOSICION_DE_MOTIVOS.md",
        "00_PROYECTO_DE_LEY/PROYECTO_DE_LEY_PROTECCION_HOGARES_Y_SEGUNDA_OPORTUNIDAD_V1.md",
        "05_ANALISIS_Y_CALCULOS/DIAGNOSTICO_CUANTITATIVO_2023_2026.md",
        "07_INVENTARIO/INDICE_DOCUMENTAL.csv",
        "07_INVENTARIO/SHA256SUMS.csv",
    ]
    for relative in required:
        if not (ROOT / relative).exists():
            errors.append(f"Falta archivo obligatorio: {relative}")


check_markdown_links()
check_legislative_sources()
check_link_register()
check_articles()
check_required_files()

if errors:
    print("FAIL")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("PASS")
print("- 23 proyectos PDF y 23 textos extraídos")
print("- 38 enlaces del documento base registrados")
print("- 86 artículos consecutivos")
print("- enlaces internos y archivos obligatorios verificados")
