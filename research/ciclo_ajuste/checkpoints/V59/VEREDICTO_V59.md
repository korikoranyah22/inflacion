# VEREDICTO V59 — Positive-income / entity-level bridge

```text
IEF_MFIR_COMPONENT_FORMULA
= EXACT_WITH_ROUNDING

P24_BROAD_INTEREST_TO_IEF_INTEREST_DIRECT_MAPPING
= REJECTED

POST_NIIF_BROAD_INTEREST_COMMINGLING
= STRONG_SUPPORT

STRUCTURAL_REASON_FOR_3_3X_MISMATCH
= IDENTIFIED

A_Q_ANNUAL_SUBACCOUNT_SCHEMA
= STRONG_SUPPORT

Q3_A_Q_RAW_AVAILABILITY
= REJECTED_BY_REPORTING_FREQUENCY

ENTITY_LEVEL_RECLASSIFICATION_EXAMPLE
= SUPPORTED_BNA_2023

SYSTEM_Q3_Q4_POSITIVE_FLOW_RECONCILIATION
= NOT_FULLY_IDENTIFIED

HOUSEHOLD_PRODUCT_LEVEL_FLOW_SCHEMA
= IDENTIFIED

HOUSEHOLD_SYSTEM_Q4_POINT_ESTIMATE
= N/D

PASSES_DIRECT_BCRA
= STRONG_SUPPORT
= 7.7 pp
= 26.83% OF Q4 GROSS POSITIVE SUBTOTAL

UNRESOLVED_COUNTERPARTY
= 21.0 pp
= 73.17%

DIRECT_HOUSEHOLD_TO_BANK_TRANSFER
= NOT_IDENTIFIED
```

## Lectura
La incompatibilidad de V58 deja de ser un misterio estadístico: el estado público broad reúne intereses de instrumentos que el IEF reclasifica en buckets analíticos separados. El régimen post-NIIF y un worked example de BNA confirman la arquitectura.

Lo que todavía falta es numérico y de frecuencia: los subcomponentes del Anexo Q son anuales. Por eso V59 no puede convertir la apertura contable en un share sistémico Q4 por hogar, emisor o contraparte.

La frontera correcta para V60 es reconciliar **2023 anual contra 2023 anual**: Anexo Q sistémico (agregado desde datos abiertos o entidades) versus Tabla 1 anual del Informe sobre Bancos. Sólo después corresponde usar el mapping para atacar Q3/Q4.
