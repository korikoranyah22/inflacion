# Auditoría V93 — Banco de La Pampa S.E.M.

## Promotion tests

1. **Target basis:** PASS. CNV registry lists 30/09/2023 filing #3121031 as individual.
2. **FY issuer counterparty opening:** PASS. Official FY Annex Q gives BCRA income 54,227,326k, other-FI income 0, BCRA expense 0, other-FI expense 5,110k.
3. **Raw FY one-to-one reconciliation:** PASS. Entity 00093 Dec raw has 511108=54,227,326k and 521022=5,110k; no 511027.
4. **Same-entity 9M bridge:** PASS. Sep raw has 511108=19,150,613k and 521022=3,334k; identities are applied only after same-entity FY validation.
5. **Homogeneous Q4 differencing:** PASS using frozen factor `1.532908152197492`.
6. **Residual policy:** PASS. Other-FI expense Q4 residual `-0.715779426438328k` is preserved, not clamped.
7. **Universal mapping prohibition:** PASS. No inference is carried to another entity.
8. **Coverage recomputation:** PASS. `56847496.640/96697695.5*100 = 58.788884622384821983684192349754601959464483825263446945330770576636958219960888%`.
9. **Gate:** remains `NO`; asset majority is not a closed counterparty network.
