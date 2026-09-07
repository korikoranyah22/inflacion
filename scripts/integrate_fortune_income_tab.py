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


def keep_first_block(payload: bytes, marker: str, end_marker: str | None = None) -> bytes:
    marker_bytes = marker.encode("utf-8")
    first = payload.find(marker_bytes)
    while first >= 0 and payload.count(marker_bytes) > 1:
        duplicate = payload.find(marker_bytes, first + len(marker_bytes))
        if end_marker is None:
            start = duplicate
            end = duplicate + len(marker_bytes)
        else:
            start = payload.rfind(b"\n", 0, duplicate) + 1
            closing = end_marker.encode("utf-8")
            end = payload.find(closing, duplicate)
            assert end >= 0, f"bloque duplicado sin cierre: {marker}"
            end += len(closing)
        payload = payload[:start] + payload[end:]
    return payload


def set_gap_after(payload: bytes, marker: str, gap: bytes, end_marker: str | None = None) -> bytes:
    marker_bytes = marker.encode("utf-8")
    start = payload.find(marker_bytes)
    if start < 0:
        return payload
    if end_marker is None:
        end = start + len(marker_bytes)
    else:
        closing = end_marker.encode("utf-8")
        end = payload.find(closing, start)
        assert end >= 0, f"bloque sin cierre: {marker}"
        end += len(closing)
    cursor = end
    while cursor < len(payload) and payload[cursor] in b"\r\n":
        cursor += 1
    return payload[:end] + gap + payload[cursor:]


def main() -> None:
    payload = INDEX.read_bytes()

    for old_version in ("1", "2", "3"):
        payload = payload.replace(
            f'<script src="assets/fortune-income-tab.js?v=20260907-{old_version}"></script>'.encode("utf-8"),
            b'<script src="assets/fortune-income-tab.js?v=20260907-4"></script>',
        )
    fortune_button = '    <button class="tab-btn" type="button" data-tab="tab-fortune-income">Ingresos y grandes fortunas</button>'
    fortune_panel_marker = '<section id="tab-fortune-income" class="tab-panel">'
    fortune_script = '<script src="assets/fortune-income-tab.js?v=20260907-4"></script>'
    payload = keep_first_block(payload, fortune_button)
    payload = keep_first_block(payload, fortune_panel_marker, '</section>')
    payload = keep_first_block(payload, fortune_script)
    payload = set_gap_after(payload, fortune_button, b"\n")
    payload = set_gap_after(payload, fortune_panel_marker, b"\n\n", '</section>')
    fortune_script_bytes = fortune_script.encode("utf-8")

    if fortune_button.encode("utf-8") not in payload:
        payload = replace_once(
            payload,
            '    <button class="tab-btn" type="button" data-tab="tab-wealth-contribution">Grandes fortunas</button>',
            '    <button class="tab-btn" type="button" data-tab="tab-wealth-contribution">Grandes fortunas</button>\n'
            + fortune_button,
            "botón del tab",
        )

    if fortune_panel_marker.encode("utf-8") not in payload:
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

    if fortune_script_bytes not in payload:
        payload = replace_once(
            payload,
            '<script src="assets/political-wealth-tab.js?v=20260903-38"></script>',
            '<script src="assets/political-wealth-tab.js?v=20260903-38"></script>\n'
            + fortune_script,
            "script del componente",
        )

    if b"'tab-wealth-contribution','tab-fortune-income','tab-milei-cost'" not in payload:
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
