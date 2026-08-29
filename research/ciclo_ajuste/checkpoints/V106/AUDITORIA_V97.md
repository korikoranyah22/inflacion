# Auditoría V97 — Columbia resolved / preservation hold; Mariva attachment hold

## Banco Columbia
1. Target basis: **PASS** — separated/individual issuer material is present inside both official packages.
2. 9M official pass totals: **PASS** — income 2,070,947k; expense 512,498k.
3. FY official Annex-Q split: **PASS** — BCRA income 8,366,812k; Other-FI income 0; BCRA expense 0; Other-FI expense 882,825k.
4. FY raw reconciliation: **PASS** — income account set `511027+511108+511055 = 170,738+8,194,679+1,395 = 8,366,812k`; `521022=882,825k`.
5. 1,395k discrepancy: **RESOLVED** — exact raw `511055` residual; same account exists at Sep as 567k.
6. 9M raw reconciliation: **PASS** — income set `55,188+2,015,192+567=2,070,947k`; `521022=512,498k`.
7. Entity-specific crosswalk: **PASS analytically**, same entity/same year/account-set only; never generalized.
8. Homogeneous Q4 differencing: **PASS candidate** with factor `1.532908152197492`.
9. Physical issuer-source preservation: **FAIL/PENDING** — original Columbia PDF binaries could not be persisted in this environment.
10. Strict promotion: **HOLD** until both original PDFs are physically stored and SHA-256 recorded.

Candidate Q4 (not in strict panel): BCRA income `5192240.460931060535076k`; BCRA expense 0; Other-FI income 0; Other-FI expense `97212.637815089744984k`.

## Banco Mariva
1. CNV identifies exact individual FY and 9M 2023 filings: **PASS discovery**.
2. BCRA raw Sep/Dec entity 00254: **PASS control**.
3. Actual CNV attachment body / Annex-Q opening: **NOT RECOVERED**.
4. Counterparty crosswalk: **N/D_STRICT**.
5. Promotion: **HOLD**.

## System state
- exact entities: 24;
- strict numerator: 57,803,557.512m ARS;
- strict coverage: 59.777595746322620480650441147276358824911189326119979767253088259998915899707248% (unchanged);
- closed-network gate: NO.
