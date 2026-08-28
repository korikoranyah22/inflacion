# Auditoría V91

## 1. Banco BMA first-pass

CNV exposes the individual 30/09/2023 filing as presentation **#3119515** (`9d3ded55-6d87-4ca2-9feb-920d961f3acd`). BCRA raw entity `00259` Sep/Dec rows were extracted, but the actual CNV attachment could not be recovered in-session. Because Santander already falsified a universal six-digit mapping rule, **BMA remains held**.

## 2. Banco Industrial: entity-specific crosswalk

BCRA entity `00322`:
- Sep-2023 raw: `511108=91,303,079k`; `511027=63,741k`; `521022=605k`.
- Dec-2023 raw: `511108=292,074,698k`; `511027=110,798k`; `521022=2,892k`.

The separated FY Annex Q reports exactly:
- BCRA pass income **292,074,698k**;
- other-FI pass income **110,798k**;
- BCRA pass expense **0**;
- other-FI pass expense **2,892k**.

This is a one-to-one FY reconciliation for Banco Industrial only. Therefore the Sep raw account identities can be used as a **same-entity, same-year target-basis crosswalk** without extending the mapping to other banks.

9M four legs (k ARS): BCRA income **91,303,079**, BCRA expense **0**, other-FI income **63,741**, other-FI expense **605**.
FY four legs (k ARS): BCRA income **292,074,698**, BCRA expense **0**, other-FI income **110,798**, other-FI expense **2,892**.
Q4 Dec-homogeneous: BCRA income **152115463.880168364322132k**, BCRA expense **0.000000000000000k**, other-FI income **13088.901470779662428k**, other-FI expense **1964.590567920517340k**.

## 3. Promotion

**Banco Industrial S.A. promoted to strict exact Q4 four-leg.** Asset added: **770685.987m ARS**.

## 4. Coverage

- V90 numerator: **55232805.681m ARS**.
- V91 addition: **770685.987m ARS**.
- V91 strict numerator: **56003491.668m ARS**.
- Denominator: **96697695.5m ARS**.
- Strict coverage: **57.916056198050759131069467937837256938558582298375456114153206474294932912853130%**.
- Increment vs V90: **0.797005536703819379025428791113227719061826039070393358029906474294932912853130 pp**.
- Exact entities: **19**.
- Gate: **NO** — majority asset coverage is still not closed-network proof.

## 5. Next priority

1. HSBC manual CNV individual PDF remains active.
2. Banco BMA attachment is now an exact manual-recovery target (#3119515).
3. BNA / Santander / Hipotecario remain held under their specific rules.
4. Autonomous next targets: Nuevo Banco del Chaco, Banco de La Pampa, then Banco de Santiago del Estero.
