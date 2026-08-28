# AUDITORIA V65

## Input
- Base cerrada: V64.
- HTML: no modificado.
- Regla Q4 homogénea heredada: FY_Dec - 9M_Sep reexpresado a Dic.

## Gate A — base sistémica
BCRA IEF Dic-2023 auditado en páginas 7 y 21:
- datos surgen de presentaciones de entidades;
- contiene información individual por entidad y agregada por grupos/sistema;
- nota: agregados se basan en rubros homónimos;
- para indicadores agregados documenta neteos de participaciones/resultados para evitar duplicidades.

Resultado V65:
`SYSTEM_PANEL_BASIS = INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING`.

## Gate B — denominador de cobertura
BCRA IEF p.40:
- Banks assets Dec-2023 = 96,697,695.5 million ARS.
- Banks deposits Dec-2023 = 62,483,328.1 million ARS.
- 63 banks.

Checks:
- ICBC asset coverage = 4.101041787495%.
- ICBC+Galicia asset footprint = 13.070316241404%.
- Coverage is retrieval diagnostic; no scaling of pass flows.

## Gate C — Banco Provincia FY
Official separated Annex Q p.169-170:
- pass income total = 1,040,489,497; BCRA = 1,040,489,497.
- pass expense total = 2,428; other financial institutions = 2,428.
- four-leg annual identity: PASS.
- Q4 reconstruction: NOT RUN because official compatible 9M not retrieved.

## Gate D — Credicoop FY
Official separated Annex Q p.244:
- pass income = 180,887,922; BCRA = 180,887,922.
- interest expenses: deposits 1,591,255,257 + other financial liabilities 622,427 = total 1,591,877,684.
- no pass-expense row; implied/reported pass expense = 0.
- annual identity: PASS.
- Q4 reconstruction: NOT RUN because compatible 9M PDF not retrieved.

## Gate E — basis-consistent open subset
ICBC+Galicia individual Q4 otherFI:
- income = 6192393.114538 thousand ARS.
- expense = 2366000.016574 thousand ARS.
- net = 3826393.097965 thousand ARS.
- asset footprint = 13.070316241404%.

Conclusion: open subset only; system cancellation test forbidden.

## Gate F — household flow
BCRA lending-rate page has by-holder-type monthly rate/amount statistics. This is not accrued-interest Annex Q allocation.
`HOUSEHOLD_ANNEX_Q_ACCRUED_INTEREST_FLOW_BRIDGE = NOT_IDENTIFIED`.

## Forbidden inference checks
- consolidated + individual implicit sum: NOT USED.
- FY control as Q4: NOT USED.
- asset coverage as pass-flow weight: NOT USED.
- open subset as system cancellation: NOT USED.
- +7.7pp passes = BCRA: NOT USED.
- stock/origination share as interest-flow share: NOT USED.
- product = household sector: NOT USED.
- household cost = bank profit: NOT USED.
- HTML modification: NOT PERFORMED.
