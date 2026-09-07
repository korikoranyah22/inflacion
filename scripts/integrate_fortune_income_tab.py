from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def replace_once(payload: bytes, old: str, new: str, label: str) -> bytes:
    old_bytes = old.encode("utf-8")
    new_bytes = new.encode("utf-8")
    count = payload.count(old_bytes)
    if count == 0 and new_bytes in payload:
        return payload
    assert count == 1, f"{label}: se esperaba una coincidencia y aparecieron {count}"
    return payload.replace(old_bytes, new_bytes, 1)


def main() -> None:
    payload = INDEX.read_bytes()

    payload = replace_once(
        payload,
        '    <button class="tab-btn" type="button" data-tab="tab-wealth-contribution">Grandes fortunas</button>',
        '    <button class="tab-btn" type="button" data-tab="tab-wealth-contribution">Grandes fortunas</button>\n'
        '    <button class="tab-btn" type="button" data-tab="tab-fortune-income">Ingresos y grandes fortunas</button>',
        "botón del tab",
    )

    payload = replace_once(
        payload,
        '\n\n  <section id="tab-milei-cost" class="tab-panel">',
        '\n\n  <section id="tab-fortune-income" class="tab-panel">\n'
        '    <fortune-income-dashboard></fortune-income-dashboard>\n'
        '  </section>\n'
        '\n'
        '  <section id="tab-milei-cost" class="tab-panel">',
        "panel del tab",
    )

    payload = replace_once(
        payload,
        '<script src="assets/political-wealth-tab.js?v=20260903-38"></script>',
        '<script src="assets/political-wealth-tab.js?v=20260903-38"></script>\n'
        '<script src="assets/fortune-income-tab.js?v=20260907-1"></script>',
        "script del componente",
    )

    payload = replace_once(
        payload,
        "'tab-wealth-contribution','tab-milei-cost'",
        "'tab-wealth-contribution','tab-fortune-income','tab-milei-cost'",
        "grupo temático de poder",
    )

    INDEX.write_bytes(payload)
    print("OK: tab Ingresos y grandes fortunas integrado en index.html")


if __name__ == "__main__":
    main()
