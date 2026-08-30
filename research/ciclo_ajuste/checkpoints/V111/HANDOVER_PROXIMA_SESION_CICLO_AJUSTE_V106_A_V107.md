# HANDOVER V106 -> V107 - CNV exact contract and 2001 primary-source map

## Frozen state

```text
checkpoint = V106
strict entities = 30
strict coverage = 61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%
asset numerator = 59,812,903.504 million ARS
system denominator = 96,697,695.5 million ARS
closed-network gate = NO
Sep->Dec factor = 1.532908152197492
catalogued sources = 205
physical/hash-valid = 200/200
```

## V106 material changes

- Preserved and hashed all eleven inherited P0 issuer PDFs.
- Promoted Hipotecario, Columbia, BACS, Banco Municipal de Rosario, BTF and VOII mechanically.
- Removed all six analytical source holds; no P0 preservation blocker remains.
- Opened the 2001–2026 historical matrix, coverage audit and source queue.
- Recorded the Banco La Pampa filename-encoding exception without changing byte identity.

## What did not change

- Closed-network gate remains `NO` despite majority asset coverage.
- No exact CNV attachment request was observed or guessed.
- BMA FY remains #3171909; #3177414 is not a substitute.
- Banco Rioja remains `HOLD_V102_MISMATCH` at 158,789k.
- No global six-digit mapping is permitted.

## V107 priorities

1. Obtain an observed CNV attachment request contract: exact path, verb, form fields and token semantics.
2. Replay only that observed contract against one PublicView, then the six frozen Mariva/HSBC/BMA targets; preserve original bytes and hashes.
3. Start the E0 2001–2003 primary-source census in the order BCRA -> official legal/Treasury -> INDEC -> issuers/AGN -> institutional secondary sources.
4. Do not narrate 2001 before the source map establishes t0, accounting regime and loss-allocation mechanisms.
5. Continue BNA/Santander/Corrientes/BSE/CMF/Chubut entity-specific recovery and Banco Rioja documentary reconciliation.
6. Keep searching for evidence that falsifies, reorders or limits the central pattern.

## High-value manual request if automated CNV recovery remains blocked

Capture one real AIF attachment click in browser DevTools/HAR and preserve the request path, method, form fields and response metadata. A screenshot or reconstructed PDF is not sufficient.
