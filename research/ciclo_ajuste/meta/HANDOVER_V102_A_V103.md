# HANDOVER V102 → V103 — source rescue + unresolved entity sweep

## Frozen state
```text
checkpoint = V102
strict entities = 24
strict coverage = 59.7775957463226204806504411472763588249111893261199797672530882599989158997072479353967644%
asset numerator = 57,803,557.512 million ARS
system denominator = 96,697,695.5 million ARS
closed-network gate = NO
Sep→Dec factor = 1.532908152197492
```

## Newly resolved in V102
### Banco VOII S.A.
Direct official issuer Annex Q at both endpoints:
- 9M: BCRA income 0; BCRA expense 0; Other-FI income 934,677k; Other-FI expense 86,752k.
- FY: BCRA income 0; BCRA expense 0; Other-FI income 2,881,991k; Other-FI expense 132,980k.
- Q4 Other-FI income = 1449217.007028504769916k.
- Q4 Other-FI expense = -2.848019436825984k (retain negative residual).
- raw entity 00312 matches both endpoint Annex-Q values exactly.
- status: analytically exact / physical-source hold.

### Banco Rioja
- FY issuer Annex Q: BCRA repo income 14,409,056k; BCRA repo expense 7,844k.
- Dec raw: 511108=14,250,267k; 521108=7,844k.
- income mismatch = 158,789k; do not crosswalk or absorb as residual.
- compatible 9M issuer opening not recovered.

## V103 priorities
1. Any manually supplied promotion-blocking PDFs: ingest, SHA, update FUENTES, promote mechanically.
2. Payoff order: Hipotecario > Columbia > BACS > BMR > BTF > VOII.
3. Continue issuer sweep among remaining raw entities. Prefer direct 9M+FY Annex Q counterparty openings.
4. Keep Banco Rioja on mismatch hold until the 158,789k difference is explained.
5. Mariva / HSBC / BMA exact CNV individual attachments remain high-value binary-discovery targets.
6. Never mass-map six-digit accounts; Banco Rioja is now another explicit counterexample.
7. Keep repo cumulative and regenerate source audit/manifests/tree/package after any promotion or new source use.
