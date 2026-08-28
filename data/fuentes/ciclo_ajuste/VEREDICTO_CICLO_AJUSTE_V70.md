# VEREDICTO V70 — BNA 9M SOURCE AUDIT AND PUBLIC BANK RETRIEVAL GATE

```text
SYSTEM_PANEL_BASIS
= INDIVIDUAL_ENTITY_REGULATORY_WITH_EXPLICIT_SYSTEM_NETTING

STRICT_Q4_FOUR_LEG_EXACT_TARGET_BASIS
= ICBC + Banco de Valores + Banco Macro
= 11.260968% bank assets

NEW_Q4_FOUR_LEG_EXACT_ENTITY
= NO

BNA_9M_AGN_SEPARATED_PACKAGE
= OFFICIAL_SOURCE_IDENTIFIED

BNA_9M_AGN_ATTACHMENTS
= CURRENT_HTTP_502

BNA_9M_ISSUER_CONDENSED
= PRIMARY_RECOVERED
= CONSOLIDATED_INCLUSIVE_CONTROL_ONLY
= NO_ANNEX_Q

BNA_Q4_FOUR_LEG
= N/D

BAPRO_SEP2023_OFFICIAL_DISCLOSURE
= RECOVERED
= DOES_NOT_CONTAIN_SEPARATED_ANNEX_Q

CREDICOOP_9M_PRIMARY_ANNEX_Q
= NOT_RECOVERED

CIUDAD_9M_CONSOLIDATED
= PRIMARY_RECOVERED_CONTROL_ONLY

CIUDAD_9M_INDIVIDUAL
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

V70 no incrementa la cobertura exacta. Su hallazgo principal es de clasificación documental: el BNA sí publica un resumen oficial 9M de septiembre de 2023, pero ese documento **no es el filing individual que necesita el panel**. La nota al pie lo define como inclusivo de filiales, subsidiarias y entes estructurados, y el resumen no contiene Anexo Q.

El paquete individual/separado de BNA sigue documentado por AGN, pero los attachments oficiales están inaccesibles en la ruta actual. Por lo tanto no existe base para construir `BNA_Q4_AQ_BRIDGE_V70.csv`.

La investigación de bancos públicos progresa en rutas de fuente (Bapro septiembre oficial; Ciudad consolidado oficial), pero todavía no en cuatro patas individuales Q4.

La prioridad siguiente debe ser recuperación **archivística/regulatoria** del attachment 9M separado de BNA y, en paralelo, la enumeración de archivos históricos separados de Provincia/Ciudad/Credicoop.
