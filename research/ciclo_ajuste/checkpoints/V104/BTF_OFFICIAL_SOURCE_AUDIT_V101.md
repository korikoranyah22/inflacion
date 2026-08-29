# Banco Provincia de Tierra del Fuego — official source audit V101

## Source
- Official FY 2023 Balance and Memory: https://www.btf.com.ar/wp-content/uploads/2024/08/BTF-Balance-y-Memoria-2023.pdf
- Official issuer index: https://www.btf.com.ar/institucional/disciplina-de-mercado-y-estados-contables/

## FY issuer mapping
FY Anexo Q explicitly reports repo income **14,938,203k**, entirely against **Banco Central de la República Argentina**, with Other-FI income zero.

Dec raw BCRA for entity `00268` has `511108=14,938,203k`, an exact same-entity FY crosswalk. Sep raw has the same account at **7,194,047k**. This mapping is therefore carried backward only within BTF and 2023.

## Exhaustive controls
- Sep selected raw interest income = **34,212,334k**; expense = **11,731,385k**.
- Dec selected raw interest income = **72,266,826k**; expense = **23,899,565k**.
- The FY totals reconcile the official Anexo Q exactly; the repo-result account set contains only `511108` and no repo-expense result account.

Other-FI income and both expense legs are therefore zero through BTF-specific same-year mapping plus exhaustive reconciliation, not through a universal six-digit-code rule.

## Preservation gate
The FY issuer PDF is web-readable but could not be persisted by the runtime. BTF remains `ANALYTICALLY_RESOLVED_SOURCE_PRESERVATION_HOLD` until physical binary + SHA-256 are stored.
