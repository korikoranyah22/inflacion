# Handover — Ciclo de ajuste V95 → V96

**Fecha:** 2026-08-28

## Frozen strict state

- coverage = **59.609772901981929858917889103158616639421360357031466173875881044135121089829902%**
- exact asset numerator = **57641276.689 million ARS**
- denominator = **96697695.5 million ARS**
- exact eligible entities = **23**
- gate = **NO**
- frozen Sep→Dec factor = **1.532908152197492**

V95 adds **Banco de Formosa S.A.** to the prior V94 exact set.

## V95 promotion — Banco de Formosa

Official separated 9M Annex Q directly validates: BCRA income 3,377,992k; Other-FI income 1,420k; BCRA expense 0; Other-FI expense 78,619k. Raw entity 00315 matches exactly.

FY issuer totals are pass income 13,951,639k and pass expense 126,499k. Official 2023 integrated report publishes Pases 13,949,461k, exactly matching Dec 511108 and its already validated BCRA identity. Dec 511027=2,178k is therefore the exact Other-FI income residual. Dec 521022=120,514k retains its direct same-entity Other-FI expense identity; the remaining 5,985k raw account 525042 is the exact BCRA expense residual. **Do not generalize 525042.**

Q4: BCRA income **8771309.525142089603936k**; BCRA expense **5985.000000000000000k**; Other-FI income **1.270423879561360k**; Other-FI expense **-1.706017614623548k**. Preserve the tiny negative residual.

## V95 hold — Banco de Corrientes

Official Argentine `Memoria y Balance 2023` page/download identified. Annex-Q body not parsed. Sep raw 511108=16,968,619k; Dec raw 511108=40,870,153k. HOLD: account name alone cannot establish counterparty.

## Active manual recoveries
- HSBC CNV Sep individual publicview `d483d33a-5c86-4fbb-ab9c-6528bf43f572`.
- Banco BMA / ex-Itaú CNV Sep individual publicview `9d3ded55-6d87-4ca2-9feb-920d961f3acd`.
- BSE official FY2023 Annex Q / compatible Sep issuer package.
- Banco de Corrientes official FY2023 PDF if manually downloadable.

## Standing holds
- BNA: Sep `521007` presentation/subaccount mapping unresolved.
- Santander: 9M pass total exact, BCRA-vs-otherFI split unresolved.
- Hipotecario: same-period expense presentation conflict.
- BSE: raw exact, issuer counterparty crosswalk unresolved.
- Corrientes: official source identified, body not recovered.

## V96 order
1. Any user-rescued HSBC/BMA/BSE/Corrientes PDF.
2. **Banco CMF S.A.** — official Argentine financial-statements archive already identified; seek separated FY/9M counterparty opening.
3. Banco del Chubut S.A.
4. Continue entity-by-entity.

**Search hygiene:** restrict evidentiary promotion sources to Argentina / correct issuer; discard Costa Rica and other ambiguous foreign-bank name matches. Never mass-map six-digit BCRA accounts.
