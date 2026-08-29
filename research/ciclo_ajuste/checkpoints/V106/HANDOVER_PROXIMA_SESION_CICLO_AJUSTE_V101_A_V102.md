# HANDOVER V101 → V102 — source-rescue promotion batch

## Frozen state
- checkpoint: V101
- strict entities: 24
- strict coverage: 59.7775957463226204806504411472763588249111893261199797672530882599989158997072479353967644%
- exact numerator: 57803557.512 million ARS
- denominator: 96697695.5 million ARS
- closed-network gate: NO
- factor: 1.532908152197492

## V101 newly analytically resolved
### BACS
Q4 k ARS: BCRA income 26576523.202785377437612; BCRA expense 0; Other-FI income 18194.067031107755768; Other-FI expense 10741.188034188034836.
Needs two physical issuer PDFs only.

### Banco Municipal de Rosario
Q4 k ARS: BCRA income 3433170.427567358059400; other three legs 0.
Important: FY separated Annex Q in annual PDF carries a wrong 9M header. Do not treat the header literally: annual separated Note 6 states 11,420,465k at 31/12/2023 and Dec raw matches exactly; full interest totals also reconcile. Keep this anomaly documented.
Needs two physical issuer PDFs only.

### Banco Provincia de Tierra del Fuego
Q4 k ARS: BCRA income 3910389.706408089269876; other three legs 0.
Needs FY2023 physical issuer PDF only.

## First V102 action
1. If user supplies any of the nine PDFs in `USER_FILE_REQUESTS_V101.md`, ingest immediately, compute SHA-256, add local path to FUENTES, and mechanically promote the corresponding already-resolved entity.
2. Promotion payoff priority: Hipotecario > Columbia > BACS > BMR > BTF.
3. If no manual rescue is available, continue issuer sweep among remaining raw entities; never mass-map codes.
4. Keep repo cumulative; update FUENTES/source audit/manifests/tree/package.

## Guardrails
Unchanged from V96/V100: individual/separated strict basis, no consolidated substitution, stocks do not substitute flows, no universal six-digit mapping, no zero from visual absence unless exhaustive reconciliation, no closed-network inference from >50% coverage.
