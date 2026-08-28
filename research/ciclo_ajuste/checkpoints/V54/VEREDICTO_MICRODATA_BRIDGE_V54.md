# Veredicto V54 — menos masa “clasificada”, más precisión causal

## Estado

```text
RAW_OFFICIAL_ENDPOINTS = VERIFIED
RAW_SOURCE_BYTES_MATERIALIZED = FALSE
SHA256_GATE = FAILED_RUNTIME_NETWORK

SECURITIES_RESULT_BRIDGE = FAILED_RECONCILIATION
INTEREST_SECTOR_BRIDGE = FAILED_RECONCILIATION
CER_GROSS_BRIDGE = FAILED_RECONCILIATION
FX_REMEASUREMENT_TRADING_SPLIT = NOT_IDENTIFIED

COUNTERPARTY_VS_ACCOUNTING_MODE_ORTHOGONALITY = STRONG_SUPPORT

V53_66_20_STRICT_CLASSIFIED_AS_JOINT_PARTITION = REVOKED
V53_MARKET_VALUATION_FLOOR_39_37 = REVOKED
V53_HOUSEHOLD_[0,2.1]PP_STRICT_CEILING = REVOKED

BCRA_DIRECT_COUNTERPARTY_FLOOR = 7.7 PP
BCRA_DIRECT_COUNTERPARTY_FLOOR_SHARE = 26.83%
Q4_2023_UNRESOLVED_COUNTERPARTY_MASS = 21.0 PP
Q4_2023_UNRESOLVED_COUNTERPARTY_SHARE = 73.17%

HOUSEHOLD_DIRECT_POINT_ESTIMATE = N/D
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED_AT_ABNORMAL_GAP_LEVEL
NET_CAUSAL_BANK_BENEFIT = NOT_IDENTIFIED
```

## Lectura

V54 encuentra que V53 había mezclado dos preguntas diferentes:

```text
¿quién es la contraparte?
vs
¿por qué mecanismo contable aparece el resultado?
```

Eso hacía parecer que 66,2% del subtotal positivo estaba dentro de una misma partición. No lo estaba.

La única masa Q4-2023 que hoy puede ubicarse en una **contraparte directa identificada** sin cambiar de eje es la de pases con el BCRA:

```text
7,7 / 28,7 = 26.83%
```

FX sigue siendo un canal fuertemente compatible con el shock cambiario, pero la cuenta mezcla remeasurement y trading. Títulos mezcla emisor y tratamiento. Intereses mezcla sectores.

Por eso el resultado científico de V54 no es “encontramos menos”, sino:

> **sabemos exactamente qué parte estaba sobreclasificada y qué evidencia falta para elevar cada N/D.**

## Próxima frontera

```text
NEXT = V55_BYTE_MATERIALIZATION_AND_SUBACCOUNT_RECONCILIATION
```

V55 debe ejecutarse en un runtime con acceso binario efectivo a los XLS/XLSX/7z oficiales o con esos archivos provistos localmente. Sólo después corresponde reintentar shares por hogar/emisor/modo contable.
