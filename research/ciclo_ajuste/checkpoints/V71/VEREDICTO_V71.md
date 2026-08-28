# VEREDICTO V71 — ARCHIVE RECOVERY AND SOURCE-SCOPE REFINEMENT

```text
SYSTEM_PANEL_BASIS
= INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING

STRICT_Q4_FOUR_LEG_EXACT_TARGET_BASIS
= ICBC + Banco de Valores + Banco Macro
= 11.260968% bank assets

NEW_Q4_FOUR_LEG_EXACT_ENTITY
= NO

BNA_9M_SEPARATED_STATEMENTS_AUDITED
= SUPPORTED_BY_AGN

BNA_9M_AGN_EXACT_ATTACHMENTS
= 2023-210-Informe SC 1.pdf
+ 2023-210-Informe CC 2.pdf
= CURRENT_HTTP_502

BNA_9M_AGN_FULL_STATEMENT_PAYLOAD
= NOT_ESTABLISHED

BNA_9M_ANNEX_Q
= NOT_RECOVERED

BNA_Q4_FOUR_LEG
= N/D

CREDICOOP_9M_PRIMARY_PUBLICATION
= OFFICIAL_ISSUER_INDEX_CONFIRMED

CREDICOOP_9M_BINARY
= NOT_RECOVERED_DYNAMIC_LINK

CREDICOOP_Q4_FOUR_LEG
= N/D

BAPRO_2023_SEPARATED_9M
= NOT_RECOVERED

CIUDAD_2023_SEPARATED_9M
= NOT_RECOVERED

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

## Interpretación

V71 no agrega cobertura exacta. Su avance es de **scope documental**: AGN prueba que el BNA tuvo estados 9M separados revisados, pero los attachments accesibles por nombre son informes de revisión y no puede asumirse que contengan el juego completo ni Anexo Q. En Credicoop, en cambio, la existencia del 30/09/2023 queda confirmada directamente por el índice oficial del emisor, aunque el link dinámico todavía impide recuperar el binario.

La siguiente iteración debe dejar de perseguir el PDF AGN como si fuera necesariamente el balance completo y buscar el filing separado BNA en BNA/BCRA/archivo regulatorio; para Credicoop, debe resolver el target dinámico del índice oficial.
