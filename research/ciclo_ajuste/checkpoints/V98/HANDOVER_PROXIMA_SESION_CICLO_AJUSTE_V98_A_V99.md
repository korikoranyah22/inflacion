# Handover — Ciclo de ajuste V98 → V99

## Frozen analytical state

```text
ANALYTIC_CHECKPOINT = V98
STRICT_COVERAGE = 59.777595746322620480650441147276358824911189326119979767253088259998915899707248%
EXACT_ASSET_NUMERATOR = 57,803,557.512 million ARS
SYSTEM_ASSET_DENOMINATOR = 96,697,695.5 million ARS
EXACT_ENTITIES = 24
CLOSED_NETWORK_GATE = NO
SEP_TO_DEC_FACTOR = 1.532908152197492
```

V98 makes **no strict promotion**.

## Do not reopen

- Columbia ~1,395k discrepancy: solved in V97 via entity-specific `511055` bridge.
- CMF source-body availability: solved in V98. The exact 2023 FY and 9M separated PDFs are now physically preserved under `inputs/issuer_retrieval/v98/binaries/` and hash-verified.
- Do **not** promote CMF from closing stock counterparty. The missing object is the pass-result **flow** BCRA-vs-Other-FI opening.
- HSBC target CNV presentations are now exactly #3121099 (Sep) and #3163537 (FY); current CNV live label Banco GGAL S.A. reflects later corporate history and does not change the 2023 recovery target.

## Highest-value next actions

1. **Rescue Columbia PDFs** `10184.pdf` + `10253.pdf`; after hash/magic verification, promotion is mechanical to candidate `59.965540816843975356165545847987659643864005011370720825503023492426456016213954%` / 25 entities.
2. **Mariva attachments** #3122483 and #3165651; then same-entity/same-year crosswalk.
3. **HSBC attachments** #3121099 and #3163537; then entity-specific crosswalk against raw entity 00150.
4. **Banco de Corrientes**: manually rescue exact FY endpoint `documentid=1193`, inspect Annex Q, then seek compatible Sep bridge.
5. If those attachment routes remain blocked, continue to the next issuer where a same-year body can be physically recovered; never mass-map six-digit accounts.

## CMF V98 exact controls

```text
9M issuer/raw pass income = 10,095,166k
9M issuer/raw pass expense = 3,830k
FY issuer/raw pass income = 36,619,212k
FY issuer/raw pass expense = 7,933k
Sep closing active-pass stock BCRA = 51,764,239k
Dec closing active-pass stock BCRA = 99,589,907k
FLOW_COUNTERPARTY_SPLIT = N/D_STRICT
```

## Preservation rule

Source-completeness and analytic sufficiency remain separate gates. A URL/publicview can identify a recovery route; it does not replace a physically preserved binary when that binary is used as evidence.
