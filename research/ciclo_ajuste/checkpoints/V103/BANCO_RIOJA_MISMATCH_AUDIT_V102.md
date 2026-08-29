# Banco Rioja — V102 mismatch / falsifier audit

The official FY2023 Annex Q directly reports repo-result counterparty as BCRA:
- income from repo operations: **14,409,056k**, all BCRA;
- expense from repo operations: **7,844k**, all BCRA.

The Dec-2023 raw BCRA entity record does **not** reproduce the income leg with the candidate six-digit account: `511108=14,250,267k`, leaving **158,789k** unexplained. The expense candidate `521108=7,844k` does match exactly.

This is therefore a useful falsifier of any global six-digit mapping. One exact leg does not license the other leg, and the 158,789k income mismatch must not be hidden inside a residual or assigned by label.

Official FY URL: https://bancorioja.com.ar/pdf/EEFF-BR-2023.pdf

Verdict: `HOLD_MISMATCH_NO_PROMOTION`. A compatible 9M issuer opening and an explanation of the FY 158,789k discrepancy are required before a strict bridge can be built. The FY binary is also pending physical preservation because it is used in this V102 audit.
