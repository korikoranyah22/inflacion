# Auditoría V104 — PublicView frontend forensics, no numeric promotion

## Frozen strict state
- exact entities: **24**;
- asset numerator: **57,803,557.512 million ARS**;
- system denominator: **96,697,695.5 million ARS**;
- strict coverage: **59.7775957463226204806504411472763588249111893261199797672530882599989158997072479353967644%**;
- closed-network gate: **NO**;
- Sep→Dec factor: **1.532908152197492**.

## What changed
1. V104 found independent browser-forensic evidence for a real AIF PublicView captured on 2025-04-30.
2. The trace proves the page loaded presentation-specific `/js/Presentations/presentations.js` (4,192 bytes in that capture) plus explicit download/file utilities.
3. Hybrid Analysis also records the original PublicView HTML as a 77,570-byte extracted artifact with SHA-256 `33ca3bed35d68eff021ee21a92444b0d0fc8d86ec9931c34b2d0aedd9427f1ba`.
4. Public artifact/response downloads are restricted and the passive run did not click an attachment, so the exact attachment endpoint/blob GUID remains unresolved.
5. The earlier V103 Almanac route description is retained as inherited secondary evidence only; its public dataset URL did not return the dataset during V104.
6. Current direct CNV target fetches were unavailable in this channel, so V104 deliberately does not claim fresh target revalidation.
7. Banco Rioja remains frozen on the 158,789k FY issuer/raw pass-income mismatch. No crosswalk was forced.

## Consequence
This is a **frontend-forensics recovery-route checkpoint**, not a numeric checkpoint. No strict numerator, entity count, candidate arithmetic, or closed-network conclusion changes.

If all eleven already-resolved promotion-blocking issuer PDFs are preserved, the frontier remains **30 entities / 61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%**, closed-network gate `NO`.
