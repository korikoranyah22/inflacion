# Handover V97 → V98

## Frozen strict state
- checkpoint: V97
- exact entities: 24
- strict coverage: 59.777595746322620480650441147276358824911189326119979767253088259998915899707248%
- numerator: 57803557.512 million ARS
- denominator: 96697695.5 million ARS
- closed-network gate: NO
- factor: 1.532908152197492

## Columbia
Analytically resolved, not promoted solely because two original issuer PDFs are not physically preserved.

Required files:
- `https://secure.bancocolumbia.com.ar/web/Multimedios/Otros/10184.pdf?v=36`
- `https://secure.bancocolumbia.com.ar/web/Multimedios/Otros/10253.pdf?v=22`

Once physically recovered:
1. validate PDF magic bytes and SHA-256;
2. add local paths/hashes to `FUENTES.csv`;
3. re-run V97 QA;
4. promote Columbia with candidate Q4 in `COLUMBIA_Q4_FOUR_LEG_CANDIDATE_V97.csv`;
5. candidate coverage becomes 59.965540816843975356165545847987659643864005011370720825503023492426456016213954% / 25 entities;
6. closed-network gate stays NO.

Do not re-open the 1,395k issue: it is solved by Columbia raw `511055=1,395k` at Dec (and 567k at Sep) inside the exact entity-specific account-set reconciliation.

## Mariva
CNV exact target-basis filings are identified:
- Sep individual #3122483 / `c23edd68-9bf4-4b3d-a1d8-9cde4770d45c`;
- FY individual #3165651 / `d28fcf1a-28dc-465b-8478-aad95e0d4539`.

Recover attachment bodies, then build a same-entity/same-year issuer/raw crosswalk. Raw-only account-name mapping remains prohibited.
