# V104

V104 keeps the V103 strict panel frozen and turns the CNV blob search into a frontend-forensics target.

New work:
- independent Hybrid Analysis browser forensics confirms the JavaScript/download stack loaded by a real AIF PublicView;
- `/js/Presentations/presentations.js` is isolated as the highest-value next extraction target (4,192 bytes in the captured 2025 instance);
- the captured PublicView HTML exists as a 77,570-byte SHA-256-addressed artifact, but its public download is disabled;
- no click-driven attachment request was present in the passive trace, so no endpoint/blob GUID is guessed;
- exact Mariva / HSBC / BMA targets remain inherited from V103, with BMA #3177414 still excluded;
- Banco Rioja mismatch hold remains untouched.

Strict state: **24 entities / 59.7775957463226204806504411472763588249111893261199797672530882599989158997072479353967644% / CLOSED_NETWORK_GATE=NO**.

Read `VEREDICTO_V104.md`, `AUDITORIA_V104.md`, `CNV_PUBLICVIEW_FRONTEND_FORENSICS_V104.md`, and `RECOVERY_QUEUE_V104.csv` first.
