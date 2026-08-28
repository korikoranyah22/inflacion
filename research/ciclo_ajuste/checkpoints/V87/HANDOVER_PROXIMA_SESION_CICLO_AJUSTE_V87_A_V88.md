# HANDOVER — Ciclo de Ajuste V87 → V88

## Frozen state

- strict Q4 four-leg coverage: **50.2498852860459327078792689532089210957462786690712810213766%**
- strict exact asset numerator: **48590481.063 million ARS**
- system assets denominator: **96697695.5 million ARS**
- exact entities: **11**
- closed-network gate: **NO**
- Sep→Dec factor: **1.532908152197492**

## V87 changes

1. **Banco Patagonia S.A. promoted**
   - Q4 other-FI income `143548485.379973139597544k`
   - Q4 other-FI expense `502688.298364354295568k`
   - BCRA legs zero.
   - Separated 9M/FY issuer + separated annual Annex Q + raw exact reconciliation.

2. **Citibank N.A. promoted**
   - Q4 BCRA income `271540204.286216447907156k`
   - Q4 other-FI income `2444912.878389518378248k`
   - expense legs zero.
   - Official issuer Note 25 prints the 9M and FY counterparty split directly.

3. **Banco Supervielle S.A. exactified**
   - previous V66–V86 income split bound removed.
   - Q4 BCRA income `86491188.977916638420204k`
   - Q4 other-FI income `222212.688446354018576k`
   - Q4 other-FI expense `591120.907458024334972k`
   - BCRA expense zero.
   - FY separated Annex Q exactly maps Supervielle's own raw account set; same set reconciles official 9M totals.

## Important methodology

Do **not** generalize any six-digit BCRA raw code to every bank. Santander remains the counterexample. Use raw only after direct or entity-specific issuer validation.

Crossing 50% does **not** set closed-network gate to YES. The uncovered side is still material and other-FI bilateral cancellation cannot be tested system-wide.

## Pending priorities for V88

1. **BNA** — recover separated 30/09/2023 interest result opening or explicit subaccount-to-presentation mapping. `521007` remains unresolved.
2. **Santander** — find explicit accumulated 9M BCRA-vs-otherFI split below the exact separated pass-income total.
3. **HSBC** — seek FY counterparty presentation and compatible 9M entity-specific validation.
4. Then continue down Dec-2023 assets with entity-specific crosswalks only.

## Read first

- `VEREDICTO_V87.md`
- `AUDITORIA_V87.md`
- `STRICT_Q4_FOUR_LEG_COVERAGE_V87.csv`
- `FOUR_LEG_PASS_PANEL_V87.csv`
- `V87_ENTITY_SPECIFIC_CROSSWALK_AUDIT.csv`
- `PATAGONIA_Q4_FOUR_LEG_PROMOTION_V87.csv`
- `CITI_Q4_FOUR_LEG_PROMOTION_V87.csv`
- `SUPERVIELLE_Q4_FOUR_LEG_PROMOTION_V87.csv`
- `SANTANDER_SEPARATED_9M_AUDIT_V87.md`
- `BNA_STATUS_V87.md`
