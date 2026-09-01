from pathlib import Path
from PIL import Image, ImageDraw


def build_contacts(source_dir: Path, output_dir: Path, per_sheet: int = 12) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = sorted(source_dir.glob("page-*.png"), key=lambda p: int(p.stem.split("-")[-1]))
    thumb_w, thumb_h = 360, 466
    cols, rows = 3, 4
    margin, label_h = 18, 28
    for sheet_index in range(0, len(pages), per_sheet):
        subset = pages[sheet_index:sheet_index + per_sheet]
        canvas = Image.new("RGB", (cols * (thumb_w + margin) + margin, rows * (thumb_h + label_h + margin) + margin), "white")
        draw = ImageDraw.Draw(canvas)
        for index, path in enumerate(subset):
            image = Image.open(path).convert("RGB")
            image.thumbnail((thumb_w, thumb_h))
            col, row = index % cols, index // cols
            x = margin + col * (thumb_w + margin)
            y = margin + row * (thumb_h + label_h + margin)
            canvas.paste(image, (x + (thumb_w - image.width) // 2, y))
            page_number = int(path.stem.split("-")[-1])
            draw.text((x, y + thumb_h + 4), f"PDF page {page_number}", fill="black")
        target = output_dir / f"contact_{sheet_index // per_sheet + 1:02d}.jpg"
        canvas.save(target, quality=88)


root = Path(r"C:\Github\inflacion\tmp\pdfs\v180")
build_contacts(root / "bid_pcr" / "pages", root / "bid_pcr" / "contacts")
build_contacts(root / "bid_eval" / "pages", root / "bid_eval" / "contacts")
build_contacts(root / "bid_proposal" / "pages", root / "bid_proposal" / "contacts")
