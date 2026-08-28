# AUDITORÍA V61 — System Q4 A-Q coverage & pass netting

## Progress

V61 extends exact Q4 reconstruction from two entities to three by adding Banco Galicia from original official Sep-2023 and FY-2023 statements. It also adds Banco Nación annual A-Q as an external counterparty/control profile.

IPC Sep→Dec factor remains `1.532908152197`.

### Galicia Q4 reconstructed (thousand Dec-23 ARS)
- broad interest: 1,193,230,518
- household-like product bundle: 201,913,046 (16.92% of broad interest)
- BCRA pass income: 228,495,363
- other-FI pass income: 6,150,559
- other-FI pass expense: 1,422,129

### Three-bank diagnostic sample
Macro + Ciudad + Galicia has broad interest 2,366,411,723 thousand Dec-23 ARS and household-like product flow 460,592,814, or 19.46%.

**This is NOT a system estimate** because coverage is incomplete and consolidation bases are mixed (individual/consolidated).

## Major methodological result

The correct pass-counterparty problem is no longer `is passes BCRA?`; it is a gross-to-net reconciliation by counterparty. The published IEF +7.7pp pass gap remains without an identified BCRA share.

## Gates retained
- household-like = product proxy, not strict institutional household sector;
- broad interest != IEF analytical interest;
- public securities != Treasury counterparty identity;
- stock != flow;
- direct household→bank transfer remains not identified.
