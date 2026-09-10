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
    button = '    <button class="tab-btn" type="button" data-tab="tab-productive-audit">Chequeo productivo</button>'
    panel = (
        '  <!-- PRODUCTIVE_AUDIT_TAB_VERSION:1 -->\n'
        '  <section id="tab-productive-audit" class="tab-panel">\n'
        '    <productive-audit-dashboard></productive-audit-dashboard>\n'
        '  </section>\n'
    )
    script = '<script src="assets/productive-audit-tab.js?v=20260910-1"></script>'

    if button.encode("utf-8") not in payload:
        payload = replace_once(
            payload,
            '    <button class="tab-btn" type="button" data-tab="tab-emae">Actividad real · ¿crecimiento o rebote?</button>',
            '    <button class="tab-btn" type="button" data-tab="tab-emae">Actividad real · ¿crecimiento o rebote?</button>\n' + button,
            "botón del tab",
        )

    if b'<section id="tab-productive-audit" class="tab-panel">' not in payload:
        payload = replace_once(
            payload,
            '  <!-- MOROSIDAD_TAB_VERSION:1 -->',
            panel + '\n  <!-- MOROSIDAD_TAB_VERSION:1 -->',
            "panel del tab",
        )

    if script.encode("utf-8") not in payload:
        payload = replace_once(
            payload,
            '<script src="assets/fortune-income-tab.js?v=20260907-4"></script>',
            '<script src="assets/fortune-income-tab.js?v=20260907-4"></script>\n' + script,
            "script del componente",
        )

    if b"'tab-emae','tab-productive-audit','tab-morosidad'" not in payload:
        payload = replace_once(
            payload,
            "'tab-emae','tab-morosidad'",
            "'tab-emae','tab-productive-audit','tab-morosidad'",
            "grupo destacado",
        )

    if b"'tab-emae','tab-productive-audit','tab-roads'" not in payload:
        payload = replace_once(
            payload,
            "'tab-emae','tab-roads'",
            "'tab-emae','tab-productive-audit','tab-roads'",
            "grupo de actividad",
        )

    INDEX.write_bytes(payload)
    print("OK: tab Chequeo productivo integrado en index.html")


if __name__ == "__main__":
    main()
