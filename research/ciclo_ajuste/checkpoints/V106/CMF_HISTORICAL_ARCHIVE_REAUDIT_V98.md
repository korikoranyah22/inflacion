# Banco CMF S.A. — V98 historical archive re-audit

V96 correctly refused to classify the raw pass-result accounts by counterparty, but one preservation statement was stale: the official historical ZIPs were already physically present in the repo and **their 2023 member bodies are recoverable locally**.

## Physical recovery

- Annual official archive: `020_Historico-Balance-e-Informes-Anual-1.zip`.
  - exact member: `Anual-2023-Balance e Informes Separado.pdf`;
  - bytes: `706493`;
  - SHA-256: `7ae34c445b53ba8edcee5d5b0efd0919f4dab77f587a12e0ab710b13b551aeef`.
- Quarterly official archive: `021_Historico-Trimestral-Balances-e-Informes-1.zip`.
  - exact member: `Trimestral-2023-03-Balance e Informes-Individual.pdf`;
  - bytes: `741522`;
  - SHA-256: `d5ab9998c7fbbc22e6ed599d033316e136406d9b8de28839da466d3bddd304a7`.

Both member hashes were recomputed directly from `unzip -p` and match the extracted preserved copies under `inputs/issuer_retrieval/v98/binaries/`.

## 30/09/2023 separated issuer evidence

The 9M separated Note 3 states:

- closing active repo stock: **51,764,239k**, in **Letras de Liquidez del BCRA**;
- no passive repo operations outstanding at 30/09/2023;
- positive repo results accumulated 9M: **10,095,166k**;
- negative repo results accumulated 9M: **3,830k**.

Annex Q independently reports pass income **10,095,166k** and pass expense **3,830k**. BCRA raw entity `00319` is an exact total reconciliation: `511027=10,095,166k`; `521022=3,830k`.

## 31/12/2023 separated issuer evidence

The annual separated Note 3 states positive active-repo results **36,619,212k** and negative passive-repo results **7,933k**. Annex Q repeats pass income **36,619,212k** and pass expense **7,933k**. BCRA raw entity `00319` again matches exactly: `511027=36,619,212k`; `521022=7,933k`.

The annual closing active repo stock is **99,589,907k** and the disclosure identifies it with BCRA; there were no passive repo operations outstanding at year-end.

## Why CMF is still not promotable

The strict object is a **flow four-leg split** (BCRA vs Other-FI, income and expense). The recovered 2023 issuer statements identify the **closing stock** counterparty as BCRA and the **aggregate flow results** as pass income/expense, but Annex Q does not open those flow results into BCRA vs Other-FI.

Therefore:

- the exact raw↔issuer total reconciliation is now stronger;
- the old claim “archive body not recovered” is revoked;
- **stock counterparty is not substituted for flow counterparty**;
- `511027` / `521022` semantics are not generalized from other banks;
- CMF remains `HOLD / N/D_STRICT` pending an explicit same-entity, same-year flow counterparty opening.
