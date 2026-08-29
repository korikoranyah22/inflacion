# Banco Columbia S.A. — official source audit V97

## Analytical result

The previously noted FY pass-income discrepancy of **1,395k** is resolved exactly: Columbia raw account `511055=1,395k` is the missing member of the entity-specific Dec income account set. The same account exists at Sep as `511055=567k`.

Exact reconciliations:

- Sep 9M pass income: `55,188 + 2,015,192 + 567 = 2,070,947k`, exactly the official separated Note 22 total.
- Dec FY pass income: `170,738 + 8,194,679 + 1,395 = 8,366,812k`, exactly the official separated Annex-Q BCRA pass-income amount.
- Sep pass expense: raw `521022=512,498k`, exactly the official separated Note 23 pass-expense total.
- Dec pass expense: raw `521022=882,825k`, exactly the official FY Annex-Q Other-FI pass expense; BCRA expense is zero.

This is a **Banco-Columbia-specific same-entity/same-year account-set crosswalk**. It does **not** authorize mapping `511055`, `511027`, `511108` or `521022` globally across banks.

## Official issuer documents verified through web rendering

1. 30/09/2023 consolidated + separated condensed interim financial statements:  
   `https://secure.bancocolumbia.com.ar/web/Multimedios/Otros/10184.pdf?v=36`
   - separated Note 22: pass income `2,070,947k`;
   - separated Note 23: pass expense `512,498k`.

2. 31/12/2023 annual financial statements:  
   `https://secure.bancocolumbia.com.ar/web/Multimedios/Otros/10253.pdf?v=22`
   - separated Annex Q: BCRA pass income `8,366,812k`; Other-FI pass income `0`;
   - Other-FI pass expense `882,825k`; BCRA pass expense `0`.

## Preservation gate

Both PDFs are readable and analytically sufficient, but this execution environment could not persist the original Banco Columbia PDF binaries. Under the repository rule `used binary source = physical local binary + SHA-256`, Columbia is therefore **not promoted in V97**.

Status: `ANALYTICALLY_RESOLVED_SOURCE_PRESERVATION_HOLD`.

If the two original PDFs are manually recovered and their content matches the audited documents, promotion becomes mechanical; no remaining numerical discrepancy exists.

Candidate impact if later promoted (not current strict state):

- asset addition: `181738.552` million ARS;
- candidate numerator: `57985296.064` million ARS;
- candidate strict coverage: `59.965540816843975356165545847987659643864005011370720825503023492426456016213954%`;
- candidate increment: `0.18794507052135487551510470071130081895281568525074105824993523242754011650670620` pp;
- candidate exact entities: `25`;
- closed-network gate would remain `NO`.
