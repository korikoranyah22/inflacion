# Handover — Ciclo de ajuste V96 → V97

**Fecha:** 2026-08-28

## Frozen strict state
- coverage = **59.777595746322620480650441147276358824911189326119979767253088259998915899707248%**
- exact asset numerator = **57803557.512 million ARS**
- denominator = **96697695.5 million ARS**
- exact eligible entities = **24**
- gate = **NO**
- frozen Sep→Dec factor = **1.532908152197492**

## V96 promotion — Banco de Servicios y Transacciones S.A.
FY official Annex Q: BCRA income 23,689,034k; Other-FI income 340,731k; BCRA expense 0; Other-FI expense 186,191k. Dec raw entity 00338 matches exactly.

Official 9M notes give combined pass income 7,577,705k and expense 107,266k. Sep raw has 511108=7,387,208k, 511027=190,497k, 521022=107,266k; the first two sum exactly to official income total and the third exhausts expense. FY direct identities therefore resolve the Sep counterparty split **only for BST**. Issuer notes state no subsidiaries requiring consolidation.

Q4: BCRA income **12365122.634821469517664k**; BCRA expense **0E-15k**; Other-FI income **48716.595730834366476k**; Other-FI expense **21762.074146383823128k**.

## V96 holds
- Banco CMF: official bank-only FY pass totals income 36,619,212k / expense 7,933k exactly match raw, but counterparty split missing. Historical archive candidates identified; do not infer from raw labels.
- Banco del Chubut: Sep 511108=17,821,255k; Dec 511108=48,938,755k; no issuer counterparty opening recovered.

## Standing manual recoveries
- HSBC CNV Sep individual publicview `d483d33a-5c86-4fbb-ab9c-6528bf43f572`.
- BMA/ex-Itaú CNV Sep individual publicview `9d3ded55-6d87-4ca2-9feb-920d961f3acd`.
- BSE FY/9M counterparty opening.
- Banco de Corrientes official 2023 Annex-Q body.
- CMF historical 2023 attachment.
- Banco del Chubut official 2023 issuer opening.

## V97 autonomous order
1. **Banco Columbia S.A.** — official Sep/FY packages already identified; resolve the exact raw bridge and FY ~1,395k income discrepancy before any promotion.
2. Banco Mariva S.A.
3. Continue entity-by-entity.

Never mass-map six-digit BCRA accounts. Keep tiny differencing residuals if they appear; do not clamp.

## Source backfill completed before V97
On 2026-08-28 the local Windows backfill run returned 47/49 validated binaries. Repository ingestion independently rechecked magic bytes, sizes and SHA-256, then placed the binaries in canonical paths and updated the master source catalog. P0=0 and P1=0; only two P2 retrieval gaps remain (BCRA `www7` DNS failure and a BCRA endpoint returning 401). This preservation pass changes no V96 numbers or promotions. V97 may resume; do not call the repo fully source-complete until the two P2 gaps are resolved or formally retired.
