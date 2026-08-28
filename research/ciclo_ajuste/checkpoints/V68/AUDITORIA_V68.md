# AUDITORÍA V68 — PRIMARY RECOVERY AND DISCLOSURE GAP

## Objetivo

Resolver el bloqueo de binarios primarios de Santander y aumentar cobertura de bancos grandes sin relajar la base individual regulatoria ni convertir stocks en flujos.

## Hallazgo 1 — Santander dejó de estar parser-blocked

Se recuperaron y auditaron los estados **separados/individuales** al 30/09/2023 y 31/12/2023. La metadata CNV confirma que la presentación 9M del banco padre es individual (#3120080), distinta de la consolidada.

## Hallazgo 2 — el cuello no era sólo técnico: hay un disclosure gap intermedio

El filing 9M recuperado lista Anexo O, Anexo P y Anexo R, sin Anexo Q. Por lo tanto no se puede fabricar el split BCRA/otherFI del 9M desde stock. Esto convierte el estado de Santander de `PARSER_BLOCKED` a `PRIMARY_PAIR_RECOVERED_INTERIM_ANNEX_Q_MISSING`.

## Hallazgo 3 — sí puede cerrarse el TOTAL de ingreso Q4

La Nota 26.1 intermedia informa `Por operaciones de pase = 100,510,106` (miles Sep-2023 homogéneos). El Anexo Q FY informa `Por operaciones de pase = 354,485,360` (miles Dic-2023 homogéneos). Con la regla congelada de reexpresión:

```text
Q4 total pass income = 200,412,599.134366 thousand ARS Dec-2023 constant
```

## Hallazgo 4 — bound individual de contraparte del ingreso

FY Anexo Q:

```text
income BCRA    = 354,462,410
income otherFI =      22,950
```

Condicionando el bound a subflujos acumulados de ingreso no negativos:

```text
Q4 BCRA income share    >= 99.988548624%
Q4 otherFI income share <= 0.011451376%
```

Es un bound de ingreso a nivel entidad. No se extrapola al sistema.

## Hallazgo 5 — no se cierra la cuarta pata

El filing 9M no separa egreso por operaciones de pase. El rubro amplio `Intereses por intermediación financiera` no es identidad de pases. Consecuencia:

```text
SANTANDER_Q4_EXPENSE_COUNTERPARTY = N/D
SANTANDER_Q4_NET_PASS_FLOW = N/D
SANTANDER_Q4_FOUR_LEG = NOT_IDENTIFIED
```

## Cobertura

La cobertura estricta four-leg exacta **no cambia**:

```text
ICBC + Banco de Valores + Banco Macro
= 11.260968% de activos bancarios
```

Pero la huella documental Q4 que ya tiene información individual de contraparte/bounds de ingreso pasa a:

```text
ICBC + Valores + Macro + Galicia + Supervielle + Santander
= 31.146102% de activos bancarios
```

Este porcentaje es sólo `RETRIEVAL / INCOME-BOUND FOOTPRINT`, no cobertura de red neteable.

## BBVA

La ruta CNV del banco padre recuperada en V68 expone estados consolidados al 30/09/2023 y 31/12/2023. Las entradas individuales visibles corresponden a controladas/vinculadas. Se mantiene `N/D` para el par individual del banco padre hasta hallar otra vía BCRA/issuer.

## Gates

```text
CLOSED_PASS_NETWORK = NOT_ACHIEVED
SYSTEM_INTERBANK_PASS_CANCELLATION = NOT_IDENTIFIED_COVERAGE_TOO_LOW
SYSTEM_BCRA_NET_PASS_FLOW = N/D
SYSTEM_INTERBANK_NET_PASS_FLOW = N/D
IEF_7_7PP_BCRA_SHARE = N/D
HOUSEHOLD_ANNEX_Q_ACCRUED_INTEREST_FLOW_BRIDGE = NOT_IDENTIFIED
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED
HTML_MODIFICATION = FORBIDDEN
```
