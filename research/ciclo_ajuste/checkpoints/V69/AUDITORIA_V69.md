# AUDITORÍA V69 — PUBLIC BANK SOURCE PATH AND COVERAGE PRIORITY

## Objetivo

V69 intentó aumentar cobertura Q4 exacta concentrándose en bancos grandes/públicos y en fuentes regulatorias alternativas, sin relajar la base individual fijada en V65.

## Resultado principal

```text
NEW_Q4_FOUR_LEG_EXACT_ENTITY = NO
STRICT_Q4_FOUR_LEG_EXACT_COVERAGE = 11.260968%
```

No se encontró un 9M individual/separado compatible nuevo que permita diferenciar FY y cerrar cuatro patas Q4.

## Banco Nación — avance fuerte de fuente y base

Se recuperó/validó el `Schedule Q — INDIVIDUAL` FY-2023 oficial:

```text
income BCRA     = 766,170,919 thousand ARS
income otherFI  = 0
expense BCRA    = 0
expense otherFI = 0
```

El `Schedule Q — CONSOLIDATED` del mismo FY reporta:

```text
income BCRA     = 766,170,918
income otherFI  = 3,980,009
expense BCRA    = 0
expense otherFI = 0
```

Esto NO se interpreta como error ni se promedia. Demuestra que la composición cambia con la base y refuerza:

```text
SYSTEM_PANEL_BASIS
= INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING
```

### 9M Nación

AGN Informe 210/2023 identifica oficialmente estados:
- consolidados condensados;
- separados condensados;
- período 01/01/2023–30/09/2023.

Los attachments oficiales fueron identificados, pero devuelven 502 en la recuperación actual. Por lo tanto:

```text
BNA_9M_SEPARATED_SOURCE = IDENTIFIED
BNA_9M_BINARY = NOT_RECOVERED
BNA_9M_ANNEX_Q = NOT_INSPECTED
BNA_Q4_FOUR_LEG = N/D
```

No se sustituye con stock, consolidado ni FY.

## Cobertura / prioridad

Denominador BCRA diciembre 2023:

```text
bank assets = 96,697,695.5 million ARS
```

Targets unresolved:

```text
BNA       = 22.015263%
Provincia = 8.979200%
Credicoop = 3.303157%
Ciudad    = 3.822184%
total     = 38.119804%
```

Si BNA solo cerrara Q4 exacto, la cobertura estricta pasaría hipotéticamente:

```text
11.260968% -> 33.276231%
```

Si los cuatro targets cerraran exactamente:

```text
strict current + four targets
= 49.380772%
```

Aun así el asset footprint quedaría por debajo de 50%. Esto no es un criterio matemático universal de "red cerrada", pero sí demuestra que el gate no debe elevarse automáticamente aun bajo ese escenario.

**Prohibición:** no usar activos como ponderadores de flujos de pases.

## Provincia

El FY individual exacto continúa vigente. Se confirmó una arquitectura histórica oficial de paquetes intermedios unificados y anexos separados, pero no se recuperó el binario Sep-2023 objetivo.

## Credicoop

FY individual exacto continúa vigente. La publicación Sep-2023 existe, pero no se recuperó el Anexo Q compatible.

## Ciudad

Se cuantificó el activo BCRA Dec-2023 = 3,695,963.4 millones ARS. El Q4 consolidado exacto heredado sigue siendo `CONTROL_ONLY`; no se incorpora a la red.

## Santander

No apareció una fuente alternativa de Anexo Q 9M. El bound individual de V68 permanece y no se intenta completar con stocks.

## Gates finales

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
