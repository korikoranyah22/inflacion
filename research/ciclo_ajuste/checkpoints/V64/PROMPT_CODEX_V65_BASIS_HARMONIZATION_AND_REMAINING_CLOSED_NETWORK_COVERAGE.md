# PROMPT CODEX V65 — BASIS HARMONIZATION AND REMAINING CLOSED-NETWORK COVERAGE

Continue from V64. Do not reopen V34–V63 unless a concrete inconsistency requires audit.

## Primary bottleneck
V64 now has exact four-leg Q4 pass flows for:
- Banco Ciudad — consolidated basis.
- ICBC Argentina — individual/standalone basis.

This improves entity-level counterparty identification but still does not create a closed system because coverage is open and bases are mixed.

## Mission A — remaining high-coverage Annex Q retrieval
Prioritize official 9M/FY 2023 Annex Q for:
1. Banco Nación Q3/9M compatible with FY.
2. Banco Provincia Q3/9M compatible with FY.
3. Banco Credicoop Q3/9M + FY.
4. Santander — recover missing expense legs / exact counterparty split.
5. BBVA — recover BCRA vs other-FI split.
6. Supervielle — recover BCRA vs other-FI split.
7. Any large bank needed to bound outside-network mass.

Extract all four legs and label exact/bound/approx/N-D.

## Mission B — accounting-basis harmonization
Determine whether entity-level standalone Annex Q can be aggregated without double counting into a system panel, or obtain a consistently individual panel across banks. Never mix consolidated and individual implicitly.

Target:
```text
SYSTEM_PANEL_BASIS = CONSISTENT_INDIVIDUAL_OR_CONSOLIDATED
```

## Mission C — quantitative coverage denominator
Find an official BCRA denominator for bank-system size (assets, deposits, or another defensible measure) at Q4-2023 and compute sample coverage only if numerator/basis are compatible. Coverage is a retrieval diagnostic, not a weighting scheme for pass flows.

## Mission D — household flow bridge
Use BCRA holder-type stock datasets only as sector evidence. Search for a regulatory/accounting table that directly maps interest accrued or product-flow rows to persons human/legal persons. If no flow bridge exists, retain N/D. Do not infer flow shares from stock shares without a model explicitly labeled as such.

## Frozen gates
- stock != flow
- product != sector
- consolidated != individual
- open subset != closed system
- entity net position != system cancellation
- +7.7 pp passes != BCRA unless compatible system numerator/denominator reconcile
- no direct household-to-bank transfer without identity
- no HTML modifications

## Outputs
Create V65 equivalents of V64 CSV/MD/QA files and a V66 prompt based on the surviving bottleneck.
