# HANDOVER CODEX — Proyecto Ciclo del Ajuste Argentina 2002–2026
## Continuación desde V68 → ejecutar V69

**Fecha de corte:** 2026-08-27  
**Rama activa:** contrapartes / incidencia distributiva / flujos bancarios  
**Última iteración cerrada:** V68  
**Próxima:** `V69_ALTERNATE_INTERIM_AQ_SOURCE_AND_PUBLIC_BANK_SCALEUP`

## Estado congelado

```text
SYSTEM_PANEL_BASIS
= INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING

BCRA_BANK_ASSETS_DEC2023
= 96,697,695.5 million ARS

STRICT_Q4_FOUR_LEG_EXACT
= ICBC + Banco de Valores + Banco Macro
= 11.260968% bank assets

SANTANDER_PRIMARY_INDIVIDUAL_9M_FY
= RECOVERED

SANTANDER_9M_ANNEX_Q
= NOT_PRESENT_IN_RECOVERED_FILING

SANTANDER_Q4_TOTAL_PASS_INCOME
= 200412599.134366 thousand ARS Dec-2023 constant

SANTANDER_Q4_BCRA_PASS_INCOME_SHARE
>= 99.988548624% CONDITIONAL_ENTITY_BOUND

SANTANDER_Q4_FOUR_LEG
= NOT_IDENTIFIED_EXPENSE_SPLIT_MISSING

Q4_INDIVIDUAL_PASS_INCOME_BOUND_FOOTPRINT
= 31.146102% bank assets
= NOT_NETTABLE

CLOSED_PASS_NETWORK = NOT_ACHIEVED
SYSTEM_INTERBANK_PASS_CANCELLATION = NOT_IDENTIFIED_COVERAGE_TOO_LOW
SYSTEM_BCRA_NET_PASS_FLOW = N/D
SYSTEM_INTERBANK_NET_PASS_FLOW = N/D
IEF_7_7PP_BCRA_SHARE = N/D
HOUSEHOLD_ANNEX_Q_ACCRUED_INTEREST_FLOW_BRIDGE = NOT_IDENTIFIED
DIRECT_HOUSEHOLD_TO_BANK_TRANSFER = NOT_IDENTIFIED
HTML_MODIFICATION = FORBIDDEN
```

## Qué NO volver a intentar

- No inferir Santander 9M counterparty flow desde Nota 7 o Anexo P stocks.
- No seguir tratando el parser como cuello: el filing 9M ya está recuperado y auditado; el Anexo Q no está en ese documento.
- No mezclar el antiguo bound consolidado Santander con el nuevo bound individual.
- No usar asset share como flow weight.

## Prioridad V69

1. **BCRA / attachment alternativo de Anexo Q intermedio** para Santander: buscar si el Anexo Q 9M existe como presentación regulatoria separada, no dentro del filing CNV principal.
2. **Banco Provincia 9M individual/separado**: FY exact ya existe; máximo retorno de cobertura.
3. **Credicoop 9M individual/separado**: FY exact ya existe.
4. **Banco Nación 9M/FY individual** mediante BCRA/AGN/BNA.
5. **Banco Ciudad individual** 9M/FY; el consolidado no entra al panel.
6. **BBVA**: cambiar de ruta desde CNV consolidada a BCRA/issuer regulatory disclosure; no usar controladas como banco padre.
7. Supervielle: sólo si aparece counterparty split intermedio directo.

## Gate

No elevar sistema hasta near-full/closed coverage con las cuatro patas. Mantener el diagnóstico de inestabilidad de signo del subset exacto.
