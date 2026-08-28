# Auditoría V94 — BPN promotion + BSE hold

## Banco Provincia del Neuquén promotion tests

1. **Official FY issuer source:** PASS. BPN's own Memorias y Balances page links Balance 2023 General.
2. **Standalone basis:** PASS. Official BPN 2023 disclosure states the bank does not form part of economic groups.
3. **FY Annex Q:** PASS. Page 83 reports BCRA pass income 129,240,317k, other-FI pass income 0, and no pass-expense line.
4. **Raw FY one-to-one reconciliation:** PASS. Entity 00097 Dec raw has 511108=129,240,317k and no 511027/521007/521022.
5. **Same-entity 9M bridge:** PASS. Sep raw has 511108=50,821,306k and no other candidate repo-result accounts; identity is applied only after BPN-specific FY validation.
6. **Homogeneous Q4 differencing:** PASS using frozen factor `1.532908152197492`.
7. **2024 comparator use:** PASS. Used only to corroborate taxonomy; its 2023 values are reexpressed to 2024 currency and are not used in nominal differencing.
8. **Universal mapping prohibition:** PASS. No inference is carried to another entity.
9. **Coverage recomputation:** PASS. `57373426.142/96697695.5*100 = 59.332775042193223725791893354893860940046911459229139540352334456615876642065374%`.
10. **Gate:** remains `NO`; asset majority is not a closed counterparty network.

## Banco de Santiago del Estero re-audit

- Sep/Dec raw account set: recovered and documented.
- Official BCRA entity-level 2023 control: recovered.
- Issuer-specific Annex-Q/counterparty split: **NOT RECOVERED**.
- Decision: **HOLD / N/D_STRICT**.

The BSE non-promotion is intentional: raw `511108` alone cannot be mass-interpreted as the strict BCRA leg after the Santander counterexample.
