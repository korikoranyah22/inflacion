# VEREDICTO V67 — Large-bank 9M retrieval and coverage scale-up

## Estado cerrado

```text
SYSTEM_PANEL_BASIS
= INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING

FULL_FOUR_LEG_EXACT_Q4_TARGET_BASIS
= ICBC + BANCO_DE_VALORES + BANCO_MACRO
= 3 entities
= 11.260968% of bank assets

POINT_Q4_OTHERFI_DETAIL
= ICBC + BANCO_DE_VALORES + BANCO_MACRO + GALICIA
= 20.230242% of bank assets
= OPEN_SUBSET

SUPERVIELLE_Q4_PASS_TOTAL
= IDENTIFIED_EXACT
SUPERVIELLE_Q4_COUNTERPARTY_SPLIT
= BOUNDED_NOT_POINT_IDENTIFIED

SANTANDER_3Q_4Q_PRIMARY_PAIR
= OFFICIAL_BINARIES_LOCATED_NOT_PARSED

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

## 1. Macro entra como tercera entidad exacta en la base correcta

Los estados oficiales de Banco Macro contienen Anexo Q **separado** tanto a septiembre como a diciembre de 2023. Ambos usan miles de pesos en moneda homogénea y abren pases entre BCRA y otras entidades financieras.

La regla congelada:

```text
Q4_Dec = FY_Dec - 9M_Sep × 1.532908152197
```

da:

```text
income BCRA      = 61675202.827
expense BCRA     = 0
income otherFI   = 5729593.580
expense otherFI  = 2502560.286
net BCRA         = 61675202.827
net otherFI      = 3227033.294
```

Unidad: miles de pesos de diciembre de 2023.

El activo individual publicado por BCRA para Macro es **5.851.533,4 millones ARS**, equivalente a **6.051368%** de activos bancarios.

## 2. La cobertura estricta se duplica, pero sigue lejos de una red cerrada

```text
V66 exact full-four-leg = 5.209600%
V67 exact full-four-leg = 11.260968%
```

El salto es material para retrieval, pero tres entidades que representan ~11,26% de activos no permiten inferir cancelación interbancaria del sistema.

## 3. El signo del subconjunto exacto cambia otra vez

V66:

```text
ICBC + Banco de Valores
net otherFI = -1,058,668.831 mil ARS
```

V67, al agregar Macro con datos exactos:

```text
ICBC + Banco de Valores + Banco Macro
net otherFI = 2168364.463 mil ARS
```

El signo pasa de negativo a positivo sin cambiar definición, período ni base; sólo cambia la cobertura. Es evidencia directa de que **el signo de una red abierta no es una propiedad del sistema**.

Al agregar Galicia para las patas otherFI puntuales, el neto del subset llega a **6896794.695 mil ARS**, pero Galicia sigue sin cerrar su pata BCRA y tampoco convierte el subset en sistema.

## 4. Santander queda mucho más cerca, pero no se fuerza

La página oficial de accionistas enlaza los balances 3T23 y 4T23 y los archivos están explícitamente nombrados como consolidados y separados. El backend disponible no puede decodificar esos PDFs. V67 registra el hallazgo documental, pero **no transcribe valores que no pudo inspeccionar**.

## 5. Gates que no cambian

Aun con el salto de cobertura:

```text
SYSTEM_INTERBANK_PASS_CANCELLATION = NOT_IDENTIFIED_COVERAGE_TOO_LOW
SYSTEM_BCRA_NET_PASS_FLOW = N/D
SYSTEM_INTERBANK_NET_PASS_FLOW = N/D
IEF_7_7PP_BCRA_SHARE = N/D
```

La masa de activos es sólo una métrica de cobertura documental; no pondera ni extrapola flujos de pases.

## 6. Próximo cuello

V68 debe intentar convertir el gran bloque de documentación ya localizada en entidades exactas: **Santander primero**, luego Provincia/Credicoop/Nación/Ciudad/BBVA. La prioridad es rendimiento marginal de cobertura, conservando la base individual y sin rescatar datos consolidados como sustituto.
