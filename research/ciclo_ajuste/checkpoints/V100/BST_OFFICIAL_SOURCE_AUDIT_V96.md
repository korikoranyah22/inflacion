# Banco de Servicios y Transacciones S.A. — official source audit V96

## Primary issuer sources

- 30/09/2023 official BST financial statements: `https://bst.com.ar/wp-content/uploads/2025/01/EEFF-BST-092023.pdf`
- 31/12/2023 official BST financial statements: `https://bst.com.ar/wp-content/uploads/2025/01/EEFF-BST-12-2023-1.pdf`

## Basis compatibility

BST's issuer notes state at both 30/09/2023 and 31/12/2023 that the entity has no equity participation/control/joint-control/significant-influence relationship requiring subsidiary consolidation. The bank-level statements are therefore compatible with the individual-entity target basis used by the strict panel.

## 9M official totals

The 30/09/2023 issuer note reports accumulated pass-operation interest:

- income, `BCRA y otras entidades financieras`: **7,577,705k**;
- expense, `BCRA y otras entidades financieras`: **107,266k**.

Sep BCRA raw entity `00338` contains:

- `511108=7,387,208k` (absolute result);
- `511027=190,497k`;
- `521022=107,266k`.

Income reconciliation is exact: `7,387,208 + 190,497 = 7,577,705`. Expense reconciliation is exact: `107,266 = 107,266`.

## FY Annex Q — direct counterparty split

The official FY Annex Q opens pass income as **24,029,765k**, split:

- BCRA: **23,689,034k**;
- Other Financial Institutions: **340,731k**.

It opens pass expense as **186,191k**, entirely under **Other Financial Institutions**, hence BCRA expense is zero.

Dec raw entity `00338` matches those three nonzero legs one-to-one:
`511108=23,689,034k`, `511027=340,731k`, `521022=186,191k`.

This creates a **BST-specific same-entity/same-year crosswalk**. Applying those exact identities back to Sep resolves the 9M combined note without ever claiming a universal meaning for the six-digit raw accounts.

## Q4 homogeneous bridge

Frozen factor: `1.532908152197492`.

- BCRA income: **12365122.634821469517664k**
- BCRA expense: **0E-15k**
- Other-FI income: **48716.595730834366476k**
- Other-FI expense: **21762.074146383823128k**

Decision: **PROMOTE / EXACT_FOUR_LEG**.
