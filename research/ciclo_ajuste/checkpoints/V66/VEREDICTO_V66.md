# VEREDICTO V66 — Individual AQ retrieval and network expansion

## Estado cerrado

```text
SYSTEM_PANEL_BASIS
= INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING

FULL_FOUR_LEG_EXACT_Q4_TARGET_BASIS
= ICBC + BANCO_DE_VALORES
= 2 entities
= 5.2096% of bank assets

POINT_Q4_OTHERFI_DETAIL
= ICBC + BANCO_DE_VALORES + GALICIA
= 14.178874% of bank assets
= OPEN_SUBSET

SUPERVIELLE_Q4_PASS_TOTAL
= IDENTIFIED_EXACT
SUPERVIELLE_Q4_COUNTERPARTY_SPLIT
= BOUNDED_NOT_POINT_IDENTIFIED

CLOSED_PASS_NETWORK
= NOT_ACHIEVED

SYSTEM_INTERBANK_PASS_CANCELLATION
= NOT_IDENTIFIED_COVERAGE_TOO_LOW

SYSTEM_BCRA_NET_PASS_FLOW
= N/D

SYSTEM_INTERBANK_NET_PASS_FLOW
= N/D

IEF_7_7PP_BCRA_SHARE
= N/D

HOUSEHOLD_ANNEX_Q_ACCRUED_INTEREST_FLOW_BRIDGE
= NOT_IDENTIFIED

DIRECT_HOUSEHOLD_TO_BANK_TRANSFER
= NOT_IDENTIFIED

HTML_MODIFICATION
= FORBIDDEN
```

## 1. V66 suma la segunda entidad exacta en la base correcta

Banco de Valores publica en su Anexo Q separado las cuatro patas de pases. El 9M original y el FY 2023 son compatibles para la diferenciación en moneda homogénea. El Q4 reconstruido es:

```text
income BCRA     132269429.624
expense BCRA    0
income otherFI  47920.656
expense otherFI 204552.353
net BCRA        132269429.624
net otherFI     -156631.697
```

Unidad: miles de pesos de diciembre de 2023.

Con el activo BCRA de Banco de Valores (1.071.950,1 millones ARS), la cobertura estricta full-four-leg exacta pasa de 4,101042% a **5.2096%**. Sigue siendo baja.

## 2. Supervielle mejora de control consolidado a bound individual

Los estados separados 9M permiten reconstruir exactamente el **total** Q4 de pases; el FY separado revela la composición anual por contraparte. Como el 9M no muestra ese split, V66 no produce un punto falso. Produce:

```text
Q4 total income  = 86713401.666
Q4 total expense = 591120.907
Q4 BCRA income   = [83427561.666 ; 86713401.666]
Q4 otherFI income= [0 ; 3,285,840]
Q4 BCRA expense  = 0
Q4 otherFI expense= 591120.907
```

Supervielle queda en base correcta, pero con calidad `BOUND`, no `EXACT_FOUR_LEG`.

## 3. La red sigue abierta y el signo del neto depende de qué entidades entran

ICBC + Banco de Valores, ambos exactos, tienen neto otherFI Q4 de **-1058668.831 mil ARS**. Al sumar las patas otherFI exactas de Galicia, el neto del subconjunto pasa a **3669761.401 mil ARS**.

Ese cambio de signo es una demostración práctica de por qué un subconjunto abierto no puede usarse para declarar cancelación —o no cancelación— del sistema.

## 4. La cobertura mejoró, pero no lo suficiente para el +7,7 pp

Diagnósticos de retrieval:

```text
full-four-leg exact: 5.2096%
point counterparty detail incl. Galicia: 14.178874%
including Supervielle bounds: 16.224729%
```

Los porcentajes son masa de activos, no pesos de flujo. No se extrapola ninguna pata de pases por activos.

Por ello el +7,7 pp del IEF sigue sin una partición BCRA/interbancaria defendible.

## 5. Prioridad siguiente

El cuello ya no es encontrar cualquier banco chico con buen disclosure. V67 debe maximizar cobertura marginal: **Provincia, Credicoop, Nación, Ciudad, Macro, Santander y BBVA**, y sólo después ampliar hacia otras entidades. Provincia y Credicoop son especialmente valiosos porque el FY exacto ya está cerrado: falta únicamente el 9M compatible.
