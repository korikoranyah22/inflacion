# Auditoría V106 - eleven original PDFs, six strict promotions and historical bootstrap

## Starting state

The actual checkout head before this transaction was V105. V106 did not exist and was constructed from that verified checkpoint. All inherited QA scripts present in V105 (V97, V98, V100–V105) passed before modification.

After the promotion, V98 and V100–V105 still pass. V97 intentionally no longer passes against the live master catalog because it asserts that Columbia's two source paths and hashes remain blank; V106 reverses exactly that historical hold. The historical V97 script is preserved unchanged, and `qa_v106.py` checks the promoted replacement invariant.

## Frozen arithmetic after promotion

- exact entities: **30**;
- asset numerator: **59,812,903.504 million ARS**;
- denominator: **96,697,695.5 million ARS**;
- strict coverage: **61.85556252889191138996688912819023696381678506495534839297178493772894515361020159989231594459249549%**;
- increment versus V105: **2.07796678256929090931644798091387813890559573883536862571869667773002925390295366449555154459249549 pp**;
- closed-network gate: **NO**;
- Sep-to-Dec factor: **1.532908152197492**.

The six promoted assets sum to exactly **2,009,345.992 million ARS**. Adding them to the V105 numerator of 57,803,557.512 yields 59,812,903.504.

## Physical source audit

The eleven original files are listed in `P0_ISSUER_SOURCE_INGEST_V106.csv`. Checks performed on the local bytes:

1. official URL download completed without HTTP failure;
2. first five bytes equal `%PDF-`;
3. Poppler parsed each complete document and returned a page count;
4. SHA-256 was calculated from the preserved local bytes;
5. material separated/individual pages were rendered and visually compared with the inherited candidate audits;
6. no new SHA-256 matched an existing catalogued source.

All eleven source entries were updated in `data/fuentes/FUENTES.csv`. The V106 master audit contains 205 catalog entries, 200 physical copies and 200 exact hash matches. Banco La Pampa has one filename-display encoding discrepancy (`Diseño` versus the Git-materialized mojibake name); `SOURCE_PATH_ENCODING_EXCEPTIONS_V106.csv` records it and the hash identity is exact.

## Promotion gates

- Hipotecario: V99 entity-specific presentation/reclassification bridge retained; two originals now preserved.
- Columbia: V97 Columbia-only raw set retained; two originals now preserved.
- BACS: separated 14,063k FY expense retained; consolidated 14,507k remains inadmissible; two originals preserved.
- Banco Municipal de Rosario: annual header anomaly remains explicit and is controlled by annual Note 6 plus exact raw totals; two originals preserved.
- BTF: BTF-only same-year raw crosswalk retained; FY original preserved.
- VOII: direct Annex Q legs retained; tiny negative Q4 Other-FI expense residual remains unclamped; two originals preserved.

No six-digit account meaning is generalized to another bank.

## Historical workstream

The V106 historical files index existing V31–V51 evidence into E0–E6. They do not add uncited values or causal claims.

- E0 2001–2003 remains `NOT_ENOUGH_EVIDENCE` and receives a primary-source queue.
- E1 2008–2009 remains a global-shock falsifier.
- E4 2018–2019 retains the negative mora-onset lag and `FAILS_ONSET` status.
- E5 COVID remains `SPECIAL_REGIME`.
- E6 keeps registered and broad wage clocks separate and retains the immediate-provision / lagged-mora reordering.

## Non-events and holds

- No exact CNV attachment path/verb/payload was observed; no route was guessed.
- No Mariva, HSBC or BMA attachment binary was recovered.
- BMA FY #3171909 remains mandatory and #3177414 remains excluded.
- Banco Rioja's 158,789k mismatch is not fitted away.
- Majority asset coverage is not treated as a closed network.
- `index.html` and the dashboard were not modified.
