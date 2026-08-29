# Auditoría V98 — source-body recovery without counterparty overreach

## Banco CMF S.A.
1. Annual historical ZIP physically present: **PASS**.
2. Quarterly historical ZIP physically present: **PASS**.
3. Exact FY-2023 separated member extracted: **PASS**, SHA `7ae34c445b53ba8edcee5d5b0efd0919f4dab77f587a12e0ab710b13b551aeef`.
4. Exact 9M-2023 separated member extracted: **PASS**, SHA `d5ab9998c7fbbc22e6ed599d033316e136406d9b8de28839da466d3bddd304a7`.
5. FY pass totals ↔ raw: **PASS exact** — 36,619,212k income; 7,933k expense.
6. 9M pass totals ↔ raw: **PASS exact** — 10,095,166k income; 3,830k expense.
7. Closing active-pass stocks disclosed as BCRA: **PASS control** — 51,764,239k Sep; 99,589,907k Dec.
8. Flow BCRA-vs-Other-FI split: **N/D**.
9. Stock→flow substitution: **PROHIBITED**.
10. Strict promotion: **HOLD**.

## HSBC
1. Sep CNV target-basis filing #3121099 / UUID d483...: **PASS discovery**.
2. FY CNV target-basis filing #3163537 / UUID 39f3...: **PASS discovery**.
3. Both metadata rows are NIIF INDIVIDUAL at the correct 2023 closes: **PASS**.
4. Attachment bodies: **NOT RECOVERED**.
5. Raw-only counterparty mapping: **PROHIBITED**.
6. Promotion: **HOLD**.

## Banco de Corrientes
1. Official FY 2023 page: **PASS discovery**.
2. Exact binary endpoint documentid=1193: **PASS discovery**.
3. Physical PDF recovery/Annex-Q parse: **FAIL/PENDING due current environment DNS**.
4. Promotion: **HOLD**.

## Columbia / Mariva
- Columbia analytical resolution unchanged; physical PDF preservation remains the only blocker.
- Mariva exact individual filings unchanged; attachment bodies remain missing.

## System
- exact entities: 24;
- strict coverage: 59.777595746322620480650441147276358824911189326119979767253088259998915899707248%;
- closed-network gate: NO;
- no numerical V97 promotion/state is altered.
