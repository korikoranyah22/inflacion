# PROMPT CODEX V66 — INDIVIDUAL AQ RETRIEVAL AND CLOSED-NETWORK EXPANSION

Continue from V65. Do not reopen basis harmonization unless a concrete filing contradicts it.

## Frozen new V65 state
```text
SYSTEM_PANEL_BASIS
= INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING

BCRA_BANK_ASSETS_DEC2023
= 96,697,695.5 million ARS

STRICT_Q4_FOUR_LEG_EXACT_INDIVIDUAL_COVERAGE
= 4.101042%
= ICBC only

ICBC_PLUS_GALICIA_INDIVIDUAL_Q4_OTHERFI_ASSET_FOOTPRINT
= 13.070316%
= OPEN_SUBSET

BAPRO_FY_SEPARATE_FOUR_LEG
= IDENTIFIED_EXACT
BAPRO_Q4
= N/D_9M_NOT_RETRIEVED

CREDICOOP_FY_SEPARATE_FOUR_LEG
= IDENTIFIED_EXACT
CREDICOOP_Q4
= N/D_9M_COMPATIBLE_PDF_NOT_RETRIEVED

SYSTEM_INTERBANK_PASS_CANCELLATION
= NOT_IDENTIFIED

IEF_7_7PP_BCRA_SHARE
= N/D
```

## Mission A — retrieve compatible individual 9M/FY Annex Q pairs
Priority order by expected coverage gain and known documents:
1. Banco Provincia — retrieve official separated/individual 30-09-2023 Annex Q compatible with FY.
2. Banco Credicoop — retrieve the official 30-09-2023 separated Annex Q whose publication existence is already located.
3. Banco Ciudad — individual/separated 9M + FY; replace consolidated control with target-basis Q4 if possible.
4. Banco Nación — individual/separated 9M + FY.
5. Banco Macro — individual/separated pair.
6. Santander Argentina — individual/separated pair and all four counterpart legs.
7. BBVA Argentina — individual/separated pair and BCRA/otherFI split.
8. Banco Supervielle — individual/separated pair and BCRA/otherFI split.
9. Additional large banks needed to reduce uncovered network mass.

Never substitute consolidated filings for missing individual rows.

## Mission B — Q4 reconstruction
Only when 9M and FY are compatible:
```text
Q4_DecPesos = FY_DecPesos - 9M_SepPesos * (IPC_Dec / IPC_Sep)
```
using frozen factor from V64/V65.

For every entity extract:
- income passes BCRA
- expense passes BCRA
- income passes other financial institutions
- expense passes other financial institutions

Labels: EXACT / BOUND / APPROX / N-D.

## Mission C — coverage scoreboard
After every successful entity, compute:
```text
sum(Dec-2023 BCRA entity assets) / 96,697,695.5
```
This is **retrieval coverage only**. Never scale pass flows using asset shares.

Keep separate:
- full-four-leg exact Q4 coverage;
- partial counterparty-detail coverage;
- FY-only source footprint.

## Mission D — interbank cancellation gate
Do not test system cancellation until the individual Q4 network is near-full/materially closed.

If coverage remains open:
```text
SYSTEM_INTERBANK_PASS_CANCELLATION = N/D
```

Do not infer missing pass-flow mass from uncovered asset mass without a separately specified model; default is not to model it.

## Mission E — household branch
Deprioritize generic sector evidence. Only elevate if a source directly maps accrued Annex Q interest/product flow to PH/PJ or household/company institutional sector.

Otherwise retain:
```text
HOUSEHOLD_ANNEX_Q_ACCRUED_INTEREST_FLOW_BRIDGE = NOT_IDENTIFIED
HOUSEHOLD_SYSTEM_Q4_POINT_ESTIMATE = N/D
```

## Frozen gates
- individual != consolidated
- stock != flow
- origination amount != accrued interest
- asset coverage != pass-flow weight
- open subset != closed system
- entity net != system cancellation
- +7.7pp passes != BCRA without compatible system bridge
- no direct household-to-bank transfer without accounting identity
- no HTML modifications

## Outputs
Create V66 equivalents, update coverage scoreboard, evidence ledger, audit, verdict, QA, handover and V67 prompt based on the surviving bottleneck.
